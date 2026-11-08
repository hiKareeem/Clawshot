# World format

Round 2, track B (cs2b); round 3, track C (cs3c) ported the whole world and added the remake's overrides. The logic
is data (AGENTS.md rule 6): regions joined by exits, with locations (checks) and events in them, each guarded by a
requirement in a small rule language. The syntax and the meaning are OoT Randomizer's (`data/World/*.json`,
`RuleParser.py`, MIT), so its region files translate by a tool, rule text unchanged; where the remake differs, a
hand-written overrides file says so, apart from the translation. Code: `src/clawshot/world/` (`rules.py` compiles
rules, `load.py` reads the files and applies the overrides, `search.py` answers reachability, `translate.py` ports
OoT Randomizer). Data: `src/clawshot/data/world/`.

## Files

| File | Holds | Written by |
|---|---|---|
| `world.toml` | `start` (region), `goal` (a rule), `files` (the region files to load), `overrides` (the overrides file); Clawshot's own `[settings]` and `[items]`, and `[progressive]` (tiers) | hand |
| `<area>.toml` | `[[region]]` entries, then a `[locations]` table | `translate` (from `port.toml`), never by hand |
| `remake.toml` | the remake's differences and Clawshot's per-location facts (below) | hand |
| `helpers.toml` | `[helpers]`: named rules, some with parameters | `translate` (`LogicHelpers.json`) |
| `items.toml` | `[items]`: every item the logic can name, with its type and class | `translate` (`ItemList.py`) |
| `settings.toml` | `[settings]`, `[tricks]`, `[flags]`: every name a rule may test | `translate` (OoT Randomizer defaults) |
| `port.toml` | which OoT Randomizer regions go into which file (with its Banc `area`), and the commit | hand |

Round 3 ports every region of `Overworld.json`, `Bosses.json` and the twelve vanilla dungeon files (Master Quest
is left out): 35 region files, 342 regions, 1370 locations. A boss room goes with its dungeon's file.

### A region

```toml
[[region]]
name = "Kokiri Forest"
scene = "Kokiri Forest"        # optional: OoT Randomizer's scene, hint area, dungeon
hint = "KOKIRI_FOREST"
area = "KokiriForest"          # the remake's Banc folder (the census `area`), from port.toml
source = "Overworld.json:154"  # where the region came from
# dungeon = "Deku Tree"        # a dungeon's own keys, maps and compasses stay in its regions
# time_passes = true           # both day and night are reachable here
# provides_time = "day"        # entering sets this time (a blue warp)

[region.events]
"Showed Mido Sword & Shield" = "is_child and Kokiri_Sword and Deku_Shield"  # Overworld.json:158

[region.locations]
"KF Kokiri Sword Chest" = "is_child"  # Overworld.json:161

[region.exits]
"KF Outside Deku Tree" = "is_adult or open_forest == 'open' or 'Showed Mido Sword & Shield'"  # Overworld.json:207
```

Every requirement notes where it came from: the translator writes OoT Randomizer's file and line as a comment
(and copies OoT Randomizer's own comments above it).

An **event** is something that, once done, stays done; it is held as an item of its name. Several regions may
define the same event; it is held once any of them passes. A rule names an event by a quoted name
(`'Showed Mido Sword & Shield'`) or a capitalised identifier (`Time_Travel`).

`[locations]` gives each location's OoT Randomizer type (`Chest`, `GS Token`, `NPC`, ...), its vanilla item (an
`items.toml` name) and its `LocationList.py` line. Location names are OoT Randomizer's; the census
(`src/clawshot/data/locations.toml`) links them to the remake's IDs through `oot_randomizer_name`.

### Overrides (`remake.toml` and `remake/*.toml`)

The translated files stay exactly what the translator writes (`tests/test_world_translate.py` compares them byte
for byte); everything written by hand is in `remake.toml` and the files of `remake/` (round 4: `child_<area>.toml`
and `adult_<area>.toml`, one per area and logic track), applied by the loader after the translated files:
`remake.toml` first, then `remake/*.toml` sorted by name (`load.apply_overrides`). One location, exit, event,
region, key count or item may be set in one file only; a second file setting it stops the build, naming both files.
New regions are added before any exit, event or location is applied, so a file may use a region another file adds.
Each entry needs a `source` (who or what says so):

```toml
[locations."Fire Temple GS Boss Key Loop"]
rule = "can_use(Megaton_Hammer)"   # the remake's requirement
was = "True"                       # the translated rule it replaces: a change upstream stops the build
source = "03-game-data.md section 9 (Kareem and the Eurogamer guide, 2026-11-07): ..."

[regions."Deku Tree Upper Floors"]  # a remake room OoT Randomizer folds into another region
area = "InsideTheDekuTree"
dungeon = "Deku Tree"
source = "..."

[exits."Deku Tree Lobby"."Deku Tree Upper Floors"]
rule = "can_use(Slingshot)"
new = true                         # an exit the translation lacks; a changed one gives `was` instead
source = "..."

[key_counts]
"Small Key (Water Temple)" = { count = 4, source = "census: 4 key chests (N64: 6); 8 chain locks = 4 doors" }

[items."Dins Fire"]
alias = ["Magic Meter", 1]         # collecting Din's Fire also counts as one Magic Meter
source = "PouchActorInfo Item_DinFire: ExpansionAvility MPMaxUP, MPMax 24"
```

| Table, field | Meaning |
|---|---|
| `[locations."<name>"]` | a location of the translated world |
| `rule` + `was` | the remake's requirement, replacing the translated one (which `was` repeats) |
| `region` | the region the location moves to (translated or from `[regions]`), its rule unchanged unless `rule` is given |
| `type` | the remake's kind of check, as an OoT Randomizer type (the Dampé race heart piece is a chest here) |
| `vanilla` | the item the remake gives here, where it differs (the swapped Great Fairies) |
| `vanilla_fixed` | with fixed items, the tier a check whose vanilla item is progressive gives (`LW Gift from Saria`: `Fairy Ocarina`) |
| `n64_only` | the check does not exist in the remake; the reason gives the evidence. Neither shuffled nor placed; set only with evidence |
| `area` | the census area, where the remake places the check outside its region's Banc folder (`Location.area`) |
| `keep_vanilla` | the check keeps its vanilla item though its type is shuffled (D17: the Treasure Chest Game room boxes) |
| `[regions."<name>"]` | a region the translation lacks, with `area`, `dungeon`, `scene`, `hint`, `time_passes`, `provides_time` |
| `[exits."<region>"."<target>"]`, `[events."<region>"."<event>"]` | `rule` with `was` (a change; `"False"` closes it) or with `new = true` (an addition) |
| `[key_counts]` | the remake's number of a dungeon's small keys, where it has fewer than N64: a rule asking for more asks for that many |
| `[items."<name>"]` | `alias = ["<item>", count]`: collecting the item also adds that many of another (an item without an alias of its own); the search counts both |

Remake-only checks use `[locations."<census definition name>"]` with `new = true`, `region`, `type`, `vanilla`,
`rule` and `source` (no `was`). The name must not already exist. They live in `remake/extra_<area>.toml`; a check
whose route is unresolved carries `keep_vanilla` with the specific reason rather than an invented access rule.
Gossip Stones are `[locations."<name>"]` too: an OoT Randomizer stone the remake lacks gets `n64_only`, a remake-only
stone `new = true` with `region`, `type = "HintStone"`, `rule` and `source` and no `vanilla`
(`remake/hint_stones.toml`). `census.hints.stone_labels()` ties each live stone to the message label it speaks.
The chest patch linker uses a definition's readable name when it has no OoT Randomizer name.
Existing region metadata can be set with `[regions."<name>"]`, `new = false` and `source`; exits, events and
locations stay intact. The tower explicitly belongs to `Ganons Castle` for dungeon-item placement.

**Key counts.** The census finds fewer small keys in three dungeons (Bottom of the Well 2 of 3, Water Temple 4 of
6, Ganon's Castle 1 of 2), and the remake's locked doors (`Obj_DoorChainLock_A_01`, one on each side of a door)
match those counts. Which N64 doors are gone is not known, so a rule's count is capped at the remake's: as long as
the remake's locked doors are N64 doors, no door needs more keys than OoT Randomizer's worst-order count or more
than the dungeon holds, so the cap never asks for fewer keys than a door needs.

`tests/test_world_census.py` holds the world to the census: every location of a type the census covers (`Chest`,
`BossHeart`, `Scrub`, `GrottoScrub`, `Shop`, `MaskShop`, `GS Token`, `Collectable`) is linked from a census
definition of the matching kind and area (`Location.area`), or is `n64_only`; the rest are *pending*. The test
prints the pending list and fails when it grows past `MAX_PENDING`. Other types are skipped by type: freestanding
rupees and hearts, pots, crates, beehives, wonder items, rupee towers, silver rupees (no census kind), and NPC,
cutscene, song and boss-reward gifts (event flows).

### Fixed or progressive items

`world.toml`'s `progressive_items` setting (default `false`, decision D16): with `false`
each check gives one fixed item, as the remake does without a code hook; with `true`, OoT Randomizer's progressive
items. `[progressive]` lists each progressive item's tiers (`"Progressive Hookshot" = ["Hookshot", "Longshot"]`);
the loader makes each tier an item that counts as that many of the progressive item, so every OoT Randomizer rule
(`Hookshot` = `Progressive_Hookshot`, `Longshot` = `(Progressive_Hookshot, 2)`) reads both kinds unchanged, and a
Longshot found first is a Longshot. With fixed items, a location whose vanilla item is progressive must say its
tier (`vanilla_fixed`), or the world does not build.

### Items, helpers, settings

`items.toml` lists every OoT Randomizer item: `type` (`Item`, `Song`, `SmallKey`, `Shop`, `Event`, `Drop`, ...),
`class` (`progression`, `priority` or `normal`: OoT Randomizer's advancement flag), and `bottle`, `medallion`,
`stone`, `alias` (a Heart Container also counts as four Pieces of Heart) where they apply. A `Map`, `Compass`,
`SmallKey`, `SmallKeyRing`, `BossKey` or `SilverRupee` named `... (<Dungeon>)` belongs to that dungeon.

`settings.toml` has three tables, merged into one namespace for rules:

- `[settings]`: OoT Randomizer settings the rules name, at its defaults (`open_forest = "closed"`, ...). A seed's
  settings may override them (`Settings.logic`), except `open_forest` / `skip_mido`, derived from `Settings.forest`.
- `[tricks]`: N64 tricks and glitches, all `false`. Turning one on is an error until it is verified in the remake
  (rule 6); the check is in `load.resolve_settings`.
- `[flags]`: OoT Randomizer `World` attributes derived from its settings (`entrance_shuffle`,
  `ensure_tod_access`, ...), at their values for its defaults: no entrance shuffle. Two are random in OoT
  Randomizer's `World` and are fixed by the translator: `skipped_trials` (all six trials active, its default
  `trials = 6`) and `selected_adult_trade_item` (`Pocket Egg`, where the unshuffled game starts the trade).

## The rule language

A rule is a Python expression, parsed with `ast` and never run as Python. It is compiled once, when the world is
built for a set of settings, into a test of (items held, age, time of day).

| Form | Meaning |
|---|---|
| `True`, `False` | always, never |
| `a and b`, `a or b`, `not a`, `( )` | as in Python |
| `Kokiri_Sword` | holds the item `Kokiri Sword` (spaces become `_`; `'()[]-` are dropped: `Rupees_5`) |
| `'Kokiri Sword'`, `'Showed Mido Sword & Shield'` | a quoted item, or an event if no item has that name |
| `(Progressive_Hookshot, 2)`, `(Gold_Skulltula_Token, bridge_tokens)` | holds at least that many (a number or a setting) |
| `is_child`, `can_use(Bow)` | a helper from `helpers.toml`; arguments are substituted into its text |
| `open_forest == 'open'`, `'Deku Tree' in dungeon_shortcuts`, `plant_beans` | settings: constants |
| `age == 'child'`, `age == starting_age` | the age the rule is evaluated for |
| `at_day`, `at_night`, `at_dampe_time` | the time of day the rule is evaluated at (see below) |
| `here(rule)` | an event in this region, held once `rule` passed here for either age |
| `at('Region', rule)` | the same, in another region |
| `has_bottle`, `has_stones(n)`, `has_medallions(n)`, `has_dungeon_rewards(n)`, `has_hearts(n)`, `can_live_dmg(h)`, `has_soul(x)`, `had_night_start` | built-ins, as OoT Randomizer's `State` defines them |
| `has_all_notes_for_song(s)`, `has_ocarina_buttons(n)` | `True` while `shuffle_individual_ocarina_notes` is off (OoT Randomizer then holds every button from the start); an error with it on |
| `region_has_shortcuts('R')` | `False` while `dungeon_shortcuts` is empty; an error otherwise |
| `skipped_trials[Forest]` | an entry of a setting that is a table (underscores become spaces) |
| `Time_Travel`, `Links_Cow` | a capitalised name that is not an item, helper or setting: an event |

A name is looked up in this order (OoT Randomizer's `visit_Name`): time-of-day built-ins, helpers, items, settings
(with tricks and flags), the other built-ins, events. Anything else is an error that names the rule
(`region 'X', location 'Y': unknown name Z`), raised when the world is built. So are syntax errors, a helper that
calls itself, a wrong number of helper arguments, comparing `age` with anything but an age, and a setting holding
text used as a condition.

**Settings fold.** Settings are constants, so `open_forest == 'open'` becomes `True` or `False` and the rule
around it shrinks. An `and`/`or` stops at the first operand that decides it, as in OoT Randomizer: a branch a
setting switches off is never compiled, so it may name a built-in this engine lacks (`has_item_goal`, ...);
reaching one in a live branch is an error.

**`here()` and `at()`** are OoT Randomizer's subrules: each becomes an event named `<Region> Subrule <n>`, held
once its rule passes in that region for either age. That is how "a bean planted as child lets the adult ride the
platform" works: the adult's rule asks for the event the child set.

## Reachability

`Search(world, items)` (ported from OoT Randomizer's `Search.py`): from the start region, child and adult are
searched separately. Before adult return unlocks, child uses an independent pre-pull item/event view; adult also
uses adult finds. After return, they share inventory. A region is reached for an age at day, at night or both.
An exit is taken when its rule passes for that age at that time; the target is reached at the same time, both
times if `time_passes`, or its `provides_time`. Events are done whenever their rule passes in a reached region, and
the search repeats until nothing changes. Collecting more items only adds, so the search resumes where it stopped.
An exit, event or location whose rule failed is tried again only once a count its rule reads grows (the compiler
records the item and event names each rule reads, `Rule.reads`), or, for an event or location, once its region is
reached at a new age or time of day.

**Start items.** `World.start_items` are held before any check: the five ocarina buttons when notes are not
shuffled, and Scarecrow's Song when `scarecrow_behavior = "free"`. The remake gives no starting dungeon keys.
The N64 free Fire Temple key is not carried over; its eight real keys must be collected from checks.

**Ages.** OoT Randomizer's start region `Root` is reached by both ages, and its exit to `Root Exits` needs
`is_starting_age or Time_Travel`. The other age therefore starts only once the event `Time Travel` is held, which
the Temple of Time's Master Sword Pedestal gives (an `Event` location in OoT Randomizer, an event here).

The remake gates reverse travel on Forest quest completion. `world.toml` settings `age_return_event` and
`age_return_region` name the completion event (`Defeat Phantom Ganon`, not the shuffled medal) and adult
pedestal (`Beyond Door of Time`). Until both hold, child checks/events can use only starting inventory and
items obtainable in a child-only prefix, never adult finds or their aliases. That prefix can finish before
the chosen first pull; already-collected checks can join it without granting their item twice.
An adult start has no child prefix before return. A partial world's missing gate stays closed.

`age_return_guarantee = true` (provisional default, reviewer, round 5) adds a separate acceptance proof:
cap each pre-pull item count in child-only collection to find its mandatory minimum for `age_pull_event`
(`Time Travel`), then prove adult can open return with only those counts, starting inventory and adult checks.
This includes the pull route's child prerequisites, not optional errands. Alternative routes may yield a
conservative intersection and rejection. Off retains temporal correctness but does not promise safety after
an early pull. Child-only goals that never open travel need no return proof.

`free_time_travel = false` by default. With it on, the search uses unrestricted shared inventory and skips the
extra return proof; `make_seed` automatically pairs that assumption with `patch.age`'s isolated pedestal
placement transform. The Forest quest, sage reward and Sheik/Prelude gates remain unchanged. In-game proof
is pending (`03-game-data.md` section 16); no GameDataList return-unlock Bool exists.

**Time of day.** Without entrance shuffle OoT Randomizer assumes any time of day can be reached from wherever the
player stands, and `at_day`/`at_night` are `True` (`RuleParser.at_day`: unless `world.ensure_tod_access`). Clawshot
keeps that: `ensure_tod_access` is `false` in `[flags]`. With it `true`, the rules test the time the region was
reached at, and Sun's Song (Ocarina and `Suns Song`) turns day to night and back; `at_dampe_time` is night (OoT
Randomizer's `TimeOfDay.DAMPE` bit, which `provides_time = "dampe"` names).

**Goal.** `world.toml`'s `goal` is a rule over items and events, without age: `Triforce`, the event of beating
Ganon (round 2's partial port used `'Defeat Queen Gohma'`).

**Key logic and the vanilla placement.** OoT Randomizer counts a dungeon's small keys for the worst order in which
its doors could be opened, so its own vanilla key layout is not always provably enough: the Spirit Temple's Silver
Gauntlets chest asks for 5 keys, and the vanilla child side holds 2. The vanilla-placement test therefore holds each
dungeon's small keys from the start; key logic is exercised by the seed tests, where the fill places keys.

## Generating a seed

`python -m clawshot --romfs <dump> --seed <n> --out <dir>` uses `clawshot.generate` and writes changed
resources under `<dir>/romfs/` plus `<dir>/spoiler.json`:

1. The world is built for the seed's logic settings; the locations whose OoT Randomizer type is in
   `Settings.shuffle` (default `Chest`, M2's chest shuffle), that have a vanilla item and are neither `n64_only` nor
   `keep_vanilla` are shuffled, every other location keeps its vanilla item. The pool is the vanilla items of the
   shuffled locations.
2. With the return guarantee on and free travel off, first forward-place `age_return_fill_families` at
   adult-reachable checks from `age_return_fill_inventory` plus adult pickups. Sources in
   `age_return_bypass_families` additionally need strictly adult-only destinations: strength tiers otherwise
   bypass the child's Saria/bracelet dependency and strand adult at Mido. Small keys bootstrap first, boss keys
   last. The independent first-pull oracle checks the finished placements, not just this construction.
   Then OoT Randomizer's assumed fill, with `random.Random(seed)`: restricted items first (a dungeon's keys, maps and
   compasses, when `dungeon_items = "own_dungeon"`; boss keys, then small keys, then the rest), then progression
   items, each to a location reachable while assuming every item not yet placed; then priority items (restriction
   only); then the rest, anywhere. With Shop enabled, filler also uses restriction checks: type-held items precede
   flexible filler within the native-display ordering, so rupees cannot consume Scrub-only capacity destinations.
   A failed fill is retried with the same generator, up to 10 times.
3. The beatability search on the result: collect sphere by sphere from the start; the goal must hold. A seed that
   fails is never returned.
4. The spoiler log, JSON: `generator` (with version), `seed`, `settings`, `settings_string`,
   `placements` (shuffled locations, world order), `spheres` (the progression items collected in each sphere;
   spheres with none are left out).

Same seed, settings, data and generator version give the same bytes: the generator is the only randomness, and the
fill walks lists in world-file order, never a set (a test compares two interpreters with different hash seeds).

### Replayable generator settings

Generator defaults live in `data/settings.toml`, separate from the translated `data/world/settings.toml`.
`Settings.to_string()` / `from_string()` and CLI `--settings` / `--print-settings` use versioned canonical `CS1`
strings; explicit CLI options override a supplied string. Effective gift restrictions are rebuilt on replay.
The same generator/world data and seed are required; strings do not promise cross-version compatibility.

`forest=closed` is the vanilla-like default (D24, Kareem). Advanced opt-ins `closed_deku` and `open` open the
bridge only or bridge plus Mido. Legacy `--skip mido` aliases `forest=open`. The GameData bridge-control flag
and Mido flag are separate; the logic derives the corresponding `open_forest` and `skip_mido` constants.
Initial-value transforms compose before gift-added saved Bools, preserving both sets of GameDataList changes.

`songs=song` keeps songs on song checks; opt-in `anywhere` releases all twelve. Non-song gift-only items
require the sourced chest actor allowlist before leaving gifts. Native Shop displays remain mandatory.
Shop wallet predicates use the same effective-price decision as the overlay: `shop_prices=affordable`
prices shuffled offers at 10; provisional default-on `cheap_deku_shield` prices the actual Kokiri shop shield
at 10 even without Shop shuffle. Stock/release, refill and adult-only rules stay intact.
Flag sources, inference limits and pending player checks: `03-game-data.md` section 21.

The overlay writer's `make_seed` supplies the remake's actual chest pool through census actor identities and
`item_actors.toml`, not the untranslated N64 chest contents. Native shops use their catalog; gift checks join
only when their fixed logic item matches the actor every grant step gives. Unresolved upgrade tiers stay vanilla.

## Porting OoT Randomizer

```sh
uv run python -m clawshot.world.translate --ootr E:/OOTRemake/work/r2-world/OoT-Randomizer
```

Reads `port.toml`, checks the checkout is at its `ootr_commit`, and rewrites the region files, `helpers.toml`,
`items.toml` and `settings.toml`. What it does with OoT Randomizer's data:

- Region fields `scene`, `hint`, `dungeon`, `time_passes`, `provides_time` are kept, and `area` is added from
  `port.toml`; `savewarp`, `is_boss_room` and `alt_hint` (entrance shuffle and hints) are dropped for now; any other
  field stops it.
- Locations of type `Drop` and `Event` (Deku Baba sticks, gossip stone fairies, the Master Sword Pedestal's
  `Time Travel`) become events named after the item they give; two in one region merge as `(a) or (b)`.
- `HintStone` locations (Gossip Stones) hold nothing: they are written with their rule and type `HintStone`, no
  vanilla item, and the loader builds them into `World.hint_stones` (a place to read a hint), not `World.locations`,
  so the fill and the beatability search never see them. `Hint` locations (the altar, Ganondorf) are left out.
- `settings.toml` gets every name the written rules (and all helpers) test that OoT Randomizer resolves to a world
  attribute, a setting or a trick, at OoT Randomizer's defaults, plus the few the engine always reads.
- `[flags]` values that OoT Randomizer's `World` draws at random are fixed (above).
- Its report (printed as JSON) lists `regions_not_ported`: regions of OoT Randomizer's files that `port.toml` names
  in no file (Master Quest files aside).

`test_world_translate.py` translates `port.toml` into a temporary folder and compares the result with the
committed files byte for byte, and checks no region of OoT Randomizer's world is left out, when `OOTR_DIR` points
at the checkout. Nothing in a translated file is edited by hand: the remake's differences are in `remake.toml`.

## Not carried over yet

- Savewarps, entrance shuffle.
- `logic_no_night_tokens_without_suns_song` (an `at_night` special case for Gold Skulltulas).
- Built-ins `has_item_goal`, `has_full_item_goal`, `has_all_item_goals`, `guarantee_hint`, `item_name`, `won`
  (hints and goals), and `has_all_notes_for_song`/`has_ocarina_buttons`/`region_has_shortcuts` with the settings
  that make them depend on the seed: errors if a live rule reaches them.
- Upgrades other than the five tiered items (quivers, bomb bags, bullet bags beyond the one above, the second
  magic meter): OoT Randomizer's rules only ask whether the base item is held, so they need no tiers, and none is
  in a chest; the gifts that give them need `vanilla_fixed` once gifts are shuffled.
