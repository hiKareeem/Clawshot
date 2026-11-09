# Round 9, Track C: seed packs and map floors (cs9c)

Branch `r9/seedpack`, base `4a0a2f3`. Required AGENTS, README, plans00–04, decisions,
round7/8 records and r6-names read; Round9 opening/shared-file rules apply. No dependency change,
fill/CLI edit, merge, push, stash, game/launcher/batch execution, window or terminal-control command.
Dump, seed8 active output and all save backups are read-only. Scratch: `E:/OOTRemake/work/r9-seedpack-cs9c/`.
Commands were launched serially; the pre-steer full suite still contained an internal8-worker pool.
That earlier safety gap and its effective cap are corrected below. Initial tasklist found no Hookshot.

## Item 1: private source-only packs

Implemented `python -m clawshot.pack --settings CS1... --seed N --out <new.zip>`;
publisher supplies `--romfs` or OOT_ROMFS. Source/data/locked metadata/license/NOTICE included;
plans, tests, environments, outputs, decoded data and game bytes excluded by positive file selection.
Reference is generated from the exact shipped source snapshot in an external disposable directory;
only its whole-output SHA256 is included. Fixed zip metadata and entry order.

Make asks once for RomFS and Hookshot, stores paths only after preflight, invokes frozen uv and
refuses to overwrite existing seeds. Play verifies bytes again before user/log creation and starts
only bin/hookshot.exe with update checks disabled and per-pack --user. Missing bin is a hard stop.
The approved new-game chest-ocarina-storms batch supplied the launch/isolation pattern; no game started.

RomFS contains no NSO build-ID header. Provisional engineering choice by cs9c: fingerprint four known
supported files (ZsDic, GameDataList, EventSetting, child Kokiri Dynamic) to identify build e0f3ccfa
before uv/generation, rather than trust a directory label/Hookshot version. Both PowerShell preflight
and Python compute SHA256 over the four lowercase SHA256 strings with LF. This is not an exefs-ID or
whole-dump integrity assertion; complete generated output must independently match the reference digest.
Only hash values are derived game content in the zip; fingerprint paths are identifiers already used by source.

Tester guide updated in the shared Discord document; separate small commit to be posted.
**Kareem: packs and source remain private to invited testers. After code review, test a pack in a new
external folder: Make -> Verified seed; Play -> isolated new game; require overlay-open log and expected
Mido placements. The agent will not execute Play or any launcher.**

Actual public pack CLI plus extracted Windows PowerShell **Make-only** path passed. Seed8's original
effective CS1 replays **287 checks,24 spheres,129 overlay resources**; all **131 files** including
spoiler/note match `E:/OOTRemake/work/r8-full/seed-full-8` byte-for-byte (same relative paths, none missing).
Reference/extracted/baseline SHA256 all
`a82ac11d0aa0dcb81611c762f4145fe03e0c796d2aecd189e2199bbb64bb49ec`.
Zip has **180 entries**, the required source/templates/license metadata, no plans/tests/seed/game formats.
Proof: external `pack-proof.json`; private artifact `seed-8-private-net-next.zip` and extracted sibling.
These are review artifacts, not a release before TrackA's item-bar guidance/fix is integrated.
No batch, Play, executable or window started; only setup.ps1 `-Action make`.

All five new safety regressions pass: wrong-version pre-generation refusal, complete-tree digest changes,
existing seed non-overwrite, changed-seed launch refusal, missing-bin no-fallback and game-folder isolation.
All four complete gates passed serially before the floor source/data cutover; no Python/TOML/test mutation
during that chain. Basetemps: external `item1-synthetic-next`, `item1-dump-next`. No test was filtered.
**Correction:** this was one pytest invocation, not one worker: the inherited world-data test internally
selected up to8 workers. These passes remain functional evidence, not proof of resource-rule compliance.

| Full command | Observed result |
|---|---|
| `uv run ruff format --check` |229 files already formatted |
| `uv run ruff check` |All checks passed |
| `uv run pytest` |726 passed,86 skipped;319.11s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` |85 passed,727 deselected;1402.32s |

812 tests collected. Initial tasklist in this chain reported no matching Hookshot process.
Item1 commits: `9370057` pack/tests/source-only oracle, `92aec67` isolated README/Discord guide,
`cc7047a` reviewer-requested Lichii/save-safety docs. Runtime proof is branch-local, not a claim about
the future merged source. No in-game acceptance is invented.

### Diagnostics before gate checkpoint

First scoped lint printed E501 at pack writer's 126-character context manager; split the context
manager, then format/lint passed. First pytest basetemp setup printed WinError3: external parent
did not exist; created the session's external scratch directory, then all five safety regressions passed.
No test body was run in that setup failure.

First real pack generated successfully, but Windows PowerShell preflight printed `Get-FileHash`
not recognized and stopped before generation on the tester side (exit1). Replaced that cmdlet with
streaming .NET SHA256, retaining the same exact signature format. Also included the repository's
`.python-version` (`3.12`): the first disposable source snapshot without it selected installed3.14.
Removed inherited VIRTUAL_ENV in the publisher's child. No game/launcher was invoked in either probe.
The cause-aimed second proof uses a new `seed-8-private-net-next` zip/folder, never rewrites the first.

## Item 2: room and pause-map floors

Read-only research began after item1 commits `9370057`, `92aec67`; gates remain serial.
The authoritative mapping is **Banc/BancBasedResource/MapParam.byml.zs**, not RSDB/DungeonParam,
Scene/Component/DungeonParam, MapMenuInfo or MapCaptureInfo (those were inspected first).
`<area>.Room[Dynamic.DefaultDungeonRoomIndex].Floor` stores signed logical floors (0=1F,
-1=B1); `<area>.Floor[slot]` starts at `MinFloor` and lists chest `TBox.InstanceID` hashes.
Use the exact icon's floor when a room spans multiple floors, never chest height or N64 room names.

All **134 existing dungeon chest descriptions** resolve:126 by exact icon Hash,8 Ganon trial
chests absent from icon lists by their single-valued room floor. No unresolved/multi-floor guess.
The Remake map texture filenames independently agree with displayed labels (Deku B2..3F,
Well B2/B1, Jabu B1..2F, Fire1F..5F). GTG and Ganon have stored map floors but no matching
floor-texture set; no newly observed pause-map surface is claimed for them.

Fire Temple: exactly **16 chests /5 Skulltulas**, matching Kareem's guide-map count; map icon lists
independently hold16 TBox and5 CollectSign entries. Chest floors:1F five,2F one,3F six,4F zero,
5F four. The timed trio's two extra red-rupee chests and the old Scarecrow check are all5F,
alongside the Hammer. The Bomb-floor shortcut chest is2F even though the boulder maze is3F.
No guide text or decoded map tree goes in the repository.

Boss-heart research first printed KeyError Dynamic for Volvagia's native pickup; the exact actor
payload has no Dynamic override. Printed all eight existing identities plus MapParam.BossRoomId:
seven explicit room values agree; Volvagia uses the unique boss room33, floor0=1F. This is a
boss-room identity join, not a guessed actor default. Implemented coverage includes eight already-supported
BossHeart descriptions and the Ice Cavern Sheik lesson at the mapped Iron Boots chest.

**Kareem: compare the timed trio with Fire5F and the shortcut cell with2F on the pause map.
GTG/Ganon have floor metadata but no shipped dungeon-floor texture set: confirm whether the pause UI
shows a floor number there; until observed, their labels describe stored floor metadata, not a proven UI.**

### Implemented and exercised

Catalogue now has369 descriptions with143 structured floor labels (134 chests,8 native boss pickups,
1 lesson). The one reader renders the floor in names used by spoiler, note and location hints; its
new floor field serializes independently of label punctuation. Logical keys/IDs/rules stay unchanged.
Removed three old hard-coded Deku floor prefixes so a label does not repeat its floor twice.
Python LSP references returned no server; literal fallback found only the one LocationName constructor
and existing spoiler/hint consumers; all consumers use the same reader. Shared reader/coverage edits
are isolated; no fill/CLI/settings/patch algorithm change.

Scoped checks: format/lint passed; names/route/presentation **12 passed**; independent native floor
oracle **1 passed** (0.76s), covering every definition, basement offset, tall-room distinction,
visible floor tokens and physical-ID coverage. The external researcher's first native run printed
Forest Boss Key Hash5306318520835485827 with **no explicit room**, but exact map-icon logical floor2=3F.
Its overstrict room assertion was removed only for exact-icon matches; aimed rerun reports all143
facts with126 icon/8 room chest matches. Production oracle already used the correct icon-first order
and passed on its first attempt. No fake room0, height fallback or narrowed oracle.

Actual public generator CLI, original seed8/effective CS1 into fresh `floors-seed8-next`: **exit0**.
All131 output paths remain; placements and chronological spheres are exactly unchanged.
**142 shuffled locations** display their correct floor (the excluded Well check remains excluded).
The printed play-note rows show timed Scarecrow5F, cracked-floor pit2F, Deku vine-wall2F,
Volvagia pickup1F. Only spoiler/note,16 Mals hint archives and the common size table differ from
r8-full. No Banc, flow, GameData or item placement delta. Retained `floors-output-proof.json`,
`floors-cli.log`, `floor-facts.json` and reusable `floors.py` outside the repo.

All four complete gates passed again on this final floor cutover with the effective single-worker cap (below).

## Coordination

Posted cs-r9 as cs9c: item order, no planned shared fill/CLI edit, supported-dump fingerprint and scratch-only
output. No request for another track's source files. Python LSP has no configured server (marksman only);
the floor-reader references attempt/fallback is recorded above. No existing pack/CLI API is replaced.

Reviewer steer: cs9b `806b1c7` changes Sheik text in16 Mals archives. The exact-r8-full comparison
is branch-local historical proof only. Pack `build()` computes each oracle by generating from the source
snapshot it ships, never from a stored r8-full seed digest. Claude will rebuild into a NEW zip/folder after
merges (floor-labelled hint names also legitimately change Mals). Posted acknowledgement on cs-r9.

Reviewer docs-only steer: Kareem played seed8 successfully in Lichii (Eden/yuzu family), recorded on
main `d3e5c08` in answers R9-LICHII. That new answer is not in this worktree's base; the reported
player result is accepted, not rerun. Added Lichii's confirmed LayeredFS destination and Add-ons steps
to `docs/seed-pack.md` and the Discord tester guide; clearly marked Ryujinx/Atmosphere paths untested.
New Game takes over this game's emulator save slots: back up first; Hookshot user isolation does not
apply; unticking a mod does not restore saves. No Make/Play behavior change. No emulator/window started.
Current Make still asks for a valid Hookshot folder; the emulator instructions replace only Play.

Removed only the completed session-created smoke_pack.py driver after its successful proof;
reference zip, extracted output, proof JSON, player checklist and reusable floor researcher are retained.

## Reviewer CPU-safety steer and effective local cap

Kareem's two crashes at100% CPU and overlapping gate runs are accepted ground truth (not rerun).
Immediately cancelled own active `bg_6` gate chain and exported `CLAWSHOT_WORKERS=1` persistently.
Cancellation output reached shop_logic, before world_data; it is **not a completed gate pass**.
No rebase or seed-sweep retry. Prior “no pools/one worker throughout” wording above is retracted:
launching one pytest process did not limit its inherited internal seed pool.

Printed this branch's exact cause: `_failures` unconditionally used `min(os.cpu_count() or1,8)`
and **did not read CLAWSHOT_WORKERS**. Prefix alone therefore could not cap this old branch.
Read main `c9e2e2b`'s actual test-only diff and ported its exact selector as isolated `33ec1e7`,
without rebasing, changing seed ranges/logic/oracles, or waiting for another track. Actual native
helper smoke printed `CLAWSHOT_WORKERS='1', selected_pool_workers=1`. Posted the effective fix.
Every remaining pytest command explicitly prefixes `CLAWSHOT_WORKERS=1`, even after this port;
scripts and seed sweeps remain one process. Fresh full-gate basetemps will be separately named.

Before the cancelled pytest started, the additional actual Make guard smoke completed successfully:
existing Make exit0 verified the historical digest and left **all131 files' contents/mtimes unchanged**;
synthetic wrong-RomFS Make exit1 printed fingerprint
`419f15a59889f04f9deac50060c071f7bdb1a7f0da9c75a252db370f1038048c`
versus expected `fc09c4af707a0ca092188cf014f6fdf3d40514def773f097b798f52f9f28bc93`,
before uv environment/output creation. Retained `pack-guards-proof.json`; no Play/batch/game run.
Format230/lint passed in that cancelled chain; **all four full commands were restarted and completed**
under the now-effective cap (below). No incomplete/cancelled pytest is presented as a pass.

## Commit ledger and handoff boundary

| Commit | Scope |
|---|---|
| `9370057` |Item1 source-only builder, Make/Play, digest/version guards, synthetic tests, guide/section39 |
| `92aec67` |Isolated shared README/Discord private-pack instructions |
| `cc7047a` |Reviewer-requested confirmed Lichii path, untested alternatives, save backups/New Game warning |
| `0c7cd7b` |Historical branch-local replay and first full gates; later CPU wording corrected above |
| `502799d` |Isolated shared names reader: structured floor and common label rendering |
| `2d2f8ca` |Item2 native floor facts, boss pickup descriptions, native map oracle, coverage/docs |
| `33ec1e7` |Exact upstream c9e2e2b test-only worker cap, no rebase |
| `bbc27b4` |Runtime/version reporting and each runtime's own log, not a nonexistent emulator Hookshot log |

After successful smoke proof removed only session-created driver/staging files:
smoke_pack.py, smoke_floors.py, smoke_guards.py, the two applied patch artifacts and the external
duplicate test staging copy. Reusable floors.py, JSON/log evidence, new CLI outputs/private zip,
and the player checklist remain outside the repository. No output/user/save/game folder was deleted.

The final gate chain uses **CLAWSHOT_WORKERS=1 on both full pytest commands**, with external
`capped-synthetic-next` and `capped-dump-next` basetemps. Source/data/tests are frozen since33ec1e7;
only report/log-guide Markdown was edited during that chain. Its completed results are below.

### Left for review / player acceptance

- Claude reviews/merges this branch, preserves section39 after37/38, and rebuilds a **new** private
  pack from merged source (including Sheik/item-bar changes); no stored r8-full digest is reused.
- **Kareem:** after review, follow external `seed-8-check.md` for Make/isolated new-game Play,
  expected starting items, overlay-open log and per-pack Save/Continue. No agent Game/Play run is claimed.
- **Kareem:** compare Fire's timed trio5F / shortcut cell2F with the fresh note. This branch's seed8
  placements are unchanged, so comparison does not require rewriting the active seed or swapping a live overlay.
  GTG/castle pause-floor UI remains the explicit question above; metadata labels are not in-game certification.
- Lichii loading is Kareem's reported acceptance, not an agent rerun; emulator New Game must follow a full
  save backup. Ryujinx/Atmosphere compatibility is still untested, not silently inferred.

## Final complete gates — effective cap, all green

Every selected test ran, with no narrowed seed range, retry increase, skip addition or oracle weakening.
813 tests collected. No source/data/test mutation after the cap commit. Both pytest commands explicitly
used `CLAWSHOT_WORKERS=1`; the actual helper smoke had already selected exactly1 worker.

| Complete command | Observed result |
|---|---|
| `uv run ruff format --check` |230 files already formatted |
| `uv run ruff check` |All checks passed |
| `CLAWSHOT_WORKERS=1 uv run pytest` |726 passed,87 skipped;1628.43s |
| `CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` |86 passed,727 deselected;787.21s |

Full chain completed exit0 in2417.59s. External basetemps are `capped-synthetic-next` /
`capped-dump-next`. All86 selected dump tests pass, including the new complete native map-floor
oracle and the existing format/census, seed, gifts, shops, hints and pickup deltas. No dump skip.
The unchanged full200-seed/default plus20-progressive-seed oracle now executes through the capped pool.
Earlier uncapped functional passes and the explicitly cancelled chain are superseded for final readiness.

## First-setup Make acceptance and final readiness

After the capped full gates completed, exercised the **real first-setup path** in another fresh
extraction of the historical source-only zip (`seed-8-first-setup-capped-next`). Supplied both folder
answers through stdin to setup.ps1 `-Action make`; no pre-created folders.json, no mocked generator.
First Make exit0 saved the two correct paths and generated all131 reference-identical files.
Second Make, **with no input**, exited0, verified the same digest and changed no seed-file mtimes.
`first-setup-proof.json` records both exits, the digest,131 paths, and no game user/log creation.
Console capture is `first-setup-make.log`. No batch, Play, window or game was started.

Tasklist showed Kareem's Hookshot already running for this last smoke; no test or second seed process
overlapped it. CLAWSHOT_WORKERS remained1; the Make/generator chain used one worker. Removed only the
completed smoke_first_setup.py driver afterward; the new extraction/output and proof/log are retained.

**Track C ready for code review/merge on r9/seedpack.** Both numbered items and both emulator-documentation
requests are complete, all four final gates pass under the effective cap, and actual builder/Make/name
surfaces were exercised. No merge, push, stash, dependency edit, live-output rewrite or agent game run.
The player checks and merged-source pack rebuild above remain explicit external acceptance, not claimed done.

## Reviewer correction: emulator-only Make after 6fb5569

Claude identified a real route blocker: both setup.ps1 and runtime.configuration required Hookshot's
bin executable even for Make. Reproduced before the fix with the new omitted-Hookshot regression:
Make CLI returned 1, stderr `error: 'hookshot'`, rather than verifying the valid local seed.

Changed only setup.ps1, runtime.py, test_pack.py, both tester guides and this round note:

- First Make asks for RomFS and **optional** Hookshot; blank means emulator and is saved as blank.
  Supplied Hookshot paths are still normalized and saved. Make never requires a Hookshot executable.
- Both preflights validate the RomFS version **before** optional Hookshot normalization/overlap checks.
  All supplied folders remain protected against overlap; blank Hookshot is not resolved to cwd.
- Only Play requires Hookshot and `bin/hookshot.exe`. With no Hookshot folder it stops before any
  launch/profile/log and points to `docs/seed-pack.md (Emulator / console loading)`.
  Missing bin still refuses the root launcher. Make's success text now names both loading routes.
- Both guides explain leaving Hookshot empty and requiring no installation for emulator Make.
  Emulator save-backup/New Game warnings remain unchanged.

### Scoped verification requested by Claude

All pytest invocations explicitly used `CLAWSHOT_WORKERS=1`, sequentially; no pool/sweep or overlapping
generation/test process. No core generator, floor data, CLI, dependency or shared-plan change.
Per the reviewer's scope instruction, did not repeat the full gates already recorded for 6fb5569.

| Command / scenario | Observed result |
|---|---|
| New targeted tests, `-k "make_without_hookshot or emulator_only_play or version_failure_precedes_optional"` | 8 passed, 5 deselected, 0.20s |
| `CLAWSHOT_WORKERS=1 uv run pytest tests/test_pack.py` | 13 passed, 0.21s |
| `uv run ruff format --check src/clawshot/pack/runtime.py tests/test_pack.py` | 2 files already formatted |
| `uv run ruff check src/clawshot/pack/runtime.py tests/test_pack.py` | All checks passed |

Permanent coverage includes omitted/empty Hookshot and a supplied non-installed path for Make,
omitted/empty Hookshot Play refusal, version failure preceding optional-folder checks, both RomFS
overlap directions with no Hookshot, and the existing supplied-Hookshot overlap/root-launcher guards.
The digest-refusal test now supplies a synthetic bin file so it reaches the digest check in Play;
that file is never executed.

Actual surface smoke, fresh external source snapshot `emulator-only-source-next`, real PowerShell
setup and real generator, no mock generation:

- Deliberately wrong manifest fingerprint stopped before folders.json, .venv or seed existed.
  Actual fingerprint `fc09c4af707a0ca092188cf014f6fdf3d40514def773f097b798f52f9f28bc93`;
  expected all zeroes. No config/output was written by the rejected preflight.
- First Make consumed the real RomFS answer plus **blank Hookshot**, exited 0, saved the blank answer,
  and generated all 131 files identical to the already-proven floor-aware `floors-seed8-next`.
  This smoke reuses that branch-local oracle, not the historical r8 digest or a new published zip.
- Second Make with **no input** exited 0; all seed-file mtimes and bytes remained unchanged.
- setup.ps1's no-Hookshot Play guard exited 1 with the emulator-guide message before uv/launch.
  This was only a negative guard check: no batch or game executable was run.
- Make with a supplied overlapping Hookshot folder exited 1 with the overlap error, preserving output.
  No game user directory/log was created. Complete serial smoke took 52.90s.

Output/reference SHA256: `85d2490f2aa2a856bd3f120ffca174b84201420fc7f1cdc17146157edd7611da`.
Retained `emulator-only-proof.json` and `emulator-{wrong-version,first-make,second-make,no-hookshot-play,given-folder-overlap}.log`
under `E:/OOTRemake/work/r9-seedpack-cs9c`. Removed only this session's completed smoke driver.
No in-game acceptance is claimed. Claude still rebuilds the private pack from merged source after review.

