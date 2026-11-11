# Round 12: physical dungeon-area constraints (cs12c)

Initial base: main `9f86b3a`; rebased without conflicts onto main `cd81449` at
Claude's request after PR #3 merged. Branch `r12/areas`; scope requested by
Kareem, 2026-11-11.

## Incident and decision

Kareem played published 0.1.1 community seed 11 at 12:41–12:47 on Hookshot 2.1.0.
Its Spirit Silver Gauntlets and Mirror Shield chests contained Spirit small/boss keys.
Both actors live in `Banc/DesertColossus`, not `Banc/SpiritTemple`. The reported
post-Save/Quit save leaves Spirit at 0/0/false with no boss key, while both chests
are open. This is authoritative played evidence; no game or save-check rerun here.
Round 11's played overworld small-key loss and section 44's handler trace explain
why generic actors cannot be placed by logical dungeon membership alone.
Incident artifacts (all read-only): `E:/OOTRemake/work/r11-release/candidates/seed-11/`;
checker `E:/OOTRemake/work/r12-spirit-hands/check_saves.py`; saves
`E:/OOTRemake/work/save-backups/2026-11-11_124548-r12-spirit-hands-2/`.

Implemented (cs12c, as requested): retain logical own-dungeon membership
and additionally require the location's physical Banc area to match its dungeon
region's own area, inside the fill predicate shared by restrictive fill and safe
swaps. No post-fill repair; every returned seed still passes the beatability oracle.
`dungeon_items` currently accepts only `own_dungeon` and `anywhere`; there is no
`vanilla` mode to modify. Unshuffled checks retain their actual vanilla items.
No version/lockfile change; Claude bumps the version at merge because output changes.

## Audit

Static audit joined every dungeon region's classification with the committed census
physical `area`, including all twelve dungeon files, remake-only regions and the
Tower metadata override. Exactly two live own-dungeon destinations are outside
their dungeon's Banc:

| Dungeon | Location / actor Hash | Logical region | Physical area | Generic item attribution |
|---|---|---|---|---|
| Spirit Temple | Silver Gauntlets Chest / `2490063409521505179` | Spirit Temple Central Chamber | `DesertColossus` | Spirit small key, boss key, map or compass was permitted. Small key loss is played; no Spirit small-key counters changed. Boss/map/compass handlers use the same standing-dungeon resolution (section 44); map/compass loss here remains static inference. |
| Spirit Temple | Mirror Shield Chest / `10012167258643363548` | Spirit Temple Beyond Anubis Room | `DesertColossus` | Same four families were permitted. Boss key loss is played despite its indicator; no Spirit boss-key flag changed. Small/map/compass attribution follows the same static handler evidence. |

The actual inside Statue Room Hand Chest (`2203243501006528435`) is in
`SpiritTemple`, not the exterior statue hands, and remains eligible.

| Dungeon audited | Own physical area | Outside destinations |
|---|---|---|
| Deku Tree | `InsideTheDekuTree` | None |
| Dodongo's Cavern | `DodongoCavern` | None |
| Jabu-Jabu's Belly | `InsideJabuJabuBelly` | None |
| Forest Temple | `ForestTemple` | None |
| Fire Temple | `FireTemple` | None |
| Water Temple | `WaterTemple` | None |
| Shadow Temple | `ShadowTemple` | None |
| Spirit Temple | `SpiritTemple` | Two above |
| Bottom of the Well | `BottomOfTheWell` | None |
| Ice Cavern | `IceCavern` | None |
| Gerudo Training Ground | `GerudoTrainingGround` | None |
| Ganon's Castle and Tower | `InsideGanonCastle` | None |
| Gerudo Fortress / Thieves' Hideout | `GerudoFortress` | No shuffled key destinations: its four keys are unshuffled Collectable checks. |

Boss rooms and blue warps are in their dungeon's own Banc, not separate outside
areas. Untagged boss regions do not become generic own-dungeon destinations.
Tower is explicitly tagged `Ganons Castle` and shares `InsideGanonCastle`, so its
boss-key chest is correctly retained. BossHeart/Freestanding palettes exclude all
four generic families. The unshuffled Well/Shadow floor keys stay where they are.

`item_actors.toml` exposes exactly four generic current-dungeon actor families:
`Item_Dungeon_SmallKey`, `Item_Dungeon_BossKey`, `Item_Dungeon_Map`,
`Item_Dungeon_Compass`. The production chest pool disambiguates them using the
logical dungeon (`patch/plan.py:remake_vanilla`, `patch/items.py:ItemActors.item`).
Named Hideout keys, key rings and silver-rupee pseudo-dungeon items do not enter the
supported shuffled pool. Treasure Chest Game's room keys remain unchanged under
D17. Unqualified generic `Small Key`/`Boss Key`/`Map`/`Compass` logic entries have no
dungeon but are not production pool entries. No vanilla dungeon item was found
in a foreign-area check.

Sources: `data/world/port.toml` (all dungeon/Banc mappings and boss rooms);
`data/world/remake.toml` (both hand area overrides);
`data/world/remake/extra_ganon_tower.toml`; `data/locations.toml` (physical areas);
`data/item_actors.toml`; `plans/03-game-data.md` sections 18 and 44. Paths prefixed
with `data/` above are under `src/clawshot/`.

Direct probe `uv run python E:/OOTRemake/work/r12-dungeon-areas-cs12c/evidence.py`
validated **134** dungeon-tagged regions, one canonical own area for every dungeon,
exactly the two mismatches above, and **zero** world/census physical-area
disagreements. High confidence on the exhaustive mismatch list and the
standing-dungeon handler mechanism; played certainty remains limited to the
reported small/boss keys. `audit-results.json` and the read-only reproducer stay
under `E:/OOTRemake/work/r12-dungeon-areas-cs12c/`.

## Silver Gauntlets story event (note only)

Kareem observed the child cutscene while adult, including child-to-adult morphing.
Research is facts-only; no cutscene or story patch belongs to this track.

**This is not known to be cosmetic-only:** the retained chest wrapper requests a
Spirit quest step without checking Link's age. Confidence is high for the explicit
flow writes below, but whether a late request can rewind an already-later quest
step is unknown: the native challenge action's ordering semantics were not proved.
No regression or adult Nabooru break is claimed from the visual morph alone.

Existing, mutually corroborating sources: `plans/03-game-data.md` section 18
(lines 1035–1044), `plans/rounds/r5-seeds.md` (chest event audit), and
`src/clawshot/patch/chest_events.toml` entry `SageOfSpirit_NaboorIsTakenAway`.
Static cross-check: original round-1 decoded `SageOfSpirit` flow, build `e0f3ccfa`,
under `E:/OOTRemake/work/r1-research/decoded/evfl_all.json`.

| Flow/node | Effect relevant to story |
|---|---|
| `SageOfSpirit:SageOfSpirit_NaboorIsTakenAway`, `Event64` | Calls `Dm_SY_Treasurebox`, which grants the current `ContentName`, not a second Silver Gauntlets grant. |
| `SageOfSpirit/Event1` | Plays `Dm_DesertColossus_0030`, Nabooru taken away. |
| `SageOfSpirit/Event190`, `Event322` | Clears `HavePlayedEvent.NaviTips_Gauntlet_01` and `HavePlayedEvent.NaviTips_Gauntlet_03`. |
| `NaviChat:NaviChat_Serious` | Sets `NaviChat_Serious_Time=true` during the subsequent Navi talk. |
| `SageOfSpirit/Event21` | Calls `EventExecuteProgressChallengeStep` for `SageOfSpirit`, `Step07`, with `IsIgnoreCompletedChallenge=true`; follows with quest progress UI. |

An adult opening can therefore invoke the same Spirit-story progression request as
a child opening (high confidence: no age branch in this wrapper). Later adult
Nabooru progression has separate `Step08` / `Step08_01` writers; completing Spirit
has its own later writers. Whether the Step07 request skips prerequisite staging or
is ignored after a later step requires the challenge handler/AINB or a controlled
play check; it is not resolved by the EVFL action name “Progress”.

The same focused direct probe read the actual dump with the current
`clawshot.formats.evfl` parser: **18** reachable wrapper nodes, no duplicate event
names, and no age branch or age setter. Event indices are preserved; the older
decode's apparent duplicate labels were not reproduced by the current parser.

It also decoded `Event/EventFlow/Dm_DesertColossus_0030.bfevfl.zs` and its `_Effect`
and `_Env` subtimelines: respectively **150 / 33 / 20** clips. The main timeline's
six `Player_Event.EventPlayASForTimeline` clips explicitly request child
animations (`C01/C02/C07/C14/C15/C17-Player_Child-A-0`). The other actions are
camera, dialogue/voice, character animation, fade, effects and environment palette;
none explicitly writes game data, changes age, grants inventory or progresses a
quest. **[INFERENCE, medium confidence]** the child animation requests explain the
visual morph; this does not prove the animation handler cannot affect transient
player presentation internally. No persistent age write was found in either the
wrapper or these timelines.

Decoded trees are external only (`story-results.json` in the scratch root).
The initially queued probe was cancelled for Claude's 14:09 gate-order request;
the final probe was a single focused data-only readback with **no lock acquisition**.
No event, cutscene, story flag, save or game output was changed by this research.

## Verification

- Before fix: `CLAWSHOT_WORKERS=1 uv run pytest tests/test_generate_dungeon_areas.py -x -q`:
  failed on `SmallKey`, printing `Outside.area='OverworldArea'` while its logical
  region belonged to Temple (`area='TempleArea'`); old `allowed()` returned true.
- After the physical-area change: `CLAWSHOT_WORKERS=1 uv run pytest tests/test_generate_dungeon_areas.py -q`:
  **7 passed** (5.27 s). Synthetic outside checks cover small keys, boss keys, maps
  and compasses, an inside positive control, synthetic anywhere compatibility,
  actual Spirit hand restrictions and a beatable seed 11 using defaults.
  The final seed-11 test was strengthened to a `dump` regression using the actual
  community shuffle recipe (Chest/Shop/Gift/Scrub/BossHeart) through Gift setup and
  `make_seed`, rather than a defaults-only seed. It asserts item attribution, not
  incidental filler choices; the full dump gate below covers that final form.
- `_in_dungeon_area()` is the only new fill helper. `allowed()` shares it across
  restrictive fill, return-kit placement, fill-time safe swaps and restricted filler.
  Existing area-less synthetic worlds keep their logical policy (`None == None`).
- `docs/settings.md`: one plain sentence explaining the hand-chest exclusion;
  no READ ME FIRST, project version, lockfile or settings schema changes.
- Initial `tasklist /FI "IMAGENAME eq hookshot.exe"`: no game process. All pytest
  runs conservatively use `CLAWSHOT_WORKERS=1`.
- All four full gates passed serially through the shared gate lock; both sweeps passed below.
  Initial `mkdir` and the required 60-second retry reported an existing lock.

### Full gate commands before the rebase

All pytest commands use `CLAWSHOT_WORKERS=1`. `TEMP`, `TMP`, `TMPDIR` point to
`E:/OOTRemake/work/r12-dungeon-areas-cs12c/tmp`; decoded fixtures/output never go
into a worktree or the player's dump. The wrapper removes its lock in `finally`
after each command. Its initial waiting-only launches were cancelled/restarted
to isolate temporary files and remove a queue-time deadline; no test was stopped
or rerun unchanged.

| Command | Result |
|---|---|
| `uv run ruff format --check` | Exit 0; 304 files already formatted |
| `uv run ruff check` | Exit 0; all checks passed |
| `CLAWSHOT_WORKERS=1 uv run pytest` | Exit 0; 975 passed, 128 skipped; 1097.42 s |
| `CLAWSHOT_WORKERS=1 uv run pytest -m dump` | Exit 0; 126 passed, 977 deselected; 3814.32 s |

Dump environment: `OOT_ROMFS=E:/Games/Hookshot/romfs`,
`OOT_NUP=E:/Games/Hookshot/The Legend of Zelda Ocarina of Time [0400486024DEC000][v131072].nup`,
`OOT_DUMP=E:/OOTRemake/work/pr1-check/dump`.
Logs: scratch `gates-0.log` through `gates-3.log`; all four exit codes are recorded
in `gates-commands.json`. The final community-recipe regression passed in the dump
gate. The synthetic run's 128 skipped cases are not claimed as native passes;
the separate dump run selected and passed all 126 dump-marked cases.

### Post-rebase integration verification (`cd81449`)

`git rebase main` replayed all eight commits without conflicts. The new base does
not change fill, world or item data. Its relevant output-side changes are the
supported-input error wording and ignoring macOS metadata in folder digests.

- With the same ROMFS/temporary-directory environment above:
  `CLAWSHOT_WORKERS=1 uv run pytest tests/test_generate_dungeon_areas.py -q`:
  **7 passed in 22.39 s**, including the actual community-recipe dump regression.
- `CLAWSHOT_WORKERS=1 uv run python E:/OOTRemake/work/r12-dungeon-areas-cs12c/rebase_smoke.py`:
  actual full-string seed-11 generation/write completed in **52.09 s**, into
  fresh `seed11-rebased-cd81449/` under the scratch root. Independently read back
  all four child/adult hand-chest copies; actor contents match the plan.
  Rewards remain Rupees (20) and Bombs (5); the full output digest remains
  `04edec972126b9b9ba0f67e1cadb001f191813118ce0fb47ece88a9677a94f91`.
  `rebase-smoke.json` records the result.

The full-suite and 100-seed sweep results above precede the rebase; they were not
rerun afterward. Post-rebase proof is the focused native regression file and the
fresh full output/readback smoke. No new full-gate or sweep worker was started.

### Locked 50 + 50 seed sweep

`uv run python E:/OOTRemake/work/r12-dungeon-areas-cs12c/gate.py sweep`
completed successfully, one process, shared lock released in `finally`.
Seeds 1–50 for each settings set, actual census-derived chest pool and the same
Gift/Scrub preparation as production; no output folder was written for the sweep.
Each new fill passed its normal oracle plus a fresh `check_beatable` search, and
every placed dungeon item was checked against the physical area invariant.

| Settings | Beatable | Outside-area dungeon items | Changed outputs |
|---|---:|---:|---:|
| Defaults | 50/50 | 0 | 50/50 |
| Community seed 11 full shared string | 50/50 | 0 | 50/50 |

Comparison used the same code/data/settings with only the old logical-only
`allowed()` predicate emulated, then the fixed predicate. All 100 placements and
serialized spoilers differ; because `spoiler.json` is part of every output,
all 100 output folders would change. This count is not a claim that 100 full
mod folders were written. Full native seed 11 was actually written and read back.

Reproducers/results: `sweep.py`, `sweep-0.log`, `sweep-results.json` and
`sweep-commands.json` under the scratch root. Wrapper elapsed 1422.25 s includes
three one-minute lock waits. No pool or second sweep ran concurrently.

### Community seed 11 output smoke

Replayed the full string from `work/r11-release/seed11-share.txt` through the CLI's
existing Gift setup and `make_seed`/`write_seed`. New output only:
`E:/OOTRemake/work/r12-dungeon-areas-cs12c/seed11-fixed/`.

| Hand chest | New item | Written actor |
|---|---|---|
| Silver Gauntlets | Rupees (20) | `TBox_Rupee_Red` |
| Mirror Shield | Bombs (5) | `Item_BombBundle_Small` |

`uv run python E:/OOTRemake/work/r12-dungeon-areas-cs12c/sweep.py seed11` completed
in 66.28 s; the generator's beatability oracle passed before writing.
`tree_digest` (SHA-256, paths and all file contents including spoiler/play note):
`04edec972126b9b9ba0f67e1cadb001f191813118ce0fb47ece88a9677a94f91`
(share hash `04EDEC972126`).
This is the cs12c pre-merge output, still labelled 0.1.1 as instructed; the version
bump and other merged output-text changes require a fresh final release digest.

Independent read-back smoke decoded all four written chest copies (child/adult):
both items match the plan, neither is generic dungeon loot, and the unchanged
story overrides remain `SageOfSpirit_NaboorIsTakenAway` / `SageOfSpirit_GetShield`.
The written spoiler has no dungeon-item physical-area violations. This is file
and logic proof, not a new in-game test.

Scratch failure diagnosed before retry: the shared string has expanded
`Boss/Cutscene/NPC/Song` shuffle types, not the `Gift` alias. My first replay driver
checked only that alias and omitted Gift preparation, causing `Buy Magic Bean`
to have zero allowed destinations. Printed full settings and the false condition,
then changed the driver to the existing CLI's expanded-type condition; one corrected
run succeeded. No production change was needed for this scratch-only mistake.

### Player follow-up (not run by the agent)

The new seed output is not a repair for an existing seed 11 save: placements change
and the opened hand chests are already consumed. Do not replace the published
candidate or point a played save at this changed recipe.

**Kareem: on an isolated new playthrough generated from the merged build, confirm
the hand rewards match its spoiler, remain collected after Save and Quit, and the
seed finishes; record the Hookshot `mods: Banc/DesertColossus/... <- ...` loading
line.** The pre-merge scratch output above gives 20 rupees / 5 bombs, not keys.
Use only Teleport/clock cheats if needed; do not edit inventory/story/age flags.
Native own-dungeon key persistence already has the round-11 Deku/Fire controls;
this track adds placement safety, not a new grant implementation.

## Handoff

Rewritten branch commits before this rebase-handoff update:

- `2052857`: incident and scope record.
- `b77f1f7`: physical-area helper, regression coverage, one settings-doc sentence.
- `f878469`: Spirit story effects and limits.
- `0ebe866`: exhaustive own-dungeon destination audit.
- `b935dd8`: both sweeps and changed-output counts.
- `cdf2001`: seed-11 regression uses its actual community shuffle recipe and dump pool.
- `97f5c49`: direct world/census join and index-faithful Spirit timeline proof.
- `116f396`: original passing full-gate evidence and handoff.

All three original jobs and all four mandatory gate commands completed; their
sequence released its lock and completion was posted at 15:30. Claude then
reported `review-pr3 gates done`, PR #3 merged and normal one-full-run-at-a-time
gate use restored. The requested rebase is now complete and verified above;
cs12c has no pending worker or lock requester.

Integration surface: one private helper plus the final return in `allowed()`,
one separate regression file, one conditional sentence in `docs/settings.md`,
and this record. The sentence explicitly describes own-dungeon placement, not
the named small-key Anywhere mode being developed by cs12b.

After merge: Claude bumps the project version; Kareem performs the new-seed
in-game check above. Adult Nabooru quest-step ordering remains an explicit
research limit, not an event change or a claim of a reproduced story regression.
No game launched, played output/save modified, merge or push.
