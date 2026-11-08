"""The remake's overrides: several files (``remake.toml`` and ``remake/*.toml``), new regions, exits and events,
locations moved between regions, and the errors that keep two files from setting one thing."""

from pathlib import Path

import pytest

from clawshot.world import CHILD, WorldError, build_world, load_spec, reachable
from clawshot.world.load import apply_overrides

WORLD_TOML = """
start = "Root"
goal = "True"
files = ["field.toml"]
overrides = "remake.toml"
"""

FIELD_TOML = """
[[region]]
name = "Root"
[region.exits]
"Field" = "True"

[[region]]
name = "Field"
area = "Field"
[region.locations]
"Field Chest" = "True"
"Tower Chest" = "True"
[region.exits]
"Root" = "True"

[locations]
"Field Chest" = { type = "Chest", vanilla = "Slingshot" }
"Tower Chest" = { type = "Chest", vanilla = "Rupee" }
"""


def write_world(directory: Path, remake: str, more: dict[str, str]) -> Path:
    files = {
        "world.toml": WORLD_TOML,
        "items.toml": '[items]\n"Slingshot" = {}\n"Rupee" = { class = "normal" }\n',
        "helpers.toml": "[helpers]\nis_child = \"age == 'child'\"\n",
        "settings.toml": '[settings]\nstarting_age = "child"\n[flags]\nensure_tod_access = false\n',
        "field.toml": FIELD_TOML,
        "remake.toml": remake,
        **{f"remake/{name}": text for name, text in more.items()},
    }
    for name, text in files.items():
        (directory / name).parent.mkdir(exist_ok=True)
        (directory / name).write_text(text, encoding="utf-8")
    return directory


# A tower OoT Randomizer folds into the field: the remake needs the Slingshot to climb it. The region is added in
# one file and used in another that sorts before it, so files see each other's regions whatever their order.
TOWER = """
[exits."Field".Tower]
rule = "Slingshot"
new = true
source = "test"

[locations."Tower Chest"]
region = "Tower"
source = "test"
"""
TOWER_REGION = """
[regions.Tower]
area = "Field"
source = "test"

[exits.Tower.Field]
rule = "True"
new = true
source = "test"
"""


def test_folder_files_apply_after_the_main_file(tmp_path: Path):
    spec = load_spec(write_world(tmp_path, "", {"a_tower.toml": TOWER, "b_region.toml": TOWER_REGION}))
    world = build_world(spec)
    tower = world.locations["Tower Chest"]
    assert tower.region == "Tower" and tower.area == "Field" and tower.override == "test"
    assert not reachable(world).can_access(tower)
    assert reachable(world, ["Slingshot"]).can_access(tower, CHILD)
    assert reachable(world).can_access(world.locations["Field Chest"], CHILD)


def test_one_thing_set_in_two_files_is_an_error(tmp_path: Path):
    other = '[locations."Tower Chest"]\nvanilla = "Slingshot"\nsource = "test"\n'
    directory = write_world(tmp_path, other, {"a_tower.toml": TOWER, "b_region.toml": TOWER_REGION})
    with pytest.raises(WorldError, match=r"remake/a_tower.toml: locations 'Tower Chest' is also set in remake.toml"):
        load_spec(directory)
    exit_twice = '[exits."Field".Tower]\nrule = "False"\nnew = true\nsource = "test"\n'
    directory = write_world(tmp_path, exit_twice, {"a_tower.toml": TOWER, "b_region.toml": TOWER_REGION})
    with pytest.raises(WorldError, match=r"exits 'Field -> Tower' is also set in remake.toml"):
        load_spec(directory)


def spec() -> dict:
    return {
        "start": "Root",
        "goal": "True",
        "items": {"Slingshot": {}},
        "helpers": {},
        "settings": {},
        "regions": [
            {"name": "Root", "exits": {"Room": "True"}},
            {"name": "Room", "exits": {"Root": "True"}, "events": {"Lit": "Slingshot"}},
        ],
        "locations": {},
    }


def test_an_exit_change_needs_the_translated_rule():
    changed = spec()
    apply_overrides(
        changed, [("f", {"exits": {"Room": {"Root": {"rule": "Slingshot", "was": "True", "source": "s"}}}})]
    )
    world = build_world(changed)
    assert [(e.target, e.source) for e in world.regions["Room"].exits] == [("Root", "s")]
    with pytest.raises(WorldError, match=r"f: region 'Room', exit to 'Root': was 'False', but the translated rule"):
        apply_overrides(spec(), [("f", {"exits": {"Room": {"Root": {"rule": "x", "was": "False", "source": "s"}}}})])


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"exits": {"Room": {"Root": {"rule": "x", "new": True, "source": "s"}}}}, "new, but the region has it"),
        ({"exits": {"Room": {"Gone": {"rule": "x", "was": "True", "source": "s"}}}}, "exit to 'Gone' is not in"),
        ({"exits": {"Room": {"Root": {"rule": "x", "source": "s"}}}}, "needs rule, and was"),
        ({"exits": {"Hall": {"Root": {"rule": "x", "new": True, "source": "s"}}}}, "region 'Hall', which is not"),
        ({"events": {"Room": {"Lit": {"rule": "True", "was": "True", "source": "s"}}}}, "event 'Lit': was 'True'"),
        ({"events": {"Room": {"Lit": {"rule": "True", "was": "Slingshot"}}}}, "event 'Lit': no source"),
        ({"regions": {"Room": {"source": "s"}}}, "region 'Room' is already in the world"),
        ({"regions": {"Hall": {"floor": 2, "source": "s"}}}, "unknown fields \\['floor'\\]"),
        ({"locations": {"Gone": {"vanilla": "Slingshot", "source": "s"}}}, "location 'Gone' is not in the world"),
        ({"walls": {}}, "unknown tables \\['walls'\\]"),
    ],
)
def test_bad_overrides_are_refused(overrides: dict, message: str):
    with pytest.raises(WorldError, match=message):
        apply_overrides(spec(), [("f", overrides)])
