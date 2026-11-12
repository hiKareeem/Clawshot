"""An event the runtime module can request to give an item as the game gives one: ``Clawshot_Receive``.

A multiworld item written straight into the save (a rupee or ammo counter) arrives silently, and the game's AddPouch
refuses the bundled contents chests give (``TBox_Rupee_Blue``: five green rupees). This module adds an event the
Archipelago bridge requests, as sloperina requests ``Dm_SY_BancChangeGo`` for its warps (FINDINGS 5.18), with the
content in ``ActorName`` and whether to show the pick-up notice in ``ShowNotice``. It is made of the game's own nodes
(:func:`build_flow`): the pick-up notice (``Dm_SY_TreasureboxSmall`` Event38, ``Dm_SY_Get_WithoutPlayer`` Event11),
the heal and magic refill of ``Dm_SY_Get`` (Event4, Event103), and the chest's rupee counter and native add
(``GetPouchContent``'s ``OpenRupeeUIIfNeed`` and ``CloseRupeeUIIfNeed`` nodes, copied in, and its Event0), which
unpacks bundles. Added:

- the flow ``Event/EventFlow/Clawshot_Receive.bfevfl.zs`` (a new file; only 13 flows are versioned in
  ``EventFlowFileEntry``, so an unlisted one is read at its plain path), its actors' definitions copied from
  ``Dm_SY_Get_WithoutPlayer``;
- a row in ``RSDB/EventSetting`` (``Dm_SY_Get_WithoutPlayer``'s, based on Link's position as ``Dm_SY_Get``, since
  the event has no starter actor), run as a sub-event: the component list and sound setting of
  ``Dm_Kokiri_0050_After_Near`` (``SubEvent``: a sub-event's priority, world time running, no member paused), so
  Link keeps moving while it runs (the donor's own list derives from ``FlowchartEvent``, whose
  ``NonEventMemberSetting`` is ``AllPause``: everything stopped, as the user saw); and a row in
  ``RSDB/GameAnalyzedEventInfo`` (the donor's, its sub-flow ``GetPouchContent``), each table in name order as the
  game keeps it;
- the saved Bool :data:`FLAG`, whose presence tells the bridge the event is there (an older mod has none), and with
  the slot's pick-up notices on, :data:`NOTICE_FLAG` (its presence turns the notice on).

Seen in game (nxnative, 2026-11-12): the requested event runs and gives rupees with the counter (its first build,
which called those two entry points as sub-flows, crashed there), stopping play as the donor's setting does. **Not
yet seen:** the sub-event setting, the notice.
"""

import bisect
import copy
from collections.abc import Callable
from pathlib import Path

from clawshot.census.hints import flow_path
from clawshot.formats import byml, evfl, zsdic
from clawshot.patch.plan import PatchError
from clawshot.patch.write import NewFile

EVENT = "Clawshot_Receive"
FLAG = "Archipelago.ReceiveEvent"
NOTICE_FLAG = "Archipelago.PickupNotice"
FLOW_PATH = f"Event/EventFlow/{EVENT}.bfevfl.zs"
DONOR = "Dm_SY_Get_WithoutPlayer"
PLAYER_BASE = "Dm_SY_Get"  # whose EventBaseSetting (Link's position) the event takes
SUB_EVENT = "Dm_Kokiri_0050_After_Near"  # whose component list (SubEvent) and sound setting it takes
SUB_EVENT_LIST = (
    "Work/Event/EventSetting/EventSettingComponentList/SubEvent.engine__event__EventSettingComponentList.gyml"
)
EVENT_SETTING = "RSDB/EventSetting.Product.111.rstbl.byml.zs"
ANALYZED = "RSDB/GameAnalyzedEventInfo.Product.111.rstbl.byml.zs"


def build_flow(donor: evfl.Flowchart) -> bytes:
    """The event's flow, for ``ActorName`` (the content) and ``ShowNotice`` (a Bool):

    0. ``ShowNotice`` set: the pick-up notice (``UISystemActor.EventTriggerRequestOpenPickUpWindow``);
    1. a heart or magic refill (``PouchSystemActor.EventQueryIsRecoverHeartOrMpActor`` case 0, as ``Dm_SY_Get``
       Event4 asks): ``EventTriggerRecoverByCureItem`` (``Dm_SY_Get`` Event103), the game's own heal and refill;
    2. anything else: the native add of one ``ActorName``; for a rupee content (category 7) inside the rupee
       counter, opened and closed as ``GetPouchContent``'s ``OpenRupeeUIIfNeed``/``CloseRupeeUIIfNeed`` do it.
    """
    by_name = {actor.name: actor for actor in donor.actors if not actor.secondary_name}
    for needed in ("UISystemActor", "PouchSystemActor"):
        if needed not in by_name:
            raise PatchError(f"{donor.name}: no {needed}")

    def system_actor(name: str, actions: list[str], queries: list[str]) -> evfl.Actor:
        # the donor's own definition where it has the actor, else its UISystemActor's (every system actor here has
        # the same default member settings)
        actor = copy.deepcopy(by_name.get(name, by_name["UISystemActor"]))
        actor.name, actor.actions, actor.queries, actor.entry_point = name, actions, queries, evfl.NONE
        return actor

    # No sub-flow calls: GetPouchContent's OpenRupeeUIIfNeed run from this flow crashed the game (nxnative,
    # 2026-11-12: a call through a null pointer, "OpenRupeeUIIfNeed" in the registers; only GetPouchContent itself
    # calls it in the game). Its nodes are copied in instead: Event78/79 (the content's category, 7 for rupees),
    # Event80 (open the counter), Event99/100/61 (a wait), Event81 (close it).
    ui = system_actor(
        "UISystemActor",
        ["EventTriggerRequestOpenPickUpWindow", "EventOpenRupeeDisplay", "EventCloseRupeeDisplay"],
        ["EventQueryIsRupeeMax"],
    )
    pouch = system_actor(
        "PouchSystemActor",
        ["EventTriggerAddOrRemovePouchContent", "EventTriggerRecoverByCureItem"],
        ["EventQueryIsRecoverHeartOrMpActor", "EventQueryCheckPouchContentCategory"],
    )
    game_data = system_actor("GameDataActor", [], ["EventQueryIsBool"])
    game_system = system_actor("GameSystemActor", ["EventWait"], [])
    UI, POUCH, DATA, SYSTEM = 0, 1, 2, 3
    content = evfl.Argument("ActorName")
    add = {
        "Num": 1,
        "IsEquipDIrect": False,
        "IsSetMessageTargetActorName": False,
        "Actor": content,
        "IsGetEvent": False,
    }
    rupees = 7  # EventQueryCheckPouchContentCategory: GetPouchContent's Event78 case for the rupee counter
    categories = range(12)  # every case the game's flows switch on (0-11)
    events = [
        evfl.SwitchEvent("Event0", DATA, 0, [(0, 1), (1, 2)], {"BoolValue": evfl.Argument("ShowNotice")}),
        evfl.ActionEvent("Event1", UI, 0, 2, {"ActorName": content}),
        evfl.SwitchEvent("Event2", POUCH, 0, [(0, 3), (1, 4)], {"ActorName": content}),
        evfl.ActionEvent("Event3", POUCH, 1, evfl.NONE, {"ActorName": content}),
        evfl.SwitchEvent(
            "Event4", POUCH, 1, [(c, 5 if c == rupees else 11) for c in categories], {"ActorName": content}
        ),
        evfl.ActionEvent(
            "Event5",
            UI,
            1,
            6,
            {"IsWaitEnd": True, "IsNeedMaxNum": False, "IsWaitOpenAnim": True, "IsWaitChoiceBtnIn": False},
        ),
        evfl.ActionEvent("Event6", POUCH, 0, 7, dict(add)),
        evfl.SwitchEvent("Event7", UI, 0, [(0, 8), (1, 9)], None),
        evfl.ActionEvent("Event8", SYSTEM, 0, 10, {"IsWaitEnd": True, "Frames": 60}),
        evfl.ActionEvent("Event9", SYSTEM, 0, 10, {"Frames": 1, "IsWaitEnd": True}),
        evfl.ActionEvent("Event10", UI, 2, evfl.NONE, {"IsWaitEnd": True}),
        evfl.ActionEvent("Event11", POUCH, 0, evfl.NONE, dict(add)),
    ]
    flowchart = evfl.Flowchart(EVENT, actors=[ui, pouch, game_data, game_system], events=events,
                               entry_points=[evfl.EntryPoint(EVENT, 0)])  # fmt: skip
    document = evfl.EventFlowFile(EVENT, flowchart=flowchart)
    data = evfl.write(document)
    if evfl.read(data) != document:
        raise PatchError(f"{EVENT}: the written flow does not read back")
    return data


def _insert(rows: list, row: dict, table: str) -> None:
    ids = [str(r["__RowId"]) for r in rows]
    if ids != sorted(ids):
        raise PatchError(f"{table}: rows are no longer in name order")
    at = bisect.bisect_left(ids, row["__RowId"])
    if at < len(ids) and ids[at] == row["__RowId"]:
        raise PatchError(f"{table}: already has a row {row['__RowId']}")
    rows.insert(at, row)


def _row(rows: list, name: str, table: str) -> dict:
    row = next((r for r in rows if r.get("__RowId") == name), None)
    if row is None:
        raise PatchError(f"{table}: no {name} row")
    return row


def add_event_setting(data: bytes) -> bytes:
    document = byml.load(data)
    rows = document.root
    row = copy.deepcopy(_row(rows, DONOR, EVENT_SETTING))
    row.update(
        {
            "__RowId": EVENT,
            "EntryPointName": EVENT,
            "FlowchartFileName": f"Work/Event/EventFlow/{EVENT}.evfc",
            "EventBaseSetting": _row(rows, PLAYER_BASE, EVENT_SETTING)["EventBaseSetting"],
        }
    )
    sub_event = _row(rows, SUB_EVENT, EVENT_SETTING)
    if sub_event.get("EventSettingComponentList") != SUB_EVENT_LIST:
        raise PatchError(f"{EVENT_SETTING}: {SUB_EVENT} is no longer a SubEvent")
    for key in ("EventSettingComponentList", "EventSoundSetting"):
        row[key] = sub_event[key]
    _insert(rows, row, EVENT_SETTING)
    return _dump(document, EVENT_SETTING)


def add_analyzed(data: bytes) -> bytes:
    document = byml.load(data)
    rows = document.root
    row = copy.deepcopy(_row(rows, DONOR, ANALYZED))
    row["__RowId"] = EVENT
    row["SubFlowList"] = ["GetPouchContent"]
    _insert(rows, row, ANALYZED)
    return _dump(document, ANALYZED)


def _dump(document: byml.Document, table: str) -> bytes:
    out = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(out))) is not None:
        raise PatchError(f"{table}: failed read-back: {difference}")
    return out


def changes(romfs: str | Path) -> tuple[dict[str, Callable[[bytes], bytes]], dict[str, NewFile]]:
    """The table changes and the new flow file."""
    romfs = Path(romfs)
    if (romfs / FLOW_PATH).exists():
        raise PatchError(f"{FLOW_PATH} is in the dump already")
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    donor_path = flow_path(romfs, DONOR)
    donor = evfl.read(dicts.decompress(donor_path, (romfs / donor_path).read_bytes())).flowchart
    if donor is None:
        raise PatchError(f"{DONOR}: no flowchart")
    return {EVENT_SETTING: add_event_setting, ANALYZED: add_analyzed}, {FLOW_PATH: NewFile(build_flow(donor))}
