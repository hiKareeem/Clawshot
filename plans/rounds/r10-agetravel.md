# Round 10, Track B: age travel (cs10b)

Branch `r10/agetravel`. Required instructions/plans and round8/9 reports read; shared edits are isolated and posted. Dump and backup saves read-only. No game, batch, window, terminal-control command, merge, push, stash or dependency change. External research/output: `E:/OOTRemake/work/r10-agetravel-cs10b/`. Tasklist found Kareem's game running; all commands use one worker. Full gates take the shared `work/rounds/r10/gate.lock` and release it on exit.

## Item 1: first adult arrival

Accepted R9-FIRST-PULL as ground truth, not rerun. Read-only `probe.py`, `expressions.py`, `scene_state.py` inspected the native placements, active flows/timeline, GameData and the broken-scene user plus original adult-first backup.

The first arrival is TWO events: `AllSage/Event9` runs timeline `Dm_TimeTemple_0050`, then `Event0` runs dialogue flow `Dm_TimeTemple_0055`. Both bind placed Temple Sheik. Using only 0050's completion risks removing him between the timeline and dialogue. The new non-saved BoolExp `Clawshot.TempleSheik.Presence` means **not HavePlayedEvent.Dm_TimeTemple_0055 OR SageOfForest_IsCompleted_Exp**. This includes the entire requested unplayed-0050 boundary and retains the subsequent dialogue too. Native Prelude-completion deletion remains unchanged. No duplicated actor, invented reward, quest completion or saved-default edit.

Native BoolExp postfix operands/operators: Bool=0, BoolExp=10, NOT=5, AND=3, OR=4. Precedents: `DoorOfTime_IsAfterStep03_AND_SageOfForest_NotCompleted_Exp` uses expression/NOT/AND; Mido's surprised predicate uses Bool/NOT/AND/OR. Added row is reset0/save-1; original metadata and every native row remain exact, so there is no added saved slot.

### What skipped dialogue changes

`Dm_TimeTemple_0050` is presentation, with no GameData/pouch/challenge action. `Dm_TimeTemple_0055/Ready` Event252 sets `HrlField_HasEnteredFirstTime_Adult=true`; Event137 increments Zelda Notes NPC-talk count. No item/song grant. AllSage continues with `Market_Child_Firsttime_GotoAdult=true`, `HavePlayedEvent.NaviHint_Shield_Hylian=true`, SageOfLight Complete, AllSage Step01, SageOfForest Step01. The broken user's adult slots03–05 have both scene-history Bools true, HrlField true, AllSage/Forest Step01; this shows these saved story writes survived the missing speaker, not that the dialogue or Notes counter was correct. No save repair is applied.

### Exercised evidence / player check

- Focused `ruff check`: passed after printed I001 identified misplaced imports; only that import block corrected.
- `CLAWSHOT_WORKERS=1 uv run pytest tests/test_age_patch.py -q`: **15 passed**.
- `CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest tests/test_age_dump.py -m dump -q -s --basetemp E:/OOTRemake/work/r10-agetravel-cs10b/age-focused-next`: **1 passed**; exact inverse Banc/GameData oracle, byte order and allocation checks.
- Actual public `python -m clawshot.patch.age --romfs ... --out .../ingame/first-pull-fixed-next --free-time-travel`: **3 resources**. Banc30540→30664, allocation30824→30952; GameData1462888→1462980, allocation1463176→1463272; size-table length unchanged.

**Kareem: after quitting the played game, run `E:/OOTRemake/work/r10-agetravel-cs10b/ingame/Test - first-pull-fixed-next.bat`. Load CHILD AUTOSAVE slot02 from the adult-first backup (not adult manual01); it has the open door/Step06 and neither first-scene history. Pull: Rauru/Light Medallion native; Sheik visible in BOTH the introductory timeline and all following dialogue, Navi/cameras normal. After the scene, leave/re-enter Temple: Sheik absent, return pedestal usable before Forest; repeat child/adult travel and Save/Continue. Later Forest clear must still show native reward and Prelude once. Require adult Banc, GameData and resource-table `from the overlay` log lines plus actual gameplay.**

Launcher is a copy/adaptation of the approved talon-boomerang pattern: bin executable only, update suppression, missing-exe/backup stop, distinct new user, outward backup copy only. No launcher or save-copy operation executed by the agent. Gameplay acceptance remains pending; free travel stays default-off.

## Coordination

Posted scope on cs-r10. The 0055 completion boundary is a provisional technical choice preserving the complete first-arrival chain; it does not broaden Prelude access. Item2 follows after the item1 checkpoint. Full four-command gates remain required before any readiness claim.

## Item 2: Door of Time modes

Implemented `Settings.door_of_time` and `--door-of-time closed|song_only|open`, with closed
default (D35). Existing CS1 canonical codec records it; explicit CLI mode clears stale derived
door logic from an effective replay. Contradictory explicit logic is refused. Free travel is
separate and remains off by default.

Native trace found TWO song-opening gates: altar ReplaceEventParam's invalid expression
`Market_Child_TimeTempleDoor_OcarinaReacts` = not DoorOfTime Step05 OR opened, then
DoorOfTime/Event60's after-Step04 expression. Song-only changes the former to opened only
and bypasses the latter, additionally requiring learned `IsGet.Item_Melody_TimeSong`.
Native sequence melody4, recommended-melody result, opened/history guards, opening scene,
proxy event signal, opened Bool and Step06 write remain. No stone quest/reward/default is forged.

Open uses a seven-byte, zero-padded **data string** substitution in the exact native common
door AINB: Step06→Ready. Its original is-after/is-equal outputs open/skip-animation for the
door. No pointer, instruction, file length or allocation changes. SHA256 validates the exact
native input; no generic AINB writer/size formula/dependency added. External unmodified AINB
decoder reports exactly one tree delta: node8 Parameters/Inputs/String1 DefaultValue.
The same common signal shows the altar's visual stones too; these are not owned stones.
Child pedestal uses the existing ungated attention module and primary Draw request, whose
own history branch still selects first-pull versus repeat travel. All actors/links/transforms
and the native first-adult/Rauru/era/Forest/Prelude flows stay native.

### Correct logic, including the newly exposed instrument boundary

The door override matches each physical mode. Early modes use data-defined return-kit
inventories and staged families: song-only guarantees only Ocarina1/Time song at the pull;
open guarantees no inventory. Optional child Saria, strength and Time ocarina are not assumed.
Adult instruments/Saria can be staged from shuffled adult checks; unshuffled child-only
prerequisites can make the strict D20 first-pull guarantee impossible. No automatic free
travel, relaxed goal or increased retry bound is introduced.

Existing translated `can_play` wrongly admitted Fairy Ocarina as adult. Section37's item-bar
age catalogue says Fairy child-only, Time both-age; early Fairy-only pulls expose this at
adult Mido. Sourced helper overrides therefore require Ocarina2 for adult song use in EVERY
door mode, including closed, as Claude explicitly directed. **This source is native
PouchTable metadata, NOT an in-game Fairy-as-adult observation.** The three canonical song
helpers all share the age restriction; no item permission or inventory grant is patched.

### Exercised checks

- `CLAWSHOT_WORKERS=1 uv run pytest tests/test_door.py -q --tb=short`: **18 passed**.
  Covers mode/item/age boundaries, learned song, wrong melody, durable once/history guards,
  unrelated-flow preservation, stale contract refusal, CS1 replay and CLI override/conflict.
- `CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest tests/test_door_dump.py
  -m dump -q -s --basetemp .../door-focused-next`: **2 passed**.
  Actual native serialized flow behavior; exact inverse flow/Banc/module/GameData diffs;
  age-presence plus altar-expression composition and final allocations.
- Actual standalone CLI song_only: **3 resources**, flow90104→90360/allocation90384→90640,
  GameData1462888→1462868 (allocation1463176 retained), common size table.
- Actual standalone CLI open: **2 resources**, child Banc259184 unchanged length,
  allocation259464 retained; native module7651 unchanged length/allocation8056 retained.
- Scoped format/lint pass. One printed test-import I001 was corrected by moving the sibling
  helper import into the prescribed import group. External pack probe encountered a native
  `AI` member where it expected BYML; printed magic identifies that unsupported selection,
  then the separate ocarina-only probe completed without retrying that failed stage.

### Isolated shared checkpoints

- `2b889c2`: Settings/defaults only; no fill algorithm edit.
- `876956f`: CLI only.
- `890074c`: owned door/instrument logic, world return-mode data and `prepare` derivation.
- `b0e28f5`: common seed pipeline only.

All posted as checkpoints, not ready before the complete gates. README/world-format changes
are separate. Section41 appends after39 on this base; reviewer inserts40 before41.

### Coordination / additional reviewer request

Posted the settled NUP inputs as a short separate cs-r10 note: adult/child Market Static,
DoorOfTime flow, raw `Logic/Market_Common_f252.logic.module.ainb`, GameDataList, size table
and ZsDic pack. The reused SpiritTemple module is referenced only, not read/copied.

Claude requested two read-only released-seed checks with the corrected all-mode instrument
rule: seed8's retained spoiler, seed10 regenerated in memory from main using that same CS1.
`check_released.py` explicitly imports main's source, disables bytecode writes, captures the
actual generator spec, keeps all native fixed placements, then changes only the three song
helpers for independent search/return-proof replay. No seed folder is written. Results and
their separate thread post follow after the serialized run.
