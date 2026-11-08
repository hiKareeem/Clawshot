"""Reachability: which regions, locations and events a player holding some items can get to, for each age.

Child and adult share collected items only after the world's return gate opens. Before then the child view
contains only starting items and checks/events reachable without adult finds: an exhaustive pre-pull prefix,
not a second simultaneous player. Adult can use that prefix plus adult finds. Once the completion event holds
and adult reaches the return pedestal, both views share inventory again. Worlds without a return gate retain
OoT Randomizer's unrestricted two-age search. Time of day spreads through region exits as before.
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
        self._return_gate = world.age_return
        self._return_open = self._return_gate is None
        self._child_counts: dict[str, int] = self.counts if self._return_open else {}
        self._child_collected: set[str] = set()
        self._starting_child = world.settings.get("starting_age", CHILD) == CHILD
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
        """Add an externally supplied/assumed item to both inventory views."""
        self._collect_item(name, child=True, global_item=True)

    def _collect_item(self, name: str, *, child: bool, global_item: bool) -> None:
        item = self.world.items.get(name)
        values = ((name, 1),) if item is None or item.alias is None else ((name, 1), item.alias)
        for key, count in values:
            if global_item:
                self._add(key, count)
            if child and self._child_counts is not self.counts:
                self._add_child(key, count)
        self._dirty = True

    # the search

    def _add(self, name: str, count: int) -> None:
        self.counts[name] = self.counts.get(name, 0) + count
        self._wake(self._by_count.pop(name, ()))

    def _add_child(self, name: str, count: int) -> None:
        self._child_counts[name] = self._child_counts.get(name, 0) + count
        self._wake(self._by_count.pop(name, ()))

    def _child_active(self) -> bool:
        return self._starting_child or self._return_open

    def _open_return(self) -> bool:
        if self._return_open:
            return False
        event, region = self._return_gate
        if not self.counts.get(event, 0) or region not in self.reached[ADULT]:
            return False
        previous = self._child_counts
        self._child_counts = self.counts
        self._return_open = True
        for name, count in self.counts.items():
            if count > previous.get(name, 0):
                self._wake(self._by_count.pop(name, ()))
        return True

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
        if age == CHILD and not self._child_active():
            return
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
            counts = self._child_counts if age == CHILD else self.counts
            if exit.rule.fn(counts, age, tod):
                self._reach(age, target, tods)
            elif exit.rule.reads is None:
                failed.append((exit, tod))  # what it reads is not known: try again at every update
            else:
                self._park((age, id(exit), tod), (exit, tod), exit.rule.reads)
        queue.extend(failed)

    def _passes(self, region: str, rule: Rule) -> bool:
        return any(self._passes_age(region, rule, age) for age in AGES)

    def _passes_age(self, region: str, rule: Rule, age: str) -> bool:
        if age == CHILD and not self._child_active():
            return False
        counts = self._child_counts if age == CHILD else self.counts
        known = self.reached[age].get(region, 0)
        return bool(known & DAY and rule.fn(counts, age, DAY) or known & NIGHT and rule.fn(counts, age, NIGHT))

    def _collect_events(self) -> bool:
        todo, self._events_todo = self._events_todo, []
        new = False
        for event in todo:
            if event.name in self._held and (self._return_open or self._child_counts.get(event.name, 0)):
                continue
            child = self._passes_age(event.region, event.rule, CHILD)
            adult = self._passes_age(event.region, event.rule, ADULT)
            if child or adult:
                self._held.add(event.name)
                if self.counts.get(event.name, 0) < 1:
                    self._add(event.name, 1)
                    new = True
                if child and self._child_counts is not self.counts and not self._child_counts.get(event.name, 0):
                    self._add_child(event.name, 1)
                    new = True
                if not self._return_open and not child:
                    self._park((id(event),), event, event.rule.reads or (), event.region)
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
            new_events = self._collect_events()
            if not self._open_return() and not new_events:
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
        return self._passes_age(location.region, location.rule, age)

    def locations(self, age: str | None = None) -> list[str]:
        """Locations reachable (as ``age``, or as either), in world order."""
        return [name for name, loc in self.world.locations.items() if self.can_access(loc, age)]

    def won(self) -> bool:
        self.update()
        return self.world.goal(self.counts, None, self.world.start_tod)

    def collect_spheres(self, placements: Mapping[str, str]) -> list[list[str]]:
        """Collect placed items sphere by sphere until nothing new is reachable, in world order.

        A failed location waits for its region or rule inputs to change. A globally collected check may later
        join the child prefix without granting its item twice or appearing twice in the returned spheres.
        """
        self._call += 1
        order = {name: i for i, name in enumerate(self.world.locations)}
        self._spots_todo = [
            _Spot(self._call, name, location)
            for name, location in self.world.locations.items()
            if name in placements
            and (name not in self.collected or not self._return_open and name not in self._child_collected)
        ]
        spheres: list[list[str]] = []
        while True:
            self.update()
            todo, self._spots_todo = self._spots_todo, []
            found: list[tuple[_Spot, bool, bool]] = []
            for spot in todo:
                if spot.name in self.collected and (self._return_open or spot.name in self._child_collected):
                    continue
                location = spot.location
                region = location.region
                child = self._passes_age(region, location.rule, CHILD)
                adult = self._passes_age(region, location.rule, ADULT)
                global_item = spot.name not in self.collected and (child or adult)
                child_item = child and spot.name not in self._child_collected
                if global_item or child_item:
                    found.append((spot, child_item, global_item))
                else:
                    if location.rule.reads is None:
                        self._spots_todo.append(spot)
                    elif region in self.reached[CHILD] or region in self.reached[ADULT]:
                        self._park((id(location),), spot, location.rule.reads, region)
                    else:
                        self._park((id(location),), spot, (), region)
            if not found:
                return spheres
            found.sort(key=lambda entry: order[entry[0].name])
            sphere = []
            for spot, child, global_item in found:
                if global_item:
                    self.collected.add(spot.name)
                    sphere.append(spot.name)
                if child:
                    self._child_collected.add(spot.name)
                self._collect_item(placements[spot.name], child=child, global_item=global_item)
                if not self._return_open and not child:
                    self._park((id(spot.location),), spot, spot.location.rule.reads or (), spot.location.region)
            if sphere:
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
