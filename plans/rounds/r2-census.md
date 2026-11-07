# Round 2, track A: census (cs2a)

Branch `r2/census`, from main `252b19c`. Owns `src/clawshot/census/`, `src/clawshot/data/locations.toml`,
`tests/test_census*.py` and this file.

## What was built

| Path | What |
|---|---|
| `src/clawshot/census/scan.py` | `scan(romfs) -> list[Location]`, and `scan_trees(banc, flags)` (the same over parsed trees, for tests) |
| `src/clawshot/census/ootr.py` | reads OoT Randomizer's `LocationList.py` as data (`ast`, nothing executed, Master Quest dropped) and links census locations to its names |
| `src/clawshot/census/definitions.py` | reads and writes `locations.toml` (`load()`, `Definition`) |
| `src/clawshot/census/write_locations.py` | `python -m clawshot.census.write_locations --romfs <dir> --ootr <LocationList.py> [--out] [--fresh]` |
| `src/clawshot/data/locations.toml` | 477 locations, 235 with an `oot_randomizer_name` |
| `tests/test_census.py` | synthetic: merging, kinds, exclusions, errors, a synthetic romfs with a big-endian `GameDataList`, the matcher rules, the TOML file |
| `tests/test_census_dump.py` | `-m dump`: `locations.toml` and `scan()` agree on ids, kinds, areas and vanilla items |

**`Location`**: `id` (actor `Hash`), `kind`, `area` (Banc folder), `room` (`Dynamic.DefaultDungeonRoomIndex`, dungeon
actors only), `files` (every placement file holding the Hash), `ages` (`child`/`adult` from `_Child_`/`_Adult_` in the
file names; a file without an age, as in dungeons, counts as both), `position` (`Translate` from the first file),
`actor` (`Gyaml`), `vanilla_item`, `event` (`GetEventName`), `has_save_flag` (a `Bool64bitKey` with the Hash), and
`shop_slot` for shop slots.

Kinds and what `vanilla_item` is:

| kind | actors | vanilla_item |
|---|---|---|
| `chest` | `Obj_TBox_*` except `Obj_TBox_A_04*` (trap, D10); pedestals are `Obj_TBoxPedestal_*` and hold nothing | `Drop__DropActor`, else `Obj_Rupee_Green` (the chest blackboard default, 03-game-data section 2) |
| `treasure_game_box` | `Obj_HrlCity_Shop_TBox_*` | `Drop__DropActor` |
| `gold_skulltula` | `Enemy_Skulltula_Gold` | `Obj_Token_Gold` |
| `freestanding` | `Obj_Heart_Piece`, `Obj_GerudoValley_Heart_Piece`, `Obj_Dungeon_SmallKey`, `Obj_Dungeon_SmallKey_GerudoFortress_01..04` | the actor itself (all are `PouchActorInfo` rows) |
| `heart_container` | `Obj_Heart_Container` | the actor |
| `scrub` | `Enemy_Scrub_Business` | `ScrubBusiness_ShopItemActorName0`; empty for the 3 scrubs that name none (their talk event holds the item) |
| `shop_slot` | `Shop_*` except `Shop_Board_*` | the actor |

`DreamWorld` is skipped (D12); cows are not a kind (D11). The scan raises if one Hash is placed as different actors,
with different `Dynamic` parameters, in two areas or more than 0.01 apart (two Gold Skulltulas differ by float noise
below that between their child and adult copies).

**`locations.toml`**: fields `id`, `kind`, `area`, `name`, `vanilla_item`, `oot_randomizer_name`. `id` is a decimal
string, because 255 of the 477 Hashes are above TOML's signed 64-bit integer range. The writer keeps `name` and
`oot_randomizer_name` of every id already in the file, so hand edits survive a rewrite (`--fresh` drops them);
rewriting the committed file from the dump reproduces it byte for byte.

## How it was checked

- `uv run python -m clawshot.census.write_locations --romfs E:/Games/Hookshot/romfs --ootr
  E:/OOTRemake/work/r1-research/LocationList.py --fresh`: 477 written; new names by basis `item` 70, `residual` 4,
  `shop slot` 128, `treasure game room` 11. Then 18 hand links (below), then the same command without `--fresh`:
  "477 kept their names", output byte-identical to the hand-edited file (`cmp`).
- The four gates, last run before the handoff: see the end of this file.
- `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump`: `test_definitions_agree_with_the_census` passes.
- Chest counts per area equal `03-game-data.md` section 1 and 9 in every area (184 chests + 12 treasure-game boxes =
  196); 100 Gold Skulltulas; every chest, Gold Skulltula, scrub, heart container and treasure-game box has a save flag.

OoT Randomizer: `LocationList.py` from `Dev` at `526b4c8d81b7c4023ef4573ffbaf39344e270d5b` (the copy in
`E:/OOTRemake/work/r1-research/`). Without Master Quest it has 1449 locations; the kinds compared here are Chest (179,
of which 11 Treasure Chest Game), GS Token (100), Collectable (28: heart pieces and keys), BossHeart (8), Scrub and
GrottoScrub (36), Shop and MaskShop (72). (Section 9 of 03-game-data says 1404 and 175 chests; I count 1449 and 179
with "Master Quest without Vanilla Dungeons" as the MQ test, and did not chase the difference.)

## Census counts

| Banc area | chest | tgame | GS | free | HC | scrub | shop | total | chests in 03 | OoTR (no GS, no shop) | linked |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BottomOfTheWell | 12 | 0 | 3 | 1 | 0 | 1 | 0 | 17 | 12 | 14 | 5 |
| DeathMountainCrater | 2 | 0 | 2 | 2 | 0 | 1 | 0 | 7 | 2 | 7 | 0 |
| DeathMountainTrail | 1 | 0 | 4 | 1 | 0 | 0 | 0 | 6 | 1 | 3 | 2 |
| DesertColossus | 3 | 0 | 3 | 1 | 0 | 0 | 0 | 7 | 3 | 5 | 3 |
| DodongoCavern | 9 | 0 | 5 | 0 | 1 | 1 | 0 | 16 | 9 | 11 | 5 |
| FireTemple | 16 | 0 | 5 | 0 | 1 | 0 | 0 | 22 | 16 | 15 | 5 |
| ForestTemple | 12 | 0 | 5 | 0 | 1 | 0 | 0 | 18 | 12 | 14 | 5 |
| GanonCastle | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| GerudoFortress | 2 | 0 | 2 | 8 | 0 | 0 | 0 | 12 | 2 | 6 | 1 |
| GerudoTrainingGround | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 22 | 22 | 22 | 3 |
| GerudoValley | 6 | 0 | 4 | 1 | 0 | 0 | 0 | 11 | 6 | 5 | 0 |
| GoronCity | 6 | 0 | 2 | 0 | 0 | 0 | 16 | 24 | 6 | 7 | 0 |
| Graveyard | 6 | 0 | 2 | 1 | 0 | 0 | 0 | 9 | 6 | 7 | 5 |
| HountedWasteland | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 2 | 1 | 1 | 1 |
| HyruleCastle | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| HyruleField | 7 | 0 | 11 | 2 | 0 | 5 | 0 | 25 | 7 | 13 | 3 |
| IceCavern | 4 | 0 | 3 | 0 | 0 | 0 | 0 | 7 | 4 | 4 | 3 |
| InsideGanonCastle | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 12 | 20 | 3 |
| InsideJabuJabuBelly | 4 | 0 | 4 | 0 | 1 | 1 | 0 | 10 | 4 | 5 | 5 |
| InsideTheDekuTree | 6 | 0 | 4 | 0 | 1 | 0 | 0 | 11 | 6 | 7 | 7 |
| KakarikoVillage | 3 | 0 | 6 | 2 | 0 | 0 | 32 | 43 | 3 | 4 | 2 |
| KokiriForest | 7 | 0 | 3 | 0 | 0 | 2 | 24 | 36 | 7 | 6 | 6 |
| LostWood | 1 | 0 | 3 | 0 | 0 | 9 | 0 | 13 | 1 | 6 | 5 |
| Market | 0 | 12 | 1 | 0 | 0 | 0 | 32 | 45 | 12 | 11 | 11 |
| SacredForestMeadow | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 3 | 2 | 3 | 1 |
| ShadowTemple | 14 | 0 | 5 | 1 | 1 | 1 | 0 | 22 | 14 | 18 | 6 |
| SpiritTemple | 14 | 0 | 5 | 0 | 1 | 0 | 0 | 20 | 14 | 18 | 5 |
| WaterTemple | 9 | 0 | 5 | 0 | 1 | 0 | 0 | 15 | 9 | 11 | 5 |
| ZoraDomain | 1 | 0 | 1 | 0 | 0 | 0 | 24 | 26 | 1 | 1 | 1 |
| ZoraFountain | 1 | 0 | 3 | 2 | 0 | 0 | 0 | 6 | 1 | 2 | 2 |
| ZoraRiver | 1 | 0 | 4 | 2 | 0 | 0 | 0 | 7 | 1 | 5 | 3 |
| **total** | 184 | 12 | 100 | 24 | 8 | 21 | 128 | 477 | 196 | 251 | 103 |

"chests in 03" = chests + treasure-game boxes from `03-game-data.md` sections 1 and 9: equal in every row. "OoTR" =
OoT Randomizer locations of the compared kinds in that area, without Gold Skulltulas and shops (Gold Skulltulas are
never linked, shops are all linked). The Spirit Temple's Silver Gauntlets and Mirror Shield chests are counted under
`DesertColossus`, where the remake places them. Shops are 72 OoT Randomizer slots (8 shops and the mask shop, x 8),
all linked, against 128 remake actors, because every slot is a separate actor in each file and stock variant.

Ages: chests 168 both / 14 adult / 2 child; Gold Skulltulas 59 both / 25 child / 16 adult; freestanding 12 both / 11
adult / 1 child; shop slots 64 child / 64 adult. Save flags: every check has one except 10 freestanding items (the
Bottom of the Well key and all 8 Gerudo Fortress key actors; the Shadow Temple key has one) and 64 of 128 shop actors
(mostly bottles, masks, Bombchus and tunics).

## Linking OoT Randomizer names

Rules in `ootr.match` (in order; a location keeps the first that applies):

1. **Shop slot**: shop actors of an area within 3 units of each other form one shop, named by area and contents
   (Market: Bombchu shop, mask shop, potion shop by its bottles, the bazaar; Kakariko: potion shop, bazaar). Slot `n`
   (`ShopItemIndex`, absent = 0) is OoT Randomizer's `<shop> Item n+1`. **This is a numbering convention, not a
   physical match**: the remake's shelves hold different items in a different order from N64 (Goron shop: N64 slots
   1-4 bombs, here slots 4-7). For logic it is harmless (all slots of a shop share one region and rule); for vanilla
   shop contents use the remake's items.
2. **Treasure game room**: the five rooms are pairs of boxes at one x coordinate; counted from the farthest from the
   two reward boxes (room 1) to the nearest (room 5). The key box is "Top", the other "Bottom" (as OoT Randomizer's
   vanilla items have it). The remake's rupees grow green, green, green, blue, blue in that order and the room-5 key
   box plays `MiniGame_ChoiceTreasure_OpenLastHitTreasureBox`, which fixes the direction. The Heart Piece reward box
   is the "Reward"; the red-rupee box at the same spot (presumably once the Heart Piece is taken) has no counterpart.
3. **Item**: in one area and kind, the only remake spot of an item family facing the only OoT Randomizer location of
   that family (families: `Item_Dungeon_SmallKey` and "Small Key (Fire Temple)" are both "Small Key", Hookshot and
   Longshot both "Progressive Hookshot", rupees by value, ammo without count, and so on; `ootr.remake_family`,
   `ootr.ootr_family`).
4. **Residual**: an area and kind with equal counts on both sides where all but one pair matched by item: the last
   pair (4: Wasteland Chest, LW Near Shortcuts Grotto Chest, ZR Open Grotto Chest, Jabu Jabus Belly Deku Scrub; the
   LW one was then removed by hand, below).

A spot is one actor plus its copies under other Hashes in other files (same area, kind, actor, item and position):
copies share the name. Gold Skulltulas are not linked (Kareem: the remake moved them; 03-game-data section 9).

**By hand** (20 links and 1 removal; applied with a throwaway script, `E:/OOTRemake/work/r2-census/hand_matches.py`;
evidence from positions and the actors placed around each one):

| OoT Randomizer name | id | evidence |
|---|---|---|
| KF Midos Top Left / Top Right / Bottom Left / Bottom Right Chest | 9725242744547055868 / 4555665598794293658 / 10831981390482426294 / 12786193094758345086 | the four `KokiriForest_TreasureBox_NaviChatOff` chests stand 2x2 (rows at z -40.9 and -42.0); the only green rupee (N64 Bottom Left: Rupee (1)) fixes its row as "bottom" and its side (larger x) as "left" |
| Deku Tree Slingshot Room Side Chest | 13027331340815880287 | room 2, the Slingshot chest's room |
| Deku Tree Compass Room Side Chest | 11368028582977069031 | room 3, the Compass chest's room |
| Deku Tree Basement Chest | 12889104996486369065 | room 4, y 79 against 108-125 for the others; the last of six on both sides |
| LLR Freestanding PoH | 9814903750835309225 | child only, among `Land_LonLon_*` actors, next to a `CrawlAnchor` and an `IndoorAreaBox` |
| LH Freestanding PoH | 13469300937852836203 | adult only, on `Land_LakeHrl_HouseOutside` (the lab) |
| Kak Windmill Freestanding PoH | 13389209437182306002 | among `Land_Kakariko_WindmillHouse` actors and `BGM_WindmillHouse_Adult` |
| Kak Impas House Freestanding PoH | 17926402522258180222 | 5 units from an `Animal_Cow`, 8 from a bed |
| ZF Bottom Freestanding PoH | 8030885465575590602 | y 70.9 (the other is 103.1), beside fallen and dead tree actors |
| ZF Iceberg Freestanding PoH | 12406896586250888098 | among `Land_ZoraFountain_Snow`/`Rubble` actors at the water line |
| ZR Near Domain Freestanding PoH | 4189391771527808272 | about 46 units from `Land_ZoraRiver_VillageEntrance_A_01`, at the upper waterfalls |
| ZR Near Open Grotto Freestanding PoH | 11455676800795329345 | the lower river, 38 units from the grotto entrance |
| Graveyard Freestanding PoH | 2157466067026784951 | the only freestanding one; 7 units from a soft-soil patch (`Obj_SmallFarm_A_01`) |
| Graveyard Dampe Race Freestanding PoH | 5534919361313859554 | a chest here: one of the four `MiniGame_DampeRace_OpenGoalTBox` chests, the one with `Obj_Heart_Piece` beside the Hookshot one |
| Graveyard Heart Piece Grave Chest | 9622128545943056087 | the other heart-piece chest, underground (y 85.8) like the Shield Grave chest |
| KF Storms Grotto Chest | 14818888396401495482 | inside KF's only grotto room (see "grotto rooms" below); N64's KF has one grotto, the Storms grotto, with one chest |
| DMT Chest | 9809508929088891725 | DMT's only chest outside a grotto, 1.4 units from a `WallCrack` and beside broken-rock fragments (N64: behind a bombable wall) |
| removed: LW Near Shortcuts Grotto Chest | 17479747339356189279 | the residual rule's pick, but this chest stands in the open by the bridge scrub, and the LW grotto room that would hold N64's chest holds no check |

**Grotto rooms.** Each grotto room is a `Land_HidingHole_Base_*` actor in the overworld file, and every check found
in one sits 9 to 16 units below its origin and 15 to 26 units from it (30 bases outside `DreamWorld`; the linked SFM
Wolfos and ZR Open grottos and the LW and HF scrub grottos fit). What the rooms hold: KF one (the green chest); LW
two (one with the Grotto Front and Rear scrubs, one with no check) plus the Deku Theater (base `L_01`, with the
`Enemy_Scrub_ForestStage` actors); HF nine (the heart-piece scrubs, the nuts/seeds/bombs trio, a red chest among
Lake Hylia rocks with `Obj_CandleStick_TimeExtinguish` candles, a purple chest, two Gold Skulltulas, three with no
check); SFM two (the Wolfos chest, a scrub-seed chest); DMC two (a scrub-seed chest, a purple chest); DMT two (no
check); GC one (two chests); GV two (a scrub-seed chest; the green chest and the Lens chest copies); Colossus one (a
purple chest); GF one (a red chest); Kakariko two (the blue chest; one with no check); ZR two (the scrub-seed chest;
one with no check); ZD one (no check); Hyrule Castle one (a Gold Skulltula). Where N64 has a scrub grotto (GC, SFM,
Colossus, DMC, ZR, GV), the remake has a chest or nothing [inference from the counts; which room is which N64 grotto
is not settled for most].

Left unlinked though a guess exists (wrong links cost more than empty ones): the two DMC heart pieces (one by the
lava falls, one by liftable rocks), the GV heart piece (`Obj_GerudoValley_Heart_Piece`, by a small shrine, against
"Crate" and "Waterfall"), the Hyrule Field child scrub trio (nuts, seeds, bombs: both N64's LLR and LH grottos sell
that set), Kakariko's blue chest (near a grotto entrance), the 8 Gerudo Fortress key actors (two per key `_0n`: one
plain, one named `SmallKeyForEvent_0n` that appears on `GerudoFortress_DestroyGerudoThief_Npc_Hylia_01x_Adult`; which
jail each opens is not in the data I read), and every dungeon chest whose item family repeats (small keys, rupees).

**Flag for review: the Fire Temple map and compass.** By item, the map chest (room 5) is linked to "Fire Temple Map
Chest" and the compass chest (room 16) to "Fire Temple Compass Chest"; but the room-5 chest plays
`FireTemple_GetCompass` and the room-16 chest `FireTemple_GetMap`. Either the remake swapped the two items between
the N64 locations, or the event names are swapped (the remake reuses `ForesetTemple_GetBossKey`, misspelled, for
four other boss keys, so its event names are not reliable). Logic differs between the two N64 chests, so this
needs an in-game look.

### OoT Randomizer checks with no remake id (Gold Skulltulas aside: all 100 unlinked)

- **BottomOfTheWell** (9): Front Left Fake Wall, Front Center Bombable, Back Left Bombable, Underwater Left, Center
  Skulltula, Right Bottom Fake Wall, Like Like, Underwater Front, Invisible chests (remake: 8 unlinked chests, 6 of them
  in room 1).
- **DeathMountainCrater** (7): Volcano and Wall heart pieces; Upper Grotto Chest; DMC Deku Scrub; Grotto scrubs Left,
  Center, Right.
- **DeathMountainTrail** (1): DMT Storms Grotto Chest (DMT's two grotto rooms hold no check).
- **DesertColossus** (2): Grotto scrubs Front, Rear.
- **DodongoCavern** (6): End of Bridge Chest; Boss Room Chest; scrubs Side Room Near Dodongos, Lobby, Near Bomb Bag
  Left and Right.
- **FireTemple** (10): Near Boss, Flare Dancer, Big Lava Room Lower Open Door and Blocked Door, Boulder Maze Lower,
  Side Room, Shortcut and Upper, Scarecrow, Highest Goron chests.
- **ForestTemple** (9): First Room, First Stalfos, Raised Island Courtyard, Well, Eye Switch, Floormaster, Red Poe,
  Falling Ceiling Room, Basement chests.
- **GerudoFortress** (5): GF Freestanding PoH; Hideout 1-4 Torch(es) Jail Gerudo Keys.
- **GerudoTrainingGround** (19): Lobby Left and Right, Stalfos, Before Heavy Block, Heavy Block First to Fourth, Eye
  Statue, Near Scarecrow, Hammer Room Clear and Switch, Maze Right Side, Underwater Silver Rupee, Beamos, Hidden
  Ceiling, Maze Path Second and Third chests; Freestanding Key.
- **GerudoValley** (5): Crate and Waterfall heart pieces; GV Chest; Grotto scrubs Front, Rear.
- **GoronCity** (7): GC Pot Freestanding PoH; Maze Left, Center, Right chests; Grotto scrubs Left, Center, Right.
- **Graveyard** (2): Royal Familys Tomb Chest; Dampe Gravedigging Tour (an event here:
  `GraveYard_DiggingHoleTour_Drop_HeartPiece`, 03-game-data section 5).
- **HyruleField** (10): Near Market, Southeast and Open Grotto chests; Tektite Grotto heart piece; LLR and LH Grotto
  scrubs (3 each).
- **IceCavern** (1): Freestanding PoH.
- **InsideGanonCastle** (17): Forest Trial; Water Trial Left (ice trap) and Right; Shadow Trial Front; Light Trial
  First, Second, Third Left and Right (three are ice traps), Invisible Enemies, Lullaby; Spirit Trial Invisible
  chests; scrubs Left, Center-Left, Center-Right, Right.
- **KakarikoVillage** (2): Open Grotto Chest; Redead Grotto Chest.
- **KokiriForest**: none (Gold Skulltulas aside).
- **LostWood** (1): Near Shortcuts Grotto Chest (that grotto room holds no check).
- **SacredForestMeadow** (2): Grotto scrubs Front, Rear.
- **ShadowTemple** (12): Early Silver Rupee, Invisible Blades Visible and Invisible, Falling Spikes Lower, Upper and
  Switch, Invisible Spikes, Wind Hint, After Wind Enemy and Hidden, Spike Walls Left, Invisible Floormaster chests.
- **SpiritTemple** (13): Child Bridge, Child Early Torches, Child Climb East, Sun Block Room, Early Adult Right, First
  Mirror Left (ice trap) and Right, Statue Room Northeast and Hand, Near Four Armos, Hallway Right and Left
  Invisible, Topmost chests.
- **WaterTemple** (6): Cracked Wall, Torches, Central Pillar, Central Bow Target, River, Dragon chests.
- **ZoraRiver** (2): Grotto scrubs Front, Rear.

Grotto scrubs on N64 are 23 locations. The remake's 21 scrubs outside `DreamWorld` are in Hyrule Field (5), the
Lost Woods (9), Kokiri Forest (2), DMC (1) and one each in BotW, Dodongo's Cavern, Jabu-Jabu and the Shadow Temple:
none in Goron City, SFM, Zora's River, Gerudo Valley, the Colossus, Lake Hylia's or LLR's grottos (beyond the one
Hyrule Field trio) or Ganon's Castle. The census reads every `Enemy_Scrub_Business`, so this is a remake difference
to confirm in game, not a matching gap.

### Remake checks with no OoT Randomizer name (Gold Skulltulas aside)

242 of 477 are unlinked: 100 Gold Skulltulas, and these (id, vanilla item, room):

- **BottomOfTheWell**: chests 631709185320708287 (blue, r1), 5429815628949128345 (blue, r1), 8397646530660039355
  (small key, r1), 8975637636514249074 (red, r1), 10905582354954996284 (red, r1), 12988877782812797760 (blue, r1),
  11718708984125260282 (purple, r2), 6064359710907908886 (scrub seed, r11); scrub 15945446340598299551 (green
  potion, r1).
- **DeathMountainCrater**: chests 1158729434763801603 (scrub seed), 9128916506605227251 (purple); heart pieces
  744856631664786545, 10331043360028932045; scrub 2518138296199711695 (heart piece, child).
- **DeathMountainTrail**: none.
- **DesertColossus**: chest 1186167733408299582 (purple).
- **DodongoCavern**: chests 7524527082521156886 (Deku Shield, r1), 8607798771661947511 (blue, r1),
  12253889300578348965 (scrub seed, r10), 11582649900854566065 (Deku Shield, r13), 850464708089653824 (scrub seed,
  r16); scrub 7388739057158296701 (no item, r7).
- **FireTemple**: small-key chests 3949488292768750868 (r1), 5634724236470386190 (r2), 16785682308850448108 (r4),
  9634924691849556346 (r5), 12567412825200613393 (r5), 12945617941305968586 (r10), 10521366928524045067 (r11),
  1705064956286753527 (r22); rupee chests 8757492004108970488 (red, r3), 862385681502746018 (purple, r8),
  15073195886628236505 (red, r8), 17001858340376096722 (red, r8).
- **ForestTemple**: small-key chests 1171460703078800858 (r0), 14776684749746592758 (r4), 6449977980406424425 (r15),
  3433400840978782007 (r16), 7535137041266964235 (r22); 15920957434854338961 (purple, r8), 15117164073907033527
  (no drop: green rupee, r24), 9038700938965170329 (large arrows, r27).
- **GerudoFortress**: chest 16619432200060282313 (red, adult); the 8 key actors (`_01`: 14727159573379044362,
  5126034700935231136; `_02`: 5303541637929200213, 12946017077004046962; `_03`: 1406667554698159711,
  7337789119684854050; `_04`: 10731814783987785199, 18396961731144479654).
- **GerudoTrainingGround**: 19 chests: 9 small keys (r1, r4, r5, r7, r8 x3, r9, r10), red x4, blue x2,
  green-default x2, bombs, scrub seed (ids in `locations.toml`).
- **GerudoValley**: chests 13612880783193811229 (red, adult), 18413589940135955604 and 6205043616869463865 (one
  Lens chest, red, adult and child copies), 6463521162691873710 (scrub seed), 17750686910716887133 (green),
  15856256242099990922 (heart piece); heart piece 16129198288828948135.
- **GoronCity**: 6 rupee chests (blue x2, purple x2, red, green).
- **Graveyard**: Dampe race repeat chests 234006393181394602 (red), 4322670163630771947 (blue).
- **HyruleField**: chests 1163740567397714729, 9891111455604007674, 17023457248274633121 (red, adult),
  6900843020594897860 (red), 5755485285664292988 (purple), 17445672702269453589 (scrub seed), 2967378296224661060
  (heart piece, `Obj_TBox_A_01_memo11`); scrubs 12901354557574090016, 16672855544778411393, 17418042722045679657
  (seeds, bombs, nuts; child).
- **IceCavern**: chest 4128092231168513176 (red, r8).
- **InsideGanonCastle**: 9 chests: arrows x2 (r2, r8), blue x3 and red (r12), small key (Lens chest) and green (r13),
  scrub seed (r17).
- **InsideJabuJabuBelly**: chest 3609242017501283521 (red, r13).
- **KakarikoVillage**: chests 11929552275106311978 and 13080955777249750889 (purple, adult and adult-alternative
  copies), 12902291359202819102 (blue).
- **KokiriForest**: chest 4349272251343787229 (purple, in the open by the stick-upgrade scrub); stick-upgrade scrub
  182031956235860994 (child) and 7488448334396031424 (adult).
- **LostWood**: chest 17479747339356189279 (purple, in the open by the bridge scrub); scrub 14619830301496284497
  (arrows, adult; the adult copy of the Grotto Rear scrub, which sells seeds as child).
- **Market**: treasure-game red-rupee reward box 6781536951709667179.
- **SacredForestMeadow**: chest 1764383515296652106 (scrub seed).
- **ShadowTemple**: 10 chests: small keys (r6, r11, r16, r21), red x3 (r11, r31 x2), scrub seed (r15), green (r16),
  large magic jar (r19); scrub 8721287453021850502 (green potion, r9).
- **SpiritTemple**: 10 chests: small keys (r4, r7, r9, r16, r26), Deku Shield (r2), bombs x2 (r18, r31), red x2 (r23).
- **WaterTemple**: chests: small keys (r4, r8, r18, r20), red (r2).
- **ZoraFountain**: chest 15055117029957340138 (purple, adult).

## Remake findings (for 03-game-data)

- **Shops have 8 slots, not 7.** The shop actor without `ShopItemIndex` is slot 0 (section 5 of 03-game-data counts
  only `ShopItemIndex` 1..7). 9 shops (8 and the mask shop) x 8 = 72, as in OoT Randomizer. Each slot is a separate
  actor (and Hash) per file: child, adult and `Adult_Alternative` files, and Kokiri Forest's child file has two stock
  sets at the same spots, switched by `Meet_DekuTree_IsAfter_Step02_Exp` (`Presence.IsNegation` false/true).
  Kakariko's shops are only in the adult files; the Market's only in the child file.
- **Same spot, different Hash, both with a save flag.** Six one-time checks are placed in two files under different
  Hashes, so the game keeps a separate flag for each: the Lens chest in Gerudo Valley (child, adult), Kakariko's
  purple chest (adult, adult-alternative), and the scrubs selling the Hyrule Field heart piece, the KF and LW stick
  upgrades and the LW nut upgrade (child, adult). [Inference: buying as child does not mark the adult copy, so each
  can be collected twice.] Where linked (the three scrub pairs), both ids carry the same `oot_randomizer_name`; a
  seed must place the same item in both.
- **Scrubs changed.** 21 business scrubs outside `DreamWorld`; 5 spots (9 actors with the age copies) sell a
  one-time item (the HF and DMC heart pieces, the KF and LW stick upgrades, the LW nut upgrade), the rest sell up to
  three repeatable offers. Three name no item at all
  (`TalkEventName` `Enemy_Scrub_Business_Item` in Dodongo's Cavern and Jabu-Jabu, `..._Item_SellBug` in the Lost
  Woods). Grotto scrubs are mostly gone (above).
- **Keys.** The BotW freestanding key and the 8 Gerudo Fortress key actors have no `Bool64bitKey` flag of their own;
  the Shadow Temple key has one. No freestanding key in Gerudo Training Ground (as 03-game-data said).
- **Treasure Chest Game** rooms and reward as described in the linking rules.
- **Events.** `ForesetTemple_GetBossKey` is the open event of 5 boss-key chests (Forest, Fire, Water, Shadow,
  Spirit); the Fire Temple map/compass event names are crossed (above).

## Provisional choices (Claude or Kareem to confirm)

1. A location is one actor Hash, also where the same check exists under another Hash in another file (shops,
   the six copies above). The alternative, one location with several Hashes, would hide the separate save flags.
2. `ages` counts a placement file without `_Child_`/`_Adult_` in its name (dungeons) as both ages.
3. A chest without `Drop__DropActor` gives `Obj_Rupee_Green` (03-game-data's inference); the Gold Skulltula's item is
   `Obj_Token_Gold`; a scrub's is its first offer.
4. Silver rupees (`Obj_RupeeToken_Silver`, 85) are not a census kind (the roadmap's kind list leaves them out).
5. Shop slots link to OoT Randomizer by slot number (above); Gold Skulltulas not at all.
6. `id` is a string in TOML.

## Questions for Kareem

1. **Six checks exist twice with separate save flags (child and adult copy, or Kakariko's two adult states): the
   Gerudo Valley Lens chest, Kakariko's purple-rupee chest, and the scrubs selling the Hyrule Field heart piece and
   the stick and nut upgrades. Should a seed treat each pair as one check (same item in both, as the definitions do
   now), or as two?**
2. **Grotto business scrubs: the census finds none in most N64 scrub grottos (GC, SFM, ZR, GV, Colossus, one trio
   for LH and LLR) and none in Ganon's Castle. Do you remember whether the remake removed them?**
3. **Fire Temple: is the map in the chest you reach earlier (room 5) or later (room 16)?** This decides which N64
   location each is.

## In-game tests for Kareem

Three mod folders under `E:/OOTRemake/work/r2-census/ingame/`, each `<name>/romfs/Banc/...` with only the changed
files (each one a new game, one at a time; Claude points `HOS_FS_OVERLAY` at `<name>/romfs`). Built by
`E:/OOTRemake/work/r2-census/make_ingame.py`, which also checks each written file reads back as the original tree
with only the intended change.

**1. `heart-piece-to-red-rupee`** (`Banc/HyruleField/HyruleField_Child_Static.bcett.byml.zs`): the Lon Lon Ranch heart
piece (Hash 9814903750835309225, child only) has `Gyaml` `Obj_Rupee_Red`, a pickup the game already places in the
world (7 times, in Hyrule Field, DMT and DMC). Hash, position and everything else unchanged.
- Go: as child, to Lon Lon Ranch; the heart piece of N64's "LLR Freestanding PoH" (on N64 inside the tower, reached
  by crawling). The census places it among `Land_LonLon_*` actors, 3 units from a crawl anchor, at (-157.2, 150.9,
  266.4).
- See: a red rupee where the heart piece was; picking it up gives 20 rupees; leave the ranch and come back: it should
  stay gone (its save flag is the heart piece's Hash). Log: `fs: OpenFile(...HyruleField_Child_Static...): from the
  overlay`.

**2. `heart-piece-to-fire-arrows`**: the same heart piece with `Gyaml` `Obj_Arrow_Fire`.
- What the game uses for a major item lying in the world: the pickups placed in Banc that are `PouchActorInfo` items
  with `PouchGetType` Large are `Obj_Arrow_Fire` (`HyruleField_Adult_Static`, named `Item`, at the Lake Hylia end:
  presumably the Fire Arrows that appear after shooting the sun), `Obj_Bottle_Letter` (`HyruleField_Child_Static`,
  presumably Ruto's letter), the GF keys, `Obj_SinkingLure`, and the
  shop display actors. Unplaced packs of the same family exist (`Obj_Ocarina_Time`, `Obj_Shield_Deku`,
  `Obj_Shield_Hylian`, `Obj_Armor_Goron`, `Obj_Armor_Zora`, `Obj_Bombchu`); no `Obj_` pickup exists for most major
  items (Boomerang, Hookshot, ...), which chests give as `Item_*`. So Fire Arrows are the test.
- See: Fire Arrows lying in the tower; picking them up shows the Fire Arrows get message and adds them to the
  inventory (child cannot use them). If nothing appears, the Fire Arrows actor probably hides itself until its Lake
  Hylia event; say so and we try `Obj_Bottle_Letter` next.

**3. `kokiri-sword-chest-no-story-event`** (both `KokiriForest_{Child,Adult}_Dynamic`): the Kokiri Sword chest (Hash
16757992849254467386) holds `TBox_Rupee_Red` and has no `GetEventName`, so the big chest's default `Dm_SY_Treasurebox`
plays.
- Go: new game, the Kokiri Sword chest (the same chest as round 1's test).
- See: the normal big-chest opening, a red rupee (20) with its text, **no sword cutscene, no sword in Link's hand**.
  The Kokiri Sword is then not obtainable anywhere in this test, so Mido should keep blocking the Deku Tree path
  [inference].

What `Get_StoneOfForest_GetSword` sets (from the decoded flows in `E:/OOTRemake/work/r1-research/decoded/`): the
row runs flow `Get_StoneOfForest`, entry `GetSword`: `EventTransition` to `Dm_SY_Treasurebox` (grants the chest's
item), then to `Dm_Kokiri_0063` (the cutscene: `EventTriggerPlayerRequestCreateDynamicEquipmentNoRelationPouch`
with `Weapon_Sword_Kokiri`, then `EventTriggerPlayerEquipDynamicEquipmentFromPouch`, which is why round 1 saw the sword
in hand but not in the menu), then Navi balloon lines chosen by `HaveTalked_Special.Npc_Kokiri_Mido_Child_Talk_Event30`,
`KokiriForest_Npc_Kokiri_Mido_Child_Blocker` and `IsGet.Weapon_Shield_Deku`. Neither flow sets a game-data flag; the
only state left behind is `HavePlayedEvent.Get_StoneOfForest_GetSword` and `HavePlayedEvent.Dm_Kokiri_0063`, which no
event flow reads and no `Logic`/`Sequence` AINB names (byte search). The story state that matters is owning
`Weapon_Sword_Kokiri` (read by `Npc_Kokiri_006_Child` through `EventQueryCheckIsGet` and named in four KokiriForest
logic modules), which the sword item sets wherever it is found. So a seed needs no extra flag for this event
[inference, to be confirmed by test 3 and by a seed that puts the sword elsewhere].

Sizes against the size table (entry = ceil32(size) + 264 by round 1's formula):

| File | decompressed | compressed | table entry | formula |
|---|---|---|---:|---:|
| `HyruleField_Child_Static` (tests 1 and 2) | 395,636 -> 395,652 (+16) | 134,949 -> 132,535 / 132,548 | 395,912 | 395,944 |
| `KokiriForest_Adult_Dynamic` (test 3) | 516,036 -> 515,996 (-40) | 194,708 -> 192,339 | 516,328 | 516,264 |
| `KokiriForest_Child_Dynamic` (test 3) | 510,884 -> 510,844 (-40) | 192,909 -> 190,319 | 511,176 | 511,112 |

The Hyrule Field file needs 32 more than its entry, the same margin round 1's Kokiri Forest file loaded with.

## Reviewer's question: KF Storms Grotto Chest and the LW Deku Theater scrubs

- **Grottos have no Banc folder of their own.** The 33 Banc folders are all areas, dungeons, `DreamWorld` and
  `SageRoom`; a grotto is a `Land_HidingHole_Base_*` room inside the overworld file it opens from (see "Grotto
  rooms"). The census scans every file of every folder.
- **KF Storms Grotto Chest exists** and is linked (9573d21, after the rebase): chest 14818888396401495482
  (`TBox_Rupee_Green`, both ages), 13 units below and 23 from KF's only grotto base, `Land_HidingHole_Base_I_01`
  at (-51.9, 116.6, -62.8).
- **The two LW Deku Theater scrub spots exist, with different offers, and are linked by an inferred left/right.**
  All 51 `Enemy_Scrub_Business` actors were listed (the other `Enemy_Scrub_*` actors are the theater audience, Mad
  Scrubs and the Deku Tree's brothers; none sells). Of the 11 business scrubs in both LW files, two spots stand by
  the Deku Theater (base `L_01` at (3.8, 94.3, -47.5), with the `Enemy_Scrub_ForestStage*` actors), both in the
  child file only (N64's two are child-only too). The path to the theater runs west along z = -48 (a line of `Area`
  actors from x 48 to 15, from the LW junction at x 24) to the hole at x 3.8. Walking it, and taking the engine as
  right-handed with y up, the player's left is +z, so:
  - **Left** = 2569517939889411425 at (12.2, -41.2) (`Enemy_Scrub_Business_Item_SellBug`: buys a bug, sells
    nothing; N64 sells a Deku Stick).
  - **Right** = 11385057993574159532 and 15048088372638595204 at (19.2, -51.2) (two scrubs at one spot,
    `Enemy_Scrub_Business_Potion`: heart, heart bundle, magic jar / red potion, green potion, heart bundle; N64 sells
    Deku Nuts). Both carry the name, like the age copies.
  The mapping is inferred (handedness and the approach direction are not stated in the data). The adult file has no
  scrub near the theater; no scrub in the game sells a single Deku Stick (`Enemy_Scrub_Business_Common` has no stick
  entry). Scrubs are not shuffled in the first seeds (D15), so a wrong side costs nothing yet.

## Cross-track posts (thread `cs-r2`)

- 15:54: `locations.toml` committed (dd08991): format, loader, many-to-one names for shops and copies, coverage of
  KF/LW/Deku Tree for track B, Gold Skulltulas unlinked by design.
- 16:05, after the second commit (dedd1a6): `KF Storms Grotto Chest` and `DMT Chest` linked, `LW Near Shortcuts Grotto Chest`
  unlinked (the residual rule was wrong there); KF now 14/17 (only the 3 GS unlinked), LW 3/9.
- Track B (16:01) asked for an N64-only list by OoT Randomizer name. From the census side, of the regions it ports,
  the evidence points to N64-only for `LW Near Shortcuts Grotto Chest` (its grotto room holds no check); the two
  `LW Deku Scrub Near Deku Theater` scrubs exist near the theater but changed offers and can't be told left from
  right. That list is Claude's or Kareem's call; I did not write one.
- 16:08: answer to the reviewer's question (above): KF Storms Grotto Chest exists and is linked; the two theater scrub
  spots exist with changed offers, unlinked until left/right is known; not N64-only.
- 16:15: theater scrubs linked by position on the reviewer's call (Left = bug-buying scrub, Right = the potion
  pair), inferred; LW now 5/9 (Near Shortcuts Grotto Chest and 3 GS open).
- 16:15 (later): item 5 report (save reader, main slot, LLR heart piece not collected in the copy, Impa tests).

## Item 5: save reader and the heart-piece tests on Kareem's save

**`clawshot.save`** (`src/clawshot/save.py`, tests `tests/test_save.py`, synthetic only): `load(path)` / `read(bytes)`
-> `Save`, read-only. The layout is Tears of the Kingdom's, confirmed on the copy:

- header 0x20 bytes: u32 magic `0x01020304`, u32 version, u32 end of the entry table, zero padding;
- entry table of (u32 key, u32 value) pairs; `(0, n)` opens section `n`; keys are murmur3 (x86 32, seed 0) of the
  flag name, as in `GameDataList`. Section order checked against `GameDataList`: every key in sections 0-7, 10, 14,
  16-22, 24, 25, 27 is a `GameDataList` entry of the type `save.TYPES` names; the other indices were empty and are
  named by TotK's order (marked unconfirmed in the code). Bool/Int/UInt/Float/Enum values sit in the pair; other types
  hold an offset (left as such);
- section 32 (`Bool64bitKey`) has one pair keyed by the file's `MetaData.SaveTypeHash` (progress.sav: `0xa3db7114`);
  its value points at the set 64-bit keys, u64 each, ending with 0.

Accessors: `flag(name)`, `int_value`, `uint_value`, `float_value`, `enum_value`, `is_set(key64)`, `set_keys`.
Tests: murmur3 vectors, every scalar type by name, the key list, an empty list, and six malformed files (bad magic,
short file, misaligned table, entry before a section, unknown section type, unterminated key list).

**On the copy** (`E:/OOTRemake/work/save-copy/`, read with `E:/OOTRemake/work/r2-census/save_report.py`; its output,
with the per-slot numbers, is `save_report.txt` next to it, not here):

- **Main game: `slot_01`**, by far the most `HavePlayedEvent.*` flags; child, past the Deku Tree (Kokiri Emerald,
  Gohma's heart container, Zelda's letter, Saria's Song). The other slots are fresh starts.
- **The mapping works for freestanding pickups and Gold Skulltulas**: the Deku Tree heart container's Hash is set (and
  `IsGet.Obj_Heart_Container` is true); the other seven are not. Each Gold Skulltula killed sets its own Hash and a
  second key at Hash +-2 (the token), as many of each as the token count. Recovery hearts, rupees, spider webs and
  pots also appear by their Hash.
- **The check asked for fails, and the save explains why: the LLR heart piece (9814903750835309225) reads NOT
  collected.** It agrees with the rest of the save: `IsGet.Obj_Heart_Piece` is false and the life maximum is exactly 3
  starting hearts plus Gohma's container, so this copy has no heart piece at all. Either the copy predates the pickup,
  or the pickup was on another save. **Kareem: is the copy from before you took the Lon Lon Ranch heart piece?**
- **All 14 freestanding heart pieces read not collected** in `slot_01` (and in every slot).
- **Finding: chests are not in the `Bool64bitKey` list.** `slot_01` played the Deku Tree map, compass and slingshot
  chest events and the Kokiri Sword's, yet no chest Hash is set (searched as u64 anywhere in the file, too). Where a
  chest keeps "opened" is open; 03-game-data section 6's "a chest's opened flag is its Hash" holds for
  `GameDataList` (the entry exists) but the save does not use it for chests. Candidate: the 3.4 KB `Binary` entry
  `0x70d7c5cb` (u64 records grouped by a high word, not actor Hashes); not decoded.

**New tests 1 and 2 on an open heart piece: Kakariko, Impa's house** (`Kak Impas House Freestanding PoH`, Hash
17926402522258180222, in all three Kakariko files: child, adult, adult-alternative):

- `ingame/impa-heart-piece-to-red-rupee/` (`Obj_Rupee_Red`) and `ingame/impa-heart-piece-to-fire-arrows/`
  (`Obj_Arrow_Fire`), three files each.
- Reachable with `slot_01` as **child, in daytime**: OoT Randomizer's `Kakariko Village -> Kak Impas Ledge` is
  `is_child and at_day` (no items), and the ledge drops into the cow pen behind Impa's house (`Kak Impas House Back`),
  where the census puts this heart piece next to the cow. The save has been to Kakariko (its Gold Skulltulas there are
  taken). Adult would need `logic_visible_collisions` (a trick), so test as child.
- See: a red rupee (or Fire Arrows) in the cow pen behind Impa's house; picking it up gives 20 rupees (or Fire
  Arrows); leave and come back: it stays gone. Log: `fs: OpenFile(...KakarikoVillage_Child_Static...): from the
  overlay`.
- Sizes: `KakarikoVillage_Child_Static` 292,584 -> 292,600 (fits its size-table entry exactly);
  `_Adult_Static` +16 (32 over the entry, the margin that loaded in round 1); `_Adult_Alternative_Static` +20 (fits).
- The Lon Lon Ranch variants stay: by this copy, that heart piece is still open in `slot_01` too.

## Left for later

- Dungeon chests with repeated items (mostly small keys and rupees): 5 to 19 per dungeon unlinked. Room numbers here
  are `DefaultDungeonRoomIndex`; linking them needs the N64 room of each OoT Randomizer chest or an in-game walk.
- Gold Skulltulas: positions and rooms are in the census for the round-3 world port.
- Event gifts (EVFL), and the alternative-state files (`Adult_Alternative`): which story state selects them.

## Gates (before the handoff, after item 5)

```
uv run ruff format --check                                  34 files already formatted
uv run ruff check                                           All checks passed!
uv run pytest                                              86 passed, 6 skipped
OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump      6 passed, 86 deselected
```
