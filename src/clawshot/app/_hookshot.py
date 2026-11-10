"""Round-11 stand-in until pack.hookshot is merged; remove once both tracks are on main."""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HookshotInfo:
    folder: Path
    exe: Path
    version: str | None
    romfs: Path | None
    nups: tuple[Path, ...]
    supports_mods: bool
    reason: str


def detect(folder: Path | str) -> HookshotInfo:
    folder = Path(folder).resolve()
    exe = folder / "bin/hookshot.exe"
    marker = folder / "hookshot_version.txt"
    text = marker.read_text(encoding="utf-8-sig") if marker.is_file() else ""
    match = re.search(r"^version=v?(\d+\.\d+\.\d+)\s*$", text, re.MULTILINE)
    version = match.group(1) if match else None
    supports = version is not None and tuple(map(int, version.split("."))) >= (2, 0, 12)
    reason = ""
    if not exe.is_file():
        reason = f"Missing {exe}; never use the folder-root updater"
    elif version is None:
        reason = "Hookshot version is unknown; mods support cannot be confirmed"
    elif not supports:
        reason = "Hookshot 2.0.12 or later is required for this mod-loading route"
    return HookshotInfo(
        folder,
        exe,
        version,
        folder / "romfs" if (folder / "romfs").is_dir() else None,
        tuple(sorted(path for path in folder.glob("*.nup") if path.is_file())),
        supports,
        reason,
    )
