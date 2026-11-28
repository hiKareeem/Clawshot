"""Synthetic effect files for tests, built in code (hard rule 1): an ELink table (XLNK 36) and a Vfx3 binary
(``BFFH``) shaped as plans/song-get-effects.md lays them out. Shared by the format tests and the song step's tests."""

import struct
import zlib
from dataclasses import dataclass

USER_PARAMS = ["UP0", "UP1", "UP2", "UP3"]
ASSET_PARAMS = [
    "AssetName",
    "RuntimeAssetName",
    "Bone",
    "Scale",
    "PositionX",
    "PositionY",
    "PositionZ",
    "RotationX",
    "Red",
    "Green",
    "Blue",
    "LifeScale",
    "BitFlag",
]
TRIGGER_PARAMS = ["TP0"]
BIT = {name: i for i, name in enumerate(ASSET_PARAMS)}
CONDITIONS = bytes(range(64))
TRIGGERS = bytes(range(100, 132))  # a user's trigger table, opaque to the module
NAME = 1 << 24


@dataclass(frozen=True)
class ActionTable:
    """A user's trigger table of action triggers, laid out as the game's (slots, actions, 0x28-byte triggers; counts in
    the user header): ``slots`` = ((slot, ((action, (call index, ...)), ...)), ...). ``always`` only sets the header's
    always-trigger count (no rows), for refusals."""

    slots: tuple[tuple[str, tuple[tuple[str, tuple[int, ...]], ...]], ...]
    always: int = 0


# Obj_Heart_Container's action triggers (dump 1.1.1): AS[Lower] Rotate_Obj -> Wait, Skl[Lower] Rotate_GetDemo -> GetDemo
HEART_ACTIONS = ActionTable((("AS[Lower]", (("Rotate_Obj", (0,)),)), ("Skl[Lower]", (("Rotate_GetDemo", (1,)),))))


def action_table(table: ActionTable, user: str, names) -> tuple[bytes, tuple[int, ...]]:
    """The trigger table bytes and the six header counts (slots, actions, triggers, properties, property triggers,
    always triggers)."""
    slot_rows, action_rows, trigger_rows = bytearray(), bytearray(), bytearray()
    n_action = n_trigger = 0
    for slot, actions in table.slots:
        slot_rows += struct.pack("<QHHI", names(slot), n_action, n_action + len(actions) - 1, 0)
        for action, calls in actions:
            action_rows += struct.pack("<QII", names(action), n_trigger, n_trigger + len(calls) - 1)
            for call in calls:
                guid = zlib.crc32(f"{user}#{action}#{call}".encode())
                trigger_rows += struct.pack(
                    "<IIQIIIHHII", guid, 0, 0x30 * call, 0, 0, 0x7FFFFFFF, 5, 0x4C8D, 0xFFFFFFFF, 0
                )
            n_action += 1
            n_trigger += len(calls)
    counts = (len(table.slots), n_action, n_trigger, 0, 0, table.always)
    return bytes(slot_rows + action_rows + trigger_rows), counts


# user -> calls (key, parameters: str = a name, int = a raw value, condition), trigger table
Calls = list[tuple[str, dict[str, str | int], int]]
DEFAULT_USERS: dict[str, tuple[Calls, bytes]] = {
    "Obj_Donor": (
        [
            ("Wait", {"AssetName": "Wait", "Bone": "Root", "BitFlag": 0x05000004}, 0x10),
            ("Get", {"AssetName": "Get", "RuntimeAssetName": "Fx_A", "Scale": 1}, 0x20),
        ],
        TRIGGERS,
    ),
    "Obj_Other": ([("Wait", {"AssetName": "Wait", "Bone": "Root", "BitFlag": 0x05000004}, 0x10)], b""),
    "Obj_Third": ([("Appear", {"AssetName": "Get", "RuntimeAssetName": "Fx_A", "Scale": 1}, 0x18)], TRIGGERS[:8]),
}
# Obj_Heart_Container's calls as the record lists them (plans/song-get-effects.md, "How it is built").
HEART_USERS: dict[str, tuple[Calls, bytes]] = {
    "Obj_Heart_Container": (
        [
            ("Wait", {"AssetName": "Wait", "Bone": "Root", "BitFlag": 0x05000004, "Scale": 1}, 0x10),
            ("GetDemo", {"AssetName": "GetDemo", "Bone": "Skl_Root", "BitFlag": 0x05000004, "PositionY": 2}, 0x20),
            ("Item_Drop", {"AssetName": "Item_Drop", "BitFlag": 0x05000004}, 0x18),
        ],
        TRIGGERS,
    ),
    "Obj_Rupee_Red": ([("Wait", {"AssetName": "Wait", "Bone": "Root"}, 0x10)], b""),
}
# The same with the heart container's real action triggers (event-items D20).
HEART_ACTION_USERS: dict[str, tuple[Calls, bytes | ActionTable]] = {
    "Obj_Heart_Container": (HEART_USERS["Obj_Heart_Container"][0], HEART_ACTIONS),
    "Obj_Rupee_Red": HEART_USERS["Obj_Rupee_Red"],
}


class Names:
    def __init__(self):
        self.blob = bytearray()
        self.at: dict[str, int] = {}

    def __call__(self, text: str) -> int:
        if text not in self.at:
            self.at[text] = len(self.blob)
            self.blob += text.encode() + b"\0"
        return self.at[text]


def define_table() -> bytes:
    strings = bytearray()
    entries = bytearray()
    for name in USER_PARAMS + ASSET_PARAMS + TRIGGER_PARAMS:
        entries += struct.pack("<QQQ", len(strings), 0, 0)
        strings += name.encode() + b"\0"
    body = bytearray(struct.pack("<6I", 0, len(USER_PARAMS), len(ASSET_PARAMS), 0, len(TRIGGER_PARAMS), 0))
    body += entries + strings
    body += bytes(-len(body) % 8)
    struct.pack_into("<I", body, 0, len(body))
    return bytes(body)


def user(name: str, calls: list[tuple], names: Names, triggers: "bytes | ActionTable" = b"") -> bytes:
    """calls: (key, asset id, flag, parent, record position, condition); triggers: opaque bytes or an
    :class:`ActionTable`."""
    n_asset = sum(1 for c in calls if c[2] == 0)
    head = bytearray(0x38)
    struct.pack_into("<IIII", head, 4, 1, len(calls), n_asset, 0)  # one local property
    if isinstance(triggers, ActionTable):
        triggers, counts = action_table(triggers, name, names)
        struct.pack_into("<6I", head, 0x14, *counts)
    local = struct.pack("<Q", names("LocalProp"))
    params = bytes(16)
    order = sorted(range(len(calls)), key=lambda i: calls[i][0].encode())
    ids = struct.pack(f"<{len(calls)}H", *order)
    ids += bytes(-len(ids) % 4)
    body = bytearray()
    for key, asset, flag, parent, pos, cond in calls:
        body += struct.pack(
            "<QhHiiIIIQQ",
            names(key),
            asset,
            flag,
            1,
            parent,
            zlib.crc32(f"{name}/{key}".encode()),
            zlib.crc32(key.encode()),
            0,
            pos,
            cond,
        )
    out = head + local + params + ids + body
    struct.pack_into("<Q", out, 0x30, len(out))
    out += triggers
    return bytes(out + bytes(-len(out) % 8))


def build_table(users: dict[str, tuple[Calls, "bytes | ActionTable"]] = DEFAULT_USERS) -> bytes:
    """An XLNK 36 table holding ``users``; equal parameter sets share one record, as in the game's tables."""
    names = Names()
    for text in ("Root", "Fx_A", "Fx_B"):
        names(text)
    records = bytearray()
    shared: dict[tuple, int] = {}

    def record(values: dict[str, str | int]) -> int:
        raw = {BIT[k]: (NAME | names(v)) if isinstance(v, str) else v for k, v in values.items()}
        key = tuple(sorted(raw.items()))
        if key not in shared:
            shared[key] = len(records)
            bits = sorted(raw)
            rec = struct.pack("<Q", sum(1 << b for b in bits)) + b"".join(struct.pack("<I", raw[b]) for b in bits)
            records.extend(rec + bytes(-len(rec) % 8))
        return shared[key]

    bodies = {}
    for name, (calls, triggers) in users.items():
        rows = [(key, i, 0, -1, record(values), cond) for i, (key, values, cond) in enumerate(calls)]
        bodies[name] = user(name, rows, names, triggers)
    for name in users:
        names(name)
    direct = struct.pack("<4f", 0.5, 1.0, -0.21, 1.0)
    order = sorted(bodies, key=lambda n: zlib.crc32(n.encode()))
    n = len(order)
    header = bytearray(0x60)
    header[0:4] = b"XLNK"
    table_at = 0x60 + 4 * n
    table_at += -table_at % 8
    define = table_at + 8 * n
    define_bytes = define_table()
    trig = define + len(define_bytes) + len(records)
    overwrite = bytes(16)
    local = trig + len(overwrite)
    locals_bytes = struct.pack("<QQ", 0, 0)  # one local property name, one enum
    misc = b"MISCDATA"
    users_at = local + len(locals_bytes) + len(direct) + len(misc)
    offsets = {}
    at = users_at
    for name in order:
        offsets[name] = at
        at += len(bodies[name])
    cond = at
    names_at = cond + len(CONDITIONS)
    struct.pack_into("<I", header, 8, 36)
    struct.pack_into("<QQ", header, 0x18, trig, local)
    struct.pack_into("<III", header, 0x28, 1, 1, len(direct) // 4)
    struct.pack_into("<Q", header, 0x40, users_at)
    struct.pack_into("<I", header, 0x48, n)
    struct.pack_into("<QQ", header, 0x50, cond, names_at)
    out = bytearray(header)
    out += struct.pack(f"<{n}I", *(zlib.crc32(name.encode()) for name in order))
    out += bytes(table_at - len(out))
    out += struct.pack(f"<{n}Q", *(offsets[name] for name in order))
    out += define_bytes + records + overwrite + locals_bytes + direct + misc
    out += b"".join(bodies[name] for name in order)
    out += CONDITIONS + names.blob
    out += bytes(-len(out) % 8)
    struct.pack_into("<I", out, 4, len(out))
    return bytes(out)


EFFECTS = {"Fx_A": ["Em0", "Em1", "Em2"], "Fx_B": ["Em0", "Em3"]}
EMITTER = 0x40


def build_bffh(effects: dict[str, list[str]] = EFFECTS) -> bytes:
    """A minimal BFFH: header, BFSI Default and StringPool, root at 0x1000, effect table, one data region per
    effect (emitter list, emitter objects with a pointer into themselves, a second vector), string pool."""
    pool = bytearray()
    pool_at: dict[str, int] = {}

    def text(s: str) -> int:  # relative to the pool start, fixed up below
        if s not in pool_at:
            pool_at[s] = len(pool)
            pool.extend(s.encode() + b"\0")
        return pool_at[s]

    regions = []
    at = 0x10000
    for name, emitters in effects.items():
        r = bytearray()
        n = len(emitters)
        list_at = at
        objs_at = list_at + 8 * n
        extra_at = objs_at + EMITTER * n
        r += b"".join(struct.pack("<Q", objs_at + EMITTER * k) for k in range(n))
        for k, em in enumerate(emitters):
            obj = bytearray(EMITTER)
            struct.pack_into("<Q", obj, 0, text(em))  # pool-relative; fixed up below
            struct.pack_into("<QII", obj, 8, objs_at + EMITTER * k + 0x20, 2, 8)  # a vector inside itself
            struct.pack_into("<ff", obj, 0x20, 1.5 + k, 0.25)
            r += obj
        r += struct.pack("<QQ", 0x12345678, 0x9ABC)  # data
        r += bytes(-len(r) % 0x100)
        regions.append((name, list_at, n, extra_at, r))
        at += len(r)
    pool0 = at
    blob = bytearray(pool0)
    blob[0:4] = b"BFFH"
    struct.pack_into("<III", blob, 0x0C, 0x1000, 0xA8, 0)
    struct.pack_into("<II", blob, 0x18, 2, 0x28)
    for i, (sec, off) in enumerate((("Default", 0x1000), ("StringPool", pool0))):
        rec = 0xA8 + 0x28 * i
        blob[rec : rec + 4] = b"BFSI"
        struct.pack_into("<IIIQ", blob, rec + 4, off, 0, 0x1000 if sec == "Default" else 1, off)
        blob[rec + 0x18 : rec + 0x18 + len(sec)] = sec.encode()
    table = 0x1100
    struct.pack_into("<QII", blob, 0x1000 + 0x30, table, len(regions), 0x68)
    for i, (name, list_at, n, extra_at, r) in enumerate(regions):
        blob[list_at : list_at + len(r)] = r
        entry = table + 0x68 * i
        struct.pack_into("<QQII", blob, entry, pool0 + text(name), list_at, n, 8)
        struct.pack_into("<QII", blob, entry + 0x18, extra_at, 1, 8)
        for k in range(n):  # emitter names: pool-relative -> absolute
            obj = list_at + 8 * n + EMITTER * k
            struct.pack_into("<Q", blob, obj, pool0 + struct.unpack_from("<Q", blob, obj)[0])
    blob += pool
    blob += bytes(-len(blob) % 0x10)
    struct.pack_into("<I", blob, 8, len(blob))
    struct.pack_into("<I", blob, 0xA8 + 0x28 + 8, len(blob) - pool0)
    struct.pack_into("<I", blob, 0xA8 + 8, pool0 - 0x1000)
    return bytes(blob)
