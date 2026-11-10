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

Fail-closed support check reads the actual bin executable through read-only mmap for its
HOS_MODS and mod-discovery diagnostic markers. It never trusts folder/version labels or starts
the executable to probe it. Unknown/older binaries stop before user/log creation; no overlay
fallback. Actual installed executable (470277120 bytes) has both markers at438474625/438474774.
This is capability detection, not a cryptographic guarantee for arbitrary modified binaries.

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

## Player acceptance boundary

**Kareem: after Claude reviews/rebuilds a fresh pack, Make, then Play only after quitting the
current game. Require one seed mod, `mods: <file> <- <path>`, expected seed placements,
isolated New Game and later Continue. Controller icons in text will be the game's own.
The agent never starts Play except its no-start dry run.** Full two-source smoke, documentation,
upstream-candidate report and complete gates follow in item order.
