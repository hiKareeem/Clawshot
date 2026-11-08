"""Fast-start logic changes only the blocker whose gameplay flag the seed patches."""

import pytest

from clawshot.generate import FillError, Settings, prepare
from clawshot.world import CHILD, Search, load_spec


def test_mido_skip_opens_deku_path_but_not_the_forest_exit():
    _, world = prepare(load_spec(), Settings(fast_start=("intro", "mido")))
    search = Search(world)
    assert search.can_reach("KF Outside Deku Tree", CHILD)
    assert not search.can_reach("LW Bridge From Forest", CHILD)
    search.collect("Defeat Queen Gohma")
    assert search.can_reach("LW Bridge From Forest", CHILD)


@pytest.mark.parametrize("shield", ["Buy Deku Shield", "Buy Hylian Shield"])
def test_kept_mido_still_needs_sword_and_either_shield(shield):
    _, world = prepare(load_spec(), Settings(fast_start=()))
    search = Search(world, ["Kokiri Sword"])
    assert not search.can_reach("KF Outside Deku Tree", CHILD)
    search.collect(shield)
    assert search.can_reach("KF Outside Deku Tree", CHILD)
    assert not search.can_reach("LW Bridge From Forest", CHILD)


@pytest.mark.parametrize("shield,helper", [("Deku Shield", "Deku_Shield"), ("Hylian Shield", "Hylian_Shield")])
def test_chest_found_shield_satisfies_helper_and_kept_mido(shield, helper):
    spec = load_spec()
    spec["goal"] = helper
    _, world = prepare(spec, Settings(fast_start=()))
    search = Search(world, ["Kokiri Sword"])
    assert not search.won()
    assert not search.can_reach("KF Outside Deku Tree", CHILD)
    chest = "KF Midos Top Left Chest"
    search.collect_spheres({chest: shield})
    assert chest in search.collected
    assert search.won()
    assert search.can_reach("KF Outside Deku Tree", CHILD)
    assert not search.can_reach("LW Bridge From Forest", CHILD)


@pytest.mark.parametrize("skips,logic", [((), True), (("mido",), False)])
def test_mido_logic_cannot_diverge_from_the_patched_setting(skips, logic):
    with pytest.raises(FillError, match="must agree"):
        prepare(load_spec(), Settings(fast_start=skips, logic={"skip_mido": logic}))
