"""Source-bound dungeon-item grants using the played small/big chest lifecycle.

Clone native wrappers and presentation entries, not shared native bindings. Small
keys write native counters; same-dungeon boss keys reuse the native grant and
indicator. Maps, compasses and off-area grants write saved ownership Bools.
Only off-dungeon small keys replace pickup text. Played acceptance and remaining
limitations are recorded in r12-keys.md and r13-dungeon-items.md.
"""

import copy
import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from clawshot.chest_openings import source_for
from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import key_text
from clawshot.patch.key_targets import DUNGEON_TARGETS, TARGETS, DungeonGrant
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import FileChanges
from clawshot.save import key as save_key

SMALL = "Dm_SY_TreasureboxSmall"
BIG = "Dm_SY_Treasurebox"
POUCH = "GetPouchContent"
SETTINGS = "RSDB/EventSetting.Product.111.rstbl.byml.zs"
ANALYZED = "RSDB/GameAnalyzedEventInfo.Product.111.rstbl.byml.zs"
HELPER = "ClawshotGrantSmallKey"
NATIVE_BOSS_HELPER = "ClawshotGrantNativeBossKey"
# Acquisition-only balloons, not the independent Nabooru story reaction (197).
# Supported-dump classification and index/parameter provenance: plans/rounds/r12-keys.md.
_ITEM_NAVI_BALLOONS = frozenset({228, 345, 354, 361, 474, 475, 476, 478, 479, 480, 495})
# These acquisition comments share a source wrapper with required room/quest state.
_COMMENTED_STORY_SOURCES = frozenset({"InsideJabuJabuBelly_TreasureBoxWithRuto09", "SubEvent_GetIceArrow_OpenTBox"})


def flow_path(name: str) -> str:
    return f"Event/EventFlow/{name}.bfevfl.zs"


def _edges(event: evfl.Event) -> list[int]:
    if isinstance(event, (evfl.SwitchEvent, evfl.SubFlowSwitchEvent)):
        return [index for _, index in event.cases]
    if isinstance(event, evfl.ForkEvent):
        return [event.join, *event.forks]
    return [event.next] if hasattr(event, "next") else []


def _reachable(chart: evfl.Flowchart, start: int) -> set[int]:
    seen: set[int] = set()
    pending = [start]
    while pending:
        index = pending.pop()
        if index == evfl.NONE or index in seen:
            continue
        if not 0 <= index < len(chart.events):
            raise PatchError(f"{chart.name}: invalid event index {index}")
        seen.add(index)
        pending.extend(_edges(chart.events[index]))
    return seen


def _operation(chart: evfl.Flowchart, actor_name: str, kind: str, operation: str) -> tuple[int, int]:
    actors = [(i, a) for i, a in enumerate(chart.actors) if a.name == actor_name and not a.secondary_name]
    if len(actors) != 1 or actors[0][1].entry_point != evfl.NONE:
        raise PatchError(f"{chart.name}: expected one unscoped {actor_name}")
    index, actor = actors[0]
    names = getattr(actor, kind)
    if operation not in names:
        names.append(operation)
    return index, names.index(operation)


def _arguments(target: str) -> dict[str, str]:
    if target not in {value.id for value in TARGETS.values()}:
        raise PatchError(f"unsupported small-key target {target!r}")
    return {
        "Remaining": f"DungeonInfo.{target}.SmallKeyNum",
        "Total": f"DungeonInfo.{target}.SmallKeyTotalNum",
        "Once": f"DungeonInfo.{target}.IsGetSmallKeyOnce",
    }


def _check_fields(document: dict, targets: list[str]) -> None:
    for target in sorted(set(targets)):
        for argument, name in _arguments(target).items():
            kind = "Bool" if argument == "Once" else "Int"
            rows = [row for row in document["Data"][kind] if row["Hash"] == save_key(name)]
            if len(rows) != 1 or rows[0].get("ResetTypeValue") != 8 or rows[0].get("SaveFileIndex") != 0:
                raise PatchError(f"{name}: expected one existing saved {kind} field, got {rows}")


def add_grant_helper(chart: evfl.Flowchart) -> None:
    """Append the played four-node grant with argument-valued field names."""
    if any(entry.name == HELPER for entry in chart.entry_points):
        raise PatchError(f"{chart.name}: small-key helper already exists")
    ai, add = _operation(chart, "GameDataActor", "actions", "EventTriggerAddOrSubGameDataInt")
    _, set_bool = _operation(chart, "GameDataActor", "actions", "EventTriggerSetGameDataBool")
    _, query = _operation(chart, "GameDataActor", "queries", "EventQueryIsGameDataInt")
    start = len(chart.events)
    chart.events.extend(
        [
            evfl.SwitchEvent(
                "ClawshotKeyWasZero",
                ai,
                query,
                [(0, start + 2), (1, start + 1), (2, start + 2)],
                {"GameDataName": evfl.Argument("Remaining"), "Index": -1, "Value": 0},
            ),
            evfl.ActionEvent(
                "ClawshotKeyOnce",
                ai,
                set_bool,
                start + 2,
                {"GameDataName": evfl.Argument("Once"), "Index": -1, "Value": True},
            ),
            evfl.ActionEvent(
                "ClawshotKeyTotal",
                ai,
                add,
                start + 3,
                {"GameDataName": evfl.Argument("Total"), "Index": -1, "Value": 1},
            ),
            evfl.ActionEvent(
                "ClawshotKeyRemaining",
                ai,
                add,
                evfl.NONE,
                {"GameDataName": evfl.Argument("Remaining"), "Index": -1, "Value": 1},
            ),
        ]
    )
    chart.entry_points.append(evfl.EntryPoint(HELPER, start))


@dataclass(frozen=True)
class Binding:
    source: str
    target: str
    event: str


class _Compiler:
    def __init__(
        self,
        documents: Mapping[str, evfl.EventFlowFile],
        rows: list[dict],
        analyzed_rows: list[dict],
        grants: Sequence[DungeonGrant],
    ):
        self.grants = {grant.id: grant for grant in grants}
        self.originals = documents
        self.documents = copy.deepcopy(dict(documents))
        self.original_rows = copy.deepcopy(rows)
        self.rows = copy.deepcopy(rows)
        self.by_row = {row["__RowId"]: row for row in self.rows}
        if len(self.by_row) != len(self.rows):
            raise PatchError("duplicate EventSetting identifiers")
        self.analyzed = {row["__RowId"]: row for row in analyzed_rows}
        self.row_sources: dict[str, str] = {}
        self.entries: dict[tuple[str, str, str, str], str] = {}
        self.nodes: dict[tuple[str, int, str, str], int] = {}
        self.bindings: dict[tuple[str, str], Binding] = {}
        self.destinations: dict[tuple[str, str, str], str] = {}
        self.touched: set[str] = set()
        if any(grant.family == "SmallKey" for grant in grants):
            add_grant_helper(self.chart(POUCH))
            self.touched.add(POUCH)
        if any(grant.native_boss for grant in grants):
            self.add_native_boss_helper()

    def chart(self, flow: str) -> evfl.Flowchart:
        if flow not in self.documents or self.documents[flow].flowchart is None:
            raise PatchError(f"small-key binding needs flowchart {flow}")
        return self.documents[flow].flowchart

    def old_chart(self, flow: str) -> evfl.Flowchart:
        return self.originals[flow].flowchart

    def row(self, source: str) -> dict:
        if source not in self.by_row:
            raise PatchError(f"small-key binding has no EventSetting {source!r}")
        return self.by_row[source]

    def add_row(self, source: str, name: str, flow: str, entry: str) -> None:
        if name in self.by_row:
            raise PatchError(f"small-key EventSetting collision: {name}")
        row = copy.deepcopy(self.row(source))
        row.update(__RowId=name, FlowchartFileName=f"Work/Event/EventFlow/{flow}.evfc", EntryPointName=entry)
        self.rows.append(row)
        self.by_row[name] = row
        self.row_sources[name] = source

    def destination(self, size: str, target: str, entry: str | None = None) -> str:
        flow = BIG if size == "Big" else SMALL
        entry = entry or "Success"
        key = (size, target, entry)
        if key in self.destinations:
            return self.destinations[key]
        name = f"Clawshot_Key_{target}_{size}_{entry}"
        self.destinations[key] = name
        cloned = self.clone_entry(flow, entry, target, "content")
        self.add_row(flow, name, flow, cloned)
        return name

    def bind(self, source: str, target: str) -> Binding:
        key = (source, target)
        if key in self.bindings:
            return self.bindings[key]
        grant = self.grants[target]
        if grant.family != "Content":
            if grant.target not in {value.id for value in DUNGEON_TARGETS.values()}:
                raise PatchError(f"unsupported dungeon-item target {grant.target!r}")
            if grant.family not in {"SmallKey", "BossKey", "Map", "Compass"}:
                raise PatchError(f"unsupported dungeon-item family {grant.family!r}")
        if grant.native_boss and (grant.family != "BossKey" or grant.named):
            raise PatchError("the native boss-key grant requires a same-dungeon boss key")
        # GetEventName is a String64 blackboard parameter. Full source names can overflow it.
        source_id = hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]
        name = f"Clawshot_Key_{target}_{source_id}"
        binding = Binding(source, target, name)
        self.bindings[key] = binding
        row = self.row(source)
        flow = Path(row["FlowchartFileName"]).stem
        entry = row["EntryPointName"]
        if source == BIG:
            # Default big chests need a real outer lifecycle, not a direct AllHide clone.
            cloned = self.handoff("Big", target)
            self.add_row("InsideTheDekuTree_GetMap", name, "NaviChat", cloned)
        else:
            cloned = self.clone_entry(flow, entry, target, "wrapper")
            self.add_row(source, name, flow, cloned)
        return binding

    def handoff(self, size: str, target: str) -> str:
        # Native PlayDemo explicitly participates Player before its EventTransition.
        return self.clone_entry("NaviChat", "PlayDemo", target, "handoff" + size)

    def clone_entry(self, flow: str, name: str, target: str, mode: str) -> str:
        key = (flow, name, target, mode)
        if key in self.entries:
            return self.entries[key]
        chart = self.chart(flow)
        old = self.old_chart(flow).entry_point(name)
        new_name = f"Clawshot_{target}_{mode}_{name}"
        if any(entry.name == new_name for entry in chart.entry_points):
            raise PatchError(f"{flow}: small-key entry collision {new_name}")
        self.entries[key] = new_name
        new = evfl.EntryPoint(new_name, variables=copy.deepcopy(old.variables))
        chart.entry_points.append(new)
        self.touched.add(flow)
        new.main_event = self.clone_node(flow, old.main_event, target, mode)
        new.sub_flow_events = sorted(
            index
            for index in _reachable(chart, new.main_event)
            if isinstance(chart.events[index], (evfl.SubFlowEvent, evfl.SubFlowSwitchEvent))
        )
        return new_name

    def clone_node(self, flow: str, index: int, target: str, mode: str) -> int:
        if index == evfl.NONE:
            return index
        key = (flow, index, target, mode)
        if key in self.nodes:
            return self.nodes[key]
        chart = self.chart(flow)
        old = self.old_chart(flow).events[index]
        if mode == "wrapper" and isinstance(old, evfl.ActionEvent):
            actor = self.old_chart(flow).actors[old.actor]
            if (
                actor.name == "Npc_Navi"
                and actor.actions[old.action] == "EventNaviRequestBallonMessage"
                and (old.params or {}).get("Index") in _ITEM_NAVI_BALLOONS
            ):
                # Only the named reward changes: retain everything before and after its old-item comment.
                self.nodes[key] = self.clone_node(flow, old.next, target, mode)
                return self.nodes[key]
        event = copy.deepcopy(old)
        event.name = f"Clawshot_{target}_{mode}_{event.name}"
        new_index = len(chart.events)
        self.nodes[key] = new_index
        chart.events.append(event)
        if hasattr(event, "next"):
            event.next = self.clone_node(flow, old.next, target, mode)
        if isinstance(event, (evfl.SwitchEvent, evfl.SubFlowSwitchEvent)):
            event.cases = [(v, self.clone_node(flow, i, target, mode)) for v, i in old.cases]
        if isinstance(event, evfl.ForkEvent):
            event.join = self.clone_node(flow, old.join, target, mode)
            event.forks = [self.clone_node(flow, i, target, mode) for i in old.forks]
        if isinstance(event, (evfl.SubFlowEvent, evfl.SubFlowSwitchEvent)):
            called = event.flowchart or flow
            if mode == "wrapper" and called == SMALL and event.entry_point != "Success_MidoHouse":
                event.flowchart = "NaviChat"
                event.entry_point = self.handoff("Small", target)
            elif (
                called == flow
                or called in (BIG, SMALL, POUCH)
                or (called, event.entry_point) == ("NaviChat", "PlayDemo")
            ):
                called_mode = mode if called == flow else "content" if called in (BIG, SMALL, POUCH) else "wrapper"
                event.entry_point = self.clone_entry(called, event.entry_point, target, called_mode)
        if isinstance(event, (evfl.ActionEvent, evfl.SwitchEvent)):
            actor = self.old_chart(flow).actors[event.actor]
            # Chest wrappers do not use the unrelated entry-scoped actors in their source files.
            if actor.entry_point != evfl.NONE:
                raise PatchError(f"{flow}:{old.name}: scoped actor {actor.name} needs a reviewed binding")
        if isinstance(event, evfl.ActionEvent):
            self.rewrite_action(flow, index, new_index, event, target, mode)
        return new_index

    def add_native_boss_helper(self) -> None:
        """Reuse the big opening's native grant, indicator and display wait on existing small-flow actors."""
        chart = self.chart(SMALL)
        if any(entry.name == NATIVE_BOSS_HELPER for entry in chart.entry_points):
            raise PatchError(f"{SMALL}: native boss-key helper already exists")
        ai, grant = _operation(chart, "GameSystemActor", "actions", "EventGetDungeonBossKey")
        ui, display = _operation(chart, "UISystemActor", "actions", "EventTriggerSetDisplayBossKey")
        _, wait = _operation(chart, "GameSystemActor", "actions", "EventWait")
        start = len(chart.events)
        chart.events.extend(
            [
                evfl.ActionEvent("ClawshotNativeBossGrant", ai, grant, start + 1, {"IsWaitEnd": True}),
                evfl.ActionEvent("ClawshotNativeBossDisplay", ui, display, start + 2, {"IsDisplayBossKey": True}),
                evfl.ActionEvent("ClawshotNativeBossWait", ai, wait, evfl.NONE, {"IsWaitEnd": True, "Frames": 50}),
            ]
        )
        chart.entry_points.append(evfl.EntryPoint(NATIVE_BOSS_HELPER, start))
        self.touched.add(SMALL)

    def grant_event(self, name: str, target: str, next_event: int) -> evfl.Event:
        grant = self.grants[target]
        chart = self.chart(POUCH)
        if grant.native_boss:
            return evfl.SubFlowEvent(name, SMALL, NATIVE_BOSS_HELPER, next_event)
        if grant.family == "SmallKey":
            if not grant.named:
                ai, action = _operation(chart, "GameDataActor", "actions", "EventTriggerSetGameDataBool")
                demo = len(chart.events)
                chart.events.append(
                    evfl.ActionEvent(
                        name + "CounterDemo",
                        ai,
                        action,
                        next_event,
                        {"GameDataName": "UI_RequestSmallKeyCountUpDemo", "Index": -1, "Value": True},
                    )
                )
                next_event = demo
            return evfl.SubFlowEvent(name, "", HELPER, next_event, _arguments(grant.target))
        ai, action = _operation(chart, "GameDataActor", "actions", "EventTriggerSetGameDataBool")
        return evfl.ActionEvent(name, ai, action, next_event, {"GameDataName": grant.field, "Index": -1, "Value": True})

    def rewrite_action(
        self, flow: str, original_index: int, index: int, event: evfl.ActionEvent, target: str, mode: str
    ) -> None:
        chart = self.chart(flow)
        actor = chart.actors[event.actor]
        operation = actor.actions[event.action]
        params = event.params or {}
        if operation == "EventTransition" and actor.name == "EventSystemActor":
            name = params.get("EventName")
            if name in (BIG, SMALL):
                size = "Small" if mode == "handoffSmall" or name == SMALL else "Big"
                params["EventName"] = self.destination(size, target, "Success_" if mode == "handoffSmall" else None)
            elif name == "InsideJabuJabuBelly_GetCompass":
                params["EventName"] = self.bind(name, target).event
        if mode != "content":
            return
        grant = self.grants[target]
        if grant.family == "Content":
            return
        if flow == BIG and actor.name == "GameSystemActor" and operation == f"EventGetDungeon{grant.family}":
            if grant.native_boss:
                return  # A big opening already performs this same native grant and indicator.
            # Keep the native post-grant presentation, but never credit the standing dungeon as well.
            pouch = self.chart(POUCH)
            entry_name = f"Clawshot_{target}_Grant"
            if not any(entry.name == entry_name for entry in pouch.entry_points):
                call = self.grant_event(event.name + "Grant", target, evfl.NONE)
                start = len(pouch.events)
                pouch.entry_points.append(
                    evfl.EntryPoint(entry_name, start, [start] if isinstance(call, evfl.SubFlowEvent) else [])
                )
                pouch.events.append(call)
                self.touched.add(POUCH)
            chart.events[index] = evfl.SubFlowEvent(event.name, POUCH, entry_name, event.next)
        elif flow == POUCH and actor.name == "PouchSystemActor" and operation == "EventTriggerAddOrRemovePouchContent":
            if params.get("Num") != 1 or params.get("Actor") != evfl.Argument("ActorName"):
                raise PatchError("unexpected pouch grant in named chest path")
            chart.events[index] = self.grant_event(event.name, target, event.next)
        elif flow == POUCH and actor.name == "SystemTextNPC" and operation == "EventTalk" and grant.named:
            message, caption = key_text.labels(grant.target)
            if params.get("MessageId") == "EventFlowMsg/Dm_SY_Get:GetMessage":
                params["MessageId"] = message
            elif params.get("MessageId") == "EventFlowMsg/Dm_SY_Get:GetCaption":
                params["MessageId"] = caption

    def analyzed_row(self, row: dict) -> dict:
        source = self.row_sources[row["__RowId"]]
        if source not in self.analyzed:
            raise PatchError(f"small-key source event {source!r} has no analyzed-event registration")
        result = copy.deepcopy(self.analyzed[source])
        result["__RowId"] = row["__RowId"]
        subflows = set(result.get("SubFlowList", ()))
        # Replaced chest transitions must preload the new child ID, not only the native one.
        children = set(result.get("ChildEventList", ())) - {BIG, SMALL, "InsideJabuJabuBelly_GetCompass"}
        root = Path(row["FlowchartFileName"]).stem
        pending = [(root, row["EntryPointName"])]
        seen = set()
        while pending:
            flow, entry = pending.pop()
            if (flow, entry) in seen:
                continue
            seen.add((flow, entry))
            if flow != root:
                subflows.add(flow)
            if flow not in self.documents:
                continue  # Native registration already carries these unchanged callees' transitive dependencies.
            chart = self.chart(flow)
            for index in sorted(_reachable(chart, chart.entry_point(entry).main_event)):
                event = chart.events[index]
                if isinstance(event, (evfl.SubFlowEvent, evfl.SubFlowSwitchEvent)):
                    pending.append((event.flowchart or flow, event.entry_point))
                elif isinstance(event, evfl.ActionEvent):
                    actor = chart.actors[event.actor]
                    if actor.name == "EventSystemActor" and actor.actions[event.action] == "EventTransition":
                        name = (event.params or {}).get("EventName")
                        if isinstance(name, str) and not isinstance(name, evfl.Argument):
                            children.add(name)
        if subflows or "SubFlowList" in result:
            result["SubFlowList"] = sorted(subflows)
        if children or "ChildEventList" in result:
            result["ChildEventList"] = sorted(children)
        return result

    def finish(self) -> FileChanges:
        changes = {}
        for name in sorted(self.touched):
            original = self.originals[name]
            document = self.documents[name]
            encoded = evfl.write(document)
            parsed = evfl.read(encoded)
            if parsed != document:
                raise PatchError(f"{name}: named-key flow read-back differs")
            # Appends only: all original entries/events/actors remain native (or an earlier patch's version).
            inverse = copy.deepcopy(parsed)
            old = original.flowchart
            chart = inverse.flowchart
            chart.events = chart.events[: len(old.events)]
            chart.entry_points = chart.entry_points[: len(old.entry_points)]
            for actor, prior in zip(chart.actors, old.actors, strict=True):
                actor.actions = actor.actions[: len(prior.actions)]
                actor.queries = actor.queries[: len(prior.queries)]
            if inverse != original:
                raise PatchError(f"{name}: named-key inverse changed native content")
            changes[flow_path(name)] = _append_flow(original, document)
        added = self.rows[len(self.original_rows) :]
        changes[SETTINGS] = _append_rows(added)
        changes[ANALYZED] = _append_rows([self.analyzed_row(row) for row in added])
        return changes


def _append_flow(original: evfl.EventFlowFile, changed: evfl.EventFlowFile):
    def transform(data: bytes) -> bytes:
        current = evfl.read(data)
        # Other patch steps may have modified original nodes (e.g. shuffled gifts); preserve them.
        old, new, now = original.flowchart, changed.flowchart, current.flowchart
        if (
            now is None
            or len(now.events) != len(old.events)
            or len(now.entry_points) != len(old.entry_points)
            or now.actors != old.actors
        ):
            raise PatchError(f"{original.name}: another patch changed named-key index bindings")
        now.events.extend(copy.deepcopy(new.events[len(old.events) :]))
        now.entry_points.extend(copy.deepcopy(new.entry_points[len(old.entry_points) :]))
        for actor, source in zip(now.actors, new.actors, strict=True):
            actor.actions = source.actions.copy()
            actor.queries = source.queries.copy()
        encoded = evfl.write(current)
        if evfl.read(encoded) != current:
            raise PatchError(f"{original.name}: composed named-key read-back differs")
        return encoded

    return transform


def _append_rows(added: list[dict]):
    def transform(data: bytes) -> bytes:
        document = byml.load(data)
        existing = {row["__RowId"] for row in document.root}
        if any(row["__RowId"] in existing for row in added):
            raise PatchError("small-key EventSetting row already exists")
        original = copy.deepcopy(document.root)
        document.root.extend(copy.deepcopy(added))
        document.root.sort(key=lambda row: row["__RowId"])
        encoded = byml.dump(document)
        parsed = byml.read(encoded)
        added_ids = {row["__RowId"] for row in added}
        if parsed != document.root or [row for row in parsed if row["__RowId"] not in added_ids] != original:
            raise PatchError("small-key EventSetting read-back/inverse differs")
        return encoded

    return transform


def compile_bindings(
    documents: Mapping[str, evfl.EventFlowFile],
    rows: list[dict],
    analyzed_rows: list[dict],
    requests: list[tuple[str, DungeonGrant]],
) -> tuple[dict[tuple[str, DungeonGrant], Binding], FileChanges]:
    """Compile native source-event/target pairs; deterministic regardless of request order."""
    if not requests:
        return {}, {}
    compiler = _Compiler(documents, rows, analyzed_rows, [grant for _, grant in requests])
    for source, grant in sorted(set(requests)):
        compiler.bind(source, grant.id)
    bindings = {(source, grant): compiler.bindings[(source, grant.id)] for source, grant in requests}
    return bindings, compiler.finish()


def changes(romfs: str | Path, plan: Plan, *, prior_changes: Sequence[FileChanges] = ()) -> tuple[Plan, FileChanges]:
    """Resolve moved dungeon items and off-dungeon keys through played source bindings."""
    routed = [
        change
        for change in plan.changes
        if change.named_key is not None
        or change.dungeon_item is not None
        or (change.kept_event is not None and change.kept_event.name in _COMMENTED_STORY_SOURCES)
    ]
    if not routed:
        return plan, {}
    romfs = Path(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def read(path: str) -> bytes:
        data = dictionaries.decompress(path, (romfs / path).read_bytes())
        for transforms in prior_changes:
            if transform := transforms.get(path):
                data = transform(data)
        return data

    rows = byml.read(read(SETTINGS))
    analyzed_rows = byml.read(read(ANALYZED))
    grants = [
        DungeonGrant(change.named_key, "SmallKey", named=True)
        if change.named_key
        else change.dungeon_item or DungeonGrant("", "Content")
        for change in routed
    ]
    game_data = byml.read(read("GameData/GameDataList.Product.110.byml.zs"))
    _check_fields(game_data, [grant.target for grant in grants if grant.family == "SmallKey"])
    for grant in grants:
        if grant.family not in {"SmallKey", "Content"}:
            found = [row for row in game_data["Data"]["Bool"] if row["Hash"] == save_key(grant.field)]
            if len(found) != 1 or found[0].get("ResetTypeValue") != 8 or found[0].get("SaveFileIndex") != 0:
                raise PatchError(f"{grant.field}: expected one existing saved Bool, got {found}")
    documents = {}
    # Source wrappers can call NaviChat; content calls remain within the three common flows.
    needed = {BIG, SMALL, POUCH, "NaviChat"}
    requests = []
    for change, grant in zip(routed, grants, strict=True):
        source = source_for(change.chest, change.kept_event.name if change.kept_event else None)
        if source is None:
            raise PatchError(f"{change.location}: no small-key opening contract for {change.chest}")
        row = next((row for row in rows if row["__RowId"] == source), None)
        if row is None:
            raise PatchError(f"{change.location}: no source event {source}")
        needed.add(Path(row["FlowchartFileName"]).stem)
        requests.append((source, grant))
    for name in sorted(needed):
        path = flow_path(name)
        documents[name] = evfl.read(read(path))
    bindings, transforms = compile_bindings(documents, rows, analyzed_rows, requests)
    replacements = {
        (change.id, change.files): bindings[request].event for change, request in zip(routed, requests, strict=True)
    }
    new_plan = replace(
        plan,
        changes=[
            replace(change, key_event=replacements[(change.id, change.files)])
            if (change.id, change.files) in replacements
            else change
            for change in plan.changes
        ],
    )
    transforms.update(key_text.changes(romfs, [grant.target for grant in grants if grant.named]))
    return new_plan, transforms
