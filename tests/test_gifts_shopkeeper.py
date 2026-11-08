"""A shuffled merchant reward must not leak a shield or repeat after collection."""

import copy

import pytest

from clawshot.census.gifts import Gift
from clawshot.formats import evfl
from clawshot.generate import Settings, prepare
from clawshot.patch import gifts
from clawshot.patch.items import loads as load_actors
from clawshot.world.load import load_spec
from clawshot.world.search import Search

FLAG = "SyntheticMerchantDone"
FLOW = gifts.SHOPKEEPER_FLOW


def offer_chart():
    # Synthetic two-branch offer, not extracted from a game file.
    return evfl.Flowchart(
        FLOW,
        [
            evfl.Actor("Player_Event", queries=["EventQueryPlayerIsEquipWeapon"]),
            evfl.Actor("GameDataActor", queries=[gifts.READ_QUERY], actions=[gifts.SET_ACTION]),
        ],
        [
            evfl.SwitchEvent("Equipment", 0, 0, [(0, 4), (1, 1)], {"ArmorName": "Weapon_Shield_Deku", "WeaponSlot": 4}),
            evfl.SwitchEvent("Dialogue", 1, 0, [(0, 2), (1, 3)], {"GameDataName": FLAG, "Index": -1}),
            evfl.SubFlowEvent("Event116", "Dm_SY_GetInEvent", "GetInEvent_Mask", 4, {"ActorName": "Obj_Shield_Deku"}),
            evfl.SubFlowEvent("Event117", "Dm_SY_GetInEvent", "GetInEvent_Mask", 4, {"ActorName": "Obj_Shield_Deku"}),
            evfl.ReturnEvent("End", 9),
        ],
        [evfl.EntryPoint("present_DekuSheld", 0)],
    )


def offer_steps():
    return tuple(
        Gift(
            ref,
            "npc_gift",
            FLOW,
            "offer.bfevfl",
            ("present_DekuSheld",),
            ref.split("/")[1],
            "Dm_SY_GetInEvent:GetInEvent_Mask",
            "ActorName",
            "Obj_Shield_Deku",
            "KokiriForest",
        )
        for ref in gifts.SHOPKEEPER_STEPS
    )


def run_offer(chart, flags, *, equipped=False, start=None):
    """Execute this small EVFL subset; external get wrappers record their bound actor, not engine behavior."""
    i = chart.entry_point("present_DekuSheld").main_event if start is None else start
    granted = []
    for _ in range(len(chart.events) + 1):
        if i == evfl.NONE:
            return granted
        event = chart.events[i]
        if isinstance(event, evfl.ReturnEvent):
            return granted
        if isinstance(event, evfl.SwitchEvent):
            actor = chart.actors[event.actor]
            query = actor.queries[event.query]
            if query == gifts.READ_QUERY:
                answer = flags.get(event.params["GameDataName"], False)
            else:
                assert query == "EventQueryPlayerIsEquipWeapon", event
                answer = equipped
            i = dict(event.cases)[0 if answer else 1]
        else:
            if isinstance(event, evfl.SubFlowEvent):
                assert (event.flowchart, event.entry_point) == ("Dm_SY_GetInEvent", "GetInEvent_Mask")
                granted.append(event.params["ActorName"])
            else:
                assert isinstance(event, evfl.ActionEvent), event
                actor = chart.actors[event.actor]
                if actor.name == "GameDataActor":
                    assert actor.actions[event.action] == gifts.SET_ACTION
                    flags[event.params["GameDataName"]] = event.params["Value"]
                else:
                    assert actor.actions[event.action] == "EventTalk", event
            i = event.next
    raise AssertionError("offer did not terminate")


@pytest.mark.parametrize("equipped", [False, True])
def test_shuffled_offer_ignores_equipment_and_saved_completion_stops_repeats(equipped):
    chart = offer_chart()
    rule = gifts.Rule(gifts.SHOPKEEPER_CHECK, "rewrite", flag=FLAG, once=(FLOW + "/Equipment",))
    change = gifts.GiftChange(rule, offer_steps(), "Item_Boomerang")
    gifts.patch_flowchart(chart, FLOW, [change])
    chart = evfl.read(evfl.write(evfl.EventFlowFile(FLOW, flowchart=chart))).flowchart
    flags = {}
    assert run_offer(chart, flags, equipped=equipped) == ["Item_Boomerang"]
    assert flags == {FLAG: True}
    assert run_offer(chart, flags, equipped=not equipped) == []
    assert run_offer(chart, dict(flags), equipped=False) == []  # saved/reloaded completion
    # Either grant branch independently establishes the same completion, including the old repeat branch.
    for step in offer_steps():
        flags = {}
        start = next(i for i, event in enumerate(chart.events) if event.name == step.event)
        assert run_offer(chart, flags, start=start) == ["Item_Boomerang"]
        assert run_offer(chart, flags) == []


def test_unpatched_offer_keeps_equipment_exclusion_and_repeat_grants():
    chart = offer_chart()
    assert run_offer(chart, {}, equipped=True) == []
    assert run_offer(chart, {FLAG: True}) == ["Obj_Shield_Deku"]
    assert run_offer(chart, {FLAG: True}) == ["Obj_Shield_Deku"]


def test_stale_equipment_contract_and_missing_grant_branch_are_refused():
    chart = offer_chart()
    chart.events[0].params["ArmorName"] = "OtherShield"
    rule = gifts.Rule(gifts.SHOPKEEPER_CHECK, "rewrite", flag=FLAG, once=(FLOW + "/Equipment",))
    with pytest.raises(gifts.GiftPatchError):
        gifts.flow_transform(FLOW, [gifts.GiftChange(rule, offer_steps(), "Item_Boomerang")])(
            evfl.write(evfl.EventFlowFile(FLOW, flowchart=chart))
        )
    with pytest.raises(gifts.GiftPatchError):
        gifts.plan({gifts.SHOPKEEPER_CHECK: "Item_Boomerang"}, offer_steps()[:1], (), {rule.check: rule})


def test_unmoved_shuffled_shield_still_gets_the_once_gate():
    rule = gifts.Rule(gifts.SHOPKEEPER_CHECK, "rewrite", flag=FLAG, once=(FLOW + "/Equipment",))
    actors = load_actors('[items]\n"Deku Shield" = { actor = "Obj_Shield_Deku" }\n')
    step = gifts.seed_step(
        [rule.check], offer_steps(), (), {rule.check: rule}, actors, {rule.check: "Deku Shield"}, {FLOW: "offer.bfevfl"}
    )
    out = step({rule.check: "Deku Shield"})
    assert gifts.GAME_DATA_LIST not in out  # existing saved Bool, no new save layout
    chart = evfl.read(out["offer.bfevfl"](evfl.write(evfl.EventFlowFile(FLOW, flowchart=offer_chart())))).flowchart
    flags = {}
    assert run_offer(chart, flags, equipped=True) == ["Obj_Shield_Deku"]
    assert run_offer(chart, flags) == []


def test_placed_reward_removes_implicit_shield_and_cannot_bootstrap_mido():
    spec = load_spec()
    before = copy.deepcopy(spec)
    changed = gifts.shopkeeper_spec(spec)
    assert spec == before
    assert any("Deku Shield" in r.get("events", {}) for r in spec["regions"] if r["name"] == gifts.SHOPKEEPER_REGION)
    _, world = prepare(changed, Settings())
    assert not any(event.name == "Deku Shield" and event.region == gifts.SHOPKEEPER_REGION for event in world.events)
    check = world.locations[gifts.SHOPKEEPER_CHECK]
    search = Search.child_only(world, ["Kokiri Sword"])
    assert not search.can_access(check, "child")
    search.collect("Hylian Shield")
    assert search.can_access(check, "child")
    assert not search.holds("Deku Shield")  # Reaching the shop is not collecting its placed reward.
    search.collect("Boomerang")
    assert not search.holds("Deku Shield")
    _, vanilla = prepare(spec, Settings())
    assert Search.child_only(vanilla, ["Kokiri Sword", "Hylian Shield"]).holds("Deku Shield")
    _, opened = prepare(changed, Settings(forest="open"))
    assert Search.child_only(opened).can_access(opened.locations[gifts.SHOPKEEPER_CHECK], "child")
    assert not Search(opened).can_access(opened.locations[gifts.SHOPKEEPER_CHECK], "adult")
