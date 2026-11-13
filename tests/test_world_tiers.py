"""Fixed logical tiers MAX-combine; native-slot order constraints exclude age-separated equipment.

Adult Silver -> Golden and scale ordering remain conservative placement policies. Synthetic worlds only.
"""

import random

import pytest

from clawshot.generate import FillError, Settings, generate
from clawshot.generate.fill import check_beatable, fill, tier_forbidden, tier_order_violations
from clawshot.world import ADULT, CHILD, Search, build_world

PROGRESSIVE = {
    "Progressive Strength Upgrade": ["Goron Bracelet", "Silver Gauntlets", "Golden Gauntlets"],
    "Progressive Scale": ["Silver Scale", "Golden Scale"],
    "Progressive Wallet": ["Adult Wallet", "Giant Wallet", "Tycoon Wallet"],
    "Progressive Hookshot": ["Hookshot", "Longshot"],
    "Ocarina": ["Fairy Ocarina", "Ocarina of Time"],
}
ITEMS = {
    **{name: {} for name in PROGRESSIVE},
    "Piece of Heart": {},
    "Heart Container": {"alias": ["Piece of Heart", 4]},
    "Magic Meter": {},
    "Dins Fire": {"alias": ["Magic Meter", 1]},
    "Lens of Truth": {"alias": ["Magic Meter", 1]},
    "Rupees (5)": {"class": "normal"},
}
STRENGTH = "Progressive Strength Upgrade"


def counts_after(*items: str) -> dict[str, int]:
    world = build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": ITEMS,
            "progressive": PROGRESSIVE,
            "settings": {"progressive_items": False},
            "regions": [{"name": "Root"}],
        }
    )
    search = Search(world)
    for item in items:
        search.collect(item)
    return search.counts


@pytest.mark.parametrize(
    ("items", "family", "level"),
    [
        (("Goron Bracelet", "Silver Gauntlets"), STRENGTH, 2),
        (("Silver Gauntlets", "Goron Bracelet"), STRENGTH, 2),
        (("Golden Gauntlets",), STRENGTH, 3),
        (("Goron Bracelet", "Silver Gauntlets", "Golden Gauntlets"), STRENGTH, 3),
        (("Fairy Ocarina", "Ocarina of Time"), "Ocarina", 2),
        (("Adult Wallet", "Giant Wallet"), "Progressive Wallet", 2),
        (("Adult Wallet", "Giant Wallet", "Tycoon Wallet"), "Progressive Wallet", 3),
        (("Silver Scale", "Golden Scale"), "Progressive Scale", 2),
        (("Hookshot", "Longshot"), "Progressive Hookshot", 2),
        # Genuine progressive copies still count one each; with fixed tiers the larger of the two counts.
        ((STRENGTH, STRENGTH), STRENGTH, 2),
        ((STRENGTH, "Silver Gauntlets"), STRENGTH, 2),
        ((STRENGTH, STRENGTH, STRENGTH, "Silver Gauntlets"), STRENGTH, 3),
    ],
)
def test_fixed_tiers_give_the_highest_tier_held(items, family, level):
    counts = counts_after(*items)
    assert counts[family] == level
    assert all(counts[item] == items.count(item) for item in items if item != family)


def test_additive_aliases_still_add():
    counts = counts_after("Heart Container", "Piece of Heart", "Dins Fire", "Lens of Truth")
    assert counts["Piece of Heart"] == 5
    assert counts["Magic Meter"] == 2  # magic availability from either spell, as before


def test_two_lower_tiers_do_not_satisfy_a_higher_tier_rule():
    world = build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": ITEMS,
            "progressive": PROGRESSIVE,
            "helpers": {"Golden_Gauntlets": "(Progressive_Strength_Upgrade, 3)"},
            "settings": {"progressive_items": False},
            "regions": [{"name": "Root", "locations": {"Pillar": {"rule": "Golden_Gauntlets", "type": "Chest"}}}],
        }
    )
    search = Search(world, ["Goron Bracelet", "Silver Gauntlets"])
    assert not search.can_access(world.locations["Pillar"])
    search.collect("Golden Gauntlets")
    assert search.can_access(world.locations["Pillar"])


def test_caps_and_raw_inventory_counts_keep_the_level_semantics():
    world = build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": ITEMS,
            "progressive": PROGRESSIVE,
            "settings": {"progressive_items": False},
            "regions": [{"name": "Root"}],
        }
    )
    capped = Search(world)
    capped._count_caps = {STRENGTH: 1}
    capped.collect("Silver Gauntlets")
    assert capped.counts[STRENGTH] == 1
    raw = Search(world)._inventory_search({STRENGTH: 2}, child=False)
    raw.collect("Goron Bracelet")
    assert raw.counts[STRENGTH] == 2
    raw.collect("Golden Gauntlets")
    assert raw.counts[STRENGTH] == 3


def gated_world(*, return_opens: bool):
    """Child takes the Bracelet; adult takes the Silver Gauntlets; the return opens only with ``return_opens``."""
    return build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": {**ITEMS, "Key": {}},
            "progressive": PROGRESSIVE,
            "settings": {
                "starting_age": "child",
                "progressive_items": False,
                "age_return_event": "Forest Clear",
                "age_return_region": "Temple",
            },
            "regions": [
                {"name": "Root", "exits": {"Field": "age == starting_age or 'Time Travel'"}},
                {
                    "name": "Field",
                    "exits": {"Temple": "True"},
                    "locations": {
                        "Child Gift": {"rule": "age == 'child'", "type": "Chest"},
                        "Adult Chest": {"rule": "age == 'adult' and Progressive_Strength_Upgrade", "type": "Chest"},
                        "Child Rock": {"rule": "age == 'child' and (Progressive_Strength_Upgrade, 2)", "type": "Chest"},
                    },
                    "events": {"Forest Clear": "age == 'adult' and " + ("True" if return_opens else "Key")},
                },
                {"name": "Temple", "events": {"Time Travel": "True"}},
            ],
        }
    )


def test_child_and_adult_views_each_hold_their_own_level():
    placements = {"Child Gift": "Goron Bracelet", "Adult Chest": "Silver Gauntlets", "Child Rock": "Rupees (5)"}
    closed = Search(gated_world(return_opens=False))
    closed.collect_spheres(placements)
    assert closed.counts[STRENGTH] == 2
    assert closed._child_counts[STRENGTH] == 1
    assert "Child Rock" not in closed.collected
    opened = Search(gated_world(return_opens=True))
    opened.collect_spheres(placements)
    assert opened._child_counts is opened.counts
    assert opened.counts[STRENGTH] == 2
    assert opened.can_access(opened.world.locations["Child Rock"], CHILD)
    assert opened.can_access(opened.world.locations["Adult Chest"], ADULT)


def chest(vanilla: str, rule: str = "True") -> dict:
    return {"rule": rule, "type": "Chest", "vanilla": vanilla}


def strength_spec(*, families=(STRENGTH,), bracelet_shuffled=True) -> dict:
    """The Bracelet waits in an open chest: a player may take it early, but need not. The Silver Gauntlets may go only
    behind the Bracelet's rock; the Golden Gauntlets only behind the Silver Gauntlets' boulder."""
    gift = (
        chest("Goron Bracelet") if bracelet_shuffled else {"rule": "True", "type": "NPC", "vanilla": "Goron Bracelet"}
    )
    return {
        "start": "Root",
        "goal": "'Win'",
        "items": ITEMS,
        "progressive": PROGRESSIVE,
        "settings": {
            "starting_age": "child",
            "progressive_items": False,
            "downgrade_tier_families": list(families),
            "downgrade_tier_exemptions": ["Goron Bracelet"],
        },
        "regions": [
            {
                "name": "Root",
                "locations": {
                    "Open A": chest("Rupees (5)"),
                    "Open B": chest("Rupees (5)"),
                    "Bracelet Gift": gift,
                    "Rock Chest": chest("Silver Gauntlets", "Progressive_Strength_Upgrade"),
                    "Boulder Chest": chest("Golden Gauntlets", "(Progressive_Strength_Upgrade, 2)"),
                },
                "events": {"Win": "(Progressive_Strength_Upgrade, 3)"},
            }
        ],
    }


def test_a_higher_tier_screen_forbids_every_spot_reachable_without_a_lower_tier():
    world = build_world(strength_spec())
    items = [loc.vanilla for loc in world.locations.values()]
    forbidden = tier_forbidden(world, items, {})
    # The child Bracelet is independent of adult gauntlets; only Silver -> Golden is constrained.
    assert "Silver Gauntlets" not in forbidden
    assert forbidden["Golden Gauntlets"] == {"Open A", "Open B", "Bracelet Gift", "Rock Chest"}
    assert tier_forbidden(build_world(strength_spec(families=())), items, {}) == {}


def test_the_fill_puts_each_higher_tier_behind_every_lower_tier():
    spec = strength_spec()
    for number in range(30):
        seed = generate(spec, number, Settings(shuffle=("Chest",)))
        assert seed.placements["Boulder Chest"] == "Golden Gauntlets", (number, seed.placements)
        assert tier_order_violations(seed.world, seed.placements) == []


BYPASS = {
    "Open A": "Golden Gauntlets",
    "Open B": "Rupees (5)",
    "Bracelet Gift": "Goron Bracelet",
    "Rock Chest": "Rupees (5)",
    "Boulder Chest": "Silver Gauntlets",
}


def test_skipping_the_lower_tier_replay_catches_an_optional_earlier_bypass():
    world = build_world(strength_spec())
    # Beatable, but Golden can be taken before the same-age Silver tier.
    assert check_beatable(world, BYPASS)
    violations = tier_order_violations(world, BYPASS)
    assert ("Silver Gauntlets", "Golden Gauntlets", "Open A") in violations
    safe = {**BYPASS, "Open A": "Silver Gauntlets", "Boulder Chest": "Golden Gauntlets"}
    assert tier_order_violations(world, safe) == []


def test_child_bracelet_is_not_a_required_predecessor_of_adult_gauntlets():
    world = build_world(strength_spec())
    silver_first = {
        **BYPASS,
        "Open A": "Silver Gauntlets",
        "Bracelet Gift": "Rupees (5)",
        "Rock Chest": "Goron Bracelet",
        "Boulder Chest": "Golden Gauntlets",
    }
    assert check_beatable(world, silver_first)
    assert tier_order_violations(world, silver_first) == []


def test_every_copy_of_the_lower_tier_is_withheld():
    world = build_world(strength_spec())
    two_silvers = {
        **BYPASS,
        "Open A": "Silver Gauntlets",
        "Open B": "Silver Gauntlets",
        "Boulder Chest": "Golden Gauntlets",
    }
    assert tier_order_violations(world, two_silvers) == []


def test_vanilla_tier_bypasses_are_rejected_when_nothing_is_shuffled():
    spec = strength_spec()
    for name, item in BYPASS.items():
        spec["regions"][0]["locations"][name].update(type="NPC", vanilla=item)
    with pytest.raises(FillError, match="tier order"):
        fill(build_world(spec), Settings(shuffle=("Chest",)), random.Random(1))


def test_a_fill_with_no_spot_behind_the_lower_tier_fails():
    spec = strength_spec()
    spec["regions"][0]["locations"]["Rock Chest"]["rule"] = "True"
    spec["regions"][0]["locations"]["Boulder Chest"]["rule"] = "True"
    spec["regions"][0]["events"]["Win"] = "True"
    with pytest.raises(FillError, match="Golden Gauntlets"):
        fill(build_world(spec), Settings(shuffle=("Chest",)), random.Random(1))


def test_fixed_rewards_are_collected_through_their_lower_tier_prerequisites():
    spec = {
        "start": "Root",
        "goal": "(Progressive_Scale, 2)",
        "items": {**ITEMS, "Key": {}},
        "progressive": PROGRESSIVE,
        "settings": {"progressive_items": False, "downgrade_tier_families": ["Progressive Scale"]},
        "regions": [
            {
                "name": "Root",
                "locations": {
                    "Diving": {"rule": "True", "type": "NPC", "vanilla": "Silver Scale"},
                    "Fixed Key": {"rule": "Progressive_Scale", "type": "NPC", "vanilla": "Key"},
                    "Early Chest": chest("Rupees (5)"),
                },
                "exits": {"Beyond Key": "Key"},
            },
            {"name": "Beyond Key", "locations": {"Higher Chest": chest("Golden Scale")}},
        ],
    }
    world = build_world(spec)
    forbidden = tier_forbidden(world, ["Golden Scale", "Rupees (5)"], {"Diving": "Silver Scale", "Fixed Key": "Key"})
    assert "Early Chest" in forbidden["Golden Scale"]
    assert "Higher Chest" not in forbidden["Golden Scale"]
    seed = generate(spec, 4, Settings(shuffle=("Chest",)), attempts=1)
    assert seed.placements["Higher Chest"] == "Golden Scale"
    assert tier_order_violations(seed.world, seed.placements) == []
