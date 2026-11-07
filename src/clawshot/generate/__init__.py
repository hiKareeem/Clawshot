"""Seeds: the fill, the beatability search on every seed, and the spoiler log.

    seed = generate(load_spec(), 12345, Settings())
    text = spoiler_json(seed)

Same seed, settings, world data and generator version give the same placements and the same spoiler bytes: the
only randomness is ``random.Random(seed)``, and every list the fill walks is in world-file order.
"""

import json
import random
from collections.abc import Mapping
from dataclasses import dataclass
from importlib.metadata import version
from typing import Any

from clawshot.generate.fill import FillError, Settings, check_beatable, fill, shuffled_locations
from clawshot.world.load import build_world
from clawshot.world.model import World

__all__ = ["FillError", "Seed", "Settings", "generate", "spoiler", "spoiler_json"]

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


def generate(spec: Mapping[str, Any], seed: int, settings: Settings, attempts: int = FILL_ATTEMPTS) -> Seed:
    """Build the world for ``settings.logic``, fill it from ``random.Random(seed)`` and check it can be beaten.

    A failed fill is retried with the same generator (so a retry is as deterministic as the first try), up to
    ``attempts`` times; then :class:`FillError` is raised.
    """
    world = build_world(spec, settings.logic)
    rng = random.Random(seed)
    errors: list[str] = []
    for _ in range(attempts):
        try:
            placements = fill(world, settings, rng)
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
        "placements": {name: seed.placements[name] for name in seed.shuffled},
        "spheres": [sphere for sphere in spheres if sphere],
    }


def spoiler_json(seed: Seed) -> str:
    return json.dumps(spoiler(seed), indent=2, ensure_ascii=False) + "\n"
