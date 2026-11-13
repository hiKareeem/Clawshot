"""Tier choice precedes the native window/grant; native callers and keys stay fixed."""

from itertools import combinations

import pytest
from test_key_bindings import KeyRun, key_analysis, key_sources

from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import keys, progressive, progressive_bonus
from clawshot.patch.events import load as chest_events
from clawshot.patch.plan import ChestChange, Plan
from clawshot.progressive import CHAINS


def selected_actor(document, entry, owned, mp_max=0):
    """Execute serialized selector nodes up to its call into the unchanged native grant."""
    chart = document.flowchart
    index = chart.entry_point(entry).main_event
    seen = set()
    while True:
        assert index not in seen, (entry, index)
        seen.add(index)
        event = chart.events[index]
        if isinstance(event, evfl.SubFlowEvent):
            assert event.flowchart == ""
            assert event.entry_point in {
                "GetPouchContentByActorNameForTreasureBox",
                "GetPouchContentByActorNameForShowPickUpWindow",
                "DisplayGetByActorName",
            }
            return event.params["ActorName"]
        assert isinstance(event, evfl.SwitchEvent), event
        actor = chart.actors[event.actor]
        operation = actor.queries[event.query]
        if operation == "EventQueryIsGameDataInt":
            assert event.params["GameDataName"] == "PlayerStatus.MPMax"
            value = event.params["Value"]
            result = 0 if mp_max < value else 1 if mp_max == value else 2
        else:
            assert operation == "EventQueryIsGameDataBool"
            result = 0 if event.params["GameDataName"] in owned else 1
        index = dict(event.cases)[result]


def compile_synthetic(requests):
    documents, rows = key_sources()
    analysis = key_analysis(rows)
    originals = {keys.flow_path(name): evfl.write(document) for name, document in documents.items()}
    originals.update({keys.SETTINGS: byml.write(rows), keys.ANALYZED: byml.write(analysis)})
    bindings, transforms = progressive.compile_bindings(documents, rows, analysis, requests)
    written = {path: transform(originals[path]) for path, transform in transforms.items()}
    return bindings, written, documents, rows, analysis


@pytest.mark.parametrize("family", CHAINS)
def test_every_ownership_subset_selects_next_tier_without_downgrade(family):
    _, written, _, _, _ = compile_synthetic([(keys.SMALL, family)])
    document = evfl.read(written[keys.flow_path(keys.POUCH)])
    entries = [entry.name for entry in document.flowchart.entry_points if entry.name.startswith("Clawshot_")]
    assert len(entries) == 1
    tiers = CHAINS[family]
    for size in range(len(tiers) + 1):
        for held in combinations(range(len(tiers)), size):
            expected = min(max(held, default=-1) + 1, len(tiers) - 1)
            if family in {"Progressive Strength", "Progressive Quiver", "Progressive Slingshot"} and 0 not in held:
                expected = 0
            owned = {f"IsGet.{tiers[index].owned}" for index in held}
            assert selected_actor(document, entries[0], owned) == tiers[expected].actor, (family, held)


@pytest.mark.parametrize("mp_max", [0, 24, 48])
def test_existing_native_magic_capacity_advances_without_requiring_the_fairy_item_flag(mp_max):
    _, written, _, _, _ = compile_synthetic([(keys.SMALL, "Progressive Magic")])
    document = evfl.read(written[keys.flow_path(keys.POUCH)])
    entry = next(entry.name for entry in document.flowchart.entry_points if entry.name.startswith("Clawshot_"))
    expected = "Item_FairyBless_MP" if mp_max == 0 else "Item_FairyBless_MPDouble"
    assert selected_actor(document, entry, set(), mp_max) == expected


def test_compilation_preserves_native_callers_and_request_order():
    requests = [(source, family) for source in (keys.SMALL, keys.BIG) for family in CHAINS]
    bindings, written, documents, rows, analysis = compile_synthetic(requests)
    other, reversed_written, _, _, _ = compile_synthetic(list(reversed(requests)))
    assert bindings == other
    assert written == reversed_written
    for name, original in documents.items():
        path = keys.flow_path(name)
        if path not in written:
            continue
        parsed = evfl.read(written[path]).flowchart
        native = original.flowchart
        assert parsed.events[: len(native.events)] == native.events
        assert parsed.entry_points[: len(native.entry_points)] == native.entry_points
    assert max(len(binding.event.encode()) for binding in bindings.values()) < 64
    assert {row["__RowId"] for row in rows} <= {row["__RowId"] for row in byml.read(written[keys.SETTINGS])}
    assert {row["__RowId"] for row in analysis} <= {row["__RowId"] for row in byml.read(written[keys.ANALYZED])}


@pytest.mark.parametrize("order", [(keys.SMALL, keys.BIG), (keys.BIG, keys.SMALL)])
def test_owned_base_actor_never_turns_a_second_copy_into_a_display_only_reward(order):
    documents, rows = key_sources()
    # Authored capacity refusal, matching the native big/small Event25/Event17:
    # a full base item displays without giving. Progressive source clones must
    # preserve that behavior for native callers, but not apply it to the next tier.
    for flow, entry in ((keys.SMALL, "Success_"), (keys.BIG, "Success")):
        chart = documents[flow].flowchart
        if flow == keys.BIG:
            # The base key fixture omits the ordinary item's popup continuation.
            # Native big Event83 -> Event21 has it (real-dump proof above).
            grant = next(event for event in chart.events if event.name == "Event90")
            grant.next = next(index for index, event in enumerate(chart.events) if event.name == "Event21")
        ai = len(chart.actors)
        chart.actors.append(evfl.Actor("PouchSystemActor", queries=["EventQueryCanAddToPorch"]))
        old_start = chart.entry_point(entry).main_event
        display = len(chart.events)
        chart.events.append(
            evfl.SubFlowEvent(
                "FullDisplayOnly",
                keys.POUCH,
                "DisplayGetByActorName",
                params={"ActorName": evfl.Argument("ContentName")},
            )
        )
        gate = len(chart.events)
        chart.events.append(
            evfl.SwitchEvent(
                "CapacityGate",
                ai,
                0,
                [(0, old_start), (1, old_start), (2, display)],
                {"Actor": evfl.Argument("ContentName")},
            )
        )
        chart.entry_point(entry).main_event = gate
        chart.entry_point(entry).sub_flow_events = sorted(
            index for index in keys._reachable(chart, gate) if isinstance(chart.events[index], evfl.SubFlowEvent)
        )
    analysis = key_analysis(rows)
    requests = [(source, "Progressive Hookshot") for source in order]
    bindings, transforms = progressive.compile_bindings(documents, rows, analysis, requests)
    written = {
        name: evfl.read(transforms[keys.flow_path(name)](evfl.write(document)))
        if keys.flow_path(name) in transforms
        else document
        for name, document in documents.items()
    }
    new_rows = byml.read(transforms[keys.SETTINGS](byml.write(rows)))
    new_analysis = byml.read(transforms[keys.ANALYZED](byml.write(analysis)))
    run = KeyRun(written, new_rows, new_analysis, "Item_Hookshot")
    for source in order:
        run.event(bindings[(source, "Progressive Hookshot")].event)
    assert run.pouch == ["Item_Hookshot", "Item_Longshot"]
    assert run.windows == ["Item_Hookshot", "Item_Longshot"]
    assert run.stock == {"Item_Hookshot": 1, "Item_Longshot": 1}
    assert run.pickups == ["Item_Hookshot", "Item_Longshot"]
    # A native caller still follows its original capacity-refusal path.
    run.event(order[-1])
    assert run.pouch == ["Item_Hookshot", "Item_Longshot"]
    assert run.windows[-1] == "Item_Hookshot"


@pytest.mark.dump
def test_real_dump_production_chest_patch_selects_every_native_tier_before_window(romfs):
    """Production changes(), source bindings, persistent field validation and serialized native flows."""
    from clawshot.census.scan import CHEST, scan

    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    sources = [location for location in scan(romfs) if location.kind == CHEST and keys.source_for(location.actor)]
    classifications = chest_events()
    changes = []
    for (family, tiers), chest in zip(CHAINS.items(), sources, strict=False):
        event = classifications.get(chest.event)
        kept = event if event is not None and event.patch != "remove" else None
        changes.append(
            ChestChange(
                family,
                chest.id,
                family,
                chest.files,
                chest.actor,
                family,
                chest.vanilla_item,
                tiers[0].actor,
                event if kept is None else None,
                kept_event=kept,
            )
        )
    plan, transforms = progressive.changes(romfs, Plan(changes, [], []))
    assert len(plan.changes) == len(CHAINS)
    actual = {}
    for path, transform in transforms.items():
        native = dictionaries.decompress(path, (romfs / path).read_bytes())
        actual[path] = transform(native)
    pouch = evfl.read(actual[keys.flow_path(keys.POUCH)])
    settings = byml.read(actual[keys.SETTINGS])
    analyzed = byml.read(actual[keys.ANALYZED])
    assert {change.key_event for change in plan.changes} <= {row["__RowId"] for row in settings}
    assert {change.key_event for change in plan.changes} <= {row["__RowId"] for row in analyzed}
    for family, tiers in CHAINS.items():
        prefix = f"Clawshot_Content_{family.replace(' ', '')}_"
        entries = [entry.name for entry in pouch.flowchart.entry_points if entry.name.startswith(prefix)]
        assert entries, family
        owned = set()
        for tier in tiers:
            for entry in entries:
                assert selected_actor(pouch, entry, owned) == tier.actor, (family, tier, entry)
            owned.add(f"IsGet.{tier.owned}")
        for entry in entries:
            assert selected_actor(pouch, entry, owned) == tiers[-1].actor


@pytest.mark.parametrize(
    ("family", "native_index"),
    [("Progressive Strength", 0), ("Progressive Scale", 0), ("Progressive Scale", 1)],
)
def test_late_native_bonus_skips_unsafe_regrant_without_losing_quest_or_once_progress(family, native_index):
    documents, _ = key_sources()
    content = CHAINS[family][native_index].actor
    source = evfl.Flowchart(
        "NativeBonus",
        [evfl.Actor("GameSystemActor")],
        [
            evfl.SubFlowEvent(
                "Gift", keys.POUCH, "GetPouchContentByActorNameForTreasureBox", 1, {"ActorName": content}
            ),
            evfl.SubFlowEvent("FinishQuest", "NativeQuest", "Finish"),
        ],
        [evfl.EntryPoint("Give", 0, [0, 1])],
    )
    quest = evfl.Flowchart(
        "NativeQuest",
        [
            evfl.Actor(
                "GameDataActor",
                actions=["EventTriggerAddOrSubGameDataInt", "EventTriggerSetGameDataBool"],
                queries=["EventQueryIsGameDataBool"],
            )
        ],
        [
            evfl.SwitchEvent("Once", 0, 0, [(0, evfl.NONE), (1, 1)], {"GameDataName": "NativeOnce"}),
            evfl.SubFlowEvent("Source", "NativeBonus", "Give"),
            evfl.ActionEvent("Advance", 0, 0, 3, {"GameDataName": "NativeQuestStep", "Value": 1}),
            evfl.ActionEvent("MarkOnce", 0, 1, params={"GameDataName": "NativeOnce", "Value": True}),
        ],
        [evfl.EntryPoint("Start", 0, [1]), evfl.EntryPoint("Finish", 2)],
    )
    progressive_bonus.guard_grants(source, documents[keys.POUCH].flowchart, {"Gift": content})
    for chart in (source, quest):
        documents[chart.name] = evfl.EventFlowFile(chart.name, chart)
    documents = {name: evfl.read(evfl.write(document)) for name, document in documents.items()}
    tiers = CHAINS[family]
    for size in range(len(tiers) + 1):
        for held in combinations(range(len(tiers)), size):
            run = KeyRun(documents, [], [])
            run.state.update({"NativeOnce": False, "NativeQuestStep": 0})
            run.state.update({f"IsGet.{tiers[index].owned}": True for index in held})
            # Child Bracelet is separate from adult gauntlets. Other native
            # lower/equal tiers must never enter their unsafe native add handler.
            blocked = 0 in held if family == "Progressive Strength" else any(index >= native_index for index in held)
            run.entry("NativeQuest", "Start", {})
            assert run.pouch == ([] if blocked else [content]), (family, native_index, held)
            assert run.state["NativeQuestStep"] == 1
            assert run.state["NativeOnce"] is True
            # Repeating the native interaction does not re-grant or repeat its quest step.
            run.entry("NativeQuest", "Start", {})
            assert run.pouch == ([] if blocked else [content])
            assert run.state["NativeQuestStep"] == 1
