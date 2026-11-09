"""Default-off free time travel: open the adult pedestal and clear pre-Forest Temple Sheik.

The ungated native pedestal module retains the adult-to-child request. Only Temple Sheik's placement
gains Forest-completion Presence, so he appears for the original Prelude scene, then disappears through
his untouched native completion gate. Quest progress, rewards and event flows stay native (section 38).
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
SHEIK_HASH = 2669233513522124871
SHEIK_GROUP_HASH = 6012439728933042438
SHEIK_LOGIC = "Logic/Module/Market_Adult_Prefab/Market_Adult_Prefab_7f43.logic.module.ain"
SHEIK_ID = "Npc_Hylia_Sheik_Adult_4b5b"
FOREST_COMPLETE = "SageOfForest_IsCompleted_Exp"


def patch_tree(tree: dict) -> None:
    """Validate both native contracts before changing the pedestal bindings and Temple Sheik's Presence."""
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
    sheiks = [actor for actor in tree.get("Actors", []) if actor.get("Hash") == SHEIK_HASH]
    sheik_groups = [entry for entry in groups if entry.get("Hash") == SHEIK_GROUP_HASH]
    expected_refs = [{"Id": SHEIK_ID, "Path": SHEIK_ID, "Reference": byml.U64(SHEIK_HASH)}]
    if (
        len(sheiks) != 1
        or sheiks[0].get("Gyaml") != "Npc_Hylia_Sheik_Adult"
        or sheiks[0].get("Phive", {}).get("Placement", {}).get("ID") != SHEIK_HASH
        or "Presence" in sheiks[0]
        or len(sheik_groups) != 1
        or sheik_groups[0].get("Logic") != SHEIK_LOGIC
        or sheik_groups[0].get("References") != expected_refs
    ):
        raise PatchError(f"{PLACEMENT}: changed Temple Sheik contract: actors {sheiks!r}; groups {sheik_groups!r}")
    group["Logic"] = UNGATED_LOGIC
    for ref in refs:
        ref["Id"] = BINDINGS[ref["Id"]][2]
    sheiks[0]["Presence"] = {"FlagName": FOREST_COMPLETE, "IsCheckLazy": False, "IsNegation": False}


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
    parser.add_argument("--free-time-travel", action="store_true", help="enable the default-off pedestal and Sheik patch")
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
