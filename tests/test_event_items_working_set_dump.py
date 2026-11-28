"""The app's working set holds every file the event-items steps read (plans/event-items.md, Handoff).

A ``.nup``, ``.nx`` or dump folder is generated from a temporary copy of only the declared working set
(``clawshot.pack.source.working_files``); an extracted romfs folder is used as is. So these builds copy ONLY the
working set of ``OOT_ROMFS`` into a temporary folder and generate full-feature seeds from it: the app's Recommended
settings (gift shuffle on) and a seed with songs, items and rewards forced at the event scenes, event_item_models on
and off. The same build from the whole dump is the oracle: a file read through an existence check (a missing pack
labels a text by the actor's name) would change the output silently instead of failing.
"""

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from clawshot.app.schema import presets
from clawshot.app.schema import validate as validate_settings
from clawshot.generate import Settings
from clawshot.pack.source import FolderRomfs, resource_spec, working_files
from clawshot.patch import containers, gifts, make_seed, saria_farewell, write_seed
from clawshot.world.load import load_spec

pytestmark = pytest.mark.dump

APP_SEED = 2431999637  # the seed of the failed app generation (BBender, 2026-11-27)
EVENT_SEED = 7100  # the QA builders' base seed
# Event scenes (event_props.toml) with a different item each: song containers (Saria's farewell, the moat's placed
# object and hand bind, the target's scene animation), a non-song item, rewards at reward scenes (Ruto's stone is a
# placed object) and prize lines (Anju, the Great Fairy). The two child songs the route needs stay at home, as in
# the QA seeds (build_qa_seed.py, build_matrix_seed.py).
FORCED = {
    "LW Gift from Saria": "Song of Storms",
    "HF Ocarina of Time Item": "Suns Song",
    "LW Target in Woods": "Eponas Song",
    "ToT Light Arrows Cutscene": "Piece of Heart",
    "DMT Biggoron": "Bottle",
    "Kak Anju as Child": "Hylian Shield",
    "HC Great Fairy Reward": "Iron Boots",
    "Queen Gohma": "Light Medallion",
    "ToT Reward from Rauru": "Kokiri Emerald",
    "Barinade": "Goron Ruby",
    "Volvagia": "Water Medallion",
    "Morpha": "Fire Medallion",
    "Song from Impa": "Zeldas Lullaby",
    "Song from Saria": "Sarias Song",
}
WARP_SONGS = ("Minuet of Forest", "Serenade of Water", "Requiem of Spirit", "Nocturne of Shadow", "Prelude of Light")


def event_settings(models: bool) -> Settings:
    """The QA seeds' settings (build_qa_seed.py): every event reachable, songs anywhere, Saria's farewell plays."""
    return replace(
        Settings(),
        shuffle=("Chest", "Gift"),
        dungeon_rewards=True,
        logic={"free_time_travel": True},
        door_of_time="open",
        forest="open",
        songs="anywhere",
        fast_start=("intro", "saria", "deku_tree", "kaepora"),
        skip_saria_farewell=False,
        starting_full_wallet=False,
        starting_items=("Fairy Ocarina", *(s for s in WARP_SONGS if s not in FORCED.values())),
        event_item_models=models,
    )


@pytest.fixture(scope="module")
def working_set(romfs, tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("event-items-working-set")
    source = FolderRomfs(romfs)
    for relative in sorted(working_files(source, resource_spec())):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read(relative))
    return root


def _setup(romfs: Path, settings: Settings):
    spec, steps = None, []
    if gifts.SHUFFLE in settings.shuffle or set(settings.shuffle).intersection(gifts.GIFT_TYPES):
        spec, settings, step = gifts.seed_setup(romfs, load_spec(), settings)
        steps.append(step)
    return spec, settings, steps


def _write(romfs: Path, output, out: Path) -> dict[str, str]:
    write_seed(output, romfs, out)
    return {
        p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob("*") if p.is_file()
    }


def app_build(romfs: Path, out: Path, settings: Settings) -> dict[str, str]:
    """As ``clawshot.app.jobs.generate_seed`` builds a seed."""
    spec, settings, steps = _setup(romfs, settings)
    return _write(romfs, make_seed(romfs, APP_SEED, settings, spec, extra_steps=steps), out)


def forced_placements(romfs: Path, settings: Settings) -> tuple[int, dict[str, str]]:
    """The first base seed from EVENT_SEED whose placements take FORCED (as build_qa_seed.py swaps them in)."""
    spec, setup, steps = _setup(romfs, settings)
    for attempt in range(EVENT_SEED, EVENT_SEED + 25):
        try:
            first = make_seed(romfs, attempt, setup, spec, extra_steps=steps)
        except Exception as error:  # noqa: BLE001 - a base seed that does not fill is skipped, as the QA builder does
            print("base", attempt, "fill failed:", error)
            continue
        placements = {name: first.seed.placements[name] for name in first.seed.shuffled}
        assert not (missing := sorted(set(FORCED) - set(placements))), f"not shuffled: {missing}"
        done: set[str] = set()
        for location, item in FORCED.items():
            done.add(location)
            if placements[location] == item:
                continue
            holders = [n for n, p in sorted(placements.items()) if p == item and n not in done]
            holder = next((n for n in holders if n not in FORCED), holders[0] if holders else None)
            assert holder is not None, f"{item} is in no shuffled location of base seed {attempt}"
            placements[holder], placements[location] = placements[location], item
        try:
            make_seed(romfs, attempt, setup, spec, extra_steps=steps, placements=placements)
        except Exception as error:  # noqa: BLE001
            print("base", attempt, "forced placements refused:", error)
            continue
        return attempt, placements
    pytest.fail("no base seed took the forced placements")


def event_build(romfs: Path, out: Path, settings: Settings, attempt: int, placements: dict[str, str]):
    spec, setup, steps = _setup(romfs, settings)
    return _write(romfs, make_seed(romfs, attempt, setup, spec, extra_steps=steps, placements=placements), out)


def _same(actual: dict[str, str], expected: dict[str, str]) -> None:
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    changed = sorted(name for name in actual.keys() & expected.keys() if actual[name] != expected[name])
    assert actual == expected, f"missing {missing}; extra {extra}; changed {changed}"


def _containers(files: dict[str, str]) -> list[str]:
    prefix = "romfs/Pack/Actor/" + containers.PREFIX
    return sorted(name for name in files if name.startswith(prefix))


FAREWELL = "romfs/" + saria_farewell.pack_path(saria_farewell.FAREWELL)


def test_the_app_settings_build_from_the_working_set_alone(romfs, working_set, tmp_path):
    recommended = next(preset for preset in presets() if preset["id"] == "recommended")
    settings = validate_settings(text=recommended["settings_string"])
    assert gifts.SHUFFLE in settings.shuffle
    actual = app_build(working_set, tmp_path / "cached", settings)
    assert FAREWELL in actual
    _same(actual, app_build(romfs, tmp_path / "reference", settings))


@pytest.mark.parametrize("models", [True, False], ids=["models-on", "models-off"])
def test_event_scene_placements_build_from_the_working_set_alone(romfs, working_set, tmp_path, models):
    settings = event_settings(models)
    attempt, placements = forced_placements(working_set, settings)
    actual = event_build(working_set, tmp_path / "cached", settings, attempt, placements)
    shown = _containers(actual)
    if models:  # the step ran: song containers and a non-song item's container
        assert any(containers.is_song_container(Path(name).name.removesuffix(".pack.zs")) for name in shown), shown
        assert any(not containers.is_song_container(Path(name).name.removesuffix(".pack.zs")) for name in shown), shown
    else:
        assert shown == []
    assert FAREWELL in actual
    _same(actual, event_build(romfs, tmp_path / "reference", settings, attempt, placements))
