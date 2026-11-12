"""A concrete, replayed opening route from actual placements, not all sphere finds.

Reverse deletion retains one sufficient source witness (including OR alternatives). Each collection step
then gets its own source-minimal predecessor witness. No inventory is assumed from unlisted purchases.
A seed whose child Link alone cannot complete the milestone (an early Door of Time lets adult Link supply it)
gets an explanation instead of a guide; adult finds never enter a child opening route.
"""

import tomllib
from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from clawshot.generate.names import CATALOG, shops
from clawshot.world.model import Location
from clawshot.world.rules import CHILD
from clawshot.world.search import Search

if TYPE_CHECKING:
    from clawshot.generate import Seed


@dataclass(frozen=True)
class Step:
    kind: str
    location: str
    requires: tuple[str, ...]
    alternatives: tuple["Step", ...] = ()


@dataclass(frozen=True)
class OpeningRoute:
    name: str
    event: str
    region: str
    steps: tuple[Step, ...]
    visits: dict[str, dict]


@dataclass(frozen=True)
class NoChildOpening:
    """The configured milestone, which child Link alone cannot complete in this seed; ``reason`` says why."""

    name: str
    event: str
    region: str
    reason: str


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


def _visit_sources(seed: "Seed", config: dict) -> tuple["Seed", dict[str, dict]]:
    """Make selected implicit events explicit sources in a private proof view, never in the seed/pool."""
    visits = {}
    events = list(seed.world.events)
    locations = dict(seed.world.locations)
    placements = dict(seed.placements)
    for info in config.get("visit", ()):
        event = next((e for e in events if e.name == info["event"] and e.region == info["region"]), None)
        if event is None:
            continue  # Custom/subset worlds do not acquire a made-up free source.
        key = f"event:{event.region}:{event.name}"
        visits[key] = {**info, "item": event.name, "price": 0}
        locations[key] = Location(key, event.region, event.rule, "Event", event.name, event.source)
        placements[key] = event.name
        events.remove(event)
    if not visits:
        return seed, visits
    world = replace(seed.world, events=events, locations=locations)
    # Reverse deletion tries paid sources first; retain the free visit when its actual prerequisites suffice.
    return replace(seed, world=world, placements=placements, spheres=[list(visits), *seed.spheres]), visits


def _first_sphere(seed: "Seed", target: str) -> int | None:
    """After how many of the seed's beatability spheres the full (two-age) search holds ``target``; None if never."""
    search = Search(seed.world)
    if search.holds(target):
        return 0
    for index, sphere in enumerate(seed.spheres, 1):
        search.collect_spheres({location: seed.placements[location] for location in sphere})
        if search.holds(target):
            return index
    return None


def _no_child_opening(seed: "Seed", name: str, target: str, entry: str) -> NoChildOpening:
    """Why ``target`` has no child-only witness, read from the seed's own beatability spheres (no new rule)."""
    reached = _first_sphere(seed, target)
    if reached is None:
        reason = (
            f"The beatability search never reaches {target!r} in this seed: finishing does not need it, so there is "
            "no opening guide."
        )
    else:
        when = "from the start" if reached == 0 else f"after collection sphere {reached}"
        reason = (
            f"Child Link alone cannot reach {target!r} in this seed. The beatability search reaches it {when} only "
            "with adult Link's help (an early Door of Time allows adult Link first), so there is no child opening "
            "guide."
        )
    return NoChildOpening(name, target, entry, reason)


def opening(seed: "Seed") -> OpeningRoute | NoChildOpening | None:
    """Prove the configured child opening; absent for worlds without that milestone or an adult start.

    Outside-dungeon prerequisites that are already accessible are collected before entering. The entry row
    lists preparation for the chosen clear, not merely the weaker predicate for reaching the lobby.
    A beatable seed whose child Link alone cannot complete the milestone (adult Link first, then the return to child)
    gets :class:`NoChildOpening` instead of a route.
    """
    config = tomllib.loads(CATALOG.read_text(encoding="utf-8")).get("opening")
    if config is None or seed.world.settings.get("starting_age", CHILD) != config["age"]:
        return None
    target, entry = config["event"], config["region"]
    if entry not in seed.world.regions or not any(event.name == target for event in seed.world.events):
        return None
    original = seed
    seed, visits = _visit_sources(seed, config)
    sales = shops(seed) if visits else {}
    prefix = []
    for sphere in seed.spheres:
        prefix.extend(name for name in sphere if name in seed.placements)
        if _proof(seed, prefix).holds(target):
            break
    else:
        return _no_child_opening(original, config["name"], target, entry)
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
        name = min(accessible, key=lambda name: (name not in visits, inside(name)))
        if inside(name) and not entered:
            steps.append(Step("enter", entry, tuple(collected)))
            entered = True
        required = _minimize(
            seed, collected, lambda search, name=name: search.can_access(seed.world.locations[name], CHILD)
        )
        alternatives = ()
        if name in visits:
            alternatives = tuple(
                Step(
                    "collect",
                    other,
                    _minimize(
                        seed,
                        collected,
                        lambda search, other=other: search.can_access(seed.world.locations[other], CHILD),
                    ),
                )
                for other, item in seed.placements.items()
                if item == seed.placements[name]
                and other in sales
                and replay.can_access(seed.world.locations[other], CHILD)
            )
        steps.append(Step("visit" if name in visits else "collect", name, required, alternatives))
        replay.collect(seed.placements[name])
        collected.append(name)
        remaining.remove(name)
    if not replay.holds(target):
        raise ValueError(f"opening replay did not reach {target!r}")
    if not entered:
        steps.append(Step("enter", entry, tuple(collected)))
    steps.append(Step("complete", target, tuple(collected)))
    return OpeningRoute(config["name"], target, entry, tuple(steps), visits)
