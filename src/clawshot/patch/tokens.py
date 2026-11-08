"""Gold Skulltula drop experiments, not certified tokensanity.

The enemy passes its permanent Hash to Obj_Token_Gold as GoldTokenGmdHash. That
pickup's OneShotGoldTokenDeadAfter callback is absent on ordinary pickups. Changing
Drop__DropActor is expressible in data, but only a game/save check can establish
whether a replacement still retires the enemy. Do not use experiments as seed checks.
"""

from collections.abc import Mapping, Sequence

from clawshot.census.scan import GOLD_SKULLTULA, Location
from clawshot.formats import byml, sarc
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


PACK_PATH = f"Pack/Actor/{TOKEN}.pack.zs"
POUCH_MEMBER = "Component/PouchContentParam/Obj_Token_Gold.game__component__PouchContentParam.bgyml"
AI_INFO_MEMBER = "AI/AIInfo/Item_Token_Gold.engine__actor__AIInfo.bgyml"
TOKEN_AI_MEMBER = "AI/Item_Token_Gold.root.ainb"
NATIVE_GRANT = "Work/Actor/Item_Token_Gold.engine__actor__ActorParam.gyml"
EXPERIMENT_GRANT = "Work/Actor/Item_Boomerang.engine__actor__ActorParam.gyml"


def grant_experiment() -> FileChanges:
    """Global native-token -> Boomerang grant experiment, NEVER a seed patch.

    Every token using this pack is affected. Retain its AI/callback, enemy hash
    overwrite, model and pickup rules. GetType/SpecialDeal stay token-native:
    whether they override PouchActor or increment tokens needs the game check.
    The component must not grow; no generic nested allocation formula is assumed.
    """

    def transform(data: bytes) -> bytes:
        pack = sarc.read(data)
        if any(member not in pack for member in (POUCH_MEMBER, AI_INFO_MEMBER, TOKEN_AI_MEMBER)):
            raise PatchError("native token experiment: missing pouch or callback AI")
        if byml.read(pack[AI_INFO_MEMBER]).get("RootAIRef") != "Work/AI/Root/Item_Token_Gold.root.ain":
            raise PatchError("native token experiment: stale native AI root")
        document = byml.load(pack[POUCH_MEMBER])
        if document.root.get("PouchActor") != NATIVE_GRANT:
            raise PatchError(f"native token experiment: stale pouch identity {document.root!r}")
        document.root["PouchActor"] = EXPERIMENT_GRANT
        changed = byml.dump(document)
        if len(changed) > len(pack[POUCH_MEMBER]):
            raise PatchError("native token experiment: pouch component grew without a size formula")
        if byml.difference(document.root, byml.read(changed)) is not None:
            raise PatchError("native token experiment: pouch does not read back")
        pack[POUCH_MEMBER] = changed
        out = sarc.write(pack)
        if sarc.read(out) != pack:
            raise PatchError("native token experiment: pack does not read back")
        return out

    return {PACK_PATH: transform}
