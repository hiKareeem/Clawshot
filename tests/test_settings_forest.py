import pytest

from clawshot.__main__ import main
from clawshot.generate import FillError, Settings, prepare
from clawshot.world import CHILD, Search, load_spec


@pytest.mark.parametrize(
    "mode,exit_open,mido_open", [("closed", False, False), ("closed_deku", True, False), ("open", True, True)]
)
def test_forest_modes_match_both_independent_routes(mode, exit_open, mido_open):
    settings, world = prepare(load_spec(), Settings(forest=mode, fast_start=()))
    search = Search(world)
    assert world.settings["open_forest"] == mode
    assert search.can_reach("LW Bridge From Forest", CHILD) is exit_open
    assert search.can_reach("KF Outside Deku Tree", CHILD) is mido_open
    search.collect("Kokiri Sword")
    search.collect("Deku Shield")
    assert search.can_reach("KF Outside Deku Tree", CHILD)
    search.collect("Defeat Queen Gohma")
    assert search.can_reach("LW Bridge From Forest", CHILD)
    assert Settings.from_string(settings.to_string()) == settings


def test_old_mido_spelling_is_the_same_canonical_open_setting(capsys):
    assert Settings(fast_start=("intro", "mido")).to_string() == Settings(forest="open").to_string()
    assert main(["--skip", "mido", "--print-settings"]) == 0
    selected = Settings.from_string(capsys.readouterr().out.strip())
    assert selected.forest == "open" and selected.fast_start == ()
    with pytest.raises(SystemExit) as error:
        main(["--forest", "closed_deku", "--skip", "mido", "--print-settings"])
    assert error.value.code == 2


def test_explicit_forest_option_replaces_derived_spoiler_logic(capsys):
    old, _ = prepare(load_spec(), Settings(forest="open"))
    assert main(["--settings", old.to_string(), "--forest", "closed_deku", "--print-settings"]) == 0
    selected = Settings.from_string(capsys.readouterr().out.strip())
    _, world = prepare(load_spec(), selected)
    assert world.settings["open_forest"] == "closed_deku"
    assert world.settings["skip_mido"] is False


def test_forest_logic_cannot_claim_an_unpatched_mode():
    with pytest.raises(FillError):
        prepare(load_spec(), Settings(forest="closed", logic={"open_forest": "open"}))
    with pytest.raises(ValueError):
        Settings(forest="fast")
