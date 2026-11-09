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

Compare identical placements under pre-D30 and D30 rules; report first usable-bomb sphere,
not the first ammo pickup. Do not compare rerolled placements as if they were the same seed.

### Independent runtime proofs

Full helper-backed synthetic Search (not a mock): pre-D30 bag-only opens Wall, Explosion, Rock
and both Octorok alternatives. D30 bag-only opens none. Collecting the real `Goron Bracelet`
wakes all six paths, including `can_use(Bombs)`.

`rule_audit.py` independently compiles pre-D30 and D30 full worlds, supplies an upper-bound
inventory (100 of each real item; events still follow their actual rules), and checks exits,
events, locations and hint stones across child/adult and day/night. **2,405 rules** in each
world; **zero newly impossible** and zero newly possible with that inventory. This does not
claim every pre-existing disabled/N64-only rule is satisfiable. External `rule-audit.json`
records the result.
