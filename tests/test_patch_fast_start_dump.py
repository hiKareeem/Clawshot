"""The default closed-forest seed removes the opening movie through the public path, without story flags."""

import pytest

from clawshot.formats import byml, zsdic
from clawshot.generate import Settings
from clawshot.patch import make_seed, write_seed
from clawshot.patch.gamedata import GAME_DATA_LIST, OPENING_FLOW, _find, opening_without_movie

pytestmark = pytest.mark.dump
SLICE = ("KokiriForest", "LostWood", "InsideTheDekuTree")


def test_default_seed_removes_the_opening_movie_without_story_flags(romfs, tmp_path):
    output = make_seed(romfs, 7, Settings(areas=SLICE, goal="'Defeat Queen Gohma'"))
    target = tmp_path / "default"
    write_seed(output, romfs, target)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    native = dicts.decompress(OPENING_FLOW, (romfs / OPENING_FLOW).read_bytes())
    written = dicts.decompress(OPENING_FLOW, (target / "romfs" / OPENING_FLOW).read_bytes())
    assert written == opening_without_movie(native)
    expected = byml.read(dicts.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes()))
    _, navi = _find(expected, "ActionGuide_IsEnd.Navi")
    navi["DefaultValue"] = True
    actual = byml.read(dicts.decompress(GAME_DATA_LIST, (target / "romfs" / GAME_DATA_LIST).read_bytes()))
    assert byml.difference(actual, expected) is None
