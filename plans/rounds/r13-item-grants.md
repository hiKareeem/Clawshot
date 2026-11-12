# R13 item grants (cs13b)

Base: `30ba5c9`, version 0.2.0, unpublished. No version bump. Player reports are ground truth;
the agent did not start the game. Dump/build e0f3ccfa is read-only. Research and generated artifacts belong under
`E:/OOTRemake/work/r13-item-grants/`, never this repository.

## Capacity integration decisions

Initial steer reserved the capacity implementation for castle. Claude subsequently approved cherry-picking
`be71d73` with castle's authorship, then separate commits for ordered wiring and missing paths. The cherry-pick
retains `-x`; `c1156dd` wires it after named-key compilation. Our extension covers the three direct
`Dm_SY_GetInEvent` grants and literal positive source gifts. `6ea2122` (D-pad) remains out: it shares the
fast-start/gamedata loader with cs13a. The audit below separates native declarations from gameplay proof.

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

### Grant-path comparison before the capacity fix

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

### Applied capacity coverage and data smoke

Castle's claim that all grants pass through `GetPouchContent/Event0` is too broad. Native
`Dm_SY_GetInEvent` directly adds at **Event124** (`GetInEvent_Goron`, also the Zelda-letter entry),
**Event430** (`GetInEvent_NotTurn_2DShop`) and **Event442** (`DekuShield_GetAndEquipCheck`).
All three now use the same missing-container guard. Cloned positive grants in that shared flow are
included. Literal source gifts are guarded after their reward/once edits; common flows have one owner
and are guarded after the key compiler. `NpcCommon` has only a negative pouch add (`Event489`, -1);
scanning it made byte-identical output. No shelf/floor major-item admission was added.

Native hand-over read/write/read and gate execution passed for all three original IDs: 783 → 876 events,
exactly one missing small bag before the requested item; larger owned bags skip the companion.
Original quantities, message, equip and get-event flags survive; the companion cannot equip or replace
the displayed reward. Synthetic purchase failure/cancel and literal once/removal/zero/bag-only boundaries
pass. Combined bag/key/gift/scrub regressions: **62 passed**. An in-memory reversed registration order
makes the public named-key regression fail at the expected literal-grant rejection; the real order passes.
These are data/model proofs, not an in-game pass.

One extra literal-source edge was reproduced before its fix: with native
`IsSetMessageTargetActorName=false`, a dynamic scratch-string gate overwrote the existing UI target.
The retained regression failed with the exact old/new values, then passed after literal actors selected
their family at compile time. Their guard now uses only pouch-tier queries and the missing-bag add,
without a GameData actor, message mutation or dead runtime family comparisons.

The section-24 stick/nut automatic-bag inference is corrected in `03-game-data.md`: player reports
override metadata-based assumptions. New-game Nut Bag x1 / Nuts x0 still composes without free nuts.

### Staged first-container check

Public `gifts.seed_setup` → `make_seed` → `write_seed`, seed 8 with existing test-only fill exclusions:
**24 spheres, 122 resources**, complete beatability and all-pair replay. No post-fill placement/resource
mutation. External `stage_capacity.py` and `capacity-staging-proof.json` retain exact inputs, actor Hashes
and source actors. Fresh isolated New Game launcher/checklist:
`ingame/Test - first containers.bat`, `ingame/first-container-checklist.md` in the external work directory.
Template-derived CRLF launcher dry-run passed; no game started or game-folder write.
Active binding after the literal-message correction is **first-container-check-v2**:
mod `ingame/mods/first-container-check-v2/first-container-check-v2`, user
`ingame/user-first-container-check-v2`. The same launcher filename passed a fresh CRLF/dry-run check.
The proof records hashes of nine current source files. Old test user/mod remain untouched; Claude
re-runs the boot check and re-arms the watcher before Kareem plays. No acceptance is inferred from process presence.

Mido's middle-left chest gives native three-stick bundle **3/10**, far-right gives Kokiri Sword and
middle-right gives Hylian Shield. After meeting the tree, the shop counter gives Slingshot **30/30**;
shoot to **29/30**, repeat talk must not refill/reward again or give an extra Deku Shield, then reload
retains stock/capacity. Optional 40-rupee near-bridge scrub gives Medium Stick Bag **20/20**; this is a
bag-only scrub regression, **not** a first Bow/quiver acceptance. Required route 7–9 minutes; stop at ten,
skipping the optional scrub if necessary. Save/reload thumbnail: Kokiri Forest outside Kokiri Shop;
first launch has no existing thumbnail. Claude must boot-check; Kareem supplies item-menu results and
runtime `mods: <file> <- <test path>` proof for Sequence, child Banc, shopkeeper and both shared flows.

### First-containers v2: in-game acceptance

**PASS — Kareem, 2026-11-12, play/save evidence 12:07–12:11, reported by Claude.**
Snapshots are outside the repository under `E:/OOTRemake/work/save-backups/`, the
`2026-11-12_12*-r13-firstcontainers-v2-1` through `-10` series. Claude first reported the save evidence,
then Kareem confirmed that he could swing a Stick and fire the Slingshot; both still worked after
**Save and Quit → Continue**, with no issues.

| Saved state | Confirmed native actors | Stock / capacity |
|---|---|---:|
| New Game | No Sticks, Stick Bag or Slingshot | — |
| Mido middle-left chest | `Item_DekuStick` + `Item_StickBag_Small` | 3 / 10 |
| Counter gift | `Weapon_Range_SlingShot` + `Item_BulletBag_Small` | 30 / 30 |
| After a shot | Slingshot retained | 29 / 30 |

No Deku Shield was granted; no crash. Runtime loaded `GetPouchContent`, `Dm_SY_GetInEvent`,
the Kokiri child shopkeeper flow/packs and `SetPouchAndStatusForGameStart` **from this mod**.
This accepts **chest Sticks + counter-gift Slingshot pickup/use/reload**, not every family or source.
Scrub/Goron, literal-source and Bow/quiver paths retain native-data/test coverage only; a loaded common
flow is not proof every branch was played.

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
The completed independent audit is external `bomb-gating-report.md` and its JSON/probe files.
Ordinary bomb LiftableParam requires Low; Bombchus require None. Bag expansion grants no strength.
D30 already gates bombs in 0.1.2 (`6e5e179` predates both releases): all 236 compiled bag-dependent
rules also read strength, no ungated witness among 2,411 compiled rules. Child Silver/Golden alone
remain conservatively unusable in logic; adult accepts them. Native one-field LiftGrade is shared.

Read-only original 0.1.2 Recommended seeds 0–99: **100/100 generated on the first attempt and beatable;
zero newly unbeatable** under the real strength gate. A deliberately pre-D30, bag-only counterfactual
generated 100 but **26** fail replay under the real gate; this is not a defect count for published 0.1.2.
In 74 actual seeds the bag can precede the Bracelet without being credited as usable bombs.
No new bomb/Bombchu logic restriction or shelf-wide King Dodongo gate is justified.

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
The complete alias-family audit follows. Historical and community impact measurements are complete;
the corrected hard-order screen's first-attempt failures are an allocation issue, documented below.

## Complete alias-family audit

Effective `prepare(load_spec(), Settings())` contains **41 alias targets**: five fixed-tier families,
four other targets, 22 silver-rupee targets and ten small-key targets. The following covers all of them.
The MAX implementation is uncommitted pending its approved placement proof's first-attempt sweep and full gates;
no fallback policy or version change has been approved.

| Family | Previous accumulation | Audited behavior / change |
|---|---|---|
| Ocarina: Fairy 1, Time 2 | SUM, incorrectly 3 together | Separate native slots; MAX 2, no placement restriction. Kareem 2026-11-12. |
| Hookshot 1, Longshot 2 | SUM, incorrectly 3 together | MAX 2, no restriction. Late Hookshot retained Longshot in R8-FROGS and Kareem's 2026-11-12 statement. |
| Strength: Bracelet 1, Silver 2, Golden 3 | SUM; Bracelet + Silver incorrectly satisfied tier 3 | Native shared saved LiftGrade can be overwritten downward. MAX needs the mandatory-lower ownership proof; not merely sphere order. |
| Scales: Silver 1, Golden 2 | SUM, incorrectly 3 together | Native saved DiveDepth can be overwritten downward. MAX needs the same mandatory-lower proof. |
| Wallets: Adult 1, Giant 2, Tycoon 3 | SUM; Adult + Giant incorrectly gave 3 | Native capacity expansion is max-guarded; MAX, no restriction. Tycoon is catalogued, not a new supported grant. |
| Magic Meter: Lens, Din/Farore/Nayru, Fire/Ice/Light Arrows, each 1 | Additive availability aliases | Unchanged: rules test availability, not a two-level magic counter. Native MPMaxUP skips an existing nonzero meter except the double-magic grant (special-deal index 12), so a later base grant does not lower double magic. |
| Bomb Bag (30) → Bomb Bag 1 | Additive availability alias | Unchanged: the rule needs presence, not a bag-tier count. Capacity is natively max-guarded. |
| Heart Container → Piece of Heart 4; TCG Piece → Piece of Heart 1 | Quantities add | Unchanged: genuine piece counts, not tiers. |
| Buy Magic Bean / Magic Bean Pack → Magic Bean 10 each | Quantities add | Unchanged: genuine bean counts. |
| Ten Small Key Ring → corresponding Small Key targets, 10 each | Quantities add | Unchanged: Bottom of the Well, Fire, Forest, Ganons Castle, Gerudo Training Ground, Shadow, Spirit, Thieves Hideout, Treasure Chest Game and Water. Catalog audit, not approval of key-ring grants. |
| Twenty-two Silver Rupee Pouch → corresponding Silver Rupee targets, 10 each | Quantities add | Unchanged: Well Basement; Dodongos Staircase; Ganons Fire/Forest/Light/Shadow/Spirit/Water trials; GTG Lava/Slopes/Water; Ice Push Block/Spinning Scythe; Shadow Huge Pit/Invisible Blades/Invisible Spikes/Scythe Shortcut; Spirit Adult Boulders/Adult Climb/Child Early Torches/Lobby and Lower Adult/Sun Block. |
| Slingshot/Bullet Bags, Bow/Quivers, stick/nut capacity | No multi-tier alias family in this world | Unchanged: Bullet Bag (40), Quiver (40) and stick/nut capacity are independent items. Their native capacities are max-guarded; a bag does not imply owning its rental weapon. |
| Swords and shields | Independent items, no tier aliases | Unchanged: Kokiri Sword, Giants Knife and Biggoron Sword are not summed into a sword level. No sword/shield MAX conversion or restriction. |

Genuine progressive copies keep counting; a fixed tier does not add its tier number to those copies.
The family level is `max(genuine progressive count, highest fixed tier)`. Focused tier/fill/age tests:
**82 passed** after correcting one test's mistaken expectation that the family level was its raw copy count.

## Historical MAX impact and unsafe original orders

Original-version generators, unchanged placements, all five alias families switched SUM→MAX only at
replay; every withheld-lower pair checked, with no native exemption. Exact source/release provenance
and settings are external `tier-impact-provenance*.json`; results/seed lists are `tier-impact-summary.json`
and its four JSONL datasets. Frozen production Search cross-check matches the independent replay.

| Original dataset | SUM wins | MAX wins | Full spheres changed | Golden Gauntlets reachable without Silver | Golden Scale reachable without Silver Scale |
|---|---:|---:|---:|---:|---:|
| 0.1.2 Recommended, seeds 0–99 | 100/100 | 100/100 | 15 | 94 | 66 |
| 0.2.0 `30ba5c9` Recommended, seeds 0–99 | 100/100 | 100/100 | 15 | 94 | 66 |
| Community 11, 0.1.1, hash `1C37F227BEDE` | 1/1 | 1/1 | 0 | 1 | 1 |
| Community 15, 0.1.2, hash `0EF74161E8AF` | 1/1 | 1/1 | 0 | 1 | 1 |

No seed needed summed tiers; no collected set shrank. Strength alone causes the sphere changes:
Bracelet+Silver overestimated tier 3 in 29 seeds per Recommended set. Only seed 2 changes sphere count,
20→21; the other changes delay OGC Great Fairy and occasional downstream checks. The four other
families change no reachability. Both version datasets have identical placements.
Community regenerated placements match their stored spoilers; full spheres are unchanged under MAX.
**Their logical wins are not in-game safety proofs:** both permit the dangerous higher-before-lower
strength and scale orders. Seed 11's Spirit hand-chest key defect is separately unresolved by this replay.

## Native source guards

Inspected the reward entries themselves, not just the item-table setters. No inspected source-specific
flow checks a higher owned tier before granting the lower one:

| Native source | Native reward path | Guard / consequence |
|---|---|---|
| Darunia's Bracelet | `Get_StoneOfFire/Event31` → `Dm_Goron_0030:C10/Event127` → `Dm_SY_GetInEvent:GetInEvent_Goron/Event124` | Literal Bracelet pouch grant. The upstream SariaMelodyPlay BoolExp compares the saved quest-stage enum, not strength. The get entry has no higher-grade condition. |
| Zora diving Silver Scale | `MiniGame_Diving:FirstClear/Event21` → `GetInEvent_NotTurn_NotNpc/Event313` → `GetPouchContent/Event0` | Literal Silver grant. First-clear/minigame flags do not inspect Golden Scale or DiveDepth. |
| Fishing Golden Scale | `MiniGame_Fishing:GiveReward/Event579` and `Event822` | Fish size, age, lure and `MiniGame_Fishing_GetGoldScale` gate the reward; not lower-scale ownership. Golden's own depth grant is idempotent at its tier. |
| Silver Gauntlets chest, Hash `2490063409521505179` | `SageOfSpirit:SageOfSpirit_NaboorIsTakenAway/Event64` → standard big chest, then Nabooru story | No query in the source wrapper; the native chest's ordinary pouch-admission path remains. No source-specific Golden/strength guard. |
| Golden Gauntlets chest, Hash `17657623307936361670` | `Defeat_Ganon:InsideGanonCastle_Dungeon_Get_Gauntlet_Gold/Event654` → standard big chest → `Event655` cutscene | No query in this source wrapper. No source-specific lower-tier test. |

Strength's Item/Armor grant rows are Low/Middle/High. Silver and Golden declare their separate adult
equipment actors; the Bracelet's GoronGauntlet special deal supplies the child armor. Equipment ownership
is not evidence that the shared saved lift grade is monotone. The separate UI-only `Pouch_Gauntlet_Gold`
row says Middle/Silver; it must not be substituted for the real Item/Armor Golden grant.

External reproducers: `source_guards.py`, `source_more.py`, `source_grant_guards.py`, `entry_guards.py`,
`source_expressions.py`, `strength_equipment.py`, under `E:/OOTRemake/work/r13-item-grants`.
No game files or decoded trees were added to the repository.

## Feasibility: distinguish assumptions from actual reachability

The first screen assumed **every other seed item**, including fixed Ruto's Letter, stones and medallions.
That is a sufficient but unnecessarily strong screen, not an exact proof that the user's rule is infeasible.
In the frozen candidate, it left Recommended Golden Scale with only LH Lab Dive (self-locked at scale 2)
and Kak 100 Skulltulas (the world has 97 available tokens): **zero viable slots**. Public CLI seed 8 failed
all ten fills there. Chest-only seeds 0–99 did generate on their first attempt; their scale pair was fixed.

**Correction to the initial agent diagnosis:** `native_slot_screen.py` tested maximal assumed inventory,
not the native placement graph. `native_tier_replay.py` replayed all native placements, forced **all pairs**
checked (no unshuffled exemption), and found **zero violations in both presets**. Withholding the Bracelet
blocked both gauntlets; withholding Silver Gauntlets blocked Golden; withholding Silver Scale blocked
Golden Scale, Ruto's Letter, the Sapphire and time travel. Native progression dependencies, rather than a
source-specific grant guard, protect this closed-default layout. A blanket native-pair exemption is not justified.

A second **read-only, no-fill diagnostic**, `fixed_progression_screen.py`, assumes only shuffled pool items
and actually collects fixed rewards through their own rules. It preserves those dependencies:

| Preset | Higher tier | Type-eligible slots | Pass corrected screen | Viable without target/later tiers |
|---|---|---:|---:|---:|
| Recommended | Silver Gauntlets | 209 | 134 | 103 |
| Recommended | Golden Gauntlets | 209 | 31 | 22 |
| Recommended | Golden Scale | 40 | 13 | 11 |
| Chest-only | Silver Gauntlets | 165 | 140 | 112 |
| Chest-only | Golden Gauntlets | 165 | 28 | 21 |
| Chest-only, hypothetical moved scale | Golden Scale | 165 | 135 | 135 |

These candidate sets are seed-invariant, so their minimum and median are identical; the last row is diagnostic,
not a claim that Chest-only shuffles scales. The diagnostic did not perform a fill.
**Approved by Claude, 2026-11-12:** repair the fixed-item assumption and retain the actual-placement replay for
every pair, including native pairs. Implemented in `generate/fill.py`; no fallback or wrapper.
The focused suite now passes **83 tests**, including the fixed-reward prerequisite regression and rejection of
an unsafe all-native layout. A fresh 100+100 sweep must count first outer attempts only (`attempts=1`), keep the
first failure, and stop further behavior changes if either rate is below 100%.

The original-screen measurement completed: Chest-only **100/100**, first attempt; Recommended **0/100** over
1,000 outer attempts. Of those attempts 997 failed at Golden Scale and three at the return kit. This is the
superseded algorithm, not the approved correction. `feasibility-report.md` and `feasibility-summary.json`
retain all seed IDs, first errors and candidate/stage min/medians; original data was not overwritten.
Historical all-family SUM/MAX/ownership replays are separate from these fill measurements.

### Corrected-screen first attempts and allocation diagnosis

The corrected screen's separate no-retry sweep preserved every first failure:

| Preset, seeds 0–99 | First-attempt generated | Failed seed IDs |
|---|---:|---|
| Chest-only | 98/100 | 16, 19 |
| Recommended | 97/100 | 12, 55, 59 |

All five fail in `_fill_age_return` with Golden Gauntlets unplaced; all successful outputs have zero
all-pair violations. Scale outcomes are unknown in those aborted fills, not falsely counted successful.
Original `approved-first-attempt-*` data are retained; corrected strength attribution is in the separate
`approved-first-attempt-family-attribution.json`. No production allocation/rule retuning followed.

Read-only exact failed-attempt replays (`allocation-diagnosis.md`, `kit-trace-*.json`) find one usable adult
Golden destination after Silver is collected: **Goron City Chest (TBox_Rupee_Purple) #1**. The tier screen
allows 28 Chest-only / 31 Recommended shuffled slots overall, but the other empty ones are not adult
return-kit reachable then. Flexible earlier staged items consume that sole slot:

| Failed seed | Consuming item | Its candidates that pass | Golden candidates that pass |
|---|---|---:|---:|
| Chest-only 16 | Longshot | 22 | 1 |
| Chest-only 19 | Hookshot | 40 | 1 |
| Recommended 12 | Bow | 19 | 1 |
| Recommended 55 | Bow | 24 | 1 |
| Recommended 59 | Bow | 22 | 1 |

The private full-MCF replacement selects the minimum **positive** candidate count per return-kit pass,
retaining staged-order ties and waiting on zero candidates. New independent first-attempt datasets
`allocation-mcf-{defaults,recommended}.jsonl` generated every seed, fixed all five old failures and introduced
none; all-pair violations and internal retries were zero. The boss key never preceded the first small key.
Original failure files and production allocation were unchanged.

**Rejected by Claude, 2026-11-12:** the success rate does not justify the predictable placements:

| Preset | Silver destinations before MCF | Silver destinations under MCF | Golden destinations under MCF |
|---|---:|---:|---:|
| Chest-only | 25 | 3 | 1 |
| Recommended | 14 | 3 | 1 |

Silver always goes to GC Chest #2 or one of the two Dampé Race checks; Golden always goes to GC Chest #1.
The measured MCF patch was never applied to production.

**New experiments approved by Claude, production still frozen:**

- **A:** derive the fixed tiers actually needed by the independent adult-return oracle, credit guaranteed
  initial inventory, and stage only those. Other fixed tiers (including Golden, and redundant Hookshot tiers)
  go through ordinary fill with the unchanged hard reachability rule and its full candidate set.
- **B:** jump the staged queue only for the first item with exactly one candidate; otherwise retain the
  original first-positive choice. No MCF priority among larger candidate sets.
- Each gets its own new Chest-only and Recommended seeds 0–99, attempts=1, full placements, first failures,
  independent beatability/age-return/all-pair checks and five-item distinct location/frequency metrics.
- Compare with actual pre-rule 0.2.0 `30ba5c9` for Goron Bracelet, Silver/Golden Gauntlets and Silver/Golden Scale.
  Reuse existing historical Recommended placements; generate only missing baseline data.

Recommend only after both results: zero failures first, then placement variety. Do not alter production
allocation, weaken the tier rule or silently accept a predictable fallback before Claude chooses.

### Option costs and recommendation

| Option | Strength cost | Scales cost | Safety requirement |
|---|---|---|---|
| (a) Whole family vanilla | Remove three rewards from shuffle | Remove two rewards from shuffle | Still replay the actual placements; the native source alone is not a downgrade guard, and changed settings can bypass native progression. |
| (b) Only infeasible tier vanilla | Remove only each affected tier, retaining the other tier rewards | Golden-only fallback removes one shuffled reward, retaining Silver | Still prove every lower prerequisite for the fixed higher source; never silently exempt a native fallback. |
| (c) Progressive chest wrapper, later | Three progressive strength copies, limited to chests | Two progressive scale copies, limited to chests | New runtime grant/owned/equipment/presentation behavior, both chest lifecycles, source wrappers and analyzed-event preloads; requires separate played acceptance. Named-key cloning is a pattern, not proof. |

Recommendation, superseded by Claude's approved correction above: do not sacrifice shuffle or introduce a wrapper
to work around pre-owned fixed checks. Correct the assumption and keep the same hard replay guarantee for both
families. The corrected diagnostic supplies nonzero candidates for every shuffled higher tier; actual first-attempt
success remains the acceptance condition. No automatic fallback has been implemented.

## Verification so far

- Independent original/patched native Sequence decoder oracle: pass.
- Public full CLI generation: seed 8, Chest+Shop+Gift+Scrub+BossHeart, 293 shuffled checks,
  24 spheres, 137 resources; actual native writer/search smoke, not a game run.
- Controlled public generation: 29 spheres / 78 resources, as above.
- Template launcher `CLAWSHOT_DRY_RUN=1`: pass; no game started.
- Focused ruff check: pass. Focused synthetic/native regressions: **15 passed**, 20 deselected
  (`tests/test_start_items.py`, new adult-trade tests). Full serialized gates still pending.

### Final verification fixture

Claude identified the default `pr1-check/dump` as an obsolete partial fixture; it was not edited or used
for these final gates. Copied its builder to external `rounds/r13/make_dump_item_grants.py`, changed only
the owned copy's output/scratch paths, and ran it with this worktree's explicit `PYTHONPATH`.
Own fixture: `E:/OOTRemake/work/rounds/r13/dump-item-grants`: **1,245 wanted files, 1,210 base copies,
48 changed/new update copies, 1,197 unchanged, zero missing**. The actual `local_romfs` adapter opened it;
the new-game Sequence, both key-compiler RSDB files and both shared item-get flows were present.
Builder used one worker while Hookshot was active. Final `review_gates.sh` ran under `r13/gate.lock`
with explicit `OOT_DUMP` pointing to this fixture, via Git Bash rather than Windows' WSL `bash`.

All five required fixture files also matched the read-only installed romfs **byte-for-byte by SHA256**,
not merely by filename. Whole-repository static gates passed: **320 Python files formatted; ruff check clean**.
Only two formatting-only differences in the pending tier correction/test were normalized; no allocation
behavior changed and the frozen experiment snapshots were not edited.
The original full run finished 2026-11-12 at 14:14: format/lint passed; synthetic **1,082 passed,
136 skipped** (557.63s); native **130 passed, four failed**, 1,084 deselected (4,448.20s).
Log: `E:/OOTRemake/work/r13-item-grants-final-gates.txt`. This was **not a clean full gate**.

### Directed four-case repair

Claude requested read-only diagnosis, evidence before edits, then only the four failed native cases
after rebasing onto integrated main `fa6f4ef`; one worker under `r13/gate.lock`, before cs13a's matrix.
All three private tier experiments remain paused at position 6 until explicitly authorized.

- `test_seed_dump.py::test_written_files_differ_only_where_the_plan_says[1-3]`: the installed romfs and
  owned fixture's `base/romfs` both store the startup Sequence as **raw AINB**, 5,916 bytes,
  magic `4149422008040000`, SHA-256
  `63ddeaa34e4839eceea2509e20b27b6f3c19f15cd72daf308c799bdfdb6e87b0`.
  No compressed sibling exists in the installed romfs. The writer already reads/writes non-`.zs`
  resources raw; the test incorrectly decompressed every extra file. The oracle now decodes only `.zs`.
- `test_gifts_dump.py::test_dump_gift_shuffle_slice_writes_each_moved_gift`: the original run passed
  the nonempty moved-gift assertion and every emitted gift actor assertion, then failed on incidental
  `assert held`. Read-only setup shows four eligible rewards: Shopkeeper Deku Shield, Skull Kid and
  Memory Game Heart Pieces (native chest actors), and Saria's Fairy Ocarina (`chest_verified`).
  Therefore no held item remains **in this slice**. An in-memory counterfactual removing **only** the
  `LW Trade Odd Potion` vanilla lock restores `Poachers Saw: (NPC, Cutscene, Boss)`.
  The adult-trade policy removed the last held item; no gift-writing regression was observed.
  Removed this slice's incidental hold block; the synthetic Letter/Song destination-policy regression
  remains unchanged. Claude required retained native held-write coverage: a fresh unrestricted production
  Gift setup still holds **28 items: 12 songs and 16 non-songs**, including Bottle, both Scales,
  Biggoron Sword and capacity upgrades. The same dump test now builds that real setup, swaps Bottle and
  Deku Shield between child Anju and the Kokiri shopkeeper, asserts the held Bottle cannot go to chests
  and both NPC destinations meet the restrictions, and reads back both native transformed hand-overs.
  No counterfactual production-policy override is needed. No production writer, grant or allocation
  behavior changed for these repairs.

Causes were posted on `cs-r13` at 15:53 before editing, and reposted as two short merge-record notes at
15:59. Rebased onto integrated main `fa6f4ef`; conflict resolution retains unconditional key/dungeon
credit compilation before bag gates, plus native dungeon-state and pouch-stock simulator behavior.
Static gates passed: **323 formatted files, ruff clean**. The initial corrected four-case run on
`45412c2` passed **4/4 in 73.65s**, using one worker, the owned fixture and `r13/gate.lock`
(`four-dump-after-main.txt`). Claude then requested the held-write assertion above and a **full rebased
synthetic suite** (`-m 'not dump'`, one worker under the lock) before handoff. The four-case run will be
repeated after this coverage addition; the initial pass and original failed output are retained.
No foreign process or lock was removed.

### Rebased verification and native-shaped fixture correction

The strengthened four-case native run on `12cd47a` passed **4/4 in 82.64s** (one worker,
owned `OOT_DUMP`, serialized lock), including the real production held-Bottle hand-over assertions.
Log/result: `four-dump-held-after-main.txt`, `four-dump-held-after-main-result.json`.

The requested full synthetic run on the same head was **not clean**: **1,154 passed, two failed,
two skipped, 129 deselected**, 1,056.32s. Both failures are the public named-key/first-bag test
(`Obj_TBox_A_01`, `Obj_TBox_A_02`). Printed payload: shared synthetic `GetPouchContent` index 0
was `Window/EventTriggerSetForGetWindow`; the bag transform requires the native argument-driven
`EventTriggerAddOrRemovePouchContent` there. Read-only native inspection confirms
`GetPouchContent.bfevfl.zs` index 0 is `Event0`, `PouchSystemActor`,
`EventTriggerAddOrRemovePouchContent`, `Num=1`, `Actor=Argument('ActorName')`.

Claude requested production proof before accepting a synthetic-only fix; the proposed fixture edit
was held/reverted until that check completed. **Real production proof passed on `12cd47a`:**

- Native `GetPouchContent` has 114 events; index 0 is the argument-driven `Event0` pouch grant.
  `EventTriggerSetForGetWindow` is `Event11` at index 6, not the synthetic fixture's index 0.
- Public seed 8 with `dungeon_items=anywhere` compiled **33 named-key bindings**. After `keys.changes`,
  the flow had 2,547 events and **the complete original 114-event prefix was unchanged**.
  An observer at the actual `bags.patch_flow` call saw that same unchanged `Event0` and prefix, then
  called the original guard unchanged. Helpers were appended, not reordered over native events.
- An independent, unmodified public CLI invocation succeeded:
  `uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 8 --dungeon-items anywhere --out
  E:/OOTRemake/work/r13-item-grants/named-keys-first-bag-cli-seed8`.
  It wrote **93 resources**; its complete spoiler matched the traced public API output exactly.
  Bomb Bag Small moved to Kokiri Sword Chest; Slingshot moved to Dodongo's Cavern Map Chest.
  The production bag guard remained enabled and its source SHA-256 unchanged.

Proof: external `named-keys-native-bags-proof.json`; CLI log `named-keys-first-bag-cli-seed8.txt`.
One worker under the lock; no game started. The first diagnostic script stopped on an unsupported
catalog name `Bomb Bag (40)` before reaching the CLI; the actual catalog was printed and the
diagnostic selector corrected. No production failure or unchanged retry was hidden.

With production identity/order demonstrated, corrected **only** the synthetic fixture's storage:
swap Grant/Window at indexes 0/4, point the display continuation to Grant 0 and display entry to
Window 4. Execution still sets window/text before grant and autosave. All fixture consumers use
names/entry points; native-state and order assertions remain intact. No production guard relaxation.
Failure log `rebased-synthetic.txt` is retained; the corrected full synthetic rerun uses
`rebased-synthetic-fixture-fixed.txt`, one worker and the lock before handoff.

### Final rebased gate-repair result

| Check | Revision | Observed result |
|---|---|---|
| Format and lint | `6204cca` | 323 Python files formatted; ruff clean |
| Directed four dump cases, including held-Bottle writes | `12cd47a` | 4 passed, 82.64s |
| Real named-key/first-bag trace and unmodified public CLI | `12cd47a` | Passed; guard unchanged, 33 named bindings, 93 resources |
| Full synthetic suite, `-m 'not dump'` | `6204cca` | 1,156 passed, 2 skipped, 129 deselected, 1,155.84s |

Both test runs used `CLAWSHOT_WORKERS=1` under `E:/OOTRemake/work/rounds/r13/gate.lock`;
the native run explicitly set the owned `OOT_DUMP` and read-only installed `OOT_ROMFS`.
The final synthetic revision differs from the passing native/CLI revision **only in the synthetic
fixture and this evidence record**, not production code. Result metadata records both revisions.
Logs/results remain outside the repository:
`four-dump-held-after-main.txt` / `four-dump-held-after-main-result.json`,
`rebased-synthetic-fixture-fixed.txt` / `rebased-synthetic-fixture-fixed-result.json`,
and the production proof/CLI files named above. Original failed logs remain intact.
Only the four requested native cases were rerun, **not the entire native suite**.

The owned lock was released after each run; no foreign lock/process was touched. Claude's position 5
matrix may proceed after this handoff. A/B and the missing historical Chest-only baseline remain
**unmeasured and explicitly paused at position 6**; no allocator experiment is applied or recommended.
