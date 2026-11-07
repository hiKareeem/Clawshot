"""The committed location definitions, ``src/clawshot/data/locations.toml`` (decisions D4, D5).

One ``[[location]]`` table per check: ``id`` (the actor Hash, in decimal, as a string because TOML integers are
signed 64-bit), ``kind``, ``area``, ``name`` (readable, unique), ``vanilla_item`` (actor name) and
``oot_randomizer_name`` (empty where no OoT Randomizer location is the same check). Identifiers and names only:
no game data.
"""

import re
import tomllib
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from clawshot.census.ootr import OOTR_COMMIT, Match, shops, spots
from clawshot.census.scan import GOLD_SKULLTULA, HEART_CONTAINER, SHOP_SLOT, Location

LOCATIONS_TOML = Path(__file__).resolve().parents[1] / "data" / "locations.toml"
FIELDS = ("id", "kind", "area", "name", "vanilla_item", "oot_randomizer_name")

HEADER = f"""\
# Clawshot location definitions: one [[location]] per check in the remake (plans/decisions.md D4, D5).
#   id                   the actor Hash (decimal; a string, as TOML integers are signed 64-bit)
#   kind, area           census kind and Banc folder; vanilla_item: the actor name the check gives
#   name                 readable and unique
#   oot_randomizer_name  the OoT Randomizer location that is the same check, empty where none or unsure:
#                        LocationList.py (MIT) of https://github.com/OoTRandomizer/OoT-Randomizer
#                        at commit {OOTR_COMMIT}
# Written by `python -m clawshot.census.write_locations` from the player's dump. name and oot_randomizer_name may
# be edited by hand: a rewrite keeps them for every id already in this file.
"""


class DefinitionError(ValueError):
    pass


@dataclass(frozen=True)
class Definition:
    id: int
    kind: str
    area: str
    name: str
    vanilla_item: str
    oot_randomizer_name: str


def loads(text: str) -> list[Definition]:
    rows = tomllib.loads(text).get("location", [])
    out = []
    for row in rows:
        if set(row) != set(FIELDS):
            raise DefinitionError(f"location {row.get('id')}: fields {sorted(row)}, expected {sorted(FIELDS)}")
        out.append(Definition(int(row["id"]), *(str(row[f]) for f in FIELDS[1:])))
    ids = Counter(d.id for d in out)
    names = Counter(d.name for d in out)
    duplicates = [i for i, n in ids.items() if n > 1] + [s for s, n in names.items() if n > 1]
    if duplicates:
        raise DefinitionError(f"duplicate ids or names: {duplicates}")
    return out


def load(path: str | Path = LOCATIONS_TOML) -> list[Definition]:
    return loads(Path(path).read_text(encoding="utf-8"))


def _quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def dumps(definitions: Iterable[Definition]) -> str:
    parts = [HEADER]
    for d in definitions:
        parts.append("\n[[location]]\n")
        parts.append(f"id = {_quote(str(d.id))}\n")
        for field in FIELDS[1:]:
            parts.append(f"{field} = {_quote(getattr(d, field))}\n")
    return "".join(parts)


def words(camel: str) -> str:
    """``InsideTheDekuTree`` -> ``Inside The Deku Tree``."""
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", camel)


def variant(location: Location) -> str:
    """Which placement files hold a location, for telling copies apart: ``Child``, ``Adult Alternative``, ..."""
    labels = []
    for path in location.files:
        stem = PurePosixPath(path).name.split(".")[0]
        label = stem.removeprefix(location.area).strip("_").rsplit("_", 1)[0].replace("_", " ")
        if label and label not in labels:
            labels.append(label)
    return ", ".join(labels) or "all"


def generated_name(location: Location) -> str:
    name = words(location.area)
    if location.room is not None:
        name += f" Room {location.room}"
    name += " " + words(location.kind.replace("_", " ").title().replace(" ", ""))
    if location.kind == SHOP_SLOT:
        name += f" Slot {location.shop_slot}"
    if location.kind not in (GOLD_SKULLTULA, HEART_CONTAINER) and location.vanilla_item:
        name += f" ({location.vanilla_item})"
    return name


def _group_sizes(locations: Sequence[Location]) -> dict[int, int]:
    """For each Hash, how many locations share its spot (copies) or shop slot."""
    size: dict[int, int] = {}
    for spot in spots(locations):
        for loc in spot:
            size[loc.id] = len(spot)
    for locs in shops(locations).values():
        per_slot = Counter(loc.shop_slot for loc in locs)
        for loc in locs:
            size[loc.id] = per_slot[loc.shop_slot]
    return size


def build(
    locations: Sequence[Location], matches: Mapping[int, Match], existing: Mapping[int, Definition] = {}
) -> list[Definition]:
    """Definitions for the census, in its order. ``name`` and ``oot_randomizer_name`` come from ``existing`` where it
    has the id (hand edits), otherwise from ``matches`` or a generated name. Names are made unique with a suffix."""
    group = _group_sizes(locations)
    base: dict[int, str] = {}
    ootr: dict[int, str] = {}
    for loc in locations:
        match = matches.get(loc.id)
        ootr[loc.id] = match.name if match else ""
        name = match.name if match else generated_name(loc)
        if group.get(loc.id, 1) > 1:
            name += f" [{variant(loc)}]"
        base[loc.id] = name
    used = {d.name for i, d in existing.items() if i in base}
    new_counts = Counter(base[loc.id] for loc in locations if loc.id not in existing)
    index: dict[str, int] = defaultdict(int)
    out = []
    for loc in locations:
        if loc.id in existing:
            name, oot_name = existing[loc.id].name, existing[loc.id].oot_randomizer_name
        else:
            name, oot_name = base[loc.id], ootr[loc.id]
            if new_counts[name] > 1 or name in used:
                stem = name
                while name in used or name == stem:
                    index[stem] += 1
                    name = f"{stem} #{index[stem]}"
            used.add(name)
        out.append(Definition(loc.id, loc.kind, loc.area, name, loc.vanilla_item, oot_name))
    names = Counter(d.name for d in out)
    duplicates = sorted(n for n, c in names.items() if c > 1)
    if duplicates:
        raise DefinitionError(f"names used twice: {duplicates}")
    return out
