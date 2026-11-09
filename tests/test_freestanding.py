import copy
from collections import Counter
from dataclasses import replace

import pytest

from clawshot.census.definitions import Definition
from clawshot.census.scan import Location
from clawshot.formats import byml
from clawshot.formats.byml import U64
from clawshot.generate import Settings, generate, prepare
from clawshot.generate.fill import allowed, shuffled_locations
from clawshot.patch import drops, freestanding
from clawshot.patch.plan import PatchError


def location(actor_id=42, actor="Obj_Heart_Piece"):
    return Location(
        actor_id,
        "freestanding",
        "Test",
        None,
        ("Banc/Test/Child_Static.bcett.byml.zs", "Banc/Test/Adult_Alternative_Static.bcett.byml.zs"),
        "both",
        (1, 2, 3),
        actor,
        actor,
        None,
        True,
    )


def tree(actor="Obj_Heart_Piece"):
    return {
        "Actors": [
            {
                "Hash": U64(42),
                "Gyaml": actor,
                "Phive": {"Placement": {"ID": U64(42)}},
                "Translate": [1, 2, 3],
                "Presence": {"FlagName": "OriginalPresence", "IsNegation": True},
            },
            {"Hash": U64(43), "Gyaml": "HeartPieceAnchor", "Links": [{"Dst": U64(42)}]},
        ],
        "AiGroups": [{"References": [{"Reference": U64(90), "Id": "Unrelated"}]}],
        "SimultaneousGroups": [[U64(90), U64(91)]],
        "FarDeleteGroups": [[U64(90), U64(91)]],
    }


@pytest.mark.parametrize("original", sorted(freestanding.HEART_PIECES))
@pytest.mark.parametrize("pickup", freestanding.NATIVE_ITEMS.values())
def test_native_palette_preserves_anchor_saved_identity_and_every_copy(original, pickup):
    loc = location(actor=original)
    transforms = freestanding.changes({42: pickup}, [loc])
    assert set(transforms) == set(loc.files)
    for transform in transforms.values():
        source = tree(original)
        after = byml.read(transform(byml.write(source)))
        assert after["Actors"][0]["Gyaml"] == pickup
        after["Actors"][0]["Gyaml"] = original
        assert byml.same(source, after)


@pytest.mark.parametrize("pickup", ["Item_Boomerang", "Obj_Arrow_Fire", "Obj_Token_Gold", "Obj_Heart", ""])
def test_other_actors_do_not_become_floor_grants(pickup):
    with pytest.raises(PatchError):
        freestanding.changes({42: pickup}, [location()])


@pytest.mark.parametrize(
    "loc",
    [
        replace(location(), has_save_flag=False),
        replace(location(), files=()),
        replace(location(), actor="Obj_Dungeon_SmallKey"),
        replace(location(), kind="heart_container"),
    ],
)
def test_nonpersistent_or_other_check_families_are_refused(loc):
    with pytest.raises(PatchError):
        freestanding.changes({42: "Obj_Shield_Hylian"}, [loc])


@pytest.mark.parametrize("fault", ["missing", "duplicate", "actor", "placement", "script"])
def test_stale_or_new_script_contract_refuses_the_file(fault):
    source = tree()
    if fault == "missing":
        source["Actors"].pop(0)
    elif fault == "duplicate":
        source["Actors"].append(copy.deepcopy(source["Actors"][0]))
    elif fault == "actor":
        source["Actors"][0]["Gyaml"] = "Obj_Arrow_Fire"
    elif fault == "placement":
        source["Actors"][0]["Phive"]["Placement"]["ID"] = U64(7)
    else:
        source["AiGroups"][0]["References"].append({"Reference": U64(42), "Id": "Scripted"})
    transform = next(iter(freestanding.changes({42: "Obj_Shield_Hylian"}, [location()]).values()))
    with pytest.raises(PatchError):
        transform(byml.write(source))


def setup():
    vanilla = {
        "Heart A": "Piece of Heart",
        "Heart B": "Piece of Heart",
        "Sword": "Sword",
        "Normal": "Normal",
        "Native": "Hylian Shield",
        "Key": "Key",
        "Unmapped N64 Rupee": "Rupees (20)",
        "Excluded Heart": "Piece of Heart",
        "Event Heart": "Piece of Heart",
    }
    spec = {
        "start": "Root",
        "goal": "Sword",
        "settings": {"starting_age": "child"},
        "items": {
            item: {"class": "progression" if item in {"Sword", "Hylian Shield"} else "normal"}
            for item in vanilla.values()
        },
        "regions": [{"name": "Root", "area": "Test", "locations": {name: "True" for name in vanilla}}],
        "locations": {
            name: {
                "type": "Collectable"
                if item in {"Piece of Heart", "Key"}
                else "Freestanding"
                if name.startswith("Unmapped")
                else "Chest",
                "vanilla": item,
                **({"keep_vanilla": "Unresolved route"} if name == "Excluded Heart" else {}),
            }
            for name, item in vanilla.items()
        },
    }
    census = [location(), location(44, "Obj_GerudoValley_Heart_Piece")]
    definitions = [
        Definition(loc.id, loc.kind, loc.area, name, loc.actor, name)
        for loc, name in zip(census, ("Heart A", "Heart B"), strict=True)
    ]
    return spec, census, definitions


def test_only_linked_hearts_join_and_prior_restrictions_survive_real_fill():
    spec, census, definitions = setup()
    before = copy.deepcopy(spec)
    settings = Settings(
        shuffle=("Chest", "Freestanding"),
        item_location_types={"Normal": ("Chest", "Freestanding"), "Hylian Shield": ("Chest",)},
    )
    restricted = freestanding.restrict_spec(spec, definitions)
    _, world = prepare(restricted, settings)
    effective, step = freestanding.seed_setup(world, settings, census, definitions, {})
    assert spec == before
    assert set(shuffled_locations(world, effective)) == {"Heart A", "Heart B", "Sword", "Normal", "Native"}
    assert world.locations["Key"].type == "Collectable"
    assert world.locations["Event Heart"].type == "Collectable"
    assert world.locations["Excluded Heart"].keep_vanilla == "Unresolved route"
    assert effective.item_location_types["Hylian Shield"] == ("Chest",)
    for n in range(20):
        seed = generate(restricted, n, effective, attempts=1)
        assert Counter(seed.placements[name] for name in seed.shuffled) == Counter(
            world.locations[name].vanilla for name in seed.shuffled
        )
        assert seed.placements["Key"] == "Key"
        assert seed.placements["Unmapped N64 Rupee"] == "Rupees (20)"
        assert seed.placements["Event Heart"] == "Piece of Heart"
        assert all(
            allowed(seed.world, effective, name, item)
            for name, item in seed.placements.items()
            if name in seed.shuffled
        )
        assert all(seed.placements[name] in freestanding.NATIVE_ITEMS for name in ("Heart A", "Heart B"))
    replay = Settings.from_string(effective.to_string())
    assert generate(restricted, 7, replay).placements == generate(restricted, 7, effective).placements
    assert step({"Heart A": "Piece of Heart", "Heart B": "Piece of Heart"}) == {}
    with pytest.raises(PatchError):
        step({"Heart A": "Sword", "Heart B": "Piece of Heart"})
    # Default-off: the unchanged spec/settings do not shuffle Collectables or N64 floor rows.
    _, default_world = prepare(spec, Settings())
    assert not set(shuffled_locations(default_world, Settings())) & {"Heart A", "Heart B", "Unmapped N64 Rupee"}


@pytest.mark.parametrize("fault", ["definition", "duplicate", "census", "saved", "area"])
def test_missing_or_unsafe_physical_link_refuses_seed_generation(fault):
    spec, census, definitions = setup()
    restricted = freestanding.restrict_spec(spec, definitions)
    if fault == "definition":
        definitions.pop()
    elif fault == "duplicate":
        definitions.append(definitions[0])
    elif fault == "census":
        census.pop()
    elif fault == "saved":
        census[0] = replace(census[0], has_save_flag=False)
    else:
        census[0] = replace(census[0], area="Other")
    settings = Settings(shuffle=("Chest", "Freestanding"))
    _, world = prepare(restricted, settings)
    with pytest.raises(PatchError):
        freestanding.seed_setup(world, settings, census, definitions, {})


def test_boss_heart_and_floor_destination_policies_intersect():
    spec, census, definitions = setup()
    spec["locations"]["Boss"] = {"type": "BossHeart", "vanilla": "Heart Container"}
    spec["items"]["Heart Container"] = {"class": "normal"}
    spec["regions"][0]["locations"]["Boss"] = "True"
    census.append(replace(location(80, drops.HEART), kind="heart_container"))
    definitions.append(Definition(80, "heart_container", "Test", "Boss", drops.HEART, "Boss"))
    settings = Settings(shuffle=("Chest", "BossHeart", "Freestanding"))
    restricted = freestanding.restrict_spec(spec, definitions)
    _, world = prepare(restricted, settings)
    effective, _ = freestanding.seed_setup(world, settings, census, definitions, {})
    effective, _ = drops.seed_setup(world, effective, census, definitions, {})
    seed = generate(restricted, 7, effective, attempts=1)
    assert seed.placements["Boss"] in drops.NATIVE_ITEMS
    assert all(seed.placements[name] in freestanding.NATIVE_ITEMS for name in ("Heart A", "Heart B"))
    assert not allowed(world, effective, "Boss", "Normal")
    assert not allowed(world, effective, "Heart A", "Normal")


def test_native_shield_from_floor_check_can_be_required_for_the_goal():
    spec, census, definitions = setup()
    spec["goal"] = "Sword and Hylian_Shield"
    settings = Settings(
        shuffle=("Chest", "Freestanding"),
        item_location_types={"Hylian Shield": ("Freestanding",)},
    )
    restricted = freestanding.restrict_spec(spec, definitions)
    _, world = prepare(restricted, settings)
    effective, step = freestanding.seed_setup(world, settings, census, definitions, {})
    for n in range(20):
        seed = generate(restricted, n, effective, attempts=1)
        floor = {name: seed.placements[name] for name in ("Heart A", "Heart B")}
        assert "Hylian Shield" in floor.values()
        transforms = step(floor)
        target = next(name for name, item in floor.items() if item == "Hylian Shield")
        loc = census[0 if target == "Heart A" else 1]
        source = tree(loc.actor)
        source["Actors"][0]["Hash"] = U64(loc.id)
        source["Actors"][0]["Phive"]["Placement"]["ID"] = U64(loc.id)
        after = byml.read(transforms[loc.files[0]](byml.write(source)))
        assert after["Actors"][0]["Gyaml"] == "Obj_Shield_Hylian"
