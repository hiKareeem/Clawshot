"""Apply shop identities, native item capabilities and wallet rules from shops.toml.

The catalog is separate from the mechanically translated N64 world. No dump reads
or patch-layer imports are needed to build/search a world.
"""

from collections.abc import Mapping
from typing import Any

from clawshot.settings import shop_price


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
    price_rules = spec.setdefault("shop_price_rules", {})
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
        price = shop_price(copies[0]["shop"], copies[0]["vanilla_item"], max(slot["price"] for slot in copies))
        old = regions[name]["locations"][name]
        old_rule = old if isinstance(old, str) else old["rule"]
        availability = data.get("availability", {}).get(name, {}).get("rule", "True")
        price_rules[name] = {
            "shop": copies[0]["shop"],
            "actor": copies[0]["vanilla_item"],
            "price": max(slot["price"] for slot in copies),
            "base_rule": f"({old_rule}) and ({availability})",
            "wallet": data["wallet"],
        }
        regions[name]["locations"][name] = _priced_rule(price_rules[name], price)


def _priced_rule(entry: Mapping[str, Any], price: int) -> dict[str, str]:
    wallet = next((tier["rule"] for tier in entry["wallet"] if price <= tier["capacity"]), "False")
    return {
        "rule": f"({entry['base_rule']}) and ({wallet})",
        "source": f"shops.toml/settings.toml: price {price}; 200/500/1000 wallets; original shelf releases",
    }


def with_shop_prices(
    spec: Mapping[str, Any], shuffle: tuple[str, ...], policy: str, cheap_shield: bool
) -> Mapping[str, Any]:
    """Recompile only price predicates on a copy; no old wallet clause survives affordable mode."""
    entries = spec.get("shop_price_rules", {})
    if not entries:
        return spec
    rules = {}
    for name, entry in entries.items():
        # Kokiri's original slots all fit the starting wallet (5–40 rupees); moving a cheap
        # shield within that shop cannot change its wallet tier. Affordable is slot-wide.
        info = spec["locations"][name]
        shuffled = "Shop" in shuffle and not info.get("keep_vanilla") and not info.get("n64_only")
        price = shop_price(
            entry["shop"], entry["actor"], entry["price"], shuffled=shuffled, policy=policy, cheap_shield=cheap_shield
        )
        rules[name] = _priced_rule(entry, price)
    regions = []
    for region in spec["regions"]:
        locations = region.get("locations", {})
        if locations.keys() & rules.keys():
            region = {**region, "locations": {name: rules.get(name, rule) for name, rule in locations.items()}}
        regions.append(region)
    return {**spec, "regions": regions}
