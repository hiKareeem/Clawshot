"""Fast start on the dump (``-m dump``): every setting in ``fast_start.toml`` applies to the game's data, and the
written files differ from the game's only in the selected and always-on initial values and flow edits."""

import pytest

from clawshot.formats import byml, rstb, zsdic
from clawshot.patch import gamedata
from clawshot.save import murmur3_32

pytestmark = pytest.mark.dump


def by_hash(tree: dict) -> dict[tuple[str, int], dict]:
    return {(t, e["Hash"]): e for t, entries in tree["Data"].items() for e in entries}


def test_all_settings_change_only_their_entries(romfs, tmp_path):
    settings = gamedata.load()
    chosen = [*gamedata.load_always(), *gamedata.select(settings, list(settings))]
    out = tmp_path / "out"
    files = {f.path: f for f in gamedata.write(romfs, out, list(settings))}
    dicts = zsdic.Dictionaries.from_romfs(romfs)

    def written(path: str) -> bytes:
        return dicts.decompress(path, (out / "romfs" / path).read_bytes())

    path = gamedata.GAME_DATA_LIST
    old_data = dicts.decompress(path, (romfs / path).read_bytes())
    new_data = written(path)
    print(f"{path}: {len(old_data)} -> {len(new_data)} bytes, size-table entry {files[path].entry}")
    assert len(new_data) == len(old_data)  # initial values are stored in place
    old, new = byml.load(old_data), byml.load(new_data)
    assert new.byte_order == old.byte_order == "big"
    assert byml.same(old.root["MetaData"], new.root["MetaData"])
    old_entries, new_entries = by_hash(old.root), by_hash(new.root)
    assert old_entries.keys() == new_entries.keys()
    changed = {}
    for key, entry in old_entries.items():
        other = new_entries[key]
        fields = {k for k in entry.keys() | other.keys() if not byml.same(entry.get(k), other.get(k))}
        if fields:
            changed[key] = fields
    wanted = {}
    for setting in chosen:
        for flag, value in setting.game_data.items():
            [list_type] = [t for t in gamedata.VALUE_TYPES if (t, murmur3_32(flag.encode())) in old_entries]
            wanted[(list_type, murmur3_32(flag.encode()))] = value
    assert changed == dict.fromkeys(wanted, {"DefaultValue"})
    for (list_type, key), value in wanted.items():
        stored = new_entries[(list_type, key)]["DefaultValue"]
        assert stored == (murmur3_32(value.encode()) if list_type == "Enum" else value)

    edits = dict.fromkeys(edit for s in chosen for edit in s.flow_edits)
    flows = [gamedata.FLOW_EDITS[edit] for edit in edits]
    table = rstb.read(dicts.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    grown = [p for p, f in files.items() if p != rstb.TABLE_PATH and f.new_entry != table.get(p)]
    assert sorted(files) == sorted([path, *(p for p, _ in flows), *([rstb.TABLE_PATH] if grown else [])])
    for flow, _ in flows:
        print(f"{flow}: {files[flow].size} -> {files[flow].new_size} bytes, entry {files[flow].new_entry}")
        assert files[flow].new_entry >= rstb.required_size(flow, files[flow].new_size)
