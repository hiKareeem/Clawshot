"""Generic dungeon rewards must be collected inside the dungeon they credit."""

import pytest

from clawshot.generate import Settings, generate
from clawshot.generate.fill import allowed, check_beatable
from clawshot.patch import gifts, make_seed
from clawshot.world import build_world, load_spec, load_world


@pytest.mark.parametrize("kind", ["SmallKey", "BossKey", "Map", "Compass"])
def test_logical_dungeon_location_outside_its_area_cannot_receive_dungeon_item(kind):
    item = f"{kind} (Temple)"
    spec = {
        "start": "Temple Lobby",
        "goal": f"'{item}'",
        "items": {item: {"type": kind}, "Coin": {"class": "normal"}},
        "regions": [
            {
                "name": "Temple Lobby",
                "area": "TempleArea",
                "dungeon": "Temple",
                "locations": {
                    "Inside": {"type": "Chest", "vanilla": item, "rule": "True"},
                    "Outside": {
                        "type": "Chest",
                        "vanilla": "Coin",
                        "rule": "True",
                        "area": "OverworldArea",
                    },
                },
            }
        ],
    }
    world = build_world(spec)
    assert not allowed(world, Settings(), "Outside", item), (kind, world.locations["Outside"])
    assert allowed(world, Settings(), "Inside", item)
    # Only small keys have a named grant; the other families remain physically restricted.
    assert allowed(world, Settings(dungeon_items="anywhere"), "Outside", item) is (kind == "SmallKey")
    assert allowed(world, Settings(dungeon_items="anywhere"), "Inside", item)
    result = generate(spec, 0, Settings(), attempts=1)
    assert result.placements == {"Inside": item, "Outside": "Coin"}
    check_beatable(result.world, result.placements)


@pytest.mark.parametrize("chest", ["Spirit Temple Silver Gauntlets Chest", "Spirit Temple Mirror Shield Chest"])
def test_spirit_hands_reject_generic_items_but_allow_named_small_keys(chest):
    world = load_world()
    for item in (
        "Small Key (Spirit Temple)",
        "Boss Key (Spirit Temple)",
        "Map (Spirit Temple)",
        "Compass (Spirit Temple)",
    ):
        assert not allowed(world, Settings(), chest, item), (chest, item, world.locations[chest])
        assert allowed(world, Settings(), "Spirit Temple Map Chest", item)
        assert allowed(world, Settings(dungeon_items="anywhere"), chest, item) is (world.items[item].type == "SmallKey")


@pytest.mark.dump
def test_community_seed_eleven_keeps_spirit_dungeon_items_off_both_hands(romfs):
    settings = Settings(shuffle=("Chest", "Shop", "Gift", "Scrub", "BossHeart"))
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), settings)
    result = make_seed(romfs, 11, settings, spec, extra_steps=(step,)).seed
    for chest in ("Spirit Temple Silver Gauntlets Chest", "Spirit Temple Mirror Shield Chest"):
        assert result.world.items[result.placements[chest]].dungeon is None, (chest, result.placements[chest])
    check_beatable(result.world, result.placements)
