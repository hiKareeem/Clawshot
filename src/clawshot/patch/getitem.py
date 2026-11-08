"""Explicit native get-display experiments; no inventory or chest-admission policy changes.

Ocarinas lack the PouchContent event performer used by chest display actions. Songs
have that performer but use a rupee mesh. These transforms borrow native resources
from the player's dump. They are not enabled automatically before visual review.
"""

import copy
from collections.abc import Iterable
from functools import partial
from pathlib import Path

from clawshot.formats import byml, sarc, zsdic
from clawshot.patch.plan import PatchError
from clawshot.patch.shops import actor_path, member_path, resolve_member

ACTOR_INFO = "RSDB/ActorInfo.Product.111.rstbl.byml.zs"
FAIRY = "Item_Ocarina_Fairy"
TIME = "Item_Ocarina_Time"
SONG_MODELS = {
    "Item_Melody_ZeldaLullaby": FAIRY,
    "Item_Melody_EponaSong": FAIRY,
    "Item_Melody_SariaSong": FAIRY,
    "Item_Melody_SunSong": FAIRY,
    "Item_Melody_TimeSong": FAIRY,
    "Item_Melody_StormSong": FAIRY,
    "Item_Melody_ForestMinuet": TIME,
    "Item_Melody_FireBolero": TIME,
    "Item_Melody_WaterSerenade": TIME,
    "Item_Melody_SpiritRequiem": TIME,
    "Item_Melody_ShadowNocturne": TIME,
    "Item_Melody_LightPrelude": TIME,
}
OCARINAS = (FAIRY, TIME)
PERFORMER = "Component/EventPerformerParam/PouchContent.engine__component__EventPerformerParam.bgyml"
COMMON = "?Component/EventPerformerParam/Common.engine__component__EventPerformerParam.bgyml"
MODEL_FIELDS = ("FmdbName", "ModelProjectName", "ModelAabbMin", "ModelAabbMax")


def pack_path(actor: str) -> str:
    return f"Pack/Actor/{actor}.pack.zs"


def _dump(document: byml.Document) -> bytes:
    result = byml.dump(document)
    if difference := byml.difference(document.root, byml.read(result)):
        raise PatchError(f"get-display BYML failed read-back: {difference}")
    return result


def patch_pack(data: bytes, *, actor: str, performer: bytes) -> bytes:
    """Change only a song's model identity or an ocarina's event-performer reference."""
    if actor not in SONG_MODELS and actor not in OCARINAS:
        raise PatchError(f"no get-display correction for {actor}")
    pack = sarc.read(data)
    root_member = member_path(actor_path(actor))
    document = byml.load(pack[root_member])
    components = resolve_member(pack, actor_path(actor))["Components"]
    model_member = member_path(components["ModelInfoRef"])
    model = byml.load(pack[model_member])
    expected = "Obj_Rupee" if actor in SONG_MODELS else actor
    if (model.root.get("FmdbName"), model.root.get("ModelProjectName")) != (expected, expected):
        raise PatchError(f"{actor}: stale native model: {model.root}")
    if actor in SONG_MODELS:
        if components.get("EventPerformerRef") != "?" + PERFORMER:
            raise PatchError(f"{actor}: song no longer uses the pouch performer")
        for field in ("FmdbName", "ModelProjectName"):
            model.root[field] = SONG_MODELS[actor]
        pack[model_member] = _dump(model)
    else:
        if components.get("EventPerformerRef") != COMMON:
            raise PatchError(f"{actor}: ocarina no longer uses the common performer")
        native = byml.read(performer)
        if native != {"EventUniqueAin": "Work/AI/Root/Event/PouchContent.event.root.ain", "UseEventUniqueAin": True}:
            raise PatchError(f"unexpected native pouch performer: {native}")
        document.root["Components"]["EventPerformerRef"] = "?" + PERFORMER
        pack[root_member] = _dump(document)
        pack[PERFORMER] = performer
    result = sarc.write(pack)
    if sarc.read(result) != pack:
        raise PatchError(f"{actor}: get-display pack failed read-back")
    return result


def patch_actor_info(data: bytes, *, actors: tuple[str, ...]) -> bytes:
    """Keep cached models consistent and reserve conservative native display heap budgets.

    Native instance budgets include more than model bytes. Adding the entire donor
    budget avoids assuming an unverified exact component/mesh heap delta. This is
    an experimental upper reservation, not a measured minimal runtime allocation.
    """
    document = byml.load(data)
    rows = {row["__RowId"]: row for row in document.root}
    for actor in actors:
        if actor not in SONG_MODELS and actor not in OCARINAS:
            raise PatchError(f"no get-display correction for {actor}")
        row = rows[actor]
        expected = "Obj_Rupee" if actor in SONG_MODELS else actor
        if (row.get("FmdbName"), row.get("ModelProjectName")) != (expected, expected):
            raise PatchError(f"{actor}: stale ActorInfo model: {row}")
    # Capture unmodified donors before changing either ocarina's reservation.
    donors = {name: copy.deepcopy(rows[name]) for name in (*OCARINAS, "Item_Boomerang")}
    for actor in actors:
        row = rows[actor]
        donor = donors[SONG_MODELS.get(actor, "Item_Boomerang")]
        if actor in SONG_MODELS:
            if (donor.get("FmdbName"), donor.get("ModelProjectName")) != (SONG_MODELS[actor],) * 2:
                raise PatchError(f"{actor}: native model donor changed: {donor}")
            for field in MODEL_FIELDS:
                row[field] = copy.deepcopy(donor[field])
            field = "PreActorRenderInfoHeapSize"
            row[field] = type(row[field])(max(row[field], donor[field]))
        field = "InstanceHeapSize"
        row[field] = type(row[field])(int(row[field]) + int(donor[field]))
    return _dump(document)


def changes(romfs: str | Path, actors: Iterable[str]) -> dict:
    """FileChanges for explicit actor identities, suitable for the common overlay writer.

    Call only for intended chest actors. This does not certify a grant or release
    a gift-only actor from the sourced allowlist.
    """
    actors = tuple(sorted(set(actors)))
    if not actors:
        return {}
    unknown = set(actors) - SONG_MODELS.keys() - set(OCARINAS)
    if unknown:
        raise PatchError(f"no get-display correction for {sorted(unknown)}")
    romfs = Path(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    donor = sarc.read(
        dictionaries.decompress(pack_path("Item_Boomerang"), (romfs / pack_path("Item_Boomerang")).read_bytes())
    )
    for model in {SONG_MODELS.get(actor, actor) for actor in actors}:
        if not (romfs / f"Model/{model}.{model}.bfres.zs").is_file():
            raise PatchError(f"missing native model {model}")
    return {
        **{pack_path(actor): partial(patch_pack, actor=actor, performer=donor[PERFORMER]) for actor in actors},
        ACTOR_INFO: partial(patch_actor_info, actors=actors),
    }


def member_growth(before: bytes, after: bytes) -> dict[str, int]:
    """Retain original parsed overhead for same-shape model/ref string substitutions.

    New embedded PouchContent components are byte-identical native resources with
    their own existing allocation, not new resource identities or expanded trees.
    """
    original, changed = sarc.read(before), sarc.read(after)
    growth = {}
    for actor in (*OCARINAS, *SONG_MODELS):
        member = member_path(actor_path(actor))
        if member not in original:
            continue
        components = resolve_member(original, actor_path(actor))["Components"]
        model_member = member_path(components["ModelInfoRef"])
        editable = (member,) if actor in OCARINAS else (model_member,)
        for name in editable:
            if changed.get(name) == original[name]:
                continue
            if name not in changed:
                raise PatchError(f"{name}: missing get-display member")
            old, new = byml.read(original[name]), byml.read(changed[name])
            if actor in OCARINAS:
                if (
                    old["Components"].get("EventPerformerRef") != COMMON
                    or new["Components"].get("EventPerformerRef") != "?" + PERFORMER
                ):
                    raise PatchError(f"{name}: unsupported performer substitution")
                new["Components"]["EventPerformerRef"] = old["Components"]["EventPerformerRef"]
            else:
                for field in ("FmdbName", "ModelProjectName"):
                    if old.get(field) != "Obj_Rupee" or new.get(field) != SONG_MODELS[actor]:
                        raise PatchError(f"{name}: unsupported model substitution")
                    new[field] = old[field]
            if not byml.same(old, new):
                raise PatchError(f"{name}: structural growth needs a measured allocation")
            delta = ((len(changed[name]) + 31) // 32 - (len(original[name]) + 31) // 32) * 32
            if delta > 0:
                growth[name] = delta
    return growth
