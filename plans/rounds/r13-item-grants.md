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

## Decisions and trade-slot fix

**Approved by Claude, 2026-11-12:** hold the seven movable adult trade gifts vanilla, in addition
to D31's Egg/Letter hold. Claude will add the decision to `decisions.md` at merge. The final
Biggoron sword reward remains shuffled behind the native Claim Check. Version remains unchanged.

Native evidence and reproducible probes: external `trade/REPORT.md`. Each trade actor has its own
saved `IsGet` and `PouchData.<actor>.StockNum`; they do **not** overwrite one shared save field.
All fourteen nevertheless share UI cell `Pa_ItemIcon_23`, whose variant order puts the eleven adult
items before Letter, Cucco and Egg. Native picker `0x00a6ef20` chooses the first owned variant.
Its child branch accepts child OR adult variants; its adult branch accepts adult variants only
(the age-byte interpretation is a strong inference cross-checked against native age readers and
266 existing saves). Thus an adult trade item can hide a child's Cucco without preventing hatching.
Talon's actor accepts the **shown** AlarmCucco item; `Dm_HrlCastle_0020` then consumes it and sets
`Talon_AfterWakeUp`. Reload recomputes the same ownership-based cell and cannot repair that problem.

Clawshot never places `Weapon_Sword_BrokenGiant` (the actual Broken Giant's Knife equipment).
**[INFERENCE]** the reporter meant `Item_BrokenSword` (Broken Goron Sword, the adult trade item).
The independent finding that `adult_trade_shuffle=false` assumed the native hand-in chain while
Gift moved its intermediate items is another reason the old placement was unsound.

### Residual early-adult ordering gap

**Yes, it remains possible with native trades:** Anju's `Npc_Hylia_049_Adult/Event264` Pocket Egg
grant has no child `Talon_AfterWakeUp` prerequisite; early adult/free-return modes can therefore
create the same hidden-Cucco situation. Following Claude's explicit 2026-11-12 option, this track
uses a **plain README/play-note/pack warning**, not a fabricated native gate: wake child Talon and
show Zelda's Letter to the Kakariko guard **before taking Anju's adult Pocket Egg**. Do not promise
that finishing the adult chain clears the slot: the inspected final Biggoron flows have no explicit
Claim Check removal (`trade/claim_consumption.py`). The warning does not rewrite existing seeds.

Other affected child use: the guard's ShowItem ZeldaLetter route consumes the Letter at
`Npc_Hylia_Soldier_003/Event57`; a hidden Letter can therefore block that interaction too.
Masks are **not** in the trade cell: native `PouchTable` puts ordinary masks in
`EquipmentArray/Pa_HeadEquip_02`, SpecialDeal `Mask`, and Amiibo masks in `Pa_HeadEquip_03`.
Mask merchant/guard flows test equipped `Armor_Child_Mask_*`, not a trade variant. An adult trade
item does not directly replace a held mask; the unfinished Letter/guard interaction can delay
the mask quest. External `trade/residual_order.py` independently prints these native cells,
guard consumption, Anju gates and mask-equipment queries. Pre-fix saves retain the
Save-and-Continue recovery advice; new-game prevention was accepted below.

## New-game-only item-bar initialization

External lead provenance: `E:/OOTRemake/work/rounds/r13/kamil-hookshot-randomized-findings.txt`
(Kamil, 2026-11-12), facts/ideas only. No external randomizer implementation was read or copied.
Native verification: `Sequence/Opening` calls `SetPouchAndStatusForGameStart`, unlike load-save;
the latter already pushes the wallet and tunics using `SeqOneShotPushToPouch`. Its native vtable
at `0x04bb5908` resolves the push execute slot to `0x0110d370`, which forwards literal actor/Num
parameters to native pouch addition. Small Nut Bag declares capacity 20 without a full-stock
grant; Nuts are an assignable both-age native item.

`patch/start_items.py` adds one ordered Sequential branch: `Item_NutBag_Small x1`, **then**
`Item_DekuNut x0`. No free nut ammunition, changed item age permission, saved default or existing-save
migration. The branch runs once in new-game setup, not once per frame or on load. Every original
node/parameter/command retains its semantic identity; only the root's added child and necessary
absolute offsets change. The supported native input is fingerprinted; unknown/already patched
inputs are refused rather than heuristically edited. This is our own narrow binary splice,
derived from native v0x408 records, not a vendored AINB implementation.

Independent external oracle: the unmodified research-only GPL `ainb` decoder already installed
under `work/r4-fast-start/.venv` was used only outside the repository. `oracle_sequence.py`
compares fresh original/patched decodes: all 17 old nodes except root child membership and every
other section unchanged; three new nodes are the Sequential branch and the two exact pushes.
Initial oracle failures exposed duplicate empty-string interning and boolean property layout;
the printed native values determined the fixes. The final oracle passes, including native
`IsUpdateNextInFrame=true`. Synthetic tests are authored graphs, never decoded game fixtures.

Size: native **5916 -> 6957** bytes; allocation **6296 -> 7352**. The per-file formula is rounded32
plus 376, matching this native module; 107 of 108 native Sequence files have that overhead
(one has 392). No unverified generic AINB formula. The NUP working-set catalogue includes this
new input. All public seed paths register the transform, independently of intro/fast-start settings.

**Player-accepted for new games, 2026-11-12.** The Bow-first/Boomerang check below passed;
this does not modify existing saves or individually certify every age-locked item family.

### Staged player check (Claude boot-checks; Kareem plays)

One launcher: `E:/OOTRemake/work/r13-item-grants/ingame/Test - item-bar first Bow.bat`,
copied/adapted from `E:/OOTRemake/tools/test-launcher-template.bat` with CRLF. Empty isolated
user; choose **New Game**, no existing thumbnail. **6–9 minutes**. Its checklist requires:
initial Nuts 0/20; Mido middle-left Bow **first**, middle-right Boomerang next; throw Boomerang
before reload; far-left native nut bundle gives 3/20 and works; Save/Continue retains everything.
The new saved thumbnail is described as outside Mido's house, never by slot number.

Generated by public `make_seed`/`write_seed`, real whole-world search, seed 8, default Chest settings,
using existing test-only `excluded_items` to pin those two rewards before fill. **29 spheres,
78 resources**, no post-fill placement/resource edits. Reproducer `stage_itembar.py` and
`itembar-staging-proof.json` record settings plus script and Sequence hashes. A plain CS1 recipe
does not include these experiment-only pins. The earlier 137-resource CLI smoke in the external
`itembar-first-bow-next` folder is **not** the player test (its early item is Hookshot).

Launcher dry run prints the bin executable, isolated user and exactly-one-mod HOS_MODS path;
no game started. Claude must obtain `mods: Sequence/SetPouchAndStatusForGameStart.module.ainb <- ...`
and the Kokiri placement loading line before player acceptance. No second launcher for trade,
bombs or capacity: native evidence settles the former policy/gates; castle's capacity PR is held.
Claude reported **ib13 boot check passed**, 2026-11-12: 490 log lines, this mod's
`SetPouchAndStatusForGameStart` loaded, no crash. He handed the check to Kareem with a save
watcher on its isolated user.

**Kareem run 2 PASS, 2026-11-12, 08:47–08:52 (reported by Claude).** Runtime loaded
`SetPouchAndStatusForGameStart` from this mod; child throughout, no crash. New save owns
Nut Bag and Deku Nuts, capacity 20, stock 0. Bow was collected first with nuts still 0,
then Boomerang: Kareem threw it immediately, before any reload, and said it "worked great".
The native nut chest then gave 3 nuts; using one left 2. Snapshots:
`save-backups/2026-11-12_08*-r13-itembar-run2-1..8`.
Run 1 (`user-...-run1-nuts-first`) opened the nuts first and **does not count** as the
first-Bow check. The played user folder is unchanged; no rename needed.
Claude approved removing the new-seed item-bar known issue while retaining recovery advice
for saves started with older builds. README, settings/UI/Discord docs, generated play note and
packaged readme now make that distinction. Version unchanged; release version remains Claude's call.


## Bomb purchase and tier audit status

Native `DisplayShop` applies an item-specific ordinary-bomb gate through
`Get_StoneOfFire_IsCompleted_Exp` (Event327; other display/sold-out routes also inspected).
Only the Market Bazaar's native bomb shelf has a corresponding shelf-release gate; putting
that requirement on every shelf would incorrectly block non-bomb shuffled replacements.
Current Buy Bombs items are inert refills in logic, not Bomb Bag/explosives progression sources;
no ungated purchase is used to prove beatability. Bombchus do not share this ordinary-bomb gate.
Full per-path identifiers and the 100-seed sweep will be appended from the independent audit.

Native lower-after-higher capacity proof: `AfterExpansionMaxNum` is row field +0xc0; the grant
reads current capacity and skips expansion/refill when current >= offered at
`0x0110f704..0x0110f708`. Wallets and all five bag/quiver families therefore do not downgrade.
Strength differs: LiftGradeUP directly writes the offered grade at `0x011103c0`, and DiveDepthUP
directly writes the offered scale depth at `0x01110480`, without comparing the old value.
Claude therefore requires higher strength/scale placements **unreachable without every lower
tier**, not merely a later earliest sphere; only then is a MAX level model sound.

Hookshot is monotone: `plans/playtest/answers.md` R8-FROGS (2026-11-09) records a late Hookshot
not replacing the Longshot, reaffirmed by Kareem to Claude on 2026-11-12. Ocarinas are separate
slots (Kareem to Claude, 2026-11-12): no lower-item overwrite. Neither family gets a fill restriction.
The complete alias-family table, MAX fix, prerequisite proof, historical/0.2.0 sweeps and
community 11/15 results remain in progress, in a separate commit from this item-bar/trade fix.

## Verification so far

- Independent original/patched native Sequence decoder oracle: pass.
- Public full CLI generation: seed 8, Chest+Shop+Gift+Scrub+BossHeart, 293 shuffled checks,
  24 spheres, 137 resources; actual native writer/search smoke, not a game run.
- Controlled public generation: 29 spheres / 78 resources, as above.
- Template launcher `CLAWSHOT_DRY_RUN=1`: pass; no game started.
- Focused ruff check: pass. Focused synthetic/native regressions: **15 passed**, 20 deselected
  (`tests/test_start_items.py`, new adult-trade tests). Full serialized gates still pending.
