"""Read-only source detection and conservative output boundaries; never launch a runtime."""

import os
from dataclasses import asdict
from pathlib import Path

from clawshot.pack import BUILD, check_version
from clawshot.pack.hookshot import detect as _detect_hookshot

SOURCE_ROOT = Path(__file__).resolve().parents[3]


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


def detect_dump(value: str) -> dict:
    path = absolute_path(value, "Dump", allow_links=True)
    if not path.is_dir() and (not path.is_file() or path.suffix.lower() != ".nup"):
        raise ValueError("Choose an extracted romfs folder or a .nup file")
    check_version(path)
    return {"path": str(path), "kind": "romfs" if path.is_dir() else "nup", "build": BUILD, "supported": True}


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


def output_path(value: str, source: Path, hookshot: Path | None = None) -> Path:
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
    for root in protected:
        root = root.resolve()
        if out.is_relative_to(root) or root.is_relative_to(out):
            raise ValueError(f"Output overlaps a protected source/game folder: {root}")
    return out
