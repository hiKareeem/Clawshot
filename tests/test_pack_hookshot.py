"""Read-only installation facts and fail-closed Play capability."""

import pytest

from clawshot.pack.hookshot import LINUX_GAME, WINDOWS_GAME, detect, native_game


@pytest.mark.parametrize("version", [None, "v2.0.13\n", "version=v2.0.13\nbuilder=synthetic.exe\n", "v99.0.0\n"])
@pytest.mark.parametrize("supports", [False, True])
def test_binary_capability_not_version_label(tmp_path, version, supports):
    exe = tmp_path / "bin/hookshot.exe"
    exe.parent.mkdir()
    exe.write_bytes(b"HOS_MODS\0" if supports else b"mods: %s: %d RomFS files\0")
    if version is not None:
        (tmp_path / "hookshot_version.txt").write_text(version, encoding="utf-8-sig")
    (tmp_path / "romfs").mkdir()
    (tmp_path / "game.nup").write_bytes(b"not decoded")
    (tmp_path / "other.NUP").write_bytes(b"not decoded either")
    (tmp_path / "directory.nup").mkdir()
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.rglob("*") if p.is_file()}
    result = detect(str(tmp_path))
    assert result.folder == tmp_path
    assert result.exe == exe
    expected_version = "v2.0.13" if version and version.startswith("version=") else version.strip() if version else None
    assert result.version == expected_version
    assert result.romfs == tmp_path / "romfs"
    assert result.nups == (tmp_path / "game.nup", tmp_path / "other.NUP")
    assert result.supports_mods == supports
    assert bool(result.reason) != supports
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.rglob("*") if p.is_file()}


def test_missing_bin_does_not_accept_root_launcher(tmp_path):
    (tmp_path / "hookshot.exe").write_bytes(b"HOS_MODS\0mods: %s: %d RomFS files\0")
    result = detect(tmp_path)
    assert not result.supports_mods
    assert "never use the folder-root launcher" in result.reason
    assert result.romfs is None
    assert result.nups == ()
    assert not (tmp_path / "bin").exists()


def test_missing_installation_is_a_read_only_result(tmp_path):
    folder = tmp_path / "missing"
    result = detect(folder)
    assert result.exe == folder / (native_game() or WINDOWS_GAME)
    assert not result.supports_mods
    assert result.reason.startswith("missing ")
    assert not folder.exists()


@pytest.mark.parametrize("game", [WINDOWS_GAME, LINUX_GAME])
@pytest.mark.parametrize("supports", [False, True])
def test_either_systems_game_binary_is_inspected_in_bin(tmp_path, game, supports):
    exe = tmp_path / game
    exe.parent.mkdir()
    exe.write_bytes(b"synthetic image\0HOS_MODS\0" if supports else b"synthetic image without the marker\0")
    # The Linux folder-root launcher is a script named like the game: it is never the game.
    (tmp_path / "hookshot").write_bytes(b"#!/bin/sh\n# HOS_MODS\0\n")
    result = detect(tmp_path)
    assert result.exe == exe
    assert result.supports_mods == supports
    assert bool(result.reason) != supports


@pytest.mark.parametrize(
    "platform, expected",
    [("win32", WINDOWS_GAME), ("linux", LINUX_GAME), ("darwin", WINDOWS_GAME)],
)
def test_missing_game_names_the_file_this_computer_needs(tmp_path, monkeypatch, platform, expected):
    monkeypatch.setattr("clawshot.pack.hookshot.sys.platform", platform)
    (tmp_path / "hookshot").write_bytes(b"#!/bin/sh\n# HOS_MODS\0\n")
    result = detect(tmp_path)
    assert result.exe == tmp_path / expected
    assert not result.supports_mods
    assert result.reason == f"missing {tmp_path / expected}; never use the folder-root launcher"


def test_native_game_is_known_only_where_hookshot_has_a_build():
    assert native_game("win32") == WINDOWS_GAME
    assert native_game("linux") == LINUX_GAME
    assert native_game("darwin") is None
