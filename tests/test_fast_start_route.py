"""Round 13: an early Door of Time with an open forest bridge is a valid adult-first seed, not a write crash.

A player's Recommended seed with the bridge open (forest closed_deku) and an early door generated, then failed in
"Write and verify" with ``ValueError: no child opening witness reaches 'Defeat Queen Gohma'``: its fill put the
Kokiri Sword where only items found by adult Link reach, which the beatability search allows. The spoiler now
explains the missing child guide instead. The current return-kit construction cannot fill Chest-only early doors
under its configured first-pull bound; validation explains that generator limitation, not physical impossibility.
"""

import json

import pytest

from clawshot.app.schema import presets, validate
from clawshot.generate import FillError, Settings, generate, play_note, spoiler
from clawshot.generate.route import NoChildOpening, OpeningRoute, opening
from clawshot.patch import door, gifts, make_seed, write_seed
from clawshot.world.load import load_spec

GOHMA = "'Defeat Queen Gohma'"
SLICE = ("KokiriForest", "LostWood", "InsideTheDekuTree")


def early_door_world():
    """Mido wants Sword and Shield; adult Link reaches one chest from the start (an early door, no return gate)."""
    return {
        "start": "Village",
        "goal": GOHMA,
        "items": {"Sword": {}, "Shield": {}, "Coin": {"class": "normal"}},
        "locations": {
            "Village Chest": {"type": "Chest", "vanilla": "Sword"},
            "House Chest": {"type": "Chest", "vanilla": "Shield"},
            "Shop Chest": {"type": "Chest", "vanilla": "Coin"},
            "Well Chest": {"type": "Chest", "vanilla": "Coin"},
            "Adult Chest": {"type": "Chest", "vanilla": "Coin"},
        },
        "regions": [
            {
                "name": "Village",
                "locations": {
                    "Village Chest": "True",
                    "House Chest": "True",
                    "Shop Chest": "True",
                    "Well Chest": "True",
                },
                "exits": {"Deku Tree Lobby": "Sword and Shield", "Temple": "age == 'adult'"},
            },
            {"name": "Temple", "locations": {"Adult Chest": "True"}},
            {"name": "Deku Tree Lobby", "dungeon": "Deku Tree", "events": {"Defeat Queen Gohma": "True"}},
        ],
    }


def test_adult_first_fills_explain_the_missing_child_guide_and_child_fills_keep_their_route():
    kinds = set()
    for number in range(12):
        seed = generate(early_door_world(), number, Settings(shuffle=("Chest",)))
        route = opening(seed)
        log = json.loads(json.dumps(spoiler(seed)))  # the written spoiler round-trips
        note = play_note(seed, log)
        adult_first = seed.placements["Adult Chest"] != "Coin"
        if adult_first:
            assert isinstance(route, NoChildOpening), number
            assert log["opening_route"] is None
            reason = log["opening_route_unavailable"]["reason"]
            assert "adult Link's help" in reason and "after collection sphere" in reason
            assert reason in note and "| Step | Action |" not in note
        else:
            assert isinstance(route, OpeningRoute), number
            assert log["opening_route_unavailable"] is None
            collected = {step["location"] for step in log["opening_route"]["steps"] if step["kind"] == "collect"}
            assert collected == {name for name, item in seed.placements.items() if item in ("Sword", "Shield")}
            assert "Adult Chest" not in collected
            assert "| Step | Action |" in note
        kinds.add(adult_first)
    assert kinds == {True, False}  # both fills occur among these seeds: the test covers the consumer's case


def test_an_opening_the_search_never_reaches_is_explained_not_raised():
    spec = early_door_world()
    spec["goal"] = "Sword"
    spec["items"]["Lens"] = {}
    spec["regions"][2]["events"]["Defeat Queen Gohma"] = "Lens"  # no check gives the Lens
    seed = generate(spec, 7, Settings(shuffle=()))
    route = opening(seed)
    assert isinstance(route, NoChildOpening)
    assert "never reaches" in route.reason
    assert spoiler(seed)["opening_route_unavailable"]["reason"] == route.reason


@pytest.mark.parametrize("mode", ["song_only", "open"])
def test_chest_only_early_door_is_refused_at_validation_with_the_return_conflict(mode):
    with pytest.raises(ValueError) as refused:
        validate({"door_of_time": mode})  # the UI refuses before any dump is read
    message = str(refused.value)
    for part in (
        f"door_of_time = {mode!r}",
        "age_return_guarantee",
        "Sarias Song",
        "Ocarina",
        "Saria in the Sacred Grove",
        "Saria's Farewell Gift",
        "Ocarina in the Castle Moat",
        "door_of_time = 'closed'",
    ):
        assert part in message, part
    with pytest.raises(FillError, match="age_return_guarantee"):
        generate(load_spec(), 1, Settings(door_of_time=mode))


@pytest.mark.parametrize("mode", door.MODES)
def test_early_doors_stay_offered_where_the_return_can_be_kept(mode):
    recommended = next(preset for preset in presets() if preset["id"] == "recommended")
    for forest in ("closed", "closed_deku", "open"):
        values = {**recommended["values"], "forest": forest, "door_of_time": mode}
        assert validate(values).door_of_time == mode  # Gift is decided after its seed setup


RECOMMENDED_BRIDGE_OPEN_EARLY_DOOR = 1
"""Round 13 baseline: Recommended, forest closed_deku, door open, seed 1 put the Kokiri Sword in KF Storms Grotto
Chest (sphere 12, after the return to child) and failed at write with the opening-witness ValueError."""


@pytest.mark.dump
def test_recommended_bridge_open_early_door_seed_writes_and_explains_its_opening(romfs, tmp_path):
    recommended = next(preset for preset in presets() if preset["id"] == "recommended")
    settings = validate({**recommended["values"], "forest": "closed_deku", "door_of_time": "open"})
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), settings)
    output = make_seed(romfs, RECOMMENDED_BRIDGE_OPEN_EARLY_DOOR, settings, spec, extra_steps=[step])
    write_seed(output, romfs, tmp_path / "seed")
    log = json.loads((tmp_path / "seed" / "spoiler.json").read_text(encoding="utf-8"))
    assert log["opening_route"] is None
    unavailable = log["opening_route_unavailable"]
    assert unavailable["event"] == "Defeat Queen Gohma" and "adult Link's help" in unavailable["reason"]
    assert unavailable["reason"] in (tmp_path / "seed" / "play-note.md").read_text(encoding="utf-8")


@pytest.mark.dump
def test_closed_forest_child_guide_still_needs_the_sword_and_a_shield(romfs):
    log = make_seed(romfs, 7, Settings(fast_start=("intro", "saria", "deku_tree"))).spoiler()
    assert log["opening_route_unavailable"] is None
    enter = next(step for step in log["opening_route"]["steps"] if step["kind"] == "enter")
    needed = {row["item"] for row in enter["requires"]}
    assert "Kokiri Sword" in needed and any("Shield" in item for item in needed), needed
