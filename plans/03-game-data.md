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
| 6 Flags | `GameDataList` keys named flags by murmur3 of their name; ordinary chests use named `IsTreasureBoxOpen.<Hash>` Struct Bools, while GS and heart pieces use saved actor-Hash `Bool64bitKey` contracts (section 44). Event checks: `HavePlayedEvent.<event>` plus named flags. |
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

- **Placement flag entries (metadata, not a universal collection oracle).** `Bool64bitKey` entries use a 64-bit key; 3686 of them equal
  a Banc actor `Hash`, including all 194 chests and 6 trap chests, all 100 Gold Skulltulas, all 13
  `Obj_Heart_Piece`, all 85 silver rupees and all 51 business scrubs. Checks use `ResetTypeValue` 24 (permanent);
  pots, rocks and grass use 88 plus an `ExtraByte`; scrubs 280. The other 7971 keys match no Banc `Hash` (1308 of
  them sit at ±2 from one); their source is open.
  **Superseded in round 11 (cs11b; section 44):** ~~So a chest's opened flag is its `Hash`, and changing only
  `Drop__DropActor` keeps it. A chest at a new `Hash` would need a new `GameDataList` entry [inference].~~
  Ordinary chests instead read the named Struct Bool `IsTreasureBoxOpen.<decimal actor Hash>`.
  A raw Bool64 entry's existence does not establish that a check uses it; section 44 distinguishes
  audited pickup/actor contracts and lists earlier chest-save checks needing re-verification.
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
map chest on 2F at y 108) that the Slingshot or Boomerang clears (Kareem via Claude, 2026-11-08); the basement
opens only by dropping from 3F into the 1F web (`Obj_InsideTheDekuTree_SpiderWeb_A_01`, y 100).
So 3F, the compass room (room 3) and everything below 1F need either weapon. OoT Randomizer's single
"Lobby" region (floors 1–3) allowed neither, which made round 3's seed 3 unbeatable in game.
The Slingshot room (room 2) has a breaking platform (`Obj_InsideTheDekuTree_FallingFloor_A_01/02/03`),
an eye switch (`Obj_EyeSwitch_A_02`, y 114) and falling ladder (`Obj_InsideTheDekuTree_FallingLadder_A_01`,
y 116). Slingshot or Boomerang activates that exit; Nintendo Life documented the Slingshot route.

**Rules that cross areas** (each as overrides in the area files; sources in them):

| Remake change | Evidence | In the logic |
|---|---|---|
| Time of day starts to flow only once Link has met Zelda | Eurogamer, "all new changes" | event `Time Flows` (HC Garden, child); every child `at_night` / `at_dampe_time` rule asks for it |
| Every grotto entrance is visible; the Stone of Agony became the Echo Gem, which finds Gold Skulltulas | Eurogamer, "all new changes"; `AgonyStoneReactArea` only at Gold Skulltulas | `can_open_bomb_grotto` -> `can_blast_or_smash`, `can_open_storm_grotto` -> `can_play(Song_of_Storms)` |
| Bomb and Song of Storms grottos have different covers | data: storms covers are `Land_Kokiri_HidingHoleCover_A_01` with an `EventProxyRequestActor`; bomb covers `Land_<Area>_HidingHoleCover_*` or a rock | Hyrule Field's tektite and ReDead grottos open with the Song of Storms |
| Zelda's Lullaby calls every Great Fairy but Death Mountain Trail's (Din's) only once Din's Fire is held; each fairy's fee is fixed (25 to 500 rupees) | flows `TriForcePoint`, `Dm_FairyFountain_*` (below) | the five other rewards ask for `Dins_Fire`, Colossus and OGC also for `Progressive_Wallet` |
| Every magic item carries the magic meter | `PouchActorInfo` `ExpansionAvility: MPMaxUP` (below) | `[items]` aliases in `remake.toml`: each counts as a `Magic Meter` |
| The Door of Time is the vanilla one (three stones, the Ocarina of Time, the Song of Time) | flow `DoorOfTime`, `Market_Child_DoorOfTime_OpenDoor` | OoT Randomizer's `open_door_of_time` setting is not read |
| Kaepora Gaebora flies Link from the summit only once Din's Fire is held | flow `Npc_Kaepora_DeathMountainTrail` (`IsGet.Item_DinFire`) | `DMT Owl Flight` asks for `Dins_Fire`; Impa's cow-pen heart piece is reached only by the owl |
| Many N64 grotto contents are gone: the grotto Deku Scrubs of Zora's River and Lake Hylia, Hyrule Field's three generic grotto chests and the tektite heart piece, the DMT storms grotto chest, the Royal Family's Tomb chest | placement data per grotto | `n64_only` with the actors found instead |
| Bombchu Bowling opens after Dodongo's Cavern; the shooting gallery's child prize is a bullet bag | flows `MiniGame_BombchuBowling`, `MiniGame_HitTarget` | `'Defeat King Dodongo'`; `vanilla_fixed` |

**Dungeons.** Dodongo's Cavern: a bombable wall (`WallCrack` 13202633467597206724) separates the Bomb Bag ledge from
the bridge over the skull, which OoT Randomizer joins; the entrance boulder breaks only by the bracelet's bomb flower
(scripted, no damage component). Jabu-Jabu: the map chest is in the water-switch room, before the Boomerang. Bottom
of the Well: the four chain locks sit on two doors (the central rooms); the Fire Keese and Like Like rooms need no key;
there is no bomb flower. Ice Cavern: no heart piece, no loose rupees; a pool past the White Wolfos drops into Zora's
Fountain (Iron Boots).

**Great Fairies (item 6, from the data; build `e0f3ccfa`).** Scratch scripts in `E:/OOTRemake/work/r4-logic-child/`:
`fairy_logic.py` (the flows' logic, cutscene actions dropped, with `clawshot.formats.evfl`), `msbt_dump.py` (texts,
`Mals/USen`), `rsdb_rows.py`, `gd_lookup.py`, `tfp_params.py`. Each fountain's Triforce symbol is an
`Obj_TriForcePoint_A_0N`; its `RSDB/EventSetting` row names the entry of flow `TriForcePoint` it runs, and that entry
calls `Sub_PlayOcarinaSequence_FairyFountain` with a `SpecialAbility` number and then the fairy's own flow:

| Banc area (actor) | `TriForcePoint` entry, `SpecialAbility` | Fairy, flow | Gift (`Dm_SY_GetInEvent`) | Fee (`EventQueryHasRuppe`, `Pay`) |
|---|---|---|---|---|
| DeathMountainTrail (`A_02`) | `Demo_FairyFountain_Din`, 2 | `Dm_Npc_GreatFairy_002`, `Dm_FairyFountain_Din` | `Item_DinFire` | 25 |
| HyruleCastle (`A_01`) | `Demo_FairyFountain_Power`, 1 | `Dm_Npc_GreatFairy_001`, `Dm_FairyFountain_Power` | `Item_FairyBless_MP` (stronger spin attack, magic 24) | 50 |
| ZoraFountain (`A_03`) | `Demo_FairyFountain_Frore`, 3 | `Dm_FairyFountain_Frore` | `Item_FaroreWind` | 100 |
| DeathMountainCrater (`A_04`) | `Demo_FairyFountain_Wisdom`, 4 | `Dm_FairyFountain_Wisdom` | `Item_FairyBless_MPDouble` (magic 48) | 200 |
| DesertColossus (`A_05`) | `Demo_FairyFountain_Nayru`, 5 | `Dm_FairyFountain_Nayru` | `Item_NayruLove` | 300 |
| GanonCastle (`A_06`) | `Demo_FairyFountain_Courage`, 6 | `Dm_FairyFountain_Courage` | `Item_FairyBless_DefenseDouble` (damage halved) | 500 |

This is Kareem's guide table: the summit fountain gives Din's Fire, Hyrule Castle's the "Gift of Improved Spin"
(the Power fairy's text: "I've made your spin attack stronger"; the item is also a magic meter).

- **Who can be met first.** `Sub_PlayOcarinaSequence_FairyFountain`, after the Lullaby, switches on
  `EventQueryFairyFountainSelectSpecialAbility`: ability 2 (Din's) goes straight on; every other value first asks
  `IsGet.Item_DinFire`, and without it Navi says "It doesn't seem like anything happened, but... I do sense some kind
  of mysterious power here" (`Dm_FairyFountain_Power` `Talk_00` once `Get_StoneOfFire_IsCompleted_Exp`, before that
  `Talk_02`, which adds "Let's come back later") and the fairy does not appear. So the first fairy is Din's, and the
  gate is the item, not the visit: in a seed, Din's Fire found anywhere opens the other five [inference: `IsGet` is
  set however the item is got]. `GreatFairy_MeetFirst` only picks the greeting ("It seems I'm not the first Great
  Fairy you've met" for the others). Din's gift, with no magic yet (`PlayerStatus.MPMax` 0), shows the magic gauge
  being born (`GreatFairy_HasNoMPOnDinDemo`). The guides' "Death Mountain Trail or Hyrule Castle first" is wrong for
  Hyrule Castle.
- **Kareem's question: Improved Spin before Din's Fire? No.** The Hyrule Castle fairy does not come without Din's
  Fire. Neither gift asks for the magic meter or for another fairy met: `Dm_FairyFountain_Power` checks only
  `HavePlayedEvent.Dm_FairyFountain_Power`, `IsGet.Item_FairyBless_MP` and the rupees.
- **Fees are fixed per fairy**, not rising per visit: each flow asks one constant (`HasRuppe` 25, 50, 100, 200, 300,
  500, matching the text variables `GreatFairy_Price1..6`, unsaved `Int`s). Track B's "rises with each visit" is the
  guides' usual visiting order.
- **Without the rupees** the fairy says "Seems you don't have enough rupees... Come back once you've saved up N
  rupees" (`DontPay2`), the event quits (`EventRequestQuit`) and nothing is lost: the next Lullaby offers again
  (`VisitedNoAbility`). Saying no to the offer (`DontPay1`) is the same.
- **Wallets** (`RSDB/PouchActorInfo`, `AfterExpansionMaxNum`): `Item_Wallet_Small` 200 (the rupee's `SmallBagActor`;
  a new game starts with it, section 14), `Item_Wallet_Medium` 500 (OoT Randomizer's Adult Wallet, 10 tokens),
  `Item_Wallet_Large` 1000 (Giant Wallet, 30 tokens). Fees up to 200 fit the start; Nayru (300) and Courage (500)
  need the Adult Wallet.
- **The magic meter comes with every magic item.** `PouchActorInfo` gives `Item_DinFire`, `Item_FaroreWind`,
  `Item_NayruLove`, `Item_GlassTruth` (Lens of Truth), `Item_Arrow_Fire/Ice/Light` and `Item_FairyBless_MP`
  `ExpansionAvility: MPMaxUP`, `MPMax: 24` (`Item_FairyBless_MPDouble` 48), and the item-get flow
  `Dm_SY_Get:PouchAddItem` calls `MPOpen`, which shows the gauge being born when `PlayerStatus.MPMax` is 0. OoT
  Randomizer's `can_use` asks for the item and `Magic_Meter`; here each of those items counts as one `Magic Meter`
  (an `[items]` alias, `plans/04-world-format.md`).
- **For the seed patch.** The flows use each gift's own `IsGet` as "already given" (Din's `IsGet.Item_DinFire`,
  Power's `IsGet.Item_FairyBless_MP`, ...) and `IsGet.Item_DinFire` as the gate for the other five. A seed that puts
  another item at a fountain, or Din's Fire elsewhere, must keep both working as the logic assumes [inference].

**In game (Kareem, 2026-11-08, `E:/OOTRemake/work/r5-seed/seed-shop-7`, child with the Kokiri Sword and a Hylian
Shield, no Deku Shield):** the Deku Tree room before the Slingshot room locks Link in with a Deku Scrub. The sword
and Deku Sticks can't reach it, Deku Nuts don't stop it, and **a child's Hylian Shield does not reflect its nuts**.
So OoT Randomizer's `here(has_shield)` (a child needs the Deku Shield) holds in the remake; the seed's logic asked for
it (the Deku Shield at KF Shop Item 6, after Mido), but its play note named only the Hylian Shield. Whether the
Slingshot or Boomerang beat the scrub is untested (Kareem expects they do; both are inside that seed's Slingshot
room).

### Round 6 play findings (cs6f, Kareem via Claude, 2026-11-08)

`seed-shop-7`, dump build `e0f3ccfa`, Hookshot 2.0.1. No agent game run. Exact data trace and checks:
`plans/rounds/r6-play.md`; regressions: `tests/test_world_remake_play.py` and `test_world_remake.py`.

- **Deku Tree:** Boomerang activates the Slingshot-room exit switch, clears the vine-wall climb and stuns
  Gohma. Static room 2 eye Hash 9080063866993537303 drives ladder 2096903280161003875 through
  `InsideTheDekuTree_Level_Room_C_Prefab_efa7`. The basement room 5 eye 10433048972954508847 is the same
  `Obj_EyeSwitch_A_02`, without a weapon override, so its rule also accepts Boomerang; this shared-actor
  deduction is data evidence, not a separate observed basement test. Gohma's rule adds Boomerang as a
  stun, **not damage**: jumpslash stays required. Fire and Deku Shield scrub gates stay. Adult vine-wall
  alternatives and save/game-over recovery with neither ranged weapon remain unanswered (DT01/DT02).
- **Castle moat (HF01):** shallow; no Silver Scale needed for the Ocarina. Child Static places
  `Obj_Ocarina_Time_A_01` Hash 2802436684568022035 at (16,145,43). **Round14 correction,
  section46:** the old stones-only rules omitted the native courtyard/Impa story prerequisite;
  that static correction does not invalidate Kareem's played no-scale finding.
- **Free Kokiri Deku Shield (GIFT02):** child with Kokiri Sword/Hylian Shield, no Deku Shield, received one
  after Mido without buying it; the shelf still sold one at 40. `Npc_Kokiri_001_Shop_Child:Talk`
  Event23/21 take this branch only while `Goto_HyruleCastle` and `Get_StoneOfForest` are incomplete;
  Event1 requires `Meet_DekuTree_IsAfter_Step02_Exp`. `present_DekuSheld` Event45 checks Deku Shield
  **equipped**, not ownership or Hylian Shield. There is no rupee, sword or shelf-content check.
  Event63's first-talk flag false reaches grant Event117 then sets the flag (Event44); true reaches
  grant Event116. **It is not once-only:** the flag changes dialogue, correcting section 19's old
  characterization. Repeat grants/late cutoff are traced in the data, not yet corroborated in game.
  Logic adds the `Deku Shield` event at `KF Kokiri Shop` after a child can reach the tree beyond Mido:
  talk to the tree (advances the meeting quest even with Mido skipped), return to the shop before Gohma.
  This monotone event records an earlier obtainable shield; it does not assert the offer survives the
  early-story window. It cannot supply a shield to pass kept Mido with no initial shield.
  **Not a shuffle check as-is:** both grant branches and the equipped test need a real once-gate rewrite
  before a randomized reward is safe. No pool item or gift patch changed.


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

### Shadow Temple

Five real small keys, with the fifth lock on the spike-wall room containing the Boss Key, not on the boss
approach. Locking the Boss Key chest behind five keys prevents placing the fifth key behind its own door.
The post-boat cracked-pillar bridge uses Bomb Bag rather than N64's Bow/Bomb Flower solution. No Bomb
Flowers or Time Blocks are placed, so Bracelet-based bomb supply and the old Time Block bridge bypass
are unsupported. The maze entrance has a burnable/explodable web.

The old single-pot token moved to the fan corridor (Longshot); the boat token needs Scarecrow. The triple-pot
token appears only after bombing its skull. Invisible Spikes and Falling Spikes Upper are absent N64 chests;
the falling-spikes floor Red Rupee and upper small key remain. The isolated route starts with zero keys,
collects all five and wins. Fan-corridor Iron Boots and alternate combat/grapple ranges remain in-game
questions, not additional inferred gates.

Sources:
- https://www.eurogamer.net/shadow-temple-walkthrough-zelda-ocarina-of-time
- https://www.ign.com/wikis/ocarina-of-time-remake/Shadow_Temple_Dungeon_Walkthrough
- https://www.eurogamer.net/all-gold-skulltulas-locations-zelda-ocarina-of-time
- Banc/ShadowTemple placement and skull-pot/web actor parameters, read-only, build `e0f3ccfa`.

### Spirit Temple

Five real keys/five ordinary locks retain the existing age-unknown/worst-order key model. The statue-floor
token needs no ranged weapon; the former child-climb token is by Pierre beside the statue's hand (adult
Longshot/Scarecrow). Lullaby spawns the hand key, then the documented collection route also uses Pierre.
The sun-block key now uses window light, not torches or the silver-rupee door trigger. Child Climb East
and Statue Northeast are absent N64 chests.

The live adult-boundary search starts with three earlier keys and collects hand key, Mirror Shield, fifth
key and Boss Key before winning. This does not resolve the inherited cross-age key abstraction or prove
chronological child-to-adult play. Short-Hookshot ranges and lensless combat remain questions in the round file.

Sources:
- https://www.eurogamer.net/spirit-temple-walkthrough-zelda-ocarina-of-time
- https://www.eurogamer.net/all-gold-skulltulas-locations-zelda-ocarina-of-time
- Banc/SpiritTemple placements, read-only, build `e0f3ccfa`.

### Gerudo Training Ground and Gerudo overworld

The Like Like room opens from the Wolfos room's Silver Gauntlets block/invisible eye, not from the upper
eye-statue ledge. Lobby and heavy-block chest-name pairings remain unresolved: both candidate locations
conservatively require the union of their prerequisites. The near-scarecrow key needs the floor eye-statue
Bow puzzle and a return route to its upper door. Lava approaches require Tunic on the documented safe route.

The ninth key is chest Hash `1883068192328530224` in the maze by the lava door. World restoration (`fa9ed2b`,
cs4a) and census link (`f3fb5ef`, cs4d) are integrated through the authorized rebase onto `ab941d2`.
Adult overrides do not duplicate the root entry. Existing maze worst-order key counts remain.
Valley/Fortress storm grottos need the song, not Stone of Agony: entrances are visible and the old item became the Echo Gem.

Sources:
- https://www.eurogamer.net/gerudo-proving-grounds-walkthrough-zelda-ocarina-of-time
- https://zeldacentral.com/games/ocarina-of-time-remake/walkthrough/gerudo-proving-grounds/
- https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2
- Banc/GerudoTrainingGround block/eye/wall and placement data, read-only, build `e0f3ccfa`.

### Desert Colossus

The old tree token is now on the north-west cliff, in both age variants: adult Longshot or child Boomerang.
The grotto under the lift rock holds a purple-rupee chest, not the two N64 business scrubs; those scrub
locations are excluded rather than falsely naming the new chest. Fairy visit-order/fees and bean/hover
alternatives remain the round file's integration/in-game questions.

Sources:
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2#gold-skulltula-95
- https://www.eurogamer.net/all-gold-skulltulas-locations-zelda-ocarina-of-time
- Banc/DesertColossus child/adult placements, read-only, build `e0f3ccfa`.

### Ganon's Castle/Tower and remaining desert findings

Fire entrance and Shadow's exit stone require Golden Gauntlets. Shadow's first torch accepts an ordinary
arrow through the lit torch, not just Fire Arrows; its exit uses a floor switch, not Hammer. Forest's wind
trial needs Time/Hover/grapple traversal; Spirit has a ceiling web requiring fire before reflected light.
Light's Lullaby chest is before the single lock and gives a Green Rupee, not a second small key. Both its
rule and vanilla item are corrected; a one-key rule cap alone had left a phantom second key in the pool.
Four castle scrubs and Spirit Invisible Chest are absent. A live six-trial route wins with exactly one key.

The root override owns Shadow's Golden Gauntlets chest; its Lens-path rule needs an owner-side update,
recorded in the round file, rather than a duplicate adult entry. Night/first-fairy/fees, lensless paths,
grapple ranges and plain-arrow fire transfer remain explicit review/in-game questions.

Valley's ledge heart is a Chest; obsolete grotto scrubs, hive, eight underwater rupees and its old heart crate
are excluded. Fortress's child freestanding heart is absent; HBA thresholds are 750/1,400 (old names retained).
Wasteland retains one physical crate, provisionally the Colossus-side name; its Business Scrub Seed chest
needs a world-item representation before vanilla-pool parity can be claimed. Colossus fairy wall accepts
Hammer and explosions, corroborated by its actor parameters.

Sources:
- https://www.eurogamer.net/inside-ganondorfs-castle-walkthrough-zelda-ocarina-of-time
- https://www.eurogamer.net/zelda-ocarina-of-time-mirage-desert
- https://www.eurogamer.net/zelda-ocarina-of-time-gerudo-valley
- https://www.eurogamer.net/zelda-ocarina-of-time-gerudo-fortress
- https://zeldacentral.com/games/ocarina-of-time-remake/great-fairy-fountains/
- Read-only Banc inventories and Colossus cracked-wall actor parameters, build `e0f3ccfa`.

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
| Opening movie | `Opening_LoadingKokiriForest` → `Dm_Kokiri_0000` | none: `Sequence/Opening` | nothing read later (round 13 audit below) | `intro`: removed by event-flow bypass (round 13; originally only made skippable) |
| Navi wakes Link | `Opening_Introduction` → `Dm_Kokiri_0030` | none: reserved boot event | `Meet_DekuTree` `Step01`, Navi talked | not offered (skippable already) |
| Saria at the door, Saria meets Navi | `Dm_Kokiri_0045` → `_0050`; `Dm_Kokiri_0060` | module `..._Npc_Kokiri_Saria_Child_a766` | `KokiriForest_LinkHouseDoor_Open`; house door module also opens on `HavePlayedEvent.Dm_Kokiri_0050`; `_0045` Event7 opens the Kokiri area banner, setting `IsVisitLocation.KokiriForest` | `saria` (round 13 also preserves the visit flag) |
| Mido's block | blocker AI | `KokiriForest_Npc_Kokiri_Mido_Child_Blocker` (default true) | flow `Npc_Kokiri_Mido_Child` clears it, `Meet_DekuTree` `Step02`/`Step03` | `mido` (logic: Mido no longer needs sword and shield) |
| Deku Tree's talk | `KokiriForest_Meet_DekuTree_MeetDekuTree_01` → `Dm_Kokiri_0070`, `_0075` | module `..._All_02_a798`, until `Meet_DekuTree` past `Step03` | `KokiriForest_Meet_DekuTree_OpenDekuTreeMouth`; `Meet_DekuTree` `Complete`; `Get_StoneOfForest` `GoInside` | `deku_tree` |
| Kaepora, Hyrule Field | `HyruleField_Goto_HyruleCastle_Kaepora` → `Dm_HrlField_0000`, `_0005`, `_0010` | module `HyruleField_Child_Prefab_de5f`: `Dm_HrlField_0010` not played, `Goto_HyruleCastle` not past `Step01` | `Goto_HyruleCastle` `Step02`; adds `Pouch_Amiibo`; `_0000` history ends the post-Saria scene-BGM mute interval (section46) | `kaepora` (round14 also preserves `_0000` history) |
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

**Round 13 corrections (2026-11-12, cs13a):** the all-skips result above did not test kept Mido.
Pre-completing the meeting selects his later scheduled talk and leaves the invisible wall's
saved blocker true. The first cross-entry wrapper then **hung in game**: its later entry
did not register the newly reachable subflow calls. It is removed. With Mido kept, the tree
skip now retains the native early meeting state, schedule, Talk and clear, and applies the
four tree-talk values only after that clear. With Mido bypassed, the initial Complete/mouth
presets remain. Saria's skip also omitted the forest visit flag, because her `_0045` Event7
opens the area banner. The initial-value patch now sets `IsVisitLocation.KokiriForest=true`
only with `saria`; intro alone retains the Saria/banner route.
The pause-map lead came from Kamil's Hookshot Randomized findings, section 5 (2026-11-12, MIT;
facts verified independently against native flows, RSDB and historical saves; no code copied).
Trace, regression proof, external source path, acceptance result and checklist:
`rounds/r13-fast-start.md`.
The round 13 `intro` flow transform removes the movie transition, starts at the native forest-load
check, and replaces the redundant post-movie wait with a one-frame yield while loading. Pouch/status
initialization, fade and reserved Navi wake-up remain. It does not pre-set the forest visit flag;
the Saria/banner route is unaffected unless `saria` is also selected. **Kareem, via Claude,
2026-11-12 11:35–11:46:** movie entirely skipped, later scenes skippable; forest pause map opens;
Mido stands in the middle, refuses sword-only, clears after a shield is added (saved blocker
true -> false at 11:40); tree dialogue absent and mouth open. Runtime loading proof is in the
round record. **Native-Mido + reload acceptance PASSED (16:45–16:47):** Kareem confirmed
normal Mido dialogue and an open Deku Tree mouth after Continue; the save retained blocker
false and completed meeting state, with no crash and the expected mod-loading evidence.
In the earlier run, the Map chest played its map text/animation but left
`DungeonInfo.InsideTheDekuTree.IsGetMap=false`: Claude assigned this separate own-dungeon
map/compass credit bug to cs13c; this fast-start fix stands.

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

## 16. Round 5: age travel (cs5a)

Evidence and exact flow nodes: `plans/rounds/r5-age.md`, item 1; build `e0f3ccfa`. No game launched.

The normal first pull follows all three stone quests, the moat Ocarina of Time and Song of Time, and opening
the Door of Time. `DoorOfTime:DoorOfTime_OpenDoor` checks quest progress beyond Step04, the recommended melody
(4), and the door/scene not already done; it sets `Market_Child_TimeTempleDoor_Opened` and Step06.
The first-pull attention request (`Market_Child_Prefab_e700`) requires DoorOfTime exactly Step06.
Stone items and Ocarina of Time inventory are not independently queried there: chest-only logic keeps the
conservative vanilla route; independently shuffled gifts need to preserve quest progression.

Adult return is gated by `SageOfForest_IsCompleted_Exp`, not Forest Medallion or Prelude inventory.
`Market_Adult_Prefab_89da` deletes the pedestal attention actor while that expression is false.
GameDataList defines it from Enum `Step_SageOfForest` and `Complete`; the Forest blue-warp completion chain
sets Complete in `Dm_SY_BancChange_EscapeDungeon` Event199.
`Market_Adult_Field_AdultToChild` then plays the return scene and changes era.
`Market_Adult_Firsttime_GobacktoChild` is checked only after the era change: setting it cannot unlock return.
There is no independent initial-value Bool for free travel; forcing the Forest quest complete has broader
story effects and is not a safe substitute.

Published corroboration (facts only):
https://www.nintendolife.com/guides/zelda-ocarina-of-time-forest-temple-walkthrough-switch-2
describes return travel and Prelude after Forest Temple.
All eighteen saves inspected in the two original directories and the nested
`2026-11-08_0802-before-adult/save/<user>/` backup are child-era (`Sequence_IsChildhood = true`,
`Step_SageOfForest = Ready`), so they do not corroborate current adult progress.
**Kareem: check the adult pedestal before and after the Forest blue warp, and supply adult save copies.**

The search keeps an independent pre-pull child inventory until the Forest completion event and an adult route
to `Beyond Door of Time` both hold. Adult-found items, aliases and events cannot unlock child checks before
that return; child checks available without adult finds can all be collected before the first pull.
The gate is data (`world.toml` settings), not a Forest Medallion inventory test.

`age_return_guarantee = true` is the reviewer's provisional default: cap each count in actual child-only
collection to find its mandatory first-pull minimum, then prove adult can open return using only those
minima, starting inventory and adult checks. Optional child loot cannot satisfy that proof.
Turning the guarantee off retains temporal correctness but permits early-pull softlocks.

The fill enforces a return kit first, rather than hoping the oracle accepts a random placement.
Shuffled strength-family sources stay in adult-only checks: otherwise child could find Silver/Golden
Gauntlets, bypass Saria's unshuffled bracelet gift, pull early and leave adult unable to pass Mido.
This preserves Saria's Song as a compulsory child dependency of the first pull. Bow, grapple sources,
strength tiers and Forest keys are forward-placed at adult-reachable checks before ordinary assumed fill;
small keys bootstrap from zero before a boss key can occupy the entrance-key chest.
The fill's data-defined lower bound is Saria's Song, strength 1, Ocarina 2 and Song of Time, not optional child
loot. The independent actual-placement oracle still verifies those assumptions on every finished seed.

### Isolated free-travel setting (off)

No fake GameData default: `patch/age.py` changes only AiGroup Hash 2075259738076588912 in
`Banc/Market/Market_Adult_Static.bcett.byml.zs`. It substitutes the existing ungated module
`SpiritTemple_Prefab_5299` (attention actor `ReceiveDoAction` → event request, default `Logic_Delete = false`)
for `Market_Adult_Prefab_89da`, rebinding its two input Ids to the existing actors. Actor Hashes, paths,
transforms, the adult-to-child request, every other group, event flows and GameDataList stay unchanged.
With `free_time_travel = true`, `make_seed` adds this transform automatically and the search uses free travel;
the extra return guarantee does nothing. Default remains false pending the in-game test.

The overlay grows 30,540 → 30,596 decompressed bytes; the common writer raises the resource entry
30,824 → 30,888. Output and play instructions:
`E:/OOTRemake/work/r5-age/free-time-travel/` and `free-time-travel-check.md`.
The dump oracle verifies that the only tree changes are that group's Logic and its two References' Ids.

### Why not force the Forest quest complete?

The gate protects more than travel; the isolated patch leaves all these readers untouched:

| Reader | What the quest/completion value controls |
|---|---|
| `Dm_SY_BancChange_EscapeDungeon` Event204 | first Forest clear enters SageRoom with boot event `ForestTemple_SageOfForest_SageRoom`; the completed branch does not repeat that first-clear route |
| same flow Event211/Event213/Event199 | Saria's sage scene (`Dm_Awake_Forest`), Forest reward (`Dm_Awake_Forest_Get`), then actual quest completion |
| `Market_Adult_Prefab_edc2` | Sheik/Prelude's separate area trigger requires Forest completion; early return does not teach Prelude |
| `SageRoom_520d`, `LostWood_Common_7c9e` | exact Step09 checks on the Forest sage/return sequence |
| `ForestTemple_Level_Room_02_*`, `...Room_22_Prefab_c724` | Poe quest substeps and later Step07/Complete conditions |
| `KokiriForest_Adult_Level_All_01_796d`, `HyruleField_Child_Prefab_c27b` | completion-dependent area logic |
| `LostWood_Adult_Prefab_33c5`, Mido/NPC/shop flows | post-Forest interaction variants; Mido's nearby state |
| `Dm_SY_BancChangeArrive` Event507, `Dm_SY_Ocarina_SariaSong` Event42 | post-Forest arrival and Saria's Song interaction branches |

The direct completion expression appears in 62 switch steps across 41 flow files (all flows scanned), plus
the three decoded logic modules named above (pedestal, Sheik and Mido). Other quest-step readers include the
listed dungeon/area modules. Initializing the entire quest to Complete could skip the actual sage/reward
sequence and advance unrelated interactions; keeping the real quest untouched avoids that data-side risk.
**Kareem: before Forest clear, test child return and the second adult pull without premature Prelude/reward;
after Forest, verify the sage/reward happens once and Sheik still teaches Prelude.** Runtime compatibility of
the reused module, pre-Forest child revisits and the second pull remain unverified until that test.

## 17. Round 5: shops and the Deku Shield (cs5b)

Full trace, provisional choices and player checks: `plans/rounds/r5-shops.md`. `data/shops.toml` identifies
all 128 shelf Hashes. Nine shops including mask loans, eight indices each; section 5's seven-slot count missed
index 0 (the default when `ShopItemIndex` is absent). Age, Alternative and Kokiri short-stock copies remain
separate Hashes, linked to the same logical shop slot.

The shelf's `Gyaml` selects the display. The linked seller's actor pack selects the sale through its inherited
`ShopRef` → `Component/ShopParam/*.bgyml` → `GoodsList[ShopItemIndex].Actor`. Price is the item's
`RSDB/PouchActorInfo.BuyingPrice` plus per-slot `PriceOffset` and conditional offsets. Stock and release gates
also live in `GoodsList`; most stock is unlimited. Market Hylian Shield is 80, discounted by 20 after
`Npc_Hylia_Soldier_003_GateOpen`. Both tunics cost 600 (1000 wallet required). Shelf Hashes have no permanent
save flag; seller stock actions record purchases and refresh boards.

`DisplayShop` uses the selected sale item (`Shop_SelectItemName`) through engine purchase/get/pay/stock
actions, rather than a literal gift grant. Actor identity supplies item UI text; merchant flavour messages are
separate fixed IDs. Forty-three placed native display actors exist, including eight masks. Most chest major
items have no native shop display; reviewer chose native-display-only destinations provisionally for round 5.

Kokiri's post-purchase shield tutorial checks acquired `Weapon_Shield_Deku` and
`KokiriForest_Meet_DekuTree_BoughtDekuShield`, then calls `Npc_Kokiri_010_Child:DekuShield_TutorialTalk` and sets
the latter flag. It is not an unconditional slot-6 tutorial. `present_DekuSheld` is a post-Mido replacement
route, guarded by quest state, equipped shield and its own talked flag; not a free pre-Mido check.

Verification: all 128 shelves match their Banc placement, linked NPC, resolved sale actor and base price
(`tests/test_shops_dump.py`, 1 passed). Live catalog smoke printed the same 128 and the three Kokiri shield
copies at 40. No game was run; changed-sale UI, stock persistence and tutorial behavior await Kareem.

Item 2 outputs in `E:/OOTRemake/work/r5-shops/`: native shield-slot Hylian Shield (40 rupees), Mido bottom-left
chest Deku Shield, and reviewer-requested unchanged shield display with Boomerang sale (40). Data-only
transforms update both shelves and seller packs, preserve slot prices/conditional discounts, and leave stock
and release fields intact. Native and mismatched-sale field-diff dump checks pass (2 tests). A mismatched
display's actual menu/get/stock behavior is unverified; no custom displays or game runs. Player checklist and
unrun, isolated-user launchers are beside the outputs. Stand-ins need text, price, category, stock persistence
and sold-out identity review before a seed setting is safe.

**Logic/integration (provisional, reviewer-approved).** `--shuffle Shop` shuffles the 64 ordinary logical shop
slots; the eight mask loans remain `MaskShop`. The pool contains the actual Deku Shield, progression-class.
Its helper now recognizes actual inventory as well as bought/drop forms, so sword + chest-found shield passes
Mido. Keeping Mido prevents a shield self-lock in the Deku Tree; skipping Mido can permit it without opening
the separate forest exit. Every bought-item helper was audited: Hylian Shield, nuts and sticks also gained
actual-inventory forms; tunics already had them. Bottle refills' capabilities require `has_bottle`; all native
Bombchu bundle counts are recognized. Thirty-five native sale variants plus eight equal-count chest-ammo
aliases may occupy shops. No custom or stand-in displays in seeds.

Wallet capacity is 200/500/1000 (`PouchActorInfo`, section 12), not N64's. Tunics cost 600 and need two upgrades.
Tunics are restricted to adult-accessible shops; Market stays child-only. Kokiri's five post-Mido releases,
Bombchu Shop's post-Dodongo gate, Bazaar's bomb-slot gate, and the potion shops' acquired-Blue-Fire gate remain
in sourced catalog rules. The latter is conservative and needs a played confirmation; no stock/release field
is discarded to make a seed pass. Test per rule: `tests/test_shop_logic.py`.

`make_seed` registers shops through Track C's extra patch steps; the common writer composes chest/shelf edits,
checks compression, updates the shared size table and builds before writing. `--shuffle Shop` alone and
`--shuffle Chest Shop` are supported. Live slice CLI runs: seed 7 Shop-only (8 checks, 4 spheres, 6 resources);
seed 22 combined (20 checks, 3 spheres, 10 resources). Seed 22 puts the Deku Shield in KF Shop Item 3 at 20,
reachable in sphere 1. Both are search/data evidence, not a game certification; whole-game chest expansion
and chronological age-model integration remain the other tracks' work.

Output safety: quantity-board removal also removes the board's `SimultaneousGroups` / `FarDeleteGroups`
memberships, not just its actor and seller links. A live generated-overlay smoke exposed the stale memberships;
the aimed fix and synthetic/all-shop dump regressions pass. Rebuilt smoke outputs contain no dangling board
references. No game boot or crash was needed to diagnose this.

**In game (Kareem, 2026-11-08, Hookshot release build in his folder, new games; logs show each changed file
`from the overlay`; saves read with `clawshot.save`):**

- `shield-slot-hylian`: the Kokiri shield shelf showed the Hylian Shield, and its name, description and every text
  were the Hylian Shield's; 40 rupees; it auto-equipped; the save has `IsGet.Weapon_Shield_Hylian`, no Deku Shield,
  `KokiriForest_Meet_DekuTree_BoughtDekuShield` false; no tutorial. **Mido let Link through with the Kokiri Sword
  and the Hylian Shield** (`KokiriForest_Npc_Kokiri_Mido_Child_Blocker` false): the remake's Mido takes any shield.
- `mido-chest-deku`: Mido's chest gave the Deku Shield; no tutorial (it follows buying, as traced); Mido let Link
  through.
- `shield-display-boomerang`: no change: the shelf, text, price, cutscene and tutorial were the Deku Shield's and
  the Deku Shield was given, though the log shows the changed seller pack loaded. What a slot sells follows the
  shelf's display actor; a stand-in display needs more than `GoodsList` (D21).
- **A bought slot restocks** (no "sold out"), the Hylian Shield in the changed slot too. Every native shop item is
  re-buyable equipment or a consumable, so a shuffled slot is a permanent purchase. To check later: with the Deku
  Shield shuffled out of every shop, whether the shopkeeper's `present_DekuSheld` route replaces a burned shield.

## 18. Round 5: whole-game chest seeds (cs5c)

Build `e0f3ccfa`, read-only dump. Per-Hash evidence, commands and unresolved checks: `plans/rounds/r5-seeds.md`;
scratch inventories and decoded probes are under `E:/OOTRemake/work/r5-seeds/`, never in the repository.

**Chest coverage.** All 184 census chests now have world identities: 164 shuffled, 20 explicit conservative
exclusions (`remake/extra_<area>.toml`, `keep_vanilla` reason and unreachable rule). The 119 previously unlinked
entries are accounted for; new remake-only checks use census names rather than invented OoTR identities.
Business Scrub Seeds and Magic Jars are normal filler. DreamWorld remains out. The Treasure Chest Game reward
stays vanilla pending D17's contents-swap test.

**Identity corrections.** DC lower-Lizalfos red-rupee reward is Hash `7764016096998075927`; the Bomb Flower
platform is `11582649900854566065` (Deku Shield). Ganon Water Trial Right is `14404733996390762670` in room 5;
Spirit Crystal Switch is `7899179288432849355` in room 17 (Business Scrub Seed). Earlier item-only matching had
paired them incorrectly. Forest Raised Island Courtyard and Well Front Center Bombable/Like Like chests are
absent from their remake rooms, not extra vanilla items.

**Dungeon ownership.** Ganon's boss key has type `GanonBossKey` and belongs to `Ganons Castle`; the Tower
region explicitly belongs there too. OoT Randomizer `526b4c8d` uses `Region.py:112-140`'s
`shuffle_ganon_bosskey` and `HintArea.at` (`Hints.py:475-507`) to inherit the castle identity through the tower
entrances (`Bosses.json:214-229`). Clawshot's own-dungeon setting likewise permits the key in its tower chest
and refuses overworld chests. Actual chest-key totals are Forest 5, Fire 8, Water 4, Spirit 5, Shadow 4,
Well 1, GTG 9, Castle 1; Shadow and Well each have an additional freestanding vanilla key.

**Owned-item substitutes.** Some `Obj_TBox_A_06` chests branch on `Drop__CheckActor`, giving
`Drop__DropActor_Substitute` when that item is already owned. A changed chest sets the substitute to the same
placed actor as its primary drop, preventing vanilla ammo/rupees from replacing shuffled progression.

**Still excluded pending play:** elevated KF/LW/ranch/windmill chests; repeat Dampé rupees; GC's sign-puzzle
rewards; unresolved GF/GV grotto access; adult Field/Lake appearance triggers; LH timed-candle chest;
ZF upper ruins; Well room 11 fake-floor chest. Exact identifiers, sources and questions are in the extra
files and round report. None is used by the oracle to supply an item.

### Chest events and the embedded song check

Reviewer-approved policy: remove **only** `Get_StoneOfForest_GetSword`. Its wrapper first grants the chest
content, then `Dm_Kokiri_0063:C01` creates/equips `Weapon_Sword_Kokiri` independently of the pouch.
`Get_StoneOfForest:GetSword` and that cut have no persistent flag or quest-step writes to restore.
Mido's inventory requirement follows the sword item wherever it is placed.

All other chest wrappers remain attached to the chest and grant its current `ContentName`. This keeps
their quest state with the actual opened check instead of reconstructing it elsewhere. Extra Navi lines or
cosmetic scenes may still refer to the vanilla item; those are not additional item grants.

| Event wrapper | Persistent state kept by retaining it |
|---|---|
| `SubEvent_GetIceArrow:SubEvent_GetIceArrow_OpenTBox` | `Event0` advances `SubEvent_GetIceArrow` to `Complete` after the default chest grant |
| `Defeat_Ganon:InsideGanonCastle_Dungeon_Get_Gauntlet_Gold` | `Event654` default chest grant, `Event655` cosmetic `Dm_InsideGanonCastle_0006`; its flow entries contain no extra grant/equipment creation or persistent flag/quest writes |
| `SageOfSpirit:SageOfSpirit_NaboorIsTakenAway` | `Event1` Nabooru timeline; `Event190`/`Event322` clear `HavePlayedEvent.NaviTips_Gauntlet_01`/`_03`; `Event21` advances `SageOfSpirit` to `Step07` |
| `SageOfWater:IceCavern_WaterSerenade` | `Event60` default chest grant; `Event281`/`Event283` plays the song event; `Event284`/`Event285` sets `SageOfWater_GetWaterSerenade`; `Event282`/`Event280` advances `Step04`/`Step05` |

**The Serenade is a song check inside the chest event**, not another chest reward:
`Dm_MelodyGet_Water:C15/Event29` calls `GetPouchContent:GetPouchContentByActorName` with
`ActorName = Item_Melody_WaterSerenade`. `Dm_MelodyGet_Water:EntryPoint0/Event14` also calls the shared
`Dm_SY_Ocarina:LearningOcarinaPlayAutoForSeek` (its Water case is `Event68`). The gift track owns both sides
when that song is shuffled; the chest patch changes neither. The world check remains `Sheik in Ice Cavern`.

### Fast start in seed outputs

Seeds use the same `fast_start.toml` settings as the standalone patcher: the intro is skippable by default;
`--skip intro saria mido deku_tree kaepora` selects skips explicitly, and `--skip` alone disables them all.
Selected initial-value edits go into the seed's `GameDataList`; the intro edits its event-setting component list.
All files are built/validated before any output is written. Fast-start GameDataList keeps its original layout
and size; removing the intro SkipSetting shrinks its tree. Their original allocations are retained without
inventing a generic `.bgyml` sizing formula.

**Mido is not the forest exit.** The skip changes only
`KokiriForest_Npc_Kokiri_Mido_Child_Blocker`. Decoded graph
`KokiriForest_Child_Level_All_02_d26e` separately reads/writes
`KokiriForest_Npc_Kokiri_007_Child_Blocker`/`_00` and checks `Get_StoneOfForest` step `Complete`.
Seed logic derives `skip_mido` from the same selected fast-start list, bypassing only the sword/shield event.
It leaves `open_forest`, `can_leave_forest` and the forest-exit guard alone. The search therefore reaches the
Deku Tree with Mido skipped and no equipment, but cannot leave the forest until Gohma is defeated.

**Mido accepts either shield (Kareem, in game 2026-11-08).** In
`E:/OOTRemake/work/r5-shops/shield-slot-hylian`, he had the Kokiri Sword and a bought Hylian Shield, no Deku
Shield; Mido let him through and `KokiriForest_Npc_Kokiri_Mido_Child_Blocker` was false in the save.
All three definitions of `Showed Mido Sword & Shield` now accept `Deku_Shield or Hylian_Shield`; the normal
definitions still require the Kokiri Sword unless Mido is skipped. Shop normalization recognizes physical
chest-found shields: both Deku and Hylian Shield now pass their respective helper and Mido regressions without
opening the independent forest exit.

## 19. Round 5: what reads a gift's item, and how each gift check is changed (cs5d)

How it was found (build `e0f3ccfa`; scratch in `E:/OOTRemake/work/r5-gifts/`, `readers.py` reproduces the reads and
gates): every flowchart the game loads, joined into one graph through `SubFlow` calls and `EventTransition`s (an
`EventSetting` row without `EntryPointName` runs `EntryPoint0`: 274 of the 284 such rows name a flow that has one); every
query that reads an item (`GameDataActor.EventQueryIsGameDataBool` on `IsGet.<item>`, `EventQueryCheckIsGet`,
`PouchSystemActor.EventQueryIsExistInPouch`, `EventQueryIsGameDataInt` on `PouchData.<item>.*`,
`EventQueryCanAddToPorch`); round 4's decoded logic modules (`Logic/*.ainb`, 1822, `IsGet.` strings); every placement's
parameters (`Presence.FlagName`); `GameDataList` `BoolExp` entries (operands hashed back to `IsGet.<item>`); and the
save reader on Kareem's save backups. For a gift check, a read is *near* when it sits on a path into the gift step
(callers included) and *far* otherwise; a far read is a *gate* when its branches lead to different effects (flags set,
events started, items given) and *lines* when they differ only in what is said. The *once gate* is the saved flag (or
quest step) that the path reads before the step and sets after it, checked by reading the flow.

**Facts the rewrite rests on.**

- `IsGet.<name>` is set by the game whenever the item enters the pouch, however it is got: no flow sets it except two
  (`Dm_MelodyGet_Fire` sets `IsGet.Item_Melody_FireBolero`, the fishing flows the sinking lure), and Kareem's saves have
  `IsGet.Weapon_Sword_Kokiri` set from the Kokiri Sword chest. The name is the pouch name: equipment pick-ups read under
  their equipment actor (`Item_Sword_Kokiri` -> `IsGet.Weapon_Sword_Kokiri`, `Obj_Shield_Deku` ->
  `IsGet.Weapon_Shield_Deku`, `Obj_Armor_Zora` -> `Armor_Adult_Zora`; `RSDB/PouchActorInfo` `AdultEquipment`/
  `ChildEquipment`). 193 of the 395 pouch actors have an `IsGet` Bool.
- A Bool query's case 0 is true, case 1 false (`IsExistInPouch` the same: case 0 = held).
- `HavePlayedEvent.<row>` is set when the event ends, also when the player declines and the flow quits:
  `Dm_FairyFountain_Power` asks its own `HavePlayedEvent` inside that event to tell a first visit from a later one, and
  offers again after a refusal, so it marks "visited", not "given" [inference from the flows: that the game sets it
  when a refused visit quits is not observed].
- The save's Bool section holds exactly the `GameDataList` Bools with `SaveFileIndex` 0 (10212 in every slot read).
  `MetaData` gives the save layout: `SaveDataOffsetPos[0]` (95704) is where `progress.sav`'s entry table ends, 0x20 + 8 ×
  (11925 entries of file 0 outside `Bool64bitKey`, + 1 `Bool64bitKey` pair, + 33 section headers), and
  `AllDataSaveOffset` (106216) is the same for every entry of a saved type in any file (13239: all but `Bool64bitKey`,
  `BoolExp` and `Struct`). `GameDataList`'s Bool list is not sorted by hash.
- **Logic fact for shuffling boss rewards (not this round): the story gates read the dungeons' quest steps, not the
  stones or medallions.** `DoorOfTime` asks `Get_StoneOfFire_IsCompleted_Exp`, `Get_StoneOfWater_IsCompleted_Exp` and
  `HavePlayedEvent.Dm_MelodyGet_Zelda`; no flow, logic module or placement reads `Item_Stone_*` or `Item_Medal_*`. With
  the rewards moved, the Door of Time (and the later gates that count medallions [inference: not each read]) would
  follow the bosses beaten, not the rewards held, unless those reads are rewritten or the logic asks for the bosses.

**Item gates elsewhere stay item reads**, because the logic models them as items: `TriForcePoint` Event8
(`IsGet.Item_DinFire` before any other Great Fairy), `Npc_Kaepora_DeathMountainTrail` (Din's Fire), the castle-grounds
soldier `Npc_Hylia_Soldier_009_Child` (`IsGet.Item_WeirdEgg` opens the gate, `Npc_Hylia_Soldier_009_Child_OpenTheGate`;
OoT Randomizer's `HC Garden` asks `Weird_Egg or Chicken`), the Gerudo stealth area (`GerudoFortress_Common_35d7`,
`IsGet.Item_Token_Gerudo`; not the guards, see the correction below), the windmill's Song of Storms spot
(`KakarikoVillage_Adult_Common_7d34`), Mido's blocker (`KokiriForest_Npc_Kokiri_Blocker_Surprised_BoolExp`: Kokiri
Sword and Deku Shield). Lines that change with an item (Kokiri children on Saria's Song, Zoras on the scales, Navi's
heat hint) are left as they are.

**Correction (round 13, `plans/rounds/r13-gerudo-card.md`).** This section first listed `GerudoFortress_Common_35d7`
as the guards' gate ("guards send Link to the cell without it"). Its card read only deletes two stealth-area sensors
once `IsGet.Item_Token_Gerudo` is set. Guard security, the desert gate guard, the Training Ground guard and horseback
archery read Spirit quest progress past Step01, which `SageOfSpirit:Meet_FourCarpenter_ClearEvent` advances to Step02
(Event146) after `Dm_Gerudo_0025` Event294 gives the card. A moved card writes no quest progress; Keanu's played
report (2026-11-12) saw the guards stay hostile. D39 therefore holds this check vanilla (`gift_rules.toml` class
`more`). The quest-step reads are a static data trace, not played acceptance of D39.

**Classes.** 79 gift checks are linked to OoT Randomizer names (93 steps). Each check's steps all get the new item
(where the game splits one check over two steps, a tier pick such as `IsExistInPouch(Item_BulletBag_Medium)` or two
code paths, both steps).

1. **Item swap only** (45): the once gate is a saved flag of the check, a quest step, the hand-in of the previous trade
   item, or the cutscene playing once (its trigger tests the cutscene's `HavePlayedEvent`, section 14 [inference per
   cutscene]); nothing reads the vanilla item as "already given".
2. **Swap plus rewrite** (19): the flow reads the vanilla item as "already given", or the step does more than give.
   - *Given flag* (six Great Fairies, Song from Windmill). An existing flag is used where one is set once the check is
     given and on no other path: the windmill's `HavePlayedEvent.Dm_MelodyGet_Storm` (the Song of Storms cutscene, an
     `EventSetting` row with no refusal in it; `Npc_Hylia_009_Child` reads it for lines only). For the fairies none is:
     `HavePlayedEvent.Dm_FairyFountain_<fairy>` ends every visit, refusal included (the flows' `VisitedNoAbility` branch
     exists for "visited, not given"); `Meet_GreatFairy_02` to `_05` are set at the start of `FirstTimeAnother_<fairy>`,
     before the offer (Frore Event51, Wisdom Event42, Nayru Event48, Courage Event47), and by Din's `GreatFairy_Disappear`;
     `Meet_GreatFairy_01` (Power) defaults to true; Din's fairy has no flag of its own; `GreatFairy_MeetFirst` (also set
     on a refusal), `GreatFairy_AlreadyAppeared`, the count `Meet_GreatFairy_RemainNumber` and the quest
     `Meet_GreatFairy` are shared by all six. So, as a last resort, the patch adds a saved Bool per fairy check to
     `GameDataList` (`Clawshot.Gift.<flow>.<event>` of the check's first step; `ResetTypeValue` 8, `SaveFileIndex` 0, as
     9338 story flags), grows the save layout in `MetaData` by one pair per flag (`SaveDataOffsetPos[0]`,
     `SaveDataSize[0]`, `AllDataSaveOffset`, `AllDataSaveSize`, +8 bytes each), sets the flag right after the gift step,
     and turns the listed "already given" reads into reads of it. Whether the game keeps a Bool it did not ship with, and
     still loads a save made before, is the in-game test (`plans/rounds/r5-gifts.md`, item 3).
   - *Skip* (the twelve songs, DMT Biggoron): each song flow first runs the shared play-along
     (`Dm_SY_Ocarina:LearningOcarinaPlayAuto` / `...ForSeek`), which adds the song of the current melody through one step
     per song (`Dm_SY_Ocarina` Event59 to Event71, chosen by `EventQueryMelodyTypeForNormal` Event45 or Event66) and is
     called only by the twelve song flows and Scarecrow's; the patch points that step's predecessors at its `next`, so the
     play-along teaches the notes and adds nothing, and the song flow's own `GetPouchContent` step gives the new item.
     Biggoron's step also takes the Giant's Knife (or the broken one) to make his sword; those two take steps are skipped.
3. **Needs more** (15): the nine boss rewards (story gates read the dungeon, not the reward), the three timed trades with a
   retry step, and the three sales inside `SimpleShop`.

| Check | Flow, step(s) | Vanilla | Once gate | Other readers of the item | Class | Change |
|---|---|---|---|---|---|---|
| DMT Trade Broken Sword | `Npc_Goron_Biggoron_Adult` Event232 | `Item_Prescription` | hand-in takes `Item_BrokenSword` | lines: 3 flows | 1 |  |
| DMT Trade Eyedrops | `Dm_DeathMtTrail_0050` Event21 | `Item_ClaimCheck` | hand-in takes `Item_EyeDrop` | none | 1 |  |
| Deku Theater Mask of Truth | `LostWood_ScrubForestStageElder_TrueMaskFirst` Event2, Event31 | `Item_NutBag_Large`, `Item_NutBag_Medium` | `LostWood_ScrubForestStage_TrueMaskEventLaunched` | tier pick `IsExistInPouch` in `LostWood_ScrubForestStageElder_TrueMaskFirst`; item gates kept: `Enemy_Scrub_Business_Common` | 1 | two steps (tier pick or two code paths): both get the item |
| Deku Theater Skull Mask | `LostWood_ScrubForestStageElder_SkullMaskFirst` Event29, Event32 | `Item_StickBag_Large`, `Item_StickBag_Medium` | `LostWood_ScrubForestStage_SkullMaskEventLaunched` | tier pick `IsExistInPouch` in `LostWood_ScrubForestStageElder_SkullMaskFirst`; item gates kept: `Enemy_Scrub_Business_Common` | 1 | two steps (tier pick or two code paths): both get the item |
| GC Darunias Joy | `Dm_Goron_0030` Event127 | `Item_Gauntlet_Goron` | the cutscene plays once | none | 1 |  |
| GC Rolling Goron as Adult | `SageOfFire` Event18 | `Obj_Armor_Goron` | `SageOfFire_Step02_DaruniaJr_FirstTalked` | lines: Navi's heat hint in `SageOfFire` (`IsExistInPouch(Armor_Adult_Goron)`), 2 other flows | 1 |  |
| GC Rolling Goron as Child | `Npc_Goron_006_Child` Event58, Event92 | `Item_BombBag_Large`, `Item_BombBag_Medium` | `GoronCity_GetBombBag_fromGoron006` | tier pick `IsExistInPouch` in `Npc_Goron_006_Child`; lines: 2 flows | 1 | two steps (tier pick or two code paths): both get the item |
| GF HBA 1000 Points | `Minigame_HorsebackArchery` Event322 | `Obj_Heart_Piece` | `MiniGame_HorsebackArchery_GotaHeart` | none | 1 |  |
| GF HBA 1500 Points | `Minigame_HorsebackArchery` Event319, Event320 | `Item_Quiver_Large`, `Item_Quiver_Medium` | `MiniGame_HorseBackArchery_Get_Quiver` | tier pick `IsExistInPouch` in `Minigame_HorsebackArchery`; lines: 1 flow | 1 | two steps (tier pick or two code paths): both get the item |
| GV Trade Poachers Saw | `Npc_Hylia_012_Adult` Event58 | `Item_BrokenSword` | hand-in takes `Item_PoacherSaw` | lines: 2 flows | 1 |  |
| HC Malon Egg | `Goto_HyruleCastle` Event35 | `Item_WeirdEgg` | quest `Goto_HyruleCastle` step | item gates kept: `Npc_Hylia_Soldier_009_Child` | 1 |  |
| HC Zeldas Letter | `Dm_HrlCastle_0050` Event59 | `Item_ZeldaLetter` | the cutscene plays once | none | 1 |  |
| HF Ocarina of Time Item | `Dm_MelodyGet_Time` Event70 | `Item_Ocarina_Time` | the cutscene plays once | none | 1 |  |
| Hideout Gerudo Membership Card | `Dm_Gerudo_0025` Event294 | `Item_Token_Gerudo` | the cutscene plays once | item read kept: logic module `GerudoFortress_Common_35d7` (`IsGet.Item_Token_Gerudo` deletes stealth-area sensors; the guards read Spirit quest progress, see the correction above) | 1 | none: held vanilla by D39 (round 13) |
| Kak 10 Gold Skulltula Reward | `GatheringTokenGold` Event398 | `Item_Wallet_Medium` | `KakarikoVillage_GatheringTokenGold_GetReward10` | lines: 1 flow | 1 |  |
| Kak 100 Gold Skulltula Reward | `GatheringTokenGold` Event215 | `Obj_Rupee_Gold` | `GatheringTokenGold` quest `Complete` | none | 1 |  |
| Kak 20 Gold Skulltula Reward | `GatheringTokenGold` Event75 | `Item_AgonyStone` | `..._GetReward20` | none | 1 |  |
| Kak 30 Gold Skulltula Reward | `GatheringTokenGold` Event194 | `Item_Wallet_Large` | `..._GetReward30` | lines: 1 flow | 1 |  |
| Kak 40 Gold Skulltula Reward | `GatheringTokenGold` Event200 | `Item_BombchuBundle_Large` | `..._GetReward40` | none | 1 |  |
| Kak 50 Gold Skulltula Reward | `GatheringTokenGold` Event219 | `Obj_Heart_Piece` | `..._GetReward50` | none | 1 |  |
| Kak Anju Trade Pocket Cucco | `Npc_Hylia_049_Adult` Event234 | `Item_CojiroCucco` | hand-in takes `Item_PocketCucco` | none | 1 |  |
| Kak Anju as Adult | `Npc_Hylia_049_Adult` Event264 | `Item_PocketEgg` | `GetSwordBigGoron_IsAfterFirstTalk_Npc_Hylia_049_Adult`, quest step | none | 1 |  |
| Kak Anju as Child | `Minigame_CatchCucco` Event181 | `Item_Bottle` | `MiniGame_CatchCucco_IsCompleted` | item gates kept: `Enemy_Scrub_Business_Common`, `Enemy_Scrub_Business_Seed` | 1 |  |
| Kak Granny Trade Odd Mushroom | `Npc_Hylia_053_Adult` Event167 | `Item_OddPowder` | hand-in takes `Item_OddMushroom` | lines: 1 flow | 1 |  |
| Kak Man on Roof | `Npc_Hylia_001_Adult` Event4 | `Obj_Heart_Piece` | `Npc_Hylia_001_IsGetHeartPiece` | none | 1 |  |
| Kak Shooting Gallery Reward | `MiniGame_HitTarget` Event242, Event381 | `Item_Quiver_Large`, `Item_Quiver_Medium` | `MiniGame_HitTarget_Kakariko_Get_Quiver` | tier pick `IsExistInPouch` in `MiniGame_HitTarget`; item gates kept: `Minigame_HorsebackArchery` | 1 | two steps (tier pick or two code paths): both get the item |
| LH Adult Fishing | `MiniGame_Fishing` Event579, Event822 | `Item_Scale_Gold` | `MiniGame_Fishing_GetGoldScale` | item gates kept: `Npc_Zora_002_Adult`; lines: 1 flow | 1 | two steps (tier pick or two code paths): both get the item |
| LH Child Fishing | `MiniGame_Fishing` Event573, Event821 | `Obj_Heart_Piece` | `MiniGame_Fishing_GetHeartPiece` | none | 1 | two steps (tier pick or two code paths): both get the item |
| LH Lab Dive | `Npc_Hylia_045_Child` Event113 | `Obj_Heart_Piece` | `Npc_Hylia_045_HasDived` | none | 1 |  |
| LLR Talons Chickens | `Minigame_FindOutCucco` Event23 | `Item_Bottle_Milk` | `IsClear_Minigame_FindOutCucco` | none | 1 |  |
| LW Gift from Saria | `Dm_Kokiri_0155` Event68 | `Item_Ocarina_Fairy` | the cutscene plays once | item gates kept: `Npc_Kokiri_007_Child`; lines: 1 flow | 1 |  |
| LW Ocarina Memory Game | `Npc_SkullKid_Child_02` Event24 | `Obj_Heart_Piece` | `Minigame_SkullKidSession_IsGetHeartPiece` | none | 1 |  |
| LW Skull Kid | `Npc_SkullKid_Child` Event71 | `Obj_Heart_Piece` | `Npc_SkullKid_Child_IsGetHeartPiece` | none | 1 |  |
| LW Target in Woods | `Dm_LostWood_0040` Event17, Event30 | `Item_BulletBag_Large`, `Item_BulletBag_Medium` | `LostWood_HitTargetOfDekuScrub_FirstClear` | tier pick `IsExistInPouch` in `Dm_LostWood_0040`, `IsGameDataBool` in `Dm_LostWood_0040`; lines: 1 flow | 1 | two steps (tier pick or two code paths): both get the item |
| LW Trade Odd Potion | `Npc_Kokiri_Fado_Adult` Event123 | `Item_PoacherSaw` | hand-in takes `Item_OddPowder` | lines: 1 flow | 1 |  |
| Market 10 Big Poes | `Npc_Hylia_048_BottleShop` Event329 | `Item_Bottle` | quest `SubEvent_GhostShop` `Complete` | item gates kept: `Enemy_Scrub_Business_Common`, `Enemy_Scrub_Business_Seed` | 1 |  |
| Market Bombchu Bowling Bombchus | `MiniGame_BombchuBowling` Event309 | `Item_BombchuBundle_Medium` | `MiniGame_BombchuBowling_Clear{First,Second,Third}Time` | none | 1 |  |
| Market Bombchu Bowling First Prize | `MiniGame_BombchuBowling` Event304, Event306 | `Item_BombBag_Large`, `Item_BombBag_Medium` | `MiniGame_BombchuBowling_Clear{First,Second,Third}Time` | tier pick `IsExistInPouch` in `MiniGame_BombchuBowling`; lines: 2 flows | 1 | two steps (tier pick or two code paths): both get the item |
| Market Bombchu Bowling Second Prize | `MiniGame_BombchuBowling` Event143 | `Obj_Heart_Piece` | `MiniGame_BombchuBowling_Clear{First,Second,Third}Time` | none | 1 |  |
| Market Lost Dog | `SubEvent_FindRichard` Event16 | `Obj_Heart_Piece` | quest `SubEvent_FindRichard` `Complete` | none | 1 |  |
| Market Shooting Gallery Reward | `MiniGame_HitTarget` Event241, Event378 | `Item_BulletBag_Large`, `Item_BulletBag_Medium` | `MiniGame_HitTarget_HrlCity_Get_BulletBag` | tier pick `IsExistInPouch` in `MiniGame_HitTarget`; item gates kept: `Dm_LostWood_0040` | 1 | two steps (tier pick or two code paths): both get the item |
| ToT Light Arrows Cutscene | `Dm_TimeTemple_0130` Event85 | `Item_Arrow_Light` | the cutscene plays once | lines: 1 flow | 1 |  |
| ZD Diving Minigame | `MiniGame_Diving` Event21 | `Item_Scale_Silver` | `MiniGame_Diving_Cleared` | item gates kept: `Npc_Zora_002`, `Npc_Zora_009`; lines: 1 flow | 1 |  |
| ZD King Zora Thawed | `SageOfWater` Event242 | `Obj_Armor_Zora` | `SageOfWater_KingZora_adult_Talk_Event198` | lines and music in `SageOfWater` (`IsExistInPouch(Armor_Adult_Zora)`); item gates kept: `Npc_Zora_KingZora_adult` | 1 |  |
| ZR Frogs Ocarina Game | `MiniGame_FrogTenors` Event384 | `Obj_Heart_Piece` | `MiniGame_FrogTenors_SongClear` | none | 1 |  |
| Colossus Great Fairy Reward | `Dm_FairyFountain_Nayru` Event163 | `Item_NayruLove` | none: `IsGet.<gift>` in `Dm_FairyFountain_Nayru` | lines: 2 flows | 2 | flag: own-flow read, `TriForcePoint` `Check_Complete` read, the two count reads in `Dm_FairyFountain_Din`; keep `TriForcePoint` Event8 (`IsGet.Item_DinFire`, the gate for the other five) |
| DMC Great Fairy Reward | `Dm_FairyFountain_Wisdom` Event144 | `Item_FairyBless_MPDouble` | none: `IsGet.<gift>` in `Dm_FairyFountain_Wisdom` | lines: 2 flows | 2 | flag: own-flow read, `TriForcePoint` `Check_Complete` read, the two count reads in `Dm_FairyFountain_Din`; keep `TriForcePoint` Event8 (`IsGet.Item_DinFire`, the gate for the other five) |
| DMT Biggoron | `Npc_Goron_Biggoron_Adult` Event123 | `Item_Sword_Biggoron` | quest `SubEvent_GetSwordBigGoron` `Complete` | item gates kept: `Npc_Goron_Medigoron_Adult` | 2 | skip the two steps that take the Giant's Knife (Event96, Event106) |
| DMT Great Fairy Reward | `Dm_FairyFountain_Din` Event212 | `Item_DinFire` | none: `IsGet.<gift>` in `Dm_FairyFountain_Din` | item gates kept: `Enemy_Scrub_Business_Common`, `Npc_Goron_008_Child`, `Npc_Kaepora_DeathMountainTrail`; lines: 4 flows | 2 | flag: own-flow read, `TriForcePoint` `Check_Complete` read; keep `TriForcePoint` Event8 (`IsGet.Item_DinFire`, the gate for the other five) |
| HC Great Fairy Reward | `Dm_FairyFountain_Power` Event141 | `Item_FairyBless_MP` | none: `IsGet.<gift>` in `Dm_FairyFountain_Power` | item gates kept: `Enemy_Scrub_Business_Common`, `Npc_Hylia_041_Child`; lines: 2 flows; placement: the fountain's `WallCrack` in `HyruleCastle_Static` is absent once `IsGet.Item_FairyBless_MP` (kept: cosmetic) | 2 | flag: own-flow read, `TriForcePoint` `Check_Complete` read, the two count reads in `Dm_FairyFountain_Din`; keep `TriForcePoint` Event8 (`IsGet.Item_DinFire`, the gate for the other five) |
| OGC Great Fairy Reward | `Dm_FairyFountain_Courage` Event144 | `Item_FairyBless_DefenseDouble` | none: `IsGet.<gift>` in `Dm_FairyFountain_Courage` | lines: 1 flow | 2 | flag: own-flow read, `TriForcePoint` `Check_Complete` read, the two count reads in `Dm_FairyFountain_Din`; keep `TriForcePoint` Event8 (`IsGet.Item_DinFire`, the gate for the other five) |
| Sheik at Colossus | `Dm_MelodyGet_Spilit` Event17 | `Item_Melody_SpiritRequiem` | the cutscene plays once | lines: 2 flows | 2 | skip the play-along add `Dm_SY_Ocarina/Event69` |
| Sheik at Temple | `Dm_MelodyGet_Shine` Event53 | `Item_Melody_LightPrelude` | the cutscene plays once | none | 2 | skip the play-along add `Dm_SY_Ocarina/Event71` |
| Sheik in Crater | `Dm_MelodyGet_Fire` Event192 | `Item_Melody_FireBolero` | the cutscene plays once | lines: 2 flows | 2 | skip the play-along add `Dm_SY_Ocarina/Event67` |
| Sheik in Forest | `Dm_MelodyGet_Forest` Event22 | `Item_Melody_ForestMinuet` | the cutscene plays once | lines: 2 flows | 2 | skip the play-along add `Dm_SY_Ocarina/Event65` |
| Sheik in Ice Cavern | `Dm_MelodyGet_Water` Event29 | `Item_Melody_WaterSerenade` | the Ice Cavern chest opens once | lines: 1 flow | 2 | skip the play-along add `Dm_SY_Ocarina/Event68`; started only by the Iron Boots chest's open event (below) |
| Sheik in Kakariko | `Dm_MelodyGet_Shadow` Event21 | `Item_Melody_ShadowNocturne` | the cutscene plays once | lines: 1 flow | 2 | skip the play-along add `Dm_SY_Ocarina/Event70` |
| Song from Impa | `Dm_MelodyGet_Zelda` Event111 | `Item_Melody_ZeldaLullaby` | the cutscene plays once | lines: 1 flow | 2 | skip the play-along add `Dm_SY_Ocarina/Event59` |
| Song from Malon | `Dm_MelodyGet_Epona` Event11 | `Item_Melody_EponaSong` | the cutscene plays once | none | 2 | skip the play-along add `Dm_SY_Ocarina/Event60` |
| Song from Ocarina of Time | `Dm_MelodyGet_Time` Event4 | `Item_Melody_TimeSong` | the cutscene plays once | none | 2 | skip the play-along add `Dm_SY_Ocarina/Event63` |
| Song from Royal Familys Tomb | `Dm_MelodyGet_Sun_03` Event34 | `Item_Melody_SunSong` | `RoyalFamilyTomb_MelodyGet_Clear` | none | 2 | skip the play-along add `Dm_SY_Ocarina/Event62` |
| Song from Saria | `Dm_MelodyGet_Saria` Event109 | `Item_Melody_SariaSong` | the cutscene plays once | item gates kept: `Npc_Kokiri_009_Child`, `Npc_Kokiri_Mido_Child`; lines: 4 flows | 2 | skip the play-along add `Dm_SY_Ocarina/Event61` |
| Song from Windmill | `Dm_MelodyGet_Storm` Event29 | `Item_Melody_StormSong` | none: `IsGet.Item_Melody_StormSong` in `Npc_Hylia_009_Adult` | lines: 3 flows; item gate kept: logic module `KakarikoVillage_Adult_Common_7d34` enables the windmill's Song of Storms spot on `IsGet.Item_Melody_StormSong` | 2 | skip the play-along add `Dm_SY_Ocarina/Event64`; `Npc_Hylia_009_Adult` Event9, 17, 31, 69 (learn or play branch, lines) read `HavePlayedEvent.Dm_MelodyGet_Storm` |
| ZF Great Fairy Reward | `Dm_FairyFountain_Frore` Event174 | `Item_FaroreWind` | none: `IsGet.<gift>` in `Dm_FairyFountain_Frore` | lines: 2 flows | 2 | flag: own-flow read, `TriForcePoint` `Check_Complete` read, the two count reads in `Dm_FairyFountain_Din`; keep `TriForcePoint` Event8 (`IsGet.Item_DinFire`, the gate for the other five) |
| Barinade | `Dm_ZoraFountain_0030` Event3 | `Item_Stone_Water` | the cutscene plays once | none | 3 | no flow reads the reward; the game's story gates read the dungeon's quest step instead (`DoorOfTime` asks `Get_StoneOfFire_IsCompleted_Exp`, ...), so a moved reward breaks them both ways |
| Bongo Bongo | `Dm_Awake_Shadow_Get` Event3 | `Item_Medal_Shadow` | the cutscene plays once | none | 3 | no flow reads the reward; the game's story gates read the dungeon's quest step instead (`DoorOfTime` asks `Get_StoneOfFire_IsCompleted_Exp`, ...), so a moved reward breaks them both ways |
| GC Medigoron | `Npc_Goron_Medigoron_Adult` Event11 | `Shop_Sword_Giant` | none: `IsExistInPouch(Weapon_Sword_Giant)` | item gates kept: `Npc_Goron_Biggoron_Adult` | 3 | a sale inside `SimpleShop` (the call returns without giving on cancel or too few rupees): a once flag must be set inside the shared purchase path; OoT Randomizer shuffles it only with `shuffle_expensive_merchants`/`shuffle_beans` |
| King Dodongo | `Dm_DeathMtTrail_0025` Event26 | `Item_Stone_Fire` | the cutscene plays once | none | 3 | no flow reads the reward; the game's story gates read the dungeon's quest step instead (`DoorOfTime` asks `Get_StoneOfFire_IsCompleted_Exp`, ...), so a moved reward breaks them both ways |
| LH Trade Eyeball Frog | `Npc_Hylia_045_Adult` Event26, Event27, Event45 | `Item_EyeDrop` | quest `SubEvent_GetSwordBigGoron`; retry steps re-give | lines: 4 flows | 3 | a retry step gives the vanilla item again whenever the player no longer holds it (timed trade item spoiled) |
| LW Trade Cojiro | `Npc_Hylia_017_Adult` Event100, Event116 | `Item_OddMushroom` | quest `SubEvent_GetSwordBigGoron`; retry step re-gives | item gates kept: `Npc_Hylia_053_Adult` | 3 | a retry step gives the vanilla item again whenever the player no longer holds it (timed trade item spoiled) |
| Morpha | `Dm_Awake_Water_Get` Event13 | `Item_Medal_Water` | the cutscene plays once | none | 3 | no flow reads the reward; the game's story gates read the dungeon's quest step instead (`DoorOfTime` asks `Get_StoneOfFire_IsCompleted_Exp`, ...), so a moved reward breaks them both ways |
| Phantom Ganon | `Dm_Awake_Forest_Get` Event13 | `Item_Medal_Forest` | the cutscene plays once | none | 3 | no flow reads the reward; the game's story gates read the dungeon's quest step instead (`DoorOfTime` asks `Get_StoneOfFire_IsCompleted_Exp`, ...), so a moved reward breaks them both ways |
| Queen Gohma | `Dm_Kokiri_0130` Event22 | `Item_Stone_Forest` | the cutscene plays once | none | 3 | no flow reads the reward; the game's story gates read the dungeon's quest step instead (`DoorOfTime` asks `Get_StoneOfFire_IsCompleted_Exp`, ...), so a moved reward breaks them both ways |
| ToT Reward from Rauru | `Dm_SageRoom_0005` Event48 | `Item_Medal_Light` | the cutscene plays once | none | 3 | no flow reads the reward; the game's story gates read the dungeon's quest step instead (`DoorOfTime` asks `Get_StoneOfFire_IsCompleted_Exp`, ...), so a moved reward breaks them both ways |
| Twinrova | `Dm_Awake_Spirit_Get` Event14 | `Item_Medal_Spirit` | the cutscene plays once | none | 3 | no flow reads the reward; the game's story gates read the dungeon's quest step instead (`DoorOfTime` asks `Get_StoneOfFire_IsCompleted_Exp`, ...), so a moved reward breaks them both ways |
| Volvagia | `Dm_Awake_Fire_Get` Event13 | `Item_Medal_Fire` | the cutscene plays once | none | 3 | no flow reads the reward; the game's story gates read the dungeon's quest step instead (`DoorOfTime` asks `Get_StoneOfFire_IsCompleted_Exp`, ...), so a moved reward breaks them both ways |
| Wasteland Bombchu Salesman | `Npc_Hylia_044_Adult` Event3 | `Shop_BombchuBundle_01` | `Npc_Hylia_044_Buy` (not saved) | none | 3 | a sale inside `SimpleShop` (the call returns without giving on cancel or too few rupees): a once flag must be set inside the shared purchase path; OoT Randomizer shuffles it only with `shuffle_expensive_merchants`/`shuffle_beans` |
| ZD Trade Prescription | `Npc_Zora_KingZora_adult` Event87, Event131 | `Item_EyeballFrog` | quest `SubEvent_GetSwordBigGoron`; retry step re-gives | item gates kept: `Npc_Hylia_045_Adult`; lines: 2 flows | 3 | a retry step gives the vanilla item again whenever the player no longer holds it (timed trade item spoiled) |
| ZR Magic Bean Salesman | `SimpleShop` Event182 | `Item_MagicBean` | none: a repeatable sale | none | 3 | a sale inside `SimpleShop` (the call returns without giving on cancel or too few rupees): a once flag must be set inside the shared purchase path; OoT Randomizer shuffles it only with `shuffle_expensive_merchants`/`shuffle_beans` |

Cutscene checks whose trigger reads quest progress (Sheik's songs after a medallion, the Light Arrows after the Shadow
and Spirit medallions) stay right only while the boss rewards are vanilla, which class 3 keeps them.

**Gifts inside a chest's open event.** Of the four story overrides on chests (`GetEventName`, section 3) that the seed
keeps, one plays a gift: the Ice Cavern Iron Boots chest (`IceCavern_Static`, Hash 6859289214373847284,
`SageOfWater_MelodyGet_Water`) runs `SageOfWater:IceCavern_WaterSerenade`, whose two `EventTransition`s (Event281,
Event283) are the only starts of `Dm_MelodyGet_Water`: the Serenade check (`Sheik in Ice Cavern`, step Event29) is that
chest's second item, given once because the chest opens once. With the override removed the Serenade is never given.
The other three (`SubEvent_GetIceArrow_OpenTBox`, `InsideGanonCastle_Get_Gauntlet_Gold`,
`SageOfSpirit_NaboorIsTakenAway`) reach no gift step (followed through their cutscenes `Dm_InsideGanonCastle_0006` and
`Dm_DesertColossus_0030`). The chest's own item stays track C's.

**Gift steps that are not checks** (55, no OoT Randomizer link): repeat and lesser prizes (rupees), the 13 play-along
steps, the hatching cuccos, the Master Sword grants, the Amiibo pouch, Scarecrow's Song, the Zora shop's tunic sale and
the mask shop's Mask of Truth (shops, track B), the Kokiri shopkeeper's free Deku Shield (`present_DekuSheld`, given
once, `HaveTalked_Npc_Kokiri_001_Shop_Child_PresentDekuShield`, when Link holds no shield: `CheckIsGet
(Weapon_Shield_Deku)`; track B's), the Market bottle (`Npc_Hylia_020_Shop_Child`), Dampé's digging heart piece and the
frogs' bug game. None is changed.

**In game (Kareem, 2026-11-08).** The five test folders of `plans/rounds/r5-gifts.md` item 3, each log showing
`fs: OpenFile(...): from the overlay` for its changed files; the first four on a copy of the save backup
`2026-11-07_llr-tower-before-pickup`, the fifth on a new game.

- `talon-boomerang` (class 1): Talon's cucco game gave the Boomerang, with its model and get cutscene, and it equips.
  Talking to him again only refills milk into an empty bottle. The save has `IsGet.Item_Boomerang` true and no milk
  bottle.
- `skullkid-bombbag` (class 1): the Skull Kid gave the Bomb Bag; nothing on a repeat.
- `din-fairy-hookshot` (class 2, the new flag): the save made before the patch loaded; Din's fairy gave the Hookshot, no
  magic gauge and no Din's Fire; a second visit, and another after quit and continue, only healed. The save has
  `Clawshot.Gift.Dm_FairyFountain_Din.Event212` true. **A Bool added to `GameDataList` with the save layout grown in
  `MetaData` is kept by the game, and an older save still loads.**
- `malon-song-heartpiece` (class 2, the skipped play-along add): Malon gave the Piece of Heart and its text; Epona's
  Song is not in the song list.
- `chest-song-storms` (track C's chest, a song actor as `Drop__DropActor`): the chest showed a green rupee model with
  the Song of Storms' pickup text, and the save has `IsGet.Item_Melody_StormSong` true. With no ocarina held, whether
  the song plays is not known yet (a follow-up test on the ranch save, which has the Fairy Ocarina).
- `chest-ocarina-storms` (Claude's follow-up, new game, `E:/OOTRemake/work/r5-gifts/make_chest_ocarina_storms.py`;
  the ranch save's Kakariko grotto chest was already opened): Mido's house, Hash `4555665598794293658` held
  `Item_Melody_StormSong` and Hash `9725242744547055868` held `Item_Ocarina_Fairy`. **The Fairy Ocarina from a chest
  works, and the Song of Storms from a chest plays as a learned song** (save: `IsGet.Item_Ocarina_Fairy`,
  `IsGet.Item_Melody_StormSong`). The song still shows a green rupee in the chest. **Naming:** walking in, the far-left
  chest is `4555665598794293658` (census and OoT Randomizer name "KF Midos Top Right Chest") and the far-right one
  `9725242744547055868` ("KF Midos Top Left Chest"): the remake's row of four is mirrored against the N64 names, so a
  spoiler's left and right for these chests are the player's right and left (the two middle chests are unchecked).

## 20. Round 6: readable location names (cs6a)

Player-facing names are presentation, not new census/world identities or new reachability rules.
`data/location_names.toml` links the world key to its physical Hashes or gift flow steps, a short label,
one-line directions and evidence. The scope includes held/excluded checks so their labels stay stable when
settings change; their existing exclusions are not lifted. Detailed verification and questions:
`plans/rounds/r6-names.md`. Research stays under `E:/OOTRemake/work/r6-names/`.

**Mido's house:** use left-to-right from the entrance looking at the chests, not N64's top/bottom labels.
All four are now settled in game (Kareem, 2026-11-08; Claude's reviewer update). `seed-shop-7` identifies
far left (`Top Right`, Mirror Shield) and second from left (`Bottom Right`, Kokiri Sword); the earlier
`chest-ocarina-storms` test identifies far right (`Top Left`), leaving third as `Bottom Left` by elimination.
Both right-hand checks held Blue Rupees in the seed. The placement order independently agrees:

| Doorway view | Hash | Existing OoTR identity |
|---|---|---|
| Far left | `4555665598794293658` | `KF Midos Top Right Chest` |
| Middle left | `12786193094758345086` | `KF Midos Bottom Right Chest` |
| Middle right | `10831981390482426294` | `KF Midos Bottom Left Chest` |
| Far right | `9725242744547055868` | `KF Midos Top Left Chest` |

The middle-right chest's vanilla item is a Green Rupee; the other three are Blue Rupees. All four have
the same region and unconditional local rule, so the naming orientation does not change access logic.
No location definition, item grant or rule is renamed.

Catalog coverage: 184 chests, 72 shop slots (including eight unshuffled mask loans), all 79 linked gift
checks (six Great Fairies included), plus cs6d's four opt-in once-sale Scrub families. **339 descriptions
cover 414 physical Hash/flow identities.** `tests/test_names.py` checks completeness/copy IDs and unique
labels; the catalog reader smoke confirms the same counts. Shop rows use the customer's view facing the
shopkeeper, top/bottom row and far/inner left/right spots; this is placement-derived, not a new shop playtest.
Static locators omit vanilla rewards/prices because shuffled placements/settings change them.

Positional audit (`r6-names.md`, item 2): the ambiguous GC blue pair, GTG lobby and First/Second pairs,
Spirit invisible pair, Fire timed scarecrow trio and Ganon Light blue/Lens pairs have equivalent modeled
access within each candidate group, verified by compiled-rule execution. GTG's native mechanisms differ
but intentionally share conservative unions. Do not generalize that label neutrality to GC's Hammer/Silver
pockets or to the Well east-dip water condition; those affect prerequisites. Actual actor-derived vanilla
items remain distinct. No link/rule is changed by presentation work.

The spoiler keeps internal placement/sphere keys and adds readable `locations` plus a logic-derived
`opening_route`; the writer emits `play-note.md` from the same snapshot. The opening is a replayed,
deletion-minimal child-only source witness, with actual predecessor items/counts per step, purchases,
physical shelves, prices and shelf-release conditions. It is not all optional sphere loot and not a
rupee-earnings proof.

Kareem's seed-shop-7 note bug (reviewer, 2026-11-08): Hylian Shield passes Mido but does not reflect the
child Slingshot-room scrub's nuts. The first fix exposed the missing paid Shield prerequisite. Section 12's
later GIFT02 finding supplies a free alternative: pass Mido, talk to the Great Deku Tree, return to the child
Kokiri shopkeeper before Gohma/castle quest completion, with **no Deku Shield equipped** (an owned one can
be unequipped). The note now prefers that free visit and shows an accessible paid shelf as an alternative,
not another required purchase. The event is materialized only in a private presentation proof so it cannot
silently supply inventory: the actual seed's world, pool and shuffled identities are unchanged. The real
seed-7 spoiler/note regression verifies the visit and its Sword/Hylian predecessors before Tree entry;
F's Boomerang route supplies the regenerated seed's ranged tool.

Presentation prices use `clawshot.settings.shop_price` with the **placed** native display, physical slot
price, shuffled membership and effective seed settings. A moved Kokiri Deku Shield is discounted; the old
shield slot holding another item is not. Affordable affects shuffled Shop sales only, not Scrub fees.
The Scrub producer exports its existing `SALES` prices through internal world metadata: required Scrub
rewards render as Buy/price rather than free collection. No gameplay gate or pricing policy is duplicated.

## 21. Round 6: settings, prices and forest modes (cs6b)

Build `e0f3ccfa`, read-only dump. Implementation, command evidence and the complete inventory-write audit:
`plans/rounds/r6-settings.md`. Generated resources and audit inventories stay under
`E:/OOTRemake/work/r6-settings/`; no game/launcher was run.

**Replay.** `Settings.to_string()` / `from_string()`, CLI `--settings` and `--print-settings` use canonical `CS1`:
sorted JSON overrides against `data/settings.toml`, zlib and URL-safe base64; defaults alone are `CS1`.
Shuffled kinds, dungeon items, logic (including travel/return guarantee), fast start, songs, prices and forest
mode participate. Spoilers store both settings and their string. Explicit CLI options win; unchanged seed/string,
generator and world data reproduce byte-identical resources, including effective gift-policy replay.

**Songs and gift actors.** `songs=song` remains default; `anywhere` is opt-in and releases all twelve songs from
song checks, subject to native Shop displays and other existing destination restrictions. Only Storms was played
from a chest: the other eleven are **inferred** from the shared `Item_Melody_*` pouch/IsGet grant path (Claude's
Round 6 review), not individually verified. Non-song gift-only items still require individual chest evidence;
the sourced `settings.toml [chest_verified]` entries are Fairy Ocarina and Song of Storms (section 19).

**Independent inventory writes: correction to section 19's Sheik-in-Crater row.** All 79 linked gift roots and
their called entries were audited, including bound wrapper arguments and GameData/pouch destinations.
The twelve play-along adds already have skip rules; ordinary census grants and legitimate egg/trade consumption
are retained. One additional independent ownership write required a redirect:

| Check | Flow / event | Original destination | Redirect |
|---|---|---|---|
| Sheik in Crater (Bolero) | `Dm_MelodyGet_Fire/Event1`, terminal after `C21/Event131` | `IsGet.Item_Melody_FireBolero` | `HavePlayedEvent.Dm_MelodyGet_Fire` |

`Value=true`, Index and terminal edge stay unchanged: never clear a Bolero learned elsewhere. The completion
Bool already exists (Hash 10850286, reset 8, save file 0); this redirect adds no save flag/layout change.
A failing-before/passing-after dump regression requires every changed gift's call graph to contain no direct
write of its vanilla IsGet. Full audit classifications, including legitimate removals, are in the round report.

**Prices.** `shop_prices=vanilla` by default; `affordable` makes every shuffled shop offer exactly 10 through
`GoodsList.PriceOffset = target - item base price`. Exact pricing clears conditional discounts; the original
Market Hylian Shield's -20 soldier discount would otherwise make an affordable offer negative.
`cheap_deku_shield=true` is provisional: the actual Deku Shield anywhere in Kokiri shop costs 10, even with
shops unshuffled; another item in the old shield slot is not discounted by that rule. Stock, releases and
tutorials are unchanged. Wallet predicates rebuild from the same price policy, retaining 200/500/1000 capacities,
adult stock, Dodongo-clear and acquired-refill gates. Kokiri's original offers all cost 5–40, within the start wallet.

**Forest (D24, Kareem).** Default **`closed`**, close to vanilla: Mido guards the Deku Tree and Gohma gates the bridge.
Advanced opt-ins: `closed_deku` opens only the bridge exit; `open` also bypasses Mido. Defaults stay vanilla-like;
difficulty is opt-in. `--forest` maps to `logic.open_forest` and derives the legacy `skip_mido` flag.
Old `--skip mido` / fast-start spelling remains accepted as an alias for `forest=open`; conflicts are refused.

The bridge control is `KokiriForest_Npc_Kokiri_007_Child_Blocker_00` (Hash 3856422516): default true, reset 8,
save file 0. `Npc_Blocker_Kokiri_007.GameDataToEnableAI` reads it; module
`KokiriForest_Child_Level_All_02_d26e` nodes 5/0/6 disable the sensor area when false, preventing the transient
blocker from being reasserted. `Npc_Kokiri_007_Child/Event42` only clears it. The transient
`KokiriForest_Npc_Kokiri_007_Child_Blocker` already defaults false (Hash 4043170676), so it is left alone.
The new `fast_start.toml forest_exit` primitive changes only the control flag; `open` also selects the existing
Mido primitive. No quest completion, actor or logic module is changed. Initial values compose before gift-added
saved Bools through the common writer; neither side overwrites the other's GameDataList changes.

**Player checks, not yet in-game certified:** under `E:/OOTRemake/work/r6-settings/`, each has a copied release-only,
isolated new-game launcher and its checklist. `chest-ocarina-minuet`: Fairy Ocarina plus Minuet in Mido's house
(far-right / far-left); **Kareem: does Minuet play and warp child Link to Sacred Forest Meadow?**
`shop-prices-10`: controlled native Kokiri stock; **verify displayed price, exactly 10 paid, shield acquired and
normal restock/tutorial/release gates.** `forest-closed-deku`: one initial Bool changed, GameDataList unchanged
length 1462888, allocation 1463176; **before sword/shield or Gohma, verify Mido blocks while the bridge exit works,
also after return/save/Continue.** Each result needs its `from the overlay` log.
Hookshot v2.0.1 safety: these launchers use only `E:\Games\Hookshot\bin\hookshot.exe`, set
`HOOKSHOT_NO_UPDATE_CHECK=1`, and stop if it is missing. Never fall back to the folder's `hookshot.exe`:
it is now the updater/launcher and ignores `--user`, risking the main save with the overlay.

Live full CLI smoke with Chest+Shop+Gift, songs anywhere, affordable, closed_deku and default return guarantee:
277 checks, 20 spheres, 118 resources; independent read-back preserved the exit default and all four new fairy
save flags/layout growth. This is generation/data proof, not an in-game completion claim.

**In game (Kareem via Claude, 2026-11-08, Hookshot 2.0.1):** the Minuet of Forest from a chest is learned and warps to Sacred Forest Meadow (green rupee
model, correct text); the Fairy Ocarina from a chest shows no model but the correct text. `closed_deku`: the
bridge Kokiri is gone, Saria's Fairy Ocarina cutscene plays on the bridge before Gohma (the world's `LW Gift from
Saria` = True behind the bridge exit agrees), Mido still blocks. Prices: the Deku Shield and Deku Nuts sell for 10,
and stay 10 after a restock. Songs anywhere and the forest modes are game-confirmed.

## 22. Round 6: message text, Gossip Stones, item-get text (cs6c)

How each was found and the scratch scripts (`E:/OOTRemake/work/r6-hints/`, read only on the dump; their decoded text
stays there): `plans/rounds/r6-hints.md`. Build `e0f3ccfa`. No game text is quoted here.

**Message files** (`clawshot.formats.msbt`). `Mals/<language>.Product.110.sarc.zs` (16 languages: `USen`, `EUen`,
`JPja`, ...) is a SARC of 540 MSBT files each: `EventFlowMsg/<flow>.msbt` (an NPC's or cutscene's lines),
`LayoutMsg/...` (menus), `LocationMsg/Location.msbt` (place names), `StaticMsg/...`, `ChallengeMsg/...`. Every file
is MSBT v3, little-endian, UTF-8, with only `LBL1` (labels) and `TXT2` (text): no attributes, no styles. A flow shows
a line by `MessageId: "EventFlowMsg/<file>:<label>"` on a talk step (`EventTalk` of `Npc_*`, `Npc_Navi`,
`Npc_EventStarter`), so changing what an NPC says is changing that label's text in the archive; the flow does not
change. Control tags inside text: group 0 the library's own (ruby, font, size, colour, page break), group 2 a value
filled in at run time from a game-data name (`PouchData.Item_Token_Gold.StockNum`, `Shop_SelectItemName`,
`UI_MessageTargetActorName`, `Npc_TimeSignal.Hour`, ...), group 201 grammar (articles, gender) in the European
languages, groups 1, 3, 4, 5 timing, voice and animation cues. All 8640 files read and write back byte-identical, and
each archive writes back byte-identical through `clawshot.formats.sarc` (its default alignment, 8); the size-table
overhead for `Mals/*.sarc` is +312 (section 11).

**Gossip Stones** (`clawshot.census.hints`). 40 talking stones with 40 names, each an `Obj_GossipStone_A_01` placed in
the child and the adult file as two actors with **different `Hash` values** (unlike chests) and the same `Name`
(`GOSSIP_<AREA>_<NN>`); the census lists 41 because the Kokiri Forest files also place the Lost Woods bridge stone
(`GOSSIP_LOST_WOOD_02`) in their copy of the bridge ledge: stone, stick-bag scrub and purple-rupee chest all stand at
one offset (82, -20, 88) from the Lost Woods copies (cs6a found the same for the chest and scrub, thread `cs-r6`). No
`Dynamic` parameters; `Presence.FlagName` `GossipStoneDisappear.<Name>`
(negated; Zora's Domain adult: `IsAppear_GossipStone_ZoraDomain_Adult`); three `Reference` links each (an
`Obj_FairySpirit` with `IsGossipStoneAppearance`, anchors `FairySpirit_AppearPoint` and `PlayerPos`: the fairy that
playing a song summons). An unnamed `Obj_GossipStone_A_02` in Zora's Domain's adult `Dynamic` files (`Presence`
`SageOfWater_IsAfter_Step08_Exp`, no links) does not talk.

- **Text:** flow `GossipStone`, entry `Talk`: with the mask worn, the stone's line is
  `Npc_EventStarter.EventTalkWithInstanceNameLabel {MstxtName: GossipStone}` (Event18): the message of
  `EventFlowMsg/GossipStone.msbt` whose label is the stone's `Name`. Before it, a stone line `Talk_03` + `Talk_10`
  the first time (`HaveTalked_MaskTruth_GossipStone` unset) or `Talk_12` after; after it, one of two closing lines at
  random (`GOSSIP_RumorCommon_01`/`_02`), and the first time a Navi balloon (232) and the flag set. Every stone label
  exists in all 16 languages. The names do not follow the areas (`GOSSIP_HYRULE_CASTLE_03` stands in a Death
  Mountain Trail grotto); each name is one stone.
- **The Mask of Truth is needed**, as on N64: every path from `Talk` to Event18 passes `PouchSystemActor`
  `EventQueryIsExistInPouch {Actor: Armor_Child_Mask_Truth}` case 0 (Event112) and `Player_Event`
  `EventQueryPlayerIsEquipArmor {ArmorName: Armor_Child_Mask_Truth}` case 0 (Event25). Without the mask Navi talks
  instead (`Talk_00`, `_05`, `_09`, `_13`, `_15`, `_19`, `_22`, `_30`), and hitting a stone tells the time
  (`ReceiveSwordDamageByPlayer`, `Reaction_*`). Making stones talk without the mask is a flow edit (Event112's and
  Event25's case 1 pointed at case 0's next), which round 6's test output makes ("In game" below).
- **Against OoT Randomizer** (`LocationList.py` at `526b4c8d`, 40 `HintStone`s): 36 stones match one each
  (`STONE_LINKS`, evidence per stone: nearby actors, grotto rooms and covers, round 4's grotto findings, Zelda Central's
  remake guide https://zeldacentral.com/games/ocarina-of-time-remake/gossip-stones/); within the Deku Tree pair, the
  SFM maze pair, the three Lake Hylia stones and the four Temple of Time stones, which name goes to which stone is not
  settled (each group is one OoT Randomizer region, so no logic depends on it), nor whether the east Hyrule Field
  grotto is N64's Southeast or Near Market grotto. Four OoT Randomizer stones have none here: the KF Storms, LW Near
  Shortcuts and DMT Storms grottos hold no stone (round 4), and Hyrule Field has one generic grotto fewer. Four stones
  are remake-only: the Sacred Forest Meadow clearing behind the Song of Time block, a Kakariko grotto with a beehive,
  the Zora's River storms grotto, and the Death Mountain Trail cow grotto.

**Other hint givers** (`HINT_GIVERS`; each label checked to be shown by its flow and present in every language):

| Giver | Flow | Lines | As a hint |
|---|---|---|---|
| Skulltula House | `GatheringTokenGold` (shows `Npc_SkullDad.msbt`) | `Talk_28`, `_23`, `_24`, `_25`, `_26`, `_27`: one per token count (10 ... 100); they name no reward | OoT Randomizer's "N Skulltulas Reward Hint": the line can name the reward |
| Dampé's diary (adult) | `Diary_Hylia_Dampe_Adult` | `Talk_03`: the page about his grave | "Dampe Diary Hint" (where the Hookshot is) |
| Sheik (adult, before the Forest Temple) | `Npc_Hylia_Sheik_Adult` | `Talk_01`, `Talk_03`: send Link to the Sheikah's tool in Kakariko | the Hookshot's place |
| Kaepora Gaebora | `Npc_Kaepora_DeathMountainTrail` (`Npc_Kaepora.msbt`), `Npc_Kaepora_LakeHylia` | directions and flight offers | none in OoT Randomizer |
| Navi | `NaviHint` (`NaviHint_Dungeon_*`), `Navi_EnemyHint_*`, 27 `NaviAreaHintEventActor` placements | area and enemy tips | none in OoT Randomizer; a possible free hint slot |

The Temple of Time altar's text is part of a cutscene (`Dm_TimeTemple_0020`), not a talk step; not traced further.
Many NPCs also have `Mask_NN` lines for when Link wears a mask (the Mask of Truth reads minds), a further slot.

**Item-get text and model** (`clawshot.patch.text`; flows `GetPouchContent`, `Dm_SY_Get`; actor packs):

- **One path for chests, NPCs and shops.** A chest's default event passes its content to
  `GetPouchContent:GetPouchContentByActorNameForTreasureBox`, NPC gifts reach `GetPouchContentByActorName` through
  their wrappers (section 4), and both run entry `GetPouchContent`: `PouchSystemActor.EventTriggerSetForGetWindow
  {Actor}`, `OpenGetWindow`, then `EventTriggerAddOrRemovePouchContent {IsSetMessageTargetActorName: True}`. A shop
  sets `Shop_SelectItemName` to the shelf item and its menu lines name it with a run-time tag (group 2 type 3 on that
  variable); Kareem saw the name, description and every text follow the shelf item (section 17).
- **The text is the item's.** `OpenGetWindow` branches on `EventQueryCheckUIMessageTargetActorName`: own windows
  for heart pieces, Gold Skulltula tokens, bottles, minigame small keys, magic, the Spiritual Stones of Fire and
  Water, the Claim Check, Iron and Hover Boots, the Longshot and Biggoron's Sword; every other item gets
  `DefaultGetMessage`, the lines `Dm_SY_Get:GetMessage` and `GetCaption`, whose only content is a run-time tag (group
  2, types 23 and 19) on `UI_MessageTargetActorName`. Each item's texts are in `ActorMsg/PouchContent.msbt` as
  `<key>_Name`, `_Caption`, `_GetMessage`, `_GetCaption` (some `_SecondGetCaption`, `_ShopCaption`), where `<key>` is
  the actor's `ActorName` component (`ActorNameRef` in its pack: `TBox_Rupee_Red` -> `Obj_Rupee_Red`,
  `Item_Sword_Kokiri` -> `Weapon_Sword_Kokiri`, `Item_HeavyBoot` -> `Armor_Adult_HeavyBoot`). 359 of the 393
  pouch actors with a pack have get texts under that key (the rest are base actors, default equipment and the small
  bags no check gives); all 106 actors of `item_actors.toml` have a name and get text in all 16 languages. That the
  two tags resolve to `<key>_GetMessage`/`_GetCaption` is an inference from the templates, and every in-game result
  agrees (the Boomerang, rupees and the Song of Storms from chests each showed their own text).
- **The model is the actor's `ModelInfo`** (`FmdbName`). All 12 `Item_Melody_*` actors use `Obj_Rupee`, the
  rupee model (green, its default colour [inference]), so a song from a chest shows a green rupee with the song's
  text, as Kareem saw; songs are shown by their own cutscenes otherwise. Other stand-in models: Farore's Wind and
  Nayru's Love show Din's Fire's model, the Pocket Egg the Weird Egg's, the Longshot the Hookshot's, the blue and
  green potions the red potion's; bombs, nuts, sticks and keys their pickup models.
- **Naming an item in an NPC's line**: (a) per language, replace the line's message with text that includes that
  language's `<key>_Name` (its parts, grammar tags included): `patch.text.item_name` and `edit_messages`; a seed then
  writes the language archives it supports (about 2.4 MB each, changed archives only). (b) At run time, as the
  business scrubs do: the flow sets a String64 game-data variable to the actor
  (`GameDataActor.EventTriggerSetGameDataString64`, e.g. `Scrub_Business_TempItemName_00`) and the line holds a group
  2 type 3 tag on it; this needs a flow edit and a line with the tag, but no item names per language. (a) is
  implemented; (b) suits an item only known at run time. Either way the NPC's other lines (about its vanilla item)
  stay unless they are rewritten too.
- **A Gossip Stone without the mask:** `patch.text.gossip_without_mask` points both answers of Event112 and Event25
  at the stone's path; the flow keeps its size (93,400 bytes). The stone's first-time opener (`Talk_03`, `Talk_10`)
  mentions the mask; `Talk_12` is the repeat opener.

**In game:** not yet. The test `E:/OOTRemake/work/r6-hints/ingame/gossip-kf-line` (a new game: every stone speaks
without the mask, the Kokiri Forest stone by the Lost Woods entrance says a custom line naming the Boomerang through
`item_name`) and what Kareem should see are in `plans/rounds/r6-hints.md`, item 4.

**In game (Kareem via Claude, 2026-11-08, Hookshot 2.0.1):** the `gossip-kf-line` stone said the custom line without the Mask of Truth.

## 23. Round 6: one-time scrubs and Gold Skulltula drop experiments (cs6d)

Build `e0f3ccfa`, dump/save backups read-only. Full 21-actor ledger, flow/event/Hash evidence,
commands, provisional choices and player instructions: `plans/rounds/r6-tokens.md`.
Research and seven controlled overlays: `E:/OOTRemake/work/r6-tokens/`; no game/launcher run.

**Scrubs:** 21 actor Hashes are 12 repeat/rotating vendors and nine physical actors implementing four
saved one-time reward families. Their placement Bool64bitKey reset type 280 is not permanent pickup type
24; the once-only proof comes from separate saved Bools. Both HF ages share
`HyruleField_Enemy_Scrub_Business_HeartPiece_01` (100 rupees); DMC has
`DeathMountain_Enemy_Scrub_Business_HeartPiece_01` (100); four KF/LW stick sellers share
`LostWood_Enemy_Scrub_Business_DekuStickPouch_01` (40); two LW nut sellers share
`Lostwood_Enemy_Scrub_Business_DekuNutsPouch_01` (40, capitalization intentional).
All four Bools default false, reset type 8, save file 0.

Banc offer fields are selectors into `Enemy_Scrub_Business_Common`'s fixed item-name dispatcher, not
arbitrary grants. Unknown item names fall through to a Magic Jar sale. Keep those selectors and rewrite
the common flow's one-time purchase calls instead: HF Event645 plus selection Event653; DMC Event293
plus Event144; stick Event317/322/555; nut Event318/326. Every grant/tier/copy of one family gets one item.
The generic purchase path checks acceptance and rupees before its get wrapper; only successful return
sets `ScrubBusiness_BuySuccess` and then the saved family flag. Cancellation, shortfall, native prices,
HF's adult-note/child-password puzzle and all other vendor paths remain intact.

`--shuffle Scrub` (off by default) admits exactly `HF Deku Scrub Grotto`, `DMC Deku Scrub`,
`LW Deku Scrub Near Bridge`, `LW Deku Scrub Grotto Front`. Repeat vendors stay vanilla (reviewer,
2026-11-08). Shared KF/LW copies are one check, never separate pool rewards. Fixed Medium capacity
actors represent existing normal-class `Deku Stick Capacity` (20 sticks) / `Deku Nut Capacity` (30 nuts)
under D16; capacity items remain at Scrub destinations until chest-grant evidence exists. Both native
tier branches normalize even for an unmoved capacity placement. Native wallet 200 covers every fee.

**Tokens:** 100 permanent enemy Hashes, 114 placement copies. Enemy drop table creates one
`Obj_Token_Gold`; its pouch identity is `Item_Token_Gold`, max 100. Enemy utility graph nodes 0–2
construct a drop override carrying its no-respawn Hash in `GoldTokenGmdHash`. The token's own AI
calls `OneShotGoldTokenDeadAfter` only on pickup death reason 10. [INFERENCE] This callback marks
collection against the enemy's Hash; ordinary pickups lack it. A per-enemy `Drop__DropActor` override
is expressible, but neither preserving the enemy Hash nor a matching file diff proves replacement
persistence. No token location enters the fill yet; `--shuffle Token` explicitly refuses before generation
or output, naming the missing callback/persistence evidence. No fake flag/no-op shuffle is shipped.

`patch/tokens.py` provides explicit experiments with actual pickup actors, not inventory-only `Item_*`.
Ranch tree Hash `341792603838029977` is unset in all six ranch-backup slots; control/token, red-rupee
and Hylian-Shield overlays change only its drop on both age copies, through the common writer and size
table. **Kareem: check native control, uncollected-drop recovery, replacement pickup/count, saved enemy
Hash, and no respawn after leaving/reloading.** Exact checklist and release-only isolated-save launchers:
`E:/OOTRemake/work/r6-tokens/ingame/checklist.md`. All remain unrun by the agent.

**House rewards already are Gift checks:** `GatheringTokenGold` Event398 (10/wallet), Event75
(20/Echo Gem), Event194 (30/large wallet), Event200 (40/Bombchu bundle), Event219 (50/heart),
Event215 (100/gold rupee). Existing gift rules preserve per-threshold saved gates (100: quest complete).
Unlinked Event471 is a repeat gold rupee, not a new once check. The 40-token gift remains vanilla because
its bundle actor/count lacks an exact fixed pool mapping (round 5), not because Token owns House gifts.

Verification: exact inverse-flow diffs cover all four scrub families/nine actors and preserve native gates,
prices and every other event; token field-diff oracle covers 100 enemies/114 copies. Real whole-world
Chest+Scrub seed 7: 168 checks, 28 spheres, finished gated-return search won, 59 resources; every scrub
branch matches its placed actor. Second CLI/hash-seed process: all 60 canonical files byte-identical.
Data/search proof only; neither scrub nor token gameplay is claimed certified. Full gate results are in
the round report.

## 24. Round 6: Castle Town shop crash and refill/container audit (cs6e)

Build `e0f3ccfa`; read-only dump. Full field audit, scratch paths, experiments and commands:
`plans/rounds/r6-shopfix.md`. All twelve seller packs in the original `seed-shop-7` change only one embedded
ShopParam each, only `GoodsList.Actor` and `PriceOffset`. ShopRef/member names and every other pack member
remain intact. All sale actors have native packs. Removed quantity-board Hashes have no remaining actor links,
AI/group memberships or empty groups; the round-5 group cleanup is not the observed missing reference.

The writer previously raised only outer pack allocations, not the modified members' own resource entries.
Market Potion's embedded `Npc_Hylia_020_Shop` component grows **1088 -> 1156** bytes, rounded **1088 -> 1184**,
but its entry stayed **7984**. The supplied GeneralFormatAsync crash names `Component/ShopPa` in x6/x7 and has
`[x19+0x080] = 000004a000000484`: **0x484 = 1156**, **0x4a0 = 1184**, identifying this component's sizes.
**Confirmed in game (Kareem via Claude, 2026-11-08):** 07's identical Market packs/Banc with only the embedded
allocations raised loads Castle Town without a crash, with randomized Bazaar/Potion shelves, prices and descriptions;
the log shows the overlay. The exact internal null-allocation operation remains inferred, not reverse-engineered.

All nine distinct original seller ShopParam resources were measured: rounded raw size + **6896** parsed overhead,
with **80** more for Market Bazaar's one conditional-price element. `patch.shops.member_growth` preserves the
original overhead for sale/price edits and discount removal; changes that grow parsed structure are refused.
The common writer sizes final composed pack bytes, uses the maximum (not the sum) across copies sharing a member
path, never lowers entries, and emits the table even for nested-only growth. No generic `.bgyml` formula is added.

`E:/OOTRemake/work/r5-seed/seed-shop-7b/` is a **size-fix-only continuation**: its `spoiler.json` is byte-for-byte
equal to 7's, all 228 placements and 26 search spheres unchanged. Every overlay resource except the size table
is byte-identical; exactly three embedded entries rise: Bazaar **8352 -> 8416**, Potion **7984 -> 8080**, Zora
**7856 -> 7952**. The original seed and user were not modified. Its unrun `Play shop seed 7b.bat` uses the game
binary under `bin`, suppresses update checks and creates a separate user copy when Kareem runs it after quitting.
New-seed refill restrictions below do not alter this continuation.

Verification: real Potion writer regression fails before (**7984 != 8080**) and passes after. Nine focused
synthetic checks pass; the actual 7b generator/writer/search smoke parses all 77 resources and proves the exact
spoiler/resource equality above. Controlled short checks are under `E:/OOTRemake/work/r6-shopfix/`; try
`Test - 07-market-allocations-fixed.bat` from the copied child ranch checkpoint first. No game/launcher was run by the agent.

### New-seed refill placement boundary

When Shop is shuffled, `prepare` derives `Settings.item_location_types` holding every `Buy ...` item to Shop,
through the existing `allowed()` path. Physical shields/tunics and native chest ammo remain distinct items.
The fill reserves the exact number of remaining shop-only refills across progression/filler stages, leaving spare
Shop slots available to flexible native items and protecting chest capacity for non-display items.
Normal/progression/spare-capacity synthetic cases pass across 20 seeds each with one attempt.

An actual new Chest+Shop CLI seed 7 has **228 checks, 25 spheres, 80 resources; 59 Buy refills, zero outside Shop**.
It differs at **127 placements** from the old seed. This policy is for **new seeds only**; 7b stays the byte-identical
spoiler/placement continuation above. No increased retry limit or weakened beatability oracle.

### Ammo packs and their containers (reviewer item 4b)

Read-only source: `RSDB/PouchActorInfo.Product.111.rstbl.byml.zs`, following `BundleActor` to the counted item,
then its `SmallBagActor`; the bag's `AfterExpansionMaxNum`, `ExpansionMaxNumActor`, `IsItemStockMaxIfGet` and
`ActorFullOnlyIfIsGetWhenGetBag`. Reproducer/report: `E:/OOTRemake/work/r6-shopfix/audit_ammo.py` and
`ammo-container-audit.json`. Identifiers/counts below are findings, not copied resource trees.

| Ammo actor(s) | Bundle count | SmallBagActor target / capacity | Missing-container finding |
|---|---|---|---|
| `Shop_BombBundle_01` / `_02` / `_03` / `_04` | 5 / 10 / 20 / 30 | `Item_BombBag_Small`, 20 | `_02` **observed** from a chest: Bomb Bag +20 bombs; other variants share `Item_Bomb` chain |
| `Item_BombBundle_Small` | 5 | same Bomb Bag, 20 | Same `Item_Bomb` chain; get-event bag grant **inferred**, not separately played |
| `Shop_BombchuBundle_01` / `_02` / `_03` / `_04` / `_05` / `_06` / `_07` / `_08` | 10 / 20 / 1 / 3 / 5 / 8 / 15 / 30 | same Bomb Bag, 20 | `Item_Bombchu` shares the bag; grant inferred; Bombchus were bought in 07 |
| `Item_BombchuBundle_Small` | 5 | same Bomb Bag, 20 | Same `Item_Bombchu` chain; get-event bag grant inferred |
| `Shop_ArrowBundle_01` / `_02` / `_03` | 10 / 30 / 50 | `Item_Quiver_Small`, 30 | `Item_Arrow_Normal` chain; bag grant inferred; **no Bow grant in these rows** |
| `TBox_ArrowBundle_Small` / `_Medium` / `_Large` | 3 / 5 / 10 | same small quiver, 30 | Same arrow chain; bag grant inferred, not a Bow |
| `Shop_DekuSeedBundle_01` / `_02` | 30 / 10 | `Item_BulletBag_Small`, 30 | `Item_DekuSeed` chain; bag grant inferred; **no Slingshot grant in these rows** |
| `Shop_DekuNutBundle_01` / `_02` | 5 / 10 | `Item_NutBag_Small`, 20 | Base `Item_DekuNut` explicitly has `IsAbleToGetBagIfGet = true` |
| `TBox_DekuNutBundle` | 3 | same small nut bag, 20 | Same declared nut link; automatic chest bag inference superseded below |
| `Shop_DekuStick`; `Shop_DekuStickBundle_Medium` | 1; 5 | `Item_StickBag_Small`, 10 | Single Shop stick and base `Item_DekuStick` declare permission to get the bag, not proof that every path does |
| `Item_DekuStickBundle_Small` | 3 | same small stick bag, 10 | Same declared stick link; automatic chest bag inference superseded below |

The Bomb Bag expands **both** bombs and Bombchus; `IsItemStockMaxIfGet = true`, while
`ActorFullOnlyIfIsGetWhenGetBag` singles out Bombchus. Exact first-Bombchu fill ordering is not established by
metadata alone. Small quiver/bullet bag also set stock-max on bag acquisition; nut/stick bags do not.
`SmallBagActor` is a real container link, not by itself proof of every ordinary dropped-pickup path:
the bomb/arrow/seed rows omit `IsAbleToGetBagIfGet`, whereas a chest uses the `GetPouchContent` get-event grant.
Only the reported Shop Bombs(10) chest case is gameplay-certified here.

**Correction, 2026-11-12 (mysterypaint player report via Claude):** sticks/nuts from chests can leave
Link without their bag despite `IsAbleToGetBagIfGet`. The row links above remain correct; inferring an
automatic first bag on every grant path was not. Slingshot from the Kokiri shopkeeper also produced 0/0.
Castle's first-bag fix plus Clawshot's missing direct-hand-over/source coverage explicitly grant a missing
small container before the original positive item add, preserving larger bags and the original quantity.
Arrow/seed refills do not grant their weapon or a new bag through this fix. See `rounds/r13-item-grants.md`
for native path identifiers, ordered key composition and the pending in-game check.

Kareem's Basement Chest finding: old seed 7 placed **Buy Bombs (10)** / `Shop_BombBundle_02`; with no Bomb Bag,
the chest gave a Bomb Bag and 20 bombs, and the save has `IsGet.Item_BombBag_Small` (Kareem via Claude).
**D25 chosen by Kareem (2026-11-08): require the bag, do not count ammo as extra bags.** The fill pre-places
`Bombs (N)` / `Bombchus (N)` only at destinations a maximal search cannot reach without any logical Bomb Bag
source or bomb/Bombchu pack. The search holds all other pool/fixed items with their counts, excludes bag aliases
and Buy pack variants, and filters excluded starting items. Thus a Hammer/other-item bypass is not mistaken for
a mandatory bag gate; packs cannot mutually stand in for the independent bag. Existing assumed fill then checks
actual reachability and dungeon/display restrictions before normal filler can consume those constrained slots.
Buy refills remain Shop-only; sale rules, ammo actor mappings and aliases are unchanged.

Regression evidence: an otherwise-open synthetic seed placed Bombs in its early Hammer chest before the fix.
Eight synthetic cases now cover all six ammo counts/classes, aliases, pack alternatives and impossible destinations;
real seed 7 passes with Chest-only and Chest+Shop shuffle. After rebasing onto `a81faf9`, two actual CLI processes
(different hash seeds; the second replays the settings string) produced **78 byte-identical files**. All **six**
native ammo pickups (three each of bombs/Bombchus) were outside bag-free reach; **59 Buy refills** stayed in Shop,
and the written placement passed beatability. Reports and full gate results: `plans/rounds/r6-shopfix.md`.
The advanced extra-bag counting option remains unimplemented. This new-seed restriction does not rebuild or
change the size-only 7b continuation. Quiver/bullet bag capacity still does not mean Bow/Slingshot ownership.

### Purchase conditions and native refusals (reviewer follow-up)

`DisplayShop:SelectItem_CheckAvailable` starts at **Event318** (index 284). Its explicit category gates are
**Event299** (BulletBag IsGet), **Event320** (Quiver IsGet), **Event327** (Fire stone quest complete) and
**Event325** (any empty bottle). **Event310/Event240** ask the native seller `EventQueryCheckBuyResult`;
**Event303/Event77** ask `EventQueryCanAddToPorchByGameData(Shop_SelectItemName)`. These native queries own
capacity/payment checks; their engine implementation was not read. No refusal or capacity query is patched.

Refusal IDs below are labels, not copied game text. The generic preamble is `NotAvailableTalk`:
merchant `Shop_01_02_1`, `_2`, `_3` (Potion's observed hesitant price line is `_3`), with adult variants.
`ChangeMstxtForActor` selects a matching merchant override. Unqualified specific labels below name the flow's
shared `EventFlowMsg/Npc_Kokiri_001_Shop_Child` message file; named Bazaar/Goron/Zora/Potion rows identify
their own message files. More specific follow-up messages:

| Item(s) | Purchase condition / explicit evidence | Refusal label(s), paraphrased |
|---|---|---|
| `Shop_Heart` | Life below maximum; recover 4 quarter-hearts, native hold check | `Shop_05`: health already full |
| `Shop_MagicJar_Small` | Magic gauge exists and MP has room; MPRecover60 metadata, native hold check | Generic preamble/recovery refusal; no new magic is granted by buying |
| `Shop_DekuNutBundle_01/02`, `Shop_DekuStick`, `Shop_DekuStickBundle_Medium` | Stock below capacity; nut/stick rows permit creating the small bag | Generic preamble, then `Shop_03`: carrying capacity full |
| `Shop_DekuSeedBundle_01/02` | `IsGet.Item_BulletBag_Small` (Event299), plus stock room | Generic preamble; `Shop_03` for full stock |
| `Shop_ArrowBundle_01/02/03` | `IsGet.Item_Quiver_Small` (Event320), plus arrow stock room; actual flow tests quiver, not literal Bow | Bazaar/Zora `Shop_09_04/05`: missing bow/container explanation; `Shop_41`: full arrows |
| `Shop_BombBundle_01/02/03/04` | `Get_StoneOfFire_IsCompleted_Exp` (Event327), then native stock/hold/payment result; no separate literal Bomb Bag query in this branch | Bazaar/Goron `Shop_10/12`: stock unavailable before Dodongo; generic/`Shop_03` for native hold refusal |
| `Shop_BombchuBundle_01..08` | Native stock/hold/payment result; no explicit Bomb Bag or Dodongo gate in this item branch | Generic preamble/`Shop_03`; **07 purchase succeeded**, including the reported initial no-Bomb-Bag state |
| `Shop_Weapon_Shield_Deku` | Must not already carry the shield; stock max is one | Kokiri `Shop_31/32`: already owned; adult-specific preamble is `Shop_01_Shield_Adult_02_*` |
| `Shop_Weapon_Shield_Hylian` | Must not already carry it; stock max is one | Bazaar `Shop_31/32`: already owned |
| `Shop_Armor_Goron`, `Shop_Armor_Zora` | Adult-use restriction; must not already carry the tunic; native price/wallet | Goron/Zora `Shop_19/20`: child; `Shop_31/32`: already owned |
| `Shop_Bottle_RedPotion`, `_GreenPotion`, `_HalfMilk`, `_Poe`, `_Bug`, `_Fish`, `_Fairy` | **An empty usable bottle**, Event325; they refill a bottle, never grant one | Generic preamble; missing empty bottle cannot be distinguished from all other native rejection reasons by that preamble alone |
| `Shop_Bottle_BlueFire` | Same empty-bottle condition; at Potion merchants also existing `IsGet.Item_Bottle_BlueFire` through `Outofstock_SelectBottle_BlueFire` Event108 | Potion `Shop_101/102`: Blue Fire unavailable; otherwise generic preamble |

All rows also retain their slot's original release/stock fields and require the quoted rupee price;
`EventQueryCheckBuyResult`/the later buy/pay actions own this, not a new randomizer bypass.

**In game (Kareem via Claude, 2026-11-08, 07):** Bazaar Bombchus were bought; Deku Stick and heart purchases
worked once stock/health had room. His initial full 10 sticks, owned Deku Shield, unknown bottle contents,
no Bomb Bag/Bow and full hearts explain native refusals. Reviewer cancelled the proposed extra buyable test;
none was created or run.

**Logic check:** actual shields satisfy the existing helpers; an already-held shield/tunic is already the
capability, so refusal to buy a second one does not block progression. Tunics stay at adult-accessible destinations,
`can_use` classifies tunics as adult items, and wallet rules use canonical effective prices. Bottle-refill helpers require
`has_bottle`; one Ruto's Letter does not qualify, whereas a drinkable milk bottle can be emptied and reused.
Current stock/full health are consumable state, not monotone progression gates; use/empty/take damage restores room.
Default `free_bombchu_drops=true` conservatively needs an actual Bombchu item for `has_bombchus`;
buy access supplies `can_refill_bombchus`. With free drops off, Bomb Bag plus buy access supplies usable Bombchus.
No new Bomb-Bag requirement is invented for the observed successful purchase.

**Blue Fire purchase gate fixed (reviewer authorization, 2026-11-08):** Potion merchants test the **selected**
Blue Fire item for prior acquisition (`DisplayShop` Event108), while only their original slot 5 release rules
already model that condition. `shops.toml [item_locations]` now allows `Buy Blue Fire` only at those two Potion
slot 5 checks or the 48 supported non-Potion shop checks. The existing `allowed()` destination check enforces
this together with the effective Shop-only `item_location_types`; no new flow bypass or release-rule rewrite.
Other bottle refills are unchanged; both vanilla/affordable price modes retain the native acquired-Blue-Fire gate.

Before the fix, both price modes allowed Market Potion slot 1, and synthetic seed 3 placed its required first
Blue Fire there. All 30 shop-logic tests now pass, including that 20-seed bootstrap regression. Actual seed 7 CLI
and settings/hash replay on **0afcca5** produce **79 identical files**, including readable `play-note.md`;
Blue Fire sells at **Kak Bazaar Item 5** and **GC Shop Item 6**.
Written shelves/seller components were parsed and original release fields preserved; D25's six native ammo
placements and beatability still pass. **All 78 files of 7b are hash-identical before/after**; no continuation reroll.
The names-track randomized-slot golden was removed with reviewer approval: its meaningful ordering checks
now live in the fixed-placement free-shield fixture. A dump-level real seed 7 CLI check independently
replays the written opening as child to Gohma and checks the note's Enter/Complete order, with no slot pins.
Full gate results and final commit: `plans/rounds/r6-shopfix.md`.

## 25. Round 7: hints on Gossip Stones (cs7a)

Build `e0f3ccfa`, read-only dump. Commands, provisional choices and the in-game test: `plans/rounds/r7-hints.md`.
Scratch scripts: `E:/OOTRemake/work/r7-hints/`. No game text is quoted here.

**Stones in the world.** OoT Randomizer's 40 `HintStone` locations (region and rule) are translated with the rest of
its world and built into `World.hint_stones`, apart from the checks. The remake lacks four of them (`n64_only`) and has
four of its own, given regions and rules by hand (`data/world/remake/hint_stones.toml`): the Sacred Forest Meadow
clearing behind the Song of Time blocks (the clearing chest's rule), Kakariko's bomb grotto, the Zora's River storms
grotto and the Death Mountain Trail cow grotto. `census.hints.stone_labels()` ties the 40 live stones to the 40 message
labels (section 22's `STONE_LINKS` plus the four remake-only names).

**Choosing.** `generate.hints.choose` (OoT Randomizer's method, `Hints.py` at `526b4c8d`): always-hint locations
first, then kinds drawn by weight (Way of the Hero, barren areas, item, sometimes and random location hints, junk);
areas are a region's `hint` or `dungeon`, or that of the region it is entered from. A hint naming a location goes only
on a stone readable with every other placed item collected, so a stone never needs what it points at. With
`hints = mask` a stone counts as readable only for child Link holding the Mask of Truth (section 22: the flow asks for
it held and worn; only child wears masks), and no hint names a location whose item the mask cannot be reached
without (D26, Kareem: a hint must stay useful from when the mask is held). Which items a location hint may name follows
OoT Randomizer: random hints skip items of type `Drop`, `Event` and `Shop` (`get_random_location_hint`,
`Hints.py:1088-1097`; the remake's own `Buy ...` refills, typed `Item` in the world, count as `Shop`) and nothing else,
sometimes hints have no item filter (`get_specific_hint`, 1127-1172), item hints name only major items
(`get_good_item_hint`, 882-891). So a random or sometimes hint may name a Red Rupee, as there. Lists, weights, area
names and wording: `data/hints.toml`. Defaults (D26): `always`, English text in every language archive.

**Writing.** Each hint replaces its stone's message (`EventFlowMsg/GossipStone.msbt`, label = the stone's `Name`)
with Clawshot's English line: the stone's opening tags kept (size, colour, voice), rows of at most 60 characters
(the game's own stone rows reach 65), two rows a page, a page break (group 0 type 4) reopening the size and colour, and
the filled-in names in colour `0000` (group 0 type 3, the colour other lines use to stress a word), each closed with
colour `ffff`. That is how the game ends a highlight: of `USen`'s colour tags following a `0000`, 3046 are `ffff`, 2 are
`0000` again, none is a line's own colour. 7c's first build closed names with the stone's own `0100`, and in game the
rest of the line stayed highlighted. Item names are the game's English (`USen` `ActorMsg/PouchContent.msbt` `<key>_Name`, grammar tags
dropped). Every language archive gets the English lines (provisional). Seed 7 (chests): each Western and Japanese
archive shrinks (`USen` 2,373,416 -> 2,373,192 bytes, `JPja` -2,416, `EUru` -2,496), while `CNzh` (+1,024), `KRko`
(+512) and `TWzh` (+992) grow past their size-table entries, which the writer raises (the size table is then written).
The `GossipStone` flow edit (section 22) is written with `hints = always`; with `mask` the flow stays vanilla.

**In game** (seed-shop-7c, Kareem, reviewer saw the screenshots): with `always` the four Temple of Time stones speak
without the mask, wrapping is fine, and facing the temple, left to right, they are `GOSSIP_HYRULE_MARKET_01` to `_04`.
Bug: after the first name the rest of the line stayed highlighted (closing colour `0100`). Fixed to `ffff` and built as
`seed-shop-7c-next` (only text files differ from 7b); the fixed colour is not yet seen in game.

## 26. Round 7: chest get-models and gift actor evidence (cs7b)

Build `e0f3ccfa`, read-only dump. Full exact-action trace, all 76 unobserved exact gift-actor
identities, commands, provisional choices and player checklist: `plans/rounds/r7-getitem.md`.
External reproducers/resources: `E:/OOTRemake/work/r7-getitem/`. No agent game/launcher run.

Chest display uses the content actor's `Components.ModelInfoRef` -> `FmdbName` and
`ModelProjectName`, mirrored in `RSDB/ActorInfo`. The twelve ordinary songs resolve to
`Obj_Rupee`, explaining the Storms/Minuet green-rupee observations. The two ocarinas already
have their correct model assets, but `Components.EventPerformerRef` selects `Common.event.root`,
not `PouchContent.event.root`. Common lacks the chest's `EventTriggerModelBindForItemGetDemo`;
PouchContent root 151 -> bind 146 computes the child/adult get-demo offset and binds to Player.
Small chest Event10 and big chest Event66 call that missing action. **[INFERENCE]** This
presentation-dispatch mismatch explains the Fairy Ocarina's invisible model; runtime proof is pending.

No standalone musical-note/song model found in the native actor/model inventory. Provisional
stand-ins: Fairy Ocarina for ordinary songs, Ocarina of Time for warp songs. `patch/getitem.py`
provides explicit `changes(romfs, actors)` transforms: song ModelInfo identity, ocarina native
PouchContent performer copied from Boomerang, matching ActorInfo model/bounds and conservative
non-shrinking native display heap reservations. Every pouch identity, OcarinaParam, text, grant
and saved flag stays unchanged. No new assets, edited AI graphs or automatic seed default.

Common writer accounts for same-shape embedded string growth without lowering original overhead.
ActorInfo's existing own-file allocation is raw 1,934,492 -> rounded 1,934,496 + 3,064 = 1,937,560;
changed table retains its size. The explicit full-family dump oracle checks inverse diffs on all
14 packs/all 8,363 ActorInfo rows, native assets and every output allocation. Public writer smoke
built 16 resources successfully. Gameplay/binding/ocarina use still needs Kareem, not a parse-only claim.

One new-game launcher: `E:/OOTRemake/work/r7-getitem/ingame/Test - chest-gift-models.bat`, its own
empty user and nine-resource overlay. Mido doorway view: middle-left Fairy Ocarina; far-left
Storms; middle-right Din's Fire; far-right Adult Wallet. Training-area chest: Ocarina of Time,
unsafe sword wrapper removed. Storms-grotto chest: Echo Gem, conditional native puzzle check.
Six original saved Hashes; no chest moved/new flag. Upper bridge-ledge chest stays untouched.
Checklist covers model/text AND usable item/capacity, Save/Continue and overlay-open logs;
no Kokiri Sword is supplied, so this is not a playable seed. Executable only the bin game,
update checks disabled, missing-exe stop; no launcher/dry-run executed by the agent.

The shared chest allowlist grows only by Minuet's **already observed round-6 warp**. Ten other
songs remain family-inferred in opt-in anywhere mode; no new gift experiment actor is released.
**Kareem: confirm the three native presentation paths and four new gift grants, including
Time replacing Fairy without losing Storms; report the grotto's actual appearance prerequisite.**

**In game (Kareem via Claude, 2026-11-08, Hookshot 2.0.1, `chest-gift-models`):** the Song of Storms shows the ocarina stand-in; Din's Fire gives the
magic meter and the spell works; the Adult's Wallet holds 500. The Fairy Ocarina still shows no model, so the bind
change did not reach it (round 8). The Ocarina of Time chest was not reported.

## 27. Round 7: boss-heart pickups and native token callback experiment (cs7c)

Build `e0f3ccfa`, read-only dump/save backups. Reproducible probes, outputs and unrun isolated launchers:
`E:/OOTRemake/work/r7-drops/`; full contracts/commands/questions: `plans/rounds/r7-drops.md`.
Sections 25/26 belong ahead of this section when their tracks are integrated; no placeholders are added.

### Boss Heart Containers

The eight census `heart_container` checks already correspond to world type `BossHeart`. Each has one
`ActorLogicSimpleActor` binding in its AiGroup and one membership in each of `SimultaneousGroups` and
`FarDeleteGroups`. They are placed scripted pickups, not the boss's drop-table item. Creation gates:

| Boss | Heart Hash | Logic_Create source |
|---|---|---|
| Gohma | 17948245526767051747 | `Gohma_DefeatBoss` |
| King Dodongo | 5936534468710061389 | `DodongoCavern_BossGroundChange` |
| Barinade | 17608884438514432711 | `Get_StoneOfWater_IsAfter_Step13_01_Exp` |
| Phantom Ganon | 18379569660496940670 | `SageOfForest_IsAfter_Step08_Exp` |
| Volvagia | 9478330070473364248 | `FireTemple_BossGroundChange` |
| Morpha | 14426685265732353862 | `SageOfWater` after `Step07_2` |
| Bongo Bongo | 17599164808183510748 | `SageOfShadow_IsAfter_DefeatBoss_Exp` |
| Twinrova | 4720088048159616469 | `SageOfSpirit_IsAfter_Step09_01_Exp` |

All eight have a permanent `Bool64bitKey` keyed by their Hash, reset 24/save file 0. Their pickup base
inherits `ActorGameDataSetting=NoRespawn`. Gohma additionally reads
`InsideTheDekuTree_Heart_Container_Obtained` to delete its pickup; the room graph writes this from its
death-related signal. The replacement retains that complete wiring, not a fabricated completion flag.

`patch/drops.py` changes only Gyaml, keeping Hash, Phive placement, room/transform, AiGroup Id/Path/
Reference and both group memberships. It refuses stale actors or missing binding/memberships.
Provisional native palette: Heart Container (`Obj_Heart_Container`), Piece of Heart (`Obj_Heart_Piece`),
Deku/Hylian Shield (`Obj_Shield_Deku`/`Obj_Shield_Hylian`), Red Rupee (`Obj_Rupee_Red`, 20 rupees).
The shields/rupee worked as freestanding pickups in section 11; persistence at a boss is still unplayed.
Inventory-only `Item_*` majors are not pickup actors. Fire Arrows remain excluded: retaining an unrelated
boss script group does not establish the object-specific dependencies absent in round 2's crash.

Opt-in `--shuffle Chest BossHeart` admits the eight existing checks; default remains Chest only.
Non-native pool items are held away from BossHeart through the existing `item_location_types`, intersecting
prior restrictions. Constrained normal filler therefore uses the existing priority stage rather than
unrestricted fast fill. Native destination actors are separate from chest actors (Red Rupee is Obj_ here).
`Heart Container -> Obj_Heart_Container` is added to the chest actor table for the new shared pool;
its chest presentation/grant also remains an in-game acceptance question. No boss rewards, quest gates,
blue warps, key policy, new flags or settings defaults change.

Test: `ingame/Test - dodongo-heart-hylian.bat`, copying nested user-save contents from
`2026-11-08_1114-main-dodongo`. All six source saves are child, Fire quest DungeonStart, boss-ground-change
false, target Hash unset, no Hylian Shield. Output changes one Banc (149088 -> 149084 bytes, allocation
149352 unchanged). **Kareem:** follow `ingame/dodongo-checklist.md`: no early spawn; defeat King Dodongo,
Hylian Shield instead of a maximum-heart increase; uncollected recovery and no duplicate after
Save/Continue/re-entry. Observe the overlay-open log and `check_dodongo_save.py`'s read-only saved Hash.

### Gold Skulltulas: keep the native pickup

Section 23's ordinary replacement loses the native token AI. An alternative data experiment changes
only the native `Obj_Token_Gold` pack's `PouchContentParam.PouchActor` from `Item_Token_Gold` to
`Item_Boomerang`. The entire `Item_Token_Gold.root.ainb`, including `OneShotGoldTokenDeadAfter`, remains
byte-identical, as do the enemy's GoldTokenGmdHash overwrite, model, physics, attachment and pickup rules.
Member shrinks 740 -> 736 bytes (allocation 5984 retained); pack 54636 -> 54628 (allocation 54968 retained).
No nested resource growth or generic component-size formula is assumed.

This is **global to all Gold Tokens**, not a per-location shuffle. PouchActor is not an exposed instance
blackboard field. Native GetType, SpecialDeal and fixed maximum 100 stay unchanged; **[INFERENCE]** they
may still force token-specific grant/count behavior. A preserved callback alone does not prove its engine
implementation saves the enemy Hash when the pouch identity changes.

`tokens.grant_experiment()` writes `ingame/native-token-boomerang/`. Adjacent
`Test - native-token-boomerang.bat` copies `2026-11-07_llr-tower-before-pickup` into its own user.
The ranch tree Hash 341792603838029977 is unset, Boomerang absent; manual slot 01 has nine tokens.
**Kareem:** follow `native-token-checklist.md`: native-looking token, uncollected recovery, actual Boomerang
ownership/use versus token count/text/model, then saved Hash and no respawn after Save/Continue.
No game or launcher has been run by the agent.

`--shuffle Token` remains refused. Per-check selection still needs a reviewed instance grant channel,
validated distinct actor definitions/registration, or an upstream hook; no global experiment is presented
as tokensanity. Four-gate and actual CLI/replay results are recorded in the round report.

**In game (Kareem via Claude, 2026-11-08, Hookshot 2.0.1):** King Dodongo's Heart Container swapped for a Hylian Shield: the shield appeared in its
place, no heart was added, and it did not come back (`dodongo-heart-hylian`). The native token with its pouch
redirected to the Boomerang dropped as a token, was collected and counted as a token, and gave no Boomerang
(`native-token-boomerang`): the pouch reference does not decide a token's grant. Tokens stay unshuffled.

## 28. Round 7: shopkeeper gift, Treasure Chest Game and boss rewards (cs7d)

Build `e0f3ccfa`, read-only dump. Research, commands, questions and controlled player artifacts:
`plans/rounds/r7-gifts.md`; external scripts/data only under `E:/OOTRemake/work/r7-gifts/`.

### Shopkeeper's shield as one gift check

The round-6 trace corrects section 19's old once-only claim: `present_DekuSheld` Event45 excludes an
equipped Deku Shield, while Event63's first-talk Bool selects Event117 (first) or Event116 (repeat).
Both grant `Obj_Shield_Deku`; Event44 sets the Bool after the first grant. An active-flow scan found
exactly those two original references to `HaveTalked_Npc_Kokiri_001_Shop_Child_PresentDekuShield`.
It is already a saved Bool (Hash 3217462169, false/reset 8/save file 0). D22 therefore needs no new flag
or GameDataList layout change.

With Gift shuffled, `KF Shopkeeper Gift` is one remake-only missable check with both stable flow/event IDs,
not an invented OoTR check. The copied gift spec moves the existing `KF Kokiri Shop` free-shield
event's rule/source to the placed location and removes its implicit shield grant. Access still requires
the early child tree visit past Mido; it cannot bootstrap its own initial shield. Event45 becomes a
saved-Bool query with the same offer/no-offer branches; both grant steps set completion immediately
after handing over the placed actor. The equipped-shield dependency is gone only for this shuffled
check. Explicit same-actor patch probes also normalize it. Unshuffled logic/flow keep vanilla repeats.

`Obj_Shield_Deku` and `TBox_Shield_Deku` have the same PouchActorInfo equipment/category fields
(both ages `Weapon_Shield_Deku`); the former is a backwards actor alias for the existing Deku Shield
logic item. Gift pool matching resolves existing aliases rather than mistaking the native gift for an
unmapped upgrade. No new item or unrelated gift family is enabled.

The synthetic and real-flow control-flow interpreter checks one grant with either equipment state,
no grant on repeat/restored completion, and completion after either original branch; an exact inverse
delta restores the entire original flow. Those oracles are file/control-flow proof.
Controlled new-game output `ingame/shopkeeper-boomerang` supplies a shield in Mido's far-right chest
and a once-only Boomerang from the shopkeeper. Its flow grows 50552 -> 51200 bytes; allocation
50832 -> 51472. No GameDataList is written. Checklist/isolated release-only launcher are in the round file.

Kareem confirmed via Claude (2026-11-08): Boomerang with the shield equipped, nothing on later
talks. No game was rerun by the agent. His option 1 keeps the native story window and forbids
progression at the shuffled check: its `Missable` location type is rejected for progression by
`allowed()`. Gift expansion/effective-CS1 replay include the new type. The controlled Boomerang
probe is engine evidence, not a placement permitted in ordinary generated seeds under this policy.
Extending the native window is later work. A 20-seed synthetic generation regression failed before
the guard (seed 1 put Deku Shield there) and passes after.

Initial pre-policy public child-slice CLI smoke (seed 7, Chest+Gift): 17 checks, three spheres, 16 resources;
both merchant branches grant the placed Fairy Ocarina, no implicit shield event or new GameDataList.
The written spoiler/note includes its two physical IDs and visit directions. A second CLI/CS1/hash-seed
process produced 18 byte-identical files; independent child-only Search won. That initial smoke did
not substitute for the whole-world Chest+Shop+Gift seed 7, which exposed D25 ammo consuming early
Fire-key capacity. Claude subsequently authorized the generator follow-up below.

### Generator follow-up: restriction order before ammo

The reviewer-authorized ordinary fill order is own-dungeon items, type-held items (songs and Shop
refills, regardless of class), D25 bag-gated ammo, remaining progression, then filler. The type-held
pool takes sparse allowed capacities before general refills, preserving Blue Fire's gated sale slots.
Type-held native ammo still waits for the dedicated D25 stage: its bag requirement and D27's
non-BossHeart type restriction are both enforced. Shop-held Buy refills remain in the type-held stage.
Constrained/progression stages assume all not-yet-placed items; the D20 return-kit prerequisite is
unchanged. Unrestricted junk retains fast fill, so otherwise-beatable slices may contain unreachable
junk. No retry bound, native rule, item eligibility or gift story window is relaxed.

Three synthetic regressions cover ammo consuming the only entrance-key slot, the type-held song/bag
dependency cycle and type-held ammo bypassing D25. They fail before their aimed fixes and pass after. Actual
whole-world seed 7 mode/attempt/sphere evidence and final gates are in `plans/rounds/r7-gifts.md`;
these do not claim a Hookshot play run.

### Treasure Chest Game: contents experiment only

The first prize is Hash `16881481538337649070`; the same-position repeat red-rupee actor is
`6781536951709667179`. Only the first prize's drop and native preview change in the controlled output:
`Obj_Heart_Piece` -> `TBox_Rupee_Red`, `Obj_Heart_Piece_MiniGame` ->
`Obj_OrnamentalRupee_Red_MiniGame`. All ten game-room boxes and the repeat prize remain vanilla.
`GetEventName`, repeated-opening setting, identity, AI groups, links and all other fields are unchanged.

The EventSetting row `MiniGame_ChoiceTreasure_OpenClearTreasureBox` runs
`MiniGame_SequentialChoiceTreasure:MiniGame_SequentialChoiceTreasure_OpenClearTreasureBox`.
Event66 passes `ContentName` to OpenTreasureBoxClear; Event191 passes it to
`Dm_SY_Treasurebox:SuccessForMiniGame`. ClearFlagOn Event146 sets
`MiniGame_ChoiceTreasure_IsClear` (Hash 3046747885; false/reset8/save0); both reward Hashes have
permanent type24 Bool64bitKey entries. No flow or flag is changed.

Output `ingame/treasure-red` and its release-only isolated save-copy launcher use the child ranch
backup `2026-11-07_llr-tower-before-pickup`, manual slot 01 (child, Sun's Song, first-clear false,
first-prize Hash unset). One resource: Market Child Static 259184 -> 259100 bytes, existing entry
259464 retained. Exact inverse two-field delta, compression/readback, unchanged source/backup
checksums and static launcher checks passed. Game acceptance is pending Kareem; D17 is not enabled.

### Nine boss rewards: research only

Reproducers: external `boss_rewards.py`, `warp_trace.py`, `warp_graphs.py`, `story_gate_trace.py`,
`gate_readers.py`; active version map used, **640 flowcharts / 261 timelines**. The five adult
medallion grant files use `.110.bfevfl.zs`, not their obsolete unversioned copies. Every row below
calls `GetPouchContent:GetPouchContentByActorName` with the named `ActorName`. Three stone grants
run at cut entries; adult medallion grants run after their awakening cutscene. The ninth reward,
Rauru's Light Medallion, is **not a ninth boss/blue warp**: it belongs to the first sword-pull story.

`Escape` below means `Dm_SY_BancChange_EscapeDungeon`; its event IDs name the transition into the
grant scene and its separate quest-completion write. Saved quest Enums are reset8/save0; the
`HavePlayedEvent.<grant flow>` history Bools also exist, reset8/save0. No new flag is needed merely
to preserve the existing one-time blue-warp reward sequence.

| Check | Blue-warp request / first-pull source | Grant flow, entry/event | Actor | Separate story completion |
|---|---|---|---|---|
| Queen Gohma | `InsideTheDekuTree_BossArea_Warp` -> Escape `BossArea_WarpIn`, then `Warp_Kokiri` | `Dm_Kokiri_0130`, `C08/Event22` (Escape Event2) | `Item_Stone_Forest` | Escape Event1: `Get_StoneOfForest=Complete` |
| King Dodongo | `Get_StoneOfFire_EscapeDungeon`; arrival boot `Get_StoneOfFire_Complete` | `Dm_DeathMtTrail_0025`, `C01-07/Event26` (Escape Event60) | `Item_Stone_Fire` | Escape Event46: `Get_StoneOfFire=Complete` |
| Barinade | `Getout_JabJab` -> Escape `Get_StoneOfWater_LeaveFromJabuJabuBelly` | `Dm_ZoraFountain_0030`, `C03/Event3` (Escape Event87) | `Item_Stone_Water` | Escape Event77: `Get_StoneOfWater=Complete` |
| Phantom Ganon | `ForestTemple_SageOfForest_EscapeFromTemple`; first clear reserves SageRoom | `Dm_Awake_Forest_Get.110`, `EntryPoint0/Event13` (Escape Event213, after `Dm_Awake_Forest` Event211) | `Item_Medal_Forest` | Escape Event199: `SageOfForest=Complete` |
| Volvagia | `Demo_SageOfFire_ClearEvent`; first clear reserves SageRoom | `Dm_Awake_Fire_Get.110`, `EntryPoint0/Event13` (Escape Event31, after `Dm_Awake_Fire` Event21) | `Item_Medal_Fire` | Escape Event40: `SageOfFire=Complete` |
| Morpha | `Demo_SageOfWater_ClearEvent`; first clear reserves SageRoom | `Dm_Awake_Water_Get.110`, `EntryPoint0/Event13` (Escape Event98, after `Dm_Awake_Water` Event97) | `Item_Medal_Water` | Escape Event41: `SageOfWater=Complete` |
| Bongo Bongo | `ShadowTemple_BossArea_Warp`; first clear reserves SageRoom | `Dm_Awake_Shadow_Get.110`, `EntryPoint0/Event3` (Escape Event126, after `Dm_Awake_Shadow` Event111) | `Item_Medal_Shadow` | Escape Event73: `SageOfShadow=Complete` |
| Twinrova | `SageOfSpirit_Clear`; first clear reserves SageRoom | `Dm_Awake_Spirit_Get.110`, `EntryPoint0/Event14` (Escape Event143, after `Dm_Awake_Spirit` Event133) | `Item_Medal_Spirit` | Escape Event141: `SageOfSpirit=Complete` |
| Rauru | `DoorOfTime:DoorOfTime_Draw`; SageRoom first-pull route, Event101 | `Dm_SageRoom_0005`, `Shine_Get_C18/Event48` | `Item_Medal_Light` | DoorOfTime Event93: `DoorOfTime=Complete`; Event103 sets adult era |

All eight boss rooms place `Obj_WarpPoint_A_01` in their boss prefab's reference group, alongside the
escape event request, separate from the heart container. Decoded native `Create_WarpPrefab` inputs:
Gohma `Gohma_DefeatBoss`; Dodongo `DodongoCavern_BossGroundChange`; Barinade
`Get_StoneOfWater_IsAfter_Step13_01_Exp`; Phantom Ganon `SageOfForest_IsAfter_Step08_Exp`;
Volvagia `FireTemple_BossGroundChange`; Morpha the `SageOfWater` `Step07_2` order check;
Bongo `SageOfShadow_IsAfter_DefeatBoss_Exp`; Twinrova `SageOfSpirit_IsAfter_Step09_01_Exp`.
These control physical post-boss warps, not reward ownership. First-clear/revisit branches read quest
completion, retaining exit/revisit behavior without granting a fresh reward on every warp.

**Temple of Time mismatch, confirmed rather than inferred from reward names.**

- `DoorOfTime:DoorOfTime_CheckStoneNum` Event38/39/56 reads Fire/Water stone **quest completion**,
  not the held stones. Event68 reads `HavePlayedEvent.Dm_MelodyGet_Zelda`.
  Door opening Event60 requires `DoorOfTime_IsAfter_Step04_Exp`, Event27 plays melody 4,
  Event69 checks the opened Bool and Event58 the door cutscene's history; Event53 sets
  `Market_Child_TimeTempleDoor_Opened`, Event57 advances Step06. First-pull attention is gated by
  that quest step (`Market_Child_Prefab_e700`, section 16), not independent stone inventory.
- Adult return and Prelude's separate trigger read `SageOfForest_IsCompleted_Exp`
  (`Market_Adult_Prefab_89da` / `_edc2`, section 16). Finding Forest Medallion elsewhere cannot
  open the pedestal, and moving that medallion away must not forge Forest completion.
- The later Light Arrows chain is `AllSage:Market_Adult_Field_GetArrowLight`, Event17 ->
  `Dm_TimeTemple_0130`; Event25/26 read `HavePlayedEvent.Dm_Awake_Spirit` and
  `...Dm_Awake_Shadow`, not Spirit/Shadow Medallion ownership. `SageOfLight`/`AllSage` progress
  separately. `AllSage_AwakeSageCount` is an existing saved Int default 5; Escape decrements it on
  the five sage routes (Event249/251/252/253/267). No literal flow/decoded-logic reader of that Int
  was found; do not invent a medallion-count gate from its name.
- Fresh query survey found **zero literal stone/medallion item queries in 640 active flowcharts**.
  The corresponding item symbols also do not occur in the 1822 previously decoded Logic graphs.
  This does not claim the engine has no implicit readers; only the inspected data corpus.

What a future reward shuffle needs, **not implemented here**:

1. Keep all nine gifts class `more` until owner-approved gate semantics exist. Swap every literal
   grant at its stable flow/event identity, using active `.110` versions; retain awakening scenes,
   warp exits, quest completion, environmental changes and the independent Master Sword/era actions.
2. Keep **check completion** separate from **reward ownership**. Existing quest/history gates
   already supply one-time collection; replacing them wholesale with IsGet would replay boss scenes
   when the vanilla medal is absent. Do not mark a dungeon complete when its reward is found elsewhere.
3. For gates intended to follow collected rewards, replace the concrete Temple/scene readers and
   their outer area/quest triggers with item checks, or explicitly change world logic to follow
   physical boss/quest completion. Grant-only swaps leave the current item-based world oracle unsound
   in both directions. D20's physical Forest-return guarantee remains a distinct constraint.
4. Verify reward actors from their permitted destinations, matching get display/text and saved
   inventory; check no duplicate after warp/reload, then rerun chronological beatability/return
   proofs with the chosen gate policy. No chest allowlist is expanded by this research.

**Kareem/co-owner: should the Door of Time and later reward gates follow the stones/medallions
actually found, or remain tied to physical dungeon/awakening quest completion? Which gates, beyond
the Door of Time, should change?** Proposed separation: reward ownership for chosen reward gates,
physical completion for world restoration/return travel; no product choice is silently applied.

## 29. Round 7: location hints never name junk (cs7e)

D29 (Kareem) supersedes section 25's original OoT Randomizer random/sometimes item policy.
`generate.hints._worth_naming` defines one candidate class for item, always, sometimes and random hints,
using the world's resolved item metadata: progression, hearts and permanent non-progression upgrades.
Explicit consumable exclusions take precedence over progression (Bombchus, Blue Potion, Buy refills
and bottle-content variants included). Empty Bottle and Ruto's Letter remain progression; Odd Potion
is a trade item. The three normal-class capacity upgrades in the world are included explicitly.

Reviewer correction (Claude, after `6fdf7e1`): new seeds' **item** hints additionally intersect that
class with the existing major-item set (`get_good_item_hint`, OoT Randomizer `Hints.py:882-891`).
They never name hearts or normal capacity upgrades; always/sometimes/random can still name them.
The already-swapped 7c continuation is not rebuilt or changed by this correction.

Barren/Way-of-the-Hero eligibility and the required-item oracle are unchanged: heart/capacity finds
may be named without making their area non-barren. Candidate filtering changes RNG draws, so exact
stone assignments need not match older builds. Tests, continuation output and verification evidence:
`plans/rounds/r7-hintfix.md`. No game data or item-pool/settings change.

Continuation built at `E:/OOTRemake/work/r7-hints/seed-shop-7c-next`: all 228 placements and all 77
original 7b resources byte-identical, beatable in 25 current-logic spheres. Adds the no-mask stone flow
and 13 language archives; the three size-growing archives remain omitted as in section 25's continuation,
so 7b's size table stays unchanged. Independent readback checks all 40 lines in each written archive
and highlight resets; the round file lists the 40 lines. **Kareem: after Claude swaps the staged output
following game exit, check the Temple of Time's four lines and normal colour after each name.**
No agent game run, played-folder write or save/launcher change.

## 30. Round 7: graves, bomb lift strength and owned-shield substitute (cs7f)

Build `e0f3ccfa`; read-only Banc, actor packs, PouchActorInfo, GameDataList, guest game NSO and save
samples. Full provenance, native addresses, commands and pending gameplay checks:
`plans/rounds/r7-play.md`. Reproducers/decoded data stay outside the repo:
`E:/OOTRemake/work/r7-play-cs7f/`. No game, launcher, save edit or active-overlay rewrite.

### Three pull-back graves, one viewpoint

Stand at the Royal Family's Tomb entrance (48.4,104.6,2.6), **face out over the graveyard**.
Kareem's fourth-from-right ReDead observation calibrates handedness; the other ordinals are
placement-derived, not separately played.

| Grave | Direction | Contents |
|---|---|---|
| Shield / ReDead | Nearest row of seven, fourth from right, unmarked; hole x21.5/z11.2 | Chest 16912540161937823130, ReDead 17994273783244561622 |
| Heart piece | Same row, leftmost/seventh from right; hole x21.4/z23.2 | Chest 9622128545943056087; no enemy/song puzzle |
| Marked fairy grave | Lower row of five, second from right, flowers/butterflies; hole x4/z5.7 | Cracked wall 9366825990748670811, eight fairies behind it; **no chest or shuffled check** |

Both age Static/Dynamic copies were checked. Heart chest has only its item Dynamic parameter:
no Presence, spawn override, actor link or AiGroup/song trigger. `True` remains the inside-grave
rule; child entrance still needs night and `Time Flows`.
Remake fact corroboration, not copied guide text:
https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2 (#8);
https://www.ign.com/wikis/ocarina-of-time-remake/Spiritual_Stone_of_Fire_-_Kakariko_Village_Walkthrough .

N64 comparison only: https://www.zeldadungeon.net/wiki/Graveyard_(Ocarina_of_Time) (facts supplied by
Claude; direct fetch returned 403). N64 combines shield chest/fairy wall in its marked grave and
requires Sun's Song for the heart chest. Remake splits them. `child_graveyard.toml` introduces
`Graveyard Fairy Grave`, moves Fairy out of Shield Grave and requires `has_explosives and has_bottle`,
not Hammer. Both ordinary grave entrances keep the same child night/time-flow access; no check added.

### Bomb capacity is not bomb usability

Samples: newest 7c under `E:/OOTRemake/work/r7-hints/user-seed-shop-7c`, main backup
`E:/OOTRemake/work/save-backups/2026-11-08_2140-main-jabu`. Exact paths/digests in external report.
Main digest stayed unchanged; live 7c changed during play but the diagnostic fields stayed the same.

| Saved name | 7c | main |
|---|---|---|
| `IsGet.Item_Bomb` / `IsGet.Item_BombBag_Small` | true / true | true / true |
| `PouchData.Item_BombBag_Small.StockNum` / `PouchContentMaxNum.Bomb` | 1 / 20 | 1 / 20 |
| `PouchData.Item_Bomb.StockNum` | 20 | 8 |
| `HavePlayedGetEvent.Item_BombBag_Small` | false | true |
| `IsGet.Armor_Child_Gauntlet_Goron` | false | true |
| `PlayerStatus.LiftGrade` (Enum hash 0x59979321) | None | Low |

**Native gate:** spawned `Item_Bomb` LiftableParam requires Low (hash 3655598229), whereas 7c's saved
None is hash 3069107721. Bomb pre-lift calls `0x027e2c50 -> 0x02e50760 -> 0x02e50570`;
`0x02e506ac..b0` compares required <= available. Player virtual +0x100 override `0x02e878d0`
reads PlayerStatus/LiftGrade and maps None/Low/Middle/High to 0/1/2/3. Failure finishes pre-lift:
this explains Kareem's brief raise/cancel, not missing capacity. No bag get-history use gate was found
on this path; setting a presentation flag is not a justified fix.

The real small Bomb Bag's expansion resource targets bombs/Bombchus capacity 20, not strength.
Goron Bracelet (`Item_Gauntlet_Goron` / `Armor_Child_Gauntlet_Goron`) grants LiftGradeUP Low.
**[INFERENCE] The KF Storms bag alone will not fix canceled bombs with strength None; Bracelet should.**
Do not infer permanent save damage. Future shared bomb logic needs the native strength requirement,
or an owner-approved gameplay change limited to ordinary bombs; proposal/request in the round report.
No shared helper, saved flag, bag policy or game parameter was changed by this investigation.

### Pre-D25 7b/7c can continue via native Bombchus

Kareem via Claude, 2026-11-08: Bombchus used on main with no Bomb Bag. Native Item_Bombchu
LiftableParam independently requires **None**, not Low. Its SmallBagActor points to the Bomb Bag,
but that link does not impose a lifting prerequisite.

Readback of **written** 7b GC Shop Item 8: native Shop_BombchuBundle_05, five Item_Bombchu,
PriceOffset 35, StockNum -1. Normal repeatable ShopItem sale, not a chest-style grant; no explicit
bag/Dodongo gate in this item branch (section 24). 7b/7c's 228 shuffled placements are identical.
Fixed-placement replay with current rules and native fixed vanilla mapping wins in 25 spheres;
GC8 at 4 precedes Windmill/Storms at 9 and KF bag at 10. Removing GC8 alone stalls before the pull
and bag (334 checks, 8 spheres). That establishes the logic dependency, not every possible game route.
The child-only prefix obtains unshuffled Saria's Song at 3, Darunia's Bracelet plus GC8 at 4;
it reaches the pull without adult loot or the Storms bag.

**Advice:** keep these saves; buy/use GC8 Bombchus for early explosives. Learn Saria's Song and play
for Darunia to obtain the unshuffled Bracelet, then retry current bombs rather than waiting for the bag.
GC8 purchase/use on7c and the post-Bracelet bomb comparison still need Kareem; no new gameplay
result is claimed. D25 remains the policy for new seeds, not a reason to rewrite this old output.

### Vanilla shield grave: explicit fallback, not universal duplicate conversion

Both ages' A_06 chest 16912540161937823130 explicitly checks TBox_Shield_Hylian and selects
TBox_Rupee_Red when already held; its default CheckCondition is true. Native root nodes 16/30/29
perform count>0 then XOR CheckCondition; nodes 24/25 select main/substitute. Red rupee's bundle count
is 20. Kareem's vanilla-file 20-rupee observation matches this exact branch, not a different grave.

The existing shuffled writer `patch_tree` already overwrites primary **and** substitute with the new
reward, so owning the shield cannot turn shuffled progression into vanilla rupees. Real-placement,
in-memory smoke across both ages selected shield/red rupee before patch and Boomerang/Boomerang
after patch. No blanket 20-rupee rule for other duplicate items, and no shuffled in-game result inferred.

## 31. Round 7: usable bombs need age-appropriate lift strength (cs7g)

D30, build e0f3ccfa. Native trace: section 30; independent PouchActorInfo/actor-pack audit and
commands: `plans/rounds/r7-bombs.md`, `E:/OOTRemake/work/r7-bombs-cs7g/lift_audit.py`.
Canonical Item_Gauntlet_Goron / Armor_Child_Gauntlet_Goron grants LiftGradeUP **Low**;
Item_Gauntlet_Silver / Armor_Adult_Gauntlet_Silver grants **Middle** and declares AdultEquipment;
Item_Gauntlet_Gold / Armor_Adult_Gauntlet_Gold grants **High** and declares AdultEquipment.
The three ExpansionAbilityActor resources agree. Item_Bomb needs Low, Item_Bombchu needs None;
the Bomb Flower fruit also requires Low. The bag expands capacity, not lift strength.

`data/world/remake/bombs.toml` supplies guarded helper overrides, leaving translated files intact.
Bombs requires Bomb Bag and the actual Goron Bracelet as fixed child, any strength upgrade as adult;
progressive mode's first strength tier represents the Bracelet. Higher fixed adult gauntlets do not
substitute for the child's Bracelet through their shared progressive alias. `can_use(Bombs)` shares
that rule; both Octorok bomb shortcuts now use Bombs instead of direct bag possession. All other
bomb paths inherit it through existing helpers, including explosives/blast-or-smash and bomb-only
tricks. There is no existing `has_bombs` alias. Bombchu supply helpers and strength-gated local
Bomb Flower routes remain unchanged; no item actor, saved flag, gameplay parameter or D25 policy
is patched. Helper overrides require `rule`, `was`, `source` and unique ownership.

Synthetic independent-path tests exercise bag-without-strength rejection, per-age fixed tiers,
the progressive first tier, wake-on-strength, unchanged Bombchu/Hammer/flower alternatives and
stale/duplicate/missing helper contracts. Native metadata plus search behavior is not new in-game
acceptance: **Kareem's same-bombs-before/after-Bracelet comparison on 7c remains pending.**

Search acceptance: real seed 7 CLI modes Chest, Chest+Shop, Chest+Shop+Gift and default `CS1`
succeed in **1, 3, 10, 1** attempts within the unchanged ten-attempt bound, with **25, 24, 27, 25**
collection spheres. Gift mode uses its last permitted attempt; its rejection payloads are retained.
The old 7b's **228 unchanged placements** still win in **25 spheres**; no continuation is rewritten.

Matched-placement timing (1-based first ordinary-bomb-use sphere, not ammo pickup): seed 7 Chest
**3 -> 5**, Chest+Shop **6 -> 6**, Chest+Shop+Gift **4 -> 7**, default CS1 **3 -> 5**;
old 7b **7 -> 7**. Independently, all 200 logic-level default seeds 0–199 win before/after:
**153 later, 47 unchanged, zero earlier**, zero newly uncollected checks. An upper-bound inventory
audit over **2,405** exit/event/location/stone rules finds zero newly impossible rules. Existing
disabled/N64-only rules are not claimed satisfiable. Exact method, output paths, full diagnostics
and verification commands are in the round report; generated output and game data stay outside
the repository. These are search/data proofs, not an agent game run.

## 32. Round 8: what the remake's world asks of the fill (cs8a)

Build e0f3ccfa. Measurement method, tables and every failure payload: `plans/rounds/r8-fill.md`; scripts and
JSONL under `E:/OOTRemake/work/r8-fill/` (outside the repository). Facts about the world, as the fill sees it:

- **The Fire Temple has no spare chest for its keys.** With every other item held, its 16 shuffled chests need
  0 (Near Boss), 1, 1 (both Big Lava Room chests), 3, 3, 4 x6, 5, 7, 7, 8, 8 of its eight small keys
  (`remake/adult_fire_temple.toml`: real keys, no N64 freebie, the lower locked door needs all eight). So the
  key-free chest and both Big Lava Room chests must hold small keys in every seed; no Fire chest needs its boss key.
  The Forest Temple likewise needs a small key in its First Room Chest (its only key-free chest); its items are
  placed by the return kit (D20). The other dungeons have slack: Water 4 key-free chests for 4 keys, Shadow 4,
  Spirit 4 for 5 keys, Gerudo Training Ground 17 for 9.
- **Song checks equal songs.** With Gift and `songs = song` the twelve song checks take exactly the twelve songs;
  several song checks need a song (the Royal Family's Tomb needs Zelda's Lullaby, Sheik at Colossus needs
  Requiem), so songs are placed as their own stage and retried there, as OoT Randomizer does.
- **Before Mido there are five chests.** With the forest closed (D24), a child without the Kokiri Sword and a
  shield reaches only Mido's four chests, the Kokiri Sword Chest, the Kokiri shop and the Lost Woods checks that
  need nothing (Saria's gift was out of reach in the failure printed, Gift seed 66). The last progression items an
  assumed fill places need one of those five chests.
- **The logic reads three normal items.** `shops.toml`'s `Nuts` and `Sticks` helpers read the physical
  `Deku Nuts (5)`, `Deku Nuts (10)` and `Deku Stick (1)` packs; no other rule reads a non-progression item. They
  stay normal (D29: hints never name them), so the fill never assumes them.
- **Bombchu packs are the only part of `has_explosives` that needs no Bomb Bag** (`free_bombchu_drops`; D30: bombs
  also need the Bracelet), and D25 puts every pack behind a Bomb Bag, so nothing placed before the packs may rely
  on one.

## 33. Round 8: chest ocarina presentation without equipment mutation (cs8b)

Build e0f3ccfa; external read-only reproducers and detailed acceptance boundary:
`plans/rounds/r8-getitem.md`, `E:/OOTRemake/work/r8-getitem/`. Kareem's post-bind Fairy Ocarina
invisibility is confirmed input, not retested by the agent.

The ocarina mesh is correct and also visible on the song stand-in. Correction to section 26:
`PouchContentGuestPerformer` uses its own `EquipmentCommon.event.root` exceptional binding,
already including the get-demo bind. Instrument EventPerformer substitution alone did not
establish a repair of that path. Native ocarinas are Accessory equipment, not generic get
objects. Saria's flow explicitly participates/binds the instrument to Player `Weapon_L`;
native cutscenes also use separate `Dm_Item_Ocarina_{Fairy,Time}` props, without Accessory.
**[INFERENCE]** Generic chest equipment presentation is the mismatch; an exact engine
visibility predicate has not been proved.

The explicit `getitem.changes` experiment now stages those existing native props only for
ocarina contents, using native hand binding, then offstages them at chest cleanup. Normal
contents retain the original guest chain. It changes only the two chest flows and their
allocations, not any playable ocarina/prop pack, inventory table, grant helper or gift flow.
The prior ineffective instrument-pack/heap mutations are removed. Song mesh changes remain.
The existing UI message-target String64 selects the prop; no new saved flag or layout edit.
Grant/text still use the original ContentName, not the prop. This is a handheld model,
not a promised floating/rotating get model or a newly certified chest grant.

Synthetic lifecycle/normal-path/inverse regressions and actual common-writer smoke pass.
Small flow 74808 -> 79616/allocation 79888; big 38848 -> 43680/allocation 43952. Native big
Rotate/NoHit/Bind order differs from small NoHit/Bind/Rotate and is guarded independently.
**Kareem: visibility, position, disappearance, actual instrument use and Time upgrade/song
retention still need the single isolated new-game experiment; no agent game run.**

The single fresh new-game experiment is `E:/OOTRemake/work/r8-getitem/ingame/chest-gifts-next/`;
the sibling `Test - chest-gifts-next.bat` and `checklist.md` specify native progression, exact chest
directions, expected models/use and overlay evidence. Fourteen existing saved chests cover Fairy/Time,
Letter, Egg, Card, Epona and all eight ordinary native masks. The seed catalog has zero mask mappings;
this experiment adds none. Sword, Slingshot and Bomb Bag chests remain native. No game/launcher run.

Independent actual-output inverse diffs and source hashes pass; reversed actor order in a fresh
Python hash-seed process reproduces all 15 resources byte-identically (`artifact-proof.json`).
Only the already player-confirmed Din's Fire and Adult's Wallet join the chest-verified list.
The new experiment admits no unreported actor; songs-anywhere's existing opt-in inference remains.

## 34. Round 8: shopkeeper gift window and shop settings (cs8c)

Read-only dump build `e0f3ccfa`; reproducible commands and player checklist:
`plans/rounds/r8-shops.md`. External research/output: `E:/OOTRemake/work/r8-shops-cs8c/`.

### Uncollected shuffled shopkeeper gift

Round 7's saved Bool `HaveTalked_Npc_Kokiri_001_Shop_Child_PresentDekuShield` remains the
completion gate (false/reset8/save0); no new flag/save layout. `Talk` initializes camera/Navi state
before Event24 -> Event23 (castle completion) -> Event21 (Gohma completion) -> Event1 (tree meeting).
When the merchant gift is shuffled, Event24 instead checks saved completion, then the same
`Meet_DekuTree_IsAfter_Step02_Exp` as Event1. Incomplete and met-tree goes to the original
Event83 offer call, past both late-story cutoffs. All other cases use original Event23 dispatch.
Both grant branches set completion, independent of equipped shield. Native shopping, quest queries,
purchase/tutorial/shelf releases and unshuffled repeat-shield behavior are unchanged.

Control-flow/readback oracles prove early/late/castle combinations, repeats, restored completion
and pre-meeting refusal. The common writer built the requested new-game Boomerang experiment:
`ingame/shopkeeper-after-gohma-next/`, own empty user and copied release-only launcher.
Mido far-right chest supplies Deku Shield so the merchant can be skipped until after Gohma
(optionally also Zelda). Flow 50552 -> 51736, allocation 50832 -> 52016; no GameDataList.
Exact inverse deltas recover the original flow and both chest files. **Kareem, 2026-11-09,
via Claude:** on a copy of his ranch save with Forest stone, Zelda's Lullaby and Deku Shield,
having never talked to the merchant, `shopkeeper-after-gohma-next` gave Boomerang and did
not offer it again. This confirms the extended window after both story milestones; no additional
overlay-log, normal-shopping or Save/Continue result is inferred from this report.

**D28 lifted for the shuffled shopkeeper gift (Kareem, 2026-11-09).** `KF Shopkeeper Gift`
is now an ordinary progression-eligible `NPC` check, not `Missable`. Its data-sourced rule remains
`is_child and at('KF Outside Deku Tree', is_child)` with no Gohma/castle cutoff; it still cannot
bootstrap Mido or be collected as adult. Gift expansion and effective-CS1/NPC replay both apply
the same world conversion and existing window/once patch. A required-progression fill and
late-story reachability regressions cover this policy. Unshuffled native flow, equipment query,
early free-shield event and rule are unchanged. The prior section 28/D28 restriction is historical.

### Partial shelves and fixed scrub fees

Settings `shop_slots=0..8` (default 8) selects the first N native indices in each of the eight ordinary
shops; mask loans stay vanilla. Selection is logical-check metadata before pool construction, so all
age/Alternative/short-stock copies share it and excluded contents never enter the pool. Unselected
`keep_vanilla` reasons survive. Affordable prices and wallet rules cover selected shelves only;
independent cheap-Deku-Shield pricing still applies even with zero selected shelves.

`scrub_prices=vanilla|fixed`, `scrub_price=0..1000` (default 10 when fixed) covers the four supported
shuffled once-sale families, not repeat vendors or unshuffled scrubs. Every tier's original call to
`SimpleShopSub_Scrub_Business_OneTime` changes only `ActorName` and `Price`; the same argument
already supplies native quote/rupee-check/payment handling. The selected-item string follows the
reward as before. Cancel/shortfall and success-only saved Bools/control flow stay unchanged.
Native prices remain 40/100 by default. Wallet predicates read the existing shops.toml tiers
(200/500/1000); the original stun/age/puzzle rule stays conjunctive. Spoiler/opening-note prices
come from the same effective fees. All three fields serialize through CS1 and have explicit CLI overrides.
Event289 quotes the supplied `SellerMessageId`. All four distinct seller labels used by the seven
grant/tier calls have a group2/type12 run-time tag on `SimpleShop_Price` in `Enemy_Event.msbt`
(all 16 language archives checked). No literal rupee amount or archive edit is needed for those price quotes; native
flavour still names the vanilla item, as with the existing reward swaps.

Provisional implementation choices by cs8c (2026-11-09): deterministic first-N indices rather
than a second random shelf-selection algorithm; fixed-price default 10; scope restricted to supported
shuffled families. Questions and exercised full-output/price boundaries: `plans/rounds/r8-shops.md`.
## 35. Round 8: gift checks, native identities and success-only merchant sales (cs8d)

Build e0f3ccfa; full command/result ledger and player checklists: `plans/rounds/r8-gifts.md`.
No agent game run. New/corrected families remain held vanilla until Kareem's results.

### Cows: placements are not independent checks

Fourteen Hashes are eight physical cows, counting age/Alternative copies: DMT 1, field grotto 1,
ranch 2, Impa's 1, Link's 1, GV 1, GF 1. No placement has Dynamic parameters selecting a milk
event or flag. Shared `Animal_Cow` GiveMilk/PushToBottleMilk fills an empty bottle with bottle 10;
`Cow_IsGetMilkFromCow` and shared talk history are not per-cow completion. Actor variants use
fixed schedules/replacement events. The active flow query inventory has no demonstrated instance
identity predicate. A new Bool alone would make one global milk reward, not cowsanity.
Reviewer narrowed this item to research: no cow patch this round; **D11 stands**.

### Skulltula House

GatheringTokenGold gives 10/Event398 Wallet_Medium, 20/Event75 AgonyStone, 30/Event194 Wallet_Large,
40/Event200 **BombchuBundle_Large = 20**, 50/Event219 Heart_Piece, 100/Event215 first Gold Rupee.
Native 10–50 saved GetReward Bools gate their checks; 100 uses the quest's completion. Event471
is the father's native repeat 200 rupees and remains untouched. The corrected 40 pool item stays
held pending acceptance; no new flag or token-count/quest change is needed.

The Gift seed step composes assigned 10–50 item previews into `Npc_SkullDad` Talk_28/Talk_23–26,
using native English item names, existing wrapping/highlighting and all 16 language archives (D26).
Existing Gossip Stone text survives composition. First 100 has no added preview/repeat slot.

### Frogs

Five stable TeachNewMusic callers: Event172 Lullaby, 220 Epona, 221 Saria, 222 Sun, 223 Time.
Each passes its own saved completion Bool. The native escalating rupees are **5/10/15/20/30 by
prior song count**, not 50 each and not a literal pouch actor. Census rows therefore have empty
item/parameter fields; no arbitrary pool item is assigned to this order-dependent native reward.

Storms' heart is **Event384** (previously mislinked as the bug game), saving StormSong at 112.
The bug game's first heart uses **Event161 or Event75** for initial/retry wins; InsectRepellent
is set after success. Native repeat Event162/Event76 Blue Rupees and failed rounds stay native.
SongClear means all six songs, not winning the bug game. All seven completion Bools already
exist, default false/reset8/save0; no new GameDataList flag is needed.

For changed ordinary songs, clone only the reachable TeachNewMusic graph for that caller.
Replace the rupee-UI subtree with the ordinary gift wrapper; preserve flag, first-song count,
growth and native repeat routing. Remap graph edges and subcall indices, retain original entries
and all untouched callers; refuse entry-local actor bindings rather than guessing. Corrected
heart identities and all five song prizes stay vanilla until gameplay acceptance; the fixed
song-pool item policy is a question for Kareem/co-owner, not an inferred five 50-rupee pool.

### Three merchants: flag only the successful grant

| Check | Stable grant call | Native price / persistence |
|---|---|---|
| Medigoron | Npc_Goron_Medigoron_Adult/Event11 -> SimpleShopRoot_Npc_Goron_Medigoron_Adult | 200; sword ownership is not check completion |
| Carpet | Npc_Hylia_044_Adult/Event3 -> SimpleShopRoot | 90; Npc_Hylia_044_Buy is unsaved reset1/save-1 |
| Granny Blue Potion sale | Npc_Hylia_053_Adult/Event12 -> GetInEventInBottle_BlueBottleShop | 100 and empty bottle; no saved purchase-completion Bool |

Granny's bottle wrapper does not reach the pouch-add census fixed point. The dedicated literal
sale is now censused separately from her unchanged Odd Mushroom/Odd Powder trade (Event167).
Her quest unlock, bottle check and price remain. This corrects the older “no literal sale” census
assumption using the active flow itself, not a shelf item or N64 assumption.

Each controlled merchant swap adds its own D22 saved Bool (reset8/save0). Medigoron/carpet get
private SimpleShop entries; original events/entries, beans and other consumers are unchanged.
Flags are set inside successful grants, never after an outer call that also returns on refusal.
Choice, funds, capacity and fees remain native. Medigoron's own two sword-ownership reads become
check reads; his private generic grant does not consume a broken knife. Granny uses the ordinary
gift wrapper plus the original 100-rupee charge on its success edge, without filling a bottle.
Revisits bypass the transaction; cancellation/poverty/full capacity do not consume the check.

Data-sourced rules retain existing adult/trade/room/approach predicates; Granny adds her bottle
requirement and carpet drops the unsupported upgraded-wallet/Bombchu prerequisites (price 90).
Every merchant stays held vanilla pending Kareem. Graph/state, serialization, allocation and
saved-Bool proofs do not establish engine presentation, actual grants/use or Save/Continue.

### D31: native child-trade sequence

Claude approved keeping `HC Malon Egg` and `HC Zeldas Letter` vanilla. The existing
`keep_vanilla` metadata excludes both checks and their items from the Gift pool; neither
actor is admitted to `chest_verified`. Native Malon, Egg hatch, Chicken/Talon and Zelda
grants remain unchanged. The shared child-trade cell is not treated as independently
retained items without an accepted ownership/cycling contract. Detailed native evidence
and pinned OoTR 526b4c8d rules/runtime patch citations are in the round file.

## 36. Round 8: freestanding native pick-ups (cs8e)

Build `e0f3ccfa`, dump/save backups read-only. Complete 36-anchor ledger, native actor-pack survey,
diagnostics, commands and acceptance checklist: `plans/rounds/r8-freestanding.md`.
Reproducers and decoded evidence stay under `E:/OOTRemake/work/r8-freestanding-cs8e/`.
Sections 32–35 belong ahead of 36 when their tracks merge; no placeholder sections are invented.

### What an anchor represents

The **36 unique HeartPieceAnchors / 55 placement copies** represent **14 placed heart pieces,
six ordinary chests and 16 named completion flags**, not 36 floor pickups. The old section 5
count of 21 named paths is superseded. Every direct reward link resolves to a permanent
type24/save0 Bool64bitKey; all 16 named completion Bools are false/reset8/save0. LLR's extra
reference is its LocationArea, not a second check. Anchors and their links stay unchanged.

The 14 placed pickups are 13 `Obj_Heart_Piece` plus GV's `Obj_GerudoValley_Heart_Piece`.
All are ungrouped, saved by their pickup Hash, inheriting NoRespawn and ActorLogicSimpleActor.
Existing heart-piece AI calls `OneShotHeartPieceTakenDeadAfter`; replacement native shield/rupee/
container actors use DropItem instead. D27's actual King Dodongo persistence result is the
precedent, not proof that every replacement at every floor/water location persists.

Census links now identify DMC volcano **744856631664786545**, wall **10331043360028932045**,
and GV waterfall **16129198288828948135**. Existing OoTR/remake access rules are retained,
not swapped by file order. The other 11 pieces were already linked. All 14 now have player
directions in the existing location-name catalog; no physical position or check Hash changes.

### Default-off Freestanding

Scope confirmed by Claude, 2026-11-09: **only the 14 anchored heart-piece checks this round**.
`--shuffle Chest Freestanding` joins them to the pool. Census-linked Collectable hearts become
Freestanding on a copied spec; original unlinked N64 Freestanding rows remain vanilla.
Digging/event hearts, keys, chests, gifts and existing exclusions keep their own types/rules.
Native grants reuse D27's single palette: Heart Container, Piece of Heart, Deku Shield, Hylian
Shield, 20-rupee Red Rupee (`Obj_`, not the chest's `TBox_` actor). All other actual-pool items
intersect prior type restrictions to stay away from floor destinations; BossHeart restrictions
compose. The CS1 string retains the option and its effective restrictions; default stays Chest.

The patch changes only Gyaml on every age/Alternative copy. Hash, Phive identity, Presence,
transforms, anchors and group tables remain. Stale/missing/duplicate actors, lost placement
identity, new unaudited AI bindings, unsaved sources and non-palette grants are refused.
An unmoved Piece of Heart retains its native GV variant rather than rewriting it unnecessarily.

### Other pickups: audited, not enabled

All 7,239 non-DreamWorld placed actor types' packs resolve. Ordinary rupees (81 green, 25 blue,
four red, two purple), 25 recovery/water hearts and three loose nut/seed/stick actors have
type24/save0 flags and native DropItem/NoRespawn metadata, but lack exact physical remake-to-logic
links; those are later work. Silver rupees 85 retain puzzle-specific AI. The two Well/Shadow keys
and eight Fortress key actors have **no saved actor Hash** and effective **AlwaysRespawn**,
despite their inherited NoRespawn base: level/key-specific logic owns their lifetime.
Fire Arrows retain the known crash exclusion. Story ocarina/letter, lures, renewable bottle
contents/fairies, diving-game rupees and shop displays do not become floor checks.

The complete family counts and respawn contracts are in the round ledger. No new physical
logic or replacement scene/callback was invented for any excluded family.

### Isolated player test and verification boundary

`ingame/Test - llr-tower-hylian-next.bat` copies the approved pre-pickup ranch backup into
its own user when Kareem runs it; bin game executable only, updates disabled, missing-exe stop.
Only LLR tower pickup 9814903750835309225 becomes Obj_Shield_Hylian. All six source saves
are child, pickup unset, Hylian Shield absent; source checksums unchanged. The agent never
started the game, launcher or a window and never copied/wrote a player save.

HyruleField Child Static **395636 -> 395656** decompressed bytes, **134949 -> 132472** compressed;
allocation **395912 -> 395944**, with the common size table emitted. Inverse tree diff and
allocation/readback checks pass. The 14-check / 26-copy whole-dump transform oracle and synthetic
palette/eligibility/restriction/CS1/BossHeart composition checks pass; full gate evidence follows
in the round file. **Kareem:** tower rear recess must show/grant the Hylian Shield, no heart
progress; uncollected recovery, then collect/Save/quit/Continue/re-enter with no respawn.
Require the Child Static overlay-open log and isolated save checker's collected Hash.
Underwater collection and other unplayed palette/location combinations remain inferred.

Seed 7 Chest+Freestanding currently exposes Track A's fill robustness issue (ten attempts,
last Boomerang 43 allowed/57 remaining). Exact first-attempt Fire-key frontier/placements and
repro are recorded in the round file and posted to `cs-r8`; no retry/rule/fill change here.
Claude permits independent successful-seed smoke plus the synthetic proof while Track A fixes
that failure; no seed 7 success or gameplay certification is claimed.

## 37. Round 9: item-bar assignment and age-locked pickups (cs9a)

Read-only dump/build e0f3ccfa and bow-lock backup; full button-family age table, native addresses,
provenance, limits and reproducible probes: `plans/rounds/r9-itembar.md`,
`E:/OOTRemake/work/r9-itembar-cs9a/`. No agent game run or save edit.

Kareem's seed 8 Bow joined child Link's greyed ZR bar and jammed item use. Zone transitions did
not help; Save and Continue removed Bow from the bar and restored use. The backup confirms
childhood, acquired `Weapon_Range_Bow`/stock 1 in all six saves; four retain Bow in saved enum
0xa0029837. Two other assignable enums are saved; fourth candidate 0x76f85e6d is save-1, so its
absence from progress.sav is expected. Separate live selection is not represented by ownership alone.

Kareem also reproduced seed 8's lock in **Lichii**: Bow obtained before Boomerang, item use
locked, Save and Continue cleared it (`answers.md`, R9-LICHII; reviewer relay).
This establishes game behaviour, not a Hookshot-specific defect. No gameplay/fill change follows.

`PouchActorInfo` supplies `AssignableItem`; the UI's
`UI/Pouch/PouchTable/PouchTable.game__ui__PouchTable.bgyml` supplies per-variant
`IsUsableChild`/`IsUsableAdult`. Child-only ZR families: Sticks, Slingshot, Boomerang, Beans,
Weird Egg/Chicken/Letter. Adult-only: Bow/arrows, Hammer, Hookshot/Longshot and adult trade
items. Nuts, bombs, Bombchus, spells, bottles, Business Scrub Seed and Amiibo are both-age
in that metadata. Ocarina, head and boot shortcuts are distinct; the round file separates them
and the scene-only fishing controls rather than inventing ZR permissions.

Chest `ContentName` reaches `GetPouchContent/Event0`, whose `IsEquipDIrect` is **already false**.
Native get code separately calls its selected-item setter (0x01110158..0x01110198 ->
0x01211c00). Native inventory readers consult the table's age fields. **[INFERENCE]** Get-time
selection misses an age-filtered rebuild that Save/Continue performs; the precise boot caller
and live use-cancellation predicate are unproved. Display/model changes do not repair inventory.
The shipped equipment-sync action calls wearable reapplication (0x02951f50 -> 0x00f201b0),
not a demonstrated item-bar refresh. No safe data-only fix is established and none is enabled.

Facts-only lead: [sloperina docs/FINDINGS.md](https://github.com/PracticeROM/sloperina/blob/master/docs/FINDINGS.md),
sections 1/2/5.6 (enum hashes, PouchTable, separate wheel state); independently checked against
the player's data. No GPL code/file copied. Adult Slingshot/Boomerang recovery remains
Kareem's reverse-direction check; only the child Bow failure/recovery is game-confirmed.

Round 9 takes the specified fallback: `data/itembar.toml` sources warning ages from the native
table; `generate.itembar` replays complete chronological sphere prefixes through Search,
including fixed finds and the isolated child pre-return view. The spoiler/note list opposite-age
first-frontier pickups, including ties; optional later wrong-age pickups remain possible.
The note says Save and Continue, not just move between zones. No item permission/placement is
changed. Actual seed 8 CLI replay: 287 placements and all 129 RomFS resources byte-identical to
the played seed, with 10 warning rows (including Mido middle-left Bow, child-first, sphere 1).
The precise get-text and strict physical matching-age fill alternatives/costs are proposals
only in the round file, awaiting Kareem/co-owner.

## 38. Round 9: Temple Sheik and free time travel (cs9b)

Build e0f3ccfa; read-only native placement/flows/GameData and twelve supplied save snapshots.
Reproducer and full evidence: `plans/rounds/r9-sheik.md`, external
`E:/OOTRemake/work/r9-sheik-cs9b/probe.py` and `probe.log`. No agent game run.

Temple Sheik is adult Market Static actor **2669233513522124871**, group
**6012439728933042438** (`Market_Adult_Prefab_7f43`). Its NPC Logic_Delete reads
saved Bool **Market_Adult_GetLightPrelude**, not the medal or Minuet. Prelude's separate
area/request group **17364055337479607892** (`Market_Adult_Prefab_edc2`) ANDs player
contact with **SageOfForest_IsCompleted_Exp**; the area is present until that Bool is set.
The expression compares **Step_SageOfForest** with **Complete**, NOT medal inventory.

Request `Market_Adult_Field_GetLightPrelude` maps to that entry in **AllSage**. Its
Event169/170 -> Event73 -> Event39 -> Event37 transitions to **Dm_MelodyGet_Shine**,
whose Event53 grants **Item_Melody_LightPrelude** and Event46 sets the completion Bool,
removing Sheik and the trigger. AllSage Event34 rolls its quest to Step01_01 afterwards.
The Forest blue-warp chain separately sets Forest Complete in Event199 (section 16).
Shuffled medals would not change those native quest gates; no reward-policy change here.

The adult-first backup's manual01/autosave04 are adult/ForestStep01, no medal or Prelude.
The after-forest backup spans Step06_2(01/02), Step09(03), Complete with medal but no
Prelude/completion(04/05), then Complete with medal/Prelude/completion(00). Thus medal
ownership precedes the scene that actually deletes Sheik, corroborating Kareem's room-entry
observation. The remaining adult-first slots are older child/Ready saves.

The existing free-travel patch opens only the pedestal (section 16), leaving that blocking
NPC alive. The isolated extension gates only this placed NPC's Presence on the same Forest
completion expression: absent before Forest, present for the original scene afterwards;
native deletion remains. Native Market uses BoolExp Presence on distant cloud actors already.
No global NPC removal, relocation, premature song, quest-completion or saved-default edit.
**Kareem: test the isolated pre-Forest return/second pull and post-Forest Prelude checklist
in the round file; runtime success is not established by these native-data observations.**

`patch/age.py` now validates both groups before mutation and emits that Presence plus the
original ungated pedestal binding. The native adult Banc is **30540 -> 30664** bytes;
allocation **30824 -> 30952**. Independent inverse-tree and saved-gate checks pass; the
two unrun isolated save-copy launchers and checklist are under the external `ingame/` folder.
The sourced `remake/sheik.toml` corrects the translated Prelude medal rule to adult Forest
completion (`Defeat Phantom Ganon`, the age-return abstraction), regardless of free travel.
No scene trigger or gift-grant behavior is replaced.

### Seed-specific Hookshot directions

The native NPC talk flow selects **Talk_01** and **Talk_03** before Hookshot ownership
(`IsGet.Item_Hookshot`); both previously directed the player to its vanilla area. Every seed
now replaces both through `patch/text`, independently of Gossip Stone mode and free travel.
It names an actual Hookshot placement using the player-facing catalogue; with multiple copies,
the lexicographically first readable location is deterministic. A slice without Hookshot uses
a Clawshot-authored neutral line with no tool/location claim. English in all 16 archives (D26),
existing opening style, two-row/page wrapping and native highlight/reset helpers. All other
NPC messages and the original talk flow remain unchanged; transforms compose with stone/House
hints rather than overwriting their archives.

Actual seed 7 Chest+Gift/free-travel CLI: **212 shuffled checks, 24 spheres, 124 resources**.
Readback found both lines in all 16 archives name its real **Ganon's Castle Light Trial
Triforce Tile Chest** Hookshot. All 40 stone texts survive; Prelude's native completion
write is unchanged despite its normal shuffled gift. Synthetic boundaries and all-language
inverse archive oracle pass. Full-gate evidence and remaining human acceptance are in the round file.

## 39. Round 9: private seed packs and pause-map floors (cs9c)

Build `e0f3ccfa`, read-only dump; implementation/check evidence: `plans/rounds/r9-seedpack.md`.
The repository and source-containing packs remain private to invited testers.

### Source-only seed packs

`python -m clawshot.pack` snapshots the generator's source/data and frozen dependency metadata,
generates an external reference seed from that snapshot, and records only its whole-output SHA256.
No game resource, generated overlay, decoded data, spoiler, save or plan is in the zip.
Testers generate against their own dump; both Make and Play require exact output digest equality.

RomFS has no NSO build-ID header. The supported-dump preflight hashes four known existing resources
(`Pack/ZsDic.pack.zs`, GameDataList, EventSetting, child Kokiri Dynamic Banc), then hashes their lowercase
hex digests with LF separators. This identifies the known build's RomFS before uv/generation; it is not
an executable build-ID read or a whole-dump checksum. Changes elsewhere that affect the output fail the
independent reference digest. Only the signature and output digest are distributed, not file content.

Play uses only `<Hookshot>/bin/hookshot.exe`, `HOOKSHOT_NO_UPDATE_CHECK=1`, the verified overlay
and a per-pack `--user` folder. Missing bin or wrong digest stops before launching. Existing seed
folders are never rebuilt in place. The agent does not run Play, a batch or the game.


### Dungeon floors

The source is `Banc/BancBasedResource/MapParam.byml.zs`, not a height estimate or an N64 room label.
For each dungeon, `Room[Dynamic.DefaultDungeonRoomIndex].Floor` contains signed logical floors:
0 is 1F, 1 is 2F, -1 is B1. The global `Floor` array starts at `MinFloor`; its `TBox.InstanceID` values
identify each chest's exact floor. Prefer that exact Hash join when a room spans multiple floors.
An icon-matched chest need not have an explicit room override (Forest Boss Key is one).

`location_names.toml` now has `floor` metadata on **143 checks**: 134 chests, 8 native boss pickups,
and the Ice Cavern Sheik lesson sharing the Iron Boots chest room. The complete catalogue has 369
descriptions. 126 chest floors come from exact map icons; 8 Ganon trial checks absent from those lists
use their single-valued physical room floor. Boss pickups use `BossRoomId` and its room floor;
Volvagia's native pickup lacks a Dynamic override, so no fake room 0 default is introduced.
The reader exposes `floor`, renders it in the same name used by spoiler, play note and location hints,
and retains world keys, physical identities, rules and exclusions. Three redundant hard-coded Deku
name prefixes were removed so the structured floor is not displayed twice in a check's label.

Fire Temple has 16 chest icons and 5 Skulltula/CollectSign icons, matching Kareem's guide-map count.
Chest floors are 1F five, 2F one, 3F six, 4F none, 5F four. The timed trio (both extra red-rupee chests
included) and Hammer are 5F; the cracked-floor shortcut cell is 2F. Map texture filenames independently
agree with the signed labels (Deku B2..3F, Well B2/B1, Jabu B1..2F, Fire 1F..5F).
GTG and the castle interior retain stored floor metadata but lack a corresponding dungeon-floor
texture set; their labels are not a claim of a newly observed pause-menu floor view.

The native dump oracle checks every floor-bearing description against map icons/physical rooms,
including basement offsets and tall-room distinctions. Actual seed 8 CLI output has 142 shuffled
floor labels (the held Well check stays held), unchanged placements and chronological spheres,
and the same 131 output paths. Only spoiler/note, 16 language hint archives and the common size table
change. Proof/check commands and remaining player comparison are in `r9-seedpack.md`; no game was run.

The earlier exact-r8-full pack proof is branch-local. Each future pack computes a fresh digest from
its own shipped source; merged Sheik text/floor labels legitimately change that digest. Claude rebuilds
the private pack after merges. Kareem's reported Lichii LayeredFS result is documented in the tester
guides with save-slot backup/New Game warnings; Ryujinx and Atmosphere layouts remain untested.

## 40. Round 10: gift checks (cs10a)

Build e0f3ccfa; native traces, checks and player checklists: `plans/rounds/r10-gifts.md`.
External decoded data and outputs stay under `E:/OOTRemake/work/r10-gifts-cs10a/`.

### Released frogs

Kareem confirmed the complete seven-check experiment (`answers.md` R8-FROGS, 2026-11-09).
Round 10 removes the holds and fixes each of the five song pool contributions at OoTR's
`Rupees (20)`, per the round spec. Their census actor fields stay empty: native rewards
still vary 5/10/15/20/30 by prior song count. Shuffled callers always use their specialized
grant, even when assigned 20 again; unshuffled behavior stays native. Storms and bug-game
first/retry wins retain their two independent heart checks and native saved completion.
No new flag, growth change or repeat reward change. Actual Chest+Gift seed 7 builds all
seven into 218 shuffled checks/28 spheres; focused persisted-state and pool tests pass.

### Market Potion Shop bottle tutorial

The actual child merchant is 020, not the tentative 046 in R9-SEED8-MARKET. Existing census
`Npc_Hylia_020_Shop_Child/Event171` now groups as remake-only `Market Potion Shop Bottle`.
Fixed logic adds its free empty Bottle as child at the existing daytime Potion Shop region.
The default AISchedule selects the offer without an item, fee or quest gate. Acceptance grants
the bottle; native saved Present/Started/Cleared Bools record the tutorial. None is item ownership.
The subsequent bug-capture path consumes selected bottle contents and refills with Red Potion.

A changed reward retains the offer/refusal, bypasses bottle-only staging/capture/consumption,
grants through the native generic wrapper, then sets those existing completion flags and
completes the tutorial quest. Completed entry visits route to unchanged shopping. Native same-
Bottle and unshuffled tutorials stay unchanged. The swap remains held under D15 until Kareem
tests the isolated backup-copy launcher/checklist in the round file. No save-layout growth.

### Deterministic bowling and gallery tiers

Gift/NPC shuffle dispatches native bowling First Prize on win 1, Second Prize on win 2,
then the existing red-rupee filler. Native opening (Dodongo quest), rental, fee, failures,
count and difficulty remain. The second grant also writes the native third/heart-marker
completion Bool. No extra shuffled/fixed Bombchu payout or phantom Bomb item in this mode.
Unshuffled routing remains native.

The two ownership-dependent grants of each supported upgrade now normalize to fixed native
medium tiers: Bomb Bag 30, Bullet Bag 40, Quiver 40 (`PouchActorInfo.AfterExpansionMaxNum`).
Bomb Bag 30 supplies the bag ability; bullet bags and quivers do not supply rental weapon
ownership. Their native normal-win saved flags remain; both normal galleries join Gift.

Native expert modes repeat 30/70 rupees (`Event202`/`Event599`) after the normal reward,
without first-win state or a literal item actor. Kareem selected fixed Rupees (20) for each
first-expert pool item (2026-11-09, via Claude). Census records these variable native calls
honestly; two remake-only checks use the normal-clear prerequisite and one D22 saved Bool each:
`Clawshot.Gift.MiniGame_HitTarget.Event202` (Hash 1800298829) and `.Event599` (Hash 2333016720),
default false/reset8/save0. Only Event445/449's expert branch gets the new query; false grants
the assignment through `GetInEvent_NotTurn_NotNpc`, then saves completion and rejoins native
post-reward talk without opening the rupee UI. True uses the original expert talk/UI/call/close
path, unchanged 30/70. Normal wins/failures do not consume expert state; same 20 assignments
still specialize. Both checks remain D15-held pending Kareem's isolated test. No existing
output was rebuilt; new `gallery-expert-next`, two users/launchers and `expert-check.md`.

### Dampé digging event check

Active `.110` Event628, already in the raw census, is the real pouch grant through
`GetInEvent_NotTurn_NotNpc_Dampe`; native Event82 staging and Event301 cleanup are preserved.
Linked it to the existing digging check and moved its unchanged child/night/Time Flows rule
into gift overrides, typed NPC, held under D15 pending the isolated test.
The saved native completion Bool is `GraveYard_DiggingHoleTour_Drop_HeartPiece`
(Hash 3037888117, false/reset8/save0). Main routes read it, but the shortcut can structurally
reenter the grant. A completion query now guards only the reward branch at Event449's fork,
and Event628 writes completion immediately after its grant. The parallel native cleanup
still runs on both paths. No new saved flag, floor-major actor, lottery or fee change.
Actual writer/inverse/serialized once-and-cleanup proofs and player checklist are in the round file.

### Market finalization correction after Kareem's re-entry crash

The old bypass gave Boomerang but omitted native post-catch Insect_Delete and
Shop_Bottle_Insect_Appeared, plus Wait/schedule-select/arrival-reset actions. The copied
save has Present/Started/Cleared true and Boomerang stock 1, but both missing flags false;
this matches the observed remaining bug/frightened merchant. The corrected path reproduces
all five native final-state flags and those three native actions before quest completion,
without bottle removal/refill. Exact FATAL native callee is not established.
Kareem confirms the Bug ->Empty content difference was his own release, not the bypass:
native IsValid bits show exactlyone bottle both before/after, no extra bottle or potion.
New `market-bottle-fix-next` and fresh isolated profile only; old output/evidence untouched.
Shuffle remains held until re-entry/talk/Save-Continue succeeds (round file/checklist).

### Round 11: release of the two tested gifts (cs11e)

Kareem confirmed the corrected bottle checklist (`answers.md` R10-MARKET-BOTTLE-FIX,
2026-11-10): decline/accept, bug removed, relaxed merchant, re-entry/talk/shopping,
Save and Continue, unchanged bottles. It supersedes R10-MARKET-BOTTLE's re-entry crash.
R10-DIGGING confirms Boomerang from the displayed heart prize, saved completion and normal
later digs; Save and Continue was not reported for digging. Both logs name the tested mod flow.

Released only `Market Potion Shop Bottle` and `Graveyard Dampe Gravedigging Tour` under D15.
Before removing the holds, the current common writer's Boomerang flows matched the tested
mods byte-for-byte, compressed and decompressed; the real Gift setup closure matches too.
No patch code changed. Detailed paths, SHA256s, sizes and verification: `rounds/r11-release.md`.
With Gift, the bottle is a pool item rather than a guaranteed early fixed bottle; without
Gift, section 40's free child bottle/access model remains. Existing names/directions and
random/item/Way of the Hero hints cover both locations.

Expert galleries, merchant experiments and unreleased Skulltula House rewards stay held.
Kareem subsequently confirmed the two bowling prizes (Storms, Epona, then red-rupee filler)
and child gallery (Echo Gem, then red rupee), R10-MINIGAMES-CHILD-JABU; together with
R10-MINIGAMES-ADULT this accepts both normal galleries. Bowling still advertises its
original prize. Save and Continue between wins was not reported. Experts remain untested.

## 41. Round 10: age travel and Door of Time (cs10b)

Build `e0f3ccfa`; native read-only probes and exact evidence: `plans/rounds/r10-agetravel.md`,
`E:/OOTRemake/work/r10-agetravel-cs10b/`. Kareem confirmed round 9's pre-Forest return and
post-Forest Prelude, but reported a missing Sheik in the first adult arrival (answers R9-FIRST-PULL).

First arrival runs `Dm_TimeTemple_0050` **then** `Dm_TimeTemple_0055` (AllSage Event9/Event0).
Both need placed Temple Sheik. Free travel now uses a non-saved BoolExp for his Presence:
**not HavePlayedEvent.Dm_TimeTemple_0055 or SageOfForest_IsCompleted_Exp**. Waiting for 0055
preserves dialogue after 0050's timeline; native Prelude completion still deletes him afterwards.
The new expression is reset0/save-1; no saved layout/default or native expression changes.
Native postfix 0=Bool, 10=BoolExp, 5=NOT, 4=OR; Mido/door predicates supply precedents.

The timeline has no item/quest/GameData writes. Dialogue 0055's Ready/Event252 sets
`HrlField_HasEnteredFirstTime_Adult`; Event137 increments Notes NPC-talk count. AllSage's
following chain sets the first-adult/Navi shield-history flags and SageOfLight Complete,
AllSage Step01 and Forest Step01. The broken-scene user's adult saves retain both event
histories, HrlField true and those quest steps; no missing item grant or save repair inferred.

Actual standalone writer emits adult Banc, GameData and size table. Exact inverse-tree,
byte-order, non-saved-expression and allocation checks pass. New isolated child-autosave
launcher/checklist is in the round report. **First-scene visibility/dialogue and immediate
return after it still require Kareem; no agent game run.** Free travel remains default-off.

### Door modes and instrument ages

D35's `door_of_time` is closed (default), song_only or open; reverse travel is independent.
Closed is the unchanged native patch path. Song-only changes the altar's non-saved invalid
expression from `Step_DoorOfTime != Step05 or opened` to `opened`, and bypasses DoorOfTime
Event60's after-Step04 query. The opening entry additionally requires the learned Time song;
native ocarina input, recommended melody, opened/history checks, scene, saved opened flag
and Step06 progression remain. Either child ocarina can play; no stone quest is completed.

Open changes the exact native `Logic/Market_Common_f252.logic.module.ainb` threshold literal
Step06 to Ready, with NUL padding and unchanged bytes/offsets/length elsewhere. Native
is-after/is-equal outputs then open the gate without advancing a quest. Independent external
AINB decoding shows exactly one changed field (node 8's ChallengeStepName); no GPL implementation
is copied. The common module also displays the altar stones when open; these are visual actors,
not inventory grants. The child pedestal reuses the existing ungated attention module and
first-pull request; native Draw still selects first-arrival or repeat travel from scene history.
All native scenes, stone grants/quests, adult return and Prelude stay separate.

The earlier door exposes an existing logic mismatch: translated `can_play` allowed Fairy
Ocarina as adult. **Source is the item-bar/PouchTable age metadata audited in section 37,
NOT an in-game Fairy-as-adult test.** Fairy is child-only there; Time is both-age.
Sourced helper overrides apply in EVERY door mode, requiring Ocarina2 for adult song use.
The return kit's data-defined mandatory inventory/staged families follow each door mode:
early pulls cannot assume optional child Saria, strength or Time ocarina. D20's actual
first-pull proof remains strict; no silent free-travel/guarantee override or retry increase.

## 42. Round 10: NUP input for source-only seed packs (cs10c)

Implementation, exact commands/results and review boundary: `plans/rounds/r10-nup.md`.
The player's original NUP and extracted RomFS are read-only; all local output is outside the repo.

`python -m clawshot.pack --romfs` / `OOT_ROMFS` and Make's dump-path answer accept either a
RomFS directory or full `.nup` filename. The generator itself retains its ordinary directory API.
The reader is [a55uka/nup](https://github.com/a55uka/nup) at
`a4840f06c94ddeb414eea5b33c9704ffe995f11c`, MIT; reader/format modules and the complete licence
are vendored and attributed in `NOTICE`. PyPI's unrelated `nup` package is not used.

Preflight reads the same four supported-version resources directly inside the newest complete
base/update RomFS. Add-ons are not selected; ambiguous/incomplete/unsupported newer packages
never borrow or fall back to older content. Upstream TOC/bounds checks precede tree indexing;
every resource read verifies its actual SHA256 against its NUP record. No filename or display
version is trusted as the supported-build oracle. Folder and NUP fingerprints must agree.

Kareem's read-only NUP is 25,020,741,061 bytes, one standalone update 131072 with 186,592 file
records and 601 directories. Its fingerprint is the existing supported signature
`fc09c4af707a0ca092188cf014f6fdf3d40514def773f097b798f52f9f28bc93`.
The initial 1,239 selected generator inputs / 25,821,037 bytes compare byte-identical with his
extracted RomFS. The later data-defined cache also includes Track B's Door of Time input
`Logic/Market_Common_f252.logic.module.ainb`; all its other named inputs are already covered.
The working set excludes ExeFS/models/textures/audio, not a full 25GB extraction.

NUP Make bootstraps frozen uv/Python/zstd for input preflight, then saves configuration and
creates a unique pack-local `.romfs-*` cache only after version success. Folder preflight remains
before uv. Cache removal occurs on normal completion or exception; force-killed remnants, like
the generated seed, remain private game data. The positive ZIP allowlist includes source/licences
only, never cache/seed resources. Existing seeds are verified, not overwritten; emulator Make
still needs no Hookshot, and Play's bin-only/isolated-save safeguards are unchanged.

Cache selection lives in one data definition, `src/clawshot/pack/resources.toml`: exact paths,
family patterns, supported item/shop actor-pack template and fast-start component discovery.
The optional `OOT_NUP` + `OOT_ROMFS` dump oracle generates AND writes complete seeds from the
cache directory alone for every enabled shuffle kind and resource-reading setting; an independent
full-RomFS run must produce exactly the same output paths and byte digests. Missing file errors
name the RomFS resource; silent missing glob members fail output equality. Forest modes, all
fast starts, free travel, songs/prices/partial shops, mask mode and (once the setting exists)
all three Door of Time modes are covered. Re-run after each integration/rebase.

Synthetic fixtures contain invented bytes only. The native oracle also compares cached bytes
and preserves NUP size/mtime. Actual publisher/PowerShell Make and observed matrix/gate results
are recorded in the round file; no game or launcher is run by the agent.

## 43. Round 10: pots, crates and ground rupees (cs10d, exploration)

Read-only native dump/build `e0f3ccfa`; full per-area counts, evidence, commands and
acceptance boundary: `plans/rounds/r10-pots.md`. Reproducers and decoded/native resources
stay under `E:/OOTRemake/work/r10-pots-cs10d/`, never in this repository.

The non-DreamWorld census finds 530 ordinary pot Hashes, 50 breakable-crate Hashes and 112
ordinary ground rupees (81 green, 25 blue, 4 red, 2 purple; 170 age copies). These are placement
identities, not 530/50 once-only logical checks. Pots/crates at the same physical site
usually have distinct child/adult Hashes. The `_Dream` pot variant also appears 12 times
in the ordinary Ganondorf room, outside the excluded DreamWorld directory.

Ordinary pots inherit the resource-supply DropParam. `Dynamic.Drop__DropActor` and
`Drop__DropTable` are native instance String128 selectors; `Drop__DropTableOverWrite`
is not instance-settable. Pot selectors: 101 actor-only, 250 table-only, 2 both, 177 neither.
The default and before-boss tables choose resources conditionally/probabilistically;
some explicitly spawn multiple objects. They are not one fixed N64 vanilla pool item.
The 50 crates are 38 `Obj_BrokenBox_A_01`, 6 `_03`, 1 `_02`, 5 `_06`; the last two variants
have no ordinary DropRef. Puzzle/movable crates, flying/archery/spinning/skull pots,
scenery, silver puzzles, diving rupees, shop displays and event representations stay out.

All 499 flagged pots and 44 flagged crates use reset88/save0, not permanent reset24.
Thirty-one pots and 6 crates lack a Bool64bitKey under their placement Hash. The 112
ordinary ground rupees are reset24/save0, native DropItem/NoRespawn. Three Deku Tree
rupees nevertheless have scrub-completion Presence gates; two lake rupees have native
AI bindings. A saved Hash is not a certificate of an ungated region or a generic grant.

The inspected pot/common-breakable AI requests object death, while DropItem handles
pickup physics/rotation. No explicit collected-spawned-drop identity channel was found
there; the engine death/drop component has not been reverse-engineered. **[INFERENCE]**
Retiring the pot on destruction can lose an uncollected shuffled item; renewing a supply
pot can duplicate an upgrade. Changing reset88 to 24 would not solve collection tracking.

The conservative candidate destination palette is the existing D27/D33 five native
pickups: Heart Container, Piece of Heart, Deku Shield, Hylian Shield and red 20-rupee pickup.
Existing floor/boss observations do not certify these as pot drops or every floor surface.
Piece-of-Heart-specific pickup AI makes its generated-drop persistence an explicit test.
Inventory-only major actors and the known-crashing Fire Arrows are not inferred safe.

**Reviewed scope (Claude, Round 10): no Pot or Rupee seed switch this round.** Four isolated
experiments under `work/r10-pots-cs10d/ingame/`, each a new `-next` overlay with copied
approved save launcher and a separate user:

- Reset88 supply pot 15406610986108637956 in the child House of Twins -> Piece of Heart.
- No-placement-Hash-save Forest 2F Bow-room pot 18069611988256927347 -> Piece of Heart.
  Its intact native room graph requires empty arrows, the ordinary partner pot dead,
  no arrow bundle nearby, camera/player clearance and 1200-frame delay. It also has an
  AutogenGameData destruction latch: absent placement Hash does **not** mean no native state.
- Child-only Kokiri training-enclosure blue rupee 16647730239269178270 -> Piece of Heart.
- East Hyrule Field bomb-grotto blue rupee 5620885265123329978 -> Hylian Shield, both ages.

`ingame/checklist.md` specifies source save/slot, directions, required overlay logs,
actual inventory/counter checks, area return and Save/Continue. Both pot experiments
also have independent `-uncollected` test users for drop-loss/recovery/duplicate checks.
`check_saves.py` reads only these isolated users. Native groups/flags/respawn graphs,
positions and identities remain unchanged; the Forest target's old arrow table becomes
native `None` alongside its explicit replacement drop. No game/launcher was run by the agent.

Actual common-writer readback/inverse-tree/allocation proof passes for all four outputs;
an independent interpreter reproduces their bytes and verifies the exact permitted
resource-entry deltas. Source-backup SHA256 maps remain unchanged. This is data proof,
not a gameplay result. **Kareem: run the four experiments and separate pot recovery paths;
report the grant, repeat/change/loss after returns and Save/Continue, with overlay logs.**

MIT OoT Randomizer 526b4c8d has 341 non-MQ Pot, 74 Crate, 6 SmallCrate and 155 Freestanding
rows (not 155 rupees). Counts, ages, geometry and vanilla rewards differ materially.
Future checks use **remake names and the actual region's access rule**, like `extra_*`
chests; record an N64 name only for an exact mapping. No ordinal/nearest-position join,
unverified rule, new saved flag or shuffle setting is introduced by this exploration.

## 44. Round 11: dungeon items and keysanity (cs11b, exploration)

Build `e0f3ccfa`; evidence and exact native addresses: `plans/rounds/r11-keys.md`.
Read-only reproducers, decoded graphs, save audit and native disassembly stay under
`E:/OOTRemake/work/r11-keys-cs11b/`, never in this repository.

`GameDataList`'s `DungeonInfo` Struct selects 14 dungeon Structs; `DungeonParam.TargetGameData`
matches the selecting child keys. Each has saved reset8/file0 leaves:
`SmallKeyNum` (remaining Int), `SmallKeyTotalNum` (acquired-total Int),
`IsGetSmallKeyOnce`, `IsGetBossKey`, `IsGetMap`, `IsGetCompass` (Bools).
All start 0/false. These exist even for keyless dungeons; Kokiri's field rows have no
TargetGameData. Names and flattened save hashes were checked against the actual Struct links.

The four generic item actors carry no dungeon name. Chest special-item actions
`GameSystemActor.EventGetDungeonSmallKey/BossKey/Map/Compass` take no dungeon argument.
Their native handlers resolve a shared live component, not an argument selected by Clawshot's
fill. Positive small-key grants update remaining, total and first-key state; spending decreases
remaining only, with an underflow check. Boss/map/compass handlers set the component's Bools.
`DoorChainLock.root` reads its remaining count and spends through the same native access path;
durable door-open state is independently indexed by controller identity in `IsChainLockDoorOpen`.

**Played small-key attribution (Kareem, 2026-11-10):** a generic overworld key is lost;
inside keyless Deku or keyed Fire it credits the standing dungeon. Named Forest writes from
child/adult overworld small chests reach Forest, and the native Forest lock spends that key.
The named big-chest redirect failed before opening; neither these experiments nor the fill's
`anywhere` option establish production-wide keysanity. Boss/map/compass handler targeting
remains static evidence, not acceptance of those shuffled named items.

### Collection-state correction and historical test audit

Section 6's old blanket chest claim is superseded, not erased. Native `TreasureBox.module`
reads/writes `IsTreasureBoxOpen`, indexed by `QueryGenericGetInstanceId.InstanceIDString`.
The Struct child key is murmur3 of the **decimal actor Hash**, and its Value selects the saved
Bool whose full name is `IsTreasureBoxOpen.<Hash>` (reset24/file0). The same unchanged Hash
still identifies the check; `Save.is_set(Hash)` is not its open-state accessor.

| Audited actor/state family | Collection/state contract; evidence boundary |
|---|---|
| Ordinary chests | Named `IsTreasureBoxOpen.<Hash>` Bool. Late Forest save has these true while the raw chest Hashes are false; the native graph confirms the reader/writer. |
| Treasure Chest Game first prize | Its native flow also gates first clear on named `MiniGame_ChoiceTreasure_IsClear`; an unset raw prize Hash is not proof it is unclaimed. |
| Ordinary placed ground rupees, recovery floor hearts, anchored floor Heart Pieces, boss hearts | Native saved placement-Hash Bool64 list, with NoRespawn/reset24/file0 contracts audited in rounds 7–10 (`r7-drops`, `r8-freestanding`, `r10-pots`). Round 2's actual saves show recovery hearts/rupees and Gohma's heart by raw Hash; the ranch backup still has Gohma's heart Hash set. Replacement callbacks and persistence remain per-experiment acceptance, not certified by table presence. Boss creation/story gates can coexist (Gohma's additional obtained Bool is documented in section 27). |
| Gold Skulltulas | Raw enemy Hash plus token-related Hash±2 in the observed round 2 saves; special token collection callback still matters (sections 22/27). |
| Saved ordinary supply pots/crates | Raw reset88 destruction state, not permanent item collection; some respawn/scripted variants have no such entry. See section 43. |
| Scripted floor small keys, fortress keys, Ocarina/letter actors | Not covered by a universal raw-Hash rule; level/event-specific state (section 36). Dungeon inventory itself uses the named DungeonInfo leaves above. |
| Small-key locks | Named `IsChainLockDoorOpen` Struct indexed by the controller ID; separate from both inventory and a pickup's Hash. |

Historical **unopened-chest save premises** found by auditing `plans/rounds/`:

| Earlier record | Raw-Hash premise / corrected disposition |
|---|---|
| `r5-gifts.md:227–234`, `chest-song-storms-kak` | Ranch manual01 target 12902291359202819102 reads raw=false **but named open=true**. Its raw-based selection was invalid. Section 19's “In game” already records replacing that follow-up with new-game `chest-ocarina-storms` because the ranch chest was open. The fresh named read corroborates that history; no new game rerun is needed and no observed song success is retracted. No output/user was rewritten. |
| `r7-gifts.md:87–109`, `treasure-red` | `build_treasure.py:16` asserts raw prize 16881481538337649070 unset. The same original ranch manual01 now reads named open=false AND native first-clear=false; the named first-clear condition was already checked by that builder. Raw evidence is redundant, not its once-only proof. |
| `r10-agetravel.md:165–168`, three controlled child door tests | `build_player_doors.py:19–22` selected a Graveyard chest using `not Save.is_set(Hash)`. Claude rechecked chosen 9622128545943056087 in main-Jabu manual01: named open=false, Mido named-open true controls. **Accepted reviewer evidence; not rerun here.** Those tests stand. |

`r2-census.md:466–470` had already explicitly warned that opened chests were absent from the raw
list; the unresolved location is now explained by the named Struct. `r1-formats.md:164–166`
only asks for a new game/an unopened save (no raw-Hash audit claim). `r6-settings.md:52–57`
and `r8-getitem.md:88–113` use new games, not an old raw-Hash source selection. Metadata-only
raw-entry counts in `r1-research`, `r2-census` and `r8-freestanding` do **not** establish
unopened chests. No other unopened-chest raw-Hash save premise was found in the round-file audit.

### In game (Kareem via Claude, 2026-11-10)

Exact player quotations, save slots and backup/log references are recorded as
R11-KEY-OVERWORLD, R11-KEY-NAMED-FOREST, R11-KEY-KEYLESS, R11-KEY-DOOR,
R11-KEY-FIRE and R11-KEY-NAMED-BIGCHEST in `playtest/answers.md`.
Counts below are remaining/acquired-total; first-key means `IsGetSmallKeyOnce`.

| Case | Observed result / saved state | Evidence |
|---|---|---|
| Plain key, overworld small chest | Chest open; remaining/total/first-key unchanged in all 14 dungeons: key lost. | Mido, 12:35/12:36; R11-KEY-OVERWORLD |
| Plain key, keyless dungeon big chest | Deku 0/0/false→1/1/true; map false, all 13 other dungeons unchanged. No indicator popup. | Deku map chest, 13:10/13:11; R11-KEY-KEYLESS |
| Plain key, keyed dungeon non-key big chest | Fire 0/7→1/8; chest open; all 13 other dungeons unchanged. Both map displays increment; persists after reload. | Hammer chest, 14:16/14:17; R11-KEY-FIRE |
| Named key, overworld small chest (child/adult) | Child Forest 0/0/false→1/1/true; adult likewise 1/1/true after Goron chest. Generic text does not identify Forest. | Mido 12:41 and Goron 13:29; R11-KEY-NAMED-FOREST / DOOR |
| Named key used on native door | Forest 1/1 after Goron; 1/2 after the door and native tree key: one spent, native key subsequently counted; only Forest changed across 14. | Door opened, 13:27–13:33; R11-KEY-DOOR |
| Named key, big chest inside another dungeon | **Failed:** prompt appears but chest does not open; no grant. Source Forest/Deku 0/0/false, map false; no post-pickup attribution result. | Rewired Deku row/cloned big entry, 14:02–14:04; R11-KEY-NAMED-BIGCHEST |

**Display correction:** Kareem's own Fire game with the map and 2 keys showed
"Map only shows Fire Temple, can't switch, 2 Small Keys shown next to the map screen and by
the map on the game UI." Keys have a **standing current-dungeon display**, beside both
the on-screen map and pause map; no other-dungeon selector. The door run had no Forest map.
The earlier pickup-only interpretation is withdrawn; **[INFERENCE]** map ownership gates
the display, not separately tested. Per-dungeon counts belong in the UI's Tracker tab,
reading the **seed's own save** (D38), not a new in-game roster.

### Experiments and seed-output boundary

Own-dungeon plain-key attribution now has played evidence for both chest sizes, including
a keyed dungeon/reload. The named prototype credits the existing Forest leaves and is
spendable, but is **not registered in generation**. The failed big-chest binding does not
show that generic big chests cannot grant keys: Deku and Fire are positive controls.
Its entry lookup, native preload, cloned topology and allocation check out statically;
**[INFERENCE, medium confidence]** bypassing native player participation/EventTransition
caused startup rejection; the exact guard is unknown. No data-only pass is gameplay proof.

`anywhere` still needs **(1)** a working named big-chest path and the cross-dungeon pickup
test, **(2)** pickup text naming the target dungeon (English in every language; native
English dungeon names read from the dump at generation, never shipped), **(3)** the Tracker.
Arbitrary per-source binding and other named dungeon-item families are not certified here.
`patch.check_dungeon_items` still refuses `dungeon_items="anywhere"` before dump access in
both CLI and `patch.make_seed`; its existing explanatory message is unchanged by this
docs-only results update. Settings/CS1 and pure fill's synthetic anywhere mode remain intact.

## 45. Round 11: Hookshot 2.0.12+ seed loading and text icons (cs11c)

R11-HOOKSHOT-2012 is Kareem/Claude's observed crash diagnosis, not an agent game run.
Read-only evidence: `work/save-backups/2026-11-10_0905-r10-tests-crash-on-start/`.
`bootcheck-A-overlay-crash.log:67–68,87–101` loads the overlay size table, selects Xbox
icons, then crashes reading guest 0 with the External font path on the stack.
`bootcheck-B-mods-ok.log:4–5,69,87,96` discovers one mod, loads its table, logs the game's
own icons fallback and reaches the isolated save mount. No crash was reproduced here.

### Pack cutover

Play removes HOS_FS_OVERLAY from its child environment and sets HOS_MODS to the extracted
pack root. `seed/romfs` stays where Make wrote it: no copies, moves or links. The pack root
is not a mod; the seed child is. Discovery descends at most 4 levels, ignores names starting
`.`, `-` or `_`, and stops at a folder containing romfs/exefs. Hidden `.romfs-*` NUP caches
cannot become mods. Play rejects a second discoverable mod, missing seed RomFS or traversed
link before creating a user/log. The existing whole-seed digest remains mandatory.

The shared read-only API is `clawshot.pack.hookshot.detect(folder) -> HookshotInfo`:
folder, expected bin executable, optional version, optional RomFS, sorted adjacent NUPs,
mods-support Boolean and refusal reason (empty when supported). Version labels are not
capability evidence: inspect only the binary's HOS_MODS marker without executing it.
Diagnostic wording is irrelevant. Builds without mod loading refuse, never fall back to
overlay or the folder-root launcher. Play requires a Hookshot that can load mods (tested
on 2.0.13). Make for emulators still needs no Hookshot. `play --dry-run` / CLAWSHOT_DRY_RUN=1 performs the same
checks and prints overrides plus explicit environment removals without starting anything.

Empty HOS_FS_OVERLAY is not equivalent to removal: a native no-game C-runtime probe
returned a non-null empty string. Hookshot's filesystem branch tests only that pointer.
The child environment therefore omits it entirely, even when inherited.

### Why icons fall back; upstream candidate (report only)

GPL-3.0 release source was read for facts only, never copied. Paths below are relative to
`C:/Users/hi/AppData/Local/HookshotBuilder/versions/v2.0.13/HookshotBuilder/tools/`:

- `host/mods.c:116–147,181–203`: discovery rules; indexed mod wins over prompt resources;
  the font fallback can query whether a mod has a resource table.
- `host/prompts.c:469–495,498–519`: any mod resource table disables the generated External
  font; Hookshot's own prompt table is served only when no mod supplies that path.
- `nx2/prompt_assets.py:86–111,952–957`: Hookshot's vanilla-derived table increases the
  External font allocation for its larger controller-specific fonts.
- `host/nn_fs.c:279–289`: filesystem overlays can replace a resolved path without the
  mod index knowing about them, explaining the mismatch in the supplied crash log.

Every seed needs its own table for grown resources. Do not delete it or substitute
Hookshot's vanilla-derived prompt table: that would discard the seed's other allocations.
Current supported cosmetic cost is the game's own Switch button icons in text; controls
are unchanged. Manual mods use the main save folder: New Game overwrites that playthrough,
unlike pack Play's isolated user folder. Player steps/warnings: `docs/seed-pack.md`.

**[INFERENCE] Candidate upstream PR:** before serving the effective winning mod table,
compose a private runtime copy that raises only the External font entry to at least the
installed prompt-font requirement. Preserve an already-larger entry, every unrelated
hashed/named entry and metadata. Then generated icons can stay enabled when no mod replaces
the font itself. Cache against the winning table's content and required font allocation.
Never mutate installed mods, dump or generated seed bytes; their digests must remain valid.
Keep native fallback for mod-provided fonts, malformed/unknown tables or a failed merge.
An overlay table must likewise be accounted for before using larger fonts, not guessed safe.

Upstream verification would need synthetic table-preservation/priority/malformed cases,
custom-font and already-large-allocation cases, then Claude's isolated headless boot and
Kareem's in-game icon/placement/save checks. None of this proposed Hookshot behavior was
implemented, built, booted or submitted by this track. Exact pack smoke/gate results and
remaining player acceptance are recorded in `plans/rounds/r11-loader.md`.

## 46. Round 14: child story and field music

Track C, issues #21/#22; supported build `e0f3ccfa`. Full trace, commands and Longshot
acceptance checklist: `rounds/r14-story.md`. Research and decoded files:
`E:/OOTRemake/work/r14-story/`; native dump read-only. No agent game run.

### Zelda's escape and the moat checks

The three Spiritual Stones in inventory are **not sufficient**. Native `RSDB/Challenge`
row `DoorOfTime` depends on `Goto_HyruleCastle_IsCompleted_Exp`. The courtyard completes
that quest and initializes `DoorOfTime=Step01` (`Goto_HyruleCastle` Event30/Event32);
Impa's lesson/send-off continues it to Step02. Its stone-quest checks advance Step03.
The missing visit cannot be replaced merely by finding a shuffled ocarina or song.

`DoorOfTime_CheckStoneNum` is called by `Dm_SY_BancChange_EscapeDungeon` Event49
(after Fire completion) and Event78 (after Water completion). Its Event38/Event39
BoolExp switches use **case0=true**: both Fire and Water quests Complete lead to Event37
(Step03), Event77 (`IsHyruleFieldBridgeClose=true`), then count0. One completed quest
gives Step2_1/Step2_2 and count1; neither gives count2, without advancing. The count is
**remaining** stones, not owned stones. Forest is not independently queried by this
two-quest check; the existing all-three-stones logic is retained conservatively.

The bridge's raised/lowered actors have opposite Presence predicates on
`IsHyruleFieldBridgeClose` (Hashes `13633262183050288401` / `10233645194156655880`).
This saved flag is distinct from the Step03 escape sensor. The escape flow clears it,
sets noon and advances Step04. A raised bridge alone therefore does not establish the
correct quest step or that the escape has run.

At the field side of the Market drawbridge, native
`HyruleField_Child_Prefab_0ce5` node3 tests **exactly DoorOfTime Step03**; its equality
output creates Area Hash `5374506228817442823`, at approximately (-0.6,149.4,49.3).
Player contact requests `HyruleField_DoorOfTime_Escape` through actor
`7081083777168801859`. No clock/day/night predicate appears in this request graph.
`HyruleField_Child_Prefab_9e35` separately enables the storm area at the same step.
After escape, `_91f9` node0 requires **exactly Step04** to create the moat's
`Obj_Ocarina_Time_A_01` (Hash `2802436684568022035`); its pickup requests
`HyruleField_DoorOfTime_GetOcarinaOfTime`, leading to `Dm_MelodyGet_Time` and both rewards.
`_32f7` is the distinct **AreaOut recovery**, not the initial escape: Step04, escape
history played and outside the moat sensor areas.

Fresh native AINB decoding with the external, unmodified GPL `ainb` research tool
matched the historical `_0ce5` and `_91f9` JSON byte-for-byte. Only facts are used here;
no GPL implementation or native decoded tree is included in Clawshot.

**Logic cutover:** persistent `Met Child Zelda` at `HC Garden Skippable Locations`,
child only, models the **complete courtyard/Impa lesson and accepted send-off through
DoorOfTime Step02**, not first courtyard contact. Both moat checks and the **closed** Door
of Time require it; `Time Flows` derives from that visit. The existing route remains:
Malon's fixed Weird Egg / hatch Chicken, wake Talon, pass the guards, meet Zelda and finish
Impa's send-off. Zelda's Letter remains native (D31), not an extra shuffled inventory gate.
OoT Randomizer at pinned commit
`526b4c8d81b7c4023ef4573ffbaf39344e270d5b`, `Overworld.json:1379,1402–1403`,
already gates HC Garden on Weird Egg or Chicken and puts Letter/Impa behind it;
`Overworld.json:491–492` instead gives the moat only the stones. The overrides correct
that remake difference without modifying translated source.

Closed Door of Time retains the native altar/flow quest gates: altar at Step05,
`DoorOfTime_OpenDoor` Event60 requires `DoorOfTime_IsAfter_Step04_Exp`, then the melody
and once-only door checks. Song-only/open deliberately bypass those native quest gates
(section41), so they do **not** inherit `Met Child Zelda`; the moat always does.

The closed-door return-kit construction therefore includes the compulsory story event.
The independent first-pull oracle also caps **declared acquired events**, not just item-table
entries, to retain only history required on every child pull route. `Met Child Zelda` is not
an item-table entry and cannot be reconstructed by revisiting its child source after pulling.
Song-only/open bounds still assume no optional Zelda visit; optional events fail the same
mandatory-count test and are not carried into the proof (r14-story full-gate diagnosis).

**Saria's Song uses the same completed sequence.** Track E's native AINB census
(`E:/OOTRemake/work/r14-steps/ainb/FINDINGS.md`, Track C evidence) identifies
`SacredForestMeadow_Child_Prefab_3265` node0: Saria Create requires
`DoorOfTime_IsAfter_Step01_Exp`. `_bbc3` nodes3/5 require that predicate AND unplayed
`Dm_MelodyGet_Saria` for the song-request area. Reprinting all three graphs confirmed
the actual consumers. `Step01_Npc_Hylia_Impa_Child_Talk` unconditionally starts the lesson;
its after-lesson talk Event124 accepts a field transfer with boot event
`HyruleField_DoorOfTime_SendOff`. EventSetting binds that to `DoorOfTime_SendOff`:
Event65 → Event10 (`Dm_HrlField_0020`) → Event91 → **Event7 (Step02)** → Event62.
There is no additional stone/inventory check in this send-off chain. Accepting the
available interaction is part of completing the courtyard route. `Song from Saria`
therefore requires `Met Child Zelda`, not a remote song or mere garden reach; translated
OoTR files remain untouched, with the correction in `child_sacred_forest_meadow.toml`.

**Market Bombchu Shop entrance correction.** `_0c76` node1 tests
`Get_StoneOfFire_IsCompleted_Exp`; node0 ANDs it with node2 Night and feeds door node3
EnableOpen. EnableDo also requires completion. E's Banc census finds the shopkeeper
Presence uses the same completion predicate. All eight native shop checks already
require `Defeat King Dodongo` via `shops.toml` availability; the interior has no other
checks/events and its only exit returns to the back alley. Thus no currently offered
check bypassed the boss, but the region/route was falsely reachable. Its override now
requires the same boss event **and** night/`Time Flows`; no shelf or pool change.

This establishes a missing logic dependency, **not the cause of TheTerribleFairy's
particular raised-bridge save**: version, seed, settings and story history remain unknown.
Kareem has not yet played the staged before/after story control on Longshot.

### Kaepora skip and field BGM

Native source: `Pack/Bootup.Nin_Ounce_NVN2.pack.zs`, member
`Sound/Bgm/Game/BGMGeneralParam/BGMGeneralParam_Default.game__sound__BGMGeneralParam.bgyml`,
table `SequenceRangeDisableBgm`. Two pre-panorama suppression intervals end at
GameData hash **3546103570 = `HavePlayedEvent.Dm_HrlField_0000`**:

- Property 1651218793 begins at `HavePlayedEvent.Dm_Kokiri_0155` (forest-bridge farewell).
- Property 17622586 begins at `Get_StoneOfForest_IsAfter_DefeatBoss_Exp`.

The old skip marked only field `_0010` played and advanced the castle quest to Step02.
That prevents the native owl request (and therefore its `_0000` panorama) while leaving
the BGM interval's end flag false. The first panorama itself starts its cutscene BGM;
`Goto_HyruleCastle` Event161 later requests the regular `BGM_HyruleField`. Scenery
`Sound/Scenery/HyruleField.game__sound__SceneryParam.bgyml` in the same Bootup pack
selects that regular theme. This is not a missing stone, song or castle quest requirement.

The field theme's C1 start-condition reference header uses **Global15 = 1651218793**,
alongside globals10/5/7 and local4; its stop header uses globals10/5/7. The separate
interval starting at `_0000` (Global16, property3996766055, unresolved end Bool1517061892)
is **not referenced by these field predicates**. A research-only header inventory checks
length/alignment/property bounds for all **122** native root start/stop conditions;
it is not a bytecode evaluator or engine run. Of 827 historical slots, 303 ordinary
post-owl saves have `_0000=true`, `_0010=true`, **1517061892=false**; 524 have all three
false. No anonymous flag is changed to “close” that unrelated interval.

Repair: **only with `kaepora`, initialize `HavePlayedEvent.Dm_HrlField_0000=true`** as
the skipped panorama normally would. Native metadata: saved Bool, default false,
reset bits8, save-file0. Existing `_0010`, Lost Woods history, UI flag and Step02 remain.
No `_0005` history, other story flag, inventory, audio resource or quest completion is
added. The generic `patch/gamedata.py` writer already applies and validates this new
TOML value; it needs no code change or new NUP working-set resource.

**Recovery distinction:** the flag is saved, so reloading alone cannot release this
interval. A Market visit does not play the suppressed first-field panorama; the native
request remains disabled. Night is not a reliable “music fixed” check: the regular field
theme's native stop condition explicitly includes Night. Those are static state/data
deductions, not observed recovery tests of Zarcos's save. Kareem's Longshot checklist
checks daytime first, Market return and Save/Continue separately. This new-game default
does not migrate an existing save's false history flag.

Before-fix regression printed `_0000=false` after the skip transform. After the repair,
focused synthetic and native writer/exact GameData oracles: **4 passed**. The actual
public before-fix app generation also wrote `_0000=false`, `_0005=false`, `_0010=true`.
Full gate/matrix evidence and the public after output are recorded in the round file.
**Built, not yet played in game.**
