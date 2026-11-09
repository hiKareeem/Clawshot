# Round 7, Track G: bombs need Goron's Bracelet (cs7g)

Branch `r7/bombs`. Read AGENTS/README, plans 00–04 and decisions, all round-5/6 reports,
Round 7's shared-file opening, section30 and `r7-play.md`. No game/window/launcher/build,
save/dump write, played-output rewrite, dependency edit, merge, push, stash or terminal control.
Research and generated smoke output stay under `E:/OOTRemake/work/r7-bombs-cs7g/`.

## Item 1: native lift grades and sourced helpers

`lift_audit.py` reads the player's PouchActorInfo and actor packs through our format readers.
Build e0f3ccfa. Canonical grants (inventory actors, not the UI-only Pouch actors):

| Logic item | Native actor / equipment | LiftGradeUP | Applicable age |
|---|---|---|---|
| Goron Bracelet | Item_Gauntlet_Goron / Armor_Child_Gauntlet_Goron | Low (3655598229), GoronGauntlet special deal | Child; also adult's first strength tier |
| Silver Gauntlets | Item_Gauntlet_Silver / Armor_Adult_Gauntlet_Silver | Middle (3064057055), Gauntlet; AdultEquipment | Adult |
| Golden Gauntlets | Item_Gauntlet_Gold / Armor_Adult_Gauntlet_Gold | High (375060617), Gauntlet; AdultEquipment | Adult |

The three GameParameter/ExpansionAbilityActor resources corroborate those grades. Item_Bomb
requires Low; Item_Bombchu requires None (3069107721). Bomb Flower A_01 inherits the bomb's
Low grade, with its own fruit LiftableParam also Low. Section30's native comparison is required
<= available. Metadata does not newly certify the pending gameplay comparison.

`remake/bombs.toml` replaces four helpers, each with exact `was` and evidence `source`:
- `Bombs`: bag plus actual Bracelet as fixed child, any strength tier as adult. Progressive mode
  recognizes its first strength tier as the Bracelet. Fixed Silver/Golden aliases alone cannot
  stand in for the child's Bracelet.
- Both Octorok bomb helpers: replace their direct `Bomb_Bag` shortcut with `Bombs`, preserving
  every non-bomb alternative and soul check.
- `can_use(item)`: classify Bombs through that same predicate; other categories unchanged.

Audit of all world-data `Bomb_Bag` predicates found only Bombs, those two Octorok shortcuts,
and the two Bombchu supply helpers. The latter retain their existing rules. `has_bombs` is not
an existing helper here; no unused alias is added. `has_explosives`, `has_both_explosives`,
`can_blast_or_smash`, combat/projectile helpers and bomb-only tricks inherit the guarded Bombs
predicate. Existing local flower routes already require strength (DMT entrance, GC pot, DC,
Beamos/Dodongo flower helpers); they gain neither a bag requirement nor a new bomb supply.
Translated files remain untouched.

Shared prerequisite `12f413a` changes only `world/load.py`: helper overrides use existing
rule/was/source validation and duplicate-owner detection. Posted to cs-r7 before/after the
commit. Live synthetic Search printed bag-only wall false, strength-added true.
World-format schema documentation is a separate shared-file-only commit.

### Diagnostics and checks

- First live probe used the prose spelling `Gorons Bracelet`; printed world.toml shows the actual
  tier is `Goron Bracelet`. Corrected the data before full-world generation. Unknown capitalized
  identifiers can be events, so the tests use the real fixed item and require real route behavior.
- A surgical edit's response exposed incorrect fixture anchors; re-read exact lines and repaired
  them before any execution.
- First targeted test run: 8 failed, 9 passed; all failures printed `unknown name glitch_equip_swap`.
  The synthetic trick fixture had discarded all other trick defaults. Preserve those defaults,
  moving only glitch_groundjump to the synthetic settings table. Production tricks remain off.
- Cause-aimed rerun: `uv run pytest tests/test_world_remake_bombs.py -q`: **17 passed**.
  Covers independent helper paths, age tiers, wake-on-Bracelet, missing bag, progressive mode,
  synthetic bomb-only trick, unchanged Bombchu/Hammer/flower alternatives and override refusals.

**Kareem: on the existing 7c save, obtain Darunia's unshuffled Bracelet and retry the same bombs;
expected: they stop canceling. Bombchus should still work without strength. Record whether the
real Bomb Bag was obtained before the comparison.** No new launcher or game patch is needed.

## Item 2: seed/search acceptance

`uv run python -u E:/OOTRemake/work/r7-bombs-cs7g/verify_seeds.py` exercised the actual
`clawshot.__main__.main` four times, with pass-through wrappers counting real fill attempts.
Every invocation wrote a fresh folder in `seed7-matrix-next/`; no prior seed/user was rewritten.
The writer, hints, spoiler and play note all ran. Re-read written placements and independently
ran `Search.collect_spheres` plus `won()` (including the gated return proof).

| Seed7 mode | Attempts / bound | Shuffled checks | Collection spheres | Written files including spoiler/note |
|---|---|---|---|---|
| Chest | 1 / 10 | 164 | 25 | 81 |
| Chest+Shop | 3 / 10 | 228 | 24 | 99 |
| Chest+Shop+Gift | 10 / 10 | 278 | 27 | 142 |
| Default string `CS1` | 1 / 10 | 164 | 25 | 81 |

The gift mode succeeds **on the last permitted attempt**, not with a raised bound. Its failed
attempts (native Bombchu capacity and song placement), and Shop's two Fire-key failures, are
retained in external `seed-proof.json` and the four `cli-*.log` transcripts. No seed, goal,
settings or placement-policy reroll was used. This is limited headroom, not an unbounded guarantee.

Fixed 7b replay follows cs7f's available `work/r7-play-cs7f/old_seed.py` reconstruction (the
older `work/r7-play/old_seed.py` is absent). Read its spoiler only; fill nothing. Resolve the
remaining fixed native chest items from census/actor mappings, overlay its **228 exact shuffled
placements**, run the current chronological search: **won=True, 25 spheres**. Assert the 228-row
mapping and the source spoiler bytes unchanged. No 7b/7c file is written.

`tests/test_world_remake_bombs.py`: **17 passed**. The unchanged existing 200-default-seed,
20-progressive-seed, vanilla-world and cross-process determinism tests all passed in the first
full synthetic run. That complete run was **610 passed, 79 skipped, 9 failed**: the nine
failures were old route fixtures treating bag-only bombs as usable, not seed-generation failures.
The `&&` chain stopped there, so no full dump result is attributed to that attempt.

Printed failures named Colossus fairy wall, Shadow statue bridge, three Spirit routes, two Water
routes and two fairy-grave cases. Shared test-only commit `5c9c96c` keeps the route assertions,
adds bag-only negative then Bracelet-positive transitions, and supplies strength in the existing
Jabu usable-bombs-versus-projectile negative case (otherwise that check would become vacuous).
Cause-aimed five-file targeted run: **52 passed**. Four full corrected gates follow at handoff.

## Item 3: bomb-use timing and unsatisfied rules

For each successful matrix placement, rebuild two worlds: current helpers, and only those four
helpers restored to their guarded `was` bodies. Replay **the same placements** in both; never
compare two differently filled seeds. A disposable non-pool observer at `Root Exits` uses `Bombs`
and grants only Nothing, so collection records the first sphere when ordinary bombs are usable.
The full chronological search preserves child-prefix provenance. Spheres below are **1-based**,
including the observation sphere, not a physical action performed in game.

| Placement sample | Pre-D30 first usable bombs | D30 first usable bombs |
|---|---|---|
| Seed7 Chest | 3 | 5 |
| Seed7 Chest+Shop | 6 | 6 |
| Seed7 Chest+Shop+Gift | 4 | 7 |
| Seed7 default `CS1` | 3 | 5 |
| Fixed old 7b | 7 | 7 |

Later in **3/4 matrix invocations**, or **2/3 distinct shuffle-mode outputs** (Chest and CS1
are the same configuration); unchanged in old 7b. Every baseline/current replay wins, and there
are **zero newly uncollected checks** in all five comparisons. `seed-proof.json` retains the
full sphere/item witnesses, missing-check sets and attempt diagnostics.

7b's witness: Darunia's Bracelet and GC8 Bombchus in sphere5; vanilla Bowling/Rolling-Goron bag
rewards in sphere6; usable ordinary bombs in sphere7; KF Storms Grotto bag in sphere11. This
distinguishes first usable bombs from the particular bag named by its hint. The unchanged 7b
placement remains playable in the oracle; no new-seed D25 restriction is imposed on its old rows.

The independent two-worker timing sweep ran `generate(load_spec(), n, Settings())` for **all
200 seeds, n=0..199**, then the same matched-placement pre-D30/D30 observer replay. This is
the existing logic-level default pool, not a claim that 200 dump-backed CLI overlays were built.
Every generated seed and both replay oracles win: **153 later, 47 unchanged, 0 earlier**.
No newly uncollected checks in any of the 200. External `timing-sweep.json` lists every seed's
before/after sphere and missing-check set. The sweep completed once without failure or reroll.

### Independent runtime proofs

Full helper-backed synthetic Search (not a mock): pre-D30 bag-only opens Wall, Explosion, Rock
and both Octorok alternatives. D30 bag-only opens none. Collecting the real `Goron Bracelet`
wakes all six paths, including `can_use(Bombs)`.

`rule_audit.py` independently compiles pre-D30 and D30 full worlds, supplies an upper-bound
inventory (100 of each item-table identity, including logical Drop/Event items), and checks exits,
events, locations and hint stones across child/adult and day/night. **2,405 rules** in each
world; **zero newly impossible** and zero newly possible with that inventory. This does not
claim every pre-existing disabled/N64-only rule is satisfiable. External `rule-audit.json`
records the result.

The completed matrix, rule-audit and timing-sweep throwaway drivers were removed after their
results were recorded; JSON evidence and CLI transcripts remain. `lift_audit.py` is retained
as the read-only native-metadata reproducer. The four fresh CLI outputs remain staged under
`seed7-matrix-next/`; no launcher/user folder was created and no played output was deleted.

## Commit ledger and review boundary

| Commit | Scope |
|---|---|
| `12f413a` | Shared loader only: guarded helper overrides |
| `6e5e179` | Item1: sourced bomb logic, native grades and section31 |
| `3179407` | Shared world-format documentation only |
| `5c9c96c` | Shared test fixtures only: usable-bomb preconditions and transition checks |
| `fbf8b59` | Item2: bomb regressions, real CLI matrix and exact 7b acceptance evidence |
| `39205e6` | Item3: matched-placement timing and no-newly-impossible-rule evidence |

No production generator/fill, retry bound, item pool, settings default, shop/Bombchu policy,
actor parameter, saved flag or played seed was changed. `decisions.md` remains reviewer's.
The final report-only commit follows this ledger; its hash is posted with the handoff.

**Left for Kareem:** the existing 7c same-bombs-before/after-Darunia-Bracelet comparison in
item1. This is still unplayed here; no game success is inferred from metadata or search.
**Left for Claude:** review/merge these scoped commits; Gift seed7's attempt10 result is
explicit headroom risk, not a hidden increased retry budget or a request to change policy.

## Final four gates and handoff

All four complete commands passed on the final source/test tree (report-only edits afterwards):

| Command | Result |
|---|---|
| `uv run ruff format --check` | 205 files already formatted |
| `uv run ruff check` | All checks passed |
| `uv run pytest` | 619 passed, 79 skipped; 292.48s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | 78 passed, 620 deselected; 762.32s |

The two pytest invocations used only `PYTEST_ADDOPTS=--basetemp=...` to put temporary data at
`E:/OOTRemake/work/r7-bombs-cs7g/gate-fixed-{synthetic,dump}-next`. No test filtering beyond
the prescribed dump marker; the unchanged 200-default/progressive/determinism and new bomb
regressions all passed. The only full-chain retry followed the printed nine stale fixture
causes and their targeted fix; no production requirement, seed, bound or assertion was weakened.

After success, removed exactly the three session-created gate basetemps (the failed first
synthetic run and both corrected runs) with Python's junction-safe `shutil.rmtree`, checking
that each root was an existing non-symlink. No active gate process or temporary driver remains.
Retained the native read-only lift reproducer, three JSON evidence files and four CLI logs,
plus the four new CLI outputs staged for review. No played output or user/save was touched.

**Track G items1–3 complete and ready for Claude's review on `r7/bombs`.** No merge, push,
rebase or dependency change. Gameplay confirmation remains explicitly Kareem's check above;
metadata/search success is not an invented in-game result.
