import pytest

from clawshot.census import hints
from clawshot.formats import evfl, msbt, rstb, sarc, zsdic
from clawshot.patch import items, text


@pytest.fixture(scope="module")
def dicts(romfs):
    return zsdic.Dictionaries.from_romfs(romfs)


@pytest.fixture(scope="module")
def size_table(romfs, dicts):
    return rstb.read(dicts.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))


@pytest.mark.dump
def test_dump_gossip_flow_without_mask_changes_only_the_two_questions(romfs, dicts, size_table):
    path = hints.flow_path(romfs, hints.GOSSIP_FLOW)
    data = dicts.decompress(path, (romfs / path).read_bytes())
    written = text.gossip_flow_transform(data)
    before, after = evfl.read(data).flowchart, evfl.read(written).flowchart
    changed = [b.name for b, a in zip(before.events, after.events, strict=True) if b != a]
    assert sorted(changed) == ["Event112", "Event25"]
    assert (before.actors, before.entry_points) == (after.actors, after.entry_points)
    assert [g for g in hints.talk_gates(after) if hints.MASK_OF_TRUTH in dict(g.params).values()] == []
    print(f"{path}: {len(data)} -> {len(written)} bytes, size entry {size_table.get(path)}")
    assert rstb.required_size(path, len(written)) <= size_table.get(path)


@pytest.mark.dump
def test_dump_one_stone_line_changes_and_nothing_else(romfs, dicts, size_table):
    path = text.archive_path("USen")
    data = dicts.decompress(path, (romfs / path).read_bytes())
    line = ["Clawshot test line."]
    written = text.edit_messages({hints.GOSSIP_MESSAGES: {"GOSSIP_KOKIRI_FOREST_01": line}})(data)
    before, after = sarc.read(data), sarc.read(written)
    assert [name for name in before if before[name] != after[name]] == [hints.GOSSIP_MESSAGES]
    old, new = msbt.read(before[hints.GOSSIP_MESSAGES]), msbt.read(after[hints.GOSSIP_MESSAGES])
    assert [label for label in old.messages if old.messages[label] != new.messages[label]] == [
        "GOSSIP_KOKIRI_FOREST_01"
    ]
    assert new.messages["GOSSIP_KOKIRI_FOREST_01"] == line
    print(f"{path}: {len(data)} -> {len(written)} bytes, size entry {size_table.get(path)}")


@pytest.mark.dump
def test_dump_every_placeable_item_has_a_name_and_get_text_in_every_language(romfs, dicts):
    actors = sorted(set(items.load().actors.values()))
    keys = {actor: text.read_text_key(romfs, actor, dicts) for actor in actors}
    for language in text.languages(romfs):
        path = text.archive_path(language)
        pouch = msbt.read(sarc.read(dicts.decompress(path, (romfs / path).read_bytes()))[text.POUCH_TEXT])
        missing = [
            (actor, key)
            for actor, key in keys.items()
            if f"{key}_Name" not in pouch.messages or f"{key}_GetMessage" not in pouch.messages
        ]
        assert not missing, f"{language}: {missing}"
    print(f"{len(actors)} item actors, all with a name and get text under their ActorName key in 16 languages")
