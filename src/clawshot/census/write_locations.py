"""Write the location definitions from the player's dump.

    python -m clawshot.census.write_locations --romfs <dir> --ootr <LocationList.py> [--out <file>] [--fresh]

Runs the census on ``<romfs>`` (read only), matches it against OoT Randomizer's ``LocationList.py`` (the file at
:data:`clawshot.census.ootr.OOTR_COMMIT`; not in this repository) and writes ``locations.toml``. For every id already
in the output file, its ``name`` and ``oot_randomizer_name`` are kept (hand edits), unless ``--fresh``. Prints how
each OoT Randomizer name was found and which ids were dropped.
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

from clawshot.census import definitions, ootr
from clawshot.census.scan import scan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m clawshot.census.write_locations", description=__doc__.split("\n")[0]
    )
    parser.add_argument("--romfs", required=True, type=Path)
    parser.add_argument("--ootr", required=True, type=Path, help="OoT Randomizer's LocationList.py")
    parser.add_argument("--out", type=Path, default=definitions.LOCATIONS_TOML)
    parser.add_argument("--fresh", action="store_true", help="ignore names in an existing output file")
    args = parser.parse_args(argv)

    locations = scan(args.romfs)
    table = ootr.read_location_list(args.ootr)
    matches = ootr.match(locations, table)
    existing = {}
    if args.out.exists() and not args.fresh:
        existing = {d.id: d for d in definitions.load(args.out)}
    defs = definitions.build(locations, matches, existing)

    known = {o.name for o in table}
    unknown = sorted({d.oot_randomizer_name for d in defs if d.oot_randomizer_name} - known)
    if unknown:
        print(f"error: oot_randomizer_name not in {args.ootr}: {unknown}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(definitions.dumps(defs).encode("utf-8"))

    ids = {d.id for d in defs}
    kept = sum(1 for i in existing if i in ids)
    print(f"{len(defs)} locations written to {args.out}; {kept} kept their names from the previous file")
    for i in sorted(set(existing) - ids):
        print(f"dropped (no longer in the census): {i} {existing[i].name}")
    basis = Counter(m.basis for i, m in matches.items() if i not in existing)
    print("new OoT Randomizer names by basis:", dict(sorted(basis.items())))
    print("with an OoT Randomizer name:", sum(1 for d in defs if d.oot_randomizer_name), "of", len(defs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
