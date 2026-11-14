# Round 14 Track A — item tracker (#16)

Initial base: `ffea543`; final integration base: `cbc7f26`, Clawshot 0.2.0. No version change.
Proposed by cs14a (openai-codex/gpt-6.1-sol), 2026-11-13. Assigned automated gates passed;
ready for maintainer merge. The staged game comparison is not claimed played.

## Scope and contracts

- New headless `clawshot.tracker` reads a seed and read-only save; UI adapter and independent static assets add the Tracker tab and compact OBS view.
- Dungeon keys first: remaining and acquired totals use the named `DungeonInfo` leaves (03-game-data section 44), not inferred chest counts.
- Chest collection uses named `IsTreasureBoxOpen.<decimal Hash>` Bools. `Save.is_set` is restricted to audited placement families. Section 44 supersedes section 6's old blanket raw-Hash claim.
- GPL reference `work/refs/sloperina-FINDINGS.md` supplies facts only (sections 1, 5.7, 5.8); no code copied. The Apache manual tracker supplies icon/cell ideas only, no assets or code copied.
- No game starts, game-folder writes, outbound UI requests, version bump, merges or pushes. Research/save copies/screenshots stay in `E:/OOTRemake/work/r14-tracker/`.
- Shared-file hooks in server.py/index.html/app.js; two folder-picker kinds in dialogs.py and explicit UI release-asset additions. Track B owns Game/Play. Claude requested A update README/docs/ui tracker mentions in the final integration commit, preserving B's Longshot prose.

## Provisional implementation choices

- Live polling reads the saved state, not process memory. Unknown/missing fields and unaudited collection contracts remain unknown rather than invented completion.
- OBS follows the configured tracker session, with controls absent and location spoilers never included. Its per-run token must be kept private and renewed after app restart.
- Current inventory uses pouch stock rather than acquisition history; songs use their permanent acquired flag.
  Magic reads saved meter capacity, including a meter granted by a spell rather than a separate upgrade item.
- Bottle count/current contents come from the native five `BottleA`–`BottleE` Struct slots, not `IsGet` history.
  Native Struct/Enum links and copied-save values were independently traced in external `probe6.py`–`probe8.py`.
  **[INFERENCE]** `IsValid` is interpreted as ownership from those native links and copied values;
  current contents are the native Enum choices. No in-game bottle acceptance is claimed.
- Heart-meter units are **[INFERENCE]** quarter hearts (early saves hold MaxLife 12 for three starting hearts).
  Heart-piece stock is reported raw; lifetime-total versus remainder semantics are not claimed.
- Unset raw pickup flags stay unknown where replacement persistence is uncertified. Shops and unaudited
  swap-only gifts do not pretend to have a permanent collected state. No new gameplay policy/default was chosen.
- Existing save-flag layouts can establish a mismatch or consistency, not seed identity. Matching layouts
  never certify a seed number; the UI says so. The core has no dependency on D's progressive family labels.

## Field sources

Each read has a source citation in `tracker/state.py` or `seeds.py`:

| Save fields | Meaning source |
|---|---|
| `PouchData.<actor>.StockNum`, `IsGet.<actor>` | 03-game-data sections 6/19; FINDINGS section 1; native pouch/GameData audit in `probe2.py`–`probe8.py` |
| Upgrade actor families (strength, scale, wallet, bags, quiver) | FINDINGS section 5.7; native saved-name audit |
| `PlayerStatus.MPMax`, `MaxLife`, `CurrentRupee` | Section 12 / playtest R10-DIGGING / native GameData and save-copy audit; FINDINGS section 1 for magic units |
| Bottle owned Bools and content Enums | Native Struct 4152414078, `BottleA`–`BottleE`, independently recovered member names and leaf hashes; `probe6.py`–`probe8.py` |
| `DungeonInfo.*.SmallKeyNum`, `SmallKeyTotalNum`, `IsGetSmallKeyOnce`, boss/map/compass Bools | Section 44; FINDINGS sections 1/5.8 |
| `IsTreasureBoxOpen.<Hash>` | Section 44's corrected chest collection contract |
| Audited placement flags and gift/scrub completion flags | Sections 19/23/44 and existing generator rule data |
| Slot path/time selection | FINDINGS section 1 and `pack/runtime.py`'s `<root>/user` launch contract |

No GPL implementation was copied. The Apache tracker supplied cell/file-name ideas only.
No normal-boot inventory field exists; normal boots are not represented by an invented flag.

## Evidence

### Read-only save audit

`E:/OOTRemake/work/r14-tracker/audit_saves.py` copied each `progress.sav` before reading it;
originals were never modified. Raw values and copy paths are in external `raw-save-audit.json`.

| Copied source / slot | Forest held / found | Fire held / found | Tokens | Expected independent check |
|---|---|---|---|---|
| `2026-11-13_084401-longshot-transferred`, all six slots | 0 / 5 | 0 / 8 | 30 | Forest/Fire/Water boss key, map and compass true; Water 0 / 4 |
| `2026-11-10_1335-r11-key-door`, slot_01 and slot_05 | 1 / 2 | 0 / 0 | 15 | One spent Forest key remains included in acquired total |
| Same historical door backup, slot_03 | 1 / 1 | 0 / 0 | 15 | Earlier acquired total remains distinct |

All inspected transferred/door slots have Mido's far-right chest named-open Bool true while
its raw placement Hash is false: regression coverage must enforce the named accessor.
The keys-23 run's user folder currently has account/option only, no progress slots; Kareem's
brief play was unsaved (Claude, 2026-11-13). It cannot supply a saved-state comparison.
No seed-23 placement details belong in this acceptance record.

`uv run python E:/OOTRemake/work/r14-tracker/verify_states.py` then exercised the actual
`load_seed`/`build_state` path against those copies and private seed 102's totals: assertions
passed for Forest remaining/acquired/total and tokens. The historical saves are **not** said
to belong to private 102; both correctly report unverifiable seed identity.

| Copied save | Grapple tier | Strength / scale / wallet tiers | Meter / pieces | Current bottles |
|---|---|---|---|---|
| Longshot-transferred slot_00 | Longshot 2 | 1 / 1 / 3 | MaxLife 36 → 9 hearts; pieces 3 | 2: Blue Fire, Fairy |
| Historical Forest-door slot_01 | None | 1 / 1 / 1 | MaxLife 24 → 6 hearts; pieces 0 | 2: Bug, Empty |

The transferred save has MPMax 240 despite `IsGet.Item_FairyBless_MP=false`: a capacity read
correctly shows a meter rather than incorrectly reporting none from that acquisition flag.

### Runtime and gates

Automated status before full gates:

- `uv run ruff format --check`: 346 files already formatted. `uv run ruff check`: all checks passed.
  First lint run printed three SIM905 literal-allocation findings; replaced the literal splits,
  removed an incidental schema-presence assertion, and reran successfully.
- Focused `uv run --extra ui pytest tests/test_tracker_state.py tests/test_tracker_saves.py
  tests/test_tracker_http.py tests/test_tracker_icons.py tests/test_pack_nup.py`: **106 passed**.
  Fixtures are synthetic; tests cover ownership/history, every mapped field, spent/found keys,
  collection contracts, spoiler consent/redaction, slot choice/change, partial writes, cache
  invalidation, NUP reads, both GOB layouts, malformed textures and actual synthetic BC1 pixels.
- While waiting for the shared gate, added requested field-boundary coverage for all ammo counters,
  empty ammo versus bag ownership, coexisting upgrades (highest tier, not sum/history), and spell-only
  magic. `uv run pytest tests/test_tracker_state.py`: **15 passed**.
  The first spell test correctly returned unknown history because MPDouble's Bool was absent;
  the real copied-save audit confirms both native upgrade-history Bools exist and are false.
  Included both in the synthetic input, preserving unknown semantics; targeted rerun passed.
- Actual CLI `--no-open`, direct Playwright `headless=True` and Chrome `--headless=new`: **passed**.
  Save rewrite updated displayed keys without reloading (`performance.timeOrigin` unchanged);
  explicit spoiler consent worked; OBS stayed redacted while the tab's spoilers were on; OBS had
  no controls; transparent background was RGBA zero; 52 icons loaded from the local dump.
  All 130 page requests stayed on the loopback origin. No omp browser tool or visible window used.
- Six primary tab/OBS screenshots (text and local icons), plus an opaque alpha-control capture,
  are under `work/r14-tracker/shots/`, never committed.
  Initial smoke failures were test-harness issues: string predicates conflicted with CSP, then
  same-document fragment navigation retained the first OBS options. Fixed the harness to use
  CSP-safe predicates and separate Browser Source documents; app CSP was never weakened.
  The first uv-launched child server was explicitly stopped; final smoke launches/terminates
  the Python CLI directly and leaves no listening server.
- Pre-rebase UI source-release command produced external `release-smoke/Clawshot-0.2.0.zip`: 233 files,
  required tracker code/assets/docs present, no PNG/BNTX/ZS/save/log payload. Version unchanged.
- Additional actual CLI/HTTP smoke (`real_http_smoke.py`): copied transferred save, explicit slot_00,
  repaired NUP selected through `api/detect`, and a real 127,960-byte Longshot-icon PNG served.
  Asserted Forest 0/5/5, Fire 0/8/8, Water 0/4/4, Longshot tier 2, wallet tier 3, two bottles
  (Blue Fire/Fairy), MaxLife 36/9 hearts, pieces 3, tokens 30; copied-save hash and mtime unchanged.
  Selecting the audited old seed-8 pack copy with that save produced the expected explicit mismatch
  warning (four added gift flags expected, zero present). Matching no-added-flag layouts remained
  unverifiable, not falsely identified. No game, browser or original-save writes in this smoke.
- Explicit transparent-canvas smoke (`alpha_smoke.py`, direct Chrome headless): rendered PNG
  corner alpha was **255 with transparency off, 0 with it on**, with the same transparent browser
  canvas. This tests actual compositing, not just the body's computed CSS. The transparent OBS
  screenshot was replaced with this RGBA capture. No visible browser or game launched.

### Main integration (requested by the coordinator, implemented by cs14a)

Rebased `r14/tracker` onto main `58ba776` after B's merge, without stash. The only conflicts were
the additive round-14 notes in `plans/05-ui.md` and `dialogs.KINDS`. Kept both plans and combined
the tracker picker kinds with B's canonical `game` kind, not the obsolete `hookshot` kind.
B's Game/Play implementation remains intact: `paths.game`, `game-folder`, `detect` with `game`,
generation with `game`, and `play` with `game`. The tracker still reads saves independently of runtime names.

Post-rebase verification:

- `uv run ruff format --check`: **349 files already formatted**; `uv run ruff check`: **all checks passed**.
- Tracker state/save/HTTP/icons, NUP, shared UI/game/dialogs, Play, library and source-release suites:
  **153 passed in 26.77s**.
- Repeated actual CLI plus direct Playwright Chrome `headless=True` / `--headless=new` smoke:
  restored the Longshot selection via the saved `game` preference; live save refresh without reload,
  spoiler-free OBS, no OBS controls, **52 loaded local icons**, **130 loopback-only requests**, no page errors.
  Regenerated and visually inspected the tab and OBS captures without opening a visible browser.
- Repeated transparent-canvas smoke: **opaque corner alpha 255; transparent corner alpha 0**.
  The transparent source PNG also composites correctly; the tool preview showed opaque glyph blocks.
  Reported that preview defect rather than changing the app or screenshot.
- Authorized full synthetic on frozen `d17fa2d`: **1369 passed, 140 skipped in 866.22s**,
  exit 0; 1509 collected. The stage removed `OOT_ROMFS`, `OOT_NUP` and `OOT_DUMP`, detected
  no exact game processes, and used **3 workers** without a deadline.
  External log: `work/r14-tracker/synthetic.log`. The owned lock was released and the
  handoff explicitly posted to D's synthetic retry, not C.

### Final main + D + A integration

Actual rebase onto `cbc7f26` replayed all three A commits cleanly, without stash. Runtime/test
source is pinned to `22b016c` (`a68ed80` implementation, `66ee6c6` field boundaries).

- Focused tracker/shared UI/Play/library/release checks: **153 passed in 35.15s**.
- Format: **360 files already formatted**; lint: **all checks passed**.
- Repeated strict headless tab/OBS smoke: **52 icons, 133 loopback-only requests**, live refresh,
  spoiler redaction, no OBS controls and no page errors. Alpha compositing again returned **255/0**.
  Tab and opaque OBS control captures were visually inspected.
- Repeated real copied-save CLI/HTTP smoke: key totals, inventory, bottles and mismatch warnings
  passed unchanged; repaired-NUP PNG served; copied save hash/mtime unchanged.
- First combined native attempt: **122 passed, 18 setup errors, 1483 deselected in 2912.58s**.
  Full error values remain in external `dump.log`; the lock was released and E notified.
  The old r13 layered cache lacks five newly required progressive packs:
  `Item_BombBag_Large`, `Item_BulletBag_Large`, `Item_FairyBless_MP`,
  `Item_FairyBless_MPDouble`, `Item_Quiver_Large` (all `Pack/Actor/*.pack.zs`).
  No tracker assertion failed; these errors arise while constructing the `OOT_DUMP` cache fixture.
- Read-only preflight against the current catalogue: **1248 required files**; accepted D fixture
  `work/rounds/r14/dump-progressive-cs14d-1e6cde0` has **zero missing**, matches D's proof inventory,
  and has the same build digest as the repaired NUP. No extraction, game write or product edit.
  The external retry runner selected this complete fixture and a fresh `dump-retry.log`,
  retaining the original failure.
- Coordinator-authorized **full 140-case retry passed: 140 passed, 1483 deselected in 5403.07s**,
  exit 0, on unchanged `22b016c`. Three workers, no exact game processes, no supervisor deadline.
  Accepted fixture build digest:
  `fc09c4af707a0ca092188cf014f6fdf3d40514def773f097b798f52f9f28bc93`.
  The lock was released and the pass posted. Subsequent edits are round-file evidence only;
  runtime and tests remain exactly those verified.

### Serialized handoff

The coordinator merged C and D into `cbc7f26`, then authorized A's rebase, light checks and
native gate. After accepting the printed stale-fixture cause, the coordinator authorized
the complete cause-directed retry. That retry passed and A released the lock.

The coordinator merges A's final evidence head before E's full gates. This track does not
merge or push; E owns its own rebase, D/E proof and gameplay packet.

The earlier detached trial onto `e7e2bb1` replayed both A commits with **zero conflicts**;
the disposable worktree was removed without changing the original branch or notes.

Every heavy stage atomically claims `work/rounds/r14/gate.lock` and releases between stages.
The external `gate.py` matches exact case-insensitive `hookshot.exe` / `longshot.exe` names
to choose workers 3 or 1 at that stage's start; LongshotLauncher.exe is excluded. No suite deadline.
No generator working-set file was added: icons read RomFS/NUP directly into user app-data cache.
The initial unchanged r13 fixture is insufficient after D; the cause-directed retry uses D's
already accepted 1248-file fixture. There is no tracker-specific working-set expansion.

### Icon implementation and dependency

Own bounded BNTX parser and NVIDIA block-linear deswizzle from the references cited in `bntx.py`.
Tegra X1 `NX  ` and actual Switch 2 `Ounc` sector orders are distinct: Ounc needs Turing order;
using X1 alone scrambles strips. NX synthetic coverage is not a real Switch 1 dump certification.
Runtime ASTC/BC decoding uses optional texture2ddecoder 1.0.6, MIT, with permissive bundled
codecs; its modified-zlib Crunch acknowledgement is included in NOTICE.

Read-only real-dump icon smoke decoded all 129 Icon files from both RomFS and repaired NUP
to identical PNGs (external `smoke_icons.py`, `icons/smoke-report.json`); contact sheet inspected.
All were Ounc v4.1.1 ASTC 4×4 sRGB. Missing decoder/source/texture falls back to text.
Songs/stones/medallions have no Icon-directory texture and intentionally use text without an error.

PyPI metadata and source licence checked:
[distribution/wheels](https://pypi.org/project/texture2ddecoder/1.0.6/),
[MIT licence](https://github.com/K0lb3/texture2ddecoder/blob/master/LICENSE).
cp311-abi3 wheels cover Windows x86/x64/ARM64, macOS x64/ARM64, Linux manylinux/musllinux
(x86/x64/ARM and additional architectures). Windows execution checked; Linux/macOS not executed.
The ui extra is optional as assigned. Current Linux/macOS starters omit it, so use text fallback
or explicitly install the extra; no extra launcher dependency/policy was silently added.

## Kareem acceptance

**Longshot only** (Kareem, 2026-11-13). Claude owns boot checks (`GAME=longshot tools/bootcheck.sh`).
The initial community-seed staging was removed on Claude's instruction before any game start;
its location-specific checklist and reference launcher were removed too. Private small-keys-anywhere
seed **102** was generated with the actual app Jobs pipeline (165 shuffled checks, 91 resources,
26 spheres, hash `6EB1DC9A2079`; source 0.2.0, no progressive patch). Gate held only for generation,
workers 3, 38 seconds; no game start.

- Output: `E:/OOTRemake/work/r14-tracker/ingame/tracker-102`, empty isolated `user`.
- Full checklist: `work/r14-tracker/ingame/CHECKLIST.md`; **10–15 minutes**.
- Reference launcher: `Tracker 102 Longshot reference.bat`, copied/adapted from the current
  **Longshot** central template, CRLF. Actual dry run selected Longshot `v3.0.0-rc.2`,
  `--user <tracker-102>/user`, `HOS_MODS=<tracker-102>`, overlay unset; no game launched.
- Primary acceptance is **integrated app Play**, not that fallback launcher: find/view private 102,
  Play Longshot, New Game, Tracker → Use selected seed, default Play save folder.
- Save at the opening, then open Mido's far-left and far-right chests (this private seed: Forest
  keys). Save after each: Forest 0/0 → 1/1 → 2/2 out of 5; Kokiri collected count increments.
  Third from left gives Kokiri Sword; save shows ownership while key counts stay 2/2.
- Leave/re-enter and Save and Continue: counters persist; next save refreshes without a reload.
  Verify default spoiler absence and optional OBS redaction.
- Require the real Longshot log's `mods: Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs
  <- <tracker-102/seed path>` plus the observed pickups/tracker updates, one mod only, overlay absent.

**Not played in game by this track.** Claude boot-checks and Kareem performs acceptance. No changes
to original seeds/saves, Hookshot/Longshot folders, or normal user profiles.
