"""Versioned generator defaults and verified placement policy; no game resources."""

import tomllib
from pathlib import Path

SETTINGS_TOML = Path(__file__).resolve().parent / "data" / "settings.toml"
with SETTINGS_TOML.open("rb") as stream:
    CATALOG = tomllib.load(stream)
DEFAULTS = CATALOG["defaults"]
