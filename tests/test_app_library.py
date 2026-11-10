"""Persist and reopen invented seeds through the real HTTP server; never launch a game."""

import json
import os
import shutil
from pathlib import Path

import pytest
from test_app import app_source as app_source
from test_app import synthetic_run, synthetic_spec
from test_app_play import made_ui_seed as made_ui_seed
from test_ui import request, running_server

import clawshot.app.library as library_module
from clawshot.app import Jobs, play_plan
from clawshot.app.library import MANIFEST, SeedLibrary, inspect_seed
from clawshot.app.paths import SOURCE_ROOT
from clawshot.app.preferences import Preferences
from clawshot.ui.server import Application


@pytest.fixture(autouse=True)
def isolated_default_root(tmp_path, monkeypatch):
    monkeypatch.setattr(library_module, "default_output_root", lambda: tmp_path / "default-seeds")


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


def test_catalog_does_not_read_seed_contents_but_view_and_play_verify_them(made_ui_seed, tmp_path, monkeypatch):
    result, hookshot, _ = made_ui_seed
    root = Path(result["output"])
    original = (root / MANIFEST).read_bytes(), (root / MANIFEST).stat().st_mtime_ns
    (root / "seed/play-note.md").write_text("modified after generation")
    reads = []
    digest = library_module.tree_digest

    def counted_digest(path):
        reads.append(path)
        return digest(path)

    monkeypatch.setattr(library_module, "tree_digest", counted_digest)
    preferences = Preferences()
    preferences.remember_root(str(tmp_path))
    app = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=preferences)
    with running_server(app) as server:
        entry = next(row for row in request(server, "seeds")[2]["seeds"] if row["output"] == str(root))
        assert entry["playable"] is True and reads == []
        assert request(server, "select-seed", {"output": str(root)})[0] == 400
        assert reads == [root / "seed"]
        assert request(server, "job")[2]["status"] == "idle"
    with pytest.raises(ValueError):
        play_plan(entry, str(hookshot))
    assert original == ((root / MANIFEST).read_bytes(), (root / MANIFEST).stat().st_mtime_ns)


@pytest.mark.parametrize("legacy_layout", ["romfs", "seed/romfs"])
def test_catalog_filters_unrelated_folders_and_orders_newest_manifest_first(made_ui_seed, tmp_path, legacy_layout):
    result, _, _ = made_ui_seed
    newest = Path(result["output"])
    older = tmp_path / "aaa-older"
    shutil.copytree(newest, older)
    legacy = tmp_path / "legacy"
    (legacy / legacy_layout).mkdir(parents=True)
    (tmp_path / "holiday-pictures").mkdir()
    (tmp_path / "not-a-seed/seed").mkdir(parents=True)
    os.utime(newest / MANIFEST, ns=(2_000_000_000, 2_000_000_000))
    os.utime(older / MANIFEST, ns=(1_000_000_000, 1_000_000_000))
    preferences = Preferences()
    preferences.remember_root(str(tmp_path))
    entries = SeedLibrary(preferences).entries()
    assert [Path(row["output"]) for row in entries] == [newest, older, legacy]
    assert entries[-1]["playable"] is False


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
