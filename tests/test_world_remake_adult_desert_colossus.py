"""The Colossus token moved from the oasis tree to a cliff shared by both ages."""

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec


def test_cliff_token_needs_longshot_as_adult_or_boomerang_as_child():
    spec = load_spec()
    spec["start"] = "Desert Colossus"
    world = build_world(spec, {"gold_skulls_ignore_daytime": True})
    token = world.locations["Colossus GS Tree"]
    search = Search(world, ["Hookshot"])
    assert not search.can_access(token, ADULT)
    search.collect("Longshot")
    assert search.can_access(token, ADULT)
    assert not search.can_access(token, CHILD)
    search.collect("Boomerang")
    assert search.can_access(token, CHILD)


def test_fairy_wall_accepts_the_documented_hammer_and_existing_bombs():
    spec = load_spec()
    spec["start"] = "Desert Colossus"
    world = build_world(spec)
    target = "Colossus Great Fairy Fountain"
    assert not Search(world).can_reach(target, ADULT)
    assert Search(world, ["Megaton Hammer"]).can_reach(target, ADULT)
    bombs = Search(world, ["Bomb Bag"])
    assert not bombs.can_reach(target, ADULT)
    bombs.collect("Goron Bracelet")
    assert bombs.can_reach(target, ADULT)
