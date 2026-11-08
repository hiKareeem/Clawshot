"""Remake Fire Temple progression with real acquired keys, not OoTR's free starting key."""

import pytest

from clawshot.world import ADULT, Search, build_world, load_spec

GEAR = ["Goron Tunic", "Goron Bracelet", "Hookshot", "Bow", "Bomb Bag", "Fairy Ocarina", "Song of Time"]


def fire_world(start="Fire Temple Lower"):
    spec = load_spec()
    spec["start"] = start
    spec["goal"] = "'Defeat Volvagia'"
    return build_world(spec)


@pytest.mark.parametrize("keys,expected", [(0, False), (1, True)])
def test_one_real_key_opens_big_lava_room(keys, expected):
    world = fire_world()
    search = Search(world, GEAR + ["Small Key (Fire Temple)"] * keys)
    assert search.can_reach("Fire Temple Big Lava Room", ADULT) is expected


def test_map_and_compass_are_in_their_remake_rooms():
    world = fire_world()
    search = Search(world, ["Goron Tunic", "Goron Bracelet", "Hookshot"] + ["Small Key (Fire Temple)"] * 3)
    assert search.can_access(world.locations["Fire Temple Map Chest"], ADULT)
    assert not search.can_access(world.locations["Fire Temple Compass Chest"], ADULT)
    search.collect("Small Key (Fire Temple)")
    assert search.can_reach("Fire Temple Boulder Maze Upper", ADULT)
    assert not search.can_access(world.locations["Fire Temple Compass Chest"], ADULT)
    search.collect("Bow")
    assert search.can_access(world.locations["Fire Temple Compass Chest"], ADULT)


def test_lower_maze_does_not_grant_the_flame_maze_key():
    world = fire_world()
    search = Search(world, GEAR + ["Small Key (Fire Temple)"] * 4)
    key = world.locations["Fire Temple Boulder Maze Side Room Chest"]
    assert search.can_reach("Fire Temple Boulder Maze Upper", ADULT)
    assert not search.can_access(key, ADULT)
    search.collect("Small Key (Fire Temple)")
    assert search.can_access(key, ADULT)


@pytest.mark.parametrize("keys,expected", [(7, False), (8, True)])
def test_boss_key_loop_needs_all_eight_real_keys(keys, expected):
    world = fire_world()
    search = Search(world, GEAR + ["Megaton Hammer"] + ["Small Key (Fire Temple)"] * keys)
    assert search.can_access(world.locations["Fire Temple Boss Key Chest"], ADULT) is expected


def test_hover_boots_do_not_replace_lowering_the_boss_pillar():
    world = fire_world("Fire Temple Near Boss")
    search = Search(world, ["Hover Boots", "Goron Tunic", "Boss Key (Fire Temple)"])
    assert not search.can_reach("Volvagia Boss Room", ADULT)

    world = fire_world("Fire Temple Upper")
    search = Search(world, ["Megaton Hammer", "Goron Tunic", "Bomb Bag", "Boss Key (Fire Temple)"])
    assert not search.can_reach("Volvagia Boss Room", ADULT)
    search.collect("Fairy Ocarina")
    search.collect("Song of Time")
    assert search.can_reach("Volvagia Boss Room", ADULT)


def test_eight_real_key_routes_bootstrap_hammer_and_boss():
    world = fire_world()
    names = [
        "Fire Temple Near Boss Chest",
        "Fire Temple Big Lava Room Lower Open Door Chest",
        "Fire Temple Big Lava Room Blocked Door Chest",
        "Fire Temple Boulder Maze Lower Chest",
        "Fire Temple Boulder Maze Upper Chest",
        "Fire Temple Boulder Maze Shortcut Chest",
        "Fire Temple Boulder Maze Side Room Chest",
        "Fire Temple Highest Goron Chest",
        "Fire Temple Megaton Hammer Chest",
        "Fire Temple Boss Key Chest",
    ]
    search = Search(world, GEAR)
    search.collect_spheres({name: world.locations[name].vanilla for name in names})
    assert search.won()
    assert search.counts["Small Key (Fire Temple)"] == 8
    assert search.collected == set(names)


def test_default_settings_do_not_invent_the_first_fire_key():
    world = fire_world()
    search = Search(world, ["Goron Tunic"])
    assert not search.can_reach("Fire Temple Big Lava Room", ADULT)
    search.collect("Small Key (Fire Temple)")
    assert search.can_reach("Fire Temple Big Lava Room", ADULT)
