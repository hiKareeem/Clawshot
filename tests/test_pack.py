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
    exe = tmp_path / "game/bin/hookshot.exe"
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"must never be run")
    runtime.make(root)
    file.write_bytes(b"changed while playing")
    with pytest.raises(PackError, match="digest mismatch"):
        runtime.make(root)
    with pytest.raises(PackError, match="digest mismatch"):
        runtime.play(root)
    assert file.read_bytes() == b"changed while playing"
    assert not (root / "user").exists()
    assert not (root / "hookshot_log.txt").exists()


def test_pack_inside_game_directory_is_rejected(tmp_path, monkeypatch):
    root = tmp_path / "game" / "pack"
    root.mkdir(parents=True)
    (root / "pack.json").write_text(json.dumps({"format": 1}))
    (root / "folders.json").write_text(json.dumps({"romfs": str(tmp_path / "romfs"), "game": str(root.parent)}))
    monkeypatch.setattr(runtime, "check_version", lambda _: None)
    with pytest.raises(PackError, match="outside your game folders"):
        runtime.configuration(root.resolve())


@pytest.fixture
def configured_pack(tmp_path, monkeypatch):
    romfs = tmp_path / "romfs"
    for index, name in enumerate(VERSION_FILES):
        path = romfs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"synthetic version {index}".encode())
    monkeypatch.setattr("clawshot.pack.ROMFS_SHA256", version_digest(romfs))
    root = tmp_path / "pack"
    seed = root / "seed"
    seed.mkdir(parents=True)
    (seed / "note.md").write_bytes(b"verified local seed")
    (root / "pack.json").write_text(json.dumps({"format": 1, "seed": 8, "output_sha256": tree_digest(seed)}))
    (root / "folders.json").write_text(json.dumps({"romfs": str(romfs)}))
    return root, romfs


@pytest.mark.parametrize("game", [None, "", "not-installed"])
def test_make_without_game_installation(configured_pack, game):
    root, _ = configured_pack
    if game is not None:
        config = json.loads((root / "folders.json").read_text())
        config["game"] = str(root.parent / game) if game else ""
        (root / "folders.json").write_text(json.dumps(config))
    seed = root / "seed" / "note.md"
    before = seed.stat().st_mtime_ns
    assert runtime.main(["make", "--root", str(root)]) == 0
    assert seed.read_bytes() == b"verified local seed"
    assert seed.stat().st_mtime_ns == before
    assert not (root / "user").exists()
    assert not (root / "hookshot_log.txt").exists()


@pytest.mark.parametrize("folders", [{}, {"game": ""}, {"hookshot": ""}, {"game": "", "hookshot": "configured"}])
def test_emulator_only_play_points_to_loading_guide(configured_pack, folders):
    root, _ = configured_pack
    config = json.loads((root / "folders.json").read_text())
    # A legacy "hookshot" folder never overrides the "game" the pack names, even an empty one.
    config |= {key: str(root.parent / value) if value else "" for key, value in folders.items()}
    (root / "folders.json").write_text(json.dumps(config))
    with pytest.raises(PackError, match="docs/seed-pack.md"):
        runtime.play(root)
    assert not (root / "user").exists()
    assert not (root / "hookshot_log.txt").exists()


def test_version_failure_precedes_optional_hookshot_checks(configured_pack):
    root, romfs = configured_pack
    (romfs / VERSION_FILES[0]).write_bytes(b"different update")
    actual = version_digest(romfs)
    with pytest.raises(PackError, match=actual):
        runtime.play(root)
    assert not (root / "user").exists()
    assert not (root / "hookshot_log.txt").exists()


@pytest.mark.parametrize("nested_romfs", [False, True])
def test_make_without_hookshot_still_rejects_romfs_overlap(configured_pack, nested_romfs):
    root, original_romfs = configured_pack
    romfs = root / "romfs" if nested_romfs else root.parent
    for name in VERSION_FILES:
        path = romfs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((original_romfs / name).read_bytes())
    (root / "folders.json").write_text(json.dumps({"romfs": str(romfs)}))
    with pytest.raises(PackError, match="outside your game folders"):
        runtime.make(root)
    assert (root / "seed" / "note.md").read_bytes() == b"verified local seed"


def test_pack_zip_keeps_its_files_at_the_root_with_the_seed_in_pack_json(tmp_path, monkeypatch):
    import zipfile

    import clawshot.pack as pack

    def fake_generate(_root, _romfs, _seed, _settings, out):
        out.mkdir()
        (out / "spoiler.json").write_text("{}")

    monkeypatch.setattr(pack, "check_version", lambda _: None)
    monkeypatch.setattr(pack, "generate", fake_generate)
    romfs = tmp_path / "romfs"
    romfs.mkdir()
    manifest = build(romfs, 4242, "CS1", tmp_path / "seed-4242.zip")
    with zipfile.ZipFile(tmp_path / "seed-4242.zip") as archive:
        names = archive.namelist()
        metadata = json.loads(archive.read("pack.json"))
    assert "READ ME FIRST.txt" in names and "Make seed.bat" in names
    assert metadata == manifest and metadata["seed"] == 4242
    assert not any(name.startswith("seed/") or ".DS_Store" in name for name in names)
