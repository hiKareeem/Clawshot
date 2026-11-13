"""Read-only Hookshot and Longshot installation facts and fail-closed Play capability; never start a game."""

import json

import pytest

from clawshot.pack.hookshot import detect, game_binary, game_folders, native_suffix, version_key

GAMES = [("Hookshot", "hookshot"), ("Longshot", "longshot")]


def snapshot(root):
    return {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}


def make_build(folder, version=None, binary="bin/longshot.exe", marker=True):
    exe = folder / binary
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"synthetic image\0HOS_MODS\0" if marker else b"synthetic image without the marker\0")
    if version is not None:
        program = binary.removeprefix("bin/").removesuffix(".exe")
        (folder / f"{program}_version.txt").write_text(f"version={version}\nbuilder=synthetic\n", encoding="utf-8")
    return exe


def write_registry(data, *builds):
    data.mkdir(parents=True, exist_ok=True)
    rows = [{"id": str(n), "folder": str(folder), "version": version} for n, (folder, version) in enumerate(builds)]
    (data / "builds.json").write_text(json.dumps({"format": 1, "builds": rows}), encoding="utf-8")


@pytest.mark.parametrize("game, program", GAMES)
@pytest.mark.parametrize("version", [None, "v2.0.13\n", "version=v3.0.0-rc.2\nbuilder=synthetic.exe\n", "v99.0.0\n"])
@pytest.mark.parametrize("supports", [False, True])
def test_binary_capability_not_version_label(tmp_path, game, program, version, supports):
    exe = tmp_path / f"bin/{program}.exe"
    exe.parent.mkdir()
    exe.write_bytes(b"HOS_MODS\0" if supports else b"mods: %s: %d RomFS files\0")
    if version is not None:
        (tmp_path / f"{program}_version.txt").write_text(version, encoding="utf-8-sig")
    (tmp_path / "romfs").mkdir()
    (tmp_path / "game.nup").write_bytes(b"not decoded")
    (tmp_path / "other.NUP").write_bytes(b"not decoded either")
    (tmp_path / "directory.nup").mkdir()
    before = snapshot(tmp_path)
    result = detect(str(tmp_path))
    assert result.game == game
    assert result.selected_folder == result.folder == tmp_path and result.launcher is None
    assert result.exe == exe
    expected_version = version.partition("\n")[0].partition("=")[2] if version and "=" in version else version
    assert result.version == (expected_version.strip() if expected_version else None)
    assert result.romfs == tmp_path / "romfs"
    assert result.nups == (tmp_path / "game.nup", tmp_path / "other.NUP")
    assert result.supports_mods == supports
    assert bool(result.reason) != supports
    assert before == snapshot(tmp_path)


@pytest.mark.parametrize("launcher", ["hookshot.exe", "hookshot", "longshot.exe", "longshot"])
def test_missing_bin_does_not_accept_root_launcher(tmp_path, launcher):
    (tmp_path / launcher).write_bytes(b"HOS_MODS\0mods: %s: %d RomFS files\0")
    result = detect(tmp_path)
    assert result.game == ("Longshot" if launcher.startswith("longshot") else "Hookshot")
    assert result.exe.parent == tmp_path / "bin"
    assert not result.supports_mods and result.reason
    assert result.romfs is None
    assert result.nups == ()
    assert not (tmp_path / "bin").exists()


def test_missing_installation_is_a_read_only_result(tmp_path):
    folder = tmp_path / "missing"
    result = detect(folder)
    assert result.exe == folder / game_binary(result.game)
    assert not result.supports_mods and result.reason
    assert game_folders(folder) == (folder,)
    assert not folder.exists()


@pytest.mark.parametrize("game, program", GAMES)
@pytest.mark.parametrize("suffix", [".exe", ""])
@pytest.mark.parametrize("supports", [False, True])
def test_either_systems_game_binary_is_inspected_in_bin(tmp_path, game, program, suffix, supports):
    exe = make_build(tmp_path, binary=f"bin/{program}{suffix}", marker=supports)
    # The Linux folder-root launcher is a script named like the game: it is never the game.
    (tmp_path / program).write_bytes(b"#!/bin/sh\n# HOS_MODS\0\n")
    result = detect(tmp_path)
    assert (result.game, result.exe) == (game, exe)
    assert result.supports_mods == supports
    assert bool(result.reason) != supports


@pytest.mark.parametrize("game, program", GAMES)
@pytest.mark.parametrize("platform, suffix", [("win32", ".exe"), ("linux", ""), ("darwin", ".exe")])
def test_missing_game_names_the_file_this_computer_needs(tmp_path, monkeypatch, game, program, platform, suffix):
    monkeypatch.setattr("clawshot.pack.hookshot.sys.platform", platform)
    (tmp_path / program).write_bytes(b"#!/bin/sh\n# HOS_MODS\0\n")
    result = detect(tmp_path)
    assert (result.game, result.exe) == (game, tmp_path / f"bin/{program}{suffix}")
    assert not result.supports_mods and str(result.exe) in result.reason


def test_native_suffix_is_known_only_where_the_games_have_builds():
    assert native_suffix("win32") == ".exe"
    assert native_suffix("linux") == ""
    assert native_suffix("darwin") is None


def test_versions_order_by_number_with_releases_above_their_candidates_and_nightlies():
    labels = ["v3.0.0", "v3.10.0", "nightly-56", "v3.0.0-rc.10", "v2.9.0", "v3.0.0-rc.9", "v3.0.0-rc.2", "nightly-7"]
    ordered = ["nightly-7", "nightly-56", "v2.9.0", "v3.0.0-rc.2", "v3.0.0-rc.9", "v3.0.0-rc.10", "v3.0.0", "v3.10.0"]
    assert sorted(labels, key=version_key) == ordered


@pytest.mark.parametrize("choose", ["program", "data"])
@pytest.mark.parametrize("binary", ["bin/longshot.exe", "bin/longshot"])
def test_portable_launcher_plays_its_newest_build(tmp_path, choose, binary):
    program = tmp_path / "LongshotLauncher"
    data = program / "LongshotLauncher-data"
    program.mkdir()
    (program / "portable").write_text("synthetic portable marker")
    (program / "LongshotLauncher.exe").write_bytes(b"synthetic launcher, never the game")
    older = make_build(data / "builds/v3.0.0-rc.9", "v3.0.0-rc.9", binary)
    newer = make_build(data / "builds/v3.0.0-rc.10", "v3.0.0-rc.10", binary)
    make_build(data / "builds/v3.0.0-rc.11", "v3.0.0-rc.11", "bin/hookshot.exe")  # not a Longshot build
    (data / "builds/broken").mkdir()
    write_registry(data, (older.parents[1], "v3.0.0-rc.9"))  # an unlisted build in builds still counts
    before = snapshot(tmp_path)
    result = detect(program if choose == "program" else data)
    assert (result.game, result.version, result.exe) == ("Longshot", "v3.0.0-rc.10", newer)
    assert result.folder == newer.parents[1]
    assert result.launcher == data and result.supports_mods and not result.reason
    assert result.folders == tuple(dict.fromkeys((result.selected_folder, data, newer.parents[1])))
    assert game_folders(result.selected_folder) == result.folders
    assert before == snapshot(tmp_path)


@pytest.mark.parametrize("choose", ["program", "data", "builds"])
def test_installed_launcher_reads_builds_json_for_builds_elsewhere(tmp_path, choose):
    local = tmp_path / "AppData/Local"
    program = local / "Programs/LongshotLauncher"
    program.mkdir(parents=True)
    (program / "LongshotLauncher.exe").write_bytes(b"synthetic launcher, never the game")
    data = local / "LongshotLauncher"
    games = tmp_path / "Games/Longshot"
    stable = make_build(games / "v3.0.0")  # no version file: the launcher's label decides
    candidate = make_build(games / "v3.0.0-rc.2", "v3.0.0-rc.2")
    listed = [(candidate.parents[1], "v3.0.0-rc.2"), (stable.parents[1], "v3.0.0"), (games / "gone", "v9.0.0")]
    write_registry(data, *listed)
    result = detect({"program": program, "data": data, "builds": games}[choose])
    # A folder of builds without the launcher's list orders by folder name but reports no version it cannot read.
    assert (result.version, result.exe) == (None if choose == "builds" else "v3.0.0", stable)
    assert result.launcher == (None if choose == "builds" else data)
    assert stable.parents[1] in result.folders and result.selected_folder in result.folders
    if choose == "program":
        assert data in result.folders and program in result.folders


@pytest.mark.parametrize("choose", ["share", "launcher", "appimage-folder", "appimage-home"])
def test_linux_launcher_homes(tmp_path, choose):
    share = tmp_path / "home/.local/share/longshot"
    apps = tmp_path / "Applications"
    home = apps / "LongshotLauncher-v1.0.0-x86_64.AppImage.home"
    data = home / ".local/share/longshot/launcher" if choose.startswith("appimage") else share / "launcher"
    exe = make_build(tmp_path / "home/Games/Longshot/v3.0.0", "v3.0.0", "bin/longshot")
    make_build(tmp_path / "home/Games/Longshot/v3.0.0-rc.2", "v3.0.0-rc.2", "bin/longshot")
    write_registry(data, (exe.parents[1], "v3.0.0"), (tmp_path / "home/Games/Longshot/v3.0.0-rc.2", "v3.0.0-rc.2"))
    chosen = {"share": share, "launcher": share / "launcher", "appimage-folder": apps, "appimage-home": home}[choose]
    result = detect(chosen)
    assert (result.game, result.version, result.exe, result.launcher) == ("Longshot", "v3.0.0", exe, data)


def test_launcher_without_a_build_explains_instead_of_guessing(tmp_path):
    data = tmp_path / "LongshotLauncher/LongshotLauncher-data"
    write_registry(data, (tmp_path / "deleted-build", "v3.0.0"))
    result = detect(tmp_path / "LongshotLauncher")
    assert result.game == "Longshot" and result.launcher == data
    assert not result.supports_mods and "has no Longshot build" in result.reason
    assert not (tmp_path / "deleted-build").exists()


def test_newest_build_without_mod_loading_is_refused_not_skipped(tmp_path):
    games = tmp_path / "Games/Longshot"
    make_build(games / "v3.0.0-rc.2", "v3.0.0-rc.2")
    newest = make_build(games / "v3.0.0", "v3.0.0", marker=False)
    result = detect(games)
    assert result.exe == newest and not result.supports_mods and "cannot load mods" in result.reason
