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

**Kareem/reviewer: update AGENTS.md's overlay proof line to the current mods log
(`mods: <file> <- <path>`).**
AGENTS.md is deliberately unchanged, as instructed. The orchestration file already records the new rule.

## Verification

The requested three checks and document/issue-form/public-tree smoke results will be recorded after
all five ordered items. No full suite, dump test, seed sweep or gate lock is needed for this track.

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

Commit `b0d932a` replaces both occurrences of the specified other author's name in the roadmap
with anonymous wording. It changes only those two lines; history and commit identities are untouched.

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

Public-review considerations retained rather than erased: plans contain machine/scratch paths,
native identifiers, research addresses and historical private-pack/overlay instructions. Those are
not decoded game-file copies; current public entry points override obsolete instructions. The still
stale pack guide is assigned to cs11c and must be integrated before publishing. The Discord drafts
are corrected separately below. No unlicensed archive, NX2navi material, game source or dump was opened.
