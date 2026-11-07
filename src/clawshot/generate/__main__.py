"""Generate a seed's spoiler log from the world data.

    python -m clawshot.generate --seed <n> --out <dir> [--shuffle Chest ...] [--dungeon-items own_dungeon]
        [--logic name=value ...]

Writes ``<out>/spoiler.json``. The patch plan and the mod folder come in a later round.
"""

import argparse
import json
import sys
from pathlib import Path

from clawshot.generate import FillError, Settings, generate, spoiler_json
from clawshot.generate.fill import DUNGEON_ITEM_CHOICES
from clawshot.world.load import WorldError, load_spec


def _logic_value(text: str) -> object:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m clawshot.generate", description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--shuffle", nargs="+", default=list(Settings().shuffle), help="location types to shuffle")
    parser.add_argument("--dungeon-items", choices=DUNGEON_ITEM_CHOICES, default=Settings().dungeon_items)
    parser.add_argument("--logic", nargs="*", default=[], metavar="NAME=VALUE", help="logic setting overrides")
    args = parser.parse_args(argv)

    logic = {}
    for pair in args.logic:
        name, sep, value = pair.partition("=")
        if not sep:
            parser.error(f"--logic expects NAME=VALUE, got {pair!r}")
        logic[name] = _logic_value(value)
    settings = Settings(shuffle=tuple(args.shuffle), dungeon_items=args.dungeon_items, logic=logic)
    try:
        seed = generate(load_spec(), args.seed, settings)
    except (FillError, WorldError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / "spoiler.json"
    path.write_text(spoiler_json(seed), encoding="utf-8", newline="\n")
    print(f"seed {seed.seed}: {len(seed.shuffled)} locations shuffled, {len(seed.spheres)} spheres; wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
