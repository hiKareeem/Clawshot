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
`NOTICE` attributes these paths/commit. No writer, extraction utility or dependency is introduced.
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
