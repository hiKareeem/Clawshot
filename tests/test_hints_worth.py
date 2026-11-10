"""D29: all location-hint kinds share the worth-naming boundary, not the barren boundary."""

import random
from dataclasses import replace

import pytest

from clawshot.census.hints import stone_labels
from clawshot.generate import Seed, Settings, hints
from clawshot.world.load import build_world, load_world

WORTH = (
    "Hookshot",
    "Bow",
    "Bomb Bag",
    "Fairy Ocarina",
    "Song of Storms",
    "Adult Wallet",
    "Giant Wallet",
    "Piece of Heart",
    "Heart Container",
    "Piece of Heart (Out of Logic)",
    "Deku Nut Capacity",
    "Deku Stick Capacity",
    "Bullet Bag (40)",
    "Quiver (40)",
    "Bottle",
    "Rutos Letter",
    "Odd Potion",
)
JUNK = (
    "Rupee (1)",
    "Rupees (20)",
    "Bombs (5)",
    "Bombchus (5)",
    "Bombchus (10)",
    "Bombchus (20)",
    "Deku Nuts (5)",
    "Deku Stick (1)",
    "Arrows (10)",
    "Deku Seeds (30)",
    "Recovery Heart",
    "Magic Jar",
    "Scrub Business Seed",
    "Buy Fish",
    "Buy Bombchu (8)",
    "Buy Deku Shield",
    "Blue Potion",
    "Milk",
    "Bottle with Milk",
    "Bottle with Blue Fire",
    "Bottle with Big Poe",
    "Blue Fire",
    "Bombchu Drop",
    "Rupees",
    "Water Temple Clear",
)


@pytest.fixture(scope="module")
def item_data():
    return load_world().items


def make_seed(item_data, number, items=WORTH + JUNK):
    placements = {f"Check {i}": item for i, item in enumerate(items)}
    random.Random(number).shuffle(items := list(placements.values()))
    placements = dict(zip(placements, items, strict=True))
    stones = stone_labels()
    world = build_world(
        {
            "start": "Start",
            "goal": "True",
            "items": {name: {} for name in item_data},
            "regions": [
                {"name": "Start", "hint": "LAKE_HYLIA", "locations": {name: "True" for name in (*placements, *stones)}}
            ],
            "locations": {
                **{name: {"type": "Chest", "vanilla": item} for name, item in placements.items()},
                **{name: {"type": "HintStone"} for name in stones},
            },
        }
    )
    world.items = item_data
    world.start_items = ("Mask of Truth",)
    return Seed(world, number, Settings(), placements, list(placements), [list(placements)])


@pytest.mark.parametrize("kind", ["always", "sometimes", "random"])
@pytest.mark.parametrize("mode", ["always", "mask"])
def test_location_hints_never_name_junk_and_keep_hearts_and_upgrades(item_data, monkeypatch, kind, mode):
    data = hints.load()
    chosen_data = data | {
        "distributions": data["distributions"]
        | {
            "only": {"weights": {kind: 1} if kind != "always" else {}, "always": kind == "always"},
        },
    }
    monkeypatch.setattr(hints, "load", lambda: chosen_data)
    named = set()
    for number in range(50):
        seed = make_seed(item_data, number)
        chosen_data["lists"] = {"always": seed.shuffled, "sometimes": seed.shuffled}
        chosen = hints.choose(seed, mode, "only")
        for hint in chosen:
            if hint.item is not None:
                assert hint.kind == kind, (number, hint)
                assert hint.item in WORTH, (number, hint)
                assert seed.placements[hint.location] == hint.item
                named.add(hint.item)
    assert named == set(WORTH)


@pytest.mark.parametrize("mode", ["always", "mask"])
def test_item_hints_name_only_good_items_that_are_worth_naming(item_data, monkeypatch, mode):
    data = hints.load()
    monkeypatch.setattr(
        hints,
        "load",
        lambda: (
            data
            | {
                "distributions": data["distributions"] | {"only": {"weights": {"item": 1}, "always": False}},
            }
        ),
    )
    # Hearts and normal capacity upgrades are worth naming, but are not OoTR good-item hints.
    excluded = {
        "Piece of Heart",
        "Heart Container",
        "Piece of Heart (Out of Logic)",
        "Deku Nut Capacity",
        "Deku Stick Capacity",
        "Bullet Bag (40)",
        "Quiver (40)",
    }
    expected = set(WORTH) - excluded
    for number in range(50):
        seed = make_seed(item_data, number)
        chosen = hints.choose(seed, mode, "only")
        named = {hint.item for hint in chosen if hint.kind == "item"}
        assert named == expected, (number, named)


@pytest.mark.parametrize(
    "items,expected",
    [
        (("Piece of Heart", "Heart Container", "Deku Nut Capacity", "Deku Stick Capacity", "Bullet Bag (40)"), True),
        (("Buy Bombchu (8)", "Rupees (20)", "Bombchus (10)"), True),
        (("Adult Wallet",), False),
        (("Hookshot",), False),
    ],
)
def test_barren_eligibility_is_not_broadened_to_the_worth_naming_class(item_data, monkeypatch, items, expected):
    data = hints.load()
    monkeypatch.setattr(
        hints,
        "load",
        lambda: (
            data
            | {
                "distributions": data["distributions"] | {"only": {"weights": {"barren": 1}, "always": False}},
            }
        ),
    )
    for number in range(30):
        seed = make_seed(item_data, number, items)
        chosen = hints.choose(seed, "always", "only")
        assert any(h.kind == "barren" and h.area == "LAKE_HYLIA" for h in chosen) == expected


def test_required_goal_item_still_prevents_a_barren_hint(item_data, monkeypatch):
    data = hints.load()
    monkeypatch.setattr(
        hints,
        "load",
        lambda: (
            data
            | {
                "distributions": data["distributions"] | {"only": {"weights": {"barren": 1}, "always": False}},
            }
        ),
    )
    seed = make_seed(item_data, 0, ("Bombchus (10)",))
    # Ammo is not worth naming, but required-location analysis still prevents a false foolish hint.
    goal = build_world(
        {"start": "Goal", "goal": "Bombchus", "items": {"Bombchus": {}}, "regions": [{"name": "Goal"}]}
    ).goal
    seed.world.goal = goal
    seed.world.items = item_data | {"Bombchus (10)": replace(item_data["Bombchus (10)"], alias=("Bombchus", 1))}
    assert all(h.kind != "barren" for h in hints.choose(seed, "always", "only"))
