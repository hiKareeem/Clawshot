"""Synthetic native-style gift/prop-cleanup fork; no decoded game fixtures."""

import pytest

from clawshot.census.gifts import Gift
from clawshot.formats import evfl
from clawshot.patch import gifts

FLOW = "Npc_Hylia_Dampe_001"


def chart():
    return evfl.Flowchart(
        FLOW,
        [
            evfl.Actor("GameDataActor", actions=[gifts.SET_ACTION], queries=[gifts.READ_QUERY]),
            evfl.Actor("Prop", actions=["Cleanup"]),
        ],
        [
            evfl.ForkEvent("Event449", 3, [1, 2]),
            evfl.SubFlowEvent(
                "Event628",
                "Dm_SY_GetInEvent",
                "GetInEvent_NotTurn_NotNpc_Dampe",
                params={"ActorName": "Obj_Heart_Piece", "IsNpcEventStarter": False},
            ),
            evfl.ActionEvent("Cleanup", 1, 0),
            evfl.JoinEvent("Join", 4),
            evfl.ActionEvent("Event357", 0, 0, params={"GameDataName": gifts.DAMPE_FLAG, "Value": True}),
        ],
        [evfl.EntryPoint("Prize", 0)],
    )


def change():
    step = Gift(
        f"{FLOW}/Event628",
        "npc_gift",
        FLOW,
        "f",
        (),
        "Event628",
        "Dm_SY_GetInEvent:GetInEvent_NotTurn_NotNpc_Dampe",
        "ActorName",
        "Obj_Heart_Piece",
        "Graveyard",
    )
    return gifts.GiftChange(gifts.Rule(gifts.DAMPE_CHECK, "swap"), (step,), "Item_Boomerang")


def run(fc, state):
    rewards, cleanup = [], []

    def visit(i):
        while i != evfl.NONE:
            e = fc.events[i]
            if isinstance(e, evfl.ForkEvent):
                for branch in e.forks:
                    visit(branch)
                i = e.join
            elif isinstance(e, evfl.SwitchEvent):
                i = dict(e.cases)[0 if state.get(e.params["GameDataName"], False) else 1]
            elif isinstance(e, evfl.SubFlowEvent):
                rewards.append(e.params["ActorName"])
                i = e.next
            elif isinstance(e, evfl.JoinEvent):
                i = e.next
            else:
                if fc.actors[e.actor].name == "GameDataActor":
                    state[e.params["GameDataName"]] = e.params["Value"]
                else:
                    cleanup.append(True)
                i = e.next

    visit(fc.entry_point("Prize").main_event)
    return rewards, cleanup


def test_digging_gift_once_even_on_direct_retry_with_prop_cleanup_preserved():
    fc = chart()
    gifts.patch_flowchart(fc, FLOW, [change()])
    fc = evfl.read(evfl.write(evfl.EventFlowFile(FLOW, flowchart=fc))).flowchart
    state = {}
    assert run(fc, state) == (["Item_Boomerang"], [True])
    assert state == {gifts.DAMPE_FLAG: True}
    saved = dict(state)
    assert run(fc, saved) == ([], [True])
    assert saved == state


def test_extra_unguarded_digging_caller_refuses():
    fc = chart()
    fc.entry_points.append(evfl.EntryPoint("Unsafe", 1))
    with pytest.raises(gifts.GiftPatchError, match="stale digging reward fork"):
        gifts.patch_flowchart(fc, FLOW, [change()])
