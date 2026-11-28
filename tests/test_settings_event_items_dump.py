"""``event_item_models`` on and off against the dump (spec event-items 1.5, 3.2, 3.3; plan 5.5, 11.2, 11.3)."""

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from clawshot.census.hints import flow_path
from clawshot.formats import evfl, zsdic
from clawshot.generate import Settings
from clawshot.patch import containers, event_props, gifts, make_seed, write_seed
from clawshot.patch import items as item_actors
from clawshot.world.load import load_spec

pytestmark = pytest.mark.dump

SARIA = "LW Gift from Saria"
SLICE = dict(areas=("KokiriForest", "LostWood", "InsideTheDekuTree"), goal="'Defeat Queen Gohma'")


def _listing(folder: Path) -> dict[str, str]:
    return {
        p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(folder.rglob("*"))
        if p.is_file() and p.name != "spoiler.json"
    }


def _build(romfs, out: Path, settings: Settings, moved: bool) -> dict[str, str]:
    spec, chosen, step = gifts.seed_setup(romfs, load_spec(), settings)
    first = make_seed(romfs, 7, chosen, spec, extra_steps=[step])
    placements = {name: first.seed.placements[name] for name in first.seed.shuffled}
    if moved and SARIA in placements and placements[SARIA] == first.seed.world.locations[SARIA].vanilla:
        other = next(n for n in sorted(placements) if n != SARIA and placements[n] != placements[SARIA])
        placements[SARIA], placements[other] = placements[other], placements[SARIA]
    output = make_seed(romfs, 7, chosen, spec, extra_steps=[step], placements=placements)
    write_seed(output, romfs, out)
    return output.seed.placements


@pytest.fixture(scope="module")
def gift_seeds(romfs, tmp_path_factory):
    base = Settings(shuffle=("Chest", gifts.SHUFFLE), **SLICE)
    folders = {}
    for value in (True, False):
        folder = tmp_path_factory.mktemp(f"models-{value}")
        placements = _build(romfs, folder, replace(base, event_item_models=value), moved=True)
        folders[value] = folder
    return folders, placements


def test_dump_off_writes_no_model_file_and_still_names_the_given_item(romfs, gift_seeds):
    (folders, placements) = gift_seeds
    assert placements[SARIA] != "Fairy Ocarina"
    off = _listing(folders[False])
    assert not [path for path in off if containers.PREFIX in path]
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    path = flow_path(romfs, "Dm_Kokiri_0155")
    chart = evfl.read(dicts.decompress(path, (folders[False] / "romfs" / path).read_bytes())).flowchart
    given = item_actors.load().actor(placements[SARIA])
    assert next(e for e in chart.events if e.name == "Event77").params == {"ActorName": given}  # 1.5: text fix on
    assert "Item_Ocarina_Fairy" in [a.name for a in chart.actors]  # the prop keeps its native actor


def test_dump_on_and_off_differ_only_in_the_model_files(romfs, gift_seeds):
    (folders, placements) = gift_seeds
    on, off = _listing(folders[True]), _listing(folders[False])
    events = {f"romfs/{flow_path(romfs, p.event)}" for p in event_props.load().props if p.event}
    models = {
        "romfs/" + containers.ACTOR_INFO,
        "romfs/" + containers.GAME_ACTOR_INFO,
        "romfs/System/Resource/ResourceSizeTable.Product.111.Nin_Ounce_NVN2.rsizetable.zs",
    }
    different = {path for path in on.keys() | off.keys() if on.get(path) != off.get(path)}
    unexpected = sorted(p for p in different if p not in events | models and containers.PREFIX not in p)
    assert unexpected == []
    assert any(containers.PREFIX in p for p in on), "on moved Saria's gift but wrote no container"


def test_dump_on_with_every_inventoried_check_vanilla_writes_what_off_writes(romfs, tmp_path):
    base = Settings(shuffle=("Chest",), **SLICE)  # gifts and rewards stay vanilla
    listings = {}
    for value in (True, False):
        _build(romfs, tmp_path / str(value), replace(base, event_item_models=value), moved=False)
        listings[value] = _listing(tmp_path / str(value))
    assert listings[True] == listings[False]
