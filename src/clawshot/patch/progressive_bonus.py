"""Native bonuses outside the copy count: guard unsafe strength/scale source grants.

Queries live in the already-preloaded GetPouchContent system actor, not a new
actor in Darunia's movie. Safe capacity/Single Magic handlers remain native.
"""

import copy
from collections.abc import Sequence
from pathlib import Path

from clawshot.census import definitions
from clawshot.census.gifts import FLOW_VERSIONS, flow_files
from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import keys
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges
from clawshot.progressive import CHAINS, FAMILY_BY_ITEM


def guard_grants(source: evfl.Flowchart, pouch: evfl.Flowchart, grants: dict[str, str]) -> None:
    """Specialize only the native source call; skip returns to its original quest/once continuation."""
    by_actor = {tier.actor: (family, index) for family, tiers in CHAINS.items() for index, tier in enumerate(tiers)}
    for name, content in sorted(grants.items()):
        matches = [index for index, event in enumerate(source.events) if event.name == name]
        if len(matches) != 1:
            raise PatchError(f"{source.name}/{name}: expected one native bonus grant, got {matches}")
        index = matches[0]
        original = source.events[index]
        if not isinstance(original, evfl.SubFlowEvent):
            raise PatchError(f"{source.name}/{name}: not a native bonus subflow grant: {original}")
        arguments = [
            key
            for key, value in (original.params or {}).items()
            if value == content and not isinstance(value, evfl.Argument)
        ]
        if len(arguments) != 1:
            raise PatchError(f"{source.name}/{name}: native bonus no longer gives {content}: {original}")
        family, tier_index = by_actor[content]
        if family not in {"Progressive Strength", "Progressive Scale"}:
            raise PatchError(f"{source.name}/{name}: {family} is natively monotone, not an unsafe bonus")
        tiers = CHAINS[family][tier_index:]
        if family == "Progressive Strength" and tier_index == 0:
            # Adult gauntlets are not child Bracelet ownership. Never deny the
            # separate child item merely because an adult tier is present.
            tiers = CHAINS[family][:1]
        entry_name = f"Clawshot_Bonus_{source.name}_{name}"
        if any(entry.name == entry_name for entry in pouch.entry_points):
            raise PatchError(f"{source.name}/{name}: native bonus guard already exists")
        ai, query = keys._operation(pouch, "GameDataActor", "queries", "EventQueryIsGameDataBool")
        give = len(pouch.events)
        pouch.events.append(
            evfl.SubFlowEvent(
                entry_name + "_Give",
                original.flowchart or source.name,
                original.entry_point,
                params={key: evfl.Argument(key) for key in (original.params or {})},
            )
        )
        first = give
        for tier in tiers:
            gate = len(pouch.events)
            pouch.events.append(
                evfl.SwitchEvent(
                    f"{entry_name}_{gate}",
                    ai,
                    query,
                    [(0, evfl.NONE), (1, first)],
                    {"GameDataName": f"IsGet.{tier.owned}", "Index": -1},
                )
            )
            first = gate
        pouch.entry_points.append(evfl.EntryPoint(entry_name, first, [give]))
        source.events[index] = evfl.SubFlowEvent(
            original.name,
            keys.POUCH,
            entry_name,
            original.next,
            copy.deepcopy(original.params),
        )


def _source_transform(original, changed):
    encoded = evfl.write(changed)
    if evfl.read(encoded) != changed:
        raise PatchError(f"{changed.name}: native bonus guard read-back differs")

    def transform(data):
        if evfl.read(data) != original:
            raise PatchError(f"{original.name}: native bonus source changed after binding")
        return encoded

    return transform


def changes(romfs: str | Path, seed, *, prior_changes: Sequence[FileChanges] = ()) -> FileChanges:
    """Protect unshuffled native gifts; safe capacity and magic grants stay native."""
    if not seed.world.progressive_copies_only:
        return {}
    moving = set(seed.shuffled)
    sources = {
        name
        for name, location in seed.world.locations.items()
        if name not in moving and FAMILY_BY_ITEM.get(location.vanilla) in {"Progressive Strength", "Progressive Scale"}
    }
    grouped: dict[str, dict[str, str]] = {}
    for definition in definitions.load():
        name = definition.oot_randomizer_name or definition.name
        if name not in sources or not isinstance(definition.id, str):
            continue
        flow, event = definition.id.split("/")
        grouped.setdefault(flow, {})[event] = definition.vanilla_item
    if not grouped:
        return {}
    root = Path(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(root)

    def read(path):
        data = dictionaries.decompress(path, (root / path).read_bytes())
        for previous in prior_changes:
            if transform := previous.get(path):
                data = transform(data)
        return data

    versions = byml.read(read(FLOW_VERSIONS))["Versions"]
    files = flow_files(root, {str(key): str(value) for key, value in versions.items()})
    pouch_path = files[keys.POUCH]
    original_pouch = evfl.read(read(pouch_path))
    pouch = copy.deepcopy(original_pouch)
    rows = byml.read(read(keys.SETTINGS))
    analyzed = {row["__RowId"]: row for row in byml.read(read(keys.ANALYZED))}
    transforms = {}
    for flow, grants in sorted(grouped.items()):
        path = files[flow]
        original = evfl.read(read(path))
        if original.flowchart is None or pouch.flowchart is None:
            raise PatchError(f"{flow}: native bonus needs source and pouch flowcharts")
        indices = {index for index, event in enumerate(original.flowchart.events) if event.name in grants}
        for row in rows:
            same_flow = Path(row.get("FlowchartFileName", "")).stem == flow
            timeline = not row.get("FlowchartFileName") and row["__RowId"] == flow
            if not same_flow and not timeline:
                continue
            relevant = bool(indices)
            if same_flow:
                entry = original.flowchart.entry_point(row.get("EntryPointName") or "EntryPoint0")
                relevant = bool(indices & keys._reachable(original.flowchart, entry.main_event))
            if relevant:
                registered = analyzed.get(row["__RowId"], {})
                if keys.POUCH not in registered.get("SubFlowList", ()):
                    raise PatchError(f"{row['__RowId']}: native bonus lacks existing pouch preload: {registered}")
        changed = copy.deepcopy(original)
        guard_grants(changed.flowchart, pouch.flowchart, grants)
        transforms[path] = _source_transform(original, changed)
    transforms[pouch_path] = keys._append_flow(original_pouch, pouch)
    return transforms
