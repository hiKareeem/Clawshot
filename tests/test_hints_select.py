"""Hint selection (``clawshot.generate.hints``) on a small synthetic world with three real stone names."""

import pytest

from clawshot.generate import Seed, Settings, hints
from clawshot.world.load import build_world

STONES = {"KF Gossip Stone": "Start", "DMT Gossip Stone": "Cliff", "LH Lab Gossip Stone": "Lake"}


def chest(vanilla):
    return {"type": "Chest", "vanilla": vanilla}


def world(goal="Hookshot and Bow"):
    regions = [
        {
            "name": "Start",
            "hint": "KOKIRI_FOREST",
            "locations": {"Forest Chest": "True", "KF Gossip Stone": "True"},
            "exits": {"Hut": "True", "Cliff": "Hookshot", "Lake": "True", "Shed": "False"},
        },
        {"name": "Hut", "locations": {"Hut Chest": "True"}},
        {
            "name": "Cliff",
            "hint": "DEATH_MOUNTAIN_TRAIL",
            "locations": {"Cliff Chest": "True", "DMT Gossip Stone": "True"},
            "exits": {"Shed": "True"},
        },
        {"name": "Shed", "locations": {}},
        {"name": "Lake", "hint": "LAKE_HYLIA", "locations": {"Lake Chest": "True", "LH Lab Gossip Stone": "True"}},
    ]
    locations = {
        "Forest Chest": chest("Hookshot"),
        "Hut Chest": chest("Rupees (5)"),
        "Cliff Chest": chest("Bow"),
        "Lake Chest": chest("Rupees (5)"),
        **{name: {"type": "HintStone"} for name in STONES},
    }
    items = {"Hookshot": {}, "Bow": {}, "Mask of Truth": {}, "Rupees (5)": {"class": "normal"}}
    return build_world({"start": "Start", "goal": goal, "regions": regions, "locations": locations, "items": items})


def seed(number, placements=None):
    w = world()
    placements = placements or {name: loc.vanilla for name, loc in w.locations.items()}
    return Seed(w, number, Settings(), placements, list(w.locations), [list(placements)])


def test_area_of_a_region_without_one_comes_from_where_it_is_entered():
    w = world()
    assert hints.hint_area(w, "Hut") == "KOKIRI_FOREST"
    assert hints.hint_area(w, "Shed") == "DEATH_MOUNTAIN_TRAIL"  # the closed exit from Start is not followed


def test_required_locations_are_the_ones_the_goal_needs():
    assert hints.required_locations(seed(1)) == ["Forest Chest", "Cliff Chest"]


@pytest.mark.parametrize("distribution", ["balanced", "strong"])
def test_every_stone_gets_one_hint_and_none_needs_the_item_it_names(distribution):
    for number in range(30):
        chosen = hints.choose(seed(number), "always", distribution)
        assert [hint.stone for hint in chosen] == list(STONES)
        for hint in chosen:
            assert hint.label  # the stone's message label
            if hint.location == "Forest Chest":  # the Hookshot: the cliff stone needs it
                assert hint.stone != "DMT Gossip Stone", (number, hint)
            if hint.kind == "barren":
                assert hint.area == "LAKE_HYLIA"  # the other areas hold a required item
            if hint.kind == "woth":
                assert (hint.location, hint.area) in {
                    ("Forest Chest", "KOKIRI_FOREST"),
                    ("Cliff Chest", "DEATH_MOUNTAIN_TRAIL"),
                }


def test_the_same_seed_gives_the_same_hints_and_another_seed_may_not():
    assert hints.choose(seed(5)) == hints.choose(seed(5))
    assert len({hints.choose(seed(n)) for n in range(10)}) > 1


def test_with_the_mask_a_stone_is_read_only_by_child_holding_it():
    assert {hint.kind for hint in hints.choose(seed(3), "mask")} == {"junk"}  # no Mask of Truth anywhere
    with_mask = seed(3).placements | {"Hut Chest": "Mask of Truth"}
    for number in range(20):
        for hint in hints.choose(seed(number, with_mask), "mask"):
            assert hint.location != "Hut Chest"  # no stone is readable without the mask


def test_useless_gives_only_junk_and_unknown_choices_are_refused():
    assert {hint.kind for hint in hints.choose(seed(1), "always", "useless")} == {"junk"}
    with pytest.raises(hints.HintError, match="distribution"):
        hints.choose(seed(1), "always", "nonsense")
    with pytest.raises(hints.HintError, match="mode"):
        hints.choose(seed(1), "worn")


def test_text_fills_in_names():
    hint = hints.Hint(
        "KF Gossip Stone", "GOSSIP_KOKIRI_FOREST_01", "item", area="LAKE_HYLIA", location="Lake Chest", item="Bow"
    )
    assert hints.text(hint, item_name=str.upper) == "They say Lake Hylia hides the BOW."
    location = hints.Hint("KF Gossip Stone", "GOSSIP_KOKIRI_FOREST_01", "random", location="Lake Chest", item="Bow")
    assert hints.text(location, location_name=lambda name: "the lake chest") == "They say the lake chest holds the Bow."
