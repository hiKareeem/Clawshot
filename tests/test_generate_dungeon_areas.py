"""Generic dungeon rewards must be collected inside the dungeon they credit."""

import pytest

from clawshot.generate import Settings, generate
from clawshot.generate.fill import allowed, check_beatable
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
    # The synthetic anywhere mode represents named grants and keeps its independent policy.
    assert allowed(world, Settings(dungeon_items="anywhere"), "Outside", item)
    result = generate(spec, 0, Settings(), attempts=1)
    assert result.placements == {"Inside": item, "Outside": "Coin"}
    check_beatable(result.world, result.placements)


@pytest.mark.parametrize("chest", ["Spirit Temple Silver Gauntlets Chest", "Spirit Temple Mirror Shield Chest"])
def test_spirit_hands_reject_all_current_dungeon_reward_families(chest):
    world = load_world()
    for item in (
        "Small Key (Spirit Temple)",
        "Boss Key (Spirit Temple)",
        "Map (Spirit Temple)",
        "Compass (Spirit Temple)",
    ):
        assert not allowed(world, Settings(), chest, item), (chest, item, world.locations[chest])
        assert allowed(world, Settings(), "Spirit Temple Map Chest", item)


def test_seed_eleven_keeps_spirit_dungeon_items_off_both_hands():
    result = generate(load_spec(), 11, Settings())
    for chest in ("Spirit Temple Silver Gauntlets Chest", "Spirit Temple Mirror Shield Chest"):
        assert result.world.items[result.placements[chest]].dungeon is None, (chest, result.placements[chest])
    check_beatable(result.world, result.placements)
