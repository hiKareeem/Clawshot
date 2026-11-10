# Public documentation — cs11a

Branch: `r11/public`. Documents only; no source, tests, dependencies, AGENTS.md or decisions.md edits.
Read the required project instructions/plans, recent implementation reports and playtest answers.
Shared ownership: README here; seed-pack guide/templates belong to cs11c; dependency metadata to cs11d.
No game, launcher, window, dump/save/output mutation, merge, push or stash.

## 1. Newcomer README and settings reference

Replaced the obsolete prototype/private-pack introduction with public-test status, own-dump/no-game-file
rules, supported build, verified versus enabled-but-unaccepted versus held features, known issues,
source/pack workflows, AI disclosure, contribution/Discord links and legal credits.
Moved the detailed CLI/developer reference into `docs/settings.md`, preserving the old options while
correcting stale evidence: Minuet/Epona as well as Storms have chest observations; free-travel first
arrival is now confirmed; floor-shield grant is confirmed but not every pickup/persistence combination.
No claim of a completed playthrough or universal runtime compatibility.

Evidence basis: roadmap results through the completed gift/age/container work and playtest IDs
R6-MINUET, R6-CLOSEDDEKU, R6-PRICES, R7-BOSSHEART, R8-GETITEM, R8-FREESTANDING,
R8-SHOPKEEPER-LATE, R8-FROGS, R9-LICHII, R9-FREE-TRAVEL, R9-PRELUDE-PATCHED,
R10-FIRST-PULL-FIXED, R10-MARKET-BOTTLE and R11-HOOKSHOT-2012. Deterministic bowling and
normal galleries are explicitly enabled but not dedicated-player-accepted; merchant/expert/bottle/digging
holds remain. Only 10-token reward evidence is claimed, not every Skulltula House threshold.

Provisional presentation choice: one status overview in README, detailed settings/evidence boundaries in
the settings reference, runtime steps linked to their owner's guide rather than duplicated.
No new product decision.

## Coordination and diagnostics

The extensionless `~/go/bin/bermuda` command failed before reading the thread (exit 127).
Read the installed executable directory: it contains `bermuda.exe`, not `bermuda`.
Use `C:/Users/hi/go/bin/bermuda.exe` for the allowed post/log commands.

Initially flagged stale/private Discord drafts outside ownership. Claude subsequently assigned
`docs/discord/server-kit.md` here: update as public-test drafts in a separate commit, retain
own-dump/no-game-files/no-piracy rules and permanent invite. `docs/seed-pack.md` remains cs11c's.

Resolved by Claude on main: AGENTS.md now uses the mods log proof, preserves hard-rule numbers,
and moves maintainers' round workflow to orchestration. Rebased on main as explicitly directed;
no agent-owned AGENTS.md edit. Read the new rules, orchestration and `plans/README.md`.

## Verification

The three requested commands passed on the final rebased documentation tree; results are below.
No full suite, dump test, seed sweep or gate lock was run or taken for this track.

## 2. Contributor guide

Added `CONTRIBUTING.md`: MIT inbound licensing; permissive-only dependencies/reuse; no GPL,
unlicensed or NX2navi material; game-free issues/attachments and synthetic fixtures; disclosed AI
assistance; scoped PRs; deterministic data/identity contracts; standard gate commands and native
coverage; isolated player checks with current mods-loading proof. Kareem/co-owner retain merge
and product decisions. No behavior or licensing policy changed.

## 3. Issue forms and PR checklist

Added bug and logic question forms with revision/seed/full-CS1/runtime/state/evidence fields,
required no-game-data acknowledgement, reviewed log excerpts and explicit inference limits.
Blank issues are disabled; the contact link uses the permanent Discord invite. The PR checklist
covers MIT rights, provenance, AI trailers, determinism, checks, docs and gameplay acceptance.
Forms do not request saves, generated spoilers or mods.

## 4. Logic porting reference

Added `docs/logic.md`: file map, override precedence/provenance, rule syntax and failure behavior,
item/settings semantics, physical versus model/display identity, chronological search and first-pull
proof, all current spoiler top-level fields, and the additional live client/runtime delivery needed
by a future multiworld integration. Each contract cites its specification or implementation path.
Read the actual spoiler producer to confirm `locations`, nullable `opening_route`, warnings and hints;
no source was changed. No live tracker/client/network IDs are invented.

## 5. Public-tree housekeeping and scan

The isolated roadmap housekeeping commit replaces both occurrences of the specified other author's
name with anonymous wording. Only those two lines changed; no history rewrite or identity edits.

Scanned the tracked-file inventory plus non-ignored working-tree paths, including hidden `.github`
files. File-pattern scan found no game containers/resources, saves/keys, generated seed manifests,
archives/logs, private-key files, `.env` files or RomFS/ExeFS/cache folders. Tracked inventory consists
of source, TOML definitions/logic, synthetic test code, text documentation/licences and build metadata.
Ignored local environments/tool caches are not release contents and were not treated as tracked data.

Full-tree text searches (excluding Git internals and agent context files) covered attribution/contact
markers, third-party GitHub sources, the requested author's exact name and credential-like strings:

- Retain legal credits: OoTRandomizer and AmazingAmpharos, Testrunner, Zannick, Junglechief87,
  LLCoolDave, KevinCathcart; Archipelago/Berserker66/CaitSith2/LegendaryLinux; a55uka. NOTICE and the
  vendored MIT licence are intentionally not anonymized.
- Hookshot/NotRexed, SkyboundTotk, OoT Randomizer, Archipelago and public factual guide citations are
  provenance, not endorsement. `sloperina`/PracticeROM remains a facts-only cited research lead in
  `plans/03-game-data.md` and `plans/rounds/r9-itembar.md`; no code from it is claimed.
- NX2navi mentions are source-use prohibitions, not imported material. AI model/Claude/Hermes,
  Kareem, Greenferret and thread/track handles occur in planning/history records; no blanket name purge.
- Contact scan found the example Anthropic noreply trailer in the roadmap, no secret email credential.
  Kareem's commit email is intentionally unchanged; no history rewrite or historical-secret audit.
- Credential heuristic matched only `sk-` substrings in mask-guide URLs, not actual credentials.
  No private-key block or token/password assignment was identified. This is a heuristic tree scan,
  not a guarantee that all secrets or licensing issues are absent.

D36 confirms `plans/` stays public as the maintainers' working notes, including its machine paths,
research identifiers and historical instructions. Those are not publication blockers; no move,
stripping or general name purge is proposed. The scan identified no material that must remain
non-public, within the heuristic limits above. Current player instructions still need cs11c's
loading-guide integration. No unlicensed archive, NX2navi material, game source or dump was opened.

## Additional assignment: public Discord drafts

Claude explicitly assigned `docs/discord/server-kit.md` during this run. Kept it as drafts Kareem
posts himself, never published messages. Updated public-test sharing (original zip only), permanent
invite, own-dump/no-piracy/no-game-file rules, NUP preflight nuance, current mods loading and manual
save warning, relevant report fields/log excerpts and evidence-bounded announcement matching README.
Removed the obsolete private/do-not-repost claims and unqualified all-version reproducibility.
No Discord API or message-send action was used.

## Reviewer follow-up: shared contributor rules

Rebased the seven documentation commits on main without conflicts at Claude's instruction.
CONTRIBUTING now explicitly directs agent-assisted contributors to AGENTS.md as the shared rule
authority instead of duplicating identity/determinism/logic/failure contracts. Ordinary contributors
need not join the maintainers' planning or gate-lock workflow. Inbound licensing, public issue safety,
required commands and practical gameplay checklist remain in the contributor guide.

## Document/pack smoke

Parsed both actual YAML issue forms with PyYAML in an isolated evaluation environment (no project
dependency change): nine/seven unique field IDs, required input/textarea fields and safety checkboxes
validated; Discord configuration parsed with blank issues disabled. Initial repository-link check:
six Markdown documents, 41 local links, all present. GitHub-hosted form rendering was not exercised.

Actual `clawshot.pack.source_files` snapshot contains 187 files, byte-identical README/seed guide.
It intentionally ships neither plans nor the new repository-only references. Printed missing pack
targets: CONTRIBUTING, settings, logic and the two evidence files. Fixed README's repository-only
references to full URLs under the observed origin (`hiKareeem/Clawshot`), retaining local runtime-guide,
NOTICE and LICENSE links shipped in packs. No pack code or allowlist expansion, game read or generation.

A rule-language example edit briefly landed at the wrong row; the edit response exposed the
misplaced table row/prose, then a fresh read supplied exact anchors for correction before checks.

## Final verification and handoff

| Command | Result |
|---|---|
| `uv run ruff format --check` | 263 files already formatted; exit 0 |
| `uv run ruff check` | All checks passed; exit 0 |
| `CLAWSHOT_WORKERS=1 uv run pytest -q tests/test_pack.py` | 13 passed in 0.29s; exit 0 |

Commands ran serially without a gate lock as requested. Tasklist before the first check chain found
no Hookshot process; no game was started. The earlier pre-rebase chain also passed (262 formatted,
lint passed, 13 tests in 0.78s); final results above supersede it. uv's initial cross-filesystem
hardlink warning fell back to copying dependencies successfully; no source/dependency edit followed.

Final document smoke passed: six Markdown documents, 35 local links present, six hosted-repository
URLs resolved against corresponding checkout files, and all four local README links included by the
actual 187-file source-pack snapshot. YAML files parse; no project dependency was added. Remote URL
availability and GitHub's hosted form rendering are explicitly not verified; the repository is still
awaiting the owner's visibility change. No dump, generated seed or game startup was needed.

### Rebased commits on `r11/public`

| Commit | Scope |
|---|---|
| `9dc554f` | Newcomer README and preserved settings reference |
| `182cf3b` | Contributor licensing/safety/evidence guide |
| `847bb63` | Issue forms, Discord contact and PR checklist |
| `bfd7e8d` | Sourced logic/porting/spoiler guide |
| `4304413` | Two-line roadmap name removal, isolated |
| `9da29db` | Public-tree scan report |
| `215a6e7` | Separately authorized Discord draft update |
| `0110184` | Main's revised AGENTS linkage and pack-safe repository references |

The final evidence-only commit follows this ledger; its ID is supplied in the handoff/thread.
Only documents/templates are changed. AGENTS.md and plans/README.md updates came from the authorized
main rebase, not this track; decisions.md, source, tests, dependency files and cs11c's seed guide
remain unedited here. No merge, push, stash, history rewrite, output rewrite or unrelated deletion.

### Left for review and publication

- Claude reviews/merges these commits and integrates cs11c's current mod-loading guide/templates
  before building a new public pack. This worktree's inherited pack guide still has old overlay text;
  ownership was respected, and the new README/Discord drafts explicitly reject old launchers.
- Keep keysanity unavailable for play pending cs11b's evidence. Under D37 a local web UI is being
  built by track D; README deliberately says nothing about it until it merges.
- Kareem controls visibility, branch protection, collaborator access and which Discord drafts he
  posts. Nothing was posted to Discord. The shared AGENTS proof correction is already resolved.
- Existing gameplay questions/held checks remain as listed in README/settings, not new requests to
  repeat completed experiments. This documentation-only work adds no new in-game acceptance task.

## Confirmed publication decisions

Read D36/D37 from main's `plans/decisions.md` after Claude's follow-up. Plans remain public;
the scan reports only material that should not be public at all, with no such material identified
by its stated checks. The UI is work in progress elsewhere, not absent from the project plan;
README remains silent until its merge. This follow-up changes only this report, not source,
player instructions or the previously checked documentation/template behavior. No checks rerun.
