"""New Game ownership/pool invariants and native initialization (no extracted fixtures)."""

import struct
from collections import Counter

import pytest
from test_fast_start import flag, game_data_list, one_setting
from test_start_items import decode, synthetic_sequence

from clawshot import starting
from clawshot.formats import byml, evfl, zsdic
from clawshot.formats.byml import I32
from clawshot.generate import (
    Seed,
    Settings,
    _progressive_grants,
    from_placements,
    generate,
    prepare,
    return_guarantee_conflict,
)
from clawshot.generate.progressive import normalize_pool
from clawshot.generate.start import replace_pool
from clawshot.patch import gamedata, start_items
from clawshot.world import load_spec
from clawshot.world.search import Search


def test_settings_round_trip_and_unsupported_starts():
    settings = Settings(starting_items=["Slingshot", "Zeldas Lullaby"], starting_hearts=3, starting_full_wallet=True)
    assert Settings.from_string(settings.to_string()) == settings
    assert "starting_items" not in Settings().as_dict()
    for item in ("Gerudo Membership Card", "Weird Egg", "Lens of Truth", "Bottle", "Small Key (Fire Temple)"):
        with pytest.raises(ValueError, match="Unsupported starting items"):
            Settings(starting_items=[item])
    for hearts in (True, -1, 18):
        with pytest.raises(ValueError, match="starting_hearts"):
            Settings(starting_hearts=hearts)
    with pytest.raises(ValueError, match="starting_full_wallet"):
        Settings(starting_full_wallet=1)
    with pytest.raises(ValueError, match="requires Master Sword shuffle"):
        Settings(starting_items=["Master Sword"])


def test_initial_string_selector_keeps_typed_defaults_and_refuses_oversize():
    tree = game_data_list()
    tree["Data"]["String64"] = [flag("PlayerStatus.EquipOcarina", "")]
    tree["Data"]["Int"].append(flag("PlayerStatus.CurrentRupee", I32(0)))
    settings = Settings(starting_items=["Ocarina of Time", "Adult Wallet"], starting_full_wallet=True)
    changes = gamedata.plan_game_data(tree, start_items.initial_values(settings))
    gamedata.apply_game_data(tree, changes)
    assert tree["Data"]["String64"][0]["DefaultValue"] == "Item_Ocarina_Time"
    assert tree["Data"]["Int"][-1]["DefaultValue"] == 500
    assert type(tree["Data"]["Int"][-1]["DefaultValue"]) is I32
    with pytest.raises(gamedata.FastStartError, match="63 UTF-8 bytes"):
        gamedata.plan_game_data(
            game_data_with_string(), [one_setting('"PlayerStatus.EquipOcarina" = "' + "x" * 64 + '"')]
        )


def game_data_with_string():
    tree = game_data_list()
    tree["Data"]["String64"] = [flag("PlayerStatus.EquipOcarina", "")]
    return tree


@pytest.mark.parametrize("items", [(), ("Slingshot",), ("Kokiri Sword",)])
def test_starting_sword_keeps_the_bypassed_door_and_pause_map_state(items):
    saria_state = gamedata.load()["saria"].game_data
    tree = game_data_list()
    tree["Data"]["Bool"].extend(flag(name, False) for name in saria_state)
    tree["Data"]["Bool"].append(flag("HavePlayedEvent.Dm_MelodyGet_Zelda", False))
    patched = byml.read(
        gamedata.patch_initial_values(byml.write(tree), start_items.initial_values(Settings(starting_items=items)))
    )
    actual = {name: gamedata._find(patched, name)[1]["DefaultValue"] for name in saria_state}
    assert actual == (saria_state if "Kokiri Sword" in items else dict.fromkeys(saria_state, False))
    assert gamedata._find(patched, "HavePlayedEvent.Dm_MelodyGet_Zelda")[1]["DefaultValue"] is False


def test_post_setup_sequence_runs_original_before_ordered_native_grants():
    original = synthetic_sequence()
    pushes = (
        *start_items.START_PUSHES,
        ("Item_BulletBag_Small", 1),
        ("Item_Range_SlingShot", 1),
        ("Item_FairyBless_MP", 1),
    )
    patched = start_items._splice(original, pushes, after_setup=True)
    before, after = decode(original), decode(patched)
    assert after[: len(before)] == before
    root = struct.unpack_from("<I", patched, 0x88)[0]
    assert after[root]["children"] == [0, *range(root + 1, len(after))]
    assert after[root]["kind"] == 2
    assert [node["params"]["ActorName"] for node in after[root + 1 :]] == [
        f"Work/Actor/{actor}.engine__actor__ActorParam.gyml" for actor, _ in pushes
    ]
    assert patched[0x8C + root * 0x3C + 6] & 4
    assert not patched[0x8C + 6] & 4


@pytest.mark.dump
@pytest.mark.parametrize(
    ("chosen", "granted"),
    [
        ("Hookshot", ["Item_NutBag_Small", "Item_DekuNut", "Item_Hookshot"]),
        ("Longshot", ["Item_NutBag_Small", "Item_DekuNut", "Item_Hookshot", "Item_Longshot"]),
    ],
)
def test_native_starting_hook_tiers_use_ordered_pouch_grants_after_setup(romfs, chosen, granted):
    original = (romfs / start_items.PATH).read_bytes()
    patched = start_items.changes(Settings(starting_items=(chosen,)))[start_items.PATH](original)
    nodes = decode(patched)
    root = struct.unpack_from("<I", patched, 0x88)[0]
    assert nodes[root]["kind"] == 2
    assert nodes[root]["children"] == [0, *range(root + 1, len(nodes))]
    assert [node["name"] for node in nodes[root + 1 :]] == [start_items.PUSH] * len(granted)
    assert [(node["params"]["ActorName"], node["params"]["Num"]) for node in nodes[root + 1 :]] == [
        (f"Work/Actor/{actor}.engine__actor__ActorParam.gyml", 0 if actor == "Item_DekuNut" else 1) for actor in granted
    ]


def song_spec():
    return {
        "start": "Root",
        "goal": "Song_of_Time",
        "items": {
            "Zeldas Lullaby": {"type": "Song"},
            "Song of Time": {"type": "Song"},
            starting.JUNK: {"class": "normal"},
        },
        "regions": [
            {
                "name": "Root",
                "locations": {
                    "Impa": {"rule": "True", "type": "Song", "vanilla": "Zeldas Lullaby"},
                    "Tomb": {"rule": "Zeldas_Lullaby", "type": "Song", "vanilla": "Song of Time"},
                },
            }
        ],
    }


def test_starting_song_leaves_pool_and_its_vacated_song_slot_accepts_junk():
    settings = Settings(
        shuffle=("Song",),
        starting_items=("Zeldas Lullaby",),
        item_location_types={name: ("Song",) for name in ("Zeldas Lullaby", "Song of Time")},
        exclusive_location_types=("Song",),
    )
    seed = generate(song_spec(), 91, settings)
    assert Counter(seed.placements.values()) == Counter({"Song of Time": 1, starting.JUNK: 1})
    assert Search.child_only(seed.world).counts["Zeldas Lullaby"] == 1
    replay = from_placements(song_spec(), 91, settings, seed.placements)
    assert replay.placements == seed.placements
    assert Search.child_only(replay.world).counts["Zeldas Lullaby"] == 1


def test_upgrade_prefix_counts_once_and_replaces_only_pooled_copies():
    settings = Settings(starting_items=("Hookshot", "Longshot", "Golden Gauntlets", "Quiver (40)"), starting_hearts=3)
    effective, world = prepare(load_spec(), settings)
    search = Search.child_only(world)
    assert search.counts["Progressive Hookshot"] == 2
    assert search.counts["Progressive Strength Upgrade"] == 3
    assert search.counts["Bow"] == 2
    assert search.counts["Goron Bracelet"] == 1
    assert search.counts["Piece of Heart"] == 12
    vanilla = normalize_pool(world, effective)
    removed = replace_pool(world, effective, vanilla)
    before = Counter(
        vanilla.get(name, loc.vanilla)
        for name, loc in world.locations.items()
        if loc.type == "Chest" and not loc.keep_vanilla and not loc.n64_only
    )
    after = Counter(
        removed.get(name, vanilla.get(name, loc.vanilla))
        for name, loc in world.locations.items()
        if loc.type == "Chest" and not loc.keep_vanilla and not loc.n64_only
    )
    assert before["Progressive Hookshot"] - after["Progressive Hookshot"] == 2
    assert before["Progressive Strength"] - after["Progressive Strength"] == 3
    assert before["Progressive Quiver"] - after["Progressive Quiver"] == 2
    assert sum(before.values()) == sum(after.values())
    replay = Seed(world, 1, effective, {"Next": "Progressive Quiver"}, ["Next"], [["Next"]])
    assert _progressive_grants(replay)["Next"]["given_in_canonical_sphere_replay"] == "Quiver (50)"


def test_starting_spell_has_native_magic_floor_without_completing_its_source():
    _, world = prepare(load_spec(), Settings(starting_items=("Dins Fire",)))
    search = Search.child_only(world)
    assert search.counts["Dins Fire"] == 1
    assert search.counts["Magic Meter"] == 1
    assert not search.holds("Defeat King Dodongo")
    assert "Magic Meter (Single)" not in world.start_items


def test_starting_strength_does_not_assume_the_bypassed_darunia_song():
    # Native strength normally proves the child learned Saria before the closed Door.
    # Starting strength removes that history; fixed child Saria cannot rescue adult Link.
    spec = load_spec()
    settings, world = prepare(spec, Settings(starting_items=("Goron Bracelet",)))
    conflict = return_guarantee_conflict(world, settings)
    assert conflict is not None
    assert (
        "Starting with the Goron Bracelet needs Saria's Song as a starting item, "
        "song shuffle (the Gift option), or free time travel."
    ) in conflict
    for items in ((), ("Goron Bracelet", "Sarias Song")):
        settings, world = prepare(spec, Settings(starting_items=items))
        assert return_guarantee_conflict(world, settings) is None


@pytest.mark.dump
@pytest.mark.parametrize("sword", [False, True])
def test_native_initialization_has_bags_before_weapons_health_and_wallet(romfs, sword):
    settings = Settings(
        starting_items=(("Kokiri Sword",) if sword else ())
        + (
            "Slingshot",
            "Bow",
            "Magic Meter (Double)",
            "Giant Wallet",
            "Ocarina of Time",
            "Map (Deku Tree)",
            "Compass (Deku Tree)",
        ),
        starting_hearts=3,
        starting_full_wallet=True,
    )
    original = (romfs / start_items.PATH).read_bytes()
    patched = start_items.changes(settings)[start_items.PATH](original)
    nodes = decode(patched)
    root = struct.unpack_from("<I", patched, 0x88)[0]
    assert nodes[root]["children"][0] == 0
    assert nodes[4]["params"]["Value"] == nodes[5]["params"]["Value"] == 24
    assert nodes[7]["params"]["ActorName"].endswith("/Item_Wallet_Large.engine__actor__ActorParam.gyml")
    grants = [node["params"]["ActorName"].split("/")[-1].split(".")[0] for node in nodes[root + 1 :]]
    assert grants.index("Item_BulletBag_Small") < grants.index("Item_Range_SlingShot")
    assert grants.index("Item_Quiver_Small") < grants.index("Item_Range_Bow")
    assert {"Item_Wallet_Small", "Item_Wallet_Medium", "Item_Wallet_Large"} <= set(grants)
    assert nodes[root]["children"].index(0) < nodes[root]["children"].index(root + 1)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    native = dictionaries.decompress(gamedata.GAME_DATA_LIST, (romfs / gamedata.GAME_DATA_LIST).read_bytes())
    tree = byml.read(gamedata.patch_initial_values(native, start_items.initial_values(settings)))
    changes = {
        change.name: change.new
        for change in gamedata.plan_game_data(byml.read(native), start_items.initial_values(settings))
    }
    assert changes == {
        "DungeonInfo.InsideTheDekuTree.IsGetMap": True,
        "DungeonInfo.InsideTheDekuTree.IsGetCompass": True,
        "PlayerStatus.CurrentRupee": 1000,
        "PlayerStatus.EquipOcarina": "Item_Ocarina_Time",
        **(gamedata.load()["saria"].game_data if sword else {}),
    }
    assert gamedata._find(tree, "HavePlayedEvent.Dm_MelodyGet_Zelda")[1]["DefaultValue"] is False


@pytest.mark.dump
def test_native_prelearned_storms_keeps_first_lesson_and_native_continuations(romfs):
    path = "Event/EventFlow/Npc_Hylia_009_Adult.bfevfl.zs"
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    original = dictionaries.decompress(path, (romfs / path).read_bytes())
    document = evfl.read(original)
    changed = evfl.read(start_items.storms_lesson(original))
    by_name = {event.name: event for event in changed.flowchart.events}
    for name in ("Event9", "Event17", "Event31", "Event69"):
        event = by_name[name]
        assert event.params["GameDataName"] == "HavePlayedEvent.Dm_MelodyGet_Storm"
        assert dict(event.cases) == dict(next(node for node in document.flowchart.events if node.name == name).cases)
        event.params["GameDataName"] = "IsGet.Item_Melody_StormSong"
    assert changed == document
    # The transform composes after Gift's same source-history rewrite.
    assert start_items.storms_lesson(start_items.storms_lesson(original)) == start_items.storms_lesson(original)
