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
