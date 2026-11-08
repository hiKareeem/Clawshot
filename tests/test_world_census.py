"""Every OoT Randomizer location of a type the census covers is a check of the remake (a census definition names
it through ``oot_randomizer_name``) or is marked N64-only in the world data, with the reason.

Scope (reviewer, round 2; whole world since round 3): the location types the census covers are checked one by one,
Gold Skulltulas included; types the census does not cover are skipped, by type. Locations neither linked nor
N64-only are *pending* (the census has not linked them yet): the test prints them, and fails if there are more than
``MAX_PENDING``, so a link lost is noticed and each link made lowers the bound.
"""

from collections import defaultdict

import pytest

from clawshot.census.definitions import load as load_definitions
from clawshot.world import load_world

# OoT Randomizer location type -> the census kinds that can be the same check.
COVERED = {
    "Chest": {"chest", "treasure_game_box", "treasure_game_reward"},
    "BossHeart": {"heart_container"},
    "Scrub": {"scrub"},
    "GrottoScrub": {"scrub"},
    "Shop": {"shop_slot"},
    "MaskShop": {"shop_slot"},
    "GS Token": {"gold_skulltula"},
    "Collectable": {"freestanding"},  # heart pieces and small keys
    # Event gifts (clawshot.census.gifts): a gift's kind follows its flow, not OoT Randomizer's type.
    "NPC": {"npc_gift", "event_gift"},
    "Song": {"song"},
    "Cutscene": {"event_gift"},
    "Boss": {"event_gift"},  # spiritual stones and medallions
}
# Not in the census: freestanding rupees and hearts, pots, crates, beehives, wonder items, rupee towers, silver
# rupees (N64 shuffles the census has no kind for).
SKIPPED = {
    "Freestanding",
    "Pot",
    "FlyingPot",
    "Crate",
    "SmallCrate",
    "Beehive",
    "Wonderitem",
    "RupeeTower",
    "SilverRupee",
}
# Covered locations with no census link and no n64_only reason, against main at the time of writing (round 3):
# lower it as the census links more.
MAX_PENDING = 237


@pytest.fixture(scope="module")
def world():
    return load_world({"progressive_items": True})  # OoT Randomizer's vanilla items, as LocationList has them


@pytest.fixture(scope="module")
def definitions():
    return load_definitions()


def _linked(definitions) -> dict[str, list]:
    linked: dict[str, list] = defaultdict(list)
    for d in definitions:
        if d.oot_randomizer_name:
            linked[d.oot_randomizer_name].append(d)
    return linked


def test_every_location_type_is_classified(world):
    unknown = sorted({loc.type for loc in world.locations.values()} - set(COVERED) - SKIPPED)
    assert not unknown, f"classify these OoT Randomizer location types in this test: {unknown}"


def test_links_match_kind_and_area(world, definitions):
    both, wrong = [], []
    for name, defs in _linked(definitions).items():
        location = world.locations[name]
        if location.n64_only is not None:
            both.append(name)
        kinds = COVERED.get(location.type, set())
        for d in defs:
            # A gift's area is empty where the placements name no single area that starts its flow.
            if d.kind not in kinds or (d.area or location.area) != location.area:
                wrong.append(f"{name}: census {d.id} is {d.kind} in {d.area}, expected {kinds} in {location.area}")
    assert not both, f"linked from the census and marked n64_only: {both}"
    assert not wrong, "\n".join(wrong)


def test_census_links_name_world_locations(world, definitions):
    assert sorted(set(_linked(definitions)) - set(world.locations)) == []


def test_covered_locations_are_remake_checks_or_n64_only(world, definitions):
    linked = _linked(definitions)
    pending: dict[str, list[str]] = defaultdict(list)
    for name, location in world.locations.items():
        if location.type in COVERED and name not in linked and location.n64_only is None:
            pending[location.area or "?"].append(f"{name} ({location.type})")
    count = sum(len(names) for names in pending.values())
    report = [f"{count} pending (no census link, not n64_only):"]
    for area in sorted(pending):
        report.append(f"  {area} ({len(pending[area])}): " + "; ".join(pending[area]))
    print("\n".join(report))
    assert count <= MAX_PENDING, "\n".join(report)
