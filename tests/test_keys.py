"""Unverified dungeon attribution cannot reach a real seed's output boundary."""

import pytest

from clawshot.__main__ import main
from clawshot.generate import Settings
from clawshot.patch import PatchError, make_seed


@pytest.mark.parametrize("shuffle", [("Chest",), ("Chest", "Gift")])
def test_anywhere_seed_pipeline_refuses_before_opening_the_dump(tmp_path, shuffle):
    with pytest.raises(PatchError, match="anywhere"):
        make_seed(tmp_path / "missing-romfs", 7, Settings(dungeon_items="anywhere", shuffle=shuffle))
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "options",
    [
        ["--dungeon-items", "anywhere"],
        ["--settings", Settings(dungeon_items="anywhere").to_string()],
        ["--settings", Settings(dungeon_items="anywhere", shuffle=("Chest", "Gift")).to_string()],
    ],
)
def test_cli_refuses_anywhere_before_reading_gifts_or_writing_output(tmp_path, capsys, options):
    out = tmp_path / "seed"
    assert main(["--romfs", str(tmp_path / "missing-romfs"), "--seed", "7", "--out", str(out), *options]) == 1
    error = capsys.readouterr().err
    assert "anywhere" in error and "in-game" in error
    assert not out.exists()


def test_anywhere_settings_remain_shareable_without_building_a_seed(capsys):
    assert main(["--dungeon-items", "anywhere", "--print-settings"]) == 0
    assert Settings.from_string(capsys.readouterr().out.strip()).dungeon_items == "anywhere"


def test_explicit_own_dungeon_overrides_a_replayed_anywhere_setting(capsys):
    encoded = Settings(dungeon_items="anywhere").to_string()
    assert main(["--settings", encoded, "--dungeon-items", "own_dungeon", "--print-settings"]) == 0
    assert Settings.from_string(capsys.readouterr().out.strip()).dungeon_items == "own_dungeon"
