"""SARC archives (little-endian, as on Switch): read to and write from ``{name: bytes}``.

Layout: a 0x14-byte ``SARC`` header, ``SFAT`` (one 16-byte node per file, sorted by name hash), ``SFNT`` (names,
each null-terminated and padded to 4 bytes), then the file data, each file aligned.
"""

import struct

HASH_KEY = 0x65
_HEADER = struct.Struct("<4sHHIIHH")
_SFAT = struct.Struct("<4sHHI")
_NODE = struct.Struct("<IIII")
_SFNT = struct.Struct("<4sHH")


class SarcError(ValueError):
    pass


def name_hash(name: str, key: int = HASH_KEY) -> int:
    h = 0
    for b in name.encode("utf-8"):
        c = b - 0x100 if b >= 0x80 else b  # the game hashes signed chars
        h = (h * key + c) & 0xFFFFFFFF
    return h


def read(data: bytes) -> dict[str, bytes]:
    """Return the archive's files by name, in the order of the file table."""
    magic, header_size, bom, _size, data_offset, _version, _ = _HEADER.unpack_from(data, 0)
    if magic != b"SARC":
        raise SarcError(f"not a SARC archive: magic {magic!r}")
    if bom != 0xFEFF:
        raise SarcError(f"only little-endian SARC is supported (BOM bytes {data[6:8].hex()})")
    sfat = header_size
    magic, sfat_size, count, _key = _SFAT.unpack_from(data, sfat)
    if magic != b"SFAT":
        raise SarcError(f"SFAT missing at 0x{sfat:x}: {magic!r}")
    nodes = [_NODE.unpack_from(data, sfat + sfat_size + _NODE.size * i) for i in range(count)]
    sfnt = sfat + sfat_size + _NODE.size * count
    magic, sfnt_size, _ = _SFNT.unpack_from(data, sfnt)
    if magic != b"SFNT":
        raise SarcError(f"SFNT missing at 0x{sfnt:x}: {magic!r}")
    names = sfnt + sfnt_size
    files: dict[str, bytes] = {}
    for _hash, attr, start, end in nodes:
        if not attr >> 24:
            raise SarcError(f"unnamed SARC node (hash 0x{_hash:08x}) is not supported")
        name_at = names + (attr & 0xFFFF) * 4
        name = data[name_at : data.index(b"\0", name_at)].decode("utf-8")
        files[name] = bytes(data[data_offset + start : data_offset + end])
    return files


def _align(n: int, a: int) -> int:
    return (n + a - 1) // a * a


def write(files: dict[str, bytes], alignment: int = 8) -> bytes:
    """Build a SARC holding ``files``; each file's data starts at a multiple of ``alignment``."""
    order = sorted(files, key=name_hash)
    hashes = [name_hash(n) for n in order]
    if len(set(hashes)) != len(hashes):
        raise SarcError("two names share a hash; this writer does not support hash collisions")
    name_table = bytearray()
    name_offsets = []
    for name in order:
        name_offsets.append(len(name_table) // 4)
        name_table += name.encode("utf-8") + b"\0"
        name_table += b"\0" * (_align(len(name_table), 4) - len(name_table))
    sfat = _HEADER.size
    sfnt = sfat + _SFAT.size + _NODE.size * len(order)
    data_offset = _align(sfnt + _SFNT.size + len(name_table), alignment)
    blob = bytearray()
    nodes = bytearray()
    for name, h, name_off in zip(order, hashes, name_offsets, strict=True):
        blob += b"\0" * (_align(len(blob), alignment) - len(blob))
        start = len(blob)
        blob += files[name]
        nodes += _NODE.pack(h, 0x01000000 | name_off, start, len(blob))
    out = bytearray()
    out += _HEADER.pack(b"SARC", _HEADER.size, 0xFEFF, data_offset + len(blob), data_offset, 0x0100, 0)
    out += _SFAT.pack(b"SFAT", _SFAT.size, len(order), HASH_KEY) + nodes
    out += _SFNT.pack(b"SFNT", _SFNT.size, 0) + name_table
    out += b"\0" * (data_offset - len(out))
    out += blob
    return bytes(out)
