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
7. (Added mid-round, from track B.) Big-endian BYML: `GameData/GameDataList.Product.110.byml.zs` is BYML v7 with
   the `BY` magic, and the census needs it (chest-opened flags are `Bool64bitKey` entries keyed by the actor
   `Hash`). Read and write both byte orders, writing a file back in the order it was read; synthetic tests for
   both; a dump test that GameDataList round-trips (tree equal; byte-identical or not, stated in the round file).

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

**Round 1 result (2026-11-07):** M0 passed in game (`03-game-data.md` section 10): both chest directions work with
the right text; a story override (`Get_StoneOfForest_GetSword`) still grants its vanilla item, so story overrides
must be replaced in the patch plan. Tracks A and B merged; track C (Hookshot mods folder) still running.

## Round 2 (M1 census and the generator's engine)

Two tracks, launched while round 1 track C finishes. Bermuda thread `cs-r2`. Each track writes
`plans/rounds/r2-<track>.md`. Read `plans/03-game-data.md` first: it is the map of the data.

### Track A: census (`r2/census`)

Owns `src/clawshot/census/`, `src/clawshot/data/locations.toml`, `tests/test_census*.py`,
`plans/rounds/r2-census.md`. Uses `clawshot.formats` (byml, zsdic) as it is on `main`; if it needs a change there,
post on the thread.

1. `clawshot.census.scan(romfs) -> list[Location]`: every placement check in the game. A `Location` has `id` (the
   actor `Hash`), `kind` (`chest`, `treasure_game_box`, `gold_skulltula`, `freestanding` (heart pieces, small
   keys), `heart_container`, `scrub`, `shop_slot`), `area` (Banc folder), `room` where the data has one, `files`
   (every placement file holding that `Hash`), `ages` (child, adult or both), `position`, `vanilla_item` (actor
   name), `event` (`GetEventName` override or none) and `has_save_flag` (a `Bool64bitKey` with that `Hash` in
   `GameDataList`). Excluded by decision: trap chests, pedestals, `DreamWorld`, cows (D10-D12). Event gifts are not
   in this round (they need EVFL).
2. `src/clawshot/data/locations.toml`: the committed definitions (D5): `id`, `kind`, `area`, `name` (a readable,
   unique name), `vanilla_item`, and `oot_randomizer_name` where one N64 check is the same check (OoT Randomizer
   `LocationList.py`, MIT, cite the commit). Match by area, kind, vanilla item and room/order; leave
   `oot_randomizer_name` empty where unsure and list those in the round file. A tool writes the file from the dump;
   names may be edited by hand afterwards. A `dump` test checks the file and `scan()` agree (same IDs, kinds,
   vanilla items).
3. Counts in the round file per kind and area, against `03-game-data.md`; OoT Randomizer checks with no match here,
   and checks here with no match there.
4. In-game test outputs for Kareem, outside the repo (`E:/OOTRemake/work/r2-census/`), one mod folder each, with
   where to go and what he should see, for a new game:
   - **Freestanding item:** a freestanding Heart Piece reachable early by child Link, with its actor (`Gyaml`)
     changed to another pickup. Make two variants: a rupee pickup the game already places in the world, and a
     major item (find which actor, if any, the game uses for a major item lying in the world; say what you found).
     Its `Hash`, and so its save flag, stays.
   - **Story override removed:** the Kokiri Sword chest holding `TBox_Rupee_Red` with its `GetEventName` removed,
     so the default open event plays. Note in the round file what story state `Get_StoneOfForest_GetSword` sets
     (from the research's event-flow notes), since a seed must still set it.

### Track B: world engine (`r2/world`)

Owns `src/clawshot/world/`, `src/clawshot/generate/`, `src/clawshot/data/world/`, `tests/test_world*.py`,
`tests/test_generate*.py`, `plans/04-world-format.md`, `plans/rounds/r2-world.md`, and `NOTICE` (for OoT Randomizer
credits).

1. `plans/04-world-format.md` and its loader: regions, exits, locations and events in data files, with requirements
   in a small rule language (items and counts, age, time of day, events, helper rules defined in data). Pick the
   rule syntax so OoT Randomizer's region JSON (`data/World/*.json`, MIT) translates mechanically; write the
   translation tool rather than translating by hand.
2. Reachability: from a start state, the regions and locations reachable for each age, with age changes through
   the Temple of Time as an event.
3. The fill: OoT Randomizer's assumed fill (restricted items first, then progression, then the rest), seeded with
   `random.Random(seed)`, and the beatability search (`01-architecture.md`) run on every seed. Spoiler log as JSON
   (seed, settings, placements, the sphere order). Determinism test: same seed and settings give the same bytes.
4. Tests on synthetic worlds built in the tests (no game data): a world that is beatable, one that is not, key
   doors, an item reachable only as adult, every seed of 200 beatable.
5. Port OoT Randomizer's regions for Kokiri Forest, the Lost Woods and the Deku Tree with the tool from item 1
   (credit the files and commit in `NOTICE`). Locations stay under their OoT Randomizer names; track A's
   `oot_randomizer_name` links them to the remake's IDs. After track A's `locations.toml` is on `main` (Claude
   will tell you): a test that every OoT Randomizer location in the ported regions either has a remake ID or is
   listed as N64-only in `03-game-data.md`.

### After round 2

Kareem runs track A's in-game outputs. Round 3: EVFL, MSBT and the resource size table (formats), event gifts in
the census, the rest of the world port with the remake's Gold Skulltula positions and key counts, and the patch
plan (what changes in which file per placement, story overrides replaced).
