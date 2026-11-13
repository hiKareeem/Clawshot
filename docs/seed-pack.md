# Seed packs

Packs are public test builds: share the zip, never a generated `seed` folder (that one holds game files).
Code is included, not hidden. No game files, decoded data, generated overlay, save or spoiler
is distributed; the zip records only the reference seed's SHA256 digest. `READ ME FIRST.txt` is the
player-facing summary (steps, known issues, the Discord link); this file has the details.

## Tester (Windows, Hookshot or Longshot)

1. Set up Hookshot or Longshot with your own legal dump of the supported game update (build `e0f3ccfa`).
   Longshot, the continuation of Hookshot (Longshot README, introduction), is built on your PC by the
   Longshot Launcher: <https://longshot.magicbean.dev/download> (project:
   <https://git.magicbean.dev/MagicBeanDev/Longshot>). Hookshot's GitHub repository has been offline since
   2026-11-13. Emulator players skip this step.
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/). Internet is needed for
   Python and locked dependencies on the first build.
3. Extract the zip into its **own new folder outside RomFS and your Hookshot or Longshot folders**, e.g.
   `C:\Clawshot\seed-8`. Extract every pack separately: each has its own `user` save folder. Do not
   extract over an old pack.
4. Run `Make seed.bat`. It asks once for your **`.nup` file or extracted RomFS folder** and an
   **optional** Hookshot or Longshot folder: the game folder containing `bin`, or a Longshot Launcher
   folder (Play then uses the launcher's newest build, as the [UI guide](ui.md) describes for **Game**).
   Leave it **empty for emulator loading**; Make needs no Hookshot or Longshot installation or executable.
   Enter paths without enclosing quotes. It stores your answers in this pack's `folders.json` (`romfs` and
   `game`; a `folders.json` from an older pack, which named the folder `hookshot`, is still read).
   It fingerprints resources inside either source before generating anything, then uses frozen dependencies
   and the included source/settings/seed. The complete output, including spoiler and play note, must match
   the reference digest. An existing seed is verified, **never regenerated or overwritten**.
5. Only after **Verified seed** appears, run `Play seed.bat`. It checks the digest again, then starts
   only the game in `bin`, from its game folder: `bin\hookshot.exe` with `HOOKSHOT_NO_UPDATE_CHECK=1`, or
   `bin\longshot.exe` with `LONGSHOT_NO_UPDATE_CHECK=1`; always with `HOS_FS_OVERLAY` cleared,
   `HOS_MODS=<pack>` (only `seed` is a mod) and `--user <pack>\user`.
   Hookshot needs a build that can load mods (tested on 2.0.13). Kareem played a community seed on
   Longshot through an isolated launcher on 2026-11-13; this new app/pack Play path is not yet
   accepted in game. If Play says your game cannot load mods, update it, then run Play again.
   Detection checks the game's binary for `HOS_MODS`, not version labels or log wording.
   No seed copy or link is made.
   Only Play requires the bin executable. If no game folder was saved, Play stops and points to the
   emulator steps below. A missing bin executable is a hard stop: the folder-root launcher ignores save
   isolation and is never used. Quit any running Hookshot or Longshot first; Play refuses while one runs.
   Start a **new game**; later plays continue this pack's saves. First Play copies only
   `option.sav` and `account.sav` from the newest ID folder under the chosen build's `user/save`,
   preserving game options such as Invert Jump. Existing seed users are left alone; no `slot_NN`
   playthrough is copied or reset. Missing source files are skipped and reported in the Play result.
   The game's own `*_options.ini` remains in its game folder and needs nothing.
6. `seed/play-note.md` and `seed/spoiler.json` both reveal item locations; open them only if you want spoilers.
   For reports, attach only the whole `<pack>/hookshot_log.txt` or `<pack>/longshot_log.txt` (if Longshot's
   is empty, its own `longshot_log.txt` in the game folder), not `pack.json`, saves, seed folders or your
   dump. On Discord, paste the settings string from `pack.json` inside single backticks.

Dungeon check labels include their map floor (`1F`, `2F`, `B1`, ...), from the game's map metadata,
not the old N64 room name or an estimated height. Some rooms span floors; each chest uses its own
map icon's floor. GTG and Ganon's Castle have stored floor metadata but no corresponding dungeon-floor
texture set; their labels are data-derived, not a newly verified pause-menu view.

Version/digest failure: stop and report the actual/expected fingerprints in help. Do not bypass the check.
To change stored paths, close the game, remove only this pack's `folders.json`, and run Make again.
A partial or altered `seed` folder is not repaired in place: extract the original zip into a **new** folder.
Keep the old folder and its saves. Avoid multiple simultaneous games using the same pack.
Do not add other mods inside this pack: Play requires exactly one discoverable mod, `seed\romfs`.
Hidden `.romfs-*` caches are not mods. The pack does not update Hookshot or Longshot or touch your game directory.

### Hookshot manual mods route

Prefer **Play seed.bat**, which isolates saves. For manual loading, after Make succeeds and
Hookshot is closed, copy `seed\romfs` to `<Hookshot>\mods\Clawshot-seed-<number>\romfs`
(real folders, not links). Keep exactly one seed mod enabled; remove/disable other randomizer
mods before launching normally. The mods root itself is not a mod: it holds the named folder
which holds `romfs`. Names starting `.`, `-` or `_` are ignored.

**The normal Hookshot launcher uses the main save folder. Back up the entire playthrough
before a New Game: it overwrites that playthrough.** The pack's `user` folder does not isolate
this route. Disabling/removing the mod does not restore saves. Never replace files while the
game is running. Do not set `HOS_FS_OVERLAY`: on Hookshot 2.0.12 and later, it crashes
at startup with Clawshot's size table through that route. Confirm `mods: <file> <- <path>`
in the game log (first 200 files).

### Longshot manual mods route

Prefer **Play seed.bat**, which isolates saves. Loading the seed through Longshot's own launcher uses
your normal saves and has not been played with Clawshot. Facts below are from the Longshot README
(*Mods*, *Where the files go*, *If something goes wrong*) and the Longshot Launcher README (*Using it*,
*Design decisions*).

1. Make succeeds; quit Longshot.
2. **Back up your saves.** Windows: the `user` folder in the game folder (the launcher keeps one per
   build). Linux: `~/.local/share/longshot`, shared by every build.
3. Copy `seed\romfs` to `<game folder>\mods\Clawshot-seed-<number>\romfs` (real folders, not links).
   Use the game folder of the build you will start: the launcher's main **Play** starts its default build,
   and each build's **Open folder** shows its folder, the one holding `bin`. The final folder must contain
   overlay subfolders such as `Banc`, not another nested `romfs`.
4. Keep only this seed in `mods`. When two mods have the same file, the one whose folder name sorts last
   wins, and only one mod's size table is used; a folder whose name starts with `-` or `_` is off.
5. Start a **New Game in an empty slot**.
6. While it is in `mods`, the seed applies to **every save slot**. Remove the `Clawshot-seed-<number>`
   folder before playing your normal saves; removing the mod does not undo changes to a save.

Never replace files while the game is running, and do not set `HOS_FS_OVERLAY`. The game folder's
`longshot_log.txt` holds the last run and names each mod and the files read from it: look for this seed's
folder there, plus the in-game result.

**Known cosmetic issue, by game:** on Hookshot (including 2.1.0), while a seed is loaded, button icons in
text are the game's own Switch icons, not Hookshot's Xbox/PlayStation/Steam Deck replacements. Controls are
unchanged. Hookshot currently falls back because every seed supplies its resource size table; do not
delete that table or change seed bytes to restore icons. Longshot merges the button prompts' sizes into a
mod's table at start (Longshot README, *Mods*); a headless v3.0.0-rc.2 boot of a Clawshot seed logged the
merge on 2026-11-13, so controller icons may stay in text there. That is not yet seen in play.

### NUP input

Give the full `.nup` filename, not its containing folder. Make reads it **read-only** using
[a55uka's MIT NUP reader](https://github.com/a55uka/nup), shipped with its licence. No separate
extractor, keys or Hookshot or Longshot installation is needed. NUP compression needs the locked Python/zstd
dependencies, so uv may install those before the version check; no seed, game-file cache or saved
folder configuration is created until that check succeeds. Folder preflight still runs before uv.

The newest base/update package must contain a complete supported RomFS. Add-ons are not used;
incomplete or unsupported newer updates never fall back to an older package. Every resource read
is checked against its NUP SHA256. The same four-resource fingerprint is computed **from inside
the container**, not from its name or display-version metadata.

After preflight, Make creates a unique `.romfs-*` working cache inside this extracted pack.
It contains only the generator's resource working set (placements, flows, messages, supported
item/shop packs and supporting tables/components), not the whole dump or ExeFS/models/textures/audio.
The cache is removed when generation finishes or fails. A force-terminated Make may leave its own
cache behind; keep it private like `seed` and use a fresh pack folder rather than repairing in place.
Never share any locally generated cache or overlay. The published zip contains neither.

### Dump folders

A dump folder may keep the game in `base/romfs` and its update in `updates/131072/romfs`.
Clawshot reads the newest update over the base without changing either. A base-only dump is
refused with the same base-game/update hint as a base-only `romfs`: include Version 1.1.1 (update v131072).
No working cache or seed is made before that check passes.


## Emulator / console loading

**Confirmed by Kareem:** seed8 loads and plays on Lichii (Eden/yuzu family), 2026-11-09;
reviewer record `plans/playtest/answers.md`, R9-LICHII, main `d3e5c08`.
Install uv and extract the pack as above, then run **Make seed**, give your `.nup` filename or
RomFS folder and **leave the optional Hookshot or Longshot answer empty**. No Hookshot or Longshot
installation is needed. Wait for Verified seed, then follow the steps below instead of Play. Do not run
Play for this route.

1. **Back up this game's entire emulator save folder first.** Start a **New Game** for the seed:
   it takes over the emulator's save slots for this game. The pack's isolated `user` folder
   does not isolate emulator saves.
2. Copy the generated `seed\romfs` folder into
   `%APPDATA%\eden\load\0400486024DEC000\<mod name>\romfs`.
   The final folder must contain overlay subfolders such as `Banc`, not another nested `romfs`.
3. In the game's **Properties > Add-ons**, tick that mod, then launch the game in Lichii and start New Game.
4. To play normally, untick the mod in Add-ons. Restore your backed-up save if you want the pre-seed progress;
   disabling the mod alone does not restore saves.

For reports, name the emulator/version and attach only its own log, not `pack.json`;
no Hookshot or Longshot log is produced on this route. Paste the seed number and settings from `pack.json`
(inside single backticks on Discord).

Other conventional layouts are **untested with Clawshot**:

| Runtime | Generated overlay destination |
|---|---|
| Ryujinx | `mods/contents/0400486024dec000/<name>/romfs` |
| Atmosphere | `atmosphere/contents/0400486024DEC000/romfs` |

Only the Lichii path and loading result above are confirmed. Keep backups before trying another runtime.
Copy generated files locally from your own dump; never redistribute the overlay.

## Publisher

```sh
OOT_ROMFS=E:/Games/Hookshot/romfs uv run python -m clawshot.pack --settings <CS1> --seed 8 --out E:/OOTRemake/work/seed-8-next.zip
```

`--romfs <path>` may replace `OOT_ROMFS`; either accepts a RomFS folder or `.nup` file. The publisher needs the read-only supported dump to compute
an oracle; testers do not need the publisher's dump. The zip destination must be new and outside both
repository and dump. No existing zip or seed folder is replaced.

The builder positively selects Clawshot `.py`/`.toml` source and launcher templates, root build metadata,
`uv.lock`, README, LICENSE, NOTICE and this guide. Plans, tests, `.git`, environments and generated files
are excluded. It generates a reference from **that exact source snapshot** in a disposable external
folder, hashes it, and discards it. Only `pack.json`'s digest survives, not filenames or resource bytes.
The zip uses fixed timestamps and sorted entries. No new dependency; the vendored reader's MIT licence is included.

RomFS has no NSO build-ID header. Preflight identifies the known `e0f3ccfa` dump by a SHA256 fingerprint
of four existing files (dictionary pack, GameDataList, EventSetting and child Kokiri Dynamic Banc),
not by trusting a folder name or the Hookshot or Longshot version. It is a supported-dump signature, not an
executable identity claim. A modified file elsewhere is caught if it changes the generated seed digest;
this is not a whole-dump integrity scanner.

The output digest is SHA256 over sorted relative UTF-8 paths, each followed by NUL and that file's raw
SHA256 digest. It includes every overlay file, `spoiler.json` and `play-note.md`, not timestamps or
absolute paths. Save/log files are outside the seed folder. Replay requires the included generator/data
and frozen dependency versions; `0.1.0` alone is not a unique source revision. A changed catalogue or
patch must be shipped in a newly built pack with a newly computed digest.

Acceptance still needs an invited tester/Kareem to play: Make succeeds, Play opens the isolated new game,
the log reports `mods: <file> <- <path>`, and the displayed seed placements agree.
Agent verification uses `python -m clawshot.pack.runtime play --root <pack> --dry-run` only:
the same checks print the command, environment, mod and log paths without starting anything or creating
the user/log. `CLAWSHOT_DRY_RUN=1` also enables this through the normal Play entry point.

### Maintaining the NUP working set

`src/clawshot/pack/resources.toml` is the single cache definition: exact files, resource-family
patterns, the supported item/shop pack template and fast-start component discovery. A patch that
reads another native resource adds its path there, not another extraction branch in Python.

```sh
CLAWSHOT_WORKERS=1 OOT_ROMFS=<romfs> OOT_NUP=<game.nup> uv run pytest tests/test_pack_nup_dump.py -m dump
```

Run under the round's gate lock, serially. The dump matrix generates and writes complete seeds
from the cache directory **alone**, then compares every output path and byte digest with a separate
full-RomFS generation. It covers each enabled shuffle kind, all forest modes/fast-start skips,
free travel, both hint modes, songs/prices/partial shops and (once present) all Door of Time modes.
Missing inputs fail by RomFS path; missing glob members also fail output equality. Re-run after
each integration/rebase so newly merged patch inputs cannot silently rely on the publisher's dump.
