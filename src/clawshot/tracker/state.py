"""What a save holds, against a seed: ``build_state(seed, save) -> dict`` (JSON-able, spoiler-free by default).

Every value read from a save cites what its field means. ``None`` always means *unknown* (no save, or the save has
no such field); ``False``/``0`` mean the save has the field and it says absent. Sources:

- [S6] plans/03-game-data.md section 6: inventory is the ``PouchData`` Struct; ``PouchData.Item_Token_Gold.StockNum``
  is the token count the Skulltula House reads.
- [S19] section 19: ``IsGet.<pouch name>`` is set whenever the item enters the pouch, however it is got (an
  ever-acquired flag); equipment reads under its pouch/equipment actor (``RSDB/PouchActorInfo``); the save's Bool
  section holds exactly the GameDataList's saved Bools (10212).
- [S44] section 44: ``DungeonInfo.<Dungeon>.SmallKeyNum`` (remaining) and ``SmallKeyTotalNum`` (acquired total),
  ``IsGetSmallKeyOnce``, ``IsGetBossKey``, ``IsGetMap``, ``IsGetCompass``; a positive key grant raises remaining and
  total, spending lowers remaining only. Chests: ``IsTreasureBoxOpen.<decimal Hash>``.
- [SL1] sloperina-FINDINGS.md section 1: ``PouchData.<item>.StockNum`` is the count owned and ``IsGet.<item>`` the
  ever-acquired flag; the ``DungeonInfo`` dungeon names; magic capacity 0 = no meter, 240 normal, 480 double.
- [SL57] section 5.7: upgrades are held pouch items (``Item_StickBag_*``, ``Item_NutBag_*``, ``Item_BulletBag_*``,
  ``Item_BombBag_*``, ``Item_Quiver_*``, ``Item_Wallet_*``, ``Item_Scale_*``, ``Item_FairyBless_*``,
  ``Armor_Child_Gauntlet_Goron``, ``Armor_Adult_Gauntlet_Silver/Gold``); the screens read the pouch, not numbers.
- [SL58] section 5.8: ``DungeonInfo.<Dungeon>.IsGet*`` are what the map screen reads.
- [R9] plans/rounds/r9-itembar.md: ``Item_Range_Bow`` saves as ``Weapon_Range_Bow`` (pouch rows of PouchActorInfo).
- [R7] plans/rounds/r7-play.md / section 30: ``Armor_Child_Gauntlet_Goron`` is the saved bracelet name.
- [AUDIT] Round 14's read-only audit, outside the repository (E:/OOTRemake/work/r14-tracker/probe2-8.py): every
  pouch name below is a ``RSDB/PouchActorInfo`` row id (build e0f3ccfa) whose ``IsGet.<name>`` (and, for counted
  items, ``PouchData.<name>.StockNum``) is a GameDataList entry present in copied real saves; so are
  ``PlayerStatus.MaxLife`` (plans/playtest/answers.md R10-DIGGING reads it), ``PlayerStatus.MPMax`` and
  ``PlayerStatus.CurrentRupee``, and the bottle Struct described at :data:`BOTTLE_SLOTS`.

Held versus ever acquired: a counted item is *held* only while its stock is above 0, so a broken Giant's Knife, a
burnt Deku Shield or a handed-over trade item shows ``held: false, ever: true``. Songs have no stock field and are
held once acquired (``basis: "ever_acquired"``). Bottles are counted from their own owned flags, never from the
``IsGet`` history of their contents.
"""

from typing import Any

from clawshot import save as save_format
from clawshot.tracker.seeds import (
    DUNGEON_INFO,
    NAMED_BOOL,
    NATIVE_SAVED_BOOLS,
    PLACEMENT_HASH,
    Check,
    Seed,
)

# Display names of the world's dungeons (data/hints.toml [areas], leading "the " dropped).
DUNGEON_LABELS = {
    "Deku Tree": "Deku Tree",
    "Dodongos Cavern": "Dodongo's Cavern",
    "Jabu Jabus Belly": "Jabu-Jabu's Belly",
    "Forest Temple": "Forest Temple",
    "Fire Temple": "Fire Temple",
    "Water Temple": "Water Temple",
    "Shadow Temple": "Shadow Temple",
    "Spirit Temple": "Spirit Temple",
    "Bottom of the Well": "Bottom of the Well",
    "Ice Cavern": "Ice Cavern",
    "Gerudo Training Ground": "Gerudo Training Ground",
    "Ganons Castle": "Ganon's Castle",
}


def _sizes(labels: tuple[str, str, str], family: str) -> tuple[tuple[str, str], ...]:
    """The Small, Medium and Large pouch items of an upgrade family (``Item_<family>_<size>``) [SL57]."""
    return tuple(zip(labels, (f"Item_{family}_{size}" for size in ("Small", "Medium", "Large")), strict=True))


# Tier cells: (id, group, ((label, pouch name), ...), count field). A tier is held while its pouch stock is above 0
# [SL1]; the cell's tier is the highest held. Upgrade families [SL57]; hookshots, ocarinas and arrows [S19] / [R9].
# The count field is ``Stock:<pouch name>`` (ammunition) or ``Int:<field>`` (``PlayerStatus.CurrentRupee``, the
# rupees held: an Int every game save has).
TIERS: tuple[tuple[str, str, tuple[tuple[str, str], ...], str | None], ...] = (
    ("hookshot", "upgrades", (("Hookshot", "Item_Hookshot"), ("Longshot", "Item_Longshot")), None),
    (
        "strength",
        "upgrades",
        (
            ("Goron's Bracelet", "Armor_Child_Gauntlet_Goron"),
            ("Silver Gauntlets", "Armor_Adult_Gauntlet_Silver"),
            ("Golden Gauntlets", "Armor_Adult_Gauntlet_Gold"),
        ),
        None,
    ),
    ("scale", "upgrades", (("Silver Scale", "Item_Scale_Silver"), ("Golden Scale", "Item_Scale_Gold")), None),
    (
        "wallet",
        "upgrades",
        _sizes(("Child's Wallet", "Adult's Wallet", "Giant's Wallet"), "Wallet"),
        "Int:PlayerStatus.CurrentRupee",
    ),
    ("bomb_bag", "upgrades", _sizes(("Bomb Bag", "Big Bomb Bag", "Biggest Bomb Bag"), "BombBag"), "Stock:Item_Bomb"),
    (
        "bullet_bag",
        "upgrades",
        _sizes(("Bullet Bag", "Big Bullet Bag", "Biggest Bullet Bag"), "BulletBag"),
        "Stock:Item_DekuSeed",
    ),
    ("quiver", "upgrades", _sizes(("Quiver", "Big Quiver", "Biggest Quiver"), "Quiver"), "Stock:Item_Arrow_Normal"),
    (
        "stick_bag",
        "upgrades",
        _sizes(("Deku Stick Bag", "Big Deku Stick Bag", "Biggest Deku Stick Bag"), "StickBag"),
        "Stock:Item_DekuStick",
    ),
    (
        "nut_bag",
        "upgrades",
        _sizes(("Deku Nut Bag", "Big Deku Nut Bag", "Biggest Deku Nut Bag"), "NutBag"),
        "Stock:Item_DekuNut",
    ),
    ("ocarina", "items", (("Fairy Ocarina", "Item_Ocarina_Fairy"), ("Ocarina of Time", "Item_Ocarina_Time")), None),
    (
        "child_trade",
        "trade",
        (("Weird Egg", "Item_WeirdEgg"), ("Cucco", "Item_AlarmCucco"), ("Zelda's Letter", "Item_ZeldaLetter")),
        None,
    ),
    (
        "adult_trade",
        "trade",
        (
            ("Pocket Egg", "Item_PocketEgg"),
            ("Pocket Cucco", "Item_PocketCucco"),
            ("Cojiro", "Item_CojiroCucco"),
            ("Odd Mushroom", "Item_OddMushroom"),
            ("Odd Poultice", "Item_OddPowder"),
            ("Poacher's Saw", "Item_PoacherSaw"),
            ("Broken Goron Sword", "Item_BrokenSword"),
            ("Prescription", "Item_Prescription"),
            ("Eyeball Frog", "Item_EyeballFrog"),
            ("Eye Drops", "Item_EyeDrop"),
            ("Biggoron Receipt", "Item_ClaimCheck"),
        ),
        None,
    ),
)

# Single counted cells: (id, group, label, pouch name, whether the stock is a useful count). [SL1] [S19] [R9] [R7]
SINGLES: tuple[tuple[str, str, str, str, bool], ...] = (
    ("slingshot", "items", "Fairy Slingshot", "Weapon_Range_SlingShot", False),
    ("bow", "items", "Fairy Bow", "Weapon_Range_Bow", False),
    ("boomerang", "items", "Boomerang", "Item_Boomerang", False),
    ("hammer", "items", "Megaton Hammer", "Item_Hammer", False),
    ("lens", "items", "Lenses of Truth", "Armor_GlassTruth", False),
    ("fire_arrows", "items", "Fire Arrow", "Item_Arrow_Fire", False),
    ("ice_arrows", "items", "Ice Arrow", "Item_Arrow_Ice", False),
    ("light_arrows", "items", "Light Arrow", "Item_Arrow_Light", False),
    ("dins_fire", "items", "Din's Fire", "Item_DinFire", False),
    ("farores_wind", "items", "Farore's Wind", "Item_FaroreWind", False),
    ("nayrus_love", "items", "Nayru's Love", "Item_NayruLove", False),
    ("bombchus", "items", "Bombchus", "Item_Bombchu", True),
    ("magic_beans", "items", "Magic Beans", "Item_MagicBean", True),
    ("kokiri_sword", "equipment", "Kokiri Sword", "Weapon_Sword_Kokiri", False),
    ("master_sword", "equipment", "Master Sword", "Weapon_Sword_Master", False),
    ("giants_knife", "equipment", "Giant's Knife", "Weapon_Sword_Giant", False),
    ("broken_knife", "equipment", "Broken Giant's Knife", "Weapon_Sword_BrokenGiant", False),
    ("biggoron_sword", "equipment", "Biggoron's Sword", "Weapon_Sword_Biggoron", False),
    ("deku_shield", "equipment", "Deku Shield", "Weapon_Shield_Deku", False),
    ("hylian_shield", "equipment", "Hylian Shield", "Weapon_Shield_Hylian", False),
    ("mirror_shield", "equipment", "Mirror Shield", "Weapon_Shield_Mirror", False),
    # Kokiri Tunic: adult and child rows (both stock 1 in every audited save; no saved row exists for plain boots).
    ("kokiri_tunic", "equipment", "Kokiri Tunic", "Armor_Adult_Normal", False),
    ("kokiri_tunic_child", "equipment", "Kokiri Tunic (child)", "Obj_Armor_Child_Normal", False),
    ("goron_tunic", "equipment", "Goron Tunic", "Armor_Adult_Goron", False),
    ("zora_tunic", "equipment", "Zora Tunic", "Armor_Adult_Zora", False),
    ("iron_boots", "equipment", "Iron Boots", "Armor_Adult_HeavyBoot", False),
    ("hover_boots", "equipment", "Hover Boots", "Armor_Adult_HoverBoot", False),
    ("double_defense", "upgrades", "Gift of Halved Damage", "Item_FairyBless_DefenseDouble", False),
    ("stone_of_agony", "quest", "Echo Gem", "Item_AgonyStone", False),
    ("gerudo_card", "quest", "Gerudo Pass", "Item_Token_Gerudo", False),
    ("keaton_mask", "trade", "Keaton Mask", "Armor_Child_Mask_Keaton", False),
    ("skull_mask", "trade", "Skull Mask", "Armor_Child_Mask_Skull", False),
    ("spooky_mask", "trade", "Spooky Mask", "Armor_Child_Mask_Spooky", False),
    ("bunny_hood", "trade", "Bunny Hood", "Armor_Child_Mask_Bunny", False),
    ("mask_of_truth", "trade", "Mask of Truth", "Armor_Child_Mask_Truth", False),
    ("goron_mask", "trade", "Goron Mask", "Armor_Child_Mask_Goron", False),
    ("zora_mask", "trade", "Zora Mask", "Armor_Child_Mask_Zora", False),
    ("gerudo_mask", "trade", "Gerudo Mask", "Armor_Child_Mask_Gerudo", False),
)

# Bottles. GameDataList (build e0f3ccfa) has a Struct (hash 4152414078; its own name is not recovered) whose members
# ``BottleA`` .. ``BottleE`` are each a Struct of ``IsValid`` (Bool: that bottle is owned) and ``BottleItem`` (Enum
# whose RawValues are the 13 contents below). Member names were recovered by murmur3 of candidate names, the key rule
# of section 6, so these leaves are read by their entry hashes. Audit on copied saves (E:/OOTRemake/work/r14-tracker/
# probe6-8.py): the transferred Longshot backup has BottleA Blue Fire and BottleB Fairy valid and C-E not; the seed-8
# copy has BottleA Red Potion. (slot member, IsValid key, BottleItem key)
BOTTLE_SLOTS = (
    ("BottleA", 4087145488, 2101927798),
    ("BottleB", 1046250, 517805642),
    ("BottleC", 4131066260, 3087823016),
    ("BottleD", 3085980366, 3837899260),
    ("BottleE", 3799716717, 912136531),
)
BOTTLE_CONTENTS = {
    save_format.murmur3_32(name.encode()): label
    for name, label in (
        ("Empty", "Empty"),
        ("Fish", "Fish"),
        ("Bug", "Bug"),
        ("Fairy", "Fairy"),
        ("BlueFire", "Blue Fire"),
        ("Poe", "Poe"),
        ("BigPoe", "Big Poe"),
        ("RedPotion", "Red Potion"),
        ("GreenPotion", "Green Potion"),
        ("BluePotion", "Blue Potion"),
        ("MaxMilk", "Lon Lon Milk"),
        ("HalfMilk", "Half Milk"),
        ("Letter", "Ruto's Letter"),
    )
}
# Pouch rows of bottle contents (PouchActorInfo ``BottleItem``): their ``IsGet`` is history only ("ever had a bottle").
BOTTLE_ACTORS = (
    "Item_Bottle",
    "Item_Bottle_Milk",
    "Item_Bottle_HalfMilk",
    "Item_Bottle_Letter",
    "Item_Bottle_RedPotion",
    "Item_Bottle_GreenPotion",
    "Item_Bottle_BluePotion",
    "Item_Bottle_Fairy",
    "Item_Bottle_Fish",
    "Item_Bottle_Bug",
    "Item_Bottle_BlueFire",
    "Item_Bottle_Poe",
    "Item_Bottle_BigPoe",
)

# Songs have only ``IsGet`` in the save (no stock) [S19]; Scarecrow's Song is listed for completeness.
SONGS = (
    ("zeldas_lullaby", "Zelda's Lullaby", "Item_Melody_ZeldaLullaby"),
    ("eponas_song", "Epona's Song", "Item_Melody_EponaSong"),
    ("sarias_song", "Saria's Song", "Item_Melody_SariaSong"),
    ("suns_song", "Sun's Song", "Item_Melody_SunSong"),
    ("song_of_time", "Song of Time", "Item_Melody_TimeSong"),
    ("song_of_storms", "Song of Storms", "Item_Melody_StormSong"),
    ("minuet", "Minuet of the Forest", "Item_Melody_ForestMinuet"),
    ("bolero", "Bolero of Fire", "Item_Melody_FireBolero"),
    ("serenade", "Serenade of Water", "Item_Melody_WaterSerenade"),
    ("requiem", "Requiem of Spirit", "Item_Melody_SpiritRequiem"),
    ("nocturne", "Nocturne of Shadow", "Item_Melody_ShadowNocturne"),
    ("prelude", "Prelude of Light", "Item_Melody_LightPrelude"),
    ("scarecrows_song", "Scarecrow's Song", "Item_Melody_ScarecrowSong"),
)

# Spiritual stones and medallions: counted pouch items (stock and IsGet) [S19, boss rewards are gift steps].
REWARDS = (
    ("kokiri_emerald", "Kokiri's Emerald", "Item_Stone_Forest"),
    ("goron_ruby", "Goron's Ruby", "Item_Stone_Fire"),
    ("zora_sapphire", "Zora's Sapphire", "Item_Stone_Water"),
    ("forest_medallion", "Forest Medallion", "Item_Medal_Forest"),
    ("fire_medallion", "Fire Medallion", "Item_Medal_Fire"),
    ("water_medallion", "Water Medallion", "Item_Medal_Water"),
    ("shadow_medallion", "Shadow Medallion", "Item_Medal_Shadow"),
    ("spirit_medallion", "Spirit Medallion", "Item_Medal_Spirit"),
    ("light_medallion", "Light Medallion", "Item_Medal_Light"),
)

# Magic capacity, ``PlayerStatus.MPMax`` (an Int GameDataList entry under that name; 0 before any magic,
# plans/03-game-data.md section 12): [SL1] 0 = no meter, 240 normal, 480 double.
MAGIC_LABELS = ("Magic Meter", "Double Magic")


class _Reader:
    """Typed, None-preserving reads of the named fields above."""

    def __init__(self, save: save_format.Save | None):
        self.save = save

    def isget(self, actor: str) -> bool | None:
        return None if self.save is None else self.save.flag(f"IsGet.{actor}")

    def stock(self, actor: str) -> int | None:
        return None if self.save is None else self.save.int_value(f"PouchData.{actor}.StockNum")

    def number(self, name: str) -> int | None:
        return None if self.save is None else self.save.int_value(name)

    def flag(self, name: str | int) -> bool | None:
        return None if self.save is None else self.save.flag(name)

    def enum(self, key: int) -> int | None:
        return None if self.save is None else self.save.enum_value(key)


def _count_field(reader: _Reader, spec: str | None) -> int | None:
    if spec is None:
        return None
    kind, _, name = spec.partition(":")
    return reader.stock(name) if kind == "Stock" else reader.number(name)


def _held(stock: int | None) -> bool | None:
    return None if stock is None else stock > 0


def _ever(values: list[bool | None]) -> bool | None:
    if any(values):
        return True
    return None if any(v is None for v in values) else False


def _tier_cell(reader: _Reader, cell_id: str, group: str, tiers, count_spec: str | None) -> dict[str, Any]:
    stocks = [reader.stock(actor) for _, actor in tiers]
    known = [s is not None for s in stocks]
    tier = max((i + 1 for i, s in enumerate(stocks) if s), default=0)
    held: bool | None = tier > 0 if all(known) or tier else None
    shown = tiers[max(tier, 1) - 1]
    return {
        "id": cell_id,
        "group": group,
        "label": shown[0],
        "tier": tier if held is not None else None,
        "max_tier": len(tiers),
        "count": _count_field(reader, count_spec),
        "held": held,
        "ever": _ever([reader.isget(actor) for _, actor in tiers]),
        "icon": shown[1],
        "basis": "stock",
    }


def _single(reader: _Reader, cell_id: str, group: str, label: str, actor: str, counted: bool) -> dict[str, Any]:
    stock = reader.stock(actor)
    held = _held(stock)
    return {
        "id": cell_id,
        "group": group,
        "label": label,
        "tier": None if held is None else int(held),
        "max_tier": 1,
        "count": stock if counted else None,
        "held": held,
        "ever": reader.isget(actor),
        "icon": actor,
        "basis": "stock",
    }


def _ever_cell(reader: _Reader, cell_id: str, group: str, label: str, actor: str) -> dict[str, Any]:
    ever = reader.isget(actor)
    return {
        "id": cell_id,
        "group": group,
        "label": label,
        "tier": None if ever is None else int(ever),
        "max_tier": 1,
        "count": None,
        "held": ever,
        "ever": ever,
        "icon": actor,
        "basis": "ever_acquired",
    }


def _magic(reader: _Reader) -> dict[str, Any]:
    capacity = reader.number("PlayerStatus.MPMax")
    tier = None if capacity is None else 0 if capacity <= 0 else 2 if capacity >= 480 else 1
    return {
        "id": "magic",
        "group": "upgrades",
        "label": MAGIC_LABELS[max(tier or 1, 1) - 1],
        "tier": tier,
        "max_tier": 2,
        "count": capacity,
        "held": None if tier is None else tier > 0,
        "ever": _ever([reader.isget("Item_FairyBless_MP"), reader.isget("Item_FairyBless_MPDouble")]),
        "icon": "Item_FairyBless_MPDouble" if tier == 2 else "Item_FairyBless_MP",
        "basis": "capacity",
    }


def _bottles(reader: _Reader) -> dict[str, Any]:
    """``count``: owned bottles (``IsValid`` set); ``contents``: what each owned bottle holds, in slot order."""
    slots = [(slot, reader.flag(valid), reader.enum(content)) for slot, valid, content in BOTTLE_SLOTS]
    contents = None
    if all(valid is not None for _, valid, _ in slots):
        # A content value outside the Enum's 13 choices (another build) shows as None, not as a guess.
        contents = [{"slot": slot, "content": BOTTLE_CONTENTS.get(value)} for slot, valid, value in slots if valid]
    count = None if contents is None else len(contents)
    return {
        "id": "bottles",
        "group": "items",
        "label": "Bottles",
        "tier": count,
        "max_tier": len(BOTTLE_SLOTS),
        "count": count,
        "held": None if count is None else count > 0,
        "ever": _ever([reader.isget(actor) for actor in BOTTLE_ACTORS]),
        "icon": "Item_Bottle",
        "basis": "slots",
        "contents": contents,
    }


def items(save: save_format.Save | None) -> list[dict[str, Any]]:
    reader = _Reader(save)
    cells = [_tier_cell(reader, *spec) for spec in TIERS]
    cells.insert(3, _magic(reader))
    cells.append(_bottles(reader))
    cells.extend(_single(reader, *spec) for spec in SINGLES)
    return cells


def songs(save: save_format.Save | None) -> list[dict[str, Any]]:
    reader = _Reader(save)
    return [_ever_cell(reader, cell_id, "songs", label, actor) for cell_id, label, actor in SONGS]


def rewards(save: save_format.Save | None) -> list[dict[str, Any]]:
    reader = _Reader(save)
    return [_single(reader, cell_id, "rewards", label, actor, False) for cell_id, label, actor in REWARDS]


def hearts(save: save_format.Save | None) -> dict[str, Any]:
    """``containers``: whole hearts of the meter, ``PlayerStatus.MaxLife`` / 4 ([AUDIT], [INFERENCE] on the unit:
    early copied saves hold 12 for the starting three hearts, so MaxLife counts quarter hearts). ``pieces``:
    ``PouchData.Obj_Heart_Piece.StockNum`` [SL1] as saved (pieces toward the next heart or all found: not
    established, so it is not turned into hearts)."""
    reader = _Reader(save)
    life = reader.number("PlayerStatus.MaxLife")
    return {
        "containers": None if life is None else life // 4,
        "max_life": life,
        "pieces": reader.stock("Obj_Heart_Piece"),
    }


def dungeons(seed: Seed, save: save_format.Save | None) -> list[dict[str, Any]]:
    """Keys first (D38): per dungeon, small keys ``held`` (remaining, ``SmallKeyNum``), ``found`` (acquired total,
    ``SmallKeyTotalNum``) and the seed's ``total`` [S44]; boss key, map and compass flags [S44] [SL58]. ``has_*`` say
    whether the seed holds that dungeon item at all."""
    reader = _Reader(save)
    out = []
    for dungeon, struct in DUNGEON_INFO.items():
        prefix = f"DungeonInfo.{struct}."
        out.append(
            {
                "name": DUNGEON_LABELS[dungeon],
                "id": struct,
                "dungeon": dungeon,
                "small_keys": {
                    "held": reader.number(prefix + "SmallKeyNum"),
                    "found": reader.number(prefix + "SmallKeyTotalNum"),
                    "total": seed.small_keys.get(dungeon, 0),
                    "first_found": reader.flag(prefix + "IsGetSmallKeyOnce"),
                },
                "boss_key": reader.flag(prefix + "IsGetBossKey"),
                "map": reader.flag(prefix + "IsGetMap"),
                "compass": reader.flag(prefix + "IsGetCompass"),
                "has_boss_key": seed.boss_keys.get(dungeon, 0) > 0,
                "has_map": seed.maps.get(dungeon, 0) > 0,
                "has_compass": seed.compasses.get(dungeon, 0) > 0,
            }
        )
    return out


def collected(check: Check, save: save_format.Save | None) -> tuple[bool | None, str | None]:
    """(collected, reason when unknown) for one check; see :class:`clawshot.tracker.seeds.Check`."""
    if save is None:
        return None, "no save read"
    if check.method == NAMED_BOOL:
        values = [save.flag(name) for name in check.flags]
        if any(values):
            return True, None
        if values and all(v is not None for v in values):
            return False, None
        if check.kind == "gift" and any(v is not None for v in values):
            return False, None  # an added flag exists under exactly one step name (``patch.gifts.GiftChange.flag``)
        return None, "the save has no record field for this check (another seed or game version?)"
    if check.method == PLACEMENT_HASH:
        if save.save_type is None:
            return None, "the save has no placement list"
        if any(save.is_set(h) for h in check.hashes):
            return True, None
        return None, "not seen collected; a replaced pickup's saved state is not certified"
    return None, check.reason or "no audited save record"


def _identity(seed: Seed, save: save_format.Save | None) -> dict[str, Any]:
    """Whether the save could come from this seed, from the only seed-specific save data Clawshot writes: the saved
    Bools its gift patch adds to GameDataList [S19: kept by the game; the save's Bool section is exactly the
    GameDataList's saved Bools]. Clawshot saves carry no seed number, so a match is consistency, not proof."""
    expected = len(seed.added_flags)
    if save is None:
        return {"status": "unknown", "detail": "no save read", "expected_added": expected, "save_added": None}
    bools = len(save.entries.get(save_format.BOOL, {}))
    added = bools - NATIVE_SAVED_BOOLS
    if added < 0:
        return {
            "status": "unverifiable",
            "detail": f"the save holds {bools} saved Bools, fewer than build e0f3ccfa's {NATIVE_SAVED_BOOLS}",
            "expected_added": expected,
            "save_added": None,
        }
    missing = [names[0] for names in seed.added_flags if all(save.flag(name) is None for name in names)]
    if added != expected or missing:
        detail = (
            f"this seed adds {expected} saved flag(s); the save's game added {added}"
            + (f" and lacks {', '.join(missing)}" if missing else "")
            + ": the save is from another seed, or was last saved without this seed loaded"
        )
        return {"status": "mismatch", "detail": detail, "expected_added": expected, "save_added": added}
    if expected == 0:
        return {
            "status": "unverifiable",
            "detail": "neither this seed nor the save adds saved flags; saves carry no seed identity",
            "expected_added": 0,
            "save_added": 0,
        }
    return {
        "status": "consistent",
        "detail": f"the save holds this seed's {expected} added flag(s) (consistent, not proof)",
        "expected_added": expected,
        "save_added": added,
    }


def _check_entry(check: Check, save: save_format.Save | None, show_locations: bool) -> dict[str, Any]:
    state, reason = collected(check, save)
    entry: dict[str, Any] = {
        "id": check.location,
        "label": check.label,
        "where": check.where,
        "kind": check.kind,
        "dungeon": check.dungeon,
        "collected": state,
        "basis": check.method if state is not None else None,
    }
    if state is None:
        entry["reason"] = reason
    if show_locations or state is True:
        entry["item"] = check.item
        entry["item_label"] = check.item_label
    return entry


def areas(seed: Seed, save: save_format.Save | None, *, show_locations: bool = False) -> list[dict[str, Any]]:
    """Checks grouped by area in the seed's world order. Without ``show_locations`` an entry names its item only once
    collected; ``collected`` is ``None`` (counted under ``unknown``) wherever the save cannot say."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for check in seed.checks:
        grouped.setdefault(check.area, []).append(_check_entry(check, save, show_locations))
    return [
        {
            "name": name,
            "collected": sum(c["collected"] is True for c in checks),
            "total": len(checks),
            "unknown": sum(c["collected"] is None for c in checks),
            "checks": checks,
        }
        for name, checks in grouped.items()
    ]


def build_state(seed: Seed, save: save_format.Save | None, *, show_locations: bool = False) -> dict[str, Any]:
    """The tracker's whole view, JSON-able. ``save`` may be ``None`` (seed totals with every save value unknown)."""
    reader = _Reader(save)
    warnings = list(seed.warnings)
    identity = _identity(seed, save)
    if identity["status"] == "mismatch":
        warnings.append("This save may not belong to this seed: " + identity["detail"] + ".")
    elif identity["status"] == "unverifiable" and save is not None:
        warnings.append("Cannot confirm this save belongs to this seed: " + identity["detail"] + ".")
    chests = [c for c in seed.checks if c.kind == "chest" and c.method == NAMED_BOOL]
    if save is not None and chests and all(all(save.flag(f) is None for f in c.flags) for c in chests):
        warnings.append("The save has none of this seed's chest records: another game version or not a game save.")
    return {
        "seed": dict(seed.metadata),
        "identity": identity,
        "dungeons": dungeons(seed, save),
        "items": items(save),
        "songs": songs(save),
        "rewards": rewards(save),
        "hearts": hearts(save),
        "tokens": reader.stock("Item_Token_Gold"),
        "areas": areas(seed, save, show_locations=show_locations),
        "show_locations": show_locations,
        "warnings": warnings,
    }
