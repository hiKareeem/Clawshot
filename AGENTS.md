# AGENTS.md: rules for coding agents working on Clawshot

These rules apply to every coding agent, and every person, changing this repository. Read this file, then
`README.md`, `CONTRIBUTING.md` and `plans/01-architecture.md`, before changing anything. The plan for the area you
are touching is the spec, and `plans/00-roadmap.md` says where things stand. If code and plan disagree, stop and say
so rather than picking one.

Product calls (what gets shuffled, settings, what a seed must guarantee) belong to the maintainers: put the question
in your pull request or issue instead of deciding it.

## Hard rules

1. **No game data in the repository, ever.** No romfs or exefs files, no decompressed or decoded copies (BYML as
   JSON/YAML, text dumps, models, textures), no generated mod folders or seeds' output, no keys. Allowed: code,
   logic files, and location definitions (file path, actor hash, a human name, the vanilla item's actor name).
   Test fixtures are synthetic: built by code in the test, never cut from the game.
2. **The dump is read-only.** Read it from `OOT_ROMFS` (your own extracted romfs folder; a Hookshot install keeps
   one in its `romfs` folder). Never write, move or delete anything under it: a Hookshot rebuild replaces it, and a
   folder build may hard-link it to the player's original files. Everything the generator writes goes to its output
   folder.
3. **Correctness is checked against an oracle, not by eye.**
   - Formats: every placement file in the dump must round-trip (read, write, read gives the same tree; byte-identical
     where the writer allows). Tests marked `dump` run over the whole dump when `OOT_ROMFS` is set and skip otherwise.
   - Logic: every generated seed passes the beatability search (`plans/01-architecture.md`) before it is written.
   - In game: a change counts as working only after a run in the game shows it: the runtime's own proof that the
     changed file loaded (in Hookshot, the log line `mods: <file> <- <path>`) plus the in-game result. Never start
     someone's game or write into their game folder: say exactly what to do and what should be seen, and a
     maintainer runs the check you cannot.
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
   into the repo. A research script kept outside the repository may use them unmodified.
8. **Changes to the game runtime go upstream.** Mod loading and code hooks are contributed to Longshot
   (`git.magicbean.dev/MagicBeanDev/Longshot`, the continuation of Hookshot, whose repository has been offline since
   2026-11-13) as small, single-issue PRs. Never vendor a patched runtime into this repo.
9. **If a first attempt fails, print the values instead of trying again** (the parsed node, the offsets, the
   assertion payload), then fix the cause they show or stop and hand off. One rerun after a change aimed at a
   printed cause is fine; an unchanged rerun is not.

## Commands to run before you call anything done

```sh
uv run ruff format --check
uv run ruff check
uv run pytest                              # synthetic fixtures only
OOT_ROMFS=<your romfs folder> uv run pytest -m dump   # when the change touches formats or census
```

## Definition of done

The acceptance criteria of the work (the roadmap's, or the issue's) are shown by test output, the commands above
pass, and anything you had to decide along the way is written down with who proposed it: in the pull request, or
for an agent in a maintainers' round, in its round file.

## Maintainers' rounds

The maintainers run several agents in parallel rounds (one worktree and branch each, a round file, review and merge
by a reviewer). An agent started in a round also follows "Rules for agents in a round" in
`plans/02-orchestration.md`. Nobody needs those to contribute. `plans/` holds the maintainers' working notes and the
evidence the logic data cites; the paths and names in it are from their machines.

## Commits

Small and scoped. Agent commits end with `Assisted-by: <model>`. Never `git add -A` or `git add .`; add named paths.
