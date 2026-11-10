"""Synthetic NUPs: package selection, compressed reads, integrity and preflight ordering."""

import hashlib
import json
import struct

import pytest
import zstandard

from clawshot.pack import VERSION_FILES, PackError, build, runtime, tree_digest, version_digest
from clawshot.pack.source import local_romfs, open_nup


def write_nup(path, packages):
    """Build v1 records from the public format; all contents are invented by tests."""
    dirs, files, roots = [], [], []
    for version, kind, contents in packages:
        root = {}
        for name, data in contents.items():
            node = root
            parts = name.split("/")
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = data

        def directory(name, children):
            index = len(dirs)
            dirs.append([name.encode(), []])
            for child, data in sorted(children.items()):
                if isinstance(data, dict):
                    dirs[index][1].append((True, directory(child, data)))
                else:
                    fi = len(files)
                    files.append((child.encode(), data))
                    dirs[index][1].append((False, fi))
            return index

        ri = directory("", {"romfs": root})
        roots.append((version, kind, ri, ri + 1))
    pool, records, children = bytearray(), bytearray(), []

    def name_ref(name):
        off = len(pool)
        pool.extend(name)
        return off, len(name)

    for name, refs in dirs:
        records.extend(struct.pack("<IIIIQ", *name_ref(name), len(children), len(refs), 0))
        children.extend(i if is_dir else len(dirs) + i for is_dir, i in refs)
    file_names = [name_ref(name) for name, _ in files]
    toc_size = 48 + 64 * len(roots) + len(records) + 80 * len(files) + 4 * len(children) + len(pool)
    blob_offset = (128 + toc_size + 15) & ~15
    blob, file_records = bytearray(), bytearray()
    for i, (_, data) in enumerate(files):
        compressed = zstandard.ZstdCompressor().compress(data)
        codec = int(len(compressed) < len(data))
        payload = compressed if codec else data
        offset = blob_offset + len(blob) if data else 0
        file_records.extend(
            struct.pack(
                "<IIQQQ32sBBH12x",
                *file_names[i],
                len(data),
                offset,
                len(payload),
                hashlib.sha256(data).digest(),
                codec,
                0,
                0,
            )
        )
        blob.extend(payload)
        blob.extend(b"\0" * (-len(blob) % 16))
    toc = bytearray(
        struct.pack("<4sIQQQQQ", b"TOC\x01", len(roots), len(dirs), len(files), toc_size - len(pool), len(pool), 0)
    )
    for version, kind, ri, romfs in roots:
        toc.extend(
            struct.pack(
                "<QIIIIBBHIQI20x", 0x0400486024DEC000, ri, 0xFFFFFFFF, romfs, version, kind, int(kind == 1), 0, 0, 0, 0
            )
        )
    toc.extend(records)
    toc.extend(file_records)
    toc.extend(struct.pack(f"<{len(children)}I", *children))
    toc.extend(pool)
    header = struct.pack(
        "<4sHHQQ32sQQII16s32s",
        b"NUP\x01",
        128,
        1,
        128,
        len(toc),
        hashlib.sha256(toc).digest(),
        blob_offset,
        blob_offset + len(blob),
        len(roots),
        0,
        b"\0" * 16,
        b"\0" * 32,
    )
    path.write_bytes(header + toc + b"\0" * (blob_offset - 128 - len(toc)) + blob)
    return path


def version_files(label=b"supported"):
    return {name: label + str(i).encode() for i, name in enumerate(VERSION_FILES)}


def test_nup_and_folder_have_identical_fingerprints_and_reads(tmp_path):
    contents = version_files() | {"nested/compressed": b"synthetic" * 1000, "empty": b""}
    path = write_nup(tmp_path / "game.nup", [(131072, 1, contents)])
    root = tmp_path / "folder"
    for name, data in contents.items():
        file = root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)
    assert version_digest(path) == version_digest(root)
    with open_nup(path) as source:
        assert {name: source.read(name) for name in source.files} == contents
        assert source.reader.file_info(source.files["nested/compressed"])[-1] == 1
    path.rename(tmp_path / "closed.nup")  # no leaked mmap/file handle on Windows


def test_newest_update_is_used_without_base_fallback(tmp_path, monkeypatch):
    path = write_nup(tmp_path / "game.nup", [(0, 0, version_files()), (131072, 1, version_files(b"new"))])
    expected = version_digest(write_nup(tmp_path / "base.nup", [(0, 0, version_files())]))
    monkeypatch.setattr("clawshot.pack.ROMFS_SHA256", expected)
    with pytest.raises(PackError, match="fingerprint"):
        build(path, 8, "never-decoded", tmp_path / "pack.zip")
    assert not (tmp_path / "pack.zip").exists()
    with pytest.raises(PackError, match="fingerprint"), local_romfs(path, tmp_path):
        pytest.fail("wrong update reached generation")
    assert not list(tmp_path.glob(".romfs-*"))


def test_incomplete_newest_update_does_not_borrow_base_files(tmp_path):
    path = write_nup(tmp_path / "game.nup", [(0, 0, version_files()), (131072, 1, {VERSION_FILES[0]: b"new"})])
    with pytest.raises(PackError, match="missing romfs"):
        version_digest(path)


@pytest.mark.parametrize("damage", ["toc", "payload", "truncated"])
def test_corrupt_nup_is_rejected_before_output(tmp_path, damage):
    path = write_nup(tmp_path / "game.nup", [(131072, 1, version_files())])
    data = bytearray(path.read_bytes())
    if damage == "toc":
        data[150] ^= 1
    elif damage == "payload":
        offset = struct.unpack_from("<Q", data, 56)[0]
        data[offset] ^= 1
    else:
        data = data[:100]
    path.write_bytes(data)
    with pytest.raises(PackError):
        build(path, 8, "never-decoded", tmp_path / "out" / "pack.zip")
    assert not (tmp_path / "out").exists()
    path.unlink()  # failed parse also closes the handle


def test_malformed_compressed_extent_is_reported_as_pack_error(tmp_path):
    contents = version_files() | {VERSION_FILES[0]: b"synthetic compressed bytes" * 1000}
    path = write_nup(tmp_path / "game.nup", [(131072, 1, contents)])
    with open_nup(path) as source:
        info = source.reader.file_info(source.files[VERSION_FILES[0]])
        assert info[-1] == 1
        offset = info[3]
    data = bytearray(path.read_bytes())
    data[offset] ^= 1  # break the zstd frame magic, not the independently hashed TOC
    path.write_bytes(data)
    with pytest.raises(PackError):
        version_digest(path)
    path.unlink()


@pytest.mark.parametrize("name", ["../escape", "C:/escape", "nested/back\\slash", "A/file", "bad./file"])
def test_unsafe_nup_names_never_reach_disk(tmp_path, name):
    contents = version_files() | {name: b"unsafe", "a/file": b"case collision"}
    path = write_nup(tmp_path / "game.nup", [(131072, 1, contents)])
    with pytest.raises(PackError):
        version_digest(path)
    assert not (tmp_path / "escape").exists()


def test_existing_nup_seed_is_verified_without_cache_or_hookshot(tmp_path, monkeypatch):
    path = write_nup(tmp_path / "game.nup", [(131072, 1, version_files())])
    monkeypatch.setattr("clawshot.pack.ROMFS_SHA256", version_digest(path))
    root = tmp_path / "pack"
    seed = root / "seed"
    seed.mkdir(parents=True)
    note = seed / "play-note.md"
    note.write_text("already generated")
    (root / "pack.json").write_text(json.dumps({"format": 1, "seed": 8, "output_sha256": tree_digest(seed)}))
    (root / "folders.json").write_text(json.dumps({"romfs": str(path), "hookshot": ""}))
    before = note.stat().st_mtime_ns
    runtime.make(root.resolve())
    assert note.read_text() == "already generated"
    assert note.stat().st_mtime_ns == before
    assert sorted(p.name for p in root.iterdir()) == ["folders.json", "pack.json", "seed"]
