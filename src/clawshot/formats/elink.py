"""ELink effect tables (``ELink2/elink2.Product.*.belnk``, XLNK version 36): decode, re-encode, and the three edits
the song effects need (add a user copied from another, set asset parameters on a call, turn a call into a play-all
container). Written from the layout in plans/song-get-effects.md, decoded from the files themselves.

File layout, in order (positions are absolute u64 unless noted):

- header (0x60): ``XLNK``, +0x04 u32 file size, +0x08 u32 version 36, +0x18 trigger-overwrite table, +0x20 local
  property table, +0x28 u32 local property count, +0x2C u32 enum count, +0x30 u32 direct value count, +0x40 first
  user, +0x48 u32 user count, +0x50 condition table, +0x58 name table. Other words are kept as read.
- u32 CRC32 of each user's name, sorted; then (8-aligned) the u64 offset of each user, in the same order.
- parameter definitions ``{u32 size, u32 user, u32 asset, u32, u32 trigger, u32, 24-byte entries {u64 name, u64
  type, u64 default}, strings}``, then the asset parameter records up to the trigger-overwrite table. A record is a
  u64 bit mask (bit i = asset parameter i) and one u32 per set bit, ``(type << 24) | value``: type 1 a name-table
  offset, type 0 a direct value index; records are shared between calls.
- trigger-overwrite table, local property and enum names (u64 each), the direct values (4-byte floats), other data
  up to the first user (kept as bytes).
- users, contiguous; the condition table; the name table to the end of the file.

A user's bytes are self-relative, so a copy works as a new user: +0x04 low u16 local property count, +0x08 call
count, +0x0C asset count, +0x30 u64 trigger table position (user-relative), +0x38 the local property names (u64),
the user parameters (u32 each), the call indices sorted by key name (u16, 4-aligned), the calls (0x30 bytes:
``{u64 key name, s16 asset id, u16 flag (1 = container), s32 duration, s32 parent, u32 guid, u32 CRC32(key), u32,
u64 parameter record (relative to the records) or container record (relative to the container block), u64
condition}``), the container block (16-byte records ``{3, first child, last child, 0}``: type 3 plays every child),
the trigger table (entries name calls by byte offset from the first call) and padding.

A user's trigger table (counts in the user header: +0x14 slots, +0x18 actions, +0x1C action triggers, +0x20
properties, +0x24 property triggers, +0x28 always triggers): slots ``{u64 name, u16 first action, u16 last action,
u32}`` (``AS[Lower]``, ``Skl[Lower]``: animation slots), actions ``{u64 name, u32 first trigger, u32 last trigger}``
(an animation node the slot plays, e.g. ``Rotate_GetDemo``, or a scene's ``<ASB root>/<node>``), then 0x28-byte
triggers ``{u32 guid, u32, u64 call (byte offset from the first call), ...}``. Within a slot, native actions are
sorted by name ignoring case (all but one of the native ASCII-named slots, dump 1.1.1; event-items D20).

Edits only append (direct values, records, names, calls), so every native position stays valid; new users go after
the native ones. :meth:`Elink.encode` lays the sections out again and fixes the header.
"""

import struct
import zlib
from collections.abc import Sequence
from dataclasses import dataclass

MAGIC = b"XLNK"
VERSION = 36
HEADER = 0x60
CALL = struct.Struct("<QhHiiIIIQQ")
NAME = 1  # value type: name-table offset
DIRECT = 0  # value type: direct value index
PLAY_ALL = 3
NO_CONDITION = 0xFFFFFFFF
TRIGGER_COUNTS = 0x14  # user header: u32 slot, action, trigger, property, property-trigger, always-trigger counts
SLOT_ROW = struct.Struct("<QHHI")
ACTION_ROW = struct.Struct("<QII")
TRIGGER_ROW = 0x28


class ElinkError(ValueError):
    pass


@dataclass(frozen=True)
class Call:
    key: str
    key_offset: int
    asset: int
    flag: int
    duration: int
    parent: int
    guid: int
    key_hash: int
    param: int
    condition: int

    @property
    def is_container(self) -> bool:
        return self.flag == 1


def _u32(data, at: int) -> int:
    return struct.unpack_from("<I", data, at)[0]


def _u64(data, at: int) -> int:
    return struct.unpack_from("<Q", data, at)[0]


def _cstr(data, at: int) -> str:
    end = data.index(b"\0", at)
    return bytes(data[at:end]).decode("utf-8")


@dataclass
class _UserLayout:
    n_local: int
    n_call: int
    ids_at: int
    calls_at: int
    calls_end: int
    trigger: int


class Elink:
    """A decoded table. Users are addressed by name (found by the CRC32 of their name)."""

    def __init__(self, data: bytes):
        if data[:4] != MAGIC:
            raise ElinkError(f"not an ELink table: magic {bytes(data[:4])!r}")
        if (version := _u32(data, 8)) != VERSION:
            raise ElinkError(f"ELink version {version}; only {VERSION} is supported")
        if (size := _u32(data, 4)) != len(data):
            raise ElinkError(f"header size {size} but {len(data)} bytes")
        self.header = bytearray(data[:HEADER])
        n = _u32(data, 0x48)
        hashes = struct.unpack_from(f"<{n}I", data, HEADER)
        table_at = _align(HEADER + 4 * n, 8)
        offsets = struct.unpack_from(f"<{n}Q", data, table_at)
        define = table_at + 8 * n
        records = define + _u32(data, define)
        trigger, local = _u64(data, 0x18), _u64(data, 0x20)
        n_local, n_enum, n_direct = struct.unpack_from("<III", data, 0x28)
        direct = local + 8 * (n_local + n_enum)
        direct_end = direct + 4 * n_direct
        users, cond, names = _u64(data, 0x40), _u64(data, 0x50), _u64(data, 0x58)
        bounds = [define, records, trigger, local, direct, direct_end, users, cond, names, len(data)]
        if bounds != sorted(bounds):
            raise ElinkError(f"sections out of order: {[hex(b) for b in bounds]}")
        if list(hashes) != sorted(hashes):
            raise ElinkError("user hashes are not sorted")
        starts = sorted(zip(offsets, hashes, strict=True))
        if n and starts[0][0] != users:
            raise ElinkError(f"first user at 0x{starts[0][0]:x}, header says 0x{users:x}")
        self.define = bytes(data[define:records])
        self.records = bytearray(data[records:trigger])
        self.overwrite = bytes(data[trigger:local])
        self.locals = bytes(data[local:direct])
        self.direct = bytearray(data[direct:direct_end])
        self.misc = bytes(data[direct_end:users])
        ends = [o for o, _ in starts[1:]] + [cond]
        self.users: list[tuple[int, bytes]] = [(h, bytes(data[o:e])) for (o, h), e in zip(starts, ends, strict=True)]
        self.conditions = bytes(data[cond:names])
        self.names = bytearray(data[names:])
        n_user, n_asset = struct.unpack_from("<II", self.define, 4)
        n_trigger = _u32(self.define, 0x10)
        strings = 0x18 + 24 * (n_user + n_asset + n_trigger)
        self.user_param_count = n_user
        self.asset_params = [
            _cstr(self.define, strings + _u64(self.define, 0x18 + 24 * (n_user + i))) for i in range(n_asset)
        ]
        self._by_hash: dict[int, str] = {}
        self._by_hash_size = -1
        self._slot: dict[int, int] = {}

    # ---------------------------------------------------------------------------------------------------------
    # Reading

    def name_at(self, offset: int) -> str:
        return _cstr(self.names, offset)

    def _hash_names(self) -> dict[int, str]:
        if self._by_hash_size != len(self.names):
            out: dict[int, str] = {}
            for chunk in bytes(self.names).split(b"\0"):
                if chunk:
                    out.setdefault(zlib.crc32(chunk), chunk.decode("utf-8", "replace"))
            self._by_hash, self._by_hash_size = out, len(self.names)
        return self._by_hash

    def user_names(self) -> list[str]:
        """Every user's name in table (hash) order; a user whose name is not in the name table shows as ``#hash``."""
        known = self._hash_names()
        return [known.get(h, f"#{h:08x}") for h, _ in sorted(self.users)]

    def _slots(self) -> dict[int, int]:
        if len(self._slot) != len(self.users):
            self._slot = {h: i for i, (h, _) in enumerate(self.users)}
        return self._slot

    def _index(self, name: str) -> int:
        if (i := self._slots().get(zlib.crc32(name.encode()))) is None:
            raise ElinkError(f"no user {name!r}")
        return i

    def has_user(self, name: str) -> bool:
        return zlib.crc32(name.encode()) in self._slots()

    def user_data(self, name: str) -> bytes:
        return self.users[self._index(name)][1]

    def _layout(self, u: bytes) -> _UserLayout:
        n_local = _u32(u, 4) & 0xFFFF
        n_call = _u32(u, 8)
        ids_at = 0x38 + 8 * n_local + 4 * self.user_param_count
        calls_at = ids_at + _align(2 * n_call, 4)
        return _UserLayout(n_local, n_call, ids_at, calls_at, calls_at + CALL.size * n_call, _u64(u, 0x30))

    def _call(self, u: bytes, lay: _UserLayout, k: int) -> Call:
        key, asset, flag, duration, parent, guid, key_hash, _, param, cond = CALL.unpack_from(
            u, lay.calls_at + CALL.size * k
        )
        return Call(self.name_at(key), key, asset, flag, duration, parent, guid, key_hash, param, cond)

    def _calls(self, u: bytes) -> list[Call]:
        lay = self._layout(u)
        return [self._call(u, lay, k) for k in range(lay.n_call)]

    def calls(self, name: str) -> list[Call]:
        return self._calls(self.user_data(name))

    def _call_index(self, name: str, u: bytes, key: str | int) -> int:
        """The index of the first call named ``key``, or ``key`` itself when it is an index (some native users have
        two calls with one key)."""
        if isinstance(key, int):
            if not 0 <= key < self._layout(u).n_call:
                raise ElinkError(f"{name}: no call {key}")
            return key
        lay = self._layout(u)
        for k in range(lay.n_call):
            if self.name_at(_u64(u, lay.calls_at + CALL.size * k)) == key:
                return k
        raise ElinkError(f"{name}: no call {key!r}")

    def _record(self, pos: int) -> dict[int, int]:
        mask = _u64(self.records, pos)
        bits = [i for i in range(64) if mask >> i & 1]
        return dict(zip(bits, struct.unpack_from(f"<{len(bits)}I", self.records, pos + 8), strict=True))

    def direct_values(self) -> list[float]:
        return list(struct.unpack(f"<{len(self.direct) // 4}f", self.direct))

    def call_params(self, name: str, key: str | int) -> dict[str, str | float | int]:
        """A call's asset parameters by name: names as ``str``, direct values as ``float``, other values raw."""
        u = self.user_data(name)
        call = self._call(u, self._layout(u), self._call_index(name, u, key))
        if call.is_container:
            raise ElinkError(f"{name}/{key} is a container")
        out: dict[str, str | float | int] = {}
        for bit, value in self._record(call.param).items():
            label = self.asset_params[bit] if bit < len(self.asset_params) else f"bit{bit}"
            kind, v = value >> 24, value & 0xFFFFFF
            if kind == NAME:
                out[label] = self.name_at(v)
            elif kind == DIRECT:
                if 4 * v + 4 > len(self.direct):
                    raise ElinkError(f"{name}/{key}: {label} names direct value {v} of {len(self.direct) // 4}")
                out[label] = struct.unpack_from("<f", self.direct, 4 * v)[0]
            else:
                out[label] = value
        return out

    def container(self, name: str, key: str | int) -> tuple[int, int, int]:
        """A container call's (type, first child, last child)."""
        u = self.user_data(name)
        call = self._call(u, self._layout(u), self._call_index(name, u, key))
        if not call.is_container:
            raise ElinkError(f"{name}/{key} is not a container")
        kind, first, last = struct.unpack_from("<III", u, self._layout(u).calls_end + call.param)
        return kind, first, last

    def local_properties(self, name: str) -> list[str]:
        u = self.user_data(name)
        return [self.name_at(_u64(u, 0x38 + 8 * i)) for i in range(self._layout(u).n_local)]

    def trigger_table(self, name: str) -> bytes:
        """A user's trigger table and the padding after it, as bytes."""
        u = self.user_data(name)
        return u[self._layout(u).trigger :]

    def _action_table(self, name: str, u: bytes) -> tuple[list[tuple], list[tuple], list[bytes]]:
        """``name``'s slots ``(name offset, first, last, rest)``, actions ``(name offset, first, last)`` and action
        triggers (bytes). Refuses a user with property or always triggers, rows that do not cover their actions and
        triggers in order, or non-zero bytes after the triggers (a user made a container keeps two paddings)."""
        n_slot, n_action, n_trigger, *other = struct.unpack_from("<6I", u, TRIGGER_COUNTS)
        if any(other):
            raise ElinkError(f"{name}: property or always triggers {other}; only action triggers are handled")
        at = self._layout(u).trigger
        slots = [SLOT_ROW.unpack_from(u, at + SLOT_ROW.size * k) for k in range(n_slot)]
        at += SLOT_ROW.size * n_slot
        actions = [ACTION_ROW.unpack_from(u, at + ACTION_ROW.size * k) for k in range(n_action)]
        at += ACTION_ROW.size * n_action
        triggers = [bytes(u[at + TRIGGER_ROW * k : at + TRIGGER_ROW * (k + 1)]) for k in range(n_trigger)]
        at += TRIGGER_ROW * n_trigger
        if any(u[at:]):
            raise ElinkError(f"{name}: data after the action triggers (padding only expected)")
        for rows, total in ((slots, n_action), (actions, n_trigger)):
            covered = 0
            for row in rows:
                if row[1] != covered or row[2] < row[1]:
                    raise ElinkError(f"{name}: trigger table rows out of order at {row[1]}..{row[2]}")
                covered = row[2] + 1
            if covered != total:
                raise ElinkError(f"{name}: trigger table rows cover {covered} of {total}")
        return slots, actions, triggers

    def action_triggers(self, name: str) -> list[tuple[str, str, list[str]]]:
        """``name``'s action triggers in table order: (slot, action, the key of each trigger's call)."""
        u = self.user_data(name)
        slots, actions, triggers = self._action_table(name, u)
        calls = self._calls(u)
        out = []
        for slot, first, last, _ in slots:
            for action, a, b in actions[first : last + 1]:
                keys = [calls[_u64(trigger, 8) // CALL.size].key for trigger in triggers[a : b + 1]]
                out.append((self.name_at(slot), self.name_at(action), keys))
        return out

    # ---------------------------------------------------------------------------------------------------------
    # Appending

    def intern(self, text: str) -> int:
        """The name-table offset of ``text``: its first complete occurrence, or appended at the end."""
        enc = text.encode("utf-8")
        if b"\0" in enc:
            raise ElinkError(f"name {text!r} holds a NUL")
        if self.names.startswith(enc + b"\0"):
            return 0
        at = self.names.find(b"\0" + enc + b"\0")
        if at >= 0:
            return at + 1
        offset = len(self.names)
        self.names += enc + b"\0"
        return offset

    def _add_direct(self, values: list[float]) -> int:
        first = len(self.direct) // 4
        self.direct += struct.pack(f"<{len(values)}f", *values)
        return first

    def _add_record(self, values: dict[int, int]) -> int:
        pos = len(self.records)
        bits = sorted(values)
        rec = struct.pack("<Q", sum(1 << b for b in bits)) + b"".join(struct.pack("<I", values[b]) for b in bits)
        self.records += rec + bytes(-len(rec) % 8)
        return pos

    def _bit(self, param: str) -> int:
        try:
            return self.asset_params.index(param)
        except ValueError:
            raise ElinkError(f"unknown asset parameter {param!r}") from None

    def _set_user(self, name: str, data: bytes) -> None:
        i = self._index(name)
        self.users[i] = (self.users[i][0], data)

    # ---------------------------------------------------------------------------------------------------------
    # Edits

    def add_user_copy(self, source: str, name: str) -> None:
        """A new user ``name`` with ``source``'s bytes (padded to 8), placed after every user; the hash table stays
        sorted. The name is added to the name table so readers can show it."""
        if self.has_user(name):
            raise ElinkError(f"{name}: a user with this name already exists")
        data = self.user_data(source)
        self.intern(name)
        self.users.append((zlib.crc32(name.encode()), data + bytes(-len(data) % 8)))

    def set_call_params(self, name: str, key: str, values: dict[str, str | float]) -> None:
        """Give a call a new record: its old one with ``values`` set (``str``: a name, otherwise a float direct
        value). Names are interned first, then the floats are appended in order, padded to 8 bytes with 1.0, then
        the record. The old record stays (other calls may share it)."""
        bits = {param: self._bit(param) for param in values}
        u = bytearray(self.user_data(name))
        k = self._call_index(name, bytes(u), key)
        call = self._calls(bytes(u))[k]
        if call.is_container:
            raise ElinkError(f"{name}/{key} is a container")
        names = {bits[p]: (NAME << 24) | self.intern(v) for p, v in values.items() if isinstance(v, str)}
        floats = [(bits[p], float(v)) for p, v in values.items() if not isinstance(v, str)]
        padded = [v for _, v in floats] + [1.0] * (len(floats) % 2)
        first = self._add_direct(padded) if padded else len(self.direct) // 4
        record = self._record(call.param)
        for j, (bit, _) in enumerate(floats):
            record[bit] = first + j
        record.update(names)
        pos = self._add_record(record)
        struct.pack_into("<Q", u, self._layout(bytes(u)).calls_at + CALL.size * k + 0x20, pos)
        self._set_user(name, bytes(u))

    def make_container(self, name: str, key: str, children: list[dict[str, str | float]], condition: int) -> None:
        """Turn call ``key`` into a play-all container of new children ``<key>_00``, ``<key>_01`` ...

        Each child copies the call's record with ``AssetName`` = its own key and ``children[i]`` set (``str``: a
        name, otherwise a float direct value), runs under ``condition`` (a condition-table offset) and is appended
        after the existing calls, so trigger entries keep naming the same calls; only the trigger table moves. Asset
        ids are renumbered 0, 1, 2 ... in call order, as in native users."""
        for child in children:
            for param in child:
                self._bit(param)
        asset_name = self._bit("AssetName")
        u = self.user_data(name)
        lay = self._layout(u)
        calls = [list(CALL.unpack_from(u, lay.calls_at + CALL.size * k)) for k in range(lay.n_call)]
        keys = [self.name_at(c[0]) for c in calls]
        if key not in keys:
            raise ElinkError(f"{name}: no call {key!r}")
        ci = keys.index(key)
        target = calls[ci]
        if target[2] == 1 or target[1] < 0:
            raise ElinkError(f"{name}/{key} is a container")
        block = u[lay.calls_end : lay.trigger]
        if len(block) % 16 or any(_u32(block, k) != PLAY_ALL for k in range(0, len(block), 16)):
            raise ElinkError(f"{name}: only play-all container blocks are handled")
        base = self._record(target[8])
        target[1], target[2], target[8], target[9] = -1, 1, len(block), NO_CONDITION
        first = len(calls)
        for k, child in enumerate(children):
            child_key = f"{key}_{k:02d}"
            values = dict(base)
            values[asset_name] = (NAME << 24) | self.intern(child_key)
            for param, value in child.items():
                if isinstance(value, str):
                    values[self._bit(param)] = (NAME << 24) | self.intern(value)
                else:
                    values[self._bit(param)] = self._add_direct([float(value)])
            calls.append(
                [
                    self.intern(child_key),
                    0,
                    0,
                    1,
                    ci,
                    zlib.crc32(f"{name}/{child_key}".encode()),
                    zlib.crc32(child_key.encode()),
                    0,
                    self._add_record(values),
                    condition,
                ]
            )
            keys.append(child_key)
        assets = 0
        for c in calls:
            if c[2] == 0:
                c[1] = assets
                assets += 1
        n = len(calls)
        order = sorted(range(n), key=lambda i: keys[i].encode())
        ids = struct.pack(f"<{n}H", *order)
        head = bytearray(u[: lay.ids_at])
        struct.pack_into("<II", head, 8, n, assets)
        body = head + ids + bytes(-len(ids) % 4) + b"".join(CALL.pack(*c) for c in calls)
        body += block + struct.pack("<IIII", PLAY_ALL, first, n - 1, 0)
        struct.pack_into("<Q", body, 0x30, len(body))
        body += u[lay.trigger :]
        self._set_user(name, bytes(body + bytes(-len(body) % 8)))

    def add_action_triggers(self, name: str, slot: str, actions: Sequence[str], template: str) -> None:
        """Give user ``name`` an action per name of ``actions`` in slot ``slot``, each with a copy of the one trigger
        of its action ``template`` (so it starts the same call) under the guid CRC32(``<name>/<action>``). The
        trigger table is laid out again: slots in their order, each slot's actions sorted by name ignoring case (as
        native users), then the triggers in action order; the native rows keep their bytes, the header gets the new
        action and trigger counts. New names are interned in that order. Refuses an action the slot has already,
        a missing slot or template, a template without exactly one trigger, and what :meth:`_action_table`
        refuses."""
        u = self.user_data(name)
        slots, rows, triggers = self._action_table(name, u)
        names = [self.name_at(row[0]) for row in rows]
        found = [k for k, row in enumerate(rows) if names[k] == template]
        if len(found) != 1 or rows[found[0]][1] != rows[found[0]][2]:
            raise ElinkError(f"{name}: needs one action {template!r} with one trigger")
        copy = triggers[rows[found[0]][1]]
        by_slot = [s for s in slots if self.name_at(s[0]) == slot]
        if len(by_slot) != 1:
            raise ElinkError(f"{name}: {len(by_slot)} slots {slot!r}, expected one")
        if len(set(actions)) != len(actions):
            raise ElinkError(f"{name}: actions named twice in {list(actions)}")
        table, action_rows, trigger_rows = bytearray(), bytearray(), bytearray()
        n_action = n_trigger = 0
        for row in slots:
            group = [(names[k], rows[k][0], triggers[rows[k][1] : rows[k][2] + 1]) for k in range(row[1], row[2] + 1)]
            if row is by_slot[0]:
                if have := sorted({g[0] for g in group} & set(actions)):
                    raise ElinkError(f"{name}: slot {slot} has {have} already")
                for action in actions:
                    guid = struct.pack("<I", zlib.crc32(f"{name}/{action}".encode()))
                    group.append((action, None, [guid + copy[4:]]))
                group.sort(key=lambda g: g[0].lower().encode("utf-8"))
            table += SLOT_ROW.pack(row[0], n_action, n_action + len(group) - 1, row[3])
            for action, offset, trigs in group:
                offset = self.intern(action) if offset is None else offset
                action_rows += ACTION_ROW.pack(offset, n_trigger, n_trigger + len(trigs) - 1)
                trigger_rows += b"".join(trigs)
                n_action += 1
                n_trigger += len(trigs)
        at = self._layout(u).trigger
        data = bytearray(u[:at]) + table + action_rows + trigger_rows
        data += bytes(-len(data) % 8)
        struct.pack_into("<II", data, TRIGGER_COUNTS + 4, n_action, n_trigger)
        self._set_user(name, bytes(data))

    # ---------------------------------------------------------------------------------------------------------
    # Writing

    def encode(self) -> bytes:
        """The table as bytes: sections in file order, header positions and counts fixed, the file padded to 8.
        An odd number of direct values gets a 1.0 after them (counted), so the sections after stay 8-aligned."""
        direct = bytes(self.direct)
        if len(direct) % 8:
            direct += struct.pack("<f", 1.0)
        n = len(self.users)
        table_at = _align(HEADER + 4 * n, 8)
        define = table_at + 8 * n
        trigger = define + len(self.define) + len(self.records)
        local = trigger + len(self.overwrite)
        users = local + len(self.locals) + len(direct) + len(self.misc)
        offsets = {}
        at = users
        for h, data in self.users:
            offsets[h] = at
            at += len(data)
        cond = at
        names = cond + len(self.conditions)
        out = bytearray(self.header)
        hashes = sorted(offsets)
        out += struct.pack(f"<{n}I", *hashes)
        out += bytes(table_at - len(out))
        out += struct.pack(f"<{n}Q", *(offsets[h] for h in hashes))
        out += self.define + self.records + self.overwrite + self.locals + direct + self.misc
        out += b"".join(data for _, data in self.users)
        out += self.conditions + self.names
        out += bytes(-len(out) % 8)
        struct.pack_into("<I", out, 4, len(out))
        struct.pack_into("<QQ", out, 0x18, trigger, local)
        struct.pack_into("<I", out, 0x30, len(direct) // 4)
        struct.pack_into("<Q", out, 0x40, users)
        struct.pack_into("<I", out, 0x48, n)
        struct.pack_into("<QQ", out, 0x50, cond, names)
        return bytes(out)


def _align(n: int, a: int) -> int:
    return (n + a - 1) // a * a


def decode(data: bytes) -> Elink:
    return Elink(data)
