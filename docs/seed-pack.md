# Private seed packs

Repository and packs are private to invited testers. Do not repost the zip or its source.
Code is included, not hidden. No game files, decoded data, generated overlay, save or spoiler
is distributed; the zip records only the reference seed's SHA256 digest.

## Tester (Windows)

1. Set up Hookshot with your own legal dump of the supported game update (build `e0f3ccfa`).
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/). Internet is needed for
   Python and locked dependencies on the first build.
3. Extract the zip into its **own new folder outside RomFS and Hookshot**, e.g. `C:\Clawshot\seed-8`.
   Extract every pack separately: each has its own `user` save folder. Do not extract over an old pack.
4. Run `Make seed.bat`. It asks once for the RomFS folder and Hookshot folder (the folder containing `bin`).
   Enter paths without enclosing quotes. It stores them in this pack's `folders.json`.
   It fingerprints the supported RomFS before running uv or generating anything, then uses frozen dependencies
   and the included source/settings/seed. The complete output, including spoiler and play note, must match
   the reference digest. An existing seed is verified, **never regenerated or overwritten**.
5. Only after **Verified seed** appears, run `Play seed.bat`. It checks the digest again, then starts
   `<Hookshot>\bin\hookshot.exe` with `HOOKSHOT_NO_UPDATE_CHECK=1`, the pack's overlay and `--user <pack>\user`.
   Missing bin executable is a hard stop: the folder-root launcher ignores save isolation and is never used.
   Start a **new game**; later plays continue this pack's saves. No main save is copied or reset.
6. Read `seed/play-note.md`. `seed/spoiler.json` reveals all placements. Reports should attach
   `<pack>/hookshot_log.txt` and `pack.json` (not saves, the overlay or your dump).

Version/digest failure: stop and report the actual/expected fingerprints in help. Do not bypass the check.
To change stored paths, close the game, remove only this pack's `folders.json`, and run Make again.
A partial or altered `seed` folder is not repaired in place: extract the original zip into a **new** folder.
Keep the old folder and its saves. Avoid multiple simultaneous games using the same pack.
Do not point Hookshot's separate mods loader at another randomizer overlay: the digest checks this pack,
not unrelated installed mods. The pack does not update Hookshot or touch your game directory.

## Publisher

```sh
OOT_ROMFS=E:/Games/Hookshot/romfs uv run python -m clawshot.pack --settings <CS1> --seed 8 --out E:/OOTRemake/work/seed-8-next.zip
```

`--romfs <path>` may replace `OOT_ROMFS`. The publisher needs the read-only supported dump to compute
an oracle; testers do not need the publisher's dump. The zip destination must be new and outside both
repository and dump. No existing zip or seed folder is replaced.

The builder positively selects Clawshot `.py`/`.toml` source and launcher templates, root build metadata,
`uv.lock`, README, LICENSE, NOTICE and this guide. Plans, tests, `.git`, environments and generated files
are excluded. It generates a reference from **that exact source snapshot** in a disposable external
folder, hashes it, and discards it. Only `pack.json`'s digest survives, not filenames or resource bytes.
The zip uses fixed timestamps and sorted entries. No new dependency.

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
the log reports `fs: OpenFile(...): from the overlay`, and the displayed seed placements agree.
Agent verification never starts the game.
