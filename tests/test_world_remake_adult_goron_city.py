"""A ceiling token cannot be awarded merely for reaching adult Goron City."""

from clawshot.world import ADULT, Search, build_world, load_spec


def test_goron_city_ceiling_token_needs_hookshot():
    spec = load_spec()
    spec["start"] = "Goron City"
    world = build_world(spec)
    search = Search(world, ["Bow"])
    token = world.locations["GC GS Center Platform"]
    assert not search.can_access(token, ADULT)
    search.collect("Hookshot")
    assert search.can_access(token, ADULT)
