"""Which open checks are in logic: reachable, by the seed's own logic, with what the save holds.

    loaded = load_world(seed)                     # once per loaded seed; never reads the dump
    logic = SeedLogic(loaded)
    state = build_state(seed, save, logic=logic)  # adds state["logic"]

The world is the one the generator searched: the spoiler's settings string through ``app.schema.validate`` and the
seed pipeline's shared builder (``clawshot.patch.logic_world``, spec ``tracker-in-logic`` D15). It is rebuilt only
when the spoiler's ``generator`` is this installed version and every location the spoiler names exists in the rebuilt
world (D14); otherwise logic is unavailable with a reason, and item tracking carries on.

State fields:

- ``state["logic"]``: ``available`` (bool); ``reason`` (why not, or None); ``unknown_items`` (ids of the save cells
  that could not be read, which count as not held, D4: the result may be conservative); ``save_age`` (``child``,
  ``adult`` or None, from ``Sequence_IsChildhood``, :func:`save_age`).
- each open check (not collected, or unknown and not marked done by hand) gains ``in_logic``: ``{child, adult,
  either}``, the first two from ``Search.can_access(location, age)``, ``either`` from ``can_access(location)`` with
  no age. Collected and marked checks have none.
- each area gains ``in_logic``: ``{child, adult, either}``, the number of its open checks in logic for each.
- ``state["vanilla_areas"]`` (spec D19, section 8): the fixed vanilla pick-ups, grouped by area like ``areas``
  (``name``, ``total``, ``collected``, ``unknown``, ``marked``, ``in_logic``, ``checks``). These are locations the
  seed does not shuffle whose vanilla item is progression (:func:`vanilla_rows`, scope :data:`VANILLA_SCOPE`), so the
  player sees a pick-up such as Ruto's Letter that gates an area. Each row has ``vanilla: true`` and always names its
  item (the settings decide it, not the seed); ``collected`` comes from the logic inventory
  (:func:`vanilla_collected`). Absent while logic is unavailable. ``areas`` and its counts are unchanged by them.

Nothing is written anywhere: the seed's spoiler and the save are only read.
"""

import json
import tomllib
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import Any

from clawshot import save as save_format
from clawshot.app.schema import validate
from clawshot.generate import Settings
from clawshot.patch.logic_world import logic_world
from clawshot.tracker import seeds, state
from clawshot.tracker.seeds import DUNGEON_INFO, OTHER_AREA, Seed, installed_version
from clawshot.world.model import Location, World
from clawshot.world.rules import ADULT, CHILD
from clawshot.world.search import Search

CHILDHOOD = "Sequence_IsChildhood"
AGE_KEYS = ("child", "adult", "either")
MAPPING_TOML = Path(__file__).resolve().parents[1] / "data" / "tracker_logic.toml"
_FAMILY_PLURALS = {"small_key": "small keys", "boss_key": "boss keys", "map": "maps", "compass": "compasses"}
VANILLA_SCOPE = "unique"
"""Which fixed vanilla pick-ups get a row (spec D19, Q3): ``unique``, those whose vanilla item no other world location
gives (proposed by Claude, awaiting the maintainer), or ``all``, every progression vanilla item."""
VANILLA_SKIPPED_TYPES = frozenset({"Shop", "Event", "Drop"})
"""Location types never listed as vanilla rows: shelves restock (no one-time check), events and drops are derived by
the search itself."""


@dataclass(frozen=True)
class CellMap:
    """What one held tracker cell is worth to the logic (``data/tracker_logic.toml`` ``[cells.<id>]``)."""

    item: str | None = None
    count: bool = False
    tiers: tuple[Mapping[str, int], ...] = ()
    acquired: bool = False
    requires: str | None = None

    def grants(self, tier: int) -> dict[str, int]:
        """Logic item -> copies for the cell held at ``tier`` (1 = lowest); a single cell's tier is 1."""
        if tier <= 0:
            return {}
        if self.tiers:
            return dict(self.tiers[min(tier, len(self.tiers)) - 1])
        return {self.item: 1} if self.item else {}

    def names(self) -> set[str]:
        return {name for grants in self.tiers for name in grants} | ({self.item} if self.item else set())


@dataclass(frozen=True)
class StoryStep:
    flag: str
    source: str


@dataclass(frozen=True)
class Mapping_:
    """The whole mapping file, parsed."""

    cells: Mapping[str, CellMap]
    bottles: Mapping[str, str]
    hearts: Mapping[str, Any]
    tokens: Mapping[str, str]
    dungeon_items: Mapping[str, str]
    story: Mapping[str, StoryStep]
    unmapped: Mapping[str, str] = field(default_factory=dict)
    stock: Mapping[str, Mapping[str, str]] = field(default_factory=dict)  # actor -> {item, label}

    def logic_names(self) -> set[str]:
        """Every logic name a save can grant, dungeon items named for each of ``seeds.DUNGEON_INFO``'s dungeons."""
        names = {name for cell in self.cells.values() for name in cell.names()}
        names |= {entry["item"] for entry in self.stock.values()}
        names |= {self.bottles["bottle"], self.bottles["letter"], self.hearts["item"], self.tokens["item"]}
        names |= {template.format(dungeon=d) for template in self.dungeon_items.values() for d in DUNGEON_INFO}
        return names | set(self.story)


@cache
def load_mapping() -> Mapping_:
    """``data/tracker_logic.toml``, parsed (see its header for the keys)."""
    with MAPPING_TOML.open("rb") as stream:
        data = tomllib.load(stream)
    cells = {
        cell_id: CellMap(
            item=info.get("item"),
            count=bool(info.get("count", False)),
            tiers=tuple(dict(tier) for tier in info.get("tiers", ())),
            acquired=bool(info.get("acquired", False)),
            requires=info.get("requires"),
        )
        for cell_id, info in data["cells"].items()
    }
    story = {name: StoryStep(info["flag"], info["source"]) for name, info in data["story"].items()}
    return Mapping_(
        cells=cells,
        bottles=dict(data["bottles"]),
        hearts=dict(data["hearts"]),
        tokens=dict(data["tokens"]),
        dungeon_items=dict(data["dungeon_items"]),
        story=story,
        unmapped=dict(data["unmapped"]),
        stock={actor: dict(entry) for actor, entry in data.get("stock", {}).items()},
    )


def world_spec() -> Mapping[str, Any] | None:
    """The world spec seeds are made from; None is the generator's own (``world.load.load_spec``). Tests replace
    this function."""
    return None


@dataclass(frozen=True)
class LogicWorld:
    """The seed's logic world, or why there is none."""

    available: bool
    reason: str | None = None
    settings: Settings | None = None
    world: World | None = None


def _unavailable(reason: str) -> LogicWorld:
    return LogicWorld(False, reason)


def load_world(seed: Seed) -> LogicWorld:
    """Rebuild the world the seed's generator searched, or say why it cannot be (D14)."""
    expected = f"clawshot {installed_version()}"
    if not seed.generator:
        return _unavailable("The spoiler does not name the generator that made this seed.")
    if seed.generator != expected:
        return _unavailable(
            f"This seed was made by {seed.generator}; in-logic needs a seed made by {expected}, the version reading it."
        )
    if not seed.settings_string:
        return _unavailable("The spoiler has no settings string to rebuild the seed's logic from.")
    spec = world_spec()
    try:
        settings = validate(text=seed.settings_string, spec=spec)
        settings, world = logic_world(settings, spec)
    except Exception as error:  # noqa: BLE001 - any failure to rebuild disables logic, never the tracker
        return _unavailable(f"The seed's settings could not be rebuilt into its logic: {error}")
    missing = [check.location for check in seed.checks if check.location not in world.locations]
    if missing:
        more = f" and {len(missing) - 1} more" if len(missing) > 1 else ""
        return _unavailable(
            f"The spoiler names {missing[0]!r}{more}, which this version's logic does not have: the seed was made "
            "from different world data."
        )
    return LogicWorld(True, None, settings, world)


@dataclass(frozen=True)
class Inventory:
    """The save's holdings as logic counts (``counts``, sorted by name) and the ids of the cells the save could not
    read (``unknown``, sorted; they contribute nothing, D4)."""

    counts: Mapping[str, int]
    unknown: tuple[str, ...]

    def as_json(self) -> str:
        return json.dumps({"counts": dict(self.counts), "unknown": list(self.unknown)}, sort_keys=True)


def _cells(save: save_format.Save | None) -> dict[str, dict[str, Any]]:
    return {cell["id"]: cell for cell in (*state.items(save), *state.songs(save), *state.rewards(save))}


def _tier_actors() -> dict[str, tuple[str, ...]]:
    return {cell_id: tuple(actor for _, actor in tiers) for cell_id, _, tiers, _ in state.TIERS}


def inventory(seed: Seed, save: save_format.Save | None, world: World, mapping: Mapping_ | None = None) -> Inventory:
    """The logic inventory the save holds (D1-D4, D17, D18): only what the save reads, never the spoiler's
    placements. Per logic name the largest grant of any source counts; names the world lacks are dropped."""
    mapping = mapping or load_mapping()
    reader = state._Reader(save)
    cells = _cells(save)
    tier_actors = _tier_actors()
    counts: dict[str, int] = {}
    unknown: set[str] = set()

    def grant(grants: Mapping[str, int]) -> None:
        for name, copies in grants.items():
            counts[name] = max(counts.get(name, 0), copies)

    for cell_id, cell_map in mapping.cells.items():
        cell = cells[cell_id]
        if cell_map.requires is not None and cells[cell_map.requires]["held"] is not True:
            if cells[cell_map.requires]["held"] is None and cell["held"] is not False:
                unknown.add(cell_id)
            continue
        if cell_map.acquired and cell_map.tiers:
            # Each tier on its own: held now (stock) or ever acquired (IsGet) (D2).
            for n, actor in enumerate(tier_actors[cell_id], start=1):
                held, ever = state._held(reader.stock(actor)), reader.isget(actor)
                if held or ever:
                    grant(cell_map.grants(n))
                elif held is None and ever is None:
                    unknown.add(cell_id)
            continue
        if cell["held"] is None and not (cell_map.acquired and cell["ever"]):
            unknown.add(cell_id)
            continue
        if cell_map.tiers:
            grant(cell_map.grants(cell["tier"] or 0))
        elif cell["held"] or (cell_map.acquired and cell["ever"]):
            grant({cell_map.item: cell["count"] or 0} if cell_map.count else cell_map.grants(1))

    for actor, entry in mapping.stock.items():
        held = reader.stock(actor)
        if held is None:
            unknown.add(entry["label"])
        elif held > 0:
            grant({entry["item"]: 1})

    contents = cells["bottles"]["contents"]
    letter_ever = reader.isget(mapping.bottles["letter_actor"])
    if contents is None:
        unknown.add("bottles")
    else:
        letters = sum(slot["content"] == "Ruto's Letter" for slot in contents)
        grant({mapping.bottles["bottle"]: len(contents) - letters})
        grant({mapping.bottles["letter"]: 1 if letters or letter_ever else 0})
    if contents is None and letter_ever:
        grant({mapping.bottles["letter"]: 1})

    containers = state.hearts(save)["containers"]
    if containers is None:
        unknown.add("hearts")
    else:
        per, start = mapping.hearts["pieces_per_heart"], mapping.hearts["starting_hearts"]
        grant({mapping.hearts["item"]: max(0, containers - start) * per})
    tokens = reader.stock("Item_Token_Gold")
    if tokens is None:
        unknown.add("tokens")
    else:
        grant({mapping.tokens["item"]: tokens})

    families = {
        "small_key": seed.small_keys,
        "boss_key": seed.boss_keys,
        "map": seed.maps,
        "compass": seed.compasses,
    }
    for entry in state.dungeons(seed, save):
        dungeon = entry["dungeon"]
        values = {
            "small_key": entry["small_keys"]["found"],
            "boss_key": entry["boss_key"],
            "map": entry["map"],
            "compass": entry["compass"],
        }
        for family, value in values.items():
            if value is None:
                if families[family].get(dungeon, 0) > 0:
                    unknown.add(f"{dungeon} {_FAMILY_PLURALS[family]}")
                continue
            grant({mapping.dungeon_items[family].format(dungeon=dungeon): int(value)})

    for name, step in mapping.story.items():
        value = reader.flag(step.flag)
        if value is None:
            unknown.add(f"story: {name}")
        elif value:
            grant({name: 1})

    known = set(world.items) | {event.name for event in world.events}
    kept = {name: n for name, n in sorted(counts.items()) if n > 0 and name in known}
    return Inventory(kept, tuple(sorted(unknown)))


def search_items(inv: Inventory, world: World) -> list[str]:
    """The items to hand ``Search`` as its constructor ``items`` (D16), sorted. ``Search`` adds the world's starting
    items itself, so each name is fed as the save's count less the starting count (never below 0): the search counts
    the larger of the two (P5.b)."""
    start = Counter(world.start_items)
    return [name for name, n in inv.counts.items() for _ in range(max(0, n - start[name]))]


@dataclass(frozen=True)
class VanillaRow:
    """One fixed vanilla pick-up (spec D19). ``shared``: a shuffled check of the seed can also give the item, so
    holding it does not say this location was taken (8.3)."""

    location: str
    label: str
    where: str
    area: str
    dungeon: str | None
    item: str
    item_label: str
    shared: bool


def vanilla_rows(seed: Seed, world: World, scope: str | None = None) -> tuple[VanillaRow, ...]:
    """The seed's fixed vanilla pick-ups in world order (8.1): world locations not in the spoiler's placements whose
    vanilla item is progression, not N64-only, not of :data:`VANILLA_SKIPPED_TYPES`, and in ``scope``
    (:data:`VANILLA_SCOPE` by default)."""
    from clawshot.generate import names

    scope = scope or VANILLA_SCOPE
    if scope not in ("unique", "all"):
        raise ValueError(f"unknown vanilla scope {scope!r}")
    placed = {check.location for check in seed.checks}
    placed_items = {check.item for check in seed.checks}
    sources = Counter(loc.vanilla for loc in world.locations.values() if loc.vanilla is not None)
    places = seeds.location_index()
    catalog = seeds._catalog()
    shown = names.item_names()
    rows = []
    for name, loc in world.locations.items():
        item = world.items.get(loc.vanilla) if loc.vanilla is not None else None
        if name in placed or item is None or not item.progression or loc.n64_only is not None:
            continue
        if loc.type in VANILLA_SKIPPED_TYPES or (scope == "unique" and sources[loc.vanilla] != 1):
            continue
        place = places.get(name)
        described = catalog.get(name)
        rows.append(
            VanillaRow(
                location=name,
                label=described.name if described else name,
                where=described.where if described else "",
                area=place.area if place else OTHER_AREA,
                dungeon=place.dungeon if place else world.regions[loc.region].dungeon,
                item=loc.vanilla,
                item_label=shown.get(loc.vanilla, loc.vanilla),
                shared=loc.vanilla in placed_items,
            )
        )
    return tuple(rows)


def _unknown_sources(mapping: Mapping_) -> dict[str, set[str]]:
    """Logic name -> the :class:`Inventory` ``unknown`` ids whose cells could grant it."""
    out: dict[str, set[str]] = {}

    def add(tag: str, names: set[str]) -> None:
        for name in names:
            out.setdefault(name, set()).add(tag)

    for cell_id, cell_map in mapping.cells.items():
        add(cell_id, cell_map.names())
    for entry in mapping.stock.values():
        add(entry["label"], {entry["item"]})
    add("bottles", {mapping.bottles["bottle"], mapping.bottles["letter"]})
    add("hearts", {mapping.hearts["item"]})
    add("tokens", {mapping.tokens["item"]})
    for family, template in mapping.dungeon_items.items():
        for dungeon in DUNGEON_INFO:
            add(f"{dungeon} {_FAMILY_PLURALS[family]}", {template.format(dungeon=dungeon)})
    for name in mapping.story:
        add(f"story: {name}", {name})
    return out


def vanilla_collected(
    row: VanillaRow, inv: Inventory, world: World, mapping: Mapping_ | None = None
) -> tuple[bool | None, str | None]:
    """(collected, reason when unknown) for a vanilla row (8.3), from the logic inventory: True when it counts the
    row's item (a fixed tier of a progressive item: the chain at that tier), False when every cell that could grant
    it was read, None when one was not, the save has no cell for the item, or a shuffled check can also give it."""
    mapping = mapping or load_mapping()
    if row.shared:
        return None, f"A shuffled check of this seed can also give {row.item_label}."
    known = mapping.logic_names()
    name, need = row.item, 1
    if name not in known:
        item = world.items[name]
        if not (item.tier and item.alias and item.alias[0] in known):
            return None, f"The tracker does not read {row.item_label} from the save."
        name, need = item.alias
    if inv.counts.get(name, 0) >= need:
        return True, None
    if _unknown_sources(mapping).get(name, set()) & set(inv.unknown):
        return None, f"The save could not be read for {row.item_label}."
    return False, None


def save_age(save: save_format.Save | None) -> str | None:
    """The save's age from ``Sequence_IsChildhood`` (Bool, file 0, default true; plans/rounds/
    r18-master-sword-design.md): ``child`` when true, ``adult`` when false, None when unreadable. Natural play keeps it
    right; Longshot's debug age switch does not change it."""
    value = None if save is None else save.flag(CHILDHOOD)
    return None if value is None else CHILD if value else ADULT


class SeedLogic:
    """One loaded seed's logic, kept by the tracker session for as long as the seed stays loaded. The search is
    rebuilt only when the inventory changes (3.5)."""

    def __init__(self, loaded: LogicWorld) -> None:
        self.loaded = loaded
        self._key: str | None = None
        self._search: Search | None = None
        self._vanilla: tuple[VanillaRow, ...] | None = None

    def vanilla(self, seed: Seed) -> tuple[VanillaRow, ...]:
        """The seed's vanilla rows, built once per loaded seed (8.1); none while logic is unavailable."""
        if not self.loaded.available:
            return ()
        if self._vanilla is None:
            self._vanilla = vanilla_rows(seed, self.loaded.world)
        return self._vanilla

    def search(self, inv: Inventory) -> Search:
        """The search for this inventory, fed as the generator feeds assumed items (D16)."""
        key = inv.as_json()
        if self._search is None or key != self._key:
            self._key, self._search = key, Search(self.loaded.world, search_items(inv, self.loaded.world))
        return self._search

    def annotate(
        self, state: dict[str, Any], seed: Seed, save: save_format.Save | None, marked: frozenset[str] = frozenset()
    ) -> None:
        """Add ``state["logic"]`` and, while logic is available, each open check's ``in_logic`` and each area's
        ``in_logic`` counts. Open: not collected, or unknown and not ``marked`` (D5)."""
        logic: dict[str, Any] = {
            "available": self.loaded.available,
            "reason": self.loaded.reason,
            "unknown_items": [],
            "save_age": save_age(save),
        }
        state["logic"] = logic
        if not self.loaded.available:  # no vanilla rows either, and no other field added (1.3, 8.1)
            return
        world = self.loaded.world
        inv = inventory(seed, save, world)
        logic["unknown_items"] = list(inv.unknown)
        search = self.search(inv)
        for area in state["areas"]:
            area["in_logic"] = _flag_open(area["checks"], world, search, marked)
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in self.vanilla(seed):
            collected, reason = vanilla_collected(row, inv, world)
            entry: dict[str, Any] = {
                "id": row.location,
                "label": row.label,
                "where": row.where,
                "kind": "vanilla",
                "dungeon": row.dungeon,
                "collected": collected,
                "basis": "inventory" if collected is not None else None,
                "vanilla": True,
                "item": row.item,
                "item_label": row.item_label,
            }
            if collected is None:
                entry["reason"] = reason
                if row.location in marked:
                    entry["marked"] = True
            grouped.setdefault(row.area, []).append(entry)
        state["vanilla_areas"] = [
            {
                "name": name,
                "collected": sum(c["collected"] is True for c in checks),
                "total": len(checks),
                "unknown": sum(c["collected"] is None for c in checks),
                "marked": sum(c.get("marked", False) for c in checks),
                "in_logic": _flag_open(checks, world, search, marked),
                "checks": checks,
            }
            for name, checks in grouped.items()
        ]


def _flag_open(checks: list[dict[str, Any]], world: World, search: Search, marked: frozenset[str]) -> dict[str, int]:
    """Give each open check ``in_logic`` (3.1, 3.2) and return how many are in logic per age (3.4)."""
    totals = dict.fromkeys(AGE_KEYS, 0)
    for entry in checks:
        if entry["collected"] is True or (entry["collected"] is None and entry["id"] in marked):
            continue
        location: Location = world.locations[entry["id"]]
        flags = {
            "child": search.can_access(location, CHILD),
            "adult": search.can_access(location, ADULT),
            "either": search.can_access(location),
        }
        entry["in_logic"] = flags
        for key, value in flags.items():
            totals[key] += value
    return totals
