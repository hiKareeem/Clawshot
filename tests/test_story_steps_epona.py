"""Native Epona progress belongs to Malon's child song scene, not its reward.

Read-only flow evidence: plans/03-game-data.md section 48.
"""

import pytest

from clawshot.world import CHILD, Search, build_world, load_spec


@pytest.fixture
def ranch_world():
    spec = load_spec()
    spec["start"] = "Lon Lon Ranch"
    return build_world(spec)


@pytest.mark.parametrize("event", ["Epona", "Links Cow"])
def test_remote_epona_song_does_not_replace_malons_source(ranch_world, event):
    adult = Search.adult_after_pull(ranch_world, ["Ocarina of Time", "Eponas Song"])
    adult.update()
    assert not adult.counts.get(event)

    completed = Search.adult_after_pull(
        ranch_world, ["Ocarina of Time", "Eponas Song", "Malon Song Source Cleared"]
    )
    completed.update()
    assert completed.counts.get(event)


def test_child_source_progress_survives_a_shuffled_non_song_reward(ranch_world):
    child = Search.child_only(ranch_world, ["Fairy Ocarina", "Weird Egg"])
    assert child.can_access(ranch_world.locations["Song from Malon"], CHILD)
    assert child.counts.get("Malon Song Source Cleared")
    assert not child.counts.get("Eponas Song")
    assert not child.counts.get("Epona")


@pytest.mark.parametrize("items", [["Weird Egg"], ["Fairy Ocarina"]])
def test_malon_source_keeps_its_instrument_and_talon_prerequisites(ranch_world, items):
    child = Search.child_only(ranch_world, items)
    child.update()
    assert not child.counts.get("Malon Song Source Cleared")


@pytest.mark.parametrize("event", ["Epona", "Links Cow"])
def test_source_progress_does_not_replace_the_playable_adult_song(ranch_world, event):
    adult = Search.adult_after_pull(ranch_world, ["Ocarina of Time", "Malon Song Source Cleared"])
    adult.update()
    assert not adult.counts.get(event)
