"""Small atomic path preferences in the user's config folder; never in the checkout."""

import json
import os
import sys
import threading
from pathlib import Path
from tempfile import NamedTemporaryFile

from clawshot.app.paths import SOURCE_ROOT

KEYS = {"dump", "update", "hookshot", "emulator_mods"}  # update: a separate update; "" when the dump has it


def _valid_value(key, value):
    if key == "seed_roots":
        return isinstance(value, list) and all(isinstance(path, str) for path in value)
    return key in KEYS and isinstance(value, str)


def user_preferences_path() -> Path:
    if sys.platform == "win32":
        parent = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming")) / "Clawshot"
    elif sys.platform == "darwin":
        parent = Path.home() / "Library/Application Support/Clawshot"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        parent = (base if base.is_absolute() else Path.home() / ".config") / "clawshot"
    return parent / "paths.json"


def suggested_eden_folder() -> str | None:
    if sys.platform != "win32" or not os.environ.get("APPDATA"):
        return None
    path = Path(os.environ["APPDATA"]) / "eden/load/0400486024DEC000"
    return str(path.resolve()) if path.is_dir() else None


class Preferences:
    """None explicitly means in-memory for embedded/test servers; CLI supplies the user path."""

    def __init__(self, path: Path | None = None):
        self.lock = threading.RLock()
        self.path = Path(path).resolve() if path is not None else None
        self.values = {}
        self.warning = ""
        if self.path is not None:
            if self.path.is_relative_to(SOURCE_ROOT):
                raise ValueError("Clawshot's configuration folder must be outside its source folder.")
            try:
                if self.path.exists():
                    data = json.loads(self.path.read_text(encoding="utf-8"))
                    if not isinstance(data, dict) or any(not _valid_value(k, v) for k, v in data.items()):
                        raise ValueError("invalid saved folders")
                    self.values = data
            except (OSError, ValueError, UnicodeError):
                self.warning = "Saved folders could not be read. Choose your folders again to remember them."

    def snapshot(self) -> dict:
        with self.lock:
            return {key: list(value) if isinstance(value, list) else value for key, value in self.values.items()}

    def remember(self, key: str, value: str | list[str]) -> str:
        if not _valid_value(key, value):
            raise ValueError("Unknown saved folder.")
        with self.lock:
            if self.values.get(key) == value and not self.warning:
                return ""
            self.values[key] = list(value) if isinstance(value, list) else value
            temporary = None
            try:
                if self.path is not None:
                    self.path.parent.mkdir(parents=True, exist_ok=True)
                    with NamedTemporaryFile(
                        mode="w",
                        encoding="utf-8",
                        newline="\n",
                        dir=self.path.parent,
                        prefix=".paths-",
                        suffix=".tmp",
                        delete=False,
                    ) as stream:
                        temporary = Path(stream.name)
                        json.dump(self.values, stream, sort_keys=True, indent=2)
                        stream.write("\n")
                    temporary.replace(self.path)
                self.warning = ""
            except OSError:
                self.warning = "Folder selected, but it could not be remembered. Choose it again next time."
            finally:
                if temporary is not None and temporary.exists():
                    temporary.unlink()
            return self.warning

    def remember_root(self, value: str) -> str:
        with self.lock:
            roots = list(self.values.get("seed_roots", []))
            if value not in roots:
                roots.append(value)
            return self.remember("seed_roots", roots)
