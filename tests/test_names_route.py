"""Opening notes need a sufficient route, not an intersection that loses alternatives."""

import pytest

from clawshot.generate import Settings, generate
from clawshot.generate.route import opening


def opening_world(*, child_shield=True):
    locations = {
        "Sword A": {"type": "NPC", "vanilla": "Sword"},
        "Sword B": {"type": "NPC", "vanilla": "Sword"},
        "Early Shelf": {"type": "Shop", "vanilla": "Hylian Shield"},
        "Optional": {"type": "NPC", "vanilla": "Coin"},
        "Adult Shortcut": {"type": "NPC", "vanilla": "Deku Shield"},
        "Inside Prize": {"type": "Chest", "vanilla": "Slingshot"},
    }
    later = {}
    if child_shield:
        locations["Later Shelf"] = {"type": "Shop", "vanilla": "Deku Shield"}
        later["Later Shelf"] = "True"
    return {
        "start": "Village",
        "goal": "'Defeat Queen Gohma'",
        "items": {item: {} for item in ("Sword", "Hylian Shield", "Deku Shield", "Slingshot", "Coin")},
        "locations": locations,
        "regions": [
            {
                "name": "Village",
                "locations": {"Sword A": "True", "Sword B": "True", "Early Shelf": "True", "Optional": "True"},
                "exits": {"After Gate": "Sword and 'Hylian Shield'", "Adult Corner": "age == 'adult'"},
            },
            {"name": "Adult Corner", "locations": {"Adult Shortcut": "True"}},
            {"name": "After Gate", "locations": later, "exits": {"Deku Tree Lobby": "True"}},
            {
                "name": "Deku Tree Lobby",
                "dungeon": "Deku Tree",
                "exits": {"Trap Room": "'Deku Shield'"},
            },
            {
                "name": "Trap Room",
                "dungeon": "Deku Tree",
                "locations": {"Inside Prize": "True"},
                "events": {"Defeat Queen Gohma": "Slingshot"},
            },
        ],
    }


def test_opening_keeps_one_alternative_and_every_needed_purchase_before_entry():
    seed = generate(opening_world(), 7, Settings(shuffle=()))
    route = opening(seed)
    steps = list(route.steps)
    collected = [step.location for step in steps if step.kind == "collect"]
    assert sum(name in collected for name in ("Sword A", "Sword B")) == 1
    assert "Optional" not in collected
    assert "Adult Shortcut" not in collected
    entry = next(i for i, step in enumerate(steps) if step.kind == "enter")
    purchase = next(i for i, step in enumerate(steps) if step.location == "Later Shelf")
    assert purchase < entry
    required_items = {seed.placements[source] for source in steps[purchase].requires}
    assert required_items == {"Sword", "Hylian Shield"}
    assert "Later Shelf" in steps[entry].requires
    inside = next(step for step in steps if step.location == "Inside Prize")
    assert "Later Shelf" in inside.requires


def test_adult_find_cannot_fake_a_child_opening_purchase():
    seed = generate(opening_world(child_shield=False), 7, Settings(shuffle=()))
    with pytest.raises(ValueError):
        opening(seed)
