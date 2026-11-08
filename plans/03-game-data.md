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
definitions still require the Kokiri Sword unless Mido is skipped. Found-shield helper semantics are the shop
track's shared normalization and must be checked after it lands on main.

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
OoT Randomizer's `HC Garden` asks `Weird_Egg or Chicken`), the Gerudo guards (`GerudoFortress_Common_35d7`,
`IsGet.Item_Token_Gerudo`), the windmill's Song of Storms spot (`KakarikoVillage_Adult_Common_7d34`), Mido's blocker
(`KokiriForest_Npc_Kokiri_Blocker_Surprised_BoolExp`: Kokiri Sword and Deku Shield). Lines that change with an item
(Kokiri children on Saria's Song, Zoras on the scales, Navi's heat hint) are left as they are.

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
| Hideout Gerudo Membership Card | `Dm_Gerudo_0025` Event294 | `Item_Token_Gerudo` | the cutscene plays once | item gate kept: logic module `GerudoFortress_Common_35d7` (`IsGet.Item_Token_Gerudo`: guards send Link to the cell without it) | 1 |  |
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
