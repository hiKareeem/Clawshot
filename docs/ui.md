# Local UI

```sh
uv run python -m clawshot.ui                  # browser, when the optional UI extra is absent
uv run --extra ui python -m clawshot.ui       # pywebview app window
uv run python -m clawshot.ui --no-open        # print a local URL; no window, browser or native dialogs
```

Python 3.12+, no JavaScript build step. The optional `ui` extra is pywebview (BSD-3-Clause).
The page, scripts and styles are local; the interface makes no external requests. A pywebview
window needs its platform web engine (WebView2 on Windows; native WebKit on macOS; an appropriate
system GTK/WebKit installation on Linux). The browser route needs no pywebview dependency.
The browser's click-only Browse dialogs use standard-library tkinter; if the OS does not provide
Tk, paste a path instead. No Qt/PySide dependency is added by Clawshot.

Keep the terminal running. Ctrl+C stops the server and cancels generation. Closing a browser tab
alone does not stop the server; closing the pywebview window does. A game already launched is not
terminated by UI shutdown. `--no-open` **disables Browse, Open seed folder and Play**, including
their HTTP endpoints. Normal sessions enable these actions; Play also requires Windows.

## Using it

- **Game:** your own romfs folder or `.nup` is the only required input. Hookshot is optional and
  needed only for Play; emulator players can skip it. Detecting Hookshot fills the dump from its
  romfs or an adjacent NUP. Detection reads files, never starts the executable. The supported game
  check is the pack's `check_version`. Read-only input links/junctions resolve to their real paths;
  output folders still refuse links. Paths are displayed in the host OS's form.
- **Settings:** Defaults restores generator defaults. Recommended selects Chest, Shop, Gift,
  Scrub and BossHeart, with the remaining generator defaults. Every control and choice comes
  from the app schema. Cards explain their coverage and actual gameplay evidence. Unavailable
  choices remain visible with a reason. Ineffective dependent settings are dimmed, retaining
  their values for later reactivation. Changes update the CS1 string; paste and Apply does the
  reverse. Copy copies it, or selects it with keyboard-copy instructions if permission is denied.
- **Generate:** choose a seed, or Random, and a **new** output folder. The suggestion is
  `Documents/Clawshot/seed-<number>` (including redirected Windows/XDG Documents). Only that
  suggested parent may be created automatically, and only when generation starts. Browse for
  output chooses an existing parent and adds the seed name. Custom parents must already exist.
  Existing seeds are never rewritten. Progress reflects real stage boundaries, not estimated
  percentages within the fill. Cancellation removes only this job's private staging/cache.
- **Result:** Play in a detected mod-capable Hookshot, Open seed folder, read the play note, or
  explicitly confirm revealing the spoiler. The play note also contains item locations/hints.
  Play uses `output/user` for this seed's saves and `output/hookshot_log.txt` for its log, never
  your normal Hookshot saves. Quit a running seed before starting another. Changed seed files are
  refused; generate a new seed instead of repairing an output in place.
- **My seeds:** finished seeds remain available after restarting Clawshot. The default output
  folder and folders opened with Find seeds are remembered in your user configuration folder.
  Each entry offers Play, Open folder and its play note, with a short hash. Missing seed information
  or changed files are shown as not playable, with a reason; existing outputs are never repaired.
  A finished seed does not need the original dump to remain at its old path.

The new output layout is `output/seed/romfs` with the note and spoiler beside romfs. Play shares
the pack's checked launch code: only `bin/hookshot.exe`, exactly that seed as the one mod under
`HOS_MODS=output`, no `HOS_FS_OVERLAY` variable, and the update check off. Older outputs are never
moved or rewritten. Emulator players get three loading steps and a main-save backup warning;
Clawshot does not start an emulator. See [seed-pack instructions](seed-pack.md) for manual loading.
Each new output includes `clawshot-seed.json` with its seed number, settings, file digest,
Clawshot version and supported game build. Play checks this record and the seed contents, not
the old dump path. Saves and logs are outside the hashed seed folder.

Before starting a game, both UI and pack Play check the PC-wide process list. Any running
`hookshot.exe` refuses with “Hookshot is already running. Quit it, then press Play.”
This happens before creating the save folder, opening the log or starting another process.

The pack's Make path was verified on Linux (WSL) with both a romfs folder and a `.nup`, producing
the same digest as Windows (maintainer verification, round11). The UI shares that generator path,
so generation is expected to work on Linux and macOS; macOS itself is untested. **Play is
Windows-only**: it starts `bin/hookshot.exe`. Linux Make verification is not native-UI certification.

## Keyboard and layout

Q/E changes tabs outside text editors. Up/Down moves focus; Left/Right changes a chooser, switch
or card; Enter activates the focused action or toggles a card/switch. Text fields retain normal
text/caret input; Esc leaves an editor, and closes a dialog. The hint bar lists only actions that
work for the current control. Disabled cards/rows remain focusable so their reasons can be read.
Mouse hover and focus both update the description panel from schema help.

The menu uses flat tan/brown colors, a label/value layout and system typography, based only on
owner-supplied reference pictures. No game art, menu source, button icons, ornaments or font files
are included. The desktop panel scrolls independently; small windows stack the description panel.
The Generate action fits without scrolling at 1280×860.

## Where to change things

| Responsibility | File |
|---|---|
| Settings metadata, per-choice labels/help/availability/dependencies | `src/clawshot/app/settings.toml` |
| Application input and stage descriptions | `src/clawshot/app/inputs.toml` |
| Defaults/Recommended preset definitions | `src/clawshot/app/presets.toml` |
| Canonical settings validation and metadata checks | `src/clawshot/app/schema.py` |
| Source detection, native paths, protected output boundaries | `src/clawshot/app/paths.py` |
| One-worker generation lifecycle, cancellation and publication | `src/clawshot/app/jobs.py` |
| Read-only verified Play plan and one running seed | `src/clawshot/app/play.py` |
| Durable manifest and known-folder seed catalog | `src/clawshot/app/library.py` |
| Atomic user-config path preferences | `src/clawshot/app/preferences.py` |
| Shared mod/save/environment plan and process start | `src/clawshot/pack/runtime.py` |
| Loopback transport and fixed asset allowlist | `src/clawshot/ui/server.py` |
| Normal/headless startup and click-only native dialogs | `src/clawshot/ui/__main__.py`, `dialogs.py` |
| Tabs, rows, cards, key handling and contextual descriptions | `src/clawshot/ui/static/app.js`, `index.html` |
| All palette/type tokens and layout rules | `src/clawshot/ui/static/style.css` |

### Add a setting

1. Add its real generator behavior/default/CS1 handling in the generator's conventions first.
2. Add a matching table in app `settings.toml`: `label`, `kind`, `group`, `help`; choices need
   both `labels` and `choice_help` entries. Bounds belong on integer fields. Schema generation
   refuses missing/stale fields, labels or choice help; never add a second JS setting list.
3. Use `unavailable` for a genuinely held choice, with a plain-language reason. It is also refused
   by validation. Use `enabled_when` for a setting that currently has no effect: a list of
   `{key, contains|equals|greater_than, reason}` conditions, all required. Inactive values are
   preserved; they are not silently reset or removed from CS1.
4. Group/display options are presentation metadata. Multi-choice cards can supply `status_labels`;
   fast start uses Skipped/Plays. `clears` identifies derived override keys to clear when a control
   changes, rather than hard-coding a field dependency in JavaScript.
   Check totals belong to the generator's actual result, not schema prose or a second UI eligibility
   algorithm: new Gift checks must not require editing a copied count or a held-check list here.
5. Run the synthetic app/HTTP tests, then exercise the actual UI and any changed generator path.
   Keep seeds/game files outside the repository. Follow the project's full gates and in-game
   evidence rules for changes to gameplay.

### Restyle or change fonts

All colors live in the `:root` block of `style.css`. The two font variables are `--serif`
(titles/tabs/section headings/panel titles) and `--sans` (rows/values/body/hints). Change those
stacks there; do not put font families on individual controls. Check row heights, long paths,
disabled controls, keyboard focus, and 1280×860 idle/running/finished captures afterwards.
The approved stacks prefer Palatino and Candara with platform fallbacks (decisions D36/D37).
A future bundled font is a **licence decision for the maintainers**, not an automatic OFL addition:
rule 7's accepted dependency licences do not currently list OFL. No font file is bundled today.

## Verification and limits

`tests/test_app.py`, `test_app_schema.py`, `test_app_play.py` and `test_ui.py` use invented
worlds/resources. The HTTP suite exercises real generation/writing, worker responsiveness,
cancellation, original fill errors, publication races, security and spoiler consent. Play tests
compare read-only plans, digest refusal, one-mod discovery, private saves, and input/output links;
they never launch a game. Dialog adapter smoke uses a synthetic picker, not an OS dialog.
The adapter prefers [pywebview FileDialog enums](https://pywebview.flowrl.com/api/) with the requested
legacy-constant fallback. Headless screenshots use `--no-open` and a fresh browser profile; no
OS dialog/window may be triggered. Keep screenshots outside the repository.

Kareem confirmed a real pywebview window was responsive and Browse opened a normal folder picker
on 2026-11-10. This does not confirm its NUP file picker, browser/Tk picker or the new native Play.

Not implemented in the current checkout:
- gamepad/Steam Deck controller navigation (keyboard/mouse only);
- emulator copying and double-click bootstrap (the next ordered release items);
- a bundled executable/installer or bundled fonts;
- native Play acceptance or Linux/macOS UI runtime certification.

Seed packs still use Make/Play; the UI is run from the source checkout or an installed Python
package containing its static assets. Architecture and the local HTTP contract: [UI plan](../plans/05-ui.md).
