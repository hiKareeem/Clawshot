"""The world as the search sees it: regions joined by exits, with locations (checks) and events in them."""

from dataclasses import dataclass, field
from typing import Any

from clawshot.world.rules import Rule

# OoT Randomizer item types whose items belong to one dungeon ("Small Key (Forest Temple)").
DUNGEON_ITEM_TYPES = frozenset({"SmallKey", "SmallKeyRing", "BossKey", "GanonBossKey", "Map", "Compass", "SilverRupee"})
# The location type of a Gossip Stone: a place to read a hint, not a check (``World.hint_stones``).
HINT_STONE = "HintStone"


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
    applied to it (``remake.toml``). ``excluded_items`` forbids unsafe delivery combinations during fill."""

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
    excluded_items: tuple[str, ...] = ()


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
    hint_stones: dict[str, Location] = field(default_factory=dict)
    """Gossip Stones (OoT Randomizer type ``HintStone``): where a hint can be read, with the rule to reach it. Not
    checks: they hold no item, so they are kept out of ``locations`` and the fill never sees them."""

    @property
    def age_return(self) -> tuple[str, str] | None:
        """The data-defined (completion event, adult return region), or unrestricted two-age travel.

        Partial worlds may omit either named event/region from their graph: return then stays closed.
        Neither a shuffled reward item nor an assumed starting age substitutes for the completion event.
        """
        if self.settings.get("free_time_travel", False):
            return None
        event = self.settings.get("age_return_event")
        region = self.settings.get("age_return_region")
        if event is None and region is None:
            return None
        if not isinstance(event, str) or not event or not isinstance(region, str) or not region:
            raise ValueError("age_return_event and age_return_region must both be nonempty strings")
        return event, region

    @property
    def age_pull_event(self) -> str:
        """The data-defined first-pull event for the early-return proof."""
        event = self.settings.get("age_pull_event")
        if not isinstance(event, str) or not event:
            raise ValueError("age-return guarantee needs age_pull_event in world settings")
        return event

    def item(self, name: str) -> Item:
        try:
            return self.items[name]
        except KeyError:
            raise KeyError(f"unknown item {name!r}") from None
