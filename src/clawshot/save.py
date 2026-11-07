"""Read-only reader of the game's save files (``slot_NN/progress.sav`` and the other files named in
``GameDataList``'s ``MetaData.SaveDirectory``).

Layout, as found in the game's own saves (Tears of the Kingdom's layout):

- A 0x20-byte header: u32 magic ``0x01020304``, u32 version, u32 offset of the end of the entry table (where the
  data area starts), zero padding.
- The entry table: (u32 key, u32 value) pairs, little-endian. A pair with key 0 opens a section; its value is the type
  index (:data:`TYPES`). Every other key is the murmur3 hash (x86, 32-bit, seed 0) of a flag's name, as in
  ``GameDataList``. Bool, Int, UInt, Float and Enum values are stored in the pair; for the other types the value is
  an offset into the file.
- Section 32 (``Bool64bitKey``) holds one pair, keyed by the save file's type hash (``MetaData.SaveTypeHash``); its
  value is the offset of the 64-bit keys whose flag is set, as u64, ending with a 0. Placement checks key these flags
  by the actor ``Hash`` (plans/03-game-data.md, section 6).

The reader never writes. Array, string and binary values are left as their offsets (:attr:`Save.entries`).
"""

import struct
from dataclasses import dataclass
from pathlib import Path

MAGIC = 0x01020304
HEADER_SIZE = 0x20

# Section type index -> GameDataList type. Each index below is confirmed by the game's saves (a section holds only
# hashes of GameDataList entries of that type) except the ones marked: those sections were empty and their names
# follow the order of the confirmed ones (Tears of the Kingdom's order).
TYPES = {
    0: "Bool",
    1: "BoolArray",
    2: "Int",
    3: "IntArray",
    4: "Float",
    5: "FloatArray",
    6: "Enum",
    7: "EnumArray",
    8: "Vector2",  # unconfirmed
    9: "Vector2Array",  # unconfirmed
    10: "Vector3",
    11: "Vector3Array",  # unconfirmed
    12: "String16",  # unconfirmed
    13: "String16Array",  # unconfirmed
    14: "String32",
    15: "String32Array",  # unconfirmed
    16: "String64",
    17: "String64Array",
    18: "Binary",
    19: "BinaryArray",
    20: "UInt",
    21: "UIntArray",
    22: "Int64",
    23: "Int64Array",  # unconfirmed
    24: "UInt64",
    25: "UInt64Array",
    26: "WString16",  # unconfirmed
    27: "WString16Array",
    28: "WString32",  # unconfirmed
    29: "WString32Array",  # unconfirmed
    30: "WString64",  # unconfirmed
    31: "WString64Array",  # unconfirmed
    32: "Bool64bitKey",
}
BOOL, INT, FLOAT, ENUM, UINT, BOOL64 = 0, 2, 4, 6, 20, 32


class SaveError(ValueError):
    pass


def murmur3_32(data: bytes, seed: int = 0) -> int:
    """MurmurHash3, x86 32-bit: the key of a named flag (``murmur3_32(name.encode())``)."""
    c1, c2, mask = 0xCC9E2D51, 0x1B873593, 0xFFFFFFFF

    def mix(k: int) -> int:
        k = (k * c1) & mask
        k = ((k << 15) | (k >> 17)) & mask
        return (k * c2) & mask

    h = seed & mask
    blocks = len(data) // 4
    for (k,) in struct.iter_unpack("<I", data[: blocks * 4]):
        h ^= mix(k)
        h = ((h << 13) | (h >> 19)) & mask
        h = (h * 5 + 0xE6546B64) & mask
    tail = data[blocks * 4 :]
    if tail:
        h ^= mix(int.from_bytes(tail, "little"))
    h ^= len(data)
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & mask
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & mask
    return h ^ (h >> 16)


def key(name: str | int) -> int:
    return name if isinstance(name, int) else murmur3_32(name.encode("utf-8"))


@dataclass(frozen=True)
class Save:
    version: int
    entries: dict[int, dict[int, int]]  # section type -> {key: raw u32 value}
    save_type: int | None  # the Bool64bitKey section's key (the save file's type hash)
    set_keys: frozenset[int]  # Bool64bitKey flags that are set

    def _raw(self, section: int, name: str | int) -> int | None:
        return self.entries.get(section, {}).get(key(name))

    def flag(self, name: str | int) -> bool | None:
        """A Bool flag by name or key; None when the save has no such entry."""
        raw = self._raw(BOOL, name)
        return None if raw is None else raw != 0

    def int_value(self, name: str | int) -> int | None:
        raw = self._raw(INT, name)
        if raw is None:
            return None
        return raw - (1 << 32) if raw & 0x80000000 else raw

    def uint_value(self, name: str | int) -> int | None:
        return self._raw(UINT, name)

    def float_value(self, name: str | int) -> float | None:
        raw = self._raw(FLOAT, name)
        return None if raw is None else struct.unpack("<f", struct.pack("<I", raw))[0]

    def enum_value(self, name: str | int) -> int | None:
        """The key of the enum's current value (murmur3 of the value's name)."""
        return self._raw(ENUM, name)

    def is_set(self, key64: int) -> bool:
        """Whether the Bool64bitKey flag with this key (for placement checks, the actor Hash) is set."""
        return key64 in self.set_keys


def read(data: bytes) -> Save:
    if len(data) < HEADER_SIZE:
        raise SaveError(f"{len(data)} bytes, shorter than the header")
    magic, version, table_end = struct.unpack_from("<III", data, 0)
    if magic != MAGIC:
        raise SaveError(f"magic 0x{magic:08x}, expected 0x{MAGIC:08x}")
    if not HEADER_SIZE <= table_end <= len(data) or (table_end - HEADER_SIZE) % 8:
        raise SaveError(f"entry table ends at 0x{table_end:x} in a file of 0x{len(data):x} bytes")

    entries: dict[int, dict[int, int]] = {}
    section = None
    for k, v in struct.iter_unpack("<II", data[HEADER_SIZE:table_end]):
        if k == 0:
            if v not in TYPES:
                raise SaveError(f"section type {v} is not known")
            section = v
            entries.setdefault(section, {})
        elif section is None:
            raise SaveError(f"entry 0x{k:08x} before the first section")
        else:
            entries[section][k] = v

    bool64 = entries.get(BOOL64, {})
    if len(bool64) > 1:
        raise SaveError(f"Bool64bitKey section has {len(bool64)} entries, expected one")
    save_type, set_keys = None, []
    if bool64:
        [(save_type, offset)] = bool64.items()
        pos = offset
        while True:
            if pos + 8 > len(data):
                raise SaveError(f"Bool64bitKey list at 0x{offset:x} runs past the end of the file")
            (k64,) = struct.unpack_from("<Q", data, pos)
            pos += 8
            if k64 == 0:
                break
            set_keys.append(k64)
    return Save(version, entries, save_type, frozenset(set_keys))


def load(path: str | Path) -> Save:
    """Read a save file (opened read-only)."""
    with open(path, "rb") as f:
        return read(f.read())
