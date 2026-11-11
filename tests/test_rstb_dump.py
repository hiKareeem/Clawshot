import pytest

from clawshot.formats import rstb, zsdic


@pytest.fixture(scope="module")
def table_bytes(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    return dicts, dicts.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes())


@pytest.mark.dump
def test_dump_size_table_round_trips(table_bytes):
    _, data = table_bytes
    table = rstb.read(data)
    print(f"{len(table.hashes)} hash entries, {len(table.names)} name entries")
    assert rstb.write(table) == data


@pytest.mark.dump
@pytest.mark.parametrize(
    "pattern",
    [
        "Banc/*/*.bcett.byml.zs",
        "Event/EventFlow/*.bfevfl.zs",
        "Mals/*.sarc.zs",
        "Pack/Actor/*.pack.zs",
        "GameData/GameDataList.Product.110.byml.zs",
        "RSDB/ActorInfo.Product.111.rstbl.byml.zs",
        "RSDB/EventSetting.Product.111.rstbl.byml.zs",
    ],
)
def test_dump_size_formula_fits_every_file(romfs, table_bytes, pattern):
    dicts, data = table_bytes
    table = rstb.read(data)
    paths = sorted(p.relative_to(romfs).as_posix() for p in romfs.glob(pattern))
    assert paths
    misfits = []
    for path in paths:
        size = len(dicts.decompress(path, (romfs / path).read_bytes()))
        entry, needed = table.get(path), rstb.required_size(path, size)
        if entry != needed:
            misfits.append((path, size, entry, needed))
    print(f"{pattern}: {len(paths) - len(misfits)} of {len(paths)} fit")
    assert misfits == []
