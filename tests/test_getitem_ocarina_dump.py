"""Ocarina get models in real produced seeds: chests and hand-overs without any ocarina chest.

Every difference from the dump is named. Gift-capable settings carry the model regardless of actual placements;
settings without Gift or its expanded kinds keep native packs and rows (PR #41 option 2)."""

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from clawshot.census import definitions
from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.generate import Settings, prepare
from clawshot.generate.fill import allowed
from clawshot.patch import (
    OCARINA_GET_MODEL,
    OCARINA_PICKUPS,
    SONG_GET_EFFECTS,
    getitem,
    gifts,
    make_seed,
    ocarina,
    ocarina_pickup,
    songs,
    write_seed,
)
from clawshot.patch import items as item_actors
from clawshot.patch.plan import PatchError
from clawshot.patch.shops import actor_path, member_path
from clawshot.world.load import load_spec

SETTINGS = Settings(shuffle=("Chest", "Gift", "Token"))
# Both ocarinas go to these chests (swapped with what the fill put there), whatever the fill chose.
CHESTS = {"KF Midos Top Left Chest": "Fairy Ocarina", "KF Midos Top Right Chest": "Ocarina of Time"}
HAND_OVERS = {"Market Shooting Gallery Reward": "Fairy Ocarina", "LW Skull Kid": "Ocarina of Time"}
# Steps allowed to change ActorInfo rows besides the ocarina step: they add rows of their own.
ROW_STEPS = {
    "clawshot.patch.event_models",  # event-items: container and placed-object rows (models in events)
    "clawshot.patch.containers",  # event-items: the container actors' own rows (models in events)
    "clawshot.patch.saria_farewell",  # event-items D9: the bridge Saria's own actor row, every seed
    "clawshot.patch.tokens",
    "clawshot.patch.custom_items",
    "clawshot.patch.floor_keys",
    "clawshot.patch.jail_keys",
}


def gift_only_spec():
    """Independent no-Chest writer world; the full game's progressive policy still requires Chest shuffle."""
    _, native = prepare(load_spec(), Settings())
    locations = {
        "LW Gift from Saria": "Fairy Ocarina",
        "HF Ocarina of Time Item": "Ocarina of Time",
        "Market Shooting Gallery Reward": "Bullet Bag (40)",
        "LW Skull Kid": "Piece of Heart",
    }
    return {
        "start": "Root",
        "goal": "True",
        "items": {
            name: asdict(item)
            | {"class": "progression" if item.progression else "priority" if item.priority else "normal"}
            for name, item in native.items.items()
        },
        "regions": [{"name": "Root", "locations": {name: "True" for name in locations}}],
        "locations": {
            name: {"type": "NPC", "vanilla": item, "source": "synthetic no-Chest writer contract"}
            for name, item in locations.items()
        },
    }


def ocarina_seed(romfs, targets, *, recipe=SETTINGS, spec=None):
    """Use the public recipe and compatible swaps; ``None`` selects audited direct-pouch gifts."""
    spec, settings, step = gifts.seed_setup(romfs, load_spec() if spec is None else spec, recipe)
    filled = make_seed(romfs, 7, settings, spec, extra_steps=[step])
    world, effective = filled.seed.world, filled.seed.settings
    placements = {name: filled.seed.placements[name] for name in filled.seed.shuffled}
    if targets is None:
        receipts = gifts.check_steps(gifts.scan_gifts(romfs), definitions.load())
        targets = {}
        for item in CHESTS.values():
            destination = next(
                name
                for name in placements
                if name not in targets
                and world.locations[name].type in gifts.GIFT_TYPES
                and receipts.get(name)
                and not gifts.is_hand_over(world.locations[name].type, receipts[name])
                and allowed(world, effective, name, item)
            )
            targets[destination] = item
    for destination, item in targets.items():
        source = next(name for name, placed in placements.items() if placed == item)
        displaced = placements[destination]
        if not allowed(world, effective, source, displaced):
            via = next(
                name
                for name, placed in placements.items()
                if name not in targets
                and not world.items[placed].progression
                and allowed(world, effective, source, placed)
                and allowed(world, effective, name, displaced)
            )
            placements[via], displaced = displaced, placements[via]
        placements[source], placements[destination] = displaced, item
    return make_seed(romfs, 7, settings, spec, extra_steps=[step], placements=placements)


@pytest.fixture(
    scope="module",
    params=(
        (SETTINGS, CHESTS, None),
        (SETTINGS, HAND_OVERS, None),
        (Settings(shuffle=("Gift",)), HAND_OVERS, gift_only_spec()),
        (SETTINGS, None, None),
    ),
    ids=("chests", "hand-overs-no-ocarina-chests", "gift-only-hand-overs", "direct-pouch-only-ocarinas"),
)
def seed(request, romfs, tmp_path_factory):
    recipe, targets, spec = request.param
    output = ocarina_seed(romfs, targets, recipe=recipe, spec=spec)
    if targets is not None:
        assert {name: output.seed.placements[name] for name in targets} == targets
    if targets != CHESTS:
        chests = [name for name in output.seed.shuffled if output.seed.world.locations[name].type == "Chest"]
        assert getitem.ocarina_locations(output.seed.placements, chests, item_actors.load()) == []
    if targets is None:
        receipts = gifts.check_steps(gifts.scan_gifts(romfs), definitions.load())
        locations = getitem.ocarina_locations(output.seed.placements, output.seed.shuffled, item_actors.load())
        assert {output.seed.placements[name] for name in locations} == set(CHESTS.values())
        assert all(
            output.seed.world.locations[name].type in gifts.GIFT_TYPES
            and not gifts.is_hand_over(output.seed.world.locations[name].type, receipts[name])
            for name in locations
        )
    out = tmp_path_factory.mktemp("ocarina-seed")
    written = {info.path: info for info in write_seed(output, romfs, out)}
    expected_steps = [OCARINA_GET_MODEL, SONG_GET_EFFECTS]
    if "Token" in recipe.shuffle:
        expected_steps.append(OCARINA_PICKUPS)
    assert json.loads((out / "spoiler.json").read_text())["patch"]["steps"] == expected_steps
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def read(path, root=None):
        root = romfs if root is None else out / "romfs"
        return dictionaries.decompress(path, (root / path).read_bytes())

    return output, written, read, lambda path: read(path, out)


@pytest.mark.dump
def test_hand_over_ocarinas_refuse_output_without_the_model_donor(romfs, monkeypatch):
    recipe = Settings(shuffle=("Chest", "Gift"))
    forced = ocarina_seed(romfs, HAND_OVERS, recipe=recipe)
    placements = {name: forced.seed.placements[name] for name in forced.seed.shuffled}
    chests = [name for name in forced.seed.shuffled if forced.seed.world.locations[name].type == "Chest"]
    assert getitem.ocarina_locations(placements, chests, item_actors.load()) == []
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), recipe)
    donor = romfs / getitem.pack_path(getitem.DONOR)
    native_is_file = Path.is_file
    monkeypatch.setattr(Path, "is_file", lambda path: path != donor and native_is_file(path))
    with pytest.raises(PatchError, match=r"ocarina get model copies from"):
        make_seed(romfs, 7, settings, spec, extra_steps=[step], placements=placements)


@pytest.mark.dump
def test_gift_ocarinas_refuse_output_without_an_audited_receipt(romfs, monkeypatch):
    forced = ocarina_seed(romfs, HAND_OVERS)
    placements = {name: forced.seed.placements[name] for name in forced.seed.shuffled}
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), SETTINGS)
    monkeypatch.setattr(gifts, "scan_gifts", lambda _: [])
    with pytest.raises(PatchError, match="ocarina gifts lack an audited receipt"):
        make_seed(romfs, 7, settings, spec, extra_steps=[step], placements=placements)


@pytest.mark.dump
def test_external_ocarina_placement_is_refused_when_settings_do_not_cover_it(romfs):
    settings = Settings(shuffle=("Chest",))
    filled = make_seed(romfs, 7, settings)
    placements = {name: filled.seed.placements[name] for name in filled.seed.shuffled}
    placements["KF Midos Top Left Chest"] = "Fairy Ocarina"
    with pytest.raises(PatchError, match="settings do not run the ocarina get model"):
        make_seed(romfs, 7, settings, placements=placements)


@pytest.mark.dump
def test_settings_without_gift_shuffle_keep_the_native_rows_and_packs(romfs, tmp_path):
    output = make_seed(romfs, 7, Settings(shuffle=("Chest", "Token")))  # Chest-only kinds: no ocarina in the pool
    assert output.steps == ()
    written = {info.path for info in write_seed(output, romfs, tmp_path / "seed")}
    assert not written & set(map(getitem.pack_path, getitem.OCARINAS)), sorted(written)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    rows = byml.read(
        dictionaries.decompress(getitem.ACTOR_INFO, (tmp_path / "seed/romfs" / getitem.ACTOR_INFO).read_bytes())
    )
    by_id = {row["__RowId"]: row for row in rows}
    assert [by_id[actor].get("CalcPriority") for actor in getitem.OCARINAS] == ["After", "After"]
    assert "CalcPriority" not in by_id[getitem.SARIA_PROP]


def step_module(transform):
    function = getattr(transform, "func", transform)
    return function.__module__


def ocarina_step(output) -> int:
    """The index of the ocarina get model's step. Only the song get effects (Gift shuffle lets songs move, so the seed
    gets them; song-get-effects) and the ocarina world actors (Gift and Token: ``ocarina_pickup.pickups_for``)
    may follow it, each adding rows of its own to ActorInfo; neither touches the ocarina packs."""
    steps = [{step_module(t) for t in step.values()} for step in output.extra_changes]
    index = max(i for i, modules in enumerate(steps) if getitem.__name__ in modules)
    assert steps[index] == {getitem.__name__}, steps[index]
    after = {songs.__name__, ocarina_pickup.__name__}
    assert all(modules <= after for modules in steps[index + 1 :]), steps[index + 1 :]
    return index


@pytest.mark.dump
def test_settings_selected_ocarina_step_is_last_on_its_files(seed):
    output, written, _, _ = seed
    paths = (getitem.ACTOR_INFO, *map(getitem.pack_path, getitem.OCARINAS))
    for path in paths:
        assert path in written, f"{path} is not in the output"
        touching = [i for i, step in enumerate(output.extra_changes[: ocarina_step(output) + 1]) if path in step]
        last = output.extra_changes[touching[-1]][path]
        assert step_module(last) == getitem.__name__, (
            path,
            [step_module(output.extra_changes[i][path]) for i in touching],
        )
    # It comes after ocarina.changes (the Time-stays-equipped receipts) in the recipe; only the song and ocarina
    # pickup steps follow.
    steps = [{step_module(t) for t in step.values()} for step in output.extra_changes]
    assert max(i for i, m in enumerate(steps) if ocarina.__name__ in m) < ocarina_step(output)
    for step in output.extra_changes[ocarina_step(output) + 1 :]:
        assert not set(map(getitem.pack_path, getitem.OCARINAS)) & set(step), "later steps leave the ocarinas"


@pytest.mark.dump
def test_actor_info_differs_from_the_dump_only_by_the_calc_priorities_and_named_steps_rows(seed):
    output, _, native, written = seed
    index = ocarina_step(output)
    other = [step[getitem.ACTOR_INFO] for step in output.extra_changes[:index] if getitem.ACTOR_INFO in step]
    later = [step[getitem.ACTOR_INFO] for step in output.extra_changes[index + 1 :] if getitem.ACTOR_INFO in step]
    names = sorted({step_module(transform) for transform in other})
    print(f"ActorInfo row steps before the ocarina step: {names}")
    assert set(names) <= ROW_STEPS, names
    expected = native(getitem.ACTOR_INFO)
    for transform in other:
        expected = transform(expected)
    expected_rows = byml.read(expected)
    before = {row["__RowId"] for row in byml.read(native(getitem.ACTOR_INFO))}
    if "Token" in output.seed.settings.shuffle:
        assert [row["__RowId"] for row in expected_rows if row["__RowId"] not in before], "Token pickups add rows"
    for row in expected_rows:
        if row["__RowId"] in getitem.OCARINAS:
            assert row.pop("CalcPriority") == "After", row["__RowId"]
        if row["__RowId"] == getitem.SARIA_PROP:
            assert "CalcPriority" not in row, row
            row["CalcPriority"] = "After"
    # The song and ocarina pickup steps after it (their own tests check their rows): applied as the seed applies them.
    expected_data = byml.dump(byml.Document(expected_rows))
    for transform in later:
        expected_data = transform(expected_data)
    expected_rows = byml.read(expected_data)
    after = byml.read(written(getitem.ACTOR_INFO))
    difference = byml.difference(after, expected_rows)
    assert difference is None, difference
    # 1.7: the written table reads back to the same tree.
    assert byml.same(byml.read(byml.dump(byml.load(written(getitem.ACTOR_INFO)))), after)


@pytest.mark.dump
@pytest.mark.parametrize("actor", getitem.OCARINAS)
def test_ocarina_pack_differs_from_native_only_by_the_get_model(seed, actor):
    _, _, native, written = seed
    path = getitem.pack_path(actor)
    before, data = sarc.read(native(path)), written(path)
    after = sarc.read(data)
    assert sarc.write(after) == data, f"{path} does not read back"
    donor = sarc.read(native(getitem.pack_path(getitem.DONOR)))
    animation = getitem.animation_member(actor)
    added = sorted(set(after) - set(before))
    assert added == sorted([animation, getitem.PERFORMER]), added
    assert not set(before) - set(after), sorted(set(before) - set(after))
    assert after[getitem.PERFORMER] == donor[getitem.PERFORMER], "PouchContent performer is not the donor's bytes"
    assert byml.read(after[animation]) == {
        "AnimationResources": [
            {"ModelProjectName": "Item_Common_Animation"},
            {"ModelProjectName": f"{actor}_Animation"},
        ]
    }, byml.read(after[animation])
    param = member_path(actor_path(actor))
    old, new = byml.read(before[param]), byml.read(after[param])
    expected = {
        **old["Components"],
        "EventPerformerRef": "?" + getitem.PERFORMER,
        "ASRef": "?" + getitem.ANIMATION_SET,
        "AnimationRef": "?" + animation,
    }
    assert old["Components"]["EventPerformerRef"] == "?" + getitem.COMMON_PERFORMER
    difference = byml.difference(new, {**old, "Components": expected})
    assert difference is None, difference
    changed = sorted(name for name in before if name != param and after[name] != before[name])
    assert changed == [], changed


@pytest.mark.dump
def test_ocarina_size_entries(seed, romfs):
    _, _, native, written = seed
    original = rstb.read(native(rstb.TABLE_PATH))
    table = rstb.read(written(rstb.TABLE_PATH))
    for actor in getitem.OCARINAS:
        pack = sarc.read(written(getitem.pack_path(actor)))
        param = member_path(actor_path(actor))
        components = len(byml.read(pack[param])["Components"])
        needed = rstb.required_size(param, len(pack[param]), components)
        assert table.get(param) == max(original.get(param), needed), (param, original.get(param), needed)
        animation = getitem.animation_member(actor)
        assert original.get(animation) is None, animation
        entry = rstb.required_size(animation, len(pack[animation]), resources=2)
        assert table.get(animation) == entry, (animation, table.get(animation), entry)
        print(f"{actor}: ActorParam {original.get(param)} -> {table.get(param)}, AnimationParam {entry}")
    assert table.get(getitem.PERFORMER) == original.get(getitem.PERFORMER) is not None
    assert table.get(getitem.ACTOR_INFO) >= original.get(getitem.ACTOR_INFO)
    for path in getitem.OCARINA_DUMP_FILES:
        assert (romfs / path).is_file(), path
