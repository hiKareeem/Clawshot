"""Compare player floor metadata against map icons and physical room identities."""

import re
from collections import Counter

import pytest

from clawshot.census.definitions import load as definitions
from clawshot.formats import byml
from clawshot.formats.zsdic import Dictionaries
from clawshot.generate.names import load as names

pytestmark = pytest.mark.dump
MAP = "Banc/BancBasedResource/MapParam.byml.zs"
AREAS = {
    "BottomOfTheWell",
    "DodongoCavern",
    "FireTemple",
    "ForestTemple",
    "GerudoTrainingGround",
    "IceCavern",
    "InsideGanonCastle",
    "InsideJabuJabuBelly",
    "InsideTheDekuTree",
    "ShadowTemple",
    "SpiritTemple",
    "WaterTemple",
}


def test_dungeon_directions_use_the_exact_pause_map_floor(romfs):
    dictionaries = Dictionaries.from_romfs(romfs)
    maps = byml.read(dictionaries.decompress(MAP, (romfs / MAP).read_bytes()))
    catalog = names()
    actors = {}
    for area in sorted(AREAS):
        actors[area] = {}
        for kind in ("Static", "Dynamic"):
            path = f"Banc/{area}/{area}_{kind}.bcett.byml.zs"
            tree = byml.read(dictionaries.decompress(path, (romfs / path).read_bytes()))
            actors[area].update((int(a["Hash"]), a) for a in tree["Actors"])
    checked = set()
    fire_chests = Counter()
    for definition in definitions():
        if definition.area not in AREAS or definition.kind not in {"chest", "heart_container"}:
            continue
        key = definition.oot_randomizer_name or definition.name
        actual = catalog[key]
        mapping = maps[definition.area]
        actor = actors[definition.area][definition.id]
        logical = [
            int(mapping["MinFloor"]) + slot
            for slot, floor in enumerate(mapping["Floor"])
            if any(box["InstanceID"] == definition.id for box in floor["TBox"])
        ]
        if not logical:
            room = actor.get("Dynamic", {}).get("DefaultDungeonRoomIndex")
            if definition.kind == "heart_container":
                if room is not None:
                    assert room == mapping["BossRoomId"], (key, room, mapping["BossRoomId"])
                room = mapping["BossRoomId"]
            assert room is not None, (key, actor)
            logical = [int(f) for f in mapping["Room"][int(room)]["Floor"]]
        assert len(logical) == 1, (key, logical)
        floor = logical[0]
        expected = f"{floor + 1}F" if floor >= 0 else f"B{-floor}"
        assert actual.floor == expected, (key, definition.id, actual.floor, expected)
        visible_floors = re.findall(r"\b(?:B[1-9][0-9]*|[1-9][0-9]*F)\b", actual.name + " " + actual.where)
        assert expected in visible_floors, (key, actual.name, actual.where, expected)
        checked.add(key)
        if definition.area == "FireTemple" and definition.kind == "chest":
            fire_chests[expected] += 1
    # A tall room must not flatten every chest to its room's first floor.
    assert catalog["Fire Temple Near Boss Chest"].floor == "1F"
    assert catalog["Fire Temple Boulder Maze Shortcut Chest"].floor == "2F"
    assert catalog["Fire Temple Scarecrow Chest"].floor == "5F"
    assert catalog["Deku Tree Map Chest"].floor == "2F"
    assert catalog["Deku Tree Basement Chest"].floor == "B1"
    assert fire_chests == {"1F": 5, "2F": 1, "3F": 6, "5F": 4}
    assert sum(a["Gyaml"] == "Enemy_Skulltula_Gold" for a in actors["FireTemple"].values()) == 5
    assert catalog["Sheik in Ice Cavern"].floor == catalog["Ice Cavern Iron Boots Chest"].floor
    checked.add("Sheik in Ice Cavern")
    assert {key for key, description in catalog.items() if description.floor} == checked
