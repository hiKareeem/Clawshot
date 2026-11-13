# Round 14 Track B — Longshot (#23), Discord copy (#18), game options (#24)

Base: `ffea543`, Clawshot 0.2.0. No version bump. Track owner: cs14b,
`openai-codex/gpt-6.1-sol`. Work in progress; Claude reviews/merges first.

## Scope and decisions

- One optional `game` path across application preferences, generation protection and Play.
  Read migration from saved `hookshot` retains the chosen path; an existing `game` wins.
- Detect Hookshot and Longshot game folders without executing binaries; preserve the
  HOS_MODS capability probe. Longshot Launcher selection resolves the newest available
  build, not the launcher's default. The chosen launcher path remains saved so a later
  update can be detected. Explicitly choosing a build pins that build.
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
  **[INFERENCE]** Controller icons may remain in ordinary text on Longshot. This is not
  an in-game observation. Hookshot 2.1.0's recorded Switch-icon fallback stays documented separately.

## Coordination

Thread `cs-r14`, plain posts as cs14b. Track A owns tracker and small hooks in shared
server/static files; this track changes Game/Play and settings-copy controls. Posted
canonical `game` key contract and requested first serialized full-gate slot. Initial
shell tilde-path lookup failed; PATH `bermuda` resolves the same executable.

## Verification

- `uv run ruff format --check`: 335 files already formatted.
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
  No boot, chest, controller-icon, save-persistence or Linux in-game result is claimed.

Full synthetic and native dump gate results follow after their serialized stages finish.

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

**Pending Kareem; estimate 8–12 minutes including startup.** Claude boot-checks first
with `GAME=longshot tools/bootcheck.sh`; this track never boots a game.

1. From this worktree, run `uv run python -m clawshot.ui` (or
   `uv run --extra ui python -m clawshot.ui` for the embedded window). No `--no-open`:
   that mode deliberately disables Play.
2. Game → Hookshot or Longshot → Browse `E:/Games/LongshotLauncher`, Detect.
   Expect Longshot `v3.0.0-rc.2` (or the newest installed build), mods supported.
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
5. Walk child Link to Mido's house; open the **top-left chest** only.
   For this seed 101 expect **Rupees (50)**; confirm the rupee counter increases by 50,
   not only pickup text. No other chest contents belong in this checklist.
6. Observe controller-button icons in ordinary item/dialogue text with the controller
   in use. Record actual icons (controller versus Switch), independently of ocarina prompts.
   Controller icons are an inference from Claude's merge log until this observation.
7. Save and Continue; verify this seed's progress persists. Quit. Confirm normal saves
   and `E:/Games/LongshotLauncher` were not changed by Clawshot.
8. Attach only observed resource-loading evidence and result: in output/longshot_log.txt,
   `mods: <file> <- <path under this seed>` for
   `Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs`, plus chest/inventory
   result, runtime version and icons seen. A mod mount alone is not gameplay proof.

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
