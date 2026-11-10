# Round 11, Track E: release tested gifts (cs11e)

Branch `r11/release`; scratch `E:/OOTRemake/work/r11-release-cs11e/`.
Read AGENTS, README, CONTRIBUTING, architecture, orchestration, roadmap Round 11/shared files,
world format, decisions, section 40 and r10-gifts; accepted Kareem's five specified answer rows.
Only two named gift holds and their release consumers are in scope. No patch code, dependency,
merge/rebase/push/stash, game/window/launcher execution, save edits or played-output writes.
Python LSP unavailable (only marksman configured). All pytest runs use `CLAWSHOT_WORKERS=1`.

## Item 1: release only matching tested flows

Read both old builders and proofs; never executed or changed them. Independently called the
current gift planner/common writer into fresh scratch folders, then compared to the read-only
`r10-gifts-cs10a/ingame/mods/<name>/<name>/romfs/` files. Both compressed and decompressed
bytes match. Removed only the bottle and digging `keep_vanilla` fields, retaining names,
rules and all unrelated holds. No patch-code change needed.

Repeated the comparison through the real `gifts.seed_setup` closure with a Boomerang assignment;
both checks are eligible and both common-writer flows still match the tested files exactly.
The closure also plans other unchanged-minigame normalization; the isolated comparison selects
only the named flow to match each original one-check experiment, not a generated whole seed.

| Flow | Decompressed bytes | SHA256 (generated and tested) |
| --- | ---: | --- |
| `Npc_Hylia_020_Shop_Child.bfevfl.zs` | 101512 | `5da5ff0cbeb84bc8509915091d4a655ae053ce47dcbde98b0e909431f1f420b1` |
| `Npc_Hylia_Dampe_001.110.bfevfl.zs` | 305688 | `4b8a48f99880400462c06afb58d3a513c944ba26db2342b26d82c0c00601e243` |

Evidence: scratch `before-comparison.json`, `released-comparison.json`.
Commands: `uv run python <scratch>/compare_tested.py before`, then `... released`: exit 0.
`CLAWSHOT_WORKERS=1 uv run pytest tests/test_gifts_bottle.py tests/test_gifts_digging.py -q`:
**5 passed**. Includes refusal, corrected NPC completion, saved revisit and digging cleanup.
Kareem's R10-MARKET-BOTTLE-FIX supersedes the old crash; R10-DIGGING confirms the real grant,
though its display remains a Piece of Heart and Save and Continue was not reported.
No additional in-game test staged or required for this data-only release of those exact flows.

Cross-track note posted: Gift coverage increases by two; UI can refresh its derived count.
The requested literal `~/go/bin/bermuda` first failed exit 127 because this shell's HOME is a
backslash Windows path. Inspected `C:/Users/hi/go/bin/bermuda.exe`, then used that executable
successfully with only `thread post`. No other Bermuda command or agent-terminal command used.

Item commits are checkpoints, not ready claims; the four full gates remain required at handoff.

## Priority integration repair: NUP matrix after the keys guard

Claude approved this separate commit while item 2 waits for his loader-review gate lock.
The inherited `songs-prices` cache row requested `dungeon_items="anywhere"` even though the
keys guard now rejects that output before reading the dump. Removed only that override:
own-dungeon still exercises exactly the same resource inputs, songs, prices and full output
comparison. Settings/fill keysanity and its refusal tests are unchanged.

Claude explained the missed integration: the keys-track dump gate lacked `OOT_NUP`, skipping
this matrix. Every dump run here sets both `OOT_ROMFS` and `OOT_NUP`; the actual read-only NUP
listed in `E:/Games/Hookshot/` is `The Legend of Zelda Ocarina of TIme [04004860224DEC000].nup`.
No NUP test skip is acceptable for the handoff. Claude will review/gate/merge keys and release
together at this branch's handoff head; base unchanged, no rebase.

## Item 2: logic regression (sweep queued)

The existing placement/search model already grants the placed reward, not an implicit bottle;
no logic-code change is needed. New `tests/test_gifts_release.py` exercises the actual remake
bottle source with a synthetic bottle-gated probe: unshuffled gives a Bottle and opens it;
shuffled Boomerang gives no Bottle and cannot open it. Both released checks enter the pool;
expert galleries, three merchant experiments and the 40-token reward remain excluded.
`CLAWSHOT_WORKERS=1 uv run pytest tests/test_gifts_release.py -q`: **3 passed**.

First test draft misused `Search.holds`, which checks events, for an inventory item. Printed
diagnostic: spheres contain the bottle source, Boomerang count 1, Bottle count 0, event-held
Boomerang false. Corrected only the test to check item counts, then one rerun passed.
The one-worker seeds 1–50 sweep for defaults and the actual read-only seed-8 settings is queued
behind Claude's loader-review lock. No sweep result is claimed yet.

## Item 3: names, hints and play note

No catalogue or hint-policy edits needed. Existing `tests/test_names.py` covers both stable
identities: `Npc_Hylia_020_Shop_Child/Event171` and `Npc_Hylia_Dampe_001/Event628`.
`CLAWSHOT_WORKERS=1 uv run pytest tests/test_names.py -q`: **1 passed**.
A throwaway in-memory fault probe removed each row independently from the test's catalogue
view; the existing permanent test rejected both missing rows with the exact missing identity.
No repository or game-data file was removed.

`uv run python <scratch>/smoke_names.py`: exit 0. Synthetic placements with the two real
location identities exercised actual random-location, item and Way of the Hero selection,
spoiler descriptions and play-note rendering. Six cases preserve the existing readable names,
directions and stable IDs; location hints name the right gift, area hints use Market/Graveyard.
Only distribution weights changed in the throwaway harness; no new always/sometimes policy.
Evidence `names-proof.json`. Names catalogue and production hint code intentionally unchanged.

## Item 4: NUP cache-only patch coverage

Extended the existing `gift` row of `tests/test_pack_nup_dump.py`, not a second build:
the actual cache-only CLI output must contain both released placements and their emitted
flow files, whose grant actors must match the written spoiler. It still compares every
output file with the independent full-dump CLI build. Missing input errors still print the
RomFS-relative path to add to `pack/resources.toml`. Existing wildcard flow coverage supplies
both inputs; no resources manifest edit needed.

`CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs OOT_NUP="E:/Games/Hookshot/The Legend of Zelda Ocarina of TIme [04004860224DEC000].nup" uv run pytest tests/test_pack_nup_dump.py -k gift -m dump -q --basetemp <scratch>/cache-gift-focused`:
**1 passed, 16 deselected, 101.49s**; no skip. This runs the real CLI twice and writes complete
outputs: cache-only and independent full dump are byte-identical. Actual seed 7 has **224 shuffled
checks**; bottle tutorial gives `Rupee (1)`, digging gives `Bottle with Milk`. Both actual written
grant actors match those spoiler assignments. The cache was removed on exit; original NUP's
size/mtime unchanged, checked by the fixture. Neither historical seed pack was rebuilt.

## Item 5: scoped player status

Updated only the owned release passages in README, settings, Discord kit and pack READ ME FIRST,
plus one new subsection at the end of section 40. Both answer IDs accompany the release;
players are told where the rewards are, that the shop skips bug catching, and that digging
still displays a heart while granting the shuffled item. Expert/merchant/Skulltula exclusions
and the limited normal-minigame acceptance are retained. Existing seed 8/10 packs untouched.

`CLAWSHOT_WORKERS=1 uv run pytest tests/test_pack.py -q`: **13 passed**.
Actual `pack.source_files()` plus the builder's READ ME FIRST template source: **189 files**;
both answer IDs are present in the shipped README and player instructions. This is a
source-snapshot smoke only, not a rebuilt historical pack or a game run.

## Serialized final verification queue

The first sweep wrapper was inspected only to reschedule it: its entire output contained
16 one-minute gate-wait notices, no acquisition and no started check. Cancelled that own,
still-queued wrapper without touching Claude's lock, then queued one deadline-free command:
`uv run python <scratch>/run_locked.py sweep uv run python <scratch>/sweep.py && uv run python <scratch>/gates.py`.
This guarantees sweep then four gates, never two own gate contenders. No executed check was
repeated. Each command acquires `E:/OOTRemake/work/rounds/r11/gate.lock` with mkdir and
releases its own directory in finally immediately at subprocess completion, including failure.
All pytest workers are 1. Synthetic gates unset both dump variables; every dump invocation
sets both actual read-only sources. Gate temporary files stay inside this track's scratch.
Final results remain pending; implementation/test sources are frozen.

## Follow-up: accepted child minigames (Claude's priority steer)

Before touching documents, inspected the own queued job: only 39 one-minute gate-wait
notices, no lock acquisition or started sweep/gate. Cancelled that still-queued own wrapper
to prevent a documentation-edit/gate race; Claude's lock remained untouched. No own full
gate was running during these edits, and no executed check is repeated by rescheduling.

Appended the supplied R10-MINIGAMES-CHILD-JABU row verbatim as the last answer row.
README/settings/Discord now accept both bowling prizes and both normal galleries, citing
that row and R10-MINIGAMES-ADULT; only first-expert minigame checks remain unshuffled/untested.
Pack instructions say the alley still shows its original prizes but gives the seed's.
Updated only this track's new section-40 summary to avoid contradicting the fresh answer.
No patch, settings, pool, held expert/merchant/House check or played output changed.

Verification: supplied row equals the last table row exactly and occurs once; **passed**.
`CLAWSHOT_WORKERS=1 uv run pytest tests/test_pack.py -q`: **13 passed, 0.29s**.
Requeue the same ordered sweep/four-gate command only after this docs commit; no full own
gate has run yet. The complete dump gate still includes both `OOT_ROMFS` and `OOT_NUP`.

## Item 2 completed: one locked seeds 1–50 sweep

Final ordered job completed with exit 0. Ran one worker, no pool, one sweep at a time.
Prepared the same kind-specific world, actual census chest pool and restrictions as the CLI,
then called `generate` and independently `check_beatable` for each result. Seed-8 settings
came from its read-only historical spoiler; neither its output nor its pack was rebuilt.
Before counts use a private copy restoring exactly these two old holds, not another worktree.

| Settings | Seeds beatable | Checks before | Checks after | Gifts before | Gifts after | Sphere range |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Defaults | 50/50 (1–50) | 165 | 165 | 0 | 0 | 22–34 |
| Seed 8's exact CS1 | 50/50 (1–50) | 298 | 300 | 57 | 59 | 17–27 |

The only added names are the bottle tutorial and digging reward; no removed checks.
Sweep subprocess: **851.55s**, exit 0. Proof: scratch `sweep-proof.json`, `sweep.log`,
`sweep-result.json`, and the exact original CS1 in `seed8-settings.txt`.
The passing bottle regression preserves fixed early-bottle logic without Gift and proves
that a shuffled Boomerang at the merchant does not unlock a bottle-dependent check.

## Complete final gates and handoff

Ran all four full required commands after `187d1a2`, including its player template change.
Every command acquired/released the shared gate directory independently; no overlapping
full gates/sweep and no other holder's directory removed. Every subprocess returned 0.
Synthetic run had both dump variables unset. Dump run set:
`OOT_ROMFS=E:/Games/Hookshot/romfs` and
`OOT_NUP=E:/Games/Hookshot/The Legend of Zelda Ocarina of TIme [04004860224DEC000].nup`.
All pytest runs used `CLAWSHOT_WORKERS=1`; temporary game data stayed under scratch.

| Full command | Observed result |
| --- | --- |
| `uv run ruff format --check` | 271 files already formatted; exit 0 |
| `uv run ruff check` | All checks passed; exit 0 |
| `uv run pytest` | 846 passed, 110 skipped; 1187.35s; exit 0 |
| `uv run pytest -m dump` (both source variables above) | 109 passed, 847 deselected, no skips; 2574.07s; exit 0 |

**No skip of the NUP tests:** all 17 rows in `test_pack_nup_dump.py` passed, including every
resource mode and both newly released gift patches. The keys-guard matrix repair is included.
Retained `gate-results.json`, four command logs and per-command result JSON under scratch.
After proof, removed only the six throwaway Python harnesses created by this session.
Evidence JSON/logs and scratch outputs remain; no pre-existing or played artifact deleted.
Only this round-file evidence changes after the fully gated source/template head.

### Branch commits (in order)

| Commit | Work |
| --- | --- |
| `5c02eb5` | Two matching tested gifts released; exact Boomerang-flow comparison |
| `3ccbae4` | Approved isolated NUP cache-test repair after the keys guard |
| `bcfae67` | Bottle dependency and unrelated-experiment exclusion regression |
| `4a1c273` | Existing names regression and actual hints/play-note evidence |
| `e2cf231` | Cache-only CLI checks both emitted grants against the spoiler |
| `deddec9` | Scoped gift-release status and section 40 |
| `880cbc9` | Serialized verification-queue provenance |
| `187d1a2` | Verbatim child-Jabu answer, accepted normal minigames, alley-display note |
| This final evidence commit | Completed sweep/gates and review handoff |

Ready for Claude's combined keys/release review and gate/merge at this branch head; base
unchanged, no rebase, merge or push. No patch code changed; no new game test was staged or
run. Kareem's exact accepted files, original builders, live outputs and saves stayed read-only.
No remaining Track E implementation or verification blocker. First-expert gallery tests,
merchant experiments, unreleased Skulltula House checks and keysanity's in-game experiments
remain outside this release. Digging Save and Continue, adult-gallery repeat/reload and
Save and Continue between bowling wins remain unreported observations, not inferred passes.
