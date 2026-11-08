# Round 5, Track E — in-game logic session (cs5e)

Branch `r5/playtest`. Owns only `plans/playtest/` and this file. No code/data/dependency edits; no merge/push.
Read the worktree AGENTS rules, README, roadmap (including Round 5 shared-file opening), architecture,
orchestration, game-data/world-format plans, decisions, all four round-4 handoffs and earlier question sections.

## Item 1 — deduplicated questions

`plans/playtest/questions.md`: 177 stable question IDs, including nine checks already asked by Claude on
2026-11-08, explicitly **asked 2026-11-08, answer pending**. They are not scheduled for replay. Each active ID
has action/observation, age/progress, rule file/key or fact to record, outcome implications and source provenance.
Area-level resource audits preserve broad unresolved drop questions without pretending guide silence proves absence.
Historical questions already answered, policy-only questions and duplicate summaries are reconciled at the end.
No player answer or in-game success is invented.

Reviewer steering received during work: Kareem is progressing his main game toward adulthood. Session 1 will
start immediately after the first Master Sword pull; child sessions wait until return travel is unlocked.
Already asked: Din fairy fee/shortfall/retry, other fairy before Din Fire, summit owl before Din Fire, moat Ocarina
without Scale, second diving round, Jabu scaleless scrub dive, explosive tonsil switch, Door of Time, first/post-Forest
sword return (the two chronological return attempts share TT02). These are absent from every session route.

## Save evidence (read-only)

Read all 12 `progress.sav` files in the two 2026-11-07 backups with `clawshot.save.load`; decoded quest Enum values
against the read-only GameDataList. The tower backup's slots 00/01/02/03/05 have Forest quest complete and Fire
quest `DungeonStart`; slot 04 is a fresh intro. Its slot 01 has Lullaby/Saria, no Din Fire/Boomerang/Hookshot/Longshot,
Talon minigame uncleared and tower-heart Hash 9814903750835309225 unset. Both old backups' slot 01 is useful child
progress, not demonstrated adult-ready state.

Also read all six progress saves under the reviewer's new snapshot:
`E:/OOTRemake/work/save-backups/2026-11-08_0802-before-adult/save/5a3c9e1f0b7d24680000000000000001/`.
Slots 00/01/05: Emerald, Lullaby, Saria, Sun Song, sword/shield and Zelda courtyard; no Ruby/Sapphire, Forest
medallion, Din Fire, Storms, Boomerang, Hookshot, Longshot or small Bomb Bag flags. Quest values:
Forest `Complete`, Fire `DodongoCavernOpne`, Water `Ready`, Door `Step02`, Forest sage `Ready`.
Other slots are intro-era, including a Boomerang chest-test slot. This snapshot is not an adult checkpoint.
The main game is moving: session starts are future milestones, not claims about a stale backup's reachability.
Missing flag lookup (`None`) was treated as unknown, never absent. Exact weapon flags were resolved from prior
census notes (`IsGet.Weapon_Sword_Kokiri`, `IsGet.Weapon_Shield_Deku`); no save was written.

## Provisional choices and owner questions

- Player sheets contain route/actions only; Claude's rule consequences stay in the question register.
- First-time/absent-item comparisons require preserved disposable copies or reviewed variants. Owning but not using
  a weapon can test combat, not an `IsGet` gate. A failed attempt without a positive control is inconclusive.
- No known-crashing Fire Arrows pickup replay, game launch, main-save edit, or automatic backup reset.
- **Kareem/co-owner: should separate age/state Hash pairs count once or twice?** GE08/PAIR01 collect evidence only.
- **Kareem/co-owner: courtyard skip, Navi-wake policy, linking Mido skip to forest exit, full intro removal and
  remake-vs-N64 desired pool remain product choices where not already settled by D18/D19.** Not player errands.

## Cross-track communication

Posted to `cs-r5` as cs5e: old backups show child progress, request producer-owned shop/gift launcher instructions;
then acknowledged revised adult-first routing and pending-answer suppression. No other agent terminal accessed.
The prescribed `~/go/bin/bermuda` first failed with exit 127 (Windows HOME expansion yielded a non-executable path).
Directory inspection showed `C:/Users/hi/go/bin/bermuda.exe`; using that explicit executable succeeded. No unchanged retry.

## Verification so far

Live read-only save reader exercised against 18 actual progress saves; quest states printed and inventory flags
resolved against known actors. Register construction checked 177 unique IDs. No gameplay verification claimed.
Four gate commands are reserved for the pre-handoff run, as requested; no repeated dump runs.

## Item 2 — player routes

`plans/playtest/README.md` is the entry point; `session-1.md` through `session-17.md` are short area/milestone
cards. Session 1 starts after the first pull, goes through Kakariko/Hookshot to Forest Temple; child cards wait
for return travel. Long routes have area stop headings. Late tools/consumed states are explicitly deferred to
proper disposable controls rather than faked with unequipping. All 168 unanswered IDs appear exactly once;
the nine already-asked IDs appear in no session. Membership verified by the route-construction smoke.

Item 1 committed as `5a7634c`. Source register pointers updated with the final area-session numbering.
Reviewer launcher steering incorporated: **only `E:\Games\Hookshot\hookshot.exe`**, no work-build path or fallback.
Item 3 will re-read the corrected template before copying; no launcher has been run.

## Item 3 — cheaper isolated checks

`plans/playtest/prepared-mods.md` lists six external overlays under `E:/OOTRemake/work/r5-playtest/`:
tower red-rupee persistence, tower chest/Boomerang fallback, fresh-game no-Slingshot room recovery, Mido Boomerang
for child vine-wall comparison, adult Longshot→Hookshot order, and supported red-rupee treasure reward preview.
Nine launchers copied/adapted from the corrected round-2 template: those six plus existing corrected mini-seed 7,
intro-removed and all-skip-chain overlays. Every EXE assignment is release-only; no launcher/dry-run/game executed.
The upgrade/reward launchers require pre-staged matching milestone users and refuse an absent checkpoint.
No source backup or dump write; all generated files/code/manifests stay outside the repository.

Observed smoke: `uv run python E:/OOTRemake/work/r5-playtest/build_overlays.py` passed four overlays/seven files,
independent field-diff allowlists, compression/readback, stable identity, three required resource-entry raises,
all other resource entries unchanged and source checksums unchanged. `build_order_reward.py` passed two overlays/
four more files, independent reverse-field diff and size limits with no table raises. Total six overlays/eleven files.
External builders/manifests remain useful reproducibility artifacts, not committed scaffolds.

Static checks passed all nine launcher texts: release path, isolated user/log/overlay, backup direction, no destructive
or window-start commands. Initial substring checker failed on `start` inside inherited dry-run ECHO prose;
printed predicates showed every real safety check true and only prose matched. Changed checker to actual command
tokens; one aimed rerun passed. No batch execution was used as a substitute for static inspection.

Item 2 commit: `6fdcda4`. Shop/gift variants remain producer-owned (MOD07/08); no duplicate patch implementation.
**Claude: review new isolated variants before scheduling, and stage first-adult/pre-Dampe and child-return/pre-treasure
checkpoint copies for MOD03/04.** Other consumed first-time states require matching preserved copies, never main resets.

## Item 4 — answer ledger

`plans/playtest/answers.md` has one row for every question ID: nine already-asked pending rows first, then 168
not-yet-played rows in route order. No actual answer filled without Kareem's observation. Each row has room for
age/inventory/progress/result/evidence; `inconclusive` and missing-control states are explicitly supported.

Observed saved-document smoke: 177 unique answer rows cover all 168 active register headings plus nine already-asked
IDs; 168 unique route IDs cover exactly the active questions and none of the already-asked questions. All 208
relative Markdown file links resolve, every primary rule-file path exists, and all nine actual launcher texts use
release-only EXE assignments. Item 3 commit: `72934b4`.

## Pre-handoff gates

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | Passed: 116 files already formatted |
| `uv run ruff check` | Passed: All checks passed |
| `uv run pytest` | Passed: 297 passed, 26 skipped; 97.72 s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | First attempt timed out at 600 s in final header scan; diagnostic retry with `-vv --durations=5`, 3,600 s deadline: **25 passed, 298 deselected; 116.16 s** |

Item 4 commit: `b225365`. The synthetic gate includes the existing seed/search suite; no tests were added,
edited or re-pinned for this plans-only track. External overlay smoke is file-level proof, not game acceptance.
The four item commits are `5a7634c`, `6fdcda4`, `72934b4`, `b225365`, in that order.

## Reviewer followup — Track C's 20 excluded chests

Read `git show r5/seeds:plans/rounds/r5-seeds.md` and all 22 `remake/extra_*.toml` files through `git show`.
Branch observed at `b42b0f4c1602`: exactly 20 entries have `rule = "False"` plus `keep_vanilla`.
`plans/playtest/excluded-chests.md` is a register addendum: XC01–XC20 each names the exact Hash, age/progress,
surface entrance/route/appearance observation and owning `[locations."<name>"]` whose rule/exclusion it can inform.
Area-card rows and answer-ledger rows cover every entry. Repeat rupees/mutually-exclusive copies do not become
independent progression checks merely because a route works.

Deduplicated existing visits: LW05→XC19 and GE01→XC04 are aliases, never separate errands. LLR02 now covers
tower token only; XC14 handles upper chest. GC signs and Dampe repeats share existing puzzle/race logs.
Also incorporated the branch's two nearby bold clarifications: FT08 identifies the falling-ceiling chest, not basement,
and W03 checks east ladder chest before Lullaby plus old west pit/Like Like absence. No source/logic file edited.

Observed followup smoke: 197 unique ledger IDs = 186 unique routed checks, nine already-asked pending IDs,
two aliases. Exactly 20/20 branch exclusions map to unique Hashes and exact extra-file entries; each is in its area's
session. All 252 local Markdown links resolve. Already-asked checks and aliases occur in no route.
Initial branch mapping looked for new world names under `oot_randomizer_name` and failed on the first Well chest.
Printed definition keys and its full definition showed an empty OoTR name and the exact name under `name`;
one aimed rerun joined by census-readable `name` and mapped all 20. No fabricated OoTR correspondence.

## Dump gate deadline diagnosis

Initial required dump command selected 25 tests and completed 24 before its 600-second deadline, while the last
`test_dump_every_zs_frame_names_the_dictionary_its_name_calls_for` was still scanning. No assertion failure printed.
Read its body: it opens 18 bytes from every `.zs` file. Printed actual workload: **102,185** `.zs` paths,
16,463,972,954 compressed bytes total; Pack subset 8,385 files/63,241,015 bytes; 16 logical CPUs.
One cause-aimed retry used a 3,600-second deadline and `-vv --durations=5`; it passed all 25 tests in 116.16 s.
The final header scan itself took 14.54 s on retry. This does not establish why the first scan stalled;
no code/test/dump mutation or retry loop was used, and no assertion failure was hidden.

## Final handoff

All requested plan work, including the reviewer followup, is complete on `r5/playtest`. Final saved-document smoke:
197 unique ledger IDs, 186 unique routed checks, 20/20 exact excluded chest targets, nine already-asked pending
checks and two aliases excluded from routes, 252 resolved local links. Formatting/lint and synthetic/dump gates passed.
No code/data/dependency files or `decisions.md` were changed; no game/launcher/GUI/build was started; no merge/push.
The final followup/evidence commit ID is reported in chat and the handoff thread (cannot self-reference its own hash).

Left for people, not unfinished implementation:

- Kareem's observations, starting with the adult-first card; already-asked checks remain pending rather than repeated.
- Claude reviews six isolated overlays, stages matching disposable milestone users, then schedules release-only launchers.
- Cross-track shop/gift in-game checks use producers' reviewed artifacts; this track does not modify their code.
- Claude uses XC answers to review Track C's exact `False`/`keep_vanilla` entries; no excluded chest was silently enabled.
- Owners decide check multiplicity/product choices; successful alternate-copy/repeat collection alone does not decide policy.
