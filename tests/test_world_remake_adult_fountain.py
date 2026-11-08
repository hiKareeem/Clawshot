"""The remodeled fountain cave uses gauntlets and lenses, not N64 bomb rocks."""

from clawshot.world import ADULT, Search, build_world, load_spec


def test_fountain_cave_needs_lenses_but_not_bombs():
    spec = load_spec()
    spec["start"] = "Zoras Fountain"
    world = build_world(spec)
    search = Search(world, ["Silver Gauntlets", "Hookshot", "Magic Meter"])
    token = world.locations["ZF GS Hidden Cave"]
    assert not search.can_access(token, ADULT)
    search.collect("Lens of Truth")
    assert search.can_access(token, ADULT)
