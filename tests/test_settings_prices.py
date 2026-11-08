import copy
from dataclasses import replace

import pytest

from clawshot.formats import byml, sarc
from clawshot.generate import Settings, generate, prepare
from clawshot.patch import shops
from clawshot.settings import shop_price
from clawshot.world.load import load_spec


def test_exact_price_removes_conditional_discount_but_keeps_stock_and_release():
    slot = shops.Slot(
        1, "Synthetic Shop", "Shop Item", "Banc/Test.bcett.byml.zs", "Seller", 2, "Shop.bgyml", 0, "Shop_Old", 80
    )
    original = {
        "GoodsList": [
            {
                "Actor": shops.actor_path("Shop_Old"),
                "StockNum": byml.I32(-1),
                "Release": {"ReleaseGameData": "SyntheticStoryGate"},
                "ConditionalPriceOffsetList": [{"GameDataFlag": "SyntheticDiscount", "PriceOffset": byml.I32(-20)}],
            }
        ]
    }
    pack = sarc.write({slot.member: byml.write(original), "unrelated": b"keep"})
    actual = sarc.read(shops.patch_goods(pack, ((slot, shops.Sale("Shop_Old", "Shop_Old", 80, price=10)),)))
    expected = copy.deepcopy(original)
    expected["GoodsList"][0]["PriceOffset"] = byml.I32(-70)
    expected["GoodsList"][0]["ConditionalPriceOffsetList"] = []
    assert byml.same(byml.read(actual[slot.member]), expected)
    assert actual["unrelated"] == b"keep"


@pytest.mark.parametrize(
    ("shuffle", "policy", "wallets", "expected"),
    [
        (("Chest", "Shop"), "affordable", 0, True),
        (("Chest", "Shop"), "vanilla", 1, False),
        (("Chest", "Shop"), "vanilla", 2, True),
        (("Chest",), "affordable", 1, False),
    ],
)
def test_logic_uses_patched_prices_only_for_shuffled_shops(shuffle, policy, wallets, expected):
    spec = load_spec()
    original = copy.deepcopy(spec)
    _, world = prepare(spec, Settings(shuffle=shuffle, shop_prices=policy))
    rule = world.locations["GC Shop Item 4"].rule
    assert rule({"Progressive Wallet": wallets}, "adult", 1) is expected
    assert not rule({"Progressive Wallet": 2}, "child", 1)  # adult-stock restriction remains
    assert not world.locations["Market Bombchu Shop Item 7"].rule({}, "child", 1)  # story gate remains
    assert not world.locations["Market Potion Shop Item 5"].rule({}, "child", 1)  # refill gate remains
    assert spec == original


def test_kokiri_shield_discount_follows_item_not_original_slot_or_other_shops():
    shield = "Shop_Weapon_Shield_Deku"
    assert shop_price("KF Shop", shield, 40) == 10
    assert shop_price("KF Shop", shield, 40, cheap_shield=False) == 40
    assert shop_price("KF Shop", "Shop_Heart", 40) == 40
    assert shop_price("Other Shop", shield, 40) == 40
    assert shop_price("KF Shop", shield, 5) == 10  # exact price, not min(original, 10)
    assert shop_price("Other Shop", "Shop_Heart", 600, shuffled=True, policy="affordable") == 10
    assert shop_price("Other Shop", "Shop_Heart", 600, shuffled=False, policy="affordable") == 600


def test_price_fields_round_trip_and_bad_types_are_refused():
    settings = Settings(shop_prices="affordable", cheap_deku_shield=False, songs="anywhere")
    assert Settings.from_string(settings.to_string()) == settings
    with pytest.raises(ValueError):
        replace(settings, shop_prices="random")
    with pytest.raises(ValueError):
        replace(settings, cheap_deku_shield="false")


def test_shop_fill_preserves_scrub_only_capacity_destinations():
    places = {
        "Only Scrub": ("Scrub", "Capacity"),
        "Shop": ("Shop", "Native"),
        "Chest": ("Chest", "Rupee"),
    }
    spec = {
        "start": "Root",
        "goal": "True",
        "settings": {"native_shop_items": ["Native"]},
        "items": {name: {"class": "normal"} for name in ("Capacity", "Native", "Rupee")},
        "regions": [{"name": "Root", "locations": {name: "True" for name in places}}],
        "locations": {name: {"type": kind, "vanilla": item} for name, (kind, item) in places.items()},
    }
    settings = Settings(
        shuffle=("Chest", "Shop", "Scrub"),
        item_location_types={"Capacity": ("Scrub",)},
    )
    for number in range(20):
        seed = generate(spec, number, settings, attempts=1)
        assert seed.placements == {"Only Scrub": "Capacity", "Shop": "Native", "Chest": "Rupee"}
