"""Saved heart-piece floor checks with D27's native pickup palette (default off).

Anchors are map markers, not checks. Preserve the linked pickup's Hash and every
age/Alternative copy. Keys and scripted/renewable pickups do not share this contract;
see plans/rounds/r8-freestanding.md for the full anchor and native-pack audit.
"""

from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any

from clawshot.census.definitions import Definition
from clawshot.census.scan import FREESTANDING, Location
from clawshot.formats import byml
from clawshot.generate import Settings
from clawshot.generate.fill import shuffled_locations
from clawshot.patch.drops import NATIVE_ITEMS
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges
from clawshot.world.model import World

SHUFFLE = "Freestanding"
HEART_PIECES = frozenset({"Obj_Heart_Piece", "Obj_GerudoValley_Heart_Piece"})


def restrict_spec(spec: Mapping[str, Any], definitions: Sequence[Definition]) -> dict[str, Any]:
    """Separate the supported Collectable hearts from untranslated N64 floor rows.

    Retain existing sourced access rules and exclusions. Small keys stay Collectable;
    ordinary rupee/refill rows lack physical remake links and must remain vanilla.
    """
    hearts = {
        d.oot_randomizer_name or d.name
        for d in definitions
        if d.kind == FREESTANDING and d.vanilla_item in HEART_PIECES
    }
    locations = {}
    for name, info in spec["locations"].items():
        if name in hearts and info.get("type") == "Collectable" and info.get("vanilla") == "Piece of Heart":
            info = {**info, "type": SHUFFLE}
        elif info.get("type") == SHUFFLE and not info.get("keep_vanilla"):
            info = {
                **info,
                "keep_vanilla": "freestanding shuffle: no verified physical remake pickup link (section 36)",
            }
        locations[name] = info
    return {**spec, "locations": locations}


def _saved_heart(loc: Location) -> bool:
    return loc.kind == FREESTANDING and loc.actor in HEART_PIECES and loc.has_save_flag and bool(loc.files)


def changes(placements: Mapping[int, str], census: Sequence[Location]) -> FileChanges:
    """Replace only Gyaml on all copies of saved, ungrouped heart-piece pickups."""
    locations = {loc.id: loc for loc in census}
    files: dict[str, dict[int, tuple[str, str]]] = {}
    for actor_id, pickup in placements.items():
        loc = locations.get(actor_id)
        if loc is None or not _saved_heart(loc):
            raise PatchError(f"{actor_id}: not a saved freestanding heart piece")
        if pickup not in NATIVE_ITEMS.values():
            raise PatchError(f"{actor_id}: {pickup!r} is not a supported native floor pickup")
        for path in loc.files:
            files.setdefault(path, {})[actor_id] = (loc.actor, pickup)
    return {path: _transform(path, targets) for path, targets in sorted(files.items())}


def _transform(path: str, targets: Mapping[int, tuple[str, str]]):
    def transform(data: bytes) -> bytes:
        document = byml.load(data)
        tree = document.root
        edits = []
        for actor_id, (original, pickup) in targets.items():
            found = [a for a in tree.get("Actors", []) if a.get("Hash") == actor_id]
            if len(found) != 1 or found[0].get("Gyaml") != original:
                raise PatchError(f"{path}: stale freestanding heart {actor_id}: {found!r}")
            if found[0].get("Phive", {}).get("Placement", {}).get("ID") != actor_id:
                raise PatchError(f"{path}: heart {actor_id} lost its placement identity: {found[0]!r}")
            references = [
                ref
                for group in tree.get("AiGroups", [])
                for ref in group.get("References", [])
                if ref.get("Reference") == actor_id
            ]
            if references:
                raise PatchError(f"{path}: heart {actor_id} gained an unaudited script binding: {references!r}")
            edits.append((found[0], pickup))
        for actor, pickup in edits:
            actor["Gyaml"] = pickup
        out = byml.dump(document)
        if byml.difference(tree, byml.read(out)) is not None:
            raise PatchError(f"{path}: changed freestanding pickups do not read back")
        return out

    return transform


def seed_setup(
    world: World,
    settings: Settings,
    census: Sequence[Location],
    definitions: Sequence[Definition],
    vanilla: Mapping[str, str],
):
    """Link selected hearts and intersect native-only destinations with prior holds."""
    shuffled = shuffled_locations(world, settings)
    checks = [name for name in shuffled if world.locations[name].type == SHUFFLE]
    locations = {loc.id: loc for loc in census}
    linked = {}
    for name in checks:
        found = [d for d in definitions if d.kind == FREESTANDING and (d.oot_randomizer_name or d.name) == name]
        if len(found) != 1 or found[0].id not in locations:
            raise PatchError(f"{name}: expected one census freestanding heart piece")
        loc = locations[found[0].id]
        if not _saved_heart(loc) or loc.area != world.locations[name].area:
            raise PatchError(f"{name}: not a saved native heart piece in its world area")
        linked[name] = loc
    held = dict(settings.item_location_types)
    other_types = tuple(sorted({loc.type for loc in world.locations.values()} - {SHUFFLE}))
    pool = {vanilla.get(name, world.locations[name].vanilla) for name in shuffled}
    for item in sorted(pool):
        if item not in NATIVE_ITEMS:
            held[item] = tuple(t for t in held.get(item, other_types) if t != SHUFFLE)
    settings = replace(settings, item_location_types=held)

    def step(placements: Mapping[str, str]) -> FileChanges:
        targets = {}
        for name, loc in linked.items():
            item = placements[name]
            if item not in NATIVE_ITEMS:
                raise PatchError(f"{name}: {item!r} has no supported native floor pickup")
            # An unmoved piece retains its native GV variant, physics and AI too.
            if item != "Piece of Heart":
                targets[loc.id] = NATIVE_ITEMS[item]
        return changes(targets, census)

    return settings, step
