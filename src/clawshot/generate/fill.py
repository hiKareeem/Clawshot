"""The fill: OoT Randomizer's assumed fill (``Fill.py``, ``distribute_items_restrictive``, MIT), for one world.

Order, as there: own-dungeon items, type-held items (songs and shop refills), bag-gated bomb ammo, then
remaining progression and filler. Each constrained/progression stage assumes every item not yet placed.
This preserves restricted capacity and keeps progression reachable. Priority filler respects its restriction;
the rest can go anywhere, including unreachable junk locations in otherwise-beatable slices.
"""

import base64
import binascii
import json
import random
import zlib
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any

from clawshot.generate import hints as hint_choices
from clawshot.settings import CATALOG, DEFAULTS
from clawshot.world.model import World
from clawshot.world.rules import ADULT, CHILD
from clawshot.world.search import Search

DUNGEON_ITEM_CHOICES = ("own_dungeon", "anywhere")
_BOMB_AMMO_PREFIXES = ("Bombs (", "Bombchus (")
STAGE_ATTEMPTS = 15
"""Tries of a stage placed on its own before the fill fails (``Fill.fill_ownworld_restrictive``'s ``attempts``)."""


class FillError(RuntimeError):
    """No placement was found (an item with nowhere reachable to go, or a game that cannot be beaten).

    A failed assumed-fill stage says which: ``stage``, the ``item`` it could not place, the ``allowed`` locations
    still empty (none reachable) and the ``frontier``: the empty locations reachable with the assumed items, which
    the item may not take."""

    def __init__(
        self,
        message: str,
        *,
        stage: str | None = None,
        item: str | None = None,
        allowed: tuple[str, ...] = (),
        frontier: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.item = item
        self.allowed = allowed
        self.frontier = frontier


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
    'song'``).

    ``hints``: ``always`` (Gossip Stones speak without the Mask of Truth, the flow patched) or ``mask`` (vanilla:
    child Link wearing it); ``hint_distribution`` names a distribution of ``data/hints.toml``."""

    shuffle: tuple[str, ...] = tuple(DEFAULTS["shuffle"])
    dungeon_items: str = DEFAULTS["dungeon_items"]
    logic: dict[str, Any] = field(default_factory=dict)
    areas: tuple[str, ...] = ()
    goal: str | None = None
    item_location_types: dict[str, tuple[str, ...]] = field(default_factory=dict)
    exclusive_location_types: tuple[str, ...] = ()
    fast_start: tuple[str, ...] = tuple(DEFAULTS["fast_start"])
    songs: str = DEFAULTS["songs"]
    shop_prices: str = DEFAULTS["shop_prices"]
    shop_slots: int = DEFAULTS["shop_slots"]
    scrub_prices: str = DEFAULTS["scrub_prices"]
    scrub_price: int = DEFAULTS["scrub_price"]
    cheap_deku_shield: bool = DEFAULTS["cheap_deku_shield"]
    forest: str = DEFAULTS["forest"]
    hints: str = DEFAULTS["hints"]
    hint_distribution: str = DEFAULTS["hint_distribution"]

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
        if self.songs not in ("song", "anywhere"):
            raise ValueError("songs must be 'song' or 'anywhere'")
        if self.shop_prices not in ("vanilla", "affordable"):
            raise ValueError("shop_prices must be 'vanilla' or 'affordable'")
        if type(self.shop_slots) is not int or not 0 <= self.shop_slots <= 8:
            raise ValueError("shop_slots must be an integer from 0 to 8")
        if self.scrub_prices not in ("vanilla", "fixed"):
            raise ValueError("scrub_prices must be 'vanilla' or 'fixed'")
        if type(self.scrub_price) is not int or not 0 <= self.scrub_price <= 1000:
            raise ValueError("scrub_price must be an integer from 0 to 1000 rupees")
        if not isinstance(self.cheap_deku_shield, bool):
            raise ValueError("cheap_deku_shield must be a boolean")
        if not isinstance(self.forest, str) or self.forest not in CATALOG["forest"]:
            raise ValueError("forest must be 'closed', 'closed_deku' or 'open'")
        if self.hints not in hint_choices.MODES:
            raise ValueError(f"hints must be one of {hint_choices.MODES}")
        if self.hint_distribution not in hint_choices.distributions():
            raise ValueError(f"hint_distribution must be one of {hint_choices.distributions()}")
        legacy = set(self.fast_start) & {"mido", "forest_exit"}
        if legacy:
            mode = "open" if "mido" in legacy else "closed_deku"
            if self.forest not in ("closed", mode):
                raise ValueError("legacy forest skips conflict with the forest setting")
            object.__setattr__(self, "forest", mode)
            object.__setattr__(self, "fast_start", tuple(name for name in self.fast_start if name not in legacy))

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "shuffle": list(self.shuffle),
            "dungeon_items": self.dungeon_items,
            "logic": {k: self.logic[k] for k in sorted(self.logic)},
            "fast_start": list(self.fast_start),
            "songs": self.songs,
            "shop_prices": self.shop_prices,
            "shop_slots": self.shop_slots,
            "scrub_prices": self.scrub_prices,
            "scrub_price": self.scrub_price,
            "cheap_deku_shield": self.cheap_deku_shield,
            "forest": self.forest,
            "hints": self.hints,
            "hint_distribution": self.hint_distribution,
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
    if location_type == "Missable" and world.items[item].progression:
        return False
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
    shop_refills: int = 0,
    stage: str = "progression",
) -> int:
    """OoT Randomizer ``fill_restrictive``: take items from the end of ``items``; put each in a location that is
    reachable holding ``assumed``, the items still to place and whatever the placements so far give."""
    native = world.settings.get("native_shop_items", ()) if "Shop" in settings.shuffle else ()
    # Reserve only the slots needed by remaining refills, not every shop slot.
    # Leave flexible native-display items until items that can only occupy chests.
    items.sort(key=lambda name: (not world.items[name].priority, name not in native))
    while items:
        item = items.pop()
        search = Search(world, [*assumed, *items])
        search.collect_spheres(placements)
        candidates = [name for name in locations if allowed(world, settings, name, item)]
        rng.shuffle(candidates)
        if item in native:
            reserve = (
                shop_refills > 0 and sum(world.locations[name].type == "Shop" for name in locations) <= shop_refills
            )
            preferred = "Chest" if reserve and settings.item_location_types.get(item) != ("Shop",) else "Shop"
            candidates.sort(key=lambda name: world.locations[name].type != preferred)
        spot = next((name for name in candidates if search.can_access(world.locations[name])), None)
        if spot is None:
            frontier = tuple(sorted(name for name in locations if search.can_access(world.locations[name])))
            raise FillError(
                f"{stage}: no reachable location for {item!r} ({len(candidates)} allowed of {len(locations)} left; "
                f"{len(items)} other items left to place; {len(frontier)} empty locations reachable)",
                stage=stage,
                item=item,
                allowed=tuple(sorted(candidates)),
                frontier=frontier,
            )
        placements[spot] = item
        locations.remove(spot)
        if item.startswith("Buy ") and settings.item_location_types.get(item) == ("Shop",):
            shop_refills -= 1
    return shop_refills


def _fill_restrictive_fast(
    world: World,
    settings: Settings,
    rng: random.Random,
    placements: dict[str, str],
    locations: list[str],
    items: list[str],
    shop_refills: int = 0,
) -> int:
    """OoT Randomizer ``fill_restrictive_fast``: placement checks only the item's restriction."""
    # Flexible native displays can still fill slots not needed by refills.
    while items and locations:
        item = items[-1]
        rng.shuffle(locations)
        if item in world.settings.get("native_shop_items", ()):
            reserve = (
                shop_refills > 0 and sum(world.locations[name].type == "Shop" for name in locations) <= shop_refills
            )
            preferred = "Chest" if reserve and settings.item_location_types.get(item) != ("Shop",) else "Shop"
            locations.sort(key=lambda name: world.locations[name].type != preferred)
        spot = next((name for name in locations if allowed(world, settings, name, item)), None)
        if spot is None:
            return shop_refills
        items.pop()
        placements[spot] = item
        locations.remove(spot)
        if item.startswith("Buy ") and settings.item_location_types.get(item) == ("Shop",):
            shop_refills -= 1
    return shop_refills


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
            raise FillError(f"return kit: no adult return-kit destination for {staged!r}", stage="return kit")


def _before_ammo(items: list[str]) -> list[str]:
    """What a stage before :func:`_fill_bomb_ammo` may assume: not the bomb and Bombchu packs. D25 puts every pack
    where only a Bomb Bag reaches, so a placement that needed a pack to be reached could leave the last pack nowhere
    (seed 7 Gift: Zelda's Letter behind Bombchus, every Bombchu pack behind a bag that needed the letter)."""
    return [item for item in items if not item.startswith(_BOMB_AMMO_PREFIXES)]


def _fill_bomb_ammo(
    world: World,
    settings: Settings,
    rng: random.Random,
    placements: dict[str, str],
    locations: list[str],
    pool: list[str],
) -> None:
    """D25: native bomb/Bombchu packs cannot become an unmodelled first Bomb Bag.

    The audited item and Shop bundle actors share SmallBagActor = Item_BombBag_Small
    (plans/03-game-data.md section 24). Buy refills remain in shops; never count any pack
    or logical bag alias in the counterfactual inventory.
    """
    ammo = [item for item in pool if item.startswith(_BOMB_AMMO_PREFIXES)]
    if not ammo:
        return
    sources = {
        name
        for name in world.items
        if _age_family(world, name) == "Bomb Bag"
        or name.startswith((*_BOMB_AMMO_PREFIXES, "Buy Bombs (", "Buy Bombchu ("))
    }
    without_bag = Search(
        replace(world, start_items=tuple(item for item in world.start_items if item not in sources)),
        (item for item in [*pool, *placements.values()] if item not in sources),
    )
    destinations = [name for name in locations if not without_bag.can_access(world.locations[name])]
    pool[:] = [item for item in pool if not item.startswith(_BOMB_AMMO_PREFIXES)]
    # Dungeon items already own their slots; place constrained ammo before unrestricted filler.
    # Assumed fill still requires actual reachability and respects dungeon/display restrictions.
    held = settings.item_location_types
    shop_refills = sum(item.startswith("Buy ") and held.get(item) == ("Shop",) for item in pool)
    _fill_restrictive(world, settings, rng, placements, destinations, ammo, pool, shop_refills, "bomb ammo")
    locations[:] = [name for name in locations if name not in placements]


def _fill_dungeon_items(
    world: World,
    settings: Settings,
    rng: random.Random,
    placements: dict[str, str],
    locations: list[str],
    pool: list[str],
    shop_refills: int,
    dungeons: Callable[[str], bool] = lambda dungeon: True,
) -> int:
    """Own-dungeon items (``Fill.fill_dungeons_restrictive``) of the ``dungeons`` chosen, taken out of ``pool``, which
    stays assumed.

    Small keys go first, then boss keys, then maps and compasses. OoT Randomizer takes boss keys first, but the
    remake's Fire Temple has exactly one key-free chest and two more behind the first lock, all three needed by small
    keys; no chest there needs its boss key. A boss key placed first took one of them in 40% of chest-only fills."""
    items = [item for item in pool if is_restricted(world, settings, item) and dungeons(world.items[item].dungeon)]
    if not items:
        return shop_refills
    for item in items:
        pool.remove(item)
    order = {"SmallKey": 3, "SmallKeyRing": 3, "BossKey": 2, "GanonBossKey": 2}
    items.sort(key=lambda name: order.get(world.items[name].type, 1))  # taken from the end
    return _fill_restrictive(
        world, settings, rng, placements, locations, items, _before_ammo(pool), shop_refills, "dungeon"
    )


def _fill_type_held(
    world: World,
    settings: Settings,
    rng: random.Random,
    placements: dict[str, str],
    locations: list[str],
    items: list[str],
    assumed: list[str],
    shop_refills: int,
) -> int:
    """Items held to some location types (songs, shop refills, gift items), on their own.

    OoT Randomizer places shop items and songs this way (``Fill.fill_ownworld_restrictive``, 526b4c8d): a failed
    stage is undone and tried again, up to ``STAGE_ATTEMPTS`` times, before the whole fill fails ("songs have a
    relatively high chance of failing compared to other item types"). The remake's twelve song checks take exactly
    the twelve songs: in 200 Gift seeds a song with no reachable song check ended 451 of the 1,001 failed attempts."""
    attempt = 0
    while True:
        attempt += 1
        rng.shuffle(items)
        # Sparse native shop whitelists must keep their slots before general refills take them.
        stage_items = sorted(
            items, key=lambda item: sum(allowed(world, settings, name, item) for name in locations), reverse=True
        )
        stage_locations, before = list(locations), set(placements)
        try:
            refills = _fill_restrictive(
                world, settings, rng, placements, stage_locations, stage_items, assumed, shop_refills, "type-held"
            )
        except FillError:
            for name in [name for name in placements if name not in before]:
                del placements[name]
            if attempt == STAGE_ATTEMPTS:
                raise
            continue
        locations[:] = stage_locations
        return refills


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
    held = settings.item_location_types
    shop_refills = sum(item.startswith("Buy ") and held.get(item) == ("Shop",) for item in pool)
    # The return kit's forward placement takes any adult chest, so the own-dungeon items of every dungeon it does not
    # draw from go first: the remake's Fire Temple has no spare chest for its keys (plans/rounds/r8-fill.md).
    families = world.settings.get("age_return_fill_families", ())
    kit_dungeons = {world.items[item].dungeon for item in pool if _age_family(world, item) in families}
    shop_refills = _fill_dungeon_items(
        world, settings, rng, placements, locations, pool, shop_refills, lambda dungeon: dungeon not in kit_dungeons
    )
    _fill_age_return(world, settings, rng, placements, locations, pool)
    shop_refills = _fill_dungeon_items(world, settings, rng, placements, locations, pool, shop_refills)
    unrestricted = pool
    # Type-held ammo still needs the stronger D25 bag gate in its dedicated stage.
    type_held = [item for item in unrestricted if item in held and not item.startswith(_BOMB_AMMO_PREFIXES)]
    unrestricted = [item for item in unrestricted if item not in held or item.startswith(_BOMB_AMMO_PREFIXES)]
    shop_refills = _fill_type_held(
        world, settings, rng, placements, locations, type_held, _before_ammo(unrestricted), shop_refills
    )
    _fill_bomb_ammo(world, settings, rng, placements, locations, unrestricted)
    progression = [item for item in unrestricted if world.items[item].progression]
    priority = [item for item in unrestricted if not world.items[item].progression and world.items[item].priority]
    rest = [item for item in unrestricted if not world.items[item].progression and item not in priority]
    shop_refills = _fill_restrictive(
        world, settings, rng, placements, locations, progression, [*priority, *rest], shop_refills, "progression"
    )
    if any(world.locations[name].type == "Shop" for name in shuffled):
        native = world.settings.get("native_shop_items", ())
        priority = [*priority, *rest]
        rest = []
        # Leave flexible native displays until filler that can only occupy chests.
        priority.sort(key=lambda item: item not in native)
        _fill_restrictive_fast(world, settings, rng, placements, locations, priority, shop_refills)
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
