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
creation. Read-only store diagnostics show threads through `cs-r6`, but no `cs-r7`; HOME/USERPROFILE are
`C:\Users\hi`, no BERMUDA override. Intended posts are retained here. Python LSP unavailable (marksman only).

## Item 2: King Dodongo test output

Item 1 committed as `7fa2c15`. `patch/drops.py` now replaces native heart Gyaml by stable saved Hash;
refuses non-pickups/Fire Arrows, stale or duplicate actors, missing native logic binding and missing/duplicate
group memberships. All copies change together. No AI, save table, boss, quest, warp or position edit.

Output: `E:/OOTRemake/work/r7-drops/ingame/dodongo-heart-hylian/`.
Launcher: adjacent **`Test - dodongo-heart-hylian.bat`**, copied from the approved `talon-boomerang`
template, never run. Its own `user-dodongo-heart-hylian`, bin executable only, updater disabled, missing-exe
hard stop. Its source is the **nested user save contents** of the King Dodongo backup, not the whole backup
root (which would accidentally add another `save/<user>` nesting). All source-file SHA256 values unchanged.

Only `DodongoCavern_Static.bcett.byml.zs`: decompressed **149088 -> 149084**, compressed
**44503 -> 43428**, original/effective allocation **149352**. Exact inverse-tree diff restores equality
after changing only the heart Gyaml back. No resource table needs writing. `verification.json` records it.

**Kareem:** follow `ingame/dodongo-checklist.md`: defeat King Dodongo normally; no early reward; Hylian
Shield at the heart's native spawn, shield notice/inventory and no added maximum heart; uncollected reward
survives Continue if practical; collect/save/Continue/re-enter, no duplicate. The overlay-open log plus
actual pickup and saved Hash must agree. Native blue-warp/Ruby progression stays untouched.
`ingame/check_dodongo_save.py` reads only the isolated test user's resulting saves.

Checks actually exercised:
- `uv run pytest tests/test_drops.py -q`: **14 passed**.
- `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_drops_dump.py -q -s
  --basetemp E:/OOTRemake/work/r7-drops/pytest-heart`: **1 passed**, all eight native heart identities.
- Scoped ruff format/lint passed (three Python files).
- `uv run python E:/OOTRemake/work/r7-drops/build_dodongo.py`: real writer/compression/readback,
  allocation, inverse-field diff, unchanged-backup SHA256 and static launcher checks **passed**.
  This is data proof, not gameplay certification. Full four gates run before a ready/handoff post.

## Item 3: retain the native token and its callback

Item 2 committed as `1f99ee4`. The native token has a real grant indirection:
`Component/PouchContentParam/Obj_Token_Gold...bgyml.PouchActor` ->
`Work/Actor/Item_Token_Gold.engine__actor__ActorParam.gyml`.
Changing it to `Item_Boomerang` keeps the actor **Obj_Token_Gold**, its native AI and
`OneShotGoldTokenDeadAfter` byte-identical. The enemy's `GoldTokenGmdHash` overwrite is untouched.
This supports a controlled grant experiment without replacing the pickup actor or copying an AI graph.

`tokens.grant_experiment()` supplies this **global pack experiment only**, not a per-enemy patch.
Every Gold Token using the pack is affected. `PouchActor` is component data, not an exposed instance
blackboard parameter; no per-enemy reward selector was found. The enemy's instance `Drop__DropActor`
selects the spawned actor, not that actor's pouch identity. Per-check tokensanity still needs either a
reviewed per-instance grant channel, distinct validated actor definitions/packs with registration, or
an upstream runtime hook. No new actor or hook is invented here.

Native token `GetType=1027255402`, `SpecialDeal=2855325032`, `FixedMaxNum=100`, model, ActorName,
physics/attachment rules and all other fields remain unchanged. **[INFERENCE]** PouchActor may redirect
the actual grant while retaining the completion callback; the token-specific path could override it or
increment tokens independently. This is exactly what Kareem must settle, not a claim of safe grants.

Output: `E:/OOTRemake/work/r7-drops/ingame/native-token-boomerang/`; adjacent
**`Test - native-token-boomerang.bat`** is copied from the approved save-copy template, never run.
Its own user copies `2026-11-07_llr-tower-before-pickup`; all six saves have the ranch tree Hash
`341792603838029977` unset and no Boomerang (manual slot 01 has 9 tokens).
Pouch member **740 -> 736** bytes, original allocation **5984**. Outer pack **54636 -> 54628**,
compressed **8995 -> 9030**, original/effective allocation **54968**. Neither nested nor outer allocation
grows; no generic component-size formula or size-table patch is needed.

**Kareem:** `ingame/native-token-checklist.md`: native-looking ranch token, uncollected recovery;
collect, check Boomerang ownership/use versus token count/text/model, then Save/Continue and no respawn.
Hypothesis: Boomerang, count unchanged at 9, saved enemy Hash set. Record actual behavior even if different.
`check_native_token_save.py` reads only the isolated user's resulting saves. Token shuffle stays refused.

Checks:
- `uv run pytest tests/test_tokens.py -q`: **10 passed**.
- Targeted `OOT_ROMFS=... uv run pytest -m dump tests/test_tokens_dump.py -k native -q -s
  --basetemp E:/OOTRemake/work/r7-drops/pytest-native-token`: **1 passed, 1 deselected**.
- Scoped format/lint passed; `build_native_token.py` exercised the real writer, byte-identical callback/
  other pack members, exact inverse component diff, non-growth allocation and backup SHA256/static launcher
  checks: **passed**. No game/launcher execution or token gameplay acceptance.

## Item 4: default-off BossHeart seed integration

Item 3 committed as `3347c7c`. `drops.seed_setup` links every selected BossHeart to exactly one saved
census/definition Hash, uses the real remake pool, and intersects existing per-item holds with types other
than BossHeart for every non-native pool item. This reuses `allowed()` and the existing constrained-filler
priority stage: normal non-pickups cannot bypass policy through fast fill. No second fill algorithm,
new setting field, alias, or generate/fill.py edit. Native destinations use the five-item palette in item 1.
Unmoved Heart Containers are left untouched. Boss rules and existing exclusions stay unchanged.

Automatic `make_seed` registration, CLI choice and the new Heart Container chest-actor mapping are
separate shared-file-only commits:

| Commit | Shared file / contract |
|---|---|
| `f60c2c7` | `data/item_actors.toml`: Heart Container -> Obj_Heart_Container; chest acceptance unplayed |
| `96ce2e3` | `patch/__init__.py`: one census read, actual-pool restrictions, BossHeart PatchStep; updated Token refusal |
| `1e31f4d` | `__main__.py`: BossHeart choice/help, no default change |

**Claude/reviewer: these are the intended shared-file posts; cs-r7 is absent in this process's store.**
No changes to settings.toml, pyproject.toml, uv.lock, gifts, get-item models or other tracks' owned code.
Section **27** is now appended after existing section 24 (in increasing numeric order); integrate 25/26
ahead of 27 when those tracks arrive. No placeholders or unauthorized rebase needed.

### Exercised integration and diagnosed failures

- `uv run pytest tests/test_drops.py tests/test_drops_seed.py -q`: **16 passed**; twenty actual synthetic fills
  prove non-native progression and normal filler cannot land on hearts, preserve pool counts and prior holds,
  and replay effective CS1 settings. Unlinked/unsaved hearts refuse before a seed can use them.
- The first real seed test printed `no actor for 'Heart Container' in item_actors.toml`. Diagnostic lookup
  printed mapping `None`, native pickup `Obj_Heart_Container`. The isolated mapping commit addresses that
  exact missing pool grant; no retry/logic/goal relaxation.
- Aimed dump rerun: `OOT_ROMFS=... uv run pytest -m dump tests/test_drops_seed_dump.py -q -s
  --basetemp E:/OOTRemake/work/r7-drops/pytest-boss-seed-mapped`: **1 passed**. Whole-world Chest+BossHeart
  seed 7 written/read back: all eight assigned native actors; inverse Gyaml diff plus planned chest changes
  reproduces each entire original Banc, including spawn/groups/save identities.
- Initial scoped lint printed the CLI help's exact excess width and import ordering. Reordered the imports;
  a 124-character shortened help was still over 120, so split it into adjacent literals. No behavioral workaround.
- Actual full CLI: seed 7, `--shuffle Chest Shop Gift Scrub BossHeart --songs anywhere`, default gated
  return guarantee: **289 checks, 24 spheres, 124 romfs resources**, plus spoiler and play note. Exit **0**.
- The two-process smoke driver's 180-second deadline expired during its second process, after the successful
  first output/log. Printed complete first output (126 files), first exit 0 and absent replay directory.
  Resumed only the second replay, preserving the first result, with a 3600-second deadline.

### Completed CLI replay

Second actual CLI process (`PYTHONHASHSEED=701`, original 700), using the first output's effective CS1:
exit **0**, **289 checks / 24 spheres**. **126/126 canonical files byte-identical**, including all
124 romfs resources, spoiler and play note. The driver printed first-output 126 files, settings length
1712 and absent second output before resuming; replay completed in 236.04 seconds under the longer deadline.
Written native-heart readback matched all eight assignments: red rupees at Dodongo, Barinade, Gohma,
Bongo Bongo, Twinrova and Morpha; Pieces of Heart at Volvagia and Phantom Ganon.

Proof retained: `boss-seed-smoke-proof.json`, `cli-boss-0.log`, `cli-boss-1.log`. After proof, removed only
the two session-created smoke overlays, completed failed/passing targeted seed-test basetemps and throwaway
smoke driver. Requested two player overlays, their unrun launchers/checklists/checkers/builders and read-only
research remain. No game, live user, original seed, dump or backup directory was touched.

## Pre-rebase full gates and handoff (historical commit IDs)

All four commands ran in full once on source through **`b5fc987`**; no code changed during or after them.

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | **185 files already formatted** |
| `uv run ruff check` | **All checks passed** |
| `uv run pytest --basetemp E:/OOTRemake/work/r7-drops/gate-synthetic` | **531 passed, 72 skipped**, 687.28 s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump --basetemp E:/OOTRemake/work/r7-drops/gate-dump` | **71 passed, 532 deselected**, 1070.35 s |

603 tests collected. The complete dump run includes all placement/EVFL/MSBT/census oracles, original seeds,
all token copies, the native-token byte-preservation oracle and the whole-world written BossHeart seed.
The synthetic gate includes the unchanged default/progressive/age-return sweeps and twenty native-destination
boundary seeds. No weakened assertion, narrowed full gate, retry-count change or unchanged failing rerun.
Both completed full-gate basetemps were removed, only after their processes finished.

Branch **`r7/drops`**, in commit order:

| Commit | Scope |
|---|---|
| `7fa2c15` | item 1: all eight spawn/flag/group contracts and native palette proposal |
| `1f99ee4` | item 2: native transforms, regression oracles, King Dodongo isolated output/checklist |
| `3347c7c` | item 3: retained-native-token grant experiment, byte-preservation regressions |
| `f60c2c7` | shared actor table only |
| `96ce2e3` | shared seed pipeline only |
| `1e31f4d` | shared CLI only |
| `b5fc987` | item 4: native-only fill policy, end-to-end regression, README and section 27 |

The next documentation-only commit records these final results; its hash is in the chat handoff.
No merge, push, stash, dependency change, game/launcher/window execution or write to game/backups/live users.

### Remaining human checks / coordination

- **Kareem:** run the two separate saved-copy launchers under
  `E:/OOTRemake/work/r7-drops/ingame/`, with their short checklists: King Dodongo Hylian pickup/persistence;
  native ranch token's actual Boomerang grant/count and enemy persistence. Require overlay logs and in-game
  observations, not only the read-only save checkers. No gameplay acceptance is claimed.
- **Kareem/reviewer:** native-only BossHeart palette is provisional; Heart Container grant/presentation from
  a chest also needs observation before treating the opt-in as gameplay-certified. Defaults remain unchanged.
- **Reviewer:** integrate sections 25/26 before 27 and review the three isolated shared-file commits.
  Token remains refused: global PouchActor redirection is not per-check tokensanity.
- The required shared/handoff thread posts could not be delivered because `cs-r7` is missing from the local
  Bermuda store. Initial post failure and store diagnostics are above; `thread log --thread cs-r7` says empty,
  but the threads table still has no such row. No forbidden thread-creation command or database mutation.
  The intended handoff is this commit ledger, four passing gates, 126-file CLI replay and the two player outputs.

## Reviewer-requested rebase onto dfe923a

Claude created `cs-r7`; both previously failed commands were reposted unchanged and in original order as
`cs7c` (scope note, then `a7f20bf` handoff). Both posts succeeded. The missing-thread blocker above is historical.

At Claude's next instruction, the branch was clean (`git status --porcelain=v1`: empty), local main resolved
to `dfe923a1a9498cf0b8eca457711ee71da68866dd`, and `git rebase main` replayed all eight commits without conflict.
This incorporates the reviewed Jabu Beginning -> Main override and D26. The earlier IDs and gate ledger above
describe pre-rebase history; the rebased ledger and fresh gate results supersede them below.

Fresh actual CLI smoke on the rebased source:
`uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 7 --out
E:/OOTRemake/work/r7-drops/rebased-seed-smoke --shuffle Chest Shop Gift Scrub BossHeart --songs anywhere`.
Exit **0**, **289 checks / 24 spheres**, **124 romfs files**; read-back spoiler contained 289 placements and
the full output contained **126 files**. Removed only this new smoke overlay after its process finished.
No game, launcher, backup or live user was touched.

### Fresh final gates after rebase

All four full gates passed on rebased source through **`0cd8073`**. Only this round report changed afterward.

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | **185 files already formatted** |
| `uv run ruff check` | **All checks passed** |
| `uv run pytest --basetemp E:/OOTRemake/work/r7-drops/gate-rebased-synthetic` | **533 passed, 72 skipped**, 788.35 s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump --basetemp E:/OOTRemake/work/r7-drops/gate-rebased-dump` | **71 passed, 534 deselected**, 756.10 s |

605 tests collected. Both completed rebased gate basetemps removed only after the entire command exited 0.
No source/test changes, failed reruns, narrowed gate or assertion changes were needed for the rebase.
The fresh combined CLI smoke above is a new real generation; the earlier 126-file byte-identical two-process
replay remains pre-rebase evidence, not a claim that a new post-rebase replay was run.

Rewritten commit ledger, in original order:

| Historical | Rebased | Scope |
|---|---|---|
| `7fa2c15` | `c1a7386` | item 1 research |
| `1f99ee4` | `4fb4cbd` | item 2 native swap and Dodongo output |
| `3347c7c` | `db70911` | item 3 retained-native-token experiment |
| `f60c2c7` | `58ad1c5` | shared actor mapping |
| `96ce2e3` | `c9a1445` | shared seed pipeline |
| `1e31f4d` | `c1d9f84` | shared CLI |
| `b5fc987` | `50b48b3` | item 4 integration |
| `a7f20bf` | `0cd8073` | pre-rebase handoff report |

This evidence is committed separately and posted as the superseding `cs7c` handoff to `cs-r7`; its hash is
in the chat/thread handoff. Human gameplay/review checks above remain outstanding; defaults unchanged.
