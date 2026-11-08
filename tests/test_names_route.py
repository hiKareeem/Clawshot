"""Opening notes need a sufficient route, not an intersection that loses alternatives."""

import pytest

from clawshot.generate import Settings, generate, play_note, spoiler
from clawshot.generate.route import opening


def opening_world(*, child_shield=True, paid_shield="Later Shelf"):
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
        locations[paid_shield] = {"type": "Shop", "vanilla": "Deku Shield"}
        later[paid_shield] = "True"
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


def test_required_scrub_reward_is_a_priced_purchase_before_dungeon_entry():
    spec = opening_world()
    spec["locations"]["Later Shelf"]["type"] = "Scrub"
    spec["settings"] = {"scrub_sale_prices": {"Later Shelf": 40}}
    seed = generate(spec, 7, Settings(shuffle=()))
    log = spoiler(seed)
    steps = log["opening_route"]["steps"]
    purchase = next(step for step in steps if step["location"] == "Later Shelf")
    entry = next(step for step in steps if step["kind"] == "enter")
    assert purchase["price"] == 40
    assert {row["item"] for row in purchase["requires"]} == {"Sword", "Hylian Shield"}
    assert steps.index(purchase) < steps.index(entry)
    rows = play_note(seed, log).splitlines()
    purchase_row = next(row for row in rows if "| Later Shelf —" in row)
    assert "| Buy |" in purchase_row
    assert "| 40 rupees;" in purchase_row


def free_shield_world():
    spec = opening_world(paid_shield="KF Shop Item 6")
    spec["regions"][0]["exits"]["KF Kokiri Shop"] = "True"
    spec["regions"].append(
        {"name": "KF Kokiri Shop", "events": {"Deku Shield": "age == 'child' and at('After Gate', age == 'child')"}}
    )
    return spec


def test_free_event_is_an_explicit_required_visit_not_a_pool_check_or_purchase():
    seed = generate(free_shield_world(), 7, Settings(shuffle=()))
    log = spoiler(seed)
    steps = log["opening_route"]["steps"]
    free = next(step for step in steps if step["kind"] == "visit")
    entry = next(step for step in steps if step["kind"] == "enter")
    assert free["item"] == "Deku Shield" and free["price"] == 0
    assert free["not_equipped"] == "Deku Shield"  # Ownership is not the offer's exclusion.
    assert {item["item"] for item in free["requires"]} == {"Sword", "Hylian Shield"}
    assert steps.index(free) < steps.index(entry)
    assert "Deku Shield" in {item["item"] for item in entry["requires"]}
    assert not any(step["kind"] == "collect" and step["item"] == "Deku Shield" for step in steps)
    assert [alt["location"] for alt in free["alternatives"]] == ["KF Shop Item 6"]
    assert free["alternatives"][0]["price"] == 10
    assert free["location"] not in seed.placements and free["location"] not in seed.world.locations
    assert any(event.name == "Deku Shield" for event in seed.world.events)
    purchase = free["alternatives"][0]
    assert {item["item"] for item in purchase["requires"]} == {"Sword", "Hylian Shield"}
    for index, step in enumerate(steps):
        prior = {earlier["location"] for earlier in steps[:index] if earlier["kind"] in ("collect", "visit")}
        for option in (step, *step["alternatives"]):
            assert all(set(item["sources"]) <= prior for item in option["requires"]), option
    note = play_note(seed, log)
    rows = [line for line in note.splitlines() if line.startswith("| ")]
    entry_row = next(line for line in rows if "| Enter |" in line)
    visit_row = next(line for line in rows if f"[{free['location']}]" in line)
    alternative_row = next(line for line in rows if f"[{purchase['location']}]" in line)
    assert note.index(visit_row) < note.index(alternative_row) < note.index(entry_row)


def test_free_shield_cannot_replace_the_initial_shield_needed_to_pass_mido():
    spec = free_shield_world()
    spec["locations"]["Early Shelf"]["vanilla"] = "Deku Shield"
    spec["regions"][0]["exits"]["After Gate"] = "Sword and 'Deku Shield'"
    seed = generate(spec, 7, Settings(shuffle=()))
    steps = spoiler(seed)["opening_route"]["steps"]
    assert not any(step["kind"] == "visit" for step in steps)
    first_shield = next(step for step in steps if step["item"] == "Deku Shield")
    assert first_shield["location"] == "Early Shelf"
