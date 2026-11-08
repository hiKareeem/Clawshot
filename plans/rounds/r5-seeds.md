# Round 5, track C: whole-game chest seeds (cs5c)

Branch `r5/seeds`. Dump and save backups read-only; no game, launcher or windows started.

## Item 1: extra patch steps

`make_seed(..., extra_steps=[step, ...])`: a `PatchStep` receives the generated placements (`Mapping[str, str]`) and returns `FileChanges`: a mapping of romfs-relative paths to `Callable[[bytes], bytes]`. Each transform receives decompressed bytes and returns decompressed bytes, validating its own format read-back. Close over romfs/census/world context when creating the step. Steps run in registration order after chest edits, including when shops and chests share one Banc. The common writer handles compression, raises size entries and builds every file before writing any. Steps must not return the size table itself.

Chest linking/planning only handles `Chest`; other kinds use these steps. A non-chest shuffle without any registered step is refused. Existing chest-only callers keep working. No dependency added.

Verification: `uv run pytest tests/test_patch.py tests/test_seed.py -q`: **20 passed** (including shared-file composition and all-or-nothing failure). Scoped ruff lint/format checks passed (4 files). Live dump-backed seed 7 slice with a registered transform wrote 6 files; the transform received the already chest-patched Banc (3,639 actors); temporary output removed. This item is committed and posted separately before chest coverage work.

## Questions and provisional choices

- Whole-game seed outputs are search-verified, not in-game certified. Track A's chronological age model requires regeneration once Claude authorizes a rebase.
