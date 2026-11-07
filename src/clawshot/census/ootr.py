"""Link census locations to OoT Randomizer's location names.

OoT Randomizer (MIT, https://github.com/OoTRandomizer/OoT-Randomizer) lists its checks in ``LocationList.py``.
:func:`read_location_list` reads that file's ``location_table`` as data (``ast.literal_eval``, nothing is
executed), without Master Quest. The file itself is not in this repository; the tool that writes the definitions
takes its path.

A remake location gets an OoT Randomizer name when it is the same check: same area, same kind and, within that
area and kind, the only one of its item family on both sides (:func:`match`). Where the remake changed an item
(many N64 hearts and ammo are rupees here), the last unmatched pair of an area and kind is linked only when both
sides had the same count. Everything else stays unlinked for a person to decide.
"""

import ast
import math
import re
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from clawshot.census.scan import (
    CHEST,
    FREESTANDING,
    GOLD_SKULLTULA,
    HEART_CONTAINER,
    SCRUB,
    SHOP_SLOT,
    TREASURE_GAME_BOX,
    TREASURE_GAME_REWARD,
    Location,
)

# The LocationList.py the committed definitions were matched against (branch Dev).
OOTR_COMMIT = "526b4c8d81b7c4023ef4573ffbaf39344e270d5b"

# OoT Randomizer name prefix -> Banc area (plans/03-game-data.md, section 9). Longest prefix first.
AREA_PREFIXES: tuple[tuple[str, str], ...] = (
    ("Gerudo Training Ground ", "GerudoTrainingGround"),
    ("Bottom of the Well ", "BottomOfTheWell"),
    ("Jabu Jabus Belly ", "InsideJabuJabuBelly"),
    ("Dodongos Cavern ", "DodongoCavern"),
    ("Shadow Temple ", "ShadowTemple"),
    ("Spirit Temple ", "SpiritTemple"),
    ("Forest Temple ", "ForestTemple"),
    ("Water Temple ", "WaterTemple"),
    ("Ganons Castle ", "InsideGanonCastle"),
    ("Ganons Tower ", "InsideGanonCastle"),
    ("Fire Temple ", "FireTemple"),
    ("Ice Cavern ", "IceCavern"),
    ("Deku Tree ", "InsideTheDekuTree"),
    ("Wasteland ", "HountedWasteland"),
    ("Graveyard ", "Graveyard"),
    ("Colossus ", "DesertColossus"),
    ("Hideout ", "GerudoFortress"),
    ("Market ", "Market"),
    ("ToT ", "Market"),
    ("OGC ", "GanonCastle"),
    ("Kak ", "KakarikoVillage"),
    ("LLR ", "HyruleField"),
    ("SFM ", "SacredForestMeadow"),
    ("DMT ", "DeathMountainTrail"),
    ("DMC ", "DeathMountainCrater"),
    ("KF ", "KokiriForest"),
    ("LW ", "LostWood"),
    ("HF ", "HyruleField"),
    ("LH ", "HyruleField"),
    ("HC ", "HyruleCastle"),
    ("GC ", "GoronCity"),
    ("ZR ", "ZoraRiver"),
    ("ZD ", "ZoraDomain"),
    ("ZF ", "ZoraFountain"),
    ("GV ", "GerudoValley"),
    ("GF ", "GerudoFortress"),
)

# Checks the remake moved to another Banc area (plans/03-game-data.md, section 9: both chests are in the
# DesertColossus files, not the Spirit Temple's).
MOVED: dict[str, str] = {
    "Spirit Temple Silver Gauntlets Chest": "DesertColossus",
    "Spirit Temple Mirror Shield Chest": "DesertColossus",
}

# OoT Randomizer location type -> census kind. Treasure Chest Game chests are told apart by name.
TYPE_KINDS = {
    "Chest": CHEST,
    "GS Token": GOLD_SKULLTULA,
    "Collectable": FREESTANDING,
    "BossHeart": HEART_CONTAINER,
    "Scrub": SCRUB,
    "GrottoScrub": SCRUB,
    "Shop": SHOP_SLOT,
    "MaskShop": SHOP_SLOT,
}
TREASURE_GAME_PREFIX = "Market Treasure Chest Game "

# Remake actor name -> item family, the common ground with OoT Randomizer's item names (:func:`ootr_family`).
_REMAKE_FAMILY = {
    "Item_Arrow_Ice": "Ice Arrows",
    "Item_BombBag_Small": "Bomb Bag",
    "Item_Boomerang": "Boomerang",
    "Item_Dungeon_BossKey": "Boss Key",
    "Item_Dungeon_Compass": "Compass",
    "Item_Dungeon_Map": "Map",
    "Item_Dungeon_SmallKey": "Small Key",
    "Obj_Dungeon_SmallKey": "Small Key",
    "Obj_MiniGame_SmallKey": "Small Key",
    "Item_Gauntlet_Silver": "Progressive Strength Upgrade",
    "Item_Gauntlet_Gold": "Progressive Strength Upgrade",
    "Item_GlassTruth": "Lens of Truth",
    "Item_Hammer": "Megaton Hammer",
    "Item_HeavyBoot": "Iron Boots",
    "Item_HoverBoot": "Hover Boots",
    "Item_Hookshot": "Progressive Hookshot",
    "Item_Longshot": "Progressive Hookshot",
    "Item_Range_Bow": "Bow",
    "Item_Range_SlingShot": "Slingshot",
    "Item_Shield_Mirror": "Mirror Shield",
    "Item_Sword_Kokiri": "Kokiri Sword",
    "Item_NutBag_Medium": "Deku Nut Capacity",
    "Item_StickBag_Medium": "Deku Stick Capacity",
    "Obj_Heart_Piece": "Piece of Heart",
    "Obj_GerudoValley_Heart_Piece": "Piece of Heart",
    "Obj_Heart_Container": "Heart Container",
    "Obj_Heart": "Recovery Heart",
    "Shop_Heart": "Recovery Heart",
    "Obj_Token_Gold": "Gold Skulltula Token",
    "Obj_Rupee_Green": "Rupee (1)",
    "TBox_Rupee_Green": "Rupee (1)",
    "TBox_Rupee_Blue": "Rupees (5)",
    "TBox_Rupee_Red": "Rupees (20)",
    "TBox_Rupee_Purple": "Rupees (50)",
    "Item_BombBundle_Small": "Bombs",
    "Item_BombchuBundle_Small": "Bombchus",
    "Item_DekuStickBundle_Small": "Deku Sticks",
    "TBox_DekuNutBundle": "Deku Nuts",
    "TBox_Shield_Deku": "Deku Shield",
    "TBox_Shield_Hylian": "Hylian Shield",
    "Item_Bottle_GreenPotion": "Green Potion",
    "Item_Bottle_RedPotion": "Red Potion",
    "Tbox_MagicJar_Large": "Magic Jar",
    "Item_ScrubBusinessSeed": "Scrub Business Seed",  # remake-only
}
_REMAKE_FAMILY_PREFIX = (
    ("Obj_Dungeon_SmallKey_", "Small Key"),
    ("TBox_ArrowBundle_", "Arrows"),
    ("Shop_ArrowBundle_", "Arrows"),
    ("Shop_BombBundle_", "Bombs"),
    ("Shop_BombchuBundle_", "Bombchus"),
    ("Shop_DekuNutBundle_", "Deku Nuts"),
    ("Shop_DekuSeedBundle_", "Deku Seeds"),
    ("Shop_DekuStick", "Deku Sticks"),
)


def remake_family(actor: str) -> str:
    """The item family of a remake actor name; the actor name itself when it has no OoT Randomizer counterpart."""
    if actor in _REMAKE_FAMILY:
        return _REMAKE_FAMILY[actor]
    for prefix, family in _REMAKE_FAMILY_PREFIX:
        if actor.startswith(prefix):
            return family
    return actor


_OOTR_RENAMES = {"Deku Nut": "Deku Nuts", "Deku Stick": "Deku Sticks", "Bombchu": "Bombchus", "Heart": "Recovery Heart"}


def ootr_family(item: str) -> str:
    """The item family of an OoT Randomizer item name: no dungeon, count, price or minigame tag."""
    item = item.replace(" (Treasure Chest Game)", "").replace(" (Out of Logic)", "")
    item = re.sub(r"^Buy ", "", item)
    item = re.sub(r" for \d+ Rupees$", "", item)
    m = re.fullmatch(r"(Map|Compass|Small Key|Boss Key) \(.+\)", item)
    if m:
        return m.group(1)
    m = re.fullmatch(r"(Bombs|Bombchus?|Arrows|Deku Nuts?|Deku Seeds|Deku Sticks?) \(\d+\)", item)
    if m:
        item = m.group(1)
    return _OOTR_RENAMES.get(item, item)


@dataclass(frozen=True)
class OotrLocation:
    name: str
    type: str
    scene: int | None
    vanilla_item: str | None
    categories: tuple[str, ...]

    @property
    def area(self) -> str | None:
        if self.name in MOVED:
            return MOVED[self.name]
        for prefix, area in AREA_PREFIXES:
            if self.name.startswith(prefix):
                return area
        return None

    @property
    def kind(self) -> str | None:
        if self.type == "Chest" and self.name == TREASURE_GAME_REWARD_NAME:
            return TREASURE_GAME_REWARD
        if self.type == "Chest" and self.name.startswith(TREASURE_GAME_PREFIX):
            return TREASURE_GAME_BOX
        return TYPE_KINDS.get(self.type)


def _table_node(tree: ast.Module) -> ast.expr:
    for node in tree.body:
        target = node.target if isinstance(node, ast.AnnAssign) else None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == "location_table":
            call = node.value
            if isinstance(call, ast.Call) and len(call.args) == 1:
                return call.args[0]
    raise ValueError("no `location_table = OrderedDict([...])` in the file")


def _literal(node: ast.expr):
    try:
        return ast.literal_eval(node)
    except ValueError:  # an address computed by a call (shop_address(...)): not needed here
        return None


def read_location_list(path: str | Path) -> list[OotrLocation]:
    """OoT Randomizer's locations without Master Quest, in the file's order."""
    table = _table_node(ast.parse(Path(path).read_text(encoding="utf-8")))
    if not isinstance(table, ast.List):
        raise ValueError("location_table is not built from a list literal")
    out = []
    for entry in table.elts:
        name = ast.literal_eval(entry.elts[0])
        fields = entry.elts[1].elts
        loc_type, scene, item, cats = (_literal(fields[i]) for i in (0, 1, 4, 5))
        cats = () if cats is None else (cats,) if isinstance(cats, str) else tuple(cats)
        if "Master Quest" in cats and "Vanilla Dungeons" not in cats:
            continue
        out.append(OotrLocation(name, loc_type, scene, item, cats))
    return out


# --------------------------------------------------------------------------------------------------------------
# Matching

ITEM = "item"  # the only one of its item family in its area and kind, on both sides
RESIDUAL = "residual"  # the last pair left in an area and kind that had equal counts on both sides
SHOP = "shop slot"  # slot n of a shop is OoT Randomizer's "Item n+1" of that shop
TREASURE_GAME = "treasure game room"  # the Treasure Chest Game's rooms, counted from the reward chest back

# The Treasure Chest Game: two boxes per room at one x coordinate, the key in one (OoT Randomizer's "Top"), five
# rooms, then two reward boxes at one spot (a Heart Piece, and a red rupee once the Heart Piece is taken).
TREASURE_GAME_REWARD_NAME = "Market Treasure Chest Game Reward"
TREASURE_GAME_KEY = "Obj_MiniGame_SmallKey"
TREASURE_GAME_ROOM_WIDTH = 1.0
TREASURE_GAME_ROOMS = 5

# A shop is the shop actors of an area within this distance of each other (shelves are about 3 units across;
# the nearest two shops, in the Market, are 6 apart).
SHOP_LINK_DISTANCE = 3.0
# Shop names in OoT Randomizer, per area; where an area has several shops, the actor that tells them apart.
SHOPS: dict[str, tuple[tuple[str, str], ...]] = {
    "KokiriForest": (("", "KF Shop"),),
    "GoronCity": (("", "GC Shop"),),
    "ZoraDomain": (("", "ZD Shop"),),
    "Market": (
        ("Shop_BombchuBundle_", "Market Bombchu Shop"),
        ("Shop_Mask_", "Market Mask Shop"),
        ("Shop_Bottle_", "Market Potion Shop"),
        ("", "Market Bazaar"),
    ),
    "KakarikoVillage": (("Shop_Bottle_", "Kak Potion Shop"), ("", "Kak Bazaar")),
}
COPY_DISTANCE = 0.5


@dataclass(frozen=True)
class Match:
    name: str
    basis: str


def spots(locations: Iterable[Location]) -> list[list[Location]]:
    """Locations grouped into spots: one actor and its copies under another Hash in other files (same area,
    kind, actor and item, the same position). Shop slots are left to :func:`shops`."""
    groups: list[list[Location]] = []
    for loc in locations:
        if loc.kind == SHOP_SLOT:
            continue
        for group in groups:
            first = group[0]
            if (
                (first.area, first.kind, first.actor, first.vanilla_item)
                == (loc.area, loc.kind, loc.actor, loc.vanilla_item)
                and math.dist(first.position, loc.position) < COPY_DISTANCE
                and not set(loc.files) & {f for g in group for f in g.files}
            ):
                group.append(loc)
                break
        else:
            groups.append([loc])
    return groups


def shops(locations: Iterable[Location]) -> dict[str, list[Location]]:
    """Shop slot locations by OoT Randomizer shop name. Raises ValueError for a shop it cannot name."""
    by_area: dict[str, list[Location]] = defaultdict(list)
    for loc in locations:
        if loc.kind == SHOP_SLOT:
            by_area[loc.area].append(loc)
    out: dict[str, list[Location]] = {}
    for area, locs in by_area.items():
        clusters: list[list[Location]] = []
        for loc in locs:
            near = [c for c in clusters if any(math.dist(loc.position, o.position) < SHOP_LINK_DISTANCE for o in c)]
            merged = [loc] + [o for c in near for o in c]
            clusters = [c for c in clusters if c not in near] + [merged]
        for cluster in clusters:
            actors = {loc.actor for loc in cluster}
            for marker, name in SHOPS.get(area, ()):
                if not marker or any(a.startswith(marker) for a in actors):
                    if name in out:
                        raise ValueError(f"two shops in {area} named {name}")
                    out[name] = sorted(cluster, key=lambda loc: loc.id)
                    break
            else:
                raise ValueError(f"no OoT Randomizer shop for the shop in {area} with {sorted(actors)}")
    return out


def treasure_game(locations: Iterable[Location]) -> dict[int, str]:
    """OoT Randomizer names of the Treasure Chest Game's boxes, by Hash; empty when the layout is not the expected
    five rooms of two boxes and the reward spot.

    The rooms are numbered from the farthest from the reward boxes (room 1) to the nearest (room 5): the remake's
    rupee boxes grow in value that way and the box at the nearest room plays ``..._OpenLastHitTreasureBox``. Of the
    two reward boxes, the Heart Piece is OoT Randomizer's reward; the red-rupee box has no counterpart.
    """
    boxes = [loc for loc in locations if loc.kind == TREASURE_GAME_BOX]
    rewards = [loc for loc in locations if loc.kind == TREASURE_GAME_REWARD]
    heart = [loc for loc in rewards if remake_family(loc.vanilla_item) == "Piece of Heart"]
    if not rewards or len(heart) != 1:
        return {}
    rooms: list[list[Location]] = []
    for loc in sorted(boxes, key=lambda b: b.position[0]):
        if rooms and abs(rooms[-1][0].position[0] - loc.position[0]) < TREASURE_GAME_ROOM_WIDTH:
            rooms[-1].append(loc)
        else:
            rooms.append([loc])
    keys = [[b for b in room if b.vanilla_item == TREASURE_GAME_KEY] for room in rooms]
    if len(rooms) != TREASURE_GAME_ROOMS or any(len(r) != 2 or len(k) != 1 for r, k in zip(rooms, keys, strict=True)):
        return {}
    rooms.sort(key=lambda room: -math.dist(room[0].position, heart[0].position))
    out = {heart[0].id: TREASURE_GAME_REWARD_NAME}
    for n, room in enumerate(rooms, start=1):
        for box in room:
            side = "Top" if box.vanilla_item == TREASURE_GAME_KEY else "Bottom"
            out[box.id] = f"{TREASURE_GAME_PREFIX}Room {n} {side}"
    return out


def match(locations: Sequence[Location], ootr: Sequence[OotrLocation]) -> dict[int, Match]:
    """OoT Randomizer names for the census locations it is sure of, by Hash.

    One-time checks are matched one spot to one OoT Randomizer location; every copy in a spot gets the name. Shop
    slots are matched by slot number within the same shop, the Treasure Chest Game by room (:func:`treasure_game`).
    Gold Skulltulas are not matched: the remake moved them (plans/03-game-data.md, section 9).
    """
    result: dict[int, Match] = {}
    names = {o.name for o in ootr}

    for shop, locs in shops(locations).items():
        for loc in locs:
            name = f"{shop} Item {loc.shop_slot + 1}"
            if name in names:
                result[loc.id] = Match(name, SHOP)
    for actor_hash, name in treasure_game(locations).items():
        if name in names:
            result[actor_hash] = Match(name, TREASURE_GAME)

    remake: dict[tuple[str, str], list[list[Location]]] = defaultdict(list)
    for spot in spots(locations):
        remake[(spot[0].area, spot[0].kind)].append(spot)
    theirs: dict[tuple[str, str], list[OotrLocation]] = defaultdict(list)
    for o in ootr:
        if (
            o.kind not in (None, SHOP_SLOT, GOLD_SKULLTULA, TREASURE_GAME_BOX, TREASURE_GAME_REWARD)
            and o.area is not None
        ):
            theirs[(o.area, o.kind)].append(o)

    for key, ours in remake.items():
        others = theirs.get(key, [])
        matched_spots: set[int] = set()
        matched_names: set[str] = set()
        by_family: dict[str, list[int]] = defaultdict(list)
        for i, spot in enumerate(ours):
            by_family[remake_family(spot[0].vanilla_item)].append(i)
        their_family: dict[str, list[OotrLocation]] = defaultdict(list)
        for o in others:
            their_family[ootr_family(o.vanilla_item or "")].append(o)
        for family, idx in by_family.items():
            candidates = their_family.get(family, [])
            if len(idx) == 1 and len(candidates) == 1:
                matched_spots.add(idx[0])
                matched_names.add(candidates[0].name)
                for loc in ours[idx[0]]:
                    result[loc.id] = Match(candidates[0].name, ITEM)
        left = [i for i in range(len(ours)) if i not in matched_spots]
        left_theirs = [o for o in others if o.name not in matched_names]
        if len(ours) == len(others) and len(left) == 1 and len(left_theirs) == 1:
            for loc in ours[left[0]]:
                result[loc.id] = Match(left_theirs[0].name, RESIDUAL)
    return result
