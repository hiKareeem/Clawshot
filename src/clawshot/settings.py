"""Versioned generator defaults and verified placement policy; no game resources."""

import tomllib
from pathlib import Path

SETTINGS_TOML = Path(__file__).resolve().parent / "data" / "settings.toml"
with SETTINGS_TOML.open("rb") as stream:
    CATALOG = tomllib.load(stream)
DEFAULTS = CATALOG["defaults"]


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
