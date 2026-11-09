"""Partial shelves and scrub fees preserve native non-price purchase gates."""

import copy
from collections import Counter

import pytest
from test_scrubs import fixture as scrub_chart

from clawshot.__main__ import main
from clawshot.formats import evfl
from clawshot.generate import Settings, generate, prepare
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import scrubs, shops
from clawshot.world.load import load_spec


@pytest.mark.parametrize("count", range(9))
def test_each_shop_selects_exactly_n_logical_shelves_and_retains_fixed_inventory(count):
    spec = load_spec()
    before = copy.deepcopy(spec)
    _, vanilla_world = prepare(spec, Settings())
    settings, world = prepare(spec, Settings(shuffle=("Shop",), shop_slots=count))
    selected = set(shuffled_locations(world, settings))
    copies = shops.load()
    expected = {
        slot.location
        for slot in copies
        if slot.shop != "Market Mask Shop"
        and slot.index < count
        and world.locations.get(slot.location) is not None
        and world.locations[slot.location].type == "Shop"
    }
    assert selected == expected
    counts = Counter(
        {
            shop: len({slot.location for slot in copies if slot.shop == shop and slot.location in selected})
            for shop in {slot.shop for slot in copies if slot.location in selected}
        }
    )
    assert all(n == count for n in counts.values())
    assert len(selected) == 8 * count
    for name, location in world.locations.items():
        if location.type == "Shop" and name not in selected:
            assert location.vanilla == vanilla_world.locations[name].vanilla
    assert spec == before


def test_partial_prices_do_not_discount_unshuffled_tunic_or_open_release_gates():
    settings, world = prepare(load_spec(), Settings(shuffle=("Shop",), shop_slots=3, shop_prices="affordable"))
    assert not world.locations["GC Shop Item 4"].rule({}, "adult", 1)  # unselected 600-rupee tunic
    assert not world.locations["GC Shop Item 4"].rule({"Progressive Wallet": 1}, "adult", 1)
    assert world.locations["GC Shop Item 4"].rule({"Progressive Wallet": 2}, "adult", 1)
    assert not world.locations["KF Shop Item 1"].rule({}, "child", 1)
    assert world.locations["KF Shop Item 1"].rule({"Showed Mido Sword & Shield": 1}, "child", 1)
    assert not world.locations["Market Bombchu Shop Item 1"].rule({}, "child", 1)
    assert settings.shop_slots == 3


@pytest.mark.parametrize("count", [0, 1, 4, 8])
def test_partial_fill_pool_contains_only_selected_stock_and_replays(count):
    names = [f"Synthetic Shop Item {i + 1}" for i in range(8)]
    spec = {
        "start": "Shop",
        "goal": "True",
        "settings": {"native_shop_items": [f"Native{i}" for i in range(8)]},
        "items": {f"Native{i}": {"class": "normal"} for i in range(8)},
        "regions": [{"name": "Shop", "locations": {name: "True" for name in names}}],
        "locations": {name: {"type": "Shop", "vanilla": f"Native{i}"} for i, name in enumerate(names)},
        "shop_price_rules": {name: {"index": i} for i, name in enumerate(names)},
    }
    # Price metadata is separate from this synthetic selection/pool-only fixture.
    for entry in spec["shop_price_rules"].values():
        entry.update(
            shop="Synthetic",
            actor="Shop_Native",
            price=10,
            base_rule="True",
            wallet=[{"capacity": 200, "rule": "True"}],
        )
    settings = Settings(shuffle=("Shop",), shop_slots=count)
    seed = generate(spec, 7, settings, attempts=1)
    assert seed.shuffled == names[:count]
    assert Counter(seed.placements[name] for name in seed.shuffled) == Counter(f"Native{i}" for i in range(count))
    assert {name: seed.placements[name] for name in names[count:]} == {
        name: f"Native{i}" for i, name in enumerate(names) if i >= count
    }
    replay = generate(spec, 7, Settings.from_string(seed.settings.to_string()), attempts=1)
    assert replay.placements == seed.placements


@pytest.mark.parametrize(
    "price,wallets,expected",
    [(0, 0, True), (200, 0, True), (201, 0, False), (500, 1, True), (501, 1, False), (1000, 2, True)],
)
def test_scrub_wallet_boundary_matches_native_wallets_without_removing_stun_gate(price, wallets, expected):
    spec = load_spec()
    before = copy.deepcopy(spec)
    prepared, settings, _ = scrubs.seed_setup(
        spec, Settings(shuffle=("Scrub",), scrub_prices="fixed", scrub_price=price)
    )
    _, world = prepare(prepared, settings)
    rule = world.locations["LW Deku Scrub Near Bridge"].rule
    assert rule({"Deku Shield": 1, "Progressive Wallet": wallets}, "child", 1) is expected
    assert not rule({"Progressive Wallet": 2}, "child", 1)
    assert not rule({"Deku Shield": 1, "Progressive Wallet": 2}, "adult", 1)
    assert world.settings["scrub_sale_prices"]["LW Deku Scrub Near Bridge"] == price
    assert spec == before


@pytest.mark.parametrize("price", [0, 10, 1000])
def test_every_scrub_tier_changes_price_without_touching_payment_or_once_control_flow(price):
    before = scrub_chart()
    raw = evfl.write(evfl.EventFlowFile(scrubs.FLOW, flowchart=before))
    placements = {name: "Item_Boomerang" for name in scrubs.SALES}
    after = evfl.read(
        scrubs.changes(placements, prices={name: price for name in placements})[scrubs.PATH](raw)
    ).flowchart
    events = {event.name: event for event in after.events}
    for name, sale in scrubs.SALES.items():
        for event, old_actor in sale.grants:
            assert events[event].params["ActorName"] == placements[name]
            assert events[event].params["Price"] == price
            events[event].params.update(ActorName=old_actor, Price=sale.price)
        if sale.selection:
            events[sale.selection].params["Value"] = "Obj_Heart_Piece"
    assert after == before


def test_cli_override_and_settings_replay_cover_all_three_fields(capsys):
    start = Settings(shop_slots=1, scrub_prices="fixed", scrub_price=500)
    assert Settings.from_string(start.to_string()) == start
    assert main(["--settings", start.to_string(), "--shop-slots", "0", "--scrub-price", "0", "--print-settings"]) == 0
    chosen = Settings.from_string(capsys.readouterr().out.strip())
    assert (chosen.shop_slots, chosen.scrub_prices, chosen.scrub_price) == (0, "fixed", 0)


@pytest.mark.parametrize(
    "fields",
    [
        {"shop_slots": -1},
        {"shop_slots": 9},
        {"shop_slots": True},
        {"shop_slots": 1.5},
        {"scrub_prices": "random"},
        {"scrub_price": -1},
        {"scrub_price": 1001},
        {"scrub_price": True},
        {"scrub_price": "10"},
    ],
)
def test_invalid_purchase_settings_are_refused(fields):
    with pytest.raises(ValueError):
        Settings(**fields)
