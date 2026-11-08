# Round 6, Track F: findings from play (cs6f)

Branch `r6/play`. Required worktree instructions, plans 00–04, decisions, all round-5 round files and
round 4's child-logic report read before edits. Round-6 opening/shared-file rules followed. No dependency
change, game/window/launcher run, dump/save write, merge or push. Research lives outside the repository at
`E:/OOTRemake/work/r6-play-cs6f/`; dump build `e0f3ccfa` is read-only.

## Item 1: Deku Tree weapon alternatives

Source: Kareem in game via Claude, 2026-11-08, `seed-shop-7`, Hookshot 2.0.1: Boomerang activates the
Slingshot-room exit switch, clears the lobby vine-wall route to 3F and stuns Gohma. These are supplied
player observations, not a new agent game run.

Read-only `probe.py` parsed both Deku Banc files and the shop flow; `switches.py` parsed the eye-switch,
Skullwalltula and boss packs and inspected existing decoded room modules. Room 0's vine blockers are
Skullwalltulas 2729587378952040865, 16183956171357380613 and 3995458350586152163 (y 113–116).
Room 2 eye 9080063866993537303 drives the ladder 2096903280161003875 via
`InsideTheDekuTree_Level_Room_C_Prefab_efa7`: node 6's first-on output starts node 8's event, whose
Bool participates in node 14's ladder trigger. Room 5 eye 10433048972954508847 is the same
`Obj_EyeSwitch_A_02`, with no placement weapon override; `...Room_F_Prefab_bdf4` node 8 likewise
starts its event from first-on. Therefore the same Boomerang switch response is applied to the basement
eye too; fire for the web remains required. This is data-backed shared-actor behavior, not a claim that
Kareem separately tested room 5. Boss Hash 15302759724049838417 is `Enemy_DungeonBoss_Gohma` in room 10.

`child_deku_tree.toml`: Slingshot or Boomerang for 3F; add Boomerang to both eye-switch routes and the
Gohma stun alternatives. Preserve Bow where already allowed, jumpslash damage, fire and Deku Shield
scrub requirements. Adult Bow/Hookshot vine traversal and unarmed room recovery remain unverified.

First targeted run: 30 passed, 2 failed in new tests. Printed counts/reached regions showed the test
start region enabled both ages (adult Nuts could beat Gohma), and the stick name was incorrectly plural.
The test start now gates on the requested starting age; the real item is `Deku Stick (1)`. No production
rule was weakened to satisfy the tests. The edit response also exposed a replaced test declaration;
restored it before execution. Corrected targeted result and live smoke follow in the next checkpoint.

Checkpoint: `uv run pytest tests/test_world_remake.py tests/test_world_remake_play.py -q`:
**32 passed**. Scoped ruff format/lint passed (2 files). Actual `load_world()` / `Search` smoke with sword,
Deku Shield, Boomerang and one stick reached 3F, basement, basement back room and Gohma as child;
`Defeat Queen Gohma = True`, `Slingshot held = False`. Full gates reserved for the branch handoff,
before any commit is posted as ready.

## Item 2: shallow castle moat

HF01 source: Kareem in game via Claude, 2026-11-08: the moat is shallow; no Silver Scale is needed.
The current rules already agree: both `HF Ocarina of Time Item` and `Song from Ocarina of Time` are
`is_child and has_all_stones`. No scale requirement was present to remove. Kept the rules intact and
recorded the confirmation beside the child-field rules, rather than adding a duplicate override for the
item already owned by `remake.toml` (`vanilla_fixed`). Read-only placement inventory identifies
`Obj_Ocarina_Time_A_01` Hash 2802436684568022035 at (16,145,43), Child Static.

`uv run pytest tests/test_world_remake_play.py -k moat -q`: **2 passed, 8 deselected**: both checks
work with three stones and no scale, not two stones, and not as adult. First full-world smoke had not
opened the forest exit: printed child frontier ended in Kokiri/Lost Woods. Supplying the actual
`Defeat Queen Gohma` event opened the path and both moat checks became reachable with scale false.
Ruff printed one required assertion-line join; applied that exact formatting correction.
