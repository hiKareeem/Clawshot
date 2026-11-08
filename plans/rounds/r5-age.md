# Round 5, track A: age travel (cs5a)

Branch `r5/age`. Dump and save backups read-only; no game, launcher, window or terminal-control command run.

## Item 1: the age-change gates

Read AGENTS.md, README, plans 00–04, decisions and all four round-4 reports before changes.
Research scripts and decoded observations stay in `E:/OOTRemake/work/r5-age/`.

- `DoorOfTime:DoorOfTime_CheckStoneNum`, Event38/Event39/Event56, reads
  `Get_StoneOfFire_IsCompleted_Exp` and `Get_StoneOfWater_IsCompleted_Exp`, not stone inventory.
  The normal route already completed the Deku Tree. The escape/moat/song sequence advances `Step_DoorOfTime`.
- `DoorOfTime:DoorOfTime_OpenDoor`, Event27, calls `Dm_SY_Ocarina:PlayOcarinaSequence` with `MelodyType = 4`.
  Event60 requires `DoorOfTime_IsAfter_Step04_Exp` (quest beyond Step04); Event69 requires the door not already
  opened; Event58 requires `Dm_TimeTemple_0010` not already played; Event28 checks the recommended melody.
  Event17 runs the door scene and Event53 sets `Market_Child_TimeTempleDoor_Opened = true`, then Event57 moves
  the quest to Step06. Thus the vanilla route needs the three stone quests, moat Ocarina of Time and Song of Time;
  **the flow does not independently test Ocarina of Time inventory or the three stone items**. Keep round 4's
  conservative door rule for chest-only seeds; gifts shuffled independently need story-gate review (posted).
- `Market_Child_Prefab_e700` links attention actor `Obj_TimeTemple_MasterSword_A_01_e482` to two requests:
  DoorOfTime exactly Step06 for the first pull; AllSage after Ready for later pulls. `DoorOfTime:DoorOfTime_Draw`
  Event23 chooses the first-pull route unless `HavePlayedEvent.Dm_TimeTemple_0040` is set; Event99 plays
  `Dm_TimeTemple_0030`, which displays the sword; the SageRoom chain grants it and sets adult era.
- **Returning really is gated by Forest completion.** `Market_Adult_Prefab_89da` node 0 reads
  `SageOfForest_IsCompleted_Exp`; node 1 inverts it; node 2 feeds that into `Logic_Delete` of
  `Obj_TimeTemple_MasterSword_A_01_b347`. Its `ReceiveDoAction` drives the adult-to-child request.
  `Market_Adult_Prefab_edc2` also ANDs the same expression with the arrival area to trigger Sheik's scene.
- GameDataList: `SageOfForest_IsCompleted_Exp` is an unsaved `BoolExp`, Hash 1371974465, operands the Enum
  `Step_SageOfForest` (Hash 2841849034) and `Complete` (Hash 1275749364). Its meaning is quest-completed,
  not owning Forest Medallion or learning Prelude. `Dm_SY_BancChange_EscapeDungeon` Event199 sets that quest
  Complete: the boss/blue-warp completion route, not a shuffled medallion.
- `Market_Adult_Field_AdultToChild:Market_Adult_Field_AdultToChild` plays `Dm_TimeTemple_0070`, swaps equipment,
  Event1 sets `Sequence_IsChildhood = true`, Event0 reserves child Market, boot event `Dm_TimeTemple_0075`.
  Event3 only then reads `Market_Adult_Firsttime_GobacktoChild`; Event9 sets it. This is history, **not unlock**.
  It also refuses while a minigame timer is counting; timer/trade expiry is not represented by existing logic.

Source corroboration (facts only, no guide text copied):
https://www.nintendolife.com/guides/zelda-ocarina-of-time-forest-temple-walkthrough-switch-2
("Where to go after the Forest Temple"): after Forest, return to the temple, learn return travel and Prelude.
The actual pedestal's dependency is Forest quest completion, not Prelude inventory.

### Save evidence and missing prerequisite

Read all twelve `*/slot_*/progress.sav` under the two supplied backup directories with `clawshot.save`.
Every one has `Sequence_IsChildhood = true`, `Step_SageOfForest = Ready`, both
`HavePlayedEvent.Dm_TimeTemple_0040` and `Market_Adult_Firsttime_GobacktoChild = false`.
DoorOfTime is NotReady or Step02. These are child saves, not the current adult playthrough; no current live save
was read while Kareem plays. **Kareem: provide a new read-only adult save backup, before and after the Forest
blue warp if available, to corroborate `Step_SageOfForest` and the return pedestal in game.**

One research command failed on a nonexistent guessed `Market_Adult.bfevfl.zs`; the exception printed the exact
missing path. The asset listing showed only the two era-transition files, removed the nonexistent input,
and the aimed rerun completed. No game or save bytes were written.

## Cross-track notes

- Posted the real Forest gate and child-only backup evidence on `cs-r5`.
- Gift owners: the Door of Time reads stone quest progress, not stone inventory; independent stone/song shuffling
  must preserve those story gates. The age-return gate likewise uses boss/blue-warp completion, not the medal.
- Item 4 investigation: no independent return-unlock Bool was found. `Market_Adult_Firsttime_GobacktoChild` cannot
  open it. Forcing `Step_SageOfForest = Complete` would falsely complete the entire Forest quest and affect every
  other reader; it is not a safe free-travel flag. This is a conditional spec prerequisite, not permission to
  ship an ineffective flag or silently mark Forest completed. Requesting reviewer direction on an isolated
  data/logic patch instead; continue with the default gated search and softlock proof.

## Item 2: separate pre-pull inventory

Reviewer approved data wiring: `world.toml`'s `age_return_event = "Defeat Phantom Ganon"` and
`age_return_region = "Beyond Door of Time"` (isolated commit `23d30c1`); no loader change was needed.
`World.age_return` derives the pair from settings. Missing gates in partial worlds remain closed.

`Search` now maintains a child-prefix inventory until the gate event holds and adult can reach the pedestal.
Adult gets child-prefix and adult finds; child cannot consume adult-only items or events before return.
Child-prefix reachability keeps growing independently, so the solver can finish all available child errands
before choosing the first pull even if the pedestal is discovered early. An adult-collected check that later
becomes reachable in that prefix is promoted without granting its item twice. Aliases follow the same provenance.
Adult-start worlds have no child prefix before return. Public `collect()` and constructor items are assumed
precollected items, available to both views; real placed pickups go through provenance-aware sphere collection.
No gate in a synthetic world preserves the existing unrestricted behavior.

Reproduction before fix: `pytest tests/test_age_travel.py -q` printed two failures: an adult Hookshot opened
the child ledge and its own return key, and an adult start collected the pre-return child key. One positive passed.
After fix: targeted age/search tests plus vanilla-world beatability **15 passed**.
Live library smoke via `uv run python -c` on the same synthetic world:
- Key requires adult-found Hookshot as child: only Adult Item collected; counts Time Travel/Hookshot;
  child ledge unreachable; goal false.
- Key already reachable in the child prefix: Adult Item + Child Key, then Child Prize; Forest Clear and goal true;
  each physical item counted once.

Regressions also cover adult event leakage, needing the actual adult pedestal, already-collected check promotion,
alias counts and repeated collection, and public assumed inventory. Full seed/gate checks follow at handoff.

## Reviewer direction on item 4

Reviewer replaced the conditional initial-value approach: implement `patch/age.py`, default-off `free_time_travel`
as an isolated pedestal-placement edit, dump field-diff test, and a test overlay for Kareem. Do not fake a Bool
or complete the Forest quest. Also trace what else Forest completion controls. Fast-start TOML may need no edit
if its existing schema cannot express placements; the seed owner must wire the new patch alongside the logic flag.

## Item 3: first-pull softlock and proposed guarantee

**Proposal for Kareem/reviewer:** with gated return, require Forest completion and the adult return pedestal to
be reachable using only adult checks plus the inventory **mandatory for the earliest first pull**. Optional
child checks must not be assumed in that proof. A merely beatable seed proves there is an order, not that an
early pull is safe. An alternative is explicit free travel (item 4), after its in-game check; changing its
default is Kareem's product call, not this track's.

`test_beatable_seed_can_still_softlock_on_an_early_pull` exercises the exact counterexample: a child key is
available before pulling but optional. The normal child-start solver collects it and wins; an early adult
start without that key collects the adult Hookshot but cannot clear Forest or return; carrying the child key
before pulling clears Forest, returns, and wins. Targeted regression **1 passed**. A live library smoke printed
the three corresponding sphere/Forest-clear/goal states: true/true, false/false, true/true.

This proposal is **not silently added as a seed-rejection policy**: computing the mandatory first-pull inventory
for arbitrary gift/logic settings, or forcing free travel on, is a separate accepted product guarantee.
The implemented model rejects temporal circular dependencies, but it does not claim every player choice is
softlock-proof. **Kareem: should seeds with free travel off guarantee return after the earliest possible pull,
or is a spoiler/play-note instruction to finish required child checks acceptable?** Recommended: the guarantee,
or free travel after its pedestal test, rather than relying only on a play note.

### Item 3 reviewer decision: enforce it provisionally

Reviewer subsequently required default-on `age_return_guarantee`, with off reserved for future play-note mode.
Implemented in `Search.won()` for actual placement searches, so the existing seed acceptance oracle enforces
it without altering assumed-fill reachability. It is irrelevant to a child-only goal that never opens travel.

The proof derives mandatory logical item counts from the actual seed: collect the maximal child-only prefix;
for each non-event inventory count, binary-search the smallest cap with which child-only collection still
reaches the first-pull event. These minima include prerequisite items on the route (not only the door's direct
requirements). Start inventory remains available. Then start an adult-only search with exactly those counts
and the first-pull event; optional child checks/events remain unavailable until the normal gate/pedestal opens.
Aliases are raw logical counts in that proof, not collected again. Alternative routes with no individually
mandatory item may be rejected conservatively. `age_return_guarantee = false` skips only this extra guarantee,
not the chronological two-age model.

An initial direct-door-item prototype rejected vanilla: diagnostic output showed adult meadow false and Saria's
Song absent. An interim all-other-items-up-front trial also missed it because assuming the stones bypassed
their own child-dungeon prerequisites. Replaced it with actual-placement count caps, not a special-case song grant.
Live vanilla smoke then printed Saria's Song, Lullaby, bracelet, Bomb Bag, Boomerang and other actual child
prerequisites in the mandatory intersection; return safe and won both true (with the vanilla test's explicit
up-front dungeon-key caveat). Targeted age/search/vanilla run: **20 passed**.
One diagnostic command imported a test-only helper from the wrong module (printed ImportError); the corrected
diagnostic constructed the vanilla mapping directly and printed the blocked frontier before the fix.

Additional small request from cs5c: `GanonBossKey` added to `DUNGEON_ITEM_TYPES`, isolated commit `f2dadc2`.
The first live allowed() smoke expected the Tower chest to be a Castle location; printed region metadata showed
`dungeon = None`. Corrected the smoke to the real Castle trial (allowed true; Kokiri false), posted the separate
Tower metadata defect to cs5c for its world integration and permanent fill coverage.

## Item 4: default-off isolated pedestal patch

`src/clawshot/patch/age.py`, setting `free_time_travel = false` in `world.toml`, matching model behavior.
No fast-start TOML edit: its GameData/skippable schema cannot express placements, and the reviewer explicitly
rejected a fake return Bool.

In `Banc/Market/Market_Adult_Static.bcett.byml.zs`, find AiGroup Hash 2075259738076588912, not its list index.
Replace `Market_Adult_Prefab_89da` with the game's existing `SpiritTemple_Prefab_5299` module. Read-only decoded
module inspection shows exactly two nodes: attention `ReceiveDoAction` feeds the event request, and both
actors' `Logic_Delete` inputs default false. Rebind just the module input Ids:
`EventRequestActor_9bc1` → `EventRequestActor_7a32`;
`Obj_TimeTemple_MasterSword_A_01_b347` → `CheckAttentionActor_8348`.
Keep `Path`, `Reference`, the original actors/Hashes and their adult-to-child event unchanged. Validate original
module, both references, both actor identities and the event before changing anything; refuse a stale contract.
The transform reads its written BYML back; the common writer handles compression, output guards and size table.

`age.changes(placements, free_time_travel=False)` satisfies the new `PatchStep` contract.
`make_seed` automatically includes it when its resolved logic setting is true, so free-travel logic cannot
silently emit an unpatched seed. That shared-file-only wiring is committed separately. The initial eager import
caused Python's `-m` already-imported warning during the standalone smoke; moved the optional import inside
`make_seed`, and `python -m clawshot.patch.age --help` then ran without the warning.

### Evidence and player output

- Synthetic age/patch run: **18 passed**, covering exact tree change, stale module/reference/event refusal
  before mutation, free-travel chronological behavior and bypassed guarantee.
- `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_age_dump.py -q -s`: **1 passed**.
  Only the target group's Logic and two Ids differ; every actor, other group, table and byte order is preserved.
- Actual CLI `python -m clawshot.patch.age --romfs ... --out E:/OOTRemake/work/r5-age/free-time-travel
  --free-time-travel` wrote **2 files**: adult Market Static (30,540 → 30,596 bytes; compressed 9,733 → 9,695)
  and size table (entry 30,824 → 30,888; table length unchanged 1,761,406).
- Actual seed CLI, seed 7 / three-area Deku slice / `--logic free_time_travel=true`, wrote
  `E:/OOTRemake/work/r5-age/seed-free-smoke/`: **12 shuffled checks, 4 spheres, 8 files**, including the adult
  pedestal and raised size table. This exercises automatic logic-to-patch pairing through the real public CLI.
  It is not the requested whole-game player seed (track C owns those).
- Player instructions: `E:/OOTRemake/work/r5-age/free-time-travel-check.md`. No game/launcher was run.
  **Kareem: after the first pull but before Forest clear, check the overlay log, the adult pedestal prompt,
  child return and a second adult pull. No premature Forest reward/Prelude. Later, clear Forest normally,
  check the sage/reward occurs once and Sheik still teaches Prelude.** Default stays off until verified.

### Forest-step risk census

Section 16 lists the readers and their effects. Scanned all 914 flow files: the completion expression has
62 switch readers in 41 files; decoded logic has pedestal, Sheik and Mido readers. Direct quest-step readers
include the Forest Poe substeps, boss room Step07/Complete, SageRoom/LostWood Step09, adult Kokiri and child
Hyrule Field completion conditions. The escape flow's incomplete branch reserves SageRoom with boot event
`ForestTemple_SageOfForest_SageRoom`; Event211 runs `Dm_Awake_Forest`, Event213 runs its actual reward, and
Event199 completes the quest. Forcing Complete at New Game could bypass that real sequence; this patch changes
none of those readers or the Enum. Other completion-dependent branches include Saria's Song, arrival scenes
and numerous NPC/shop interactions.

The reused module has no room-specific node beyond its two bound actors [observed from its decoded graph],
but runtime compatibility, pre-Forest child revisits and the second pull still need Kareem's check.
The distinct Sheik area trigger (`Market_Adult_Prefab_edc2`) remains Forest-gated, so free travel does not
promise early Prelude.

### New backup and integration

Reviewer authorized rebase onto main `cd592e3`; completed cleanly before the pedestal work.
Read the six newly supplied nested saves in `2026-11-08_0802-before-adult/save/<user>/`: all also show
`Sequence_IsChildhood = true`, `Step_SageOfForest = Ready`, first-pull/first-return false, DoorOfTime
NotReady or Step02. Eighteen inspected saves in total, still no adult-ready backup; no live game save was read.
Posted all integration contracts and the Ganon Tower dungeon-metadata request on the thread.

## Commit ledger after authorized rebase

Base `cd592e3`, branch `r5/age`. Earlier inline/thread IDs before the rebase are historical.

| Commit | Scope |
|---|---|
| `036b008` | item 1 research and section 16 |
| `1bb8187` | isolated world gate data |
| `9a4f542` | item 2 chronological child-prefix search |
| `1833047` | item 3 counterexample/proposal |
| `fe72c12` | cs5c's isolated GanonBossKey model fix |
| `27e4667` | isolated default-on guarantee settings |
| `f3586cf` | reviewer-required mandatory-count/adult-only guarantee |
| `94ad473` | isolated default-off free-travel setting |
| `e2ff6b0` | item 4 pedestal transform, model, tests, evidence |
| `8356c6c` | isolated automatic seed-output pairing |
| `fba0c82` | isolated world-format documentation |
| `c2fa669` | explicit adult-after-pull search phase |
| `33a339b` | isolated return-kit data and preserved child dependency |
| `571a143` | isolated `generate/fill.py` forward return-kit stage |
| `8d39b8d` | source-family/key-bootstrap regression and failure evidence |
| `efbc291` | isolated return-kit fill documentation |

No merge, push, stash, dependency change, game/save write or game process.

## Full-gate failure and reviewer-directed fill constraint

First four-gate attempt: format **101 files**, lint passed; synthetic suite **318 passed, 27 skipped,
3 failed in 409.74 s**. The default 200-seed sweep rejected 147, progressive sweep rejected 10 of 20,
and determinism seed 4242 could not be generated; the `&&` chain therefore did not run the full dump gate.
No failing command was rerun unchanged.

Seed 0 diagnostics printed the real cause: normal goal true, return false, adult meadow false,
mandatory Saria's Song zero. Other child-route necessities were present. Its optional shuffled gauntlet
tiers let child get strength without Saria's unshuffled bracelet gift; after pulling early, adult cannot
pass Mido, and the song is not obtainable as adult. This is a genuine earliest-pull softlock, not a demand for
the optional 100-token reward. Ten diagnostic fill candidates showed two safe ones, several missing Saria
and others missing Forest gear. `generate` checks the oracle after its existing retry loop; no retry count
or acceptance assertion was changed.

Reviewer required a fill constraint, not reliance on rejection. Added a forward return-kit stage before the
normal assumed fill:

- Data names the logical source families (Bow, grapple, strength, Forest small/boss keys), the stricter
  bypass family (strength), and its safe lower-bound adult-start inventory.
- Every shuffled strength source must go to a strictly adult-only check, tested against maximum child access.
  This preserves the actual compulsory child Saria → bracelet → Dodongo boulder route instead of inventing
  an extra logical first-pull gate or moving an unshuffled gift.
- The safe lower bound is Ocarina 2, Song of Time (the actual door), Saria's Song and strength 1 (the preserved
  child dependency). No optional child chest, Bomb Bag, wallet or boots are assumed.
- Forward-place the staged sources at adult-reachable checks with that inventory and already placed/vanilla
  adult pickups. Small keys bootstrap first; if further keys need another item, place that reachable item
  next. Boss keys cannot consume the only reachable entrance-key chest first.
- Then the existing assumed fill handles the remainder; the independent mandatory-count/return oracle still
  checks every generated seed. Free travel or guarantee-off skips this extra placement stage.

`Search.adult_after_pull` is the explicit phase constructor used by that stage.
Synthetic regression `test_age_fill.py` shows a child-only song/bracelet route, shuffled bypass tier forced
into the adult dungeon, two keys bootstrapped from zero, and return without optional child loot.
Targeted fill/age tests **15 passed**. Live generation of previously failing seeds **0, 93 and 4242** succeeded;
their mandatory Saria count is now 1 (seed 0 actual return proof also printed true, 21 spheres).
The unchanged full 200/progressive/determinism tests and full dump gate passed after this aimed fix (below).

Removed the disposable `seed-free-smoke` output created by this session after its observed CLI proof; the
requested `free-time-travel` player overlay and read-only research material remain outside the repository.
Removed incidental error-wording assertions from the new tests; they assert the rejection type and state instead.

## Final gates and handoff

Base `cd592e3`, through `efbc291` plus this final report. Earlier failure results above are superseded by:

| Command | Result |
|---|---|
| `uv run ruff format --check` | **102 files already formatted** |
| `uv run ruff check` | **All checks passed** |
| `uv run pytest` | **322 passed, 27 skipped**, 208.49 s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | **26 passed, 323 deselected**, 227.95 s |

The synthetic run includes the unchanged 200-default-seed, 20-progressive-seed, cross-interpreter determinism
and vanilla-placement checks. The dump run includes the isolated pedestal field-diff oracle, all placement/
GameData/EVFL round trips and seed-output checks. The earlier 147-seed rejection is fixed by construction,
not skipped, weakened or hidden behind more retries.

Delivered: data/source age gates; chronological inventory; default-on early-return proof and forward fill
constraint; default-off isolated free-travel placement patch automatically paired with seed logic; tests,
section 16, world-format documentation and player overlay/instructions.

Still for review/Kareem:

- **Confirm the provisional `age_return_guarantee = true` default and whether free travel should later default
  on after its in-game check.** Off-by-default free travel is not claimed to work in game yet.
- **Run `free-time-travel-check.md` on a disposable adult-before-Forest save copy**, with overlay log evidence,
  child return/second pull, no premature Prelude/reward, then normal Forest sage/reward and Prelude afterwards.
- Current known save copies are all child-era; an adult-ready read-only backup is still needed.
- Gift integration that shuffles `GC Darunias Joy` must preserve/rebuild the compulsory child strength anchor:
  the default return-kit data deliberately relies on the unshuffled Saria → bracelet route. Posted to cs5d/cs5c;
  the independent finished-seed oracle rejects violations. Chest/Shop-only pools retain that gift.
- cs5c owns the separate Ganon Tower region's missing dungeon metadata and permanent fill coverage; this branch
  contains only the requested GanonBossKey classification. No Tower metadata fix is claimed.

Requested player overlay retained: `E:/OOTRemake/work/r5-age/free-time-travel/` and its adjacent check note.
No game/launcher was run; dump, backups and live game files were never written. No dependencies changed.
All commits remain on `r5/age`; no merge or push. Final report commit ID is given in chat and the thread.
