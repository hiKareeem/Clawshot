"""Real synthetic generation and read-only launch plans; never start a game or dialog."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from test_app import app_source as app_source
from test_app import synthetic_run, wait_job
from test_pack_loader import hookshot_mods

from clawshot.app import GenerationRequest, Jobs, detect_dump, detect_hookshot, play_plan
from clawshot.app.library import MANIFEST
from clawshot.app.paths import absolute_path, output_path
from clawshot.pack import VERSION_FILES, version_digest


@pytest.fixture
def made_ui_seed(app_source, tmp_path, monkeypatch):
    for relative in VERSION_FILES:
        path = app_source / relative
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"invented fingerprint input: " + relative.encode())
    monkeypatch.setattr("clawshot.pack.ROMFS_SHA256", version_digest(app_source))
    jobs = Jobs(synthetic_run)
    try:
        jobs.start(GenerationRequest(str(app_source), str(tmp_path / "made"), 7, "CS1"))
        state = wait_job(jobs)
        assert state["status"] == "succeeded", state
    finally:
        jobs.close()
    hookshot = tmp_path / "hookshot"
    exe = hookshot / "bin/hookshot.exe"
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"synthetic non-executable HOS_MODS\0")
    return state["result"], hookshot, app_source


def files_under(root):
    return {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}


def test_ui_plan_has_one_mod_private_saves_and_unsets_overlay(made_ui_seed, tmp_path, monkeypatch):
    result, hookshot, _ = made_ui_seed
    root = Path(result["output"])
    before = files_under(tmp_path)
    monkeypatch.setenv("HOS_FS_OVERLAY", "another-overlay")
    monkeypatch.setenv("HOS_MODS", "another-mods-root")
    plan = play_plan(result, str(hookshot))
    assert plan["command"] == [str(hookshot / "bin/hookshot.exe"), "--user", str(root / "user")]
    assert plan["environment"] == {"HOOKSHOT_NO_UPDATE_CHECK": "1", "HOS_MODS": str(root)}
    assert plan["unset_environment"] == ["HOS_FS_OVERLAY"]
    assert hookshot_mods(Path(plan["environment"]["HOS_MODS"])) == [root / "seed"]
    assert plan["log"] == str(root / "hookshot_log.txt")
    assert not (root / "user").exists() and not (root / "hookshot_log.txt").exists()
    assert files_under(tmp_path) == before
    assert os.environ["HOS_FS_OVERLAY"] == "another-overlay"


@pytest.mark.parametrize("damage", ["seed", "extra-mod", "user-link", "log-link", "missing-manifest", "wrong-build"])
def test_ui_refuses_changed_or_unsafe_seed_without_touching_saves(made_ui_seed, tmp_path, damage):
    result, hookshot, _ = made_ui_seed
    root = Path(result["output"])
    outside = tmp_path / "normal-saves"
    outside.mkdir()
    marker = outside / "keep.sav"
    marker.write_bytes(b"player's normal save")
    if damage == "seed":
        (root / "seed/play-note.md").write_text("changed after generation")
    elif damage == "extra-mod":
        (root / "another/romfs").mkdir(parents=True)
    elif damage == "user-link":
        (root / "user").symlink_to(outside, target_is_directory=True)
    elif damage == "log-link":
        (root / "hookshot_log.txt").symlink_to(marker)
    elif damage == "missing-manifest":
        (root / MANIFEST).unlink()
    else:
        manifest = json.loads((root / MANIFEST).read_text())
        manifest["game_build"] = "a different game update"
        (root / MANIFEST).write_text(json.dumps(manifest))
    before = marker.read_bytes(), marker.stat().st_mtime_ns
    with pytest.raises(ValueError):
        play_plan(result, str(hookshot))
    assert before == (marker.read_bytes(), marker.stat().st_mtime_ns)
    assert not (root / "hookshot_log.txt").exists() or (root / "hookshot_log.txt").is_symlink()


@pytest.mark.parametrize(
    "kind", ["symlink", pytest.param("junction", marks=pytest.mark.skipif(os.name != "nt", reason="Windows junction"))]
)
def test_read_only_inputs_resolve_links_but_outputs_refuse_them(made_ui_seed, tmp_path, kind):
    result, hookshot, source = made_ui_seed
    aliases = []
    for name, target in (("dump-alias", source), ("game-alias", hookshot)):
        link = tmp_path / name
        if kind == "junction":
            subprocess.run(
                ["cmd.exe", "/c", "mklink", "/J", str(link), str(target)],
                check=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        else:
            link.symlink_to(target, target_is_directory=True)
        aliases.append(link)
    dump_alias, game_alias = aliases
    before = files_under(source)
    assert Path(detect_dump(str(dump_alias))["path"]) == source
    assert Path(detect_hookshot(str(game_alias))["folder"]) == hookshot
    request = GenerationRequest(str(dump_alias), str(tmp_path / "fresh"), 8, "CS1", str(game_alias))
    assert request.paths()[0] == source
    with pytest.raises(ValueError):
        output_path(str(dump_alias / "new-output"), source)
    assert before == files_under(source)
    assert not (source / "new-output").exists()


def test_looping_read_only_link_is_a_path_error(tmp_path):
    loop = tmp_path / "loop"
    loop.symlink_to(loop.name, target_is_directory=True)
    with pytest.raises(ValueError):
        absolute_path(str(loop), "Game files", allow_links=True)
    assert loop.is_symlink()


@pytest.mark.parametrize("change", ["moved", "deleted"])
def test_saved_seed_plan_does_not_need_the_original_game_files(made_ui_seed, tmp_path, change):
    result, hookshot, source = made_ui_seed
    if change == "moved":
        source.rename(tmp_path / "moved-original")
    else:
        shutil.rmtree(source)
    plan = play_plan(result, str(hookshot))
    root = Path(result["output"])
    assert plan["mod"] == str(root / "seed")
    assert plan["command"] == [str(hookshot / "bin/hookshot.exe"), "--user", str(root / "user")]
    assert not (root / "user").exists() and not (root / "hookshot_log.txt").exists()
