"""Gifts through the event flows: make a gift check give another item (plans/03-game-data.md sections 19 and 28).

    rules = load()                                            # gift_rules.toml: each check's class and edits
    changes = plan({"LLR Talons Chickens": "Item_Boomerang"}, scan_gifts(romfs), definitions.load(), rules)
    transforms = file_changes(changes, flow_paths)            # romfs path -> decompressed bytes -> bytes

A gift check is the census gift steps that share one OoT Randomizer name (a tier pick or two code paths give one check
in two steps). Every step's item parameter gets the new item. A ``rewrite`` check also has its "already given" reads of
the vanilla item (``IsGet.<item>``) turned into reads of the check's own flag, and the steps listed in ``skip`` taken
out of the flow (their predecessors point at their ``next``). The flag is an existing one the game sets once the check
is given (``flag`` in the rules) or, as a last resort, a saved Bool the patch adds to ``GameDataList`` and sets right
after each step. A ``more`` check cannot be changed yet.
The remake-only shopkeeper check groups its two stable grant IDs explicitly. Its ``once`` gate replaces the
equipped-shield test with a saved Bool, set after both grants even when the shuffled reward stays a shield.

The transforms take and return decompressed files, so they compose with the other kinds' changes to the same file
(``clawshot.patch.write``); each one refuses a file that does not hold what the census and the rules say, and checks
the file it writes reads back as the changed tree. New events are appended, so every existing event keeps its index.
"""

import tomllib
from collections.abc import Callable, Iterable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from clawshot import progressive
from clawshot.census import definitions as census_definitions
from clawshot.census import event_items
from clawshot.census.definitions import Definition
from clawshot.census.gifts import (
    DIRECT,
    FLOW_VERSIONS,
    FROG_SONG_CALL,
    FROG_SONG_FLAGS,
    GALLERY_EXPERT_CALL,
    GALLERY_EXPERT_RUPEES,
    Gift,
    _successors,
    flow_files,
    reachable,
    scan_gifts,
)
from clawshot.census.scan import CHEST, read_romfs_byml, scan
from clawshot.formats import byml, evfl, zsdic
from clawshot.formats.byml import I32, U32
from clawshot.generate import Settings, prepare
from clawshot.generate import tokens as token_policy
from clawshot.patch import bags
from clawshot.patch import items as item_actors
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.patch.items import ItemActors
from clawshot.patch.key_targets import DUNGEON_TARGETS, DungeonGrant
from clawshot.patch.plan import PatchError
from clawshot.save import TYPES, murmur3_32
from clawshot.settings import CATALOG, DEFAULTS
from clawshot.world.model import World

RULES_TOML = Path(__file__).with_name("gift_rules.toml")
SWAP, REWRITE, MORE = "swap", "rewrite", "more"
CLASSES = (SWAP, REWRITE, MORE)
FLAG_PREFIX = "Clawshot.Gift."
FIELDS = {"class", "gate", "given", "flag", "skip", "reason", "writes", "once", "purchase", "track", "display"}
# Tracker-only native once-flags (spec tracker-auto-checks D1, D6): the patch never reads them.
TRACK_KINDS = ("bool", "played", "quest")
TRACK_FIELDS = {*TRACK_KINDS, "step", "source", "accepted", "played_by"}

GAME_DATA_ACTOR = "GameDataActor"
READ_QUERY = "EventQueryIsGameDataBool"
SET_ACTION = "EventTriggerSetGameDataBool"
NEW_EVENT_PREFIX = "ClawshotGift"

# Two already-censused branches of one remake-only check; no invented OoTR link (section 28).
SHOPKEEPER_CHECK = "KF Shopkeeper Gift"
SHOPKEEPER_FLOW = "Npc_Kokiri_001_Shop_Child"
SHOPKEEPER_STEPS = tuple(f"{SHOPKEEPER_FLOW}/{event}" for event in ("Event116", "Event117"))
SHOPKEEPER_REGION = "KF Kokiri Shop"

MARKET_BOTTLE_CHECK = "Market Potion Shop Bottle"
MARKET_BOTTLE_FLOW = "Npc_Hylia_020_Shop_Child"
MARKET_BOTTLE_STEP = f"{MARKET_BOTTLE_FLOW}/Event171"
MARKET_BOTTLE_FLAG = "Npc_Hylia_020_Shop_Item_Bottle_Present"

BOWLING_FLOW = "MiniGame_BombchuBowling"
BOWLING_FIRST = "Market Bombchu Bowling First Prize"
BOWLING_SECOND = "Market Bombchu Bowling Second Prize"
BOWLING_CHECKS = (BOWLING_FIRST, BOWLING_SECOND)

SKULL_KID_CHECK = "LW Ocarina Memory Game"
SKULL_KID_FLOW = "Npc_SkullKid_Child_02"
SKULL_KID_FLAG = "Minigame_SkullKidSession_IsGetHeartPiece"

DAMPE_CHECK = "Graveyard Dampe Gravedigging Tour"
DAMPE_FLAG = "GraveYard_DiggingHoleTour_Drop_HeartPiece"

GALLERY_EXPERT_CHECKS = {
    "Event202": "Market Shooting Gallery Expert Reward",
    "Event599": "Kak Shooting Gallery Expert Reward",
}
GALLERY_EXPERT_ROUTES = {
    "Event202": ("Event445", "Event448", "Event411"),
    "Event599": ("Event449", "Event452", "Event413"),
}
VARIABLE_RUPEE_CALLS = (FROG_SONG_CALL, GALLERY_EXPERT_CALL)

# Sale calls need their flag inside the success branch, not after a wrapper that can refuse.
MERCHANT_SHOPS = {
    "GC Medigoron": ("SimpleShopRoot_Npc_Goron_Medigoron_Adult", "Event119"),
    "Wasteland Bombchu Salesman": ("SimpleShopRoot", "Event150"),
}
GRANNY_CHECK = "Kak Granny Buy Blue Potion"
# A refill is not a bottle-container prize. Keep one ordinary, already-supported junk copy in the pool.
GRANNY_POOL_ITEM = "Rupees (5)"
ANALYZED = "RSDB/GameAnalyzedEventInfo.Product.111.rstbl.byml.zs"

# Merchant stock actors identify native sources, not the generic gift's payout actor.
# Keep this local: Shop_BombchuBundle_01 still means Buy Bombchu (10) in ordinary shops.
_MERCHANT_SOURCE_ACTORS = {
    "Item_Sword_Giant": "Shop_Sword_Giant",
    "Item_BombchuBundle_Medium": "Shop_BombchuBundle_01",
}

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
class TrackEntry:
    """A native flag the tracker reads to see that a gift was given (spec tracker-auto-checks D1, D6).

    ``bool`` reads the saved Bool ``name``, ``played`` reads ``HavePlayedEvent.<name>``, ``quest`` reads the enum
    ``Step_<name>`` against ``step``. ``accepted`` only after a recorded maintainer run (``played_by``, D2)."""

    kind: str
    name: str
    step: str | None
    source: str
    accepted: bool
    played_by: str | None


@dataclass(frozen=True)
class Rule:
    check: str  # the world check name (OoTR or remake-only)
    cls: str
    gate: str = ""
    given: tuple[str, ...] = ()  # "<flow>/<event>" reads that mean "given"
    flag: str | None = None  # an existing flag the game sets once the check is given
    skip: tuple[str, ...] = ()  # "<flow>/<event>" steps taken out
    reason: str = ""
    writes: tuple[str, ...] = ()  # vanilla IsGet writes redirected to an existing check-completion flag
    once: tuple[str, ...] = ()  # equipped-shield queries replaced by saved check-completion queries
    purchase: bool = False  # specialize a native sale and save completion only after its grant
    track: tuple[TrackEntry, ...] = ()  # tracker only; the patch ignores it (D1)
    # "<flow>/<event>" display-only get windows and Zelda's Notes targets naming the check's item (event-items 1.1)
    display: tuple[str, ...] = ()


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _track(check: str, value: object) -> tuple[TrackEntry, ...]:
    if not isinstance(value, list) or not value:
        raise GiftPatchError(f"{check}: track must be a list of one or more entries")
    out = []
    for entry in value:
        if not isinstance(entry, dict):
            raise GiftPatchError(f"{check}: track entry {entry!r} is not a table")
        unknown = set(entry) - TRACK_FIELDS
        if unknown:
            raise GiftPatchError(f"{check}: unknown track fields {sorted(unknown)}")
        kinds = [kind for kind in TRACK_KINDS if kind in entry]
        if len(kinds) != 1:
            raise GiftPatchError(f"{check}: a track entry needs exactly one of {TRACK_KINDS}, not {kinds}")
        kind = kinds[0]
        if not _nonempty(entry[kind]):
            raise GiftPatchError(f"{check}: track {kind} must be a non-empty name")
        step = entry.get("step")
        if kind == "quest" and not _nonempty(step):
            raise GiftPatchError(f"{check}: a track quest needs a step")
        if kind != "quest" and "step" in entry:
            raise GiftPatchError(f"{check}: step belongs only to a quest track entry")
        if not _nonempty(entry.get("source")):
            raise GiftPatchError(f"{check}: a track entry needs a non-empty source")
        accepted = entry.get("accepted")
        if type(accepted) is not bool:
            raise GiftPatchError(f"{check}: track accepted must be a Bool")
        played_by = entry.get("played_by")
        if played_by is not None and not _nonempty(played_by):
            raise GiftPatchError(f"{check}: track played_by must be a non-empty string")
        if accepted and played_by is None:
            raise GiftPatchError(f"{check}: an accepted track entry needs played_by (who, which build, date)")
        out.append(TrackEntry(kind, entry[kind], step, entry["source"], accepted, played_by))
    return tuple(out)


def _ref(check: str, value: object) -> str:
    if not isinstance(value, str) or value.count("/") != 1 or not all(value.split("/")):
        raise GiftPatchError(f"{check}: {value!r} is not '<flow>/<event>'")
    return value


def _adds_flag(check: str, rule: Rule) -> bool:
    """Whether the patch adds a ``Clawshot.Gift.*`` flag for this rule (:attr:`GiftChange.new_flag` at load time)."""
    return rule.flag is None and bool(
        rule.given or rule.once or rule.purchase or check in GALLERY_EXPERT_CHECKS.values()
    )


def loads(text: str) -> dict[str, Rule]:
    rules = {}
    for check, entry in tomllib.loads(text).get("check", {}).items():
        unknown = set(entry) - FIELDS
        if unknown:
            raise GiftPatchError(f"{check}: unknown fields {sorted(unknown)}")
        cls = entry.get("class")
        if cls not in CLASSES:
            raise GiftPatchError(f"{check}: class {cls!r}, expected one of {CLASSES}")
        displays = entry.get("display", [])
        if not isinstance(displays, list) or any(not isinstance(ref, str) for ref in displays):
            raise GiftPatchError(f"{check}: display must be a list of '<flow>/<event>' references")
        rule = Rule(
            check,
            cls,
            entry.get("gate", ""),
            tuple(_ref(check, r) for r in entry.get("given", [])),
            entry.get("flag"),
            tuple(_ref(check, r) for r in entry.get("skip", [])),
            entry.get("reason", ""),
            tuple(_ref(check, r) for r in entry.get("writes", [])),
            tuple(_ref(check, r) for r in entry.get("once", [])),
            entry.get("purchase", False),
            _track(check, entry["track"]) if "track" in entry else (),
            tuple(_ref(check, ref) for ref in displays),
        )
        if len(set(rule.display)) != len(rule.display):
            raise GiftPatchError(f"{check}: duplicate display reference")
        if rule.display and cls == MORE:
            raise GiftPatchError(f"{check}: display belongs to a changeable gift")
        if type(rule.purchase) is not bool:
            raise GiftPatchError(f"{check}: purchase must be a Bool")
        if (rule.given or rule.skip or rule.flag or rule.writes or rule.once or rule.purchase) and cls != REWRITE:
            raise GiftPatchError(f"{check}: rewrite fields belong to class {REWRITE!r}, not {cls!r}")
        if cls == REWRITE and not (rule.given or rule.skip or rule.writes or rule.once or rule.purchase):
            raise GiftPatchError(f"{check}: class {REWRITE!r} with nothing to rewrite")
        if rule.flag is not None and not (rule.given or rule.writes or rule.once or rule.purchase):
            raise GiftPatchError(f"{check}: a flag without reads or writes to rewrite")
        if rule.purchase and check not in (*MERCHANT_SHOPS, GRANNY_CHECK):
            raise GiftPatchError(f"{check}: no native purchase specialization")
        if rule.writes and (not isinstance(rule.flag, str) or not rule.flag.startswith("HavePlayedEvent.")):
            raise GiftPatchError(f"{check}: writes need an existing per-check event completion flag")
        if cls == MORE and rule.display:
            raise GiftPatchError(f"{check}: class {MORE!r} is never shuffled, so it has no display")
        if cls == MORE and not rule.reason:
            raise GiftPatchError(f"{check}: class {MORE!r} needs a reason")
        if rule.track:
            # 1.2: the tracker already reads these; a second, native record would be a competing source.
            if cls == MORE:
                raise GiftPatchError(f"{check}: class {MORE!r} is never shuffled, so it has no track")
            if rule.flag is not None:
                raise GiftPatchError(f"{check}: track beside a flag ({rule.flag}); the tracker reads the flag")
            if _adds_flag(check, rule):
                raise GiftPatchError(f"{check}: track on a check with an added {FLAG_PREFIX}* flag")
        rules[check] = rule
    return rules


def load(path: str | Path = RULES_TOML) -> dict[str, Rule]:
    return loads(Path(path).read_text(encoding="utf-8"))


@dataclass(frozen=True)
class GiftChange:
    rule: Rule
    steps: tuple[Gift, ...]
    item: str  # native grant actor; plan resolves tunic shelf displays to their Obj_ gift actors
    dungeon_grant: DungeonGrant | None = None

    @property
    def check(self) -> str:
        return self.rule.check

    @property
    def flag(self) -> str | None:
        """The flag the check's "given" reads read, or None when it has none."""
        if not (self.rule.given or self.rule.writes or self.rule.once or self.rule.purchase or self.expert):
            return None
        return self.rule.flag or FLAG_PREFIX + self.steps[0].id.replace("/", ".")

    @property
    def new_flag(self) -> str | None:
        """The flag the patch adds to GameDataList and sets after each step, or None."""
        return (
            self.flag
            if (self.rule.given or self.rule.once or self.rule.purchase or self.expert) and self.rule.flag is None
            else None
        )

    @property
    def expert(self) -> bool:
        return any(s.call == GALLERY_EXPERT_CALL for s in self.steps)


def check_steps(gifts: Iterable[Gift], definitions: Iterable[Definition]) -> dict[str, tuple[Gift, ...]]:
    """World check name -> its census gift steps, including the remake-only shopkeeper, in census order."""
    name_of = {d.id: d.oot_randomizer_name for d in definitions if isinstance(d.id, str) and d.oot_randomizer_name}
    name_of.update({step: SHOPKEEPER_CHECK for step in SHOPKEEPER_STEPS})
    name_of[MARKET_BOTTLE_STEP] = MARKET_BOTTLE_CHECK
    name_of.update({f"MiniGame_HitTarget/{event}": name for event, name in GALLERY_EXPERT_CHECKS.items()})
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
        if check == SHOPKEEPER_CHECK and {step.id for step in steps[check]} != set(SHOPKEEPER_STEPS):
            raise GiftPatchError(f"{check}: expected both grant branches {SHOPKEEPER_STEPS}")
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


def _clone_entry(
    fc: evfl.Flowchart, entry: str, replacements: Mapping[str, evfl.Event], *, name: str | None = None
) -> str:
    """Specialize one call without changing shared callees or unrelated callers; retain native branches.

    Replacement edges use original indices. Only their reachable graph is copied, so replaced grant
    machinery does not leave dead copies. Native entry-local actors are not supported implicitly.
    """
    source = fc.entry_point(entry)
    original = reachable(fc, source.main_event)
    indices = {_index(fc, fc.name, name): event for name, event in replacements.items()}
    if not indices.keys() <= original:
        raise GiftPatchError(f"{fc.name}:{entry}: replacement is outside the native entry")
    seen, stack = set(), [source.main_event]
    while stack:
        index = stack.pop()
        if index != evfl.NONE and index not in seen:
            seen.add(index)
            stack.extend(_successors(indices.get(index, fc.events[index])))
    actors = {fc.events[i].actor for i in seen if isinstance(fc.events[i], evfl.ActionEvent | evfl.SwitchEvent)}
    if any(fc.actors[i].entry_point != evfl.NONE for i in actors):
        raise GiftPatchError(f"{fc.name}:{entry}: entry-local actor needs an explicit binding")
    prefix = f"{NEW_EVENT_PREFIX}{len(fc.events)}_"
    name = name or prefix + entry
    if any(e.name == name for e in fc.entry_points):
        raise GiftPatchError(f"{fc.name}: duplicate specialized entry {name}")
    mapping = {index: len(fc.events) + n for n, index in enumerate(sorted(seen))}
    if len(fc.events) + len(mapping) >= evfl.NONE:
        raise GiftPatchError(f"{fc.name}: specialized graph exceeds the event-index limit")
    for index in sorted(seen):
        event = deepcopy(indices.get(index, fc.events[index]))
        event.name = prefix + fc.events[index].name
        if hasattr(event, "next") and event.next != evfl.NONE:
            event.next = mapping[event.next]
        if hasattr(event, "cases"):
            event.cases = [(case, mapping[target] if target != evfl.NONE else target) for case, target in event.cases]
        if isinstance(event, evfl.ForkEvent):
            event.forks = [mapping[target] for target in event.forks]
            event.join = mapping[event.join]
        fc.events.append(event)
    calls = [
        mapping[i]
        for i in sorted(seen)
        if isinstance(fc.events[mapping[i]], evfl.SubFlowEvent | evfl.SubFlowSwitchEvent)
    ]
    fc.entry_points.append(evfl.EntryPoint(name, mapping[source.main_event], calls, deepcopy(source.variables)))
    return name


def _frog_song(fc: evfl.Flowchart, step: Gift, item: str) -> None:
    call = fc.events[_index(fc, step.flow, step.event)]
    if (
        not isinstance(call, evfl.SubFlowEvent)
        or (call.flowchart or fc.name, call.entry_point) != ("MiniGame_FrogTenors", "TeachNewMusic")
        or (call.params or {}).get("GameDataName") != FROG_SONG_FLAGS.get(step.event)
        or isinstance((call.params or {}).get("GameDataName"), evfl.Argument)
    ):
        raise GiftPatchError(f"{step.id}: not a native frog-song call: {call}")
    gate = fc.events[_index(fc, fc.name, "Event167")]
    start = fc.events[_index(fc, fc.name, "Event380")]
    counter = _index(fc, fc.name, "Event392")
    if (
        not isinstance(gate, evfl.SwitchEvent)
        or fc.actors[gate.actor].queries[gate.query] != READ_QUERY
        or gate.params != {"GameDataName": evfl.Argument("GameDataName"), "Index": -1}
        or not isinstance(start, evfl.ActionEvent)
        or fc.actors[start.actor].actions[start.action] != "EventTriggerOpenRupeeDisplay"
    ):
        raise GiftPatchError(f"{step.id}: native frog first/repeat reward graph changed")
    # The native first-song counter/flag/growth still runs; the escalating rupee-only UI does not.
    grant = evfl.SubFlowEvent(
        start.name,
        "Dm_SY_GetInEvent",
        "GetInEvent_NotTurn_NotNpc",
        counter,
        {"ActorName": item, "IsNpcEventStarter": False},
    )
    call.flowchart = ""
    call.entry_point = _clone_entry(fc, "TeachNewMusic", {start.name: grant})


def _gallery_expert(fc: evfl.Flowchart, step: Gift, item: str) -> None:
    """First expert win grants one saved gift; later wins keep the untouched native 30/70 path."""
    repeat = fc.events[_index(fc, fc.name, step.event)]
    mode_name, native_start, close_name = GALLERY_EXPERT_ROUTES[step.event]
    mode = fc.events[_index(fc, fc.name, mode_name)]
    close = fc.events[_index(fc, fc.name, close_name)]
    if (
        fc.name != "MiniGame_HitTarget"
        or not isinstance(repeat, evfl.SubFlowEvent)
        or (repeat.flowchart or fc.name, repeat.entry_point) != ("MiniGame_HitTarget", "GetRupy_HitTarget")
        or repeat.params != {"GetRupee": GALLERY_EXPERT_RUPEES[step.event]}
        or repeat.next != _index(fc, fc.name, close_name)
        or not isinstance(mode, evfl.SwitchEvent)
        or fc.actors[mode.actor].queries[mode.query] != READ_QUERY
        or mode.params != {"GameDataName": "MiniGame_HitTarget_IsHardMode", "Index": -1}
        or dict(mode.cases).get(0) != _index(fc, fc.name, native_start)
        or not isinstance(close, evfl.ActionEvent)
        or fc.actors[close.actor].actions[close.action] != "EventCloseRupeeDisplay"
    ):
        raise GiftPatchError(f"{step.id}: stale expert reward dispatch: {repeat!r}, {mode!r}, {close!r}")
    flag = FLAG_PREFIX + step.id.replace("/", ".")
    grant_index = len(fc.events)
    grant = evfl.SubFlowEvent(
        f"{NEW_EVENT_PREFIX}{grant_index}",
        "Dm_SY_GetInEvent",
        "GetInEvent_NotTurn_NotNpc",
        close.next,
        {"ActorName": item, "IsNpcEventStarter": False},
    )
    fc.events.append(grant)
    _set_flag_after(fc, replace(step, event=grant.name), flag)
    actor = _game_data_actor(fc, fc.name)
    gate_index = len(fc.events)
    fc.events.append(
        evfl.SwitchEvent(
            f"{NEW_EVENT_PREFIX}{gate_index}",
            actor,
            _slot(fc.actors[actor].queries, READ_QUERY),
            [(0, _index(fc, fc.name, native_start)), (1, grant_index)],
            {"GameDataName": flag, "Index": -1},
        )
    )
    mode.cases = [(case, gate_index if case == 0 else target) for case, target in mode.cases]


def _set_item(fc: evfl.Flowchart, step: Gift, item: str) -> None:
    if step.call == FROG_SONG_CALL:
        _frog_song(fc, step, item)
        return
    if step.call == GALLERY_EXPERT_CALL:
        _gallery_expert(fc, step, item)
        return
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


def _once_gate(fc: evfl.Flowchart, flow: str, ref: str, flag: str) -> None:
    """Replace the shopkeeper's equipped-shield test, preserving its no-gift return and offer branch."""
    event = fc.events[_index(fc, flow, ref.split("/")[1])]
    if not isinstance(event, evfl.SwitchEvent):
        raise GiftPatchError(f"{ref}: not an equipped-shield query")
    actor = fc.actors[event.actor]
    if (
        (actor.name, actor.queries[event.query]) != ("Player_Event", "EventQueryPlayerIsEquipWeapon")
        or event.params != {"ArmorName": "Weapon_Shield_Deku", "WeaponSlot": 4}
        or sorted(case for case, _ in event.cases) != [0, 1]
    ):
        raise GiftPatchError(f"{ref}: unexpected equipped-shield gate: {event}")
    if flow == SHOPKEEPER_FLOW and ref == f"{SHOPKEEPER_FLOW}/Event45":
        _shopkeeper_window(fc, flag)
    event.actor = _game_data_actor(fc, flow)
    event.query = _slot(fc.actors[event.actor].queries, READ_QUERY)
    event.params = {"GameDataName": flag, "Index": -1}


def _shopkeeper_window(fc: evfl.Flowchart, flag: str) -> None:
    """Offer an uncollected shuffled gift after initialization, before native quest dispatch."""
    dispatch = fc.events[_index(fc, SHOPKEEPER_FLOW, "Event24")]
    original = _index(fc, SHOPKEEPER_FLOW, "Event23")
    meeting = fc.events[_index(fc, SHOPKEEPER_FLOW, "Event1")]
    offer = _index(fc, SHOPKEEPER_FLOW, "Event83")
    if (
        not isinstance(dispatch, evfl.ActionEvent)
        or dispatch.next != original
        or not isinstance(meeting, evfl.SwitchEvent)
        or fc.actors[meeting.actor].name != GAME_DATA_ACTOR
        or fc.actors[meeting.actor].queries[meeting.query] != "EventQueryIsGameDataBoolExp"
        or meeting.params != {"GameDataName": "Meet_DekuTree_IsAfter_Step02_Exp"}
        or dict(meeting.cases).get(0) != offer
    ):
        raise GiftPatchError(f"{SHOPKEEPER_FLOW}: stale shopkeeper story dispatch: {dispatch!r}, {meeting!r}")
    names = {event.name for event in fc.events}
    if names & {"ClawshotShopkeeperDone", "ClawshotShopkeeperMetTree"}:
        raise GiftPatchError(f"{SHOPKEEPER_FLOW}: shopkeeper dispatch already extended")
    actor = _game_data_actor(fc, SHOPKEEPER_FLOW)
    start = len(fc.events)
    fc.events.extend(
        [
            evfl.SwitchEvent(
                "ClawshotShopkeeperDone",
                actor,
                _slot(fc.actors[actor].queries, READ_QUERY),
                [(0, original), (1, start + 1)],
                {"GameDataName": flag, "Index": -1},
            ),
            evfl.SwitchEvent(
                "ClawshotShopkeeperMetTree",
                meeting.actor,
                meeting.query,
                [(0, offer), (1, original)],
                dict(meeting.params),
            ),
        ]
    )
    dispatch.next = start


def _set_display(fc: evfl.Flowchart, flow: str, ref: str, vanilla: set[str], item: str) -> None:
    """Point the display-only get window or Zelda's Notes target ``ref`` at ``item`` (spec event-items 1.2). Its
    native value must be the grant's vanilla item."""
    event = fc.events[_index(fc, flow, ref.split("/")[1])]
    if (
        isinstance(event, evfl.SubFlowEvent)
        and (event.flowchart or flow) == event_items.DISPLAY_FLOW
        and event.entry_point == event_items.DISPLAY_ENTRY
    ):
        param = event_items.DISPLAY_PARAM
    elif (
        isinstance(event, evfl.ActionEvent) and fc.actors[event.actor].actions[event.action] == event_items.NOTES_ACTION
    ):
        param = event_items.NOTES_PARAM
    else:
        raise GiftPatchError(
            f"{ref}: expected DisplayGetByActorName with literal ActorName or a Zelda's Notes step, got {event!r}"
        )
    native = (event.params or {}).get(param)
    if isinstance(native, evfl.Argument) or native not in vanilla:
        raise GiftPatchError(
            f"{ref}: expected DisplayGetByActorName with literal ActorName in {sorted(vanilla)}: {param} is {native!r}"
        )
    event.params = {**event.params, param: item}


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


def _completion_gate(fc: evfl.Flowchart, entry: str, flag: str, done: int) -> None:
    root = fc.entry_point(entry)
    actor = _game_data_actor(fc, fc.name)
    fc.events.append(
        evfl.SwitchEvent(
            f"{NEW_EVENT_PREFIX}{len(fc.events)}",
            actor,
            _slot(fc.actors[actor].queries, READ_QUERY),
            [(0, done), (1, root.main_event)],
            {"GameDataName": flag, "Index": -1},
        )
    )
    root.main_event = len(fc.events) - 1


def _native_purchase_gate(fc: evfl.Flowchart, entry: str, change: GiftChange) -> None:
    """Keep the untouched native transaction after the saved randomized check."""
    native = _clone_entry(fc, entry, {}, name=NEW_EVENT_PREFIX + "NativePurchase" + change.steps[0].flow)
    index = len(fc.events)
    fc.events.append(evfl.SubFlowEvent(f"{NEW_EVENT_PREFIX}{index}", "", native, evfl.NONE))
    fc.entry_point(entry).sub_flow_events.append(index)
    _completion_gate(fc, entry, change.flag, index)


def _purchase(fc: evfl.Flowchart, flow: str, change: GiftChange) -> None:
    (step,) = change.steps
    if change.check == GRANNY_CHECK:
        if flow != step.flow:
            return
        grant = fc.events[_index(fc, flow, step.event)]
        if not isinstance(grant, evfl.SubFlowEvent) or grant.entry_point != "GetInEventInBottle_BlueBottleShop":
            raise GiftPatchError(f"{step.id}: not Granny's native bottle sale")
        _native_purchase_gate(fc, "Buy_BluePotion", change)
        if change.item != step.vanilla_item:
            # Non-refill rewards use an ordinary gift; only that path needs an explicit charge.
            # _set_item resolves its actor after the pristine native graph has been preserved.
            grant.entry_point = "GetInEvent_NotTurn_NotNpc"
            grant.params = {"ActorName": step.vanilla_item, "IsNpcEventStarter": False}
        _set_flag_after(fc, step, change.flag)
        if change.item != step.vanilla_item:
            pouch = next(i for i, a in enumerate(fc.actors) if a.name == "PouchSystemActor")
            fc.events.append(
                evfl.ActionEvent(
                    f"{NEW_EVENT_PREFIX}{len(fc.events)}",
                    pouch,
                    _slot(fc.actors[pouch].actions, "EventTriggerAddGameDataIntToRupee"),
                    grant.next,
                    {"IsSignInverse": True, "GameDataName": "SimpleShop_Price"},
                )
            )
            grant.next = len(fc.events) - 1
        return

    entry, success = MERCHANT_SHOPS[change.check]
    specialized = NEW_EVENT_PREFIX + "Purchase" + step.flow
    if flow == step.flow:
        call = fc.events[_index(fc, flow, step.event)]
        if not isinstance(call, evfl.SubFlowEvent) or (call.flowchart, call.entry_point) != ("SimpleShop", entry):
            raise GiftPatchError(f"{step.id}: not the native merchant sale")
        _native_purchase_gate(fc, "Talk", change)
        call.entry_point = specialized
        if change.check == "GC Medigoron":
            # Sword ownership (including Biggoron's Sword) must not consume an independent reward.
            for name, item in (("Event6", "Weapon_Sword_Giant"), ("Event19", "Weapon_Sword_Biggoron")):
                event = fc.events[_index(fc, flow, name)]
                if (
                    not isinstance(event, evfl.SwitchEvent)
                    or fc.actors[event.actor].queries[event.query] != "EventQueryIsExistInPouch"
                    or event.params != {"Num": 1, "Actor": item}
                ):
                    raise GiftPatchError(f"{flow}/{name}: native sword ownership gate changed")
                event.actor = _game_data_actor(fc, flow)
                event.query = _slot(fc.actors[event.actor].queries, READ_QUERY)
                event.params = {"GameDataName": change.flag, "Index": -1}
        return
    if flow != "SimpleShop":
        return

    replacements = {}
    if change.check == "Wasteland Bombchu Salesman":
        prefix = f"{NEW_EVENT_PREFIX}{len(fc.events)}_"
        buy = _clone_entry(fc, "Sub_SimpleShop_Buy", {}, name=specialized + "Buy")
        _set_flag_after(fc, replace(step, flow=flow, event=prefix + success), change.flag)
        call = deepcopy(fc.events[_index(fc, flow, "Event124")])
        call.entry_point = buy
        replacements[call.name] = call
    else:
        native = fc.events[_index(fc, flow, success)]
        if not isinstance(native, evfl.SubFlowEvent) or native.entry_point != "GetInEventItemSwordMedigoron":
            raise GiftPatchError(f"{flow}/{success}: native sword grant changed")
        replacements[success] = evfl.SubFlowEvent(
            success,
            "Dm_SY_GetInEvent",
            "GetInEvent_NotTurn_NotNpc",
            native.next,
            {"ActorName": evfl.Argument("ActorName"), "IsNpcEventStarter": False},
        )
        # A shuffled reward is not a knife repair: never take the player's broken sword.
        autosave = deepcopy(fc.events[_index(fc, flow, "Event62")])
        autosave.name = "Event25"
        replacements[autosave.name] = autosave
    prefix = f"{NEW_EVENT_PREFIX}{len(fc.events)}_"
    _clone_entry(fc, entry, replacements, name=specialized)
    if change.check == "GC Medigoron":
        _set_flag_after(fc, replace(step, flow=flow, event=prefix + success), change.flag)


def _market_bottle(fc: evfl.Flowchart, change: GiftChange) -> None:
    """A shuffled tutorial reward must not require, consume or animate a bottle it no longer gives."""
    (step,) = change.steps
    grant = fc.events[_index(fc, fc.name, step.event)]
    accept = fc.events[_index(fc, fc.name, "Event6")]
    root = fc.entry_point("Item_Bottle_TutorialEvent_Talk")
    if (
        step.id != MARKET_BOTTLE_STEP
        or not isinstance(grant, evfl.SubFlowEvent)
        or (grant.flowchart, grant.entry_point, grant.next)
        != ("Dm_SY_GetInEvent", "GetInEvent_NotTurn_FixedCamera_WarpLink", evfl.NONE)
        or not isinstance(accept, evfl.ActionEvent)
        or accept.next != _index(fc, fc.name, "Event10")
        or root.main_event != _index(fc, fc.name, "Event27")
    ):
        raise GiftPatchError(f"{step.id}: stale bottle tutorial dispatch: {grant!r}, {accept!r}, {root!r}")
    # Keep the native offer/refusal, but replace its bottle-only staging/bug-capture tail.
    accept.next = _index(fc, fc.name, step.event)
    grant.entry_point = "GetInEvent_NotTurn_NotNpc"
    grant.params = {"ActorName": change.item, "IsNpcEventStarter": False}
    # Finish the native non-bottle state machine: bug removal, relaxed schedule and arrival AS.
    continuation = _index(fc, fc.name, "Event76")  # native tutorial quest completion
    for name, action in reversed(
        (
            ("Event65", "EventPlayAS"),
            ("Event63", "EventTriggerAIScheduleSelectSchedule"),
            ("Event62", "EventTriggerAIScheduleSetForceCancelEventContinueArrivalAS"),
        )
    ):
        native = fc.events[_index(fc, fc.name, name)]
        if (
            not isinstance(native, evfl.ActionEvent)
            or fc.actors[native.actor].name != MARKET_BOTTLE_FLOW
            or fc.actors[native.actor].actions[native.action] != action
            or (name == "Event65" and (native.params or {}).get("ASName") != "Wait")
            or (name == "Event62" and native.params != {"Value": False})
        ):
            raise GiftPatchError(f"{step.id}: stale bottle schedule finalization: {native!r}")
        event = deepcopy(native)
        event.name = f"{NEW_EVENT_PREFIX}{len(fc.events)}"
        event.next = continuation
        fc.events.append(event)
        continuation = len(fc.events) - 1
    grant.next = continuation
    for flag in (
        "Market_Item_Bottle_TutorialEvent_Cleared",
        "Market_Item_Bottle_TutorialEvent_Shop_Bottle_Insect_Appeared",
        "Market_Item_Bottle_TutorialEvent_Insect_Delete",
        "Market_Item_Bottle_TutorialEvent_Started",
        MARKET_BOTTLE_FLAG,
    ):
        _set_flag_after(fc, step, flag)
    _completion_gate(fc, root.name, MARKET_BOTTLE_FLAG, fc.entry_point("Talk").main_event)


def _bowling_order(fc: evfl.Flowchart) -> None:
    """First win -> bag check, second -> heart check, later wins -> unchanged native filler."""
    for event_name, flag, original, targets in (
        ("Event73", "ClearFirstTime", ("Event72", "Event309"), ("Event72", "Event76")),
        ("Event72", "ClearSecondTime", ("Event260", "Event76"), ("Event81", "Event143")),
    ):
        event = fc.events[_index(fc, fc.name, event_name)]
        if (
            not isinstance(event, evfl.SwitchEvent)
            or fc.actors[event.actor].queries[event.query] != READ_QUERY
            or event.params != {"GameDataName": f"MiniGame_BombchuBowling_{flag}", "Index": -1}
            or event.cases != [(case, _index(fc, fc.name, name)) for case, name in enumerate(original)]
        ):
            raise GiftPatchError(f"{fc.name}: stale bowling prize order: {event!r}")
        event.cases = [(case, _index(fc, fc.name, name)) for case, name in enumerate(targets)]


def _skull_kid_first_win(fc: evfl.Flowchart) -> None:
    """Give the unclaimed prize after a complete win, at the native serial reward boundary."""
    join = fc.events[_index(fc, fc.name, "Event178")]
    dispatch = _index(fc, fc.name, "Event9")
    grade = fc.events[_index(fc, fc.name, "Event12")]
    gate = fc.events[_index(fc, fc.name, "Event64")]
    grant = fc.events[_index(fc, fc.name, "Event24")]
    flag = fc.events[_index(fc, fc.name, "Event58")]
    if (
        not isinstance(join, evfl.JoinEvent)
        or join.next != dispatch
        or not isinstance(grade, evfl.ActionEvent)
        or fc.actors[grade.actor].name != GAME_DATA_ACTOR
        or fc.actors[grade.actor].actions[grade.action] != "EventTriggerSetGameDataInt"
        or grade.params
        != {"GameDataName": "Minigame_SkullKidSession_CurrentGradeSoundNumForSession", "Index": -1, "Value": 8}
        or grade.next != _index(fc, fc.name, "Event23")
        or not isinstance(gate, evfl.SwitchEvent)
        or fc.actors[gate.actor].name != GAME_DATA_ACTOR
        or fc.actors[gate.actor].queries[gate.query] != READ_QUERY
        or gate.params != {"GameDataName": SKULL_KID_FLAG, "Index": -1}
        or gate.cases != [(0, _index(fc, fc.name, "Event154")), (1, _index(fc, fc.name, "Event24"))]
        or not isinstance(grant, evfl.SubFlowEvent)
        or (grant.flowchart, grant.entry_point, grant.next)
        != ("Dm_SY_GetInEvent", "GetInEvent_NotTurn_NotNpc", _index(fc, fc.name, "Event58"))
        or not isinstance(flag, evfl.ActionEvent)
        or fc.actors[flag.actor].name != GAME_DATA_ACTOR
        or fc.actors[flag.actor].actions[flag.action] != SET_ACTION
        or flag.params != {"GameDataName": SKULL_KID_FLAG, "Index": -1, "Value": True}
    ):
        raise GiftPatchError(f"{fc.name}: stale memory-game reward boundary: {join!r}, {grade!r}, {gate!r}")
    # Native Bool queries use 0=true, 1=false. A completed source keeps the entire native dispatcher.
    first = deepcopy(gate)
    first.name = f"{NEW_EVENT_PREFIX}SkullKidFirstWin"
    first.cases = [(0, dispatch), (1, len(fc.events) + 1)]
    completed_grade = deepcopy(grade)
    completed_grade.name = f"{NEW_EVENT_PREFIX}SkullKidPrizeGrade"
    # Match the native third-win state, then its rally reset, camera, gift, once-flag and Ready tail.
    completed_grade.next = _index(fc, fc.name, "Event68")
    join.next = len(fc.events)
    fc.events.extend((first, completed_grade))


def skull_kid_changes() -> dict[str, Callable[[bytes], bytes]]:
    """Every seed gives the memory game's native or shuffled prize on its first complete win."""

    def transform(data: bytes) -> bytes:
        tree = evfl.read(data)
        if tree.flowchart is None or tree.flowchart.name != SKULL_KID_FLOW:
            raise GiftPatchError(f"{SKULL_KID_FLOW}: the file holds no flowchart of that name")
        _skull_kid_first_win(tree.flowchart)
        out = evfl.write(tree)
        if evfl.read(out) != tree:
            raise GiftPatchError(f"{SKULL_KID_FLOW}: the written flow does not read back as the changed tree")
        return out

    return {f"Event/EventFlow/{SKULL_KID_FLOW}.bfevfl.zs": transform}


def _dampe_reward(fc: evfl.Flowchart, step: Gift) -> None:
    """Reuse the native completion flag around the real gift, not the temporary floor prop."""
    index = _index(fc, fc.name, step.event)
    grant = fc.events[index]
    fork = fc.events[_index(fc, fc.name, "Event449")]
    inbound = [e.name for e in fc.events if index in _successors(e)]
    if (
        not isinstance(grant, evfl.SubFlowEvent)
        or (grant.flowchart, grant.entry_point, grant.next)
        != ("Dm_SY_GetInEvent", "GetInEvent_NotTurn_NotNpc_Dampe", evfl.NONE)
        or not isinstance(fork, evfl.ForkEvent)
        or fork.forks[0] != index
        or inbound != ["Event449"]
        or any(e.main_event == index for e in fc.entry_points)
    ):
        raise GiftPatchError(f"{step.id}: stale digging reward fork: {grant!r}, {fork!r}, {inbound!r}")
    _set_flag_after(fc, step, DAMPE_FLAG)
    actor = _game_data_actor(fc, fc.name)
    fork.forks[0] = len(fc.events)
    fc.events.append(
        evfl.SwitchEvent(
            f"{NEW_EVENT_PREFIX}{len(fc.events)}",
            actor,
            _slot(fc.actors[actor].queries, READ_QUERY),
            [(0, evfl.NONE), (1, index)],
            {"GameDataName": DAMPE_FLAG, "Index": -1},
        )
    )


def patch_flowchart(fc: evfl.Flowchart, flow: str, changes: Sequence[GiftChange]) -> None:
    """Apply ``changes``' edits that fall in ``flow`` to its flowchart, in place."""
    if flow == BOWLING_FLOW and any(c.check in BOWLING_CHECKS for c in changes):
        _bowling_order(fc)
    for change in changes:
        vanilla = {step.vanilla_item for step in change.steps}
        if change.rule.purchase:
            _purchase(fc, flow, change)
        for step in change.steps:
            if step.flow == flow:
                _set_item(fc, step, change.item)
                if change.dungeon_grant is not None:
                    _set_flag_after(fc, step, change.dungeon_grant.field)
                if (change.new_flag or change.rule.once) and not change.rule.purchase and not change.expert:
                    _set_flag_after(fc, step, change.flag)
                if change.check == MARKET_BOTTLE_CHECK:
                    _market_bottle(fc, change)
                if change.check == BOWLING_SECOND:
                    # Its native heart-marker flag remains correct when the reward moves to win two.
                    _set_flag_after(fc, step, "MiniGame_BombchuBowling_ClearThirdTime")
                if change.check == DAMPE_CHECK:
                    _dampe_reward(fc, step)
        for ref in change.rule.display:
            if ref.split("/")[0] == flow:
                _set_display(fc, flow, ref, vanilla, change.item)
        for ref in change.rule.given:
            if ref.split("/")[0] == flow:
                _read_flag(fc, flow, ref, vanilla, change.flag)
        for ref in change.rule.writes:
            if ref.split("/")[0] == flow:
                _redirect_write(fc, flow, ref, vanilla, change.flag)
        for ref in change.rule.once:
            if ref.split("/")[0] == flow:
                _once_gate(fc, flow, ref, change.flag)
        for ref in change.rule.skip:
            if ref.split("/")[0] == flow:
                _skip(fc, flow, ref)
    # Shared flows are guarded once by bags.changes, after all source edits and key compilation.
    if flow not in {bags.FLOW, bags.HANDOVER_FLOW}:
        bags.patch_grants(fc, literal_only=True)


def flows_changed(changes: Iterable[GiftChange]) -> list[str]:
    out = set()
    for change in changes:
        out |= {step.flow for step in change.steps}
        out |= {
            ref.split("/")[0]
            for ref in (
                *change.rule.given,
                *change.rule.skip,
                *change.rule.writes,
                *change.rule.once,
                *change.rule.display,
            )
        }
        if change.rule.purchase and change.check in MERCHANT_SHOPS:
            out.add("SimpleShop")
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


def _granny_preload(data: bytes) -> bytes:
    """Register the ordinary get scene used only by a non-refill first reward."""
    document = byml.load(data)
    rows = [row for row in document.root if row.get("__RowId") == "Npc_Hylia_053_Adult_D_T"]
    if len(rows) != 1:
        raise GiftPatchError(f"Granny purchase: expected one Talk analyzed-event row, got {rows!r}")
    row = rows[0]
    row["SubFlowList"] = sorted(set(row.get("SubFlowList", ())) | {"Dm_SY_Get"})
    out = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(out))) is not None:
        raise GiftPatchError(f"Granny purchase: written preload registration differs: {difference}")
    return out


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
    if any(change.check == GRANNY_CHECK and change.item != change.steps[0].vanilla_item for change in changes):
        out[ANALYZED] = _granny_preload
    return out


# Native reward-preview labels (round 6 hints design note; section 35).
SKULLTULA_HINTS = {
    f"Kak {count} Gold Skulltula Reward": (count, label)
    for count, label in ((10, "Talk_28"), (20, "Talk_23"), (30, "Talk_24"), (40, "Talk_25"), (50, "Talk_26"))
}

# Freed sons, not the still-cursed SkullChild actors. The first son also discusses
# the later wallet reward; both must stop describing native wallet capacities.
SKULLTULA_CHILDREN = {
    10: ("Npc_Hylia_029", ("Talk_12", "Talk_13", "Talk_14")),
    20: (
        "Npc_Hylia_028",
        ("Talk_11", "Talk_14", "Talk_08", "Talk_02", "Talk_03", "Talk_01", "Talk_09", "Talk_10", "Talk_07"),
    ),
    30: ("Npc_Hylia_027", ("Talk_06", "Talk_14", "Talk_05", "Talk_03", "Talk_04")),
    40: ("Npc_Hylia_026", ("Talk_09", "Talk_14", "Talk_06", "Talk_05", "Talk_12", "Talk_10")),
    50: ("Npc_Hylia_025", ("Talk_00", "Talk_01", "Talk_11")),
}
SKULLTULA_CHILD_CHOICES = {
    "Npc_Hylia_029": ("Talk_12", "Talk_16"),
    "Npc_Hylia_028": ("Talk_11",),
    "Npc_Hylia_027": ("Talk_06", "Talk_14"),
    "Npc_Hylia_026": ("Talk_09", "Talk_14"),
}
SKULLTULA_APPEND = {
    "Npc_Hylia_029": ("Talk_14",),
    "Npc_Hylia_028": ("Talk_07",),
    "Npc_Hylia_027": ("Talk_04",),
    "Npc_Hylia_026": ("Talk_10",),
    "Npc_Hylia_025": ("Talk_00", "Talk_01", "Talk_11"),
}


def skulltula_hint_changes(romfs: str | Path, placements: Mapping[str, str]) -> dict[str, Callable[[bytes], bytes]]:
    """Name shuffled 10–50 rewards in Dad's previews and the freed sons' advice.

    English in every language follows D26. Both pending and claimed advice describes
    the seed's item, never its vanilla effect. The separate first/repeat 100 reward
    has no child and is outside these existing 10–50 preview lines.
    """
    from clawshot.formats import msbt, sarc
    from clawshot.patch import text

    selected = {name: actor for name, actor in placements.items() if name in SKULLTULA_HINTS}
    if not selected:
        return {}
    romfs = Path(romfs)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    path = text.archive_path(text.NAME_LANGUAGE)
    archive = sarc.read(dicts.decompress(path, (romfs / path).read_bytes()))
    pouch = msbt.read(archive[text.POUCH_TEXT])
    lines: dict[str, dict[str, str]] = {"EventFlowMsg/Npc_SkullDad.msbt": {}}
    reward_lines = {}

    def child_lines(actor: str, labels: Sequence[str], line: str) -> None:
        file = f"EventFlowMsg/{actor}.msbt"
        originals = msbt.read(archive[file]).messages
        for label in labels:
            shown = line
            if label in SKULLTULA_APPEND.get(actor, ()):
                shown = msbt.plain(originals[label]) + " " + line
            if label in SKULLTULA_CHILD_CHOICES.get(actor, ()):
                shown += " Hear that again?"
            lines.setdefault(file, {})[label] = shown

    for name, actor in selected.items():
        count, label = SKULLTULA_HINTS[name]
        key = text.read_text_key(romfs, actor, dicts)
        item = msbt.plain(text.item_name(pouch, key))
        marked = f"{text.FIELD_START}{item}{text.FIELD_END}"
        lines["EventFlowMsg/Npc_SkullDad.msbt"][label] = f"For {count} tokens, the reward is {marked}."
        reward_lines[count] = f"{count}-token reward: {marked}."
        child, labels = SKULLTULA_CHILDREN[count]
        child_lines(child, labels, reward_lines[count])
    if 30 in reward_lines:
        child_lines("Npc_Hylia_029", ("Talk_15", "Talk_16"), reward_lines[30])
    wallet = " ".join(reward_lines[count] for count in (10, 30) if count in reward_lines)
    if wallet:
        child_lines("Npc_Hylia_029", ("Talk_17", "Talk_18", "Talk_19"), wallet)

    def transform(data: bytes) -> bytes:
        files = sarc.read(data)
        edits = {}
        for file, labels in lines.items():
            messages = msbt.read(files[file]).messages
            width = text.HINT_WIDTH if file == "EventFlowMsg/Npc_SkullDad.msbt" else 40
            edits[file] = {
                label: text.stone_line(messages[label], line, width=width, rows=2) for label, line in labels.items()
            }
        return text.edit_messages(edits)(data)

    return {text.archive_path(language): transform for language in text.languages(romfs)}


# --- seeds --------------------------------------------------------------------------------------------------------

# World event-gift types; the persistent shopkeeper reward is an ordinary NPC check (section 34).
GIFT_TYPES = ("NPC", "Song", "Cutscene", "Boss")
SHUFFLE = "Gift"  # the --shuffle value
SONG_TYPE = "Song"
FREE_TIME_TRAVEL = "free_time_travel"  # lifts legacy anchors, not the seed's native child-strength source
# Copy-only seed logic always needs the native child Bracelet source, even with free return.
# Direct legacy worlds lift this D20 anchor only when time travel is free.
ANCHORS = {"GC Darunias Joy": "native Darunia supplies child strength (D20; section 47), never a copy tier"}


def shopkeeper_spec(spec: Mapping[str, Any]) -> dict[str, Any]:
    """For Gift/NPC shuffle, turn the data-sourced free-shield event into a persistent placed reward."""
    regions = []
    locations = dict(spec["locations"])
    for region in spec["regions"]:
        if region["name"] == SHOPKEEPER_REGION and "Deku Shield" in region.get("events", {}):
            events = dict(region["events"])
            rule = events.pop("Deku Shield")
            locations[SHOPKEEPER_CHECK] = {
                "type": "NPC",
                "vanilla": "Deku Shield",
                "source": rule["source"],
            }
            region = {
                **region,
                "events": events,
                "locations": {**region.get("locations", {}), SHOPKEEPER_CHECK: rule},
            }
        regions.append(region)
    return {**spec, "regions": regions, "locations": locations}


def logic_spec(spec: Mapping[str, Any], settings: Settings) -> Mapping[str, Any]:
    """Gift/NPC shuffle's shared world policy: the shopkeeper check and Granny's non-container pool item.

    An explicit native identity pin uses keep_vanilla and retains Blue Potion outside the fill.
    The tracker uses the same conversion through clawshot.patch.logic_world.
    """
    if SHUFFLE not in settings.shuffle and "NPC" not in settings.shuffle:
        return spec
    spec = shopkeeper_spec(spec)
    granny = spec["locations"].get(GRANNY_CHECK)
    if granny and granny.get("vanilla") == "Blue Potion" and granny.get("keep_vanilla") is None:
        spec = {
            **spec,
            "locations": {
                **spec["locations"],
                GRANNY_CHECK: {**granny, "vanilla": GRANNY_POOL_ITEM},
            },
        }
    return spec


def movable_checks(world: World, rules: Mapping[str, Rule]) -> list[str]:
    """Dump-free upper bound on movable gifts. Native step/actor checks in ``seed_checks`` can only remove checks."""
    free = world.settings.get(FREE_TIME_TRAVEL) is True
    return [
        name
        for name, loc in world.locations.items()
        if loc.type in GIFT_TYPES
        and name in rules
        and rules[name].cls != MORE
        and loc.vanilla is not None
        and loc.n64_only is None
        and loc.keep_vanilla is None
        and not (name in ANCHORS and (world.progressive_copies_only or not free))
    ]


def seed_checks(
    world: World,
    gifts: Iterable[Gift],
    definitions: Iterable[Definition],
    rules: Mapping[str, Rule],
    actors: ItemActors,
) -> list[str]:
    """The world locations a gift shuffle may move, in world order: a gift check of class ``swap`` or ``rewrite``
    whose vanilla logic item's actor (``item_actors.toml``) is what every one of its steps gives. Granny's native
    refill is the exception: it contributes ordinary Rupees (5), never a new bottle. A Great Fairy, given once
    through a new GameDataList flag, is one of them (Kareem, in game, 2026-11-08: the game keeps the flag and an
    older save loads; 03-game-data.md section 19). The :data:`ANCHORS` stay vanilla in copy-only seed worlds;
    direct legacy worlds release them with free travel."""
    steps = check_steps(gifts, definitions)
    out = []
    for name in movable_checks(world, rules):
        loc = world.locations[name]
        if name not in steps:
            continue
        # Accepted variable-rupee families contribute fixed20, and always specialize same-item assignments.
        if all(s.call in VARIABLE_RUPEE_CALLS for s in steps[name]) and loc.vanilla == "Rupees (20)":
            out.append(name)
            continue
        if name in progressive.TIERED_GIFTS:
            item, native = progressive.TIERED_GIFTS[name]
            if loc.vanilla == item and {s.vanilla_item for s in steps[name]} == native:
                out.append(name)
            continue
        if name == GRANNY_CHECK and loc.vanilla == GRANNY_POOL_ITEM:
            if {s.vanilla_item for s in steps[name]} == {"Item_Bottle_BluePotion"}:
                out.append(name)
            continue
        if {actors.aliases.get(s.vanilla_item, s.vanilla_item) for s in steps[name]} != {
            _MERCHANT_SOURCE_ACTORS.get(actors.actors.get(loc.vanilla), actors.actors.get(loc.vanilla))
        }:
            continue
        out.append(name)
    return out


HAND_OVER_SCRUB_TYPES = ("Scrub", "GrottoScrub")


def is_hand_over(source_type: str | None, steps: Iterable[Gift]) -> bool:
    """Whether the native recipient creates the item actor rather than granting directly to the pouch."""
    return source_type in HAND_OVER_SCRUB_TYPES or any(
        step.call not in (DIRECT, "GetPouchContent:GetPouchContentByActorName") for step in steps
    )


def restrict_spec(
    spec: Mapping[str, Any], shuffled: Iterable[str], steps: Mapping[str, tuple[Gift, ...]] | None = None
) -> dict[str, Any]:
    """Keep unsupported gifts vanilla, and exclude unsafe items at show-item hand-overs.

    Direct pouch grants and the ordinary GetPouchContent wrapper do not create the
    item actor. All other admitted gift wrappers, plus scrub sales, do (r11-ocarina).
    """
    keep = set(shuffled)
    steps = steps or {}
    locations = {}
    for name, info in spec["locations"].items():
        if info.get("type") in GIFT_TYPES and name not in keep and not info.get("keep_vanilla"):
            info = {
                **info,
                "keep_vanilla": "gift shuffle: not changeable yet (gift_rules.toml, plans/03-game-data.md section 19)",
            }
        hand_over = (info.get("type") in HAND_OVER_SCRUB_TYPES or name in keep) and is_hand_over(
            info.get("type"), steps.get(name, ())
        )
        if hand_over:
            info = {
                **info,
                "excluded_items": tuple(
                    dict.fromkeys((*info.get("excluded_items", ()), *CATALOG["hand_over"]["excluded_items"]))
                ),
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
    *,
    dungeon_grants: Mapping[tuple[str, str], DungeonGrant] | None = None,
) -> Callable[[Mapping[str, str]], dict[str, Callable[[bytes], bytes]]]:
    """The seed's patch step for gifts: placements (location -> logic item) in, the flow and GameDataList
    transforms out, for moved gifts and once-gate normalization (``vanilla``: check -> its logic item)."""
    gifts, definitions = list(gifts), list(definitions)
    steps = check_steps(gifts, definitions)

    def step(placements: Mapping[str, str]) -> dict[str, Callable[[bytes], bytes]]:
        moved = {
            name: (
                steps[name][0].vanilla_item
                if name == GRANNY_CHECK and placements[name] == "Blue Potion"
                else actors.actor(placements[name])
            )
            for name in shuffled
            if placements[name] != vanilla[name]
            or rules[name].once
            or rules[name].purchase
            or name in progressive.TIERED_GIFTS
            or name in BOWLING_CHECKS
            or any(s.call in VARIABLE_RUPEE_CALLS for s in steps[name])
        }
        changes = plan(moved, gifts, definitions, rules)
        if dungeon_grants:
            changes = [
                replace(change, dungeon_grant=dungeon_grants.get((change.check, placements[change.check])))
                for change in changes
            ]
        return file_changes(changes, files)

    return step


def seed_setup(
    romfs: str | Path, spec: Mapping[str, Any], settings: Settings
) -> tuple[dict[str, Any], Settings, Callable[[Mapping[str, str]], dict[str, Callable[[bytes], bytes]]]]:
    """For ``--shuffle Gift``: the spec with the gifts that cannot move held vanilla, the settings shuffling the
    gift types in place of ``Gift`` and a placement policy from ``settings.songs`` plus the verified chest
    actor list in ``data/settings.toml``), and the patch step to pass to ``make_seed``."""
    spec = logic_spec(spec, settings)
    if SHUFFLE in settings.shuffle or "NPC" in settings.shuffle:
        locations = dict(spec["locations"])
        for name in ("Market Bombchu Bowling Bombchus", "Market Bombchu Bowling Bomb"):
            if name not in locations:
                continue
            locations[name] = {
                **locations[name],
                "n64_only": "shuffled bowling has two prizes, then native repeat filler (Round 10)",
            }
        spec = {**spec, "locations": locations}
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
    held = held_items(
        world,
        vanilla.values(),
        actors,
        chest_actors,
        songs=settings.songs,
        token_shuffle=token_policy.SHUFFLE in settings.shuffle,
    )
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
    # Generic pouch grants do not credit dungeon maps/compasses. Reuse the chest grant's target/field contract.
    # Same-dungeon gifts only; admission remains chest-held until the staged lesson check passes.
    dungeon_grants = {
        (name, item): DungeonGrant(DUNGEON_TARGETS[info.dungeon].id, info.type)
        for name in shuffled
        for item, info in world.items.items()
        if info.type in {"Map", "Compass"}
        and info.dungeon in DUNGEON_TARGETS
        and info.dungeon == world.regions[world.locations[name].region].dungeon
    }
    gift_step = seed_step(shuffled, census, definitions, rules, actors, vanilla, files, dungeon_grants=dungeon_grants)

    def step(placements: Mapping[str, str]) -> dict[str, Callable[[bytes], bytes]]:
        hints = skulltula_hint_changes(
            romfs, {name: actors.actor(placements[name]) for name in shuffled if name in SKULLTULA_HINTS}
        )
        return {**gift_step(placements), **hints}

    return restrict_spec(spec, shuffled, check_steps(census, definitions)), settings, step


def held_items(
    world: World,
    items: Iterable[str],
    actors: ItemActors,
    chest_actors: set[str],
    *,
    songs: str = DEFAULTS["songs"],
    token_shuffle: bool = False,
) -> dict[str, tuple[str, ...]]:
    """Songs-on-songs by default; anywhere releases the whole song family (reviewer, Round 6).

    The other eleven songs are inferred from the Song of Storms chest result, not individually verified.
    Non-song gifts still need a vanilla chest actor or a sourced ``chest_verified`` catalog entry for chests.
    Scoped records add only their named destination kinds to existing Gift/Token eligibility.
    Unscoped records retain the existing item-type hold release.
    Independently played Token rewards may also use Skulltulas; this does not certify their chest path.
    """
    out = {}
    for item in items:
        if world.items[item].type == SONG_TYPE:
            if songs == "song":
                out[item] = (SONG_TYPE,)
        else:
            actor = actors.actor(item)
            # Gift sources must not remove tunics from their existing native shop palette.
            if item in ("Goron Tunic", "Zora Tunic"):
                continue
            receipt = CATALOG["chest_verified"].get(actor)
            destinations = receipt.get("destinations") if receipt is not None else None
            if destinations is None and (actor in chest_actors or receipt is not None):
                continue
            out[item] = tuple(t for t in GIFT_TYPES if songs == "anywhere" or t != SONG_TYPE)
            if token_shuffle and item in token_policy.REWARDS:
                out[item] += (token_policy.SHUFFLE,)
            if destinations is not None:
                out[item] += tuple(destinations)
    return dict(sorted(out.items()))
