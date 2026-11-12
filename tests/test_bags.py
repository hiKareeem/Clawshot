"""The first stick and nut bags come with sticks and nuts (clawshot.patch.bags), on a synthetic GetPouchContent."""

import pytest

from clawshot.census.gifts import DIRECT, Gift
from clawshot.formats import evfl
from clawshot.patch import bags, gifts
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


def walk(fc, content, held, *, entry=None, flags=None, trace=None):
    """Run a synthetic entry, retaining inventory checks, quantities and once flags."""
    index = next(ep.main_event for ep in fc.entry_points if entry is None or ep.name == entry)
    strings, adds = {}, []
    flags = set() if flags is None else flags
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
            elif query == "EventQueryIsGameDataBool":
                true = event.params["GameDataName"] in flags
            else:
                assert query == "EventQueryIsExistInPouch"
                true = event.params["Actor"] in held
            index = dict(event.cases)[0 if true else 1]  # case 0 is "yes", as the game's own gates
            continue
        action = actor.actions[event.action]
        if action == "EventTriggerSetGameDataString64":
            value = event.params["Value"]
            strings[event.params["GameDataName"]] = content if isinstance(value, evfl.Argument) else value
        elif action == "EventTriggerSetGameDataBool":
            name = event.params["GameDataName"]
            flags.add(name) if event.params["Value"] else flags.discard(name)
        elif action == "EventTriggerAddOrRemovePouchContent":
            value = event.params["Actor"]
            added = content if isinstance(value, evfl.Argument) else value
            adds.append(added)
            if event.params["Num"] > 0:
                held.add(added)
            elif event.params["Num"] < 0:
                held.discard(added)
            if trace is not None:
                trace.append(
                    (
                        added,
                        event.params["Num"],
                        event.params.get("IsEquipDIrect"),
                        event.params.get("IsSetMessageTargetActorName"),
                        event.params.get("IsGetEvent"),
                    )
                )
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


@pytest.mark.parametrize(
    ("event", "entry", "get_event", "content", "bag"),
    [
        ("Event124", "GetInEvent_Goron", False, "Item_Range_SlingShot", "Item_BulletBag_Small"),
        ("Event430", "GetInEvent_NotTurn_2DShop", True, "Weapon_Range_Bow", "Item_Quiver_Small"),
        ("Event442", "DekuShield_GetAndEquipCheck", False, "Item_DekuNut", "Item_NutBag_Small"),
    ],
)
def test_direct_handovers_get_missing_bag_only_after_success(event, entry, get_event, content, bag):
    document = flow()
    fc = document.flowchart
    document.name = fc.name = bags.HANDOVER_FLOW
    fc.events[0].name = event
    fc.events[0].params["IsGetEvent"] = get_event
    fc.actors[1].queries.append("EventQueryIsGameDataBool")
    fc.events.append(
        evfl.SwitchEvent("MayReceive", 1, 1, [(0, 1), (1, evfl.NONE)], {"GameDataName": "PurchaseSucceeded"})
    )
    fc.entry_points = [evfl.EntryPoint(entry, 3), evfl.EntryPoint("Cancelled", evfl.NONE)]
    fc = evfl.read(bags.handover_transform(evfl.write(document))).flowchart
    trace = []
    assert walk(fc, content, set(), entry=entry, flags={"PurchaseSucceeded"}, trace=trace) == [bag, content]
    assert trace == [(bag, 1, False, False, False), (content, 1, False, True, get_event)]
    large = next(tiers[-1] for _, tiers in bags.FAMILIES.values() if tiers[0] == bag)
    assert walk(fc, content, {large}, entry=entry, flags={"PurchaseSucceeded"}) == [content]
    assert walk(fc, content, set(), entry=entry) == []  # refused/shortfall
    assert walk(fc, content, set(), entry="Cancelled") == []


def test_literal_shuffled_gift_keeps_bundle_message_equip_and_once_behavior():
    document = flow()
    fc = document.flowchart
    document.name = fc.name = "Npc_Synthetic"
    fc.events[0].params.update({"Actor": "Item_Old", "Num": 3, "IsEquipDIrect": True, "IsGetEvent": False})
    fc.actors[1].actions[0] = "EventTriggerSetGameDataBool"
    fc.actors[1].queries[0] = "EventQueryIsGameDataBool"
    fc.events[2].params = {"GameDataName": "GiftDone", "Index": -1, "Value": True}
    fc.events.append(evfl.SwitchEvent("Given", 1, 0, [(0, evfl.NONE), (1, 1)], {"GameDataName": "GiftDone"}))
    fc.entry_points = [evfl.EntryPoint("Talk", 3)]
    step = Gift(
        f"{fc.name}/Event0", "npc_gift", fc.name, "synthetic", ("Talk",), "Event0", DIRECT, "Actor", "Item_Old", ""
    )
    change = gifts.GiftChange(gifts.Rule("Direct gift", "swap"), (step,), "Item_DekuStick")
    fc = evfl.read(gifts.flow_transform(fc.name, (change,))(evfl.write(document))).flowchart
    trace, flags, held = [], set(), set()
    assert walk(fc, None, held, flags=flags, trace=trace) == ["Item_StickBag_Small", "Item_DekuStick"]
    assert trace == [("Item_StickBag_Small", 1, False, False, False), ("Item_DekuStick", 3, True, True, False)]
    assert flags == {"GiftDone"}
    assert walk(fc, None, held, flags=flags) == []


@pytest.mark.parametrize(
    ("content", "amount"),
    [("Item_DekuStick", -1), ("Item_DekuNut", 0), ("Item_Arrow_Normal", 5), ("Item_Quiver_Medium", 1)],
)
def test_literal_removals_zero_ammo_and_bag_only_grants_do_not_gain_companions(content, amount):
    document = flow()
    fc = document.flowchart
    fc.events[0].params.update({"Actor": content, "Num": amount})
    bags.patch_grants(fc, literal_only=True)
    assert walk(evfl.read(evfl.write(document)).flowchart, None, set()) == [content]


def test_literal_grant_without_existing_game_data_actor():
    fc = evfl.Flowchart(
        "Npc_Synthetic",
        actors=[evfl.Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"])],
        events=[evfl.ActionEvent("Give", 0, 0, params={"Actor": "Weapon_Range_SlingShot", "Num": 1})],
        entry_points=[evfl.EntryPoint("Talk", 0)],
    )
    bags.patch_grants(fc, literal_only=True)
    assert walk(fc, None, set()) == ["Item_BulletBag_Small", "Weapon_Range_SlingShot"]
