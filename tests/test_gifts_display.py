"""A gift check's display-only get windows and Zelda's Notes targets name the item its grant gives (spec event-items
1.2, 1.3; plan task 5)."""

import pytest

from clawshot.census import event_items
from clawshot.census.gifts import DIRECT, EVENT_GIFT, GIVE_ACTION, GIVE_ACTOR, Gift
from clawshot.formats import evfl
from clawshot.formats.evfl import ActionEvent, Actor, EntryPoint, EventFlowFile, Flowchart, SubFlowEvent
from clawshot.patch import custom_items, gifts
from clawshot.patch.gifts import GiftChange, GiftPatchError, Rule

FLOW = "Dm_Gift"
VANILLA = "Item_Ocarina_Fairy"
STEP = Gift(f"{FLOW}/Event68", EVENT_GIFT, FLOW, "f", ("C01",), "Event68", DIRECT, "Actor", VANILLA, "")
DISPLAYS = (f"{FLOW}/Event77", f"{FLOW}/Event58")


def chart(window: str = VANILLA, target: str = VANILLA) -> Flowchart:
    return Flowchart(
        FLOW,
        [Actor(GIVE_ACTOR, actions=[GIVE_ACTION]), Actor("ZeldaNotesActor", actions=[event_items.NOTES_ACTION])],
        [
            ActionEvent("Event68", actor=0, action=0, next=1, params={"Actor": VANILLA, "Num": 1}),
            SubFlowEvent(
                "Event77", event_items.DISPLAY_FLOW, event_items.DISPLAY_ENTRY, next=2, params={"ActorName": window}
            ),
            ActionEvent("Event58", actor=1, action=0, params={"TypeID": "get_item", "TargetID": target, "Frame": 0}),
        ],
        [EntryPoint("C01", 0)],
    )


def change(item: str, display=DISPLAYS) -> GiftChange:
    return GiftChange(Rule("LW Gift from Saria", "swap", display=display), (STEP,), item)


def events(fc: Flowchart) -> dict:
    return {e.name: e for e in fc.events}


@pytest.mark.parametrize("item", ["Item_Sword_Biggoron", custom_items.NOTHING, custom_items.FOREIGN.format(index=3)])
def test_a_moved_check_names_its_given_item_in_its_window_and_notes_target(item):
    fc = chart()
    gifts.patch_flowchart(fc, FLOW, [change(item)])
    by_name = events(fc)
    assert by_name["Event68"].params["Actor"] == item
    assert by_name["Event77"].params == {"ActorName": item}
    assert by_name["Event58"].params == {"TypeID": "get_item", "TargetID": item, "Frame": 0}


@pytest.mark.parametrize(("window", "target"), [("Item_Other", VANILLA), (VANILLA, "Item_Other")])
def test_a_display_naming_another_item_than_the_grant_is_refused_by_name(window, target):
    with pytest.raises(GiftPatchError, match="Dm_Gift/Event(77|58)"):
        gifts.patch_flowchart(chart(window, target), FLOW, [change("Item_Sword_Biggoron")])


def test_a_display_that_is_no_window_or_notes_step_is_refused():
    with pytest.raises(GiftPatchError, match="Dm_Gift/Event68"):
        gifts.patch_flowchart(chart(), FLOW, [change("Item_Sword_Biggoron", display=(f"{FLOW}/Event68",))])


def test_a_vanilla_placement_writes_the_same_bytes_as_without_displays():
    data = evfl.write(EventFlowFile(FLOW, flowchart=chart()))
    with_displays = gifts.flow_transform(FLOW, [change(VANILLA)])(data)
    without = gifts.flow_transform(FLOW, [change(VANILLA, display=())])(data)
    assert with_displays == without == data


def test_display_flows_are_changed_flows():
    other = GiftChange(Rule("C", "swap", display=("Other/Event1",)), (STEP,), "Item_X")
    assert gifts.flows_changed([other]) == [FLOW, "Other"]
