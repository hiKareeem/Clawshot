"""Remake castle rocks, floor switches and traversal must survive shuffled rewards."""

from clawshot.world import ADULT, Search, build_world, load_spec


def castle_world(start):
    spec = load_spec()
    spec["start"] = start
    return build_world(spec)


def test_fire_trial_entrance_needs_gauntlets_as_well_as_heat_protection():
    world = castle_world("Ganons Castle Main")
    search = Search(world, ["Goron Tunic"])
    assert not search.can_reach("Ganons Castle Fire Trial", ADULT)
    search.collect("Golden Gauntlets")
    assert search.can_reach("Ganons Castle Fire Trial", ADULT)


def test_shadow_trial_stone_needs_gauntlets_not_the_old_hammer_switch():
    world = castle_world("Ganons Castle Shadow Trial Second Gap")
    search = Search(world, ["Megaton Hammer", "Lens of Truth", "Magic Meter"])
    assert not search.can_reach("Ganons Castle Shadow Trial Ending", ADULT)
    search = Search(world, ["Golden Gauntlets", "Lens of Truth", "Magic Meter"])
    assert search.can_reach("Ganons Castle Shadow Trial Ending", ADULT)


def test_gauntlets_cannot_self_lock_behind_the_shadow_trial_stone():
    world = castle_world("Ganons Castle Shadow Trial Second Gap")
    search = Search(world, ["Lens of Truth", "Magic Meter"])
    chest = world.locations["Ganons Castle Shadow Trial Golden Gauntlets Chest"]
    search.collect_spheres({chest.name: "Golden Gauntlets"})
    assert chest.name in search.collected
    assert search.can_reach("Ganons Castle Shadow Trial Ending", ADULT)


def test_forest_trial_rupees_do_not_bypass_the_new_traversal():
    world = castle_world("Ganons Castle Forest Trial Wind Room")
    search = Search(world, ["Silver Rupee (Ganons Castle Forest Trial)"] * 5)
    target = "Ganons Castle Forest Trial Ending"
    assert not search.can_reach(target, ADULT)
    for item in ["Ocarina of Time", "Song of Time", "Hover Boots"]:
        search.collect(item)
    assert not search.can_reach(target, ADULT)
    search.collect("Hookshot")
    assert search.can_reach(target, ADULT)


def test_spirit_trial_web_needs_fire_before_reflecting_light():
    world = castle_world("Ganons Castle Spirit Trial Second Room Back")
    search = Search(world, ["Bow", "Mirror Shield", "Magic Meter"])
    target = "Ganons Castle Spirit Trial Ending"
    assert not search.can_reach(target, ADULT)
    search.collect("Fire Arrows")
    assert search.can_reach(target, ADULT)


def test_shadow_trial_torch_accepts_an_arrow_through_the_lit_torch():
    world = castle_world("Ganons Castle Shadow Trial")
    search = Search(world, ["Hover Boots", "Lens of Truth", "Magic Meter"])
    chest = world.locations["Ganons Castle Shadow Trial Golden Gauntlets Chest"]
    assert not search.can_access(chest, ADULT)
    search.collect("Bow")
    assert search.can_access(chest, ADULT)


def test_lullaby_rupee_does_not_invent_a_second_castle_key():
    world = castle_world("Ganons Castle Light Trial")
    search = Search(world, ["Ocarina of Time", "Zeldas Lullaby"])
    lullaby = world.locations["Ganons Castle Light Trial Lullaby Chest"]
    key = world.locations["Ganons Castle Light Trial Invisible Enemies Chest"]
    placement = {loc.name: loc.vanilla for loc in [lullaby, key]}
    search.collect_spheres(placement)
    assert lullaby.name in search.collected
    assert not search.can_reach("Ganons Castle Light Trial Boulder Room", ADULT)
    assert search.counts.get("Small Key (Ganons Castle)", 0) == 0
    search.collect("Lens of Truth")
    search.collect("Magic Meter")
    search.collect_spheres(placement)
    assert search.counts["Small Key (Ganons Castle)"] == 1
    assert search.can_reach("Ganons Castle Light Trial Boulder Room", ADULT)
