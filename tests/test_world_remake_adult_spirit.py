"""Spirit Temple token geometry differs from N64 despite the five-key count matching."""

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec


def spirit_world(start):
    spec = load_spec()
    spec["start"] = start
    return build_world(spec)


def test_statue_corner_token_does_not_require_a_hookshot_or_boomerang():
    world = spirit_world("Spirit Temple Central Chamber")
    search = Search(world, ["Bomb Bag"])
    token = world.locations["Spirit Temple GS Lobby"]
    assert not search.can_access(token, ADULT)
    assert not search.can_access(token, CHILD)
    search.collect("Goron Bracelet")
    assert search.can_access(token, ADULT)
    assert search.can_access(token, CHILD)


def test_statue_hand_token_requires_adult_longshot_and_scarecrow():
    world = spirit_world("Spirit Temple Central Chamber")
    token = world.locations["Spirit Temple GS Sun on Floor Room"]
    search = Search(world, ["Hookshot", "Fairy Ocarina", "Scarecrow Song"] + ["Small Key (Spirit Temple)"] * 3)
    assert not search.can_access(token, ADULT)
    search.collect("Longshot")
    assert search.can_access(token, ADULT)
    assert not search.can_access(token, CHILD)


def test_old_child_climb_cannot_collect_the_moved_statue_hand_token():
    world = spirit_world("Child Spirit Temple Climb")
    search = Search(world, ["Longshot", "Fairy Ocarina", "Scarecrow Song"] + ["Small Key (Spirit Temple)"] * 3)
    token = world.locations["Spirit Temple GS Sun on Floor Room"]
    assert not search.can_access(token, ADULT)
    search.collect("Bomb Bag")
    assert not search.can_access(token, ADULT)
    search.collect("Goron Bracelet")
    assert search.can_access(token, ADULT)


def test_sun_block_key_uses_window_light_not_fire_or_silver_rupees():
    world = spirit_world("Spirit Temple Central Chamber")
    search = Search(world, ["Bomb Bag"])
    chest = world.locations["Spirit Temple Sun Block Room Chest"]
    assert not search.can_access(chest, CHILD)
    assert not search.can_access(chest, ADULT)
    search.collect("Goron Bracelet")
    assert search.can_access(chest, CHILD)
    assert search.can_access(chest, ADULT)


def test_hand_key_cannot_ignore_the_return_route_to_the_other_hand():
    world = spirit_world("Adult Spirit Temple Climb")
    chest = world.locations["Spirit Temple Statue Room Hand Chest"]
    search = Search(world, ["Fairy Ocarina", "Zeldas Lullaby", "Longshot"])
    assert not search.can_access(chest, ADULT)
    search.collect("Scarecrow Song")
    assert search.can_access(chest, ADULT)
