import copy
import random
from collections import Counter

import pytest

from clawshot.generate import Settings, generate, prepare
from clawshot.generate.fill import allowed, fill, shuffled_locations
from clawshot.world import build_world
from clawshot.world.load import load_spec
from clawshot.world.search import Search


@pytest.fixture
def spec():
    return load_spec()


def test_actual_shields_unlock_their_child_and_adult_rules(spec):
    world = build_world(spec)
    assert Search(world, ["Kokiri Sword", "Deku Shield"]).can_reach("KF Outside Deku Tree", "child")
    location = world.locations["Deku Tree Slingshot Chest"]
    assert not Search(world, ["Kokiri Sword"]).can_access(location)
    assert world.items["Deku Shield"].progression
    # An adult shield helper must also read actual inventory, not only shop access.
    rule_spec = {**spec, "start": "Root", "goal": "Hylian_Shield"}
    assert Search(build_world(rule_spec), ["Hylian Shield"]).won()


def test_vanilla_shield_is_bought_and_shop_shuffle_puts_actual_shield_in_pool(spec):
    world = build_world(spec)
    assert "KF Shop Item 7" not in shuffled_locations(world, Settings())
    assert world.locations["KF Shop Item 7"].vanilla == "Deku Shield"
    assert "KF Shop Item 7" in shuffled_locations(world, Settings(shuffle=("Shop",)))
    search = Search(world, ["Kokiri Sword"])
    assert not search.can_reach("KF Outside Deku Tree", "child")
    search.collect_spheres({"KF Shop Item 7": "Deku Shield"})
    assert search.can_reach("KF Outside Deku Tree", "child")


def test_shuffled_shield_cannot_self_lock_behind_mido_but_skip_allows_it(spec):
    placements = {"Deku Tree Map Chest": "Deku Shield"}
    world = build_world(spec)
    blocked = Search(world, ["Kokiri Sword"])
    blocked.collect_spheres(placements)
    assert "Deku Tree Map Chest" not in blocked.collected
    skipped = copy.deepcopy(spec)
    forest = next(region for region in skipped["regions"] if region["name"] == "Kokiri Forest")
    forest["exits"]["KF Outside Deku Tree"] = "True"  # Mido skip only, not the separate forest exit.
    search = Search(build_world(skipped), ["Kokiri Sword"])
    search.collect_spheres(placements)
    assert "Deku Tree Map Chest" in search.collected
    assert not search.can_reach("LW Bridge From Forest", "child")


@pytest.mark.parametrize(
    ("name", "wallets", "expected"),
    [
        ("ZD Shop Item 8", 0, True),  # 70 fits 200.
        ("Market Bombchu Shop Item 7", 0, False),  # 240 needs the 500 wallet.
        ("Market Bombchu Shop Item 7", 1, True),
        ("GC Shop Item 4", 1, False),  # 600 needs the 1000 wallet.
        ("GC Shop Item 4", 2, True),
    ],
)
def test_prices_require_remake_wallet_capacity(spec, name, wallets, expected):
    world = build_world(spec)
    counts = {"Progressive Wallet": wallets, "Defeat King Dodongo": 1}
    assert world.locations[name].rule(counts, "adult", 1) is expected


def test_kokiri_short_stock_and_bombchu_release_gates(spec):
    world = build_world(spec)
    assert world.locations["KF Shop Item 7"].rule({}, "child", 1)
    assert not world.locations["KF Shop Item 1"].rule({}, "child", 1)
    assert world.locations["KF Shop Item 1"].rule({"Showed Mido Sword & Shield": 1}, "child", 1)
    rule = world.locations["Market Bombchu Shop Item 1"].rule
    assert not rule({}, "child", 1)
    assert rule({"Defeat King Dodongo": 1}, "child", 1)


def test_bazaar_bombs_and_blue_fire_keep_their_original_release_flags(spec):
    world = build_world(spec)
    bombs = world.locations["Market Bazaar Item 5"].rule
    assert not bombs({}, "child", 1)
    assert bombs({"Defeat King Dodongo": 1}, "child", 1)
    for name in ("Market Potion Shop Item 5", "Kak Potion Shop Item 5"):
        rule = world.locations[name].rule
        assert not rule({}, "adult", 1)
        assert rule({"Blue Fire": 1, "Bottle": 1}, "adult", 1)


def test_tunic_destinations_need_adult_shop_access_and_market_stays_child_only(spec):
    world = build_world(spec)
    settings = Settings(shuffle=("Chest", "Shop"))
    assert not allowed(world, settings, "Market Bazaar Item 1", "Goron Tunic")
    assert allowed(world, settings, "Kak Bazaar Item 1", "Goron Tunic")
    assert not world.locations["GC Shop Item 4"].rule({"Progressive Wallet": 2}, "child", 1)
    market = next(exit for exit in world.regions["Market"].exits if exit.target == "Market Bazaar")
    assert not market.rule({}, "adult", 1)


@pytest.mark.parametrize("shop_prices", ["vanilla", "affordable"])
def test_blue_fire_only_uses_gated_potion_slots_or_non_potion_shops(spec, shop_prices):
    settings, world = prepare(spec, Settings(shuffle=("Chest", "Shop"), shop_prices=shop_prices))
    for merchant in ("Market Potion Shop", "Kak Potion Shop"):
        for slot in range(1, 9):
            name = f"{merchant} Item {slot}"
            assert allowed(world, settings, name, "Buy Blue Fire") is (slot == 5), name
            assert allowed(world, settings, name, "Buy Fish"), name
        rule = world.locations[f"{merchant} Item 5"].rule
        counts = {"Bottle": 1, "Progressive Wallet": 2}
        assert not rule(counts, "adult", 1)
        assert rule({**counts, "Blue Fire": 1}, "adult", 1)
    for merchant in ("KF Shop", "Market Bazaar", "Market Bombchu Shop", "Kak Bazaar", "GC Shop", "ZD Shop"):
        for slot in range(1, 9):
            assert allowed(world, settings, f"{merchant} Item {slot}", "Buy Blue Fire")
    assert not allowed(world, settings, "Deku Tree Basement Chest", "Buy Blue Fire")


def test_blue_fire_seed_cannot_bootstrap_from_an_ungated_potion_slot(spec):
    _, full_world = prepare(spec, Settings(shuffle=("Chest", "Shop")))
    synthetic = {
        "start": "Start",
        "goal": "Buy_Blue_Fire",
        "settings": {
            "native_shop_items": ["Buy Blue Fire", "Buy Fish"],
            "shop_item_locations": full_world.settings["shop_item_locations"],
        },
        # Buying the first Blue Fire sets its owned-content flag; only then does Potion slot5 open.
        "items": {"Buy Blue Fire": {"alias": ["Blue Fire", 1]}, "Buy Fish": {"class": "normal"}, "Blue Fire": {}},
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Market Potion Shop Item 1": {"rule": "True", "type": "Shop", "vanilla": "Buy Blue Fire"},
                    "Market Potion Shop Item 5": {"rule": "Blue_Fire", "type": "Shop", "vanilla": "Buy Fish"},
                    "KF Shop Item 7": {"rule": "True", "type": "Shop", "vanilla": "Buy Fish"},
                },
            }
        ],
    }
    for number in range(20):
        seed = generate(synthetic, number, Settings(shuffle=("Chest", "Shop")), attempts=1)
        # Only this merchant can sell the first Blue Fire; Potion slot5 cannot unlock itself.
        assert seed.placements["KF Shop Item 7"] == "Buy Blue Fire", (number, seed.placements)


@pytest.mark.parametrize(
    "item,helper",
    [("Buy Bottle Bug", "Bugs"), ("Buy Fish", "Fish"), ("Buy Fairy's Spirit", "Fairy"), ("Buy Blue Fire", "Blue_Fire")],
)
def test_bought_refills_do_not_supply_a_bottle(spec, item, helper):
    spec = {**spec, "goal": helper}
    world = build_world(spec)
    assert not Search(world, [item]).won()
    assert Search(world, [item, "Bottle"]).won()


@pytest.mark.parametrize(
    "item,helper",
    [
        ("Goron Tunic", "Goron_Tunic"),
        ("Zora Tunic", "Zora_Tunic"),
        ("Deku Nuts (5)", "Nuts"),
        ("Deku Stick (1)", "Sticks"),
        ("Buy Deku Stick (5)", "Sticks"),
        ("Buy Bombchu (8)", "can_refill_bombchus"),
    ],
)
def test_other_bought_item_helpers_read_normal_inventory_or_native_bundle(spec, item, helper):
    world = build_world({**spec, "goal": helper})
    assert not Search(world).won()
    assert Search(world, [item]).won()


def test_all_fill_stages_respect_native_display_restrictions():
    spec = {
        "start": "Start",
        "goal": "Sword",
        "settings": {"native_shop_items": ["Shield", "Shop Filler"]},
        "items": {
            "Sword": {},
            "Shield": {},
            "Shop Filler": {"class": "normal"},
            "Non-display Filler": {"class": "normal"},
        },
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Shop A": {"rule": "True", "type": "Shop", "vanilla": "Shield"},
                    "Shop B": {"rule": "True", "type": "Shop", "vanilla": "Shop Filler"},
                    "Chest A": {"rule": "True", "type": "Chest", "vanilla": "Sword"},
                    "Chest B": {"rule": "True", "type": "Chest", "vanilla": "Non-display Filler"},
                },
            }
        ],
    }
    world = build_world(spec)
    settings = Settings(shuffle=("Chest", "Shop"))
    for seed in range(30):
        placements = fill(world, settings, random.Random(seed))
        assert placements["Shop A"] in ("Shield", "Shop Filler")
        assert placements["Shop B"] in ("Shield", "Shop Filler")
        assert Counter(placements.values()) == Counter(list(spec["items"]))


def test_shop_mini_seed_is_beatable_with_shield_in_the_shared_pool(spec):
    settings = Settings(
        shuffle=("Chest", "Shop"), areas=("KokiriForest", "LostWood", "InsideTheDekuTree"), goal="'Defeat Queen Gohma'"
    )
    seed = generate(spec, 22, settings)
    search = Search(seed.world)
    search.collect_spheres(seed.placements)
    assert search.won()
    for name in seed.shuffled:
        if seed.world.locations[name].type == "Shop":
            assert allowed(seed.world, settings, name, seed.placements[name])


def test_buy_refill_destination_boundary_uses_effective_settings(spec):
    settings, world = prepare(
        spec, Settings(shuffle=("Chest", "Shop"), item_location_types={"Kokiri Sword": ("Chest",)})
    )
    assert not allowed(world, settings, "Deku Tree Basement Chest", "Buy Bombs (10)")
    assert allowed(world, settings, "KF Shop Item 7", "Buy Bombs (10)")
    for item in world.items:
        if item.startswith("Buy "):
            assert settings.item_location_types[item] == ("Shop",)
    assert settings.item_location_types["Kokiri Sword"] == ("Chest",)
    assert allowed(world, settings, "Deku Tree Basement Chest", "Deku Shield")
    chest_settings, _ = prepare(spec, Settings(item_location_types={"Kokiri Sword": ("Chest",)}))
    assert chest_settings.item_location_types == {
        "Kokiri Sword": ("Chest",),
        "Progressive Hookshot": ("Chest",),
        "Progressive Strength": ("Chest",),
        "Progressive Scale": ("Chest",),
        "Progressive Wallet": ("Chest",),
        "Progressive Bomb Bag": ("Chest",),
        "Progressive Quiver": ("Chest",),
        "Progressive Slingshot": ("Chest",),
        "Progressive Magic": ("Chest",),
    }


@pytest.mark.parametrize("shield_class", ["normal", "progression"])
def test_new_chest_shop_seed_never_places_buy_refills_in_chests(shield_class):
    spec = {
        "start": "Start",
        "goal": "Sword",
        "settings": {"native_shop_items": ["Buy Bombs (10)", "Buy Arrows (10)", "Shield"]},
        "items": {
            "Sword": {},
            "Shield": {"class": shield_class},
            "Buy Bombs (10)": {"class": "priority"},
            "Buy Arrows (10)": {"class": "priority"},
        },
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Shop A": {"rule": "True", "type": "Shop", "vanilla": "Buy Bombs (10)"},
                    "Shop B": {"rule": "True", "type": "Shop", "vanilla": "Buy Arrows (10)"},
                    "Chest A": {"rule": "True", "type": "Chest", "vanilla": "Sword"},
                    "Chest B": {"rule": "True", "type": "Chest", "vanilla": "Shield"},
                },
            }
        ],
    }
    settings = Settings(shuffle=("Chest", "Shop"))
    for number in range(20):
        seed = generate(spec, number, settings, attempts=1)
        assert {seed.placements["Shop A"], seed.placements["Shop B"]} == {"Buy Bombs (10)", "Buy Arrows (10)"}
        assert {seed.placements["Chest A"], seed.placements["Chest B"]} == {"Sword", "Shield"}


def test_refill_reservation_also_leaves_space_for_chest_only_filler():
    spec = {
        "start": "Start",
        "goal": "Sword",
        "settings": {"native_shop_items": ["Buy Bombs (10)", "Shield"]},
        "items": {"Sword": {}, "Shield": {}, "Buy Bombs (10)": {"class": "priority"}, "Rupee": {"class": "normal"}},
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Shop A": {"rule": "True", "type": "Shop", "vanilla": "Buy Bombs (10)"},
                    "Shop B": {"rule": "True", "type": "Shop", "vanilla": "Shield"},
                    "Chest A": {"rule": "True", "type": "Chest", "vanilla": "Sword"},
                    "Chest B": {"rule": "True", "type": "Chest", "vanilla": "Rupee"},
                },
            }
        ],
    }
    for number in range(20):
        seed = generate(spec, number, Settings(shuffle=("Chest", "Shop")), attempts=1)
        assert {seed.placements["Shop A"], seed.placements["Shop B"]} == {"Buy Bombs (10)", "Shield"}
        assert {seed.placements["Chest A"], seed.placements["Chest B"]} == {"Sword", "Rupee"}
