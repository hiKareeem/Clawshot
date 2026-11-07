"""Item 5: every OoT Randomizer location in the ported regions is a check of the remake (a census definition
names it through ``oot_randomizer_name``) or is marked N64-only in the world data, with the reason.

Scope (reviewer, round 2): OoT Randomizer location types the census covers are checked one by one; Gold
Skulltulas are checked by count per area (the remake moved them, so they are not linked one by one before round 3
places them from the remake's positions); types the census does not cover are skipped, by type.
"""

from collections import Counter

import pytest

from clawshot.census.definitions import load as load_definitions
from clawshot.world import load_world

# OoT Randomizer location type -> the census kinds that can be the same check.
COVERED = {
    "Chest": {"chest", "treasure_game_box"},
    "BossHeart": {"heart_container"},
    "Scrub": {"scrub"},
    "GrottoScrub": {"scrub"},
    "Shop": {"shop_slot"},
}
# Freestanding items the census covers: heart pieces and small keys (rupees and hearts it does not).
FREESTANDING_ITEMS = ("Piece of Heart", "Small Key")
GOLD_SKULLTULA = "GS Token"
# Not in the census: freestanding rupees and hearts, pots, beehives, wonder items, rupee towers (N64 shuffles the
# remake has no placement for), and NPC, cutscene, song and boss-reward gifts (event flows, round 3).
SKIPPED = {"Freestanding", "Pot", "Beehive", "Wonderitem", "RupeeTower", "NPC", "Cutscene", "Song", "Boss"}


@pytest.fixture(scope="module")
def world():
    return load_world({"progressive_items": True})  # OoT Randomizer's vanilla items, as LocationList has them


@pytest.fixture(scope="module")
def definitions():
    return load_definitions()


def _covered(location) -> bool:
    if location.type in COVERED:
        return True
    return location.type == "Freestanding" and (location.vanilla or "").startswith(FREESTANDING_ITEMS)


def test_every_ported_location_type_is_classified(world):
    known = set(COVERED) | SKIPPED | {GOLD_SKULLTULA}
    unknown = sorted({loc.type for loc in world.locations.values()} - known)
    assert not unknown, f"classify these OoT Randomizer location types in this test: {unknown}"


def test_covered_locations_are_remake_checks_or_n64_only(world, definitions):
    linked: dict[str, list] = {}
    for d in definitions:
        if d.oot_randomizer_name:
            linked.setdefault(d.oot_randomizer_name, []).append(d)
    missing, both, wrong = [], [], []
    for name, location in world.locations.items():
        if not _covered(location):
            continue
        region = world.regions[location.region]
        kinds = COVERED.get(location.type, {"freestanding"})
        if name in linked and location.n64_only is not None:
            both.append(name)
        elif name in linked:
            for d in linked[name]:
                if d.kind not in kinds or d.area != region.area:
                    wrong.append(f"{name}: census {d.id} is {d.kind} in {d.area}, expected {kinds} in {region.area}")
        elif location.n64_only is None:
            missing.append(f"{name} ({location.type}, {region.area})")
    assert not both, f"linked from the census and marked n64_only: {both}"
    assert not wrong, "\n".join(wrong)
    assert not missing, "no census link and no n64_only reason:\n" + "\n".join(missing)


def test_census_links_in_ported_areas_name_ported_locations(world, definitions):
    areas = {r.area for r in world.regions.values() if r.area}
    names = {d.oot_randomizer_name for d in definitions if d.area in areas and d.oot_randomizer_name}
    assert sorted(names - set(world.locations)) == []


def test_gold_skulltulas_match_by_count_per_area(world, definitions):
    areas = {r.area for r in world.regions.values() if r.area}
    ootr = Counter(world.regions[loc.region].area for loc in world.locations.values() if loc.type == GOLD_SKULLTULA)
    remake = Counter(d.area for d in definitions if d.kind == "gold_skulltula" and d.area in areas)
    assert ootr == remake
    assert sum(ootr.values()) == 10
