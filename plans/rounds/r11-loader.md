# Round 11, Track C: Hookshot loading (cs11c)

Branch `r11/loader`. Required AGENTS/README, plans00–04, decisions, round9/10 records,
sections39/42, R11-HOOKSHOT-2012 and crash/headless-boot evidence read. Shared-file opening
applies: README belongs to A; no dependency edits. Dump, installation and save backups read-only.
No game, batch, bootcheck, window, Hookshot build, merge, push, stash or terminal-control command.
Scratch: `E:/OOTRemake/work/r11-loader-cs11c/`. Initial tasklist: no Hookshot process.
Every pytest explicitly uses CLAWSHOT_WORKERS=1. Full gates acquire/release r11/gate.lock.

## Item 1: urgent Play cutover

Play now clears HOS_FS_OVERLAY and overrides HOS_MODS with the extracted pack root.
Existing `seed/romfs` is the sole mod; no moved/copied seed or linked folder. Discovery checks
use facts from Hookshot v2.0.13 `HookshotBuilder/tools/host/mods.c:116–147`: root itself is
not a mod; descend at most4 levels, skip dot/dash/underscore names, stop at romfs/exefs.
Reject any visible traversed link or any second mod, including an unexpected user/romfs.
The existing digest rejects links within the seed; hidden NUP caches are never traversed.
An independent synthetic walk exercises these rules on an actual made pack directory.

Support detection reads the actual bin executable through read-only mmap for HOS_MODS
alone; log wording is not a compatibility contract. It never trusts folder/version labels
or starts the executable to probe it. Builds without that marker stop before user/log
creation; no overlay fallback. Actual installed v2.0.13 executable (470277120 bytes) has
HOS_MODS at438474625. This is capability detection, not a cryptographic guarantee.

Added Play --dry-run (also CLAWSHOT_DRY_RUN=1): all real checks, JSON launch plan, no process,
user folder or log. It keeps the bin-only executable, updater suppression and isolated --user.
Synthetic main/dry-run smoke observes the effective overrides despite inherited overlay/mods.

Focused format/lint passed; `CLAWSHOT_WORKERS=1 uv run pytest tests/test_pack_loader.py
 tests/test_pack.py -q --basetemp E:/OOTRemake/work/r11-loader-cs11c/green-loader-next`:
**23 passed,0.42s**. Red new-path probe printed unrecognized --dry-run before implementation;
no game was launched. Initial shell failure127 printed wrapper resolution; selected the installed
`C:/Users/hi/.local/bin/uv.exe`. Initial pytest setup printed missing external parent; created it.
No unchanged failed command was retried without addressing its printed cause.

Item1 commit is an urgent review checkpoint, **not ready before all four full gates**.
README request posted on cs-r11: replace overlay loading with HOS_MODS and retain save isolation.

## Added reviewer request (after item 1)

Provide one read-only public Hookshot detector for cs11d: executable, optional version,
RomFS, adjacent NUPs, mods support and reason seed Play cannot start. Play uses the same
check. Post the committed symbol/return fields immediately. No Hookshot source code is copied.

### Shared detector delivered

`clawshot.pack.hookshot.detect(folder: Path | str) -> HookshotInfo` is read-only.
Frozen dataclass fields: `folder: Path`, `exe: Path` (always the expected bin path),
`version: str | None`, `romfs: Path | None`, `nups: tuple[Path, ...]` (sorted sibling
files, case-insensitive extension), `supports_mods: bool`, `reason: str` (empty if playable).
Version supports the installed `version=...`/`builder=...` file and a plain one-line value.
Play imports this function: one binary-capability policy, no execution or fallback.
Focused detector/loader/existing pack checks: **33 passed,0.46s**, format/lint passed.
Actual read-only detection reports v2.0.13, bin executable, RomFS, one adjacent NUP,
supports_mods=true and empty reason. No file byte/mtime changes in synthetic detection.
The first actual detection exposed the key/value version format; corrected parsing before commit.

## Item 2: player instructions

Both READ ME FIRST.txt and docs/seed-pack.md now describe the game's own Switch icons
in text as expected while a seed is loaded. Never delete its size table to restore icons.
Manual route: copy made seed/romfs to a named Hookshot mods child, real folders, one seed,
no HOS_FS_OVERLAY. Explicit main-save/New Game overwrite/back-up warning; disabling the mod
does not restore saves. Play remains the safer isolated route. Emulator steps are unchanged.
Removed the summary's obsolete random-Bowling warning against Round10's implemented first/
second deterministic rewards; no generation behavior changes. Player-facing summary reviewed
directly; actual two-source source-pack/Make/dry-Play proof follows next.

### Native environment correction before final smoke/gates

A no-game native subprocess probe printed Python getenv='' and C-runtime getenv=b'' when
the child environment contains an empty value. `host/nn_fs.c:279–289` tests only whether
getenv returned non-null, so an empty value can still enter overlay lookup. Play now removes
HOS_FS_OVERLAY entirely from its child environment; dry plans explicitly list it under
`unset_environment` rather than setting an empty value. Focused33 tests pass in0.47s;
format10/lint pass. The initial actual baseline/RomFS/NUP smoke already passed (260.36s,
137 files,193 ZIP entries each, identical baseline digest68a95611e704adf8d016ada69729593dcdb19e14aa6635cd9195a5fb1c24d76b).
Those first two archives predate this stricter clearing correction and are superseded:
fresh final source packs/Make/dry-Play will exercise actual removal before the full gates.

## Item 3: completed actual two-source smoke (no game)

Final `smoke.py` completed exit0 in244.67s after e3fbb96. Ran the real public publisher
once from RomFS and once from the NUP, then actual Windows PowerShell setup.ps1 -Action
make on each fresh extraction (first-setup path, answers via stdin). Both Make outputs
verify; both real runtime Play --dry-run commands exit0. No batch or game was started.
New artifacts are `romfs-unset-pack-next.zip`/`nup-unset-pack-next.zip` and respective
`*-unset-make-next` folders under this track's scratch; earlier packs remain untouched.

Each ZIP has193 source-only entries. Each seed has137 files, identical across input
routes and identical to the publisher oracle from the exact pre-track source (`87c03da^`,
archived and run separately). Complete output SHA256:
`68a95611e704adf8d016ada69729593dcdb19e14aa6635cd9195a5fb1c24d76b`.
This track changes no generator/resource/output digest.

Independent Hookshot-rule walks of both actually made pack folders find **only seed**,
even with an intentionally added hidden interrupted-cache folder and disabled mod folder.
Dry plans print only bin/hookshot.exe, per-pack --user, update suppression, HOS_MODS=pack,
and explicit HOS_FS_OVERLAY removal despite deliberately inherited wrong values.
All seed bytes AND mtimes stay unchanged; neither user nor hookshot_log.txt is created.
Evidence: `pack-smoke-unset-proof.json` and six `*-unset-{publisher,make,dry-play}.log`
files. This is launch-plan/source-generation proof, not an invented gameplay result.

The final four-command gate runner follows this successful smoke, serially, using
CLAWSHOT_WORKERS=1 and a separate atomic gate.lock acquisition/finally release for each
full pytest command. Native gates also set OOT_NUP to exercise the full cache matrix.

## Item 4: report-only upstream candidate

Section45 cites the exact GPL release-source files/lines read for facts only:
host/mods.c, host/prompts.c, host/nn_fs.c and nx2/prompt_assets.py in the v2.0.13 builder.
Current mod-table fallback and overlay mismatch match the supplied crash/save-mount logs.

Proposed Hookshot-only change: compose a private runtime table from the **winning mod
table**, raise only the External font entry to the installed generated-font requirement,
keep already-larger/unrelated/named entries intact, then allow generated text icons if
no mod supplies its own font. Never substitute the vanilla-derived prompt table, alter
seed bytes or mutate installed game/mod resources. Cache by actual winning-table content/
font allocation; retain native fallback for custom fonts, malformed/unknown tables or merge
failure. Effective overlays would need the same accounting before larger fonts are used.
This is explicitly [INFERENCE], not an implemented or tested Hookshot fix; the report names
upstream synthetic/boot/player acceptance. No Hookshot code copied, edited, built or booted.

Section45 follows43 on this base; Claude inserts Track B's44 before45 at review. No invented
placeholder section and no decisions.md/README edit. README requests were posted to A.
Merged main's later docs/UI/keys changes require a **new** integrated source pack; these
branch-local proofs never authorize rewriting an old/played seed or reusing its digest.

## Player acceptance boundary

**Kareem: after Claude reviews/rebuilds a fresh pack, Make, then Play only after quitting the
current game. Require one seed mod, `mods: <file> <- <path>`, expected seed placements,
isolated New Game and later Continue. Controller icons in text will be the game's own.
The agent never starts Play except its no-start dry run.** Source-pack smoke and report are
complete; full-gate results below will establish readiness, not in-game certification.

For the branch-local final smoke packs (digest above), not the older played seed8:

1. Extract `romfs-unset-pack-next.zip` OR `nup-unset-pack-next.zip` into another fresh
   folder; Make with the matching source and Hookshot folder; require Verified seed.
2. After quitting the current game and Claude's review/boot check, Play and start a new
   isolated game. If any cheat menu is enabled, use **Teleport and clock only**, never
   inventory, age or flags. Check dialogue text uses Switch icons with normal controls.
3. Enter Mido's house and face its four chests. Left to right: **Longshot, Piece of Heart,
   Kokiri Sword, Boomerang** (read directly from the new actual spoiler/note). Prefer the
   middle/right checks first; after child Longshot pickup, **Save and Continue** before
   using other items. Confirm item notices/inventory and working Boomerang as child.
4. Require log `mods: seed: 135 RomFS files` and one mod, plus
   `mods: Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs <- <this pack>/seed/romfs/...`
   and the native-icons fallback line. Mods file proofs are capped at the first200 opens.
5. Save, quit and Play again: Continue retains these pickups in **this pack's user**;
   the main playthrough was never copied/reset. Attach this pack's hookshot_log.txt and
   pack.json, never seed/cache/save/game bytes.

An integrated rebuild can legitimately change assignments/digest; follow **its** note and
spoiler instead of these branch-local four rewards. These steps remain Kareem's, unrun here.

## Branch commit ledger

| Commit | Scope |
| --- | --- |
| `87c03da` | Item1 urgent single-mod Play cutover, fail-closed support and dry run |
| `67582d9` | Requested read-only shared Hookshot detector and synthetic tests |
| `44f9147` | Item2 player summary, native icons and manual-mod/main-save warnings |
| `e3fbb96` | Native-probe correction: remove inherited overlay variable entirely |
| `0b87f63` | Item3 completed final RomFS/NUP publisher/Make/dry-Play proof |
| `16bdc44` | Item4 source-cited upstream candidate and section45 |

All commits remain on r11/loader; none merged or pushed. No dependency changes.
Removed only completed session-created smoke.py and the duplicate external report draft;
source archives, generated outputs and all evidence JSON/logs remain outside the repository.
After successful completion removed only this session's external gates.py driver as well.
All generated output/user/game/save-backup folders remain untouched.

## Full gate evidence

Both pytest gates use CLAWSHOT_WORKERS=1, absolute external forward-slash basetemps and
exclusive r11/gate.lock ownership. No production/test changes during the final chain.
All observed results are recorded below; an in-progress stage is not counted as a pass.

| Complete command | Observed result |
| --- | --- |
| `uv run ruff format --check` |261 files already formatted; exit0 |
| `uv run ruff check` |All checks passed; exit0 |
| `CLAWSHOT_WORKERS=1 uv run pytest` |836 passed,110 skipped;1187.76s; exit0 |
| `CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs OOT_NUP=<full NUP path> uv run pytest -m dump` |109 passed,837 deselected;1981.21s; exit0 |

All946 tests collected. Native109 includes the full NUP cache-only/full-RomFS matrix;
no selected dump test skipped. No extra retry, narrowed seed range, relaxed oracle or test
change during the gate chain. Runner wall times: synthetic1188.28s, dump1981.89s.
Observed stdout records acquired/released for **each** lock and ALL FOUR GATES PASSED.
Logs: `gate-{format,lint,synthetic,dump}.log`; command/exit/timing evidence: gate-results.json.

## Final handoff

Ready for Claude's code review on r11/loader: all four ordered track items plus the requested
shared detector are committed and exercised. The final evidence-only commit follows the
ledger above; its actual hash is posted on cs-r11 rather than self-referenced here.

Remaining external work: review/merge, combine section44/45 and the public-doc/UI/keys changes,
rebuild a **new** integrated pack and use its own digest/note. cs11d consumes the detector
contract in67582d9 directly after integration. **Kareem's exact isolated New Game/Continue,
placements and native-icons check above remains unrun by this agent.** No source/runtime
change to Hookshot, PR, dependency edit, unauthorized rebase, merge or push was made here.

## Review follow-up to 06d05b4

Claude requested five changes; his subsequent version correction supersedes the original
point2. Implemented:

1. `detect()` gates only on HOS_MODS. Log format strings are not a compatibility contract;
   removed the second marker from the decision rather than adding another public field.
   Synthetic detection and actual runtime dry-Play fixtures now succeed with HOS_MODS alone.
   A diagnostic string without HOS_MODS still refuses, independent of version labels.
2. Requirement: a Hookshot that can load mods (tested on2.0.13), not an asserted first
   supporting version. The overlay-crash statement correctly retains **2.0.12 and later**,
   sourced by R11-HOOKSHOT-2012 and the supplied crash logs, as Claude clarified.
3. READ ME FIRST uses the requested plain Play/update steps; its manual route is two lines
   pointing to the technical guide and warning about main saves. Icons and Bowling use
   the requested player-facing wording, without variables or the rental/table advice.
4. The technical guide keeps its mod-layout, environment, digest and save-safety details,
   but explains update/refusal in plain words. Section45 and this report agree with the
   revised single-marker policy.
5. Missing-support reason is exactly: “This Hookshot build cannot load mods. Update
   Hookshot, then run Play again.”

Tasklist found Kareem's Hookshot PID28256 running; all commands were serial and pytest
explicitly used CLAWSHOT_WORKERS=1. Per Claude's requested review scope, **no full suite,
dump test, source-pack regeneration, game/launcher start or rebase** was run. He runs
full gates after rebasing on main. Existing pack outputs and saves remain untouched.

| Review command | Observed result |
| --- | --- |
| `uv run ruff format --check` |261 files already formatted |
| `uv run ruff check` |All checks passed |
| `CLAWSHOT_WORKERS=1 uv run pytest tests/test_pack.py tests/test_pack_hookshot.py tests/test_pack_loader.py tests/test_pack_nup.py -q --basetemp E:/OOTRemake/work/r11-loader-cs11c/review-focused-next` |46 passed in0.91s |

The dry-Play smoke in that focused run exercises the real checked launch-plan path with
only HOS_MODS in the synthetic executable, without creating user/log files or starting it.
The earlier full-gate table describes06d05b4, not a new full-gate run on these revisions.
The follow-up commit's actual head is posted on cs-r11 for Claude's rebase/gate/merge.
