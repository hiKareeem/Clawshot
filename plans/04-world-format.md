# World format

Round 2, track B (cs2b). The logic is data (AGENTS.md rule 6): regions joined by exits, with locations (checks)
and events in them, each guarded by a requirement in a small rule language. The syntax and the meaning are OoT
Randomizer's (`data/World/*.json`, `RuleParser.py`, MIT), so its region files translate by a tool, rule text
unchanged. Code: `src/clawshot/world/` (`rules.py` compiles rules, `load.py` reads the files, `search.py` answers
reachability, `translate.py` ports OoT Randomizer). Data: `src/clawshot/data/world/`.

## Files

| File | Holds | Written by |
|---|---|---|
| `world.toml` | `start` (region), `goal` (a rule), `files` (the region files to load) | hand |
| `<area>.toml` | `[[region]]` entries, then a `[locations]` table | `translate` (from `port.toml`), then hand edits |
| `helpers.toml` | `[helpers]`: named rules, some with parameters | `translate` (`LogicHelpers.json`) |
| `items.toml` | `[items]`: every item the logic can name, with its type and class | `translate` (`ItemList.py`) |
| `settings.toml` | `[settings]`, `[tricks]`, `[flags]`: every name a rule may test | `translate` (OoT Randomizer defaults) |
| `port.toml` | which OoT Randomizer regions go into which file, and the commit | hand |

### A region

```toml
[[region]]
name = "Kokiri Forest"
scene = "Kokiri Forest"        # optional: OoT Randomizer's scene, hint area, dungeon
hint = "KOKIRI_FOREST"
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
(and copies OoT Randomizer's own comments above it). A requirement changed after a check in the remake becomes a
table that says so:

```toml
"KF Kokiri Sword Chest" = { rule = "True", source = "verified: Kareem, build e0f3ccfa, 2026-11-20" }
```

`[locations]` gives each location's OoT Randomizer type (`Chest`, `GS Token`, `NPC`, ...), its vanilla item (an
`items.toml` name) and its `LocationList.py` line. Location names are OoT Randomizer's; the census
(`src/clawshot/data/locations.toml`, track A) links them to the remake's IDs through `oot_randomizer_name`.

An **event** is something that, once done, stays done; it is held as an item of its name. Several regions may
define the same event; it is held once any of them passes. A rule names an event by a quoted name
(`'Showed Mido Sword & Shield'`) or a capitalised identifier (`Time_Travel`).

### Items, helpers, settings

`items.toml` lists every OoT Randomizer item: `type` (`Item`, `Song`, `SmallKey`, `Shop`, `Event`, `Drop`, ...),
`class` (`progression`, `priority` or `normal`: OoT Randomizer's advancement flag), and `bottle`, `medallion`,
`stone`, `alias` (a Heart Container also counts as four Pieces of Heart) where they apply. A `Map`, `Compass`,
`SmallKey`, `SmallKeyRing`, `BossKey` or `SilverRupee` named `... (<Dungeon>)` belongs to that dungeon.

`settings.toml` has three tables, merged into one namespace for rules:

- `[settings]`: OoT Randomizer settings the rules name, at its defaults (`open_forest = "closed"`, ...). A seed's
  settings may override them (`Settings.logic`).
- `[tricks]`: N64 tricks and glitches, all `false`. Turning one on is an error until it is verified in the remake
  (rule 6); the check is in `load.resolve_settings`.
- `[flags]`: OoT Randomizer `World` attributes derived from its settings (`entrance_shuffle`,
  `ensure_tod_access`, ...), at their values for its defaults: no entrance shuffle.

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
| `Time_Travel`, `Links_Cow` | a capitalised name that is not an item, helper or setting: an event |

A name is looked up in this order (OoT Randomizer's `visit_Name`): time-of-day built-ins, helpers, items, settings
(with tricks and flags), the other built-ins, events. Anything else is an error that names the rule
(`region 'X', location 'Y': unknown name Z`), raised when the world is built. So are syntax errors, a helper that
calls itself, a wrong number of helper arguments, comparing `age` with anything but an age, and a setting holding
text used as a condition.

**Settings fold.** Settings are constants, so `open_forest == 'open'` becomes `True` or `False` and the rule
around it shrinks. An `and`/`or` stops at the first operand that decides it, as in OoT Randomizer: a branch a
setting switches off is never compiled, so it may name a built-in this engine lacks
(`has_all_notes_for_song`, `region_has_shortcuts`, ...); reaching one in a live branch is an error.

**`here()` and `at()`** are OoT Randomizer's subrules: each becomes an event named `<Region> Subrule <n>`, held
once its rule passes in that region for either age. That is how "a bean planted as child lets the adult ride the
platform" works: the adult's rule asks for the event the child set.

## Reachability

`Search(world, items)` (ported from OoT Randomizer's `Search.py`): from the start region, child and adult are
searched separately, sharing one set of items and events. A region is reached for an age at day, at night or both.
An exit is taken when its rule passes for that age at that time; the target is reached at the same time, both
times if `time_passes`, or its `provides_time`. Events are done whenever their rule passes in a reached region, and
the search repeats until nothing changes. Collecting more items only adds, so the search resumes where it stopped.

**Ages.** OoT Randomizer's start region `Root` is reached by both ages, and its exit to `Root Exits` needs
`is_starting_age or Time_Travel`. The other age therefore starts only once the event `Time Travel` is held, which
the Temple of Time's Master Sword Pedestal gives (an `Event` location in OoT Randomizer, an event here). Round 2's
port ends before the Temple of Time, so in the ported world only the child moves; the synthetic tests cover the
adult.

**Time of day.** Without entrance shuffle OoT Randomizer assumes any time of day can be reached from wherever the
player stands, and `at_day`/`at_night` are `True` (`RuleParser.at_day`: unless `world.ensure_tod_access`). Clawshot
keeps that: `ensure_tod_access` is `false` in `[flags]`. With it `true`, the rules test the time the region was
reached at, and Sun's Song (Ocarina and `Suns Song`) turns day to night and back; `at_dampe_time` is night.

**Goal.** `world.toml`'s `goal` is a rule over items and events, without age. Round 2: `'Defeat Queen Gohma'`.

## Generating a seed

`clawshot.generate` (`python -m clawshot.generate --seed <n> --out <dir>` writes `<dir>/spoiler.json`):

1. The world is built for the seed's logic settings; the locations whose OoT Randomizer type is in
   `Settings.shuffle` (default `Chest`, M2's chest shuffle) and that have a vanilla item are shuffled, every other
   location keeps its vanilla item. The pool is the vanilla items of the shuffled locations.
2. OoT Randomizer's assumed fill, with `random.Random(seed)`: restricted items first (a dungeon's keys, maps and
   compasses, when `dungeon_items = "own_dungeon"`; boss keys, then small keys, then the rest), then progression
   items, each to a location reachable while assuming every item not yet placed; then priority items (restriction
   only); then the rest, anywhere. A failed fill is retried with the same generator, up to 10 times.
3. The beatability search on the result: collect sphere by sphere from the start; the goal must hold. A seed that
   fails is never returned.
4. The spoiler log, JSON: `generator` (with version), `seed`, `settings`, `placements` (shuffled locations, world
   order), `spheres` (the progression items collected in each sphere; spheres with none are left out).

Same seed, settings, data and generator version give the same bytes: the generator is the only randomness, and the
fill walks lists in world-file order, never a set (a test compares two interpreters with different hash seeds).

## Porting OoT Randomizer

```sh
uv run python -m clawshot.world.translate --ootr E:/OOTRemake/work/r2-world/OoT-Randomizer
```

Reads `port.toml`, checks the checkout is at its `ootr_commit`, and rewrites the region files, `helpers.toml`,
`items.toml` and `settings.toml`. What it does with OoT Randomizer's data:

- Region fields `scene`, `hint`, `dungeon`, `time_passes`, `provides_time` are kept; `savewarp`, `is_boss_room`
  and `alt_hint` (entrance shuffle and hints) are dropped for now; any other field stops it.
- Locations of type `Drop` and `Event` (Deku Baba sticks, gossip stone fairies, the Master Sword Pedestal's
  `Time Travel`) become events named after the item they give; two in one region merge as `(a) or (b)`.
- `Hint` and `HintStone` locations hold nothing and are left out.
- `settings.toml` gets every name the written rules (and all helpers) test that OoT Randomizer resolves to a world
  attribute, a setting or a trick, at OoT Randomizer's defaults, plus the few the engine always reads.

A `test_world_translate.py` test reruns the translator into a temporary folder and compares bytes with the
committed files when `OOTR_DIR` points at the checkout. Once a file carries hand edits for the remake, that test
will need an override layer or the file leaves the translator; round 3 decides.

## Not carried over yet

- Shop prices and wallets (OoT Randomizer `Rules.set_shop_rules`), savewarps, entrance shuffle.
- `logic_no_night_tokens_without_suns_song` (an `at_night` special case for Gold Skulltulas).
- Built-ins `has_all_notes_for_song`, `has_ocarina_buttons`, `region_has_shortcuts`, the goal-hint ones: errors if
  a live rule reaches them.
- Progressive items: OoT Randomizer's pool and rules use `Progressive Hookshot` and the like. Without code hooks a
  remake chest gives one fixed actor, so the item mapping (logic item to remake actor) must decide how these read.
