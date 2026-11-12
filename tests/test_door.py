"""Synthetic door contracts and world/CS1 boundaries; no game trees or decoded data fixtures."""

from copy import deepcopy
from dataclasses import replace

import pytest

from clawshot.__main__ import main
from clawshot.formats import evfl
from clawshot.generate import FillError, Settings, prepare
from clawshot.patch import door, gifts
from clawshot.patch.plan import PatchError
from clawshot.world import ADULT, CHILD, load_spec

# An early door under the adult-return guarantee needs movable gifts and songs (fill.return_guarantee_conflict).
GIFTS = ("Chest", *gifts.GIFT_TYPES)


def run_open_flow(fc, state, *, recommended=True, quest_ready=False):
    """Evaluate the door's native state-changing actions; presentation calls have no inventory effect."""
    scenes, writes = [], []

    def run(index):
        while index != evfl.NONE:
            event = fc.events[index]
            params = getattr(event, "params", None) or {}
            if isinstance(event, evfl.SwitchEvent):
                actor = fc.actors[event.actor]
                query = actor.queries[event.query]
                if query == "EventQueryIsGameDataBool":
                    value = 0 if state.get(params["GameDataName"], False) else 1
                elif query == "EventQueryHavePlayedEvent":
                    value = 0 if state.get("HavePlayedEvent." + params["EventName"], False) else 1
                elif query == "EventQueryIsGameDataBoolExp":
                    value = 0 if quest_ready else 1
                elif query == "EventQueryIsRecommendedMelody":
                    value = 0 if recommended else 1
                else:
                    pytest.fail(f"unhandled door query {query}: {params}")
                index = dict(event.cases).get(value, evfl.NONE)
                continue
            if isinstance(event, evfl.ForkEvent):
                for fork in event.forks:
                    run(fork)
                index = event.join
                continue
            if isinstance(event, evfl.ActionEvent):
                action = fc.actors[event.actor].actions[event.action]
                if action == "EventTriggerSetGameDataBool":
                    state[params["GameDataName"]] = params["Value"]
                    writes.append(params["GameDataName"])
                elif action == "EventExecuteProgressChallengeStep":
                    state["Step_" + params["ChallengeName"]] = params["StepName"]
                    writes.append("Step_" + params["ChallengeName"])
                elif action == "EventTransition":
                    scenes.append(params["EventName"])
                elif "Pouch" in action or "AddOrRemove" in action:
                    pytest.fail(f"door unexpectedly grants inventory: {action} {params}")
            index = event.next

    run(fc.entry_point("DoorOfTime_OpenDoor").main_event)
    return scenes, writes


def synthetic_flow():
    return evfl.EventFlowFile(
        name="DoorOfTime",
        flowchart=evfl.Flowchart(
            "DoorOfTime",
            actors=[
                evfl.Actor(
                    "GameDataActor",
                    actions=["EventTriggerSetGameDataBool"],
                    queries=["EventQueryIsGameDataBoolExp", "EventQueryIsGameDataBool", "EventQueryHavePlayedEvent"],
                ),
                evfl.Actor("GameSystemActor", queries=["EventQueryIsRecommendedMelody"]),
                evfl.Actor(
                    "Presentation",
                    actions=["EventSoundRequestDucking", "EventTriggerCameraSavePoint", "EventTransition"],
                ),
                evfl.Actor("ChallengeSystemActor", actions=["EventExecuteProgressChallengeStep"]),
            ],
            events=[
                evfl.ActionEvent("Event18", 2, 1, 1),
                evfl.SubFlowEvent("Event27", "Dm_SY_Ocarina", "PlayOcarinaSequence", 2, {"MelodyType": 4}),
                evfl.ActionEvent("Event92", 2, 0, 3),
                evfl.SwitchEvent("Event60", 0, 0, [(0, 4)], {"GameDataName": "DoorOfTime_IsAfter_Step04_Exp"}),
                evfl.SwitchEvent("Event69", 0, 1, [(1, 5)], {"GameDataName": door.OPENED, "Index": -1}),
                evfl.SwitchEvent("Event58", 0, 2, [(1, 6)], {"EventName": "Dm_TimeTemple_0010"}),
                evfl.SwitchEvent("Event28", 1, 0, [(0, 7)]),
                evfl.ActionEvent("Scene", 2, 2, 8, {"EventName": "Dm_TimeTemple_0010"}),
                evfl.ActionEvent("SetOpened", 0, 0, 9, {"GameDataName": door.OPENED, "Value": True}),
                evfl.ActionEvent("SetStep", 3, 0, evfl.NONE, {"ChallengeName": "DoorOfTime", "StepName": "Step06"}),
                evfl.ActionEvent("OtherEntry", 2, 2, evfl.NONE, {"EventName": "OtherNativeScene"}),
            ],
            entry_points=[evfl.EntryPoint("DoorOfTime_OpenDoor", 0, [1]), evfl.EntryPoint("Other", 10)],
        ),
    )


@pytest.mark.parametrize(
    "learned,recommended,opened,played",
    [
        (True, True, False, False),
        (False, True, False, False),
        (True, False, False, False),
        (True, True, True, False),
        (True, True, False, True),
    ],
)
def test_song_only_opens_without_quests_but_retains_song_play_and_saved_once_gates(
    learned, recommended, opened, played
):
    original = synthetic_flow()
    patched = evfl.read(door.song_flow(evfl.write(original)))
    state = {door.TIME_SONG: learned, door.OPENED: opened, "HavePlayedEvent.Dm_TimeTemple_0010": played}
    scenes, writes = run_open_flow(patched.flowchart, state, recommended=recommended)
    success = learned and recommended and not opened and not played
    assert scenes == (["Dm_TimeTemple_0010"] if success else [])
    assert writes == ([door.OPENED, "Step_DoorOfTime"] if success else [])
    if success:
        assert state["Step_DoorOfTime"] == "Step06"
        assert run_open_flow(patched.flowchart, deepcopy(state)) == ([], [])
    # Restore only the intentional entry/edge/appended query; all other flow data must be native.
    patched.flowchart.events.pop()
    patched.flowchart.entry_points[0].main_event = original.flowchart.entry_points[0].main_event
    patched.flowchart.events[2].next = original.flowchart.events[2].next
    assert patched == original


def test_song_patch_refuses_changed_native_gate():
    document = synthetic_flow()
    document.flowchart.events[3].params["GameDataName"] = "OtherQuest"
    with pytest.raises(PatchError, match="changed native"):
        door.song_flow(evfl.write(document))


@pytest.mark.parametrize(
    "mode,items,expected",
    [
        ("open", {}, True),
        ("song_only", {"Ocarina": 1}, False),
        ("song_only", {"Song of Time": 1}, False),
        ("song_only", {"Ocarina": 1, "Song of Time": 1}, True),
        ("closed", {"Ocarina": 2, "Song of Time": 1}, False),
        ("closed", {"Ocarina": 1, "Song of Time": 1, "Kokiri Emerald": 1, "Goron Ruby": 1, "Zora Sapphire": 1}, False),
        ("closed", {"Ocarina": 2, "Song of Time": 1, "Kokiri Emerald": 1, "Goron Ruby": 1, "Zora Sapphire": 1}, True),
    ],
)
def test_world_door_modes_match_actual_inventory_requirements(mode, items, expected):
    settings, world = prepare(load_spec(), Settings(shuffle=GIFTS, door_of_time=mode))
    exit = next(exit for exit in world.regions["Temple of Time"].exits if exit.target == "Beyond Door of Time")
    assert exit.rule(items, CHILD, 3) is expected
    # Early door is independent of reverse travel and the physical Forest/Prelude gate.
    assert not world.settings["free_time_travel"]
    assert not world.locations["Sheik at Temple"].rule(items, ADULT, 3)
    if mode != "closed":
        assert "Sarias Song" not in world.settings["age_return_fill_inventory"]
        assert world.settings["age_return_fill_inventory"].get("Ocarina", 0) < 2
    assert Settings.from_string(settings.to_string()) == settings


@pytest.mark.parametrize("mode", door.MODES)
def test_adult_fairy_ocarina_cannot_play_saria_in_any_door_mode(mode):
    _, world = prepare(load_spec(), Settings(shuffle=GIFTS, door_of_time=mode))
    exit = next(exit for exit in world.regions["Lost Woods"].exits if exit.target == "LW Beyond Mido")
    assert exit.rule({"Ocarina": 1, "Sarias Song": 1}, CHILD, 3)
    assert not exit.rule({"Ocarina": 1, "Sarias Song": 1}, ADULT, 3)
    assert exit.rule({"Ocarina": 2, "Sarias Song": 1}, ADULT, 3)


def test_cli_explicit_door_mode_overrides_an_effective_settings_string(capsys):
    effective, _ = prepare(load_spec(), Settings(shuffle=GIFTS, door_of_time="open"))
    assert main(["--settings", effective.to_string(), "--door-of-time", "song_only", "--print-settings"]) == 0
    settings = Settings.from_string(capsys.readouterr().out.strip())
    assert settings.door_of_time == "song_only"
    resolved, world = prepare(load_spec(), settings)
    assert world.settings["age_return_fill_inventory"] == {"Ocarina": 1, "Song of Time": 1}
    back, _ = prepare(load_spec(), replace(resolved, door_of_time="closed", logic={}))
    assert back.logic["age_return_fill_inventory"]["Ocarina"] == 2
    with pytest.raises(FillError, match="must agree"):
        prepare(load_spec(), Settings(door_of_time="closed", logic={"door_of_time": "open"}))


@pytest.mark.parametrize("mode", ["unsupported", False, None])
def test_bad_modes_are_refused(mode):
    with pytest.raises(ValueError, match="door_of_time"):
        Settings(door_of_time=mode)
    with pytest.raises(PatchError, match="unknown"):
        door.changes({}, mode=mode)
