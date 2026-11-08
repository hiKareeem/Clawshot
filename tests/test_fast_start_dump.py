"""Fast start on the dump (``-m dump``): every setting in ``fast_start.toml`` applies to the game's data, and the
written files differ from the game's only in the chosen entries."""

import pytest

from clawshot.formats import byml, zsdic
from clawshot.patch import gamedata
from clawshot.save import murmur3_32

pytestmark = pytest.mark.dump


def by_hash(tree: dict) -> dict[tuple[str, int], dict]:
    return {(t, e["Hash"]): e for t, entries in tree["Data"].items() for e in entries}


@pytest.mark.parametrize("name", list(gamedata.load()))
def test_each_setting_applies_to_the_game_alone(romfs, name):
    assert gamedata.build(romfs, [name])


def test_all_settings_change_only_their_entries(romfs):
    settings = gamedata.load()
    files = {f.path: f for f in gamedata.build(romfs, list(settings))}
    dicts = zsdic.Dictionaries.from_romfs(romfs)

    path = gamedata.GAME_DATA_LIST
    old_data = dicts.decompress(path, (romfs / path).read_bytes())
    new_data = dicts.decompress(path, files[path].content)
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
    for setting in settings.values():
        for flag, value in setting.game_data.items():
            [list_type] = [t for t in gamedata.VALUE_TYPES if (t, murmur3_32(flag.encode())) in old_entries]
            wanted[(list_type, murmur3_32(flag.encode()))] = value
    assert changed == dict.fromkeys(wanted, {"DefaultValue"})
    for (list_type, key), value in wanted.items():
        stored = new_entries[(list_type, key)]["DefaultValue"]
        assert stored == (murmur3_32(value.encode()) if list_type == "Enum" else value)

    event_settings = byml.read(
        dicts.decompress(gamedata.EVENT_SETTING_TABLE, (romfs / gamedata.EVENT_SETTING_TABLE).read_bytes())
    )
    skippable = [e for s in settings.values() for e in s.skippable]
    lists = [gamedata.component_list_path(event_settings, e) for e in skippable]
    assert sorted(files) == sorted([path, *lists])
    for list_path in lists:
        old_list = byml.read((romfs / list_path).read_bytes())
        new_list = byml.read(files[list_path].content)
        print(f"{list_path}: {files[list_path].size} -> {files[list_path].new_size} bytes")
        del old_list["Components"][gamedata.SKIP_SETTING]
        assert byml.same(old_list, new_list)


def test_the_default_writes_only_the_intro_component_list(romfs, tmp_path):
    written = gamedata.write(romfs, tmp_path / "out", gamedata.defaults(gamedata.load()))
    assert [f.path for f in written] == [
        "Event/EventSetting/EventSettingComponentList/Dm_Kokiri_0000.engine__event__EventSettingComponentList.bgyml"
    ]
