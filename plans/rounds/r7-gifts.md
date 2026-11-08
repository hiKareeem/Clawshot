# Round 7, Track D: gift follow-ups (cs7d)

Branch `r7/gifts`. Required AGENTS/README/plans 00–04/decisions and all round-5/6 reports read,
including the Round 7 opening/shared-file rules. Dump and save backups are read-only; no game,
launcher, GUI, Hookshot build or terminal-control command is run. Scratch/generated data stays under
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
the original repeat event and equipment condition. Normalize the gate even if the shuffled gift lands on
its vanilla shield. Existing flavour dialogue remains; no claim of new dialogue or gameplay acceptance.

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

**Kareem: new game, get that chest shield and the normal Kokiri Sword; pass Mido and talk to the tree;
before Gohma/castle completion return to the shop with the shield equipped. Expect Boomerang model/text,
then no second reward after unequipping/re-entry and Save/Continue. Require overlay log lines for the
merchant flow, child Kokiri Dynamic and size table.** Flavour dialogue still refers to the shield.

### Full-seed diagnostic, not a passed smoke

Whole-world Chest+Shop+Gift seed 7 refused within the existing ten-attempt bound after adding the check:
last failure `Small Key (Fire Temple)`, 6 allowed of 225 left. No unchanged retry or seed/settings reroll.
A one-attempt diagnostic printed all candidate/key/placement values: only two Fire keys were collectable;
native ammo prefill occupied Big Lava Room Blocked Door with Bombs and Highest Goron with Bombchus.
The remaining Fire slots all needed later keys. This exposes the existing D25 prefill/key-capacity
interaction under the changed pool/RNG, not the shield gate (seven assumed shields; Mido/time travel
and Forest gear held). Diagnostic artifact: external `diagnose_fill.py`; error log `gift-cli-0.log`.
No retry-count, dungeon rule, ammo policy or fill code is changed by this track. The generator correctly
refuses output; the controlled player overlay and focused merchant behavior are independently verified.
**Claude: review the D25 prefill preserving early dungeon-key capacity before treating this full
Chest+Shop+Gift seed 7 as generatable.** This is an explicit residual integration finding, not a passed seed.

### Coordination delivery failure

Two prescribed `bermuda.exe thread post --thread cs-r7 --as cs7d ...` notices returned
`no thread cs-r7`; `thread log` returned empty. Read-only store inspection shows cs-r1 through cs-r6,
no cs-r7. No thread was created (forbidden by this track's command allowlist). Shared notices and the
fill request are preserved here; handoff will attempt the prescribed post once more after the work.

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

## Completed gate evidence

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | 182 files already formatted |
| `uv run ruff check` | All checks passed |
| `uv run pytest --basetemp E:/OOTRemake/work/r7-gifts/gate-synthetic` | 517 passed, 70 skipped; 757.53 s |

The full `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` gate is running, with its
basetemp `E:/OOTRemake/work/r7-gifts/gate-dump`. No code edits after the full gates started.
Final results and handoff follow after it completes; nothing is posted as ready yet.
