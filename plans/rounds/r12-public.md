# Round 12: public polish (cs12a)

Branch: `r12/public`. Owner: cs12a (openai-codex/gpt-6.1-sol).

## Scope and choices

- Jobs 1–5 from Claude's round prompt: mechanical proofreading; UI-friendly issue forms; the base-only dump-folder hint; public-pack/spoiler wording; first-player troubleshooting.
- No generation algorithm, logic or placement changes. No version or `uv.lock` edits. No game launch, game-folder writes, push, merge or GitHub comments.
- `docs/settings.md` belongs to cs12b; read for consistency, never edited here.
- Provisional choice (cs12a): preserve historical round/decision records as history. Correct current architecture/UI statements contradicted by shipped code, as explicitly requested; do not revise decisions.
- Provisional choice (cs12a): use plain player language in new help/report text. Keep existing developer API identifiers where they document a real contract; mechanical proofreading is not a technical-reference rewrite.
- Required documents read directly or through the read-only audit: the roadmap/game-data/world-format documents received a full delegated proofreading pass, and player strings received a separate full census. All edits and commits belong to cs12a.

## Findings

- `pack.runtime.launch_plan` writes saves to `<output>/user` and stderr to `<output>/hookshot_log.txt`; `app.play.play_plan` passes the seed's parent output folder. UI Open seed folder opens `<output>/seed`, so the log is one folder above that view.
- The existing report form and contribution instructions ask for excerpts; job 2 explicitly requires the complete Hookshot log as a file. Update the report instructions together, explaining folder-path privacy and prohibiting other attachments.
- `plans/01-architecture.md` still describes future mods support; current `pack.runtime` uses `HOS_MODS`. Treat as a stale current-state statement, not a new architecture decision.
- `docs/ui.md` still describes the UI as source/package-only and Play as new/unaccepted; release 0.1.1 is already public. Distinguish recorded game/launch evidence from platform coverage.
- Job 1: corrected glued numbers/current-state claims and the UI's instruction to choose “Check” next to Hookshot (the button is “Detect”). No spelling-style changes: the optional Center/Centre suggestion was rejected.
- Job 2: separate in-game and Clawshot-itself forms, exact UI recipe/hash locations, log/save paths verified against code, path-privacy disclosure, log-only attachment checkbox. Kept the Discord config unchanged. Updated contribution, seed-pack and Discord report instructions together.
- Job 3: only the missing version-marker read of a single-layer dump delegates to the existing `check_romfs` diagnostic, preserving `PackError` for pack callers. Synthetic regression covers absent and empty updates folders and refusal before a cache is made.
- Job 4: public-test source-pack wording and an explicit pack-note spoiler warning. The template/report edits are pack source content, not generated seed content.
- Job 5: `docs/ui.md#troubleshooting` answers game/update checks, Hookshot support, disabled Play, hash differences, Linux/macOS, emulators, saves and reports. Its known-issue list matches Claude's read-only `release-notes-0.1.1-final.md`; macOS is untested with contributor testing underway.
- Full plan audit: 200 line corrections; all differ only in whitespace except the front summary's stale chest-save claim, corrected from the later section 44 evidence. Preserved code spans, canonical report IDs, compact save-state tokens, uppercase emphasis and historical status.

## Commits and seed output

Seed-output changes are isolated: three closing parentheses in location `where` descriptions (LW Trade Cojiro, LW Ocarina Memory Game, GC Rolling Goron as Adult), plus spaces in source-reference metadata rendered into `spoiler.json` (`section 27/39/40`, `round 9/10`, `repeat 30/70`, `fixed 20`). Files: `data/location_names.toml` and `generate/names.py`. This changes output text/digests, not placements, logic or game patches. **Claude must bump the version at merge.** Other job commits do not change generated seed output.

| Commit | Job | Seed output changes? |
|---|---|---|
| `19a6f11` | 1: public text/current-state fixes and Detect guidance | No |
| `ec24c52` | 1: isolated generated description/source-reference text | **Yes** |
| `a5aa7c3` | 2: player issue forms and consistent reporting instructions | No |
| `d0265dc` | 3: base-only dump hint, synthetic test and guide | No |
| `7c1d18e` | 4: public pack wording and spoilers warning | No |
| `df88a73` | 5: first-player troubleshooting and release known issues | No |
| `7830592` | 1: full plan audit, current flag summary, logic-form UI string guidance | No |
| `cfd0afa` | Round implementation record | No |
| `1efa1e0` | Linux Play steer: platform help, schema/API docs, neutral log privacy | No |
| `f9b8940` | Rebased commit record and conflict-resolution note | No |

## Verification

Initial `git status --short --branch`: clean `r12/public`. Initial `tasklist /FI "IMAGENAME eq hookshot.exe"`: no matching process. Use `CLAWSHOT_WORKERS=1` conservatively for tests regardless, and the shared gate lock for full pytest/dump runs.

- Expected-before regression: `CLAWSHOT_WORKERS=1 uv run pytest tests/test_pack_dump_folder.py -k base_only_dump_explains -x -q` failed with the printed technical missing-GameDataList message.
- After the targeted fix: `CLAWSHOT_WORKERS=1 uv run pytest tests/test_pack_dump_folder.py tests/test_cli_romfs.py -q`: **10 passed**, 0.41 s.
- External synthetic smoke (`uv run --with pyyaml python E:/OOTRemake/work/r12-public-cs12a/smoke.py`): all three issue forms parse and have unique required fields; Discord URL unchanged. Real generator CLI and source-preflight commands now print the base-game/update hint, without making output. Pack success formatting exercised with a synthetic publisher boundary, not a real pack build.
- `uv run python -m clawshot.pack --help`: public-test wording observed.
- Claude's steer: main moved to `9f86b3a` with PR #2 (Linux Play). Rebased in a detached scratch worktree to keep the in-flight gates' source stable, then moved `r12/public` onto the rebased commits and removed that scratch worktree. The only conflict was the Linux paragraph in `docs/ui.md`: retained merged behavior plus spacing corrections. Help/templates support Windows/Linux Play, Linux Hookshot Builder `bin/hookshot`, macOS without Play. Save/log paths are unchanged.
- External link checker: **17 documents, zero broken local links/anchors**, including the troubleshooting section.
- Real headless UI (`python -m clawshot.ui --no-open`) loaded at 1280×860. Synthetic frontend completed-seed/capability state displayed the corrected “Choose Detect” guidance with Play disabled; screenshot inspected. No game, OS dialogs or visible windows opened; tab and owned server closed. This is text-rendering proof, not Play acceptance.
- UI smoke first exposed a browser-helper execution-world discrepancy (`page.evaluate` could not see the classic-script function, while direct `tab.evaluate` could). Printed function/script/error values, reported the tool issue, then used direct page-world evaluation successfully.
- Real `generate`, `spoiler_json` and `play_note` smoke on an invented three-location world rendered the corrected parentheses; no game files read.
- Pre-rebase full gates under `gate.lock`, `CLAWSHOT_WORKERS=1`: `uv run ruff format --check` **303 files formatted**; `uv run ruff check` **passed**; `uv run pytest` **954 passed, 126 skipped**, 1250.93 s. The dump gate was intentionally interrupted, **not passed**, to correct temporary-file placement.
- Scratch correction: printed inherited `TEMP`/`TMP` and `tempfile.gettempdir()` showed `C:/Users/hi/AppData/Local/Temp`. Stopped only owned jobs and verified native pytest PID **45052** had exited. Its `.lock` identified the owned `pytest-271` directory; removed only that directory and released the owned gate lock. Further gates set `TEMP`, `TMP`, `TMPDIR` and `PYTEST_DEBUG_TEMPROOT` to `E:/OOTRemake/work/r12-public-cs12a/tmp`. No game folder was written or game started. This initial temporary-location deviation is recorded rather than hidden.
- Claude's PR #3 steer: read local commit `cd7c1f7` (on `9f86b3a`), including source, picker and documentation changes. Its `check_romfs` remains the single base-game hint source, so job 3 automatically inherits “Version 1.0.0” / “Version 1.1.1” without a duplicated detector or message. New help uses the corrected Version 1.1.1 / update v131072 name. Wait for Claude's merge notice, then rebase and run final full gates with the corrected scratch environment.

## Questions / remaining work

None requiring a product decision so far. Implementation and gates in progress.
