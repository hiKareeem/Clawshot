"""Event flows (``Event/EventFlow/*.bfevfl``): read and write.

Written from the files themselves and from the public description of the format on the ZeldaMods wiki
(https://zeldamods.org/wiki/BFEVFL, revision 11752, written for *Breath of the Wild*'s files). No code from any other
implementation. This game (build ``e0f3ccfa``) writes version 0.4.0.0, little-endian, which differs from the wiki in
these ways, found in the dump:

- An event is 0x30 bytes, not 0x28, and there are two more event types: 5 calls an entry point and branches on the
  value it returns (cases as for a switch, then the sub flow's flowchart and entry point names, the second at 0x28),
  and 6 ends an entry point returning a 32-bit value (at 0xc). The official names are unknown; here they are
  :class:`SubFlowSwitchEvent` and :class:`ReturnEvent`.
- An entry point's variable definitions are 0x10 bytes: an 8-byte value, a u16 count (1), a u16 type (container
  types 2 int, 3 bool, 4 float). An entry point without variables still owns an empty dictionary of 0x18 zero bytes.
- A string-like container item (String, Argument, Actor identifier) holds pointers to its strings, which follow it.
- The string pool (``STR ``) holds every name once, sorted by its bits read from the last byte's lowest bit
  (:func:`_bit_key`, the order the radix-tree dictionaries compare in), after a 0x14-byte header that ends with the
  count and an empty string.
- A file holds one flowchart (653 of 914) or one timeline (261), never both; no timeline has oneshots.

Layout, as the writer reproduces it: header; flowchart pointer array and dictionary; timeline pointer array and
dictionary; then the flowchart (header, actors, events, entry point dictionary, entry points, then per event its
cases or fork indices and parameters, per actor its parameters and action and query names, per entry point its sub
flow indices and variables) or the timeline (per actor its parameters and names, then the header, actors, clips,
subtimelines, triggers, cuts and the clips' parameters); the string pool; the relocation table, which lists every
array pointer even when null and an optional object's pointer only when set. Sections start 8-aligned.

A file is read into plain objects (:class:`EventFlowFile`, :class:`Flowchart`, :class:`Timeline`, events, actors,
entry points, parameter containers as ``dict``) and written back in that layout, so that every flow in the dump
writes back byte-identical (``tests/test_evfl_dump.py``). References between events, actors and entry points are
indices, as in the file; :data:`NONE` (0xFFFF) means none.

Parameter values keep their container type: ``int`` (Int), ``bool`` (Bool), ``float`` (Float, binary32), ``str``
(String), :class:`Argument` (an argument name), :class:`FloatArray` and :class:`ActorIdentifier`; a nested ``dict``
is a Container.
"""

import struct
from dataclasses import dataclass, field

MAGIC = b"BFEVFL\x00\x00"
VERSION = (0, 4, 0, 0)
ALIGNMENT_SHIFT = 3
NONE = 0xFFFF  # an absent event, actor, action or entry point index

ACTION, SWITCH, FORK, JOIN, SUB_FLOW, SUB_FLOW_SWITCH, RETURN = range(7)

# Container item types (the wiki's ContainerDataType). The game's flows use 0-5, 9 and 12; the others (6 wide
# string, 7 int array, 8 bool array, 10 string array, 11 wide string array) are not read or written.
T_ARGUMENT, T_CONTAINER, T_INT, T_BOOL, T_FLOAT, T_STRING = range(6)
T_FLOAT_ARRAY = 9
T_ACTOR_IDENTIFIER = 12

_TRUE = 0x80000001  # a Bool item's value when true


class EvflError(ValueError):
    pass


# --- parameter values ---------------------------------------------------------------------------------------------


class Argument(str):
    """A parameter whose value is the name of a flow argument (container type 0)."""

    def __repr__(self) -> str:
        return f"Argument({str.__repr__(self)})"


@dataclass(frozen=True)
class ActorIdentifier:
    name: str
    secondary_name: str = ""


class FloatArray(tuple):
    """A float array (container type 9)."""

    def __repr__(self) -> str:
        return f"FloatArray({tuple.__repr__(self)})"


def value_type(value: object) -> int:
    """The container type a parameter value is written as."""
    if isinstance(value, dict):
        return T_CONTAINER
    if isinstance(value, Argument):
        return T_ARGUMENT
    if isinstance(value, str):
        return T_STRING
    if isinstance(value, bool):
        return T_BOOL
    if isinstance(value, int):
        return T_INT
    if isinstance(value, float):
        return T_FLOAT
    if isinstance(value, FloatArray):
        return T_FLOAT_ARRAY
    if isinstance(value, ActorIdentifier):
        return T_ACTOR_IDENTIFIER
    raise EvflError(f"not a parameter value: {value!r} ({type(value).__name__})")


# --- the tree -----------------------------------------------------------------------------------------------------


@dataclass
class Actor:
    name: str
    secondary_name: str = ""
    argument_name: str = ""
    actions: list[str] = field(default_factory=list)
    queries: list[str] = field(default_factory=list)
    params: dict | None = None
    entry_point: int = NONE  # index of the entry point this actor belongs to
    cut_number: int = 1


@dataclass
class ActionEvent:
    name: str
    actor: int
    action: int  # index into the actor's actions
    next: int = NONE
    params: dict | None = None


@dataclass
class SwitchEvent:
    name: str
    actor: int
    query: int  # index into the actor's queries
    cases: list[tuple[int, int]] = field(default_factory=list)  # (value, event index)
    params: dict | None = None


@dataclass
class ForkEvent:
    name: str
    join: int
    forks: list[int] = field(default_factory=list)


@dataclass
class JoinEvent:
    name: str
    next: int = NONE


@dataclass
class SubFlowEvent:
    name: str
    flowchart: str  # "" for this file's flowchart
    entry_point: str
    next: int = NONE
    params: dict | None = None


@dataclass
class SubFlowSwitchEvent:
    """Type 5: calls ``flowchart``:``entry_point`` and branches on the value a :class:`ReturnEvent` there gives."""

    name: str
    flowchart: str
    entry_point: str
    cases: list[tuple[int, int]] = field(default_factory=list)  # (returned value, event index)
    params: dict | None = None


@dataclass
class ReturnEvent:
    """Type 6: ends the entry point, returning ``value`` to a :class:`SubFlowSwitchEvent`."""

    name: str
    value: int


Event = ActionEvent | SwitchEvent | ForkEvent | JoinEvent | SubFlowEvent | SubFlowSwitchEvent | ReturnEvent


@dataclass
class Variable:
    """An entry point's variable definition: container type ``type`` (2 int, 3 bool, 4 float) and its value."""

    type: int
    value: int | bool | float


@dataclass
class EntryPoint:
    name: str
    main_event: int = NONE
    sub_flow_events: list[int] = field(default_factory=list)
    variables: dict[str, Variable] = field(default_factory=dict)


@dataclass
class Flowchart:
    name: str
    actors: list[Actor] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    entry_points: list[EntryPoint] = field(default_factory=list)

    def entry_point(self, name: str) -> EntryPoint:
        for entry in self.entry_points:
            if entry.name == name:
                return entry
        raise KeyError(name)


@dataclass
class Clip:
    start: float
    duration: float
    actor: int
    action: int
    unknown: int = 0  # the byte at 0xc
    params: dict | None = None


@dataclass
class Trigger:
    clip: int
    type: int  # 1 enter, 2 leave


@dataclass
class Cut:
    start: float
    unknown: int  # the u32 at 0x4
    name: str
    params: dict | None = None


@dataclass
class Timeline:
    name: str
    duration: float
    actors: list[Actor] = field(default_factory=list)
    clips: list[Clip] = field(default_factory=list)
    triggers: list[Trigger] = field(default_factory=list)
    subtimelines: list[str] = field(default_factory=list)
    cuts: list[Cut] = field(default_factory=list)
    params: dict | None = None


@dataclass
class EventFlowFile:
    name: str
    flowchart: Flowchart | None = None
    timeline: Timeline | None = None


# --- reading ------------------------------------------------------------------------------------------------------

_HEADER = struct.Struct("<8s4BHBBIHHIIHHI4Q")  # 0x48 bytes
_FLOWCHART = struct.Struct("<4sIII5H3H5Q")  # 0x48
_TIMELINE = struct.Struct("<4sIIIf6H8Q")  # 0x60
_ACTOR = struct.Struct("<6QHHHBB")  # 0x38
_EVENT = struct.Struct("<QBBHHH4Q")  # 0x30
_ENTRY_POINT = struct.Struct("<3QHHHH")  # 0x20
_VARIABLE = struct.Struct("<QHHI")  # 0x10
_CLIP = struct.Struct("<ffHHB3xQ")  # 0x18
_TRIGGER = struct.Struct("<HBB")  # 4
_CUT = struct.Struct("<fIQQ")  # 0x18
_ITEM = struct.Struct("<BBHIQ")  # 0x10, a container item's header
_DIC_ENTRY = struct.Struct("<IHHQ")  # 0x10


class _Reader:
    def __init__(self, data: bytes):
        self.data = data

    def u16(self, off: int) -> int:
        return struct.unpack_from("<H", self.data, off)[0]

    def u32(self, off: int) -> int:
        return struct.unpack_from("<I", self.data, off)[0]

    def ptr(self, off: int) -> int:
        return struct.unpack_from("<Q", self.data, off)[0]

    def string(self, off: int) -> str:
        """The pascal string at ``off`` (a u16 length, then the bytes)."""
        if not 0 < off < len(self.data):
            raise EvflError(f"string pointer 0x{off:x} outside the file")
        n = self.u16(off)
        return self.data[off + 2 : off + 2 + n].decode("utf-8")

    def dictionary(self, off: int) -> list[str]:
        """The names of a dictionary (``DIC ``), in entry order."""
        if self.data[off : off + 4] != b"DIC ":
            raise EvflError(f"no dictionary at 0x{off:x}")
        n = self.u32(off + 4)
        return [self.string(_DIC_ENTRY.unpack_from(self.data, off + 0x18 + 0x10 * i)[3]) for i in range(n)]

    def container(self, off: int) -> dict | None:
        if off == 0:
            return None
        value = self.item(off)
        if not isinstance(value, dict):
            raise EvflError(f"parameters at 0x{off:x} are not a container")
        return value

    def item(self, off: int):
        t, _, n, _, dic = _ITEM.unpack_from(self.data, off)
        p = off + 0x10
        if t == T_CONTAINER:
            names = self.dictionary(dic)
            if len(names) != n:
                raise EvflError(f"container at 0x{off:x}: {n} items, {len(names)} names")
            return {name: self.item(self.ptr(p + 8 * i)) for i, name in enumerate(names)}
        if t == T_ARGUMENT:
            return Argument(self.string(self.ptr(p)))
        if t == T_STRING:
            return self.string(self.ptr(p))
        if t == T_INT:
            return struct.unpack_from("<i", self.data, p)[0]
        if t == T_BOOL:
            raw = self.u32(p)
            if raw not in (0, _TRUE):
                raise EvflError(f"bool at 0x{off:x} is 0x{raw:x}")
            return raw == _TRUE
        if t == T_FLOAT:
            return struct.unpack_from("<f", self.data, p)[0]
        if t == T_FLOAT_ARRAY:
            return FloatArray(struct.unpack_from(f"<{n}f", self.data, p))
        if t == T_ACTOR_IDENTIFIER:
            return ActorIdentifier(self.string(self.ptr(p)), self.string(self.ptr(p + 8)))
        raise EvflError(f"container item at 0x{off:x}: unsupported type {t}")

    def actors(self, off: int, n: int) -> list[Actor]:
        out = []
        for i in range(n):
            name, sec, arg, actions, queries, params, na, nq, entry, cut, _ = _ACTOR.unpack_from(
                self.data, off + _ACTOR.size * i
            )
            out.append(
                Actor(
                    name=self.string(name),
                    secondary_name=self.string(sec),
                    argument_name=self.string(arg),
                    actions=[self.string(self.ptr(actions + 8 * j)) for j in range(na)],
                    queries=[self.string(self.ptr(queries + 8 * j)) for j in range(nq)],
                    params=self.container(params),
                    entry_point=entry,
                    cut_number=cut,
                )
            )
        return out

    def cases(self, off: int, n: int) -> list[tuple[int, int]]:
        return [struct.unpack_from("<IHxx", self.data, off + 8 * i) for i in range(n)]

    def event(self, off: int) -> Event:
        name_p, t, _, a, b, c, p10, p18, p20, p28 = _EVENT.unpack_from(self.data, off)
        name = self.string(name_p)
        if t == ACTION:
            return ActionEvent(name, actor=b, action=c, next=a, params=self.container(p10))
        if t == SWITCH:
            return SwitchEvent(name, actor=b, query=c, cases=self.cases(p18, a), params=self.container(p10))
        if t == FORK:
            return ForkEvent(name, join=b, forks=[self.u16(p10 + 2 * i) for i in range(a)])
        if t == JOIN:
            return JoinEvent(name, next=a)
        if t == SUB_FLOW:
            return SubFlowEvent(name, self.string(p18), self.string(p20), next=a, params=self.container(p10))
        if t == SUB_FLOW_SWITCH:
            return SubFlowSwitchEvent(
                name, self.string(p20), self.string(p28), cases=self.cases(p18, a), params=self.container(p10)
            )
        if t == RETURN:
            return ReturnEvent(name, value=b | c << 16)
        raise EvflError(f"event {name} at 0x{off:x}: unknown type {t}")

    def entry_points(self, dic: int, off: int, n: int) -> list[EntryPoint]:
        names = self.dictionary(dic) if n else []
        if len(names) != n:
            raise EvflError(f"{n} entry points, {len(names)} names")
        out = []
        for i, name in enumerate(names):
            subs, var_dic, var_off, nsub, nvar, main, _ = _ENTRY_POINT.unpack_from(self.data, off + 0x20 * i)
            variables = {}
            for j, var_name in enumerate(self.dictionary(var_dic) if nvar else []):
                raw, count, t, _ = _VARIABLE.unpack_from(self.data, var_off + 0x10 * j)
                if count != 1 or t not in (T_INT, T_BOOL, T_FLOAT):
                    raise EvflError(f"entry point {name}: variable {var_name} of type {t}, count {count}")
                variables[var_name] = Variable(t, _variable_value(t, raw))
            out.append(
                EntryPoint(
                    name,
                    main_event=main,
                    sub_flow_events=[self.u16(subs + 2 * j) for j in range(nsub)],
                    variables=variables,
                )
            )
        return out

    def flowchart(self, off: int) -> Flowchart:
        magic, _, _, _, na, _, _, ne, nep, _, _, _, name, actors, events, dic, eps = _FLOWCHART.unpack_from(
            self.data, off
        )
        if magic != b"EVFL":
            raise EvflError(f"no flowchart at 0x{off:x}")
        return Flowchart(
            name=self.string(name),
            actors=self.actors(actors, na),
            events=[self.event(events + _EVENT.size * i) for i in range(ne)],
            entry_points=self.entry_points(dic, eps, nep),
        )

    def timeline(self, off: int) -> Timeline:
        (magic, _, _, _, duration, na, _, nclip, nshot, nsub, ncut, name, actors, clips, _, triggers, subs, cuts,
         params) = _TIMELINE.unpack_from(self.data, off)  # fmt: skip
        if magic != b"TLIN":
            raise EvflError(f"no timeline at 0x{off:x}")
        if nshot:
            raise EvflError(f"timeline at 0x{off:x} has {nshot} oneshots; the game's timelines have none")
        out = Timeline(name=self.string(name), duration=duration, actors=self.actors(actors, na))
        for i in range(nclip):
            start, length, actor, action, unknown, p = _CLIP.unpack_from(self.data, clips + _CLIP.size * i)
            out.clips.append(Clip(start, length, actor, action, unknown, self.container(p)))
        for i in range(2 * nclip):
            clip, t, _ = _TRIGGER.unpack_from(self.data, triggers + _TRIGGER.size * i)
            out.triggers.append(Trigger(clip, t))
        out.subtimelines = [self.string(self.ptr(subs + 8 * i)) for i in range(nsub)]
        for i in range(ncut):
            start, unknown, name_p, p = _CUT.unpack_from(self.data, cuts + _CUT.size * i)
            out.cuts.append(Cut(start, unknown, self.string(name_p), self.container(p)))
        out.params = self.container(params)
        return out


def _variable_value(t: int, raw: int):
    if t == T_BOOL:
        return bool(raw)
    if t == T_FLOAT:
        return struct.unpack("<f", struct.pack("<I", raw & 0xFFFFFFFF))[0]
    return struct.unpack("<q", struct.pack("<Q", raw))[0]


def _align(n: int, a: int) -> int:
    return (n + a - 1) & -a


def read(data: bytes) -> EventFlowFile:
    """Parse a decompressed ``.bfevfl``."""
    if len(data) < _HEADER.size:
        raise EvflError("file shorter than the header")
    (magic, *version, bom, shift, _, name, _, _, _, size, nfc, ntl, _, fcs, _, tls, _) = _HEADER.unpack_from(data)
    if magic != MAGIC:
        raise EvflError(f"not an event flow: magic {magic!r}")
    if tuple(version) != VERSION or bom != 0xFEFF or shift != ALIGNMENT_SHIFT:
        raise EvflError(f"unsupported version {version}, byte order 0x{bom:x} or alignment {shift}")
    if size != len(data):
        raise EvflError(f"header says {size} bytes, file has {len(data)}")
    if nfc + ntl != 1:
        raise EvflError(f"{nfc} flowcharts and {ntl} timelines; the game's files hold exactly one of either")
    r = _Reader(data)
    file_name = r.string(name - 2)
    return EventFlowFile(
        name=file_name,
        flowchart=r.flowchart(r.ptr(fcs)) if nfc else None,
        timeline=r.timeline(r.ptr(tls)) if ntl else None,
    )


# --- writing ------------------------------------------------------------------------------------------------------

_BIT_REVERSED = bytes(int(f"{i:08b}"[::-1], 2) for i in range(256))
_EMPTY_DICTIONARY_SIZE = 0x18  # an entry point without variables still owns this many zero bytes


def _bit(key: bytes, i: int) -> int:
    """Bit ``i`` of a name as the dictionaries count them: from the lowest bit of the last byte."""
    k = i >> 3
    return key[-1 - k] >> (i & 7) & 1 if k < len(key) else 0


def _bit_key(s: str) -> bytes:
    """A sort key giving the string pool's order: the bits of ``s`` read from the lowest bit of its last byte."""
    return bytes(_BIT_REVERSED[b] for b in reversed(s.encode("utf-8")))


def dictionary_entries(names: list[str]) -> list[tuple[int, int, int]]:
    """The radix-tree entries (bit index, child for 0, child for 1) of a dictionary of ``names``, root first.

    Each name is inserted in order as in a PATRICIA tree: it hangs below the last node that tests a lower bit than
    the first bit in which it differs from the name its search ends at. The root tests no bit (0xFFFFFFFF)."""
    keys = [b""]
    bits = [-1]
    children = [[0, 0]]
    for index, name in enumerate(names, 1):
        key = name.encode("utf-8")
        prev, cur = 0, children[0][0]
        while bits[prev] < bits[cur]:
            prev, cur = cur, children[cur][_bit(key, bits[cur])]
        other = keys[cur]
        differ = next((i for i in range(8 * max(len(key), len(other))) if _bit(key, i) != _bit(other, i)), None)
        if differ is None:
            raise EvflError(f"dictionary name {name!r} twice")
        prev, cur = 0, children[0][0]
        while bits[prev] < bits[cur] < differ:
            prev, cur = cur, children[cur][_bit(key, bits[cur])]
        side = _bit(key, differ)
        keys.append(key)
        bits.append(differ)
        children.append([cur, index] if side else [index, cur])
        children[prev][_bit(key, bits[prev]) if prev else 0] = index
    return [(b & 0xFFFFFFFF, c[0], c[1]) for b, c in zip(bits, children, strict=True)]


class _Writer:
    def __init__(self):
        self.buf = bytearray()
        self.relocations: list[int] = []
        self.string_fields: dict[str, list[int]] = {}

    def pos(self) -> int:
        return len(self.buf)

    def align(self, a: int = 8) -> None:
        self.buf += bytes(_align(len(self.buf), a) - len(self.buf))

    def reserve(self, size: int) -> int:
        off = len(self.buf)
        self.buf += bytes(size)
        return off

    def put(self, off: int, fmt: str, *values) -> None:
        struct.pack_into("<" + fmt, self.buf, off, *values)

    def pointer(self, field_off: int, target: int, *, relocate: bool = True) -> None:
        """A pointer field; :meth:`write` lists it for relocation when ``relocate``, null or not, as the game's
        files do for array fields (an optional object's field is relocated only when it is set)."""
        self.put(field_off, "Q", target)
        if relocate:
            self.relocations.append(field_off)

    def optional(self, field_off: int, target: int) -> None:
        if target:
            self.pointer(field_off, target)

    def string(self, field_off: int, s: str) -> None:
        """A pointer to ``s`` in the string pool, filled in when the pool is written."""
        self.string_fields.setdefault(s, []).append(field_off)
        self.relocations.append(field_off)

    def inline_string(self, s: str) -> int:
        off = self.pos()
        raw = s.encode("utf-8")
        if len(raw) > 0xFFFF:
            raise EvflError(f"string of {len(raw)} bytes")
        self.buf += struct.pack("<H", len(raw)) + raw + b"\x00"
        return off

    def dictionary(self, names: list[str]) -> int:
        self.align()
        off = self.reserve(0x18 + 0x10 * len(names))
        self.put(off, "4sI", b"DIC ", len(names))
        for i, (bit, left, right) in enumerate(dictionary_entries(names)):
            entry = off + 8 + 0x10 * i
            self.put(entry, "IHH", bit, left, right)
            self.string(entry + 8, names[i - 1] if i else "")
        return off

    def item(self, value) -> int:
        self.align()
        t = value_type(value)
        off = self.pos()
        if t == T_CONTAINER:
            self.reserve(0x10 + 8 * len(value))
            self.put(off, "BBHI", t, 0, len(value), 0)
            self.pointer(off + 8, self.dictionary(list(value)))
            for i, child in enumerate(value.values()):
                self.pointer(off + 0x10 + 8 * i, self.item(child))
        elif t in (T_ARGUMENT, T_STRING):
            self.reserve(0x18)
            self.put(off, "BBHI", t, 0, 1, 0)
            self.pointer(off + 0x10, self.inline_string(value))
        elif t == T_ACTOR_IDENTIFIER:
            self.reserve(0x20)
            self.put(off, "BBHI", t, 0, 2, 0)
            self.pointer(off + 0x10, self.inline_string(value.name))
            self.align(2)
            self.pointer(off + 0x18, self.inline_string(value.secondary_name))
        elif t == T_FLOAT_ARRAY:
            self.reserve(0x10)
            self.put(off, "BBHI", t, 0, len(value), 0)
            self.buf += struct.pack(f"<{len(value)}f", *value)
        else:
            self.reserve(0x18)
            self.put(off, "BBHI", t, 0, 1, 0)
            if t == T_BOOL:
                self.put(off + 0x10, "I", _TRUE if value else 0)
            else:
                self.put(off + 0x10, "i" if t == T_INT else "f", value)
        self.align()
        return off

    def container(self, field_off: int, params: dict | None) -> None:
        if params is not None:
            if not isinstance(params, dict):
                raise EvflError(f"parameters must be a dict, not {type(params).__name__}")
            self.pointer(field_off, self.item(params))

    def u16_array(self, field_off: int, values: list[int]) -> None:
        self.align()
        off = self.pos() if values else 0
        self.buf += struct.pack(f"<{len(values)}H", *values)
        self.pointer(field_off, off)

    def cases(self, field_off: int, cases: list[tuple[int, int]]) -> None:
        self.align()
        off = self.pos() if cases else 0
        for value, event in cases:
            self.buf += struct.pack("<IHxx", value, event)
        self.pointer(field_off, off)

    def string_array(self, field_off: int, strings: list[str]) -> None:
        self.align()
        off = self.reserve(8 * len(strings)) if strings else 0
        for i, s in enumerate(strings):
            self.string(off + 8 * i, s)
        self.pointer(field_off, off)

    def actor_headers(self, actors: list[Actor]) -> int:
        return self.reserve(_ACTOR.size * len(actors)) if actors else 0

    def actor_data(self, off: int, actors: list[Actor]) -> None:
        """Each actor's fields, then its parameters and action and query name arrays."""
        for i, actor in enumerate(actors):
            a = off + _ACTOR.size * i
            self.put(a + 0x30, "HHHBB", len(actor.actions), len(actor.queries), actor.entry_point, actor.cut_number, 0)
            self.string(a, actor.name)
            self.string(a + 8, actor.secondary_name)
            self.string(a + 0x10, actor.argument_name)
            self.container(a + 0x28, actor.params)
            self.string_array(a + 0x18, actor.actions)
            self.string_array(a + 0x20, actor.queries)

    def event(self, off: int, event: Event) -> None:
        self.string(off, event.name)
        if isinstance(event, ActionEvent):
            self.put(off + 8, "BxHHH", ACTION, event.next, event.actor, event.action)
            self.container(off + 0x10, event.params)
        elif isinstance(event, SwitchEvent):
            self.put(off + 8, "BxHHH", SWITCH, len(event.cases), event.actor, event.query)
            self.cases(off + 0x18, event.cases)
            self.container(off + 0x10, event.params)
        elif isinstance(event, ForkEvent):
            self.put(off + 8, "BxHHH", FORK, len(event.forks), event.join, 0)
            self.u16_array(off + 0x10, event.forks)
        elif isinstance(event, JoinEvent):
            self.put(off + 8, "BxHHH", JOIN, event.next, 0, 0)
        elif isinstance(event, SubFlowEvent):
            self.put(off + 8, "BxHHH", SUB_FLOW, event.next, 0, 0)
            self.container(off + 0x10, event.params)
            self.string(off + 0x18, event.flowchart)
            self.string(off + 0x20, event.entry_point)
        elif isinstance(event, SubFlowSwitchEvent):
            self.put(off + 8, "BxHHH", SUB_FLOW_SWITCH, len(event.cases), 0, 0)
            self.cases(off + 0x18, event.cases)
            self.container(off + 0x10, event.params)
            self.string(off + 0x20, event.flowchart)
            self.string(off + 0x28, event.entry_point)
        elif isinstance(event, ReturnEvent):
            self.put(off + 8, "BxHI", RETURN, 0, event.value)
        else:
            raise EvflError(f"not an event: {event!r}")

    def entry_point_data(self, off: int, entry: EntryPoint) -> None:
        """The sub flow event indices, then the variables' dictionary (zeros when there are none) and values."""
        self.u16_array(off, entry.sub_flow_events)
        self.align()
        if entry.variables:
            self.pointer(off + 8, self.dictionary(list(entry.variables)))
            values = self.reserve(_VARIABLE.size * len(entry.variables))
            for i, var in enumerate(entry.variables.values()):
                self.put(values + _VARIABLE.size * i, "QHHI", _variable_raw(var), 1, var.type, 0)
            self.pointer(off + 0x10, values)
        else:
            self.reserve(_EMPTY_DICTIONARY_SIZE)
            self.pointer(off + 0x10, 0)

    def flowchart(self, fc: Flowchart) -> int:
        off = self.reserve(_FLOWCHART.size)
        self.put(off, "4s", b"EVFL")
        self.put(off + 0x10, "5H", len(fc.actors), *_action_counts(fc.actors), len(fc.events), len(fc.entry_points))
        self.string(off + 0x20, fc.name)
        actors = self.actor_headers(fc.actors)
        self.pointer(off + 0x28, actors)
        events = self.reserve(_EVENT.size * len(fc.events)) if fc.events else 0
        self.pointer(off + 0x30, events)
        self.pointer(off + 0x38, self.dictionary([e.name for e in fc.entry_points]))
        entries = self.reserve(_ENTRY_POINT.size * len(fc.entry_points)) if fc.entry_points else 0
        self.pointer(off + 0x40, entries)
        for i, entry in enumerate(fc.entry_points):
            self.put(entries + _ENTRY_POINT.size * i + 0x18, "HHHH", len(entry.sub_flow_events),
                     len(entry.variables), entry.main_event, 0)  # fmt: skip
        for i, event in enumerate(fc.events):
            self.event(events + _EVENT.size * i, event)
        self.actor_data(actors, fc.actors)
        for i, entry in enumerate(fc.entry_points):
            self.entry_point_data(entries + _ENTRY_POINT.size * i, entry)
        return off

    def timeline(self, tl: Timeline) -> int:
        """The actors' parameters and name arrays come first, then the timeline and its arrays."""
        actor_fields: list[tuple[int, int, int, int, int]] = []
        for actor in tl.actors:
            self.align()
            params = self.item(actor.params) if actor.params is not None else 0
            self.align()
            actions = self.pos() if actor.actions else 0
            action_fields = self.reserve(8 * len(actor.actions))
            self.align()
            queries = self.pos() if actor.queries else 0
            query_fields = self.reserve(8 * len(actor.queries))
            actor_fields.append((params, actions, action_fields, queries, query_fields))
        self.align()
        off = self.reserve(_TIMELINE.size)
        self.put(off, "4sIIIf", b"TLIN", 0, 0, 0, tl.duration)
        self.put(off + 0x14, "6H", len(tl.actors), _action_counts(tl.actors)[0], len(tl.clips), 0,
                 len(tl.subtimelines), len(tl.cuts))  # fmt: skip
        self.string(off + 0x20, tl.name)
        actors = self.actor_headers(tl.actors)
        self.pointer(off + 0x28, actors)
        for i, (actor, (params, actions, action_fields, queries, query_fields)) in enumerate(
            zip(tl.actors, actor_fields, strict=True)
        ):
            a = actors + _ACTOR.size * i
            self.put(a + 0x30, "HHHBB", len(actor.actions), len(actor.queries), actor.entry_point, actor.cut_number, 0)
            self.string(a, actor.name)
            self.string(a + 8, actor.secondary_name)
            self.string(a + 0x10, actor.argument_name)
            for j, name in enumerate(actor.actions):
                self.string(action_fields + 8 * j, name)
            for j, name in enumerate(actor.queries):
                self.string(query_fields + 8 * j, name)
            self.pointer(a + 0x18, actions)
            self.pointer(a + 0x20, queries)
            self.optional(a + 0x28, params)
        clips = self.reserve(_CLIP.size * len(tl.clips)) if tl.clips else 0
        self.pointer(off + 0x30, clips)
        self.pointer(off + 0x38, 0)  # oneshots: none in the game's timelines
        self.string_array(off + 0x48, tl.subtimelines)
        if len(tl.triggers) != 2 * len(tl.clips):
            raise EvflError(f"timeline {tl.name}: {len(tl.triggers)} triggers for {len(tl.clips)} clips (two each)")
        self.align()
        triggers = self.pos() if tl.triggers else 0
        for trigger in tl.triggers:
            self.buf += _TRIGGER.pack(trigger.clip, trigger.type, 0)
        self.pointer(off + 0x40, triggers)
        self.align()
        cuts = self.reserve(_CUT.size * len(tl.cuts)) if tl.cuts else 0
        self.pointer(off + 0x50, cuts)
        for i, clip in enumerate(tl.clips):
            c = clips + _CLIP.size * i
            self.put(c, "ffHHB", clip.start, clip.duration, clip.actor, clip.action, clip.unknown)
            self.container(c + 0x10, clip.params)
        for i, cut in enumerate(tl.cuts):
            c = cuts + _CUT.size * i
            self.put(c, "fI", cut.start, cut.unknown)
            self.string(c + 8, cut.name)
            self.container(c + 0x10, cut.params)
        self.container(off + 0x58, tl.params)
        return off

    def string_pool(self) -> tuple[int, dict[str, int]]:
        self.align()
        off = self.reserve(0x14)
        strings = sorted(set(self.string_fields) - {""}, key=_bit_key)
        self.put(off, "4s12xI", b"STR ", len(strings))
        where = {}
        for s in ["", *strings]:
            where[s] = self.inline_string(s)
            self.align(2)
        for s, fields in self.string_fields.items():
            for f in fields:
                self.put(f, "Q", where[s])
        return off, where

    def relocation_table(self, data_end: int) -> int:
        self.align()
        off = self.pos()
        entries = []
        pending = sorted(set(self.relocations))
        i = 0
        while i < len(pending):
            base, mask = pending[i], 0
            while i < len(pending) and pending[i] < base + 8 * 32:
                mask |= 1 << (pending[i] - base) // 8
                i += 1
            entries.append((base, mask))
        self.buf += struct.pack("<4sIII", b"RELT", off, 1, 0)
        self.buf += struct.pack("<QiiiI", 0, 0, data_end, 0, len(entries))
        for base, mask in entries:
            self.buf += struct.pack("<II", base, mask)
        return off


def _action_counts(actors: list[Actor]) -> tuple[int, int]:
    return sum(len(a.actions) for a in actors), sum(len(a.queries) for a in actors)


def _variable_raw(var: Variable) -> int:
    if var.type == T_BOOL:
        return int(bool(var.value))
    if var.type == T_FLOAT:
        return struct.unpack("<I", struct.pack("<f", var.value))[0]
    if var.type == T_INT:
        return struct.unpack("<Q", struct.pack("<q", var.value))[0]
    raise EvflError(f"variable of type {var.type}")


def write(file: EventFlowFile) -> bytes:
    """The decompressed ``.bfevfl`` bytes of ``file``, laid out as the game's files are."""
    if (file.flowchart is None) == (file.timeline is None):
        raise EvflError("an event flow file holds exactly one flowchart or one timeline")
    w = _Writer()
    w.reserve(_HEADER.size)
    w.put(0, "8s4BHBB", MAGIC, *VERSION, 0xFEFF, ALIGNMENT_SHIFT, 0)
    w.put(0x20, "HH", file.flowchart is not None, file.timeline is not None)
    if file.flowchart is not None:
        flowcharts = w.reserve(8)
        w.pointer(0x28, flowcharts)
        w.pointer(0x30, w.dictionary([file.flowchart.name]))
        w.pointer(0x38, 0)
        w.pointer(0x40, w.dictionary([]))
        block = w.flowchart(file.flowchart)
        w.pointer(flowcharts, block)
    else:
        w.pointer(0x28, 0)
        w.pointer(0x30, w.dictionary([]))
        timelines = w.reserve(8)
        w.pointer(0x38, timelines)
        w.pointer(0x40, w.dictionary([file.timeline.name]))
        block = w.timeline(file.timeline)
        w.pointer(timelines, block)
    w.string_fields.setdefault(file.name, [])  # the header points at the name's characters (below), unrelocated
    pool, where = w.string_pool()
    data_end = w.pos()
    w.put(block + 4, "I", pool - block)
    relocation = w.relocation_table(data_end)
    if block > 0xFFFF:
        raise EvflError(f"first block at 0x{block:x} does not fit the header")
    w.put(0x10, "IHHII", where[file.name] + 2, 0, block, relocation, len(w.buf))
    return bytes(w.buf)
