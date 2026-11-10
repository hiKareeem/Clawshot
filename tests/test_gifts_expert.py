"""Synthetic first-expert gates: normal/failure isolation, independent saved prizes, native repeats."""

import pytest

from clawshot.census.gifts import find_gifts
from clawshot.formats import evfl
from clawshot.patch import gifts

FLOW = "MiniGame_HitTarget"


def chart():
    fc = evfl.Flowchart(
        FLOW,
        [
            evfl.Actor("GameDataActor", actions=[gifts.SET_ACTION], queries=[gifts.READ_QUERY]),
            evfl.Actor("UISystemActor", actions=["Open", "EventCloseRupeeDisplay"]),
        ],
        [],
        [evfl.EntryPoint("Lose", evfl.NONE)],
    )
    for event, (mode, start, close) in gifts.GALLERY_EXPERT_ROUTES.items():
        index = len(fc.events)
        fc.events.extend(
            [
                evfl.SwitchEvent(
                    mode,
                    0,
                    0,
                    [(0, index + 1), (1, index + 4)],
                    {"GameDataName": "MiniGame_HitTarget_IsHardMode", "Index": -1},
                ),
                evfl.ActionEvent(start, 1, 0, index + 2),
                evfl.SubFlowEvent(
                    event, "", "GetRupy_HitTarget", index + 3, {"GetRupee": gifts.GALLERY_EXPERT_RUPEES[event]}
                ),
                evfl.ActionEvent(close, 1, 1),
                evfl.SubFlowEvent(
                    "Normal" + event,
                    "Dm_SY_GetInEvent",
                    "GetInEvent_NotTurn_NotNpc",
                    params={"ActorName": "NativeNormalRepeat"},
                ),
            ]
        )
        fc.entry_points.append(evfl.EntryPoint(event, index))
    return fc


def changes(fc, item="Item_Boomerang"):
    return gifts.plan(
        dict.fromkeys(gifts.GALLERY_EXPERT_CHECKS.values(), item),
        find_gifts({FLOW: fc}, {FLOW: "gallery.bfevfl"}),
        [],
        gifts.load(),
    )


def run(fc, entry, state, hard=True):
    index = fc.entry_point(entry).main_event
    rewards, display = [], False
    while index != evfl.NONE:
        event = fc.events[index]
        if isinstance(event, evfl.SwitchEvent):
            name = event.params["GameDataName"]
            yes = hard if name == "MiniGame_HitTarget_IsHardMode" else state.get(name, False)
            index = dict(event.cases)[0 if yes else 1]
        elif isinstance(event, evfl.SubFlowEvent):
            if event.entry_point == "GetRupy_HitTarget":
                assert display
                rewards.append(event.params["GetRupee"])
            else:
                assert not display  # First gift must bypass the native rupee UI, not just the rupee grant.
                actor = event.params["ActorName"]
                rewards.append(20 if actor in {"Obj_Rupee_Red", "TBox_Rupee_Red"} else actor)
            index = event.next
        else:
            action = fc.actors[event.actor].actions[event.action]
            if action == gifts.SET_ACTION:
                state[event.params["GameDataName"]] = event.params["Value"]
            elif action == "Open":
                display = True
            else:
                assert display
                display = False
            index = event.next
    assert not display
    return rewards


def test_first_expert_prizes_are_independent_saved_and_not_consumed_by_normal_or_failed_games():
    fc = chart()
    cs = changes(fc)
    gifts.patch_flowchart(fc, FLOW, cs)
    fc = evfl.read(evfl.write(evfl.EventFlowFile(FLOW, flowchart=fc))).flowchart
    state = {}
    for event in gifts.GALLERY_EXPERT_ROUTES:
        assert run(fc, event, state, hard=False) == ["NativeNormalRepeat"]
    assert run(fc, "Lose", state) == []
    assert state == {}
    for event, native in gifts.GALLERY_EXPERT_RUPEES.items():
        assert run(fc, event, state) == ["Item_Boomerang"]
        state = dict(state)  # Reconstructed saved state, unrelated to current item ownership.
        assert run(fc, event, state) == [native]
        assert run(fc, "Lose", state) == []
    assert state == {c.flag: True for c in cs}


def test_unchanged_twenty_rupee_assignment_still_creates_saved_first_win_then_native_repeats():
    from clawshot.patch.items import load

    fc = chart()
    names = list(gifts.GALLERY_EXPERT_CHECKS.values())
    vanilla = dict.fromkeys(names, "Rupees (20)")
    step = gifts.seed_step(
        names,
        find_gifts({FLOW: fc}, {FLOW: "gallery.bfevfl"}),
        [],
        gifts.load(),
        load(),
        vanilla,
        {FLOW: "gallery.bfevfl"},
    )
    transforms = step(vanilla)
    data = evfl.write(evfl.EventFlowFile(FLOW, flowchart=fc))
    fc = evfl.read(transforms["gallery.bfevfl"](data)).flowchart
    state = {}
    for event, native in gifts.GALLERY_EXPERT_RUPEES.items():
        assert run(fc, event, state) == [20]
        assert run(fc, event, dict(state)) == [native]


def test_held_experts_are_selectable_with_fixed_twenty_pool_only_after_hold_removed():
    from clawshot.generate import Settings, prepare
    from clawshot.patch.items import load
    from clawshot.world.load import load_spec

    spec = load_spec()
    settings = Settings(shuffle=gifts.GIFT_TYPES)
    census = find_gifts({FLOW: chart()}, {FLOW: "gallery.bfevfl"})
    _, world = prepare(spec, settings)
    assert gifts.seed_checks(world, census, [], gifts.load(), load()) == []
    for name in gifts.GALLERY_EXPERT_CHECKS.values():
        assert world.locations[name].vanilla == "Rupees (20)"
        del spec["locations"][name]["keep_vanilla"]
    _, world = prepare(spec, settings)
    assert set(gifts.seed_checks(world, census, [], gifts.load(), load())) == set(gifts.GALLERY_EXPERT_CHECKS.values())


def test_changed_native_expert_dispatch_refuses_with_values():
    fc = chart()
    cs = changes(fc)
    fc.events[2].params["GetRupee"] = 1
    with pytest.raises(gifts.GiftPatchError, match="stale expert reward dispatch.*GetRupee.*1"):
        gifts.patch_flowchart(fc, FLOW, cs)
