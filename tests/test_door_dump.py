"""Native door overlays: behavioral flow oracle, exact inverse edits and composed GameData."""

from copy import deepcopy

import pytest
from test_door import run_open_flow

from clawshot.formats import byml, evfl, rstb, zsdic
from clawshot.patch import age, door
from clawshot.patch.plan import Plan
from clawshot.patch.write import write
from clawshot.save import key

pytestmark = pytest.mark.dump


def test_song_only_native_output_keeps_play_once_and_all_other_story_paths(romfs, tmp_path):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    out = tmp_path / "song-only"
    write(
        Plan([], [], []),
        romfs,
        out,
        extra_changes=[age.changes({}, free_time_travel=True), door.changes({}, mode="song_only")],
    )
    native = evfl.read(dictionaries.decompress(door.FLOW, (romfs / door.FLOW).read_bytes()))
    patched = evfl.read(dictionaries.decompress(door.FLOW, (out / "romfs" / door.FLOW).read_bytes()))
    for learned, recommended, opened in [
        (True, True, False),
        (False, True, False),
        (True, False, False),
        (True, True, True),
    ]:
        state = {door.TIME_SONG: learned, door.OPENED: opened}
        scenes, writes = run_open_flow(patched.flowchart, state, recommended=recommended)
        success = learned and recommended and not opened
        assert scenes == (["Dm_TimeTemple_0010"] if success else [])
        assert (door.OPENED in writes) == success
        assert ("Step_DoorOfTime" in writes) == success
        assert not any(name.startswith("Step_Get_Stone") or name.startswith("IsGet.") for name in writes)
        if success:
            assert run_open_flow(patched.flowchart, deepcopy(state)) == ([], [])
    old_fc, new_fc = native.flowchart, patched.flowchart
    new_fc.events.pop()
    new_fc.entry_point("DoorOfTime_OpenDoor").main_event = old_fc.entry_point("DoorOfTime_OpenDoor").main_event
    old_predecessor = next(event for event in old_fc.events if event.name == "Event92")
    next(event for event in new_fc.events if event.name == "Event92").next = old_predecessor.next
    assert native == patched  # Other entries, grants, first pull, Rauru and repeat travel untouched.

    native_game = byml.load(dictionaries.decompress(door.GAME_DATA_LIST, (romfs / door.GAME_DATA_LIST).read_bytes()))
    new_game = byml.load(
        dictionaries.decompress(door.GAME_DATA_LIST, (out / "romfs" / door.GAME_DATA_LIST).read_bytes())
    )
    assert new_game.byte_order == native_game.byte_order
    added = new_game.root["Data"]["BoolExp"].pop()
    assert added["Hash"] == key(age.SHEIK_PRESENCE)
    old_reaction = next(row for row in native_game.root["Data"]["BoolExp"] if row["Hash"] == key(door.REACTION))
    new_reaction = next(row for row in new_game.root["Data"]["BoolExp"] if row["Hash"] == key(door.REACTION))
    assert new_reaction["Values"] == [[byml.U64(0), byml.U64(key(door.OPENED))]]
    new_reaction["Values"] = old_reaction["Values"]
    assert byml.same(native_game.root, new_game.root)
    table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (out / "romfs" / rstb.TABLE_PATH).read_bytes()))
    for path in (age.PLACEMENT, door.FLOW, door.GAME_DATA_LIST):
        size = len(dictionaries.decompress(path, (out / "romfs" / path).read_bytes()))
        assert table.get(path) >= rstb.required_size(path, size)


def test_open_native_door_and_first_pull_need_no_quest_forgery(romfs, tmp_path):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    out = tmp_path / "open"
    written = door.write(romfs, out, mode="open")
    original = byml.load(dictionaries.decompress(door.PLACEMENT, (romfs / door.PLACEMENT).read_bytes()))
    patched = byml.load(dictionaries.decompress(door.PLACEMENT, (out / "romfs" / door.PLACEMENT).read_bytes()))
    old_group = next(group for group in original.root["AiGroups"] if group["Hash"] == door.DRAW_GROUP)
    new_group = next(group for group in patched.root["AiGroups"] if group["Hash"] == door.DRAW_GROUP)
    assert new_group["Logic"] == age.UNGATED_LOGIC
    assert {ref["Id"]: ref["Reference"] for ref in new_group["References"]} == {
        "EventRequestActor_7a32": 17385100471140562353,
        "CheckAttentionActor_8348": 1016238122178870176,
    }
    new_group.clear()
    new_group.update(old_group)
    assert byml.same(original.root, patched.root)
    assert original.byte_order == patched.byte_order
    old_module = (romfs / door.DOOR_LOGIC).read_bytes()
    new_module = (out / "romfs" / door.DOOR_LOGIC).read_bytes()
    offset = old_module.index(b"Step06\0")
    assert len(new_module) == len(old_module)
    assert new_module[offset : offset + 7] == b"Ready\0\0"
    assert new_module[:offset] + b"Step06\0" + new_module[offset + 7 :] == old_module
    assert {file.path for file in written} == {door.PLACEMENT, door.DOOR_LOGIC}
    assert not (out / "romfs" / door.FLOW).exists()
    assert not (out / "romfs" / door.GAME_DATA_LIST).exists()
    # Closed is the actual no-patch control, not another state-setting route.
    assert door.write(romfs, tmp_path / "closed", mode="closed") == []
