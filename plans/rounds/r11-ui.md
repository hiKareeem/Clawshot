# Round 11, Track D: UI base (cs11d)

Branch `r11/ui`. Required AGENTS/README, plans00–04, decisions, round9/10 reports and Round11 opening/shared-file ownership read. Reference screenshot inspected in place; no Hookshot code/assets copied. Scratch/screenshots: `E:/OOTRemake/work/r11-ui-cs11d/`. No game, launcher, foreground browser/window, terminal-control command, merge or push.

## Plan and contracts

Implement numbered items in order and commit each. App owns the exhaustive Settings metadata and uses the existing canonical CS1 codec; defaults come from Settings/data/settings.toml. Advanced structured overrides remain JSON, not a second logic-settings implementation. No product default changes.

Generation runs in one spawned process, with genuine stage boundaries around the existing public seed APIs, not invented per-item progress. Cancellation terminates only that worker and removes only its private staging/cache; existing output is never overwritten. The output parent must already exist and be outside the dump/game/source tree. Finished output is published only after successful writing. No game-launch endpoint.

Pack APIs imported, never edited: `check_version`, `BUILD`, `source.local_romfs`. Initial thread post requests any public Hookshot detection API; otherwise read `hookshot_version.txt` and check bin executable presence, without executing it. Generator/CLI/data files are unchanged unless a demonstrated public-API need is recorded here.

## Item 1 checkpoint

Implemented all 19 Settings fields with required label/kind/choices/default/help/group; live dataclass enumeration refuses missing/stale metadata. Defaults and canonical CS1 remain upstream. Validation compiles the actual world and refuses held Token/anywhere modes, malformed types, slice-without-goal and contradictory derived logic. No generator, CLI, data/settings.toml or pack edit.

One spawned worker, stage timings, original exception type/text, cancellation and private staging cleanup. Exclusive output mkdir prevents replacing even a concurrently created empty directory; only the newly reserved output is removed on a publish failure. Synthetic fixtures exercise the actual fill/search/patch writer, written actor assignments, source immutability, cancellation and impossible goals.

Focused `CLAWSHOT_WORKERS=1 uv run pytest tests/test_app.py -q`: **15 passed in 1.86s** after cause-specific corrections. First run printed missing scratch-parent and a FillError/ValueError validation boundary; created the external parent and normalized validation errors without changing text. The next run exposed a wording-only assertion (removed, not re-pinned) and early Windows spawn cancellation blocked on pipe EOF. Faulthandler printed `_recv_bytes` waiting after termination; monitor now also waits on the process sentinel. No failed command was repeated unchanged.

Claude supplied Track C's future detector contract. One import fallback in app/paths.py uses `pack.hookshot.detect` whenever importable, otherwise the isolated stand-in with identical frozen fields (`folder`, `exe`, `version`, `romfs`, `nups`, `supports_mods`, `reason`). **Remove the stand-in once both tracks are on main.** No cherry-pick. Play remains instructions only until Track C's safe logic is importable; no game launch endpoint.

Item2: first-render screenshot paths will be posted immediately before polishing. Items3–5 follow; checkpoints are not ready before all four locked full gates.

Provisional technical choices (cs11d): path inputs are explicit absolute paths (no directory upload or shell picker); no path persistence; spoiler requires a separate confirmed request. Local HTTP is loopback/token protected from the first runnable screen; item3 adds dedicated attack-boundary coverage. Optional pywebview extra follows the specified BSD toolkit; browser fallback stays dependency-free.
