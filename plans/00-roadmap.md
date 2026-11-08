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
   Kareem's save backups (his main game has an adult Link: what flags it has set). Cite the flow, entry and flag.
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
