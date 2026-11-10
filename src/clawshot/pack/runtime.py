"""Shared checked Hookshot launching and the extracted pack's Make/Play entry point."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from clawshot.pack import PackError, check_version, generate, tree_digest
from clawshot.pack.hookshot import detect


def configuration(root: Path) -> tuple[dict, Path, Path | None]:
    manifest = json.loads((root / "pack.json").read_text(encoding="utf-8-sig"))
    config = json.loads((root / "folders.json").read_text(encoding="utf-8-sig"))
    romfs = Path(config["romfs"]).resolve()
    check_version(romfs)
    hookshot = Path(config["hookshot"]).resolve() if config.get("hookshot") else None
    for protected in (romfs, hookshot):
        if protected is None:
            continue
        if root.is_relative_to(protected) or protected.is_relative_to(root):
            raise PackError(f"extract the pack outside your game folders: {protected}")
    if manifest["format"] != 1:
        raise PackError(f"unsupported pack format: {manifest['format']}")
    return manifest, romfs, hookshot


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
    print("Read seed/play-note.md. Hookshot: Play seed.bat. Emulator: docs/seed-pack.md (Emulator / console loading).")


def check_mod_layout(root: Path) -> None:
    """Require exactly seed, using v2.0.13 discovery facts (host/mods.c), never linked folders."""
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


def launch_plan(root: Path, hookshot: Path) -> dict:
    """Read-only plan shared by pack Play and the UI; root contains exactly seed/romfs."""
    root = Path(root).absolute()
    hookshot = Path(hookshot).resolve()
    if not root.is_dir():
        raise PackError("The seed folder is missing. Generate a new seed, then try Play again.")
    if root.resolve() != root:
        raise PackError("The seed folder must not be a link. Use its real folder and generate again.")
    if root.is_relative_to(hookshot) or hookshot.is_relative_to(root):
        raise PackError("Keep seed outputs outside Hookshot. Choose a new output folder and generate again.")
    installation = detect(hookshot)
    if installation.reason:
        if not installation.exe.is_file():
            raise PackError(installation.reason + ". Choose the Hookshot folder containing bin, then try Play again.")
        raise PackError(installation.reason)
    check_mod_layout(root)
    user = root / "user"
    log = root / "hookshot_log.txt"
    if any(path.resolve() != path for path in (user, log, root / "seed")):
        raise PackError("The seed, saves or log path is a link. Generate a new seed in a fresh output folder.")
    return {
        "command": [str(installation.exe), "--user", str(user)],
        "cwd": str(hookshot),
        "environment": {"HOOKSHOT_NO_UPDATE_CHECK": "1", "HOS_MODS": str(root)},
        "unset_environment": ["HOS_FS_OVERLAY"],
        "mod": str(root / "seed"),
        "user": str(user),
        "log": str(log),
    }


def start_game(plan: dict) -> subprocess.Popen:
    """Execute a checked plan. Tests inspect launch_plan instead; never invoke this on a real game."""
    if sys.platform != "win32":
        raise PackError("Play needs Windows. Open the seed folder and load romfs as a mod in your emulator.")
    Path(plan["user"]).mkdir(exist_ok=True)
    env = dict(os.environ, **plan["environment"])
    for key in plan["unset_environment"]:
        env.pop(key, None)
    with Path(plan["log"]).open("wb") as log:
        return subprocess.Popen(plan["command"], cwd=plan["cwd"], env=env, stderr=log)


def play(root: Path, *, dry_run: bool = False) -> int:
    manifest, _, hookshot = configuration(root)
    if hookshot is None:
        raise PackError(
            "no Hookshot folder configured; for emulator loading, follow docs/seed-pack.md "
            "(Emulator / console loading); do not run Play"
        )
    verify(root, manifest)
    plan = launch_plan(root, hookshot)
    if dry_run:
        print(json.dumps(plan, indent=2))
        return 0
    print(f"Seed {manifest['seed']}; isolated saves: {plan['user']}; log: {plan['log']}", flush=True)
    return start_game(plan).wait()


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
