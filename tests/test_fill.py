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


def _bracelet_spec() -> dict:
    # Seed 7 Gift: Zelda's Letter went where only Bombchus reach while every Bombchu pack still had to wait behind a
    # Bomb Bag (D25), so the last pack had nowhere reachable.
    explosives = "(Bomb_Bag and Bracelet) or Bombchus_5"
    return {
        "start": "Start",
        "goal": "Bracelet and Bomb_Bag and Bombchus_5",
        "items": {"Bomb Bag": {}, "Bracelet": {}, "Bombchus (5)": {}, "Rupee": {"class": "normal"}},
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Open NPC": {"rule": "True", "type": "NPC", "vanilla": "Rupee"},
                    "Wall NPC": {"rule": explosives, "type": "NPC", "vanilla": "Bracelet"},
                    "Bag Chest": {"rule": "True", "type": "Chest", "vanilla": "Bomb Bag"},
                    "Wall Chest": {"rule": explosives, "type": "Chest", "vanilla": "Bombchus (5)"},
                },
            }
        ],
    }


def test_held_items_before_the_ammo_stage_do_not_rely_on_bag_gated_bombchus():
    settings = Settings(shuffle=("Chest", "NPC"), item_location_types={"Bracelet": ("NPC",)})
    for number in range(20):
        seed = generate(_bracelet_spec(), number, settings, attempts=1)
        assert seed.placements["Open NPC"] == "Bracelet", (number, seed.placements)


def test_songs_with_no_spare_song_location_are_retried_as_their_own_stage():
    # OoT Randomizer places songs on their own and retries only that stage (Fill.py:348, 15 attempts at 526b4c8d).
    spec = {
        "start": "Start",
        "goal": "Lullaby and Storms",
        "items": {"Lullaby": {"type": "Song"}, "Storms": {"type": "Song"}},
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Free Song": {"rule": "True", "type": "Song", "vanilla": "Lullaby"},
                    "Lullaby Song": {"rule": "Lullaby", "type": "Song", "vanilla": "Storms"},
                },
            }
        ],
    }
    settings = Settings(
        shuffle=("Song",),
        item_location_types={"Lullaby": ("Song",), "Storms": ("Song",)},
        exclusive_location_types=("Song",),
    )
    for number in range(20):
        seed = generate(spec, number, settings, attempts=1)
        assert seed.placements == {"Free Song": "Lullaby", "Lullaby Song": "Storms"}, (number, seed.placements)


def test_either_shield_is_placed_while_the_other_can_still_open_the_way():
    # Shop mode kept native-display items (both shields) to the end of the progression stage; the last shield then
    # needed the only chest before Mido, already taken (seed 17 Chest+Shop: 70 allowed, none reachable).
    spec = {
        "start": "Start",
        "goal": "Sword",
        "settings": {"native_shop_items": ["Deku Shield", "Hylian Shield"]},
        "items": {"Sword": {}, "Deku Shield": {}, "Hylian Shield": {}, "Rupee": {"class": "normal"}},
        "regions": [
            {
                "name": "Start",
                "locations": {"Early Chest": {"rule": "True", "type": "Chest", "vanilla": "Deku Shield"}},
                "exits": {"Village": "Deku_Shield or Hylian_Shield"},
            },
            {
                "name": "Village",
                "locations": {
                    "Village A": {"rule": "True", "type": "Chest", "vanilla": "Sword"},
                    "Village B": {"rule": "True", "type": "Chest", "vanilla": "Hylian Shield"},
                    "Village C": {"rule": "True", "type": "Chest", "vanilla": "Rupee"},
                },
            },
        ],
    }
    for number in range(20):
        seed = generate(spec, number, Settings(shuffle=("Chest", "Shop")), attempts=1)
        assert seed.placements["Early Chest"] in ("Deku Shield", "Hylian Shield"), (number, seed.placements)


def _pickup_spec() -> dict:
    return {
        "start": "Start",
        "goal": "Key",
        "items": {"Key": {}, "Rupee": {"class": "normal"}, "Heart": {"class": "normal"}},
        "regions": [
            {
                "name": "Start",
                "locations": {"Early": {"rule": "True", "type": "Chest", "vanilla": "Rupee"}},
                "exits": {"Village": "Key"},
            },
            {
                "name": "Village",
                "locations": {
                    "Village A": {"rule": "True", "type": "Chest", "vanilla": "Key"},
                    "Village B": {"rule": "True", "type": "Chest", "vanilla": "Rupee"},
                    "Floor": {"rule": "True", "type": "BossHeart", "vanilla": "Heart"},
                },
            },
        ],
    }


def test_native_pickup_destinations_take_their_palette_and_leave_junk_to_the_fast_fill():
    # Holding every other item away from BossHeart/Freestanding sent junk through the reachability stage with the
    # progression, where it took the only early chest (cs8e's Chest+Freestanding seed 7: Boomerang, none reachable).
    settings = Settings(shuffle=("Chest", "BossHeart"), location_type_items={"BossHeart": ("Heart",)})
    for number in range(20):
        seed = generate(_pickup_spec(), number, settings, attempts=1)
        assert seed.placements["Early"] == "Key", (number, seed.placements)
        assert seed.placements["Floor"] == "Heart"
