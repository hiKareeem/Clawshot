import copy

import pytest

from clawshot.census import definitions
from clawshot.census.definitions import Definition
from clawshot.census.gifts import Gift
from clawshot.formats import byml, evfl
from clawshot.formats.byml import I32, U32
from clawshot.formats.evfl import (
    ActionEvent,
    Actor,
    EntryPoint,
    EventFlowFile,
    Flowchart,
    SubFlowEvent,
    SwitchEvent,
)
from clawshot.patch import gifts
from clawshot.patch import items as item_actors
from clawshot.patch.gifts import GiftChange, GiftPatchError, Rule
from clawshot.save import murmur3_32

FLOW = "Npc_Test"


def flowchart() -> Flowchart:
    """A made-up NPC flow: a query on IsGet.Item_Old picks a tier step or another, both handing over Item_Old; a
    melody switch leads to a direct add that the song rules skip."""
    game_data = Actor("GameDataActor", actions=["EventTriggerSetGameDataBool"], queries=["EventQueryIsGameDataBool"])
    pouch = Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"], queries=["Melody"])
    events = [
        SwitchEvent("Event0", 0, 0, [(0, 4), (1, 1)], {"GameDataName": "IsGet.Item_Old", "Index": -1}),
        SubFlowEvent("Event1", "Wrap", "Give", next=2, params={"ActorName": "Item_Old"}),
        ActionEvent("Event2", 0, 0, params={"GameDataName": "Npc_Test_Done", "Index": -1, "Value": True}),
        SwitchEvent("Event3", 1, 0, [(0, 5), (1, 6)]),
        SubFlowEvent("Event4", "Wrap", "Give", next=2, params={"ActorName": "Item_Old_Large"}),
        ActionEvent("Event5", 1, 0, next=7, params={"Actor": "Item_Song", "Num": 1}),
        ActionEvent("Event6", 1, 0, next=7, params={"Actor": "Item_Other", "Num": 1}),
        ActionEvent("Event7", 0, 0, params={"GameDataName": "Sung", "Index": -1, "Value": True}),
    ]
    entries = [EntryPoint("Talk", 0), EntryPoint("Sing", 3), EntryPoint("Direct", 5)]
    return Flowchart(FLOW, [game_data, pouch], events, entries)


def gift(event: str, item: str) -> Gift:
    return Gift(f"{FLOW}/{event}", "npc_gift", FLOW, "f", ("Talk",), event, "Wrap:Give", "ActorName", item, "")


STEPS = (gift("Event1", "Item_Old"), gift("Event4", "Item_Old_Large"))


def change(item: str = "Item_New", **rule) -> GiftChange:
    return GiftChange(Rule("Test Check", rule.pop("cls", "swap"), **rule), STEPS, item)


def patched(*changes: GiftChange) -> Flowchart:
    fc = flowchart()
    gifts.patch_flowchart(fc, FLOW, changes)
    return fc


def test_swap_sets_every_step_and_nothing_else():
    fc = patched(change())
    before = flowchart()
    assert [e.params["ActorName"] for e in (fc.events[1], fc.events[4])] == ["Item_New", "Item_New"]
    fc.events[1].params["ActorName"], fc.events[4].params["ActorName"] = "Item_Old", "Item_Old_Large"
    assert fc == before


def test_new_flag_is_set_after_each_step_and_replaces_the_given_read():
    c = change(cls="rewrite", given=(f"{FLOW}/Event0",))
    assert c.flag == c.new_flag == "Clawshot.Gift.Npc_Test.Event1"
    fc = patched(c)
    assert len(fc.events) == 10
    for step in (1, 4):
        added = fc.events[fc.events[step].next]
        assert added.name.startswith("ClawshotGift")
        assert (added.actor, added.action, added.next) == (0, 0, 2)
        assert added.params == {"GameDataName": c.flag, "Index": -1, "Value": True}
    assert fc.events[0].params == {"GameDataName": c.flag, "Index": -1}
    assert len({e.name for e in fc.events}) == 10
    # what the file holds reads back the same
    file = EventFlowFile(FLOW, flowchart=fc)
    assert evfl.read(evfl.write(file)) == file


def test_an_existing_flag_is_read_and_nothing_is_set():
    c = change(cls="rewrite", given=(f"{FLOW}/Event0",), flag="HavePlayedEvent.Dm_Test")
    assert (c.flag, c.new_flag) == ("HavePlayedEvent.Dm_Test", None)
    fc = patched(c)
    assert len(fc.events) == 8
    assert fc.events[0].params["GameDataName"] == "HavePlayedEvent.Dm_Test"
    assert fc.events[1].next == 2


def test_skip_points_cases_next_and_entry_points_past_the_step():
    fc = patched(change(cls="rewrite", skip=(f"{FLOW}/Event5",)))
    assert fc.events[3].cases == [(0, 7), (1, 6)]
    assert fc.entry_points[2].main_event == 7
    assert fc.events[6].next == 7


def test_refusals():
    with pytest.raises(GiftPatchError, match="the census said"):
        patched(change(), change())  # the second change finds the item already changed
    with pytest.raises(GiftPatchError, match="not a read of IsGet"):
        patched(change(cls="rewrite", given=(f"{FLOW}/Event3",)))
    with pytest.raises(GiftPatchError, match="not a query"):
        patched(change(cls="rewrite", given=(f"{FLOW}/Event1",)))
    with pytest.raises(GiftPatchError, match="only a step with a next event"):
        patched(change(cls="rewrite", skip=(f"{FLOW}/Event2",)))
    skip_only = GiftChange(Rule("Song", "rewrite", skip=(f"{FLOW}/Event5",)), (), "Item_New")
    with pytest.raises(GiftPatchError, match="nothing leads to it"):
        patched(skip_only, skip_only)
    with pytest.raises(GiftPatchError, match="no event"):
        patched(change(cls="rewrite", skip=(f"{FLOW}/Event99",)))


def test_flow_transform_round_trips_bytes():
    data = evfl.write(EventFlowFile(FLOW, flowchart=flowchart()))
    out = gifts.flow_transform(FLOW, [change(cls="rewrite", given=(f"{FLOW}/Event0",))])(data)
    assert evfl.read(out).flowchart == patched(change(cls="rewrite", given=(f"{FLOW}/Event0",)))
    with pytest.raises(GiftPatchError, match="no flowchart of that name"):
        gifts.flow_transform("Other", [change()])(data)


RULES = """
[check."A"]
class = "swap"
gate = "a flag"

[check."B"]
class = "rewrite"
given = ["Flow/Event1"]
flag = "HavePlayedEvent.Dm_B"
skip = ["Other/Event2"]

[check."C"]
class = "more"
reason = "needs more"
"""


def test_rules_load_and_refuse_bad_entries():
    rules = gifts.loads(RULES)
    assert rules["B"] == Rule("B", "rewrite", "", ("Flow/Event1",), "HavePlayedEvent.Dm_B", ("Other/Event2",))
    bad = {
        'class = "maybe"': "class",
        'class = "swap"\ngiven = ["F/E"]': "belong to class",
        'class = "rewrite"': "nothing to rewrite",
        'class = "rewrite"\nskip = ["F/E"]\nflag = "X"': "a flag without reads",
        'class = "more"': "needs a reason",
        'class = "rewrite"\nskip = ["FE"]': "is not",
        'class = "swap"\ncolour = 1': "unknown fields",
    }
    for body, message in bad.items():
        with pytest.raises(GiftPatchError, match=message):
            gifts.loads(f'[check."X"]\n{body}\n')


def test_plan_groups_steps_by_check_and_refuses():
    defs = [
        Definition(f"{FLOW}/Event1", "npc_gift", "", "a", "Item_Old", "Test Check"),
        Definition(f"{FLOW}/Event4", "npc_gift", "", "b", "Item_Old_Large", "Test Check"),
        Definition(f"{FLOW}/Event9", "npc_gift", "", "c", "Obj_Rupee_Red", ""),
    ]
    rules = {"Test Check": Rule("Test Check", "swap"), "More": Rule("More", "more", reason="r")}
    [c] = gifts.plan({"Test Check": "Item_New"}, STEPS, defs, rules)
    assert (c.check, c.steps, c.item) == ("Test Check", STEPS, "Item_New")
    with pytest.raises(GiftPatchError, match="no census gift step"):
        gifts.plan({"Nobody": "Item_New"}, STEPS, defs, rules)
    with pytest.raises(GiftPatchError, match="no rule"):
        gifts.plan({"Test Check": "Item_New"}, STEPS, defs, {})
    defs.append(Definition(f"{FLOW}/Event5", "npc_gift", "", "d", "Item_Song", "More"))
    with pytest.raises(GiftPatchError, match="cannot be changed yet"):
        gifts.plan({"More": "Item_New"}, [*STEPS, gift("Event5", "Item_Song")], defs, rules)


def test_file_changes_cover_every_flow_the_rules_touch():
    c = change(cls="rewrite", given=("Reader/Event0",), skip=("Song/Event5",))
    out = gifts.file_changes([c], {FLOW: "a", "Reader": "b", "Song": "c"})
    assert sorted(out) == ["GameData/GameDataList.Product.110.byml.zs", "a", "b", "c"]
    with pytest.raises(GiftPatchError, match="no flow file"):
        gifts.file_changes([c], {FLOW: "a"})


def game_data_list() -> dict:
    """A small GameDataList whose MetaData agrees with its entries as the game's does."""

    def entry(name: str, sfi: int) -> dict:
        return {
            "DefaultValue": False,
            "Hash": U32(murmur3_32(name.encode())),
            "ResetTypeValue": I32(8),
            "SaveFileIndex": I32(sfi),
        }

    data = {
        "Bool": [entry("A", 0), entry("B", 0), entry("C", -1), entry("D", 1)],
        "Int": [entry("E", 0) | {"DefaultValue": I32(0)}],
        "Bool64bitKey": [{"Hash": byml.U64(5), "ResetTypeValue": I32(24), "SaveFileIndex": I32(0)}],
        "BoolExp": [{"Hash": U32(9), "ResetTypeValue": I32(0), "SaveFileIndex": I32(-1), "Values": []}],
    }
    file0 = 0x20 + 8 * (3 + 1 + 33)  # A, B, E; the Bool64bitKey pair; the section headers
    every = 0x20 + 8 * (5 + 1 + 33)  # all but Bool64bitKey and BoolExp
    meta = {
        "AllDataSaveOffset": I32(every),
        "AllDataSaveSize": I32(every + 100),
        "SaveDataOffsetPos": [I32(file0), I32(40)],
        "SaveDataSize": [I32(file0 + 64), I32(80)],
    }
    return {"Data": data, "MetaData": meta}


def test_add_flags_appends_saved_bools_and_grows_the_save_layout():
    tree = game_data_list()
    before = copy.deepcopy(tree)
    gifts.add_flags(tree, ["Clawshot.Gift.X.Event1", "Clawshot.Gift.Y.Event2"])
    assert tree["Data"]["Bool"][:4] == before["Data"]["Bool"]
    assert tree["Data"]["Bool"][4:] == [
        {"DefaultValue": False, "Hash": murmur3_32(n.encode()), "ResetTypeValue": 8, "SaveFileIndex": 0}
        for n in ("Clawshot.Gift.X.Event1", "Clawshot.Gift.Y.Event2")
    ]
    meta, old = tree["MetaData"], before["MetaData"]
    assert meta["SaveDataOffsetPos"] == [old["SaveDataOffsetPos"][0] + 16, 40]
    assert meta["SaveDataSize"] == [old["SaveDataSize"][0] + 16, 80]
    assert (meta["AllDataSaveOffset"], meta["AllDataSaveSize"]) == (
        old["AllDataSaveOffset"] + 16,
        old["AllDataSaveSize"] + 16,
    )
    assert all(type(v) is I32 for v in (*meta["SaveDataOffsetPos"], *meta["SaveDataSize"]))
    # the formula holds again, so a second step could add more
    gifts.add_flags(tree, ["Clawshot.Gift.Z.Event3"])


def test_add_flags_refuses_a_taken_hash_and_a_layout_it_cannot_explain():
    with pytest.raises(GiftPatchError, match="already has an entry"):
        gifts.add_flags(game_data_list(), ["A"])
    with pytest.raises(GiftPatchError, match="already has an entry"):
        gifts.add_flags(game_data_list(), ["N", "N"])
    tree = game_data_list()
    tree["MetaData"]["AllDataSaveOffset"] = I32(0)
    with pytest.raises(GiftPatchError, match="MetaData table ends"):
        gifts.add_flags(tree, ["N"])


def test_game_data_transform_keeps_the_byte_order():
    data = byml.write(game_data_list(), "big")
    out = gifts.game_data_transform(["N"])(data)
    assert byml.byte_order(out) == "big"
    assert len(byml.read(out)["Data"]["Bool"]) == 5


def test_every_linked_gift_check_has_a_rule():
    linked = {d.oot_randomizer_name for d in definitions.load() if isinstance(d.id, str) and d.oot_randomizer_name}
    rules = gifts.load()
    assert set(rules) == linked | {gifts.SHOPKEEPER_CHECK}
    for rule in rules.values():
        for ref in (*rule.given, *rule.skip):
            assert ref.split("/")[1].startswith("Event"), ref


class _Loc:
    def __init__(self, type, vanilla, n64_only=None, keep_vanilla=None):
        self.type, self.vanilla, self.n64_only, self.keep_vanilla = type, vanilla, n64_only, keep_vanilla


class _World:
    def __init__(self, locations, settings=None):
        self.locations = locations
        self.settings = settings or {}


def test_seed_checks_take_changeable_gifts_whose_pool_item_is_what_they_give():
    def step(flow: str, item: str) -> Gift:
        return Gift(f"{flow}/Event1", "npc_gift", flow, "f", (), "Event1", "W:G", "ActorName", item, "")

    gs = [step("A", "Item_A"), step("B", "Item_B"), step("C", "Item_C"), step("D", "Item_D"), step("E", "Item_E")]
    defs = [Definition(g.id, "npc_gift", "", g.flow, g.vanilla_item, f"Check {g.flow}") for g in gs]
    rules = {
        "Check A": Rule("Check A", "swap"),
        "Check B": Rule("Check B", "more", reason="r"),
        "Check C": Rule("Check C", "rewrite", given=("C/Event0",)),  # needs a new flag
        "Check D": Rule("Check D", "swap"),
        "Check E": Rule("Check E", "rewrite", given=("E/Event0",), flag="HavePlayedEvent.E"),
    }
    actors = item_actors.loads(
        '[items]\nA = { actor = "Item_A" }\nB = { actor = "Item_B" }\nC = { actor = "Item_C" }\n'
        'D = { actor = "Item_Other" }\nE = { actor = "Item_E" }\n'
    )
    world = _World(
        {
            "Check A": _Loc("NPC", "A"),
            "Check B": _Loc("Boss", "B"),
            "Check C": _Loc("NPC", "C"),
            "Check D": _Loc("NPC", "D"),  # its pool item's actor is not what it gives
            "Check E": _Loc("Song", "E"),
            "Chest X": _Loc("Chest", "A"),
        }
    )
    # Check C has no existing given flag: it moves with a new GameDataList flag, as the Great Fairies do
    assert gifts.seed_checks(world, gs, defs, rules, actors) == ["Check A", "Check C", "Check E"]
    world.locations["Check A"].keep_vanilla = "D17"
    assert gifts.seed_checks(world, gs, defs, rules, actors) == ["Check C", "Check E"]


def test_restrict_spec_holds_the_other_gift_locations_vanilla():
    spec = {
        "start": "Root",
        "locations": {
            "Moves": {"type": "NPC", "vanilla": "A"},
            "Stays": {"type": "Song", "vanilla": "B"},
            "Kept": {"type": "Boss", "vanilla": "C", "keep_vanilla": "own reason"},
            "Chest": {"type": "Chest", "vanilla": "D"},
        },
    }
    out = gifts.restrict_spec(spec, ["Moves"])
    assert "keep_vanilla" not in out["locations"]["Moves"]
    assert out["locations"]["Stays"]["keep_vanilla"].startswith("gift shuffle")
    assert out["locations"]["Kept"]["keep_vanilla"] == "own reason"
    assert out["locations"]["Chest"] == spec["locations"]["Chest"]
    assert "keep_vanilla" not in spec["locations"]["Stays"]  # the spec given is not changed


def test_seed_step_changes_only_moved_gifts():
    defs = [Definition(s.id, "npc_gift", "", "n", s.vanilla_item, "Test Check") for s in STEPS]
    actors = item_actors.loads('[items]\nOld = { actor = "Item_Old" }\nNew = { actor = "Item_New" }\n')
    rules = {"Test Check": Rule("Test Check", "swap")}
    step = gifts.seed_step(["Test Check"], STEPS, defs, rules, actors, {"Test Check": "Old"}, {FLOW: "flow.bfevfl"})
    assert step({"Test Check": "Old"}) == {}
    out = step({"Test Check": "New"})
    data = evfl.write(EventFlowFile(FLOW, flowchart=flowchart()))
    fc = evfl.read(out["flow.bfevfl"](data)).flowchart
    assert fc.events[1].params["ActorName"] == fc.events[4].params["ActorName"] == "Item_New"


class _Item:
    def __init__(self, type="Item"):
        self.type = type


def test_held_items_keep_songs_to_songs_and_chestless_actors_to_gifts():
    world = _World({})
    world.items = {"Lullaby": _Item("Song"), "Letter": _Item(), "Heart": _Item()}
    actors = item_actors.loads(
        '[items]\nLullaby = { actor = "Item_Melody_Z" }\nLetter = { actor = "Item_Letter" }\n'
        'Heart = { actor = "Obj_Heart_Piece" }\n'
    )
    held = gifts.held_items(world, ["Letter", "Lullaby", "Heart", "Letter"], actors, {"Obj_Heart_Piece"})
    assert held == {"Letter": ("NPC", "Cutscene", "Boss"), "Lullaby": ("Song",)}


def test_anchors_stay_vanilla_unless_time_travel_is_free():
    s = Gift("Dm_Goron/Event1", "event_gift", "Dm_Goron", "f", (), "Event1", "W:G", "ActorName", "Item_Bracelet", "")
    defs = [Definition(s.id, "event_gift", "", "n", s.vanilla_item, "GC Darunias Joy")]
    rules = {"GC Darunias Joy": Rule("GC Darunias Joy", "swap")}
    actors = item_actors.loads('[items]\nBracelet = { actor = "Item_Bracelet" }\n')
    locations = {"GC Darunias Joy": _Loc("Cutscene", "Bracelet")}
    assert gifts.seed_checks(_World(locations), [s], defs, rules, actors) == []
    free = _World(locations, {"free_time_travel": True})
    assert gifts.seed_checks(free, [s], defs, rules, actors) == ["GC Darunias Joy"]
