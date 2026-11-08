"""Gossip Stones as hint locations in the world (round 7): the loader keeps them apart from the checks, and the
world's stones are exactly the census's 40, one message label each."""

import pytest

from clawshot.census.hints import STONE_LINKS, stone_labels
from clawshot.world.load import WorldError, apply_overrides, build_world, load_world
from clawshot.world.search import reachable


def stone_world(**stone):
    return {
        "start": "Root",
        "goal": "Sword",
        "regions": [
            {"name": "Root", "locations": {"Chest": "True"}, "exits": {"Ledge": "Sword"}},
            {"name": "Ledge", "locations": {"Stone": "True"}},
        ],
        "locations": {"Chest": {"type": "Chest", "vanilla": "Sword"}, "Stone": {"type": "HintStone", **stone}},
        "items": {"Sword": {}},
    }


def test_a_stone_is_a_hint_location_not_a_check():
    world = build_world(stone_world())
    assert list(world.locations) == ["Chest"]
    assert [location.name for location in world.regions["Ledge"].locations] == []
    stone = world.hint_stones["Stone"]
    assert (stone.region, stone.vanilla) == ("Ledge", None)
    assert not reachable(world).can_access(stone)
    assert reachable(world, ["Sword"]).can_access(stone)


def test_a_stone_holding_an_item_is_refused():
    with pytest.raises(WorldError, match="holds no item"):
        build_world(stone_world(vanilla="Sword"))


def test_a_new_stone_needs_no_vanilla_item_but_a_new_check_does():
    spec = stone_world()
    apply_overrides(
        spec,
        [
            (
                "new.toml",
                {
                    "locations": {
                        "Other Stone": {
                            "new": True,
                            "region": "Root",
                            "type": "HintStone",
                            "rule": "True",
                            "source": "test",
                        }
                    }
                },
            )
        ],
    )
    assert set(build_world(spec).hint_stones) == {"Stone", "Other Stone"}
    with pytest.raises(WorldError, match="new needs rule, region, type and vanilla"):
        apply_overrides(
            stone_world(),
            [
                (
                    "bad.toml",
                    {
                        "locations": {
                            "Other Chest": {
                                "new": True,
                                "region": "Root",
                                "type": "Chest",
                                "rule": "True",
                                "source": "test",
                            }
                        }
                    },
                )
            ],
        )


def test_one_world_stone_per_label():
    world = load_world()
    live = {name for name, stone in world.hint_stones.items() if stone.n64_only is None}
    labels = stone_labels()
    assert live == set(labels)
    assert len(labels) == len(set(labels.values())) == 40
    # every census entry is a world stone, apart from the Kokiri Forest files' copy of the Lost Woods bridge stone
    assert {label for (_, label) in STONE_LINKS} == set(labels.values())
    assert {name for name, stone in world.hint_stones.items() if stone.n64_only} == {
        "KF Storms Grotto Gossip Stone",
        "LW Near Shortcuts Grotto Gossip Stone",
        "HF Near Market Grotto Gossip Stone",
        "DMT Storms Grotto Gossip Stone",
    }
