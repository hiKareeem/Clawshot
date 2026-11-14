"""Invented source callbacks: Fire may advance, never lose a later step.

Native dump proofs exercise the real room/door/song callbacks separately. These
fixtures are constructed here, not extracted or shortened game files.
"""

import pytest
from test_story_steps_darunia import PLAY, STEP, STEPS, movie_flow, play, stone_flow

from clawshot.formats import evfl
from clawshot.patch import darunia

ROOM = "Get_StoneOfFire_MeetDarnia"
MEADOW = "Get_StoneOfFire_MelodyGet_Saria"
LETTER = "Get_StoneOfFire_KakarikoVillageLetter"
TRAIL = "Get_StoneOfFire_DeathMtTrailIn"
SENDOFF = "DoorOfTime_SendOff"
DOOR_FLOW = "Event/EventFlow/DoorOfTime.bfevfl.zs"
SOURCES = (
    ("Get_StoneOfFire", ROOM, "DarniaRoomKokiriTalk"),
    ("Get_StoneOfFire", MEADOW, "SariaMelodyPlay"),
    ("Get_StoneOfFire", LETTER, "DeathMtTrailIn"),
    ("Get_StoneOfFire", TRAIL, "DeathMtTrailNpc"),
    ("DoorOfTime", SENDOFF, "KakarikoVillageNpc"),
)


def fire_stone():
    document = stone_flow()
    fc = document.flowchart
    challenge = len(fc.actors)
    fc.actors.append(
        evfl.Actor(
            "ChallengeSystemActor",
            actions=["EventExecuteProgressChallengeStep", "EventTriggerShowChallengeProgressUI"],
        )
    )
    for event, target, entry, tail in (
        ("Event169", "DarniaRoomKokiriTalk", ROOM, "Event146"),
        ("Event86", "SariaMelodyPlay", MEADOW, None),
        ("Event152", "DeathMtTrailIn", LETTER, "Event88"),
        ("Event156", "DeathMtTrailNpc", TRAIL, None),
    ):
        index = len(fc.events)
        fc.events.append(
            evfl.ActionEvent(
                event,
                challenge,
                0,
                index + 1 if tail else evfl.NONE,
                {**darunia.STEP_WRITE, "StepName": target},
            )
        )
        fc.entry_points.append(evfl.EntryPoint(entry, index))
        if tail:
            fc.events.append(evfl.ActionEvent(tail, challenge, 1, evfl.NONE, dict(darunia.STEP_NOTICE)))
    return document


def fire_door():
    return evfl.EventFlowFile(
        "FireSendoffTest",
        evfl.Flowchart(
            "DoorOfTime",
            [evfl.Actor("ChallengeSystemActor", actions=["EventExecuteProgressChallengeStep"])],
            [evfl.ActionEvent("Event62", 0, 0, evfl.NONE, {**darunia.STEP_WRITE, "StepName": "KakarikoVillageNpc"})],
            [evfl.EntryPoint(SENDOFF, 0)],
        ),
    )


def patched_sources():
    transforms = darunia.changes()
    return (
        evfl.read(transforms[darunia.STONE_FLOW](evfl.write(fire_stone()))),
        evfl.read(transforms[darunia.MOVIE_FLOW](evfl.write(movie_flow()))),
        evfl.read(transforms[DOOR_FLOW](evfl.write(fire_door()))),
    )


@pytest.mark.parametrize("flow,entry,target", SOURCES)
@pytest.mark.parametrize("boundary", ("before", "equal", "after", "complete"))
def test_a_source_advances_to_its_step_but_cannot_undo_later_progress(flow, entry, target, boundary):
    target_index = STEPS.index(target)
    step = STEPS[
        {
            "before": target_index - 1,
            "equal": target_index,
            "after": target_index + 1,
            "complete": STEPS.index("Complete"),
        }[boundary]
    ]
    stone, movie, door = patched_sources()
    after, result = play(stone, movie, step=step, extra=(door,), entries=((flow, entry),))
    expected = target if STEPS.index(step) <= target_index else step
    assert after[STEP] == expected
    assert result["writes"] == ([(step, target)] if STEPS.index(step) <= target_index else [])
    if STEPS.index(step) <= target_index:
        native_state, native_result = play(
            fire_stone(), movie_flow(), step=step, extra=(fire_door(),), entries=((flow, entry),)
        )
        assert after == native_state
        assert (result["rewards"], result["writes"], result["notices"]) == (
            native_result["rewards"],
            native_result["writes"],
            native_result["notices"],
        )


@pytest.mark.parametrize("step", ("DungeonStart", "BossBattle", "EscapeDungeon", "Complete"))
def test_late_room_talk_then_dance_keeps_the_quest_and_collects_the_source(step):
    stone, movie, _ = patched_sources()
    after, result = play(stone, movie, step=step, entries=(("Get_StoneOfFire", ROOM), ("Get_StoneOfFire", PLAY)))
    assert after[STEP] == step
    assert after[darunia.SOURCE] is True
    assert result["rewards"] == ["Item_Gauntlet_Goron"]
    assert result["writes"] == []
