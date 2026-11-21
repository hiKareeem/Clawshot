"""Vanilla rows (spec tracker-in-logic D19, section 8): fixed vanilla pick-ups the seed does not shuffle, on a tiny
synthetic world. Nothing comes from the game."""

import copy
import json

import pytest
from test_tracker_logic import GENERATOR, PLACES
from test_tracker_state import build_save, parse

from clawshot.generate import Settings
from clawshot.tracker import TrackerSession, build_state, load_seed, seeds
from clawshot.tracker import logic as tracker_logic
from clawshot.tracker.seeds import Place

BOOMERANG = "PouchData.Item_Boomerang.StockNum"

# test_tracker_logic's world plus fixed pick-ups: the child's Boomerang (which opens the Child Ledge, like Ruto's
# Letter opens Jabu-Jabu), two Lens pick-ups (an item given twice) and a non-progression trinket.
SPEC = copy.deepcopy(__import__("test_tracker_logic").SPEC)
SPEC["items"] |= {"Lens of Truth": {}, "Trinket": {"class": "normal"}}
SPEC["regions"][1]["locations"] |= {
    "Boomerang Pickup": {"rule": "age == 'child'", "type": "NPC", "vanilla": "Boomerang"},
    "Lens Pickup A": {"rule": "True", "type": "NPC", "vanilla": "Lens of Truth"},
    "Lens Pickup B": {"rule": "True", "type": "NPC", "vanilla": "Lens of Truth"},
    "Trinket Pickup": {"rule": "True", "type": "NPC", "vanilla": "Trinket"},
}
# The Boomerang is not shuffled: only its vanilla pick-up gives it.
PLACEMENTS = {
    "Adult Chest": "Key",
    "Child Chest": "Hookshot",
    "Boomerang Chest": "Rupees (5)",
    "Ledge Chest": "Rupees (5)",
}
VANILLA_PLACES = PLACES | {"Boomerang Pickup": Place("Lake", None, "NPC")}


@pytest.fixture
def world(monkeypatch):
    monkeypatch.setattr(seeds, "location_index", lambda: VANILLA_PLACES)
    monkeypatch.setattr(tracker_logic, "world_spec", lambda: SPEC)
    return SPEC


def write_seed(tmp_path, placements=PLACEMENTS, *, generator=GENERATOR, name="seed-1"):
    root = tmp_path / name
    (root / "seed").mkdir(parents=True)
    spoiler = {
        "generator": generator,
        "seed": 1,
        "settings_string": Settings().to_string(),
        "settings": {"shuffle": ["Chest"]},
        "placements": placements,
        "locations": {
            name: {"name": name, "where": "Field", "ids": [str(100 + i)]} for i, name in enumerate(placements)
        },
    }
    (root / "seed" / "spoiler.json").write_text(json.dumps(spoiler), encoding="utf-8")
    (root / "clawshot-seed.json").write_text(json.dumps({"seed": 1, "output_sha256": "ef" * 32}), encoding="utf-8")
    return root


def state_for(tmp_path, ints=None, *, placements=PLACEMENTS, marks=frozenset(), name="seed-1", logic=None):
    seed = load_seed(write_seed(tmp_path, placements, name=name))
    logic = logic or tracker_logic.SeedLogic(tracker_logic.load_world(seed))
    return build_state(seed, parse({}, ints or {}), logic=logic, marks=marks), seed, logic


def shuffled(state):
    return {check["id"]: check for area in state["areas"] for check in area["checks"]}


def vanilla(state):
    return {check["id"]: check for area in state["vanilla_areas"] for check in area["checks"]}


# 16.2 (8.1)
def test_rows_are_unshuffled_unique_progression_pick_ups(tmp_path, world):
    state, seed, logic = state_for(tmp_path, {BOOMERANG: 0})
    assert list(vanilla(state)) == ["Boomerang Pickup"]
    every = tracker_logic.vanilla_rows(seed, logic.loaded.world, "all")
    assert [row.location for row in every] == ["Boomerang Pickup", "Lens Pickup A", "Lens Pickup B"]
    with pytest.raises(ValueError, match="scope"):
        tracker_logic.vanilla_rows(seed, logic.loaded.world, "some")


def test_rows_are_built_once_per_loaded_seed(tmp_path, world, monkeypatch):
    calls = []
    real = tracker_logic.vanilla_rows
    monkeypatch.setattr(tracker_logic, "vanilla_rows", lambda *a: calls.append(1) or real(*a))
    _, seed, logic = state_for(tmp_path, {BOOMERANG: 0})
    for held in (0, 1, 0):
        build_state(seed, parse({}, {BOOMERANG: held}), logic=logic)
    assert len(calls) == 1


def test_no_rows_while_logic_is_unavailable(tmp_path, world):
    seed = load_seed(write_seed(tmp_path, generator="clawshot 0.0.0"))
    logic = tracker_logic.SeedLogic(tracker_logic.load_world(seed))
    state = build_state(seed, parse({}, {BOOMERANG: 0}), logic=logic)
    assert state["logic"]["available"] is False and "vanilla_areas" not in state


# 16.3 (8.2)
def test_a_row_names_its_place_and_item_without_spoilers(tmp_path, world):
    state, _, _ = state_for(tmp_path, {BOOMERANG: 0})
    assert state["show_locations"] is False
    row = vanilla(state)["Boomerang Pickup"]
    assert row | {"in_logic": None} == {
        "id": "Boomerang Pickup",
        "label": "Boomerang Pickup",
        "where": "",
        "kind": "vanilla",
        "dungeon": None,
        "collected": False,
        "basis": "inventory",
        "vanilla": True,
        "item": "Boomerang",
        "item_label": "Boomerang",
        "in_logic": None,
    }
    assert [area["name"] for area in state["vanilla_areas"]] == ["Lake"]


# 16.4, 16.6 (8.3, 8.4): the gate is open and in logic, the gated check out; holding the item flips both.
def test_a_fixed_gate_item_shows_open_then_collected(tmp_path, world):
    before, _, _ = state_for(tmp_path, {BOOMERANG: 0})
    row = vanilla(before)["Boomerang Pickup"]
    assert row["collected"] is False
    assert row["in_logic"] == {"child": True, "adult": False, "either": True}
    assert shuffled(before)["Ledge Chest"]["in_logic"]["child"] is False
    assert before["vanilla_areas"][0]["in_logic"] == {"child": 1, "adult": 0, "either": 1}

    after, _, _ = state_for(tmp_path, {BOOMERANG: 1}, name="held")
    row = vanilla(after)["Boomerang Pickup"]
    assert row["collected"] is True and "in_logic" not in row
    assert shuffled(after)["Ledge Chest"]["in_logic"]["child"] is True
    assert after["vanilla_areas"][0]["collected"] == 1


def test_an_unreadable_item_is_unknown_with_a_reason(tmp_path, world):
    state, _, _ = state_for(tmp_path)  # no Boomerang stock in the save
    row = vanilla(state)["Boomerang Pickup"]
    assert row["collected"] is None and row["basis"] is None and "could not be read" in row["reason"]
    assert "in_logic" in row  # unknown and unmarked is open (3.1)


def test_an_item_a_shuffled_check_can_give_is_unknown(tmp_path, world):
    placements = PLACEMENTS | {"Boomerang Chest": "Boomerang"}
    state, _, _ = state_for(tmp_path, {BOOMERANG: 1}, placements=placements)
    row = vanilla(state)["Boomerang Pickup"]
    assert row["collected"] is None and "shuffled check" in row["reason"]


def test_a_fixed_tier_counts_its_chain(tmp_path, world):
    inv = tracker_logic.Inventory({"Progressive Scale": 1}, ())
    golden = tracker_logic.VanillaRow("Fishing", "Fishing", "", "Lake", None, "Golden Scale", "Golden Scale", False)
    from types import SimpleNamespace

    from clawshot.world.model import Item

    # vanilla_collected reads only the world's item table.
    fake = SimpleNamespace(items={"Golden Scale": Item("Golden Scale", alias=("Progressive Scale", 2), tier=True)})
    assert tracker_logic.vanilla_collected(golden, inv, fake) == (False, None)
    two = tracker_logic.Inventory({"Progressive Scale": 2}, ())
    assert tracker_logic.vanilla_collected(golden, two, fake) == (True, None)


# 16.5 (8.3): unknown rows take manual marks like any unknown check, and a save-confirmed state drops the mark.
@pytest.fixture
def marks_folder(tmp_path, monkeypatch):
    from clawshot.app import preferences

    prefs = tmp_path / "prefs"
    monkeypatch.setattr(preferences, "user_preferences_path", lambda: prefs / "paths.json")
    return prefs


def test_unknown_rows_can_be_marked_and_known_rows_cannot(tmp_path, world, marks_folder):
    root = write_seed(tmp_path)
    progress = root / "user" / "save" / "1" / "slot_00" / "progress.sav"
    progress.parent.mkdir(parents=True)
    progress.write_bytes(build_save({}))  # no Boomerang stock: the row is unknown
    session = TrackerSession()
    session.configure(root)
    session.mark("Boomerang Pickup", True)
    row = vanilla(session.snapshot()["state"])["Boomerang Pickup"]
    assert row["marked"] is True and "in_logic" not in row
    assert session.snapshot()["state"]["vanilla_areas"][0]["marked"] == 1

    progress.write_bytes(build_save({}, {BOOMERANG: 1}))
    import os

    stat = progress.stat()
    os.utime(progress, ns=(stat.st_atime_ns, stat.st_mtime_ns + 10**9))
    row = vanilla(session.snapshot()["state"])["Boomerang Pickup"]
    assert row["collected"] is True and "marked" not in row
    with pytest.raises(ValueError, match="already says"):
        session.mark("Boomerang Pickup", True)


# 16.7 (8.5): the seed's own checks and area counts are the same with and without vanilla rows.
def test_shuffled_checks_and_area_counts_are_unchanged(tmp_path, world, monkeypatch):
    with_rows, _, _ = state_for(tmp_path, {BOOMERANG: 0})
    monkeypatch.setattr(tracker_logic, "vanilla_rows", lambda *a: ())
    without, _, _ = state_for(tmp_path, {BOOMERANG: 0}, name="without")
    assert without["vanilla_areas"] == [] and with_rows["vanilla_areas"]
    assert with_rows["areas"] == without["areas"]
    assert with_rows["skulltula_checks"] == without["skulltula_checks"]


# 16.9 (8.7)
def test_obs_payload_has_no_vanilla_rows(tmp_path, world, marks_folder):
    from clawshot.ui.tracker import TrackerController

    root = write_seed(tmp_path)
    progress = root / "user" / "save" / "1" / "slot_00" / "progress.sav"
    progress.parent.mkdir(parents=True)
    progress.write_bytes(build_save({}, {BOOMERANG: 0}))
    controller = TrackerController()
    controller.session = TrackerSession()
    controller.session.configure(root)
    assert controller.snapshot()["state"]["vanilla_areas"]
    obs = controller.snapshot(obs=True)
    assert "vanilla_areas" not in obs["state"] and "Boomerang Pickup" not in json.dumps(obs)


# 16.10 (P14.a)
def test_same_seed_and_save_give_equal_json(tmp_path, world):
    first, _, _ = state_for(tmp_path, {BOOMERANG: 0})
    second, _, _ = state_for(tmp_path, {BOOMERANG: 0}, name="again")
    for state in (first, second):
        state["seed"].pop("root"), state["seed"].pop("seed_dir")
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
