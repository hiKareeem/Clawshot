"""Repair only missing native grant paths; native placements and working grants stay native."""

from dataclasses import replace

import pytest
from test_key_model import (
    CENSUS,
    DEFINITIONS,
    EVENTS,
    FIRE_BOSS_KEY,
    FIRE_COMPASS,
    FIRE_KEY,
    FIRE_MAP,
    TABLE,
    VANILLA,
    world_spec,
)

from clawshot.generate import Seed, Settings
from clawshot.patch import items as item_actors
from clawshot.patch.key_targets import DungeonGrant
from clawshot.patch.plan import PatchError, link, make_plan
from clawshot.patch.write import patch_tree
from clawshot.world import build_world


def planned(item, kind, *, actor=None, event=None):
    world = build_world(world_spec())
    chest = next(c for c in CENSUS if c.id == 501)
    chest = replace(chest, actor=kind, vanilla_item=actor or chest.vanilla_item, event=event)
    census = [chest if c.id == chest.id else c for c in CENSUS]
    links = link(world, ["Fire Key Chest"], DEFINITIONS, census)
    placements = {**VANILLA, "Fire Key Chest": item}
    seed = Seed(world, 1, Settings(), placements, ["Fire Key Chest"], [list(placements)])
    return make_plan(seed, links, TABLE, EVENTS), chest


@pytest.mark.parametrize("item,family", [(FIRE_MAP, "Map"), (FIRE_COMPASS, "Compass"), (FIRE_BOSS_KEY, "BossKey")])
@pytest.mark.parametrize("kind", ["Obj_TBox_A_01", "Obj_TBox_A_06_NoBake", "Obj_TBox_GlassTruth_A_01"])
def test_missing_small_chest_ownership_requires_a_bound_grant(item, family, kind):
    plan, chest = planned(item, kind)
    (change,) = plan.changes
    assert change.dungeon_item == DungeonGrant("FireTemple", family)
    tree = {"Actors": [{"Gyaml": kind, "Hash": chest.id, "Dynamic": {"Drop__DropActor": chest.vanilla_item}}]}
    with pytest.raises(PatchError, match="no grant binding"):
        patch_tree(tree, chest.files[0], plan)


@pytest.mark.parametrize("item", [FIRE_MAP, FIRE_COMPASS, FIRE_BOSS_KEY, FIRE_KEY])
@pytest.mark.parametrize("kind", ["Obj_TBox_A_02", "Obj_TBox_A_03_NoBake"])
def test_big_chest_already_has_the_native_dungeon_grant(item, kind):
    plan, _ = planned(item, kind, actor="TBox_Rupee_Blue")
    (change,) = plan.changes
    assert change.dungeon_item is None
    assert change.named_key is None
    assert change.key_event is None


def test_moved_own_small_key_keeps_native_pouch_grant_and_demo():
    plan, _ = planned(FIRE_KEY, "Obj_TBox_A_01", actor="TBox_Rupee_Blue")
    (change,) = plan.changes
    assert change.dungeon_item is None
    assert change.key_event is None


@pytest.mark.parametrize("item", [FIRE_MAP, FIRE_COMPASS, FIRE_BOSS_KEY, FIRE_KEY])
def test_native_placements_need_no_new_binding(item):
    plan, chest = planned(item, "Obj_TBox_A_02", actor=TABLE.actor(item))
    assert plan.changes == []
    assert plan.unchanged == [("Fire Key Chest", chest.id)]


def test_ganons_castle_boss_key_uses_the_boss_key_saved_field():
    spec = world_spec()
    item = "Boss Key (Ganons Castle)"
    spec["items"][item] = {"type": "GanonBossKey"}
    world = build_world(spec)
    chest = replace(
        next(c for c in CENSUS if c.id == 501),
        area="InsideGanonCastle",
        vanilla_item="TBox_Rupee_Blue",
    )
    links = link(world, ["Fire Key Chest"], DEFINITIONS, [chest])
    seed = Seed(world, 1, Settings(), {"Fire Key Chest": item}, ["Fire Key Chest"], [["Fire Key Chest"]])
    plan = make_plan(seed, links, item_actors.load(), EVENTS)
    (change,) = plan.changes
    assert change.dungeon_item == DungeonGrant("InsideGanonCastle", "BossKey")
    assert change.dungeon_item.field == "DungeonInfo.InsideGanonCastle.IsGetBossKey"
