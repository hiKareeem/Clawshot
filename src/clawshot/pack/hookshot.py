"""Read-only Hookshot and Longshot installation detection; never probe by starting the game."""

import json
import mmap
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# A game folder keeps the game in bin; the program of the same name at the folder's root is a launcher, never the game.
# Hookshot readme: "In a game folder, hookshot is the launcher and the game itself is bin/hookshot". Longshot readme
# (Running the game from the command line): "The built game is bin\longshot.exe on Windows and bin/longshot in a
# packaged Linux game folder." Each writes <program>_version.txt (version=...) beside bin (Hookshot v2.1.0 and
# Longshot v3.0.0-rc.2 folders, read-only, 2026-11-13).
PROGRAMS = {"Hookshot": "hookshot", "Longshot": "longshot"}
# Longshot Launcher readme (Installing; Environment and command line): a portable launcher keeps its data in
# LongshotLauncher-data beside it, an installed one (%LOCALAPPDATA%\Programs\LongshotLauncher) in
# %LOCALAPPDATA%\LongshotLauncher, on Linux ~/.local/share/longshot/launcher or a portable AppImage's <AppImage>.home.
# That home holds builds.json, whose builds name their folders; a portable launcher builds into builds/<version>
# (a portable v1 launcher's home, read-only, 2026-11-13), an installed one into ~/Games/Longshot/<version> (readme,
# Planned next).
# Longshot Launcher README (What it does; Design decisions) says Play starts the default build. Its format-1
# builds.json records that choice as builds[].default=true beside folder/version (portable v1, read-only, 2026-11-13).
LAUNCHER_DATA = "LongshotLauncher-data"
LINUX_LAUNCHER_DATA = ".local/share/longshot/launcher"
REGISTRY = "builds.json"
RELEASE = re.compile(r"v?(\d+)\.(\d+)\.(\d+)(?:-rc\.(\d+))?")


def native_suffix(platform: str | None = None) -> str | None:
    """The suffix of a game binary this computer can start ("" on Linux); None where neither game has a build."""
    platform = sys.platform if platform is None else platform
    if platform == "win32":
        return ".exe"
    return "" if platform.startswith("linux") else None


def game_binary(game: str, platform: str | None = None) -> str:
    """The binary a missing game folder should hold, relative to it: this computer's, else the Windows one."""
    suffix = native_suffix(platform)
    return f"bin/{PROGRAMS[game]}{'.exe' if suffix is None else suffix}"


def version_key(label: str | None) -> tuple:
    """Order of version labels: vX.Y.Z above its own vX.Y.Z-rc.N, every number compared as a number; a label that is
    not a release (a nightly) below every release, by its numbers."""
    if label and (match := RELEASE.fullmatch(label.strip())):
        major, minor, patch, candidate = match.groups()
        return 1, (int(major), int(minor), int(patch), candidate is None, int(candidate or 0))
    return 0, tuple(int(number) for number in re.findall(r"\d+", label or ""))


@dataclass(frozen=True)
class GameInfo:
    game: str  # "Hookshot" or "Longshot"
    selected_folder: Path  # what the player chose: a game folder, a Longshot Launcher folder or a folder of builds
    launcher: Path | None  # the Longshot Launcher data folder the build was found through
    folder: Path  # the game folder Play starts the game in
    exe: Path
    version: str | None
    romfs: Path | None
    nups: tuple[Path, ...]
    supports_mods: bool
    reason: str

    @property
    def folders(self) -> tuple[Path, ...]:
        """Every folder this choice stands for; seed outputs stay outside all of them."""
        return tuple(dict.fromkeys(p for p in (self.selected_folder, self.launcher, self.folder) if p is not None))


def _binary(folder: Path) -> tuple[str, Path] | None:
    """The game in a folder's bin. A folder holds one platform's build; this computer's is looked for first."""
    suffixes = ("", ".exe") if native_suffix() == "" else (".exe", "")
    for suffix in suffixes:
        for game, program in PROGRAMS.items():
            if (path := folder / f"bin/{program}{suffix}").is_file():
                return game, path
    return None


def _version(folder: Path, game: str) -> str | None:
    version_file = folder / f"{PROGRAMS[game]}_version.txt"
    if not version_file.is_file():
        return None
    lines = version_file.read_text(encoding="utf-8-sig").splitlines()
    version = next((line.partition("=")[2].strip() for line in lines if line.startswith("version=")), None)
    if version is None and len(lines) == 1 and "=" not in lines[0]:
        version = lines[0].strip()
    return version or None


def _launcher_data(folder: Path) -> Path | None:
    """The Longshot Launcher home a chosen folder means: itself, the portable program's, the installed program's,
    ~/.local/share/longshot's, or a portable AppImage's (picked, or the folder holding it)."""
    candidates = [folder, folder / LAUNCHER_DATA, folder / "launcher", folder / LINUX_LAUNCHER_DATA]
    if folder.is_dir():
        for home in sorted(folder.glob("*.AppImage.home")):
            candidates += [home, home / LINUX_LAUNCHER_DATA]
    if folder.parent.name.casefold() == "programs" and (folder / "LongshotLauncher.exe").is_file():
        candidates.append(folder.parent.parent / "LongshotLauncher")
    return next((path for path in candidates if (path / REGISTRY).is_file() or (path / "builds").is_dir()), None)


def _subfolders(folder: Path) -> list[Path]:
    return sorted(child for child in folder.iterdir() if child.is_dir()) if folder.is_dir() else []


def _launcher_builds(data: Path) -> dict[Path, tuple[str | None, bool]]:
    """Listed/scanned build folders with version and the launcher's recorded default flag."""
    builds = {}
    try:
        registry = json.loads((data / REGISTRY).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError):
        registry = {}
    entries = registry.get("builds") if isinstance(registry, dict) else None
    for entry in entries if isinstance(entries, list) else ():
        folder = entry.get("folder") if isinstance(entry, dict) else None
        if isinstance(folder, str) and folder.strip():
            version = entry.get("version")
            builds.setdefault(
                (data / folder).resolve(),
                (version if isinstance(version, str) else None, entry.get("default") is True),
            )
    for folder in _subfolders(data / "builds"):
        builds.setdefault(folder.resolve(), (None, False))
    return builds


def _choose_build(builds: dict[Path, tuple[str | None, bool]]) -> tuple[Path, str | None] | None:
    """Prefer an available recorded default, otherwise choose by numeric version."""
    found = []
    for folder, (listed, preferred) in builds.items():
        binary = _binary(folder)
        if binary is None or binary[0] != "Longshot":
            continue
        try:
            label = _version(folder, "Longshot") or listed
        except (OSError, UnicodeError):
            label = listed
        found.append((preferred, version_key(label or folder.name), str(folder), folder, listed))
    if not found:
        return None
    *_, folder, listed = max(found)
    return folder, listed


def _locate(selected: Path) -> tuple[Path | None, Path, str | None]:
    """(launcher home or None, game folder, the launcher's version label) for a chosen folder."""
    if _binary(selected):
        return None, selected, None
    data = _launcher_data(selected)
    builds = _launcher_builds(data) if data else {folder: (None, False) for folder in _subfolders(selected)}
    chosen = _choose_build(builds)
    return (data, *chosen) if chosen else (data, selected, None)


def game_folders(folder: Path | str) -> tuple[Path, ...]:
    """The chosen folder, a Longshot Launcher home it means and the build Play would start, without reading binaries."""
    selected = Path(folder).resolve()
    try:
        data, build, _ = _locate(selected)
    except OSError:
        return (selected,)
    return tuple(dict.fromkeys(path for path in (selected, data, build) if path is not None))


def _guess(folder: Path) -> str:
    """The game a folder without a binary was meant for: from its version file or folder-root launcher."""
    for game, program in PROGRAMS.items():
        if any((folder / name).exists() for name in (f"{program}_version.txt", program, f"{program}.exe")):
            return game
    return "Longshot"


def detect(folder: Path | str) -> GameInfo:
    """Inspect a chosen folder. Empty reason means the binary can load a seed through HOS_MODS.

    The folder may be a Hookshot or Longshot game folder, a Longshot Launcher folder (portable, installed or its data
    folder) or a folder of Longshot builds. An available recorded default wins, otherwise the newest numeric version.
    Version is informational, not a capability claim; HOS_MODS indicates mod loading. No root launcher or dump decoding.
    """
    selected = Path(folder).resolve()
    launcher, game_folder, listed = None, selected, None
    game = "Longshot"
    exe = selected / game_binary(game)
    version = None
    nups = ()
    supported = False
    reason = ""
    try:
        launcher, game_folder, listed = _locate(selected)
        found = _binary(game_folder)
        if found:
            game, exe = found
        else:
            game = "Longshot" if launcher else _guess(selected)
            exe = game_folder / game_binary(game)
        version = _version(game_folder, game) or listed
        if game_folder.is_dir():
            nups = tuple(sorted(p for p in game_folder.iterdir() if p.is_file() and p.suffix.lower() == ".nup"))
        if found is None and launcher is not None:
            reason = (
                f"The Longshot Launcher folder {launcher} has no Longshot build. "
                "Build the game there, then check again."
            )
        elif found is None:
            reason = (
                f"Missing {exe}; never use the folder-root launcher. Choose the Hookshot or Longshot folder containing "
                "bin, or the Longshot Launcher folder."
            )
        else:
            with exe.open("rb") as stream:
                if exe.stat().st_size:
                    with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as image:
                        supported = image.find(b"HOS_MODS\0") >= 0
            if not supported:
                reason = f"This {game} build cannot load mods. Update {game}, then run Play again."
    except (OSError, UnicodeError, ValueError) as error:
        reason = f"Cannot inspect the {game} folder: {error}"
    romfs = game_folder / "romfs"
    return GameInfo(
        game, selected, launcher, game_folder, exe, version, romfs if romfs.is_dir() else None, nups, supported, reason
    )
