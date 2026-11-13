"""Public native seeds cannot claim unimplemented access modes."""

import json

import pytest

from clawshot.__main__ import main
from clawshot.app.schema import validate
from clawshot.generate import Settings, prepare
from clawshot.patch import make_seed
from clawshot.settings import validate_logic_overrides
from clawshot.world import load_spec

SPEC = load_spec()
DEFAULT_LOGIC = {**SPEC.get("settings", {}), **SPEC.get("tricks", {}), **SPEC.get("flags", {})}
SUPPORTED_BOOLEAN_KEYS = {"free_time_travel", "age_return_guarantee", "keysanity", "skip_mido"}
UNPAIRED = [
    (name, not value)
    for name, value in sorted(DEFAULT_LOGIC.items())
    if type(value) is bool and name not in SUPPORTED_BOOLEAN_KEYS
] + [
    ("open_kakariko", "open"),
    ("gerudo_fortress", "open"),
    ("gerudo_fortress", "fast"),
    ("scarecrow_behavior", "free"),
    ("starting_age", "adult"),
    ("starting_tod", "midnight"),
    ("open_door_of_time", "open"),
    ("future_oot_access_mode", True),
]


@pytest.mark.parametrize("name,value", UNPAIRED)
@pytest.mark.parametrize("entrypoint", ["cli", "settings_string", "app", "native_seed"])
def test_unpaired_access_override_is_refused_at_every_native_boundary(name, value, entrypoint, capsys, tmp_path):
    logic = {name: value}
    if entrypoint in ("cli", "settings_string"):
        args = (
            ["--logic", f"{name}={json.dumps(value)}"]
            if entrypoint == "cli"
            else ["--settings", Settings(logic=logic).to_string()]
        )
        with pytest.raises(SystemExit) as error:
            main([*args, "--print-settings"])
        assert error.value.code == 2
        message = capsys.readouterr().err
    else:
        with pytest.raises(ValueError) as error:
            if entrypoint == "app":
                validate({"logic": logic})
            else:
                # Refusal must precede opening a dump or attempting generation.
                make_seed(tmp_path / "not-a-dump", 1, Settings(logic=logic))
        message = str(error.value)
    assert name in message
    assert "isn't supported in the remake yet" in message
    assert "no game change" in message


@pytest.mark.parametrize(
    "values,name,expected",
    [
        ({"logic": {"free_time_travel": True}}, "free_time_travel", True),
        ({"logic": {"age_return_guarantee": False}}, "age_return_guarantee", False),
        ({"dungeon_items": "anywhere", "logic": {"keysanity": True}}, "keysanity", True),
        ({"forest": "closed_deku", "logic": {"open_forest": "closed_deku"}}, "open_forest", "closed_deku"),
        ({"forest": "open", "logic": {"open_forest": "open"}}, "open_forest", "open"),
        ({"forest": "open", "logic": {"skip_mido": True}}, "skip_mido", True),
        (
            {"door_of_time": "song_only", "logic": {"door_of_time": "song_only", "free_time_travel": True}},
            "door_of_time",
            "song_only",
        ),
        (
            {"door_of_time": "open", "logic": {"door_of_time": "open", "free_time_travel": True}},
            "door_of_time",
            "open",
        ),
    ],
)
def test_supported_access_modes_still_compile_to_the_selected_world(values, name, expected):
    selected = validate(values)
    _, world = prepare(load_spec(), selected)
    assert world.settings[name] == expected


@pytest.mark.parametrize("mode", ["closed", "song_only", "open"])
def test_effective_door_recipe_replays_its_native_return_kit(mode):
    effective, first = prepare(load_spec(), Settings(door_of_time=mode, logic={"free_time_travel": True}))
    selected = validate(text=effective.to_string())
    _, replay = prepare(load_spec(), selected)
    assert replay.settings["age_return_fill_inventory"] == first.settings["age_return_fill_inventory"]
    assert replay.settings["age_return_fill_families"] == first.settings["age_return_fill_families"]


def test_unchanged_world_defaults_remain_valid_even_when_explicit():
    selected = validate({"logic": DEFAULT_LOGIC})
    _, explicit = prepare(load_spec(), selected)
    _, ordinary = prepare(load_spec(), Settings())
    assert explicit.settings == ordinary.settings


def test_new_imported_oot_key_is_not_implicitly_supported():
    spec = load_spec()
    spec["settings"]["future_oot_access_mode"] = False
    with pytest.raises(ValueError, match="future_oot_access_mode"):
        validate({"logic": {"future_oot_access_mode": True}}, spec=spec)


@pytest.mark.parametrize("logic", [{"free_time_travel": 1}, {"keysanity": 1}, {"skip_mido": 0}])
def test_integer_values_do_not_impersonate_supported_booleans(logic):
    with pytest.raises(ValueError, match="isn't supported"):
        validate_logic_overrides(load_spec(), logic)
