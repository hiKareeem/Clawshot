"""The CLI names a wrong or missing romfs folder plainly, before reading the dump or writing output."""

from clawshot.__main__ import main


def _run(tmp_path, romfs):
    out = tmp_path / "seed"
    status = main(["--romfs", str(romfs), "--seed", "7", "--out", str(out)])
    return status, out


def test_missing_romfs_folder_is_named(tmp_path, capsys):
    status, out = _run(tmp_path, tmp_path / "missing-romfs")
    assert status == 1
    assert "romfs folder not found" in capsys.readouterr().err
    assert not out.exists()


def test_base_game_romfs_without_the_update_is_explained(tmp_path, capsys):
    romfs = tmp_path / "base" / "romfs"
    (romfs / "GameData").mkdir(parents=True)
    (romfs / "GameData" / "GameDataList.Product.100.byml.zs").write_bytes(b"synthetic")
    status, out = _run(tmp_path, romfs)
    assert status == 1
    error = capsys.readouterr().err
    assert "v131072" in error and "base game" in error and "Traceback" not in error
    assert not out.exists()


def test_other_folder_is_refused_without_a_traceback(tmp_path, capsys):
    romfs = tmp_path / "not-a-romfs"
    romfs.mkdir()
    status, out = _run(tmp_path, romfs)
    assert status == 1
    error = capsys.readouterr().err
    assert "GameData/GameDataList.Product.110.byml.zs" in error and "base game" not in error
    assert not out.exists()
