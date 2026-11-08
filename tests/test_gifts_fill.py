"""Dungeon keys keep their bootstrap slots before bag-gated ammo is placed (D25)."""

from clawshot.generate import Settings, generate


def test_ammo_prefill_cannot_consume_the_only_early_dungeon_key_slot():
    spec = {
        "start": "Start",
        "goal": "Small_Key_Temple",
        "items": {
            "Bomb Bag": {},
            "Small Key (Temple)": {"type": "SmallKey"},
            "Bombs (5)": {"class": "normal"},
            "Bombchus (5)": {},
        },
        "regions": [
            {
                "name": "Start",
                "locations": {"Bag": {"rule": "True", "type": "Chest", "vanilla": "Bomb Bag"}},
                "exits": {"Temple": "Bomb_Bag"},
            },
            {
                "name": "Temple",
                "dungeon": "Temple",
                "locations": {
                    "Entrance Key": {"rule": "True", "type": "Chest", "vanilla": "Small Key (Temple)"},
                    "Locked Bombs": {"rule": "Small_Key_Temple", "type": "Chest", "vanilla": "Bombs (5)"},
                    "Locked Bombchus": {"rule": "Small_Key_Temple", "type": "Chest", "vanilla": "Bombchus (5)"},
                },
            },
        ],
    }
    seed = generate(spec, 0, Settings(), attempts=1)
    assert seed.placements["Bag"] == "Bomb Bag"
    assert seed.placements["Entrance Key"] == "Small Key (Temple)"
    assert {seed.placements[name] for name in ("Locked Bombs", "Locked Bombchus")} == {
        "Bombs (5)",
        "Bombchus (5)",
    }
    sphere_of = {name: index for index, sphere in enumerate(seed.spheres) for name in sphere}
    assert sphere_of["Bag"] < sphere_of["Entrance Key"]
    assert all(sphere_of["Entrance Key"] < sphere_of[name] for name in ("Locked Bombs", "Locked Bombchus"))


def test_type_held_song_is_placed_before_flexible_progression_can_depend_on_it():
    # The real Gift seed exposed Storms -> bag -> adult-only remaining song slots.
    # Keep the type-restricted song ahead of flexible items, not only shop-native items.
    spec = {
        "start": "Start",
        "goal": "Storms and Bomb_Bag and Hammer",
        "items": {"Bomb Bag": {}, "Hammer": {}, "Storms": {"type": "Song"}},
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Early Chest": {"rule": "True", "type": "Chest", "vanilla": "Bomb Bag"},
                    "Storms Chest": {"rule": "Storms", "type": "Chest", "vanilla": "Hammer"},
                    "Bag Song": {"rule": "Bomb_Bag", "type": "Song", "vanilla": "Storms"},
                },
            }
        ],
    }
    settings = Settings(
        shuffle=("Chest", "Song"),
        item_location_types={"Storms": ("Song",)},
        exclusive_location_types=("Song",),
    )
    seed = generate(spec, 2, settings, attempts=1)
    assert seed.placements == {"Early Chest": "Bomb Bag", "Storms Chest": "Hammer", "Bag Song": "Storms"}
    sphere_of = {name: index for index, sphere in enumerate(seed.spheres) for name in sphere}
    assert sphere_of["Early Chest"] < sphere_of["Bag Song"] < sphere_of["Storms Chest"]
