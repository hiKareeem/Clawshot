"""Story completion cannot retire a shuffled, uncollected merchant reward."""

import copy

import pytest
from test_gifts_shopkeeper import offer_chart, offer_steps, run_offer

from clawshot.formats import evfl
from clawshot.patch import gifts

FLOW = gifts.SHOPKEEPER_FLOW
FLAG = "HaveTalked_Npc_Kokiri_001_Shop_Child_PresentDekuShield"
MEETING = "Meet_DekuTree_IsAfter_Step02_Exp"
CASTLE = "Goto_HyruleCastle_IsCompleted_Exp"
GOHMA = "Get_StoneOfForest_IsCompleted_Exp"


def merchant_chart():
    chart = offer_chart()
    chart.events[0].name = "Event45"
    chart.events[1].params["GameDataName"] = FLAG
    chart.actors[1].queries.append("EventQueryIsGameDataBoolExp")
    chart.events.extend(
        [
            evfl.ActionEvent("Event24", 1, 0, 6, {"GameDataName": "NaviTalked", "Index": -1, "Value": True}),
            evfl.SwitchEvent("Event23", 1, 1, [(0, 10), (1, 7)], {"GameDataName": CASTLE}),
            evfl.SwitchEvent("Event21", 1, 1, [(0, 10), (1, 8)], {"GameDataName": GOHMA}),
            evfl.SwitchEvent("Event1", 1, 1, [(0, 9), (1, 10)], {"GameDataName": MEETING}),
            evfl.SubFlowSwitchEvent("Event83", "", "present_DekuSheld", [(9, 10)], None),
            evfl.ReturnEvent("NativeShop", 0),
        ]
    )
    chart.entry_points.append(evfl.EntryPoint("Talk", 5))
    return chart


def dispatch_offer(chart, flags, *, equipped=True):
    """Interpret the story-dispatch prefix; native shop/menu handling is the boundary."""
    index = next(i for i, event in enumerate(chart.events) if event.name == "Event24")
    for _ in range(len(chart.events) + 1):
        event = chart.events[index]
        if isinstance(event, evfl.SwitchEvent):
            query = chart.actors[event.actor].queries[event.query]
            assert query in (gifts.READ_QUERY, "EventQueryIsGameDataBoolExp"), event
            index = dict(event.cases)[0 if flags.get(event.params["GameDataName"], False) else 1]
        elif isinstance(event, evfl.ActionEvent):
            assert chart.actors[event.actor].actions[event.action] == gifts.SET_ACTION, event
            flags[event.params["GameDataName"]] = event.params["Value"]
            index = event.next
        elif isinstance(event, evfl.SubFlowSwitchEvent):
            assert event.entry_point == "present_DekuSheld", event
            return run_offer(chart, flags, equipped=equipped)
        else:
            return []  # Original story-specific shop path, outside the offer dispatch.
    raise AssertionError("merchant dispatch did not terminate")


@pytest.mark.parametrize("castle,gohma", [(False, False), (False, True), (True, False), (True, True)])
@pytest.mark.parametrize("equipped", [False, True])
def test_uncollected_reward_survives_both_story_cutoffs(castle, gohma, equipped):
    chart = merchant_chart()
    original = copy.deepcopy(chart)
    rule = gifts.Rule(gifts.SHOPKEEPER_CHECK, "rewrite", flag=FLAG, once=(FLOW + "/Event45",))
    gifts.patch_flowchart(chart, FLOW, [gifts.GiftChange(rule, offer_steps(), "Item_Boomerang")])
    chart = evfl.read(evfl.write(evfl.EventFlowFile(FLOW, flowchart=chart))).flowchart
    flags = {MEETING: True, CASTLE: castle, GOHMA: gohma}
    assert dispatch_offer(chart, flags, equipped=equipped) == ["Item_Boomerang"], flags
    assert flags[FLAG] is True
    assert dispatch_offer(chart, flags, equipped=not equipped) == []
    assert dispatch_offer(chart, dict(flags)) == []  # persisted completion
    if castle or gohma:
        assert dispatch_offer(original, {MEETING: True, CASTLE: castle, GOHMA: gohma}, equipped=False) == []


def test_dispatch_still_requires_the_native_meeting_and_preserves_completed_story_path():
    chart = merchant_chart()
    rule = gifts.Rule(gifts.SHOPKEEPER_CHECK, "rewrite", flag=FLAG, once=(FLOW + "/Event45",))
    gifts.patch_flowchart(chart, FLOW, [gifts.GiftChange(rule, offer_steps(), "Item_Boomerang")])
    flags = {CASTLE: True, GOHMA: True}
    assert dispatch_offer(chart, flags) == []
    assert FLAG not in flags
    flags.update({MEETING: True, FLAG: True})
    assert dispatch_offer(chart, flags) == []


def test_stale_story_dispatch_is_refused():
    chart = merchant_chart()
    chart.events[5].next = 7
    rule = gifts.Rule(gifts.SHOPKEEPER_CHECK, "rewrite", flag=FLAG, once=(FLOW + "/Event45",))
    with pytest.raises(gifts.GiftPatchError, match="dispatch"):
        gifts.patch_flowchart(chart, FLOW, [gifts.GiftChange(rule, offer_steps(), "Item_Boomerang")])
