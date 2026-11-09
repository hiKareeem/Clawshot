"""Synthetic first-song state transitions; fixtures are not extracted game graphs."""

import pytest

from clawshot.census.gifts import FROG_SONG_CALL, FROG_SONG_FLAGS, Gift, find_gifts
from clawshot.formats import evfl
from clawshot.patch import gifts

FLOW = "MiniGame_FrogTenors"


def song_chart():
    events = [
        evfl.SwitchEvent("Event167", 0, 0, [(0, 4), (1, 1)], {"GameDataName": evfl.Argument("GameDataName"), "Index": -1}),
        evfl.ActionEvent("Event380", 1, 0, 2),
        evfl.ActionEvent("NativeRupees", 2, 0, 3, {"Value": 5}),
        evfl.ActionEvent("Event392", 0, 1, 4, {"GameDataName": "SongCount", "Value": 1}),
        evfl.ActionEvent("SaveSong", 0, 0, params={"GameDataName": evfl.Argument("GameDataName"), "Value": True}),
    ]
    entries = [evfl.EntryPoint("TeachNewMusic", 0)]
    for event, flag in FROG_SONG_FLAGS.items():
        index = len(events)
        events.append(evfl.SubFlowEvent(event, "", "TeachNewMusic", params={"GameDataName": flag}))
        entries.append(evfl.EntryPoint(event, index, [index]))
    return evfl.Flowchart(
        FLOW,
        [
            evfl.Actor("GameDataActor", actions=["EventTriggerSetGameDataBool", "EventTriggerAddOrSubGameDataInt"], queries=[gifts.READ_QUERY]),
            evfl.Actor("UISystemActor", actions=["EventTriggerOpenRupeeDisplay"]),
            evfl.Actor("PouchSystemActor", actions=["EventTriggerIncreaseRupee"]),
        ],
        events,
        entries,
    )


def run(chart, entry, state, rewards, args=None):
    args = args or {}
    index = chart.entry_point(entry).main_event
    while index != evfl.NONE:
        event = chart.events[index]
        params = {key: args[str(value)] if isinstance(value, evfl.Argument) else value for key, value in (event.params or {}).items()}
        if isinstance(event, evfl.SwitchEvent):
            index = dict(event.cases)[0 if state.get(params["GameDataName"], False) else 1]
        elif isinstance(event, evfl.SubFlowEvent):
            if event.flowchart == "Dm_SY_GetInEvent":
                rewards.append(params["ActorName"])
            else:
                run(chart, event.entry_point, state, rewards, params)
            index = event.next
        else:
            action = chart.actors[event.actor].actions[event.action]
            if action == "EventTriggerSetGameDataBool":
                state[params["GameDataName"]] = params["Value"]
            elif action == "EventTriggerAddOrSubGameDataInt":
                state[params["GameDataName"]] = state.get(params["GameDataName"], 0) + params["Value"]
            elif action == "EventTriggerIncreaseRupee":
                state["rupees"] = state.get("rupees", 0) + params["Value"]
            elif action != "EventTriggerOpenRupeeDisplay":
                raise AssertionError(action)
            index = event.next


def test_each_song_grants_once_and_keeps_native_completion_counter_without_extra_rupees():
    chart = song_chart()
    steps = find_gifts({FLOW: chart}, {FLOW: "song.bfevfl"})
    changes = [gifts.GiftChange(gifts.Rule(step.event, "swap"), (step,), "Item_" + step.event) for step in steps]
    gifts.patch_flowchart(chart, FLOW, changes)
    chart = evfl.read(evfl.write(evfl.EventFlowFile(FLOW, flowchart=chart))).flowchart
    state, rewards = {}, []
    for event, flag in FROG_SONG_FLAGS.items():
        run(chart, event, state, rewards)
        assert rewards[-1] == "Item_" + event
        assert state[flag] is True
        # A saved state reconstructed for another run still bypasses the new reward.
        saved = dict(state)
        previous = list(rewards)
        run(chart, event, saved, rewards)
        assert rewards == previous and saved == state
    assert rewards == ["Item_" + event for event in FROG_SONG_FLAGS]
    assert state["SongCount"] == 5
    assert state.get("rupees", 0) == 0
    # The shared native entry remains usable by an untouched caller.
    native = {}
    run(chart, "TeachNewMusic", native, [], {"GameDataName": "UnmodifiedSong"})
    assert native == {"UnmodifiedSong": True, "SongCount": 1, "rupees": 5}


def test_song_specialization_refuses_a_stale_completion_flag():
    chart = song_chart()
    event = next(e for e in chart.events if e.name == "Event172")
    event.params["GameDataName"] = "UnrelatedFlag"
    step = Gift(FLOW + "/Event172", "npc_gift", FLOW, "f", (), "Event172", FROG_SONG_CALL, "", "", "")
    with pytest.raises(gifts.GiftPatchError, match="not a native frog-song call"):
        gifts.patch_flowchart(chart, FLOW, [gifts.GiftChange(gifts.Rule("Song", "swap"), (step,), "Item_New")])
