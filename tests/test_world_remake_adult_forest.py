"""Remake Forest Temple gates, including the entrance-key self-lock."""

import pytest

from clawshot.world import ADULT, Search, build_world, load_spec


def forest_world(start="Forest Temple Lobby"):
    spec = load_spec()
    spec["start"] = start
    return build_world(spec)


def test_first_key_cannot_be_behind_the_new_front_door():
    world = forest_world()
    search = Search(world)
    search.collect_spheres({"Forest Temple First Stalfos Chest": "Small Key (Forest Temple)"})
    assert not search.can_reach("Forest Temple Central Area", ADULT)
    assert "Forest Temple First Stalfos Chest" not in search.collected

    search = Search(world)
    search.collect_spheres({"Forest Temple First Room Chest": "Small Key (Forest Temple)"})
    assert search.can_reach("Forest Temple Central Area", ADULT)
    assert not search.can_reach("Forest Temple Block Push Room", ADULT)
    search.collect("Small Key (Forest Temple)")
    search.update()
    assert search.can_reach("Forest Temple Block Push Room", ADULT)


@pytest.mark.parametrize("keys,expected", [(2, False), (3, True)])
def test_straightened_hall_counts_the_front_door(keys, expected):
    world = forest_world()
    search = Search(world, ["Small Key (Forest Temple)"] * keys + ["Goron Bracelet", "Bow"])
    search.update()
    assert search.can_reach("Forest Temple Straightened Hall", ADULT) is expected


def test_bow_route_does_not_gain_a_sixth_key_requirement():
    world = forest_world()
    search = Search(world, ["Small Key (Forest Temple)"] * 3 + ["Goron Bracelet"])
    search.update()
    assert search.can_reach("Forest Temple Bow Region", ADULT)
    assert not search.can_reach("Forest Temple Frozen Eye Switch Room", ADULT)
    search.collect("Small Key (Forest Temple)")
    search.collect("Small Key (Forest Temple)")
    search.update()
    assert search.can_reach("Forest Temple Frozen Eye Switch Room", ADULT)


def test_east_garden_token_needs_scarecrow_even_from_falling_room():
    world = forest_world("Forest Temple Falling Room")
    token = world.locations["Forest Temple GS Raised Island Courtyard"]
    search = Search(world, ["Hookshot", "Bow", "Bomb Bag", "Ocarina of Time"])
    search.update()
    assert not search.can_access(token, ADULT)
    search.collect("Scarecrow Song")
    search.update()
    assert search.can_access(token, ADULT)


def test_well_route_uses_the_new_hookshot_target():
    world = forest_world("Forest Temple NW Outdoors")
    search = Search(world)
    search.update()
    assert not search.can_access(world.locations["Forest Temple Well Chest"], ADULT)
    search.collect("Hookshot")
    search.update()
    assert search.can_access(world.locations["Forest Temple Well Chest"], ADULT)


def test_basement_ice_eye_cannot_be_opened_without_the_bow():
    world = forest_world("Forest Temple Basement")
    search = Search(world, ["Boss Key (Forest Temple)", "Dins Fire", "Magic Meter"])
    search.update()
    assert not search.can_reach("Phantom Ganon Boss Room", ADULT)
    search.collect("Bow")
    search.update()
    assert search.can_reach("Phantom Ganon Boss Room", ADULT)
