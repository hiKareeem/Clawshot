# Local UI

Download the **Clawshot-\<version\>.zip** attached to a UI test release (not the generic source zip).
Unzip the whole Clawshot folder, then double-click **Clawshot.bat** on Windows.
Linux uses executable **clawshot.sh**. **macOS is untested:** the first time, right-click
**Clawshot.command** and choose **Open** because the download is unsigned; later, double-click it.
The wrapper runs clawshot.sh from the extracted app folder.
Keep its terminal open while playing with the menu. Nothing requires administrator access.

The starter first uses uv already on your PATH or in the app's `.tools` folder. If missing, it
announces a one-time download of pinned uv 0.13.7 from its official GitHub release, checks the
embedded SHA-256 before extracting/executing, and keeps it inside `.tools`. It changes no PATH,
profile or system install. No internet or a blocked download gives the manual release link.
Dependencies come from `uv.lock` with `--frozen --no-dev`; Windows also selects the optional UI extra.
The first start may also fetch Python and these dependencies; it never fetches a game.

Optional terminal commands for a source checkout:

```sh
uv run python -m clawshot.ui                  # browser, when the optional UI extra is absent
uv run --extra ui python -m clawshot.ui       # pywebview app window
uv run python -m clawshot.ui --no-open        # print a local URL; no window, browser or native dialogs
```

Python 3.12+, no JavaScript build step. The optional `ui` extra is pywebview (BSD-3-Clause).
The page, scripts and styles are local; the interface makes no external requests. A pywebview
window needs its platform web engine (WebView2 on Windows; native WebKit on macOS; an appropriate
system GTK/WebKit installation on Linux). The browser route needs no pywebview dependency.
The browser's click-only Browse dialogs use standard-library tkinter, opened over the browser
window, on Windows and Linux, and the system chooser through `osascript` on macOS; if neither is
available, paste a path instead. No Qt/PySide dependency is added by Clawshot.

Keep the terminal running. Ctrl+C stops the server and cancels generation. Closing a browser tab
alone does not stop the server; closing the pywebview window does. A game already launched is not
terminated by UI shutdown. `--no-open` **disables Browse, Open seed folder, emulator copying and Play**,
including their HTTP endpoints. Normal sessions enable them; Play also requires Windows or Linux.

## Using it

On a fresh page, Recommended and a random seed are already selected, with a new output under
Documents. Choose and check your dump, then go straight to Generate; no settings changes or
Hookshot/Longshot installation are required. Checked input paths are remembered in your user configuration.
Saved folders live in `%APPDATA%/Clawshot/paths.json` on Windows, `~/Library/Application Support/Clawshot/paths.json`
on macOS, and `$XDG_CONFIG_HOME/clawshot/paths.json` (or `~/.config/clawshot/paths.json`) on Linux.
The game folder is saved as `game`; a folder an older Clawshot saved as `hookshot` is read as the game folder.

- **Game:** your own romfs folder or `.nup` is the only required input. A Hookshot or Longshot folder
  is optional and needed only for Play; emulator players can skip it. Choose one of:
  - a Hookshot or Longshot game folder, the one holding `bin` (`bin/hookshot.exe` or `bin/longshot.exe` on
    Windows, `bin/hookshot` or `bin/longshot` on Linux);
  - a Longshot Launcher folder: the portable program folder or its `LongshotLauncher-data`, the installed
    `%LOCALAPPDATA%\LongshotLauncher` (or its program folder `%LOCALAPPDATA%\Programs\LongshotLauncher`),
    `~/.local/share/longshot/launcher` on Linux, a portable AppImage's `<AppImage>.home`, or a folder of
    builds such as `~/Games/Longshot`. Play prefers an available build marked `default: true` in
    the launcher's `builds.json` (its README, *What it does* / *Design decisions*).
    Without one it uses numeric version order: a release ranks above the same version's RCs;
    unversioned nightlies rank below recognized releases. Picking a build folder pins that build.

  **Detect** shows which game, its version (from `hookshot_version.txt` or `longshot_version.txt`) and
  whether its program can load mods. It can fill an empty dump field from the game folder's romfs or an
  adjacent NUP; it does not replace a dump you already chose. Detection only reads files. The supported game
  check is the pack's `check_version`. Read-only input links/junctions resolve to their real paths;
  output folders still refuse links. Paths are displayed in the host OS's form.
  Longshot facts come from its README (*Where the files go*, *Running the game from the command line*) and the
  Longshot Launcher README (*Installing*, *Design decisions*).
- **Settings:** Defaults restores generator defaults. Recommended selects Chest, Shop, Gift,
  Scrub and BossHeart, with the remaining generator defaults. Every control and choice comes
  from the app schema. Cards explain their coverage and actual gameplay evidence. Unavailable
  choices remain visible with a reason. Ineffective dependent settings are dimmed, retaining
  their values for later reactivation. Changes update the versioned share string; paste and Apply does the
  reverse. Copy copies it, or selects it with keyboard-copy instructions if permission is denied.
  **Copy for Discord** (here and under Seed ready) copies the same string inside single backticks.
  Discord reads text between two `_` as italics and drops them, which breaks a pasted string; inside
  backticks it stays exact. If you copy the plain string, wrap it in single backticks yourself.
- **Generate:** choose a seed, or Random, and a **new** output folder. The suggestion is
  `Documents/Clawshot/seed-<number>` (including redirected Windows/XDG Documents). Only that
  suggested parent may be created automatically, and only when generation starts. Browse for
  output chooses an existing parent and adds the seed name. Custom parents must already exist.
  Existing seeds are never rewritten. Progress reflects real stage boundaries, not estimated
  percentages within the fill. Cancellation removes only this job's private staging/cache.
- **Result:** Play in a detected mod-capable Hookshot or Longshot, Open seed folder, explicitly open
  **Play note (spoilers)**, or confirm revealing the raw spoiler JSON. Neither opens automatically.
  Play uses `output/user` for this seed's saves and `output/hookshot_log.txt` or `output/longshot_log.txt`
  (named after the game) for its log, never your normal saves. Quit a running seed before starting another.
  Changed seed files are refused; generate a new seed instead of repairing an output in place.
  Play loads through `HOS_MODS`, not an overlay. In this seed's `hookshot_log.txt`, check
  `mods: 1 mods from <seed folder>` and `mods: <file> <- <path in this seed>`, plus the
  matching in-game reward. Longshot's log names each mod and the files read from it (Longshot README,
  *Mods*); if `output/longshot_log.txt` stays empty, Longshot's own `longshot_log.txt` in the game folder
  holds the run (Longshot README, *If something goes wrong*). Mounting a mod alone does not prove gameplay.
- **My seeds:** finished seeds remain available after restarting Clawshot. The default output
  folder and folders opened with Find seeds are remembered in your user configuration folder.
  Each entry offers Play, Open folder and **Play note (spoilers)**, with a short hash. Only folders with
  seed information or an older seed/romfs or romfs layout appear; unrelated folders are ignored.
  Older seeds get a calm regeneration message. Newest information files appear first.
  Listing reads only the small information file; View and Play check the seed's actual digest.
  Changed files are refused then, without repairing them. Finished seeds do not need the old dump path.

The new output layout is `output/seed/romfs` with the note and spoiler beside romfs. Play shares
the pack's checked launch code: only the game in `bin` (`bin/hookshot.exe` or `bin/longshot.exe` on
Windows, `bin/hookshot` or `bin/longshot` on Linux; never the folder-root launcher), started in its own
game folder, exactly that seed as the one mod under `HOS_MODS=output`, `--user output/user`, no
`HOS_FS_OVERLAY` variable, and that game's update check off (`HOOKSHOT_NO_UPDATE_CHECK=1` or
`LONGSHOT_NO_UPDATE_CHECK=1`, the switch each game folder's own launcher passes). Older outputs are never
moved or rewritten. Emulator players get three loading steps and a main-save backup warning;
Clawshot does not start an emulator. See [seed-pack instructions](seed-pack.md) for manual loading.
Each new output includes `clawshot-seed.json` with its seed number, settings, file digest,
Clawshot version and supported game build. Play checks this record and the seed contents, not
the old dump path. Saves and logs are outside the hashed seed folder.

When Play creates a seed's `user` folder, it copies only `option.sav` and `account.sav` once
from the chosen build's `user/save/<id>/` (the newest ID folder by modification time).
Camera speed, Invert Jump and ocarina controls therefore carry over if those files exist.
Existing seed users/options are kept unchanged; `slot_NN` progress is never copied.
Missing source files are skipped and named in Play's result. The game's own
`hookshot_options.ini` / `longshot_options.ini` stays in the game folder and needs no copy.

**Copy to my emulator** asks for your emulator's mod folder for this game once and remembers it.
Back up your normal emulator saves before confirming. The copy is real files in
`Clawshot-seed-<number>/romfs`; an existing copy is never overwritten, even for different settings
with the same number. Enable only this seed in your emulator. Clawshot never starts the emulator.
If the tested Eden/Lichii game folder exists, it is offered as an explicit choice, not assumed.
Other emulators use only the folder picker. Copying is disabled in `--no-open`.

Before starting a game, both UI and pack Play check the PC-wide process list. Any running
`hookshot.exe` or `longshot.exe` (Windows) or program file named `hookshot` or `longshot` (Linux, from
`/proc/<pid>/exe`) refuses with “Hookshot or Longshot is already running. Quit it, then press Play.”
This happens before creating the save folder, opening the log or starting another process.

The pack's Make path was verified on Linux (WSL) with both a romfs folder and a `.nup`, producing
the same digest as Windows (maintainer verification, round 11). The UI shares that generator path,
so generation is expected to work on Linux and macOS; macOS itself is untested. **Play starts
`bin/hookshot.exe` or `bin/longshot.exe` on Windows and `bin/hookshot` or `bin/longshot` on Linux**, the
layout of a Hookshot Builder or Longshot game folder (Longshot README, *Running the game from the command
line*: in a game folder, `longshot` is the launcher and the game itself is `bin/longshot`). A Linux source
build without `bin` is refused like any folder-root launcher, and a folder holding the other system's game
is refused before anything is written. Neither Hookshot nor Longshot has a macOS build (Longshot README,
*What you need*: Windows 10/11 or Linux), so Play stays off there. Linux Play is **built, not accepted by
the maintainers in game**; Linux Make verification does not certify the Linux UI.
Windows app Play on **Longshot v3.0.0-rc.2** passed Kareem's 2026-11-13 seed-101 check:
isolated saves, game options including Ocarina controls, shuffled rewards, Xbox prompts and reload.

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
| Exclusive real-folder emulator export | `src/clawshot/app/emulator.py` |
| Generator-version-bound player share strings | `src/clawshot/app/sharing.py` |
| Game-free source-release allowlist and archive command | `src/clawshot/ui/release.py` |
| Read-only Hookshot/Longshot game and Longshot Launcher folder detection | `src/clawshot/pack/hookshot.py` |
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
3. Use `unavailable` for a choice that is not yet available, with a plain-language reason. It is also refused
   by validation. Use `enabled_when` for a setting that currently has no effect: a list of
   `{key, contains|equals|greater_than, reason}` conditions, all required. Inactive values are
   preserved; they are not silently reset or removed from CS1.
4. Group/display options are presentation metadata. Multi-choice cards can supply `status_labels`;
   fast start uses Skipped/Plays. `clears` identifies derived override keys to clear when a control
   changes, rather than hard-coding a field dependency in JavaScript.
   Check totals belong to the generator's actual result, not schema prose or a second UI eligibility
   algorithm: new Gift checks must not require editing a copied count or an unavailable-check list here.
5. Run the synthetic app/HTTP tests, then exercise the actual UI and any changed generator path.
   Keep seeds/game files outside the repository. Follow the project's full gates and in-game
   evidence rules for changes to gameplay.

### Restyle or change fonts

All colors live in the `:root` block of `style.css`. The two font variables are `--serif`
(titles/tabs/section headings/panel titles) and `--sans` (rows/values/body/hints). Change those
stacks there; do not put font families on individual controls. Check row heights, long paths,
disabled controls, keyboard focus, and 1280×860 idle/running/finished captures afterwards.
The approved stacks prefer Palatino and Candara with platform fallbacks.
A future bundled font is a **licence decision for the maintainers**, not an automatic OFL addition:
rule 7's accepted dependency licences do not currently list OFL. No font file is bundled today.

## Verification and limits

`tests/test_app.py`, `test_app_schema.py`, `test_app_play.py` and `test_ui.py` use invented
worlds/resources. The HTTP suite exercises real generation/writing, worker responsiveness,
cancellation, original fill errors, publication races, security and spoiler consent. Play tests
compare read-only plans, digest refusal, one-mod discovery, private saves, and input/output links;
they never launch a game. Detection tests use synthetic Hookshot, Longshot and Longshot Launcher
folders; Longshot Play has not been played. Dialog adapter smoke uses a synthetic picker, not an OS dialog.
The adapter prefers [pywebview FileDialog enums](https://pywebview.flowrl.com/api/) with the requested
legacy-constant fallback. Headless screenshots use `--no-open` and a fresh browser profile; no
OS dialog/window may be triggered. Keep screenshots outside the repository.

Kareem confirmed a real pywebview window was responsive and Browse opened a normal folder picker
on 2026-11-10. This does not confirm its NUP file picker or browser/Tk picker.

Not implemented in the current checkout:
- gamepad/Steam Deck controller navigation (keyboard/mouse only);
- the planned Tracker tab (not a separate tracker application);
- a bundled executable/installer or bundled fonts;
- Linux/macOS UI runtime certification.

Seed packs still use Make/Play; the UI is available in the public release zip, from a source checkout or an
installed Python package containing its static assets. Architecture and the local HTTP contract:
[UI plan](../plans/05-ui.md).

## Sharing

Copy the result's number, settings and short hash. Enter a shared seed on Generate applies its
number and settings together; another Clawshot version is refused before generating anything.
Player strings begin `Clawshot-<version>:`; the existing CS1 codec remains the internal app/CLI format.
The short hash comes from the finished files, not the number alone. Same version, number, settings
and supported game files are required to reproduce it; timestamps and output paths are not hashed.
On Discord, share the settings string with **Copy for Discord**, or paste it inside single backticks
(`` `Clawshot-…` ``). Plain text loses the `_` characters Discord takes for italics, and the
string then fails to apply; the string itself is unchanged, with no Discord-only format.

## Play note and spoilers

**Play note (spoilers)** is a full spoiler: its wrong-age table, opening route and All shuffled
rewards table list items by place. Generate and View seed never open or preview it automatically.
Choose the labeled action in the result or My seeds to open its equally labeled viewer.
There is no spoiler-free note yet; that requires a later generator change. Raw spoiler JSON
stays behind explicit confirmation. Note contents are rendered as text nodes, never executed
as HTML or remote content.

## Remake item names

Menus and play notes use the remake's names, such as Echo Gem, Fairy Bow and Lon Lon Milk.
`data/item_names.toml` is display-only: logic/actor/placement identities do not change. Spoiler
JSON keeps those logical names and includes the corresponding display-name map. Runtime game
text takes precedence for hints; unknown items keep their existing name.

## Build a UI release

```sh
uv run python -m clawshot.ui.release --out E:/Clawshot-releases
```

This builds `Clawshot-<project version>.zip` without reading a dump or generating a seed. It
contains source, local UI assets, the starters/PowerShell helper, lock file, licences/notices and
a five-line READ ME. The positive source allowlist excludes tools, caches, tests and game/output
files. Both shell entry points are executable in the zip; an existing release is never replaced.

## Troubleshooting

### Where do I get the game, and which version do I need?

Clawshot provides and downloads no game files. Dump your own Nintendo Switch 2 copy of *Ocarina
of Time*, including **Version 1.1.1 (update v131072)**, build **e0f3ccfa**; the base game alone is not enough.
Choose its updated `romfs`, full `.nup`, or dump folder with `base/romfs` and `updates/131072/romfs`.
**Check** on Game compares four game files' contents with the supported build's fingerprints, not
the folder name. It never starts or changes the game. A different update or incomplete dump is
refused: check your own dump and update, rather than renaming files or bypassing the check.
If Check says **Not found: …**, that path no longer exists (including a stale remembered dump).
Choose your romfs folder or .nup again. An existing file of the wrong kind still gets the input-type advice.

### Which Hookshot or Longshot version do I need?

Use a current Hookshot or Longshot with mod loading. Clawshot checks the program for that support
(its `HOS_MODS` marker), not just its version number. On Hookshot, **2.0.14** has been played and seeds
also start on **2.1.0**. Longshot **v3.0.0-rc.2** passed Kareem's Windows app Play check on
2026-11-13, including isolated saves/options, a shuffled chest and reload persistence.

- **Hookshot:** on Game, choose the Hookshot Builder game folder containing `bin/hookshot.exe` on Windows
  or `bin/hookshot` on Linux, then press **Detect**. Update or repair Hookshot if refused. A Linux
  source-build folder without `bin/hookshot` is not enough. Hookshot's GitHub repository has been offline
  since 2026-11-13.
- **Longshot:** get the Longshot Launcher from <https://longshot.magicbean.dev/download> (project:
  <https://git.magicbean.dev/MagicBeanDev/Longshot>) and let it build the game from your own dump
  (Longshot README, *Install and play*). On Game, choose the game folder containing `bin/longshot.exe`
  (Windows) or `bin/longshot` (Linux), or the launcher's folder (see **Game** above), then press **Detect**.

Neither is needed for generating a seed or copying it to an emulator.

### Why is Play missing or greyed out?

Generate a seed, or choose **View seed** in My seeds. Play needs a chosen Hookshot or Longshot folder,
Windows or Linux, a successful **Detect**, and finished, unchanged seed files.
It is disabled while generating or while a seed launched by this UI runs; quit any running Hookshot
or Longshot before pressing Play. Sessions with desktop actions turned off also disable Play. Read the
message beneath the buttons. Generate old or changed seeds into a new folder; keep the old folder and its
saves. macOS has no Hookshot or Longshot Play support; use the emulator steps instead.

### What is the hash, and what if mine differs?

**Hash** under Seed ready on Generate, also beside entries in My seeds, is a short fingerprint
of the finished files, not the seed number. Share the number, whole settings string and hash.
If yours differs, check the Clawshot version, number, whole settings string and supported game
files match the shared recipe. Report both hashes and the recipe if it still differs; never edit
files or bypass a failed check. For changed seed files, generate into a new folder and keep old saves.

### Why does a settings string from Discord fail to apply?

Discord reads text between two `_` characters as italics and removes them, so a string pasted as
plain text can lose characters. Ask for it again inside single backticks (`` `Clawshot-…` ``), or have
the sender use **Copy for Discord**. Do not guess the missing characters.

### Does it work on Linux or macOS?

On Linux, use `clawshot.sh`; Play supports a Linux Hookshot Builder game folder with `bin/hookshot`
and a Longshot game folder with `bin/longshot`.
Linux's seed-pack Make was checked in WSL with matching Windows output; Linux Play has not yet
been accepted in game by the maintainers. **macOS is untested; a contributor is testing it.**
Use `Clawshot.command` there; macOS has no Play, but can generate and copy to an emulator.
Gamepad and Steam Deck controller navigation are not available yet.

### Can I use an emulator?

Yes, without Hookshot or Longshot. Use **Copy to my emulator**, choose this game's mod folder and confirm.
Back up your emulator saves first, then enable only this seed in its mod menu. Clawshot does not
start the emulator or replace an existing copy. Lichii has play results; other layouts are untested.
See [manual emulator steps](seed-pack.md#emulator--console-loading).

### Can I load a seed in Longshot without Play?

Yes, but it uses your normal Longshot saves. Quit Longshot and back up its saves: the `user` folder in
the game folder on Windows, `~/.local/share/longshot` on Linux (Longshot README, *Where the files go*).
Copy this seed's `seed/romfs` folder to `<game folder>/mods/Clawshot-seed-<number>/romfs` (Longshot
README, *Mods*; with the launcher, its **Open folder** for that build shows the game folder). Start a
**New Game in an empty slot**. While the mod is in `mods` it applies to every save slot, so remove the
`Clawshot-seed-<number>` folder before playing your normal saves. Details:
[Longshot manual mods route](seed-pack.md#longshot-manual-mods-route).

### Where are the saves made by Play?

In `user` inside **your chosen output folder**, usually `Documents/Clawshot/seed-<number>/user`,
not the game's normal save folder. **Open seed folder** opens the inner `seed` folder: go up one
folder to find `user` and the log (`hookshot_log.txt` or `longshot_log.txt`). Keep the whole output
folder when moving or backing up a playthrough. Emulators, Hookshot's own launcher and the Longshot
Launcher use their normal saves instead.

### How do I report a crash or a Clawshot error?

Use [In-game bug or crash](https://github.com/hiKareeem/Clawshot/issues/new?template=bug_report.yml)
for problems while playing. Give the Clawshot version (zip folder name or `Clawshot-<version>:`
settings-string start), seed, whole settings string, hash, game and version (Hookshot: the log's first
line; Longshot: the `longshot v…` line near the top of its log, or the version **Detect** shows), OS,
area, Link's age and what Link was doing. Attach **only the whole log**: `hookshot_log.txt` or
`longshot_log.txt` from the output folder beside `seed` and `user` (for Longshot loaded without Play,
`longshot_log.txt` in the game folder). It contains folder paths, including your user name, but
no game data; those paths will be public. Emulator players attach their emulator's log instead.
Never attach game files, seed folders, saves, keys, caches or spoilers. On Discord, paste the settings
string inside single backticks or with **Copy for Discord**.

For UI, Generate or game-check problems, use [Clawshot itself](https://github.com/hiKareeem/Clawshot/issues/new?template=clawshot.yml):
give the version, OS and whole UI error text (terminal error if it never opens). Attach nothing.
[Discord](https://discord.gg/7R5ZXPcJqn) is also available for help.

### Known issues

- **Seeds made with Clawshot 0.1.1 or earlier (including community seed 11) can be impossible to
  finish:** keys placed on Spirit Temple's outdoor hand chests are lost. To check an old seed,
  open its `seed/spoiler.json` (this reveals rewards) and find `Spirit Temple Silver Gauntlets Chest`
  and `Spirit Temple Mirror Shield Chest` under `placements`. These are the Desert Colossus statue
  hand chests at the child and adult exits. If either reward is a Small Key or Boss Key, generate
  a fresh seed with a newer Clawshot and start a new game; keep the old folder and saves.
  Newer versions never put keys there while dungeon items stay home; with **Small keys
  anywhere** a hand chest can hold a small key named to its own dungeon, so it is not lost.
- Ocarinas from chests have no visible model, but you still receive them.
- Dampé's digging prize and Bombchu Bowling prizes show the original prize but give the seed's item.
- **Saves started with older builds:** Save and Continue after an age-unusable pickup before using other
  items; changing areas does not clear the old item-bar jam. New games initialize an empty nut slot (0/20);
  child Bow first followed by Boomerang use without a reload passed Kareem's 2026-11-12 check.
- On **Hookshot 2.1.0**, ordinary text shows Switch button icons while a seed is loaded.
  **Longshot v3.0.0-rc.2 showed Xbox prompts correctly** in Kareem's 2026-11-13 seed-101
  app check. Longshot merges button-prompt sizes into the mod's size table (Longshot README, *Mods*).
  The ocarina note interface is drawn separately.
- Earlier seeds can also lose boss keys, maps and compasses moved to small chests inside their
  own dungeon; pickup text or an icon is not saved ownership. Repaired map/compass saves
  and menus, boss-key credit, pickup indicator and normal boss-door opening passed in-game.
  Rebuilding cannot re-award opened chests.
- Of dungeon items outside their own dungeon, only the opt-in **Small keys anywhere** choice
  exists: small keys in any shuffled chest, named to their own dungeon, with the game's key
  counters still showing only the dungeon you are in. Moving boss keys, maps or compasses
  outside their dungeon, and wider keysanity, are not available.
- Both `play-note.md` and `spoiler.json` reveal item locations. Do not open them if you want surprises.
