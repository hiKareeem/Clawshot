import random
import struct

import pytest

from clawshot.formats import evfl
from clawshot.formats.evfl import (
    NONE,
    ActionEvent,
    Actor,
    ActorIdentifier,
    Argument,
    Clip,
    Cut,
    EntryPoint,
    EventFlowFile,
    EvflError,
    FloatArray,
    Flowchart,
    ForkEvent,
    JoinEvent,
    ReturnEvent,
    SubFlowEvent,
    SubFlowSwitchEvent,
    SwitchEvent,
    Timeline,
    Trigger,
    Variable,
)


def flowchart_file() -> EventFlowFile:
    """A made-up flow with every event type, every parameter type the game uses, and entry point variables."""
    pouch = Actor(
        "PouchSystemActor",
        actions=["EventTriggerAddOrRemovePouchContent"],
        params={"EventMemberCreateMethod": 1, "IsBindNearestActor": False, "UseEventAS": "Default"},
    )
    npc = Actor(
        "Npc_Test",
        secondary_name="Second",
        argument_name="Arg",
        actions=["Talk", "Turn"],
        queries=["IsFlagOn"],
        entry_point=1,
        cut_number=2,
    )
    events = [
        SwitchEvent("Event0", actor=1, query=0, cases=[(0, 1), (1, 2)], params={"Flag": "Test_Flag"}),
        SubFlowEvent("Event1", "", "Give", next=3, params={"ActorName": "Item_Test"}),
        ForkEvent("Event2", join=5, forks=[3, 4]),
        ActionEvent("Event3", actor=1, action=1, next=5),
        ActionEvent(
            "Event4",
            actor=1,
            action=0,
            next=5,
            params={
                "Nested": {"Inner": 1.5, "Deeper": {"Bool": True}},
                "Position": FloatArray([1.0, -2.5, 0.25]),
                "Who": ActorIdentifier("Npc_Test", ""),
                "Count": -3,
            },
        ),
        JoinEvent("Event5", next=6),
        SubFlowSwitchEvent("Event6", "Other", "Check", cases=[(0xDEADBEEF, 8)], params={"Step": 2}),
        ActionEvent(
            "Event7",
            actor=0,
            action=0,
            params={"Actor": Argument("ActorName"), "Num": 1, "IsGetEvent": True},
        ),
        ReturnEvent("Event8", value=0xDEADBEEF),
        SubFlowSwitchEvent("Event9", "", "Check"),
    ]
    entry_points = [
        EntryPoint("Start", main_event=0, sub_flow_events=[1, 6, 9]),
        EntryPoint("Give", main_event=7, variables={"Done": Variable(evfl.T_BOOL, True)}),
        EntryPoint("Check", main_event=8, variables={"Count": Variable(evfl.T_INT, -1)}),
        EntryPoint("Empty"),
    ]
    return EventFlowFile("Test", Flowchart("Test", [pouch, npc], events, entry_points))


def timeline_file() -> EventFlowFile:
    actors = [
        Actor("Camera", actions=["Move", "Shake"], params={"Name": "Cam"}),
        Actor("Player", actions=["Walk"]),
    ]
    clips = [
        Clip(0.0, 30.0, actor=0, action=0, unknown=1, params={"Speed": 2.0}),
        Clip(30.0, 15.5, actor=1, action=0),
    ]
    return EventFlowFile(
        "Dm_Test",
        timeline=Timeline(
            "Dm_Test",
            duration=45.5,
            actors=actors,
            clips=clips,
            triggers=[Trigger(0, 1), Trigger(0, 2), Trigger(1, 1), Trigger(1, 2)],
            subtimelines=["Dm_Test_Effect"],
            cuts=[Cut(0.0, 0, "C01"), Cut(30.0, 1, "C02")],
        ),
    )


@pytest.mark.parametrize("make", [flowchart_file, timeline_file])
def test_write_reads_back_to_the_same_tree_and_bytes(make):
    data = evfl.write(make())
    back = evfl.read(data)
    assert back == make()
    assert evfl.write(back) == data
    relocation, size = struct.unpack_from("<4xII", data, 0x14)
    assert data[:8] == evfl.MAGIC and size == len(data) and data[relocation : relocation + 4] == b"RELT"


def test_parameter_types_survive_the_round_trip():
    back = evfl.read(evfl.write(flowchart_file()))
    params = back.flowchart.events[4].params
    assert type(params["Position"]) is FloatArray and params["Position"] == (1.0, -2.5, 0.25)
    assert type(params["Count"]) is int and type(params["Nested"]["Deeper"]["Bool"]) is bool
    assert type(params["Nested"]["Inner"]) is float
    assert type(back.flowchart.events[7].params["Actor"]) is Argument
    assert type(back.flowchart.events[0].params["Flag"]) is str
    assert back.flowchart.entry_point("Give").variables == {"Done": Variable(evfl.T_BOOL, True)}


def test_a_longer_item_name_moves_the_rest_of_the_file_and_reads_back():
    """The census's use: change one string parameter (a gift's item) and write the flow again."""
    tree = flowchart_file()
    before = evfl.write(tree)
    tree.flowchart.events[1].params["ActorName"] = "Item_A_Much_Longer_Actor_Name"
    after = evfl.write(tree)
    assert len(after) > len(before)
    back = evfl.read(after)
    assert back.flowchart.events[1].params == {"ActorName": "Item_A_Much_Longer_Actor_Name"}
    assert back == tree


def _lookup(entries, names, name):
    """The radix-tree search the game runs on a dictionary: descend while the tested bit grows, compare at the end."""
    key = name.encode()
    prev, cur = 0, entries[0][1]
    while (entries[prev][0] if prev else -1) < entries[cur][0] and cur:
        bit = entries[cur][0]
        k = bit >> 3
        side = key[-1 - k] >> (bit & 7) & 1 if k < len(key) else 0
        prev, cur = cur, entries[cur][1 + side]
    return cur if cur and names[cur - 1] == name else None


def test_every_dictionary_name_is_found_by_the_radix_search():
    rng = random.Random(7)
    for size in (1, 2, 3, 17, 60):
        names = list(
            {f"{rng.choice(['Event', 'Npc_', 'C', ''])}{rng.randrange(10 ** rng.randrange(1, 5))}" for _ in range(size)}
        )
        entries = evfl.dictionary_entries(names)
        assert entries[0][0] == 0xFFFFFFFF
        for index, name in enumerate(names, 1):
            assert _lookup(entries, names, name) == index, name
        assert _lookup(entries, names, "NotInTheDictionary") is None


def test_dictionary_refuses_a_name_twice():
    with pytest.raises(EvflError, match="twice"):
        evfl.dictionary_entries(["Event1", "Event2", "Event1"])


def test_entry_point_without_events_and_flowchart_without_actors():
    file = EventFlowFile("Bare", Flowchart("Bare", entry_points=[EntryPoint("Only")]))
    back = evfl.read(evfl.write(file))
    assert back == file
    assert back.flowchart.entry_point("Only").main_event == NONE


def _corrupt(data: bytes, offset: int, fmt: str, value) -> bytes:
    out = bytearray(data)
    struct.pack_into(fmt, out, offset, value)
    return bytes(out)


def test_read_refuses_files_it_does_not_understand():
    data = evfl.write(flowchart_file())
    with pytest.raises(EvflError, match="magic"):
        evfl.read(b"XFEVFL\0\0" + data[8:])
    with pytest.raises(EvflError, match="version"):
        evfl.read(_corrupt(data, 9, "<B", 3))
    with pytest.raises(EvflError, match="header says"):
        evfl.read(data + bytes(8))
    with pytest.raises(EvflError, match="exactly one"):
        evfl.read(_corrupt(data, 0x22, "<H", 1))
    with pytest.raises(EvflError, match="shorter"):
        evfl.read(data[:0x20])


def test_read_refuses_a_container_item_type_the_game_does_not_use():
    data = evfl.write(flowchart_file())
    assert evfl.read(data).flowchart.events[1].params == {"ActorName": "Item_Test"}
    # The first item of event 1's parameters, through the header's flowchart array and the flowchart's events.
    flowchart = struct.unpack_from("<Q", data, struct.unpack_from("<Q", data, 0x28)[0])[0]
    events = struct.unpack_from("<Q", data, flowchart + 0x30)[0]
    container = struct.unpack_from("<Q", data, events + 0x30 + 0x10)[0]
    item = struct.unpack_from("<Q", data, container + 0x10)[0]
    with pytest.raises(EvflError, match="unsupported type 6"):
        evfl.read(_corrupt(data, item, "<B", 6))


def test_write_refuses_what_it_cannot_lay_out():
    with pytest.raises(EvflError, match="exactly one"):
        evfl.write(EventFlowFile("Neither"))
    with pytest.raises(EvflError, match="not a parameter value"):
        evfl.write(EventFlowFile("X", Flowchart("X", events=[ActionEvent("E", 0, 0, params={"List": [1, 2]})])))
    timeline = timeline_file()
    timeline.timeline.triggers.pop()
    with pytest.raises(EvflError, match="two each"):
        evfl.write(timeline)
