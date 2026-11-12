"""Apply the skipped tree talk only after kept Mido's native equipment/clear route.

Keep the early quest state, scheduled Talk entry, initialization and per-entry subflow
registrations native. A cross-entry wrapper hung in game (r13-fast-start.md): Event222
was not registered by the later entry and starts with a synchronous blocker wait.
"""

from clawshot.formats import evfl
from clawshot.patch.plan import PatchError

FLOW = "Event/EventFlow/Npc_Kokiri_Mido_Child.bfevfl.zs"
BLOCKER = "KokiriForest_Npc_Kokiri_Mido_Child_Blocker"
SEEN_TREE = "HavePlayedEvent.Dm_Kokiri_0070"
MOUTH_OPEN = "KokiriForest_Meet_DekuTree_OpenDekuTreeMouth"


def complete_deku_meeting(data: bytes) -> bytes:
    """Retain native Talk/clear; its terminal Step03 supplies the skipped talk's state instead."""
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != "Npc_Kokiri_Mido_Child":
        raise PatchError("fast start: expected child Mido flowchart")
    events = {event.name: (index, event) for index, event in enumerate(fc.events)}
    required = ("Event26", "Event32", "Event33", "Event48", "Event0")
    if any(name not in events for name in required):
        raise PatchError("fast start: missing native Mido clear tail")
    _, clear = events["Event26"]
    end_index, end = events["Event32"]
    talk1_index, talk1 = events["Event33"]
    talk2_index, talk2 = events["Event48"]
    step_index, step = events["Event0"]
    if (
        not all(isinstance(event, evfl.ActionEvent) for event in (clear, end, talk1, talk2, step))
        or clear.params != {"Index": -1, "GameDataName": BLOCKER, "Value": False}
        or clear.next != end_index
        or fc.actors[clear.actor].name != "GameDataActor"
        or fc.actors[clear.actor].actions[clear.action] != "EventTriggerSetGameDataBool"
        or fc.actors[end.actor].name != "Npc_Kokiri_Mido_Child"
        or fc.actors[end.actor].actions[end.action] != "EventNpcBlockerEndBlockerAI"
        or end.next != talk1_index
        or talk1.actor != clear.actor
        or talk1.action != clear.action
        or talk1.next != talk2_index
        or talk2.actor != clear.actor
        or talk2.action != clear.action
        or talk2.next != step_index
        or fc.actors[step.actor].name != "ChallengeSystemActor"
        or fc.actors[step.actor].actions[step.action] != "EventExecuteProgressChallengeStep"
        or step.params
        != {
            "ChallengeName": "Meet_DekuTree",
            "IsWaitEnd": True,
            "IsIgnoreChallengeProgressUI": False,
            "StepName": "Step03",
            "IsIgnoreCompletedChallenge": False,
        }
        or step.next != evfl.NONE
    ):
        raise PatchError(
            f"fast start: changed native Mido clear tail: {clear!r}, {end!r}, {talk1!r}, {talk2!r}, {step!r}"
        )
    first = len(fc.events)
    # Match the tree scenes' order: seen 0070, meeting Complete, next quest GoInside, mouth open.
    fc.events.extend(
        [
            evfl.ActionEvent(
                "ClawshotDekuSeen",
                clear.actor,
                clear.action,
                step_index,
                {"GameDataName": SEEN_TREE, "Index": -1, "Value": True},
            ),
            evfl.ActionEvent(
                "ClawshotDekuGoInside",
                step.actor,
                step.action,
                first + 2,
                {**step.params, "ChallengeName": "Get_StoneOfForest", "StepName": "GoInside"},
            ),
            evfl.ActionEvent(
                "ClawshotDekuMouth",
                clear.actor,
                clear.action,
                evfl.NONE,
                {"GameDataName": MOUTH_OPEN, "Index": -1, "Value": True},
            ),
        ]
    )
    talk2.next = first
    step.params = {**step.params, "StepName": "Complete"}
    step.next = first + 1
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError("fast start: Mido clear tail failed read-back")
    return result
