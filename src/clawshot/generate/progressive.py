"""Native progressive chains in a seed (Round 14, issue #13; ``plans/03-game-data.md`` section 47).

Kareem, 2026-11-13: the remake's eight upgrade chains (:data:`clawshot.progressive.CHAINS`) are progressive in every
seed, always, with no setting. The world declares them (``world.toml`` ``[native_progressive]``); a seed:

1. prepares the spec (:func:`prepare_spec`): the chains checked against the catalog, the legacy ``progressive_items``
   toggle pinned off, and the world built to count only copies (``World.progressive_copies_only``);
2. holds every raw copy to the check kinds that can grant the next tier (:func:`restrict_settings`);
3. gives each chain the world has its full set of copies (:func:`normalize_pool`): each shuffled check's own fixed
   tier becomes its chain's raw copy, and ordinary chest filler makes up the rest, N copies for N tiers.

Claude approved, 2026-11-13: logic order cannot force play order, so the logic counts only copies, the Nth copy tier
N, never a native reward. An unshuffled check keeps its fixed tier as a bonus: opened before, between or after the
copies it never takes a tier away (a copy with no tier left is a harmless leftover), and the full set of copies still
reaches the last tier. Deliberate child-strength exception (Claude, 2026-11-13): world data credits Darunia's
native source as child capability, never a copy tier; child logic never relies on a copy Bracelet. Adult strength
stays copy-only. A world without ``[native_progressive]`` passes every step unchanged.
"""

from collections import Counter
from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from clawshot.generate.fill import FillError, Settings, shuffled_locations
from clawshot.progressive import CHAINS, FAMILY_BY_ITEM, next_tier
from clawshot.world.load import WorldError
from clawshot.world.model import World

LEGACY_SETTING = "progressive_items"
"""OoT Randomizer's global progressive items: a world built directly may read them; a seed never does."""


def prepare_spec(spec: Mapping[str, Any]) -> Mapping[str, Any]:
    """``spec`` ready for a seed's world: unchanged without ``native_progressive``; otherwise a new spec whose chains
    match the catalog, whose ``progressive_items`` setting is locked to ``False`` (logic naming it is an error,
    ``clawshot.world.load.resolve_settings``) and whose world counts only copies (``copies_only``). Raises
    :class:`WorldError` for chains that disagree with the catalog."""
    native = spec.get("native_progressive")
    if not native:
        return spec
    _check_chains(spec, native)
    settings = dict(spec.get("settings", {}))
    if settings.pop(LEGACY_SETTING, False):
        raise WorldError(f"[native_progressive]: the world's own {LEGACY_SETTING} must be false")
    return {
        **spec,
        "settings": settings,
        "locked": {**spec.get("locked", {}), LEGACY_SETTING: False},
        "native_progressive": {**native, "copies_only": True},
    }


def _check_chains(spec: Mapping[str, Any], native: Mapping[str, Any]) -> None:
    """The declared chains are the catalog's: every family and tier an item, a leveled family's ``[progressive]``
    tiers the catalog's in order, and ``first`` where the catalog's grant takes a missing first tier first."""
    items = spec.get("items", {})
    tiered = spec.get("progressive", {})
    known = set(items) | {tier for tiers in tiered.values() for tier in tiers}
    chains = native.get("chains", [])
    if sorted(chains) != sorted(CHAINS):
        raise WorldError(f"[native_progressive]: chains {sorted(chains)} are not the catalog's {sorted(CHAINS)}")
    for family, tiers in CHAINS.items():
        missing = sorted({tier.item for tier in tiers} - known) + ([family] if family not in items else [])
        if missing:
            raise WorldError(f"[native_progressive]: {family}: no item {missing}")
        alias = items[family].get("alias")
        logic = alias[0] if alias else family
        if logic in tiered and tiered[logic] != [tier.item for tier in tiers]:
            raise WorldError(f"[native_progressive]: {family}: [progressive] {logic!r} tiers are not the catalog's")
        first = next_tier(family, {tiers[-1].owned}) == tiers[0]
        if first != (family in native.get("first", [])):
            raise WorldError(f"[native_progressive]: {family}: first must be {str(first).lower()}, as the grant is")


def restrict_settings(world: World, settings: Settings) -> Settings:
    """``settings`` with each raw progressive copy held to the world's destination kinds (``Chest``), within any
    holding the settings already give it: the type-held fill stage places copies, and no stage, swap or filler can
    put one in a check that cannot grant the next tier. Unchanged for a world without native chains."""
    if not world.progressive:
        return settings
    held = dict(settings.item_location_types)
    for item in world.progressive:
        given = held.get(item)
        kinds = tuple(kind for kind in world.progressive_destinations if given is None or kind in given)
        if not kinds:
            raise FillError(
                f"{item}: a progressive copy may go only to {list(world.progressive_destinations)}, "
                f"but item_location_types holds it to {list(given or ())}"
            )
        held[item] = kinds
    return replace(settings, item_location_types=held)


def normalize_pool(world: World, settings: Settings, vanilla: Mapping[str, str] | None = None) -> dict[str, str]:
    """The pool overrides of a seed (merge them over ``vanilla``): every chain the world gives, at any check, gets N
    raw copies for its N tiers in the shuffled pool, so the copies alone reach its last tier.

    Each shuffled location whose effective vanilla item (``vanilla``, else the world's) is a tier of a chain gives
    that chain's copy instead; unshuffled checks keep their fixed tier, a bonus the logic never counts. Each copy
    still missing replaces one ordinary filler item of a shuffled destination check (a chest): its rupees first, then
    other plain junk, each in world order; never a key, a shop or refill item, a type-held item or progression.
    Deterministic. Raises :class:`FillError` when the seed shuffles no destination kind or has too little filler:
    the chains are never left short or fixed. Empty for a world without native chains."""
    if not world.progressive:
        return {}
    vanilla = vanilla or {}

    items = {name: vanilla.get(name, loc.vanilla) for name, loc in world.locations.items() if loc.n64_only is None}
    given = {FAMILY_BY_ITEM.get(item, item) for item in items.values()}
    chains = [family for family in world.progressive if family in given]
    if not chains:
        return {}
    destinations = world.progressive_destinations
    if not set(destinations) & set(settings.shuffle):
        raise FillError(
            f"progressive items ({', '.join(chains)}) go only to {list(destinations)} checks, so the seed must "
            f"shuffle them; shuffle is {list(settings.shuffle)}"
        )
    shuffled = shuffled_locations(world, settings)
    overrides = {}
    for name in shuffled:
        family = FAMILY_BY_ITEM.get(items[name])
        if family in world.progressive:
            overrides[name] = family
    pooled = Counter(overrides.get(name, items[name]) for name in shuffled)
    missing = [family for family in chains for _ in range(len(CHAINS[family]) - pooled[family])]
    if not missing:
        return overrides
    rupees, junk = [], []
    for name in shuffled:
        kind = world.locations[name].type
        if name not in overrides and kind in destinations and _ordinary(world, settings, items[name]):
            (rupees if items[name].startswith("Rupee") else junk).append(name)
    filler = rupees + junk
    if len(filler) < len(missing):
        short = Counter(missing)
        raise FillError(
            f"progressive items need {len(missing)} more copies ({', '.join(f'{f} x{n}' for f, n in short.items())}) "
            f"in place of ordinary filler in shuffled {list(destinations)} checks, but the seed has {len(filler)}"
        )
    overrides.update(zip(filler, missing, strict=False))
    return overrides


def _ordinary(world: World, settings: Settings, name: str | None) -> bool:
    """Plain junk a copy may replace in the pool: no progression or priority item, key, map or compass, shop or
    refill item (``Item`` type only), and nothing ``item_location_types`` holds to some checks."""
    item = world.items.get(name) if name is not None else None
    return (
        item is not None
        and item.type == "Item"
        and not item.progression
        and not item.priority
        and item.dungeon is None
        and not name.startswith("Buy ")
        and name not in settings.item_location_types
    )
