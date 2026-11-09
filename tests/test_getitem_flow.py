"""Chest display dispatch must never replace the actual item grant or equipment actor."""

import copy

import pytest

from clawshot.formats import evfl
from clawshot.patch import getitem
from clawshot.patch.plan import PatchError


def prop_template():
    return evfl.Actor("Dm_Item_Ocarina_Time", params={"EventMemberCreateMethod": 1})


def chest(flow):
    actions = ["EventTriggerPlayerNoHit", "EventTriggerModelBindForItemGetDemo", "EventPlayAS"]
    if flow == "Dm_SY_Treasurebox":
        actions = [actions[2], actions[0], actions[1]]
    fc = evfl.Flowchart(
        flow,
        actors=[
            evfl.Actor("PouchContentGuestPerformer", actions=actions),
            evfl.Actor("TreasureBox_EventStarter", actions=["EventTriggerTBoxRequestSleepActorHolderData"]),
            evfl.Actor("GameDataActor"),
            evfl.Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"]),
        ],
        events=[
            evfl.ActionEvent("Before", 1, 0, 1),
            *[evfl.ActionEvent(f"Display{i}", 0, i, i + 2) for i in range(3)],
            evfl.ActionEvent("Grant", 3, 0, 5, {"Actor": evfl.Argument("ContentName"), "Num": 1}),
            evfl.ActionEvent("Sleep", 1, 0),
        ],
        entry_points=[evfl.EntryPoint("Display", 1)],
    )
    # The display predecessor is deliberately a different action, not a second sleep.
    fc.actors[1].actions.append("BeforeDisplay")
    fc.events[0].action = 1
    fc.entry_points[0].main_event = 0
    return evfl.EventFlowFile(flow, flowchart=fc)


def walk(fc, item):
    """Execute the straight-line native fixture and the real added String64 switches."""
    index = fc.entry_points[0].main_event
    strings = {}
    observed = []
    while index != evfl.NONE:
        event = fc.events[index]
        actor = fc.actors[event.actor]
        if isinstance(event, evfl.SwitchEvent):
            assert actor.queries[event.query] == "EventQueryIsGameDataString64"
            index = dict(event.cases)[0 if strings[event.params["GameDataName"]] == event.params["Value"] else 1]
            continue
        action = actor.actions[event.action]
        if action == "EventTriggerSetGameDataString64":
            assert event.params["Value"] == evfl.Argument("ContentName")
            strings[event.params["GameDataName"]] = item
        else:
            observed.append((actor.name, action, event.params))
        index = event.next
    return observed


@pytest.mark.parametrize("flow", getitem.CHEST_FLOWS)
@pytest.mark.parametrize("item", [*getitem.OCARINAS, "Item_Boomerang", "Item_Melody_EponaSong"])
def test_chest_presentation_uses_only_selected_prop_and_keeps_native_grant(flow, item):
    original = chest(flow)
    data = evfl.write(original)
    changed = evfl.read(getitem.patch_chest_flow(data, prop_template=prop_template())).flowchart
    observed = walk(changed, item)
    grant = (
        "PouchSystemActor",
        "EventTriggerAddOrRemovePouchContent",
        {"Actor": evfl.Argument("ContentName"), "Num": 1},
    )
    assert observed.count(grant) == 1
    if item not in getitem.OCARINAS:
        assert observed == walk(original.flowchart, item)
    else:
        props = [(a, action, params) for a, action, params in observed if a.startswith("Dm_")]
        assert [(a, action) for a, action, _ in props] == [
            ("Dm_" + item, "EventTriggerParticipateEvent"),
            ("Dm_" + item, "EventTriggerModelBind"),
            ("Dm_" + item, "EventGoOffstageForUser"),
        ]
        assert props[1][2]["ActorName"] == "Player_Event"
        assert props[1][2]["BoneName"] == "Weapon_L"
        assert observed.index(props[1]) < observed.index(grant) < observed.index(props[2])
        assert not any(a == "PouchContentGuestPerformer" for a, _, _ in observed)
    assert original == evfl.read(data)


@pytest.mark.parametrize("flow", getitem.CHEST_FLOWS)
def test_changed_native_display_chain_is_refused_before_output(flow):
    original = chest(flow)
    original.flowchart.events[2].next = 4
    data = evfl.write(original)
    with pytest.raises(PatchError, match="chain changed"):
        getitem.patch_chest_flow(data, prop_template=prop_template())
    assert evfl.read(data) == original


def test_reapplying_presentation_patch_is_refused():
    data = evfl.write(chest(getitem.CHEST_FLOWS[0]))
    template = prop_template()
    before = copy.deepcopy(template)
    changed = getitem.patch_chest_flow(data, prop_template=template)
    with pytest.raises(PatchError, match="already patched"):
        getitem.patch_chest_flow(changed, prop_template=template)
    assert template == before
