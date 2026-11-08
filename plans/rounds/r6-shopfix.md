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
