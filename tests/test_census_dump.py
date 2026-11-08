from collections import Counter

import pytest

from clawshot.census import definitions, scan
from clawshot.census.gifts import GIFT_KINDS, scan_gifts


@pytest.mark.dump
def test_definitions_agree_with_the_census(romfs):
    """Placement checks and event gifts alike: the same ids, kinds, areas and vanilla items."""
    found = {loc.id: (loc.kind, loc.area, loc.vanilla_item) for loc in scan(romfs)}
    gifts = scan_gifts(romfs)
    found |= {g.id: (g.kind, g.area, g.vanilla_item) for g in gifts}
    committed = {d.id: (d.kind, d.area, d.vanilla_item) for d in definitions.load()}
    assert sorted(set(found) - set(committed), key=str) == [], "in the dump, not in locations.toml"
    assert sorted(set(committed) - set(found), key=str) == [], "in locations.toml, not in the dump"
    differ = {i: (committed[i], found[i]) for i in found if committed[i] != found[i]}
    assert differ == {}
    print(f"{len(gifts)} gifts:", dict(Counter(g.kind for g in gifts)))
    assert {g.kind for g in gifts} == set(GIFT_KINDS)
