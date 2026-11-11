from dataclasses import replace

import pytest

from clawshot.census.gifts import DIRECT, Gift
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


def gift_step(call):
    return Gift("Test/Event0", "npc_gift", "Test", "Test.bfevfl.zs", ("Talk",), "Event0", call, "Actor", "", "")


@pytest.mark.parametrize("item", ["Fairy Ocarina", "Ocarina of Time"])
@pytest.mark.parametrize("mode", ["song", "anywhere"])
def test_ocarina_fill_uses_reachable_chests_instead_of_hand_over_gifts(item, mode):
    # Seed 1 previously put either instrument at Gift. The second chest needs it,
    # so restricting destinations must also preserve the assumed-fill proof.
    spec = {
        "start": "Root",
        "goal": repr(item),
        "items": {item: {}, "Boomerang": {}, "Rupees (20)": {"class": "normal"}},
        "regions": [
            {
                "name": "Root",
                "locations": {
                    "Early Chest": {"type": "Chest", "vanilla": "Rupees (20)", "rule": "True"},
                    "Locked Chest": {"type": "Chest", "vanilla": "Boomerang", "rule": repr(item)},
                    "Gift": {"type": "NPC", "vanilla": item, "rule": "True"},
                },
            }
        ],
    }
    spec["locations"] = {name: {"type": info["type"]} for name, info in spec["regions"][0]["locations"].items()}
    spec = gifts.restrict_spec(
        spec, ["Gift"], {"Gift": (gift_step("NpcCommon:NpcCommon_HandOver_NpcToPlayer_NoDisplay"),)}
    )
    world = build_world(spec)
    held = gifts.held_items(world, world.items, items.load(), {"TBox_Rupee_Red", "Item_Boomerang"}, songs=mode)
    settings = Settings(shuffle=("Chest", "NPC"), songs=mode, item_location_types=held)
    seed = generate(spec, 1, settings, attempts=1)
    assert seed.placements["Early Chest"] == item
    assert seed.placements["Gift"] != item
    sphere_of = {name: index for index, sphere in enumerate(seed.spheres) for name in sphere}
    assert sphere_of["Early Chest"] < sphere_of["Locked Chest"]
    for kind in gifts.GIFT_TYPES:
        world.locations["Gift"] = replace(world.locations["Gift"], type=kind)
        assert not allowed(world, settings, "Gift", item)


@pytest.mark.parametrize("item", ["Fairy Ocarina", "Ocarina of Time"])
@pytest.mark.parametrize("call", [DIRECT, "GetPouchContent:GetPouchContentByActorName"])
def test_gift_only_ocarinas_still_have_direct_story_destinations(item, call):
    places = {
        "Story Scene": {"type": "NPC", "vanilla": item, "rule": "True"},
        "Hand Over": {"type": "NPC", "vanilla": "Rupees (20)", "rule": "True"},
    }
    spec = {
        "start": "Root",
        "goal": repr(item),
        "items": {item: {}, "Rupees (20)": {"class": "normal"}},
        "regions": [{"name": "Root", "locations": places}],
        "locations": {name: {"type": info["type"]} for name, info in places.items()},
    }
    steps = {
        "Story Scene": (gift_step(call),),
        "Hand Over": (gift_step("Dm_SY_GetInEvent:GetInEvent_NotTurn_NotNpc"),),
    }
    spec = gifts.restrict_spec(spec, places, steps)
    world = build_world(spec)
    held = gifts.held_items(world, world.items, items.load(), set(), songs="anywhere")
    seed = generate(spec, 1, Settings(shuffle=("NPC",), item_location_types=held), attempts=1)
    assert seed.placements == {"Story Scene": item, "Hand Over": "Rupees (20)"}


@pytest.mark.parametrize("kind", ["Scrub", "GrottoScrub"])
def test_ocarina_restriction_covers_scrub_sales_in_a_mixed_pool(kind):
    places = {
        "Chest": {"type": "Chest", "vanilla": "Rupees (20)", "rule": "True"},
        "Sale": {"type": kind, "vanilla": "Fairy Ocarina", "rule": "True"},
    }
    spec = {
        "start": "Root",
        "goal": "Fairy_Ocarina",
        "items": {"Fairy Ocarina": {}, "Rupees (20)": {"class": "normal"}},
        "regions": [{"name": "Root", "locations": places}],
        "locations": {name: {"type": info["type"]} for name, info in places.items()},
    }
    spec = gifts.restrict_spec(spec, ())
    seed = generate(spec, 1, Settings(shuffle=("Chest", kind)), attempts=1)
    assert seed.placements == {"Chest": "Fairy Ocarina", "Sale": "Rupees (20)"}
