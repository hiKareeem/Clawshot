"""Fast start: what a new game skips (``src/clawshot/data/fast_start.toml``), written as a mod folder.

    settings = load()                               # name -> FastStartSetting, in file order
    file_changes = changes(select(settings, ["intro", "saria"]))   # romfs path -> decompressed transform
    write(romfs, out, ["intro", "saria"])           # <out>/romfs/... (only the changed files, and the size table)

    python -m clawshot.patch.gamedata --romfs <dump> --out <dir> [--skip intro saria ...] [--list]

A setting changes initial values in ``GameData/GameDataList.Product.110.byml.zs`` (a new game resets every flag to
its ``DefaultValue``), and, for what no flag gates, applies named event-flow edits (:data:`FLOW_EDITS`). Both are
decompressed transforms for ``clawshot.patch.write``, which composes them with a seed's other changes and raises a
grown file's size-table entry. Facts and the reasons for each value: ``plans/03-game-data.md``, section 14. Flags
are found by name: a ``GameDataList`` entry's ``Hash`` is the murmur3 of its name.
"""

import argparse
import sys
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import partial
from pathlib import Path

from clawshot.formats import byml, evfl
from clawshot.patch import mido
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import FileChanges, WrittenFile
from clawshot.patch.write import write as write_patch
from clawshot.save import murmur3_32

FAST_START_TOML = Path(__file__).resolve().parents[1] / "data" / "fast_start.toml"
GAME_DATA_LIST = "GameData/GameDataList.Product.110.byml.zs"
OPENING_FLOW = "Event/EventFlow/OpeningEvent.bfevfl.zs"
OPENING_LOADING = "Opening_LoadingKokiriForest"
OPENING_MOVIE = "Dm_Kokiri_0000"
OPENING_WAIT = "ClawshotWaitForKokiriForest"

# The GameDataList types a setting may change, and the Python type of the value fast_start.toml gives for each.
VALUE_TYPES = {"Bool": bool, "Int": int, "Enum": str}
# ResetTypeValue bit of the entries a new game resets (every story flag has it: 8 or 24). [Inference from the
# values: Sequence/NormalTitle resets with ResetType 3 before the opening, and bit 3 is set on all 9338 per-slot
# story Bools; system entries such as Sequence_* have 0.]
NEW_GAME_RESET_BIT = 1 << 3
SETTING_KEYS = {"default", "skips", "state", "source", "logic", "game_data", "flow_edits"}


@dataclass(frozen=True)
class FastStartSetting:
    name: str
    default: bool
    skips: str
    """What a new game no longer plays."""
    state: str
    """The state the skipped scenes would have left, and how the setting gives it."""
    source: str
    logic: str | None
    """How the setting changes what a seed's logic may assume (None: it does not)."""
    game_data: dict[str, bool | int | str]
    """GameDataList entry name -> its new initial value (a Bool, an Int, or an Enum's value name)."""
    flow_edits: tuple[str, ...]
    """Names of the event-flow edits (:data:`FLOW_EDITS`) the setting applies."""


@dataclass(frozen=True)
class GameDataChange:
    setting: str
    name: str
    type: str  # the GameDataList list: Bool, Int or Enum
    old: bool | int | str
    new: bool | int | str


@dataclass(frozen=True)
class BuiltFile:
    path: str  # romfs-relative
    content: bytes  # as written (compressed when the game's file is)
    size: int  # decompressed, before
    new_size: int  # decompressed, after
    entry: int  # its resource-size-table entry, which the new size must fit


class FastStartError(PatchError):
    pass


# --- event flows ----------------------------------------------------------------------------------------------------


def _targets(event: evfl.Event) -> list[int]:
    """The event indices ``event`` may continue to."""
    if isinstance(event, evfl.SwitchEvent | evfl.SubFlowSwitchEvent):
        return [target for _, target in event.cases]
    if isinstance(event, evfl.ForkEvent):
        return [*event.forks, event.join]
    return [event.next] if isinstance(event, evfl.ActionEvent | evfl.JoinEvent | evfl.SubFlowEvent) else []


def opening_without_movie(data: bytes) -> bytes:
    """``OpeningEvent`` (decompressed) with ``Opening_LoadingKokiriForest`` starting after the opening movie.

    Natively that entry plays the movie (``EventSystemActor.EventTransition`` ``Dm_Kokiri_0000``) while
    ``Sequence/Opening`` loads Kokiri Forest, then switches on ``GameSystemActor.EventQueryBancChangeIsLoaded``, whose
    only case (1) fades in. Here the entry starts at that query, and the movie's event becomes its case 0: a one-frame
    ``GameSystemActor.EventWait`` back to the query, so the flow waits for the load the movie used to cover. Every
    other event, actor and entry point stays native; no actor, action, query, sub flow or child event is added."""
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != "OpeningEvent":
        raise FastStartError(f"{OPENING_FLOW}: expected the OpeningEvent flowchart")
    entries = [entry for entry in fc.entry_points if entry.name == OPENING_LOADING]
    if len(entries) != 1:
        raise FastStartError(f"{OPENING_FLOW}: expected one {OPENING_LOADING} entry point, found {len(entries)}")
    entry = entries[0]
    movie_index = entry.main_event
    movie = fc.events[movie_index] if movie_index < len(fc.events) else None
    query_index = movie.next if isinstance(movie, evfl.ActionEvent) else evfl.NONE
    query = fc.events[query_index] if query_index < len(fc.events) else None
    if (
        not isinstance(movie, evfl.ActionEvent)
        or fc.actors[movie.actor].name != "EventSystemActor"
        or fc.actors[movie.actor].actions[movie.action] != "EventTransition"
        or (movie.params or {}).get("EventName") != OPENING_MOVIE
        or not isinstance(query, evfl.SwitchEvent)
        or fc.actors[query.actor].name != "GameSystemActor"
        or fc.actors[query.actor].queries[query.query] != "EventQueryBancChangeIsLoaded"
        or query.params is not None
        or [value for value, _ in query.cases] != [1]
        or "EventWait" not in fc.actors[query.actor].actions
    ):
        raise FastStartError(f"{OPENING_FLOW}: changed native {OPENING_LOADING} start: {movie!r}, {query!r}")
    others = [event.name for event in fc.events if movie_index in _targets(event)]
    others += [e.name for e in fc.entry_points if e is not entry and movie_index in (e.main_event, *e.sub_flow_events)]
    if others or movie_index in entry.sub_flow_events:
        raise FastStartError(f"{OPENING_FLOW}: the movie's event is also reached from {others}")
    action = fc.actors[query.actor].actions.index("EventWait")
    fc.events[movie_index] = evfl.ActionEvent(
        OPENING_WAIT, query.actor, action, query_index, {"Frames": 1, "IsWaitEnd": True}
    )
    query.cases = [(0, movie_index), *query.cases]
    entry.main_event = query_index
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise FastStartError(f"{OPENING_FLOW}: the written flow does not read back as the changed flow")
    return result


# Named event-flow edits a setting may apply (``flow_edits`` in fast_start.toml): name -> (romfs path, transform of
# the decompressed file). Each validates the native structure it changes and its read-back.
FLOW_EDITS: dict[str, tuple[str, Callable[[bytes], bytes]]] = {
    "opening_without_movie": (OPENING_FLOW, opening_without_movie),
    "deku_tree_after_mido": (mido.FLOW, mido.complete_deku_meeting),
}


# --- settings -------------------------------------------------------------------------------------------------------


def loads(text: str, table: str = "setting") -> dict[str, FastStartSetting]:
    """The settings of ``table``: ``setting`` (the choices a run makes) or ``always`` (applied to every seed)."""
    out = {}
    for name, entry in tomllib.loads(text).get(table, {}).items():
        where = f"fast_start.toml: {table} {name!r}"
        if unknown := set(entry) - SETTING_KEYS:
            raise FastStartError(f"{where}: unknown keys {sorted(unknown)}")
        for key in ("skips", "state", "source"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                raise FastStartError(f"{where}: {key!r} is required (text)")
        if not isinstance(entry.get("default"), bool):
            raise FastStartError(f"{where}: 'default' is required (true or false)")
        game_data = entry.get("game_data", {})
        for flag, value in game_data.items():
            if not isinstance(value, bool | int | str):
                raise FastStartError(f"{where}: {flag} = {value!r}: a value is true/false, a number or a step name")
        flow_edits = entry.get("flow_edits", [])
        if not isinstance(flow_edits, list) or not all(isinstance(e, str) for e in flow_edits):
            raise FastStartError(f"{where}: 'flow_edits' is a list of edit names")
        if unknown := [e for e in flow_edits if e not in FLOW_EDITS]:
            raise FastStartError(f"{where}: unknown flow edits {unknown}; known: {', '.join(FLOW_EDITS)}")
        if not game_data and not flow_edits:
            raise FastStartError(f"{where}: changes nothing (no game_data, no flow_edits)")
        logic = entry.get("logic")
        if logic is not None and not isinstance(logic, str):
            raise FastStartError(f"{where}: 'logic' is text")
        out[name] = FastStartSetting(
            name, entry["default"], entry["skips"], entry["state"], entry["source"], logic, dict(game_data),
            tuple(flow_edits),
        )  # fmt: skip
    return out


def load(path: str | Path = FAST_START_TOML) -> dict[str, FastStartSetting]:
    return loads(Path(path).read_text(encoding="utf-8"))


def load_always(path: str | Path = FAST_START_TOML) -> list[FastStartSetting]:
    """The ``[always.*]`` settings: every seed applies them, whatever fast-start choices it names."""
    return list(loads(Path(path).read_text(encoding="utf-8"), "always").values())


def defaults(settings: dict[str, FastStartSetting]) -> list[str]:
    return [name for name, s in settings.items() if s.default]


def select(settings: dict[str, FastStartSetting], names: list[str]) -> list[FastStartSetting]:
    """Resolve skips in file order. Kept Mido supplies the tree skip only after his native clear."""
    if unknown := [n for n in names if n not in settings]:
        raise FastStartError(f"unknown fast-start settings {unknown}; known: {', '.join(settings)}")
    chosen = [s for name, s in settings.items() if name in names]
    bypassed = any(setting.game_data.get(mido.BLOCKER) is False for setting in chosen)
    # Completing the meeting up front selects the wrong Mido schedule/init protocol.
    # With Mido kept, the flow supplies these four values after his native clear.
    # With Mido bypassed, retain the presets and leave his entire flow native.
    return [
        replace(
            setting,
            game_data=setting.game_data if bypassed else {},
            flow_edits=tuple(edit for edit in setting.flow_edits if edit != "deku_tree_after_mido")
            if bypassed
            else setting.flow_edits,
        )
        if "deku_tree_after_mido" in setting.flow_edits
        else setting
        for setting in chosen
    ]


# --- GameDataList ---------------------------------------------------------------------------------------------------


def _entries(tree: dict, list_type: str) -> list[dict]:
    try:
        return tree["Data"][list_type]
    except (KeyError, TypeError):
        raise FastStartError(f"GameDataList has no Data/{list_type} list") from None


def _find(tree: dict, name: str) -> tuple[str, dict]:
    """The list type and the entry whose Hash is ``name``'s murmur3 (only the types a setting may change)."""
    key = murmur3_32(name.encode("utf-8"))
    found = [(t, e) for t in VALUE_TYPES for e in _entries(tree, t) if e.get("Hash") == key]
    if len(found) != 1:
        what = "no entry" if not found else f"{len(found)} entries"
        raise FastStartError(f"GameDataList has {what} named {name!r} (hash 0x{key:08x}) among {list(VALUE_TYPES)}")
    return found[0]


def _value_name(entry: dict, raw: int) -> str:
    values, names = entry.get("Values", []), entry.get("RawValues", [])
    return names[values.index(raw)] if raw in values else f"0x{raw:08x}"


def plan_game_data(tree: dict, chosen: list[FastStartSetting]) -> list[GameDataChange]:
    """Every initial value the chosen settings change, checked against the tree. Two settings may set one entry only
    to the same value; a value that is already the initial value is an error (the data is out of date)."""
    changes: dict[str, GameDataChange] = {}
    for setting in chosen:
        for name, value in setting.game_data.items():
            where = f"setting {setting.name!r}: {name}"
            list_type, entry = _find(tree, name)
            want = VALUE_TYPES[list_type]
            if type(value) is not want:
                raise FastStartError(f"{where} is a {list_type}; its value must be {want.__name__}, not {value!r}")
            if not entry.get("ResetTypeValue", 0) & NEW_GAME_RESET_BIT:
                raise FastStartError(f"{where}: ResetTypeValue {entry.get('ResetTypeValue')} is not reset on New Game")
            if list_type == "Enum":
                if value not in entry.get("RawValues", []):
                    raise FastStartError(f"{where}: {value!r} is not one of {entry.get('RawValues')}")
                old = _value_name(entry, entry["DefaultValue"])
            else:
                old = entry["DefaultValue"] if list_type == "Bool" else int(entry["DefaultValue"])
            if old == value:
                raise FastStartError(f"{where} is already {value!r} in the game's GameDataList")
            if name in changes and changes[name].new != value:
                raise FastStartError(f"{where}: {changes[name].setting!r} sets it to {changes[name].new!r}")
            changes.setdefault(name, GameDataChange(setting.name, name, list_type, old, value))
    return list(changes.values())


def apply_game_data(tree: dict, changes: list[GameDataChange]) -> None:
    """Set each change's initial value in the tree, in place, keeping the node's BYML type."""
    for change in changes:
        list_type, entry = _find(tree, change.name)
        old = entry["DefaultValue"]
        if list_type == "Enum":
            new = murmur3_32(str(change.new).encode("utf-8"))
            if new not in entry["Values"]:
                raise FastStartError(f"{change.name}: the hash of {change.new!r} is not among the enum's Values")
            entry["DefaultValue"] = type(old)(new)
        elif list_type == "Bool":
            entry["DefaultValue"] = bool(change.new)
        else:
            entry["DefaultValue"] = type(old)(change.new)


def patch_initial_values(data: bytes, chosen: list[FastStartSetting]) -> bytes:
    """The initial-value edit as a composable decompressed transform (including seeds with gift flags)."""
    document = byml.load(data)
    apply_game_data(document.root, plan_game_data(document.root, chosen))
    result = byml.dump(document)
    if difference := byml.difference(document.root, byml.read(result)):
        raise FastStartError(f"{GAME_DATA_LIST}: initial values failed read-back: {difference}")
    return result


# --- changes and writing --------------------------------------------------------------------------------------------


def changes(chosen: list[FastStartSetting]) -> FileChanges:
    """The chosen settings as decompressed file transforms: their initial values and each flow edit once."""
    out: dict[str, Callable[[bytes], bytes]] = {}
    if any(s.game_data for s in chosen):
        out[GAME_DATA_LIST] = partial(patch_initial_values, chosen=chosen)
    for name in dict.fromkeys(edit for s in chosen for edit in s.flow_edits):
        path, transform = FLOW_EDITS[name]
        if path in out:
            raise FastStartError(f"flow edit {name!r}: another fast-start edit changes {path} too")
        out[path] = transform
    return out


def write(romfs: str | Path, out: str | Path, names: list[str], settings=None) -> list[WrittenFile]:
    """Write the files the named settings change to ``<out>/romfs/``, and the size table when a changed file needs a
    bigger entry; ``out`` must be empty or absent and outside the romfs, which is only read. Every file is built and
    read back before the first is written."""
    chosen = select(load() if settings is None else settings, names)
    return write_patch(Plan([], [], []), romfs, out, extra_changes=[changes(chosen)])


def main(argv: list[str] | None = None) -> int:
    settings = load()
    parser = argparse.ArgumentParser(prog="python -m clawshot.patch.gamedata", description=__doc__.splitlines()[0])
    parser.add_argument("--romfs", type=Path, help="the game's romfs folder (read only)")
    parser.add_argument("--out", type=Path, help="the mod folder to write (empty or absent)")
    parser.add_argument(
        "--skip", nargs="*", default=None, metavar="SETTING", help=f"default: {' '.join(defaults(settings))}"
    )
    parser.add_argument("--list", action="store_true", help="list the settings and exit")
    args = parser.parse_args(argv)
    if args.list:
        for s in settings.values():
            print(f"{s.name}{' (default)' if s.default else ''}: {s.skips}")
        return 0
    if args.romfs is None or args.out is None:
        parser.error("--romfs and --out are required")
    names = defaults(settings) if args.skip is None else args.skip
    try:
        written = write(args.romfs, args.out, names, settings)
    except PatchError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"fast start: {', '.join(names) or 'nothing'}")
    for f in written:
        entry = "" if f.entry is None else f", size-table entry {f.entry} -> {f.new_entry}"
        print(f"  {f.path}: {f.size} -> {f.new_size} bytes ({f.new_size - f.size:+d}){entry}")
    print(f"wrote {len(written)} files under {args.out / 'romfs'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
