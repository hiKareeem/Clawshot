"""Event props: the census of item actors an event shows, and the data file that sorts them (spec event-items 2.1)."""

import pytest

from clawshot.census import event_items
from clawshot.formats.evfl import ActionEvent, Actor, Clip, EntryPoint, EventFlowFile, Flowchart, Timeline
from clawshot.patch import event_props
from clawshot.patch.event_props import EventPropsError, Prop

BIND = "EventTriggerModelBind"


def flowchart_doc():
    chart = Flowchart(
        "Dm_Test",
        [
            Actor("Item_Shown", actions=[BIND]),
            Actor("Item_Sparkle", actions=["EventTriggerEmitXLink"]),  # effects only: no model shown
            Actor("Npc_Holder", actions=[BIND]),  # not an item actor
            Actor("Item_Branch", "LostWood", actions=["EventPlayAS"]),
        ],
        [
            ActionEvent("Event0", actor=0, action=0, next=1),
            ActionEvent("Event1", actor=1, action=0, next=2),
            ActionEvent("Event2", actor=2, action=0, next=3),
            ActionEvent("Event3", actor=3, action=0),
        ],
        [EntryPoint("C01", 0)],
    )
    return EventFlowFile("Dm_Test", flowchart=chart)


def timeline_doc():
    timeline = Timeline(
        "Dm_Test_TL",
        1.0,
        actors=[
            Actor("Dm_Item_Prop", "0", actions=["EventPlayASAndModelBindForTimeline"]),
            Actor("Dm_Item_Idle", "0", actions=["EventPlayASAndModelBindForTimeline"]),  # in no clip
        ],
        clips=[Clip(0.0, 1.0, actor=0, action=0)],
    )
    return EventFlowFile("Dm_Test_TL", timeline=timeline)


def test_the_census_lists_item_actors_an_event_binds_animates_or_brings_on_stage():
    assert event_items.find_prop_actors("Dm_Test", flowchart_doc()) == [
        "Dm_Test/flowchart/Item_Shown",
        "Dm_Test/flowchart/Item_Branch@LostWood",
    ]
    assert event_items.find_prop_actors("Dm_Test_TL", timeline_doc()) == ["Dm_Test_TL/timeline/Dm_Item_Prop@0"]


DATA = """
[[prop]]
check = "Gift"
item = "Item_Shown"
event = "Dm_Test"
part = "flowchart"
actor = "Item_Shown"

[[prop]]
check = "Branches"
item = "Item_Branch"
event = "Dm_Test"
part = "flowchart"
actor = "Item_Branch"
secondary = "LostWood"
grant = "Dm_Test/Event9"

[[prop]]
check = "Moat"
item = "Item_Ocarina_Time"
part = "placement"
actor = "Obj_Ocarina_Time_A_01"
banc = "Banc/HyruleField/HyruleField_Child_Static.bcett.byml.zs"
hash = 2802436684568022035

[exclude.played]
reason = "someone plays it"
actors = ["Dm_Test_TL/timeline/Dm_Item_Prop@0"]

[exclude.not_check]
reason = "no check"
events = ["Dm_Other"]
"""


def test_the_data_reads_props_and_named_exclusions():
    data = event_props.loads(DATA)
    assert data.props[0] == Prop("Gift", "Item_Shown", "flowchart", "Item_Shown", event="Dm_Test")
    assert data.props[1].id == "Dm_Test/flowchart/Item_Branch@LostWood"
    assert data.props[1].grant == "Dm_Test/Event9"
    assert data.props[2].id == "Banc/HyruleField/HyruleField_Child_Static.bcett.byml.zs/2802436684568022035"
    assert data.exclusions["played"].actors == ("Dm_Test_TL/timeline/Dm_Item_Prop@0",)
    assert data.exclusions["not_check"].events == ("Dm_Other",)
    assert data.excluded("Dm_Other/flowchart/Item_Any") == "not_check"
    assert data.excluded("Dm_Test_TL/timeline/Dm_Item_Prop@0") == "played"
    assert data.excluded("Dm_Test/flowchart/Item_Shown") is None


@pytest.mark.parametrize(
    "bad",
    [
        DATA.replace('reason = "no check"\n', ""),  # an exclusion needs its reason
        DATA.replace('part = "placement"', 'part = "cutscene"'),
        DATA.replace("hash = 2802436684568022035\n", ""),  # a placed object needs its Hash
        DATA.replace('actors = ["Dm_Test_TL/timeline/Dm_Item_Prop@0"]', 'actors = ["Dm_Test/flowchart/Item_Shown"]'),
        DATA.replace('grant = "Dm_Test/Event9"', 'grant = "Event9"'),
        DATA.replace('event = "Dm_Test"\npart = "flowchart"\nactor = "Item_Shown"', 'part = "flowchart"\nactor = "X"'),
    ],
)
def test_the_data_refuses_a_bad_entry(bad):
    with pytest.raises(EventPropsError):
        event_props.loads(bad)


def test_the_repository_data_loads():
    data = event_props.load()
    assert data.props
    assert {"played", "not_check", "hand_in"} <= set(data.exclusions)


def test_the_data_holds_rutos_stone_as_barinades_placed_object():
    """Plan 10b (decision Q6, BBender 2026-11-25): the stone Ruto shows in Jabu-Jabu stands for Barinade's reward."""
    placed = [p for p in event_props.load().props if p.check == "Barinade" and p.part == event_props.PLACEMENT]
    assert [(p.item, p.actor, p.banc, p.hash) for p in placed] == [
        (
            "Item_Stone_Water",
            "Obj_InsideJabu_Jabu_Stone_Water_A_01",
            "Banc/InsideJabuJabuBelly/InsideJabuJabuBelly_Static.bcett.byml.zs",
            15570932853683785298,
        )
    ]


def test_the_data_holds_links_hand_in_the_moat_scene():
    """Played run E10 (BBender 2026-11-26, pilot arm A): Link's look in Dm_MelodyGet_Time (cuts C01-C04) gets a bind
    of its own, the template being Zelda's ocarina entry (its bind and offstage actions)."""
    assert event_props.load().hands == (
        event_props.HandBind(
            "HF Ocarina of Time Item",
            "Item_Ocarina_Time",
            "Dm_MelodyGet_Time",
            "Dm_Item_Ocarina_Time",
            "Player_Event",
            "Weapon_L",
            "C01",
            "C05",
        ),
    )
    with pytest.raises(event_props.EventPropsError):
        event_props.loads('[[hand]]\ncheck = "X"\n')


def test_a_flowchart_prop_reads_its_scene_set_and_a_bad_one_is_refused():
    """D20: ``scene_as`` names the animation set the event plays on a flowchart prop."""
    branch = 'secondary = "LostWood"\n'
    data = event_props.loads(DATA.replace(branch, branch + 'scene_as = "Dm_Test_Item_Branch"\n'))
    assert data.props[1].scene_as == "Dm_Test_Item_Branch"
    assert data.props[0].scene_as == ""
    placed = "hash = 2802436684568022035\n"
    for bad in (
        DATA.replace(branch, branch + 'scene_as = ""\n'),
        DATA.replace(branch, branch + 'scene_as = "Dm_Test_Item_Branch/C02"\n'),
        DATA.replace(placed, placed + 'scene_as = "Dm_Test_Item_Branch"\n'),
    ):
        with pytest.raises(EventPropsError):
            event_props.loads(bad)


def test_the_target_and_darunia_name_the_scene_sets_pilot_a_played():
    """Pilot A (BBender, runs S12, S13): the triggers Dm_LostWood_0040_Item_BulletBag_{Large,Medium}/C02 and
    Dm_Goron_0030_Gauntlet_Goron/C09-Gauntlet."""
    sets = {(p.event, p.actor): p.scene_as for p in event_props.load().props if p.scene_as}
    assert sets[("Dm_LostWood_0040", "Item_BulletBag_Large")] == "Dm_LostWood_0040_Item_BulletBag_Large"
    assert sets[("Dm_LostWood_0040", "Item_BulletBag_Medium")] == "Dm_LostWood_0040_Item_BulletBag_Medium"
    assert sets[("Dm_Goron_0030", "Item_Gauntlet_Goron")] == "Dm_Goron_0030_Gauntlet_Goron"
