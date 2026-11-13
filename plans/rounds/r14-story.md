# Round 14: story fixes (cs14c)

Branch `r14/story`, base `ffea543` (published Clawshot 0.2.0). No version bump; Claude owns versions and review/merge. Issues #21 and #22. Merge order B, C, D, A.

## Scope and evidence status

- Trace Zelda's escape, drawbridge, moat rewards and closed Door of Time from supported build `e0f3ccfa`; correct logic rather than pre-completing unproven story state.
- Trace Hyrule Field BGM and preserve the state omitted by the Kaepora skip.
- Regression coverage, all offered fast-start subsets × forest/door modes × Chest-only/Recommended × seeds 1/7/42 through the public generation path.
- One combined isolated **Longshot** in-game checklist, launchers copied from `E:/OOTRemake/tools/test-launcher-template-longshot.bat` (Kareem's 2026-11-13 decision); Claude boot-checks with `GAME=longshot`, Kareem plays.

Discord reports are ground truth, but missing #22 version/seed/settings/Zelda-history prevent diagnosis of that particular save. Neither repair is played yet. No game started, no game-folder writes, no merge/push. Native data, decoded research, scripts, saves and outputs stay outside the repository in `E:/OOTRemake/work/r14-story/`. Gates/sweeps serialize under `E:/OOTRemake/work/rounds/r14/gate.lock`, with Claude ordering the queue; workers 3 without Hookshot/Longshot, otherwise 1, selected at each stage start.

Claude's 08:47 queue rule: whoever is ready takes the atomic lock; if two wait, B, C, D, A. Release between stages. The external runner therefore executes one requested stage per invocation, not a gate waiter or an uninterrupted gates-plus-matrix reservation.

## Research sources and constraints

Read repository rules, README, CONTRIBUTING, architecture, Round 14 ownership, round orchestration rules, world format, decisions D18/D24/D31/D35/D39; game-data sections 12, 14, 15, 21 and 41; fast-start presets and GameData writer; Field/Market/Castle generated rules and remake overrides; GitHub issue bodies #21/#22.

The requested `work/rounds/r13/ootns2-findings-issue.md` actually contains the outbound chest/dungeon/card/trade findings, not the incoming Skip Child Zelda/door notes described in the prompt. Treat the described option only as an idea until independently traced. Kamil's findings sections 1–5 provide earlier fast-start precedents, not native escape/music proof. GPL `work/refs/sloperina-FINDINGS.md` section 1, “Useful name patterns”, describes saved quest enums/event history; facts only, no implementation copied. Native research is authoritative for this change.

The world format requires hand-written changes in `world/remake/*.toml`; translated OoT Randomizer files remain unchanged. Native evidence supersedes section 12's stones-only claim; that paragraph now points to section46 while retaining the independent played no-scale finding.

## Native trace

Escape: independently decoded `DoorOfTime`, `Goto_HyruleCastle`, their field/owl flows, native Challenge rows, Banc actor bindings and fresh `_0ce5/_91f9/_941f/_c061/_32f7` AINBs. Section46 records the exact Step03 escape / Step04 pickup gates and courtyard dependency. Fresh decoded `_0ce5` SHA256 `dab6c519b58b8fc4a7193ada643e4ab6b7e988fd2df46550bd2215cd81f1c663`, `_91f9` `d07c95bf92ecedbbfbab103973d146d6b2c4d42ba889a651964c49d54049b0aa`; both equal the historical decode. No native resource is patched for #22.

Implementation: `Met Child Zelda` at the native courtyard reward region; both moat checks and closed Door require it; `Time Flows` depends on that visit. Song-only/open remain independent. Moved the existing HF fixed-tier stanza into its field override to obey single-owner override rules. Replaced the obsolete stones-only shallow-moat test with story/each-stone/child/no-scale boundaries and the Egg/Chicken route. Updated existing door-mode behavior coverage and public directions/settings/logic docs.

BGM causal source: Bootup pack `Sound/Bgm/Game/BGMGeneralParam/BGMGeneralParam_Default.game__sound__BGMGeneralParam.bgyml`, `SequenceRangeDisableBgm`. Global15/property1651218793 spans Saria's bridge farewell (`Dm_Kokiri_0155`) to `HavePlayedEvent.Dm_HrlField_0000` (3546103570). The old skip left that end flag false. A separate post-Gohma interval also ends there. Own `music_condition_refs.py` validates all 122 C1 root headers: the field Start references globals10/5/**15**/7 plus local4; Stop uses10/5/7. The other interval beginning at `_0000` is global16 and is **not a field predicate dependency**. Its unresolved end Bool1517061892 stays false in all 303 ordinary post-owl saves (524 pre-owl saves also false). Do not set it speculatively.

Repair is exactly one named Kaepora initial value, `_0000=true`; existing four values unchanged. `_0005`, ArriveEntrance, ChangeENV, inventory, audio resources and other quests remain unchanged. The existing generic writer suffices, so `patch/gamedata.py` is intentionally unchanged. No resource is added to the NUP working set; the r13 integrated dump fixture remains applicable.

The native `Sound/Bgm/bgm.Product.111.byml.zs` contains binary subtype0xa1, unsupported by the production BYML reader; printed cause led to a research-only binary-preserving reader outside the repo, not an unrelated format change. The field SceneryParam and regular Day/Night predicates were traced in Bootup/BGM data. Reload/Market cannot clear the saved false panorama history; a forced native scene-BGM start in a later cutscene is a distinct possible recovery, not proof this history gate repaired itself. Night stop/day resume and actual recovery remain player observations to collect.

Source-review corrections: one scout initially inverted `EventQueryIsGameDataBoolExp` cases and proposed dropping stones; rejected after printing native Event38/39/56 and Event60. **Case0=true**, both Fire/Water quests complete advance Step03; the count0/1/2 is remaining stones. Another scout initially required closing anonymous1517061892; rejected by the C1 field-reference inventory plus native save states. Both recommendations were retracted. Neither entered product code.

**Product question (Kareem/Claude): offer a future “Skip Child Zelda” option? It would need `Step_Goto_HyruleCastle=Complete`, the native courtyard/Impa history and post-send-off `Step_DoorOfTime=Step02` before the native stone-quest check, plus the actual Zelda's Letter and Impa reward grants (including a shuffled Impa reward), and their tutorial/time-flow side effects. Simply setting played cutscenes or giving Zelda's Lullaby does not initialize the quest. This round implements only the conservative logic prerequisite; no option or quest-precompletion patch is added. A skip needs its own complete side-effect and once-only grant audit before approval/implementation.**

### Save inventory (read-only)

`inventory_saves.py` examined 821 historical slots: no child slot has all three stone quests Complete with `Goto_HyruleCastle` incomplete. Six pre-escape child slots have all three quests Complete, Zelda met, `DoorOfTime=Step03`. Candidate `2026-11-09_0954-main-after-jabu/save/5a3c9e1f0b7d24680000000000000001/slot_01`: caption area `ZoraDomain/ZoraDomain_Child`; extracted thumbnail shows Link on the circular stone platform in the blue cavern, beside the waterfall and below King Zora. This source remains untouched.

Kareem's newly transferred backup `2026-11-13_084401-longshot-transferred` has six child slots, all with `Goto_HyruleCastle=Complete`, `DoorOfTime=Complete`, three stone quests Complete. Three are in the Bottom of the Well, three in Kakariko. It cannot replay the escape unmodified. `inspect_transferred.py` records native enum names and caption areas, with thumbnails outside the repo. Plan: Longshot runtime for both checks, empty new-game source for music, historical pre-escape save copies for precise negative/positive story controls; no edit to any original save.

## Verification and player check

Pending implementation and Claude's gate queue handoff. Full required commands: `uv run ruff format --check`; `uv run ruff check`; `uv run pytest` with dump variables unset; `uv run pytest -m dump` with read-only native RomFS, repaired v131072 NUP and integrated dump-folder fixture (rebuild an owned r14 fixture if inputs grow).

Before-fix public smoke, under the owned gate lock (then released): `uv run python E:/OOTRemake/work/r14-story/build_public.py before`. Real `app.jobs.generate_seed`, seed 7, Chest-only, forest open, closed door, intro/Saria/Deku/Kaepora skips: **165 shuffled checks, 28 spheres, 91 resources**. Written GameData history is `_0000=false`, `_0005=false`, `_0010=true`; proof and generated output are in `public-before/`. This demonstrates the omitted earlier histories, not which one BGM reads or an in-game reproduction. Worker cap 3, neither game running at stage start.

Focused story regression: initial collection failed because `ALL_TIMES` is exported from `world.rules`, not `world`; corrected that printed import cause. On unchanged product rules the corrected regression then failed **4/4**, explicitly showing stones-only access returns True and courtyard access contributes no story event. After the sourced logic edit: `uv run pytest -q tests/test_story.py tests/test_door.py tests/test_world_remake_play.py` — **50 passed in 17.11s**. No game run is inferred.

Kaepora regression before repair: **1 failed, 1 passed, 1 dump skip**, with written panorama history False despite the skip. After adding the single sourced value: `CLAWSHOT_WORKERS=3 OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -q tests/test_fast_start_kaepora.py tests/test_fast_start_dump.py` — **4 passed in 3.37s**, including actual native writing and the exhaustive unchanged-entry/metadata oracle.

`uv run ruff format --check && uv run ruff check` — **336 files already formatted; all checks passed**. Claude's later queue steering orders the final serialized stages after B's dump: format/lint, full synthetic, full dump, then the matrix; release the lock between each so A/D can interleave. The included 18-cell empty-skip calibration is reused. If measured full-864 wall estimate exceeds about two hours, cut seeds7/42 repeats only and prove the complete 288-settings keyset is preserved.

No automated data check is presented as in-game proof. The combined checklist will identify saves by visible place/thumbnail and inventory/story state, include loading-log resources, and state a realistic play duration.

## One combined Longshot acceptance session

**20–30 minutes** with Debug teleport/clock; allow another 10 if unfamiliar with those menus.
Prepared staging recipe: `E:/OOTRemake/work/r14-story/stage_story.py`; master launcher
`E:/OOTRemake/work/r14-story/ingame/Test - story combined.bat`. It runs three isolated
profiles sequentially, waiting for each game to close. Staging/dry-run completion is recorded
below when executed; **Claude must boot-check with `GAME=longshot` before handing it over**.
No agent starts the game.

All three profiles use the same actual public-generated Chest-only mod: seed7, forest open,
closed door, intro/Saria/Deku/Kaepora skips. No chest needs opening, no spoiler needs reading.
Launchers are copied from the current **Longshot** template, use exactly one real mod,
`HOS_OOT_CHEATS=1`, no overlay, a separate `--user`, and `LONGSHOT_NO_UPDATE_CHECK=1`.
Use **only teleport and the clock**; do not change inventory, age or quests during the test.

1. **Fresh game / field music:** profile `story-music-next`, empty save source.
   - Start **New Game**, not Continue. Navi waking Link remains; intro movie and selected
     talks are skipped. Confirm ordinary music is audible in Kokiri first.
   - Walk out of the forest over Saria's bridge (forest open), then into Hyrule Field.
     At daytime, walk for several seconds: **no owl talk; regular field theme audible**.
     The bridge farewell may still play; it is not one of these skipped owl talks.
   - Enter the Market and return to the field; listen again. Save, title, Continue; listen
     again. Optional clock check: night may stop the normal daytime theme; return to noon
     and walk to test resumption. Record each observation separately.
   - Quit Longshot completely before continuing the master launcher.
2. **Raised bridge without the exact story step:** profile `story-escape-missing-step-next`.
   - Continue the child save whose thumbnail shows **Link on the circular platform in
     Zora's Domain's blue cavern, beside the waterfall below King Zora**. It has three stones.
   - This is a deliberate test-copy control: the authentic pre-escape source has
     `DoorOfTime=Step03`; **only that one enum word is changed to Ready**. The bridge-closed
     Bool stays true, inventory and every other save byte stay unchanged.
   - Teleport to **Hyrule Field (child)**, set noon, and approach the Market drawbridge from
     the field side. Expected: **bridge raised, no Zelda/Ganondorf escape, no moat Ocarina**.
     Do not try to get behind the bridge or repair the quest in Debug. Quit the game.
3. **Same save with the native required step:** profile `story-escape-ready-next`.
   - Continue the **same Zora's Domain thumbnail**, now the **unmodified Step03 source copy**.
     Three stones, Zelda met, bridge-closed Bool true; escape/throw history and Time
     ocarina/song ownership all false before loading.
   - Teleport to child Hyrule Field, set noon, approach the bridge head-on from the field.
     Expected: **Zelda/Ganondorf escape and Ocarina throw**, then the moat glint.
   - Take the glint. Expected: usable **Ocarina of Time and learned Song of Time** (Gift is
     unshuffled in this packet); Door quest should reach Step05. Check inventory/song use,
     not just a pickup notice. Leave/re-enter and Save/Continue: no repeat escape/reward.
   - Do not pull the Master Sword; adult travel is outside this short check.

The negative is **not an authentic “three stones, never met Zelda” playthrough**: none was
found in the 827-slot inventory. It deliberately isolates the exact Step03 sensor while
preserving the raised bridge, and therefore demonstrates why a raised bridge alone is not
proof the escape can trigger. It does **not** establish the original reporter's story state,
late-courtyard recovery, or every runtime's behavior.

Collect `longshot_log.txt` from each isolated user. Required loading proof:
`mods: GameData/GameDataList.Product.110.byml.zs <- <this profile's mod path>` and, for the
new-game intro, `mods: Event/EventFlow/OpeningEvent.bfevfl.zs <- <same mod>`.
The escape flow is intentionally native/unmodified (#22 is a logic fix), so do not expect a
`mods:` line for `DoorOfTime`. Claude can read the new positive save for Step04/05,
escape history and actual Ocarina/song stock; never write to Kareem's original backups.
If a result differs, stop and retain that profile/log/save: no unchanged rerun or live patch.
