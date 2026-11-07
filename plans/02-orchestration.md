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
2. **Setup.** One worktree per track at `E:/OOTRemake/clawshot-r<N>/<track>` on branch `r<N>/<track>` (`herdr
   worktree create`), one for a Hookshot track at `E:/OOTRemake/hookshot-r<N>/<track>`. Bermuda thread
   `cs-r<N>` (`BERMUDA_THREAD_AGENT=claude ~/go/bin/bermuda thread new cs-r<N> --about "..."`).
3. **Launch.** A fresh omp session per track in its worktree's pane, named `cs<N><letter>` (`cs1a`). Three
   agents at once at most (Kareem's subscription). One background watcher per agent on its pane id, and one on
   the thread (`thread_watch.sh`).
4. **During.** Claude answers thread posts and gaps in a spec by steering the agent (a queued note, no restart).
5. **Review.** Per track: the handoff from its session file, its round file, the diff, the gates on the branch;
   then merge to `main`, gates again on `main`, decisions moved into `decisions.md` with who proposed them.
6. **Kareem's checks.** One message with what to run, where, and what he should see, in order.
7. **Cleanup.** Remove each merged worktree (`herdr worktree remove`), close its workspace.

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
  Hookshot build track may boot its own test build headless and muted for at most 20 s.
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
- Agents never message each other through herdr; cross-track requests go to the Bermuda thread as plain posts
  without @-mentions.
- A report is not evidence: Claude reruns the checks on `main` before calling a track done.
