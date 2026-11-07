# AGENTS.md: rules for coding agents working on Clawshot

Read this file, then `README.md`, `plans/00-roadmap.md` and `plans/01-architecture.md`, before changing anything.
The plan for the area you are touching is the spec. If code and plan disagree, stop and say so rather than picking
one.

Kareem owns the project, with a co-owner (a senior software engineer). Product calls (what gets shuffled, settings,
what a seed must guarantee) are theirs: write the question into your round file (below) instead of deciding it.
How rounds run, who launches and reviews: `plans/02-orchestration.md`.

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
7. **The project is MIT; dependencies must be permissive** (MIT, BSD, Apache-2.0, ISC, Zlib). OoT Randomizer and
   Archipelago are MIT (OoT Randomizer's GPLv2+ folders excepted): their code may be ported, credited in `NOTICE`
   with file and commit. zeldamods `oead`/`evfl`/`byml-v2` and dt-12345's AINB are GPL-2.0: never copy their code
   into the repo. A research script outside the repo (under `E:\OOTRemake\work`) may use them unmodified.
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

## Working in parallel

- One agent per track, each in its own git worktree and branch (`r<N>/<track>`), set up by Claude before you
  start. The round's section in `plans/00-roadmap.md` lists what each track owns; don't edit another track's
  files. The main checkout (`E:\OOTRemake\Clawshot`) only receives merges.
- **Don't merge.** Commit on your branch; Claude reviews it and merges it to `main`. Rebase on `main` only when
  Claude says it moved. Never push. Never `git stash` (all worktrees share one stash).
- **Your round file** is `plans/rounds/r<N>-<track>.md`, yours alone: what you built, how it was checked (commands
  and their results), choices you made provisionally, and questions for Kareem in **bold**. Never edit
  `plans/decisions.md`; Claude moves decisions there at review.
- **Cross-track requests** go in your round file and as a plain post:
  `~/go/bin/bermuda thread post --thread cs-r<N> --as <your track name> "<text>"`. No @-mentions (they deliver
  into another agent's pane), no other bermuda command than `thread post` and `thread log --thread cs-r<N>`, and
  never set `BERMUDA_THREAD_AGENT`. Never message another agent through herdr. Claude reads the thread and
  answers by steering you.
- **In-game checks are Kareem's.** Never start `hookshot.exe` from E:\Games\Hookshot or touch that folder. Write
  what he should do and see into your round file. (A Hookshot build track may boot its own test build headless;
  its prompt says how.)
- Paths: give native programs (python, uv, git) Windows paths such as `E:/OOTRemake/...`, never Git Bash's `/e/...`.
  Delete only what you created in this session.
- Finish with a handoff: what is on your branch (commit ids), what was checked, what is left.

## Commits

Small and scoped. Agent commits end with `Assisted-by: <model>`. Never `git add -A` or `git add .`; add named paths.
