## Problem and change

Describe one issue, its evidence, the change and remaining limits. Link the relevant plan or issue.

## Verification

List exact commands/results, skipped native coverage and any runtime smoke result. For game behavior,
include runtime/build, seed/settings, age/inventory/story state, steps, loading-log excerpt and actual
result. Say **built, untested in game** when acceptance is pending. Never attach game data or saves.

## Checklist

- [ ] Small, single-topic change; product/default/logic changes discussed with the owners.
- [ ] I have the right to submit this contribution under the project's MIT licence.
- [ ] No game files, decoded data, keys, saves, generated mods, spoilers or caches anywhere in the PR or attachments.
- [ ] Reused code/dependencies are permissively licensed and credited by file/commit in NOTICE; no GPL, unlicensed or NX2navi material.
- [ ] AI assistance, if used, is disclosed here and in `Assisted-by:` commit trailers; otherwise stated not used.
- [ ] Determinism, stable location identities and sourced data rules are preserved.
- [ ] `uv run ruff format --check` and `uv run ruff check` pass.
- [ ] Synthetic tests pass; relevant dump tests pass on my own supported dump, or skipped coverage is explicitly explained.
- [ ] Significant behavior is exercised; in-game acceptance or its pending status is recorded without treating data tests as gameplay proof.
- [ ] Docs, affected callers and contract tests are updated; no unrelated output/save folder was modified.

AI assistance used (or none):

Owner review and merge: Kareem and his co-owner.
