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

Keep decoded research and generated output outside the repository. For the complete repository
data/safety rules and allowed location definitions, see [AGENTS.md](AGENTS.md), rules 1–2.

For a report, provide the seed number and settings string, exact source revision/pack metadata,
steps, expected/observed result and a **reviewed plain-text log excerpt**. Remove private paths,
usernames and credentials. Logs must not contain dumped game resources or decoded data. If uncertain,
ask on Discord before attaching anything. Do not upload saves or `spoiler.json`; name only the relevant
location/reward in the report, marking spoilers.

## Preparing a change

1. Start with [README](README.md), [settings](docs/settings.md) and, for logic changes,
   [the logic reference](docs/logic.md). The [plans folder](plans/README.md) is the maintainers'
   evidence/design record, not a workflow you need to join.
2. **Contributing with an agent? Have it read [AGENTS.md](AGENTS.md) before making changes.**
   That file is the shared authority for game-data safety, read-only dumps, oracle checks,
   determinism, stable IDs, sourced logic, dependency licences and failure diagnosis.
   Do not restate or replace those contracts in a new agent-specific workflow.
3. Use a branch and a small, single-topic PR. Explain the problem, evidence, change and remaining
   limits. Discuss product/default/logic-policy changes with the maintainers; do not silently
   change them or add unrelated refactors. Include affected docs and meaningful regression coverage.
4. AI assistance is welcome; disclose it in the PR and in each assisted commit with a trailer, for example:

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
Use one worker on a shared playtest PC and avoid overlapping heavy runs. The maintainers' parallel
agent workflow, including its gate lock, is separate: [orchestration](plans/02-orchestration.md).
It is not required for ordinary contributions. Diagnose failures under [AGENTS.md](AGENTS.md), rule 9;
do not weaken a test or reduce coverage to hide one.

## In-game evidence for behavior changes

Automated file round trips and beatability tests are necessary, but do not prove the game uses a
changed file or grants the item correctly. A change remains **built, untested in game** until observed.
Kareem performs the project's acceptance checks; AI agents do not start his game or open test windows.

Supply a precise checklist: supported game build, runtime/version, seed/settings, Link's age and
required inventory/story state, exact location and steps, expected reward and actual result. For
once-only checks include refusal/failure, leave/re-enter and Save and Continue; verify usable inventory,
not only a model or notice. Use an isolated new user/save copy and only the Teleport/clock cheats unless
a step explicitly needs something else. Never alter the original save or a played output.

The loading-log-plus-game-result requirement is [AGENTS.md](AGENTS.md), rule 3. On current
Hookshot the relevant line is `mods: <file> <- <path>`; include the exact resource and observation.
For safe runtime setup use the [seed-pack guide](docs/seed-pack.md), not an old overlay launcher.
For another runtime, provide its own loading evidence; Hookshot evidence does not certify an emulator.

## Questions and reports

Use the GitHub bug/logic templates or [Discord](https://discord.gg/7R5ZXPcJqn). Include the exact
source revision as well as seed/settings; settings strings do not promise compatibility between
versions. Do not request or distribute the game, keys, generated mods or saves.
