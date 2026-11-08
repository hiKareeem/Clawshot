"""Gifts through the event flows: make a gift check give another item (plans/03-game-data.md sections 15 and 19).

    rules = load()                                            # gift_rules.toml: each check's class and edits
    changes = plan({"LLR Talons Chickens": "Item_Boomerang"}, scan_gifts(romfs), definitions.load(), rules)
    transforms = file_changes(changes, flow_paths)            # romfs path -> decompressed bytes -> bytes

A gift check is the census gift steps that share one OoT Randomizer name (a tier pick or two code paths give one check
in two steps). Every step's item parameter gets the new item. A ``rewrite`` check also has its "already given" reads of
the vanilla item (``IsGet.<item>``) turned into reads of the check's own flag, and the steps listed in ``skip`` taken
out of the flow (their predecessors point at their ``next``). The flag is an existing one the game sets once the check
is given (``flag`` in the rules) or, as a last resort, a saved Bool the patch adds to ``GameDataList`` and sets right
after each step. A ``more`` check cannot be changed yet.

The transforms take and return decompressed files, so they compose with the other kinds' changes to the same file
(``clawshot.patch.write``); each one refuses a file that does not hold what the census and the rules say, and checks
the file it writes reads back as the changed tree. New events are appended, so every existing event keeps its index.
"""

import tomllib
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from clawshot.census import definitions as census_definitions
from clawshot.census.definitions import Definition
from clawshot.census.gifts import FLOW_VERSIONS, Gift, flow_files, scan_gifts
from clawshot.census.scan import CHEST, read_romfs_byml, scan
from clawshot.formats import byml, evfl, zsdic
from clawshot.formats.byml import I32, U32
from clawshot.generate import Settings, prepare
from clawshot.patch import items as item_actors
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.patch.items import ItemActors
from clawshot.patch.plan import PatchError
from clawshot.save import TYPES, murmur3_32
from clawshot.settings import CATALOG, DEFAULTS
from clawshot.world.model import World

RULES_TOML = Path(__file__).with_name("gift_rules.toml")
SWAP, REWRITE, MORE = "swap", "rewrite", "more"
CLASSES = (SWAP, REWRITE, MORE)
FLAG_PREFIX = "Clawshot.Gift."
FIELDS = {"class", "gate", "given", "flag", "skip", "reason", "writes"}

GAME_DATA_ACTOR = "GameDataActor"
READ_QUERY = "EventQueryIsGameDataBool"
SET_ACTION = "EventTriggerSetGameDataBool"
NEW_EVENT_PREFIX = "ClawshotGift"

# GameDataList: a saved story flag as the game's own (9338 of its Bools), and the save layout it implies.
FLAG_RESET_TYPE = 8
SAVE_FILE = 0  # progress.sav
ENTRY_SIZE = 8  # one (key, value) pair in a save's entry table
SAVE_HEADER = 0x20
UNSAVED_TYPES = ("BoolExp", "Struct")  # computed or runtime only: in no save table
BOOL64 = "Bool64bitKey"  # one pair in the table; its keys live in the data area


class GiftPatchError(PatchError):
    pass


@dataclass(frozen=True)
class Rule:
    check: str  # the OoT Randomizer name
    cls: str
    gate: str = ""
    given: tuple[str, ...] = ()  # "<flow>/<event>" reads that mean "given"
    flag: str | None = None  # an existing flag the game sets once the check is given
    skip: tuple[str, ...] = ()  # "<flow>/<event>" steps taken out
    reason: str = ""
    writes: tuple[str, ...] = ()  # vanilla IsGet writes redirected to an existing check-completion flag


def _ref(check: str, value: object) -> str:
    if not isinstance(value, str) or value.count("/") != 1 or not all(value.split("/")):
        raise GiftPatchError(f"{check}: {value!r} is not '<flow>/<event>'")
    return value


def loads(text: str) -> dict[str, Rule]:
    rules = {}
    for check, entry in tomllib.loads(text).get("check", {}).items():
        unknown = set(entry) - FIELDS
        if unknown:
            raise GiftPatchError(f"{check}: unknown fields {sorted(unknown)}")
        cls = entry.get("class")
        if cls not in CLASSES:
            raise GiftPatchError(f"{check}: class {cls!r}, expected one of {CLASSES}")
        rule = Rule(
            check,
            cls,
            entry.get("gate", ""),
            tuple(_ref(check, r) for r in entry.get("given", [])),
            entry.get("flag"),
            tuple(_ref(check, r) for r in entry.get("skip", [])),
            entry.get("reason", ""),
            tuple(_ref(check, r) for r in entry.get("writes", [])),
        )
        if (rule.given or rule.skip or rule.flag or rule.writes) and cls != REWRITE:
            raise GiftPatchError(f"{check}: given, flag, skip and writes belong to class {REWRITE!r}, not {cls!r}")
        if cls == REWRITE and not (rule.given or rule.skip or rule.writes):
            raise GiftPatchError(f"{check}: class {REWRITE!r} with nothing to rewrite")
        if rule.flag is not None and not (rule.given or rule.writes):
            raise GiftPatchError(f"{check}: a flag without reads or writes to rewrite")
        if rule.writes and (not isinstance(rule.flag, str) or not rule.flag.startswith("HavePlayedEvent.")):
            raise GiftPatchError(f"{check}: writes need an existing per-check event completion flag")
        if cls == MORE and not rule.reason:
            raise GiftPatchError(f"{check}: class {MORE!r} needs a reason")
        rules[check] = rule
    return rules


def load(path: str | Path = RULES_TOML) -> dict[str, Rule]:
    return loads(Path(path).read_text(encoding="utf-8"))


@dataclass(frozen=True)
class GiftChange:
    rule: Rule
    steps: tuple[Gift, ...]
    item: str  # the actor name the check gives now

    @property
    def check(self) -> str:
        return self.rule.check

    @property
    def flag(self) -> str | None:
        """The flag the check's "given" reads read, or None when it has none."""
        if not (self.rule.given or self.rule.writes):
            return None
        return self.rule.flag or FLAG_PREFIX + self.steps[0].id.replace("/", ".")

    @property
    def new_flag(self) -> str | None:
        """The flag the patch adds to GameDataList and sets after each step, or None."""
        return self.flag if self.rule.given and self.rule.flag is None else None


def check_steps(gifts: Iterable[Gift], definitions: Iterable[Definition]) -> dict[str, tuple[Gift, ...]]:
    """OoT Randomizer name -> the census gift steps linked to it, in census order."""
    name_of = {d.id: d.oot_randomizer_name for d in definitions if isinstance(d.id, str) and d.oot_randomizer_name}
    out: dict[str, list[Gift]] = {}
    for gift in gifts:
        if gift.id in name_of:
            out.setdefault(name_of[gift.id], []).append(gift)
    return {name: tuple(steps) for name, steps in out.items()}


def plan(
    placements: Mapping[str, str],
    gifts: Iterable[Gift],
    definitions: Iterable[Definition],
    rules: Mapping[str, Rule],
) -> list[GiftChange]:
    """The changes for ``placements`` (OoT Randomizer name of a gift check -> item actor), sorted by check."""
    steps = check_steps(gifts, definitions)
    out = []
    for check in sorted(placements):
        if check not in steps:
            raise GiftPatchError(f"{check}: no census gift step is linked to it")
        rule = rules.get(check)
        if rule is None:
            raise GiftPatchError(f"{check}: no rule in gift_rules.toml")
        if rule.cls == MORE:
            raise GiftPatchError(f"{check}: cannot be changed yet ({rule.reason})")
        out.append(GiftChange(rule, steps[check], placements[check]))
    return out


# --- flows --------------------------------------------------------------------------------------------------------


def _index(fc: evfl.Flowchart, flow: str, event: str) -> int:
    for i, e in enumerate(fc.events):
        if e.name == event:
            return i
    raise GiftPatchError(f"{flow}: no event {event}")


def _slot(names: list[str], name: str) -> int:
    if name not in names:
        names.append(name)
    return names.index(name)


def _game_data_actor(fc: evfl.Flowchart, flow: str) -> int:
    found = [i for i, a in enumerate(fc.actors) if a.name == GAME_DATA_ACTOR and not a.secondary_name]
    if len(found) != 1:
        raise GiftPatchError(f"{flow}: {len(found)} {GAME_DATA_ACTOR} actors, expected one")
    return found[0]


def _set_item(fc: evfl.Flowchart, step: Gift, item: str) -> None:
    event = fc.events[_index(fc, step.flow, step.event)]
    params = getattr(event, "params", None) or {}
    if params.get(step.param) != step.vanilla_item or isinstance(params.get(step.param), evfl.Argument):
        raise GiftPatchError(
            f"{step.id}: {step.param} is {params.get(step.param)!r}, the census said {step.vanilla_item!r}"
        )
    params[step.param] = item


def _set_flag_after(fc: evfl.Flowchart, step: Gift, flag: str) -> None:
    i = _index(fc, step.flow, step.event)
    event = fc.events[i]
    if not isinstance(event, evfl.ActionEvent | evfl.SubFlowEvent):
        raise GiftPatchError(f"{step.id}: a {type(event).__name__} has no single next event to follow")
    actor = _game_data_actor(fc, step.flow)
    action = _slot(fc.actors[actor].actions, SET_ACTION)
    names = {e.name for e in fc.events}
    n = sum(1 for name in names if name.startswith(NEW_EVENT_PREFIX))
    while f"{NEW_EVENT_PREFIX}{n}" in names:
        n += 1
    params = {"GameDataName": flag, "Index": -1, "Value": True}
    fc.events.append(evfl.ActionEvent(f"{NEW_EVENT_PREFIX}{n}", actor, action, event.next, params))
    event.next = len(fc.events) - 1


def _read_flag(fc: evfl.Flowchart, flow: str, ref: str, vanilla: set[str], flag: str) -> None:
    event = fc.events[_index(fc, flow, ref.split("/")[1])]
    if not isinstance(event, evfl.SwitchEvent):
        raise GiftPatchError(f"{ref}: a {type(event).__name__}, not a query")
    actor = fc.actors[event.actor]
    query = actor.queries[event.query]
    name = (event.params or {}).get("GameDataName")
    if (actor.name, query) != (GAME_DATA_ACTOR, READ_QUERY) or name not in {f"IsGet.{v}" for v in vanilla}:
        raise GiftPatchError(f"{ref}: {actor.name}.{query} on {name!r}, not a read of IsGet of {sorted(vanilla)}")
    event.params["GameDataName"] = flag


def _redirect_write(fc: evfl.Flowchart, flow: str, ref: str, vanilla: set[str], flag: str) -> None:
    event = fc.events[_index(fc, flow, ref.split("/")[1])]
    params = getattr(event, "params", None) or {}
    if not isinstance(event, evfl.ActionEvent):
        raise GiftPatchError(f"{ref}: not an inventory Bool write")
    actor = fc.actors[event.actor]
    if (
        actor.name != GAME_DATA_ACTOR
        or actor.actions[event.action] != SET_ACTION
        or params.get("GameDataName") not in {"IsGet." + item for item in vanilla}
        or params.get("Value") is not True
    ):
        raise GiftPatchError(f"{ref}: not a true write of the vanilla item's IsGet: {params}")
    params["GameDataName"] = flag


def _skip(fc: evfl.Flowchart, flow: str, ref: str) -> None:
    i = _index(fc, flow, ref.split("/")[1])
    event = fc.events[i]
    if not isinstance(event, evfl.ActionEvent | evfl.SubFlowEvent) or event.next == evfl.NONE:
        raise GiftPatchError(f"{ref}: only a step with a next event can be skipped")
    target, found = event.next, 0
    for e in fc.events:
        if getattr(e, "next", None) == i:
            e.next, found = target, found + 1
        if isinstance(e, evfl.SwitchEvent | evfl.SubFlowSwitchEvent):
            for k, (value, to) in enumerate(e.cases):
                if to == i:
                    e.cases[k], found = (value, target), found + 1
        if isinstance(e, evfl.ForkEvent):
            for k, to in enumerate(e.forks):
                if to == i:
                    e.forks[k], found = target, found + 1
    for entry in fc.entry_points:
        if entry.main_event == i:
            entry.main_event, found = target, found + 1
    if not found:
        raise GiftPatchError(f"{ref}: nothing leads to it")


def patch_flowchart(fc: evfl.Flowchart, flow: str, changes: Sequence[GiftChange]) -> None:
    """Apply ``changes``' edits that fall in ``flow`` to its flowchart, in place."""
    for change in changes:
        vanilla = {step.vanilla_item for step in change.steps}
        for step in change.steps:
            if step.flow == flow:
                _set_item(fc, step, change.item)
                if change.new_flag:
                    _set_flag_after(fc, step, change.new_flag)
        for ref in change.rule.given:
            if ref.split("/")[0] == flow:
                _read_flag(fc, flow, ref, vanilla, change.flag)
        for ref in change.rule.writes:
            if ref.split("/")[0] == flow:
                _redirect_write(fc, flow, ref, vanilla, change.flag)
        for ref in change.rule.skip:
            if ref.split("/")[0] == flow:
                _skip(fc, flow, ref)


def flows_changed(changes: Iterable[GiftChange]) -> list[str]:
    out = set()
    for change in changes:
        out |= {step.flow for step in change.steps}
        out |= {ref.split("/")[0] for ref in (*change.rule.given, *change.rule.skip, *change.rule.writes)}
    return sorted(out)


def flow_transform(flow: str, changes: Sequence[GiftChange]) -> Callable[[bytes], bytes]:
    def transform(data: bytes) -> bytes:
        tree = evfl.read(data)
        if tree.flowchart is None or tree.flowchart.name != flow:
            raise GiftPatchError(f"{flow}: the file holds no flowchart of that name")
        patch_flowchart(tree.flowchart, flow, changes)
        out = evfl.write(tree)
        if evfl.read(out) != tree:
            raise GiftPatchError(f"{flow}: the written flow does not read back as the changed tree")
        return out

    return transform


# --- GameDataList -------------------------------------------------------------------------------------------------


def _table_end(data: Mapping, keep: Callable[[str, Mapping], bool]) -> int:
    pairs = sum(1 for t, entries in data.items() if t != BOOL64 for e in entries if keep(t, e))
    return SAVE_HEADER + ENTRY_SIZE * (pairs + 1 + len(TYPES))


def add_flags(tree: Mapping, names: Sequence[str]) -> None:
    """Add a saved Bool per name to a parsed GameDataList, in place, and grow the save layout its MetaData gives:
    progress.sav's entry table (``SaveDataOffsetPos[0]``, ``SaveDataSize[0]``) and the table of every saved entry
    (``AllDataSaveOffset``, ``AllDataSaveSize``), each by one (key, value) pair per flag."""
    data, meta = tree["Data"], tree["MetaData"]
    file_end = _table_end(data, lambda t, e: int(e["SaveFileIndex"]) == SAVE_FILE)
    all_end = _table_end(data, lambda t, e: t not in UNSAVED_TYPES)
    if (int(meta["SaveDataOffsetPos"][SAVE_FILE]), int(meta["AllDataSaveOffset"])) != (file_end, all_end):
        raise GiftPatchError(
            f"GameDataList MetaData table ends {int(meta['SaveDataOffsetPos'][SAVE_FILE])}, "
            f"{int(meta['AllDataSaveOffset'])}; its entries give {file_end}, {all_end}"
        )
    taken = {int(e["Hash"]) for entries in data.values() for e in entries}
    new = []
    for name in names:
        key = murmur3_32(name.encode("utf-8"))
        if key in taken:
            raise GiftPatchError(f"GameDataList already has an entry hashed like {name!r} ({key})")
        taken.add(key)
        new.append(
            {"DefaultValue": False, "Hash": U32(key), "ResetTypeValue": I32(FLAG_RESET_TYPE), "SaveFileIndex": I32(0)}
        )
    data["Bool"].extend(new)
    grow = ENTRY_SIZE * len(new)
    for key in ("SaveDataOffsetPos", "SaveDataSize"):
        meta[key][SAVE_FILE] = I32(int(meta[key][SAVE_FILE]) + grow)
    for key in ("AllDataSaveOffset", "AllDataSaveSize"):
        meta[key] = I32(int(meta[key]) + grow)


def game_data_transform(names: Sequence[str]) -> Callable[[bytes], bytes]:
    def transform(data: bytes) -> bytes:
        document = byml.load(data)
        add_flags(document.root, names)
        out = byml.dump(document)
        if (d := byml.difference(document.root, byml.read(out))) is not None:
            raise GiftPatchError(f"{GAME_DATA_LIST}: the written file does not read back as the changed tree: {d}")
        return out

    return transform


def file_changes(changes: Sequence[GiftChange], files: Mapping[str, str]) -> dict[str, Callable[[bytes], bytes]]:
    """The transforms of the files ``changes`` touch (``files``: flow name -> romfs path of the flow the game
    loads), for ``clawshot.patch.write``."""
    out = {}
    for flow in flows_changed(changes):
        if flow not in files:
            raise GiftPatchError(f"{flow}: no flow file")
        out[files[flow]] = flow_transform(flow, changes)
    names = [change.new_flag for change in changes if change.new_flag]
    if names:
        out[GAME_DATA_LIST] = game_data_transform(names)
    return out


# --- seeds --------------------------------------------------------------------------------------------------------

GIFT_TYPES = ("NPC", "Song", "Cutscene", "Boss")  # the world's location types of event gifts (OoT Randomizer's)
SHUFFLE = "Gift"  # the --shuffle value
SONG_TYPE = "Song"
FREE_TIME_TRAVEL = "free_time_travel"  # the world setting that lifts the anchors
# Gift checks a seed keeps vanilla while adult Link cannot go back freely: the adult-return guarantee (D20) relies on
# them (Saria's Song -> Darunia's Joy gives the child the Goron Bracelet; shuffled strength upgrades are placed
# adult-only).
ANCHORS = {"GC Darunias Joy": "the child's Goron Bracelet anchors the adult-return guarantee (D20)"}


def seed_checks(
    world: World,
    gifts: Iterable[Gift],
    definitions: Iterable[Definition],
    rules: Mapping[str, Rule],
    actors: ItemActors,
) -> list[str]:
    """The world locations a gift shuffle may move, in world order: a gift check of class ``swap`` or ``rewrite``
    whose vanilla logic item's actor (``item_actors.toml``) is what every one of its steps gives, so the pool item it
    adds is the one it gave. A Great Fairy, given once through a new GameDataList flag, is one of them (Kareem, in
    game, 2026-11-08: the game keeps the flag and an older save loads; 03-game-data.md section 19). The
    :data:`ANCHORS` stay vanilla unless the world's ``free_time_travel`` setting is on."""
    steps = check_steps(gifts, definitions)
    free = world.settings.get(FREE_TIME_TRAVEL) is True
    out = []
    for name, loc in world.locations.items():
        rule = rules.get(name)
        if loc.type not in GIFT_TYPES or name not in steps or rule is None or rule.cls == MORE:
            continue
        if loc.vanilla is None or loc.n64_only is not None or loc.keep_vanilla is not None:
            continue
        if name in ANCHORS and not free:
            continue
        if {s.vanilla_item for s in steps[name]} != {actors.actors.get(loc.vanilla)}:
            continue
        out.append(name)
    return out


def restrict_spec(spec: Mapping[str, Any], shuffled: Iterable[str]) -> dict[str, Any]:
    """A copy of the world spec in which every gift-type location outside ``shuffled`` keeps its vanilla item."""
    keep = set(shuffled)
    locations = {}
    for name, info in spec["locations"].items():
        if info.get("type") in GIFT_TYPES and name not in keep and not info.get("keep_vanilla"):
            info = {
                **info,
                "keep_vanilla": "gift shuffle: not changeable yet (gift_rules.toml, plans/03-game-data.md section 19)",
            }
        locations[name] = info
    return {**spec, "locations": locations}


def seed_step(
    shuffled: Sequence[str],
    gifts: Iterable[Gift],
    definitions: Iterable[Definition],
    rules: Mapping[str, Rule],
    actors: ItemActors,
    vanilla: Mapping[str, str],
    files: Mapping[str, str],
) -> Callable[[Mapping[str, str]], dict[str, Callable[[bytes], bytes]]]:
    """The seed's patch step for gifts: placements (location -> logic item) in, the flow and GameDataList
    transforms out, for every shuffled gift location whose item changed (``vanilla``: location -> its logic item)."""
    gifts, definitions = list(gifts), list(definitions)

    def step(placements: Mapping[str, str]) -> dict[str, Callable[[bytes], bytes]]:
        moved = {name: actors.actor(placements[name]) for name in shuffled if placements[name] != vanilla[name]}
        return file_changes(plan(moved, gifts, definitions, rules), files)

    return step


def seed_setup(
    romfs: str | Path, spec: Mapping[str, Any], settings: Settings
) -> tuple[dict[str, Any], Settings, Callable[[Mapping[str, str]], dict[str, Callable[[bytes], bytes]]]]:
    """For ``--shuffle Gift``: the spec with the gifts that cannot move held vanilla, the settings shuffling the
    gift types in place of ``Gift`` and a placement policy from ``settings.songs`` plus the verified chest
    actor list in ``data/settings.toml``), and the patch step to pass to ``make_seed``."""
    settings = replace(
        settings,
        shuffle=tuple(dict.fromkeys(t for s in settings.shuffle for t in (GIFT_TYPES if s == SHUFFLE else (s,)))),
    )
    census, definitions = scan_gifts(romfs), census_definitions.load()
    rules, actors = load(), item_actors.load()
    _, world = prepare(spec, settings)
    shuffled = seed_checks(world, census, definitions, rules, actors)
    vanilla = {name: world.locations[name].vanilla for name in shuffled}
    chest_actors = {loc.vanilla_item for loc in scan(romfs) if loc.kind == CHEST}
    held = held_items(world, vanilla.values(), actors, chest_actors, songs=settings.songs)
    songs = (SONG_TYPE,) if settings.songs == "song" else ()
    settings = replace(
        settings,
        # Rebuild the derived gift restrictions when replaying an effective spoiler string or changing songs.
        item_location_types={
            **{k: v for k, v in settings.item_location_types.items() if k not in vanilla.values()},
            **held,
        },
        exclusive_location_types=tuple(t for t in settings.exclusive_location_types if t != SONG_TYPE) + songs,
    )
    dicts = zsdic.Dictionaries.from_romfs(Path(romfs))
    versions = {str(k): str(v) for k, v in read_romfs_byml(Path(romfs), dicts, FLOW_VERSIONS)["Versions"].items()}
    files = flow_files(Path(romfs), versions)
    step = seed_step(shuffled, census, definitions, rules, actors, vanilla, files)
    return restrict_spec(spec, shuffled), settings, step


def held_items(
    world: World, items: Iterable[str], actors: ItemActors, chest_actors: set[str], *, songs: str = DEFAULTS["songs"]
) -> dict[str, tuple[str, ...]]:
    """Songs-on-songs by default; anywhere releases the whole song family (reviewer, Round 6).

    The other eleven songs are inferred from the Song of Storms chest result, not individually verified.
    Non-song gifts still need a vanilla chest actor or a sourced ``chest_verified`` catalog entry.
    """
    out = {}
    for item in items:
        if world.items[item].type == SONG_TYPE:
            if songs == "song":
                out[item] = (SONG_TYPE,)
        elif actors.actor(item) not in chest_actors and actors.actor(item) not in CATALOG["chest_verified"]:
            out[item] = tuple(t for t in GIFT_TYPES if songs == "anywhere" or t != SONG_TYPE)
    return dict(sorted(out.items()))
