"""The remake's documented adult crater-wall heart route."""

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec


def test_crater_wall_needs_both_safe_route_items():
    spec = load_spec()
    spec["start"] = "DMC Upper Local"
    world = build_world(spec)
    search = Search(world)
    heart = world.locations["DMC Wall Freestanding PoH"]
    assert not search.can_access(heart, ADULT)
    search.collect("Hookshot")
    assert not search.can_access(heart, ADULT)
    search.collect("Goron Tunic")
    assert search.can_access(heart, ADULT)
    assert not search.can_access(heart, CHILD)
