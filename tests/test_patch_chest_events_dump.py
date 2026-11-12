"""Native story-state evidence: no equipment replay in shuffled rewards, and songs remain separate gifts."""

from pathlib import Path

import pytest

from clawshot.formats import evfl, zsdic

pytestmark = pytest.mark.dump


def events_from(chart, entry):
    todo = [chart.entry_point(entry).main_event]
    visited = set()
    while todo:
        index = todo.pop()
        if index == evfl.NONE or index in visited:
            continue
        visited.add(index)
        event = chart.events[index]
        yield event
        if isinstance(event, (evfl.SwitchEvent, evfl.SubFlowSwitchEvent)):
            todo.extend(i for _, i in event.cases)
        elif isinstance(event, evfl.ForkEvent):
            todo.extend([*event.forks, event.join])
        else:
            todo.append(getattr(event, "next", evfl.NONE))


def flow(romfs, name):
    path = f"Event/EventFlow/{name}.bfevfl.zs"
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    return evfl.read(dictionaries.decompress(path, (Path(romfs) / path).read_bytes())).flowchart


def test_removed_sword_wrapper_does_not_write_persistent_story_state(romfs):
    for name, entry in (("Get_StoneOfForest", "GetSword"), ("Dm_Kokiri_0063", "C01")):
        chart = flow(romfs, name)
        writes = []
        for event in events_from(chart, entry):
            if not isinstance(event, evfl.ActionEvent):
                continue
            actor = chart.actors[event.actor]
            action = actor.actions[event.action]
            if (actor.name == "GameDataActor" and "SetGameData" in action) or (
                actor.name == "ChallengeSystemActor" and "ProgressChallengeStep" in action
            ):
                writes.append((event.name, actor.name, action, event.params))
        assert not writes, (name, entry, writes)


def test_water_song_is_a_gift_inside_the_retained_chest_event(romfs):
    chart = flow(romfs, "Dm_MelodyGet_Water")
    grants = [
        event
        for event in events_from(chart, "C15")
        if isinstance(event, evfl.SubFlowEvent)
        and event.flowchart == "GetPouchContent"
        and event.entry_point == "GetPouchContentByActorName"
    ]
    assert [(e.name, e.params.get("ActorName")) for e in grants] == [("Event29", "Item_Melody_WaterSerenade")]
