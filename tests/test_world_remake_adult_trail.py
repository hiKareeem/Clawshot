"""The cavern-roof heart needs the adult bean route, never damage or Hover Boots."""

import pytest

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec


@pytest.mark.parametrize(
    "age,items,planted,damage,expected",
    [
        pytest.param(CHILD, [], False, "normal", False, id="child-cannot-damage-boost"),
        pytest.param(
            CHILD,
            ["Magic Bean"] * 10 + ["Goron Bracelet"],
            False,
            "normal",
            False,
            id="child-with-bean-plot-access-cannot-collect",
        ),
        pytest.param(ADULT, [], False, "normal", False, id="adult-cannot-damage-boost"),
        pytest.param(ADULT, ["Hover Boots"], False, "ohko", False, id="hover-boots-do-not-replace-bean"),
        pytest.param(ADULT, ["Magic Bean"] * 10, False, "ohko", False, id="beans-without-plot-access"),
        pytest.param(
            ADULT,
            ["Magic Bean"] * 9 + ["Goron Bracelet"],
            False,
            "ohko",
            False,
            id="plot-access-without-full-bean-stock",
        ),
        pytest.param(
            ADULT,
            ["Magic Bean"] * 10 + ["Goron Bracelet"],
            False,
            "ohko",
            True,
            id="child-can-plant-and-adult-can-ride",
        ),
        pytest.param(ADULT, [], True, "ohko", True, id="preplanted-bean-keeps-adult-route"),
        pytest.param(CHILD, [], True, "ohko", False, id="preplanted-bean-does-not-admit-child"),
    ],
)
def test_cavern_roof_heart_needs_the_adult_bean_route(age, items, planted, damage, expected):
    spec = load_spec()
    spec["start"] = "Death Mountain"
    spec["settings"].update(plant_beans=planted, damage_multiplier=damage)
    world = build_world(spec)
    search = Search(world, items)
    search.update()
    assert search.can_access(world.locations["DMT Freestanding PoH"], age) is expected
