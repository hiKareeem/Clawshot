"""Reachability: which regions, locations and events a player holding some items can get to, for each age.

Ported from OoT Randomizer's ``Search.py`` (MIT): child and adult are searched separately from the start region,
with one shared set of items and events. The start region's exits gate the other age (OoT Randomizer's ``Root
Exits``: ``is_starting_age or Time_Travel``), so playing as the other age is an event like any other, done at the
Temple of Time. Each region is reached at day, at night or both: a region where time passes has both, a region
with ``provides_time`` has that time, any other has the times of the regions it was entered from.
"""

from collections.abc import Iterable, Mapping

from clawshot.world.model import Exit, Location, Region, World
from clawshot.world.rules import ADULT, AGES, ALL_TIMES, CHILD, DAY, NIGHT, Rule


class Search:
    """The search over a growing item set. Collecting only ever adds, so each update resumes where the last
    stopped: exits that failed are retried, nothing reached is visited again."""

    def __init__(self, world: World, items: Iterable[str] = ()) -> None:
        self.world = world
        self.counts: dict[str, int] = {}
        self.reached: dict[str, dict[str, int]] = {CHILD: {}, ADULT: {}}
        self.collected: set[str] = set()
        """Locations whose item has been collected (by :meth:`collect_spheres`)."""
        self._pending: dict[str, list[tuple[Exit, int]]] = {age: [] for age in AGES}
        self._held: set[str] = set()
        self._dirty = True
        start = world.regions[world.start]
        for age in AGES:
            self._reach(age, start, ALL_TIMES if start.time_passes else world.start_tod)
        for item in items:
            self.collect(item)

    def collect(self, name: str) -> None:
        item = self.world.items.get(name)
        self.counts[name] = self.counts.get(name, 0) + 1
        if item is not None and item.alias is not None:
            alias, count = item.alias
            self.counts[alias] = self.counts.get(alias, 0) + count
        self._dirty = True

    # the search

    def _reach(self, age: str, region: Region, tods: int) -> None:
        reached = self.reached[age]
        known = reached.get(region.name, 0)
        new = tods & ~known
        if not new:
            return
        reached[region.name] = known | new
        pending = self._pending[age]
        for bit in (DAY, NIGHT):
            if new & bit:
                pending.extend((exit, bit) for exit in region.exits)

    def _expand(self, age: str) -> None:
        queue = self._pending[age]  # _reach appends to this same list while we walk it
        reached = self.reached[age]
        failed: list[tuple[Exit, int]] = []
        while queue:
            exit, tod = queue.pop()
            target = self.world.regions.get(exit.target)
            if target is None:
                continue
            tods = ALL_TIMES if target.time_passes else (target.provides_time or tod)
            if not tods & ~reached.get(target.name, 0):
                continue
            if exit.rule(self.counts, age, tod):
                self._reach(age, target, tods)
            else:
                failed.append((exit, tod))
        self._pending[age] = failed

    def _passes(self, region: str, rule: Rule) -> bool:
        for age in AGES:
            known = self.reached[age].get(region, 0)
            if known & DAY and rule(self.counts, age, DAY):
                return True
            if known & NIGHT and rule(self.counts, age, NIGHT):
                return True
        return False

    def _collect_events(self) -> bool:
        new = False
        for event in self.world.events:
            if event.name not in self._held and self._passes(event.region, event.rule):
                self._held.add(event.name)
                self.counts[event.name] = max(1, self.counts.get(event.name, 0))
                new = True
        return new

    def update(self) -> None:
        """Reach every region and do every event the current items allow."""
        if not self._dirty:
            return
        while True:
            for age in AGES:
                self._expand(age)
            if not self._collect_events():
                break
        self._dirty = False

    # questions

    def can_reach(self, region: str, age: str | None = None) -> bool:
        self.update()
        return any(region in self.reached[a] for a in ((age,) if age else AGES))

    def regions(self, age: str) -> list[str]:
        """Regions reachable as ``age``, in world order."""
        self.update()
        return [name for name in self.world.regions if name in self.reached[age]]

    def holds(self, event: str) -> bool:
        self.update()
        return event in self._held

    def can_access(self, location: Location, age: str | None = None) -> bool:
        self.update()
        for a in (age,) if age else AGES:
            known = self.reached[a].get(location.region, 0)
            if known & DAY and location.rule(self.counts, a, DAY):
                return True
            if known & NIGHT and location.rule(self.counts, a, NIGHT):
                return True
        return False

    def locations(self, age: str | None = None) -> list[str]:
        """Locations reachable (as ``age``, or as either), in world order."""
        return [name for name, loc in self.world.locations.items() if self.can_access(loc, age)]

    def won(self) -> bool:
        self.update()
        return self.world.goal(self.counts, None, self.world.start_tod)

    def collect_spheres(self, placements: Mapping[str, str]) -> list[list[str]]:
        """Collect placed items sphere by sphere until nothing new is reachable. A sphere is every location
        reachable with the items of the spheres before it; returns the location names of each sphere."""
        spheres: list[list[str]] = []
        while True:
            self.update()
            sphere = [
                name
                for name, location in self.world.locations.items()
                if name in placements and name not in self.collected and self.can_access(location)
            ]
            if not sphere:
                return spheres
            for name in sphere:
                self.collected.add(name)
                self.collect(placements[name])
            spheres.append(sphere)


def reachable(world: World, items: Iterable[str] = ()) -> Search:
    """A search from the start state holding ``items``, brought up to date."""
    search = Search(world, items)
    search.update()
    return search
