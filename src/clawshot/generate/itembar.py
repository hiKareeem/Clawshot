"""Seed-specific wrong-age pickup warnings, not changes to native item permissions.

Only child Bow locking/reload recovery is game-confirmed. Other age-locked buttons and the
separate ocarina/boot shortcuts are precautionary warnings from native PouchTable metadata.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from clawshot.world.rules import AGES
from clawshot.world.search import Search

if TYPE_CHECKING:
    from clawshot.generate import Seed

CATALOG = Path(__file__).parents[1] / "data" / "itembar.toml"


@dataclass(frozen=True)
class AgeLockedPickup:
    location: str
    item: str
    usable_age: str
    first_ages: tuple[str, ...]
    sphere: int


def age_locked_pickups(seed: "Seed") -> list[AgeLockedPickup]:
    """List shuffled items first reachable by an unusable age, including same-frontier ties.

    Replay the existing oracle's complete sphere prefixes through Search, including fixed finds
    and its independent pre-return child inventory. Never assume a location's age from its area
    or grant the next sphere's items before testing access. This is a possible pickup order,
    not a prediction of the player's route; later optional wrong-age pickups remain possible.
    """
    data = tomllib.loads(CATALOG.read_text(encoding="utf-8"))
    usable = {item: age for age in AGES for item in data[age]}
    pending = {name: usable[seed.placements[name]] for name in seed.shuffled if seed.placements[name] in usable}
    if not pending:
        return []
    search = Search(seed.world)
    prefix: dict[str, str] = {}
    warnings = []
    for index, sphere in enumerate(seed.spheres, 1):
        for name, age in list(pending.items()):
            location = seed.world.locations[name]
            first_ages = tuple(a for a in AGES if search.can_access(location, a))
            if not first_ages:
                continue
            del pending[name]
            if any(a != age for a in first_ages):
                warnings.append(AgeLockedPickup(name, seed.placements[name], age, first_ages, index))
        if not pending:
            break
        prefix.update((name, seed.placements[name]) for name in sphere)
        search.collect_spheres(prefix)
    return warnings
