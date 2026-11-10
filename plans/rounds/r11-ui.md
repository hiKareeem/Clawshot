# Round 11, Track D: UI base (cs11d)

Branch `r11/ui`. Required AGENTS/README, plans00–04, decisions, round9/10 reports and Round11 opening/shared-file ownership read. Reference screenshot inspected in place; no Hookshot code/assets copied. Scratch/screenshots: `E:/OOTRemake/work/r11-ui-cs11d/`. No game, launcher, foreground browser/window, terminal-control command, merge or push.

## Plan and contracts

Implement numbered items in order and commit each. App owns the exhaustive Settings metadata and uses the existing canonical CS1 codec; defaults come from Settings/data/settings.toml. Advanced structured overrides remain JSON, not a second logic-settings implementation. No product default changes.

Generation runs in one spawned process, with genuine stage boundaries around the existing public seed APIs, not invented per-item progress. Cancellation terminates only that worker and removes only its private staging/cache; existing output is never overwritten. Output stays outside the dump/game/source tree. The suggested Documents/Clawshot parent may be created at generation time; any custom parent must exist. Finished output is published only after successful writing. No game-launch endpoint.

Pack APIs imported, never edited: `check_version`, `BUILD`, `source.local_romfs`. Initial thread post requests any public Hookshot detection API; otherwise read `hookshot_version.txt` and check bin executable presence, without executing it. Generator/CLI/data files are unchanged unless a demonstrated public-API need is recorded here.

## Item 1 checkpoint

Implemented all 19 Settings fields with required label/kind/choices/default/help/group; live dataclass enumeration refuses missing/stale metadata. Defaults and canonical CS1 remain upstream. Validation compiles the actual world and refuses held Token/anywhere modes, malformed types, slice-without-goal and contradictory derived logic. No generator, CLI, data/settings.toml or pack edit.

One spawned worker, stage timings, original exception type/text, cancellation and private staging cleanup. Exclusive output mkdir prevents replacing even a concurrently created empty directory; only the newly reserved output is removed on a publish failure. Synthetic fixtures exercise the actual fill/search/patch writer, written actor assignments, source immutability, cancellation and impossible goals.

Focused `CLAWSHOT_WORKERS=1 uv run pytest tests/test_app.py -q`: **15 passed in 1.86s** after cause-specific corrections. First run printed missing scratch-parent and a FillError/ValueError validation boundary; created the external parent and normalized validation errors without changing text. The next run exposed a wording-only assertion (removed, not re-pinned) and early Windows spawn cancellation blocked on pipe EOF. Faulthandler printed `_recv_bytes` waiting after termination; monitor now also waits on the process sentinel. No failed command was repeated unchanged.

Claude supplied Track C's future detector contract. One import fallback in app/paths.py uses `pack.hookshot.detect` whenever importable, otherwise the isolated stand-in with identical frozen fields (`folder`, `exe`, `version`, `romfs`, `nups`, `supports_mods`, `reason`). **Remove the stand-in once both tracks are on main.** No cherry-pick. Play remains instructions only until Track C's safe logic is importable; no game launch endpoint.

Item2: first-render screenshot paths will be posted immediately before polishing. Items3–5 follow; checkpoints are not ready before all four locked full gates.

Provisional technical choices (cs11d): no path persistence, uploads or external assets; spoiler requires a separate confirmed request. Local HTTP is loopback/token protected from the first runnable screen; item3 adds dedicated attack-boundary coverage. Optional pywebview extra follows the specified BSD toolkit; browser fallback stays dependency-free.

## Item 2: runnable front end and reviewed menu look

`python -m clawshot.ui --no-open` starts a random loopback URL without importing a GUI or opening a window. Normal mode embeds in optional pywebview, otherwise uses the default browser. Added only optional `ui = ["pywebview>=6.1"]` and its lock resolution; posted on cs-r11. Licence inspected: [pywebview BSD-3-Clause](https://raw.githubusercontent.com/r0x0r/pywebview/master/LICENSE). No mandatory UI dependency/build step.

First three builder-style renders were posted immediately (09:37/09:38) before polishing: `shots/{game,settings,generate}-first.png`. Kareem then approved the base and requested the in-game menu look through Claude. Read the complete external ui-look.md and all five reference pictures; sampled the three Hookshot pictures with system Python3.11/Pillow into external `palette-samples.json`. CSS variables use sampled band #b18d5d, panel #21180f, label #3a2e1e, value #1e1913, selected #5a4528, description #231a13 and amber #eaa734. No game/menu code, PR, art, traced ornament or font files were opened/copied.

Current UI: tan Game/Settings/Generate tabs, brown label/value rows, four-column shuffle cards, amber focus/white outline, contextual schema help and unavailable-option reasons, actual progress rows/timings, result/play guidance in the description panel, and context-sensitive working-key hints. Q/E tabs, Up/Down focus navigation, Left/Right changes, Enter activates, Esc closes dialogs/leaves an editor; text fields keep ordinary typing/caret keys. Every setting/choice label comes from app metadata, not JS field lists.

Claude/Kareem's ordered review changes are built:
- Every path has Browse plus pasteable text. pywebview uses its native file/folder dialog; browser fallback queues a stdlib tkinter chooser onto the main thread (macOS-safe ownership). Dialogs open only on an explicit click, never during startup/tests/--no-open. Detected Hookshot fills/verifies its romfs or adjacent NUP automatically. Documents uses the Windows redirected known folder (here OneDrive/Documents), or platform/XDG Documents. The output suggestion tracks the seed until customized.
- Plain titles and one-sentence descriptions, no slogans/eyebrows.
- Schema-sourced player labels; tokens and dungeon-items-anywhere are visibly unavailable with reasons and refused by validation. Defaults and **Recommended** presets; the five Recommended shuffle kinds were explicitly requested by Kareem through Claude (not a new default). Copy works, with a selection/keyboard fallback if clipboard permission is denied.
- Local Random seed action; Generate remains visible (observed bottom666px at1280x860).

Five reviewed menu captures were posted at10:01, all under `E:/OOTRemake/work/r11-ui-cs11d/shots/`:
`game-menu-next.png`, `settings-menu-next.png`, `generate-idle-menu-next.png`, `generate-running-menu-next.png`, `generate-finished-menu-next.png`.

Actual headless Chrome/CDP smoke: real dump fingerprint and Hookshot2.0.13 detection without execution; control→CS1→control replay; Q/E tab navigation and unavailable-card help; both presets; actual Copy clipboard equality; random seed/default-path update; real synthetic fill/search/writer with written result; cancellation and original FillError; play note and play instructions; unconfirmed spoiler refusal/confirmed reveal. Zero JS exceptions or off-origin requests. External `browser-menu-proof.json`, `synthetic-menu-proof.json`. Synthetic screenshot harness alone pauses3s at the real fill stage for an observable running frame; production has no delay or mocked generation.

Diagnostics: first screenshot harness had an unterminated expression, corrected before it executed. Its first clipboard attempt used an offscreen untrusted `.click()` and selected the fallback instead; focused the fallback input and used a real headless pointer click/clipboard permission for the cause-aimed pass. No claim of native dialog/window, Linux/macOS or in-game testing: those foreground surfaces were deliberately not opened. Both --no-open and tests reject native Browse/Open calls; tkinter is not imported in the headless smoke.

No source/API edits outside owned app/ui modules, optional dependency metadata and owned tests/round file. In particular no generate/, __main__.py, pack/, data/settings.toml or README edit. HTTP/security cases, documentation and all four locked full gates follow; this checkpoint is not ready for merge.

### Final UI review and font checkpoint

Kareem accepted the menu look through Claude ("I think the UI looks great"). Applied all seven review corrections:
1. Every choice now requires its own help; shuffle-card descriptions state scope, approximate counts and observed/pending gameplay. Supported-dump read-only preparation counted165 chests,64 shop shelves and57 gift/song checks; scrub help names the four saved families, not the six pre-restriction world rows. Player-facing reasons replace implementation jargon.
2. Fast start uses cards, not browser checkboxes; numeric spinners are removed and integer settings have menu-style minus/plus actions. After the last wording steer the cards say "Skip…" and show **Skipped / Plays**, entirely from schema metadata.
3. Key hints use Move, Change, Toggle, Open, Generate and the focused action's own verb; unavailable controls omit keys that cannot act.
4. Schema dependencies dim shop/scrub settings that currently have no effect, with a reason. Values survive disabling/re-enabling and CS1 replay; the independent cheap-shield patch remains enabled without Shop.
5. Browse/detected/pasted/result paths are normalized through the app API to the host OS form.
6. Removed progress-width interpolation so terminal success is exactly100%; correct singular/plural results.
7. Browse/Open are enabled explicitly in **both normal browser and pywebview branches**. --no-open disables them intentionally. Real HTTP tests inject a synthetic chooser and exercise the enabled path, rejecting untrusted/invalid requests before the chooser, checking kind/path/seed normalization and proving selection creates no output. They do not open a dialog/Explorer; real native dialog rendering remains an intentional verification limit.

Claude's exact approved serif/sans stacks are the two CSS variables `--serif` / `--sans`; base16px, slightly larger rows/cards. No font file/dependency. Headless captures posted with `-font` names: `game-menu-font.png`, `settings-menu-font.png`, `generate-finished-menu-font.png` (also idle/running siblings). Final Generate bottom668.58px; completed bar682.80/682.80px; result **1 mod file**. Fonts/row geometry and descriptions reviewed from the actual images. Copy, all schema dependencies, native path text, disabled choices, presets, synthetic generation/cancel/fill error and no off-origin/JS errors passed again (`browser-font-proof.json`, `synthetic-font-proof.json`).

The first hint assertion printed the focused card and stale hints; the next diagnostic established `document.hasFocus() == false` in the background headless target. Bringing only that **headless** target forward and focusing it produced the real focus events and Move/Change/Toggle hints. No speculative UI workaround; no foreground window. Lint's printed SIM102 was corrected by combining the Gift-normalization guard.

Effective spoiler CS1 strings expand Gift into the engine's four gift kinds. The app now collapses that complete group back to the player-facing Gift choice before validation/replay; the generator still expands/rebuilds its own policy. This fixes a real imported-spoiler-string boundary without changing the generator codec or any public source file.

Focused checks: app/schema **21 passed** (missing setting/choice metadata, effective-Gift replay, dependency activation and retained values included); real HTTP safety **11 passed**. Earlier incidental error-wording checks were removed rather than re-pinned. All source/generator/pack APIs remain unchanged. Final full gates and docs still required.

## Item 3: local transport and path safety

Loopback-only random port; per-run random token in every static URL and an additional token header on every API call; exact Host/Origin and cross-site checks; no CORS access; no-store/no-referrer/nosniff/CSP headers. Only the three named local assets are served. JSON bodies are bounded and typed. Source/output paths are absolute, local, link-free, protected from overlap and existing output reuse; result reads accept only the note/spoiler names and spoiler needs explicit confirmation. No game-start endpoint.

Real HTTP boundary suite: **11 passed in5.80s**. Covers missing/wrong/non-ASCII tokens, hostile Host/Origin/fetch-site, static traversal and arbitrary-file refusal, malformed/oversized/non-finite JSON, headless native-action refusal, enabled chooser validation without a dialog, normalized paths and pre-staging output protection. An added malformed-token case reproduced a real `compare_digest` TypeError/closed connection; ASCII preflight now rejects it with403. The failing case remains as a regression. Removed an extra nested-array fixture because it duplicated the already-covered non-object refusal.

The first filtered-test command's nested cmd quoting passed `or` as a filename (no tests ran); ran the explicit single file instead to print the actual header failure. No unchanged failing retry, no skip or weakened oracle. Safety checkpoint is committed separately; synthetic HTTP generation tests follow as item4.
