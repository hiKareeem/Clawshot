"""Load the world data files (``src/clawshot/data/world/``) and build a :class:`World` for a set of logic settings.

A *spec* is the data as plain dicts, merged from the files (``load_spec``) or written directly by a test:

``start``, ``goal``
    the start region and the goal rule.
``regions``
    a list of ``{name, source?, dungeon?, scene?, hint?, time_passes?, provides_time?, events?, locations?,
    exits?}``; ``events``, ``locations`` and ``exits`` map a name to a rule, or to a table with ``rule`` (and, for a
    location, ``type``, ``vanilla``, ``source``).
``locations``
    ``{name: {type, vanilla?, source?}}`` for locations whose region entry gives only the rule.
``items``
    ``{name: {type?, class?, dungeon?, bottle?, medallion?, stone?, alias?}}``; ``class`` is ``progression``
    (default), ``priority`` or ``normal``.
``helpers``, ``settings``, ``tricks``, ``flags``
    helper rules by signature; logic settings; tricks (always off until verified in the remake); derived world flags.
"""

import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from clawshot.world.model import DUNGEON_ITEM_TYPES, Event, Exit, Item, Location, Region, World
from clawshot.world.rules import ALL_TIMES, DAY, NIGHT, Compiler, ItemFacts, RuleError

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "world"

_TIMES = {"day": DAY, "night": NIGHT, "all": ALL_TIMES}
_NIGHT_STARTS = ("sunset", "evening", "midnight", "witching-hour")


class WorldError(ValueError):
    """World data that does not hold together (a missing field, a duplicate name, a bad setting)."""


def _read(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)


def load_spec(directory: Path = DATA_DIR) -> dict[str, Any]:
    """Merge the data files named by ``<directory>/world.toml`` into one spec."""
    meta = _read(directory / "world.toml")
    spec: dict[str, Any] = {"start": meta["start"], "goal": meta["goal"], "regions": [], "locations": {}}
    for name in ("items", "helpers"):
        spec[name] = _read(directory / f"{name}.toml")[name]
    settings = _read(directory / "settings.toml")
    for name in ("settings", "tricks", "flags"):
        spec[name] = settings.get(name, {})
    for file in meta["files"]:
        data = _read(directory / file)
        spec["regions"].extend(data.get("region", []))
        for location, info in data.get("locations", {}).items():
            if location in spec["locations"]:
                raise WorldError(f"{file}: location {location!r} is described twice")
            spec["locations"][location] = info
    return spec


def _item(name: str, info: Mapping[str, Any]) -> Item:
    item_type = info.get("type", "Item")
    cls = info.get("class", "progression")
    if cls not in ("progression", "priority", "normal"):
        raise WorldError(f"item {name!r}: class {cls!r} is not progression, priority or normal")
    dungeon = info.get("dungeon")
    if dungeon is None and item_type in DUNGEON_ITEM_TYPES and name.endswith(")") and " (" in name:
        dungeon = name[name.rindex(" (") + 2 : -1]
    alias = info.get("alias")
    return Item(
        name=name,
        type=item_type,
        progression=cls == "progression",
        priority=cls == "priority",
        dungeon=dungeon,
        bottle=bool(info.get("bottle", False)),
        medallion=bool(info.get("medallion", False)),
        stone=bool(info.get("stone", False)),
        alias=(alias[0], int(alias[1])) if alias else None,
    )


def resolve_settings(spec: Mapping[str, Any], logic: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """The spec's settings, tricks and flags with ``logic`` applied on top."""
    settings = dict(spec.get("settings", {}))
    tricks = dict(spec.get("tricks", {}))
    flags = dict(spec.get("flags", {}))
    for name, value in (logic or {}).items():
        if name in tricks:
            if value:
                raise WorldError(f"trick {name} stays off until it is verified in the remake (AGENTS.md rule 6)")
            continue
        if name in settings:
            settings[name] = value
        elif name in flags:
            flags[name] = value
        else:
            raise WorldError(f"unknown logic setting {name!r}")
    overlap = (settings.keys() & tricks.keys()) | (settings.keys() & flags.keys()) | (tricks.keys() & flags.keys())
    if overlap:
        raise WorldError(f"defined twice among settings, tricks and flags: {sorted(overlap)}")
    return settings | tricks | flags


def _rule_entry(value: Any, where: str) -> tuple[str, dict[str, Any]]:
    if isinstance(value, str):
        return value, {}
    if isinstance(value, Mapping) and isinstance(value.get("rule"), str):
        return value["rule"], dict(value)
    raise WorldError(f"{where}: expected a rule string or a table with 'rule'")


def build_world(spec: Mapping[str, Any], logic: Mapping[str, Any] | None = None) -> World:
    """Compile every rule of ``spec`` under the logic settings ``logic`` (defaults from the spec)."""
    settings = resolve_settings(spec, logic)
    items = {name: _item(name, info) for name, info in spec.get("items", {}).items()}
    facts = ItemFacts(
        names=frozenset(items),
        bottles=tuple(n for n, i in items.items() if i.bottle),
        medallions=tuple(n for n, i in items.items() if i.medallion),
        stones=tuple(n for n, i in items.items() if i.stone),
    )
    helpers = {name: _rule_entry(value, f"helper {name!r}")[0] for name, value in spec.get("helpers", {}).items()}
    compiler = Compiler(facts, helpers, settings)
    location_info: Mapping[str, Mapping[str, Any]] = spec.get("locations", {})

    regions: dict[str, Region] = {}
    locations: dict[str, Location] = {}
    events: list[Event] = []
    try:
        for data in spec["regions"]:
            name = data["name"]
            if name in regions:
                raise WorldError(f"region {name!r} is defined twice")
            provides = data.get("provides_time")
            if provides is not None and provides.lower() not in _TIMES:
                raise WorldError(f"region {name!r}: provides_time {provides!r} is not day, night or all")
            region = Region(
                name=name,
                source=data.get("source", ""),
                dungeon=data.get("dungeon"),
                scene=data.get("scene"),
                hint=data.get("hint"),
                time_passes=bool(data.get("time_passes", False)),
                provides_time=_TIMES[provides.lower()] if provides else 0,
            )
            regions[name] = region
            for event_name, value in data.get("events", {}).items():
                where = f"region {name!r}, event {event_name!r}"
                text, extra = _rule_entry(value, where)
                event = Event(event_name, name, compiler.compile(text, name, where), extra.get("source", region.source))
                region.events.append(event)
                events.append(event)
            for location_name, value in data.get("locations", {}).items():
                where = f"region {name!r}, location {location_name!r}"
                text, extra = _rule_entry(value, where)
                info = {**location_info.get(location_name, {}), **extra}
                if location_name in locations:
                    raise WorldError(f"{where}: location already defined in {locations[location_name].region!r}")
                if "type" not in info:
                    raise WorldError(f"{where}: no type (add it under [locations])")
                vanilla = info.get("vanilla")
                if vanilla is not None and vanilla not in items:
                    raise WorldError(f"{where}: vanilla item {vanilla!r} is not in the item table")
                location = Location(
                    name=location_name,
                    region=name,
                    rule=compiler.compile(text, name, where),
                    type=info["type"],
                    vanilla=vanilla,
                    source=info.get("source", region.source),
                )
                region.locations.append(location)
                locations[location_name] = location
            for target, value in data.get("exits", {}).items():
                where = f"region {name!r}, exit to {target!r}"
                text, extra = _rule_entry(value, where)
                rule = compiler.compile(text, name, where)
                region.exits.append(Exit(name, target, rule, extra.get("source", region.source)))

        goal = compiler.compile(spec["goal"], None, "goal")
        # here() and at() make events while compiling, and compiling those may make more.
        while subrules := compiler.take_subrules():
            for subrule in subrules:
                event = Event(subrule.name, subrule.region, compiler.compile_subrule(subrule), "here()/at()")
                events.append(event)
                if subrule.region in regions:
                    regions[subrule.region].events.append(event)
    except RuleError as e:
        raise WorldError(str(e)) from None

    start = spec["start"]
    if start not in regions:
        raise WorldError(f"start region {start!r} is not defined")
    unknown = sorted(set(location_info) - set(locations))
    if unknown:
        raise WorldError(f"[locations] describes locations no region has: {unknown}")
    defined = {e.name for e in events} | set(items)
    return World(
        regions=regions,
        locations=locations,
        events=events,
        items=items,
        settings=settings,
        start=start,
        start_tod=NIGHT if settings.get("starting_tod") in _NIGHT_STARTS else DAY,
        goal=goal,
        dangling_exits=[(r.name, e.target) for r in regions.values() for e in r.exits if e.target not in regions],
        undefined_events=sorted(compiler.events_named - defined),
        missing_regions=sorted({e.region for e in events if e.region not in regions}),
    )


def load_world(logic: Mapping[str, Any] | None = None, directory: Path = DATA_DIR) -> World:
    return build_world(load_spec(directory), logic)
