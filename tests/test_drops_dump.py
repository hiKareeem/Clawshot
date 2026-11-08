import pytest

from clawshot.census.scan import GAME_DATA_LIST, read_romfs_byml, scan
from clawshot.formats import byml, zsdic
from clawshot.patch import drops


@pytest.mark.dump
def test_every_boss_heart_retains_spawn_groups_and_saved_hash(romfs):
    pickup = "Obj_Shield_Hylian"
    census = [loc for loc in scan(romfs) if loc.kind == "heart_container"]
    assert len(census) == 8
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    gd = read_romfs_byml(romfs, dicts, GAME_DATA_LIST)
    flags = {int(entry["Hash"]): entry for entry in gd["Data"]["Bool64bitKey"]}
    transforms = drops.changes({loc.id: pickup for loc in census}, census)
    for loc in census:
        assert flags[loc.id]["ResetTypeValue"] == 24
        assert flags[loc.id]["SaveFileIndex"] == 0
        for path in loc.files:
            raw = dicts.decompress(path, (romfs / path).read_bytes())
            before, after = byml.read(raw), byml.read(transforms[path](raw))
            actor = next(a for a in after["Actors"] if a["Hash"] == loc.id)
            assert actor["Gyaml"] == pickup
            actor["Gyaml"] = drops.HEART
            assert byml.same(before, after), (path, loc.id)
    print(f"{len(census)} boss hearts: only Gyaml changed; all spawn/save/group identities retained")
