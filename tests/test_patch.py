"""The item-to-actor table, the patch plan and the writer, on a synthetic world, census and romfs."""

import copy

import pytest

from clawshot.census.definitions import Definition
from clawshot.census.scan import CHEST, TREASURE_GAME_BOX, Location
from clawshot.formats import byml, rstb, zsdic
from clawshot.formats.byml import F32, U32, U64
from clawshot.generate import Seed, Settings
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import events as chest_events
from clawshot.patch import items as item_actors
from clawshot.patch.plan import PatchError, link, make_plan, remake_vanilla
from clawshot.patch.write import write
from clawshot.world import build_world

CHILD = "Banc/Village/Village_Child_Dynamic.bcett.byml.zs"
ADULT = "Banc/Village/Village_Adult_Dynamic.bcett.byml.zs"
TEMPLE = "Banc/Temple/Temple_Static.bcett.byml.zs"

SWORD_CHEST = 101  # holds the Sword, with a story override
RUPEE_CHEST = 102  # holds blue rupees, with an override that stays
TWIN_A, TWIN_B = 103, 104  # one check placed twice under two Hashes (as the GV Lens chest is)
MAP_CHEST = 201  # the dungeon's map
NUT_CHEST = 202  # the dungeon's nuts

TABLE = item_actors.loads(
    """
[items]
"Sword" = { actor = "Item_Sword", source = "test" }
"Rupees (5)" = { actor = "TBox_Rupee_Blue", source = "test" }
"Deku Nuts (5)" = { actor = "TBox_DekuNutBundle", source = "test" }
"Map (Temple)" = { actor = "Item_Dungeon_Map", source = "test" }
"Map (Other)" = { actor = "Item_Dungeon_Map", source = "test" }
"""
)

EVENTS = chest_events.loads(
    """
[event.Story_GetSword]
flow = "Story:GetSword"
patch = "remove"
does = "the chest event, then a sword cutscene"
story_state = "nothing to restore"

[event.House_NaviChatOff]
flow = "Small:Success_House"
patch = "keep"
does = "sets a flag, then the default event"
"""
)


def chest(vanilla: str, rule: str = "True") -> dict:
    return {"rule": rule, "type": "Chest", "vanilla": vanilla}


def world_spec() -> dict:
    """A village with three chests and a temple (a dungeon) with two. OoT Randomizer's vanilla items differ from
    the remake's in two chests (Recovery Heart, as N64 has, against the remake's nuts and rupees)."""
    return {
        "start": "Village",
        "goal": "Sword",
        "items": {
            "Sword": {},
            "Rupees (5)": {"class": "normal"},
            "Recovery Heart": {"class": "normal"},
            "Deku Nuts (5)": {"class": "normal"},
            "Map (Temple)": {"type": "Map", "class": "priority"},
            "Map (Other)": {"type": "Map", "class": "priority"},
        },
        "helpers": {},
        "settings": {},
        "regions": [
            {
                "name": "Village",
                "area": "Village",
                "locations": {
                    "Sword Chest": chest("Sword"),
                    "House Chest": chest("Recovery Heart"),
                    "Twin Chest": chest("Rupees (5)"),
                },
                "exits": {"Temple": "True"},
            },
            {
                "name": "Temple",
                "area": "Temple",
                "dungeon": "Temple",
                "locations": {"Temple Map Chest": chest("Map (Temple)"), "Temple Side Chest": chest("Recovery Heart")},
            },
        ],
    }


def census_location(
    actor_hash: int, area: str, files: tuple[str, ...], item: str, event: str | None = None, kind: str = CHEST
) -> Location:
    return Location(
        id=actor_hash,
        kind=kind,
        area=area,
        room=None,
        files=files,
        ages="both",
        position=(0.0, 0.0, 0.0),
        actor="Obj_TBox_A_01",
        vanilla_item=item,
        event=event,
        has_save_flag=True,
    )


CENSUS = [
    census_location(SWORD_CHEST, "Village", (ADULT, CHILD), "Item_Sword", "Story_GetSword"),
    census_location(RUPEE_CHEST, "Village", (ADULT, CHILD), "TBox_Rupee_Blue", "House_NaviChatOff"),
    census_location(TWIN_A, "Village", (CHILD,), "TBox_Rupee_Blue"),
    census_location(TWIN_B, "Village", (ADULT,), "TBox_Rupee_Blue"),
    census_location(MAP_CHEST, "Temple", (TEMPLE,), "Item_Dungeon_Map"),
    census_location(NUT_CHEST, "Temple", (TEMPLE,), "TBox_DekuNutBundle"),
    census_location(999, "Village", (CHILD,), "TBox_Rupee_Purple"),  # a remake-only chest no location names
]


def definition(location: Location, ootr: str) -> Definition:
    return Definition(
        location.id, location.kind, location.area, ootr or f"chest {location.id}", location.vanilla_item, ootr
    )


DEFINITIONS = [
    definition(loc, name)
    for loc, name in zip(
        CENSUS,
        ["Sword Chest", "House Chest", "Twin Chest", "Twin Chest", "Temple Map Chest", "Temple Side Chest", ""],
        strict=True,
    )
]


@pytest.fixture
def world():
    return build_world(world_spec())


@pytest.fixture
def links(world):
    return link(world, shuffled_locations(world, Settings()), DEFINITIONS, CENSUS)


def seed_with(world, placements: dict[str, str]) -> Seed:
    return Seed(world, 1, Settings(), placements, shuffled_locations(world, Settings()), [list(placements)])


# --------------------------------------------------------------------------------------------------------------
# The table


def test_actor_and_item_lookups(world):
    assert TABLE.actor("Deku Nuts (5)") == "TBox_DekuNutBundle"
    assert TABLE.item("TBox_Rupee_Blue", None, world.items) == "Rupees (5)"
    assert TABLE.item("Item_Dungeon_Map", "Temple", world.items) == "Map (Temple)"
    with pytest.raises(item_actors.ItemActorError, match="no logic item for the actor 'Item_Dungeon_Map' outside"):
        TABLE.item("Item_Dungeon_Map", None, world.items)
    with pytest.raises(item_actors.ItemActorError, match="no logic item for the actor 'Obj_Nope'"):
        TABLE.item("Obj_Nope", None, world.items)
    with pytest.raises(item_actors.ItemActorError, match="no actor for the item 'Recovery Heart'"):
        TABLE.actor("Recovery Heart")


def test_table_check(world):
    TABLE.check(world.items)
    shared = item_actors.loads('[items]\n"Sword" = { actor = "X" }\n"Rupees (5)" = { actor = "X" }\n')
    with pytest.raises(item_actors.ItemActorError, match="only one item per dungeon"):
        shared.check(world.items)
    with pytest.raises(item_actors.ItemActorError, match="does not know"):
        item_actors.loads('[items]\n"Nope" = { actor = "X" }\n').check(world.items)


def test_event_file_needs_story_state_exactly_with_remove():
    with pytest.raises(chest_events.ChestEventError, match="story_state is required"):
        chest_events.loads('[event.A]\npatch = "remove"\n')
    with pytest.raises(chest_events.ChestEventError, match="story_state is required"):
        chest_events.loads('[event.A]\npatch = "keep"\nstory_state = "x"\n')
    with pytest.raises(chest_events.ChestEventError, match="patch must be"):
        chest_events.loads('[event.A]\npatch = "drop"\n')


# --------------------------------------------------------------------------------------------------------------
# Links and the remake's pool


def test_remake_vanilla_is_what_the_chests_hold(world, links):
    assert [loc.id for loc in links.chests["Twin Chest"]] == [TWIN_A, TWIN_B]
    assert remake_vanilla(world, links, TABLE) == {
        "Sword Chest": "Sword",
        "House Chest": "Rupees (5)",  # N64: Recovery Heart
        "Twin Chest": "Rupees (5)",
        "Temple Map Chest": "Map (Temple)",  # the map of the chest's own dungeon
        "Temple Side Chest": "Deku Nuts (5)",  # N64: Recovery Heart
    }
    assert [d.id for d in links.vanilla_chests] == [999]


def test_copies_holding_different_actors_stop(world):
    census = [*CENSUS[:3], census_location(TWIN_B, "Village", (ADULT,), "TBox_Rupee_Red"), *CENSUS[4:]]
    links = link(world, shuffled_locations(world, Settings()), DEFINITIONS, census)
    with pytest.raises(PatchError, match="Twin Chest: its chests hold different actors"):
        remake_vanilla(world, links, TABLE)


@pytest.mark.parametrize(
    ("definitions", "census", "message"),
    [
        (DEFINITIONS[1:], CENSUS, "Sword Chest: no census definition"),
        (DEFINITIONS, CENSUS[1:], r"Sword Chest: the census of this dump has no chest \[101\]"),
        (
            [Definition(SWORD_CHEST, TREASURE_GAME_BOX, "Village", "x", "Item_Sword", "Sword Chest"), *DEFINITIONS[1:]],
            CENSUS,
            r"Sword Chest: links to 101 \(treasure_game_box\); seeds shuffle chests only",
        ),
    ],
)
def test_link_refusals(world, definitions, census, message):
    with pytest.raises(PatchError, match=message):
        link(world, shuffled_locations(world, Settings()), definitions, census)


# --------------------------------------------------------------------------------------------------------------
# The plan


def test_plan_changes_what_moved_and_removes_only_tied_overrides(world, links):
    plan = make_plan(
        seed_with(
            world,
            {
                "Sword Chest": "Rupees (5)",
                "House Chest": "Sword",
                "Twin Chest": "Deku Nuts (5)",
                "Temple Map Chest": "Map (Temple)",
                "Temple Side Chest": "Rupees (5)",
            },
        ),
        links,
        TABLE,
        EVENTS,
    )
    rows = [(c.location, c.id, c.files, c.old_actor, c.new_actor, c.event and c.event.name) for c in plan.changes]
    assert rows == [
        ("Sword Chest", SWORD_CHEST, (ADULT, CHILD), "Item_Sword", "TBox_Rupee_Blue", "Story_GetSword"),
        ("House Chest", RUPEE_CHEST, (ADULT, CHILD), "TBox_Rupee_Blue", "Item_Sword", None),  # override kept
        ("Twin Chest", TWIN_A, (CHILD,), "TBox_Rupee_Blue", "TBox_DekuNutBundle", None),
        ("Twin Chest", TWIN_B, (ADULT,), "TBox_Rupee_Blue", "TBox_DekuNutBundle", None),
        ("Temple Side Chest", NUT_CHEST, (TEMPLE,), "TBox_DekuNutBundle", "TBox_Rupee_Blue", None),
    ]
    assert plan.unchanged == [("Temple Map Chest", MAP_CHEST)]
    assert plan.files() == [TEMPLE, ADULT, CHILD]  # sorted romfs paths
    assert plan.as_dict()["changes"][0]["story_state"] == "nothing to restore"


def test_an_unchanged_chest_keeps_even_a_tied_override(world, links):
    vanilla = remake_vanilla(world, links, TABLE)
    plan = make_plan(seed_with(world, vanilla), links, TABLE, EVENTS)
    assert plan.changes == []
    assert plan.files() == []


def test_an_unclassified_override_stops_the_plan(world, links):
    events = {k: v for k, v in EVENTS.items() if k != "Story_GetSword"}
    seed = seed_with(
        world, {**remake_vanilla(world, links, TABLE), "Sword Chest": "Rupees (5)", "House Chest": "Sword"}
    )
    with pytest.raises(PatchError, match="GetEventName 'Story_GetSword', which chest_events.toml does not classify"):
        make_plan(seed, links, TABLE, events)


# --------------------------------------------------------------------------------------------------------------
# The writer


def actor(gyaml: str, actor_hash: int, dynamic: dict | None = None) -> dict:
    a = {"Gyaml": gyaml, "Hash": U64(actor_hash), "SRTHash": U32(actor_hash), "Translate": [F32(1.0)] * 3}
    if dynamic is not None:
        a["Dynamic"] = dynamic
    return a


def village_tree(path: str) -> dict:
    twin = TWIN_A if path == CHILD else TWIN_B
    return {
        "Actors": [
            actor("Obj_TBox_A_01", SWORD_CHEST, {"Drop__DropActor": "Item_Sword", "GetEventName": "Story_GetSword"}),
            actor(
                "Obj_TBox_A_01",
                RUPEE_CHEST,
                {"Drop__DropActor": "TBox_Rupee_Blue", "GetEventName": "House_NaviChatOff"},
            ),
            actor("Obj_TBox_A_01", twin, {"Drop__DropActor": "TBox_Rupee_Blue"}),
            actor("Obj_Signboard", 7),
        ],
        "FilePath": path,
    }


TEMPLE_TREE = {
    "Actors": [
        actor("Obj_TBox_A_01", MAP_CHEST, {"Drop__DropActor": "Item_Dungeon_Map"}),
        actor("Obj_TBox_A_01", NUT_CHEST, {"Drop__DropActor": "TBox_DekuNutBundle"}),
    ]
}


@pytest.fixture
def fake_romfs(tmp_path, zsdic_pack):
    root = tmp_path / "romfs"
    (root / "Pack").mkdir(parents=True)
    (root / zsdic.PACK_PATH).write_bytes(zsdic_pack)
    dicts = zsdic.Dictionaries.from_pack(zsdic_pack)
    for path, tree in ((CHILD, village_tree(CHILD)), (ADULT, village_tree(ADULT)), (TEMPLE, TEMPLE_TREE)):
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(dicts.compress(path, byml.write(tree)))
    write_size_table(root, dicts, {CHILD: ROOMY, ADULT: ROOMY, TEMPLE: ROOMY, "Other/File.bfevfl": 1234})
    return root


ROOMY = 1 << 20  # an entry every synthetic file fits


def write_size_table(root, dicts, entries: dict[str, int]) -> None:
    table = rstb.ResourceSizeTable()
    for path, size in entries.items():
        table.set(path, size)
    (root / rstb.TABLE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / rstb.TABLE_PATH).write_bytes(dicts.compress(rstb.TABLE_PATH, rstb.write(table)))


def swap_plan(world, links):
    seed = seed_with(world, {**remake_vanilla(world, links, TABLE), "Sword Chest": "Rupees (5)", "Twin Chest": "Sword"})
    return make_plan(seed, links, TABLE, EVENTS)


def test_writer_changes_only_what_the_plan_says(world, links, fake_romfs, tmp_path):
    before = {p: p.read_bytes() for p in fake_romfs.rglob("*") if p.is_file()}
    out = tmp_path / "out"
    written = write(swap_plan(world, links), fake_romfs, out)

    assert [f.path for f in written] == [ADULT, CHILD]  # the temple file holds no change
    assert sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()) == [
        f"romfs/{ADULT}",
        f"romfs/{CHILD}",
    ]
    dicts = zsdic.Dictionaries.from_romfs(fake_romfs)
    for path in (ADULT, CHILD):
        new = byml.read(dicts.decompress(path, (out / "romfs" / path).read_bytes()))
        expected = copy.deepcopy(village_tree(path))
        sword, _, twin, _ = expected["Actors"]
        sword["Dynamic"] = {"Drop__DropActor": "TBox_Rupee_Blue"}  # the story override is gone
        twin["Dynamic"]["Drop__DropActor"] = "Item_Sword"
        assert byml.difference(new, expected) is None
    assert {p: p.read_bytes() for p in fake_romfs.rglob("*") if p.is_file()} == before


def test_writer_refuses_a_file_that_is_not_what_the_census_saw(world, links, fake_romfs, tmp_path, zsdic_pack):
    tree = village_tree(ADULT)
    tree["Actors"][2]["Dynamic"]["Drop__DropActor"] = "TBox_Rupee_Red"
    dicts = zsdic.Dictionaries.from_pack(zsdic_pack)
    (fake_romfs / ADULT).write_bytes(dicts.compress(ADULT, byml.write(tree)))
    out = tmp_path / "out"
    with pytest.raises(
        PatchError, match="holding 'TBox_Rupee_Red'; the census said Obj_TBox_A_01 holding 'TBox_Rupee_Blue'"
    ):
        write(swap_plan(world, links), fake_romfs, out)
    assert not out.exists()  # nothing written, not even the files that were fine


def test_writer_raises_short_size_entries_and_writes_the_table(world, links, fake_romfs, tmp_path, zsdic_pack):
    dicts = zsdic.Dictionaries.from_pack(zsdic_pack)
    write_size_table(fake_romfs, dicts, {CHILD: 1, ADULT: ROOMY, TEMPLE: 2, "Other/File.bfevfl": 1234})
    out = tmp_path / "out"
    written = {f.path: f for f in write(swap_plan(world, links), fake_romfs, out)}

    child = written[CHILD]
    need = rstb.required_size(CHILD, child.new_size)
    assert (child.entry, child.new_entry) == (1, need)  # short: raised to what the file needs
    assert (written[ADULT].entry, written[ADULT].new_entry) == (ROOMY, ROOMY)  # never lowered
    assert rstb.TABLE_PATH in written
    table = rstb.read(dicts.decompress(rstb.TABLE_PATH, (out / "romfs" / rstb.TABLE_PATH).read_bytes()))
    assert [table.get(p) for p in (CHILD, ADULT, TEMPLE, "Other/File.bfevfl")] == [need, ROOMY, 2, 1234]


def test_writer_leaves_the_size_table_out_when_every_entry_fits(world, links, fake_romfs, tmp_path):
    written = write(swap_plan(world, links), fake_romfs, tmp_path / "out")
    assert rstb.TABLE_PATH not in [f.path for f in written]
    assert not (tmp_path / "out" / "romfs" / rstb.TABLE_PATH).exists()


def test_writer_needs_an_empty_folder_outside_the_romfs(world, links, fake_romfs, tmp_path):
    plan = swap_plan(world, links)
    with pytest.raises(PatchError, match="overlaps the romfs"):
        write(plan, fake_romfs, fake_romfs / "out")
    (tmp_path / "used").mkdir()
    (tmp_path / "used" / "spoiler.json").write_text("{}")
    with pytest.raises(PatchError, match="is not empty"):
        write(plan, fake_romfs, tmp_path / "used")


def test_writer_gives_the_same_bytes_twice(world, links, fake_romfs, tmp_path):
    plan = swap_plan(world, links)
    write(plan, fake_romfs, tmp_path / "a")
    write(plan, fake_romfs, tmp_path / "b")
    for path in plan.files():
        assert (tmp_path / "a" / "romfs" / path).read_bytes() == (tmp_path / "b" / "romfs" / path).read_bytes()


def test_extra_steps_compose_with_chests_and_each_other(world, links, fake_romfs, tmp_path):
    def mark(data):
        document = byml.load(data)
        document.root["Actors"][-1]["Dynamic"] = {"Seen": document.root["Actors"][0]["Dynamic"]["Drop__DropActor"]}
        return byml.dump(document)

    def finish(data):
        document = byml.load(data)
        document.root["Actors"][-1]["Dynamic"]["Seen"] += "!"
        return byml.dump(document)

    out = tmp_path / "composed"
    write(swap_plan(world, links), fake_romfs, out, extra_changes=({CHILD: mark}, {CHILD: finish}))
    dicts = zsdic.Dictionaries.from_romfs(fake_romfs)
    tree = byml.read(dicts.decompress(CHILD, (out / "romfs" / CHILD).read_bytes()))
    assert tree["Actors"][0]["Dynamic"]["Drop__DropActor"] == "TBox_Rupee_Blue"
    assert tree["Actors"][-1]["Dynamic"]["Seen"] == "TBox_Rupee_Blue!"


def test_extra_step_failure_writes_nothing(world, links, fake_romfs, tmp_path):
    def fail(data):
        raise PatchError("gift no longer matches its census")

    out = tmp_path / "failed"
    with pytest.raises(PatchError, match="gift no longer matches"):
        write(swap_plan(world, links), fake_romfs, out, extra_changes=({CHILD: fail},))
    assert not out.exists()


def test_owned_item_substitute_cannot_replace_a_shuffled_reward(world, links, fake_romfs, tmp_path):
    dicts = zsdic.Dictionaries.from_romfs(fake_romfs)
    tree = village_tree(CHILD)
    tree["Actors"][0]["Dynamic"].update(
        {"Drop__CheckActor": "Item_Bow", "Drop__DropActor_Substitute": "TBox_ArrowBundle_Medium"}
    )
    (fake_romfs / CHILD).write_bytes(dicts.compress(CHILD, byml.write(tree)))
    out = tmp_path / "substitute"
    write(swap_plan(world, links), fake_romfs, out)
    changed = byml.read(dicts.decompress(CHILD, (out / "romfs" / CHILD).read_bytes()))["Actors"][0]["Dynamic"]
    assert changed["Drop__DropActor"] == "TBox_Rupee_Blue"
    assert changed["Drop__DropActor_Substitute"] == "TBox_Rupee_Blue"
    assert changed["Drop__CheckActor"] == "Item_Bow"
