import struct
import zlib

import pytest

from clawshot.formats import rstb
from clawshot.formats.rstb import ResourceSizeTable, RstbError

PLACEMENT = "Banc/Area/Area_Static.bcett.byml"
COLLIDING = "Actor/Some_Actor.engine__actor__ActorParam.bgyml"


def crc(path):
    return zlib.crc32(path.encode())


def sample():
    return ResourceSizeTable(
        hashes={0xFFFFFFF0: 7, crc(PLACEMENT): 1000, 0x10: 5, crc(COLLIDING): 99},
        names={COLLIDING: 4242, "A/first.bntx": 1},
    )


def test_write_sorts_entries_and_reads_back():
    data = rstb.write(sample())
    magic, version, name_size, n_hash, n_name = struct.unpack_from("<6sIIII", data)
    assert (magic, version, name_size, n_hash, n_name) == (b"RESTBL", 1, 160, 4, 2)
    assert len(data) == 22 + 4 * 8 + 2 * 164
    crcs = [struct.unpack_from("<I", data, 22 + 8 * i)[0] for i in range(4)]
    assert crcs == sorted(crcs)
    first_name = data[22 + 32 : 22 + 32 + 160].rstrip(b"\0")
    assert first_name == b"A/first.bntx"  # "A" sorts before "Actor"
    back = rstb.read(data)
    assert (back.hashes, back.names) == (sample().hashes, sample().names)
    assert rstb.write(back) == data


def test_lookup_uses_the_name_entry_first_then_crc32_without_zs():
    table = sample()
    assert table.get(PLACEMENT + ".zs") == 1000
    assert table.get(PLACEMENT) == 1000
    assert table.get(COLLIDING) == 4242  # not the hash entry of the same CRC32
    assert table.get("Banc/Area/Other.bcett.byml.zs") is None


def test_set_updates_a_name_entry_or_adds_a_hash_entry():
    table = sample()
    table.set(COLLIDING, 5000)
    assert (table.names[COLLIDING], table.hashes[crc(COLLIDING)]) == (5000, 99)
    table.set("Banc/New/New_Static.bcett.byml.zs", 1234)
    assert table.hashes[crc("Banc/New/New_Static.bcett.byml")] == 1234
    with pytest.raises(RstbError, match="32 bits"):
        table.set(PLACEMENT, 1 << 32)


@pytest.mark.parametrize(
    ("path", "size", "entry"),
    [
        ("Banc/A/A_Static.bcett.byml.zs", 510_880, 510_880 + 264),
        ("Banc/A/A_Static.bcett.byml", 510_881, 510_912 + 264),
        ("Event/EventFlow/Flow.bfevfl.zs", 20_160, 20_160 + 272),
        ("Mals/USen.Product.110.sarc.zs", 1, 32 + 312),
        ("Pack/Actor/Obj_X.pack.zs", 0, 312),
    ],
)
def test_required_size(path, size, entry):
    assert rstb.required_size(path, size) == entry


def test_required_size_refuses_an_unchecked_type():
    with pytest.raises(RstbError, match="no size formula"):
        rstb.required_size("Logic/X.logic.module.ainb", 100)


def _header(magic=b"RESTBL", version=1, name_size=160, n_hash=0, n_name=0):
    return struct.pack("<6sIIII", magic, version, name_size, n_hash, n_name)


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (b"RESTBL", "too short"),
        (_header(magic=b"RSTB\0\0"), "magic"),
        (_header(version=2), "version 2"),
        (_header(n_hash=1), "not 22"),
        (_header(n_hash=2) + struct.pack("<IIII", 5, 1, 5, 2), "appears twice"),
        (_header(name_size=4, n_name=2) + b"ab\0\0" + b"\1\0\0\0" + b"ab\0\0" + b"\2\0\0\0", "appears twice"),
    ],
)
def test_malformed_tables_are_rejected(data, message):
    with pytest.raises(RstbError, match=message):
        rstb.read(data)


def test_a_name_too_long_for_its_field_is_rejected():
    table = ResourceSizeTable(names={"x" * 160: 1})
    with pytest.raises(RstbError, match="does not fit"):
        rstb.write(table)
