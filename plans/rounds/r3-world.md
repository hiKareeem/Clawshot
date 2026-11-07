# Round 3, track C: world port (cs3c)

Branch `r3/world`, rebased on main `3dc8dbe` (track A's `keep_vanilla` in the fill). OoT Randomizer: the checkout in
`E:/OOTRemake/work/r2-world/OoT-Randomizer` at `526b4c8d81b7c4023ef4573ffbaf39344e270d5b` (NOTICE); MIT files only,
nothing from `bin/` or `Notes/`. Scratch scripts (research and timing, read-only on the dump) are in
`E:/OOTRemake/work/r3-world/`.

## What is on the branch

| Item | Where | State |
|---|---|---|
| 1 Port of the whole world | `port.toml`, 35 region files in `src/clawshot/data/world/`, `NOTICE` | done: every region of `Overworld.json`, `Bosses.json` and the 12 vanilla dungeons; 342 regions, 1370 locations, 257 events; no dangling exit, no undefined event |
| 2 Remake overrides, apart from the translation | `src/clawshot/data/world/remake.toml`, `world.load.apply_overrides` | done (list below) |
| 3 Vanilla beatable; 200 default seeds beatable | `tests/test_world_data.py` | done (vanilla with the key caveat below) |
| 4 Every covered location linked or N64-only, pending list printed | `tests/test_world_census.py` | done: 237 pending (list below) |

Engine changes the whole world needed (`src/clawshot/world/`, `plans/04-world-format.md`):

- **Overrides file** (`world.toml` `overrides = "remake.toml"`): per location `rule` (with `was`, the translated rule
  it replaces: a change upstream stops the build), `type`, `vanilla`, `vanilla_fixed`, `n64_only`, `area`,
  `keep_vanilla`, each with a required `source`; `[key_counts]` caps a rule's key count. The translated files hold
  no hand field any more (round 2's `vanilla_fixed`/`n64_only` moved to `remake.toml`), so the translator test
  translates `port.toml` into an empty folder and compares bytes.
- **Location** gains `area` (census area; the region's unless overridden), `keep_vanilla`, `override` (source).
  **World** gains `start_items`.
- **Translator**: reports `regions_not_ported`; fixes two `World` attributes OoT Randomizer draws at random
  (`skipped_trials`: all six trials active at `trials = 6`; `selected_adult_trade_item`: `Pocket Egg`). Before the
  fix, two runs wrote different `settings.toml` files (printed diff: `selected_adult_trade_item` `"Prescription"`
  against `"Pocket Egg"`).
- **Rules**: `has_all_notes_for_song`/`has_ocarina_buttons` (true while notes are not shuffled: OoT Randomizer then
  collects every button at the start, `ItemPool.py` `get_pool_core`), `region_has_shortcuts` (false with no
  shortcuts), `skipped_trials[Forest]` (table settings), `provides_time = "dampe"` (OoT Randomizer's name for the
  night bit). Each compiled rule records the item and event names it reads (`Rule.reads`).
- **Start items** (`load._start_items`, from `ItemPool.get_pool_core`): the ocarina buttons, Scarecrow's Song when
  free, and one Fire Temple small key while `keysanity` is false (its rules say `(Small_Key_Fire_Temple, 8) or (not
  keysanity)`). Without the buttons the vanilla world failed at once (printed: `LW Ocarina Memory Game` asks for
  `Ocarina_A_Button` ...; 265 placed items unreached).
- **Search speed**: the whole world made a seed take 1.8 s (profile: `collect_spheres` re-testing every location
  each sphere, failed exits retried at every update). Now a failed exit, event or location waits until a count its
  rule reads grows or its region is reached anew: 0.72 s a seed, same spheres. The 200-seed test runs in worker
  processes: about 45 s for 200 fixed-item and 20 progressive seeds.

## Overrides (`remake.toml`), each with its source

| Location(s) | Override | Source |
|---|---|---|
| LW Gift from Saria, LW Target in Woods, HF Ocarina of Time Item, LH Adult Fishing, ZD Diving Minigame, Kak 10 / 30 Gold Skulltula Reward, GC Darunias Joy, Graveyard Dampe Race Hookshot Chest, Water Temple Longshot Chest, Spirit Temple Silver Gauntlets Chest, Ganons Castle Shadow Trial Golden Gauntlets Chest | `vanilla_fixed` (Fairy Ocarina, Bullet Bag (40), Ocarina of Time, Golden Scale, Silver Scale, Adult Wallet, Giant Wallet, Goron Bracelet, Hookshot, Longshot, Silver Gauntlets, Golden Gauntlets) | D16; census items for the chests; 03-game-data section 4 for the wallets |
| Spirit Temple Silver Gauntlets Chest, Spirit Temple Mirror Shield Chest | `area = "DesertColossus"` | 03-game-data section 9 ("Moved"), census |
| DMT Great Fairy Reward / HC Great Fairy Reward | `vanilla` Dins Fire / Magic Meter | Kareem in game, 03-game-data section 9 |
| Fire Temple GS Boss Key Loop | `True` -> `can_use(Megaton_Hammer)` | 03-game-data section 9, Eurogamer guide |
| OGC GS | `True` -> `can_use(Hookshot)` | 03-game-data section 9, Eurogamer guide |
| HF GS Near Kak Grotto | adds `has_explosives` | track B 18:06 (the remake's grotto in HF's southern woods, opened with explosives) |
| Graveyard Dampe Race Freestanding PoH | `type = "Chest"` | census: one of the four race goal chests |
| HF GS Cow Grotto, LLR GS Rain Shed, LLR GS Back Wall | `n64_only` | track B 18:06 |
| LW Near Shortcuts Grotto Chest | `n64_only` | round 2 census |
| Gerudo Training Ground Freestanding Key | `n64_only` | 03-game-data section 9, census (all 9 GTG keys in chests) |
| the six N64 Ice Trap chests | `n64_only` (trap chests, no item; D10) | 03-game-data section 2 |
| the nine cows | `n64_only` (no per-cow flag; D11) | 03-game-data section 5 |
| Market Treasure Chest Game Room 1-5 Top/Bottom | `keep_vanilla` | D17 |
| Small Key (Bottom of the Well) 2, (Water Temple) 4, (Ganons Castle) 1 | `[key_counts]` | census key counts; chain locks below |

**Key counts, how found** (`E:/OOTRemake/work/r3-world/keys.py` on the census, `doors.py` on the dump's Static
files): small keys per dungeon, census against OoT Randomizer: BotW 2/3, Fire 8/8, Forest 5/5, Ganon's Castle 1/2,
GTG 9/9 (all chests here; 8 chests + freestanding there), Shadow 5/5, Spirit 5/5, Water 4/6, Hideout 4/4 (8
actors). `Obj_DoorChainLock_A_01` actors (one per side of a door): BotW 4, Water 8, Ganon's Castle 2, Forest 10,
GTG 18, i.e. as many doors as keys; Fire (16, mostly `_A_04`), Shadow (9) and Spirit (9, `Obj_SpiritTemple_...`)
do not pair this cleanly. The capped rules: BotW `Behind Locked Doors` 3 -> 2; Ganon's `Light Trial Boulder Room`
2 -> 1; Water Temple, five rules asking for 5 -> 4 (GS Central Pillar, Middle Water Level, Central Pillar Chest, Boss
Key Chest Room, Dark Link Region). The cap is safe as long as the remake's locked doors are N64 doors (no door then
needs more than OoT Randomizer's worst-order count or more than the dungeon holds).

**Remake GS changes the guide states but not applied** (provisional: no item named that OoT Randomizer lacks, or
unclear): Forest Temple east-garden GS needs Scarecrow's Song and the Hookshot in the remake (OoT Randomizer's rule
also allows the Boomerang trick and a route from the falling room); Shadow Temple rotating-skull GS ("blow up the
skull": explosives?) is `Shadow Temple GS Triple Giant Pot` or `... Single Giant Pot`, not settled; DMT GS Falling
Rocks Path needs the Hammer in the remake, which OoT Randomizer's rule already asks.

## How it was checked

| Command | Result |
|---|---|
| `uv run python -m clawshot.world.translate --ootr E:/OOTRemake/work/r2-world/OoT-Randomizer` | 35 files, `regions_not_ported: []`, 54 hints left out, 156 helpers, 286 items, 51 settings / 160 tricks / 9 flags |
| `OOTR_DIR=E:/OOTRemake/work/r2-world/OoT-Randomizer uv run pytest tests/test_world_translate.py` (3 runs) | passed each time |
| `uv run pytest tests/test_world_data.py tests/test_generate.py` | 17 passed in 47 s (200 fixed-item seeds, 20 progressive, spoiler bytes equal across hash seeds) |
| `uv run pytest -s tests/test_world_census.py` | 4 passed; prints the pending list below |
| gates | end of this file |

**Vanilla placement.** With every check at its vanilla item the goal is *not* reached in OoT Randomizer's own logic:
printed, the Spirit Temple's Silver Gauntlets chest asks `(Small_Key_Spirit_Temple, 5) or (has_explosives and
Longshot and (Small_Key_Spirit_Temple, 3))`, and the vanilla child side holds 2 keys, so adult never gets past the
Spirit Temple lobby (and Ganon's bridge needs the Spirit Medallion). OoT Randomizer counts keys for the worst door
order; its vanilla layout is not provably enough. With 3 extra Spirit keys the goal holds and the only unreached
checks with items are `Kak 100 Gold Skulltula Reward` (97 tokens) and `Gerudo Training Ground Maze Path Final Chest`
(8 keys in the pool, rules ask 9). The test therefore holds each dungeon's small keys from the start and checks the
goal, `Time Travel`, Ganondorf's room as adult and every chest reached; key logic is tested by the seeds.

## Pending list (item 4)

237 covered locations with no census link and no `n64_only` (against `locations.toml` on main at `3dc8dbe`; track
B's Gold Skulltula links will remove most of the 97 GS). `MAX_PENDING = 237` in the test.

```
BottomOfTheWell (12): Front Center Bombable, Underwater Left, Underwater Front, Invisible, Front Left Fake Wall,
  Right Bottom Fake Wall, Center Skulltula, Back Left Bombable, Like Like chests; GS West Inner Room, East Inner
  Room, Like Like Cage
DeathMountainCrater (9): Wall and Volcano Freestanding PoH; GS Crate, Bean Patch; DMC Deku Scrub; Upper Grotto
  Chest; Deku Scrub Grotto Left, Right, Center
DeathMountainTrail (5): GS Bean Patch, Near Kak, Above Dodongos Cavern, Falling Rocks Path; Storms Grotto Chest
DesertColossus (5): GS Bean Patch, Tree, Hill; Deku Scrub Grotto Rear, Front
DodongoCavern (11): Deku Scrubs Lobby, Side Room Near Dodongos, Near Bomb Bag Right, Left; GS Side Room Near Lower
  Lizalfos, Scarecrow, Vines Above Stairs, Alcove Above Stairs, Back Room; End of Bridge Chest; Boss Room Chest
FireTemple (15): Near Boss, Flare Dancer, Big Lava Room Lower Open Door, Blocked Door, Boulder Maze Lower, Side Room,
  Upper, Shortcut, Scarecrow, Highest Goron chests; GS Boss Key Loop, Song of Time Room, Boulder Maze, Scarecrow
  Climb, Scarecrow Top
ForestTemple (14): First Room, First Stalfos, Well, Raised Island Courtyard, Eye Switch, Floormaster, Red Poe,
  Falling Ceiling Room, Basement chests; GS First Room, Lobby, Level Island Courtyard, Raised Island Courtyard,
  Basement
GanonCastle (1): OGC GS
GerudoFortress (7): GF GS Archery Range, Top Floor; GF Freestanding PoH; Hideout 1-4 Torch(es) Jail Gerudo Key
GerudoTrainingGround (17): Lobby Left, Lobby Right, Stalfos, Beamos, Hidden Ceiling, Maze Path Second, Third,
  Underwater Silver Rupee, Maze Right Side, Before Heavy Block, Near Scarecrow, Heavy Block First, Second, Third, Eye
  Statue, Hammer Room Clear, Switch chests
GerudoValley (9): GS Small Bridge, Bean Patch, Behind Tent, Pillar; Waterfall and Crate Freestanding PoH; GV Chest;
  Deku Scrub Grotto Rear, Front
GoronCity (9): Maze Left, Center, Right chests; GS Boulder Maze, Center Platform; Pot Freestanding PoH; Deku Scrub
  Grotto Left, Right, Center
Graveyard (4): Dampe Gravedigging Tour; GS Wall, Bean Patch; Royal Familys Tomb Chest
HountedWasteland (1): Wasteland GS
HyruleCastle (2): HC GS Tree, Storms Grotto
HyruleField (18): HF Southeast, Open, Near Market Grotto chests; HF GS Near Kak Grotto; HF Tektite Grotto
  Freestanding PoH; LLR GS Tree, House Window; LLR Deku Scrub Grotto Left, Right, Center; LH GS Bean Patch, Lab
  Wall, Small Island, Tree, Lab Crate; LH Deku Scrub Grotto Left, Right, Center
IceCavern (4): GS Spinning Scythe Room, Heart Piece Room, Push Block Room; Freestanding PoH
InsideGanonCastle (13): Forest Trial, Water Trial Right, Shadow Trial Front, Light Trial First Left, Third Left,
  Second Right, Invisible Enemies, Lullaby, Spirit Trial Invisible chests; Deku Scrubs Left, Center-Left,
  Center-Right, Right
InsideJabuJabuBelly (4): GS Water Switch Room, Lobby Basement Lower, Lobby Basement Upper, Near Boss
InsideTheDekuTree (4): GS Compass Room, Basement Gate, Basement Vines, Basement Back Room
KakarikoVillage (8): GS House Under Construction, Skulltula House, Near Gate Guard, Tree, Watchtower, Above Impas
  House; Redead Grotto Chest; Open Grotto Chest
KokiriForest (3): GS Know It All House, Bean Patch, House of Twins
LostWood (3): GS Bean Patch Near Bridge, Above Theater, Bean Patch Near Theater
Market (1): Market GS Guard House
SacredForestMeadow (3): SFM GS; Deku Scrub Grotto Rear, Front
ShadowTemple (17): Early Silver Rupee, Invisible Blades Visible, Invisible, Falling Spikes Lower, Upper, Switch,
  Invisible Spikes, Wind Hint, After Wind Enemy, Hidden, Invisible Floormaster, Spike Walls Left chests; GS
  Invisible Blades Room, Falling Spikes Room, Single Giant Pot, Near Ship, Triple Giant Pot
SpiritTemple (17): Child Bridge, Child Early Torches, Early Adult Right, Child Climb East, Sun Block Room, First
  Mirror Right, Statue Room Hand, Northeast, Near Four Armos, Hallway Left and Right Invisible, Topmost chests; GS
  Metal Fence, Boulder Room, Sun on Floor Room, Lobby, Hall After Sun Block Room
WaterTemple (11): Torches, Central Pillar, Cracked Wall, Central Bow Target, River, Dragon chests; GS Central
  Pillar, Behind Gate, Near Boss Key Chest, Falling Platform Room, River
ZoraDomain (1): ZD GS Frozen Waterfall
ZoraFountain (3): ZF GS Tree, Above the Log, Hidden Cave
ZoraRiver (6): ZR GS Tree, Ladder, Near Raised Grottos, Above Bridge; Deku Scrub Grotto Rear, Front
```

The grotto scrubs (23) are pending, not N64-only: round 2's census found none of them, but Kareem was asked whether
the remake removed them (r2-census question 2) and the answer is not recorded.

## Provisional choices (for review)

1. **Overrides file, not hand edits**: everything hand-written about a location lives in `remake.toml`, including
   round 2's `vanilla_fixed` and `n64_only`, so translated files are pure translator output.
2. **Key caps** (`[key_counts]`) rather than rewriting each key rule: which N64 doors the remake removed is unknown,
   and the cap is safe while the remake's doors are N64 doors.
3. **Vanilla items stay OoT Randomizer's** except where an override says otherwise: the Water Temple pool keeps 6
   keys (4 needed), the GTG pool 8 (rules ask up to 9: `Maze Path Final Chest` is out of logic, so it only ever gets
   a non-progression item), ammo and recovery hearts where the remake has rupees. A chest's remake contents need
   every chest linked and an actor-to-item mapping (track A's `item_actors.toml`); round 4.
4. **Dampé race heart piece as a Chest** (`type` override): the remake places it in a race goal chest, so the
   chest shuffle (D15) shuffles it like the race's Hookshot chest. Its `GetEventName`
   (`MiniGame_DampeRace_OpenGoalTBox`) records the race state; the in-game swap is untested.
5. **Cows N64-only** (D11): their `Milk` is never placed; no rule reads `Milk`.
6. **Start items as OoT Randomizer's**, including the free Fire Temple key while `keysanity` is false. A seed with
   `dungeon_items = "anywhere"` should set logic `keysanity = true` (posted for track A).
7. **Vanilla-placement test with keys held** (above), since OoT Randomizer's worst-order key logic cannot prove its
   own vanilla Spirit Temple.
8. **HF GS Near Kak Grotto** asks for explosives on the location (the region's entrance still allows the Hammer as
   N64's does); the remake's grotto is elsewhere, so its entrance rule is a guess either way.

## Questions for Kareem

1. **Grotto Deku Scrubs: did the remake remove them (Goron City, SFM, Zora's River, Gerudo Valley, Colossus, Lake
   Hylia's and Lon Lon Ranch's grottos, DMC's, Ganon's Castle)?** They stay pending until then (round 2 asked too).
2. **Forest Temple, east garden: is the Gold Skulltula reachable only by the scarecrow and the Hookshot, or also
   from the upper ledge or with the Boomerang as on N64?** Until then the N64 rule stands.
3. **Shadow Temple, the Gold Skulltula behind a rotating skull: do you need bombs for it?**

## Cross-track posts (thread `cs-r3`)

- 18:10: request to track A: leave `keep_vanilla` locations out of the shuffle (done in `3dc8dbe`).
- 18:23: port on the branch; start items and `keysanity` for `dungeon_items = "anywhere"`; goal `Triforce`;
  Dampé chest type; census test bound and `treasure_game_reward`.

## Left for later

- The three new remake Gold Skulltulas (HF tree by the forest entrance 2177746409373494991, adult HF grotto crate
  9047381233010434881, LLR tower vines 2730878115209290675) need regions and rules once track B's names are on main;
  until then `Kak 100 Gold Skulltula Reward` is out of logic (97 tokens).
- The pending list above (dungeon chests with repeated items, Gold Skulltulas, grotto scrubs).
- GTG's ninth key: which OoT Randomizer chest holds it in the remake (a chest link).
- Event gifts and their vanilla items (round 4).

## Gates

```
uv run ruff format --check                                   52 files already formatted
uv run ruff check                                            All checks passed!
uv run pytest                                                131 passed, 7 skipped in 43.78s
OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump      6 passed, 132 deselected in 23.77s
```

The 7 skipped are the dump tests and the translator test without `OOTR_DIR`; with it, the translator test passes
(above).
