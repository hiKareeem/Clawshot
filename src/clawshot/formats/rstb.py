"""The resource size table (``System/Resource/ResourceSizeTable.Product.111.Nin_Ounce_NVN2.rsizetable.zs``).

The game sizes a file's load buffer from this table, as Tears of the Kingdom's RESTBL does. The file is plain zstd
around, little-endian:

- header (22 bytes): magic ``RESTBL``, u32 version (1), u32 name field size (160), u32 hash entry count, u32 name
  entry count;
- hash entries, sorted by hash: u32 CRC32 of the resource path, u32 size;
- name entries, sorted by name: the resource path, NUL-padded to the name field size, u32 size. These hold paths
  whose CRC32 collides with another path's.

The resource path is the romfs path without ``.zs`` (:func:`resource_path`). A path in the name entries is looked up
by name, any other by CRC32.
"""

import struct
import zlib
from dataclasses import dataclass, field

TABLE_PATH = "System/Resource/ResourceSizeTable.Product.111.Nin_Ounce_NVN2.rsizetable.zs"
MAGIC = b"RESTBL"
_HEADER = struct.Struct("<6sIIII")
_HASH_ENTRY = struct.Struct("<II")

# Resource path suffix -> what an entry adds to the file size rounded up to 32 bytes, for the types checked against
# every such file in the game (build e0f3ccfa; plans/03-game-data.md, section 11). Other types are not covered.
OVERHEAD: dict[str, int] = {
    ".bcett.byml": 264,  # placement files (160 of 160)
    ".bfevfl": 272,  # event flows (914 of 914)
    ".sarc": 312,  # message archives (16 of 16)
    ".pack": 312,  # packs (8384 of 8384 that have an entry; Pack/ZsDic.pack.zs has none)
}
ALIGNMENT = 32

# Files with a formula of their own: resource path -> (alignment, overhead). GameDataList is one file: its entry
# (1,463,176) is its size (1,462,888, a multiple of 8) + 288, which rounding to 32 would overshoot.
OWN_FORMULA: dict[str, tuple[int, int]] = {
    "GameData/GameDataList.Product.110.byml": (8, 288),
    # ActorInfo: 1,934,492 raw -> 1,937,560; Round 7 same-shape model/heap field substitutions only.
    "RSDB/ActorInfo.Product.111.rstbl.byml": (32, 3064),
    # Round 12: EventSetting 509212 -> 509480; same +264 observed in 19/19
    # non-ActorInfo RSDB tables; growth is enabled for these two event registries.
    "RSDB/EventSetting.Product.111.rstbl.byml": (32, 264),
    # The matching analyzed-event registry: 247276 raw -> 247560 allocated.
    "RSDB/GameAnalyzedEventInfo.Product.111.rstbl.byml": (32, 264),
    # R13 native new-game Sequence: 5916 raw -> 6296 allocated, rounded32 +376.
    # 107/108 native Sequence AINBs share this overhead; not a generic AINB rule.
    "Sequence/SetPouchAndStatusForGameStart.module.ainb": (32, 376),
}


class RstbError(ValueError):
    pass


@dataclass
class ResourceSizeTable:
    hashes: dict[int, int] = field(default_factory=dict)  # CRC32 of the resource path -> size
    names: dict[str, int] = field(default_factory=dict)  # resource path -> size, for paths whose CRC32 collides
    version: int = 1
    name_size: int = 160

    def get(self, path: str) -> int | None:
        """The entry for a resource path (or a romfs path with ``.zs``), or None when the table has none."""
        path = resource_path(path)
        if path in self.names:
            return self.names[path]
        return self.hashes.get(path_hash(path))

    def set(self, path: str, size: int) -> None:
        """Set the entry for a resource path (or a romfs path with ``.zs``); a new path gets a hash entry."""
        if not 0 <= size <= 0xFFFFFFFF:
            raise RstbError(f"size {size} for {path} does not fit in 32 bits")
        path = resource_path(path)
        if path in self.names:
            self.names[path] = size
        else:
            self.hashes[path_hash(path)] = size


def resource_path(path: str) -> str:
    """``Banc/A/A_Static.bcett.byml.zs`` -> ``Banc/A/A_Static.bcett.byml``: the key the table uses."""
    return path.removesuffix(".zs")


def path_hash(path: str) -> int:
    return zlib.crc32(resource_path(path).encode("utf-8"))


def read(data: bytes) -> ResourceSizeTable:
    """Parse a decompressed table."""
    if len(data) < _HEADER.size:
        raise RstbError(f"too short for a RESTBL header: {len(data)} bytes")
    magic, version, name_size, hash_count, name_count = _HEADER.unpack_from(data, 0)
    if magic != MAGIC:
        raise RstbError(f"not a RESTBL: magic {magic!r}")
    if version != 1:
        raise RstbError(f"RESTBL version {version} is not supported (only 1)")
    name_entry = struct.Struct(f"<{name_size}sI")
    expected = _HEADER.size + hash_count * _HASH_ENTRY.size + name_count * name_entry.size
    if len(data) != expected:
        raise RstbError(
            f"RESTBL of {hash_count} hash and {name_count} name entries is {expected} bytes, not {len(data)}"
        )
    table = ResourceSizeTable(version=version, name_size=name_size)
    offset = _HEADER.size
    for _ in range(hash_count):
        crc, size = _HASH_ENTRY.unpack_from(data, offset)
        if crc in table.hashes:
            raise RstbError(f"hash 0x{crc:08x} appears twice")
        table.hashes[crc] = size
        offset += _HASH_ENTRY.size
    for _ in range(name_count):
        raw_name, size = name_entry.unpack_from(data, offset)
        name = raw_name.split(b"\0", 1)[0].decode("utf-8")
        if name in table.names:
            raise RstbError(f"name {name!r} appears twice")
        table.names[name] = size
        offset += name_entry.size
    return table


def write(table: ResourceSizeTable) -> bytes:
    """The decompressed table, entries sorted (hashes by value, names by UTF-8 bytes) as the game's are."""
    name_entry = struct.Struct(f"<{table.name_size}sI")
    out = bytearray(_HEADER.pack(MAGIC, table.version, table.name_size, len(table.hashes), len(table.names)))
    for crc in sorted(table.hashes):
        out += _HASH_ENTRY.pack(crc, table.hashes[crc])
    for name in sorted(table.names, key=lambda n: n.encode("utf-8")):
        encoded = name.encode("utf-8")
        if len(encoded) >= table.name_size:
            raise RstbError(f"name {name!r} does not fit the {table.name_size}-byte name field with its NUL")
        out += name_entry.pack(encoded, table.names[name])
    return bytes(out)


def required_size(path: str, size: int) -> int:
    """The entry a file at ``path`` (resource or romfs path) needs when its decompressed size is ``size``:
    ``size`` rounded up to 32 bytes plus the overhead of its type (:data:`OVERHEAD`), or a file's own formula
    (:data:`OWN_FORMULA`).

    Raises :class:`RstbError` for a type whose formula has not been checked against the game.
    """
    path = resource_path(path)
    if path in OWN_FORMULA:
        alignment, overhead = OWN_FORMULA[path]
        return (size + alignment - 1) // alignment * alignment + overhead
    for suffix, overhead in OVERHEAD.items():
        if path.endswith(suffix):
            return (size + ALIGNMENT - 1) // ALIGNMENT * ALIGNMENT + overhead
    raise RstbError(f"no size formula for {path}: only {', '.join(OVERHEAD)} are checked against the game")
