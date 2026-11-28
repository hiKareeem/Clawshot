"""Lake tree ownership gating preserves other Banc edits and Water Temple source state."""

from copy import deepcopy

import pytest

from clawshot.formats import byml, rstb, zsdic
from clawshot.patch._goggles import longshot_vines
from clawshot.patch.plan import ChestChange, PatchError, Plan
from clawshot.patch.write import write

WALL_HASHES = {"Child": 6295005719083773433, "Adult": 9829790505452123995}


def path(age):
    return f"Banc/HyruleField/HyruleField_{age}_Dynamic.bcett.byml.zs"


def tree(age):
    # Invented scene, not a dump excerpt. Only the target's stable identity/predicate is native.
    return {
        "Actors": [
            {
                "Hash": byml.U64(WALL_HASHES[age]),
                "Gyaml": "FldObj_AirWall_Hookshot",
                "Presence": {"FlagName": "WaterTemple_Room07_00", "IsNegation": True, "IsCheckLazy": False},
                "Phive": {"Placement": {"ID": "synthetic-wall"}},
            },
            {"Hash": byml.U64(101), "Gyaml": "Obj_TBox_A_01", "Dynamic": {"Drop__DropActor": "Item_TestBefore"}},
            {
                "Hash": byml.U64(102),
                "Gyaml": "FldObj_AirWall_Hookshot",
                "Presence": {"FlagName": "OtherBefore", "IsNegation": True},
            },
            {"Hash": byml.U64(103), "Gyaml": "OtherActor", "Presence": {"FlagName": "WaterTemple_Room07_00"}},
        ],
        "AiGroups": [{"Hash": byml.U64(104), "References": [{"Id": byml.U64(101), "InstanceName": "Test"}]}],
        "SyntheticRoom07State": False,
    }


@pytest.mark.parametrize("age", ["Child", "Adult"])
def test_only_the_identified_walls_presence_flag_changes(age):
    original = tree(age)
    result = byml.read(longshot_vines.changes()[path(age)](byml.write(original)))
    expected = deepcopy(original)
    expected["Actors"][0]["Presence"]["FlagName"] = "IsGet.Item_Longshot"
    assert byml.difference(expected, result) is None


@pytest.mark.parametrize("stale", ["missing", "duplicate", "gyaml", "flag", "negation", "lazy", "presence"])
def test_stale_wall_identity_or_predicate_is_refused(stale):
    original = tree("Child")
    wall = original["Actors"][0]
    if stale == "missing":
        wall["Hash"] = byml.U64(999)
    elif stale == "duplicate":
        original["Actors"].append(deepcopy(wall))
    elif stale == "gyaml":
        wall["Gyaml"] = "OtherActor"
    elif stale == "flag":
        wall["Presence"]["FlagName"] = "OtherFlag"
    elif stale == "negation":
        wall["Presence"]["IsNegation"] = False
    elif stale == "lazy":
        wall["Presence"]["IsCheckLazy"] = True
    else:
        del wall["Presence"]
    with pytest.raises(PatchError, match="Lake tree wall"):
        longshot_vines.changes()[path("Child")](byml.write(original))


def other_field_edit(data):
    document = byml.load(data)
    document.root["Actors"][2]["Presence"]["FlagName"] = "OtherAfter"
    return byml.dump(document)


@pytest.mark.parametrize("vines_first", [False, True])
def test_common_writer_keeps_chest_and_other_dynamic_edits(tmp_path, zsdic_pack, vines_first):
    romfs = tmp_path / "romfs"
    (romfs / zsdic.PACK_PATH).parent.mkdir(parents=True)
    (romfs / zsdic.PACK_PATH).write_bytes(zsdic_pack)
    dictionaries = zsdic.Dictionaries.from_pack(zsdic_pack)
    table = rstb.ResourceSizeTable()
    for age in ("Child", "Adult"):
        rel = path(age)
        (romfs / rel).parent.mkdir(parents=True, exist_ok=True)
        (romfs / rel).write_bytes(dictionaries.compress(rel, byml.write(tree(age))))
        table.set(rel, 1 << 20)
    (romfs / rstb.TABLE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (romfs / rstb.TABLE_PATH).write_bytes(dictionaries.compress(rstb.TABLE_PATH, rstb.write(table)))
    before = {p: p.read_bytes() for p in romfs.rglob("*") if p.is_file()}
    plan = Plan(
        [
            ChestChange(
                "Synthetic chest",
                101,
                "Synthetic chest",
                (path("Child"), path("Adult")),
                "Obj_TBox_A_01",
                "Rupees (5)",
                "Item_TestBefore",
                "Item_TestAfter",
                None,
            )
        ],
        [],
        [],
    )
    other = {path(age): other_field_edit for age in ("Child", "Adult")}
    changes = (longshot_vines.changes(), other) if vines_first else (other, longshot_vines.changes())
    out = tmp_path / "output"
    write(plan, romfs, out, extra_changes=changes)
    for age in ("Child", "Adult"):
        rel = path(age)
        result = byml.read(dictionaries.decompress(rel, (out / "romfs" / rel).read_bytes()))
        expected = tree(age)
        expected["Actors"][0]["Presence"]["FlagName"] = "IsGet.Item_Longshot"
        expected["Actors"][1]["Dynamic"]["Drop__DropActor"] = "Item_TestAfter"
        expected["Actors"][2]["Presence"]["FlagName"] = "OtherAfter"
        assert byml.difference(expected, result) is None
    assert {p: p.read_bytes() for p in romfs.rglob("*") if p.is_file()} == before


@pytest.mark.dump
def test_native_wall_rewrite_has_exactly_the_intended_delta(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    for age in ("Child", "Adult"):
        rel = path(age)
        data = dictionaries.decompress(rel, (romfs / rel).read_bytes())
        original = byml.read(data)
        expected = deepcopy(original)
        wall = next(a for a in expected["Actors"] if a["Hash"] == WALL_HASHES[age])
        wall["Presence"]["FlagName"] = "IsGet.Item_Longshot"
        result = longshot_vines.changes()[rel](data)
        assert byml.difference(expected, byml.read(result)) is None
        assert dictionaries.decompress(rel, dictionaries.compress(rel, result)) == result
