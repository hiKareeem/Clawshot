from dataclasses import replace

import pytest

from clawshot.census.scan import Location
from clawshot.formats import byml
from clawshot.formats.byml import U64
from clawshot.patch import drops
from clawshot.patch.plan import PatchError


def location():
    return Location(
        42,
        "heart_container",
        "Test",
        7,
        ("Banc/Test/Static.bcett.byml.zs", "Banc/Test/Alternative.bcett.byml.zs"),
        "both",
        (1, 2, 3),
        drops.HEART,
        drops.HEART,
        None,
        True,
    )


def tree():
    return {
        "Actors": [
            {"Hash": U64(42), "Gyaml": drops.HEART, "Translate": [1, 2, 3], "Dynamic": {"Room": 7}},
            {"Hash": U64(43), "Gyaml": "Enemy_Boss"},
        ],
        "AiGroups": [
            {
                "Hash": U64(80),
                "Logic": "Logic/TestBoss.ain",
                "References": [{"Id": "Obj_Heart_Container_1234", "Path": "heart", "Reference": U64(42)}],
            }
        ],
        "SimultaneousGroups": [[U64(42), U64(43)]],
        "FarDeleteGroups": [[U64(42), U64(43)]],
    }


def test_native_pickup_replaces_only_gyaml_on_every_copy():
    transforms = drops.changes({42: "Obj_Shield_Hylian"}, [location()])
    assert set(transforms) == set(location().files)
    for transform in transforms.values():
        after = byml.read(transform(byml.write(tree())))
        assert after["Actors"][0]["Gyaml"] == "Obj_Shield_Hylian"
        after["Actors"][0]["Gyaml"] = drops.HEART
        assert byml.same(after, tree())


@pytest.mark.parametrize("pickup", ["Item_Boomerang", "Obj_Arrow_Fire", "Obj_Unknown", ""])
def test_non_native_or_known_crashing_pickup_refused(pickup):
    with pytest.raises(PatchError):
        drops.changes({42: pickup}, [location()])


@pytest.mark.parametrize("change", ["missing", "duplicate", "actor", "logic", "binding", "simultaneous", "far"])
def test_stale_actor_or_lost_group_contract_refused(change):
    source = tree()
    if change == "missing":
        source["Actors"].pop(0)
    elif change == "duplicate":
        source["Actors"].append(source["Actors"][0].copy())
    elif change == "actor":
        source["Actors"][0]["Gyaml"] = "Obj_Heart_Piece"
    elif change == "logic":
        source["AiGroups"] = []
    elif change == "binding":
        source["AiGroups"][0]["References"][0]["Id"] = "Enemy_Boss"
    elif change == "simultaneous":
        source["SimultaneousGroups"] = []
    else:
        source["FarDeleteGroups"] = []
    transform = next(iter(drops.changes({42: "Obj_Shield_Hylian"}, [location()]).values()))
    with pytest.raises(PatchError):
        transform(byml.write(source))


@pytest.mark.parametrize("loc", [replace(location(), has_save_flag=False), replace(location(), kind="chest")])
def test_non_saved_or_non_heart_location_refused(loc):
    with pytest.raises(PatchError):
        drops.changes({42: "Obj_Shield_Hylian"}, [loc])
