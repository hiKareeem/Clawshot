"""Every split gift display is declared; native grant/window pairs change together."""

import pytest

from clawshot.census import definitions, event_items
from clawshot.census.gifts import FLOW_VERSIONS, flow_files, scan_gifts
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import evfl, zsdic
from clawshot.patch import gifts

pytestmark = pytest.mark.dump


def _display_param(fc, event):
    """The parameter a declared display sets: a get window's ActorName or a Zelda's Notes step's target."""
    if isinstance(event, evfl.ActionEvent) and fc.actors[event.actor].actions[event.action] == event_items.NOTES_ACTION:
        return event_items.NOTES_PARAM
    return event_items.DISPLAY_PARAM


@pytest.fixture(scope="module")
def context(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    versions = read_romfs_byml(romfs, dictionaries, FLOW_VERSIONS)["Versions"]
    files = flow_files(romfs, {str(k): str(v) for k, v in versions.items()})
    census = scan_gifts(romfs)
    charts = {}
    for flow in sorted({gift.flow for gift in census}):
        path = files[flow]
        charts[flow] = dictionaries.decompress(path, (romfs / path).read_bytes())
    return census, files, charts


def test_every_literal_display_in_a_gift_flow_is_declared(context):
    _, _, charts = context
    found = set()
    for flow, data in charts.items():
        for event in evfl.read(data).flowchart.events:
            if (
                isinstance(event, evfl.SubFlowEvent)
                and (event.flowchart, event.entry_point) == ("GetPouchContent", "DisplayGetByActorName")
                and isinstance((event.params or {}).get("ActorName"), str)
                and not isinstance(event.params["ActorName"], evfl.Argument)
            ):
                found.add(f"{flow}/{event.name}")
    declared = [ref for rule in gifts.load().values() for ref in rule.display]
    # The other declared displays are Zelda's Notes targets (event-items), which name the grant's item too.
    notes = {ref for ref in declared if ref not in found}
    for ref in sorted(notes):
        flow, name = ref.split("/")
        fc = evfl.read(charts[flow]).flowchart
        assert _display_param(fc, next(e for e in fc.events if e.name == name)) == event_items.NOTES_PARAM, ref
    assert found == set(declared) - notes
    assert len(declared) == len(set(declared)), "a display cannot belong to two grants"


@pytest.mark.parametrize(
    "check,item",
    [("HF Ocarina of Time Item", "Obj_Heart_Piece"), ("LW Gift from Saria", "Item_Bottle")],
)
def test_native_display_and_grant_change_together_and_vanilla_is_identical(context, check, item):
    census, files, charts = context
    rules = gifts.load()
    [change] = gifts.plan({check: item}, census, definitions.load(), rules)
    for flow in gifts.flows_changed([change]):
        data = charts[flow]
        fc = evfl.read(gifts.file_changes([change], files)[files[flow]](data)).flowchart
        for step in change.steps:
            if step.flow == flow:
                assert next(e for e in fc.events if e.name == step.event).params[step.param] == item
        for ref in change.rule.display:
            if ref.split("/")[0] == flow:
                event = next(e for e in fc.events if e.name == ref.split("/")[1])
                assert event.params[_display_param(fc, event)] == item
        vanilla = change.steps[0].vanilla_item
        [unchanged] = gifts.plan({check: vanilla}, census, definitions.load(), rules)
        assert gifts.file_changes([unchanged], files)[files[flow]](data) == data
