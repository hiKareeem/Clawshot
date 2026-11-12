"""Write the mod for one Archipelago slot: the placements come from the multiworld's fill, not Clawshot's.

    python -m clawshot.ap --romfs <dump> --slot <slot.json> --out <dir>

``<slot.json>`` is what the Archipelago world writes into its patch file (``FORMAT`` below)::

    {"format": 1, "seed": 123, "settings": {<Settings fields>}, "placements": {"<location>": "<item>", ...}}

Every shuffled location must be named. A location holding another player's item names :data:`FOREIGN_ITEM`, the
native pickup the chest shows; the runtime module reports the check from the chest's own flag either way. The
module's received-item counter is :data:`RECEIVED_BITS` saved Bools added to the GameDataList, so a loaded save
knows how many multiworld items it already holds.

The APWorld (``ounce-ocarina-ap``) reads this module's constants through its sync tool: change them here only.
"""

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from clawshot.generate import FillError, Settings
from clawshot.pack import PackError
from clawshot.patch import PatchError, SeedOutput, make_seed, write_seed

FORMAT = 1
FOREIGN_ITEM = "Rupee (1)"
"""The native item a check holding another player's item gives: a chest-verified actor (TBox_Rupee_Green)."""
RECEIVED_BITS = 16
RECEIVED_FLAG = "Archipelago.ReceivedIndex.Bit{bit:02d}"
"""Saved Bool names of the received-item counter, bit 0 first (murmur3 of each is the GameData key)."""


def received_flags() -> list[str]:
    return [RECEIVED_FLAG.format(bit=bit) for bit in range(RECEIVED_BITS)]


def load_slot(data: Mapping[str, Any]) -> tuple[int, Settings, dict[str, str]]:
    if data.get("format") != FORMAT:
        raise ValueError(f"slot file format {data.get('format')!r}; this Clawshot reads format {FORMAT}")
    seed, placements = data.get("seed"), data.get("placements")
    if type(seed) is not int or not isinstance(placements, dict):
        raise ValueError("slot file needs an integer seed and a placements table")
    if not all(isinstance(k, str) and isinstance(v, str) for k, v in placements.items()):
        raise ValueError("placements map location names to item names")
    return seed, Settings(**data.get("settings", {})), dict(placements)


def make_ap_seed(romfs: str | Path, data: Mapping[str, Any]) -> SeedOutput:
    seed, settings, placements = load_slot(data)
    return make_seed(romfs, seed, settings, placements=placements, game_data_flags=received_flags())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m clawshot.ap", description=__doc__.splitlines()[0])
    parser.add_argument("--romfs", type=Path, required=True, help="romfs folder, dump folder, .nup or .nx")
    parser.add_argument("--slot", type=Path, required=True, help="the slot JSON from the Archipelago patch file")
    parser.add_argument("--out", type=Path, required=True, help="the mod folder to write (empty or absent)")
    args = parser.parse_args(argv)
    from clawshot.pack.source import local_romfs
    from clawshot.patch.write import check_output_folder

    try:
        data = json.loads(args.slot.read_text(encoding="utf-8"))
        with local_romfs(args.romfs, None) as romfs:
            check_output_folder(Path(romfs), args.out)
            output = make_ap_seed(romfs, data)
            written = write_seed(output, romfs, args.out)
    except (OSError, ValueError, FillError, PackError, PatchError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"wrote {len(written)} files to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
