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

### Additional Zelda-dependent consumers (Claude steering, 09:45)

Track E's 09:42 AINB findings were accepted for this track before gates. `Met Child Zelda`
now explicitly means **the whole courtyard/Impa lesson and accepted send-off through
DoorOfTime Step02**, not initial contact/Step01. Native Step01 Impa talk starts the lesson
without an item/stone query; the after-lesson talk Event124 reserves the field boot event.
EventSetting maps `HyruleField_DoorOfTime_SendOff` to `DoorOfTime_SendOff`; its printed
reachable graph is Event65 → Event10 (`Dm_HrlField_0020`) → Event91 → **Event7 (Step02)**
→ Event62. No extra inventory/stone gate is present. Completing that available interaction
is modeled at the existing courtyard reward region, so no second story event is needed.

Reprinted E's decoded `_3265` and `_bbc3`: child Saria Create and the unplayed-song trigger
both consume `DoorOfTime_IsAfter_Step01_Exp`. Added the Song-from-Saria rule to
`remake/child_sacred_forest_meadow.toml`, requiring the shared event; translated
`sacred_forest_meadow.toml` stays untouched per the override convention.

Reprinted `Market_Child_Prefab_0c76`: node3 EnableOpen is completion AND night; EnableDo
also requires completion. E's native Banc census gives the same shopkeeper Presence flag.
Runtime world smoke confirms **eight shelves, zero interior events, one return exit**;
all shelves deny without `Defeat King Dodongo` and allow with it at adequate wallet capacity.
Thus no existing check/alternate route bypassed the boss, but interior reach was wrong.
Corrected the entrance to require the existing boss event plus night/`Time Flows`; no
shop-stock, reward or pool changes. Proposed by E, assigned by Claude, implemented by cs14c.

New regressions reproduced both old-rule mismatches (persistent story event not honored by
Saria; night/TimeFlows alone opened the shop). Fixture corrections came from printed
payloads: external counts do not populate Search.holds' derived-event set; default `at_night` folds to
available-time true, so the clock boundary explicitly uses the supported
`build_world(..., {"ensure_tod_access": True})` logic flag, not a duplicate setting.
Final `uv run pytest -q tests/test_story.py`: **6 passed in2.10s**.
Consumer smoke additionally took the real field → Egg → courtyard → Saria path and printed
False/False → True/True for the story event/source; checked all eight shop releases and
the entrance's pre-boss-night / post-boss-night / post-boss-day results **False/True/False**.
The earlier broad focused run was81 passed/1 night-fixture failure, not a full gate.

### Return-proof integration found by the first full gate

Frozen `b5cd1a5` format/lint passed (336 files). Full synthetic then **failed11,
passed1201, skipped141 in176.44s**; lock released and B's final synthetic given priority.
Failure payloads reject even closed-door defaults; the native-world vanilla proof also fails.
No unchanged rerun. The printed cause is twofold:

- The construction's closed-door lower bound omitted the newly compulsory story event.
  Added `Met Child Zelda=1` to **only the closed-door** `age_return_fill_inventory`;
  song-only/open lower bounds remain unchanged.
- `mandatory_pull_inventory` considered only non-Event/non-Drop items. Runtime metadata
  confirms `Met Child Zelda` has a declared source but **no item-table entry**, so merely
  admitting Event-typed items would still miss it. The independent post-pull proof lost a
  native story flag that every closed-door pull must already have.

The generic proof now subjects **declared acquired events** to the same child-only count-cap
test as items (excluding the pull itself, already supplied separately). Optional history
is excluded; no blanket precompletion or hard-coded Zelda branch is introduced. A synthetic
regression printed `child_story_collected=1` while mandatory counts had only Song/Strength;
after the fix it preserves the compulsory source, excludes Optional History and proves return.
Its first fixture used an unavailable `is_child` helper; corrected to the fixture's existing
`age == 'child'` rule after the printed unknown-name error.

Focused after: `tests/test_age_fill.py tests/test_age_travel.py tests/test_story.py` —
**23 passed in10.71s**, including an actual whole-world Chest+Shop seed and the independent
return oracle. Exact former failure `test_world_data.py::test_vanilla_placement_is_beatable` —
**1 passed in1.96s**. Source/test formatter left both files unchanged. Replacement full gate
uses a separate attempt log so the first failure evidence is retained.

### Rejected extra Saria/Darunia gate and added gameplay check

Claude paused the matrix for the newly licensed OotrR (Mozencaz, MIT) lead. Track E's
12:33 native verdict rejects it for this build: registered
`SacredForestMeadow_Field_MelodyGet_Saria` runs Event0 → `Dm_MelodyGet_Saria` **first**,
then Event3 resets pose and Event4 calls `Get_StoneOfFire_MelodyGet_Saria`.
The movie's Event109 grants `Item_Melody_SariaSong`; its only query is TalkChoice2.
The later hook's Event83 tests `Get_StoneOfFire_IsAfter_GoronCityDarniaTalk_Exp`; true
advances the journal to `SariaMelodyPlay` (Event86), false ends without suppressing the
already-given reward. The SFM AINB gates remain DoorOfTime-after-Step01/unplayed song.

Claude accepted that ordering: **no extra rule/event, no code change or re-freeze**.
A second source claims otherwise from play, so the combined fresh-game check now goes
from actual Zelda/Impa send-off directly to Saria **without visiting Darunia/Goron City**.
The existing song regression already accepts the Zelda event without any Fire event.
This native trace does not substitute for that new player observation.

## Completed merge gates on code commit57e12aa

- Replacement `ruff format --check`: **336 already formatted**; `ruff check`: **all passed**.
- Full synthetic: **1213 passed,141 skipped in643.09s**, runner643.64s.
- Full dump: **139 passed,1215 deselected in4530.31s**, runner4530.81s.
- Each used workers3 after exact-name checks found neither game process; each owned lock
  released in finally. Native inputs: actual Hookshot RomFS, repairedv131072 NUP and
  unchanged r13 integrated fixture. No working-set expansion.
- Logs/results: `E:/OOTRemake/work/r14-story/gate-results.json`, `gate-*-attempt2.log`,
  `gate-dump.log`. The failed first synthetic remains in `gate-synthetic.log`.
- Current queue after dump: E short stages, D synthetic, A synthetic, then C matrix;
  matrix/public-after staging have not run at this evidence point. No game started.

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

## Longshot acceptance checks

**Two independent sessions:** music/Kaepora **10–15 minutes**; story **35–50 minutes**.
Allow another15 for unfamiliar castle guards/Debug menus. Either can be done separately.
Launch from `E:/OOTRemake/work/r14-story/ingame/`:
- `Test - Music and Kaepora.bat`
- `Test - Zelda Saria and escape.bat`

Each starts its **own fresh new-game profile**. The story session then opens two isolated
historical escape controls, waiting for each game to close. Follow the adjacent `CHECKLIST.md`.
**Claude must boot-check with `GAME=longshot` before handing either over.** No agent starts
the game. Recipe: `E:/OOTRemake/work/r14-story/stage_story.py`.

All four profiles use the same public-generated Chest-only mod: seed7, forest open,
closed door, intro/Saria/Deku/Kaepora skips. No chest needs opening, no spoiler needs reading.
Launchers are copied from the current **Longshot** template, use exactly one real mod,
`HOS_OOT_CHEATS=1`, no overlay, a separate `--user`, and `LONGSHOT_NO_UPDATE_CHECK=1`.
Use **only teleport and the clock**; do not change inventory, age or quests during the test.

### Music and Kaepora (10–15 minutes)

Open `Test - Music and Kaepora.bat`; fresh profile `story-music-next`.
   - Start **New Game**, not Continue. Navi waking Link remains; intro movie and selected
     talks are skipped. Confirm ordinary music is audible in Kokiri first.
   - Walk out of the forest over Saria's bridge (forest open), then into Hyrule Field.
     At daytime, walk for several seconds: **no owl talk; regular field theme audible**.
     The bridge farewell may still play; it is not one of these skipped owl talks.
   - Enter the Market and return to the field; listen again. Save, title, Continue; listen
     again. Optional clock check: night may stop the normal daytime theme; return to noon
     and walk to test resumption. Record each observation separately.
   - Quit Longshot when finished. The story launcher uses a different fresh profile.

### Zelda/Impa, Saria and escape (35–50 minutes)

Open `Test - Zelda Saria and escape.bat`. Pause points separate its three profiles.

1. **Fresh courtyard/Saria:** profile `story-courtyard-saria-next`.
   - Start New Game and walk out of the forest normally to receive the Fairy Ocarina
     at Saria's bridge; no chest needed. This session does not depend on the music save.
   - **Saria before Darunia:** follow the actual child castle route:
     Malon's fixed Egg / Chicken, wake Talon, pass the guards, complete Zelda and Impa's
     lesson, and accept Impa's field send-off. Teleport only to area entrances during this
     sequence; do not teleport past Talon/guards or change quest steps.
     **Do not visit Goron City or Darunia.** From Impa's send-off go straight to child
     Sacred Forest Meadow. Expected: **Saria is present and teaches Saria's Song**;
     confirm the learned song, not just dialogue. If unarmed, teleport to the north
     clearing just south of Saria (approximately -2,114,-94), then walk toward her stump;
     this avoids Wolfos combat without altering story state. Keep a save immediately
     before approaching Saria and report the result even if it contradicts the trace.
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

## Immediate staging handoff (before matrix, per Claude)

Code tree was checked against **57e12aa** (`git diff --quiet 57e12aa -- src`, exit0);
later commits change only evidence/checklist docs. One actual public `app.jobs.generate_seed`
run built seed7 after the fixes: **165 shuffled checks,28 spheres,91 resources** in58.23s.
Read-back native GameData history: `_0000=true`, `_0005=false`, `_0010=true` (before:
false/false/true). Proof: `E:/OOTRemake/work/r14-story/public-after/proof.json`.
This one staging seed ran alongside D's authorized native gate as requested; it did not
claim/remove D's lock. It was not the matrix or a many-seed run.

`stage_story.py` then created **four physical one-mod copies**, each91 files, and two
independent entry launchers. Actual `cmd.exe /d /c` with `CLAWSHOT_DRY_RUN=1`:
**all four child launchers and both entry launchers exit0**. Runtime resolves to
`LongshotLauncher-data/builds/v3.0.0-rc.2/bin/longshot.exe`; each uses its own user,
only its own mod and no overlay. Both fresh users have no progress slots. **No game started**.

Story controls: original child/Zora's Domain snapshot has Step03, completed castle,
raised bridge, all stone stocks1 and no escape/throw/Time-ocarina/Time-song state.
Negative differs in exactly the one enum word at offset93156, Step03 → Ready.
Original progress/caption/account/options SHA256s unchanged. No authentic never-met-Zelda
three-stone save is claimed. `ingame/staging-proof.json` records these checks.

Ready paths posted to the round thread for Claude's boot-check/hand-off:
- `E:/OOTRemake/work/r14-story/ingame/Test - Music and Kaepora.bat` —10–15min.
- `E:/OOTRemake/work/r14-story/ingame/Test - Zelda Saria and escape.bat` —35–50min.
- `E:/OOTRemake/work/r14-story/ingame/CHECKLIST.md` — player-only extract of the section above.

Both sessions can be played separately; the second has its own new-game profile, not the
first session's save. It includes the Saria-before-Darunia observation plus the two
escape controls. **Boot and gameplay remain unplayed by cs14c**; Claude boot-checks and
Kareem observes. Packet/profile files stay frozen while the player uses them.

## Played acceptance — Kareem, Longshot (reported/read by Claude)

Claude relayed all four **PASS** results on2026-11-13. These are Kareem's actual observations
and Claude's save reads, not another agent run or a rerun to confirm them:

1. **Music/Kaepora PASS:** Hyrule Field music plays correctly with the skip enabled.
2. **Courtyard/Saria PASS:** real Malon/Talon/courtyard/Impa sequence, then Sacred Forest
   Meadow **without visiting Goron City/Darunia**. Teleport landed directly in Saria's
   cutscene; Kareem also approached from the Lost Woods side, using noclip only for
   movement past Wolfos. Song learned and in inventory. Claude read
   `Goto_HyruleCastle=Complete`, `DoorOfTime=Step02`, and owned Zelda's Letter, Lullaby
   and Saria's Song. This confirms the teaching route, not natural Wolfos combat.
3. **Missing-step control PASS:** bridge up, no escape; saved DoorOfTime remains Ready.
4. **Ready control PASS:** escape and Ocarina throw play; Ocarina of Time and Song of Time
   obtained, saved DoorOfTime reaches Step05. Reload leaves the bridge down, without replay.

Runtime loading proof independently read from each staged `longshot_log.txt`:
`mods: GameData/GameDataList.Product.110.byml.zs <-` each profile's own staged mod
(music line73; courtyard/Saria, missing-step and ready line58). The intro resource
`Event/EventFlow/OpeningEvent.bfevfl.zs` also loads from those mods (lines450/455/451/452).
All logs stay outside the repository under `E:/OOTRemake/work/r14-story/ingame/user-*`.

The **in-game requirement is complete**. No agent started or played the game; packet/profile
files are not rewritten after play. Separate music night/day, Market-return and music-reload
observations were not relayed, so are not additionally claimed. Late-courtyard recovery and
the original reporter's exact save cause remain outside these controlled observations.

The matrix remains the only pending C verification stage, next after D's posted15:34
native-stage release. D's own dump failures do not change C's57e12aa native139-pass result.

## Completed public-path matrix

Code **57e12aa**, unchanged executable/data tree throughout; later commits are docs-only.
The cs13a public CLI/settings-validation/native `make_seed`/spoiler/play-note probe ran every
combination: all16 offered skip subsets ×3 forest modes ×3 door modes ×2 presets ×seeds1/7/42.
**864 expected,864 observed; all288 distinct settings preserved; no seeds/repeats cut.**

- **576 generated successfully.**
- **288 expected refusals:** pre-existing `song_only`/`open` + Chest-only adult-return-guarantee
  validation messages (16subsets ×3forests ×2early doors ×3seeds). Not new failures, not
  silently omitted combinations.
- **0 unexpected outcomes.**
- Included18 pilot cells took77.953s; full estimate3741.744s was below7200s, retaining
  all three seeds. Actual matrix2925.20s; runner2925.92s, workers3/no game at stage start.
- Owned gate lock released; exact counts accepted by Claude. D revalidation has the next slot.

Evidence, outside the repository: `E:/OOTRemake/work/r14-story/matrix.jsonl`,
`matrix-plan.json`, `matrix-summary.json`, `gate-matrix.log`, `gate-results.json`.
All originally requested C gates and all four player checks are complete. Claude subsequently
requested integration onto B's merged `main`58ba776, light checks, then a rebased full
synthetic in the gap after D synthetic and before D dump; that integration evidence follows.
