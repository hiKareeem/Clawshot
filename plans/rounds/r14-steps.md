# Round 14: quest-step audit (cs14e, issue #25)

Branch `r14/steps`; baseline main 0.2.0 (published 2026-11-13). No version change.

## Scope and safety

Read-only audit of supported build `e0f3ccfa`: direct AINB/EVFL step reads and writes,
GameData expression dependency closure, and resource consumers. Reproducers and full
machine tables live under `E:/OOTRemake/work/r14-steps/`, never in this repository.
GPL sources/decoders supply facts only; no code is copied into Clawshot. No agent
game start, merge, push, hc/herdr, original-save modification, or writes to game/
Longshot folders. Disclosed control-save copies stay under the external work folder.

Track C retains Zelda/Door of Time/Kaepora and Hyrule Field/Market/Castle world files
and `fast_start.toml`. Track D retains `world.toml`/`bombs.toml`. Findings in those areas
are requests, not overlapping edits. Section 48 and `tests/test_story_steps*.py` belong here.

## Method and work in progress

- Native AINB census, including packed modules: `work/r14-steps/ainb/`.
  11,707 occurrences / 5,036 distinct streams, zero decode errors.
- Native EVFL reads/writes, entry/branch effects and hand-over continuations:
  `work/r14-steps/evfl/`; 914 files, 901 active versions, 676 step-read rows,
  332 write rows (316 active), 502 schedules, zero decode errors.
- GameData dependency closure and BYML/resource consumers: `work/r14-steps/`.
  The corrected pass decoded 149,463 BYML resources, including 1,432 v5 Effect
  resources and binary Tag/BGM values, with zero errors in 53.781s. It examined
  3,060 opaque blocks (1,021,808,198 bytes), retaining three aligned-hash candidates
  as unproven references. Research-only reader; production formats unchanged.
- Supplementary lexical surfaces: `other-reference-coverage.json` and
  `other-reference-candidates.json`; zero errors in 23.016s, 171 candidates.
  The three resolved quest-expression strings occur only in compression
  dictionaries, not execution sites. Motion/UI/message names remain labelled
  lexical candidates; none is promoted into the joined consumer table.
- Compare gates against translated world plus remake overrides and fast-start presets;
  distinguish actual mismatches from source-bound continuation preserved by gift swaps.

`classified-all.json|csv`: 5,226 joined rows; 4,209 read occurrences, 332 EVFL
writes, 116 AINB write/action rows, 522 configuration rows and 43 literal/binary
references. Read classes: a 2,935; b 513; c 761. The 799 review markers include
configuration, linked values and missing scene attribution; these are not
silently promoted to per-row safety proofs. The AINB report separately retains
30 linked/blackboard parameters, 11 unmapped sink instances, 38 dead outputs and
three decoder warnings. EVFL retains 11 unresolved non-step operand hashes.

Played evidence is attributed to Kareem via Claude. The river pair below has
now been played; static decoding alone still does not establish engine behavior.

## Preliminary findings and rejected leads

- All 45 Challenge rows resolve to saved `Step_<challenge>` enums. There are 329
  expressions directly reading those enums and 391 in their transitive BoolExp
  dependency closure. Checking only names containing `_IsAfter_` misses composites
  such as Zora water/alternate-scene and Kakariko burning predicates.
- RSDB adds 182 per-step participant schedule bindings and eight automatic
  `ForceProgressGameData` conditions. The field's engine transition semantics have
  not been executed: the audit records containing step and condition, not an
  invented next-step write.
- **Rejected Minuet self-lock lead:** `SacredForestMeadow_Adult_Prefab_03df`
  requests `ForestTemple_SageOfForest_MelodyGet` from player contact and unplayed
  `Dm_MelodyGet_Forest`, not Forest progress or Hookshot ownership. The nearby
  `SacredForestMeadow_Common_751d` after-Step04 predicate has no consumer.
  `UnderTheGrave_Prefab_6971` really does write Forest Step04 from exact Step03
  plus `IsGet.Item_Hookshot`; this fact alone does not imply a Minuet gate.
- Kokiri short-stock/full-stock appearances are opposite polarities of
  `Meet_DekuTree_IsAfter_Step02_Exp`, not missing shops. Native indices 2/6/7
  (world slots 3/7/8) are available before the meeting; indices 0/1/3/4/5 have
  the release predicate. `shops.toml` already models this through the corrected
  Mido event, including the Mido-skip abstraction. No new shop fix follows.
- **Rejected Saria farewell lead:** the post-Gohma village Saria (Hash
  `7299789031121947235`, group `..._e163`) is not the bridge gift participant.
  The gift's group `KokiriForest_Child_Level_All_02_ddcd` requests its event
  directly on player contact until `Dm_Kokiri_0150` has played; the event's own
  Bool creates bridge Saria (Hash `1660754835063030086`). It has no quest gate.
  `Goto_HyruleCastle:KokiriForest_ArriveLostWood` then plays `0150`/`0155`;
  `0155` Event68 grants the Fairy Ocarina. A proposed Gohma prerequisite failed
  three exploratory model assertions, but those expectations were disproved by
  the complete actor/event trace and the speculative test file was removed.
  No unsupported Gohma requirement is added to the world.
- Track C received the baseline Malon/Talon/ranch-airwall and Zelda/Impa
  presence consumers. They are not edited here.

## Confirmed mismatch: Epona source progression

Proposed by cs14e from native EVFL; Claude approved ownership/implementation on
2026-11-13. `Get_Epona/AfterGetEponaSong` has one writer,
`Dm_MelodyGet_Epona` C07/Event82, after the Song from Malon source reward.
Adult Ingo Event12/Event90 and adult Malon Event178/Event86 require progress past
`ReadyForGetEponaSong`. A remotely found Epona song cannot execute that source
write. Gift rewriting skips only the shared pouch-add demonstration Event60;
the source tail, including Event82, stays intact.

Change: existing `remake/child_lon_lon_ranch.toml` adds `Malon Song Source Cleared`
with the existing child/day/instrument/Talon-wake source rule. Both `Epona` and
`Links Cow` additionally require this event, retaining playable adult Epona song
and day. Translated `lon_lon_ranch.toml` is intentionally unchanged, following
the world-format override contract. No item, quest default or new skip is granted.
This changes logic/fill/output for affected seeds; version is not bumped here.

`tests/test_story_steps_epona.py`: **before 3 failed / 4 passed**, with the
incorrect adult Epona/Cow counts printed; **after 7 passed in 2.44s**.
The tests distinguish source completion from its shuffled reward, preserve
instrument/Talon requirements, and do not let source progress replace the song.
Full suites and public generation sweep remain queued.

## Confirmed mismatch: Darunia's missable source

Proposed by cs14e; Claude approved option 1 on 2026-11-13 (Kareem may overturn).
`fire_quest.py --cache evfl/cache/decoded.pkl` reproduces the native trace;
`fire-quest-trace.json` records exact nodes, payloads, branches and step order.

- `DeathMountainTrail_Child_Prefab_ffa7` node8 writes `DungeonStart` on boulder
  death while the quest is earlier. It does not require Darunia's dance.
- `SariaMelodyPlay` is step15; `DungeonStart` is step17. `Get_StoneOfFire`
  Event39 takes true/case0 to repeat Event42 after step15, rather than
  false/case1 Event31 → `Dm_Goron_0030` → gift Event127. Early bombs/Bracelet
  can therefore pass the source's reward cutoff.
- Boss entry Event4 writes `BossBattle`; defeat Event8 writes `EscapeDungeon`.
  The blue-warp completion checks only not-Complete, plays the native Darunia/
  Fire Stone scenes, then writes Complete (Event46). No dance prerequisite
  appears in that chain. This is static evidence, not an executed game route.

Options requested by Claude, in preference order:

1. **Approved:** gate the gift by its own collected Bool
   `HavePlayedEvent.Dm_Goron_0030` (existing saved Bool, default false), explicitly
   write it after Event127, and guard Event121 so the quest only moves forward.
   Remote strength ownership must not count as source collection.
2. Suppress/defer the boulder step jump. Insufficient alone: boss entry/defeat
   also pass the cutoff; rock deletion/persistence is coupled to later steps.
3. Keep only non-required filler at this check, move required strength elsewhere
   and remove the D20 source anchor. Early-opening players could lose its
   optional reward. Not selected.

Approved D/E contract: E's source-once/forward121 transform first; D's
`progressive_bonus` transform second, reading prior changes. D owns only the
Event127 wrapper and preserves its next pointer; E owns Event39, Event121 and
the post-gift Bool. Grant parameters stay native. D merges first; E rebases and
must prove the combined real-dump flow. The implementation and synthetic paths
pass; combined proof/staging awaits D's merge and E's rebase. D retains its
recorded dependency until the fix lands.

The wider decoded audit covered all 37 active gift-bearing step reads and
1,517 AINB sink rows. No further confirmed source-loss mismatch: trade retries
cover both sides, source-local Complete writers retain their rewards, and
bridge Saria remains ungated. Granny Blue Potion was a rejected polarity lead:
`Npc_Hylia_053_Adult` Event3 true/case0 (`>Step05_01`) unlocks the sale.
`gift-step-cutoffs.json` retains per-case gift effects. Hash-only references,
dynamic bindings and opaque binary payloads are not treated as proven reads.

## Confirmed mismatch: field-side Zora River entry

**Paired Longshot result (Kareem via Claude, 2026-11-13; saves verified by Claude).**
Both native probe resources loaded, with no crash:
`Banc/ZoraRiver/ZoraRiver_Adult_Static.bcett.byml.zs` and
`Logic/ZoraRiver_Common_08f0.logic.module.ainb`. No visible rocks in either control.

| Control | `Step_Get_StoneOfWater` | `Zorariver_BrokenRock_Broken` | Observed result, also after reload |
|---|---|---|---|
| Negative | Ready (enum value `398436934`) | false | Large invisible wall at the Hyrule Field doorway, spanning the river to the other bank; no glitchless way around |
| Positive | Step03 (enum value `1871805950`) | false | No invisible wall; passage open |

The named values persisted across Claude's verified snapshots. The diagnostic
copies changed only that enum and the rock Bool; neither control proves the
rock-true branch in play. No agent launched the game.

### Exact native predicate and rock branch

`ZoraRiver_Common_08f0` has seven wall nodes, with two placed age variants each:
nodes `1/3/4/10/11/12/13`, instance suffixes
`a664/ce56/949e/d780/95d7/afa6/2c3b`. Every `Logic_Create` is node 8's
`OperateOR.False` output:

```text
NOT(Zorariver_BrokenRock_Broken
    OR Get_StoneOfWater == Step03
    OR Get_StoneOfWater > Step03)
```

All seven `Logic_Delete` and `RespawnTrigger` inputs are unconnected false
defaults. Node 5 reads the saved rock Bool; node 9 supplies equality/after.
Nodes 0/2 bind entrance rocks `Obj_BrokenRock_A_01_71ea`/`_c155`;
their `Dead`/`IsDeathProcedureComplete` outputs feed OR node 7, then node 6
`TriggerGameDataSetBoolTrue(Zorariver_BrokenRock_Broken)`. No weapon-type
condition qualifies that write. The walls are **not step-only**.

The river rocks use `Obj_BrokenRock_A_01`, inheriting `WallCrack`. Its
`CrackStoneObject` damage table accepts Hammer (`85358548`) at rate `100.0`,
with finite life; `StaticCrackObject` supplies `ReactionForHammerAttack`.
The `Weapon_Hammer` pack identifies that same Hammer enum. Hammer shockwave
damage is disabled here: the supported alternative is direct strikes, not a
ranged slam. Kareem confirms Hammer breaks rocks generally; the river Hammer
alternative is actor-data evidence, not a newly played third control.
Only those two actor packs were read for this follow-up, not a native sweep.

### Step03 source and implemented rule

The exact writer is `Dm_SY_BancChangeArrive:Goto_ZoraDomain`: Event48 plays
`Dm_Zora_0000`, then Event46 reads `Get_StoneOfWater_MeetImpa`. False/case1
goes to Event44 (`Step03`); true/case0 goes to Event45 (`Step03_Impa`, later
than Step03). Both use `EventExecuteProgressChallengeStep` with
`IsIgnoreCompletedChallenge=true`. No Water step has `ForceProgressGameData`.
Both river-to-Domain entrance actors (`8680147983491088093` child,
`4848284814404943915` adult) bind `InitEventName=Goto_ZoraDomain` and
`InitEventFlag=HavePlayedEvent.Dm_Zora_0000`.

cs14e proposed the source-bound event; Claude approved the rule conditional
on confirming the rock predicate, then requested the Hammer alternative
after Kareem's report. Both conditions were checked and posted before the
implementation/commit. `child_zora_river.toml` now adds persistent event
`Zora River Domain Arrival` at `ZR Behind Waterfall`, rule `True`: that
region has the free transition into the Domain. The field-side edge is:

```text
can_blast_or_smash or 'Zora River Domain Arrival'
```

The existing helper means usable explosives or usable adult Hammer. This
does not grant the event merely for owning a song, reaching the river or
being adult. Lost Woods entry and reverse Domain/waterfall exits stay intact.
A first-visit child can still break the rocks with usable explosives; a
diving Lost Woods entry also remains available where its existing rule allows.

### Affected model and fixture impact

- Changed rules: only `ZR Front -> Zora River` plus the new source event.
- River checks inheriting that route: Open Grotto Chest; both freestanding
  Heart Pieces; all seven frog checks; Magic Bean Salesman; four Skulltulas.
  Existing age, item, once-only and shuffle-policy restrictions remain.
  The frogs' initial/retry grant definitions group to one Ocarina Game check.
- Downstream Domain/Fountain/Ice access can occur later when the field route
  was the only early-adult route. Their local rules are not changed; alternate
  entry remains valid. No check IDs, pool contributions, native file edits,
  GameData presets or new resource requirements are introduced.
- Placements/spheres/spoilers and seed hashes can change, especially with
  early pulls. Default closed-door prefixes already visit the Domain; no
  universal hash-neutrality claim is made. Rebuild combined generated-output
  fixtures after rebase; the unchanged native input working set can be reused.
  No old golden hash is repinned. Release/version decisions remain Claude's.

Focused consumer regressions: **8 failed / 6 passed before the rule**, with
printed inventories/source state; **14 passed in 2.00s after**. Coverage:
blocked early adult, insufficient Bomb Bag alone, usable bombs before the
source, adult Hammer, child Hammer refusal, saved source without tools,
both age variants, Lost Woods alternative and reverse Domain route.
Compiled public-search smoke exercised six corresponding scenarios and
the actual Open Grotto Chest access. Its initial harness incorrectly used
`holds()` for an externally assumed saved event; the printed state showed
the route open, and using the rule's public `counts` state fixed that harness.
No product change was made to mask that diagnostic.

Full format/lint/synthetic/dump gates remain scheduled only after D merges
and E rebases. Research evidence and smoke output are external
`river-rock-actor.json`, `river-rock-Weapon_Hammer.json`,
`river-logic-smoke.json` and `river-stage-proof.json`; decoded data stays out
of the repository.

## Decision: refuse unpaired advanced logic settings

The baseline public validator accepted these OoT-derived overrides without a
paired native quest/flag patch:

- `open_kakariko='open'`: model bypasses the child mountain gate; native shutter
  uses Fire quest progress from the guard's Letter hand-over.
- `gerudo_fortress='open'`: model bypasses native rescue/clearance; D39 retains
  the captain and Spirit-step sequence rather than implementing an open fortress.
- `scarecrow_behavior='free'`: model precollects Scarecrow Song; native custom-song
  registration/quest is untouched.
- `skip_child_zelda=true`: model source rules can bypass the Talon/Egg route;
  C's actual courtyard/quest patch is not a Skip Zelda implementation.

Reproducer/result: external `unpaired-logic-settings.json` (actual public
`validate` + `prepare`, all four accepted). Defaults are not changed by this
observation. No new native skip is proposed.

**Decision (Claude, 2026-11-13, under Kareem's standing rule): REFUSE.**
Track E owns the validation cutover. `data/settings.toml` explicitly lists
supported non-default values: free travel, return guarantee, key/forest/Mido/
door modes, plus world-derived return-kit values written into effective recipes.
Unchanged world defaults remain allowed; new OoT non-default keys are refused.

The policy covers CLI overrides/printed recipes, app dict/string validation and
native seed generation. The CS1 codec and standalone `generate`/`prepare`
remain generic for synthetic/custom logic models; they do not write a game mod.
No settings serialization, preset or community recipe is changed. Regressions
cover every unpaired Boolean key, explicit unimplemented access modes, supported
modes and effective door-recipe replay. Malon's new source rule no longer has a
`skip_child_zelda` branch. Allowlist-only commit `a153327` was cherry-picked
alone onto published `9f67400` as detached scratch commit `b258fa3`.
Gated real UI-job regenerations passed on that checkout: standard
`3EA5D532A06B` (146 resources), keys `14B0424D9E97` (148 resources).
Both shares validated; both full SHA-256 digests matched the published output.
Per-file comparison found zero added, removed or changed files in either.
Separately, the combined build must still report new hashes and per-file
differences: Darunia changes mod files.

Integration diagnostic: D's current kit replaces the old strength-family count
with native Bracelet ownership. Checking the stored effective kit would refuse
both old in-branch recipes even though `prepare()` replaces it. The policy
therefore ignores only the two fields it can prove that compiler path always
regenerates. Mode-table overrides remain checked. Claude confirmed this narrow
scope; share-version checks stay strict and no legacy migration is added.

The first allowlist-only attempt validated both shares but generated neither:
the real UI job refused a nonexistent output parent. The external harness
created that parent; the authorized retry passed both recipes in 142.016s.
The success post included both exact hashes, then `E SHORT BATCH DONE`;
the lock was released. Evidence: `community-allowlist-only-results.json` and
`allowlist-only-regeneration.log` outside the repository.

## OotrR cross-check

Maintainer requested the four remake leads from **OotrR (Mozencaz, MIT)** on
2026-11-13. Read-only clone HEAD and MIT `LICENSE` verified at
`fdc2b2f26ba146b60f565aa83892ccd8bb25acdc`; no code or rule copied.
All four verdicts, native source nodes and model consequences are recorded in
`03-game-data.md` section 48. Detailed retained-cache trace and bean-anchor
measurements are external `work/r14-steps/ootrr-crosscheck.json`.

cs14e proposed rejecting Saria's extra Fire gate from the scene-before-journal
trace; Claude accepted that verdict for C. The chest lead confirms a bean
destination 2.933 m from the existing excluded check, not its route exclusivity
or copy identity. Rauru's first-pull source is already modelled and held vanilla.
The farewell's extra Gohma gate is independently refuted by the earlier played
`R6-CLOSEDDEKU` counterexample. No world rule or shuffle policy changed.

Metadata smoke, actual `load_world()` invocation: farewell location is
Cutscene/Fairy Ocarina with `keep_vanilla=None`, `n64_only=None`. Thus
`vanilla_fixed` is the canonical item tier, not a shuffle exclusion. This
check does participate in Gift shuffle; its pre-Gohma source is proven.
Research used retained native caches, not a second dump scan or new game run.

## Verification and handoff

Focused settings/codec/forest/Epona/Darunia/key-binding regressions:
**861 passed in 104.06s**. Selected allowlist Python files formatted/linted clean.
Actual browser UI: an Open Kakariko share is refused with the explicit unsupported
message; the valid community keys share subsequently applies `anywhere`. The
error banner is above the paste field (visible after scrolling); no UI code changed.
Browser and isolated-preference server closed. No generation or game invoked there.

Full serialized gates, combined-build community regenerations, combined native
proof and Darunia staging remain pending. The combined proof now uses a full
production world, not the Gohma slice that excludes Darunia from D's source scan;
it checks child ownership versus adult-only ownership, source-once behavior and
forward-only Fire progress through the written shared-pouch guard.

Latest maintainer queue: D fixture/dump on `18a04cb`, C matrix,
D 300-row sweep, A dump, then E full gates. C stages its own in-game check
meanwhile; its merge also awaits Kareem's result. D must merge and Claude
authorize E's rebase before combined proof/staging. The river pair is now
played and confirmed above; Darunia remains unplayed. No full-gate pass claim.

## Topic commits before integration

Claude requested committing the finished work before D merges, then remaining
idle until explicitly told main moved. No rebase or additional gate run is
authorized by that request. The topic commits are:

- `c8cef31`: Epona/Malon source prerequisite and regressions.
- `7dbc5d7`: Darunia source-once/forward-only transform and regressions.
- `8d934d4`: narrow settings allowlist replay follow-up; base allowlist commit
  `a153327` is preserved unchanged for the published-source neutrality proof.
- `3c4e027`: section 48, census coverage and attributed OotrR cross-checks.
- `4e3ed9c`: the then-final round-file handoff with `Fixes #25`; its
  preceding topic commits use `Refs #25`. Each has an Assisted-by trailer.
  Claude subsequently authorized the river follow-up above as a separate
  `Refs #25` commit, with full gates still deferred until authorized rebase.

Combined D/E proof, staging, combined-share hashes and full gates retain the
pending status above; committing the work does not claim those checks passed.
