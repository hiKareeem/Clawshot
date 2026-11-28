"""The fill: OoT Randomizer's assumed fill (``Fill.py``, ``distribute_items_restrictive``, MIT), for one world.

Stages: own-dungeon items of the dungeons the return kit does not draw from, the return kit, the kit's own
dungeons' items, native pick-up palettes except Skulltulas, type-held items (songs, shop refills, gift items,
progressive copies; retried on their own), bag-gated bomb ammo, shared progression, capacity-matched Skulltula
filler, then other filler. Skulltula-compatible progression and spilled tokens stay in the shared assumed fill,
where swaps can repair their dependencies. A stage assumes only later reachable items, never junk.
``plans/04-world-format.md`` has the reasons.
"""

import base64
import binascii
import json
import random
import zlib
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any

from clawshot import starting
from clawshot.generate import hints as hint_choices
from clawshot.settings import CATALOG, DEFAULTS
from clawshot.world.model import World
from clawshot.world.rules import ADULT, CHILD
from clawshot.world.search import Search

SMALL_KEY = "SmallKey"
"""The item type ``anywhere`` lets out of its dungeon, into chests only."""
HIDEOUT_SMALL_KEY = "HideoutSmallKey"
"""The Gerudo Fortress jail keys' item type. No logic dungeon holds them: a chest grants one with named Fortress
credit (``clawshot.patch.key_targets``), a jail source with its native key."""
FLOOR_KEY_SOURCE = "KeyPickup"
"""Released floor-key sources' location type, currently only the Well, when small keys leave their dungeon into
shuffled chests (``clawshot.generate.key_families``). Chosen by settings, never a ``shuffle`` kind."""
HIDEOUT_KEY_SOURCE = "HideoutKeyPickup"
"""The four Fortress jail-key sources' location type with ``shuffle_hideout_keys``. Never a ``shuffle`` kind."""
HIDEOUT_KEY_DESTINATIONS = ("Chest", HIDEOUT_KEY_SOURCE)
"""Where a Fortress key may go: a chest (named Fortress grant) or a jail source (its native key)."""
SWORD_PEDESTAL_SOURCE = "SwordPedestal"
"""The first-pull source when ``shuffle_master_sword`` is enabled; never a user shuffle kind."""
CHEST_HELD_DUNGEON_TYPES = frozenset({SMALL_KEY, "BossKey", "GanonBossKey", "Map", "Compass"})
"""Dungeon item types held to chests in every mode, inside their own dungeon too (Kareem, 2026-11-23, on cs21j's
``plans/rounds/r21-placement-audit.md`` section 6). Another kind grants the generic item with no
``DungeonInfo.<target>`` write, unplayed: with Gift and ``songs = "anywhere"`` the Ice Cavern map and compass could go
to Sheik's lesson; with Freestanding or Scrub shuffled and no palette, to the Well's floor rupees or the dungeon
scrubs. Silver rupees and key rings keep their own-dungeon rule: they have no chest grant."""
CHEST_HELD_DESTINATIONS = ("Chest", FLOOR_KEY_SOURCE)
"""Where those types may go: a chest, or a released floor-key source, whose palette admits only its own native key
(``clawshot.generate.key_families``)."""
RELEASED_DUNGEON_ITEM_TYPES: dict[str, frozenset[str]] = {
    "own_dungeon": frozenset(),
    "anywhere": frozenset({SMALL_KEY}),
    "all_anywhere": frozenset({SMALL_KEY, "BossKey", "GanonBossKey", "Map", "Compass"}),
}
"""The dungeon item types each ``dungeon_items`` mode lets out of their dungeon, into chests only: a chest's
source-bound grant credits their dungeon from elsewhere (``clawshot.patch.key_targets``). ``all_anywhere`` is
experimental (built, not played). Key rings and silver rupees never leave."""
DUNGEON_ITEM_CHOICES = tuple(RELEASED_DUNGEON_ITEM_TYPES)
SHOP_ONLY_PREFIX = "Buy "
"""Bought goods (``Buy ...``: refills, ammo, Bombchus, bottle contents, hearts, magic jars) go only to shop shelves, in
every seed, whatever the settings hold (Claude, 2026-11-14, Round 15 family table: no adapter this round). A shelf
keeps its native display and restock; a purchase's grant (``NotPushToPouch`` bottle contents fill an owned bottle,
never give a new one) has no proven equivalent at a chest, gift, scrub, floor pickup or Skulltula."""
_BOMB_AMMO_PREFIXES = ("Bombs (", "Bombchus (")
# Prefixes, independent container providers, shop refills, and farmable supply events.
# Refills never become containers in the counterfactual (D25; Claude, 2026-11-14).
_AMMO_CONTAINERS = {
    "bomb": (_BOMB_AMMO_PREFIXES, ("Bomb Bag",), ("Buy Bombs (", "Buy Bombchu ("), ()),
    "arrow": (("Arrows (",), ("Bow", "Quiver (40)", "Quiver (50)"), ("Buy Arrows (",), ()),
    "seed": (
        ("Deku Seeds (",),
        ("Slingshot", "Bullet Bag (40)", "Bullet Bag (50)"),
        ("Buy Deku Seeds (",),
        (),
    ),
    "nut": (("Deku Nuts (",), ("Deku Nut Capacity",), ("Buy Deku Nut (",), ("Deku Nut Drop",)),
    "stick": (("Deku Stick (",), ("Deku Stick Capacity",), ("Buy Deku Stick (",), ("Deku Stick Drop",)),
}
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
    themselves, or ``Token`` for the Gold Skulltulas (``clawshot.generate.tokens``, never the raw ``GS Token``);
    every other location keeps its vanilla item. ``dungeon_items`` keeps a dungeon's keys, maps and
    compasses in that dungeon (``own_dungeon``), also lets its small keys out, into any chest (``anywhere``; boss
    keys, maps and compasses still stay), or lets all of them out, Ganon's Castle's boss key included, into any
    chest (``all_anywhere``, experimental). Both release modes need ``Chest`` shuffled (Round 18: before, ``anywhere``
    without it was accepted and moved nothing) and also shuffle the Well floor key's source; Shadow stays native.
    ``shuffle_hideout_keys`` (needs ``Chest``) shuffles the four Fortress jail keys' sources
    (``clawshot.generate.key_families``). ``shuffle_100_token_reward`` (default off, needs ``Gift``, or its expanded
    ``NPC``) lifts the first 100-token House reward's non-progression-only rule (issue #12); the reward stays junk
    otherwise. ``logic`` overrides logic settings from ``settings.toml``.

    ``areas`` and ``goal`` cut the world down to a slice (a playtest of a few areas): only the regions in those
    census areas (Banc folders) and the area-less start regions, with ``goal`` in place of the world's. Empty: the
    whole world.

    ``item_location_types`` holds a logic item to the location types it may go to (songs to song locations, an
    item whose actor is not known to work in a chest to the gift locations); a location type in
    ``exclusive_location_types`` takes only items held to it there (OoT Randomizer's ``shuffle_song_items =
    'song'``). ``location_type_items`` holds a location type to the only items it may take (D27: a boss heart or
    freestanding pick-up shows only a native floor pick-up).

    ``hints``: ``always`` (Gossip Stones speak without the Mask of Truth, the flow patched) or ``mask`` (vanilla:
    child Link wearing it); ``hint_distribution`` names a distribution of ``data/hints.toml``."""

    shuffle: tuple[str, ...] = tuple(DEFAULTS["shuffle"])
    dungeon_items: str = DEFAULTS["dungeon_items"]
    shuffle_hideout_keys: bool = DEFAULTS["shuffle_hideout_keys"]
    shuffle_100_token_reward: bool = DEFAULTS["shuffle_100_token_reward"]
    dungeon_rewards: bool = DEFAULTS["dungeon_rewards"]
    shuffle_master_sword: bool = DEFAULTS["shuffle_master_sword"]
    excluded_locations: tuple[str, ...] = tuple(DEFAULTS["excluded_locations"])
    bridge: str = DEFAULTS["bridge"]
    bridge_count: int = DEFAULTS["bridge_count"]
    trials_count: int = DEFAULTS["trials_count"]
    logic: dict[str, Any] = field(default_factory=dict)
    areas: tuple[str, ...] = ()
    goal: str | None = None
    item_location_types: dict[str, tuple[str, ...]] = field(default_factory=dict)
    exclusive_location_types: tuple[str, ...] = ()
    location_type_items: dict[str, tuple[str, ...]] = field(default_factory=dict)
    fast_start: tuple[str, ...] = tuple(DEFAULTS["fast_start"])
    # Reserved for reading old off-valued settings; the enabled feature is withdrawn.
    skippable_story: bool = DEFAULTS["skippable_story"]
    skip_saria_farewell: bool = DEFAULTS["skip_saria_farewell"]
    event_item_models: bool = DEFAULTS["event_item_models"]
    songs: str = DEFAULTS["songs"]
    shop_prices: str = DEFAULTS["shop_prices"]
    shop_slots: int = DEFAULTS["shop_slots"]
    scrub_prices: str = DEFAULTS["scrub_prices"]
    scrub_price: int = DEFAULTS["scrub_price"]
    cheap_deku_shield: bool = DEFAULTS["cheap_deku_shield"]
    forest: str = DEFAULTS["forest"]
    door_of_time: str = DEFAULTS["door_of_time"]
    hints: str = DEFAULTS["hints"]
    hint_distribution: str = DEFAULTS["hint_distribution"]
    starting_items: tuple[str, ...] = tuple(DEFAULTS["starting_items"])
    starting_hearts: int = DEFAULTS["starting_hearts"]
    starting_full_wallet: bool = DEFAULTS["starting_full_wallet"]

    def __post_init__(self) -> None:
        for name in (
            "shuffle",
            "areas",
            "fast_start",
            "exclusive_location_types",
            "excluded_locations",
            "starting_items",
        ):
            values = getattr(self, name)
            if not isinstance(values, (tuple, list)) or not all(isinstance(value, str) for value in values):
                raise ValueError(f"{name} must be a list of names")
            object.__setattr__(self, name, tuple(sorted(set(values))))
        starting.validate(self.starting_items, self.starting_hearts, self.starting_full_wallet)
        if "Master Sword" in self.starting_items and not self.shuffle_master_sword:
            raise ValueError(
                "Starting with Master Sword requires Master Sword shuffle; the native pedestal owns it otherwise"
            )
        if not isinstance(self.logic, dict) or not all(isinstance(key, str) for key in self.logic):
            raise ValueError("logic must be a table of setting names to JSON values")
        if self.goal is not None and not isinstance(self.goal, str):
            raise ValueError("goal must be a rule string")
        for name, what in (("item_location_types", "location types"), ("location_type_items", "items")):
            table = getattr(self, name)
            if not isinstance(table, dict):
                raise ValueError(f"{name} must be a table")
            held = {}
            for key, values in table.items():
                if not isinstance(key, str) or not isinstance(values, (tuple, list)):
                    raise ValueError(f"{name} must map names to lists of {what}")
                if not all(isinstance(value, str) for value in values):
                    raise ValueError(f"{name} must contain {what} names")
                held[key] = tuple(sorted(set(values)))
            object.__setattr__(self, name, held)
        try:
            json.dumps(self.logic, allow_nan=False)
        except (ValueError, TypeError) as error:
            raise ValueError("logic must contain finite JSON values") from error
        if self.dungeon_items not in DUNGEON_ITEM_CHOICES:
            raise ValueError(f"dungeon_items must be one of {DUNGEON_ITEM_CHOICES}, not {self.dungeon_items!r}")
        if self.dungeon_items != "own_dungeon" and "Chest" not in self.shuffle:
            # Round 18: released keys, the Well floor key among them, leave their dungeon only into chests.
            choice = "Small keys anywhere" if self.dungeon_items == "anywhere" else "All dungeon items anywhere"
            raise ValueError(f"{choice} needs Chests set to Shuffled.")
        if sources := sorted(set(self.shuffle) & {FLOOR_KEY_SOURCE, HIDEOUT_KEY_SOURCE}):
            raise ValueError(
                f"{sources} are not shuffle kinds: floor keys follow dungeon_items, jail keys shuffle_hideout_keys"
            )
        if not isinstance(self.shuffle_hideout_keys, bool):
            raise ValueError("shuffle_hideout_keys must be a boolean")
        if self.shuffle_hideout_keys and "Chest" not in self.shuffle:
            raise ValueError("shuffle_hideout_keys moves the jail keys into shuffled chests: shuffle Chest")
        if type(self.shuffle_100_token_reward) is not bool:
            raise ValueError("shuffle_100_token_reward must be a boolean")
        # ``clawshot.patch.gifts.seed_setup`` expands Gift to NPC; an effective (spoiler) string names NPC.
        if self.shuffle_100_token_reward and not {"Gift", "NPC"} & set(self.shuffle):
            raise ValueError(
                "shuffle_100_token_reward needs the 100-token House reward among shuffled gifts: shuffle Gift"
            )
        if type(self.dungeon_rewards) is not bool:
            raise ValueError("dungeon_rewards must be a boolean")
        if type(self.shuffle_master_sword) is not bool:
            raise ValueError("shuffle_master_sword must be a boolean")
        if self.shuffle_master_sword and "Chest" not in self.shuffle:
            raise ValueError("Master Sword shuffle needs Chests set to Shuffled.")
        if SWORD_PEDESTAL_SOURCE in self.shuffle:
            raise ValueError("SwordPedestal is not a shuffle kind: use shuffle_master_sword")
        limits = {"vanilla": 0, "stones": 3, "medallions": 6, "rewards": 9, "tokens": 100}
        if not isinstance(self.bridge, str) or self.bridge not in limits:
            raise ValueError("bridge must be vanilla, stones, medallions, rewards or tokens")
        if type(self.bridge_count) is not int or not 0 <= self.bridge_count <= limits[self.bridge]:
            raise ValueError(f"bridge_count for {self.bridge} must be an integer from 0 to {limits[self.bridge]}")
        if type(self.trials_count) is not int or not 0 <= self.trials_count <= 6:
            raise ValueError("trials_count must be an integer from 0 to 6")
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
        if not isinstance(self.skippable_story, bool):
            raise ValueError("skippable_story must be a boolean")
        if self.skippable_story:
            raise ValueError("Skippable story dialogue isn't available yet")
        if type(self.skip_saria_farewell) is not bool:
            raise ValueError("skip_saria_farewell must be a boolean")
        if type(self.event_item_models) is not bool:
            raise ValueError("event_item_models must be a boolean")
        if not isinstance(self.forest, str) or self.forest not in CATALOG["forest"]:
            raise ValueError("forest must be 'closed', 'closed_deku' or 'open'")
        if self.door_of_time not in ("closed", "song_only", "open"):
            raise ValueError("door_of_time must be 'closed', 'song_only' or 'open'")
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
            "dungeon_rewards": self.dungeon_rewards,
            "bridge": self.bridge,
            "bridge_count": self.bridge_count,
            "logic": {k: self.logic[k] for k in sorted(self.logic)},
            "fast_start": list(self.fast_start),
            "skippable_story": self.skippable_story,
            "skip_saria_farewell": self.skip_saria_farewell,
            "songs": self.songs,
            "shop_prices": self.shop_prices,
            "shop_slots": self.shop_slots,
            "scrub_prices": self.scrub_prices,
            "scrub_price": self.scrub_price,
            "cheap_deku_shield": self.cheap_deku_shield,
            "forest": self.forest,
            "door_of_time": self.door_of_time,
            "hints": self.hints,
            "hint_distribution": self.hint_distribution,
        }
        if self.areas:
            out["areas"] = list(self.areas)
            out["goal"] = self.goal
        if self.shuffle_hideout_keys:
            out["shuffle_hideout_keys"] = True  # absent when off: existing settings strings and logs keep their bytes
        if self.shuffle_master_sword:
            out["shuffle_master_sword"] = True
        if self.shuffle_100_token_reward:
            out["shuffle_100_token_reward"] = True  # absent when off, like shuffle_hideout_keys
        if self.excluded_locations:
            out["excluded_locations"] = list(self.excluded_locations)
        if self.starting_items:
            out["starting_items"] = list(self.starting_items)
        if self.starting_hearts:
            out["starting_hearts"] = self.starting_hearts
        if not self.event_item_models:
            out["event_item_models"] = False  # absent when on (the default): existing strings keep their bytes
        if self.starting_full_wallet:
            out["starting_full_wallet"] = True
        if self.trials_count != 6:
            out["trials_count"] = self.trials_count
        if self.item_location_types:
            out["item_location_types"] = {
                k: list(self.item_location_types[k]) for k in sorted(self.item_location_types)
            }
        if self.exclusive_location_types:
            out["exclusive_location_types"] = list(self.exclusive_location_types)
        if self.location_type_items:
            out["location_type_items"] = {
                k: list(self.location_type_items[k]) for k in sorted(self.location_type_items)
            }
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
    """Whether ``item`` must stay in its own dungeon: a dungeon item whose type its ``dungeon_items`` mode does not
    release (:data:`RELEASED_DUNGEON_ITEM_TYPES`). With ``own_dungeon`` every one; with ``anywhere`` every one but
    the small keys (boss keys, maps and compasses stay); with ``all_anywhere`` only the types no chest grant
    credits (key rings, silver rupees)."""
    info = world.items[item]
    return info.dungeon is not None and info.type not in RELEASED_DUNGEON_ITEM_TYPES[settings.dungeon_items]


def key_source_types(settings: Settings) -> tuple[str, ...]:
    """The key-source location types a seed shuffles besides ``shuffle``, chosen by its settings, never named in them:
    the floor keys' when small keys leave their dungeon into shuffled chests, the jail keys' with
    ``shuffle_hideout_keys``. Own-dungeon floor keys stay native."""
    kinds = []
    if SMALL_KEY in RELEASED_DUNGEON_ITEM_TYPES[settings.dungeon_items]:
        kinds.append(FLOOR_KEY_SOURCE)
    if settings.shuffle_hideout_keys:
        kinds.append(HIDEOUT_KEY_SOURCE)
    return tuple(kinds)


def _in_dungeon_area(world: World, location: str, dungeon: str) -> bool:
    """Logical dungeon routes can contain checks physically outside its Banc (the Spirit hands).

    Region.area identifies the dungeon's Banc; Location.area includes the physical overrides.
    Area-less synthetic worlds retain their logical-only policy (None equals None).
    """
    loc = world.locations[location]
    region = world.regions[loc.region]
    return region.dungeon == dungeon and loc.area == region.area


def allowed(world: World, settings: Settings, location: str, item: str) -> bool:
    """Whether ``item`` may go to ``location`` at all, reachable or not. A world from :func:`with_screens` (every
    :func:`fill`, every external assignment) also carries the seed's tier and ammo-container screens."""
    if item in world.locations[location].excluded_items:
        return False
    if location in world.settings.get("tier_forbidden", {}).get(item, ()):
        return False
    if location in world.settings.get("container_forbidden", {}).get(item, ()):
        return False
    if world.locations[location].type == "Shop":
        if item not in world.settings.get("native_shop_items", ()):
            return False
        destinations = world.settings.get("shop_item_locations", {}).get(item)
        if destinations is not None and location not in destinations:
            return False
    location_type = world.locations[location].type
    if settings.dungeon_rewards:
        # Reward-only means both directions, even if an advanced recipe loosens derived restrictions.
        reward = world.items[item].stone or world.items[item].medallion
        if reward != (location_type == "DungeonReward"):
            return False
    if item.startswith(SHOP_ONLY_PREFIX) and location_type != "Shop":
        return False
    if location_type == "Missable" and world.items[item].progression:
        return False
    # Only a supported kind of check can grant the next tier of a raw progressive copy (``World.progressive``).
    if item in world.progressive and location_type not in world.progressive_destinations:
        return False
    palette = settings.location_type_items.get(location_type)
    if palette is not None and item not in palette:
        return False
    types = settings.item_location_types.get(item)
    if types is not None and location_type not in types:
        return False
    if location_type in settings.exclusive_location_types and (types is None or location_type not in types):
        return False
    if world.items[item].type == HIDEOUT_SMALL_KEY and (
        not settings.shuffle_hideout_keys or location_type not in HIDEOUT_KEY_DESTINATIONS
    ):
        return False  # only a named chest grant or a jail source's native key credits the Fortress
    if world.items[item].type in CHEST_HELD_DUNGEON_TYPES and location_type not in CHEST_HELD_DESTINATIONS:
        return False  # even in its own dungeon: only a chest's grant is known to credit the dungeon
    dungeon = world.items[item].dungeon
    if dungeon is None or _in_dungeon_area(world, location, dungeon):
        return True
    # A released dungeon item outside its dungeon needs a source-bound grant, which only a chest's binding can carry.
    return not is_restricted(world, settings, item) and location_type == "Chest"


def shuffled_locations(world: World, settings: Settings) -> list[str]:
    """Locations of a shuffled type (``shuffle`` and :func:`key_source_types`) that hold an item in the remake (not
    N64-only) and are not held to their vanilla item (``keep_vanilla``, a reason, e.g. the Treasure Chest Game's room
    boxes: D17). The others keep their vanilla item."""
    kinds = {*settings.shuffle, *key_source_types(settings)}
    if settings.shuffle_master_sword:
        kinds.add(SWORD_PEDESTAL_SOURCE)
    return [
        name
        for name, loc in world.locations.items()
        if (loc.type in kinds or (settings.dungeon_rewards and loc.type == "DungeonReward"))
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
    natives_first: bool = False,
    first: frozenset[str] = frozenset(),
    later: list[str] | None = None,
) -> int:
    """OoT Randomizer ``fill_restrictive``: take items from the end of ``items``; put each in a location that is
    reachable holding ``assumed``, the items still to place and whatever the placements so far give.

    Items with a native shop display are taken last, leaving chests to items that can only go there, unless
    ``natives_first``: the progression stage takes them first, while the other shield can still open the way past
    Mido. Taken last, the second shield found every chest before Mido full (Chest+Shop: 11 of 130 failed attempts).
    Then the ``first`` items, before the rest of the stage, while the most is still assumed and reachable.

    Given the ``later`` stages' items, chests are kept for the items that need one (:func:`_chest_bound`): once the
    empty chests those items may take are no more than those items, here and later, any other item takes another
    check, or a chest none of them may take, when it can. Native displays keep their own shop reserve above.

    An item with no reachable location left swaps into one this call filled before (:func:`_swap`); the displaced
    item goes back to be placed next, under the same rules."""
    native = world.settings.get("native_shop_items", ()) if "Shop" in settings.shuffle else ()
    # Reserve only the slots needed by remaining refills, not every shop slot.
    items.sort(key=lambda name: (not world.items[name].priority, (name in native) == natives_first, name in first))
    filled: list[str] = []
    swaps: dict[str, int] = {}
    if later is not None:
        bound, useful = _chest_bound(world, settings, locations, [*items, *later])
        later_bound = sum(item in bound for item in later)
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
        elif later is not None and item not in bound:
            chests = sum(name in useful for name in locations)
            if chests <= later_bound + sum(name in bound for name in items):
                candidates.sort(key=lambda name: name in useful)
        spot = next((name for name in candidates if search.can_access(world.locations[name])), None)
        if spot is not None:
            locations.remove(spot)
            filled.append(spot)
        else:
            spot = _swap(world, settings, placements, filled, item, [*assumed, *items], swaps)
            if spot is not None:
                displaced = placements[spot]
                items.append(displaced)  # placed next
                shop_refills += _is_shop_refill(settings, displaced)
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
        shop_refills -= _is_shop_refill(settings, item)
    return shop_refills


def _is_shop_refill(settings: Settings, item: str) -> bool:
    return item.startswith("Buy ") and settings.item_location_types.get(item) == ("Shop",)


def _chest_bound(world: World, settings: Settings, locations: list[str], items: list[str]) -> tuple[set[str], set[str]]:
    """The ``items`` that need a chest, and the empty chests every one of them may take.

    An item needs one when no other empty location may take it, or when it is a released dungeon item: outside its
    dungeon only a chest takes it, and its own floor-key source does not make it flexible (round 21: maps and compasses
    counted as flexible because of one other check in their dungeon were stranded in 14 of 200 seeds).
    A chest only some of them may take (``Hyrule Field Chest (Obj_Heart_Piece)`` refuses maps) is not counted."""
    others = [name for name in locations if world.locations[name].type != "Chest"]
    bound = {
        item
        for item in dict.fromkeys(items)
        if (world.items[item].dungeon is not None and not is_restricted(world, settings, item))
        or not any(allowed(world, settings, name, item) for name in others)
    }
    chests = [name for name in locations if world.locations[name].type == "Chest"]
    useful = {name for name in chests if all(allowed(world, settings, name, item) for item in bound)}
    return bound, useful


def _swap(
    world: World,
    settings: Settings,
    placements: dict[str, str],
    filled: list[str],
    item: str,
    assumed: list[str],
    swaps: dict[str, int],
) -> str | None:
    """Archipelago's swap (``Fill.py`` ``fill_restrictive``, ``swap=True``, at 1041167c, MIT): the first location this
    stage filled, in filling order, that ``item`` may take and that is reachable holding ``assumed`` without the item
    there now. That item is displaced and placed again; an item name is displaced at most twice. Only Archipelago's
    safe swaps: its unsafe ones assume the displaced item, which nothing guarantees can still be reached.

    With the forest closed, the last progression items can only go to the five chests before Mido; an earlier item
    had taken them in 13 of the 14 failed attempts of 200 Gift seeds (Kokiri Sword, Fairy Ocarina, Slingshot,
    Boomerang)."""
    for spot in filled:
        displaced = placements[spot]
        if displaced == item or swaps.get(displaced, 0) > 1 or not allowed(world, settings, spot, item):
            continue
        del placements[spot]
        search = Search(world, assumed)
        search.collect_spheres(placements)
        placements[spot] = displaced
        if search.can_access(world.locations[spot]):
            swaps[displaced] = swaps.get(displaced, 0) + 1
            return spot
    return None


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


def return_guarantee_conflict(world: World, settings: Settings, vanilla: Mapping[str, str] | None = None) -> str | None:
    """Why the return-kit stage cannot support this door mode's configured first-pull inventory, or None.

    This is a generator limitation, not proof that no physical route exists. The kit starts adult Link holding
    only ``age_return_fill_inventory``. As an upper bound, give every shuffled location's effective pool item,
    every non-progression item and every dungeon reward, then search unshuffled checks in place. Apply the same
    native ``vanilla`` overrides as the fill; if even that cannot open the gate, the kit stage cannot succeed.

    For song_only, the actual earliest pull can require more: the fixed Time-song gift requires all three stones
    (hyrule_field.toml:18-19), unlike the configured Ocarina + Time-song bound. Do not call this physically impossible.
    None (undecided) for a missing gate/first pull (a slice), or a shuffle meta-kind absent from the world (Gift
    before seed setup expands it). The seed pipeline checks again after that setup.

    The pool is the native progressive one: :func:`clawshot.generate.progressive.normalize_pool` is applied here too,
    so a caller that gives no ``vanilla`` (the UI's settings check) sees the seed's raw copies.
    """
    families = world.settings.get("age_return_fill_families", ())
    if world.age_return is None or not world.settings.get("age_return_guarantee", False) or not families:
        return None
    event, region = world.age_return
    events = {e.name for e in world.events}
    if region not in world.regions or event not in events or world.age_pull_event not in events:
        return None
    types = {loc.type for loc in world.locations.values()}
    if any(kind not in types for kind in settings.shuffle):
        return None
    from clawshot.generate.progressive import normalize_pool

    vanilla = dict(vanilla or {})
    vanilla.update(normalize_pool(world, settings, vanilla))

    def vanilla_item(name: str) -> str | None:
        return vanilla.get(name, world.locations[name].vanilla)

    shuffled = shuffled_locations(world, settings)
    pool = [vanilla_item(name) for name in shuffled]
    moving = set(shuffled)
    fixed = {
        name: vanilla_item(name)
        for name, loc in world.locations.items()
        if name not in moving and vanilla_item(name) is not None and loc.n64_only is None
    }
    pooled = set(pool)
    possible = pool + [
        name
        for name, item in world.items.items()
        if item.type != "Event" and (not item.progression or item.type == "DungeonReward") and name not in pooled
    ]
    inventory = world.settings.get("age_return_fill_inventory", {})
    held = [name for name, count in inventory.items() for _ in range(count)]

    def opens(extra: Iterable[str]) -> bool:
        search = Search.adult_after_pull(world, [*held, *possible, *extra])
        search.collect_spheres(fixed)
        return search.holds(event) and search.can_reach(region, ADULT)

    if opens(()):
        return None
    # Return-kit families that only unshuffled checks give: the ones the kit cannot forward-place.
    moved = {_age_family(world, item) for item in pool}
    withheld = sorted(({_age_family(world, item) for item in fixed.values()} & set(families)) - moved)
    from clawshot.generate.names import load as location_names

    door = world.settings.get("door_of_time")
    holding = f"holding only {', '.join(sorted(inventory))}" if inventory else "before finding anything"
    start = (
        f"door_of_time = {door!r} with shuffle {list(settings.shuffle)} is not supported with the adult-return "
        f"guarantee (logic age_return_guarantee): the generator's return kit assumes Link may pull the Master Sword "
        f"{holding} (age_return_fill_inventory for this door mode), then must reach {event!r} to return to child."
    )
    if not withheld or not opens(name for name in world.items if _age_family(world, name) in withheld):
        return (
            f"{start} Under that assumption, adult Link cannot reach it even with every item the fill can place. "
            "Choose door_of_time = 'closed'."
        )
    catalog = location_names()
    sources = [name for name, item in fixed.items() if _age_family(world, item) in withheld]
    checks = ", ".join(sorted(catalog[name].name if name in catalog else name for name in sources))
    kinds = ", ".join(sorted({world.locations[name].type for name in sources}))
    advice = (
        "Choose door_of_time = 'closed', or also shuffle those checks "
        f"(their kinds: {kinds}; the Gift shuffle moves gifts and songs)."
    )
    if "Goron Bracelet" in world.start_items and "Sarias Song" in withheld:
        advice = (
            "Starting with the Goron Bracelet needs Saria's Song as a starting item, "
            "song shuffle (the Gift option), or free time travel."
        )
    return (
        f"{start} Even with every item the fill can place, that assumed start still needs {', '.join(withheld)}, "
        f"which stay at unshuffled checks adult Link cannot reach first ({checks}). "
        f"{advice}"
    )


def _assumable(world: World, settings: Settings, items: list[str]) -> list[str]:
    """What a stage may assume collected: the items a later stage places where they can be reached.

    Not junk: the fast fill puts it anywhere, though a rule may read it (shops.toml's ``Nuts`` and ``Sticks`` read the
    physical nut and stick packs, normal items so hints never name them, D29; assumed, a pack let the Kokiri Sword go
    to a Deku Scrub and the fast fill then put every pack behind Mido). Not the bomb and Bombchu packs either, until
    their own stage: D25 puts every pack where only a Bomb Bag reaches, so a placement that needed a pack could leave
    the last pack nowhere (seed 7 Gift: Zelda's Letter behind Bombchus, every Bombchu pack behind a bag that needed
    the letter)."""
    return [
        item
        for item in items
        if not item.startswith(_BOMB_AMMO_PREFIXES)
        and (
            world.items[item].progression
            or item in settings.item_location_types
            or is_restricted(world, settings, item)
        )
    ]


def _without_ammo_container(
    world: World,
    pool: list[str],
    placements: Mapping[str, str],
    prefixes: tuple[str, ...],
    containers: tuple[str, ...],
    refills: tuple[str, ...],
    events: tuple[str, ...],
) -> Search:
    sources = {
        name for name in world.items if _age_family(world, name) in containers or name.startswith((*prefixes, *refills))
    } | set(events)
    return Search(
        replace(
            world,
            start_items=tuple(item for item in world.start_items if item not in sources),
            events=[event for event in world.events if event.name not in sources],
        ),
        (item for item in [*pool, *placements.values()] if item not in sources),
    )


def _container_forbidden(
    world: World, locations: list[str], pool: list[str], placements: Mapping[str, str]
) -> dict[str, frozenset[str]]:
    """Screen ammo before palettes, type-held fill, swaps, filler or an external assignment can bypass a container.

    Holding every other item, a destination must still be unreachable without an independent container provider.
    D25: bomb and Bombchu packs go only where the Bomb Bag is guaranteed, at every location. At Skulltulas every other
    ammo family needs its container too. This is D25's counterfactual, not an assumption that an ammo get will create
    a bag or weapon. Native new games already have an empty Nut Bag (``token_starting_containers``); that sourced world
    fact needs no Skulltula gate.
    """
    skulltulas = [name for name in locations if world.locations[name].type == "Token"]
    starting = world.settings.get("token_starting_containers", ())
    forbidden = {}
    for family, contract in _AMMO_CONTAINERS.items():
        destinations = locations if family == "bomb" else skulltulas
        if family != "bomb" and family in starting:  # D25 has no starting-container exception
            destinations = []
        ammo = dict.fromkeys(item for item in pool if item.startswith(contract[0]))
        if not destinations or not ammo:
            continue
        without = _without_ammo_container(world, pool, placements, *contract)
        blocked = frozenset(name for name in destinations if without.can_access(world.locations[name]))
        if blocked:
            forbidden.update(dict.fromkeys(ammo, blocked))
    return forbidden


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
    or logical bag alias in the counterfactual inventory. The seed's container screen
    (:func:`with_screens`) already holds every location reachable without a bag, the same for every pack.
    """
    ammo = [item for item in pool if item.startswith(_BOMB_AMMO_PREFIXES)]
    if not ammo:
        return
    without_bag = world.settings.get("container_forbidden", {}).get(ammo[0], frozenset())
    destinations = [name for name in locations if name not in without_bag]
    pool[:] = [item for item in pool if not item.startswith(_BOMB_AMMO_PREFIXES)]
    # Dungeon items already own their slots; place constrained ammo before unrestricted filler.
    # Assumed fill still requires actual reachability and respects dungeon/display restrictions.
    held = settings.item_location_types
    shop_refills = sum(item.startswith("Buy ") and held.get(item) == ("Shop",) for item in pool)
    _fill_restrictive(
        world,
        settings,
        rng,
        placements,
        destinations,
        ammo,
        _assumable(world, settings, pool),
        shop_refills,
        "bomb ammo",
    )
    locations[:] = [name for name in locations if name not in placements]


def _tier_chains(world: World) -> dict[str, list[str]]:
    """Conservatively ordered native-slot tiers, lowest first; age-separated items are exempt.

    This is independent of the MAX-combined logical family level.
    """
    chains = {}
    exemptions = world.settings.get("downgrade_tier_exemptions", ())
    for family in world.settings.get("downgrade_tier_families", ()):
        tiers = sorted(
            (item.alias[1], name)
            for name, item in world.items.items()
            if item.tier and item.alias[0] == family and name not in exemptions
        )
        if tiers:
            chains[family] = [name for _, name in tiers]
    return chains


def tier_forbidden(world: World, items: list[str], fixed: Mapping[str, str]) -> dict[str, frozenset[str]]:
    """Locations each higher fixed tier may not take: reachable without a lower tier the seed holds.

    Assume only the shuffled ``items``; collect ``fixed`` checks through their real rules. Pre-owning fixed
    rewards would bypass prerequisites such as the Silver Scale needed for Ruto's Letter and time travel.
    Exclude the lower tier, the target and later tiers, and genuine family copies from both sources, so a higher
    tier cannot prove its own prerequisite. The completed placements are checked again by ``tier_order_violations``.
    """
    held = {*items, *fixed.values()}
    forbidden: dict[str, set[str]] = {}
    for family, tiers in _tier_chains(world).items():
        for index, low in enumerate(tiers[:-1]):
            if low not in held or low in world.start_items:
                continue  # a tier the seed never gives, or always starts with, cannot downgrade anything
            excluded = {family, *tiers[index:]}
            without = Search(
                replace(world, start_items=tuple(item for item in world.start_items if item not in excluded)),
                (item for item in items if item not in excluded),
            )
            without.collect_spheres({name: item for name, item in fixed.items() if item not in excluded})
            reachable = {name for name, location in world.locations.items() if without.can_access(location)}
            for high in tiers[index + 1 :]:
                forbidden.setdefault(high, set()).update(reachable)
    return {item: frozenset(names) for item, names in forbidden.items()}


def with_screens(world: World, shuffled: list[str], pool: list[str], fixed: Mapping[str, str]) -> World:
    """``world`` carrying the seed's placement screens, which :func:`allowed` reads: each higher fixed tier's forbidden
    locations (:func:`tier_forbidden`) and ammo whose container is not guaranteed (:func:`_container_forbidden`: D25
    bomb packs anywhere, every ammo family at Skulltulas).

    ``pool`` holds every item the ``shuffled`` locations may give, ``fixed`` the other locations' placements.
    :func:`fill` screens its pool before any stage; ``generate.from_placements`` screens before it checks a supplied
    assignment, so neither can place past a screen."""
    # Strength and scales: a higher fixed tier goes only where every lower tier the seed holds is mandatory.
    forbidden = tier_forbidden(world, pool, fixed)
    if forbidden:
        world = replace(world, settings={**world.settings, "tier_forbidden": forbidden})
    containers = _container_forbidden(world, shuffled, pool, fixed)
    if containers:
        world = replace(world, settings={**world.settings, "container_forbidden": containers})
    return world


def tier_order_violations(world: World, placements: Mapping[str, str]) -> list[tuple[str, str, str]]:
    """``(lower tier, higher tier, its location)`` for a higher tier reachable without owning a lower tier.

    Withhold every location giving that lower tier and collect the actual placements. Native pairs have the same
    requirement as shuffled pairs; being available in an earlier sphere is not enough. A lower tier absent from
    the seed, or owned from the start, cannot be picked up later to downgrade the higher tier.
    """
    chains = _tier_chains(world)
    where: dict[str, list[str]] = {}
    for name, item in placements.items():
        where.setdefault(item, []).append(name)
    violations = []
    for tiers in chains.values():
        for index, low in enumerate(tiers[:-1]):
            lows = set(where.get(low, ()))
            if not lows or low in world.start_items:
                continue
            higher = [(high, location) for high in tiers[index + 1 :] for location in where.get(high, ())]
            if not higher:
                continue
            search = Search(world)
            search.collect_spheres({name: item for name, item in placements.items() if name not in lows})
            violations.extend((low, high, location) for high, location in higher if location in search.collected)
    return violations


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
    keys; no chest there needs its boss key. Fire Temple keys were all 134 failed attempts of 200 chest-only seeds."""
    items = [item for item in pool if is_restricted(world, settings, item) and dungeons(world.items[item].dungeon)]
    if not items:
        return shop_refills
    for item in items:
        pool.remove(item)
    order = {"SmallKey": 3, "SmallKeyRing": 3, "BossKey": 2, "GanonBossKey": 2}
    items.sort(key=lambda name: order.get(world.items[name].type, 1))  # taken from the end
    return _fill_restrictive(
        world, settings, rng, placements, locations, items, _assumable(world, settings, pool), shop_refills, "dungeon"
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


def _fill_palettes(
    world: World,
    settings: Settings,
    rng: random.Random,
    placements: dict[str, str],
    locations: list[str],
    pool: list[str],
    shop_refills: int,
) -> int:
    """Fill the non-Skulltula ``location_type_items`` palettes before anything else can need them,
    as OoT Randomizer fills its shop locations first (``distribute_items_restrictive``, 526b4c8d).

    The items are those that may go nowhere else (a shield held to Freestanding), then the first of the shuffled pool
    that the type may take, as many as it has locations. Holding every other item away from these locations instead
    sent the junk through the reachability stages with the progression, where it took the early chests
    (Chest+Freestanding seed 7: no reachable location for the Boomerang)."""
    for location_type in sorted(settings.location_type_items):
        if location_type == "Token":
            continue
        destinations = [name for name in locations if world.locations[name].type == location_type]
        if not destinations:
            continue
        elsewhere = [name for name in locations if world.locations[name].type != location_type]
        fits = {item: any(allowed(world, settings, name, item) for name in destinations) for item in set(pool)}
        only = {item: fits[item] and not any(allowed(world, settings, n, item) for n in elsewhere) for item in fits}
        items = [item for item in pool if only[item]] + [item for item in pool if fits[item] and not only[item]]
        items = items[: len(destinations)]
        if len(items) < len(destinations):
            raise FillError(
                f"{location_type}: {len(destinations)} locations but {len(items)} items they may take",
                stage=location_type,
            )
        for item in items:
            pool.remove(item)
        shop_refills = _fill_restrictive(
            world,
            settings,
            rng,
            placements,
            destinations,
            items,
            _assumable(world, settings, pool),
            shop_refills,
            location_type,
        )
        locations[:] = [name for name in locations if name not in placements]
    return shop_refills


def _fill_token_filler(
    world: World,
    settings: Settings,
    rng: random.Random,
    placements: dict[str, str],
    locations: list[str],
    pool: list[str],
) -> None:
    """Match remaining Skulltulas to filler copies after progression, using the unchanged placement predicate.

    Items with nowhere else to go are mandatory. Optional ammo bundles compete for their actual shared capacity;
    an augmenting path can move an earlier flexible rupee to make room, or skip an excess bundle for other filler.
    The shuffled pool and seeded destination order make the matching deterministic without fixing a cohort first.
    """
    destinations = [name for name in locations if world.locations[name].type == "Token"]
    if not destinations:
        return
    elsewhere = [name for name in locations if world.locations[name].type != "Token"]
    rng.shuffle(destinations)
    compatible = {
        item: [name for name in destinations if allowed(world, settings, name, item)] for item in dict.fromkeys(pool)
    }
    only = {item: not any(allowed(world, settings, name, item) for name in elsewhere) for item in compatible}
    assigned: dict[str, int] = {}

    def match(index: int, seen: set[str]) -> bool:
        for name in compatible[pool[index]]:
            if name in seen:
                continue
            seen.add(name)
            previous = assigned.get(name)
            if previous is None or match(previous, seen):
                assigned[name] = index
                return True
        return False

    for index, item in enumerate(pool):
        if only[item] and not match(index, set()):
            raise FillError(
                f"Token: no compatible capacity for mandatory {item!r}; candidates: {compatible[item]}",
                stage="Token",
                item=item,
                allowed=tuple(compatible[item]),
            )
    for index, item in enumerate(pool):
        if len(assigned) == len(destinations):
            break
        if not only[item]:
            match(index, set())
    if len(assigned) != len(destinations):
        empty = [name for name in destinations if name not in assigned]
        raise FillError(f"Token: no compatible filler for {empty}", stage="Token", allowed=tuple(empty))
    used = set(assigned.values())
    for name in destinations:
        placements[name] = pool[assigned[name]]
    pool[:] = [item for index, item in enumerate(pool) if index not in used]
    locations[:] = [name for name in locations if name not in placements]


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
    world = with_screens(world, shuffled, pool, placements)
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
    shop_refills = _fill_palettes(world, settings, rng, placements, locations, pool, shop_refills)
    unrestricted = pool
    # Progression-compatible Token holds stay shared; normal held items need their slots before tokens consume them.
    token_held = {item for item, kinds in held.items() if "Token" in kinds} if "Token" in settings.shuffle else set()
    # Type-held ammo still needs the stronger D25 bag gate in its dedicated stage.
    type_held = [
        item
        for item in unrestricted
        if item in held
        and (item not in token_held or not world.items[item].progression)
        and not item.startswith(_BOMB_AMMO_PREFIXES)
    ]
    unrestricted = [item for item in unrestricted if item not in type_held]
    shop_refills = _fill_type_held(
        world, settings, rng, placements, locations, type_held, _assumable(world, settings, unrestricted), shop_refills
    )
    _fill_bomb_ammo(world, settings, rng, placements, locations, unrestricted)
    progression = [item for item in unrestricted if world.items[item].progression]
    # Tokens held to chests and Skulltulas go first, while those are still reachable everywhere: placed in seeded
    # order among the rest, the last copies found every reachable chest and Skulltula taken by earlier copies, with
    # only gifts, songs and scrubs left to them (round 20: 4 of 9 failed first attempts of 200 broad seeds).
    first = frozenset(item for item in token_held if set(held[item]) <= {"Chest", "Token"})
    filler = [item for item in unrestricted if not world.items[item].progression]
    # The filler's maps and compasses still need chests; flexible progression took the last ones in 4 of round 20's 9.
    shop_refills = _fill_restrictive(
        world, settings, rng, placements, locations, progression, [], shop_refills, "progression", True, first, filler
    )
    _fill_token_filler(world, settings, rng, placements, locations, filler)
    priority = [item for item in filler if world.items[item].priority]
    rest = [item for item in filler if not world.items[item].priority]
    if any(world.locations[name].type == "Shop" for name in shuffled):
        native = world.settings.get("native_shop_items", ())
        priority = [*rest, *priority]  # The stack places priority items before ordinary filler.
        rest = []
        # Leave flexible native displays until filler that can only occupy chests.
        priority.sort(key=lambda item: item not in native)
        _fill_restrictive_fast(world, settings, rng, placements, locations, priority, shop_refills)
    else:
        _fill_restrictive_fast(world, settings, rng, placements, locations, priority)
        if any(world.locations[name].excluded_items for name in locations):
            _fill_restrictive_fast(world, settings, rng, placements, locations, rest)
        else:
            _fast_fill(rng, placements, locations, rest)

    if priority or rest:
        raise FillError(f"items left unplaced: {sorted(priority + rest)}")
    if locations:
        raise FillError(f"locations left empty: {sorted(locations)}")
    result = {name: placements[name] for name in world.locations if name in placements}
    # Every stage and swap applies ``allowed``; the unchecked fast fill relies on the restricted kinds being full.
    unsafe = [
        (name, item)
        for name, item in result.items()
        if name in shuffled_set and not allowed(world, settings, name, item)
    ]
    if unsafe:
        raise FillError(f"placements outside their restrictions (location, item): {unsafe[:4]}", stage="restrictions")
    violations = tier_order_violations(world, result)
    if violations:
        raise FillError(
            f"tier order: a higher tier is reachable without a lower one (lower, higher, where): {violations[:4]}",
            stage="tier order",
        )
    return result


def _refuse_traps(search: Search, sphere: int) -> None:
    if not search.world.settings.get("softlock_anchors"):
        return
    from clawshot.world.softlocks import reachable_traps

    regions = search.world.settings.get("softlock_verified_regions")
    if regions is not None and not any(search.can_reach(name) for name in regions):
        return
    if traps := reachable_traps(search, sphere, regions=regions):
        details = "; ".join(f"{t.age}: {t.region} ({t.time})" for t in traps[:8])
        raise FillError(
            f"reachable softlock after sphere {sphere}: {details}. "
            "No return path with the items held; the remake has no save warp.",
            stage="softlock",
        )


def check_no_traps(world: World, placements: Mapping[str, str]) -> None:
    """Refuse traps in the evidenced acceptance scope, including external placements."""
    if world.settings.get("softlock_anchors"):
        Search(world).collect_spheres(placements, observe=_refuse_traps)


def check_beatable(world: World, placements: dict[str, str]) -> list[list[str]]:
    """The beatability search: collect everything reachable from the start; the goal must be met. Returns the
    spheres (location names) on success."""
    search = Search(world)
    spheres = search.collect_spheres(placements, observe=_refuse_traps)
    if not search.won():
        unreached = [name for name in placements if name not in search.collected]
        raise FillError(f"the goal cannot be reached; {len(unreached)} placed items never reachable: {unreached[:10]}")
    return spheres
