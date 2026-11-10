# Round 10, Track A: gift checks (cs10a)

Branch `r10/gifts`. Required instructions, README, plans00–04, decisions, round8/9 reports and
Round10 opening/shared-file rules read. Dump and backups read-only; no game, launcher, window,
Hookshot build, terminal-control command, merge, push, stash or dependency edit.
Research/output: `E:/OOTRemake/work/r10-gifts-cs10a/`. Initial tasklist: Hookshot running.
Every pytest uses `CLAWSHOT_WORKERS=1`; full suites/sweeps acquire the shared gate directory.
Python LSP: only marksman configured; references request reports no Python server.

## Item 1: release seven frog checks

Accepted Kareem's R8-FROGS result without rerunning the game. Removed all seven holds;
five song checks contribute `Rupees (20)` as specified, two hearts remain Piece of Heart.
Census keeps honest empty actor/parameter fields for native variable payouts. Eligibility
explicitly recognizes the already-validated TeachNewMusic calls. Always specialize shuffled
song callers, even an unchanged20 assignment, so native5/10/15/20/30 never leaks into that seed.
Unshuffled callers retain native escalating payment; completion/growth/repeats are unchanged.

Checks:
- `CLAWSHOT_WORKERS=1 uv run pytest tests/test_gifts_frogs.py -q`: **4 passed**.
  Includes persisted-state once behavior, five fixed20 grants even for unchanged assignments,
  exact seven-check eligibility and five20/two-heart pool contributions.
- Actual public CLI seed7, `--shuffle Chest Gift`, new `frogs-seed7-next`: **exit0,
  218 shuffled checks,28 spheres,119 resources**. Written spoiler includes all seven frogs;
  their assignments are20 rupees, Cojiro, Odd Potion, green rupee, Agony, Broken Sword,50 rupees.
  Native frog flow150328 ->225136, allocation150608 ->225424.
- Scoped ruff format completed. Full four gates remain required before any readiness claim.

## Ordered remaining work

2. Market child bottle tutorial: native conditions/persistence, census/logic/swap, isolated save-copy checklist.
3. Deterministic bowling, then normal/expert gallery prizes if native flows permit; controlled outputs.
4. Dampé digging once-only reward if the native grant permits.

No new family beyond the accepted frogs is claimed in-game certified. Questions for Kareem
will be recorded here in **bold**, without stopping the reachable work.

## Item 2: Market Potion Shop bottle

Native probe confirms the section15 identity, not the tentative046 name in the playtest answer:
`Npc_Hylia_020_Shop_Child/Event171`, already censused but unlinked. Now named
`Market Potion Shop Bottle`, with explicit remake-only grouping (no fake OoTR name), directions,
and a new child check at `Market Potion Shop`. It supplies a fifth native bottle in fixed logic;
no owned bottle, item, payment or story prerequisite. Existing child/day shop entrance remains.

Default AISchedule calls `Item_Bottle_TutorialEvent_Talk`. Choice acceptance reaches171,
then native fork writes `Npc_Hylia_020_Shop_Item_Bottle_Present` (Hash1617407101).
Started970426237 and Cleared1298325109 are also defaultfalse/reset8/save0.
Native continuation requires catching a bug, removes the selected bottle contents at59 and
fills it with Red Potion at172; a literal non-bottle swap would strand that tutorial.

Provisional engineering choice: changed rewards retain the native offer/refusal but route
acceptance directly to the generic grant, then set the three existing completion Bools and
run the native quest-completion action. The entry checks Present before any staging and
routes completed visits to ordinary Talk. No bottle removal, fake bottle grant, bug requirement,
new saved Bool, NPC pack/schedule edit or shelf edit. Unchanged/unshuffled Bottle stays native.
**Kareem: accept this short shuffled tutorial bypass only after the isolated check below.**
D15 holds the new shuffled check until that result; the vanilla early bottle is modeled now.

Output: `ingame/market-bottle-next`, launcher `Test - market-bottle-next.bat`, checklist
`bottle-check.md` under this track's external folder. Uses its own absent user; copies only
the read-only2026-11-07_llr-tower-before-pickup backup at launch. All six source slots:
child, Present/Started/Cleared false, Boomerang absent; slot01 is the manual checkpoint.
No save copied or launcher executed. Static launcher: bin executable only, updater off,
missing-exe/backup/copy-failure stop, isolated user/log, outward-only backup copy.

Checks:
- Synthetic bottle/gift/catalogue: **24 passed**; child without bottle can collect the fixed
  bottle, adult cannot; refusal consumes nothing, accepted generic gift saves completion,
  restored-state revisit gives no duplicate; stale dispatch refuses.
- Focused native `tests/test_gifts_dump.py -k \"round_trips or every_step\" -m dump`:
  **2 passed,3 deselected**,10.47s.
- Actual common writer `build_bottle.py`: **two resources**, flow99536 ->100240,
  allocation99824 ->100528. Exact inverse restores the entire native flow; actual serialized
  dispatch interpreted refusal/accept/revisit and no selected-bottle action. Proof:
  `bottle-proof.json`. Runtime presentation/shopping/Save-Continue still require Kareem.

Diagnostics: an inline minigame-summary probe failed before reading files with Python's
comprehension assignment-expression restriction; printed SyntaxError. Replace with an external
straight-line researcher, not an unchanged rerun. No production behavior failed.

## Item 3: deterministic bowling and gallery prizes

Bowling uses its existing saved First/Second flags to dispatch First Prize on win1, Second
Prize on win2, then the unchanged native red-rupee filler. Its normal opening, rental equipment,
fees, failure paths, difficulty progression and count routine remain. The second grant also sets
the native Third flag (the heart-map marker) immediately; no new Bool. The old native Bombchu
payout is no third shuffled check or phantom fixed Bombchu source in Gift/NPC mode. Unshuffled
mode retains all native routing. Both checks always normalize, including unchanged assignments.

Native ownership-dependent upgrade branches now take one fixed pool item: bowling Bomb Bag30,
child gallery Bullet Bag40, adult gallery Quiver40. PouchActorInfo `AfterExpansionMaxNum`
confirms30/40/40; native large Bomb Bag is40. Both native tier branches give the assignment,
even when unchanged. Bomb Bag30 aliases the Bomb Bag ability; bullet bags/quivers are normal
capacity upgrades, **not ownership of the rental Slingshot/Bow**. All three stay gift-only until
chest-verified. Added small shared actor/world/catalogue metadata; no general fill change.

Normal gallery saved flags remain HrlCity_Get_BulletBag and Kakariko_Get_Quiver
(reset8/save0); native failure/fee/rental/normal-repeat rewards are unchanged.

### Expert gallery report / owner question

The flows have expert mode, but **not a first-expert check**. After normal completion,
Event445/449 dispatch IsHardMode to repeat30 rupees (child Event202) or70 (adult Event599)
through `GetRupy_HitTarget`. Neither is a literal item actor or an independent saved first-win
flag. A separate check is technically feasible using D22's new saved Bool and a specialized
grant; a fixed pool contribution still needs a product choice (as frogs explicitly received20).
**Kareem/co-owner: should each first-expert win contribute fixed Rupees (20), or retain the
native30/70 amounts through a broader numeric-reward item representation?** No invented
actor or silent replacement of30/70 by20. Posted this gap to cs-r10; expert stays native in
the current output. This is a bounded report, not a claim the engine cannot support it.

### Exercised acceptance

- `tests/test_gifts_minigames.py` plus gift/catalogue tests: **27 passed**.
  Persisted first/second/filler, failed rounds, both owned-upgrade states, unchanged assignment
  normalization, exact native-tier eligibility and stale dispatch refusal.
- Focused whole-gift native inverse/grant tests: **2 passed,3 deselected**,12.13s.
- Actual Gift setup/native normalization oracle: **1 passed**,9.52s. Both bowling prizes
  and both normal galleries selected; extra refill rows excluded; same assignments force
  fixed tiers; exact inverse restores every original flow field.
- Actual common writer `build_minigames.py`: **three resources**, bowling184184 ->184488,
  allocation184464 ->184784; gallery279936 unchanged length. Full inverse on both flows;
  serialized native reward replay proves Storms/Epona/red/red for both prior-upgrade states,
  normal child Agony/red and adult Epona/purple, with saved completion. No new GameData.
  Retained `minigames-proof.json`.

Player outputs: `ingame/minigames-next`, two unrun launchers `Test - minigames-child-next.bat`
and `Test - minigames-adult-next.bat`, exact `minigames-check.md`. Child copies the read-only
main-dodongo backup; adult the after-forest backup. All six source slots in each have all
bowling/gallery once flags false; rewards selected are unowned (child Storms/Epona/Agony,
adult Epona). Unique users/logs, bin executable only, missing-exe/backup/copy-failure stops.
No save copy or game execution by the agent. Expert output remains native pending policy.

Shared consumer follow-up `557a8d0`: the new normal Quiver40 joins D29's named permanent
upgrades without becoming a major-item hint; **13 hint-worth tests passed**.

## Item 4: Dampé digging's real event grant

Active file is `Npc_Hylia_Dampe_001.110.bfevfl.zs`. Existing uncatalogued census Event628
calls `GetInEvent_NotTurn_NotNpc_Dampe`, then GetPouchContent: the actual pouch grant.
Event82's temporary heart staging and Event301 cleanup remain native, not a crashing major
floor-actor swap. The native saved completion is
`GraveYard_DiggingHoleTour_Drop_HeartPiece` (Hash3037888117,false/reset8/save0).
Main talk/check routes already read it; the shortcut entry can still structurally reach
the reward with completion true. Added a guard to the reward branch of Event449's fork
and an immediate completion write after628; the parallel prop-cleanup branch and original
later completion write remain. No new Bool, lottery/fee/route/digging modification.

Linked Event628 to the existing OoTR digging check, retyped it NPC (not a placed Collectable),
moved its exact child/night/Time Flows rule from child_graveyard into the owned gift overrides
(no duplicate override), and added player directions/rule. D15 holds the shuffle pending the
controlled test, but its native fixed reward/access remain in logic.

- Focused digging/gift/catalogue tests: **23 passed**. Synthetic serialized fork proves one
  grant, saved direct-retry denial, cleanup still runs, unsafe extra incoming entry refuses.
- Focused generic native gift oracle: **2 passed,3 deselected**,12.69s.
- Actual common writer `build_digging.py`: **two resources**, active flow305112 ->305688,
  allocation305392 ->305968. Full inverse recovers every original field. Native serialized
  fork replay gives Boomerang once, then none, with cleanup on both paths; no GameData emitted.
- Dedicated real-writer/saved-Bool/native-fork oracle: **1 passed**,8.85s.

Output `ingame/digging-next`; unrun `Test - digging-next.bat`, own user, `digging-check.md`.
Copies main-dodongo backup outward once at launch. All six source slots: child, met Zelda,
completion false, Boomerang absent. **Kareem: check notice/model/use, no extra permanent Heart
Piece or lingering prop, native repeat rupees, map marker and Save/Continue; require the .110
flow and size-table overlay logs.** Retaining native presentation is not an in-game certification.

## Integrated runtime proof before gates

Actual public CLI seed7 `--shuffle Chest Gift` and separate-interpreter effective-CS1 replay:
both **exit0,221 checks,21 spheres,122 resources**. Complete outputs: **124/124 files
SHA256-identical**. Read each actual written frog, bowling and gallery grant against its
spoiler assignment; all agree. Bottle/digging stay held and their native flows are not emitted;
the old extra bowling refill rows are absent. Proof `final-seed-proof.json`; CLI logs
`final-seed-original.log` / `final-seed-replay.log`.

The first smoke's final static assertion incorrectly required every test user still to be
absent. Printed cause: `user-market-bottle-next` now exists externally, with save/temp/log;
the current game PID differs from the initial snapshot. No agent launched/copied it and no
gameplay acceptance is inferred. Did not rerun generation or touch that output/user. A targeted
read-only verifier retained the byte/reward proof and checks unique isolated user paths while
allowing external presence. All staged overlays/users are treated as potentially played.
Neither player outputs nor save backups were rewritten/deleted.

All four full gates remain mandatory; no earlier checkpoint was posted ready.

## Priority follow-up: Market re-entry crash

Claude/Kareem reported the old `market-bottle-next` run: Boomerang granted; lesson/potion
skipped; bug remained; after leaving/re-entering the merchant remained frightened and talk
crashed. Read-only log confirms overlay merchant read417,7.4fps at3063, skipped indirect
call0 at3078, FATAL indirect call1061fce5d8/lr8124948c at3079, backtrace3083.
The precise native failing callee is unproved; incomplete tutorial finalization is demonstrated.

Read all six copied saves and the original backup. Played manual01/autosave04:
Present/Started/Cleared true, Boomerang IsGettrue/stock1; Insect_Delete and
Shop_Bottle_Insect_Appeared false. Thus the reward and our three writes completed before
the reported re-entry crash. Native post-catch Event134 sets Insect_Delete; Event45 sets
Shop_Bottle_Insect_Appeared; Event65 Wait ->63 schedule-select ->62 force-cancel-arrival=false.
The bug module creates on Started and deletes on Insect_Delete. The first conditional NPC
schedule reads Shop_Bottle_Insect_Appeared and uses normal Talk/relaxed behavior. All five
native completion flags and the native quest completion are now reproduced; no bottle step.

Bottle evidence: native Struct entries identify five IsValid Bools and content Enums.
Original manual01 and played manual01 each have exactlyone valid bottle
(valid0xf39ce410 true, the other four false). Content0x7d48df76 changed Bug ->Empty.
**Kareem clarified he emptied it himself before the test**; no extra bottle and no potion
refill, as designed. No bottle-consumption fix is introduced. A conservative accepted-offer
subflow audit covers324 nodes/eight flows: only Boomerang pouch-add, get-window/history and
its cure check; **no bottle action**. Retain “every bottle/contents untouched” in the checklist.

Cause-specific implementation clones the native Wait/schedule-select/arrival-reset actions
after setting the two missing native flags alongside the original three, then quest completion.
No new saved state, vanilla flow edit or bottle mutation. Synthetic native-state regression:
**3 passed**; actual new common-writer output **two resources**, flow99536 ->101512,
allocation99824 ->101808, full native inverse and final-state replay pass. Original played
overlay SHA256 map unchanged (`bottle-fix-proof.json`); user/save evidence untouched.

New output ONLY `ingame/market-bottle-fix-next`; new unrun launcher
`Test - market-bottle-fix-next.bat` and `bottle-fix-check.md`, own fresh user copied from the
original backup at launch. Checks cover bug removal, relaxed animation, re-entry/talk/shopping,
Save/Continue and all bottle contents. **The old output is superseded and must not be reused.**
Bottle remains held pending Kareem's full re-entry result; no runtime crash fix is claimed yet.

Priority interruption: own gate job was cancelled while waiting for another holder. Its saved
results contain only format244/lint passes; **no synthetic or dump run completed** and no
other agent's lock was removed. Full four gates restart after the requested source follow-ups.
Kareem also approved fixed20 for both first-expert gallery pool items; implementation follows.
