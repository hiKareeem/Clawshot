"""The gift patch on the player's dump: every changeable gift check, changed, gives a flow that round-trips and differs
from the game's only in the intended events, a GameDataList that differs only in the added flags, and an analyzed-event
table that differs only in Granny's Talk row."""

from copy import deepcopy

import pytest

from clawshot.census import definitions
from clawshot.census.gifts import FLOW_VERSIONS, FROG_SONG_CALL, flow_files, reachable, scan_gifts
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import byml, evfl, rstb, zsdic
from clawshot.patch import gifts
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.save import murmur3_32

NEW_ITEM = "Item_Boomerang"


@pytest.fixture(scope="module")
def context(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    versions = {str(k): str(v) for k, v in read_romfs_byml(romfs, dicts, FLOW_VERSIONS)["Versions"].items()}
    rules = gifts.load()
    placements = {check: NEW_ITEM for check, rule in rules.items() if rule.cls != gifts.MORE}
    changes = gifts.plan(placements, scan_gifts(romfs), definitions.load(), rules)
    return dicts, flow_files(romfs, versions), changes


def _intended(fc: evfl.Flowchart, flow: str, changes) -> set[int]:
    """Indices of the game's events a change may touch in ``flow``: the steps, the given reads, the display-only
    windows and Notes targets, and whatever led to a skipped step."""
    index = {e.name: i for i, e in enumerate(fc.events)}
    out = set()
    for change in changes:
        out |= {index[s.event] for s in change.steps if s.flow == flow}
        out |= {
            index[r.split("/")[1]]
            for r in (*change.rule.given, *change.rule.writes, *change.rule.once, *change.rule.display)
            if r.split("/")[0] == flow
        }
        if (
            change.check == gifts.SHOPKEEPER_CHECK
            and flow == gifts.SHOPKEEPER_FLOW
            and f"{flow}/Event45" in change.rule.once
        ):
            out.add(index["Event24"])  # Initialized dispatch keeps the uncollected offer past native cutoffs.
        if change.rule.purchase and change.check == "GC Medigoron" and flow == change.steps[0].flow:
            out |= {index["Event6"], index["Event19"]}
        if change.check == gifts.MARKET_BOTTLE_CHECK and flow == gifts.MARKET_BOTTLE_FLOW:
            out.add(index["Event6"])
        if change.check in gifts.BOWLING_CHECKS and flow == gifts.BOWLING_FLOW:
            out |= {index["Event73"], index["Event72"]}
        if change.check == gifts.DAMPE_CHECK and flow == change.steps[0].flow:
            out.add(index["Event449"])
        if change.expert and flow == change.steps[0].flow:
            out |= {index[gifts.GALLERY_EXPERT_ROUTES[s.event][0]] for s in change.steps}
        for ref in change.rule.skip:
            if ref.split("/")[0] == flow:
                i = index[ref.split("/")[1]]
                for j, e in enumerate(fc.events):
                    targets = [
                        getattr(e, "next", None),
                        *(t for _, t in getattr(e, "cases", ())),
                        *getattr(e, "forks", ()),
                    ]
                    if i in targets:
                        out.add(j)
    return out


def _same_graph(before: evfl.Flowchart, start: int, after: evfl.Flowchart, clone: int) -> None:
    """The clone is the untouched native graph: equal events, other than their names, along equal edges."""
    edges = ("name", "next", "cases", "forks", "join")
    seen: dict[int, int] = {}
    stack = [(start, clone)]
    while stack:
        a, b = stack.pop()
        if evfl.NONE in (a, b):
            assert a == b, (a, b)
            continue
        if a in seen:
            assert seen[a] == b, (before.events[a].name, after.events[b].name)
            continue
        seen[a] = b
        native, copy = before.events[a], after.events[b]
        assert type(native) is type(copy), (native, copy)
        fields = [{k: v for k, v in vars(e).items() if k not in edges} for e in (native, copy)]
        assert fields[0] == fields[1], native.name
        if hasattr(native, "cases"):
            assert [case for case, _ in native.cases] == [case for case, _ in copy.cases], native.name
            stack += [(x, y) for (_, x), (_, y) in zip(native.cases, copy.cases, strict=True)]
        if isinstance(native, evfl.ForkEvent):
            stack += [*zip(native.forks, copy.forks, strict=True), (native.join, copy.join)]
        if hasattr(native, "next"):
            stack.append((native.next, copy.next))


@pytest.mark.dump
def test_dump_each_changed_flow_round_trips_and_differs_only_where_intended(romfs, context):
    dicts, files, changes = context
    transforms = gifts.file_changes(changes, files)
    table = rstb.read(dicts.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    flows = gifts.flows_changed(changes)
    flow_paths = [path for path in transforms if path.startswith("Event/EventFlow/") and path.endswith(".bfevfl.zs")]
    # Every flow transform round-trips; only event flows count, not the known non-flow tables.
    assert len(flows) == len(flow_paths)
    assert set(transforms) - set(flow_paths) == {GAME_DATA_LIST, gifts.ANALYZED}
    report = []
    for flow in flows:
        path = files[flow]
        data = dicts.decompress(path, (romfs / path).read_bytes())
        out = transforms[path](data)
        before, after = evfl.read(data).flowchart, evfl.read(out)
        assert evfl.read(evfl.write(after)) == after, flow
        after = after.flowchart
        intended = _intended(before, flow, changes)
        changed = {i for i, (a, b) in enumerate(zip(before.events, after.events, strict=False)) if a != b}
        assert changed <= intended, (flow, sorted(changed - intended))
        added = after.events[len(before.events) :]
        for a, b in zip(before.actors, after.actors, strict=True):
            assert (a.name, a.actions, a.queries) == (b.name, b.actions[: len(a.actions)], b.queries[: len(a.queries)])
        expected_entries = deepcopy(before.entry_points)
        native_entries = set()
        for change in changes:
            if not change.rule.purchase or flow != change.steps[0].flow:
                continue
            # A saved check dispatches to an untouched clone of the native transaction; otherwise to the gift.
            entry = "Buy_BluePotion" if change.check == gifts.GRANNY_CHECK else "Talk"
            root = next(e for e in expected_entries if e.name == entry)
            gate_index = after.entry_point(entry).main_event
            gate = after.events[gate_index]
            assert after.actors[gate.actor].queries[gate.query] == gifts.READ_QUERY, flow
            assert gate.params == {"GameDataName": change.flag, "Index": -1}, flow
            done = dict(gate.cases)[0]
            assert gate.cases == [(0, done), (1, root.main_event)], flow
            call = after.events[done]
            assert isinstance(call, evfl.SubFlowEvent) and (call.flowchart, call.next) == ("", evfl.NONE), call
            native = after.entry_point(call.entry_point)
            _same_graph(before, root.main_event, after, native.main_event)
            native_entries.add(native.name)
            root.main_event = gate_index
            root.sub_flow_events = [*root.sub_flow_events, done]
        bottle = next((c for c in changes if c.check == gifts.MARKET_BOTTLE_CHECK), None)
        if bottle and flow == gifts.MARKET_BOTTLE_FLOW:
            root = next(e for e in expected_entries if e.name == "Item_Bottle_TutorialEvent_Talk")
            gate = after.events[after.entry_point(root.name).main_event]
            assert gate.params == {"GameDataName": gifts.MARKET_BOTTLE_FLAG, "Index": -1}
            assert gate.cases == [(0, before.entry_point("Talk").main_event), (1, root.main_event)]
            root.main_event = after.entry_point(root.name).main_event
        assert expected_entries == after.entry_points[: len(before.entry_points)], flow
        specialized = [s for c in changes for s in c.steps if s.flow == flow and s.call == FROG_SONG_CALL]
        extra_entries = after.entry_points[len(before.entry_points) :]
        expected_extra = {next(e for e in after.events if e.name == s.event).entry_point for s in specialized}
        expected_extra |= native_entries
        if flow == "SimpleShop":
            for change in changes:
                if change.rule.purchase and change.check in gifts.MERCHANT_SHOPS:
                    name = gifts.NEW_EVENT_PREFIX + "Purchase" + change.steps[0].flow
                    expected_extra.add(name)
                    if change.check == "Wasteland Bombchu Salesman":
                        expected_extra.add(name + "Buy")
        assert {e.name for e in extra_entries} == expected_extra, flow
        report.append(
            f"{flow}: {len(changed)} events changed, {len(added)} added, {len(data)} -> {len(out)} bytes, "
            f"size entry {table.get(path)} needs {rstb.required_size(path, len(out))}"
        )
    print("\n".join(report))


@pytest.mark.dump
def test_dump_granny_purchase_preload_round_trips_and_changes_only_its_talk_row(romfs, context):
    dicts, files, changes = context
    transforms = gifts.file_changes(changes, files)
    raw = dicts.decompress(gifts.ANALYZED, (romfs / gifts.ANALYZED).read_bytes())
    before = byml.read(raw)
    encoded = transforms[gifts.ANALYZED](raw)
    after = byml.read(encoded)
    assert byml.read(byml.dump(byml.load(encoded))) == after
    changed = [(old, new) for old, new in zip(before, after, strict=True) if old != new]
    assert len(changed) == 1, changed
    original, updated = changed[0]
    assert original["__RowId"] == "Npc_Hylia_053_Adult_D_T"
    assert updated == {**original, "SubFlowList": sorted(set(original["SubFlowList"]) | {"Dm_SY_Get"})}


@pytest.mark.dump
def test_dump_every_step_gives_the_new_item_and_given_reads_read_the_flag(romfs, context):
    dicts, files, changes = context
    transforms = gifts.file_changes(changes, files)
    trees = {}
    for flow in gifts.flows_changed(changes):
        path = files[flow]
        trees[flow] = evfl.read(transforms[path](dicts.decompress(path, (romfs / path).read_bytes()))).flowchart
    for change in changes:
        for step in change.steps:
            event = next(e for e in trees[step.flow].events if e.name == step.event)
            if step.call == FROG_SONG_CALL:
                indices = reachable(trees[step.flow], trees[step.flow].entry_point(event.entry_point).main_event)
                grants = [
                    e
                    for i in indices
                    if isinstance(e := trees[step.flow].events[i], evfl.SubFlowEvent)
                    and e.flowchart == "Dm_SY_GetInEvent"
                ]
                assert [e.params["ActorName"] for e in grants] == [NEW_ITEM], step.id
                assert not any(
                    isinstance(e := trees[step.flow].events[i], evfl.ActionEvent)
                    and trees[step.flow].actors[e.actor].actions[e.action] == "EventTriggerIncreaseRupee"
                    for i in indices
                ), step.id
            elif change.expert:
                fc = trees[step.flow]
                mode = next(e for e in fc.events if e.name == gifts.GALLERY_EXPERT_ROUTES[step.event][0])
                gate = fc.events[dict(mode.cases)[0]]
                assert gate.params == {"GameDataName": change.flag, "Index": -1}
                grant = fc.events[dict(gate.cases)[1]]
                assert grant.params == {"ActorName": NEW_ITEM, "IsNpcEventStarter": False}
                assert event.params == {"GetRupee": gifts.GALLERY_EXPERT_RUPEES[step.event]}
                assert fc.events[dict(gate.cases)[0]].name == gifts.GALLERY_EXPERT_ROUTES[step.event][1]
                assert fc.events[grant.next].params == {
                    "GameDataName": change.flag,
                    "Index": -1,
                    "Value": True,
                }
            else:
                assert event.params[step.param] == NEW_ITEM, step.id
            if (change.new_flag or change.rule.once) and not change.rule.purchase and not change.expert:
                added = trees[step.flow].events[event.next]
                assert added.params == {"GameDataName": change.flag, "Index": -1, "Value": True}, step.id
        for ref in change.rule.given:
            flow, name = ref.split("/")
            event = next(e for e in trees[flow].events if e.name == name)
            assert event.params["GameDataName"] == change.flag, ref
        for ref in change.rule.writes:
            flow, name = ref.split("/")
            event = next(e for e in trees[flow].events if e.name == name)
            original = evfl.read(dicts.decompress(files[flow], (romfs / files[flow]).read_bytes())).flowchart
            expected = next(e for e in original.events if e.name == name)
            expected.params["GameDataName"] = change.flag
            assert event == expected  # Value stays true; a song acquired elsewhere is never cleared.
        for ref in change.rule.display:  # event-items 5.7: the written flow names the given item
            flow, name = ref.split("/")
            event = next(e for e in trees[flow].events if e.name == name)
            assert NEW_ITEM in (event.params.get("ActorName"), event.params.get("TargetID")), ref
        for ref in change.rule.skip:
            flow, name = ref.split("/")
            i = next(i for i, e in enumerate(trees[flow].events) if e.name == name)
            assert not any(
                i in (getattr(e, "next", None), *(t for _, t in getattr(e, "cases", ()))) for e in trees[flow].events
            )


@pytest.mark.dump
def test_dump_game_data_list_differs_only_in_the_added_flags(romfs, context):
    dicts, files, changes = context
    names = [c.new_flag for c in changes if c.new_flag]
    data = dicts.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes())
    out = gifts.file_changes(changes, files)[GAME_DATA_LIST](data)
    before, after = byml.read(data), byml.read(out)
    assert byml.byte_order(out) == byml.byte_order(data) == "big"
    added = after["Data"]["Bool"][len(before["Data"]["Bool"]) :]
    assert [int(e["Hash"]) for e in added] == [murmur3_32(n.encode()) for n in names]
    after["Data"]["Bool"] = after["Data"]["Bool"][: len(before["Data"]["Bool"])]
    grow = 8 * len(names)
    for key in ("SaveDataOffsetPos", "SaveDataSize"):
        assert after["MetaData"][key][0] == before["MetaData"][key][0] + grow
        after["MetaData"][key][0] = before["MetaData"][key][0]
    for key in ("AllDataSaveOffset", "AllDataSaveSize"):
        assert after["MetaData"][key] == before["MetaData"][key] + grow
        after["MetaData"][key] = before["MetaData"][key]
    assert byml.difference(before, after) is None
    print(f"{GAME_DATA_LIST}: {len(data)} -> {len(out)} bytes, {len(names)} flags")


@pytest.mark.dump
def test_dump_gift_shuffle_slice_writes_each_moved_gift(romfs, tmp_path):
    from clawshot.generate import Settings, prepare
    from clawshot.generate.fill import allowed
    from clawshot.patch import items as item_actors
    from clawshot.patch import make_seed, write_seed
    from clawshot.world.load import load_spec

    settings = Settings(
        shuffle=("Chest", gifts.SHUFFLE),
        areas=("KokiriForest", "LostWood", "InsideTheDekuTree"),
        goal="'Defeat Queen Gohma'",
    )
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), settings)
    assert gifts.SHUFFLE not in settings.shuffle and set(gifts.GIFT_TYPES) <= set(settings.shuffle)
    output = make_seed(romfs, 7, settings, spec, extra_steps=[step])
    write_seed(output, romfs, tmp_path / "seed")
    seed, actors = output.seed, item_actors.load()
    steps = gifts.check_steps(scan_gifts(romfs), definitions.load())
    moved = [n for n in seed.shuffled if n in steps and seed.placements[n] != seed.world.locations[n].vanilla]
    assert moved, "the slice moved no gift"
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    for name in moved:
        for s in steps[name]:
            data = dicts.decompress(s.file, (tmp_path / "seed" / "romfs" / s.file).read_bytes())
            event = next(e for e in evfl.read(data).flowchart.events if e.name == s.event)
            actor = actors.actor(seed.placements[name])
            assert event.params[s.param] == actor, s.id
    rules = gifts.load()
    for name in seed.shuffled:
        if name in rules:
            assert rules[name].cls != gifts.MORE, name
    print(f"moved gifts: {[(n, seed.placements[n]) for n in moved]}")

    # Bottle now has a scoped Chest lift, not a Scrub lift. Retain its native
    # hand-over coverage with a controlled NPC-to-NPC swap.
    held_spec, held_settings, held_step = gifts.seed_setup(
        romfs, load_spec(), Settings(shuffle=("Chest", gifts.SHUFFLE), songs="song")
    )
    _, held_world = prepare(held_spec, held_settings)
    held_placements = {name: loc.vanilla for name, loc in held_world.locations.items()}
    source, destination = "Kak Anju as Child", gifts.SHOPKEEPER_CHECK
    held_placements[source], held_placements[destination] = (
        held_placements[destination],
        held_placements[source],
    )
    held = held_settings.item_location_types
    assert held_placements[destination] == "Bottle"
    assert allowed(held_world, held_settings, "KF Midos Top Left Chest", "Bottle")
    assert not allowed(held_world, held_settings, "LW Deku Scrub Near Bridge", "Bottle")
    transforms = held_step(held_placements)
    for name in (source, destination):
        item = held_placements[name]
        if item in held:
            assert held_world.locations[name].type in held[item], (name, item)
        for s in steps[name]:
            original = dicts.decompress(s.file, (romfs / s.file).read_bytes())
            event = next(e for e in evfl.read(transforms[s.file](original)).flowchart.events if e.name == s.event)
            actor = actors.actor(item)
            assert event.params[s.param] == actor, s.id


@pytest.mark.dump
def test_dump_gift_shuffle_moves_great_fairies_through_their_new_flags(romfs):
    from clawshot.generate import Settings, prepare
    from clawshot.world.load import load_spec

    spec, settings, step = gifts.seed_setup(romfs, load_spec(), Settings(shuffle=(gifts.SHUFFLE,)))
    fairies = {n: info for n, info in spec["locations"].items() if n.endswith("Great Fairy Reward")}
    moving = sorted(n for n, info in fairies.items() if not info.get("keep_vanilla"))
    # All six sources shuffle; the two Magic Meter prizes donate copies to eligible chests.
    assert moving == [
        "Colossus Great Fairy Reward",
        "DMC Great Fairy Reward",
        "DMT Great Fairy Reward",
        "HC Great Fairy Reward",
        "OGC Great Fairy Reward",
        "ZF Great Fairy Reward",
    ]
    _, world = prepare(spec, settings)
    placements = {name: loc.vanilla for name, loc in world.locations.items()}
    baseline = step(placements)  # admitted merchants normalize their saved checks even when unmoved
    placements["DMT Great Fairy Reward"], placements["ZF Great Fairy Reward"] = "Farores Wind", "Dins Fire"
    transforms = step(placements)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    data = dicts.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes())
    before = {int(e["Hash"]) for e in byml.read(baseline[GAME_DATA_LIST](data))["Data"]["Bool"]}
    added = {int(e["Hash"]) for e in byml.read(transforms[GAME_DATA_LIST](data))["Data"]["Bool"]} - before
    # the Din flag's name is the one Kareem's save showed set (03-game-data.md section 19, in game)
    assert len(added) == 2 and murmur3_32(b"Clawshot.Gift.Dm_FairyFountain_Din.Event212") in added
    steps = gifts.check_steps(scan_gifts(romfs), definitions.load())
    for name, actor in (("DMT Great Fairy Reward", "Item_FaroreWind"), ("ZF Great Fairy Reward", "Item_DinFire")):
        for s in steps[name]:
            out = transforms[s.file](dicts.decompress(s.file, (romfs / s.file).read_bytes()))
            event = next(e for e in evfl.read(out).flowchart.events if e.name == s.event)
            assert event.params[s.param] == actor, s.id


@pytest.mark.dump
def test_dump_gift_setup_moves_granny_from_her_five_rupees_and_holds_no_blue_potion(romfs):
    from clawshot.generate import Settings, prepare
    from clawshot.generate.fill import shuffled_locations
    from clawshot.patch import items
    from clawshot.world.load import load_spec

    spec, settings, step = gifts.seed_setup(romfs, load_spec(), Settings(shuffle=("Chest", gifts.SHUFFLE)))
    _, world = prepare(spec, settings)
    assert gifts.GRANNY_CHECK in shuffled_locations(world, settings)
    assert world.locations[gifts.GRANNY_CHECK].vanilla == gifts.GRANNY_POOL_ITEM
    assert all(location.vanilla != "Blue Potion" for location in world.locations.values())
    (granny,) = gifts.check_steps(scan_gifts(romfs), definitions.load())[gifts.GRANNY_CHECK]
    assert granny.vanilla_item == "Item_Bottle_BluePotion"  # the native refill the census records
    transforms = step({name: location.vanilla for name, location in world.locations.items()})
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    out = transforms[granny.file](dicts.decompress(granny.file, (romfs / granny.file).read_bytes()))
    event = next(e for e in evfl.read(out).flowchart.events if e.name == granny.event)
    assert event.params[granny.param] == items.load().actor(gifts.GRANNY_POOL_ITEM)


@pytest.mark.dump
def test_dump_forty_token_reward_uses_native_bundle_and_preserves_threshold_and_collected_flag(romfs):
    from clawshot.generate import Settings, prepare
    from clawshot.generate.fill import shuffled_locations
    from clawshot.patch import items
    from clawshot.world import load_spec

    name = "Kak 40 Gold Skulltula Reward"
    path = "Event/EventFlow/GatheringTokenGold.bfevfl.zs"
    spec, settings, _ = gifts.seed_setup(romfs, load_spec(), Settings(shuffle=("Chest", gifts.SHUFFLE)))
    _, world = prepare(spec, settings)
    assert name in shuffled_locations(world, settings)
    assert world.locations[name].vanilla == "Bombchus (20)"
    actors = items.load()
    assert actors.actor(world.locations[name].vanilla) == "Item_BombchuBundle_Large"
    # Isolate this source; unrelated gifts have their own once-gate normalization.
    step = gifts.seed_step(
        [name],
        scan_gifts(romfs),
        definitions.load(),
        gifts.load(),
        actors,
        {name: world.locations[name].vanilla},
        {"GatheringTokenGold": path},
    )
    transforms = step({name: "Megaton Hammer"})
    assert GAME_DATA_LIST not in transforms
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    original = dicts.decompress(path, (romfs / path).read_bytes())
    before, after = evfl.read(original), evfl.read(transforms[path](original))
    native = next(event for event in before.flowchart.events if event.name == "Event200")
    changed = next(event for event in after.flowchart.events if event.name == "Event200")
    assert native.params["TakenRewardActor"] == "Item_BombchuBundle_Large"
    assert changed.params["TakenRewardActor"] == "Item_Hammer"
    changed.params["TakenRewardActor"] = native.params["TakenRewardActor"]
    assert before == after  # Includes all thresholds, completion writes, repeats and other rewards.
