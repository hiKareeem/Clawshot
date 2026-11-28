"""Saria's farewell fix: the bridge Saria gets an actor and schedule list of her own (spec event-items 4.4; plan 13.1;
played as arm N9, BBender 2026-11-25)."""

import pytest

from clawshot.formats import byml, evfl, sarc
from clawshot.formats.evfl import ActionEvent, Actor, Clip, EntryPoint, EventFlowFile, Flowchart, Timeline
from clawshot.patch import saria_farewell as fix
from clawshot.patch.actor_packs import actor_member
from clawshot.patch.plan import PatchError

HOLD = byml.U32(1627154745)
INFO = "Component/ModelInfo/x.bgyml"


def schedule() -> bytes:
    setting = {"ArrivalAS": "Act_SitChair_Wait", "EquipmentStateWhenWait": HOLD, "EquipmentStateWhenWalk": HOLD}
    warp_done = {"ActionSchedule": [{"Setting": setting}], "ConditionFlag": fix.WARP_DONE}
    other = {"ActionSchedule": [{"Setting": {"ArrivalAS": "Act_Sad_Wait"}}], "ConditionFlag": "After"}
    return byml.write({"ConditionalSchedule": [warp_done, other], "DefaultSchedule": {}})


def test_her_own_schedule_list_is_sarias_without_hold_on_the_warpdone_entry():
    out = byml.read(fix.schedule_without_hold(schedule()))
    native = byml.read(schedule())
    assert out["ConditionalSchedule"][0]["ActionSchedule"][0]["Setting"] == {"ArrivalAS": "Act_SitChair_Wait"}
    assert out["ConditionalSchedule"][1:] == native["ConditionalSchedule"][1:]
    assert out["DefaultSchedule"] == native["DefaultSchedule"]


def saria_pack() -> dict[str, bytes]:
    components = {"AIScheduleRef": "?" + fix.schedule_path(fix.SARIA), "ModelInfoRef": "?" + INFO}
    param = {"$parent": "Work/Actor/Npc_Kokiri_WC_Default.gyml", "Components": components}
    return {actor_member(fix.SARIA): byml.write(param), INFO: byml.write({"FmdbName": "Npc_Kokiri_WC_Saria"})}


def test_her_actor_is_sarias_pack_with_its_own_param_pointing_at_her_own_list():
    new = fix.actor_pack(saria_pack())
    members = sarc.read(new.data)
    assert actor_member(fix.SARIA) not in members
    param = byml.read(members[actor_member(fix.FAREWELL)])
    native = byml.read(saria_pack()[actor_member(fix.SARIA)])
    assert param["Components"]["AIScheduleRef"] == "?" + fix.schedule_path(fix.FAREWELL)
    assert param["Components"]["ModelInfoRef"] == native["Components"]["ModelInfoRef"]
    assert param["$parent"] == native["$parent"]
    assert new.copied == {INFO: fix.pack_path(fix.SARIA)}


def test_her_rows_are_copies_of_sarias_inserted_by_name():
    rows = byml.write([{"__RowId": "A"}, {"__RowId": fix.SARIA, "FmdbName": "Saria"}, {"__RowId": "Z"}])
    out = byml.read(fix.rows_transform("t")(rows))
    assert [r["__RowId"] for r in out] == ["A", fix.SARIA, fix.FAREWELL, "Z"]
    assert out[2] == {"__RowId": fix.FAREWELL, "FmdbName": "Saria"}
    with pytest.raises(PatchError):
        fix.rows_transform("t")(byml.write(out))


def placements(name=fix.INSTANCE) -> bytes:
    village = {"Gyaml": fix.SARIA, "Hash": byml.U64(1)}
    bridge = {"Gyaml": fix.SARIA, "Hash": byml.U64(fix.PLACEMENT_HASH), "Name": name}
    return byml.write({"Actors": [village, bridge]})


def test_only_the_bridge_placement_uses_her_actor():
    out = byml.read(fix.placement_transform(placements()))["Actors"]
    assert [a["Gyaml"] for a in out] == [fix.SARIA, fix.FAREWELL]
    with pytest.raises(PatchError):
        fix.placement_transform(placements(name="Elsewhere"))


def hand_over() -> EventFlowFile:
    chart = Flowchart(
        "Dm_Kokiri_0155",
        [
            Actor(fix.SARIA, fix.INSTANCE, actions=["EventPlayAS"]),
            Actor("Dm_Item_Ocarina_Fairy_Saria", "saria", actions=["EventTriggerModelBind"]),
            Actor("EventCamera", actions=["Move"]),
        ],
        [
            ActionEvent("Event7", 1, 0, next=1, params={"ActorName": fix.SARIA, "InstanceName": fix.INSTANCE}),
            ActionEvent(
                "Event38", 2, 0, params={"TargetActorName": fix.SARIA, "TargetActorInstanceName": fix.INSTANCE}
            ),
            ActionEvent("Event9", 2, 0, params={"TargetActorName": fix.SARIA, "TargetActorInstanceName": "Other"}),
        ],
        [EntryPoint("C01", 0)],
    )
    return EventFlowFile("Dm_Kokiri_0155", flowchart=chart)


def test_the_flows_name_her_actor_wherever_they_name_the_bridge_instance_and_nowhere_else():
    out = evfl.read(fix.flow_transform("Dm_Kokiri_0155")(evfl.write(hand_over()))).flowchart
    assert (out.actors[0].name, out.actors[0].secondary_name) == (fix.FAREWELL, fix.INSTANCE)
    assert out.events[0].params["ActorName"] == fix.FAREWELL
    assert out.events[1].params["TargetActorName"] == fix.FAREWELL
    assert out.events[2].params["TargetActorName"] == fix.SARIA  # another instance keeps Saria


def test_a_timeline_clip_binding_to_her_is_renamed_too():
    timeline = Timeline(
        "Dm_Kokiri_0150",
        10.0,
        actors=[Actor(fix.SARIA, fix.INSTANCE, actions=["Play"]), Actor("Prop", "0", actions=["Bind"])],
        clips=[Clip(0.0, 1.0, 1, 0, params={"BindActorName": fix.SARIA, "BindInstanceName": fix.INSTANCE})],
    )
    document = EventFlowFile("Dm_Kokiri_0150", timeline=timeline)
    assert fix.rename(document) == 2
    assert document.timeline.actors[0].name == fix.FAREWELL
    assert document.timeline.clips[0].params["BindActorName"] == fix.FAREWELL


def test_the_app_working_set_holds_the_farewell_inputs():
    from types import SimpleNamespace

    from clawshot.pack.source import resource_spec, working_files

    inputs = set(fix.native_inputs())
    assert {fix.pack_path(fix.SARIA), fix.schedule_path(fix.SARIA), fix.PLACEMENT_FILE, *fix.TABLES} <= inputs
    wanted = working_files(SimpleNamespace(files=[]), resource_spec())
    assert inputs <= wanted, sorted(inputs - wanted)
