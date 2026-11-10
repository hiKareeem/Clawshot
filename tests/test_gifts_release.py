"""Released gifts contribute their placed item, not an assumed early bottle."""

import pytest

from clawshot.generate import Settings, prepare
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import gifts
from clawshot.world.load import load_spec
from clawshot.world.search import Search

RELEASED = (gifts.MARKET_BOTTLE_CHECK, gifts.DAMPE_CHECK)


@pytest.mark.parametrize("shuffle", [("Chest",), ("Chest", *gifts.GIFT_TYPES)])
def test_bottle_access_uses_the_selected_reward_not_a_fixed_early_bottle(shuffle):
    spec = load_spec()
    spec["start"] = "Market Potion Shop"
    shop = next(region for region in spec["regions"] if region["name"] == spec["start"])
    shop["locations"]["Bottle-dependent probe"] = {"rule": "has_bottle", "type": "NPC"}
    _, world = prepare(spec, Settings(shuffle=shuffle))
    selected = shuffled_locations(world, Settings(shuffle=shuffle))
    gift_shuffle = "NPC" in shuffle
    assert all((name in selected) is gift_shuffle for name in RELEASED)
    # Isolate this source: no other fixed bottle or later route can mask an assumed grant.
    item = "Boomerang" if gift_shuffle else world.locations[gifts.MARKET_BOTTLE_CHECK].vanilla
    search = Search(world)
    search.collect_spheres({gifts.MARKET_BOTTLE_CHECK: item})
    assert search.counts.get("Bottle", 0) == (0 if gift_shuffle else 1)
    assert search.counts.get("Boomerang", 0) == int(gift_shuffle)
    # A bottle-dependent check must not open merely because the merchant was collected.
    assert search.can_access(world.locations["Bottle-dependent probe"], "child") is not gift_shuffle


def test_releasing_two_gifts_does_not_release_other_experiments():
    _, world = prepare(load_spec(), Settings(shuffle=gifts.GIFT_TYPES))
    selected = set(shuffled_locations(world, Settings(shuffle=gifts.GIFT_TYPES)))
    assert set(RELEASED) <= selected
    for name in (
        *gifts.GALLERY_EXPERT_CHECKS.values(),
        "GC Medigoron",
        "Wasteland Bombchu Salesman",
        "Kak Granny Buy Blue Potion",
        "Kak 40 Gold Skulltula Reward",
    ):
        assert name not in selected, name
        assert world.locations[name].keep_vanilla, name
