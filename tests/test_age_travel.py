"""Chronological child-prefix inventory on synthetic, gated two-age worlds."""

from dataclasses import replace

import pytest

from clawshot.generate.fill import FillError, check_beatable
from clawshot.world import ADULT, CHILD, Search, build_world
from clawshot.world.model import Event, Item
from clawshot.world.rules import Rule


def age_world(*, child_key=False, adult_start=False):
    return build_world(
        {
            "start": "Root",
            "goal": "Victory",
            "settings": {
                "starting_age": "adult" if adult_start else "child",
                "age_return_event": "Forest Clear",
                "age_return_region": "Temple",
            },
            "items": {name: {} for name in ("Hookshot", "Key", "Prize")},
            "regions": [
                {
                    "name": "Root",
                    "exits": {"Field": "age == starting_age or 'Time Travel'"},
                },
                {
                    "name": "Field",
                    "exits": {"Temple": "True", "Child Ledge": "age == 'child' and Hookshot"},
                    "locations": {
                        "Adult Item": {"rule": "age == 'adult'", "type": "Chest"},
                        "Child Key": {
                            "rule": "age == 'child'" if child_key else "age == 'child' and Hookshot",
                            "type": "Chest",
                        },
                    },
                    "events": {"Forest Clear": "age == 'adult' and Key"},
                },
                {"name": "Temple", "events": {"Time Travel": "True"}},
                {
                    "name": "Child Ledge",
                    "locations": {"Child Prize": {"rule": "True", "type": "Chest"}},
                    "events": {"Victory": "age == 'child'"},
                },
            ],
        }
    )


PLACEMENTS = {"Adult Item": "Hookshot", "Child Key": "Key", "Child Prize": "Prize"}


def test_adult_item_cannot_bootstrap_its_own_child_return():
    search = Search(age_world())
    search.collect_spheres(PLACEMENTS)
    assert search.counts.get("Hookshot") == 1
    assert not search.can_reach("Child Ledge", CHILD)
    assert "Child Key" not in search.collected
    assert not search.holds("Forest Clear")
    assert not search.won()


def test_child_prefix_can_finish_before_pull_and_adult_item_returns_after_gate():
    search = Search(age_world(child_key=True))
    spheres = search.collect_spheres(PLACEMENTS)
    assert search.can_reach("Child Ledge", CHILD)
    assert search.holds("Forest Clear")
    assert search.counts["Key"] == 1
    assert search.counts["Hookshot"] == 1
    assert search.won()
    assert sum(spheres, []).count("Adult Item") == 1
    assert sum(spheres, []).count("Child Prize") == 1


def test_adult_start_has_no_child_prefix_before_return():
    world = age_world(child_key=True, adult_start=True)
    search = Search(world)
    search.collect_spheres(PLACEMENTS)
    assert search.can_reach("Field", ADULT)
    assert not search.can_access(world.locations["Child Key"], CHILD)
    assert not search.won()


def test_adult_events_do_not_leak_into_child_here_subrules():
    world = age_world()
    location = world.locations["Child Key"]
    world.locations["Child Key"] = replace(
        location,
        rule=Rule("child and adult knowledge", lambda c, a, t: a == CHILD and c.get("Adult Knowledge", 0) > 0),
    )
    event = Event("Adult Knowledge", "Field", Rule("adult", lambda c, a, t: a == ADULT), "synthetic")
    world.events.append(event)
    search = Search(world)
    search.collect_spheres(PLACEMENTS)
    assert search.holds("Adult Knowledge")
    assert "Child Key" not in search.collected
    assert not search.won()


def test_return_needs_the_adult_pedestal_not_only_forest_clear():
    world = age_world(child_key=True)
    world.regions["Field"].exits[0] = replace(
        world.regions["Field"].exits[0], rule=Rule("child only", lambda c, a, t: a == CHILD)
    )
    search = Search(world)
    search.collect_spheres(PLACEMENTS)
    assert search.holds("Forest Clear")
    assert not search.can_reach("Temple", ADULT)
    assert not search.won()


def test_already_collected_adult_check_can_join_child_prefix_without_double_grant():
    world = age_world(child_key=True)
    world.settings["age_return_event"] = "Unfinished"
    location = world.locations["Adult Item"]
    world.locations["Adult Item"] = replace(
        location,
        rule=Rule("adult or Key", lambda c, a, t: a == ADULT or c.get("Key", 0) > 0, frozenset({"Key"})),
    )
    search = Search(world)
    spheres = search.collect_spheres(PLACEMENTS)
    assert search.can_reach("Child Ledge", CHILD)
    assert search.counts["Hookshot"] == 1
    assert sum(spheres, []).count("Adult Item") == 1
    assert search.collect_spheres(PLACEMENTS) == []
    assert search.counts["Hookshot"] == 1


def test_adult_item_alias_cannot_open_child_checks_before_return():
    world = age_world()
    world.items["Hookshot"] = Item("Hookshot", alias=("Key", 2))
    world.settings["age_return_event"] = "Unfinished"
    location = world.locations["Child Key"]
    world.locations["Child Key"] = replace(
        location,
        rule=Rule("child needs two Keys", lambda c, a, t: a == CHILD and c.get("Key", 0) >= 2, frozenset({"Key"})),
    )
    search = Search(world)
    search.collect_spheres(PLACEMENTS)
    assert search.counts["Key"] == 2
    assert "Child Key" not in search.collected
    assert not search.won()


def test_external_assumed_items_are_usable_in_the_child_prefix():
    search = Search(age_world(), ["Hookshot"])
    search.collect_spheres(PLACEMENTS)
    assert search.won()


def test_beatable_seed_can_still_softlock_on_an_early_pull():
    # Child Key is optional before the pedestal. The solver can choose to get it, but a player can skip it.
    planned = Search(age_world(child_key=True))
    planned.collect_spheres(PLACEMENTS)
    assert planned.won()

    pulled_early = Search(age_world(child_key=True, adult_start=True))
    pulled_early.collect_spheres(PLACEMENTS)
    assert pulled_early.counts["Hookshot"] == 1
    assert not pulled_early.holds("Forest Clear")
    assert not pulled_early.won()

    prepared = Search(age_world(child_key=True, adult_start=True), ["Key"])
    prepared.collect_spheres(PLACEMENTS)
    assert prepared.holds("Forest Clear")
    assert prepared.won()


def guarantee(world):
    world.settings.update(age_return_guarantee=True, age_pull_event="Time Travel")
    return world


def test_default_guarantee_rejects_beatable_but_early_pull_unsafe_seed():
    world = guarantee(age_world(child_key=True))
    with pytest.raises(FillError, match="goal cannot be reached"):
        check_beatable(world, PLACEMENTS)
    world.settings["age_return_guarantee"] = False
    assert "Child Prize" in sum(check_beatable(world, PLACEMENTS), [])


def test_guarantee_accepts_adult_supply_and_mandatory_pull_inventory():
    adult_supply = guarantee(age_world(child_key=True))
    adult_supply.items["Hookshot"] = Item("Hookshot", alias=("Key", 1))
    assert "Child Prize" in sum(check_beatable(adult_supply, PLACEMENTS), [])

    mandatory = guarantee(age_world(child_key=True))
    index = next(i for i, event in enumerate(mandatory.events) if event.name == "Time Travel")
    mandatory.events[index] = replace(
        mandatory.events[index], rule=Rule("Key", lambda c, a, t: c.get("Key", 0) > 0, frozenset({"Key"}))
    )
    assert "Child Prize" in sum(check_beatable(mandatory, PLACEMENTS), [])


def test_child_only_goal_does_not_need_an_unreachable_return_pedestal():
    world = guarantee(age_world(child_key=True))
    world.events = [event for event in world.events if event.name != "Time Travel"]
    world.goal = Rule("child Key", lambda c, a, t: c.get("Key", 0) > 0, frozenset({"Key"}))
    assert "Child Key" in sum(check_beatable(world, PLACEMENTS), [])


def test_mandatory_counts_include_child_prerequisites_not_just_the_pedestal():
    world = guarantee(age_world(child_key=True))
    # The pedestal itself needs only Prize, but obtaining Prize as child needs two Keys.
    key = world.locations["Child Key"]
    world.locations["Child Key"] = replace(
        key, rule=Rule("two Keys", lambda c, a, t: a == CHILD and c.get("Key", 0) >= 2, frozenset({"Key"}))
    )
    world.locations["Child Supply"] = replace(key, name="Child Supply")
    world.items["Bundle"] = Item("Bundle", alias=("Key", 2))
    index = next(i for i, event in enumerate(world.events) if event.name == "Time Travel")
    world.events[index] = replace(
        world.events[index], rule=Rule("Prize", lambda c, a, t: c.get("Prize", 0) > 0, frozenset({"Prize"}))
    )
    placements = {"Child Supply": "Bundle", "Child Key": "Prize", "Adult Item": "Hookshot"}
    search = Search(world)
    search.collect_spheres(placements)
    mandatory = search.mandatory_pull_inventory(placements)
    assert mandatory["Key"] == 2
    assert mandatory["Prize"] == 1
    assert "Hookshot" not in mandatory
    assert search.return_safe(placements)
