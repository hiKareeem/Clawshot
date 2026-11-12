"""Synthetic event execution: source lifecycle, target attribution, native controls."""

import copy

import pytest

from clawshot import patch as patch_api
from clawshot.census.gifts import FLOW_VERSIONS
from clawshot.formats import byml, evfl, msbt, sarc, zsdic
from clawshot.generate import Settings
from clawshot.patch import key_text, keys, text
from clawshot.patch.key_targets import DungeonGrant
from clawshot.patch.key_text import labels
from clawshot.patch.plan import ChestChange, Plan
from clawshot.save import key as save_key

GET_TEXT = ["EventFlowMsg/Dm_SY_Get:GetMessage", "EventFlowMsg/Dm_SY_Get:GetCaption"]
# The four shared dungeon-item actors, in the big chest's dispatch order (cases 0-3; r13-dungeon-items.md).
ITEMS = {
    "Map": "Item_Dungeon_Map",
    "Compass": "Item_Dungeon_Compass",
    "BossKey": "Item_Dungeon_BossKey",
    "SmallKey": "Item_Dungeon_SmallKey",
}
FIXTURE_TARGETS = ("ForestTemple", "FireTemple", "InsideTheDekuTree")
DUNGEON_FIELDS = {
    "SmallKeyNum": 0,
    "SmallKeyTotalNum": 0,
    "IsGetSmallKeyOnce": False,
    "IsGetBossKey": False,
    "IsGetMap": False,
    "IsGetCompass": False,
}
FLAGS = ("UI_RequestSmallKeyCountUpDemo", "MidoStart", "MapFollowUp", "StoryAfter")
PRESENTATION = {
    "EventTriggerParticipateEvent",
    "EventTriggerSetDisplayBossKey",
    "EventTriggerRequestOpenPickUpWindow",
    "EventTriggerRequestAutoSave",
    "EventWait",
}


def native_small_key(state, target, delta=1):
    """The native counter routine (r11-keys.md): first-key flag at zero, total on grants, refused underflow."""
    remaining = f"DungeonInfo.{target}.SmallKeyNum"
    if state[remaining] + delta < 0:
        return False
    if delta > 0:
        if state[remaining] == 0:
            state[f"DungeonInfo.{target}.IsGetSmallKeyOnce"] = True
        state[f"DungeonInfo.{target}.SmallKeyTotalNum"] += delta
    state[remaining] += delta
    return True


def _document(name, actors, events, entries):
    return evfl.EventFlowFile(name, evfl.Flowchart(name, actors, events, entries))


def _content(name="ContentName"):
    return {"ActorName": evfl.Argument(name)}


def _success_arguments():
    return {"ContentName": evfl.Argument("ContentName"), "IsMiniGame": False}


def key_sources():
    """Native-shaped chest paths: the big chest's four explicit dungeon-item actions, the small chest's pouch grant."""
    pouch = _document(
        keys.POUCH,
        [
            evfl.Actor(
                "PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent", "EventTriggerSetForGetWindow"]
            ),
            evfl.Actor("GameDataActor"),
            evfl.Actor("SystemTextNPC", actions=["EventTalk"]),
            evfl.Actor("GameSystemActor", actions=["EventTriggerRequestAutoSave"]),
        ],
        [
            # Native Event0 stores the grant; the display entry still sets the
            # get window and text before returning to that grant.
            evfl.ActionEvent(
                "Grant", 0, 0, 5, {"Num": 1, "IsSetMessageTargetActorName": True, "Actor": evfl.Argument("ActorName")}
            ),
            evfl.ActionEvent("Message", 2, 0, 2, {"MessageId": GET_TEXT[0]}),
            evfl.ActionEvent("Caption", 2, 0, evfl.NONE, {"MessageId": GET_TEXT[1]}),
            evfl.SubFlowEvent("Display", "", "DisplayGetByActorName", 0, _content("ActorName")),
            evfl.ActionEvent("Window", 0, 1, 1, {"Actor": evfl.Argument("ActorName")}),
            evfl.ActionEvent("AutoSave", 3, 0),
        ],
        [
            evfl.EntryPoint("GetPouchContentByActorNameForTreasureBox", 3, [3]),
            evfl.EntryPoint("DisplayGetByActorName", 4),
        ],
    )
    big = _document(
        keys.BIG,
        [
            evfl.Actor("GameSystemActor", actions=[f"EventGetDungeon{family}" for family in ITEMS]),
            evfl.Actor("TreasureBox_EventStarter", queries=["EventQueryTreasureBoxIsDungeonCommonItemInside"]),
            evfl.Actor(
                "UISystemActor", actions=["EventTriggerSetDisplayBossKey", "EventTriggerRequestOpenPickUpWindow"]
            ),
        ],
        [
            evfl.SwitchEvent("Event19", 1, 0, [(0, 1), (1, 1), (2, 1), (3, 1), (4, 8)], _content()),
            evfl.SubFlowEvent("Event34", keys.POUCH, "DisplayGetByActorName", 2, _content()),
            evfl.SwitchEvent("Event32", 1, 0, [(0, 3), (1, 4), (2, 5), (3, 6), (4, 8)], _content()),
            evfl.ActionEvent("Event23", 0, 0, 9, {"IsWaitEnd": True}),
            evfl.ActionEvent("Event26", 0, 1, 9, {"IsWaitEnd": True}),
            evfl.ActionEvent("Event27", 0, 2, 7, {"IsWaitEnd": True}),
            evfl.ActionEvent("Event30", 0, 3, 9, {"IsWaitEnd": True}),
            evfl.ActionEvent("Event82", 2, 0, 9, {"IsDisplayBossKey": True}),
            evfl.SubFlowEvent("Event90", keys.POUCH, "GetPouchContentByActorNameForTreasureBox", params=_content()),
            evfl.ActionEvent("Event21", 2, 1, params=_content()),
        ],
        [evfl.EntryPoint("Success", 0, [1, 8])],
    )
    small = _document(
        keys.SMALL,
        [
            evfl.Actor("GameDataActor", actions=["EventTriggerSetGameDataBool"]),
            evfl.Actor("GameSystemActor", actions=["EventWait"]),
            evfl.Actor("UISystemActor", actions=["EventTriggerRequestOpenPickUpWindow"]),
        ],
        [
            evfl.SubFlowEvent(
                "Grant",
                keys.POUCH,
                "GetPouchContentByActorNameForTreasureBox",
                next=5,
                params={"ActorName": evfl.Argument("ContentName"), "IsMiniGame": evfl.Argument("IsMiniGame")},
            ),
            evfl.ActionEvent("MidoStart", 0, 0, 2, {"GameDataName": "MidoStart", "Value": True}),
            evfl.SubFlowEvent("MidoContent", "", "Success_", params=_success_arguments()),
            evfl.ActionEvent("DefaultStart", 0, 0, 4, {"GameDataName": "MidoStart", "Value": False}),
            evfl.SubFlowEvent("DefaultContent", "", "Success_", params=_success_arguments()),
            evfl.ActionEvent("SmallPickUpWindow", 2, 0, params=_content()),
        ],
        [
            evfl.EntryPoint("Success", 3, [4]),
            evfl.EntryPoint("Success_", 0, [0]),
            evfl.EntryPoint("Success_MidoHouse", 1, [2]),
        ],
    )
    navi = _document(
        "NaviChat",
        [
            evfl.Actor("Player_Event", actions=["EventTriggerParticipateEvent"]),
            evfl.Actor("EventSystemActor", actions=["EventTransition"]),
            evfl.Actor("GameDataActor", actions=["EventTriggerSetGameDataBool"]),
            evfl.Actor("Npc_Navi", actions=["EventNaviRequestBallonMessage"]),
        ],
        [
            evfl.ActionEvent("Participate", 0, 0, 1),
            evfl.ActionEvent("Transition", 1, 0, evfl.NONE, {"EventName": keys.BIG, "SpecialEventActionType": 1}),
            evfl.SubFlowEvent("MapDemo", "", "PlayDemo", 3),
            evfl.ActionEvent("MapFollowUp", 2, 0, 4, {"GameDataName": "MapFollowUp", "Value": True}),
            evfl.ActionEvent("ItemBalloon", 3, 0, 5, {"Index": 354}),
            evfl.ActionEvent("StoryAfter", 2, 0, 6, {"GameDataName": "StoryAfter", "Value": True}),
            evfl.ActionEvent("StoryBalloon", 3, 0, evfl.NONE, {"Index": 197}),
        ],
        [evfl.EntryPoint("PlayDemo", 0), evfl.EntryPoint("Map", 2, [2])],
    )
    documents = {doc.flowchart.name: doc for doc in (pouch, big, small, navi)}
    rows = [
        {
            "__RowId": name,
            "FlowchartFileName": f"Work/Event/EventFlow/{flow}.evfc",
            "EntryPointName": entry,
            "Camera": camera,
        }
        for name, flow, entry, camera in [
            (keys.BIG, keys.BIG, "Success", "BigCamera"),
            (keys.SMALL, keys.SMALL, "Success", ""),
            ("InsideTheDekuTree_GetMap", "NaviChat", "Map", ""),
            ("KokiriForest_TreasureBox_NaviChatOff", keys.SMALL, "Success_MidoHouse", ""),
        ]
    ]
    return documents, sorted(rows, key=lambda row: row["__RowId"])


def key_analysis(rows):
    return [
        {
            "__RowId": row["__RowId"],
            "SubFlowList": [] if row["__RowId"] == "InsideTheDekuTree_GetMap" else [keys.POUCH],
            "ChildEventList": [keys.BIG] if row["__RowId"] == "InsideTheDekuTree_GetMap" else [],
        }
        for row in rows
    ]


class KeyRun:
    """Executes the flows. Native dungeon-item handlers credit the dungeon Link stands in, as in the game."""

    def __init__(self, documents, rows, analyzed, content=ITEMS["SmallKey"], standing="InsideTheDekuTree"):
        self.documents = documents
        self.rows = {row["__RowId"]: row for row in rows}
        self.analyzed = {row["__RowId"]: row for row in analyzed}
        self.content = content
        self.standing = standing
        self.active = None
        self.state = {
            f"DungeonInfo.{target}.{field}": value
            for target in FIXTURE_TARGETS
            for field, value in DUNGEON_FIELDS.items()
        }
        self.state.update(dict.fromkeys(FLAGS, False))
        self.messages = []
        self.balloons = []
        self.trace = []
        self.windows = []  # the actors the get window was set for: its text names that item
        self.pouch = []  # generic pouch grants (their IsGet bit), never dungeon ownership for the three Bools
        self.stock = {}
        self.writes = []
        self.boss_display = False

    def observed(self):
        return copy.deepcopy(
            (
                self.state,
                self.messages,
                self.balloons,
                self.trace,
                self.windows,
                self.pouch,
                self.stock,
                self.writes,
                self.boss_display,
            )
        )

    def event(self, name):
        row = self.rows[name]
        flow = row["FlowchartFileName"].split("/")[-1].removesuffix(".evfc")
        analyzed = self.analyzed[name]
        if self.active:
            assert name in self.active[1]["ChildEventList"]
        prior = self.active
        self.active = (flow, analyzed)
        # A chest event's arguments come from the chest, not from the event that transitioned to it.
        self.entry(flow, row["EntryPointName"], {"ContentName": self.content, "IsMiniGame": False})
        self.active = prior

    def entry(self, flow, name, arguments):
        if self.active and flow != self.active[0]:
            assert flow in self.active[1]["SubFlowList"]
        chart = self.documents[flow].flowchart
        index = chart.entry_point(name).main_event
        while index != evfl.NONE:
            event = chart.events[index]
            params = {
                key: arguments[str(value)] if isinstance(value, evfl.Argument) else value
                for key, value in (event.params or {}).items()
            }
            if isinstance(event, evfl.SubFlowEvent):
                self.entry(event.flowchart or flow, event.entry_point, params)
                index = event.next
                continue
            actor = chart.actors[event.actor]
            if isinstance(event, evfl.SwitchEvent):
                operation = actor.queries[event.query]
                if operation == "EventQueryTreasureBoxIsDungeonCommonItemInside":
                    items = list(ITEMS.values())
                    result = items.index(params["ActorName"]) if params["ActorName"] in items else len(items)
                elif operation == "EventQueryIsGameDataString64":
                    result = 0 if self.state[params["GameDataName"]] == params["Value"] else 1
                elif operation == "EventQueryIsExistInPouch":
                    result = 0 if self.stock.get(params["Actor"], 0) >= params["Num"] else 1
                else:
                    assert operation == "EventQueryIsGameDataInt"
                    current = self.state[params["GameDataName"]]
                    result = 0 if current < params["Value"] else 1 if current == params["Value"] else 2
                index = dict(event.cases)[result]
                continue
            operation = actor.actions[event.action]
            self.trace.append(operation)
            if operation == "EventTransition":
                self.event(params["EventName"])
            elif operation == "EventTalk":
                self.messages.append(params["MessageId"])
            elif operation == "EventNaviRequestBallonMessage":
                self.balloons.append(params["Index"])
            elif operation == "EventTriggerSetGameDataBool":
                assert params["GameDataName"] in self.state, params
                self.state[params["GameDataName"]] = params["Value"]
                self.writes.append((params["GameDataName"], params["Value"]))
            elif operation == "EventTriggerAddOrSubGameDataInt":
                self.state[params["GameDataName"]] += params["Value"]
                self.writes.append((params["GameDataName"], params["Value"]))
            elif operation == "EventTriggerSetGameDataString64":
                self.state[params["GameDataName"]] = params["Value"]
            elif operation == "EventTriggerSetForGetWindow":
                self.windows.append(params["Actor"])
            elif operation == "EventTriggerAddOrRemovePouchContent":
                content = params["Actor"]
                self.pouch.append(content)
                self.stock[content] = self.stock.get(content, 0) + params["Num"]
                # Only the small key has a pouch special deal; the other three are NotPushToPouch (r11-keys.md).
                if content == ITEMS["SmallKey"]:
                    native_small_key(self.state, self.standing)
            elif operation.startswith("EventGetDungeon"):
                family = operation.removeprefix("EventGetDungeon")
                if family == "SmallKey":
                    native_small_key(self.state, self.standing)
                else:
                    self.state[f"DungeonInfo.{self.standing}.IsGet{family}"] = True
            elif operation == "EventTriggerSetDisplayBossKey":
                self.boss_display = params["IsDisplayBossKey"]
            else:
                assert operation in PRESENTATION, operation
            index = event.next


def compile_grants(requests):
    """Compile ``(source, DungeonGrant)`` requests; every written flow and table is read back from its transform."""
    documents, rows = key_sources()
    analyzed = key_analysis(rows)
    bindings, transforms = keys.compile_bindings(documents, rows, analyzed, requests)
    written = {
        name: evfl.read(transforms[keys.flow_path(name)](evfl.write(document)))
        if keys.flow_path(name) in transforms
        else document
        for name, document in documents.items()
    }
    new_rows = byml.read(transforms[keys.SETTINGS](byml.write(rows)))
    new_analyzed = byml.read(transforms[keys.ANALYZED](byml.write(analyzed)))
    return bindings, written, new_rows, new_analyzed, transforms


def _compile(requests):
    """Off-dungeon small keys, requested and looked up as ``(source, target)``."""
    named = [(source, DungeonGrant(target, "SmallKey", named=True)) for source, target in requests]
    bindings, *outputs = compile_grants(named)
    return {(source, grant.target): binding for (source, grant), binding in bindings.items()}, *outputs


@pytest.mark.parametrize("order", [(0, 1, 2, 3), (3, 0, 2, 1)])
def test_two_targets_both_sizes_do_not_cross_credit_or_replace_native_controls(order):
    requests = [
        (keys.SMALL, "ForestTemple"),
        (keys.BIG, "FireTemple"),
        (keys.SMALL, "FireTemple"),
        (keys.BIG, "ForestTemple"),
    ]
    bindings, documents, rows, analyzed, _ = _compile(requests)
    run = KeyRun(documents, rows, analyzed)
    for i in order:
        source, target = requests[i]
        before = run.state.copy()
        run.messages.clear()
        run.trace.clear()
        run.event(bindings[(source, target)].event)
        expected = before.copy()
        expected[f"DungeonInfo.{target}.SmallKeyNum"] += 1
        expected[f"DungeonInfo.{target}.SmallKeyTotalNum"] += 1
        expected[f"DungeonInfo.{target}.IsGetSmallKeyOnce"] = True
        assert run.state == expected
        assert run.messages == list(labels(target))
        assert run.trace.index("EventTriggerParticipateEvent") < run.trace.index("EventTransition")
        assert "EventGetDungeonSmallKey" not in run.trace
        assert "EventTriggerAddOrRemovePouchContent" not in run.trace
    run.event(keys.BIG)
    assert run.state["DungeonInfo.InsideTheDekuTree.SmallKeyNum"] == 1
    assert run.messages[-2:] == GET_TEXT


def test_source_specific_before_and_after_behavior_survives_named_handoffs():
    requests = [("InsideTheDekuTree_GetMap", "ForestTemple"), ("KokiriForest_TreasureBox_NaviChatOff", "FireTemple")]
    bindings, documents, rows, analyzed, _ = _compile(requests)
    run = KeyRun(documents, rows, analyzed)
    for request in requests:
        run.event(bindings[request].event)
    assert run.state["MapFollowUp"] is True
    assert run.state["MidoStart"] is True
    assert run.state["DungeonInfo.ForestTemple.SmallKeyNum"] == 1
    assert run.state["DungeonInfo.FireTemple.SmallKeyNum"] == 1
    assert run.state["DungeonInfo.InsideTheDekuTree.SmallKeyNum"] == 0


def test_native_non_key_pouch_path_does_not_call_named_helper():
    request = (keys.SMALL, "ForestTemple")
    _, documents, rows, analyzed, _ = _compile([request])
    run = KeyRun(documents, rows, analyzed)
    run.entry(keys.POUCH, "GetPouchContentByActorNameForTreasureBox", {"ActorName": "Rupee"})
    assert "EventTriggerAddOrRemovePouchContent" in run.trace
    assert run.messages == GET_TEXT
    assert run.state["DungeonInfo.ForestTemple.SmallKeyNum"] == 0


def test_equivalent_sources_share_binding_and_request_order_is_deterministic():
    requests = [(keys.BIG, "FireTemple"), (keys.SMALL, "ForestTemple")]
    a, _, _, _, transforms_a = _compile(requests)
    b, _, _, _, transforms_b = _compile([*reversed(requests), requests[0]])
    assert a == b
    docs, rows = key_sources()
    originals = {keys.flow_path(name): evfl.write(document) for name, document in docs.items()}
    originals[keys.SETTINGS] = byml.write(rows)
    originals[keys.ANALYZED] = byml.write(key_analysis(rows))
    assert {path: transform(originals[path]) for path, transform in transforms_a.items()} == {
        path: transform(originals[path]) for path, transform in transforms_b.items()
    }


def test_existing_presentation_or_helper_collision_is_not_overwritten():
    documents, rows = key_sources()
    documents[keys.POUCH].flowchart.entry_points.append(evfl.EntryPoint(keys.HELPER))
    before = copy.deepcopy(documents)
    request = (keys.BIG, DungeonGrant("ForestTemple", "SmallKey", named=True))
    with pytest.raises(ValueError, match="already exists"):
        keys.compile_bindings(documents, rows, key_analysis(rows), [request])
    assert documents == before


def test_source_without_analyzed_registration_is_refused():
    documents, rows = key_sources()
    analyzed = [row for row in key_analysis(rows) if row["__RowId"] != "KokiriForest_TreasureBox_NaviChatOff"]
    request = ("KokiriForest_TreasureBox_NaviChatOff", DungeonGrant("ForestTemple", "SmallKey", named=True))
    with pytest.raises(ValueError, match="no analyzed-event registration"):
        keys.compile_bindings(documents, rows, analyzed, [request])


def test_long_source_names_keep_distinct_bindings_inside_the_actor_string64_limit():
    documents, rows = key_sources()
    native = next(row for row in rows if row["__RowId"] == "KokiriForest_TreasureBox_NaviChatOff")
    sources = ["Long_Source_" + "x" * 41 + suffix for suffix in ("A", "B")]
    rows.extend({**native, "__RowId": source} for source in sources)
    grant = DungeonGrant("GerudoTrainingGround", "SmallKey", named=True)
    bindings, _ = keys.compile_bindings(documents, rows, key_analysis(rows), [(source, grant) for source in sources])
    names = [bindings[(source, grant)].event for source in sources]
    assert names[0] != names[1]
    assert all(len(name.encode("utf-8")) < 64 for name in names)


def test_default_small_source_keeps_its_reset_and_argument_bootstrap():
    bindings, documents, rows, analyzed, _ = _compile([(keys.SMALL, "FireTemple")])
    run = KeyRun(documents, rows, analyzed)
    run.state["MidoStart"] = True
    run.event(bindings[(keys.SMALL, "FireTemple")].event)
    assert run.state["MidoStart"] is False
    assert run.state["DungeonInfo.FireTemple.SmallKeyNum"] == 1
    assert run.state["DungeonInfo.InsideTheDekuTree.SmallKeyNum"] == 0


def test_named_reward_omits_old_item_comment_but_preserves_story_and_native_comments():
    request = ("InsideTheDekuTree_GetMap", "ForestTemple")
    bindings, documents, rows, analyzed, _ = _compile([request])
    run = KeyRun(documents, rows, analyzed)
    run.event(bindings[request].event)
    assert run.balloons == [197]
    assert run.state["MapFollowUp"] is True
    assert run.state["StoryAfter"] is True
    assert run.state["DungeonInfo.ForestTemple.SmallKeyNum"] == 1
    assert run.messages == list(labels("ForestTemple"))
    run.balloons.clear()
    run.event(request[0])
    assert run.balloons == [354, 197]


@pytest.mark.parametrize("chest", ["Obj_TBox_A_01", "Obj_TBox_A_02"])
def test_public_seed_preserves_named_key_credit_and_first_weapon_bag(tmp_path, zsdic_pack, monkeypatch, chest):
    """Reversing bag/key registration makes the real key compiler reject the literal bag grant."""
    documents, rows = key_sources()
    handover = patch_api.bags.HANDOVER_FLOW
    documents[handover] = evfl.EventFlowFile(handover, flowchart=evfl.Flowchart(handover))
    originals = {keys.flow_path(name): evfl.write(document) for name, document in documents.items()}
    originals[keys.SETTINGS] = byml.write(rows)
    originals[keys.ANALYZED] = byml.write(key_analysis(rows))
    originals[FLOW_VERSIONS] = byml.write({"Versions": {}})
    game_data = {
        "Data": {
            "Bool64bitKey": [],
            "Enum": [],
            **{
                kind: [
                    {"Hash": byml.U32(save_key(name)), "ResetTypeValue": 8, "SaveFileIndex": 0}
                    for argument, name in keys._arguments("ForestTemple").items()
                    if (argument == "Once") == (kind == "Bool")
                ]
                for kind in ("Int", "Bool")
            },
        }
    }
    game_data["Data"]["Bool"].append(
        {
            "Hash": byml.U32(save_key("ActionGuide_IsEnd.Navi")),
            "DefaultValue": False,
            "ResetTypeValue": 8,
            "SaveFileIndex": 0,
        }
    )
    originals["GameData/GameDataList.Product.110.byml.zs"] = byml.write(game_data)
    originals["Banc/Synthetic/Synthetic_Static.bcett.byml.zs"] = byml.write({"Actors": []})
    originals[text.archive_path("USen")] = sarc.write(
        {
            key_text.GET_TEXT: msbt.write(msbt.Msbt({}, buckets=2)),
            key_text.LOCATION_TEXT: msbt.write(
                msbt.Msbt({keys.TARGETS["Forest Temple"].location_label: ["Invented Grove"]}, buckets=2)
            ),
            text.POUCH_TEXT: msbt.write(msbt.Msbt({key_text.KEY_NOUN: ["Invented Key"]}, buckets=2)),
        }
    )
    dictionaries = zsdic.Dictionaries.from_pack(zsdic_pack)
    for path, data in {zsdic.PACK_PATH: zsdic_pack, **originals}.items():
        destination = tmp_path / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data if path == zsdic.PACK_PATH else dictionaries.compress(path, data))
    plan = Plan(
        [
            ChestChange(
                "Foreign Key",
                1,
                "Foreign Key",
                ("Banc/Synthetic/Synthetic_Static.bcett.byml.zs",),
                chest,
                "Small Key (Forest Temple)",
                "TBox_Rupee_Blue",
                "Item_Dungeon_SmallKey",
                None,
                named_key="ForestTemple",
            )
        ],
        [],
        [],
    )
    # The placement plan is invented; unrelated Sheik localization does not participate in this grant.
    monkeypatch.setattr(patch_api.item_actors, "load", lambda: patch_api.item_actors.loads(""))
    monkeypatch.setattr(patch_api, "make_plan", lambda *args: plan)
    monkeypatch.setattr(text, "sheik_hint_changes", lambda *args: {})
    output = patch_api.make_seed(
        tmp_path,
        0,
        Settings(dungeon_items="anywhere", fast_start=(), cheap_deku_shield=False),
        {"start": "Root", "goal": "True", "items": {}, "regions": [{"name": "Root"}]},
    )
    written = originals.copy()
    for changes in output.extra_changes:
        for path in written.keys() & changes.keys():
            written[path] = changes[path](written[path])
    initial = byml.read(written["GameData/GameDataList.Product.110.byml.zs"])
    navi = next(entry for entry in initial["Data"]["Bool"] if entry["Hash"] == save_key("ActionGuide_IsEnd.Navi"))
    assert navi["DefaultValue"] is True
    run = KeyRun(
        {name: evfl.read(written[keys.flow_path(name)]) for name in documents},
        byml.read(written[keys.SETTINGS]),
        byml.read(written[keys.ANALYZED]),
    )
    run.entry(keys.POUCH, "GetPouchContentByActorNameForTreasureBox", {"ActorName": "Item_Range_SlingShot"})
    assert run.stock == {"Item_BulletBag_Small": 1, "Item_Range_SlingShot": 1}
    run.event(output.plan.changes[0].key_event)
    assert run.state["DungeonInfo.ForestTemple.SmallKeyNum"] == 1
    assert run.state["DungeonInfo.ForestTemple.SmallKeyTotalNum"] == 1
    assert run.state["DungeonInfo.InsideTheDekuTree.SmallKeyNum"] == 0
