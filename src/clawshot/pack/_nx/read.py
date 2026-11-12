"""A read-only NX archive reader (``.nx``, magic ``NXAR``, wire versions (0,2) and (0,3)).

Written from fab918/nxformat's ``docs/SPEC.md`` (release 1.0.3, MIT; see ``LICENSE.txt`` beside this file), section
numbers below are the spec's. Only what Clawshot needs is read: the selected header generation, the Catalog's
applications and snapshots, the Manifest tree and the file bytes. Every range is bounds-checked and every structure
that is hashed is verified before use: the header CRC-32C, the Catalog, Manifest and index SHA-256 digests, and each
file's own SHA-256 when it is read (the spec's per-file full verification, §12; the per-slice CRC-32C table is not
needed when the whole file's digest is checked). Media payloads (icons, NACP) are never read.
"""

import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path

import zstandard

MAGIC = b"NXAR"
SUPPORTED_VERSIONS = {(0, 2), (0, 3)}
HEADER_SIZE = 256
SLOT_OFFSETS = (0, 4096)
REQUIRED_FEATURE_HEADER_PAGES = 1
CHECK_SIZE = 16384
MAX_CATALOG = 16 << 20
ABSENT = 0xFFFFFFFF

# §4 snapshot types and the required extensions this reader understands (unknown required ones reject, §11).
SNAPSHOT_BASE, SNAPSHOT_UPDATE, SNAPSHOT_DLC, SNAPSHOT_STANDALONE_UPDATE = 0, 1, 2, 3
KNOWN_REQUIRED_EXTENSIONS = {0x00010004, 0x00010005, 0x00010008}

CODEC_RAW, CODEC_ZSTD = 0, 1
ENTRY_DIRECTORY, ENTRY_FILE = 1, 2


class NxError(ValueError):
    """The archive is damaged, unsupported or not an NX archive."""


def crc32c(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc = _CRC32C_TABLE[(crc ^ byte) & 0xFF] ^ (crc >> 8)
    return crc ^ 0xFFFFFFFF


def _crc32c_table() -> tuple[int, ...]:
    table = []
    for n in range(256):
        c = n
        for _ in range(8):
            c = (c >> 1) ^ 0x82F63B78 if c & 1 else c >> 1
        table.append(c)
    return tuple(table)


_CRC32C_TABLE = _crc32c_table()


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _u64(data: bytes, offset: int) -> int:
    return struct.unpack_from("<Q", data, offset)[0]


def _range(data: bytes, offset: int, size: int, what: str) -> bytes:
    if offset < 0 or size < 0 or offset + size > len(data):
        raise NxError(f"{what}: range {offset}+{size} is outside its {len(data)}-byte region")
    return data[offset : offset + size]


@dataclass(frozen=True)
class Header:
    generation: int
    archive_size: int
    catalog: tuple[int, int]
    manifest: tuple[int, int]
    block_index_offset: int
    block_count: int
    integrity: tuple[int, int]
    catalog_sha256: bytes
    manifest_sha256: bytes
    index_sha256: bytes
    raw: bytes


@dataclass(frozen=True)
class Snapshot:
    index: int
    application_id: int
    platform: int
    snapshot_type: int
    version: int
    root: int
    display_version: str | None


@dataclass(frozen=True)
class NxFile:
    size: int
    first_reference: int
    block_count: int
    chunk_log2: int
    sha256: bytes


def _parse_header(raw: bytes, file_size: int) -> Header:
    """§3, one slot; raises NxError for a slot that fails validation."""
    if len(raw) != HEADER_SIZE or raw[:4] != MAGIC:
        raise NxError("not an NX header")
    if (_u16(raw, 4), _u16(raw, 6)) not in SUPPORTED_VERSIONS:
        raise NxError(f"unsupported NX version {_u16(raw, 4)}.{_u16(raw, 6)}")
    if _u32(raw, 8) != HEADER_SIZE:
        raise NxError("bad header size")
    if _u16(raw, 12) != REQUIRED_FEATURE_HEADER_PAGES or _u16(raw, 14) != 0:
        raise NxError("unsupported NX feature bits")
    if any(raw[228:252]):
        raise NxError("nonzero reserved header bytes")
    if crc32c(raw[:252]) != _u32(raw, 252):
        raise NxError("header CRC-32C mismatch")
    if _u32(raw, 224) != CHECK_SIZE:
        raise NxError("unsupported integrity check size")
    archive_size = _u64(raw, 16)
    if archive_size > file_size:
        raise NxError("archive_size is past the end of the file")
    catalog = (_u64(raw, 24), _u64(raw, 32))
    if not 128 <= catalog[1] <= MAX_CATALOG:
        raise NxError("bad catalog size")
    return Header(
        generation=_u64(raw, 216),
        archive_size=archive_size,
        catalog=catalog,
        manifest=(_u64(raw, 72), _u64(raw, 80)),
        block_index_offset=_u64(raw, 88),
        block_count=_u64(raw, 96),
        integrity=(_u64(raw, 104), _u64(raw, 112)),
        catalog_sha256=raw[120:152],
        manifest_sha256=raw[152:184],
        index_sha256=raw[184:216],
        raw=raw,
    )


class NxArchive:
    """One opened archive. ``snapshots`` lists the Catalog's snapshots; ``tree(snapshot)`` maps each file path of a
    snapshot (``romfs/Pack/ZsDic.pack.zs``) to its file record; ``read(file)`` returns verified file bytes."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._stream = self.path.open("rb")
        try:
            self._open()
        except BaseException:
            self._stream.close()
            raise

    def close(self) -> None:
        self._stream.close()

    def _pread(self, offset: int, size: int) -> bytes:
        self._stream.seek(offset)
        data = self._stream.read(size)
        if len(data) != size:
            raise NxError(f"short read at {offset} ({len(data)} of {size} bytes)")
        return data

    # --- mount (§1, §3, §12 levels 1 and 2) -------------------------------------------------------------------

    def _open(self) -> None:
        file_size = self.path.stat().st_size
        valid: list[Header] = []
        errors: list[str] = []
        for offset in SLOT_OFFSETS:
            try:
                page = self._pread(offset, 4096) if offset + 4096 <= file_size else self._pread(offset, HEADER_SIZE)
                if any(page[HEADER_SIZE:]):
                    raise NxError("nonzero header page padding")
                valid.append(_parse_header(page[:HEADER_SIZE], file_size))
            except (NxError, struct.error) as error:
                errors.append(f"slot at {offset}: {error}")
        if not valid:
            raise NxError("no valid header slot (" + "; ".join(errors) + ")")
        valid.sort(key=lambda h: h.generation, reverse=True)
        if len(valid) == 2 and valid[0].generation == valid[1].generation and valid[0].raw != valid[1].raw:
            raise NxError("both header slots have the same generation but differ")
        # Newest generation whose metadata checks out first; an older one only if the newer one is damaged (§1).
        last_error = None
        for header in valid:
            try:
                self._mount(header)
                return
            except (NxError, struct.error, UnicodeError) as error:
                last_error = error
        raise NxError(f"no header generation mounts: {last_error}")

    def _mount(self, header: Header) -> None:
        catalog = self._pread(*header.catalog)
        if hashlib.sha256(catalog).digest() != header.catalog_sha256:
            raise NxError("catalog SHA-256 mismatch")
        manifest = self._pread(*header.manifest)
        if hashlib.sha256(manifest).digest() != header.manifest_sha256:
            raise NxError("manifest SHA-256 mismatch")
        index = b""
        if header.block_count:
            index = self._pread(header.block_index_offset, header.block_count * 24)
            index += self._pread(*header.integrity)
        if hashlib.sha256(index).digest() != header.index_sha256:
            raise NxError("block index SHA-256 mismatch")
        self.header = header
        self._blocks = index[: header.block_count * 24]
        self._parse_catalog(catalog)
        self._parse_manifest(manifest)

    def _parse_catalog(self, data: bytes) -> None:
        """§4: applications and snapshots, plus the extension table's required types."""
        if data[:4] != b"NXCT" or _u16(data, 4) != 1 or _u16(data, 6) != 128 or _u64(data, 8) != len(data):
            raise NxError("bad catalog header")
        app_count, snap_count, ext_count = _u32(data, 20), _u32(data, 28), _u32(data, 40)
        app_table, snap_table, ext_table = _u64(data, 48), _u64(data, 64), _u64(data, 88)
        pool = _range(data, _u64(data, 96), _u64(data, 104), "catalog string pool")
        apps = _range(data, app_table, app_count * 80, "application table")
        snaps = _range(data, snap_table, snap_count * 120, "snapshot table")
        exts = _range(data, ext_table, ext_count * 32, "extension table")
        for i in range(ext_count):
            type_id, flags = _u32(exts, i * 32), _u32(exts, i * 32 + 4)
            if flags & 1 and type_id not in KNOWN_REQUIRED_EXTENSIONS:
                raise NxError(f"unknown required catalog extension {type_id:#010x}")

        def string(offset: int, length: int) -> str | None:
            if offset == ABSENT and length == 0:
                return None
            return _range(pool, offset, length, "catalog string").decode("utf-8")

        owner = {}
        for a in range(app_count):
            row = apps[a * 80 : a * 80 + 80]
            first, count = _u32(row, 20), _u32(row, 24)
            if first + count > snap_count:
                raise NxError("application snapshot range out of bounds")
            for s in range(first, first + count):
                owner[s] = (_u64(row, 0), row[8])
        self.snapshots: list[Snapshot] = []
        for s in range(snap_count):
            row = snaps[s * 120 : s * 120 + 120]
            if s not in owner:
                raise NxError(f"snapshot {s} belongs to no application")
            application_id, platform = owner[s]
            self.snapshots.append(
                Snapshot(
                    index=s,
                    application_id=application_id,
                    platform=platform,
                    snapshot_type=row[4],
                    version=_u32(row, 8),
                    root=_u32(row, 12),
                    display_version=string(_u32(row, 24), _u32(row, 28)),
                )
            )

    def _parse_manifest(self, data: bytes) -> None:
        """§6: directory, file, entry and block-reference tables, and the path pool."""
        if data[:4] != b"NXMF" or _u16(data, 4) != 1 or _u16(data, 6) != 96 or _u64(data, 8) != len(data):
            raise NxError("bad manifest header")
        dirs, files, entries, refs = _u32(data, 16), _u32(data, 20), _u32(data, 24), _u32(data, 28)
        self._dirs = _range(data, _u64(data, 32), dirs * 16, "directory table")
        self._files = _range(data, _u64(data, 40), files * 64, "file table")
        self._entries = _range(data, _u64(data, 48), entries * 24, "entry table")
        self._refs = _range(data, _u64(data, 56), refs * 4, "block reference table")
        self._manifest = data
        self._pool = (_u64(data, 64), _u64(data, 72))
        _range(data, *self._pool, "path pool")
        self._dir_count, self._file_count = dirs, files

    # --- trees and files (§6, §7, §8) -------------------------------------------------------------------------

    def file(self, file_id: int) -> NxFile:
        if file_id >= self._file_count:
            raise NxError(f"file id {file_id} out of range")
        row = self._files[file_id * 64 : file_id * 64 + 64]
        record = NxFile(_u64(row, 0), _u32(row, 8), _u32(row, 12), row[16], row[20:52])
        if not 16 <= record.chunk_log2 <= 20:
            raise NxError(f"file {file_id}: bad chunk size")
        expected = -(-record.size // (1 << record.chunk_log2))
        if record.block_count != expected:
            raise NxError(f"file {file_id}: {record.block_count} blocks for {record.size} bytes")
        return record

    def tree(self, snapshot: Snapshot) -> dict[str, NxFile]:
        """Every file of ``snapshot``, by its slash-joined path. A node reached twice is a cycle (§6)."""
        out: dict[str, NxFile] = {}
        seen_dirs: set[int] = set()
        seen_files: set[int] = set()
        pool_start, pool_size = self._pool
        stack = [(snapshot.root, "")]
        while stack:
            directory, prefix = stack.pop()
            if directory >= self._dir_count or directory in seen_dirs:
                raise NxError(f"snapshot {snapshot.index}: directory {directory} is out of range or a cycle")
            seen_dirs.add(directory)
            first, count = _u32(self._dirs, directory * 16), _u32(self._dirs, directory * 16 + 4)
            for e in range(first, first + count):
                row = _range(self._entries, e * 24, 24, "directory entry")
                name_offset, name_length = _u64(row, 0), _u32(row, 8)
                if name_offset < pool_start or name_offset + name_length > pool_start + pool_size:
                    raise NxError("entry name outside the path pool")
                name = self._manifest[name_offset : name_offset + name_length].decode("utf-8")
                if not name or name in (".", "..") or "/" in name or "\\" in name or "\0" in name:
                    raise NxError(f"bad path component {name!r}")
                target, kind = _u32(row, 12), row[16]
                path = f"{prefix}{name}"
                if kind == ENTRY_DIRECTORY:
                    stack.append((target, path + "/"))
                elif kind == ENTRY_FILE:
                    if target in seen_files:
                        raise NxError(f"snapshot {snapshot.index}: file {target} appears twice")
                    seen_files.add(target)
                    out[path] = self.file(target)
                else:
                    raise NxError(f"bad entry kind {kind}")
        return out

    def _block(self, block_id: int) -> bytes:
        if block_id >= self.header.block_count:
            raise NxError(f"block {block_id} out of range")
        row = self._blocks[block_id * 24 : block_id * 24 + 24]
        offset, stored, logical, codec = _u64(row, 0), _u32(row, 8), _u32(row, 12), row[16]
        data = self._pread(offset, stored)
        if codec == CODEC_RAW:
            if stored != logical:
                raise NxError(f"block {block_id}: RAW sizes differ")
            return data
        if codec == CODEC_ZSTD:
            out = zstandard.ZstdDecompressor().decompress(data, max_output_size=logical)
            if len(out) != logical:
                raise NxError(f"block {block_id}: decoded {len(out)} bytes, expected {logical}")
            return out
        raise NxError(f"block {block_id}: unknown codec {codec}")

    def read(self, record: NxFile) -> bytes:
        chunk = 1 << record.chunk_log2
        parts = []
        for k in range(record.block_count):
            block_id = _u32(self._refs, (record.first_reference + k) * 4)
            data = self._block(block_id)
            want = min(chunk, record.size - k * chunk)
            if len(data) != want:
                raise NxError(f"block {block_id}: {len(data)} bytes where the file needs {want}")
            parts.append(data)
        data = b"".join(parts)
        if hashlib.sha256(data).digest() != record.sha256:
            raise NxError("file SHA-256 mismatch")
        return data
