"""NX archive input (fab918/nxformat SPEC.md 1.0.3), on synthetic archives this test writes itself."""

import hashlib
import struct

import pytest
import zstandard

from clawshot.pack import PackError
from clawshot.pack._nx.read import NxArchive, NxError, crc32c
from clawshot.pack.source import game_version, open_source

CHUNK_LOG2 = 16


def _align(value: int, alignment: int) -> int:
    return -(-value // alignment) * alignment


def _pad(data: bytearray, alignment: int) -> None:
    data.extend(b"\0" * (_align(len(data), alignment) - len(data)))


def write_nx(path, snapshots, *, compress=frozenset(), application_id=0x0400486024DEC000):
    """A minimal valid archive: one application, one program, ``snapshots`` = [(type, version, {path: bytes})]."""
    blocks, refs, files, block_ids = [], [], [], {}
    data = bytearray(b"\0" * 8192)
    block_rows = []

    def add_file(content: bytes, name: str) -> int:
        first = len(refs)
        chunk = 1 << CHUNK_LOG2
        for k in range(0, len(content), chunk):
            piece = content[k : k + chunk]
            if piece not in block_ids:
                stored = zstandard.ZstdCompressor().compress(piece) if name in compress else piece
                _pad(data, 16)
                checks = -(-len(piece) // 16384)
                first_check = sum(-(-row[2] // 16384) for row in block_rows)
                block_rows.append((len(data), len(stored), len(piece), 1 if name in compress else 0, first_check))
                blocks.append([crc32c(piece[i : i + 16384]) for i in range(0, len(piece), 16384)][:checks])
                data.extend(stored)
                block_ids[piece] = len(block_rows) - 1
            refs.append(block_ids[piece])
        files.append((len(content), first, len(refs) - first, hashlib.sha256(content).digest()))
        return len(files) - 1

    # Manifest: directories are built per snapshot from slash paths.
    directories: list[list[tuple[bytes, int, int]]] = []  # entries (name, kind, target)

    def build_dir(tree: dict) -> int:
        index = len(directories)
        directories.append([])
        entries = []
        for name in sorted(tree, key=lambda n: n.encode()):
            value = tree[name]
            if isinstance(value, dict):
                entries.append((name.encode(), 1, build_dir(value)))
            else:
                entries.append((name.encode(), 2, add_file(value, name)))
        directories[index] = entries
        return index

    roots = []
    for _, _, content in snapshots:
        tree: dict = {}
        for full, value in content.items():
            node = tree
            parts = full.split("/")
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = value
        roots.append(build_dir(tree))

    entry_rows, dir_rows, pool = [], [], bytearray()
    for entries in directories:
        dir_rows.append((len(entry_rows), len(entries)))
        for name, kind, target in entries:
            entry_rows.append((len(pool), len(name), target, kind))
            pool.extend(name)
    m = bytearray(b"\0" * 96)
    dir_off = len(m)
    for first, count in dir_rows:
        m += struct.pack("<IIII", first, count, 0, 0)
    _pad(m, 8)
    file_off = len(m) if files else 0
    for size, first, count, digest in files:
        m += struct.pack("<QIIBBH", size, first, count, CHUNK_LOG2, 0, 0) + digest + b"\0" * 12
    _pad(m, 8)
    entry_off = len(m)
    pool_off_placeholder = []
    for name_off, name_len, target, kind in entry_rows:
        pool_off_placeholder.append(len(m))
        m += struct.pack("<QIIBBHI", name_off, name_len, target, kind, 0, 0, 0)
    _pad(m, 4)
    ref_off = len(m) if refs else 0
    for block_id in refs:
        m += struct.pack("<I", block_id)
    _pad(m, 8)
    pool_off = len(m)
    for position, (name_off, *_rest) in zip(pool_off_placeholder, entry_rows, strict=True):
        struct.pack_into("<Q", m, position, pool_off + name_off)
    m += pool
    _pad(m, 8)
    struct.pack_into(
        "<4sHHQIIIIQQQQQQ",
        m,
        0,
        b"NXMF",
        1,
        96,
        len(m),
        len(dir_rows),
        len(files),
        len(entry_rows),
        len(refs),
        dir_off,
        file_off,
        entry_off,
        ref_off,
        pool_off,
        len(pool),
    )

    # Catalog: one application, one program, the snapshots.
    strings = bytearray(b"1.0.0")
    c = bytearray(b"\0" * 128)
    app_off = len(c)
    c += struct.pack("<QBBHIIII", application_id, 2, 1, 0, 0, 1, 0, len(snapshots))
    c += struct.pack("<IIIIIIIIIIII", 0xFFFFFFFF, 0, 0xFFFFFFFF, 0, 0xFFFFFFFF, 0, 0, 0xFFFFFFFF, 0, 0, 0xFFFFFFFF, 0)
    c += b"\0" * 8
    program_off = len(c)
    c += struct.pack("<QIBBH", application_id, 0, 0, 0, 0) + b"\0" * 16
    c += struct.pack("<IIII", 0, len(snapshots), 0xFFFFFFFF, 0) + b"\0" * 16
    snap_off = len(c)
    for (kind, version, _), root in zip(snapshots, roots, strict=True):
        c += struct.pack("<IBBHIIQII", 0, kind, 0, 0, version, root, 0, 0, 5) + b"\0" * 16
        c += struct.pack("<II", 0, 0) + hashlib.sha256(bytes([kind, version & 0xFF, root])).digest() + b"\0" * 32
    string_off = len(c)
    c += strings
    _pad(c, 8)
    struct.pack_into(
        "<4sHHQIIIIIIIIQQQQQQQQ",
        c,
        0,
        b"NXCT",
        1,
        128,
        len(c),
        0,
        1,
        1,
        len(snapshots),
        0,
        0,
        0,
        0,
        app_off,
        program_off,
        snap_off,
        0,
        0,
        0,
        string_off,
        len(strings),
    )

    # Tail and header.
    data_size = len(data) - 8192 if block_rows else 0
    _pad(data, 16)
    catalog_offset = len(data)
    data += c
    _pad(data, 16)
    manifest_offset = len(data)
    data += m
    index = b"".join(struct.pack("<QIIBBHI", off, st, lg, codec, 0, 0, fc) for off, st, lg, codec, fc in block_rows)
    integrity = b"".join(struct.pack("<I", v) for row in blocks for v in row)
    index_offset = integrity_offset = 0
    if block_rows:
        _pad(data, 16)
        index_offset = len(data)
        data += index
        _pad(data, 16)
        integrity_offset = len(data)
        data += integrity
    header = bytearray(256)
    struct.pack_into(
        "<4sHHIHHQQQQQQQQQQQQQ",
        header,
        0,
        b"NXAR",
        0,
        2,
        256,
        1,
        0,
        len(data),
        catalog_offset,
        len(c),
        0,
        0,
        8192 if block_rows else 0,
        data_size,
        manifest_offset,
        len(m),
        index_offset,
        len(block_rows),
        integrity_offset,
        len(integrity),
    )
    header[120:152] = hashlib.sha256(c).digest()
    header[152:184] = hashlib.sha256(m).digest()
    header[184:216] = hashlib.sha256(index + integrity).digest()
    struct.pack_into("<QI", header, 216, 0, 16384)
    struct.pack_into("<I", header, 252, crc32c(bytes(header[:252])))
    data[0:256] = header
    data[4096:4352] = header
    path.write_bytes(bytes(data))
    return path


BIG = bytes(range(256)) * 600  # spans three 64 KiB chunks


def _game(tmp_path, **kwargs):
    base = {"exefs/main": b"code", "romfs/GameData/GameDataList.Product.100.byml.zs": b"cart", "romfs/Big.bin": BIG}
    update = {
        "exefs/main": b"code 2",
        "romfs/GameData/GameDataList.Product.110.byml.zs": b"update",
        "romfs/Big.bin": BIG,
        "romfs/Pack/ZsDic.pack.zs": b"dict",
    }
    return write_nx(tmp_path / "game.nx", [(0, 0, base), (1, 131072, update)], **kwargs)


def test_crc32c_check_value():
    assert crc32c(b"123456789") == 0xE3069283


def test_the_newest_snapshot_is_read_as_one_complete_romfs(tmp_path):
    path = _game(tmp_path, compress={"Big.bin"})
    with open_source(path) as source:
        assert game_version(source) == "1.1.1"
        assert sorted(source.files) == [
            "Big.bin",
            "GameData/GameDataList.Product.110.byml.zs",
            "Pack/ZsDic.pack.zs",
        ]
        assert source.read("Big.bin") == BIG and source.read("Pack/ZsDic.pack.zs") == b"dict"
        with pytest.raises(PackError, match="missing romfs/Nope"):
            source.read("Nope")


def test_a_damaged_file_or_header_is_refused(tmp_path):
    path = _game(tmp_path)
    data = bytearray(path.read_bytes())
    data[8192 + 20] ^= 0xFF  # inside the first block: the file's SHA-256 no longer matches
    path.write_bytes(bytes(data))
    with open_source(path) as source, pytest.raises(NxError, match="SHA-256"):
        source.read("Big.bin")
    data[4096 + 30] ^= 0xFF  # slot B damaged: slot A still mounts
    data[30] ^= 0xFF  # and slot A: nothing does
    path.write_bytes(bytes(data))
    with pytest.raises(NxError, match="no valid header slot"):
        NxArchive(path)


def test_an_archive_without_a_romfs_tree_is_explained(tmp_path):
    path = write_nx(tmp_path / "nsp.nx", [(0, 0, {"main.nca": b"native"})])
    with pytest.raises(PackError, match="no romfs/ tree"), open_source(path):
        pass
