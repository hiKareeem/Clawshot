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

**Round 2 result (2026-11-07):** in game, the chest without its story event gave its rupee with no sword or
cutscene; freestanding heart pieces became red rupees (Kakariko seen, Lon Lon picked up); Fire Arrows as a
freestanding pickup crashed three times out of three (`03-game-data.md` section 10). Census (477 checks), save
reader and world engine (Kokiri Forest, Lost Woods, Deku Tree) are on `main`.

## Round 3 (M2's first playable mini-seed)

Three tracks. Bermuda thread `cs-r3`. Each track writes `plans/rounds/r3-<track>.md`. Read `03-game-data.md`
(sections 9 and 10 are new) and `decisions.md` (D15-D17) first.

### Track A: seed output (`r3/seed`)

Owns `src/clawshot/patch/`, `src/clawshot/data/item_actors.toml`, `src/clawshot/__main__.py`,
`src/clawshot/generate/` (extending what is there), `tests/test_patch*.py`, `tests/test_seed*.py`,
`plans/rounds/r3-seed.md`. Consumes `census` and `world` as they are on `main`; changes there go through the
thread.

1. `item_actors.toml`: for every item the fill can place in the first seeds (fixed items, D16), the remake actor a
   chest's `Drop__DropActor` takes (e.g. `Kokiri Sword` -> `Item_Sword_Kokiri`, `Rupees (5)` -> `TBox_Rupee_Blue`,
   the Deku Tree's map and compass). Derive the pairs from linked locations (census `vanilla_item` against OoT
   Randomizer's vanilla item for the same `oot_randomizer_name`) and check each actor exists in `Pack/Actor`. A
   test fails for any placeable item with no actor.
2. The patch plan: from a seed's placements, per location, every file and actor `Hash` to change (all copies:
   child and adult, `Static`/`Dynamic`, `Alternative`; census `files`), the new `Drop__DropActor`, and story
   overrides removed (`GetEventName`, as round 2 showed works). The plan lists, per removed override, the story
   state it set (`03-game-data.md` and `r2-census.md` have the Kokiri Sword's); where a seed must restore it, say
   how (event flow or flag) and leave it as a finding if no data path exists yet.
3. The writer: `python -m clawshot --romfs <dump> --seed <n> --out <dir>` writes `<dir>/romfs/...` (changed files
   only, through `formats`) and `<dir>/spoiler.json`; chests only (D15); the Treasure Chest Game boxes stay
   vanilla (D17). A `dump` test reads every written file back and checks it differs from the original only where
   the plan says (field-level diff, as `E:/OOTRemake/work/r1-test/check_mod.py` does) and prints each file's size
   change.
4. Output for Kareem, outside the repo: three seeds of the Kokiri Forest / Lost Woods / Deku Tree slice in
   `E:/OOTRemake/work/r3-seed/seed-<n>/`, each with its spoiler log, and a short play note per seed (where the
   Kokiri Sword and Slingshot are). These are played from a new game, so note what a player needs to reach the Deku
   Tree (Mido's check).

### Track B: census and formats (`r3/census`)

Owns `src/clawshot/census/`, `src/clawshot/data/locations.toml`, `src/clawshot/formats/rstb.py` (new),
`tests/test_census*.py`, `tests/test_rstb*.py`, `plans/rounds/r3-census.md`, and a new section 11 of
`plans/03-game-data.md`.

1. Gold Skulltulas: link the 97 that keep their N64 checks to their OoT Randomizer names (area, room, position
   and the guide facts in `03-game-data.md` section 9; the guides' text is in `E:/OOTRemake/work/r3/`, local
   only). Mark the 3 gone ones for track C (post their OoT Randomizer names) and give the 3 new ones readable
   names. List what you could not link and why.
2. The Treasure Chest Game reward chest: a field or kind that lets the generator shuffle it while the 11 game boxes
   stay vanilla (D17). Post what you chose.
3. `formats/rstb`: read and write the resource size table (`System/Resource/ResourceSizeTable.Product.111.
   Nin_Ounce_NVN2.rsizetable.zs`, round 1 track C found the game opens it), with a function giving the entry a
   changed file needs (the formula in `03-game-data.md`; check it against the table for every Banc file and report
   any that don't fit). Synthetic tests and a `dump` round-trip test. Post when it is on your branch: track A uses
   it.
4. Freestanding major items: find an actor that can show a major item lying in the world without the crash round
   2 hit with `Obj_Arrow_Fire` (section 10): compare its actor pack and placement (its `AiGroups` logic module)
   with `Obj_Rupee_Red` and the other `Obj_` pickups; then make test mod folders (outside the repo,
   `E:/OOTRemake/work/r3-census/`) for the Lon Lon Ranch tower heart piece, which Kareem has a save right before
   (`E:/OOTRemake/work/save-backups/2026-11-07_llr-tower-before-pickup`). Also say whether a red rupee placed
   over a heart piece saves a flag (the save reader on his copies: section 10 says neither Hash was set after the
   pickup).

### Track C: world port (`r3/world`)

Owns `src/clawshot/world/`, `src/clawshot/data/world/`, `tests/test_world*.py`, `plans/04-world-format.md`,
`plans/rounds/r3-world.md`, `NOTICE`.

1. Port the rest of OoT Randomizer's world (overworld and every dungeon, vanilla dungeon layouts) with the
   translator; credit the files in `NOTICE`.
2. The remake's differences, as overrides kept apart from the translated files (round 2's finding): the
   requirement changes and N64-only checks in `03-game-data.md` sections 5 and 9 (Gold Skulltulas that need the
   Megaton Hammer or the Hookshot now, the swapped Great Fairies, the gone Gold Skulltulas once track B posts
   them), and each dungeon's key count and key locations from the census (the Water Temple has 4 keys in chests
   against OoT Randomizer's 6). List each override with its source.
3. The vanilla placement is beatable (the beatability search on the vanilla world), and 200 seeds with the
   default settings are beatable, as tests.
4. Every OoT Randomizer location of a type the census covers either has a remake ID or an `n64_only` reason (the
   round 2 test, now over the whole world); the pending list it prints goes in the round file.

### After round 3

Kareem plays track A's mini-seeds and track B's freestanding test. Round 4: the whole-game seed (track A's writer
over track C's world), event gifts (EVFL), and the size table written by the patch.

**Round 3 result (2026-11-07):** census, size table, world port and seed writer merged. In game: freestanding Hylian
and Deku Shields work (`03-game-data.md` section 11). Seed 3 was **not beatable**: the Slingshot was in the Deku Tree
basement chest, and in the remake the Slingshot is needed to leave the Slingshot room and to climb to the top floor
(from where the basement opens), which OoT Randomizer's N64 logic doesn't require. OoT Randomizer's dungeon logic
can't be trusted for the remake until each area is checked against the remake.

## Round 4 (remake logic, fast start, event flows)

Four tracks. Bermuda thread `cs-r4`. Tracks run in herdr-core (`hc`), not old herdr panes. Each track writes
`plans/rounds/r4-<track>.md`.

### Track A: remake logic, child areas (`r4/logic-child`)

Owns `src/clawshot/world/load.py` (item 1 only), `src/clawshot/data/world/remake.toml`,
`src/clawshot/data/world/remake/` (new), `tests/test_world_remake*.py`, `plans/rounds/r4-logic-child.md`, and
section 12 of `plans/03-game-data.md` (child areas).

1. First, small, its own commit, posted: the loader also reads every `src/clawshot/data/world/remake/*.toml` after
   `remake.toml` (sorted by name; a location or exit set in two files is an error), so the two logic tracks write
   separate files. Claude merges it early.
2. Deku Tree, from seed 3: the Slingshot is needed to leave the Slingshot room and to reach the top floor. Model it
   (overrides with `source`), add a test that a Slingshot in the basement chest is not beatable, and say in the
   round file how a player who enters the Slingshot room without it gets out (Kareem is asked whether reloading
   puts him at the dungeon entrance); if he can't, the room must not be a trap: propose the rule.
3. Then every child-reachable area: Kokiri Forest, Lost Woods, Sacred Forest Meadow, Hyrule Field, Lon Lon Ranch,
   Market, Hyrule Castle, Kakariko, Graveyard, Death Mountain Trail and Crater (child side), Goron City, Zora's
   River, Domain and Fountain, Lake Hylia, and the dungeons Deku Tree, Dodongo's Cavern, Jabu-Jabu's Belly, Bottom
   of the Well, Ice Cavern. For each OoT Randomizer rule, check it against the remake: published remake
   walkthroughs and guides (cite each URL; facts only, no copied text), the census and `03-game-data.md`, and the
   placement data where it settles a question (a target, ladder, block or door in the Banc files). Write overrides
   in `src/clawshot/data/world/remake/child_<area>.toml`, each with `source`.
4. The round file lists per area: rules checked and unchanged, rules changed (with source), and what could not be
   settled from sources (a question for an in-game check, in **bold**).
5. Remake the three mini-seeds (`E:/OOTRemake/work/r4-seed/seed-<n>/`, the round 3 command with the new logic) once
   item 2 is in, with play notes, and check each is beatable under the new rules.

### Track B: remake logic, adult areas (`r4/logic-adult`)

Owns `src/clawshot/data/world/remake/adult_*.toml`, `tests/test_world_remake_adult*.py`,
`plans/rounds/r4-logic-adult.md`, and section 13 of `plans/03-game-data.md` (adult areas).

Track A's item 3 for the adult side: the Forest, Fire, Water, Shadow and Spirit Temples, Gerudo Training Ground,
Ganon's Castle and Tower, Gerudo Valley and Fortress, the Haunted Wasteland, Desert Colossus, Death Mountain
Crater (adult side), and adult-only rules in the shared overworld areas. Same sources, same output, files named
`adult_<area>.toml`. Until track A's loader change is on main, test with it applied locally; don't commit it.
The Water Temple's key count already differs (`03-game-data.md`).

### Track C: fast start (`r4/fast-start`)

Owns `src/clawshot/patch/gamedata.py` (new), `src/clawshot/data/fast_start.toml` (new), `tests/test_fast_start*.py`,
`plans/rounds/r4-fast-start.md`, and section 14 of `plans/03-game-data.md`.

1. What a new game sets and plays before the player has control: the initial values in
   `GameData/GameDataList.Product.110.byml.zs` (big-endian BYML, read and written by `formats.byml`), the event
   flows that run (`HavePlayedEvent.*` flags), and which flags gate the opening cutscenes (the intro, Navi waking
   Link, the Deku Tree's talk, Mido's block, Zelda's courtyard, Kaepora Gaebora). The save reader on Kareem's save
   copies shows which flags a played game has set.
2. A patch that changes `GameDataList`'s initial values so a new game skips the intro (and, as separate settings,
   the other cutscenes found, each named in `fast_start.toml` with what it skips and what state it must still set).
   Default: skip the intro only. A dump test that the written file differs only in the chosen entries.
3. Test outputs for Kareem, outside the repo (`E:/OOTRemake/work/r4-fast-start/`): skip the intro alone, and the
   intro plus the others found, each with what he should see on a new game.

### Track D: event flows and gifts (`r4/evfl`)

Owns `src/clawshot/formats/evfl.py` (new), `src/clawshot/census/` (gifts), `src/clawshot/data/locations.toml`,
`tests/test_evfl*.py`, `tests/test_census*.py`, `plans/rounds/r4-evfl.md`, and section 15 of `plans/03-game-data.md`.

1. `formats/evfl`: read and write `.bfevfl` event flows (our own implementation from the format; no code from the
   GPL evfl library, which round 1's scripts used: don't read its source). Round-trip every flow in the dump
   byte-identical or tree-equal (say which), in a `dump` test.
2. The census of gifts: every flow step that gives an item by name (round 1 found the pattern; `03-game-data.md`
   section 3), as locations of kind `npc_gift`, `song`, `event_gift` with the flow, entry and step, the vanilla
   item and the OoT Randomizer name where it is the same check. Count them against OoT Randomizer's NPC, song and
   cutscene checks.
3. How a gift's item would be changed in the flow (the step's item name, the text it shows), as a finding with one
   example written to `E:/OOTRemake/work/r4-evfl/` for a later in-game test; no seed writes flows yet.

### After round 4

Kareem tests the mini-seeds on the corrected Deku Tree logic and the fast-start outputs. Round 5: whole-game
chest seeds over the checked logic, gifts through the flows, and in-game checks for the logic questions.

Engine questions from track B for round 5 (`plans/rounds/r4-logic-adult.md`): (1) the Forest Temple walkthrough
says the remake lets adult Link return to child only after the Forest Temple; the search shares one inventory
across ages and can't tell an adult-found item used as child before that, so it needs an age-travel model, not a
data gate; (2) Great Fairies: settled from the data by track A's item 6 (`03-game-data.md` section 12): Din's
Fire opens the other five, fees are fixed per fairy, wallets hold 200/500/1000, every magic item carries the
magic meter. The adult rules keep conservative routes where the remake is
unproven (stricter than the game, never looser); their in-game questions are in bold in the round file.

**Round 4 result (2026-11-08):** all four tracks merged (`main` 7a46b04; 297 tests, 25 dump tests). Every child
and adult area checked against the remake (track A 125 changed rules over 21 child areas plus the Deku Tree; track
B the adult areas and temples, the phantom Fire Temple key removed); fast start passed in game (D18); EVFL
reader/writer and the gift census (148 gift steps). About 85 logic questions only play can answer, kept with
stricter rules until then. Round 5 (Kareem agreed, 2026-11-08): the age-travel model, Deku Shield and shops
(D19), whole-game chest seeds, gifts through the flows, an organised in-game logic session; most tracks on
`openai-codex/gpt-6.1-sol`, Opus for one track and for review.

## Round 5 (M2 whole-game chest seeds; M3 shops and gifts begin)

Five tracks. Bermuda thread `cs-r5`. Tracks run in herdr-core (`hc`). Each track writes `plans/rounds/r5-<track>.md`.
New sections of `plans/03-game-data.md`: 16 (track A), 17 (track B), 18 (track C), 19 (track D); each track appends
only its own section, after the last one on `main` when it rebases. No Hookshot build this round.

Shared files: `src/clawshot/data/locations.toml` is written by `python -m clawshot.census.write_locations`; tracks C
and D may both change it (C chest names, D gift entries). On a rebase conflict there, rerun the writer on the
rebased tree instead of hand-merging. `src/clawshot/patch/__init__.py` and `src/clawshot/__main__.py` are track C's;
tracks B and D wire their kind into a seed in their own last commit, after Claude says track C's item 1 is on
`main` (one call in `make_seed`, one `--shuffle` value), so the merge conflict is a few lines. A change a track
needs in another track's file: post it on the thread; if it is small, make it as its own commit that touches only
that, and say so in the post.

### Track A: age travel (`r5/age`)

Owns `src/clawshot/world/search.py`, `src/clawshot/world/model.py`, `tests/test_world_search*.py`,
`tests/test_age*.py`, `plans/rounds/r5-age.md`, and section 16.

1. Settle from the data and sources when the remake lets Link change age: what the first Master Sword pull needs
   (spiritual stones, the Ocarina of Time, the Song of Time, the Door of Time), and when adult Link can put the sword
   back. Round 4's track B read a walkthrough saying only after the Forest Temple. Look at the Temple of Time and
   Master Sword event flows (`clawshot.formats.evfl`), the flags they ask (`GameDataList`), and the save reader on
   Kareem's save backups (all still child-era on 2026-11-08; he is playing to adult Link now, and a save taken after
   the first pull will follow). Cite the flow, entry and flag.
2. If returning is gated, model it in the search: an item found as adult before the gate opens is not usable as
   child until the gate opens. Tests: a seed that needs an adult-found item as child before the gate is not
   beatable; the same after the gate is.
3. The softlock this creates: a player who pulls the sword early can be stuck as adult if the gate needs something
   only a child can get. Propose a rule in the round file (for example: everything adult needs to open the gate is
   reachable as adult with what a child can collect before the first pull, or a setting below), with its test.
4. If one flag opens the return (a `GameDataList` default like round 4's fast start), write it as a setting in
   `src/clawshot/data/fast_start.toml` (`free_time_travel`, off) and its dump test; with it on, the search treats
   age changes as free, as OoT Randomizer does. Kareem decides the default.

### Track B: Deku Shield and shops (`r5/shops`)

Owns `src/clawshot/patch/shops.py` (new), `src/clawshot/data/shops.toml` (new), `tests/test_shop*.py`,
`plans/rounds/r5-shops.md`, and section 17. D19: the Deku Shield and shop contents are shuffled.

1. Every shop in the data: its slots (the 128 `shop_slot` census entries), what decides each slot's item, price, text
   and stock (actor parameters, `RSDB` rows, the shop's event flow), how buying gives the item, and the Kokiri
   shopkeeper's Deku Shield entry (`Npc_*_Shop_*`, section 15) and the tutorial after buying the shield. Wallet sizes
   are section 12's (200/500/1000). Write it as `shops.toml` (each shop and slot: Banc, Hash, vanilla item, price)
   with a dump test that reads every slot.
2. How one slot is changed to sell another item: the display object, the item given, the price, the name and
   description text; which items have a shop display object and which don't. Two test outputs outside the repo
   (`E:/OOTRemake/work/r5-shops/`): the Kokiri shop's Deku Shield slot selling another item (one with a display
   object), and the Deku Shield in a Kokiri Forest chest (the chest actor exists: `item_actors.toml`), each with what
   Kareem should see, including whether the shield's tutorial plays for the other item.
3. The shield in the logic: with shops vanilla, the Deku Shield is bought (as now); with `--shuffle Shop`, the Kokiri
   shield slot is a location and the shield is in the pool, so Mido's rule (sword and shield) puts it before him and
   the Mido skip lets it go anywhere. Prices as wallet requirements. Tests for both.
4. Last, after Claude's word: wire `--shuffle Shop` into `make_seed` (one commit).

### Track C: whole-game chest seeds (`r5/seeds`)

Owns `src/clawshot/generate/`, `src/clawshot/patch/{__init__,plan,write,items,events}.py`,
`src/clawshot/patch/chest_events.toml`, `src/clawshot/data/item_actors.toml`, `src/clawshot/__main__.py`,
`tests/test_generate*.py`, `tests/test_patch*.py`, `plans/rounds/r5-seeds.md`, and section 18.

1. First, small, its own commit, posted: `make_seed` takes a list of extra patch steps (a callable per kind:
   placements in, file changes out) so tracks B and D add theirs without touching the chest code. Claude merges it
   early.
2. Every chest a location: 119 census chests have no OoT Randomizer name (the remake's extra chests, D12:
   shuffled, Business Seeds filler; Dream World out). Give each a world location in its region (in
   `src/clawshot/data/world/remake/extra_<area>.toml`, new files; the loader reads them), with the rule to reach it
   and its source, or a reason it stays out. A test that every chest is a location or listed as excluded.
3. Chest events: for every chest whose `GetEventName` the patch removes (the Kokiri Sword's, others in
   `chest_events.toml`), what story state the event set (flags, quest steps) and the patch's way to set it anyway;
   a dump test per event.
4. Fast start in seeds: the seed's `GameDataList` gets the fast-start settings (D18: the intro skip by default, the
   others as settings), and the Mido skip removes Mido's requirement from the logic (OoT Randomizer's `open_forest`
   covers Mido and the forest exit together; the remake's exit gate is separate: check what the skip changes).
5. Three whole-game chest seeds for Kareem (`E:/OOTRemake/work/r5-seed/seed-<n>/`, launchers copied from
   `E:/OOTRemake/work/r3-seed/`, never run), each beatable, with its spoiler and a short note of the route the search
   found. Check every written file against the size table. After track A's model is on `main`, Claude asks for them
   to be made again.

### Track D: gifts through the flows (`r5/gifts`, Opus)

Owns `src/clawshot/patch/gifts.py` (new), `src/clawshot/census/gifts.py`, `src/clawshot/formats/evfl.py`,
`tests/test_gift*.py`, `tests/test_evfl*.py`, `plans/rounds/r5-gifts.md`, and section 19.

1. For every gift step in the census (148): what else in the flows reads the vanilla item (an `IsGet.<item>` used
   as "already given", or as a gate elsewhere: the Great Fairies use `IsGet.Item_DinFire` both ways, section 12), and
   the flag to use instead so the check gives its item once and gates stay as the logic models them. Class each
   gift: item swap only; swap plus flag rewrite; needs more (songs' play-along, cutscenes). A table in section 19.
2. `patch/gifts.py`: change a gift step's item (and the flag rewrites) for the first two classes, with dump tests
   that each changed flow round-trips and differs only in the intended steps.
3. Test outputs outside the repo (`E:/OOTRemake/work/r5-gifts/`): round 4's Talon test, plus three early-game gifts
   (a child NPC gift, a Great Fairy, one song if any is in class one or two), each with what Kareem should see and
   which save to start from (`E:/OOTRemake/work/save-backups/`, read with `clawshot.save`; a new game is fine).
4. Last, after Claude's word: wire `--shuffle Gift` into `make_seed` for the gifts that passed review (one commit).

### Track E: the in-game logic session (`r5/playtest`)

Owns `plans/playtest/` (new) and `plans/rounds/r5-playtest.md`; no code.

1. Every question for an in-game check in the round files (`plans/rounds/r*-*.md`, the **bold** ones) and in
   `03-game-data.md`, deduplicated: what to do, where, at which age and progress, what to watch, and what each
   answer changes (the rule file and key, or the fact to record).
2. A route: `plans/playtest/session-<n>.md`, the questions in the order a player meets them, grouped so one sitting
   covers an area. Kareem's saves (`E:/OOTRemake/work/save-backups/`, read with `clawshot.save`) say what his
   main game can reach now; questions that need later progress go in a later session.
3. Where a mod makes a question cheaper (an item placed where the question needs it), prepare it outside the repo
   (`E:/OOTRemake/work/r5-playtest/`) with a launcher copied from `E:/OOTRemake/work/r2-test/`, never run.
4. `plans/playtest/answers.md`: one line per question for Claude to fill in after the session.

### After round 5

**Round 5 result (2026-11-08):** all five tracks merged (`main` 6f7cbf0; 381 tests, 46 dump tests).
- A, age travel: the remake keeps adult Link adult until the Forest sage (`SageOfForest_IsCompleted_Exp` gates the
  pedestal); the search is chronological; `age_return_guarantee` on by default (D20, Kareem) and built into the fill;
  `free_time_travel` (a pedestal patch, off) waits for its in-game test after Kareem's first pull.
- B, shops: all 128 shelves traced; `--shuffle Shop` with native-display items only (D21); in game the slot swap
  and a chest Deku Shield work, a stand-in display does not, slots restock; Mido takes any shield.
- C, seeds: all 184 chests accounted for (164 shuffled, 20 excluded until their routes are known); four kept story
  wrappers; fast start in seeds; seeds 3, 7, 22 (Chest) and shop-7 (Chest+Shop) in `E:/OOTRemake/work/r5-seed/`,
  regenerated from `main` byte-identical.
- D, gifts: 79 gift checks classed; `--shuffle Gift` for 45 swaps plus the Great Fairies (new saved Bools, D22,
  worked on an old save) and the songs' play-along; songs and the Fairy Ocarina work from chests (D23).
- E, playtest: 197 questions in 17 route sessions with prepared mods (`plans/playtest/`).

For round 6 (to agree with Kareem): player-facing location descriptions for spoilers (Mido's chests are mirrored
against the N64 names); a "songs anywhere" setting; gift items in chests as each is tested; the logic-session
answers as they come; the rupee economy for early shop purchases.

## Round 6 (M2 settings string and readable spoilers; M3 hints, scrubs and tokens begin)

Kareem agreed, 2026-11-08 ("go ahead and continue"); he plays `seed-shop-7` meanwhile. Four tracks, Bermuda thread
`cs-r6`, herdr-core. New sections of `plans/03-game-data.md`: 20 (A), 21 (B), 22 (C), 23 (D), each appended in number
order. The round 5 rules on shared files carry over (a small change to another track's file is its own commit,
posted). No Hookshot build. Track C runs on the default Claude model, the others on `openai-codex/gpt-6.1-sol`.

### Track A: readable locations (`r6/names`)

Owns `src/clawshot/data/location_names.toml` (new), the spoiler and play-note code (`spoiler()` in
`src/clawshot/generate/__init__.py`), `tests/test_names*.py`, `plans/rounds/r6-names.md`, section 20.

1. For every shuffled location (chests first, then shops, gifts, the Great Fairies): a short player-facing name and a
   one-line "where" (area, room, what you see; dungeon room numbers mean nothing to a player), from the placement
   data (positions, the room's doors and landmarks) and guides (facts only, cite the URL). Mido's house, settled in
   game: walking in, the far-left chest is Hash `4555665598794293658` (OoT Randomizer's "KF Midos Top Right Chest")
   and the far-right one `9725242744547055868` ("Top Left"); say how the middle two map.
2. Every place where an OoT Randomizer name was matched to a remake chest by position or by guess (track C's
   symmetric pairs: Goron City maze blue chests, Gerudo Training Ground lobby and heavy-block chests, Spirit
   invisible pair, Fire's timed scarecrow-room chests; Mido's house): is the match only a label, or do the
   vanilla item or the rule differ between the pair? List any that change logic.
3. The spoiler and the play note show the player-facing name and "where" next to the OoT Randomizer name. A test
   that every shuffled location has both.

### Track B: settings (`r6/settings`)

Owns `src/clawshot/generate/fill.py`'s `Settings` and `src/clawshot/__main__.py`, the price part of
`src/clawshot/patch/shops.py`, `src/clawshot/data/settings.toml` (new), `tests/test_settings*.py`,
`plans/rounds/r6-settings.md`, section 21.

1. A settings string (M2): every setting (shuffled kinds, dungeon items, logic options, fast start, free travel, the
   return guarantee, the new ones below) in one short string; `--settings <string>` and `--print-settings`; the
   spoiler records it; the same string and seed give byte-identical files (a test). Defaults written in one place.
2. `songs`: `song` (default, D23) or `anywhere`. Gift items allowed in chests: a list in `settings.toml` of actors
   seen working in a chest (the Fairy Ocarina, the Song of Storms so far), each with its source; only those leave
   gift locations.
3. Prices: `shop_prices` = `vanilla` or `affordable` (every shuffled shop item 10 rupees, as Ship of Harkinian and
   OoT Randomizer offer), and `cheap_deku_shield` (the Kokiri shop's Deku Shield at 10 rupees whether or not shops
   are shuffled; default on, provisional: Kareem counted 36 guaranteed free-standing rupees in the forest outside
   Mido's house and seed 22 needed nearly all of them). Through `GoodsList` `PriceOffset`, which the shop tests showed
   working; the logic's wallet rules use the patched price. One test output in `E:/OOTRemake/work/r6-settings/`.

### Track C: text and Gossip Stones (`r6/hints`, Claude)

Owns `src/clawshot/formats/msbt.py` (new), `src/clawshot/census/hints.py` (new), `src/clawshot/patch/text.py`
(new), `tests/test_msbt*.py`, `tests/test_hints*.py`, `plans/rounds/r6-hints.md`, section 22.

1. `formats/msbt`: read and write the game's message files (round 4 read them for the Great Fairies' lines with a
   scratch script) from the format, no GPL code. Every message file in the dump round-trips (byte-identical or
   tree-equal, say which) in a `dump` test.
2. A census of Gossip Stones: every stone (Banc actor), how it picks its text (actor parameter, flow, message id),
   and whether it needs the Mask of Truth; the other hint givers (Sheik, the owl, the Kakariko Skulltula house).
3. Item-get text: what decides the get window's text and model for an item from a chest, an NPC and a shop (the song
   in a chest showed a green rupee), and how a patch would name an item in an NPC's line.
4. One test output (`E:/OOTRemake/work/r6-hints/`): a Gossip Stone Kareem can reach early saying a custom line, with
   what he should see. A short design note for hints in round 7 (OoT Randomizer's hint kinds, which fit the remake).

### Track D: scrubs and Skulltula tokens (`r6/tokens`)

Owns `src/clawshot/patch/scrubs.py` and `src/clawshot/patch/tokens.py` (new), `tests/test_scrub*.py`,
`tests/test_token*.py`, `plans/rounds/r6-tokens.md`, section 23.

1. Deku Scrubs (21 in the census): how each sells (actor parameters, flow, price), which are one-time checks, and a
   patch that changes one scrub's item; a test output.
2. Gold Skulltula tokens: how a token is given (the enemy's death, the token actor, its flag), whether a token's
   actor can be swapped for another item (OoT Randomizer's tokensanity), and the House of Skulltula rewards as gift
   checks (are they in the gift census?). A patch and a test output for one early token, if the data allows it.
3. Both as locations the fill can use behind `--shuffle Scrub` and `--shuffle Token` (off), only for what passed
   review; their in-game tests decide the defaults later.

### Track E: the Castle Town shop crash (`r6/shopfix`, added 2026-11-08)

Owns `src/clawshot/patch/shops.py` (except the price code, track B's), `tests/test_shop*.py`,
`plans/rounds/r6-shopfix.md`, a section 24.

Kareem's `seed-shop-7` crashed on entering Castle Town as child (Hookshot v2.0.1, log
`E:/OOTRemake/work/r5-seed/user-seed-shop-7/hookshot_log.txt`, line ~24488): thread `GeneralFormatAsync_`, write to
guest `0x10`, x6/x7 holding the ASCII `Component/ShopPa`; just before, the overlay served `Market_Child_Static` and
the seller packs `Npc_Hylia_021_Shop_Child`, `_018_` and `_020_`. The Kokiri shop's changed packs worked in the
same run and in the round 5 tests.

1. Find the cause from the data, without the game: diff the seed's three Market packs (and the Kakariko and other
   shops' packs it writes) against the dump's, field by field; check every reference a changed `ShopParam`
   (`GoodsList`, boards, group memberships removed by round 5's `dc037c8`) makes against what the pack and the
   placement still provide. Name the change that leaves a null.
2. Bisect outputs for Kareem in `E:/OOTRemake/work/r6-shopfix/` (new game is too slow: use a copy of a save that
   is a child near Castle Town, from `E:/OOTRemake/work/save-backups/`): each Market pack alone, and the suspected
   change reverted, each with what he should see.
3. Fix the patch, with a dump test that reproduces the bad reference, and regenerate the seed as
   `E:/OOTRemake/work/r5-seed/seed-shop-7b/` (same seed and settings) with a launcher; never touch `seed-shop-7`
   or `user-seed-shop-7`.

### Track F: findings from play (`r6/play`, added 2026-11-08)

Owns the round 4 logic files `src/clawshot/data/world/remake/child_*.toml` (no other track this round), their
tests, `plans/playtest/answers.md`, `plans/rounds/r6-play.md`.

Kareem's `seed-shop-7` run (2026-11-08), each to settle against the data and apply with `source` and a test:
1. The Deku Tree: the Boomerang hits the switch that opens the Slingshot room's exit and reaches the top floor, as
   the Slingshot does (round 4's rules ask for the Slingshot only); the Boomerang stuns Gohma. Check each against
   the placement data (the switch and target actors) and change the rules to `Slingshot or Boomerang` where the
   data agrees.
2. The castle moat is shallow: the Ocarina of Time needs no Silver Scale (playtest question; check the HF rules).
3. The Kokiri shopkeeper gave a free Deku Shield after Mido (Kareem held the Kokiri Sword and a Hylian Shield; the
   slot also sold one at 40): round 5's `present_DekuSheld` route. Find its exact conditions and model it (a free
   Deku Shield event after Mido, under those conditions), and say whether it is a check to shuffle later.
4. Record each in `plans/playtest/answers.md` and section 12.

### After round 6

**Round 6 result (2026-11-08):** all six tracks merged (`main` a786358; 511 tests, 68 dump tests).
- A, names: a sourced player-facing catalogue (335 checks); spoilers carry the names and a `play-note.md` with a
  logic-built opening route, shelf positions and prices.
- B, settings: one settings string (`--settings`, recorded in the spoiler, byte-identical replay); songs anywhere
  (opt-in, all 12); `shop_prices` and `cheap_deku_shield` (on); forest closed by default with `closed_deku` and
  `open` (D24); a fill fix that keeps held-item priority when shops are shuffled.
- C, hints: `formats/msbt` (8,640 message files in 16 languages round-trip byte-identical); 40 Gossip Stones
  catalogued; `patch/text`; a custom stone line test output.
- D, scrubs: `--shuffle Scrub` for the four one-time sale families (nine copies; repeat vendors stay vanilla); Gold
  Skulltula tokens not shuffled (a replaced token has no persistence).
- E, shop crash: shuffled shop goods grew a file inside the seller pack past its size-table entry; the writer now
  raises nested entries (game-confirmed in Castle Town, purchases work). Shop refills stay in shops; bomb and
  Bombchu pickups only where the Bomb Bag is guaranteed (D25); Buy Blue Fire only where the game sells it.
  `seed-shop-7b` is seed-shop-7 with the size fix only, for Kareem's save.
- F, play findings: the Boomerang works for the Deku Tree's switches, the vine wall and Gohma; the Kokiri
  shopkeeper's free Deku Shield (repeats while none is equipped) is a logic event, not a check; the moat needs no
  scale.

Waiting on Kareem in game: `seed-shop-7b`; `free_time_travel` after his first Master Sword pull; the logic-session
route cards. The Minuet, closed-Deku, price and Gossip Stone tests passed (2026-11-08; the Fairy Ocarina from a
chest shows no model).

For round 7 (to agree with Kareem): hints on Gossip Stones (track C's design note); gift items in chests as each is
tested, and get-item models for gift items from chests (songs show a green rupee, the Fairy Ocarina
none); a once-only gate for the shopkeeper's shield so it can be a check; boss Heart Containers as checks; token
persistence; the advanced options (bomb pickups as bags, open Deku) as Kareem asks for them.

## Round 7 (M3 hints, get-item models, boss hearts, gift follow-ups)

Kareem agreed, 2026-11-08 ("Yes, please do"); he plays `seed-shop-7b` and his main save meanwhile. Four tracks,
Bermuda thread `cs-r7`, herdr-core. New sections of `plans/03-game-data.md`: 25 (A), 26 (B), 27 (C), 28 (D), each
appended in number order after 24. The round 5 and 6 rules on shared files carry over (a small change to another
track's file is its own commit, posted; `patch/__init__.py`, `generate/fill.py`, `settings.toml`,
`item_actors.toml` and the CLI are shared). No Hookshot build. Track A runs on the default Claude model, the others
on `openai-codex/gpt-6.1-sol`. Every in-game test is one launcher with its own user folder and a short checklist;
save-copy tests name the save they copy from `E:/OOTRemake/work/save-backups/`.

### Track A: hints (`r7/hints`, Claude)

Owns `src/clawshot/generate/hints.py` (new), the hint step in `src/clawshot/patch/text.py`, `tests/test_hints*.py`,
`plans/rounds/r7-hints.md`, section 25. Round 6's design note (`plans/rounds/r6-hints.md`, "Design note: hints in
round 7") is the spec:
1. Gossip Stones as hint locations in the world (a non-item kind; OoT Randomizer's `HintStone` regions and rules
   through `STONE_LINKS`, the four remake-only stones by hand), one label per stone.
2. Hint selection: Way of the Hero, barren ("foolish") areas, item and `always`/`sometimes` location hints, junk;
   a hint goes only on a stone reachable where it matters. Names from the round 6 catalogue; area names from the
   world's hint areas. Clawshot's own wording (no copied text).
3. Settings through the settings string: `hints` = `always` (stones speak without the Mask of Truth) or `mask`
   (vanilla), and the distribution. Provisional default `always`, English text written to every language archive;
   both are questions for Kareem.
4. A `make_seed` step, the hints in the spoiler and the play note, a dump test that every hint names a placed item
   at a reachable stone. Test output: `E:/OOTRemake/work/r7-hints/seed-shop-7c/`, which is `seed-shop-7b` plus hint
   text only (same placements, hints chosen from its spoiler under current logic; every non-text file byte-identical
   to 7b's), with a launcher that continues from his `user-seed-shop-7b` save copy.

### Track B: get-item models and gift items in chests (`r7/getitem`)

Owns `src/clawshot/patch/getitem.py` (new), the chest-allowed list in `src/clawshot/data/settings.toml`,
`tests/test_getitem*.py`, `plans/rounds/r7-getitem.md`, section 26.
1. What picks the model in the get window for an item from a chest (round 6: `Item_Melody_*` ModelInfo is
   `Obj_Rupee`, so a song shows a green rupee; the Fairy Ocarina from a chest shows no model, text correct). Trace
   both from the data and name the field each reads.
2. A patch so each gift item that can land in a chest shows a fitting native model (an ocarina for the ocarinas; a
   native note or song model for songs if the game has one, else say so and propose one); no new assets.
3. Gift items in chests: list the gift items not yet seen working in a chest; one test output (new game, Kokiri
   Forest and Mido's chests) holding as many of them as fit, each with what Kareem should see; the allowed list grows
   only with his results.

### Track C: boss Heart Containers and Gold Skulltula tokens (`r7/drops`)

Owns `src/clawshot/patch/drops.py` (new), `src/clawshot/patch/tokens.py`, `tests/test_drops*.py`,
`tests/test_token*.py`, `plans/rounds/r7-drops.md`, section 27.
1. The 8 boss Heart Containers (`Obj_Heart_Container` in each boss room's Banc): how each spawns after the boss, its
   saved flag, and which items can replace it without round 2's freestanding crash (#287 signature: majors need their
   object or script group). Propose a location kind with a native-actor restriction, as D21 does for shops.
2. A test output on a save copy before a boss (King Dodongo: check `2026-11-08_1114-main-dodongo`; say if no backup
   fits): the Heart Container swapped for a safe item, with what Kareem should see, including after Save and Continue.
3. Gold Skulltula tokens: round 6 found a replaced token lacks the `OneShotGoldTokenDeadAfter` callback (section 23).
   Is there a way to keep the token actor and change what it grants, or to keep the callback? A test output only if
   the data supports one; else say what is missing.
4. `--shuffle BossHeart` (off) for what passed review; their in-game tests decide.

### Track D: the shopkeeper's shield as a check, and the Treasure Chest Game (`r7/gifts`)

Owns `src/clawshot/patch/gifts.py`, `tests/test_gift*.py`, `plans/rounds/r7-gifts.md`, section 28.
1. The Kokiri shopkeeper's free Deku Shield repeats while none is equipped (round 6, track F, `r6-play.md`). Add a
   once-only gate on both grant branches (an existing flag first, else a new saved Bool, D22) so it becomes a gift
   check; keep the vanilla repeat when unshuffled. Logic: the free shield event stays as it is when unshuffled.
   Test output (new game) with the check given a different item, and what Kareem sees on a second visit.
2. The Treasure Chest Game reward chest (D17, kept vanilla): a contents-swap test output on a save copy of a child
   near Castle Town (the round 6 Castle Town tests used one), with what he should see. It joins the shuffle only
   after his result.
3. The 9 boss rewards (stones and medallions): research only: how each is given (the blue warp and its cutscene,
   flags, the Temple of Time's checks of quest steps rather than items, section 19), and what shuffling them would
   need. No patch.

### Track E: hints never name junk (`r7/hintfix`, added 2026-11-08)

Owns `src/clawshot/generate/hints.py`, `tests/test_hints*.py`, `plans/rounds/r7-hintfix.md`, section 29.
1. D29: item, `always`, `sometimes` and random hints name only items worth having (progression items, Pieces of Heart
   and Heart Containers, non-progression upgrades such as wallets and capacity upgrades); never rupees, ammo, refills,
   `Buy` items, recovery hearts or bottle contents. Define the class once from the world's item data, with a test
   that no location hint names junk over many seeds and that barren hints are unchanged.
2. Rebuild Kareem's test output as `E:/OOTRemake/work/r7-hints/seed-shop-7c-next/` (7b's placements, only text files
   differ from 7b; never write to `seed-shop-7c`, which he plays; Claude swaps it in). List the 40 lines.

### Track F: graveyard and bombs from play (`r7/play`, added 2026-11-08)

Owns `src/clawshot/data/world/remake/child_graveyard.toml`, the graveyard rows of
`src/clawshot/data/location_names.toml`, `tests/test_world_remake_play.py`, `plans/playtest/answers.md`,
`plans/rounds/r7-play.md`, section 30.
1. The child graveyard's three pull-back graves (`Land_Graveyard_HidingHoleJoint_A_01` at x 4.0 z 5.7, x 21.5 z 11.2,
   x 21.4 z 23.2 in `Graveyard_Child_Dynamic`). Kareem, from the Royal Family's Tomb: the fourth grave from the right
   (unmarked) holds a ReDead and a chest (the shield grave, `Obj_TBox_A_06` 16912540161937823130); another (marked)
   grave holds a cracked wall (`WallCrack` 9366825990748670811 at (3.9, 83.9, 27.0) in `Graveyard_Child_Static`).
   What is behind the cracked wall, and is any of it a check? Rewrite the three graves' "where" so a player standing
   at the tomb entrance finds each, and check the heart-piece grave's rule (`True`) against the data.
2. Bombs from a chest pack: in Kareem's `seed-shop-7c` save (read only:
   `E:/OOTRemake/work/r7-hints/user-seed-shop-7c`, newest slot) a shop bomb bundle from a chest gave
   `IsGet.Item_BombBag_Small` and 20 bombs; bombs equip, but Link raises one for a few frames and the action cancels.
   His main save, where bombs work, is copied at `E:/OOTRemake/work/save-backups/2026-11-08_2140-main-jabu`. Find
   what makes bombs usable (compare the two saves' bomb and pouch entries by GameDataList name; trace the player's
   bomb action condition), and say whether the real Bomb Bag (KF Storms Grotto chest in 7b/7c) will make bombs work
   on his 7c save or leave him without bombs. No save edits; if a fix is needed, propose it in the round file.
3. What a vanilla chest gives when its item is already owned (the shield grave's `TBox_Shield_Hylian` with the
   Hylian Shield held; Kareem got 20 rupees from that grave while the graveyard had loaded vanilla files).
4. Record each in `plans/playtest/answers.md`, the catalogue and section 30.

### Track G: bombs need Goron's Bracelet (`r7/bombs`, added 2026-11-08)

Owns the remake helper overrides for explosives (wherever the world's remake overrides keep them; small posted
commits to shared world files), `tests/test_world_remake_bombs.py`, `plans/rounds/r7-bombs.md`, section 31.
1. D30: every rule that uses bombs (OoT Randomizer's `Bombs`/`has_bombs`, the bomb half of `has_explosives` and
   `can_blast_or_smash`, `can_use(Bombs)`, bomb-only tricks) also needs lift grade Low: Goron's Bracelet as child, any
   strength upgrade as adult. Which items grant `LiftGradeUP` at which grade: from `PouchActorInfo`/`ExpansionAvility`
   (section 30), per age. Bombchus and Bomb Flowers keep their own rules (check Bomb Flowers already need strength).
   Overrides with `was` and `source`, never edits to the translated OoT Randomizer files.
2. Tests: a synthetic world where bombs without the Bracelet reach nothing new; the seed 7 matrix (Chest,
   Chest+Shop, Chest+Shop+Gift, the default string) still generates within the existing bound (print attempts and
   spheres); the 200-seed default beatability test passes; 7b's 228 placements still replay to a win.
3. List, from those seeds, how often the first bomb use moved later, and any rule that now cannot be met.

### After round 7

**Round 7 result (2026-11-08/09):** all seven tracks merged (`main` 739b930; 619 tests, 78 dump tests).
- A, hints: the 40 Gossip Stones as hint locations; Way of the Hero, barren, item, `always`/`sometimes`, random and
  junk hints; `hints` = `always` (default, D26) or `mask`; English text in every language archive. In game
  (`seed-shop-7c`): the stones speak without the mask; the highlight colour now ends after each name.
- B, get-item models: the get window's model traced; the Song of Storms shows an ocarina stand-in, Din's Fire and
  the Adult's Wallet work from chests; the Fairy Ocarina still shows no model.
- C, boss hearts and tokens: `--shuffle BossHeart` (off) with native floor pick-ups only (D27), game-confirmed at
  King Dodongo; a token's pouch reference does not decide its grant, so tokens stay unshuffled.
- D, gift follow-ups: the Kokiri shopkeeper's gift is a once-only check holding only items no seed needs (D28,
  game-confirmed); the fill places items in order of restriction; the Treasure Chest Game swap is built, untested;
  the nine boss rewards researched.
- E, hints never name junk (D29).
- F, from play: the graveyard's three graves (the fairy wall split from the shield grave); an owned Hylian Shield
  turns that chest into a red rupee, which the seed's patch overrides; bombs need lift strength.
- G, bombs need Goron's Bracelet in logic (D30); helper overrides in the remake files.

Waiting on Kareem in game: bombs before and after Darunia's Bracelet on `seed-shop-7c`; the Jabu-Jabu switch with
Bombchus; the Treasure Chest Game swap; `free_time_travel` after his first Master Sword pull; the route cards.

For round 8 (to agree with Kareem): fill robustness (Chest+Shop+Gift seed 7 needed all 10 attempts); the Fairy
Ocarina's get model; a fresh full seed with every proven setting for a real playthrough; extending the shopkeeper's
window (D28); token shuffle by another route; the boss rewards; run and sprint speeds from the animations (optional).

## Round 8 (M2 dependable seeds; M3 more checks: gifts, freestanding, shops)

Kareem agreed, 2026-11-09 ("let's go on please"); he plays `seed-shop-7c` and his main save meanwhile. Five tracks,
Bermuda thread `cs-r8`, herdr-core. New sections of `plans/03-game-data.md`: 32 (A) to 36 (E), in number order. The
round 5 to 7 rules on shared files carry over (`generate/fill.py` belongs to track A this round; other tracks post
small isolated commits to it). No Hookshot build. Track A runs on the default Claude model, the others on
`openai-codex/gpt-6.1-sol`. Kareem showed Ship of Harkinian's shuffle settings for reference; its options that need
engine code (shuffling swim, grab, climb, crawl, ocarina buttons, Roc's Feather, skeleton key) are out of reach for
RomFS-only mods (D14).

### Track A: dependable fill (`r8/fill`, Claude)

Owns `src/clawshot/generate/fill.py`, `tests/test_generate*.py`, `tests/test_fill*.py`, `plans/rounds/r8-fill.md`,
section 32.
1. Measure: fill attempts for 200 seeds in each mode (Chest; Chest+Shop; Chest+Shop+Gift; with Scrub and BossHeart;
   the default string), printing the item, the allowed locations left and the frontier at every failed attempt.
   Round 7's Chest+Shop+Gift seed 7 needed all 10 attempts.
2. Fix the causes the measurements show, the way OoT Randomizer's fill handles them (`Fill.py`: order, restrictive
   fill, its swap and retry rules at 526b4c8d), with a failing-before test for each; no relaxed rules or added
   attempts. Target: every mode's first attempt succeeds for at least 95% of the 200 seeds and none needs more than 3.

### Track B: get-item models (`r8/getitem`)

Owns `src/clawshot/patch/getitem.py`, the chest-allowed list in `src/clawshot/data/settings.toml`,
`tests/test_getitem*.py`, `plans/rounds/r8-getitem.md`, section 33.
1. The Fairy Ocarina from a chest shows no model (round 7, game-confirmed after the bind change). Find why from the
   data (the ocarina's ModelInfo, the get window's bind actions, how a gift's own presentation differs) and fix it.
2. One new-game test output with the Fairy Ocarina and the gift items not yet seen in a chest (Zelda's Letter, the
   Weird Egg, the Gerudo Membership Card, Epona's Song, the Ocarina of Time, the masks a seed could place), each with
   what Kareem should see. The allowed list grows only with his results.

### Track C: shops (`r8/shops`)

Owns `src/clawshot/patch/shops.py`, the Kokiri shopkeeper's gift patch in `src/clawshot/patch/gifts.py` (posted
small commits; track D owns the rest of the file this round), `tests/test_shop*.py`, `plans/rounds/r8-shops.md`,
section 34.
1. The Kokiri shopkeeper's gift window (D28): keep a shuffled gift available until collected, past Gohma and the
   castle visit, through the merchant's flow (an existing flag first, else a new saved Bool, D22); unshuffled stays
   vanilla. A new-game test output that skips him until after Gohma. D28's restriction lifts only after Kareem's
   result.
2. Settings like Ship of Harkinian's: `shop_slots` (0 to 8 shuffled shelves per shop, the rest vanilla; default all
   eight) and `scrub_prices` (`vanilla` or `fixed` with a price), through the settings string, with tests.

### Track D: more gift checks (`r8/gifts`)

Owns `src/clawshot/patch/gifts.py` (except track C's part), `src/clawshot/patch/gift_rules.toml`,
`src/clawshot/census/gifts.py`, `tests/test_gift*.py`, `plans/rounds/r8-gifts.md`, section 35.
From Ship of Harkinian's list, the checks the remake's flows can give: the 14 cows (milk with Epona's Song), the
Skulltula House rewards (10 to 50 tokens; 100 if the flow allows), the frogs (the song prizes and the two rewards),
and the merchants (Medigoron's Giant's Knife, the carpet salesman's Bombchus, Granny's potion). For each: the census
(flow, event, saved flag, repeat behaviour), the swap through the existing gift machinery (D22 once-gates), logic
rules, and a test output on a fitting save copy or new game. Each joins `--shuffle Gift` only after Kareem's result.

### Track E: freestanding items with native pick-ups (`r8/freestanding`)

Owns `src/clawshot/patch/freestanding.py` (new), `tests/test_freestanding*.py`, `plans/rounds/r8-freestanding.md`,
section 36.
1. The freestanding locations (the 36 heart-piece anchors first, then other placed pick-ups): actor, saved flag,
   respawn behaviour, and whether a native floor pick-up from D27's palette (Heart Container, Piece of Heart, Deku
   Shield, Hylian Shield, red rupee) can stand in, as the King Dodongo test showed.
2. `--shuffle Freestanding` (off) restricted to that palette, logic and tests; one test output (an early heart piece
   swapped for a shield), with what Kareem should see, including after Save and Continue.

### After round 8

Claude builds a fresh full seed with every game-confirmed setting (Chest, Shop, Gift, Scrub, BossHeart as proven;
hints; forest closed; cheap Deku Shield) for Kareem's first full playthrough.

### Settings backlog (Ship of Harkinian's lists, shown by Kareem 2026-11-09)

Reference for later rounds and presets; feasibility marked [inference] is unverified. RomFS-only (D14) rules out
anything needing engine code.
- **Have:** songs anywhere; forest closed/`closed_deku`/open; dungeon items in their own dungeon or anywhere; Gossip
  Stone hints without the mask (`always`) or with it, `balanced` distribution; scrubs; shops and prices; boss hearts.
- **Likely through saved flags or flows** [inference, each needs research and an in-game test]: Door of Time open
  (the `DoorOfTime` flow counts the stones); Zora's Fountain open (King Zora moved); Jabu-Jabu open; Gerudo Fortress
  fast carpenters; skip Ganon's trials; skip child stealth, the Epona race, planting beans; start with maps and
  compasses; full wallets; Big Poe count; Rainbow Bridge conditions (the bridge's check); separate small key, boss key
  and Fortress key settings (logic and fill only).
- **Text, through `patch/text`:** static hints at Dampé's diary, the Skulltula House, merchants, Malon, the frogs,
  Saria, warp-song destinations; the Temple of Time altar and Ganondorf need their text traced first (round 6 note).
- **Research first:** random or adult starting age; shuffled dungeon rewards (round 7 researched how they are given);
  dungeon and boss entrance shuffle (whether Banc exits name their destination).
- **Needs engine code, out of reach:** ice traps, keyrings, boss and Ganon souls, Triforce Hunt, Ganon's boss key
  given by a reward count, Blue Fire and Sunlight Arrows, Bunny Hood speed, masks as adult.
