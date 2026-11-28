"""Event displays: the steps of a gift flow that name the vanilla item without giving it (spec event-items 1.1).

Some events give the item in one step and open the get window in another, display-only step
(``GetPouchContent:DisplayGetByActorName`` with a literal ``ActorName``); their Zelda's Notes screenshot
(``EventTriggerZeldaNotesRequestSendDailyScreenShot``) names the item in ``TargetID``. A gift patch that rewrites only
the grant leaves both naming the vanilla item. :func:`find_displays` lists them in every flow that has a gift step,
keyed by ``<flow>/<event>`` (AGENTS.md rule 5). Arguments (a wrapper's ``Argument('ActorName')``) are left out: the
wrapper's caller names the item.
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from clawshot.census import gifts
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import evfl, zsdic

DISPLAY_FLOW = "GetPouchContent"
DISPLAY_ENTRY = "DisplayGetByActorName"
DISPLAY_PARAM = "ActorName"
NOTES_ACTION = "EventTriggerZeldaNotesRequestSendDailyScreenShot"
NOTES_PARAM = "TargetID"

WINDOW = "window"
NOTES = "notes"


@dataclass(frozen=True)
class Display:
    id: str  # "<flow>/<event>"
    kind: str  # WINDOW or NOTES
    flow: str
    event: str
    param: str  # the parameter naming the item
    native: str  # the actor name it names in the dump


def gift_flows(found: Iterable[gifts.Gift]) -> set[str]:
    return {gift.flow for gift in found}


def _named(event, param: str) -> str | None:
    value = (event.params or {}).get(param)
    return value if isinstance(value, str) and not isinstance(value, evfl.Argument) else None


def find_displays(flowcharts: Mapping[str, evfl.Flowchart], flows: Iterable[str]) -> list[Display]:
    """The literal display-only windows and Notes targets in ``flows`` (names in ``flowcharts``), sorted by flow,
    then event index."""
    out = []
    for flow in sorted(set(flows)):
        fc = flowcharts[flow]
        for event in fc.events:
            if (
                isinstance(event, evfl.SubFlowEvent)
                and (event.flowchart or flow) == DISPLAY_FLOW
                and event.entry_point == DISPLAY_ENTRY
            ):
                kind, param = WINDOW, DISPLAY_PARAM
            elif isinstance(event, evfl.ActionEvent) and fc.actors[event.actor].actions[event.action] == NOTES_ACTION:
                kind, param = NOTES, NOTES_PARAM
            else:
                continue
            native = _named(event, param)
            if native is not None:
                out.append(Display(f"{flow}/{event.name}", kind, flow, event.name, param, native))
    return out


def scan_displays(romfs: str | Path) -> list[Display]:
    """Every display in a gift flow of the dump at ``romfs`` (read only)."""
    files, flowcharts = gifts.load_flowcharts(Path(romfs))
    return find_displays(flowcharts, gift_flows(gifts.find_gifts(flowcharts, files)))


# --- event props (spec event-items 2.1) ---------------------------------------------------------------------------
#
# An event shows an item through an actor of its flowchart or timeline that it binds to a bone or locator, animates
# or brings on stage. The census lists every such item actor of the dump; ``patch/event_props.toml`` sorts each into
# a prop of a check or a named exclusion. A prop is identified by ``<event>/<part>/<actor>[@<secondary name>]``.

FLOWCHART = "flowchart"
TIMELINE = "timeline"
PROP_ACTOR = re.compile(r"^(Dm_Item_|Item_|Weapon_Sword_)")
MODEL_ACTIONS = frozenset(
    {
        "EventTriggerModelBind",
        "EventModelBind",
        "EventPlayAS",
        "EventPlayASForTimeline",
        "EventPlayASAndModelBindForTimeline",
        "EventTriggerParticipateEvent",
        "EventTriggerSetModelLodManual",
    }
)


def prop_id(event: str, part: str, actor: str, secondary: str = "") -> str:
    return f"{event}/{part}/{actor}" + (f"@{secondary}" if secondary else "")


def find_prop_actors(event: str, document: evfl.EventFlowFile) -> list[str]:
    """The ids of the item actors ``document`` (the flow file ``event``) shows, in actor order."""
    out = []
    for part, chart in ((FLOWCHART, document.flowchart), (TIMELINE, document.timeline)):
        if chart is None:
            continue
        steps = chart.events if isinstance(chart, evfl.Flowchart) else chart.clips
        used: dict[int, set[str]] = {}
        for step in steps:
            if isinstance(step, evfl.ActionEvent | evfl.Clip):
                used.setdefault(step.actor, set()).add(chart.actors[step.actor].actions[step.action])
        for index, actor in enumerate(chart.actors):
            if PROP_ACTOR.match(actor.name) and used.get(index, set()) & MODEL_ACTIONS:
                out.append(prop_id(event, part, actor.name, actor.secondary_name))
    return out


def scan_prop_actors(romfs: str | Path) -> list[str]:
    """Every item actor an event of the dump at ``romfs`` shows (read only), sorted by event."""
    romfs = Path(romfs)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    versions = {str(k): str(v) for k, v in read_romfs_byml(romfs, dicts, gifts.FLOW_VERSIONS)["Versions"].items()}
    out = []
    for event, path in sorted(gifts.flow_files(romfs, versions).items()):
        out += find_prop_actors(event, evfl.read(dicts.decompress(path, (romfs / path).read_bytes())))
    return out
