"""The fill: OoT Randomizer's assumed fill (``Fill.py``, ``distribute_items_restrictive``, MIT), for one world.

Order, as there: items restricted to some locations first (a dungeon's own keys, maps and compasses), then
progression items, then priority items, then the rest. A restricted or progression item goes to a location that is
reachable assuming the player holds every item not yet placed; that keeps every progression item reachable, so
the game stays beatable. Priority items only respect their restriction; the rest go anywhere.
"""

import random
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from clawshot.world.model import World
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
    whole world."""

    shuffle: tuple[str, ...] = ("Chest",)
    dungeon_items: str = "own_dungeon"
    logic: dict[str, Any] = field(default_factory=dict)
    areas: tuple[str, ...] = ()
    goal: str | None = None

    def __post_init__(self) -> None:
        if self.dungeon_items not in DUNGEON_ITEM_CHOICES:
            raise ValueError(f"dungeon_items must be one of {DUNGEON_ITEM_CHOICES}, not {self.dungeon_items!r}")
        if self.goal is not None and not self.areas:
            raise ValueError("a goal is given only with the areas of a slice")

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "shuffle": list(self.shuffle),
            "dungeon_items": self.dungeon_items,
            "logic": {k: self.logic[k] for k in sorted(self.logic)},
        }
        if self.areas:
            out["areas"] = list(self.areas)
            out["goal"] = self.goal
        return out


def is_restricted(world: World, settings: Settings, item: str) -> bool:
    return settings.dungeon_items == "own_dungeon" and world.items[item].dungeon is not None


def allowed(world: World, settings: Settings, location: str, item: str) -> bool:
    """Whether ``item`` may go to ``location`` at all, reachable or not."""
    if world.locations[location].type == "Shop" and item not in world.settings.get("native_shop_items", ()):
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
    items.sort(key=lambda name: not world.items[name].priority)  # stable: priority items last to be taken
    while items:
        item = items.pop()
        search = Search(world, [*assumed, *items])
        search.collect_spheres(placements)
        candidates = [name for name in locations if allowed(world, settings, name, item)]
        rng.shuffle(candidates)
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
    restricted = [item for item in pool if is_restricted(world, settings, item)]
    unrestricted = [item for item in pool if not is_restricted(world, settings, item)]
    progression = [item for item in unrestricted if world.items[item].progression]
    priority = [item for item in unrestricted if world.items[item].priority]
    rest = [item for item in unrestricted if not world.items[item].progression and not world.items[item].priority]
    locations = list(shuffled)

    if restricted:
        # Boss keys are taken first, then small keys, then the rest (Fill.fill_dungeons_restrictive).
        order = {"BossKey": 3, "GanonBossKey": 3, "SmallKey": 2, "SmallKeyRing": 2}
        restricted.sort(key=lambda name: order.get(world.items[name].type, 1))
        _fill_restrictive(world, settings, rng, placements, locations, restricted, unrestricted)
    _fill_restrictive(world, settings, rng, placements, locations, progression, [])
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
