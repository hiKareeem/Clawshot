"""Container actors: model-only event props, one per model a seed needs (spec event-items 2.4, D14-D16; plan task 7).

An event shows the given item through a container in place of its native prop: ``Dm_Item_Clawshot_<model actor>``,
built from a native event prop (:data:`DONOR`) and the model actor (:func:`clawshot.patch.getitem.model_actor`, the
model the get pose shows). The container keeps the donor's structure (its dummy AS, event performer, empty bind
parameter, physics) and takes from the model actor only what is visual:

- its model, written to a member of the container's own (:func:`model_member`), so no shared component path changes
  (the Link's-ocarina pitfall: component files are cached by path);
- its ``ModelVariationAnims`` (in that member and the GameActorInfo row) together with a reference to its own
  ``AnimationParam``, where the material animation lives (D15: the demo crashed with the first and not the second);
- its ``ELink`` when it has one, else none (the donor's names the ocarina's effects);
- its animation set (``ASRef``, ``ASInfoRef``) when it has one of its own, else the donor's dummy: a scene that plays
  an item animation on its prop (``Dm_TimeTemple_0130`` plays ``Rotate_GetDemo``) then plays it on the container,
  and a scene that plays none shows it still (D16 revised after pilot arm B, BBender 2026-11-26).

A song has a container of its own (:func:`container_model`), built from its pack as the song step shows it
(``songs.patch_song_pack``: the ocarina's model, the song's effect user, the common animation set), so the scene shows
the ocarina with the song's effect, as the song's get pose does (PR #41).

Never: a pouch, pickup, game parameter table, item name or AI component, so an event cannot give or collect the
container. Native members are copied byte-identically (``NewFile.copied``); the writer sizes the two new ones.
"""

import bisect
import copy
from collections.abc import Callable, Iterable, Mapping, Sequence
from functools import partial
from pathlib import Path

from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.patch import actor_packs, getitem, songs
from clawshot.patch.actor_packs import actor_member
from clawshot.patch.getitem import MODEL_FIELDS, pack_path
from clawshot.patch.plan import PatchError
from clawshot.patch.shops import member_path
from clawshot.patch.write import NewFile

DONOR = "Dm_Item_Ocarina_Fairy"  # Saria's presented ocarina: a timeline prop with an empty bind parameter
PREFIX = "Dm_Item_Clawshot_"
ACTOR_INFO = "RSDB/ActorInfo.Product.111.rstbl.byml.zs"
GAME_ACTOR_INFO = "RSDB/GameActorInfo.Product.111.rstbl.byml.zs"
VISUAL_ROW_FIELDS = (*MODEL_FIELDS, "ModelVariationFmabName", "AnimationResources")
LARGER_ROW_FIELDS = ("InstanceHeapSize", "PreActorRenderInfoHeapSize", "CalcRadius", "DisplayRadius", "LoadRadius")
NEVER = ("PouchContentRef", "ActorNameRef", "GameParameterTableRef", "AIRef", "CaptureRef", "SLinkRef")
DUMMY_SETS = ("?AS/DemoDummy.root.asb", "?AS/Dummy.root.asb")  # an animation set that plays nothing


def is_song_container(name: str) -> bool:
    """Whether ``name`` is a song's own container (D17)."""
    return name.startswith(PREFIX) and name.removeprefix(PREFIX) in getitem.SONG_MODELS


def container_model(actor: str) -> str:
    """The actor a container is built from for an item ``actor``: a song itself (its pack, as the song step shows it,
    holds the ocarina's model and the song's effect), any other item the model its get pose shows
    (:func:`getitem.model_actor`)."""
    return actor if actor in getitem.SONG_MODELS else getitem.model_actor(actor)


def container_name(model: str) -> str:
    return PREFIX + model


def model_member(container: str) -> str:
    return f"Component/ModelInfo/{container}.engine__component__ModelInfo.bgyml"


def build_pack(
    donor: Mapping[str, bytes],
    model_pack: Mapping[str, bytes],
    model: str,
    *,
    donor_entry: int | None = None,
    elink_user: str | None = None,
) -> NewFile:
    """The container pack for ``model`` from the decompressed packs' members (``donor``: :data:`DONOR`'s).
    ``donor_entry``, the size entry of the donor's ActorParam, lets the container's ActorParam grow by what the
    game's formula needs when that is more than its rounded byte growth (more components than the donor's).
    ``elink_user`` (a song's event user, D18) names the container's effect user through an ELink member of its own,
    sized from the effect donor's."""
    name = container_name(model)
    if actor_member(DONOR) not in donor:
        raise PatchError(f"{DONOR}: the pack has no {actor_member(DONOR)}")
    source = actor_packs.closure([model_pack], model)
    document = byml.load(donor[actor_member(DONOR)])
    components = document.root["Components"]
    native_info = member_path(source.components["ModelInfoRef"])
    info = actor_packs.resolve_node([model_pack], native_info)
    components["ModelInfoRef"] = "?" + model_member(name)
    for key in ("AnimationRef", "ELinkRef"):
        if key in source.components:
            components[key] = source.components[key]
        else:
            components.pop(key, None)
    if source.components.get("ASRef", DUMMY_SETS[0]) not in DUMMY_SETS:
        for key in ("ASRef", "ASInfoRef", "XLinkRef"):
            if key in source.components:
                components[key] = source.components[key]
    for key in NEVER:
        components.pop(key, None)
    link = songs.elink_member(name)
    if elink_user is not None:
        components["ELinkRef"] = "?" + link
    new = {actor_member(name): byml.dump(document), model_member(name): byml.write(info)}
    if elink_user is not None:
        new[link] = byml.write({"UserName": elink_user})
    packed = actor_packs.closure([new, donor, model_pack], name)
    copied = {}
    for member in packed.members:
        if member in new:
            continue
        origin, other = (DONOR, model) if member in donor else (model, DONOR)
        native = donor if origin == DONOR else model_pack
        alternative = model_pack if origin == DONOR else donor
        if member in alternative and alternative[member] != native[member]:
            raise PatchError(f"{name}: {member} differs between {origin} and {other}")
        copied[member] = pack_path(origin)
    data = sarc.write(packed.members)
    if sarc.read(data) != packed.members:
        raise PatchError(f"{name}: the container pack does not read back")
    # The game has no size formula for a ModelInfo member: both new members are sized from their native donor member
    # plus their rounded growth, as custom items are.
    natives = {actor_member(name): (actor_member(DONOR), donor), model_member(name): (native_info, model_pack)}
    sized = {
        member: (origin, max(0, _rounded(len(new[member])) - _rounded(len(pack[origin]))))
        for member, (origin, pack) in natives.items()
    }
    if elink_user is not None:  # the donor's member: UserName Obj_Heart_Container
        native_link = songs.elink_member(songs.EFFECT_DONOR)
        native_size = _rounded(len(byml.write({"UserName": songs.EFFECT_DONOR})))
        sized[link] = (native_link, max(0, _rounded(len(new[link])) - native_size))
    if donor_entry is not None:
        param = actor_member(name)
        need = rstb.required_size(param, len(new[param]), len(components))
        sized[param] = (sized[param][0], max(sized[param][1], need - donor_entry))
    return NewFile(data, members=sized, copied=copied)


def _rounded(n: int) -> int:
    return (n + 31) // 32 * 32


def _rows(data: bytes, path: str) -> tuple[byml.Document, dict[str, dict]]:
    document = byml.load(data)
    if not isinstance(document.root, list):
        raise PatchError(f"{path}: not a row table")
    return document, {row["__RowId"]: row for row in document.root}


def _insert(document: byml.Document, path: str, new: Sequence[dict]) -> bytes:
    rows = document.root
    for row in sorted(new, key=lambda r: r["__RowId"].encode("utf-8")):
        keys = [r["__RowId"].encode("utf-8") for r in rows]
        if row["__RowId"].encode("utf-8") in keys:
            raise PatchError(f"{path}: row {row['__RowId']} already exists")
        rows.insert(bisect.bisect_left(keys, row["__RowId"].encode("utf-8")), row)
    out = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(out))) is not None:
        raise PatchError(f"{path}: the changed table does not read back: {difference}")
    return out


def actor_info_transform(models: Sequence[str]) -> Callable[[bytes], bytes]:
    """ActorInfo gains a row per container: the donor's, with the model actor's visual fields and the larger of the
    two heaps and radii; no effects user unless the model actor has one, no item identity (``ActorName``)."""

    def transform(data: bytes) -> bytes:
        document, rows = _rows(data, ACTOR_INFO)
        new = []
        for model in sorted(set(models)):
            if DONOR not in rows or model not in rows:
                raise PatchError(f"{ACTOR_INFO}: no row for {DONOR} or {model}")
            donor, source = rows[DONOR], rows[model]
            if model in getitem.SONG_MODELS and "ELinkUserName" not in source:  # the song step has not run yet
                source = {**source, **songs.shown_row(source, rows[getitem.SONG_MODELS[model]], model)}
            row = copy.deepcopy(donor)
            row["__RowId"] = container_name(model)
            for field in VISUAL_ROW_FIELDS:
                if field in source:
                    row[field] = copy.deepcopy(source[field])
                else:
                    row.pop(field, None)
            for field in LARGER_ROW_FIELDS:
                if field in donor and field in source:
                    row[field] = type(donor[field])(max(donor[field], source[field]))
            if model in getitem.SONG_MODELS:  # D18: the song's event user
                row["ELinkUserName"] = songs.event_user_name(model)
            elif "ELinkUserName" in source:
                row["ELinkUserName"] = source["ELinkUserName"]
            else:
                row.pop("ELinkUserName", None)
            new.append(row)
        return _insert(document, ACTOR_INFO, new)

    return transform


def game_actor_info_transform(models: Sequence[str]) -> Callable[[bytes], bytes]:
    """GameActorInfo gains a row per container: the donor's, with the model actor's ``ModelVariationAnims``."""

    def transform(data: bytes) -> bytes:
        document, rows = _rows(data, GAME_ACTOR_INFO)
        new = []
        for model in sorted(set(models)):
            if DONOR not in rows or model not in rows:
                raise PatchError(f"{GAME_ACTOR_INFO}: no row for {DONOR} or {model}")
            row = {**copy.deepcopy(rows[DONOR]), "__RowId": container_name(model)}
            if "ModelVariationAnims" in rows[model]:
                row["ModelVariationAnims"] = copy.deepcopy(rows[model]["ModelVariationAnims"])
            new.append(row)
        return _insert(document, GAME_ACTOR_INFO, new)

    return transform


def native_inputs(actors: Iterable[str]) -> tuple[str, ...]:
    """Every romfs file :func:`changes` and its transforms can read when an event shows any of the item ``actors``
    (the actors grants give), the dictionaries' pack included, so the app's working set
    (``clawshot.pack.source.working_files``) holds them: the donor's pack, each actor's container model's pack (a
    song's with the effect donor's), the size table, the two actor tables and the ELink table."""
    models = {container_model(actor) for actor in actors}
    songs_shown = bool(models & set(getitem.SONG_MODELS))
    return (
        zsdic.PACK_PATH,
        rstb.TABLE_PATH,
        ACTOR_INFO,
        GAME_ACTOR_INFO,
        pack_path(DONOR),
        *((songs.ELINK, pack_path(songs.EFFECT_DONOR)) if songs_shown else ()),
        *(pack_path(model) for model in sorted(models)),
    )


def changes(
    romfs: str | Path, models: Sequence[str], *, scene_actions: Sequence[str] = ()
) -> tuple[dict[str, Callable[[bytes], bytes]], dict[str, NewFile]]:
    """The row transforms and the container packs for ``models`` (model actors, as :func:`getitem.model_actor` gives
    them); nothing when there are none. ``scene_actions``: the scene animations the seed's events play on song
    containers, which their event users answer (``songs.patch_event_elink``, D20). Reads the dump only."""
    models = sorted(set(models))
    if not models:
        return {}, {}
    romfs = Path(romfs)
    dicts = zsdic.Dictionaries.from_romfs(romfs)

    def members(actor: str) -> dict[str, bytes]:
        path = pack_path(actor)
        if not (romfs / path).is_file():
            raise PatchError(f"no actor pack {path}")
        return sarc.read(dicts.decompress(path, (romfs / path).read_bytes()))

    donor = members(DONOR)
    song_models = [m for m in models if m in getitem.SONG_MODELS]

    def model_pack(model: str) -> dict[str, bytes]:
        if model not in getitem.SONG_MODELS:
            return members(model)
        heart = sarc.write(members(songs.EFFECT_DONOR))
        return sarc.read(songs.patch_song_pack(sarc.write(members(model)), song=model, effect_donor=heart))

    table = rstb.read(dicts.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    entry = table.get(actor_member(DONOR))
    packs = {
        pack_path(container_name(m)): build_pack(
            donor,
            model_pack(m),
            m,
            donor_entry=entry,
            elink_user=songs.event_user_name(m) if m in song_models else None,
        )
        for m in models
    }
    transforms = {ACTOR_INFO: actor_info_transform(models), GAME_ACTOR_INFO: game_actor_info_transform(models)}
    if song_models:  # D18: the songs' event users
        transforms[songs.ELINK] = partial(
            songs.patch_event_elink,
            songs=song_models,
            effects=songs.load_effects(),
            scene_actions=tuple(sorted(set(scene_actions))),
        )
    return transforms, packs
