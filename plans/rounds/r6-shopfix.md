# Round 6, Track E: Castle Town shop crash (cs6e)

Branch `r6/shopfix`. Dump and backup saves read-only. No game, launcher, GUI, Hookshot build or terminal-control command run. Required AGENTS rules, README, plans 00–04, decisions and all five round-5 reports read before edits, including round 6's opening and round 5's shared-file rules. No dependency change. Price code remains cs6b's.

## Item 1: field/reference audit

External reproducible probes and decoded reports: `E:/OOTRemake/work/r6-shopfix/` (`audit_packs.py`, `pack-audit.json`, `probe_references.py`, `probe_allocations.py`, `allocations.json`). All twelve seller packs written by the original `seed-shop-7` were compared against the read-only dump. Each changes exactly one ShopParam member; all other members and the member-name set are unchanged. Field differences are only `GoodsList[index].Actor` and `PriceOffset`. Stock, release gates, conditional prices, parent references and ShopRef paths are unchanged. Every changed sale actor has its own native actor pack; goods actors are external identities, not missing members of the seller pack (the originals also omit them).

Original and rewritten SARC headers, hash multipliers and every node's stored name hash were checked. All changed ShopRef paths still resolve inside their seller pack. Original ShopParam BYML reads/writes byte-identically. No new component reference is introduced outside GoodsList actors. Shared/base references already absent from the original seller packs are not classified as new dangling references.

The ten changed shop Banc files remove 28 quantity-board actors in total; the Market file removes four. Their Hashes are absent from remaining links, AiGroups, FarDeleteGroups and SimultaneousGroups. No group is left empty. The round-5 `dc037c8` membership removal is not the observed broken reference.

### Leading cause: embedded resource allocation, not the enclosing pack

The writer raises entries for changed outer `.pack` files, but never the changed members' own resource-table entries. The same embedded component path can occur in multiple seller packs; its allocation must cover the largest changed copy.

| Changed ShopParam owner | Old bytes | New bytes (child / adult) | Existing member entry | Rounded growth |
|---|---:|---:|---:|---:|
| Market Bazaar, Hylia 018 | 1348 | 1412 / separate adult member 1392 | 8352 | 64 |
| Market/Kakariko Potion, Hylia 020 | 1088 | 1156 / 1184 | 7984 | 96 |
| Market Bombchu, Hylia 021 | 956 | 960 | 7856 | 0 |
| Zora | 960 | 1028 / 1028 | 7856 | 96 |
| Kokiri full stock | 1156 | 1164 / 1164 | 8080 | 0 |

The Kokiri full-stock change stays in its original 32-byte bucket; Market Potion does not. In the supplied crash log, line 24488 is the GeneralFormatAsync guest-null write, x6/x7 encode `Component/ShopPa`, and `[x19+0x080]` is `000004a000000484`: **0x484 = 1156**, exactly the changed child Potion ShopParam length, and **0x4a0 = 1184**, its rounded length. This identifies the component under construction. **[INFERENCE]** Its unchanged embedded allocation causes the null allocation/parser destination; gameplay bisects must confirm this rather than treating a parse round trip as runtime proof.

The inherited component's exact runtime-allocation formula is not yet claimed. Controlled correction will retain the original parsed-structure overhead and add only the verified rounded serialized growth for these shape-preserving Actor/PriceOffset edits. Conditional offsets and GoodsList cardinality stay unchanged. No generic `.bgyml` formula is assumed.

### Checks / diagnostics

- `uv run python E:/OOTRemake/work/r6-shopfix/audit_packs.py`: completed; twelve packs, one member each, full field diffs saved externally.
- `uv run python E:/OOTRemake/work/r6-shopfix/probe_references.py`: completed; archive hashes, ShopRef resolution, board/group links and original/output size entries printed.
- `uv run python E:/OOTRemake/work/r6-shopfix/probe_allocations.py`: completed; twelve nested allocation comparisons and 24 read-only backup saves inspected (all child). Initial save-string probe used the wrong section indices; printed empty results are not proof of scene absence. Correct scene lookup follows for item 2.
- `xd://lsp` references: no Python language server available. Initial descriptive lookup at `src/clawshot/save` printed path-not-found; filename listing located `src/clawshot/save.py`. No unchanged retry.

**Kareem: compare the isolated Potion pack and the same bytes with only embedded allocations corrected; does Castle Town load, and can its shop be entered?** Exact launchers/check order follow in item 2. No success is inferred before your observation.

### Shared-file request

The required correction needs the common writer to include embedded ShopParam allocations in its single size-table transaction, after all price/sale transforms compose. Proposed isolated `patch/write.py` commit: invoke a shop-owned allocation updater on final actor-pack bytes; take the maximum across all copies, never lower existing entries, and emit the table if a nested entry changed even when no outer entry grew. Keep all price policy in cs6b's code. This avoids a forbidden second size-table transform or writing loose copies of packed game resources.

## Item 2: isolated save-copy bisects

Built eight external overlays with independent users and copied, statically checked launchers under `E:/OOTRemake/work/r6-shopfix/`. `checklist.md` gives the short route and `bisect-manifest.json` records files and allocation deltas. Copied the corrected `r5-gifts/ingame/Test - talon-boomerang.bat` template, retaining **only** `E:\Games\Hookshot\bin\hookshot.exe`, `HOOKSHOT_NO_UPDATE_CHECK=1`, missing-exe stop and explicit `--user`. No batch was executed, including dry-run mode.

Starting save: byte-identical copies of `2026-11-07_llr-tower-before-pickup`, known child ranch checkpoint (manual slot 01); leave ranch, cross north Hyrule Field to Castle Town, Sun's Song if night. This is closer than the new Dodongo snapshot. Read-only inspection confirmed all 24 backup slots are child; the newer snapshot's saved scene is `DodongoCavern`, while older manual saves use an empty reserved scene string, so the known ranch provenance is used rather than inventing a scene from that empty field.

| Suffix after `Test - ` | Controlled overlay |
|---|---|
| `01-potion-alone` | Suspect Market Potion pack alone + outer-size table |
| `02-potion-allocation-fixed` | Identical pack bytes; only member allocation 7984 -> 8080 |
| `03-bazaar-alone` | Market Bazaar pack alone + outer-size table |
| `04-bombchu-alone` | Market Bombchu pack alone + outer-size table |
| `05-market-banc-alone` | Market child Static only + outer-size table |
| `06-market-all` | Three suspect Market packs + Market Static + outer-size table |
| `07-market-allocations-fixed` | Identical 06 packs/Banc; only Bazaar +64 and Potion +96 embedded entries raised |
| `08-seed-potion-reverted` | All original seed-shop-7 resources, but Potion child pack restored byte-identically from dump |

**Kareem: try 07 first: enter town, then Bazaar and Potion Shop, open their menus, quit.** The hypothesis predicts a successful load with changed native shelves. If successful, 02 isolates the same correction to one pack (shelves remain vanilla). Deliberate crash controls 01/06 are optional only if Claude needs confirmation; do not replay eight runs unnecessarily. Logs are inside each `user-<suffix>/hookshot_log.txt`; look for the table and selected files `from the overlay`. Success remains unobserved.

`uv run python E:/OOTRemake/work/r6-shopfix/build_bisects.py` completed: all eight overlays decompressed/parsed; eight user copies matched every source save byte; paired 01/02 and 06/07 pack/Banc bytes matched; SHA256 of all backup files and original seed files unchanged. Statically checked every launcher for bin executable, updater suppression, missing-exe stop, isolated user/log/overlay and no work-build fallback. No original seed/user or backup was changed. Full repository gates will run on the completed item-3 fix before code readiness is posted.

## Item 3: permanent nested-size correction and exact 7b continuation

`shops.member_growth` computes positive 32-byte-rounded raw growth only for changed ShopParams whose parsed structure cannot grow: same GoodsList cardinality, unchanged other component fields, row edits limited to Actor/PriceOffset and conditional-price removal. Unsupported structural changes fail rather than borrow a guessed allocation formula. The common writer applies this to final composed actor-pack bytes, caches each original embedded entry once and takes the maximum across copies, never sums growth. A nested-only raise emits the size table even when all outer entries already fit. This leaves cs6b's price policy untouched and covers its final composed bytes.

Measured all nine unique original ShopParams (including masks): rounded raw bytes +6896, with +80 for Bazaar's one conditional-price element. The implementation preserves each original overhead, including extra conditional capacity after a discount is removed; it does not lower entries or establish a generic `.bgyml` formula.

- Before fix, `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_shops_dump.py -k embedded --basetemp E:/OOTRemake/work/r6-shopfix/pytest-before -q`: **1 failed, 5 deselected**. Exact printed payload: old/new bytes **1088/1156**, stale entry **7984**, required **8080**.
- Cause-aimed rerun after fix, same selected test with `--basetemp .../pytest-after`: **1 passed, 5 deselected**.
- `uv run pytest tests/test_shop_allocations.py tests/test_shops.py -q`: **9 passed**. Shared-path copies in both orderings use max not sum, roomy outer entries still emit a nested-only table, unrelated entries stay unchanged, parsed-structure growth is refused.
- Scoped `ruff format` and `ruff check` on the four changed Python files passed.
- `uv run python E:/OOTRemake/work/r6-shopfix/build_seed_7b.py`: real whole-world generator, writer and fresh gated-return search passed: **228 shuffled checks, 26 spheres, 77 resources**. `seed-7b-verification.json` records the result.

**7b's spoiler equals 7's byte-for-byte**, not just its placement dictionary. Output is `E:/OOTRemake/work/r5-seed/seed-shop-7b/`. All 76 non-table overlay resources also equal 7's byte-for-byte. Exactly three existing embedded entries change: Bazaar **8352 -> 8416**, Potion **7984 -> 8080**, Zora **7856 -> 7952**. All changed components were read back and their allocation checked, and the original seed folder's SHA256 set stayed unchanged.

`E:/OOTRemake/work/r5-seed/Play shop seed 7b.bat` is copied/adapted from the mandated corrected save-copy template, with bin executable, updater suppression and missing-exe stop. It is **unrun**. When Kareem runs it after quitting, it reads his original seed-7 save as the source of a one-time independent `user-seed-shop-7b` copy, never writes/deletes the source, then continues that copy with 7b's overlay and its own log. The agent has not read or copied the active original user's saves. No fresh new game or vanilla ranch save is substituted for his seed progress.

Reviewer added item 4: future seeds keep every `Buy ...` refill at Shop destinations; ammo/container metadata is reported without changing chest ammo logic. Reviewer explicitly corrected item 4(c): **7b stays size-fix-only**, so its existing chest `Buy ...` items remain; a newly filled seed under the restriction is a restart, not a compatible continuation.

### Item 3 in-game confirmation (Kareem via Claude, 2026-11-08)

Kareem ran **07-market-allocations-fixed**: Castle Town loaded without crashing; Bazaar and Potion shelves were randomized with prices/descriptions, and the log shows the overlay. The nested size correction is confirmed in game. He subsequently bought Bombchus at Bazaar, and a Deku Stick and a heart once he could hold them. The initial refusals were native can't-hold checks, not another shop patch failure. Reviewer cancelled the extra buyable experiment; none was built or run.

## Item 4(a): future seeds keep refills in shops

Effective `Settings.item_location_types` now holds **every** `Buy ...` item to `("Shop",)` when Shop is shuffled, through `prepare`; existing non-refill restrictions remain. `allowed()` is unchanged. With Shop vanilla the added policy does nothing. Physical shields/tunics and actual chest-ammo items are not classified as Buy refills.

The fill needs the matching capacity invariant: remaining Shop destinations must cover remaining shop-only refills. Both progression and filler retain the old native-Shop preference only while spare slots exist; flexible native items prefer chests at the refill reserve. This preserves room for both shop-only refills and non-display chest filler. Held filler still precedes unrestricted filler when Shop merges them (same prerequisite correction as cs6b).

Evidence:

- Boundary regression fails before: `allowed(..., "Deku Tree Basement Chest", "Buy Bombs (10)")` was true. It passes after, preserves physical-shield chest placement and other held-item settings, and leaves vanilla-Shop settings unchanged.
- Synthetic exact-capacity normal and progression cases, plus a spare-shop/non-display-filler case, each cover 20 seeds with `attempts=1`. Before the fixes they printed `Buy Bombs (10)` unplaced, or `Buy Bombs (10), Rupee` unplaced. After: **4 focused tests passed**.
- First whole-world diagnostic's final error was Fire small-key placement, also seen with legacy settings. Instrumentation printed each bounded attempt: the usable candidate had **24 Shop slots for 36 remaining refills**, after flexible progression consumed shelves. An all-chest preference overcorrected and stranded chest-only filler. Final implementation reserves the **exact remaining count**, not every shop. No retries, key rules or oracle requirements were changed.
- An early full-spec `generate` test omitted remake census vanilla overrides; replaced that invalid test setup with synthetic boundary cases. Actual public CLI below uses `make_seed` and the real census pool.
- A shell-backend timeout produced no test output; process diagnostics showed no surviving shopfix pytest. A direct scenario printed the exact unplaced-refill cause before the aimed fix. A later metadata diagnostic tried `Location.dungeon`; printed AttributeError, so no dungeon inference was made from that field (dungeon belongs to the region).
- Final real CLI: `uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 7 --shuffle Chest Shop --out E:/OOTRemake/work/r6-shopfix/new-seed-refills`: **228 checks, 25 spheres, 80 resources**, exit 0. Parsed spoiler: **59 Buy refills, zero outside Shop**. **127 placements differ** from old seed 7. This is smoke output for new-seed behavior, not Kareem's continuation.
- 7b's spoiler was checked again byte-identical to 7's after this smoke. **Never replace 7b with the new refill-restricted fill.**

Shared changes are isolated per round rules: `generate/__init__.py` effective-settings hook and `generate/fill.py` capacity/priority correction. Reviewer authorized rebase onto main **65bbcf7** at this clean checkpoint; preserve cs6b's canonical pricing, forest defaults, settings string and held priority, then run all four gates.

## Item 4(b): ammo/container audit; rule proposed, not applied

The full family/count/container table is in section 24, from `PouchActorInfo` `BundleActor -> SmallBagActor` and bag expansion/full-stock fields. External `audit_ammo.py` resolved every selected target and wrote `ammo-container-audit.json`; no decoded tree entered the repository.

- Native and shop bombs share `Item_Bomb -> Item_BombBag_Small` (20); Bombchus share the same bag through `Item_Bombchu`. The bag expands both types, stock-max on get; Bombchu refill-on-bag is conditional on its IsGet.
- Native/shop arrows share `Item_Arrow_Normal -> Item_Quiver_Small` (30), not Bow; shop seeds share `Item_DekuSeed -> Item_BulletBag_Small` (30), not Slingshot.
- Nut/stick rows explicitly allow automatic small-bag acquisition; capacities 20 nuts /10 sticks. Chest bundle counts are 3 nuts, 3 sticks, 5 bombs, 5 Bombchus, arrows 3/5/10, not necessarily the old OoTR names' quantities.
- Bomb/arrow/seed automatic container behavior for every entry/path remains **inferred from the shared get-event metadata**, not separately certified. Only Kareem's Shop Bombs(10) chest case is observed: old Basement placement grants Bomb Bag +20 bombs and sets `IsGet.Item_BombBag_Small` without a pre-existing bag.

**Kareem: proposed rule for confirmed native chest bomb/Bombchu packs: the search should count the Bomb Bag they actually grant, or those packs must stay at checks reachable with an independently held Bomb Bag. Prefer counting the real grant after the family check; otherwise a hidden early bag changes D20's earliest-pull route.** Do not add Bow/Slingshot ownership just because an arrow/seed pack names a quiver/bullet bag. No ammo aliases, actors, chest restrictions or world logic were changed for this finding.

## Item 4(c): 7b is not regenerated under new defaults/policy

Reviewer correction followed: **7b's spoiler is byte-for-byte equal to 7's**. It was built before the new-seed restriction and before the settings rebase. Its preserved placement bytes include the old Buy refills in chests, including the Basement Bombs(10); no claim that 7b obeys the new-seed policy. The refill-restricted new smoke differs at 127 checks and would require a restart. 7b is the size-fix-only continuation, not that smoke and not a seed with main's new forest/price defaults.

## Authorized rebase

Rebase onto **65bbcf7** completed. `prepare` keeps both the canonical price transformation and the new Buy-held map, plus cs6b's forest/settings behavior. The fill keeps main's held-priority sort and the exact remaining-refill reserve; no duplicate competing policy path. Sections already present remain in numeric order (19,21,22,23,24; track A's section20 has not been merged here). No merge/push/stash or other-track worktree edit.

Post-rebase scoped proof: `uv run python .../check_shop_logic.py` and `uv run pytest tests/test_shop_logic.py tests/test_shop_allocations.py -q`: **26 live capability checks; 32 tests passed**. The capability diagnostic initially expected Buy Bombchu + Bomb Bag to satisfy `has_bombchus` under defaults; printed `free_bombchu_drops=True` and helper source show that mode needs an actual Bombchu item. Corrected only the diagnostic: bought access supplies `can_refill_bombchus`; with free drops off, Bomb Bag + bought access supplies `has_bombchus`. Default mode under-credits Buy-only first acquisition conservatively. No helper/rule was changed to make the assertion pass.

## Item 5: purchase refusals and logic check

Section 24 now lists every native sale family: condition, explicit flow query/flag and refusal message ID, with paraphrases only (no copied game text). External traces: `shop_conditions.py`, `availability_trace.py`, `DisplayShop-conditions.txt`, `refusal_messages.py`, `refusal-messages.json`; the latter decodes only the selected local US-English messages outside the repository.

Evidence: `DisplayShop:SelectItem_CheckAvailable` Event318 branches to bullet bag IsGet (Event299), quiver IsGet (Event320), Fire stone quest completed (Event327), or empty bottle (Event325), then native buy/hold checks. The hesitant price preambles are `NotAvailableTalk` merchant `Shop_01_02_1/2/3`; the observed Potion line is `_3`. Capacity/duplicate/age/stock follow-ups are named in the table. Pouch metadata supplies heart/MP recovery, ammo counts/capacity and equipment identity, not an invented engine query implementation.

Kareem's successful Bazaar Bombchus and later Deku Stick/heart purchases settle the suspected malfunction: he needed stock/health room, not a rewritten purchase flow. **Extra buyable test cancelled by reviewer; no new overlay or launcher for it.**

Logic conclusions:

- Actual shield ownership satisfies the capability; inability to buy an already-held shield/tunic is not a missing progression item.
- Tunic destinations retain adult-accessible catalog restrictions; `can_use` classifies both as adult items. Canonical effective prices/wallet rules survive the rebase.
- Bottle-refill helpers require a usable bottle; first Ruto's Letter is excluded, a milk bottle can be emptied. Empty/currently full consumable stock is deliberately not a permanent progression flag.
- Bombchu purchase succeeds without a new invented Bomb Bag gate. Existing default free-drop logic conservatively under-credits Buy-only first acquisition; off-mode requires Bomb Bag plus refill access. These are reported, not silently broadened.

**Claude/Kareem: selected Blue Fire at either Potion merchant runs an acquired-Blue-Fire gate (Event108), but current catalog rules attach that condition only to the original two slot-5 checks. If Blue Fire moves to another Potion slot, this item-following condition is missing from the static logic. Proposed conservative correction: restrict Buy Blue Fire to already-gated destinations, or add an item-dependent purchase rule; do not remove the native flag query.** Other merchant types bypass the Potion-specific dialogue branch. Posted on cs-r6; kept this pre-existing audit finding explicit, without unrequested logic policy changes.

### Integrated runtime smoke after rebase

`uv run python -u E:/OOTRemake/work/r6-shopfix/smoke_integrated.py`: two real CLI processes, default forest/cheap-shield/settings-string behavior from **65bbcf7**, new refill policy and nested sizing. Both exit **0**, **228 checks /25 spheres**. Replaying the emitted settings string with a different hash seed gives **81/81 byte-identical canonical files**. **59 Buy refills**, all at Shop; **12 changed packed ShopParam copies** checked against original member allocation plus rounded growth. No launches.

The same smoke rechecked existing 7b: spoiler equal to old7, same resource paths, **only the size table differs**. It never rewrites 7b or the old seed/user. Report `integrated-verification.json` and CLI transcripts stay outside the repository. Full four-gate chain is running on this integrated code; final results follow.

## Rebased commit ledger

Base **a81faf9**, branch `r6/shopfix`; previous `65bbcf7`/`fcb265f` checkpoint and earlier hashes are superseded by the requested second rebase. Section12 play findings remain before section24; D25 is present in `plans/decisions.md`.

| Commit | Scope |
|---|---|
| `ed6ce49` | item1 field/reference/allocation diagnosis |
| `da417a8` | item2 eight isolated bisects and save/launcher evidence |
| `021ac67` | item3 shop-owned sizing helper, regressions, section24 and exact 7b proof |
| `ed73737` | isolated `patch/write.py` embedded-size transaction hook |
| `c502854` | isolated effective `Settings.item_location_types` Buy-to-Shop hook |
| `d341f33` | isolated fill capacity reservation, retaining main's held priority |
| `9f19b10` | item4(a) failing-before/passing-after boundary tests and confirmed game result |
| `c53ecbc` | initial item4(b/c) ammo audit and proposed rule, unchanged 7b contract |
| `ba6bb35` | native refusal table, purchase observations and logic audit |
| `7e0e77c` | first rebased ledger and smoke cleanup |
| `70696f5` | pre-D25 full integration gates and handoff |
| `fa358ae` | isolated D25 `generate/fill.py` restriction plus synthetic/real-seed regressions |

## Cleanup

Removed only this session's completed three future-seed/replay smoke folders, both targeted and both full-gate pytest basetemps, and throwaway generation/diagnostic builders after recording their evidence. Requested eight bisect overlays and all their users remain, including Kareem's played07 user; 7b and its launcher remain. Read-only audit reproducers, decoded local audit reports, CLI transcripts and verification JSON remain outside the repository. No source dump, backup, original seed/user, junction, other track file or dependency was removed or changed.

## Pre-D25 full integration gates

Run once on the integrated code after rebase, with pytest temporary output explicitly outside the repository:

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | **171 files already formatted** |
| `uv run ruff check` | **All checks passed** |
| `uv run pytest --basetemp E:/OOTRemake/work/r6-shopfix/pytest-full-synthetic` | **468 passed, 66 skipped**, 527.46 s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump --basetemp E:/OOTRemake/work/r6-shopfix/pytest-full-dump` | **65 passed, 469 deselected**, 594.64 s |

All four full gates passed on the integrated code; no gate was narrowed or rerun unchanged. The synthetic gate covers all new Shop destination/capacity tests and inherited settings/age/gift/scrub tests; the dump gate includes the real failing-before/passing-after embedded Potion allocation oracle. No failing check remains.

## Pre-D25 handoff

- **Crash fixed and confirmed in game:** 07 loads town, randomized shelves/prices/descriptions and successful Bombchu/stick/heart purchases; overlay log observed by Kareem.
- **Continuation:** `E:/OOTRemake/work/r5-seed/seed-shop-7b/`, launcher `E:/OOTRemake/work/r5-seed/Play shop seed 7b.bat`. Quit before first launch; the human-run launcher makes its separate save copy once. **7b spoiler equals 7 byte-for-byte; only the size table differs among resources.** It does not include new refill placement rules, price defaults or forest defaults.
- **New seeds:** every Buy refill stays at Shop; exact slot reservation prevents both refill and chest-only-filler starvation. Integrated string replay: 81 identical canonical files; 59 Buy refills, none in chests.
- **Reports:** section24 has ammo/container and purchase-condition/refusal-ID tables; this file has scoped commit ledger, failure payloads, smoke proof and all four complete gate results.
- **Review follow-up:** the ammo-container decision below is now D25 (require the bag), not an open product choice. The Blue Fire/Potion gate correction remains explicitly deferred by reviewer; extra buyable test remains cancelled.

No game/launcher/window started by the agent; no merge, push, stash, dependency edit, or write under the game dump/backups/original seed/user. Final documentation commit hash is posted in the handoff thread and chat.

## D25 follow-up: require the Bomb Bag

Reviewer relayed Kareem's selected default, then requested rebase onto **a81faf9** (r6/play merged plus D25).
Committed source/tests before rebasing at the clean point; rebase completed without conflict. Shared-file change was
posted before editing. **`fa358ae` changes only `generate/fill.py`, `tests/test_generate.py`, `tests/test_shops_dump.py`.**

### Restriction

`_fill_bomb_ammo` runs after the existing adult-return kit stage, before dungeon/progression/filler stages.
For every native `Bombs (N)` / `Bombchus (N)` in the actual pool, it computes eligible destinations once from a
maximal search holding all other actual pool/fixed items, including their duplicate counts. It excludes every
logical Bomb Bag source (canonical and aliases), every native/Buy bomb or Bombchu pack, and excluded starting items.
A destination is eligible only if this inventory cannot access it. Existing assumed fill then places the constrained
ammo there, preserving actual reachability and existing restrictions; unconstrained filler cannot steal its slots.
No advanced bag-counting alias or sale/price/Blue Fire rule changed; Buy refills remain held to Shop.

### Failure payloads and targeted checks

- Before fix, the synthetic seed1 put `Bombs (5)` at open `Early Hammer`, with `Hammer` behind `Bag Required`.
  The maximal no-bag inventory could reach that pickup. The Hammer-bypass alternative is intentionally not safe.
- The first dump test's incidental count guess was wrong: printed counts showed **three**, not one, native Bombchu
  packs. Removed that unrelated count assertion rather than repinning an incidental value.
- Before fix, real Chest seed7's early placements included bombs at **KF Kokiri Sword Chest** and
  **Graveyard Shield Grave Chest**; all six native ammo rows were printed in the failing payload.
- After fix, the first dump oracle still held unmapped N64-derived counts: diagnostic output showed
  **five `Bombs (10)` and three `Bombchus (10)`**. These reopened routes despite a nominal pack-free inventory.
  Corrected the oracle to exclude all six named ammo counts plus the unmapped Buy variant, not merely mapped actors.
  The actor-derived set independently identifies all actual native/Shop bag-granting packs.
- Synthetic: `uv run pytest tests/test_generate.py -k 'ammo or bag_requirement' -q`:
  **8 passed, 11 deselected**. Six ammo/count/class combinations over20 seeds each; alias/pack-alternative world
  over20 seeds, starting-source exclusion, and rejection when every candidate has a Hammer bypass.
- Real dump: `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest tests/test_shops_dump.py -k real_seed_ammo -q
  --basetemp E:/OOTRemake/work/r6-shopfix/pytest-d25-complete-sources`:
  **2 passed, 6 deselected**, 18.76 s (Chest-only and Chest+Shop).

### Actual CLI smoke on a81faf9 + fa358ae

`uv run python -u E:/OOTRemake/work/r6-shopfix/smoke_d25.py` ran two actual CLI processes successfully:
first seed7 Chest+Shop, then its complete `CS1` string; `PYTHONHASHSEED`51 versus52. **78/78 files byte-identical**.
All **six** native packs (three `Item_BombBundle_Small`, three `Item_BombchuBundle_Small`) were inaccessible
to the maximal no-bag/no-pack search. **59 Buy refills, zero outside Shop**. Independent reconstruction of the
written placement passed beatability. Local transcripts: `d25-cli-0.txt`, `d25-cli-1.txt`; result:
`E:/OOTRemake/work/r6-shopfix/d25-verification.json`. No game or launcher started; 7b was not regenerated.

**Blue Fire gap, proposed fix only:** selected Blue Fire at either Potion merchant requires prior acquired Blue Fire,
but the logic gates only its original slots; restrict `Buy Blue Fire` to already-gated Potion slots or non-Potion
merchants. **Unchanged as requested.**

### Rebased D25 full gates

The complete four-command chain is running on this rebased implementation, with temporary output outside the repo.
Final results and final documentation head will be recorded below before the ready handoff.

After smoke proof, removed only the two session-created `d25-seed-*` overlays and the throwaway
`smoke_d25.py` / `diagnose_d25_sources.py` scripts. The four targeted `pytest-d25-*` basetemps were never
materialized (those selected tests do not request temporary paths). Retained both CLI transcripts and
`d25-verification.json`; original seed7/7b, every requested bisect/user and all read-only audits remain untouched.
The active full-gate temporary directory is retained until completion.
