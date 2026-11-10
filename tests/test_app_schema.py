"""Settings metadata is a checked contract, not a second set of generator defaults."""

from dataclasses import make_dataclass
from importlib import import_module

import pytest

from clawshot.app import schema, settings_payload, validate
from clawshot.generate import Settings
from clawshot.patch.gifts import GIFT_TYPES

schema_module = import_module("clawshot.app.schema")


def test_new_setting_without_metadata_refuses_schema(monkeypatch):
    expanded = make_dataclass("ExpandedSettings", [("future_setting", bool, False)], bases=(Settings,), frozen=True)
    monkeypatch.setattr(schema_module, "Settings", expanded)
    with pytest.raises(ValueError):
        schema()


@pytest.mark.parametrize("section, key", [("shuffle", "help"), ("shuffle.choice_help", "Chest")])
def test_missing_setting_or_choice_help_refuses_schema(tmp_path, monkeypatch, section, key):
    original = schema_module.METADATA_PATH.read_text(encoding="utf-8")
    current = ""
    lines = []
    for line in original.splitlines():
        if line.startswith("["):
            current = line.strip("[]")
        if current == section and line.startswith(key + " ="):
            continue
        lines.append(line)
    path = tmp_path / "settings.toml"
    path.write_text("\n".join(lines), encoding="utf-8")
    monkeypatch.setattr(schema_module, "METADATA_PATH", path)
    with pytest.raises(ValueError):
        schema()


def test_effective_gift_string_can_be_loaded_back_into_player_controls():
    effective = Settings(shuffle=("Chest", *GIFT_TYPES))
    restored = validate(text=effective.to_string())
    assert restored.shuffle == ("Chest", "Gift")
    assert validate(text=restored.to_string()) == restored


def test_inactive_prices_keep_their_values_and_activate_only_with_their_check_kind():
    inactive = Settings(shuffle=("Chest",), shop_prices="affordable", scrub_prices="fixed", scrub_price=75)
    payload = settings_payload(inactive)
    assert {"shop_slots", "shop_prices", "scrub_prices", "scrub_price"} <= payload["inactive"].keys()
    assert "cheap_deku_shield" not in payload["inactive"]  # independent price patch even without Shop
    replay = Settings.from_string(payload["settings_string"])
    assert replay.scrub_price == 75 and replay.shop_prices == "affordable"
    active = Settings(**(payload["values"] | {"shuffle": ["Chest", "Shop", "Scrub"]}))
    assert (
        not {"shop_slots", "shop_prices", "scrub_prices", "scrub_price"} & settings_payload(active)["inactive"].keys()
    )
    assert active.scrub_price == 75


def test_fixed_fee_and_zero_shop_shelves_explain_why_prices_have_no_effect():
    selected = Settings(shuffle=("Chest", "Shop", "Scrub"), shop_slots=0, scrub_prices="vanilla")
    inactive = settings_payload(selected)["inactive"]
    assert {"shop_prices", "scrub_price"} <= inactive.keys()
    assert not {"shop_slots", "scrub_prices"} & inactive.keys()
