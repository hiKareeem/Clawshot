# Round 11, Track B: keysanity exploration (cs11b)

Branch `r11/keys`. Read supplied AGENTS, README, plans00–04, decisions, Round11 opening/shared-file rules and round9/10 reports. Dump and save backups are read-only. No game, launcher, window, Hookshot build, terminal-control command, merge, push or stash. No dependency change. Research, decoded data and experiments live only at `E:/OOTRemake/work/r11-keys-cs11b/`. Commands are serial; pytest uses `CLAWSHOT_WORKERS=1`. Full suites/sweeps acquire `E:/OOTRemake/work/rounds/r11/gate.lock`, wait60s on contention, and release immediately on exit.

## Item 1: native state and grant trace

Build `e0f3ccfa`. Executed read-only `probe.py`, `contracts.py`, `native_trace.py`, `final_contracts.py` and `select_saves.py`. Their JSON/disassembly remains external. Native addresses below refer to the player's own `.hookshot_exefs/main`, not Hookshot source. Ephemeral permissive Capstone via `uv run --with capstone`; existing external unmodified AINB decoder used only to decode native graphs. No GPL code or NX2navi code/docs read/copied.

### Saved state

`GameData/GameDataList.Product.110.byml.zs` has a non-saved `DungeonInfo` Struct whose children select14 dungeon Structs. `RSDB/DungeonParam.Product.111.rstbl.byml.zs` `TargetGameData` matches those child keys. Each dungeon has these existing, independent leaves (all reset8/save0, so stored in `slot_NN/progress.sav`):

| Full named leaf under `DungeonInfo.<area>.` | Type / native default | Native member hash |
|---|---|---|
| `SmallKeyNum` | Int /0 | `0x1af87831` |
| `SmallKeyTotalNum` | Int /0 | `0x642f7364` |
| `IsGetSmallKeyOnce` | Bool /false | `0x251d4c2a` |
| `IsGetBossKey` | Bool /false | `0x5fb83617` |
| `IsGetMap` | Bool /false | `0x58aeb8fb` |
| `IsGetCompass` | Bool /false | `0xc7692e3f` |

Areas: `InsideTheDekuTree`, `DodongoCavern`, `InsideJabuJabuBelly`, `ForestTemple`, `FireTemple`, `IceCavern`, `WaterTemple`, `BottomOfTheWell`, `ShadowTemple`, `SpiritTemple`, `GerudoTrainingGround`, `InsideGanonCastle`, `FinalBattleField`, `GerudoFortress` (the last is selected by row `GerudoFortress_Adult`). Even keyless dungeons have these leaves. Kokiri rows are `IsFieldData=true` with **no TargetGameData**. Exact per-dungeon hashes are retained in `state-catalog.json`; these are not global `PouchData.Item_Dungeon_SmallKey.StockNum` counts.

### Native grant/read contracts

- All dungeons share the four actors `Item_Dungeon_SmallKey`, `Item_Dungeon_BossKey`, `Item_Dungeon_Map`, `Item_Dungeon_Compass`. No dungeon argument is carried in those names. Pouch rows: small key `PouchSpecialDeal=SmallKey`; other three `NotPushToPouch`.
- `Dm_SY_Treasurebox` dispatches special chest contents to `GameSystemActor.EventGetDungeonMap` (Event23), `...Compass` (Event26), `...BossKey` (Event27), `...SmallKey` (Event30). Their only explicit parameter is `IsWaitEnd=true`; **no target dungeon parameter**. The small-chest/shared-grant paths are retained in external `chest-contracts.json`.
- Native `OneShotDungeonGetSmallKey` execute `0x028cb390` resolves the same live component via `0x00b2af20` / `0x00b2afc0`, then calls `0x03283160` with +1. That routine reads `SmallKeyNum`, sets `IsGetSmallKeyOnce` when the current count is zero, increments `SmallKeyTotalNum` for positive grants, then changes `SmallKeyNum`. Its negative branch refuses underflow and does not decrease the total. `OneShotDungeonUseSmallKey` execute `0x028cbd20` passes -1 to that same routine.
- Boss/map/compass execute `0x028cae10` / `0x028cb1c0` / `0x028caff0` use that same live component and set its `IsGetBossKey` / `IsGetMap` / `IsGetCompass` via `0x032830e0` / `0x03282fe0` / `0x03283060`. Boss also requests native display state; these are not per-dungeon named-argument APIs.
- `DoorChainLock.root` node3 reads `QueryDungeonGetSmallKeyNum` (no inputs); node18 uses `OneShotDungeonUseSmallKey` (no inputs). The open state is separate: `IsChainLockDoorOpen` Struct indexed by the controller InstanceID string, not the key pickup Hash. Query execute `0x029ebb10` resolves the same component and reads the remaining count. The counterpart boss-key query `0x029ebd70` resolves it and reads the boss flag. This establishes count consumption and native flag readers, not an in-game opening result.
- **[INFERENCE]** Shared component selection plus DungeonParam's target mapping means the generic pickup credits the loaded dungeon, not the fill's intended dungeon. Kokiri has no target: whether the native path silently loses the item, retains an earlier target, or behaves otherwise is **not established** by this static trace. The explicit item2 experiments distinguish these outcomes. No claim of keysanity working follows from settings/fill support.

### Save evidence and diagnostics

All24 slots of four candidate backups were read, not edited. Early ranch manual01 is child, Deku map/compass owned, Deku remaining/total0 and Forest remaining/total0. Adult-first manual01 is adult, no Hookshot/Minuet, Forest remaining/total0. After-Forest manual01 has Forest boss/map/compass true, remaining0/total5/once true, Fire remaining/total0. This independently corroborates **separate remaining and acquired-total counters**, not a controlled before/after key pickup.

First scratch hash probe passed bytes to `save.key`, which requires str: printed AttributeError and source signature; decoded before hashing, then the aimed run succeeded. Initial total-name guess `TotalGetSmallKeyNum` had no matching saved row; printed native member `0x642f7364` and Struct values instead of treating it as absent. Candidate-name hash proof identifies actual `SmallKeyTotalNum`; `IsGetSmallKeyOnce` likewise matches its member. No game result inferred. A trace-helper insertion was caught in the edit response, read back and moved before execution. Python references request: no language server available.

## Coordination / provisional choices

- Required shared edits will be isolated: early refusal in `patch.make_seed` and the public CLI; **no fill, Settings, CS1 or synthetic-anywhere removal**. TrackD can expose the setting but must surface generation refusal. TrackA README text requested: “Dungeon items remain own-dungeon. Anywhere is encoded for research but seed generation refuses it until named-dungeon grants pass in-game tests.” TrackC's pack generation inherits the same pipeline guard.
- Experiments will preserve native actors/Hash/age copies and use the current template's real-folder one-mod layout; no existing output will be rebuilt. Named-grant prototype is experimental only and will not be registered in seed generation.
- **Kareem: which counter changes after each controlled generic pickup, and can a named Forest grant from outside Forest open a Forest lock after Save/Continue?** The precise launchers/checklists and artifact proof follow in item order. No production success is claimed before your result.
