"""Generate a seed as a mod folder.

    python -m clawshot --romfs <dump> --seed <n> --out <dir> [--shuffle Chest ...] [--dungeon-items own_dungeon]
        [--logic name=value ...] [--areas <Banc folder> ... --goal <rule>]

Reads the player's dump (read only), shuffles chests and optionally native shop contents,
checks beatability, and writes changed resources (plus the size table when needed)
under ``<out>/romfs`` and the placements/spheres/patch plan to ``<out>/spoiler.json``.
``--areas`` with ``--goal`` makes a slice: only those areas' regions, beaten when the goal holds (round 3's
playtest: ``--areas KokiriForest LostWood InsideTheDekuTree --goal "'Defeat Queen Gohma'"``).
"""

import argparse
import json
import sys
from pathlib import Path

from clawshot.generate import FillError, Settings
from clawshot.generate.fill import DUNGEON_ITEM_CHOICES
from clawshot.patch import PatchError, make_seed, write_seed
from clawshot.patch.items import ItemActorError
from clawshot.patch.write import check_output_folder
from clawshot.world.load import WorldError


def _logic_value(text: str) -> object:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m clawshot", description=__doc__.splitlines()[0])
    parser.add_argument("--romfs", type=Path, required=True, help="the game's romfs folder (read only)")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True, help="the mod folder to write (empty or absent)")
    parser.add_argument(
        "--shuffle",
        nargs="+",
        choices=("Chest", "Shop"),
        default=list(Settings().shuffle),
        help="location types to shuffle; Shop uses native displays only",
    )
    parser.add_argument("--dungeon-items", choices=DUNGEON_ITEM_CHOICES, default=Settings().dungeon_items)
    parser.add_argument("--logic", nargs="*", default=[], metavar="NAME=VALUE", help="logic setting overrides")
    parser.add_argument("--areas", nargs="+", default=[], metavar="AREA", help="census areas of a slice")
    parser.add_argument("--goal", help="the slice's goal (a rule); needs --areas")
    args = parser.parse_args(argv)

    logic = {}
    for pair in args.logic:
        name, sep, value = pair.partition("=")
        if not sep:
            parser.error(f"--logic expects NAME=VALUE, got {pair!r}")
        logic[name] = _logic_value(value)
    if args.areas and not args.goal:
        parser.error("--areas needs --goal (the world's goal lies outside most slices)")
    try:
        settings = Settings(
            shuffle=tuple(args.shuffle),
            dungeon_items=args.dungeon_items,
            logic=logic,
            areas=tuple(args.areas),
            goal=args.goal,
        )
    except ValueError as e:
        parser.error(str(e))
    try:
        check_output_folder(args.romfs, args.out)
        output = make_seed(args.romfs, args.seed, settings)
        written = write_seed(output, args.romfs, args.out)
    except (FillError, WorldError, PatchError, ItemActorError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    seed = output.seed
    print(f"seed {seed.seed}: {len(seed.shuffled)} locations shuffled, {len(seed.spheres)} spheres")
    for f in written:
        if f.entry is None:
            entry = ""
        elif f.new_entry == f.entry:
            entry = f", size-table entry {f.entry} kept"
        else:
            entry = f", size-table entry {f.entry} -> {f.new_entry}"
        print(
            f"  {f.path}: {f.size} -> {f.new_size} bytes ({f.new_size - f.size:+d}), "
            f"compressed {f.compressed_size} -> {f.new_compressed_size}{entry}"
        )
    print(f"wrote {len(written)} files under {args.out / 'romfs'} and {args.out / 'spoiler.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
