"""Native child-story prerequisites are independent of shuffled item ownership (section 46)."""

import pytest

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec
from clawshot.world.rules import ALL_TIMES

STONES = {"Kokiri Emerald": 1, "Goron Ruby": 1, "Zora Sapphire": 1}
MET_ZELDA = "Met Child Zelda"


@pytest.mark.parametrize("name", ["HF Ocarina of Time Item", "Song from Ocarina of Time"])
def test_moat_rewards_need_the_courtyard_and_each_stone_but_no_scale(name):
    world = build_world(load_spec())
    rule = world.locations[name].rule
    assert not rule(STONES, CHILD, ALL_TIMES)
    ready = STONES | {MET_ZELDA: 1}
    assert rule(ready, CHILD, ALL_TIMES)
    assert not rule(ready, ADULT, ALL_TIMES)
    for stone in STONES:
        assert not rule({item: count for item, count in ready.items() if item != stone}, CHILD, ALL_TIMES)


@pytest.mark.parametrize("trade_item", ["Weird Egg", "Chicken"])
def test_meeting_zelda_follows_the_native_castle_route_not_stone_ownership(trade_item):
    spec = load_spec()
    spec["start"] = "Hyrule Field"
    world = build_world(spec)
    search = Search(world, STONES)
    assert not search.can_reach("HC Garden", CHILD)
    assert not search.holds(MET_ZELDA)
    search.collect(trade_item)
    assert search.can_reach("HC Garden", CHILD)
    assert search.holds(MET_ZELDA)
    assert search.holds("Time Flows")
    assert search.can_access(world.locations["HF Ocarina of Time Item"], CHILD)
    assert search.can_access(world.locations["Song from Ocarina of Time"], CHILD)
