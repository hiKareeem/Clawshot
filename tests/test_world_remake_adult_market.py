"""The remake Poe Collector's bottle threshold is five, despite the retained N64 name."""

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec


def test_fifth_bottled_poe_unlocks_the_collector_reward():
    spec = load_spec()
    spec["start"] = "Market Guard House"
    world = build_world(spec)
    search = Search(world, ["Bottle with Big Poe"] * 4)
    reward = world.locations["Market 10 Big Poes"]
    assert not search.can_access(reward, ADULT)
    search.collect("Bottle with Big Poe")
    assert search.can_access(reward, ADULT)
    assert not search.can_access(reward, CHILD)
