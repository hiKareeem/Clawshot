"""A concrete, replayed opening route from actual placements, not all sphere finds.

Reverse deletion retains one sufficient source witness (including OR alternatives). Each collection step
then gets its own source-minimal predecessor witness. No inventory is assumed from unlisted purchases.
"""

import tomllib
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clawshot.generate.names import CATALOG
from clawshot.world.rules import CHILD
from clawshot.world.search import Search

if TYPE_CHECKING:
    from clawshot.generate import Seed


@dataclass(frozen=True)
class Step:
    kind: str
    location: str
    requires: tuple[str, ...]


@dataclass(frozen=True)
class OpeningRoute:
    name: str
    event: str
    region: str
    steps: tuple[Step, ...]


def _proof(seed: "Seed", sources: Iterable[str]) -> Search:
    search = Search.child_only(seed.world)
    search.collect_spheres({name: seed.placements[name] for name in sources})
    return search


def _minimize(seed: "Seed", sources: Iterable[str], accepts: Callable[[Search], bool]) -> tuple[str, ...]:
    kept = list(sources)
    if not accepts(_proof(seed, kept)):
        raise ValueError("opening prerequisite witness does not reach its target")
    for name in reversed(kept.copy()):
        trial = [source for source in kept if source != name]
        if accepts(_proof(seed, trial)):
            kept = trial
    return tuple(kept)


def opening(seed: "Seed") -> OpeningRoute | None:
    """Prove the configured child opening; absent for worlds without that milestone or an adult start.

    Outside-dungeon prerequisites that are already accessible are collected before entering. The entry row
    lists preparation for the chosen clear, not merely the weaker predicate for reaching the lobby.
    """
    config = tomllib.loads(CATALOG.read_text(encoding="utf-8")).get("opening")
    if config is None or seed.world.settings.get("starting_age", CHILD) != config["age"]:
        return None
    target, entry = config["event"], config["region"]
    if entry not in seed.world.regions or not any(event.name == target for event in seed.world.events):
        return None
    prefix = []
    for sphere in seed.spheres:
        prefix.extend(name for name in sphere if name in seed.placements)
        if _proof(seed, prefix).holds(target):
            break
    else:
        raise ValueError(f"no child opening witness reaches {target!r}")
    witness = _minimize(seed, prefix, lambda search: search.holds(target))
    dungeon = seed.world.regions[entry].dungeon

    def inside(name: str) -> bool:
        return seed.world.regions[seed.world.locations[name].region].dungeon == dungeon

    remaining = list(witness)
    collected = []
    steps = []
    entered = False
    replay = Search.child_only(seed.world)
    while remaining:
        accessible = [name for name in remaining if replay.can_access(seed.world.locations[name], CHILD)]
        if not accessible:
            raise ValueError(f"opening witness stalled before {remaining}")
        name = next((name for name in accessible if not inside(name)), accessible[0])
        if inside(name) and not entered:
            steps.append(Step("enter", entry, tuple(collected)))
            entered = True
        required = _minimize(
            seed, collected, lambda search, name=name: search.can_access(seed.world.locations[name], CHILD)
        )
        steps.append(Step("collect", name, required))
        replay.collect(seed.placements[name])
        collected.append(name)
        remaining.remove(name)
    if not replay.holds(target):
        raise ValueError(f"opening replay did not reach {target!r}")
    if not entered:
        steps.append(Step("enter", entry, tuple(collected)))
    steps.append(Step("complete", target, tuple(collected)))
    return OpeningRoute(config["name"], target, entry, tuple(steps))
