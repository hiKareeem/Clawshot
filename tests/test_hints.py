import pytest

from clawshot.census import hints
from clawshot.census.hints import HintCensusError
from clawshot.formats import evfl


def _stone(name, hash_, at, gyaml=hints.STONE_ACTOR, flag=None):
    actor = {"Gyaml": gyaml, "Hash": hash_, "Translate": list(at)}
    if name is not None:
        actor["Name"] = name
    if flag:
        actor["Presence"] = {"FlagName": flag, "IsNegation": True}
    return actor


def test_scan_stones_merges_age_copies_and_keeps_shared_labels_apart_by_area():
    banc = {
        "Banc/Forest/Forest_Child_Static.bcett.byml.zs": {
            "Actors": [
                _stone("GOSSIP_A", 11, (1.0, 2.0, 3.0), flag="GossipStoneDisappear.GOSSIP_A"),
                _stone("GOSSIP_B", 12, (50.0, 0.0, 0.0)),
                {"Gyaml": "Obj_TBox_A_01", "Hash": 99, "Translate": [0, 0, 0]},
            ]
        },
        "Banc/Forest/Forest_Adult_Static.bcett.byml.zs": {
            "Actors": [
                _stone("GOSSIP_A", 21, (1.0, 2.9, 3.0), flag="IsAppear_GOSSIP_A_Adult"),
                _stone(None, 22, (1.0, 2.0, 3.0), gyaml=hints.SILENT_STONE_ACTOR),
            ]
        },
        "Banc/Woods/Woods_Child_Static.bcett.byml.zs": {"Actors": [_stone("GOSSIP_B", 31, (0.0, 0.0, 0.0))]},
        "Banc/DreamWorld/Dream_Static.bcett.byml.zs": {"Actors": [_stone("GOSSIP_C", 41, (0.0, 0.0, 0.0))]},
    }
    stones = hints.scan_stones(banc)
    assert [(s.area, s.label, s.ages) for s in stones] == [
        ("Forest", "GOSSIP_A", "both"),
        ("Forest", "GOSSIP_B", "child"),
        ("Woods", "GOSSIP_B", "child"),
    ]
    a = stones[0]
    assert a.copies == (
        ("Banc/Forest/Forest_Adult_Static.bcett.byml.zs", 21),
        ("Banc/Forest/Forest_Child_Static.bcett.byml.zs", 11),
    )
    assert a.presence == ("GossipStoneDisappear.GOSSIP_A", "IsAppear_GOSSIP_A_Adult")


def test_scan_stones_refuses_one_label_at_two_places_in_an_area():
    banc = {
        "Banc/Forest/Forest_Child_Static.bcett.byml.zs": {
            "Actors": [_stone("GOSSIP_A", 11, (0.0, 0.0, 0.0)), _stone("GOSSIP_A", 12, (10.0, 0.0, 0.0))]
        }
    }
    with pytest.raises(HintCensusError, match="not one stone"):
        hints.scan_stones(banc)


def test_scan_stones_refuses_a_talking_stone_without_a_name():
    banc = {"Banc/Forest/Forest_Child_Static.bcett.byml.zs": {"Actors": [_stone(None, 11, (0.0, 0.0, 0.0))]}}
    with pytest.raises(HintCensusError, match="no Name"):
        hints.scan_stones(banc)


def _flow(equip_gate=True):
    """Talk: has mask? -> worn? -> (random either way) -> instance-name line; every 'no' goes to Navi."""
    actors = [
        evfl.Actor("PouchSystemActor", queries=["EventQueryIsExistInPouch"]),
        evfl.Actor("Player_Event", queries=["EventQueryPlayerIsEquipArmor"]),
        evfl.Actor("GameSystemActor", queries=["EventQueryRandomChoice2"]),
        evfl.Actor("Npc_EventStarter", actions=["EventTalk", hints.INSTANCE_TALK]),
        evfl.Actor("Npc_Navi", actions=["EventTalk"]),
    ]
    mask = {"ArmorName": hints.MASK_OF_TRUTH, "ArmorSlot": 0}
    events = [
        evfl.SwitchEvent("Has", 0, 0, [(0, 1), (1, 5)], {"Actor": hints.MASK_OF_TRUTH, "Num": 1}),
        evfl.SwitchEvent("Worn", 1, 0, [(0, 2), (1, 5)], mask) if equip_gate else evfl.JoinEvent("Worn", 2),
        evfl.SwitchEvent("Random", 2, 0, [(0, 3), (1, 4)]),
        evfl.ActionEvent("LineA", 3, 0, 4, {"MessageId": "EventFlowMsg/GossipStone:Talk_03"}),
        evfl.ActionEvent("Stone", 3, 1, evfl.NONE, {"MstxtName": "GossipStone"}),
        evfl.ActionEvent("Navi", 4, 0, evfl.NONE, {"MessageId": "EventFlowMsg/GossipStone:Talk_00"}),
    ]
    return evfl.Flowchart("GossipStone", actors, events, [evfl.EntryPoint("Talk", main_event=0)])


def test_talk_gates_lists_only_switches_every_path_passes():
    gates = hints.talk_gates(_flow())
    assert [(g.event, g.query, g.case) for g in gates] == [
        ("Has", "EventQueryIsExistInPouch", 0),
        ("Worn", "EventQueryPlayerIsEquipArmor", 0),
    ]
    assert hints.needs_mask_of_truth(gates)


def test_a_stone_reachable_without_the_equip_query_does_not_need_the_mask_worn():
    gates = hints.talk_gates(_flow(equip_gate=False))
    assert [g.event for g in gates] == ["Has"]
    assert not hints.needs_mask_of_truth(gates)


def test_talk_gates_refuses_a_flow_that_never_reaches_the_stone_line():
    flow = _flow()
    flow.events[0].cases = [(0, 5), (1, 5)]
    with pytest.raises(HintCensusError, match="no path"):
        hints.talk_gates(flow)


def test_stone_links_name_each_ootr_stone_once():
    names = [name for name, _ in hints.STONE_LINKS.values() if name is not None]
    assert len(names) == len(set(names))
    assert not set(names) & set(hints.OOTR_STONES_MISSING)
