# Round 14: progressive items (cs14d, issue #13)

Branch `r14/progressive`, base `ffea543` (Clawshot 0.2.0). No version bump.
Research/generated output: `E:/OOTRemake/work/r14-progressive/`.
Dump and all game folders remain read-only. No game starts, merges or pushes.

## Feasibility first — verdict posted before pool implementation

Read AGENTS, README, CONTRIBUTING, architecture, orchestration round rules,
roadmap Round 14 Track D, world format, D16 and the fixed-tier/child-Bracelet
exemption, requested game-data sections 3/4/19/22/24/26/33/36/37/44 and rounds
r12-keys, r13-item-grants, r13-dungeon-items (relevant implementation/evidence).

`uv run python E:/OOTRemake/work/r14-progressive/probe_chest.py` read the real
supported dump through Clawshot's EVFL/zstd readers. Native small Event23 and
big Event90 call `GetPouchContentByActorNameForTreasureBox` with ContentName.
`GetPouchContent` Event11 sets the get-window actor before showing its message;
Event0 adds the actor only after the message. Selecting only at Event0 is too late
for tier-correct text. The rising model is a separately bound
`PouchContentGuestPerformer`, not the eventual pouch actor. A grant-only change
therefore does not establish tier-correct model presentation. Hookshot/Longshot
already share their model (section 22); visual similarity is not a selection proof.

Native `EventQueryIsExistInPouch {Actor, Num:1}` is the existing bag/tier query
(case0 held, case1 absent). The implementation instead uses
`GameDataActor.EventQueryIsGameDataBool` on saved `IsGet.<canonical pouch actor>`
(case0 acquired, case1 absent): acquisition history persists when an upgrade or
age transition changes current equipment/stock. Every used flag is checked against
the real GameDataList (saved file0, reset8); no new saved counter is invented.
`probe_ownership.py` independently printed native pouch rows and saved fields.
Strength uses `Armor_Child_Gauntlet_Goron` versus adult Silver/Gold canonical
identities, not the acquisition-only `Item_Gauntlet_*` names, which have no saved
IsGet fields. Wallet has starting Small200, upgrades Medium500/Large1000, no
native Tycoon tier. Exact native time-travel capability audit continues; only
Kareem's 2026-11-12 child-Bracelet/adult-gauntlet separation is played evidence.

Facts-only lead: `E:/OOTRemake/work/refs/sloperina-FINDINGS.md` section5.7:
menu/story checks need upgrade pouch items, not just capacity/depth numbers.
No GPL code copied. Kamil's findings and the OOTNS2 issue draft were read as ideas;
the latter does not contain the claimed 0.4.0 wallet implementation, so that claim
is not implementation evidence.

**Grant kinds:** source-bound chest events can select before the native get
window/grant. Gift direct-pouch and ordinary GetPouchContent calls are editable,
but hand-over wrappers also create/display actors and need independent tier
binding. Scrubs use those hand-overs inside successful-purchase branches.
Native shops require a supported physical shelf actor and purchase path; floor
checks use the native pickup actor, not an arbitrary event. Those paths do not
currently support a uniform next-tier copy. All progressive copies are therefore
Chest-only, including copies originating in shuffled gift/minigame checks.
Fixed native grants at unshuffled checks remain native.

Small `Event17` and big `Event25` query `EventQueryCanAddToPorch(ContentName)` and
can route to a display-only branch for the physical base actor. Progressive-only clones take the native
success path instead: an already-owned Hookshot base must not suppress the
selected Longshot grant. Native fixed callers retain their original capacity gate.
The rising model remains the base actor; the selected tier supplies the native
get-window name/text and pouch grant. Neither UI rendering nor event startup is
claimed played from event-graph tests.

## Product decisions / remaining question

**Kareem, via Claude, 2026-11-13: ALL eight chains are progressive: Hookshot,
strength, scales, wallets, bomb bag, quiver, slingshot bag, magic. Always on, no
setting. Kinds unable to grant the next tier receive no progressive copies.**
This supersedes the initial provisional scope. Claude also requires all new
player checks on Longshot, using the central Longshot template.

The child-Bracelet exemption remains: adult gauntlets are not child Bracelet.
Chest copies cannot let the logic invent a Bracelet from fixed adult gauntlets.
Native quiver/bullet capacity alone is not Bow/Slingshot ownership; first-copy
selection establishes the missing weapon before upgrading capacity.

**Spoiler concrete tiers are collection-order dependent. cs14d proposes listing
the family and ordered possible grants, plus the tier in a deterministic canonical
sphere replay, explicitly not a promise for a different collection route.**

## Verification / staging

`OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest
tests/test_progressive_events.py -x -q`: **10 passed**, including production
`changes()` on real resources, saved-flag validation, both native event registries
and serialized dispatch through every native tier. Initial synthetic assertion
printed two distinct native presentation/grant entries; an incidental duplicate
test was removed. The real-dump proof then exposed the additional native
`GetPouchContentByActorNameForShowPickUpWindow` branch; that actual grant path was
added and the cause-directed rerun passed. No failure was called fixture-only.

**Superseded/frozen initial packet; not for play (late popup still showed base):**
`E:/OOTRemake/work/r14-progressive/ingame/Test - progressive Hookshot and Scale.bat`.
Checklist `PROGRESSIVE-CHECKLIST.md` beside it; proof `staged-chests-proof.json`
in the scratch root. Common writer emitted **10 resources**. New Game in a fresh
empty profile; no existing save was copied or changed. Mido's two left chests give
Hookshot then Longshot in either order; his two right give Silver then Golden Scale.
Base rising models are intentional; native tier text/inventory and saved flags
are acceptance criteria. Save/Quit/Continue and once-only chest state are included.
**7–10 minutes; allow12 if the normal intro is slow.** Only Teleport/clock allowed.

The initial packet's actual cmd dry-run passed **exit0**, CRLF, exactly-one-mod
HOS_MODS, no overlay, selected Longshot `v3.0.0-rc.2/bin/longshot.exe`, isolated
`ingame/user-progressive-chests-next`; no game start or game log.
**Unplayed and superseded.** Do not play, reset or overwrite this old mod/profile.

Full suites/sweeps await Claude's gate queue and atomic `gate.lock` directory.
Adding five native tier actor mappings expands the extraction working set; rebuild
our own repaired-v131072 NUP fixture under `work/rounds/r14` before the dump gate.
Later stages use3 workers while neither exact game process runs (Claude's
2026-11-13 interjection; LongshotLauncher.exe alone does not count). No version bump.

## Approved child-strength exception and E dependency

**Claude, 2026-11-13, approved a deliberate exception to option (a): child
strength in seed logic comes only from Darunia's native Bracelet gift, through
his door with Lullaby and Saria's Song. The gift adds no progressive copy tier.
All three strength copies remain in chests; adult strength stays copy-only.
An early copy Bracelet physically works out of logic, but logic never relies on it.**

Reason: the closed-door return kit keeps strength copies adult-only to preserve
the Saria prerequisite before the pull. Ignoring the native child gift then
deadlocked child Dodongo access: the pre-exception seed0–2 probes all failed
(`Compass (Forest Temple): no reachable location`). Dropping the bypass allowed
an early pull without Saria, leaving adult Mido's return route blocked.
E's `work/r14-steps/ainb/FINDINGS.md:70-73` proves the DC flower/boulder path has
no quest-step precondition; a speculative Fire-quest gate cannot repair this.

The age-aware first-tier helper lives in world data. The quoted counted form
still reads the raw copy counter. Child bombs use the native Bracelet source,
not a copy. The return-kit lower bound now holds `Goron Bracelet:1` instead of
inventing an adult copy tier from it; the kit must supply its own first adult copy.

**Dependency, E's 10:37 static trace (unplayed): Fire stone, cavern and blue warp
do not need Darunia's dance, but opening the DC boulder first makes Darunia's Joy
uncollectable. Claude approved E's source-once/forward-step correction; it has
not yet landed or been played.**
The modeled child gift route reaches Goron City/Darunia's door directly without
passing the DC boulder. All-orders collectibility still depends on E's fix/proof.
The late-Bracelet check now runs only on the combined D/E build and opens the
boulder first. The equivalent early-bombs concern was posted for cs14e in one line.


## D/E contract and standalone proof

**Claude approved: E's source-once/forward-121 patch runs FIRST; D's
`progressive_bonus.changes(..., prior_changes=changes)` runs SECOND.**
D owns only the `Dm_Goron_0030/Event127` subflow replacement, preserving its
original `next` (including E's after-gift flag continuation) and native grant
parameters. Queries are appended to already-preloaded GetPouchContent as
`Clawshot_Bonus_Dm_Goron_0030_Event127`; D adds no movie actor. E owns Event121
and the HavePlayed gate/flag. D merges first; E rebases, inserts its step before D
and proves the combined flow on the real dump.

Standalone without E: `probe_bonus.py` compiled production `changes()` over the
real dump with no `prior_changes`, serialized/re-read the results, and exercised
unowned/owned Darunia, Diving21 and Fishing579/822 guards: PASS. Original quest/
once continuations remain. The first attempt printed Darunia's actor list and
proved there is no native movie GameDataActor; the fix reused the existing POUCH
query actor rather than inventing one. Timeline-only registry rows were printed
and handled explicitly. Native movie equipment matches only the
`Gauntlet_Goron_Equip` animation action, not another direct equipment/status setter.
This is native-data proof, not a played no-downgrade claim.

Focused native event/key integration: `focused.py --native
tests/test_progressive_events.py tests/test_key_bindings.py -x -q`:
**30 passed in6.23s**, workers3, no exact game process. The new unsafe-native
regression executes serialized grants/guards plus quest and once completion.

Child exception smoke: `probe_child_exception.py` printed the entire0–3-copy /
native-gift matrix: copies alone never enable child DC/bombs, native source enables
child but adds no adult tier. Actual default seed0 now generates with all20 copies,
three strength. The six native-source/door/Saria regressions passed in2.24s.

## Corrected D-only v2 packet; combined late-gift handoff

`ingame/Test - progressive upgrades v2.bat`, mod/profile
`progressive-chests-v2-next`; `PROGRESSIVE-V2-CHECKLIST.md`.
Four Mido copies plus sixteen diagnostic training-chest production-selector calls
cover all eight chains. Support is normal chest-granted Sword, Time Ocarina,
Saria, Lullaby and200 rupees, not a debug inventory or quest preset.
Ordinary generated seeds never bundle copies. Writer emitted14 resources;
`staged-chests-v2-proof.json` records physical bindings and file hashes.
`prove_packet_v2.py` passed every bundled tier sequence, the late-Bracelet skip
with all other movie actors/nodes unchanged, and source registry identities.
Actual cmd dry-run exit0 selected Longshot rc.2, one mod, unset overlay and a fresh
empty profile; no game started. The old packet/profile stay frozen, not reset.

**The late-native-gift check must run on E's combined build, not this D-only v2.**
E's combined checklist opens the DC boulder before Darunia, then exercises
source-once, forward-only quest progress and D's lower-tier skip together.
The v2 builder/bundle and checklist are available for E to reuse without touching
the frozen profile. Combined late-gift estimate30–45 minutes; capacity/scale
continuations and adult archery are separately labeled optional/unplayed.

