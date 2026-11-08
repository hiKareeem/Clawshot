"""Seed outputs include the selected fast-start files without opening the independent forest-exit gate."""

import pytest

from clawshot.formats import byml, zsdic
from clawshot.generate import Settings
from clawshot.patch import make_seed, write_seed
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.save import murmur3_32

pytestmark = pytest.mark.dump
INTRO = "Event/EventSetting/EventSettingComponentList/Dm_Kokiri_0000.engine__event__EventSettingComponentList.bgyml"
SLICE = ("KokiriForest", "LostWood", "InsideTheDekuTree")


def flag(tree, name):
    key = murmur3_32(name.encode("utf-8"))
    return next(e["DefaultValue"] for e in tree["Data"]["Bool"] if e["Hash"] == key)


def test_default_seed_makes_intro_skippable_without_story_flags(romfs, tmp_path):
    output = make_seed(romfs, 7, Settings(areas=SLICE, goal="'Defeat Queen Gohma'"))
    target = tmp_path / "default"
    write_seed(output, romfs, target)
    original = byml.read((romfs / INTRO).read_bytes())
    changed = byml.read((target / "romfs" / INTRO).read_bytes())
    assert "SkipSetting" in original["Components"]
    assert "SkipSetting" not in changed["Components"]
    assert not (target / "romfs" / GAME_DATA_LIST).exists()


def test_selected_mido_skip_changes_only_its_flag_and_logic(romfs, tmp_path):
    output = make_seed(
        romfs,
        7,
        Settings(areas=SLICE, goal="'Defeat Queen Gohma'", fast_start=("intro", "mido")),
    )
    target = tmp_path / "mido"
    write_seed(output, romfs, target)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    original = byml.read(dictionaries.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes()))
    changed = byml.read(dictionaries.decompress(GAME_DATA_LIST, (target / "romfs" / GAME_DATA_LIST).read_bytes()))
    mido = "KokiriForest_Npc_Kokiri_Mido_Child_Blocker"
    assert flag(original, mido) is True
    assert flag(changed, mido) is False
    assert output.seed.world.settings["skip_mido"] is True
    # No quest progress or other blocker is changed by this setting.
    expected = byml.read(dictionaries.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes()))
    key = murmur3_32(mido.encode("utf-8"))
    next(e for e in expected["Data"]["Bool"] if e["Hash"] == key)["DefaultValue"] = False
    assert byml.difference(expected, changed) is None
    for name in ("KokiriForest_Npc_Kokiri_007_Child_Blocker", "KokiriForest_Npc_Kokiri_007_Child_Blocker_00"):
        assert flag(changed, name) == flag(original, name)
