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

The existing `docs/discord/server-kit.md` still says private/do not repost and has stale dump/loading
claims. It is not in this track's owned list. Request reviewer authorization/owner correction; do not
silently edit it. `docs/seed-pack.md` contains the old overlay route and evidence wording, owned by cs11c.

**Kareem/reviewer: before changing visibility, approve or replace the stale Discord-kit drafts, and
update AGENTS.md's overlay proof line to the current mods log (`mods: <file> <- <path>`).**
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
