"""Synthetic tutorial offer: no copied native graph or dialogue."""

from copy import deepcopy

import pytest

from clawshot.census.gifts import Gift
from clawshot.formats import evfl
from clawshot.patch import gifts

FLOW = gifts.MARKET_BOTTLE_FLOW
ENTRY = "Item_Bottle_TutorialEvent_Talk"


def chart():
    return evfl.Flowchart(
        FLOW,
        [
            evfl.Actor("GameDataActor", actions=[gifts.SET_ACTION], queries=[gifts.READ_QUERY]),
            evfl.Actor("Player_Event", actions=["Accept"]),
            evfl.Actor("GameSystemActor", queries=["Choice"]),
            evfl.Actor("ChallengeSystemActor", actions=["Complete"]),
            evfl.Actor(
                FLOW,
                actions=[
                    "EventPlayAS",
                    "EventTriggerAIScheduleSelectSchedule",
                    "EventTriggerAIScheduleSetForceCancelEventContinueArrivalAS",
                ],
            ),
        ],
        [
            evfl.ActionEvent("Event27", 1, 0, 1),
            evfl.SwitchEvent("Offer", 2, 0, [(0, 2), (1, evfl.NONE)]),
            evfl.ActionEvent("Event6", 1, 0, 3),
            evfl.ActionEvent("Event10", 1, 0),
            evfl.SubFlowEvent(
                "Event171",
                "Dm_SY_GetInEvent",
                "GetInEvent_NotTurn_FixedCamera_WarpLink",
                params={"ActorName": "Item_Bottle"},
            ),
            evfl.ActionEvent("Event76", 3, 0),
            evfl.ActionEvent("Shop", 1, 0),
            evfl.ActionEvent("Event65", 4, 0, params={"ASName": "Wait"}),
            evfl.ActionEvent("Event63", 4, 1),
            evfl.ActionEvent("Event62", 4, 2, params={"Value": False}),
        ],
        [evfl.EntryPoint(ENTRY, 0), evfl.EntryPoint("Talk", 6)],
    )


def change():
    step = Gift(
        gifts.MARKET_BOTTLE_STEP,
        "npc_gift",
        FLOW,
        "f",
        (ENTRY,),
        "Event171",
        "Dm_SY_GetInEvent:GetInEvent_NotTurn_FixedCamera_WarpLink",
        "ActorName",
        "Item_Bottle",
        "Market",
    )
    return gifts.GiftChange(gifts.Rule(gifts.MARKET_BOTTLE_CHECK, "swap"), (step,), "Item_Boomerang")


def run(fc, state, accept, npc=None):
    index = fc.entry_point(ENTRY).main_event
    rewards = []
    while index != evfl.NONE:
        event = fc.events[index]
        if isinstance(event, evfl.SwitchEvent):
            result = state.get(event.params["GameDataName"], False) if event.params else accept
            index = dict(event.cases)[0 if result else 1]
        elif isinstance(event, evfl.SubFlowEvent):
            rewards.append(event.params["ActorName"])
            index = event.next
        else:
            if fc.actors[event.actor].name == "GameDataActor":
                state[event.params["GameDataName"]] = event.params["Value"]
            elif npc is not None and fc.actors[event.actor].name == FLOW:
                action = fc.actors[event.actor].actions[event.action]
                if action == "EventPlayAS":
                    npc["animation"] = event.params["ASName"]
                elif action == "EventTriggerAIScheduleSelectSchedule":
                    npc["schedule"] = (
                        "shop"
                        if state.get("Market_Item_Bottle_TutorialEvent_Shop_Bottle_Insect_Appeared")
                        else "tutorial"
                    )
                else:
                    npc["force_arrival"] = event.params["Value"]
            index = event.next
    return rewards


def test_accept_without_bottle_grants_once_then_saved_revisit_uses_shop():
    fc = chart()
    gifts.patch_flowchart(fc, FLOW, [change()])
    fc = evfl.read(evfl.write(evfl.EventFlowFile(FLOW, flowchart=fc))).flowchart
    state = {}
    assert run(fc, state, False) == []
    assert state == {}
    npc = {"animation": "frightened", "schedule": "tutorial", "force_arrival": True}
    assert run(fc, state, True, npc) == ["Item_Boomerang"]
    assert npc == {"animation": "Wait", "schedule": "shop", "force_arrival": False}
    assert state == {
        gifts.MARKET_BOTTLE_FLAG: True,
        "Market_Item_Bottle_TutorialEvent_Started": True,
        "Market_Item_Bottle_TutorialEvent_Cleared": True,
        "Market_Item_Bottle_TutorialEvent_Insect_Delete": True,
        "Market_Item_Bottle_TutorialEvent_Shop_Bottle_Insect_Appeared": True,
    }
    saved = deepcopy(state)
    assert run(fc, saved, True) == []
    assert saved == state


def test_stale_bottle_tutorial_dispatch_refuses():
    fc = chart()
    fc.events[2].next = evfl.NONE
    with pytest.raises(gifts.GiftPatchError, match="stale bottle tutorial"):
        gifts.patch_flowchart(fc, FLOW, [change()])


def test_market_tutorial_is_an_early_child_bottle_without_an_owned_bottle():
    from clawshot.generate import Settings, prepare
    from clawshot.world.load import load_spec
    from clawshot.world.search import Search

    spec = load_spec()
    spec["start"] = "Market Potion Shop"
    _, world = prepare(spec, Settings())
    search = Search(world)
    location = world.locations[gifts.MARKET_BOTTLE_CHECK]
    assert search.can_access(location, "child")
    assert not search.can_access(location, "adult")
    search.collect_spheres({gifts.MARKET_BOTTLE_CHECK: location.vanilla})
    assert search.counts["Bottle"] == 1
