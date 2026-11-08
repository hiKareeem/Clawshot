"""The fill and the beatability search on synthetic worlds: beatable and unbeatable worlds, key doors, an
adult-only item, 200 seeds, and byte-identical spoilers."""

import json
import random

import pytest

from clawshot.generate import FillError, Settings, generate, spoiler_json
from clawshot.generate.fill import allowed, check_beatable, fill, shuffled_locations
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


def test_keep_vanilla_locations_are_not_shuffled():
    # A location held to its vanilla item (world Location.keep_vanilla, a reason) keeps it in every seed, and its
    # item is not in the pool: here the Bow on the adult-only roof, which the goal needs.
    world = build_world(dungeon_world())
    object.__setattr__(world.locations["Village Roof"], "keep_vanilla", "test: held to its vanilla item")
    assert "Village Roof" not in shuffled_locations(world, Settings())
    for seed_number in range(50):
        rng = random.Random(seed_number)
        for _ in range(10):  # a fill may fail and is retried, as generate() does
            try:
                placements = fill(world, Settings(), rng)
                break
            except FillError:
                continue
        else:
            pytest.fail(f"seed {seed_number}: no fill in 10 attempts")
        assert placements["Village Roof"] == "Bow"
        assert [loc for loc, item in placements.items() if item == "Bow"] == ["Village Roof"]
        check_beatable(world, placements)


def test_a_slice_keeps_only_its_areas_and_its_goal():
    spec = dungeon_world()
    for region in spec["regions"]:
        if region["name"] != "Root":
            region["area"] = "Village" if region["name"] == "Village" else "Elsewhere"
    spec["regions"][1]["locations"]["Village Ledge"] = chest("Rupees (5)")  # open, so Sword and Bow both fit
    settings = Settings(areas=("Village",), goal="Sword")
    seed = generate(spec, 3, settings)
    assert list(seed.world.regions) == ["Root", "Village"]  # the temple and the dungeon are cut away
    assert seed.shuffled == ["Village Chest", "Village Ledge", "Village Roof"]
    assert seed.placements["Village Roof"] == "Rupees (5)"  # the roof needs the adult, who never comes here
    log = json.loads(spoiler_json(seed))
    assert (log["settings"]["areas"], log["settings"]["goal"]) == (["Village"], "Sword")
    with pytest.raises(FillError, match="no region of the world lies in the areas"):
        generate(spec, 3, Settings(areas=("Nowhere",), goal="Sword"))


def test_dungeon_items_anywhere_turn_keysanity_on():
    # OoT Randomizer's rules give a free key while keys stay in their dungeon; with keys anywhere that must stop.
    spec = dungeon_world()
    spec["settings"] = {**spec["settings"], "keysanity": False}
    assert generate(spec, 1, Settings(dungeon_items="anywhere")).settings.logic == {"keysanity": True}
    assert generate(spec, 1, Settings()).settings.logic == {}
    with pytest.raises(FillError, match="needs the logic setting keysanity = true"):
        generate(spec, 1, Settings(dungeon_items="anywhere", logic={"keysanity": False}))


def test_items_held_to_location_types_go_only_there():
    # A song goes only to the song location, and the song location takes only the song (shuffle_song_items =
    # 'song'); a letter held to the gift locations goes to one of them, never to a chest.
    spec = dungeon_world()
    spec["items"] = ITEMS | {"Lullaby": {"type": "Song"}, "Letter": {"class": "normal"}}
    village = spec["regions"][1]["locations"]
    village["Village Song"] = {"rule": "True", "type": "Song", "vanilla": "Lullaby"}
    village["Village Gift"] = {"rule": "True", "type": "NPC", "vanilla": "Letter"}
    village["Village Other Gift"] = {"rule": "True", "type": "NPC", "vanilla": "Rupees (5)"}
    settings = Settings(
        shuffle=("Chest", "Song", "NPC"),
        item_location_types={"Lullaby": ("Song",), "Letter": ("NPC",)},
        exclusive_location_types=("Song",),
    )
    world = build_world(spec)
    assert not allowed(world, settings, "Village Chest", "Lullaby")
    assert not allowed(world, settings, "Village Song", "Sword")
    assert allowed(world, settings, "Village Gift", "Sword") and not allowed(world, settings, "Village Chest", "Letter")
    letters = set()
    for n in range(40):
        placements = generate(spec, n, settings).placements
        assert placements["Village Song"] == "Lullaby"
        letters |= {loc for loc, item in placements.items() if item == "Letter"}
    assert letters == {"Village Gift", "Village Other Gift"}
    assert Settings(item_location_types={"B": ("x",), "A": ("y",)}).as_dict()["item_location_types"] == {
        "A": ["y"],
        "B": ["x"],
    }
