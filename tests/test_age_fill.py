"""Forward return-kit fill must preserve compulsory child errands and bootstrap adult key doors."""

from clawshot.generate import Settings, generate
from clawshot.generate.fill import allowed
from clawshot.world import CHILD, Search, load_spec


def return_spec():
    return {
        "start": "Root",
        "goal": "'Forest Clear'",
        "settings": {
            "starting_age": "child",
            "age_return_event": "Forest Clear",
            "age_return_region": "Field",
            "age_pull_event": "Time Travel",
            "age_return_guarantee": True,
            "age_return_fill_families": ["Strength", "Weapon", "Small Key (D)"],
            "age_return_bypass_families": ["Strength"],
            "age_return_fill_inventory": {"Song": 1, "Strength": 1},
        },
        "items": {
            "Song": {},
            "Strength": {},
            "Bracelet": {"alias": ["Strength", 1]},
            "Upgrade": {"alias": ["Strength", 2]},
            "Weapon": {},
            "Small Key (D)": {"type": "SmallKey"},
            "Rupee": {"class": "normal"},
        },
        "regions": [
            {"name": "Root", "exits": {"Field": "age == starting_age or 'Time Travel'"}},
            {
                "name": "Field",
                "events": {"Time Travel": "age == 'child' and Strength"},
                "locations": {
                    "Child Song": {"rule": "age == 'child'", "type": "NPC", "vanilla": "Song"},
                    "Child Bracelet": {
                        "rule": "age == 'child' and Song",
                        "type": "NPC",
                        "vanilla": "Bracelet",
                    },
                    "Shared A": {"rule": "True", "type": "Chest", "vanilla": "Upgrade"},
                    "Shared B": {"rule": "True", "type": "Chest", "vanilla": "Weapon"},
                },
                "exits": {"Dungeon": "age == 'adult'"},
            },
            {
                "name": "Dungeon",
                "dungeon": "D",
                "locations": {"First Key": {"rule": "True", "type": "Chest", "vanilla": "Small Key (D)"}},
                "exits": {"Middle": "Small_Key_D"},
            },
            {
                "name": "Middle",
                "dungeon": "D",
                "locations": {"Second Key": {"rule": "True", "type": "Chest", "vanilla": "Small Key (D)"}},
                "exits": {"End": "(Small_Key_D, 2)"},
            },
            {
                "name": "End",
                "dungeon": "D",
                "locations": {"Adult Chest": {"rule": "True", "type": "Chest", "vanilla": "Rupee"}},
                "events": {"Forest Clear": "Weapon and Song"},
            },
        ],
    }


def test_return_kit_stays_adult_and_keys_bootstrap_without_optional_child_loot():
    result = generate(return_spec(), 0, Settings())
    [upgrade] = [name for name, item in result.placements.items() if item == "Upgrade"]
    maximal = Search(result.world, result.placements.values())
    assert not maximal.can_access(result.world.locations[upgrade], CHILD)

    planned = Search(result.world)
    planned.collect_spheres(result.placements)
    assert planned.mandatory_pull_inventory(result.placements)["Song"] == 1

    adult = Search.adult_after_pull(result.world, ["Song", "Bracelet"])
    adult.collect_spheres(result.placements)
    assert adult.holds("Forest Clear")
    assert adult.counts["Small Key (D)"] == 2
    assert {"First Key", "Second Key", "Adult Chest"} <= adult.collected


def test_chest_and_shop_seed_is_beatable_with_gated_return_guarantee():
    settings = Settings(shuffle=("Chest", "Shop"), logic={"age_return_guarantee": True, "free_time_travel": False})
    result = generate(load_spec(), 0, settings)
    search = Search(result.world)
    search.collect_spheres(result.placements)
    assert search.holds("Time Travel")
    assert search.holds("Defeat Phantom Ganon")
    assert search.won()
    assert all(allowed(result.world, settings, name, result.placements[name]) for name in result.shuffled)
