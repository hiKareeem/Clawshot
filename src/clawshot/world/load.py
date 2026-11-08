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
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clawshot.world.model import DUNGEON_ITEM_TYPES, Event, Exit, Item, Location, Region, World
from clawshot.world.rules import ALL_TIMES, DAY, NIGHT, Compiler, ItemFacts, RuleError

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "world"

# OoT Randomizer's TimeOfDay (Region.py) calls the night bit DAMPE: at_night and at_dampe_time both test it.
_TIMES = {"day": DAY, "night": NIGHT, "dampe": NIGHT, "all": ALL_TIMES}
_NIGHT_STARTS = ("sunset", "evening", "midnight", "witching-hour")


class WorldError(ValueError):
    """World data that does not hold together (a missing field, a duplicate name, a bad setting)."""


def _read(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)


def load_spec(directory: Path = DATA_DIR) -> dict[str, Any]:
    """Merge the data files named by ``<directory>/world.toml`` into one spec. ``world.toml``'s own ``[settings]``
    and ``[items]`` (Clawshot's, not OoT Randomizer's) add to the generated tables; a name in both is an error.
    Its ``overrides`` file (the remake's differences, by hand) and then every ``*.toml`` in the folder of the same
    name (``remake.toml``, then ``remake/*.toml`` sorted by name) are applied last: :func:`apply_overrides`."""
    meta = _read(directory / "world.toml")
    spec: dict[str, Any] = {"start": meta["start"], "goal": meta["goal"], "regions": [], "locations": {}}
    for name in ("items", "helpers"):
        spec[name] = _read(directory / f"{name}.toml")[name]
    settings = _read(directory / "settings.toml")
    for name in ("settings", "tricks", "flags"):
        spec[name] = settings.get(name, {})
    for name in ("settings", "items"):
        both = sorted(spec[name].keys() & meta.get(name, {}).keys())
        if both:
            raise WorldError(f"world.toml [{name}] repeats generated entries: {both}")
        spec[name] = spec[name] | meta.get(name, {})
    spec["progressive"] = meta.get("progressive", {})
    for file in meta["files"]:
        data = _read(directory / file)
        spec["regions"].extend(data.get("region", []))
        for location, info in data.get("locations", {}).items():
            if location in spec["locations"]:
                raise WorldError(f"{file}: location {location!r} is described twice")
            spec["locations"][location] = info
    if "overrides" in meta:
        main = directory / meta["overrides"]
        more = sorted((main.parent / main.stem).glob("*.toml"), key=lambda path: path.name)
        apply_overrides(spec, [(path.relative_to(directory).as_posix(), _read(path)) for path in [main, *more]])
    return spec


# Fields an override may set, besides ``source``. A location's ``rule`` needs ``was``; ``region`` moves it.
_LOCATION_FIELDS = frozenset(
    {"rule", "was", "new", "type", "vanilla", "vanilla_fixed", "n64_only", "area", "keep_vanilla", "region"}
)
_REGION_FIELDS = frozenset({"area", "dungeon", "scene", "hint", "time_passes", "provides_time"})
_RULE_FIELDS = frozenset({"rule", "was", "new"})
_TABLES = ("regions", "locations", "exits", "events", "key_counts", "items")


def apply_overrides(spec: dict[str, Any], files: Sequence[tuple[str, Mapping[str, Any]]]) -> None:
    """Apply the remake's differences, ``(label, table)`` per overrides file, to a spec merged from the translated
    files, in place. Every entry needs a ``source`` (why, with the evidence), and one entry (a region, a location,
    an exit, an event, a key count) may be set in one file only.

    ``[regions."<name>"]``: a region the translation lacks (a remake room OoT Randomizer folds into another), with
    ``area``, ``dungeon``, ``scene``, ``hint``, ``time_passes``, ``provides_time`` as a translated region has them.

    ``[locations."<name>"]``: any of ``rule`` (the remake's requirement; ``was`` must repeat the translated rule, so
    a change upstream is noticed), ``region`` (the region it moves to), ``type`` (the remake's kind of check, as an
    OoT Randomizer location type), ``vanilla`` (the remake's vanilla item), ``vanilla_fixed``, ``n64_only``,
    ``area`` (the census area, where the check lies outside its region's Banc folder) and ``keep_vanilla`` (the
    reason a check of a shuffled type keeps its vanilla item).

    ``[exits."<region>"."<target>"]`` and ``[events."<region>"."<event>"]``: ``rule`` with ``was`` (the translated
    rule it replaces) or with ``new = true`` (an exit or event the translation lacks).

    ``[key_counts]``: ``"<key item>" = { count, source }``, the number of that key the remake has; a rule asking for
    more asks for that many (:class:`~clawshot.world.rules.Compiler`).

    ``[items."<name>"]``: ``alias = ["<item>", count]``, a count of another item that collecting this one adds
    (the remake's Din's Fire carries a magic meter), for an item that has no alias yet.
    """
    owner: dict[tuple[str, ...], str] = {}
    for label, overrides in files:
        unknown_tables = sorted(set(overrides) - set(_TABLES))
        if unknown_tables:
            raise WorldError(f"{label}: unknown tables {unknown_tables}")
        for table in _TABLES:
            for key in _entry_keys(overrides.get(table, {}), table in ("exits", "events"), f"{label}: [{table}]"):
                if (table, *key) in owner:
                    raise WorldError(f"{label}: {table} {' -> '.join(key)!r} is also set in {owner[(table, *key)]}")
                owner[(table, *key)] = label

    regions = {region["name"]: region for region in spec["regions"]}
    for label, overrides in files:
        for name, fields in overrides.get("regions", {}).items():
            where = f"{label}: region {name!r}"
            _check_fields(fields, _REGION_FIELDS, where)
            if name in regions:
                raise WorldError(f"{where} is already in the world")
            region = {"name": name, **fields, "events": {}, "locations": {}, "exits": {}}
            spec["regions"].append(region)
            regions[name] = region

    for label, overrides in files:
        for kind, singular in (("exits", "exit to"), ("events", "event")):
            for region_name, entries in overrides.get(kind, {}).items():
                if region_name not in regions:
                    raise WorldError(f"{label}: {kind} of region {region_name!r}, which is not in the world")
                rules = regions[region_name].setdefault(kind, {})
                for name, fields in entries.items():
                    where = f"{label}: region {region_name!r}, {singular} {name!r}"
                    _check_fields(fields, _RULE_FIELDS, where)
                    if "rule" not in fields or ("was" in fields) == bool(fields.get("new")):
                        raise WorldError(f"{where}: needs rule, and was (a change) or new = true (an addition)")
                    if fields.get("new"):
                        if name in rules:
                            raise WorldError(f"{where}: new, but the region has it already")
                    else:
                        _check_was(rules, name, fields["was"], where)
                    rules[name] = {"rule": fields["rule"], "source": fields["source"]}

    holder: dict[str, dict[str, Any]] = {}
    for region in spec["regions"]:
        for name in region.get("locations", {}):
            holder[name] = region
    for label, overrides in files:
        for name, fields in overrides.get("locations", {}).items():
            where = f"{label}: location {name!r}"
            _check_fields(fields, _LOCATION_FIELDS, where)
            if fields.get("new"):
                if name in spec["locations"] or name in holder:
                    raise WorldError(f"{where}: new, but the world has it already")
                if "was" in fields or any(key not in fields for key in ("rule", "region", "type", "vanilla")):
                    raise WorldError(f"{where}: new needs rule, region, type and vanilla, without was")
                target = regions.get(fields["region"])
                if target is None:
                    raise WorldError(f"{where}: region {fields['region']!r} is not in the world")
                target.setdefault("locations", {})[name] = fields["rule"]
                holder[name] = target
                spec["locations"][name] = {k: v for k, v in fields.items() if k not in ("new", "region", "rule")}
                continue
            if name not in spec["locations"] or name not in holder:
                raise WorldError(f"{where} is not in the world")
            if ("rule" in fields) != ("was" in fields):
                raise WorldError(f"{where}: rule and was go together")
            rules = holder[name]["locations"]
            if "rule" in fields:
                _check_was(rules, name, fields["was"], where)
                rules[name] = fields["rule"]
            if "region" in fields:
                target = regions.get(fields["region"])
                if target is None:
                    raise WorldError(f"{where}: region {fields['region']!r} is not in the world")
                target.setdefault("locations", {})[name] = rules.pop(name)
                holder[name] = target
            info = dict(spec["locations"][name])
            info.update({k: v for k, v in fields.items() if k not in ("rule", "was", "new", "region", "source")})
            info["override"] = fields["source"]
            spec["locations"][name] = info

    counts: dict[str, int] = {}
    for label, overrides in files:
        for item, entry in overrides.get("key_counts", {}).items():
            if item not in spec["items"] or not isinstance(entry.get("count"), int) or not entry.get("source"):
                raise WorldError(f"{label}: key_counts {item!r} needs a known item, a count and a source")
            counts[item] = entry["count"]
    spec["key_counts"] = counts

    for label, overrides in files:
        for name, fields in overrides.get("items", {}).items():
            where = f"{label}: item {name!r}"
            _check_fields(fields, frozenset({"alias"}), where)
            info = spec["items"].get(name)
            if info is None:
                raise WorldError(f"{where} is not in the world")
            if info.get("alias"):
                raise WorldError(f"{where} already counts as {info['alias']}")
            alias = fields.get("alias")
            if not (
                isinstance(alias, list)
                and len(alias) == 2
                and alias[0] in spec["items"]
                and isinstance(alias[1], int)
                and alias[1] >= 1
            ):
                raise WorldError(f"{where}: alias must be [a known item, a count of at least 1], not {alias!r}")
            spec["items"][name] = {**info, "alias": list(alias)}


def _entry_keys(table: Mapping[str, Any], nested: bool, where: str) -> list[tuple[str, ...]]:
    """The keys of an overrides table: ``(name,)``, or ``(region, name)`` for exits and events."""
    if not nested:
        return [(name,) for name in table]
    keys = []
    for region, entries in table.items():
        if not isinstance(entries, Mapping) or not all(isinstance(fields, Mapping) for fields in entries.values()):
            raise WorldError(f'{where}: {region!r} must hold one table per name ("<region>"."<name>")')
        keys.extend((region, name) for name in entries)
    return keys


def _check_fields(fields: Mapping[str, Any], allowed: frozenset[str], where: str) -> None:
    unknown = sorted(set(fields) - allowed - {"source"})
    if unknown:
        raise WorldError(f"{where}: unknown fields {unknown}")
    if not fields.get("source"):
        raise WorldError(f"{where}: no source")


def _check_was(rules: Mapping[str, Any], name: str, was: str, where: str) -> None:
    if name not in rules:
        raise WorldError(f"{where} is not in the world")
    current, _ = _rule_entry(rules[name], where)
    if " ".join(current.split()) != " ".join(was.split()):
        raise WorldError(f"{where}: was {was!r}, but the translated rule is {current!r}")


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


def _progressive_tiers(table: Mapping[str, list[str]], items: dict[str, Item]) -> dict[str, list[str]]:
    """Add an item for each tier of each progressive item: tier ``n`` (from 1) counts as ``n`` of the progressive
    item, so every rule that asks for ``(Progressive_Hookshot, 2)`` reads a Longshot as well."""
    for progressive, tiers in table.items():
        if progressive not in items:
            raise WorldError(f"[progressive]: {progressive!r} is not in the item table")
        base = items[progressive]
        for n, tier in enumerate(tiers, start=1):
            if tier in items:
                raise WorldError(f"[progressive]: tier {tier!r} of {progressive!r} is already an item")
            items[tier] = Item(tier, base.type, base.progression, base.priority, alias=(progressive, n))
    return dict(table)


def _fixed_vanilla(vanilla: str | None, fixed: str | None, progressive: Mapping[str, list[str]], where: str) -> Any:
    """The vanilla item when each check gives one fixed item: ``vanilla_fixed`` where given; a progressive item
    without it is an error, since which tier the check gives is not known."""
    if fixed is not None:
        if vanilla in progressive and fixed not in progressive[vanilla]:
            raise WorldError(f"{where}: vanilla_fixed {fixed!r} is not a tier of {vanilla!r}")
        return fixed
    if vanilla in progressive:
        raise WorldError(f"{where}: vanilla item {vanilla!r} is progressive; say which tier (vanilla_fixed)")
    return vanilla


def build_world(spec: Mapping[str, Any], logic: Mapping[str, Any] | None = None) -> World:
    """Compile every rule of ``spec`` under the logic settings ``logic`` (defaults from the spec)."""
    settings = resolve_settings(spec, logic)
    items = {name: _item(name, info) for name, info in spec.get("items", {}).items()}
    progressive = _progressive_tiers(spec.get("progressive", {}), items)
    # Without the setting, a world reads OoT Randomizer's vanilla items as they are (progressive).
    fixed_items = not settings.get("progressive_items", True)
    facts = ItemFacts(
        names=frozenset(items),
        bottles=tuple(n for n, i in items.items() if i.bottle),
        medallions=tuple(n for n, i in items.items() if i.medallion),
        stones=tuple(n for n, i in items.items() if i.stone),
    )
    helpers = {name: _rule_entry(value, f"helper {name!r}")[0] for name, value in spec.get("helpers", {}).items()}
    compiler = Compiler(facts, helpers, settings, dict(spec.get("key_counts", {})))
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
                area=data.get("area"),
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
                if fixed_items:
                    vanilla = _fixed_vanilla(vanilla, info.get("vanilla_fixed"), progressive, where)
                if vanilla is not None and vanilla not in items:
                    raise WorldError(f"{where}: vanilla item {vanilla!r} is not in the item table")
                location = Location(
                    name=location_name,
                    region=name,
                    rule=compiler.compile(text, name, where),
                    type=info["type"],
                    vanilla=vanilla,
                    source=info.get("source", region.source),
                    area=info.get("area", region.area),
                    n64_only=info.get("n64_only"),
                    keep_vanilla=info.get("keep_vanilla"),
                    override=info.get("override"),
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
        start_items=_start_items(settings, items),
        goal=goal,
        dangling_exits=[(r.name, e.target) for r in regions.values() for e in r.exits if e.target not in regions],
        undefined_events=sorted(compiler.events_named - defined),
        missing_regions=sorted({e.region for e in events if e.region not in regions}),
    )


OCARINA_BUTTONS = (
    "Ocarina A Button",
    "Ocarina C down Button",
    "Ocarina C right Button",
    "Ocarina C left Button",
    "Ocarina C up Button",
)


def _start_items(settings: Mapping[str, Any], items: Mapping[str, Item]) -> tuple[str, ...]:
    """The ocarina buttons when notes are not shuffled and Scarecrow's Song when it is free.

    The remake gives no starting dungeon keys; Fire Temple keys must be collected from real checks.
    Only items the world's item table has are given.
    """
    held: list[str] = []
    if not settings.get("shuffle_individual_ocarina_notes", False):
        held.extend(OCARINA_BUTTONS)
    if settings.get("scarecrow_behavior") == "free":
        held.append("Scarecrow Song")
    return tuple(name for name in held if name in items)


def load_world(logic: Mapping[str, Any] | None = None, directory: Path = DATA_DIR) -> World:
    return build_world(load_spec(directory), logic)
