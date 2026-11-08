"""Packed ShopParams retain parsed overhead, including across shared resource paths."""

from functools import partial

import pytest

from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.patch import shops
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import write

MEMBER = "Component/ShopParam/Test.game__component__ShopParam.bgyml"


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("already_roomy", [False, True])
def test_nested_only_growth_uses_largest_copy_not_sum(tmp_path, zsdic_pack, reverse, already_roomy):
    romfs = tmp_path / "dump"
    (romfs / "Pack/Actor").mkdir(parents=True)
    (romfs / zsdic.PACK_PATH).write_bytes(zsdic_pack)
    dictionaries = zsdic.Dictionaries.from_pack(zsdic_pack)
    original = byml.write({"GoodsList": [{"Actor": shops.actor_path("Shop_Old"), "StockNum": byml.I32(-1)}]})
    pack = sarc.write({MEMBER: original})
    table = rstb.ResourceSizeTable()
    initial = len(original) + (4096 if already_roomy else 256)
    table.set(MEMBER, initial)
    table.set("Untouched", 1234)
    changes, deltas = {}, []
    for name, length in zip(("A", "B"), (300, 100) if reverse else (100, 300), strict=True):
        path = f"Pack/Actor/{name}.pack.zs"
        (romfs / path).write_bytes(dictionaries.compress(path, pack))
        table.set(path, 1 << 20)  # No outer entry needs raising.
        slot = shops.Slot(1, "Test", "Test Item", "Banc/Test", name, 2, MEMBER, 0, "Shop_Old", 10)
        sale = shops.Sale("Shop_" + "x" * length, "Shop_New", 20)
        changes[path] = partial(shops.patch_goods, changes=((slot, sale),))
        result = sarc.read(changes[path](pack))[MEMBER]
        deltas.append(((len(result) + 31) // 32 - (len(original) + 31) // 32) * 32)
    (romfs / rstb.TABLE_PATH).parent.mkdir(parents=True)
    (romfs / rstb.TABLE_PATH).write_bytes(dictionaries.compress(rstb.TABLE_PATH, rstb.write(table)))
    out = tmp_path / "overlay"
    written = write(Plan([], [], []), romfs, out, extra_changes=(changes,))
    output = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (out / "romfs" / rstb.TABLE_PATH).read_bytes()))
    table.set(MEMBER, initial + max(deltas))
    assert output == table
    assert all(info.entry == info.new_entry for info in written if info.path != rstb.TABLE_PATH)
    assert rstb.TABLE_PATH in {info.path for info in written}


def test_parsed_structure_growth_is_not_mistaken_for_only_raw_growth():
    before = sarc.write({MEMBER: byml.write({"GoodsList": [{"Actor": shops.actor_path("Shop_Old")}]})})
    after = sarc.write({MEMBER: byml.write({"GoodsList": [{"Actor": shops.actor_path("Shop_New")}] * 2})})
    with pytest.raises(PatchError):
        shops.member_growth(before, after)
