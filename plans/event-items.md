# Events name and show the item given

Record of feature `event-items` (spec and plan: `docs/specs/event-items/`, kept local). Branch `feature/event-items`
in the main checkout, made off `feature/ocarina-song-drops-everywhere` at `ceab074` (PR #42, open on 2026-11-25).
Dump: romfs 1.1.1. Builds on `plans/chest-ocarina-model.md` (PR #40; Saria farewell known issue) and the fix design in
`plans/rounds/r21-pr40.md:429-442`.

## Handoff 2026-11-28 (Claude, after the final run)

- Committed and rebased onto main `5ea1c58` (PR #42 merged with Kareem's changes), then `69dfe92` (R07 chest tunics); PR opened (BBender, 2026-11-28:
  "make the changes ... rebase onto main ... Then open a PR. If you need any decisions go with the recommended for now
  but note them"). Backup of the pre-rebase branch: `backup/event-items-pre-rebase` (local).
- Rebase decisions (Claude, recommended, for BBender to confirm):
  - main's `display` rule (`_display_item`, 9e5b97a) and this branch's (`_set_display`, get windows and Notes targets)
    are one field: `_set_display` takes main's literal-actor checks and error wording, main's validation in `loads`
    stays, the two extra refs stay (`Dm_MelodyGet_Time/Event280`, `Dm_Kokiri_0155/Event58`).
  - merchants (`GC Medigoron`, `Kak Granny Buy Blue Potion`, `Wasteland Bombchu Salesman`, shuffled on main since
    #42) speak the same messages for their shuffled first sale and their native repeat sales: their marks wait
    (`event_lines.REPEAT_SALES`), as decision D's re-offers.
  - Talon's Cucco game (main's `talon.py`, round 22 scenes): with a moved prize main writes neutral English in his
    first-prize lines (`Talk_09_2`, `Talk_29`, its D26) and keeps the repeat prize (`Talk_11`, `Talk_56`) and the milk
    sale (`Talk_57`) native. The dump suite caught the clash (our CNzh fingerprint on main's rewritten line); all five
    Talon marks wait (`event_lines.WRITTEN_ELSEWHERE`). Naming the given item in the first-prize lines instead of
    main's neutral words is a question for the maintainers.
  - main's `test_gift_display_dump.py` checked only get windows: it now accepts the declared Notes targets too.
  - main's direct-pouch ocarina seed runs `containers`' ActorInfo rows before the ocarina step: added to the test's
    `ROW_STEPS` (`tests/test_getitem_ocarina_dump.py`).
- Suites after the rebase: synthetic 5176 passed, 967 skipped; dump 877 passed, 7 failed, 16 errors, all from Talon's
  lines and the display test above; after the fixes the affected files rerun green (90 passed, then the one ActorInfo
  test, 4 passed). After the rebase onto `69dfe92`: synthetic 5184 passed, 967 skipped; tunic, gift, display and
  event-line dump tests 35 passed.
- Fairy reruns for J and K (BBender, 2026-11-28, Longshot 3.2.0, seed from the rebased branch, `fairy/seed`,
  base 7100), all pass: castle (Iron Boots) the spin attack line vanilla (J); summit (Bomb Bag), Zora's Fountain
  (Megaton Hammer, `child-zoras-fountain-great-fairy-500r`) and desert (Hylian Shield, `...-500r`) name the given
  item in the spell's explanation line, and the get window names it (K). Not played: the crater fairy (no save).
  The older handoff below is history.

## Handoff 2026-11-26 (Claude, for the next session)

Read this first. Nothing is committed; no commit or PR until BBender confirms. Work folder:
`C:/Users/bened/ootr/work/event-items/` (`qa/next-runs.md` run list, `qa/run-results.md` every played result).

- **Done and played this day:** model-only placed objects (crash fix, R1 moat sword); Zelda's Letter randomized
  (`plan_subflow_renames`, r1-zelda3); song containers (D16b, D17); the song effect in events by emit
  (`event_models.add_song_effect`: flow emit after each bind/join, timeline emit clip; S1 Saria's farewell passes);
  **D18** (song containers name the event user `Clawshot_Song_<Song>_Event`, effect on `Skl_Root`): S2c, Zelda's
  throw with Bolero, the effect now follows the ocarina, no lean.
- **D18 code** (uncommitted): `songs.patch_event_elink`, `songs.event_user_name`, `songs.EVENT_BONE`, `_add_users`
  (shared with `patch_elink`, whose output is unchanged); `containers.build_pack(elink_user=...)`, the container row's
  `ELinkUserName`, `containers.changes` adds the `ELINK` transform for song containers. Tests: 3 new in
  `tests/test_songs.py`, 1 new in `tests/test_containers.py` (plus the row test edit), `tests/test_containers_dump.py`
  (fresh members, event users on `Skl_Root`, a new sizing test). Synthetic tests pass, ruff passes. **Dump tests for
  D18 not run**: BBender's rule, no dump tests during the run session; run them once the run list is done.
- **D19 code** (uncommitted): `event_models.box_centre`, `hand_shift`, `_f32`, `HandRename.shift`, `add_hand_bind`
  (adds the shift to the template bind's `TransOffset` as f32), `plan_hands(hands, moved, rows)` (shift from the hand's
  `item` and `getitem.model_actor` of the given item), `seed_changes` (reads the dump's ActorInfo when a hand bind is
  planned). Tests: 4 new and 1 edited in `tests/test_event_models.py`, 1 new in `tests/test_event_models_dump.py`
  (heart at the moat = the pilot's value; checked by hand against the dump with the same code). Synthetic tests pass,
  ruff passes. **Dump tests for D19 not run** (run-session rule).
- **D20 code (uncommitted):** `elink.Elink.action_triggers`, `add_action_triggers`, `_action_table` (+ the trigger
  table layout in the module docstring); `songs.SCENE_SLOT`, `SCENE_TEMPLATE`, `_add_users(scene_actions=)`,
  `patch_event_elink(scene_actions=)` (`patch_elink` unchanged); `containers.changes(scene_actions=)`;
  `event_props.Prop.scene_as` and `scene_as` on 7 props in `event_props.toml`; `event_models.scene_actions`,
  `plan_scene_actions`, `seed_changes` passes them on. Tests: 7 new in `tests/test_elink.py` (12 cases) (+ `ActionTable`,
  `HEART_ACTION_USERS` in `tests/synthetic_effects.py`), 3 in `tests/test_songs.py`, 3 in `tests/test_event_models.py`,
  2 in `tests/test_event_props.py`, 2 dump tests in `tests/test_event_models_dump.py` (every animation a flowchart prop
  plays has its trigger or is the donor's own; a seed's song event users answer every scene animation, native users
  byte-identical). **Dump tests for D20 not run** (run-session rule; collected). Seeds `qa-matrix-A/seed` and
  `qa-real/R1-A/seed` built with it (same placements as `qa-matrix`, `qa-real/R1`): the ELink tables reproduce through
  the code from the dump (`songs.patch_event_elink` then `patch_elink`), and with the pilot's three actions the same
  code gives both pilots' tables byte for byte (`R1` only when the triggers are added after a first encode, as the
  pilot did: that encode's 4 padding bytes stay inside the pilot's name table; one pass leaves none). A vs pilot: `qa-matrix-A` has the two target triggers only
  (no Darunia song there), `R1-A` only Darunia's; hence also shorter name tables and the warp songs' own users'
  name offsets (the songs step appends its names after the event users'), decoded the same. Their Mals files differ
  from the pilots' too: the event-lines work (Q8) since the pilot build, not D20.
- **Line endings:** Python `write_text` on Windows writes CRLF. Four files were converted back to LF on 2026-11-26;
  write with `newline="\n"` or bytes.
- **Ready at handoff:** `qa-matrix/seed` rebuilt with D18 (225 files; Sun's Song container names `Clawshot_Song_SunSong_Event`, `Skl_Root`, checked) (old copy `qa-matrix-v2`; old R2 in
  `qa-real/R2-v1`). Check the build finished (`qa-matrix/seed` exists, about 225 files) before launching; if not:
  `nice -n 10 uv run python -I <work>/tools/build_matrix_seed.py C:/Users/bened/Games/Hookshot/romfs <work>/qa-matrix 7100 --once`.
- **Next runs, in order:** S2 again on the rebuilt `qa-matrix` (save `child-hyrule-field-before-drawbridge`, Sun's
  Song shown as the Fairy Ocarina: does the effect follow the throw with the Fairy model; is the yellow glow on Link
  Sun's own effect, compare with its get pose); then S3 (target, Epona's Song, same `qa-matrix`), S4 (R1 Darunia,
  Song of Storms: rebuild R1 for D18 first, `tools/build_real_seed.py ROMFS <work>/qa-real/R1 7100 R1 --once`), S5
  (`qa/seed` Light Arrows Bolero, effect not doubled: rebuild `qa/seed` for D18 too, `tools/build_qa_seed.py ROMFS
  <work>/qa 7100 --once`), S6 (hand-offset pilot, issue 4; adopting it changes D6). Ask BBender before building
  while they play (CPU).
- **Known issue confirmed again (S2c):** in the moat look Link also holds his equipped ocarina (plan 10.4, arm A).
- **Q8 lines (uncommitted), dump tests not run:** 24 lines added to `patch/event_lines.toml` (50 in all) and the
  as-text match now takes the rest of its word; see "Q8 code" under Decision Q8. Synthetic `tests/test_event_lines.py`
  passes (24), ruff passes; the dump tests (`tests/test_event_lines_dump.py`, collected) wait for the run-session rule.
- **Hand-read marks (uncommitted), dump tests not run:** the name matcher is replaced by BBender's hand-read marks
  (`patch/event_marks.toml`, 164 lines, 2349 marks; `patch/event_lines.toml` deleted); see "Marks code" under
  "Hand-read marks". Synthetic `tests/test_event_lines.py` (17) and `tests/test_event_marks_convert.py` (4) pass,
  ruff passes; `tests/test_event_lines_dump.py` (2, collected) waits for the run-session rule. A read-only scratch
  check of every mark against dump 1.1.1 found no problem. Preview for BBender:
  `C:/Users/bened/ootr/work/event-items/lines/preview.md`. To confirm: the two lines kept from outside the reading
  (Gohma's caption, Ruto's line) and the drop of the Kokiri shopkeeper's `Talk_0102`.
- **App working set (Claude, 2026-11-27, after BBender's app run from a `.nup` failed with `PatchError: no actor
  pack Pack/Actor/Dm_Item_Ocarina_Fairy.pack.zs`; uncommitted):** for a `.nup`, `.nx` or dump folder the app
  generates from a temporary copy of only the declared working set, `clawshot.pack.source.working_files`
  (`pack/resources.toml` plus each step's `native_inputs()`); an extracted romfs folder is used as is, which is why
  no QA build saw it. The event-items steps read five files nobody declared: `containers` the donor
  `Dm_Item_Ocarina_Fairy`'s pack; `placed_models` (through `event_models`) the placed objects' packs,
  `Obj_Ocarina_Time_A_01` and `Obj_InsideJabu_Jabu_Stone_Water_A_01`; `saria_farewell` (every seed, so every
  `.nup` seed failed, gifts or not) `Npc_Kokiri_Saria_Child`'s pack and her `AIScheduleParam`. Everything else they
  read was already in the set (flows, Banc files and language archives by pattern; the item packs, tables, ELink and
  size table by name). Now declared, data-driven: `containers.native_inputs(actors)` (donor, each item's container
  model's pack, a song's effect donor and ELink), `event_models.native_inputs(actors)` (that plus the versions list,
  the `placement` props' packs from `event_props.toml` and each item's `getitem.model_actor` pack),
  `event_lines.native_inputs(actors)` (each item's pack for its text key: `_text_key` falls back silently without
  one), `saria_farewell.native_inputs()`, registered in `working_files` for every actor of `item_actors.toml`. The
  set grew by exactly those five files (1301). Cross-check: a read/probe trace of the five QA builds
  (`build_final_seed.py` with and without `--models-off`, `build_matrix_seed.py`, `build_qa_seed.py`,
  `build_real_seed.py R1`, base 7100) read nothing outside the new set and probed no existing file outside it; the
  old set missed the same five. Tests (new only): one working-set test each in `tests/test_event_models.py` (plus
  one that the patterns hold the props' flows and Banc files), `test_containers.py`, `test_saria_farewell.py`,
  `test_event_lines.py`; dump `tests/test_event_items_working_set_dump.py` builds from a copy of only the working
  set (Recommended preset seed 2431999637; event-scene placements, models on and off) and compares with the same
  build from the whole dump (3 passed, 10 min). The real `.nup` (`C:/Users/bened/git/nup/0400486024dec000_v131072.nup`)
  through `clawshot.app.jobs.generate_seed`, read only, output in a scratch folder: seed 2431999637 succeeds with
  the Recommended preset (204 files, four containers, Saria's actor) and with the QA seeds' event-heavy settings
  (songs anywhere, dungeon rewards, Chest+Gift; 228 files, thirteen containers). Not run: `tests/test_pack_nup_dump.py`
  (needs `OOT_NUP`; its full mode matrix is long) and the full suites.
- **After the runs:** dump tests of the changed areas, then the full synthetic and dump suites once, the docs' played
  list (`docs/settings.md`, `docs/specs/event-items/pr.md`), plan 6.5 (Eyedrops/Biggoron saves), plan 16 (commit and
  PR only after BBender confirms).

## Decisions

Copied from the spec (2026-11-25); later decisions added with who and date.

| ID | Who, when | Decision |
|---|---|---|
| D1 | BBender, 2026-11-25 | Feature name `event-items` (BBender's suggestion). |
| D2 | BBender, 2026-11-25 | Text: every display-only get window in a flow with a gift step names the given item, plus Zelda's Notes screenshot `TargetID` (`Dm_Kokiri_0155` Event58 and its like). Always applied, whatever the setting. |
| D3 | BBender, 2026-11-25 | Models: every gift and reward event whose shown prop is the vanilla item given (all three mechanisms). Played instruments stay native. |
| D4 | BBender, 2026-11-25 | Model choice: the event shows the model Link's get pose shows for that item. Songs show their ocarina (`getitem.SONG_MODELS`), Nothing and another player's item show Zelda's Letter (`custom_items.DONOR`), every other item shows its own actor's model. |
| D5 | BBender, 2026-11-25 | Moat: Zelda's thrown prop, the object in the water and Link's look all show the given item. |
| D6 | BBender, 2026-11-25 | Native bone, pose and offsets; no per-item tuning. Clipping and odd sizes are intended (the point is that it's funny), never a defect. |
| D7 | BBender, 2026-11-25 | New setting `event_item_models`, label "Show shuffled items in events", default **on**; it switches the model swaps only. Settings are a maintainers' call (AGENTS.md), so the PR asks Kareem to confirm. |
| D8 | BBender, 2026-11-25 | NPC dialogue lines that name the vanilla item are rewritten too ("try"). If that grows out of proportion (BBender decides from the plan's inventory), the lines move to a follow-up spec. |
| D9 | BBender, 2026-11-25 | When Saria's fix applies (every seed, or only seeds that can reach the pre-Gohma farewell) is decided **after** the investigation shows the exact conditions. |
| D10 | BBender, 2026-11-25 | Played checks: one QA seed reaching every event fast; BBender saves before each event; Claude copies the saves into a collection at `C:/Users/bened/ootr/work/event-items/saves/` and reuses it for every rebuild. |
| D11 | BBender, 2026-11-25 | Saria matrix axes: Gohma beaten, Fairy Ocarina owned before, gift item and prop row, candidate stow fix, Longshot version **3.2.0 vs 3.0.0** (BBender installs 3.0.0; 3.1.1 not tested). |
| D12 | BBender, 2026-11-25 | Work in the main checkout (`C:/Users/bened/git/Clawshot`), on branch `feature/event-items`. |
| D13 | BBender, 2026-11-25 | Progressive tiers: gift grants are fixed when the seed is generated, so the model follows the actor the grant gives. Native branch pairs (LW Target's Medium/Large bag) keep their branches, each showing its own branch's item. |
| D14 | BBender proposed, Claude agreed, 2026-11-25 | Props are **container actors**, not native item actors (BBender's proposal, Claude agreed, 2026-11-25): one new actor per model a seed needs, from a native event-prop donor, holding only the model under its own uniquely named `ModelInfo` member, with no pouch, pickup, get-pose or effect components. It replaces both investigation variants (A: rename to the native item actor; B: re-model the event's own prop) for flowchart and timeline props. Exception: the moat water object must stay the pickup, so it gets variant B (its own member). Reasons: no native item behaviour in events (field objects such as `Obj_Heart_Piece` or rupees could be collectible), no shared component path (the Link's-ocarina pitfall), and one mechanism for every item family. |
| D15 | BBender asked; static cause Claude, 2026-11-25 | Containers keep the item's animations where they are visual (BBender asked, 2026-11-25). Material animations: the donor's `ModelVariationAnims` plus a reference to the donor's own `AnimationParam`. Static cause of the demo's crash (Claude, dump 1.1.1, not played): Saria's prop has an empty `Dummy` AnimationParam, yet got Biggoron's `ModelVariationAnims` (`Weapon_Sword_Biggoron_Color.fmab`), which lives in `Weapon_Sword_Biggoron_Animation`; no native `Dm_Item_*` prop uses `ModelVariationAnims`. Effects: the donor's `ELink`. Motion through the scene comes from the event's bind or timeline anyway. Idle motion (a heart piece's spin, a rupee's turn) is decided after a test (D16). |
| D16 | BBender, 2026-11-25 (after pilot arms B and C) | No idle animation in containers. Superseded by D16b. |
| D16b | BBender, 2026-11-26 (after the Light Arrows run and pilot arm B) | D16 revised: every container takes its model's own animation set (`ASRef`, `ASInfoRef`, `XLinkRef`) where the model has one (not `DemoDummy`/`Dummy`), so a scene that plays an item animation on its prop plays it (`Dm_TimeTemple_0130` Event15 `Rotate_GetDemo`); scenes that play none stay still (arm C). Options offered: all containers (chosen) or only containers of animating scenes. |
| D17 | BBender, 2026-11-26 (after pilot arm B) | A song shown in an event has a container of its own (`Dm_Item_Clawshot_Item_Melody_<Song>`), built from the song's pack as the song step shows it (`songs.patch_song_pack`: the ocarina's model, the song's effect user `Clawshot_Song_<Song>`, the common animation set) and its row as the song step makes it (`songs.shown_row`), so the scene shows the ocarina with the song's effect. Options offered: in this feature (chosen) or a known issue. |
| D18 | Claude, 2026-11-26 (after runs S2, S2b); played S2c (BBender) | A song container names an event user of its own, `Clawshot_Song_<Song>_Event` (`songs.patch_event_elink`: the song's user with its get-pose effect, and a warp song's children, on `Skl_Root`), through its own ELink member (`containers.build_pack(elink_user=...)`, sized from the heart container's). Why: Zelda's throw animates the prop's `Skl_Root` and leaves `Root` at the origin, so an effect on `Root` stayed at the landing spot (S2 Sun's Song, S2b Bolero: not a model mismatch). The song's own user keeps `Root` (E6, its upright get pose). S2c: the effect follows the throw, no lean. Test edits: `test_a_song_containers_row_shows_...` and the song dump test now expect the event user; the dump test's fresh members include the song container's ELink member. |
| D19 | BBender, 2026-11-26 (after pilot run S6) | Hand binds the feature adds (`Clawshot_hand_bind`, the moat's Link's look) hold the item by its middle: the bind's `TransOffset` is its own plus (native held item's model box centre - shown model's box centre), both from ActorInfo `ModelAabbMin`/`ModelAabbMax` (native: the event's own item, `Item_Ocarina_Time` at the moat). Computed per seed from the model, no per-item tuning. Changes D6 for these binds only; the scenes' own binds keep their native offsets. S6 (Piece of Heart, TransOffset about (-0.009, -0.175, 0.002)): sits by its middle, looks right. Fixes issue 4. |
| D19 code | Claude, 2026-11-26 (to confirm) | Implemented in `event_models` (uncommitted). Native row: the hand entry's own `item` (`event_props.toml`, `Item_Ocarina_Time` at the moat), not hard-coded. Shown row: `getitem.model_actor` of the given item (a song: its ocarina, whose model fields its container row copies via `songs.shown_row`; anything else the container's model). Both rows from the dump, not the seed output: the container rows copy their model box verbatim from these dump rows, no step changes a model box of the native or shown rows (the ocarina get model changes only `CalcPriority`), the scene's pose was made for the vanilla ocarina, and the flow transform then does not depend on the order of the ActorInfo steps. Moat heart: (-0.0087890625, -0.17549985647201538, 0.0017242431640625), the pilot's value exactly. A template bind without a 3-float `TransOffset` is refused when the shift is not zero. |
| D20 | Claude, 2026-11-27 (fix agent; played pilot A, S12/S13 by BBender) | A song container's event user also starts its get-pose effect from the scene animations the seed's events play on song containers: every `Clawshot_Song_<Song>_Event` gets, in slot `AS[Lower]`, an action `<scene set>/<node>` per such animation with a copy of its `Rotate_GetDemo` trigger (call `GetDemo`) under the guid CRC32(`<user>/<action>`), actions sorted as native users sort them (`elink.Elink.add_action_triggers`). Why: the emitted key (D17/D18 emit) does not show while a scene animation plays on the prop (S3, S4, S11); natively an item answers a scene animation by such an action (`Obj_Heart_Piece`: `Dm_Goron_0040_Obj_Heart_Piece/C01`); pilot A passed at the target (Epona's Song, S12) and at Darunia (Song of Storms, S13). The emit stays (Saria's farewell and the moat play no scene animation on the prop). **Derived, not hard-coded:** the nodes are each `EventPlayAS` `ASName` the prop's flow plays on it (`event_models.scene_actions`, `plan_scene_actions`), only for props of checks that give a song in this seed; the set is data, `scene_as` per prop in `event_props.toml` (the one of the event's `ExtraResources.EventAS` sets whose ASB holds the nodes; a name rule does not fit: `Dm_Goron_0030_Gauntlet_Goron` for `Item_Gauntlet_Goron`, and a node such as `C02` is in several of an event's sets). Choices (Claude, to confirm): one set per seed for every song event user, as the pilot (not per song); `scene_as` also on Zelda's Letter and the three stones (dump-checked, not played; the stones' slots hold only rewards today); case-insensitive sort (961 of 962 native ASCII slots; byte order gives the same order for these names); native rows keep their name offsets. The songs' own users get no triggers. Byte check: the code with the pilot's three actions rebuilds both pilots' tables byte for byte (R1 with the pilot's two passes); the A seeds' tables differ from the pilots' only by the actions their placements do not need (see Handoff). Test edits: none (new tests only; `tests/synthetic_effects.py` gained `ActionTable`). |
| 5.6 | BBender, 2026-11-25 | No made-up text and grammar does not matter: in each language only the words naming the vanilla item are replaced by the given item's name (`text.item_name`), even where the grammar around them is then wrong. A language whose line does not name the item in words the patch can find keeps its own line. This replaces the first answer (an English fallback line), which BBender withdrew the same day. |
| QA-Nothing | BBender, 2026-11-25 (Claude's recommendation) | Plan 6.2 and spec 5.2 ask for Nothing at an event, but `make_seed` places Nothing and other players' items only at chests (`patch/__init__.py` `custom_step`). Nothing is dropped from the QA seed and the pilot's played arms; the Nothing/foreign model choice (D4, Zelda's Letter donor) is checked by synthetic tests only. Custom items at gifts stay out of scope. |
| Q2 / D9 | BBender, 2026-11-25 | Saria's farewell fix (N9: the bridge Saria's own actor and schedule list) applies in **every seed**; after Gohma it behaves as the native Saria. The pilot code of the failed attempts (stow action, `WarpDone` flag toggle, hidden schedule copy, `make_seed(saria_stow=...)`) and the idle-motion switch (D16) are removed; the record keeps what each arm showed. |
| 12.1 dropped | BBender, 2026-11-25 | No Saria matrix on Longshot 3.0.0: the version was not the cause (the glitch is the shared schedule's `Hold` on the bridge Saria, fixed by her own actor). D11's 3.0.0 axis is withdrawn. |
| Q3 | BBender, 2026-11-25 | NPC lines in scope (D8): only group A of the inventory (25 prize and hand-over lines); groups B, C and D (63 lines) are deferred to a follow-up spec. |

## Test edits

Every change to an existing test is listed here with its reason.

- `tests/test_gifts_dump.py` (Claude, 2026-11-25, plan task 5): `_intended` also allows the events in a rule's
  `display` list to change, since the text fix rewrites them on purpose; `test_dump_every_step_gives_the_new_item...`
  also checks that each display names the new item (plan 5.7). No assertion was loosened otherwise.
- `src/clawshot/patch/event_props.toml` (Claude, 2026-11-26): `Dm_MelodyGet_Time/flowchart/Dm_Item_Ocarina_Time` moved
  from the props (HF Ocarina of Time Item) to the `played` exclusions after run E10.
- Full dump suite (Claude, 2026-11-26, first full run on this branch): 12 failures, all from the branch's every-seed
  steps (Saria's own actor, task 13) and the event containers (setting on by default), none from a wrong patch.
  Edited, each kept as strict as before for everything else:
  - `tests/test_event_registration.py`: `saria_farewell` (every recipe) and `event_models` (opt-in, covered by
    `broad`) added to the flow writer register; `written_world` skips timeline-only flows (Saria presenting,
    Zelda's throw), which no seed wrote before. The registration checks themselves passed unchanged.
  - `tests/test_getitem_ocarina_dump.py`: both steps added to `ROW_STEPS` (the test applies their transforms to the
    expected table, so their rows are still checked).
  - `tests/test_seed_dump.py`: the Saria fix's one field in `KokiriForest_Child_Static` expected beside the chest
    changes; size entries predicted as the writer gives them (a placed object's own model member and a sized-like
    file: donor entry plus growth; a new pack's members: declared donors, copies, else the formula with own
    component counts); a loose new file read uncompressed; the planned file list deduplicated (a chest file a step
    also edits).
  - `tests/test_shops_dump.py`, `tests/test_settings_prices_dump.py`: a sized-like new file's entry is its donor's
    plus growth (no size formula for a schedule list).
  - `tests/test_tokens_dump.py`: "no token output" asks whether the token step edits GameActorInfo (other steps now
    do); the token pickup comparison leaves out Saria's actor and the event containers; their rows and the placed
    objects' own rows are expected by name; a loose sized-like new file read uncompressed.
- `tests/test_key_bindings.py` (Claude, 2026-11-26): `test_public_seed_preserves_named_key_credit_and_first_weapon_bag`
  builds a seed on an invented romfs without Saria's pack; since the Saria fix runs in every seed (task 13) it
  failed reading that pack. The test now stubs `saria_farewell.changes`, as it already stubs the ocarina get model;
  `test_saria_farewell*` cover the fix. Found by the full synthetic run (4822 passed, these 2 failed).
- `tests/test_event_models_dump.py` (Claude, 2026-11-26, plan 10b): the moat test picks the moat by its check, not
  as the first placed object, since Ruto's stone is a second one. `tests/test_event_props_dump.py`: the placement
  test expects both placed objects (moat, Ruto's stone).
- D16b/D17 (Claude, 2026-11-26): `tests/test_containers.py`
  `test_a_container_has_no_pouch_pickup_ai_get_pose_or_item_animation_set` asserted the D16 dummy set and no
  `ASInfoRef`; now `test_a_container_has_no_pouch_pickup_ai_or_item_identity` (the rest kept) plus new tests for the
  model's set and the dummy case. `tests/test_event_models.py`: the song test expected the shared ocarina container,
  now the song's own; the every-item test resolves through `containers.container_model`.
  `tests/test_containers_dump.py`: models through `container_model`; a song container's copies are compared with the
  song pack as the song step writes it (its effect members are new there), every other copy still with the dump.
- D19 (Claude, 2026-11-26): `tests/test_event_models.py`
  `test_a_moved_check_plans_its_hand_bind_and_the_container_and_a_vanilla_one_none`: `plan_hands` takes the ActorInfo
  rows now; the test passes synthetic rows and expects the hand bind with its shift (it expected the zero-shift bind).
- D20 (Claude, 2026-11-27): no existing test changed. `tests/synthetic_effects.py` (shared helper) gained
  `ActionTable`, `HEART_ACTIONS`, `HEART_ACTION_USERS` and `user()` accepts an `ActionTable`; the tables it built
  before are byte-identical (opaque trigger bytes, zero counts).
- `tests/test_event_lines.py` (Claude, 2026-11-25, plan 5.8): the data test expects 25 lines instead of 24 and that
  Queen Gohma's Key Items caption is among them (decision Q5).
- `tests/test_event_lines.py` (Claude, 2026-11-27, decision Q8): the data test
  `test_the_data_holds_the_group_a_lines_gohmas_key_items_caption_and_rutos_line` expects 50 lines instead of 26 (the
  24 Q8 lines); new tests check the Q8 lines and those left out, the word-end match, and a plain-kind second name.

## Inventories

### Display-only get windows and Zelda's Notes targets (plan task 2)

Claude, 2026-11-25, dump 1.1.1, `clawshot.census.event_items.scan_displays`: 81 flows have a gift step; in them, 2
literal `GetPouchContent:DisplayGetByActorName` windows and 11 literal Notes `TargetID`s. Each is assigned in the data
(`display` in `gift_rules.toml`, or a reward slot's `notes` in `data/dungeon_rewards.toml`);
`tests/test_census_event_items_dump.py` fails on a new unassigned one or a stale assignment. Outside gift flows (not
listed, no check): `Dm_TimeTemple_0030/Event117` window and `Event209` Notes (Master Sword),
`Dm_InsideJabu_Jabu_0030/Event252` Notes (`Item_Stone_Water_Ruto`, Ruto's held stone).

| Flow/event | Kind | Check | Native name | Grant's vanilla item |
|---|---|---|---|---|
| `Dm_Kokiri_0155/Event77` | window | LW Gift from Saria | `Item_Ocarina_Fairy` | `Item_Ocarina_Fairy` (`Event68`) |
| `Dm_Kokiri_0155/Event58` | Notes | LW Gift from Saria | `Item_Ocarina_Fairy` | `Item_Ocarina_Fairy` (`Event68`) |
| `Dm_MelodyGet_Time/Event229` | window | HF Ocarina of Time Item | `Item_Ocarina_Time` | `Item_Ocarina_Time` (`Event70`) |
| `Dm_MelodyGet_Time/Event280` | Notes | HF Ocarina of Time Item | `Item_Ocarina_Time` | `Item_Ocarina_Time` (`Event70`) |
| `Dm_SageRoom_0005/Event432` | Notes | ToT Reward from Rauru | `Item_Medal_Light` | `Item_Medal_Light` |
| `Dm_Kokiri_0130/Event109` | Notes | Queen Gohma | `Item_Stone_Forest` | `Item_Stone_Forest` |
| `Dm_DeathMtTrail_0025/Event205` | Notes | King Dodongo | `Item_Stone_Fire` | `Item_Stone_Fire` |
| `Dm_ZoraFountain_0030/Event159` | Notes | Barinade | `Item_Stone_Water` | `Item_Stone_Water` |
| `Dm_Awake_Forest_Get/Event46` | Notes | Phantom Ganon | `Item_Medal_Forest` | `Item_Medal_Forest` |
| `Dm_Awake_Fire_Get/Event46` | Notes | Volvagia | `Item_Medal_Fire` | `Item_Medal_Fire` |
| `Dm_Awake_Water_Get/Event45` | Notes | Morpha | `Item_Medal_Water` | `Item_Medal_Water` |
| `Dm_Awake_Shadow_Get/Event46` | Notes | Bongo Bongo | `Item_Medal_Shadow` | `Item_Medal_Shadow` |
| `Dm_Awake_Spirit_Get/Event47` | Notes | Twinrova | `Item_Medal_Spirit` | `Item_Medal_Spirit` |

The nine reward Notes are already rewritten by `patch/rewards.py` with dungeon reward shuffle on. Dm_MelodyGet_Time
also holds the Song of Time grant (`Event4`, check Song from Time); its window and Notes name the ocarina, so they
belong to HF Ocarina of Time Item.

- `tests/test_event_lines.py` (Claude, 2026-11-27, hand-read marks): rewritten. The matcher it tested
  (`substitute`, `_find`, `edit_line` with name forms, `check_english`, second names, the data's 50 lines) is gone;
  the new tests build synthetic lines and marks (raw text and fingerprint, span to raw position, plain and
  highlighted marks, a declined-forms tag with its gender tag, several marks, overlap refused, a mark in another
  label per language, fingerprint mismatch refused, determinism, shared marks of two checks, the data format, and
  the data file holding positions only for known checks).
- `tests/test_event_lines_dump.py` (Claude, 2026-11-27, hand-read marks): rewritten for the marks: every mark
  resolves, its fingerprint matches and its slice is not empty; with every check moved each marked line-language
  becomes the raw text with the given name in the marks' places, unmarked ones and other files stay. The old test
  (each line names the given item or stays native, English always changes) asked what the matcher found.

### NPC lines naming the vanilla item (plan task 3)

Claude, 2026-11-25, dump 1.1.1, script `C:/Users/bened/ootr/work/event-items/tools/scan_npc_lines.py` (output kept
there, not committed). Scope: every message (`MessageId` parameter) in the flow of each gift check's census step and
of each dungeon reward slot (92 check/flow pairs), matched against the vanilla item's English name (USen
`PouchContent` `<key>_Name`). **88 lines name it in full**; every one exists in all 16 languages. A further 163 lines
match only the name's last word (the last word of Ocarina of Time, of the bomb bags); read through, they are noise
or name the item generically, not by its name, and are not listed. No line in Saria's farewell names the Fairy Ocarina.

Groups (Claude's reading): **A** the NPC announces or hands over the prize; **B** the line talks about the item
outside the hand-over (explanations, reminders); **C** a trade-quest story line (the item is part of the quest
chain); **D** a song lesson naming the song Link is taught to play.

**Text fix as built (plan task 5, Claude, 2026-11-25).** Data: `src/clawshot/patch/event_lines.toml`, **24 lines**
in 23 messages, plus Queen Gohma's Key Items caption since E2 (Q5, plan 5.8: 25 lines in 24 messages): `MiniGame_FrogTenors` Talk_19 describes the bug-catching game, so it is ZR Frogs Ocarina Game's line
only (the inventory listed it under ZR Frogs in the Rain too, whose steps share the flow); Gerudo Talk_16 names two
checks' items. How a line's words naming the item are found, in this order:

1. the name as the item stores it, grammar tags included (German Rolling Goron line: the game declines it at run
   time, so the given item's tags decline too);
2. the name as text, case-insensitive, any whitespace matching a space (German Bombchu Bowling line, a line break
   inside the name), and any declined form of a name stored only as a grammar tag (Polish, some German);
3. every word of the name by its stem with an ending of up to five letters, umlauts folded (German and Russian
   quiver lines, which decline the Bigger Quiver's name). The words found are replaced; grammar around them is
   not fixed (decision 5.6).

A line naming two items swaps those it finds. The share quoted with the first 5.6 question (about 80%) was too high: it
counted tag-only names as found. With every check moved (`tests/test_event_lines_dump.py`), messages of 23 left native
per language: USen, EUen, EUde, EUfr, USfr, EUnl 0; EUru 2; EUes, USes, KRko, EUpl 3; CNzh, TWzh, JPja, EUit, USpt 4.
Almost all are the tier lines (Bigger Quiver, Bigger Deku-Seed Bag: Talk_04, Talk_17), which those languages word
with another comparative; also the frogs' Talk_19 in Chinese and Japanese, Biggoron's Talk_11 in Italian and
Portuguese, and Talon's Talk_57 in Polish.

**Decision Q3 (BBender, 2026-11-25):** group **A** (25 prize and hand-over lines) stays in scope; groups **B** (17),
**C** (30) and **D** (16) are deferred to a follow-up spec, with BBender's OK. Claude's caveat given with the
question: the name inside a line is often lowercase or inflected, so each kept line needs a per-language edit.

Groups: A prize/hand-over 25, B about the item 17, C trade story 30, D song lesson 16. Only group A is listed
(identifiers only, no game text: AGENTS.md rule 1); `tools/scan_npc_lines.py` lists all four groups again for the
follow-up spec.

| Group | Check | Flow messages | Label | Vanilla item |
|---|---|---|---|---|
| A prize/hand-over | DMT Biggoron | `EventFlowMsg/Npc_Goron_Biggoron_Adult` | `Talk_11` | Biggoron Sword |
| A prize/hand-over | GC Rolling Goron as Adult | `EventFlowMsg/SageOfFire` | `Talk_0028_2` | Goron Tunic |
| A prize/hand-over | GF HBA 1000 Points | `EventFlowMsg/Npc_Gerudo_008` | `Talk_16` | Piece of Heart |
| A prize/hand-over | GF HBA 1500 Points | `EventFlowMsg/Npc_Gerudo_008` | `Talk_16` | Bigger Quiver |
| A prize/hand-over | GF HBA 1500 Points | `EventFlowMsg/Npc_Gerudo_008` | `Talk_17` | Bigger Quiver |
| A prize/hand-over | KF Shopkeeper Gift | `EventFlowMsg/Npc_Kokiri_001_Shop_Child` | `Talk_0102` | Deku Shield |
| A prize/hand-over | Kak Anju as Child | `EventFlowMsg/Npc_Hylia_049_Child` | `Talk_07` | Empty Bottle |
| A prize/hand-over | Kak Anju as Child | `EventFlowMsg/Npc_Hylia_049_Child` | `Talk_12` | Empty Bottle |
| A prize/hand-over | Kak Anju as Child | `EventFlowMsg/Npc_Hylia_049_Child` | `Talk_21` | Empty Bottle |
| A prize/hand-over | Kak Shooting Gallery Reward | `EventFlowMsg/Npc_Hylia_019_Shop_Adult` | `Talk_04` | Bigger Quiver |
| A prize/hand-over | LLR Talons Chickens | `EventFlowMsg/Npc_Hylia_Talon_Child` | `Talk_09_2` | Lon Lon Milk |
| A prize/hand-over | LLR Talons Chickens | `EventFlowMsg/Npc_Hylia_Talon_Child` | `Talk_11` | Lon Lon Milk |
| A prize/hand-over | LLR Talons Chickens | `EventFlowMsg/Npc_Hylia_Talon_Child` | `Talk_29` | Lon Lon Milk |
| A prize/hand-over | LLR Talons Chickens | `EventFlowMsg/Npc_Hylia_Talon_Child` | `Talk_56` | Lon Lon Milk |
| A prize/hand-over | LLR Talons Chickens | `EventFlowMsg/Npc_Hylia_Talon_Child` | `Talk_57` | Lon Lon Milk |
| A prize/hand-over | Market Bombchu Bowling First Prize | `EventFlowMsg/Npc_Hylia_067_Shop_Child` | `Talk_06` | Bigger Bomb Bag |
| A prize/hand-over | Market Bombchu Bowling First Prize | `EventFlowMsg/Npc_Hylia_067_Shop_Child` | `Talk_22` | Biggest Bomb Bag |
| A prize/hand-over | Market Bombchu Bowling Second Prize | `EventFlowMsg/Npc_Hylia_067_Shop_Child` | `Talk_05` | Piece of Heart |
| A prize/hand-over | Market Bombchu Bowling Second Prize | `EventFlowMsg/Npc_Hylia_067_Shop_Child` | `Talk_30` | Piece of Heart |
| A prize/hand-over | Market Bombchu Bowling Second Prize | `EventFlowMsg/Npc_Hylia_067_Shop_Child` | `Talk_72` | Piece of Heart |
| A prize/hand-over | Market Potion Shop Bottle | `EventFlowMsg/Npc_Hylia_020_Shop_Child` | `Talk_110` | Empty Bottle |
| A prize/hand-over | Market Shooting Gallery Reward | `EventFlowMsg/Npc_Hylia_019_Shop_Child` | `Talk_04` | Bigger Deku-Seed Bag |
| A prize/hand-over | Queen Gohma | `EventFlowMsg/Dm_Kokiri_0130` | `Dm_Kokiri_0130_0004` | Kokiri Emerald |
| A prize/hand-over | ZR Frogs Ocarina Game | `EventFlowMsg/MiniGame_FrogTenors` | `Talk_19` | Piece of Heart |
| A prize/hand-over | ZR Frogs in the Rain | `EventFlowMsg/MiniGame_FrogTenors` | `Talk_19` | Piece of Heart |

#### Wider scan (Claude, 2026-11-27, BBender's question about the Market shooting gallery)

`C:/Users/bened/ootr/work/event-items/tools/scan_item_lines_wide.py` (output `item_lines_wide.tsv` there): every
flow-based check (`locations.toml` kinds `event_gift`, `song`, `npc_gift`), every line of every message file the
check's flow uses (not only the lines the flow shows), and a core-name match (size words, counts and hyphens
ignored: "Biggest Deku-Seed Bag" -> "deku seed bag"). 158 lines; 89 were already in the list above, **69 are new**. The
gallery's promise (`Npc_Hylia_019_Shop_Child` `Talk_04`, "a bigger Deku-seed bag") was already in group A and is
rewritten (`patch/event_lines.toml`); it is not in the QA event list (`qa/events.md` covers cutscene events) and has
not been played. New prize/promise lines (A-like, not decided): GF HBA 1500 `Npc_Gerudo_008:Talk_07_3` ("a larger
quiver"), galleries `Talk_05`/`Talk_23` ("a new quiver"/"a new Deku-seed bag"), Bombchu Bowling `Talk_31`, `Talk_74`
("bomb bag prize"), `Talk_37` (Bombchus prize), `Talk_12` (red rupee prize), Wasteland Bombchu Salesman `Talk_03`,
Sun's Song lesson `Dm_MelodyGet_Sun_0014`, the Magic Bean Salesman's sale offers (about 22 lines). The rest are B/C
(Medigoron's knife, the Mask of Truth, shop policy lines, Cojiro, Lon Lon Milk, Eyeball Frog, Scarecrow Song).
Not covered by any scan: checks without a flow (chests, shop slots, scrubs, the treasure game reward).

**Decision Q8 (BBender, 2026-11-27):** a line is rewritten only where it names the item as what is given or as the
prize; lines that describe or comment on the original item stay (confirms Q3's group A boundary for the new lines).
Lines from the wider scan to add by that rule (Claude's reading; the two borderline ones decided by BBender,
2026-11-27): GF HBA `Talk_07_3`, the galleries' `Talk_05` (Kak) / `Talk_23` (Market), Bombchu Bowling `Talk_31`,
`Talk_74`, `Talk_37`, `Talk_12`, Wasteland Bombchu Salesman `Talk_03`, the Magic Bean Salesman's sale offers, and the
Sun's Song lesson `Dm_MelodyGet_Sun_0014` (said as the song is taught: change). Kept: the Rolling Goron's `Talk_05`
(names the bomb bag Link must own first, not the prize).

**Q8 code (uncommitted; Claude, 2026-11-27, dump 1.1.1).** `patch/event_lines.toml` has 24 new lines (50 in all):
GF HBA 1500 `Npc_Gerudo_008:Talk_07_3`, Kak gallery `Npc_Hylia_019_Shop_Adult:Talk_05`, Market gallery
`Npc_Hylia_019_Shop_Child:Talk_23`, Bombchu Bowling First Prize `Talk_31`, `Talk_74`, Bombchu Bowling Bombchus
`Talk_37`, Wasteland Bombchu Salesman `Npc_Hylia_044_Adult:Talk_03`, Sun's Song `Dm_MelodyGet_Sun_0014`, and 16 of
the Magic Bean Salesman's sale offers (`Npc_Hylia_047_Child` `Talk_00`, `Talk_00_02_01`, `Talk_00_03_01`,
`Talk_00_04_01`, `Talk_04` to `Talk_09` each with its `_02`; every one names the beans as on offer in English).
- **Vanilla item per line:** a check with two tiers names the tier its other lines use, the Medium one
  (`Item_Quiver_Medium` for GF HBA 1500 and the Kak gallery, `Item_BulletBag_Medium`, `Item_BombBag_Medium`), as the
  galleries' `Talk_04`; `Item_BombchuBundle_Medium` (Bowling Bombchus), `Shop_BombchuBundle_01` (Wasteland),
  `Item_MagicBean`, `Item_Melody_SunSong`.
- **Plain-kind names:** the lines that name the item by its kind ("a new quiver", "the bomb bag", "Bombchus") get the
  existing `name` field pointed at the smallest tier's own name in `ActorMsg/PouchContent.msbt`
  (`Item_Quiver_Small_Name`, `Item_BulletBag_Small_Name`, `Item_BombBag_Small_Name`, `Item_Bombchu_Name`): each
  language's own word, nothing made up, no code change for it.
- **Matcher change (Claude):** a name found as text now runs on to the end of its word by up to five cased letters
  (`event_lines._find`), so a plural ending is not left behind ("Krabbelmine|n" gave "Bumerangn", "Bombchu|s" gave
  "Boomerangs"); never in CJK or Hangul, and not when the word is longer. With every check moved, the 26 earlier
  lines' output over the dump is unchanged; only `Talk_37` and `Talk_03` change (EUde, EUen, USen, EUes, USes, USpt).
- **Left out:** `Talk_12` (the red rupee prize): `MiniGame_BombchuBowling Event81` is a census location with no check
  (no OoT Randomizer name, no gift rule). The bean salesman's `0000` and stock comments (`Talk_101`, `Talk_103`,
  `Talk_105`, `Talk_107`, `Talk_13`, `Talk_14`, `Talk_17`) and the Rolling Goron's `Talk_05`, by Q8.
- **Inert for now:** Bowling Bombchus and the Magic Bean Salesman are gift_rules class `more` (not shuffled); their
  lines change only once those checks can move.
- **Languages left native** (with every check moved, given Boomerang): the 8 single lines are found in all 16
  languages. Bean offers: `Talk_00_02_01`, `Talk_05_02` EUfr, USfr; `Talk_08_02` EUfr, USfr, EUru; `Talk_09_02` EUru;
  `Talk_06_02` EUpl; `Talk_07_02` EUit (those lines say "them", "one bean" or "haricots" without the item's name); the
  other 10 offers are found in all 16. Grammar around the words is not fixed (5.6): e.g. EUfr "un plus Boomerang",
  KRko particles.

#### Hand-read marks (2026-11-27)

BBender's goal (2026-11-27): every text that names a given item as what is given, sold, the prize or handed over has
those words cut out and the randomized item's name put in (always the same form, no grammar fix; plural and compound
words cut whole; short or stylised names count). Read by 18 agents in parallel, one per group of dialog files, each
reading English first and then all 16 languages (`C:/Users/bened/ootr/work/event-items/lines/TASK.md`); where a
language uses a pronoun, the mark goes to the earlier box of that exchange that names the item (BBender's rule).
Result `lines/merged.tsv`: 157 lines from 62 checks (97 clear, 60 doubtful), 2489 spans, 60 marks moved to an earlier
box, 38 rows where a language names the item nowhere; every span checked to occur in its line. Grammar-tag words
(201/10) count as text (five German lines first missed by the reading helper, fixed). Storage (Claude's choice B):
the repository gets position, length and a fingerprint of each line, no game text.

Decisions on the doubtful groups (BBender, 2026-11-27; letters as in `lines/questions.md` review):
- A (described, not named: "heart-shaped prize", "something golden", "a special song", "this song", "key
  ingredient", "shiny rock", "spending money", "a new power", "masterworks"): replace where it is the prize at the
  moment of giving.
- B (rupees by amount: "20 rupees", "50 rupees", "five rupees", "good rupees"): replace.
- C (right after the hand-over, reminding or explaining: Nayru's Love, Pierre, the Gerudo pass, the prescription, the
  second potion-shop bottle line): keep (Q8); except the song lessons' closing lines (Requiem, Nocturne), replaced
  like "Keep the Sun's Song in your heart".
- E (a translation names the item where English uses a pronoun: Silver Scale EUit/USpt, soldier's rupees EUnl, King
  Zora's ingredient EUde/EUnl, bean price boxes, running man): replace there too (to be marked).
- F (Link's own choice answers "Magic beans?", "I'll buy some beans!"): replace.
- G (Din's Great Fairy names what her sisters give): keep for now. BBender's idea: a later option for players who
  want such hints, like the Gold Skulltula reward hints.
- H (Queen Gohma "this Spiritual Stone— the Kokiri Emerald"): replace only the item's own name.
- I (descriptors around the name: "state-of-the-art bombs called Bombchus", "holds 40 bombs"): leave as marked.
- D (re-offers, refusals, repeat sales: odd mushroom and eyeball frog re-offers, Kokiri replacement shield, Zora Tunic
  "one per customer", Medigoron after the knife breaks, eye drops after they spoil): left as they are; to be
  considered when such checks become randomizable.
- J (BBender, final run 2026-11-28, F18): a line that strengthens what Link already has (the castle fairy's spin
  attack line) is not a gift: its mark is dropped (`Dm_FairyFountain_Power_0004`, all languages).
- K (BBender, final run 2026-11-28, F19, F25): the Great Fairies' explanation lines that name the spell just given
  are replaced (overrides Q8 and C for them): Din's Fire `Dm_FairyFountain_Din_0006_01`, Farore's Wind
  `Dm_FairyFountain_Frore_0004_01` (same rule, Claude), Nayru's Love `Dm_FairyFountain_Nayru_0004`; read in all 16
  languages by Claude (`lines/extra.tsv`, group Y). Unchanged: the courage and wisdom fairies' lines that describe the
  effect (no item noun to swap, like J); the wisdom fairy's "a new power" stays marked (A). 166 lines.

**Marks code (uncommitted; Claude, 2026-11-27, dump 1.1.1).** The name matcher is gone from the patch path; the
hand-read marks are the truth.
- **Data:** `src/clawshot/patch/event_marks.toml`, one `[[line]]` per (check, file, label): `check`, `item` (vanilla
  actor(s), `|` between a progressive pair; a record), `file`, `label`, and per language
  `marks.<lang> = { fingerprint, at = [[start, length], ...] }`. Positions are code points in the line's raw text
  (`event_lines.raw_text`: text parts as they are, a declined-forms tag 201/10 as its first form, other tags left
  out; Claude's choice: a tag word counts as its form's length, so the fingerprint covers it); the fingerprint is the
  first 16 hex digits of the sha256 of that raw text. No span text in the repository (a synthetic test checks every
  data line is a name, a hex fingerprint or numbers). 164 lines (157 messages), 2327 line-languages, 2349 marks; the
  sheets' 60 COVERED BY and 42 NOT NAMED rows give no marks.
- **Converter:** `tools/event_marks/convert.py` (`uv run python -m tools.event_marks.convert ROMFS final.tsv
  extra.tsv`): reads the sheets (outside the repository), maps each sheet check to a placement key, finds each span's
  n-th place in the collapsed text and maps it back to raw positions (`event_lines.collapse`, `locate`), refuses
  unmapped rows, spans not found and overlapping marks, and writes the file sorted (byte-identical on a rerun).
- **Check mapping:** OoT Randomizer names are `gift_rules.toml` checks or reward slots as they are; `<check> = <tier>`
  is the check; `a | b` and `<flow> EventA / EventB (<actor>)` are two checks (the frogs' blue rupees: Event162 and
  Event76, the same words marked for both, filled once with the first moved check's item); a census `name` maps to
  its `oot_randomizer_name`, or stays when it has none. Every row maps. Lines whose check can move today: 89
  (swap 49, rewrite 37, reward slots Queen Gohma 2 and Barinade 1); waiting: 75 (gift class `more`: Magic Bean
  Salesman 34, King Zora's prescription 5, Eyeball Frog 3, Bowling Bombchus 3; census names without an OoT
  Randomizer name: 30, the rupee prizes, the bottle shop's gold rupee, the Mask of Truth sale).
- **Patch:** `event_lines.load`, `moved_lines` (message -> (line, given actor)), `changes` (one transform per
  language with marks), `archive_transform(language, swaps)`, `edit_line` (fingerprint check: a mismatch is a
  `PatchError` naming file, label and language), `apply_marks` (right to left; a text part loses the marked
  characters, a declined-forms tag touched by a mark goes whole; 201/0 gender tags right before such a tag or right
  before a mark that starts a text part go too, the given name brings its own, as the old run replacement did;
  other tags stay and the given name takes the mark's last place, inside a highlight). Given name:
  `text.item_name` of the given actor's text key, unchanged.
- **Old entries:** of `event_lines.toml`'s 50 lines, 47 are in the reading; one is dropped: KF Shopkeeper Gift
  `Npc_Kokiri_001_Shop_Child:Talk_0102`, which the reading places under the replacement-shield events (Event116/117,
  decision D: re-offers stay). Two in-scope lines are outside the reading (not C/D/G) and are **kept** (Claude, to
  confirm): Queen Gohma's Key Items caption `LayoutMsg/ImportantMenu_01:T_Message_00` (Q5) and Ruto's line
  `Dm_InsideJabu_Jabu_0030_0019` (plan 10b). Their spans are what the old matcher cut, written as a sheet
  `lines/extra.tsv` (outside the repository, final.tsv unchanged); Ruto's line names the stone in CNzh, JPja,
  KRko, TWzh in no words the matcher found (NOT NAMED there, as before). Lines that now change in more languages
  than with the matcher: the tier lines and others the matcher missed; three bean offers keep French/Russian lines,
  as before.
- **Removed:** `substitute`, `_find`, `_replace_run`, the markers, `check_english` (replaced by the fingerprints),
  second names (`name` field), `Line.item` as a search key.
- **Preview:** `C:/Users/bened/ootr/work/event-items/lines/preview.md`, made through `event_lines.changes` with every
  check moved and the Boomerang given: per message, per language before (`[[cut]]`) and after
  (`[[cut→Boomerang's name]]`), checked equal to the patch output; 2215 of 2512 message-languages change.
- **Self-check** (scratch script, read-only on the dump): every mark's fingerprint matches, every slice is not empty
  and equals its sheet span, overlapping and plain occurrence counting agree, the patched raw text is the expected
  one, no other file changes, two runs give the same bytes: 0 problems.

### Event props (plan task 4)

Claude, 2026-11-25, dump 1.1.1. Census rule (`clawshot.census.event_items.scan_prop_actors`): every actor named
`Dm_Item_*`, `Item_*` or `Weapon_Sword_*` that an event flowchart or timeline binds, animates or brings on stage
(`EventTriggerModelBind`, `EventModelBind`, `EventPlayAS`, `EventPlayASForTimeline`,
`EventPlayASAndModelBindForTimeline`, `EventTriggerParticipateEvent`, `EventTriggerSetModelLodManual`): 56 actors.
Data: `src/clawshot/patch/event_props.toml`, 21 props (18 flowchart actors, 2 timeline actors, 1 placed object; LW Target's
two bags as one entry per branch, D13) and three named exclusions; `tests/test_event_props_dump.py` fails on a new,
missing or stale entry and checks each prop's check, vanilla item, branch grant and the moat's Hash.

| Stable ID | Mechanism | Check | Vanilla item | Branch grant | EventSetting resources naming the prop (4.5) |
|---|---|---|---|---|---|
| `Dm_Kokiri_0155/flowchart/Item_Ocarina_Fairy` | flowchart | LW Gift from Saria | `Item_Ocarina_Fairy` |  | - |
| `Dm_LostWood_0040/flowchart/Item_BulletBag_Large@LostWood` | flowchart | LW Target in Woods | `Item_BulletBag_Large` | `Dm_LostWood_0040/Event17` | anim Dm_LostWood_0040_Item_BulletBag_Large; AS Dm_LostWood_0040_Item_BulletBag_Large.root.as |
| `Dm_LostWood_0040/flowchart/Item_BulletBag_Medium@LostWood` | flowchart | LW Target in Woods | `Item_BulletBag_Medium` | `Dm_LostWood_0040/Event30` | anim Dm_LostWood_0040_Item_BulletBag_Medium; AS Dm_LostWood_0040_Item_BulletBag_Medium.root.as |
| `Dm_Goron_0030/flowchart/Item_Gauntlet_Goron` | flowchart | GC Darunias Joy | `Item_Gauntlet_Goron` |  | anim Dm_Goron_0030_Item_Gauntlet_Goron; AS Dm_Goron_0030_Gauntlet_Goron.root.as |
| `Dm_HrlCastle_0050/flowchart/Item_ZeldaLetter` | flowchart | HC Zeldas Letter | `Item_ZeldaLetter` |  | anim Dm_HrlCastle_0050_Item_ZeldaLetter; AS Dm_HrlCastle_0050_Item_ZeldaLetter.root.as |
| `Dm_MelodyGet_Time/flowchart/Dm_Item_Ocarina_Time` | flowchart | HF Ocarina of Time Item | `Item_Ocarina_Time` |  | - |
| `Dm_TimeTemple_0130/flowchart/Item_Arrow_Light` | flowchart | ToT Light Arrows Cutscene | `Item_Arrow_Light` |  | - |
| `Dm_DeathMtTrail_0050/flowchart/Item_ClaimCheck@daigoron` | flowchart | DMT Trade Eyedrops | `Item_ClaimCheck` |  | - |
| `Npc_Goron_Biggoron_Adult/flowchart/Item_Sword_Biggoron` | flowchart | DMT Biggoron | `Item_Sword_Biggoron` |  | no EventSetting row (NPC flow) |
| `Dm_Kokiri_0130/flowchart/Item_Stone_Forest` | flowchart | Queen Gohma | `Item_Stone_Forest` |  | anim Dm_Kokiri_0130_Item_Stone_Forest; AS Dm_Kokiri_0130_Item_Stone_Forest.root.as |
| `Dm_DeathMtTrail_0025/flowchart/Item_Stone_Fire` | flowchart | King Dodongo | `Item_Stone_Fire` |  | anim Dm_DeathMtTrail_0025_Item_Stone_Fire; AS Dm_DeathMtTrail_0025_Item_Stone_Fire.root.as |
| `Dm_ZoraFountain_0030/flowchart/Item_Stone_Water` | flowchart | Barinade | `Item_Stone_Water` |  | anim Dm_ZoraFountain_0030_Item_Stone_Water; AS Dm_ZoraFountain_0030_Item_Stone_Water.root.as |
| `Dm_Awake_Forest_Get/flowchart/Item_Medal_Forest` | flowchart | Phantom Ganon | `Item_Medal_Forest` |  | - |
| `Dm_Awake_Fire_Get/flowchart/Item_Medal_Fire` | flowchart | Volvagia | `Item_Medal_Fire` |  | - |
| `Dm_Awake_Water_Get/flowchart/Item_Medal_Water` | flowchart | Morpha | `Item_Medal_Water` |  | - |
| `Dm_Awake_Shadow_Get/flowchart/Item_Medal_Shadow` | flowchart | Bongo Bongo | `Item_Medal_Shadow` |  | - |
| `Dm_Awake_Spirit_Get/flowchart/Item_Medal_Spirit` | flowchart | Twinrova | `Item_Medal_Spirit` |  | - |
| `Dm_SageRoom_0005/flowchart/Item_Medal_Light` | flowchart | ToT Reward from Rauru | `Item_Medal_Light` |  | - |
| `Dm_Kokiri_0150/timeline/Dm_Item_Ocarina_Fairy@0` | timeline | LW Gift from Saria | `Item_Ocarina_Fairy` |  | anim Dm_Kokiri_0150_Item_Ocarina_Fairy |
| `Dm_HrlField_0060/timeline/Dm_Item_Ocarina_Time@0` | timeline | HF Ocarina of Time Item | `Item_Ocarina_Time` |  | anim Dm_HrlField_0060_Item_Ocarina_Time |
| `Banc/HyruleField/HyruleField_Child_Static.bcett.byml.zs` Hash `2802436684568022035` | placement | HF Ocarina of Time Item | `Item_Ocarina_Time` |  | - |

Exclusions (spec 2.8):

- **played** (an instrument someone plays in the event, not the item given; it keeps its look (D3)): `Dm_Kokiri_0150/timeline/Dm_Item_Ocarina_Fairy_Saria@0`, `Dm_Kokiri_0155/flowchart/Dm_Item_Ocarina_Fairy_Saria@saria`, `Dm_MelodyGet_Fire/flowchart/Dm_Item_Sheik_Harp`, `Dm_MelodyGet_Forest/flowchart/Dm_Item_Sheik_Harp`, `Dm_MelodyGet_Shadow/flowchart/Dm_Item_Sheik_Harp`, `Dm_MelodyGet_Shine/flowchart/Dm_Item_Sheik_Harp`, `Dm_MelodyGet_Spilit/flowchart/Dm_Item_Sheik_Harp`, `Dm_MelodyGet_Water/flowchart/Dm_Item_Sheik_Harp`, `Dm_MelodyGet_Fire/flowchart/Item_Ocarina_Time_Holder`, `Dm_MelodyGet_Forest/flowchart/Item_Ocarina_Time_Holder`, `Dm_MelodyGet_Shadow/flowchart/Item_Ocarina_Time_Holder`, `Dm_MelodyGet_Shine/flowchart/Item_Ocarina_Time_Holder`, `Dm_MelodyGet_Storm/flowchart/Item_Ocarina_Time_Holder`
- **hand_in** (an item Link already owns and shows, hands over or uses in the event, not the item the check gives): `Dm_DeathMtTrail_0050/flowchart/Item_EyeDrop@daigoron`, `Npc_Goron_Biggoron_Adult/flowchart/Item_Sword_BrokenGiant`, `Npc_Goron_Biggoron_Adult/flowchart/Item_Sword_Giant`, `Dm_Zora_0010/flowchart/Dm_Item_RutoLetter`, `Dm_Zora_0010/flowchart/Item_Bottle_Letter`, `Dm_Kakariko_0010/flowchart/Item_ZeldaLetter`, `Dm_HrlCastle_0020/flowchart/Item_AlarmCucco`, `Dm_SY_LetterBottle/flowchart/Dm_Item_RutoLetter`
- **not_check** (the event gives no check's item: story scenes, the ending, Sheik's knife, the six medallions together): `Dm_TimeTemple_0010`, `Dm_Kokiri_0030`, `Dm_FinalBattle_0010`, `Dm_WaterTemple_0000`, `Dm_InsideGanonCastle_0150`, `Dm_Ending_0000`, `Dm_FinalBattle_BossIn`, `Dm_FinalBattle_BossOut`, `Dm_InsideGanonCastle_0000`, `Dm_InsideGanonCastle_0110`, `Dm_InsideGanonCastle_BossOut`, `Dm_SageRoom_0000`, `Dm_Kakariko_0030`

Spec candidates confirmed without a prop: LW Trade Cojiro (`Item_CojiroCucco` only emits effects), Market Potion
Shop Bottle (`Weapon_Bottle` only leaves the stage), DMT Trade Broken Sword (the swords Link holds are hand-ins; the
Prescription is not shown). `Dm_InsideGanonCastle_0000` (spec list) shows all six medallions together and gives
nothing, so it is excluded, not a reward scene. `Dm_InsideJabu_Jabu_0030` (spec list) has no item actor the rule
finds; Barinade's stone is shown in `Dm_ZoraFountain_0030`.

**4.5, input for 7.6.** No `EventSetting` row lists the actors an event loads. A row lists per-actor resources
(`ExtraResources.EventModelAnimations`, `EventAS`), and the actor's own parameters (`UseEventModelAnime`,
`UseEventAS`) point at them. 11 props use none (the parameters' "not used" value); 9 use an animation project made for the vanilla
item's model (LW bags, Goron's Bracelet, Zelda's Letter, the three Spiritual Stones, both timeline ocarinas), and 7 of
those also an AS. A container in their place inherits those parameters: whether the item's event animation drives a
different model's skeleton is a pilot question (task 8), not something the static data answers. Biggoron's flow is an
NPC flow with no `EventSetting` row.

Not in scope by the rule, left for BBender: the boss heart containers shown in the `*_BossOut` timelines
(`Obj_Heart_Container`) and the Goron City pot's heart piece (`Dm_Goron_0045`, `Obj_Heart_Piece`) belong to BossHeart
and freestanding checks, not gift or reward events (D3), so they keep the vanilla model.

## QA seed and saves (plan task 6)

Claude, 2026-11-25. Tools outside the repository, `C:/Users/bened/ootr/work/event-items/`:
`tools/build_qa_seed.py` (settings of 6.1: Gift shuffle, dungeon reward shuffle, free time travel, Door of Time and
forest open, songs anywhere, every fast start, Saria's farewell plays, no full wallet; starts with the Fairy Ocarina
and the warp songs not placed at an event, `--no-ocarina` without), `tools/launch.sh` (Longshot 3.2.0 or 3.0.0,
`SAVE=`/`SLOT=`, closes a running Longshot, prints the seed's `mods:` lines), `qa/route.md`,
`saves/index.md`.

Forced placements, each event a different item (6.2): LW Gift from Saria Biggoron Sword; HF Ocarina of Time Item Piece
of Heart; LW Target in Woods Rupees (20); DMT Biggoron Bottle; ToT Light Arrows Cutscene Bolero of Fire (a song);
Kak Anju as Child Hylian Shield (equipment, and her prize lines); Queen Gohma Light Medallion and ToT Reward from Rauru
Kokiri Emerald (the stone/medallion swap); King Dodongo Goron Ruby (vanilla control). No Nothing (decision
QA-Nothing). GC Darunias Joy, HC Zeldas Letter and DMT Trade Eyedrops are kept vanilla in every seed by the gift spec
(`keep_vanilla`: not changeable yet, D31, R13), so their props never swap and they are not forced.

Base seed 7100 at the working tree on `ceab074`: built twice, 201 files byte-identical (6.3). The written
`Dm_Kokiri_0155` names `Item_Sword_Biggoron` in Event68, Event77 and Event58; `Dm_MelodyGet_Time` names
`Obj_Heart_Piece` in Event70, Event229 and Event280.

**Saves collected (plan 6.5, BBender played, Claude copied; 2026-11-25/26).** Decisions along the way (BBender): the
saves follow vanilla order; one walk-through on a seed whose events are all vanilla, randomized seeds are tested later
by loading the saves ("this run is only intended for me to create the saves"); helpers placed early to make the run
easier; the saves are kept agnostic, by place and progress, in a shared library
(`C:/Users/bened/ootr/work/saves/`, `index.md` there), not per event. Event list with the vanilla order BBender set:
`C:/Users/bened/ootr/work/event-items/qa/events.md` (40 events: every gift check whose step runs in a cutscene, the
two NPC events Anju and Biggoron, Malon's egg, Ruto's stone in Jabu-Jabu (Q6) and the Master Sword pull (Q7);
columns gives (vanilla), shows, text, in route, save).

Walk-through seed: `tools/build_walk_seed.py`, base 7100, built twice byte-identical (113 files). A purely vanilla
placement does not pass the beatability search in the remake: the Deku Tree's Slingshot room traps Link without an exit
tool, so the vanilla Slingshot is unreachable (`child_deku_tree.toml`, Kareem 2026-11-16), and the remake's key logic
refuses some N64 key positions. The script therefore starts from the real fill and swaps each chest toward its target
(vanilla pool item, plus the helpers) while the seed stays beatable, in passes until nothing changes: 2 chests left
off target. Helpers: Mido's chests Slingshot, Hylian Shield, Bomb Bag, Boomerang; Hyrule Field chests #1/#2 (adult)
Hookshot, Megaton Hammer; the pool's Strength copy from Mido moved to the Fire Temple so Link has no bracelet before
Darunia's Joy. Every event vanilla.

Result: 38 of 40 events have a save (`qa/events.md`, column save); the Eyedrops trade and Biggoron are skipped for now
(trade chain, BBender). Bosses are saved in front of the blue warp (loading puts Link there, BBender checked); Rauru has
no save of his own (none possible after the pull: the Temple of Time save covers him). Found on the way: Ruto's stone
scene plays from a noclip without Ruto's Letter; Darunia's line describes the bracelet without naming it (open
questions); a debug Bow comes without a quiver (arrows stay 0) until a quiver is added.

## Containers (plan task 7)

Claude, 2026-11-25, revised 2026-11-26 (D16b, D17, D18). `src/clawshot/patch/containers.py`: one actor
`Dm_Item_Clawshot_<model actor>` per model a seed needs (`containers.container_model`: a song is its own model, any
other item `getitem.model_actor`, D4).

- **Donor `Dm_Item_Ocarina_Fairy`** (Claude's choice): Saria's presented ocarina, a timeline prop with a dummy AS, the
  common event performer, an **empty** `ModelBindParam` (bind offsets come from each event's own bind action: D6).
- **From the model actor:** its resolved ModelInfo in a new member of its own (with `ModelVariationAnims`); its
  `AnimationRef` and `ELinkRef` when it has them; its animation set (`ASRef`, `ASInfoRef`, `XLinkRef`) unless that is
  `DemoDummy`/`Dummy` (D16b). A song's model pack is the song pack as the song step writes it (`songs.patch_song_pack`,
  D17), and its container names the song's event user `Clawshot_Song_<Song>_Event` through an ELink member of its own
  (D18). Rows: ActorInfo = the donor's with the model's visual fields, the larger heaps and radii and the effect user
  (a song's row via `songs.shown_row`); GameActorInfo = the donor's with the model's `ModelVariationAnims`. The
  ActorParam's size entry grows to what `rstb.required_size` needs.
- **Never:** `PouchContentRef`, `ActorNameRef`, `GameParameterTableRef`, `AIRef`, `CaptureRef`, `SLinkRef`; no
  `ActorName` in the row.
- Static checks (`tests/test_containers_dump.py`): every item model builds; every member other than the new ones is
  byte-identical to its native pack's (a song's, to the song pack as written); new paths have no native size entry.

## Pilot: containers on Saria's farewell (plan task 8)

Built (Claude, 2026-11-25): `event_models` renames a prop's actor-table entry to the container of the given item's
model; nothing else in the flow or timeline changes (`tests/test_event_models.py`, 8.1). Arms, each the QA seed with
Saria's gift forced and only `Dm_Kokiri_0150`/`Dm_Kokiri_0155` swapped, played by BBender on 2026-11-25 (Longshot
3.2.0, save `saves/before-farewell-ocarina-qa` slot 01: pre-Gohma, no Fairy Ocarina; `mods:` lines for both flows and
the container; no crash):

- **A Biggoron Sword:** presented and held, normal texture (D15's variation pairing holds), window "Biggoron Sword",
  one get. Saria's own ocarina still glitched: the pre-Gohma glitch (task 12), her prop was not swapped. 8.2, 8.3 pass.
- **B Piece of Heart:** still in both hands, one get, window right. BBender prefers the still look.
- **C Piece of Heart with the heart's animation set:** no spin either, no other difference: decision D16 (later
  revised, D16b). Arms D and E (rupee) were not played.

## Containers for every prop (plan task 9)

Claude, 2026-11-25. The pilot's step is general: `event_models.plan_renames` renames every flowchart and timeline prop
of a moved check (check -> the actor its grant gives) to the container of `getitem.model_actor` of that actor; the
placed moat object is left to task 10. `tests/test_event_models.py`: the composed gift patch and rename still grant the
real item (9.2); both LW Target branches show the item the check gives (9.3: gift grants are fixed when the seed is
generated, the same item for both branch grants); every item actor of the table resolves to its get-pose model's
container (9.4: gifts never hold progressive copies, the play note says only chests do); a stone scene, an awakening
scene and Rauru's show the reward placed there (9.5); one container serves several events (9.6).
`tests/test_event_models_dump.py`: with every check that has props moved, each of the 20 props in 19 event files names
its container and no other actor, event or clip changes (9.1); every reward slot has a scene prop (9.5).

## Moat placed object (plan task 10)

Claude, 2026-11-25, revised 2026-11-26 after the crash bisect. `src/clawshot/patch/placed_models.py`:
`Obj_Ocarina_Time_A_01` keeps its actor and pack (AI, glow, attention, physics); its `ModelInfoRef` points at a new
member of its own with the given item's model **only**: no `ModelVariationAnims`, no `AnimationRef` (a model's colour
variation on a placed object crashed the game on load, thread `GeneralFormatAsync_`; bisect arms none/noanim/norows,
BBender 2026-11-26). Rows take `MODEL_FIELDS` only and keep the object's own effect users and `AnimationResources`;
GameActorInfo carries no variation. The added member is sized from the pack's native ModelInfo entry plus its rounded
growth (`placed_models.added_member_sizes`). Zelda's thrown prop (`Dm_HrlField_0060`) and Link's look
(`Dm_MelodyGet_Time`, a hand bind) are ordinary props. Played: E10, `t14-moat3`, R1 `r1-moat` (sword, no crash), S2c.

## Ruto's stone in Jabu-Jabu (plan task 10b, decision Q6)

Claude, 2026-11-26, dump 1.1.1. The stone Ruto shows in `Dm_InsideJabu_Jabu_0030` is the placed object
`Obj_InsideJabu_Jabu_Stone_Water_A_01` (`Banc/InsideJabuJabuBelly/InsideJabuJabuBelly_Static.bcett.byml.zs`, Hash
`15570932853683785298`), one entry in `patch/event_props.toml` with check Barinade: the moat's mechanism (variant B)
needed no new code path, only `placed_models` resolving the model reference through `$parent`. The stone has no
`ModelInfoRef` of its own: it inherits the Temple of Time Spiritual Stone's (`Obj_TimeTemple_SpiritStone_A_03`, in its
pack); its own components now carry the reference to its own member, the parent's file is untouched. It animates
with the Key Items screen's assets (`ASRef` `Item_Medal_Light_ImportantMenu`, `AnimationRef`
`Item_Stone_Forest_ImportantMenu`), kept as they are: whether another reward's model spins right is for the played
check (10b.5). Dump test: all eight other rewards Barinade can hold fit.

Played (BBender, 2026-11-26, QA seed `ceab074` + working tree, Longshot 3.2.0, save
`child-jabu-jabu-before-big-octo-room`, run `runs/t14-ruto`; `mods:` `Pack/Actor/Obj_InsideJabu_Jabu_Stone_Water_A_01.pack.zs`):
Ruto's stone shows the Spirit Medallion, model correct; her line still named the Zora Sapphire
(`EventFlowMsg/Dm_InsideJabu_Jabu_0030` `Dm_InsideJabu_Jabu_0030_0019`). Decision (BBender, 2026-11-26):
rewrite it. The line names the stone by the quest log's name (`ChallengeMsg/Info_Get_StoneOfWater` `Name`), not the
item's, so a line may now point at such a second-name text (`name` in `event_lines.toml`), searched per language
besides the item's name. Dump test: rewritten in 12 of 16 languages; CNzh, TWzh, JPja, KRko word it differently and
keep their line (decision 5.6: no made-up text). Replayed (BBender, 2026-11-26, run `runs/t14-ruto2`, same save,
rebuilt QA seed; `mods:` `Pack/Actor/Obj_InsideJabu_Jabu_Stone_Water_A_01.pack.zs`, `Mals/USen.Product.110.sarc.zs`):
Spirit Medallion over Ruto, and her line names it. 10b.3 (the Notes target) is not built and cannot
be checked: Zelda's Notes go to the Nintendo Switch App, which Longshot does not connect to (BBender: "probably
ever"); `Item_Stone_Water_Ruto` stays vanilla. The other Notes rewrites (task 2) are likewise checked only statically.

## Setting `event_item_models` (plan task 11)

Claude, 2026-11-25. Catalog `data/settings.toml` (`true`, D7; Kareem to confirm in the PR, Q1), `Settings` field with a
Bool check, absent from `as_dict` when on so existing settings strings and logs keep their bytes; CLI
`--event-item-models`/`--no-event-item-models`; app entry "Show shuffled items in events" (group World) whose help says
what has been played; `docs/settings.md` "Items shown in events". `make_seed` runs the model step when the setting is
on (the pilot keyword `event_models` still limits it to named events). Tests: `tests/test_settings_event_items.py`
(default, string round-trip, refusal, CLI, app, doc: 11.1, 11.4); `tests/test_settings_event_items_dump.py`, forest
slice with Saria's gift moved: off writes no container and no renamed prop while Saria's window names the given item
(11.2, 5.5); on and off differ only in model files (the props' event files, ActorInfo, GameActorInfo, the size table,
container packs); on with every inventoried check vanilla writes byte-identically what off writes (11.3).

## Saria matrix (plan task 12)

Longshot 3.2.0 (BBender, 2026-11-25; the 3.0.0 axis was dropped, 12.1). Each cell: who played, build, save, result.

| Cell | Save | Build | Gift | Stow | Result |
|---|---|---|---|---|---|
| pilot A | pre-Gohma, no Fairy Ocarina (`saves/before-farewell-ocarina-qa` slot 01) | `ceab074` + tree, QA seed 7100, models on, PR #40 prop row | Biggoron Sword | none | glitched (BBender) |
| no-mod control | same | no mod (`mods: ... 0 RomFS entries`) | Fairy Ocarina (native) | none | glitched (BBender, screenshots) |
| N0 | same | `ceab074` + tree, QA seed 7100 without starting ocarina, models on, prop row | Fairy Ocarina (native) | none | glitched, as the no-mod control: double at the timeline's start, mirrored after the get (BBender) |
| N1 | same | N0 + hand-over stow (derived, `tools/derive_stow.py`); log: `mods:` `Dm_Kokiri_0155`, no abort | Fairy Ocarina (native) | hand-over | still glitched after the get, as N0 (BBender, screenshot) |
| N2 | same | N0 + timeline and hand-over stows (derived); log: `mods:` `Goto_HyruleCastle`, `Dm_Kokiri_0155`, no abort | Fairy Ocarina (native) | timeline, hand-over | still glitched in the first moments of the presenting timeline (BBender) |
| N3 | same | N0 + `WarpDone` flag off before Event43 and on after it (BBender's idea; derived); log: `mods:` `Goto_HyruleCastle`, `Dm_Kokiri_0155`, no abort | Fairy Ocarina (native) | flag | still glitched in the first part of the presenting timeline (BBender) |
| N4 (diagnostic) | same | N0 + Saria's schedule list without `EquipmentStateWhenWait`/`WhenWalk` on the `WarpDone` entry (`tools/derive_nohold.py`); log: `mods: Component/AIScheduleParam/Npc_Kokiri_Saria_Child...` before `Dm_Kokiri_0155`, no abort | Fairy Ocarina (native) | none | **clean**, the whole farewell; before it she sits on her stump in Kokiri Forest with empty hands (BBender, rerun N4b) |
| N5 | same | N0 + a copy of the `WarpDone` schedule entry with `Invisible` equipment after it, switched by a new saved flag `Clawshot.SariaFarewell.HideOcarina` that the forest exit sets before Event43 and clears after (`tools/derive_hide.py`); log: `mods:` `GameDataList`, `Goto_HyruleCastle`, the schedule list, `Dm_Kokiri_0155`, no abort | Fairy Ocarina (native) | hide copy | holds her ocarina before the bridge (as wanted), but the timeline's start **and** the part after the get are still glitched (BBender) |
| N6 (diagnostic) | same | N5 with the hide flag starting true (`--default-on`); bridge read in play: `Clawshot.SariaFarewell.HideOcarina` 1, `Npc_Kokiri_Saria_Child_WarpDone` 1 | Fairy Ocarina (native) | hide copy, on from the start | farewell **clean**; afterwards in Kokiri Forest Saria sits on her stump playing with empty hands (BBender, screenshot) |
| N8 (diagnostic) | same | N0 + the hand-over skips Saria's own prop (Event18 -> Event32: no `ParticipateEvent`, no bind; `tools/derive_noprop.py`); log: `mods: Dm_Kokiri_0155`, no abort | Fairy Ocarina (native) | none | before: Saria at her stump looks right; timeline start glitched; hand-over: **only the wrong model** shows, the right one is missing; after the farewell she no longer plays at the stump (BBender) |
| N7 | same | N0 + both scenes' Saria entry `EventMemberCreateMethod` 2 -> 0, forest exit without the warp (Event11 -> Event191; `tools/derive_scene_saria.py`); log: `mods:` `Goto_HyruleCastle`, `Dm_Kokiri_0150`, `Dm_Kokiri_0155`, no abort | Fairy Ocarina (native) | none | stump looked right; the farewell looked as always (one Saria, at the bridge): timeline start glitched, hand-over glitched (BBender). The creation method on her entry changed nothing visible. |
| **N9** | same | N0 + the bridge Saria (placement `KokiriForest_ArriveLostWood`, Hash 1660754835063030086) gets an actor of her own, `Npc_Kokiri_Saria_Child_Farewell` (Saria's pack with `AIScheduleRef` to her own list: Saria's list without `Hold` on `WarpDone`), ActorInfo/GameActorInfo rows copied, the three flows name the new actor for that instance (`tools/derive_farewell_saria.py`); log: `mods:` row tables, `KokiriForest_Child_Static`, the new pack and list, `Goto_HyruleCastle`, `Dm_Kokiri_0150`, `Dm_Kokiri_0155`, no abort | Fairy Ocarina (native) | own actor | **clean before, during and after** (BBender): rock Saria plays her ocarina, both farewell parts show one correct ocarina |

**What the glitch looks like** (no-mod control, BBender's screenshots, 2026-11-25). It shows twice:

1. At the start of the presenting timeline `Dm_Kokiri_0150`, Saria holds a malformed double ocarina until she reaches to
   her back waist; from then the timeline is correct.
2. In the hand-over `Dm_Kokiri_0155`, after the get window (the gift is right), two ocarinas: one in the correct place
   and one clipping into it, mirrored.

So the glitch is the remake's own, before Gohma, with no mod.

**Cause (N4, N6, N8):** Saria's schedule entry `WarpDone` holds `Npc_Equipment_009` on `Weapon_R`; it is drawn beside
the scene's own prop (the right one, N8). The equipment state is applied only when Saria is created (N6), so every
change made when the farewell starts came too late: the stow action `EventTriggerChangeAIScheduleEquipState
{EquipState: 0}` (N1, N2), the `WarpDone` flag toggle (N3), a hidden copy of the entry (N5), the scenes creating
their own Saria (N7). Changing the list itself (N4, N6) also reached Saria playing on her stump in Kokiri Forest.

**Fix found (N9, BBender, 2026-11-25).** BBender's vanilla walk-through led to the placements: Kokiri Forest has four
Saria placements on one schedule list, and the farewell's Saria is the separate bridge placement
`KokiriForest_ArriveLostWood`. Giving it its own actor and list, as the game does for the Sacred Forest Meadow
Saria, removes the held ocarina from the farewell only.

## Saria fix in the repository (plan task 13)

Claude, 2026-11-25. `src/clawshot/patch/saria_farewell.py` builds N9 in every seed (Q2): new actor
`Npc_Kokiri_Saria_Child_Farewell` (Saria's pack, its ActorParam renamed, `AIScheduleRef` to its own list), its list
`Component/AIScheduleParam/Npc_Kokiri_Saria_Child_Farewell...` (Saria's without `Hold` on `WarpDone`), ActorInfo and
GameActorInfo rows copied from Saria's, the `KokiriForest_ArriveLostWood` placement (Hash 1660754835063030086) on the new
actor, and the names in `Dm_Kokiri_0150` (actor entry, clip `BindActorName`), `Dm_Kokiri_0155` (actor entry, Event7,
Event38, Event44) and `Goto_HyruleCastle` (actor entry, Event11). The writer gained `NewFile.sized_like` for a new loose
file without a size formula (the list: Saria's entry, it only shrinks). Tests: `tests/test_saria_farewell.py`,
`tests/test_saria_farewell_dump.py` (exactly 3 actor entries and 5 names, only that placement, the list differs only in
the `Hold` fields), `tests/test_write_new_files.py`; `test_scene_handoff_dump.py`, the gift and setting seed dump tests
pass with the fix always on (53 passed). The failed attempts' pilot code (stow action, flag toggle, hidden copy,
`saria_stow`) and the idle switch (`event_models_idle`, containers' `idle`) are removed. Plan 13.1's wording (a stow
before Event7) predates the matrix; the fix that replaces it is covered by these tests. **Played, repository build (BBender, 2026-11-25):** QA seed 7100 built once from the working tree on `ceab074`
(models on, Saria's gift the Biggoron Sword), Longshot v3.2.0, save `saves/before-farewell-ocarina-qa` slot 01 (pre-Gohma,
no Fairy Ocarina). Log: `mods:` `KokiriForest_Child_Static`, `Npc_Kokiri_Saria_Child_Farewell.pack.zs`, her schedule
list, `Goto_HyruleCastle`, `Dm_Kokiri_0150`, `Dm_Kokiri_0155`, `Dm_Item_Clawshot_Item_Sword_Biggoron.pack.zs`; no abort.
All clean: Saria plays her ocarina on the rock before, presents and hands over the Biggoron Sword, holds one normal
ocarina of her own (13.2, 13.4).

## Played results (plan task 14)

Each result names who played, the build (commit + Longshot version) and the `mods:` lines seen. All runs on the QA
seed (`qa/seed`, base seed 7100, models on), built from `ceab074` plus the working tree of `feature/event-items`;
Longshot 3.2.0. Play sheet: `C:/Users/bened/ootr/work/event-items/qa/task14.md`.

### E1 LW Gift from Saria: Biggoron Sword (vanilla Fairy Ocarina), 2026-11-25

- Played by BBender, save `before-farewell-ocarina-qa` slot 01 (pre-Gohma, no Fairy Ocarina), run `runs/t14-saria`.
- `mods:` lines seen: `Event/EventFlow/Dm_Kokiri_0150.bfevfl.zs`, `Event/EventFlow/Dm_Kokiri_0155.bfevfl.zs`,
  `Pack/Actor/Dm_Item_Clawshot_Item_Sword_Biggoron.pack.zs`, `Pack/Actor/Npc_Kokiri_Saria_Child_Farewell.pack.zs`,
  `Mals/USen.Product.110.sarc.zs`, `RSDB/ActorInfo.Product.111.rstbl.byml.zs`,
  `RSDB/GameActorInfo.Product.111.rstbl.byml.zs`.
- Seen (BBender): Saria presents the Biggoron Sword and Link holds it; get window "Biggoron Sword"; Saria's own
  ocarina normal; no pre-Gohma glitch (the Saria fix holds on this seed).
- Bridge (Claude, 19:25): `HavePlayedEvent.Dm_Kokiri_0155` 1, `IsGet.Weapon_Sword_Biggoron` 1,
  `IsGet.Item_Ocarina_Fairy` 0. One get, no crash or softlock.
- Not checked here: Link's own ocarina (14.5), since this save owns no ocarina; left for E10.

From E2 on, one new game played in vanilla order (BBender, 2026-11-25: the saves follow vanilla order, and the
farewell save made after Gohma is the one later runs use). The QA seed starts with the Fairy Ocarina and the warp
songs not placed at an event (fast travel, task 6.1). Run `runs/t14-newgame`.

### E2 Queen Gohma: Light Medallion (vanilla Kokiri Emerald), 2026-11-25

- Played by BBender, new game; save `gohma` slot 03 (Gohma beaten, before the blue warp).
- Seen (BBender): the Deku Tree's farewell shows the Light Medallion and his line names it; the Key Items screen that
  follows shows the Light Medallion model, but its caption still names the Kokiri Emerald.
- Bridge (Claude): `HavePlayedEvent.Dm_Kokiri_0130` 1, `IsGet.Item_Medal_Light` 1, `IsGet.Item_Stone_Forest` 0.
- Finding: the caption is a layout text, `LayoutMsg/ImportantMenu_01.msbt` `T_Message_00`, not an event line, so
  the line inventory (task 3, event messages only) missed it. `Dm_Kokiri_0130` Event52 opens the screen
  (`UISystemActor` `EventOpenPerformanceImportantMenu`, params only `IsWaitEnd: True`); the model follows the item
  given, the caption is fixed. No other flow in the 1.1.1 dump opens this screen, so it concerns Queen Gohma only.
  Decision Q5: rewritten since (plan 5.8), to be played on a rebuilt seed.

### E1b LW Gift from Saria after Gohma: Biggoron Sword (vanilla Fairy Ocarina), 2026-11-25

- Played by BBender, new game; save `saria-post-gohma` slot 03 (before the farewell trigger, Gohma beaten, Fairy
  Ocarina owned from the start).
- Seen (BBender): Saria presents the Biggoron Sword, Link holds it, get window "Biggoron Sword", her own ocarina
  normal; afterwards Link played a song and his own Fairy Ocarina looked normal (14.5).
- `mods:` lines as in E1 (same seed and files).

### E3 LW Target in Woods: Rupees (20) (vanilla Bullet Bag (40)), 2026-11-25

- Played by BBender, new game; save `lw-target` slot 03 (on the stump, Slingshot owned).
- `mods:` lines seen: `Event/EventFlow/Dm_LostWood_0040.bfevfl.zs`, `Pack/Actor/Dm_Item_Clawshot_TBox_Rupee_Red.pack.zs`.
- Seen (BBender): as expected: the scrub's prize shows the red rupee, one get of 20 rupees, the rupee moves with the
  scene.
- Bridge (Claude): `HavePlayedEvent.Dm_LostWood_0040` 1, `IsGet.Item_BulletBag_Medium` 0, `IsGet.Item_BulletBag_Large`
  0, `PlayerStatus.CurrentRupee` 22. Only the branch for a Link who owns the Slingshot was played; both branches name
  the same container (static check), the other branch is not played.

### E5 Kak Anju as Child: Hylian Shield (vanilla Empty Bottle), 2026-11-25: the English NPC line check (14.1)

- Played by BBender, new game; save `anju-child` slot 03 (in front of Anju, last Cucco in hand).
- `mods:` lines seen: `Mals/USen.Product.110.sarc.zs` (startup).
- Seen (BBender): her lines before completion name the Hylian Shield; she gives the Hylian Shield ("looks good").
- Bridge (Claude): `IsGet.Weapon_Shield_Hylian` 1, `IsGet.Item_Bottle` 0.

### Task 14 replays from the save library (QA seed rebuilt 2026-11-26 with 10b and Ruto's line; kept as `qa/seed-v2`)

Each run: Longshot 3.2.0, QA seed `qa/seed` (base 7100, `ceab074` + working tree), loaded from a library save
(`C:/Users/bened/ootr/work/saves/`), played by BBender, `mods:` lines and flags read by Claude.

- **E2b Queen Gohma (2026-11-26, run `runs/t14-gohma`, save `child-deku-tree-gohma-beaten`)**: Light Medallion shown
  and named in the Deku Tree's farewell; Key Items screen shows it, its caption naming it (Q5, plan 5.8
  played). `mods:` `Event/EventFlow/Dm_Kokiri_0130.bfevfl.zs`,
  `Pack/Actor/Dm_Item_Clawshot_Item_Medal_Light.pack.zs`, `Mals/USen.Product.110.sarc.zs`. Bridge:
  `HavePlayedEvent.Dm_Kokiri_0130` 1, `IsGet.Item_Medal_Light` 1, `IsGet.Item_Stone_Forest` 0.
- **E9a Barinade (2026-11-26, run `runs/t14-barinade`, save `child-jabu-jabu-barinade-beaten`)**: Ruto's thanks at
  Zora's Fountain show the Spirit Medallion (BBender: "looks good"). `mods:`
  `Event/EventFlow/Dm_ZoraFountain_0030.bfevfl.zs`, `Pack/Actor/Dm_Item_Clawshot_Item_Medal_Spirit.pack.zs`. Bridge
  did not answer during the scene (flags not read).
- **E10 HF Ocarina of Time Item (2026-11-26, run `runs/t14-moat`, save `child-hyrule-field-before-drawbridge`)**:
  Zelda throws a Piece of Heart; the moat object shows it, still glows and can be picked up (10.3); the get window
  names it with the right count. Two findings in `Dm_MelodyGet_Time`: (a) during Link's look he holds a Fairy
  Ocarina; (b) in the Song of Time lesson Zelda plays the Piece of Heart. Cause of (b): the inventory's prop
  `Dm_MelodyGet_Time/flowchart/Dm_Item_Ocarina_Time` is bound to Zelda's hand (Event35, `Weapon_L`), the instrument
  of her memory, not Link's look (task 4 misread it; 10.2 was ticked on that). Fixed: moved to the `played`
  exclusions (test `test_dump_zeldas_ocarina_in_the_moat_lesson_is_played_not_the_given_item`). Cause of (a): Link's
  look (cuts C01-C04) runs on his own animation (`C01`-`C03-Player_Child`), whose animation events
  (`AnimationEvent/AsNode/Dm_MelodyGet_Time_Player_Child.root.baev`) write the blackboard key `HoldOcarina`: the
  player shows his equipped ocarina; the flow binds no item. Decision (BBender, 2026-11-26): try a bind.
- **Pilot arm A (run `runs/t14-moat-lookA`, `pilot/moat-look-A`)**: the given item's container bound to
  `Player_Event` `Weapon_L` before C01, offstage before C05. BBender: Link holds the Piece of Heart ("sensible
  enough") and his own ocarina beside it; Zelda plays the Ocarina of Time again (fix (b) played). Decision (BBender):
  investigate editing the animation; if too complex, keep arm A. Built into the repository as a `[[hand]]` entry in
  `event_props.toml` (`HandBind`, `event_models.add_hand_bind`/`plan_hands`; synthetic and dump tests).
- **Pilot arm B (run `runs/t14-moat-lookB`, `pilot/moat-look-B`)**: arm A plus the animation events' key
  `HoldOcarina` renamed to `HoldOcarinX` (same length, file size as native). Log: `mods:` lines for the changed
  `AnimationEvent/AsNode/Dm_MelodyGet_Time_Player_Child.root.baev.zs`, the flow, the moat object and the heart's
  container; no crash. BBender (2026-11-26): Link still holds his fairy ocarina beside the Piece of Heart; everything
  else as arm A. So the scene's key is not what shows it. Claude's look (2026-11-26): the key's string is referenced
  by offset only (no hash of it in the file); the scene's other player files (`Animation/...Player_Child.anim.baev`,
  `AS/...Player_Child.root.asb`, `Model/...Player_Child.anim.bfres`) name no ocarina; `HoldOcarina` is also written by
  the player's own `Player_Child.root.baev` and 18 other scenes. Hiding it means reverse engineering the player's
  animation system: too complex by BBender's rule, so arm A stays and the extra ocarina is a known issue (plan 10.4).

Replays on the QA seed `qa/seed-v2` (2026-11-26, BBender, Longshot 3.2.0; flags read by Claude through the bridge):

- **Saria's farewell after Gohma (run `t14-saria2`, save `child-kokiri-forest-bridge`)**: Biggoron Sword presented
  and received, one item shown, all as E1b. `mods:` `Dm_Kokiri_0150`, `Dm_Kokiri_0155`, Saria's own actor and schedule
  list, `Dm_Item_Clawshot_Item_Sword_Biggoron.pack.zs`. Bridge: `IsGet.Weapon_Sword_Biggoron` 1,
  `IsGet.Item_Ocarina_Fairy` 0.
- **Lost Woods target (run `t14-target2`)**: Rupees (20) shown and named. `mods:` `Dm_LostWood_0040`,
  `Dm_Item_Clawshot_TBox_Rupee_Red.pack.zs`.
- **Anju (run `t14-anju2`)**: lines and get text name the Hylian Shield. `mods:` `Mals/USen.Product.110.sarc.zs`.
  Bridge: `IsGet.Weapon_Shield_Hylian` 1.
- **Controls, vanilla on this seed** (runs `t14-darunia`, `t14-zelda`, `t14-dodongo`, `t14-pg`): native look and text;
  no container loaded. Darunia's Joy and Zelda's Letter can not move today (`vanilla_fixed` D16 of the world data,
  `keep_vanilla` D31); their props are ready for when they can, saves `child-goron-city-darunia`,
  `child-castle-courtyard-zelda`. Volvagia and Morpha controls dropped (BBender: test swaps first; an unmoved check
  leaves its scene untouched, checked by the dump tests).
- **Rauru (run `t14-rauru`)**: Kokiri Emerald presented and named. `mods:` `Dm_SageRoom_0005`,
  `Dm_Item_Clawshot_Item_Stone_Forest.pack.zs`.
- **Bongo Bongo (run `t14-bongo`)**: Zora Sapphire. `mods:` `Dm_Awake_Shadow_Get.110`,
  `Dm_Item_Clawshot_Item_Stone_Water.pack.zs`.
- **Twinrova (run `t14-twinrova`)**: Shadow Medallion. `mods:` `Dm_Awake_Spirit_Get.110`,
  `Dm_Item_Clawshot_Item_Medal_Shadow.pack.zs`.
- **Light Arrows (run `t14-light-arrows`)**: Bolero of Fire shown as the Ocarina of Time, named right; BBender: "the
  model doesnt rotate and doesnt have the song effect". Cause (Claude): the flow plays `Rotate_GetDemo` on the prop
  (Event15); the native `Item_Arrow_Light` has it from `AS/Item_Common.root.asb`, the container had `DemoDummy` (D16);
  the effect is the song pack's (PR #41), which the shared ocarina container lacked.
- **Pilot arm B (run `t14-light-arrowsB`, `pilot/light-arrows-B`, `tools/build_light_arrows_pilot.py`)**: the
  container with the song pack's `ASRef`, `ASInfoRef`, `AnimationRef`, `ELinkRef`, row `ELinkUserName` and heaps.
  `mods:` the container, ActorInfo, the ELink table, `static`. BBender: "all good" (spins, Bolero's effect).
  Decisions D16b, D17.

Replays on the QA seed rebuilt with D16b/D17 (`qa/seed`, same placements as `qa/seed-v2`, built twice byte-identical,
216 files; 2026-11-26, BBender, Longshot 3.2.0):

- **Light Arrows (run `t14-light-arrows3`)**: spins with Bolero's effect, from the repository's code. `mods:`
  `Dm_Item_Clawshot_Item_Melody_FireBolero.pack.zs`, ActorInfo, GameActorInfo, the ELink table, `static`.
- **Saria's farewell (`t14-saria3`)**, **Lost Woods target (`t14-target3`)**, **moat (`t14-moat3`)**: as before with
  the sword, rupee and heart containers now carrying their own sets (no spin in hands, the target's `C02` fine, no
  crash). BBender noted (moat): in Link's look the heart hangs from his hand by its tip, where Zelda's throw and
  Saria's farewell hold it by its middle. Cause (Claude): the model's origin is the heart's tip; the hand bind has no
  offset (D6), while the get pose uses the item's `GetDemoOffsetPos` (pouch data, which containers leave out). Known
  issue; a follow-up could give hand binds the item's offset.

### Runs on real placements (2026-11-26, BBender playing, Longshot 3.2.0)

Seeds built outside the repository by `tools/build_matrix_seed.py` (`qa-matrix`: songs at Saria, the moat and the
target, every reward slot swapped) and `tools/build_real_seed.py` (`qa-real/R1`: moat Biggoron Sword, Zelda's Letter
Piece of Heart, Darunia Song of Storms; `R2`: moat Bolero of Fire), with checks lifted in that process only
(Darunia's and Zelda's Letter's `keep_vanilla`/`vanilla_fixed`, `gifts.ANCHORS`). Look-only seeds (item shown but not
granted) were dropped by BBender after the first batch: real placements only. Full log: `qa/run-results.md`.

- **First batch (runs 01-15):** heart, sword and song props in hands, the target, Darunia, Ruto's stone, the
  awakenings and the Light Arrows passed; four issues: (1) songs show their effect only where the scene plays an
  animation on the prop; (2) a model with a colour variation on a placed object crashes on load; (3) Zelda's Letter
  scene leaves the letter standing; (4) hand binds hold the item by its model origin.
- **(2) fixed:** model-only placed objects (task 10 section). `r1-moat`: sword thrown, shown, picked up, held, named
  right (`IsGet.Weapon_Sword_Biggoron` 1), no crash.
- **(3) fixed:** the grant calls the shared subflow `Dm_SY_GetInEvent`/`GetInEvent_Zeldaletter`, whose own
  `Item_ZeldaLetter` is the same actor as the scene's prop; it now takes the same container
  (`event_models.plan_subflow_renames`). `r1-zelda3`: no letter, heart handed over and held, no second heart.
- **(1) fixed:** pilots on Saria's farewell: container autoplay (`Pose_GetDemo`, `GetDemo`), played nodes
  (`Pose_GetDemo`, `GetDemo`, `Rotate_Stoped`) and an `Always` effect user showed nothing; `Rotate_GetDemo` showed the
  effect with a spin (BBender: the fallback); emitting the song user's key (`EventTriggerEmitXLink {ELinkKey:
  GetDemo}`, BBender's hint from the song lessons) shows the effect on a still ocarina. Built as
  `event_models.add_song_effect` (an emit after each bind or join, a timeline emit clip, an emit after a song hand
  bind). S1 (Saria, Song of Storms): effect while presenting and in Link's hand. S2 (moat, Sun's Song) and S2b (R2,
  Bolero): the effect stayed at the landing spot during Zelda's throw, with either ocarina model; the throw animates
  `Skl_Root` and leaves `Root` at the origin. D18; S2c (R2 rebuilt): the effect follows the throw, no lean.
- **(4) open:** pilot `pilot/hand-offset-heart` (TransOffset from the models' box centres) waits for run S6; adopting
  it changes D6.
- **Known issue, seen again (S2c):** in the moat look Link also holds his equipped ocarina (plan 10.4, arm A/B).
- **Known issue (BBender, 2026-11-26, runs S2d, S7, S8): Sun's Song's effect in events.** Its effect does not follow
  the prop: at the moat it appears and disappears at random places during Zelda's throw; at Saria's farewell it is
  missing while she presents the ocarina except one moment at Link's feet, and in Link's hand it does not follow when
  he puts the ocarina away (Song of Storms does, S1). The ELink calls are like the other songs' (same `BitFlag`,
  `Skl_Root`); the effect differs: `Ply_Ocarina_Correct_SunSong_00` alone has a second emitter `Pointlight`, and its
  `Cloth_00` differs from Storm's in a few bits (offsets 0x20, 0x7c, 0xf6c, 0xfcc). Pilot S8 (a clone without
  `Pointlight`) changed nothing. BBender set it aside to finish the other scene/item combinations first.
  Fix agent (2026-11-27): Sun's `Cloth_00` is built from another emitter template (shared only with effects that play
  on still things: `SunSong_End_00`, the Sun's Song sensor areas, `Enm_Redead_Freeze_00`); its particles stay where
  they are born. Pilot P1 (`UseEmitterSetPosDiff` = 1 on the event user's `GetDemo`, S14): no change. Pilot P2 (S15:
  Zelda's Lullaby's cloth recoloured to Sun's yellow): sticks to the ocarina, so the container and attachment are
  right, but BBender rejected the look. BBender's observation from the pickup-effect work: the effect rotated with an
  ocarina held at an angle, so maybe only rotation follows, not translation. **Decision (BBender, 2026-11-27): known
  issue for this feature, skipped; maybe a later PR.** Pilots and values: `qa/run-results.md` (S7, S8, S14, S15).
- **Open issue (BBender, 2026-11-26, runs S3, S11): no song effect on the Lost Woods target's prize.** While the scrub
  shoots it, the prize (Epona's Song, `Dm_LostWood_0040`) spins (`EventPlayAS C02`) without its effect; Link's get
  pose afterwards is fine. Each branch runs bind -> emit `GetDemo` -> `C02`; pilot S11 (emit after `C02` starts)
  changed nothing. To fix after the run list (BBender: the runs first, then fixes by separate agents, a rerun of the
  cases with issues, a final run). Played fine with this code: S9 Saria (Storms), S10 moat (Storms), S2e moat (Bolero).
  Fix agent (2026-11-27): the event user (copied from `Obj_Heart_Container`) starts `GetDemo` only from its action
  triggers `Rotate_Obj` and `Rotate_GetDemo` (why Light Arrows works); the scenes' own ASes (`C02`, `C09-Gauntlet`,
  from the scenes' `EventAS` sets) start nothing. Native pattern: `Obj_Heart_Piece` has a trigger on the scene AS
  `Dm_Goron_0040_Obj_Heart_Piece/C01`. Pilot A (`AS[Lower]` triggers `<scene ASB root>/<AS>` -> `GetDemo` on every song
  event user): **passes**, BBender S12 (target) and S13 (Darunia). Ported (D20, uncommitted; not yet played from the
  repository build: `qa-matrix-A`, `qa-real/R1-A`).

The full synthetic and dump suites run once after the remaining runs (plan 15); their earlier results (2026-11-26,
before D16b-D18) are superseded.

### Final run (2026-11-28, BBender, seeds `final/seed` and `final-off/seed`, run sheet `qa/final-run.md`)

29 of 30 checks played, all pass (P1 1-11, P2 12-22 without 19, P3 23-30). Check 19 (DMC Great Fairy) not played: the
save `adult-death-mountain-crater-great-fairy` is at the summit fountain (DMT gave its Progressive Bomb Bag, right).
Text decisions from the run: J and K above (not yet played; rerun of the castle, summit, desert and Zora's Fountain
fairies next). Issues seen that are not from this branch (read-only investigation, `investigate-f2/report.md`, both
on main too): the pause menu's Key Items tab opens only with a Spiritual Stone (`PouchTable` `StoneArray`), so a
medallion first leaves it "???"; the Threads of Time entry of the castle quest shows MsgNotFound after the `kaepora`
fast start plus the Deku Tree blue warp (`Warp_Kokiri` Event4 sets `Step01`, which has no text).

## Open questions

- Q1 (Kareem, in the PR): should `event_item_models` be a setting, and default on? (D7)
- ~~Q2~~ answered (BBender, 2026-11-25): the Saria fix applies in every seed (D9).
- ~~Q3~~ answered (BBender, 2026-11-25): group A of the NPC line inventory; B, C, D deferred (D8).
- ~~Q4~~ answered (BBender, 2026-11-25): no idle animation in containers (D16).
- ~~Q5~~ answered (BBender, 2026-11-25, "if not too difficult"): Queen Gohma's Key Items caption `ImportantMenu_01`
  `T_Message_00` has its item name rewritten like the NPC lines (5.6): a 25th entry in `patch/event_lines.toml`
  (plan 5.8). Dump test: the caption names the given item in all 16 languages, none left native. Not yet played (the
  E2 run's seed was built before it). Open: what the screen shows when Gohma gives an item that is not a key item.
  (The screen's model is a per-item actor, `<item>_ImportantMenu`, e.g. `Item_Stone_Water_ImportantMenu`.)
- ~~Q6~~ answered (BBender, 2026-11-25): Ruto's stone in Jabu-Jabu (`Dm_InsideJabu_Jabu_0030`, placed object
  `Obj_InsideJabu_Jabu_Stone_Water_A_01`, Notes `Event252` `Item_Stone_Water_Ruto`) follows Barinade's reward in this
  feature, like the moat object (variant B); plan task 10b.
- Note (BBender, 2026-11-25, walk-through run): Darunia's Joy (`Dm_Goron_0030`, always vanilla today) shows
  Goron's Bracelet (prop, inventoried) and his line (what the bracelet lets Link lift) describes the item without
  naming it, so it stays (decision 5.6: only words naming the item change). Once GC Darunias Joy is
  randomized the prop follows the item, the line keeps describing the bracelet: a known issue then, not now.
- ~~Q7~~ answered (BBender, 2026-11-25): out of scope for now ("too complicated"), but a save before the pull is
  collected. BBender's idea for a later Master Sword shuffle: the first pull shows and names the item placed there;
  later pulls show the sword. The pull (`Dm_TimeTemple_0030`: window `Event117`, Notes `Event209`,
  `Land_HrlCity_MasterSword`, pedestal `Obj_TimeTemple_MasterSword_A_01`) is played as a vanilla control.
  Design: `plans/rounds/r18-master-sword-design.md` (design only).
