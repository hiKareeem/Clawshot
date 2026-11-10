"""Explicit emulator export: verified seed, real copied files, exclusive destination."""

import shutil
from pathlib import Path

from clawshot.app.library import inspect_seed
from clawshot.app.paths import SOURCE_ROOT, absolute_path
from clawshot.pack import tree_digest

SAVE_WARNING = "Back up your emulator saves first: your emulator uses your normal saves. Enable only this seed."


def copy_to_emulator(result: dict | None, folder: str, *, protected=()) -> dict:
    if result is None:
        raise ValueError("Generate a seed or choose one from My seeds first.")
    entry = inspect_seed(Path(result["output"]))
    if not entry["playable"]:
        raise ValueError(entry["reason"])
    parent = absolute_path(folder, "Emulator mod folder")
    if not parent.is_dir():
        raise ValueError("Choose your emulator's existing mod folder for this game.")
    seed = Path(entry["output"]) / "seed"
    destination = parent / f"Clawshot-seed-{entry['seed']}"
    for source in (SOURCE_ROOT, seed.parent, *(Path(p).resolve() for p in protected if p)):
        if destination.is_relative_to(source) or source.is_relative_to(destination):
            raise ValueError("Choose your emulator's mod folder, outside Clawshot, game files and this seed.")
    try:
        destination.mkdir()
    except FileExistsError as error:
        raise ValueError(
            "That seed already exists in this mod folder. Choose another folder; Clawshot never replaces it."
        ) from error
    except OSError as error:
        raise ValueError(f"Cannot write to that mod folder. Choose a writable folder: {error}") from error
    try:
        shutil.copytree(seed / "romfs", destination / "romfs")
        if tree_digest(destination / "romfs") != tree_digest(seed / "romfs"):
            raise ValueError("The copied files did not match. Choose a reliable writable folder and copy again.")
    except OSError as error:
        shutil.rmtree(destination)
        raise ValueError(f"Copy failed. Choose a reliable writable mod folder and copy again: {error}") from error
    except BaseException:
        shutil.rmtree(destination)
        raise
    return {"path": str(destination), "warning": SAVE_WARNING}
