"""Event props: which actor of which event shows which check's item (spec event-items 2.1, plan task 4).

``event_props.toml`` lists each prop (an actor of an event's flowchart or timeline, or a placed object) with its
check and the vanilla item it stands for, and sorts every other item actor the census finds
(:func:`clawshot.census.event_items.scan_prop_actors`) into a named exclusion with its reason. A ``hand`` entry is a
bind the event does not have: the given item's container bound to an actor's bone from one cut (entry point) until
another, for an event whose native item comes from that actor's own animation (Link's look in the moat scene shows
his equipped ocarina; played run E10, BBender 2026-11-26). A flowchart prop's ``scene_as`` names the scene animation
set its event plays on it (D20: a song container's effect user answers those animations).
``tests/test_event_props_dump.py`` keeps the file in step with the dump.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

from clawshot.census.event_items import FLOWCHART, TIMELINE, prop_id
from clawshot.patch.plan import PatchError

PROPS_TOML = Path(__file__).with_name("event_props.toml")
PLACEMENT = "placement"
PARTS = (FLOWCHART, TIMELINE, PLACEMENT)
PROP_FIELDS = {"check", "item", "event", "part", "actor", "secondary", "grant", "banc", "hash", "scene_as"}
EXCLUDE_FIELDS = {"reason", "actors", "events"}
HAND_FIELDS = ("check", "item", "event", "template", "target", "bone", "start", "end")


class EventPropsError(PatchError):
    pass


@dataclass(frozen=True)
class Prop:
    check: str  # gift check (gift_rules.toml) or dungeon reward slot (data/dungeon_rewards.toml)
    item: str  # the vanilla item actor the prop stands for
    part: str  # FLOWCHART, TIMELINE or PLACEMENT
    actor: str
    secondary: str = ""
    event: str = ""  # the flow file; empty for a placed object
    grant: str = ""  # "<flow>/<event>" of the branch's grant, for a branch pair (D13)
    banc: str = ""  # placement file, for a placed object
    hash: int = 0  # the placed actor's Hash
    scene_as: str = ""  # a flowchart prop's scene animation set (its event's EventAS; D20)

    @property
    def id(self) -> str:
        if self.part == PLACEMENT:
            return f"{self.banc}/{self.hash}"
        return prop_id(self.event, self.part, self.actor, self.secondary)


@dataclass(frozen=True)
class HandBind:
    check: str
    item: str  # the vanilla item the actor's own animation shows
    event: str  # the flow file
    template: str  # a flowchart actor whose bind and offstage actions (and first events of them) are copied
    target: str  # the actor whose bone takes the container (the bind's ActorName)
    bone: str
    start: str  # entry point (cut) before which the container is bound
    end: str  # entry point (cut) before which it goes offstage


@dataclass(frozen=True)
class Exclusion:
    name: str
    reason: str
    actors: tuple[str, ...] = ()  # prop ids
    events: tuple[str, ...] = ()  # every item actor of these events


@dataclass(frozen=True)
class EventProps:
    props: tuple[Prop, ...]
    exclusions: dict[str, Exclusion]
    hands: tuple[HandBind, ...] = ()

    def excluded(self, actor_id: str) -> str | None:
        """The name of the exclusion that covers ``actor_id``, or None."""
        event = actor_id.split("/", 1)[0]
        for exclusion in self.exclusions.values():
            if actor_id in exclusion.actors or event in exclusion.events:
                return exclusion.name
        return None


def _str(where: str, entry: dict, key: str, required: bool = True) -> str:
    value = entry.get(key, "")
    if not isinstance(value, str) or (required and not value):
        raise EventPropsError(f"{where}: {key} must be a non-empty string")
    return value


def _prop(entry: dict) -> Prop:
    where = f"prop {entry.get('check', '?')}/{entry.get('actor', '?')}"
    unknown = set(entry) - PROP_FIELDS
    if unknown:
        raise EventPropsError(f"{where}: unknown fields {sorted(unknown)}")
    part = entry.get("part")
    if part not in PARTS:
        raise EventPropsError(f"{where}: part {part!r}, expected one of {PARTS}")
    grant = _str(where, entry, "grant", required=False)
    if grant and (grant.count("/") != 1 or not all(grant.split("/"))):
        raise EventPropsError(f"{where}: grant {grant!r} is not '<flow>/<event>'")
    common = dict(
        check=_str(where, entry, "check"),
        item=_str(where, entry, "item"),
        part=part,
        actor=_str(where, entry, "actor"),
        secondary=_str(where, entry, "secondary", required=False),
        grant=grant,
    )
    if part == PLACEMENT:
        value = entry.get("hash")
        if type(value) is not int or "event" in entry or "scene_as" in entry:
            raise EventPropsError(f"{where}: a placed object needs banc and an integer hash, and no event or scene_as")
        return Prop(**common, banc=_str(where, entry, "banc"), hash=value)
    if "banc" in entry or "hash" in entry:
        raise EventPropsError(f"{where}: banc and hash belong to part {PLACEMENT!r}")
    scene_as = _str(where, entry, "scene_as", required=False)
    if "scene_as" in entry and (part != FLOWCHART or not scene_as or "/" in scene_as):
        raise EventPropsError(f"{where}: scene_as must be an animation set name, on a {FLOWCHART} prop")
    return Prop(**common, event=_str(where, entry, "event"), scene_as=scene_as)


def _hand(entry: dict) -> HandBind:
    where = f"hand {entry.get('check', '?')}/{entry.get('event', '?')}"
    if set(entry) != set(HAND_FIELDS):
        raise EventPropsError(f"{where}: needs exactly {list(HAND_FIELDS)}")
    return HandBind(*(_str(where, entry, key) for key in HAND_FIELDS))


def loads(text: str) -> EventProps:
    data = tomllib.loads(text)
    hands = tuple(_hand(entry) for entry in data.get("hand", []))
    props = tuple(_prop(entry) for entry in data.get("prop", []))
    exclusions = {}
    for name, entry in data.get("exclude", {}).items():
        unknown = set(entry) - EXCLUDE_FIELDS
        if unknown:
            raise EventPropsError(f"exclude {name}: unknown fields {sorted(unknown)}")
        exclusions[name] = Exclusion(
            name,
            _str(f"exclude {name}", entry, "reason"),
            tuple(entry.get("actors", ())),
            tuple(entry.get("events", ())),
        )
    ids = [p.id for p in props] + [a for e in exclusions.values() for a in e.actors]
    twice = sorted({i for i in ids if ids.count(i) > 1})
    if twice:
        raise EventPropsError(f"listed twice: {twice}")
    out = EventProps(props, exclusions, hands)
    covered = sorted(p.id for p in props if p.part != PLACEMENT and out.excluded(p.id) is not None)
    if covered:
        raise EventPropsError(f"props inside an excluded event: {covered}")
    return out


def load(path: str | Path = PROPS_TOML) -> EventProps:
    return loads(Path(path).read_text(encoding="utf-8"))
