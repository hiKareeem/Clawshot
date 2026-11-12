"""Source-bound dungeon items: each family's native ownership fields, played lifecycles and native get text."""

import copy
import hashlib

import pytest
from test_key_bindings import GET_TEXT, ITEMS, KeyRun, compile_grants, key_analysis, key_sources, native_small_key

from clawshot.formats import byml, evfl
from clawshot.patch import keys
from clawshot.patch.key_targets import DUNGEON_TARGETS, TARGETS, DungeonGrant
from clawshot.patch.key_text import labels
from clawshot.patch.plan import PatchError

CHESTS = (keys.BIG, keys.SMALL)  # the default big and small chest lifecycles
SOURCES = (*CHESTS, "InsideTheDekuTree_GetMap", "KokiriForest_TreasureBox_NaviChatOff")
STICK = "Item_DekuStickBundle_Small"  # Deku Tree Basement Chest's native content
# What each source-specific wrapper does around its reward, with its acquisition comment (354) left out.
SOURCE_EFFECTS = {
    "InsideTheDekuTree_GetMap": ({"MapFollowUp": True, "StoryAfter": True}, [197]),
    "KokiriForest_TreasureBox_NaviChatOff": ({"MidoStart": True}, []),
}


def _bound(source, grant, content, standing="InsideTheDekuTree"):
    bindings, documents, rows, analyzed, _ = compile_grants([(source, grant)])
    return KeyRun(documents, rows, analyzed, content, standing), bindings[(source, grant)].event, documents


def _granted(state, grant):
    """``state`` after the native pickup of ``grant``'s family credited its target dungeon."""
    expected = copy.deepcopy(state)
    if grant.family == "SmallKey":
        native_small_key(expected, grant.target)
        if not grant.named:
            expected["UI_RequestSmallKeyCountUpDemo"] = True
    else:
        expected[grant.field] = True
    return expected


def _written(transforms):
    documents, rows = key_sources()
    originals = {keys.flow_path(name): evfl.write(document) for name, document in documents.items()}
    originals[keys.SETTINGS] = byml.write(rows)
    originals[keys.ANALYZED] = byml.write(key_analysis(rows))
    return {path: transform(originals[path]) for path, transform in transforms.items()}


@pytest.mark.parametrize("standing", ["InsideTheDekuTree", "ForestTemple"], ids=["off-area", "same-area"])
@pytest.mark.parametrize("family", ITEMS)
@pytest.mark.parametrize("source", CHESTS)
def test_bound_item_sets_exactly_its_targets_native_fields_and_keeps_native_presentation(source, family, standing):
    grant = DungeonGrant("ForestTemple", family)
    run, event, documents = _bound(source, grant, ITEMS[family], standing)
    expected = _granted(run.state, grant)
    run.event(event)
    # Only the target's own fields: no standing-dungeon credit, no second count, no generic pouch grant.
    assert run.state == expected
    assert run.pouch == []
    assert not [operation for operation in run.trace if operation.startswith("EventGetDungeon")]
    # The native window and text name the item itself; nothing comments on another item.
    assert run.windows == [ITEMS[family]]
    assert run.messages == GET_TEXT
    assert run.balloons == []
    if source == keys.BIG:
        assert run.trace[-1] == "EventTriggerRequestOpenPickUpWindow"
        assert ("EventTriggerSetDisplayBossKey" in run.trace) == (family == "BossKey")
    else:
        assert run.trace[-1] == "EventTriggerRequestAutoSave"
    entries = [entry.name for entry in documents[keys.POUCH].flowchart.entry_points]
    assert (keys.HELPER in entries) == (family == "SmallKey")


@pytest.mark.parametrize("source", CHESTS)
def test_own_small_key_requests_the_counter_demo_once_after_its_counters(source):
    run, event, _ = _bound(source, DungeonGrant("ForestTemple", "SmallKey"), ITEMS["SmallKey"], "ForestTemple")
    run.event(event)
    fields = [name for name, _ in run.writes]
    assert fields.count("UI_RequestSmallKeyCountUpDemo") == 1
    assert fields[-1] == "UI_RequestSmallKeyCountUpDemo"
    counters = ("SmallKeyNum", "SmallKeyTotalNum", "IsGetSmallKeyOnce")
    assert {f"DungeonInfo.ForestTemple.{field}" for field in counters} <= set(fields[:-1])


@pytest.mark.parametrize("source", CHESTS)
def test_repeated_own_small_keys_follow_the_native_routine_across_spending(source):
    target = "ForestTemple"
    run, event, _ = _bound(source, DungeonGrant(target, "SmallKey"), ITEMS["SmallKey"], target)
    model = copy.deepcopy(run.state)
    for step in ["get", "get", "use", "use", "use", "get", "use", "get", "get"]:
        run.state["UI_RequestSmallKeyCountUpDemo"] = model["UI_RequestSmallKeyCountUpDemo"] = False
        if step == "get":
            run.event(event)
            native_small_key(model, target)
            model["UI_RequestSmallKeyCountUpDemo"] = True
        else:
            # A locked door spends through the native routine (-1, refused at zero), not through a chest flow.
            native_small_key(run.state, target, -1)
            native_small_key(model, target, -1)
        assert run.state == model
    assert run.state[f"DungeonInfo.{target}.SmallKeyNum"] == 2
    assert run.state[f"DungeonInfo.{target}.SmallKeyTotalNum"] == 5
    assert run.state[f"DungeonInfo.{target}.IsGetSmallKeyOnce"] is True


@pytest.mark.parametrize("remaining", [0, 1, 3])
def test_own_small_key_sets_the_first_key_flag_only_from_zero(remaining):
    grant = DungeonGrant("ForestTemple", "SmallKey")
    run, event, _ = _bound(keys.SMALL, grant, ITEMS["SmallKey"], "ForestTemple")
    run.state["DungeonInfo.ForestTemple.SmallKeyNum"] = remaining
    run.state["DungeonInfo.ForestTemple.SmallKeyTotalNum"] = remaining + 2
    expected = _granted(run.state, grant)
    run.event(event)
    assert run.state == expected
    assert run.state["DungeonInfo.ForestTemple.IsGetSmallKeyOnce"] is (remaining == 0)


def test_named_key_own_key_and_map_for_one_target_stay_distinct():
    source = keys.SMALL
    named = DungeonGrant("ForestTemple", "SmallKey", named=True)
    own = DungeonGrant("ForestTemple", "SmallKey")
    map_ = DungeonGrant("ForestTemple", "Map")
    bindings, documents, rows, analyzed, _ = compile_grants([(source, named), (source, own), (source, map_)])
    source_id = hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]
    # Off-dungeon keys keep their 0.2.0 event names; other grants are named by family and target.
    assert bindings[(source, named)].event == f"Clawshot_Key_ForestTemple_{source_id}"
    assert bindings[(source, own)].event == f"Clawshot_Key_SmallKey_ForestTemple_{source_id}"
    assert bindings[(source, map_)].event == f"Clawshot_Key_Map_ForestTemple_{source_id}"
    for grant, text in [(named, list(labels("ForestTemple"))), (own, GET_TEXT), (map_, GET_TEXT)]:
        run = KeyRun(documents, rows, analyzed, ITEMS[grant.family], "ForestTemple")
        expected = _granted(run.state, grant)
        run.event(bindings[(source, grant)].event)
        assert run.state == expected
        assert run.messages == text
        assert run.pouch == []


@pytest.mark.parametrize(
    "grant",
    [DungeonGrant("InsideTheDekuTree", "Compass"), *(DungeonGrant("ForestTemple", family) for family in ITEMS)],
    ids=lambda grant: grant.id,
)
@pytest.mark.parametrize("source", SOURCE_EFFECTS)
def test_source_specific_wrapper_keeps_its_story_but_not_the_old_item_comment(source, grant):
    run, event, _ = _bound(source, grant, ITEMS[grant.family])
    effects, balloons = SOURCE_EFFECTS[source]
    expected = _granted(run.state, grant)
    expected.update(effects)
    run.event(event)
    assert run.state == expected
    assert run.balloons == balloons
    assert run.messages == GET_TEXT
    assert run.windows == [ITEMS[grant.family]]
    assert run.pouch == []


@pytest.mark.parametrize("source", SOURCE_EFFECTS)
def test_content_only_binding_is_the_native_event_without_its_acquisition_comment(source):
    grant = DungeonGrant("", "Content")
    bindings, documents, rows, analyzed, _ = compile_grants([(source, grant)])
    bound = KeyRun(documents, rows, analyzed, STICK)
    bound.event(bindings[(source, grant)].event)
    native = KeyRun(documents, rows, analyzed, STICK)
    native.event(source)
    assert bound.balloons == [index for index in native.balloons if index != 354]
    assert (bound.state, bound.messages, bound.windows, bound.pouch) == (
        native.state,
        native.messages,
        native.windows,
        native.pouch,
    )
    assert bound.pouch == [STICK]
    # Besides the comment, the bound event differs only by the played handoff into the chest's content.
    handoff = {"EventNaviRequestBallonMessage", "EventTriggerParticipateEvent", "EventTransition"}
    assert [op for op in bound.trace if op not in handoff] == [op for op in native.trace if op not in handoff]
    assert keys.HELPER not in [entry.name for entry in documents[keys.POUCH].flowchart.entry_points]


def test_every_family_binding_appends_only_and_native_events_behave_as_before():
    requests = [(source, DungeonGrant("ForestTemple", family)) for source in SOURCES for family in ITEMS]
    requests += [(source, DungeonGrant("FireTemple", "SmallKey", named=True)) for source in SOURCES]
    requests += [(source, DungeonGrant("", "Content")) for source in SOURCES]
    _, written, new_rows, new_analyzed, _ = compile_grants(requests)
    documents, rows = key_sources()
    analyzed = key_analysis(rows)
    for name, document in documents.items():
        chart, old = written[name].flowchart, document.flowchart
        assert chart.events[: len(old.events)] == old.events
        assert chart.entry_points[: len(old.entry_points)] == old.entry_points
        for actor, prior in zip(chart.actors, old.actors, strict=True):
            assert (actor.name, actor.secondary_name, actor.entry_point) == (
                prior.name,
                prior.secondary_name,
                prior.entry_point,
            )
            assert actor.actions[: len(prior.actions)] == prior.actions
            assert actor.queries[: len(prior.queries)] == prior.queries
    native_ids = {row["__RowId"] for row in rows}
    assert [row for row in new_rows if row["__RowId"] in native_ids] == rows
    assert [row for row in new_analyzed if row["__RowId"] in native_ids] == analyzed
    for source in SOURCES:
        for content in [*ITEMS.values(), STICK]:
            before = KeyRun(documents, rows, analyzed, content)
            before.event(source)
            after = KeyRun(written, new_rows, new_analyzed, content)
            after.event(source)
            assert after.observed() == before.observed()


def test_mixed_requests_are_keyed_by_request_and_compile_independently_of_order():
    requests = [
        (keys.BIG, DungeonGrant("ForestTemple", "Map")),
        (keys.SMALL, DungeonGrant("ForestTemple", "SmallKey")),
        (keys.SMALL, DungeonGrant("FireTemple", "SmallKey", named=True)),
        ("InsideTheDekuTree_GetMap", DungeonGrant("InsideTheDekuTree", "Compass")),
        ("KokiriForest_TreasureBox_NaviChatOff", DungeonGrant("", "Content")),
        (keys.BIG, DungeonGrant("FireTemple", "BossKey")),
    ]
    a, _, _, _, transforms_a = compile_grants(requests)
    b, _, _, _, transforms_b = compile_grants([*reversed(requests), requests[2], requests[0]])
    assert set(a) == set(requests)
    assert a == b
    assert _written(transforms_a) == _written(transforms_b)


def test_every_target_and_family_event_name_fits_the_string64_parameter():
    keyed = {target.id for target in TARGETS.values()}
    grants = [
        DungeonGrant(target.id, family)
        for target in DUNGEON_TARGETS.values()
        for family in ITEMS
        if family != "SmallKey" or target.id in keyed
    ]
    grants += [DungeonGrant(target, "SmallKey", named=True) for target in sorted(keyed)]
    bindings, _, new_rows, _, _ = compile_grants([(source, grant) for source in SOURCES for grant in grants])
    _, rows = key_sources()
    native_ids = {row["__RowId"] for row in rows}
    added = [row["__RowId"] for row in new_rows if row["__RowId"] not in native_ids]
    assert {binding.event for binding in bindings.values()} <= set(added)
    assert max(len(name.encode("utf-8")) for name in added) < 64


@pytest.mark.parametrize(
    ("grant", "message"),
    [
        (DungeonGrant("HyruleField", "Map"), "unsupported dungeon-item target"),
        (DungeonGrant("ForestTemple", "Ocarina"), "unsupported dungeon-item family"),
        (DungeonGrant("InsideTheDekuTree", "SmallKey"), "unsupported small-key target"),
    ],
)
def test_unsupported_grant_is_refused_without_touching_the_inputs(grant, message):
    documents, rows = key_sources()
    analyzed = key_analysis(rows)
    before = copy.deepcopy((documents, rows, analyzed))
    with pytest.raises(PatchError, match=message):
        keys.compile_bindings(documents, rows, analyzed, [(keys.SMALL, grant)])
    assert (documents, rows, analyzed) == before


@pytest.mark.parametrize(
    "grant",
    [
        DungeonGrant("ForestTemple", "SmallKey", named=True),
        DungeonGrant("ForestTemple", "SmallKey"),
        DungeonGrant("ForestTemple", "Map"),
    ],
    ids=["named", "own", "map"],
)
@pytest.mark.parametrize("source", CHESTS)
def test_pouch_grant_an_earlier_patch_made_literal_is_refused_not_overwritten(source, grant):
    # An earlier transform (bags before keys) left the shared grant naming one item instead of its argument.
    documents, rows = key_sources()
    pouch_grant = next(event for event in documents[keys.POUCH].flowchart.events if event.name == "Grant")
    pouch_grant.params["Actor"] = "Item_BombBag_Small"
    before = copy.deepcopy(documents)
    with pytest.raises(PatchError, match="unexpected pouch grant"):
        keys.compile_bindings(documents, rows, key_analysis(rows), [(source, grant)])
    assert documents == before
