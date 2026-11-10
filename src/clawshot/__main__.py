"""Generate a seed as a mod folder.

    python -m clawshot --romfs <dump> --seed <n> --out <dir> [--shuffle Chest ...] [--dungeon-items own_dungeon]
        [--skip intro saria mido deku_tree kaepora] [--logic name=value ...] [--areas <Banc folder> ... --goal <rule>]

Reads the player's dump (read only), shuffles chests and optionally native shop contents,
checks beatability, and writes changed resources (including selected fast-start files and the size table when needed)
under ``<out>/romfs`` and the placements/spheres/patch plan to ``<out>/spoiler.json``.
The intro is skippable by default; ``--skip`` alone disables all fast start.
``--areas`` with ``--goal`` makes a slice: only those areas' regions, beaten when the goal holds (round 3's
playtest: ``--areas KokiriForest LostWood InsideTheDekuTree --goal "'Defeat Queen Gohma'"``). ``--shuffle Gift`` also
moves the event gifts that can be changed (``clawshot.patch.gifts``); the others keep their items.
``--shuffle Scrub`` adds the four saved one-time scrub families; repeat vendors stay vanilla.
``--shuffle BossHeart`` adds native-only boss-heart pickups (off; in-game acceptance pending).
``--shuffle Freestanding`` adds the fourteen saved heart-piece floor checks (native palette only; off).
``Token`` is reserved and refused until replacement-pickup persistence is verified.
"""

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

from clawshot.generate import FillError, Settings
from clawshot.generate import hints as hint_choices
from clawshot.generate.fill import DUNGEON_ITEM_CHOICES
from clawshot.patch import PatchError, gamedata, gifts, make_seed, write_seed
from clawshot.patch.items import ItemActorError
from clawshot.patch.write import check_output_folder
from clawshot.world.load import WorldError, load_spec


def _logic_value(text: str) -> object:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m clawshot", description=__doc__.splitlines()[0])
    parser.add_argument("--romfs", type=Path, help="the game's romfs folder (read only)")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--out", type=Path, help="the mod folder to write (empty or absent)")
    parser.add_argument("--settings", help="a CS1 settings string; explicit options override it")
    parser.add_argument(
        "--print-settings", action="store_true", help="print the resolved string and exit; no dump needed"
    )
    parser.add_argument(
        "--shuffle",
        nargs="+",
        choices=("Chest", "Shop", gifts.SHUFFLE, "Scrub", "BossHeart", "Freestanding", "Token"),
        default=None,
        help=(
            "types; Shop: native displays; Gift: supported; Scrub: once sales; "
            "BossHeart/Freestanding: native pickups; Token: disabled"
        ),
    )
    parser.add_argument("--dungeon-items", choices=DUNGEON_ITEM_CHOICES)
    parser.add_argument(
        "--forest",
        choices=("closed", "closed_deku", "open"),
        help="closed: vanilla; closed_deku: exit only; open: exit and Mido",
    )
    parser.add_argument(
        "--door-of-time",
        choices=("closed", "song_only", "open"),
        help="closed: stones, Ocarina of Time and Time song (default); song_only: either ocarina; open: no items",
    )
    parser.add_argument(
        "--songs", choices=("song", "anywhere"), help="song locations only (default), or all songs anywhere"
    )
    parser.add_argument(
        "--shop-prices", choices=("vanilla", "affordable"), help="affordable: shuffled shop items cost 10"
    )
    parser.add_argument("--shop-slots", type=int, help="0..8 shuffled shelves per shop (first native indices)")
    parser.add_argument(
        "--scrub-prices", choices=("vanilla", "fixed"), help="price policy for supported shuffled once-sale scrubs"
    )
    parser.add_argument("--scrub-price", type=int, help="fixed scrub fee, 0..1000 rupees (default 10)")
    parser.add_argument(
        "--cheap-deku-shield",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Kokiri shop Deku Shield costs 10 (default on, including vanilla shops)",
    )
    parser.add_argument(
        "--hints",
        choices=hint_choices.MODES,
        help="Gossip Stones speak without the Mask of Truth (always, default) or only to child Link wearing it (mask)",
    )
    parser.add_argument("--hint-distribution", choices=hint_choices.distributions(), help="kinds of hint (balanced)")
    parser.add_argument("--logic", nargs="*", default=[], metavar="NAME=VALUE", help="logic setting overrides")
    parser.add_argument("--areas", nargs="+", metavar="AREA", help="census areas of a slice")
    parser.add_argument("--goal", help="the slice's goal (a rule); needs --areas")
    parser.add_argument(
        "--skip",
        nargs="*",
        choices=list(gamedata.load()),
        default=None,
        help="fast-start skips (default: intro); mido is a legacy alias for --forest open",
    )
    args = parser.parse_args(argv)

    try:
        settings = Settings.from_string(args.settings) if args.settings is not None else Settings()
        overrides = {}
        for option, field in (
            ("shuffle", "shuffle"),
            ("dungeon_items", "dungeon_items"),
            ("areas", "areas"),
            ("goal", "goal"),
            ("skip", "fast_start"),
            ("songs", "songs"),
            ("shop_prices", "shop_prices"),
            ("shop_slots", "shop_slots"),
            ("scrub_prices", "scrub_prices"),
            ("scrub_price", "scrub_price"),
            ("cheap_deku_shield", "cheap_deku_shield"),
            ("forest", "forest"),
            ("door_of_time", "door_of_time"),
            ("hints", "hints"),
            ("hint_distribution", "hint_distribution"),
        ):
            value = getattr(args, option)
            if value is not None:
                overrides[field] = tuple(value) if isinstance(value, list) else value
        logic = dict(settings.logic)
        for pair in args.logic:
            name, sep, value = pair.partition("=")
            if not name or not sep:
                parser.error(f"--logic expects NAME=VALUE, got {pair!r}")
            logic[name] = _logic_value(value)
        aliases = set(overrides.get("fast_start", ())) & {"mido", "forest_exit"}
        if aliases and args.forest is not None:
            wanted = "open" if "mido" in aliases else "closed_deku"
            if args.forest != wanted:
                parser.error("--forest conflicts with legacy --skip mido/forest_exit")
        if args.forest is not None or aliases:
            explicit_logic = {pair.partition("=")[0] for pair in args.logic}
            for name in ("open_forest", "skip_mido"):
                if name not in explicit_logic:
                    logic.pop(name, None)  # derived fields in an effective spoiler string must be rebuilt
        if args.door_of_time is not None:
            explicit_logic = {pair.partition("=")[0] for pair in args.logic}
            if "door_of_time" not in explicit_logic:
                logic.pop("door_of_time", None)
        settings = replace(settings, **overrides, logic=logic)
        if settings.areas and not settings.goal:
            parser.error("--areas needs --goal (the world's goal lies outside most slices)")
    except ValueError as e:
        parser.error(str(e))
    if args.print_settings:
        print(settings.to_string())
        return 0
    if args.romfs is None or args.seed is None or args.out is None:
        parser.error("generation needs --romfs, --seed and --out")
    try:
        check_output_folder(args.romfs, args.out)
        spec, steps = None, []
        if gifts.SHUFFLE in settings.shuffle or set(settings.shuffle).intersection(gifts.GIFT_TYPES):
            spec, settings, step = gifts.seed_setup(args.romfs, load_spec(), settings)
            steps.append(step)
        output = make_seed(args.romfs, args.seed, settings, spec, extra_steps=steps)
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
