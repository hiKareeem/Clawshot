import struct

import pytest

from clawshot.formats import msbt
from clawshot.formats.msbt import Msbt, MsbtError, Tag, TagEnd


def _section(magic: bytes, body: bytes) -> bytes:
    out = magic + struct.pack("<I", len(body)) + bytes(8) + body
    return out + b"\xab" * (-len(out) % 16)


def _hand_built() -> bytes:
    """Two labels in bucket 1 of two, a third alone in bucket 0, built byte by byte."""
    labels = ["Ac", "Ca", "B"]  # indices 0, 1, 2
    assert [msbt.label_hash(x) % 2 for x in labels] == [1, 1, 0]
    entries0 = b"\x01B" + struct.pack("<I", 2)
    entries1 = b"\x02Ac" + struct.pack("<I", 0) + b"\x02Ca" + struct.pack("<I", 1)
    lbl = struct.pack("<I", 2) + struct.pack("<II", 1, 20) + struct.pack("<II", 2, 20 + len(entries0))
    lbl += entries0 + entries1
    texts = [
        b"Hi\n\0",
        b"\x0e"
        + struct.pack("<HHH", 0, 3, 2)
        + b"\x01\x00"
        + "é".encode()
        + b"\x0f"
        + struct.pack("<HH", 0, 3)
        + b"\0",
        b"\x0e" + struct.pack("<HHH", 2, 23, 0) + b"\0",
    ]
    offsets = [16, 16 + len(texts[0]), 16 + len(texts[0]) + len(texts[1])]
    txt = struct.pack("<4I", 3, *offsets) + b"".join(texts)
    body = _section(b"LBL1", lbl) + _section(b"TXT2", txt)
    header = b"MsgStdBn" + struct.pack("<HHBBHHI", 0xFEFF, 0, 0, 3, 2, 0, 32 + len(body)) + bytes(10)
    return header + body


def test_reads_hand_built_file():
    m = msbt.read(_hand_built())
    assert m.buckets == 2
    assert m.messages == {
        "Ac": ["Hi\n"],
        "Ca": [Tag(0, 3, b"\x01\x00"), "é", TagEnd(0, 3)],
        "B": [Tag(2, 23)],
    }
    assert msbt.plain(m.messages["Ca"]) == "é"


def test_writes_hand_built_file_byte_identical():
    data = _hand_built()
    assert msbt.write(msbt.read(data)) == data


def test_bucket_entries_follow_message_index_not_insertion_into_bucket():
    # "Ca" (index 0) and "Ac" (index 1) share bucket 1: the entries must come in index order.
    m = Msbt({"Ca": ["x"], "Ac": ["y"], "B": ["z"]}, buckets=2)
    data = msbt.write(m)
    lbl = data[0x30:]
    assert lbl.index(b"\x02Ca") < lbl.index(b"\x02Ac")
    assert msbt.read(data) == m


def test_changed_message_moves_later_offsets_and_keeps_others():
    m = msbt.read(_hand_built())
    m.messages["Ac"] = ["A longer line", Tag(0, 4), "next page"]
    back = msbt.read(msbt.write(m))
    assert back.messages["Ac"] == ["A longer line", Tag(0, 4), "next page"]
    assert back.messages["Ca"] == [Tag(0, 3, b"\x01\x00"), "é", TagEnd(0, 3)]
    assert back.messages["B"] == [Tag(2, 23)]


def test_added_label_lands_in_its_bucket_and_reads_back():
    m = msbt.read(_hand_built())
    m.messages["Clawshot_Hint_01"] = ["They say the Hookshot is in a chest."]
    back = msbt.read(msbt.write(m))
    assert list(back.messages) == ["Ac", "Ca", "B", "Clawshot_Hint_01"]
    assert back.messages["Clawshot_Hint_01"] == ["They say the Hookshot is in a chest."]


def test_file_size_and_alignment():
    m = Msbt({"A": ["odd length"]}, buckets=1)
    data = msbt.write(m)
    assert len(data) % 16 == 0
    assert struct.unpack_from("<I", data, 0x12)[0] == len(data)


def test_empty_message_and_empty_file():
    m = Msbt({"A": []}, buckets=1)
    assert msbt.read(msbt.write(m)) == m
    empty = Msbt({}, buckets=1)
    assert msbt.read(msbt.write(empty)) == empty


@pytest.mark.parametrize("text", ["a\0b", "a\x0eb", "a\x0fb"])
def test_refuses_reserved_bytes_in_text(text):
    with pytest.raises(MsbtError, match="reserved byte"):
        msbt.write(Msbt({"A": [text]}, buckets=1))


def test_refuses_utf16_file():
    data = bytearray(_hand_built())
    data[0x0C] = 1
    with pytest.raises(MsbtError, match="UTF-8"):
        msbt.read(bytes(data))


def test_refuses_label_in_wrong_bucket():
    data = _hand_built()
    swapped = data.replace(b"\x01B", b"\x01Y")  # Y hashes to bucket 1
    assert msbt.label_hash("Y") % 2 != 0
    with pytest.raises(MsbtError, match="bucket"):
        msbt.read(swapped)


def test_refuses_unknown_section():
    data = bytearray(_hand_built())
    data[0x20:0x24] = b"ATR1"
    with pytest.raises(MsbtError, match="expected sections"):
        msbt.read(bytes(data))


def test_refuses_truncated_tag():
    m = Msbt({"A": [Tag(1, 1, b"\x01\x02\x03")]}, buckets=1)
    data = bytearray(msbt.write(m))
    at = data.index(b"\x0e\x01\x00\x01\x00\x03\x00")
    data[at + 5] = 9  # parameter size past the message's end
    with pytest.raises(MsbtError, match="runs past"):
        msbt.read(bytes(data))
