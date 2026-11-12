"""Skipping Saria must retain the visit state normally written by the area banner."""

import pytest

from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import gamedata
from clawshot.save import key

VISIT = "IsVisitLocation.KokiriForest"


@pytest.mark.parametrize("skips", [[], ["intro"], ["saria"], ["intro", "saria"]])
def test_saria_skip_marks_only_its_missing_area_banner_visited(skips):
    names = [
        "HavePlayedEvent.Dm_Kokiri_0045",
        "HavePlayedEvent.Dm_Kokiri_0050",
        "HavePlayedEvent.Dm_Kokiri_0060",
        "KokiriForest_LinkHouseDoor_Open",
        "HaveTalked.Npc_Kokiri_Saria_Child",
        VISIT,
        "IsVisitLocation.HyruleField",
    ]
    rows = [{"Hash": byml.U32(key(name)), "DefaultValue": False, "ResetTypeValue": byml.I32(8)} for name in names]
    data = byml.write({"Data": {"Bool": rows, "Int": [], "Enum": []}}, "big")
    result = byml.read(gamedata.patch_initial_values(data, gamedata.select(gamedata.load(), skips)))
    flags = {row["Hash"]: row["DefaultValue"] for row in result["Data"]["Bool"]}
    assert flags[key(VISIT)] is ("saria" in skips)
    assert flags[key("IsVisitLocation.HyruleField")] is False


@pytest.mark.dump
def test_native_saria_banner_visit_state_is_preserved(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    flow = "Event/EventFlow/Dm_Kokiri_0045.bfevfl.zs"
    fc = evfl.read(dictionaries.decompress(flow, (romfs / flow).read_bytes())).flowchart
    banner = next(event for event in fc.events if event.name == "Event7")
    assert fc.actors[banner.actor].actions[banner.action] == "EventTriggerOpenLocationUI"
    location = "Work/Location/KokiriForest.game__location__Location.gyml"
    assert banner.params == {"LocationName": location}
    path = "RSDB/Location.Product.111.rstbl.byml.zs"
    locations = byml.read(dictionaries.decompress(path, (romfs / path).read_bytes()))
    assert next(row for row in locations if row["__RowId"] == location)["IsShowLocationUIFirstTimeInDemo"]
    path = gamedata.GAME_DATA_LIST
    data = dictionaries.decompress(path, (romfs / path).read_bytes())
    original = byml.read(data)
    _, before = gamedata._find(original, VISIT)
    assert before["DefaultValue"] is False
    assert before["ResetTypeValue"] == 8 and before["SaveFileIndex"] == 0
    patched = byml.read(gamedata.patch_initial_values(data, gamedata.select(gamedata.load(), ["saria"])))
    assert gamedata._find(patched, VISIT)[1]["DefaultValue"] is True
