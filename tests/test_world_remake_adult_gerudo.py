"""Gerudo storm grottos need the song, not the original game's Stone of Agony."""

import pytest

from clawshot.world import ADULT, Search, build_world, load_spec


@pytest.mark.parametrize(
    "start,target",
    [("GV Fortress Side", "GV Storms Grotto"), ("GF Entrances Behind Crates", "GF Storms Grotto")],
)
def test_visible_storm_grotto_needs_song_but_no_stone_of_agony(start, target):
    spec = load_spec()
    spec["start"] = start
    world = build_world(spec)
    search = Search(world, ["Fairy Ocarina"])
    assert not search.can_reach(target, ADULT)
    search.collect("Song of Storms")
    assert search.can_reach(target, ADULT)
