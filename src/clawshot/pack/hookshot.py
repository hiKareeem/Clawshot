"""Read-only Hookshot installation detection; never probe by starting the game."""

import mmap
import sys
from dataclasses import dataclass
from pathlib import Path

# Hookshot Builder game folders keep the game in bin: hookshot.exe on Windows, hookshot on Linux
# (Hookshot readme, "In a game folder, hookshot is the launcher and the game itself is bin/hookshot").
WINDOWS_GAME = "bin/hookshot.exe"
LINUX_GAME = "bin/hookshot"


def native_game(platform: str | None = None) -> str | None:
    """The game binary this computer can start, relative to the game folder; None where Hookshot has no build."""
    platform = sys.platform if platform is None else platform
    if platform == "win32":
        return WINDOWS_GAME
    return LINUX_GAME if platform.startswith("linux") else None


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
    """Inspect a game folder. Empty reason means the binary can load a seed through HOS_MODS.

    Version is informational, not a capability claim. The HOS_MODS marker indicates mod
    loading; diagnostic wording is irrelevant. No folder-root fallback or dump decoding.
    """
    folder = Path(folder).resolve()
    # A folder holds one platform's build. With neither present, name the file this computer would need.
    exe = next(
        (path for name in (WINDOWS_GAME, LINUX_GAME) if (path := folder / name).is_file()),
        folder / (native_game() or WINDOWS_GAME),
    )
    version = None
    romfs = folder / "romfs"
    nups = ()
    supported = False
    reason = ""
    try:
        version_file = folder / "hookshot_version.txt"
        if version_file.is_file():
            lines = version_file.read_text(encoding="utf-8-sig").splitlines()
            version = next((line.partition("=")[2].strip() for line in lines if line.startswith("version=")), None)
            if version is None and len(lines) == 1 and "=" not in lines[0]:
                version = lines[0].strip()
            version = version or None
        if folder.is_dir():
            nups = tuple(sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".nup"))
        if not exe.is_file():
            reason = f"missing {exe}; never use the folder-root launcher"
        else:
            with exe.open("rb") as stream:
                if exe.stat().st_size:
                    with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as image:
                        supported = image.find(b"HOS_MODS\0") >= 0
            if not supported:
                reason = "This Hookshot build cannot load mods. Update Hookshot, then run Play again."
    except (OSError, UnicodeError, ValueError) as error:
        reason = f"cannot inspect Hookshot installation: {error}"
    return HookshotInfo(folder, exe, version, romfs if romfs.is_dir() else None, nups, supported, reason)
