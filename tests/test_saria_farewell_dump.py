"""Saria's farewell fix against the dump (spec event-items 4.4; plan 13.1): exactly the bridge Saria changes."""

import pytest

from clawshot.census.hints import flow_path
from clawshot.formats import byml, evfl, sarc, zsdic
from clawshot.patch import saria_farewell as fix
from clawshot.patch.actor_packs import actor_member, closure

pytestmark = pytest.mark.dump


@pytest.fixture(scope="module")
def built(romfs):
    return fix.changes(romfs)


def _read(romfs, dicts, path):
    return dicts.decompress(path, (romfs / path).read_bytes())


def test_dump_the_three_flows_rename_three_actor_entries_and_five_names(romfs, built):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    counts = {}
    for flow in fix.FLOWS:
        document = evfl.read(_read(romfs, dicts, flow_path(romfs, flow)))
        counts[flow] = fix.rename(document)
        transforms, _ = built
        assert evfl.read(transforms[flow_path(romfs, flow)](_read(romfs, dicts, flow_path(romfs, flow)))) == document
    assert counts == {"Dm_Kokiri_0150": 2, "Dm_Kokiri_0155": 4, "Goto_HyruleCastle": 2}


def test_dump_only_the_bridge_placement_changes(romfs, built):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    data = _read(romfs, dicts, fix.PLACEMENT_FILE)
    before, after = byml.read(data)["Actors"], byml.read(built[0][fix.PLACEMENT_FILE](data))["Actors"]
    changed = [(a["Hash"], b["Gyaml"]) for a, b in zip(before, after, strict=True) if a != b]
    assert changed == [(fix.PLACEMENT_HASH, fix.FAREWELL)]


def test_dump_her_list_differs_from_sarias_only_in_the_warpdone_hold(romfs, built):
    native = byml.read((romfs / fix.schedule_path(fix.SARIA)).read_bytes())
    mine = byml.read(built[1][fix.schedule_path(fix.FAREWELL)].data)
    for setting in (
        a["Setting"]
        for e in native["ConditionalSchedule"]
        if e.get("ConditionFlag") == fix.WARP_DONE
        for a in e["ActionSchedule"]
    ):
        for field in fix.HOLD_FIELDS:
            setting.pop(field)
    assert mine == native


def test_dump_her_pack_is_a_native_style_pack_whose_schedule_is_her_own(romfs, built):
    members = sarc.read(built[1][fix.pack_path(fix.FAREWELL)].data)
    packed = closure([members], fix.FAREWELL)
    assert packed.components["AIScheduleRef"] == "?" + fix.schedule_path(fix.FAREWELL)
    assert set(members) <= set(packed.members) | {m for m in members if m.startswith("AI/")}
    assert actor_member(fix.SARIA) not in members
