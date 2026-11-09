"""Free travel must not award Prelude early or gate it on shuffled reward ownership."""

import pytest

from clawshot.world import ADULT, CHILD, build_world, load_spec


@pytest.mark.parametrize("free_travel", [False, True])
def test_prelude_needs_adult_forest_completion_not_medal_or_minuet(free_travel):
    spec = load_spec()
    spec["settings"]["free_time_travel"] = free_travel
    world = build_world(spec)
    rule = world.locations["Sheik at Temple"].rule
    for items in ({}, {"Forest Medallion": 1}, {"Minuet of Forest": 1}, {"Prelude of Light": 1}):
        assert not rule(items, ADULT, 3)
    clear = {"Defeat Phantom Ganon": 1}
    assert rule(clear, ADULT, 3)
    assert not rule(clear, CHILD, 3)
