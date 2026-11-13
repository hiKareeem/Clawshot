"""The headless tracker against synthetic seeds and saves: every field is built here, none comes from the game."""

import json
import struct
from pathlib import Path

import pytest

from clawshot import save
from clawshot.tracker import SeedError, build_state, load_seed, seeds
from clawshot.tracker import state as tracker_state
from clawshot.tracker.seeds import NATIVE_SAVED_BOOLS, Place, installed_version

SAVE_TYPE = 0xA3DB7114  # progress.sav's Bool64bitKey pair key (MetaData.SaveTypeHash)

PLACES = {
    "Test Chest": Place("Test", None, "Chest"),
    "Test Hidden Chest": Place("Test", None, "Chest"),
    "Test Copy Chest": Place("Test", None, "Chest"),
    "Forest Key Chest": Place("Forest Temple", "Forest Temple", "Chest"),
    "Forest Floor Key": Place("Forest Temple", "Forest Temple", "Collectable", vanilla="Small Key (Forest Temple)"),
    "Forest Gone Key": Place(
        "Forest Temple", "Forest Temple", "Collectable", vanilla="Small Key (Forest Temple)", n64_only=True
    ),
    "Forest Map Chest": Place("Forest Temple", "Forest Temple", "Chest", vanilla="Map (Forest Temple)"),
    "DMT Great Fairy Reward": Place("Death Mountain Trail", None, "NPC"),
    "Song from Windmill": Place("Kakariko Village", None, "Song"),
    "LW Skull Kid": Place("Lost Woods", None, "NPC"),
    "DMC Deku Scrub": Place("Death Mountain Crater", None, "Scrub"),
    "Test Shop Item": Place("Market", None, "Shop"),
    "Test Boss Heart": Place("Deku Tree", "Deku Tree", "BossHeart"),
}
PLACEMENTS = {
    "Test Chest": "Boss Key (Forest Temple)",
    "Test Hidden Chest": "Rupees (50)",
    "Test Copy Chest": "Small Key (Forest Temple)",
    "Forest Key Chest": "Small Key (Forest Temple)",
    "DMT Great Fairy Reward": "Hookshot",
    "Song from Windmill": "Bolero of Fire",
    "LW Skull Kid": "Piece of Heart",
    "DMC Deku Scrub": "Piece of Heart",
    "Test Shop Item": "Buy Arrows (10)",
    "Test Boss Heart": "Heart Container",
    "Unknown Place Chest": "Rupees (5)",
}
LOCATIONS = {
    "Test Chest": {"name": "Test Chest", "where": "Test", "ids": ["123"]},
    "Test Hidden Chest": {"name": "Hidden Chest", "where": "Test", "ids": ["456"]},
    "Test Copy Chest": {"name": "Copy Chest", "where": "Test", "ids": ["1001", "1002"]},
    "Forest Key Chest": {"name": "Forest Key Chest", "where": "Forest", "ids": ["789"]},
    "DMT Great Fairy Reward": {"name": "Summit Fairy", "where": "DMT", "ids": ["Dm_FairyFountain_Din/Event212"]},
    "Test Boss Heart": {"name": "Boss Pickup", "where": "Deku", "ids": ["555"]},
}
PATCH = {
    "changes": [
        {"location": "Test Chest", "id": "123", "chest": "Obj_TBox_A_01"},
        {"location": "Forest Key Chest", "id": "789", "chest": "Obj_TBox_A_01"},
    ],
    "unchanged": [{"location": "Test Hidden Chest", "id": "456"}],
}
FAIRY_FLAG = "Clawshot.Gift.Dm_FairyFountain_Din.Event212"


@pytest.fixture
def places(monkeypatch):
    monkeypatch.setattr(seeds, "location_index", lambda: PLACES)
    return PLACES


def build_save(
    bools=None, ints=None, keys=(), *, bool_total=NATIVE_SAVED_BOOLS, extra=None, terminate=True, table_end=None
) -> bytes:
    """A synthetic progress.sav: named Bools/Ints, unnamed Bools padding the section to ``bool_total`` (an unmodified
    GameDataList's count), any ``extra`` sections, then the Bool64bitKey list."""
    sections = {
        save.BOOL: {save.key(name): int(bool(value)) for name, value in (bools or {}).items()},
        save.INT: {save.key(name): value & 0xFFFFFFFF for name, value in (ints or {}).items()},
        **(extra or {}),
    }
    sections[save.INT].setdefault(1, 0)  # every real save has Ints
    for filler in range(1, bool_total - len(sections[save.BOOL]) + 1):
        assert filler not in sections[save.BOOL]
        sections[save.BOOL][filler] = 0
    table = b""
    for section in sorted(sections):
        table += struct.pack("<II", 0, section)
        table += b"".join(struct.pack("<II", k, v) for k, v in sections[section].items())
    end = save.HEADER_SIZE + len(table) + 16
    table += struct.pack("<II", 0, save.BOOL64) + struct.pack("<II", SAVE_TYPE, end)
    header = struct.pack("<III", save.MAGIC, 1, end if table_end is None else table_end).ljust(save.HEADER_SIZE, b"\0")
    data = b"".join(struct.pack("<Q", k) for k in keys) + (struct.pack("<Q", 0) if terminate else b"")
    return header + table + data


def parse(bools=None, ints=None, keys=(), **options) -> save.Save:
    return save.read(build_save(bools, ints, keys, **options))


def make_seed(tmp_path, placements=None, locations=None, patch=None, *, layout="ui", name="seed-1"):
    root = tmp_path / name
    seed_dir = root / "seed"
    seed_dir.mkdir(parents=True)
    spoiler = {
        "generator": f"clawshot {installed_version()}",
        "seed": 1,
        "settings_string": "CS1-test",
        "settings": {"dungeon_items": "own_dungeon", "shuffle": ["Chest"]},
        "placements": PLACEMENTS if placements is None else placements,
        "item_names": {"Rupees (50)": "Purple Rupee"},
        "locations": LOCATIONS if locations is None else locations,
        "patch": PATCH if patch is None else patch,
        "hints": [{"text": "They say Test hides Rupees (50)."}],
    }
    (seed_dir / "spoiler.json").write_text(json.dumps(spoiler), encoding="utf-8")
    if layout == "ui":
        manifest = {"seed": 1, "settings_string": "CS1-test", "output_sha256": "ab" * 32}
        (root / "clawshot-seed.json").write_text(json.dumps(manifest), encoding="utf-8")
    elif layout == "pack":
        (root / "pack.json").write_text(json.dumps({"seed": 1}), encoding="utf-8")
    return root


def by_id(state, group="items"):
    return {cell["id"]: cell for cell in state[group]}


def checks(state):
    return {check["id"]: check for area in state["areas"] for check in area["checks"]}


def test_seed_layouts_and_save_folder(tmp_path, places):
    root = make_seed(tmp_path)
    for path in (root, root / "seed", root / "seed" / "spoiler.json"):
        seed = load_seed(path)
        assert (seed.root, seed.layout, seed.user_path) == (root, "ui", root / "user")
    assert seed.metadata["short_hash"] == "AB" * 6 and seed.metadata["seed"] == 1
    assert not [w for w in seed.warnings if "made by" in w]  # same generator version: no version warning

    pack = load_seed(make_seed(tmp_path, layout="pack", name="pack"))
    assert (pack.layout, pack.user_path) == ("pack", tmp_path / "pack" / "user")

    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "spoiler.json").write_text((root / "seed" / "spoiler.json").read_text(encoding="utf-8"), encoding="utf-8")
    assert (load_seed(raw).layout, load_seed(raw).user_path) == ("raw", None)
    (raw / "user").mkdir()
    assert load_seed(raw).user_path == raw / "user"

    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(SeedError, match="No seed here"):
        load_seed(empty)
    with pytest.raises(SeedError, match="does not exist"):
        load_seed(tmp_path / "missing")
    (raw / "spoiler.json").write_text("{", encoding="utf-8")
    with pytest.raises(SeedError, match="not valid JSON"):
        load_seed(raw)


def test_seed_checks_kinds_and_dungeon_totals(tmp_path, places):
    seed = load_seed(make_seed(tmp_path))
    kinds = {check.location: (check.kind, check.method) for check in seed.checks}
    assert kinds == {
        "Test Chest": ("chest", "named_bool"),
        "Test Hidden Chest": ("chest", "named_bool"),
        "Test Copy Chest": ("chest", "named_bool"),
        "Forest Key Chest": ("chest", "named_bool"),
        "DMT Great Fairy Reward": ("gift", "named_bool"),
        "Song from Windmill": ("gift", "named_bool"),
        "LW Skull Kid": ("gift", "none"),
        "DMC Deku Scrub": ("scrub", "named_bool"),
        "Test Shop Item": ("shop", "none"),
        "Test Boss Heart": ("boss_heart", "placement_hash"),
        "Unknown Place Chest": ("other", "none"),
    }
    copy = next(c for c in seed.checks if c.location == "Test Copy Chest")
    assert copy.flags == ("IsTreasureBoxOpen.1001", "IsTreasureBoxOpen.1002")
    # Two placed keys plus the unshuffled floor key; the N64-only one is not in the remake.
    assert seed.small_keys == {"Forest Temple": 3}
    assert seed.boss_keys == {"Forest Temple": 1} and seed.maps == {"Forest Temple": 1}
    assert seed.added_flags == ((FAIRY_FLAG,),)
    assert any("not in this version's world data" in w for w in seed.warnings)
    assert next(c for c in seed.checks if c.location == "Unknown Place Chest").area == "Other"


def test_named_chest_record_beats_conflicting_raw_hash(tmp_path, places):
    seed = load_seed(make_seed(tmp_path))
    opened = parse(
        {"IsTreasureBoxOpen.123": True, "IsTreasureBoxOpen.456": False, "IsTreasureBoxOpen.789": False},
        keys=[456, 789],  # raw chest Hashes set, as a raw-Hash reader would misread
    )
    found = checks(build_state(seed, opened))
    assert found["Test Chest"]["collected"] is True  # named true, raw Hash unset
    assert found["Test Hidden Chest"]["collected"] is False  # raw Hash set, named false
    assert found["Forest Key Chest"]["collected"] is False
    assert found["Test Copy Chest"]["collected"] is None  # neither copy's named field: unknown, not "not opened"
    assert "reason" in found["Test Copy Chest"]
    one_copy = parse({"IsTreasureBoxOpen.1001": False, "IsTreasureBoxOpen.1002": True})
    assert checks(build_state(seed, one_copy))["Test Copy Chest"]["collected"] is True
    neither = parse({"IsTreasureBoxOpen.1001": False, "IsTreasureBoxOpen.1002": False})
    assert checks(build_state(seed, neither))["Test Copy Chest"]["collected"] is False


def test_gift_scrub_heart_and_unrecorded_checks(tmp_path, places):
    seed = load_seed(make_seed(tmp_path))
    state = build_state(
        seed,
        parse(
            {
                FAIRY_FLAG: True,
                "HavePlayedEvent.Dm_MelodyGet_Storm": False,
                "DeathMountain_Enemy_Scrub_Business_HeartPiece_01": True,
            },
            keys=[555],
            bool_total=NATIVE_SAVED_BOOLS + 1,
        ),
    )
    found = checks(state)
    assert found["DMT Great Fairy Reward"]["collected"] is True
    assert found["Song from Windmill"]["collected"] is False
    assert found["DMC Deku Scrub"]["collected"] is True
    assert found["Test Boss Heart"]["collected"] is True
    for unrecorded in ("LW Skull Kid", "Test Shop Item", "Unknown Place Chest"):
        assert found[unrecorded]["collected"] is None and found[unrecorded]["reason"]
    # An unset placement Hash is never claimed as "not collected".
    assert checks(build_state(seed, parse()))["Test Boss Heart"]["collected"] is None
    areas = {area["name"]: area for area in state["areas"]}
    assert (areas["Market"]["collected"], areas["Market"]["total"], areas["Market"]["unknown"]) == (0, 1, 1)
    assert list(areas)[:2] == ["Test", "Forest Temple"]


def test_spoiler_free_by_default_and_opt_in(tmp_path, places):
    seed = load_seed(make_seed(tmp_path))
    opened = parse({"IsTreasureBoxOpen.123": True, "IsTreasureBoxOpen.456": False})
    default = build_state(seed, opened)
    text = json.dumps(default)
    assert "Rupees (50)" not in text and "Purple Rupee" not in text  # the unopened chest's item, nowhere
    found = checks(default)
    assert found["Test Chest"]["item"] == "Boss Key (Forest Temple)"  # seen: collected
    assert all("item" not in c for c in found.values() if c["collected"] is not True)
    shown = checks(build_state(seed, opened, show_locations=True))
    assert shown["Test Hidden Chest"]["item"] == "Rupees (50)"
    assert shown["Test Hidden Chest"]["item_label"] == "Purple Rupee"
    assert all("item" in c for c in shown.values())
    assert "hints" not in default["seed"] and "placements" not in default["seed"]


def test_small_keys_spent_versus_found_and_absent_fields(tmp_path, places):
    seed = load_seed(make_seed(tmp_path))
    prefix = "DungeonInfo.ForestTemple."
    state = build_state(
        seed,
        parse(
            {prefix + "IsGetSmallKeyOnce": True, prefix + "IsGetBossKey": True, prefix + "IsGetMap": False},
            {prefix + "SmallKeyNum": 1, prefix + "SmallKeyTotalNum": 3},
        ),
    )
    assert state["dungeons"][0]["name"] == "Deku Tree"  # keys first, in game order
    forest = next(d for d in state["dungeons"] if d["id"] == "ForestTemple")
    assert forest["small_keys"] == {"held": 1, "found": 3, "total": 3, "first_found": True}
    assert (forest["boss_key"], forest["map"], forest["compass"]) == (True, False, None)
    assert (forest["has_boss_key"], forest["has_map"], forest["has_compass"]) == (True, True, False)
    water = next(d for d in state["dungeons"] if d["id"] == "WaterTemple")
    assert water["small_keys"] == {"held": None, "found": None, "total": 0, "first_found": None}


def test_consumed_equipment_is_not_held(tmp_path, places):
    seed = load_seed(make_seed(tmp_path))
    bools = {f"IsGet.{a}": True for a in ("Weapon_Sword_Giant", "Weapon_Sword_BrokenGiant", "Weapon_Shield_Deku")}
    bools |= {"IsGet.Item_PocketEgg": True, "IsGet.Item_CojiroCucco": True, "IsGet.Item_ZeldaLetter": True}
    stocks = {"Weapon_Sword_Giant": 0, "Weapon_Sword_BrokenGiant": 1, "Weapon_Shield_Deku": 0, "Item_PocketEgg": 0}
    stocks |= {"Item_CojiroCucco": 1, "Item_WeirdEgg": 0, "Item_AlarmCucco": 0, "Item_ZeldaLetter": 0}
    stocks |= {"Weapon_Range_Bow": 0}
    items = by_id(build_state(seed, parse(bools, {f"PouchData.{a}.StockNum": n for a, n in stocks.items()})))
    assert (items["giants_knife"]["held"], items["giants_knife"]["ever"]) == (False, True)
    assert (items["broken_knife"]["held"], items["broken_knife"]["ever"]) == (True, True)
    assert (items["deku_shield"]["held"], items["deku_shield"]["ever"]) == (False, True)
    child = items["child_trade"]
    assert (child["held"], child["tier"], child["ever"]) == (False, 0, True)  # the letter was handed over
    adult = items["adult_trade"]
    assert (adult["held"], adult["tier"], adult["label"], adult["icon"]) == (True, 3, "Cojiro", "Item_CojiroCucco")
    assert (items["bow"]["held"], items["bow"]["ever"]) == (False, None)  # stock 0; no IsGet field: unknown
    assert items["hammer"]["held"] is None and items["hammer"]["tier"] is None  # no fields at all


def no_checks_seed():
    folder = Path("seed")
    return seeds.Seed(folder, folder, folder / "spoiler.json", None, "raw", {}, ())


def _cells(save_value):
    state = build_state(no_checks_seed(), save_value)
    return [*state["items"], *state["songs"], *state["rewards"]]


def test_every_item_mapping_reads_its_own_fields():
    for cell_id, _group, tiers, _count in tracker_state.TIERS:
        for n, (label, actor) in enumerate(tiers, 1):
            only = parse({f"IsGet.{actor}": True}, {f"PouchData.{actor}.StockNum": 1})
            cell = next(c for c in _cells(only) if c["id"] == cell_id)
            assert (cell["tier"], cell["held"], cell["label"], cell["icon"]) == (n, True, label, actor)
    for cell_id, _group, _label, actor, _counted in tracker_state.SINGLES:
        only = parse({f"IsGet.{actor}": True}, {f"PouchData.{actor}.StockNum": 1})
        held = {c["id"] for c in _cells(only) if c["held"]}
        assert held == {cell_id}, (cell_id, held)
    for cell_id, _label, actor in tracker_state.SONGS:
        assert {c["id"] for c in _cells(parse({f"IsGet.{actor}": True})) if c["held"]} == {cell_id}
    for cell_id, _label, actor in tracker_state.REWARDS:
        only = parse({f"IsGet.{actor}": True}, {f"PouchData.{actor}.StockNum": 1})
        assert {c["id"] for c in _cells(only) if c["held"]} == {cell_id}


def test_bottles_count_owned_slots_not_content_history():
    blue, fairy, empty = (save.murmur3_32(name.encode()) for name in ("BlueFire", "Fairy", "Empty"))
    slots = tracker_state.BOTTLE_SLOTS
    owned = {valid: n < 2 for n, (_slot, valid, _content) in enumerate(slots)}
    values = (blue, fairy, empty, empty, blue)
    contents = {content: value for (_slot, _valid, content), value in zip(slots, values, strict=True)}
    history = {"IsGet.Item_Bottle_Bug": True, "IsGet.Item_Bottle_Letter": True}
    cell = by_id(build_state(no_checks_seed(), parse(owned | history, extra={save.ENUM: contents})))["bottles"]
    assert (cell["count"], cell["held"], cell["tier"], cell["max_tier"], cell["ever"]) == (2, True, 2, 5, True)
    assert cell["contents"] == [{"slot": "BottleA", "content": "Blue Fire"}, {"slot": "BottleB", "content": "Fairy"}]
    none_owned = {valid: False for _slot, valid, _content in slots}
    cell = by_id(build_state(no_checks_seed(), parse(none_owned | history, extra={save.ENUM: contents})))["bottles"]
    assert (cell["count"], cell["held"], cell["contents"], cell["ever"]) == (0, False, [], True)
    cell = by_id(build_state(no_checks_seed(), parse(history)))["bottles"]
    assert (cell["count"], cell["held"], cell["contents"]) == (None, None, None)  # no owned flags: unknown


def test_counts_magic_hearts_and_tokens():
    ints = {
        "PlayerStatus.MPMax": 480,
        "PlayerStatus.MaxLife": 20,
        "PlayerStatus.CurrentRupee": 321,
        "PouchData.Obj_Heart_Piece.StockNum": 2,
        "PouchData.Item_Token_Gold.StockNum": 17,
        "PouchData.Item_Wallet_Large.StockNum": 1,
        "PouchData.Item_BombBag_Small.StockNum": 1,
        "PouchData.Item_Bomb.StockNum": 9,
        "PouchData.Item_Bombchu.StockNum": 5,
    }
    state = build_state(no_checks_seed(), parse(ints=ints))
    items = by_id(state)
    assert (items["magic"]["tier"], items["magic"]["label"], items["magic"]["count"]) == (2, "Double Magic", 480)
    assert (items["wallet"]["tier"], items["wallet"]["count"]) == (3, 321)
    assert (items["bomb_bag"]["tier"], items["bomb_bag"]["count"]) == (1, 9)
    assert items["bombchus"]["count"] == 5
    assert state["hearts"] == {"containers": 5, "max_life": 20, "pieces": 2}
    assert state["tokens"] == 17
    no_meter = by_id(build_state(no_checks_seed(), parse(ints={"PlayerStatus.MPMax": 0})))["magic"]
    assert (no_meter["tier"], no_meter["held"]) == (0, False)
    assert by_id(build_state(no_checks_seed(), parse()))["magic"]["held"] is None


def test_no_save_is_all_unknown(tmp_path, places):
    state = build_state(load_seed(make_seed(tmp_path)), None)
    assert state["identity"]["status"] == "unknown"
    assert all(c["collected"] is None for c in checks(state).values())
    assert all(a["unknown"] == a["total"] for a in state["areas"])
    assert all(c["held"] is None for c in [*state["items"], *state["songs"], *state["rewards"]])
    assert state["tokens"] is None and state["hearts"]["containers"] is None
    assert all(d["boss_key"] is None and d["small_keys"]["held"] is None for d in state["dungeons"])
    json.dumps(state)


def test_save_identity_from_the_seeds_added_flags(tmp_path, places):
    seed = load_seed(make_seed(tmp_path))
    matching = build_state(seed, parse({FAIRY_FLAG: False}, bool_total=NATIVE_SAVED_BOOLS + 1))
    assert matching["identity"]["status"] == "consistent"
    assert not any("belong" in w for w in matching["warnings"])
    for other in (parse(), parse({"Clawshot.Gift.Other.Event1": True}, bool_total=NATIVE_SAVED_BOOLS + 2)):
        state = build_state(seed, other)
        assert state["identity"]["status"] == "mismatch"
        assert any("may not belong to this seed" in w for w in state["warnings"])
    plain = load_seed(make_seed(tmp_path, {"Test Chest": "Bow"}, name="plain"))
    unverifiable = build_state(plain, parse())
    assert unverifiable["identity"]["status"] == "unverifiable"
    assert any("Cannot confirm" in w for w in unverifiable["warnings"])
    assert build_state(plain, parse(bool_total=5))["identity"]["status"] == "unverifiable"
