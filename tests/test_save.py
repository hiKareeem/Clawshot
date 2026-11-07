import struct

import pytest

from clawshot import save
from clawshot.save import BOOL, BOOL64, ENUM, FLOAT, INT, UINT, SaveError, murmur3_32

SAVE_TYPE = 0xA1B2C3D4
CHEST = 2**64 - 7  # a 64-bit actor Hash
GS = 1234567890123456789


def build(sections: dict[int, dict[int, int]], keys: list[int], magic: int = save.MAGIC, terminate: bool = True):
    """A synthetic save: header, entry table (sections in type order, Bool64bitKey last), then the key list."""
    table = b""
    for section in sorted(s for s in sections if s != BOOL64):
        table += struct.pack("<II", 0, section)
        for k, v in sections[section].items():
            table += struct.pack("<II", k, v)
    table_end = save.HEADER_SIZE + len(table) + 16
    table += struct.pack("<II", 0, BOOL64) + struct.pack("<II", SAVE_TYPE, table_end)
    header = struct.pack("<III", magic, 0x2D80EB, table_end).ljust(save.HEADER_SIZE, b"\0")
    data = b"".join(struct.pack("<Q", k) for k in keys) + (struct.pack("<Q", 0) if terminate else b"")
    return header + table + data


@pytest.mark.parametrize(
    ("text", "expected"),
    [("", 0), ("hello", 0x248BFA47), ("The quick brown fox jumps over the lazy dog", 0x2E4FF723), ("abc", 0xB3DD93FA)],
)
def test_murmur3(text, expected):
    assert murmur3_32(text.encode()) == expected


def test_values_by_name_and_set_keys():
    sections = {
        BOOL: {murmur3_32(b"IsGet.Obj_Heart_Piece"): 1, murmur3_32(b"Off"): 0},
        INT: {murmur3_32(b"Life"): 16, murmur3_32(b"Negative"): 0xFFFFFFFE},
        FLOAT: {murmur3_32(b"Speed"): struct.unpack("<I", struct.pack("<f", 1.5))[0]},
        ENUM: {murmur3_32(b"Age"): murmur3_32(b"Child")},
        UINT: {murmur3_32(b"Count"): 0xFFFFFFFF},
    }
    s = save.read(build(sections, [CHEST, GS]))
    assert s.flag("IsGet.Obj_Heart_Piece") is True and s.flag("Off") is False and s.flag("Missing") is None
    assert (s.int_value("Life"), s.int_value("Negative"), s.uint_value("Count")) == (16, -2, 0xFFFFFFFF)
    assert s.float_value("Speed") == 1.5
    assert s.enum_value("Age") == murmur3_32(b"Child")
    assert s.save_type == SAVE_TYPE
    assert s.is_set(CHEST) and s.is_set(GS) and not s.is_set(CHEST - 1)


def test_empty_key_list():
    s = save.read(build({BOOL: {}}, []))
    assert s.set_keys == frozenset()


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (build({BOOL: {}}, [], magic=0x04030201), "magic"),
        (build({BOOL: {}}, [CHEST], terminate=False), "runs past the end"),
        (b"\0" * 8, "shorter than the header"),
        (struct.pack("<III", save.MAGIC, 1, 0x24).ljust(0x24, b"\0"), "entry table ends"),
        (struct.pack("<III", save.MAGIC, 1, 0x28).ljust(0x20, b"\0") + struct.pack("<II", 5, 1), "before the first"),
        (struct.pack("<III", save.MAGIC, 1, 0x28).ljust(0x20, b"\0") + struct.pack("<II", 0, 99), "type 99"),
    ],
)
def test_malformed_saves_are_rejected(data, message):
    with pytest.raises(SaveError, match=message):
        save.read(data)
