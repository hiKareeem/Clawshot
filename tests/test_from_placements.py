"""Seeds from placements chosen elsewhere (an Archipelago slot), on test_generate's synthetic dungeon world."""

import pytest

from clawshot.ap import FOREIGN_ITEM, load_slot, received_flags
from clawshot.generate import FillError, Settings, from_placements, generate
from clawshot.generate.fill import shuffled_locations
from clawshot.world import build_world
from tests.test_generate import dungeon_world


def _world_spec():
    spec = dungeon_world()
    spec["items"] = {**spec["items"], FOREIGN_ITEM: {"class": "normal"}}
    return spec


def test_given_placements_fill_the_shuffled_locations_and_keep_the_rest_vanilla():
    spec = _world_spec()
    settings = Settings(shuffle=("Chest",), dungeon_items="anywhere")
    reference = generate(spec, 7, settings)
    placements = dict.fromkeys(reference.shuffled, FOREIGN_ITEM)
    out = from_placements(spec, 7, settings, placements)
    assert out.shuffled == reference.shuffled
    assert all(out.placements[name] == FOREIGN_ITEM for name in out.shuffled)
    assert out.spheres == [] and out.hints == ()
    from clawshot.generate.route import opening

    assert opening(out) is None  # no spheres: the opening witness is absent, not an error


def test_placements_that_do_not_fit_the_world_are_refused_by_name():
    spec = _world_spec()
    settings = Settings(shuffle=("Chest",))  # own_dungeon: the Temple's key may not leave the Temple
    world = build_world(spec)
    shuffled = shuffled_locations(world, settings)
    placements = dict.fromkeys(shuffled, FOREIGN_ITEM)
    placements["Village Chest"] = "Small Key (Temple)"
    placements["Nowhere"] = "Sword"
    del placements[shuffled[-1]]
    with pytest.raises(FillError) as error:
        from_placements(spec, 1, settings, placements)
    text = str(error.value)
    assert "not a shuffled location: Nowhere" in text
    assert f"no item given for {shuffled[-1]}" in text
    assert "Village Chest: may not hold 'Small Key (Temple)'" in text


def test_slot_files_are_checked():
    assert len(received_flags()) == 16 and received_flags()[0] == "Archipelago.ReceivedIndex.Bit00"
    with pytest.raises(ValueError, match="format"):
        load_slot({"format": 99})
    seed, settings, placements = load_slot({"format": 1, "seed": 3, "settings": {"forest": "open"}, "placements": {}})
    assert (seed, settings.forest, placements) == (3, "open", {})
