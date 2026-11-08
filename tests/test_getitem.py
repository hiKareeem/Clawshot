"""Presentation changes must not alter the item being granted or its pouch behavior."""

import copy
from functools import partial

import pytest

from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.patch import getitem
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.shops import actor_path, member_path
from clawshot.patch.write import write


def native_performer():
    return byml.write({"EventUniqueAin": "Work/AI/Root/Event/PouchContent.event.root.ain", "UseEventUniqueAin": True})


def actor_pack(actor):
    model = f"Component/ModelInfo/{actor}.engine__component__ModelInfo.bgyml"
    root = {"Components": {"ModelInfoRef": "?" + model, "EventPerformerRef": getitem.COMMON}}
    if actor in getitem.SONG_MODELS:
        root["Components"]["EventPerformerRef"] = "?" + getitem.PERFORMER
    name = "Obj_Rupee" if actor in getitem.SONG_MODELS else actor
    pack = {
        member_path(actor_path(actor)): byml.write(root),
        model: byml.write({"FmdbName": name, "ModelProjectName": name}),
        "PouchContent": byml.write({"PouchActor": actor, "SpecialDeal": "unchanged"}),
    }
    if actor in getitem.SONG_MODELS:
        pack[getitem.PERFORMER] = native_performer()
    return sarc.write(pack), model


@pytest.mark.parametrize("actor", [getitem.FAIRY, getitem.TIME, *getitem.SONG_MODELS])
def test_model_correction_preserves_every_nonpresentation_member(actor):
    before, model = actor_pack(actor)
    original = sarc.read(before)
    after = sarc.read(getitem.patch_pack(before, actor=actor, performer=native_performer()))
    if actor in getitem.SONG_MODELS:
        assert byml.read(after[model]) == {
            "FmdbName": getitem.SONG_MODELS[actor],
            "ModelProjectName": getitem.SONG_MODELS[actor],
        }
        after[model] = original[model]
    else:
        root = member_path(actor_path(actor))
        old_root, new_root = byml.read(original[root]), byml.read(after[root])
        assert new_root["Components"]["EventPerformerRef"] == "?" + getitem.PERFORMER
        new_root["Components"]["EventPerformerRef"] = old_root["Components"]["EventPerformerRef"]
        assert byml.same(old_root, new_root)
        assert after.pop(getitem.PERFORMER) == native_performer()
        after[root] = original[root]
    assert after == original


def test_actor_info_keeps_grant_identity_and_unrelated_rows_and_uses_unmodified_donors():
    def row(name, heap, model):
        return {
            "__RowId": name,
            "ActorName": name,
            "FmdbName": model,
            "ModelProjectName": model,
            "ModelAabbMin": {"X": byml.F32(-heap)},
            "ModelAabbMax": {"X": byml.F32(heap)},
            "InstanceHeapSize": byml.U32(heap),
            "PreActorRenderInfoHeapSize": byml.U32(heap),
            "Unrelated": "keep",
        }

    song = "Item_Melody_StormSong"
    rows = [
        row(getitem.FAIRY, 100, getitem.FAIRY),
        row(getitem.TIME, 200, getitem.TIME),
        row("Item_Boomerang", 300, "Item_Boomerang"),
        row(song, 50, "Obj_Rupee"),
        row("Other", 9, "Other"),
    ]
    data = byml.write(rows, byte_order="big")
    result = getitem.patch_actor_info(data, actors=(getitem.FAIRY, song))
    assert byml.byte_order(result) == "big"
    after = byml.read(result)
    assert after[0]["InstanceHeapSize"] == 400
    assert after[3]["InstanceHeapSize"] == 150  # Never use the already-grown Fairy row.
    assert after[3]["PreActorRenderInfoHeapSize"] == 100
    for field in getitem.MODEL_FIELDS:
        assert byml.same(after[3][field], rows[0][field])
        after[3][field] = rows[3][field]
    after[0]["InstanceHeapSize"] = rows[0]["InstanceHeapSize"]
    after[3]["InstanceHeapSize"] = rows[3]["InstanceHeapSize"]
    after[3]["PreActorRenderInfoHeapSize"] = rows[3]["PreActorRenderInfoHeapSize"]
    assert byml.same(after, rows)


def test_stale_model_or_performer_is_refused_and_does_not_mutate_input():
    data, model = actor_pack(getitem.FAIRY)
    pack = sarc.read(data)
    pack[model] = byml.write({"FmdbName": "Changed", "ModelProjectName": "Changed"})
    with pytest.raises(PatchError):
        getitem.patch_pack(sarc.write(pack), actor=getitem.FAIRY, performer=native_performer())
    with pytest.raises(PatchError):
        getitem.patch_pack(data, actor=getitem.FAIRY, performer=byml.write({"EventUniqueAin": "Changed"}))
    with pytest.raises(PatchError):
        getitem.patch_pack(data, actor="Other", performer=native_performer())
    assert sarc.read(data) != pack


def test_structural_growth_cannot_borrow_a_string_substitution_allocation():
    actor = "Item_Melody_StormSong"
    before, model = actor_pack(actor)
    pack = sarc.read(getitem.patch_pack(before, actor=actor, performer=native_performer()))
    tree = byml.read(pack[model])
    tree["NewArray"] = [byml.I32(1)]
    pack[model] = byml.write(tree)
    with pytest.raises(PatchError):
        getitem.member_growth(before, sarc.write(pack))


def test_common_writer_reserves_nested_model_growth_without_lowering_other_entries(tmp_path, zsdic_pack):
    actor = "Item_Melody_StormSong"
    before, model = actor_pack(actor)
    # Put the synthetic original exactly on a size bucket boundary.
    pack = sarc.read(before)
    pack[model] = byml.write(byml.read(pack[model]) | {"Padding": ""})
    before = sarc.write(pack)
    transform = partial(getitem.patch_pack, actor=actor, performer=native_performer())
    after = sarc.read(transform(before))
    old = sarc.read(before)
    delta = ((len(after[model]) + 31) // 32 - (len(old[model]) + 31) // 32) * 32
    assert delta > 0
    romfs = tmp_path / "dump"
    dictionaries = zsdic.Dictionaries.from_pack(zsdic_pack)
    path = getitem.pack_path(actor)
    for name, content in ((zsdic.PACK_PATH, zsdic_pack), (path, dictionaries.compress(path, before))):
        (romfs / name).parent.mkdir(parents=True, exist_ok=True)
        (romfs / name).write_bytes(content)
    table = rstb.ResourceSizeTable()
    table.set(model, 6000)
    table.set(path, 1 << 20)
    table.set("Unrelated", 1234)
    table_path = romfs / rstb.TABLE_PATH
    table_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.write_bytes(dictionaries.compress(rstb.TABLE_PATH, rstb.write(table)))
    out = tmp_path / "out"
    write(Plan([], [], []), romfs, out, extra_changes=({path: transform},))
    result = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (out / "romfs" / rstb.TABLE_PATH).read_bytes()))
    expected = copy.deepcopy(table)
    expected.set(model, 6000 + delta)
    assert result == expected
