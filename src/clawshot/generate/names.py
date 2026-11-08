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
