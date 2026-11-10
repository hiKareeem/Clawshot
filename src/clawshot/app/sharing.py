"""Player share strings bind the existing canonical CS1 settings to one generator version."""

from importlib.metadata import version

from clawshot.app.schema import settings_payload, validate


def share_settings(text: str, generator_version: str | None = None) -> str:
    return f"Clawshot-{generator_version or version('clawshot')}:{text}"


def player_settings(settings) -> dict:
    payload = settings_payload(settings)
    return payload | {"share_string": share_settings(payload["settings_string"])}


def import_settings(text: str, *, spec=None):
    if not isinstance(text, str):
        raise ValueError("Paste the whole settings string copied from Clawshot.")
    prefix, separator, canonical = text.strip().partition(":")
    expected = "Clawshot-" + version("clawshot")
    if not separator or not prefix.startswith("Clawshot-"):
        raise ValueError("Paste the whole settings string copied from Clawshot, including its version.")
    if prefix != expected:
        raise ValueError(f"This string needs {prefix}. Open that version of Clawshot to make the same seed.")
    return validate(text=canonical, spec=spec)
