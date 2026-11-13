"""Native river walls need broken rocks or the river-to-Domain arrival source.

Paired Longshot result and native seven-wall predicate: plans/03-game-data.md section 48.
"""

import pytest

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec

SOURCE = "Zora River Domain Arrival"


@pytest.fixture(scope="module")
def worlds():
    spec = load_spec()
    return {
        start: build_world({**spec, "start": start})
        for start in ("ZR Front", "Lost Woods", "ZR Behind Waterfall", "Zoras Domain")
    }


@pytest.mark.parametrize("items", [(), ("Ocarina of Time", "Zeldas Lullaby"), ("Bomb Bag",)])
def test_early_adult_cannot_walk_through_the_field_side_wall(worlds, items):
    search = Search.adult_after_pull(worlds["ZR Front"], items)
    assert not search.can_reach("Zora River", ADULT), {"items": items, "source": search.holds(SOURCE)}
    assert not search.can_access(worlds["ZR Front"].locations["ZR Open Grotto Chest"], ADULT)
    assert not search.holds(SOURCE)


@pytest.mark.parametrize(
    "age,items",
    [
        (CHILD, ("Bomb Bag", "Goron Bracelet")),
        (ADULT, ("Bomb Bag", "Silver Gauntlets")),
        (ADULT, ("Megaton Hammer",)),
    ],
)
def test_rock_breaking_tools_open_the_route_before_the_domain_source(worlds, age, items):
    constructor = Search.child_only if age == CHILD else Search.adult_after_pull
    search = constructor(worlds["ZR Front"], items)
    assert search.can_reach("Zora River", age), {"age": age, "items": items}
    assert not search.holds(SOURCE)  # no scale, warp or playable waterfall song reaches the source
    assert search.can_access(worlds["ZR Front"].locations["ZR Open Grotto Chest"], age)


def test_child_cannot_use_a_remote_hammer_to_break_the_entrance_rocks(worlds):
    search = Search.child_only(worlds["ZR Front"], ["Megaton Hammer"])
    assert not search.can_reach("Zora River", CHILD)
    assert not search.holds(SOURCE)


@pytest.mark.parametrize("age", [CHILD, ADULT])
def test_saved_domain_arrival_opens_the_entrance_without_explosives(worlds, age):
    constructor = Search.child_only if age == CHILD else Search.adult_after_pull
    search = constructor(worlds["ZR Front"], [SOURCE])
    assert search.can_reach("Zora River", age), {"age": age, "source": search.holds(SOURCE)}
    assert search.can_access(worlds["ZR Front"].locations["ZR Open Grotto Chest"], age)


def test_lost_woods_dive_still_reaches_river_without_clearing_the_domain_source(worlds):
    search = Search.adult_after_pull(worlds["Lost Woods"], ["Silver Scale"])
    assert search.can_reach("Zora River", ADULT)
    assert search.can_access(worlds["Lost Woods"].locations["ZR Open Grotto Chest"], ADULT)
    assert not search.holds(SOURCE)


def test_alternate_entry_can_execute_the_native_arrival_without_explosives(worlds):
    search = Search.adult_after_pull(worlds["Lost Woods"], ["Silver Scale", "Ocarina of Time", "Zeldas Lullaby"])
    assert search.can_reach("Zoras Domain", ADULT)
    assert search.holds(SOURCE), {"domain": search.can_reach("Zoras Domain", ADULT)}


@pytest.mark.parametrize("age", [CHILD, ADULT])
def test_domain_arrival_source_is_available_to_both_native_age_variants(worlds, age):
    constructor = Search.child_only if age == CHILD else Search.adult_after_pull
    search = constructor(worlds["ZR Behind Waterfall"])
    assert search.can_reach("Zoras Domain", age)
    assert search.holds(SOURCE), {"age": age, "domain": search.can_reach("Zoras Domain", age)}


def test_reverse_domain_route_is_not_blanket_gated_by_explosives(worlds):
    search = Search.adult_after_pull(worlds["Zoras Domain"])
    assert search.can_reach("Zora River", ADULT)
    assert search.holds(SOURCE)
