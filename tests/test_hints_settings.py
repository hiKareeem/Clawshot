"""The hint settings travel in the settings string and the CLI (round 7)."""

import pytest

from clawshot.__main__ import main
from clawshot.generate import Settings


def test_defaults_keep_the_bare_string_and_choices_round_trip():
    assert Settings().to_string() == "CS1"
    assert (Settings().hints, Settings().hint_distribution) == ("always", "balanced")
    chosen = Settings(hints="mask", hint_distribution="strong")
    back = Settings.from_string(chosen.to_string())
    assert (back.hints, back.hint_distribution) == ("mask", "strong")
    assert back == chosen


@pytest.mark.parametrize("field", [{"hints": "agony"}, {"hint_distribution": "tournament"}])
def test_unknown_hint_choices_are_refused(field):
    with pytest.raises(ValueError, match="hint"):
        Settings(**field)


def test_cli_options_override_the_string(capsys):
    base = Settings(hints="mask", hint_distribution="useless").to_string()
    assert main(["--settings", base, "--hints", "always", "--print-settings"]) == 0
    printed = Settings.from_string(capsys.readouterr().out.strip())
    assert (printed.hints, printed.hint_distribution) == ("always", "useless")
