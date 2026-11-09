"""Private packs reject wrong dumps and never replace played output."""

import hashlib
import json

import pytest

from clawshot.pack import VERSION_FILES, PackError, build, runtime, tree_digest, version_digest


def test_digest_covers_names_bytes_and_extra_files_but_not_mtime(tmp_path):
    seed = tmp_path / "seed"
    seed.mkdir()
    file = seed / "note.md"
    file.write_bytes(b"route\n")
    expected = hashlib.sha256(b"note.md\0" + hashlib.sha256(b"route\n").digest()).hexdigest()
    assert tree_digest(seed) == expected
    file.touch()
    assert tree_digest(seed) == expected
    file.rename(seed / "other.md")
    assert tree_digest(seed) != expected
    file = seed / "other.md"
    renamed = tree_digest(seed)
    file.write_bytes(b"wrong\n")
    assert tree_digest(seed) != renamed
    changed = tree_digest(seed)
    (seed / "extra").write_bytes(b"stale overlay")
    assert tree_digest(seed) != changed


def test_wrong_version_stops_before_any_pack_output(tmp_path):
    romfs = tmp_path / "romfs"
    for index, name in enumerate(VERSION_FILES):
        path = romfs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"synthetic version {index}".encode())
    out = tmp_path / "not-created" / "pack.zip"
    actual = version_digest(romfs)
    with pytest.raises(PackError, match=actual):
        build(romfs, 8, "invalid-settings-never-read", out)
    assert not out.parent.exists()


def test_existing_seed_is_verified_not_rebuilt_and_mismatch_stops_play(tmp_path, monkeypatch):
    root = tmp_path / "pack"
    seed = root / "seed"
    seed.mkdir(parents=True)
    file = seed / "note.md"
    file.write_bytes(b"existing")
    manifest = {"seed": 8, "output_sha256": tree_digest(seed)}
    # Only substitute input discovery; exercise real output reuse and digest refusal.
    monkeypatch.setattr(runtime, "configuration", lambda _: (manifest, tmp_path / "romfs", tmp_path / "game"))
    runtime.make(root)
    file.write_bytes(b"changed while playing")
    with pytest.raises(PackError, match="digest mismatch"):
        runtime.make(root)
    with pytest.raises(PackError, match="digest mismatch"):
        runtime.play(root)
    assert file.read_bytes() == b"changed while playing"
    assert not (root / "user").exists()
    assert not (root / "hookshot_log.txt").exists()


def test_missing_bin_never_uses_root_launcher(tmp_path, monkeypatch):
    root = tmp_path / "pack"
    root.mkdir()
    game = tmp_path / "hookshot"
    game.mkdir()
    (game / "hookshot.exe").write_bytes(b"not executable; must never be run")
    (root / "pack.json").write_text(json.dumps({"format": 1}))
    (root / "folders.json").write_text(json.dumps({"romfs": str(tmp_path / "romfs"), "hookshot": str(game)}))
    monkeypatch.setattr(runtime, "check_version", lambda _: None)
    with pytest.raises(PackError, match="never use the folder-root"):
        runtime.play(root)
    assert not (root / "user").exists()
    assert not (root / "hookshot_log.txt").exists()


def test_pack_inside_game_directory_is_rejected(tmp_path, monkeypatch):
    root = tmp_path / "game" / "pack"
    root.mkdir(parents=True)
    (root / "pack.json").write_text(json.dumps({"format": 1}))
    (root / "folders.json").write_text(json.dumps({"romfs": str(tmp_path / "romfs"), "hookshot": str(root.parent)}))
    monkeypatch.setattr(runtime, "check_version", lambda _: None)
    with pytest.raises(PackError, match="outside your game folders"):
        runtime.configuration(root.resolve())
