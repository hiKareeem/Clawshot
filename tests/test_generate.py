"""The fill and the beatability search on synthetic worlds: beatable and unbeatable worlds, key doors, an
adult-only item, 200 seeds, and byte-identical spoilers."""

import json

import pytest

from clawshot.generate import FillError, Settings, generate, spoiler_json
from clawshot.generate.fill import check_beatable
from clawshot.world import build_world

HELPERS = {
    "is_child": "age == 'child'",
    "is_adult": "age == 'adult'",
    "is_starting_age": "age == starting_age",
}
ITEMS = {
    "Time Travel": {"type": "Event"},
    "Sword": {},
    "Slingshot": {},
    "Hookshot": {},
    "Bow": {},
    "Small Key (Temple)": {"type": "SmallKey"},
    "Boss Key (Temple)": {"type": "BossKey"},
    "Map (Temple)": {"type": "Map", "class": "priority"},
    "Rupees (5)": {"class": "normal"},
    "Recovery Heart": {"class": "normal"},
}


def chest(vanilla: str, rule: str = "True") -> dict:
    return {"rule": rule, "type": "Chest", "vanilla": vanilla}


def dungeon_world() -> dict:
    """Child starts in a village; the Sword opens the Temple of Time (adult) and a dungeon with two key doors and
    a boss door. The boss needs the Bow, which waits behind an adult-only ledge. Every chest is shuffled."""
    return {
        "start": "Root",
        "goal": "'Beat Boss'",
        "items": ITEMS,
        "helpers": HELPERS,
        "settings": {"starting_age": "child"},
        "regions": [
            {"name": "Root", "exits": {"Village": "is_starting_age or Time_Travel"}},
            {
                "name": "Village",
                "locations": {
                    "Village Chest": chest("Sword"),
                    "Village Ledge": chest("Rupees (5)", "Slingshot"),
                    "Village Roof": chest("Bow", "is_adult and Hookshot"),
                },
                "exits": {"Temple of Time": "Sword", "Dungeon Hall": "Sword"},
            },
            {"name": "Temple of Time", "events": {"Time Travel": "True"}},
            {
                "name": "Dungeon Hall",
                "dungeon": "Temple",
                "locations": {
                    "Hall Chest": chest("Small Key (Temple)"),
                    "Hall Side Chest": chest("Slingshot"),
                    "Hall High Chest": chest("Recovery Heart", "Slingshot"),
                },
                "exits": {"Dungeon Middle": "(Small_Key_Temple, 1)"},
            },
            {
                "name": "Dungeon Middle",
                "dungeon": "Temple",
                "locations": {"Middle Chest": chest("Small Key (Temple)"), "Middle Map Chest": chest("Map (Temple)")},
                "exits": {"Dungeon Deep": "(Small_Key_Temple, 2)"},
            },
            {
                "name": "Dungeon Deep",
                "dungeon": "Temple",
                "locations": {
                    "Deep Chest": chest("Boss Key (Temple)"),
                    "Deep Hook Chest": chest("Hookshot", "is_adult"),
                },
                "exits": {"Boss Room": "Boss_Key_Temple"},
            },
            {"name": "Boss Room", "events": {"Beat Boss": "Bow"}, "locations": {"Boss Prize": chest("Rupees (5)")}},
        ],
    }


def test_vanilla_placement_is_beatable():
    world = build_world(dungeon_world())
    placements = {name: loc.vanilla for name, loc in world.locations.items()}
    spheres = check_beatable(world, placements)
    assert spheres == [
        ["Village Chest"],
        ["Hall Chest", "Hall Side Chest"],
        ["Village Ledge", "Hall High Chest", "Middle Chest", "Middle Map Chest"],
        ["Deep Chest", "Deep Hook Chest"],
        ["Village Roof", "Boss Prize"],  # adult with the Hookshot; the boss key opens the boss room
    ]


def test_every_seed_of_200_is_beatable_with_keys_in_their_dungeon():
    spec = dungeon_world()
    world = build_world(spec)
    dungeon_items = {"Small Key (Temple)", "Boss Key (Temple)", "Map (Temple)"}
    for seed_number in range(200):
        seed = generate(spec, seed_number, Settings())
        check_beatable(world, seed.placements)  # the oracle, again, on a fresh search
        for location, item in seed.placements.items():
            if item in dungeon_items:
                assert world.regions[world.locations[location].region].dungeon == "Temple", (seed_number, location)
        # keys are never behind the doors they open: one key at most behind the first door, none behind the second
        keys = [loc for loc, item in seed.placements.items() if item == "Small Key (Temple)"]
        regions = [world.locations[loc].region for loc in keys]
        assert regions.count("Dungeon Middle") <= 1 and "Dungeon Deep" not in regions, (seed_number, keys)


def test_dungeon_items_anywhere_leave_the_dungeon_sometimes():
    spec = dungeon_world()
    world = build_world(spec)
    outside = 0
    for seed_number in range(50):
        seed = generate(spec, seed_number, Settings(dungeon_items="anywhere"))
        outside += sum(
            1
            for location, item in seed.placements.items()
            if item.startswith("Small Key") and world.regions[world.locations[location].region].dungeon is None
        )
    assert outside > 0


def test_item_reachable_only_as_adult_comes_after_time_travel():
    # The roof needs the Hookshot as adult. Whatever lands there is collected only after the Hookshot's sphere.
    spec = dungeon_world()
    on_roof = 0
    for seed_number in range(50):
        seed = generate(spec, seed_number, Settings())
        sphere_of = {loc: i for i, sphere in enumerate(seed.spheres) for loc in sphere}
        hookshot = next(loc for loc, item in seed.placements.items() if item == "Hookshot")
        assert sphere_of["Village Roof"] > sphere_of[hookshot] > sphere_of["Village Chest"]
        on_roof += seed.world.items[seed.placements["Village Roof"]].progression
    assert on_roof > 0  # some seeds do put a progression item on the roof


def test_goal_needing_an_item_nobody_holds_raises():
    spec = dungeon_world()
    spec["regions"][1]["locations"]["Village Roof"] = chest("Rupees (5)", "is_adult and Hookshot")  # no Bow left
    with pytest.raises(FillError, match="goal cannot be reached"):
        generate(spec, 1, Settings())


def test_item_locked_behind_itself_raises():
    spec = dungeon_world()
    del spec["regions"][1]["locations"]["Village Chest"]  # the only chest open without the Sword
    spec["regions"][3]["locations"]["Hall Sword Chest"] = chest("Sword")
    with pytest.raises(FillError, match="no beatable fill in 10 attempts; last: no reachable location"):
        generate(spec, 1, Settings())


def test_same_seed_same_bytes():
    spec = dungeon_world()
    first = spoiler_json(generate(spec, 7, Settings()))
    assert spoiler_json(generate(spec, 7, Settings())) == first
    log = json.loads(first)
    assert log["seed"] == 7
    assert log["settings"] == {"shuffle": ["Chest"], "dungeon_items": "own_dungeon", "logic": {}}
    assert list(log["placements"]) == list(build_world(spec).locations)
    assert list(log["spheres"][0]) == ["Village Chest"]  # the only chest open at the start
    assert len({spoiler_json(generate(spec, n, Settings())) for n in range(8)}) > 1  # seeds do differ
