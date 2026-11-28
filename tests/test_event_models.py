"""Event props renamed to containers (spec event-items 2.3, 2.4a; plan 8.1): only the prop's actor entry changes."""

import copy

import pytest

from clawshot.census.event_items import FLOWCHART, TIMELINE
from clawshot.formats import evfl
from clawshot.formats.evfl import ActionEvent, Actor, Clip, EntryPoint, EventFlowFile, Flowchart, Timeline, Trigger
from clawshot.patch import event_models, event_props
from clawshot.patch.plan import PatchError

CONTAINER = "Dm_Item_Clawshot_Item_Sword_Biggoron"


def farewell() -> EventFlowFile:
    """Shaped like Dm_Kokiri_0155: the grant names the item by string, Saria's own ocarina is another prop."""
    chart = Flowchart(
        "Dm_Kokiri_0155",
        [
            Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"]),
            Actor("Dm_Item_Ocarina_Fairy_Saria", "saria", actions=["EventTriggerModelBind"]),
            Actor("Item_Ocarina_Fairy", actions=["EventTriggerModelBind", "EventGoOffstageForUser"]),
        ],
        [
            ActionEvent("Event68", 0, 0, next=1, params={"Actor": "Item_Ocarina_Fairy", "Num": 1}),
            ActionEvent(
                "Event93",
                2,
                0,
                next=2,
                params={"ActorName": "Player_Event", "BoneName": "Weapon_L", "InstanceName": ""},
            ),
            ActionEvent("Event94", 1, 0, params={"ActorName": "Npc_Kokiri_Saria_Child", "BoneName": "Weapon_R"}),
        ],
        [EntryPoint("C01", 0)],
    )
    return EventFlowFile("Dm_Kokiri_0155", flowchart=chart)


def presenting() -> EventFlowFile:
    """Shaped like Dm_Kokiri_0150: two props with the secondary name "0", clips naming the vanilla model's AS."""
    anime = {"UseEventModelAnime": "Work/Model/Event/Dm_Kokiri_0150/Dm_Kokiri_0150_Item_Ocarina_Fairy/x.gyml"}
    timeline = Timeline(
        "Dm_Kokiri_0150",
        10.0,
        actors=[
            Actor("Dm_Item_Ocarina_Fairy_Saria", "0", actions=["EventPlayASAndModelBindForTimeline"], params=anime),
            Actor("Dm_Item_Ocarina_Fairy", "0", actions=["EventPlayASAndModelBindForTimeline"], params=anime),
        ],
        clips=[Clip(0.0, 2.0, 1, 0, params={"ASName": "C11-Item_Ocarina_Fairy-A-0"}), Clip(2.0, 1.0, 0, 0)],
        # two per clip, by time; at one time leaves before enters, then by clip (as in the dump's timelines)
        triggers=[Trigger(0, 1), Trigger(0, 2), Trigger(1, 1), Trigger(1, 2)],
    )
    return EventFlowFile("Dm_Kokiri_0150", timeline=timeline)


def test_the_flowchart_prop_is_renamed_and_nothing_else_changes():
    before = farewell()
    after = copy.deepcopy(before)
    event_models.rename_prop(after, FLOWCHART, "Item_Ocarina_Fairy", "", CONTAINER)
    assert [a.name for a in after.flowchart.actors] == ["PouchSystemActor", "Dm_Item_Ocarina_Fairy_Saria", CONTAINER]
    assert after.flowchart.actors[2].actions == before.flowchart.actors[2].actions
    assert after.flowchart.events == before.flowchart.events  # the grant, the bind and Saria's own bind
    assert after.flowchart.entry_points == before.flowchart.entry_points


def test_the_timeline_prop_is_renamed_keeping_its_secondary_name_parameters_and_tracks():
    before = presenting()
    after = copy.deepcopy(before)
    event_models.rename_prop(after, TIMELINE, "Dm_Item_Ocarina_Fairy", "0", CONTAINER)
    renamed, saria = after.timeline.actors[1], after.timeline.actors[0]
    assert (renamed.name, renamed.secondary_name, renamed.params) == (CONTAINER, "0", before.timeline.actors[1].params)
    assert saria == before.timeline.actors[0]  # her own played ocarina keeps its look (2.8)
    assert after.timeline.clips == before.timeline.clips


@pytest.mark.parametrize(
    ("make", "part", "actor", "secondary"),
    [
        (farewell, FLOWCHART, "Item_Ocarina_Time", ""),  # no such actor
        (farewell, TIMELINE, "Item_Ocarina_Fairy", ""),  # the file holds no timeline
        (presenting, TIMELINE, "Dm_Item_Ocarina_Fairy", ""),  # wrong secondary name
    ],
)
def test_a_prop_the_file_does_not_hold_is_refused(make, part, actor, secondary):
    with pytest.raises(PatchError):
        event_models.rename_prop(make(), part, actor, secondary, CONTAINER)


def test_the_file_transform_renames_reads_back_and_leaves_an_empty_rename_list_byte_identical():
    data = evfl.write(farewell())
    out = event_models.prop_transform("Dm_Kokiri_0155", [(FLOWCHART, "Item_Ocarina_Fairy", "", CONTAINER)])(data)
    assert [a.name for a in evfl.read(out).flowchart.actors][2] == CONTAINER
    assert event_models.prop_transform("Dm_Kokiri_0155", [])(data) == data


def prop(check, item, event, part, actor, secondary="", grant=""):
    from clawshot.patch.event_props import Prop

    return Prop(check, item, part, actor, secondary, event=event, grant=grant)


PROPS = [
    prop("LW Gift from Saria", "Item_Ocarina_Fairy", "Dm_Kokiri_0155", FLOWCHART, "Item_Ocarina_Fairy"),
    prop("LW Gift from Saria", "Item_Ocarina_Fairy", "Dm_Kokiri_0150", TIMELINE, "Dm_Item_Ocarina_Fairy", "0"),
    prop("Queen Gohma", "Item_Stone_Forest", "Dm_Kokiri_0130", FLOWCHART, "Item_Stone_Forest"),
    prop(
        "LW Target in Woods",
        "Item_BulletBag_Large",
        "Dm_LostWood_0040",
        FLOWCHART,
        "Item_BulletBag_Large",
        "LostWood",
        "Dm_LostWood_0040/Event17",
    ),
    prop(
        "LW Target in Woods",
        "Item_BulletBag_Medium",
        "Dm_LostWood_0040",
        FLOWCHART,
        "Item_BulletBag_Medium",
        "LostWood",
        "Dm_LostWood_0040/Event30",
    ),
]


def test_each_prop_of_a_moved_check_gets_the_container_of_the_given_items_model():
    renames, models = event_models.plan_renames(PROPS, {"LW Gift from Saria": "Item_Sword_Biggoron"})
    assert renames == {
        "Dm_Kokiri_0150": [(TIMELINE, "Dm_Item_Ocarina_Fairy", "0", CONTAINER)],
        "Dm_Kokiri_0155": [(FLOWCHART, "Item_Ocarina_Fairy", "", CONTAINER)],
    }
    assert models == ["Item_Sword_Biggoron"]


def test_a_song_shows_its_own_container_and_checks_that_keep_their_item_change_nothing():
    """The song's container shows its ocarina with the song's effect (pilot arm B, BBender 2026-11-26)."""
    renames, models = event_models.plan_renames(PROPS, {"Queen Gohma": "Item_Melody_FireBolero"})
    assert renames == {
        "Dm_Kokiri_0130": [(FLOWCHART, "Item_Stone_Forest", "", "Dm_Item_Clawshot_Item_Melody_FireBolero")]
    }
    assert models == ["Item_Melody_FireBolero"]
    assert event_models.plan_renames(PROPS, {}) == ({}, [])


def test_both_branches_of_a_pair_show_the_item_their_grant_gives_and_one_container_serves_several_events():
    renames, models = event_models.plan_renames(
        PROPS, {"LW Target in Woods": "Obj_Heart_Piece", "LW Gift from Saria": "Obj_Heart_Piece"}
    )
    heart = "Dm_Item_Clawshot_Obj_Heart_Piece"
    assert renames["Dm_LostWood_0040"] == [
        (FLOWCHART, "Item_BulletBag_Large", "LostWood", heart),
        (FLOWCHART, "Item_BulletBag_Medium", "LostWood", heart),
    ]
    assert models == ["Obj_Heart_Piece"]  # one container for every event that shows the heart piece


def test_the_pilot_filter_keeps_only_the_named_events():
    renames, _ = event_models.plan_renames(
        PROPS,
        {"LW Gift from Saria": "Item_Sword_Biggoron", "Queen Gohma": "Obj_Heart_Piece"},
        events={"Dm_Kokiri_0150", "Dm_Kokiri_0155"},
    )
    assert sorted(renames) == ["Dm_Kokiri_0150", "Dm_Kokiri_0155"]


def test_the_grant_still_names_the_real_item_after_the_gift_patch_and_the_rename_compose():
    from clawshot.census.gifts import DIRECT, EVENT_GIFT, Gift
    from clawshot.patch import gifts

    step = Gift(
        "Dm_Kokiri_0155/Event68",
        EVENT_GIFT,
        "Dm_Kokiri_0155",
        "f",
        ("C01",),
        "Event68",
        DIRECT,
        "Actor",
        "Item_Ocarina_Fairy",
        "",
    )
    change = gifts.GiftChange(gifts.Rule("LW Gift from Saria", "swap"), (step,), "Item_Sword_Biggoron")
    renames, _ = event_models.plan_renames(PROPS, {"LW Gift from Saria": "Item_Sword_Biggoron"})
    data = gifts.flow_transform("Dm_Kokiri_0155", [change])(evfl.write(farewell()))
    out = evfl.read(event_models.prop_transform("Dm_Kokiri_0155", renames["Dm_Kokiri_0155"])(data)).flowchart
    assert out.events[0].params["Actor"] == "Item_Sword_Biggoron"  # the real item, not the container
    assert out.actors[2].name == CONTAINER


def test_every_item_a_gift_can_give_resolves_to_a_container_of_its_container_model():
    from clawshot.patch import containers
    from clawshot.patch import items as item_actors

    table = item_actors.load()
    for item, actor in sorted(table.actors.items()):
        renames, models = event_models.plan_renames(PROPS[:1], {"LW Gift from Saria": actor})
        assert models == [containers.container_model(actor)], item
        assert renames["Dm_Kokiri_0155"][0][3] == "Dm_Item_Clawshot_" + containers.container_model(actor)


@pytest.mark.parametrize(
    ("check", "event", "actor", "reward"),
    [
        ("Queen Gohma", "Dm_Kokiri_0130", "Item_Stone_Forest", "Item_Medal_Light"),  # a stone scene shows a medallion
        ("Phantom Ganon", "Dm_Awake_Forest_Get", "Item_Medal_Forest", "Item_Stone_Water"),  # awakening shows a stone
        ("ToT Reward from Rauru", "Dm_SageRoom_0005", "Item_Medal_Light", "Item_Medal_Shadow"),
    ],
)
def test_a_boss_reward_scene_shows_the_reward_the_seed_places_there(check, event, actor, reward):
    props = [prop(check, actor, event, FLOWCHART, actor)]
    renames, _ = event_models.plan_renames(props, {check: reward})
    assert renames == {event: [(FLOWCHART, actor, "", "Dm_Item_Clawshot_" + reward)]}


# Link's look in the moat scene (played run E10, BBender 2026-11-26): his hand gets the given item's container through
# a bind of its own, since the flow has no prop for what he holds (his animation shows his own ocarina).
MOAT_CONTAINER = "Dm_Item_Clawshot_Obj_Heart_Piece"


def moat_lesson() -> EventFlowFile:
    """Shaped like Dm_MelodyGet_Time: cuts as entry points, Zelda's ocarina bound to her hand and sent offstage."""
    chart = Flowchart(
        "Dm_MelodyGet_Time",
        [
            Actor("Player_Event", actions=["EventPlayerPlayASForFlowchart"]),
            Actor("Dm_Item_Ocarina_Time", actions=["EventTriggerModelBind", "EventGoOffstageForUser"]),
        ],
        [
            ActionEvent("Event32", 0, 0, params={"ASCommand": "C01-Player_Child-A-0"}),
            ActionEvent(
                "Event35",
                1,
                0,
                next=2,
                params={"ActorName": "Npc_Hylia_Zelda_Child", "BoneName": "Weapon_L", "InstanceName": "", "X": 1},
            ),
            ActionEvent("Event200", 1, 1, params={"IsWaitEnd": True}),
        ],
        [EntryPoint("C01", 0), EntryPoint("C05", 1)],
    )
    return EventFlowFile("Dm_MelodyGet_Time", flowchart=chart)


HAND = event_models.HandRename("Dm_Item_Ocarina_Time", "Player_Event", "Weapon_L", "C01", "C05", MOAT_CONTAINER)


def test_a_hand_bind_adds_the_container_bound_at_the_start_cut_and_sent_offstage_at_the_end_cut():
    document = moat_lesson()
    event_models.add_hand_bind(document, HAND)
    chart = document.flowchart
    added = chart.actors[-1]
    assert (added.name, added.secondary_name) == (MOAT_CONTAINER, "hand")
    assert added.actions == ["EventTriggerModelBind", "EventGoOffstageForUser"]
    bind = chart.events[chart.entry_point("C01").main_event]
    assert (bind.actor, added.actions[bind.action]) == (len(chart.actors) - 1, "EventTriggerModelBind")
    assert bind.params == {"ActorName": "Player_Event", "BoneName": "Weapon_L", "InstanceName": "", "X": 1}
    assert chart.events[bind.next].name == "Event32"  # then the cut as before
    off = chart.events[chart.entry_point("C05").main_event]
    assert added.actions[off.action] == "EventGoOffstageForUser" and off.params == {"IsWaitEnd": True}
    assert chart.events[off.next].name == "Event35"
    native = moat_lesson().flowchart
    assert chart.actors[: len(native.actors)] == native.actors  # Zelda's ocarina untouched (played, D3)
    assert chart.events[: len(native.events)] == native.events


def test_a_hand_bind_is_refused_when_its_cut_or_template_is_missing_or_it_is_there_already():
    document = moat_lesson()
    event_models.add_hand_bind(document, HAND)
    with pytest.raises(PatchError):
        event_models.add_hand_bind(document, HAND)
    with pytest.raises(PatchError):
        event_models.add_hand_bind(moat_lesson(), HAND._replace(start="C99"))
    with pytest.raises(PatchError):
        event_models.add_hand_bind(moat_lesson(), HAND._replace(template="Nope"))


def test_the_file_transform_adds_the_hand_bind_and_reads_back():
    data = evfl.write(moat_lesson())
    out = evfl.read(event_models.prop_transform("Dm_MelodyGet_Time", [], [HAND])(data))
    assert out.flowchart.actors[-1].name == MOAT_CONTAINER


def test_a_moved_check_plans_its_hand_bind_and_the_container_and_a_vanilla_one_none():
    hands = [
        event_models.event_props.HandBind(
            "HF Ocarina of Time Item",
            "Item_Ocarina_Time",
            "Dm_MelodyGet_Time",
            "Dm_Item_Ocarina_Time",
            "Player_Event",
            "Weapon_L",
            "C01",
            "C05",
        )
    ]
    rows = {"Item_Ocarina_Time": box_row((-1, 0, 2), (1, 2, 4)), "Obj_Heart_Piece": box_row((-1, 1, 0), (1, 5, 0))}
    planned, models = event_models.plan_hands(hands, {"HF Ocarina of Time Item": "Obj_Heart_Piece"}, rows)
    assert planned == {"Dm_MelodyGet_Time": [HAND._replace(shift=(0.0, -2.0, 3.0))]}
    assert models == ["Obj_Heart_Piece"]
    assert event_models.plan_hands(hands, {}, {}) == ({}, [])


# D19 (BBender, 2026-11-26, played run S6): the hand bind holds the shown item by its middle.
def box_row(low, high) -> dict:
    return {
        "ModelAabbMin": dict(zip("XYZ", map(float, low), strict=True)),
        "ModelAabbMax": dict(zip("XYZ", map(float, high), strict=True)),
    }


def test_a_hand_shift_is_the_native_box_centre_minus_the_shown_one():
    rows = {"native": box_row((-0.5, -1, 0), (1.5, 1, 2)), "shown": box_row((-1, 0, -1), (1, 4, 1))}
    assert event_models.box_centre(rows["native"]) == (0.5, 0.0, 1.0)
    assert event_models.hand_shift(rows, "native", "shown") == (0.5, -2.0, 1.0)
    assert event_models.hand_shift(rows, "shown", "shown") == (0.0, 0.0, 0.0)
    with pytest.raises(PatchError):
        event_models.hand_shift(rows, "native", "missing")
    with pytest.raises(PatchError):
        event_models.box_centre({"__RowId": "boxless"})


def moat_lesson_with_offsets(trans=(0.25, 0.0, -1.0)) -> EventFlowFile:
    """The moat lesson with the real template bind's offset parameters (Dm_MelodyGet_Time Event35)."""
    document = moat_lesson()
    params = document.flowchart.events[1].params
    params["RotOffset"] = evfl.FloatArray((0.0, 0.0, 0.0))
    params["TransOffset"] = evfl.FloatArray(trans)
    return document


def test_a_hand_bind_adds_its_shift_to_the_templates_offset_as_f32():
    document = moat_lesson_with_offsets()
    event_models.add_hand_bind(document, HAND._replace(shift=(0.1, -0.2, 0.5)))
    chart = document.flowchart
    bind = chart.events[chart.entry_point("C01").main_event]
    f32 = [event_models._f32(v) for v in (0.25 + 0.1, -0.2, -0.5)]
    assert isinstance(bind.params["TransOffset"], evfl.FloatArray)
    assert list(bind.params["TransOffset"]) == f32 and f32[0] != 0.25 + 0.1  # stored as the file stores it
    assert bind.params["RotOffset"] == (0.0, 0.0, 0.0)
    assert chart.events[1].params["TransOffset"] == (0.25, 0.0, -1.0)  # Zelda's own bind keeps its offset (D6)
    out = evfl.read(evfl.write(document))
    assert out == document  # the f32 values read back unchanged


def test_a_hand_bind_with_a_shift_needs_the_templates_offset():
    with pytest.raises(PatchError):
        event_models.add_hand_bind(moat_lesson(), HAND._replace(shift=(0.0, 1.0, 0.0)))
    document = moat_lesson()  # no shift: the template's parameters as they are
    event_models.add_hand_bind(document, HAND)
    assert "TransOffset" not in document.flowchart.events[document.flowchart.entry_point("C01").main_event].params


def test_a_song_at_the_moat_is_held_by_the_middle_of_its_ocarina():
    """A song's container shows its ocarina's model fields (songs.shown_row), so its shift is the ocarina's."""
    hands = [
        event_models.event_props.HandBind(
            "HF Ocarina of Time Item",
            "Item_Ocarina_Time",
            "Dm_MelodyGet_Time",
            "Dm_Item_Ocarina_Time",
            "Player_Event",
            "Weapon_L",
            "C01",
            "C05",
        )
    ]
    rows = {
        "Item_Ocarina_Time": box_row((0, 0, 0), (2, 2, 2)),
        "Item_Ocarina_Fairy": box_row((0, 0, 0), (1, 1, 1)),
        "Item_Melody_SunSong": box_row((-9, -9, -9), (0, 0, 0)),  # its native rupee box: not what it shows
    }
    planned, models = event_models.plan_hands(hands, {"HF Ocarina of Time Item": "Item_Melody_SunSong"}, rows)
    assert models == ["Item_Melody_SunSong"]
    [hand] = planned["Dm_MelodyGet_Time"]
    assert hand.container == "Dm_Item_Clawshot_Item_Melody_SunSong" and hand.shift == (0.5, 0.5, 0.5)
    with pytest.raises(PatchError):
        event_models.plan_hands(hands, {"HF Ocarina of Time Item": "Obj_Heart_Piece"}, rows)


ZELDA = "Dm_Item_Clawshot_Obj_Heart_Piece"


def courtyard() -> EventFlowFile:
    """Shaped like Dm_HrlCastle_0050: the letter prop, and the grant calling the shared get subflow."""
    chart = Flowchart(
        "Dm_HrlCastle_0050",
        [Actor("Item_ZeldaLetter", actions=["EventPlayAS", "EventGoOffstageForUser"])],
        [
            ActionEvent("Event257", 0, 0, params={"ASName": "C14-0-st"}),
            evfl.SubFlowEvent("Event59", "Dm_SY_GetInEvent", "GetInEvent_Zeldaletter", params={"ActorName": "x"}),
        ],
        [EntryPoint("C14", 0), EntryPoint("C15", 1)],
    )
    return EventFlowFile("Dm_HrlCastle_0050", flowchart=chart)


def get_in_event() -> EventFlowFile:
    """Shaped like Dm_SY_GetInEvent: its own entry for the letter, which it sends offstage (Event335)."""
    chart = Flowchart(
        "Dm_SY_GetInEvent",
        [
            Actor("Player_Event", actions=["EventIgnitionShowItem"]),
            Actor("Item_ZeldaLetter", actions=["EventGoOffstageForUser"]),
        ],
        [ActionEvent("Event335", 1, 0)],
        [EntryPoint("GetInEvent_Zeldaletter", 0)],
    )
    return EventFlowFile("Dm_SY_GetInEvent", flowchart=chart)


def flows(*documents: EventFlowFile):
    by_name = {d.name: d for d in documents}
    return lambda event: by_name.get(event)


def test_a_subflow_actor_named_like_a_renamed_prop_takes_the_same_container():
    """Played run r1-zelda2 (BBender, 2026-11-26): the shared get subflow names the letter too; in vanilla the two are
    one actor (it sends the prop offstage for the get pose). Renamed apart, its letter stood still on the ground and the
    container stayed at the hand-over spot."""
    renames = {"Dm_HrlCastle_0050": [(FLOWCHART, "Item_ZeldaLetter", "", ZELDA)]}
    assert event_models.plan_subflow_renames(renames, flows(courtyard(), get_in_event())) == {
        "Dm_SY_GetInEvent": [(FLOWCHART, "Item_ZeldaLetter", "", ZELDA)]
    }


def test_a_subflow_without_the_props_actor_is_left_alone():
    plain = get_in_event()
    plain.flowchart.actors = plain.flowchart.actors[:1]
    plain.flowchart.events = []
    renames = {"Dm_HrlCastle_0050": [(FLOWCHART, "Item_ZeldaLetter", "", ZELDA)]}
    assert event_models.plan_subflow_renames(renames, flows(courtyard(), plain)) == {}


def test_two_scenes_renaming_one_subflow_actor_differently_are_refused():
    other = copy.deepcopy(courtyard())
    other.name = other.flowchart.name = "Other"
    renames = {
        "Dm_HrlCastle_0050": [(FLOWCHART, "Item_ZeldaLetter", "", ZELDA)],
        "Other": [(FLOWCHART, "Item_ZeldaLetter", "", CONTAINER)],
    }
    with pytest.raises(PatchError):
        event_models.plan_subflow_renames(renames, flows(courtyard(), other, get_in_event()))


SONG_CONTAINER = "Dm_Item_Clawshot_Item_Melody_StormSong"
EMIT = "EventTriggerEmitXLink"


def test_a_song_container_emits_its_effect_key_right_after_each_bind():
    """Pilot "emit" (BBender, 2026-11-26): in Saria's farewell, Song of Storms' ocarina showed its effect and stayed
    still once the flow emitted the song user's key GetDemo after the bind (as song lessons emit their Shine key on the
    ocarina). Playing an animation instead gave no effect, or the effect only with Rotate_GetDemo's spin."""
    data = evfl.write(farewell())
    chart = evfl.read(
        event_models.prop_transform("Dm_Kokiri_0155", [(FLOWCHART, "Item_Ocarina_Fairy", "", SONG_CONTAINER)])(data)
    ).flowchart
    actor = next(i for i, a in enumerate(chart.actors) if a.name == SONG_CONTAINER)
    assert chart.actors[actor].actions[-1] == EMIT
    bind = next(e for e in chart.events if e.name == "Event93")
    emit = chart.events[bind.next]
    assert (emit.actor, chart.actors[actor].actions[emit.action]) == (actor, EMIT)
    assert emit.params == {"ELinkKey": "GetDemo", "SLinkKey": ""}
    assert chart.events[emit.next].name == "Event94"  # the bind's old next


def test_another_container_emits_nothing():
    data = evfl.write(farewell())
    chart = evfl.read(
        event_models.prop_transform("Dm_Kokiri_0155", [(FLOWCHART, "Item_Ocarina_Fairy", "", CONTAINER)])(data)
    ).flowchart
    assert all(EMIT not in a.actions for a in chart.actors)
    assert len(chart.events) == 3


def test_a_song_container_the_scene_never_binds_emits_after_it_joins_the_event():
    """Shaped like Biggoron's flow: the prop only joins the event (EventTriggerParticipateEvent, Event8)."""
    chart = Flowchart(
        "Npc_Goron_Biggoron_Adult",
        [Actor("Item_Sword_Biggoron", actions=["EventTriggerParticipateEvent", "EventGoOffstageForUser"])],
        [ActionEvent("Event8", 0, 0, next=1), ActionEvent("Event9", 0, 1)],
        [EntryPoint("C01", 0)],
    )
    data = evfl.write(EventFlowFile("Npc_Goron_Biggoron_Adult", flowchart=chart))
    out = evfl.read(
        event_models.prop_transform(
            "Npc_Goron_Biggoron_Adult", [(FLOWCHART, "Item_Sword_Biggoron", "", SONG_CONTAINER)]
        )(data)
    ).flowchart
    emit = out.events[out.events[0].next]
    assert emit.params["ELinkKey"] == "GetDemo" and out.events[emit.next].name == "Event9"


def test_a_song_container_on_a_timeline_gets_an_emit_clip_over_its_whole_presence():
    """Native timelines emit keys as clips (Dm_FinalBattle_BossIn, Dm_InsideGanonCastle_BossIn_Effect)."""
    data = evfl.write(presenting())
    timeline = evfl.read(
        event_models.prop_transform("Dm_Kokiri_0150", [(TIMELINE, "Dm_Item_Ocarina_Fairy", "0", SONG_CONTAINER)])(data)
    ).timeline
    actor = next(i for i, a in enumerate(timeline.actors) if a.name == SONG_CONTAINER)
    assert timeline.actors[actor].actions[-1] == EMIT
    emits = [c for c in timeline.clips if c.actor == actor and timeline.actors[actor].actions[c.action] == EMIT]
    assert [(c.start, c.duration, c.params) for c in emits] == [(0.0, 2.0, {"ELinkKey": "GetDemo", "SLinkKey": ""})]
    assert len(timeline.clips) == 3  # the native clips stay, in order
    # its enter and leave triggers sit where time order puts them; the native triggers keep their order
    assert [(t.clip, t.type) for t in timeline.triggers] == [(0, 1), (2, 1), (0, 2), (2, 2), (1, 1), (1, 2)]


def test_a_song_containers_hand_bind_emits_right_after_the_bind():
    hand = event_models.HandRename("Dm_Item_Ocarina_Time", "Player_Event", "Weapon_L", "C01", "C05", SONG_CONTAINER)
    chart = evfl.read(event_models.prop_transform("Dm_MelodyGet_Time", [], [hand])(evfl.write(moat_lesson()))).flowchart
    bind = chart.events[chart.entry_point("C01").main_event]
    assert bind.name == "Clawshot_hand_bind"
    emit = chart.events[bind.next]
    assert chart.actors[emit.actor].secondary_name == "hand" and emit.params["ELinkKey"] == "GetDemo"


def test_a_song_on_both_branches_of_a_pair_emits_after_each_branchs_bind_once():
    """Matrix build (2026-11-26): the target scene's two props (D13 branches, both secondary LostWood) both take the
    song container, so two actors share its name; each gets its emit once, the build does not stop."""
    chart = Flowchart(
        "Dm_LostWood_0040",
        [
            Actor("Item_BulletBag_Large", "LostWood", actions=["EventTriggerModelBind", "EventPlayAS"]),
            Actor("Item_BulletBag_Medium", "LostWood", actions=["EventTriggerModelBind", "EventPlayAS"]),
        ],
        [
            ActionEvent("Event31", 0, 0, next=2),
            ActionEvent("Event28", 1, 0, next=3),
            ActionEvent("Event32", 0, 1),
            ActionEvent("Event29", 1, 1),
        ],
        [EntryPoint("C01", 0), EntryPoint("C02", 1)],
    )
    renames = [
        (FLOWCHART, "Item_BulletBag_Large", "LostWood", SONG_CONTAINER),
        (FLOWCHART, "Item_BulletBag_Medium", "LostWood", SONG_CONTAINER),
    ]
    data = evfl.write(EventFlowFile("Dm_LostWood_0040", flowchart=chart))
    out = evfl.read(event_models.prop_transform("Dm_LostWood_0040", renames)(data)).flowchart
    for bind, after in (("Event31", "Event32"), ("Event28", "Event29")):
        event = next(e for e in out.events if e.name == bind)
        emit = out.events[event.next]
        assert emit.params == {"ELinkKey": "GetDemo", "SLinkKey": ""} and emit.actor == event.actor
        assert out.events[emit.next].name == after
    assert sum(1 for e in out.events if e.name.startswith("Clawshot_song_effect")) == 2


# D20 (pilot A, BBender, runs S12, S13): a scene animation the flow plays on a song container starts its effect.


def target() -> EventFlowFile:
    """Shaped like Dm_LostWood_0040: each branch binds its bag to the locator and plays the scene's C02 on it."""
    actions = ["EventTriggerModelBind", "EventPlayAS", "EventGoOffstageForUser"]
    chart = Flowchart(
        "Dm_LostWood_0040",
        [
            Actor("Enemy_ScrubDeku", actions=["EventPlayAS"]),
            Actor("Item_BulletBag_Medium", "LostWood", actions=list(actions)),
            Actor("Item_BulletBag_Large", "LostWood", actions=list(actions)),
        ],
        [
            ActionEvent("Event0", 0, 0, next=1, params={"ASName": "C02"}),  # the scrub's own C02: not the prop's
            ActionEvent("Event28", 1, 0, next=2, params={"ActorName": "Dm_Locator"}),
            ActionEvent("Event32", 1, 1, next=3, params={"ASName": "C02"}),
            ActionEvent("Event31", 2, 0, next=4, params={"ActorName": "Dm_Locator"}),
            ActionEvent("Event33", 2, 1, params={"ASName": "C02"}),
        ],
        [EntryPoint("C02", 0)],
    )
    return EventFlowFile("Dm_LostWood_0040", flowchart=chart)


def scene_prop(check, event, actor, secondary="", scene_as=""):
    from clawshot.patch.event_props import Prop

    return Prop(check, actor, FLOWCHART, actor, secondary, event=event, scene_as=scene_as)


LARGE = scene_prop(
    "LW Target in Woods",
    "Dm_LostWood_0040",
    "Item_BulletBag_Large",
    "LostWood",
    "Dm_LostWood_0040_Item_BulletBag_Large",
)
MEDIUM = scene_prop(
    "LW Target in Woods",
    "Dm_LostWood_0040",
    "Item_BulletBag_Medium",
    "LostWood",
    "Dm_LostWood_0040_Item_BulletBag_Medium",
)
LETTER = scene_prop(
    "HC Zeldas Letter", "Dm_HrlCastle_0050", "Item_ZeldaLetter", "", "Dm_HrlCastle_0050_Item_ZeldaLetter"
)
SARIA = scene_prop("LW Gift from Saria", "Dm_Kokiri_0155", "Item_Ocarina_Fairy")


def test_a_prop_with_a_scene_set_names_each_scene_animation_played_on_it():
    assert event_models.scene_actions(target(), LARGE) == ["Dm_LostWood_0040_Item_BulletBag_Large/C02"]
    assert event_models.scene_actions(courtyard(), LETTER) == ["Dm_HrlCastle_0050_Item_ZeldaLetter/C14-0-st"]
    assert event_models.scene_actions(farewell(), SARIA) == []  # no scene set: nothing


def test_a_scene_set_on_a_prop_the_flow_plays_nothing_on_is_refused():
    with pytest.raises(PatchError, match="plays no EventPlayAS"):
        event_models.scene_actions(farewell(), scene_prop("LW Gift from Saria", "x", "Item_Ocarina_Fairy", "", "Set"))


def test_only_props_of_checks_that_give_a_song_add_scene_animations():
    props = [LARGE, MEDIUM, LETTER, SARIA]
    read = flows(target(), courtyard(), farewell())
    song = "Item_Melody_EponaSong"
    assert event_models.plan_scene_actions(props, {"LW Target in Woods": song}, read) == [
        "Dm_LostWood_0040_Item_BulletBag_Large/C02",
        "Dm_LostWood_0040_Item_BulletBag_Medium/C02",
    ]
    assert event_models.plan_scene_actions(props, {"LW Target in Woods": "Obj_Heart_Piece"}, read) == []
    assert event_models.plan_scene_actions(props, {"LW Gift from Saria": song}, read) == []  # emit only (S1)
    both = {"LW Target in Woods": song, "HC Zeldas Letter": "Item_Melody_StormSong"}
    assert event_models.plan_scene_actions(props, both, read) == [
        "Dm_HrlCastle_0050_Item_ZeldaLetter/C14-0-st",
        "Dm_LostWood_0040_Item_BulletBag_Large/C02",
        "Dm_LostWood_0040_Item_BulletBag_Medium/C02",
    ]
    assert event_models.plan_scene_actions(props, both, read, events={"Dm_HrlCastle_0050"}) == [
        "Dm_HrlCastle_0050_Item_ZeldaLetter/C14-0-st"
    ]


def test_the_app_working_set_holds_the_event_model_inputs():
    from types import SimpleNamespace

    from clawshot.pack.source import resource_spec, working_files
    from clawshot.patch import containers, custom_items, event_props, getitem, items

    given = set(items.load().actors.values())
    inputs = set(event_models.native_inputs(given))
    wanted = working_files(SimpleNamespace(files=[]), resource_spec())
    assert inputs <= wanted, sorted(inputs - wanted)
    # every model a container or a placed object can show, for any item a grant gives, and the placed objects' packs
    for actor in given:
        assert getitem.pack_path(containers.container_model(actor)) in inputs, actor
        assert getitem.pack_path(getitem.model_actor(actor)) in inputs, actor
    placed = [prop.actor for prop in event_props.load().props if prop.part == event_props.PLACEMENT]
    assert placed and {getitem.pack_path(actor) for actor in placed} <= inputs
    assert getitem.pack_path(containers.DONOR) in inputs
    # Nothing and another player's item show Zelda's Letter, whose pack is declared too
    assert getitem.pack_path(getitem.model_actor(custom_items.NOTHING)) in wanted


def test_the_app_working_set_patterns_hold_the_event_flows_and_placements():
    """Flows and placement files are not in native_inputs (a dump names a flow's version): the patterns hold them."""
    from types import SimpleNamespace

    from clawshot.pack.source import resource_spec, working_files

    data = event_props.load()
    events = {prop.event for prop in data.props if prop.event} | {hand.event for hand in data.hands}
    flows = [f"Event/EventFlow/{event}.bfevfl.zs" for event in sorted(events)]
    flows += [f"Event/EventFlow/{event}.Product.110.bfevfl.zs" for event in sorted(events)]
    bancs = sorted({prop.banc for prop in data.props if prop.banc})
    listed = [*flows, *bancs]
    assert set(listed) <= working_files(SimpleNamespace(files=listed), resource_spec())
