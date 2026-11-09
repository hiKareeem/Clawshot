"""Synthetic purchases: refusing is not collecting; saved checks are independent of stock ownership."""

from clawshot.census.gifts import Gift
from clawshot.formats import evfl
from clawshot.patch import gifts


def chart(flow_name, rows, entries):
    """Build synthetic nodes by label, never from a decoded game fixture."""
    index = {name: i for i, (name, *_) in enumerate(rows)}
    events = []
    for name, kind, target, params in rows:
        if kind == "choice":
            events.append(evfl.SwitchEvent(name, 2, 0, [(k, index[v]) for k, v in target], params))
        elif kind in ("funds", "capacity", "bottle"):
            events.append(
                evfl.SwitchEvent(
                    name, 1, ("funds", "capacity", "bottle").index(kind), [(k, index[v]) for k, v in target], params
                )
            )
        elif kind in ("charge", "take"):
            events.append(
                evfl.ActionEvent(name, 1, ("charge", "take").index(kind), index.get(target, evfl.NONE), params)
            )
        elif kind == "save":
            events.append(evfl.ActionEvent(name, 0, 0, index.get(target, evfl.NONE), params))
        elif kind == "end":
            events.append(evfl.ActionEvent(name, 2, 0))
        else:
            flow, entry = kind.split(":")
            events.append(evfl.SubFlowEvent(name, flow, entry, index.get(target, evfl.NONE), params))
    return evfl.Flowchart(
        name=flow_name,
        actors=[
            evfl.Actor("GameDataActor", actions=[gifts.SET_ACTION], queries=[gifts.READ_QUERY]),
            evfl.Actor(
                "PouchSystemActor",
                actions=["EventTriggerAddGameDataIntToRupee", "EventTriggerAddOrRemovePouchContent"],
                queries=["EventQueryHasRuppe", "EventQueryCanAddToPorch", "EventQueryIsAnyBottleEmpty"],
            ),
            evfl.Actor("GameSystemActor", actions=["EventTriggerRequestAutoSave"], queries=["EventQueryTalkChoice2"]),
        ],
        events=events,
        entry_points=[evfl.EntryPoint(e, index[n]) for e, n in entries],
    )


def shops():
    rows = []
    entries = []
    for root, suffix, grant in (
        ("SimpleShopRoot", "C", "Event124"),
        ("SimpleShopRoot_Npc_Goron_Medigoron_Adult", "M", "Event119"),
    ):
        entries.append((root, "Choice" + suffix))
        rows.extend(
            [
                (
                    "Choice" + suffix,
                    "choice",
                    [(0, "Funds" + suffix), (1, "Event26" if suffix == "C" else "Event116")],
                    None,
                ),
                (
                    "Funds" + suffix,
                    "funds",
                    [(0, "Capacity" + suffix), (1, "Cancel")],
                    {"Value": evfl.Argument("Price")},
                ),
                (
                    "Capacity" + suffix,
                    "capacity",
                    [(0, grant if suffix == "C" else "ChargeM"), (2, "Cancel")],
                    {"Actor": evfl.Argument("ActorName")},
                ),
            ]
        )
    rows.extend(
        [
            ("Event26", ":Sub_ShopCancel", None, {}),
            ("Event116", ":Sub_ShopCancel", None, {}),
            ("Cancel", "end", None, None),
            ("Event124", ":Sub_SimpleShop_Buy", None, {"ActorName": evfl.Argument("ActorName")}),
            ("ChargeM", "charge", "Event119", {"IsSignInverse": True, "GameDataName": "SimpleShop_Price"}),
            (
                "Event119",
                "Dm_SY_GetInEvent:GetInEventItemSwordMedigoron",
                "Event25",
                {"ActorName": evfl.Argument("ActorName")},
            ),
            ("Event25", "take", "Event62", {"Actor": "Weapon_Sword_BrokenGiant", "Num": -1}),
            ("Event62", "end", None, None),
            ("ChargeC", "charge", "Event150", {"IsSignInverse": True, "GameDataName": "SimpleShop_Price"}),
            (
                "Event150",
                "NpcCommon:NpcCommon_HandOver_NpcToPlayer_NoTurn_NoWaitAS",
                "Event222",
                {"ReceiveItem": evfl.Argument("ActorName")},
            ),
            ("Event222", "save", None, {"GameDataName": "Npc_Hylia_044_Buy", "Value": True}),
        ]
    )
    entries.extend([("Sub_ShopCancel", "Cancel"), ("Sub_SimpleShop_Buy", "ChargeC")])
    fc = chart("SimpleShop", rows, entries)
    fc.name = "SimpleShop"
    return fc


def granny():
    fc = chart(
        "Npc_Hylia_053_Adult",
        [
            ("Choice", "choice", [(0, "Funds"), (1, "Cancel")], None),
            ("Funds", "funds", [(0, "Bottle"), (1, "Cancel")], {"Value": 100}),
            ("Bottle", "bottle", [(0, "Event12"), (1, "Cancel")], {}),
            (
                "Event12",
                "Dm_SY_GetInEvent:GetInEventInBottle_BlueBottleShop",
                None,
                {"ActorName": "Item_Bottle_BluePotion", "BottleItem": 2},
            ),
            ("Cancel", "end", None, None),
        ],
        [("Buy_BluePotion", "Choice")],
    )
    fc.name = "Npc_Hylia_053_Adult"
    return fc


def change(check, flow, event, item):
    step = Gift(flow + "/" + event, "npc_gift", flow, "synthetic", (), event, "", "ActorName", item, "")
    return gifts.GiftChange(gifts.Rule(check, gifts.REWRITE, purchase=True), (step,), "Item_" + event)


def run(fc, entry, state, received, *, choice=0, capacity=0, bottle=True, args=None):
    args = args or {}
    index = fc.entry_point(entry).main_event
    while index != evfl.NONE:
        event = fc.events[index]
        params = {k: args[str(v)] if isinstance(v, evfl.Argument) else v for k, v in (event.params or {}).items()}
        if isinstance(event, evfl.SwitchEvent):
            query = fc.actors[event.actor].queries[event.query]
            if query == gifts.READ_QUERY:
                case = 0 if state.get(params["GameDataName"], False) else 1
            elif query == "EventQueryTalkChoice2":
                case = choice
            elif query == "EventQueryHasRuppe":
                case = 0 if state["rupees"] >= params["Value"] else 1
            elif query == "EventQueryCanAddToPorch":
                case = capacity
            elif query == "EventQueryIsAnyBottleEmpty":
                case = 0 if bottle else 1
            else:
                raise AssertionError(query)
            index = dict(event.cases)[case]
            continue
        if isinstance(event, evfl.SubFlowEvent):
            if event.flowchart == "Dm_SY_GetInEvent":
                received.append(params["ActorName"])
            elif event.flowchart == "NpcCommon":
                received.append(params["ReceiveItem"])
            else:
                run(
                    fc, event.entry_point, state, received, choice=choice, capacity=capacity, bottle=bottle, args=params
                )
        else:
            action = fc.actors[event.actor].actions[event.action]
            if action == gifts.SET_ACTION:
                state[params["GameDataName"]] = params["Value"]
            elif action == "EventTriggerAddGameDataIntToRupee":
                state["rupees"] -= state[params["GameDataName"]]
            elif action == "EventTriggerAddOrRemovePouchContent":
                state[params["Actor"]] = state.get(params["Actor"], 0) + params["Num"]
            elif action != "EventTriggerRequestAutoSave":
                raise AssertionError(action)
        index = event.next


def test_private_shop_purchases_refuse_without_collecting_then_charge_once_across_reload():
    fc = shops()
    changes = [
        change("GC Medigoron", "Npc_Goron_Medigoron_Adult", "Event11", "Shop_Sword_Giant"),
        change("Wasteland Bombchu Salesman", "Npc_Hylia_044_Adult", "Event3", "Shop_BombchuBundle_01"),
    ]
    gifts.patch_flowchart(fc, fc.name, changes)
    fc = evfl.read(evfl.write(evfl.EventFlowFile(fc.name, flowchart=fc))).flowchart
    state, received = {"rupees": 500, "Weapon_Sword_BrokenGiant": 1}, []
    for purchase, price in zip(changes, (200, 90), strict=True):
        entry = gifts.NEW_EVENT_PREFIX + "Purchase" + purchase.steps[0].flow
        state["SimpleShop_Price"] = price
        args = {"Price": price, "ActorName": purchase.item}
        for refusal in ({"choice": 1}, {"capacity": 2}):
            before = dict(state)
            run(fc, entry, state, received, args=args, **refusal)
            assert state == before and purchase.item not in received
        state["rupees"] = price - 1
        before = dict(state)
        run(fc, entry, state, received, args=args)
        assert state == before and purchase.item not in received
        state["rupees"] = 500
        run(fc, entry, state, received, args=args)
        assert state["rupees"] == 500 - price and state[purchase.flag] is True
        assert received.count(purchase.item) == 1
        saved = {k: v for k, v in state.items() if k != "Npc_Hylia_044_Buy"}
        before = dict(saved)
        run(fc, entry, saved, received, args=args)
        assert saved == before and received.count(purchase.item) == 1
    assert state["Weapon_Sword_BrokenGiant"] == 1
    # The original sale remains repeatable for every untouched consumer.
    original, rewards = {"rupees": 500, "SimpleShop_Price": 90}, []
    for _ in range(2):
        run(fc, "SimpleShopRoot", original, rewards, args={"Price": 90, "ActorName": "NativeStock"})
    assert rewards == ["NativeStock", "NativeStock"] and original["rupees"] == 320


def test_granny_preserves_refusal_funds_and_bottle_gates_and_charges_only_success():
    fc = granny()
    purchase = change(gifts.GRANNY_CHECK, fc.name, "Event12", "Item_Bottle_BluePotion")
    gifts.patch_flowchart(fc, fc.name, [purchase])
    fc = evfl.read(evfl.write(evfl.EventFlowFile(fc.name, flowchart=fc))).flowchart
    state, rewards = {"rupees": 200, "SimpleShop_Price": 100}, []
    for refusal in ({"choice": 1}, {"bottle": False}):
        before = dict(state)
        run(fc, "Buy_BluePotion", state, rewards, **refusal)
        assert state == before and rewards == []
    state["rupees"] = 99
    run(fc, "Buy_BluePotion", state, rewards)
    assert state["rupees"] == 99 and purchase.flag not in state and rewards == []
    state["rupees"] = 200
    run(fc, "Buy_BluePotion", state, rewards)
    assert state["rupees"] == 100 and state[purchase.flag] is True and rewards == [purchase.item]
    saved = dict(state)
    run(fc, "Buy_BluePotion", saved, rewards)
    assert saved == state and rewards == [purchase.item]
