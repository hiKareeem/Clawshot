import pytest

from clawshot.census import definitions, ootr
from clawshot.census.scan import CensusError, Location, scan, scan_trees
from clawshot.formats import byml, zsdic
from clawshot.formats.byml import F32, I32, U64

CHILD = "Banc/Field/Field_Child_Dynamic.bcett.byml.zs"
ADULT = "Banc/Field/Field_Adult_Dynamic.bcett.byml.zs"
ADULT_ALT = "Banc/Field/Field_Adult_Alternative_Static.bcett.byml.zs"
DUNGEON = "Banc/Cave/Cave_Static.bcett.byml.zs"
DREAM = "Banc/DreamWorld/GohmaStage_Static.bcett.byml.zs"
BIG = 2**64 - 5  # above TOML's signed 64-bit range


def actor(gyaml, actor_hash, dynamic=None, pos=(1.0, 2.0, 3.0)):
    a = {"Gyaml": gyaml, "Hash": U64(actor_hash), "Translate": [F32(x) for x in pos]}
    if dynamic is not None:
        a["Dynamic"] = dynamic
    return a


def by_id(locations):
    return {loc.id: loc for loc in locations}


def test_one_location_per_hash_across_age_files():
    chest = actor("Obj_TBox_A_01", BIG, {"Drop__DropActor": "TBox_Rupee_Red", "GetEventName": "Ev"})
    banc = {CHILD: {"Actors": [chest]}, ADULT: {"Actors": [chest]}}
    [loc] = scan_trees(banc, flags=[BIG])
    assert loc == Location(
        id=BIG,
        kind="chest",
        area="Field",
        room=None,
        files=(ADULT, CHILD),
        ages="both",
        position=(1.0, 2.0, 3.0),
        actor="Obj_TBox_A_01",
        vanilla_item="TBox_Rupee_Red",
        event="Ev",
        has_save_flag=True,
    )


def test_kinds_items_and_exclusions():
    banc = {
        ADULT: {
            "Actors": [
                actor("Obj_TBox_A_02", 1),  # no drop: the chest default
                actor("Obj_TBox_A_04", 2),  # trap chest
                actor("Obj_TBoxPedestal_A_01", 3),
                actor("Enemy_Skulltula_Gold", 4),
                actor("Obj_Dungeon_SmallKey_GerudoFortress_02", 5),
                actor("Enemy_Scrub_Business", 6, {"ScrubBusiness_ShopItemActorName0": "Item_NutBag_Medium"}),
                actor("Enemy_Scrub_Business", 7, {"TalkEventName": "Enemy_Scrub_Business_Item"}),
                actor("Shop_Heart", 8),
                actor("Shop_Bottle_Bug", 9, {"ShopItemIndex": I32(6)}),
                actor("Shop_Board_SoldOut", 10),
                actor("Obj_HrlCity_Shop_TBox_A_01", 11, {"Drop__DropActor": "Obj_MiniGame_SmallKey"}),
                actor("Obj_HrlCity_Shop_TBox_A_02", 15, {"Drop__DropActor": "Obj_Heart_Piece"}),
                actor("Animal_Cow", 12),
            ]
        },
        DUNGEON: {"Actors": [actor("Obj_Heart_Container", 13, {"DefaultDungeonRoomIndex": I32(22)})]},
        DREAM: {"Actors": [actor("Obj_TBox_A_01", 14, {"Drop__DropActor": "TBox_Rupee_Gold"})]},
    }
    locs = by_id(scan_trees(banc, flags=[]))
    assert {i: (loc.kind, loc.vanilla_item) for i, loc in locs.items()} == {
        1: ("chest", "Obj_Rupee_Green"),
        4: ("gold_skulltula", "Obj_Token_Gold"),
        5: ("freestanding", "Obj_Dungeon_SmallKey_GerudoFortress_02"),
        6: ("scrub", "Item_NutBag_Medium"),
        7: ("scrub", ""),
        8: ("shop_slot", "Shop_Heart"),
        9: ("shop_slot", "Shop_Bottle_Bug"),
        11: ("treasure_game_box", "Obj_MiniGame_SmallKey"),
        15: ("treasure_game_reward", "Obj_Heart_Piece"),
        13: ("heart_container", "Obj_Heart_Container"),
    }
    assert (locs[8].shop_slot, locs[9].shop_slot, locs[1].shop_slot) == (0, 6, None)
    assert (locs[13].room, locs[13].ages, locs[1].ages) == (22, "both", "adult")


def test_ages_of_alternative_file_and_merge():
    gs = actor("Enemy_Skulltula_Gold", 1)
    [loc] = scan_trees({ADULT: {"Actors": [gs]}, ADULT_ALT: {"Actors": [gs]}}, flags=[])
    assert loc.ages == "adult"


@pytest.mark.parametrize(
    "other",
    [
        actor("Obj_TBox_A_01", 1, {"Drop__DropActor": "TBox_Rupee_Blue"}),
        actor("Obj_TBox_A_02", 1, {"Drop__DropActor": "TBox_Rupee_Red"}),
        actor("Obj_TBox_A_01", 1, {"Drop__DropActor": "TBox_Rupee_Red"}, pos=(1.0, 2.5, 3.0)),
    ],
)
def test_a_hash_that_differs_between_files_is_an_error(other):
    chest = actor("Obj_TBox_A_01", 1, {"Drop__DropActor": "TBox_Rupee_Red"})
    with pytest.raises(CensusError, match="Hash 1"):
        scan_trees({CHILD: {"Actors": [chest]}, ADULT: {"Actors": [other]}}, flags=[])


def test_float_noise_between_copies_is_tolerated():
    a = actor("Enemy_Skulltula_Gold", 1, pos=(1.0, 2.0, 3.0))
    b = actor("Enemy_Skulltula_Gold", 1, pos=(1.002, 2.0, 3.0))
    [loc] = scan_trees({CHILD: {"Actors": [a]}, ADULT: {"Actors": [b]}}, flags=[])
    assert loc.files[0] == ADULT and loc.position == tuple(float(x) for x in b["Translate"])


def test_scan_reads_a_romfs(tmp_path, zsdic_pack):
    root = tmp_path / "romfs"
    (root / "Pack").mkdir(parents=True)
    (root / zsdic.PACK_PATH).write_bytes(zsdic_pack)
    dicts = zsdic.Dictionaries.from_pack(zsdic_pack)
    files = {
        CHILD: {"Actors": [actor("Obj_Heart_Piece", BIG)]},
        DUNGEON: {"Actors": [actor("Obj_TBox_A_01", 7, {"Drop__DropActor": "Item_Dungeon_Map"})]},
    }
    for path, tree in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(dicts.compress(path, byml.write(tree)))
    gdl = "GameData/GameDataList.Product.110.byml.zs"
    (root / gdl).parent.mkdir(parents=True)
    tree = {"Data": {"Bool64bitKey": [{"Hash": U64(BIG), "ResetTypeValue": I32(24)}]}}
    (root / gdl).write_bytes(dicts.compress(gdl, byml.write(tree, "big")))

    locs = by_id(scan(root))
    assert set(locs) == {BIG, 7}
    assert (locs[BIG].kind, locs[BIG].has_save_flag, locs[7].has_save_flag) == ("freestanding", True, False)


# --------------------------------------------------------------------------------------------------------------
# OoT Randomizer names

LOCATION_LIST = """
def shop_address(shop_id, shelf_id):
    return 0
location_table: dict = OrderedDict([
    ("KF Kokiri Sword Chest", ("Chest", 0x55, 0x00, None, 'Kokiri Sword', ("Kokiri Forest",))),
    ("KF Midos Top Left Chest", ("Chest", 0x28, 0x00, None, 'Rupees (5)', ("Kokiri Forest",))),
    ("KF Midos Top Right Chest", ("Chest", 0x28, 0x01, None, 'Rupees (5)', ("Kokiri Forest",))),
    ("KF Storms Grotto Chest", ("Chest", 0x3E, 0x0C, None, 'Rupees (20)', ("Kokiri Forest",))),
    ("KF GS Know It All House", ("GS Token", 0x0C, 0x02, None, 'Gold Skulltula Token', ("Kokiri Forest",))),
    ("KF Shop Item 1", ("Shop", 0x2D, 0x30, (shop_address(0, 0), None), 'Buy Deku Shield', ("Kokiri Forest",))),
    ("KF Shop Item 2", ("Shop", 0x2D, 0x31, (shop_address(0, 1), None), 'Buy Deku Nut (5)', ("Kokiri Forest",))),
    ("Deku Tree Map Chest", ("Chest", 0x00, 0x03, None, 'Map (Deku Tree)', ("Deku Tree", "Vanilla Dungeons"))),
    ("Deku Tree Basement Chest", ("Chest", 0x00, 0x04, None, 'Recovery Heart', ("Deku Tree", "Vanilla Dungeons"))),
    ("Deku Tree MQ Map Chest", ("Chest", 0x00, 0x03, None, 'Map (Deku Tree)', ("Deku Tree MQ", "Master Quest"))),
])
"""


@pytest.fixture
def location_list(tmp_path):
    path = tmp_path / "LocationList.py"
    path.write_text(LOCATION_LIST, encoding="utf-8")
    return ootr.read_location_list(path)


def test_location_list_is_read_without_master_quest(location_list):
    names = [o.name for o in location_list]
    assert "Deku Tree MQ Map Chest" not in names
    sword = location_list[0]
    assert (sword.area, sword.kind, sword.vanilla_item) == ("KokiriForest", "chest", "Kokiri Sword")
    assert location_list[5].area == "KokiriForest" and location_list[5].kind == "shop_slot"


@pytest.mark.parametrize(
    ("item", "family"),
    [
        ("Small Key (Forest Temple)", "Small Key"),
        ("Buy Bombs (5) for 35 Rupees", "Bombs"),
        ("Buy Deku Nut (10)", "Deku Nuts"),
        ("Rupee (Treasure Chest Game) (1)", "Rupee (1)"),
        ("Piece of Heart (Out of Logic)", "Piece of Heart"),
        ("Rupees (20)", "Rupees (20)"),
        ("Buy Heart", "Recovery Heart"),
    ],
)
def test_ootr_family(item, family):
    assert ootr.ootr_family(item) == family


def loc(actor_hash, kind, area, item, actor=None, pos=(0.0, 0.0, 0.0), files=None, room=None, slot=None):
    return Location(
        id=actor_hash,
        kind=kind,
        area=area,
        room=room,
        files=files or (f"Banc/{area}/{area}_Child_Static.bcett.byml.zs",),
        ages="child",
        position=pos,
        actor=actor or ("Obj_TBox_A_01" if kind == "chest" else item),
        vanilla_item=item,
        event=None,
        has_save_flag=True,
        shop_slot=slot,
    )


ADULT_KF = ("Banc/KokiriForest/KokiriForest_Adult_Static.bcett.byml.zs",)


def test_match_by_unique_item_residual_copies_and_shop_slots(location_list):
    locations = [
        loc(1, "chest", "KokiriForest", "Item_Sword_Kokiri", actor="Obj_TBox_A_02"),
        loc(2, "chest", "KokiriForest", "TBox_Rupee_Blue", pos=(1.0, 0.0, 0.0)),  # two blue: ambiguous
        loc(3, "chest", "KokiriForest", "TBox_Rupee_Blue", pos=(2.0, 0.0, 0.0)),
        loc(4, "chest", "KokiriForest", "TBox_Rupee_Red", pos=(3.0, 0.0, 0.0)),
        loc(5, "chest", "KokiriForest", "TBox_Rupee_Red", pos=(3.0, 0.0, 0.0), files=ADULT_KF),  # copy of 4
        loc(6, "gold_skulltula", "KokiriForest", "Obj_Token_Gold"),
        loc(7, "shop_slot", "KokiriForest", "Shop_Heart", pos=(10.0, 0.0, 0.0), slot=0),
        loc(8, "shop_slot", "KokiriForest", "Shop_Heart", pos=(10.0, 0.0, 0.0), slot=0, files=ADULT_KF),
        loc(9, "shop_slot", "KokiriForest", "Shop_DekuStick", pos=(11.0, 0.0, 0.0), slot=1),
        loc(10, "chest", "InsideTheDekuTree", "Item_Dungeon_Map", room=0),
        loc(11, "chest", "InsideTheDekuTree", "TBox_DekuNutBundle", room=4, pos=(5.0, 0.0, 0.0)),
    ]
    found = {i: (m.name, m.basis) for i, m in ootr.match(locations, location_list).items()}
    assert found == {
        1: ("KF Kokiri Sword Chest", ootr.ITEM),
        4: ("KF Storms Grotto Chest", ootr.ITEM),
        5: ("KF Storms Grotto Chest", ootr.ITEM),
        7: ("KF Shop Item 1", ootr.SHOP),
        8: ("KF Shop Item 1", ootr.SHOP),
        9: ("KF Shop Item 2", ootr.SHOP),
        10: ("Deku Tree Map Chest", ootr.ITEM),
        11: ("Deku Tree Basement Chest", ootr.RESIDUAL),
    }


def test_treasure_game_rooms_count_back_from_the_reward():
    boxes = [
        loc(
            100, "treasure_game_reward", "Market", "Obj_Heart_Piece", actor="Obj_HrlCity_Shop_TBox_A_02", pos=(0, 0, 0)
        ),
        loc(101, "treasure_game_reward", "Market", "TBox_Rupee_Red", actor="Obj_HrlCity_Shop_TBox_A_02", pos=(0, 0, 0)),
    ]
    for room in range(5):  # room 5 is nearest the reward
        x = -10.0 * (5 - room)
        boxes.append(loc(200 + room, "treasure_game_box", "Market", "Obj_MiniGame_SmallKey", pos=(x, 0, -3)))
        boxes.append(loc(300 + room, "treasure_game_box", "Market", "TBox_Rupee_Green", pos=(x, 0, 3)))
    names = ootr.treasure_game(boxes)
    assert names[100] == "Market Treasure Chest Game Reward"
    assert 101 not in names
    assert (names[200], names[300]) == (
        "Market Treasure Chest Game Room 1 Top",
        "Market Treasure Chest Game Room 1 Bottom",
    )
    assert names[204] == "Market Treasure Chest Game Room 5 Top"
    assert ootr.treasure_game(boxes[:-1]) == {}  # a room with one box: not the expected layout


def test_only_the_treasure_game_reward_is_its_own_kind():
    def kind(name):
        return ootr.OotrLocation(name, "Chest", 0x10, None, ("Market",)).kind

    assert kind("Market Treasure Chest Game Reward") == "treasure_game_reward"
    assert kind("Market Treasure Chest Game Room 1 Top") == "treasure_game_box"


def test_shops_are_named_by_area_and_contents():
    locs = [
        loc(1, "shop_slot", "Market", "Shop_BombchuBundle_01", pos=(0.0, 0.0, 0.0), slot=0),
        loc(2, "shop_slot", "Market", "Shop_Heart", pos=(2.0, 0.0, 0.0), slot=1),  # same shelf, 2 apart
        loc(3, "shop_slot", "Market", "Shop_Bottle_Bug", pos=(20.0, 0.0, 0.0), slot=0),
    ]
    named = {name: [x.id for x in members] for name, members in ootr.shops(locs).items()}
    assert named == {"Market Bombchu Shop": [1, 2], "Market Potion Shop": [3]}


# --------------------------------------------------------------------------------------------------------------
# Definitions file


def test_definitions_round_trip_and_hand_edits_survive():
    locations = [
        loc(BIG, "chest", "KokiriForest", "TBox_Rupee_Blue"),
        loc(2, "chest", "KokiriForest", "TBox_Rupee_Blue", pos=(5.0, 0.0, 0.0)),
        loc(3, "gold_skulltula", "KokiriForest", "Obj_Token_Gold"),
    ]
    defs = definitions.build(locations, {3: ootr.Match("KF GS Know It All House", ootr.ITEM)})
    assert [d.name for d in defs] == [
        "Kokiri Forest Chest (TBox_Rupee_Blue) #1",
        "Kokiri Forest Chest (TBox_Rupee_Blue) #2",
        "KF GS Know It All House",
    ]
    text = definitions.dumps(defs)
    assert definitions.loads(text) == defs

    edited = {BIG: definitions.Definition(BIG, "chest", "KokiriForest", "Mido Chest", "TBox_Rupee_Blue", "X")}
    rebuilt = definitions.build(locations, {}, existing=edited)
    assert (rebuilt[0].name, rebuilt[0].oot_randomizer_name) == ("Mido Chest", "X")
    assert rebuilt[1].name == "Kokiri Forest Chest (TBox_Rupee_Blue)"
    assert rebuilt[2].oot_randomizer_name == ""


def test_definitions_reject_duplicate_names():
    row = 'id = "{}"\nkind = "chest"\narea = "A"\nname = "Same"\nvanilla_item = "I"\noot_randomizer_name = ""\n'
    text = "[[location]]\n" + row.format(1) + "[[location]]\n" + row.format(2)
    with pytest.raises(definitions.DefinitionError, match="Same"):
        definitions.loads(text)
