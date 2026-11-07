"""Translate OoT Randomizer's logic files into Clawshot's world data, without rewriting a rule by hand.

    python -m clawshot.world.translate --ootr <OoT-Randomizer checkout> [--out <dir>]

Reads ``<out>/port.toml`` (which OoT Randomizer regions go into which file) and writes into ``<out>`` (default:
the package's ``data/world``):

- one region file per ``port.toml`` entry: the regions with their events, locations and exits, rules copied
  verbatim; each requirement carries its source line as a comment, and OoT Randomizer's comments above it;
- ``helpers.toml`` from ``data/LogicHelpers.json``;
- ``items.toml`` from ``ItemList.py`` (type and progression class);
- ``settings.toml``: every setting, trick and world flag the written rules name, at OoT Randomizer's defaults
  (tricks and glitches off: they do not carry over until verified in the remake, AGENTS.md rule 6).

OoT Randomizer is MIT (its GPL folders, under ``bin/`` and ``Notes/``, are not read). The checkout's modules
(``ItemList``, ``LocationList``, ``SettingsList``, ``Settings``, ``World``) are imported to read their tables;
nothing from it is copied into Clawshot but the logic data written here, credited in ``NOTICE``.

Location kinds: OoT Randomizer lists drops (``Drop``) and fixed events (``Event``) as locations holding a fixed
item; they become events named after that item. Hints (``Hint``, ``HintStone``) hold nothing and are left out.
"""

import argparse
import ast
import importlib
import json
import re
import subprocess
import sys
import tomllib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from clawshot.world.load import DATA_DIR

EVENT_TYPES = frozenset({"Event", "Drop"})
SKIPPED_TYPES = frozenset({"Hint", "HintStone"})
REGION_KEYS = frozenset(
    {"region_name", "scene", "hint", "dungeon", "time_passes", "provides_time", "events", "locations", "exits"}
)
# Region fields OoT Randomizer uses for entrance shuffle and hints only; not carried over yet.
IGNORED_REGION_KEYS = frozenset({"savewarp", "is_boss_room", "alt_hint"})
# Names the engine reads even when no rule names them.
ALWAYS_SETTINGS = ("starting_age", "starting_tod", "damage_multiplier")
ALWAYS_FLAGS = ("ensure_tod_access",)
# OoT Randomizer's region files for Master Quest dungeons, left out of the port.
MASTER_QUEST_SUFFIX = " MQ.json"


class TranslateError(RuntimeError):
    pass


# reading OoT Randomizer


def read_logic_json(path: Path) -> Any:
    """OoT Randomizer's ``Utils.read_logic_file``: JSON with ``#`` comments to the end of a line."""
    text = "".join(line.split("#")[0].replace("\n", " ") for line in path.read_text(encoding="utf-8").splitlines(True))
    return json.loads(re.sub(" +", " ", text))


def _key_line(lines: list[str], key: str, start: int, end: int) -> int:
    pattern = re.compile(rf'^\s*"{re.escape(key)}"\s*:')
    for i in range(start, end):
        if pattern.match(lines[i]):
            return i
    raise TranslateError(f"cannot find the line of {key!r} between lines {start + 1} and {end}")


def _comments_above(lines: list[str], index: int) -> list[str]:
    found: list[str] = []
    i = index - 1
    while i >= 0 and lines[i].strip().startswith("#"):
        found.append(lines[i].strip().lstrip("#").strip())
        i -= 1
    return list(reversed(found))


def _normalize(rule: str) -> str:
    return " ".join(rule.split())


@dataclass
class Entry:
    """One requirement: a name, its rule, where it came from and OoT Randomizer's comments on it."""

    name: str
    rule: str
    source: str
    comments: list[str] = field(default_factory=list)


@dataclass
class PortedRegion:
    name: str
    source: str
    fields: dict[str, Any]
    events: list[Entry]
    locations: list[Entry]
    exits: list[Entry]


@dataclass
class Port:
    regions: dict[str, list[PortedRegion]]
    locations: dict[str, dict[str, Any]]
    skipped: list[str]
    rules: list[str]


def _ootr_module(name: str) -> Any:
    return importlib.import_module(name)


def _line_of(text_lines: list[str], needle: str) -> int:
    for i, line in enumerate(text_lines):
        if needle in line:
            return i + 1
    raise TranslateError(f"cannot find {needle!r}")


def port_regions(ootr: Path, files: Mapping[str, Mapping[str, list[str]]]) -> Port:
    location_table = _ootr_module("LocationList").location_table
    location_lines = (ootr / "LocationList.py").read_text(encoding="utf-8").splitlines()
    result: dict[str, list[PortedRegion]] = {}
    locations: dict[str, dict[str, Any]] = {}
    skipped: list[str] = []
    rules: list[str] = []
    for out_name, config in files.items():
        ported: list[PortedRegion] = []
        area = config.get("area")
        for relative, wanted in config["regions"].items():
            path = ootr / relative
            data = {r["region_name"]: r for r in read_logic_json(path)}
            lines = path.read_text(encoding="utf-8").splitlines()
            starts = [i for i, line in enumerate(lines) if '"region_name"' in line]
            file_label = Path(relative).name
            for region_name in wanted:
                if region_name not in data:
                    raise TranslateError(f"{relative}: no region {region_name!r}")
                region = data[region_name]
                unknown = set(region) - REGION_KEYS - IGNORED_REGION_KEYS
                if unknown:
                    raise TranslateError(f"{relative}: region {region_name!r} has unknown keys {sorted(unknown)}")
                start = next(i for i in starts if f'"{region_name}"' in lines[i])
                end = next((i for i in starts if i > start), len(lines))
                span = (lines, start, end, file_label)
                events = _entries(region, "events", *span)
                kept_locations: list[Entry] = []
                for entry in _entries(region, "locations", *span):
                    if entry.name not in location_table:
                        raise TranslateError(f"{relative}: location {entry.name!r} is not in LocationList.py")
                    loc_type, _, _, _, vanilla, _ = location_table[entry.name]
                    if loc_type in SKIPPED_TYPES:
                        skipped.append(entry.name)
                        continue
                    if loc_type in EVENT_TYPES:
                        if vanilla is None:
                            raise TranslateError(f"{entry.name!r}: an {loc_type} location without an item")
                        note = f"OoT Randomizer location {entry.name!r} ({loc_type})"
                        events.append(Entry(vanilla, entry.rule, entry.source, [*entry.comments, note]))
                        continue
                    kept_locations.append(entry)
                    info: dict[str, Any] = {"type": loc_type}
                    if vanilla is not None:
                        info["vanilla"] = vanilla
                    info["source"] = f"LocationList.py:{_line_of(location_lines, f'("{entry.name}",')}"
                    locations[entry.name] = info
                events = _merge_events(events)
                exits = _entries(region, "exits", *span)
                for entry in [*events, *kept_locations, *exits]:
                    rules.append(entry.rule)
                keys = ("dungeon", "scene", "hint", "time_passes", "provides_time")
                fields = {k: region[k] for k in keys if k in region}
                if "provides_time" in fields:
                    fields["provides_time"] = str(fields["provides_time"]).lower()
                if area is not None:
                    fields = {"area": area, **fields}
                ported.append(
                    PortedRegion(region_name, f"{file_label}:{start + 1}", fields, events, kept_locations, exits)
                )
        result[out_name] = ported
    return Port(result, locations, skipped, rules)


def _entries(region: Mapping[str, Any], block: str, lines: list[str], start: int, end: int, label: str) -> list[Entry]:
    """The entries of one block (``events``, ``locations``, ``exits``) of the region at ``lines[start:end]``."""
    if block not in region:
        return []
    block_line = _key_line(lines, block, start, end)
    out = []
    for key, rule in region[block].items():
        i = _key_line(lines, key, block_line + 1, end)
        out.append(Entry(key, _normalize(rule), f"{label}:{i + 1}", _comments_above(lines, i)))
    return out


def _merge_events(events: list[Entry]) -> list[Entry]:
    """Two sources of one event in a region become one rule, ``(a) or (b)``."""
    merged: dict[str, Entry] = {}
    for entry in events:
        if entry.name in merged:
            first = merged[entry.name]
            merged[entry.name] = Entry(
                entry.name,
                f"({first.rule}) or ({entry.rule})",
                f"{first.source}, {entry.source}",
                [*first.comments, *entry.comments],
            )
        else:
            merged[entry.name] = entry
    return list(merged.values())


def port_helpers(ootr: Path) -> list[Entry]:
    path = ootr / "data" / "LogicHelpers.json"
    data = read_logic_json(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for key, rule in data.items():
        i = _key_line(lines, key, 0, len(lines))
        out.append(Entry(key, _normalize(rule), f"LogicHelpers.json:{i + 1}", _comments_above(lines, i)))
    return out


def port_items() -> list[tuple[str, dict[str, Any]]]:
    item_table = _ootr_module("ItemList").item_table
    out = []
    for name, (item_type, progressive, _, special) in item_table.items():
        special = special or {}
        info: dict[str, Any] = {
            "type": item_type,
            "class": {True: "progression", False: "priority", None: "normal"}[progressive],
        }
        for flag in ("bottle", "medallion", "stone"):
            if special.get(flag):
                info[flag] = True
        if "alias" in special:
            alias, count = special["alias"]
            info["alias"] = [alias, count]
        out.append((name, info))
    return out


def _names_in(rules: Iterable[str]) -> set[str]:
    names: set[str] = set()
    for rule in rules:
        for node in ast.walk(ast.parse(rule, mode="eval")):
            if isinstance(node, ast.Name):
                names.add(node.id)
    return names


def port_settings(rules: Iterable[str], helper_names: set[str]) -> dict[str, dict[str, Any]]:
    """Every setting, trick and world flag named in ``rules``, resolved in OoT Randomizer's order (helpers, items,
    world attributes, settings; ``RuleParser.visit_Name``) at its default settings."""
    settings_mod = _ootr_module("Settings")
    world_mod = _ootr_module("World")
    tricks_mod = _ootr_module("SettingsListTricks")
    escape = _ootr_module("RulesCommon").escape_name
    items = {escape(n) for n in _ootr_module("ItemList").item_table}
    defaults = settings_mod.Settings({})
    world = world_mod.World(0, defaults)
    tricks = {t["name"] for t in tricks_mod.logic_tricks.values()} | {
        t["name"] for t in tricks_mod.advanced_logic_tricks.values()
    }
    out: dict[str, dict[str, Any]] = {"settings": {}, "tricks": {}, "flags": {}}
    names = _names_in(rules) | set(ALWAYS_SETTINGS) | set(ALWAYS_FLAGS)
    for name in sorted(names):
        if name in helper_names or name in items:
            continue
        if name in world.__dict__ and name not in ALWAYS_SETTINGS:
            value = world.__dict__[name]
            if name == "skipped_trials":
                # World.__init__ leaves every trial active; World.resolve_random_settings then skips all but
                # `trials` of them, at random unless the count is 0 or 6 (all six: OoT Randomizer's default).
                trials = defaults.settings_dict["trials"]
                if defaults.settings_dict["trials_random"] or trials not in (0, len(value)):
                    raise TranslateError(f"skipped_trials depends on the seed at trials = {trials}")
                value = {trial: trials == 0 for trial in value}
            elif name == "selected_adult_trade_item":
                # World.__init__ picks one of adult_trade_start at random; the unshuffled game starts the adult
                # trade sequence with the Pocket Egg.
                if "Pocket Egg" not in defaults.settings_dict["adult_trade_start"]:
                    raise TranslateError("adult_trade_start at its default no longer holds the Pocket Egg")
                value = "Pocket Egg"
            if isinstance(value, bool | int | str | dict):
                out["flags"][name] = value
            continue
        if name in tricks:
            out["tricks"][name] = False
        elif name in defaults.settings_dict:
            value = defaults.settings_dict[name]
            if isinstance(value, set | tuple):
                value = sorted(value)
            out["settings"][name] = value
    return out


# writing TOML


def _toml_key(key: str) -> str:
    return key if re.fullmatch(r"[A-Za-z0-9_-]+", key) else _toml_value(key)


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return repr(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        if any(ord(c) < 0x20 for c in escaped):
            raise TranslateError(f"control character in {value!r}")
        return f'"{escaped}"'
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{ " + ", ".join(f"{_toml_key(k)} = {_toml_value(v)}" for k, v in value.items()) + " }"
    raise TranslateError(f"cannot write {value!r} as TOML")


def _entry_lines(entries: list[Entry]) -> list[str]:
    out = []
    for entry in entries:
        out.extend(f"# {c}" if c else "#" for c in entry.comments)
        out.append(f"{_toml_key(entry.name)} = {_toml_value(entry.rule)}  # {entry.source}")
    return out


def _header(commit: str, sources: str) -> list[str]:
    return [
        "# Generated by `python -m clawshot.world.translate` from OoT Randomizer",
        f"# (https://github.com/OoTRandomizer/OoT-Randomizer, MIT) at {commit}: {sources}.",
        "# Rules are OoT Randomizer's, verbatim; plans/04-world-format.md describes the format.",
        "",
    ]


def write_region_file(path: Path, commit: str, regions: list[PortedRegion], locations: Mapping[str, Any]) -> None:
    sources = ", ".join(sorted({r.source.split(":")[0] for r in regions}))
    lines = _header(commit, f"data/World/{sources}, LocationList.py")
    for region in regions:
        lines.append("[[region]]")
        lines.append(f"name = {_toml_value(region.name)}")
        for key, value in region.fields.items():
            lines.append(f"{key} = {_toml_value(value)}")
        lines.append(f"source = {_toml_value(region.source)}")
        for block, entries in (("events", region.events), ("locations", region.locations), ("exits", region.exits)):
            if entries:
                lines.append("")
                lines.append(f"[region.{block}]")
                lines.extend(_entry_lines(entries))
        lines.append("")
    names = [entry.name for region in regions for entry in region.locations]
    if names:
        lines.append("[locations]")
        lines.extend(f"{_toml_key(n)} = {_toml_value(locations[n])}" for n in names)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_helpers(path: Path, commit: str, helpers: list[Entry]) -> None:
    lines = _header(commit, "data/LogicHelpers.json")
    lines.append("[helpers]")
    lines.extend(_entry_lines(helpers))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_items(path: Path, commit: str, items: list[tuple[str, dict[str, Any]]]) -> None:
    lines = _header(commit, "ItemList.py item_table")
    lines.append("# class: progression (advancement True), priority (False) or normal (None).")
    lines.append("[items]")
    lines.extend(f"{_toml_key(name)} = {_toml_value(info)}" for name, info in items)
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_settings(path: Path, commit: str, settings: Mapping[str, Mapping[str, Any]]) -> None:
    lines = _header(commit, "defaults from SettingsList.py, SettingsListTricks.py and World.py")
    notes = {
        "settings": "Logic settings the rules name, at OoT Randomizer's defaults. A seed's settings may override them.",
        "tricks": "N64 tricks and glitches: off until verified in the remake (AGENTS.md rule 6).",
        "flags": "OoT Randomizer World attributes, as its default settings derive them (no entrance shuffle).",
    }
    for table in ("settings", "tricks", "flags"):
        lines.append(f"# {notes[table]}")
        lines.append(f"[{table}]")
        lines.extend(f"{_toml_key(k)} = {_toml_value(v)}" for k, v in settings[table].items())
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _commit(ootr: Path) -> str:
    try:
        out = subprocess.run(["git", "-C", str(ootr), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        raise TranslateError(f"cannot read the OoT Randomizer commit in {ootr}: {e}") from None
    return out.stdout.strip()


def unported_regions(ootr: Path, files: Mapping[str, Mapping[str, Any]]) -> list[str]:
    """Regions of OoT Randomizer's region files (Master Quest aside) that no ``port.toml`` entry names."""
    ported = {(src, name) for config in files.values() for src, names in config["regions"].items() for name in names}
    out = []
    for path in sorted((ootr / "data" / "World").glob("*.json")):
        if path.name.endswith(MASTER_QUEST_SUFFIX):
            continue
        relative = f"data/World/{path.name}"
        out.extend(
            f"{path.name}: {r['region_name']}"
            for r in read_logic_json(path)
            if (relative, r["region_name"]) not in ported
        )
    return out


def translate(ootr: Path, out: Path) -> dict[str, Any]:
    with (out / "port.toml").open("rb") as f:
        port_config = tomllib.load(f)
    commit = _commit(ootr)
    if commit != port_config["ootr_commit"]:
        raise TranslateError(f"{ootr} is at {commit}, port.toml names {port_config['ootr_commit']}")
    sys.path.insert(0, str(ootr))
    try:
        port = port_regions(ootr, port_config["files"])
        helpers = port_helpers(ootr)
        items = port_items()
        settings = port_settings([*port.rules, *(h.rule for h in helpers)], {h.name.split("(")[0] for h in helpers})
    finally:
        sys.path.remove(str(ootr))
    for name, regions in port.regions.items():
        write_region_file(out / name, commit, regions, port.locations)
    write_helpers(out / "helpers.toml", commit, helpers)
    write_items(out / "items.toml", commit, items)
    write_settings(out / "settings.toml", commit, settings)
    return {
        "commit": commit,
        "files": {
            name: {
                "regions": len(regions),
                "locations": sum(len(r.locations) for r in regions),
                "events": sum(len(r.events) for r in regions),
                "exits": sum(len(r.exits) for r in regions),
            }
            for name, regions in port.regions.items()
        },
        "hints_left_out": len(port.skipped),
        "regions_not_ported": unported_regions(ootr, port_config["files"]),
        "helpers": len(helpers),
        "items": len(items),
        "settings": {k: len(v) for k, v in settings.items()},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m clawshot.world.translate", description=__doc__.splitlines()[0])
    parser.add_argument("--ootr", type=Path, required=True, help="an OoT-Randomizer checkout at port.toml's commit")
    parser.add_argument("--out", type=Path, default=DATA_DIR)
    args = parser.parse_args(argv)
    try:
        report = translate(args.ootr.resolve(), args.out)
    except TranslateError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
