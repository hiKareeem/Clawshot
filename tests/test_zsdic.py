import random

import pytest
import zstandard as zstd

from clawshot.formats import sarc, zsdic

# The game's dictionary IDs, as recorded in each .zs frame header.
DICTIONARY_IDS = {"zs.zsdic": 1, "bkprb.zsdic": 2, "bcett.byml.zsdic": 3, "pack.zsdic": 4}


def _samples(seed: int) -> list[bytes]:
    rng = random.Random(seed)
    words = [b"Actors", b"Gyaml", b"Hash", b"Translate", b"Rotate", b"Dynamic", b"Phive", b"Placement"]
    return [b"".join(rng.choice(words) + bytes([rng.randrange(256)]) for _ in range(40)) for _ in range(400)]


@pytest.fixture(scope="module")
def pack() -> bytes:
    """A synthetic ZsDic.pack.zs: plain zstd around a SARC of four trained dictionaries."""
    files = {
        name: zstd.train_dictionary(4096, _samples(dict_id), dict_id=dict_id).as_bytes()
        for name, dict_id in DICTIONARY_IDS.items()
    }
    return zstd.ZstdCompressor().compress(sarc.write(files))


@pytest.mark.parametrize(
    ("name", "dictionary"),
    [
        ("Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs", "bcett.byml.zsdic"),
        ("Pack/Actor/Foo.pack.zs", "pack.zsdic"),
        ("Phive/Foo.bkprb.zs", "bkprb.zsdic"),
        ("Event/EventFlow/Foo.bfevfl.zs", "zs.zsdic"),
        ("Model/Foo.bkprmb.zs", "zs.zsdic"),
        ("RSDB\\Tag.Product.111.rstbl.byml.zs", "zs.zsdic"),
        ("Pack/ZsDic.pack.zs", None),
    ],
)
def test_dictionary_for(name, dictionary):
    assert zsdic.dictionary_for(name) == dictionary


def test_dictionary_for_rejects_uncompressed_names():
    with pytest.raises(zsdic.ZsError):
        zsdic.dictionary_for("Banc/Foo.bcett.byml")


def test_round_trip_with_each_dictionary(pack):
    dicts = zsdic.Dictionaries.from_pack(pack)
    payload = b"".join(_samples(99)[:20])
    for name, dict_id in [
        ("Banc/A/A_Child_Static.bcett.byml.zs", 3),
        ("Pack/Actor/B.pack.zs", 4),
        ("Phive/C.bkprb.zs", 2),
        ("Event/EventFlow/D.bfevfl.zs", 1),
    ]:
        packed = dicts.compress(name, payload)
        assert zsdic.frame_dictionary_id(packed) == dict_id
        params = zstd.get_frame_parameters(packed)
        assert params.content_size == len(payload)
        assert not params.has_checksum
        assert dicts.decompress(name, packed) == payload


def test_plain_pack_round_trip(pack):
    dicts = zsdic.Dictionaries.from_pack(pack)
    packed = dicts.compress(zsdic.PACK_PATH, b"plain")
    assert zsdic.frame_dictionary_id(packed) == 0
    assert dicts.decompress(zsdic.PACK_PATH, packed) == b"plain"


def test_decompress_refuses_a_mismatched_dictionary(pack):
    dicts = zsdic.Dictionaries.from_pack(pack)
    packed = dicts.compress("A.bcett.byml.zs", b"data" * 50)
    with pytest.raises(zsdic.ZsError, match="dictionary ID 3"):
        dicts.decompress("A.pack.zs", packed)


def test_pack_must_hold_all_four_dictionaries():
    files = {"zs.zsdic": zstd.train_dictionary(4096, _samples(1), dict_id=1).as_bytes()}
    with pytest.raises(zsdic.ZsError, match="lacks"):
        zsdic.Dictionaries.from_pack(zstd.ZstdCompressor().compress(sarc.write(files)))


@pytest.mark.dump
def test_dump_dictionaries(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    assert {name: dicts.dictionary_id(name) for name in zsdic.DICTIONARY_NAMES} == DICTIONARY_IDS


@pytest.mark.dump
def test_dump_every_placement_file_decompresses(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    paths = sorted((romfs / "Banc").rglob("*.bcett.byml.zs"))
    assert len(paths) == 160
    for path in paths:
        data = dicts.decompress(path.name, path.read_bytes())
        assert data[:4] == b"YB\x07\x00", path
