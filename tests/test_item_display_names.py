"""Players read the remake's item names; the logic's names stay the keys of every placement, rule and hint target."""

import json
from dataclasses import replace

from clawshot.generate import Settings, generate, play_note, spoiler, spoiler_json
from clawshot.generate.hints import Hint
from clawshot.generate.names import item_names
from clawshot.patch import items as item_actors
from clawshot.world import load_spec

# Logic item -> what the remake calls it (read from Kareem's dump, 2026-11-10). Coin is no remake item: it keeps
# its own name.
SHOWN = {"Stone of Agony": "Echo Gem", "Bow": "Fairy Bow", "Bottle with Milk": "Lon Lon Milk", "Coin": "Coin"}
# A synthetic stand-in for a name clawshot.patch.text.item_names reads from the game's own text.
GAME_TEXT = {"Stone of Agony": "Gem named by game text"}


def remake_seed():
    """Four chests a child reaches at once, shuffled by the real fill: the Bow among them is an age-locked pickup."""
    chests = {f"Chest {index}": item for index, item in enumerate(SHOWN, 1)}
    spec = {
        "start": "Root",
        "goal": "Bow",
        "settings": {"starting_age": "child"},
        "items": {item: {} for item in SHOWN},
        "locations": {name: {"type": "Chest", "vanilla": item} for name, item in chests.items()},
        "regions": [
            {"name": "Root", "exits": {"Field": "age == starting_age or 'Time Travel'"}},
            {"name": "Field", "locations": {name: "True" for name in chests}},
        ],
    }
    return generate(spec, 7, Settings(shuffle=("Chest",)))


def table_rows(note):
    return [
        line.removeprefix("| ").removesuffix(" |").split(" | ") for line in note.splitlines() if line.startswith("| ")
    ]


def test_every_display_name_is_for_an_item_the_logic_and_the_game_both_have():
    logic = load_spec()["items"]
    actors = item_actors.load().actors
    for item, shown in item_names().items():
        assert item in logic and item in actors, item  # read from the item's actor text, keyed by its logic name
        assert shown.strip() and shown != item, item


def test_spoiler_keeps_logic_names_and_shows_the_remake_names_beside_them():
    seed = remake_seed()
    log = json.loads(spoiler_json(seed))
    assert log["placements"] == {name: seed.placements[name] for name in seed.shuffled}
    assert sorted(log["placements"].values()) == sorted(SHOWN)
    assert {item for sphere in log["spheres"] for item in sphere.values()} <= set(SHOWN)
    assert [pickup["item"] for pickup in log["age_locked_pickups"]] == ["Bow"]
    assert log["item_names"] == {"Bottle with Milk": "Lon Lon Milk", "Bow": "Fairy Bow", "Stone of Agony": "Echo Gem"}


def test_play_note_names_every_item_as_the_remake_does():
    seed = remake_seed()
    note = play_note(seed)
    rows = table_rows(note)
    rewards = {row[3]: row[4] for row in rows if len(row) == 5 and row[3] in seed.shuffled}
    assert rewards == {name: SHOWN[seed.placements[name]] for name in seed.shuffled}
    [warning] = [row for row in rows if row[1:3] == ["adult", "child"]]
    assert warning[0] == "Fairy Bow"
    assert "Stone of Agony" not in note and "Bottle with Milk" not in note
    assert "Bow" not in {cell for row in rows for cell in row}


def test_hints_word_items_by_the_remake_name_and_the_games_own_text_wins():
    seed = remake_seed()
    gem = next(name for name in seed.shuffled if seed.placements[name] == "Stone of Agony")
    coin = next(name for name in seed.shuffled if seed.placements[name] == "Coin")
    seed = replace(
        seed,
        hints=(
            Hint("KF Gossip Stone", "GOSSIP_KOKIRI_FOREST_01", "random", location=gem, item="Stone of Agony"),
            Hint("DMT Gossip Stone", "GOSSIP_DEATH_MOUNTAIN_01", "random", location=coin, item="Coin"),
        ),
    )
    hints = spoiler(seed)["hints"]
    assert [(hint["location"], hint["item"]) for hint in hints] == [(gem, "Stone of Agony"), (coin, "Coin")]
    assert "Echo Gem" in hints[0]["text"] and "Stone of Agony" not in hints[0]["text"]
    assert "Coin" in hints[1]["text"]

    log = spoiler(seed, GAME_TEXT)
    assert log["hints"][0]["item"] == "Stone of Agony"
    assert GAME_TEXT["Stone of Agony"] in log["hints"][0]["text"]
    assert log["item_names"]["Stone of Agony"] == GAME_TEXT["Stone of Agony"]
    assert log["item_names"]["Bow"] == "Fairy Bow"  # the game's text covers hinted items; the rest keep the table
    rows = table_rows(play_note(seed, log))
    rewards = {row[3]: row[4] for row in rows if len(row) == 5 and row[3] in seed.shuffled}
    assert rewards[gem] == GAME_TEXT["Stone of Agony"]
    stone = next(row for row in rows if row[0] == "KF Gossip Stone")
    assert stone[4] == f"{gem} — {GAME_TEXT['Stone of Agony']}"


def test_opening_rewards_and_requirements_use_display_names_without_renaming_the_proof():
    placements = {"Outside reward": "Stone of Agony", "Inside reward": "Lens of Truth"}
    spec = {
        "start": "Village",
        "goal": "'Defeat Queen Gohma'",
        "items": {item: {} for item in placements.values()},
        "locations": {name: {"type": "Chest", "vanilla": item} for name, item in placements.items()},
        "regions": [
            {
                "name": "Village",
                "locations": {"Outside reward": "True"},
                "exits": {"Deku Tree Lobby": "'Stone of Agony'"},
            },
            {
                "name": "Deku Tree Lobby",
                "dungeon": "Deku Tree",
                "locations": {"Inside reward": "True"},
                "events": {"Defeat Queen Gohma": "'Lens of Truth'"},
            },
        ],
    }
    seed = generate(spec, 7, Settings(shuffle=()))
    log = spoiler(seed)
    steps = log["opening_route"]["steps"]
    assert {step["location"]: step["item"] for step in steps if step["kind"] == "collect"} == placements
    inside = next(step for step in steps if step["location"] == "Inside reward")
    assert inside["requires"] == [{"item": "Stone of Agony", "count": 1, "sources": ["Outside reward"]}]
    note = play_note(seed, log)
    rows = [row for row in table_rows(note) if len(row) == 6]
    assert {row[3] for row in rows if row[1] == "Collect"} == {"Echo Gem", "Lenses of Truth"}
    assert any("Echo Gem (step " in row[4] for row in rows if "Inside reward" in row[2])
    assert any("Lenses of Truth (step " in row[4] for row in rows if row[1] == "Complete")
    assert "Stone of Agony" not in note and "Lens of Truth" not in note
    assert seed.placements == placements
