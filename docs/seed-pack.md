# Seed packs

Packs are public test builds: share the zip, never a generated `seed` folder (that one holds game files).
Code is included, not hidden. No game files, decoded data, generated overlay, save or spoiler
is distributed; the zip records only the reference seed's SHA256 digest. `READ ME FIRST.txt` is the
player-facing summary (steps, known issues, the Discord link); this file has the details.

## Tester (Windows, Hookshot)

1. Set up Hookshot with your own legal dump of the supported game update (build `e0f3ccfa`).
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/). Internet is needed for
   Python and locked dependencies on the first build.
3. Extract the zip into its **own new folder outside RomFS and Hookshot**, e.g. `C:\Clawshot\seed-8`.
   Extract every pack separately: each has its own `user` save folder. Do not extract over an old pack.
4. Run `Make seed.bat`. It asks once for your **`.nup` file or extracted RomFS folder** and an
   **optional** Hookshot folder (the folder containing `bin`).
   Leave Hookshot **empty for emulator loading**; Make needs no Hookshot installation or executable.
   Enter paths without enclosing quotes. It stores your answers in this pack's `folders.json`.
   It fingerprints resources inside either source before generating anything, then uses frozen dependencies
   and the included source/settings/seed. The complete output, including spoiler and play note, must match
   the reference digest. An existing seed is verified, **never regenerated or overwritten**.
5. Only after **Verified seed** appears, run `Play seed.bat`. It checks the digest again, then starts
   `<Hookshot>\bin\hookshot.exe` with `HOOKSHOT_NO_UPDATE_CHECK=1`, `HOS_FS_OVERLAY` cleared,
   `HOS_MODS=<pack>` (only `seed` is a mod) and `--user <pack>\user`.
   Requires a Hookshot that can load mods (tested on 2.0.13).
   If Play says your Hookshot is too old, update Hookshot, then run Play again.
   Detection checks the game's binary for `HOS_MODS`, not version labels or log wording.
   No seed copy or link is made.
   Only Play requires the bin executable. If no Hookshot folder was saved, Play stops and points to the
   emulator steps below. A missing bin executable is a hard stop: the folder-root launcher ignores save
   isolation and is never used.
   Start a **new game**; later plays continue this pack's saves. No main save is copied or reset.
6. Read `seed/play-note.md`. `seed/spoiler.json` reveals all placements. Reports should attach
   `<pack>/hookshot_log.txt` and `pack.json` (not saves, the overlay or your dump).

Dungeon check labels include their map floor (`1F`, `2F`, `B1`, ...), from the game's map metadata,
not the old N64 room name or an estimated height. Some rooms span floors; each chest uses its own
map icon's floor. GTG and Ganon's Castle have stored floor metadata but no corresponding dungeon-floor
texture set; their labels are data-derived, not a newly verified pause-menu view.

Version/digest failure: stop and report the actual/expected fingerprints in help. Do not bypass the check.
To change stored paths, close the game, remove only this pack's `folders.json`, and run Make again.
A partial or altered `seed` folder is not repaired in place: extract the original zip into a **new** folder.
Keep the old folder and its saves. Avoid multiple simultaneous games using the same pack.
Do not add other mods inside this pack: Play requires exactly one discoverable mod, `seed\romfs`.
Hidden `.romfs-*` caches are not mods. The pack does not update Hookshot or touch your game directory.

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

**Known cosmetic issue:** while a seed is loaded, button icons in text are the game's own
Switch icons, not Hookshot's Xbox/PlayStation/Steam Deck replacements. Controls are unchanged.
Hookshot currently falls back because every seed supplies its resource size table; do not
delete that table or change seed bytes to restore icons.

### NUP input

Give the full `.nup` filename, not its containing folder. Make reads it **read-only** using
[a55uka's MIT NUP reader](https://github.com/a55uka/nup), shipped with its licence. No separate
extractor, keys or Hookshot installation is needed. NUP compression needs the locked Python/zstd
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


## Emulator / console loading

**Confirmed by Kareem:** seed8 loads and plays on Lichii (Eden/yuzu family), 2026-11-09;
reviewer record `plans/playtest/answers.md`, R9-LICHII, main `d3e5c08`.
Install uv and extract the pack as above, then run **Make seed**, give your `.nup` filename or
RomFS folder and **leave the optional Hookshot answer empty**. No Hookshot installation is needed. Wait for Verified seed, then follow
the steps below instead of Play. Do not run Play for this route.

1. **Back up this game's entire emulator save folder first.** Start a **New Game** for the seed:
   it takes over the emulator's save slots for this game. The pack's isolated Hookshot `user` folder
   does not isolate emulator saves.
2. Copy the generated `seed\romfs` folder into
   `%APPDATA%\eden\load\0400486024DEC000\<mod name>\romfs`.
   The final folder must contain overlay subfolders such as `Banc`, not another nested `romfs`.
3. In the game's **Properties > Add-ons**, tick that mod, then launch the game in Lichii and start New Game.
4. To play normally, untick the mod in Add-ons. Restore your backed-up save if you want the pre-seed progress;
   disabling the mod alone does not restore saves.

For reports, name the emulator/version and attach its own log plus `pack.json`;
the Hookshot log is not produced on this route.

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
not by trusting a folder name or the Hookshot version. It is a supported-dump signature, not an
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
