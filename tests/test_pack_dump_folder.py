"""A base+update dump folder reads as the newest update laid over the base. Synthetic files only."""

import pytest

from clawshot.pack import VERSION_FILES, PackError, check_version, version_digest
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


def test_a_layer_picked_inside_a_dump_folder_means_the_dump_folder(tmp_path, monkeypatch):
    from clawshot.app import paths

    root = tmp_path / "dump"
    _write(root / "base/romfs", {name: b"cart " + name.encode() for name in VERSION_FILES[::3]})
    _write(root / "updates/131072/romfs", {name: b"update " + name.encode() for name in VERSION_FILES[1:3]})
    monkeypatch.setattr(paths, "check_version", lambda path: version_digest(path))
    for picked in ("base/romfs", "base", "updates/131072/romfs", "updates/131072", "updates"):
        assert paths.detect_dump(str(root / picked))["path"] == str(root)
    lone = tmp_path / "cart/romfs"
    _write(lone, {name: b"cart" for name in VERSION_FILES[::3]})
    with pytest.raises(ValueError, match="cart files plus the Version 1.1.1 update") as error:
        paths.detect_dump(str(lone))
    assert VERSION_FILES[1] in str(error.value) and VERSION_FILES[0] not in str(error.value)


def test_finder_metadata_is_not_game_or_seed_content(tmp_path):
    from clawshot.pack import tree_digest

    _write(tmp_path / "seed", {"romfs/a.txt": b"a", "spoiler.json": b"{}"})
    before = tree_digest(tmp_path / "seed")
    _write(tmp_path / "seed", {".DS_Store": b"x", "romfs/._a.txt": b"x", "__MACOSX/romfs/a.txt": b"x"})
    assert tree_digest(tmp_path / "seed") == before
    _write(tmp_path / "dump/base/romfs", {"a.txt": b"a", ".DS_Store": b"x", "dir/._a.txt": b"x"})
    assert sorted(LayeredRomfs(tmp_path / "dump").files) == ["a.txt"]


def test_generation_uses_and_protects_the_whole_dump_folder(tmp_path):
    from clawshot.app import GenerationRequest

    root = tmp_path / "dump"
    _write(root / "base/romfs", {"a.txt": b"cart"})
    _write(root / "updates/131072/romfs", {"a.txt": b"update"})
    request = GenerationRequest(str(root / "base/romfs"), str(tmp_path / "seed-1"), 1, "CS1")
    assert request.paths()[0] == root
    inside = GenerationRequest(str(root / "base/romfs"), str(root / "seed-1"), 1, "CS1")
    with pytest.raises(ValueError, match="protected"):
        inside.paths()


@pytest.mark.parametrize("empty_updates", [False, True])
def test_base_only_dump_explains_the_required_update_before_caching(tmp_path, empty_updates):
    root = tmp_path / "dump"
    _write(
        root / "base/romfs",
        {
            VERSION_FILES[0]: b"synthetic dictionary pack",
            VERSION_FILES[1].replace(".110.", ".100."): b"synthetic base game data",
        },
    )
    if empty_updates:
        (root / "updates").mkdir()
    with pytest.raises(PackError, match="base game.*v131072"):
        check_version(root)
    parent = tmp_path / "stage"
    parent.mkdir()
    with pytest.raises(PackError, match="base game.*v131072"), local_romfs(root, parent):
        pytest.fail("a base-only dump must not be used for generation")
    assert not list(parent.iterdir())
