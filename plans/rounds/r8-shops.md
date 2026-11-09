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

### Historical commit ledger on e3745f5

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
| `ffea4bf` | rebased ledger and completed CLI replay evidence |
| `9cf5659` | native dynamic quote audit across all16 languages |
| `c1d60bb` | isolated full gift-delta oracle update |

At this historical checkpoint, production behavior was through `90ad1b3` and the generic oracle update was `c1d60bb`. Those hashes are superseded by the 15d4c70 ledger below. Section34 then followed31; the later integration preserves33/34/36 in numeric order.

Additional read-only quote audit (`scrub-quote-trace.txt`, `scrub-quote-tokens.txt`, `scrub-price-languages.txt`): Event289 uses `SellerMessageId`; all seven native calls' four distinct seller labels carry group2/type12 `SimpleShop_Price` in **all16 language archives**. Fixed fees therefore reuse the native dynamic price quote, rupee query and payment variable without writing language archives. Original item-flavour wording remains unchanged; no game text is copied into the repo.

## Full-gate integration correction

The first full chain completed: format **210 files**, lint clean, synthetic **662 passed/81 skipped** (582.10s), dump **79 passed/1 failed/663 deselected** (1401.08s). The sole failure printed `Npc_Kokiri_001_Shop_Child` changed indices `{16,57,109,110}` against the old generic intended set `{57,109,110}`: index16 is Event24, the deliberately extended initialized dispatch. It was not a runtime failure or a failing merchant semantic/inverse oracle.

Shared test-only `c1d60bb` permits Event24 only for the merchant's normalized once-gate. Removed the incidental assertion that every appended event name starts with `ClawshotGift`; no name golden/whitelist was substituted. Actual once-gate/late-dispatch semantics and complete inverse deltas remain independently covered.

Cause-aimed check: `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_gifts_dump.py -k each_changed_flow -q --tb=short --basetemp E:/OOTRemake/work/r8-shops-cs8c/gift-oracle-after-next`: **1 passed/4 deselected**, 8.91s. This is not a substitute for the fresh full four-command chain, which runs on the corrected test tree with `gate-corrected-{synthetic,dump}-next` basetemps. No production source change or relaxed oracle/goal/retry bound was made.

Reviewer CPU-safety steer acknowledged (2026-11-09): read main's updated `02-orchestration.md`. Track C's running gate chain is one serial pytest process, no multiprocessing/xdist pool or concurrent sweep; no additional smoke is running. Retain one worker regardless of game presence (the new maximum while Hookshot runs). No game or build was started.

## Pre-integration complete gates and handoff checkpoint

Fresh four-command chain on production through `90ad1b3` plus shared test-only `c1d60bb`:

| Full command | Observed result |
|---|---|
| `uv run ruff format --check` | **210 files already formatted** |
| `uv run ruff check` | **All checks passed** |
| `uv run pytest` | **662 passed, 81 skipped**, 381.64s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | **80 passed, 663 deselected**, 1110.38s |

Both pytest commands used only `PYTEST_ADDOPTS=--basetemp=E:/OOTRemake/work/r8-shops-cs8c/gate-corrected-{synthetic,dump}-next` to keep generated/decoded temporary data outside the repo. All743 tests were collected; no dump test skipped or test filtered except the prescribed marker. The generic whole-gift oracle, both merchant control-flow/inverse oracles, partial-shop field oracle, existing format/census/seed/hint/chronological/200-default-seed tests all pass. The single full-gate retry followed the printed missing-Event24 oracle cause and targeted passing correction; no unchanged failed rerun, widened retries or relaxed gameplay rule.

**Pre-integration checkpoint only:** these passes cover authorized `e3745f5`, not the subsequently requested B/E integration (corrected target `15d4c70`). All requested implementation, native-output smoke and CS1 replay work is complete; the new rebase and four fresh full gates remain mandatory before readiness. No merge, push, stash, dependency edit, game/batch/window/build or played-output rewrite.

### Left for Claude / Kareem

- **Kareem:** run `E:/OOTRemake/work/r8-shops-cs8c/ingame/Test - shopkeeper-after-gohma-next.bat` after quitting the current game; follow adjacent `late-gift-check.md`. Skip the merchant until after Gohma (optionally also Zelda before first talk), receive Boomerang with the shield equipped, test normal shopping and repeat/Save-Continue, and supply overlay log. No game acceptance is invented; **D28's non-progression restriction remains**.
- **Claude:** review the isolated shared-file commits. Section34 is integrated between33/36 below; future32/35 remain their tracks' content. Questions about first-N versus seeded shelf membership and pricing beyond the four supported shuffled scrub families remain provisional product choices above, not expanded policy.
- Controlled player output, isolated unrun launcher/checklist, three CLI outputs, read-only native trace reports and JSON/log proofs remain outside the repository. Only the two completed temporary driver scripts were removed; no game, save backup, existing user/seed/output folder or other agent's file was deleted.

Reviewer initially supplied `536b4a5` for the B/E merge, then corrected it to **`15d4c70`**. The first rebase contained only the new CPU rule (B/E reports were absent); no B/E acceptance was inferred. The corrected exact-target rebase is documented below; pre-integration results remain historical.

## Corrected B/E integration onto 15d4c70

The reviewer-authorized `git rebase 15d4c70` is complete. Only conflicts were additive `03-game-data.md` appendices: keep B's entire33, insert C's entire34 (including partial-price and dynamic-quote subsections), then keep E's entire36. Numeric order is **31,33,34,36** with no invented32/35. README, settings defaults, CLI and source hooks auto-merged; no producer code was discarded. Read B/E reports, the new Freestanding pipeline/CLI contract and the merged CPU rule.

### Current branch commits

| Commit | Scope |
|---|---|
| `54fa4b8` | shared gifts.py merchant dispatch only |
| `10ce0f8` | existing merchant inverse oracle |
| `79cfc4f` | item1 owned tests/report/section34 |
| `c4529a0` | shared settings defaults only |
| `20fb16c` | Settings fields only, no fill-algorithm change |
| `ea2f1c6`, `c78d87e` | shared CLI only |
| `02ddae1` | world.shops logical shelf selection |
| `15bff35` | prepare hook before effective pricing |
| `27e18ae` | scrub fees/wallets/presentation metadata |
| `25906ca` | item2 owned regressions, README and section34 |
| `841df27` | prior CLI replay/ledger evidence |
| `2e41913` | all-language native quote evidence |
| `a725a51` | shared generic gift-oracle correction |
| `2383e5f` | completed pre-integration gates and new integration instruction |

Fresh real CLI smoke used seed7 with Chest+Shop+Scrub,3 shelves/affordable and fixed201 fees, into absent `seed15d-partial-next`, chained **serially** before all four complete gates. Freestanding remains available in the CLI/pipeline but was not silently enabled in this unchanged Track C scenario. No extra worker, sweep, new launcher or player-output rewrite.

### Completed integrated acceptance

Actual CLI: **exit0, 192 shuffled checks, 23 spheres, 92 resources** plus spoiler/note. Read the written settings and all four Scrub descriptions:3 slots, fixed201, exactly the requested shuffled kinds. Independent whole-folder SHA256 comparison: **all94 integrated files equal the pre-integration partial seed byte-for-byte** (`integrated-15d-proof.json`). The earlier separate-interpreter CS1 replay and zero-slot/free-scrub proof remain recorded above; no changed scope/seed/settings or reroll was used for this fresh integration.

| Complete command on 15d4c70 integration | Observed result |
|---|---|
| `uv run ruff format --check` | **216 files already formatted** |
| `uv run ruff check` | **All checks passed** |
| `uv run pytest` | **703 passed, 84 skipped**, 311.38s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | **83 passed, 704 deselected**, 707.42s |

Both pytest invocations used only external `PYTEST_ADDOPTS=--basetemp=E:/OOTRemake/work/r8-shops-cs8c/gate15d-{synthetic,dump}-next`. **787 tests collected**, all selected dump tests passed, no dump skip, no filter beyond the required marker. Includes incoming B get-item flow and E floor/palette oracles, current Gift/Shop/Scrub integration and the new late-window/partial-price tests. The entire serial smoke-plus-gates chain completed successfully in1051.46s; no source/test edit occurred after its start, no failed integration rerun.

**Track C ready for review on `r8/shops`, rebased onto corrected target `15d4c70`.** Both numbered items and all reachable acceptance work are complete. This final commit changes the round report only; its actual head is posted with the full handoff. Commit-by-commit current ledger is above; no merge, push, stash or dependency change.

The pending-D28 acceptance recorded above is **superseded by Kareem's 2026-11-09 result and the follow-up below**. First-N shelf selection and fixed-fee scope/default remain the explicitly recorded provisional product choices. No game/launcher/window was started by this agent and no existing player seed/user/backup/output was rewritten or deleted.

## Follow-up: D28 lifted for the persistent shuffled gift

**Kareem, 2026-11-09, reported via Claude:** a copy of his ranch save already had Forest stone, Zelda's Lullaby and Deku Shield and had never talked to the merchant. With this track's `shopkeeper-after-gohma-next` overlay, the merchant gave Boomerang and did not offer it again. This is the requested played confirmation of the extended window after Gohma and the castle. No new overlay-log, shopping or Save/Continue observation is invented. Claude explicitly requested the progression-policy cutover on `r8/shops`; **D28 is lifted for the shuffled check**, superseding earlier pending/restricted status in this chronological report.

`KF Shopkeeper Gift` now uses ordinary `NPC`, not `Missable`, retaining the existing data rule `is_child and at('KF Outside Deku Tree', is_child)` with no story cutoffs. No new logic branch or fill-algorithm exception: progression follows existing NPC placement policy. Removed obsolete Missable gift expansion; Gift and expanded-NPC effective-CS1 setup both add the check and pair it with the already-verified window/once patch. Vanilla event/rule/flow remain unchanged when unshuffled. Child/tree visit, Mido bootstrap protection and saved once-gate remain. Provenance and player directions now state the verified late window instead of incorrectly requiring an early pickup. No decisions.md edit; Claude records the final D28 decision.

Failing-before regression: forcing required Boomerang into the merchant before a Boomerang-locked chest failed with `no reachable location for 'Boomerang' (1 allowed of 1 left; 0 other items left to place)`. Corrected classification makes that seed beatable in one attempt, with gift then chest spheres. Removed the obsolete twenty-seed non-progression-policy test rather than re-pinning it. Initial late-state fixture wrongly used `Search.holds` on externally supplied event counts; printed raw counts versus `_held` identified the fixture error. Replaced it with actual child reachability that earns Gohma and, with Weird Egg, the castle's `Time Flows` event before checking the gift.

Targeted verification: `uv run pytest tests/test_gifts_shopkeeper.py tests/test_shopkeeper_window.py -q --tb=short` **19 passed**. `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_shopkeeper_window_dump.py tests/test_gifts_shopkeeper_dump.py -q --tb=short --basetemp E:/OOTRemake/work/r8-shops-cs8c/d28-focused-next` **3 passed**. The new real-dump test checks both public Gift and effective-CS1 replay: progression is allowed, the actual transformed merchant grants Boomerang after both story flags with a shield equipped, then saved completion stops another offer.

Non-test runtime smoke: actual public `uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 7 --shuffle Chest Gift --out E:/OOTRemake/work/r8-shops-cs8c/d28-gift-seed7-next` **exit0, 214 shuffled checks, 25 spheres, 125 resources**, 73.95s. This fresh output naturally places **Stone of Agony (progression)** at `KF Shopkeeper Gift`. An independent runtime read of the written spoiler and compressed merchant flow confirms `NPC`, the positive child/tree rule, and **both Event116/117 grant `Item_AgonyStone`**, matching the assigned actor (`d28-runtime-proof.json`). No custom placement restriction, seed sweep, reroll, relaxed guarantee or raised retry limit was used.

All four fresh full gates completed serially with external `d28-{synthetic,dump}-next` basetemps. No source/test edit after their start; game, save copies and all earlier generated/player output remain untouched.

| Follow-up complete command | Observed result |
|---|---|
| `uv run ruff format --check` | **216 files already formatted** |
| `uv run ruff check` | **All checks passed** |
| `uv run pytest` | **705 passed, 85 skipped**, 366.68s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | **84 passed, 706 deselected**, 775.37s |

**790 tests collected**, all84 selected dump tests passed, none skipped; only the prescribed dump marker filters the full dump invocation. No full-gate failure/retry, omitted oracle, new dependency or test weakening. Retains incoming B/E gates, default200-seed and Gift/CS1 real-writer coverage, vanilla merchant/equipment/free-shield behavior and native Mido/age guards. Removed only the superseded D28 non-progression expectation.

Follow-up ready for review as one scoped commit on `r8/shops` after `c3ab818`; exact head posted to `cs-r8`. Changes: merchant conversion/expansion in gifts.py, three merchant test files, merchant-only provenance/directions in two data files, section34 and this round report. No other gift family or fill algorithm changed. **No remaining D28 gameplay blocker:** Kareem's reported late grant/no-repeat result is accepted, per Claude's instruction; no extra game result is claimed. No merge, push, stash, launcher execution or existing-output rewrite.
