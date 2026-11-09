"""Round 8: the fill's first attempt succeeds where the measured whole-world failures came from."""

from clawshot.generate import Settings, generate


def _dungeon_spec() -> dict:
    # The remake's Fire Temple has no slack (plans/rounds/r8-fill.md): its one key-free chest and the two chests
    # behind the first lock must hold small keys, or the eighth key has nowhere to go. A boss key placed first
    # takes one of them as often as any other chest.
    return {
        "start": "Start",
        "goal": "Boss_Key_Temple and (Small_Key_Temple, 2)",
        "items": {
            "Small Key (Temple)": {"type": "SmallKey"},
            "Boss Key (Temple)": {"type": "BossKey"},
        },
        "regions": [
            {"name": "Start", "exits": {"Temple": "True"}},
            {
                "name": "Temple",
                "dungeon": "Temple",
                "locations": {
                    "Entrance": {"rule": "True", "type": "Chest", "vanilla": "Small Key (Temple)"},
                    "Middle": {"rule": "Small_Key_Temple", "type": "Chest", "vanilla": "Small Key (Temple)"},
                    "Deep A": {"rule": "(Small_Key_Temple, 2)", "type": "Chest", "vanilla": "Boss Key (Temple)"},
                },
            },
        ],
    }


def test_small_keys_take_their_forced_chests_before_the_boss_key():
    for number in range(20):
        seed = generate(_dungeon_spec(), number, Settings(), attempts=1)
        keys = (seed.placements["Entrance"], seed.placements["Middle"])
        assert keys == ("Small Key (Temple)", "Small Key (Temple)"), (number, seed.placements)
        assert seed.placements["Deep A"] == "Boss Key (Temple)"


def test_the_return_kit_leaves_another_dungeons_key_chest_to_its_key():
    # The real Golden Gauntlets went forward to the Fire Temple's key-free chest before the Fire keys were placed.
    spec = {
        "start": "Root",
        "goal": "'Forest Clear'",
        "settings": {
            "starting_age": "child",
            "age_return_event": "Forest Clear",
            "age_return_region": "Field",
            "age_pull_event": "Time Travel",
            "age_return_guarantee": True,
            "age_return_fill_families": ["Weapon"],
            "age_return_bypass_families": [],
            "age_return_fill_inventory": {},
        },
        "items": {"Weapon": {}, "Small Key (E)": {"type": "SmallKey"}, "Rupee": {"class": "normal"}},
        "regions": [
            {"name": "Root", "exits": {"Field": "age == starting_age or 'Time Travel'"}},
            {
                "name": "Field",
                "events": {"Time Travel": "age == 'child'", "Forest Clear": "age == 'adult' and Weapon"},
                "locations": {"Field Chest": {"rule": "True", "type": "Chest", "vanilla": "Rupee"}},
                "exits": {"E": "age == 'adult'"},
            },
            {
                "name": "E",
                "dungeon": "E",
                "locations": {
                    "E Entrance": {"rule": "True", "type": "Chest", "vanilla": "Small Key (E)"},
                    "E Inner": {"rule": "Small_Key_E", "type": "Chest", "vanilla": "Weapon"},
                },
            },
        ],
    }
    for number in range(20):
        seed = generate(spec, number, Settings(), attempts=1)
        assert seed.placements["E Entrance"] == "Small Key (E)", (number, seed.placements)
