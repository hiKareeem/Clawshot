# Round 8, Track C: shops (cs8c)

Branch `r8/shops`. Required AGENTS, README, plans 00–04, decisions and every round-6/7 report read before changes; Round 8 opening and inherited shared-file rules apply. Dump and save backups read-only. No game, batch, GUI, build or terminal-control command is run. Research and generated resources stay under `E:/OOTRemake/work/r8-shops-cs8c/`. No dependency change, merge, push, stash or unauthorized rebase.

## Item 1: persistent shuffled shopkeeper offer

Actual merchant flow printed to external `merchant-flow.txt` using the repository EVFL reader. `Talk` initializes its camera/Navi state before Event24 dispatches to Event23 (castle quest), Event21 (Gohma quest), then Event1 (Deku Tree meeting). The existing saved Bool `HaveTalked_Npc_Kokiri_001_Shop_Child_PresentDekuShield` already supplies D22 completion and the round-7 both-grant once-gate. No new save flag is needed.

Plan: intercept only the shuffled once-gated merchant after Event24's initialization. If incomplete and the existing meeting expression holds, call the original offer; otherwise retain original story dispatch. Never force Gohma/castle/meeting state. Unshuffled flow and implicit free-shield logic stay vanilla. Keep the `Missable` non-progression restriction (D28) until Kareem's result.

**Kareem: the requested new-game test will skip talking to the merchant until after Gohma, then test the late grant, repeat talk and Save/Continue; the castle-visit variant should also retain the offer.** Exact output/checklist and exercised evidence follow.

## Coordination / diagnostics


### Implemented / exercised

`gifts.py` intercepts only the `Event45` once-gated merchant at Event24's initialized dispatch. Two appended queries read the existing saved completion Bool and native tree-meeting BoolExp. An incomplete eligible offer reuses Event83 and its original return handling; completed/pre-meeting paths retain Event23's story-specific dispatch. Original quest queries, shelf releases, purchases, tutorial and saved flags are untouched. Both grant branches retain round7's immediate completion writes.

Failing-before regression: six late-story/equipment combinations returned no Boomerang (printed meeting=true with castle/Gohma=true); stale dispatch was not rejected. After the cause-specific fix, `uv run pytest tests/test_shopkeeper_window.py tests/test_gifts_shopkeeper.py -q --tb=short`: **17 passed**. `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_shopkeeper_window_dump.py tests/test_gifts_shopkeeper_dump.py -q --tb=short --basetemp E:/OOTRemake/work/r8-shops-cs8c/merchant-dump-next`: **2 passed**. Real-flow interpreter proves all four castle/Gohma combinations, equipped shield, repeat/restored completion and no pre-meeting gift; exact inverse recovers every other flow field.

Actual writer smoke: `uv run python E:/OOTRemake/work/r8-shops-cs8c/build_late_gift.py` passed, writing `ingame/shopkeeper-after-gohma-next/` with **four resources** (both Dynamic Bancs, merchant flow, size table). Flow **50552 -> 51736**, allocation **50832 -> 52016**; both chest copies change only Mido far-right's drop to Deku Shield. No GameDataList or quest state is changed. Every emitted resource parses/fits the table; inverse field deltas recover originals. Copied/statically checked approved new-game launcher; never executed.

**Kareem: follow `E:/OOTRemake/work/r8-shops-cs8c/ingame/late-gift-check.md`: avoid the merchant entirely, collect the supplied chest shield and vanilla Sword/Slingshot, clear Gohma, optionally visit Zelda before the first merchant talk, then obtain Boomerang with the shield equipped. Repeat after re-entry and Save/Continue must give nothing; normal shopping must still work.** Require overlay-open log. D28 stays in place; no gameplay result is claimed.
Initial allowed thread post failed with shell exit127: extensionless `~/go/bin/bermuda` not found. Filename lookup found `C:/Users/hi/go/bin/bermuda.exe`; using that actual binary posted successfully as cs8c. Python LSP references returned `No language server found`; known-symbol searches are the fallback. An attempted historical builder path was absent; use the actual external directory listing rather than infer a builder filename.

Shared changes will be isolated and posted; `generate/fill.py` algorithm remains Track A's and gift families other than this merchant remain Track D's. Section34 is appended in increasing order after available sections, no placeholders for32/33.
