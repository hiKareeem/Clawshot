"""UI-independent Clawshot application API."""

from clawshot.app.jobs import STAGES, GenerationRequest, Jobs
from clawshot.app.paths import detect_dump, detect_game
from clawshot.app.play import Player, play_plan
from clawshot.app.schema import input_schema, presets, schema, settings_payload, validate

__all__ = [
    "STAGES",
    "GenerationRequest",
    "Jobs",
    "Player",
    "detect_dump",
    "detect_game",
    "input_schema",
    "presets",
    "play_plan",
    "schema",
    "settings_payload",
    "validate",
]
