# Round 8, Track C: shops (cs8c)

Branch `r8/shops`. Required AGENTS, README, plans 00–04, decisions and every round-6/7 report read before changes; Round 8 opening and inherited shared-file rules apply. Dump and save backups read-only. No game, batch, GUI, build or terminal-control command is run. Research and generated resources stay under `E:/OOTRemake/work/r8-shops-cs8c/`. No dependency change, merge, push, stash or unauthorized rebase.

## Item 1: persistent shuffled shopkeeper offer

Actual merchant flow printed to external `merchant-flow.txt` using the repository EVFL reader. `Talk` initializes its camera/Navi state before Event24 dispatches to Event23 (castle quest), Event21 (Gohma quest), then Event1 (Deku Tree meeting). The existing saved Bool `HaveTalked_Npc_Kokiri_001_Shop_Child_PresentDekuShield` already supplies D22 completion and the round-7 both-grant once-gate. No new save flag is needed.

Plan: intercept only the shuffled once-gated merchant after Event24's initialization. If incomplete and the existing meeting expression holds, call the original offer; otherwise retain original story dispatch. Never force Gohma/castle/meeting state. Unshuffled flow and implicit free-shield logic stay vanilla. Keep the `Missable` non-progression restriction (D28) until Kareem's result.

**Kareem: the requested new-game test will skip talking to the merchant until after Gohma, then test the late grant, repeat talk and Save/Continue; the castle-visit variant should also retain the offer.** Exact output/checklist and exercised evidence follow.

### Implemented / exercised

`gifts.py` intercepts only the `Event45` once-gated merchant at Event24's initialized dispatch. Two appended queries read the existing saved completion Bool and native tree-meeting BoolExp. An incomplete eligible offer reuses Event83 and its original return handling; completed/pre-meeting paths retain Event23's story-specific dispatch. Original quest queries, shelf releases, purchases, tutorial and saved flags are untouched. Both grant branches retain round7's immediate completion writes.

Failing-before regression: six late-story/equipment combinations returned no Boomerang (printed meeting=true with castle/Gohma=true); stale dispatch was not rejected. After the cause-specific fix, `uv run pytest tests/test_shopkeeper_window.py tests/test_gifts_shopkeeper.py -q --tb=short`: **17 passed**. `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_shopkeeper_window_dump.py tests/test_gifts_shopkeeper_dump.py -q --tb=short --basetemp E:/OOTRemake/work/r8-shops-cs8c/merchant-dump-next`: **2 passed**. Real-flow interpreter proves all four castle/Gohma combinations, equipped shield, repeat/restored completion and no pre-meeting gift; exact inverse recovers every other flow field.

Actual writer smoke: `uv run python E:/OOTRemake/work/r8-shops-cs8c/build_late_gift.py` passed, writing `ingame/shopkeeper-after-gohma-next/` with **four resources** (both Dynamic Bancs, merchant flow, size table). Flow **50552 -> 51736**, allocation **50832 -> 52016**; both chest copies change only Mido far-right's drop to Deku Shield. No GameDataList or quest state is changed. Every emitted resource parses/fits the table; inverse field deltas recover originals. Copied/statically checked approved new-game launcher; never executed.

**Kareem: follow `E:/OOTRemake/work/r8-shops-cs8c/ingame/late-gift-check.md`: avoid the merchant entirely, collect the supplied chest shield and vanilla Sword/Slingshot, clear Gohma, optionally visit Zelda before the first merchant talk, then obtain Boomerang with the shield equipped. Repeat after re-entry and Save/Continue must give nothing; normal shopping must still work.** Require overlay-open log. D28 stays in place; no gameplay result is claimed.

## Coordination / diagnostics

Initial allowed thread post failed with shell exit127: extensionless `~/go/bin/bermuda` not found. Filename lookup found `C:/Users/hi/go/bin/bermuda.exe`; using that actual binary posted successfully as cs8c. Python LSP references returned `No language server found`; known-symbol searches are the fallback. An attempted historical builder path was absent; use the actual external directory listing rather than infer a builder filename.

Shared changes will be isolated and posted; `generate/fill.py` algorithm remains Track A's and gift families other than this merchant remain Track D's. Section34 is appended in increasing order after available sections, no placeholders for32/33.

## Item 2: partial shelves and scrub fees

Implemented `shop_slots`0..8/default8, `scrub_prices=vanilla|fixed` and `scrub_price`0..1000/default10. All three use the existing Settings/as_dict/CS1 codec and explicit CLI override loop; no second serialization path or fill-algorithm change. `world.shops` applies first-N native indices as `keep_vanilla` metadata before pricing and pool construction. All copies share logical membership; eight mask loans remain untouched. Independent cheap-shield pricing remains active with zero selected shelves.

Supported Scrub once-sales change every grant/tier's `Price` argument alongside the assigned actor. `scrub-price-trace.txt` prints original Event300 binding `SimpleShop_Price` to `Price`, Event288's rupee test of `Price`, and Event4 passing that price variable to the normal purchase/get wrapper. Native cancellation/shortfall/success-only flags and every repeat-vendor event remain unchanged. Logic reads wallet tiers from the same `shops.toml` catalogue (200/500/1000); original stun/child/puzzle rules remain conjunctive. Effective `scrub_sale_prices` supplies spoiler/opening-note fees.

Provisional choices by cs8c: first N catalog indices rather than randomizing shelf membership; fixed-fee parameter defaults10; only the four supported shuffled once-sales change price. **Kareem/co-owner: do you prefer seeded random shelf membership to stable first-N indices, or fixed pricing for unshuffled/repeat vendors too?** Those are different policies, not silently enabled here. Existing defaults remain all8 shelves and vanilla scrub fees.

### Exercised evidence

- `uv run pytest tests/test_shop_settings.py tests/test_settings.py tests/test_settings_prices.py tests/test_scrubs.py tests/test_scrub_seed.py -q --tb=short`: **61 passed**. All nine shelf counts, exact selected pool/fixed remainder, CS1 fill replay, price-only effect on selected shelves, retained stock gates, fee0/200/201/500/501/1000 wallet boundaries, all native grant tiers and CLI override/refusals.
- Scoped format followed by `uv run ruff check`: **passed** after correcting the two printed excess-width lines (CLI help122, scrub source123).
- `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_shop_settings_dump.py -q --tb=short --basetemp E:/OOTRemake/work/r8-shops-cs8c/partial-dump-next`: **1 passed**. Real writer checks24 selected logical shelves across all128 physical definitions; unchanged unselected shelf/seller rows (except independent cheap shield), exact201 fees, wallet predicate transitions, exact inverse scrub flow and fresh chronological win.
- Actual public CLI, seed7, `--shuffle Chest Shop Scrub --shop-slots 3 --shop-prices affordable --scrub-prices fixed --scrub-price 201 --out E:/OOTRemake/work/r8-shops-cs8c/partial-fixed-seed-next`: **exit0, 192 checks, 23 spheres, 92 resources**, spoiler and play note. Full-world/default forest/return guarantee, no reroll or increased retry bound.

### Isolated shared commits (pre-rebase)

| Commit | Scope |
|---|---|
| `123daf6` | item1 gifts.py merchant-only dispatch |
| `6a9969d` | existing inverse-flow oracle's additional Event24 delta |
| `224b3e8` | item1 owned tests, report and section34 |
| `eb6ff95` | defaults only in settings.toml |
| `cf533d1` | fill.py Settings fields/validation/as_dict only |
| `95d5291`, `7bb5ab2` | CLI options and help-width correction |
| `a4570e7` | world.shops native-index selection metadata |
| `48956a6` | prepare hook before effective prices |
| `7f6de32` | scrub fees, wallet predicates and presentation metadata |

Reviewer-authorized rebase onto plans-only main `e3745f5` completed without conflict. Read the new settings backlog; it changes no Track C acceptance criterion. No tested resource or player folder is rewritten.

### Actual settings replay and zero boundary

`uv run python -u E:/OOTRemake/work/r8-shops-cs8c/smoke_replay.py` (completed external driver, subsequently removed):

- Replayed the first written spoiler's effective CS1 in another interpreter (`PYTHONHASHSEED=888`), no overrides: **exit0, 192 checks/23 spheres, all94 complete output files SHA256-identical**, including spoiler/note and all92 resources.
- Fresh full CLI seed7 with `--shuffle Chest Shop Scrub --shop-slots 0 --scrub-prices fixed --scrub-price 0`: **exit0, 168 checks/28 spheres**, no Shop check in the written placements and all four supported Scrub descriptions at price0.
- Read the saved partial-seed spoiler's actual three fields, selected shelves at10 and all four Scrub prices201. Read its actual play-note opening: unselected KF7 remains vanilla Deku Shield at the independent cheap price10, explicitly Buy before Tree entry. Selection does not erase fixed stock from the player's route.

Retained `settings-cli-proof.json`, both replay/zero CLI logs, the original partial CLI log, every fresh output folder, and `ingame/late-gift-proof.json`. Removed only the two completed session-created builder/smoke driver files, never an output/user/backup/game path. Original reusable trace reports remain external. The copied new-game launcher was read back from disk: bin executable only, update checks disabled, missing-exe hard stop, unique user/overlay/log; no batch executed.

### Current commit ledger on e3745f5

| Commit | Scope |
|---|---|
| `b6455d9` | item1 merchant-only shared gift patch |
| `b051367` | existing shared inverse-gift oracle |
| `feaf020` | item1 owned regressions/report/section34 |
| `eeb5181` | settings defaults only |
| `f611b46` | Settings fields only, no fill-algorithm edit |
| `1ed428e`, `c16b944` | CLI only |
| `b5c9ae3` | logical shelf selection metadata |
| `995438d` | prepare hook before pricing |
| `d0b61d2` | scrub fee/logic/metadata integration |
| `90ad1b3` | item2 owned synthetic/dump regressions, README and research |

Full gates run on this rebased source; later commits change this report only. Shared hashes were posted to `cs-r8` as cs8c. Section34 follows existing31; reviewer inserts32/33 before34 when those tracks merge, without placeholders or other-track edits.
