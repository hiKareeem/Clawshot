"""The remake's overrides: several files (``remake.toml`` and ``remake/*.toml``), new regions, exits and events,
locations moved between regions, and the errors that keep two files from setting one thing."""

from pathlib import Path

import pytest

from clawshot.generate import Settings, prepare
from clawshot.generate.fill import FillError, check_beatable
from clawshot.world import ADULT, CHILD, Search, WorldError, build_world, load_spec, load_world, reachable
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
        ({"items": {"Gone": {"alias": ["Slingshot", 1], "source": "s"}}}, "item 'Gone' is not in the world"),
        ({"items": {"Slingshot": {"alias": ["Gone", 1], "source": "s"}}}, "alias must be \\[a known item"),
        ({"items": {"Slingshot": {"alias": ["Slingshot", 0], "source": "s"}}}, "alias must be \\[a known item"),
        ({"walls": {}}, "unknown tables \\['walls'\\]"),
    ],
)
def test_bad_overrides_are_refused(overrides: dict, message: str):
    with pytest.raises(WorldError, match=message):
        apply_overrides(spec(), [("f", overrides)])


def test_an_item_alias_also_counts_the_other_item():
    """The remake's magic items each carry a magic meter: collecting one counts as the meter too."""
    changed = spec()
    changed["items"]["Bullet Bag"] = {}
    alias = {"items": {"Bullet Bag": {"alias": ["Slingshot", 1], "source": "s"}}}
    apply_overrides(changed, [("f", alias)])
    world = build_world(changed)
    assert world.items["Bullet Bag"].alias == ("Slingshot", 1)
    assert reachable(world, []).counts.get("Lit", 0) == 0
    assert reachable(world, ["Bullet Bag"]).counts["Lit"] == 1
    with pytest.raises(WorldError, match=r"f: item 'Bullet Bag' already counts as \['Slingshot', 1\]"):
        apply_overrides(changed, [("f", alias)])


# Round 3's playtest slice: Kokiri Forest, the Lost Woods and the Deku Tree, beaten at Queen Gohma.
SLICE = Settings(areas=("KokiriForest", "LostWood", "InsideTheDekuTree"), goal="'Defeat Queen Gohma'")


@pytest.fixture(scope="module")
def deku_slice():
    return prepare(load_spec(), SLICE)[1]


def test_deku_tree_slingshot_in_the_basement_is_not_beatable(deku_slice):
    """Gohma is unreachable when the only ranged-weapon copy is past the ranged gate."""
    vanilla = {
        name: "Progressive Slingshot" if loc.vanilla == "Slingshot" else loc.vanilla
        for name, loc in deku_slice.locations.items()
        if loc.vanilla is not None
    }
    check_beatable(deku_slice, vanilla)
    swapped = vanilla | {
        "Deku Tree Basement Chest": "Progressive Slingshot",
        "Deku Tree Slingshot Chest": vanilla["Deku Tree Basement Chest"],
    }
    with pytest.raises(FillError, match="the goal cannot be reached"):
        check_beatable(deku_slice, swapped)


@pytest.mark.parametrize("weapon", ["Progressive Slingshot", "Boomerang"])
def test_deku_tree_top_floor_and_basement_need_a_verified_ranged_weapon(deku_slice, weapon):
    others = [
        loc.vanilla for loc in deku_slice.locations.values() if loc.vanilla not in (None, "Slingshot", "Boomerang")
    ]
    without = reachable(deku_slice, others)
    with_weapon = reachable(deku_slice, [*others, weapon])
    for name in ("Deku Tree Compass Chest", "Deku Tree GS Compass Room", "Deku Tree Basement Chest"):
        assert not without.can_access(deku_slice.locations[name]), name
        assert with_weapon.can_access(deku_slice.locations[name], CHILD), name
    # Entry still needs a Deku Shield, not either ranged weapon; exit/reload recovery is a separate question.
    for name in ("Deku Tree Map Chest", "Deku Tree Slingshot Chest", "Deku Tree Slingshot Room Side Chest"):
        assert without.can_access(deku_slice.locations[name], CHILD), name


def test_night_comes_only_after_meeting_zelda():
    """The remake's clock starts once Link has met Zelda (event 'Time Flows' in the castle garden, which the Weird
    Egg or the Chicken opens): before that a child gets no night-only check."""
    world = load_world()
    items = [
        loc.vanilla
        for loc in world.locations.values()
        if loc.vanilla is not None and loc.vanilla not in ("Weird Egg", "Chicken")
    ]
    night_only = ("Graveyard Dampe Gravedigging Tour", "Kak GS Skulltula House", "Market Lost Dog")
    before = reachable(world, items)
    after = reachable(world, [*items, "Weird Egg"])
    assert not before.holds("Time Flows") and after.holds("Time Flows")
    for name in night_only:
        assert not before.can_access(world.locations[name], CHILD), name
        assert after.can_access(world.locations[name], CHILD), name


def fountain(region: str):
    spec = load_spec()
    spec["start"] = region
    return build_world(spec)


LULLABY = ["Fairy Ocarina", "Zeldas Lullaby"]


def test_only_dins_fairy_comes_without_dins_fire():
    """TriForcePoint: Zelda's Lullaby calls every Great Fairy but Din's only once Din's Fire is held, so the
    Improved Spin (Hyrule Castle) cannot come first; the magic meter does not stand in for Din's Fire."""
    dmt = fountain("DMT Great Fairy Fountain")
    assert Search(dmt, LULLABY).can_access(dmt.locations["DMT Great Fairy Reward"], CHILD)
    hc = fountain("HC Great Fairy Fountain")
    spin = hc.locations["HC Great Fairy Reward"]
    search = Search(hc, [*LULLABY, "Magic Meter"])
    assert not search.can_access(spin, CHILD)
    search.collect("Dins Fire")
    assert search.can_access(spin, CHILD)


@pytest.mark.parametrize(
    ("region", "location"),
    [
        ("Colossus Great Fairy Fountain", "Colossus Great Fairy Reward"),
        ("OGC Great Fairy Fountain", "OGC Great Fairy Reward"),
    ],
)
def test_the_300_and_500_rupee_fairies_need_the_adult_wallet(region: str, location: str):
    """Their fees are past the starting wallet's 200; the Adult Wallet holds 500."""
    world = fountain(region)
    search = Search(world, ["Ocarina of Time", "Zeldas Lullaby", "Dins Fire"])
    assert not search.can_access(world.locations[location], ADULT)
    search.collect("Adult Wallet")
    assert search.can_access(world.locations[location], ADULT)
