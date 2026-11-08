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
  unlimited (`StockNum = -1`); Bombchu Shop stock is finite. Kokiri short stock enables only nuts, shield and one
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
