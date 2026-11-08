"""Story wrappers stay on the actual opened chest; the unsafe sword equipment scene does not."""

from pathlib import Path

import pytest

from clawshot.formats import byml, evfl, zsdic
from clawshot.generate import Settings
from clawshot.patch import make_seed, write_seed
from clawshot.patch.items import load as load_items

pytestmark = pytest.mark.dump

STATEFUL = (
    "SubEvent_GetIceArrow_OpenTBox",
    "InsideGanonCastle_Get_Gauntlet_Gold",
    "SageOfSpirit_NaboorIsTakenAway",
    "SageOfWater_MelodyGet_Water",
)


@pytest.fixture(scope="module")
def chest_overlay(romfs, tmp_path_factory):
    output = make_seed(romfs, 7, Settings())
    target = tmp_path_factory.mktemp("chest-events") / "seed"
    write_seed(output, romfs, target)
    return output, target, zsdic.Dictionaries.from_romfs(romfs)


@pytest.mark.parametrize("event_name", STATEFUL)
def test_changed_chest_keeps_its_story_wrapper_and_placed_reward(chest_overlay, event_name):
    output, target, dictionaries = chest_overlay
    changes = [c for c in output.plan.changes if c.kept_event and c.kept_event.name == event_name]
    assert changes, (event_name, output.plan.as_dict())
    actors = load_items()
    for change in changes:
        placed = actors.actor(output.seed.placements[change.location])
        assert placed != change.old_actor
        for path in change.files:
            tree = byml.read(dictionaries.decompress(path, (target / "romfs" / path).read_bytes()))
            chest = next(a for a in tree["Actors"] if a.get("Hash") == change.id)
            assert chest["Dynamic"]["GetEventName"] == event_name
            assert chest["Dynamic"]["Drop__DropActor"] == placed
        print(event_name, change.id, change.old_actor, "->", placed, "wrapper retained")


def test_sword_wrapper_is_removed_without_removing_other_story_events(chest_overlay):
    output, target, dictionaries = chest_overlay
    removed = [c for c in output.plan.changes if c.event]
    assert {c.event.name for c in removed} == {"Get_StoneOfForest_GetSword"}
    for change in removed:
        for path in change.files:
            tree = byml.read(dictionaries.decompress(path, (target / "romfs" / path).read_bytes()))
            chest = next(a for a in tree["Actors"] if a.get("Hash") == change.id)
            assert "GetEventName" not in chest["Dynamic"]
            assert chest["Dynamic"]["Drop__DropActor"] == change.new_actor


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
