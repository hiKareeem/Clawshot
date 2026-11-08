"""Seeds: the fill, the beatability search on every seed, and the spoiler log.

    seed = generate(load_spec(), 12345, Settings())
    text = spoiler_json(seed)

Same seed, settings, world data and generator version give the same placements and the same spoiler bytes: the
only randomness is ``random.Random(seed)``, and every list the fill walks is in world-file order.
"""

import json
import random
from collections.abc import Mapping
from dataclasses import dataclass, replace
from importlib.metadata import version
from typing import Any

from clawshot.generate.fill import FillError, Settings, check_beatable, fill, shuffled_locations
from clawshot.world.load import build_world
from clawshot.world.model import World
from clawshot.world.shops import with_shop_prices

__all__ = ["FillError", "Seed", "Settings", "generate", "prepare", "spoiler", "spoiler_json", "world_spec"]

FILL_ATTEMPTS = 10


@dataclass(frozen=True)
class Seed:
    world: World
    seed: int
    settings: Settings
    placements: dict[str, str]
    """Every placed location (shuffled or vanilla) to its item, in world order."""
    shuffled: list[str]
    """The locations whose items were shuffled, in world order."""
    spheres: list[list[str]]
    """The beatability search's spheres: location names collected in each."""


def world_spec(spec: Mapping[str, Any], settings: Settings) -> Mapping[str, Any]:
    """The spec cut down to ``settings.areas`` (the regions in those census areas and the area-less start regions,
    whose exits elsewhere then dangle) with ``settings.goal``; the spec unchanged when no areas are given."""
    if not settings.areas:
        return spec
    areas = set(settings.areas)
    regions = [r for r in spec["regions"] if r.get("area") is None or r.get("area") in areas]
    if not any(r.get("area") in areas for r in regions):
        raise FillError(f"no region of the world lies in the areas {sorted(areas)}")
    kept = {name for r in regions for name in r.get("locations", {})}
    locations = {name: info for name, info in spec.get("locations", {}).items() if name in kept}
    return {**spec, "regions": regions, "locations": locations, "goal": settings.goal or spec["goal"]}


def prepare(spec: Mapping[str, Any], settings: Settings) -> tuple[Settings, World]:
    """The settings as a seed uses them, and the world they build.

    With ``dungeon_items = "anywhere"`` the logic setting ``keysanity`` is set too, where the world has it.
    ``skip_mido`` is derived from the same fast-start list the overlay writer uses; it cannot diverge.
    """
    logic = dict(settings.logic)
    if "skip_mido" in spec.get("settings", {}):
        skipped = "mido" in settings.fast_start
        if "skip_mido" in logic and logic["skip_mido"] != skipped:
            raise FillError("skip_mido logic must agree with the seed's fast_start settings")
        logic["skip_mido"] = skipped
    if settings.dungeon_items == "anywhere" and "keysanity" in spec.get("settings", {}):
        if logic.get("keysanity") is False:
            raise FillError("dungeon_items = 'anywhere' needs the logic setting keysanity = true")
        logic["keysanity"] = True
    settings = replace(settings, logic=logic)
    spec = with_shop_prices(spec, settings.shuffle, settings.shop_prices, settings.cheap_deku_shield)
    return settings, build_world(world_spec(spec, settings), settings.logic)


def generate(
    spec: Mapping[str, Any],
    seed: int,
    settings: Settings,
    attempts: int = FILL_ATTEMPTS,
    vanilla: Mapping[str, str] | None = None,
) -> Seed:
    """Build the world for ``settings`` (:func:`prepare`), fill it from ``random.Random(seed)`` and check it can be
    beaten.

    ``vanilla`` gives the remake's own item for locations where it differs from the world's (OoT Randomizer's):
    the pool is then what the remake hands out (``clawshot.patch.remake_vanilla``).

    A failed fill is retried with the same generator (so a retry is as deterministic as the first try), up to
    ``attempts`` times; then :class:`FillError` is raised.
    """
    settings, world = prepare(spec, settings)
    vanilla = dict(vanilla or {})
    unknown = sorted(name for name in vanilla if name not in world.locations)
    if unknown:
        raise FillError(f"vanilla items given for locations the world does not have: {unknown}")
    bad = sorted(item for item in vanilla.values() if item not in world.items)
    if bad:
        raise FillError(f"vanilla items the world does not know: {bad}")
    rng = random.Random(seed)
    errors: list[str] = []
    for _ in range(attempts):
        try:
            placements = fill(world, settings, rng, vanilla)
            break
        except FillError as e:
            errors.append(str(e))
    else:
        raise FillError(f"no beatable fill in {attempts} attempts; last: {errors[-1]}")
    spheres = check_beatable(world, placements)
    return Seed(world, seed, settings, placements, shuffled_locations(world, settings), spheres)


def spoiler(seed: Seed) -> dict[str, Any]:
    """The spoiler log: seed, settings, the shuffled placements, and the progression items sphere by sphere
    (spheres holding no progression item are left out)."""
    items = seed.world.items
    spheres = [
        {name: seed.placements[name] for name in sphere if items[seed.placements[name]].progression}
        for sphere in seed.spheres
    ]
    return {
        "generator": f"clawshot {version('clawshot')}",
        "seed": seed.seed,
        "settings": seed.settings.as_dict(),
        "settings_string": seed.settings.to_string(),
        "placements": {name: seed.placements[name] for name in seed.shuffled},
        "spheres": [sphere for sphere in spheres if sphere],
    }


def spoiler_json(seed: Seed) -> str:
    return json.dumps(spoiler(seed), indent=2, ensure_ascii=False) + "\n"
