"""The opening without its movie on the dump (``-m dump``): only the loading entry's start changes; the reserved
boot event (Navi wakes Link, time, first quest step, autosave) and every other event stay native."""

import pytest
from test_fast_start_intro import run_entry

from clawshot.formats import evfl, zsdic
from clawshot.patch import gamedata

pytestmark = pytest.mark.dump
BOOT_EVENT = "Opening_Introduction"


@pytest.fixture(scope="module")
def flows(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    native = dicts.decompress(gamedata.OPENING_FLOW, (romfs / gamedata.OPENING_FLOW).read_bytes())
    return evfl.read(native).flowchart, evfl.read(gamedata.opening_without_movie(native)).flowchart


def reachable(fc: evfl.Flowchart, name: str) -> set[int]:
    entry = fc.entry_point(name)
    seen, pending = set(), [entry.main_event, *entry.sub_flow_events]
    while pending:
        index = pending.pop()
        if index == evfl.NONE or index in seen:
            continue
        seen.add(index)
        event = fc.events[index]
        pending += [target for _, target in getattr(event, "cases", [])]
        pending += [getattr(event, "next", evfl.NONE), getattr(event, "join", evfl.NONE), *getattr(event, "forks", [])]
    return seen


def test_native_loading_runs_without_the_movie(flows):
    native, changed = flows
    before = run_entry(native, gamedata.OPENING_LOADING, [1])
    after = run_entry(changed, gamedata.OPENING_LOADING, [0, 1])
    print("native:", before, "\nchanged:", after, sep="\n")
    assert before[0][:2] == ("EventSystemActor", "EventTransition")
    assert before[0][2]["EventName"] == gamedata.OPENING_MOVIE
    poll = [("GameSystemActor", "EventQueryBancChangeIsLoaded", 0), ("GameSystemActor", "EventWait", after[1][2])]
    assert after[1][2] == {"Frames": 1, "IsWaitEnd": True}
    assert after == [*poll, *before[1:]]


def test_only_the_loading_start_changes(flows):
    native, changed = flows
    movie = native.entry_point(gamedata.OPENING_LOADING).main_event
    query = changed.entry_point(gamedata.OPENING_LOADING).main_event
    assert changed.actors == native.actors  # no new actor, action or query
    assert [i for i, (a, b) in enumerate(zip(native.events, changed.events, strict=True)) if a != b] == [movie, query]
    assert [e.name for e in changed.entry_points] == [e.name for e in native.entry_points]
    for old, new in zip(native.entry_points, changed.entry_points, strict=True):
        if old.name != gamedata.OPENING_LOADING:
            assert new == old
    assert not {movie, query} & reachable(native, BOOT_EVENT)
    assert reachable(changed, BOOT_EVENT) == reachable(native, BOOT_EVENT)
    assert all(gamedata.OPENING_MOVIE not in repr(getattr(e, "params", None)) for e in changed.events)
