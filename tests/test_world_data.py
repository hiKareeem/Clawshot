"""The ported world (all of OoT Randomizer's overworld and vanilla dungeons, with the remake's overrides): it loads,
its vanilla placement is beatable, its rules say what OoT Randomizer's and the remake's say, and seeds with the
default settings are beatable and reproducible."""

import os
import subprocess
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor

import pytest

from clawshot.generate import FillError, Settings, generate
from clawshot.generate.fill import check_beatable
from clawshot.world import ADULT, CHILD, DATA_DIR, Search, load_spec, load_world, reachable

SEEDS = 200


@pytest.fixture(scope="module")
def world():
    return load_world()


def test_the_whole_world_is_ported(world):
    assert world.dangling_exits == []  # every exit leads to a ported region
    assert world.undefined_events == []
    assert world.missing_regions == []
    # The translated regions; the remake's overrides may add more (rooms OoT Randomizer folds together).
    with (DATA_DIR / "world.toml").open("rb") as f:
        files = tomllib.load(f)["files"]
    translated = []
    for file in files:
        with (DATA_DIR / file).open("rb") as f:
            translated.extend(region["name"] for region in tomllib.load(f)["region"])
    assert set(translated) <= world.regions.keys()


def vanilla_placements(world) -> dict[str, str]:
    return {n: loc.vanilla for n, loc in world.locations.items() if loc.vanilla is not None and loc.n64_only is None}


def test_vanilla_placement_is_beatable(world):
    """OoT Randomizer counts a dungeon's small keys for the worst order of its locked doors, so its own vanilla key
    layout is not provably enough (the Spirit Temple's Silver Gauntlets chest asks for 5 keys; the child side has
    2). Key logic is what seeds test below; here every other item lies where the game puts it, and each dungeon's
    small keys are held from the start."""
    placements = vanilla_placements(world)
    keys = [item for item in placements.values() if world.items[item].type == "SmallKey"]
    search = Search(world, keys)
    search.collect_spheres(placements)
    assert search.won()
    assert search.holds("Time Travel") and search.can_reach("Ganondorf Boss Room", ADULT)
    # Only the twenty explicitly documented, unreachable keep-vanilla checks are exempt. D17's reachable
    # Treasure Chest Game boxes/reward are not exempt; neither is any shuffled or merely unreachable chest.
    excluded = {n for n, loc in world.locations.items() if loc.keep_vanilla and loc.rule.test is False}
    assert excluded == {
        "Bottom Of The Well Room 11 Chest (Item_ScrubBusinessSeed)",
        "Gerudo Fortress Chest (TBox_Rupee_Red)",
        "Gerudo Valley Chest (Item_ScrubBusinessSeed)",
        "Gerudo Valley Chest (TBox_Rupee_Green)",
        "Gerudo Valley Chest (TBox_Rupee_Red) [Adult]",
        "Gerudo Valley Chest (TBox_Rupee_Red) [Child]",
        "Goron City Chest (TBox_Rupee_Green)",
        "Goron City Chest (TBox_Rupee_Purple) #2",
        "Graveyard Chest (TBox_Rupee_Blue)",
        "Graveyard Chest (TBox_Rupee_Red)",
        "Hyrule Field Chest (Item_ScrubBusinessSeed)",
        "Hyrule Field Chest (TBox_Rupee_Red) #1",
        "Hyrule Field Chest (TBox_Rupee_Red) #2",
        "Hyrule Field Chest (TBox_Rupee_Red) #3",
        "Hyrule Field Chest (TBox_Rupee_Red) #4",
        "Kakariko Village Chest (TBox_Rupee_Purple) [Adult Alternative]",
        "Kakariko Village Chest (TBox_Rupee_Purple) [Adult]",
        "Kokiri Forest Chest (TBox_Rupee_Purple)",
        "Lost Wood Chest (TBox_Rupee_Purple)",
        "Zora Fountain Chest (TBox_Rupee_Purple)",
    }
    assert (
        sorted(
            n
            for n in placements
            if n not in search.collected and n not in excluded and world.locations[n].type == "Chest"
        )
        == []
    )


def test_forest_start(world):
    search = reachable(world)
    assert search.can_access(world.locations["KF Kokiri Sword Chest"], CHILD)
    assert not search.can_reach("KF Outside Deku Tree")  # Mido wants the sword and a shield
    assert not search.can_reach("Kokiri Forest", ADULT)  # adult only after the Master Sword (Time Travel)

    search = reachable(world, ["Kokiri Sword", "Buy Deku Shield"])
    assert search.holds("Showed Mido Sword & Shield")
    assert search.can_reach("Deku Tree Slingshot Room", CHILD)  # here(has_shield)
    assert not search.can_reach("LW Bridge From Forest")  # can_leave_forest: Gohma first


def test_deku_tree_needs_what_ootr_says(world):
    base = ["Kokiri Sword", "Buy Deku Shield"]
    gohma = world.locations["Deku Tree Queen Gohma Heart"]
    # Child reaches the boss through the basement eye (Slingshot or verified Boomerang);
    # sticks for the torches come from the Deku Babas the Kokiri Sword kills ('Deku Stick Drop').
    assert not reachable(world, base).can_access(gohma)
    search = reachable(world, [*base, "Slingshot"])
    assert search.holds("Deku Stick Drop")
    assert search.can_access(gohma)


def test_remake_overrides(world):
    # Gold Skulltulas that need another item in the remake.
    hammer_gs = world.locations["Fire Temple GS Boss Key Loop"].rule
    assert not hammer_gs({}, ADULT, 1) and hammer_gs({"Megaton Hammer": 1}, ADULT, 1)
    ogc = world.locations["OGC GS"].rule
    assert not ogc({}, ADULT, 1) and ogc({"Hookshot": 1, "Progressive Hookshot": 1}, ADULT, 1)
    # The swapped Great Fairies, and checks the remake does not have.
    assert world.locations["DMT Great Fairy Reward"].vanilla == "Dins Fire"
    assert world.locations["HC Great Fairy Reward"].vanilla == "Magic Meter"
    assert world.locations["LLR GS Rain Shed"].n64_only
    assert world.locations["Ganons Castle Water Trial Left Chest"].n64_only
    assert world.locations["Spirit Temple Mirror Shield Chest"].area == "DesertColossus"
    assert world.locations["Market Treasure Chest Game Room 1 Top"].keep_vanilla


@pytest.mark.parametrize("keys,expected", [(2, False), (3, True)])
def test_three_keys_reach_dark_link(keys, expected):
    world = load_world()
    world.start = "Water Temple Lobby"
    gear = ["Hookshot", "Iron Boots", "Zora Tunic", "Fairy Ocarina", "Zeldas Lullaby"]
    search = Search(world, gear + ["Small Key (Water Temple)"] * keys)
    assert search.can_access(world.locations["Water Temple Longshot Chest"], ADULT) is expected


def test_fixed_items_are_the_default(world):
    # Saria gives the Fairy Ocarina, the target game a bigger bullet bag: one fixed item each (vanilla_fixed).
    assert world.locations["LW Gift from Saria"].vanilla == "Fairy Ocarina"
    assert world.locations["LW Target in Woods"].vanilla == "Bullet Bag (40)"
    assert world.locations["Water Temple Longshot Chest"].vanilla == "Longshot"
    assert not world.items["Bullet Bag (40)"].progression
    progressive = load_world({"progressive_items": True})
    assert progressive.locations["LW Gift from Saria"].vanilla == "Ocarina"


def _seed_failure(seed: int, progressive: bool) -> str | None:
    """Generate one seed and run the beatability search again on its placements (in a worker process)."""
    logic = {"progressive_items": progressive}
    try:
        result = generate(load_spec(), seed, Settings(logic=logic))
        check_beatable(load_world(logic), result.placements)
    except FillError as e:
        return f"seed {seed}: {e}"
    return None


def _workers() -> int:
    """At most 3 pool workers, 1 while hookshot.exe runs (plans/02-orchestration.md: Kareem plays on this PC; an
    8-worker sweep beside other test runs held the CPU at 100% and the game crashed twice). CLAWSHOT_WORKERS
    overrides."""
    if os.environ.get("CLAWSHOT_WORKERS"):
        return max(1, int(os.environ["CLAWSHOT_WORKERS"]))
    if sys.platform == "win32":
        try:
            tasks = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq hookshot.exe", "/NH"], capture_output=True, text=True, timeout=10
            ).stdout
        except (OSError, subprocess.SubprocessError):
            tasks = ""
        if "hookshot.exe" in tasks.lower():
            return 1
    return min(os.cpu_count() or 1, 3)


def _failures(seeds: range, progressive: bool) -> list[str]:
    with ProcessPoolExecutor(_workers()) as pool:
        results = pool.map(_seed_failure, seeds, [progressive] * len(seeds), chunksize=5)
        return [r for r in results if r]


def test_seeds_with_the_default_settings_are_beatable():
    assert _failures(range(SEEDS), progressive=False) == []


def test_seeds_with_progressive_items_are_beatable():
    assert _failures(range(20), progressive=True) == []


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
