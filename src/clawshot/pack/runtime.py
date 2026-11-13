"""Shared checked Hookshot and Longshot launching and the extracted pack's Make/Play entry point."""

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from clawshot.pack import PackError, check_version, generate, tree_digest
from clawshot.pack.hookshot import PROGRAMS, detect, game_folders, native_suffix

RUNNING_GAME = "Hookshot or Longshot is already running. Quit it, then press Play."
NO_PLAY = "Play needs Windows or Linux. Open the seed folder and load romfs as a mod in your emulator."
OTHER_SYSTEM = (
    "This game folder holds the game for another system. "
    "Choose a Hookshot or Longshot game built on this computer, then press Play."
)
NOT_CHECKED = "Clawshot could not check running programs. Close Hookshot or Longshot and try Play again."


def play_refusal(exe: Path | str | None = None, platform: str | None = None) -> str:
    """Why this computer cannot start the game, or "": no game build for it, or ``exe`` is another system's."""
    native = native_suffix(platform)
    if native is None:
        return NO_PLAY
    if exe is not None and Path(exe).suffix.lower() != native:
        return OTHER_SYSTEM
    return ""


def _windows_process_names() -> tuple[str, ...]:
    tasklist = Path(os.environ.get("SYSTEMROOT", r"C:\Windows")) / "System32/tasklist.exe"
    try:
        result = subprocess.run(
            [str(tasklist), "/FO", "CSV", "/NH"],
            capture_output=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise PackError(NOT_CHECKED) from error
    rows = csv.reader(result.stdout.decode("utf-8", errors="replace").splitlines())
    return tuple(row[0] for row in rows if len(row) > 1)


def _linux_process_names(proc: Path = Path("/proc")) -> tuple[str, ...]:
    """The program file name of every process whose /proc/<pid>/exe link this user may read."""
    try:
        entries = sorted(entry for entry in proc.iterdir() if entry.name.isdigit())
    except OSError as error:
        raise PackError(NOT_CHECKED) from error
    names = []
    for entry in entries:
        try:
            target = os.readlink(entry / "exe")
        except OSError:
            continue  # a kernel thread, another user's process, or one that ended meanwhile
        # The kernel marks a program file replaced while it runs, as a rebuilt game is.
        names.append(Path(target.removesuffix(" (deleted)")).name)
    return tuple(names)


def running_process_names() -> tuple[str, ...]:
    """Read the process list without opening a console or adding a dependency."""
    if sys.platform == "win32":
        return _windows_process_names()
    if sys.platform.startswith("linux"):
        return _linux_process_names()
    return ()


def game_running(process_lister=None) -> bool:
    lister = running_process_names if process_lister is None else process_lister
    # Windows names are case-insensitive; a Linux program file is exactly "hookshot" or "longshot".
    windows = {f"{program}.exe" for program in PROGRAMS.values()}
    return any(name.casefold() in windows or name in PROGRAMS.values() for name in lister())


def configuration(root: Path) -> tuple[dict, Path, Path | None]:
    manifest = json.loads((root / "pack.json").read_text(encoding="utf-8-sig"))
    config = json.loads((root / "folders.json").read_text(encoding="utf-8-sig"))
    romfs = Path(config["romfs"]).resolve()
    check_version(romfs)
    # A pack set up before Longshot support names the game folder "hookshot"; "game" wins when both are there.
    chosen = config["game"] if "game" in config else config.get("hookshot")
    game = Path(chosen).resolve() if chosen else None
    for protected in (romfs, *(game_folders(game) if game else ())):
        if root.is_relative_to(protected) or protected.is_relative_to(root):
            raise PackError(f"extract the pack outside your game folders: {protected}")
    if manifest["format"] != 1:
        raise PackError(f"unsupported pack format: {manifest['format']}")
    return manifest, romfs, game


def verify(root: Path, manifest: dict) -> str:
    actual = tree_digest(root / "seed")
    expected = manifest["output_sha256"]
    if actual != expected:
        raise PackError(f"seed digest mismatch: {actual}, expected {expected}; do not play; report in help")
    return actual


def make(root: Path) -> None:
    manifest, romfs, _ = configuration(root)
    output = root / "seed"
    if not output.exists():
        generate(root, romfs, manifest["seed"], manifest["settings"], output)
    # Never rewrite an existing seed; it may be in use. A partial/modified one is a hard error.
    print(f"Verified seed {manifest['seed']}: {verify(root, manifest)}")
    print(
        "Read seed/play-note.md. Hookshot or Longshot: Play seed.bat. "
        "Emulator: docs/seed-pack.md (Emulator / console loading)."
    )


def check_mod_layout(root: Path) -> None:
    """Require exactly seed, using v2.0.13 discovery facts (host/mods.c), never linked folders. Longshot's readme (Mods)
    describes the same discovery: <name>/romfs, deeper layouts, folders starting with - or _ off."""
    mods = []

    def walk(folder: Path, depth: int) -> None:
        if folder.is_symlink() or folder.is_junction():
            raise PackError(f"The mod folder contains a link: {folder}. Use a normal folder and generate again.")
        if depth and any((folder / name).exists() for name in ("romfs", "exefs")):
            mods.append(folder)
            return
        if depth < 4:
            for child in sorted(folder.iterdir()):
                if child.name[0] not in ".-_" and child.is_dir():
                    walk(child, depth + 1)

    walk(root, 0)
    if mods != [root / "seed"] or not (root / "seed/romfs").is_dir():
        raise PackError(
            "The output must expose exactly one mod, seed/romfs. Generate a new seed in a fresh output folder."
        )


def launch_plan(root: Path, game: Path) -> dict:
    """Read-only plan shared by pack Play and the UI; root contains exactly seed/romfs.

    ``game`` is the chosen game folder, Longshot Launcher folder or folder of builds; the plan starts the build it
    resolves to, in that build's folder, with this seed's own saves whichever game plays it.
    """
    root = Path(root).absolute()
    if not root.is_dir():
        raise PackError("The seed folder is missing. Generate a new seed, then try Play again.")
    if root.resolve() != root:
        raise PackError("The seed folder must not be a link. Use its real folder and generate again.")
    installation = detect(game)
    for protected in installation.folders:
        if root.is_relative_to(protected) or protected.is_relative_to(root):
            raise PackError(
                "Keep seed outputs outside your game and Longshot Launcher folders. "
                "Choose a new output folder and generate again."
            )
    if installation.reason:
        raise PackError(installation.reason)
    check_mod_layout(root)
    program = PROGRAMS[installation.game]
    user = root / "user"
    log = root / f"{program}_log.txt"
    if any(path.resolve() != path for path in (user, log, root / "seed")):
        raise PackError("The seed, saves or log path is a link. Generate a new seed in a fresh output folder.")
    return {
        "game": installation.game,
        "version": installation.version,
        "command": [str(installation.exe), "--user", str(user)],
        "cwd": str(installation.folder),
        # The folder launcher of each game starts bin/<program> with <PROGRAM>_NO_UPDATE_CHECK=1: Hookshot's game reads
        # it; Longshot's checks nothing at start (readme, "What Longshot connects to"), yet its v3.0.0-rc.2 launcher
        # still passes it, so Play passes exactly what that game's own launcher does.
        "environment": {f"{program.upper()}_NO_UPDATE_CHECK": "1", "HOS_MODS": str(root)},
        "unset_environment": ["HOS_FS_OVERLAY"],
        "mod": str(root / "seed"),
        "user": str(user),
        "log": str(log),
    }


def prepare_user(plan: dict) -> dict:
    """Initialize a fresh seed user with options/account only; never import progress or overwrite a seed file."""
    user = Path(plan["user"])
    try:
        user.mkdir()
    except FileExistsError:
        if not user.is_dir():
            raise PackError(f"The seed user path is not a folder: {user}") from None
        return {"copied": [], "missing": [], "message": "Existing seed saves and game options kept."}
    saves = Path(plan["cwd"]) / "user/save"
    accounts = [folder for folder in saves.iterdir() if folder.is_dir()] if saves.is_dir() else []
    source = max(accounts, key=lambda folder: (folder.stat().st_mtime_ns, folder.name), default=None)
    copied, missing = [], []
    for name in ("option.sav", "account.sav"):
        if source is None or not (source / name).is_file():
            missing.append(name)
            continue
        try:
            incoming = (source / name).open("rb")
        except FileNotFoundError:
            missing.append(name)
            continue
        with incoming:
            destination = user / "save" / source.name / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            try:
                outgoing = destination.open("xb")
            except FileExistsError:
                continue
            try:
                with outgoing:
                    shutil.copyfileobj(incoming, outgoing)
            except BaseException:
                destination.unlink()
                raise
        copied.append(name)
    message = "Game options carried over: " + ", ".join(copied) + "." if copied else "No game options copied."
    if missing:
        message += " Source missing: " + ", ".join(missing) + "; skipped."
    return {"copied": copied, "missing": missing, "message": message}


def start_game(plan: dict, *, process_lister=None) -> tuple[subprocess.Popen, dict]:
    """Execute a checked plan and return its process/options result; tests never invoke a real game."""
    if game_running(process_lister):
        raise PackError(RUNNING_GAME)
    if refusal := play_refusal(plan["command"][0]):
        raise PackError(refusal)
    options = prepare_user(plan)
    env = dict(os.environ, **plan["environment"])
    for key in plan["unset_environment"]:
        env.pop(key, None)
    with Path(plan["log"]).open("wb") as log:
        return subprocess.Popen(plan["command"], cwd=plan["cwd"], env=env, stderr=log), options


def play(root: Path, *, dry_run: bool = False) -> int:
    manifest, _, game = configuration(root)
    if game is None:
        raise PackError(
            "no Hookshot or Longshot folder configured; for emulator loading, follow docs/seed-pack.md "
            "(Emulator / console loading); do not run Play"
        )
    verify(root, manifest)
    plan = launch_plan(root, game)
    if dry_run:
        print(json.dumps(plan, indent=2))
        return 0
    print(f"Seed {manifest['seed']} in {plan['game']}; isolated saves: {plan['user']}; log: {plan['log']}", flush=True)
    process, options = start_game(plan)
    print(options["message"], flush=True)
    return process.wait()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("make", "play"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument(
        "--dry-run", action="store_true", help="Play: verify and print launch plan; start/write nothing"
    )
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        if args.action == "make":
            make(root)
            return 0
        return play(root, dry_run=args.dry_run or os.environ.get("CLAWSHOT_DRY_RUN") == "1")
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
