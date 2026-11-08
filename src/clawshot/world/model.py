"""The world as the search sees it: regions joined by exits, with locations (checks) and events in them."""

from dataclasses import dataclass, field
from typing import Any

from clawshot.world.rules import Rule

# OoT Randomizer item types whose items belong to one dungeon ("Small Key (Forest Temple)").
DUNGEON_ITEM_TYPES = frozenset({"SmallKey", "SmallKeyRing", "BossKey", "Map", "Compass", "SilverRupee"})


@dataclass(frozen=True)
class Item:
    """An item the logic knows. ``progression`` items can unlock something; ``priority`` and normal items cannot
    (OoT Randomizer's advancement True/False/None). ``dungeon`` is set for a dungeon's own keys, maps and
    compasses. ``alias`` adds a count of another item when collected (a Heart Container is four Pieces of Heart)."""

    name: str
    type: str = "Item"
    progression: bool = True
    priority: bool = False
    dungeon: str | None = None
    bottle: bool = False
    medallion: bool = False
    stone: bool = False
    alias: tuple[str, int] | None = None


@dataclass(frozen=True)
class Exit:
    parent: str
    target: str
    rule: Rule
    source: str


@dataclass(frozen=True)
class Location:
    """A check: one item, placed once. ``type`` is OoT Randomizer's location type (``Chest``, ``GS Token``, ...);
    ``vanilla`` the item the unrandomized game puts there (with fixed items, the tier this check gives). ``area``
    is the remake's Banc folder the check lies in (its region's, unless the remake moved it).
    ``n64_only`` is the reason, with its evidence, when the check does not exist in the remake; ``keep_vanilla`` the
    reason a check of a shuffled type keeps its vanilla item; ``override`` the source of the remake overrides
    applied to it (``remake.toml``)."""

    name: str
    region: str
    rule: Rule
    type: str
    vanilla: str | None
    source: str
    area: str | None = None
    n64_only: str | None = None
    keep_vanilla: str | None = None
    override: str | None = None


@dataclass(frozen=True)
class Event:
    """Something that, once done, stays done: held as an item named ``name`` when ``rule`` passes in ``region``."""

    name: str
    region: str
    rule: Rule
    source: str


@dataclass
class Region:
    name: str
    source: str = ""
    area: str | None = None
    """The remake's Banc folder the region lies in (the census ``area``)."""
    dungeon: str | None = None
    scene: str | None = None
    hint: str | None = None
    time_passes: bool = False
    provides_time: int = 0
    exits: list[Exit] = field(default_factory=list)
    locations: list[Location] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)


@dataclass
class World:
    regions: dict[str, Region]
    locations: dict[str, Location]
    events: list[Event]
    items: dict[str, Item]
    settings: dict[str, Any]
    start: str
    start_tod: int
    goal: Rule
    start_items: tuple[str, ...] = ()
    """Items held before any check (precollected items such as the ocarina buttons)."""
    dangling_exits: list[tuple[str, str]] = field(default_factory=list)
    """Exits whose target region is not in this world (a partial port): never taken."""
    undefined_events: list[str] = field(default_factory=list)
    """Events a rule names that no region defines: never held."""
    missing_regions: list[str] = field(default_factory=list)
    """Regions an ``at()`` names that are not in this world."""

    def item(self, name: str) -> Item:
        try:
            return self.items[name]
        except KeyError:
            raise KeyError(f"unknown item {name!r}") from None
