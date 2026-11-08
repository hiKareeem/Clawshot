"""Kareem's 2026-11-08 play findings, with prerequisites kept around each newly verified route."""

import pytest

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec


def starting_at(region, age=CHILD):
    spec = load_spec()
    spec["settings"]["starting_age"] = age
    spec["start"] = "Playtest Start"
    spec["regions"].append({"name": "Playtest Start", "exits": {region: "is_starting_age"}})
    return build_world(spec)


@pytest.mark.parametrize("weapon", ["Slingshot", "Boomerang"])
def test_child_can_drop_the_slingshot_room_exit_with_either_weapon(weapon):
    world = starting_at("Deku Tree Slingshot Room")
    search = Search(world)
    assert not search.can_reach("Deku Tree Lobby", CHILD)
    search.collect(weapon)
    assert search.can_reach("Deku Tree Lobby", CHILD)
    assert not search.can_reach("Deku Tree Lobby", ADULT)


def test_bow_exit_alternative_is_retained_for_adult_only():
    world = starting_at("Deku Tree Slingshot Room", ADULT)
    search = Search(world, ["Bow"])
    assert search.can_reach("Deku Tree Lobby", ADULT)
    assert not search.can_reach("Deku Tree Lobby", CHILD)


def test_boomerang_opens_basement_eye_but_does_not_burn_the_web():
    world = starting_at("Deku Tree Basement")
    search = Search(world, ["Boomerang", "Deku Shield"])
    assert not search.can_reach("Deku Tree Basement Back Room", CHILD)
    search.collect("Deku Stick (1)")
    assert search.can_reach("Deku Tree Basement Back Room", CHILD)
    assert search.can_reach("Queen Gohma Boss Room", CHILD)


@pytest.mark.parametrize("stun", ["Slingshot", "Boomerang", "Deku Nuts (5)"])
def test_gohma_stun_still_needs_a_damaging_weapon(stun):
    world = starting_at("Queen Gohma Boss Room")
    search = Search(world, [stun])
    assert not search.holds("Defeat Queen Gohma")
    search.collect("Kokiri Sword")
    assert search.holds("Defeat Queen Gohma")


def test_sword_alone_does_not_stun_gohma():
    world = starting_at("Queen Gohma Boss Room")
    assert not Search(world, ["Kokiri Sword"]).holds("Defeat Queen Gohma")
