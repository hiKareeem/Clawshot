"""Lake tree vines follow Longshot acquisition without changing Water Temple progress."""

# SPDX-License-Identifier: Apache-2.0
# Changed from Goggles of Truth by AbyssDragonModding, src/generator/longshot_vines.zig
# at 523487f37adf5637c28786c752d5124e5865d06e: Zig -> Python, strict source-Hash/polarity
# validation and checked BYML transforms for Clawshot's common writer. See LICENSE.txt and root NOTICE.

from functools import partial

from clawshot.formats import byml
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

SOURCES = {
    "Banc/HyruleField/HyruleField_Child_Dynamic.bcett.byml.zs": 6295005719083773433,
    "Banc/HyruleField/HyruleField_Adult_Dynamic.bcett.byml.zs": 9829790505452123995,
}
WALL = "FldObj_AirWall_Hookshot"
CHEST_FLAG = "WaterTemple_Room07_00"
OWNED_FLAG = "IsGet.Item_Longshot"


def _patch(data: bytes, *, path: str, actor_hash: int) -> bytes:
    document = byml.load(data)
    actors = document.root.get("Actors") if isinstance(document.root, dict) else None
    if not isinstance(actors, list):
        raise PatchError(f"{path}: no Actors list for the Lake tree hook wall")
    found = [a for a in actors if isinstance(a, dict) and a.get("Hash") == actor_hash]
    if len(found) != 1:
        raise PatchError(f"{path}: {len(found)} actors have Lake tree wall Hash {actor_hash}, expected one")
    wall = found[0]
    presence = wall.get("Presence")
    if (
        wall.get("Gyaml") != WALL
        or not isinstance(presence, dict)
        or presence.get("FlagName") != CHEST_FLAG
        or presence.get("IsNegation") is not True
        or presence.get("IsCheckLazy") is not False
    ):
        raise PatchError(f"{path}: Lake tree wall {actor_hash} has unexpected Gyaml/Presence: {wall!r}")
    # Keep the wall until the actual Longshot is acquired; Room07's own source state stays native.
    presence["FlagName"] = OWNED_FLAG
    result = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(result))) is not None:
        raise PatchError(f"{path}: Lake tree wall does not round-trip: {difference}")
    return result


def changes() -> FileChanges:
    """Always-on transforms, composed with other Field edits after chest placement by the common writer."""
    return {path: partial(_patch, path=path, actor_hash=actor_hash) for path, actor_hash in SOURCES.items()}
