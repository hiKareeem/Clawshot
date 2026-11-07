# Round 1, track C: Hookshot `mods` folder (cs1c)

Worktree `E:/OOTRemake/hookshot-r1/mods`, branch `mods-folder` (fork hiKareeem/Hookshot, based on `upstream/main`
033271f). Not pushed, not merged.

## Commits

| Commit | What |
|---|---|
| `8171cfb` | Mods folder: RomFS mods in the emulator layout (`host/mods.c` new, the three stubs out of `host/mkw_glue.c`, a comment in `host/hos_main.c`, a "Mods" section in `readme.md`) |

## What was built

- `host/mods.c`: the RomFS part of SkyboundTotk's `a64-kit/hos/mods.c` (MIT; fetched with `gh api`, its only
  commit `4315342`, 2026-10-28), credited in the file header and the commit body. Layout `mods/<name>/romfs/...`
  beside `hookshot.exe` or `HOS_MODS=<dir>`; deeper emulator layouts (`contents/<title id>/<name>/romfs`, up to 4
  levels); folders starting with `-` or `_` are off; when two mods have the same file the last-sorted mod path
  wins; every mod file is indexed once at start (hash table, lower-case keys), `hos_mods_romfs` answers each
  `rom:` path, `hos_mods_dir_extras` lists mod-only entries in a folder listing. Log lines: `mods: <name>: <n>
  RomFS files`, `mods: <n> mods from <dir>: <n> RomFS entries`, and per file read `mods: <path> <- <host file>`
  (first 200).
- The three stubs (`hos_mods_init`, `hos_mods_romfs`, `hos_mods_dir_extras`) removed from `host/mkw_glue.c`.
  `nx2/build.py` needed no change: it compiles every `host/*.c`.
- `HOS_FS_OVERLAY` is untouched (`host/nn_fs.c` OpenFile looks at it after `host_path`, which asks the mods), so
  an overlay file still wins over a mod file. Track A's chest check keeps working as planned.
- Differences from Skybound's file: no `__EMSCRIPTEN__` stubs (Hookshot has no web build), and the executable's
  folder and a mod file's name are found with either path separator (`last_sep`), because `host/posix`'s
  `GetModuleFileNameA` returns `/` paths and Skybound's `strrchr(root, '\\')` would find no mods folder on Linux.

### exefs patches: left out

Provisional (spec item 2 allows it). Skybound places data patches using `image.json` beside `image.bin` (each
module's base, size, build id, `.text` end). A Hookshot game folder has only `image.bin`: `nx2/make_game.py`
copies `work/sa/image/image.bin` and nothing else, and the generated `hos_image.c` has module names and main's
build id but no per-module base, build id or `.text` range. Code patches would also need a lift with the patches
applied (Skybound's `build.py lift --mods`), which Hookshot's `nx2/lift.py` does not have. Bringing them in means
changing `nx2/standalone.py` / `nx2/make_game.py` (outside this track) and a lift option; most Switch exefs mods are
code patches anyway. A mod's `exefs` folder is logged as left out:
`mods: <name>: exefs patches are left out (the code is compiled ahead of time)`.

## Checks

| Check | Result |
|---|---|
| Real build: `make_game.py --romfs E:/Games/Hookshot/romfs --exefs E:/Games/Hookshot/.hookshot_exefs --out E:/OOTRemake/work/buildtest-mods/game --language en-US` from `E:/OOTRemake/work/buildtest-mods/tools` (worktree files + builder prebuilts + junctions, as specified) | exit 0 after 1300 s; log shows `mods.c ... 1s` compiled and `linked ...\hookshot.exe: 433 MB` (no undefined symbols with the stubs gone) |
| Linux: `clang --target=x86_64-linux-gnu -fsyntax-only -I host/posix -D_GNU_SOURCE -I host -I <rt64> -I <gen>` on `host/mods.c`, `host/mkw_glue.c`, `host/nn_fs.c`, against Ubuntu 22.04's `libc6-dev 2.35-0ubuntu3` and `linux-libc-dev 5.15.0-25` headers (extracted to `E:/OOTRemake/work/r1-hookshot-mods/sysroot`) | all three exit 0; `mods.c` clean with `-Wall -Wextra` (`mkw_glue.c` has two old `-Wformat` warnings, not from this change) |
| Boot 1 (headless, muted, `HOS_FS_TRACE=1`, 20 s, stopped by its own pid) with `mods/r1-test/romfs/Pack/ZsDic.pack.zs` (a byte-identical copy, sha1 equal, a new file, not a hard link), `mods/-off/romfs/...` and `mods/r1-exefs/exefs/test.pchtxt` | the loader's start-up lines all as expected (below); the game itself did not reach the file system in 20 s: a release build (`RX_RELEASE=1`) translates every shader before the game starts, and this folder had no caches |
| Boot 2 (same mods, `HOS_FS_TRACE=1 RX_VK_PRECOMPILE=0`, 20 s, started only after `tasklist` showed no `hookshot.exe`) | the game read `Pack/ZsDic.pack.zs` from the mod and went on loading with it (packs, RSDB tables, 60 fps presents by the end): log lines below |
| Boot 3 (as boot 2 plus `HOS_FS_OVERLAY=E:/OOTRemake/work/buildtest-mods/overlay` holding copies of `Pack/ZsDic.pack.zs` and `System/RegionLangMask.txt`) | `fs: OpenFile(...): from the overlay` for both; for `ZsDic` the mod line is logged first and the overlay file is the one opened: the overlay keeps working and wins over mods |

Boot 1 (`run1.log`) and every boot after it, the loader's start-up lines:

```
[hos host] mods: E:\OOTRemake\work\buildtest-mods\game\mods\-off is off (its name starts with -)
[hos host] mods: r1-exefs: exefs patches are left out (the code is compiled ahead of time)
[hos host] mods: r1-exefs: 0 RomFS files
[hos host] mods: r1-test: 1 RomFS files
[hos host] mods: 2 mods from E:\OOTRemake\work\buildtest-mods\game\mods: 2 RomFS entries
```

Boot 2 (`run2.log`), the line that shows the file came from the mod:

```
[hos ARes Loading 0] mods: Pack/ZsDic.pack.zs <- E:\OOTRemake\work\buildtest-mods\game\mods\r1-test\romfs\Pack\ZsDic.pack.zs
[hos ARes Loading 0] fs: OpenFile(content:/Pack/ZsDic.pack.zs)
```

Boot 3 (`run3.log`):

```
[hos sead::MainThread] fs: OpenFile(content:/System/RegionLangMask.txt): from the overlay
[hos ARes Loading 0] mods: Pack/ZsDic.pack.zs <- E:\OOTRemake\work\buildtest-mods\game\mods\r1-test\romfs\Pack\ZsDic.pack.zs
[hos ARes Loading 0] fs: OpenFile(content:/Pack/ZsDic.pack.zs): from the overlay
```

Not checked: a Linux link or run (no Linux toolchain here: WSL's Ubuntu has no compiler; the syntax check above
is against real glibc headers with the `host/posix` shim); a folder listing with mod-only entries in game (the
code is Skybound's unchanged; the game's `OpenDirectory` calls in the boot logged `0 entries from mods`, as
expected with no mod-only entries).

Found on the way (posted to `cs-r1`): the game opens
`System/Resource/ResourceSizeTable.Product.111.Nin_Ounce_NVN2.rsizetable.zs` early at boot, then the
`RSDB/*.Product.111.rstbl.byml.zs` tables. The resource size table for track A item 6 is that `System/Resource` file.

## Incident

Boot 1 started while Kareem's game ran (`E:\Games\Hookshot\hookshot.exe`, pid 18680, started 15:14): my boot
helper printed `tasklist` but did not stop on it. The test build ran 20 s headless from
`E:/OOTRemake/work/buildtest-mods/game` and was stopped by its own pid; Kareem's process was not touched. Later
boots are gated on `tasklist` showing no `hookshot.exe`.

The build (`make_game.py`) compiles in `%LOCALAPPDATA%\HookshotBuilder\sa` (its fixed work folder), so the objects
and `hookshot.exe` there are now this branch's build. The game folder `E:\Games\Hookshot` was not touched.

## In-game check for Kareem

Not needed for this branch (boot 2 shows a boot file served from a mod). Once it is merged and built by Hookshot
Builder: put a copy of any RomFS file at `<game folder>\mods\test\romfs\<same path>` (for example
`Pack\ZsDic.pack.zs`) and start the game from its icon; `hookshot_log.txt` should show `mods: test: 1 RomFS files`
and `mods: Pack/ZsDic.pack.zs <- ...\mods\test\romfs\Pack\ZsDic.pack.zs`, and the game plays as before. Delete
`mods\test` afterwards.

## Questions

- **exefs patches: worth a follow-up?** It would need `nx2/make_game.py` to put the module map beside `image.bin`
  (or `nx2/standalone.py` to put it in `hos_image.c`) for data patches, and a lift option for code patches. Nothing
  Clawshot plans needs them; provisional answer: no.

## Left

- Claude: review `8171cfb`, open the upstream PR from the fork.
- `E:/OOTRemake/work/buildtest-mods/` is kept for review (tools copy with four junctions into the builder, the game
  folder whose `romfs` is hard links to the dump, logs `make_game.log`, `run1.log`..`run3.log`). To delete it, first
  remove the junctions `tools/emsdk`, `tools/cpm`, `tools/python`, `tools/wgpu-native` with
  `[System.IO.Directory]::Delete(<path>, $false)`, then the folder. `E:/OOTRemake/work/r1-hookshot-mods/` holds
  Skybound's `mods.c` and the Linux header sysroot.
