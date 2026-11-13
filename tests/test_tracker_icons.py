"""Tracker icons: BNTX reading, block-linear layout, PNG output and the cache, on synthetic files only.

Every BNTX here is built by the test from the documented layout (see clawshot.tracker.bntx); the expected
block-linear placement comes from the documented sector grids below, not from the implementation.
"""

import os
import random
import struct
import threading
import zlib

import pytest
import zstandard
from test_pack_nup import write_nup

from clawshot.pack import ROOT
from clawshot.tracker import bntx, icons

RGBA8 = 0x0B01
BGRA8 = 0x0C01
BC1 = 0x1A01
BC2 = 0x1B01
ASTC_4X4_SRGB = 0x2D06
IDENTITY = (2, 3, 4, 5)
# Sector numbers of a GOB's 4x4 grid (16-byte columns, 2-line rows), by grid row: Mesa src/nouveau/nil/tiling.rs
# GOBType::TegraColor and GOBType::TuringColor2D.
TEGRA = ((0, 1, 8, 9), (2, 3, 10, 11), (4, 5, 12, 13), (6, 7, 14, 15))
TURING = ((0, 2, 8, 10), (1, 3, 9, 11), (4, 6, 12, 14), (5, 7, 13, 15))
FIRST_INFO = 0x60  # one texture: the pointer table at 0x58, its BRTI right after


def tile(linear: bytes, width_bytes: int, rows: int, block_height_log2: int, sectors) -> bytes:
    """Place every byte by the documented addressing: blocks of 2^h GOBs stacked vertically, blocks and the GOBs
    in them x first, then the sector grid inside a 64x8-byte GOB."""
    block = 1 << block_height_log2
    gobs_x = -(-width_bytes // 64)
    out = bytearray(gobs_x * -(-rows // (8 * block)) * block * 512)
    for y in range(rows):
        for x in range(width_bytes):
            gob = ((y // (8 * block)) * gobs_x + x // 64) * block + (y % (8 * block)) // 8
            sector = sectors[(y % 8) // 2][(x % 64) // 16]
            out[gob * 512 + sector * 32 + (y % 2) * 16 + x % 16] = linear[y * width_bytes + x]
    return bytes(out)


def noise(size: int, seed: int = 7) -> bytes:
    return random.Random(seed).randbytes(size)


def texture(name="Item_Bomb", width=5, height=3, image_format=RGBA8, pixels=None, platform=b"Ounc", **fields):
    """Fields for :func:`bntx_file`; an uncompressed texture is tiled from ``pixels`` (default: noise)."""
    data = fields.pop("data", None)
    if data is None:
        pixels = pixels if pixels is not None else noise(width * height * 4)
        data = tile(pixels, width * 4, height, fields.get("block_height", 0), TURING if platform == b"Ounc" else TEGRA)
    return {"name": name, "width": width, "height": height, "format": image_format, "data": data, **fields}


def bntx_file(*textures, platform=b"Ounc", major=4, order=b"\xff\xfe") -> bytes:
    """A little-endian BNTX in the documented layout: header, texture container, pointer table, BRTI blocks, then
    names, image data and mip pointer arrays."""
    table = 0x58
    out = bytearray(table + 8 * len(textures) + 0xA0 * len(textures))

    def place(blob: bytes, align: int) -> int:
        out.extend(b"\0" * (-len(out) % align))
        at = len(out)
        out.extend(blob)
        return at

    for index, fields in enumerate(textures):
        info = table + 8 * len(textures) + 0xA0 * index
        struct.pack_into("<Q", out, table + 8 * index, info)
        name = fields["name"].encode() if isinstance(fields["name"], str) else fields["name"]
        name_at = place(struct.pack("<H", len(name)) + name + b"\0", 2)
        data_at = place(fields["data"], 16)
        mips = fields.get("mips", 1)
        mip_table = place(struct.pack(f"<{mips}Q", *[data_at] * mips), 8)
        out[info : info + 4] = b"BRTI"
        struct.pack_into("<III", out, info + 4, 0, 0xA0, 0)
        out[info + 0x10] = 0x09
        out[info + 0x11] = fields.get("storage", 2)
        struct.pack_into("<4H", out, info + 0x12, fields.get("tile", 0), 0, mips, fields.get("samples", 1))
        dimensions = (fields["width"], fields["height"], fields.get("depth", 1), fields.get("layers", 1))
        struct.pack_into("<7I", out, info + 0x1C, fields["format"], 0x20, *dimensions, fields.get("block_height", 0))
        struct.pack_into("<II", out, info + 0x50, len(fields["data"]), 0x200)
        out[info + 0x58 : info + 0x5C] = bytes(fields.get("sources", IDENTITY))
        out[info + 0x5C] = fields.get("dimension", 1)
        struct.pack_into("<3Q", out, info + 0x60, name_at, 0x20, mip_table)
    out[0:8] = b"BNTX\0\0\0\0"
    struct.pack_into("<BBH", out, 8, 0, 1, major)
    out[0xC:0xE] = order
    struct.pack_into("<BBIHHII", out, 0xE, 0xC, 64, 0, 0, 0x20, 0, len(out))
    out[0x20:0x24] = platform
    struct.pack_into("<IQ", out, 0x24, len(textures), table)
    return bytes(out)


def icon_file(**fields) -> bytes:
    """A ``UI/Tex/Icon`` file: one texture in a BNTX, zstd without a dictionary."""
    return zstandard.ZstdCompressor().compress(bntx_file(texture(**fields), platform=fields.get("platform", b"Ounc")))


def png_pixels(data: bytes) -> tuple[int, int, bytes]:
    """Read back a filter-0 RGBA PNG, checking the signature, IHDR and every chunk's CRC."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    at, chunks = 8, []
    while at < len(data):
        (length,) = struct.unpack(">I", data[at : at + 4])
        kind, body = data[at + 4 : at + 8], data[at + 8 : at + 8 + length]
        assert struct.unpack(">I", data[at + 8 + length : at + 12 + length])[0] == zlib.crc32(kind + body)
        chunks.append((kind, body))
        at += 12 + length
    assert [kind for kind, _ in chunks] == [b"IHDR", b"IDAT", b"IEND"]
    width, height, depth, colour, compression, filtering, interlace = struct.unpack(">IIBBBBB", chunks[0][1])
    assert (depth, colour, compression, filtering, interlace) == (8, 6, 0, 0, 0)
    lines = zlib.decompress(chunks[1][1])
    stride = width * 4 + 1
    assert len(lines) == stride * height and all(lines[y * stride] == 0 for y in range(height))
    return width, height, b"".join(lines[y * stride + 1 : (y + 1) * stride] for y in range(height))


# --- the block-linear layout ---


@pytest.mark.parametrize(
    ("x", "y", "tegra", "turing"),
    [
        (0, 0, 0, 0),
        (0, 1, 16, 16),
        (16, 0, 32, 64),
        (0, 2, 64, 32),
        (0, 4, 128, 128),
        (16, 4, 160, 192),
        (32, 0, 256, 256),
        (17, 3, 113, 113),
        (63, 7, 511, 511),
    ],
)
def test_gob_offsets_match_the_documented_sector_grids(x, y, tegra, turing):
    assert bntx.tegra_gob_offset(x, y) == tegra
    assert bntx.turing_gob_offset(x, y) == turing
    for offset, grid in ((bntx.tegra_gob_offset, TEGRA), (bntx.turing_gob_offset, TURING)):
        assert sorted(offset(i % 64, i // 64) for i in range(512)) == list(range(512))
        assert offset(x, y) == grid[y // 2][x // 16] * 32 + (y % 2) * 16 + x % 16


@pytest.mark.parametrize(
    ("width_bytes", "rows", "block_height_log2"),
    [(64, 8, 0), (20, 3, 0), (100, 13, 1), (200, 40, 2), (96, 70, 3), (16, 129, 5), (130, 33, 2)],
)
@pytest.mark.parametrize(("gob_offset", "sectors"), [(bntx.tegra_gob_offset, TEGRA), (bntx.turing_gob_offset, TURING)])
def test_deblock_undoes_documented_tiling_at_gob_and_block_boundaries(
    width_bytes, rows, block_height_log2, gob_offset, sectors
):
    linear = noise(width_bytes * rows, width_bytes + rows)
    tiled = tile(linear, width_bytes, rows, block_height_log2, sectors)
    assert bntx.surface_size(width_bytes, rows, block_height_log2) == len(tiled)
    assert bntx.deblock(tiled, width_bytes, rows, block_height_log2, gob_offset) == linear
    assert bntx.deblock(tiled + b"\xee" * 512, width_bytes, rows, block_height_log2, gob_offset) == linear


@pytest.mark.parametrize(
    ("rows", "stored", "used"), [(8, 4, 0), (9, 4, 1), (16, 4, 1), (17, 4, 2), (86, 4, 4), (65, 5, 4), (129, 5, 5)]
)
def test_block_height_shrinks_to_cover_the_surface(rows, stored, used):
    assert bntx.effective_block_height_log2(rows, stored) == used
    linear = noise(48 * rows)
    tiled = tile(linear, 48, rows, used, TURING)
    assert bntx.deblock(tiled, 48, rows, stored, bntx.turing_gob_offset) == linear


def test_known_surface_sizes_and_truncation():
    # ASTC 4x4, 341x341: 86 rows of 86 16-byte blocks = 22 GOBs across, one block of 16 GOBs down.
    assert bntx.surface_size(86 * 16, 86, 4) == 22 * 16 * 512 == 180224
    assert bntx.surface_size(1, 1, 5) == 512
    with pytest.raises(bntx.BntxError, match="needs 0x200 bytes"):
        bntx.deblock(b"\0" * 511, 64, 8, 0, bntx.turing_gob_offset)
    with pytest.raises(bntx.BntxError, match="outside 1..32"):
        bntx.surface_size(64, 8, 6)


# --- reading and decoding textures ---


def test_uncompressed_textures_decode_with_platform_order_layers_and_channel_sources():
    pixels = noise(5 * 3 * 4, 1)
    (ounc,) = bntx.read(bntx_file(texture(pixels=pixels)))
    assert (ounc.name, ounc.platform, ounc.width, ounc.height) == ("Item_Bomb", b"Ounc", 5, 3)
    assert ounc.format_name == "R8G8B8A8"
    assert bntx.to_rgba(ounc) == (5, 3, pixels)
    tall = noise(16 * 20 * 4, 2)
    (nx,) = bntx.read(bntx_file(texture(width=16, height=20, pixels=tall, platform=b"NX  "), platform=b"NX  "))
    assert bntx.to_rgba(nx)[2] == tall
    swapped = bntx.read(bntx_file(texture(width=16, height=20, pixels=tall, platform=b"NX  ")))[0]
    assert bntx.to_rgba(swapped)[2] != tall  # Tegra-ordered data read as Switch 2 is scrambled

    (bgra,) = bntx.read(bntx_file(texture(image_format=BGRA8, pixels=pixels)))
    expected = bytes(pixels[i + (2, 1, 0, 3)[i % 4] - i % 4] for i in range(len(pixels)))
    assert bntx.to_rgba(bgra)[2] == expected
    (mapped,) = bntx.read(bntx_file(texture(pixels=pixels, sources=(5, 0, 1, 2))))
    want = bytearray(len(pixels))
    want[0::4], want[1::4], want[2::4], want[3::4] = pixels[3::4], bytes(15), b"\xff" * 15, pixels[0::4]
    assert bntx.to_rgba(mapped)[2] == bytes(want)

    first, second = noise(4 * 2 * 4, 3), noise(4 * 2 * 4, 4)
    layered = tile(first, 16, 2, 0, TURING) + tile(second, 16, 2, 0, TURING)
    (array,) = bntx.read(bntx_file(texture(width=4, height=2, data=layered, layers=2, dimension=5)))
    assert bntx.to_rgba(array) == (4, 2, first)


def test_compressed_texture_pixels_keep_channels_block_order_and_partial_edges():
    pytest.importorskip("texture2ddecoder")
    # Nine synthetic BC1 blocks, solid RGB565 endpoints and all-zero indices. No copied texture data.
    endpoints = (0xF800, 0x07E0, 0x001F, 0xFFFF, 0x0000, 0xFFE0, 0xF81F, 0x07FF, 0xF800)
    colours = (
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 255),
        (0, 0, 0),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
        (255, 0, 0),
    )
    blocks = b"".join(struct.pack("<HHI", endpoint, 0, 0) for endpoint in endpoints)
    stored = tile(blocks, 3 * 8, 3, 0, TURING)
    (compressed,) = bntx.read(bntx_file(texture(width=9, height=9, image_format=BC1, data=stored)))
    expected = b"".join(bytes((*colours[(y // 4) * 3 + x // 4], 255)) for y in range(9) for x in range(9))
    assert bntx.to_rgba(compressed) == (9, 9, expected)


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({"tile": 1}, "tile mode 1"),
        ({"image_format": BC2, "data": b"\0" * 512}, "image format 0x1b01"),
        ({"storage": 3}, "storage dimension 3"),
        ({"dimension": 3}, "texture dimension 3"),
        ({"samples": 4}, "4 samples"),
        ({"depth": 2}, "depth 2"),
        ({"sources": (6, 3, 4, 5)}, "channel sources"),
    ],
)
def test_unsupported_textures_say_why(fields, message):
    (unsupported,) = bntx.read(bntx_file(texture(**fields)))
    with pytest.raises(bntx.UnsupportedTexture, match=message):
        bntx.to_rgba(unsupported)


def _set(offset, fmt, *values):
    def change(data):
        struct.pack_into(fmt, data, offset, *values)

    return change


@pytest.mark.parametrize(
    ("change", "error", "message"),
    [
        (lambda d: d.__delitem__(slice(0x40, None)), bntx.BntxError, "too short"),
        (_set(0, "4s", b"BNTY"), bntx.BntxError, "not a BNTX"),
        (_set(0xC, "2s", b"\xfe\xff"), bntx.UnsupportedTexture, "big-endian"),
        (_set(0xC, "2s", b"\0\0"), bntx.BntxError, "byte-order"),
        (_set(0xA, "<H", 5), bntx.UnsupportedTexture, "major version 5"),
        (_set(0x1C, "<I", 1 << 30), bntx.BntxError, "the header says"),
        (_set(0x20, "4s", b"Gen "), bntx.UnsupportedTexture, "platform"),
        (_set(0x24, "<I", 0), bntx.BntxError, "texture count 0"),
        (_set(0x24, "<I", 100000), bntx.BntxError, "texture count"),
        (_set(0x28, "<Q", 1 << 40), bntx.BntxError, "pointer array"),
        (_set(0x58, "<Q", 1 << 40), bntx.BntxError, "texture 0"),
        (_set(FIRST_INFO, "4s", b"BRTX"), bntx.BntxError, "not a BRTI"),
        (_set(FIRST_INFO + 0x60, "<Q", 1 << 40), bntx.BntxError, "name"),
        (_set(FIRST_INFO + 0x24, "<I", 0), bntx.BntxError, "width 0"),
        (_set(FIRST_INFO + 0x28, "<I", 1 << 20), bntx.BntxError, "height"),
        (_set(FIRST_INFO + 0x16, "<H", 0), bntx.BntxError, "0 mip levels"),
        (_set(FIRST_INFO + 0x70, "<Q", 1 << 40), bntx.BntxError, "mip pointer array"),
        (_set(FIRST_INFO + 0x50, "<I", 1 << 30), bntx.BntxError, "image data"),
        (_set(FIRST_INFO + 0x50, "<I", 0), bntx.BntxError, "no image data"),
    ],
)
def test_malformed_files_are_refused_with_bounds_checks(change, error, message):
    data = bytearray(bntx_file(texture()))
    change(data)
    with pytest.raises(error, match=message):
        bntx.read(bytes(data))


def test_names_must_be_utf8_and_truncated_image_data_is_refused():
    with pytest.raises(bntx.BntxError, match="not UTF-8"):
        bntx.read(bntx_file(texture(name=b"\xff\xfe")))
    (short,) = bntx.read(bntx_file(texture(width=16, height=9, data=b"\0" * 512)))  # needs two GOBs down
    with pytest.raises(bntx.BntxError, match="needs 0x400 bytes"):
        bntx.to_rgba(short)


# --- PNG and names ---


def test_png_writer_is_valid_and_deterministic():
    pixels = noise(7 * 3 * 4, 9)
    png = icons.encode_png(7, 3, pixels)
    assert png_pixels(png) == (7, 3, pixels)
    assert icons.encode_png(7, 3, pixels) == png
    with pytest.raises(ValueError, match="not 7x3"):
        icons.encode_png(7, 3, pixels[:-1])


def test_only_whitelisted_names_resolve_to_icon_files():
    assert set(icons.ICON_ACTORS.values()) <= icons.ICON_IDS
    assert not set(icons.ICON_ACTORS) & icons.ICON_IDS
    assert icons.icon_id("Item_Hookshot") == "Item_Hookshot"
    assert icons.icon_id("Item_Sword_Kokiri") == "Weapon_Sword_Kokiri"
    assert icons.icon_id("TBox_Rupee_Red") == "Obj_Rupee_Red"
    refused = ("Item_Melody_SariaSong", "../Item_Bomb", "Item_Bomb.bntx.zs", "UI/Tex/Icon/Item_Bomb", "item_bomb", "")
    for name in (*refused, None, 5):
        assert icons.icon_id(name) is None


def test_default_cache_folder_is_the_users_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(icons.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    assert icons.default_cache_dir() == tmp_path / "local" / "Clawshot" / "Cache" / "icons"
    monkeypatch.setattr(icons.sys, "platform", "darwin")
    assert icons.default_cache_dir() == icons.Path.home() / "Library" / "Caches" / "Clawshot" / "icons"
    monkeypatch.setattr(icons.sys, "platform", "linux")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg"))
    assert icons.default_cache_dir() == tmp_path / "xdg" / "clawshot" / "icons"
    monkeypatch.setenv("XDG_CACHE_HOME", "relative")
    assert icons.default_cache_dir() == icons.Path.home() / ".cache" / "clawshot" / "icons"


# --- the cache ---


def romfs_with(root, files: dict[str, bytes]):
    for name, data in files.items():
        path = root / "UI" / "Tex" / "Icon" / f"{name}.bntx.zs"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return root


def tree(root):
    return sorted((p.relative_to(root).as_posix(), p.read_bytes()) for p in root.rglob("*") if p.is_file())


def test_icons_decode_once_into_the_cache_and_are_reused(tmp_path, monkeypatch):
    pixels = noise(5 * 3 * 4, 11)
    source = romfs_with(tmp_path / "romfs", {"Item_Bomb": icon_file(pixels=pixels)})
    before = tree(source)
    cache = icons.IconCache(source, cache_dir=tmp_path / "cache")
    path = cache.get("Pouch_Bomb")
    assert path is not None and path.parent == tmp_path / "cache"
    assert path.name.startswith("Item_Bomb.") and path.name.endswith(f".v{icons.CACHE_VERSION}.png")
    assert png_pixels(path.read_bytes()) == (5, 3, pixels)
    assert cache.get("Item_Bomb") == path and cache.problems == {}
    assert cache.status()["kind"] == "romfs"
    assert tree(source) == before  # the dump is only read

    monkeypatch.setattr(icons, "icon_png", lambda *_: pytest.fail("decoded again"))
    assert icons.IconCache(source, cache_dir=tmp_path / "cache").get("Obj_Bomb") == path


def test_a_changed_source_file_is_decoded_again_and_its_old_png_removed(tmp_path):
    source = romfs_with(tmp_path / "romfs", {"Item_Bomb": icon_file(pixels=noise(60, 1))})
    cache = icons.IconCache(source, cache_dir=tmp_path / "cache")
    old = cache.get("Item_Bomb")
    changed = noise(16 * 2 * 4, 2)
    romfs_with(source, {"Item_Bomb": icon_file(width=16, height=2, pixels=changed)})
    new = cache.get("Item_Bomb")
    assert new != old and not old.exists()
    assert png_pixels(new.read_bytes()) == (16, 2, changed)
    assert [p.name for p in (tmp_path / "cache").iterdir()] == [new.name]


def test_dump_folders_take_the_newest_update_over_the_base(tmp_path):
    base, update = noise(60, 3), noise(60, 4)
    dump = tmp_path / "dump"
    romfs_with(dump / "base" / "romfs", {"Item_Bomb": icon_file(pixels=base), "Item_Bombchu": icon_file(pixels=base)})
    romfs_with(dump / "updates" / "131072" / "romfs", {"Item_Bomb": icon_file(pixels=update)})
    romfs_with(dump / "updates" / "65536" / "romfs", {"Item_Bombchu": icon_file(pixels=update)})
    cache = icons.IconCache(dump, cache_dir=tmp_path / "cache")
    assert cache.status()["kind"] == "dump"
    assert png_pixels(cache.get("Item_Bomb").read_bytes())[2] == update
    assert png_pixels(cache.get("Item_Bombchu").read_bytes())[2] == base


def test_a_nup_is_read_in_place_and_closed(tmp_path):
    pixels = noise(60, 5)
    stored = icon_file(pixels=pixels)
    nup = write_nup(tmp_path / "game.nup", [(131072, 1, {"UI/Tex/Icon/Item_Bomb.bntx.zs": stored, "other": b"x"})])
    cache = icons.IconCache(nup, cache_dir=tmp_path / "cache")
    path = cache.get("Pouch_Bomb")
    assert png_pixels(path.read_bytes())[2] == pixels and cache.status()["kind"] == "nup"
    folder = icons.IconCache(romfs_with(tmp_path / "romfs", {"Item_Bomb": stored}), cache_dir=tmp_path / "other")
    assert folder.get("Item_Bomb").name == path.name  # named by the stored file's content, whatever the source
    assert cache.get("Item_Bombchu") is None
    assert "no romfs/UI/Tex/Icon/Item_Bombchu.bntx.zs" in cache.problems["Item_Bombchu"]
    nup.rename(tmp_path / "closed.nup")  # no leaked handle (Windows)


def test_every_failure_falls_back_to_text_with_a_reason(tmp_path, monkeypatch):
    source = romfs_with(
        tmp_path / "romfs",
        {
            "Item_Bomb": b"not zstd",
            "Item_Bombchu": icon_file(tile=1),
            "Item_Hookshot": icon_file(width=8, height=8, image_format=ASTC_4X4_SRGB, data=b"\0" * 512),
            "Item_Longshot": zstandard.ZstdCompressor().compress(b"BNTX"),
        },
    )
    monkeypatch.setattr(bntx, "load_decoder", lambda: None)
    cache = icons.IconCache(source, cache_dir=tmp_path / "cache")
    names = ["Item_Bomb", "Item_Bombchu", "Item_Hookshot", "Item_Longshot", "Item_Boomerang", "Item_Melody_TimeSong"]
    assert [cache.get(name) for name in names] == [None] * len(names)
    problems = cache.problems
    assert set(problems) == set(names)
    assert "tile mode 1" in problems["Item_Bombchu"]
    assert "texture2ddecoder" in problems["Item_Hookshot"] and "ui extra" in problems["Item_Hookshot"]
    assert "too short" in problems["Item_Longshot"]
    assert "no romfs/UI/Tex/Icon/Item_Boomerang.bntx.zs" in problems["Item_Boomerang"]
    assert not list((tmp_path / "cache").glob("*.png"))

    missing = icons.IconCache(tmp_path / "nowhere", cache_dir=tmp_path / "cache")
    assert missing.get("Item_Bomb") is None and "is not there" in missing.problems["Item_Bomb"]
    assert missing.status()["kind"] is None

    romfs_with(source, {"Item_Bomb": icon_file()})
    assert cache.get("Item_Bomb") is not None and "Item_Bomb" not in cache.problems


def test_the_cache_folder_stays_outside_the_dump_and_the_checkout(tmp_path):
    source = romfs_with(tmp_path / "romfs", {"Item_Bomb": icon_file()})
    with pytest.raises(ValueError, match="outside"):
        icons.IconCache(source, cache_dir=source / "UI" / "cache")
    with pytest.raises(ValueError, match="outside"):
        icons.IconCache(source, cache_dir=ROOT / "icon-cache")
    assert not (ROOT / "icon-cache").exists()


def test_threads_share_one_decode(tmp_path):
    source = romfs_with(tmp_path / "romfs", {"Item_Bomb": icon_file(width=64, height=64)})
    cache = icons.IconCache(source, cache_dir=tmp_path / "cache")
    results = []
    threads = [threading.Thread(target=lambda: results.append(cache.get("Pouch_Bomb"))) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(set(results)) == 1 and None not in results
    assert len(os.listdir(tmp_path / "cache")) == 1
