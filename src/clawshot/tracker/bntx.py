"""Read BNTX texture files (nn::gfx ``ResTextureFile``) and undo the NVIDIA block-linear layout of their pixels.

Read-only and bounded: every offset is checked against the file before it is used, and nothing is relocated or
written. Only what a tracker icon needs is decoded: mip level 0 of array layer 0 of a 2D texture.

Format facts, each from documentation (no code was copied or adapted):

- EPD Wiki, "Bntx" (https://epd.zeldamods.org/wiki/Bntx, oldid 74), "Common nn::util" (oldid 155) and
  "Common nn::gfx" (oldid 160): the 0x20-byte file header, the ``ResTextureContainer`` that follows it (texture count,
  pointer to the ``ResTextureInfo`` pointer array), ``ResTextureInfo`` ("BRTI": total texture size at 0x50, channel
  sources at 0x58, texture dimension at 0x5C, name at 0x60, mip-level pointer array at 0x70) with
  ``nn::gfx::TextureInfo`` at 0x10, names as a u16 length and the characters, ``ChannelFormat``/``TypeFormat`` values
  and ``ImageFormat = ChannelFormat << 8 | TypeFormat``. The wiki prints ASTC 10x6 as 0x26; the values run
  0x2D..0x3A in table order, so it is 0x36.
- Wexos's Wiki, "BNTX (File Format)" (https://wiki.wexosmk.xyz/index.php/BNTX_(File_Format), oldid 749): the
  platform tags ``NX  `` (Switch) and ``Ounc`` (Switch 2), tile mode 0 = optimal (block linear) and 1 = linear, the
  texture-layout word at BRTI 0x34 carrying the block height shift, channel sources 0 zero, 1 one, 2..5 red, green,
  blue, alpha, and texture dimensions 1 = 2D, 5 = 2D array.
- Linux ``include/uapi/drm/drm_fourcc.h`` at a77fa227bb0c681eaa0a20476a388c176af4789e,
  ``DRM_FORMAT_MOD_NVIDIA_16BX2_BLOCK`` and ``DRM_FORMAT_MOD_NVIDIA_BLOCK_LINEAR_2D``: pixels in 64x8-byte groups of
  bytes (GOBs), 2^h GOBs stacked vertically per block, data inside a GOB in 16-byte x 2-line sectors, whose order
  ("sector layout") differs between Tegra K1..Parker/TX2 and desktop/Xavier-Orin GPUs; "Chapter 20 'Pixel Memory
  Formats' of the Tegra X1 TRM describes this format in full detail".
- envytools, "G80 surface formats", "Blocklinear surfaces"
  (https://envytools.readthedocs.io/en/latest/hw/memory/g80-surface.html): blocks are stored x first, then y;
  texture units shrink the block height while half of it would still cover the surface; compressed formats count
  compressed blocks as elements.
- Mesa ``src/nouveau/nil/tiling.rs`` at c6e94180ced38b556294667b3631171a462c3497: the sector numbering of a 512-byte
  GOB's 4x4 grid of 32-byte sectors, by grid rows, for ``GOBType::TegraColor`` (0 1 8 9 / 2 3 10 11 / 4 5 12 13 /
  6 7 14 15, :func:`tegra_gob_offset`) and ``GOBType::TuringColor2D`` (0 2 8 10 / 1 3 9 11 / 4 6 12 14 /
  5 7 13 15, :func:`turing_gob_offset`).

Checked on build e0f3ccfa (Switch 2, platform ``Ounc``): every ``UI/Tex/Icon`` texture's stored size equals
:func:`surface_size` of its level 0, and the icons decode whole with the Turing sector order and visibly scrambled in
4x8-pixel strips with the Tegra one, so ``Ounc`` files use the Turing order. ``NX  `` files (the Tegra X1) use the
Tegra order; no such file was decoded here.
"""

import math
import struct
from dataclasses import dataclass

MAGIC = b"BNTX\0\0\0\0"
PLATFORMS = (b"NX  ", b"Ounc")
MAJOR_VERSION = 4
HEADER_SIZE = 0x20  # nn::util::BinaryFileHeader; the ResTextureContainer follows
CONTAINER_SIZE = 0x38
INFO_SIZE = 0x78  # the ResTextureInfo fields read here, up to and including the mip-level pointer array's pointer

GOB_WIDTH = 64  # bytes
GOB_HEIGHT = 8  # lines
GOB_SIZE = GOB_WIDTH * GOB_HEIGHT
MAX_BLOCK_HEIGHT_LOG2 = 5  # 1 to 32 GOBs a block
MAX_TEXTURES = 4096
MAX_DIMENSION = 16384
MAX_MIPS = 32

TILE_OPTIMAL = 0
STORAGE_2D = 2
TEXTURE_2D = 1
TEXTURE_2D_ARRAY = 5
ZERO, ONE, RED, GREEN, BLUE, ALPHA = range(6)
IDENTITY = (RED, GREEN, BLUE, ALPHA)

# ChannelFormat -> (name, block width, block height, bytes per block). ASTC is ChannelFormat 0x2D..0x3A.
_ASTC_SIZES = [
    "4x4",
    "5x4",
    "5x5",
    "6x5",
    "6x6",
    "8x5",
    "8x6",
    "8x8",
    "10x5",
    "10x6",
    "10x8",
    "10x10",
    "12x10",
    "12x12",
]
FORMATS: dict[int, tuple[str, int, int, int]] = {
    0x0B: ("R8G8B8A8", 1, 1, 4),
    0x0C: ("B8G8R8A8", 1, 1, 4),
    0x1A: ("BC1", 4, 4, 8),
    0x1C: ("BC3", 4, 4, 16),
    0x20: ("BC7", 4, 4, 16),
}
FORMATS.update(
    {0x2D + i: (f"ASTC {size}", *(int(n) for n in size.split("x")), 16) for i, size in enumerate(_ASTC_SIZES)}
)


class BntxError(ValueError):
    """The bytes are not a well-formed BNTX file, or a texture's data is truncated."""


class UnsupportedTexture(BntxError):
    """Well-formed, but a kind of texture this reader does not decode (format, layout or dimension)."""


class DecoderUnavailable(BntxError):
    """The texture is compressed and the optional decoder (``texture2ddecoder``) is not installed."""


@dataclass(frozen=True)
class Texture:
    name: str
    platform: bytes
    """The container's platform tag: ``NX  `` (Switch) or ``Ounc`` (Switch 2); it selects the GOB sector order."""
    image_format: int
    """``ChannelFormat << 8 | TypeFormat``."""
    width: int
    height: int
    depth: int
    layers: int
    mip_count: int
    sample_count: int
    storage_dimension: int
    texture_dimension: int
    tile_mode: int
    block_height_log2: int
    channel_sources: tuple[int, int, int, int]
    data: bytes
    """All stored image data (every level and layer, ``ResTextureInfo`` total size), level 0 of layer 0 first."""

    @property
    def channel_format(self) -> int:
        return self.image_format >> 8

    @property
    def format_name(self) -> str:
        known = FORMATS.get(self.channel_format)
        return known[0] if known else f"image format {self.image_format:#06x}"


def _span(data: bytes, offset: int, size: int, what: str) -> None:
    if offset < 0 or size < 0 or offset + size > len(data):
        raise BntxError(f"{what} at {offset:#x}+{size:#x} lies outside the {len(data):#x}-byte file")


def _string(data: bytes, offset: int, what: str) -> str:
    _span(data, offset, 2, what)
    (length,) = struct.unpack_from("<H", data, offset)
    _span(data, offset + 2, length, what)
    try:
        return data[offset + 2 : offset + 2 + length].decode("utf-8")
    except UnicodeDecodeError as error:
        raise BntxError(f"{what} at {offset:#x} is not UTF-8") from error


def read(data: bytes) -> list[Texture]:
    """Every texture in a little-endian BNTX file (version 4, Switch or Switch 2), in the file's order."""
    data = bytes(data)
    if len(data) < HEADER_SIZE + CONTAINER_SIZE:
        raise BntxError(f"{len(data)} bytes is too short for a BNTX header")
    if data[:8] != MAGIC:
        raise BntxError(f"not a BNTX file (magic {data[:8]!r})")
    order = data[0xC:0xE]
    if order == b"\xfe\xff":
        raise UnsupportedTexture("big-endian BNTX files are not read")
    if order != b"\xff\xfe":
        raise BntxError(f"bad byte-order mark {order.hex()}")
    (major,) = struct.unpack_from("<H", data, 0xA)
    if major != MAJOR_VERSION:
        raise UnsupportedTexture(f"BNTX major version {major} is not read (only {MAJOR_VERSION})")
    (size,) = struct.unpack_from("<I", data, 0x1C)
    if size > len(data):
        raise BntxError(f"the header says {size:#x} bytes; the file has {len(data):#x}")
    platform = data[HEADER_SIZE : HEADER_SIZE + 4]
    if platform not in PLATFORMS:
        raise UnsupportedTexture(f"platform {platform!r} is not read")
    count, table = struct.unpack_from("<IQ", data, HEADER_SIZE + 4)
    if not 0 < count <= MAX_TEXTURES:
        raise BntxError(f"texture count {count} is outside 1..{MAX_TEXTURES}")
    _span(data, table, 8 * count, "texture pointer array")
    return [_texture(data, platform, struct.unpack_from("<Q", data, table + 8 * i)[0], i) for i in range(count)]


def _texture(data: bytes, platform: bytes, info: int, index: int) -> Texture:
    what = f"texture {index}"
    _span(data, info, INFO_SIZE, what)
    if data[info : info + 4] != b"BRTI":
        raise BntxError(f"{what} at {info:#x} is not a BRTI block ({data[info : info + 4]!r})")
    name_offset, _parent, mip_table = struct.unpack_from("<3Q", data, info + 0x60)
    name = _string(data, name_offset, f"{what} name")
    tile, _swizzle, mips, samples = struct.unpack_from("<4H", data, info + 0x12)
    image_format, _access, width, height, depth, layers, layout = struct.unpack_from("<7I", data, info + 0x1C)
    (image_size,) = struct.unpack_from("<I", data, info + 0x50)
    for label, value in (("width", width), ("height", height), ("depth", depth), ("layers", layers)):
        if not 0 < value <= MAX_DIMENSION:
            raise BntxError(f"{name}: {label} {value} is outside 1..{MAX_DIMENSION}")
    if not 0 < mips <= MAX_MIPS:
        raise BntxError(f"{name}: {mips} mip levels is outside 1..{MAX_MIPS}")
    _span(data, mip_table, 8 * mips, f"{name} mip pointer array")
    (level0,) = struct.unpack_from("<Q", data, mip_table)
    if image_size == 0:
        raise BntxError(f"{name}: no image data")
    _span(data, level0, image_size, f"{name} image data")
    return Texture(
        name=name,
        platform=platform,
        image_format=image_format,
        width=width,
        height=height,
        depth=depth,
        layers=layers,
        mip_count=mips,
        sample_count=samples,
        storage_dimension=data[info + 0x11],
        texture_dimension=data[info + 0x5C],
        tile_mode=tile,
        block_height_log2=layout & 0x7,
        channel_sources=tuple(data[info + 0x58 : info + 0x5C]),
        data=data[level0 : level0 + image_size],
    )


def tegra_gob_offset(x: int, y: int) -> int:
    """Byte offset inside a Tegra X1 GOB of byte column ``x`` (0..63) on line ``y`` (0..7): sectors of two 16-byte
    lines, two sectors across and four down, the left 32 bytes of all eight lines first (``GOBType::TegraColor``)."""
    return (x >> 5) * 256 + (y >> 1) * 64 + ((x >> 4) & 1) * 32 + (y & 1) * 16 + (x & 15)


def turing_gob_offset(x: int, y: int) -> int:
    """The same for the desktop/Xavier+ order (``GOBType::TuringColor2D``): in each 32-byte-wide half, the upper four
    lines before the lower four; in each such band, the left two-sector column (top first) before the right one."""
    return (x >> 5) * 256 + (y >> 2) * 128 + ((x >> 4) & 1) * 64 + ((y >> 1) & 1) * 32 + (y & 1) * 16 + (x & 15)


GOB_OFFSETS = {b"NX  ": tegra_gob_offset, b"Ounc": turing_gob_offset}


def effective_block_height_log2(rows: int, block_height_log2: int) -> int:
    """The block height a texture unit uses: halved while half a block would still cover ``rows`` (envytools)."""
    if not 0 <= block_height_log2 <= MAX_BLOCK_HEIGHT_LOG2:
        raise BntxError(f"block height 2^{block_height_log2} GOBs is outside 1..32")
    while block_height_log2 > 0 and (GOB_HEIGHT << (block_height_log2 - 1)) >= rows:
        block_height_log2 -= 1
    return block_height_log2


def surface_size(width_bytes: int, rows: int, block_height_log2: int) -> int:
    """Bytes a block-linear surface of ``rows`` lines of ``width_bytes`` occupies (whole GOBs and blocks)."""
    block_gobs = 1 << effective_block_height_log2(rows, block_height_log2)
    return math.ceil(width_bytes / GOB_WIDTH) * math.ceil(rows / (GOB_HEIGHT * block_gobs)) * block_gobs * GOB_SIZE


def deblock(data: bytes, width_bytes: int, rows: int, block_height_log2: int, gob_offset) -> bytes:
    """Block-linear ``data`` (block width one GOB, depth one, sectors placed by ``gob_offset``) as ``rows`` contiguous
    lines of ``width_bytes``.

    A byte's address is the sum of its line's part and its column's part, so each line copies 16-byte runs.
    """
    if width_bytes <= 0 or rows <= 0:
        raise BntxError(f"empty surface {width_bytes}x{rows}")
    needed = surface_size(width_bytes, rows, block_height_log2)
    if len(data) < needed:
        raise BntxError(f"the block-linear surface needs {needed:#x} bytes; {len(data):#x} are stored")
    block_gobs = 1 << effective_block_height_log2(rows, block_height_log2)
    block_bytes = block_gobs * GOB_SIZE
    block_lines = GOB_HEIGHT * block_gobs
    row_of_blocks = math.ceil(width_bytes / GOB_WIDTH) * block_bytes
    columns = [
        (x, min(16, width_bytes - x), x // GOB_WIDTH * block_bytes + gob_offset(x % GOB_WIDTH, 0))
        for x in range(0, width_bytes, 16)
    ]
    source = memoryview(data)
    out = bytearray(width_bytes * rows)
    for y in range(rows):
        line = y // block_lines * row_of_blocks + y % block_lines // GOB_HEIGHT * GOB_SIZE + gob_offset(0, y % 8)
        start = y * width_bytes
        for x, length, column in columns:
            at = line + column
            out[start + x : start + x + length] = source[at : at + length]
    return bytes(out)


def load_decoder():
    """The optional ``texture2ddecoder`` module (MIT; Clawshot's ``ui`` extra), or None when it is not installed."""
    try:
        import texture2ddecoder
    except ImportError:
        return None
    return texture2ddecoder


def _apply_sources(rgba: bytes, sources: tuple[int, int, int, int]) -> bytes:
    if sources == IDENTITY:
        return rgba
    if any(not ZERO <= source <= ALPHA for source in sources):
        raise UnsupportedTexture(f"channel sources {sources} are outside 0..5")
    count = len(rgba) // 4
    plane = {
        ZERO: bytes(count),
        ONE: b"\xff" * count,
        RED: rgba[0::4],
        GREEN: rgba[1::4],
        BLUE: rgba[2::4],
        ALPHA: rgba[3::4],
    }
    out = bytearray(len(rgba))
    for channel, source in enumerate(sources):
        out[channel::4] = plane[source]
    return bytes(out)


def _bgra_to_rgba(bgra: bytes) -> bytes:
    out = bytearray(bgra)
    out[0::4] = bgra[2::4]
    out[2::4] = bgra[0::4]
    return bytes(out)


def to_rgba(texture: Texture, decoder=None) -> tuple[int, int, bytes]:
    """``(width, height, pixels)``: level 0 of layer 0 as 8-bit RGBA rows, channel sources applied.

    Uncompressed RGBA/BGRA needs nothing else; BC1, BC3, BC7 and every ASTC block size need ``decoder`` (default
    :func:`load_decoder`). Raises :class:`UnsupportedTexture` for anything else and :class:`DecoderUnavailable`
    when the decoder is missing.
    """
    name = texture.name
    if texture.storage_dimension != STORAGE_2D or texture.texture_dimension not in (TEXTURE_2D, TEXTURE_2D_ARRAY):
        raise UnsupportedTexture(
            f"{name}: storage dimension {texture.storage_dimension}, texture dimension {texture.texture_dimension}"
            " (only 2D textures and 2D arrays are read)"
        )
    if texture.depth != 1 or texture.sample_count > 1:
        raise UnsupportedTexture(f"{name}: depth {texture.depth}, {texture.sample_count} samples")
    if texture.tile_mode != TILE_OPTIMAL:
        raise UnsupportedTexture(f"{name}: tile mode {texture.tile_mode} (only block-linear textures are read)")
    known = FORMATS.get(texture.channel_format)
    if known is None:
        raise UnsupportedTexture(f"{name}: {texture.format_name} is not decoded")
    label, block_w, block_h, block_bytes = known
    gob_offset = GOB_OFFSETS.get(texture.platform)
    if gob_offset is None:
        raise UnsupportedTexture(f"{name}: platform {texture.platform!r} has no known GOB sector order")
    compressed = label not in ("R8G8B8A8", "B8G8R8A8")
    if compressed:
        decoder = decoder or load_decoder()
        if decoder is None:
            raise DecoderUnavailable(f"{name}: {label} needs the optional texture2ddecoder package")
    width, height = texture.width, texture.height
    width_bytes = math.ceil(width / block_w) * block_bytes
    linear = deblock(texture.data, width_bytes, math.ceil(height / block_h), texture.block_height_log2, gob_offset)
    if label == "R8G8B8A8":
        rgba = linear
    elif label == "B8G8R8A8":
        rgba = _bgra_to_rgba(linear)
    else:
        if label.startswith("ASTC"):
            bgra = decoder.decode_astc(linear, width, height, block_w, block_h)
        else:
            bgra = getattr(decoder, f"decode_{label.lower()}")(linear, width, height)
        if len(bgra) != width * height * 4:
            raise BntxError(f"{name}: the decoder returned {len(bgra)} bytes for {width}x{height}")
        rgba = _bgra_to_rgba(bytes(bgra))
    return width, height, _apply_sources(rgba, texture.channel_sources)
