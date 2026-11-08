from dataclasses import replace

import pytest

from clawshot.generate import Settings, generate
from clawshot.generate.fill import allowed
from clawshot.patch import gifts, items
from clawshot.world.load import build_world


def song_spec():
    names = {
        "Storms": "Song",
        "Lullaby": "Song",
        "Fairy Ocarina": "Item",
        "Letter": "Item",
        "Coin": "Item",
        "Sword": "Item",
    }
    places = {
        "Song A": ("Song", "Storms"),
        "Song B": ("Song", "Lullaby"),
        "Gift A": ("NPC", "Fairy Ocarina"),
        "Gift B": ("NPC", "Letter"),
        "Chest A": ("Chest", "Coin"),
        "Chest B": ("Chest", "Sword"),
    }
    return {
        "start": "Root",
        "goal": "Sword",
        "items": {name: {"type": kind} for name, kind in names.items()},
        "regions": [{"name": "Root", "locations": {name: "True" for name in places}}],
        "locations": {name: {"type": kind, "vanilla": item} for name, (kind, item) in places.items()},
    }


@pytest.mark.parametrize("mode", ["song", "anywhere"])
def test_song_mode_respects_observed_chest_allowlist_in_actual_fills(mode):
    spec = song_spec()
    world = build_world(spec)
    actors = items.loads("""[items]
Storms = { actor = "Item_Melody_StormSong" }
Lullaby = { actor = "Item_Melody_ZeldaLullaby" }
"Fairy Ocarina" = { actor = "Item_Ocarina_Fairy" }
Letter = { actor = "Item_ZeldaLetter" }
Coin = { actor = "TBox_Rupee_Blue" }
Sword = { actor = "Item_Sword_Kokiri" }
""")
    held = gifts.held_items(world, world.items, actors, {"TBox_Rupee_Blue", "Item_Sword_Kokiri"}, songs=mode)
    settings = Settings(
        shuffle=("Chest", "NPC", "Song"),
        songs=mode,
        item_location_types=held,
        exclusive_location_types=("Song",) if mode == "song" else (),
    )
    assert Settings.from_string(settings.to_string()) == settings
    assert allowed(world, settings, "Chest A", "Fairy Ocarina")
    assert not allowed(world, settings, "Chest A", "Letter")
    assert allowed(world, settings, "Chest A", "Lullaby") == (mode == "anywhere")
    assert allowed(world, settings, "Chest A", "Storms") == (mode == "anywhere")
    seen = set()
    for number in range(30):
        seed = generate(spec, number, settings)
        for location, item in seed.placements.items():
            kind = seed.world.locations[location].type
            assert allowed(seed.world, settings, location, item)
            seen.add((item, kind))
            if mode == "song" and (kind == "Song" or item in ("Storms", "Lullaby")):
                assert kind == "Song" and item in ("Storms", "Lullaby")
    assert ("Fairy Ocarina", "Chest") in seen
    assert (("Storms", "Chest") in seen) == (mode == "anywhere")

    assert (("Lullaby", "Chest") in seen) == (mode == "anywhere")


def test_unknown_songs_mode_is_rejected():
    with pytest.raises(ValueError):
        replace(Settings(), songs="random")
