"""Placed objects that show the given item (spec event-items 2.5, D5, D14 exception; plan task 10).

The moat's ``Obj_Ocarina_Time_A_01`` must stay the pickup (its AI, glow, attention and physics), so it is not replaced
by a container: it keeps its actor and pack, and only its ``ModelInfoRef`` points at a member of its own,
:func:`member_name`, holding the given item's model (the model the get pose shows, ``getitem.model_actor``). Its
native ModelInfo member is a shared path (``Item_Ocarina_Time``'s) and is never edited. An object whose model comes
from its ``$parent`` (Ruto's stone in Jabu-Jabu inherits the Temple of Time Spiritual Stone's, plan 10b) gets the
reference in its own components, which replace the parent's; the parent's file stays as it is.

Only the model, never its colour variation: a model's ``ModelVariationAnims`` in a placed object's ModelInfo crashes the
game on load (the Biggoron Sword on the moat object and on Ruto's stone, played runs 08 and 11 and the bisect arms,
BBender 2026-11-26), with or without the model's ``AnimationRef`` and variation rows; the bare model loads and looks
normal. So the object keeps its own animation (Ruto's stone turns) and takes no AnimationRef. Containers keep the
variation (D15). The ActorInfo row takes the model's fields (``MODEL_FIELDS``) and the larger heaps and radii, keeping
the object's effect users and its own ``AnimationResources``; the GameActorInfo row carries no ``ModelVariationAnims``.

The game has no size formula for a ModelInfo member, so :func:`added_member_sizes` gives the writer the new member's
entry: the pack's native ModelInfo entry plus the rounded growth, as custom items and containers are sized. This
module imports nothing from ``patch.write``, which imports it.
"""

import copy
from collections.abc import Callable, Mapping

from clawshot.formats import byml, sarc
from clawshot.patch import actor_packs
from clawshot.patch.actor_packs import actor_member
from clawshot.patch.getitem import MODEL_FIELDS
from clawshot.patch.plan import PatchError
from clawshot.patch.shops import member_path

ACTOR_INFO = "RSDB/ActorInfo.Product.111.rstbl.byml.zs"
GAME_ACTOR_INFO = "RSDB/GameActorInfo.Product.111.rstbl.byml.zs"
SUFFIX = "_Clawshot.engine__component__ModelInfo.bgyml"
VARIATION = "ModelVariationAnims"
LARGER_ROW_FIELDS = ("InstanceHeapSize", "PreActorRenderInfoHeapSize", "CalcRadius", "DisplayRadius", "LoadRadius")


def member_name(actor: str) -> str:
    return f"Component/ModelInfo/{actor}{SUFFIX}"


def _rounded(n: int) -> int:
    return (n + 31) // 32 * 32


def effective_components(pack: Mapping[str, bytes], actor: str) -> dict:
    """``actor``'s components merged down its ``$parent`` chain within ``pack`` (a child's component replaces its
    parent's)."""
    return actor_packs.resolve([pack], actor_member(actor))[0].get("Components", {})


def pack_transform(actor: str, model_pack: Mapping[str, bytes], model: str) -> Callable[[bytes], bytes]:
    """``actor``'s pack (decompressed) showing ``model``'s model (``model_pack``: its pack's members)."""
    source = actor_packs.closure([model_pack], model)
    info_ref = member_path(source.components["ModelInfoRef"])
    info = {key: value for key, value in actor_packs.resolve_node([model_pack], info_ref).items() if key != VARIATION}

    def transform(data: bytes) -> bytes:
        pack = sarc.read(data)
        param = actor_member(actor)
        if param not in pack:
            raise PatchError(f"{actor}: the pack has no {param}")
        document = byml.load(pack[param])
        components = document.root.setdefault("Components", {})
        effective = effective_components(pack, actor)
        if "ModelInfoRef" not in effective or member_name(actor) in pack:
            raise PatchError(f"{actor}: no native ModelInfoRef, or its own member is there already")
        components["ModelInfoRef"] = "?" + member_name(actor)
        pack[member_name(actor)] = byml.write(info)
        pack[param] = byml.dump(document)
        out = sarc.write(pack)
        if sarc.read(out) != pack:
            raise PatchError(f"{actor}: the changed pack does not read back")
        return out

    return transform


def added_member_sizes(before: bytes, after: bytes) -> dict[str, tuple[str, int]]:
    """For a pack :func:`pack_transform` changed: its own ModelInfo member -> (the native ModelInfo member whose size
    entry it starts from, its rounded growth). Empty for any other pack."""
    old, new = sarc.read(before), sarc.read(after)
    out = {}
    for name in sorted(set(new) - set(old)):
        if not name.endswith(SUFFIX):
            continue
        actor = name.removeprefix("Component/ModelInfo/").removesuffix(SUFFIX)
        donor = member_path(effective_components(old, actor)["ModelInfoRef"])
        out[name] = (donor, max(0, _rounded(len(new[name])) - _rounded(len(old[donor]))))
    return out


def _rows(data: bytes, path: str) -> tuple[byml.Document, dict[str, dict]]:
    document = byml.load(data)
    if not isinstance(document.root, list):
        raise PatchError(f"{path}: not a row table")
    return document, {row["__RowId"]: row for row in document.root}


def _dump(document: byml.Document, path: str) -> bytes:
    out = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(out))) is not None:
        raise PatchError(f"{path}: the changed table does not read back: {difference}")
    return out


def actor_info_transform(models: Mapping[str, str]) -> Callable[[bytes], bytes]:
    """ActorInfo with each placed actor's row (``models``: actor -> model actor) showing its model."""

    def transform(data: bytes) -> bytes:
        document, rows = _rows(data, ACTOR_INFO)
        for actor, model in sorted(models.items()):
            if actor not in rows or model not in rows:
                raise PatchError(f"{ACTOR_INFO}: no row for {actor} or {model}")
            row, source = rows[actor], rows[model]
            for field in MODEL_FIELDS:
                if field in source:
                    row[field] = copy.deepcopy(source[field])
                else:
                    row.pop(field, None)
            for field in LARGER_ROW_FIELDS:
                if field in row and field in source:
                    row[field] = type(row[field])(max(row[field], source[field]))
        return _dump(document, ACTOR_INFO)

    return transform


def game_actor_info_transform(models: Mapping[str, str]) -> Callable[[bytes], bytes]:
    """GameActorInfo with each placed actor's row carrying no ``ModelVariationAnims`` (the model's would crash)."""

    def transform(data: bytes) -> bytes:
        document, rows = _rows(data, GAME_ACTOR_INFO)
        for actor, model in sorted(models.items()):
            if actor not in rows or model not in rows:
                raise PatchError(f"{GAME_ACTOR_INFO}: no row for {actor} or {model}")
            rows[actor].pop(VARIATION, None)
        return _dump(document, GAME_ACTOR_INFO)

    return transform
