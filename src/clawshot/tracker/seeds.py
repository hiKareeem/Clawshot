"""A seed as the tracker sees it: where its files and saves are, and every shuffled check with how a save records it.

``load_seed(path)`` accepts the three layouts Clawshot writes:

- the UI's output root: ``<root>/seed/spoiler.json``, ``<root>/clawshot-seed.json`` (``app.library.MANIFEST``) and the
  isolated save folder ``<root>/user`` that Play passes as ``--user`` (``pack.runtime``: ``user = root / "user"``);
- a seed pack after Make seed: ``<root>/seed/spoiler.json``, ``<root>/pack.json`` and the same ``<root>/user``;
- a raw generator output (``python -m clawshot --out <dir>``): ``<dir>/spoiler.json`` beside ``<dir>/romfs``, or the
  path of a ``spoiler.json`` itself. Such a folder has no save convention; ``<dir>/user`` is used only when it exists.

Everything comes from the seed's own spoiler (``generate.spoiler`` plus ``patch.SeedOutput.spoiler``'s ``patch``) and
the generator's own definitions (the world data, ``patch/gift_rules.toml``, ``patch.scrubs.SALES``); nothing is
inferred from play.
"""

import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from functools import cache
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

MANIFEST = "clawshot-seed.json"  # app.library.MANIFEST, kept literal so the tracker needs no UI import
PACK_MANIFEST = "pack.json"  # pack.build's manifest beside the pack's seed folder
SPOILER = "spoiler.json"
MAX_SPOILER_BYTES = 64 << 20

# Bools in progress.sav for an unmodified GameDataList of build e0f3ccfa: "The save's Bool section holds exactly the
# GameDataList Bools with SaveFileIndex 0 (10212 in every slot read)" (plans/03-game-data.md section 19). Each saved
# Bool the gift patch adds (``patch.gifts.add_flags``) grows it by one.
NATIVE_SAVED_BOOLS = 10212

# World dungeon name -> the ``DungeonInfo.<name>`` Struct holding its saved key/map/compass leaves, in game order.
# Names: sloperina-FINDINGS.md section 1 ("Dungeon names ... same as the map name") and plans/03-game-data.md
# section 44 (the 14 dungeon Structs; FinalBattleField and GerudoFortress hold no world dungeon's items).
DUNGEON_INFO = {
    "Deku Tree": "InsideTheDekuTree",
    "Dodongos Cavern": "DodongoCavern",
    "Jabu Jabus Belly": "InsideJabuJabuBelly",
    "Forest Temple": "ForestTemple",
    "Fire Temple": "FireTemple",
    "Water Temple": "WaterTemple",
    "Shadow Temple": "ShadowTemple",
    "Spirit Temple": "SpiritTemple",
    "Bottom of the Well": "BottomOfTheWell",
    "Ice Cavern": "IceCavern",
    "Gerudo Training Ground": "GerudoTrainingGround",
    "Ganons Castle": "InsideGanonCastle",
}

# How a check's collection is read from a save (``Check.method``).
NAMED_BOOL = "named_bool"  # any of ``Check.flags`` true
PLACEMENT_HASH = "placement_hash"  # any of ``Check.hashes`` in the save's Bool64bitKey list
NO_RECORD = "none"  # no audited record: always unknown

OTHER_AREA = "Other"
_DUNGEON_ITEM = re.compile(r"^(Small Key|Boss Key|Map|Compass) \((.+)\)$")


class SeedError(ValueError):
    """The path holds no readable Clawshot seed."""


@dataclass(frozen=True)
class Place:
    """Where the world puts a location: ``area`` (the display name of the generator's hint area,
    ``generate.hints.hint_area``), ``dungeon`` (``Region.dungeon``), ``type`` (OoT Randomizer's location type) and,
    for unshuffled locations, ``vanilla`` (the item it keeps) unless ``n64_only`` (the check is not in the remake)."""

    area: str
    dungeon: str | None
    type: str | None
    vanilla: str | None = None
    n64_only: bool = False


@dataclass(frozen=True)
class Check:
    """One shuffled location of the seed.

    ``location`` is the world key (the spoiler's ``placements`` key); ``label`` and ``where`` the spoiler's readable
    name and directions; ``item`` the placed logic item (a spoiler: only shown when asked, or once collected).
    ``kind`` is chest, boss_heart, freestanding, scrub, gift, shop or other. ``method`` says how the save records it:

    - ``named_bool``: chests read ``IsTreasureBoxOpen.<decimal actor Hash>`` (plans/03-game-data.md section 44: the
      raw Hash is "not its open-state accessor"); gifts read the check's flag from ``patch/gift_rules.toml`` (an
      existing flag the game sets once the check is given and on no other path, or the patch's own saved
      ``Clawshot.Gift.<flow>.<event>``, section 19); one-time scrubs read their native success-only completion Bool
      (``patch.scrubs.SALES``; section 23). A gift's added flag is named after its first census step, so every step
      of the check is a candidate and the one the save holds is read.
    - ``placement_hash``: boss hearts and anchored floor Heart Pieces, the audited placement-Hash Bool64 families of
      section 44. Persistence of a replaced pickup is per-experiment there, so an unset Hash is reported unknown,
      never "not collected".
    - ``none``: no audited record (shops restock, section 17; swap-only gifts): always unknown, with ``reason``.
    """

    location: str
    label: str
    where: str
    area: str
    dungeon: str | None
    kind: str
    item: str | None
    item_label: str | None
    method: str
    flags: tuple[str, ...] = ()
    hashes: tuple[int, ...] = ()
    reason: str | None = None


@dataclass(frozen=True)
class Seed:
    """A loaded seed. ``root`` is the output root (``seed_dir``'s parent for UI and pack layouts); ``user_path`` the
    save folder its runtime convention gives (``None`` for a raw output without one); ``metadata`` the spoiler-free
    facts (seed number, settings string, generator, manifest hash); ``checks`` every shuffled location in world order;
    ``small_keys``/``boss_keys``/``maps``/``compasses`` how many of each dungeon item the seed holds (shuffled
    placements plus unshuffled vanilla sources); ``added_flags`` the candidate names of every saved Bool the seed's
    gift patch adds, one tuple per added Bool."""

    root: Path
    seed_dir: Path
    spoiler_path: Path
    user_path: Path | None
    layout: str
    metadata: Mapping[str, Any]
    checks: tuple[Check, ...]
    small_keys: Mapping[str, int] = field(default_factory=dict)
    boss_keys: Mapping[str, int] = field(default_factory=dict)
    maps: Mapping[str, int] = field(default_factory=dict)
    compasses: Mapping[str, int] = field(default_factory=dict)
    added_flags: tuple[tuple[str, ...], ...] = ()
    warnings: tuple[str, ...] = ()


def installed_version() -> str:
    try:
        return version("clawshot")
    except PackageNotFoundError:
        return "unknown"


@cache
def _default_location_index() -> dict[str, Place]:
    from clawshot.generate import hints
    from clawshot.patch import gifts
    from clawshot.world import build_world, load_spec

    # The shopkeeper's free shield is a placed check only in Gift/NPC seeds (``patch.gifts.shopkeeper_spec``).
    world = build_world(gifts.shopkeeper_spec(load_spec()))
    names = hints.load()["areas"]
    areas: dict[str, str] = {}

    def display(region: str) -> str:
        if region not in areas:
            key = hints.hint_area(world, region)
            label = names.get(key, key) if key else world.regions[region].scene or region
            label = label[4:] if label.startswith("the ") else label
            areas[region] = label[:1].upper() + label[1:]
        return areas[region]

    return {
        name: Place(display(loc.region), world.regions[loc.region].dungeon, loc.type, loc.vanilla, bool(loc.n64_only))
        for name, loc in world.locations.items()
    }


def location_index() -> Mapping[str, Place]:
    """Every world location's :class:`Place`, from the generator's world data. Tests replace this function."""
    return _default_location_index()


@cache
def _gift_rules() -> dict:
    from clawshot.patch import gifts

    return gifts.load()


def _scrub_flags() -> dict[str, str]:
    from clawshot.patch import scrubs

    return {name: sale.flag for name, sale in scrubs.SALES.items()}


@cache
def _catalog() -> dict:
    """The readable-location catalog the spoiler copies its ``ids`` from (``generate.names.load``)."""
    from clawshot.generate import names

    return names.load()


def _gift_record(name: str, ids: tuple[str, ...]) -> tuple[tuple[str, ...], bool]:
    """(candidate flag names, whether the patch adds the flag) for a gift check; ((), False) without a record.

    Mirrors ``patch.gifts.GiftChange.flag``/``new_flag``: the rule's own ``flag``, else ``Clawshot.Gift.`` plus the
    first census step when the check has reads, once gates, a purchase or is an expert gallery prize."""
    from clawshot.patch import gifts

    rule = _gift_rules().get(name)
    if rule is None or rule.cls == gifts.MORE:
        return (), False
    expert = name in gifts.GALLERY_EXPERT_CHECKS.values()
    if not (rule.given or rule.writes or rule.once or rule.purchase or expert):
        return (), False
    if rule.flag:
        return (rule.flag,), False
    steps = tuple(i for i in ids if "/" in i)
    return tuple(gifts.FLAG_PREFIX + step.replace("/", ".") for step in steps), True


def _hash_ids(ids: Any) -> tuple[int, ...]:
    if not isinstance(ids, list):
        return ()
    return tuple(int(i) for i in ids if isinstance(i, str) and i.isdigit())


def _chest_hashes(spoiler: Mapping[str, Any]) -> dict[str, tuple[int, ...]]:
    """Location -> its chest actor Hashes from the spoiler's patch plan (``patch.plan.Plan.as_dict``)."""
    patch = spoiler.get("patch")
    if not isinstance(patch, Mapping):
        return {}
    out: dict[str, list[int]] = {}
    for key in ("changes", "unchanged"):
        rows = patch.get(key, [])
        if not isinstance(rows, list):
            raise SeedError(f"spoiler patch.{key} is not a list")
        for row in rows:
            if not isinstance(row, Mapping) or not isinstance(row.get("location"), str):
                raise SeedError(f"spoiler patch.{key} has an entry without a location")
            raw = row.get("id")
            if not isinstance(raw, str) or not raw.isdigit():
                raise SeedError(f"spoiler patch.{key} entry {row['location']!r} has no decimal actor Hash")
            hashes = out.setdefault(row["location"], [])
            if int(raw) not in hashes:
                hashes.append(int(raw))
    return {name: tuple(sorted(hashes)) for name, hashes in out.items()}


def _classify(
    name: str,
    place: Place | None,
    ids: tuple[str, ...],
    chests: Mapping[str, tuple[int, ...]],
    scrubs: Mapping[str, str],
) -> tuple[str, str, tuple[str, ...], tuple[int, ...], str | None, bool]:
    """(kind, method, flags, hashes, reason, flag is added by the patch)."""
    location_type = place.type if place else None
    if name in chests or location_type == "Chest":
        hashes = chests.get(name) or _hash_ids(list(ids))
        if not hashes:
            return "chest", NO_RECORD, (), (), "the spoiler names no actor Hash for this chest", False
        return "chest", NAMED_BOOL, tuple(f"IsTreasureBoxOpen.{h}" for h in hashes), hashes, None, False
    if name in scrubs:
        return "scrub", NAMED_BOOL, (scrubs[name],), (), None, False
    flags, added = _gift_record(name, ids)
    if flags:
        return "gift", NAMED_BOOL, flags, (), None, added
    if name in _gift_rules():
        return "gift", NO_RECORD, (), (), "this gift keeps no saved record of being given", False
    if location_type in ("BossHeart", "Collectable", "Freestanding"):
        kind = "boss_heart" if location_type == "BossHeart" else "freestanding"
        hashes = _hash_ids(list(ids))
        if not hashes:
            return kind, NO_RECORD, (), (), "the spoiler names no pickup Hash", False
        return kind, PLACEMENT_HASH, (), hashes, None, False
    if location_type in ("Shop", "MaskShop"):
        return "shop", NO_RECORD, (), (), "shop slots restock and keep no sold record", False
    return "other", NO_RECORD, (), (), "no audited save record for this kind of check", False


def _read_json(path: Path, what: str) -> Any:
    try:
        if path.stat().st_size > MAX_SPOILER_BYTES:
            raise SeedError(f"{what} is too large to be a Clawshot file: {path}")
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SeedError(f"{what} is not valid JSON ({error.msg}, line {error.lineno}): {path}") from None
    except UnicodeDecodeError:
        raise SeedError(f"{what} is not UTF-8 text: {path}") from None


def _locate(path: Path) -> tuple[Path, Path, Path, str]:
    """(root, seed_dir, spoiler_path, layout)."""
    if path.is_file():
        spoiler, seed_dir = path, path.parent
    elif (path / "seed" / SPOILER).is_file():
        spoiler, seed_dir = path / "seed" / SPOILER, path / "seed"
    elif (path / SPOILER).is_file():
        spoiler, seed_dir = path / SPOILER, path
    elif path.exists():
        raise SeedError(f"No seed here: neither {path / 'seed' / SPOILER} nor {path / SPOILER} exists.")
    else:
        raise SeedError(f"The seed folder does not exist: {path}")
    parent = seed_dir.parent
    # A folder called ``seed`` inside a UI or pack root (its manifest, or Play's ``user`` folder, beside it).
    nested = seed_dir.name == "seed" and (
        any((parent / name).is_file() for name in (MANIFEST, PACK_MANIFEST)) or (parent / "user").is_dir()
    )
    root = parent if nested else seed_dir
    if (root / MANIFEST).is_file():
        layout = "ui"
    elif (root / PACK_MANIFEST).is_file():
        layout = "pack"
    else:
        layout = "raw"
    return root, seed_dir, spoiler, layout


def _manifest(root: Path, layout: str, warnings: list[str]) -> dict[str, Any]:
    name = {"ui": MANIFEST, "pack": PACK_MANIFEST}.get(layout)
    if name is None:
        return {}
    try:
        record = _read_json(root / name, "The seed's information file")
    except (SeedError, OSError) as error:
        warnings.append(f"{name} could not be read: {error}")
        return {}
    if not isinstance(record, dict):
        warnings.append(f"{name} is not a JSON object")
        return {}
    return record


def _count(spoiler_items: Mapping[str, str], index: Mapping[str, Place]) -> dict[str, dict[str, int]]:
    """Per dungeon item family, per world dungeon: placements in the seed plus unshuffled vanilla sources that exist in
    the remake (plans/03-game-data.md section 18: the Shadow Temple and Bottom of the Well keep one freestanding
    vanilla key each). Items are named ``<family> (<Dungeon>)`` (plans/04-world-format.md, Items)."""
    counts: dict[str, dict[str, int]] = {"Small Key": {}, "Boss Key": {}, "Map": {}, "Compass": {}}

    def add(item: str | None) -> None:
        match = _DUNGEON_ITEM.match(item or "")
        if match and match.group(2) in DUNGEON_INFO:
            family = counts[match.group(1)]
            family[match.group(2)] = family.get(match.group(2), 0) + 1

    for item in spoiler_items.values():
        add(item)
    for name, place in index.items():
        if name not in spoiler_items and not place.n64_only:
            add(place.vanilla)
    return counts


def load_seed(path: str | Path, *, index: Callable[[], Mapping[str, Place]] | None = None) -> Seed:
    """Read a seed's spoiler and manifest (never its romfs) into a :class:`Seed`.

    Raises :class:`SeedError` when the path holds no usable spoiler."""
    root, seed_dir, spoiler_path, layout = _locate(Path(path).expanduser())
    warnings: list[str] = []
    spoiler = _read_json(spoiler_path, "The spoiler")
    if not isinstance(spoiler, dict):
        raise SeedError(f"The spoiler is not a JSON object: {spoiler_path}")
    placements = spoiler.get("placements")
    if not isinstance(placements, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in placements.items()
    ):
        raise SeedError(f"The spoiler has no placements table: {spoiler_path}")
    descriptions = spoiler.get("locations", {})
    if not isinstance(descriptions, dict):
        raise SeedError(f"The spoiler's locations are not a table: {spoiler_path}")
    item_names = spoiler.get("item_names", {})
    if not isinstance(item_names, dict):
        item_names = {}
    if type(spoiler.get("seed")) is not int:
        warnings.append("The spoiler has no seed number.")

    manifest = _manifest(root, layout, warnings)
    if "seed" in manifest and manifest["seed"] != spoiler.get("seed"):
        warnings.append(f"The manifest's seed {manifest['seed']!r} differs from the spoiler's {spoiler.get('seed')!r}.")
    if layout == "ui" and manifest.get("settings_string") not in (None, spoiler.get("settings_string")):
        warnings.append("The manifest's settings string differs from the spoiler's.")

    generator = spoiler.get("generator") if isinstance(spoiler.get("generator"), str) else None
    reading = installed_version()
    if generator and generator != f"clawshot {reading}":
        warnings.append(
            f"This seed was made by {generator}; the tracker reads it with clawshot {reading}'s definitions. "
            "Checks or flags that changed between versions may show wrongly."
        )

    places = (index or location_index)()
    chests = _chest_hashes(spoiler)
    scrubs = _scrub_flags()
    catalog = _catalog()
    checks = []
    added: list[tuple[str, ...]] = []
    unplaced = 0
    for name, item in placements.items():
        description = descriptions.get(name, {})
        if not isinstance(description, dict):
            description = {}
        raw_ids = description.get("ids", [])
        ids = tuple(i for i in raw_ids if isinstance(i, str)) if isinstance(raw_ids, list) else ()
        if not ids and name in catalog:
            ids = catalog[name].ids  # older spoilers lack some rows; a check's physical identity is stable (rule 5)
        place = places.get(name)
        if place is None:
            unplaced += 1
        kind, method, flags, hashes, reason, is_added = _classify(name, place, ids, chests, scrubs)
        if is_added:
            added.append(flags)
        label = description.get("name") if isinstance(description.get("name"), str) else name
        where = description.get("where") if isinstance(description.get("where"), str) else ""
        display = item_names.get(item) if isinstance(item_names.get(item), str) else item
        checks.append(
            Check(
                location=name,
                label=label,
                where=where,
                area=place.area if place else OTHER_AREA,
                dungeon=place.dungeon if place else None,
                kind=kind,
                item=item,
                item_label=display,
                method=method,
                flags=flags,
                hashes=hashes,
                reason=reason,
            )
        )
    if unplaced:
        warnings.append(
            f"{unplaced} of the seed's checks are not in this version's world data; they show under {OTHER_AREA!r}."
        )
    counts = _count(placements, places)
    settings = spoiler.get("settings") if isinstance(spoiler.get("settings"), dict) else {}
    digest = manifest.get("output_sha256")
    metadata = {
        "seed": spoiler.get("seed") if type(spoiler.get("seed")) is int else None,
        "settings_string": spoiler.get("settings_string") if isinstance(spoiler.get("settings_string"), str) else None,
        "generator": generator,
        "tracker_version": reading,
        "layout": layout,
        "root": str(root),
        "seed_dir": str(seed_dir),
        "output_sha256": digest if isinstance(digest, str) else None,
        "short_hash": digest[:12].upper() if isinstance(digest, str) and len(digest) == 64 else None,
        "dungeon_items": settings.get("dungeon_items") if isinstance(settings.get("dungeon_items"), str) else None,
        "shuffle": [s for s in settings.get("shuffle", []) if isinstance(s, str)]
        if isinstance(settings.get("shuffle"), list)
        else [],
        "checks": len(checks),
    }
    user = root / "user"
    user_path = user if layout in ("ui", "pack") or user.is_dir() else None
    return Seed(
        root=root,
        seed_dir=seed_dir,
        spoiler_path=spoiler_path,
        user_path=user_path,
        layout=layout,
        metadata=metadata,
        checks=tuple(checks),
        small_keys=counts["Small Key"],
        boss_keys=counts["Boss Key"],
        maps=counts["Map"],
        compasses=counts["Compass"],
        added_flags=tuple(added),
        warnings=tuple(warnings),
    )
