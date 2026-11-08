import pytest

from clawshot.census import definitions
from clawshot.census.scan import scan
from clawshot.formats import byml, zsdic
from clawshot.generate import Settings
from clawshot.patch import drops, make_seed, write_seed
from clawshot.patch.write import patch_tree


@pytest.mark.dump
def test_boss_heart_seed_writes_native_pickups_without_changing_spawn_or_flags(romfs, tmp_path):
    output = make_seed(romfs, 7, Settings(shuffle=("Chest", "BossHeart")))
    seed = output.seed
    census = {loc.id: loc for loc in scan(romfs) if loc.kind == "heart_container"}
    names = {d.id: d.oot_randomizer_name for d in definitions.load() if d.id in census}
    assert len(names) == 8
    assert all(name in seed.shuffled for name in names.values())
    write_seed(output, romfs, tmp_path / "seed")
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    for actor_id, name in names.items():
        item = seed.placements[name]
        assert item in drops.NATIVE_ITEMS
        loc = census[actor_id]
        for path in loc.files:
            original_raw = dicts.decompress(path, (romfs / path).read_bytes())
            target = tmp_path / "seed" / "romfs" / path
            raw = dicts.decompress(path, target.read_bytes()) if target.exists() else original_raw
            actual = byml.read(raw)
            heart = next(a for a in actual["Actors"] if a["Hash"] == actor_id)
            assert heart["Gyaml"] == drops.NATIVE_ITEMS[item]
            heart["Gyaml"] = drops.HEART
            expected = byml.read(original_raw)
            patch_tree(expected, path, output.plan)
            assert byml.same(actual, expected), (path, actor_id)
