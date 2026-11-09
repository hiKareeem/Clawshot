import copy
from collections import Counter
from dataclasses import replace

import pytest

from clawshot.census.definitions import Definition
from clawshot.census.scan import Location
from clawshot.generate import Settings, generate, prepare
from clawshot.generate.fill import allowed
from clawshot.patch import drops
from clawshot.patch.plan import PatchError


def setup():
    vanilla = {"Heart A": "Heart Container", "Heart B": "Heart Container", "Sword": "Sword", "Junk": "Junk"}
    spec = {
        "start": "Root",
        "goal": "Sword",
        "settings": {"starting_age": "child"},
        "items": {
            "Heart Container": {"class": "normal"},
            "Sword": {"class": "progression"},
            "Junk": {"class": "normal"},
        },
        "regions": [{"name": "Root", "locations": {name: "True" for name in vanilla}}],
        "locations": {
            name: {"type": "BossHeart" if name.startswith("Heart") else "Chest", "vanilla": item}
            for name, item in vanilla.items()
        },
    }
    census = [
        Location(
            i,
            "heart_container",
            "Test",
            0,
            ("Banc/Test/Static.bcett.byml.zs",),
            "both",
            (0, 0, 0),
            drops.HEART,
            drops.HEART,
            None,
            True,
        )
        for i in (42, 43)
    ]
    definitions = [
        Definition(i, "heart_container", "Test", name, drops.HEART, name)
        for i, name in zip((42, 43), ("Heart A", "Heart B"), strict=True)
    ]
    return spec, census, definitions


def test_non_native_progression_and_normal_filler_cannot_leak_to_boss_hearts():
    spec, census, definitions = setup()
    before = copy.deepcopy(spec)
    settings = Settings(shuffle=("Chest", "BossHeart"), item_location_types={"Junk": ("Chest", "BossHeart")})
    _, world = prepare(spec, settings)
    effective, step = drops.seed_setup(world, settings, census, definitions, {})
    assert spec == before
    assert settings.item_location_types["Junk"] == ("BossHeart", "Chest")
    assert effective.location_type_items == {"BossHeart": tuple(sorted(drops.NATIVE_ITEMS))}
    for n in range(20):
        seed = generate(spec, n, effective, attempts=1)
        assert Counter(seed.placements.values()) == Counter(loc.vanilla for loc in world.locations.values())
        assert all(allowed(seed.world, effective, name, item) for name, item in seed.placements.items())
        assert {seed.placements[name] for name in ("Heart A", "Heart B")} <= drops.NATIVE_ITEMS.keys()
    assert step({"Heart A": "Heart Container", "Heart B": "Heart Container"}) == {}
    with pytest.raises(PatchError):
        step({"Heart A": "Sword", "Heart B": "Heart Container"})
    replay = Settings.from_string(effective.to_string())
    assert generate(spec, 7, replay).placements == generate(spec, 7, effective).placements


def test_missing_or_unsaved_heart_cannot_become_a_seed_check():
    spec, census, definitions = setup()
    settings = Settings(shuffle=("Chest", "BossHeart"))
    _, world = prepare(spec, settings)
    for bad_census in (census[:1], [replace(census[0], has_save_flag=False), census[1]]):
        with pytest.raises(PatchError):
            drops.seed_setup(world, settings, bad_census, definitions, {})
