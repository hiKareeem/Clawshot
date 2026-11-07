# AGENTS.md: rules for coding agents working on this randomizer

Read this file, then `README.md`, `plans/00-roadmap.md` and `plans/01-architecture.md`, before changing anything.
The plan for the area you are touching is the spec. If code and plan disagree, stop and say so rather than picking
one.

Kareem owns the project, with a co-owner (a senior software engineer). Product calls (what gets shuffled, settings,
names, license) are theirs: write the question into `plans/decisions.md` (Open) instead of deciding it.

## Hard rules

1. **No game data in the repository, ever.** No romfs or exefs files, no decompressed or decoded copies (BYML as
   JSON/YAML, text dumps, models, textures), no generated mod folders or seeds' output, no keys. Allowed: code,
   logic files, and location definitions (file path, actor hash, a human name, the vanilla item's actor name).
   Test fixtures are synthetic: built by code in the test, never cut from the game.
2. **The dump is read-only.** Read it from `OOT_ROMFS` (e.g. `E:\Games\Hookshot\romfs`). Never write, move or
   delete anything under it: a Hookshot rebuild replaces it, and a folder build may hard-link it to the player's
   original files. Everything the generator writes goes to its output folder.
3. **Correctness is checked against an oracle, not by eye.**
   - Formats: every placement file in the dump must round-trip (read, write, read gives the same tree; byte-identical
     where the writer allows). Tests marked `dump` run over the whole dump when `OOT_ROMFS` is set and skip otherwise.
   - Logic: every generated seed passes the beatability search (`plans/01-architecture.md`) before it is written.
   - In game: a change counts as working only after a run in Hookshot shows it (the log line
     `fs: OpenFile(...): from the overlay` plus the in-game result). Ask Kareem for the in-game check; say exactly
     what to do and what he should see.
4. **Determinism.** Same seed, settings and generator version give a byte-identical output folder. No unseeded
   randomness, no iteration over unordered sets in placement code, no timestamps in output files.
5. **Stable location IDs.** A location is identified by its source file and the actor's `Hash` (or, for event
   gifts, the event flow and node), never by a list index or position.
6. **Logic is data.** Regions, exits and requirements live in data files with a short rule language, not in Python
   branches. Each requirement notes where it came from: ported from OoT Randomizer (file and line) or verified in
   the remake (who, which build). N64 tricks and glitches do not carry over until verified in the remake.
7. **Permissive dependencies only** (MIT, BSD, Apache-2.0, ISC, Zlib) until the license is decided. OoT Randomizer
   and Archipelago are MIT (OoT Randomizer's GPLv2+ folders excepted): their code may be ported with attribution
   in `NOTICE`. zeldamods `oead`/`evfl`/`byml-v2` and dt-12345's AINB are GPL-2.0: read their docs and behaviour,
   don't copy their code.
8. **Changes to Hookshot go upstream.** Mod loading and code hooks are contributed to `NotRexed/Hookshot` as small,
   single-issue PRs from the `hiKareeem/Hookshot` fork (checkout at `E:\OOTRemake\Hookshot`). Never vendor a
   patched Hookshot into this repo.
9. **If a first attempt fails, print the values instead of trying again** (the parsed node, the offsets, the
   assertion payload), then fix the cause they show or stop and hand off. One rerun after a change aimed at a
   printed cause is fine; an unchanged rerun is not.

## Commands to run before you call anything done

```sh
uv run ruff format --check
uv run ruff check
uv run pytest                              # synthetic fixtures only
OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump   # when the change touches formats or census
```

## Definition of done

The milestone's acceptance criteria in `plans/00-roadmap.md` are shown by test output, the commands above pass,
and `plans/decisions.md` records anything decided along the way (with who proposed it).

## Parallel work

One agent per track and per directory (`plans/00-roadmap.md` lists the owners). Don't edit another track's
directory; ask in your handoff instead.

## Commits

Small and scoped. Agent commits end with `Assisted-by: <model>`. Never commit with `git add -A`; add your own paths.
