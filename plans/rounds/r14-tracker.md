# Round 14 Track A — item tracker (#16)

Base: `ffea543`, Clawshot 0.2.0. No version change. Proposed by cs14a (openai-codex/gpt-6.1-sol), 2026-11-13.

## Scope and contracts

- New headless `clawshot.tracker` reads a seed and read-only save; UI adapter and independent static assets add the Tracker tab and compact OBS view.
- Dungeon keys first: remaining and acquired totals use the named `DungeonInfo` leaves (03-game-data section 44), not inferred chest counts.
- Chest collection uses named `IsTreasureBoxOpen.<decimal Hash>` Bools. `Save.is_set` is restricted to audited placement families. Section 44 supersedes section 6's old blanket raw-Hash claim.
- GPL reference `work/refs/sloperina-FINDINGS.md` supplies facts only (sections 1, 5.7, 5.8); no code copied. The Apache manual tracker supplies icon/cell ideas only, no assets or code copied.
- No game starts, game-folder writes, network requests from the UI, version bump, merges or pushes. Research/save copies/screenshots stay in `E:/OOTRemake/work/r14-tracker/`.
- Shared-file hooks in server.py/index.html/app.js; two folder-picker kinds in dialogs.py and explicit UI release-asset additions. Track B owns Game/Play. Claude requested A update README/docs/ui tracker mentions in the final integration commit, preserving B's Longshot prose.

## Provisional implementation choices

- Live polling reads the saved state, not process memory. Unknown/missing fields and unaudited collection contracts remain unknown rather than invented completion.
- OBS follows the configured tracker session, with controls absent and location spoilers never included. Its per-run token must be kept private and renewed after app restart.
- Current inventory uses pouch stock rather than acquisition history; songs use their permanent acquired flag.
  Magic reads saved meter capacity, including a meter granted by a spell rather than a separate upgrade item.
- Bottle count/current contents come from the native five `BottleA`–`BottleE` Struct slots, not `IsGet` history.
  Native Struct/Enum links and copied-save values were independently traced in external `probe6.py`–`probe8.py`.
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
- Actual CLI `--no-open`, direct Playwright `headless=True` and Chrome `--headless=new`: **passed**.
  Save rewrite updated displayed keys without reloading (`performance.timeOrigin` unchanged);
  explicit spoiler consent worked; OBS stayed redacted while the tab's spoilers were on; OBS had
  no controls; transparent background was RGBA zero; 52 icons loaded from the local dump.
  All 130 page requests stayed on the loopback origin. No omp browser tool or visible window used.
- Six tab/OBS screenshots (text and local icons) are under `work/r14-tracker/shots/`, never committed.
  Initial smoke failures were test-harness issues: string predicates conflicted with CSP, then
  same-document fragment navigation retained the first OBS options. Fixed the harness to use
  CSP-safe predicates and separate Browser Source documents; app CSP was never weakened.
  The first uv-launched child server was explicitly stopped; final smoke launches/terminates
  the Python CLI directly and leaves no listening server.
- UI source-release command produced external `release-smoke/Clawshot-0.2.0.zip`: 233 files,
  required tracker code/assets/docs present, no PNG/BNTX/ZS/save/log payload. Version unchanged.

Full synthetic and dump suites remain queued behind ready B/C/D stages at this point.
Every heavy stage atomically claims `work/rounds/r14/gate.lock` and releases between stages.
The external `gate.py` matches exact case-insensitive `hookshot.exe` / `longshot.exe` names
to choose workers 3 or 1 at that stage's start; LongshotLauncher.exe is excluded. No suite deadline.
No generator working-set file was added: icons read RomFS/NUP directly into user app-data cache.
The requested r13 `dump-fast-start-integrated` fixture remains the input; no replacement needed.

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
