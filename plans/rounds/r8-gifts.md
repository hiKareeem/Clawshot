# Round 8, Track D: more gift checks (cs8d)

Branch `r8/gifts`. Dump and save backups read-only. No game, launcher, GUI, Hookshot build or
terminal-control command executed. Generated/decoded evidence stays under `E:/OOTRemake/work/r8-gifts/`.
Track C owns the Kokiri merchant portion of `patch/gifts.py`; shared-file changes are isolated commits.
No dependency changes, merge, push, stash or unauthorized rebase.

## Ordered work

1. Cows (14): census, per-check persistence feasibility, isolated experiment and data-sourced logic.
2. Skulltula House: audit 10–100 rewards, support omitted native quantity, controlled output.
3. Frogs: song prizes and both heart rewards, native saved gates and controlled output.
4. Merchants: Medigoron, carpet salesman, Granny; success-only once gates, rules and controlled output.

Every newly supported check remains outside `--shuffle Gift` until Kareem's result. Existing verified
Gift behavior must not be silently disabled or broadened.

## Item 1: cow census and blocked per-cow dispatch

Read-only `probe.py`, `cow_dispatch.py`, `cow_components.py`, `extract_cows.py` and
`decode_cows.py` ran under the external research directory. Active flow version map: 640 flowcharts.
The unmodified external `ainb` decoder read the cow root and reaction graphs; no decoder dependency
or game data enters this worktree.

**The old count is placements, not checks:** 14 distinct placement Hashes represent eight physical
cows. Child/adult and Kakariko Alternative copies have different Hashes. The ranch has two placed
cows, not the four N64 stables/tower checks. No positional identity is proposed for seeds.

| Physical cow | Placement file suffix / Hash |
|---|---|
| DMT grotto | Child Dynamic / 6253945510651149508; Adult Dynamic / 15885469363360155465 |
| HF cow grotto | Child Dynamic / 4825657261695689152; Adult Dynamic / 1795271317212409607 |
| Ranch pair, first | Child Static / 5665703420335364217; Adult Dynamic / 6142142215325798939 |
| Ranch pair, second | Child Static / 2139721051512122393; Adult Dynamic / 14685178647961621150 |
| Impa's house | Child Dynamic / 3581309213670406493; Adult Dynamic / 13825940715109866119; Adult Alternative Dynamic / 17113125743534325889 |
| Link's house | Adult Dynamic / 11142894434822030727 |
| Gerudo Valley | Child Static / 9796879244811108931 |
| Gerudo Fortress | Adult Static / 11341244778524449886 |

All flow grants are `Animal_Cow/Event4`, `Event74`, `Event114`, calling
`Dm_SY_GetInEvent:GetInEventInBottle` with `BottleItem=10`. That wrapper fills an empty bottle,
not the ordinary literal pouch-add census grant. Entry `GiveMilk` calls `Cow_GiveMilk` at
Event72; LinkHouse calls it with its distinct push event; Valley/Fortress use `Cow_GiveMilk_gerudo`.
`Cow_GiveMilk` plays the recommended Epona melody, then transitions at Event3 into the shared
PushToBottleMilk event. Event141 checks an empty bottle before Event4. Event20 sets
`Cow_IsGetMilkFromCow`, which is shared, not an already-collected gate.
`HaveTalked_Special.Animal_Cow_PushToBottleMilk_Event5` is also shared dialogue history.

Each cow actor pack references a fixed external AISchedule; the shared actor root uses
`NpcCommon.OcarinaReplaceEvent.OneShotBeforehandLoadEventRequestRegister.module`.
`ReplaceEventParam/Animal_Cow` names `Animal_Cow_GiveMilk`. The root's EventName blackboard
comes from EventRequestParam (talk), not a demonstrated per-instance milk-grant selector.
The full active event-query inventory has no actor-hash/instance-name equality query.
Distance queries support named actors but are not identity predicates; inventing a geometric
dispatcher would not prove an independent saved check and is not applied.

Reviewer direction (Claude, 2026-11-09): timebox to Banc/event-request selectors; **no cow patch
this round either way**. That bounded audit found no existing per-placement event/flag selector.
The fourteen complete placement records contain no Dynamic parameters; schedules/replacement events
are per actor variant. Absence of a shipped override does not prove the engine could never support a
new one, but no such contract has been demonstrated. **D11 stands.** No cow patch/test overlay,
new Bool, global milk replacement or logic change is introduced. Item 1 is complete as the narrowed
research task; no gameplay claim or fourteen-independent-check claim.

## Item 2: Skulltula House rewards

Native read-only trace `rewards.py GatheringTokenGold` confirms:

| Tokens | Grant event | Actor | Persistence |
|---|---|---|---|
| 10 | Event398 | Item_Wallet_Medium | KakarikoVillage_GatheringTokenGold_GetReward10 |
| 20 | Event75 | Item_AgonyStone | corresponding GetReward20 |
| 30 | Event194 | Item_Wallet_Large | corresponding GetReward30 |
| 40 | Event200 | Item_BombchuBundle_Large | corresponding GetReward40 |
| 50 | Event219 | Obj_Heart_Piece | corresponding GetReward50 |
| 100 | Event215 | Obj_Rupee_Gold | GatheringTokenGold Complete; father transformation |

10–50 reuse native saved Bools (D22); no new Bool is needed. Event471 is the native repeat
200-rupee reward after completion and is deliberately untouched. First100 is distinct and
changeable through its existing wrapper, without shuffling every repeat.

Shared data commit `f0b4451`: PouchActorInfo proves the large Bombchu bundle is **20**, not the
translated ten; `remake/gifts.toml` corrects vanilla to `Bombchus (20)` and holds40 vanilla until
Kareem's result. The actor table now represents that actual item. Existing threshold rules are
the sourced OoTR token-count predicates; all native token-count/quest queries are unchanged.

`skulltula_hint_changes` implements the round6 design note: native `Npc_SkullDad` labels
Talk_28/Talk_23–26 name each assigned10–50 reward using native English item names in all16
language archives (D26), with existing style/wrapping/highlight helpers. The Gift seed step
composes these transforms with existing Gossip Stone text;100's repeat is not a hint/check slot.

Controlled final output: `E:/OOTRemake/work/r8-gifts/ingame/skulltula-rewards-play-next/`.
Copied release-only launcher `Test - skulltula-rewards-play-next.bat`; checklist `skulltula-check.md`.
Its separate user copies `2026-11-08_2140-main-jabu/save/5a3c9e1f0b7d24680000000000000001`.
Read-only slot01: child,14 tokens, GetReward10 false; Hookshot not owned. Swaps10 Hookshot,
20 Boomerang,30 Longshot,40 Hammer,50 Lens,100 Deku Shield. Native repeats remain gold rupees.
Actual common writer emitted17 resources, all parsed/sized; inverse six-item delta restores
the entire original flow. No GameDataList or resource-size growth was needed.

**Kareem: follow `skulltula-check.md`: immediately claim10 at the House, check Hookshot/text/
preview, revisit and Save/Continue with no duplicate; later collect the natural20–100 thresholds.
Require overlay log plus game result.** No launcher/game was executed here.40 stays disabled.

Diagnostics: first preview regression printed literal `{Boomerang}` (wrong highlight markup);
used canonical FIELD_START/FIELD_END, not braces. The cause-aimed run passed:
`OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_gifts_rewards_dump.py -q
--basetemp E:/OOTRemake/work/r8-gifts/pytest-skulltula-markup-fixed-next`: **1 passed**.
This regression verifies actual assigned names and preservation of already-patched stone text.
Two unused prototype overlays are superseded, not overwritten; the final play-next test
uses an unowned10 reward after printing the backup's actual ownership.

## Item 3: frogs — five songs and two distinct heart rewards

Native `MiniGame_FrogTenors` census:

| Check | Flow event(s) | Native completion Bool |
|---|---|---|
| Zelda's Lullaby | Event172 -> TeachNewMusic | MiniGame_FrogTenors_ZeldaLullaby |
| Epona's Song | Event220 -> TeachNewMusic | MiniGame_FrogTenors_EponaSong |
| Saria's Song | Event221 -> TeachNewMusic | MiniGame_FrogTenors_SariaSong |
| Sun's Song | Event222 -> TeachNewMusic | MiniGame_FrogTenors_SunSong |
| Song of Time | Event223 -> TeachNewMusic | MiniGame_FrogTenors_TimeSong |
| Song of Storms / Rain heart | Event384 | MiniGame_FrogTenors_StormSong, written Event112 |
| Butterfly game first heart | Event161 initial, Event75 retry | MiniGame_FrogTenors_InsectRepellent, written Event151 after success |

All seven completion Bools exist, default false, reset8/save0. Native SongClear requires all
six song flags and only unlocks the bug game; it does **not** mean the bug-game prize was won.
The old census incorrectly called Event384 `ZR Frogs Ocarina Game`. Shared `ae3099f` corrects
that to Rain and links both first-win/retry calls to the actual Ocarina Game. Repeat bug rewards
Event162/Event76 remain Blue Rupees; a failed round grants nothing.

The five ordinary songs use `EventTriggerIncreaseRupee`, not a pouch actor. Event378 selects
5/10/15/20/30 by saved `MiniGame_FrogTenors_GetCount`; Event392 increments it. The census
records their stable song call IDs with empty `param`/`vanilla_item`: no fake item actor or
fixed50 payout is invented. Those entries intentionally cannot match a seed-pool actor yet.

Implementation: specialize the native `TeachNewMusic` entry **per changed caller**. Append
only its reachable graph after replacing Event380's rupee-UI subtree with the existing ordinary
GetInEvent wrapper and one literal item. Remap every edge/case/fork/join/subcall index; retain
native variables, original entries and all other callers. First-song counter, saved flag and
frog growth remain; repeat song routes give no second item or extra rupees. Entry-local actor
bindings and graph-index overflow refuse explicitly, rather than silently misbinding actors.
D22 reuses the native flags: no new Bool/save-layout change for any frog check.

Logic: the existing sourced child/playable-song predicates agree with native melody0–5 dispatch;
the bug game asks all six. `remake/gifts.toml` records native provenance and holds all seven
vanilla until Kareem's result. This intentionally retires the old incorrectly linked shuffled
Rain-as-all-songs check instead of enabling the newly corrected families without acceptance.

Controlled final output: `ingame/frog-seven-play-next/` under the round's external folder.
Own copied launcher/user; first launch copies the read-only main-jabu backup's save/user directory.
Slot01 was checked: child, Bomb Bag plus Bracelet (river entrance reachable), ocarina and
Lullaby/Saria/Sun, no Epona/Time/Storms; all seven completion Bools false.
Three song checks supply missing Epona/Time/Storms; Epona gives Hammer, Time gives Lens,
Storms gives Longshot, first bug win (initial or retry) gives Hookshot.
Common writer: flow **150328 -> 225104**, entry **150608 -> 225392**; only the flow and
resource size table emitted. All five specialized roots and both first-bug branches read back
as assigned; repeat Blue Rupees unchanged. No launcher/game/save mutation.

**Kareem: `ingame/frog-check.md` gives the exact order. Verify new songs actually learn,
growth remains, first song/retry/failed round behavior, both heart replacements, native repeat
rupees and Save/Continue; require frog-flow/size-table overlay log lines.**

Checks: `uv run pytest tests/test_gifts_frogs.py tests/test_gifts.py tests/test_names.py -q`:
**21 passed**. Synthetic persisted-state replay proves each song grants once, no extra rupees,
counter remains5, untouched native caller still pays normally, stale completion flag refuses.
The initial synthetic fixture put65535 in a switch target (printed IndexError at that target);
replaced it with a real terminal branch, matching native graph shape. Cause-aimed rerun passed.
`OOT_ROMFS=... uv run pytest -m dump tests/test_gifts_dump.py -k "round_trips or every_step"
--basetemp E:/OOTRemake/work/r8-gifts/pytest-frog-native-next -q`: **2 passed,3 deselected**.
The native oracle covers every changed gift and allows only the new caller-local entries,
verifying first-grant identity and absence of a reachable duplicate rupee action.

## Item 4: three native merchant transactions

| Check | Stable caller | Native transaction |
|---|---|---|
| Medigoron | Npc_Goron_Medigoron_Adult/Event11 | SimpleShopRoot_Npc_Goron_Medigoron_Adult;200 rupees; no saved purchase flag |
| Carpet | Npc_Hylia_044_Adult/Event3 | SimpleShopRoot;90 rupees; Npc_Hylia_044_Buy is reset1/save-1, not persistent |
| Granny Blue Potion | Npc_Hylia_053_Adult/Event12 | GetInEventInBottle_BlueBottleShop;100 rupees plus an empty bottle; separate from trade Event167 |

The older census and the research helper's initial “Granny sale absent” conclusion were wrong:
the active053 flow has a literal ActorName and bottle2, but its bottle wrapper never reaches
the pouch-add fixed point. Read the actual Event12, Event11 funds, Event15 bottle and wrapper's
native charge; added exactly that sale to the census. Odd Mushroom/Odd Powder trade, quest
unlock and all other bottle gifts stay unchanged.

Shared metadata-only `f9cc8e8` adds its stable definition/catalogue, holds all three merchants
vanilla, records native fee90 (carpet needs no upgraded wallet/Bombchu prerequisite), and adds
Granny's empty-bottle requirement with guarded/source overrides. Medigoron's existing adult,
wallet and room rule stays; existing trade/approach predicates are not claimed newly game-proven.

`purchase=true` in gift rules uses the existing D22 saved-Bool allocator, one new flag per check.
Medigoron/carpet specialize only their reachable SimpleShop roots/tails; all115 original common
events and all7 original entries are unchanged, including beans/untouched merchants. Flags are
set immediately after successful grants, not after wrappers which also return on cancellation.
Native choice/funds/capacity/price behavior stays. Medigoron's two ownership gates read completion,
his presentation uses the generic gift wrapper and no longer takes a broken knife for an unrelated
reward. Granny keeps her unlock/bottle gate, replaces only the bottle-grant wrapper and restores
its native100-rupee charge on success. No gate is set on cancellation, poverty or full capacity.

Controlled output `ingame/merchants-three-play-next/`, copied release-only launcher
`Test - merchants-three-play-next.bat`, checklist `merchant-check.md`. Medigoron gives Hammer,
carpet Longshot, Granny Hookshot. Own user copies the main-Jabu backup's nested save/user contents;
slot01 owns none of these three. All six inspected slots of both candidate before-adult and
main-Jabu backups lack Master Sword and these rewards. The chosen checkpoint is child; the
checklist requires normal child-to-adult progression and Granny's trade, not immediate claims.
Do Granny before carpet for a clean Hookshot-before-Longshot upgrade check.

Real common writer produced **six resources** (four flows, GameDataList and size table), all
parsed/sized. Added Bools are defaultfalse/reset8/save0; backup SHA256 values unchanged.
`uv run python E:/OOTRemake/work/r8-gifts/build_merchants.py` passed; launcher checked only as
text and never executed. `smoke_merchants.py` interpreted the actual serialized native transaction
graphs: all three cancel/poor/full-or-no-bottle paths gave/charged nothing, each successful path
gave its distinct item and charged exactly200/100/90, saved-state revisit gave/charged nothing.
It also loaded the real world and verified all three remain held vanilla.

Smoke diagnostic: the first reload equality assertion printed an extra native
`UI_IsPlayingShopEvent=false`, not an extra reward/charge. Printed before/after/diff, initialized
that transient UI flag as the real idle baseline, then one cause-aimed run passed all scenarios.
This changes no production behavior. Synthetic persisted-state regressions:
`uv run pytest tests/test_gifts_merchants.py tests/test_gifts.py tests/test_gifts_frogs.py -q`:
**22 passed**. Targeted full native inverse/given/flag oracle:
`OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest tests/test_gifts_dump.py
-k "round_trips or every_step or game_data_list" -m dump -q -s
--basetemp E:/OOTRemake/work/r8-gifts/pytest-merchants-native-next`: **3 passed,2 deselected**.

**Kareem: follow `merchant-check.md`: refusal, insufficient funds, capacity/bottle refusal,
actual grant/use and exact fee, revisit and Save/Continue, independent merchants and untouched
Odd Mushroom trade. Require overlay-open log plus result.** Native sales dialogue may still
name original merchandise; report presentation differences. No new merchant is seed-enabled.

Owned section35 is appended after existing31, keeping present sections in numeric order.
Reviewer inserts32–34 ahead of35 when integrating their tracks; no placeholders added.

## Decisions / questions

- Cow policy resolved by the reviewer above: D11 stands; no cow patch in Round 8.
- **Kareem/co-owner: after the frog experiment passes, what fixed rupee item should each of
  the five order-dependent song prizes add to a shuffled pool?** Native payouts are5/10/15/20/30
  by collection order, not five50-rupee items. No pool/product choice is made here.

## Coordination

Initial prescribed `~/go/bin/bermuda` invocation failed (127): executable resolution omitted `.exe`
on this Windows shell. Printed HOME/USERPROFILE and `command -v bermuda`: actual executable is
`C:/Users/hi/go/bin/bermuda.exe`. The corrected explicit executable is used for subsequent posts.

Reviewer-authorized rebase onto the plans-only main move completed conflict-free at a clean
worktree. Superseding commit IDs, in order:

| Original | Rebased | Scope |
|---|---|---|
| 07ec6f4 | 86da76e | Cow research; D11 stands |
| f0b4451 | b061ebe | Native40-token quantity, shared metadata only |
| 55a2d23 | cffec46 | House previews and controlled rewards |
| ae3099f | 24a40e5 | Corrected frog identities, shared metadata only |
| bfa10b0 | 66bf25f | Per-song specialization and first-win retry preservation |
| f9cc8e8 | da55183 | Merchant definitions/rules/catalogue, shared metadata only |
| d9ed925 | b854f57 | Success-only merchant transactions, tests and section35 |


## Verification

All four complete gates run after the authorized plans-only rebase; results recorded below.

Independent post-rebase actual-writer replay used `PYTHONHASHSEED=947` and reversed placement
input order in a separate interpreter: **all17 House,2 frog and6 merchant compressed resources
byte-identical** to the three retained player outputs. `replay-verification.json` retains the
SHA256 ledger outside the repo. The chosen source's actual `Sequence_IsChildhood` flag is
**true**, read-only. No existing output/launcher/user was written. Removed only this session's
completed replay folder/driver and the throwaway native-graph smoke driver after observing the
proof; the retained builders, research probes, three requested final overlays and checklists remain.

Reviewer concurrency update read from main `02-orchestration.md:61–63`: parallel pools at most3,
one worker while Hookshot runs, one sweep at a time. This track's gates are sequential plain
pytest with no pool/xdist; no seed sweep is active. No additional pool/sweep will be started.

### First complete gates and diagnosed failures

| Command | Observed result before the terminal-edge correction |
|---|---|
| `uv run ruff format --check` |209 files already formatted |
| `uv run ruff check` |All checks passed |
| `uv run pytest` |623 passed,80 skipped;371.24s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` |77 passed,2 failed,624 deselected;1048.56s |

Both suites used only outside-repository `PYTEST_ADDOPTS=--basetemp=...` directories
`gate-synthetic-rebased` / `gate-dump-rebased`; no failure was filtered or interrupted.

1. Existing BossHeart seed7 oracle exhausted unchanged10 attempts: last Small Key(Fire Temple),
   **8 allowed of125 left;20 other items**. Posted exact test/API/payload to Track A. No filler
   change, retry increase, seed reroll or test substitution here.
2. Gift-inventory graph oracle reached Granny's new collected-return switch and raised IndexError.
   Printed actual serialized values: **156 events, root155, cases0->65535(NONE),1->113**.
   The earlier “event list153” interpretation in the checkpoint post was wrong: the parser/flow
   is valid; `_successors` included a terminal switch target as if it were an event index.
   Filter exactly the EVFL NONE sentinel from switch successors, not exceptions or valid nodes.
   Added a synthetic terminal-switch/census-reachability regression. Cause-aimed checks:
   `uv run pytest tests/test_census_gifts.py tests/test_gifts_merchants.py -q`: **9 passed**;
   full affected `OOT_ROMFS=... uv run pytest tests/test_settings_gift_inventory_dump.py
   -m dump -q -s --basetemp E:/OOTRemake/work/r8-gifts/pytest-inventory-terminal-fixed`:
   **1 passed**. No overlay bytes changed; the fix is traversal only.

Reviewer corrected the rebase target to **15d4c70** (B/E merged; the earlier536b4a5 hash was
incorrect), followed by all four gates again. Preserve section order33/35/36.

### Rebase15d4c70 and measured pool delta for Track A

Authorized rebase completed. The only conflict was additive `03-game-data.md`; retained B's
entire33 and E's entire36, inserting owned35 between them. No source/test conflicts.
Current ledger:

| Commit | Scope |
|---|---|
| a7ba027 | Cow research; D11 stands |
| 7bc50c0 | Native40 quantity, shared metadata |
| dd4c041 | House previews / controlled rewards |
| 42be03e | Frog identities / shared metadata |
| 6ede2d5 | Per-song specialization / first-win retries |
| 8945263 | Merchant shared metadata |
| 4b75106 | Success-only merchant transactions / section35 |
| ca81dd7 | Terminal switch traversal correction / regression |

Reviewer requested a pool delta because his main seed7 passes. Read-only instrumentation
intercepted `patch.make_seed` at its actual `generate` boundary, prepared the real Settings/world,
and captured the pool/fixed placements **without invoking fill**. Separate interpreters explicitly
imported this branch and `E:/OOTRemake/Clawshot/src`; printed module paths prove which source ran.

For `make_seed(Path("E:/Games/Hookshot/romfs"),7,Settings(shuffle=("Chest","BossHeart")))`:

- Both have **172 shuffled locations**, identical order, identical per-location items and item
  multiset; **no shuffled pool item is added, removed or moved**. Effective Settings and
  `remake_vanilla` overrides are identical.
- Both have1156 fixed placements; the only fixed-item difference is **Kak40 reward:
  Bombchus(10) -> Bombchus(20)**, the native quantity correction.
- Other access-rule changes are the native90-rupee carpet sale dropping upgraded-wallet/Bombchu
  prerequisites, and Granny adding her native bottle prerequisite. No claim that a particular
  one of these is the single causal trigger; the shuffled-pool-change hypothesis is not supported.
- Exact JSON snapshots/delta and read-only reproducer:
  `E:/OOTRemake/work/r8-gifts/pool-{main,branch,delta}.json`, `capture_pool.py`.
  Full findings and exact API/test command posted to `cs-r8` for cs8a.

Track A's09:50 post independently confirms this branch's case: diagnostic old fill fails all10
attempts (six Fire-key failures, four Bombchu-pack failures); their fill+BossHeart palette fix
passes attempt1. No Track A code is copied into this branch and no gate is rerun unchanged.

**Claude/cs8a: merge the fill fix first and provide its main target, as directed. Then rebase
this branch and run all four full gates.** Final readiness is blocked on that upstream merge,
not on the now-fixed Granny traversal. No fill edit, seed substitution, retry increase or test
weakening is made here. All reachable implementation, player artifacts, exact failure/pool
evidence and the clean15d4c70 integration are complete; gameplay acceptance remains Kareem's.

## Additional research: Egg, Chicken and Zelda's Letter share the child trade cell

Reviewer/Kareem observation is accepted: taking Zelda's Letter from a chest while holding
the Weird Egg made the Egg disappear from the inventory. **Research only; no gameplay,
world rule, pool, grant, pouch or engine code is changed for this item.**

### Native evidence

Read-only `uv run python E:/OOTRemake/work/r8-gifts/child_trade.py` passed against builde0f3ccfa:

- `RSDB/PouchActorInfo.Product.111.rstbl.byml.zs` has distinct AssignableItem identities
  `WeirdEgg`, `AlarmCucco` (the child Chicken), `ZeldaLetter`; all are Material/Large,
  PouchSpecialDeal None and autosave-on-get. Each native PouchContent component has
  `EnableStock=false`. **Those rows alone do not declare an independent slot per item.**
- `UI/Pouch/PouchTable/PouchTable.game__ui__PouchTable.bgyml` groups all three in the
  **same** ItemArray cell, `BtnName=Pa_ItemIcon_23`, `SpecialDeal=SwordBigGoronChallenge`.
  They are the cell's only child-usable variants, ordered Letter, AlarmCucco, WeirdEgg.
  Adult trade variants occupy that same UI group for their age. This confirms the shared
  child-trade presentation/selection cell, not three simultaneously selectable inventory cells.
- This is consistent with the reported loss of the Egg from the visible inventory. **Whether
  receiving Letter actually deletes the Egg's underlying pouch record, rather than making
  it inaccessible behind another cell variant, is not established by these metadata files.**
  No before/after raw save was supplied or invented. Do not infer recoverable independent
  ownership from separate IsGet flags; usable Egg/Chicken must remain available for Talon.
- The actual native chain is explicit: `Goto_HyruleCastle/Event55` takes WeirdEgg,
  `Event20` gives `Item_AlarmCucco` through the egg-hatch event, and `Event93` checks the
  Chicken in the pouch. Talon's wake cutscene `Dm_HrlCastle_0020/Event69` takes Chicken;
  `Event121` advances Goto_HyruleCastle to Step04 and `Event134` sets **Talon_AfterWakeUp**.
  The existing Bool is defaultfalse/reset8/save0, verified by its GameDataList hash822480096.
  That saved event, not mere historical Egg ownership, is the relevant completion fact.

### What OoT Randomizer526b4c8d actually does

The existing read-only upstream checkout at `E:/OOTRemake/work/r2-world/OoT-Randomizer`
reports HEAD **526b4c8d81b7c4023ef4573ffbaf39344e270d5b**. No NX2navi code/docs were read.
Facts below are source evidence, not a claimed execution of OoTR or its N64 runtime:

1. [Castle rules][ct-castle] require Weird Egg **or** Chicken to reach HC Garden;
   Zelda's Letter and Impa's song are checks beyond that gate. [Ranch rules][ct-ranch]
   independently retain the castle Egg/Chicken prerequisite for child Malon's song and Talon's
   chicken game, unless Skip Child Zelda is selected. Early Letter is **not** treated as a
   substitute for waking Talon.
2. [ItemPool.py695–712][ct-pool] shuffles only selected child-trade items; otherwise they stay
   vanilla. Selecting Chicken but not Egg replaces the native Egg pool contribution with
   Chicken; selecting both does not add both stages. [Patches.py796–797][ct-enable] enables
   CFG_CHILD_TRADE_SHUFFLE when child trade is shuffled (or advanced logic).
3. The runtime has **more state than vanilla's current child-trade slot**.
   [trade_quests.c53–139][ct-owned] maps child items to one slot but keeps a separate
   per-item owned bitset; Egg/Chicken/Letter are distinct ownership bits. Hatching updates
   Egg ownership to Chicken without clearing unrelated owned Letter. The same file's
   179–230 functions select next/previous owned items and update the selected slot/equips.
   [dpad.c22–37][ct-cycle] exposes that cycling in the item menu. Thus selecting Letter does
   not destroy the ability to reselect owned Egg/Chicken and wake Talon; Letter remains owned.
4. [Item grant effects][ct-effects] register Zelda's Letter as owned too (the Letter effect ends
   in trade_quest_upgrade); it is not protected merely by a fill-order rule.
   [Installed runtime hooks][ct-hooks] update owned flags on hatch and prevent courtyard
   savewarp from reverting Letter to Chicken when child-trade shuffle is on; a separate
   hook prevents collecting the shuffled Zelda check twice. These are executable patches,
   not guarantees obtained by copying OoTR's monotonic inventory logic into a RomFS-only mod.

### Proposal for Clawshot — not applied

**Recommendation for the next reviewed playable seed: keep both Weird Egg and Zelda's Letter
at their native gifts, with native hatch/Chicken consumption unchanged, until the shared-slot
contract has an accepted solution. Kareem/co-owner: approve this temporary hold?**
No claim that a seed may require both simultaneously usable merely because Search remembers
both. A check granting Letter before Talon's chain completes can strand the required Chicken.

If keeping the two shuffled is preferred, the minimum safe alternative is to constrain Letter
to checks **physically impossible to collect before Talon_AfterWakeUp**, and prove every
permitted destination has that native gate. The native Zelda courtyard gift is the conservative
candidate. Merely adding `Weird_Egg` to a logical requirement is insufficient: the reported
failure occurs while holding Egg, and logic-only gates do not stop an optional chest being
opened early. An explicit persistent “child Talon woken” event, item-placement restrictions
and physical gate acceptance would be needed, plus shuffled-Egg hatch/Talon tests.

The full OoTR solution instead requires independently retained ownership plus a demonstrated
selection/cycling mechanism and native trade/hatch integration; no such remake contract is
proved here, and no Hookshot/runtime patch is proposed as Round8 code. No allowlist expansion
or quiet production restriction is made by this research.

[ct-castle]: https://github.com/OoTRandomizer/OoT-Randomizer/blob/526b4c8d/data/World/Overworld.json#L1351-L1404
[ct-ranch]: https://github.com/OoTRandomizer/OoT-Randomizer/blob/526b4c8d/data/World/Overworld.json#L2792-L2817
[ct-pool]: https://github.com/OoTRandomizer/OoT-Randomizer/blob/526b4c8d/ItemPool.py#L695-L712
[ct-enable]: https://github.com/OoTRandomizer/OoT-Randomizer/blob/526b4c8d/Patches.py#L792-L797
[ct-owned]: https://github.com/OoTRandomizer/OoT-Randomizer/blob/526b4c8d/ASM/c/trade_quests.c#L53-L230
[ct-cycle]: https://github.com/OoTRandomizer/OoT-Randomizer/blob/526b4c8d/ASM/c/dpad.c#L22-L37
[ct-effects]: https://github.com/OoTRandomizer/OoT-Randomizer/blob/526b4c8d/ASM/c/item_effects.c#L231-L269
[ct-hooks]: https://github.com/OoTRandomizer/OoT-Randomizer/blob/526b4c8d/ASM/src/hacks.asm#L2717-L2785

### Temporary gate cleanup

Removed only this session's completed full-gate basetemps, leaving requested player outputs
untouched. Git Bash rm initially refused47 dangling pytest `*current` directory symlinks.
Printed reparse attributes1040 and native link targets, verified every remaining link points
inside its own session basetemp, then removed only the links with native directory-unlink and
the now-empty roots. No unchanged rm retry, target traversal or unrelated deletion.
