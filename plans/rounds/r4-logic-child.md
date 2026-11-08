# Round 4, track A: remake logic, child areas (cs4a)

Branch `r4/logic-child`. Owns `src/clawshot/world/load.py` (item 1 only), `src/clawshot/data/world/remake.toml`,
`src/clawshot/data/world/remake/child_*.toml`, `tests/test_world_remake*.py`, this file and section 12 of
`plans/03-game-data.md`. Scratch scripts (read only on the dump) and decoded data: `E:/OOTRemake/work/r4-logic-child/`.

## Item 1: overrides in several files (9c4abf0)

`load_spec` applies `remake.toml`, then every `remake/*.toml` sorted by name (`load.apply_overrides`). Tables:
`[locations]` (as before, plus `region` to move a location), `[regions]` (a region the translation lacks),
`[exits."<region>"."<target>"]` and `[events."<region>"."<event>"]` (`rule` with `was`, or with `new = true`),
`[key_counts]`. One location, exit, event, region or key count set in two files stops the build, naming both files.
Regions are added before anything else is applied, so a file may use a region from a file sorted after it. Format
written into `plans/04-world-format.md` ("Overrides"; that file had no round 4 owner, the format change is this
item's). Tests: `tests/test_world_remake.py` (files applied in order, a region from a later file, the same location
or exit in two files, a stale `was`, `new` on an existing exit, unknown tables and fields, missing source). Posted on
`cs-r4` at 19:52.

## Item 2: the Deku Tree (`remake/child_deku_tree.toml`)

Evidence: Kareem's round 3 seed 3 report (`00-roadmap.md`, "Round 3 result"); Nintendo Life, "Great Deku Tree
walkthrough" (Switch 2, 2026-11-05,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-great-deku-tree-walkthrough-switch-2); the placement files
(`InsideTheDekuTree_Static`/`_Dynamic`, listed by `E:/OOTRemake/work/r4-logic-child/actors.py`; output
`deku_all.tsv` there). Rooms are the actors' `DefaultDungeonRoomIndex`; heights are Banc `y`.

| Room | What the data has | What the guide says |
|---|---|---|
| 0 lobby | 1F web `Obj_InsideTheDekuTree_SpiderWeb_A_01` at y 100; map chest y 108 (2F); three `Enemy_Skullwalltula` at y 113-116 on the wall above the map chest; Skulltulas at y 127 (3F) | 2F by ladder or vines; the Slingshot shoots down the Skulltulas that block the vine wall to 3F; the basement is entered by jumping from 3F into the 1F web |
| 1 | `Enemy_Scrub_Deku`, shutter | reflect the nut with the shield |
| 2 Slingshot room | `FallingFloor_A_01/02/03` (y 110, at the entrance), `Obj_EyeSwitch_A_02` (y 114) and `FallingLadder_A_01` (y 116) above the entrance, Slingshot chest y 112, side chest y 116 | the floating platform breaks under Link; vines up to the Slingshot chest; shoot the switch above the entrance door to drop it and escape; the side chest is up the vines by the Slingshot chest |
| 3 compass room | compass chest y 120, side chest y 126, Gold Skulltula y 121, `Obj_StepSwitch_A_02`, three `ElevatorLift` platforms | floor switch raises three platforms to the alcove (Gold Skulltula) and to the compass chest; the side chest through a vent |
| 4-11 basement | eye switch in room 5, water room 6, torches 7, webs 8, scrubs 9, boss 10 | as N64 (OoT Randomizer's basement rules hold) |

Overrides (each with `source` in the file):

| Change | Rule |
|---|---|
| new region `Deku Tree Top Floor` (3F and the compass room) | entered from `Deku Tree Lobby` with `can_use(Slingshot)`; back down `True` |
| `Deku Tree Compass Chest`, `Compass Room Side Chest`, `GS Compass Room` | moved to `Deku Tree Top Floor`, rules unchanged |
| `Deku Tree Top Floor` -> `Deku Tree Basement` (new) | `here(is_adult or can_child_attack or Nuts)`, OoT Randomizer's condition for the way down (Deku Tree.json:20) |
| `Deku Tree Lobby` -> `Deku Tree Basement` | was `deku_tree_shortcuts or here(...)`, now `deku_tree_shortcuts` (the basement opens from 3F only) |
| `Deku Tree Slingshot Room` -> `Deku Tree Lobby` (new; OoT Randomizer's room has no exit) | `can_use(Slingshot) or can_use(Bow)` |

Checked and unchanged: the Slingshot room entry `here(has_shield)` (the scrub); both Slingshot room chests `True`
after the drop; the map chest `True`; the basement back room (an eye switch: Slingshot or Bow, and a fire source),
the ledge, the B2 web (torch and stick), the boss door (`has_shield`: the 2-3-1 scrubs), Queen Gohma (stun with
the Slingshot or nuts, then the sword).

Tests (`tests/test_world_remake.py`): on round 3's slice (Kokiri Forest, Lost Woods, Deku Tree, goal Queen Gohma),
the vanilla placement is beatable and the vanilla placement with the Slingshot and the basement chest's item swapped
(seed 3's case) is not; holding every other vanilla item of the slice, the compass chest, the compass room Gold
Skulltula and the basement chest are out of reach without the Slingshot and in reach with it, and the map chest and
both Slingshot room chests are in reach without it.

**Getting out of the Slingshot room without the Slingshot.** The exit in logic does not change what is reachable
(the lobby is reached before the room), so it only records the trap. Nothing in the data shows a way out besides the
eye switch: the only "return to entrance" flow is the Wallmaster's (`Enemy_Wallmaster_ReturnToEntrance`), and room
2's only other actors are the vines, a Skullwalltula and the chests. Farore's Wind would work, but no child holds it
this early.

- **Kareem: in the Slingshot room without the Slingshot (seed 3), how did you get out? Does saving and quitting (or
  a game over) and continuing put Link at the Deku Tree's entrance, as on N64?**
- If it does, the room is no trap: the rules above stand (enter with a shield, the chests open, reload to leave).
- If it does not, proposal: the room's entry asks for the Slingshot too (`here(has_shield) and can_use(Slingshot)`
  on `Deku Tree Lobby` -> `Deku Tree Slingshot Room`), so the logic never sends a player in without it; a seed then
  never puts the Slingshot in either of the room's chests, and the vanilla-placement test must accept that
  (vanilla is then out of logic). A player can still walk in early, so the better fix is a placement patch that
  leaves the ladder down (`Obj_InsideTheDekuTree_FallingLadder_A_01`) or the platform whole, for an in-game test.
- **Kareem: can the Boomerang (child), or the Bow or Hookshot (adult), clear the Skullwalltulas on the lobby's vine
  wall to 3F?** Until then only the Slingshot opens 3F, so an adult never reaches 3F or the basement in logic.
