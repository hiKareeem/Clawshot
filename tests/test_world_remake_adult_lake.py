"""Lake Hylia remake entrance and post-Water access."""

from clawshot.world import ADULT, Search, build_world, load_spec


def test_golden_scale_does_not_substitute_for_water_entry_boots():
    spec = load_spec()
    spec["start"] = "Lake Hylia"
    world = build_world(spec)
    search = Search(world, ["Longshot", "Golden Scale", "Zora Tunic"])
    assert not search.can_reach("Water Temple Lobby", ADULT)
    search.collect("Iron Boots")
    assert search.can_reach("Water Temple Lobby", ADULT)


def test_low_water_scarecrow_does_not_grant_fire_arrows():
    spec = load_spec()
    spec["start"] = "Lake Hylia"
    world = build_world(spec)
    search = Search(world, ["Bow", "Longshot", "Fairy Ocarina", "Scarecrow Song"])
    arrows = world.locations["LH Sun"]
    assert not search.can_access(arrows, ADULT)
    search.collect("Water Temple Clear")
    assert search.can_access(arrows, ADULT)
