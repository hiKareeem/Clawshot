"""The fill: OoT Randomizer's assumed fill (``Fill.py``, ``distribute_items_restrictive``, MIT), for one world.

Order, as there: items restricted to some locations first (a dungeon's own keys, maps and compasses), then
progression items, then priority items, then the rest. A restricted or progression item goes to a location that is
reachable assuming the player holds every item not yet placed; that keeps every progression item reachable, so
the game stays beatable. Priority items only respect their restriction; the rest go anywhere.
"""

import base64
import binascii
import json
import random
import zlib
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from clawshot.settings import DEFAULTS
from clawshot.world.model import World
from clawshot.world.rules import ADULT, CHILD
from clawshot.world.search import Search

DUNGEON_ITEM_CHOICES = ("own_dungeon", "anywhere")


class FillError(RuntimeError):
    """No placement was found (an item with nowhere reachable to go, or a game that cannot be beaten)."""


@dataclass(frozen=True)
class Settings:
    """What a seed shuffles. ``shuffle`` lists OoT Randomizer location types whose items are shuffled among
    themselves; every other location keeps its vanilla item. ``dungeon_items`` keeps a dungeon's keys, maps and
    compasses in that dungeon (``own_dungeon``) or lets them go ``anywhere``. ``logic`` overrides logic settings
    from ``settings.toml``.

    ``areas`` and ``goal`` cut the world down to a slice (a playtest of a few areas): only the regions in those
    census areas (Banc folders) and the area-less start regions, with ``goal`` in place of the world's. Empty: the
    whole world.

    ``item_location_types`` holds a logic item to the location types it may go to (songs to song locations, an
    item whose actor is not known to work in a chest to the gift locations); a location type in
    ``exclusive_location_types`` takes only items held to it there (OoT Randomizer's ``shuffle_song_items =
    'song'``)."""

    shuffle: tuple[str, ...] = tuple(DEFAULTS["shuffle"])
    dungeon_items: str = DEFAULTS["dungeon_items"]
    logic: dict[str, Any] = field(default_factory=dict)
    areas: tuple[str, ...] = ()
    goal: str | None = None
    item_location_types: dict[str, tuple[str, ...]] = field(default_factory=dict)
    exclusive_location_types: tuple[str, ...] = ()
    fast_start: tuple[str, ...] = tuple(DEFAULTS["fast_start"])

    def __post_init__(self) -> None:
        for name in ("shuffle", "areas", "fast_start", "exclusive_location_types"):
            values = getattr(self, name)
            if not isinstance(values, (tuple, list)) or not all(isinstance(value, str) for value in values):
                raise ValueError(f"{name} must be a list of names")
            object.__setattr__(self, name, tuple(sorted(set(values))))
        if not isinstance(self.logic, dict) or not all(isinstance(key, str) for key in self.logic):
            raise ValueError("logic must be a table of setting names to JSON values")
        if self.goal is not None and not isinstance(self.goal, str):
            raise ValueError("goal must be a rule string")
        if not isinstance(self.item_location_types, dict):
            raise ValueError("item_location_types must be a table")
        held = {}
        for item, types in self.item_location_types.items():
            if not isinstance(item, str) or not isinstance(types, (tuple, list)):
                raise ValueError("item_location_types must map item names to lists of location types")
            if not all(isinstance(value, str) for value in types):
                raise ValueError("item_location_types must contain location type names")
            held[item] = tuple(sorted(set(types)))
        object.__setattr__(self, "item_location_types", held)
        try:
            json.dumps(self.logic, allow_nan=False)
        except (ValueError, TypeError) as error:
            raise ValueError("logic must contain finite JSON values") from error
        if self.dungeon_items not in DUNGEON_ITEM_CHOICES:
            raise ValueError(f"dungeon_items must be one of {DUNGEON_ITEM_CHOICES}, not {self.dungeon_items!r}")
        if self.goal is not None and not self.areas:
            raise ValueError("a goal is given only with the areas of a slice")

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "shuffle": list(self.shuffle),
            "dungeon_items": self.dungeon_items,
            "logic": {k: self.logic[k] for k in sorted(self.logic)},
            "fast_start": list(self.fast_start),
        }
        if self.areas:
            out["areas"] = list(self.areas)
            out["goal"] = self.goal
        if self.item_location_types:
            out["item_location_types"] = {
                k: list(self.item_location_types[k]) for k in sorted(self.item_location_types)
            }
        if self.exclusive_location_types:
            out["exclusive_location_types"] = list(self.exclusive_location_types)
        return out

    def to_string(self) -> str:
        """Canonical CS1 string: sorted JSON overrides, zlib, URL-safe base64 (no padding).

        CS1 alone selects this generator version's defaults. World data and generator version
        must also match to reproduce a seed, as with the JSON settings.
        """
        baseline = Settings().as_dict()
        delta = {name: value for name, value in self.as_dict().items() if value != baseline.get(name)}
        if not delta:
            return "CS1"
        payload = json.dumps(delta, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        return "CS1." + base64.urlsafe_b64encode(zlib.compress(payload.encode("utf-8"), 9)).decode("ascii").rstrip("=")

    @classmethod
    def from_string(cls, text: str) -> "Settings":
        """Decode a CS1 string; reject unknown versions, corrupt payloads and invalid fields."""
        if text == "CS1":
            return cls()
        if not text.startswith("CS1."):
            raise ValueError("unsupported settings string version (expected CS1)")
        try:
            payload = text[4:]
            compressed = base64.b64decode(payload + "=" * (-len(payload) % 4), altchars=b"-_", validate=True)
            data = json.loads(zlib.decompress(compressed))
            if not isinstance(data, dict):
                raise ValueError("settings payload must be a table")
            return cls(**data)
        except (binascii.Error, zlib.error, UnicodeError, ValueError, TypeError) as error:
            raise ValueError(f"invalid settings string: {error}") from error


def is_restricted(world: World, settings: Settings, item: str) -> bool:
    return settings.dungeon_items == "own_dungeon" and world.items[item].dungeon is not None


def allowed(world: World, settings: Settings, location: str, item: str) -> bool:
    """Whether ``item`` may go to ``location`` at all, reachable or not."""
    if world.locations[location].type == "Shop":
        if item not in world.settings.get("native_shop_items", ()):
            return False
        destinations = world.settings.get("shop_item_locations", {}).get(item)
        if destinations is not None and location not in destinations:
            return False
    location_type = world.locations[location].type
    types = settings.item_location_types.get(item)
    if types is not None and location_type not in types:
        return False
    if location_type in settings.exclusive_location_types and (types is None or location_type not in types):
        return False
    if not is_restricted(world, settings, item):
        return True
    return world.regions[world.locations[location].region].dungeon == world.items[item].dungeon


def shuffled_locations(world: World, settings: Settings) -> list[str]:
    """Locations of a shuffled type that hold an item in the remake (not N64-only) and are not held to their
    vanilla item (``keep_vanilla``, a reason, e.g. the Treasure Chest Game's room boxes: D17). The others keep
    their vanilla item."""
    return [
        name
        for name, loc in world.locations.items()
        if loc.type in settings.shuffle
        and loc.vanilla is not None
        and loc.n64_only is None
        and getattr(loc, "keep_vanilla", None) is None
    ]


def _fill_restrictive(
    world: World,
    settings: Settings,
    rng: random.Random,
    placements: dict[str, str],
    locations: list[str],
    items: list[str],
    assumed: list[str],
) -> None:
    """OoT Randomizer ``fill_restrictive``: take items from the end of ``items``; put each in a location that is
    reachable holding ``assumed``, the items still to place and whatever the placements so far give."""
    native = world.settings.get("native_shop_items", ()) if "Shop" in settings.shuffle else ()
    # Leave flexible native-display items until items that can only occupy chests.
    items.sort(key=lambda name: (not world.items[name].priority, name not in native))
    while items:
        item = items.pop()
        search = Search(world, [*assumed, *items])
        search.collect_spheres(placements)
        candidates = [name for name in locations if allowed(world, settings, name, item)]
        rng.shuffle(candidates)
        if item in native:
            candidates.sort(key=lambda name: world.locations[name].type != "Shop")
        spot = next((name for name in candidates if search.can_access(world.locations[name])), None)
        if spot is None:
            raise FillError(
                f"no reachable location for {item!r} ({len(candidates)} allowed of {len(locations)} left; "
                f"{len(items)} other items left to place)"
            )
        placements[spot] = item
        locations.remove(spot)


def _fill_restrictive_fast(
    world: World,
    settings: Settings,
    rng: random.Random,
    placements: dict[str, str],
    locations: list[str],
    items: list[str],
) -> None:
    """OoT Randomizer ``fill_restrictive_fast``: placement checks only the item's restriction."""
    while items and locations:
        item = items[-1]
        rng.shuffle(locations)
        if item in world.settings.get("native_shop_items", ()):
            locations.sort(key=lambda name: world.locations[name].type != "Shop")
        spot = next((name for name in locations if allowed(world, settings, name, item)), None)
        if spot is None:
            return
        items.pop()
        placements[spot] = item
        locations.remove(spot)


def _fast_fill(rng: random.Random, placements: dict[str, str], locations: list[str], items: list[str]) -> None:
    """OoT Randomizer ``fast_fill``: the rest, anywhere."""
    rng.shuffle(locations)
    while items and locations:
        placements[locations.pop()] = items.pop()


def _age_family(world: World, item: str) -> str:
    alias = world.items[item].alias
    return alias[0] if alias is not None else item


def _fill_age_return(
    world: World,
    settings: Settings,
    rng: random.Random,
    placements: dict[str, str],
    locations: list[str],
    pool: list[str],
) -> None:
    """Forward-place the data-defined return kit in an adult phase, before the usual assumed fill.

    Bypass families additionally need an adult-only destination: otherwise an optional early child pickup
    could bypass an unshuffled child prerequisite (the remake's Saria/bracelet route).
    """
    families = world.settings.get("age_return_fill_families", ())
    if world.age_return is None or not world.settings.get("age_return_guarantee", False) or not families:
        return
    bypass = world.settings.get("age_return_bypass_families", ())
    staged = [item for item in pool if _age_family(world, item) in families]
    if not staged:
        return
    for item in staged:
        pool.remove(item)
    # Small keys must bootstrap the entrance before a boss key can consume its only reachable chest.
    order = {"SmallKey": 0, "SmallKeyRing": 0, "BossKey": 2, "GanonBossKey": 2}
    staged.sort(key=lambda name: order.get(world.items[name].type, 1))
    maximal = Search(world, [*pool, *staged, *placements.values()])
    child_access = {name for name in locations if maximal.can_access(world.locations[name], CHILD)}
    inventory = world.settings.get("age_return_fill_inventory", {})
    search = Search.adult_after_pull(world, (name for name, count in inventory.items() for _ in range(count)))
    while staged:
        search.collect_spheres(placements)
        for index, item in enumerate(staged):
            candidates = [
                name
                for name in locations
                if allowed(world, settings, name, item)
                and (_age_family(world, item) not in bypass or name not in child_access)
                and search.can_access(world.locations[name], ADULT)
            ]
            if candidates:
                rng.shuffle(candidates)
                location = candidates[0]
                placements[location] = item
                locations.remove(location)
                staged.pop(index)
                break
        else:
            raise FillError(f"no adult return-kit destination for {staged!r}")


def fill(
    world: World, settings: Settings, rng: random.Random, vanilla: Mapping[str, str] | None = None
) -> dict[str, str]:
    """Place the vanilla items of the shuffled locations. Returns every placement: the shuffled locations and the
    locations that keep their vanilla item, in world order.

    ``vanilla`` replaces the world's vanilla item (OoT Randomizer's) of the locations it names with the remake's
    own, so the pool is what the remake hands out."""
    vanilla = vanilla or {}

    def vanilla_item(name: str) -> str | None:
        return vanilla.get(name, world.locations[name].vanilla)

    shuffled = shuffled_locations(world, settings)
    shuffled_set = set(shuffled)
    placements = {
        name: vanilla_item(name)
        for name, loc in world.locations.items()
        if name not in shuffled_set and vanilla_item(name) is not None and loc.n64_only is None
    }
    pool = [vanilla_item(name) for name in shuffled]
    rng.shuffle(pool)
    locations = list(shuffled)
    _fill_age_return(world, settings, rng, placements, locations, pool)
    restricted = [item for item in pool if is_restricted(world, settings, item)]
    unrestricted = [item for item in pool if not is_restricted(world, settings, item)]
    progression = [item for item in unrestricted if world.items[item].progression]
    # A non-progression item held to some location types goes with the priority items, which are placed only where
    # allowed() lets them; the rest go anywhere.
    held = settings.item_location_types
    priority = [i for i in unrestricted if not world.items[i].progression and (world.items[i].priority or i in held)]
    rest = [item for item in unrestricted if not world.items[item].progression and item not in priority]

    if restricted:
        # Boss keys are taken first, then small keys, then the rest (Fill.fill_dungeons_restrictive).
        order = {"BossKey": 3, "GanonBossKey": 3, "SmallKey": 2, "SmallKeyRing": 2}
        restricted.sort(key=lambda name: order.get(world.items[name].type, 1))
        _fill_restrictive(world, settings, rng, placements, locations, restricted, unrestricted)
    _fill_restrictive(world, settings, rng, placements, locations, progression, [])
    if any(world.locations[name].type == "Shop" for name in shuffled):
        native = world.settings.get("native_shop_items", ())
        priority = [*priority, *rest]
        rest = []
        priority.sort(key=lambda item: item not in native)
        _fill_restrictive_fast(world, settings, rng, placements, locations, priority)
    else:
        _fill_restrictive_fast(world, settings, rng, placements, locations, priority)
        _fast_fill(rng, placements, locations, rest)

    if priority or rest:
        raise FillError(f"items left unplaced: {sorted(priority + rest)}")
    if locations:
        raise FillError(f"locations left empty: {sorted(locations)}")
    return {name: placements[name] for name in world.locations if name in placements}


def check_beatable(world: World, placements: dict[str, str]) -> list[list[str]]:
    """The beatability search: collect everything reachable from the start; the goal must be met. Returns the
    spheres (location names) on success."""
    search = Search(world)
    spheres = search.collect_spheres(placements)
    if not search.won():
        unreached = [name for name in placements if name not in search.collected]
        raise FillError(f"the goal cannot be reached; {len(unreached)} placed items never reachable: {unreached[:10]}")
    return spheres
