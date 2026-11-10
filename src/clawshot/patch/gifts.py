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

from clawshot.census import definitions as census_definitions
from clawshot.census.definitions import Definition
from clawshot.census.gifts import (
    FLOW_VERSIONS,
    FROG_SONG_CALL,
    FROG_SONG_FLAGS,
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
FIELDS = {"class", "gate", "given", "flag", "skip", "reason", "writes", "once", "purchase"}

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
# Fix the native ownership-dependent upgrade tiers, not the weapon used by a rental minigame.
TIERED_GIFTS = {
    BOWLING_FIRST: ("Bomb Bag (30)", {"Item_BombBag_Medium", "Item_BombBag_Large"}),
    "Market Shooting Gallery Reward": ("Bullet Bag (40)", {"Item_BulletBag_Medium", "Item_BulletBag_Large"}),
    "Kak Shooting Gallery Reward": ("Quiver (40)", {"Item_Quiver_Medium", "Item_Quiver_Large"}),
}

# Sale calls need their flag inside the success branch, not after a wrapper that can refuse.
MERCHANT_SHOPS = {
    "GC Medigoron": ("SimpleShopRoot_Npc_Goron_Medigoron_Adult", "Event119"),
    "Wasteland Bombchu Salesman": ("SimpleShopRoot", "Event150"),
}
GRANNY_CHECK = "Kak Granny Buy Blue Potion"

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
            tuple(_ref(check, r) for r in entry.get("once", [])),
            entry.get("purchase", False),
        )
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
        if not (self.rule.given or self.rule.writes or self.rule.once or self.rule.purchase):
            return None
        return self.rule.flag or FLAG_PREFIX + self.steps[0].id.replace("/", ".")

    @property
    def new_flag(self) -> str | None:
        """The flag the patch adds to GameDataList and sets after each step, or None."""
        return (
            self.flag if (self.rule.given or self.rule.once or self.rule.purchase) and self.rule.flag is None else None
        )


def check_steps(gifts: Iterable[Gift], definitions: Iterable[Definition]) -> dict[str, tuple[Gift, ...]]:
    """World check name -> its census gift steps, including the remake-only shopkeeper, in census order."""
    name_of = {d.id: d.oot_randomizer_name for d in definitions if isinstance(d.id, str) and d.oot_randomizer_name}
    name_of.update({step: SHOPKEEPER_CHECK for step in SHOPKEEPER_STEPS})
    name_of[MARKET_BOTTLE_STEP] = MARKET_BOTTLE_CHECK
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


def _set_item(fc: evfl.Flowchart, step: Gift, item: str) -> None:
    if step.call == FROG_SONG_CALL:
        _frog_song(fc, step, item)
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


def _purchase(fc: evfl.Flowchart, flow: str, change: GiftChange) -> None:
    (step,) = change.steps
    if change.check == GRANNY_CHECK:
        if flow != step.flow:
            return
        grant = fc.events[_index(fc, flow, step.event)]
        if not isinstance(grant, evfl.SubFlowEvent) or grant.entry_point != "GetInEventInBottle_BlueBottleShop":
            raise GiftPatchError(f"{step.id}: not Granny's native bottle sale")
        # This wrapper normally fills a bottle AND charges. The ordinary gift wrapper does neither charge
        # nor touch bottles, so restore only the native charge on the successful grant edge.
        grant.entry_point = "GetInEvent_NotTurn_NotNpc"
        grant.params = {"ActorName": change.item, "IsNpcEventStarter": False}
        _set_flag_after(fc, step, change.flag)
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
        _completion_gate(fc, "Buy_BluePotion", change.flag, evfl.NONE)
        return

    entry, success = MERCHANT_SHOPS[change.check]
    specialized = NEW_EVENT_PREFIX + "Purchase" + step.flow
    if flow == step.flow:
        call = fc.events[_index(fc, flow, step.event)]
        if not isinstance(call, evfl.SubFlowEvent) or (call.flowchart, call.entry_point) != ("SimpleShop", entry):
            raise GiftPatchError(f"{step.id}: not the native merchant sale")
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
        cancel = "Event26"
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
        cancel = "Event116"
    prefix = f"{NEW_EVENT_PREFIX}{len(fc.events)}_"
    _clone_entry(fc, entry, replacements, name=specialized)
    if change.check == "GC Medigoron":
        _set_flag_after(fc, replace(step, flow=flow, event=prefix + success), change.flag)
    _completion_gate(fc, specialized, change.flag, _index(fc, flow, prefix + cancel))


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
    grant.next = _index(fc, fc.name, "Event76")  # native tutorial quest completion
    for flag in (
        "Market_Item_Bottle_TutorialEvent_Cleared",
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


def patch_flowchart(fc: evfl.Flowchart, flow: str, changes: Sequence[GiftChange]) -> None:
    """Apply ``changes``' edits that fall in ``flow`` to its flowchart, in place."""
    if flow == BOWLING_FLOW and any(c.check in BOWLING_CHECKS for c in changes):
        _bowling_order(fc)
    for change in changes:
        vanilla = {step.vanilla_item for step in change.steps}
        for step in change.steps:
            if step.flow == flow:
                _set_item(fc, step, change.item)
                if (change.new_flag or change.rule.once) and not change.rule.purchase:
                    _set_flag_after(fc, step, change.flag)
                if change.check == MARKET_BOTTLE_CHECK:
                    _market_bottle(fc, change)
                if change.check == BOWLING_SECOND:
                    # Its native heart-marker flag remains correct when the reward moves to win two.
                    _set_flag_after(fc, step, "MiniGame_BombchuBowling_ClearThirdTime")
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
        if change.rule.purchase:
            _purchase(fc, flow, change)


def flows_changed(changes: Iterable[GiftChange]) -> list[str]:
    out = set()
    for change in changes:
        out |= {step.flow for step in change.steps}
        out |= {
            ref.split("/")[0] for ref in (*change.rule.given, *change.rule.skip, *change.rule.writes, *change.rule.once)
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


# Native reward-preview labels (round 6 hints design note; section 35).
SKULLTULA_HINTS = {
    f"Kak {count} Gold Skulltula Reward": (count, label)
    for count, label in ((10, "Talk_28"), (20, "Talk_23"), (30, "Talk_24"), (40, "Talk_25"), (50, "Talk_26"))
}


def skulltula_hint_changes(romfs: str | Path, placements: Mapping[str, str]) -> dict[str, Callable[[bytes], bytes]]:
    """Name the actual actor at each shuffled 10–50 reward, in the native preview lines.

    English in every language archive follows D26. The repeat 100-token rupee is not a new check.
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
    lines = {}
    for name, actor in selected.items():
        count, label = SKULLTULA_HINTS[name]
        key = text.read_text_key(romfs, actor, dicts)
        item = "".join(p for p in text.item_name(pouch, key) if isinstance(p, str))
        lines[label] = f"For {count} tokens, the reward is {text.FIELD_START}{item}{text.FIELD_END}."

    def transform(data: bytes) -> bytes:
        archive = sarc.read(data)
        file = "EventFlowMsg/Npc_SkullDad.msbt"
        messages = msbt.read(archive[file])
        edits = {label: text.stone_line(messages.messages[label], line) for label, line in lines.items()}
        return text.edit_messages({file: edits})(data)

    return {text.archive_path(language): transform for language in text.languages(romfs)}


# --- seeds --------------------------------------------------------------------------------------------------------

# World event-gift types; the persistent shopkeeper reward is an ordinary NPC check (section 34).
GIFT_TYPES = ("NPC", "Song", "Cutscene", "Boss")
SHUFFLE = "Gift"  # the --shuffle value
SONG_TYPE = "Song"
FREE_TIME_TRAVEL = "free_time_travel"  # the world setting that lifts the anchors
# Gift checks a seed keeps vanilla while adult Link cannot go back freely: the adult-return guarantee (D20) relies on
# them (Saria's Song -> Darunia's Joy gives the child the Goron Bracelet; shuffled strength upgrades are placed
# adult-only).
ANCHORS = {"GC Darunias Joy": "the child's Goron Bracelet anchors the adult-return guarantee (D20)"}


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
        # Native frog songs pay variable rupees, not a literal actor. Round 10's approved
        # pool contribution is fixed at 20; even an unchanged assignment must specialize it.
        if all(s.call == FROG_SONG_CALL for s in steps[name]) and loc.vanilla == "Rupees (20)":
            out.append(name)
            continue
        if name in TIERED_GIFTS:
            item, native = TIERED_GIFTS[name]
            if loc.vanilla == item and {s.vanilla_item for s in steps[name]} == native:
                out.append(name)
            continue
        if {actors.aliases.get(s.vanilla_item, s.vanilla_item) for s in steps[name]} != {
            actors.actors.get(loc.vanilla)
        }:
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
    transforms out, for moved gifts and once-gate normalization (``vanilla``: check -> its logic item)."""
    gifts, definitions = list(gifts), list(definitions)
    steps = check_steps(gifts, definitions)

    def step(placements: Mapping[str, str]) -> dict[str, Callable[[bytes], bytes]]:
        moved = {
            name: actors.actor(placements[name])
            for name in shuffled
            if placements[name] != vanilla[name]
            or rules[name].once
            or name in TIERED_GIFTS
            or name in BOWLING_CHECKS
            or any(s.call == FROG_SONG_CALL for s in steps[name])
        }
        return file_changes(plan(moved, gifts, definitions, rules), files)

    return step


def seed_setup(
    romfs: str | Path, spec: Mapping[str, Any], settings: Settings
) -> tuple[dict[str, Any], Settings, Callable[[Mapping[str, str]], dict[str, Callable[[bytes], bytes]]]]:
    """For ``--shuffle Gift``: the spec with the gifts that cannot move held vanilla, the settings shuffling the
    gift types in place of ``Gift`` and a placement policy from ``settings.songs`` plus the verified chest
    actor list in ``data/settings.toml``), and the patch step to pass to ``make_seed``."""
    if SHUFFLE in settings.shuffle or "NPC" in settings.shuffle:
        spec = shopkeeper_spec(spec)
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
    gift_step = seed_step(shuffled, census, definitions, rules, actors, vanilla, files)

    def step(placements: Mapping[str, str]) -> dict[str, Callable[[bytes], bytes]]:
        hints = skulltula_hint_changes(
            romfs, {name: actors.actor(placements[name]) for name in shuffled if name in SKULLTULA_HINTS}
        )
        return {**gift_step(placements), **hints}

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
