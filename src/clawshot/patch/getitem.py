"""Explicit native get-display experiments; no inventory or chest-admission policy changes.

Songs borrow native ocarina meshes. Ocarina chests stage native cutscene props,
without changing the playable Accessory actors. Neither correction is automatic
before visual review.
"""

import copy
from collections.abc import Iterable
from functools import partial
from pathlib import Path

from clawshot.census.hints import flow_path, read_flow
from clawshot.formats import byml, evfl, sarc
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
CHEST_FLOWS = ("Dm_SY_TreasureboxSmall", "Dm_SY_Treasurebox")
MESSAGE_TARGET = "UI_MessageTargetActorName"
MODEL_FIELDS = ("FmdbName", "ModelProjectName", "ModelAabbMin", "ModelAabbMax")


def pack_path(actor: str) -> str:
    return f"Pack/Actor/{actor}.pack.zs"


def _dump(document: byml.Document) -> bytes:
    result = byml.dump(document)
    if difference := byml.difference(document.root, byml.read(result)):
        raise PatchError(f"get-display BYML failed read-back: {difference}")
    return result


def patch_pack(data: bytes, *, actor: str) -> bytes:
    """Change a song's mesh without changing its grant identity."""
    if actor not in SONG_MODELS:
        raise PatchError(f"no song get-display correction for {actor}")
    pack = sarc.read(data)
    components = resolve_member(pack, actor_path(actor))["Components"]
    model_member = member_path(components["ModelInfoRef"])
    model = byml.load(pack[model_member])
    if (model.root.get("FmdbName"), model.root.get("ModelProjectName")) != ("Obj_Rupee", "Obj_Rupee"):
        raise PatchError(f"{actor}: stale native model: {model.root}")
    if components.get("EventPerformerRef") != "?" + PERFORMER:
        raise PatchError(f"{actor}: song no longer uses the pouch performer")
    for field in ("FmdbName", "ModelProjectName"):
        model.root[field] = SONG_MODELS[actor]
    pack[model_member] = _dump(model)
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
        if actor not in SONG_MODELS:
            raise PatchError(f"no song get-display correction for {actor}")
        row = rows[actor]
        if (row.get("FmdbName"), row.get("ModelProjectName")) != ("Obj_Rupee", "Obj_Rupee"):
            raise PatchError(f"{actor}: stale ActorInfo model: {row}")
    # Donors remain native; never alter the playable ocarina rows.
    donors = {name: copy.deepcopy(rows[name]) for name in OCARINAS}
    for actor in actors:
        row = rows[actor]
        donor = donors[SONG_MODELS[actor]]
        if (donor.get("FmdbName"), donor.get("ModelProjectName")) != (SONG_MODELS[actor],) * 2:
            raise PatchError(f"{actor}: native model donor changed: {donor}")
        for field in MODEL_FIELDS:
            row[field] = copy.deepcopy(donor[field])
        field = "PreActorRenderInfoHeapSize"
        row[field] = type(row[field])(max(row[field], donor[field]))
        field = "InstanceHeapSize"
        row[field] = type(row[field])(int(row[field]) + int(donor[field]))
    return _dump(document)


def patch_chest_flow(data: bytes, *, prop_template: evfl.Actor) -> bytes:
    """Stage native props for ocarinas, keeping the actual equipment actors native.

    The native gift binds to Player's Weapon_L, not the generic chest guest.
    UI_MessageTargetActorName is the existing item-name UI scratch String64; the
    normal get window subsequently sets it to the very same ContentName.
    """
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name not in CHEST_FLOWS:
        raise PatchError("not a native chest flow")
    if any(e.name.startswith("Clawshot_Ocarina") for e in fc.events):
        raise PatchError(f"{fc.name}: ocarina presentation already patched")
    original = list(fc.events)

    def action_name(event):
        if isinstance(event, evfl.ActionEvent):
            return fc.actors[event.actor].name, fc.actors[event.actor].actions[event.action]
        return None

    def unique(actor, action):
        found = [i for i, e in enumerate(original) if action_name(e) == (actor, action)]
        if len(found) != 1:
            raise PatchError(f"{fc.name}: expected one {actor}.{action}, found {found}")
        return found[0]

    guest = "PouchContentGuestPerformer"
    actions = ["EventTriggerPlayerNoHit", "EventTriggerModelBindForItemGetDemo", "EventPlayAS"]
    if fc.name == "Dm_SY_Treasurebox":
        actions = [actions[2], actions[0], actions[1]]
    chain = [unique(guest, action) for action in actions]
    if any(original[a].next != b for a, b in zip(chain, chain[1:], strict=False)):
        raise PatchError(f"{fc.name}: native get-demo chain changed: {[original[i] for i in chain]}")
    start = chain[0]
    continuation = original[chain[-1]].next
    sleep = unique("TreasureBox_EventStarter", "EventTriggerTBoxRequestSleepActorHolderData")
    game_data = next(i for i, a in enumerate(fc.actors) if a.name == "GameDataActor")
    gd = fc.actors[game_data]
    for collection, name in (
        (gd.actions, "EventTriggerSetGameDataString64"),
        (gd.queries, "EventQueryIsGameDataString64"),
    ):
        if name not in collection:
            collection.append(name)
    props = []
    for actor in OCARINAS:
        prop = copy.deepcopy(prop_template)
        prop.name = "Dm_" + actor
        prop.secondary_name = ""
        prop.entry_point = evfl.NONE
        prop.actions = ["EventTriggerParticipateEvent", "EventTriggerModelBind", "EventGoOffstageForUser"]
        props.append(len(fc.actors))
        fc.actors.append(prop)

    def append(event):
        index = len(fc.events)
        event.name = f"Clawshot_Ocarina_{index}"
        fc.events.append(event)
        return index

    def gate(targets, otherwise):
        current = otherwise
        for actor, target in reversed(list(zip(OCARINAS, targets, strict=True))):
            current = append(
                evfl.SwitchEvent(
                    "",
                    game_data,
                    gd.queries.index("EventQueryIsGameDataString64"),
                    [(0, target), (1, current)],
                    {"GameDataName": MESSAGE_TARGET, "Index": -1, "Value": actor},
                )
            )
        return append(
            evfl.ActionEvent(
                "",
                game_data,
                gd.actions.index("EventTriggerSetGameDataString64"),
                current,
                {"GameDataName": MESSAGE_TARGET, "Index": -1, "Value": evfl.Argument("ContentName")},
            )
        )

    show, hide = [], []
    for prop in props:
        attach = append(
            evfl.ActionEvent(
                "",
                prop,
                1,
                continuation,
                {
                    "ActorName": "Player_Event",
                    "InstanceName": "",
                    "BoneName": "Weapon_L",
                    "TransOffset": evfl.FloatArray((0.0, 0.0, 0.0)),
                    "RotOffset": evfl.FloatArray((0.0, 0.0, 0.0)),
                },
            )
        )
        show.append(append(evfl.ActionEvent("", prop, 0, attach)))
        hide.append(
            append(
                evfl.ActionEvent(
                    "",
                    prop,
                    2,
                    original[sleep].next,
                    {
                        "IsWaitEnd": True,
                        "IsSleepXLink": True,
                        "ExecuteSetSpeedZeroEveryFrame": False,
                        "IsRidingTargetGoOffstage": False,
                    },
                )
            )
        )
    show_gate = gate(show, start)
    # Redirect existing incoming edges; the fallback still runs the native chain.
    for event in original:
        if getattr(event, "next", None) == start:
            event.next = show_gate
        if isinstance(event, evfl.ForkEvent):
            event.forks = [show_gate if i == start else i for i in event.forks]
        if isinstance(event, (evfl.SwitchEvent, evfl.SubFlowSwitchEvent)):
            event.cases = [(value, show_gate if i == start else i) for value, i in event.cases]
    for entry in fc.entry_points:
        if entry.main_event == start:
            entry.main_event = show_gate
    original[sleep].next = gate(hide, original[sleep].next)
    written = evfl.write(document)
    if evfl.read(written) != document:
        raise PatchError(f"{fc.name}: ocarina presentation failed read-back")
    return written


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
    for model in {SONG_MODELS.get(actor, actor) for actor in actors}:
        if not (romfs / f"Model/{model}.{model}.bfres.zs").is_file():
            raise PatchError(f"missing native model {model}")
    songs = tuple(actor for actor in actors if actor in SONG_MODELS)
    out = {pack_path(actor): partial(patch_pack, actor=actor) for actor in songs}
    if songs:
        out[ACTOR_INFO] = partial(patch_actor_info, actors=songs)
    if any(actor in OCARINAS for actor in actors):
        # Copy native lifecycle metadata, not a guessed event actor creation policy.
        template = next(a for a in read_flow(romfs, "Dm_MelodyGet_Time").actors if a.name == "Dm_" + TIME)
        if (template.params or {}).get("EventMemberCreateMethod") != 1:
            raise PatchError(f"native ocarina prop creation changed: {template}")
        for flow in CHEST_FLOWS:
            out[flow_path(romfs, flow)] = partial(patch_chest_flow, prop_template=template)
    return out


def member_growth(before: bytes, after: bytes) -> dict[str, int]:
    """Retain original parsed overhead for same-shape song model substitutions."""
    original, changed = sarc.read(before), sarc.read(after)
    growth = {}
    for actor in SONG_MODELS:
        member = member_path(actor_path(actor))
        if member not in original:
            continue
        components = resolve_member(original, actor_path(actor))["Components"]
        model_member = member_path(components["ModelInfoRef"])
        editable = (model_member,)
        for name in editable:
            if changed.get(name) == original[name]:
                continue
            if name not in changed:
                raise PatchError(f"{name}: missing get-display member")
            old, new = byml.read(original[name]), byml.read(changed[name])
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
