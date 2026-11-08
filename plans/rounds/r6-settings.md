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

## Cross-track requests

Posted startup contract on `cs-r6`: cs6a owns `spoiler()`; preserve my separate settings-string field commit.
Gift-policy changes need a separate `patch/gifts.py` commit; price logic needs separate world/seed integration
commits. No overlapping chest/name edits. Section 21 will follow section 20 in the shared game-data plan.

## Provisional choices / questions

- Explicit CLI options win over a supplied string; unspecified flags preserve it.
- Strings are versioned format, not portable promises across generator/data versions.
- **Kareem: confirm default-on `cheap_deku_shield` (10 rupees), as provisionally specified for Round 6.**
- In-game acceptance remains Kareem's: file round trips and search proofs do not certify gameplay.
