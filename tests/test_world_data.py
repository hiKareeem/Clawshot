"""The ported world (OoT Randomizer's Kokiri Forest, Lost Woods and Deku Tree): it loads, its vanilla placement
is beatable, its rules say what OoT Randomizer's say, and its seeds are beatable and reproducible."""

import os
import subprocess
import sys

import pytest

from clawshot.generate import Settings, generate
from clawshot.generate.fill import check_beatable
from clawshot.world import ADULT, CHILD, load_spec, load_world, reachable


@pytest.fixture(scope="module")
def world():
    return load_world()


def test_vanilla_placement_is_beatable(world):
    placements = {name: loc.vanilla for name, loc in world.locations.items() if loc.vanilla is not None}
    spheres = check_beatable(world, placements)
    assert "Queen Gohma" in spheres[-1]


def test_forest_start(world):
    search = reachable(world)
    assert search.can_access(world.locations["KF Kokiri Sword Chest"], CHILD)
    assert not search.can_reach("KF Outside Deku Tree")  # Mido wants the sword and a shield
    assert search.regions(ADULT) == ["Root"]  # no Temple of Time in this port

    search = reachable(world, ["Kokiri Sword", "Buy Deku Shield"])
    assert search.holds("Showed Mido Sword & Shield")
    assert search.can_reach("Deku Tree Slingshot Room", CHILD)  # here(has_shield)
    assert not search.can_reach("LW Bridge From Forest")  # can_leave_forest: Gohma first


def test_open_forest_setting(world):
    open_world = load_world({"open_forest": "open"})
    search = reachable(open_world, ["Kokiri Sword"])
    assert search.can_reach("Deku Tree Lobby", CHILD)  # Mido steps aside
    assert not search.can_reach("Deku Tree Slingshot Room")  # still no shield
    assert search.can_reach("LW Bridge From Forest")  # can_leave_forest: open_forest != 'closed'


def test_deku_tree_needs_what_ootr_says(world):
    base = ["Kokiri Sword", "Buy Deku Shield"]
    gohma = world.locations["Deku Tree Queen Gohma Heart"]
    # Child reaches the boss only through the basement back room, which needs the Slingshot (or an adult's Bow);
    # sticks for the torches come from the Deku Babas the Kokiri Sword kills ('Deku Stick Drop').
    assert not reachable(world, base).can_access(gohma)
    search = reachable(world, [*base, "Slingshot"])
    assert search.holds("Deku Stick Drop")
    assert search.can_access(gohma)


@pytest.mark.parametrize("progressive", [False, True])
def test_seeds_are_beatable(progressive):
    spec = load_spec()
    logic = {"progressive_items": progressive}
    world = load_world(logic)
    for seed_number in range(100):
        seed = generate(spec, seed_number, Settings(logic=logic))
        check_beatable(world, seed.placements)


def test_fixed_items_are_the_default(world):
    # Saria gives the Fairy Ocarina, the target game a bigger bullet bag: one fixed item each (vanilla_fixed).
    assert world.locations["LW Gift from Saria"].vanilla == "Fairy Ocarina"
    assert world.locations["LW Target in Woods"].vanilla == "Bullet Bag (40)"
    assert not world.items["Bullet Bag (40)"].progression
    progressive = load_world({"progressive_items": True})
    assert progressive.locations["LW Gift from Saria"].vanilla == "Ocarina"


def test_spoiler_is_the_same_in_another_process():
    """No set or dict ordering leaks into the output: two interpreters with different hash seeds agree."""
    script = (
        "import sys; from clawshot.generate import Settings, generate, spoiler_json; "
        "from clawshot.world import load_spec; "
        "sys.stdout.write(spoiler_json(generate(load_spec(), 4242, Settings())))"
    )
    outputs = set()
    for hash_seed in ("1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": hash_seed}
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, env=env, check=True)
        outputs.add(result.stdout)
    assert len(outputs) == 1
    assert b'"seed": 4242' in outputs.pop()
