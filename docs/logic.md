# Logic reference for ports and trackers

Clawshot's access model is reusable data, not a claim that N64 rules match this remake. This guide
maps the data and contracts for a tracker or a possible Archipelago world. Paths below are relative
to the repository root. The detailed specification is [world format](../plans/04-world-format.md);
licences and exact upstream revisions are in [NOTICE](../NOTICE).

## Data map

| Path | Contract |
|---|---|
| `src/clawshot/data/world/world.toml` | Start region, goal, file list, overrides, local settings/items and progressive tiers. |
| `src/clawshot/data/world/port.toml` | Translation inputs, Banc area mapping and pinned OoT Randomizer commit. |
| `src/clawshot/data/world/*.toml` region files named by `port.toml` | Translated regions, exits, events and location metadata. Do not hand-edit these generated files. |
| `src/clawshot/data/world/helpers.toml` | Named and parameterized rule helpers, translated from OoT Randomizer. |
| `src/clawshot/data/world/items.toml` | Item types/classes, aliases and properties used by search. |
| `src/clawshot/data/world/settings.toml` | Translated settings, tricks and world flags used by rules. Not the generator's user-facing defaults. |
| `src/clawshot/data/world/remake.toml`, `src/clawshot/data/world/remake/*.toml` | Sourced remake corrections, exclusions, new regions/checks, items and helpers. |
| `src/clawshot/data/settings.toml` | Generator defaults and placement restrictions; distinct from translated logic defaults. |
| `src/clawshot/data/locations.toml` | Placement identity definitions and links to world location names. |
| `src/clawshot/data/location_names.toml` | Player-facing labels, directions, physical IDs and map-floor descriptions. Presentation is not a new identity or access rule. |
| `src/clawshot/patch/gift_rules.toml` | Event grant identities and patch policies for supported gifts. |

Sources: `plans/04-world-format.md` sections Files, Overrides, Items/helpers/settings and Replayable
generator settings; `plans/03-game-data.md` sections Readable location names and Event gifts;
`NOTICE` for the provenance of translated data and algorithms. The world translation tool is
`src/clawshot/world/translate.py`; its inputs must match `port.toml`'s pinned commit, and the
translation comparison is in `tests/test_world_translate.py`.

### Overrides and evidence

`src/clawshot/world/load.py` applies `remake.toml` first, then `remake/*.toml` in sorted name order.
A location, exit, event, region, key count or item cannot be set in two override files. New regions
are added before their contents are resolved. A changed rule states `was` as well as `rule`; upstream
changes must not silently invalidate the correction. Overrides carry a `source` explaining the
ported file/line or remake evidence. See `plans/04-world-format.md`, Overrides.

The same specification defines `n64_only` (not a remake check), `keep_vanilla` (present but not
shuffled), `vanilla_fixed` (a concrete tier), and `new = true` (a remake addition). Preserve those
meanings in a port. Do not turn a held check into a randomized check just because it has a rule.
The current acceptance boundary is in [settings](settings.md), with observations in
`plans/playtest/answers.md` and completed results in `plans/00-roadmap.md`.

## Rule language

Rules are parsed expressions, **not Python to execute**. The compiler validates and folds settings
once; the remaining predicate reads items, events, age and time. Implementation:
`src/clawshot/world/rules.py`; syntax/lookup/unsupported branches:
`plans/04-world-format.md`, The rule language.

| Form | Meaning |
|---|---|
| `True`, `False`, `and`, `or`, `not`, parentheses | Boolean requirements. |
| `Kokiri_Sword`, `'Kokiri Sword'` | Item identifier; quoted names can also name events. Identifier normalization follows the compiler, not a new port-specific naming scheme. |
| `(Progressive_Hookshot, 2)` | Required count. Counts can also refer to a setting. |
| `is_child`, `can_use(Bow)`, `can_play(Song_of_Time)` | Helpers resolved from helper data and remake overrides, not hard-coded N64 assumptions. |
| `open_forest == 'open'`, `'Deku Tree' in dungeon_shortcuts` | Setting comparisons/membership; tables use their declared data shape. |
| `age == 'child'`, `at_day`, `at_night` | Age/time predicates; time semantics depend on settings. |
| `here(rule)`, `at('Region', rule)` | Region-scoped subrules represented as persistent events; not arbitrary teleports. |
| `has_bottle`, `has_stones(n)`, `has_medallions(n)` | Built-in inventory predicates. The specification lists all supported built-ins. |

Names resolve through built-ins, helpers, items, settings and events as specified by the compiler;
unknown names, helper recursion and unsupported live features fail rather than becoming true.
An inactive constant-folded branch can contain an unsupported name; do not eagerly evaluate it in a
port. N64 tricks default false and cannot be enabled without remake verification.
Sources: `src/clawshot/world/rules.py`, `src/clawshot/world/load.py`, and the rule-language and
Items/helpers/settings sections of `plans/04-world-format.md`.

Items have types and classes (progression, priority, normal), aliases and optional properties such
as bottle/stone/medallion. Dungeon items belong to their declared dungeon. Fixed tiers count toward
the progressive names read by imported rules, but ordinary seeds grant fixed items, not runtime
progressive upgrades. Starting items and event grants also participate in search; the remake has no
free starting Fire Temple key. Sources: `plans/04-world-format.md`, Fixed or progressive items,
Items/helpers/settings and Reachability; `src/clawshot/world/load.py`.

## Identity: model names are not physical IDs

A placement is identified by **source file and actor `Hash`**, never its array index, position or
translated N64 actor number. Child/adult/Alternative copies of one check must receive the same patch.
Event gifts use **flow and grant node**. Keep the world key, physical identity and player label distinct.
Sources: `AGENTS.md` rules 4–6; `plans/01-architecture.md`; `plans/03-game-data.md`, How collected
checks are recorded; `src/clawshot/data/locations.toml`; `src/clawshot/patch/gift_rules.toml`.

`oot_randomizer_name` links a known corresponding check; an empty link is not permission to infer
one by list order or distance. Remake-only checks use sourced additions. Floor labels come from map
metadata and describe directions, not identity. Pots and other age-dependent actors can have distinct
Hashes at matching positions. Sources: `plans/04-world-format.md`, Overrides;
`plans/03-game-data.md`, Readable location names, Pause-map floors and Pots/crates/ground rupees.

For a tracker, preserve world keys for placements/rules and use `location_names.toml` for display.
Do not allocate Archipelago network IDs from mutable array order; an eventual port needs an explicit
stable mapping from these identities. That network-ID mapping is a port requirement, not an existing
Clawshot feature (architecture: `plans/01-architecture.md`; current scope: `plans/00-roadmap.md`).

## Search and seed acceptance

The search repeatedly collects every reachable reward, updates events/inventory and explores exits
until nothing changes. Child/adult reachability is separate, with time tracked when enabled. The
configured goal must hold before a generated seed can be written. Sources:
`src/clawshot/world/search.py`, `src/clawshot/generate/__init__.py`,
`plans/01-architecture.md`, The beatability search, and `plans/04-world-format.md`, Reachability.

Before adult return unlocks, child reachability uses an independent pre-pull inventory/event view;
it cannot borrow later adult finds. Native return follows Forest **quest completion**, not owning
a shuffled medallion. The default first-pull guarantee separately proves adult return from mandatory
pull prerequisites and adult checks, without assuming optional child errands. Free travel changes
both logic and native patches; do not copy the search assumption without that patch contract.
Sources: `plans/04-world-format.md`, Ages; `src/clawshot/world/search.py`;
`src/clawshot/data/world/remake/sheik.toml`; `plans/playtest/answers.md`, R9-FREE-TRAVEL and
R10-FIRST-PULL-FIXED. Non-default Door of Time modes remain untested in game; see [settings](settings.md).

The fill uses seeded assumed fill, placement restrictions and safe swaps, then an independent
collection search on the completed placement. Item pool preparation uses actual remake identities,
not the untranslated N64 vanilla pool. Shops, floor pickups and gifts have destination restrictions;
held/excluded checks remain fixed sources for logic where applicable. Sources:
`src/clawshot/generate/fill.py`, `src/clawshot/generate/__init__.py`,
`plans/04-world-format.md`, Generating a seed and Replayable generator settings; attribution: `NOTICE`.

Determinism requires the same source/world data, seed and effective settings. Tests include changed
Python hash seeds; unordered placement iteration and timestamps are forbidden. A passing search is
proof of **this model**, not of unplayed remake routes. The earlier Slingshot-room softlock exposed an
N64/remake mismatch; player answers remain essential. Sources: `AGENTS.md` rule 4;
`plans/04-world-format.md`, Generating a seed; `plans/00-roadmap.md`, recorded mini-seed result;
`plans/playtest/answers.md`, DT01/DT02.

## Spoiler contract

The JSON is local generated output: **do not upload or distribute it**. The producer is
`src/clawshot/generate/__init__.py` (`spoiler`, `spoiler_json`); metadata specification:
`plans/04-world-format.md`, Generating a seed; physical descriptions:
`src/clawshot/data/location_names.toml`. Consumers should handle nullable/optional descriptive data.

| Top-level field | Meaning |
|---|---|
| `generator` | Generator name and package version; not an exact source revision by itself. |
| `seed` | Seed number. |
| `settings` | Effective settings mapping. |
| `settings_string` | Replayable CS1 representation, requiring the same source/world data. |
| `placements` | World-location key → item for shuffled checks only, not a complete list of fixed rewards. |
| `locations` | Descriptions keyed by those world keys, with catalogue fields and applicable shop/scrub metadata. Custom worlds can lack physical IDs. |
| `opening_route` | An opening witness (`name`, `event`, `region`, `steps`), or null. Steps carry kind, location, requirements and alternatives. Not the entire game's route. |
| `age_locked_pickups` | Wrong-age first-frontier warnings, including ties. Not proof that later optional pickup timing is safe. |
| `spheres` | World-keyed progression pickups grouped by search collection sphere; empty progression spheres omitted. Not every collected filler item. |
| `hints` | Stone, where, message label, kind, rendered text, area, location and item; some target fields can be null. |

Age-warning source: `src/clawshot/generate/itembar.py`, `plans/03-game-data.md`, Item-bar assignment;
its observed child Bow failure/recovery: `plans/playtest/answers.md`, R8-SEED8-BOWLOCK/R9-LICHII.
Do not reconstruct the complete search using only the progression-filtered `spheres`: include fixed
rewards and the actual world/settings instead (`plans/04-world-format.md`, Reachability).

## What a multiworld port still needs

Clawshot currently generates a static RomFS mod, not a live multiworld client. Archipelago remains
future scope (`plans/00-roadmap.md`; decision D8 in `plans/decisions.md`). Reusing the logic does not
automatically provide a playable multiworld integration.

An integration would still need a stable network item/location mapping, check-completion reporting,
connection/session handling, and **items delivered during play**, including durable receipt/reconnect
semantics. A static RomFS mod cannot receive arbitrary items from a network by itself: delivery needs
a hook/API in the runtime plus a client. Runtime code hooks are explicitly a separate future layer in
`plans/01-architecture.md`; these requirements are not shipped interfaces. Keep data licensing
attribution from `NOTICE`, and verify remake routes/grants rather than assuming another runtime or
N64 behavior supplies them. A read-only tracker likewise needs its own observation/import mechanism;
the spoiler is an offline description, not a live state feed.
