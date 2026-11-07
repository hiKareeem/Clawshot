import struct

import pytest

from clawshot.formats import byml
from clawshot.formats.byml import F32, F64, I32, I64, U32, U64, Hash32Map, Hash64Map


def round_trip(tree):
    data = byml.write(tree)
    back = byml.read(data)
    assert byml.difference(tree, back) is None, byml.difference(tree, back)
    assert byml.write(back) == data
    return back


def header(data: bytes) -> tuple[int, int, int]:
    return struct.unpack_from("<III", data, 4)


def entry_raw(data: bytes, map_off: int, index: int) -> tuple[int, int, int]:
    """(key index, value type, raw value) of a map entry."""
    kv, raw = struct.unpack_from("<II", data, map_off + 4 + 8 * index)
    return kv & 0xFFFFFF, kv >> 24, raw


EVERY_TYPE = {
    "string": "Obj_TBox_Small",
    "unicode": "デクの樹",
    "empty_string": "",
    "array": [I32(1), "two", F32(3.5), [U32(4)], {"k": None}],
    "map": {"Gyaml": "Obj_TBox", "Translate": [F32(1.25), F32(-0.5), F32(1e30)]},
    "hash32": Hash32Map({0xDEADBEEF: "a", 0: I32(-1), 7: [True]}),
    "hash64": Hash64Map({0xFFFFFFFFFFFFFFFF: U64(1), 1: {"x": False}}),
    "bool_true": True,
    "bool_false": False,
    "i32_min": I32(-(1 << 31)),
    "i32_max": I32((1 << 31) - 1),
    "f32": F32(0.1),
    "f32_negzero": F32(-0.0),
    "u32_max": U32(0xFFFFFFFF),
    "i64_min": I64(-(1 << 63)),
    "u64_max": U64((1 << 64) - 1),
    "u64_hash": U64(0x0123456789ABCDEF),
    "f64": F64(0.1),
    "null": None,
    "empty_array": [],
    "empty_map": {},
}


def test_every_node_type_round_trips_with_its_type():
    back = round_trip(EVERY_TYPE)
    assert type(back["i32_min"]) is I32
    assert type(back["f32"]) is F32
    assert type(back["u32_max"]) is U32
    assert type(back["i64_min"]) is I64
    assert type(back["u64_max"]) is U64
    assert type(back["f64"]) is F64
    assert type(back["hash32"]) is Hash32Map
    assert type(back["hash64"]) is Hash64Map
    assert back["bool_true"] is True
    assert back["null"] is None
    assert back["f64"] == 0.1
    assert back["f32"] == struct.unpack("<f", struct.pack("<f", 0.1))[0]


@pytest.mark.parametrize("root", [[I32(5), "x"], Hash32Map({3: "y"}), Hash64Map({1 << 40: [I64(-2)]}), {}, []])
def test_other_roots(root):
    round_trip(root)


def test_plain_python_numbers_read_back_as_int32_and_float32():
    back = byml.read(byml.write({"i": 3, "f": 1.5}))
    assert type(back["i"]) is I32
    assert type(back["f"]) is F32


def test_same_value_with_another_type_is_a_difference():
    assert byml.same({"a": [U64(1)]}, {"a": [U64(1)]})
    assert "/a/0" in byml.difference({"a": [U64(1)]}, {"a": [I64(1)]})
    assert byml.difference({"a": I32(1)}, {"a": U32(1)}) is not None
    assert byml.difference({"a": F32(1)}, {"a": F64(1)}) is not None
    assert byml.difference({"a": True}, {"a": I32(1)}) is not None
    assert byml.difference(Hash32Map({1: "x"}), {"1": "x"}) is not None


def test_exact_layout():
    # header, key table, string table, 8-byte values, then containers depth first from the root
    data = byml.write({"b": [I32(-1), "x"], "a": U64(5)})
    keys = struct.pack("<I3I", 0xC2 | 2 << 8, 16, 18, 20) + b"a\0b\0"
    strings = struct.pack("<I2I", 0xC2 | 1 << 8, 12, 14) + b"x\0" + b"\0\0"
    longs = struct.pack("<Q", 5)
    root = struct.pack("<IIIII", 0xC1 | 2 << 8, 0 | 0xD5 << 24, 0x34, 1 | 0xC0 << 24, 0x50)
    array = struct.pack("<I4BII", 0xC0 | 2 << 8, 0xD1, 0xA0, 0, 0, 0xFFFFFFFF, 0)
    expected = b"YB" + struct.pack("<HIII", 7, 0x10, 0x24, 0x3C) + keys + strings + longs + root + array
    assert data == expected


def test_map_entries_are_written_in_key_byte_order():
    data = byml.write({"b": I32(1), "a": I32(2), "B": I32(3), "é": I32(4)})
    root = header(data)[2]
    assert [entry_raw(data, root, i)[0] for i in range(4)] == [0, 1, 2, 3]
    assert list(byml.read(data)) == ["B", "a", "b", "é"]


def test_equal_containers_and_8_byte_values_are_stored_once():
    shared = {"Rotate": [F32(0), F32(90), F32(0)], "Hash": U64(42)}
    tree = {"a": shared, "b": {"Rotate": [F32(0), F32(90), F32(0)], "Hash": U64(42)}, "c": {"ID": U64(42)}}
    data = byml.write(tree)
    root = header(data)[2]
    a, b, c = (entry_raw(data, root, i)[2] for i in range(3))
    assert a == b
    assert entry_raw(data, a, 0)[2] == entry_raw(data, c, 0)[2]  # Hash and ID share one 8-byte value
    assert data.count(struct.pack("<Q", 42)) == 1
    round_trip(tree)


def test_equal_values_of_different_types_are_not_merged():
    data = byml.write({"a": [I32(1)], "b": [U32(1)], "c": [F32(1.0)], "d": [True]})
    root = header(data)[2]
    assert len({entry_raw(data, root, i)[2] for i in range(4)}) == 4


def test_write_rejects_bad_values():
    with pytest.raises(byml.BymlError, match="int32"):
        byml.write({"a": 1 << 31})
    with pytest.raises(byml.BymlError, match="uint32"):
        U32(-1)
    with pytest.raises(byml.BymlError, match="not a string"):
        byml.write({1: "x"})
    with pytest.raises(byml.BymlError, match="32 bits"):
        byml.write(Hash32Map({1 << 32: "x"}))
    with pytest.raises(byml.BymlError, match="root"):
        byml.write("x")
    with pytest.raises(byml.BymlError, match="no BYML node type"):
        byml.write({"a": b"bytes"})


def test_read_rejects_other_versions_and_formats():
    data = bytearray(byml.write({"a": I32(1)}))
    data[2] = 2
    with pytest.raises(byml.BymlError, match="version 2"):
        byml.read(bytes(data))
    with pytest.raises(byml.BymlError, match="magic"):
        byml.read(b"BY" + bytes(14))


def test_unsupported_node_type_is_named():
    data = bytearray(byml.write({"a": I32(1)}))
    root = header(data)[2]
    data[root + 4 + 3] = 0xA1  # binary data, not seen in the game's placement files
    with pytest.raises(byml.BymlError, match="0xa1"):
        byml.read(bytes(data))
