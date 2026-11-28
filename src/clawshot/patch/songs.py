"""Song get effects: songs found in a chest, at a gift or on the floor show an ocarina with an effect of their own
instead of the green rupee every ``Item_Melody_*`` natively shows (plans/song-get-effects.md).

:func:`build` gives the step's changes and new files:

- the ELink table ``.110``: one user ``Clawshot_Song_<Song>`` per song, a copy of ``Obj_Heart_Container``'s; non-warp
  songs play their own lesson effect on ``Wait`` (the floor pickup) and ``GetDemo`` (the get pose), warp songs a
  play-all container of nine charge-effect children on each (:func:`patch_elink`);
- the always-loaded effect file ``static``: the charge effect split into three clones (:func:`patch_static`);
- each ``Item_Melody_*`` pack: the ocarina's model with the common get-pose animation, the effect user, the heart
  container's ASInfo and the resident XLink component (:func:`patch_song_pack`), and its ActorInfo row
  (:func:`patch_actor_info`);
- with ``pickups`` only: twelve floor pickups ``Obj_Clawshot_Melody_<Song>`` built from ``Obj_Arrow_Fire``
  (:func:`pickup_pack`) with their ActorInfo, GameActorInfo and PouchActorInfo rows. Seeds build without them:
  they are written only once a feature places them (Kareem, 2026-11-23, rounds/r21-pr41.md finding 4).

The effect values live in ``data/song_effects.toml`` (:func:`load_effects`).
"""

import bisect
import copy
import math
import tomllib
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from clawshot.formats import byml, elink, sarc, vfx, zsdic
from clawshot.patch import getitem
from clawshot.patch.plan import PatchError
from clawshot.patch.shops import actor_path, member_path, resolve_member
from clawshot.patch.write import FileChanges, NewFile

ELINK = "ELink2/elink2.Product.110.belnk.zs"  # the table game version 1.1.1 loads (S12)
STATIC = "Effect/static.Nin_Ounce_NVN2.vsetb.byml.zs"
ACTOR_INFO = getitem.ACTOR_INFO
GAME_ACTOR_INFO = "RSDB/GameActorInfo.Product.111.rstbl.byml.zs"
POUCH_ACTOR_INFO = "RSDB/PouchActorInfo.Product.111.rstbl.byml.zs"
EFFECT_DONOR = "Obj_Heart_Container"  # its ELink user and ASInfo (S5)
EVENT_BONE = "Skl_Root"  # the bone event containers show the effect on (event-items D18)
# event-items D20: an event user starts its get-pose effect from these scene animations too (slot, template action)
SCENE_SLOT = "AS[Lower]"  # as Obj_Heart_Piece's Dm_Goron_0040_Obj_Heart_Piece/C01
SCENE_TEMPLATE = "Rotate_GetDemo"  # its trigger starts GetDemo
PICKUP_DONOR = "Obj_Arrow_Fire"  # a native free-standing item pickup
CHARGE = "Ply_ChargeLv3_Loop_02"  # the player's sword-charge effect, in static
SPARK, AURA, LIGHT = "Clawshot_ChargeSpark", "Clawshot_ChargeAura", "Clawshot_ChargeLight"
CLONES = {SPARK: ("Spark_Small",), AURA: ("Glow_L", "Glow_Long_00"), LIGHT: ("LineLight",)}
# A resident resource (no pack member) that runs the effect triggers; songs lack it natively.
XLINK = "?Component/XLink/ActorBasic.engine__component__XLinkParam.bgyml"
PICKUP_DROPPED = ("GameParameterTableRef", "SLinkRef", "CaptureRef")
SONG_ADDED = ("ASRef", "AnimationRef", "ELinkRef", "XLinkRef", "ASInfoRef")

EFFECTS_TOML = Path(__file__).resolve().parents[1] / "data" / "song_effects.toml"
WARP, NON_WARP = "warp", "non_warp"
PLACES = ("floor", "get_pose")
COLOURS = ("sparks", "aura", "light")


class SongEffectsError(ValueError):
    pass


@dataclass(frozen=True)
class NonWarpEffect:
    effect: str
    scale: float


@dataclass(frozen=True)
class Place:
    """A warp song's effect at one place (the floor pickup or the get pose): scale, height below the ocarina and the
    R, G, B multipliers of each part."""

    scale: float
    position_y: float
    sparks: tuple[float, float, float]
    aura: tuple[float, float, float]
    light: tuple[float, float, float]


@dataclass(frozen=True)
class WarpEffect:
    ring_radius: float
    rotation_x: float
    life_scale: float
    floor: Place
    get_pose: Place


@dataclass(frozen=True)
class SongEffects:
    source: str
    floor_condition: int
    get_pose_condition: int
    songs: dict[str, NonWarpEffect | WarpEffect]


def _number(value, where: str, *, low: float | None = None, above: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise SongEffectsError(f"{where}: {value!r} is not a number")
    if low is not None and value < low:
        raise SongEffectsError(f"{where}: {value!r} is below {low}")
    if above is not None and value <= above:
        raise SongEffectsError(f"{where}: {value!r} must be above {above}")
    return float(value)


def _colour(value, where: str) -> tuple[float, float, float]:
    if not isinstance(value, list) or len(value) != 3:
        raise SongEffectsError(f"{where}: {value!r} is not three numbers (R, G, B)")
    r, g, b = (_number(v, where, low=0) for v in value)
    return r, g, b


def _get(table: dict, key: str, where: str):
    if key not in table:
        raise SongEffectsError(f"{where}: missing")
    return table[key]


def _song(song: str, entry) -> NonWarpEffect | WarpEffect:
    if not isinstance(entry, dict):
        raise SongEffectsError(f"{song}: not a table")
    kind = _get(entry, "kind", f"{song}: kind")
    if kind not in (WARP, NON_WARP):
        raise SongEffectsError(f"{song}: kind {kind!r} is neither {WARP!r} nor {NON_WARP!r}")
    expected = WARP if getitem.SONG_MODELS[song] == getitem.TIME else NON_WARP
    if kind != expected:
        raise SongEffectsError(f"{song}: kind {kind!r}, but it shows {getitem.SONG_MODELS[song]} ({expected!r})")
    if kind == NON_WARP:
        effect = _get(entry, "effect", f"{song}: effect")
        if not isinstance(effect, str) or not effect:
            raise SongEffectsError(f"{song}: effect {effect!r} is not an effect name")
        return NonWarpEffect(effect, _number(_get(entry, "scale", f"{song}: scale"), f"{song}: scale", above=0))
    places = {}
    for place in PLACES:
        table = _get(entry, place, f"{song}: {place}")
        if not isinstance(table, dict):
            raise SongEffectsError(f"{song}: {place} is not a table")
        at = f"{song}: {place}"
        places[place] = Place(
            _number(_get(table, "scale", f"{at}.scale"), f"{at}.scale", above=0),
            _number(_get(table, "position_y", f"{at}.position_y"), f"{at}.position_y"),
            *(_colour(_get(table, c, f"{at}.{c}"), f"{at}.{c}") for c in COLOURS),
        )
    return WarpEffect(
        _number(_get(entry, "ring_radius", f"{song}: ring_radius"), f"{song}: ring_radius", low=0),
        _number(_get(entry, "rotation_x", f"{song}: rotation_x"), f"{song}: rotation_x"),
        _number(_get(entry, "life_scale", f"{song}: life_scale"), f"{song}: life_scale", above=0),
        places["floor"],
        places["get_pose"],
    )


def parse_effects(text: str) -> SongEffects:
    """The effect values from TOML text; :class:`SongEffectsError` names the song and key of the first problem."""
    data = tomllib.loads(text)
    source = _get(data, "source", "source")
    if not isinstance(source, str) or not source:
        raise SongEffectsError("source: not a description of where the values come from")
    conditions = _get(data, "conditions", "conditions")
    floor, get_pose = (_get(conditions, key, f"conditions: {key}") for key in ("floor", "get_pose"))
    for key, value in (("floor", floor), ("get_pose", get_pose)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise SongEffectsError(f"conditions: {key} {value!r} is not a condition-table offset")
    table = _get(data, "songs", "songs")
    for song in table:
        if song not in getitem.SONG_MODELS:
            raise SongEffectsError(f"{song}: not a song actor")
    effects = {}
    for song in getitem.SONG_MODELS:
        effects[song] = _song(song, _get(table, song, f"{song}: missing"))
    return SongEffects(source, floor, get_pose, effects)


def load_effects(path: Path = EFFECTS_TOML) -> SongEffects:
    return parse_effects(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------------------------------
# Names


def user_name(song: str) -> str:
    return "Clawshot_Song_" + song.removeprefix("Item_Melody_")


def event_user_name(song: str) -> str:
    """A song's event containers' effect user (event-items D18)."""
    return user_name(song) + "_Event"


def pickup_name(song: str) -> str:
    return "Obj_Clawshot_Melody_" + song.removeprefix("Item_Melody_")


def elink_member(actor: str) -> str:
    return f"Component/ELink/{actor}.engine__component__ELinkParam.bgyml"


def pouch_member(actor: str) -> str:
    return f"Component/PouchContentParam/{actor}.game__component__PouchContentParam.bgyml"


def _ordered(effects: SongEffects) -> list[str]:
    """Warp songs, then the others, each in ``getitem.SONG_MODELS`` order (the gallery build's order)."""
    warp = [s for s, e in effects.songs.items() if isinstance(e, WarpEffect)]
    return warp + [s for s in effects.songs if s not in warp]


# ---------------------------------------------------------------------------------------------------------------
# The ELink table


def warp_children(effect: WarpEffect, place: Place) -> list[dict[str, str | float]]:
    """The nine children of a warp song's call: 4 sparks and 4 auras on the ring (0, 90, 180, 270 degrees; positions
    rounded to 4 places, so 270 degrees gives -0.0 as in the gallery), then the light in the centre."""
    children = []
    for part, colour in ((SPARK, place.sparks), (AURA, place.aura), (LIGHT, place.light)):
        angles = [math.radians(90 * k) for k in range(4)] if part != LIGHT else [None]
        for angle in angles:
            x = 0.0 if angle is None else round(effect.ring_radius * math.cos(angle), 4)
            z = 0.0 if angle is None else round(effect.ring_radius * math.sin(angle), 4)
            children.append(
                {
                    "RuntimeAssetName": part,
                    "PositionX": x,
                    "PositionZ": z,
                    "RotationX": effect.rotation_x,
                    "Scale": place.scale,
                    "LifeScale": effect.life_scale,
                    "PositionY": place.position_y,
                    "Red": colour[0],
                    "Green": colour[1],
                    "Blue": colour[2],
                }
            )
    return children


def _add_users(
    data: bytes,
    songs: Sequence[str],
    name: Callable[[str], str],
    bone: str,
    effects: SongEffects,
    scene_actions: Sequence[str] = (),
) -> bytes:
    """``data`` with a user ``name(song)`` per song of ``songs`` (in :func:`_ordered` order), a copy of the effect
    donor's showing the song's effect, its get-pose effect (``GetDemo``, and a warp song's children) on ``bone``, and
    a trigger starting it from each of ``scene_actions`` (:data:`SCENE_SLOT`, a copy of :data:`SCENE_TEMPLATE`'s)."""
    try:
        table = elink.decode(data)
        order = [song for song in _ordered(effects) if song in songs]
        for song in order:
            table.add_user_copy(EFFECT_DONOR, name(song))
        for song in order:
            effect, user = effects.songs[song], name(song)
            if isinstance(effect, WarpEffect):
                table.set_call_params(user, "Wait", {"RuntimeAssetName": CHARGE, "Bone": "Root"})
                # the children copy these records
                table.set_call_params(user, "GetDemo", {"RuntimeAssetName": CHARGE, "Bone": bone})
            else:
                values = {"RuntimeAssetName": effect.effect, "Scale": effect.scale}
                table.set_call_params(user, "Wait", values)
                table.set_call_params(user, "GetDemo", {**values, "Bone": bone, "PositionY": 0.0})
        for song in order:
            effect, user = effects.songs[song], name(song)
            if isinstance(effect, WarpEffect):
                get_pose = warp_children(effect, effect.get_pose)
                table.make_container(user, "GetDemo", get_pose, effects.get_pose_condition)
                table.make_container(user, "Wait", warp_children(effect, effect.floor), effects.floor_condition)
        if scene_actions:
            for song in order:
                table.add_action_triggers(name(song), SCENE_SLOT, sorted(set(scene_actions)), SCENE_TEMPLATE)
        out = table.encode()
        again = elink.decode(out)
    except elink.ElinkError as error:
        raise PatchError(f"{ELINK}: {error}") from error
    if again.encode() != out or sorted(again.user_names()) != sorted(table.user_names()):
        raise PatchError(f"{ELINK}: the song users do not read back")
    return out


def patch_elink(data: bytes, *, effects: SongEffects) -> bytes:
    """The ``.110`` table with the twelve song users (plans/song-get-effects.md, "The effect table"). Every native
    user decodes as before: the edits only append."""
    return _add_users(data, list(effects.songs), user_name, "Root", effects)


def patch_event_elink(
    data: bytes, *, songs: Sequence[str], effects: SongEffects, scene_actions: Sequence[str] = ()
) -> bytes:
    """The table with an event user per song of ``songs`` (event-items D18): the song's user with its get-pose effect
    on :data:`EVENT_BONE`, which a scene's own animation moves (Zelda's throw) and which is ``Root`` at rest.

    ``scene_actions`` (D20, ``<ASB root>/<node>``: the scene animations a seed's events play on song containers) each
    start the get-pose effect too, as ``Rotate_GetDemo`` does: an emitted key does not show while a scene animation
    plays on the prop (runs S3, S4, S11), a trigger on the scene animation does (pilot A, runs S12, S13). The songs'
    own users (:func:`patch_elink`) get none."""
    if unknown := sorted(set(songs) - set(effects.songs)):
        raise PatchError(f"{ELINK}: {unknown} are not songs")
    return _add_users(data, songs, event_user_name, EVENT_BONE, effects, scene_actions)


# ---------------------------------------------------------------------------------------------------------------
# The effect file


def patch_static(data: bytes, *, effects: SongEffects) -> bytes:
    """``static`` with the charge effect cloned three times, each clone keeping only its emitters."""
    document = byml.load(data)
    ptcl = document.root.get("PtclBin") if isinstance(document.root, dict) else None
    if document.version != 5 or not isinstance(ptcl, byml.Binary):
        raise PatchError(f"{STATIC}: not a version 5 effect file with a PtclBin")
    try:
        names = set(vfx.effect_names(ptcl.data))
        needed = [CHARGE] + [e.effect for e in effects.songs.values() if isinstance(e, NonWarpEffect)]
        for name in needed:
            if name not in names:
                raise PatchError(f"{STATIC}: no effect {name!r}, which the song effects play")
        for name in CLONES:
            if name in names:
                raise PatchError(f"{STATIC}: effect {name!r} already exists")
        blob = ptcl.data
        for name, keep in CLONES.items():
            blob = vfx.clone(blob, CHARGE, name, keep)
        vfx.check(blob, dict.fromkeys(CLONES, CHARGE))
    except vfx.VfxError as error:
        raise PatchError(f"{STATIC}: {error}") from error
    document.root["PtclBin"] = byml.Binary(blob, ptcl.alignment)
    out = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(out))) is not None:
        raise PatchError(f"{STATIC}: the grown effect file does not read back: {difference}")
    return out


# ---------------------------------------------------------------------------------------------------------------
# Song packs and rows


def _asinfo(effect_donor: bytes) -> tuple[str, bytes]:
    """The donor's ASInfo reference and member (native path, native size entry)."""
    donor = sarc.read(effect_donor)
    ref = resolve_member(donor, actor_path(EFFECT_DONOR))["Components"].get("ASInfoRef")
    if not ref or member_path(ref) not in donor:
        raise PatchError(f"{EFFECT_DONOR}: its ASInfoRef {ref!r} is not a member of its pack")
    return ref, donor[member_path(ref)]


def patch_song_pack(data: bytes, *, song: str, effect_donor: bytes) -> bytes:
    """A song pack showing its ocarina with the effect user: the ocarina's model, ``ASRef`` to the common animation
    set, its own AnimationParam ``[Item_Common_Animation, <ocarina>_Animation]``, ELinkParam ``{UserName}``, the
    heart container's ASInfo and the resident XLink component. Every other member stays as it is."""
    if song not in getitem.SONG_MODELS:
        raise PatchError(f"{song}: not a song")
    ocarina = getitem.SONG_MODELS[song]
    pack = sarc.read(data)
    param = member_path(actor_path(song))
    if param not in pack:
        raise PatchError(f"{song}: the pack has no {param}")
    document = byml.load(pack[param])
    components = document.root.get("Components", {})
    for key in SONG_ADDED:
        if key in components:
            raise PatchError(f"{song}: already has {key} {components[key]!r}")
    model_member = member_path(components.get("ModelInfoRef", ""))
    if model_member not in pack:
        raise PatchError(f"{song}: no ModelInfo member {model_member!r}")
    model = byml.load(pack[model_member])
    if (model.root.get("FmdbName"), model.root.get("ModelProjectName")) != ("Obj_Rupee", "Obj_Rupee"):
        raise PatchError(f"{song}: ModelInfo is {model.root!r}, not the native Obj_Rupee")
    animation, link = getitem.animation_member(song), elink_member(song)
    for member in (animation, link):
        if member in pack:
            raise PatchError(f"{song}: the pack already holds {member}")
    ref, asinfo = _asinfo(effect_donor)
    if pack.get(member_path(ref), asinfo) != asinfo:
        raise PatchError(f"{song}: holds a different {member_path(ref)}")
    model.root["FmdbName"] = model.root["ModelProjectName"] = ocarina
    pack[model_member] = byml.dump(model)
    pack[animation] = getitem.animation_param(ocarina)
    pack[link] = byml.write({"UserName": user_name(song)})
    pack[member_path(ref)] = asinfo
    components["ASRef"] = "?" + getitem.ANIMATION_SET
    components["AnimationRef"] = "?" + animation
    components["ELinkRef"] = "?" + link
    components["XLinkRef"] = XLINK
    components["ASInfoRef"] = ref
    pack[param] = byml.dump(document)
    result = sarc.write(pack)
    if sarc.read(result) != pack:
        raise PatchError(f"{song}: the song pack does not read back")
    return result


def _rows(data: bytes, path: str) -> tuple[byml.Document, dict[str, dict]]:
    document = byml.load(data)
    rows = document.root
    if not isinstance(rows, list):
        raise PatchError(f"{path}: not a row table")
    ids = [row.get("__RowId") for row in rows]
    keys = [str(i).encode("utf-8") for i in ids]
    if any(not isinstance(i, str) for i in ids) or any(a >= b for a, b in zip(keys, keys[1:], strict=False)):
        raise PatchError(f"{path}: rows are not uniquely sorted by __RowId")
    return document, dict(zip(ids, rows, strict=True))


def _need(rows: Mapping[str, dict], path: str, *names: str) -> None:
    for name in names:
        if name not in rows:
            raise PatchError(f"{path}: no row {name}")


def _insert(document: byml.Document, path: str, new: list[dict]) -> bytes:
    rows = document.root
    for row in sorted(new, key=lambda r: r["__RowId"].encode("utf-8")):
        keys = [r["__RowId"].encode("utf-8") for r in rows]
        name = row["__RowId"].encode("utf-8")
        if name in keys:
            raise PatchError(f"{path}: row {row['__RowId']} already exists")
        rows.insert(bisect.bisect_left(keys, name), row)
    out = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(out))) is not None:
        raise PatchError(f"{path}: the changed table does not read back: {difference}")
    return out


def shown_row(row: Mapping, ocarina: Mapping, song: str) -> dict:
    """The fields that make a song's native ActorInfo ``row`` show its ocarina with the effect user: the ocarina's
    model fields, ``ELinkUserName``, ``InstanceHeapSize`` plus the ocarina's and the larger
    ``PreActorRenderInfoHeapSize`` (as the gallery confirmed in game). Shared with the song's event container
    (``containers``). Raises :class:`PatchError` for a row that is not the native one."""
    if (row.get("FmdbName"), row.get("ModelProjectName")) != ("Obj_Rupee", "Obj_Rupee"):
        raise PatchError(f"{ACTOR_INFO}: {song} shows {row.get('FmdbName')!r}, not the native Obj_Rupee")
    if "ELinkUserName" in row:
        raise PatchError(f"{ACTOR_INFO}: {song} already has ELinkUserName {row['ELinkUserName']!r}")
    out = {field: copy.deepcopy(ocarina[field]) for field in getitem.MODEL_FIELDS}
    heap, render = "InstanceHeapSize", "PreActorRenderInfoHeapSize"
    out[heap] = type(row[heap])(int(row[heap]) + int(ocarina[heap]))
    out[render] = type(row[render])(max(int(row[render]), int(ocarina[render])))
    out["ELinkUserName"] = user_name(song)
    return out


def patch_actor_info(data: bytes, *, pickups: bool = False) -> bytes:
    """Song rows get the ocarina's model fields, ``ELinkUserName`` and heaps (``InstanceHeapSize`` plus the
    ocarina's, ``PreActorRenderInfoHeapSize`` the larger: as the gallery confirmed in game); with ``pickups`` the
    pickups' rows, copied from ``Obj_Arrow_Fire``'s, are inserted by name. Works on a table earlier steps changed."""
    document, rows = _rows(data, ACTOR_INFO)
    _need(rows, ACTOR_INFO, *getitem.SONG_MODELS, *getitem.OCARINAS, *([PICKUP_DONOR] if pickups else []))
    new = []
    for song in getitem.SONG_MODELS:
        ocarina = getitem.model_actor(song)  # the get pose's model
        row, donor = rows[song], rows[ocarina]
        row.update(shown_row(row, donor, song))
        if not pickups:
            continue
        pickup = copy.deepcopy(rows[PICKUP_DONOR])
        pickup["__RowId"] = pickup_name(song)
        for field in getitem.MODEL_FIELDS:
            pickup[field] = copy.deepcopy(donor[field])
        pickup["ELinkUserName"] = user_name(song)
        pickup.pop("SLinkUserName", None)
        if "AnimationResources" in pickup:
            pickup["AnimationResources"] = byml.read(getitem.animation_param(ocarina))["AnimationResources"]
        pickup["ActorName"] = song
        new.append(pickup)
    return _insert(document, ACTOR_INFO, new)


def patch_game_actor_info(data: bytes) -> bytes:
    """The pickups' rows: ``Obj_Arrow_Fire``'s (world behaviour), renamed."""
    document, rows = _rows(data, GAME_ACTOR_INFO)
    _need(rows, GAME_ACTOR_INFO, PICKUP_DONOR)
    new = [{**copy.deepcopy(rows[PICKUP_DONOR]), "__RowId": pickup_name(song)} for song in getitem.SONG_MODELS]
    return _insert(document, GAME_ACTOR_INFO, new)


def patch_pouch_actor_info(data: bytes) -> bytes:
    """The pickups' rows: each song's own, renamed."""
    document, rows = _rows(data, POUCH_ACTOR_INFO)
    _need(rows, POUCH_ACTOR_INFO, *getitem.SONG_MODELS)
    new = [{**copy.deepcopy(rows[song]), "__RowId": pickup_name(song)} for song in getitem.SONG_MODELS]
    return _insert(document, POUCH_ACTOR_INFO, new)


# ---------------------------------------------------------------------------------------------------------------
# Floor pickups


def pickup_pack(song: str, *, arrow: bytes, song_pack: bytes) -> NewFile:
    """``Obj_Clawshot_Melody_<Song>``: ``Obj_Arrow_Fire``'s pack with its ActorParam renamed and pointing at the
    song (ActorName, the song's ModelInfo as ``song_pack`` holds it), its own AnimationParam, PouchContentParam
    ``{$parent: the song's, PouchActor: the song, GetDemoOffsetPos: the arrow's}`` and ELinkParam; the arrow's
    GameParameterTable, SLink and Capture references dropped (plans/song-get-effects.md, "Floor pickups")."""
    pickup, ocarina = pickup_name(song), getitem.SONG_MODELS[song]
    donor = sarc.read(arrow)
    old_param = member_path(actor_path(PICKUP_DONOR))
    if old_param not in donor:
        raise PatchError(f"{PICKUP_DONOR}: the pack has no {old_param}")
    song_members = sarc.read(song_pack)
    song_components = byml.read(song_members[member_path(actor_path(song))])["Components"]
    model_member = member_path(song_components["ModelInfoRef"])
    pouch_parent = member_path(song_components["PouchContentRef"])
    pack = dict(donor)
    document = byml.load(pack.pop(old_param))
    components = document.root["Components"]
    for key in PICKUP_DROPPED:
        components.pop(key, None)
    donor_pouch = byml.read(donor[member_path(components["PouchContentRef"])])
    if "GetDemoOffsetPos" not in donor_pouch:
        raise PatchError(f"{PICKUP_DONOR}: its pouch component has no GetDemoOffsetPos")
    param = member_path(actor_path(pickup))
    animation, link, pouch = getitem.animation_member(pickup), elink_member(pickup), pouch_member(pickup)
    for member in (param, animation, link, pouch):
        if member in pack:
            raise PatchError(f"{PICKUP_DONOR}: the pack already holds {member}")
    components["ActorNameRef"] = f"?ActorSystem/ActorName/{song}.engine__actor__ActorName.bgyml"
    components["ModelInfoRef"] = "?" + model_member
    components["AnimationRef"] = "?" + animation
    components["PouchContentRef"] = "?" + pouch
    components["ELinkRef"] = "?" + link
    pack[model_member] = song_members[model_member]
    pack[pouch_parent] = song_members[pouch_parent]
    pack[animation] = getitem.animation_param(ocarina)
    pack[link] = byml.write({"UserName": user_name(song)})
    pack[pouch] = byml.write(
        {
            "$parent": "Work/" + pouch_parent.replace(".bgyml", ".gyml"),
            "GetDemoOffsetPos": donor_pouch["GetDemoOffsetPos"],
            "PouchActor": actor_path(song),
        }
    )
    pack[param] = byml.dump(document)
    data = sarc.write(pack)
    if sarc.read(data) != pack:
        raise PatchError(f"{pickup}: the pickup pack does not read back")
    copied = {name: getitem.pack_path(PICKUP_DONOR) for name in donor if name != old_param}
    copied[model_member] = copied[pouch_parent] = getitem.pack_path(song)
    return NewFile(data, copied=copied)


# ---------------------------------------------------------------------------------------------------------------
# The step


@dataclass(frozen=True)
class Delivery:
    """``changes`` for the common writer's ``extra_changes`` and ``new_files`` (the pickup packs, with ``pickups``)
    for its ``new_files``."""

    changes: FileChanges
    new_files: Mapping[str, NewFile]


def songs_can_move(shuffle: Iterable[str]) -> bool:
    """Whether the settings let songs leave their places (today: Gift or an expanded gift kind).

    Like ``getitem.ocarina_get_model_possible``, this selects the build from settings, not actual placements
    (PR #41 option 2, 2026-11-23). Other seeds keep these files byte-identical to the dump."""
    return bool(getitem.gift_kinds(shuffle))


PICKUP_KINDS = ("Token", "BossHeart", "Freestanding")
"""The location kinds where a song stands as its floor pickup (ocarina-song-drops-everywhere): a Skulltula drop
(``patch.tokens``) or a floor (``patch.drops``)."""


def pickups_possible(shuffle: Iterable[str], songs_setting: str) -> bool:
    """Whether the settings could put a song at a kind of :data:`PICKUP_KINDS`: the song step runs
    (:func:`songs_can_move`), ``songs = anywhere`` (only then do songs join the Skulltula and floor pools) and Token,
    BossHeart or Freestanding is shuffled. A seed gets :func:`build` with ``pickups`` exactly then: Kareem's rule that
    the pickups are written only once a feature places them (2026-11-23, rounds/r21-pr41.md finding 4), as a settings
    rule like the other get-display steps (PR #41, the maintainers' option 2). A seed whose placements need a pickup
    without it is refused (:func:`placed_pickups`, S8)."""
    shuffle = set(shuffle)
    return songs_can_move(shuffle) and songs_setting == "anywhere" and bool(shuffle & set(PICKUP_KINDS))


def placed_pickups(placements: Mapping[str, str], world, actors) -> list[str]:
    """The locations (sorted) of a kind of :data:`PICKUP_KINDS` holding a song: each needs the song's floor pickup."""
    out = []
    for name, item in placements.items():
        location = world.locations.get(name)
        if actors.actors.get(item) in getitem.SONG_MODELS and location is not None and location.type in PICKUP_KINDS:
            out.append(name)
    return sorted(out)


def moved_songs(placements: Mapping[str, str], world, actors) -> list[str]:
    """The locations (sorted) holding a song that is not their vanilla item. ``make_seed`` refuses a seed that has
    one when :func:`songs_can_move` says the settings cannot: the song would show the green rupee. ``actors`` maps
    item names to actors (``clawshot.patch.items.ItemActors``)."""
    out = []
    for name, item in placements.items():
        location = world.locations.get(name)
        if actors.actors.get(item) in getitem.SONG_MODELS and (location is None or location.vanilla != item):
            out.append(name)
    return sorted(out)


def native_inputs(*, pickups: bool = False) -> tuple[str, ...]:
    """Every romfs file :func:`build` and its transforms read, the dictionaries' pack included, so the app's working
    set (``clawshot.pack.source.working_files``) holds them. The animation files the AnimationParams name are not
    read (the game loads them from its own romfs): ``tests/test_getitem_ocarina_dump.py`` checks they exist."""
    return (
        zsdic.PACK_PATH,
        ELINK,
        STATIC,
        ACTOR_INFO,
        *((GAME_ACTOR_INFO, POUCH_ACTOR_INFO) if pickups else ()),
        getitem.pack_path(EFFECT_DONOR),
        *((getitem.pack_path(PICKUP_DONOR),) if pickups else ()),
        *(getitem.pack_path(song) for song in getitem.SONG_MODELS),
    )


def build(romfs: str | Path, *, pickups: bool = False) -> Delivery:
    """The song get effects for a seed: changes to the ELink table, ``static``, the song packs and ActorInfo; with
    ``pickups`` also the twelve pickup packs as new files and their rows in ActorInfo, GameActorInfo and
    PouchActorInfo (no seed asks for them until a feature places them). Raises :class:`PatchError` when a native
    input is missing or not as the record describes it."""
    romfs = Path(romfs)
    for path in native_inputs(pickups=pickups):
        if not (romfs / path).is_file():
            raise PatchError(f"the dump has no {path}, which the song get effects read")
    if pickups:
        for song in getitem.SONG_MODELS:
            path = getitem.pack_path(pickup_name(song))
            if (romfs / path).exists():
                raise PatchError(f"the dump already has {path}")
    try:
        effects = load_effects()
    except SongEffectsError as error:
        raise PatchError(f"{EFFECTS_TOML.name}: {error}") from error
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def read(path: str) -> bytes:
        return dictionaries.decompress(path, (romfs / path).read_bytes())

    heart = read(getitem.pack_path(EFFECT_DONOR))
    changes: dict = {
        ELINK: partial(patch_elink, effects=effects),
        STATIC: partial(patch_static, effects=effects),
        ACTOR_INFO: partial(patch_actor_info, pickups=True) if pickups else patch_actor_info,
    }
    if pickups:
        changes[GAME_ACTOR_INFO] = patch_game_actor_info
        changes[POUCH_ACTOR_INFO] = patch_pouch_actor_info
        arrow = read(getitem.pack_path(PICKUP_DONOR))
    new_files = {}
    for song in getitem.SONG_MODELS:
        path = getitem.pack_path(song)
        changes[path] = partial(patch_song_pack, song=song, effect_donor=heart)
        if pickups:
            changed = patch_song_pack(read(path), song=song, effect_donor=heart)
            new_files[getitem.pack_path(pickup_name(song))] = pickup_pack(song, arrow=arrow, song_pack=changed)
    return Delivery(changes, new_files)
