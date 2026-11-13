"""Read-only source detection and conservative output boundaries; never launch a runtime."""

import os
from dataclasses import asdict
from pathlib import Path

from clawshot.pack import BUILD, VERSION_FILES, PackError, check_version
from clawshot.pack.hookshot import detect, game_folders

SOURCE_ROOT = Path(__file__).resolve().parents[3]
SUPPORTED_UPDATE = "Version 1.1.1 update (v131072)"


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


def _missing_version_files(path: Path) -> list[str]:
    from clawshot.pack.source import dump_layers

    if not path.is_dir() or dump_layers(path) is not None:
        return []
    return [name for name in VERSION_FILES if not (path / name).is_file()]


def detect_dump(value: str) -> dict:
    path = absolute_path(value, "Dump", allow_links=True)
    if not path.is_dir() and (not path.is_file() or path.suffix.lower() != ".nup"):
        raise ValueError("Choose an extracted romfs folder or a .nup file")
    if path.is_dir():
        path = dump_root(path)
    try:
        check_version(path)
    except PackError as error:
        raise ValueError(
            f"These game files are not the supported build {BUILD} ({SUPPORTED_UPDATE}). "
            "Choose the correct full game dump."
        ) from error
    except OSError as error:
        missing = _missing_version_files(path)
        if missing:
            raise ValueError(
                f"This romfs is missing {', '.join(missing)}. Build {BUILD} is the Version 1.0.0 cart files "
                f"plus the {SUPPORTED_UPDATE}, so one of them alone is not enough. Choose the folder that holds both "
                "base/romfs and updates/<version>/romfs, a romfs with the update applied, or a .nup."
            ) from error
        raise ValueError(
            "These game files are incomplete or cannot be read. Choose the full romfs folder or .nup."
        ) from error
    return {"path": str(path), "kind": "romfs" if path.is_dir() else "nup", "build": BUILD, "supported": True}


def detect_game(value: str) -> dict:
    """JSON projection of the shared pack detector; never infer capability from a version.

    ``selected_folder`` is the chosen folder to remember (it may be a Longshot Launcher folder); ``folder`` the build
    Play starts; ``folders`` every folder the choice stands for, which outputs and copies stay outside.
    """
    path = absolute_path(value, "Game folder", allow_links=True)
    if not path.is_dir():
        raise ValueError("Hookshot or Longshot folder does not exist")
    info = detect(path)
    result = asdict(info)
    for key in ("selected_folder", "launcher", "folder", "exe", "romfs"):
        result[key] = str(result[key]) if result[key] is not None else None
    result["nups"] = [str(file) for file in result["nups"]]
    result["folders"] = [str(folder) for folder in info.folders]
    return result


def output_path(value: str, source: Path, game: Path | None = None) -> Path:
    out = absolute_path(value, "Output")
    if out.exists():
        raise ValueError(f"Output already exists; choose a new folder: {out}")
    if not out.parent.is_dir() and out.parent != default_output_root():
        raise ValueError("Choose an existing output parent folder")
    # A conventional romfs folder's parent is the installation, not a scratch output root.
    protected = [source, SOURCE_ROOT]
    if source.is_file() or source.name.lower() == "romfs":
        protected.append(source.parent)
    if game is not None:  # the chosen folder, a Longshot Launcher home and the build it resolves to
        protected.extend(game_folders(game))
    for root in protected:
        root = root.resolve()
        if out.is_relative_to(root) or root.is_relative_to(out):
            raise ValueError(f"Output overlaps a protected source/game folder: {root}")
    return out
