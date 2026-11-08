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
