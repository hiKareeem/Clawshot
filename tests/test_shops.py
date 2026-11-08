import copy

import pytest

from clawshot.formats import byml, sarc
from clawshot.patch import shops
from clawshot.patch.plan import PatchError


@pytest.fixture
def slot():
    return shops.Slot(
        101,
        "Test Shop",
        "Test Shop Item 1",
        "Banc/Test/Test_Static.bcett.byml.zs",
        "Npc_Test",
        201,
        "Component/Shop.bgyml",
        0,
        "Shop_Old",
        40,
    )


def test_sale_changes_price_offset_but_not_release_stock_or_other_goods(slot):
    original = {
        "GoodsList": [
            {
                "Actor": shops.actor_path("Shop_Old"),
                "StockNum": byml.I32(1),
                "Release": {"ReleaseGameData": "StoryGate"},
                "PriceOffset": byml.I32(5),
            },
            {"Actor": shops.actor_path("Shop_Second"), "StockNum": byml.I32(-1)},
        ],
        "Unrelated": byml.U64(123),
    }
    pack = sarc.write({slot.member: byml.write(original), "untouched.bin": b"unrelated"})
    sale = shops.Sale("Shop_New", "Shop_New", 80)
    output = sarc.read(shops.patch_goods(pack, ((slot, sale),)))
    expected = copy.deepcopy(original)
    expected["GoodsList"][0]["Actor"] = shops.actor_path("Shop_New")
    expected["GoodsList"][0]["PriceOffset"] = byml.I32(-40)
    assert byml.same(byml.read(output[slot.member]), expected)
    assert output["untouched.bin"] == b"unrelated"


def test_stand_in_display_does_not_replace_the_sale_actor(slot):
    original = {"GoodsList": [{"Actor": shops.actor_path("Shop_Old"), "StockNum": byml.I32(-1)}]}
    sale = shops.Sale("Item_New", "Shop_Old", 0)
    pack = sarc.write({slot.member: byml.write(original)})
    patched = sarc.read(shops.patch_goods(pack, ((slot, sale),)))
    assert byml.read(patched[slot.member])["GoodsList"][0]["Actor"] == shops.actor_path("Item_New")
    tree = {"Actors": [{"Hash": byml.U64(101), "Gyaml": "Shop_Old", "Dynamic": {"ShopItemIndex": byml.I32(0)}}]}
    assert byml.same(byml.read(shops.patch_shelves(byml.write(tree), ((slot, sale),))), tree)


def test_shelf_swap_keeps_identity_and_removes_only_obsolete_quantity_boards(slot):
    tree = {
        "Actors": [
            {
                "Hash": byml.U64(101),
                "Gyaml": "Shop_Old",
                "Links": [{"Dst": byml.U64(102)}, {"Dst": byml.U64(103)}],
                "Dynamic": {"ShopItemIndex": byml.I32(0)},
            },
            {"Hash": byml.U64(102), "Gyaml": "Shop_Board_Bundle_05"},
            {"Hash": byml.U64(103), "Gyaml": "Shop_Board_SoldOut"},
            {"Hash": byml.U64(999), "Gyaml": "Unrelated"},
        ],
        "FarDeleteGroups": [[byml.U64(101), byml.U64(102), byml.U64(103)]],
        "SimultaneousGroups": [[byml.U64(102), byml.U64(999)]],
    }
    output = byml.read(shops.patch_shelves(byml.write(tree), ((slot, shops.Sale("Shop_New", "Shop_New", 80)),)))
    expected = copy.deepcopy(tree)
    expected["Actors"][0]["Gyaml"] = "Shop_New"
    expected["Actors"][0]["Links"] = [{"Dst": byml.U64(103)}]
    del expected["Actors"][1]
    expected["FarDeleteGroups"] = [[byml.U64(101), byml.U64(103)]]
    expected["SimultaneousGroups"] = [[byml.U64(999)]]
    assert byml.same(output, expected)


def test_stale_shelf_and_sale_fail_instead_of_patching_another_item(slot):
    with pytest.raises(PatchError, match="no longer holds"):
        shops.patch_shelves(
            byml.write({"Actors": [{"Hash": byml.U64(101), "Gyaml": "Shop_Other"}]}),
            ((slot, shops.Sale("Shop_New", "Shop_New", 80)),),
        )
    pack = sarc.write({slot.member: byml.write({"GoodsList": [{"Actor": shops.actor_path("Shop_Other")}]})})
    with pytest.raises(PatchError, match="no longer holds"):
        shops.patch_goods(pack, ((slot, shops.Sale("Shop_New", "Shop_New", 80)),))
