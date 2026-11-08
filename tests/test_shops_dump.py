"""Shop definitions are metadata only; the oracle is the player's read-only dump."""

import pytest

from clawshot.census.scan import scan
from clawshot.formats import byml, sarc, zsdic
from clawshot.patch import shops

pytestmark = pytest.mark.dump


def test_every_shop_shelf_matches_its_seller_and_price(romfs):
    slots = shops.load()
    census = {location.id: location for location in scan(romfs) if location.kind == "shop_slot"}
    assert {slot.id for slot in slots} == set(census)
    for slot in slots:
        assert census[slot.id].files == (slot.file,)
    shops.validate(romfs, slots)
    print(f"Validated {len(slots)} shelves in {len({slot.shop for slot in slots})} shops, including mask loans")


@pytest.mark.parametrize(
    ("sale", "display", "base_price"),
    [("Shop_Weapon_Shield_Hylian", None, 80), ("Item_Boomerang", "Shop_Weapon_Shield_Deku", 0)],
)
def test_kokiri_shield_sale_changes_only_shelf_and_selected_goods(romfs, sale, display, base_price):
    selected = tuple(slot for slot in shops.load() if slot.location == "KF Shop Item 7")
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    displays = {"KF Shop Item 7": display} if display else None
    changes = shops.changes(romfs, {"KF Shop Item 7": sale}, displays=displays)
    for path, transform in changes.items():
        before = dictionaries.decompress(path, (romfs / path).read_bytes())
        after = transform(before)
        if path.startswith("Banc/"):
            expected = byml.read(before)
            for actor in expected["Actors"]:
                if int(actor["Hash"]) in {slot.id for slot in selected if slot.file == path}:
                    actor["Gyaml"] = display or sale
            assert byml.same(byml.read(after), expected)
        else:
            expected, actual = sarc.read(before), sarc.read(after)
            for slot in selected:
                if slot.pack != path:
                    continue
                member = byml.read(expected[slot.member])
                goods = member["GoodsList"][slot.index]
                goods["Actor"] = shops.actor_path(sale)
                goods["PriceOffset"] = byml.I32(slot.price - base_price)
                assert byml.same(byml.read(actual[slot.member]), member)
                del actual[slot.member], expected[slot.member]
            assert actual == expected
        assert transform(before) == after
    if display:
        assert all(path.startswith("Pack/") for path in changes)
