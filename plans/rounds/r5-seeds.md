# Round 5, track C: whole-game chest seeds (cs5c)

Branch `r5/seeds`. Dump and save backups read-only; no game, launcher or windows started.

## Item 1: extra patch steps

`make_seed(..., extra_steps=[step, ...])`: a `PatchStep` receives the generated placements (`Mapping[str, str]`) and returns `FileChanges`: a mapping of romfs-relative paths to `Callable[[bytes], bytes]`. Each transform receives decompressed bytes and returns decompressed bytes, validating its own format read-back. Close over romfs/census/world context when creating the step. Steps run in registration order after chest edits, including when shops and chests share one Banc. The common writer handles compression, raises size entries and builds every file before writing any. Steps must not return the size table itself.

Chest linking/planning only handles `Chest`; other kinds use these steps. A non-chest shuffle without any registered step is refused. Existing chest-only callers keep working. No dependency added.

Verification: `uv run pytest tests/test_patch.py tests/test_seed.py -q`: **20 passed** (including shared-file composition and all-or-nothing failure). Scoped ruff lint/format checks passed (4 files). Live dump-backed seed 7 slice with a registered transform wrote 6 files; the transform received the already chest-patched Banc (3,639 actors); temporary output removed. This item is committed and posted separately before chest coverage work.

## Questions and provisional choices

- Whole-game seed outputs are search-verified, not in-game certified. Track A's chronological age model requires regeneration once Claude authorizes a rebase.

## Item 2 prerequisites and investigation

- New checks were not supported by the existing override loader: `3a9b692` adds explicit `new = true` locations. Four schema/reachability tests passed; live search printed `[]` before Bomb Bag and the new chest afterwards. Posted on `cs-r5`.
- `1b2fbfd` (reviewer-authorized, model and test only) gives `GanonBossKey` dungeon ownership. Before: dungeon `None`, outside placement allowed. After: `Ganons Castle`, outside refused; regression also checks actor disambiguation and the `anywhere` setting.
- Follow-up reviewer request: region `Ganons Castle Tower` inherited no dungeon from `Bosses.json`. `extra_ganon_tower.toml` sets its dungeon with explicit existing-region metadata (`new = false`, source required); this preserves its checks/exits. Six focused tests passed. Actual full-world smoke: tower dungeon `Ganons Castle`, tower chest allowed, Kokiri Sword chest refused.
- OoT Randomizer treats the tower as castle for its boss-key setting: `Region.py:112-140` selects `shuffle_ganon_bosskey`, then checks `HintArea.at`; `Hints.py:475-507` inherits the castle hint through the tower's entrances (`Bosses.json:214-229`), at MIT commit `526b4c8d`. Clawshot's explicit dungeon field reproduces that ownership without adding a second hint-traversal model.
- The first Bermuda command failed with exit 127 because `~/go/bin/bermuda` resolves without `.exe` in this shell. Directory inspection showed `C:/Users/hi/go/bin/bermuda.exe`; all posts use that binary now.
- Launcher requirement (reviewer): use the corrected r2-test/cs5b launcher, executable **only** `E:\Games\Hookshot\hookshot.exe`, never the device-losing `work\hookshot-main` build. Launchers will be written, never run.
