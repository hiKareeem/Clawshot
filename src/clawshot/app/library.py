"""Portable completed-seed records and read-only discovery, independent of the generation dump."""

import json
from importlib.metadata import version
from pathlib import Path

from clawshot.app.paths import SOURCE_ROOT, absolute_path, default_output_root
from clawshot.pack import BUILD, tree_digest

MANIFEST = "clawshot-seed.json"
FIELDS = (
    "format",
    "seed",
    "settings_string",
    "output_sha256",
    "shuffled",
    "resources",
    "spheres",
    "clawshot_version",
    "game_build",
)


def write_manifest(root: Path, result: dict) -> dict:
    record = {
        key: result[key] for key in ("seed", "settings_string", "output_sha256", "shuffled", "resources", "spheres")
    }
    record.update(format=1, clawshot_version=version("clawshot"), game_build=BUILD)
    (root / MANIFEST).write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    return record


def inspect_seed(root: Path, *, verify: bool = True) -> dict:
    root = Path(root)
    entry = {
        "output": str(root),
        "name": root.name,
        "playable": False,
        "reason": "",
        "short_hash": "",
        "note_available": False,
    }
    try:
        root = absolute_path(str(root), "Seed folder")
        entry.update(output=str(root), name=root.name)
        note = root / "seed/play-note.md"
        entry["note_available"] = note.is_file() and not note.is_symlink()
        if root.is_relative_to(SOURCE_ROOT) or SOURCE_ROOT.is_relative_to(root):
            raise ValueError("Move this seed outside the Clawshot source folder, then open it again.")
        path = root / MANIFEST
        if not path.is_file():
            raise ValueError("Made by an older Clawshot: generate it again to play it from here")
        if path.is_symlink() or path.stat().st_size > 65536:
            raise ValueError("This seed's information file is not usable. Generate a new seed.")
        record = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict) or set(record) != set(FIELDS):
            raise ValueError("This seed's information is incomplete or not supported. Generate a new seed.")
        if type(record["format"]) is not int or record["format"] != 1:
            raise ValueError("This seed's information format is not supported. Use the Clawshot version that made it.")
        for key in ("seed", "shuffled", "resources", "spheres"):
            if type(record.get(key)) is not int:
                raise ValueError("This seed's information is incomplete. Generate a new seed.")
        if not -(2**53 - 1) <= record["seed"] <= 2**53 - 1 or any(
            record[key] < 0 for key in ("shuffled", "resources", "spheres")
        ):
            raise ValueError("This seed's numbers are not valid. Generate a new seed.")
        for key in ("settings_string", "output_sha256", "clawshot_version", "game_build"):
            if not isinstance(record.get(key), str) or not record[key]:
                raise ValueError("This seed's information is incomplete. Generate a new seed.")
        digest = record["output_sha256"]
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("This seed's hash is not valid. Generate a new seed.")
        entry.update({key: record[key] for key in FIELDS}, short_hash=digest[:12].upper())
        if record["game_build"] != BUILD:
            raise ValueError("This seed was made for a different game version. Use the Clawshot version that made it.")
        if verify:
            seed = absolute_path(str(root / "seed"), "Seed files")
            if not (seed / "romfs").is_dir():
                raise ValueError("This seed's romfs folder is missing. Generate a new seed.")
            if tree_digest(seed) != digest:
                raise ValueError("This seed's files have changed. Generate a new seed before playing.")
        entry["playable"] = True
    except json.JSONDecodeError:
        entry["reason"] = "This seed's information file is damaged. Generate a new seed."
    except (OSError, ValueError, RecursionError) as error:
        entry["playable"] = False
        entry["reason"] = str(error)
    return entry


def verified_seed(result: dict | None) -> Path:
    if result is None:
        raise ValueError("Generate a seed or choose one from My seeds first.")
    entry = inspect_seed(Path(result["output"]))
    if not entry["playable"]:
        raise ValueError(entry["reason"])
    return Path(entry["output"]) / "seed"


def _looks_like_seed(folder: Path) -> bool:
    return (folder / MANIFEST).is_file() or (folder / "seed/romfs").is_dir() or (folder / "romfs").is_dir()


def _newest_first(folder: Path) -> tuple[int, str]:
    try:
        modified = (folder / MANIFEST).stat().st_mtime_ns
    except OSError:
        modified = 0
    return -modified, str(folder).casefold()


class SeedLibrary:
    def __init__(self, preferences):
        self.preferences = preferences

    def folders(self) -> list[Path]:
        return list(
            dict.fromkeys(
                [default_output_root(), *(Path(p) for p in self.preferences.snapshot().get("seed_roots", []))]
            )
        )

    def add_folder(self, value: str) -> str:
        path = absolute_path(value, "Seed folder", allow_links=True)
        if not path.is_dir():
            raise ValueError("Choose an existing folder containing your seeds.")
        return self.preferences.remember_root(str(path))

    def candidates(self) -> list[Path]:
        found = set()
        for folder in self.folders():
            try:
                folder = absolute_path(str(folder), "Seed folder", allow_links=True)
                if not folder.exists():
                    continue
                if _looks_like_seed(folder):
                    found.add(folder)
                else:
                    found.update(child for child in folder.iterdir() if child.is_dir() and _looks_like_seed(child))
            except (OSError, ValueError):
                continue
        return sorted(found, key=_newest_first)

    def entries(self) -> list[dict]:
        return [inspect_seed(path, verify=False) for path in self.candidates()]

    def get(self, value: str, *, verify: bool = True) -> dict:
        requested = absolute_path(value, "Seed folder", allow_links=True)
        if requested not in self.candidates():
            raise ValueError("Choose a seed from My seeds, or open the folder containing it first.")
        return inspect_seed(requested, verify=verify)
