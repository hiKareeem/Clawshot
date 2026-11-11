"""A base+update dump folder reads as the newest update laid over the base. Synthetic files only."""

import pytest

from clawshot.pack import VERSION_FILES, PackError, version_digest
from clawshot.pack.source import LayeredRomfs, dump_layers, local_romfs


def _write(root, files):
    for relative, data in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


@pytest.fixture
def dump(tmp_path):
    root = tmp_path / "dump"
    _write(root / "base/romfs", {"a.txt": b"base a", "b.txt": b"base b", "dir/c.txt": b"base c"})
    _write(root / "updates/65536/romfs", {"a.txt": b"old update a", "d.txt": b"old update d"})
    _write(root / "updates/131072/romfs", {"a.txt": b"update a", "dir/c.txt": b"update c", "e.txt": b"update e"})
    _write(root / "updates/notes/romfs", {"a.txt": b"not a version"})
    (root / "updates/196608").mkdir()  # no romfs: not a layer
    return root


def test_newest_update_shadows_the_base_by_path(dump):
    layered = LayeredRomfs(dump)
    assert layered.layers == [dump / "base/romfs", dump / "updates/131072/romfs"]
    assert sorted(layered.files) == ["a.txt", "b.txt", "dir/c.txt", "e.txt"]  # never the older update's d.txt
    assert layered.read("a.txt") == b"update a"
    assert layered.read("dir/c.txt") == b"update c"
    assert layered.read("b.txt") == b"base b"
    with pytest.raises(PackError, match="romfs/d.txt"):
        layered.read("d.txt")


def test_base_only_dump_is_one_layer_and_other_folders_are_not_dumps(tmp_path):
    _write(tmp_path / "dump/base/romfs", {"a.txt": b"base a"})
    assert dump_layers(tmp_path / "dump") == [tmp_path / "dump/base/romfs"]
    assert dump_layers(tmp_path / "dump/base/romfs") is None
    with pytest.raises(PackError, match="not a dump folder"):
        LayeredRomfs(tmp_path / "dump/base/romfs")


def test_plain_romfs_folder_is_used_in_place(tmp_path):
    romfs = tmp_path / "romfs"
    romfs.mkdir()
    with local_romfs(romfs, tmp_path / "unused") as used:
        assert used == romfs
    assert not (tmp_path / "unused").exists()


def test_dump_fingerprint_equals_the_merged_folder(tmp_path):
    merged = {name: f"v1.1 {name}".encode() for name in VERSION_FILES}
    _write(tmp_path / "merged", merged)
    _write(tmp_path / "dump/base/romfs", {name: f"v1.0 {name}".encode() for name in VERSION_FILES})
    _write(tmp_path / "dump/updates/131072/romfs", merged)
    assert version_digest(tmp_path / "dump") == version_digest(tmp_path / "merged")
    assert version_digest(tmp_path / "dump") != version_digest(tmp_path / "dump/base/romfs")


def test_wrong_build_dump_is_refused_before_any_cache_is_made(tmp_path):
    _write(tmp_path / "dump/base/romfs", {name: b"not the game" for name in VERSION_FILES})
    parent = tmp_path / "stage"
    parent.mkdir()
    with pytest.raises(PackError, match="does not match build"), local_romfs(tmp_path / "dump", parent):
        pass
    assert not list(parent.iterdir())
