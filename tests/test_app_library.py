"""Persist and reopen invented seeds through the real HTTP server; never launch a game."""

import json
import shutil
from pathlib import Path

import pytest
from test_app import app_source as app_source
from test_app import synthetic_run, synthetic_spec
from test_app_play import made_ui_seed as made_ui_seed
from test_ui import request, running_server

from clawshot.app import Jobs, play_plan
from clawshot.app.library import MANIFEST, SeedLibrary, inspect_seed
from clawshot.app.paths import SOURCE_ROOT
from clawshot.app.preferences import Preferences
from clawshot.ui.server import Application


def test_saved_seed_reopens_after_server_restart_without_original_files(made_ui_seed, tmp_path):
    result, hookshot, source = made_ui_seed
    root = Path(result["output"])
    config = tmp_path / "config/paths.json"
    first = Application(
        Jobs(synthetic_run), spec=synthetic_spec(), preferences=Preferences(config), chooser=lambda _: root
    )
    with running_server(first) as server:
        assert request(server, "browse", {"kind": "seeds"})[0] == 200
        before = next(row for row in request(server, "seeds")[2]["seeds"] if row["output"] == str(root))
        assert before["playable"]
    shutil.rmtree(source)
    second = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=Preferences(config))
    with running_server(second) as server:
        entry = next(row for row in request(server, "seeds")[2]["seeds"] if row["output"] == str(root))
        assert entry["playable"] and entry["output_sha256"] == before["output_sha256"]
        status, _, selected = request(server, "select-seed", {"output": str(root)})
        assert status == 200 and selected["status"] == "loaded"
        assert selected["result"]["seed"] == 7 and selected["stages"] == []
        assert request(server, "result", {"file": "note", "output": str(root)})[0] == 200
        assert request(server, "result", {"file": "spoiler", "output": str(root)})[0] == 400
        spoiler = request(server, "result", {"file": "spoiler", "output": str(root), "confirmed": True})[2]
        assert json.loads(spoiler["text"])["seed"] == 7
        assert request(server, "play", {"hookshot": str(hookshot), "output": str(root)})[0] == 400  # headless
        assert request(server, "select-seed", {"output": None})[2]["status"] == "idle"
    plan = play_plan(entry, str(hookshot))
    assert plan["command"] == [str(hookshot / "bin/hookshot.exe"), "--user", str(root / "user")]
    assert not (root / "user").exists() and not (root / "hookshot_log.txt").exists()


def test_missing_manifest_and_changed_files_are_listed_but_cannot_be_selected(made_ui_seed, tmp_path):
    result, _, _ = made_ui_seed
    root = Path(result["output"])
    missing = tmp_path / "missing-info"
    (missing / "seed/romfs").mkdir(parents=True)
    original = (root / MANIFEST).read_bytes(), (root / MANIFEST).stat().st_mtime_ns
    (root / "seed/play-note.md").write_text("modified after generation")
    preferences = Preferences()
    preferences.remember_root(str(tmp_path))
    app = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=preferences)
    with running_server(app) as server:
        entries = {row["output"]: row for row in request(server, "seeds")[2]["seeds"]}
        assert entries[str(root)]["playable"] is False
        assert entries[str(missing)]["playable"] is False
        for folder in (root, missing):
            assert request(server, "select-seed", {"output": str(folder)})[0] == 400
        assert request(server, "job")[2]["status"] == "idle"
    assert original == ((root / MANIFEST).read_bytes(), (root / MANIFEST).stat().st_mtime_ns)
    assert (root / "seed/play-note.md").read_text() == "modified after generation"


def test_result_documents_cannot_escape_registered_seed_folders(made_ui_seed, tmp_path):
    result, _, _ = made_ui_seed
    root = Path(result["output"])
    foreign = tmp_path / "not-registered"
    (foreign / "seed").mkdir(parents=True)
    (foreign / "seed/play-note.md").write_text("must not be served")
    preferences = Preferences()
    preferences.remember_root(str(root))
    app = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=preferences)
    with running_server(app) as server:
        assert request(server, "result", {"file": "note", "output": str(foreign)})[0] == 400
        assert request(server, "select-seed", {"output": str(foreign)})[0] == 400
        assert request(server, "result", {"file": "note", "output": str(root)})[0] == 200


@pytest.mark.parametrize("field", ["output", "playable", "note_available", "name"])
def test_manifest_cannot_override_catalog_authority(made_ui_seed, tmp_path, field):
    result, _, _ = made_ui_seed
    root = Path(result["output"])
    record = json.loads((root / MANIFEST).read_text())
    record[field] = str(tmp_path / "elsewhere") if field in ("output", "name") else True
    (root / MANIFEST).write_text(json.dumps(record))
    entry = inspect_seed(root)
    assert entry["playable"] is False and entry["output"] == str(root)
    preferences = Preferences()
    preferences.remember_root(str(root))
    assert SeedLibrary(preferences).get(str(root))["playable"] is False


def test_path_preferences_never_use_the_source_checkout():
    path = SOURCE_ROOT / "never-write-config-test.json"
    before = path.exists()
    with pytest.raises(ValueError):
        Preferences(path)
    assert path.exists() == before
