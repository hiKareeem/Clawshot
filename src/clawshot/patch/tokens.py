"""Gold Skulltula drop experiments, not certified tokensanity.

The enemy passes its permanent Hash to Obj_Token_Gold as GoldTokenGmdHash. That
pickup's OneShotGoldTokenDeadAfter callback is absent on ordinary pickups. Changing
Drop__DropActor is expressible in data, but only a game/save check can establish
whether a replacement still retires the enemy. Do not use experiments as seed checks.
"""

from collections.abc import Mapping, Sequence

from clawshot.census.scan import GOLD_SKULLTULA, Location
from clawshot.formats import byml
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

ENEMY = "Enemy_Skulltula_Gold"
TOKEN = "Obj_Token_Gold"
DROP = "Drop__DropActor"
# Actual pickup actors, unlike Item_* inventory-only actors. Shields/red rupee have
# worked as freestanding pickups (03-game-data.md sections 10/11), not token drops.
PICKUPS = frozenset({TOKEN, "Obj_Rupee_Red", "Obj_Shield_Deku", "Obj_Shield_Hylian"})


def changes(placements: Mapping[int, str], census: Sequence[Location]) -> FileChanges:
    """Experimental per-enemy drop overrides, on every age/Alternative copy."""
    locations = {loc.id: loc for loc in census}
    files: dict[str, dict[int, str]] = {}
    for actor_id, item in placements.items():
        loc = locations.get(actor_id)
        if loc is None or loc.kind != GOLD_SKULLTULA or loc.actor != ENEMY or not loc.has_save_flag:
            raise PatchError(f"{actor_id}: not a saved Gold Skulltula census location")
        if item not in PICKUPS:
            raise PatchError(f"{actor_id}: {item!r} is not a supported pickup experiment")
        for path in loc.files:
            files.setdefault(path, {})[actor_id] = item
    return {path: _transform(path, targets) for path, targets in sorted(files.items())}


def _transform(path: str, targets: Mapping[int, str]):
    def transform(data: bytes) -> bytes:
        document = byml.load(data)
        edits = []
        for actor_id, item in targets.items():
            found = [a for a in document.root.get("Actors", []) if a.get("Hash") == actor_id]
            if len(found) != 1:
                raise PatchError(f"{path}: expected one actor Hash {actor_id}, found {len(found)}")
            actor = found[0]
            dynamic = actor.get("Dynamic") or {}
            if actor.get("Gyaml") != ENEMY or dynamic.get(DROP, "") not in ("", TOKEN):
                raise PatchError(f"{path}: stale token enemy {actor_id}: {actor!r}")
            edits.append((actor, item))
        for actor, item in edits:
            actor.setdefault("Dynamic", {})[DROP] = item
        out = byml.dump(document)
        if byml.difference(document.root, byml.read(out)) is not None:
            raise PatchError(f"{path}: changed token placement does not read back")
        return out

    return transform
