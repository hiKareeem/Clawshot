# Round 14 Track B — Longshot (#23), Discord copy (#18), game options (#24)

Base: `ffea543`, Clawshot 0.2.0. No version bump. Track owner: cs14b,
`openai-codex/gpt-6.1-sol`. Complete; ready for Claude's first review/merge. No merge or push.

## Scope and decisions

- One optional `game` path across application preferences, generation protection and Play.
  Read migration from saved `hookshot` retains the chosen path; an existing `game` wins.
- Detect Hookshot and Longshot game folders without executing binaries; preserve the
  HOS_MODS capability probe. Per Kareem's followup, a launcher's available recorded
  default wins; otherwise use numeric version order, release above same-version RCs,
  unversioned nightlies below recognized releases. A directly picked build folder is pinned.
  The chosen launcher path stays saved, not its transient resolved build.
- UI Game tab names both runtimes; Longshot download address is plain text, not an
  application network request. A missing game keeps Play visible and disabled with a reason.
- Copy for Discord wraps the same settings string in single backticks. No codec or
  generator output change. No seed working-set additions; r13 integrated dump fixture applies.
- Output/user remains the seed's save folder when switching runtimes. Per Kareem's #24
  addition, first creation copies only option.sav/account.sav from the selected game's
  newest user/save/<id> folder; never slots or existing seed files. Missing files are
  skipped and reported in the UI/pack result. No game is started by automated checks.

## Sources (GPL: facts only; no code copied)

Read 2026-11-13:

- [Longshot `README.md`](https://git.magicbean.dev/MagicBeanDev/Longshot/src/branch/main/README.md),
  “What you need”: program 0400486024DEC000, update v131072, build e0f3ccfa.
  “On Windows”, “On Linux”, “Where the files go”: bin game, selected game folder,
  default Windows `%USERPROFILE%/Games/Longshot`, Linux `~/Games/Longshot`, separate
  `--user` folder. “Updating”: back up saves; mods survive updates.
- [LongshotLauncher `README.md`](https://git.magicbean.dev/MagicBeanDev/LongshotLauncher/src/branch/main/README.md),
  “Installing”: portable `LongshotLauncher-data` beside the Windows executable;
  installed program `%LOCALAPPDATA%/Programs/LongshotLauncher`, data
  `%LOCALAPPDATA%/LongshotLauncher`; Linux data `~/.local/share/longshot/launcher`,
  portable AppImage `.home`. “Planned next” explicitly says current builds are
  `~/Games/Longshot/<version>`; `versions/<version>` is planned, not current.
- Selection citation: `LongshotLauncher-data/builds.json`, format 1,
  `builds[].default=true` next to `folder`/`version`, read-only on Kareem's install.
  The launcher README's “What it does” and “Design decisions” say its Play starts that
  default. settings.json stores channels, not the selected build. A missing default falls
  back to available numeric versions; an available default lacking mod support refuses.
  Kareem approved the mixed-channel fallback order on 2026-11-13.
- Read-only local evidence: `E:/Games/LongshotLauncher` portable layout;
  `E:/OOTRemake/work/r20-release/play-keys-23/Play Clawshot 0.2.0 keys 23 on Longshot.bat`
  uses `bin/longshot.exe`, HOS_MODS only, empty/unset HOS_FS_OVERLAY,
  LONGSHOT_NO_UPDATE_CHECK=1 and separate --user. User reports Kareem played this
  community seed today. That is not acceptance of the new Clawshot UI integration.
- Current loading contract: `plans/03-game-data.md` section 45. Per Kareem's updated
  instruction, launcher staging uses `E:/OOTRemake/tools/test-launcher-template-longshot.bat`.
  The initially copied Hookshot template was replaced before execution.
- Claude's supplied headless Longshot v3.0.0-rc.2 boot evidence with keys-23 only:
  `prompts: <mod>/romfs/System/Resource/ResourceSizeTable...rsizetable.zs: the button prompts' sizes merge`.
  The initial controller-icon inference is now superseded by Kareem's seed101 app check:
  **Xbox prompts were observed on Longshot rc.2**. Hookshot 2.1.0's Switch-icon fallback
  is a separate runtime-specific issue.

## Coordination

Thread `cs-r14`, plain posts as cs14b. Track A owns tracker and small hooks in shared
server/static files; this track changes Game/Play and settings-copy controls. Posted
canonical `game` key contract and requested first serialized full-gate slot. Initial
shell tilde-path lookup failed; PATH `bermuda` resolves the same executable.

## Verification

- Final `uv run ruff format --check`: 336 files already formatted after #24.
- `uv run ruff check`: all checks passed. Each ran under atomic gate.lock, workers=3,
  with neither game process present; lock released between stages.
- Read-only real-install smoke used actual `detect_game` + verified `play_plan`:
  portable launcher resolved to Longshot v3.0.0-rc.2, Hookshot to v2.1.0.
  Asserted selected bin/cwd, only seed101 HOS_MODS, game-specific update variable/log,
  no HOS_FS_OVERLAY, same private user. Saves remained empty and logs nonexistent.
- Started actual `uv run python -m clawshot.ui --no-open` with an isolated APPDATA
  preference directory under work/r14-longshot, not Kareem's real preferences.
  Actual page HTTP calls checked the dump, switched games, loaded seed101, and showed
  Play disabled with an explicit missing-game reason. No game was launched.
- Browser smoke caught a Detect/blur path-normalization race: forward slashes changed
  to native separators while a request was in flight, leaving “Checking…” behind.
  Fixed same-canonical-folder recognition; repeated that exact interaction successfully.
  The race is exercised by the actual browser smoke, not a source-text unit test.
- Both Copy for Discord controls produced exactly one backtick on each side of the
  unchanged canonical string. Plain Copy stayed plain. Clipboard permission-denial
  smoke selected the original string and gave wrapping advice without altering it.
  Only the clipboard boundary was substituted in the actual page's main world.
- `node --check src/clawshot/ui/static/app.js`: passed after the race fix.
- Browser requests stayed on loopback (zero external requests), no external links.
- Screenshots at `E:/OOTRemake/work/r14-longshot/shots/`: game-longshot.png,
  game-hookshot.png, game-no-runtime.png, play-no-game.png, settings-discord.png.
  Reviewed at 1280×860: labels/paths and Discord buttons fit, no horizontal overflow.
- Browser-tool incident: `headed:false` with app.path opened a blank visible Chrome
  despite the request. Closed it immediately when notified; PID 47100 was absent.
  Reported the tool defect. All captures used a replacement Chrome explicitly started
  with `--headless=new`, verified via actual PID 17704 command line, connected over CDP.
  Both UI and browser services were stopped; PID 17704 was then absent.
- Seed101 fallback launcher: CLAWSHOT_DRY_RUN=1 printed the expected command only.
  No agent boot, chest, controller-icon, save-persistence or Linux in-game result is claimed.
- Claude reports boot check **ls101 passed**: Longshot rc.2, seed101 as the only mod,
  92 files, crash=0, save mounted. This establishes headless loading, not the chest result.
  Kareem's app check was handed off through
  `E:/OOTRemake/work/r14-longshot/Start Clawshot (Longshot test).bat`.
  Worktree edits were frozen during his app session. Kareem's later 09:35–09:39 app
  result passed; the evidence is recorded below.
- Pre-#24 full synthetic gate: **1262 passed, 140 skipped**, 606.37s, workers=3.
  Superseded by the post-#24 and final followup gates below.

Post-#24 full synthetic gate: **1269 passed, 140 skipped**, 583.79s, workers=3.
Final native dump gate: **138 passed, 1271 deselected**, 4892.73s, workers=3,
with the actual RomFS, repaired v131072 NUP and unchanged r13 integrated fixture.
The runner released `gate.lock` in `finally`; release was posted immediately.
Coverage inspection established that ZIP/source capsule tests are synthetic; this native
stage uses unchanged generator/resources/formats, not Play or dump UI detection.
The later default-build and missing-path edits were therefore applied after the app closed,
with synthetic proofs and focused checks. Their final full synthetic gate then passed
**1275 passed, 140 skipped**, 579.33s, workers=3, `OOT_*` unset and neither game running.
It followed E's short census and C's synthetic stage in Claude's explicit order; the runner
released the lock and B immediately posted release for C's dump stage.

Followup focused command:
`uv run pytest tests/test_pack_hookshot.py tests/test_app.py tests/test_app_play.py tests/test_ui_games.py tests/test_ui_first_run.py`
→ **91 passed**, 13.61s. Covers recorded-default preference, unavailable-default fallback,
unsupported-default refusal, directly pinned builds, missing versus wrong-kind paths and HTTP persistence.
Final format/lint and JS syntax checks passed after removing one extra import-group separator reported by Ruff.

Actual headless UI followup used invented fingerprint-only files and synthetic non-executable
game binaries; no game files or execution. It displayed an older recorded default despite a
newer available build, honored a directly picked newer build, and showed the exact Not found
message versus the existing wrong-kind advice. `shots/game-not-found.png` and
`shots/game-preferred-default.png` were reviewed; no horizontal overflow or external requests.
The followup also reproduced an own guard regression: a picked base/romfs layer normalized
while its successful dump detection redirected to the enclosing root. Scoping the stale-game
guard to game selection restored the existing dump-root redirect. Delaying the synthetic HTTP
response reproduced Checking before, then Verified/root after. `shots/game-layer-root.png`
records this synthetic UI regression, not native-data validation. All smoke services were closed.

### Added #24 options preservation

Kareem requested this during the track. `prepare_user` initializes only a newly created
seed user, reads the newest source-ID folder by mtime (name breaks ties), exclusively
creates option.sav/account.sav and never visits slot_NN. An existing user is retained
without copying anything. Other I/O errors are not hidden; only missing source files skip.
`start_game` returns process plus copy/missing result; pack prints it and UI shows it.
Normal game options.ini files are untouched.

Focused regression run:
`uv run pytest tests/test_pack_options.py tests/test_pack_loader.py tests/test_ui_games.py`
→ **49 passed, 1 skipped** (Linux-only proc-link check on Windows), 3.06s.
Synthetic folders prove newest-ID selection, both files/partial/absent source,
no source writes or slots, once-only behavior and existing-seed preservation.
Actual headless UI smoke used real detection, digest plan and prepare_user with only the
process boundary replaced; it copied synthetic option.sav, skipped missing account.sav,
and displayed that result. Screenshot `shots/options-missing-source.png`.
No real account/options files were copied by the agent.

## Kareem check

**PASSED — Kareem, Longshot v3.0.0-rc.2, 2026-11-13 09:35–09:39.**
The staged checklist estimate was 8–12 minutes; Claude performed the boot check, never this agent.

1. From this worktree, run `uv run python -m clawshot.ui` (or
   `uv run --extra ui python -m clawshot.ui` for the embedded window). No `--no-open`:
   that mode deliberately disables Play.
2. Game → Hookshot or Longshot → Browse `E:/Games/LongshotLauncher`, Detect.
   Expect Longshot `v3.0.0-rc.2` (or the launcher's available default; numeric fallback), mods supported.
3. Generate → My seeds → Find seeds → `E:/OOTRemake/work/r14-longshot/ingame`.
   View seed 101; hash **52B614F085D9**, defaults (`CS1`), 165 shuffled rewards,
   92 resources, 31 search spheres. Never use either community seed 23 for this check.
4. Close any running Hookshot or Longshot, then press Play. Expect `bin/longshot.exe`,
   `--user E:/OOTRemake/work/r14-longshot/ingame/seed-101/user`, only seed/romfs through
   HOS_MODS, overlay absent, LONGSHOT_NO_UPDATE_CHECK=1. The app's user folder does not
   exist before first Play, so Play initializes options/account only, never progress slots.
   Choose New Game in an empty slot. The transferred save backups are not needed.
   **Before opening the chest, confirm your game options carried over (e.g. Invert Jump,
   camera speed and Ocarina controls).** Compare with the selected Longshot build's normal
   options; Play's result names any missing option.sav/account.sav it skipped.
5. Walk child Link to Mido's house; open the **far-right chest**.
   For this seed 101 expect **Rupees (50)**; confirm the rupee counter increases by 50,
   not only pickup text. No other chest contents belong in this checklist.
6. Observe controller-button icons in ordinary item/dialogue text with the controller
   in use. Record actual icons (controller versus Switch), independently of ocarina prompts.
   Longshot rc.2 is expected to show the controller's icons; Xbox prompts passed this check.
7. Save and Continue; verify this seed's progress persists. Quit. Confirm normal saves
   and `E:/Games/LongshotLauncher` were not changed by Clawshot.
8. Attach only observed resource-loading evidence and result: in output/longshot_log.txt,
   `mods: <file> <- <path under this seed>` for
   `Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs`, plus chest/inventory
   result, runtime version and icons seen. A mod mount alone is not gameplay proof.

### Played result and loading proof

Kareem: “Seed loads fine, settings do carry over including Ocarina controls. Button
prompts are Xbox.” He also confirmed open chests, 60 rupees and the sword after reload.
Claude verified the Mido rewards against the spoiler: the required **far-right chest**
gave Rupees (50); all four opened chests matched. The player-facing position is far right,
not the OoT Randomizer label used in the original draft.

Claude's supplied runtime proof: `longshot v3.0.0-rc.2`, exactly one mod from seed101,
`KokiriForest_Child_Dynamic` served from this seed, saves mounted under seed-101/user,
zero crashes. Save observations: slot_01 held sword and 10 rupees; slots 02/03 held the
sword and 60 rupees. `account.sav` was copied at 09:35. This proves actual app Play,
option carryover, ordinary-text controller icons, shuffled reward and save persistence for this case.
These are Kareem's play and Claude's supplied log/save observations, not an agent game run.
No replay or decoded save copies were requested or performed to confirm their report.

The app initially restored an old nonexistent NUP path. Its vague kind error was a
pre-existing main behavior, now changed to `Not found: <path>. Choose your romfs folder or .nup again.`
Existing wrong-kind files retain their old advice. Both cases have synthetic HTTP regressions.
Linux, other runtime versions and every item/route combination are not certified by this one Windows result.

Fallback launcher for Claude/Kareem:
`E:/OOTRemake/work/r14-longshot/Longshot seed 101 check.bat`, copied from the new
Longshot template. It uses a separate **diagnostic-user**, never the app's user folder,
so running it cannot preempt the app's first-Play options initialization. Acceptance
requires **app Play**, not this diagnostic fallback.

The initially staged community-seed copy, launcher and temporary scripts were deleted
at Kareem's direction before any game launch. Played originals and saves were untouched.
No community-seed chest contents are retained in this round file.

### Seed-101 staging evidence

`uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 101 --out E:/OOTRemake/work/r14-longshot/ingame/seed-101/seed`
completed under the shared gate lock, workers=1 while Kareem was playing: 165 shuffled,
31 search spheres, 92 resources. The spoiler stores only 30 nonempty item spheres; the
manifest counter uses the CLI/search total, as the UI worker does.
`app.library.write_manifest` recorded the generated seed's actual `pack.tree_digest`;
`inspect_seed` verified it. Full SHA256:
`52b614f085d9a75400a99757cbe2f7eabf9a3c25d2ecc7e83e92a3a639c695b8`.
Full settings string is in `clawshot-seed.json`; no seeded files were edited.
The initially empty `user` folder was removed after #24 arrived: app Play must create it
to copy options once. Stage logs and generated files stay outside the repo.

## Handoff

- `6c753b3`: dual-game Play, Discord copy, per-seed options (#23/#18/#24).
- `5689a79`: prefer the recorded launcher default; cite `builds.json`.
- `39f99f4`: distinguish absent dump paths and preserve layered-root detection.
- `e9f7a13`: played Longshot acceptance, Xbox prompts and player-facing checklist.
- All requested behavior and gates complete. No seed working-set change, version bump,
  game boot by this agent, game-folder writes by this agent, merge or push.
- Temporary smoke prototypes, test profiles and gate-controller scripts were removed;
  owner launchers, played seed/user, screenshots and gate logs remain outside the repo.
