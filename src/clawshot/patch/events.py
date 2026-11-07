"""Chest open-event overrides (``GetEventName``) and what the patch does with each (``chest_events.toml``)."""

import tomllib
from dataclasses import dataclass
from pathlib import Path

CHEST_EVENTS_TOML = Path(__file__).resolve().with_name("chest_events.toml")
REMOVE = "remove"
KEEP = "keep"


class ChestEventError(ValueError):
    pass


@dataclass(frozen=True)
class ChestEvent:
    name: str
    flow: str
    patch: str
    """``remove`` (the override is tied to the vanilla item) or ``keep``."""
    does: str
    story_state: str | None
    """For a removed override: the state it leaves that the default event does not, and how a seed restores it."""


def loads(text: str) -> dict[str, ChestEvent]:
    out = {}
    for name, entry in tomllib.loads(text).get("event", {}).items():
        patch = entry.get("patch")
        if patch not in (REMOVE, KEEP):
            raise ChestEventError(f"chest_events.toml: {name}: patch must be {REMOVE!r} or {KEEP!r}, not {patch!r}")
        story = entry.get("story_state")
        if (patch == REMOVE) != (story is not None):
            raise ChestEventError(f"chest_events.toml: {name}: story_state is required with remove, and only there")
        out[name] = ChestEvent(name, str(entry.get("flow", "")), patch, str(entry.get("does", "")), story)
    return out


def load(path: str | Path = CHEST_EVENTS_TOML) -> dict[str, ChestEvent]:
    return loads(Path(path).read_text(encoding="utf-8"))
