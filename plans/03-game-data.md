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
- Gold Skulltulas: the count per area matches, but Kareem reports they are not in the same places as on N64, so
  token logic is built from the remake's positions, not ported per token. He also expects the Skulltula House
  reward table to differ; the flow reads rewards at 10, 20, 30, 40 and 50 tokens (section 4, example 3), to
  compare with what he has seen.

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
