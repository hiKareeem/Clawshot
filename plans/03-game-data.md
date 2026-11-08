# Game data: where checks live and how the game records them

Round 1, track B (cs1b). Build `e0f3ccfa` (romfs from `E:/Games/Hookshot/romfs`). Identifiers, names and counts
only; nothing here is copied from a game file.

**How it was found.** Scratch scripts in `E:/OOTRemake/work/r1-research/` (outside the repo): `lib.py` (romfs
loader on `clawshot.formats` from main `fa37c50`), `byml_any.py` (big-endian BYML, which `clawshot.formats.byml`
does not read), and `r1_numbers.py`, which recomputes the headline numbers below (run from the worktree:
`uv run python E:/OOTRemake/work/r1-research/r1_numbers.py`). Event flows were decoded with zeldamods `evfl` 1.3.0
(GPL-2.0, used unmodified outside the repo, rule 7). OoT Randomizer's `LocationList.py` is from `Dev` at
`526b4c8d81b7c4023ef4573ffbaf39344e270d5b`. "Unique" always means deduplicated by actor `Hash`.

## Summary

| Question | Answer in one line |
|---|---|
| 1 Chests | 267 `Obj_TBox*` placements = 232 unique actors: **194 chests**, 6 trap chests, 32 pedestals. 184 chests outside `DreamWorld`. |
| 2 The 41 without a drop | 32 pedestals (not chests), 6 trap chests (`Obj_TBox_A_04`), 3 real chests that fall back to the chest's default (`Obj_Rupee_Green`, inferred). |
| 3 `GetEventName` | Row of `RSDB/EventSetting`; overrides the chest's default open event. The item is passed in, not hard-coded: a new item needs no new event. |
| 4 Event gifts | Every gift ends in `PouchSystemActor.EventTriggerAddOrRemovePouchContent` with the item's actor name as a string parameter, usually through a wrapper flow. |
| 5 Other checks | 100 Gold Skulltulas, 36 heart-piece anchors, 8 boss heart containers, 56 shop slots + 7 mask slots, 21 business scrubs, 14 cows, 6 Great Fairy events. |
| 6 Flags | `GameDataList` keys flags by murmur3 of their name; placement checks (chests, GS, heart pieces) are `Bool64bitKey` flags keyed **by the actor `Hash`**. Event checks: `HavePlayedEvent.<event>` plus named flags. |
| 7 Sizes | `RSDB/` has no size table. `System/Resource/ResourceSizeTable...rsizetable.zs` (TotK's RESTBL) has an entry for every placement file. |
| 8 `DreamWorld` | Boss and miniboss rematch / boss rush / Enemy Museum with a swapped-in temporary inventory. Not a source of checks. |
| 9 vs OoT Randomizer | Gold Skulltulas match per area exactly (100/100). Chests: 175 there vs 184 here (+12 treasure-game boxes), with real per-area differences listed below. |

## 1. Chests per area

Chests are actors whose `Gyaml` starts with `Obj_TBox`, in `Banc/<Area>/*_{Child,Adult}_{Static,Dynamic}.bcett.byml.zs`
(dungeons have one `<Dungeon>_{Static,Dynamic}` pair). The same chest appears in both age files with the same `Hash`
and, checked for every one, the same drop parameters; no `Hash` appears in two areas or in both a Static and a
Dynamic file. Kinds: `Obj_TBox_A_01` (small), `A_02` (big), `A_03` (boss key), `A_06` (small, with a substitute
drop), `GlassTruth_A_01` (Lens-only), each also as `_NoBake`; `Obj_TBox_A_04` is a trap chest and
`Obj_TBoxPedestal_A_0{1,2}` a stand that a chest appears on.

| Banc area | placements | unique Hash | chests | trap | pedestal | chests by age |
|---|---:|---:|---:|---:|---:|---|
| BottomOfTheWell | 13 | 13 | 12 | 0 | 1 | one file 12 |
| DeathMountainCrater | 6 | 4 | 2 | 0 | 2 | both ages 2 |
| DeathMountainTrail | 2 | 1 | 1 | 0 | 0 | both ages 1 |
| DesertColossus | 6 | 3 | 3 | 0 | 0 | both ages 3 |
| DodongoCavern | 11 | 11 | 9 | 0 | 2 | one file 9 |
| DreamWorld | 13 | 13 | 10 | 0 | 3 | one file 10 |
| FireTemple | 16 | 16 | 16 | 0 | 0 | one file 16 |
| ForestTemple | 13 | 13 | 12 | 0 | 1 | one file 12 |
| GerudoFortress | 2 | 2 | 2 | 0 | 0 | adult only 2 |
| GerudoTrainingGround | 23 | 23 | 22 | 1 | 0 | one file 22 |
| GerudoValley | 9 | 6 | 6 | 0 | 0 | adult only 2, both ages 3, child only 1 |
| GoronCity | 16 | 10 | 6 | 0 | 4 | both ages 6 |
| Graveyard | 8 | 6 | 6 | 0 | 0 | adult only 4, both ages 2 |
| HountedWasteland | 2 | 1 | 1 | 0 | 0 | both ages 1 |
| HyruleField | 15 | 11 | 7 | 0 | 4 | adult only 3, both ages 4 |
| IceCavern | 4 | 4 | 4 | 0 | 0 | one file 4 |
| InsideGanonCastle | 20 | 20 | 12 | 4 | 4 | one file 12 |
| InsideJabuJabuBelly | 4 | 4 | 4 | 0 | 0 | one file 4 |
| InsideTheDekuTree | 6 | 6 | 6 | 0 | 0 | one file 6 |
| KakarikoVillage | 5 | 3 | 3 | 0 | 0 | adult only 2, both ages 1 |
| KokiriForest | 14 | 7 | 7 | 0 | 0 | both ages 7 |
| LostWood | 2 | 1 | 1 | 0 | 0 | both ages 1 |
| SacredForestMeadow | 6 | 4 | 2 | 0 | 2 | both ages 2 |
| ShadowTemple | 20 | 20 | 14 | 0 | 6 | one file 14 |
| SpiritTemple | 15 | 15 | 14 | 1 | 0 | one file 14 |
| WaterTemple | 9 | 9 | 9 | 0 | 0 | one file 9 |
| ZoraDomain | 4 | 4 | 1 | 0 | 3 | child only 1 |
| ZoraFountain | 1 | 1 | 1 | 0 | 0 | adult only 1 |
| ZoraRiver | 2 | 1 | 1 | 0 | 0 | both ages 1 |
| **total** | 267 | 232 | 194 | 6 | 32 | |

Not in the table: the Market treasure chest game uses its own actors, `Obj_HrlCity_Shop_TBox_A_01` (10) and
`_A_02` (2), with `Drop__DropActor` and `GetEventName` like chests. Banc folders are wider than OoT Randomizer's
areas: `HyruleField` also holds Lon Lon Ranch, Lake Hylia and the fishing pond; `Market` holds the Temple of Time;
`InsideGanonCastle` holds Ganon's Tower; grottos ("HidingHole" actors) are inside the overworld file they open from.
`HountedWasteland` is the game's spelling.

Contents: `Drop__DropActor` names the item actor (`Item_*`, `TBox_Rupee_*`, `Obj_Heart_Piece`, ...). `A_06` chests
add `Drop__CheckActor` and `Drop__DropActor_Substitute` (9 placements): the substitute is given when the player
already owns the check actor (e.g. a Deku Shield chest gives rupees once you have one) [inference from the names;
not traced into the AI]. `SpawnType` 1 (17) marks chests that appear on a condition, matching the
`Gimmick_TreasureBoxAppear_*` logic modules in `Logic/`. `IsEnableRepeatOpen` (10) is set only on the `DreamWorld`
gold-rupee chests.

## 2. The 41 chest placements without `Drop__DropActor`

| What | Placements | Unique | Contents |
|---|---:|---:|---|
| `Obj_TBoxPedestal_A_01`/`_A_02` | 32 | 32 | none: a stand placed at the same position as a spawned chest; no save flag |
| `Obj_TBox_A_04` trap chest | 6 | 6 | none: its actor logic is `ActorLogicTrapTreasureBox` (attack, life and destruction components); its pack's drop table drops rupees when destroyed |
| real chests | 3 | 3 | the chest's default, see below |

The six trap chests are exactly OoT Randomizer's six vanilla Ice Trap chests (room numbers match): Spirit Temple
First Mirror Left (room 18), Gerudo Training Ground Heavy Block Fourth (room 10), Ganon's Castle Water Trial Left
(room 5) and Light Trial Second Left, First Right and Third Right (room 12). Each has a save flag like a chest.

The three real chests: `ForestTemple_Dynamic` `Obj_TBox_A_01` Hash 15117164073907033527 (room 24),
`GerudoTrainingGround_Dynamic` `Obj_TBox_GlassTruth_A_01` Hash 11182647876438515984 (room 0), and
`GerudoTrainingGround_Static` `Obj_TBox_A_06_NoBake` Hash 4961588221597286817 (room 5, check `Item_Range_Bow`,
substitute `TBox_ArrowBundle_Medium`, linked from an `EventRequestActor` that plays
`GerudoTrainingGround_05_AppaerTreasureBox`). Every chest kind's blackboard (`TreasureBox` and
`Obj_TBox_A_0x` `BlackboardParamTable` in its actor pack) has a non-instance `DefaultDropActorName` of
`Obj_Rupee_Green`, and `Drop__DropActor` defaults to empty, so these three most likely give a green rupee
(the GTG one only when the player has no Bow) [inference; the AI graph was not decoded]. Their hashes appear in no
`Logic`/`Sequence` AINB and no other actor links to the first two.

## 3. `GetEventName`

`GetEventName` (61 placements, 54 unique, 36 distinct values; on 49 chests and the 12 treasure-game boxes) is an
instance override of the chest blackboard parameter of the same name. Its defaults per kind are
`Dm_SY_TreasureboxSmall` (`A_01`, `A_06`, `GlassTruth`) and `Dm_SY_Treasurebox` (`A_02`, `A_03`). Every value,
default or override, is a `__RowId` in `RSDB/EventSetting.Product.111.rstbl.byml.zs` (2380 rows), whose
`FlowchartFileName` and `EntryPointName` name the flow to run (36 of 36 found).

The item is not in the event. The default flows take a `ContentName` argument and grant it through
`GetPouchContent:GetPouchContentByActorNameForTreasureBox` (big chest: entry `Success_AddContent`; small chest:
entry `ItemDisplay`). Every override checked plays `EventSystemActor.EventTransition` to `Dm_SY_Treasurebox`
(or `...Small`) and adds its own beat around it:

| Override kind | Examples | Effect of changing the chest's item |
|---|---|---|
| Navi comment (`NaviChat:TreasureBoxDM_NaviChat_*`) | maps, compasses, Slingshot, Hammer, boss keys | item still given; Navi's line names the vanilla item [inference from entry names] |
| story beat | `Get_StoneOfForest_GetSword` (then `Dm_Kokiri_0063`), `SageOfWater_MelodyGet_Water` (Iron Boots chest, then `Dm_MelodyGet_Water`, sets `SageOfWater_GetWaterSerenade`), `SageOfSpirit_NaboorIsTakenAway` (Silver Gauntlets, then `Dm_DesertColossus_0030`), `InsideGanonCastle_Get_Gauntlet_Gold` (then `Dm_InsideGanonCastle_0006`) | item still given; the story event still plays, so the follow-on check (e.g. Serenade) stays tied to opening this chest |
| minigame | `MiniGame_DampeRace_OpenGoalTBox`, `MiniGame_ChoiceTreasure_Open*` | item still given; the flow sets minigame state (e.g. `Minigame_DampeRace_TreasureBoxState`) |
| other | `KokiriForest_TreasureBox_NaviChatOff` (Mido's house), Ruto chests in Jabu-Jabu | item still given |

So a changed chest item needs no different event for the grant. Open points: the big/small open animation follows
the chest kind (`Gyaml`), and whether a small chest may use `Dm_SY_Treasurebox` is untested.

## 4. Event item gifts (NPCs, songs, rewards)

Every gift ends in one action: `PouchSystemActor.EventTriggerAddOrRemovePouchContent` with parameters `Actor`
(item actor name), `Num` (1 to give, -1 to take away a trade item), `IsEquipDIrect`, `IsSetMessageTargetActorName`,
`IsGetEvent`. Item names are the same actor names chests use. Most flows reach it through a wrapper that takes
the item as a string argument; counts are call sites in the 914 flows with a literal item name:

| Wrapper (flow:entry) | Argument | Literal call sites | Used by |
|---|---|---:|---|
| `GetPouchContent:GetPouchContentByActorName` | `ActorName` | 29 | songs (`Dm_MelodyGet_*`), medallions (`Dm_Awake_*_Get`), spiritual stones, Light Arrows, Scarecrow's Song |
| `Dm_SY_GetInEvent:<entry>` (60 entries, 33 called from other flows) | `ActorName` | 73 | NPC handovers with a get animation: Great Fairies, Biggoron, Fado, minigame prizes, Skull Kid, Dampé, masks, Gerudo card |
| `NpcCommon:NpcCommon_HandOver_NpcToPlayer_NoDisplay` (and `_BombBag`) | `ReveiveItem` (sic) | 32 | Bombchu Bowling, shooting galleries, Cucco lady, Richard, trade sequence |
| `GatheringTokenGold:TakenReward_Common_Event` | `TakenRewardActor` | 5 | Skulltula House rewards |
| direct `EventTriggerAddOrRemovePouchContent` | `Actor` | 24 give, 25 take | Ocarinas, Master Sword, trade items, boss-rush loadouts |

Rewriting a gift is therefore one string parameter per call site, once EVFL can be written (round 2). Ending the
flow, the game opens the get window by actor name (`EventTriggerSetForGetWindow`), so item-get text follows the
new item [inference].

**Example 1: Saria's Song.** Event `Dm_MelodyGet_Saria` (EventSetting row of the same name; started by
`SacredForestMeadow` Event0 `EventTransition` and two `SacredForestMeadow_Child` logic modules). Timeline cut entry
`C12` → Event109 `SubFlow GetPouchContent:GetPouchContentByActorName {ActorName: Item_Melody_SariaSong}` → entry
`GetPouchContent` → Event0 `EventTriggerAddOrRemovePouchContent {Actor: ActorName, Num: 1}`. The flow sets no flag
itself; `HavePlayedEvent.Dm_MelodyGet_Saria` exists in `GameDataList`.

**Example 2: Din's Fire.** Event `Dm_FairyFountain_Din` (started from `TriForcePoint` Event56 `EventTransition`).
Cut entry `C15-01` → Event212 `SubFlow Dm_SY_GetInEvent:GetInEvent_GreatFairyDin {ActorName: Item_DinFire}` →
Event3 `GetPouchContent:GetPouchContentByActorName` → Event0. The flow sets `GreatFairy_MeetFirst`,
`Meet_GreatFairy_01`..`05`, `GreatFairy_AlreadyAppeared` and others; the map icon of a fountain is lit by
`HavePlayedEvent.Dm_FairyFountain_*`.

**Example 3: Skulltula House, 10 tokens.** Flow `GatheringTokenGold`, entry `TokenCheck_Reward` → Event40
`EventQueryIsGameDataInt {PouchData.Item_Token_Gold.StockNum, 10}` → Event48
`EventQueryIsGameDataBool {KakarikoVillage_GatheringTokenGold_GetReward10}` → Event398
`SubFlow TakenReward_Common_Event {TakenRewardActor: Item_Wallet_Medium}` → Event563
`Dm_SY_GetInEvent:GetInEvent_NotTurn` → Event90 `GetPouchContent:GetPouchContentByActorName_ForGetInEvent` →
Event0; back in the caller, Event199 sets `KakarikoVillage_GatheringTokenGold_GetReward10`. The other rewards are
Event75 `Item_AgonyStone`, Event194 `Item_Wallet_Large`, Event200 `Item_BombchuBundle_Large`, Event219
`Obj_Heart_Piece`, each gated by its own `..._GetReward20/30/40/50` flag.

## 5. Other kinds of check

| Kind | Actor / mechanism | Where | Count (unique) |
|---|---|---|---|
| Gold Skulltula | `Enemy_Skulltula_Gold` | 29 areas; per area equal to OoT Randomizer (table in 9) | 100 (114 placements) |
| Heart piece, freestanding | `Obj_Heart_Piece`, `Obj_GerudoValley_Heart_Piece` | DMC 2, DMT 1, Colossus 1, GV 1, Graveyard 1, HyruleField 2, Kakariko 2, ZoraFountain 2, ZoraRiver 2 | 14 |
| Heart piece, any source | `HeartPieceAnchor` (map icon); 21 carry `HeartPieceAnchor_GameDataPath`, the flag of an event heart piece (e.g. `MiniGame_FrogTenors_StormSong`, `GraveYard_DiggingHoleTour_Drop_HeartPiece`, `HyruleField_Enemy_Scrub_Business_HeartPiece_01`) | 14 areas | 36, OoT's total |
| Heart piece in a chest or prize | `Drop__DropActor: Obj_Heart_Piece` on chests (GV, GF, Graveyard ×2, HyruleField `A_01_memo11`, treasure game) | | 6 |
| Boss heart container | `Obj_Heart_Container`, placed in the dungeon's own Banc (boss room index) | Deku, DC, Jabu, Forest, Fire, Water, Shadow, Spirit | 8 |
| Small key, freestanding | `Obj_Dungeon_SmallKey` (BotW room 3, Shadow room 13); `Obj_Dungeon_SmallKey_GerudoFortress_01..04` (each twice, one named `SmallKeyForEvent_0x`); three `Enemy_MiddleBoss_GerudoThief*` drop GF keys via `Drop__DropActor` | | 2 + 4 |
| Silver rupee | `Obj_RupeeToken_Silver` | BotW 5, GTG 20, Ice Cavern 10, Ganon's Castle 20, Shadow 15, Spirit 15 | 85 |
| Shop slot | `Shop_*` actors with `ShopItemIndex` 1..7 (prices and sold-out boards are `Shop_Board_*`) | Kokiri, Market Bazaar, Market Potion, Bombchu, Kakariko Bazaar and Potion (both only in the adult file), Goron, Zora; Mask shop (7 indexed `Shop_Mask_*`) | 8 shops × 7 + 7 masks; 112 placements (some shops have 2 stock variants) |
| Business scrub | `Enemy_Scrub_Business` with `ScrubBusiness_ShopItemActorName0..2` (up to three offers) and `TalkEventName`; sale flows `Enemy_Scrub_Business_Common:SimpleShopSub_Scrub_Business_*` | HyruleField 5, LostWood 9, KokiriForest 2, DMC 1, BotW 1, DC 1, Jabu 1, Shadow 1; `DreamWorld` 30 | 21 + 30 |
| Cow | `Animal_Cow` (11), `_LinkHouse`, `_GerudoValley`, `_GerudoFortress`; milk via `Animal_Cow:PushToBottleMilk*` → `Dm_SY_GetInEvent:GetInEventInBottle {Item_Bottle_Milk}` | HyruleField 6, Kakariko 3, DMT 2, KF 1, GV 1, GF 1 | 14 |
| Great Fairy | events `Dm_FairyFountain_{Courage,Din,Frore,Nayru,Power,Wisdom}`, gifts `Item_FairyBless_DefenseDouble`, `Item_DinFire`, `Item_FaroreWind`, `Item_NayruLove`, `Item_FairyBless_MP`, `Item_FairyBless_MPDouble`; no NPC is placed in Banc, the fountain logic modules start them | fountains in DMC, DMT, Colossus, GanonCastle, HyruleCastle, ZoraFountain | 6 |

Two remake facts that matter for logic, from the data: cows record milk only in global flags
(`Cow_IsGetMilkFromCow`, `HaveTalked_Special.Animal_Cow_PushToBottleMilk_Event5`) and no cow has a per-actor save
flag, so a cow is not a one-time check as in OoT Randomizer. And the map-icon anchors tie the Death Mountain Trail
fountain to `HavePlayedEvent.Dm_FairyFountain_Din` and the Hyrule Castle fountain to `..._Power` (magic meter), and
a `HyruleCastle` logic module reads `HavePlayedEvent.Dm_FairyFountain_Power`: the reverse of N64, where Hyrule Castle
gives Din's Fire [inference, needs an in-game look].

## 6. How collected checks are recorded

`GameData/GameDataList.Product.110.byml.zs` is a **big-endian** BYML v7 (`BY`). `Data` holds 26 typed lists
(`Bool` 11292, `Bool64bitKey` 11657, `BoolExp` 884, `Int` 1259, `Struct` 874, `Enum` 130, ...). Entries carry a
`Hash`, `DefaultValue`, `ResetTypeValue` and `SaveFileIndex`; names are not stored. A flag's key is murmur3_x86_32
(seed 0) of its name, as in Tears of the Kingdom: 2540 of the 2565 `GameDataName` strings used in event flows hash
to an entry. `MetaData` names the save files (`slot_%02d/progress.sav`, `option.sav`, `slot_%02d/caption.sav`,
`account.sav`).

- **Placement checks are keyed by the actor `Hash`.** `Bool64bitKey` entries use a 64-bit key; 3686 of them equal
  a Banc actor `Hash`, including all 194 chests and 6 trap chests, all 100 Gold Skulltulas, all 13
  `Obj_Heart_Piece`, all 85 silver rupees and all 51 business scrubs. Checks use `ResetTypeValue` 24 (permanent);
  pots, rocks and grass use 88 plus an `ExtraByte`; scrubs 280. The other 7971 keys match no Banc `Hash` (1308 of
  them sit at ±2 from one); their source is open. So a chest's opened flag is its `Hash`, and changing only
  `Drop__DropActor` keeps it. A chest at a new `Hash` would need a new `GameDataList` entry [inference].
- **Event checks** have `HavePlayedEvent.<EventSetting row>`: all 2380 rows have such a `Bool`. Flows also gate
  repeats on their own named flags (`..._GetReward10`, `GreatFairy_AlreadyAppeared`, `HeartPieceAnchor_GameDataPath`
  values).
- **Inventory** is the `PouchData` struct; `PouchData.Item_Token_Gold.StockNum` is the token count the Skulltula
  House reads.

## 7. `RSDB` and the resource size table

`RSDB/` holds 20 `.rstbl.byml.zs` tables, all row tables keyed by `__RowId` or a name: `ActorInfo` (8363),
`GameActorInfo` (8363), `PouchActorInfo` (395, item categories), `EventSetting` (2380), `GameAnalyzedEventInfo`
(2379), `GameEventBaseSetting` (200), `GameEventMetadata` (333), `EventPlayEnvSetting` (7), `GameBancInfo` (80),
`DungeonParam` (24), `Location` (36), `Challenge` (45), `GameSafetySetting` (28), `RumbleCall` (122), `Tag`,
`TagDef` (168), `UIScreen` (62), `XLinkPropertyTable` (63), `XLinkPropertyTableList` (61), `LocatorData` (0). None
holds file sizes.

The size table is `System/Resource/ResourceSizeTable.Product.111.Nin_Ounce_NVN2.rsizetable.zs`: Tears of the
Kingdom's RESTBL (magic `RESTBL`, version 1, 219968 entries keyed by CRC32 of the romfs path without `.zs`, plus 10
named entries). **All 160 placement files have an entry**, and for every one entry = decompressed size rounded up
to 32 + 264; event flows use + 272, `GameDataList` + 288. Whether the game rejects a placement file larger than its
entry is untested; a grown file is the case to check in game.

## 8. `Banc/DreamWorld`

54 files = 27 stages × Static/Dynamic: 10 boss stages (`GohmaStage` ... `GanondorfStage`, `GanonStage`), 15
miniboss stages (`StalfosStage`, `DarkLinkStage`, `IronKnuckleBlackStage`, ...), `BossRushIntervalRoom` and
`EnemyMuseum`. `RSDB/GameBancInfo` lists them under `Work/Banc/Scene/DreamWorld/`. The flows `DreamBossStage`
(entries `Rematch_<Boss>`, `ConfirmRematch`, `TimeCountStart`/`Stop`), `SubEvent_AllBossBattle`, `Npc_Dream` and
`Enemy_Scrub_Business_Dream` run it; `LinkSleepInBed` reads `HavePlayedEvent.Npc_Dream_FirstTalk`, so it is
entered by sleeping in a bed [inference]. On entry
`UISystemActor.EventTriggertExchangeEnemyMuseumPouchAndState` swaps the inventory and
`EventTriggertRestorePouchFromEnemyMuseum` restores it, so its 10 chests (gold rupees, `IsEnableRepeatOpen`) and 30
scrubs (heart containers, Longshot, Biggoron's Sword, ...) are temporary: no checks. `GetPouchContent` tests
`EventQueryIsDreamWorld` to change the get message.

## 9. Against OoT Randomizer

OoT Randomizer `Dev` lists 2219 locations; without Master Quest 1404, of which 175 `Chest` and 100 `GS Token`. Its
area categories map onto Banc folders as in section 1. Here: chests unique by `Hash` outside `DreamWorld`; Market =
treasure-game boxes.

| Banc area | OoTR chests | chests here | OoTR GS | GS here |
|---|---:|---:|---:|---:|
| BottomOfTheWell | 13 | 12 | 3 | 3 |
| DeathMountainCrater | 1 | 2 | 2 | 2 |
| DeathMountainTrail | 2 | 1 | 4 | 4 |
| DesertColossus | 0 | 3 | 3 | 3 |
| DodongoCavern | 5 | 9 | 5 | 5 |
| FireTemple | 14 | 16 | 5 | 5 |
| ForestTemple | 13 | 12 | 5 | 5 |
| GanonCastle | 0 | 0 | 1 | 1 |
| GerudoFortress | 1 | 2 | 2 | 2 |
| GerudoTrainingGround | 21 | 22 | 0 | 0 |
| GerudoValley | 1 | 6 | 4 | 4 |
| GoronCity | 3 | 6 | 2 | 2 |
| Graveyard | 4 | 6 | 2 | 2 |
| HountedWasteland | 1 | 1 | 1 | 1 |
| HyruleCastle | 0 | 0 | 2 | 2 |
| HyruleField | 3 | 7 | 11 | 11 |
| IceCavern | 3 | 4 | 3 | 3 |
| InsideGanonCastle | 15 | 12 | 0 | 0 |
| InsideJabuJabuBelly | 3 | 4 | 4 | 4 |
| InsideTheDekuTree | 6 | 6 | 4 | 4 |
| KakarikoVillage | 2 | 3 | 6 | 6 |
| KokiriForest | 6 | 7 | 3 | 3 |
| LostWood | 1 | 1 | 3 | 3 |
| Market | 11 | 12 | 1 | 1 |
| SacredForestMeadow | 1 | 2 | 1 | 1 |
| ShadowTemple | 16 | 14 | 5 | 5 |
| SpiritTemple | 17 | 14 | 5 | 5 |
| WaterTemple | 10 | 9 | 5 | 5 |
| ZoraDomain | 1 | 1 | 1 | 1 |
| ZoraFountain | 0 | 1 | 3 | 3 |
| ZoraRiver | 1 | 1 | 4 | 4 |
| **total** | 175 | 196 | 100 | 100 |

Other kinds (OoTR without MQ / here): boss heart containers 8 / 8; heart pieces 35 + 1 / 36 anchors; songs 12 / 12
`Dm_MelodyGet_*` grants; Great Fairies 6 / 6; cows 9 / 14 placements without per-cow flags; shop slots 64 + 8 mask
/ 56 + 7 mask; scrubs 36 / 21 (+30 in `DreamWorld`); silver rupees 80 / 85; freestanding small keys 7 / 6 (GTG's
freestanding key not found).

**Identified differences** (each from the data above; the one-to-one match of chests by room and position is the
M1 census job):

- N64-only as checks: the 6 Ice Trap chests are trap chests here (section 2) and hold no item; cows are not one-time
  checks; shops have 7 slots, not 8; the GTG freestanding key.
- Moved: the Silver Gauntlets and Mirror Shield chests are in `DesertColossus`, not in the Spirit Temple file;
  Spirit is 14 + 1 trap here against 17.
- Remake-only: `DreamWorld` (temporary); the item `Item_ScrubBusinessSeed` (in 13 chests and as a scrub offer);
  Dampé's race has four goal chests (`Item_Hookshot`, `Obj_Heart_Piece`, `TBox_Rupee_Blue`, `TBox_Rupee_Red`, all with
  `GetEventName: MiniGame_DampeRace_OpenGoalTBox`, which records the opened one in
  `Minigame_DampeRace_TreasureBoxState`); more chests than OoT Randomizer lists, mostly rupees and
  `Item_ScrubBusinessSeed`, in the overworld (GV +5, GC +3, HF +4, Kak +1, KF +1, Colossus +1, ZF +1) and in
  dungeons (DC +4, Fire +2, Ice +1, Jabu +1); a cow in Gerudo's Fortress and extra cows in
  HF, Kakariko and DMT; Amiibo content (`Pouch_Amiibo`, `Armor_Child_Mask_Amiibo0/1`, chest blackboard
  `IsGeneratedByAmiibo`).
- Changed contents: many N64 ammo, heart and ice-trap fills are rupees or `Item_ScrubBusinessSeed` here, and some
  dungeons have fewer keys in chests (Water Temple 4 against 6), so the key logic of each dungeon must be rebuilt
  from this data, not ported.
- Changed placement (confirmed in game by Kareem, 2026-11-07): Din's Fire at the Death Mountain Trail fountain and
  the magic meter at Hyrule Castle (section 5).
- Gold Skulltulas: the count per area matches. Kareem first reported different places and a different Skulltula
  House reward table, then corrected the rewards (2026-11-07): they are N64's (10, 20, 30, 40 and 50 tokens, section
  4, example 3); the Stone of Agony only has a new name. Positions (Kareem and the Eurogamer and Polygon guides,
  2026-11-07): three N64 Gold Skulltulas are gone (the Hyrule Field grotto near Gerudo Valley with the webs, likely
  OoT Randomizer's `HF GS Cow Grotto`; Lon Lon Ranch's shed, likely `LLR GS Rain Shed`; and the ranch's cliff wall
  left of the tower, likely `LLR GS Back Wall`) and three new ones stand elsewhere. The other 97 keep their N64
  names, though several moved within their room or need other items: e.g. the Lake Hylia lab one is on the other
  side of the lab; the Fire Temple boss-key one and the Death Mountain Trail one near the crater entrance need the
  Megaton Hammer; the one on the ruined gate outside Ganon's Castle needs the Hookshot. The guides' text is in
  `E:/OOTRemake/work/r3/` (local only, copyrighted); facts from it may be used, its text may not.

## 10. In-game results (round 1, Kareem, 2026-11-07, Hookshot `movie-sync`)

Overlay `Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs` with two `Drop__DropActor` changes, loaded
through `HOS_FS_OVERLAY` (log: `fs: OpenFile(...KokiriForest_Child_Dynamic...): from the overlay`):

- A small chest in Mido's house (`Obj_TBox_A_01`, Hash 12786193094758345086) gave `Item_Boomerang` with the
  Boomerang's own get text and model. A small chest can hold a big chest's item.
- The Kokiri Sword chest (`Obj_TBox_A_02`, Hash 16757992849254467386) gave `TBox_Rupee_Red` with the rupee's text.
  A big chest can hold a small item. **But its `GetEventName` (`Get_StoneOfForest_GetSword`) then played the sword
  cutscene and put the Kokiri Sword in Link's hand, usable, though not shown in the inventory menu.** Story
  overrides grant or equip their vanilla item themselves: the patch plan must replace them (default open event)
  and handle the story state they set.
- The changed file was 510,920 bytes against the original 510,884 (+36). By the size-table formula it needed an
  entry of 511,208 and the table has 511,176; it loaded anyway, so small growth is tolerated. How much is untested.

Round 2 (Kareem, 2026-11-07, Hookshot `foliage-linux-updater`, new game): the Kokiri Sword chest with
`TBox_Rupee_Red` and its `GetEventName` removed (both KokiriForest `*_Dynamic` files) gave the Red Rupee through the
big chest's default event, with **no sword cutscene and no sword**. Removing a story override works; the story
state it would have set is the patch plan's to restore (`plans/rounds/r2-census.md`).

Round 2, freestanding items (Kareem, 2026-11-07, his save copy through `--user`, Hookshot `foliage-linux-updater`
then `main-ba594da`):

- Kakariko, Impa's cow-pen heart piece (Hash 17926402522258180222) with `Gyaml` `Obj_Rupee_Red` in the three
  KakarikoVillage `*_Static` files: a red rupee stands in its place (seen through the gate; not reached yet).
- Lon Lon Ranch tower heart piece (Hash 9814903750835309225) with `Gyaml` `Obj_Rupee_Red` in
  `HyruleField_Child_Static`: a red rupee there; picked up, with its text, and added to the wallet. In the save
  copies written afterwards neither Hash is set yet; whether a swapped rupee comes back after leaving (a pickup
  type that saves no flag would) is still to see.
- The same heart piece with `Gyaml` `Obj_Arrow_Fire`: three crashes out of three on the way (thread
  `OptimizeChangeBanc`, read of guest `0x4`, lr `0x809051ec`, the signature of Hookshot issue #287), each soon after
  `HyruleField_Child_Static` loaded from the overlay; with the rupee instead, the same route had none. The game's
  only `Obj_Arrow_Fire` (adult Lake Hylia) is a member of an `AiGroups` logic module (with an `EventRequestActor`
  and two `Area`s) and of the matching `SimultaneousGroups`/`FarDeleteGroups`; the moved one was in none. The
  inference is that this pickup needs its logic group; it is not tested. Major items lying in the world need a
  different actor or the group.

## 11. Round 3: size table, Gold Skulltulas, Treasure Chest Game, freestanding pick-ups (cs3b)

How each was found and the scratch scripts: `plans/rounds/r3-census.md`. Build `e0f3ccfa`.

**Resource size table** (`clawshot.formats.rstb`). Format: Tears of the Kingdom's RESTBL v1, plain zstd; 22-byte
header (`RESTBL`, version, name field size 160, counts), 219,968 `(CRC32 of the path without .zs, size)` entries sorted
by CRC, then 10 `(160-byte path, size)` entries, sorted by name, for paths whose CRC32 collides (none of them a
placement file, event flow or pack). Entry = decompressed size rounded up to 32 bytes + an overhead per type, checked
against every file of the type:

| Type | Overhead | Fit |
|---|---:|---|
| `.bcett.byml` | 264 | 160 of 160 |
| `.bfevfl` | 272 | 914 of 914 |
| `.sarc` (`Mals/`) and `.pack` | 312 | 16 of 16, 8384 of 8384 |
| `GameDataList` (`.byml`), `RSDB` tables | 264 | 1 of 1; 19 of 20 (`ActorInfo` +3064) |
| `.ainb` | 376 for `Logic/` | not fixed elsewhere (`Sequence/LoadBancImpl` +392, `AI/` +376 to +416) |

(Section 7's "`GameDataList` + 288" is the entry minus the raw size; minus the rounded size it is 264.)

**Gold Skulltulas.** The data marks the kind of spot: `Enemy_Skulltula_Gold_IsMagicBeanSoil` with a
`Gimmick_MagicBeanSoil_<Area>` presence flag (soft soil, 10: N64's 9 plus Zora's River's, which has none on N64), the
module `Gimmick_SwayingTree_Skulltula_Gold` (a tree to roll into, 5), `Gimmick_BoxBroken_Skulltula` or a link from an
`Obj_BrokenBox` (a crate, 5), and `Enemy_Skulltula_Gold_Nocturnal` with `Gimmick_Nighttime_Skulltula_Gold_Appear`
(night, 24 of 100). 97 keep an N64 location (linked in `locations.toml`; several moved, e.g. `ZR GS Tree` is now the
bean-seller soft soil and `Spirit Temple GS Sun on Floor Room` stands on the statue's hand); gone: `HF GS Cow Grotto`
(the cow grotto exists, with webs and a Skulltula, but no Gold Skulltula), `LLR GS Rain Shed`, `LLR GS Back Wall`;
new: a swaying tree in Hyrule Field near the Kokiri Forest entrance, an adult crate in a Hyrule Field grotto with a
Skullwalltula, and Lon Lon Ranch's tower vines. Coordinates in Banc are +x east, +z south.

**Treasure Chest Game.** The two reward boxes (`Obj_HrlCity_Shop_TBox_A_02`: Heart Piece, and a red rupee at the same
spot) are a census kind of their own, `treasure_game_reward`; the logic module `MiniGame_SequentialChoiceTreasure_cbde`
holds all twelve boxes. Every box names the model shown in it, `Dynamic.DropViewActor`; only five such view actors
exist (`Obj_Heart_Piece_MiniGame`, `Obj_MiniGame_SmallKey`, three `Obj_OrnamentalRupee_*_MiniGame`).

**Freestanding pick-ups.** All pick-ups inherit `Obj_Item_Base`; nothing a major pick-up's pack names is missing (the
shared AI is in `Pack/AI.Global.Product.111.pack.zs`). Every major pick-up the game places (Fire Arrows, Ruto's letter,
lures, keys, boss heart containers) is in a level prefab's logic group and `SimultaneousGroups`/`FarDeleteGroups`;
heart pieces and placed rupees are in none. Round 2's crash has the signature of Hookshot issue #287, but the fix
made for #287 (a null NVN texture builder answered with 0, in `main-ba594da`) did not stop it: round 2's last two
crashes ran that build and its log line never appeared, so the null read is elsewhere in the game's code. With a red
rupee in the same spot the same route had no crash. Major items with an `Obj_` pick-up: Fire Arrows, Deku and
Hylian shields, Goron and Zora tunics, Ocarina of Time, Bombchus, Ruto's letter, the lure, Amiibo masks, small keys;
the rest exist only as `Item_*` actors without pick-up components. Placed red rupees have `GameDataList` entries of
the permanent type (24) under their own Hashes, like the heart pieces.

**In game (Kareem, 2026-11-07, Lon Lon Ranch tower heart piece, fresh copies of his save, `hookshot-main` build
`main-ba594da`):** the red-rupee control worked, with the size table written by `formats.rstb` loaded from the
overlay (log: `...rsizetable.zs): from the overlay`); `Obj_Shield_Hylian` lay on the floor in place of the heart piece
(not picked up yet). With `Obj_Shield_Deku` the game hung while loading the save: the GPU device was lost
(`vk: submit ... failed (-4)`, checkpoints in a compute dispatch at frame 675; Windows logged `nvlddmkm` 153). Every
later start of that build lost the device the same way, the control included, so after that run the build or its
caches (moved to `E:/OOTRemake/work/hookshot-main/cache-1848-device-lost/`) were broken, not the variants; whether
the Deku Shield variant caused it is open. Tests 3 and 4 (chest at the heart piece) are to run again on the release
build.

Correction (Kareem, the same evening): the "hang" was the picture stopping on the loading screen while the game
went on; he could move, and picked up the **Hylian Shield** with the screen frozen. The first **Deku Shield** run
worked: a pick-up notice for the shield he already had, no duplicate. So two major `Obj_` pick-ups that belong to no
logic group work as freestanding items; the Fire Arrows crash belongs to that actor. Only the chest at the heart
piece is left to test.

## 12. Round 4: the remake's logic in the child areas (cs4a)

What the remake changed against OoT Randomizer's (N64) rules in the areas child Link reaches, as the overrides in
`src/clawshot/data/world/remake/child_<area>.toml` encode it. Per area, every rule checked, unchanged and open:
`plans/rounds/r4-logic-child.md`. Sources are remake walkthroughs (cited per entry, facts only) and the placement
files (actors listed by `E:/OOTRemake/work/r4-logic-child/actors.py`; room = `DefaultDungeonRoomIndex`, height =
Banc `y`).

**Inside the Deku Tree.** The lobby's 2F-to-3F vine wall carries three `Enemy_Skullwalltula` (y 113-116, above the
map chest on 2F at y 108) that the Slingshot clears; the basement opens only by dropping from 3F into the 1F web
(`Obj_InsideTheDekuTree_SpiderWeb_A_01`, y 100). So 3F, the compass room (room 3) and everything below 1F need the
Slingshot; OoT Randomizer's single "Lobby" region (floors 1-3) let the basement open without it, which made round
3's seed 3 unbeatable in game. The Slingshot room (room 2) has a breaking floating platform
(`Obj_InsideTheDekuTree_FallingFloor_A_01/02/03`) at its entrance and an eye switch (`Obj_EyeSwitch_A_02`, y 114)
with a falling ladder (`Obj_InsideTheDekuTree_FallingLadder_A_01`, y 116) above it: once in, Link leaves by shooting
the eye. Nintendo Life's Deku Tree walkthrough (Switch 2) agrees on each point.

## 14. A new game and its opening cutscenes (round 4, cs4c)

How it was found: AINB modules decoded with dt-12345's `ainb` 0.2.16 (GPL, unmodified, in a scratch venv under
`E:/OOTRemake/work/r4-fast-start/`), event flows from round 1's decode, the decoded placement files, `RSDB`
tables, and `clawshot.save` on Kareem's saves; his round 3 seed-3 run (`r3-seed/user-seed-3`, six autosaves from a
new game to the Deku Tree, 19:27 to 19:36) is the timeline. The writer is `clawshot.patch.gamedata` with
`src/clawshot/data/fast_start.toml`; details and checks in `plans/rounds/r4-fast-start.md`.

**New Game, step by step.** `Sequence/NormalTitle` (title menu) → `ConfirmationNewGame` →
`SeqExecuteResetGameData` (ResetType 3, then 5) → `OnResetGameData` → `Sequence/Opening`, with no flag test on the
way. `Opening` runs `SetPouchAndStatusForGameStart` (3 hearts: `Life`/`MaxLife` 12, no magic, small wallet, Kokiri
and adult tunics), changes to `KokiriForest_Child`, requests event `Opening_LoadingKokiriForest` (flow
`OpeningEvent`: `EventTransition Dm_Kokiri_0000`, the opening movie, then waits for the area to load and fades in)
and sets `Sequence_ReservedBootEventName = Opening_Introduction` (flow `OpeningEvent`: time 6:00, challenge
`Meet_DekuTree` to `Step01`, `Dm_Kokiri_0030` (the Deku Tree sends Navi, Navi wakes Link), Navi marked talked to,
autosave). The reset sets every entry to its `DefaultValue`; every per-slot story flag has `ResetTypeValue` bit 3
(8 or 24) and system entries (`Sequence_*`) have 0, so ResetType 3 resets bit 3 [inference from the values].

**The first autosave of a new game** (slot written right after the opening) differs from the defaults in 20 Bools
(`HavePlayedEvent` of `Dm_Kokiri_0000`, `_0030`, `Opening_Introduction`, `Opening_LoadingKokiriForest`,
`HaveTalked.Npc_Navi`, `IsGet.Armor_Adult_Normal`, ...), 7 Ints, no placement flag, and in the challenge enums:
`Meet_DekuTree` at `Step01` and 39 of the 45 challenges moved from `NotReady` to `Ready`, presumably by the
challenge manager (no flow or sequence of the opening names that step).

**Challenge progress is game data.** Each `RSDB/Challenge` row has an Enum `Step_<challenge>` in `GameDataList`
whose `RawValues` are its steps (`NotReady`, `Ready`, then the row's steps); flows move it with
`ChallengeSystemActor.EventExecuteProgressChallengeStep`, logic reads it with `HoldChallengeCurrentStepCheckOrder`
(outputs is-after, is-before, is-equal) and BoolExp entries such as `Meet_DekuTree_IsAfter_Step01_Exp`. Several
story triggers fire only at exactly one step (the Market arrival at `Goto_HyruleCastle` `Step02`, Zelda's
courtyard at `Step04`), so a skipped step can stop a chain. Whether a progress call can move a step backwards is
not known (the in-game test of `fast_start` `all` shows it).

**How cutscenes are gated.** In the world an `EventRequestActor` (`Dynamic.RequestEventName`) is driven by a logic
module (`AiGroups`, matched by reference `Id`) that ANDs an `Area` hit with flag tests, mostly
`HoldGameDataHavePlayedEvent` on the cutscene itself; flows test `EventQueryHavePlayedEvent` (case 1 = not played,
[inference] from how `Meet_DekuTree` and `Dm_SY_BancChangeArrive` branch). Placement `Presence.FlagName` hides or
shows actors by flag (the fog over the Deku Tree's face until
`HavePlayedEvent.Dm_Kokiri_0070`). Skipping is a game feature for every cutscene except three whose setting
component list sets `SkipSetting` `DisableSkip`: `Dm_Kokiri_0000` (the opening movie), `Dm_Title_0005` and
`Dm_StaffCredit_0005`.

| Scene | Event(s) | Gate | State it leaves | `fast_start` |
|---|---|---|---|---|
| Opening movie | `Opening_LoadingKokiriForest` → `Dm_Kokiri_0000` | none: `Sequence/Opening` | nothing read later | `intro`: skippable |
| Navi wakes Link | `Opening_Introduction` → `Dm_Kokiri_0030` | none: reserved boot event | `Meet_DekuTree` `Step01`, Navi talked | not offered (skippable already) |
| Saria at the door, Saria meets Navi | `Dm_Kokiri_0045` → `_0050`; `Dm_Kokiri_0060` | module `..._Npc_Kokiri_Saria_Child_a766` | `KokiriForest_LinkHouseDoor_Open`; house door module also opens on `HavePlayedEvent.Dm_Kokiri_0050` | `saria` |
| Mido's block | blocker AI | `KokiriForest_Npc_Kokiri_Mido_Child_Blocker` (default true) | flow `Npc_Kokiri_Mido_Child` clears it, `Meet_DekuTree` `Step02`/`Step03` | `mido` (logic: Mido no longer needs sword and shield) |
| Deku Tree's talk | `KokiriForest_Meet_DekuTree_MeetDekuTree_01` → `Dm_Kokiri_0070`, `_0075` | module `..._All_02_a798`, until `Meet_DekuTree` past `Step03` | `KokiriForest_Meet_DekuTree_OpenDekuTreeMouth`; `Meet_DekuTree` `Complete`; `Get_StoneOfForest` `GoInside` | `deku_tree` |
| Kaepora, Hyrule Field | `HyruleField_Goto_HyruleCastle_Kaepora` → `Dm_HrlField_0000`, `_0005`, `_0010` | module `HyruleField_Child_Prefab_de5f`: `Dm_HrlField_0010` not played, `Goto_HyruleCastle` not past `Step01` | `Goto_HyruleCastle` `Step02`; adds `Pouch_Amiibo` | `kaepora` |
| Kaepora, Lost Woods | `Dm_LostWood_0010` | flow `Dm_SY_BancChangeArrive` Event213 | none found | `kaepora` |
| Zelda's courtyard | `HyruleCastle_Goto_HyruleCastle_MeetZelda` → `Dm_HrlCastle_0030` ... `_0060` | module `HyruleCastle_Prefab_941f`: `Goto_HyruleCastle` exactly `Step04` | Zelda's Letter (`Dm_HrlCastle_0050`: `Dm_SY_GetInEvent:GetInEvent_Zeldaletter`), `Goto_HyruleCastle` `Complete`, `DoorOfTime` `Step01`; Impa then teaches Zelda's Lullaby (`DoorOfTime` → `Dm_MelodyGet_Zelda`) | not offered: it gives two checks (letter, song) |

Other Kaepora Gaebora scenes (Lake Hylia `Dm_LakeHrl_0010`/`_0011`, Death Mountain Trail `Dm_DeathMtTrail_0030`)
are flights or talks from his NPC flows (`Npc_Kaepora_*`) and are not offered.

**Not settable through initial values:** the opening movie and Navi's wake-up (sequence-driven), and anything that
must give an item (the pouch is not a flag). The intro can be removed entirely by starting
`OpeningEvent:Opening_LoadingKokiriForest` after the movie (an event-flow edit; a scratch test of it is in
`E:/OOTRemake/work/r4-fast-start/intro-removed`).

**In game (Kareem, 2026-11-07, Hookshot `foliage-linux-updater`, new games):** `intro` (the movie made skippable)
worked; he saved after Navi woke Link. `all` (`--skip intro saria mido deku_tree kaepora`) worked: he walked
straight to the Great Deku Tree. Its first autosave read `Step_Meet_DekuTree = Complete`,
`Step_Get_StoneOfForest = GoInside`, `Step_Goto_HyruleCastle = Step02`, `KokiriForest_Npc_Kokiri_Mido_Child_Blocker =
False`, `KokiriForest_Meet_DekuTree_OpenDekuTreeMouth = True`: the opening did not set the quest steps back.
`intro-removed` and the owl after the Deku Tree are not tested yet.

## 15. Round 4: event flows and gifts (cs4d)

How each was found and the scratch scripts: `plans/rounds/r4-evfl.md`. Build `e0f3ccfa`.

**Event flows** (`clawshot.formats.evfl`, written from the files and the ZeldaMods wiki's description; all 914 flows
write back byte-identical). Version 0.4.0.0: 653 files hold one flowchart, 261 one timeline (cutscene timing, cuts
named `C01`...), none both. Beyond the wiki's version: 0x30-byte events; event type 5 calls an entry point and
branches on the value a type-6 event there returns (583 returns); entry points may carry variables (5 do).
Thirteen flows exist in two versions, `X.bfevfl.zs` and `X.110.bfevfl.zs`; `Event/EventFlow/EventFlowFileEntry.
Product.110.byml.zs` lists those 13 with version `110` (the five medallion flows, Dampé's `Npc_Hylia_Dampe_001`, the
horse race, `DreamBossStage` and five cutscenes), so the game presumably loads the `.110` file [inference].

**Gifts.** Every gift is `PouchSystemActor.EventTriggerAddOrRemovePouchContent` with a literal item, reached directly
or through one of 64 wrapper entry points that pass an argument down (found by following `Argument` parameters to a
fixed point; section 4 named the main ones). Outside the scrub sales and DreamWorld, **148 steps give an item by
name**: 96 `npc_gift`, 26 `event_gift` (cutscene flows `Dm_*`), 26 `song`. Against OoT Randomizer: all 12 songs, all
9 boss rewards (stones and medallions), 8 of 9 cutscene gifts (not `Gift from Sages`) and 50 of 71 NPC checks are
given by a flow step; the 21 others are the 9 cows (D11), two placed pick-ups (`LH Sun`, `LH Underwater Item`), and
ten with no literal step (the five frog song rupees and `Frogs in the Rain`, loach fishing, the bowling bomb, the
treasure-game salesman's key, Granny's blue potion). Remake-only or unclear: a Market bottle
(`Npc_Hylia_020_Shop_Child`, entry `Item_Bottle_TutorialEvent_Talk`), a Deku Shield from the Kokiri shopkeeper (entry
`present_DekuSheld`), the frogs' bug game (a heart piece and a blue rupee), and the lake scientist's dive heart piece
in his *child-era* flow (`Npc_Hylia_045_Child`, OoT Randomizer's adult `LH Lab Dive`).

**Songs are granted twice.** Each `Dm_MelodyGet_*` flow first runs `Dm_SY_Ocarina:LearningOcarinaPlayAuto` (the
play-along), which adds the song the game's current melody state names (`EventQueryMelodyTypeForNormal`, 13 direct
steps shared by all songs), then gives the song by name through `GetPouchContent:GetPouchContentByActorName`.

**Changing a gift.** The item is one string parameter of the step (`ActorName`, `ReveiveItem` (sic), `Actor`,
`TakenRewardActor`); every wrapper ends in `Dm_SY_GetInEvent:*` or `GetPouchContent:*`, which show the item by actor
name, so the get model and text should follow [inference]; the NPC's own lines (`EventFlowMsg/...` message ids) and the
flags the flow sets do not change. A song needs its play-along changed too. Test folders for Talon's cucco game (milk
bottle -> Heart Piece, -> Boomerang) are in `E:/OOTRemake/work/r4-evfl/ingame/`; not yet run in game.
## 13. Round 4: adult remake logic (cs4b)

Audit evidence, unresolved alternatives and reproducible checks are in `plans/rounds/r4-logic-adult.md`.
Overrides are separate `src/clawshot/data/world/remake/adult_*.toml`; generated N64 rules stay untouched.
Guide facts are evidence for the described route, not proof of every alternative; unresolved routes are not
certified as remake-safe. Build `e0f3ccfa`; placement reads only, no game boot.

### Forest Temple

The front door now consumes a small key. The west lobby lock therefore needs two acquired keys and the
straightened corridor needs three. The Bow route still needs three and the frozen-eye hall five: the old
pre-Bow lock is absent. Read-only Static Banc inspection found five pairs of small-key locks at room
boundaries 0/1, 5/5, 9/10, 17/18, 20/23. The well switch/map route uses a Hookshot target; the east-garden
token uses the scarecrow. The frozen eye and rotating basement's new iced eye use arrows through a lit torch.

Sources (facts only):
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-forest-temple-walkthrough-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2#forest-temple
- https://www.ign.com/wikis/ocarina-of-time-remake/Biggest_Changes_and_Differences

Unsettled: ordinary-Hookshot west-garden access, hand collection of the entrance/basement tokens, Phantom
Ganon with Hookshot, Din's Fire at the iced eyes, N64 pots/drops and alternate traversal. Exact in-game
questions are in the round file. Five locks, not an N64 count plus a sixth inferred lock.

### Water Temple

The four-key graph, not just a cap: pillar lock → middle-water west lock → high-west falling-platform lock
reaches Longshot; fourth key (middle-water Bow/Longshot/underwater block room) opens the north basement lock.
The pillar basement chest is now a Red Rupee (Hash 11682974908842171598) and has a token in that room.
Compass moved to the south bomb/boots/Hookshot route. The old falling-platform token is in the Ruto-side
middle-water cracked room; the third key is instead past a middle-floor east bomb wall, underwater Stingers
and a geyser switch (room 4 Hash 16490222392193949581). The river exit uses Longshot targets, not Song of Time;
there is no river key chest. Nine chests/four keys in Banc agree with those routes. The boss slope uses Boots.

Sources:
- https://www.ign.com/wikis/ocarina-of-time-remake/Water_Temple_Dungeon_Walkthrough
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-water-temple-walkthrough-switch-2

`adult_water_temple.toml` moves checks as well as changing rules. Its retained unlinked N64 name
`Water Temple Cracked Wall Chest` for the east-geyser key is provisional world nomenclature, not a census
link. The normal route bootstraps all four keys and Longshot without free Water keys. Hookshot/Longshot
token ranges and N64 alternate traversal remain in-game questions in the round file.

### Fire Temple

Eight real keys/eight small-key locks. Acquired-key totals along the described remake route are 1 (lava bridge),
3 (past both east/elevator locks), 4 (narrow walkway and upper-boulder shortcut), 5 (flame maze), 7 (Flare Dancer/
Hammer), 8 (lower boss-key loop). Map is now in the lower boulder maze, Compass behind the narrow-walkway eye;
their event names say the opposite item, so use their drop actors. The old lower-maze side-key world name is
provisionally moved to the north flame-maze cell (room 11 Hash 10521366928524045067; not a new census link).
The pillar-lowered event follows Hammer and Song of Time; Hover bypass remains unverified.

Source: https://www.nintendolife.com/guides/zelda-ocarina-of-time-fire-temple-walkthrough-switch-2

The N64 free Fire key in `world.load._start_items` is not an actual remake starting item. Reviewer authorized
cs4b to remove that grant. The isolated route starts with zero Fire keys and collects all eight, Hammer and
boss key before reaching Volvagia. After removal, the default-path regression, whole-world vanilla beatability
test (with its documented up-front-key caveat) and 200 default generated seeds all passed.

### Adult shared overworld

- Goron City's adult token is on the ceiling: Hookshot, not adult age alone. The frozen Domain token likewise
  needs collection reach, not just Bow or Magic Meter.
- Water Temple entrance uses Iron Boots/Hookshot; the N64 Scale/Longshot alternative has no remake proof.
  The documented Fire Arrows route needs the lake restored by Morpha; low-water scarecrow collection is unverified.
- After Water Temple, the Domain thaws and its lake shortcut works as adult. Blue Fire on King Zora does not
  unseal the shop during Water Temple. Reopening after the whole-area thaw is provisional, not a traced flag.
- Zora Fountain's hidden cave uses Silver Gauntlets and Lenses; the extra bombable rocks were original-only.
- The crater wall-heart has a child heat-risk climb from the summit; the adult Tunic route is safe, without
  needing Hookshot. Eurogamer's explicit alternate route corrects Nintendo Life's nonexclusive Hookshot approach.
- The adult Poe Collector's bottle threshold is five; its world name remains `Market 10 Big Poes`.
- Light Arrows' documented route is all five adult sages. Reduced-medallion triggers need an in-game check.

Sources:
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2
- https://www.eurogamer.net/all-gold-skulltulas-locations-zelda-ocarina-of-time
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-biggeron-sword-trading-sequence-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-bow-arrow-fire-ice-light-arrows-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-bottle-locations-switch-2
- https://www.ign.com/wikis/ocarina-of-time-remake/Water_Temple_Dungeon_Walkthrough
- https://www.eurogamer.net/zelda-ocarina-of-time-death-mountain-crater
- https://www.eurogamer.net/big-poe-locations-in-zelda-ocarina-of-time

The per-area audit matrix (including adult rules checked unchanged in Kokiri, Lost Woods, Meadow, Field,
Ranch, Kakariko, Graveyard, Trail and River) and every unresolved category are in the round file. In particular,
reverse time travel after Forest is not represented chronologically by the monotone two-age search; that needs
engine review, not a Forest requirement on initial adult access. No complete-game safety claim is made.
