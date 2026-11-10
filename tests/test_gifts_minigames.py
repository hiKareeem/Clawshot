"""Synthetic bowling completion sequence and fixed upgrade contracts."""

from copy import deepcopy

import pytest

from clawshot.census.definitions import Definition
from clawshot.census.gifts import Gift
from clawshot.formats import evfl
from clawshot.patch import gifts
from clawshot.patch.items import load as actors

FLOW = gifts.BOWLING_FLOW
FIRST = "MiniGame_BombchuBowling_ClearFirstTime"
SECOND = "MiniGame_BombchuBowling_ClearSecondTime"
THIRD = "MiniGame_BombchuBowling_ClearThirdTime"


def chart():
    return evfl.Flowchart(
        FLOW,
        [
            evfl.Actor("GameDataActor", actions=[gifts.SET_ACTION], queries=[gifts.READ_QUERY]),
            evfl.Actor("PouchSystemActor", queries=["EventQueryIsExistInPouch"]),
        ],
        [
            evfl.SwitchEvent("Event73", 0, 0, [(0, 1), (1, 7)], {"GameDataName": FIRST, "Index": -1}),
            evfl.SwitchEvent("Event72", 0, 0, [(0, 3), (1, 2)], {"GameDataName": SECOND, "Index": -1}),
            evfl.SwitchEvent("Event76", 1, 0, [(0, 6), (1, 5)], {"Actor": "Item_BombBag_Medium", "Num": 1}),
            evfl.SwitchEvent("Event260", 0, 0, [(0, 8), (1, 4)], {"GameDataName": THIRD, "Index": -1}),
            evfl.SubFlowEvent("Event143", "NpcCommon", "Give", 9, {"ReveiveItem": "Obj_Heart_Piece"}),
            evfl.SubFlowEvent("Event304", "NpcCommon", "Give", 9, {"ReveiveItem": "Item_BombBag_Medium"}),
            evfl.SubFlowEvent("Event306", "NpcCommon", "Give", 9, {"ReveiveItem": "Item_BombBag_Large"}),
            evfl.SubFlowEvent("Event309", "NpcCommon", "Give", 9, {"ReveiveItem": "Item_BombchuBundle_Medium"}),
            evfl.SubFlowEvent("Event81", "NpcCommon", "Give", 9, {"ReveiveItem": "Obj_Rupee_Red"}),
            evfl.SubFlowEvent("Count", "", "MiniGameClearCount"),
            evfl.SwitchEvent("CountSecond", 0, 0, [(0, 14), (1, 11)], {"GameDataName": SECOND}),
            evfl.SwitchEvent("CountFirst", 0, 0, [(0, 13), (1, 12)], {"GameDataName": FIRST}),
            evfl.ActionEvent("SetFirst", 0, 0, params={"GameDataName": FIRST, "Value": True}),
            evfl.ActionEvent("SetSecond", 0, 0, params={"GameDataName": SECOND, "Value": True}),
            evfl.ActionEvent("SetThird", 0, 0, params={"GameDataName": THIRD, "Value": True}),
        ],
        [evfl.EntryPoint("Win", 0), evfl.EntryPoint("MiniGameClearCount", 10), evfl.EntryPoint("Lose", evfl.NONE)],
    )


def changes():
    out = []
    for check, events, item in [
        (
            gifts.BOWLING_FIRST,
            [("Event304", "Item_BombBag_Medium"), ("Event306", "Item_BombBag_Large")],
            "Item_Boomerang",
        ),
        (gifts.BOWLING_SECOND, [("Event143", "Obj_Heart_Piece")], "Item_Hookshot"),
    ]:
        steps = tuple(
            Gift(f"{FLOW}/{e}", "npc_gift", FLOW, "f", (), e, "NpcCommon:Give", "ReveiveItem", old, "Market")
            for e, old in events
        )
        out.append(gifts.GiftChange(gifts.Rule(check, "swap"), steps, item))
    return out


def run(fc, state, entry="Win", owns_upgrade=False):
    rewards = []

    def visit(entry):
        i = fc.entry_point(entry).main_event
        while i != evfl.NONE:
            e = fc.events[i]
            if isinstance(e, evfl.SwitchEvent):
                yes = state.get(e.params["GameDataName"], False) if "GameDataName" in e.params else owns_upgrade
                i = dict(e.cases)[0 if yes else 1]
            elif isinstance(e, evfl.SubFlowEvent):
                if e.flowchart == "NpcCommon":
                    rewards.append(e.params["ReveiveItem"])
                else:
                    visit(e.entry_point)
                i = e.next
            else:
                state[e.params["GameDataName"]] = e.params["Value"]
                i = e.next

    visit(entry)
    return rewards


@pytest.mark.parametrize("owns_upgrade", [False, True])
def test_first_second_then_native_filler_survive_save_and_failed_round(owns_upgrade):
    fc = chart()
    gifts.patch_flowchart(fc, FLOW, changes())
    fc = evfl.read(evfl.write(evfl.EventFlowFile(FLOW, flowchart=fc))).flowchart
    state = {}
    assert run(fc, state, "Lose") == []
    assert state == {}
    assert run(fc, state, owns_upgrade=owns_upgrade) == ["Item_Boomerang"]
    assert state == {FIRST: True}
    state = deepcopy(state)
    assert run(fc, state, "Lose") == []
    assert state == {FIRST: True}
    assert run(fc, state, owns_upgrade=owns_upgrade) == ["Item_Hookshot"]
    assert state == {FIRST: True, SECOND: True, THIRD: True}
    assert run(fc, dict(state), owns_upgrade=owns_upgrade) == ["Obj_Rupee_Red"]


def test_fixed_tier_selection_does_not_require_an_owned_rental_weapon():
    from clawshot.generate import Settings, prepare
    from clawshot.world.load import load_spec

    _, world = prepare(load_spec(), Settings(shuffle=gifts.GIFT_TYPES))
    census, definitions = [], []
    for check, (_, native) in gifts.TIERED_GIFTS.items():
        for n, actor in enumerate(sorted(native)):
            step = Gift(
                f"Synthetic{check}/Event{n}",
                "npc_gift",
                "Synthetic",
                "f",
                (),
                f"Event{n}",
                "W:G",
                "ActorName",
                actor,
                "",
            )
            census.append(step)
            definitions.append(Definition(step.id, step.kind, "", step.id, actor, check))
    assert set(gifts.seed_checks(world, census, definitions, gifts.load(), actors())) == set(gifts.TIERED_GIFTS)
    assert world.items["Bomb Bag (30)"].alias == ("Bomb Bag", 1)
    assert not world.items["Bullet Bag (40)"].progression
    assert not world.items["Quiver (40)"].progression


def test_stale_bowling_order_refuses():
    fc = chart()
    fc.events[0].cases.reverse()
    with pytest.raises(gifts.GiftPatchError, match="stale bowling prize order"):
        gifts.patch_flowchart(fc, FLOW, changes())


@pytest.mark.parametrize("owned", [False, True])
def test_unchanged_pool_assignment_still_fixes_order_and_ownership_dependent_tier(owned):
    from clawshot.census.definitions import load

    census = [s for c in changes() for s in c.steps]
    vanilla = {gifts.BOWLING_FIRST: "Bomb Bag (30)", gifts.BOWLING_SECOND: "Piece of Heart"}
    step = gifts.seed_step(list(vanilla), census, load(), gifts.load(), actors(), vanilla, {FLOW: "f"})
    data = evfl.write(evfl.EventFlowFile(FLOW, flowchart=chart()))
    fc = evfl.read(step(vanilla)["f"](data)).flowchart
    state = {}
    assert run(fc, state, owns_upgrade=owned) == ["Item_BombBag_Medium"]
    assert run(fc, state, owns_upgrade=owned) == ["Obj_Heart_Piece"]
    assert run(fc, state, owns_upgrade=owned) == ["Obj_Rupee_Red"]
