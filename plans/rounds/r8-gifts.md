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


## Decisions / questions

- Cow policy resolved by the reviewer above: D11 stands; no cow patch in Round 8.

## Coordination

Initial prescribed `~/go/bin/bermuda` invocation failed (127): executable resolution omitted `.exe`
on this Windows shell. Printed HOME/USERPROFILE and `command -v bermuda`: actual executable is
`C:/Users/hi/go/bin/bermuda.exe`. The corrected explicit executable is used for subsequent posts.

## Verification

Pending implementation and the four complete gates. No readiness claim.
