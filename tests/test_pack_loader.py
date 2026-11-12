"""A pack loads only its verified seed, never caches, unrelated mods or vanilla."""

import json
import os
import sys
from pathlib import Path

import pytest

from clawshot.pack import PackError, runtime, tree_digest


@pytest.fixture
def made_pack(tmp_path, monkeypatch):
    root = tmp_path / "pack"
    resource = root / "seed/romfs/Banc/Synthetic.byml.zs"
    resource.parent.mkdir(parents=True)
    resource.write_bytes(b"invented placement")
    (root / "seed/play-note.md").write_text("synthetic route")
    game = tmp_path / "game"
    exe = game / "bin/hookshot.exe"
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"synthetic image\0HOS_MODS\0")
    (root / "pack.json").write_text(json.dumps({"format": 1, "seed": 8, "output_sha256": tree_digest(root / "seed")}))
    (root / "folders.json").write_text(json.dumps({"romfs": str(tmp_path / "dump"), "hookshot": str(game)}))
    monkeypatch.setattr(runtime, "check_version", lambda _: None)
    return root, exe


def hookshot_mods(root: Path, depth=0):
    """Independent facts-only oracle: v2.0.13 host/mods.c find_mods, depth <= 4."""
    if depth and any((root / name).exists() for name in ("romfs", "exefs")):
        return [root]
    if depth == 4:
        return []
    return [
        mod
        for child in sorted(root.iterdir())
        if child.is_dir() and child.name[0] not in ".-_"
        for mod in hookshot_mods(child, depth + 1)
    ]


def test_dry_play_isolated_single_mod_without_writes(made_pack, monkeypatch, capsys):
    root, exe = made_pack
    for folder in (".romfs-aborted/Pack", ".venv/romfs", "_disabled/romfs", "-disabled/exefs", "src/clawshot"):
        (root / folder).mkdir(parents=True)
    monkeypatch.setenv("HOS_FS_OVERLAY", "wrong overlay")
    monkeypatch.setenv("HOS_MODS", "unrelated mods")
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}
    assert runtime.main(["play", "--root", str(root), "--dry-run"]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["command"] == [str(exe), "--user", str(root / "user")]
    assert plan["environment"] == {"HOOKSHOT_NO_UPDATE_CHECK": "1", "HOS_MODS": str(root)}
    assert plan["unset_environment"] == ["HOS_FS_OVERLAY"]
    assert hookshot_mods(root) == [root / "seed"]
    assert plan["mod"] == str(root / "seed")
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}
    assert not (root / "user").exists()
    assert not (root / "hookshot_log.txt").exists()


@pytest.mark.parametrize("content", [b"old executable", b"mods: %s: %d RomFS files\0", b""])
def test_no_mod_support_refuses_before_user_or_log(made_pack, content):
    root, exe = made_pack
    exe.write_bytes(content)
    with pytest.raises(PackError, match="cannot load mods"):
        runtime.play(root)
    assert not (root / "user").exists()
    assert not (root / "hookshot_log.txt").exists()


@pytest.mark.parametrize("folder", ["other/romfs", "nested/title/extra/exefs", "user/romfs"])
def test_unrelated_mod_refuses_before_user_or_log(made_pack, folder):
    root, _ = made_pack
    (root / folder).mkdir(parents=True)
    with pytest.raises(PackError, match="exactly one mod"):
        runtime.play(root)
    assert not (root / "hookshot_log.txt").exists()


@pytest.mark.parametrize("target", ["seed", "seed/romfs", "src/linked"])
def test_linked_mod_paths_are_rejected(made_pack, tmp_path, target):
    root, _ = made_pack
    path = root / target
    if path.exists():
        path.rename(tmp_path / "original")
        destination = tmp_path / "original"
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        destination = tmp_path / "elsewhere"
        destination.mkdir()
    path.symlink_to(destination, target_is_directory=True)
    with pytest.raises(PackError, match="link"):
        runtime.play(root)
    assert not (root / "user").exists()
    assert not (root / "hookshot_log.txt").exists()


@pytest.mark.parametrize(
    "names, expected",
    [
        (["hookshot.exe"], True),
        (["HOOKSHOT.EXE", "other.exe"], True),
        (["HookshotBuilder.exe"], False),
        (["myhookshot.exe"], False),
        (["hookshot"], True),
        (["bash", "python3.12", "hookshot"], True),
        (["Hookshot", "hookshot-folder", "AppRun", "hookshot.bin"], False),
        ([], False),
    ],
)
def test_pc_wide_hookshot_name_detection_with_fake_lister(names, expected):
    assert runtime.hookshot_running(lambda: names) is expected


def test_global_running_game_refuses_before_saves_log_or_process(made_pack, monkeypatch):
    root, exe = made_pack
    plan = runtime.launch_plan(root, exe.parent.parent)
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}

    def forbidden(*args, **kwargs):
        raise AssertionError("No test may launch a game")

    monkeypatch.setattr(runtime.subprocess, "Popen", forbidden)
    with pytest.raises(PackError) as caught:
        runtime.start_game(plan, process_lister=lambda: ["hookshot.exe"])
    assert str(caught.value) == "Hookshot is already running. Quit it, then press Play."
    assert not (root / "user").exists() and not (root / "hookshot_log.txt").exists()
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}


@pytest.mark.skipif(sys.platform == "win32", reason="builds a synthetic /proc from symbolic links")
def test_linux_process_names_come_from_readable_exe_links(tmp_path):
    proc = tmp_path / "proc"
    links = {
        "101": "/games/Hookshot/bin/hookshot",
        "102": "/games/Rebuilt/bin/hookshot (deleted)",
        "103": "/usr/bin/bash",
    }
    for pid, target in links.items():
        (proc / pid).mkdir(parents=True)
        os.symlink(target, proc / pid / "exe")
    (proc / "104").mkdir()  # a kernel thread or another user's process: no readable link
    (proc / "self").mkdir()
    os.symlink("/games/Hookshot/bin/hookshot", proc / "self/exe")
    (proc / "uptime").write_text("not a process")
    names = runtime._linux_process_names(proc)
    assert names == ("hookshot", "hookshot", "bash")
    assert runtime.hookshot_running(lambda: names)
    assert not runtime.hookshot_running(lambda: runtime._linux_process_names(proc / "104"))


def test_play_is_refused_where_it_cannot_start_the_folders_game():
    assert runtime.play_refusal(platform="win32") == ""
    assert runtime.play_refusal(platform="linux") == ""
    assert runtime.play_refusal(platform="darwin") == runtime.NO_PLAY
    assert runtime.play_refusal("C:/Games/Hookshot/bin/hookshot.exe", "win32") == ""
    assert runtime.play_refusal("/games/Hookshot/bin/hookshot", "linux") == ""
    assert runtime.play_refusal("/mnt/windows/Hookshot/bin/hookshot.exe", "linux") == runtime.OTHER_SYSTEM
    assert runtime.play_refusal("C:/Games/Hookshot/bin/hookshot", "win32") == runtime.OTHER_SYSTEM
    assert runtime.play_refusal("/games/Hookshot/bin/hookshot", "darwin") == runtime.NO_PLAY


def pack_with_game(tmp_path, game):
    root = tmp_path / "pack"
    resource = root / "seed/romfs/Banc/Synthetic.byml.zs"
    resource.parent.mkdir(parents=True)
    resource.write_bytes(b"invented placement")
    exe = tmp_path / "game" / game
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"synthetic image\0HOS_MODS\0")
    return root, exe


@pytest.mark.parametrize(
    "platform, game, refusal",
    [
        ("linux", "bin/hookshot.exe", runtime.OTHER_SYSTEM),
        ("win32", "bin/hookshot", runtime.OTHER_SYSTEM),
        ("darwin", "bin/hookshot", runtime.NO_PLAY),
    ],
)
def test_unstartable_game_refuses_before_saves_log_or_process(tmp_path, monkeypatch, platform, game, refusal):
    root, exe = pack_with_game(tmp_path, game)
    plan = runtime.launch_plan(root, exe.parent.parent)
    monkeypatch.setattr("clawshot.pack.hookshot.sys.platform", platform)

    def forbidden(*args, **kwargs):
        raise AssertionError("No test may launch a game")

    monkeypatch.setattr(runtime.subprocess, "Popen", forbidden)
    with pytest.raises(PackError) as caught:
        runtime.start_game(plan, process_lister=lambda: [])
    assert str(caught.value) == refusal
    assert not (root / "user").exists() and not (root / "hookshot_log.txt").exists()


@pytest.mark.parametrize("platform, game", [("win32", "bin/hookshot.exe"), ("linux", "bin/hookshot")])
def test_native_start_hands_the_checked_plan_to_one_process(tmp_path, monkeypatch, platform, game):
    root, exe = pack_with_game(tmp_path, game)
    plan = runtime.launch_plan(root, exe.parent.parent)
    assert plan["command"] == [str(exe), "--user", str(root / "user")]
    monkeypatch.setattr("clawshot.pack.hookshot.sys.platform", platform)
    monkeypatch.setenv("HOS_FS_OVERLAY", "inherited overlay")
    monkeypatch.setenv("HOS_MODS", "inherited mods")
    started = []

    def recorded(command, **options):
        started.append((command, options["cwd"], dict(options["env"]), options["stderr"].name))
        return "synthetic process"

    monkeypatch.setattr(runtime.subprocess, "Popen", recorded)
    assert runtime.start_game(plan, process_lister=lambda: []) == "synthetic process"
    ((command, cwd, env, log),) = started
    assert command == plan["command"] and cwd == str(exe.parent.parent)
    assert env["HOS_MODS"] == str(root) and env["HOOKSHOT_NO_UPDATE_CHECK"] == "1" and "HOS_FS_OVERLAY" not in env
    assert log == str(root / "hookshot_log.txt") and (root / "user").is_dir()
    assert exe.read_bytes() == b"synthetic image\0HOS_MODS\0"
