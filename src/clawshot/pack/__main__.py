"""Build a private seed source zip, never a generated overlay."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from clawshot.pack import PackError, build


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", required=True, help="CS1 settings string")
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--out", required=True, type=Path, help="new zip outside the repository and dump")
    parser.add_argument(
        "--romfs", type=Path, default=os.environ.get("OOT_ROMFS"), help="RomFS folder or .nup file; or set OOT_ROMFS"
    )
    args = parser.parse_args(argv)
    if args.romfs is None:
        parser.error("publisher needs --romfs or OOT_ROMFS to compute the reference digest")
    try:
        manifest = build(args.romfs, args.seed, args.settings, args.out)
    except (OSError, PackError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"seed {args.seed}: {manifest['output_sha256']}\nPrivate source pack: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
