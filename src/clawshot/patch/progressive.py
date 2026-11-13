"""Chest-only next-tier grants, through the existing source-bound chest lifecycle.

The native guest model remains the base acquisition actor. Selection happens
before the get window, so its name/text and the actual grant use the same tier.
Native unshuffled callers and named dungeon-key bindings are not changed.
"""

import copy
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

from clawshot.chest_openings import source_for
from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import keys
from clawshot.patch.key_targets import DungeonGrant
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import FileChanges
from clawshot.progressive import CHAINS
from clawshot.save import key as save_key


class _Compiler(keys._Compiler):
    """Specialize content dispatch, retaining the key compiler's native source binding."""

    def __init__(self, documents, rows, analyzed_rows, families):
        self.families = {DungeonGrant(name.replace(" ", ""), "Content").id: name for name in families}
        super().__init__(
            documents, rows, analyzed_rows, [DungeonGrant(name.replace(" ", ""), "Content") for name in families]
        )

    def clone_node(self, flow: str, index: int, target: str, mode: str) -> int:
        if index != evfl.NONE and flow in (keys.SMALL, keys.BIG):
            old = self.old_chart(flow).events[index]
            if isinstance(old, evfl.SwitchEvent):
                actor = self.old_chart(flow).actors[old.actor]
                if actor.name == "PouchSystemActor" and actor.queries[old.query] == "EventQueryCanAddToPorch":
                    # The chest's physical base actor may already be owned. It must not
                    # turn the next-tier grant into the native display-only/full path.
                    if (old.params or {}).get("Actor") != evfl.Argument("ContentName"):
                        raise PatchError(f"{flow}/{old.name}: unexpected capacity gate {old.params}")
                    return self.clone_node(flow, dict(old.cases)[0], target, mode)
        result = super().clone_node(flow, index, target, mode)
        if index != evfl.NONE and flow in (keys.SMALL, keys.BIG):
            old = self.old_chart(flow).events[index]
            if (
                isinstance(old, evfl.SubFlowEvent)
                and isinstance(self.chart(flow).events[result], evfl.SubFlowEvent)
                and old.flowchart == "ActionGuide"
                and (old.params or {}).get("ActorName") == evfl.Argument("ContentName")
            ):
                self.selected_argument(flow, result, target)
        return result

    def clone_entry(self, flow: str, name: str, target: str, mode: str) -> str:
        if flow != keys.POUCH or name not in {
            "GetPouchContentByActorNameForTreasureBox",
            "GetPouchContentByActorNameForShowPickUpWindow",
            "DisplayGetByActorName",
        }:
            return super().clone_entry(flow, name, target, mode)
        key = (flow, name, target, mode)
        if key in self.entries:
            return self.entries[key]
        chart = self.chart(flow)
        chart.entry_point(name)  # Refuse a changed native contract before adding anything.
        family = self.families[target]
        tiers = CHAINS[family]
        entry_name = f"Clawshot_{target}_{name}"
        self.entries[key] = entry_name
        ai, query = keys._operation(chart, "GameDataActor", "queries", "EventQueryIsGameDataBool")

        def append(event):
            event.name = f"Clawshot_{target}_{name}_{len(chart.events)}"
            index = len(chart.events)
            chart.events.append(event)
            return index

        grants = [append(evfl.SubFlowEvent("", "", name, params={"ActorName": tier.actor})) for tier in tiers]
        # Highest acquired native item wins. IsGet survives upgrades and age changes,
        # unlike the current equipment/stock view. Never re-grant a lower shared tier.
        first = grants[0]
        for index, tier in enumerate(tiers):
            first = append(
                evfl.SwitchEvent(
                    "",
                    ai,
                    query,
                    [(0, grants[min(index + 1, len(tiers) - 1)]), (1, first)],
                    {"GameDataName": f"IsGet.{tier.owned}", "Index": -1},
                )
            )
        if family == "Progressive Magic":
            _, has_magic = keys._operation(chart, "GameDataActor", "queries", "EventQueryIsGameDataInt")
            first = append(
                evfl.SwitchEvent(
                    "",
                    ai,
                    has_magic,
                    [(0, first), (1, first), (2, grants[-1])],
                    {"GameDataName": "PlayerStatus.MPMax", "Index": -1, "Value": 0},
                )
            )
        if family in {"Progressive Strength", "Progressive Quiver", "Progressive Slingshot"}:
            # Child Bracelet and weapon acquisition are independent of adult strength
            # and ammunition capacity. Owning those upgrades must not skip either.
            first = append(
                evfl.SwitchEvent(
                    "",
                    ai,
                    query,
                    [(0, first), (1, grants[0])],
                    {"GameDataName": f"IsGet.{tiers[0].owned}", "Index": -1},
                )
            )
        chart.entry_points.append(evfl.EntryPoint(entry_name, first, grants))
        self.touched.add(flow)
        return entry_name

    def rewrite_action(self, flow, original_index, index, event, target, mode):
        super().rewrite_action(flow, original_index, index, event, target, mode)
        actor = self.chart(flow).actors[event.actor]
        if (
            flow in (keys.SMALL, keys.BIG)
            and actor.name == "UISystemActor"
            and actor.actions[event.action] == "EventTriggerRequestOpenPickUpWindow"
            and (event.params or {}).get("ActorName") == evfl.Argument("ContentName")
        ):
            self.selected_argument(flow, index, target)

    def selected_argument(self, flow: str, index: int, target: str) -> None:
        """Use the native get-window's latched actor after grant, never choose the *next* tier again."""
        chart = self.chart(flow)
        original = chart.events[index]
        ai, query = keys._operation(chart, "GameDataActor", "queries", "EventQueryIsGameDataString64")
        choices = []
        tiers = CHAINS[self.families[target]]
        for tier in tiers:
            event = copy.deepcopy(original)
            event.name += f"_{len(chart.events)}"
            event.params["ActorName"] = tier.actor
            choices.append(len(chart.events))
            chart.events.append(event)
        # An unrelated native UI target retains the original base presentation.
        # Every progressive grant sets this target before this continuation.
        first = choices[0]
        for tier, choice in zip(tiers, choices, strict=True):
            for value in dict.fromkeys((tier.actor, tier.owned)):
                first_index = len(chart.events)
                chart.events.append(
                    evfl.SwitchEvent(
                        f"Clawshot_{target}_Selected_{first_index}",
                        ai,
                        query,
                        [(0, choice), (1, first)],
                        {"GameDataName": "UI_MessageTargetActorName", "Index": -1, "Value": value},
                    )
                )
                first = first_index
        chart.events[index] = chart.events.pop()
        chart.events[index].name = original.name


def compile_bindings(documents, rows, analyzed_rows, requests):
    """Source event/family requests; additions only, with both native registries."""
    if not requests:
        return {}, {}
    compiler = _Compiler(documents, rows, analyzed_rows, sorted({family for _, family in requests}))
    for source, family in sorted(set(requests)):
        compiler.bind(source, DungeonGrant(family.replace(" ", ""), "Content").id)
    bindings = {
        (source, family): compiler.bindings[(source, DungeonGrant(family.replace(" ", ""), "Content").id)]
        for source, family in requests
    }
    return bindings, compiler.finish()


def changes(romfs: str | Path, plan: Plan, *, prior_changes: Sequence[FileChanges] = ()) -> tuple[Plan, FileChanges]:
    """Bind progressive chest contents; no global rewrite of fixed native rewards."""
    routed = [change for change in plan.changes if change.item in CHAINS]
    if not routed:
        return plan, {}
    root = Path(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(root)

    def read(path):
        data = dictionaries.decompress(path, (root / path).read_bytes())
        for transforms in prior_changes:
            if transform := transforms.get(path):
                data = transform(data)
        return data

    rows = byml.read(read(keys.SETTINGS))
    analyzed_rows = byml.read(read(keys.ANALYZED))
    game_data = byml.read(read("GameData/GameDataList.Product.110.byml.zs"))["Data"]
    families = sorted({change.item for change in routed})
    for family in families:
        for tier in CHAINS[family]:
            found = [row for row in game_data["Bool"] if row["Hash"] == save_key(f"IsGet.{tier.owned}")]
            if len(found) != 1 or found[0].get("SaveFileIndex") != 0 or found[0].get("ResetTypeValue") != 8:
                raise PatchError(f"{tier.owned}: expected a persistent canonical IsGet Bool, got {found}")
    if "Progressive Magic" in families:
        found = [row for row in game_data["Int"] if row["Hash"] == save_key("PlayerStatus.MPMax")]
        if len(found) != 1 or found[0].get("SaveFileIndex") != 0:
            raise PatchError(f"PlayerStatus.MPMax: expected one native saved capacity field, got {found}")
    needed = {keys.BIG, keys.SMALL, keys.POUCH, "NaviChat"}
    requests = []
    for change in routed:
        source = source_for(change.chest, change.kept_event.name if change.kept_event else None)
        row = next((row for row in rows if row["__RowId"] == source), None)
        if row is None:
            raise PatchError(f"{change.location}: no supported progressive chest source {source}")
        needed.add(Path(row["FlowchartFileName"]).stem)
        requests.append((source, change.item))
    documents = {name: evfl.read(read(keys.flow_path(name))) for name in sorted(needed)}
    bindings, transforms = compile_bindings(documents, rows, analyzed_rows, requests)
    replacements = {
        (change.id, change.files): bindings[request].event for change, request in zip(routed, requests, strict=True)
    }
    return replace(
        plan,
        changes=[
            replace(change, key_event=replacements[(change.id, change.files)])
            if (change.id, change.files) in replacements
            else change
            for change in plan.changes
        ],
    ), transforms
