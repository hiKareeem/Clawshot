"""Gerudo Training Ground remake routes, searched from starts inside the dungeon."""

import pytest

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec


def world_from(start: str):
    spec = load_spec()
    spec["start"] = start
    return build_world(spec)


@pytest.fixture(scope="module")
def gtg_lobby():
    return world_from("Gerudo Training Ground Lobby")


@pytest.fixture(scope="module")
def gtg_wolfos_room():
    return world_from("Gerudo Training Ground Heavy Block Room")


@pytest.fixture(scope="module")
def gtg_statue_room():
    return world_from("Gerudo Training Ground Eye Statue Lower")


# Gerudo Training Ground


@pytest.mark.parametrize("chest", ["Gerudo Training Ground Lobby Left Chest", "Gerudo Training Ground Lobby Right Chest"])
def test_lobby_chests_need_the_eye_switch_and_the_lens(gtg_lobby, chest):
    location = gtg_lobby.locations[chest]
    search = Search(gtg_lobby, ["Bow"])
    assert not search.can_access(location, ADULT)
    search.collect("Lens of Truth")
    assert not search.can_access(location, ADULT)  # the Lens needs magic
    search.collect("Magic Meter")
    assert search.can_access(location, ADULT)


def test_like_like_room_is_behind_the_room_three_silver_block_and_lens_eye(gtg_wolfos_room):
    room = "Gerudo Training Ground Like Like Room"
    # N64's route (Hookshot up to the eye statue, then the silver block) no longer reaches it without the Bow.
    search = Search(gtg_wolfos_room, ["Hookshot", "Lens of Truth", "Magic Meter", "Silver Gauntlets"])
    assert search.can_reach("Gerudo Training Ground Eye Statue Upper", ADULT)
    assert not search.can_reach(room, ADULT)
    search.collect("Bow")
    assert search.can_reach(room, ADULT)
    # Without the Hookshot: the silver block and the Lens-only eye switch in room 3 are enough.
    search = Search(gtg_wolfos_room, ["Bow", "Lens of Truth", "Magic Meter"])
    assert not search.can_reach(room, ADULT)
    search.collect("Silver Gauntlets")
    assert search.can_reach(room, ADULT)
    assert not search.can_reach(room, CHILD)


def test_heavy_block_chests_ask_for_the_cracked_wall(gtg_wolfos_room):
    search = Search(gtg_wolfos_room, ["Bow", "Lens of Truth", "Magic Meter", "Silver Gauntlets"])
    first = gtg_wolfos_room.locations["Gerudo Training Ground Heavy Block First Chest"]
    second = gtg_wolfos_room.locations["Gerudo Training Ground Heavy Block Second Chest"]
    third = gtg_wolfos_room.locations["Gerudo Training Ground Heavy Block Third Chest"]
    assert search.can_access(third, ADULT)
    assert not search.can_access(first, ADULT)
    assert not search.can_access(second, ADULT)
    search.collect("Megaton Hammer")
    assert search.can_access(first, ADULT)
    assert search.can_access(second, ADULT)


def test_near_scarecrow_key_is_beyond_the_scarecrow_from_the_statue_floor(gtg_statue_room):
    chest = gtg_statue_room.locations["Gerudo Training Ground Near Scarecrow Chest"]
    search = Search(gtg_statue_room, ["Bow", "Hookshot", "Fairy Ocarina", "Scarecrow Song"])
    assert not search.can_access(chest, ADULT)
    search.collect("Longshot")
    assert search.can_access(chest, ADULT)
    search = Search(gtg_statue_room, ["Longshot", "Fairy Ocarina", "Scarecrow Song"])
    assert not search.can_access(chest, ADULT)  # the statue (Bow) opens the upper door


def test_scarecrow_key_loop_still_needs_the_lens_and_hookshot_ledge(gtg_statue_room):
    chest = gtg_statue_room.locations["Gerudo Training Ground Near Scarecrow Chest"]
    search = Search(gtg_statue_room, ["Bow", "Goron Tunic"])
    assert not search.can_access(chest, ADULT)
    search.collect("Hookshot")
    search.collect("Lens of Truth")
    search.collect("Magic Meter")
    assert search.can_access(chest, ADULT)
