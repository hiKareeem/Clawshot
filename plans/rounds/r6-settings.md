# Round 6, Track B: settings (cs6b)

Branch `r6/settings`. Read AGENTS, README, plans 00–04, decisions, every round-5 report,
Round 6's opening and Round 5's shared-file rules. No game, launcher, window or build started.
`E:/OOTRemake/work/r5-seed/`, save backups and the dump remain untouched/read-only as required.
No dependency change, merge, push, stash or other-terminal command.

## Item 1 — settings strings

`Settings.to_string()` / `from_string()`: canonical versioned `CS1` strings. `CS1` selects the generator's
current defaults; nondefaults are sorted compact JSON, zlib-compressed, URL-safe base64 without padding.
Generator defaults live in `data/settings.toml`; logic defaults retain their single existing definitions in
`data/world/{settings,world}.toml`. Seed, string, generator version and world data must all match for replay.
All generator fields are encoded, including slices and effective item/location restrictions. Unknown versions,
corrupt payloads and malformed fields are refused. Unordered lists and nested JSON map order normalize.

CLI `--settings STRING`; explicit flags override the string, individual `--logic` entries overlay its logic,
and bare `--skip` clears skips. `--print-settings` prints then exits without requiring dump/seed/output.
Gift-expanded spoiler strings trigger gift setup again on replay, preserving the reviewed gift patch steps.
The separately committed one-line `spoiler()` change records `settings_string` alongside `settings`.

Checks:
- `uv run pytest tests/test_settings.py tests/test_generate.py tests/test_generate_fast_start.py -q`:
  **30 passed**, including a real synthetic fill after string decode.
- Actual `python -m clawshot ... --print-settings`: exit **0**, one CS1 string, no dump read/output needed.
- `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_settings_dump.py -q -s
  --basetemp E:/OOTRemake/work/r6-settings/pytest-item1`: **1 passed**. Two actual CLI processes, different
  hash seeds, Chest+Gift slice, Mido skip, free travel on/return guarantee off: every overlay/spoiler byte equal.
  The second process used the first spoiler's expanded string; both emitted the adult pedestal patch.
- First dump attempt stopped before execution: WinError 3 printed missing parent
  `E:/OOTRemake/work/r6-settings`. Created that external parent; one cause-aimed rerun passed above.
- No LSP server is installed for Python; references were inspected with the known-symbol search fallback.

## Item 2 — song mode and gift chest evidence

`Settings.songs` / CLI `--songs song|anywhere`; default `song`, from the same default catalog and included in strings.
Default: songs only on song checks and those checks accept only songs. `anywhere`: all twelve songs may leave
song checks, still respecting Shop native-display and dungeon-item restrictions.

Reviewer direction (Claude, 2026-11-08, responding to 10:26 post) supersedes the initial strict per-song proposal:
all twelve share `Item_Melody_*` → pouch → `IsGet`; Storms was acquired and played from a chest.
**The other eleven are inferred, not individually verified.** This exception is opt-in; no default changed.
Non-song gift items still leave gifts only if already a vanilla chest item or individually listed with a source
under `settings.toml [chest_verified]`: Fairy Ocarina and Song of Storms are the observed entries so far.
The effective gift policy is rebuilt on replay, so a decoded song-only string can switch to anywhere without
retaining stale derived song restrictions.

Checks: `uv run pytest tests/test_settings_songs.py tests/test_settings.py tests/test_gifts.py -q`:
**33 passed**. Sixty synthetic actual fills verify both song modes, Fairy Ocarina into chests, unverified letter
kept in gifts, inferred Lullaby allowed into chests only in anywhere mode, and settings round trips.

Requested warp experiment: `E:/OOTRemake/work/r6-settings/chest-ocarina-minuet/`, unrun copied launcher
`Test - chest-ocarina-minuet.bat`, and `minuet-check.md`. New game, isolated user, release EXE only.
Walking into Mido's house: far-right Hash `9725242744547055868` gives Fairy Ocarina; far-left Hash
`4555665598794293658` gives Minuet of Forest. Independent written-tree diff verifies only these drops in both
age copies; allocation checks pass. Child **510884 → 510976**, entry **511240**; Adult **516036 → 516128**,
entry **516392**. No game or batch executed.

**Kareem: run that new-game launcher, obtain both chests, check Minuet learned, leave the house and play it,
accept warp: does child Link reach Sacred Forest Meadow's warp pad, and does learning persist after Continue?
Record model/text and the `from the overlay` log.** Until then the warp result remains unverified.

## Item 3 — prices and wallet predicates

`shop_prices = vanilla|affordable`, default vanilla; `cheap_deku_shield = true`, provisional default.
CLI `--shop-prices` and `--[no-]cheap-deku-shield`; both participate in strings/spoilers.
Affordable makes every shuffled shop offer **exactly 10**, including unchanged placed actors.
The cheap-shield rule follows the actual Deku Shield sold anywhere in Kokiri shop, not the original slot
when it contains another item. It also applies with shops unshuffled. Other shops and masks stay untouched.

`GoodsList.PriceOffset = target - item base price`. An exact-price setting clears conditional discounts:
the dump has one such list (Market Bazaar Hylian Shield, soldier-gate discount **-20**); retaining it at 10
would give a negative price. Vanilla-price mode retains that discount, original stock and release predicates.
No sale model, message, pouch, restock or tutorial policy was changed.

One neutral `shop_price()` decision is shared by patching and world preparation. Shop wallet predicates rebuild
from their original pre-wallet access rule on a copy, rather than layering 10 over a surviving 600-rupee gate.
Affordable applies only to shuffled Shop checks; price-only cheap shield is included even without Shop shuffle.
All Kokiri original prices are **5–40**, so a shield moved inside Kokiri remains in the starting-wallet tier.
Adult stock, Dodongo-clear and Blue-Fire/refill gates remain; wallet capacities stay 200/500/1000.

Checks so far:
- `uv run pytest tests/test_settings_prices.py tests/test_settings.py tests/test_settings_songs.py
  tests/test_shop_logic.py tests/test_shops.py -q`: **49 passed**.
- Actual whole-game CLI, seed 7, `--shuffle Chest Shop Gift --songs anywhere --shop-prices affordable`:
  **277 shuffled checks, 18 spheres, 123 overlay files**, finished-seed beatability and default-on chronological
  early-return guarantee passed before writing. Output stays in `E:/OOTRemake/work/r6-settings/seed-affordable-anywhere-7`.
- Controlled output `shop-prices-10`, `Test - shop-prices-10.bat`, `price-check.md` in the same external root:
  native Kokiri stock, eight logical prices 10 through the real PatchStep; all age/short-stock copies.
  Independent field diff preserves every field except price offsets. Adult **715636 → 715716**, child
  **715276 → 715356**, short-stock **717144 → 717144**, allocations checked/raised by the writer.
  Copied release-only new-game launcher uses its own user, never run.

**Kareem: test that controlled price overlay: shield/menu 10, purchase subtracts exactly 10, actual shield,
normal tutorial/restock, early nuts 10, five later offers still story-locked; report overlay log.**

The old chest-only field-diff oracle and preserved-vanilla-price shop oracle now explicitly opt out of the new
default cheap shield; separate dump regressions cover the new default's exact fields and full affordable prices.
The existing generation/beatability assertions were not relaxed.

## Reviewer-requested follow-up — independent inventory writes

Claude approved redirecting an independent vanilla `IsGet` write to the check's own completion flag, never
`Value=false`, and requested an all-79-check audit before the one gifts-only fix commit.

Fresh read-only audit: **640 active flowcharts**, **79 linked checks** (93 census steps), all events/entries
in each gift root, transitive called entries and `EventTransition` targets. A second pass binds wrapper arguments
and inspects GameData write destinations (`GameDataName`, `DstGameDataName`, `GameDataA/B`) and pouch actor/item
parameters. Rooting every internal entry also yields unresolved generic callback arguments; inspected their
literal call-site sources across active flows: no `IsGet.*` or `PouchData.*` flag is supplied to those generic
flag arguments. The remaining generic pouch bindings are the normal census grant wrappers, not new literal grants.
Metadata inventories are external: `gift-write-audit.json`, `gift-bound-write-audit.json`. The research used own
external code; eight throwaway builders/auditors/verifiers and their cache were removed after the recorded proof.
No GPL implementation or decoded data was committed.

| Finding | Flow / event | Treatment |
|---|---|---|
| Bolero independent learned flag | `Dm_MelodyGet_Fire/Event1`, reached from `C21` via `Event131` | `IsGet.Item_Melody_FireBolero` → `HavePlayedEvent.Dm_MelodyGet_Fire`; `Value=true`, Index, terminal edge and all other fields unchanged |
| Twelve play-along adds | `Dm_SY_Ocarina/Event59`–`Event65`, `Event67`–`Event71` | Existing per-song skip rules already bypass these; retained |
| Actual direct census grants | `Dm_MelodyGet_Time/Event70`, `Dm_Kokiri_0155/Event68` | Existing item replacement, not an extra grant |
| Egg hatching consumes egg | `Goto_HyruleCastle/Event55`, `Num=-1` | Legitimate world conversion, not extra ownership; retained |
| Timed-trade removals | `Npc_Hylia_045_Adult/Event137`, `Npc_Hylia_017_Adult/Event56`, `Npc_Zora_KingZora_adult/Event47`, all `Num=-1` | Class 3, not shuffled; legitimate consumption/retry paths retained |

**No other independent vanilla inventory grant was found.** Section 19's original Sheik-in-Crater row now needs
the above extra rewrite; section 21 now carries that pointer rather than modifying another track's section.
The completion Bool exists in the original GameDataList: Hash **10850286**, default false, reset **8**, save file **0**.
No new Bool, save-layout edit or inventory clear is introduced for this fix.

Regression first: new whole-dump changed-gift graph check failed with exactly
`Sheik in Crater / Dm_MelodyGet_Fire / Event1 / IsGet.Item_Melody_FireBolero / Value=true`.
After the cause-specific redirect, synthetic gift safety suite **24 passed**; the new dump graph check plus
existing every-flow field-diff/every-grant checks **3 passed, 3 deselected**. The redirect is guarded against
stale actions, wrong vanilla flag or false writes. Existing completion flags only; no arbitrary inventory target.
The dump oracle also verifies the target is an existing saved Bool and that every other event field is unchanged.

One read-only diagnostic initially accessed `.params` on a ForkEvent; the printed AttributeError identified
the event-type mistake. Typed `getattr` inspection then printed the real action, predecessor and completion flag.
No unchanged retry, game boot or save write.

Live corrected full-seed replay (277 checks, 18 spheres, 123 resources): original settings/fill/spoiler identical,
all 120 shop copies read back at 10, every resource parsed/allocation checked; **only the Bolero flow changed**
after the fix. Its Event1 now writes completion true, never the inventory flag. Evidence outside the repository:
`combined-seed-verification.json` and `combined-seed-smoke.log`.

## Added item 4 — forest modes (D24)

Kareem decided **forest defaults to `closed`**, close to vanilla; `closed_deku` and `open` are advanced opt-ins.
Defaults stay vanilla-like and difficulty is opt-in (D24, reviewer relay, 2026-11-08).

| Mode | Bridge exit | Mido / Deku Tree path |
|---|---|---|
| `closed` (default) | vanilla, until Gohma | sword and shield |
| `closed_deku` | open immediately | sword and shield |
| `open` | open immediately | bypassed |

`Settings.forest`, `--forest`, strings/spoilers, derived `logic.open_forest` and legacy `logic.skip_mido` all agree.
Legacy `--skip mido` / old `fast_start` spelling canonicalizes to `forest=open`, not a hidden fourth mode.
Explicit conflicting forest/skip options are rejected. When overriding a spoiler's forest mode, derived logic
fields rebuild rather than carrying the old mode forward. The standalone flag patcher's `mido` primitive remains
Mido-only; the generator's `open` combines it with the new independent `forest_exit` primitive.

**The bridge's control flag is `KokiriForest_Npc_Kokiri_007_Child_Blocker_00`, Hash 3856422516**:
default true, Bool, reset 8, save file 0. Its BlockerParam `Npc_Blocker_Kokiri_007` uses it as `GameDataToEnableAI`.
Decoded `KokiriForest_Child_Level_All_02_d26e` nodes 5/0/6 delete `Area_a467` when false, disabling the contact
sensor that could drive node 4's transient blocker true. The transient
`KokiriForest_Npc_Kokiri_007_Child_Blocker` (Hash 4043170676) already defaults false; do **not** try to patch that
unchanged default. `Npc_Kokiri_007_Child/Event42` only clears the control flag; no active flow writes it true.
No quest step, Gohma flag, NPC actor or module is changed. This is a new-game initial-value patch, not a live-save edit.

Forest/other initial-value edits now compose **before** gift-added save flags through the common writer.
Previously a prebuilt fast-start GameDataList could collide with a gift's GameDataList transform; both changes
must survive. Cutscene components remain prebuilt. Common compression/read-back/size-table handling stays intact.

Checks:
- Forest/legacy CLI/synthetic fast-start suite: **45 passed**.
- Forest dump field diffs and real new saved fairy flag composed with the exit default: **3 passed**.
- Actual full CLI from the settings string, seed 7, Chest+Shop+Gift / songs anywhere / affordable /
  **closed_deku**, default early-return guarantee: **277 checks, 20 spheres, 118 resources**. Output
  `seed-closed-deku-7`; independent read-back confirms exactly the original exit default changed, all four
  changed fairies' new saved Bools and all four save-layout growth values retained.
- The external verifier initially used the wrong ZF event suffix `Event144`; diagnostic printed added hashes
  and the committed definition **`Dm_FairyFountain_Frore/Event174`, Hash 2751359020**. Corrected only that
  verifier and rechecked the already-successful output (did not regenerate or rerun the CLI); passed.

Player output: `forest-closed-deku/`, `Test - forest-closed-deku.bat`, `forest-check.md`, all under
`E:/OOTRemake/work/r6-settings/`. New game, isolated user, release EXE only; no launcher run.
One GameDataList Bool differs, **1462888 → 1462888**, existing allocation **1463176**, no table edit needed.
**Kareem: without a sword/shield or Gohma clear, verify Mido still blocks but the bridge reaches Hyrule Field,
then return/save/Continue and recheck; supply the overlay-open log and note any unexpected story advance.**

Full gates: first sequence stopped at printed import ordering / imported fixture shadowing; corrected imports and
made the new dump inventory audit self-contained. The next sequence was explicitly cancelled for this newly
requested item 4, before changing code. The completed four-gate results below supersede those interrupted runs.

## Cross-track requests

Posted startup contract on `cs-r6`: cs6a owns `spoiler()`; preserve my separate settings-string field commit.
Shared gift, price, forest and seed hooks were isolated and posted. No overlapping chest/name edits.
Only my section 21 is appended in this branch's shared game-data plan; insert section 20 ahead of it when
integrating the readable-names track. No unauthorized rebase, merge or push.

## Provisional choices / questions

- Explicit CLI options win over a supplied string; unspecified flags preserve it.
- Strings are versioned format, not portable promises across generator/data versions.
- **Kareem: confirm default-on `cheap_deku_shield` (10 rupees), as provisionally specified for Round 6.**
- In-game acceptance remains Kareem's: file round trips and search proofs do not certify gameplay.

## Hookshot v2.0.1 launcher safety

Reviewer announced the layout change after these outputs were built. Re-read all three Track B batch files and
the corrected approved template: Claude had already updated them. Preserved those edits, no batch executed.
All three now use **`E:\Games\Hookshot\bin\hookshot.exe`**, set **`HOOKSHOT_NO_UPDATE_CHECK=1`**, and stop with
`exit /b 1` when it is missing; no fallback. Their separate `--user` and overlay/log paths are unchanged.
Updated all three player checklists and section 21 to prohibit the outer launcher, which ignores `--user`.
The external builders were already deleted, so no stale generator can recreate an unsafe batch here.

## Branch commit ledger (rebased onto `main` `29ebecf`)

| Original → rebased | Scope |
|---|---|
| `860d466` → `eeffc4f` | Item 1: codec, centralized generator defaults, CLI and deterministic replay regression |
| `a274339` → `db3df0a` | Isolated spoiler settings-string field |
| `8e35d5d` → `d0f8ce0` | Item 2: songs setting, sourced chest evidence, fill policy regressions |
| `2f9b27b` → `f2c775e` | Isolated gift policy integration |
| `832b573` → `fc928e0` | Item 3: exact prices, cheap shield, CLI and price regressions |
| `ad0bea7` → `dd6a7d5` | Isolated shop wallet rule rebuilding |
| `3e4f0d1` → `ea6211c` | Isolated price-logic preparation hook |
| `0ec0866` → `181a347` | Isolated price patch registration |
| `0dcd3a5` → `a7341f8` | Explicit vanilla-price opt-outs in existing field-diff oracles |
| `02c2da5` → `3929ed0` | Reviewer-requested gifts-only Bolero redirect and inventory safety regressions |
| `4f1941b` → `fca904c` | All-79 gift audit table/evidence |
| `95c153d` → `fd22fcd` | Added item 4: forest modes, legacy alias, D24 and tests |
| `bf596d5` → `51384b8` | Isolated bridge exit flag definition |
| `abd9be3` → `319808c` | Isolated composable initial-value patch helper |
| `0cd6fbb` → `82b5496` | Isolated forest/fast-start and gift GameData composition |
| `ec3d8a3` → `251e04e` | Derived forest logic and sourced legacy Mido rule note |
| `737a91c` → `9905bfc` | Delete obsolete Mido-only generator assertions |
| `2db0c13` → `016be3b` | Import cleanup and independent dump graph context |
| `8b2314a` → `8034a19` | Section 21, complete track ledger and Hookshot v2.0.1 safety notes |
| `2e9d88f` → `e944997` | Isolated world-format documentation for replay, forest and effective prices |
| `58dbe9d` → `b0ae167` | Pre-rebase full gates and handoff |

The post-rebase verification/handoff commit follows this ledger; its ID is posted on `cs-r6`
and in the final handoff (a commit cannot include its own hash).


## Pre-rebase completed full gates and handoff

All four required commands completed on the finished code, after item 4 and the inventory redirect:

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | **151 files already formatted** |
| `uv run ruff check` | **All checks passed** |
| `uv run pytest` | **414 passed, 54 skipped**, 375.62 s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | **53 passed, 415 deselected**, 765.04 s |

`PYTEST_ADDOPTS` directed each complete suite's temporary output to
`E:/OOTRemake/work/r6-settings/pytest-{synthetic,dump}-final`, keeping decoded/generated data out of the repo.
No failing test was skipped, weakened or hidden by retries. The old Mido-only mode assertions were deleted because
the reviewer explicitly folded that mode into forest settings; new tests cover all three modes and compatibility.
The complete suites include original seed/age-return sweeps, cross-interpreter determinism, every placement/EVFL
round trip, census and the new settings, price, forest and inventory-leak dump oracles.

Requested player artifacts/checklists are complete under `E:/OOTRemake/work/r6-settings/`:
`chest-ocarina-minuet`, `shop-prices-10`, `forest-closed-deku`. Each launcher was statically checked after Claude's
v2.0.1 correction; only the bin game executable, update check disabled, missing-exe refusal and isolated user.
The full generated-seed smoke outputs and verification JSON/logs remain there as data/search evidence.
Eight temporary scripts/cache and completed earlier targeted-test outputs were removed. Git Bash's removal of
two pytest `*current` directory symlinks initially reported permission denied; metadata printed SymbolicLink
attributes 1040 and their session-local targets. Removed the links and empty parents non-recursively instead,
without traversing a link or touching another session's data.

Left for Claude/Kareem, not unfinished code:
- Review/merge the scoped commits (never pushed or merged here); order section 20 before 21 during integration.
- Run the **three in-game checks above** with overlay logs. No game/launcher/window was started by this track.
- Confirm the **provisional cheap-shield default**; forest's `closed` default is already decided by Kareem (D24).
- Integrate other tracks' shared `spoiler`/play-note and Scrub hooks while preserving the posted settings/price/
  forest APIs. This worktree was not rebased without authorization.

No dependency or lockfile edits requested, no game data committed, no source-dump or save writes, and no write/read
of Kareem's active `E:/OOTRemake/work/r5-seed/` output or users.

## Authorized rebase onto `main` `29ebecf`

Claude authorized `git rebase main` after tracks C/D merged. All 21 track commits replayed.
Resolved the CLI conflict by keeping D's Scrub/Token choices/help and `default=None`, so a supplied string's
shuffle list survives unless explicitly overridden. The patch pipeline auto-merged D's early Token refusal and
Scrub setup with the price step and forest-before-gift GameData composition; no upstream hooks were dropped.
Resolved the research append conflict as section **19, 21, 22, 23**, retaining C/D text intact; section 20 is
still A's integration. The ledger above maps every original commit to its rebased ID.

### Integration-only priority collision, fixed in `cdf2e9b`

The first additional all-four-kinds CS1 CLI smoke refused seed 7 after the existing ten-attempt bound.
Printed first-fill values instead of retrying unchanged: both capacity holds were exactly `("Scrub",)`,
no holds were empty, and all four once-sale slots contained unrestricted rupees before capacities were placed.
The Shop branch merges priority with ordinary filler; its native/non-native sort had erased the held-item
priority the standalone Scrub branch retained. Added a stable held-item tie-break within that existing ordering;
no retry-count, destination-policy, price, saved-flag or logic changes.

Synthetic regression: only one Scrub capacity destination, one native Shop and one unrestricted chest.
Before the fix, seed 3 with one attempt failed with `['Capacity', 'Native']` unplaced; after, all twenty
deterministic seed permutations preserve Capacity→Scrub, Native→Shop and Rupee→Chest, one attempt each.
The complete pre-fix gate job was cancelled before editing code; a new full four-gate sequence runs on the fix.
The same actual combined CLI command then succeeded: **281 checks, 20 spheres, 123 resources**, full world,
default gated-return guarantee. No seed/mode/guarantee was changed to make that smoke pass.

Token override smoke used that combined string plus `--shuffle Token`: exit **1**, expected
`GoldTokenGmdHash` callback/persistence refusal, no stdout and no output directory created.

### Independent integrated overlay read-back and replay

`E:/OOTRemake/work/r6-settings/rebased-integration-proof.json` and `rebased-replay.log` record:
- All four scrub families: every tier grant and selection matches the assigned actor, native 100/40 fees stay
  intact; restoring only those actor fields reproduces the entire original flow tree, including gates.
- Both capacity items stay at Scrubs; their effective-string restrictions remain exactly `("Scrub",)`.
- All **120 physical Shop copies** show their assigned native display at exactly 10, no conditional discount,
  unchanged stock and releases.
- Bridge default false, Mido default true; four saved gift Bools remain false/reset 8/save 0 with **32 bytes**
  layout growth. Remove the new Bools and growth: the tree is exactly the selected initial-value transform.
- Effective spoiler string round-trips; a separate CLI replay process with `PYTHONHASHSEED=31337` reproduces
  **all 124 files byte-identically** (123 resources plus spoiler). Spoiler has 19 progression-bearing spheres;
  the CLI's 20 spheres also include its non-progression-only sphere.

Both temporary diagnostic/verification scripts were removed after use. No player launcher, game or user folder
was run or changed; these overlays are generation/read-back/search evidence only.

