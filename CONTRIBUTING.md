# Contributing to Clawshot

Clawshot is an unfinished, unofficial randomizer. Small fixes, remake logic evidence, documentation
and tests are welcome. Discuss larger changes in [Discord](https://discord.gg/7R5ZXPcJqn) first.
Kareem and his co-owner decide product behavior and merge contributions.

## Licence and sources

By submitting a contribution, you agree to license it under Clawshot's [MIT licence](LICENSE)
(inbound = outbound). You must have the right to contribute it. Keep existing copyright and permission
notices. Cite any ported work by project, file and commit in [NOTICE](NOTICE).

- Dependencies and reused code must be permissively licensed: MIT, BSD, Apache-2.0, ISC or Zlib.
- Do not copy code from GPL or unlicensed projects. A public download is not permission to reuse it.
  OoT Randomizer's MIT portions are usable; its GPL folders are not.
- Do not read or use NX2navi code or documentation for an AI-assisted contribution; its licence
  forbids AI use. No material from it is accepted here.
- Hookshot is GPL-3.0. Facts may be researched with a file citation, but do not copy its code or
  assets into Clawshot. Runtime loading/hooks belong upstream in Hookshot, not in a vendored fork.
- Guides and walkthroughs may supply facts with a URL citation, never copied text.

## Never submit game data

**No game files or anything generated from them in a PR, issue, comment or attachment.** This includes
RomFS/ExeFS resources, keys, decoded trees or text dumps, models, textures, saves, generated seed mods,
spoilers and extraction caches. Do not link to downloads of them. Test fixtures must be synthetic,
created by code in the test, never extracted from the game.

Allowed location definitions are identifiers and human labels: source path, actor Hash, name and
vanilla item's actor name. Keep decoded research and generated output outside the repository. Read
your own dump in place, never modify it. Do not write to the game installation or shared save backups.
Build changed seeds into new output folders, never over a folder a player may be using.

For a report, provide the seed number and settings string, exact source revision/pack metadata,
steps, expected/observed result and a **reviewed plain-text log excerpt**. Remove private paths,
usernames and credentials. Logs must not contain dumped game resources or decoded data. If uncertain,
ask on Discord before attaching anything. Do not upload saves or `spoiler.json`; name only the relevant
location/reward in the report, marking spoilers.

## Preparing a change

1. Read [AGENTS.md](AGENTS.md), [README](README.md), the [architecture](plans/01-architecture.md),
   [roadmap](plans/00-roadmap.md) and the plan for the area. Keep to the documented contract; flag a
   disagreement rather than choosing a new product behavior. Automated contributors must follow AGENTS.md.
2. Use a branch and a small, single-topic PR. Explain the problem, evidence, change and remaining limits.
   Do not add unrelated refactors or silently change defaults, check eligibility or beatability guarantees.
3. Keep stable location IDs: placement source file + actor Hash; event flow + grant node for gifts.
   Put access rules and their provenance in world data, not Python branches. Unverified N64 tricks do
   not carry over to the remake. See [logic reference](docs/logic.md).
4. Preserve determinism: same source/world data, settings and seed must reproduce identical output bytes.
   Do not introduce unseeded randomness, timestamps or unordered placement iteration.
5. AI assistance is welcome; disclose it in the PR and in each assisted commit with a trailer, for example:

   ```text
   Assisted-by: <tool or model used>
   ```

   Human review, licensing and evidence requirements still apply. Do not feed prohibited sources to an AI.

## Checks

Install [uv](https://docs.astral.sh/uv/getting-started/installation/); Python 3.12+ is required.
From the repository root, use the locked dependencies and run:

```sh
uv sync --frozen
uv run ruff format --check
uv run ruff check
CLAWSHOT_WORKERS=1 uv run pytest
```

The environment prefix above is for a POSIX/Git Bash shell. In PowerShell use
`$env:CLAWSHOT_WORKERS = '1'` before `uv run pytest`. Without a dump, native-data tests skip.
For format or census changes, also check your own read-only supported dump (path is an example):

```sh
CLAWSHOT_WORKERS=1 OOT_ROMFS=C:/Games/OoT/romfs uv run pytest -m dump
```

In PowerShell set `$env:OOT_ROMFS = 'C:/Games/OoT/romfs'` before that pytest command.
NUP/cache changes also need the matrix documented in [seed packs](docs/seed-pack.md).
Record exact commands, results and skipped coverage; never call a skipped native check a pass.
Do not overlap full suites or seed sweeps on a shared playtest PC. Use one worker while the game runs;
internal contributors follow the shared gate-lock procedure in [orchestration](plans/02-orchestration.md).

On a failure, print the actual values/log/assertion that explain it before changing anything. Do not
repeat an unchanged failing command hoping it passes. A focused rerun after fixing the printed cause
is appropriate. Do not weaken a check or reduce seed coverage to hide a failure.

## In-game evidence for behavior changes

Automated file round trips and beatability tests are necessary, but do not prove the game uses a
changed file or grants the item correctly. A change remains **built, untested in game** until observed.
Kareem performs the project's acceptance checks; AI agents do not start his game or open test windows.

Supply a precise checklist: supported game build, runtime/version, seed/settings, Link's age and
required inventory/story state, exact location and steps, expected reward and actual result. For
once-only checks include refusal/failure, leave/re-enter and Save and Continue; verify usable inventory,
not only a model or notice. Use an isolated new user/save copy and only the Teleport/clock cheats unless
a step explicitly needs something else. Never alter the original save or a played output.

On Hookshot 2.0.12+, evidence that the resource loaded is its **`mods: <file> <- <path>`** log line
(the loader logs the first 200 files) plus the observed game result. Clear `HOS_FS_OVERLAY` and use the
mods route: the overlay route crashes with Clawshot's size table. The current process/save-isolation
requirements are in [orchestration](plans/02-orchestration.md); players should use the
[seed-pack guide](docs/seed-pack.md). For another runtime, provide its own loading log and result;
Hookshot evidence does not certify an emulator. Keep untested boundaries explicit.

## Questions and reports

Use the GitHub bug/logic templates or [Discord](https://discord.gg/7R5ZXPcJqn). Include the exact
source revision as well as seed/settings; settings strings do not promise compatibility between
versions. Do not request or distribute the game, keys, generated mods or saves.
