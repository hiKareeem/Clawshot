# Round 9, Track B: Sheik and free time travel (cs9b)

Branch `r9/sheik`. Read AGENTS/README, plans00–04, decisions, all round7/8 reports and
`r5-age.md`; Round9's shared-file rules apply. Dump and save backups read-only. No game,
launcher, GUI, Hookshot build, terminal-control command, merge, push or stash. External
research/output: `E:/OOTRemake/work/r9-sheik-cs9b/`. No dependency changes.

## Item 1: placement, Prelude trigger and saved evidence

Executed `uv run python E:/OOTRemake/work/r9-sheik-cs9b/probe.py` against builde0f3ccfa;
complete native flow/placement/GameData/save evidence is in external `probe.log` and flow
reports. Read existing decoded native modules in `work/r4-fast-start/ainb_json/Logic`;
no GPL implementation or NX2navi code/docs read/copied. Python LSP reports no server.

- Temple Sheik is actor **2669233513522124871**, at (139.0265,106.3536,-34), adult Market
  Static. Group **6012439728933042438**, module `Market_Adult_Prefab_7f43`, binds
  `Npc_Hylia_Sheik_Adult_4b5b`. `ActorLogicNpc.Logic_Delete` reads saved Bool
  **Market_Adult_GetLightPrelude**, not a medal, Minuet, Prelude inventory or Forest completion.
  There is no placement Presence gate. Its other module query, `AllSage_IsAfter_Ready_Exp`,
  is not connected to that deletion input. Sheik stays until the Prelude **scene/check** finishes.
- The separate group **17364055337479607892**, `Market_Adult_Prefab_edc2`, ANDs player
  contact with **SageOfForest_IsCompleted_Exp**. The area actor **3406708549665898725**
  is present while `Market_Adult_GetLightPrelude` is false. Request actor
  **3409851866200498477** names `Market_Adult_Field_GetLightPrelude`.
- EventSetting resolves that request to `AllSage:Market_Adult_Field_GetLightPrelude`.
  Event169/170 -> Event73 -> Event39 -> Event37 transitions to `Dm_MelodyGet_Shine`.
  The latter's Event53 gives `Item_Melody_LightPrelude`; Event46 sets
  `Market_Adult_GetLightPrelude=true`. AllSage Event34 then rolls its quest to Step01_01.
- **The scene/travel unlock reads the Forest sage quest, NOT Forest Medallion ownership.**
  GameData BoolExp1371974465 compares `Step_SageOfForest`2841849034 with Complete1275749364.
  The native Forest warp chain Event199 completes the quest separately from the reward grant.
  Speedrunners' medal observation is consistent with vanilla's simultaneous reward/completion,
  not evidence of an item query. Future shuffled medals must not silently inherit an item gate.

Read all twelve supplied `progress.sav` files, not live saves:

| Backup / slots | Era | Forest quest | Forest medal | Prelude scene / completion Bool |
|---|---|---|---|---|
| adult-first /01,04 | adult | Step01 | absent | false /false |
| adult-first /00,02,03,05 | child | Ready | absent | false /false |
| after-forest /01,02 | adult | Step06_2 | absent | false /false |
| after-forest /03 | adult | Step09 | absent | false /false |
| after-forest /04,05 | adult | Complete | owned(1) | false /false |
| after-forest /00 | adult | Complete | owned(1) | true /true |

The last pair isolates the missing scene: medal already owned in04/05, but Sheik's deletion
Bool is still false. Slot00 has both the scene and Bool true. This corroborates Kareem's
reported room-entry transition, not a game run by this agent.

### Item 2 design / provisional implementation choice

Keep the existing ungated pedestal binding. Add a non-negated, non-lazy Presence gate on
**only the placed Temple Sheik** using the SAME Forest-completion BoolExp as his scene.
Before completion he is absent; afterwards he can participate normally, then his existing
Prelude-completion deletion still removes him. Preserve actor Hash/links/transforms, his
module, area/request/flow, song grant and every quest/save value. Native adult Market already
uses that Presence shape with the Fire-completion BoolExp (two distant cloud actors).
This avoids moving a schedule-driven NPC or globally deleting the actor used by cutscenes.
Default remains off; no early Prelude, fake medal, quest completion or saved flag is added.

**Kareem: verify pre-Forest return and second pull, then normal Forest reward/Prelude and
no repeat after Save/Continue on the isolated copies described below.** Runtime actor/scene
compatibility remains unverified until that game check.

### Diagnostics

First probe passed a third argument to two-argument `read_flow`; printed TypeError/signature,
removed it. Next printed timeline-only0050 (`holds no flowchart`); inspect it as a timeline.
The request name is not a flow-map key; printed EventSetting row resolves AllSage.evfc,
then normalized that explicit Work path to its filename stem. Each cause was printed before
its targeted correction; final probe exit0. No game bytes written or unchanged failed retry.

## Item 2: implemented isolated free travel

`age.patch_tree` validates the pedestal AND Sheik actor/group identities before mutation.
It retains the round5 ungated binding and adds only the sourced Forest BoolExp Presence
to Temple Sheik. Stale/missing/duplicate NPC, module/reference or pre-existing Presence
refuses atomically. Every other actor/anchor/group/trigger remains native.

Native/code discrepancy discovered: the unoverridden translated Prelude rule still read
`Forest_Medallion and is_adult`, unlike the observed quest trigger. Stopped using that
premise; posted the evidence and correction. Isolated shared checkpoint **47f25da** adds
`remake/sheik.toml`: adult plus `Defeat Phantom Ganon`, the existing Forest-completion
abstraction used by `age_return_event`. No medal-shuffle policy or fill algorithm changed.
Free travel bypasses neither this check nor the actual scene trigger.

Failing-before `pytest tests/test_age_patch.py`: **7 failed,3 passed**, printing missing
Presence and every stale Sheik contract accepted. After the aimed fix:
- `uv run pytest tests/test_age_patch.py tests/test_age_travel.py -q --tb=short`:
  **24 passed** (including free-return chronology and skipped guarantee).
- `OOT_ROMFS=... uv run pytest tests/test_age_dump.py -m dump -q -s --basetemp
  E:/OOTRemake/work/r9-sheik-cs9b/age-focused-next`: **1 passed**; full native tree
  differs only by the original pedestal changes plus Temple Sheik Presence.
- `uv run pytest tests/test_sheik_logic.py -q --tb=short`: **2 passed**; both setting
  values refuse medal/Minuet/Prelude without clear, accept clear without medal only as adult.

Actual public `python -m clawshot.patch.age --romfs ... --out
E:/OOTRemake/work/r9-sheik-cs9b/ingame/free-time-travel-next --free-time-travel`:
**2 resources**, native adult Banc **30540 ->30664**, allocation **30824 ->30952**,
size table length unchanged. Real-output `smoke_age.py` passes inverse tree, allocation,
twelve save/native-gate scenarios and static launcher isolation checks (`age-proof.json`).
This is data proof, not game compatibility certification.

Approved save-copy template adapted into two unrun launchers under `ingame/`:
**Test - free-time-travel-next.bat** (adult-first manual01), and independent
**Test - prelude-after-forest-next.bat** (after-forest04/05, not already-played00).
Both use bin executable only, update suppression, missing-exe/backup stop, distinct absent
user folders and outward-only backup copies. No save was copied by the agent.

**Kareem: follow `E:/OOTRemake/work/r9-sheik-cs9b/ingame/checklist.md`: absent pre-Forest
Sheik, usable pedestal/child return/second pull/Save-Continue, no early reward; later normal
Forest sage and Prelude once. The independent post-Forest copy shortens the Prelude check.**
Require overlay logs plus gameplay. First adult-arrival scene with pre-Forest NPC absent
is an explicit risk to check, not declared safe by the tree oracle. Default remains off.

One fixture edit initially inserted a statement after `return {`; tool printed syntax
location, re-read and moved only the return before running tests. No failed syntax run.
Four full gates run on the completed item3 tree before any readiness post.

## Item 3: truthful static Hookshot directions

`text.sheik_hint_changes` rewrites both **Talk_01/Talk_03**, never just one random branch.
All16 language archives get the same English seed location; opening style, existing wrap/
page/highlight/reset helpers remain. Every other message/member and NPC talk/Prelude flow
is preserved. `make_seed` registers it independently of stone hints/free travel and composes
after earlier archive transforms, so it cannot erase Gossip Stone or House hints.

It selects the lexicographically first readable location holding an actual Hookshot (not
Longshot); multiple copies still name a real source deterministically. Slices without one
omit the tool entirely in an original neutral line, as the spec permits. No fake Kakariko
fallback, extra setting, item/flow/placement change or hint-distribution change.

- Scoped ruff format/lint: **passed**.
- `uv run pytest tests/test_sheik_text.py tests/test_hints_lines.py -q --tb=short`:
  **8 passed**; both labels, no-source slice, deterministic multi-source, missing-label
  refusal, untouched messages/members and highlight/wrapping behavior.
- `OOT_ROMFS=... uv run pytest tests/test_sheik_text_dump.py -m dump -q --tb=short
  --basetemp E:/OOTRemake/work/r9-sheik-cs9b/text-focused-next`: **1 passed**;
  all16 archives, both native labels, exact inverse message diff, composed stone preserved.
- Public CLI seed7, `--shuffle Chest Gift --logic free_time_travel=true --out
  E:/OOTRemake/work/r9-sheik-cs9b/seed7-gift-free-next`: **exit0,212 shuffled
  checks,24 spheres,124 resources**; full world, unchanged goal/fill bounds, no reroll.
- Independent actual-output `verify_seed.py`: both lines/all16 archives name the real
  **Ganon's Castle Light Trial Triforce Tile Chest** Hookshot; all40 stone lines agree
  with the spoiler; paired pedestal/Sheik transform present; Prelude Event46 completion
  write unchanged in the normally shuffled gift flow; all changed archive/Banc allocations
  fit. Retained external `seed-proof.json`. No game was launched.

**Kareem: in a future seed with free travel OFF, talk to pre-Forest Sheik repeatedly before
finding Hookshot; both tool-direction variants should name the seed's actual Hookshot check,
not send you to vanilla Kakariko. Check wrapping/highlight reset and the language-archive
overlay log. Free travel ON deliberately hides that optional pre-Forest speaker.**

Shared-file changes are isolated: sourced logic/settings checkpoint47f25da, world-format
documentation e05c49a, seed-pipeline hook806b1c7, README a287d1e. Section38 follows the
present36 on this base; reviewer inserts Track A's37 before it and C's39 afterwards. No
placeholder sections or other track's text are invented.

## Commit ledger and acceptance boundary

| Commit | Scope |
|---|---|
| `cbc8e90` | Item1 native Sheik/Prelude/save trace, section38 |
| `47f25da` | Isolated native Prelude logic correction and its boundary test |
| `f42571a` | Item2 pedestal/Sheik placement transform and atomic/inverse oracles |
| `e05c49a` | Isolated world-format documentation |
| `f199780` | Item3 both tool lines, synthetic/all-language inverse tests, section38 |
| `806b1c7` | Isolated automatic seed text composition |
| `a287d1e` | Isolated README feature/acceptance description |

The report-only final evidence commit follows these implementation checkpoints. No rebase,
merge, push, stash, dependency edit, game/window/launcher execution or played-output rewrite.
Removed only the two completed session-created smoke drivers after retaining their JSON proofs;
the read-only research reproducer, fresh requested outputs and unrun launchers/checklist remain.

Additional first-arrival boundary: recorded native0050 timeline's Sheik member uses
EventMemberCreateMethod0, IsWorldfalse and its own event model animation. The numeric creation
mode's engine meaning was not reverse-engineered; this is not proof that a missing field NPC
is recreated. The long-path checklist explicitly tests that first arrival plus later Prelude.
No in-game success or changed default is inferred.

### Cross-track pack integration

Posted on cs-r9: Track C's existing r8 seed8 byte-identical pack proof is historical once
806b1c7 is merged: every new seed's16 Mals archives gain the two Sheik lines. Recompute the
integrated pack reference digest from integrated source; never rebuild the played r8-full
output. Track C's floor-qualified catalogue labels automatically appear in this static hint
after merge. Both README additions are isolated for additive integration. No other worktree
or existing pack/output is changed here.

## First complete gates: stale archive oracle diagnosed

The full unfiltered chain completed on a287d1e plus report-only edits:

| Full command | Observed result |
|---|---|
| `uv run ruff format --check` | 227 files already formatted |
| `uv run ruff check` | All checks passed |
| `uv run pytest` | 733 passed,87 skipped;428.54s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | 84 passed,2 failed,734 deselected;1071.49s |

Both failures are `test_hints_seed_dump.py::test_dump_the_stones_say_the_spoiler_hints`
for always/mask. Printed payload: CNzh stone01 still vanilla instead of the expected
English spoiler text. Its local dict comprehension flattened all PatchSteps, selecting
only the last Sheik transform for each archive and discarding the earlier stone transform.
That is not the common writer's behavior: it composes every step, independently proved
by the successful full CLI/all16 readback above.

Changed the oracle to run actual `write_seed` and read the on-disk compressed archives.
Retained every stone/spoiler equality and mode/flow assertion; additionally require both
Sheik lines in every written archive to identify an actual shuffled Hookshot source.
No production transform, composition, goal, fill bound or hint policy changed.
Also removed the incidental exact A-chest preference assertion from the multiple-source
test; it now requires deterministic bytes AND a true source, not a particular correct source.
Cause-aimed native check and fresh full gates follow; no unchanged failed command rerun.
