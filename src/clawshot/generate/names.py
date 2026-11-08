"""Player-facing labels; world identities, placements and access rules stay unchanged."""

import tomllib
from dataclasses import dataclass
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "data" / "location_names.toml"


@dataclass(frozen=True)
class LocationName:
    name: str
    where: str
    oot_randomizer_name: str
    source: str
    ids: tuple[str, ...]


def load(path: Path = CATALOG) -> dict[str, LocationName]:
    """Read one description per logical check, with all physical copies/flow steps attached."""
    rows = tomllib.loads(path.read_text(encoding="utf-8"))["location"]
    result = {}
    for row in rows:
        key = row["location"]
        if key in result:
            raise ValueError(f"two location descriptions for {key!r}")
        result[key] = LocationName(
            row["name"], row["where"], row["oot_randomizer_name"], row["source"], tuple(row["ids"])
        )
    return result


def shops() -> dict[str, dict]:
    """Physical-slot prices and release predicates, independent of shelf contents."""
    data = tomllib.loads((CATALOG.parent / "shops.toml").read_text(encoding="utf-8"))
    result = {}
    for slot in data["slot"]:
        name = slot["location"]
        if name in result:
            result[name]["price"] = max(result[name]["price"], slot["price"])
            continue
        rule = data.get("availability", {}).get(name, {}).get("rule", "True")
        release = (
            "No additional shelf-release gate"
            if rule == "True"
            else rule.replace("is_adult", "adult Link").replace("is_child", "child Link").replace("_", " ")
        )
        result[name] = {"price": slot["price"], "opens": release, "release_rule": rule}
    return result
