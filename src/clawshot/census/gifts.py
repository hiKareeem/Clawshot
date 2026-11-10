"""Event gifts: every event-flow step that gives an item by name.

An item is given by one action, ``PouchSystemActor.EventTriggerAddOrRemovePouchContent``, whose ``Actor`` parameter
names the item and ``Num`` the count (negative takes it away: trade items, planted beans). Most flows reach it
through a wrapper entry point that takes the item as an argument (``GetPouchContent:GetPouchContentByActorName``,
``Dm_SY_GetInEvent:*``, ``NpcCommon:NpcCommon_HandOver_*``, ...). :func:`givers` finds those wrappers from the data:
an entry point gives its argument ``A`` when a step reachable from it gives ``Argument(A)``, directly or by passing
it to another giving entry point (a fixed point over all flows). A gift is a step that passes a literal item name to
the action or to such a wrapper (:func:`find_gifts`).

A gift is identified by its flow and step, ``<flow>/<event>`` (rules: AGENTS.md 5, decisions D4). Its kind is
``song`` for a song, ``event_gift`` in a cutscene flow (``Dm_*``) and ``npc_gift`` otherwise.

Left out: steps that take items (``Num`` below 0), and the flows whose items are other census checks or no checks:
the business scrubs' sale flows (each scrub is a census ``scrub``, its offers in its placement) and the
``DreamWorld`` flows (D12: a boss rush with a temporary inventory).

The game loads some flows in a newer version, ``<flow>.<version>.bfevfl.zs``, as
``Event/EventFlow/EventFlowFileEntry.Product.110.byml.zs`` lists (13 flows, version 110); the census reads those.

The five frog-song call sites are variable rupee prizes, not pouch actors. They are censused at
their stable ``TeachNewMusic`` calls with empty ``param`` and ``vanilla_item``; the native
first-song sequence pays 5/10/15/20/30 by prior song count. Round 10 admits them to the
seed pool as Rupees (20), after Kareem's R8-FROGS acceptance (section 40).
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from clawshot.census.scan import BANC_GLOB, EXCLUDED_AREAS, read_romfs_byml
from clawshot.formats import evfl, zsdic

FLOW_DIR = "Event/EventFlow"
FLOW_SUFFIX = ".bfevfl.zs"
FLOW_VERSIONS = "Event/EventFlow/EventFlowFileEntry.Product.110.byml.zs"
EVENT_SETTING = "RSDB/EventSetting.Product.111.rstbl.byml.zs"

GIVE_ACTOR = "PouchSystemActor"
GIVE_ACTION = "EventTriggerAddOrRemovePouchContent"
ITEM_PARAM = "Actor"
COUNT_PARAM = "Num"
DIRECT = f"{GIVE_ACTOR}.{GIVE_ACTION}"

NPC_GIFT = "npc_gift"
SONG = "song"
EVENT_GIFT = "event_gift"
GIFT_KINDS = (NPC_GIFT, SONG, EVENT_GIFT)

SONG_PREFIX = "Item_Melody_"
CUTSCENE_PREFIX = "Dm_"
FROG_SONG_CALL = "MiniGame_FrogTenors:TeachNewMusic"
FROG_SONG_FLAGS = {
    "Event172": "MiniGame_FrogTenors_ZeldaLullaby",
    "Event220": "MiniGame_FrogTenors_EponaSong",
    "Event221": "MiniGame_FrogTenors_SariaSong",
    "Event222": "MiniGame_FrogTenors_SunSong",
    "Event223": "MiniGame_FrogTenors_TimeSong",
}

# Flows left out (see the module docstring): business scrub sales, and the DreamWorld boss rush.
EXCLUDED_FLOWS = frozenset(
    {
        "Enemy_Scrub_Business_Common",
        "Enemy_Scrub_Business_Seed",
        "Enemy_Scrub_Business_Dream",
        "SubEvent_AllBossBattle",
    }
)


class GiftError(ValueError):
    pass


@dataclass(frozen=True)
class Gift:
    id: str  # "<flow>/<event>"
    kind: str
    flow: str
    file: str  # the romfs path read for the flow
    entries: tuple[str, ...]  # entry points of the flow from which the step is reached, sorted
    event: str  # the step
    call: str  # DIRECT, or "<flow>:<entry>" of the wrapper the step calls
    param: str  # item parameter; empty for the frogs' variable-rupee call sites
    vanilla_item: str  # actor name; empty when the native prize is variable rupees, not an actor
    area: str  # the Banc folder that starts the flow, "" when the placements name none or several


def _successors(event) -> list[int]:
    out = [i for _, i in getattr(event, "cases", ()) if i != evfl.NONE]
    nxt = getattr(event, "next", evfl.NONE)
    if nxt != evfl.NONE:
        out.append(nxt)
    if isinstance(event, evfl.ForkEvent):
        out += [*event.forks, event.join]
    return out


def reachable(flowchart: evfl.Flowchart, start: int) -> set[int]:
    """Indices of the events run from ``start`` within one flowchart (not into the entry points it calls)."""
    seen: set[int] = set()
    stack = [] if start == evfl.NONE else [start]
    while stack:
        i = stack.pop()
        if i not in seen:
            seen.add(i)
            stack += _successors(flowchart.events[i])
    return seen


def _is_give(flowchart: evfl.Flowchart, event) -> bool:
    if not isinstance(event, evfl.ActionEvent):
        return False
    actor = flowchart.actors[event.actor]
    return actor.name == GIVE_ACTOR and actor.actions[event.action] == GIVE_ACTION


def _takes(event) -> bool:
    count = (event.params or {}).get(COUNT_PARAM)
    return isinstance(count, int) and not isinstance(count, bool) and count < 0


def _callee(flow: str, event) -> tuple[str, str] | None:
    if isinstance(event, evfl.SubFlowEvent | evfl.SubFlowSwitchEvent):
        return (event.flowchart or flow, event.entry_point)
    return None


def givers(flowcharts: Mapping[str, evfl.Flowchart]) -> dict[tuple[str, str], set[str]]:
    """(flow, entry point) -> the names of the arguments it gives as items."""
    steps = {
        (flow, entry.name): sorted(reachable(fc, entry.main_event))
        for flow, fc in flowcharts.items()
        for entry in fc.entry_points
    }
    out: dict[tuple[str, str], set[str]] = {key: set() for key in steps}
    changed = True
    while changed:
        changed = False
        for (flow, entry), indices in steps.items():
            fc = flowcharts[flow]
            for i in indices:
                event = fc.events[i]
                given: set[str] = set()
                if _is_give(fc, event) and not _takes(event):
                    item = (event.params or {}).get(ITEM_PARAM)
                    if isinstance(item, evfl.Argument):
                        given.add(str(item))
                callee = _callee(flow, event)
                if callee is not None:
                    for param in out.get(callee, ()):
                        value = (event.params or {}).get(param)
                        if isinstance(value, evfl.Argument):
                            given.add(str(value))
                if not given <= out[(flow, entry)]:
                    out[(flow, entry)] |= given
                    changed = True
    return out


def kind_of(flow: str, item: str) -> str:
    if item.startswith(SONG_PREFIX):
        return SONG
    return EVENT_GIFT if flow.startswith(CUTSCENE_PREFIX) else NPC_GIFT


def find_gifts(
    flowcharts: Mapping[str, evfl.Flowchart], files: Mapping[str, str], areas: Mapping[str, str] = {}
) -> list[Gift]:
    """The gifts in ``flowcharts`` (flow name -> flowchart), read from ``files`` (flow name -> romfs path), with the
    Banc area that starts each flow where known. Sorted by flow, then event index."""
    gives = givers(flowcharts)
    out = []
    for flow in sorted(flowcharts):
        if flow in EXCLUDED_FLOWS:
            continue
        fc = flowcharts[flow]
        entries_of: dict[int, list[str]] = {}
        for entry in fc.entry_points:
            for i in reachable(fc, entry.main_event):
                entries_of.setdefault(i, []).append(entry.name)
        for i, event in enumerate(fc.events):
            found = []
            if _is_give(fc, event) and not _takes(event):
                found.append((DIRECT, ITEM_PARAM))
            callee = _callee(flow, event)
            if callee is not None:
                found += [(f"{callee[0]}:{callee[1]}", param) for param in sorted(gives.get(callee, ()))]
            # Bottle fills do not pass through the pouch-add wrapper fixed point. This dedicated
            # Granny sale still has one literal item identity; its price/bottle checks stay in her flow.
            if flow == "Npc_Hylia_053_Adult" and callee == ("Dm_SY_GetInEvent", "GetInEventInBottle_BlueBottleShop"):
                found.append((f"{callee[0]}:{callee[1]}", "ActorName"))
            for call, param in found:
                item = (event.params or {}).get(param)
                if not isinstance(item, str) or isinstance(item, evfl.Argument):
                    continue
                out.append(
                    Gift(
                        id=f"{flow}/{event.name}",
                        kind=kind_of(flow, item),
                        flow=flow,
                        file=files[flow],
                        entries=tuple(sorted(entries_of.get(i, ()))),
                        event=event.name,
                        call=call,
                        param=param,
                        vanilla_item=item,
                        area=areas.get(flow, ""),
                    )
                )
            if callee == ("MiniGame_FrogTenors", "TeachNewMusic") and flow == "MiniGame_FrogTenors":
                flag = (event.params or {}).get("GameDataName")
                if flag != FROG_SONG_FLAGS.get(event.name) or isinstance(flag, evfl.Argument):
                    raise GiftError(f"{flow}/{event.name}: unexpected frog song completion flag {flag!r}")
                out.append(
                    Gift(
                        f"{flow}/{event.name}",
                        NPC_GIFT,
                        flow,
                        files[flow],
                        tuple(sorted(entries_of.get(i, ()))),
                        event.name,
                        FROG_SONG_CALL,
                        "",
                        "",
                        areas.get(flow, ""),
                    )
                )
    ids = [g.id for g in out]
    if len(set(ids)) != len(ids):
        raise GiftError(f"a step gives two items: {sorted({i for i in ids if ids.count(i) > 1})}")
    return out


def flow_files(romfs: Path, versions: Mapping[str, str]) -> dict[str, str]:
    """Flow name -> the romfs path of the file the game loads (``<flow>.<version>.bfevfl.zs`` where listed)."""
    out = {}
    for path in sorted((romfs / FLOW_DIR).glob("*" + FLOW_SUFFIX)):
        stem = path.name.removesuffix(FLOW_SUFFIX)
        flow, _, version = stem.partition(".")
        if version and versions.get(flow) != version:
            continue
        if not version and flow in versions:
            continue
        out[flow] = path.relative_to(romfs).as_posix()
    missing = sorted(set(versions) - set(out))
    if missing:
        raise GiftError(f"versioned flows not found: {missing}")
    return out


def _strings(value, out: set[str]) -> None:
    if isinstance(value, Mapping):
        for v in value.values():
            _strings(v, out)
    elif isinstance(value, list):
        for v in value:
            _strings(v, out)
    elif isinstance(value, str):
        out.add(value)


def flow_areas(banc: Mapping[str, object], event_settings: Iterable[Mapping]) -> dict[str, str]:
    """Flow name -> the one Banc area whose placements start it: an actor named like the flow (an NPC runs its own
    flow) or an actor parameter naming one of the flow's ``EventSetting`` rows. Flows placed in several areas or in
    none are left out."""
    flow_of_row = {}
    for row in event_settings:
        if "FlowchartFileName" in row:
            flow_of_row[str(row["__RowId"])] = PurePosixPath(str(row["FlowchartFileName"])).stem
    found: dict[str, set[str]] = {}
    for path, tree in banc.items():
        area = PurePosixPath(path).parts[1]
        if area in EXCLUDED_AREAS:
            continue
        for actor in tree.get("Actors", []) if isinstance(tree, Mapping) else []:
            found.setdefault(str(actor["Gyaml"]), set()).add(area)
            names: set[str] = set()
            _strings(actor.get("Dynamic") or {}, names)
            for name in names & flow_of_row.keys():
                found.setdefault(flow_of_row[name], set()).add(area)
    return {flow: areas.pop() for flow, areas in found.items() if len(areas) == 1}


def scan_gifts(romfs: str | Path, banc: Mapping[str, object] | None = None) -> list[Gift]:
    """Every gift in the dump at ``romfs`` (read only). ``banc`` (romfs path -> placement tree) saves reading the
    placement files again when the caller has them."""

    romfs = Path(romfs)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    versions = {str(k): str(v) for k, v in read_romfs_byml(romfs, dicts, FLOW_VERSIONS)["Versions"].items()}
    files = flow_files(romfs, versions)
    flowcharts = {}
    for flow, path in files.items():
        tree = evfl.read(dicts.decompress(path, (romfs / path).read_bytes()))
        if tree.flowchart is not None:
            flowcharts[flow] = tree.flowchart
    if banc is None:
        paths = sorted(p.relative_to(romfs).as_posix() for p in romfs.glob(BANC_GLOB))
        banc = {path: read_romfs_byml(romfs, dicts, path) for path in paths}
    areas = flow_areas(banc, read_romfs_byml(romfs, dicts, EVENT_SETTING))
    return find_gifts(flowcharts, files, areas)
