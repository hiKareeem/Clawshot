"""Synthetic opening flow: ``intro`` starts the new-game loading entry after the movie, waiting for the load."""

import pytest

from clawshot.formats import evfl
from clawshot.formats.evfl import NONE, ActionEvent, Actor, EntryPoint, EventFlowFile, Flowchart, SwitchEvent
from clawshot.patch import gamedata
from clawshot.patch.gamedata import FastStartError, opening_without_movie

MOVIE, QUERY, FADE = 1, 2, 3


def opening_file() -> EventFlowFile:
    """An invented flow with the native contracts the edit relies on: the loading entry plays the movie, then
    switches on the load query whose only case fades in; a second entry (the reserved boot event) is unrelated."""
    actors = [
        Actor("EventSystemActor", actions=["EventTransition"]),
        Actor(
            "GameSystemActor",
            actions=["EventTriggerRequestAutoSave", "EventWait"],
            queries=["EventQueryBancChangeIsLoaded"],
        ),
        Actor("UISystemActor", actions=["EventEventFadeIn"]),
    ]
    events = [
        ActionEvent("Wake", 0, 0, 5, {"EventName": "Dm_Wake", "IsWaitEnd": True}),
        ActionEvent("Movie", 0, 0, QUERY, {"EventName": gamedata.OPENING_MOVIE, "IsWaitEnd": True}),
        SwitchEvent("Loaded", 1, 0, [(1, FADE)]),
        ActionEvent("FadeIn", 2, 0, 4, {"Length": 1}),
        ActionEvent("Settle", 1, 1, NONE, {"Frames": 120, "IsWaitEnd": True}),
        ActionEvent("Save", 1, 0, NONE),
    ]
    entries = [EntryPoint("Opening_Introduction", main_event=0), EntryPoint(gamedata.OPENING_LOADING, MOVIE)]
    return EventFlowFile("OpeningEvent", Flowchart("OpeningEvent", actors, events, entries))


def run_entry(fc: Flowchart, entry: str, loaded: list[int]) -> list[tuple]:
    """The actions and queries an entry point runs, the load query answering ``loaded`` in turn."""
    answers = iter(loaded)
    trace = []
    index = fc.entry_point(entry).main_event
    for _ in range(100):
        if index == NONE:
            return trace
        event = fc.events[index]
        actor = fc.actors[event.actor]
        if isinstance(event, ActionEvent):
            trace.append((actor.name, actor.actions[event.action], event.params))
            index = event.next
        else:
            value = next(answers)
            trace.append((actor.name, actor.queries[event.query], value))
            index = dict(event.cases)[value]
    raise AssertionError(f"{entry} does not end: {trace[-5:]}")


def test_loading_starts_at_the_load_query_and_waits_a_frame_while_loading():
    native = opening_file()
    document = evfl.read(opening_without_movie(evfl.write(native)))
    fc = document.flowchart
    wait = ("GameSystemActor", "EventWait", {"Frames": 1, "IsWaitEnd": True})
    poll = [("GameSystemActor", "EventQueryBancChangeIsLoaded", 0), wait]
    before = run_entry(native.flowchart, gamedata.OPENING_LOADING, [1])
    after = run_entry(fc, gamedata.OPENING_LOADING, [0, 0, 1])
    assert before[0] == ("EventSystemActor", "EventTransition", native.flowchart.events[MOVIE].params)
    assert after == [*poll, *poll, *before[1:]]
    assert run_entry(fc, gamedata.OPENING_LOADING, [1]) == before[1:]
    assert all(gamedata.OPENING_MOVIE not in repr(getattr(e, "params", None)) for e in fc.events)


def test_everything_else_stays_native():
    native = opening_file()
    fc = evfl.read(opening_without_movie(evfl.write(native))).flowchart
    assert fc.actors == native.flowchart.actors  # no new actor, action or query
    assert len(fc.events) == len(native.flowchart.events)  # the movie's slot is the wait: no orphan event
    changed = [i for i, (a, b) in enumerate(zip(fc.events, native.flowchart.events, strict=True)) if a != b]
    assert changed == [MOVIE, QUERY]
    assert fc.events[MOVIE] == ActionEvent(gamedata.OPENING_WAIT, 1, 1, QUERY, {"Frames": 1, "IsWaitEnd": True})
    assert fc.events[QUERY].cases == [(0, MOVIE), (1, FADE)]
    assert fc.entry_point("Opening_Introduction") == native.flowchart.entry_point("Opening_Introduction")
    assert fc.entry_point(gamedata.OPENING_LOADING).main_event == QUERY


def _other_movie(fc):
    fc.events[MOVIE].params["EventName"] = "Dm_Other"


def _query_has_case_zero(fc):
    fc.events[QUERY].cases.insert(0, (0, FADE))


def _movie_reached_twice(fc):
    fc.events[5].next = MOVIE


def _no_wait_action(fc):
    fc.actors[1].actions.remove("EventWait")
    fc.events[4].action = 0


def _other_flowchart(fc):
    fc.name = "OtherEvent"


@pytest.mark.parametrize(
    "change,message",
    [
        (_other_movie, "changed native"),
        (_query_has_case_zero, "changed native"),
        (_no_wait_action, "changed native"),
        (_movie_reached_twice, r"also reached from \['Save'\]"),
        (_other_flowchart, "expected the OpeningEvent flowchart"),
    ],
)
def test_a_changed_native_opening_is_refused(change, message):
    document = opening_file()
    change(document.flowchart)
    with pytest.raises(FastStartError, match=message):
        opening_without_movie(evfl.write(document))


def test_unknown_flow_edits_are_refused():
    text = '[setting.a]\ndefault = false\nskips = "x"\nstate = "y"\nsource = "z"\nflow_edits = ["outro"]'
    with pytest.raises(FastStartError, match=r"unknown flow edits \['outro'\]"):
        gamedata.loads(text)
