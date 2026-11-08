import pytest

from clawshot.census import definitions, gifts
from clawshot.census.gifts import DIRECT, EVENT_GIFT, NPC_GIFT, SONG, GiftError
from clawshot.formats.evfl import (
    ActionEvent,
    Actor,
    Argument,
    EntryPoint,
    Flowchart,
    SubFlowEvent,
    SwitchEvent,
)

POUCH = Actor(gifts.GIVE_ACTOR, actions=[gifts.GIVE_ACTION])


def give(name, item, num=1, next=0xFFFF):
    return ActionEvent(name, actor=0, action=0, next=next, params={"Actor": item, "Num": num})


def flows():
    """A wrapper chain like the game's: GetPouch gives its argument, Wrapper passes its own argument on, and the
    NPC and cutscene flows call them with literal items."""
    get_pouch = Flowchart("GetPouch", [POUCH], [give("Event0", Argument("ActorName"))], [EntryPoint("ByName", 0)])
    wrapper = Flowchart(
        "Wrapper",
        [],
        [SubFlowEvent("Event0", "GetPouch", "ByName", params={"ActorName": Argument("Item")})],
        [EntryPoint("Hand", 0)],
    )
    npc = Flowchart(
        "Npc_Test",
        [POUCH, Actor("Npc_Test", queries=["IsDone"])],
        [
            SwitchEvent("Event0", actor=1, query=0, cases=[(0, 1), (1, 2)]),
            SubFlowEvent("Event1", "Wrapper", "Hand", params={"Item": "Item_Bottle"}),
            give("Event2", "Item_Trade", num=-1, next=3),  # taking a trade item is no gift
            give("Event3", "Obj_Rupee_Red", next=5),
            SubFlowEvent("Event4", "", "Local", params={"Item": "Item_Unused"}),  # Local gives nothing
            SubFlowEvent("Event5", "Wrapper", "Hand", params={"Item": Argument("Passed")}),  # not literal
        ],
        [EntryPoint("Talk", 0), EntryPoint("Local", 4)],
    )
    cutscene = Flowchart(
        "Dm_Test",
        [],
        [
            SubFlowEvent("Event0", "GetPouch", "ByName", params={"ActorName": "Item_Stone_Forest"}),
            SubFlowEvent("Event1", "GetPouch", "ByName", params={"ActorName": "Item_Melody_SariaSong"}),
        ],
        [EntryPoint("C01", 0)],
    )
    scrub = Flowchart("Enemy_Scrub_Business_Common", [POUCH], [give("Event0", "Shop_Heart")], [EntryPoint("Buy", 0)])
    return {f.name: f for f in (get_pouch, wrapper, npc, cutscene, scrub)}


def files(fcs):
    return {name: f"Event/EventFlow/{name}.bfevfl.zs" for name in fcs}


def test_wrappers_are_found_through_argument_passing():
    found = gifts.givers(flows())
    assert found[("GetPouch", "ByName")] == {"ActorName"}
    assert found[("Wrapper", "Hand")] == {"Item"}
    assert found[("Npc_Test", "Local")] == set()
    assert found[("Npc_Test", "Talk")] == {"Passed"}  # Event5 passes its own argument on


def test_gifts_are_literal_items_passed_to_a_giver_or_the_action():
    fcs = flows()
    rows = [
        (g.id, g.kind, g.entries, g.call, g.param, g.vanilla_item, g.area)
        for g in gifts.find_gifts(fcs, files(fcs), {"Npc_Test": "KokiriForest"})
    ]
    assert rows == [
        ("Dm_Test/Event0", EVENT_GIFT, ("C01",), "GetPouch:ByName", "ActorName", "Item_Stone_Forest", ""),
        ("Dm_Test/Event1", SONG, (), "GetPouch:ByName", "ActorName", "Item_Melody_SariaSong", ""),
        ("Npc_Test/Event1", NPC_GIFT, ("Talk",), "Wrapper:Hand", "Item", "Item_Bottle", "KokiriForest"),
        ("Npc_Test/Event3", NPC_GIFT, ("Talk",), DIRECT, "Actor", "Obj_Rupee_Red", "KokiriForest"),
    ]


def test_a_step_giving_two_items_has_no_single_id():
    fcs = flows()
    two = Flowchart("Two", [POUCH], [give("Event0", Argument("A"))], [EntryPoint("Both", 0)])
    fcs["Two"] = two
    fcs["Twice"] = Flowchart(
        "Twice",
        [],
        [SubFlowEvent("Event0", "Wrapper2", "Hand", params={"X": "Item_A", "Y": "Item_B"})],
        [EntryPoint("E", 0)],
    )
    fcs["Wrapper2"] = Flowchart(
        "Wrapper2",
        [],
        [
            SubFlowEvent("Event0", "Two", "Both", params={"A": Argument("X")}, next=1),
            SubFlowEvent("Event1", "Two", "Both", params={"A": Argument("Y")}),
        ],
        [EntryPoint("Hand", 0)],
    )
    with pytest.raises(GiftError, match="Twice/Event0"):
        gifts.find_gifts(fcs, files(fcs))


def test_flow_files_take_the_listed_version(tmp_path):
    folder = tmp_path / "Event" / "EventFlow"
    folder.mkdir(parents=True)
    for name in ("A.bfevfl.zs", "A.110.bfevfl.zs", "B.bfevfl.zs", "C.120.bfevfl.zs"):
        (folder / name).write_bytes(b"")
    assert gifts.flow_files(tmp_path, {"A": "110"}) == {
        "A": "Event/EventFlow/A.110.bfevfl.zs",
        "B": "Event/EventFlow/B.bfevfl.zs",
    }
    with pytest.raises(GiftError, match="not found"):
        gifts.flow_files(tmp_path, {"B": "110"})


def test_flow_areas_from_npc_actors_and_event_rows():
    banc = {
        "Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs": {
            "Actors": [{"Gyaml": "Npc_Test"}, {"Gyaml": "EventRequestActor", "Dynamic": {"Event": "Row_Dm_Test"}}]
        },
        "Banc/LostWood/LostWood_Child_Dynamic.bcett.byml.zs": {"Actors": [{"Gyaml": "Npc_Twice"}]},
        "Banc/Market/Market_Static.bcett.byml.zs": {"Actors": [{"Gyaml": "Npc_Twice"}]},
        "Banc/DreamWorld/GohmaStage_Static.bcett.byml.zs": {"Actors": [{"Gyaml": "Npc_Test"}]},
    }
    rows = [{"__RowId": "Row_Dm_Test", "FlowchartFileName": "Work/Event/EventFlow/Dm_Test.evfc"}, {"__RowId": "X"}]
    areas = gifts.flow_areas(banc, rows)
    assert areas["Npc_Test"] == "KokiriForest"  # the DreamWorld copy does not count
    assert areas["Dm_Test"] == "KokiriForest"
    assert "Npc_Twice" not in areas  # two areas: none named


def test_gift_definitions_follow_the_placements_and_keep_hand_edits():
    fcs = flows()
    found = gifts.find_gifts(fcs, files(fcs))
    defs = definitions.build([], {}, gifts=found)
    assert [(d.id, d.name) for d in defs][:2] == [
        ("Dm_Test/Event0", "Dm_Test Event0 (Item_Stone_Forest)"),
        ("Dm_Test/Event1", "Dm_Test Event1 (Item_Melody_SariaSong)"),
    ]
    assert definitions.loads(definitions.dumps(defs)) == defs
    edited = {
        "Dm_Test/Event0": definitions.Definition("Dm_Test/Event0", EVENT_GIFT, "", "Queen Gohma", "I", "Queen Gohma")
    }
    rebuilt = definitions.build([], {}, existing=edited, gifts=found)
    assert (rebuilt[0].name, rebuilt[0].oot_randomizer_name) == ("Queen Gohma", "Queen Gohma")
