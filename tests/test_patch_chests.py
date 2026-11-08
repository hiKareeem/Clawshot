"""Every actual chest has exactly one source-backed world identity, or a specific exclusion."""

from collections import Counter

from clawshot.census.definitions import load as load_definitions
from clawshot.generate import Settings
from clawshot.generate.fill import shuffled_locations
from clawshot.patch.items import load as load_items
from clawshot.world import load_world


def test_every_census_chest_is_a_location_or_explicitly_excluded():
    world = load_world()
    missing = []
    for definition in load_definitions():
        if definition.kind != "chest":
            continue
        name = definition.oot_randomizer_name or definition.name
        location = world.locations.get(name)
        if location is None:
            missing.append((definition.id, name))
            continue
        assert location.type == "Chest", name
        assert location.area == definition.area, name
        assert not location.n64_only, name
        assert location.source or location.override, name
        if location.keep_vanilla:
            assert location.rule.text == "False", (name, location.keep_vanilla)
    assert not missing, missing


def test_shuffled_chest_key_pool_has_no_phantom_keys():
    world = load_world()
    definitions = load_definitions()
    actors = load_items()
    actors.check(world.items)
    named = {}
    for definition in definitions:
        if definition.kind == "chest":
            named.setdefault(definition.oot_randomizer_name or definition.name, []).append(definition)
    pool = []
    for name in shuffled_locations(world, Settings()):
        assert name in named, name
        dungeon = world.regions[world.locations[name].region].dungeon
        copies = {d.vanilla_item for d in named[name]}
        assert len(copies) == 1, (name, copies)
        pool.append(actors.item(next(iter(copies)), dungeon, world.items))
    counts = Counter(pool)
    # Bottom of the Well and Shadow each have one additional *freestanding* key, kept vanilla.
    assert {name: count for name, count in counts.items() if name.startswith("Small Key (")} == {
        "Small Key (Forest Temple)": 5,
        "Small Key (Fire Temple)": 8,
        "Small Key (Water Temple)": 4,
        "Small Key (Spirit Temple)": 5,
        "Small Key (Shadow Temple)": 4,
        "Small Key (Bottom of the Well)": 1,
        "Small Key (Gerudo Training Ground)": 9,
        "Small Key (Ganons Castle)": 1,
    }
    assert counts["Boss Key (Ganons Castle)"] == 1
    assert counts["Scrub Business Seed"] > 0
