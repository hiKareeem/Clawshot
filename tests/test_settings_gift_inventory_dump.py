"""No changed gift or called flow may independently set its old inventory flag."""

from pathlib import Path

import pytest

from clawshot.census.gifts import EVENT_SETTING, _callee, reachable
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import evfl
from clawshot.patch import gifts, shops
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.save import murmur3_32
from test_gifts_dump import context  # noqa: F401 — shared fresh-dump patch context

pytestmark = pytest.mark.dump


def test_shuffled_gift_call_graphs_do_not_write_their_vanilla_isget(romfs, context):
    dictionaries, files, changes = context
    transforms = gifts.file_changes(changes, files)
    charts = {}
    for flow, path in files.items():
        data = dictionaries.decompress(path, (romfs / path).read_bytes())
        if path in transforms:
            data = transforms[path](data)
        chart = evfl.read(data).flowchart
        if chart is not None:
            charts[flow] = chart
    rows = {str(row["__RowId"]): row for row in read_romfs_byml(romfs, dictionaries, shops.POUCH_TABLE)}
    game_data = read_romfs_byml(romfs, dictionaries, GAME_DATA_LIST)
    saved = {int(row["Hash"]): row for row in game_data["Data"]["Bool"]}
    transitions = {}
    for row in read_romfs_byml(romfs, dictionaries, EVENT_SETTING):
        filename = row.get("FlowchartFileName") or row.get("TimelineFileName")
        if filename:
            transitions[str(row["__RowId"])] = (
                Path(str(filename)).name.split(".")[0],
                row.get("EntryPointName", "EntryPoint0"),
            )
    leaks = []
    for change in changes:
        if change.rule.writes:
            target = saved[murmur3_32(change.flag.encode())]
            assert int(target["SaveFileIndex"]) == 0 and int(target["ResetTypeValue"]) == 8
        actors = {step.vanilla_item for step in change.steps}
        for actor in tuple(actors):
            for field in ("AdultEquipment", "ChildEquipment"):
                if rows.get(actor, {}).get(field):
                    actors.add(Path(str(rows[actor][field])).name.split(".")[0])
        flags = {"IsGet." + actor for actor in actors}
        roots = {step.flow for step in change.steps}
        pending = [(flow, index) for flow in roots for index in range(len(charts[flow].events))]
        seen = set()
        while pending:
            flow, index = pending.pop()
            if (flow, index) in seen or index == evfl.NONE:
                continue
            seen.add((flow, index))
            fc = charts[flow]
            event = fc.events[index]
            callee = _callee(flow, event)
            if isinstance(event, evfl.ActionEvent):
                actor = fc.actors[event.actor]
                action = actor.actions[event.action]
                params = event.params or {}
                if actor.name == "GameDataActor" and any(
                    value in flags for value in params.values() if isinstance(value, str)
                ):
                    leaks.append((change.check, flow, event.name, action, params))
                if actor.name == "EventSystemActor" and action == "EventTransition":
                    callee = transitions.get(params.get("EventName"))
            if callee and callee[0] in charts:
                target = charts[callee[0]]
                entry = next((entry for entry in target.entry_points if entry.name == callee[1]), None)
                indices = reachable(target, entry.main_event) if entry else range(len(target.events))
                pending.extend((callee[0], i) for i in indices)
    assert leaks == [], leaks
