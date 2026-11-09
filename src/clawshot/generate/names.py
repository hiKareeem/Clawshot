"""Player-facing labels; world identities, placements and access rules stay unchanged."""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from clawshot.settings import shop_price

if TYPE_CHECKING:
    from clawshot.generate import Seed

CATALOG = Path(__file__).resolve().parents[1] / "data" / "location_names.toml"


@dataclass(frozen=True)
class LocationName:
    name: str
    where: str
    oot_randomizer_name: str
    source: str
    ids: tuple[str, ...]
    floor: str


def load(path: Path = CATALOG) -> dict[str, LocationName]:
    """Read one description per logical check, with all physical copies/flow steps attached."""
    rows = tomllib.loads(path.read_text(encoding="utf-8"))["location"]
    result = {}
    for row in rows:
        key = row["location"]
        if key in result:
            raise ValueError(f"two location descriptions for {key!r}")
        floor = row.get("floor", "")
        source = row["source"]
        if floor:
            source += "; floor: Banc/BancBasedResource/MapParam.byml.zs (e0f3ccfa), section39."
        result[key] = LocationName(
            row["name"] + (f" ({floor})" if floor else ""),
            row["where"],
            row["oot_randomizer_name"],
            source,
            tuple(row["ids"]),
            floor,
        )
    return result


def shops(seed: "Seed") -> dict[str, dict]:
    """Actual sale prices from the canonical policy, plus physical shelf-release predicates."""
    data = tomllib.loads((CATALOG.parent / "shops.toml").read_text(encoding="utf-8"))
    native = data["items"]
    aliases = data.get("display_aliases", {})
    result = {}
    for slot in data["slot"]:
        name = slot["location"]
        if name not in seed.placements:
            continue
        item = seed.placements[name]
        display = native.get(aliases.get(item, item), {}).get("display", slot["vanilla_item"])
        price = shop_price(
            slot["shop"],
            display,
            slot["price"],
            shuffled=name in seed.shuffled,
            policy=seed.settings.shop_prices,
            cheap_shield=seed.settings.cheap_deku_shield,
        )
        if name in result:
            result[name]["price"] = max(result[name]["price"], price)
            continue
        rule = data.get("availability", {}).get(name, {}).get("rule", "True")
        release = (
            "No additional shelf-release gate"
            if rule == "True"
            else rule.replace("is_adult", "adult Link").replace("is_child", "child Link").replace("_", " ")
        )
        result[name] = {"price": price, "opens": release, "release_rule": rule}
    return result
