"""The documented remake Light Arrows route awakens all five adult sages."""

from clawshot.world import ADULT, Search, build_world, load_spec


def test_light_arrows_wait_for_all_five_adult_sages():
    spec = load_spec()
    spec["start"] = "Temple of Time"
    world = build_world(spec)
    search = Search(world, ["Shadow Medallion", "Spirit Medallion"])
    gift = world.locations["ToT Light Arrows Cutscene"]
    assert not search.can_access(gift, ADULT)
    search.collect("Forest Medallion")
    search.collect("Fire Medallion")
    assert not search.can_access(gift, ADULT)
    search.collect("Water Medallion")
    assert search.can_access(gift, ADULT)
