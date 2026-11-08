# Round 5, track A: age travel (cs5a)

Branch `r5/age`. Dump and save backups read-only; no game, launcher, window or terminal-control command run.

## Item 1: the age-change gates

Read AGENTS.md, README, plans 00–04, decisions and all four round-4 reports before changes.
Research scripts and decoded observations stay in `E:/OOTRemake/work/r5-age/`.

- `DoorOfTime:DoorOfTime_CheckStoneNum`, Event38/Event39/Event56, reads
  `Get_StoneOfFire_IsCompleted_Exp` and `Get_StoneOfWater_IsCompleted_Exp`, not stone inventory.
  The normal route already completed the Deku Tree. The escape/moat/song sequence advances `Step_DoorOfTime`.
- `DoorOfTime:DoorOfTime_OpenDoor`, Event27, calls `Dm_SY_Ocarina:PlayOcarinaSequence` with `MelodyType = 4`.
  Event60 requires `DoorOfTime_IsAfter_Step04_Exp` (quest beyond Step04); Event69 requires the door not already
  opened; Event58 requires `Dm_TimeTemple_0010` not already played; Event28 checks the recommended melody.
  Event17 runs the door scene and Event53 sets `Market_Child_TimeTempleDoor_Opened = true`, then Event57 moves
  the quest to Step06. Thus the vanilla route needs the three stone quests, moat Ocarina of Time and Song of Time;
  **the flow does not independently test Ocarina of Time inventory or the three stone items**. Keep round 4's
  conservative door rule for chest-only seeds; gifts shuffled independently need story-gate review (posted).
- `Market_Child_Prefab_e700` links attention actor `Obj_TimeTemple_MasterSword_A_01_e482` to two requests:
  DoorOfTime exactly Step06 for the first pull; AllSage after Ready for later pulls. `DoorOfTime:DoorOfTime_Draw`
  Event23 chooses the first-pull route unless `HavePlayedEvent.Dm_TimeTemple_0040` is set; Event99 plays
  `Dm_TimeTemple_0030`, which displays the sword; the SageRoom chain grants it and sets adult era.
- **Returning really is gated by Forest completion.** `Market_Adult_Prefab_89da` node 0 reads
  `SageOfForest_IsCompleted_Exp`; node 1 inverts it; node 2 feeds that into `Logic_Delete` of
  `Obj_TimeTemple_MasterSword_A_01_b347`. Its `ReceiveDoAction` drives the adult-to-child request.
  `Market_Adult_Prefab_edc2` also ANDs the same expression with the arrival area to trigger Sheik's scene.
- GameDataList: `SageOfForest_IsCompleted_Exp` is an unsaved `BoolExp`, Hash 1371974465, operands the Enum
  `Step_SageOfForest` (Hash 2841849034) and `Complete` (Hash 1275749364). Its meaning is quest-completed,
  not owning Forest Medallion or learning Prelude. `Dm_SY_BancChange_EscapeDungeon` Event199 sets that quest
  Complete: the boss/blue-warp completion route, not a shuffled medallion.
- `Market_Adult_Field_AdultToChild:Market_Adult_Field_AdultToChild` plays `Dm_TimeTemple_0070`, swaps equipment,
  Event1 sets `Sequence_IsChildhood = true`, Event0 reserves child Market, boot event `Dm_TimeTemple_0075`.
  Event3 only then reads `Market_Adult_Firsttime_GobacktoChild`; Event9 sets it. This is history, **not unlock**.
  It also refuses while a minigame timer is counting; timer/trade expiry is not represented by existing logic.

Source corroboration (facts only, no guide text copied):
https://www.nintendolife.com/guides/zelda-ocarina-of-time-forest-temple-walkthrough-switch-2
("Where to go after the Forest Temple"): after Forest, return to the temple, learn return travel and Prelude.
The actual pedestal's dependency is Forest quest completion, not Prelude inventory.

### Save evidence and missing prerequisite

Read all twelve `*/slot_*/progress.sav` under the two supplied backup directories with `clawshot.save`.
Every one has `Sequence_IsChildhood = true`, `Step_SageOfForest = Ready`, both
`HavePlayedEvent.Dm_TimeTemple_0040` and `Market_Adult_Firsttime_GobacktoChild = false`.
DoorOfTime is NotReady or Step02. These are child saves, not the current adult playthrough; no current live save
was read while Kareem plays. **Kareem: provide a new read-only adult save backup, before and after the Forest
blue warp if available, to corroborate `Step_SageOfForest` and the return pedestal in game.**

One research command failed on a nonexistent guessed `Market_Adult.bfevfl.zs`; the exception printed the exact
missing path. The asset listing showed only the two era-transition files, removed the nonexistent input,
and the aimed rerun completed. No game or save bytes were written.

## Cross-track notes

- Posted the real Forest gate and child-only backup evidence on `cs-r5`.
- Gift owners: the Door of Time reads stone quest progress, not stone inventory; independent stone/song shuffling
  must preserve those story gates. The age-return gate likewise uses boss/blue-warp completion, not the medal.
- Item 4 investigation: no independent return-unlock Bool was found. `Market_Adult_Firsttime_GobacktoChild` cannot
  open it. Forcing `Step_SageOfForest = Complete` would falsely complete the entire Forest quest and affect every
  other reader; it is not a safe free-travel flag. This is a conditional spec prerequisite, not permission to
  ship an ineffective flag or silently mark Forest completed. Requesting reviewer direction on an isolated
  data/logic patch instead; continue with the default gated search and softlock proof.
