import pytest

from clawshot.census.scan import Location
from clawshot.formats import byml
from clawshot.formats.byml import U64
from clawshot.patch import tokens
from clawshot.patch.plan import PatchError


def location():
    return Location(
        42,
        "gold_skulltula",
        "Test",
        None,
        ("Banc/Test/Child.bcett.byml.zs", "Banc/Test/Adult.bcett.byml.zs"),
        "both",
        (0, 0, 0),
        tokens.ENEMY,
        tokens.TOKEN,
        None,
        True,
    )


def tree():
    return {
        "Actors": [
            {
                "Hash": U64(42),
                "Gyaml": tokens.ENEMY,
                "Translate": [0, 0, 0],
                "Dynamic": {"Enemy_Skulltula_Gold_Nocturnal": True},
            },
            {"Hash": U64(43), "Gyaml": tokens.ENEMY, "Translate": [1, 0, 0]},
        ],
        "AiGroups": [{"Hash": U64(80), "References": [{"Reference": U64(42)}]}],
    }


def test_every_copy_changes_drop_not_enemy_hash_or_spawn_logic():
    loc = location()
    transforms = tokens.changes({42: "Obj_Shield_Hylian"}, [loc])
    assert tuple(transforms) == tuple(sorted(loc.files))
    for transform in transforms.values():
        after = byml.read(transform(byml.write(tree())))
        assert after["Actors"][0]["Dynamic"].pop(tokens.DROP) == "Obj_Shield_Hylian"
        assert byml.same(after, tree())


@pytest.mark.parametrize("item", ["Item_Boomerang", "Unknown", ""])
def test_inventory_only_or_unknown_actor_is_not_a_pickup(item):
    with pytest.raises(PatchError):
        tokens.changes({42: item}, [location()])


def test_wrong_or_already_changed_enemy_is_refused():
    transform = next(iter(tokens.changes({42: "Obj_Rupee_Red"}, [location()]).values()))
    for change in ("missing", "actor", "drop"):
        t = tree()
        if change == "missing":
            t["Actors"].pop(0)
        elif change == "actor":
            t["Actors"][0]["Gyaml"] = "Enemy_Other"
        else:
            t["Actors"][0]["Dynamic"][tokens.DROP] = "Obj_Heart"
        with pytest.raises(PatchError):
            transform(byml.write(t))
    with pytest.raises(PatchError):
        tokens.changes({99: "Obj_Rupee_Red"}, [location()])


def test_unverified_token_mode_refuses_before_reading_dump_or_writing_seed(tmp_path):
    from clawshot.generate import Settings
    from clawshot.patch import make_seed

    with pytest.raises(PatchError):
        make_seed(tmp_path / "no-dump", 7, Settings(shuffle=("Token",)))
    assert not list(tmp_path.iterdir())
