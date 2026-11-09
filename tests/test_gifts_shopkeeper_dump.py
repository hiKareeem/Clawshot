"""Exact merchant-flow delta and existing saved eligibility flag on the player's read-only dump."""

import copy

import pytest
from test_gifts_shopkeeper import run_offer

from clawshot.census import definitions
from clawshot.census.gifts import scan_gifts
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import evfl, zsdic
from clawshot.generate import Settings, prepare
from clawshot.patch import gifts
from clawshot.patch.items import load as load_actors
from clawshot.save import murmur3_32
from clawshot.world.load import load_spec


@pytest.mark.dump
def test_shopkeeper_both_grants_are_once_only_without_new_save_data(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    census = scan_gifts(romfs)
    [change] = gifts.plan({gifts.SHOPKEEPER_CHECK: "Item_Boomerang"}, census, definitions.load(), gifts.load())
    assert {step.id for step in change.steps} == set(gifts.SHOPKEEPER_STEPS)
    assert change.new_flag is None
    flag = change.flag
    _, world = prepare(gifts.shopkeeper_spec(load_spec()), Settings())
    assert gifts.SHOPKEEPER_CHECK in gifts.seed_checks(world, census, definitions.load(), gifts.load(), load_actors())
    gamedata = read_romfs_byml(romfs, dicts, gifts.GAME_DATA_LIST)
    [saved] = [row for row in gamedata["Data"]["Bool"] if row["Hash"] == murmur3_32(flag.encode())]
    assert (saved["DefaultValue"], saved["ResetTypeValue"], saved["SaveFileIndex"]) == (False, 8, 0)
    path = change.steps[0].file
    changes = gifts.file_changes([change], {gifts.SHOPKEEPER_FLOW: path})
    assert set(changes) == {path}
    original = dicts.decompress(path, (romfs / path).read_bytes())
    before = evfl.read(original).flowchart
    after = evfl.read(changes[path](original)).flowchart
    flags = {}
    assert run_offer(after, flags, equipped=True) == ["Item_Boomerang"]
    assert flags[flag] is True
    assert run_offer(after, flags, equipped=False) == []
    assert run_offer(after, dict(flags), equipped=True) == []
    # Vanilla remains repeatable when its first-talk Bool is true; this is deliberately not patched globally.
    assert run_offer(before, {flag: True}) == ["Obj_Shield_Deku"]
    for step in change.steps:
        i = next(i for i, event in enumerate(after.events) if event.name == step.event)
        flags = {}
        assert run_offer(after, flags, start=i) == ["Item_Boomerang"]
        assert run_offer(after, flags) == []
    # Independently reverse only the allowed mutations; every other original event/actor/entry stays equal.
    restored = copy.deepcopy(after)
    for i, old in enumerate(before.events):
        if old.name in {"Event116", "Event117", "Event45", "Event24"}:
            restored.events[i] = copy.deepcopy(old)
    restored.events = restored.events[: len(before.events)]
    assert restored == before
