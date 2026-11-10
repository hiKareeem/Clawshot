# Round 11, Track B: keysanity exploration (cs11b)

Branch `r11/keys`. Read supplied AGENTS, README, plans00–04, decisions, Round11 opening/shared-file rules and round9/10 reports. Dump and save backups are read-only. No game, launcher, window, Hookshot build, terminal-control command, merge, push or stash. No dependency change. Research, decoded data and experiments live only at `E:/OOTRemake/work/r11-keys-cs11b/`. Commands are serial; pytest uses `CLAWSHOT_WORKERS=1`. Full suites/sweeps acquire `E:/OOTRemake/work/rounds/r11/gate.lock`, wait60s on contention, and release immediately on exit.

## Item 1: native state and grant trace

Build `e0f3ccfa`. Executed read-only `probe.py`, `contracts.py`, `native_trace.py`, `final_contracts.py` and `select_saves.py`. Their JSON/disassembly remains external. Native addresses below refer to the player's own `.hookshot_exefs/main`, not Hookshot source. Ephemeral permissive Capstone via `uv run --with capstone`; existing external unmodified AINB decoder used only to decode native graphs. No GPL code or NX2navi code/docs read/copied.

### Saved state

`GameData/GameDataList.Product.110.byml.zs` has a non-saved `DungeonInfo` Struct whose children select14 dungeon Structs. `RSDB/DungeonParam.Product.111.rstbl.byml.zs` `TargetGameData` matches those child keys. Each dungeon has these existing, independent leaves (all reset8/save0, so stored in `slot_NN/progress.sav`):

| Full named leaf under `DungeonInfo.<area>.` | Type / native default | Native member hash |
|---|---|---|
| `SmallKeyNum` | Int /0 | `0x1af87831` |
| `SmallKeyTotalNum` | Int /0 | `0x642f7364` |
| `IsGetSmallKeyOnce` | Bool /false | `0x251d4c2a` |
| `IsGetBossKey` | Bool /false | `0x5fb83617` |
| `IsGetMap` | Bool /false | `0x58aeb8fb` |
| `IsGetCompass` | Bool /false | `0xc7692e3f` |

Areas: `InsideTheDekuTree`, `DodongoCavern`, `InsideJabuJabuBelly`, `ForestTemple`, `FireTemple`, `IceCavern`, `WaterTemple`, `BottomOfTheWell`, `ShadowTemple`, `SpiritTemple`, `GerudoTrainingGround`, `InsideGanonCastle`, `FinalBattleField`, `GerudoFortress` (the last is selected by row `GerudoFortress_Adult`). Even keyless dungeons have these leaves. Kokiri rows are `IsFieldData=true` with **no TargetGameData**. Exact per-dungeon hashes are retained in `state-catalog.json`; these are not global `PouchData.Item_Dungeon_SmallKey.StockNum` counts.

### Native grant/read contracts

- All dungeons share the four actors `Item_Dungeon_SmallKey`, `Item_Dungeon_BossKey`, `Item_Dungeon_Map`, `Item_Dungeon_Compass`. No dungeon argument is carried in those names. Pouch rows: small key `PouchSpecialDeal=SmallKey`; other three `NotPushToPouch`.
- `Dm_SY_Treasurebox` dispatches special chest contents to `GameSystemActor.EventGetDungeonMap` (Event23), `...Compass` (Event26), `...BossKey` (Event27), `...SmallKey` (Event30). Their only explicit parameter is `IsWaitEnd=true`; **no target dungeon parameter**. The small-chest/shared-grant paths are retained in external `chest-contracts.json`.
- Native `OneShotDungeonGetSmallKey` execute `0x028cb390` resolves the same live component via `0x00b2af20` / `0x00b2afc0`, then calls `0x03283160` with +1. That routine reads `SmallKeyNum`, sets `IsGetSmallKeyOnce` when the current count is zero, increments `SmallKeyTotalNum` for positive grants, then changes `SmallKeyNum`. Its negative branch refuses underflow and does not decrease the total. `OneShotDungeonUseSmallKey` execute `0x028cbd20` passes -1 to that same routine.
- Boss/map/compass execute `0x028cae10` / `0x028cb1c0` / `0x028caff0` use that same live component and set its `IsGetBossKey` / `IsGetMap` / `IsGetCompass` via `0x032830e0` / `0x03282fe0` / `0x03283060`. Boss also requests native display state; these are not per-dungeon named-argument APIs.
- `DoorChainLock.root` node3 reads `QueryDungeonGetSmallKeyNum` (no inputs); node18 uses `OneShotDungeonUseSmallKey` (no inputs). The open state is separate: `IsChainLockDoorOpen` Struct indexed by the controller InstanceID string, not the key pickup Hash. Query execute `0x029ebb10` resolves the same component and reads the remaining count. The counterpart boss-key query `0x029ebd70` resolves it and reads the boss flag. This establishes count consumption and native flag readers, not an in-game opening result.
- **[INFERENCE]** Shared component selection plus DungeonParam's target mapping means the generic pickup credits the loaded dungeon, not the fill's intended dungeon. Kokiri has no target: whether the native path silently loses the item, retains an earlier target, or behaves otherwise is **not established** by this static trace. The explicit item2 experiments distinguish these outcomes. No claim of keysanity working follows from settings/fill support.

### Save evidence and diagnostics

All24 slots of four candidate backups were read, not edited. Early ranch manual01 is child, Deku map/compass owned, Deku remaining/total0 and Forest remaining/total0. Adult-first manual01 is adult, no Hookshot/Minuet, Forest remaining/total0. After-Forest manual01 has Forest boss/map/compass true, remaining0/total5/once true, Fire remaining/total0. This independently corroborates **separate remaining and acquired-total counters**, not a controlled before/after key pickup.

First scratch hash probe passed bytes to `save.key`, which requires str: printed AttributeError and source signature; decoded before hashing, then the aimed run succeeded. Initial total-name guess `TotalGetSmallKeyNum` had no matching saved row; printed native member `0x642f7364` and Struct values instead of treating it as absent. Candidate-name hash proof identifies actual `SmallKeyTotalNum`; `IsGetSmallKeyOnce` likewise matches its member. No game result inferred. A trace-helper insertion was caught in the edit response, read back and moved before execution. Python references request: no language server available.

## Coordination / provisional choices

- Required shared edits will be isolated: early refusal in `patch.make_seed` and the public CLI; **no fill, Settings, CS1 or synthetic-anywhere removal**. TrackD can expose the setting but must surface generation refusal. TrackA README text requested: “Dungeon items remain own-dungeon. Anywhere is encoded for research but seed generation refuses it until named-dungeon grants pass in-game tests.” TrackC's pack generation inherits the same pipeline guard.
- Experiments will preserve native actors/Hash/age copies and use the current template's real-folder one-mod layout; no existing output will be rebuilt. Named-grant prototype is experimental only and will not be registered in seed generation.
- **Kareem: which counter changes after each controlled generic pickup, and can a named Forest grant from outside Forest open a Forest lock after Save/Continue?** The precise launchers/checklists and artifact proof follow in item order. No production success is claimed before your result.

## Priority correction: chest-open save evidence

Claude authorized an isolated section6 correction, keeping the old inference visibly superseded.
Committed **79e00ce** (only that paragraph); section44 now documents the actor-family distinction
and historical audit. `TreasureBox.module` uses named Struct `IsTreasureBoxOpen`, indexed by
the decimal actor Hash; saved Bool name is `IsTreasureBoxOpen.<Hash>`. Raw Bool64 entry presence
is metadata, not evidence that the actor uses it for its check. Ordinary ground rupees,
recovery floor hearts, anchored floor pieces and boss hearts retain their audited raw-Hash
NoRespawn contracts; scripted floor keys, chest gates and door gates are not interchangeable.
Actual original ranch save still has Gohma's native heart Hash set, corroborating that distinction.

Audited all round files for unopened/uncollected/chest-save/Hash checks, then read the exact
external reproducers for the three implicated records. Results in section44:

- r5-gifts227–234 `chest-song-storms-kak`: raw target12902291359202819102=false, but
  **named open=true** in original ranch manual01. That particular follow-up source is invalid;
  do not reuse it. No game run or prior observed song success is retracted.
- r7-gifts87–109 `treasure-red`: builder asserts raw false but also checks the correct
  native first-clear Bool. Fresh original-source read: named open=false, first-clear=false;
  its source remains suitable without relying on the raw premise.
- r10-agetravel165–168 controlled door copies: builder selected using raw `is_set`.
  Claude's independent corrected named=false plus Mido=true controls establishes the chosen
  grave chest is unopened; accepted without rerunning that reported check.

r2-census466–470 already warned about the raw chest absence. r1-formats merely requests an
unopened/new-game source; r6-settings and r8-getitem use new games. Other identified raw counts
are metadata, not source-slot availability proof. No further raw-based unopened-chest premise
found in the round files. Evidence retained externally in `historical-chest-flag-audit.json`.

This caught my initial scratch selector too: it reported every late-Forest chest unopened.
Printed the actual raw182-key list and true inventory/quest controls, traced the named Struct,
then changed only the scratch source selector and reran it once. Item2 uses only explicit
named false (None is not accepted), with the actual selected slot recorded below.

## Item 2: three built, unplayed generic-key experiments

`build_experiments.py` used the real common writer after the corrected named-open source
selection. All lab items are annotated “Small Key (Forest Temple)”; this intent is **not**
encoded in the generic actor. No flow, GameData, actor pack, position, spawn gate or save edit.

Under `E:/OOTRemake/work/r11-keys-cs11b/ingame/`, each name below has
`mods/<name>/<name>/romfs`, `Test - <name>.bat` and a distinct `user-<name>` destination.
Launchers are copies of the current central template with only NAME/ROUND/SAVES/SLOT changed,
CRLF preserved. Bin executable, updater off, cheats on, overlay cleared, exact one real mod.

| Name | Physical chest / native reward | Source / selected slot |
|---|---|---|
| `generic-overworld-next` | Mido far-right9725242744547055868 / blue rupee | `2026-11-07_1630`, **autosave04**, child |
| `generic-keyless-next` | Deku2F vine-wall map8579518566955184384 / map | same backup, **autosave02**, child |
| `generic-other-dungeon-next` | Fire1F second Flare Dancer8757492004108970488 / red rupee | `2026-11-09_1347-main-after-forest`, **autosave00**, adult |

All selected named chest-open flags are explicitly false, not None. Both child checkpoints
have no sword/Mido unlock; the checklist authorizes only Teleport to shorten access, never
inventory/age/flag cheats. Fire's target normally needs late Fire access: use Teleport to the
specified arena and beat its Flare Dancer with the owned Hookshot; do not fake Hammer/keys
or spawn flags. If that Teleport target/native appearance cannot be reached, report the
actual obstruction; the experiment remains pending rather than quietly substituting a chest.
Before/after counters, no other key pickup/spend, save/reload, repeat denial and exact
`mods: <file> <- <path>` proof are specified in `ingame/checklist.md`.

| Resource | Raw before→after | Allocation before→after |
|---|---|---|
| Overworld adult Dynamic |516036→516084|516328→516360|
| Overworld child Dynamic |510884→510932|511176→511208|
| Keyless Deku Static |109808→109812|110088 retained|
| Other-dungeon Fire Static |266440 unchanged|266728 retained|

Only the overworld case emits a size table (length unchanged); the others each emit one
Banc. Exact inversions restore the whole original tree after reverting only the selected
Drop__DropActor in every age copy. Independent `verify_experiments.py` recomputed serialized
and compressed bytes, exact size-table deltas, original save SHA256 maps, one-mod/no-reparse
layout and exact current-template substitutions: **three of three passed**.
`ingame/check_saves.py` ran read-only, reporting zero saves in all three isolated users.
It reads every dungeon's remaining/total/once and boss/map/compass leaves plus named chest-open
state after Kareem plays; it creates no profile or save. Proof JSONs are external.

Additional grant-path trace: small chests call GetPouchContent's pouch grant, not the big
chest's explicit special action. Native call search found the pouch's +1 path at
`0x033ac518..0x033ac530`: same live component resolution then `0x03283160`. Thus both
paths share the observed counter updater; no “small chest is different” success is assumed.

**Kareem: run the three independent launchers only after Claude boot-checks them and after
quitting the played game. Report exact counters, model/text, reload result and mod lines.**
No game, launcher, copy-user operation or boot-check was executed by this track.

## Item 3: named Forest small-key grant prototype (external only)

Built **`named-forest-key-fixed-next`** under the same real one-mod layout, with its own
template launcher and `ingame/named-key-checklist.md`. Source is early1630 **autosave04**;
the same genuinely unopened Mido far-right chest gives the generic small-key display actor.
No production `patch/keys.py`, pipeline hook, new setting, EventSetting row, GameData row,
saved default or inventory cheat is introduced.

Technical prototype in reusable external `prototype.py`: the existing
`KokiriForest_TreasureBox_NaviChatOff` row already enters Small/Success_MidoHouse.
Only that entry's targets redirect to cloned small-chest/GetPouchContent paths; original
shared entries/events remain intact. On a small-key grant in the cloned path, existing
GameData actions increment **DungeonInfo.ForestTemple.SmallKeyTotalNum and SmallKeyNum**,
setting existing **IsGetSmallKeyOnce** when the prior remaining count is0. The generic
current-dungeon pouch grant is skipped for that branch; non-key contents still take the
original pouch action. Native chest identity/opening, display and cleanup remain.
All four Mido chests share this wrapper; only the one experimental key qualifies in this
output. This is explicitly **not a source-bound general keysanity implementation**.

Five resources: both Kokiri Bancs (same item2 deltas), Small flow74808→135384
(allocation75088→135664), GetPouchContent65880→126408
(66160→126704), common size table unchanged length. Entire native flows invert exactly
after restoring the one entry's targets and trimming appended nodes/entries/operation names.
Existing saved metadata for all three named leaves is checked before writing.

`verify_prototype.py` read the actual serialized payout dispatch:
zero keys→remaining1/total1/once true; existing2/5→3/6 without another first-key write;
non-key→exactly the native pouch action with no dungeon-state change. No current-dungeon
pouch action occurs on either key path. It independently rebuilt the exact compressed flow
bytes, inversed both complete Banc trees, recomputed the exact size table, checked immutable
backup SHA256 maps and exact template/one-real-mod/no-reparse/absent-user layout: **passed**.
These are data/interpreter checks, **not the native engine or an in-game grant**.

First smoke caught reversed boolean cases: printed SmallKey=true taking the original pouch
action with remaining0/total0. Existing project's native boolean-query convention is0=true,
1=false (`tests/test_gifts_*`); corrected only that dispatch and built into a NEW
`named-forest-key-fixed-next`, then the cause-aimed smoke passed. The old
**`named-forest-key-next` is invalid; do not run it**. Its unplayed files are preserved,
not overwritten or silently presented as successful.

**[INFERENCE]** Named GameData writes should credit Forest independently of Link's current
area, but native dungeon caches, actor context, display, saved once behavior and actual lock
consumption remain unplayed. **Kareem: use only the fixed-next launcher's named-key checklist;
report saved Forest1/1/once, no other dungeon change, Save/Continue/no repeat, and later native
Forest door consumption if normal progression in that disposable child copy reaches it.**
The latter long-path check can remain pending without pretending stored numbers prove it.
No boss-key/map/compass prototype is claimed. The seed-generation guard remains required.

## Item 4: refuse unverified game output, retain the fill mode

Added `patch.check_dungeon_items(settings)` and call it at the start of `make_seed`
and before CLI gift setup/output checks. Anywhere generation raises PatchError with
the reason: generic key/map/compass actors have no target dungeon, named grants lack
in-game acceptance, use own_dungeon. CLI reports it with exit1, not a traceback.
Settings/CS1/print-settings and the pure assumed fill are intentionally unchanged.
No experimental prototype is imported by production code.

Failing-before single-file regression printed `make_seed` reaching census/dictionary
access (`missing-romfs/Pack/ZsDic.pack.zs`) instead of rejecting anywhere. After the
cause-specific boundary guard, `CLAWSHOT_WORKERS=1 uv run pytest tests/test_keys.py -q
--tb=short --basetemp E:/OOTRemake/work/r11-keys-cs11b/keys-after-next`: **7 passed**.
Covers direct pipeline, explicit CLI, encoded CS1, Gift pre-read refusal, no output
creation, research settings printing and explicit own-dungeon override on replay.
Scoped format (3 files) and lint passed. Python references request again found no
language server; literal callsite search confirms the CLI is the production caller.

Actual public CLI smoke (not just tests), `smoke_cli.py`, serial/CLAWSHOT_WORKERS=1:
- Explicit anywhere + Chest/Gift: exit1 with the attribution/in-game reason; no folder.
- Replayed anywhere + Gift CS1: same refusal before gift scanning; no folder.
- Fresh default-own seed7, Kokiri/Lost Woods/Deku slice, Gohma goal: exit0,
  **12 shuffled checks,4 spheres,28 resources**, spoiler and play-note written to
  `own-slice-next`; emitted settings remain own_dungeon.
Proof and CLI logs are external (`cli-smoke-proof.json`); no game was started.

All requested source/data changes are complete. The four-command gates have now passed;
exact results are recorded below. No checkpoint or full-gate pass above is an in-game success.

## Commit ledger / review boundary

| Commit | Scope |
|---|---|
| `d4d5621` | Item1 native dungeon state/handler trace and section44 |
| `79e00ce` | Authorized section6-only superseding correction |
| `cc805a9` | Actor-state distinction and historical unopened-chest premise audit |
| `c029622` | Item2 three independently checked generic-key experiments |
| `6499f5a` | Item3 external named-Forest prototype, diagnosis and acceptance limits |
| `6f0b9a6` | Isolated shared seed-pipeline guard |
| `bdcc5e0` | Isolated CLI guard and seven boundary regressions |
| `174286c` | Item4 docs and actual public-CLI smoke proof |
| `f1bedbc` | Exact chest reset metadata and reviewer dry-run/superseded-launcher boundaries |

Only report/metadata documentation follows these source checkpoints. Source/tests are frozen
for full gates. Later exact GameData-row inspection corrected the named chest-open Bool's
reset metadata in section44 to **24/file0**, not8; its saved accessor/Hash mapping is unchanged.
The short completed CLI smoke driver was removed; reusable read-only researchers/builders/
artifact verifiers and the player's save observer remain external with their proof/log files.

Claude clarified the external changes: his four launcher dry-runs created their user/save
copies as expected; **a user folder alone is not a played test** (a hookshot_log.txt identifies
a launch). He moved the invalid launcher into `ingame/superseded/`; leave it there. This
track started no game/launcher or user-copy operation. Build-time absent-user assertions are
historical, not conditions to rerun after these dry-runs. Claude's boot checks wait until the
current test session has been closed for a few minutes; only failures will be relayed. No
boot success is inferred from silence: boot covers startup only, and area files still need
Kareem's actual play. Preserve every current mod/profile and do not rebuild them.

Additional historical context: section19's existing “In game” record already says the ranch
Kakariko chest was opened and the successful follow-up was replaced with new-game
`chest-ocarina-storms`. The named-flag audit corroborates that history; it is not a new
unresolved song failure or a request to rerun Kareem's reported success.

Cross-track documentation request (posted on cs-r11): roadmap915–919's later tracker
candidate still describes the raw Bool64 list as universal opened-check state. Future tracker
work must dispatch by actor/check kind, including named chest Bools; reviewer/roadmap owner
should correct that backlog statement. Only the explicitly authorized section6 and owned
section44 were edited here.

## Final verification and handoff

All four required gates passed on the frozen source/tests, with one worker. The full
synthetic run acquired `E:/OOTRemake/work/rounds/r11/gate.lock` by mkdir at10:33:38
and released it by rmdir at10:53:38. The separate dump run acquired it at10:53:38
and released it at11:05:06. The waiting runner retried occupied-lock mkdir once per
minute; neither full test run overlapped another holder.

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | exit0;259 files already formatted |
| `uv run ruff check` | exit0;all checks passed |
| `CLAWSHOT_WORKERS=1 uv run pytest` | exit0;823 passed,110 skipped |
| `CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | exit0;93 passed,16 skipped,824 deselected |

Both pytest commands also used new external `--basetemp` directories:
`gate-synthetic-final-next` and `gate-dump-final-next` under the track scratch.
Synthetic OOT_ROMFS was unset; OOT_NUP/PYTEST_ADDOPTS were unset for both.
Exact command/environment/exit records are in external `gate-final-results.json`;
complete captured output is in `gate-{format,lint,synthetic,dump}-final.log`.
The completed one-shot gate coordinator was removed; logs/proof and reusable
experiment researchers/builders/verifiers remain outside the repository.

Ready for review of the isolated commits in the ledger plus this final evidence
commit; no push or merge. No game executable or launcher was started by this track.
The four current mods/profiles and superseded launcher remain untouched.
The acceptance requests above are historical: Kareem's subsequent results are now in
section44's **In game** table and the six `R11-KEY-*` rows in `playtest/answers.md`.
Named Forest overworld grants and native spending passed; the redirected big-chest entry
failed before opening. Production anywhere generation remains refused.

## Results publication after merge (`r11/keys-results`)

Claude merged the old `r11/keys` work and gift release into main, then authorized this new
docs-only branch. Recorded all six cases from the external `work/rounds/r11/keys-results.md`,
including exact player quotations/save values, the failed named big-chest case and the
current-dungeon standing map display. Section44 and the keysanity candidate distinguish
played plain-key/door evidence from remaining anywhere requirements. The Tracker candidate
uses kind-specific opened state and D38's seed-owned-save UI tab; the earlier roadmap
request is resolved. `README.md`, source/tests and `decisions.md` were not touched.

No format/lint/pytest rerun for this docs-only update, per Claude. His merged-main review
results (846 passed/110 skipped; dump109 passed with nup tests) are reviewer-reported,
not new runs by this track. Static diagnosis and later experiment work remain external.
