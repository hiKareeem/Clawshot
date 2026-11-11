"""The patch plan: from a seed's placements, every placement-file change it takes.

A shuffled world location (OoT Randomizer's name) is one or more census chests: the definitions whose
``oot_randomizer_name`` is that name (copies of one check under other Hashes in other files carry the same name and
get the same item). Each chest is an actor ``Hash`` in every file the census lists for it (child and adult,
``Static``/``Dynamic``, ``Alternative``). A chest whose item changes gets the new item's actor in
``Dynamic.Drop__DropActor``, and loses its ``GetEventName`` when that override is tied to the vanilla item
(``chest_events.toml``). A chest that keeps its item is left alone.

With ``dungeon_items = "anywhere"`` a small key in a chest outside its dungeon's Banc area is a named key
(:attr:`ChestChange.named_key`): the generic actor would credit the dungeon Link stands in, or nothing in the
overworld, so the chest changes even when it already holds a small key, and ``clawshot.patch.keys`` binds a named
grant to it (:attr:`ChestChange.key_event`). ``own_dungeon`` plans have no named keys.

Chests only (D15): a shuffled location that is not a census chest (a Treasure Chest Game box, D17) stops the plan.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from clawshot.census.definitions import Definition
from clawshot.census.scan import CHEST, Location
from clawshot.generate import Seed
from clawshot.generate.fill import SMALL_KEY
from clawshot.patch.events import REMOVE, ChestEvent
from clawshot.patch.items import ItemActors
from clawshot.patch.key_targets import BY_ID, TARGETS
from clawshot.world.model import World

DROP_KEY = "Drop__DropActor"
EVENT_KEY = "GetEventName"
SUBSTITUTE_KEY = "Drop__DropActor_Substitute"


class PatchError(ValueError):
    pass


@dataclass(frozen=True)
class ChestChange:
    """One chest (one actor ``Hash``) whose item changes, or whose small key now names another dungeon."""

    location: str  # the world location (OoT Randomizer's name)
    id: int  # the actor Hash
    name: str  # the census definition's name
    files: tuple[str, ...]  # every placement file holding the Hash
    chest: str  # Gyaml
    item: str  # the logic item placed here
    old_actor: str  # Drop__DropActor before
    new_actor: str  # Drop__DropActor after
    event: ChestEvent | None  # the GetEventName override this change removes
    kept_event: ChestEvent | None = None
    named_key: str | None = None
    """A small key outside its dungeon (``anywhere`` only): the target's native ID (``key_targets``)."""
    key_event: str | None = None
    """The ``GetEventName`` binding the named grant for :attr:`named_key`, written last."""

    def __post_init__(self) -> None:
        where = f"{self.location} (chest {self.id})"
        if self.named_key is not None and self.named_key not in BY_ID:
            raise PatchError(f"{where}: {self.named_key!r} is not a small-key target")
        if self.key_event is not None:
            if self.named_key is None:
                raise PatchError(f"{where}: a key binding {self.key_event!r} needs a named key")
            if not isinstance(self.key_event, str) or not self.key_event:
                raise PatchError(f"{where}: the key binding must be an event name, not {self.key_event!r}")

    def as_dict(self) -> dict:
        out = {
            "location": self.location,
            "id": str(self.id),
            "name": self.name,
            "chest": self.chest,
            "files": list(self.files),
            "item": self.item,
            "drop_actor": [self.old_actor, self.new_actor],
        }
        if self.event is not None:
            out["removed_event"] = self.event.name
            out["story_state"] = self.event.story_state
        if self.kept_event is not None:
            out["kept_event"] = self.kept_event.name
            if self.kept_event.story_state is not None:
                out["story_state"] = self.kept_event.story_state
        if self.named_key is not None:
            out["named_key"] = self.named_key
        if self.key_event is not None:
            out["key_event"] = self.key_event
        return out


@dataclass(frozen=True)
class Plan:
    changes: list[ChestChange]
    """In world order, then by Hash."""
    unchanged: list[tuple[str, int]]
    """Shuffled locations' chests that got the item they already hold: (location, Hash)."""
    vanilla_chests: list[Definition]
    """Census chests in the world's areas that no world location names: they keep their items."""

    def files(self) -> list[str]:
        return sorted({f for change in self.changes for f in change.files})

    def for_file(self, path: str) -> list[ChestChange]:
        return [change for change in self.changes if path in change.files]

    def as_dict(self) -> dict:
        return {
            "changes": [change.as_dict() for change in self.changes],
            "unchanged": [{"location": name, "id": str(i)} for name, i in self.unchanged],
            "vanilla_chests": [{"id": str(d.id), "name": d.name, "item": d.vanilla_item} for d in self.vanilla_chests],
            "files": self.files(),
        }


@dataclass(frozen=True)
class Links:
    """World locations to census chests."""

    chests: dict[str, list[Location]]
    """Shuffled world location -> its census chests, sorted by Hash."""
    names: dict[int, str]
    """Census Hash -> the definition's name."""
    vanilla_chests: list[Definition]


def link(world: World, shuffled: Sequence[str], definitions: Sequence[Definition], census: Sequence[Location]) -> Links:
    """The census chests of each shuffled location. Raises :class:`PatchError` for a shuffled location that no
    census chest names, one whose census entry is not a chest, or a definition the census does not have."""
    by_id = {loc.id: loc for loc in census}
    named: dict[str, list[Definition]] = {}
    for d in definitions:
        name = d.oot_randomizer_name or d.name
        named.setdefault(name, []).append(d)
    problems = []
    chests: dict[str, list[Location]] = {}
    for name in shuffled:
        found = named.get(name, [])
        if not found:
            problems.append(f"{name}: no census definition has this oot_randomizer_name or remake name")
            continue
        not_chests = [f"{d.id} ({d.kind})" for d in found if d.kind != CHEST]
        if not_chests:
            problems.append(f"{name}: links to {', '.join(not_chests)}; seeds shuffle chests only (D15, D17)")
            continue
        missing = [d.id for d in found if d.id not in by_id]
        if missing:
            problems.append(f"{name}: the census of this dump has no chest {missing}")
            continue
        chests[name] = sorted((by_id[d.id] for d in found), key=lambda loc: loc.id)
    if problems:
        raise PatchError("cannot link the shuffled locations to the remake's chests:\n  " + "\n  ".join(problems))
    areas = {loc.area for loc in world.locations.values()}
    linked = {loc.id for locs in chests.values() for loc in locs}
    world_names = set(world.locations)
    vanilla = [
        d
        for d in definitions
        if d.kind == CHEST
        and d.area in areas
        and d.id not in linked
        and (d.oot_randomizer_name or d.name) not in world_names
    ]
    return Links(chests, {d.id: d.name for d in definitions}, vanilla)


def remake_vanilla(world: World, links: Links, items: ItemActors) -> dict[str, str]:
    """Each linked location's item as the remake fills it: its chests' actor, read back through ``items``. A
    location's copies must agree."""
    out = {}
    for name, chests in links.chests.items():
        actors = sorted({loc.vanilla_item for loc in chests})
        if len(actors) != 1:
            raise PatchError(f"{name}: its chests hold different actors {actors}")
        dungeon = world.regions[world.locations[name].region].dungeon
        out[name] = items.item(actors[0], dungeon, world.items)
    return out


def _named_key(seed: Seed, location: str, item: str, area: str | None) -> str | None:
    """With ``anywhere``: the target ID for ``item`` placed at ``location`` in the Banc folder ``area``, or None
    where the generic actor already credits the right dungeon. Raises :class:`PatchError` for a dungeon item that
    lies outside its dungeon with no grant to credit it from there.

    A small key is named when it lies outside its target's area, judged by the physical Banc folder, as the game
    credits it: the Spirit Temple's two hand chests stand in ``DesertColossus``, which credits no dungeon. Boss keys,
    maps and compasses have no named grant; the fill keeps them in their dungeon's regions."""
    world = seed.world
    info = world.items[item]
    if info.dungeon is None:
        return None
    target = TARGETS.get(info.dungeon) if info.type == SMALL_KEY else None
    if target is not None:
        return None if area == target.id else target.id
    if world.regions[world.locations[location].region].dungeon != info.dungeon:
        what = "small-key target" if info.type == SMALL_KEY else "named grant"
        raise PatchError(f"{location}: {item} lies outside {info.dungeon}, which has no {what}")
    return None


def make_plan(seed: Seed, links: Links, items: ItemActors, events: Mapping[str, ChestEvent]) -> Plan:
    """The changes that give every shuffled location its placed item.

    With ``anywhere`` a small key outside its dungeon's area is named (:func:`_named_key`); a chest already holding
    the generic small key still changes for it. Other shuffled kinds have no named grant: a small key there must
    lie in its own dungeon's area."""
    anywhere = seed.settings.dungeon_items == "anywhere"
    changes, unchanged = [], []
    for name in seed.shuffled:
        if name not in links.chests:
            # Other shuffled kinds are handled by make_seed's registered patch steps.
            if anywhere:
                item = seed.placements[name]
                if _named_key(seed, name, item, seed.world.locations[name].area) is not None:
                    raise PatchError(f"{name}: {item} outside its dungeon needs a named grant, which only chests have")
            continue
        item = seed.placements[name]
        actor = items.actor(item)
        for chest in links.chests[name]:
            named_key = _named_key(seed, name, item, chest.area) if anywhere else None
            if chest.vanilla_item == actor and named_key is None:
                unchanged.append((name, chest.id))
                continue
            event, kept_event = None, None
            if chest.event is not None:
                event = events.get(chest.event)
                if event is None:
                    raise PatchError(
                        f"{name} (chest {chest.id}) has GetEventName {chest.event!r}, which chest_events.toml does "
                        "not classify"
                    )
                if event.patch != REMOVE:
                    kept_event = event
                    event = None
            changes.append(
                ChestChange(
                    location=name,
                    id=chest.id,
                    name=links.names.get(chest.id, ""),
                    files=chest.files,
                    chest=chest.actor,
                    item=item,
                    old_actor=chest.vanilla_item,
                    new_actor=actor,
                    event=event,
                    kept_event=kept_event,
                    named_key=named_key,
                )
            )
    return Plan(changes, unchanged, list(links.vanilla_chests))
