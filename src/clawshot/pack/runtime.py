"""Make/Play implementation used only inside an extracted private pack."""

import argparse
import json
import mmap
import os
import subprocess
import sys
from pathlib import Path

from clawshot.pack import PackError, check_version, generate, tree_digest


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


def check_mods_support(exe: Path) -> None:
    """Check the actual binary's loader capability without executing it or trusting a version label."""
    markers = (b"HOS_MODS\0", b"mods: %s: %d RomFS files\0")
    with exe.open("rb") as stream:
        if exe.stat().st_size:
            with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as image:
                if all(image.find(marker) >= 0 for marker in markers):
                    return
    raise PackError(
        "cannot confirm Hookshot mods support in bin/hookshot.exe; update/rebuild Hookshot "
        "(2.0.12+ recommended); Play will not start a possibly vanilla game"
    )


def check_mod_layout(root: Path) -> None:
    """Require exactly seed, using v2.0.13 discovery facts (host/mods.c), never linked folders."""
    mods = []

    def walk(folder: Path, depth: int) -> None:
        if folder.is_symlink() or folder.is_junction():
            raise PackError(f"pack mod search contains a link: {folder}")
        if depth and any((folder / name).exists() for name in ("romfs", "exefs")):
            mods.append(folder)
            return
        if depth < 4:
            for child in sorted(folder.iterdir()):
                if child.name[0] not in ".-_" and child.is_dir():
                    walk(child, depth + 1)

    walk(root, 0)
    if mods != [root / "seed"] or not (root / "seed/romfs").is_dir():
        raise PackError(f"pack must expose exactly one mod, seed/romfs; found: {mods}; use a fresh extraction")


def play(root: Path, *, dry_run: bool = False) -> int:
    manifest, _, hookshot = configuration(root)
    if hookshot is None:
        raise PackError(
            "no Hookshot folder configured; for emulator loading, follow docs/seed-pack.md "
            "(Emulator / console loading); do not run Play"
        )
    if not (hookshot / "bin/hookshot.exe").is_file():
        raise PackError(f"missing {hookshot / 'bin/hookshot.exe'}; never use the folder-root launcher")
    verify(root, manifest)
    check_mods_support(hookshot / "bin/hookshot.exe")
    check_mod_layout(root)
    user = root / "user"
    if user.resolve() != user or (root / "seed").resolve() != root / "seed":
        raise PackError("pack user/seed folder must not be a link")
    overrides = {"HOOKSHOT_NO_UPDATE_CHECK": "1", "HOS_FS_OVERLAY": "", "HOS_MODS": str(root)}
    command = [str(hookshot / "bin/hookshot.exe"), "--user", str(user)]
    if dry_run:
        print(
            json.dumps(
                {
                    "command": command,
                    "cwd": str(hookshot),
                    "environment": overrides,
                    "mod": str(root / "seed"),
                    "log": str(root / "hookshot_log.txt"),
                },
                indent=2,
            )
        )
        return 0
    user.mkdir(exist_ok=True)
    env = dict(os.environ, **overrides)
    print(f"Seed {manifest['seed']}; isolated saves: {user}; log: {root / 'hookshot_log.txt'}", flush=True)
    with (root / "hookshot_log.txt").open("wb") as log:
        return subprocess.run(
            command,
            cwd=hookshot,
            env=env,
            stderr=log,
            check=False,
        ).returncode


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
