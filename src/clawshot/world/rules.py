"""The rule language: requirements as Python-syntax expressions, compiled to tests over a player state.

The syntax is OoT Randomizer's (``RuleParser.py``, MIT), so its region files translate without rewriting a rule;
``plans/04-world-format.md`` is the reference. A rule is parsed with :mod:`ast` (never evaluated as Python) and
compiled once, when the world is built, into a test ``test(counts, age, tod) -> bool``. Settings are constants at
that point, so a rule that depends only on settings folds to ``True`` or ``False``, and an ``and``/``or`` stops
compiling at the first operand that decides it (as OoT Randomizer does), so a branch switched off by a setting may
name things this engine does not support.
"""

import ast
import operator
import re
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

CHILD = "child"
ADULT = "adult"
AGES = (CHILD, ADULT)

# Time of day, as bits: a region can be reached at day, at night or both.
DAY = 1
NIGHT = 2
ALL_TIMES = DAY | NIGHT

Counts = Mapping[str, int]
Test = Callable[[Counts, str | None, int], bool]

_ESCAPE = re.compile(r"['()[\]-]")
_EVENT_NAME = re.compile(r"[A-Z]\w+")


def escape_name(name: str) -> str:
    """An item's name as an identifier: spaces become ``_``, quotes, brackets and dashes go (OoT Randomizer's
    ``RulesCommon.escape_name``)."""
    return _ESCAPE.sub("", name.replace(" ", "_"))


class RuleError(ValueError):
    """A rule that does not parse or names something the world does not define."""


def _constant(value: bool) -> Test:
    return lambda c, a, t: value


@dataclass(frozen=True)
class Rule:
    """A compiled requirement. ``test`` is a bool when the rule folded to a constant; ``fn`` is always a callable
    (the search's hot path calls it directly). ``reads`` names every count the rule looks at (items, events): its
    result for one age and time of day changes only when one of them does. ``None``: not known."""

    text: str
    test: Test | bool
    reads: frozenset[str] | None = None
    fn: Test = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        test = self.test
        object.__setattr__(self, "fn", _constant(test) if isinstance(test, bool) else test)

    def __call__(self, counts: Counts, age: str | None, tod: int) -> bool:
        return self.fn(counts, age, tod)

    @property
    def always(self) -> bool:
        return self.test is True

    @property
    def never(self) -> bool:
        return self.test is False


@dataclass(frozen=True)
class ItemFacts:
    """What the built-in functions need to know about the item table."""

    names: frozenset[str]
    bottles: tuple[str, ...] = ()
    medallions: tuple[str, ...] = ()
    stones: tuple[str, ...] = ()


@dataclass
class Subrule:
    """An event made from ``here(rule)`` or ``at(region, rule)``: held once ``rule`` passes in ``region``."""

    region: str
    name: str
    node: ast.expr


_AGE = object()  # stands for the evaluating age inside a comparison

_COMPARE: dict[type, Callable[[Any, Any], bool]] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
}

_ARITHMETIC: dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
}

# Built-ins OoT Randomizer has that this engine does not implement yet. Reaching one while compiling is an error
# that names it, rather than a silent ``False``.
UNSUPPORTED = frozenset(
    {
        "has_item_goal",
        "has_full_item_goal",
        "has_all_item_goals",
        "guarantee_hint",
        "item_name",
        "won",
    }
)


def _has(name: str, count: int = 1) -> Test:
    def test(c: Counts, a: str | None, t: int, name: str = name, count: int = count) -> bool:
        return c.get(name, 0) >= count

    return test


def _all(parts: list[Test]) -> Test:
    # Two operands are the common case; a plain lambda is faster than all() over a generator.
    if len(parts) == 2:
        first, second = parts
        return lambda c, a, t: first(c, a, t) and second(c, a, t)
    frozen = tuple(parts)
    return lambda c, a, t: all(part(c, a, t) for part in frozen)


def _any(parts: list[Test]) -> Test:
    if len(parts) == 2:
        first, second = parts
        return lambda c, a, t: first(c, a, t) or second(c, a, t)
    frozen = tuple(parts)
    return lambda c, a, t: any(part(c, a, t) for part in frozen)


def _distinct_at_least(names: tuple[str, ...], count: int) -> Test | bool:
    if count <= 0:
        return True
    if count > len(names):
        return False

    def test(c: Counts, a: str | None, t: int) -> bool:
        return sum(1 for n in names if c.get(n, 0) > 0) >= count

    return test


@dataclass
class Compiler:
    """Compiles rule strings against one world's items, helpers and settings.

    ``helpers`` maps a helper's signature (``"can_use(item)"`` or ``"is_child"``) to its body. ``settings`` holds
    every setting, trick and world flag a rule may name. ``key_counts`` caps a count asked of an item at the number
    the world holds (the remake has fewer keys and locked doors than N64 in some dungeons).
    """

    items: ItemFacts
    helpers: Mapping[str, str]
    settings: Mapping[str, Any]
    key_counts: Mapping[str, int] = field(default_factory=dict)
    subrules: list[Subrule] = field(default_factory=list)
    events_named: set[str] = field(default_factory=set)
    _escaped: dict[str, str] = field(init=False)
    _helpers: dict[str, tuple[list[str], str]] = field(init=False)
    _subrule_keys: dict[tuple[str, str], str] = field(init=False, default_factory=dict)
    _subrule_count: dict[str, int] = field(init=False, default_factory=dict)
    _stack: list[str] = field(init=False, default_factory=list)
    _region: str | None = field(init=False, default=None)
    _reads: set[str] = field(init=False, default_factory=set)
    _where: str = field(init=False, default="")

    def __post_init__(self) -> None:
        self._escaped = {escape_name(n): n for n in sorted(self.items.names)}
        self._helpers = {}
        for signature, body in self.helpers.items():
            if "(" in signature:
                name, params = signature[:-1].split("(", 1)
                self._helpers[name.strip()] = ([p.strip() for p in params.split(",")], body)
            else:
                self._helpers[signature.strip()] = ([], body)

    # entry points

    def compile(self, text: str, region: str | None, where: str) -> Rule:
        """Compile ``text``. ``region`` is the region ``here()`` refers to; ``where`` names the rule in errors."""
        self._region, self._where, self._reads = region, where, set()
        test = self._visit(self._parse(text))
        return Rule(text, test, frozenset(self._reads))

    def compile_subrule(self, subrule: Subrule) -> Rule:
        self._region, self._where, self._reads = subrule.region, f"{subrule.name}", set()
        test = self._visit(subrule.node)
        return Rule(ast.unparse(subrule.node), test, frozenset(self._reads))

    def _has(self, name: str, count: int = 1) -> Test:
        self._reads.add(name)
        return _has(name, count)

    def take_subrules(self) -> list[Subrule]:
        """Subrule events created since the last call, in creation order."""
        taken, self.subrules = self.subrules, []
        return taken

    # helpers

    def _error(self, message: str, node: ast.AST | None = None) -> RuleError:
        at = f" in {ast.unparse(node)!r}" if node is not None else ""
        return RuleError(f"{self._where}: {message}{at}")

    def _parse(self, text: str) -> ast.expr:
        try:
            return ast.parse(text.replace("\n", " ").strip(), mode="eval").body
        except SyntaxError as e:
            raise self._error(f"syntax error in {text!r}: {e.msg}") from None

    def _item_or_event(self, name: str) -> str:
        """A quoted name: an item when the item table has it, an event otherwise."""
        escaped = escape_name(name)
        if escaped in self._escaped:
            return self._escaped[escaped]
        self.events_named.add(name)
        return name

    def _expand(self, name: str, args: list[ast.expr], node: ast.AST) -> Test | bool:
        params, body = self._helpers[name]
        if len(params) != len(args):
            raise self._error(f"helper {name} takes {len(params)} argument(s), got {len(args)}", node)
        if name in self._stack:
            raise self._error(f"helper {name} refers to itself ({' -> '.join([*self._stack, name])})", node)
        # OoT Randomizer substitutes arguments into the body as text (RuleParser.visit_Call).
        for param, arg in zip(params, args, strict=True):
            if isinstance(arg, ast.Name):
                value = arg.id
            elif isinstance(arg, ast.Constant):
                value = repr(arg.value)
            else:
                raise self._error(f"argument to {name} must be a name or a constant", node)
            body = re.sub(rf"\b{re.escape(param)}\b", value, body)
        self._stack.append(name)
        try:
            return self._visit(self._parse(body))
        finally:
            self._stack.pop()

    def _subrule(self, region: str, node: ast.expr) -> Test:
        key = (region, ast.unparse(node))
        name = self._subrule_keys.get(key)
        if name is None:
            number = self._subrule_count.get(region, 0) + 1
            self._subrule_count[region] = number
            name = f"{region} Subrule {number}"
            self._subrule_keys[key] = name
            self.subrules.append(Subrule(region, name, node))
        return self._has(name)

    def _value(self, node: ast.expr) -> Any:
        """A comparison operand or a built-in's argument: a constant, or ``_AGE``."""
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id == "age":
                return _AGE
            if node.id in self.settings:
                return self.settings[node.id]
            if node.id in self._escaped:
                return self._escaped[node.id]
            return node.id
        if isinstance(node, ast.BinOp) and type(node.op) in _ARITHMETIC:
            left, right = self._value(node.left), self._value(node.right)
            if _AGE in (left, right):
                raise self._error("arithmetic on age", node)
            return _ARITHMETIC[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -self._value(node.operand)
        raise self._error(f"cannot use {type(node).__name__} as a value", node)

    def _count(self, node: ast.expr) -> int:
        value = self._value(node)
        if not isinstance(value, int) or isinstance(value, bool):
            raise self._error(f"expected a whole number, got {value!r}", node)
        return value

    # the visitor

    def _visit(self, node: ast.expr) -> Test | bool:
        match node:
            case ast.Constant(value=bool() as value):
                return value
            case ast.Constant(value=str() as value):
                return self._has(self._item_or_event(value))
            case ast.BoolOp():
                return self._bool_op(node)
            case ast.UnaryOp(op=ast.Not(), operand=operand):
                inner = self._visit(operand)
                if isinstance(inner, bool):
                    return not inner
                return lambda c, a, t, inner=inner: not inner(c, a, t)
            case ast.Name(id=name):
                return self._name(name, node)
            case ast.Tuple(elts=[item, count]):
                return self._tuple(item, count, node)
            case ast.Call(func=ast.Name(id=name), args=args, keywords=keywords):
                return self._call(name, args, keywords, node)
            case ast.Compare():
                return self._compare(node)
            case ast.Subscript(value=ast.Name(id=table), slice=ast.Name(id=key)):
                return self._setting_entry(table, key, node)
        raise self._error(f"unsupported expression ({type(node).__name__})", node)

    def _setting_entry(self, table: str, key: str, node: ast.AST) -> bool:
        """``skipped_trials[Forest]``: an entry of a setting that is a table, keyed as OoT Randomizer does
        (``RuleParser.visit_Subscript``: underscores become spaces)."""
        values = self.settings.get(table)
        if not isinstance(values, Mapping):
            raise self._error(f"{table} is not a setting holding a table", node)
        entry = key.replace("_", " ")
        if not isinstance(values.get(entry), bool):
            raise self._error(f"{table} has no true/false entry {entry!r}", node)
        return values[entry]

    def _bool_op(self, node: ast.BoolOp) -> Test | bool:
        is_or = isinstance(node.op, ast.Or)
        parts: list[Test] = []
        for value in node.values:
            part = self._visit(value)
            if isinstance(part, bool):
                if part is is_or:
                    return part  # decides the whole expression; later operands are not compiled
                continue
            parts.append(part)
        if not parts:
            return not is_or
        if len(parts) == 1:
            return parts[0]
        return _any(parts) if is_or else _all(parts)

    def _name(self, name: str, node: ast.AST) -> Test | bool:
        if name in ("at_day", "at_night", "at_dampe_time"):
            return self._time_of_day(name)
        if name in self._helpers:
            return self._expand(name, [], node)
        if name in self._escaped:
            return self._has(self._escaped[name])
        if name in self.settings:
            value = self.settings[name]
            if isinstance(value, str):
                raise self._error(f"setting {name} = {value!r} used as a condition", node)
            return bool(value)
        if name in ("has_bottle", "had_night_start"):
            return self._call(name, [], [], node)
        if name in UNSUPPORTED:
            raise self._error(f"built-in {name} is not supported yet", node)
        if _EVENT_NAME.fullmatch(name):
            event = name.replace("_", " ")
            self.events_named.add(event)
            return self._has(event)
        raise self._error(f"unknown name {name}", node)

    def _tuple(self, item: ast.expr, count: ast.expr, node: ast.AST) -> Test | bool:
        if isinstance(item, ast.Constant) and isinstance(item.value, str):
            name = self._item_or_event(item.value)
        elif isinstance(item, ast.Name):
            if item.id in self._escaped:
                name = self._escaped[item.id]
            elif _EVENT_NAME.fullmatch(item.id):
                name = item.id.replace("_", " ")
                self.events_named.add(name)
            else:
                raise self._error(f"{item.id} is not an item", node)
        else:
            raise self._error("the first value of (item, count) must be an item", node)
        n = min(self._count(count), self.key_counts.get(name, sys.maxsize))
        return True if n <= 0 else self._has(name, n)

    def _time_of_day(self, name: str) -> Test | bool:
        # Without entrance shuffle, OoT Randomizer assumes every time of day can be reached from where the player
        # stands (RuleParser.at_day/at_night: True unless world.ensure_tod_access).
        if not self.settings.get("ensure_tod_access", False):
            return True
        bit = DAY if name == "at_day" else NIGHT
        if name == "at_dampe_time" or "Suns Song" not in self.items.names or "Ocarina" not in self.items.names:
            return lambda c, a, t, bit=bit: bool(t & bit)
        # Sun's Song turns day to night and back (RuleParser.at_day: Ocarina and Suns_Song).
        self._reads.update(("Ocarina", "Suns Song"))
        return lambda c, a, t, bit=bit: bool(t & bit) or (c.get("Ocarina", 0) > 0 and c.get("Suns Song", 0) > 0)

    def _call(self, name: str, args: list[ast.expr], keywords: list[ast.keyword], node: ast.AST) -> Test | bool:
        if name == "here":
            if self._region is None:
                raise self._error("here() outside a region", node)
            if len(args) != 1:
                raise self._error("here() takes one rule", node)
            return self._subrule(self._region, args[0])
        if name == "at":
            if len(args) != 2 or not (isinstance(args[0], ast.Constant) and isinstance(args[0].value, str)):
                raise self._error("at() takes a region name and a rule", node)
            return self._subrule(args[0].value, args[1])
        if name in self._helpers:
            if keywords:
                raise self._error(f"helper {name} takes no keyword arguments", node)
            return self._expand(name, args, node)
        if name in ("at_day", "at_night", "at_dampe_time"):
            return self._time_of_day(name)
        if name == "has_bottle":
            bottles = self.items.bottles
            has_letter = "Rutos Letter" in self.items.names
            self._reads.update((*bottles, "Rutos Letter"))

            def test(c: Counts, a: str | None, t: int) -> bool:
                return any(c.get(b, 0) > 0 for b in bottles) or (has_letter and c.get("Rutos Letter", 0) >= 2)

            return test
        if name == "had_night_start":
            return self.settings.get("starting_tod", "default") in ("sunset", "evening", "midnight", "witching-hour")
        if name in ("has_stones", "has_medallions", "has_dungeon_rewards"):
            count = self._count(args[0]) if len(args) == 1 else None
            if count is None:
                raise self._error(f"{name} takes one count", node)
            names = {
                "has_stones": self.items.stones,
                "has_medallions": self.items.medallions,
                "has_dungeon_rewards": self.items.stones + self.items.medallions,
            }[name]
            self._reads.update(names)
            return _distinct_at_least(names, count)
        if name == "has_hearts":
            if len(args) != 1:
                raise self._error("has_hearts takes one count", node)
            hearts = self._count(args[0])
            self._reads.add("Piece of Heart")
            # OoT Randomizer counts pieces (a Heart Container is four, by alias) plus three starting hearts.
            return lambda c, a, t, hearts=hearts: c.get("Piece of Heart", 0) // 4 + 3 >= hearts
        if name in ("has_all_notes_for_song", "has_ocarina_buttons"):
            # Without shuffled notes OoT Randomizer collects every ocarina button at the start (ItemPool.py,
            # get_pool_core), so both hold; with them, the buttons are items this engine does not track yet.
            if self.settings.get("shuffle_individual_ocarina_notes", False):
                raise self._error(f"built-in {name} with shuffle_individual_ocarina_notes is not supported yet", node)
            return True
        if name == "region_has_shortcuts":
            # OoT Randomizer World.region_has_shortcuts: the region's dungeon is in dungeon_shortcuts. With none
            # set it is False everywhere; naming a dungeon would need each boss room's dungeon, not tracked yet.
            if self.settings.get("dungeon_shortcuts"):
                raise self._error("built-in region_has_shortcuts with dungeon_shortcuts is not supported yet", node)
            return False
        if name == "has_soul":
            return True  # OoT Randomizer's own State.has_soul: enemy souls are not shuffled
        if name == "can_live_dmg":
            values = [self._value(a) for a in args]
            options = {k.arg: self._value(k.value) for k in keywords}
            return self._can_live_dmg(values, options, node)
        if name in UNSUPPORTED:
            raise self._error(f"built-in {name} is not supported yet", node)
        raise self._error(f"unknown function {name}", node)

    def _can_live_dmg(self, values: list[Any], options: dict[str, Any], node: ast.AST) -> Test | bool:
        # OoT Randomizer State.can_live_dmg: unavoidable damage of `hearts`, survivable by damage setting, a fairy
        # (unless allow_revive is False) or Nayru's Love (unless allow_nayrus is False).
        names = ["hearts", "allow_revive", "allow_nayrus"]
        params = {"allow_revive": True, "allow_nayrus": True} | dict(zip(names, values, strict=False)) | options
        if "hearts" not in params:
            raise self._error("can_live_dmg needs a number of hearts", node)
        limit = {"ohko": 0, "quad": 0.75, "double": 1.5, "normal": 3, "half": 6}.get(
            self.settings.get("damage_multiplier", "normal")
        )
        if limit is None:
            return False
        if params["hearts"] < limit:
            return True
        parts: list[Test | bool] = []
        if params["allow_revive"]:
            parts.append(self._visit(self._parse("Fairy")))
        if params["allow_nayrus"]:
            parts.append(self._visit(self._parse("Nayrus_Love and Magic_Meter")))
        tests = [p for p in parts if not isinstance(p, bool)]
        if any(p is True for p in parts):
            return True
        if not tests:
            return False
        return _any(tests)

    def _compare(self, node: ast.Compare) -> Test | bool:
        if len(node.ops) != 1:
            raise self._error("chained comparisons are not supported", node)
        op = type(node.ops[0])
        if op not in _COMPARE:
            raise self._error(f"unsupported comparison {op.__name__}", node)
        # Two plain names compare as names: OoT Randomizer's fast path for helper arguments (item == Bow).
        left, right = self._value(node.left), self._value(node.comparators[0])
        if left is _AGE or right is _AGE:
            other = right if left is _AGE else left
            if other is _AGE or op not in (ast.Eq, ast.NotEq) or not isinstance(other, str):
                raise self._error("age can only be compared (== or !=) with an age name", node)
            if other not in AGES:
                raise self._error(f"{other!r} is not an age", node)
            if op is ast.Eq:
                return lambda c, a, t, other=other: a == other
            return lambda c, a, t, other=other: a != other
        try:
            return bool(_COMPARE[op](left, right))
        except TypeError as e:
            raise self._error(f"cannot compare: {e}", node) from None
