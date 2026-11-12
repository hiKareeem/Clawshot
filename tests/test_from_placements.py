"""Seeds from placements chosen elsewhere (another placer's fill, such as an Archipelago multiworld's). Synthetic
worlds from test_generate, and the repository's own logic data for the spoiler's opening route."""

import pytest
from test_generate import dungeon_world

from clawshot.generate import FillError, Settings, from_placements, generate, spoiler
from clawshot.generate.fill import shuffled_locations
from clawshot.world import build_world
from clawshot.world.load import load_spec

STAND_IN = "Stand-in"
"""An item a placer puts where it has no item of this world's to give (another player's, in a multiworld)."""


def _world_spec():
    spec = dungeon_world()
    spec["items"] = {**spec["items"], STAND_IN: {"class": "normal"}}
    return spec


def test_given_placements_fill_the_shuffled_locations_and_keep_the_rest_vanilla():
    spec = _world_spec()
    settings = Settings(shuffle=("Chest",), dungeon_items="anywhere")
    reference = generate(spec, 7, settings)
    placements = dict.fromkeys(reference.shuffled, STAND_IN)
    out = from_placements(spec, 7, settings, placements)
    assert out.shuffled == reference.shuffled
    assert all(out.placements[name] == STAND_IN for name in out.shuffled)
    assert {name: item for name, item in out.placements.items() if name not in out.shuffled} == {
        name: item for name, item in reference.placements.items() if name not in reference.shuffled
    }
    assert out.spheres == [] and out.hints == ()


def test_placements_that_do_not_fit_the_world_are_refused_by_name():
    spec = _world_spec()
    settings = Settings(shuffle=("Chest",))  # own_dungeon: the Temple's key may not leave the Temple
    world = build_world(spec)
    shuffled = shuffled_locations(world, settings)
    placements = dict.fromkeys(shuffled, STAND_IN)
    placements["Village Chest"] = "Small Key (Temple)"
    placements["Nowhere"] = "Sword"
    other = next(name for name in shuffled[:-1] if name != "Village Chest")
    placements[other] = "No Such Item"
    del placements[shuffled[-1]]
    with pytest.raises(FillError) as error:
        from_placements(spec, 1, settings, placements)
    text = str(error.value)
    assert "not a shuffled location: Nowhere" in text
    assert f"no item given for {shuffled[-1]}" in text
    assert "Village Chest: may not hold 'Small Key (Temple)'" in text
    assert f"{other}: unknown item 'No Such Item'" in text


def test_a_seed_from_given_placements_has_no_opening_route_instead_of_failing_the_spoiler():
    """The real world has the child opening milestone; with no spheres there is no witness to replay, and the
    spoiler's opening_route is null (as its contract allows) rather than "no child opening witness"."""
    spec = load_spec()
    settings = Settings(shuffle=("Chest",))
    world = build_world(spec)
    placements = {name: world.locations[name].vanilla for name in shuffled_locations(world, settings)}
    out = from_placements(spec, 1, settings, placements)
    assert all(out.placements[name] == item for name, item in placements.items())
    assert spoiler(out)["opening_route"] is None
