"""Price-only field diffs and full affordable seed, without running the game."""

import pytest

from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.generate import Settings
from clawshot.patch import make_seed, shops, write_seed

pytestmark = pytest.mark.dump


def test_unshuffled_kokiri_shield_changes_only_exact_price_fields(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    selected = tuple(
        slot for slot in shops.load() if slot.shop == "KF Shop" and slot.vanilla_item == "Shop_Weapon_Shield_Deku"
    )
    transforms = shops.patch_step(romfs, ())({})
    assert set(transforms) == {slot.pack for slot in selected}
    for path, transform in transforms.items():
        original = dictionaries.decompress(path, (romfs / path).read_bytes())
        expected = sarc.read(original)
        for slot in selected:
            if slot.pack == path:
                tree = byml.read(expected[slot.member])
                tree["GoodsList"][slot.index]["PriceOffset"] = byml.I32(-30)  # base 40, exact price 10
                expected[slot.member] = byml.write(tree)
        actual = sarc.read(transform(original))
        assert actual.keys() == expected.keys()
        for member, data in expected.items():
            if member in {slot.member for slot in selected if slot.pack == path}:
                assert byml.same(byml.read(actual[member]), byml.read(data)), (path, member)
            else:
                assert actual[member] == data, (path, member)
    assert shops.patch_step(romfs, (), cheap_deku_shield=False)({}) == {}


def test_affordable_full_seed_has_exact_prices_and_original_release_stock(romfs, tmp_path):
    settings = Settings(shuffle=("Chest", "Shop"), shop_prices="affordable")
    output = make_seed(romfs, 7, settings)
    out = tmp_path / "affordable"
    written = write_seed(output, romfs, out)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    palette = shops.native_items()
    cache = {}

    def pack(path, overlay):
        key = path, overlay
        if key not in cache:
            target = out / "romfs" / path if overlay else romfs / path
            if not target.exists():
                target = romfs / path
            cache[key] = sarc.read(dictionaries.decompress(path, target.read_bytes()))
        return cache[key]

    count = 0
    for slot in shops.load():
        if slot.location not in output.seed.shuffled:
            continue
        target = palette[output.seed.placements[slot.location]]
        goods = shops.resolve_member(pack(slot.pack, True), slot.member)["GoodsList"][slot.index]
        original = shops.resolve_member(pack(slot.pack, False), slot.member)["GoodsList"][slot.index]
        assert shops.actor_name(goods["Actor"]) == target["display"]
        assert int(goods.get("PriceOffset", 0)) + target["price"] == 10, (slot, goods, target)
        assert not goods.get("ConditionalPriceOffsetList"), (slot, goods)
        assert goods.get("StockNum") == original.get("StockNum")
        assert goods.get("Release") == original.get("Release")
        count += 1
    assert count == 120  # all ordinary physical copies, masks excluded
    table_file = out / "romfs" / rstb.TABLE_PATH
    table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, table_file.read_bytes()))
    for info in written:
        if info.path != rstb.TABLE_PATH and info.path not in {file.path for file in output.fast_start_files}:
            assert table.get(info.path) >= rstb.required_size(info.path, info.new_size), info
