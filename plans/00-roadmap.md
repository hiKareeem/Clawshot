# Roadmap

Priority (Kareem, 2026-11-07): a stable solo randomizer first. Archipelago waits until seeds are solid.

## Milestones

| | What | Done when |
|---|---|---|
| **M0** | formats and the day-1 risk check | every placement file round-trips; a swapped chest gives its new item in game |
| **M1** | check census | every check in the game has a stable ID and its vanilla item; differences from OoT Randomizer's list are written down |
| **M2** | first playable seeds | chest shuffle with logic, spoiler log, settings string; Kareem and his co-owner finish a seed |
| **M3** | the rest of the shuffle | NPC and song gifts, shops, scrubs, Skulltula tokens, item-get text, Gossip Stone hints |
| **M4** | code features | a hook API in Hookshot upstream; progressive items, arbitrary item models, entrance shuffle |
| Later | Archipelago world and client; settings GUI; race seeds | |

Day-1 numbers from the spike (raw placements, not deduplicated): 267 chests in 72 files; 41 without a drop
parameter; major items found in chests include the Hookshot, Longshot, Megaton Hammer, Bow, Slingshot, Boomerang,
Iron and Hover Boots, Lens of Truth, Kokiri Sword, Mirror Shield, Ice Arrows and both gauntlets.

## Round 1 (M0, with M1 research and the Hookshot mod loader alongside)

Three tracks, launched together. Bermuda thread `cs-r1`. Each track writes `plans/rounds/r1-<track>.md`.

### Track A: formats and the chest swap (`r1/formats`)

Owns `pyproject.toml`, `uv.lock`, `src/clawshot/`, `tests/`, `plans/rounds/r1-formats.md`.

1. uv project (`clawshot`, Python 3.12+), `src/` layout, ruff, pytest with a `dump` marker that skips when
   `OOT_ROMFS` is unset. Test: `uv run pytest` passes with and without `OOT_ROMFS`.
2. `clawshot.formats.zsdic`: open `Pack/ZsDic.pack.zs` (plain zstd around a SARC holding `zs.zsdic`,
   `bcett.byml.zsdic`, `pack.zsdic`, `bkprb.zsdic`); decompress and compress a `.zs` file with the dictionary its
   name calls for. Test: a synthetic round-trip; under `-m dump`, every `Banc/**/*.bcett.byml.zs` decompresses.
3. `clawshot.formats.byml`: BYML v7 little-endian reader and writer. Start from the reader in
   `E:/OOTRemake/work/spike_banc.py` (node types seen: 0xC0 array, 0xC1 map, 0xA0 string, 0xD0 bool, 0xD1 int,
   0xD2 float, 0xD3 uint, 0xD5 u64; hash maps 0x20/0x21 read but not yet seen). Keep the node types exact (a
   float stays a float, a u64 stays a u64). Tests: synthetic fixtures for every node type, built in code.
4. Round trip under `-m dump`: all 160 `Banc/**/*.bcett.byml.zs` files read, write and read back to the same
   tree; report how many are byte-identical after decompression, and for the rest, the first difference.
5. `python -m clawshot.tools.swap_chest --romfs <dir> --out <dir> --file <Banc path> --hash <actor Hash>
   --item <actor name>`: writes the changed file to `<out>/romfs/<same relative path>`, compressed with the
   same dictionary. Pick two chests in `Banc/KokiriForest/` reachable in the first minutes of a new game and
   write two outputs: one chest with another rupee (`TBox_Rupee_Red`), one with a major item it never held
   (`Item_Boomerang`). Explain how you identified each chest (position, nearby actors) so Kareem can find it.
6. Write into your round file: the decompressed and compressed sizes of each changed file against the original,
   and whether `RSDB/` holds a size entry for that file (Tears of the Kingdom's resource size table needed one
   when a file grew). Don't change RSDB yet; say what you found.

The in-game check is Kareem's: Claude sets `HOS_FS_OVERLAY` and asks him to open both chests.

### Track B: game-data research (`r1/research`)

Owns `plans/03-game-data.md` and `plans/rounds/r1-research.md`; scratch scripts and decoded data stay in
`E:/OOTRemake/work/r1-research/` (outside the repo). Use the spike reader in `E:/OOTRemake/work/spike_banc.py`
until track A's package lands. Findings go into `plans/03-game-data.md` as prose and tables of identifiers,
names and counts, never file contents.

Answer, each with how you found it:

1. Chests deduplicated across `Child`/`Adult` and `Static`/`Dynamic` files by actor `Hash`: count per area.
2. The 41 chest placements without `Dynamic.Drop__DropActor`: where their contents come from.
3. What `Dynamic.GetEventName` refers to, and whether a changed chest item needs a different event.
4. NPC gifts, songs and other event item-gets: how `Event/EventFlow/*.bfevfl.zs` grants an item (the action
   names and parameters), with three worked examples.
5. Freestanding items (Heart Pieces and the like), Gold Skulltulas, shops, Business Scrubs, cows, Great Fairies:
   their actor names and where they are placed.
6. How the game records that a check was collected (`GameData/GameDataList`): the flag naming, and whether a
   chest's opened flag is keyed by its `Hash`.
7. `RSDB`: which tables exist, and whether placement files have size entries.
8. What `Banc/DreamWorld` (54 files) is.
9. OoT Randomizer's location list (MIT; `https://github.com/OoTRandomizer/OoT-Randomizer`, `LocationList.py`):
   count of checks per area there vs here so far; list N64-only and remake-only checks you can identify.

### Track C: Hookshot `mods` folder (Hookshot fork, branch `mods-folder`)

Worktree `E:/OOTRemake/hookshot-r1/mods`, based on `upstream/main` of `NotRexed/Hookshot`. Owns `host/mods.c`
(new), `host/mkw_glue.c` (the stubs only), and anything the port needs in `nx2/build.py`. Writes its round file
to `E:/OOTRemake/Clawshot/plans/rounds/r1-hookshot-mods.md` (only that file in the Clawshot repo, uncommitted;
Claude commits it).

Hookshot already calls `hos_mods_init`, `hos_mods_romfs` and `hos_mods_dir_extras` (`host/hos_main.c`,
`host/nn_fs.c`) and stubs them in `host/mkw_glue.c`. The same author's Tears of the Kingdom port has the real
loader: `a64-kit/hos/mods.c` in `NotRexed/SkyboundTotk` (MIT), with the emulator layout (`mods/<name>/romfs`,
`exefs/*.pchtxt`, `exefs/*.ips`, `HOS_MODS=<dir>`, `-`/`_` prefixes off, last-sorted wins).

1. Port its RomFS part to Hookshot and remove the three stubs. Keep `HOS_FS_OVERLAY` working.
2. Port the exefs data patches if they fit Hookshot's image loading as they are; otherwise leave them out and
   say why.
3. Keep the Linux build compiling (`host/posix` provides `windows.h`); say what you could not check.
4. Check with a real build, following "Verify a source change with a real build" (below), into
   `E:/OOTRemake/work/buildtest-mods/`: a mod that replaces a file the game reads at boot with a byte-identical
   copy, and the log line that shows it came from the mod. Boot only headless and muted
   (`HOS_HEADLESS=1 HOS_AUDIO=0`, at most 20 s), only after `tasklist` shows no `hookshot.exe`, and never in
   `E:/Games/Hookshot`.
5. Commits follow Hookshot's convention: title, a body that explains why, and the trailers
   `Assisted-by: Claude Opus 5.5` and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Credit
   SkyboundTotk's `mods.c` in the body. Don't push; Claude reviews and opens the PR.

**Verify a source change with a real build.** Mirror the builder's layout in `<test>/tools`: copy
`host gpu nx2 scripts third_party LICENSE readme.md assets` from the worktree; copy from the release builder
(`E:/Games/Hookshot/HookshotBuilder/tools`) the prebuilts the repo lacks (`third_party/zbic/zbic.dll`,
`zbic.lib`, `third_party/sdl2/*`, `third_party/a64-kit/tools/lld-link.exe`,
`third_party/a64-kit/lift/a64emit.dll`, `a64emit.dll.sha1`, `a64emit.lib`) and its `work/` folder; make
directory junctions for `emsdk cpm python wgpu-native` to the builder's (PowerShell `New-Item -ItemType Junction`).
Then, from `<test>/tools`, with `EMSDK`, `RX_CPM`, `WGPU_NATIVE` set to those junctions:
`python/python.exe -I nx2/make_game.py --romfs E:/Games/Hookshot/romfs --exefs E:/Games/Hookshot/.hookshot_exefs
--out <test>/game --language en-US` (romfs is hard-linked, about 6 minutes). Read the game's log from
`2> <file>`, never `/dev/null`. Stop it with `taskkill /IM hookshot.exe /F` only if it is your own. When you
delete the test folder, remove the junctions first with `[System.IO.Directory]::Delete(<path>, $false)`:
deleting through a junction deletes the builder's files.

### After round 1

Claude reviews each track, runs the gates on `main`, asks Kareem for the chest check, opens the Hookshot PR, and
writes round 2 from track B's findings: M1 census (`census/`), the formats M1 needs (EVFL for event flows, MSBT
for text, the resource size table), and the world format with OoT Randomizer's region graph ported (`world/`).
