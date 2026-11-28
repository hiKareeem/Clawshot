"""Events show the given item: each prop of a moved check is renamed to the container of the item's model (spec
event-items 2.2-2.4, D3, D4, D14; plan tasks 8, 9).

Only the prop's entry in the flowchart's or timeline's actor table changes (its name; the secondary name, actions and
parameters stay), so binds, actions, tracks and the grant run as before (D6: native bone, pose and offsets). The grant
names the given item by string and is the gift patch's business.

A hand bind (``event_props.HandBind``) adds what an event lacks: where the native item comes from an actor's own
animation (Link's look in the moat scene shows his equipped ocarina), the given item's container gets an actor entry
of its own (secondary name ``hand``, copied from a template entry with bind and offstage actions), bound to the actor's
bone before one cut and sent offstage before another (played run E10, pilot arm A, BBender 2026-11-26). It holds the
shown item by its middle (D19, played run S6): the bind's ``TransOffset`` is the template bind's plus the native item's
model box centre minus the shown model's (:func:`hand_shift`), both from the dump's ActorInfo rows, so this one
offset differs from the scene's (D6 for every other bind).

A subflow the event calls can name the prop too: actors of one name are one actor in the running event, so the shared
get subflow (``Dm_SY_GetInEvent``, entry ``GetInEvent_Zeldaletter``) sends Zelda's letter prop offstage for the get
pose. Such a subflow actor takes the same container (:func:`plan_subflow_renames`), or the renamed prop and the
subflow's own letter come apart (played run r1-zelda2, BBender 2026-11-26).

A song's container shows its effect only when its effect user's key is emitted (:func:`add_song_effect`): the flow emits
``GetDemo`` right after the container is bound (or joins the event, where the scene never binds it), a timeline runs an
emit clip over its whole presence, a hand bind emits after the new bind. Played pilots (BBender, 2026-11-26): the
container's own animation info, a played still node and an ``Always`` effect user gave no effect; ``Rotate_GetDemo``
gave it with a spin; the emitted key gives it with the ocarina still, as song lessons emit their key on the ocarina.
Where the flow plays a scene animation on the prop (the target's ``C02``, Darunia's ``C09-Gauntlet``) the emitted key
does not show (runs S3, S4, S11); the song's event user then starts its effect from that animation, an action
``<scene set>/<node>`` (:func:`plan_scene_actions`, the prop's ``scene_as``; D20, pilot A, runs S12, S13), as
``Obj_Heart_Piece``'s user does from ``Dm_Goron_0040_Obj_Heart_Piece/C01``. The emit stays: Saria's farewell and the
moat play no scene animation on the prop.
"""

import copy
import struct
from collections.abc import Callable, Collection, Iterable, Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from clawshot.census.event_items import FLOWCHART, TIMELINE
from clawshot.census.gifts import FLOW_VERSIONS, flow_files
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import evfl, sarc, zsdic
from clawshot.patch import containers, event_props, getitem, placed_models
from clawshot.patch.containers import container_name
from clawshot.patch.event_props import PLACEMENT
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges, NewFile

if TYPE_CHECKING:
    from clawshot.patch.event_props import HandBind, Prop

Rename = tuple[str, str, str, str]  # (part, actor, secondary name, container)
HAND = "hand"  # the secondary name of a hand bind's actor entry
BIND, OFFSTAGE = "EventTriggerModelBind", "EventGoOffstageForUser"
JOIN, EMIT = "EventTriggerParticipateEvent", "EventTriggerEmitXLink"
PLAY_AS, AS_NAME = "EventPlayAS", "ASName"
ENTER, LEAVE = 1, 2  # timeline trigger types
SONG_KEY = "GetDemo"  # the song effect user's get-pose key (songs.patch_elink)
EMIT_PARAMS = {"ELinkKey": SONG_KEY, "SLinkKey": ""}
TRANS_OFFSET = "TransOffset"
Vector = tuple[float, float, float]


class HandRename(NamedTuple):
    template: str
    target: str
    bone: str
    start: str
    end: str
    container: str
    shift: Vector = (0.0, 0.0, 0.0)  # added to the template bind's TransOffset (D19, :func:`hand_shift`)


def box_centre(row: Mapping) -> Vector:
    """The middle of an ActorInfo ``row``'s model box: (``ModelAabbMin`` + ``ModelAabbMax``) / 2 per axis."""
    try:
        low, high = row["ModelAabbMin"], row["ModelAabbMax"]
        return tuple((float(low[axis]) + float(high[axis])) / 2 for axis in "XYZ")
    except (KeyError, TypeError) as error:
        raise PatchError(f"{row.get('__RowId', '?')}: no model box ({error!r})") from None


def hand_shift(rows: Mapping[str, Mapping], native: str, shown: str) -> Vector:
    """What a hand bind adds to its offset so ``shown`` sits by its middle where the native item ``native`` does
    (D19): the native row's box centre minus the shown row's, from ActorInfo ``rows`` by ``__RowId``."""
    missing = [name for name in (native, shown) if name not in rows]
    if missing:
        raise PatchError(f"ActorInfo: no row for {missing}")
    return tuple(a - b for a, b in zip(box_centre(rows[native]), box_centre(rows[shown]), strict=True))


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def rename_prop(document: evfl.EventFlowFile, part: str, actor: str, secondary: str, container: str) -> None:
    """Rename the one actor ``actor``/``secondary`` of ``document``'s flowchart or timeline (``part``) to
    ``container``, in place."""
    chart = document.flowchart if part == FLOWCHART else document.timeline if part == TIMELINE else None
    if chart is None:
        raise PatchError(f"{document.name}: no {part} to hold the prop {actor}")
    found = [a for a in chart.actors if (a.name, a.secondary_name) == (actor, secondary)]
    if len(found) != 1:
        raise PatchError(f"{document.name} {part}: {len(found)} actors {actor!r}/{secondary!r}, expected one")
    found[0].name = container


def add_hand_bind(document: evfl.EventFlowFile, hand: HandRename) -> None:
    """Add ``hand`` to ``document``'s flowchart, in place: an actor entry for the container (the template's actions and
    parameters), a bind to ``hand.target``'s ``hand.bone`` run before cut ``hand.start``, and an offstage run before
    cut ``hand.end``; the parameters come from the template's own first bind and offstage events, the bind's
    ``TransOffset`` plus ``hand.shift`` (as f32, as the file stores it)."""
    chart = document.flowchart
    if chart is None:
        raise PatchError(f"{document.name}: no flowchart for the hand bind")
    if any((a.name, a.secondary_name) == (hand.container, HAND) for a in chart.actors):
        raise PatchError(f"{document.name}: the hand bind of {hand.container} is there already")
    found = [i for i, a in enumerate(chart.actors) if a.name == hand.template and a.secondary_name == ""]
    if len(found) != 1:
        raise PatchError(f"{document.name}: {len(found)} template actors {hand.template!r}, expected one")
    template = chart.actors[found[0]]
    if BIND not in template.actions or OFFSTAGE not in template.actions:
        raise PatchError(f"{document.name}: {hand.template} lacks {BIND} or {OFFSTAGE}")
    entries = {entry.name: entry for entry in chart.entry_points}
    if hand.start not in entries or hand.end not in entries:
        raise PatchError(f"{document.name}: no cut {hand.start!r} or {hand.end!r}")

    def first(action: str) -> evfl.ActionEvent:
        index = template.actions.index(action)
        for event in chart.events:
            if isinstance(event, evfl.ActionEvent) and event.actor == found[0] and event.action == index:
                return event
        raise PatchError(f"{document.name}: {hand.template} has no {action} event to copy")

    bind_params = {**copy.deepcopy(first(BIND).params or {}), "ActorName": hand.target, "BoneName": hand.bone}
    if any(hand.shift):
        old = bind_params.get(TRANS_OFFSET)
        if not isinstance(old, evfl.FloatArray) or len(old) != 3:
            raise PatchError(f"{document.name}: {hand.template}'s bind has no 3-float {TRANS_OFFSET} ({old!r})")
        bind_params[TRANS_OFFSET] = evfl.FloatArray(_f32(o + s) for o, s in zip(old, hand.shift, strict=True))
    off_params = copy.deepcopy(first(OFFSTAGE).params)
    names = {event.name for event in chart.events}
    bind_name, off_name = f"Clawshot_{HAND}_bind", f"Clawshot_{HAND}_offstage"
    if bind_name in names or off_name in names:
        raise PatchError(f"{document.name}: event names {bind_name}/{off_name} are taken")
    actor = copy.deepcopy(template)
    actor.name, actor.secondary_name = hand.container, HAND
    chart.actors.append(actor)
    index = len(chart.actors) - 1
    start, end = entries[hand.start], entries[hand.end]
    chart.events.append(evfl.ActionEvent(bind_name, index, template.actions.index(BIND), start.main_event, bind_params))
    start.main_event = len(chart.events) - 1
    chart.events.append(evfl.ActionEvent(off_name, index, template.actions.index(OFFSTAGE), end.main_event, off_params))
    end.main_event = len(chart.events) - 1


def add_song_effect(document: evfl.EventFlowFile, part: str, container: str, secondary: str) -> None:
    """Make the song container ``container``/``secondary`` show its effect, in place, on every actor of that name (the
    two branches of a pair share it): in a flowchart, an emit of :data:`SONG_KEY` right after each of its binds (each
    time it joins the event, where it has no bind); on a timeline, an emit clip from its first clip's start to its last
    clip's end, with its enter and leave triggers in time order."""
    chart = document.flowchart if part == FLOWCHART else document.timeline
    found = [i for i, a in enumerate(chart.actors) if (a.name, a.secondary_name) == (container, secondary)]
    if not found:
        raise PatchError(f"{document.name} {part}: no actor {container!r}/{secondary!r}")
    for index in found:
        _add_song_effect(document, part, chart, index)


def _add_song_effect(document: evfl.EventFlowFile, part: str, chart, index: int) -> None:
    actor = chart.actors[index]
    if EMIT not in actor.actions:
        actor.actions.append(EMIT)
    emit = actor.actions.index(EMIT)
    if part == TIMELINE:
        clips = [clip for clip in chart.clips if clip.actor == index and clip.action != emit]
        if not clips:
            raise PatchError(f"{document.name} timeline: {actor.name} has no clip to show its effect over")
        start = min(clip.start for clip in clips)
        end = max(clip.start + clip.duration for clip in clips)
        chart.clips.append(evfl.Clip(start, end - start, index, emit, clips[0].unknown, copy.deepcopy(EMIT_PARAMS)))
        new = len(chart.clips) - 1

        def key(trigger: evfl.Trigger) -> tuple[float, int, int]:
            clip = chart.clips[trigger.clip]
            leave = trigger.type == LEAVE
            return (clip.start + clip.duration if leave else clip.start, 0 if leave else 1, trigger.clip)

        for trigger in (evfl.Trigger(new, ENTER), evfl.Trigger(new, LEAVE)):
            at = next((i for i, t in enumerate(chart.triggers) if key(t) > key(trigger)), len(chart.triggers))
            chart.triggers.insert(at, trigger)
        return

    def on(action: str) -> list[evfl.ActionEvent]:
        if action not in actor.actions:
            return []
        number = actor.actions.index(action)
        return [e for e in chart.events if isinstance(e, evfl.ActionEvent) and e.actor == index and e.action == number]

    anchors = on(BIND) or on(JOIN)
    if not anchors:
        raise PatchError(f"{document.name}: {actor.name} is never bound and never joins: no place for its effect")
    names = {event.name for event in chart.events}
    for number, anchor in enumerate(anchors):
        name = f"Clawshot_song_effect_{actor.secondary_name or 'prop'}_{index}_{number}"
        if name in names:
            raise PatchError(f"{document.name}: event name {name} is taken")
        chart.events.append(evfl.ActionEvent(name, index, emit, anchor.next, copy.deepcopy(EMIT_PARAMS)))
        anchor.next = len(chart.events) - 1


def prop_transform(event: str, renames: Sequence[Rename], hands: Sequence[HandRename] = ()) -> Callable[[bytes], bytes]:
    """The flow file ``event``'s transform: each rename made, each hand bind added, the written file read back."""

    def transform(data: bytes) -> bytes:
        if not renames and not hands:
            return data
        document = evfl.read(data)
        for part, actor, secondary, container in renames:
            rename_prop(document, part, actor, secondary, container)
        songs = sorted({(part, c, sec) for part, _, sec, c in renames if containers.is_song_container(c)})
        for part, container, secondary in songs:  # once per actor, after every rename (branches share a name)
            add_song_effect(document, part, container, secondary)
        for hand in hands:
            add_hand_bind(document, hand)
            if containers.is_song_container(hand.container):
                add_song_effect(document, FLOWCHART, hand.container, HAND)
        out = evfl.write(document)
        if evfl.read(out) != document:
            raise PatchError(f"{event}: the written flow does not read back as the renamed one")
        return out

    return transform


def plan_renames(
    props: Sequence["Prop"], moved: Mapping[str, str], *, events: Collection[str] | None = None
) -> tuple[dict[str, list[Rename]], list[str]]:
    """Event -> its renames, and the model actors the containers need, for ``moved`` (check -> the actor its grant
    gives, only checks whose item is not their vanilla one). Placed objects are left to their own step; ``events``
    (pilot only) keeps the props of those events alone."""
    renames: dict[str, list[Rename]] = {}
    models: set[str] = set()
    for prop in props:
        if prop.check not in moved or prop.part == PLACEMENT or (events is not None and prop.event not in events):
            continue
        model = containers.container_model(moved[prop.check])
        models.add(model)
        renames.setdefault(prop.event, []).append((prop.part, prop.actor, prop.secondary, container_name(model)))
    return {event: renames[event] for event in sorted(renames)}, sorted(models)


def plan_subflow_renames(
    renames: Mapping[str, Sequence[Rename]], read: Callable[[str], "evfl.EventFlowFile | None"]
) -> dict[str, list[Rename]]:
    """Subflow -> the renames its actors take: an actor of a flowchart prop's name (and secondary name) in a flow the
    prop's event calls takes the prop's container. ``read`` gives an event's flow file (None when there is none).
    Raises :class:`PatchError` when two events would give one subflow actor different containers."""
    chosen: dict[tuple[str, str, str], tuple[str, str]] = {}
    for event in sorted(renames):
        props = [
            (actor, secondary, container) for part, actor, secondary, container in renames[event] if part == FLOWCHART
        ]
        document = read(event) if props else None
        if document is None or document.flowchart is None:
            continue
        called = sorted(
            {e.flowchart for e in document.flowchart.events if getattr(e, "flowchart", "") not in ("", event, None)}
        )
        for name in called:
            sub = read(name)
            if sub is None or sub.flowchart is None:
                continue
            present = {(a.name, a.secondary_name) for a in sub.flowchart.actors}
            for actor, secondary, container in props:
                if (actor, secondary) not in present:
                    continue
                key = (name, actor, secondary)
                if key in chosen and chosen[key][0] != container:
                    raise PatchError(
                        f"{name}: {actor} would be {chosen[key][0]} for {chosen[key][1]} and {container} for {event}"
                    )
                chosen[key] = (container, event)
    out: dict[str, list[Rename]] = {}
    for (name, actor, secondary), (container, _) in sorted(chosen.items()):
        out.setdefault(name, []).append((FLOWCHART, actor, secondary, container))
    return out


def scene_actions(document: evfl.EventFlowFile, prop: "Prop") -> list[str]:
    """The scene animations ``document`` (``prop``'s flow, as the dump has it) plays on ``prop``, named as an effect
    user's actions name them: ``<prop.scene_as>/<ASName>`` for each ``EventPlayAS`` on the prop's actor (D20); none
    for a prop without ``scene_as`` (what it plays comes from its own set, such as Light Arrows' ``Rotate_GetDemo``).
    """
    if not prop.scene_as:
        return []
    chart = document.flowchart if prop.part == FLOWCHART else None
    if chart is None:
        raise PatchError(f"{prop.id}: scene_as on a prop without a flowchart")
    found = [i for i, a in enumerate(chart.actors) if (a.name, a.secondary_name) == (prop.actor, prop.secondary)]
    names = set()
    for event in chart.events:
        if not isinstance(event, evfl.ActionEvent) or event.actor not in found:
            continue
        if chart.actors[event.actor].actions[event.action] != PLAY_AS:
            continue
        name = (event.params or {}).get(AS_NAME)
        if not isinstance(name, str) or isinstance(name, evfl.Argument) or not name:
            raise PatchError(f"{prop.id}: {event.name} plays {name!r}, not a node name")
        names.add(f"{prop.scene_as}/{name}")
    if not names:
        raise PatchError(f"{prop.id}: scene_as {prop.scene_as!r} but the flow plays no {PLAY_AS} on it")
    return sorted(names)


def plan_scene_actions(
    props: Sequence["Prop"],
    moved: Mapping[str, str],
    read: Callable[[str], "evfl.EventFlowFile | None"],
    *,
    events: Collection[str] | None = None,
) -> list[str]:
    """The scene animations the seed's events play on song containers (:func:`scene_actions` of every prop with
    ``scene_as`` whose moved check gives a song), sorted: every song event user answers each of them (D20, as the
    played pilot A). ``read`` gives an event's flow file; ``events`` as in :func:`plan_renames`."""
    out: set[str] = set()
    for prop in props:
        if not prop.scene_as or prop.check not in moved or (events is not None and prop.event not in events):
            continue
        if not containers.is_song_container(container_name(containers.container_model(moved[prop.check]))):
            continue
        document = read(prop.event)
        if document is None:
            raise PatchError(f"{prop.id}: no flow file {prop.event}")
        out.update(scene_actions(document, prop))
    return sorted(out)


def plan_hands(
    hands: Sequence["HandBind"], moved: Mapping[str, str], rows: Mapping[str, Mapping]
) -> tuple[dict[str, list[HandRename]], list[str]]:
    """Event -> its hand binds, and the model actors their containers need, for ``moved`` (check -> the actor its grant
    gives, only checks whose item is not their vanilla one). Each bind's shift (D19) is :func:`hand_shift` of the
    hand's native item (``HandBind.item``) and the model its container shows (:func:`getitem.model_actor`: a song's
    container shows its ocarina's model fields), from the dump's ActorInfo ``rows``."""
    out: dict[str, list[HandRename]] = {}
    models: set[str] = set()
    for hand in hands:
        if hand.check not in moved:
            continue
        model = containers.container_model(moved[hand.check])
        models.add(model)
        shift = hand_shift(rows, hand.item, getitem.model_actor(moved[hand.check]))
        out.setdefault(hand.event, []).append(
            HandRename(hand.template, hand.target, hand.bone, hand.start, hand.end, container_name(model), shift)
        )
    return {event: out[event] for event in sorted(out)}, sorted(models)


def _chain(*transforms: Callable[[bytes], bytes]) -> Callable[[bytes], bytes]:
    def transform(data: bytes) -> bytes:
        for one in transforms:
            data = one(data)
        return data

    return transform


def native_inputs(actors: Iterable[str]) -> tuple[str, ...]:
    """Every romfs file :func:`seed_changes` and its transforms can read for any seed whose events give any of the
    item ``actors``, the dictionaries' pack included, so the app's working set (``clawshot.pack.source.working_files``)
    holds them: the flow versions list, the containers' inputs (:func:`containers.native_inputs`), and for each placed
    object (``event_props.toml``) its own pack and the pack of each model it can show. The event flows themselves are
    every ``Event/EventFlow/*.bfevfl.zs``, which the working set's patterns hold (the version a dump loads is in its
    versions list, so a flow's path is not known here)."""
    actors = sorted(set(actors))
    placed = sorted({prop.actor for prop in event_props.load().props if prop.part == PLACEMENT})
    return (
        FLOW_VERSIONS,
        *containers.native_inputs(actors),
        placed_models.ACTOR_INFO,
        placed_models.GAME_ACTOR_INFO,
        *(getitem.pack_path(actor) for actor in placed),
        *sorted({getitem.pack_path(getitem.model_actor(actor)) for actor in actors}),
    )


def seed_changes(
    romfs: str | Path, moved: Mapping[str, str], *, events: Collection[str] | None = None
) -> tuple[FileChanges, dict[str, NewFile]]:
    """The flow transforms, row transforms and container packs that show ``moved``'s items in their events, and the
    placed objects' own model members (``events``, pilot only, leaves the placed objects out)."""
    data = event_props.load()
    props = data.props
    renames, models = plan_renames(props, moved, events=events)
    moved_hands = [hand for hand in data.hands if hand.check in moved] if events is None else []
    placed = {
        prop.actor: getitem.model_actor(moved[prop.check])
        for prop in props
        if prop.part == PLACEMENT and prop.check in moved and events is None
    }
    if not renames and not placed and not moved_hands:
        return {}, {}
    romfs = Path(romfs)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    # D19: the dump's rows, which the container rows copy their model box from (containers.actor_info_transform)
    rows = {row["__RowId"]: row for row in read_romfs_byml(romfs, dicts, containers.ACTOR_INFO)} if moved_hands else {}
    hands, hand_models = plan_hands(moved_hands, moved, rows)
    models = sorted({*models, *hand_models})
    versions = {str(k): str(v) for k, v in read_romfs_byml(romfs, dicts, FLOW_VERSIONS)["Versions"].items()}
    files = flow_files(romfs, versions)

    def read(event: str) -> evfl.EventFlowFile | None:
        if event not in files:
            return None
        return evfl.read(dicts.decompress(files[event], (romfs / files[event]).read_bytes()))

    for event, extra in plan_subflow_renames(renames, read).items():
        renames[event] = sorted({*renames.get(event, []), *extra})
    out: dict[str, Callable[[bytes], bytes]] = {
        files[event]: prop_transform(event, renames.get(event, []), hands.get(event, []))
        for event in sorted({*renames, *hands})
    }
    actions = plan_scene_actions(props, moved, read, events=events)
    rows, packs = containers.changes(romfs, models, scene_actions=actions)
    out.update(rows)
    if placed:
        for actor, model in sorted(placed.items()):
            path = getitem.pack_path(model)
            model_pack = sarc.read(dicts.decompress(path, (romfs / path).read_bytes()))
            out[getitem.pack_path(actor)] = placed_models.pack_transform(actor, model_pack, model)
        for table, edit in (
            (placed_models.ACTOR_INFO, placed_models.actor_info_transform(placed)),
            (placed_models.GAME_ACTOR_INFO, placed_models.game_actor_info_transform(placed)),
        ):
            out[table] = _chain(out[table], edit) if table in out else edit
    return out, packs
