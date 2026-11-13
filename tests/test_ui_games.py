"""HTTP game switching uses real detection and verified plans, never starts a game."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_app import app_source as app_source
from test_app import synthetic_run, synthetic_spec
from test_app_play import made_ui_seed as made_ui_seed
from test_ui import request, running_server

from clawshot.app import Jobs
from clawshot.app.preferences import Preferences
from clawshot.pack.runtime import prepare_user
from clawshot.ui.server import Application


@pytest.mark.parametrize("binary", ["longshot.exe", "longshot"])
def test_http_migrates_game_selection_switches_and_rejects_changed_seed(made_ui_seed, tmp_path, monkeypatch, binary):
    result, hookshot, _ = made_ui_seed
    launcher = tmp_path / "LongshotLauncher"
    build = launcher / "LongshotLauncher-data/builds/v3.0.0-rc.2"
    exe = build / "bin" / binary
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"synthetic, not executable: HOS_MODS\0")
    (build / "longshot_version.txt").write_text("version=v3.0.0-rc.2\n", encoding="utf-8")
    newer = build.parent / "v3.1.0"
    (newer / "bin").mkdir(parents=True)
    (newer / "bin" / binary).write_bytes(b"synthetic newer HOS_MODS\0")
    (newer / "longshot_version.txt").write_text("version=v3.1.0\n", encoding="utf-8")
    (build.parents[1] / "builds.json").write_text(
        json.dumps({"format": 1, "builds": [{"folder": str(build), "version": "v3.0.0-rc.2", "default": True}]}),
        encoding="utf-8",
    )
    config = tmp_path / "paths.json"
    config.write_text(json.dumps({"hookshot": str(hookshot)}), encoding="utf-8")
    preferences = Preferences(config)
    preferences.remember_root(result["output"])
    app = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=preferences, allow_play=True)
    plans = []

    def inspect_only(plan):
        plans.append(plan)
        return SimpleNamespace(poll=lambda: 0), prepare_user(plan)

    monkeypatch.setattr("clawshot.app.play.start_game", inspect_only)
    with running_server(app) as server:
        saved = request(server, "schema")[2]["paths"]
        assert saved["game"] == str(hookshot) and "hookshot" not in saved
        status, _, detected = request(server, "detect", {"game": str(launcher)})
        assert status == 200, detected
        assert detected["game"]["game"] == "Longshot"
        assert detected["game"]["version"] == "v3.0.0-rc.2"
        assert Path(detected["game"]["folder"]) == build
        assert request(server, "schema")[2]["paths"]["game"] == str(launcher)
        assert request(server, "select-seed", {"output": result["output"]})[0] == 200
        status, _, played = request(server, "play", {"game": str(launcher)})
        assert status == 200, played
        assert played["options"]["missing"] == ["option.sav", "account.sav"]
        plan = plans[-1]
        root = Path(result["output"])
        assert plan["command"] == [str(exe), "--user", str(root / "user")]
        assert plan["cwd"] == str(build)
        assert plan["environment"] == {"LONGSHOT_NO_UPDATE_CHECK": "1", "HOS_MODS": str(root)}
        assert plan["unset_environment"] == ["HOS_FS_OVERLAY"]
        assert plan["log"] == str(root / "longshot_log.txt")
        assert request(server, "detect", {"game": str(hookshot)})[2]["game"]["game"] == "Hookshot"
        assert request(server, "play", {"game": str(hookshot)})[0] == 200
        assert plans[-1]["environment"] == {"HOOKSHOT_NO_UPDATE_CHECK": "1", "HOS_MODS": str(root)}
        assert plans[-1]["user"] == plan["user"]
        (root / "seed/play-note.md").write_text("changed", encoding="utf-8")
        assert request(server, "play", {"game": str(launcher)})[0] == 400
        assert len(plans) == 2
        assert (root / "user").is_dir() and not list((root / "user").iterdir())
        assert not (root / "longshot_log.txt").exists()
    assert Preferences(config).snapshot()["game"] == str(hookshot)
