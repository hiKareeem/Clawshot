"""Shop definitions are metadata only; the oracle is the player's read-only dump."""

import pytest

from clawshot.census.scan import scan
from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.generate import Settings
from clawshot.patch import make_seed, shops, write_seed

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


def test_seed_shop_copies_share_the_placement_and_keep_slot_prices(romfs, tmp_path):
    settings = Settings(
        shuffle=("Chest", "Shop"),
        areas=("KokiriForest", "LostWood", "InsideTheDekuTree"),
        goal="'Defeat Queen Gohma'",
    )
    output = make_seed(romfs, 22, settings)
    out = tmp_path / "shop-seed"
    written = write_seed(output, romfs, out)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    palette = shops.native_items()

    def resource(path):
        overlay = out / "romfs" / path
        return dictionaries.decompress(path, (overlay if overlay.exists() else romfs / path).read_bytes())

    for slot in shops.load():
        if slot.location not in output.seed.shuffled:
            continue
        target = palette[output.seed.placements[slot.location]]
        tree = byml.read(resource(slot.file))
        actor = next(actor for actor in tree["Actors"] if int(actor["Hash"]) == slot.id)
        assert actor["Gyaml"] == target["display"]
        pack = sarc.read(resource(slot.pack))
        goods = shops.resolve_member(pack, slot.member)["GoodsList"][slot.index]
        assert shops.actor_name(goods["Actor"]) == target["display"]
        assert int(goods.get("PriceOffset", 0)) + target["price"] == slot.price
        original = sarc.read(dictionaries.decompress(slot.pack, (romfs / slot.pack).read_bytes()))
        original_goods = shops.resolve_member(original, slot.member)["GoodsList"][slot.index]
        assert goods.get("StockNum") == original_goods.get("StockNum")
        assert goods.get("Release") == original_goods.get("Release")
    table = rstb.read(resource(rstb.TABLE_PATH))
    for info in written:
        if info.path != rstb.TABLE_PATH:
            assert table.get(info.path) >= rstb.required_size(info.path, info.new_size)
