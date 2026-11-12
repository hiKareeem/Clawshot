"""Warnings follow actual acquisition-age frontiers, not location/region name guesses."""

import pytest

from clawshot.generate import Seed, Settings, play_note, spoiler
from clawshot.generate.itembar import age_locked_pickups
from clawshot.world import Search, build_world


def seed_with(placements, rules, *, starting_age="child", events=None, settings=None, shuffled=None):
    world = build_world(
        {
            "start": "Root",
            "goal": "True",
            "settings": {"starting_age": starting_age, **(settings or {})},
            "items": {item: {} for item in placements.values()},
            "locations": {name: {"type": "Chest", "vanilla": item} for name, item in placements.items()},
            "regions": [
                {"name": "Root", "exits": {"Field": "age == starting_age or 'Time Travel'"}},
                {"name": "Field", "locations": rules, "events": events or {}},
            ],
        }
    )
    spheres = Search(world).collect_spheres(placements)
    return Seed(world, 9, Settings(), placements, list(placements) if shuffled is None else shuffled, spheres)


@pytest.mark.parametrize("item", ["Bow", "Hookshot", "Longshot", "Megaton Hammer", "Ice Arrows", "Pocket Egg"])
def test_adult_only_items_reachable_as_child_are_named_with_their_real_check(item):
    seed = seed_with({"Early chest": item}, {"Early chest": "True"})
    [warning] = age_locked_pickups(seed)
    assert (warning.location, warning.item, warning.usable_age, warning.first_ages) == (
        "Early chest",
        item,
        "adult",
        ("child",),
    )
    assert seed.placements == {"Early chest": item}  # Reporting never replaces the reward.


@pytest.mark.parametrize("item", ["Slingshot", "Boomerang", "Deku Stick (1)", "Magic Bean"])
def test_reverse_direction_warns_when_adult_can_get_the_child_item_first(item):
    seed = seed_with({"Adult chest": item}, {"Adult chest": "True"}, starting_age="adult")
    [warning] = age_locked_pickups(seed)
    assert (warning.usable_age, warning.first_ages) == ("child", ("adult",))


def test_same_frontier_tie_is_not_silently_classified_as_safe():
    seed = seed_with({"Shared chest": "Bow"}, {"Shared chest": "True"}, events={"Time Travel": "True"})
    [warning] = age_locked_pickups(seed)
    assert set(warning.first_ages) == {"child", "adult"}
    assert warning.usable_age == "adult"


def test_matching_age_both_age_items_and_fixed_rewards_are_not_warning_rows():
    seed = seed_with(
        {"Adult Bow": "Bow", "Child Sling": "Slingshot", "Nut": "Deku Nuts (5)", "Fixed Bow": "Bow"},
        {"Adult Bow": "age == 'adult'", "Child Sling": "age == 'child'", "Nut": "True", "Fixed Bow": "True"},
        events={"Time Travel": "True"},
        shuffled=["Adult Bow", "Child Sling", "Nut"],
    )
    assert age_locked_pickups(seed) == []


def test_frontier_uses_fixed_prerequisites_without_assuming_later_items():
    seed = seed_with(
        {"Fixed key": "Key", "Child Bow": "Bow", "Later adult permit": "Permit"},
        {"Fixed key": "True", "Child Bow": "Key", "Later adult permit": "Bow and age == 'adult'"},
        events={"Time Travel": "Permit"},
        shuffled=["Child Bow"],
    )
    [warning] = age_locked_pickups(seed)
    assert (warning.first_ages, warning.sphere) == (("child",), 2)


def test_adult_finds_cannot_fake_child_first_access_before_the_return_gate():
    seed = seed_with(
        {"Pull key": "Key", "Adult key": "Permit", "Delayed Bow": "Bow"},
        {"Pull key": "age == 'child'", "Adult key": "age == 'adult'", "Delayed Bow": "Permit"},
        events={"Time Travel": "Key"},
        settings={"age_return_event": "Forest Clear", "age_return_region": "Field"},
        shuffled=["Delayed Bow"],
    )
    assert age_locked_pickups(seed) == []  # Only adult has Permit; child's prefix must not borrow it.
    returned = seed_with(
        seed.placements,
        {"Pull key": "age == 'child'", "Adult key": "age == 'adult'", "Delayed Bow": "Permit"},
        events={"Time Travel": "Key", "Forest Clear": "age == 'adult' and Permit"},
        settings={"age_return_event": "Forest Clear", "age_return_region": "Field"},
        shuffled=["Delayed Bow"],
    )
    [warning] = age_locked_pickups(returned)
    assert set(warning.first_ages) == {"child", "adult"}


def test_spoiler_and_rendered_note_expose_the_warning_at_the_actual_destination():
    seed = seed_with({"Crate | chest": "Bow"}, {"Crate | chest": "True"})
    log = spoiler(seed)
    [warning] = log["age_locked_pickups"]
    assert warning["item"] == "Bow" and warning["location"] == "Crate | chest"
    note = play_note(seed, log)
    # Parse the warning's table by its ages and destination rather than pin prose, item wording or a placement.
    rows = [
        line.removeprefix("| ").removesuffix(" |").split(" | ") for line in note.splitlines() if line.startswith("| ")
    ]
    warnings = [row for row in rows if row[1:3] == ["adult", "child"]]
    assert len(warnings) == 1
    assert warnings[0][3:] == [r"Crate \| chest", r"Crate \| chest", "Field"]
