"""Native boss-heart pickups, retaining the room's spawn and persistence wiring.

BossHeart destinations accept only this explicit native palette, not inventory-only
Item_* actors or the known-crashing Obj_Arrow_Fire. See r7-drops.md for the eight
Logic_Create gates and the pending King Dodongo Save/Continue check.
"""

from collections.abc import Mapping, Sequence
from dataclasses import replace

from clawshot.census.definitions import Definition
from clawshot.census.scan import HEART_CONTAINER, Location
from clawshot.formats import byml
from clawshot.generate import Settings
from clawshot.generate.fill import shuffled_locations
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges
from clawshot.world.model import World

SHUFFLE = "BossHeart"
HEART = "Obj_Heart_Container"
# Logical grants, not chest actors: Rupees (20) uses a native Obj_ pickup here.
NATIVE_ITEMS = {
    "Heart Container": HEART,
    "Piece of Heart": "Obj_Heart_Piece",
    "Deku Shield": "Obj_Shield_Deku",
    "Hylian Shield": "Obj_Shield_Hylian",
    "Rupees (20)": "Obj_Rupee_Red",
}


def changes(placements: Mapping[int, str], census: Sequence[Location]) -> FileChanges:
    """Replace saved heart actors by Hash on every copy, never their script groups."""
    locations = {loc.id: loc for loc in census}
    files: dict[str, dict[int, str]] = {}
    for actor_id, pickup in placements.items():
        loc = locations.get(actor_id)
        if loc is None or loc.kind != HEART_CONTAINER or loc.actor != HEART or not loc.has_save_flag:
            raise PatchError(f"{actor_id}: not a saved boss Heart Container")
        if pickup not in NATIVE_ITEMS.values():
            raise PatchError(f"{actor_id}: {pickup!r} is not a supported native boss-heart pickup")
        for path in loc.files:
            files.setdefault(path, {})[actor_id] = pickup
    return {path: _transform(path, targets) for path, targets in sorted(files.items())}


def _transform(path: str, targets: Mapping[int, str]):
    def transform(data: bytes) -> bytes:
        document = byml.load(data)
        tree = document.root
        edits = []
        for actor_id, pickup in targets.items():
            found = [a for a in tree.get("Actors", []) if a.get("Hash") == actor_id]
            if len(found) != 1 or found[0].get("Gyaml") != HEART:
                raise PatchError(f"{path}: stale boss heart {actor_id}: {found!r}")
            references = [
                ref
                for group in tree.get("AiGroups", [])
                for ref in group.get("References", [])
                if ref.get("Reference") == actor_id
            ]
            if len(references) != 1 or not references[0].get("Id", "").startswith(HEART + "_"):
                raise PatchError(f"{path}: heart {actor_id} lost its native logic binding: {references!r}")
            for key in ("SimultaneousGroups", "FarDeleteGroups"):
                memberships = [group for group in tree.get(key, []) if actor_id in group]
                if len(memberships) != 1 or memberships[0].count(actor_id) != 1:
                    raise PatchError(f"{path}: heart {actor_id} has invalid {key}: {memberships!r}")
            edits.append((found[0], pickup))
        for actor, pickup in edits:
            actor["Gyaml"] = pickup
        out = byml.dump(document)
        if byml.difference(tree, byml.read(out)) is not None:
            raise PatchError(f"{path}: changed boss hearts do not read back")
        return out

    return transform


def seed_setup(
    world: World,
    settings: Settings,
    census: Sequence[Location],
    definitions: Sequence[Definition],
    vanilla: Mapping[str, str],
):
    """Restrict BossHeart destinations to the native palette (``Settings.location_type_items``), intersecting a
    palette already given. The fill fills them from that palette first; no other item can reach them."""
    shuffled = shuffled_locations(world, settings)
    checks = [name for name in shuffled if world.locations[name].type == SHUFFLE]
    locations = {loc.id: loc for loc in census}
    linked = {}
    for name in checks:
        found = [d for d in definitions if d.kind == HEART_CONTAINER and (d.oot_randomizer_name or d.name) == name]
        if len(found) != 1 or found[0].id not in locations:
            raise PatchError(f"{name}: expected one census boss heart")
        loc = locations[found[0].id]
        if loc.kind != HEART_CONTAINER or loc.actor != HEART or not loc.has_save_flag:
            raise PatchError(f"{name}: not a saved native boss heart")
        linked[name] = loc.id
    palettes = dict(settings.location_type_items)
    palette = [item for item in NATIVE_ITEMS if item in palettes.get(SHUFFLE, NATIVE_ITEMS)]
    settings = replace(settings, location_type_items={**palettes, SHUFFLE: tuple(palette)})

    def step(placements: Mapping[str, str]) -> FileChanges:
        targets = {}
        for name, actor_id in linked.items():
            item = placements[name]
            if item not in NATIVE_ITEMS:
                raise PatchError(f"{name}: {item!r} has no native boss-heart pickup")
            if (pickup := NATIVE_ITEMS[item]) != HEART:
                targets[actor_id] = pickup
        return changes(targets, census)

    return settings, step
