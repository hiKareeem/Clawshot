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
Metadata inventories are external: `gift-write-audit.json`, `gift-bound-write-audit.json`; research scripts there
are own code, no GPL implementation or decoded data committed.

| Finding | Flow / event | Treatment |
|---|---|---|
| Bolero independent learned flag | `Dm_MelodyGet_Fire/Event1`, reached from `C21` via `Event131` | `IsGet.Item_Melody_FireBolero` → `HavePlayedEvent.Dm_MelodyGet_Fire`; `Value=true`, Index, terminal edge and all other fields unchanged |
| Twelve play-along adds | `Dm_SY_Ocarina/Event59`–`Event65`, `Event67`–`Event71` | Existing per-song skip rules already bypass these; retained |
| Actual direct census grants | `Dm_MelodyGet_Time/Event70`, `Dm_Kokiri_0155/Event68` | Existing item replacement, not an extra grant |
| Egg hatching consumes egg | `Goto_HyruleCastle/Event55`, `Num=-1` | Legitimate world conversion, not extra ownership; retained |
| Timed-trade removals | `Npc_Hylia_045_Adult/Event137`, `Npc_Hylia_017_Adult/Event56`, `Npc_Zora_KingZora_adult/Event47`, all `Num=-1` | Class 3, not shuffled; legitimate consumption/retry paths retained |

**No other independent vanilla inventory grant was found.** Section 19's original Sheik-in-Crater row now needs
the above extra rewrite; section 21 will carry that pointer rather than modifying another track's section.
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
requested item 4, before changing code. All four complete gates will run again on the finished item-4 tree.

## Cross-track requests

Posted startup contract on `cs-r6`: cs6a owns `spoiler()`; preserve my separate settings-string field commit.
Gift-policy changes need a separate `patch/gifts.py` commit; price logic needs separate world/seed integration
commits. No overlapping chest/name edits. Section 21 will follow section 20 in the shared game-data plan.

## Provisional choices / questions

- Explicit CLI options win over a supplied string; unspecified flags preserve it.
- Strings are versioned format, not portable promises across generator/data versions.
- **Kareem: confirm default-on `cheap_deku_shield` (10 rupees), as provisionally specified for Round 6.**
- In-game acceptance remains Kareem's: file round trips and search proofs do not certify gameplay.
