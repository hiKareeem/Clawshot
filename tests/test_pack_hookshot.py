"""Read-only installation facts and fail-closed Play capability."""

import pytest

from clawshot.pack.hookshot import detect


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
    assert result.exe == folder / "bin/hookshot.exe"
    assert not result.supports_mods
    assert result.reason.startswith("missing ")
    assert not folder.exists()
