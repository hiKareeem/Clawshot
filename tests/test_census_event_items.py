"""Display-only get windows and Zelda's Notes targets in flows with a gift step (spec event-items 1.1)."""

import pytest

from clawshot.census import event_items, gifts
from clawshot.census.event_items import NOTES, WINDOW, Display
from clawshot.formats.evfl import ActionEvent, Actor, Argument, EntryPoint, Flowchart, SubFlowEvent
from clawshot.patch import gifts as gift_patch

POUCH = Actor(gifts.GIVE_ACTOR, actions=[gifts.GIVE_ACTION])
NOTES_ACTOR = Actor("ZeldaNotesActor", actions=[event_items.NOTES_ACTION])


def give(name, item, next=0xFFFF):
    return ActionEvent(name, actor=0, action=0, next=next, params={"Actor": item, "Num": 1})


def display(name, item, next=0xFFFF):
    return SubFlowEvent(
        name, event_items.DISPLAY_FLOW, event_items.DISPLAY_ENTRY, next=next, params={"ActorName": item}
    )


def notes(name, target, next=0xFFFF):
    params = {"TypeID": "get_item", "TargetID": target, "Frame": 0}
    return ActionEvent(name, actor=1, action=0, next=next, params=params)


def flows():
    gift_flow = Flowchart(
        "Dm_Gift",
        [POUCH, NOTES_ACTOR],
        [
            give("Event0", "Item_Ocarina_Fairy", next=1),
            display("Event1", "Item_Ocarina_Fairy", next=2),
            notes("Event2", "Item_Ocarina_Fairy", next=3),
            display("Event3", Argument("ActorName")),  # a wrapper's argument is no literal window
        ],
        [EntryPoint("C01", 0)],
    )
    no_gift = Flowchart(
        "Dm_NoGift",
        [POUCH, NOTES_ACTOR],
        [display("Event0", "Weapon_Sword_Master", next=1), notes("Event1", "Weapon_Sword_Master")],
        [EntryPoint("C01", 0)],
    )
    return {"Dm_Gift": gift_flow, "Dm_NoGift": no_gift}


def test_a_gift_flow_lists_its_literal_window_and_notes_target_keyed_by_flow_and_event():
    found = event_items.find_displays(flows(), {"Dm_Gift"})
    assert found == [
        Display("Dm_Gift/Event1", WINDOW, "Dm_Gift", "Event1", "ActorName", "Item_Ocarina_Fairy"),
        Display("Dm_Gift/Event2", NOTES, "Dm_Gift", "Event2", "TargetID", "Item_Ocarina_Fairy"),
    ]


def test_a_flow_without_a_gift_step_yields_nothing():
    assert event_items.find_displays(flows(), set()) == []
    assert all(d.flow != "Dm_NoGift" for d in event_items.find_displays(flows(), {"Dm_Gift"}))


def test_gift_flows_are_the_flows_of_the_census_gifts():
    found = gifts.find_gifts(flows(), {"Dm_Gift": "a", "Dm_NoGift": "b"})
    assert event_items.gift_flows(found) == {"Dm_Gift"}


def test_gift_rules_read_a_check_display_list():
    rules = gift_patch.loads(
        '[check.A]\nclass = "swap"\ndisplay = ["Dm_Gift/Event1", "Dm_Gift/Event2"]\n'
        '[check.B]\nclass = "rewrite"\ngiven = ["Flow/Event1"]\ndisplay = ["Flow/Event3"]\n'
    )
    assert rules["A"].display == ("Dm_Gift/Event1", "Dm_Gift/Event2")
    assert rules["B"].display == ("Flow/Event3",)


@pytest.mark.parametrize(
    "text",
    [
        '[check.A]\nclass = "swap"\ndisplay = ["no slash"]\n',
        '[check.A]\nclass = "more"\nreason = "r"\ndisplay = ["Flow/Event1"]\n',
    ],
)
def test_gift_rules_refuse_a_bad_display(text):
    with pytest.raises(gift_patch.GiftPatchError):
        gift_patch.loads(text)
