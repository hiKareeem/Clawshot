"""Remake Shadow Temple moved checks, real bombs and fifth-key placement safety."""

from clawshot.world import ADULT, Search, build_world, load_spec


def shadow_world(start):
    spec = load_spec()
    spec["start"] = start
    return build_world(spec)


def test_wind_token_is_not_in_the_silver_rupee_skull_room():
    world = shadow_world("Shadow Temple Invisible Spikes")
    token = world.locations["Shadow Temple GS Single Giant Pot"]
    search = Search(world, ["Longshot"] + ["Silver Rupee (Shadow Temple Invisible Spikes)"] * 5)
    assert not search.can_access(token, ADULT)
    for _ in range(3):
        search.collect("Small Key (Shadow Temple)")
    assert search.can_access(token, ADULT)

    search = Search(world, ["Hookshot"] + ["Small Key (Shadow Temple)"] * 3)
    assert search.can_reach("Shadow Temple Wind Tunnel", ADULT)
    assert not search.can_access(token, ADULT)


def test_ship_token_requires_scarecrow_not_longshot_alone():
    world = shadow_world("Shadow Temple Boat")
    search = Search(world, ["Longshot"])
    token = world.locations["Shadow Temple GS Near Ship"]
    assert not search.can_access(token, ADULT)
    search.collect("Fairy Ocarina")
    search.collect("Scarecrow Song")
    assert search.can_access(token, ADULT)


def test_bracelet_cannot_supply_a_missing_bomb_flower():
    world = shadow_world("Shadow Temple Invisible Spikes")
    search = Search(world, ["Goron Bracelet"] + ["Silver Rupee (Shadow Temple Invisible Spikes)"] * 5)
    key = world.locations["Shadow Temple Freestanding Key"]
    assert not search.can_access(key, ADULT)
    search.collect("Bomb Bag")
    assert search.can_access(key, ADULT)


def test_rotating_skull_token_and_web_need_real_explosives():
    world = shadow_world("Shadow Temple Beyond Boat")
    search = Search(world, ["Goron Bracelet"])
    token = world.locations["Shadow Temple GS Triple Giant Pot"]
    chest = world.locations["Shadow Temple Invisible Floormaster Chest"]
    assert not search.can_access(token, ADULT)
    assert not search.can_access(chest, ADULT)
    search.collect("Dins Fire")
    search.collect("Magic Meter")
    assert search.can_access(chest, ADULT)
    assert not search.can_access(token, ADULT)
    search.collect("Bomb Bag")
    assert search.can_access(token, ADULT)


def test_fifth_key_cannot_self_lock_in_the_spike_wall_room():
    world = shadow_world("Shadow Temple Beyond Boat")
    search = Search(world, ["Dins Fire", "Magic Meter"] + ["Small Key (Shadow Temple)"] * 4)
    boss_key_chest = world.locations["Shadow Temple Boss Key Chest"]
    search.collect_spheres({boss_key_chest.name: "Small Key (Shadow Temple)"})
    assert boss_key_chest.name not in search.collected
    search.collect("Small Key (Shadow Temple)")
    assert search.can_access(boss_key_chest, ADULT)


def test_scarecrow_ledge_does_not_bypass_the_statue_bridge():
    world = shadow_world("Shadow Temple Beyond Boat")
    search = Search(world, ["Longshot", "Fairy Ocarina", "Scarecrow Song"])
    assert not search.can_reach("Shadow Temple Before Boss", ADULT)
    search.collect("Bow")
    assert not search.can_reach("Shadow Temple Before Boss", ADULT)
    search.collect("Bomb Bag")
    assert not search.can_reach("Shadow Temple Before Boss", ADULT)
    search.collect("Goron Bracelet")
    assert search.can_reach("Shadow Temple Before Boss", ADULT)


def test_boss_door_requires_the_boss_key():
    world = shadow_world("Shadow Temple Before Boss")
    search = Search(world)
    assert not search.can_reach("Bongo Bongo Boss Room", ADULT)
    search.collect("Boss Key (Shadow Temple)")
    assert search.can_reach("Bongo Bongo Boss Room", ADULT)


def test_falling_spikes_token_has_a_normal_cube_and_ceiling_route():
    world = shadow_world("Shadow Temple Falling Spikes")
    search = Search(world)
    token = world.locations["Shadow Temple GS Falling Spikes Room"]
    assert not search.can_access(token, ADULT)
    search.collect("Goron Bracelet")
    assert search.can_access(token, ADULT)
