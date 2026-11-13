"""Darunia's Joy follows its own source, so opening Dodongo's Cavern another way cannot skip it.

Native facts (plans/03-game-data.md section 48): after a recommended Saria's Song and the dance,
``Get_StoneOfFire`` Event39 asks ``Get_StoneOfFire_IsAfter_SariaMelodyPlay_Exp``. True repeats the
dance reaction (Event42); false transitions to ``Dm_Goron_0030``, whose C10 Event127 hands over the
gift and whose C11 Event121 advances Fire to ``DodongoCavernOpne``. The Death Mountain boulder
(``DungeonStart``), the boss entry and its defeat all pass that cutoff without the gift.

Event39 asks the cutscene's own saved ``HavePlayedEvent.Dm_Goron_0030`` instead, written right after
Event127, so any reward there (vanilla, shuffled, or a hand-over a later step bypasses while keeping
Event127's next) completes the source. Event121 and its progress notice run only while Fire is before
``DodongoCavernOpne``, so later steps are never written back. Event127's grant, every entry's
registrations, the song requirement and the cutscene's tail stay native.
"""

from clawshot.formats import evfl
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

STONE_FLOW = "Event/EventFlow/Get_StoneOfFire.bfevfl.zs"
MOVIE_FLOW = "Event/EventFlow/Dm_Goron_0030.bfevfl.zs"
SOURCE = "HavePlayedEvent.Dm_Goron_0030"  # native saved Bool: default false, reset type 8, progress.sav
CUTOFF = "Get_StoneOfFire_IsAfter_SariaMelodyPlay_Exp"  # true from DodongoCavernOpne on
PREFIX = "ClawshotDarunia"

GAME_DATA_ACTOR = "GameDataActor"
SET_BOOL = "EventTriggerSetGameDataBool"
READ_BOOL = "EventQueryIsGameDataBool"
READ_EXPRESSION = "EventQueryIsGameDataBoolExp"
# The cutscene's system actors and the GameDataActor of the native Dm_ flows that have one carry these.
SYSTEM_ACTOR_PARAMS = {
    "EventMemberCreateMethod": 0,
    "IsBindNearestActor": False,
    "IsGrounding": False,
    "IsWorld": False,
    "UseEventModelAnime": "使用しない",
    "UseEventAS": "使用しない",
}
STEP_WRITE = {
    "IsWaitEnd": True,
    "IsIgnoreCompletedChallenge": False,
    "IsIgnoreChallengeProgressUI": False,
    "ChallengeName": "Get_StoneOfFire",
    "StepName": "DodongoCavernOpne",
}
STEP_NOTICE = {"IsFirstStep": False, "ChallengeName": "Get_StoneOfFire"}


def _targets(event: evfl.Event) -> list[int]:
    targets = [getattr(event, "next", evfl.NONE), *(target for _, target in getattr(event, "cases", ()))]
    if isinstance(event, evfl.ForkEvent):
        targets += [*event.forks, event.join]
    return [target for target in targets if target != evfl.NONE]


def _callers(fc: evfl.Flowchart, index: int) -> list[str]:
    """The events that lead to ``index``, and the entries that start there."""
    events = [event.name for event in fc.events if index in _targets(event)]
    return events + [f"entry {entry.name}" for entry in fc.entry_points if entry.main_event == index]


def _find(fc: evfl.Flowchart, names: tuple[str, ...]) -> dict[str, int]:
    index = {event.name: i for i, event in enumerate(fc.events)}
    if missing := [name for name in names if name not in index]:
        raise PatchError(f"Darunia: {fc.name} lacks native events {missing}")
    if any(event.name.startswith(PREFIX) for event in fc.events):
        raise PatchError(f"Darunia: {fc.name} is already patched")
    return {name: index[name] for name in names}


def _op(fc: evfl.Flowchart, event: evfl.Event) -> str | None:
    if not isinstance(event, evfl.ActionEvent | evfl.SwitchEvent):
        return None
    actor = fc.actors[event.actor]
    name = actor.actions[event.action] if isinstance(event, evfl.ActionEvent) else actor.queries[event.query]
    return f"{actor.name}{'/' + actor.secondary_name if actor.secondary_name else ''}.{name}"


def _slot(names: list[str], name: str) -> int:
    if name not in names:
        names.append(name)
    return names.index(name)


def _written(document: evfl.EventFlowFile, path: str) -> bytes:
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError(f"Darunia: {path} does not read back as the edited flow")
    return result


def gift_gate(data: bytes) -> bytes:
    """``Get_StoneOfFire``: the danced song reaches the gift cutscene until that cutscene's source is recorded."""
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != "Get_StoneOfFire":
        raise PatchError(f"Darunia: {STONE_FLOW} holds no Get_StoneOfFire flowchart")
    at = _find(fc, ("Event39", "Event42", "Event31", "Event185"))
    gate, gift, dance = fc.events[at["Event39"]], fc.events[at["Event31"]], fc.events[at["Event185"]]
    callers = _callers(fc, at["Event39"])
    if (
        not isinstance(gate, evfl.SwitchEvent)
        or _op(fc, gate) != f"{GAME_DATA_ACTOR}.{READ_EXPRESSION}"
        or gate.params != {"GameDataName": CUTOFF}
        or gate.cases != [(0, at["Event42"]), (1, at["Event31"])]
        or not isinstance(gift, evfl.ActionEvent)
        or _op(fc, gift) != "EventSystemActor.EventTransition"
        or (gift.params or {}).get("EventName") != "Dm_Goron_0030"
        or gift.next != evfl.NONE
        or not isinstance(dance, evfl.ActionEvent)
        or _op(fc, dance) != "EventSystemActor.EventTransition"
        or (dance.params or {}).get("EventName") != "Dm_Goron_0025"
        or dance.next != at["Event39"]
        or callers != ["Event185"]
    ):
        raise PatchError(f"Darunia: changed native gift gate: {gate!r}, {gift!r}, {dance!r}, callers {callers}")
    # Same cases: true (played) keeps the repeat reaction, false (not played) still transitions to the gift.
    gate.query = _slot(fc.actors[gate.actor].queries, READ_BOOL)
    gate.params = {"GameDataName": SOURCE, "Index": -1}
    return _written(document, STONE_FLOW)


def _game_data_actor(fc: evfl.Flowchart) -> int:
    found = [i for i, actor in enumerate(fc.actors) if actor.name == GAME_DATA_ACTOR and not actor.secondary_name]
    if len(found) > 1 or any(fc.actors[i].entry_point != evfl.NONE for i in found):
        unexpected = [fc.actors[i] for i in found]
        raise PatchError(f"Darunia: {fc.name} has unexpected {GAME_DATA_ACTOR} actors: {unexpected}")
    if found:
        return found[0]
    # The native cutscene has none: add one shaped like the system actors it already binds.
    fc.actors.append(evfl.Actor(GAME_DATA_ACTOR, params=dict(SYSTEM_ACTOR_PARAMS)))
    return len(fc.actors) - 1


def source_once(data: bytes) -> bytes:
    """``Dm_Goron_0030``: record the source after the hand-over; advance Fire only from before the cavern opens."""
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != "Dm_Goron_0030":
        raise PatchError(f"Darunia: {MOVIE_FLOW} holds no Dm_Goron_0030 flowchart")
    at = _find(fc, ("Event127", "Event130", "Event121", "Event128", "Event202"))
    grant, before, step, notice = (fc.events[at[name]] for name in ("Event127", "Event130", "Event121", "Event128"))
    gift_entries = [entry for entry in fc.entry_points if entry.name == "C10"]
    challenge = [actor for actor in fc.actors if actor.name == "ChallengeSystemActor"]
    params = getattr(grant, "params", None) or {}
    callers = _callers(fc, at["Event121"])
    if (
        not isinstance(grant, evfl.SubFlowEvent)
        or (grant.flowchart, grant.entry_point, grant.next) != ("Dm_SY_GetInEvent", "GetInEvent_Goron", evfl.NONE)
        or params.keys() != {"ActorName"}
        or not isinstance(params["ActorName"], str)
        or isinstance(params["ActorName"], evfl.Argument)
        or len(gift_entries) != 1
        or at["Event127"] not in gift_entries[0].sub_flow_events
    ):
        raise PatchError(f"Darunia: changed native hand-over: {grant!r}, entries {gift_entries!r}")
    if (
        not isinstance(step, evfl.ActionEvent)
        or _op(fc, step) != "ChallengeSystemActor.EventExecuteProgressChallengeStep"
        or step.params != STEP_WRITE
        or step.next != at["Event128"]
        or not isinstance(notice, evfl.ActionEvent)
        or _op(fc, notice) != "ChallengeSystemActor.EventTriggerShowChallengeProgressUI"
        or notice.params != STEP_NOTICE
        or notice.next != at["Event202"]
        or not isinstance(before, evfl.ActionEvent)
        or callers != ["Event130"]
        or [actor.params for actor in challenge] != [SYSTEM_ACTOR_PARAMS]
    ):
        raise PatchError(
            f"Darunia: changed native Fire step tail: {before!r}, {step!r}, {notice!r}, callers {callers}, "
            f"challenge actors {challenge!r}"
        )
    actor = _game_data_actor(fc)
    first = len(fc.events)
    fc.events.append(
        evfl.ActionEvent(
            f"{PREFIX}SourceOnce",
            actor,
            _slot(fc.actors[actor].actions, SET_BOOL),
            grant.next,
            {"GameDataName": SOURCE, "Index": -1, "Value": True},
        )
    )
    grant.next = first
    # True (Fire already at or past DodongoCavernOpne): skip the write and its notice, keep the camera tail.
    fc.events.append(
        evfl.SwitchEvent(
            f"{PREFIX}BeforeCavern",
            actor,
            _slot(fc.actors[actor].queries, READ_EXPRESSION),
            [(0, notice.next), (1, at["Event121"])],
            {"GameDataName": CUTOFF},
        )
    )
    before.next = first + 1
    return _written(document, MOVIE_FLOW)


def changes() -> FileChanges:
    """Every seed's Darunia transforms. Compose after gift swaps of Event127 and before any guard that replaces it."""
    return {STONE_FLOW: gift_gate, MOVIE_FLOW: source_once}
