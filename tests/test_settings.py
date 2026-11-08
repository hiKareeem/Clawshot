import base64
import json
import zlib

import pytest

from clawshot.__main__ import main
from clawshot.generate import Settings, generate, spoiler_json
from test_generate import dungeon_world


def test_string_round_trip_preserves_complete_settings_and_seed_behavior():
    original = Settings(
        shuffle=("Chest", "NPC"),
        dungeon_items="anywhere",
        logic={"free_time_travel": True, "age_return_guarantee": False, "nested": {"b": [1, False], "a": "é"}},
        fast_start=("mido", "intro"),
        areas=("Village",),
        goal="Sword",
        item_location_types={"Sword": ("NPC", "Chest")},
        exclusive_location_types=("NPC",),
    )
    restored = Settings.from_string(original.to_string())
    assert restored == original
    assert restored.to_string() == original.to_string()
    # Exercise an actual fill, not just a serialization echo.
    first = Settings(dungeon_items="anywhere", fast_start=())
    second = Settings.from_string(first.to_string())
    assert spoiler_json(generate(dungeon_world(), 7, first)) == spoiler_json(generate(dungeon_world(), 7, second))


def test_semantically_unordered_inputs_have_one_string():
    a = Settings(shuffle=("Shop", "Chest", "Shop"), logic={"b": {"z": 0, "a": 1}, "a": False})
    b = Settings(shuffle=("Chest", "Shop"), logic={"a": False, "b": {"a": 1, "z": 0}})
    assert a.to_string() == b.to_string()


@pytest.mark.parametrize("text", ["", "CS2", "CS1.!", "CS1.e30"])
def test_bad_version_or_corrupt_string_is_refused(text):
    with pytest.raises(ValueError):
        Settings.from_string(text)


@pytest.mark.parametrize("payload", [[], {"unknown": True}, {"logic": []}, {"shuffle": "Chest"}, {"goal": 1}])
def test_invalid_decoded_contract_is_refused(payload):
    data = zlib.compress(json.dumps(payload).encode())
    text = "CS1." + base64.urlsafe_b64encode(data).decode().rstrip("=")
    with pytest.raises(ValueError):
        Settings.from_string(text)


def test_print_settings_needs_no_dump_and_explicit_options_override_string(capsys):
    start = Settings(shuffle=("Chest", "Gift"), logic={"free_time_travel": True}, fast_start=("intro", "saria"))
    assert (
        main(
            [
                "--settings",
                start.to_string(),
                "--skip",
                "--logic",
                "age_return_guarantee=false",
                "--dungeon-items",
                "anywhere",
                "--songs",
                "anywhere",
                "--shop-prices",
                "affordable",
                "--no-cheap-deku-shield",
                "--print-settings",
            ]
        )
        == 0
    )
    chosen = Settings.from_string(capsys.readouterr().out.strip())
    assert chosen.shuffle == ("Chest", "Gift")
    assert chosen.fast_start == ()
    assert chosen.dungeon_items == "anywhere"
    assert chosen.logic == {"free_time_travel": True, "age_return_guarantee": False}
    assert chosen.songs == "anywhere"
    assert chosen.shop_prices == "affordable"
    assert chosen.cheap_deku_shield is False
