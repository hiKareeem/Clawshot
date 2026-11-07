"""The rule language on synthetic worlds: what each construct means, and what it refuses."""

import pytest

from clawshot.world import ADULT, CHILD, DAY, NIGHT, WorldError, build_world, reachable

HELPERS = {
    "is_child": "age == 'child'",
    "is_adult": "age == 'adult'",
    "is_starting_age": "age == starting_age",
    "Hookshot": "Progressive_Hookshot",
    "Longshot": "(Progressive_Hookshot, 2)",
    "can_use(item)": "(_is_adult_item(item) and is_adult and item) or (_is_child_item(item) and is_child and item)",
    "_is_adult_item(item)": "item == Bow or item == Hookshot",
    "_is_child_item(item)": "item == Slingshot",
}
ITEMS = {
    "Bow": {},
    "Slingshot": {},
    "Progressive Hookshot": {},
    "Bottle": {"bottle": True},
    "Rutos Letter": {},
    "Kokiri Emerald": {"type": "DungeonReward", "stone": True},
    "Goron Ruby": {"type": "DungeonReward", "stone": True},
    "Piece of Heart": {},
    "Heart Container": {"alias": ["Piece of Heart", 4]},
    "Time Travel": {"type": "Event"},
}
SETTINGS = {"starting_age": "child", "open_forest": "closed", "needed": 2, "shortcuts": ["Deku Tree"]}


def world(rule: str, *, settings: dict | None = None, flags: dict | None = None, helpers: dict | None = None):
    """Start -> Field (both ages: child by default, adult with Time Travel); one location with ``rule``."""
    return build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": ITEMS,
            "helpers": HELPERS | (helpers or {}),
            "settings": SETTINGS | (settings or {}),
            "tricks": {"logic_trick": False},
            "flags": {"ensure_tod_access": False} | (flags or {}),
            "regions": [
                {"name": "Root", "exits": {"Field": "is_starting_age or Time_Travel"}},
                {"name": "Field", "locations": {"Spot": {"rule": rule, "type": "Chest"}}},
            ],
        }
    )


def access(rule: str, items=(), age=None, **kw) -> bool:
    w = world(rule, **kw)
    return reachable(w, items).can_access(w.locations["Spot"], age)


def test_items_counts_and_aliases():
    assert not access("Bow")
    assert access("Bow", ["Bow"])
    assert access("'Progressive Hookshot'", ["Progressive Hookshot"])  # quoted name with spaces
    assert not access("Longshot", ["Progressive Hookshot"])
    assert access("Longshot", ["Progressive Hookshot"] * 2)
    assert access("(Rutos_Letter, needed)", ["Rutos Letter"] * 2)  # count from a setting
    assert not access("(Rutos_Letter, needed)", ["Rutos Letter"])


def test_age_and_helper_arguments():
    # can_use substitutes its argument into the helper's text and compares item names (OoT Randomizer).
    assert access("can_use(Slingshot)", ["Slingshot"], CHILD)
    assert not access("can_use(Bow)", ["Bow"], CHILD)
    assert not access("can_use(Bow)", ["Bow", "Time Travel"], CHILD)
    assert access("can_use(Bow)", ["Bow", "Time Travel"], ADULT)
    assert access("can_use(Hookshot)", ["Progressive Hookshot", "Time Travel"], ADULT)
    assert not access("can_use(Slingshot)", ["Slingshot", "Time Travel"], ADULT)


def test_settings_fold_at_build_time():
    w = world("open_forest == 'open' or 'Deku Tree' in shortcuts")
    assert w.locations["Spot"].rule.always
    w = world("open_forest == 'open' and Bow")
    assert w.locations["Spot"].rule.never
    w = world("open_forest == 'open' and Bow", settings={"open_forest": "open"})
    assert not w.locations["Spot"].rule.always and not w.locations["Spot"].rule.never


def test_a_branch_switched_off_is_not_compiled():
    # OoT Randomizer stops at the operand that decides an and/or, so a dead branch may name unsupported things.
    assert access("not logic_trick or has_all_notes_for_song(Bow)")
    with pytest.raises(WorldError, match="has_all_notes_for_song is not supported"):
        world("logic_trick or has_all_notes_for_song(Bow)")


def test_events_and_quoted_items():
    w = world("'Some Event' and 'Bow'")
    assert w.undefined_events == ["Some Event"]  # quoted names that are not items are events
    assert w.locations["Spot"].rule({"Some Event": 1, "Bow": 1}, CHILD, DAY)
    assert not w.locations["Spot"].rule({"Bow": 1}, CHILD, DAY)


def test_builtins():
    assert access("has_bottle", ["Bottle"])
    assert access("has_bottle", ["Rutos Letter"] * 2)  # a second letter counts as a bottle
    assert not access("has_bottle", ["Rutos Letter"])
    assert access("has_stones(2)", ["Kokiri Emerald", "Goron Ruby"])
    assert not access("has_stones(2)", ["Kokiri Emerald", "Kokiri Emerald"])  # distinct stones
    assert not access("has_hearts(4)", ["Piece of Heart"] * 3)
    assert access("has_hearts(4)", ["Heart Container"])  # alias: a container is four pieces
    assert access("has_soul(Keese)")


def test_time_of_day():
    # Without entrance shuffle OoT Randomizer assumes every time of day is reachable.
    assert world("at_night").locations["Spot"].rule.always
    rule = world("at_night", flags={"ensure_tod_access": True}).locations["Spot"].rule
    assert rule({}, CHILD, NIGHT) and not rule({}, CHILD, DAY)


@pytest.mark.parametrize(
    ("rule", "message"),
    [
        ("Bow and", "syntax error"),
        ("not_a_thing", "unknown name not_a_thing"),
        ("open_forest", "used as a condition"),
        ("age == 'teen'", "not an age"),
        ("loop", "refers to itself"),
        ("can_use(Bow, Slingshot)", "takes 1 argument"),
        ("Bow + 1", "unsupported expression"),
    ],
)
def test_errors_name_the_rule(rule, message):
    with pytest.raises(WorldError, match=message) as error:
        world(rule, helpers={"loop": "Bow and loop"})
    assert "location 'Spot'" in str(error.value)


def test_tricks_stay_off():
    spec_world = world("logic_trick")
    assert spec_world.locations["Spot"].rule.never
    with pytest.raises(WorldError, match="verified in the remake"):
        build_world(
            {
                "start": "Root",
                "goal": "True",
                "items": {},
                "tricks": {"logic_trick": False},
                "regions": [{"name": "Root"}],
            },
            {"logic_trick": True},
        )
