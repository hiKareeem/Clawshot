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

### Round 8 result (2026-11-09)

All five tracks merged; main `14d7a26`, gates 721 passed / 86 skipped, dump 85.
- A fill: every mode 200/200 seeds on the first attempt, none unbeatable (D32 keys first, D33 type palettes, D34
  Archipelago's safe swap). Before: all kinds 0%, gifts 9.5%.
- B get-item models: gift items in chests show their models and text (Letter, Egg, Card confirmed by Kareem); the two
  ocarinas still show none (cosmetic; parked).
- C shops: `shop_slots`, fixed scrub fees; the shopkeeper's gift persists past Gohma and the castle (Kareem's test),
  so it holds any item (D28 lifted).
- D gifts: frog prizes, Skulltula House rewards and three merchant sales built behind in-game acceptance (not in
  `--shuffle Gift` yet); D31 keeps the Weird Egg and Zelda's Letter vanilla (one shared trade cell).
- E freestanding: floor heart pieces and boss hearts take native pickups; Kareem confirmed the ranch tower shield.

### After round 8

Round 9 candidate from play: `free_time_travel` also needs Sheik moved: as adult before the Forest Temple, Sheik
stands at the pedestal with a Talk prompt in the way (Kareem, 2026-11-09). Trace Sheik's Temple of Time placement
and its gate, and patch both before the pedestal test. Speedrunners (via Kareem, 2026-11-09): Sheik leaves once the Forest
Medallion is held, not after the Minuet; trace whether that reads the medallion item or the sage flag, which matters once
rewards are shuffled.
Kareem (2026-11-09, after the Forest Temple): Sheik stays at the pedestal until entering the room plays the Prelude
of Light scene, then leaves. `free_time_travel` must therefore clear Sheik's pre-Forest placement or that scene's
gate as well as the pedestal's; saves from before Phantom Ganon to after the scene are in
`save-backups/2026-11-09_1347-main-after-forest` for the trace.
Also from play: Sheik's second line there sends the player to Kakariko for the Hookshot (its vanilla place). In a seed
it should name where the Hookshot is (a static hint through `patch/text`, like Dampé's diary) or say nothing about it.

Claude builds a fresh full seed with every game-confirmed setting (Chest, Shop, Gift, Scrub, BossHeart as proven;
hints; forest closed; cheap Deku Shield) for Kareem's first full playthrough.

Round 9 candidate (Kareem, 2026-11-09): label dungeon checks in `location_names.toml` with the pause map's floor
(1F to 5F), so play notes match what the player sees. Kareem's Fire Temple floor maps (a guide's, facts only) show
16 chests and 5 Gold Skulltulas, as the census has, the two remake chests being the timed 5F trio's extra pair.
Derive floors from game data (room index to map floor) [inference: the map data holds it; not traced].

Round 9 candidate (seed 8 play, Kareem 2026-11-09): adult-only items obtained as child lock the item buttons. The
Bow from a chest auto-equipped as child; afterwards the Boomerang and Deku Sticks could not be used until save and
reload. Trace the remake's age gate for button items and the get-time auto-assign (player and pouch data, the get
flow); fix in data if it lives there, otherwise document the reload workaround and consider which items (Bow,
Hookshot, Hammer and others) need it. Backup: `save-backups/2026-11-09_1423-seed8-bow-lock`.
Detail (Kareem): loading zones do not clear it, Save and Continue does; at pickup the Bow joined the ZR item bar though
greyed out for child, and the reload removed it from the bar. Test the reverse too (adult picking up the Slingshot or
Boomerang). Fallbacks if no data fix: the play note and get text tell the player to Save and Continue, or a setting
keeps age-locked button items out of locations the other age reaches first.

Round 10 candidates (seed 8 play, Kareem 2026-11-09):
- The Market Potion Shop's child bottle (the owner gives an empty bottle, Link catches a bug in the shop, the owner
  fills it with Red Potion) is a remake-only check missing from the census; round 4 listed it as unclear
  (`Npc_Hylia_020_Shop_Child`, entry `Item_Bottle_TutorialEvent_Talk`, section 15). The remake has five bottles, not
  four. Trace it, add it as a gift check and to the logic as an early bottle (its conditions: child, day, no bottle
  yet?), and an in-game test.
- Bombchu Bowling opens after Dodongo's Cavern (round 4 already has `'Defeat King Dodongo'`; players online agree). The
  remake picks among five prizes at random (players online: a heart piece and a Bomb Bag upgrade among them; the
  flow's `Clear{First,Second,Third}Time` flags exist). Make it deterministic as OoT Randomizer does: the first win
  gives First Prize, the second win Second Prize, later wins the filler prizes; an in-game test. Same question for
  the shooting galleries' normal and expert prizes (Kareem: an expert tier exists).

- Release the seven frog checks into `--shuffle Gift` (Kareem's frog experiment passed, 2026-11-09, answers.md R8-FROGS):
  drop their `keep_vanilla` holds in `remake/gifts.toml`; the five song prizes enter the pool as Rupees (20), OoT
  Randomizer's vanilla item for them (the native prize varies 5 to 30). The Skulltula House previews passed too; the
  40 reward stays held until tested; merchants wait for Kareem's main save.
- Dampé's gravedigging heart piece (Kareem asked, 2026-11-09): not in `--shuffle Gift` yet (logic has it, child at
  night after Time Flows; the remake reworks the tour, Link leads Dampé to the spot). Trace its grant and add it as a
  gift check if the flow allows a once-only swap.
- Door of Time setting (Kareem, 2026-11-09: he expected door and pedestal open from the start, as Ship of Harkinian
  offers; free time travel alone still leaves the three Spiritual Stones, the Ocarina of Time and the Song of Time
  between child and adult). `door_of_time` = closed (vanilla) | song_only | open, through the `DoorOfTime` flow and
  its gates; logic for each; the default is Kareem's call (asked 2026-11-09). With it, decide whether
  `free_time_travel` becomes default on (after the first-pull boundary test).
- `free_time_travel` first-pull bug (Kareem, 2026-11-09, answers.md R9-FIRST-PULL): with the patch, Sheik's first adult
  scene plays without him (dialogue skipped). Keep the placed Temple Sheik for `Dm_TimeTemple_0050` (present while it
  has not played, or after Forest completion until the Prelude), check flags the skipped dialogue sets, and retest
  from an older child autosave; the pedestal may stay blocked until he leaves after that first scene.

Later-round candidate (Kareem, 2026-11-09, seed 8: "we need a check/item tracker"): **D38 makes
this a Tracker tab of the UI**, reading the **seed's own save folder**, not an independent page
watching the player's main autosave. Resolve collected state by actor/check kind: chests use
named `IsTreasureBoxOpen.<Hash>` Bools; ordinary loose pickups use their saved placement-Hash
Bool64 state; gifts and scripted actors use their audited event/state flags (section 44).
A universal raw-Hash test falsely labels opened chests unclaimed. Read the seed's spoiler and
save to show checks by area, owned items and remaining keys per dungeon (its first job), and
checks currently in logic without naming unfound items. Update on saves; PopTracker/EmoTracker
export remains a later option. D38 and section 44 distinguish this from the native current-
dungeon-only map/key display.

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

## Round 9 (M2 seeds that play cleanly; testers)

Kareem agreed, 2026-11-09 ("Sounds good, please do"); he plays seed 8 (`work/r8-full`) meanwhile, so the CPU rule
holds the whole round: one worker process at a time while `hookshot.exe` runs. Three tracks, Bermuda thread `cs-r9`,
herdr-core, all on `openai-codex/gpt-6.1-sol`; Claude reviews. New sections of `plans/03-game-data.md`: 37 (A) to 39
(C), in number order. Shared files as in rounds 5 to 8 (small isolated commits; `generate/fill.py` changes only with
a post). Seed 8's findings may be routed to any track during the round. No Hookshot build.

### Track A: the item bar and age-locked items (`r9/itembar`)

Owns `plans/rounds/r9-itembar.md`, section 37, any new `src/clawshot/patch/itembar.py` and its tests.
1. Trace the remake's item bar (one ZR item; R cycles the bar; the Items menu greys out items Link's age cannot use)
   from the game data: what adds an item to the bar when it is obtained, what rebuilds it on load, and where the age
   restriction lives. Kareem (seed 8): the Bow from a chest joined the bar as child, item use jammed until Save and
   Continue, loading zones did not clear it, and after the reload the Bow was off the bar. Backup:
   `save-backups/2026-11-09_1423-seed8-bow-lock`. Table every button item with its usable age.
2. If a data change prevents it (the item not added, or the bar rebuilt at the get), patch it behind a default-on
   setting, with tests and a new-game test output: child takes the Bow from a Mido chest; an adult takes the
   Slingshot or Boomerang. A checklist for Kareem.
3. Otherwise: the play note says to Save and Continue after obtaining an item Link's age cannot use, listing those
   items when the seed places one where the other age reaches it first; propose (do not build) a get-text line and a
   fill setting that keeps age-locked button items out of such locations, with their costs, for Kareem.

### Track B: Sheik and free time travel (`r9/sheik`)

Owns `src/clawshot/patch/age.py`, `plans/rounds/r9-sheik.md`, section 38, Sheik's text patch and tests.
1. Trace what puts Sheik at the Temple of Time pedestal before the Forest Temple and what the Prelude of Light scene
   sets when it moves him (Kareem: Sheik stays until entering the room after the Forest Temple plays the scene; the
   speedrunners say the Forest Medallion triggers it). Compare `save-backups/2026-11-09_1022-main-adult-first`
   (adult, before the Forest Temple) with `2026-11-09_1347-main-after-forest` (before Phantom Ganon to after the
   scene). Say whether the gate reads the medallion item or a sage flag (matters when rewards are shuffled).
2. Extend `free_time_travel` (section 16) so an adult before the Forest Temple can return to child: Sheik not in the
   way and the pedestal usable, while the Prelude of Light check (Sheik at Temple) still plays after the Forest
   Medallion. Logic for the setting; a test output on a copy of the adult-first backup with a checklist.
3. Sheik's line there sends the player to Kakariko for the Hookshot. In seeds, rewrite it through `patch/text` to name
   where the seed's Hookshot is (as a static hint) or to drop the Hookshot; all 16 language archives get the English
   (D26). Tests.

### Track C: seed packs and map floors (`r9/seedpack`)

Owns a new `src/clawshot/pack/`, `docs/seed-pack.md`, `plans/rounds/r9-seedpack.md`, section 39 and their tests;
`src/clawshot/data/location_names.toml` for item 2 (posted small commits).
1. Seed packs for invited testers (Kareem: ready-made seeds, code not hidden): `python -m clawshot.pack --settings
   <CS1> --seed <n> --out <zip>` builds a zip with Clawshot's source and data (no plans), `Make seed.bat` and
   `Play seed.bat`. Make asks once for the tester's romfs and Hookshot folders, checks the game version (the dump
   build, `e0f3ccfa`) before anything else, runs the generator with `uv`, and checks the output against a digest the
   pack records (same string, seed and version give the same bytes). Play starts `<Hookshot>\bin\hookshot.exe` with
   `HOOKSHOT_NO_UPDATE_CHECK=1` and its own user folder, and stops if that exe is missing. No game file and nothing
   derived from one goes in the zip except that digest. A pack for seed 8's settings, made in a scratch folder and
   compared with `work/r8-full/seed-full-8`; `docs/discord/server-kit.md`'s tester guide brought in line.
2. Dungeon directions name the pause map's floor (1F, 2F, B1...), taken from the game data (room to map floor), so
   play notes match what the player sees; facts from guides only to cross-check (Kareem's Fire Temple maps: 16 chests,
   5 Gold Skulltulas).

### Round 9 result (2026-11-09)

All three tracks merged; main `90ef730`, gates 761 passed / 89 skipped, dump 88.
- A item bar: the save keeps the selected bar item and the load-time rebuild filters by age; no data action rebuilds
  it at a pickup, so seeds ship the fallback: `play-note.md` tells the player to Save and Continue and lists the
  seed's age-locked items the wrong age reaches first (seed 8: 10). Kareem reproduced the lock on Lichii (game
  behaviour). A get-text line and a fill setting are proposed in `plans/rounds/r9-itembar.md` for Kareem.
- B Sheik: Temple Sheik follows Forest quest completion (`SageOfForest_IsCompleted_Exp`), not the medallion; "Sheik
  at Temple" now needs `'Defeat Phantom Ganon'`. `free_time_travel` (default off) opens the pedestal and hides Temple
  Sheik until Forest completion; Kareem's test pending (`work/r9-sheik-cs9b/ingame`). Every seed's Sheik names the
  seed's Hookshot location in all 16 languages.
- C seed packs and floors: `python -m clawshot.pack` builds a private source-only zip with `Make seed.bat` (version
  check first, Hookshot optional) and `Play seed.bat`; a pack replayed seed 8 byte for byte. Emulator steps in
  `docs/seed-pack.md` (Lichii confirmed). Dungeon directions name the pause-map floor (134 chests, from MapParam).
- From play: the guard house crashes are Hookshot#1112 (commented with Kareem's OK); test pools now cap their workers
  (`c9e2e2b`).

First public test seed (Kareem, 2026-11-09, after another randomizer posted a ready-made rando in the Lichii server without
trouble): seed 10 with seed 8's settings (Chest, Shop, Gift, Scrub, BossHeart), main `ceaada4`, pack
`work/r9-packs/clawshot-seed-10.zip` (`READ ME FIRST.txt` with the Discord link). Chosen because Bombchu Bowling's
random Second Prize holds a 1-rupee filler (seeds 9 to 16 checked; the First Prize stays the vanilla Bomb Bag).
Make replayed it end to end from a fresh extract: Verified seed 10, 10 wrong-age warnings in its play note.

## Round 10 (M3 more gift checks; age-travel settings; `.nup` packs; pots exploration)

Kareem agreed, 2026-11-09 ("please go ahead"); he plays seed 8 meanwhile, so one worker process at a time while
`hookshot.exe` runs (`CLAWSHOT_WORKERS=1` on every gate run). Four tracks, Bermuda thread `cs-r10`, herdr-core, all on
`openai-codex/gpt-6.1-sol`; Claude reviews. New sections of `plans/03-game-data.md`: 40 (A) to 43 (D), in number
order. Shared files as before (small isolated commits, posted). No Hookshot build.

### Track A: gift checks (`r10/gifts`)

Owns `src/clawshot/patch/gifts.py`, `patch/gift_rules.toml`, `data/world/remake/gifts.toml`, `census/gifts.py`,
`tests/test_gifts*`, `plans/rounds/r10-gifts.md`, section 40.
1. Release the seven frog checks into `--shuffle Gift` (Kareem's experiment passed, answers.md R8-FROGS): drop their
   holds; the five song prizes enter the pool as Rupees (20) (OoT Randomizer's item; the native prize varies).
2. The Market Potion Shop's child bottle (answers.md R9-SEED8-MARKET; round 4 listed it as unclear,
   `Npc_Hylia_020_Shop_Child`, entry `Item_Bottle_TutorialEvent_Talk`, section 15): trace its conditions and saved
   gate, add it to the census and as a gift check (an early bottle in logic: child, its real conditions), a swap
   patch, and a test on a save copy that has not had it, with a checklist.
3. Bombchu Bowling, deterministic as OoT Randomizer: the first win gives First Prize, the second win Second Prize,
   later wins the native filler; both shuffled under Gift (the opening stays `'Defeat King Dodongo'`). Then the
   shooting galleries' normal and expert prizes (Kareem: an expert tier exists): the same if the flows allow, else
   a report. Test outputs with checklists.
4. Dampé's gravedigging heart piece (the remake reworks the tour): trace its grant and add it as a once-only check if
   the flow allows.

### Track B: age travel (`r10/agetravel`)

Owns `src/clawshot/patch/age.py`, a new Door of Time patch module, their logic overrides and tests,
`plans/rounds/r10-agetravel.md`, section 41.
1. `free_time_travel` first-pull bug (answers.md R9-FIRST-PULL): Sheik's first adult scene plays without him. Keep the
   placed Temple Sheik while `Dm_TimeTemple_0050` has not played, and from Forest completion until the Prelude; find
   what the skipped dialogue sets (Kareem's test user `work/r9-sheik-cs9b/ingame/user-free-time-travel-next` holds the
   save after the broken scene); a test from an older child autosave.
2. D35: `door_of_time` = closed (default) | song_only | open. Trace the `DoorOfTime` flow and its gates (the stones,
   the Ocarina of Time, the Song of Time); patch song_only and open; logic for each; the settings string and CLI;
   test outputs per mode on a child save copy with fewer than three stones, with a checklist.

### Track C: `.nup` dumps in seed packs (`r10/nup`)

Owns `src/clawshot/pack/`, any NUP reader module, `docs/seed-pack.md`, the pack's `READ ME FIRST.txt`,
`plans/rounds/r10-nup.md`, section 42.
1. Make accepts a `.nup` file (the dump format Hookshot's builder, Lichii and EglantinePS5 read) as well as an
   extracted romfs folder. Use a55uka's NUP reader (MIT; a dependency if published, else vendored with its licence and a
   `NOTICE` entry). Version check first, from inside the `.nup`. Generation reads either source (a read-through layer,
   or a pack-local cache of only the files it needs, on the tester's own disk and never in a zip). Tests with a
   synthetic `.nup` fixture (no game data in the repository); a real read-only check against Kareem's `.nup` in
   `E:/Games/Hookshot`. Docs and the readme updated.

### Track D: pots and loose rupees (`r10/pots`, exploration)

Owns `plans/rounds/r10-pots.md`, section 43, any new `src/clawshot/patch/pots.py` and its tests.
1. Census the remake's pots, crates and loose (ground) rupees: actors, how a pot's drop is set, counts per area, and
   OoT Randomizer's names for them where they exist.
2. Find whether a pot or loose rupee can give a shuffled item through the game's own pickups (as round 8's boss hearts
   and floor heart pieces do, D33), and which items.
3. If it can: a `Pot` (and rupee) shuffle type behind the settings string, logic from OoT Randomizer's pot and rupee
   locations, tests and a test output with a checklist. If not: a report of what blocks it. Another randomizer
   (Lichii Discord) shuffles pot drops; its zip has no licence: never open, read or use it.

### Round 10 Track D result (merged `5653956`, docs only)

Pots (530), crates (50), ground rupees (112) and floor recovery hearts (25) censused (section 43,
`plans/rounds/r10-pots.md`). Kareem's tests: ground rupees and their replacements grant cleanly (Kokiri Piece of
Heart, grotto Hylian Shield); a pot's drop can be any native pickup, but a thrown pot drops where it breaks (a Piece
of Heart stranded on a tree, lost), and the game records only the pot's destruction, not the drop's collection.
Later-round candidates: (1) `Rupee` and `RecoveryHeart` shuffle types (all saved permanently, reset24, NoRespawn;
names: remake positions and regions, OoT Randomizer names only where exact; Saria's house has separate child and
adult hearts, so decide 7 or 14 checks); still to test: return and Save and Continue repeat steps. (2) Pots and
crates only with a per-pot D22 Bool set on collecting that pot's own drop, recoverable delivery (placed position or
direct grant), and ideally a marked pot model (eight native models exist; contrast unchecked), as Kareem described
Ship of Harkinian doing. No seed switch shipped.

### Round 10 result (2026-11-10)

All four tracks merged; main `809b421`. Last full review gates (track C, on top of A, B and D): 816 passed / 110
skipped, dump 109 (with `OOT_NUP`).
- A gifts: the seven frog checks, deterministic Bombchu Bowling (first win, second win, then filler) and the normal
  shooting-gallery prizes are in `--shuffle Gift`. Held until Kareem's tests pass (D15): the Market Potion Shop
  bottle (first build crashed on re-entry, R10-MARKET-BOTTLE; `market-bottle-fix-next` untested), Dampé's digging
  reward, the first expert gallery wins (Rupees (20), Kareem's choice). Launchers in `work/r10-gifts-cs10a/ingame`.
- B age travel: `free_time_travel` first-pull fix confirmed in game (R10-FIRST-PULL-FIXED). `door_of_time` =
  closed (default, D35) | song_only | open, with logic; all three passed a first in-game check on
  2026-11-10 (answers.md R10-DOOR-*); the early Zelda escape after an early pull is still untested. Adult
  songs now need the Ocarina of Time (from the item-bar age table, not an in-game test); seeds 8 and 10 re-checked
  beatable under it.
- C `.nup`: Make reads a `.nup` dump or a romfs folder; a55uka's reader vendored (MIT, `NOTICE`). The cache list is
  data (`pack/resources.toml`) and a dump test builds every shuffle kind and setting from the cache alone (16 rows,
  door modes included), naming any missing input.
- D pots: docs only, see "Round 10 Track D result".
- From play: the Goron City sign-puzzle solution chest is shuffled, its failure chest stays vanilla (`1432705`;
  165 of 184 chests shuffled). Test launchers enable Hookshot's cheat Teleport (`c3a5c0a`).

### After round 10 (candidates, not started)

- Going public (Kareem, 2026-11-10: "the right move once we clean things up"; his commit email stays as is). One
  docs track: README rewritten for newcomers (it still says "Day-1 spike" and "private tester packs"),
  `CONTRIBUTING.md` (MIT inbound, no game files or game-derived output, AI use disclosed, no unlicensed sources, how
  to run the gates), issue templates and a PR checklist, `docs/logic.md` for porters (world data, rule language,
  location IDs; an Archipelago port also needs a client that delivers items during play, which a RomFS mod cannot
  do), another randomizer author's name removed from this file. Then Kareem flips visibility; `main` protected;
  Greenferret added when he returns.
- Keysanity (Kareem, 2026-11-10; section 44 and R11-KEY-* answers). Played: a generic key
  outside a dungeon is lost; in keyless Deku or keyed Fire it credits that dungeon, including
  a native big chest and persistence on reload. The default own-dungeon mode therefore has
  plain-key evidence for both chest sizes. Named Forest writes from child/adult overworld
  small chests persist and open a native Forest lock; the later native key still counts.
  The named big-chest redirect in Deku **failed before opening**, not a generic-big-key failure.
  `--dungeon-items anywhere` remains refused by CLI/seed pipeline; settings/fill retain it.
  It still needs **(1)** a working named big-chest path plus the cross-dungeon pickup test,
  **(2)** pickup text identifying the target (English in every language, English dungeon names
  read from the dump at generation, never shipped), **(3)** the D38 Tracker tab reading the
  seed's own save. Arbitrary source binding and other named dungeon-item families remain
  outside these small-key proofs; no production keysanity release is claimed.
- A fresh public seed pack from merged main (seed 10's zip predates round 10; `.nup` support needs a new pack).

## Round 11 (going public; Hookshot 2.0.12+ loading; keysanity exploration; a UI base)

Kareem agreed, 2026-11-10 ("Yes please, go ahead", and asked for a UI base a contributor can build on,
cross-platform and close to Hookshot's interface). He tests and plays meanwhile: one worker process while
`hookshot.exe` runs, `CLAWSHOT_WORKERS=1` on every pytest run, the gate lock `work/rounds/r11/gate.lock` around full
gates. Four tracks, Bermuda thread `cs-r11`, herdr-core, all on `openai-codex/gpt-6.1-sol`; Claude reviews. New
sections of `plans/03-game-data.md`: 44 (B) and 45 (C); A and D write none. Shared files this round: `README.md`
belongs to A (other tracks post the text they need there on the thread); `docs/seed-pack.md` and the pack templates
to C; `pyproject.toml` and `uv.lock` to D. Test launchers: copy `E:/OOTRemake/tools/test-launcher-template.bat`
(outputs load as a mod, `plans/02-orchestration.md`), never an older launcher. No Hookshot build.

### Track A: going public (`r11/public`, documents only)

Owns `README.md`, `CONTRIBUTING.md`, `.github/`, `docs/logic.md`, `docs/settings.md`, `plans/rounds/r11-public.md`.
1. `README.md` for a newcomer: what Clawshot is and is not (unofficial, no game files, the player's own dump); status
   (what is shuffled today, only what is verified; what is built but held for in-game tests; known issues); playing a
   seed pack (link `docs/seed-pack.md`; Hookshot and emulators); running from source (uv, the commands, settings
   strings); how it is built (AI coding agents directed by Kareem, every change tested in game by him); contributing;
   the Discord invite `https://discord.gg/7R5ZXPcJqn`; credits (`NOTICE`) and licence. The "Day-1 spike" status and
   "Private tester packs" section go; the developer reference now in the README moves to `docs/settings.md`, not
   deleted.
2. `CONTRIBUTING.md`: contributions are MIT (inbound = outbound); no game files or anything generated from the game in
   a PR, issue or attachment (AGENTS.md rule 1); no code from GPL or unlicensed projects and none from NX2navi (rule 7);
   AI assistance is fine and is disclosed (`Assisted-by:` trailer); small single-topic PRs; the gate commands; what
   in-game evidence a behaviour change needs; where to ask. Kareem and his co-owner merge.
3. `.github/ISSUE_TEMPLATE/` (bug report: seed and settings string, runtime and version, where, expected and seen, the
   log; logic question; `config.yml` pointing to the Discord) and `.github/PULL_REQUEST_TEMPLATE.md` (the checklist).
4. `docs/logic.md` for someone porting the logic (an Archipelago world, a tracker): the world data files and remake
   overrides, the rule language, items, settings, location IDs, how a seed is proved beatable, the spoiler's fields,
   each statement with the path it comes from. Say what a multiworld port would still need: items delivered during
   play, which a RomFS mod cannot do without a hook in the runtime.
5. Housekeeping before the flip: the other randomizer author's name leaves `plans/00-roadmap.md` ("another
   randomizer"), one small commit; a scan of the tree for third parties' names or handles and for anything that
   should not be public, reported in the round file (history is not rewritten; Kareem keeps his commit email).

### Track B: keysanity exploration (`r11/keys`)

Owns `plans/rounds/r11-keys.md`, section 44, any new `src/clawshot/patch/keys.py` and its tests.
1. Trace, read only: where each dungeon's small-key and boss-key state is saved, what picking up
   `Item_Dungeon_SmallKey` and `Item_Dungeon_BossKey` writes (the dungeon Link stands in, or a named one) and what the
   locked doors read; the same for maps and compasses.
2. In-game experiments for Kareem (template launcher, checklists): a small key in an overworld chest, one in a chest
   of a dungeon that has no keys, one in another dungeon's chest; which counter moves, if any, and whether the item is
   lost. Choose saves from the save library by reading their flags.
3. If an event or saved-flag write can credit a named dungeon (as the gift patches write flags), prototype one
   per-dungeon key grant in a chest with a test output; otherwise report what blocks it.
4. Until an in-game test passes, building a seed with `dungeon_items = "anywhere"` stops with a message that says why
   (at the CLI and seed pipeline; the fill and its synthetic tests keep the mode).

### Track C: loading in Hookshot 2.0.12+ (`r11/loader`)

Owns `src/clawshot/pack/` (code, templates), `docs/seed-pack.md`, `plans/rounds/r11-loader.md`, section 45.
Facts: answers.md R11-HOOKSHOT-2012. Hookshot's release source is at
`C:/Users/hi/AppData/Local/HookshotBuilder/versions/<version>/HookshotBuilder/tools/` (GPL-3.0: read `host/mods.c` and
`host/prompts.c` for facts, cite them, never copy code).
1. The pack's Play starts the game with `HOS_MODS` (and `HOS_FS_OVERLAY` cleared) so that Hookshot sees exactly one
   mod, the made seed: no links, no second copy of the seed, and neither the `.nup` cache nor any other pack folder may
   count as a mod under Hookshot's rules (a test walks a made pack folder by those rules). A Hookshot without mods
   support must stop Play with a message, never start a vanilla game silently. Emulator steps stay as simple as now.
2. `READ ME FIRST.txt` and `docs/seed-pack.md`: the new known issue (button icons in text are the game's own while a
   seed is loaded); the Hookshot `mods` folder as the manual route and its warning (it uses the main save folder: a
   new game there overwrites the playthrough).
3. Smoke, no game start: a pack built from the romfs and from the `.nup`, Make on each, Play as a dry run printing
   what it would start; the digest unchanged by this track.
4. Report only: what Hookshot would need so a mod's size table keeps the controller icons (a candidate upstream PR).

### Track D: a UI base (`r11/ui`)

Owns `src/clawshot/app/`, `src/clawshot/ui/`, `tests/test_app*.py`, `tests/test_ui*.py`, `docs/ui.md`,
`plans/05-ui.md`, `plans/rounds/r11-ui.md`; `pyproject.toml` and `uv.lock` for one optional extra.
Toolkit (decided by Claude, 2026-11-10; Kareem can overturn): a local web front end, plain HTML, CSS and JavaScript
with no build step, served by a standard-library HTTP server on 127.0.0.1 and shown in an app window through
`pywebview` (BSD-3-Clause, optional extra `ui`) or, without it, the default browser. Reasons: rule 7 excludes Qt
(PySide6 is LGPL), HTML and CSS can follow HookshotBuilder's look closely and are what a UI contributor most likely
knows, and it runs on Windows, Linux, macOS and Steam Deck. Hookshot's own builder is WPF on Windows, with a PySide6
port and a tkinter Linux builder in its repository (GPL-3.0): the look comes from Kareem's screenshots, never from
Hookshot's code, XAML, images or logo.
1. `clawshot.app`, no UI code: a schema of every setting (key, label, kind, choices, default, help, group) built from
   `Settings` and `data/settings.toml`, so no front end hard-codes a setting; validation; the settings string both
   ways; detection of a dump (romfs folder or `.nup`) and of a Hookshot folder and version; a generation job that
   runs off the UI thread with progress stages, cancel and the fill's error text. Unit tests on synthetic worlds.
2. `python -m clawshot.ui`: one window in the manner of Hookshot's in-game menu (Kareem, 2026-11-10, after the first
   renders in the builder's slate look: "match the in-game menus a bit ... style close and remain clean overall"). A
   tan top band with tabs (Game, Settings, Generate), a dark-brown panel of label-and-value rows, amber section
   headers and focus, a description panel that shows the focused row's help text from the schema, a cards grid for
   what to shuffle, a key-hint bar; keyboard and mouse. Flat colours and CSS only: nothing from the game's art or
   fonts, no code or image from Hookshot (GPL-3.0); system font stacks; every asset local, no network request. The
   look's brief with Kareem's reference pictures is `E:/OOTRemake/work/rounds/r11/ui-look.md`. Paths are picked with
   a Browse dialog; a detected Hookshot folder fills in the dump; unavailable options are shown dimmed with their
   reason; plain titles, no slogans.
3. Safety: 127.0.0.1 only, a random port and a per-run token on every call, no cross-origin access, only the UI's own
   static files served, paths validated.
4. Tests through the HTTP server on a synthetic world; the schema test fails for a setting without metadata. Review
   screenshots of each screen from a headless browser into `E:/OOTRemake/work/r11-ui-cs11d/shots/`; no window may
   open on Kareem's screen (a `--no-open` switch; tests never open one).
5. `docs/ui.md` and `plans/05-ui.md`: the architecture, the calls, how to add a setting or restyle, what is not done:
   the base a contributor starts from.

### Track E: release the tested gift checks (`r11/release`; added 2026-11-10 after Kareem's gift tests)

Owns the two entries named below in `src/clawshot/data/world/remake/gifts.toml`, the tests that pin them,
`src/clawshot/pack/resources.toml` if the release reads files the cache lacks, the status lines about these two checks
in `README.md`, `docs/settings.md`, `docs/discord/server-kit.md` and `src/clawshot/pack/templates/READ ME FIRST.txt`,
`plans/rounds/r11-release.md`, and one new subsection at the end of section 40.
Facts: answers.md R10-MARKET-BOTTLE-FIX and R10-DIGGING (both confirmed in game), R10-MINIGAMES-ADULT (confirmed),
R10-MINIGAMES-CHILD (not run yet); section 40; `plans/rounds/r10-gifts.md`.
1. Release (D15) "Market Potion Shop Bottle" and "Graveyard Dampe Gravedigging Tour": remove their `keep_vanilla`
   holds, so `--shuffle Gift` shuffles both. The generator must write the patch Kareem tested and no other: build
   each with the placement of its test (Boomerang) and compare the changed flow files, decompressed, with the tested
   ones in `E:/OOTRemake/work/r10-gifts-cs10a/ingame/mods/market-bottle-fix-next/` and `.../digging-next/` (read
   only). A difference is reported in the round file and that check stays held.
2. Logic: with the bottle shuffled the early fixed bottle is no longer assumed; without Gift shuffle the model of
   section 40 stays. One sweep under the gate lock (seeds 1 to 50, seed 8's settings string and the default
   settings, at most one worker while the game runs): every seed beatable; report the check counts before and after.
3. Names, hints, play note: both locations keep their player-facing name and "where"; the hint classes cover them;
   a test fails if either is missing from the names catalogue.
4. Packs: the dump test that builds from the `.nup` cache alone covers both patches (it names any missing input).
   Seed 8 and seed 10 packs already built are pinned to the source they ship and are not rebuilt.
5. Status wording in the documents this track owns: both checks become shuffled with Gift and confirmed in game,
   with their answers ids.
Not in scope, still held or pending: the first expert gallery wins (untested), the bowling prizes and the child
gallery prize (enabled, Kareem's child test pending), the merchant experiments, Skulltula House rewards.


## Round 14 (tracker; Longshot; story fixes; progressive items)

Kareem agreed, 2026-11-13, after 0.2.0 was published ("all three or four are fine ... full speed ahead"). He is not
playing today apart from the checks a track asks for, so full gates may use `CLAWSHOT_WORKERS=3`; drop to 1 whenever
`hookshot.exe` or `longshot.exe` runs. One heavy job at a time under `work/rounds/r14/gate.lock`. Four tracks,
Bermuda thread `cs-r14`, herdr-core, all on `openai-codex/gpt-6.1-sol`; Claude reviews and merges, and bumps the
version (none of the tracks does). New sections of `plans/03-game-data.md`: 46 (C) and 47 (D); A and B write none.
Shared files: `README.md` and the pack templates belong to B (other tracks post the text they need on the thread);
`src/clawshot/ui/static/*` and `ui/server.py` are shared by A and B: B changes the Game tab and Play, A adds its own
tab and files and only small hooks in the shared ones. Merge order: B, C, D, A. Hookshot's GitHub repository has
been offline since 2026-11-13; Longshot (`git.magicbean.dev/MagicBeanDev/Longshot`, GPL-3.0, a fork of Hookshot) is
the active one. GPL sources (Hookshot, Longshot, sloperinaGZ): facts only, cited, never code.

### Track A: item tracker (`r14/tracker`, issue #16)

Owns a new `src/clawshot/tracker/` package, new tracker files under `src/clawshot/ui/static/`, `tests/test_tracker*.py`,
`docs/tracker.md`, `plans/rounds/r14-tracker.md`; small hooks in `ui/server.py`, `index.html`, `app.js`; one optional
dependency in `pyproject.toml`/`uv.lock` if icon decoding needs it.
1. `clawshot.tracker`, no UI code: from a seed's output (its spoiler and settings) and a save (`clawshot.save`), what
   the player holds (tiers, songs, stones and medallions, hearts, tokens), and per dungeon the small keys held and
   found out of the seed's total, plus boss key, map and compass; checks collected per area. D38: keys per dungeon
   first. Synthetic-save tests.
2. Which save: the seed's own save folder from Play, or a folder the player picks (Longshot and emulator players);
   the newest slot, with a choice. It updates on each game save without a reload.
3. A Tracker tab, and the same page standalone for an OBS Browser Source (compact, transparent option). Spoiler-free
   by default; showing locations is opt-in.
4. Icons decoded at run time from the player's own dump (`romfs/UI/Tex/Icon`), cached outside the repository, never
   shipped; flat CSS fallback without them. Own decoder from format facts or MIT/BSD libraries only.
5. One in-game check for Kareem: play a few chests with the tracker beside the game.

### Track B: Longshot (`r14/longshot`, issues #23 and #18)

Owns `src/clawshot/pack/hookshot.py`, `pack/runtime.py`, `app/play.py`, `app/paths.py`, `app/inputs.toml`,
`app/preferences.py`, the Game tab and Play in `ui/static/*`, `README.md`, `docs/ui.md`, `docs/seed-pack.md`, the pack
templates, `tests/test_app*.py`/`test_runtime*.py`/`test_hookshot*.py`, `plans/rounds/r14-longshot.md`.
1. Detect a Longshot game folder (`bin/longshot.exe`, `bin/longshot` on Linux, its version file) and a Longshot
   Launcher folder (its newest build), as well as Hookshot; the player can choose which.
2. Play starts the chosen game with the seed as its only mod, its own `--user` folder, and that game's update check
   off. Running-game detection knows both names.
3. Docs and templates name both, with the manual steps (mods folder, a New Game in an empty slot).
4. #18, short term: a "Copy for Discord" button (the string in backticks) and the backticks advice in the docs.
5. One in-game check for Kareem: Play a seed on Longshot from the app.

### Track C: story fixes (`r14/story`, issues #21 and #22)

Owns `src/clawshot/data/fast_start.toml`, the Hyrule Field, Market and Hyrule Castle world files, the matching
`patch/gamedata.py` changes, `tests/test_fast_start*.py` and new story tests, section 46, `plans/rounds/r14-story.md`.
1. #22: from the game data, the exact conditions of Zelda's escape after the three stones; then logic that requires
   them (or a fix that makes them always met), so no seed asks for an unreachable Ocarina of Time.
2. #21: what starts Hyrule Field's music, and a Kaepora skip that leaves it working.
3. Every offered fast-start combination still generates; sweep before handoff.
4. One in-game check for Kareem covering both.

### Track D: progressive items (`r14/progressive`, issue #13; replaces D16 for these items if it works)

Owns the item pool and fill changes, the chest-event patch for progressive grants, item names, hints and play-note
text for them, `tests/test_progressive*.py`, section 47, `plans/rounds/r14-progressive.md`.
1. Feasibility first, on Hookshot then Longshot from chests: a chest event that checks what is owned and grants the
   next tier, as 0.2.0's named small keys do; whether the model and name shown follow the granted tier.
2. Then the chains Kareem confirms (provisional: Hookshot, strength, scales, wallets; bags and magic if they fit),
   in every check kind that can carry them; others keep fixed items or are restricted, and say so.
3. Logic and fill treat progressive copies as counted tiers; the fixed-tier placement rule stays for fixed items.
4. Sweep and gates; one in-game check for Kareem.

### Track E: quest-step audit (`r14/steps`, issue #25; added 2026-11-13 at Kareem's request)

Owns section 48, `tests/test_story_steps*.py`, `plans/rounds/r14-steps.md`, and fixes only in world files no other track
owns this round. Kareem: "do we need to go through the rest of the quests/Threads of Time to make sure no other steps
are gating things we don't realize yet?" Three step gates were found by players (Mido, the Gerudo guards, Zelda's
escape).
1. A scripted census of every read and write of a quest step in the romfs (AI modules, event flows, GameData
   expressions and where they are used), with what each gates.
2. Each read classified against our logic and fast-start skips; flagged: logic granting access on an item where the
   game asks for a step, and steps advanced only by a native hand-over the randomizer replaces.
3. Section 48 and a full table; a failing test and a proposed fix for each confirmed mismatch. Track C keeps the
   Zelda, Door of Time and Kaepora fixes.

### After round 14

Done 2026-11-14; released as 0.2.1 the same day (tag `v0.2.1`, `5e16847`). All five tracks merged: B (Longshot
Detect and Play, carried-over game options; #18, #23, #24), C (Kaepora music, Met Child Zelda gating Zelda's escape,
Saria and the closed Door; #21, #22), D (progressive items, always on, chest copies only, D40; #13), A (tracker and
its OBS view; #16), E (quest-step audit: Zora's River walls, Epona, the Bombchu Shop, Darunia's gift, refused
logic-only overrides; #25), plus the forward-only Fire quest writes (#27). Every in-game check ran on Longshot (D41).
Not done here: the progressive chest's rising model still shows the base tier, and several copies granted inside one
chest event read stale ownership (seeds place one copy per chest).

## Round 15 (castle's pull requests; tracker overlay; free time travel in the app; scrub softlock; token shuffle)

Kareem agreed, 2026-11-14, after 0.2.1 was published: "we keep going". He plays the small-keys-anywhere community
seed 24 beside this round, so every gate uses `CLAWSHOT_WORKERS=1` while `longshot.exe` or `hookshot.exe` runs (3
otherwise), one heavy job at a time under `work/rounds/r15/gate.lock`, and the long dump gates go when he is away.
Nobody opens seed 24's spoiler or names its contents. Bermuda thread `cs-r15`, herdr-core, tracks on
`openai-codex/gpt-6.1-sol`; Claude reviews, merges and bumps the version. In-game checks run on Longshot (D41).

### Track A: castle's pull requests (`r15/castle`; #5, #4, #20, then #6)

Kareem: rebase them ourselves and keep castle's (mysterypaintwo) authorship; castle is not asked to do more. Each PR
is rebased onto main in its own stack (#5 then #6; #4 then #20). Conflicts are resolved inside castle's commits, so
he stays their author; adaptations to what main gained since 2026-11-12 (Longshot Detect and Play, the tracker,
progressive items, the quest-step fixes) are separate commits of the track's own. Each PR's own tests plus full
gates; #20 is checked read-only against Kareem's `.nx` dump; #6 changes the game and gets one in-game check. Claude
pushes the rebased stacks to the PR branches (maintainer edits are allowed) and merges, so each PR closes as merged.

### Track B: tracker overlay and free time travel in the app (`r15/ui`)

1. The OBS view is too wide and too big (Kareem, 2026-11-14). A vertical layout of a few columns, a column count
   option, and a toggle that hides names and tiers so icons sit close together. Dungeon keys, boss key, map and
   compass use the game's own icons (`Item_Dungeon_*` in `UI/Tex/Icon`) with the text fallback. The in-app tab's
   layout stays.
2. `free_time_travel` (CLI-only and experimental since 0.1.1) becomes an app setting with the same label and
   help, in the settings string as today.

### Track C: token shuffle, research and specification (`r15/tokens-spec`; clean room, step 1 of 2)

REALAZK reports (ootrr issue 6, 2026-11-14) that a generated Gold Skulltula token actor with a borrowed collection
callback works in game, and that an uncollected token makes the Skulltula come back. ootrr is GPL. Track C may read
it and our own dump and experiments (sections 11, 23 and 27, D27) and writes a facts-only specification; it writes
no Clawshot code. The implementer never opens ootrr. Credit "ootrr (REALAZK)".

### Track D: scrub softlock, then token shuffle from C's specification (`r15/scrub-tokens`)

1. #26: in the Lost Woods scrub grotto near Sacred Forest Meadow, one scrub offers nothing, and talking to it a
   second time leaves an invisible text box. Reproduce, find the cause, fix, and stage an in-game check.
2. After C's specification is accepted: Gold Skulltula tokens as a shuffle option, built only from that
   specification and our own sources (D never opens `E:/OOTRemake/work/refs/ootrr-azk` or ootrr on GitHub).
