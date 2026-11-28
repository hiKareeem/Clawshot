"""Saria's farewell without her doubled ocarina (spec event-items section 4; plan tasks 12, 13; decision Q2/D9: every
seed).

Kokiri Forest places four Sarias that share one schedule list (``Component/AIScheduleParam/Npc_Kokiri_Saria_Child``).
Its ``WarpDone`` entry (her sitting on the rock playing her ocarina) sets the equipment state ``Hold``. Before Gohma
that entry also applies to the farewell's Saria, the separate placement ``KokiriForest_ArriveLostWood`` at the bridge,
so she exists holding her own ``Npc_Equipment_009`` on ``Weapon_R`` when the farewell starts, and the scene's ocarina
prop is drawn beside it: doubled at the presenting timeline's start, mirrored in the hand-over (played, Longshot 3.2.0,
no mod: BBender 2026-11-25). The unmodified game only plays the farewell after Gohma, when no entry holds.

As the game does for the Sacred Forest Meadow Saria, the bridge placement gets an actor of her own,
:data:`FAREWELL`: Saria's pack with its ActorParam renamed and ``AIScheduleRef`` pointing at her own schedule list,
which is Saria's without ``Hold`` on the ``WarpDone`` entry; ActorInfo and GameActorInfo rows copied from Saria's;
and the three flows that name that instance name the new actor. Every other Saria keeps the native actor and list.
Played clean before, during and after the farewell (arm N9, BBender, 2026-11-25; ``plans/event-items.md``).
"""

import bisect
import copy
from collections.abc import Callable, Mapping
from pathlib import Path

from clawshot.census.gifts import FLOW_VERSIONS
from clawshot.census.hints import flow_path
from clawshot.formats import byml, evfl, sarc, zsdic
from clawshot.patch.actor_packs import actor_member
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges, NewFile

SARIA = "Npc_Kokiri_Saria_Child"
FAREWELL = "Npc_Kokiri_Saria_Child_Farewell"
INSTANCE = "KokiriForest_ArriveLostWood"
PLACEMENT_FILE = "Banc/KokiriForest/KokiriForest_Child_Static.bcett.byml.zs"
PLACEMENT_HASH = 1660754835063030086
FLOWS = ("Dm_Kokiri_0150", "Dm_Kokiri_0155", "Goto_HyruleCastle")
TABLES = ("RSDB/ActorInfo.Product.111.rstbl.byml.zs", "RSDB/GameActorInfo.Product.111.rstbl.byml.zs")
WARP_DONE = "Npc_Kokiri_Saria_Child_WarpDone"
HOLD_FIELDS = ("EquipmentStateWhenWait", "EquipmentStateWhenWalk")
NAME_PAIRS = (
    ("ActorName", "InstanceName"),
    ("TargetActorName", "TargetActorInstanceName"),
    ("BindActorName", "BindInstanceName"),
)


def schedule_path(actor: str) -> str:
    return f"Component/AIScheduleParam/{actor}.game__component__AIScheduleParam.bgyml"


def pack_path(actor: str) -> str:
    return f"Pack/Actor/{actor}.pack.zs"


def schedule_without_hold(data: bytes) -> bytes:
    """Saria's schedule list without the ``Hold`` equipment states of its ``WarpDone`` entry."""
    document = byml.load(data)
    entries = [e for e in document.root["ConditionalSchedule"] if e.get("ConditionFlag") == WARP_DONE]
    if len(entries) != 1:
        raise PatchError(f"{schedule_path(SARIA)}: {len(entries)} {WARP_DONE} entries, expected one")
    for action in entries[0]["ActionSchedule"]:
        missing = [f for f in HOLD_FIELDS if f not in action["Setting"]]
        if missing:
            raise PatchError(f"{schedule_path(SARIA)}: the {WARP_DONE} entry has no {missing}")
        for field in HOLD_FIELDS:
            action["Setting"].pop(field)
    out = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(out))) is not None:
        raise PatchError(f"{schedule_path(FAREWELL)}: does not read back: {difference}")
    return out


def actor_pack(saria: Mapping[str, bytes]) -> NewFile:
    """:data:`FAREWELL`'s pack from Saria's members: her ActorParam renamed, its schedule her own."""
    if actor_member(SARIA) not in saria:
        raise PatchError(f"{SARIA}: the pack has no {actor_member(SARIA)}")
    pack = dict(saria)
    param = byml.load(pack.pop(actor_member(SARIA)))
    components = param.root.get("Components", {})
    if components.get("AIScheduleRef") != "?" + schedule_path(SARIA):
        raise PatchError(f"{SARIA}: unexpected AIScheduleRef {components.get('AIScheduleRef')!r}")
    components["AIScheduleRef"] = "?" + schedule_path(FAREWELL)
    pack[actor_member(FAREWELL)] = byml.dump(param)
    data = sarc.write(pack)
    if sarc.read(data) != pack:
        raise PatchError(f"{FAREWELL}: the pack does not read back")
    return NewFile(data, copied={m: pack_path(SARIA) for m in pack if m != actor_member(FAREWELL)})


def rows_transform(path: str) -> Callable[[bytes], bytes]:
    """The row table ``path`` with a copy of Saria's row named :data:`FAREWELL`, inserted by name."""

    def transform(data: bytes) -> bytes:
        document = byml.load(data)
        rows = document.root
        keys = [r["__RowId"].encode() for r in rows]
        if FAREWELL.encode() in keys or SARIA.encode() not in keys:
            raise PatchError(f"{path}: {FAREWELL} is there already, or {SARIA} is missing")
        row = {**copy.deepcopy(rows[keys.index(SARIA.encode())]), "__RowId": FAREWELL}
        rows.insert(bisect.bisect_left(keys, FAREWELL.encode()), row)
        out = byml.dump(document)
        if (difference := byml.difference(document.root, byml.read(out))) is not None:
            raise PatchError(f"{path}: does not read back: {difference}")
        return out

    return transform


def placement_transform(data: bytes) -> bytes:
    """Kokiri Forest's static placements with the bridge Saria using :data:`FAREWELL`."""
    document = byml.load(data)
    found = [a for a in document.root["Actors"] if int(a["Hash"]) == PLACEMENT_HASH]
    if len(found) != 1 or found[0]["Gyaml"] != SARIA or found[0].get("Name") != INSTANCE:
        raise PatchError(f"{PLACEMENT_FILE}: Hash {PLACEMENT_HASH} is not {SARIA} {INSTANCE}: {found!r}")
    found[0]["Gyaml"] = FAREWELL
    out = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(out))) is not None:
        raise PatchError(f"{PLACEMENT_FILE}: does not read back: {difference}")
    return out


def _rename_params(params: object) -> int:
    if not isinstance(params, dict):
        return 0
    renamed = 0
    for name_key, instance_key in NAME_PAIRS:
        if params.get(instance_key) == INSTANCE and params.get(name_key) == SARIA:
            params[name_key] = FAREWELL
            renamed += 1
    return renamed


def rename(document: evfl.EventFlowFile) -> int:
    """Name :data:`FAREWELL` wherever ``document`` names Saria's :data:`INSTANCE`, in place; how many names changed."""
    part = document.flowchart or document.timeline
    actors = [a for a in part.actors if (a.name, a.secondary_name) == (SARIA, INSTANCE)]
    if len(actors) != 1:
        raise PatchError(f"{document.name}: {len(actors)} actors {SARIA}/{INSTANCE}, expected one")
    actors[0].name = FAREWELL
    renamed = 1
    for event in getattr(part, "events", []):
        renamed += _rename_params(getattr(event, "params", None))
    for clip in getattr(part, "clips", []):
        renamed += _rename_params(clip.params)
    return renamed


def flow_transform(flow: str) -> Callable[[bytes], bytes]:
    def transform(data: bytes) -> bytes:
        document = evfl.read(data)
        rename(document)
        out = evfl.write(document)
        if evfl.read(out) != document:
            raise PatchError(f"{flow}: the written flow does not read back as the renamed one")
        return out

    return transform


def native_inputs() -> tuple[str, ...]:
    """Every romfs file :func:`changes` and its transforms read (every seed), the dictionaries' pack included, so the
    app's working set (``clawshot.pack.source.working_files``) holds them: Saria's pack and schedule list, the
    placement file and the two actor tables, and the flow versions list that names the three flows' files (the flows
    are every ``Event/EventFlow/*.bfevfl.zs``, which the working set's patterns hold)."""
    return (zsdic.PACK_PATH, FLOW_VERSIONS, pack_path(SARIA), schedule_path(SARIA), PLACEMENT_FILE, *TABLES)


def changes(romfs: str | Path) -> tuple[FileChanges, dict[str, NewFile]]:
    """Every seed's Saria fix: the transforms of the placement, row tables and three flows, and the new actor's pack
    and schedule list (sized from Saria's: the list only shrinks). Reads the dump only."""
    romfs = Path(romfs)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    saria = sarc.read(dicts.decompress(pack_path(SARIA), (romfs / pack_path(SARIA)).read_bytes()))
    native = (romfs / schedule_path(SARIA)).read_bytes()
    schedule = schedule_without_hold(native)
    growth = max(0, (len(schedule) + 31) // 32 * 32 - (len(native) + 31) // 32 * 32)
    new_files = {
        pack_path(FAREWELL): actor_pack(saria),
        schedule_path(FAREWELL): NewFile(schedule, sized_like=(schedule_path(SARIA), growth)),
    }
    transforms: dict[str, Callable[[bytes], bytes]] = {PLACEMENT_FILE: placement_transform}
    transforms.update({path: rows_transform(path) for path in TABLES})
    transforms.update({flow_path(romfs, flow): flow_transform(flow) for flow in FLOWS})
    return transforms, new_files
