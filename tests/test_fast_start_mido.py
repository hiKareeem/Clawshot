"""Replay quest/equipment and per-entry call contracts; engine animation completion still needs gameplay."""

import copy

import pytest

from clawshot.formats import evfl
from clawshot.patch import mido
from clawshot.patch.plan import PatchError


def mido_flow():
    """Invented dialogue using the native clear-tail contracts, never extracted game content."""
    return evfl.EventFlowFile(
        "MidoTest",
        evfl.Flowchart(
            "Npc_Kokiri_Mido_Child",
            [
                evfl.Actor(
                    "GameDataActor",
                    actions=["EventTriggerSetGameDataBool"],
                    queries=["EventQueryIsGameDataBoolExp", "EventQueryIsGameDataBool"],
                ),
                evfl.Actor("Player_Event", queries=["EventQueryCheckIsEquippedDynamicEquipment"]),
                evfl.Actor("Npc_Kokiri_Mido_Child", actions=["EventNpcBlockerEndBlockerAI"]),
                evfl.Actor("ChallengeSystemActor", actions=["EventExecuteProgressChallengeStep"]),
            ],
            [
                evfl.SwitchEvent(
                    "Event6", 0, 0, [(0, 1), (1, 1)], {"GameDataName": "Meet_DekuTree_IsAfter_Step01_Exp"}
                ),
                evfl.SubFlowEvent(
                    "Init",
                    "InitTalk",
                    "InitTalk_Blocker",
                    2,
                    {"BlockerNpc": evfl.ActorIdentifier("Npc_Kokiri_Mido_Child")},
                ),
                evfl.SwitchEvent("Event10", 1, 0, [(0, 3), (1, evfl.NONE)], {"DynamicEquipmentSlot": 0}),
                evfl.SwitchEvent("Event12", 1, 0, [(0, 4), (1, evfl.NONE)], {"DynamicEquipmentSlot": 4}),
                evfl.ActionEvent("Event26", 0, 0, 5, {"Index": -1, "GameDataName": mido.BLOCKER, "Value": False}),
                evfl.ActionEvent("Event32", 2, 0, 6, {"IsWaitEnd": True}),
                evfl.ActionEvent("Event33", 0, 0, 7, {"GameDataName": "FirstTalk", "Index": -1, "Value": True}),
                evfl.ActionEvent("Event48", 0, 0, 8, {"GameDataName": "SecondTalk", "Index": -1, "Value": True}),
                evfl.ActionEvent(
                    "Event0",
                    3,
                    0,
                    evfl.NONE,
                    {
                        "ChallengeName": "Meet_DekuTree",
                        "IsWaitEnd": True,
                        "IsIgnoreChallengeProgressUI": False,
                        "StepName": "Step03",
                        "IsIgnoreCompletedChallenge": False,
                    },
                ),
                evfl.SwitchEvent("Later", 0, 0, [(0, evfl.NONE)], {"GameDataName": "Meet_DekuTree_IsCompleted_Exp"}),
            ],
            [evfl.EntryPoint("Talk", 0, [1]), evfl.EntryPoint("Later", 9)],
        ),
    )


class UnregisteredCall(AssertionError):
    pass


class BlockerWait(AssertionError):
    pass


def run_mido(document, *, sword=False, shield=False, meeting="Step01", entry="Talk", blocker_finished=True):
    """Enforce entry call registrations and blocker waits; native presentation actions are not an engine simulation."""
    fc = document.flowchart
    state = {
        mido.BLOCKER: True,
        mido.SEEN_TREE: False,
        mido.MOUTH_OPEN: False,
        "Step_Meet_DekuTree": meeting,
        "Step_Get_StoneOfForest": "Ready",
    }
    trace = []
    budget = 2000

    def wait_for_blocker():
        trace.append("blocker-wait")
        if not blocker_finished:
            raise BlockerWait(f"EventWaitFinishBlockerAction has not completed: {trace}")

    def run(index, current_entry, arguments, stop=evfl.NONE):
        nonlocal budget
        while index not in (evfl.NONE, stop):
            budget -= 1
            assert budget > 0, trace
            event = fc.events[index]
            trace.append(event.name)
            params = getattr(event, "params", None) or {}
            if isinstance(event, evfl.SwitchEvent):
                query = fc.actors[event.actor].queries[event.query]
                if query == "EventQueryIsGameDataBoolExp":
                    name = params["GameDataName"]
                    if name == "Meet_DekuTree_IsAfter_Step01_Exp":
                        holds = state["Step_Meet_DekuTree"] not in {"NotReady", "Ready", "Step01"}
                    elif name == "Meet_DekuTree_IsCompleted_Exp":
                        holds = state["Step_Meet_DekuTree"] == "Complete"
                    else:
                        raise AssertionError((name, event))
                    value = 0 if holds else 1
                elif query == "EventQueryIsGameDataBool":
                    value = 0 if state.get(params["GameDataName"], False) else 1
                elif query == "EventQueryCheckIsEquippedDynamicEquipment":
                    value = 0 if (sword if params["DynamicEquipmentSlot"] == 0 else shield) else 1
                elif query in (
                    "EventQueryAvoidDuplicationRandomChoice2",
                    "EventQueryRandomChoice2",
                    "EventNPCQueryCheckFrontToTarget",
                ):
                    value = 0
                else:
                    raise AssertionError((query, event))
                index = dict(event.cases).get(value, evfl.NONE)
            elif isinstance(event, evfl.ForkEvent):
                assert isinstance(fc.events[event.join], evfl.JoinEvent), event
                for fork in event.forks:
                    run(fork, current_entry, arguments, event.join)
                index = event.join
            elif isinstance(event, evfl.SubFlowEvent):
                if index not in current_entry.sub_flow_events:
                    raise UnregisteredCall(f"{current_entry.name}: {event.name} at {index} not registered; {trace}")
                if not event.flowchart:
                    child = fc.entry_point(event.entry_point)
                    run(child.main_event, child, params)
                elif event.flowchart == "InitTalk" and event.entry_point == "InitTalk_Blocker":
                    # The actual callee's first action is InitTalk Event203, before any fork/message.
                    assert params["BlockerNpc"].name == "Npc_Kokiri_Mido_Child"
                    wait_for_blocker()
                else:
                    # These are unchanged native presentation helpers, not a proof of engine completion.
                    assert event.flowchart in {
                        "InitTalk",
                        "NpcCommon",
                        "Common_Camera_Pln",
                        "NaviEventCommon",
                        "NaviChat",
                    }, event
                index = event.next
            else:
                if isinstance(event, evfl.ActionEvent):
                    action = fc.actors[event.actor].actions[event.action]
                    if action == "EventWaitFinishBlockerAction":
                        wait_for_blocker()
                    elif action == "EventTriggerSetGameDataBool":
                        state[params["GameDataName"]] = params["Value"]
                    elif action == "EventExecuteProgressChallengeStep":
                        state["Step_" + params["ChallengeName"]] = params["StepName"]
                        trace.append(params["ChallengeName"] + ":" + params["StepName"])
                    elif action == "EventNpcBlockerEndBlockerAI":
                        assert state[mido.BLOCKER] is False  # native clear must precede the end action
                        trace.append("blocker-ai-ended")
                    elif action == "EventTalk":
                        assert params.get("MessageId"), event
                index = event.next

    start = fc.entry_point(entry)
    run(start.main_event, start, {})
    return state, trace


@pytest.mark.parametrize("sword,shield", [(False, False), (True, False), (False, True), (True, True)])
def test_tree_skip_takes_effect_only_after_native_equipment_clear(sword, shield):
    original = mido_flow()
    changed = evfl.read(mido.complete_deku_meeting(evfl.write(original)))
    state, trace = run_mido(changed, sword=sword, shield=shield)
    cleared = sword and shield
    assert state[mido.BLOCKER] is not cleared
    assert state[mido.MOUTH_OPEN] is cleared and state[mido.SEEN_TREE] is cleared
    assert state["Step_Meet_DekuTree"] == ("Complete" if cleared else "Step01")
    assert state["Step_Get_StoneOfForest"] == ("GoInside" if cleared else "Ready")
    assert "blocker-wait" in trace
    if cleared:
        assert trace.index("blocker-ai-ended") < trace.index("ClawshotDekuSeen") < trace.index("Meet_DekuTree:Complete")
        assert (
            trace.index("Meet_DekuTree:Complete")
            < trace.index("Get_StoneOfForest:GoInside")
            < trace.index("ClawshotDekuMouth")
        )
    else:
        assert run_mido(original, sword=sword, shield=shield) == (state, trace)


@pytest.mark.parametrize("sword,shield", [(False, False), (True, False), (False, True), (True, True)])
def test_the_failed_cross_entry_jump_is_detected_before_equipment_queries(sword, shield):
    failed = mido_flow()
    failed.flowchart.entry_point("Later").main_event = failed.flowchart.entry_point("Talk").main_event
    with pytest.raises(UnregisteredCall, match="Later: Init at 1 not registered"):
        run_mido(failed, sword=sword, shield=shield, meeting="Complete", entry="Later")


def test_blocker_initialization_wait_is_not_treated_as_an_inert_subflow():
    with pytest.raises(BlockerWait, match="EventWaitFinishBlockerAction has not completed"):
        run_mido(evfl.read(mido.complete_deku_meeting(evfl.write(mido_flow()))), blocker_finished=False)


def test_native_entries_actors_and_pre_clear_events_are_preserved():
    original = mido_flow()
    changed = evfl.read(mido.complete_deku_meeting(evfl.write(original)))
    assert changed.flowchart.entry_points == original.flowchart.entry_points
    assert changed.flowchart.actors == original.flowchart.actors
    restored = copy.deepcopy(changed)
    restored.flowchart.events = restored.flowchart.events[: len(original.flowchart.events)]
    for index in (7, 8):  # only the existing post-clear tail can differ
        restored.flowchart.events[index] = original.flowchart.events[index]
    assert restored == original
    assert all(
        isinstance(event, evfl.ActionEvent) for event in changed.flowchart.events[len(original.flowchart.events) :]
    )


def test_changed_native_clear_tail_is_refused():
    original = mido_flow()
    original.flowchart.events[8].params["StepName"] = "Complete"
    with pytest.raises(PatchError, match="changed native Mido clear tail"):
        mido.complete_deku_meeting(evfl.write(original))
