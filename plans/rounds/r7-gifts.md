# Round 7, Track D: gift follow-ups (cs7d)

Branch `r7/gifts`. Required AGENTS/README/plans 00–04/decisions and all round-5/6 reports read,
including the Round 7 opening/shared-file rules. Dump and save backups are read-only; no game,
launcher, GUI, Hookshot build or terminal-control command is run by this agent. Scratch/generated data stays under
`E:/OOTRemake/work/r7-gifts/`. No dependency, merge, push or stash change.

## Item 1: shopkeeper gift

Read-only round-6 trace reproduced: Event45 checks equipped Deku Shield; Event63's saved first-talk
Bool selects Event117 or Event116, and both give `Obj_Shield_Deku`. Event44 sets the first-talk Bool
only after the first branch. Existing Bool `HaveTalked_Npc_Kokiri_001_Shop_Child_PresentDekuShield`
(Hash 3217462169) defaults false, reset 8, save file 0. D22 therefore needs no new Bool/save layout.

Implementation decision: on Gift shuffle only, reuse that Bool as the eligibility gate in place of the
equipment test, set it after both grants, and represent the two stable flow/event IDs as one remake-only
check, `KF Shopkeeper Gift`. Move the existing data-sourced free-shield event rule to that location in a
copied gift spec; do not leave an implicit free shield in a shuffled world. Unshuffled specs/flows keep
the original repeat event and equipment condition. Low-level same-actor probes still normalize the
once-gate; ordinary generated seeds now follow Kareem's non-progression policy below. Dialogue is unchanged.

**Kareem's decision via Claude, 2026-11-08: option1.** Keep the native quest cutoffs unchanged.
When shuffled, `KF Shopkeeper Gift` may contain only non-progression items, enforced by a missable
location type through `allowed()`. No seed may rely on a progression reward surviving this missable
window. Extending its Talk-dispatch/story window is a later change, not part of this round.

Isolated shared-file commits: `b0cbb2f` (`gift_rules.toml`), `5e2f128` (player-name row and its coverage
oracle), `079b8f9` (`item_actors.toml` backwards alias). First smoke printed the check absent: the native
`Obj_Shield_Deku` did not match canonical `TBox_Shield_Deku`. Printed both PouchActorInfo rows: same
equipment/category fields, both ages `Weapon_Shield_Deku`. Resolved this existing actor alias in gift
pool matching; no unrelated gift family is loosened. No Python language server is available (LSP
references returned none); known-symbol consumers were searched.

Verification: 31 focused synthetic tests passed; four focused dump tests passed (new merchant interpreter
and exact inverse delta; every changed gift flow; every grant; unchanged six-fairy GameData additions).
Ruff's unused inverse-oracle loop variable was printed and replaced with an indexed enumeration.
The final full gates below also exercise the actor-alias eligibility assertion added after the smoke.

Controlled output: `E:/OOTRemake/work/r7-gifts/ingame/shopkeeper-boomerang/`, launcher
`ingame/Test - shopkeeper-boomerang.bat`, checklist `ingame/shopkeeper-check.md`. Built via the actual
common writer; four resources parsed and sized. Both Kokiri Dynamic copies put a Deku Shield in Mido's
far-right chest; the merchant gives Boomerang. Flow 50552 -> 51200, allocation 50832 -> 51472;
Child Banc 510884 -> 510924, allocation 511176 -> 511208; Adult 516036 -> 516076,
allocation 516328 -> 516360. No GameDataList. Copied/statically checked approved new-game launcher;
no batch, dry run, window or game executed.

**In game, Kareem confirmed via Claude (2026-11-08): Boomerang is granted with the shield equipped,
and later talks give nothing.** This is the supplied game result, not a rerun by the agent. The original
isolated new-game launcher and `ingame/shopkeeper-check.md` remain available. The message did not
separately report Save/Continue or quote overlay-log lines; no additional observations are invented.

### Original full-seed diagnostic (before reviewer-authorized item4)

Before item4, whole-world Chest+Shop+Gift seed 7 refused within the existing ten-attempt bound:
last failure `Small Key (Fire Temple)`, 6 allowed of 225 left. No unchanged retry or seed/settings reroll.
A one-attempt diagnostic printed all candidate/key/placement values: only two Fire keys were collectable;
native ammo prefill occupied Big Lava Room Blocked Door with Bombs and Highest Goron with Bombchus.
The remaining Fire slots all needed later keys. This exposes the existing D25 prefill/key-capacity
interaction under the changed pool/RNG, not the shield gate (seven assumed shields; Mido/time travel
and Forest gear held). Diagnostic artifact: external `diagnose_fill.py`; error log `gift-cli-0.log`.
At that point no retry-count, dungeon rule, ammo policy or fill code was changed. The generator correctly
refused output; controlled player overlays were independently verified. Claude subsequently authorized
item4 below to correct the generator ordering. This original failure is retained as the failing-before
evidence, not described as the outcome of the updated generator.

### Successful required early-game surface

Independently ran the public CLI for the Kokiri/Lost Woods/Deku Tree slice (same seed7,
`--shuffle Chest Gift --areas KokiriForest LostWood InsideTheDekuTree --goal "'Defeat Queen Gohma'"`):
**17 shuffled checks, three spheres, 16 resources**, plus spoiler/note. The real written shopkeeper
gives Fairy Ocarina on both grant branches and reads the existing saved once-Bool; no GameDataList.
Read the actual spoiler and rendered note: both physical flow IDs and the early-story visit directions
are present. Reconstructed child-only Search wins and has no implicit free-shield event.
A second CLI process replays its expanded CS1 with another hash seed: **18/18 files byte-identical**.
Evidence: external `slice-proof.json`. This verifies the requested early check end to end; it does not
substitute for or relabel the explicitly refused whole-world Fire-key fill above.

### Initial coordination delivery failure, resolved

The two initial notices and first final handoff returned `no thread cs-r7`. No thread was created by
this track (forbidden by the command allowlist). After Claude supplied the missing thread, all three
original messages were reposted unchanged, in order, with `thread post --thread cs-r7 --as cs7d`;
all three succeeded. Subsequent item4 shared-file notices also posted successfully.

## Item 2: Treasure Chest Game

Built `E:/OOTRemake/work/r7-gifts/ingame/treasure-red/` through the common writer. Copied the
approved `Test - talon-boomerang.bat` into `ingame/Test - treasure-red.bat`, replacing only this
experiment's paths/name. Own `user-treasure-red`, copies
`E:/OOTRemake/work/save-backups/2026-11-07_llr-tower-before-pickup` only on first launch.
Read-only slot01 evidence: child, Sun's Song, prize Hash unset, `MiniGame_ChoiceTreasure_IsClear=false`.
The same child/ranch checkpoint was used by the round-6 Castle Town tests. No Lens availability is
assumed; the unmodified five-room game may require retries or a later Lens acquisition.

Only first-clear reward Hash `16881481538337649070` changes: `Obj_Heart_Piece` ->
`TBox_Rupee_Red`; preview `Obj_Heart_Piece_MiniGame` -> `Obj_OrnamentalRupee_Red_MiniGame`,
the native repeat prize's existing preview. All ten room boxes and repeat red-rupee prize Hash
`6781536951709667179` remain vanilla (the eleven non-first-prize boxes of D17).
Market Child Static: 259184 -> 259100 bytes, allocation 259464 retained; one resource, no size table.
Exact inverse two-field diff recovers the entire original placement; dump and backup SHA256 maps
are unchanged. Compression/readback and static launcher checks passed; no launcher executed.

First probe wrongly assumed the EventSetting prefix was the physical flow filename: missing
`MiniGame_ChoiceTreasure.bfevfl.zs` printed. Resolved the actual row's `FlowchartFileName` and entry,
then corrected that one script: `MiniGame_SequentialChoiceTreasure`.
OpenClear Event66 forwards `ContentName`; OpenTreasureBoxClear Event191 calls
`Dm_SY_Treasurebox:SuccessForMiniGame` with it. ClearFlagOn Event146 sets
`MiniGame_ChoiceTreasure_IsClear` (Hash3046747885, saved Bool false/reset8/file0).
Both prize actors also have permanent type24 Bool64bitKey entries. Their logic/flow/flags are untouched.

**Kareem: run `ingame/Test - treasure-red.bat`, Continue manual slot01, leave the ranch for Castle
Town, make night with Sun's Song, pay10 and win the native five key rooms. First prize must preview
and grant a Red Rupee (+20 below wallet cap), with rupee text and no heart-piece progress. Save,
quit/Continue and verify first-clear completion persists. Require Market Child Static's overlay log.**
Checklist: `ingame/treasure-check.md`. The repeat prize is already a red rupee, so distinguish first-win
from repeat behavior. D17 stays disabled pending that observation; no shuffle/logic code changed.

## Item 3: boss rewards

Completed research in section28, “Nine boss rewards”: all three stones, five adult temple medals and
Rauru's Light Medallion. The last is a first-sword-pull check, not a ninth blue warp. The section gives
each grant flow/entry/event, blue-warp request, cutscene and separate quest-completion write.
Five `.110` grant files selected via the active version map; all nine use the shared GetPouchContent
wrapper. All nine history Bools and all nine quest Enums exist as saved reset8/file0 entries.

Actual read-only reproducers ran successfully under `E:/OOTRemake/work/r7-gifts/`:
`boss_rewards.py` (640 active flowcharts, 261 timelines, nine asserted native grants, eight warp
placements, zero literal reward-item query readers), `warp_trace.py` (each warp's exact escape
request), `warp_graphs.py` (eight referenced native graphs and their real Create_WarpPrefab sources),
`story_gate_trace.py` (request mapping, quest writes, saved types), `gate_readers.py` (later scene
history reads and the saved sage counter). Full decoded inventories remain external:
`boss-rewards-audit.json`, `warp-graphs-audit.json`.

The initial warp-name filter returned no rows because the actor is `Obj_WarpPoint_A_01`, not a
Boss-named actor; printed the unique actual actor names and corrected the filter. The first graph
filter likewise returned empty roots: printed bindings showed `Create_WarpPrefab` is an input name
on a boss module, not a node name/property. Following those actual input edges produced all eight
creation predicates. No native data or decoder source was changed or copied.

Confirmed Temple mismatch: DoorOfTime Event38/39/56 checks Fire/Water quest completion; opening
still depends on DoorOfTime Step04/Step06, melody4, scene/opened history. Adult return/Prelude
depends on Forest quest completion. The Light Arrows flow reads Spirit/Shadow **awakening-scene**
history, not medals. Existing `AllSage_AwakeSageCount` defaults5 and decrements on sage routes;
no literal query reader was found, so no new count gate is inferred. There are no reward-item
symbols in the 1822 previously decoded Logic graphs; engine-implicit readers are not claimed absent.

No boss reward, world rule, flag or gate patch. The nine class-more entries stay excluded.
Future work must separate physical check completion from reward ownership, preserve warp/story/
environmental changes and D20, update whichever reward gates owners choose, then test grant/display/
save/revisit behavior and chronological beatability. Grant-only swaps would disagree with the oracle.

**Kareem/co-owner: which Temple/reward gates should follow stones/medallions actually found,
rather than completed dungeons/awakening scenes?** Proposed separation is recorded in section28,
not applied as an unapproved product decision.

## Initial items1–3 gates (before rebase/item4)

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | 182 files already formatted |
| `uv run ruff check` | All checks passed |
| `uv run pytest --basetemp E:/OOTRemake/work/r7-gifts/gate-synthetic` | 517 passed, 70 skipped; 757.53 s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump --basetemp E:/OOTRemake/work/r7-gifts/gate-dump` | 69 passed, 518 deselected; 1194.27 s |

These four full commands passed before the reviewer follow-up. They covered formats/census,
the merchant oracle, Gift integration and chronological/seed oracles; they are historical evidence,
not substitutes for the fresh post-fix gates below. Runtime game acceptance remains Kareem's.

Completed temporary artifacts removed only after their proof: the initial no-check smoke folder,
both successful child-slice/replay folders, both completed full-gate basetemps and the failed whole-world
smoke driver. Requested two controlled overlays, their copied release-only launchers/checklists,
reproducible read-only research, `slice-proof.json` and `gift-cli-0.log` remain outside the repository.
No active test, game/save/user/backup path, other worktree or pre-existing file was removed.

Independent saved-artifact audit (not the builders' in-memory trees) also passed: all **five** emitted
resources parsed; exact inverse allowed-field deltas restore the original Banc/flow trees; only the
shield output's three planned size entries change. Both actual batch texts use only the bin executable,
suppress update checks, stop if missing and name distinct isolated users. At this initial pre-play audit,
neither user folder existed. Retained external evidence: `ingame/artifact-proof.json`.

## Branch handoff ledger (rebased onto approved main `dfe923a`)

| Commit | Scope |
|---|---|
| `5802aba` | Isolated shared gift-rule data/schema contract |
| `ebbbfed` | Isolated shared player-name row and copy-identity coverage |
| `d187892` | Isolated shared native gift/chest shield actor equivalence |
| `54bf25f` | Item1: both-branch saved once-gate, copied-spec event-to-check cutover and tests |
| `1bfe7d6` | Item2: first-prize contents/preview experiment and save-copy checklist |
| `e1d3615` | Item3: all-nine reward/blue-warp/quest-gate research, no patch |
| `f7a39e7` | Initial gates, CLI/replay and artifact audit; earlier posted hashes are historical |
| `313a01e` | Item4: own-dungeon items before D25 ammo, early-key regression |
| `266f219` | Item4: captured type-held dependency cycle and second regression |
| `708cedb` | Item4: explicit type-held stage before ammo; replaces the intermediate sort workaround |
| `9a1ac61` | Item4: sparse type-held capacities before general refills |
| `c543679` | Shared synthetic purchase fixture: first Blue Fire sets its owned-content state |

Final documentation evidence and its own head are reported after the post-fix gates, rather than
self-referenced here. The approved rebase was conflict-free; the clean final rebase was up to date.
No merge, push, stash, dependency change, other-worktree edit or unauthorized rebase.

### Left for review and play

- **Kareem:** Treasure Chest Game's isolated-save checklist remains pending; D17 stays disabled.
  The shopkeeper's equipped-shield grant and repeat-talk result are confirmed above.
- **Kareem/co-owner:** future boss-reward gate semantics (question in item3/section28); no boss rewards enabled.
- **Claude:** integrate the isolated shared-file commits and section28 after sections25–27. Item4's
  latest generator/matrix/gate evidence below supersedes the original D25 refusal.
- **Kareem:** option1 is the approved policy: missable shuffled gifts reject progression. The native
  window remains unchanged; extending it is later work, not an unanswered decision in this branch.
- **Coordination:** the missing-thread blocker is resolved. Final post-fix head is posted only after
  the four required commands, not inferred from the earlier handoff.

## Item4: reviewer-authorized generator ordering

Claude authorized the generator fix and its restriction order in this conversation (2026-11-08).
The implementation preserves D20 return-kit staging and uses these explicit ordinary fill stages:
own-dungeon items (keys/maps/compasses), all type-held items (including songs and normal/progression
shop refills), D25 bag-gated ammo, remaining progression, then filler. Each constrained/progression
stage assumes every not-yet-placed item. No retries, rules, location eligibility, seed or settings are
relaxed. No product decision was made about the native gift window.

Two synthetic failing-before/passing-after cases in `tests/test_gifts_fill.py`:

- A bag-gated dungeon has one entrance-key slot and two key-locked ammo slots. Printed RNG/state
  values showed ammo in the entrance slot; seed0, one attempt, failed with no reachable Small Key.
  Both ammo families now wait behind the real entrance key and an independently obtained bag.
- A type-held song/bag dependency: flexible progression consumes the song's viable frontier.
  The three-check seed2, one-attempt case failed with no reachable `Storms`; taking the type-held
  song first leaves the bag before the song and its unlocked chest, without widening allowed types.

Dungeon-before-ammo alone exposed another ordering issue: the unchanged ten-attempt whole-world
Gift run had five Fire-key failures and five type-held-song failures. Captured exception-frame values
showed Storms stranded at adult Windmill/Sheik Temple while the independent bag was in the Well.
The intermediate type-priority safeguard generated 278 checks in 22 spheres. Per Claude's subsequent
direction, the final code replaces that workaround with the explicit type-held stage before ammo.
All 23 focused generator, age-return and regression tests pass after that cutover.

**Claude: final unrestricted junk retains OoTR-style fast fill. A valid child slice intentionally has
unreachable adult-roof junk (`test_a_slice_keeps_only_its_areas_and_its_goal`); applying reachability
to all filler would be a separate all-checks-reachable policy change.** This distinction was posted;
all constrained/progression stages do use the requested assumed search.

### Type-held capacity follow-up

The first full synthetic gate on `708cedb` exposed a genuine constrained-Shop regression:
**one failed, 520 passed, 70 skipped**. Normal Fish refills could consume Blue Fire's eligible frontier.
Printed native whitelist values: Blue Fire has two of the fixture's three slots; Fish has all three.
`9a1ac61` stably orders the type-held pool by allowed destination count, most constrained first.

The original synthetic purchase fixture also never supplied its separate owned `Blue Fire` state,
leaving Potion slot5 permanently unreachable even after the first purchase. `c543679` models that
ownership transition so all type-held normal refills may use the intended assumed search. The exact
first-Blue-Fire-at-`KF Shop Item 7` assertion is retained across all 20 seeds; no native shop whitelist,
sale gate or bottle rule is changed. All **53** focused shop/generator/return-kit/regression tests pass.

### Pre-missable-policy whole-world CLI matrix after `9a1ac61`/`c543679`

All four modes used seed7, no slice/alternate goal and the unchanged ten-attempt bound. The real
public CLI entrypoint built and wrote each output; a pass-through wrapper counted actual `fill`
calls without altering arguments, RNG, results or error handling. Independent Search replayed the
returned full placements, matched the written spoiler's progression spheres and reached the goal.

| Mode | Actual attempts / existing bound | Shuffled checks | Collection spheres | Output files |
|---|---|---|---|---|
| Chest | 1 / 10 | 164 | 24 | 64 |
| Chest+Shop | 3 / 10 | 228 | 24 | 82 |
| Chest+Shop+Gift | 1 / 10 | 278 | 19 | 123 |
| `--settings CS1` default | 1 / 10 | 164 | 24 | 64 |

The Shop run's first two failures were ordinary Fire-key capacity refusals, captured in the proof;
the generator did not reroll settings or extend its bound. Each mode retained **63** correctly
own-dungeon items and **six** ammo pickups inaccessible under maximal independent-bag-free inventory.
Both shuffled-Shop modes retained **59** Buy refills in Shop. The explicit Chest/default-CS1 outputs
were **64/64 files byte-identical**. Every collection sphere's shuffled checks/items was printed.

Retained external final evidence under `E:/OOTRemake/work/r7-gifts/`: `item4-final-matrix-proof.json`,
`item4-final-matrix-spheres.log`, `item4-final-matrix-hashes.json`, and four `item4-final-*-cli.log` files.
Captured failing-before values remain in `item4-failure-states.json`. The raw four smoke outputs,
obsolete interim output and throwaway counter/diagnostic/unused verifier scripts were removed only
after the successful proof; the two requested controlled player overlays/launchers/checklists remain.
No game or launcher was started; no main save, backup or dump file was modified.

### Completed pre-missable-policy gates

The earlier synthetic failure above is not counted as a passed gate. Its in-flight old-source dump
run was cancelled, not reported as success. The refreshed full commands use `9a1ac61`/`c543679`
on approved main `dfe923a`; no source/test edits followed their start.

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | 183 files already formatted |
| `uv run ruff check` | All checks passed |
| `uv run pytest --basetemp E:/OOTRemake/work/r7-gifts/gate-dfe923a-synthetic-vvmt3e1o` | 521 passed, 70 skipped; 329.50 s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump --basetemp E:/OOTRemake/work/r7-gifts/gate-dfe923a-dump-ojz3x37k` | 69 passed, 522 deselected; 881.35 s |

All four completed on `9a1ac61`/`c543679` before Kareem supplied the game result and missable policy.
The attempted stop found the dump job already completed successfully; that run was not cancelled.
Fresh policy-source gates below supersede these pre-policy counts. The completed synthetic basetemp
was removed only after its passing run; no active test directory was removed.

## Approved missable-check policy follow-up

Kareem's equipped-shield Boomerang/repeat-talk confirmation and option1 are recorded above.
Shared commit `8001e9a` rejects any `world.items[item].progression` at a `Missable` location in
`allowed()`. Owned `bcad046` assigns that type only to the shuffled merchant check, expands/replays
it through Gift settings, and leaves the unshuffled native free-shield event and story window intact.
No flow grant/gate bytes change in this policy follow-up.

The new synthetic generated-world regression failed before at seed1:
`Independent Chest = Rupee`, `KF Shopkeeper Gift = Deku Shield` (progression). After the guard,
all 20 one-attempt seeds place only non-progression at the merchant while still obtaining the required
shield elsewhere. The former literal held-type tuple test was replaced with real `allowed()` behavior
on Chest/Gift/Song/Missable destinations; no obsolete tuple snapshot is re-pinned. All **78** focused
gift/shop/generator/return-kit tests pass before the newly authorized main rebase.

Claude then advanced main to `9b4735c` (merged B/C, D27/D28). This clean checkpoint precedes that
rebase; section28 is retained after27, with section25's integration remaining before26. Fresh policy
CLI matrix (including expanded Gift CS1 replay and goal-without-missable proof), four gates and
rewritten head follow on the approved new base; pre-policy results above are not reused.
