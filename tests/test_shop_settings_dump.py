"""Partial shelf selection and exact scrub fees agree with written native resources."""

import copy

import pytest

from clawshot.formats import byml, evfl, sarc, zsdic
from clawshot.generate import Settings
from clawshot.patch import make_seed, scrubs, shops, write_seed
from clawshot.patch.items import load as load_actors
from clawshot.settings import shop_price
from clawshot.world.search import Search


@pytest.mark.dump
def test_partial_shelves_and_fixed_scrub_fees_preserve_unselected_stock_and_native_gates(romfs, tmp_path):
    settings = Settings(
        shuffle=("Chest", "Shop", "Scrub"),
        shop_slots=3,
        shop_prices="affordable",
        scrub_prices="fixed",
        scrub_price=201,
    )
    output = make_seed(romfs, 7, settings)
    write_seed(output, romfs, tmp_path / "partial-next")
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    palette = shops.native_items()
    actors = load_actors()
    packs, original_packs, trees = {}, {}, {}

    def raw(path, changed=True):
        written = tmp_path / "partial-next" / "romfs" / path
        source = written if changed and written.is_file() else romfs / path
        return dictionaries.decompress(path, source.read_bytes())

    selected = {name for name in output.seed.shuffled if output.seed.world.locations[name].type == "Shop"}
    assert len(selected) == 24
    for slot in shops.load():
        if slot.pack not in packs:
            packs[slot.pack] = sarc.read(raw(slot.pack))
            original_packs[slot.pack] = sarc.read(raw(slot.pack, False))
        if slot.file not in trees:
            trees[slot.file] = {int(actor["Hash"]): actor for actor in byml.read(raw(slot.file))["Actors"]}
        before = byml.read(original_packs[slot.pack][slot.member])["GoodsList"][slot.index]
        after = byml.read(packs[slot.pack][slot.member])["GoodsList"][slot.index]
        if slot.location in selected:
            assert slot.index < settings.shop_slots
            display = palette[output.seed.placements[slot.location]]["display"]
            assert trees[slot.file][slot.id]["Gyaml"] == display
            assert shops.actor_name(after["Actor"]) == display
            assert int(after["PriceOffset"]) + palette[output.seed.placements[slot.location]]["price"] == 10
            assert {
                k: v for k, v in before.items() if k not in ("Actor", "PriceOffset", "ConditionalPriceOffsetList")
            } == {k: v for k, v in after.items() if k not in ("Actor", "PriceOffset", "ConditionalPriceOffsetList")}
        else:
            assert trees[slot.file][slot.id]["Gyaml"] == slot.vanilla_item
            expected = copy.deepcopy(before)
            price = shop_price(slot.shop, slot.vanilla_item, slot.price)
            if price != slot.price:  # Existing independent cheap-shield setting, not partial shuffle.
                expected["PriceOffset"] = byml.I32(int(before.get("PriceOffset", 0)) + price - slot.price)
                if "ConditionalPriceOffsetList" in expected:
                    expected["ConditionalPriceOffsetList"] = []
            assert byml.same(after, expected), (slot.location, before, after)

    before, after = evfl.read(raw(scrubs.PATH, False)), evfl.read(raw(scrubs.PATH))
    events = {event.name: event for event in after.flowchart.events}
    for name, sale in scrubs.SALES.items():
        item = actors.actor(output.seed.placements[name])
        for event, old in sale.grants:
            assert events[event].params["ActorName"] == item
            assert events[event].params["Price"] == settings.scrub_price
            events[event].params.update(ActorName=old, Price=sale.price)
        if sale.selection:
            assert events[sale.selection].params["Value"] == item
            events[sale.selection].params["Value"] = "Obj_Heart_Piece"
        rule = output.seed.world.locations[name].rule
        counts = {read: 10 for read in rule.reads}
        counts["Progressive Wallet"] = 0
        assert not rule(counts, "child", 1)
        counts["Progressive Wallet"] = 1
        assert rule(counts, "child", 1)
    assert after == before  # Includes every repeat vendor, payment, cancellation and saved gate.
    oracle = Search(output.seed.world)
    oracle.collect_spheres(output.seed.placements)
    assert oracle.won()
