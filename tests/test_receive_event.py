"""The receive event (clawshot.patch.receive_event) and the one-box get window (custom_items.single_box), on synthetic
flows and tables."""

import pytest

from clawshot.formats import byml, evfl
from clawshot.patch import custom_items, receive_event
from clawshot.patch.plan import PatchError


def donor():
    actors = [
        evfl.Actor(
            "UISystemActor", actions=["EventTriggerRequestOpenPickUpWindow"], params={"EventMemberCreateMethod": 0}
        ),
        evfl.Actor(
            "PouchSystemActor", queries=["EventQueryIsAutoSavePouchContent"], params={"EventMemberCreateMethod": 0}
        ),
    ]
    return evfl.Flowchart(receive_event.DONOR, actors=actors)


def walk(fc, actor_name, notice, recover, category=0):
    """The actions the event runs for a content (``recover``: a heart or magic refill; ``category``: its pouch
    category, 7 for rupees)."""
    args = {"ActorName": actor_name, "ShowNotice": notice}
    index, done = fc.entry_points[0].main_event, []
    while index != evfl.NONE:
        e = fc.events[index]
        assert not isinstance(e, evfl.SubFlowEvent)  # a sub-flow call from this flow crashed the game
        actor = fc.actors[e.actor]
        if isinstance(e, evfl.SwitchEvent):
            query = actor.queries[e.query]
            answer = {
                "EventQueryIsBool": 0 if args["ShowNotice"] else 1,
                "EventQueryIsRecoverHeartOrMpActor": 0 if recover else 1,
                "EventQueryCheckPouchContentCategory": category,
                "EventQueryIsRupeeMax": 1,
            }[query]
            index = dict(e.cases)[answer]
            continue
        params = {k: args.get(v, v) if isinstance(v, evfl.Argument) else v for k, v in (e.params or {}).items()}
        done.append((actor.actions[e.action], params.get("ActorName") or params.get("Actor")))
        index = e.next
    return done


def test_the_event_gives_consumables_as_the_game_does():
    fc = evfl.read(receive_event.build_flow(donor())).flowchart
    assert fc.name == receive_event.EVENT and fc.entry_points[0].name == receive_event.EVENT
    assert walk(fc, "TBox_Rupee_Blue", False, False, category=7) == [
        ("EventOpenRupeeDisplay", None),
        ("EventTriggerAddOrRemovePouchContent", "TBox_Rupee_Blue"),
        ("EventWait", None),
        ("EventCloseRupeeDisplay", None),
    ]
    assert walk(fc, "Item_BombBundle_Small", False, False, category=3) == [
        ("EventTriggerAddOrRemovePouchContent", "Item_BombBundle_Small"),
    ]
    for category in range(12):  # every category the game's flows switch on goes on
        assert ("EventTriggerAddOrRemovePouchContent", "X") in walk(fc, "X", False, False, category)
    assert walk(fc, "Obj_Heart", True, True) == [
        ("EventTriggerRequestOpenPickUpWindow", "Obj_Heart"),
        ("EventTriggerRecoverByCureItem", "Obj_Heart"),
    ]


def test_its_rows_go_in_name_order():
    setting = [
        {
            "__RowId": name,
            "EntryPointName": name,
            "EventBaseSetting": f"base/{name}",
            "EventSettingComponentList": receive_event.SUB_EVENT_LIST
            if name == receive_event.SUB_EVENT
            else f"list/{name}",
            "EventSoundSetting": f"sound/{name}",
            "FlowchartFileName": name,
        }
        for name in sorted(("A", receive_event.PLAYER_BASE, receive_event.DONOR, receive_event.SUB_EVENT, "Zz"))
    ]
    rows = byml.read(receive_event.add_event_setting(byml.write(setting)))
    ids = [r["__RowId"] for r in rows]
    assert ids == sorted(ids) and receive_event.EVENT in ids
    row = next(r for r in rows if r["__RowId"] == receive_event.EVENT)
    assert row["EventBaseSetting"] == f"base/{receive_event.PLAYER_BASE}"
    assert row["FlowchartFileName"] == f"Work/Event/EventFlow/{receive_event.EVENT}.evfc"
    # a sub-event, so Link keeps moving: the Near event's component list and sound, not the donor's AllPause list
    assert row["EventSettingComponentList"] == receive_event.SUB_EVENT_LIST
    assert row["EventSoundSetting"] == f"sound/{receive_event.SUB_EVENT}"
    analyzed = [{"__RowId": receive_event.DONOR, "SubFlowList": ["Dm_SY_Get"]}]
    row = next(
        r for r in byml.read(receive_event.add_analyzed(byml.write(analyzed))) if r["__RowId"] == receive_event.EVENT
    )
    assert row["SubFlowList"] == ["GetPouchContent"]
    with pytest.raises(PatchError, match="already has"):
        receive_event.add_analyzed(receive_event.add_analyzed(byml.write(analyzed)))


def test_the_default_get_window_is_one_box():
    talk = ["EventTalk"]
    fc = evfl.Flowchart(
        "GetPouchContent",
        actors=[evfl.Actor("SystemTextNPC", actions=talk)],
        events=[
            evfl.ActionEvent("Event16", 0, 0, 1, {"MessageId": custom_items.GET_MESSAGE}),
            evfl.ActionEvent("Event18", 0, 0, evfl.NONE, {"MessageId": custom_items.GET_CAPTION}),
        ],
        entry_points=[evfl.EntryPoint("DefaultGetMessage", 0)],
    )
    custom_items.single_box(fc)
    assert fc.events[0].next == evfl.NONE
    with pytest.raises(PatchError, match="no longer"):
        custom_items.single_box(fc)
