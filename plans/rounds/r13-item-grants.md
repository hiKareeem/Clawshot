# R13 item grants (cs13b)

Base: `30ba5c9`, version 0.2.0, unpublished. No version bump. Player reports are ground truth;
no game was started. Dump/build e0f3ccfa is read-only. Research and generated artifacts belong under
`E:/OOTRemake/work/r13-item-grants/`, never this repository.

## Capacity implementation hold

Claude's 2026-11-12 steer: castle is preparing the capacity PR. **Do not implement a competing fix.**
No capacity implementation has been written in this worktree. Review that PR against the following
native contract when Claude supplies it. This audit distinguishes native declarations, explicit flow
operations, and behavior that still needs the game; a metadata row alone is not gameplay proof.

## Native capacity and expected regression values

Fresh read-only probes: `probe_grants.py`, `pack_probe.py`, `companion_refs.py`, `chest_trace.py` under
the external research directory. Native source: `RSDB/PouchActorInfo.Product.111.rstbl.byml.zs`,
actor packs' `GameParameter/ExpansionMaxNumActor/*`, and active event-flow versions selected through
`EventFlowFileEntry.Product.110.byml.zs`.

`ExpansionMaxNumActor` identifies the counted actor(s); `AfterExpansionMaxNum` identifies capacity.
`IsItemStockMaxIfGet` is a native refill declaration, not a quantity invented by Clawshot. Ownership
is the canonical pouch actor's `IsGet` / `PouchData.<actor>.StockNum`, not the get-window history.

| Item / native actor | Native ownership / capacity target | Native capacity | Native stock declaration; expected regression value |
|---|---|---:|---|
| Slingshot / `Item_Range_SlingShot` | Canonical equipment `Weapon_Range_SlingShot`; weapon row itself has **no capacity expansion** | None from weapon row | First grant must also establish `Item_BulletBag_Small`, seed capacity/stock **30/30**, not 0/0 |
| Bullet Bag Small / Medium / Large | `Item_BulletBag_{Small,Medium,Large}`; `Item_DekuSeed`, `PouchContentMaxNum.DekuSeed` | 30 / 40 / 50 | All declare `IsItemStockMaxIfGet=true`: **30/30, 40/40, 50/50** on first corresponding bag grant |
| Bomb Bag Small / Medium / Large | `Item_BombBag_{Small,Medium,Large}`; `Item_Bomb` **and** `Item_Bombchu`, common `PouchContentMaxNum.Bomb` | 20 / 30 / 40 | All declare full stock. Ordinary bombs **20/20, 30/30, 40/40**; `ActorFullOnlyIfIsGetWhenGetBag=Item_Bombchu`: do **not** grant new Bombchu ownership just to fill an unowned Bombchu stack |
| Bow / `Item_Range_Bow` | Canonical equipment `Weapon_Range_Bow`; weapon row itself has **no capacity expansion** | None from weapon row | First grant must also establish `Item_Quiver_Small`, arrow capacity/stock **30/30**, not 0/0 |
| Quiver Small / Medium / Large | `Item_Quiver_{Small,Medium,Large}`; `Item_Arrow_Normal`, `PouchContentMaxNum.Arrow` | 30 / 40 / 50 | All declare full stock: **30/30, 40/40, 50/50**. A quiver alone is not Bow ownership |
| Stick Bag Small / Medium / Large | `Item_StickBag_{Small,Medium,Large}`; `Item_DekuStick`, `PouchContentMaxNum.DekuStick` | 10 / 20 / 30 | Small has no full-stock declaration; Medium/Large declare full stock: **20/20, 30/30**. Small capacity alone must not fabricate sticks |
| Nut Bag Small / Medium / Large | `Item_NutBag_{Small,Medium,Large}`; `Item_DekuNut`, `PouchContentMaxNum.DekuNut` | 20 / 30 / 40 | Small has no full-stock declaration; Medium/Large declare full stock: **30/30, 40/40**. Small capacity alone must not fabricate nuts |
| Wallet Small / Medium / Large | `Item_Wallet_{Small,Medium,Large}`; `Obj_Rupee_Green`, `PouchContentMaxNum.Rupee` | 200 / 500 / 1000 | No full-stock declaration: capacity changes, existing rupees preserved; do not award 200/500/1000 rupees |

Actual current pool includes base Slingshot/Bow/Bomb Bag, fixed Medium Bomb Bag/Bullet Bag/Quiver
minigame prizes, fixed Medium scrub Stick/Nut capacity, and both larger wallets. Native Large tiers
also occur in ownership-dependent native branches; documenting them does not admit new pool items.

### Grant-path comparison

| Grant path | Native operation / source | What current Clawshot changes | Capacity/ammo consequence and review obligation |
|---|---|---|---|
| Physical native item get | `Dm_SY_Get:PouchAddItem`: Event38 sets own name, Event40 opens get window, Event39 calls `PouchContentGuestPerformer.EventTriggerGetFirstExpansionMaxNumActor`, Event35 adds own actor | Ordinary item identities/metadata retained | Explicit native first-container operation exists; weapon ownership alone is insufficient. Match this companion contract rather than just setting `HavePlayedGetEvent` |
| Chest, big and small | `Dm_SY_Treasurebox/Event90` and `Dm_SY_TreasureboxSmall/Event23` call `GetPouchContentByActorNameForTreasureBox`; shared Event0 adds named actor with `Num=1`, direct equip false, message target true, `IsGetEvent=true` | `Drop__DropActor` and substitute actor; unsafe sword story wrapper removal; key-only bindings are separate | Bag actors retain their expansion/refill rows. Weapon companion handling is native get-event behavior, not an explicit bag write in our chest patch. Do not claim a new chest gameplay pass from the flow alone |
| Shop shelf | Native `DisplayShop` / `Dm_SY_ShopGet` purchase, ownership/stock/payment checks | Native shop display palette, seller GoodsList, prices and shelf identity | **No Slingshot/Bow/Bag major-item shelf admission.** Report A cannot be a shuffled shelf with current published policy. Shop ammo remains a refill, not weapon ownership; preserve native capacity/payment refusal |
| Kokiri shopkeeper gift | `Npc_Kokiri_001_Shop_Child/Event116,117` -> native hand-over wrappers | Both reward actor parameters, once-only flag and extended availability window | `--shuffle Gift` enables `KF Shopkeeper Gift`. A weapon row has no bag field; report A establishes **Slingshot 0/0 on this path**. Require weapon **and** native small bag/capacity/ammo, with no extra shield |
| NPC hand-over / generic gift | `Dm_SY_GetInEvent` named grants Event124 and Event442 use `IsGetEvent=false`; Event430 uses true; ordinary `GetPouchContentByActorName` supplies false | Gift reward string plus documented once/state rewrites; no explicit capacity companion | Same missing-companion risk for ranged weapons through non-get-event named grants. Bag items still carry their own expansion metadata. Cover every actual positive grant, not only one wrapper or one shopkeeper branch |
| Direct event gift | `PouchSystemActor.EventTriggerAddOrRemovePouchContent` on the source flow, with a literal actor | Literal reward actor; native flags/consumption preserved | Must audit the direct path too; a shared-wrapper-only fix can miss it. Negative trade consumption must never gain capacity/ammo |
| One-time scrub | `Enemy_Scrub_Business_Common` fixed sale calls -> `Dm_SY_GetInEvent:GetInEvent_NotTurn_2DShop` | All native tier alternatives normalized to the pool actor, price/selection edits, success flags retained | Apply ranged companion fix on the successful grant only. Existing Medium Stick/Nut actors already declare full stock. Cancel/shortfall must grant nothing |
| Freestanding / boss heart | Actual native pickup actor (`Gyaml`) and its native performer | Native floor palette only: Heart Container, Heart Piece, Deku/Hylian Shield, red rupee | No ranged weapon, bag, wallet or capacity item can be placed here. No capacity rewrite needed or justified; retain rejection of unsupported majors |

Expected regression cases for castle's PR: first Slingshot and Bow at both shopkeeper branches,
ordinary shared gift, direct gift and scrub success; base chest paths unchanged; each actual bag tier's
capacity/refill declaration preserved; quiver/bullet upgrade acquired before weapon is not downgraded
or gratuitously refilled by later weapon; unrelated item and negative/removal grants unchanged;
failed/cancelled purchases grant nothing; the original reward's message/once flag remains correct.
These are **expected values**, not unrun test results or new in-game acceptance.

## Other investigations in progress

- Bomb strength gate and 100-seed historical-settings sweep: independent audit running.
- Native child/adult trade cells, egg transition and Save/Continue note: independent audit running.
- New-game-only nut-slot prevention and all native bomb-shop purchase gates: added by Claude's steer.

External lead provenance: `E:/OOTRemake/work/rounds/r13/kamil-hookshot-randomized-findings.txt`
(Kamil, 2026-11-12), facts/ideas only; no external randomizer implementation read or copied.
Section 1's proposed new-game pushes and section 4's bomb shop gates require independent native
verification. Section 5's optional bomb LiftGrade change and chest-bomb bag behavior are record-only;
no optional bomb gameplay patch is authorized in this track.
