"""Write the mod for one Archipelago slot: the placements come from the multiworld's fill, not Clawshot's.

    python -m clawshot.ap --romfs <dump> --slot <slot.json> --out <dir>

``<slot.json>`` is what the Archipelago world writes into its patch file (``FORMAT`` below)::

    {"format": 2, "seed": 123, "settings": {<Settings fields>}, "placements": {"<location>": "<item>", ...},
     "foreign": {"<location>": {"player": "<name>", "item": "<item name>", "own": false}, ...},
     "pickup_notice": false}

Every shuffled location must be named. A location holding another player's item names :data:`FOREIGN_ITEM` and has
an entry in ``foreign``: its chest shows Zelda's Letter and "You found <player>'s <item>!" in each language, and
gives nothing (``clawshot.patch.custom_items``); with ``"own": true`` (optional) it is this player's own item that the
multiworld gives instead, a progressive one, and says "You found your <item>!". ``Nothing`` is a get window with no
item. The player's own items
say "You found your <item>!". The runtime module reports a check from the chest's own flag either way. The module's
received-item counter is :data:`RECEIVED_BITS` saved Bools added to the GameDataList, so a loaded save knows how
many multiworld items it already holds.

A format-2 mod also holds the event the bridge requests to give consumables as the game gives them (rupees with the
counter, hearts and magic healed natively: ``patch.receive_event``); ``pickup_notice`` true also shows the game's
pick-up notice for each. Get windows show one box.

Format 1 (no ``foreign``; another player's item written as :data:`FOREIGN_ITEM_V1`) is still read.

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
from clawshot.patch import PatchError, SeedOutput, make_seed, receive_event, write_seed
from clawshot.patch.custom_items import FOREIGN_ITEM, NOTHING_ITEM, Foreign

FORMAT = 2
FORMATS = (1, 2)
FOREIGN_ITEM_V1 = "Rupee (1)"
"""Format 1's stand-in for another player's item: a chest-verified native actor (TBox_Rupee_Green)."""
__all__ = [
    "FOREIGN_ITEM",
    "NOTHING_ITEM",
    "FORMAT",
    "RECEIVED_BITS",
    "RECEIVED_FLAG",
    "load_slot",
    "make_ap_seed",
    "received_flags",
]
RECEIVED_BITS = 16
RECEIVED_FLAG = "Archipelago.ReceivedIndex.Bit{bit:02d}"
"""Saved Bool names of the received-item counter, bit 0 first (murmur3 of each is the GameData key)."""


def received_flags() -> list[str]:
    return [RECEIVED_FLAG.format(bit=bit) for bit in range(RECEIVED_BITS)]


def load_slot(data: Mapping[str, Any]) -> tuple[int, Settings, dict[str, str], dict[str, Foreign]]:
    if data.get("format") not in FORMATS:
        raise ValueError(f"slot file format {data.get('format')!r}; this Clawshot reads formats {FORMATS}")
    seed, placements = data.get("seed"), data.get("placements")
    if type(seed) is not int or not isinstance(placements, dict):
        raise ValueError("slot file needs an integer seed and a placements table")
    if not all(isinstance(k, str) and isinstance(v, str) for k, v in placements.items()):
        raise ValueError("placements map location names to item names")
    foreign_data = data.get("foreign", {}) if data["format"] >= 2 else {}
    if not isinstance(foreign_data, dict):
        raise ValueError("foreign maps location names to {player, item}")
    foreign = {}
    for location, entry in foreign_data.items():
        if not (
            isinstance(entry, dict) and isinstance(entry.get("player"), str) and isinstance(entry.get("item"), str)
        ):
            raise ValueError(f"foreign[{location!r}] needs a player and an item name")
        if "own" in entry and type(entry["own"]) is not bool:
            raise ValueError(f"foreign[{location!r}]: own is true or false")
        foreign[location] = Foreign(entry["player"], entry["item"], entry.get("own", False))
    return seed, Settings(**data.get("settings", {})), dict(placements), foreign


def make_ap_seed(romfs: str | Path, data: Mapping[str, Any]) -> SeedOutput:
    seed, settings, placements, foreign = load_slot(data)
    flags = received_flags()
    if data.get("format") >= 2 and data.get("pickup_notice") is True:
        flags.append(receive_event.NOTICE_FLAG)
    return make_seed(
        romfs,
        seed,
        settings,
        placements=placements,
        game_data_flags=flags,
        foreign=foreign,
        possessive_text=data.get("format") >= 2,
        receive_event=data.get("format") >= 2,
    )


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
