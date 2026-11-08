"""King Zora's thaw is not the Domain thaw; adult token collection needs reach."""

import pytest

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec


@pytest.mark.parametrize("start,target", [("Lake Hylia", "Zoras Domain"), ("Zoras Domain", "Lake Hylia")])
def test_adult_lake_shortcut_opens_after_water_clear(start, target):
    spec = load_spec()
    spec["start"] = start
    # Isolate the shortcut: walking Domain -> River -> Field -> Lake is always possible.
    source = next(region for region in spec["regions"] if region["name"] == start)
    source["exits"] = {target: source["exits"][target]}
    world = build_world(spec)
    search = Search(world, ["Silver Scale"])
    assert not search.can_reach(target, ADULT)
    assert search.can_reach(target, CHILD)
    search.collect("Water Temple Clear")
    assert search.can_reach(target, ADULT)


def test_blue_fire_does_not_unseal_adult_shop():
    spec = load_spec()
    spec["start"] = "Zoras Domain"
    world = build_world(spec)
    search = Search(world, ["Blue Fire"])
    assert not search.can_reach("ZD Shop", ADULT)
    assert search.can_reach("ZD Shop", CHILD)
    search.collect("Water Temple Clear")
    assert search.can_reach("ZD Shop", ADULT)


def test_domain_token_cannot_be_collected_with_just_magic_or_bow():
    spec = load_spec()
    spec["start"] = "Zoras Domain"
    world = build_world(spec)
    search = Search(world, ["Magic Meter", "Bow"])
    token = world.locations["ZD GS Frozen Waterfall"]
    assert not search.can_access(token, ADULT)
    search.collect("Hookshot")
    assert search.can_access(token, ADULT)
