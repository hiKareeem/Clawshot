"""The default closed-forest seed only makes the intro skippable, without story flags."""

import pytest

from clawshot.formats import byml
from clawshot.generate import Settings
from clawshot.patch import make_seed, write_seed
from clawshot.patch.gamedata import GAME_DATA_LIST

pytestmark = pytest.mark.dump
INTRO = "Event/EventSetting/EventSettingComponentList/Dm_Kokiri_0000.engine__event__EventSettingComponentList.bgyml"
SLICE = ("KokiriForest", "LostWood", "InsideTheDekuTree")


def test_default_seed_makes_intro_skippable_without_story_flags(romfs, tmp_path):
    output = make_seed(romfs, 7, Settings(areas=SLICE, goal="'Defeat Queen Gohma'"))
    target = tmp_path / "default"
    write_seed(output, romfs, target)
    original = byml.read((romfs / INTRO).read_bytes())
    changed = byml.read((target / "romfs" / INTRO).read_bytes())
    assert "SkipSetting" in original["Components"]
    assert "SkipSetting" not in changed["Components"]
    assert not (target / "romfs" / GAME_DATA_LIST).exists()
