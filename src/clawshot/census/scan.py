"""Find every placement check in the player's dump.

A check is an actor in ``Banc/<Area>/*.bcett.byml.zs`` whose ``Gyaml`` names a kind of check (:func:`kind_of`). The
same actor appears in several files (child and adult, ``Alternative`` states) under the same ``Hash``; the census
merges those into one :class:`Location`, identified by that ``Hash``. Actors that stand at the same spot under a
different ``Hash`` (a shop slot in the child and the adult file, a few chests and scrubs) stay separate locations:
each has its own save flag.

Left out by decision (``plans/decisions.md``): trap chests (D10), cows (D11), ``DreamWorld`` (D12), and the chest
pedestals, which hold nothing. Event gifts need event flows and come later.
"""

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from clawshot.formats import byml, zsdic

BANC_GLOB = "Banc/*/*.bcett.byml.zs"
GAME_DATA_LIST = "GameData/GameDataList.Product.110.byml.zs"
EXCLUDED_AREAS = frozenset({"DreamWorld"})

CHEST = "chest"
TREASURE_GAME_BOX = "treasure_game_box"
TREASURE_GAME_REWARD = "treasure_game_reward"
GOLD_SKULLTULA = "gold_skulltula"
FREESTANDING = "freestanding"
HEART_CONTAINER = "heart_container"
SCRUB = "scrub"
SHOP_SLOT = "shop_slot"
KINDS = (
    CHEST,
    TREASURE_GAME_BOX,
    TREASURE_GAME_REWARD,
    GOLD_SKULLTULA,
    FREESTANDING,
    HEART_CONTAINER,
    SCRUB,
    SHOP_SLOT,
)

# The Treasure Chest Game (Market): ten boxes in five rooms (``_A_01``), then two reward boxes at one spot
# (``_A_02``: the Heart Piece, and a red rupee, presumably the prize once the Heart Piece is taken). Only the reward
# is shuffled (D17), so its boxes are a kind of their own. Every box also names the model shown inside it
# (``Dynamic.DropViewActor``), which a changed item may need changed too.
TREASURE_GAME_ACTOR_PREFIX = "Obj_HrlCity_Shop_TBox_"
TREASURE_GAME_REWARD_ACTOR = "Obj_HrlCity_Shop_TBox_A_02"

# A chest without ``Drop__DropActor`` gives its blackboard's ``DefaultDropActorName``, the same for every chest kind
# (plans/03-game-data.md, section 2; inferred from the actor packs, not seen in game).
DEFAULT_CHEST_DROP = "Obj_Rupee_Green"
# What a Gold Skulltula leaves when killed: the token's pickup actor (a ``PouchActorInfo`` row, as are chest drops).
GOLD_SKULLTULA_TOKEN = "Obj_Token_Gold"
FREESTANDING_ACTORS = frozenset({"Obj_Heart_Piece", "Obj_GerudoValley_Heart_Piece", "Obj_Dungeon_SmallKey"})
SMALL_KEY_PREFIX = "Obj_Dungeon_SmallKey_"  # Gerudo Fortress keys: Obj_Dungeon_SmallKey_GerudoFortress_01..04

CHILD = "child"
ADULT = "adult"
BOTH = "both"

# Two copies of one actor in different files may differ by float noise (two Gold Skulltulas differ by < 0.003).
POSITION_TOLERANCE = 0.01


class CensusError(ValueError):
    pass


@dataclass(frozen=True)
class Location:
    id: int  # the actor's Hash
    kind: str
    area: str  # Banc folder
    room: int | None  # Dynamic.DefaultDungeonRoomIndex; only dungeon actors carry one
    files: tuple[str, ...]  # romfs paths of every placement file holding this Hash, sorted
    ages: str  # child, adult or both (a file without an age in its name serves both)
    position: tuple[float, float, float]  # Translate, from the first of ``files``
    actor: str  # Gyaml
    vanilla_item: str  # actor name; "" when the placement does not name it (scrubs whose item is in their event)
    event: str | None  # Dynamic.GetEventName, an override of the default open event
    has_save_flag: bool  # GameDataList has a Bool64bitKey flag keyed by this Hash
    shop_slot: int | None = None  # Dynamic.ShopItemIndex for shop slots (absent in the data means 0)


def kind_of(gyaml: str) -> str | None:
    """The kind of check an actor is, or None when it is none (including trap chests and pedestals)."""
    if gyaml.startswith("Obj_TBox_"):  # pedestals are Obj_TBoxPedestal_*, no underscore after TBox
        return None if gyaml.startswith("Obj_TBox_A_04") else CHEST
    if gyaml.startswith(TREASURE_GAME_ACTOR_PREFIX):
        return TREASURE_GAME_REWARD if gyaml == TREASURE_GAME_REWARD_ACTOR else TREASURE_GAME_BOX
    if gyaml == "Enemy_Skulltula_Gold":
        return GOLD_SKULLTULA
    if gyaml in FREESTANDING_ACTORS or gyaml.startswith(SMALL_KEY_PREFIX):
        return FREESTANDING
    if gyaml == "Obj_Heart_Container":
        return HEART_CONTAINER
    if gyaml == "Enemy_Scrub_Business":
        return SCRUB
    if gyaml.startswith("Shop_") and not gyaml.startswith("Shop_Board_"):
        return SHOP_SLOT
    return None


def vanilla_item(kind: str, actor: Mapping) -> str:
    dynamic = actor.get("Dynamic") or {}
    if kind in (CHEST, TREASURE_GAME_BOX, TREASURE_GAME_REWARD):
        return str(dynamic.get("Drop__DropActor", DEFAULT_CHEST_DROP))
    if kind == GOLD_SKULLTULA:
        return GOLD_SKULLTULA_TOKEN
    if kind == SCRUB:
        # Up to three offers (ShopItemActorName0..2); the first is the scrub's item. Some scrubs name none.
        return str(dynamic.get("ScrubBusiness_ShopItemActorName0", ""))
    return str(actor["Gyaml"])  # freestanding items, heart containers and shop slots are the item's own actor


def file_age(path: str) -> str:
    stem = PurePosixPath(path).name
    if "_Child_" in stem:
        return CHILD
    if "_Adult_" in stem:
        return ADULT
    return BOTH


def _ages(files: Iterable[str]) -> str:
    found = {file_age(f) for f in files}
    if BOTH in found or found == {CHILD, ADULT}:
        return BOTH
    return found.pop()


def _area(path: str) -> str:
    parts = PurePosixPath(path).parts
    if len(parts) != 3 or parts[0] != "Banc":
        raise CensusError(f"not a placement file path: {path}")
    return parts[1]


def _close(a: tuple[float, ...], b: tuple[float, ...]) -> bool:
    return all(math.isclose(x, y, abs_tol=POSITION_TOLERANCE) for x, y in zip(a, b, strict=True))


def scan_trees(banc: Mapping[str, object], flags: Iterable[int]) -> list[Location]:
    """The census over parsed placement files (romfs path -> BYML tree) and the ``Bool64bitKey`` flag keys.

    Raises :class:`CensusError` when one ``Hash`` is placed as different actors, with different parameters, at
    different positions or in two areas: the merge would hide a difference.
    """
    flag_set = {int(f) for f in flags}
    copies: dict[int, list[tuple[str, Mapping]]] = {}
    for path in sorted(banc):
        if _area(path) in EXCLUDED_AREAS:
            continue
        tree = banc[path]
        for actor in tree.get("Actors", []) if isinstance(tree, Mapping) else []:
            if kind_of(actor["Gyaml"]) is not None:
                copies.setdefault(int(actor["Hash"]), []).append((path, actor))

    locations = []
    for actor_hash, placed in copies.items():
        path, first = placed[0]
        kind = kind_of(first["Gyaml"])
        position = tuple(float(x) for x in first["Translate"])
        dynamic = first.get("Dynamic") or {}
        for other_path, other in placed[1:]:
            if _area(other_path) != _area(path):
                raise CensusError(f"Hash {actor_hash} is in two areas: {path}, {other_path}")
            if other["Gyaml"] != first["Gyaml"] or not byml.same(other.get("Dynamic") or {}, dynamic):
                raise CensusError(
                    f"Hash {actor_hash} differs between {path} and {other_path}: "
                    f"{first['Gyaml']} {dict(dynamic)} vs {other['Gyaml']} {dict(other.get('Dynamic') or {})}"
                )
            if not _close(position, tuple(float(x) for x in other["Translate"])):
                raise CensusError(f"Hash {actor_hash} moves between {path} and {other_path}")
        files = tuple(p for p, _ in placed)
        room = dynamic.get("DefaultDungeonRoomIndex")
        event = dynamic.get("GetEventName")
        slot = int(dynamic.get("ShopItemIndex", 0)) if kind == SHOP_SLOT else None
        locations.append(
            Location(
                id=actor_hash,
                kind=kind,
                area=_area(path),
                room=None if room is None else int(room),
                files=files,
                ages=_ages(files),
                position=position,
                actor=str(first["Gyaml"]),
                vanilla_item=vanilla_item(kind, first),
                event=None if event is None else str(event),
                has_save_flag=actor_hash in flag_set,
                shop_slot=slot,
            )
        )
    return sorted(locations, key=sort_key)


def sort_key(location: Location) -> tuple:
    """Area, kind (in :data:`KINDS` order), room, shop slot, files, then Hash: a stable order for listings and the
    definitions file."""
    room = -1 if location.room is None else location.room
    slot = -1 if location.shop_slot is None else location.shop_slot
    return (location.area, KINDS.index(location.kind), room, slot, location.files, location.id)


def save_flags(game_data_list: object) -> set[int]:
    """The ``Bool64bitKey`` keys of a parsed ``GameDataList``."""
    return {int(entry["Hash"]) for entry in game_data_list["Data"]["Bool64bitKey"]}


def read_romfs_byml(romfs: Path, dicts: zsdic.Dictionaries, path: str):
    data = (romfs / path).read_bytes()
    if path.endswith(".zs"):
        data = dicts.decompress(path, data)
    return byml.read(data)


def scan(romfs: str | Path) -> list[Location]:
    """Every placement check in the dump at ``romfs`` (read only), sorted by :func:`sort_key`."""
    romfs = Path(romfs)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    paths = sorted(p.relative_to(romfs).as_posix() for p in romfs.glob(BANC_GLOB))
    if not paths:
        raise CensusError(f"no placement files under {romfs / 'Banc'}")
    banc = {path: read_romfs_byml(romfs, dicts, path) for path in paths}
    flags = save_flags(read_romfs_byml(romfs, dicts, GAME_DATA_LIST))
    return scan_trees(banc, flags)
