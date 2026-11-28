"""The setting ``event_item_models`` (spec event-items 3.1, D7; plan 11.1, 11.4)."""

import tomllib
from pathlib import Path

import pytest

from clawshot.__main__ import main
from clawshot.generate import Settings
from clawshot.settings import DEFAULTS

ROOT = Path(__file__).resolve().parents[1]


def test_it_is_on_by_default_and_the_default_keeps_the_bare_settings_string():
    assert DEFAULTS["event_item_models"] is True
    assert Settings().event_item_models is True
    assert Settings().to_string() == "CS1"
    assert "event_item_models" not in Settings().as_dict()  # absent when on: existing strings and logs keep their bytes


def test_off_round_trips_through_the_settings_string():
    off = Settings(event_item_models=False)
    assert off.as_dict()["event_item_models"] is False
    assert Settings.from_string(off.to_string()).event_item_models is False


def test_a_value_that_is_no_boolean_is_refused():
    with pytest.raises(ValueError, match="event_item_models"):
        Settings(event_item_models="yes")


def test_the_command_line_turns_it_off(capsys):
    assert main(["--no-event-item-models", "--print-settings"]) == 0
    assert Settings.from_string(capsys.readouterr().out.strip()).event_item_models is False


def test_the_app_shows_it_with_its_label_and_help():
    entry = tomllib.loads((ROOT / "src/clawshot/app/settings.toml").read_text(encoding="utf-8"))["event_item_models"]
    assert entry["label"] == "Show shuffled items in events"
    assert entry["kind"] == "boolean"
    assert "Saria" in entry["help"] and "played" in entry["help"].lower()


def test_the_settings_doc_names_it():
    assert "event_item_models" in (ROOT / "docs/settings.md").read_text(encoding="utf-8")
