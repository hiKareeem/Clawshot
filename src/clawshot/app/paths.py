"""Read-only source detection and conservative output boundaries; never launch a runtime."""

import os
from dataclasses import asdict
from pathlib import Path

from clawshot.pack import BUILD, VERSION_FILES, PackError, check_version
from clawshot.pack.hookshot import detect as _detect_hookshot

SOURCE_ROOT = Path(__file__).resolve().parents[3]
SUPPORTED_VERSION = "1.1.1"
SUPPORTED_UPDATE = "Version 1.1.1 update (v131072)"
UPDATE_OPTION = "Update is a separate folder, .nup or .nx"
ARCHIVE_SUFFIXES = (".nup", ".nx")


def default_output_root() -> Path:
    """User Documents, including Windows' redirected known folder; no creation during discovery."""
    home = Path.home()
    documents = home / "Documents"
    if os.name == "nt":
        import ctypes

        buffer = ctypes.create_unicode_buffer(32768)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buffer) == 0:
            documents = Path(buffer.value)
    elif os.name == "posix":
        config = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config")) / "user-dirs.dirs"
        if config.is_file():
            for line in config.read_text(encoding="utf-8").splitlines():
                if line.startswith('XDG_DOCUMENTS_DIR="') and line.endswith('"'):
                    value = line.partition("=")[2].strip('"').replace("$HOME", str(home))
                    if Path(value).is_absolute():
                        documents = Path(value)
    return (documents / "Clawshot").resolve()


def absolute_path(value: str, label: str, *, allow_links: bool = False) -> Path:
    if not isinstance(value, str) or not value.strip() or "\0" in value:
        raise ValueError(f"{label} needs an absolute path")
    path = Path(value.strip())
    if not path.is_absolute() or str(path).startswith(("\\\\", "//")):
        raise ValueError(f"{label} needs an absolute local path (no network share)")
    if not allow_links:
        for part in (path, *path.parents):
            if part.is_symlink() or part.is_junction():
                raise ValueError(f"{label} must not traverse links: {part}")
    try:
        return path.resolve()
    except RuntimeError as error:
        raise ValueError(f"{label} contains a looping link; choose the real folder instead") from error


def dump_root(path: Path) -> Path:
    """A layer picked inside a base+updates dump folder (``base``, ``base/romfs``, ``updates/<n>[/romfs]``) means
    that dump folder, so the newest update is laid over the cart files instead of either being checked alone."""
    from clawshot.pack.source import dump_layers

    for candidate in list(path.parents)[:3]:
        if not (path.is_relative_to(candidate / "base") or path.is_relative_to(candidate / "updates")):
            continue
        layers = dump_layers(candidate)
        if layers is not None and len(layers) > 1:
            return candidate
    return path


def _source_path(value: str, label: str) -> Path:
    path = absolute_path(value, label, allow_links=True)
    if not path.is_dir() and (not path.is_file() or path.suffix.lower() not in ARCHIVE_SUFFIXES):
        raise ValueError(f"{label}: choose an extracted romfs folder, a .nup or an .nx file")
    return path


def _inspect(path: Path, update: Path | None) -> tuple[str | None, list[str]]:
    """The version the files name and which fingerprint files are missing, without judging the build."""
    from clawshot.pack.source import game_version, open_source

    try:
        with open_source(path, update) as source:
            return game_version(source), [name for name in VERSION_FILES if not source.has(name)]
    except (OSError, PackError):
        return None, []


def _refusal(version: str | None, missing: list[str], update: Path | None) -> str:
    if missing and version == "1.0.0":
        if update is not None:
            return (
                f"Found Version 1.0.0: the update you chose does not hold the Version {SUPPORTED_VERSION} files "
                f"({', '.join(missing)}). Choose the {SUPPORTED_UPDATE} folder, .nup or .nx."
            )
        return (
            f"Found Version 1.0.0 (the cart files only). Clawshot needs Version {SUPPORTED_VERSION}: tick "
            f"'{UPDATE_OPTION}' and choose the update, or choose the folder that holds both base/romfs and "
            "updates/<version>/romfs."
        )
    if missing and version == SUPPORTED_VERSION:
        return (
            f"Found only Version {SUPPORTED_VERSION} update files (missing {', '.join(missing)}). Choose the "
            f"Version 1.0.0 cart files as the game dump, tick '{UPDATE_OPTION}' and choose this as the update."
        )
    if missing:
        return f"These game files are missing {', '.join(missing)}. Choose the full romfs folder, .nup or .nx."
    if version is None:
        return "These game files cannot be read or name no known version. Choose the full romfs folder, .nup or .nx."
    return (
        f"Found Version {version}, but not the supported build {BUILD} (Version {SUPPORTED_VERSION}). "
        "Choose an unmodified dump of that version."
    )


def detect_dump(value: str, update: str | None = None) -> dict:
    path = _source_path(value, "Game dump")
    update_path = _source_path(update, "Update") if update else None
    if update_path is not None and update_path == path:
        raise ValueError("Choose the update separately from the game dump.")
    if path.is_dir() and update_path is None:
        path = dump_root(path)
    try:
        check_version(path, update_path)
    except (OSError, PackError) as error:
        raise ValueError(_refusal(*_inspect(path, update_path), update_path)) from error
    version, _ = _inspect(path, update_path)
    return {
        "path": str(path),
        "kind": "romfs" if path.is_dir() else path.suffix.lower().lstrip("."),
        "update": str(update_path) if update_path is not None else None,
        "version": version or SUPPORTED_VERSION,
        "build": BUILD,
        "supported": True,
    }


def detect_hookshot(value: str) -> dict:
    """JSON projection of the shared pack detector; never infer capability from a version."""
    path = absolute_path(value, "Hookshot", allow_links=True)
    if not path.is_dir():
        raise ValueError("Hookshot folder does not exist")
    result = asdict(_detect_hookshot(path))
    for key in ("folder", "exe", "romfs"):
        result[key] = str(result[key]) if result[key] is not None else None
    result["nups"] = [str(file) for file in result["nups"]]
    return result


def output_path(value: str, source: Path, hookshot: Path | None = None, update: Path | None = None) -> Path:
    out = absolute_path(value, "Output")
    if out.exists():
        raise ValueError(f"Output already exists; choose a new folder: {out}")
    if not out.parent.is_dir() and out.parent != default_output_root():
        raise ValueError("Choose an existing output parent folder")
    # A conventional romfs folder's parent is the installation, not a scratch output root.
    protected = [source, SOURCE_ROOT]
    if source.is_file() or source.name.lower() == "romfs":
        protected.append(source.parent)
    if hookshot is not None:
        protected.append(hookshot)
    if update is not None:
        protected.append(update)
        if update.is_file() or update.name.lower() == "romfs":
            protected.append(update.parent)
    for root in protected:
        root = root.resolve()
        if out.is_relative_to(root) or root.is_relative_to(out):
            raise ValueError(f"Output overlaps a protected source/game folder: {root}")
    return out
