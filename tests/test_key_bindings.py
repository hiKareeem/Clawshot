"""Synthetic event execution: source lifecycle, target attribution, native controls."""

import copy

import pytest

from clawshot.formats import byml, evfl
from clawshot.patch import keys
from clawshot.patch.key_text import labels


def _document(name, actors, events, entries):
    return evfl.EventFlowFile(name, evfl.Flowchart(name, actors, events, entries))


def _sources():
    pouch = _document(
        keys.POUCH,
        [
            evfl.Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"]),
            evfl.Actor("GameDataActor"),
            evfl.Actor("SystemTextNPC", actions=["EventTalk"]),
        ],
        [
            evfl.ActionEvent("Grant", 0, 0, 1, {"Actor": evfl.Argument("ActorName"), "Num": 1}),
            evfl.ActionEvent("Message", 2, 0, 2, {"MessageId": "EventFlowMsg/Dm_SY_Get:GetMessage"}),
            evfl.ActionEvent("Caption", 2, 0, evfl.NONE, {"MessageId": "EventFlowMsg/Dm_SY_Get:GetCaption"}),
        ],
        [evfl.EntryPoint("GetPouchContentByActorNameForTreasureBox", 0), evfl.EntryPoint("DisplayGetByActorName", 1)],
    )
    big = _document(
        keys.BIG,
        [evfl.Actor("GameSystemActor", actions=["EventGetDungeonSmallKey"])],
        [
            evfl.ActionEvent("Grant", 0, 0, 1, {"IsWaitEnd": True}),
            evfl.SubFlowEvent("Display", keys.POUCH, "DisplayGetByActorName"),
        ],
        [evfl.EntryPoint("Success", 0, [1])],
    )
    small = _document(
        keys.SMALL,
        [evfl.Actor("GameDataActor", actions=["EventTriggerSetGameDataBool"])],
        [
            evfl.SubFlowEvent(
                "Grant", keys.POUCH, "GetPouchContentByActorNameForTreasureBox", params={"ActorName": "Key"}
            ),
            evfl.ActionEvent("MidoStart", 0, 0, 2, {"GameDataName": "MidoStart", "Value": True}),
            evfl.SubFlowEvent("MidoContent", "", "Success_"),
        ],
        [
            evfl.EntryPoint("Success", 0, [0]),
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
        ],
        [
            evfl.ActionEvent("Participate", 0, 0, 1),
            evfl.ActionEvent("Transition", 1, 0, evfl.NONE, {"EventName": keys.BIG, "SpecialEventActionType": 1}),
            evfl.SubFlowEvent("MapDemo", "", "PlayDemo", 3),
            evfl.ActionEvent("MapFollowUp", 2, 0, evfl.NONE, {"GameDataName": "MapFollowUp", "Value": True}),
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


def _analysis(rows):
    return [
        {
            "__RowId": row["__RowId"],
            "SubFlowList": [] if row["__RowId"] == "InsideTheDekuTree_GetMap" else [keys.POUCH],
            "ChildEventList": [keys.BIG] if row["__RowId"] == "InsideTheDekuTree_GetMap" else [],
        }
        for row in rows
    ]


class _Run:
    def __init__(self, documents, rows, analyzed):
        self.documents = documents
        self.rows = {row["__RowId"]: row for row in rows}
        self.analyzed = {row["__RowId"]: row for row in analyzed}
        self.active = None
        self.state = {
            f"DungeonInfo.{target}.{field}": value
            for target in ("ForestTemple", "FireTemple", "InsideTheDekuTree")
            for field, value in [("SmallKeyNum", 0), ("SmallKeyTotalNum", 0), ("IsGetSmallKeyOnce", False)]
        }
        self.messages = []
        self.trace = []

    def event(self, name):
        row = self.rows[name]
        flow = row["FlowchartFileName"].split("/")[-1].removesuffix(".evfc")
        analyzed = self.analyzed[name]
        if self.active:
            assert name in self.active[1]["ChildEventList"]
        prior = self.active
        self.active = (flow, analyzed)
        self.entry(flow, row["EntryPointName"], {})
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
                if operation == "EventQueryIsSmallKey":
                    result = 0 if params["ActorName"] == "Key" else 1
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
            elif operation == "EventTriggerParticipateEvent":
                pass
            elif operation == "EventTalk":
                self.messages.append(params["MessageId"])
            elif operation == "EventTriggerSetGameDataBool":
                self.state[params["GameDataName"]] = params["Value"]
            elif operation == "EventTriggerAddOrSubGameDataInt":
                self.state[params["GameDataName"]] += params["Value"]
            else:
                assert operation in ("EventGetDungeonSmallKey", "EventTriggerAddOrRemovePouchContent")
                self.state["DungeonInfo.InsideTheDekuTree.SmallKeyNum"] += 1
            index = event.next


def _compile(requests):
    documents, rows = _sources()
    analyzed = _analysis(rows)
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


@pytest.mark.parametrize("order", [(0, 1, 2, 3), (3, 0, 2, 1)])
def test_two_targets_both_sizes_do_not_cross_credit_or_replace_native_controls(order):
    requests = [
        (keys.SMALL, "ForestTemple"),
        (keys.BIG, "FireTemple"),
        (keys.SMALL, "FireTemple"),
        (keys.BIG, "ForestTemple"),
    ]
    bindings, documents, rows, analyzed, _ = _compile(requests)
    run = _Run(documents, rows, analyzed)
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
        assert run.trace[0:2] == ["EventTriggerParticipateEvent", "EventTransition"]
        assert "EventGetDungeonSmallKey" not in run.trace
        assert "EventTriggerAddOrRemovePouchContent" not in run.trace
    run.event(keys.BIG)
    assert run.state["DungeonInfo.InsideTheDekuTree.SmallKeyNum"] == 1
    assert run.messages[-2:] == ["EventFlowMsg/Dm_SY_Get:GetMessage", "EventFlowMsg/Dm_SY_Get:GetCaption"]


def test_source_specific_before_and_after_behavior_survives_named_handoffs():
    requests = [("InsideTheDekuTree_GetMap", "ForestTemple"), ("KokiriForest_TreasureBox_NaviChatOff", "FireTemple")]
    bindings, documents, rows, analyzed, _ = _compile(requests)
    run = _Run(documents, rows, analyzed)
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
    run = _Run(documents, rows, analyzed)
    run.entry(keys.POUCH, "GetPouchContentByActorNameForTreasureBox", {"ActorName": "Rupee"})
    assert "EventTriggerAddOrRemovePouchContent" in run.trace
    assert run.messages == ["EventFlowMsg/Dm_SY_Get:GetMessage", "EventFlowMsg/Dm_SY_Get:GetCaption"]
    assert run.state["DungeonInfo.ForestTemple.SmallKeyNum"] == 0


def test_equivalent_sources_share_binding_and_request_order_is_deterministic():
    requests = [(keys.BIG, "FireTemple"), (keys.SMALL, "ForestTemple")]
    a, _, _, _, transforms_a = _compile(requests)
    b, _, _, _, transforms_b = _compile([*reversed(requests), requests[0]])
    assert a == b
    docs, rows = _sources()
    originals = {keys.flow_path(name): evfl.write(document) for name, document in docs.items()}
    originals[keys.SETTINGS] = byml.write(rows)
    originals[keys.ANALYZED] = byml.write(_analysis(rows))
    assert {path: transform(originals[path]) for path, transform in transforms_a.items()} == {
        path: transform(originals[path]) for path, transform in transforms_b.items()
    }


def test_existing_presentation_or_helper_collision_is_not_overwritten():
    documents, rows = _sources()
    documents[keys.POUCH].flowchart.entry_points.append(evfl.EntryPoint(keys.HELPER))
    before = copy.deepcopy(documents)
    with pytest.raises(ValueError, match="already exists"):
        keys.compile_bindings(documents, rows, _analysis(rows), [(keys.BIG, "ForestTemple")])
    assert documents == before


def test_source_without_analyzed_registration_is_refused():
    documents, rows = _sources()
    analyzed = [row for row in _analysis(rows) if row["__RowId"] != "KokiriForest_TreasureBox_NaviChatOff"]
    with pytest.raises(ValueError, match="no analyzed-event registration"):
        keys.compile_bindings(documents, rows, analyzed, [("KokiriForest_TreasureBox_NaviChatOff", "ForestTemple")])
