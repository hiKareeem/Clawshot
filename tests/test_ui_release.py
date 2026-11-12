"""Source releases have a positive file boundary and never require a game dump."""

import zipfile
from pathlib import Path

import pytest

from clawshot.ui.release import EXTRA, build


def synthetic_source(root):
    names = (
        "pyproject.toml",
        "uv.lock",
        ".python-version",
        "README.md",
        "LICENSE",
        "NOTICE",
        "docs/seed-pack.md",
        "src/clawshot/pack/_nup/LICENSE.txt",
        "src/clawshot/pack/_nx/LICENSE.txt",
        "src/clawshot/__init__.py",
        "src/clawshot/data/world.toml",
        *EXTRA,
    )
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('[project]\nversion="2.4.6"\n' if name == "pyproject.toml" else "synthetic source\n")
    for name in (
        "romfs/secret.zs",
        "keys.txt",
        "output/seed/romfs/secret.zs",
        ".tools/uv.exe",
        "src/clawshot/ui/static/private.bin",
        "plans/private.md",
    ):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"invented forbidden payload")


def test_release_lists_only_source_and_local_assets_with_no_game_and_does_not_overwrite(tmp_path, monkeypatch):
    root = tmp_path / "source"
    synthetic_source(root)
    monkeypatch.delenv("OOT_ROMFS", raising=False)
    first = build(tmp_path / "one", root=root)
    second = build(tmp_path / "two", root=root)
    assert first.name == "Clawshot-2.4.6.zip" and first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        names = {Path(name).relative_to("Clawshot-2.4.6").as_posix() for name in archive.namelist()}
        assert set(EXTRA) <= names
        assert {"LICENSE", "NOTICE", "uv.lock", "src/clawshot/data/world.toml", "READ ME FIRST.txt"} <= names
        assert {"src/clawshot/pack/_nup/LICENSE.txt", "src/clawshot/pack/_nx/LICENSE.txt"} <= names
        assert all(b"invented forbidden payload" not in archive.read(name) for name in archive.namelist())
        for launcher in ("clawshot.sh", "Clawshot.command"):
            assert archive.getinfo(f"Clawshot-2.4.6/{launcher}").external_attr >> 16 & 0o111
    before = first.read_bytes(), first.stat().st_mtime_ns
    with pytest.raises(FileExistsError):
        build(first.parent, root=root)
    assert before == (first.read_bytes(), first.stat().st_mtime_ns)
