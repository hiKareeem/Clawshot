# Round 13: fast-start release bugs (cs13a)

Branch `r13/fast-start`, base main `30ba5c9` (0.2.0, not yet published). Version unchanged; Claude owns version decisions.

## Scope and evidence status

Requested by Kareem/Claude, 2026-11-12: reproduce public generation witness failures across every fast-start subset; trace and repair closed-forest Mido with the Deku Tree talk skipped; remove the intro movie if its post-state is safe; stage one isolated new-game test; serialized synthetic/native gates.

Player reports A/B/C are ground truth. The proposed cause of A is now confirmed by the native schedule/flow/placement trace below; gameplay of the repair remains unverified. The all-skips test does not establish closed-forest behavior. The historical `intro-removed` scratch output is unplayed.

No game start, merge, push, version change, or writes to the dump/game installation. Research and generated files stay under `E:/OOTRemake/work/r13-fast-start-cs13a/`. Full sweeps and gates take `E:/OOTRemake/work/rounds/r13/gate.lock`.

## Work in progress

- Public-path before/after matrix and witness diagnosis.
- Read-only Mido flow/AI/default audit and intro movie state audit.
- Fixes and regression coverage; parent integrates shared data and docs.
- One public-generated new-game pack, empty save source and template-derived dry-run launcher; Claude boot-checks before Kareem plays.

## B: decide validity before changing the witness contract

Claude's 2026-11-12 steering is authoritative: a child-only Gohma guide must not become an
extra validity policy. A valid adult-first seed must remain accepted; a physically impossible
modeled route instead needs a logic correction. No witness-based rejection/retry policy is adopted.

Native evidence for the first observed failure class (`Recommended`, early Door of Time,
`forest=closed_deku`): the bridge's saved blocker is intentionally false from a new game
(section 21 / played R6-CLOSEDDEKU), independently of Mido and Gohma. Open Door of Time
uses a native Ready threshold and ungated first-pull attention module (section 41 / played
R10-DOOR-OPEN), independently of spiritual stones and Gohma. The model's Forest Temple
completion still gates adult return. **Data/model inference, not a newly played route:** in this
offered mode a child can leave and pull the sword first, then obtain the child sword/complete Gohma.
A child-only Gohma witness can be unavailable despite a valid complete search; that is a guide limitation,
not evidence that the seed is invalid. The guide must omit/explain that opening rather than
invent pre-pull purchases or reject the seed. The measured matrix and final repair follow below.

Repair: `opening()` returns a distinct `NoChildOpening` result rather than throwing when
the child-only proof is unavailable. Spoilers retain `opening_route=null` and additionally
record `opening_route_unavailable={name,event,region,reason}`; ordinary child guides remain
fully replayed. The play note prints the explanation, not a fake child route. No new
generation rejection/retry rule was added and `check_beatable` remains the validity oracle.

Public smoke of the formerly failing class: seed 1, Recommended, `forest=closed_deku`,
`door_of_time=open`, all four fast-start skips. The CLI wrote 143 files, 300 shuffled
locations / 20 spheres. The play note explains Gohma after collection sphere 13 with adult
help; no child step table appears. Source of the original crash is recorded in external
`witness/probe1.jsonl` with its `route.py:97` traceback; the sword is in KF Storms Grotto
Chest after the return (sphere 12).

The other failure class was Chest-only plus early Door of Time under the return guarantee:
the existing return-kit stage exhausted ten attempts because its configured first-pull
inventory lacked access to fixed Saria/ocarina checks. Validation now detects an upper bound
for that **construction**: give adult all shuffled items, every non-progression item and
every dungeon reward, then search fixed checks. If even that cannot open return from the
configured bound, refuse before filling. The player message names the door mode, shuffle,
`age_return_guarantee`, Ocarina/Saria's Song, their three fixed checks, and closed-door/Gift
alternatives. Public CLI smoke exits 1 with that explanation and creates no output folder;
UI validation accepts closed and gives the same clear refusal for open/song_only.

**Important limit, caught during review:** for song_only with the Time-song gift fixed, the
actual first pull requires `has_all_stones` (`hyrule_field.toml:18-19`, verified by the remake
override), so its real inventory is larger than the configured Fairy-ocarina + Time-song
bound. The validation message therefore says this generator's return-kit construction is
unsupported, **not** that no physical route or valid assignment exists. No guarantee was
relaxed and no option is silently dropped. For open mode the empty configured inventory does
match the physical earliest pull. This is independent of the valid adult-first guide case.

**Preflight ordering correction (reviewer finding, cs13a repair):** its first version examined
spec vanilla items inside `prepare`, before native census overrides existed. A synthetic
return-world case with spec `E Inner=Rupee`, effective override `Weapon`, was falsely refused
although its effective fill equals the supported original fixture. The regression failed
with that exact FillError before the fix. `prepare` now compiles only; UI validation checks
the spec bound, and `generate` checks after validating native overrides. Both shuffled pool
items and fixed checks use the effective values. No blanket Chest-only ban was added.
Post-fix focused run (native B regression, Mido and the return-world override included):
**32 passed in 75.78s**. Native-event review found no issues; the one generation review
finding is repaired. The partial gate run was cancelled for this behavioral change and its
owned lock released; final full gates restart on the corrected source.

Required before/after matrix is still pending the serialized gate handoff; no full-matrix
pass is claimed here. The resumable baseline currently contains 118 rows (86 generated,
32 return-kit failures); the first baseline failure is Chest-only, closed forest, open door,
seed 1, no fast skips. Its exact payload and every recorded combination are in
`witness/baseline.jsonl`; the matrix covers all 16 subsets, explicit forest modes and legacy
Mido normalization, Chest/Recommended and seeds 1/7/42. Open/closed door rows take priority;
song_only is additional coverage.

## A: Mido's saved blocker and native clear

**First repair FAILED in game and is superseded; the wrapper below must not ship.**
Kareem reported a Talk event hang around 08:44 on 2026-11-12. The replacement must retain
native early meeting state, initialization and actor bindings rather than cross-entry jumps.

Read-only probes: external `mido_probe.py`, `mido_schedule.py`, `mido_smoke.py`; raw research stays outside the repository. Dump build `e0f3ccfa`.

- `GameDataList`: `KokiriForest_Npc_Kokiri_Mido_Child_Blocker` is a saved Bool, default true, reset 8. The skip of the tree talk initializes `Step_Meet_DekuTree=Complete` but leaves this Bool true when Mido is kept.
- `Component/AIScheduleParam/Npc_Kokiri_Mido_Child.game__component__AIScheduleParam.bgyml`: the after-Step02 and completed-meeting schedules both select `Npc_Kokiri_Mido_Child_C1C2_TT`, whose flow entry is `Meet_DekuTree_IsAfter_Step02_Exp_Talk`. That entry bypasses the equipment/first-clear route.
- Native flow `Npc_Kokiri_Mido_Child`: `Talk` tests equipped sword/shield slots (`Event10`, `Event12`/`Event36`). Success reaches `Event118` -> `Event26`, which writes the saved blocker false -> `Event32`, `EventNpcBlockerEndBlockerAI`. `Event29` is the other clear, after the post-Gohma event (`Event111`); it cannot rescue the opening. Later talk `Event119` ends without clearing.
- `Banc/KokiriForest/KokiriForest_Child_Dynamic`: invisible wall `FldObj_AirWall_Player_GenerateNavMesh`, Hash `3960132711735390266`, has non-negated, non-lazy Presence on that same saved blocker. The actor pack's `Npc_Blocker_Mido` BlockerParam also uses it as `GameDataToEnableAI`. Clearing the native flag removes the wall and disables blocking; merely seeing a positive dialogue does not.
- World AI `KokiriForest_Child_Level_All_02_35ae` uses the saved Bool to retain/delete blocker areas and drive the separate transient `KokiriForest_Npc_Kokiri_Blocker`; `_2680` uses it to retire the attention-ignore area. The tree-talk trigger `_a798` removes its area once the meeting is past Step03. No AI rewrite is needed.
- Native Mido `Event0` still requests meeting Step03 after clearing. The existing all-skips
  save proves a preset Complete survives OpeningEvent `Event8` requesting Step01 with the
  same `EventExecuteProgressChallengeStep` options (`IsIgnoreCompletedChallenge=false`);
  the repair therefore does not invent a second quest-state implementation. Retaining
  Complete after Mido remains part of the unplayed combined check.

**Superseded repair:** the later entry wrapped the native Talk graph while the saved blocker
was true. Its old four-equipment replay reported the desired clear results but ignored
per-entry subflow registrations and treated external initialization/presentation as inert.
Those results did not certify a runnable event; the live hang invalidates that repair.

## New lead: Saria's banner and the pause map

Source lead: Kamil, Hookshot Randomized (MIT), 2026-11-12, section 5 of
`E:/OOTRemake/work/rounds/r13/kamil-hookshot-randomized-findings.txt`. Facts only;
no source code was read or copied. Independently checked by external `banner_probe.py`:

- `Dm_Kokiri_0045` Event7 calls `UISystemActor.EventTriggerOpenLocationUI` for KokiriForest.
  The corresponding `RSDB/Location.Product.111` row has `IsShowLocationUIFirstTimeInDemo=true`.
- `IsVisitLocation.KokiriForest` is a saved Bool, default false, reset 8, save file 0.
  No EVFL explicitly writes this literal flag; the banner's visit side effect is corroborated
  by historical saves, not inferred solely from its name.
- Historical `r4-fast-start/user-all` after entry to the tree: Saria's `_0045` played flag true
  (preset by skip), forest visit false. Normal post-Saria `r3-seed/user-seed-3` snapshots:
  played true, visit true. `r4-fast-start/user-intro` before Saria: movie played true,
  Saria played false, visit false. Thus playing the opening movie does not supply the visit.

Fix: `saria.game_data` additionally sets the forest visit Bool true, through the existing
initial-value patch. No unrelated location is visited. `intro` alone does not pre-set it:
the Saria flow/banner remains available. Synthetic regression covers no skips, intro alone,
Saria alone and intro+Saria; native regression checks the banner contract and saved flag.
The one new-game check includes Saria skip and checks pause-map availability both outside
and inside the Deku Tree. **Map behavior of the fix is not yet observed in game.**

## C: remove the opening movie, retain normal initialization

`intro` now edits `OpeningEvent:Opening_LoadingKokiriForest`: entry starts at native
`GameSystemActor.EventQueryBancChangeIsLoaded` (`Event18`). The movie's exclusive event slot
(`Event3`) becomes a one-frame `EventWait` returning to that query while loading; the native
loaded branch, fades and 120-frame settling wait remain. All other events/entries/actors stay
unchanged, including `Opening_Introduction` (6:00, meeting Step01, Navi talked, autosave).
Pouch/status initialization in `Sequence/Opening` still precedes the requested loading event.

Read-only audit artifacts: external `intro_*` scripts/results. The movie is a prerecorded
`Event/Movie/Dm_Kokiri_0000.webm`; its timeline has rumble, title display, fade and narration,
no saved-data writes. Searches across 914 flows, 121,634 decompressed native files and game
executable references found no consumer of its played flag; only `OpeningEvent` transitions
to the movie. Four-byte hash matches in terrain/lighting binaries were distinguished from
actual readers. `Pack/Bootup` contains no shadow copy of OpeningEvent. Native analyzed-event
preloading is retained; no dependency is added.

**Inference retained:** the load query returns loaded when the forest load finishes (the native
movie previously hid this interval). The only skipped saved-state effect is
`HavePlayedEvent.Dm_Kokiri_0000`, which stays false rather than falsely claiming the movie played;
the audit found no reader. No inventory, visit state, clock, quest or wake-up work is skipped.
This is the requested state difference limited to the movie, not a general new-game shortcut.

Fast-start edits now share the normal composable writer through `gamedata.changes(chosen)`.
Data names the two checked transforms (`opening_without_movie`, `mido_equipment_gate`).
The obsolete skippable/component-list path and its cache metadata are removed, not retained
as a second intro mode. Standalone `patch.gamedata.write` uses the same writer, so Mido's
repair is paired there too and native size-table growth is accounted for.

Standalone CLI smoke: default writes OpeningEvent only (17,504 -> 17,416 bytes, allocation
17,776 kept); all selected skips write the two flows, GameDataList and the raised size table.
Intro implementation ran no pytest/ruff. Witness implementation reported focused checks
(32 passed / 2 native skips; another 48 passed) before the parent's wording corrections;
parent owns the serialized full gates.

## Superseded staged check (FAILED; frozen for evidence)

- Public command: `uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 7 --forest closed --door-of-time closed --skip intro saria deku_tree --out E:/OOTRemake/work/r13-fast-start-cs13a/ingame/mods/fast-start-next/fast-start-next`
- Result: 165 shuffled locations, 30 spheres, 82 written files; real remake census/pool,
  beatability, opening witness, flow transforms and output read-back all exercised.
- Launcher: `E:/OOTRemake/work/r13-fast-start-cs13a/ingame/Test - fast-start-next.bat`,
  copied from the current template, CRLF, dry-run exit 0. `SAVES` points to the created **empty**
  `ingame/empty-new-game`; no save is copied. HOS_MODS contains exactly one real mod, no links.
- Checklist: adjacent `ingame/CHECKLIST.md`, **20–30 minutes**, plus 10 if unfamiliar with
  the dungeon. Sword: far-right Mido chest; cash: far-left chest (20); Deku Shield: native
  shop (10). Avoid middle-right Fairy Bow; middle-left Boomerang supports the short map route.
  Tests both missing equipment refusals and actual step-aside/wall passage; no tree talk;
  movie absent but Navi wake retained; forest map and Deku map after its basement chest;
  re-entry and Save and Continue. No Gohma clear required.
- `check_staged.py` confirms saved Mido blocker initially true, visit flag true, meeting Complete,
  forest stone GoInside; generated Mido flow clears only after equipment; OpeningEvent has
  no movie transition; all three native allocations fit. Launcher dry-run starts nothing.
- UI smoke: actual `--no-open` UI in hidden Chromium; checked all three updated help panels,
  no browser errors, visual evidence `intro-ui-help.webp`; tab and owned server closed.

**Claude reported boot check fs13 OK on 2026-11-12:** 502 log lines, OpeningEvent and
GameDataList loaded from this mod, no crash. He handed it to Kareem with a watcher on
`user-fast-start-next`. The played output is **frozen**. cs13a did not start a game or
add cs13b's item-bar change. **Kareem's subsequent gameplay FAILED at Mido (~08:44):**
Mido idled to the side, followed when approached, then the game hung on Talk while rendering
continued at 59.8 fps. No exception/crash was reported. Claude reported the lone 08:42:11 save
had blocker true, visit true and no sword/shield/Boomerang; no-equipment Talk is likely, not yet
confirmed. Loaded-mod proof is present for OpeningEvent (418), Kokiri Banc (602/603), and
child Mido flow (681) in `ingame/user-fast-start-next/hookshot_log.txt`. This is a logic/event
hang, not a failure to load the patch.

The original replay treated external InitTalk and presentation actions as inert and could
not certify waits/bindings. Static diagnosis must expand those dependencies, then compare
all four equipment states. Claude prefers preserving the native early meeting/idle state
and changing only the post-clear meeting advancement plus tree-talk side effects; the
Mido-skipped/open-forest path keeps initial Complete. New output/user names are required;
the failed played folder will not be rebuilt or deleted. Full gates must cover the replacement.

## Failed-wrapper diagnosis before replacement

`mido_hang_registration.py` reproduces a registration-aware **static** failure for all four
equipment states: `ClawshotMidoStillBlocking` -> native `Event6` -> `Event222` (index 195).
The BFEVFL later entry still registers only `[174,175,148,128,176]` in `sub_flow_events`;
native `Talk` registers `[195,144,0]`. Thus the jump introduces a call not registered for its
active entry **before any sword/shield query**, regardless of inventory. The old replay did
not check this table. This is a definite structural defect in the patch.

`Event222` calls `InitTalk:InitTalk_Blocker`; its first action is `Event203`,
`Npc_Kokiri_Mido_Child` via argument `BlockerNpc`, `EventWaitFinishBlockerAction`,
`IsWaitEnd=true`. It precedes the initialization fork, every message and EndBlockerAI.
The subsequent fork joins all four branches normally. Native `EventSetting` default/later
rows are identical except row ID and entry; native `GameAnalyzedEventInfo` rows are also
identical (same four SubFlowList files, no child event list). No missing RSDB dependency or
new actor/action/query is evidenced. No message or EndBlockerAI is reached before the
missing registration. **Live-PC limit:** the static defect is certain; a silent engine stall
at that unregistered subflow is inference without an engine instruction trace. The blocker
wait itself is native on blocked re-talks; no schedule-dependent wait parameter was found.

**Idle-position inference:** pre-completing Meet_DekuTree changes the schedule: the component selects the
after-Step02/completed C1C2 schedule instead of native early blocking. The saved blocker
still enables following. The side position is not proof the wall cleared; the schedule also
selects the later entry whose stale registration makes the wrapper structurally invalid.
Restoring native early state removes this artificial schedule/state combination.

Bindings cross-check: all 13 native entry registrations match their reachable subflow calls.
The wrapper additionally omits reachable indices 144 (`Event91`, NpcCommon) and 0 (`Event1`,
local blocker-Trio init), though index 195 fails first with preset Complete. Existing key/gift
entry cloning also preserves/recomputes this table. No cross-entry jump may bypass it.

**Replacement (cs13a, following Claude's native-clear preference):** kept Mido receives no
initial tree-talk presets. OpeningEvent advances the native early state as usual. All actors,
queries, entries, entry registrations and native Talk/clear actions remain unchanged. Only
`Event48 -> Event0`'s clear tail adds bound GameData/Challenge actions: mark `_0070` seen,
request meeting Complete rather than Step03, forest stone GoInside, and mouth open.
Mido-skipped/open-forest selections retain initial presets and do not edit his flow.
No new subflow, actor/action/query or EventSetting/GameAnalyzedEventInfo dependency is added.

Focused native/synthetic check after replacement:
`CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -q tests/test_fast_start_mido.py tests/test_fast_start_mido_dump.py`
— **18 passed in 2.69s**. Registration-aware replay covers neither, sword-only, shield-only
and both equipped; keeps the original path up to the clear and checks native blocker waits,
fork joins and the resulting four values. It also reproduces the failed wrapper's missing
registration and checks kept/bypassed initial values. Presentation actions are not an engine
simulation; the replacement still needs a fresh in-game check.

## Replacement staged check: native Mido clear

- New root `E:/OOTRemake/work/r13-fast-start-cs13a/ingame-native-mido/`;
  launcher `Test - fast-start-native-mido.bat`, adjacent `CHECKLIST.md`, **20–30 minutes**.
  Created from the current launcher template for NEW GAME, CRLF. Empty `empty-new-game`
  source, fresh `user-fast-start-native-mido`, one real `fast-start-native-mido` mod.
  `HOS_FS_OVERLAY` cleared; failed output/user untouched. No cs13b changes added.
- Same public command/settings as the failed check, new output
  `mods/fast-start-native-mido/fast-start-native-mido`: seed 7, Chest-only, 165 checks,
  30 spheres. Newly generated play-note confirms sword far-right, 20 rupees far-left,
  Boomerang middle-left, Deku Shield bottom inner-right shelf for 10, dungeon Map in B1
  Basement Cobweb Chest; avoid the middle-right child Fairy Bow.
- `check_staged.py` exercised the actual written files: initial meeting and forest-stone
  **NotReady**, mouth and `_0070` false, blocker true, forest visit true. Registration-aware
  native/changed replay passes all four equipment states at **both Step01 and Step02**;
  refusals finish unchanged, both-equipped clear applies Complete/GoInside/mouth/seen only
  after native EndBlockerAI. All actor bindings and entry registrations equal native.
- Actual Mido flow **138,824 bytes**, allocation **139,120**; OpeningEvent **17,416 / 17,776**;
  GameDataList **1,462,888 / 1,463,176**. Required allocations fit; no movie-transition action.
  Single real mod/no links verified; launcher dry-run prints the new isolated user/mod paths
  and starts nothing. **Not boot-checked or played by cs13a.** Posted to `cs-r13` at 09:27.
- Related shop gift remains honest: existing child-only `at('KF Outside Deku Tree', is_child)`
  rule already requires reaching past kept Mido. The later native offer window does not
  grant a pre-Mido shield; no shop-gift logic relaxation is needed.
- After the preflight-order correction, a fresh public `make_seed` using the staged CS1
  reproduced the **entire frozen spoiler exactly**: no differing fields, including placements,
  spheres, opening and patch metadata. The staged files were not rewritten.

## Native-Mido played result (Kareem, via Claude)

**2026-11-12 11:35–11:46; A/C core checks PASS.** Claude reports:

- Opening movie skipped entirely; later scenes remain skippable.
- Forest pause map opens.
- Mido is in the correct **middle** position. Sword-only still blocks. With the shield
  added, dialogue opens the path; saves show blocker **true -> false at 11:40**.
- No Deku Tree dialogue; mouth open. The player reached the dungeon Map chest.
- **Reload passed (16:45–16:47; acceptance below).** Neither-equipped and shield-only live talks
  were not reported in this result; their registration-aware native replays passed.

Read-only runtime loading proof from the new isolated user's `hookshot_log.txt`:
GameDataList **59**, OpeningEvent **410**, Kokiri Forest child dynamic/static Banc
**1093/1094**, child Mido flow **1152**. Every `mods: <file> <- <path>` points at
`ingame-native-mido/mods/fast-start-native-mido/fast-start-native-mido/romfs`, not the failed
frozen candidate. No game was started or controlled by cs13a.

**Separate issue, not a fast-start regression:** the dungeon Map chest opens with map
text/animation, but `DungeonInfo.InsideTheDekuTree.IsGetMap` remains **false**. Claude assigns
the own-dungeon map/compass credit bug to **cs13c** and states this fix stands. Do not claim
the Map pickup was credited, and do not fold its repair into this branch.

Docs/UI now reflect the observed movie-removal pass rather than saying unplayed.
The matrix's immutable source is implementation commit `240600a`; the later UI-help change
only updates played status, not settings, generation or patch behavior.

## Verification

Focused replacement/return-pool regression run: **32 passed in 75.78s**. Actual browser UI
smoke after the preflight-order repair: Chest-only + open door returns HTTP 400 and visibly
names the settings, configured first-pull inventory, inaccessible Ocarina/Saria checks and
closed-door/Gift alternatives. Recommended + open door returns HTTP 200 with that choice
retained and no alert. No JavaScript errors; owned hidden tab/server closed. Screenshot:
external `return-kit-ui-refusal.webp`. No game was started.

The full serialized run used `tools/review_gates.sh`, workers **1**, retained log
`E:/OOTRemake/work/r13-fast-start-cs13a-final-gates.txt`. Claude confirmed it acquired
the lock at 10:30:05; the 10:42 waiting-lock statement was stale.

| Initial command | Observed result |
|---|---|
| `ruff format --check` | rc 0; 322 files already formatted |
| `ruff check` | rc 0; all checks passed |
| `pytest` | rc 0; 1,072 passed, 144 skipped; 976.27 s |
| `pytest -m dump` | rc 1; 124 passed, 1,074 deselected, 18 setup errors; 2,315.63 s |

All 18 errors are `OOT_DUMP` cases in `test_pack_nup_dump.py`: the default
`E:/OOTRemake/work/pr1-check/dump` lacks
`RSDB/GameAnalyzedEventInfo.Product.111.rstbl.byml.zs`. The NUP and feature cases passed.
Claude identified the cause: that shared fixture contains only the 0.1.1-era working set;
0.2.0's key compiler added this resource. This is **stale fixture data, not a production
code failure**. No production/test code was changed to suppress it and no case skipped; no unchanged rerun.

Per Claude's 2026-11-12 instruction, copied external `pr1-check/make_dump_folder.py`,
changed only `OUT` to `E:/OOTRemake/work/rounds/r13/dump-fast-start`, and ran it from this
worktree. **1,242 wanted files; base 1,207; update 48; same 1,194; missing 0.**
The fresh base/update layers resolve every current resource, including the missing RSDB
in `updates/131072/romfs`. Its fingerprint equals the read-only reference:
`fc09c4af707a0ca092188cf014f6fdf3d40514def773f097b798f52f9f28bc93`.
The old fixture was not edited; Claude owns its merged-main rebuild at integration.
Superseded full-tree extraction was stopped and its owned output/script removed.

Only `tests/test_pack_nup_dump.py -m dump -k OOT_DUMP` was rerun under the shared lock,
`OOT_DUMP` pointing at the new fixture. Separate retained log:
`E:/OOTRemake/work/r13-fast-start-cs13a-oot-dump-rerun.txt`.
**rc 0; 18 passed, 19 deselected in 1,585.77 s (26:25).** The original report retains all
18 setup errors; this report records their corrected-input pass. The initial 124 native
passes were not rerun. No NUP, synthetic or broader dump rerun was substituted.
The matrix's prepared guard accepts the original successful gates plus exactly these
corrected 18 cases, retaining both reports.
It uses
the immutable `witness/after-native-mido-src` snapshot (208 source files; manifest SHA256
`d9f0232a0c18c4f6b90bab81356e83dcb803e16b30d19f5ec6e8312615469633`).
Open/closed rows precede extra song_only rows; already recorded baseline rows are resumed,
not repeated. No full-matrix pass is claimed yet. A/C core checks passed in game as recorded
above; reload remains pending, and the separate map/compass credit defect belongs to cs13c.

### Ordered matrix pause (12:52)

Preserved **71 complete after records: 55 generated, 16 expected refusals, zero unexpected
failures**, all valid JSON; the 118 existing baseline records are unchanged. The last
complete after row is Recommended / closed_deku / closed / seed 1 / intro+deku_tree.
The unfinished row is excluded. This is partial evidence, not a complete matrix verdict.

The record-boundary watcher timed out, so only the owned runner/process tree was stopped;
this was not a graceful full-chunk completion. Only the unchanged, owned 12:39:52 gate
lock was released after checking its identity and the absence of another active sweep or
pytest. No foreign process or lock was touched.

Claude's order is cs13b full gates, cs13c full gates, then this matrix (position 4), followed
by cs13b's private comparisons. No matrix runner or gate waiter is active. Resume retained
rows only after the ordered handoff; do not repeat completed rows. Reload remains pending.

**14:19 order update (Claude):** cs13b's full gate ended with four dump failures, not a
pass: three `written_files_differ` / `ZsError` cases involving uncompressed Sequence
`.ainb`, and one gift-slice failure (`no gift item is held`). cs13c's full gates are now
running at position 3. Position 4 is cs13b's rerun of those four cases after its fix;
this matrix moves to **position 5**, and cs13b's private comparisons to position 6.
Keep the matrix stopped until the ordered handoff. Hookshot is running: use one worker.

### Rebase and evidence provenance (Claude's 15:52 instruction)

Rebased cleanly onto main `fa6f4ef`; resulting branch head `e187ca6`. The old snapshot's
208-file checksum list differs from this source in seven files: the played-status intro
help text and six dungeon-compiler files. The changed `make_seed` invokes that compiler
before returning, so the 71 historical after rows cannot stand in for this integrated
public path. They remain untouched in `after-native-mido.jsonl`, not counted toward the
new verdict. The unchanged `base-30ba5c9` / `baseline.jsonl` resumes its 118 retained rows.

The replacement immutable snapshot is
`E:/OOTRemake/work/r13-fast-start-cs13a/witness/after-e187ca6-src`, created by
`git archive e187ca6 -- src`. Source tree: `53b0be4277ac436cb0ff5816667f5fe3654e6b46`;
archive SHA256: `1318ac3584c9635476952516a0ff389c0f29dba6652ba09fdfd57a7deb55027f`.
`SOURCE_STATE.txt` records its provenance. The runner now selects that snapshot and
`after-e187ca6.jsonl`, with separate current-source logs and summary.

A lightweight smoke imported the public CLI from this exact snapshot, printed and
validated closed forest / closed Door of Time / intro+deku_tree skips, and observed the
expected clear validation refusal for Chest-only / open Door of Time. Exit 0; no native
generation, mod writing or game launch. This is not a witness or full-gate pass.

cs13c reports its four gates passed and released the lock at 15:43:46. Its old-position
handoff was flagged on the thread: Claude's 14:19 order still requires cs13b's corrected
four-case rerun before this matrix at position 5. No heavy runner or gate waiter is active.
The earlier full fast-start gates remain evidence for their original source, not a new
whole-rebased-branch gate run. Matrix and reload evidence remain pending.

### Native-Mido + reload acceptance: PASSED (Kareem, 16:45–16:47)

Claude reports Continue in the same staged user folder, with three snapshots matching
`save-backups/2026-11-12_164*-r13-mido-reload-1..3`. `check_player_save.py` on the newest
`slot_01` (16:47:17) reports the expected persisted state:

- `Mido_Child_Blocker = False`
- `IsVisitLocation.KokiriForest = True`
- `Step_Meet_DekuTree = Complete`

The reported runtime log has no crash and 15 mod-loading lines, including
`Npc_Kokiri_Mido_Child`, `OpeningEvent`, `GameDataList` and the KokiriForest banks.
The reported slot thumbnail shows young Link beside Mido at the Deku Tree tunnel mouth.
These are Claude's save/log/thumbnail observations, not a replay by this agent.

Kareem subsequently confirmed, via Claude, that talking to Mido finished normally and the
Deku Tree's mouth was open after Continue. Together with the persisted save state and
no-crash/mod-loading evidence above, Claude accepts **native-Mido + reload as PASSED**.

Gates and matrix are separate, still pending. Claude explicitly requires the ordered GO
before either starts; no heavy job or gate waiter has been launched.

### Superseding order: integrated source only (Claude, 17:05)

Read the complete cs-r13 post and Claude's direct confirmation. Position 5 is now cs13b's
250-seed public-generation sweep on `6174a3b`, with default outer attempts, not attempts=1.
Only after every seed generates does Claude merge that branch into main.

At position 6, this branch rebases onto that resulting main, freezes the integrated source,
and runs its required gates plus matrix together on that source. Claude will give GO then.
The `e187ca6` snapshot and earlier rows remain retained preparation/historical artifacts,
not final integrated-source proof. Do not launch the old prepared source or count its
historical rows toward the integrated verdict.

cs13b's tier experiments stay paused at position 7; cs13d's read-only Gerudo-card count
queues after position 6. No heavy job or gate waiter is active here before Claude's GO.
