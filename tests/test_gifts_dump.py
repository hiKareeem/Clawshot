"""The gift patch on the player's dump: every changeable gift check, changed, gives a flow that round-trips and differs
from the game's only in the intended events, and a GameDataList that differs only in the added flags."""

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
    """Indices of the game's events a change may touch in ``flow``: the steps, the given reads, and whatever led
    to a skipped step."""
    index = {e.name: i for i, e in enumerate(fc.events)}
    out = set()
    for change in changes:
        out |= {index[s.event] for s in change.steps if s.flow == flow}
        out |= {
            index[r.split("/")[1]]
            for r in (*change.rule.given, *change.rule.writes, *change.rule.once)
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


@pytest.mark.dump
def test_dump_each_changed_flow_round_trips_and_differs_only_where_intended(romfs, context):
    dicts, files, changes = context
    transforms = gifts.file_changes(changes, files)
    table = rstb.read(dicts.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    flows = gifts.flows_changed(changes)
    assert len(flows) == len([p for p in transforms if p != GAME_DATA_LIST])
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
        expected_entries = before.entry_points.copy()
        granny = next((c for c in changes if c.check == gifts.GRANNY_CHECK), None)
        if granny and flow == granny.steps[0].flow:
            from copy import deepcopy

            expected_entries = deepcopy(expected_entries)
            root = next(e for e in expected_entries if e.name == "Buy_BluePotion")
            gate = after.events[after.entry_point(root.name).main_event]
            assert gate.cases == [(0, evfl.NONE), (1, root.main_event)]
            assert gate.params == {"GameDataName": granny.flag, "Index": -1}
            root.main_event = after.entry_point(root.name).main_event
        bottle = next((c for c in changes if c.check == gifts.MARKET_BOTTLE_CHECK), None)
        if bottle and flow == gifts.MARKET_BOTTLE_FLOW:
            from copy import deepcopy

            expected_entries = deepcopy(expected_entries)
            root = next(e for e in expected_entries if e.name == "Item_Bottle_TutorialEvent_Talk")
            gate = after.events[after.entry_point(root.name).main_event]
            assert gate.params == {"GameDataName": gifts.MARKET_BOTTLE_FLAG, "Index": -1}
            assert gate.cases == [(0, before.entry_point("Talk").main_event), (1, root.main_event)]
            root.main_event = after.entry_point(root.name).main_event
        assert expected_entries == after.entry_points[: len(before.entry_points)], flow
        specialized = [s for c in changes for s in c.steps if s.flow == flow and s.call == FROG_SONG_CALL]
        extra_entries = after.entry_points[len(before.entry_points) :]
        expected_extra = {next(e for e in after.events if e.name == s.event).entry_point for s in specialized}
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
            else:
                assert event.params[step.param] == NEW_ITEM, step.id
            if (change.new_flag or change.rule.once) and not change.rule.purchase:
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
    from clawshot.generate import Settings
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
            assert event.params[s.param] == actors.actor(seed.placements[name]), s.id
    rules = gifts.load()
    for name in seed.shuffled:
        if name in rules:
            assert rules[name].cls != gifts.MORE, name
    held = settings.item_location_types
    assert held, "no gift item is held"
    for name, item in seed.placements.items():
        if name in seed.shuffled and item in held:
            assert seed.world.locations[name].type in held[item], (name, item)
    print(f"moved gifts: {[(n, seed.placements[n]) for n in moved]}")


@pytest.mark.dump
def test_dump_gift_shuffle_moves_great_fairies_through_their_new_flags(romfs):
    from clawshot.generate import Settings, prepare
    from clawshot.world.load import load_spec

    spec, settings, step = gifts.seed_setup(romfs, load_spec(), Settings(shuffle=(gifts.SHUFFLE,)))
    fairies = {n: info for n, info in spec["locations"].items() if n.endswith("Great Fairy Reward")}
    moving = sorted(n for n, info in fairies.items() if not info.get("keep_vanilla"))
    # the two Magic Meter fairies stay: their pool item is a tier (MP or MP double), not one actor
    assert moving == [
        "Colossus Great Fairy Reward",
        "DMT Great Fairy Reward",
        "OGC Great Fairy Reward",
        "ZF Great Fairy Reward",
    ]
    _, world = prepare(spec, settings)
    placements = {name: loc.vanilla for name, loc in world.locations.items()}
    placements["DMT Great Fairy Reward"], placements["ZF Great Fairy Reward"] = "Farores Wind", "Dins Fire"
    transforms = step(placements)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    data = dicts.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes())
    before, after = byml.read(data), byml.read(transforms[GAME_DATA_LIST](data))
    added = [int(e["Hash"]) for e in after["Data"]["Bool"][len(before["Data"]["Bool"]) :]]
    # the Din flag's name is the one Kareem's save showed set (03-game-data.md section 19, in game)
    assert len(added) == 2 and murmur3_32(b"Clawshot.Gift.Dm_FairyFountain_Din.Event212") in added
    steps = gifts.check_steps(scan_gifts(romfs), definitions.load())
    for name, actor in (("DMT Great Fairy Reward", "Item_FaroreWind"), ("ZF Great Fairy Reward", "Item_DinFire")):
        for s in steps[name]:
            out = transforms[s.file](dicts.decompress(s.file, (romfs / s.file).read_bytes()))
            event = next(e for e in evfl.read(out).flowchart.events if e.name == s.event)
            assert event.params[s.param] == actor, s.id
