"""UI-neutral presentation metadata around the generator's single settings contract."""

import tomllib
from dataclasses import asdict, fields
from pathlib import Path

from clawshot.generate import FillError, Settings, hints, prepare
from clawshot.generate.fill import DUNGEON_ITEM_CHOICES
from clawshot.patch import gamedata, gifts
from clawshot.settings import CATALOG
from clawshot.world.load import WorldError, load_spec

METADATA_PATH = Path(__file__).with_name("settings.toml")


def schema() -> list[dict]:
    metadata = tomllib.loads(METADATA_PATH.read_text(encoding="utf-8"))
    names = {field.name for field in fields(Settings)}
    if names != metadata.keys():
        raise ValueError(
            f"Settings metadata mismatch: missing={names - metadata.keys()}, stale={metadata.keys() - names}"
        )
    choices = {
        "forest": list(CATALOG["forest"]),
        "dungeon_items": list(DUNGEON_ITEM_CHOICES),
        "hint_distribution": list(hints.distributions()),
        "hints": list(hints.MODES),
        "fast_start": [name for name in gamedata.load() if name not in ("mido", "forest_exit")],
    }
    defaults = asdict(Settings())
    result = []
    for field in fields(Settings):
        info = dict(metadata[field.name])
        for key in ("label", "kind", "group", "help"):
            if not info.get(key):
                raise ValueError(f"Settings metadata missing {field.name}.{key}")
        info.update(
            key=field.name, default=defaults[field.name], choices=choices.get(field.name, info.get("choices", []))
        )
        labels = info.pop("labels", {})
        unavailable = info.pop("unavailable", {})
        choice_help = info.pop("choice_help", {})
        if set(choice_help) != set(info["choices"]) or any(not text.strip() for text in choice_help.values()):
            raise ValueError(f"Choice help missing/stale for {field.name}")
        for condition in info.get("enabled_when", []):
            operations = {"contains", "equals", "greater_than"} & condition.keys()
            if condition.get("key") not in names or len(operations) != 1 or not condition.get("reason"):
                raise ValueError(f"Invalid dependency metadata for {field.name}")
        if set(labels) != set(info["choices"]):
            raise ValueError(f"Choice labels missing/stale for {field.name}: {set(info['choices']) ^ set(labels)}")
        info["options"] = [
            {
                "value": choice,
                "label": labels[choice],
                "help": choice_help[choice],
                "disabled": choice in unavailable,
                "reason": unavailable.get(choice, ""),
            }
            for choice in info["choices"]
        ]
        result.append(info)
    return result


def validate(values: dict | None = None, *, text: str | None = None, spec: dict | None = None) -> Settings:
    """Decode or construct, enforce presentation types, then compile with the actual logic oracle.

    No dump needed. ``spec`` permits a caller's synthetic/custom world without introducing a UI-only world.
    Held modes are refused here; the seed pipeline independently enforces its own physical restrictions.
    """
    if text is not None:
        if not isinstance(text, str) or len(text) > 32768:
            raise ValueError("settings string must be text of at most 32768 characters")
        settings = Settings.from_string(text.strip())
        values = asdict(settings)
    elif not isinstance(values, dict):
        raise ValueError("settings must be an object")
    defaults = asdict(Settings())
    known = {item["key"]: item for item in schema()}
    if unknown := values.keys() - known.keys():
        raise ValueError(f"unknown settings: {sorted(unknown)}")
    merged = defaults | values
    shuffle = merged.get("shuffle")
    if (
        isinstance(shuffle, (list, tuple))
        and all(isinstance(kind, str) for kind in shuffle)
        and set(gifts.GIFT_TYPES).issubset(shuffle)
    ):
        merged["shuffle"] = [kind for kind in shuffle if kind not in gifts.GIFT_TYPES] + [gifts.SHUFFLE]
    for key, info in known.items():
        value = merged[key]
        kind = info["kind"]
        if kind == "boolean" and type(value) is not bool:
            raise ValueError(f"{info['label']} must be a boolean")
        if kind == "integer" and (type(value) is not int or not info["min"] <= value <= info["max"]):
            raise ValueError(f"{info['label']} must be an integer from {info['min']} to {info['max']}")
        if kind == "choice" and value not in info["choices"]:
            raise ValueError(f"{info['label']} must be one of {info['choices']}")
        if kind == "multi" and (not isinstance(value, (list, tuple)) or any(v not in info["choices"] for v in value)):
            raise ValueError(f"{info['label']} must select from {info['choices']}")
        selected = value if kind == "multi" else [value] if kind == "choice" else []
        for option in info["options"]:
            if option["disabled"] and option["value"] in selected:
                raise ValueError(f"{option['label']}: {option['reason']}")
    settings = Settings(**merged)
    if settings.areas and not settings.goal:
        raise ValueError("Playtest areas require a goal")
    try:
        prepare(load_spec() if spec is None else spec, settings)
    except (FillError, WorldError) as error:
        raise ValueError(str(error)) from error
    return settings


def settings_payload(settings: Settings) -> dict:
    values = asdict(settings)
    inactive = {}
    for info in schema():
        for condition in info.get("enabled_when", []):
            value = values[condition["key"]]
            if "contains" in condition:
                enabled = condition["contains"] in value
            elif "equals" in condition:
                enabled = value == condition["equals"]
            else:
                enabled = value > condition["greater_than"]
            if not enabled:
                inactive[info["key"]] = condition["reason"]
                break
    return {"values": values, "settings_string": settings.to_string(), "inactive": inactive}


def presets(*, spec: dict | None = None) -> list[dict]:
    data = tomllib.loads(Path(__file__).with_name("presets.toml").read_text(encoding="utf-8"))
    return [
        {
            "id": key,
            "label": info["label"],
            "help": info["help"],
            **settings_payload(validate(info["values"], spec=spec)),
        }
        for key, info in data.items()
    ]


def input_schema() -> dict:
    """Descriptions for application inputs and job stages, without a front-end dependency."""
    return tomllib.loads(Path(__file__).with_name("inputs.toml").read_text(encoding="utf-8"))
