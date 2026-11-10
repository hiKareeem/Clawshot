"""Real-folder export of invented seed files; no emulator, game, or native picker."""

from pathlib import Path

import pytest
from test_app import app_source as app_source
from test_app import synthetic_run, synthetic_spec
from test_app_play import made_ui_seed as made_ui_seed
from test_ui import request, running_server

from clawshot.app import Jobs
from clawshot.app.emulator import copy_to_emulator
from clawshot.app.preferences import Preferences, suggested_eden_folder
from clawshot.ui.server import Application


def test_emulator_folder_is_remembered_and_copy_is_exclusive_and_independent(made_ui_seed, tmp_path):
    result, _, _ = made_ui_seed
    root = Path(result["output"])
    mods = tmp_path / "emulator/mods"
    mods.mkdir(parents=True)
    save = tmp_path / "emulator/main.sav"
    save.write_bytes(b"normal player save")
    config = tmp_path / "preferences/paths.json"
    first = Application(
        Jobs(synthetic_run), spec=synthetic_spec(), preferences=Preferences(config), chooser=lambda _: mods
    )
    first.library.add_folder(str(root))
    with running_server(first) as server:
        assert request(server, "browse", {"kind": "emulator_mods"})[0] == 200
        assert request(server, "copy-emulator", {"output": str(root)})[0] == 400
        assert not (mods / "Clawshot-seed-7").exists()

    def no_new_picker(_):
        raise AssertionError("remembered copying must not reopen the picker")

    second = Application(
        Jobs(synthetic_run), spec=synthetic_spec(), preferences=Preferences(config), chooser=no_new_picker
    )
    with running_server(second) as server:
        status, _, copied = request(server, "copy-emulator", {"output": str(root), "confirmed": True})
        assert status == 200
        destination = Path(copied["path"])
        assert destination == mods / "Clawshot-seed-7"
        source_files = {
            p.relative_to(root / "seed/romfs"): p.read_bytes() for p in (root / "seed/romfs").rglob("*") if p.is_file()
        }
        actual = {
            p.relative_to(destination / "romfs"): p.read_bytes()
            for p in (destination / "romfs").rglob("*")
            if p.is_file()
        }
        assert actual == source_files
        assert all(not p.is_symlink() and not p.is_junction() for p in destination.rglob("*"))
        sample = next((destination / "romfs").rglob("*.zs"))
        original = (root / "seed/romfs" / sample.relative_to(destination / "romfs")).read_bytes()
        sample.write_bytes(b"emulator-side modification")
        assert (root / "seed/romfs" / sample.relative_to(destination / "romfs")).read_bytes() == original
        assert request(server, "copy-emulator", {"output": str(root), "confirmed": True})[0] == 400
        assert sample.read_bytes() == b"emulator-side modification"
    assert save.read_bytes() == b"normal player save"


def test_emulator_copy_refuses_changed_seed_and_headless_export(made_ui_seed, tmp_path):
    result, _, _ = made_ui_seed
    root = Path(result["output"])
    mods = tmp_path / "mods"
    mods.mkdir()
    (root / "seed/play-note.md").write_text("changed")
    with pytest.raises(ValueError):
        copy_to_emulator(result, str(mods))
    assert not (mods / "Clawshot-seed-7").exists()
    preferences = Preferences()
    preferences.remember("emulator_mods", str(mods))
    app = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=preferences)
    app.library.add_folder(str(root))
    with running_server(app) as server:
        assert request(server, "copy-emulator", {"output": str(root), "confirmed": True})[0] == 400


def test_emulator_copy_refuses_linked_and_protected_destinations(made_ui_seed, tmp_path):
    result, _, source = made_ui_seed
    mods = tmp_path / "mods"
    mods.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(mods, target_is_directory=True)
    with pytest.raises(ValueError):
        copy_to_emulator(result, str(alias))
    with pytest.raises(ValueError):
        copy_to_emulator(result, str(source), protected=(source,))
    assert not (mods / "Clawshot-seed-7").exists()
    assert not (source / "Clawshot-seed-7").exists()


def test_eden_suggestion_requires_an_existing_game_folder(tmp_path, monkeypatch):
    monkeypatch.setattr("clawshot.app.preferences.sys.platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert suggested_eden_folder() is None
    expected = tmp_path / "eden/load/0400486024DEC000"
    expected.mkdir(parents=True)
    assert suggested_eden_folder() == str(expected)
