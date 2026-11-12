"""Small-key settings remain shareable and explicit CLI overrides win."""

from clawshot.__main__ import main
from clawshot.generate import Settings


def test_anywhere_settings_remain_shareable_without_building_a_seed(capsys):
    assert main(["--dungeon-items", "anywhere", "--print-settings"]) == 0
    assert Settings.from_string(capsys.readouterr().out.strip()).dungeon_items == "anywhere"


def test_explicit_own_dungeon_overrides_a_replayed_anywhere_setting(capsys):
    encoded = Settings(dungeon_items="anywhere").to_string()
    assert main(["--settings", encoded, "--dungeon-items", "own_dungeon", "--print-settings"]) == 0
    assert Settings.from_string(capsys.readouterr().out.strip()).dungeon_items == "own_dungeon"
