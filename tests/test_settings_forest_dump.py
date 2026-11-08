import copy
from functools import partial

import pytest

from clawshot.census import definitions
from clawshot.census.gifts import FLOW_VERSIONS, flow_files, scan_gifts
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import byml, zsdic
from clawshot.patch import gamedata, gifts
from clawshot.patch.plan import Plan
from clawshot.patch.write import write
from clawshot.save import murmur3_32
from clawshot.settings import CATALOG

pytestmark = pytest.mark.dump
EXIT = "KokiriForest_Npc_Kokiri_007_Child_Blocker_00"
MIDO = "KokiriForest_Npc_Kokiri_Mido_Child_Blocker"


def entry(tree, name):
    return next(row for row in tree["Data"]["Bool"] if int(row["Hash"]) == murmur3_32(name.encode()))


@pytest.mark.parametrize("mode,names", [("closed_deku", (EXIT,)), ("open", (EXIT, MIDO))])
def test_forest_initial_values_change_only_the_selected_blockers(romfs, mode, names):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    data = dictionaries.decompress(gamedata.GAME_DATA_LIST, (romfs / gamedata.GAME_DATA_LIST).read_bytes())
    chosen = gamedata.select(gamedata.load(), CATALOG["forest"][mode]["fast_start"])
    output = gamedata.patch_initial_values(data, chosen)
    expected = byml.read(data)
    for name in names:
        row = entry(expected, name)
        assert row["DefaultValue"] is True and int(row["ResetTypeValue"]) == 8
        row["DefaultValue"] = False
    assert byml.byte_order(output) == byml.byte_order(data) == "big"
    assert byml.same(byml.read(output), expected)
    transient = "KokiriForest_Npc_Kokiri_007_Child_Blocker"
    assert entry(expected, transient)["DefaultValue"] is False


def test_forest_defaults_compose_with_new_saved_gift_flag(romfs, tmp_path):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    versions = {str(k): str(v) for k, v in read_romfs_byml(romfs, dictionaries, FLOW_VERSIONS)["Versions"].items()}
    changes = gifts.plan(
        {"DMT Great Fairy Reward": "Item_Hookshot"}, scan_gifts(romfs), definitions.load(), gifts.load()
    )
    chosen = gamedata.select(gamedata.load(), ["forest_exit"])
    transforms = gifts.file_changes(changes, flow_files(romfs, versions))
    out = tmp_path / "forest-gift"
    write(
        Plan([], [], []),
        romfs,
        out,
        extra_changes=(
            {gamedata.GAME_DATA_LIST: partial(gamedata.patch_initial_values, chosen=chosen)},
            transforms,
        ),
    )
    original = read_romfs_byml(romfs, dictionaries, gamedata.GAME_DATA_LIST)
    result = byml.read(
        dictionaries.decompress(gamedata.GAME_DATA_LIST, (out / "romfs" / gamedata.GAME_DATA_LIST).read_bytes())
    )
    flag = "Clawshot.Gift.Dm_FairyFountain_Din.Event212"
    added = entry(result, flag)
    assert added["DefaultValue"] is False and int(added["SaveFileIndex"]) == 0 and int(added["ResetTypeValue"]) == 8
    assert entry(result, EXIT)["DefaultValue"] is False
    assert entry(result, MIDO)["DefaultValue"] is True
    expected = copy.deepcopy(original)
    entry(expected, EXIT)["DefaultValue"] = False
    result["Data"]["Bool"].remove(added)
    for key in ("SaveDataOffsetPos", "SaveDataSize"):
        assert result["MetaData"][key][0] == expected["MetaData"][key][0] + 8
        result["MetaData"][key][0] -= 8
    for key in ("AllDataSaveOffset", "AllDataSaveSize"):
        assert result["MetaData"][key] == expected["MetaData"][key] + 8
        result["MetaData"][key] -= 8
    assert byml.same(result, expected)
