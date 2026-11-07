"""BYML v7, little-endian (magic ``YB``, placement files) or big-endian (magic ``BY``, ``GameDataList``): read to
and write from Python trees. :func:`load`/:func:`dump` keep a file's byte order; :func:`read`/:func:`write` work on
the tree alone (``write`` defaults to little-endian).

Node types map to Python types so that a tree read from a file writes back with the same types:

========  ===================  ============================
type      node                 Python
========  ===================  ============================
0xA0      string               ``str``
0xC0      array                ``list``
0xC1      map (string keys)    ``dict`` with ``str`` keys
0x20      hash map, 32-bit     :class:`Hash32Map` (``int`` keys)
0x21      hash map, 64-bit     :class:`Hash64Map` (``int`` keys)
0xD0      bool                 ``bool``
0xD1      int32                :class:`I32` (also plain ``int``)
0xD2      float32              :class:`F32` (also plain ``float``)
0xD3      uint32               :class:`U32`
0xD4      int64                :class:`I64`
0xD5      uint64               :class:`U64`
0xD6      float64              :class:`F64`
0xFF      null                 ``None``
========  ===================  ============================

Use :func:`same` to compare trees: ``==`` treats ``I32(1)`` and ``U32(1)`` as equal.
"""

import struct
from dataclasses import dataclass
from typing import Any

MAGIC_LITTLE = b"YB"
MAGIC_BIG = b"BY"
VERSION = 7

STRING = 0xA0
ARRAY = 0xC0
MAP = 0xC1
STRING_TABLE = 0xC2
HASH32_MAP = 0x20
HASH64_MAP = 0x21
BOOL = 0xD0
INT = 0xD1
FLOAT = 0xD2
UINT = 0xD3
INT64 = 0xD4
UINT64 = 0xD5
DOUBLE = 0xD6
NULL = 0xFF

CONTAINERS = (ARRAY, MAP, HASH32_MAP, HASH64_MAP)
LONG_VALUES = (INT64, UINT64, DOUBLE)


class BymlError(ValueError):
    pass


class I32(int):
    __slots__ = ()

    def __new__(cls, value=0):
        v = int.__new__(cls, value)
        if not -(1 << 31) <= v < 1 << 31:
            raise BymlError(f"{value} does not fit an int32")
        return v

    def __repr__(self):
        return f"I32({int(self)})"


class U32(int):
    __slots__ = ()

    def __new__(cls, value=0):
        v = int.__new__(cls, value)
        if not 0 <= v < 1 << 32:
            raise BymlError(f"{value} does not fit a uint32")
        return v

    def __repr__(self):
        return f"U32({int(self)})"


class I64(int):
    __slots__ = ()

    def __new__(cls, value=0):
        v = int.__new__(cls, value)
        if not -(1 << 63) <= v < 1 << 63:
            raise BymlError(f"{value} does not fit an int64")
        return v

    def __repr__(self):
        return f"I64({int(self)})"


class U64(int):
    __slots__ = ()

    def __new__(cls, value=0):
        v = int.__new__(cls, value)
        if not 0 <= v < 1 << 64:
            raise BymlError(f"{value} does not fit a uint64")
        return v

    def __repr__(self):
        return f"U64({int(self)})"


class F32(float):
    """A float32. The value is held exactly (as read from four bytes), so writing it back gives the same bytes."""

    __slots__ = ()

    def __new__(cls, value=0.0):
        return float.__new__(cls, struct.unpack("<f", struct.pack("<f", value))[0])

    def __repr__(self):
        return f"F32({float(self)!r})"


class F64(float):
    __slots__ = ()

    def __repr__(self):
        return f"F64({float(self)!r})"


class Hash32Map(dict):
    """A hash map node with 32-bit integer keys (type 0x20)."""

    def __repr__(self):
        return f"Hash32Map({dict.__repr__(self)})"


class Hash64Map(dict):
    """A hash map node with 64-bit integer keys (type 0x21)."""

    def __repr__(self):
        return f"Hash64Map({dict.__repr__(self)})"


_INT_TYPES = {I32: INT, U32: UINT, I64: INT64, U64: UINT64}


def node_type(value) -> int:
    """The BYML node type ``value`` is written as."""
    if value is None:
        return NULL
    if isinstance(value, bool):
        return BOOL
    if isinstance(value, str):
        return STRING
    if isinstance(value, Hash32Map):
        return HASH32_MAP
    if isinstance(value, Hash64Map):
        return HASH64_MAP
    if isinstance(value, dict):
        return MAP
    if isinstance(value, list):
        return ARRAY
    if isinstance(value, int):
        return _INT_TYPES.get(type(value), INT)
    if isinstance(value, float):
        return DOUBLE if isinstance(value, F64) else FLOAT
    raise BymlError(f"no BYML node type for {type(value).__name__}: {value!r}")


def difference(a, b, path: str = "") -> str | None:
    """Where two trees differ (a path and both values), or None when they are equal and every node has the same
    BYML type. Maps compare as unordered (the writer sorts them); floats compare by their bits."""
    ta, tb = node_type(a), node_type(b)
    if ta != tb:
        return f"{path or '/'}: type 0x{ta:02x} {a!r} vs 0x{tb:02x} {b!r}"
    if ta == ARRAY:
        if len(a) != len(b):
            return f"{path or '/'}: array length {len(a)} vs {len(b)}"
        for i, (x, y) in enumerate(zip(a, b, strict=True)):
            if (d := difference(x, y, f"{path}/{i}")) is not None:
                return d
        return None
    if ta in (MAP, HASH32_MAP, HASH64_MAP):
        if a.keys() != b.keys():
            return f"{path or '/'}: keys only in first {sorted(a.keys() - b.keys())}, only in second " + str(
                sorted(b.keys() - a.keys())
            )
        for k in a:
            if (d := difference(a[k], b[k], f"{path}/{k}")) is not None:
                return d
        return None
    if ta in (FLOAT, DOUBLE):
        fmt = "<f" if ta == FLOAT else "<d"
        equal = struct.pack(fmt, a) == struct.pack(fmt, b)
    else:
        equal = a == b
    return None if equal else f"{path or '/'}: {a!r} vs {b!r}"


def same(a, b) -> bool:
    """True when two trees are equal and every node has the same BYML type."""
    return difference(a, b) is None


# --------------------------------------------------------------------------------------------------------------
# Reading


def byte_order(data: bytes) -> str:
    """``"little"`` (magic ``YB``) or ``"big"`` (magic ``BY``)."""
    magic = bytes(data[:2])
    if magic == MAGIC_LITTLE:
        return "little"
    if magic == MAGIC_BIG:
        return "big"
    raise BymlError(f"not BYML: magic {magic!r}")


class _Reader:
    def __init__(self, data: bytes):
        self.d = memoryview(data)
        self.big = byte_order(data) == "big"
        self.e = ">" if self.big else "<"
        self.version, keys_off, strings_off, self.root_off = struct.unpack_from(self.e + "HIII", data, 2)
        if self.version != VERSION:
            raise BymlError(f"BYML version {self.version}; only {VERSION} is supported")
        self.keys = self.string_table(keys_off)
        self.strings = self.string_table(strings_off)

    def header(self, off: int) -> tuple[int, int]:
        """(node type, count) of the node at ``off``: one type byte, then a 24-bit count."""
        v = struct.unpack_from(self.e + "I", self.d, off)[0]
        return (v >> 24, v & 0xFFFFFF) if self.big else (v & 0xFF, v >> 8)

    def string_table(self, off: int) -> list[str]:
        if not off:
            return []
        t, n = self.header(off)
        if t != STRING_TABLE:
            raise BymlError(f"string table at 0x{off:x} has type 0x{t:02x}")
        offs = struct.unpack_from(f"{self.e}{n + 1}I", self.d, off + 4)
        d = bytes(self.d)
        return [d[off + o : d.index(b"\0", off + o)].decode("utf-8") for o in offs[:n]]

    def value(self, t: int, raw: int):
        if t == STRING:
            return self.strings[raw]
        if t in CONTAINERS:
            return self.container(raw)
        if t == BOOL:
            return raw != 0
        if t == INT:
            return I32(raw - (1 << 32) if raw & 0x80000000 else raw)
        if t == FLOAT:
            return F32(struct.unpack("<f", struct.pack("<I", raw))[0])  # bits only; raw is already in host order
        if t == UINT:
            return U32(raw)
        if t == INT64:
            return I64(struct.unpack_from(self.e + "q", self.d, raw)[0])
        if t == UINT64:
            return U64(struct.unpack_from(self.e + "Q", self.d, raw)[0])
        if t == DOUBLE:
            return F64(struct.unpack_from(self.e + "d", self.d, raw)[0])
        if t == NULL:
            return None
        raise BymlError(f"unsupported BYML value type 0x{t:02x}")

    def container(self, off: int):
        t, n = self.header(off)
        d = self.d
        if t == ARRAY:
            types = bytes(d[off + 4 : off + 4 + n])
            vals = off + 4 + ((n + 3) & ~3)
            raws = struct.unpack_from(f"{self.e}{n}I", d, vals)
            return [self.value(types[i], raws[i]) for i in range(n)]
        if t == MAP:
            out = {}
            for i in range(n):
                # 24-bit key index, then the value's type byte
                kv, raw = struct.unpack_from(self.e + "II", d, off + 4 + 8 * i)
                key, vt = (kv >> 8, kv & 0xFF) if self.big else (kv & 0xFFFFFF, kv >> 24)
                out[self.keys[key]] = self.value(vt, raw)
            return out
        if t in (HASH32_MAP, HASH64_MAP):
            hash_size = 4 if t == HASH32_MAP else 8
            entry = hash_size + 4
            types = bytes(d[off + 4 + entry * n : off + 4 + entry * n + n])
            out = Hash32Map() if t == HASH32_MAP else Hash64Map()
            fmt = self.e + ("II" if t == HASH32_MAP else "QI")
            for i in range(n):
                h, raw = struct.unpack_from(fmt, d, off + 4 + entry * i)
                out[h] = self.value(types[i], raw)
            return out
        raise BymlError(f"unsupported BYML container type 0x{t:02x} at 0x{off:x}")


def read(data: bytes):
    """Parse a BYML v7 document of either byte order; returns its root node (None for an empty document)."""
    r = _Reader(data)
    if not r.root_off:
        return None
    t, _ = r.header(r.root_off)
    if t not in CONTAINERS:
        raise BymlError(f"root node at 0x{r.root_off:x} has type 0x{t:02x}")
    return r.container(r.root_off)


# --------------------------------------------------------------------------------------------------------------
# Writing
#
# The layout follows the game's own files: header, key table, string table (both sorted by UTF-8 bytes, each
# padded to 4), the 8-byte values (int64, uint64, float64; each distinct value once), then the containers. The
# root comes first and every container is followed by its child containers, depth first; a container equal to one
# already written (same types and values) is not written again, its first copy is referenced instead.


def _align4(n: int) -> int:
    return (n + 3) & ~3


def _key_bytes(s: str) -> bytes:
    return s.encode("utf-8")


class _Writer:
    def __init__(self, root, e: str):
        self.e = e  # struct byte-order prefix
        self.keys: set[str] = set()
        self.strings: set[str] = set()
        self.long_order: list[bytes] = []  # 8-byte values in first-use order
        self.long_index: dict[tuple[int, bytes], int] = {}  # (type, bytes): equal bytes of two types stay apart
        self.container_order: list[tuple[int, object]] = []  # (identity, node) in layout order
        self.ident: dict[int, int] = {}  # id(node) -> identity; every node stays alive in the tree
        self.node_entries: dict[int, list] = {}  # id(node) -> entries in written order
        self.identities: dict[tuple, int] = {}
        self.root = root
        self.visit(root)

    def visit(self, node) -> int:
        """Register ``node`` (a container) and everything under it; return its identity, which equal containers
        share."""
        if id(node) in self.ident:
            return self.ident[id(node)]
        t = node_type(node)
        entries = self.entries(node, t)
        sig = []
        for key, value in entries:
            vt = node_type(value)
            sig.append((key, vt, self.visit(value) if vt in CONTAINERS else self.scalar(vt, value)))
        identity = self.identities.setdefault((t, tuple(sig)), len(self.identities))
        self.ident[id(node)] = identity
        self.node_entries[id(node)] = entries
        return identity

    def entries(self, node, t: int):
        if t == ARRAY:
            return list(enumerate(node))
        if t == MAP:
            for k in node:
                if not isinstance(k, str):
                    raise BymlError(f"map key {k!r} is not a string")
                self.keys.add(k)
            return [(k, node[k]) for k in sorted(node, key=_key_bytes)]
        bits = 32 if t == HASH32_MAP else 64
        for k in node:
            if not isinstance(k, int) or isinstance(k, bool) or not 0 <= k < 1 << bits:
                raise BymlError(f"hash map key {k!r} does not fit {bits} bits")
        return [(k, node[k]) for k in sorted(node)]

    def scalar(self, t: int, value):
        if t == STRING:
            self.strings.add(value)
            return value
        if t == BOOL:
            return int(value)
        if t == NULL:
            return 0
        if t == INT:
            if not -(1 << 31) <= value < 1 << 31:
                raise BymlError(f"{value} does not fit an int32; use I64 or U32/U64")
            return value & 0xFFFFFFFF
        if t == UINT:
            return int(value)
        if t == FLOAT:
            return struct.unpack("<I", struct.pack("<f", value))[0]
        if t == INT64:
            return struct.pack(self.e + "q", value)
        if t == UINT64:
            return struct.pack(self.e + "Q", value)
        if t == DOUBLE:
            return struct.pack(self.e + "d", value)
        raise BymlError(f"unsupported node type 0x{t:02x}")

    def layout(self):
        """Walk depth first from the root in layout order: containers (first copy only) and 8-byte values."""
        placed: set[int] = set()

        def walk(node):
            identity = self.ident[id(node)]
            if identity in placed:
                return
            placed.add(identity)
            self.container_order.append((identity, node))
            for _key, value in self.node_entries[id(node)]:
                vt = node_type(value)
                if vt in CONTAINERS:
                    walk(value)
                elif vt in LONG_VALUES:
                    raw = self.scalar(vt, value)
                    if (vt, raw) not in self.long_index:
                        self.long_index[vt, raw] = len(self.long_order)
                        self.long_order.append(raw)

        walk(self.root)


def _container_size(t: int, n: int) -> int:
    if t == ARRAY:
        return 4 + _align4(n) + 4 * n
    if t == MAP:
        return 4 + 8 * n
    if t == HASH32_MAP:
        return 4 + 8 * n + _align4(n)
    return 4 + 12 * n + _align4(n)


def _string_table(strings: list[str], e: str) -> bytes:
    n = len(strings)
    offsets = []
    blob = bytearray()
    base = 4 + 4 * (n + 1)
    for s in strings:
        offsets.append(base + len(blob))
        blob += s.encode("utf-8") + b"\0"
    offsets.append(base + len(blob))
    out = _node_header(STRING_TABLE, n, e) + struct.pack(f"{e}{n + 1}I", *offsets) + blob
    return out + b"\0" * (_align4(len(out)) - len(out))


def _node_header(t: int, n: int, e: str) -> bytes:
    """One type byte, then a 24-bit count in the file's byte order."""
    return bytes([t]) + n.to_bytes(3, "big" if e == ">" else "little")


def _map_entry(key: int, vt: int, e: str) -> bytes:
    """A 24-bit key index in the file's byte order, then the value's type byte."""
    return key.to_bytes(3, "big" if e == ">" else "little") + bytes([vt])


def write(root, byte_order: str = "little") -> bytes:
    """Serialize a tree (a map, array or hash map at the root) as BYML v7, ``"little"`` or ``"big"`` endian."""
    if byte_order not in ("little", "big"):
        raise BymlError(f"byte order must be 'little' or 'big', not {byte_order!r}")
    if node_type(root) not in CONTAINERS:
        raise BymlError(f"the root must be a container, not {type(root).__name__}")
    e = ">" if byte_order == "big" else "<"
    w = _Writer(root, e)
    w.layout()
    keys = sorted(w.keys, key=_key_bytes)
    strings = sorted(w.strings, key=_key_bytes)
    key_index = {k: i for i, k in enumerate(keys)}
    string_index = {s: i for i, s in enumerate(strings)}
    if len(keys) >= 1 << 24:
        raise BymlError(f"{len(keys)} keys; a map key index has 24 bits")

    out = bytearray(16)
    keys_off = len(out) if keys else 0
    if keys:
        out += _string_table(keys, e)
    strings_off = len(out) if strings else 0
    if strings:
        out += _string_table(strings, e)
    long_base = len(out)
    for raw in w.long_order:
        out += raw
    offset = len(out)
    container_offset: dict[int, int] = {}
    for identity, node in w.container_order:
        container_offset[identity] = offset
        offset += _container_size(node_type(node), len(node))
    root_off = container_offset[w.ident[id(root)]]
    magic = MAGIC_BIG if e == ">" else MAGIC_LITTLE
    struct.pack_into(e + "2sHIII", out, 0, magic, VERSION, keys_off, strings_off, root_off)

    def raw_value(vt: int, value) -> int:
        if vt in CONTAINERS:
            return container_offset[w.ident[id(value)]]
        if vt == STRING:
            return string_index[value]
        r = w.scalar(vt, value)
        if vt in LONG_VALUES:
            return long_base + 8 * w.long_index[vt, r]
        return r

    for _identity, node in w.container_order:
        t = node_type(node)
        entries = w.node_entries[id(node)]
        n = len(entries)
        out += _node_header(t, n, e)
        if t == ARRAY:
            types = bytes(node_type(v) for _, v in entries)
            out += types + b"\0" * (_align4(n) - n)
            out += struct.pack(f"{e}{n}I", *(raw_value(node_type(v), v) for _, v in entries))
        elif t == MAP:
            for k, v in entries:
                vt = node_type(v)
                out += _map_entry(key_index[k], vt, e) + struct.pack(e + "I", raw_value(vt, v))
        else:
            fmt = e + ("II" if t == HASH32_MAP else "QI")
            for k, v in entries:
                out += struct.pack(fmt, k, raw_value(node_type(v), v))
            out += bytes(node_type(v) for _, v in entries) + b"\0" * (_align4(n) - n)
    return bytes(out)


@dataclass
class Document:
    """A tree and the byte order of the file it came from, so that it is written back the same way."""

    root: Any
    byte_order: str = "little"


def load(data: bytes) -> Document:
    """Parse a BYML v7 document and remember its byte order."""
    return Document(read(data), byte_order(data))


def dump(document: Document) -> bytes:
    """Serialize a document in its own byte order."""
    return write(document.root, document.byte_order)
