"""D30: capacity alone is not usable bombs; lift strength is age-specific."""

from copy import deepcopy

import pytest

from clawshot.world import ADULT, CHILD, Search, WorldError, build_world, load_spec
from clawshot.world.load import apply_overrides

BOMB_ROUTES = {
    "Wall": "Bombs",
    "Explosive wall": "has_explosives",
    "Breakable rock": "can_blast_or_smash",
    "Use bombs": "can_use(Bombs)",
    "Octorok": "can_kill_octorok_with_bombs",
    "Octorok or magic": "can_kill_octorok_with_bombs_or_magic",
}


def bomb_world(*, progressive=False):
    # Synthetic rooms use the shipped helpers/items, without unrelated vanilla drops or events.
    spec = load_spec()
    spec.update(
        start="Start",
        goal="True",
        regions=[
            {
                "name": "Start",
                "locations": {"Open": "True", **BOMB_ROUTES, "Bomb jump": "can_groundjump"},
                "exits": {"Blocked": "Bombs"},
            },
            {"name": "Blocked"},
        ],
        locations={name: {"type": "Chest"} for name in ("Open", *BOMB_ROUTES, "Bomb jump")},
    )
    # Test the bomb-only branch of this synthetic trick; no real-world trick is enabled.
    spec["tricks"].pop("glitch_groundjump")
    spec["settings"] = {**spec["settings"], "glitch_groundjump": True, "progressive_items": progressive}
    return build_world(spec)


@pytest.mark.parametrize("age", [CHILD, ADULT])
def test_bag_without_strength_reaches_nothing_new(age):
    world = bomb_world()
    without = Search(world)
    bag_only = Search(world, ["Bomb Bag"])
    assert without.locations(age) == ["Open"]
    assert bag_only.locations(age) == ["Open"]
    assert not bag_only.can_reach("Blocked", age)


@pytest.mark.parametrize(
    ("strength", "child", "adult"),
    [("Goron Bracelet", True, True), ("Silver Gauntlets", False, True), ("Golden Gauntlets", False, True)],
)
def test_fixed_strength_respects_age_and_wakes_blocked_routes(strength, child, adult):
    world = bomb_world()
    search = Search(world, ["Bomb Bag"])
    assert search.locations() == ["Open"]
    search.collect(strength)
    for age, expected in [(CHILD, child), (ADULT, adult)]:
        assert search.can_reach("Blocked", age) is expected
        for name in BOMB_ROUTES:
            assert search.can_access(world.locations[name], age) is expected, (name, age, strength)
    no_bag = Search(world, [strength])
    assert not no_bag.can_reach("Blocked")


def test_progressive_strength_first_tier_is_the_bracelet():
    world = bomb_world(progressive=True)
    search = Search(world, ["Bomb Bag"])
    assert not search.can_reach("Blocked")
    search.collect("Progressive Strength Upgrade")
    assert search.can_reach("Blocked", CHILD)
    assert search.can_reach("Blocked", ADULT)


@pytest.mark.parametrize("age", [CHILD, ADULT])
def test_bomb_only_trick_keeps_its_lift_requirement(age):
    world = bomb_world()
    search = Search(world, ["Bomb Bag", "Deku Shield", "Hylian Shield"])
    jump = world.locations["Bomb jump"]
    assert not search.can_access(jump, age)
    search.collect("Goron Bracelet")
    assert search.can_access(jump, age)


@pytest.mark.parametrize("age", [CHILD, ADULT])
def test_bombchus_and_hammer_do_not_inherit_the_bomb_lift_gate(age):
    spec = load_spec()
    rules = {
        "Bomb-only wall": "Bombs",
        "Explosive wall": "has_explosives",
        "Rock": "can_blast_or_smash",
        "Flower": "can_kill_beamos_with_bomb_flower",
    }
    spec.update(
        start="Room",
        goal="True",
        regions=[{"name": "Room", "locations": rules}],
        locations={name: {"type": "Chest"} for name in rules},
    )
    world = build_world(spec)
    chus = Search(world, ["Bombchus (5)"])
    assert not chus.can_access(world.locations["Bomb-only wall"], age)
    assert chus.can_access(world.locations["Explosive wall"], age)
    assert chus.can_access(world.locations["Rock"], age)
    hammer = Search(world, ["Megaton Hammer"])
    assert hammer.can_access(world.locations["Rock"], age) is (age == ADULT)
    assert not hammer.can_access(world.locations["Explosive wall"], age)
    flower = Search(world)
    assert not flower.can_access(world.locations["Flower"], age)
    flower.collect("Goron Bracelet")
    assert flower.can_access(world.locations["Flower"], age)
    assert not flower.can_access(world.locations["Bomb-only wall"], age)


def test_helper_override_preserves_parameter_substitution():
    spec = {
        "start": "Room",
        "goal": "True",
        "items": {"Bag": {}, "Lift": {}},
        "helpers": {"use(item)": "item"},
        "regions": [{"name": "Room", "locations": {"Wall": "use(Bag)"}}],
        "locations": {"Wall": {"type": "Chest"}},
    }
    apply_overrides(
        spec,
        [
            (
                "remake",
                {
                    "helpers": {
                        "use(item)": {
                            "rule": "item and Lift",
                            "was": "item",
                            "source": "synthetic",
                        }
                    }
                },
            )
        ],
    )
    world = build_world(spec)
    search = Search(world, ["Bag"])
    assert not search.can_access(world.locations["Wall"])
    search.collect("Lift")
    assert search.can_access(world.locations["Wall"])


@pytest.mark.parametrize(
    "entry",
    [
        {"rule": "True", "source": "s"},
        {"was": "False", "source": "s"},
        {"rule": "True", "was": "False"},
        {"rule": "True", "was": "stale", "source": "s"},
        {"rule": "True", "was": "False", "source": "s", "new": True},
    ],
)
def test_invalid_helper_override_is_refused(entry):
    spec = {"regions": [], "locations": {}, "helpers": {"Bombs": "False"}}
    with pytest.raises(WorldError):
        apply_overrides(spec, [("remake", {"helpers": {"Bombs": entry}})])


def test_unknown_or_multiply_owned_helper_is_refused():
    spec = {"regions": [], "locations": {}, "helpers": {"Bombs": "False"}}
    entry = {"rule": "True", "was": "False", "source": "synthetic"}
    with pytest.raises(WorldError):
        apply_overrides(deepcopy(spec), [("a", {"helpers": {"Absent": entry}})])
    with pytest.raises(WorldError):
        apply_overrides(spec, [("a", {"helpers": {"Bombs": entry}}), ("b", {"helpers": {"Bombs": entry}})])
