"""The first stick and nut bags come with sticks and nuts (clawshot.patch.bags), on a synthetic GetPouchContent."""

import pytest

from clawshot.formats import evfl
from clawshot.patch import bags
from clawshot.patch.plan import PatchError


def flow():
    fc = evfl.Flowchart(
        bags.FLOW,
        actors=[
            evfl.Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"]),
            evfl.Actor("GameDataActor", actions=["EventTriggerCopyGameDataInt"], queries=["EventQueryIsBool"]),
        ],
        events=[
            evfl.ActionEvent(
                "Event0",
                0,
                0,
                2,
                {
                    "Num": 1,
                    "IsEquipDIrect": False,
                    "IsSetMessageTargetActorName": True,
                    "Actor": evfl.Argument("ActorName"),
                    "IsGetEvent": evfl.Argument("IsGetInEvent"),
                },
            ),
            evfl.SubFlowEvent("Event82", "", "OpenRupeeUIIfNeed", 0),
            evfl.ActionEvent("Event83", 1, 0),
        ],
        entry_points=[evfl.EntryPoint("GetPouchContent", 1)],
    )
    return evfl.EventFlowFile(bags.FLOW, flowchart=fc)


def walk(fc, content, held):
    """Run the flow from its entry point; returns the pouch adds made."""
    index = fc.entry_points[0].main_event
    strings, adds = {}, []
    for _ in range(200):
        if index == evfl.NONE:
            return adds
        event = fc.events[index]
        if isinstance(event, evfl.SubFlowEvent):
            index = event.next
            continue
        actor = fc.actors[event.actor]
        if isinstance(event, evfl.SwitchEvent):
            query = actor.queries[event.query]
            if query == "EventQueryIsGameDataString64":
                true = strings[event.params["GameDataName"]] == event.params["Value"]
            else:
                assert query == "EventQueryIsExistInPouch"
                true = event.params["Actor"] in held
            index = dict(event.cases)[0 if true else 1]  # case 0 is "yes", as the game's own gates
            continue
        action = actor.actions[event.action]
        if action == "EventTriggerSetGameDataString64":
            strings[event.params["GameDataName"]] = content
        elif action == "EventTriggerAddOrRemovePouchContent":
            added = content if event.params["Actor"] == evfl.Argument("ActorName") else event.params["Actor"]
            adds.append(added)
            held.add(added)
        index = event.next
    raise AssertionError("the flow loops")


def patched():
    document = flow()
    bags.patch_flow(document.flowchart)
    return evfl.read(evfl.write(document)).flowchart


def test_sticks_and_nuts_bring_their_first_bag_once():
    fc = patched()
    assert walk(fc, "Item_DekuStickBundle_Small", set()) == ["Item_StickBag_Small", "Item_DekuStickBundle_Small"]
    assert walk(fc, "TBox_DekuNutBundle", set()) == ["Item_NutBag_Small", "TBox_DekuNutBundle"]
    assert walk(fc, "Item_DekuStick", {"Item_StickBag_Small"}) == ["Item_DekuStick"]
    # A capacity upgrade found first is kept: no small bag over it.
    assert walk(fc, "Item_DekuNut", {"Item_NutBag_Medium"}) == ["Item_DekuNut"]
    assert walk(fc, "Item_Boomerang", set()) == ["Item_Boomerang"]


def test_the_slingshot_and_bow_bring_their_bag_and_ammo_brings_none():
    fc = patched()
    assert walk(fc, "Item_Range_SlingShot", set()) == ["Item_BulletBag_Small", "Item_Range_SlingShot"]
    assert walk(fc, "Item_Range_Bow", set()) == ["Item_Quiver_Small", "Item_Range_Bow"]
    assert walk(fc, "Item_Range_Bow", {"Item_Quiver_Large"}) == ["Item_Range_Bow"]
    assert walk(fc, "TBox_ArrowBundle_Small", set()) == ["TBox_ArrowBundle_Small"]  # arrows wait for the Bow
    assert walk(fc, "TBox_DekuSeedBundle", set()) == ["TBox_DekuSeedBundle"]


def test_the_edit_refuses_a_changed_flow():
    document = flow()
    bags.patch_flow(document.flowchart)
    with pytest.raises(PatchError, match="already"):
        bags.patch_flow(document.flowchart)
    changed = flow()
    changed.flowchart.events[0].params["Actor"] = "Item_Boomerang"
    with pytest.raises(PatchError, match="no longer"):
        bags.patch_flow(changed.flowchart)
