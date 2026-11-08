"""The crater wall heart has a documented child climb, not a Hookshot requirement."""

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec


def test_crater_wall_has_child_heat_route_and_safe_adult_tunic_route():
    spec = load_spec()
    spec["start"] = "DMC Upper Local"
    world = build_world(spec)
    search = Search(world)
    heart = world.locations["DMC Wall Freestanding PoH"]
    assert search.can_access(heart, CHILD)
    assert not search.can_access(heart, ADULT)
    search.collect("Goron Tunic")
    assert search.can_access(heart, ADULT)
    assert search.can_access(heart, CHILD)
    world = build_world(load_spec(), {"damage_multiplier": "ohko"})
    search = Search(world)
    assert not world.locations["DMC Wall Freestanding PoH"].rule(search.counts, CHILD, 1)
