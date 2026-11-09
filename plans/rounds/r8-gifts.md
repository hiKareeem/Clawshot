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

**Missing prerequisite:** a demonstrated per-placed-cow grant dispatcher (or a code hook), plus
approval to supersede D11. Adding eight Bools alone would still grant through the same shared
flow and cannot distinguish the two simultaneously loaded ranch cows. No global replacement
is mislabeled as fourteen checks, no unsafe test overlay is written, and no cow is enabled.
The inherited Epona/song/access rules remain unchanged. This item is a research checkpoint,
not an implementation-ready claim. The blocker was posted to `cs-r8`; remaining families proceed.

## Decisions / questions

- **Kareem/Claude: Round 8 requests cow checks but D11 says cows stay out (no per-cow flag).
  May a proven RomFS-only per-cow D22 gate supersede D11?** Research and a controlled experiment
  may proceed; no production cow enable is assumed.

## Coordination

Initial prescribed `~/go/bin/bermuda` invocation failed (127): executable resolution omitted `.exe`
on this Windows shell. Printed HOME/USERPROFILE and `command -v bermuda`: actual executable is
`C:/Users/hi/go/bin/bermuda.exe`. The corrected explicit executable is used for subsequent posts.

## Verification

Pending implementation and the four complete gates. No readiness claim.
