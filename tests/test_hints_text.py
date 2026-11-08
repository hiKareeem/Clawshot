import pytest

from clawshot.census import hints
from clawshot.formats import byml, evfl, msbt, sarc
from clawshot.formats.msbt import Msbt, Tag
from clawshot.patch import text
from clawshot.patch.plan import PatchError


def _archive():
    stone = Msbt({"GOSSIP_A": ["old rumor"], "GOSSIP_B": ["other rumor"]}, buckets=3)
    pouch = Msbt({"Item_X_Name": [Tag(201, 13), "Hookshot"], "Item_X_GetMessage": ["You got it"]}, buckets=2)
    return {"EventFlowMsg/GossipStone.msbt": msbt.write(stone), text.POUCH_TEXT: msbt.write(pouch)}


def test_edit_messages_replaces_only_the_named_message():
    files = _archive()
    out = text.edit_messages({"EventFlowMsg/GossipStone.msbt": {"GOSSIP_A": ["new line"]}})(sarc.write(files))
    back = sarc.read(out)
    assert back[text.POUCH_TEXT] == files[text.POUCH_TEXT]
    stone = msbt.read(back["EventFlowMsg/GossipStone.msbt"])
    assert stone.messages == {"GOSSIP_A": ["new line"], "GOSSIP_B": ["other rumor"]}
    assert stone.buckets == 3


@pytest.mark.parametrize(
    ("edits", "match"),
    [
        ({"EventFlowMsg/Nope.msbt": {"GOSSIP_A": ["x"]}}, "no message file"),
        ({"EventFlowMsg/GossipStone.msbt": {"GOSSIP_Z": ["x"]}}, "no message labelled"),
    ],
)
def test_edit_messages_refuses_what_is_not_there(edits, match):
    with pytest.raises(PatchError, match=match):
        text.edit_messages(edits)(sarc.write(_archive()))


def test_keep_style_takes_only_the_opening_tags_of_the_old_line():
    old = [Tag(0, 3, b"\x01\x00"), Tag(0, 2, b"P\x00"), "rumor", Tag(0, 4), "more"]
    assert text.keep_style(old, ["new"]) == [Tag(0, 3, b"\x01\x00"), Tag(0, 2, b"P\x00"), "new"]
    assert text.keep_style(["plain"], ["new"]) == ["new"]


def test_item_name_keeps_grammar_tags_and_refuses_unknown_items():
    pouch = msbt.read(_archive()[text.POUCH_TEXT])
    assert text.item_name(pouch, "Item_X") == [Tag(201, 13), "Hookshot"]
    with pytest.raises(PatchError, match="Item_Y_Name"):
        text.item_name(pouch, "Item_Y")


def _actor(components=None, parent=None):
    tree = {}
    if parent:
        tree["$parent"] = f"Work/Actor/{parent}.engine__actor__ActorParam.gyml"
    if components is not None:
        tree["Components"] = components
    return byml.write(tree)


def test_text_key_follows_the_actor_name_component_and_its_parents():
    ref = "?ActorSystem/ActorName/Obj_Rupee_Red.engine__actor__ActorName.bgyml"
    pack = {
        "Actor/TBox_Rupee_Red.engine__actor__ActorParam.bgyml": _actor({"ActorNameRef": ref}, "TBox_Rupee_Green"),
        "Actor/Child.engine__actor__ActorParam.bgyml": _actor({"ModelInfoRef": "?x"}, "Base"),
        "Actor/Base.engine__actor__ActorParam.bgyml": _actor({"ActorNameRef": "?ActorSystem/ActorName/Base.b.bgyml"}),
        "Actor/Bare.engine__actor__ActorParam.bgyml": _actor({}),
    }
    assert text.text_key(pack, "TBox_Rupee_Red") == "Obj_Rupee_Red"
    assert text.text_key(pack, "Child") == "Base"
    assert text.text_key(pack, "Bare") == "Bare"


def _gossip_flow():
    actors = [
        evfl.Actor("PouchSystemActor", queries=["EventQueryIsExistInPouch"]),
        evfl.Actor("Player_Event", queries=["EventQueryPlayerIsEquipArmor"]),
        evfl.Actor("Npc_EventStarter", actions=[hints.INSTANCE_TALK]),
        evfl.Actor("Npc_Navi", actions=["EventTalk"]),
    ]
    events = [
        evfl.SwitchEvent("Has", 0, 0, [(0, 1), (1, 3)], {"Actor": hints.MASK_OF_TRUTH, "Num": 1}),
        evfl.SwitchEvent("Worn", 1, 0, [(0, 2), (1, 3)], {"ArmorName": hints.MASK_OF_TRUTH, "ArmorSlot": 0}),
        evfl.ActionEvent("Stone", 2, 0, evfl.NONE, {"MstxtName": "GossipStone"}),
        evfl.ActionEvent("Navi", 3, 0, evfl.NONE, {"MessageId": "EventFlowMsg/GossipStone:Talk_00"}),
    ]
    return evfl.Flowchart("GossipStone", actors, events, [evfl.EntryPoint("Talk", main_event=0)])


def test_gossip_without_mask_sends_every_answer_on_to_the_stone():
    flow = _gossip_flow()
    assert text.gossip_without_mask(flow) == ["Has", "Worn"]
    assert flow.events[0].cases == [(0, 1), (1, 1)]
    assert flow.events[1].cases == [(0, 2), (1, 2)]
    assert hints.talk_gates(flow) == []


def test_gossip_without_mask_refuses_a_flow_without_the_mask_question():
    flow = _gossip_flow()
    text.gossip_without_mask(flow)
    with pytest.raises(PatchError, match="no Mask of Truth question"):
        text.gossip_without_mask(flow)
