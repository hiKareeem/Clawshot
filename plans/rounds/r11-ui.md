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

## Item 4: synthetic HTTP generation and screenshots

Expanded the real-server suite to **15 passed in8.55s**, including an Event-held worker proving the HTTP server remains responsive while generation waits; actual synthetic fill/search/writer through Generate; consent-gated spoiler with a reachable Sword goal; existing-output byte/mtime preservation; cancellation cleanup; exact original FillError propagation; and a destination created by another owner while the worker runs (never overwritten or cleaned). No game fixtures or mock generation.

Final font/browser proofs already recorded above cover all five screen/state captures, zero script/off-origin failures, exact complete progress width, native path presentation, cards/dependencies, clipboard and settings replay. The last review wording change is metadata-only: each fast-start card names "Skip…" and its two states are Skipped/Plays; no new default or scene patch. Native dialogs/Explorer/game still deliberately unstarted.

## Item 5: contributor docs and API plan

Added `docs/ui.md` (launch modes, native/headless capabilities, settings/seed/loading workflow, keyboard/layout, source ownership, schema extension, font/color tokens and explicit not-done list) and `plans/05-ui.md` (application/HTTP contracts, real generator sequence, process/cancellation/publication ownership, native-dialog boundary, frontend extension). No README edit: Track A owns it.

Additional native headless key-event smoke passed: Q/E tabs, Up/Down focus, Left/Right card and select changes, Enter toggles, E left to the focused editor, Esc back; zero JS exceptions. Evidence: `E:/OOTRemake/work/r11-ui-cs11d/keyboard-final-proof.json`. Stopped both old --no-open servers before integration/gates; no native GUI, Explorer or game started.

Main moved to D37 as Claude reported; rebase and the four full gates follow. Public `pack.hookshot` still has no main history at this checkpoint, so the specifically agreed isolated detector stand-in remains until Track C integration. This is not yet the final gate/handoff claim.

## Base handoff: items 1–5 complete

Full commands ran serially with `CLAWSHOT_WORKERS=1`; whole pytest, dump tests and the one native app smoke each acquired/released `E:/OOTRemake/work/rounds/r11/gate.lock` in a finally path, with no other gate overlapped:

- `uv run ruff format --check`: 278 files already formatted.
- `uv run ruff check`: all checks passed.
- `uv run pytest`: **852 passed, 110 skipped in1197.85s**.
- `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump`: **93 passed, 16 skipped, 853 deselected in966.16s**. This run supplied romfs, not the optional NUP fixture.
- Actual default `Jobs` generation, seed11/CS1, using the real dump and existing make_seed/write_seed: **succeeded**,165 shuffled checks,26 spheres,83 resources; all stages done, private staging removed, ZsDic SHA256/mtime unchanged. Output is a new untouched folder: `E:/OOTRemake/work/r11-ui-cs11d/real-app-seed-11-next-20261110-122355`. No launcher/game run. Native proof: `native-app-proof.json`; full logs/results: `E:/OOTRemake/work/r11-ui-cs11d/gates-20261110-104649/`.

After these completed, followed Claude's integration instruction: rebased onto main containing loader e4fe456, imported `pack.hookshot.detect` directly, deleted `app/_hookshot.py` and its ImportError fallback. Capability is the HOS_MODS marker alone, not a version inference. The synthetic non-execution fixture now contains that marker; removed its incidental normalized-version assertion instead of re-pinning it. Real authenticated HTTP detection of the installed game returned200, version `v2.0.13`, supports_mods=true, empty reason and native romfs/NUP paths, without execution.

Authorized post-rebase checks only: full format **281 formatted**, full lint passed; `CLAWSHOT_WORKERS=1 uv run pytest tests/test_app.py tests/test_app_schema.py tests/test_ui.py -q`: **36 passed in12.54s**. Full gates were not rerun after integration; Claude runs them in review as directed. Throwaway gate/native-smoke scripts removed after proof; logs, screenshots and the new native seed remain outside the repo.

Updated platform facts from Claude: Make verified under Linux/WSL from folder and NUP with the Windows digest; UI generation expected on Linux/macOS, macOS untested; Play is Windows-only. Corrected stale Door of Time help to D35's first-check evidence and still-untested early child return.

Provisional metadata choice (cs11d): removed copied check totals and the stale bottle/digging hold list instead of duplicating generator eligibility policy in the UI. Actual generation reports its check/resource totals. Gift additions therefore need no schema count edit. Per-choice coverage and specific gameplay evidence remain; no defaults or generator behavior changed.

Final fast-start wording proof: `E:/OOTRemake/work/r11-ui-cs11d/shots/settings-menu-faststart-final.png`,1280×860, fresh --no-open process: Skip the opening intro / Skipped; other Skip… cards / Plays. Earlier approved -font Game/Settings/finished and menu idle/running captures remain valid. Browse/Open are enabled by both normal startup branches; their capability/HTTP path is tested using an injected chooser without a dialog. Native window/dialog visuals and in-game acceptance are not claimed.

Rebased base commits, in order: `3fe5b26` app; `a104b44` menu UI; `ad8bb39` HTTP safety; `d183f31` synthetic HTTP generation; `7d60ff6` docs; this integration/handoff commit's exact head is posted on cs-r11. No merge/push, played output/save/dump changes or game start. Base intentionally has loading instructions, not a real Play/installer/gamepad. Kareem's new release direction supersedes those limits in the next work: after this base handoff, read `ui-next.md` and implement its ordered items on this branch.

## UI release continuation: ordered plan

Read `work/rounds/r11/ui-next.md` only after posting base headbc0ba1f. Eight item commits in order: real Play; double-click starts; zero-settings first run; sharing/hash; readable result; remake display names; game-free release zip; first-player docs. Handoff after3 and after8. Base review proceeds separately; stay on r11/ui and rebase only when Claude says main moved.

Item1 design (cs11d): expose the pack's existing checked launch plan and process start as public functions, with pack Play continuing to call them and wait. This is the necessary clean public-API change to owned-by-C runtime.py, not a copied launcher. New app outputs use the pack layout `output/seed/romfs`, with `output/user` and `output/hookshot_log.txt`; old outputs are never moved or rewritten. Publication records the existing tree_digest so Play refuses changed resources. App owns one Player, HTTP derives the output from its completed job (never a caller path), normal Windows sessions alone may launch; --no-open refuses before any launch. Pure plans remain inspectable without OS actions. Hookshot capability comes only from the shared detector. No test/script/screenshot may launch Hookshot.

The existing test-launcher template comments were read for the one-mod, unset-overlay, bin-executable and isolated-save facts; no test launcher or save copy is needed here. Later root start scripts start only the UI, not the game. No dependency added by item1. Native Play still needs Kareem's manual acceptance; plan/guard and synthetic generation are the allowed agent proofs.

Owner evidence, 2026-11-10 (Claude relaying Kareem): the base opened in a real pywebview window on Kareem's PC — **"UI looks good, responsive"**. This is the first real-window evidence. Which dialogs he used is unknown; do not infer either chooser route or Play acceptance.

New first-run requirement: lead Game with the dump as the only required input; Hookshot is optional, needed only for Play, with the exact player explanation supplied. New ordered item immediately after Play: Copy to my emulator, remembered game-mod folder, exclusive `Clawshot-seed-<number>/romfs` real-folder copy, no replacement; show the emulator main-save backup warning. Offer `%APPDATA%/eden/load/0400486024DEC000` only when it exists (Kareem's Eden/Lichii check), otherwise only the folder picker. No emulator is launched.

Owner evidence update (Claude relaying Kareem): **Browse opens a normal folder picker in the pywebview window**, alongside the earlier **"UI looks good, responsive"**. This confirms that base build's pywebview folder-picker route on his PC. The NUP file picker, browser/Tk route and native Play remain unconfirmed; do not extend the claim.

Item1 focused check: **77 passed in15.73s**, full scoped app/schema/UI/Play/detector/pack cases; format283/lint passed. First plan test run exposed conftest's `"dump" in item.keywords` skip on a synthetic parameter named dump; renamed it source-version, so that negative version case actually runs. The integrated run then exposed a duplicate error-precedence assertion with both no seed and no bin executable: it pinned which diagnostic wins. Removed that wording-only test, not re-pinned; the dedicated pure detector test still proves a root launcher is never accepted. All current plan cases run, including symlink and Windows junction inputs, strict output refusal, changed data, separate saves/log and no writes. No game or native dialog started by the agent.

### Release item 1 complete: real Play, not invoked by tests

Shared `pack.runtime.launch_plan`/`start_game`; pack waits, UI Player keeps one process handle. New jobs publish `output/seed` and remember its tree digest; Play checks the unchanged seed and game files, real-folder one-mod layout, binary support, isolated `output/user`, log, removed overlay and disabled update check. Headless and non-Windows launch requests refuse with player instructions. Open seed folder and three emulator loading/save-backup lines work without Hookshot. Existing outputs remain untouched. No dependency or generator default changed.

Final format283/lint passed; the seven focused app/schema/Play/UI/loader/detector/pack files: **77 passed in16.81s**. Modern-enum and legacy-name chooser dispatch both exercised with a synthetic window, zero native dialogs. Enum facts: https://pywebview.flowrl.com/api/ . New tests include real synthetic fill/writer, source-version change, output change, extra mod, user/log link refusal, input symlink and junction resolution, output-link refusal and looping input.

Actual headless surface rerun succeeded: real synthetic generation into the new layout, note/spoiler controls, disabled Play plus HTTP400 under --no-open, emulator fallback, cancellation, original FillError, no JS exception and no off-origin request. Generate button bottom668.58px and result bottom773.58px at1280×860. Captures: `shots/generate-running-play-next.png`, `shots/generate-finished-play-next.png`, `shots/generate-emulator-play-next.png`; proof `synthetic-play-proof.json`, all under the existing external scratch. Test-only fixture binary is non-executable; no real game can be launched by this screenshot harness.

Docs/API plan now describe the shared Play boundary and new layout. Six-line owner checklist will accompany the first-run handoff once the double-click starts exist. Next is the newly inserted emulator-copy item, then the original items2/3.

### Priority Play review 1: PC-wide guard

Added the process-list guard to the shared starter, so pack and UI both refuse any existing hookshot.exe, not only their own child. Exact player refusal: **Hookshot is already running. Quit it, then press Play.** System tasklist runs hidden, no dependency; exact case-insensitive name matching ignores HookshotBuilder and unrelated suffix names. Query failure refuses safely. Guard precedes user-folder creation, log opening and native process creation. Pure plans remain inspectable.

Fake-lister tests plus the existing loader plans:16 passed in0.30s; real native lister smoke observed no running Hookshot and did not start a game. The first lint pass printed SIM112 for environment-name casing; changed SystemRoot to SYSTEMROOT, then format/lint passed. CSV's informational no-match row is not a process. Next ordered reviews are durable manifests/My seeds and removing the original-dump dependency; emulator copy then startup remains queued.

### Priority reviews 2/3: durable library and portability decision

Implementing a deterministic `clawshot-seed.json` beside output/seed: the requested number/settings/digest/Clawshot-version/game-build, plus format and the existing small result counters. No original absolute dump path. Its digest covers seed contents, not the manifest, saves or log. My seeds scans the default folder and explicitly opened folders, remembers those roots in user config, shows invalid/missing/changed records as unplayable, and authorizes per-seed actions only against known entries. Manifest keys cannot override output/playable/catalog authority. Loaded seeds show no invented generation timings.

Choice for review3 (cs11d, allowed by Claude): **rely on the verified seed digest and its supported game-build record**, plus the shared Hookshot capability/one-mod checks; do not require the original dump or fingerprint a new Hookshot dump for Play. Source version is still checked for Generate. Moving/deleting the original files must not disable a finished seed. This is necessary to make the durable library portable, so the common reader and Play cutover land as one coherent reviews2/3 change with moved/deleted-source regressions. No compatibility shim or silent manifest upgrade; no manifest is shown as not playable, as requested.

User-folder Preferences is shared infrastructure for the library and subsequent remembered emulator/game paths; normal CLI supplies the OS user config path, test/embedded servers explicitly keep it in memory or an injected external fixture path. No dependency added. Later native lister smoke also detected a real hookshot.exe correctly (the agent did not start it); both empty and occupied PC states observed.

Reviews2/3 proof: format286/lint passed; eight focused app/schema/Play/library/HTTP/loader/detector/pack files **94 passed in23.79s**. A first focused command named a nonexistent detector test; its printed inventory error was corrected to `test_pack_hookshot.py`, not rerun unchanged. HTTP regressions recreate the application from disk preferences, delete the original synthetic source, load the same seed, enforce spoiler consent/catalog boundaries, and reject malformed authority fields. Read-only plans work after both source move and deletion.

Actual hidden Chromium surface: generated synthetic seed27 with no Hookshot, catalog discovered it, View seed loaded it, note opened, reload retained the loaded view; generation inputs/progress were hidden for the loaded seed and no JS errors occurred. Screenshots `shots/library-generated.png` and `shots/library-loaded.png` under the external scratch were visually inspected. Headless native Play/Open remained disabled; no OS dialog or game started. The catalog deliberately shows unrecognized folders under an opened root as not playable, satisfying the no-manifest requirement without guessing an old output's validity.

### My seeds review corrections (before emulator copy)

Claude accepted2c46c8e's manifest/portable-Play boundary; reported66 tests passing in the copy now used for Kareem's try-out. Three requested corrections supersede the earlier catalog behavior: ignore all folders without a manifest or an older seed/romfs/romfs layout; show older outputs with the supplied calm regeneration line; draw from metadata only and sort newest manifest mtime first. View and Play retain actual content verification. No changed-resource claim is made at list time, and unrelated directories no longer become broken rows. No output timestamp was added; filesystem times affect only the list order.

Correction proof: scoped format/lint passed; app/library/Play/HTTP **52 passed in24.11s**. Regression observes zero content-digest reads during listing of a changed seed, then View refuses it and Play's pure plan refuses it too. Both older layouts and deliberately reverse-alphabetical folder names are covered; only manifests and older layouts survive filtering, newest manifest first.

Hidden Chromium proof visually inspected `shots/catalog-review-filtered-newest.png`: z-newest precedes a-older, hookshot/input/holiday-pictures absent, legacy has one calm line and no disabled action clutter. Refresh still displayed a deliberately changed synthetic seed; View refused it, then the unchanged older row loaded successfully with no generation timings or JS errors. The instrumented smoke emitted exactly the two content verifications for those two View clicks, not for list/refresh. Browser selector tooling briefly held a detached row after Refresh; printed the live row values, reported the tooling issue, and selected a freshly observed element. No app workaround or unchanged rerun.

### Emulator copy

Added the explicit backup reminder/confirmation and remembered game-mod folder. Exclusive Clawshot-seed-N/romfs is a real file copy with a post-copy digest check; existing names are never replaced. Configured dump/Hookshot, environment dump, current output and source checkout are protected destinations. Eden's known game folder is offered only when present and clicked; other emulators use the folder picker. No emulator start or main-save access. Native-capable sessions alone may copy; headless refuses.

**Startup platform question for Claude/Kareem:** macOS Finder normally opens `.sh` as text. The requested `clawshot.sh` can be opened with Terminal, but a literal Finder double-click needs a `.command` entry or association. Shall the release include a `.command` wrapper? Windows/Linux implementation proceeds; macOS remains explicitly untested as requested.

Emulator proof: focused export/library/app/Play/HTTP/loader/detector/pack **94 passed in28.06s**; integrated display-name/bootstrap focused checks also passed (50 cases), format/lint passed. Hidden Chromium used one injected synthetic chooser, copied successfully, refused a second copy without replacing anything, and remembered the selected folder after reload. `shots/emulator-copy-complete.png` visually inspected. Eden's real existing path was offered but never selected or written; only external synthetic fixtures were copied. No JS errors, emulator, game or OS dialog.

The added action exposed a24px desktop overflow; constrained the description panel with flex scrolling. Reload proof: root height860 for860 viewport, panel bottom766.5 and hints bottom814.5. Copy success/collision, changed seed, strict output links/protected folders, remembered choice across a new server, independent real files and unchanged normal-save marker are covered.
