"""Guard against newly undeclared event dependencies: a suspected risk, not a proven freeze cause.

The structural model relates ``RSDB/EventSetting`` roots to ``GameAnalyzedEventInfo`` declarations:
``SubFlowList`` covers reachable external flowcharts and ``ChildEventList`` static ``EventTransition`` targets.
Each entry point's ``sub_flow_events`` covers its reachable local and external calls. The supported dump mostly
follows this model, but that does not establish that every undeclared dependency prevents runtime execution.

Sword v3 and cows v1 had both registration gaps and blocking waits; the unowned equipment wait is sword v4's primary
cause hypothesis. Registration is secondary and unproven. The Market bottle repeat/shop path was played successfully
with its gaps (R10-MARKET-BOTTLE-FIX), so those exact gaps have one named allowance, not a production behavior change.
Synthetic negatives preserve the v3/cows shapes as precautionary guards. Real-dump tests compose all modified flows
through production seeds and reject new risks except that exact played allowance and inherited native debt.
"""

import copy
import functools
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from unittest import mock

import pytest
from dampe_flow import assert_first_race_cycle

from clawshot.census.gifts import FLOW_DIR, FLOW_SUFFIX, FLOW_VERSIONS, flow_files, reachable
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import byml, evfl, zsdic
from clawshot.generate import Settings, from_placements
from clawshot.generate.fill import FillError, allowed, with_screens
from clawshot.patch import SeedOutput, gifts, make_seed, scrubs
from clawshot.patch.keys import ANALYZED, SETTINGS
from clawshot.world.load import load_spec

CALLS = (evfl.SubFlowEvent, evfl.SubFlowSwitchEvent)

# Where a declaration is missing (Gap.registry).
SUB_FLOWS = "GameAnalyzedEventInfo.SubFlowList"
CHILDREN = "GameAnalyzedEventInfo.ChildEventList"
ANALYZED_ROW = "GameAnalyzedEventInfo row"
SETTING_ROW = "EventSetting row"  # of a transition's target event
START = "EventSetting FlowchartFileName/EntryPointName"
ENTRY_CALLS = "entry point sub_flow_events"
CALL_TARGET = "called flowchart entry point"


@dataclass(frozen=True, order=True)
class Gap:
    """``owner`` (an EventSetting row, ``flow:entry`` or ``flow/event``) needs ``target`` declared in ``registry``."""

    registry: str
    owner: str
    target: str

    def __str__(self) -> str:
        return f"{self.owner}: {self.target or '(its row)'} missing from {self.registry}"


# Supported dump's inherited gaps (1.1.1); newly introduced gaps need the exact played allowance below.
NATIVE_DEBT = frozenset(
    {
        # The one EventSetting row without an analyzed row (and without a flowchart).
        Gap(ANALYZED_ROW, "PlayOcarina_ReplaceEvent", ""),
        # A self-transition.
        Gap(CHILDREN, "Step03_Npc_SkullKid_Child_Talk", "Step03_Npc_SkullKid_Child_Talk"),
        # Rows without an entry point name whose analysis does not cover their flowchart's first entry point.
        *(
            Gap(registry, row, target)
            for row in ("BancChangeArrive_DungeonWarp_Base", "BancChangeGo_DungeonWarp_Base")
            for registry, target in (
                (SUB_FLOWS, "DoorOfTime"),
                (SUB_FLOWS, "NaviChat"),
                (SUB_FLOWS, "SubEvent_GetEponaSong"),
                (CHILDREN, "Dm_ZoraFountain_0020"),
                (CHILDREN, "Dm_ZoraFountain_0030"),
            )
        ),
        Gap(SUB_FLOWS, "HountedWasteland_Field_Restart", "NaviEventCommon"),
    }
)

# ONE played exception, not a blanket exemption for this flow or gifts. Kareem, 2026-11-10:
# plans/playtest/answers.md R10-MARKET-BOTTLE-FIX: decline, accept, leave/re-enter, TALK AGAIN, SHOP,
# Save/Continue: "All checks out, no issues." Claude directed preserving gifts._market_bottle, 2026-11-20.
PLAYED_MARKET_BOTTLE_ALLOWANCE = frozenset(
    {
        *(
            Gap(ENTRY_CALLS, "Npc_Hylia_020_Shop_Child:Item_Bottle_TutorialEvent_Talk", event)
            for event in ("Event19", "Event25", "Event88", "Event118", "Event107", "Event126", "Event160", "Event140")
        ),
        *(Gap(SUB_FLOWS, "Npc_Hylia_020_Shop_Child_D_T", flow) for flow in ("DisplayShop", "Dm_SY_ShopGet")),
    }
)


def _transition(chart: evfl.Flowchart, event: evfl.Event) -> str | None:
    """The static event name an ``EventSystemActor.EventTransition`` starts (an argument-valued one is dynamic)."""
    if not isinstance(event, evfl.ActionEvent):
        return None
    actor = chart.actors[event.actor]
    if actor.name != "EventSystemActor" or actor.actions[event.action] != "EventTransition":
        return None
    name = (event.params or {}).get("EventName")
    return name if isinstance(name, str) and not isinstance(name, evfl.Argument) else None


@dataclass(frozen=True)
class Entry:
    """What one entry point reaches inside its own flowchart."""

    calls: frozenset[tuple[str, str]]  # (flowchart, entry point) of each sub-flow call, local or external
    children: frozenset[str]


def entries(charts: Mapping[str, evfl.Flowchart]) -> dict[tuple[str, str], Entry]:
    out = {}
    for flow, chart in charts.items():
        for entry in chart.entry_points:
            reached = [chart.events[i] for i in reachable(chart, entry.main_event)]
            calls = {(event.flowchart or flow, event.entry_point) for event in reached if isinstance(event, CALLS)}
            children = {_transition(chart, event) for event in reached} - {None}
            out[(flow, entry.name)] = Entry(frozenset(calls), frozenset(children))
    return out


def start(row: Mapping, charts: Mapping[str, evfl.Flowchart]) -> tuple[str, str] | None:
    """The ``(flowchart, entry point)`` an EventSetting row starts, or ``None`` for a row without a flowchart."""
    if "FlowchartFileName" not in row:
        return None
    flow = PurePosixPath(str(row["FlowchartFileName"])).stem
    if "EntryPointName" in row:
        return flow, str(row["EntryPointName"])
    chart = charts.get(flow)
    return flow, chart.entry_points[0].name if chart is not None and chart.entry_points else ""


def closure(graph: Mapping[tuple[str, str], Entry], root: tuple[str, str]) -> tuple[set[tuple[str, str]], set[str]]:
    """Every entry point an event started at ``root`` runs, and every event it transitions to."""
    seen, children, pending = set(), set(), [root]
    while pending:
        node = pending.pop()
        if node in seen or node not in graph:
            continue
        seen.add(node)
        children |= graph[node].children
        pending.extend(graph[node].calls)
    return seen, children


def registration_gaps(
    charts: Mapping[str, evfl.Flowchart], settings: Sequence[Mapping], analyzed: Sequence[Mapping]
) -> set[Gap]:
    """Every dependency of every flowchart entry point and EventSetting row that its registry does not declare."""
    gaps = set()
    graph = entries(charts)
    for flow, chart in charts.items():
        for entry in chart.entry_points:
            for index in sorted(reachable(chart, entry.main_event)):
                event = chart.events[index]
                if not isinstance(event, CALLS):
                    continue
                if index not in entry.sub_flow_events:
                    gaps.add(Gap(ENTRY_CALLS, f"{flow}:{entry.name}", event.name))
                called = (event.flowchart or flow, event.entry_point)
                if called not in graph:
                    gaps.add(Gap(CALL_TARGET, f"{flow}/{event.name}", ":".join(called)))
    declared = {str(row["__RowId"]): row for row in analyzed}
    events = {str(row["__RowId"]) for row in settings}
    for row in settings:
        name, root = str(row["__RowId"]), start(row, charts)
        if name not in declared:
            gaps.add(Gap(ANALYZED_ROW, name, ""))
        if root is None:
            continue
        if root not in graph:
            gaps.add(Gap(START, name, ":".join(root)))
            continue
        if name not in declared:
            continue
        reached, children = closure(graph, root)
        flows = {flow for flow, _ in reached} | {flow for node in reached for flow, _ in graph[node].calls}
        sub_flows, child_events = (set(declared[name].get(key, ())) for key in ("SubFlowList", "ChildEventList"))
        gaps |= {Gap(SUB_FLOWS, name, flow) for flow in flows - {root[0]} - sub_flows}
        gaps |= {Gap(CHILDREN, name, child) for child in children - child_events}
        gaps |= {Gap(SETTING_ROW, name, child) for child in children - events}
    return gaps


def checked_entries(charts: Mapping[str, evfl.Flowchart], settings: Sequence[Mapping]) -> set[tuple[str, str]]:
    """The entry points some EventSetting row's event runs: the ones whose dependencies a row must declare."""
    graph = entries(charts)
    out = set()
    for row in settings:
        if (root := start(row, charts)) is not None:
            out |= closure(graph, root)[0]
    return out


def changed_dependencies(
    before: Mapping[str, evfl.Flowchart], after: Mapping[str, evfl.Flowchart]
) -> set[tuple[str, str]]:
    """Entry points of ``after`` that call or transition to something they did not in ``before``."""
    old, out = entries(before), set()
    for node, entry in entries(after).items():
        native = old.get(node, Entry(frozenset(), frozenset()))
        if entry.calls - native.calls or entry.children - native.children:
            out.add(node)
    return out


@dataclass
class World:
    charts: dict[str, evfl.Flowchart]
    settings: list[dict]
    analyzed: list[dict]

    def gaps(self) -> set[Gap]:
        return registration_gaps(self.charts, self.settings, self.analyzed)

    def analyzed_row(self, name: str) -> dict:
        return next(row for row in self.analyzed if row["__RowId"] == name)


# --- synthetic flows ------------------------------------------------------------------------------------------------


def _chart(name, events, entry_points, actors=None):
    return evfl.Flowchart(name, actors=actors or [], events=events, entry_points=entry_points)


def _row(name, flow, entry=None):
    row = {"__RowId": name, "FlowchartFileName": f"Work/Event/EventFlow/{flow}.evfc"}
    if entry is not None:
        row["EntryPointName"] = entry
    return row


def native_world() -> World:
    """Native-shaped events: the pedestal arrival pans its camera and transitions on; a cow fills a bottle through the
    shared bottle get, which grants through the pouch; an NPC's talk gives through ``Dm_SY_Get``; a shopkeeper's talk
    opens the shop, her tutorial does not."""
    charts = {
        "Dm_TimeTemple_0085": _chart(
            "Dm_TimeTemple_0085",
            [
                evfl.SubFlowEvent("Event0", "Common_Camera_Pln", "Pan", 1),
                evfl.ActionEvent("Event1", 0, 0, evfl.NONE, {"EventName": "Dm_TimeTemple_0090"}),
            ],
            [evfl.EntryPoint("Dm_TimeTemple_0085", 0, [0])],
            [evfl.Actor("EventSystemActor", actions=["EventTransition"])],
        ),
        "Dm_TimeTemple_0090": _chart("Dm_TimeTemple_0090", [], [evfl.EntryPoint("Dm_TimeTemple_0090")]),
        "Common_Camera_Pln": _chart("Common_Camera_Pln", [], [evfl.EntryPoint("Pan")]),
        "Animal_Cow": _chart(
            "Animal_Cow",
            [evfl.SubFlowEvent("Event6", "Dm_SY_GetInEvent", "GetInEventInBottle")],
            [evfl.EntryPoint("PushToBottleMilk", 0, [0])],
        ),
        "Dm_SY_GetInEvent": _chart(
            "Dm_SY_GetInEvent",
            [evfl.SubFlowEvent("Event2", "GetPouchContent", "GetPouchContentByActorName")],
            [evfl.EntryPoint("GetInEventInBottle", 0, [0])],
        ),
        "GetPouchContent": _chart("GetPouchContent", [], [evfl.EntryPoint("GetPouchContentByActorName")]),
        "Npc_Talker": _chart(
            "Npc_Talker",
            [evfl.SubFlowEvent("Event3", "Dm_SY_Get", "Get")],
            [evfl.EntryPoint("Talk", 0, [0]), evfl.EntryPoint("Near")],
        ),
        "Dm_SY_Get": _chart("Dm_SY_Get", [], [evfl.EntryPoint("Get")]),
        "Npc_Hylia_020_Shop_Child": _chart(
            "Npc_Hylia_020_Shop_Child",
            [evfl.SubFlowEvent("Event19", "DisplayShop", "Root_Buy")],
            [evfl.EntryPoint("Talk", 0, [0]), evfl.EntryPoint("Item_Bottle_TutorialEvent_Talk")],
            [evfl.Actor("GameDataActor", queries=["EventQueryIsGameDataBool"])],
        ),
        "DisplayShop": _chart("DisplayShop", [], [evfl.EntryPoint("Root_Buy")]),
    }
    settings = [
        _row("Dm_TimeTemple_0085", "Dm_TimeTemple_0085", "Dm_TimeTemple_0085"),
        _row("Dm_TimeTemple_0090", "Dm_TimeTemple_0090", "Dm_TimeTemple_0090"),
        _row("Animal_Cow_PushToBottleMilk", "Animal_Cow", "PushToBottleMilk"),
        _row("Npc_Talker_Talk", "Npc_Talker"),  # no entry point name: the first one, Talk
        _row("Dm_SY_Get", "Dm_SY_Get", "Get"),
        _row("Npc_Hylia_020_Shop_Child_C0C1_TT", "Npc_Hylia_020_Shop_Child", "Talk"),
        _row("Npc_Hylia_020_Shop_Child_D_T", "Npc_Hylia_020_Shop_Child", "Item_Bottle_TutorialEvent_Talk"),
    ]
    analyzed = [
        {
            "__RowId": "Dm_TimeTemple_0085",
            "SubFlowList": ["Common_Camera_Pln"],
            "ChildEventList": ["Dm_TimeTemple_0090"],
        },
        {"__RowId": "Dm_TimeTemple_0090"},
        {"__RowId": "Animal_Cow_PushToBottleMilk", "SubFlowList": ["Dm_SY_GetInEvent", "GetPouchContent"]},
        {"__RowId": "Npc_Talker_Talk", "SubFlowList": ["Dm_SY_Get"]},
        {"__RowId": "Dm_SY_Get"},
        {"__RowId": "Npc_Hylia_020_Shop_Child_C0C1_TT", "SubFlowList": ["DisplayShop"]},
        {"__RowId": "Npc_Hylia_020_Shop_Child_D_T"},
    ]
    return World(charts, settings, analyzed)


def added(world: World) -> list[Gap]:
    return sorted(world.gaps() - native_world().gaps())


def era_helper(world: World) -> None:
    """The v3 shape: arrival asks a new external helper through a SubFlowSwitch, registered per entry point."""
    world.charts["ClawshotSwordEra"] = _chart(
        "ClawshotSwordEra",
        [evfl.ReturnEvent("Owned", 0), evfl.ReturnEvent("Unowned", 1)],
        [evfl.EntryPoint("IsOwned", 0)],
    )
    arrival = world.charts["Dm_TimeTemple_0085"]
    switch = len(arrival.events)
    arrival.events.append(evfl.SubFlowSwitchEvent("ClawshotEraOwned", "ClawshotSwordEra", "IsOwned", [(0, 1), (1, 1)]))
    arrival.events[0].next = switch
    arrival.entry_points[0].sub_flow_events.append(switch)


def test_native_shapes_have_no_gap():
    assert native_world().gaps() == set()


def test_v3_external_helper_absent_from_analyzed_sub_flows_fails():
    world = native_world()
    era_helper(world)
    assert added(world) == [Gap(SUB_FLOWS, "Dm_TimeTemple_0085", "ClawshotSwordEra")]
    world.analyzed_row("Dm_TimeTemple_0085")["SubFlowList"].append("ClawshotSwordEra")
    assert added(world) == []


def test_cows_v1_appended_external_call_without_entry_registration_fails():
    """The appended call reaches a flowchart the row already declares; only the entry point's table lacks it."""
    world = native_world()
    cow = world.charts["Animal_Cow"]
    cow.events.append(evfl.SubFlowEvent("ClawshotCowGrant", "GetPouchContent", "GetPouchContentByActorName"))
    cow.events[0].next = 1
    assert added(world) == [Gap(ENTRY_CALLS, "Animal_Cow:PushToBottleMilk", "ClawshotCowGrant")]
    cow.entry_points[0].sub_flow_events.append(1)
    assert added(world) == []


def test_undeclared_external_call_is_reported_against_both_registries():
    world = native_world()
    cow = world.charts["Animal_Cow"]
    cow.events.append(evfl.SubFlowSwitchEvent("ClawshotCowOwned", "ClawshotCowRule", "Owned", [(0, evfl.NONE)]))
    cow.events[0].next = 1
    world.charts["ClawshotCowRule"] = _chart(
        "ClawshotCowRule", [evfl.ReturnEvent("Yes", 0)], [evfl.EntryPoint("Owned", 0)]
    )
    assert added(world) == [
        Gap(SUB_FLOWS, "Animal_Cow_PushToBottleMilk", "ClawshotCowRule"),
        Gap(ENTRY_CALLS, "Animal_Cow:PushToBottleMilk", "ClawshotCowOwned"),
    ]


def test_call_added_inside_a_callee_needs_every_calling_row():
    """``Dm_SY_Get`` is the root of its own row and a callee of the talk: both must name the new flowchart."""
    world = native_world()
    get = world.charts["Dm_SY_Get"]
    get.events.append(evfl.SubFlowEvent("ClawshotGrant", "GetPouchContent", "GetPouchContentByActorName"))
    get.entry_points[0].main_event = 0
    get.entry_points[0].sub_flow_events.append(0)
    assert added(world) == [
        Gap(SUB_FLOWS, "Dm_SY_Get", "GetPouchContent"),
        Gap(SUB_FLOWS, "Npc_Talker_Talk", "GetPouchContent"),
    ]


def test_gate_into_another_entry_points_native_calls_needs_their_registration():
    """The Market bottle tutorial's completion gate shape: a revisit is sent into the shop talk's native calls, which
    only the talk's entry point and row declare."""
    world = native_world()
    shop = world.charts["Npc_Hylia_020_Shop_Child"]
    shop.events.append(evfl.SwitchEvent("ClawshotGift1", 0, 0, [(0, 0), (1, evfl.NONE)], {"GameDataName": "Present"}))
    shop.entry_point("Item_Bottle_TutorialEvent_Talk").main_event = 1
    assert added(world) == [
        Gap(SUB_FLOWS, "Npc_Hylia_020_Shop_Child_D_T", "DisplayShop"),
        Gap(ENTRY_CALLS, "Npc_Hylia_020_Shop_Child:Item_Bottle_TutorialEvent_Talk", "Event19"),
    ]


def test_added_transition_needs_child_list_and_event_setting_row():
    world = native_world()
    world.charts["Dm_TimeTemple_0085"].events[1].params = {"EventName": "Clawshot_Arrival"}
    assert added(world) == [
        Gap(SETTING_ROW, "Dm_TimeTemple_0085", "Clawshot_Arrival"),
        Gap(CHILDREN, "Dm_TimeTemple_0085", "Clawshot_Arrival"),
    ]
    world.analyzed_row("Dm_TimeTemple_0085")["ChildEventList"].append("Clawshot_Arrival")
    world.settings.append(_row("Clawshot_Arrival", "Dm_TimeTemple_0090", "Dm_TimeTemple_0090"))
    assert added(world) == [Gap(ANALYZED_ROW, "Clawshot_Arrival", "")]
    world.analyzed.append({"__RowId": "Clawshot_Arrival"})
    assert added(world) == []


def test_local_call_needs_entry_registration_and_a_real_entry_but_no_sub_flow_declaration():
    world = native_world()
    talker = world.charts["Npc_Talker"]
    talker.events.append(evfl.SubFlowEvent("ClawshotLocal", "", "Near"))
    talker.events[0].next = 1
    assert added(world) == [Gap(ENTRY_CALLS, "Npc_Talker:Talk", "ClawshotLocal")]
    talker.entry_points[0].sub_flow_events.append(1)
    assert added(world) == []
    talker.events[1].entry_point = "Missing"
    assert added(world) == [Gap(CALL_TARGET, "Npc_Talker/ClawshotLocal", "Npc_Talker:Missing")]


def test_row_without_entry_point_name_checks_its_first_entry_point():
    world = native_world()
    talker = world.charts["Npc_Talker"]
    talker.events.append(evfl.SubFlowEvent("ClawshotNear", "GetPouchContent", "GetPouchContentByActorName"))
    talker.entry_points[1].main_event = 1
    talker.entry_points[1].sub_flow_events.append(1)
    assert added(world) == []
    # No row's event runs Near: its new call is one no registry can check, which the real-dump tests refuse.
    assert ("Npc_Talker", "Near") in changed_dependencies(native_world().charts, world.charts)
    assert ("Npc_Talker", "Near") not in checked_entries(world.charts, world.settings)
    talker.events[0].next = 1
    talker.entry_points[0].sub_flow_events.append(1)
    assert added(world) == [Gap(SUB_FLOWS, "Npc_Talker_Talk", "GetPouchContent")]


def test_inherited_debt_is_kept_apart_from_added_gaps():
    native = native_world()
    native.analyzed_row("Dm_TimeTemple_0085")["ChildEventList"].clear()
    native.analyzed = [row for row in native.analyzed if row["__RowId"] != "Dm_SY_Get"]
    debt = native.gaps()
    assert debt == {Gap(CHILDREN, "Dm_TimeTemple_0085", "Dm_TimeTemple_0090"), Gap(ANALYZED_ROW, "Dm_SY_Get", "")}
    patched = copy.deepcopy(native)
    era_helper(patched)
    assert patched.gaps() & debt == debt
    assert sorted(patched.gaps() - debt) == [Gap(SUB_FLOWS, "Dm_TimeTemple_0085", "ClawshotSwordEra")]


# --- the supported dump and production seeds ------------------------------------------------------------------------

RECOMMENDED = ("BossHeart", "Chest", "Gift", "Scrub", "Shop")  # the app's Recommended preset
RECIPES: dict[str, tuple[int, Settings, dict]] = {
    # Generator defaults: chests in their dungeons, closed Door of Time without dungeon rewards, Gossip Stone hints
    # without the Mask of Truth, the closed forest, the intro skip.
    "defaults": (1, Settings(), {}),
    "starting": (
        1,
        Settings(
            starting_items=("Ocarina of Time", "Song of Storms", "Slingshot", "Map (Deku Tree)"),
            starting_hearts=3,
            starting_full_wallet=True,
        ),
        {},
    ),
    # Recommended kinds with the song-only Door of Time, the open forest and vanilla Mask of Truth hints.
    "song_door": (1, Settings(shuffle=RECOMMENDED, door_of_time="song_only", forest="open", hints="mask"), {}),
    # Every shuffle kind and opt-in flow writer: released dungeon items and jail keys, dungeon rewards with the
    # owned-Stones Door, the shuffled Master Sword with free time travel, a reward bridge, every flow-editing fast
    # start, Saria's opt-in farewell handoff, and the runtime module's receive event and "your" get lines.
    # Keep the seed for the rest of the recipe; generate() below deterministically swaps a compatible shield
    # onto a scrub when needed. Writer coverage must not depend on a placement pin surviving logic/fill changes.
    "broad": (
        46,
        Settings(
            shuffle=(*RECOMMENDED, "Freestanding", "Token"),
            dungeon_items="all_anywhere",
            shuffle_hideout_keys=True,
            dungeon_rewards=True,
            shuffle_master_sword=True,
            bridge="rewards",
            bridge_count=6,
            logic={"free_time_travel": True},
            fast_start=("deku_tree", "intro", "kaepora", "saria"),
            skip_saria_farewell=True,
            songs="anywhere",
            shop_prices="affordable",
            scrub_prices="fixed",
            forest="closed_deku",
        ),
        {"receive_event": True, "possessive_text": True},
    ),
}


def _modules(*names: str) -> frozenset[str]:
    return frozenset(f"clawshot.patch.{name}" for name in names)


# The modules whose transforms each recipe runs on an event flow or table (measured on these seeds). A recipe that
# stops running one loses coverage; a module outside every set is a writer no recipe was chosen for.
_EVERY_RECIPE = _modules(
    "bags",
    "dampe_first_race",
    "dampe_safety",
    "darunia",
    "door_story",
    "equipment",
    "gamedata",
    "keys",
    "ocarina",
    "progressive_bonus",
    "saria_farewell",  # event-items Q2/D9: the bridge Saria's own actor, every seed
    "scene_handoff",
    "scrubs",
)
_OPT_IN = _modules(
    "custom_items",
    "door",
    "event_models",  # event-items: events show the given item (setting on by default) once a gift or reward moves
    "gifts",
    "master_sword",
    "mido",
    "owl_skips",
    "receive_event",
    "reward_bridge",
    "rewards",
    "scene_gifts",
    "scrub_shields",
    "talon",
    "text",
)
WRITERS = {
    "defaults": _EVERY_RECIPE | _modules("text"),
    # Gift with Token or a floor kind runs the ocarina pickups' receipt in Dm_SY_Get (ocarina-song-drops-everywhere).
    "song_door": _EVERY_RECIPE | _modules("door", "gifts", "ocarina_pickup"),
    "broad": _EVERY_RECIPE | _OPT_IN | _modules("ocarina_pickup"),
    "starting": _EVERY_RECIPE | _modules("text", "start_items"),
}
FLOW_WRITERS = frozenset().union(*WRITERS.values())


def _event_file(path: str) -> bool:
    return (path.startswith(FLOW_DIR + "/") and path.endswith(FLOW_SUFFIX)) or path in (SETTINGS, ANALYZED)


@functools.cache
def dump_events(romfs: Path) -> tuple[World, dict[str, str]]:
    """The dump's flowcharts (by name, from the file the game loads), event tables and flow name -> romfs path."""
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    versions = {str(k): str(v) for k, v in read_romfs_byml(romfs, dictionaries, FLOW_VERSIONS)["Versions"].items()}
    files = flow_files(romfs, versions)
    charts = {}
    for flow, path in files.items():
        chart = evfl.read(dictionaries.decompress(path, (romfs / path).read_bytes())).flowchart
        if chart is not None:
            charts[flow] = chart
    tables = [read_romfs_byml(romfs, dictionaries, table) for table in (SETTINGS, ANALYZED)]
    return World(charts, *tables), files


def generate(romfs: Path, seed: int, settings: Settings, options: Mapping, *, scrub_shield: bool = False) -> SeedOutput:
    """Production seed setup, optionally fixing one allowed placement pair to exercise the scrub-shield writer."""
    spec, steps = None, []
    if gifts.SHUFFLE in settings.shuffle or set(settings.shuffle).intersection(gifts.GIFT_TYPES):
        spec, settings, step = gifts.seed_setup(romfs, load_spec(), settings)
        steps.append(step)
    output = make_seed(romfs, seed, settings, spec, extra_steps=steps, **options)
    if not scrub_shield:
        return output
    placements = {name: output.seed.placements[name] for name in output.seed.shuffled}
    shields = ("Deku Shield", "Hylian Shield", "Mirror Shield")
    targets = [name for name in scrubs.SALES if name in placements]
    if any(placements[name] in shields for name in targets):
        return output
    effective = output.seed.settings
    # The replay uses the same container/tier screens as the fill; pair selection must honor them too.
    world = with_screens(
        output.seed.world,
        output.seed.shuffled,
        list(placements.values()),
        {name: item for name, item in output.seed.placements.items() if name not in placements},
    )
    for target in targets:
        for source, item in placements.items():
            if (
                item in shields
                and allowed(world, effective, target, item)
                and allowed(world, effective, source, placements[target])
            ):
                displaced = placements[target]
                placements[source], placements[target] = displaced, item
                print(f"scrub-shield coverage swap: {source} <-> {target} ({item})")

                # External placements omit hint selection; keep this generated recipe's existing hints so
                # the same compile still covers the GossipStone flow writer, not only the scrub shield.
                def placed(*args, **kwargs):
                    return replace(from_placements(*args, **kwargs), hints=output.seed.hints)

                # ``allowed`` on the seed's world does not carry the placement screens ``from_placements`` checks
                # (Skulltula ammo containers): a swap the screens refuse is undone and the next pair tried.
                try:
                    with mock.patch("clawshot.patch.from_placements", placed):
                        return make_seed(
                            romfs, seed, settings, spec, extra_steps=steps, placements=placements, **options
                        )
                except FillError as error:
                    print(f"  refused: {str(error).splitlines()[-1].strip()}")
                    placements[source], placements[target] = item, displaced
    pytest.fail(
        f"no compatible scrub-shield coverage swap: scrubs={[(name, placements[name]) for name in targets]}, "
        f"shields={[(name, item) for name, item in placements.items() if item in shields]}"
    )


def written_world(romfs: Path, output: SeedOutput) -> tuple[World, list[str]]:
    """The dump's event flows and tables with the seed's changes, composed as ``clawshot.patch.write`` composes them
    (every extra change in order; new and fast-start files whole), and the names of the flows the seed writes."""
    native, files = dump_events(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    changed = sorted({path for changes in output.extra_changes for path in changes if _event_file(path)})
    assert not set(changed) & set(output.plan.files()), "chest placement changes touch an event file"
    data = {}
    for path in changed:
        content = dictionaries.decompress(path, (romfs / path).read_bytes())
        for changes in output.extra_changes:
            if transform := changes.get(path):
                content = transform(content)
        data[path] = content
    data |= {path: file.data for path, file in output.new_files.items() if _event_file(path)}
    data |= {
        file.path: dictionaries.decompress(file.path, file.content)
        for file in output.fast_start_files
        if _event_file(file.path)
    }
    charts, written = dict(native.charts), []
    for path, content in sorted(data.items()):
        if path in (SETTINGS, ANALYZED):
            continue
        flow = PurePosixPath(path).name.removesuffix(FLOW_SUFFIX).partition(".")[0]
        if files.get(flow, path) != path:
            continue  # a copy the game does not load (patch.rewards edits the dormant base flow with the .110 one)
        document = evfl.read(content)
        chart = document.flowchart
        if chart is None:
            # A timeline-only file (event-items: Saria presenting her gift, Zelda's throw): no flowchart events.
            assert document.timeline is not None, path
            continue
        assert chart.name == flow, path
        charts[flow] = chart
        written.append(flow)
    settings, analyzed = (
        byml.read(data[table]) if table in data else default
        for table, default in ((SETTINGS, native.settings), (ANALYZED, native.analyzed))
    )
    return World(charts, settings, analyzed), written


def writers(output: SeedOutput) -> set[str]:
    """The modules whose transforms change an event flow or table in this seed (a partial counts as its function)."""
    found = set()
    for changes in output.extra_changes:
        for path, transform in changes.items():
            if _event_file(path):
                while isinstance(transform, functools.partial):
                    transform = transform.func
                found.add(transform.__module__)
    return found


@pytest.mark.dump
def test_dump_follows_the_model_but_for_its_named_debt(romfs):
    native, _ = dump_events(romfs)
    assert native.gaps() == NATIVE_DEBT


@pytest.mark.dump
@pytest.mark.parametrize("recipe", sorted(RECIPES))
def test_production_seed_declares_every_event_dependency_it_adds(romfs, recipe):
    seed, settings, options = RECIPES[recipe]
    output = generate(romfs, seed, settings, options, scrub_shield=recipe == "broad")
    native, _ = dump_events(romfs)
    patched, written = written_world(romfs, output)
    debt = native.gaps()
    gaps = patched.gaps()
    print(f"{recipe}: {len(written)} flows written: {written}; inherited debt: {sorted(map(str, gaps & debt))}")
    print(f"played Market bottle allowance: {sorted(map(str, gaps & PLAYED_MARKET_BOTTLE_ALLOWANCE))}")
    added = sorted(gaps - debt - PLAYED_MARKET_BOTTLE_ALLOWANCE)
    assert added == [], "new suspected registration risks (not a proven freeze cause):\n" + "\n".join(map(str, added))
    unchecked = changed_dependencies(native.charts, patched.charts) - checked_entries(patched.charts, patched.settings)
    assert unchecked == set(), f"dependencies added where no EventSetting row's event runs: {sorted(unchecked)}"
    found = writers(output)
    assert WRITERS[recipe] <= found, f"{recipe} no longer runs {sorted(WRITERS[recipe] - found)}"
    assert found <= FLOW_WRITERS, f"event writers no recipe covers: {sorted(found - FLOW_WRITERS)}"
    assert_first_race_cycle(patched.charts["MiniGame_DampeRace"])
