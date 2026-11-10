"""Door of Time modes (D35): native closed, playable Song of Time only, or physically open.

No stone quest, inventory grant, saved default or first-adult scene is forged. Native facts and
pending gameplay acceptance: plans/03-game-data.md section 41 and rounds/r10-agetravel.md.
"""

import argparse
import hashlib
import sys
from collections.abc import Mapping
from pathlib import Path

from clawshot.formats import byml, evfl, rstb, zsdic
from clawshot.patch import age
from clawshot.patch.gamedata import GAME_DATA_LIST, BuiltFile
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import FileChanges, WrittenFile
from clawshot.patch.write import write as write_patch
from clawshot.save import key

MODES = ("closed", "song_only", "open")
FLOW = "Event/EventFlow/DoorOfTime.bfevfl.zs"
PLACEMENT = "Banc/Market/Market_Child_Static.bcett.byml.zs"
DOOR_LOGIC = "Logic/Market_Common_f252.logic.module.ainb"
DOOR_LOGIC_SHA256 = "5b4152c4e56bf51b7f2400fbdd6a39e4b506f3104cee49a24f6f49e72eb4d6a4"
DRAW_GROUP = 11738513547087641325
DRAW_LOGIC = "Logic/Module/Market_Child_Prefab/Market_Child_Prefab_e700.logic.module.ain"
DRAW_BINDINGS = {
    "EventRequestActor_7fe2": (17385100471140562353, "EventRequestActor"),
    "EventRequestActor_0b2e": (2548516804884289836, "EventRequestActor"),
    "Obj_TimeTemple_MasterSword_A_01_e482": (1016238122178870176, "Obj_TimeTemple_MasterSword_A_01"),
}
OPENED = "Market_Child_TimeTempleDoor_Opened"
REACTION = "Market_Child_TimeTempleDoor_OcarinaReacts"
TIME_SONG = "IsGet.Item_Melody_TimeSong"


def song_reaction(data: bytes) -> bytes:
    """The altar may react before Step05; the native opened flag still stops replacement events."""
    document = byml.load(data)
    found = [row for row in document.root["Data"]["BoolExp"] if row.get("Hash") == key(REACTION)]
    expected = [
        [byml.U64(1), byml.U64(key("Step_DoorOfTime"))],
        [byml.U64(2), byml.U64(key("Step05"))],
        [byml.U64(5)],
        [byml.U64(0), byml.U64(key(OPENED))],
        [byml.U64(4)],
    ]
    if len(found) != 1 or found[0].get("Values") != expected or found[0].get("SaveFileIndex") != -1:
        raise PatchError(f"song_only: changed altar reaction expression: {found!r}")
    found[0]["Values"] = [[byml.U64(0), byml.U64(key(OPENED))]]
    result = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(result))) is not None:
        raise PatchError(f"song_only: written reaction does not read back: {difference}")
    return result


def song_flow(data: bytes) -> bytes:
    """Bypass only the quest gate; require a learned song and retain native play/once/scene actions."""
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != "DoorOfTime":
        raise PatchError("song_only: expected DoorOfTime flowchart")
    events = {event.name: (index, event) for index, event in enumerate(fc.events)}
    required = ("Event92", "Event60", "Event69", "Event18")
    if any(name not in events for name in required):
        raise PatchError("song_only: missing native door gate events")
    gate_index, gate = events["Event60"]
    opened_index, opened = events["Event69"]
    _, predecessor = events["Event92"]
    entries = [entry for entry in fc.entry_points if entry.name == "DoorOfTime_OpenDoor"]
    if (
        not isinstance(gate, evfl.SwitchEvent)
        or fc.actors[gate.actor].name != "GameDataActor"
        or fc.actors[gate.actor].queries[gate.query] != "EventQueryIsGameDataBoolExp"
        or gate.params != {"GameDataName": "DoorOfTime_IsAfter_Step04_Exp"}
        or gate.cases != [(0, opened_index)]
        or not isinstance(opened, evfl.SwitchEvent)
        or opened.params != {"GameDataName": OPENED, "Index": -1}
        or not isinstance(predecessor, evfl.ActionEvent)
        or predecessor.next != gate_index
        or len(entries) != 1
        or entries[0].main_event != events["Event18"][0]
    ):
        raise PatchError(f"song_only: changed native door chain: {gate!r}, {opened!r}, {predecessor!r}")
    actor = fc.actors[opened.actor]
    query = actor.queries.index("EventQueryIsGameDataBool")
    first = entries[0].main_event
    entries[0].main_event = len(fc.events)
    fc.events.append(
        evfl.SwitchEvent(
            "ClawshotDoorLearnedTime", opened.actor, query, [(0, first)], {"GameDataName": TIME_SONG, "Index": -1}
        )
    )
    predecessor.next = opened_index
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError("song_only: written flow does not read back")
    return result


def open_pedestal(data: bytes) -> bytes:
    """Use the ungated native attention module; Draw itself selects first-pull versus repeat travel."""
    document = byml.load(data)
    tree = document.root
    found = [group for group in tree["AiGroups"] if group.get("Hash") == DRAW_GROUP]
    if len(found) != 1 or found[0].get("Logic") != DRAW_LOGIC:
        raise PatchError(f"open door: changed child pedestal group: {found!r}")
    group = found[0]
    refs = group.get("References", [])
    if len(refs) != len(DRAW_BINDINGS) or {r.get("Id") for r in refs} != DRAW_BINDINGS.keys():
        raise PatchError(f"open door: changed child pedestal references: {refs!r}")
    for ref in refs:
        actor_hash, actor_type = DRAW_BINDINGS[ref["Id"]]
        actors = [actor for actor in tree["Actors"] if actor.get("Hash") == actor_hash]
        if (
            ref.get("Path") != ref["Id"]
            or ref.get("Reference") != actor_hash
            or len(actors) != 1
            or actors[0].get("Gyaml") != actor_type
        ):
            raise PatchError(f"open door: changed child pedestal identity: {ref!r}, {actors!r}")
        if (
            ref["Id"] == "EventRequestActor_7fe2"
            and actors[0].get("Dynamic", {}).get("RequestEventName") != "Market_Child_DoorOfTime_Draw"
        ):
            raise PatchError(f"open door: changed first-pull request: {actors!r}")
    group["Logic"] = age.UNGATED_LOGIC
    group["References"] = [
        {**ref, "Id": "EventRequestActor_7a32" if ref["Id"] == "EventRequestActor_7fe2" else "CheckAttentionActor_8348"}
        for ref in refs
        if ref["Id"] != "EventRequestActor_0b2e"
    ]
    result = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(result))) is not None:
        raise PatchError(f"open door: written pedestal does not read back: {difference}")
    return result


def changes(_placements: Mapping[str, str], *, mode: str = "closed") -> FileChanges:
    if mode not in MODES:
        raise PatchError(f"unknown door_of_time mode {mode!r}")
    if mode == "song_only":
        return {FLOW: song_flow, GAME_DATA_LIST: song_reaction}
    return {PLACEMENT: open_pedestal} if mode == "open" else {}


def build(romfs: str | Path, *, mode: str = "closed") -> list[BuiltFile]:
    """Open the native gate at Ready or later, without resizing/repacking its AINB string pool.

    The exact native module has ONE Step06 literal; only its threshold string changes. Both
    is-after/is-equal feed the door's open/skip-animation signal. No instruction or pointer changes.
    Same-size resources retain their audited allocation; no generic AINB size formula is invented.
    """
    if mode not in MODES:
        raise PatchError(f"unknown door_of_time mode {mode!r}")
    if mode != "open":
        return []
    romfs = Path(romfs)
    data = (romfs / DOOR_LOGIC).read_bytes()
    if hashlib.sha256(data).hexdigest() != DOOR_LOGIC_SHA256 or data.count(b"Step06\0") != 1:
        raise PatchError("open door: native common door module fingerprint/Step06 literal changed")
    content = data.replace(b"Step06\0", b"Ready\0\0")
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    entry = table.get(DOOR_LOGIC)
    if entry is None or entry < len(content):
        raise PatchError(f"open door: missing/short native module allocation {entry!r}")
    return [BuiltFile(DOOR_LOGIC, content, len(data), len(content), entry)]


def write(romfs: str | Path, out: str | Path, *, mode: str = "closed") -> list[WrittenFile]:
    return write_patch(
        Plan([], [], []), romfs, out, extra_changes=[changes({}, mode=mode)], fast_start_files=build(romfs, mode=mode)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--romfs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--door-of-time", choices=MODES, default="closed")
    args = parser.parse_args(argv)
    try:
        files = write(args.romfs, args.out, mode=args.door_of_time)
    except PatchError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    for file in files:
        print(f"{file.path}: {file.size} -> {file.new_size}; allocation {file.entry} -> {file.new_entry}")
    print(f"door_of_time={args.door_of_time}; wrote {len(files)} resources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
