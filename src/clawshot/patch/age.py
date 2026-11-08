"""Default-off free time travel: keep the adult pedestal's attention actor before Forest clear.

Only its AiGroup module and reference bindings change. The existing ungated Spirit Temple module sends
ReceiveDoAction to the existing EventRequestActor, without the Forest-completion deletion input.
Forest quest progress, Sheik/Prelude and all event flows remain untouched (game-data plan section 16).
"""

import argparse
import sys
from collections.abc import Mapping
from pathlib import Path

from clawshot.formats import byml
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import FileChanges, WrittenFile
from clawshot.patch.write import write as write_patch

PLACEMENT = "Banc/Market/Market_Adult_Static.bcett.byml.zs"
GROUP_HASH = 2075259738076588912
GATED_LOGIC = "Logic/Module/Market_Adult_Prefab/Market_Adult_Prefab_89da.logic.module.ain"
UNGATED_LOGIC = "Logic/Module/SpiritTemple_Prefab/SpiritTemple_Prefab_5299.logic.module.ain"
# Module input Id -> (existing actor Hash, actor type, ungated module input Id).
BINDINGS = {
    "EventRequestActor_9bc1": (16146179233394378722, "EventRequestActor", "EventRequestActor_7a32"),
    "Obj_TimeTemple_MasterSword_A_01_b347": (
        7921822793324574197,
        "Obj_TimeTemple_MasterSword_A_01",
        "CheckAttentionActor_8348",
    ),
}


def patch_tree(tree: dict) -> None:
    """Rebind only the known adult pedestal group; reject changed actor/module identities before mutation."""
    groups = tree.get("AiGroups", [])
    found = [group for group in groups if group.get("Hash") == GROUP_HASH]
    if len(found) != 1 or found[0].get("Logic") != GATED_LOGIC:
        raise PatchError(f"{PLACEMENT}: expected one gated pedestal group {GROUP_HASH}; found {found!r}")
    group = found[0]
    refs = group.get("References", [])
    if len(refs) != len(BINDINGS) or {ref.get("Id") for ref in refs} != BINDINGS.keys():
        raise PatchError(f"{PLACEMENT}: unexpected pedestal reference bindings {refs!r}")
    for ref in refs:
        actor_hash, actor_type, _ = BINDINGS[ref["Id"]]
        actors = [actor for actor in tree.get("Actors", []) if actor.get("Hash") == actor_hash]
        if (
            ref.get("Reference") != actor_hash
            or ref.get("Path") != ref["Id"]
            or len(actors) != 1
            or actors[0].get("Gyaml") != actor_type
        ):
            raise PatchError(f"{PLACEMENT}: changed pedestal actor binding {ref!r}; actors {actors!r}")
        if actor_type == "EventRequestActor":
            event = actors[0].get("Dynamic", {}).get("RequestEventName")
            if event != "Market_Adult_Field_AdultToChild":
                raise PatchError(f"{PLACEMENT}: pedestal requests {event!r}, not adult-to-child travel")
    group["Logic"] = UNGATED_LOGIC
    for ref in refs:
        ref["Id"] = BINDINGS[ref["Id"]][2]


def transform(data: bytes) -> bytes:
    """Transform decompressed placement bytes, preserving byte order and checking the written tree."""
    document = byml.load(data)
    patch_tree(document.root)
    result = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(result))) is not None:
        raise PatchError(f"{PLACEMENT}: free-travel patch did not read back: {difference}")
    return result


def changes(_placements: Mapping[str, str], *, free_time_travel: bool = False) -> FileChanges:
    """A seed PatchStep (bind the keyword to its matching logic setting); common writer handles sizes/compression."""
    return {PLACEMENT: transform} if free_time_travel else {}


def write(romfs: str | Path, out: str | Path, *, free_time_travel: bool = False) -> list[WrittenFile]:
    """Write a standalone test overlay through the same guarded writer used for seeds."""
    return write_patch(Plan([], [], []), romfs, out, extra_changes=[changes({}, free_time_travel=free_time_travel)])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--romfs", type=Path, required=True, help="game dump (read-only)")
    parser.add_argument("--out", type=Path, required=True, help="empty or absent output directory")
    parser.add_argument("--free-time-travel", action="store_true", help="enable the default-off pedestal patch")
    args = parser.parse_args(argv)
    try:
        files = write(args.romfs, args.out, free_time_travel=args.free_time_travel)
    except PatchError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    for file in files:
        print(f"{file.path}: {file.size} -> {file.new_size} bytes; size entry {file.entry} -> {file.new_entry}")
    print(f"free_time_travel={args.free_time_travel}; wrote {len(files)} files to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
