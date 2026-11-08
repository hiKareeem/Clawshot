"""Remake Water Temple: actual four-lock progression, remodeled rooms and moved checks."""

import pytest

from clawshot.world import ADULT, Search, build_world, load_spec

GEAR = ["Hookshot", "Iron Boots", "Zora Tunic", "Fairy Ocarina", "Zeldas Lullaby"]


def water_world(start="Water Temple Lobby"):
    spec = load_spec()
    spec["start"] = start
    spec["goal"] = "'Defeat Morpha'"
    return build_world(spec)


def test_map_is_available_before_lullaby_or_keys():
    world = water_world()
    search = Search(world, ["Hookshot", "Iron Boots", "Zora Tunic"])
    assert search.can_access(world.locations["Water Temple Map Chest"], ADULT)
    assert not search.can_reach("Water Temple Middle Water Level", ADULT)


@pytest.mark.parametrize("keys,expected", [(0, False), (1, True)])
def test_pillar_door_cannot_be_replaced_by_a_bow(keys, expected):
    world = water_world()
    search = Search(world, GEAR + ["Bow"] + ["Small Key (Water Temple)"] * keys)
    assert search.can_reach("Water Temple Middle Water Level", ADULT) is expected
    assert search.can_access(world.locations["Water Temple GS Behind Gate"], ADULT) is expected


def test_compass_and_pillar_basement_no_longer_share_the_old_south_region():
    world = water_world()
    search = Search(world, GEAR + ["Small Key (Water Temple)"])
    assert search.can_access(world.locations["Water Temple Central Pillar Chest"], ADULT)
    assert search.can_access(world.locations["Water Temple GS Behind Gate"], ADULT)
    assert not search.can_access(world.locations["Water Temple Compass Chest"], ADULT)
    search.collect("Bomb Bag")
    assert search.can_access(world.locations["Water Temple Compass Chest"], ADULT)


def test_ruto_cracked_wall_token_is_not_on_the_longshot_route():
    world = water_world()
    search = Search(world, GEAR + ["Small Key (Water Temple)"])
    token = world.locations["Water Temple GS Falling Platform Room"]
    assert not search.can_access(token, ADULT)
    search.collect("Bomb Bag")
    assert search.can_access(token, ADULT)
    assert not search.can_reach("Water Temple Falling Platform Room", ADULT)


def test_river_exit_needs_longshot_not_song_of_time():
    world = water_world("Water Temple Dark Link Region")
    search = Search(world, ["Hookshot", "Fairy Ocarina", "Song of Time"])
    assert not search.can_reach("Water Temple River", ADULT)
    search.collect("Longshot")
    assert search.can_reach("Water Temple River", ADULT)


def test_final_key_requires_longshot_and_middle_water():
    world = water_world()
    search = Search(world, GEAR + ["Bow", "Goron Bracelet", "Hover Boots", "Small Key (Water Temple)"])
    assert not search.can_access(world.locations["Water Temple Central Bow Target Chest"], ADULT)
    search.collect("Longshot")
    assert search.can_access(world.locations["Water Temple Central Bow Target Chest"], ADULT)


def test_fourth_key_opens_north_route_without_a_fifth():
    world = water_world()
    search = Search(world, GEAR + ["Longshot", "Bomb Bag", "Goron Bracelet"] + ["Small Key (Water Temple)"] * 3)
    boss_key = world.locations["Water Temple Boss Key Chest"]
    assert not search.can_access(boss_key, ADULT)
    search.collect("Small Key (Water Temple)")
    assert search.can_access(boss_key, ADULT)
    assert search.can_access(world.locations["Water Temple GS Near Boss Key Chest"], ADULT)


def test_four_real_key_routes_bootstrap_longshot_and_boss_without_free_keys():
    world = water_world()
    names = [
        "Water Temple Torches Chest",
        "Water Temple Dragon Chest",
        "Water Temple Cracked Wall Chest",
        "Water Temple Central Bow Target Chest",
        "Water Temple Longshot Chest",
        "Water Temple Boss Key Chest",
    ]
    placements = {name: world.locations[name].vanilla for name in names}
    search = Search(world, GEAR + ["Bow", "Bomb Bag", "Goron Bracelet"])
    search.collect_spheres(placements)
    assert search.won()
    assert search.counts["Small Key (Water Temple)"] == 4
    assert search.collected == set(names)

    placements["Water Temple Central Bow Target Chest"] = "Longshot"
    placements["Water Temple Longshot Chest"] = "Small Key (Water Temple)"
    search = Search(world, GEAR + ["Bow", "Bomb Bag", "Goron Bracelet"])
    search.collect_spheres(placements)
    assert not search.won()
    assert "Water Temple Central Bow Target Chest" not in search.collected


def test_boss_slope_needs_iron_boots_even_with_boss_key():
    world = water_world("Water Temple Before Boss")
    search = Search(world, ["Boss Key (Water Temple)", "Longshot"])
    assert not search.can_reach("Morpha Boss Room", ADULT)
    search.collect("Iron Boots")
    assert search.can_reach("Morpha Boss Room", ADULT)
