"""Native field-diff and allocation oracles; gameplay still needs Kareem."""

import copy

import pytest

from clawshot.census.hints import read_flow
from clawshot.formats import byml, evfl, rstb, sarc, zsdic
from clawshot.patch import getitem
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.patch.plan import Plan
from clawshot.patch.shops import actor_path, member_path, resolve_member
from clawshot.patch.write import write
from clawshot.save import murmur3_32


@pytest.mark.dump
def test_native_song_models_keep_every_grant_identity_and_size_all_changed_members(romfs, tmp_path):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def raw(path, root=romfs):
        return dictionaries.decompress(path, (root / path).read_bytes())

    actors = tuple(getitem.SONG_MODELS)
    transforms = getitem.changes(romfs, actors)
    out = tmp_path / "native-models"
    written = write(Plan([], [], []), romfs, out, extra_changes=(transforms,))
    original_table = rstb.read(raw(rstb.TABLE_PATH))
    table = rstb.read(raw(rstb.TABLE_PATH, out / "romfs"))
    expected_table = copy.deepcopy(original_table)
    for actor in actors:
        path = getitem.pack_path(actor)
        original = sarc.read(raw(path))
        changed = sarc.read(raw(path, out / "romfs"))
        components = resolve_member(original, actor_path(actor))["Components"]
        member = member_path(components["ModelInfoRef"])
        before, after = byml.read(original[member]), byml.read(changed[member])
        native = getitem.SONG_MODELS[actor]
        assert (after["FmdbName"], after["ModelProjectName"]) == (native, native)
        assert (romfs / f"Model/{native}.{native}.bfres.zs").is_file()
        for field in ("FmdbName", "ModelProjectName"):
            after[field] = before[field]
        assert byml.same(before, after)
        delta = max(0, ((len(changed[member]) + 31) // 32 - (len(original[member]) + 31) // 32) * 32)
        expected_table.set(member, original_table.get(member) + delta)
        changed[member] = original[member]
        assert changed == original
    before = byml.read(raw(getitem.ACTOR_INFO))
    after = byml.read(raw(getitem.ACTOR_INFO, out / "romfs"))
    old_rows = {row["__RowId"]: row for row in before}
    for row in after:
        actor = row["__RowId"]
        if actor not in actors:
            continue
        old = old_rows[actor]
        donor = old_rows[getitem.SONG_MODELS[actor]]
        for field in getitem.MODEL_FIELDS:
            assert byml.same(row[field], donor[field])
            row[field] = old[field]
        field = "PreActorRenderInfoHeapSize"
        assert row[field] >= max(old[field], donor[field])
        row[field] = old[field]
        field = "InstanceHeapSize"
        assert row[field] >= int(old[field]) + int(donor[field])
        row[field] = old[field]
    assert byml.same(before, after)
    for info in written:
        if info.path == rstb.TABLE_PATH:
            continue
        expected_table.set(info.path, max(original_table.get(info.path), rstb.required_size(info.path, info.new_size)))
    assert table == expected_table


@pytest.mark.dump
def test_ocarina_chest_props_preserve_native_equipment_and_all_grants(romfs, tmp_path):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def raw(path, root=romfs):
        return dictionaries.decompress(path, (root / path).read_bytes())

    gamedata = byml.read(raw(GAME_DATA_LIST))["Data"]
    key = murmur3_32(getitem.MESSAGE_TARGET.encode())
    assert any(int(row["Hash"]) == key for row in gamedata["String64"]), (getitem.MESSAGE_TARGET, key)
    transforms = getitem.changes(romfs, getitem.OCARINAS)
    # No modified instrument, prop, inventory table or grant helper is shipped.
    assert all(path.startswith("Event/EventFlow/Dm_SY_Treasurebox") for path in transforms)
    out = tmp_path / "ocarina-props"
    written = write(Plan([], [], []), romfs, out, extra_changes=(transforms,))
    table = rstb.read(raw(rstb.TABLE_PATH, out / "romfs"))
    for path in transforms:
        before = evfl.read(raw(path)).flowchart
        after = evfl.read(raw(path, out / "romfs")).flowchart
        old_events = copy.deepcopy(after.events[: len(before.events)])
        for old, changed in zip(before.events, old_events, strict=True):
            if old != changed:
                assert isinstance(old, (evfl.ActionEvent, evfl.SubFlowEvent))
                assert changed.next >= len(before.events)
                changed.next = old.next
            assert changed == old
        for old, changed in zip(before.actors, after.actors, strict=False):
            if old.name == "GameDataActor":
                changed.actions = old.actions
                changed.queries = old.queries
            assert old == changed
        assert after.entry_points == before.entry_points
        for prop in after.actors[len(before.actors) :]:
            assert prop.params == next(
                a.params for a in read_flow(romfs, "Dm_MelodyGet_Time").actors if a.name == "Dm_" + getitem.TIME
            )
            pack = sarc.read(raw(getitem.pack_path(prop.name)))
            components = resolve_member(pack, actor_path(prop.name))["Components"]
            assert "AccessoryRef" not in components
            assert "PhysicsRef" in components
            model = resolve_member(pack, components["ModelInfoRef"])
            assert model["FmdbName"] == prop.name.removeprefix("Dm_")
            assert (romfs / f"Model/{model['ModelProjectName']}.{model['FmdbName']}.bfres.zs").is_file()
        for row in written:
            if row.path == path:
                assert table.get(path) >= rstb.required_size(path, row.new_size)
                print(path, row.size, "->", row.new_size, "allocation", table.get(path))
