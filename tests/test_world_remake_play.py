"""Kareem's 2026-11-08 play findings, with prerequisites kept around each newly verified route."""

import pytest

from clawshot.generate import Settings, prepare
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


@pytest.mark.parametrize("name", ["HF Ocarina of Time Item", "Song from Ocarina of Time"])
def test_shallow_moat_needs_stones_but_no_scale(name):
    world = starting_at("Hyrule Field")
    search = Search(world, ["Kokiri Emerald", "Goron Ruby"])
    assert not search.can_access(world.locations[name], CHILD)
    search.collect("Zora Sapphire")
    assert search.can_access(world.locations[name], CHILD)
    assert not search.holds("Progressive Scale")
    adult = starting_at("Hyrule Field", ADULT)
    assert not Search(adult, ["Kokiri Emerald", "Goron Ruby", "Zora Sapphire"]).can_access(adult.locations[name], ADULT)


@pytest.mark.parametrize(
    "items",
    [[], ["Kokiri Sword"], ["Hylian Shield"], ["Kokiri Sword", "Boomerang"]],
)
def test_free_shield_cannot_bootstrap_kept_mido(items):
    world = build_world(load_spec())
    search = Search(world, items)
    assert not search.holds("Deku Shield")
    assert not search.can_reach("KF Outside Deku Tree", CHILD)
    assert not search.can_reach("Deku Tree Slingshot Room", CHILD)


def test_post_mido_free_shield_opens_the_scrub_without_buying_a_deku_shield():
    world = build_world(load_spec())
    search = Search(world, ["Kokiri Sword", "Hylian Shield"])
    assert search.can_reach("KF Outside Deku Tree", CHILD)
    assert search.holds("Deku Shield")
    assert not search.holds("Buy Deku Shield")
    assert search.can_reach("Deku Tree Slingshot Room", CHILD)
    assert not search.holds("Defeat Queen Gohma")
    assert not search.can_reach("LW Bridge From Forest", CHILD)


@pytest.mark.parametrize("forest", ["closed", "closed_deku", "open"])
def test_free_shield_follows_the_merged_forest_mode_without_bootstrapping_mido(forest):
    _, world = prepare(load_spec(), Settings(forest=forest))
    search = Search(world)
    assert search.holds("Deku Shield") is (forest == "open")
    assert not search.holds("Kokiri Sword")
    assert search.can_reach("Deku Tree Slingshot Room", CHILD) is (forest == "open")
    assert search.can_reach("LW Bridge From Forest", CHILD) is (forest != "closed")


def test_adult_cannot_claim_the_child_shopkeepers_free_shield():
    world = starting_at("KF Kokiri Shop", ADULT)
    search = Search(world, ["Kokiri Sword", "Hylian Shield"])
    assert not search.holds("Deku Shield")
