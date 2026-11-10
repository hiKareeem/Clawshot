"""Read-only Hookshot installation detection; never probe by starting the game."""

import mmap
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
    """Inspect a game folder. Empty reason means the binary can load a seed through HOS_MODS.

    Version is informational, not a capability claim. Unknown/custom binaries must retain
    both loader markers to pass; no folder-root executable fallback. No dump is decoded.
    """
    folder = Path(folder).resolve()
    exe = folder / "bin/hookshot.exe"
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
                        supported = all(
                            image.find(marker) >= 0 for marker in (b"HOS_MODS\0", b"mods: %s: %d RomFS files\0")
                        )
            if not supported:
                reason = (
                    "cannot confirm Hookshot mods support in bin/hookshot.exe; update/rebuild Hookshot "
                    "(2.0.12+ recommended); Play will not start a possibly vanilla game"
                )
    except (OSError, UnicodeError, ValueError) as error:
        reason = f"cannot inspect Hookshot installation: {error}"
    return HookshotInfo(folder, exe, version, romfs if romfs.is_dir() else None, nups, supported, reason)
