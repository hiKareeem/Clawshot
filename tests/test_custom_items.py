"""Custom items (clawshot.patch.custom_items) and the writer's new files, on synthetic packs, tables and messages."""

import pytest

from clawshot.formats import byml, msbt, rstb, sarc, zsdic
from clawshot.patch import custom_items
from clawshot.patch.custom_items import DONOR, NOTHING, Foreign
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import NewFile, write

PARAM = f"Actor/{DONOR}.engine__actor__ActorParam.bgyml"
MODEL = f"Component/ModelInfo/{DONOR}.engine__component__ModelInfo.bgyml"


def donor_pack() -> bytes:
    param = {
        "$parent": "Work/Actor/Item_EventObject_Base.engine__actor__ActorParam.gyml",
        "Components": {
            "ActorNameRef": f"?ActorSystem/ActorName/{DONOR}.engine__actor__ActorName.bgyml",
            "ModelInfoRef": f"?{MODEL}",
        },
    }
    return sarc.write({PARAM: byml.write(param), MODEL: byml.write({"FmdbName": DONOR, "ModelProjectName": DONOR})})


def test_a_new_actor_is_the_letter_under_its_own_name():
    new = custom_items.build_pack(donor_pack(), NOTHING)
    files = sarc.read(new.data)
    param = f"Actor/{NOTHING}.engine__actor__ActorParam.bgyml"
    assert sorted(files) == sorted([param, MODEL])
    components = byml.read(files[param])["Components"]
    assert components["ActorNameRef"] == f"?ActorSystem/ActorName/{NOTHING}.engine__actor__ActorName.bgyml"
    assert components["ModelInfoRef"] == f"?{MODEL}"  # the letter's model
    assert files[MODEL] == sarc.read(donor_pack())[MODEL]
    assert set(new.members) == {param} and new.members[param][0] == PARAM


def table(rows) -> bytes:
    return byml.write(sorted(rows, key=lambda r: r["__RowId"]))


def test_rows_are_copied_from_the_letter_and_kept_in_name_order():
    rows = [
        {"__RowId": "Aaa", "ActorName": "Aaa"},
        {"__RowId": DONOR, "ActorName": DONOR, "FmdbName": DONOR},
        {"__RowId": "Zzz", "ActorName": "Zzz"},
    ]
    actors = (NOTHING, "Item_Clawshot_AP_000")
    out = byml.read(custom_items.add_rows(table(rows), table=custom_items.ACTOR_INFO, actors=actors))
    ids = [row["__RowId"] for row in out]
    assert ids == sorted(ids) and set(actors) <= set(ids)
    nothing = next(row for row in out if row["__RowId"] == NOTHING)
    assert nothing == {"__RowId": NOTHING, "ActorName": NOTHING, "FmdbName": DONOR}  # text key = new name
    pouch = byml.read(custom_items.add_rows(table(rows), table=custom_items.POUCH_ACTOR_INFO, actors=actors))
    row = next(row for row in pouch if row["__RowId"] == NOTHING)
    assert row["PouchSpecialDeal"] == "NotPushToPouch" and "AssignableItem" not in row
    with pytest.raises(PatchError, match="already has a row"):
        custom_items.add_rows(table(rows), table=custom_items.ACTOR_INFO, actors=("Aaa",))
    with pytest.raises(PatchError, match="no Item_ZeldaLetter row"):
        custom_items.add_rows(table(rows[:1]), table=custom_items.ACTOR_INFO, actors=actors)


def test_texts_are_added_per_actor_and_own_lines_say_your():
    pouch = msbt.Msbt(
        {"Item_Boomerang_Name": ["Boomerang"], "Item_Boomerang_GetMessage": ["You found the Boomerang!"]}, 7
    )
    foreign = {
        "Kokiri Forest Chest": Foreign("Kareem", "Morph Ball"),
        "Mido Chest": Foreign("Me", "Progressive Wallet", own=True),
    }
    actors = custom_items.foreign_actors(foreign)
    assert actors == {"Kokiri Forest Chest": "Item_Clawshot_AP_000", "Mido Chest": "Item_Clawshot_AP_001"}
    out = custom_items.pouch_texts(
        "USen", pouch, nothing=True, foreign=foreign, actors=actors, own_keys=["Item_Boomerang", "Missing"]
    )
    messages = out.messages
    assert msbt.plain(messages["Item_Boomerang_GetMessage"]) == "You found your Boomerang!"
    assert msbt.plain(messages[f"{NOTHING}_GetMessage"]) == "You found Nothing."
    assert msbt.plain(messages["Item_Clawshot_AP_000_GetMessage"]) == "You found Kareem's Morph Ball!"
    assert msbt.plain(messages["Item_Clawshot_AP_001_GetMessage"]) == "You found your Progressive Wallet!"
    assert list(messages)[:2] == ["Item_Boomerang_Name", "Item_Boomerang_GetMessage"]  # natives keep their order
    assert msbt.read(msbt.write(out)) == out
    with pytest.raises(PatchError, match="already taken"):
        custom_items.pouch_texts("USen", out, nothing=True, foreign={}, actors={})


def test_the_writer_adds_new_files_with_size_entries(tmp_path, zsdic_pack):
    romfs = tmp_path / "dump"
    dicts = zsdic.Dictionaries.from_pack(zsdic_pack)
    (romfs / zsdic.PACK_PATH).parent.mkdir(parents=True)
    (romfs / zsdic.PACK_PATH).write_bytes(zsdic_pack)
    sizes = rstb.ResourceSizeTable()
    sizes.set(PARAM, 5000)
    (romfs / rstb.TABLE_PATH).parent.mkdir(parents=True)
    (romfs / rstb.TABLE_PATH).write_bytes(dicts.compress(rstb.TABLE_PATH, rstb.write(sizes)))
    new = custom_items.build_pack(donor_pack(), NOTHING)
    path = f"Pack/Actor/{NOTHING}.pack.zs"
    written = write(Plan([], [], []), romfs, tmp_path / "out", new_files={path: new})
    assert sorted(f.path for f in written) == sorted([path, rstb.TABLE_PATH])
    assert dicts.decompress(path, (tmp_path / "out/romfs" / path).read_bytes()) == new.data
    result = rstb.read(dicts.decompress(rstb.TABLE_PATH, (tmp_path / "out/romfs" / rstb.TABLE_PATH).read_bytes()))
    member = f"Actor/{NOTHING}.engine__actor__ActorParam.bgyml"
    assert result.get(member) == 5000 + new.members[member][1]
    assert result.get(path) == rstb.required_size(path, len(new.data))
    assert not (romfs / path).exists()  # the dump is never written
    with pytest.raises(PatchError, match="does not hold"):
        (romfs / "Pack/Actor").mkdir(parents=True)
        (romfs / path).write_bytes(b"")
        write(Plan([], [], []), romfs, tmp_path / "out2", new_files={path: NewFile(b"x")})
