"""Gossip Stone hints for a filled seed: which stone says what (round 7).

    hints = choose(seed, "always", "balanced")      # one Hint per live stone, in world order
    lines = {hint.label: text(hint) for hint in hints}

The kinds, their weights and Clawshot's wording are data (``data/hints.toml``); the method follows OoT Randomizer's
``Hints.py`` (MIT, at ``526b4c8d``):

- **Readable stones.** A stone is read where its world rule lets Link reach it (``World.hint_stones``); with
  ``mode = "mask"`` only as child holding the Mask of Truth (the remake asks for the mask worn, which only child Link
  can), as the game does without the ``patch.text.gossip_without_mask`` edit. Then no hint names a location whose
  item the mask cannot be reached without (:func:`mask_prerequisites`; Kareem, D26): the player holds those before
  any stone speaks, so Way of the Hero and the location hints start from the mask.
- **Where it matters.** A hint naming a location goes only on a stone readable with every other placed item
  collected (OoT Randomizer's ``can_reach_hint``): the stone never needs the item it points at. Hints naming no
  location (barren areas, junk) go on any stone; junk takes the unreadable stones first.
- **Way of the Hero.** A shuffled location is required when the goal cannot be reached with its item withheld.
  Restricted dungeon items (a dungeon's own keys, maps and compasses with ``dungeon_items = "own_dungeon"``) are
  not hinted this way, as in OoT Randomizer.
- **Barren.** An area none of whose shuffled locations is required or holds a major item (progression, not a shop
  refill, Gold Skulltula token, heart, Bombchu pack or restricted dungeon item). Stricter than OoT Randomizer, which
  also calls an area barren when its major items are surplus copies.
- **Areas** are a region's ``hint`` or ``dungeon``; a region with neither takes the area of the nearest region with
  one that has an exit into it, never through ``Root`` (OoT Randomizer's ``HintArea.at``; exits closed by a
  ``False`` rule are not followed).
- **Location hints (D29).** Item, always, sometimes and random hints name only progression, hearts and permanent
  upgrades, never ammo, refills, Buy items or bottle contents, even when those are progression in the logic.
  This deliberately differs from OoT Randomizer's random/sometimes hints. Item hints additionally require its
  major-item set (``get_good_item_hint``, ``Hints.py:882-891``), so never name hearts or normal capacity upgrades.
  Barren and Way of the Hero keep their separate required/major-item definition.

Only shuffled locations are hinted (vanilla ones are known). Every stone gets one hint (``copies`` 1). The choices
use their own ``random.Random`` seeded from the seed number, so the fill's placements are not touched.
"""

import random
import tomllib
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

from clawshot.census.hints import stone_labels
from clawshot.world.model import Location, World
from clawshot.world.rules import CHILD, Rule
from clawshot.world.search import Search

if TYPE_CHECKING:
    from clawshot.generate import Seed

HINTS_TOML = Path(__file__).resolve().parents[1] / "data" / "hints.toml"
MODES = ("always", "mask")
KINDS = ("always", "woth", "barren", "item", "sometimes", "random", "junk")
MASK_OF_TRUTH = "Mask of Truth"
ROOT = "Root"
# Progression items that do not count as major for barren areas (OoT Randomizer's Item.majoritem at its defaults).
NOT_MAJOR_TYPES = frozenset({"Shop", "Event", "Drop", "Token", "Map", "Compass"})
# Shop refills ("Buy ...") are type Shop in OoT Randomizer; the remake's own refill sizes are added as plain items.
NOT_MAJOR_PREFIXES = ("Buy ", "Bombchus", "Heart Container", "Piece of Heart")
# D29's non-progression permanent upgrades in the world's item data. Fixed wallet/strength/etc. tiers inherit
# progression from their parent; these do not. Hearts are recognized separately, including their variants.
NAMED_UPGRADES = frozenset({"Deku Nut Capacity", "Deku Stick Capacity", "Bullet Bag (40)", "Quiver (40)"})
UNNAMED_TYPES = frozenset({"Drop", "Event", "Shop", "Refill"})
UNNAMED_PREFIXES = (
    "Buy ",
    "Rupee",
    "Bomb (",
    "Bombs (",
    "Bombchus",
    "Arrows (",
    "Deku Nuts (",
    "Deku Seeds (",
    "Deku Stick (",
    "Bottle with ",
)


class HintError(ValueError):
    pass


@dataclass(frozen=True)
class Hint:
    """What one stone says. ``area`` is a hint area key (``data/hints.toml`` ``[areas]``); ``location`` and ``item``
    are the world location and logic item a hint names; ``line`` is the junk line's index."""

    stone: str
    label: str
    kind: str
    area: str | None = None
    location: str | None = None
    item: str | None = None
    line: int | None = None


@cache
def load(path: Path = HINTS_TOML) -> dict[str, Any]:
    with path.open("rb") as stream:
        data = tomllib.load(stream)
    for name, distribution in data["distributions"].items():
        unknown = set(distribution["weights"]) - set(KINDS)
        if unknown:
            raise HintError(f"distribution {name}: unknown kinds {sorted(unknown)}")
    return data


def distributions() -> tuple[str, ...]:
    return tuple(load()["distributions"])


def hint_area(world: World, region: str) -> str | None:
    """The hint area of ``region``: its dungeon or ``hint``, else the nearest one it is entered from (breadth first,
    parents in world order, not through ``Root`` unless the region is ``Root``)."""
    parents = _parents(world)
    seen = {region}
    queue = [region]
    while queue:
        name = queue.pop(0)
        current = world.regions[name]
        area = current.dungeon or current.hint
        if area and (name != ROOT or region == ROOT):
            return area
        for parent in parents.get(name, ()):
            if parent not in seen:
                seen.add(parent)
                queue.append(parent)
    return None


def _parents(world: World) -> dict[str, list[str]]:
    parents: dict[str, list[str]] = {}
    for name, region in world.regions.items():
        for exit in region.exits:
            if exit.rule.test is not False and exit.target in world.regions:
                parents.setdefault(exit.target, []).append(name)
    return parents


def _readable(stone: Location, mode: str) -> Location:
    """``stone`` with the rule to read it: its world rule, and with ``mode = "mask"`` child Link holding the mask."""
    if mode == "always":
        return stone
    if mode != "mask":
        raise HintError(f"hint mode must be one of {MODES}, not {mode!r}")
    rule = stone.rule

    def test(counts: Mapping[str, int], age: str | None, tod: int) -> bool:
        return age == CHILD and counts.get(MASK_OF_TRUTH, 0) > 0 and rule.fn(counts, age, tod)

    reads = None if rule.reads is None else rule.reads | {MASK_OF_TRUTH}
    return replace(stone, rule=Rule(f"is_child and Mask_of_Truth and ({rule.text})", test, reads))


class _Searches:
    """Full searches of the seed's placements, each with at most one location's item withheld (cached)."""

    def __init__(self, seed: "Seed") -> None:
        self.seed = seed
        self._done: dict[str | None, Search] = {}

    def __call__(self, without: str | None = None) -> Search:
        if without is not None and not self.seed.world.items[self.seed.placements[without]].progression:
            without = None  # withholding an item that unlocks nothing changes nothing
        if without not in self._done:
            search = Search(self.seed.world)
            search.collect_spheres({k: v for k, v in self.seed.placements.items() if k != without})
            self._done[without] = search
        return self._done[without]

    def won(self, without: str | None = None) -> bool:
        world = self.seed.world
        return bool(world.goal(self(without).counts, None, world.start_tod))


def _restricted(seed: "Seed", item: str) -> bool:
    return seed.settings.dungeon_items == "own_dungeon" and seed.world.items[item].dungeon is not None


def _major(seed: "Seed", item: str) -> bool:
    info = seed.world.items[item]
    return (
        info.progression
        and info.type not in NOT_MAJOR_TYPES
        and not item.startswith(NOT_MAJOR_PREFIXES)
        and not _restricted(seed, item)
    )


def _worth_naming(world: World, item: str) -> bool:
    """D29's location-hint class, independent of whether an item keeps its area off the barren list."""
    info = world.items[item]
    if info.type in UNNAMED_TYPES or item.startswith(UNNAMED_PREFIXES) or item == "Blue Potion":
        return False
    return info.progression or item.startswith(("Piece of Heart", "Heart Container")) or item in NAMED_UPGRADES


def required_locations(seed: "Seed", searches: _Searches | None = None) -> list[str]:
    """Shuffled locations, in world order, whose item the goal cannot be reached without (OoT Randomizer's Way of the
    Hero), restricted dungeon items left out."""
    searches = searches or _Searches(seed)
    if not searches.won():
        raise HintError("the seed's goal cannot be reached with every item")
    collected = searches().collected
    return [
        name
        for name in seed.shuffled
        if name in collected
        and seed.world.items[seed.placements[name]].progression
        and not _restricted(seed, seed.placements[name])
        and not searches.won(name)
    ]


def mask_prerequisites(seed: "Seed", searches: _Searches | None = None) -> list[str]:
    """Shuffled locations, in world order, whose item the Mask of Truth cannot be reached without (the mask's own
    location among them): with ``mask`` hints the player holds them before any stone speaks. Empty when the mask
    cannot be reached at all."""
    searches = searches or _Searches(seed)
    if not searches().counts.get(MASK_OF_TRUTH, 0):
        return []
    return [
        name
        for name in seed.shuffled
        if seed.world.items[seed.placements[name]].progression and not searches(name).counts.get(MASK_OF_TRUTH, 0)
    ]


def choose(seed: "Seed", mode: str = "always", distribution: str = "balanced") -> tuple[Hint, ...]:
    """One hint per live stone of ``seed``'s world (a stone the remake has, linked to a message label), in world
    order. A world without stones gets none."""
    data = load()
    if distribution not in data["distributions"]:
        raise HintError(f"hint distribution must be one of {distributions()}, not {distribution!r}")
    plan = data["distributions"][distribution]
    world = seed.world
    labels = stone_labels()
    stones = {
        name: _readable(stone, mode)
        for name, stone in world.hint_stones.items()
        if stone.n64_only is None and name in labels
    }
    if not stones:
        return ()
    rng = random.Random(f"clawshot hints {seed.seed}")
    searches = _Searches(seed)
    full = searches()
    free = list(stones)
    rng.shuffle(free)
    hints: dict[str, Hint] = {}

    def place(kind: str, location: str | None = None, **fields: Any) -> bool:
        """Put a hint on the first free stone readable with ``location``'s item withheld."""
        search = searches(location) if location is not None else full
        for stone in free:
            if search.can_access(stones[stone]):
                free.remove(stone)
                item = seed.placements[location] if location is not None else None
                hints[stone] = Hint(stone, labels[stone], kind, location=location, item=item, **fields)
                return True
        return False

    area_of = {name: hint_area(world, world.locations[name].region) for name in seed.shuffled}
    hinted_locations: set[str] = set()
    hinted_areas: set[str] = set()
    dungeons = {"woth": 0, "barren": 0}
    limits = {"woth": plan.get("dungeon_woth_limit", 2), "barren": plan.get("dungeon_barren_limit", 1)}
    is_dungeon = {area: any(r.dungeon == area for r in world.regions.values()) for area in set(area_of.values())}

    hinted_items: set[str] = set()  # items an item hint named: one hint per item, not per copy

    def location_hint(kind: str, candidates: list[str]) -> bool:
        candidates = [name for name in candidates if name not in hinted_locations]
        if kind == "item":
            candidates = [name for name in candidates if seed.placements[name] not in hinted_items]
        while candidates:
            name = candidates.pop(rng.randrange(len(candidates)))
            hinted_locations.add(name)
            if place(kind, name, area=area_of[name]):
                if kind == "item":
                    hinted_items.add(seed.placements[name])
                return True
        return False

    required = required_locations(seed, searches)
    if mode == "mask":
        # A stone is read only once the mask is held: a hint about an item needed to get the mask would come too
        # late. Such locations are never named (the readability check alone would also refuse them).
        before_mask = set(mask_prerequisites(seed, searches))
        required = [name for name in required if name not in before_mask]
    else:
        before_mask = set()
    by_area: dict[str, list[str]] = {}
    for name in seed.shuffled:
        if area_of[name] is not None:
            by_area.setdefault(area_of[name], []).append(name)

    def woth() -> bool:
        candidates = [
            name
            for name in required
            if area_of[name] not in hinted_areas
            and area_of[name] is not None
            and not (is_dungeon[area_of[name]] and dungeons["woth"] >= limits["woth"])
        ]
        while candidates:
            name = candidates.pop(rng.randrange(len(candidates)))
            area = area_of[name]
            if place("woth", name, area=area):
                hinted_locations.add(name)
                hinted_areas.add(area)
                dungeons["woth"] += is_dungeon[area]
                return True
        return False

    def barren() -> bool:
        areas = [
            area
            for area, names in by_area.items()
            if area not in hinted_areas
            and not (is_dungeon[area] and dungeons["barren"] >= limits["barren"])
            and not any(name in required or _major(seed, seed.placements[name]) for name in names)
        ]
        if not areas:
            return False
        area = rng.choices(areas, weights=[len(by_area[a]) for a in areas])[0]
        if not place("barren", area=area):
            return False
        hinted_areas.add(area)
        dungeons["barren"] += is_dungeon[area]
        return True

    lists = data["lists"]
    named = [name for name in seed.shuffled if _worth_naming(world, seed.placements[name]) and name not in before_mask]
    always = [name for name in named if name in set(lists["always"])]
    hintable = [name for name in named if not _restricted(seed, seed.placements[name])]
    sometimes = [name for name in hintable if name in set(lists["sometimes"])]
    majors = [name for name in hintable if _major(seed, seed.placements[name])]
    junk_lines = len(data["wording"]["junk"])
    junk_order = list(range(junk_lines))
    rng.shuffle(junk_order)

    def junk() -> bool:
        # The unreadable stones first: a readable stone should carry information when there is any.
        unreadable = [stone for stone in free if not full.can_access(stones[stone])]
        stone = (unreadable or free)[0]
        free.remove(stone)
        line = junk_order[len([h for h in hints.values() if h.kind == "junk"]) % junk_lines]
        hints[stone] = Hint(stone, labels[stone], "junk", line=line)
        return True

    makers: dict[str, Callable[[], bool]] = {
        "woth": woth,
        "barren": barren,
        "item": lambda: location_hint("item", majors),
        "sometimes": lambda: location_hint("sometimes", sometimes),
        "random": lambda: location_hint("random", hintable),
        "junk": junk,
    }
    if plan.get("always", True):
        for name in always:
            if free and name not in hinted_locations:
                hinted_locations.add(name)
                place("always", name, area=area_of[name])
    weights = {kind: weight for kind, weight in plan["weights"].items() if weight > 0}
    while free and weights:
        kinds = list(weights)
        kind = rng.choices(kinds, weights=[weights[k] for k in kinds])[0]
        if not makers[kind]():
            del weights[kind]
    while free:
        junk()
    return tuple(hints[name] for name in stones)


def area_name(area: str | None) -> str:
    if area is None:
        return "somewhere"
    return load()["areas"].get(area, area)


def stone_place(stone: str) -> str:
    """Where ``stone`` stands, for a player."""
    return load()["stones"].get(stone, stone)


# With ``marked``, each filled-in name stands between these two characters, so a text patch can colour it.
FIELD_START, FIELD_END = "\x01", "\x02"


def text(
    hint: Hint,
    item_name: Callable[[str], str] = str,
    location_name: Callable[[str], str] = str,
    *,
    marked: bool = False,
) -> str:
    """The hint in Clawshot's wording; ``item_name`` and ``location_name`` turn the logic's names into the player's."""
    wording = load()["wording"]
    if hint.kind == "junk":
        return wording["junk"][hint.line or 0]
    fields = {
        "area": area_name(hint.area),
        "item": item_name(hint.item) if hint.item else "",
        "location": location_name(hint.location) if hint.location else "",
    }
    if marked:
        fields = {key: f"{FIELD_START}{value}{FIELD_END}" for key, value in fields.items()}
    template = wording["location"] if hint.kind in ("always", "sometimes", "random") else wording[hint.kind]
    return template.format(**fields)
