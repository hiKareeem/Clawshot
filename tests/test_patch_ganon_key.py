"""The final boss key participates in the same dungeon ownership contract as other boss keys."""

from clawshot.generate.fill import Settings, allowed
from clawshot.patch.items import loads
from clawshot.world.load import apply_overrides, build_world


def test_ganon_boss_key_ownership_and_actor_disambiguation():
    world = build_world(
        {
            "start": "Field",
            "goal": "True",
            "items": {
                "Boss Key (Ganons Castle)": {"type": "GanonBossKey"},
                "Boss Key (Forest Temple)": {"type": "BossKey"},
            },
            "regions": [
                {"name": "Field", "locations": {"Field Chest": {"rule": "True", "type": "Chest"}}},
                {
                    "name": "Tower",
                    "dungeon": "Ganons Castle",
                    "locations": {"Tower Chest": {"rule": "True", "type": "Chest"}},
                },
            ],
        }
    )
    key = "Boss Key (Ganons Castle)"
    assert allowed(world, Settings(), "Tower Chest", key)
    assert not allowed(world, Settings(), "Field Chest", key)
    assert allowed(world, Settings(dungeon_items="anywhere"), "Field Chest", key)
    table = loads(
        '[items]\n"Boss Key (Ganons Castle)" = { actor = "Item_Dungeon_BossKey" }\n'
        '"Boss Key (Forest Temple)" = { actor = "Item_Dungeon_BossKey" }\n'
    )
    table.check(world.items)
    assert table.item("Item_Dungeon_BossKey", "Ganons Castle", world.items) == key


def test_region_metadata_override_allows_the_tower_but_not_the_field():
    spec = {
        "start": "Field",
        "goal": "True",
        "items": {"Boss Key (Ganons Castle)": {"type": "GanonBossKey"}},
        "locations": {},
        "regions": [
            {"name": "Field", "locations": {"Field Chest": {"rule": "True", "type": "Chest"}}},
            {"name": "Tower", "locations": {"Tower Chest": {"rule": "True", "type": "Chest"}}},
            {
                "name": "Castle",
                "dungeon": "Ganons Castle",
                "locations": {"Castle Chest": {"rule": "True", "type": "Chest"}},
            },
        ],
    }
    apply_overrides(
        spec,
        [("tower.toml", {"regions": {"Tower": {"new": False, "dungeon": "Ganons Castle", "source": "test"}}})],
    )
    world = build_world(spec)
    key = "Boss Key (Ganons Castle)"
    assert allowed(world, Settings(), "Tower Chest", key)
    assert allowed(world, Settings(), "Castle Chest", key)
    assert not allowed(world, Settings(), "Field Chest", key)
