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
