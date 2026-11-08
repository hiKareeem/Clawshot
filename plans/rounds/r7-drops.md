# Round 7, Track C: boss hearts and tokens (cs7c)

Branch `r7/drops`. Required instructions, plans 00–04, decisions and round-5/6 histories read.
No game, batch file, GUI, Hookshot build or terminal-control command run. Dump and save backups read-only.
Research and generated data live only under `E:/OOTRemake/work/r7-drops/`. No dependency change.

## Item 1: eight boss Heart Containers

Read-only executable probes: `probe_hearts.py`, `finish_heart_trace.py`, `decode_hearts.py`,
`decode_remaining.py` in the external research directory. Parsed the actual census, all eight Bancs,
GameDataList, native pickup packs and each heart's bound room logic. Build `e0f3ccfa`.

Every heart has **one AiGroup, one SimultaneousGroup and one FarDeleteGroup**. Its bound node is
`ActorLogicSimpleActor`; preserve its instance Id, Path, Reference, Hash and memberships when replacing Gyaml.
These are already scripted pickups, unlike the ungrouped heart piece in round 2. Presence is driven by
`Logic_Create`, not by changing the boss's drop table. Original positions/room/rotation remain untouched.

| Boss / Banc area | Heart Hash | Module suffix; heart node / gate node | Native creation gate |
|---|---|---|---|
| King Dodongo / DodongoCavern | 5936534468710061389 | BossBattle_75a7; 0 / 2 | `DodongoCavern_BossGroundChange` Bool |
| Volvagia / FireTemple | 9478330070473364248 | Room_26_80f5; 0 / 13 | `FireTemple_BossGroundChange` Bool |
| Phantom Ganon / ForestTemple | 18379569660496940670 | Room_22_c724; 0 / 7 | `SageOfForest_IsAfter_Step08_Exp` |
| Barinade / InsideJabuJabuBelly | 17608884438514432711 | Room_15_39e3; 3 / 8 | `Get_StoneOfWater_IsAfter_Step13_01_Exp` |
| Gohma / InsideTheDekuTree | 17948245526767051747 | Room_L_Common_865f; 0 / 14 | `Gohma_DefeatBoss` Bool |
| Bongo Bongo / ShadowTemple | 17599164808183510748 | Room_B3FB4F_Q_f38f; 0 / 1 | `SageOfShadow_IsAfter_DefeatBoss_Exp` |
| Twinrova / SpiritTemple | 4720088048159616469 | Room_34_90de; 1 / 0 | `SageOfSpirit_IsAfter_Step09_01_Exp` |
| Morpha / WaterTemple | 14426685265732353862 | Room_23_eb85; 11 / 12 | `SageOfWater`, after `Step07_2` (`HoldChallengeCurrentStepCheckOrder.IsAfter`) |

All eight actor Hashes are `Bool64bitKey`, reset **24**, save file **0**. The pickup base's
`ActorGameDataSetting` is `NoRespawn`; its AI is `DropItem.root` and actor logic is `ActorLogicSimpleActor`.
Gohma additionally deletes its heart on `InsideTheDekuTree_Heart_Container_Obtained`; its room graph sets
that Bool from the heart's death-related signal. Keep this native wiring; do not mark the boss quest complete
or invent a heart-granted flag. The other seven heart nodes' Logic_Delete/RespawnTrigger use false defaults.
A saved Hash existing is not proof a changed pickup sets it: Save/Continue acceptance remains Kareem's.

### Native restriction proposal

Reuse the existing world kind **BossHeart** (census kind **heart_container**); off by default. Initial native
palette: `Obj_Heart_Container`, `Obj_Heart_Piece`, `Obj_Shield_Deku`, `Obj_Shield_Hylian`, `Obj_Rupee_Red`.
The two shields and red rupee have already worked as freestanding pickups (section 11); the heart piece is
native. All inherit `Obj_Item_Base`, `NoRespawn`, `DropItem.root`, `ActorLogicSimpleActor`. Inventory-only
`Item_Boomerang` etc are not pickups. Exclude `Obj_Arrow_Fire`: its earlier crash is real; merely retaining
an unrelated boss group does not reproduce its own object/script group. No arbitrary Obj_* allowlist.

**Kareem/reviewer: approve this native-only BossHeart palette, analogous to D21, subject to the King Dodongo
persistence check.** No boss reward (stone/medallion), blue warp or quest gate is shuffled by this track.

### Save checkpoint

Read all six `progress.sav` copies under
`E:/OOTRemake/work/save-backups/2026-11-08_1114-main-dodongo/save/5a3c9e1f0b7d24680000000000000001/`.
All: child, Fire quest `DungeonStart` (580975620), heart Hash unset, `DodongoCavern_BossGroundChange=false`,
`HavePlayedEvent.Dm_DodongoCave_BossOut=false`; no acquired Hylian Shield, acquired Deku Shield.
This is a suitable pre-boss checkpoint, not a completed-heart save. Item 2 will copy only that nested user's
save contents outward to its own isolated user, never the source and never the live user.

### Diagnostics / coordination

The unmodified external GPL AINB decoder decoded all eight boss modules. It failed on the heart event AI's
expression string-pool warning (`ParseWarning.__init__` missing `msg`). Printed filenames, byte lengths and
headers; skipped only those event graphs, not a failed boss module; no decoder source modified/copied.
The eight Logic_Create contracts above come from successfully decoded room graphs, not that failed parse.

First thread post command returned exit 1: `bermuda: no thread cs-r7`. No unchanged retry or prohibited thread
creation. This report retains the intended post: Track C ordered work and isolated shared commits; section 27
waits for sections 25/26. No other track's files edited. Python LSP unavailable (only marksman configured).

## Pending ordered items

2. King Dodongo safe-pickup output and isolated launcher, including Save/Continue checklist.
3. Keep native token callback while changing grants, if supported by data.
4. Default-off BossHeart seed integration for reviewed native pickups.

Section 27 will be appended after sections 25/26 on an authorized integrated base; this file holds its source
material meanwhile. No out-of-order section or placeholder is added to the shared research file.
