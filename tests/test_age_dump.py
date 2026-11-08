"""Free-travel overlay changes only the adult pedestal's module and its two input Ids."""

from copy import deepcopy

import pytest

from clawshot.formats import byml, rstb, zsdic
from clawshot.patch import age

pytestmark = pytest.mark.dump


def test_free_travel_changes_only_the_pedestal_binding(romfs, tmp_path):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    original = (romfs / age.PLACEMENT).read_bytes()
    old_data = dictionaries.decompress(age.PLACEMENT, original)
    old = byml.load(old_data)
    expected = deepcopy(old.root)
    [group] = [entry for entry in expected["AiGroups"] if entry["Hash"] == age.GROUP_HASH]
    group["Logic"] = age.UNGATED_LOGIC
    for ref in group["References"]:
        ref["Id"] = age.BINDINGS[ref["Id"]][2]

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
    assert {file.path for file in written} == {age.PLACEMENT} | ({rstb.TABLE_PATH} if need > entry else set())
    print(f"adult pedestal: {len(old_data)} -> {len(new_data)}; size entry {entry} -> {max(entry, need)}")
