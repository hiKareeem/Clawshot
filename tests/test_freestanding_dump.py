import pytest

from clawshot.census import definitions
from clawshot.census.scan import GAME_DATA_LIST, read_romfs_byml, scan
from clawshot.formats import byml, zsdic
from clawshot.generate import Settings
from clawshot.patch import freestanding, make_seed, write_seed
from clawshot.patch.write import patch_tree
from clawshot.world.search import Search


@pytest.mark.dump
def test_all_anchored_floor_hearts_keep_permanent_identity_and_only_gyaml_changes(romfs):
    census = scan(romfs)
    hearts = [loc for loc in census if loc.kind == "freestanding" and loc.actor in freestanding.HEART_PIECES]
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    gd = read_romfs_byml(romfs, dicts, GAME_DATA_LIST)
    flags = {int(entry["Hash"]): entry for entry in gd["Data"]["Bool64bitKey"]}
    paths = {path for loc in hearts for path in loc.files}
    anchors = set()
    linked = set()
    for path in sorted(paths):
        tree = read_romfs_byml(romfs, dicts, path)
        for actor in tree["Actors"]:
            if actor["Gyaml"] == "HeartPieceAnchor":
                targets = {ref["Dst"] for ref in actor.get("Links", [])} & {loc.id for loc in hearts}
                if targets:
                    anchors.add(actor["Hash"])
                    linked.update(targets)
    assert len(anchors) == 14
    assert linked == {loc.id for loc in hearts}
    for loc in hearts:
        assert flags[loc.id]["ResetTypeValue"] == 24
        assert flags[loc.id]["SaveFileIndex"] == 0
    transforms = freestanding.changes({loc.id: "Obj_Shield_Hylian" for loc in hearts}, census)
    for path, transform in transforms.items():
        raw = dicts.decompress(path, (romfs / path).read_bytes())
        before = byml.read(raw)
        after = byml.read(transform(raw))
        for loc in hearts:
            if path in loc.files:
                actor = next(a for a in after["Actors"] if a["Hash"] == loc.id)
                assert actor["Gyaml"] == "Obj_Shield_Hylian"
                actor["Gyaml"] = loc.actor
        assert byml.same(before, after), path
    print(f"{len(hearts)} saved floor hearts / {sum(len(loc.files) for loc in hearts)} copies: inverse diff passed")


@pytest.mark.dump
def test_freestanding_seed_uses_only_native_pickups_and_preserves_access_and_other_families(romfs, tmp_path):
    output = make_seed(
        romfs,
        14,
        Settings(shuffle=("Chest", "Freestanding"), cheap_deku_shield=False, hints="mask"),
    )
    seed = output.seed
    census = {loc.id: loc for loc in scan(romfs) if loc.actor in freestanding.HEART_PIECES}
    names = {d.id: d.oot_randomizer_name for d in definitions.load() if d.id in census}
    selected = {name for name in seed.shuffled if seed.world.locations[name].type == freestanding.SHUFFLE}
    assert selected == set(names.values())
    assert len(selected) == 14
    assert all(seed.placements[name] in freestanding.NATIVE_ITEMS for name in selected)
    assert all(
        loc.type != "Collectable" and not loc.keep_vanilla
        for name, loc in seed.world.locations.items()
        if name in seed.shuffled
    )
    search = Search(seed.world)
    search.collect_spheres(seed.placements)
    assert search.won()
    write_seed(output, romfs, tmp_path / "seed")
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    for path in sorted({p for loc in census.values() for p in loc.files}):
        raw = dicts.decompress(path, (romfs / path).read_bytes())
        expected = byml.read(raw)
        target = tmp_path / "seed" / "romfs" / path
        actual = byml.read(dicts.decompress(path, target.read_bytes())) if target.exists() else byml.read(raw)
        patch_tree(expected, path, output.plan)
        for actor_id, loc in census.items():
            if path not in loc.files:
                continue
            item = seed.placements[names[actor_id]]
            actor = next(a for a in actual["Actors"] if a["Hash"] == actor_id)
            assert actor["Gyaml"] == (loc.actor if item == "Piece of Heart" else freestanding.NATIVE_ITEMS[item])
            actor["Gyaml"] = loc.actor
        assert byml.same(actual, expected), path
