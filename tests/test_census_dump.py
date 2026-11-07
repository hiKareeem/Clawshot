import pytest

from clawshot.census import definitions, scan


@pytest.mark.dump
def test_definitions_agree_with_the_census(romfs):
    found = {loc.id: (loc.kind, loc.area, loc.vanilla_item) for loc in scan(romfs)}
    committed = {d.id: (d.kind, d.area, d.vanilla_item) for d in definitions.load()}
    assert sorted(set(found) - set(committed)) == [], "in the dump, not in locations.toml"
    assert sorted(set(committed) - set(found)) == [], "in locations.toml, not in the dump"
    differ = {i: (committed[i], found[i]) for i in found if committed[i] != found[i]}
    assert differ == {}
