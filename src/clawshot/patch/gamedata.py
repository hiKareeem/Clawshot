"""Fast start: what a new game skips (``src/clawshot/data/fast_start.toml``), written as a mod folder.

    settings = load()                               # name -> FastStartSetting, in file order
    files = build(romfs, ["intro", "saria"])        # the changed files, built and checked, nothing written
    write(romfs, out, ["intro", "saria"])           # <out>/romfs/... (only the changed files)

    python -m clawshot.patch.gamedata --romfs <dump> --out <dir> [--skip intro saria ...] [--list]

A setting changes initial values in ``GameData/GameDataList.Product.110.byml.zs`` (a new game resets every flag to
its ``DefaultValue``), and, for a cutscene no flag gates, removes the ``SkipSetting`` from the event's setting
component list so the player may skip it. Facts and the reasons for each value: ``plans/03-game-data.md``,
section 14. Flags are found by name: a ``GameDataList`` entry's ``Hash`` is the murmur3 of its name.
"""

import argparse
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from clawshot.formats import byml, rstb, zsdic
from clawshot.patch.plan import PatchError
from clawshot.patch.write import check_output_folder
from clawshot.save import murmur3_32

FAST_START_TOML = Path(__file__).resolve().parents[1] / "data" / "fast_start.toml"
GAME_DATA_LIST = "GameData/GameDataList.Product.110.byml.zs"
EVENT_SETTING_TABLE = "RSDB/EventSetting.Product.111.rstbl.byml.zs"
SKIP_SETTING = "SkipSetting"

# The GameDataList types a setting may change, and the Python type of the value fast_start.toml gives for each.
VALUE_TYPES = {"Bool": bool, "Int": int, "Enum": str}
# ResetTypeValue bit of the entries a new game resets (every story flag has it: 8 or 24). [Inference from the
# values: Sequence/NormalTitle resets with ResetType 3 before the opening, and bit 3 is set on all 9338 per-slot
# story Bools; system entries such as Sequence_* have 0.]
NEW_GAME_RESET_BIT = 1 << 3
SETTING_KEYS = {"default", "skips", "state", "source", "logic", "game_data", "skippable"}


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
    skippable: tuple[str, ...]
    """Events whose SkipSetting is removed."""


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
        skippable = entry.get("skippable", [])
        if not isinstance(skippable, list) or not all(isinstance(e, str) for e in skippable):
            raise FastStartError(f"{where}: 'skippable' is a list of event names")
        if not game_data and not skippable:
            raise FastStartError(f"{where}: changes nothing (no game_data, no skippable)")
        logic = entry.get("logic")
        if logic is not None and not isinstance(logic, str):
            raise FastStartError(f"{where}: 'logic' is text")
        out[name] = FastStartSetting(
            name, entry["default"], entry["skips"], entry["state"], entry["source"], logic, dict(game_data),
            tuple(skippable),
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
    """The named settings, in file order; an unknown name is an error."""
    if unknown := [n for n in names if n not in settings]:
        raise FastStartError(f"unknown fast-start settings {unknown}; known: {', '.join(settings)}")
    return [s for name, s in settings.items() if name in names]


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


# --- event settings -------------------------------------------------------------------------------------------------


def _romfs_path(work_path: str) -> str:
    """``Work/Event/.../X.engine__event__T.gyml`` -> ``Event/.../X.engine__event__T.bgyml`` (``?``-prefixed too)."""
    path = work_path.removeprefix("?").removeprefix("Work/")
    if path.endswith(".gyml"):
        path = path.removesuffix(".gyml") + ".bgyml"
    return path


def component_list_path(event_settings: list[dict], event: str) -> str:
    """The romfs path of ``event``'s setting component list (``RSDB/EventSetting``'s ``EventSettingComponentList``).
    Shared by another event, it is an error: removing its SkipSetting would change that event too."""
    rows = {row.get("__RowId"): row for row in event_settings}
    if event not in rows:
        raise FastStartError(f"RSDB/EventSetting has no event {event!r}")
    work_path = rows[event].get("EventSettingComponentList", "")
    if not work_path:
        raise FastStartError(f"event {event!r} has no EventSettingComponentList")
    sharing = sorted(r for r, row in rows.items() if r != event and row.get("EventSettingComponentList") == work_path)
    if sharing:
        raise FastStartError(f"event {event!r}: its component list {work_path} is shared with {sharing}")
    return _romfs_path(work_path)


def _skip_setting_in_parents(read, path: str, seen: tuple[str, ...] = ()) -> str | None:
    """The first ``$parent`` (romfs path) up the chain from ``path`` that sets a SkipSetting, or None."""
    tree = read(path)
    parent = tree.get("$parent") if isinstance(tree, dict) else None
    if not parent:
        return None
    parent_path = _romfs_path(parent)
    if parent_path in seen:
        raise FastStartError(f"{path}: $parent loop through {parent_path}")
    parent_tree = read(parent_path)
    if SKIP_SETTING in (parent_tree.get("Components") or {}):
        return parent_path
    return _skip_setting_in_parents(read, parent_path, (*seen, parent_path))


def make_skippable(tree: dict, path: str) -> None:
    """Remove the SkipSetting from a component list tree, in place."""
    components = tree.get("Components") if isinstance(tree, dict) else None
    if not isinstance(components, dict) or SKIP_SETTING not in components:
        raise FastStartError(f"{path} has no Components/{SKIP_SETTING}: the event is skippable already")
    del components[SKIP_SETTING]


# --- building and writing -------------------------------------------------------------------------------------------


class _Romfs:
    def __init__(self, romfs: Path):
        self.root = romfs
        self.dicts = zsdic.Dictionaries.from_romfs(romfs)
        self.table = rstb.read(self.dicts.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))

    def raw(self, path: str) -> bytes:
        data = (self.root / PurePosixPath(path)).read_bytes()
        return self.dicts.decompress(path, data) if path.endswith(".zs") else data

    def tree(self, path: str):
        return byml.read(self.raw(path))

    def built(self, path: str, document: byml.Document, data: bytes) -> BuiltFile:
        """Write ``document``, check it reads back and fits the file's size-table entry, and compress it like the
        game's file."""
        new_data = byml.dump(document)
        if (d := byml.difference(document.root, byml.read(new_data))) is not None:
            raise FastStartError(f"{path}: the written file does not read back as the changed tree: {d}")
        entry = self.table.get(path)
        if entry is None:
            raise FastStartError(f"{path}: the resource size table has no entry for it")
        if len(new_data) > entry:
            raise FastStartError(f"{path}: {len(new_data)} bytes do not fit its size-table entry {entry}")
        content = new_data
        if path.endswith(".zs"):
            content = self.dicts.compress(path, new_data)
            if self.dicts.decompress(path, content) != new_data:
                raise FastStartError(f"{path}: the compressed file does not decompress to the written bytes")
        return BuiltFile(path, content, len(data), len(new_data), entry)


def build(romfs: str | Path, names: list[str], settings: dict[str, FastStartSetting] | None = None) -> list[BuiltFile]:
    """The files the named settings change, built and checked; nothing is written. The romfs is only read."""
    settings = load() if settings is None else settings
    chosen = select(settings, names)
    fs = _Romfs(Path(romfs))
    out = []
    if any(s.game_data for s in chosen):
        data = fs.raw(GAME_DATA_LIST)
        document = byml.load(data)
        apply_game_data(document.root, plan_game_data(document.root, chosen))
        out.append(fs.built(GAME_DATA_LIST, document, data))
    events = [event for s in chosen for event in s.skippable]
    if events:
        event_settings = fs.tree(EVENT_SETTING_TABLE)
        for event in dict.fromkeys(events):
            path = component_list_path(event_settings, event)
            if parent := _skip_setting_in_parents(fs.tree, path):
                raise FastStartError(f"event {event!r}: its parent list {parent} sets a SkipSetting too")
            data = fs.raw(path)
            document = byml.load(data)
            make_skippable(document.root, path)
            out.append(fs.built(path, document, data))
    return out


def write(romfs: str | Path, out: str | Path, names: list[str], settings=None) -> list[BuiltFile]:
    """Write the changed files to ``<out>/romfs/``; ``out`` must be empty or absent and outside the romfs. Every file
    is built and checked before the first is written."""
    romfs, out = Path(romfs), Path(out)
    check_output_folder(romfs, out)
    files = build(romfs, names, settings)
    for f in files:
        target = out / "romfs" / PurePosixPath(f.path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(f.content)
    return files


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
        print(f"  {f.path}: {f.size} -> {f.new_size} bytes ({f.new_size - f.size:+d}), size-table entry {f.entry}")
    print(f"wrote {len(written)} files under {args.out / 'romfs'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
