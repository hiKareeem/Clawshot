"""Remake-only checks enter the same reachability graph as translated checks."""

import copy

import pytest

from clawshot.world.load import WorldError, apply_overrides, build_world
from clawshot.world.search import Search


def spec():
    return {
        "start": "Village",
        "goal": "Prize",
        "items": {"Bomb Bag": {}, "Prize": {}},
        "regions": [{"name": "Village", "area": "Village", "locations": {}}],
        "locations": {},
    }


def extra(**changes):
    return {
        "locations": {
            "Village Hidden Chest": {
                "new": True,
                "region": "Village",
                "rule": "Bomb_Bag",
                "type": "Chest",
                "vanilla": "Prize",
                "source": "synthetic bomb wall",
                **changes,
            }
        }
    }


def test_new_chest_obeys_its_requirement():
    data = spec()
    apply_overrides(data, [("extra_village.toml", extra())])
    world = build_world(data)
    search = Search(world)
    assert "Village Hidden Chest" not in search.locations()
    search.collect("Bomb Bag")
    assert "Village Hidden Chest" in search.locations()


@pytest.mark.parametrize("change", [{"was": "True"}, {"region": "Absent"}])
def test_invalid_addition_is_refused(change):
    with pytest.raises(WorldError):
        apply_overrides(spec(), [("extra.toml", extra(**change))])


def test_addition_cannot_replace_an_existing_check():
    data = spec()
    apply_overrides(data, [("extra.toml", extra())])
    with pytest.raises(WorldError, match="world has it already"):
        apply_overrides(copy.deepcopy(data), [("extra.toml", extra())])
