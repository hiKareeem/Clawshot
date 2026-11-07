import struct

import pytest

from clawshot.formats import sarc


def test_round_trip_keeps_names_and_data():
    files = {"a.bin": b"", "dir/b.txt": b"hello", "zs.zsdic": bytes(range(256)) * 3, "é.dat": b"\x01"}
    data = sarc.write(files, alignment=0x10)
    back = sarc.read(data)
    assert back == files
    # file table is sorted by name hash, as the game looks names up by binary search
    assert list(back) == sorted(files, key=sarc.name_hash)


def test_file_data_is_aligned():
    data = sarc.write({"one": b"x", "two": b"yy", "three": b"zzz"}, alignment=0x80)
    data_offset = struct.unpack_from("<I", data, 0x0C)[0]
    assert data_offset % 0x80 == 0
    count = struct.unpack_from("<H", data, 0x14 + 6)[0]
    starts = [struct.unpack_from("<I", data, 0x14 + 12 + 16 * i + 8)[0] for i in range(count)]
    assert all(s % 0x80 == 0 for s in starts)


def test_name_hash_uses_signed_chars():
    # 'é' is two bytes >= 0x80; the game hashes them as negative chars
    expected = 0
    for c in (0xC3 - 0x100, 0xA9 - 0x100):
        expected = (expected * 0x65 + c) & 0xFFFFFFFF
    assert sarc.name_hash("é") == expected
    assert sarc.name_hash("ab") == (ord("a") * 0x65 + ord("b"))


def test_rejects_other_formats():
    with pytest.raises(sarc.SarcError):
        sarc.read(b"Yaz0" + bytes(0x20))
