# Round 10, Track C: NUP dumps in seed packs (cs10c)

Branch `r10/nup`. Read supplied AGENTS rules, README, plans00–04, decisions and round8/9 reports;
Round10's opening/shared-file rules apply. Dump, NUP and save backups remain read-only. No game,
batch/Play, GUI, Hookshot build, terminal-control command, merge, push, stash or dependency edit.
External scratch/evidence: `E:/OOTRemake/work/r10-nup-cs10c/`. Initial tasklist found Hookshot PID44680;
all commands/generation are serial, every pytest uses `CLAWSHOT_WORKERS=1`. Full gates use the shared
`E:/OOTRemake/work/rounds/r10/gate.lock` directory and release it immediately in a finally path.

## Item 1: NUP or extracted RomFS

Publisher `--romfs`/`OOT_ROMFS` and Make's existing dump-path answer now accept either source.
The generator's public CLI/filesystem contract, fill, settings and patchers are unchanged. Make's
optional Hookshot answer remains optional; Play's bin-only executable/isolation protections stay.
An already-generated seed is verified without rebuilding it or making a new cache.

### Reader and licence

[a55uka/nup](https://github.com/a55uka/nup), pinned
`a4840f06c94ddeb414eea5b33c9704ffe995f11c`, MIT, Copyright2026 a55uka.
Vendored only `tools/nup/nup/{read,format}.py`, plus full upstream licence under `pack/_nup/`.
The two source files are unchanged except leading ruff/formatter guard comments, so upstream
comparison remains straightforward. Pack positive selection explicitly includes the MIT licence.
`NOTICE` attributes these paths/commit. No writer/CLI/extraction module or dependency is introduced;
the intact upstream format module still contains its unused record-packing primitives.
PyPI's package called `nup` is an unrelated project (`github.com/albertas/nup`), not this reader.
No NX2navi source/docs, GPL code or unlicensed randomizer was opened or used.

### Source, preflight and private working set

Use only the newest base/update full RomFS for one title, not add-ons or a base/update file union.
Ambiguous/missing/incomplete newest packages refuse; an unsupported newer update never silently
falls back to an older supported base. Validate the upstream TOC and bounds, safe/unique member
names and directory traversal, then verify each selected resource's actual SHA256 against its
NUP file record. Read the same four fingerprint resources directly inside the container.

Folder PowerShell preflight still needs no uv. NUP extents may use zstd, so NUP Make bootstraps
frozen uv/Python/zstd to run only the input preflight first. No saved folders.json, game-file cache
or seed exists before a successful fingerprint. This dependency bootstrap is not generation.
Python runtime independently rechecks input before cache/generation. No source path is ever written.

Provisional engineering choice by cs10c: disposable pack-local `.romfs-*` cache, not a second
filesystem protocol threaded through every generator/patcher. The bounded working set comprises
census placements/flows, supported item/shop packs, messages, dictionary/flag/resource tables and
selected fast-start components/parents. No ExeFS, model, texture or audio extraction. The cache is
unique per invocation and removed on success or exception; force-killed cache remnants stay private
and users should use a fresh extraction. Source-only ZIP selection never includes the cache/seed.

### Observed read-only source proof

`uv run python E:/OOTRemake/work/r10-nup-cs10c/probe.py`:
Kareem's NUP is25,020,741,061 bytes, one standalone-update package, version131072,
186,592 file records/601 directories. No file content is retained in the repo.

`uv run python E:/OOTRemake/work/r10-nup-cs10c/smoke_source.py`: NUP and folder fingerprints both
`fc09c4af707a0ca092188cf014f6fdf3d40514def773f097b798f52f9f28bc93`.
All1,239 cached generator resources /25,821,037 bytes match the extracted read-only RomFS exactly;
cache removal observed. `source-proof.json` records the result outside the repo.

### Focused checks / diagnostics

First scoped ruff run printed upstream style diagnostics (imports, original explicit file-handle
lifecycle, unused unpacked fields, line width), two new import-order diagnostics and one unused
fixture import. Kept vendored implementation pristine with two tooling-guard comments per file,
fixed only new-code imports, and formatted only the two authored Python files.

`uv run ruff check src/clawshot/pack tests/test_pack_nup.py`: passed.
`CLAWSHOT_WORKERS=1 uv run pytest tests/test_pack_nup.py tests/test_pack.py -q --basetemp
E:/OOTRemake/work/r10-nup-cs10c/focused-corrected`:25 passed,0.63s.
Synthetic NUPs are built from invented bytes by test code: raw/zstd/empty reads, exact folder
fingerprint, newest-package/no-base-fallback, incomplete newest package, corrupt TOC/content,
truncation, traversal/unsafe/case-colliding names and unchanged existing-seed reuse. No game fixture.

Actual publisher/PowerShell Make, complete gates, commit ledger and final handoff follow only after
observed completion; this checkpoint is not a ready claim. No in-game result is claimed.

## Actual publisher and PowerShell Make proof

`CLAWSHOT_WORKERS=1 uv run python E:/OOTRemake/work/r10-nup-cs10c/smoke_pack.py` completed
exit0 in184.46s, invoking the real public publisher with NUP input and seed8's actual effective CS1.
New archive `seed8-nup-next.zip`,189 entries, includes upstream MIT licence and no game/cache/seed files.
Fresh extractions `nup-make-next` and `folder-make-next` each ran the actual Windows PowerShell
`setup.ps1 -Action make`, with first-setup answers supplied through stdin and blank optional Hookshot.
No pre-created folder configuration, mock generation, batch, Play or game executable.

Both first Make runs exit0; each complete131-file seed matches the publisher reference:
`329021b92650c0b11c1d3230c925a4fe372f18226bc43b9e33b36736eb57e0ba`.
NUP and directory routes therefore produce identical overlay/spoiler/note bytes. Both no-input second
Make runs exit0 and preserve every seed file's bytes AND nanosecond mtime. No cache, user folder or
Hookshot log remains/was created by either Make route.

A third fresh extraction deliberately has expected fingerprint all-zeroes. Actual NUP PowerShell
preflight exits1, printing the supported actual fingerprint versus expected, before folders.json,
seed, user, game log or cache exists. The frozen reader environment may be installed first, as documented.
No failed positive command was repeated or narrowed. `pack-proof.json` and individual logs retain evidence.

Final scoped format/lint passed (9 files); focused pack suites now26 passed in0.43s after adding the
malformed-zstd-frame error regression. The optional dump oracle also covers complete cache equality and
unchanged NUP size/mtime. Full-gate source/tests are frozen; no source/test edit during the gate chain.

## Shared-file integration and player acceptance

Committed in item order: `f5a6249` is isolated NOTICE attribution; `2d8c41a` is the complete owned
item1 implementation/tests/docs; `4116069` is isolated section42. These are checkpoints, not a
ready claim before the full gates. Section42 currently follows39; reviewer inserts A's40 and B's41
before it, then D's43, preserving all tracks' findings without invented placeholders.

Posted a plain cross-track request on cs-r10: the new Door of Time patch may read native module
bytes outside the current generator working set. Track B/reviewer should supply its exact additional
RomFS read/patch paths for cache inclusion and an integrated NUP replay. A module-name reference
alone does not require extracting that module. Current NUP/folder equivalence proves this branch's
source snapshot, not an unmerged future generator. No other track's files are edited here.

Removed only the two completed session-created throwaway smoke drivers after retaining their
source/pack proof JSON and logs; new zips/extractions/seeds remain untouched outside the repo.

**Kareem: after review, extract `seed8-nup-next.zip` into another new external folder. Run Make,
give the full NUP filename and your Hookshot folder, require Verified seed, then Play only after
quitting the current game. Start a new isolated game; Mido's house from the doorway must show
far-left Magic Jar, middle-left Bow, middle-right Kokiri Sword, far-right Boomerang. After the child
Bow pickup, Save and Continue before using other items. Require the Kokiri Dynamic `from the overlay`
log and normal item grants/use, then confirm Continue retains this pack's own progress. No main save
copy/reset. This is the still-unperformed player check, not agent certification.**

For a newly rebuilt merged-source pack, use its own spoiler/note and newly computed digest instead
of this historical branch-local archive's placements. No existing played seed/output is regenerated.

## Reviewer steer: self-checking cache definition and door inputs

Claude requested a cache-only seed-generation oracle instead of trusting a hand-maintained list.
Cancelled the superseded gate chain, then printed native process/lock diagnostics: no own Python,
uv or pytest remained; gate.lock creation time exactly equalled the interrupted synthetic log's
creation time. Removed that owned lock immediately. Format245/lint passed in that chain; interrupted
pytest is NOT a pass, and fresh four-command gates will follow the expanded acceptance.

All literal cache paths/patterns now live in `pack/resources.toml`, included as ordinary source data.
The resolver derives actor names from existing item/shop catalogues and fast-start component/parent
paths from EventSetting. Later tracks add an input path in that one file; no second Python path list.

Claude supplied cs10b's20:43 input-path post. Existing patterns/fixed resources already cover both
Market Bancs, DoorOfTime flow, GameDataList, ResourceSizeTable and dictionary pack. Added only
`Logic/Market_Common_f252.logic.module.ainb`. This is source input coverage, not a Door of Time
gameplay patch or a claim that the unmerged setting exists on this branch.

Expanded `test_pack_nup_dump.py`: one temporary NUP cache; real CLI preparation/census/fill/search
AND writer from that directory alone for Chest, Shop, Gift, Scrub, BossHeart and Freestanding.
Additional full-kind rows cover every forest mode with all non-legacy fast starts, free travel,
song placement, price policies, partial/zero shelves, both hint modes and skips off. Each complete
output is compared path-for-path and SHA256-for-SHA256 with a separate original-RomFS generation,
so even silently absent glob members fail. Missing file exceptions name the RomFS input and the
cache data file; a deliberately empty cache tests that diagnostic. No generation fallback root.
All three door modes enter the matrix automatically once Track B's `Settings.door_of_time` field
exists after integration; this branch does not fake or skip tests for a nonexistent setting.

Scoped format/lint passed; existing synthetic pack suites26 passed in0.45s. The new cache-only
matrix runs under gate.lock with one worker. `docs/seed-pack.md` records its exact OOT_NUP command
for each reviewer rebase. No production/test mutation after this matrix starts; only reporting/docs.

Gate scheduling request posted to cs-r10: if the cache-matrix runner is waiting, give cs10c
the next free gate interval without interrupting an active run. All independent implementation,
data/door-path wiring, documentation and final smoke/gate-runner preparation are complete;
the matrix result is the prerequisite for the new pack smoke and replacement full gates.

## Completed cache-only matrix

`CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs OOT_NUP=<Kareem's full NUP filename>
uv run pytest tests/test_pack_nup_dump.py -m dump -v -x --basetemp
E:/OOTRemake/work/r10-nup-cs10c/cache-matrix-next`: **14 passed in1068.46s**.
The external runner acquired the shared directory lock after waiting in60-second steps, then
released it in its finally path as soon as pytest exited. No tests ran while another gate held it.
`cache-matrix.log` contains every collected row/result. No failed row, retry or filtered mode.

All12 supported-mode rows generated AND wrote from the cached directory alone and exactly matched
the independent full-RomFS output map (each relative path and SHA256, including note/spoiler).
The native cached-byte/source-size/mtime oracle and deliberately missing-input diagnostic also pass.
The new Door of Time module is part of that validated cache; actual door-mode rows are intentionally
conditional on the unmerged setting field, not falsely reported as exercised here.

New source-backed pack smoke and all four fresh full gates now run sequentially on the frozen
`8d35a95` production/test tree; later changes are reporting/attribution only. The publisher has
already exited0; final Make/gate results will be recorded after the entire chain returns.

## Shipped-data Make proof and gate-runner correction

`smoke_data.py` completed the actual publisher and first/repeated Windows PowerShell Make with
NUP input, all exit0. New `seed8-data-cache-next.zip` ships `pack/resources.toml` and the MIT
licence; fresh extraction is `data-cache-make-next`. All131 generated files retain digest
`329021b92650c0b11c1d3230c925a4fe372f18226bc43b9e33b36736eb57e0ba`.
Second Make preserves all bytes/mtimes; no cache, user or game log exists. `data-pack-proof.json`
and `data-{publisher,first-make,repeat-make}.log` retain this completed real surface proof.

The subsequent format gate refused two generated `LocationList.py` synthetic fixtures under a
session-created worktree directory. Printed exact cause using shlex: the old gate runner put
native backslashes in unquoted PYTEST_ADDOPTS, so
`--basetemp=E:\\OOTRemake\\work\\r10-nup-cs10c\\gate-synthetic-next` parsed as the drive-relative
`E:OOTRemakeworkr10-nup-cs10cgate-synthetic-next`, resolving inside this worktree.
The cancelled first synthetic run had created that directory; no dump-marked test ran there,
and all contents were invented synthetic fixtures, not native game data.

Printed/validated every49 directory-link target as internal to that exact owned basetemp, unlinked
only those links, then removed its275 session-created files/root without following links.
No original fixture was reformatted or test relaxed. Changed only the external gate runner to
use `Path.as_posix()` in PYTEST_ADDOPTS; printed shlex now preserves the absolute E:/ path.
Fresh corrected basetemps/logs use `gate-corrected-*`, never the failed/played output names.

Cause-aimed replacement chain: full format **245 files already formatted**, full lint **passed**;
the corrected full synthetic gate has acquired gate.lock. Both pytest invocations explicitly cap
CLAWSHOT_WORKERS=1; native dump also supplies OOT_NUP so the full cache matrix is not skipped.
All four commands will complete before any readiness/handoff post. This runner-only correction
changes no production/test code, generator setting, seed, retry bound or oracle.

## Branch commit ledger

| Commit | Scope |
|---|---|
| `f5a6249` | Isolated shared NOTICE attribution for the pinned MIT reader |
| `2d8c41a` | Item1 NUP reader/adapter, publisher/Make, synthetic/native checks, tester guide/readme and round record |
| `4116069` | Isolated shared section42 source/package findings |
| `8d35a95` | Reviewer steer: one cache data definition, door module input and full cache-only output matrix |
| `ecc631a` | Isolated shared section42 matrix/door-input documentation |
| `8f4876c` | Isolated NOTICE clarification: original format primitives remain, writer/CLI/extraction modules are absent |

The final evidence-only round-file commit follows the completed corrected gates; its actual hash
will be posted with the handoff rather than self-referenced. No merge, push, stash, dependency edit,
native game/save/active-output write or agent game/launcher execution.

## Final complete gates and handoff

The corrected four-command chain completed exit0 in3094.78s. Both full pytest invocations
used **CLAWSHOT_WORKERS=1**, external absolute forward-slash `gate-corrected-{synthetic,dump}-next`
basetemps, and separate atomic gate.lock acquisition/release. The runner printed release immediately
after each pytest process exited. No source/test mutation after `8d35a95`; no omitted/relaxed oracle,
seed substitution, retry increase or additional skip.

| Full command | Observed result |
|---|---|
| `uv run ruff format --check` |245 files already formatted |
| `uv run ruff check` |All checks passed |
| `CLAWSHOT_WORKERS=1 uv run pytest` |774 passed,103 skipped;1226.92s |
| `CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs OOT_NUP=<full NUP path> uv run pytest -m dump` |102 passed,775 deselected;1866.30s |

All877 tests were collected. Every102 selected native test passed, including the complete14-test
cache suite (12 cache-only/full-RomFS generation/write comparisons plus native-byte and missing-input
oracles), all existing format/census/gift/shop/seed/hint/chronological tests and the default seed sweep.
`gate-corrected-results.json` and four `gate-corrected-*.log` files retain full evidence outside the repo.
Earlier cancelled/format-failed chains are superseded, not represented as complete gate passes.

Removed only completed session-created smoke/matrix/cleanup/gate driver scripts; reusable read-only
`probe.py`, proof JSONs/logs, new source zips/extractions and every generated player output remain external.
No played folder, source dump/NUP, game installation or save backup was rewritten/deleted.

**Ready for Claude's code review on `r10/nup`.** Item1 and both cache-definition/native-matrix steers
are implemented and exercised. The six implementation/shared-doc commits are listed above; the final
round-file evidence commit's hash is in the thread/chat handoff. No merge, push or dependency change.

Left for integration/player acceptance:

- Claude reviews the small shared commits, preserves sections40/41/42/43 in order, and rebuilds a
  **new** source pack after merges. Re-run the documented cache matrix after each authorized rebase.
  Door closed/song_only/open rows activate when Track B's `Settings.door_of_time` exists; those three
  currently nonexistent-on-this-branch modes are **not** claimed exercised. Its native module is
  already included and byte-equal in the passed cache oracle.
- **Kareem:** the isolated Make/Play/new-game/Continue check above remains unperformed. Prefer the
  final data-backed `seed8-data-cache-next.zip` for this branch, or the reviewer's freshly rebuilt
  merged-source pack and its own spoiler/note. Require the overlay-open log plus actual grants/use.
  The agent never starts Play, a batch or the game.
