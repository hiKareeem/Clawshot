"""Item icons for the tracker: decoded at run time from the player's own dump and cached as PNG outside the repository.

The game keeps one item picture per file, ``UI/Tex/Icon/<name>.bntx.zs`` (plain zstd, without a dictionary:
:mod:`clawshot.formats.zsdic`, ``plans/rounds/r1-formats.md``), each a BNTX holding one texture (ASTC 4x4 on build
e0f3ccfa) read by :mod:`clawshot.tracker.bntx`. A file is named after the ``ActorNameRef`` key of the actors that
show it, the key their texts are labelled by (``plans/03-game-data.md`` section 22, "Item-get text and model":
``Item_Sword_Kokiri`` -> ``Weapon_Sword_Kokiri``, ``Item_HeavyBoot`` -> ``Armor_Adult_HeavyBoot``). So an icon is
asked for by actor name: a file's own name (:data:`ICON_IDS`) or an actor of :data:`ICON_ACTORS`. Only those fixed
names ever become a path; nothing a caller passes is joined to the file system.

Songs, medallions, Spiritual Stones, heart pieces and containers, ammunition bundles and magic jars have no file in
``UI/Tex/Icon`` on build e0f3ccfa; :meth:`IconCache.get` returns None for them and the tracker shows text.
"""

import contextlib
import hashlib
import os
import sys
import threading
import zlib
from pathlib import Path
from tempfile import NamedTemporaryFile

import zstandard

from clawshot.formats import zsdic
from clawshot.pack import ROOT
from clawshot.pack.source import dump_layers, open_nup
from clawshot.tracker import bntx

ICON_FOLDER = "UI/Tex/Icon"
ICON_SUFFIX = ".bntx.zs"
CACHE_VERSION = 1  # part of every cached PNG's name: bump it when decoding or PNG writing changes the output
MAX_ICON_BYTES = 64 << 20  # a decompressed icon file; the largest on build e0f3ccfa is 2.2 MB

# Every file in UI/Tex/Icon on build e0f3ccfa (129).
ICON_IDS = frozenset(
    [
        "Animal_Fish_Bass",
        "Armor_Adult_Gauntlet_Gold",
        "Armor_Adult_Gauntlet_Silver",
        "Armor_Adult_Goron",
        "Armor_Adult_HeavyBoot",
        "Armor_Adult_HoverBoot",
        "Armor_Adult_Normal",
        "Armor_Adult_Zora",
        "Armor_Child_Gauntlet_Goron",
        "Armor_Child_Mask_Amiibo0",
        "Armor_Child_Mask_Amiibo1",
        "Armor_Child_Mask_Bunny",
        "Armor_Child_Mask_Gerudo",
        "Armor_Child_Mask_Goron",
        "Armor_Child_Mask_Keaton",
        "Armor_Child_Mask_Skull",
        "Armor_Child_Mask_Spooky",
        "Armor_Child_Mask_Truth",
        "Armor_Child_Mask_Zora",
        "Armor_GlassTruth",
        "Item_AgonyStone",
        "Item_AlarmCucco",
        "Item_Arrow_Fire",
        "Item_Arrow_Fire_PouchIcon",
        "Item_Arrow_Ice",
        "Item_Arrow_Ice_PouchIcon",
        "Item_Arrow_Light",
        "Item_Arrow_Light_PouchIcon",
        "Item_Arrow_Normal",
        "Item_Arrow_Normal_PouchIcon",
        "Item_Bomb",
        "Item_BombBag_Large",
        "Item_BombBag_Medium",
        "Item_BombBag_Small",
        "Item_Bombchu",
        "Item_Boomerang",
        "Item_Bottle",
        "Item_Bottle_BigPoe",
        "Item_Bottle_BlueFire",
        "Item_Bottle_BluePotion",
        "Item_Bottle_Bug",
        "Item_Bottle_Fairy",
        "Item_Bottle_Fish",
        "Item_Bottle_GreenPotion",
        "Item_Bottle_HalfMilk",
        "Item_Bottle_Letter",
        "Item_Bottle_Milk",
        "Item_Bottle_Poe",
        "Item_Bottle_RedPotion",
        "Item_BrokenSword",
        "Item_BulletBag_Large",
        "Item_BulletBag_Medium",
        "Item_BulletBag_Small",
        "Item_ClaimCheck",
        "Item_CojiroCucco",
        "Item_DekuNut",
        "Item_DekuSeed",
        "Item_DekuStick",
        "Item_DinFire",
        "Item_Dungeon_BossKey",
        "Item_Dungeon_Compass",
        "Item_Dungeon_Map",
        "Item_Dungeon_SmallKey",
        "Item_EyeDrop",
        "Item_EyeballFrog",
        "Item_FairyBless_DefenseDouble",
        "Item_FairyBless_MP",
        "Item_FairyBless_MPDouble",
        "Item_FaroreWind",
        "Item_FishingRod",
        "Item_Hammer",
        "Item_Hammer_PouchIcon",
        "Item_Hookshot",
        "Item_Longshot",
        "Item_MagicBean",
        "Item_NayruLove",
        "Item_NutBag_Large",
        "Item_NutBag_Medium",
        "Item_NutBag_Small",
        "Item_Ocarina_Fairy",
        "Item_Ocarina_Time",
        "Item_Ocarina_Time_PouchIcon",
        "Item_OddMushroom",
        "Item_OddPowder",
        "Item_PoacherSaw",
        "Item_PocketCucco",
        "Item_PocketEgg",
        "Item_Prescription",
        "Item_Quiver_Large",
        "Item_Quiver_Medium",
        "Item_Quiver_Small",
        "Item_Scale_Gold",
        "Item_Scale_Silver",
        "Item_ScrubBusinessSeed",
        "Item_StickBag_Large",
        "Item_StickBag_Medium",
        "Item_StickBag_Small",
        "Item_Token_Gerudo",
        "Item_Token_Gold",
        "Item_Wallet_Large",
        "Item_Wallet_Medium",
        "Item_Wallet_Small",
        "Item_WeirdEgg",
        "Item_ZeldaLetter",
        "Land_Gerudo_HorsebackArcheryTarget_A_01",
        "Obj_Armor_Child_Normal",
        "Obj_Rupee_Blue",
        "Obj_Rupee_Gold",
        "Obj_Rupee_Green",
        "Obj_Rupee_Purple",
        "Obj_Rupee_Red",
        "Obj_Shop_TargetPrize_A_01",
        "Obj_ZoraDomain_DivingGame_A_01",
        "Pouch_FishingRod_SinkingLure",
        "Pouch_Range_BowAndArrow_Fire",
        "Pouch_Range_BowAndArrow_Ice",
        "Pouch_Range_BowAndArrow_Light",
        "Weapon_Lure",
        "Weapon_Range_Bow",
        "Weapon_Range_SlingShot",
        "Weapon_Shield_Deku",
        "Weapon_Shield_Hylian",
        "Weapon_Shield_Mirror",
        "Weapon_SinkingLure",
        "Weapon_Sword_Biggoron",
        "Weapon_Sword_BrokenGiant",
        "Weapon_Sword_Giant",
        "Weapon_Sword_Kokiri",
        "Weapon_Sword_Master",
    ]
)

# Icon -> the actors whose ActorNameRef key it is although their own name differs: clawshot.patch.text.text_key over
# every RSDB/PouchActorInfo row and item_actors.toml actor of build e0f3ccfa (read 2026-11-13), keeping item, pouch,
# equipment, chest, shop and pickup actors (not projectiles, NPCs or minigame rentals). Names only.
_ACTORS_BY_ICON: dict[str, tuple[str, ...]] = {
    "Armor_Adult_Gauntlet_Gold": ("Item_Gauntlet_Gold", "Pouch_Gauntlet_Gold"),
    "Armor_Adult_Gauntlet_Silver": ("Item_Gauntlet_Silver", "Pouch_Gauntlet_Silver"),
    "Armor_Adult_Goron": ("Obj_Armor_Goron", "Shop_Armor_Goron"),
    "Armor_Adult_HeavyBoot": ("Item_HeavyBoot",),
    "Armor_Adult_HoverBoot": ("Item_HoverBoot",),
    "Armor_Adult_Normal": ("Obj_Armor_Adult_Normal",),
    "Armor_Adult_Zora": ("Obj_Armor_Zora", "Shop_Armor_Zora"),
    "Armor_Child_Gauntlet_Goron": ("Item_Gauntlet_Goron", "Pouch_Gauntlet_Goron"),
    "Armor_Child_Mask_Amiibo0": ("Obj_Mask_Amiibo0",),
    "Armor_Child_Mask_Amiibo1": ("Obj_Mask_Amiibo1",),
    "Armor_Child_Mask_Bunny": ("Item_Mask_Bunny", "Shop_Mask_Bunny"),
    "Armor_Child_Mask_Gerudo": ("Item_Mask_Gerudo", "Shop_Mask_Gerudo"),
    "Armor_Child_Mask_Goron": ("Item_Mask_Goron", "Shop_Mask_Goron"),
    "Armor_Child_Mask_Keaton": ("Item_Mask_Keaton", "Shop_Mask_Keaton"),
    "Armor_Child_Mask_Skull": ("Item_Mask_Skull", "Shop_Mask_Skull"),
    "Armor_Child_Mask_Spooky": ("Item_Mask_Spooky", "Shop_Mask_Spooky"),
    "Armor_Child_Mask_Truth": ("Item_Mask_Truth", "Shop_Mask_Truth"),
    "Armor_Child_Mask_Zora": ("Item_Mask_Zora", "Shop_Mask_Zora"),
    "Armor_GlassTruth": ("Armor_Adult_GlassTruth", "Armor_Child_GlassTruth", "Item_GlassTruth"),
    "Item_AgonyStone": ("Armor_Adult_AgonyStone", "Armor_Child_AgonyStone"),
    "Item_AlarmCucco": ("Pouch_AlarmCoucco",),
    "Item_Arrow_Fire": ("Obj_Arrow_Fire", "Pouch_Arrow_Fire"),
    "Item_Arrow_Ice": ("Pouch_Arrow_Ice",),
    "Item_Arrow_Light": ("Pouch_Arrow_Light",),
    "Item_Arrow_Normal": ("Pouch_Arrow_Normal",),
    "Item_Bomb": ("Obj_Bomb", "Pouch_Bomb"),
    "Item_BombBag_Large": ("Pouch_BombBag_Large",),
    "Item_BombBag_Medium": ("Pouch_BombBag_Medium",),
    "Item_BombBag_Small": ("Pouch_BombBag_Small",),
    "Item_Bombchu": ("Obj_Bombchu", "Pouch_Bombchu"),
    "Item_Boomerang": ("Pouch_Boomerang", "Weapon_Boomerang"),
    "Item_Bottle": ("Pouch_Bottle", "Weapon_Bottle"),
    "Item_Bottle_BigPoe": ("Pouch_Bottle_BigPoe", "Weapon_Bottle_BigPoe"),
    "Item_Bottle_BlueFire": ("Pouch_Bottle_BlueFire", "Shop_Bottle_BlueFire", "Weapon_Bottle_BlueFire"),
    "Item_Bottle_BluePotion": ("Pouch_Bottle_BluePotion", "Weapon_Bottle_BluePotion"),
    "Item_Bottle_Bug": ("Pouch_Bottle_Bug", "Shop_Bottle_Bug", "Weapon_Bottle_Bug"),
    "Item_Bottle_Fairy": ("Pouch_Bottle_Fairy", "Shop_Bottle_Fairy", "Weapon_Bottle_Fairy"),
    "Item_Bottle_Fish": ("Pouch_Bottle_Fish", "Shop_Bottle_Fish", "Weapon_Bottle_Fish"),
    "Item_Bottle_GreenPotion": ("Pouch_Bottle_GreenPotion", "Shop_Bottle_GreenPotion", "Weapon_Bottle_GreenPotion"),
    "Item_Bottle_HalfMilk": ("Pouch_Bottle_HalfMilk", "Shop_Bottle_HalfMilk", "Weapon_Bottle_HalfMilk"),
    "Item_Bottle_Letter": ("Obj_Bottle_Letter", "Pouch_Bottle_Letter", "Weapon_Bottle_Letter"),
    "Item_Bottle_Milk": ("Pouch_Bottle_Milk", "Weapon_Bottle_Milk"),
    "Item_Bottle_Poe": ("Pouch_Bottle_Poe", "Shop_Bottle_Poe", "Weapon_Bottle_Poe"),
    "Item_Bottle_RedPotion": ("Pouch_Bottle_RedPotion", "Shop_Bottle_RedPotion", "Weapon_Bottle_RedPotion"),
    "Item_BrokenSword": ("Pouch_BrokenSword",),
    "Item_BulletBag_Large": ("Pouch_BulletBag_Large",),
    "Item_BulletBag_Medium": ("Pouch_BulletBag_Medium",),
    "Item_BulletBag_Small": ("Pouch_BulletBag_Small",),
    "Item_ClaimCheck": ("Pouch_ClaimCheck",),
    "Item_CojiroCucco": ("Pouch_CojiroCucco",),
    "Item_DekuNut": ("Obj_DekuNut", "Pouch_DekuNut"),
    "Item_DekuStick": ("Obj_DekuStick", "Pouch_DekuStick", "Shop_DekuStick", "Weapon_DekuStick"),
    "Item_DinFire": ("Pouch_DinFire",),
    "Item_Dungeon_SmallKey": (
        "Obj_Dungeon_SmallKey",
        "Obj_Dungeon_SmallKey_GerudoFortress_01",
        "Obj_Dungeon_SmallKey_GerudoFortress_02",
        "Obj_Dungeon_SmallKey_GerudoFortress_03",
        "Obj_Dungeon_SmallKey_GerudoFortress_04",
    ),
    "Item_EyeDrop": ("Pouch_EyeDrop",),
    "Item_EyeballFrog": ("Pouch_EyeballFrog",),
    "Item_FairyBless_DefenseDouble": ("Pouch_FairyBless_DefenseDouble",),
    "Item_FairyBless_MP": ("Pouch_FairyBless_MP",),
    "Item_FairyBless_MPDouble": ("Pouch_FairyBless_MPDouble",),
    "Item_FaroreWind": ("Pouch_FaroreWind",),
    "Item_FishingRod": ("Weapon_FishingRod",),
    "Item_Hammer": ("Pouch_Hammer", "Weapon_Hammer"),
    "Item_Hookshot": ("Pouch_Hookshot",),
    "Item_Longshot": ("Pouch_Longshot",),
    "Item_MagicBean": ("Pouch_MagicBean",),
    "Item_NayruLove": ("Pouch_NayruLove",),
    "Item_NutBag_Large": ("Pouch_NutBag_Large",),
    "Item_NutBag_Medium": ("Pouch_NutBag_Medium",),
    "Item_NutBag_Small": ("Pouch_NutBag_Small",),
    "Item_Ocarina_Fairy": ("Pouch_Ocarina_Fairy",),
    "Item_Ocarina_Time": ("Obj_Ocarina_Time", "Pouch_Ocarina_Time"),
    "Item_OddMushroom": ("Pouch_OddMushroom",),
    "Item_OddPowder": ("Pouch_OddPowder",),
    "Item_PoacherSaw": ("Pouch_PoacherSaw",),
    "Item_PocketCucco": ("Pouch_PocketCucco",),
    "Item_PocketEgg": ("Pouch_PocketEgg",),
    "Item_Prescription": ("Pouch_Prescription",),
    "Item_Quiver_Large": ("Pouch_Quiver_Large",),
    "Item_Quiver_Medium": ("Pouch_Quiver_Medium",),
    "Item_Quiver_Small": ("Pouch_Quiver_Small",),
    "Item_Scale_Gold": ("Pouch_Scale_Gold",),
    "Item_Scale_Silver": ("Pouch_Scale_Silver",),
    "Item_ScrubBusinessSeed": ("Obj_ScrubBusinessSeed", "Pouch_ScrubBusinessSeed"),
    "Item_StickBag_Large": ("Pouch_StickBag_Large",),
    "Item_StickBag_Medium": ("Pouch_StickBag_Medium",),
    "Item_StickBag_Small": ("Pouch_StickBag_Small",),
    "Item_Token_Gerudo": ("Pouch_Token_Gerudo",),
    "Item_Token_Gold": ("Obj_Token_Gold", "Pouch_Token_Gold"),
    "Item_Wallet_Large": ("Pouch_Wallet_Large",),
    "Item_Wallet_Medium": ("Pouch_Wallet_Medium",),
    "Item_Wallet_Small": ("Pouch_Wallet_Small",),
    "Item_WeirdEgg": ("Pouch_WeirdEgg",),
    "Item_ZeldaLetter": ("Pouch_ZeldaLetter",),
    "Obj_Rupee_Blue": ("TBox_Rupee_Blue",),
    "Obj_Rupee_Gold": ("TBox_Rupee_Gold",),
    "Obj_Rupee_Green": ("TBox_Rupee_Green",),
    "Obj_Rupee_Purple": ("TBox_Rupee_Purple",),
    "Obj_Rupee_Red": ("TBox_Rupee_Red",),
    "Weapon_Range_Bow": ("Item_Range_Bow", "Pouch_Range_BowAndArrow_Normal"),
    "Weapon_Range_SlingShot": ("Item_Range_SlingShot", "Pouch_Range_SlingShot"),
    "Weapon_Shield_Deku": ("Obj_Shield_Deku", "Shop_Weapon_Shield_Deku", "TBox_Shield_Deku"),
    "Weapon_Shield_Hylian": ("Obj_Shield_Hylian", "Shop_Weapon_Shield_Hylian", "TBox_Shield_Hylian"),
    "Weapon_Shield_Mirror": ("Item_Shield_Mirror",),
    "Weapon_SinkingLure": ("Obj_SinkingLure",),
    "Weapon_Sword_Biggoron": ("Item_Sword_Biggoron",),
    "Weapon_Sword_BrokenGiant": ("Item_Sword_BrokenGiant",),
    "Weapon_Sword_Giant": ("Item_Sword_Giant", "Shop_Sword_Giant"),
    "Weapon_Sword_Kokiri": ("Item_Sword_Kokiri",),
}
ICON_ACTORS: dict[str, str] = {actor: icon for icon, actors in _ACTORS_BY_ICON.items() for actor in actors}
"""Actor -> the icon file it shows, for actors whose own name is not a file in ``UI/Tex/Icon``."""


class IconUnavailable(LookupError):
    """The source holds no file for a known icon, or the source itself is missing."""


def icon_id(actor: str) -> str | None:
    """The ``UI/Tex/Icon`` file name (without ``.bntx.zs``) that shows ``actor``, or None for any other name."""
    if not isinstance(actor, str):
        return None
    return actor if actor in ICON_IDS else ICON_ACTORS.get(actor)


def default_cache_dir() -> Path:
    """The user's cache folder for decoded icons, never the checkout: ``%LOCALAPPDATA%\\Clawshot\\Cache\\icons`` on
    Windows, ``~/Library/Caches/Clawshot/icons`` on macOS, ``$XDG_CACHE_HOME/clawshot/icons`` (``~/.cache`` when unset
    or relative) elsewhere."""
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA", "")
        parent = Path(local) if local and Path(local).is_absolute() else Path.home() / "AppData" / "Local"
        return parent / "Clawshot" / "Cache" / "icons"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "Clawshot" / "icons"
    xdg = os.environ.get("XDG_CACHE_HOME", "")
    parent = Path(xdg) if xdg and Path(xdg).is_absolute() else Path.home() / ".cache"
    return parent / "clawshot" / "icons"


def decoder_version() -> str | None:
    """``texture2ddecoder <version>`` when the optional decoder is installed, else None."""
    if bntx.load_decoder() is None:
        return None
    from importlib.metadata import PackageNotFoundError, version

    try:
        return f"texture2ddecoder {version('texture2ddecoder')}"
    except PackageNotFoundError:
        return "texture2ddecoder"


def encode_png(width: int, height: int, rgba: bytes) -> bytes:
    """An 8-bit RGBA PNG of ``rgba`` rows (W3C PNG Third Edition, https://www.w3.org/TR/png-3/: the signature, IHDR
    with colour type 6, one zlib IDAT of filter-type-0 lines, IEND). Deterministic: the same pixels give the same
    bytes."""
    stride = width * 4
    if width <= 0 or height <= 0 or len(rgba) != stride * height:
        raise ValueError(f"{len(rgba)} bytes are not {width}x{height} RGBA pixels")

    def chunk(kind: bytes, body: bytes) -> bytes:
        return len(body).to_bytes(4, "big") + kind + body + zlib.crc32(kind + body).to_bytes(4, "big")

    header = width.to_bytes(4, "big") + height.to_bytes(4, "big") + bytes((8, 6, 0, 0, 0))
    lines = b"".join(b"\0" + rgba[y * stride : (y + 1) * stride] for y in range(height))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(lines)) + chunk(b"IEND", b"")


def icon_png(stored: bytes, icon: str, decoder=None) -> bytes:
    """The PNG of ``UI/Tex/Icon/<icon>.bntx.zs`` from the file's stored bytes (one zstd frame without a dictionary,
    as :mod:`clawshot.formats.zsdic` lists ``.bntx.zs``): its texture named ``icon``, or its only texture. Raises
    :class:`~clawshot.tracker.bntx.BntxError` (and subclasses), ``ZsError`` or ``zstandard.ZstdError``."""
    name = f"{ICON_FOLDER}/{icon}{ICON_SUFFIX}"
    frame = zstandard.get_frame_parameters(stored)
    if frame.dict_id != 0:
        raise zsdic.ZsError(f"{name}: the frame names dictionary {frame.dict_id}; icon files use none")
    if frame.content_size != zstandard.CONTENTSIZE_UNKNOWN and frame.content_size > MAX_ICON_BYTES:
        raise zsdic.ZsError(f"{name}: {frame.content_size} bytes decompressed is more than an icon")
    textures = bntx.read(zstandard.ZstdDecompressor().decompress(stored, max_output_size=MAX_ICON_BYTES))
    named = [texture for texture in textures if texture.name == icon]
    if named:
        texture = named[0]
    elif len(textures) == 1:
        texture = textures[0]
    else:
        raise bntx.BntxError(f"{name} holds {len(textures)} textures and none is named {icon}")
    return encode_png(*bntx.to_rgba(texture, decoder))


def _inside(path: Path, folder: Path) -> bool:
    return path == folder or folder in path.parents


_FAILURES = (ValueError, OSError, LookupError, zstandard.ZstdError)


class IconCache:
    """PNG icons for whitelisted actor names, decoded once from the player's dump and kept in ``cache_dir``.

    ``source`` is an extracted RomFS folder, a dump folder in the layout NUP packs from (``base/romfs`` and
    optionally ``updates/<version>/romfs``, the newest update's copy winning, as
    :class:`clawshot.pack.source.LayeredRomfs`) or a ``.nup`` read in place through
    :func:`clawshot.pack.source.open_nup` (one opening reads the whitelisted icon files into memory, about 7 MB;
    nothing is extracted and the file is closed again). The source is only read.

    ``cache_dir`` defaults to :func:`default_cache_dir`; it may not lie inside the source folder or the Clawshot
    checkout. A PNG's name carries the SHA-256 of the stored icon file and :data:`CACHE_VERSION`, so another dump or a
    changed file is decoded again and older PNGs of that icon are removed; a later :class:`IconCache` reuses the PNG.

    :meth:`get` never raises for a missing source, file or decoder, or an unreadable or unsupported texture: it
    returns None and :attr:`problems` keeps why, for the tracker to show the item's name instead. No network access.
    Safe to share between threads.
    """

    def __init__(self, source: str | os.PathLike, cache_dir: str | os.PathLike | None = None):
        self.source = Path(source)
        self.cache_dir = Path(cache_dir) if cache_dir is not None else default_cache_dir()
        cache = self.cache_dir.resolve()
        if _inside(cache, ROOT.resolve()) or (self.source.is_dir() and _inside(cache, self.source.resolve())):
            raise ValueError(f"icon cache {self.cache_dir} must lie outside the game dump and the Clawshot folder")
        self._lock = threading.Lock()
        self._done: dict[str, tuple[tuple, Path]] = {}
        self._nup_files: dict[str, bytes] = {}
        self._nup_signature: tuple | None = None
        self._problems: dict[str, str] = {}

    @property
    def problems(self) -> dict[str, str]:
        """Requested name -> why its last :meth:`get` returned None (cleared when one succeeds)."""
        with self._lock:
            return dict(self._problems)

    def status(self) -> dict:
        """JSON-able summary: source and its kind, cache folder, decoder, and the current problems."""
        with self._lock:
            problems = dict(self._problems)
        return {
            "source": str(self.source),
            "kind": self._kind(),
            "cache_dir": str(self.cache_dir),
            "decoder": decoder_version(),
            "problems": problems,
        }

    def get(self, actor: str) -> Path | None:
        """The cached PNG showing ``actor`` (decoded now if needed), or None with the reason in :attr:`problems`."""
        icon = icon_id(actor)
        with self._lock:
            if icon is None:
                self._problems[str(actor)] = "no UI/Tex/Icon picture is known for this name"
                return None
            try:
                path = self._png(icon)
            except bntx.DecoderUnavailable:
                self._problems[actor] = (
                    "icons need the optional texture2ddecoder package (Clawshot's ui extra); showing names instead"
                )
                return None
            except _FAILURES as error:
                self._problems[actor] = f"{icon}: {error}"
                return None
            self._problems.pop(actor, None)
            return path

    def _kind(self) -> str | None:
        if self.source.is_dir():
            return "dump" if dump_layers(self.source) is not None else "romfs"
        return "nup" if self.source.is_file() else None

    def _png(self, icon: str) -> Path:
        relative = f"{ICON_FOLDER}/{icon}{ICON_SUFFIX}"
        kind = self._kind()
        if kind is None:
            raise IconUnavailable(f"the game dump {self.source} is not there")
        if kind == "nup":
            stat = self.source.stat()
            signature = ("nup", stat.st_size, stat.st_mtime_ns)
            file = None
        else:
            layers = dump_layers(self.source) if kind == "dump" else [self.source]
            file = next((layer / relative for layer in reversed(layers) if (layer / relative).is_file()), None)
            if file is None:
                raise IconUnavailable(f"the game dump has no romfs/{relative}")
            stat = file.stat()
            signature = (str(file), stat.st_size, stat.st_mtime_ns)
        done = self._done.get(icon)
        if done is not None and done[0] == signature and done[1].is_file():
            return done[1]
        stored = self._nup_icon(icon, relative, signature) if file is None else file.read_bytes()
        digest = hashlib.sha256(stored).hexdigest()[:32]
        target = self.cache_dir / f"{icon}.{digest}.v{CACHE_VERSION}.png"
        if not target.is_file():
            self._write(icon, target, icon_png(stored, icon))
        self._done[icon] = (signature, target)
        return target

    def _nup_icon(self, icon: str, relative: str, signature: tuple) -> bytes:
        if self._nup_signature != signature:
            with open_nup(self.source) as nup:
                paths = {name: f"{ICON_FOLDER}/{name}{ICON_SUFFIX}" for name in sorted(ICON_IDS)}
                files = {name: nup.read(path) for name, path in paths.items() if path in nup.files}
            self._nup_files, self._nup_signature = files, signature
        if icon not in self._nup_files:
            raise IconUnavailable(f"the NUP's newest package has no romfs/{relative}")
        return self._nup_files[icon]

    def _write(self, icon: str, target: Path, png: bytes) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with NamedTemporaryFile(dir=self.cache_dir, prefix=f".{icon}.", suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(png)
            temporary.replace(target)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
        for old in self.cache_dir.glob(f"{icon}.*.png"):
            if old != target:
                with contextlib.suppress(OSError):  # in use (being served) on Windows: removed on a later decode
                    old.unlink()
