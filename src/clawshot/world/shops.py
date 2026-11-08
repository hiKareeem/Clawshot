"""Apply shop identities, native item capabilities and wallet rules from shops.toml.

The catalog is separate from the mechanically translated N64 world. No dump reads
or patch-layer imports are needed to build/search a world.
"""

from collections.abc import Mapping
from typing import Any


def apply_shop_data(spec: dict[str, Any], data: Mapping[str, Any]) -> None:
    native = data["items"]
    by_actor = {entry["display"]: name for name, entry in native.items()}
    settings = spec.setdefault("settings", {})
    settings["native_shop_items"] = [*native, *data.get("display_aliases", {})]
    settings["shop_item_locations"] = data.get("item_locations", {})
    spec.setdefault("helpers", {}).update(data.get("helpers", {}))
    for name, entry in native.items():
        old = spec.setdefault("items", {}).get(name, {})
        spec["items"][name] = {**old, "class": entry["class"]}
    regions = {name: region for region in spec["regions"] for name in region.get("locations", {})}
    slots = {}
    for slot in data["slot"]:
        if slot["vanilla_item"] in by_actor:
            slots.setdefault(slot["location"], []).append(slot)
    for name, copies in slots.items():
        if name not in regions:
            continue  # A caller may load a region subset.
        actors = {slot["vanilla_item"] for slot in copies}
        if len(actors) != 1:
            raise ValueError(f"shops.toml: conflicting vanilla items for {name}: {sorted(actors)}")
        item = by_actor[next(iter(actors))]
        info = spec["locations"][name]
        if info["type"] != "Shop":
            raise ValueError(f"shops.toml: {name} is not a Shop location")
        spec["locations"][name] = {**info, "vanilla": item, "override": "shops.toml: shelf/seller census"}
        price = max(slot["price"] for slot in copies)
        wallet = next((tier["rule"] for tier in data["wallet"] if price <= tier["capacity"]), "False")
        old = regions[name]["locations"][name]
        old_rule = old if isinstance(old, str) else old["rule"]
        availability = data.get("availability", {}).get(name, {}).get("rule", "True")
        regions[name]["locations"][name] = {
            "rule": f"({old_rule}) and ({wallet}) and ({availability})",
            "source": f"shops.toml: price {price}; 200/500/1000 wallets; original shelf releases",
        }
