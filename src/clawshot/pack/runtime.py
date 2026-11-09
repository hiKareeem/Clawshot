"""Make/Play implementation used only inside an extracted private pack."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from clawshot.pack import PackError, check_version, generate, tree_digest


def configuration(root: Path) -> tuple[dict, Path, Path]:
    manifest = json.loads((root / "pack.json").read_text(encoding="utf-8-sig"))
    config = json.loads((root / "folders.json").read_text(encoding="utf-8-sig"))
    romfs, hookshot = Path(config["romfs"]).resolve(), Path(config["hookshot"]).resolve()
    check_version(romfs)
    for protected in (romfs, hookshot):
        if root.is_relative_to(protected) or protected.is_relative_to(root):
            raise PackError(f"extract the pack outside your game folders: {protected}")
    if not (hookshot / "bin/hookshot.exe").is_file():
        raise PackError(f"missing {hookshot / 'bin/hookshot.exe'}; never use the folder-root launcher")
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
    print("Read seed/play-note.md; then run Play seed.bat. Normal saves are not used.")


def play(root: Path) -> int:
    manifest, _, hookshot = configuration(root)
    verify(root, manifest)
    user = root / "user"
    if user.resolve() != user or (root / "seed").resolve() != root / "seed":
        raise PackError("pack user/seed folder must not be a link")
    user.mkdir(exist_ok=True)
    env = dict(os.environ, HOOKSHOT_NO_UPDATE_CHECK="1", HOS_FS_OVERLAY=str(root / "seed/romfs"))
    print(f"Seed {manifest['seed']}; isolated saves: {user}; log: {root / 'hookshot_log.txt'}", flush=True)
    with (root / "hookshot_log.txt").open("wb") as log:
        return subprocess.run(
            [str(hookshot / "bin/hookshot.exe"), "--user", str(user)],
            cwd=hookshot,
            env=env,
            stderr=log,
            check=False,
        ).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("make", "play"))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        if args.action == "make":
            make(root)
            return 0
        return play(root)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
