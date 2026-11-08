# Round 5, track B: Deku Shield and shops (cs5b)

Branch `r5/shops`. Dump/save backups read-only. No game, launcher or window started.
Required plans and all four round-4 handoffs read before changes. No dependency added.

## Item 1: every shop

`data/shops.toml` records all **128** census `shop_slot` Hashes, their Banc file, linked seller Hash/actor,
ShopRef member, index, vanilla display actor, base price and census world name. Nine shops including Mask Shop;
eight slots each, with age/stock/Alternative copies. Earlier section 5's seven-slot count omitted index 0
(the blackboard default when the parameter is absent). Hash, not index, remains the stable identity.

The dump oracle reads every shelf, follows the seller's `ForSale`/`Reference` link, resolves inherited
`ActorParam.Components.ShopRef`, checks `GoodsList[index].Actor` and `PouchActorInfo.BuyingPrice + PriceOffset`.
The owner pack matters: changing Banc alone does not change the sale definition.

- Display: shelf `Gyaml`; model/ActorName/PouchContent refs in that actor's pack. Forty-three distinct placed
  native `Shop_*` actors (eight are masks). No native shop display for most chest major items.
- Sale, stock and releases: seller pack's `Component/ShopParam/*.bgyml`, `GoodsList[ShopItemIndex]`. Most stock is
  unlimited (`StockNum = -1`), including all eight Bombchu Shop offers. Kokiri short stock enables nuts, shield and one
  stick until `Meet_DekuTree_IsAfter_Step02_Exp`; full/short sellers and shelf copies have complementary Presence.
- Price: item pack `GameParameter/PriceParam`, reflected in `RSDB/PouchActorInfo`. Per-slot `PriceOffset` and
  `ConditionalPriceOffsetList` modify it. Market Hylian Shield: 80, discounted by 20 on
  `Npc_Hylia_Soldier_003_GateOpen`. Tunics are **600**, requiring the 1000 wallet, not N64 prices.
- Buying: `DisplayShop:Root_Buy` → selection screen → availability/stock/pouch checks →
  `EventTriggerGetItemAtShop` / `Dm_SY_ShopGet:ShopGet`, `EventTriggerShopItemPutInPouch`,
  `EventTriggerPayItemPriceAtShop`, `EventTriggerAddShopItemSoldNum`, board refresh. These engine actions use the
  selected sale item (`Shop_SelectItemName`), not a literal gift parameter. Bottles use a separate refill path.
- Name/description/get text: actor identity/ActorName and the selected sale item's UI lookup; merchant flavour
  messages are separate fixed `EventFlowMsg` IDs. No message strings copied or patched. Whether a deliberately
  mismatched shelf and sale item agree in UI is an in-game question, not an established behavior.
- Stock/save: no shelf has a permanent census save flag. Seller actions track sold numbers and refresh boards;
  a one-time randomized item needs the seller stock mechanism, not a made-up Bool64bitKey.

### Kokiri shield and tutorial

`Npc_Kokiri_001_Shop_Child:Talk` branches on the Deku Tree quest. Before Mido it uses `DisplayShop:Root_Buy`;
after returning, `Event10` checks acquired `Weapon_Shield_Deku`, then `Event6` checks
`KokiriForest_Meet_DekuTree_BoughtDekuShield`; when not yet set it calls
`Npc_Kokiri_010_Child:DekuShield_TutorialTalk` (`Event8`) and sets that Bool (`Event7`). Thus the tutorial is
item/history-based, not intrinsically attached to shelf index 6. A different item should not grant/equip the shield
or trigger its tutorial [INFERENCE; Kareem's test required]. A shield obtained elsewhere may trigger it later.

After `Meet_DekuTree_IsAfter_Step02_Exp`, `present_DekuSheld` checks whether the Deku Shield is equipped and
`HaveTalked_Npc_Kokiri_001_Shop_Child_PresentDekuShield`; `Event116/117` give `Obj_Shield_Deku` through
`Dm_SY_GetInEvent:GetInEvent_Mask`. This is not an additional pre-Mido free shield; it is a post-Mido replacement
route. Track D was asked to leave these grants alone pending integration.

## Item 2: native sale patch and three outputs

`shops.changes(romfs, {logical_slot: sale_actor})` builds decompressed resource transforms. It changes each
age/stock/Alternative shelf's `Gyaml` and each seller pack's active `GoodsList[index].Actor`. Fixed destination
price is preserved with `PriceOffset = old_slot_price - new_item_base_price`; conditional discounts stay.
The engine's original stock and release fields stay unchanged. Bundle-number boards follow the new bundle,
or are removed for a single item (sold-out boards stay). No ActorInfo, PouchActorInfo, message or event change.

All three outputs and **unrun** launchers are under `E:/OOTRemake/work/r5-shops/`; `README.md` there gives the
full checklist. Each launcher uses its own new-game user folder, based on the round-2 safe launcher:

| Output | Expected experiment | Size-table result |
|---|---|---|
| `shield-slot-hylian` | Usual Kokiri shield slot displays/sells Hylian Shield at **40**, not 80; no Deku Shield or its tutorial expected without acquired Deku Shield | 5 files; Adult/Child seller packs raised by 32 each; size table included |
| `mido-chest-deku` | Mido bottom-left chest Hash 12786193094758345086 gives Deku Shield; get sword and approach Mido; visit shop without buying to check acquired-item tutorial | Child Dynamic grows 510884 → 510924; entry 511176 → 511208; size table included |
| `shield-display-boomerang` | Shelf stays Deku Shield, sale is `Item_Boomerang` at **40**; inspect selection name/description, merchant, get model/text, inventory and tutorial | Three seller packs only; all fit existing entries |

The third output is a **finding to test**, not proof stand-ins work. Shelf and sale definitions are independent
in the data and engine flow actions use selected-item game data, but the native NPC selection code may bind
by actor identity rather than index. **Kareem: does this mismatch sell a Boomerang at all? Which identity drives
the menu name/description, get model/text and stock?** If it works, a future stand-in setting needs:

- Explicit display actor separate from sale/pouch actor; accurate selection/get text (merchant flavour may remain).
- Price/conditional offsets based on the sale actor; stand-in experiment preserves 40 with offset +40.
- Compatible `EventQueryCanAddToPorchByGameData`/category route (bottle refill vs ordinary grant).
- Per-slot stock/release policy and sold-number identity traced across seller age/short-stock/Alternative copies.
  The original refill stock is not a demonstrated permanent one-time reward flag. Item-based
  `SoldOutGameData` (e.g. potion-shop Blue Fire) must not accidentally follow the old item.
- Kokiri tutorial remains item/history-gated. Do not suppress it to make an experiment look successful.

No game has been run. Data build/readback is complete; `from the overlay` plus the in-game result is still required.
Synthetic transform tests: **4 passed**. Targeted dump field-diff tests for native and stand-in variants:
**2 passed**; all other members/fields, including stock/release, match the original. Live output builder printed
each old/new resource size, checked compression/readback and wrote raised entries only where needed.

## Item 3: shield pool, native destinations and wallets

`world/shops.py` normalizes the translated shop locations from the catalog, then compiles its wallet and release
rules. The separate loader hook follows after the authorized rebase onto `cd592e3`. There are **64** ordinary
shop locations, not 128 independent rewards; shelf copies keep one shared logical placement. The eight mask
loans stay `MaskShop`, outside `--shuffle Shop` (their rental/trade flow is not an ordinary sale).

The shield slot's pool entry is now the actual **Deku Shield**, classified progression. Before: a live search
holding Kokiri Sword + Deku Shield could not pass Mido (helper read only `Buy Deku Shield`/drop). After: it can.
Vanilla shops still supply the shield by purchase; shuffling `Shop` removes the fixed purchase and puts its shield
in the shared pool. Keeping Mido blocks a shield self-lock in the Deku Tree; skipping Mido permits that placement,
without opening the separate forest exit.

Audited **every helper with a `Buy_*` reference**:

| Helper | Result |
|---|---|
| `Deku_Shield`, `Hylian_Shield` | Added actual shield inventory; retained bought/drop forms |
| `Goron_Tunic`, `Zora_Tunic` | Already read quoted actual inventory and bought forms; unchanged |
| `Nuts`, `Sticks` | Added actual chest inventory; Sticks also recognizes native five-stick bundles |
| `Bugs`, `Fish`, `Fairy`, `Blue_Fire` | Bought refill capability usable only with `has_bottle`; Blue Fire Arrow alternative retained |
| `can_refill_bombchus` | Includes all native 1/3/5/8/10/15/20/30 bundle variants |

Other direct `Buy_*` checks keep their existing logical item identity, so no helper silently loses a native
offer. Refills are not new bottles; their `Buy ...` names describe refill access, not bottle ownership.

Reviewer-approved **provisional** constraints (sources and rules in `shops.toml`):

- Only the 35 ordinary native-display item variants can occupy Shop destinations. No custom/stand-in displays.
- Tunics only at adult-accessible shops; child-only Market excluded. Original tunic slots are conservatively adult.
- Capacity tiers **200/500/1000**; 240-rupee Bombchus need one wallet upgrade, 600-rupee tunics need two.
  Slot prices remain fixed under item swaps; conditional discounts remain (using the undiscounted upper bound
  is conservative).
- Kokiri's five locked early slots keep the post-Mido release; the cheap nuts/stick and shield remain early.
- Bombchu Shop keeps Dodongo's clear gate; Market Bazaar's bomb slot keeps its own clear gate.
- Potion shops' Blue Fire slot keeps the acquired-Blue-Fire gate from `SoldOutGameData`/`DisplayShop:Event108`.
  **Kareem: confirm the old Blue Fire slot unlocks on first Blue Fire acquisition, including when it sells
  something else.** Conservative until played; component fields are not silently deleted.

Fill commits are intentionally isolated: `bc71356` touches only `allowed()`; `ee886a3` fixes its caller gap.
Normal filler previously bypassed `allowed()` entirely. Shop seeds now place chest-only items first and route
all remaining filler through allowed-aware placement; native items prefer native shop destinations to avoid
exhausting the chests needed by non-display items. Chest-only seed ordering is unchanged.

Checks: initial shop-logic run **21 passed, 1 failed**; printed failure was test `Counter(dict)` treating the
dictionary's item metadata as counts. Changed the assertion to count its keys; aimed rerun **1 passed**,
including 30 complete synthetic fills with non-display normal filler. The first run's mini-seed 22 was beatable.
Live smoke printed actual shield + sword passes Mido; catalog gives 35 native items; tunic false with 500 wallet,
true with 1000. New stock-gate test and post-rebase hook results are recorded below.

Reviewer corrected all three launchers to **only `E:/Games/Hookshot/hookshot.exe`**; that correction was read
back, not overwritten. No test build/fallback is allowed. None was run.

## Item 4: seed integration after the prerequisites

Claude confirmed main `cd592e3`; clean rebase succeeded. Loader hook `5b6e92f` is a separate, four-line
`load.py`-only commit and was posted. Native shop-to-chest mappings are isolated in `17207fb`; native `Shop_*`
pouch actor grants are still pending family-level in-game checks, not presented as certified.

`make_seed` now registers `shops.patch_step` for only its shuffled Shop locations, through the approved
`extra_steps` API. Other vanilla shops are not patched. CLI accepts `--shuffle Shop` or `--shuffle Chest Shop`.
The native palette includes eight equal-quantity chest-ammo aliases (Arrows 10/30, Bombs 5/10/20,
Bombchus 5/10/20) in addition to 35 ordinary sale variants. `Buy Magic Jar` is distinct from Track C's
actual chest `Magic Jar`, avoiding an actor/count collision. Refills keep bought-capability names, not fake bottles.

Live CLI smoke (no game):

| Command selection / output | Observed result |
|---|---|
| seed 22, `--shuffle Chest Shop --areas KokiriForest LostWood InsideTheDekuTree --goal "'Defeat Queen Gohma'"`, `.../r5-shops/seed-shop-22` | 20 checks, 3 spheres, 10 resources, seller-pack size entries raised |
| seed 7, same slice, `--shuffle Shop`, `.../r5-shops/seed-shop-only-7` | 8 checks, 4 spheres, 6 resources, seller-pack size entries raised |

Seed 22's shield is **KF Shop Item 3, 20 rupees**, in sphere 1 with Kokiri Sword and Slingshot. The intended
single-shop placement reaches all three Kokiri age/short-stock shelf copies and their seller packs.
The final dump regression checks this end-to-end plus preserved slot prices, release/stock and all output
resource sizes. No launcher was added for these smoke seeds; the three controlled experiments remain the
first in-game checks. Whole-game chest coverage and chronological age travel are still the other tracks'
integration prerequisites, not claimed by the slice smoke.

## Coordination and provisional choices

- Requested a narrow world loader hook for shop normalization/price predicates (not owned by B).
- Reviewer approved **native-display-only shop destinations**, no custom display packs (M4). The fill restriction
  will be a separate commit touching only `generate/fill.py`, posted to the thread. Shop pool items may move into
  chests; non-display chest items may not move into shops. Deku Shield has a native display.
- Reviewer requested a third output: unchanged Deku Shield shelf, `GoodsList.Actor = Item_Boomerang`.
- Item 4 waits for Claude's explicit confirmation that Track C's extra-step API is on main.
- **Kareem: with a changed shield slot, does its model/name/description match the new item, what does buying grant,
  and does any shield tutorial or extra shield appear?** Exact output routes follow under item 2.

## Tooling failures diagnosed

The tilde Bermuda path failed exit 127. Read `C:/Users/hi/go/bin`: only `bermuda.exe` exists; explicit native path
works. Initial research assumed `Shop_Shield_Deku`; printed the actor list, corrected to
`Shop_Weapon_Shield_Deku`. A guessed ShortStock flow did not exist; its actor pack inherits the normal flow and
replaces only ShopRef. Neither failure was rerun unchanged.

## Verification

Item 1: `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_shops_dump.py -s`: **1 passed**.
Live `load(); validate(...)` smoke: **128 shelves, nine shops**, all three KF shield copies priced 40.

## Final safety follow-up: removed quantity-board references

Live output inspection found a real omission after the first complete synthetic gate: quantity boards removed
from `Actors` and seller links still appeared in `FarDeleteGroups` and `SimultaneousGroups`. Printed exact
paths/Hash lists: Adult group 2 held removed 11847747441471484392 / 16953505662516287090; Child groups 3/4 held
4602234734267749628 / 4733469548168048595 / 10712672058188138415. No AI-group reference was found.

Fixed `patch_shelves` to remove those memberships too, preserving other group members and types. Extended the
synthetic regression with both group kinds: **1 passed** after the fix. Added a whole-catalog dump regression
replacing every ordinary shelf with a single-item native display: **1 passed**, no dangling group/link refs in
any shop's Banc. Rebuilt both smoke seeds after the aimed change (same placements/spheres/resource counts).
Fresh output smoke printed **zero** remaining references for all five removed boards. The throwaway inspection
script was removed; permanent behavior regressions remain. The three controlled player experiments were
unaffected (their old shield shelf has no quantity board).

