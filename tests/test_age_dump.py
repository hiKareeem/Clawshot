"""Free travel changes only the adult pedestal binding and the placed Temple Sheik's Presence."""

from copy import deepcopy

import pytest

from clawshot.formats import byml, rstb, zsdic
from clawshot.patch import age

pytestmark = pytest.mark.dump


def test_free_travel_preserves_prelude_and_changes_only_pedestal_and_sheik(romfs, tmp_path):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    original = (romfs / age.PLACEMENT).read_bytes()
    old_data = dictionaries.decompress(age.PLACEMENT, original)
    old = byml.load(old_data)
    expected = deepcopy(old.root)
    [group] = [entry for entry in expected["AiGroups"] if entry["Hash"] == age.GROUP_HASH]
    group["Logic"] = age.UNGATED_LOGIC
    for ref in group["References"]:
        ref["Id"] = age.BINDINGS[ref["Id"]][2]
    [sheik] = [actor for actor in expected["Actors"] if actor["Hash"] == age.SHEIK_HASH]
    sheik["Presence"] = {
        "FlagName": age.SHEIK_PRESENCE,
        "IsCheckLazy": False,
        "IsNegation": False,
    }

    out = tmp_path / "overlay"
    written = age.write(romfs, out, free_time_travel=True)
    new_data = dictionaries.decompress(age.PLACEMENT, (out / "romfs" / age.PLACEMENT).read_bytes())
    new = byml.load(new_data)
    assert byml.same(expected, new.root)
    assert new.byte_order == old.byte_order
    assert (romfs / age.PLACEMENT).read_bytes() == original
    assert (romfs / "Logic/SpiritTemple_Prefab_5299.logic.module.ainb").is_file()
    table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    entry = table.get(age.PLACEMENT)
    assert entry is not None
    need = rstb.required_size(age.PLACEMENT, len(new_data))
    if need > entry:
        table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (out / "romfs" / rstb.TABLE_PATH).read_bytes()))
        assert table.get(age.PLACEMENT) == need
    game_path = age.GAME_DATA_LIST
    native_game = byml.load(dictionaries.decompress(game_path, (romfs / game_path).read_bytes()))
    patched_game = byml.load(dictionaries.decompress(game_path, (out / "romfs" / game_path).read_bytes()))
    assert patched_game.byte_order == native_game.byte_order
    added = patched_game.root["Data"]["BoolExp"].pop()
    from clawshot.save import key

    assert added["Hash"] == key(age.SHEIK_PRESENCE)
    assert added["SaveFileIndex"] == -1  # No new saved value or layout adjustment.
    assert byml.same(native_game.root, patched_game.root)
    assert {file.path for file in written} == {age.PLACEMENT, game_path, rstb.TABLE_PATH}
    for file in written:
        assert file.new_entry >= rstb.required_size(file.path, file.new_size) if file.entry else True
    print(f"adult pedestal: {len(old_data)} -> {len(new_data)}; size entry {entry} -> {max(entry, need)}")
