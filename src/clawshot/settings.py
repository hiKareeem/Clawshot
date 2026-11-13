"""Versioned generator defaults and verified placement policy; no game resources."""

import json
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

SETTINGS_TOML = Path(__file__).resolve().parent / "data" / "settings.toml"
with SETTINGS_TOML.open("rb") as stream:
    CATALOG = tomllib.load(stream)
DEFAULTS = CATALOG["defaults"]


def validate_logic_overrides(spec: Mapping[str, Any], logic: Mapping[str, Any]) -> None:
    """Native seed policy; the settings codec and standalone logic models remain generic."""
    world_settings = spec.get("settings", {})
    defaults = {**world_settings, **spec.get("tricks", {}), **spec.get("flags", {})}
    for name, value in logic.items():
        source = CATALOG["logic_override_modes"].get(name)
        if source and name in world_settings and "door_of_time" in world_settings and source in world_settings:
            # prepare() always regenerates these fields from the selected door mode.
            # Stored effective recipes cannot override the current world's return kit.
            continue
        allowed = list(CATALOG["logic_overrides"].get(name, ()))
        if name in defaults:
            allowed.append(defaults[name])
        if source:
            allowed.extend(defaults.get(source, {}).values())
        # JSON comparison keeps Bool distinct from integer 0/1, including nested inventories.
        encoded = json.dumps(value, sort_keys=True, allow_nan=False)
        if not any(encoded == json.dumps(option, sort_keys=True, allow_nan=False) for option in allowed):
            raise ValueError(
                f"{name}={value!r} isn't supported in the remake yet (no game change makes this logic override true)"
            )


def shop_price(
    shop: str,
    actor: str,
    vanilla: int,
    *,
    shuffled: bool = False,
    policy: str = DEFAULTS["shop_prices"],
    cheap_shield: bool = DEFAULTS["cheap_deku_shield"],
) -> int:
    """One price decision shared by the overlay and the logic (not an economy simulation)."""
    prices = CATALOG["prices"]
    if (shuffled and policy == "affordable") or (
        cheap_shield and shop == prices["shield_shop"] and actor == prices["shield_actor"]
    ):
        return prices["affordable"]
    return vanilla
