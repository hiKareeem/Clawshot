# How rounds run

Adapted from how Overread runs (Hermes' `project-inception` and `herdr` skills, and Overread's orchestration
skill). This file is the project's own version; where it differs from Overread, this file wins.

## Who does what

| Who | Does |
|---|---|
| Kareem and his co-owner | Product calls (what gets shuffled, settings, what a seed guarantees), in-game checks, playtests. |
| Claude (Hermes) | Plans each round in `00-roadmap.md`; sets up worktrees and the Bermuda thread; starts the omp agents in herdr panes and watches them; reviews each branch and merges it to `main`; runs the gates; records decisions in `decisions.md`; pushes `main` to GitHub after a round's review; opens Hookshot PRs from the `hiKareeem/Hookshot` fork (Kareem's standing OK for this project). Tells Kareem exactly what to test and when. |
| omp agents | One track each, in its own worktree and branch; commit on the branch, write a round file, never merge, never push. |

## A round

1. **Spec.** Claude writes the round into `00-roadmap.md`: tracks, what each owns (directories, files), numbered
   items in merge order, the test that proves each. Producer items name their consumers.
2. **Setup.** One worktree per track at `E:/OOTRemake/clawshot-r<N>/<track>` on branch `r<N>/<track>` (made by
   `E:/OOTRemake/tools/launch_hc.sh`), one for a Hookshot track at `E:/OOTRemake/hookshot-r<N>/<track>`. Bermuda
   thread `cs-r<N>` (`BERMUDA_THREAD_AGENT=claude ~/go/bin/bermuda thread new cs-r<N> --about "..."`).
3. **Launch.** From round 4, tracks run in herdr-core (`hc`), the Herdr desktop app's terminal core, not old herdr
   panes: `bash E:/OOTRemake/tools/launch_hc.sh <N> cs<N>a:<track>[:<model>] ...` makes the worktree, starts omp
   (in an app space when the window is open, else a plain `hc` terminal), sends the prompt
   `E:/OOTRemake/work/rounds/r<N>/<agent>.txt` with `hc send` once omp is idle, and writes the terminal address to
   `<agent>.term`. One watcher per agent (`bash E:/OOTRemake/tools/hc_watch.sh <address> <agent>` as a background
   job) and one on the thread (`thread_watch.sh`). Steer with `hc send <address> "<text>"`. From round 5 most tracks
   run on Kareem's OpenAI quota (`openai-codex/gpt-6.1-sol`, the launcher's third field) and one on the default
   Claude model; Claude reviews (Kareem, 2026-11-08: the Sol track kept working through round 4's Claude usage
   limit). `hc_watch.sh` stops on done, idle, blocked and error (a provider limit shows as error).
   Recipes and pitfalls: the `herdr` skill's `references/herdr-app-hc.md` and the overread-orchestration skill's
   `references/herdr-core-move.md`.
4. **During.** Claude answers thread posts and gaps in a spec by steering the agent (a queued note, no restart).
5. **Review.** Per track: the handoff from its session file, its round file, the diff, the gates on the branch;
   then merge to `main`, gates again on `main`, decisions moved into `decisions.md` with who proposed them.
6. **Kareem's checks.** One message with what to run, where, and what he should see, in order.
7. **Cleanup.** Close each merged track's terminal (`hc kill <address>; hc rm <address>`, or `herdr-app do
   space.close` for an app space), then `git worktree remove` and delete the branch.

## Gates

```sh
uv run ruff format --check
uv run ruff check
uv run pytest
OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump
```

## What differs from Overread

- **No build folders.** Python worktrees are small; disk is not a constraint on the number of tracks.
- **The game dump is outside every repo** and read in place (`OOT_ROMFS`) from all worktrees: nothing to copy or
  link. Decoded game data goes only to `E:/OOTRemake/work/`, never into a worktree.
- **In-game checks need Kareem and one running game.** Agents never start the game in `E:/Games/Hookshot`. A
  Hookshot build track may boot its own test build headless and muted for at most 20 s. From Hookshot v2.0.1 the
  folder's `hookshot.exe` is a launcher that ignores `--user` and starts the main save with the caller's overlay:
  every test launcher starts `E:\Games\Hookshot\bin\hookshot.exe` with `HOOKSHOT_NO_UPDATE_CHECK=1` and stops if it
  is missing.
- **Kareem's in-game tests run on a copy of his saves.** The game keeps one playthrough across the `slot_NN`
  folders (TotK-style save slots, not N64 files): round 1 and 2's "new game" tests overwrote five of the six
  slots holding his main game. Tests start from `E:/OOTRemake/work/r2-test/Clawshot test.bat` (or a copy for the
  round): it resets a test user folder from a save backup, sets `HOS_FS_OVERLAY` for that process only, and runs
  `hookshot.exe --user <test folder>` with the log redirected into the test folder. Nothing in his game folder
  changes. A new-game test uses an empty test user folder.
- **No Hookshot build or boot while Kareem plays.** A build compiles for about 20 minutes on every core and a boot
  loads the GPU: both made his round 1 test session stutter. The prompt makes the agent check `tasklist` for
  `hookshot.exe` before starting a build and before each boot, and wait (30 s steps) while it is there; Claude
  tells Kareem before a build round starts.
- **One Hookshot test build at a time.** Builds share `%LOCALAPPDATA%\HookshotBuilder` (object cache and lift
  work) with Kareem's own builder.
- **Hookshot work is upstream work.** Small single-issue PRs to `NotRexed/Hookshot` in its conventions
  (Claude-assisted trailers, game-free tests); never a fork Clawshot depends on.
- **Agents don't edit `decisions.md`** and don't merge: each writes `plans/rounds/r<N>-<track>.md`, and Claude
  merges and moves decisions.

## Rules carried over

- If a first attempt fails, print the values instead of trying again (AGENTS.md rule 9).
- Agents never message or read each other through herdr or herdr-core (no `herdr`, `hc` or `herdr-app`
  command at all; hc's own agent skill stays out of omp); cross-track requests go to the Bermuda thread as plain
  posts without @-mentions.
- A report is not evidence: Claude reruns the checks on `main` before calling a track done.
