"""Reachability: which regions, locations and events a player holding some items can get to, for each age.

Ported from OoT Randomizer's ``Search.py`` (MIT): child and adult are searched separately from the start region,
with one shared set of items and events. The start region's exits gate the other age (OoT Randomizer's ``Root
Exits``: ``is_starting_age or Time_Travel``), so playing as the other age is an event like any other, done at the
Temple of Time. Each region is reached at day, at night or both: a region where time passes has both, a region
with ``provides_time`` has that time, any other has the times of the regions it was entered from.
"""

from collections.abc import Iterable, Mapping
from typing import NamedTuple

from clawshot.world.model import Event, Exit, Location, Region, World
from clawshot.world.rules import ADULT, AGES, ALL_TIMES, CHILD, DAY, NIGHT, Rule


class Search:
    """The search over a growing item set. Collecting only ever adds, so each update resumes where the last
    stopped: nothing reached is visited again, and an exit or event that failed is tried again only once a count
    its rule reads (``Rule.reads``) has grown, or, for an event, once its region is reached at a new age or time."""

    def __init__(self, world: World, items: Iterable[str] = ()) -> None:
        self.world = world
        self.counts: dict[str, int] = {}
        self.reached: dict[str, dict[str, int]] = {CHILD: {}, ADULT: {}}
        self.collected: set[str] = set()
        """Locations whose item has been collected (by :meth:`collect_spheres`)."""
        self._pending: dict[str, list[tuple[Exit, int]]] = {age: [] for age in AGES}
        self._held: set[str] = set()
        self._events_todo: list[Event] = list(world.events)  # events to try, in world order
        # Failed exits, events and (in collect_spheres) locations wait ("park") for a count their rule reads (an item
        # or event name) to grow, events and locations also for their region to be reached at a new age or time. A
        # parked entry is listed under each of those names with the token it was parked with; waking it by one name
        # makes the other listings stale. Keys are ids of the world's exits, events and locations.
        self._by_count: dict[str, list[tuple[int, tuple, object]]] = {}
        self._by_region: dict[str, list[tuple[int, tuple, object]]] = {}
        self._parked: dict[tuple, int] = {}  # key -> token of its current parking
        self._token = 0
        self._call = 0  # collect_spheres calls so far
        self._spots_todo: list[_Spot] = []
        self._dirty = True
        start = world.regions[world.start]
        for age in AGES:
            self._reach(age, start, ALL_TIMES if start.time_passes else world.start_tod)
        for item in (*world.start_items, *items):
            self.collect(item)

    def collect(self, name: str) -> None:
        item = self.world.items.get(name)
        self._add(name, 1)
        if item is not None and item.alias is not None:
            self._add(*item.alias)
        self._dirty = True

    # the search

    def _add(self, name: str, count: int) -> None:
        self.counts[name] = self.counts.get(name, 0) + count
        self._wake(self._by_count.pop(name, ()))

    def _park(self, key: tuple, entry: object, counts: Iterable[str], region: str | None = None) -> None:
        """Park ``entry`` under ``key`` (stable for the search: ids of the world's exits and events)."""
        self._token += 1
        token = self._parked[key] = self._token
        for name in counts:
            self._by_count.setdefault(name, []).append((token, key, entry))
        if region is not None:
            self._by_region.setdefault(region, []).append((token, key, entry))

    def _wake(self, listed: Iterable[tuple[int, tuple, object]]) -> None:
        for token, key, entry in listed:
            if self._parked.get(key) != token:
                continue  # stale: woken already by another name
            del self._parked[key]
            if isinstance(entry, _Spot):
                if entry.call == self._call:
                    self._spots_todo.append(entry)
            elif isinstance(entry, Event):
                self._events_todo.append(entry)
            else:
                exit, tod = entry  # type: ignore[misc]
                self._pending[key[0]].append((exit, tod))

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
        self._wake(self._by_region.pop(region.name, ()))

    def _expand(self, age: str) -> None:
        queue = self._pending[age]  # _reach and _add append to this same list while we walk it
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
            if exit.rule.fn(self.counts, age, tod):
                self._reach(age, target, tods)
            elif exit.rule.reads is None:
                failed.append((exit, tod))  # what it reads is not known: try again at every update
            else:
                self._park((age, id(exit), tod), (exit, tod), exit.rule.reads)
        queue.extend(failed)

    def _passes(self, region: str, rule: Rule) -> bool:
        fn, counts = rule.fn, self.counts
        for age in AGES:
            known = self.reached[age].get(region, 0)
            if known & DAY and fn(counts, age, DAY):
                return True
            if known & NIGHT and fn(counts, age, NIGHT):
                return True
        return False

    def _collect_events(self) -> bool:
        todo, self._events_todo = self._events_todo, []
        new = False
        for event in todo:
            if event.name in self._held:
                continue
            if self._passes(event.region, event.rule):
                self._held.add(event.name)
                if self.counts.get(event.name, 0) < 1:
                    self._add(event.name, 1 - self.counts.get(event.name, 0))
                new = True
            elif event.rule.reads is None:
                self._events_todo.append(event)  # not known what it reads: try again at every update
            elif any(event.region in self.reached[age] for age in AGES):
                self._park((id(event),), event, event.rule.reads, event.region)
            else:
                self._park((id(event),), event, (), event.region)  # nothing to test until its region is reached
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
        if age is None:
            return self._passes(location.region, location.rule)
        fn, known = location.rule.fn, self.reached[age].get(location.region, 0)
        return bool(known & DAY and fn(self.counts, age, DAY) or known & NIGHT and fn(self.counts, age, NIGHT))

    def locations(self, age: str | None = None) -> list[str]:
        """Locations reachable (as ``age``, or as either), in world order."""
        return [name for name, loc in self.world.locations.items() if self.can_access(loc, age)]

    def won(self) -> bool:
        self.update()
        return self.world.goal(self.counts, None, self.world.start_tod)

    def collect_spheres(self, placements: Mapping[str, str]) -> list[list[str]]:
        """Collect placed items sphere by sphere until nothing new is reachable. A sphere is every location
        reachable with the items of the spheres before it (in world order); returns the location names of each
        sphere. A location that fails is tried again only once its region or a count its rule reads changes."""
        self._call += 1
        order = {name: i for i, name in enumerate(self.world.locations)}
        self._spots_todo = [
            _Spot(self._call, name, location)
            for name, location in self.world.locations.items()
            if name in placements and name not in self.collected
        ]
        spheres: list[list[str]] = []
        child, adult, counts = self.reached[CHILD], self.reached[ADULT], self.counts
        while True:
            self.update()
            todo, self._spots_todo = self._spots_todo, []
            sphere: list[str] = []
            for spot in todo:
                location = spot.location
                # _passes, inlined: this loop is the fill's hot path
                region, fn = location.region, location.rule.fn
                known_child, known_adult = child.get(region, 0), adult.get(region, 0)
                if (
                    known_child
                    and (
                        known_child & DAY and fn(counts, CHILD, DAY) or known_child & NIGHT and fn(counts, CHILD, NIGHT)
                    )
                ) or (
                    known_adult
                    and (
                        known_adult & DAY and fn(counts, ADULT, DAY) or known_adult & NIGHT and fn(counts, ADULT, NIGHT)
                    )
                ):
                    sphere.append(spot.name)
                elif location.rule.reads is None:
                    self._spots_todo.append(spot)
                elif known_child or known_adult:
                    self._park((id(location),), spot, location.rule.reads, region)
                else:
                    self._park((id(location),), spot, (), region)
            if not sphere:
                return spheres
            sphere.sort(key=order.__getitem__)
            for name in sphere:
                self.collected.add(name)
                self.collect(placements[name])
            spheres.append(sphere)


class _Spot(NamedTuple):
    """A placed location waiting in :meth:`Search.collect_spheres` (``call`` tells one call's from another's)."""

    call: int
    name: str
    location: Location


def reachable(world: World, items: Iterable[str] = ()) -> Search:
    """A search from the start state holding ``items``, brought up to date."""
    search = Search(world, items)
    search.update()
    return search
