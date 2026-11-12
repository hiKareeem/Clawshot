# Archipelago slots (`clawshot.ap`)

This is the developer reference for the one entry point an [Archipelago](https://archipelago.gg) world uses:
writing a seed from placements chosen by a multiworld's fill instead of Clawshot's. Solo seeds do not use any of it.
The world that calls it is `ounce-ocarina-ap` (Archipelago game `Ocarina of Time (2026)`), maintained outside this
repository. It runs Clawshot's own logic, so a slot's mod is what Clawshot would build with those placements.

## What runs, and where

```sh
python -m clawshot.ap --romfs <dump> --slot <slot.json> --out <dir>
```

The Archipelago client runs this from the player's Clawshot checkout (`cwd` = checkout, `PYTHONPATH=src`, the
checkout's `.venv` Python when it has one). Exit status 0 prints `wrote <n> files to <dir>`; 1 prints
`ERROR: <reason>` on stderr, which the client shows to the player. `--romfs` takes anything `local_romfs` takes.
The output is the usual LayeredFS mod folder (`romfs/`); the client adds the in-game bridge's `exefs/` beside it.

`<slot.json>` (`FORMAT = 2`):

```json
{"format": 2, "seed": 123, "settings": {"<Settings field>": "..."}, "placements": {"<location>": "<item>"},
 "foreign": {"<location>": {"player": "<player name>", "item": "<item name>"}}}
```

`settings` are `Settings(**fields)`; `placements` name every shuffled location, by world location name, with an
item from the world's item table. A location holding another player's item names `FOREIGN_ITEM`
(`Archipelago Item`) and has an entry in `foreign`. Its chest shows Zelda's Letter and "You found <player>'s
<item>!" in each of the game's 16 languages, and gives nothing; `Nothing` is a get window saying "You found Nothing."
and no item; in a format-2 slot the player's own items say "You found your <item>!" (`patch.custom_items`,
`patch.get_text`). Both go to chests only. Format 1 (no `foreign`, other players' items as `Rupee (1)`) is still
read.
`generate.from_placements` refuses a slot whose placements break `fill.allowed`, then fills the rest vanilla; there
is no beatability search (the multiworld proved the seed) and the spoiler's `opening_route` is null.

## The interface the world depends on

The world copies part of Clawshot into its `.apworld` and bakes the rest into data with its sync tool
(`tools/build_data.py`, run with Clawshot's interpreter against a checkout). Changing any of the following
breaks the world or its players' existing seeds, so it needs the world's maintainer told (an issue or a mention
in the PR is enough):

| Clawshot | Used by the world for | Safe to change? |
|---|---|---|
| `ap.FORMAT` and the slot fields above | the patch file the world writes | Bump `FORMAT` on any incompatible change; the world then resyncs |
| `ap.RECEIVED_FLAG`, `ap.RECEIVED_BITS` | the save's received-item counter; the **in-game bridge hard-codes** the name pattern and 16 bits | No, not without a coordinated bridge release; old saves lose their count |
| `ap.FOREIGN_ITEM` (`Archipelago Item`), `ap.NOTHING_ITEM` (`Nothing`) | what another player's item shows; the world's filler; the world's placement rules require each location to be able to hold `FOREIGN_ITEM` | Renaming breaks the world's item ids (`Nothing` has one); resync |
| `IsTreasureBoxOpen.<census id>` chest flags | how the bridge detects a check | Only if the game data says otherwise |
| Location and item names (`world/*.toml`, `oot_randomizer_name`) | the keys of Archipelago's ids, which are append-only | A rename gives the thing a new id; tell the world so it can carry the old one |
| `Settings` fields and values the world sets: `shuffle`, `dungeon_items`, `forest`, `door_of_time`, `fast_start`, `cheap_deku_shield`, `logic.free_time_travel` | the player's options | Adding values is fine; renaming or removing breaks generation |
| `fill.allowed`, `shuffled_locations`, `world.search.Search` | the world's item rules, pool and reachability | Yes: they are vendored, so the world follows on its next sync |

### Vendored files

The sync copies these verbatim into the world (`src/vendor/clawshot/`), apart from mechanical edits:
`settings.py`, `world/{__init__,model,rules,search,load,shops}.py`, `generate/fill.py` and
`generate/prepare.py`. They must keep importing nothing else from `clawshot`; a new import there stops the sync with
an error naming it. Two lines are rewritten by exact text, and the sync stops if either changes:

- `settings.py`: the three lines that open `data/settings.toml` (the world reads a baked catalog, as an `.apworld`
  is a zip).
- `generate/fill.py`: `from clawshot.generate import hints as hint_choices` (replaced by the two values it
  validates against, `hints.MODES` and `hints.distributions()`).

This is why `world_spec` and `prepare` live in `generate/prepare.py`: settings-to-world must be the same code in
both placers, and that module imports only the fill's `Settings`, the world loader and the shop helpers.

### Data the sync reads

`world.load.load_spec()`, `generate.prepare(spec, Settings())`, `settings.CATALOG`,
`patch.items.load()` (`.actors`, `.actor(name)`, `.item(actor, dungeon, items)`),
`census.definitions.load()` (`name`, `oot_randomizer_name`, `kind`, `id`, `vanilla_item`), and on the world model
`locations[].{type, region, n64_only, vanilla}`, `regions[].dungeon`, `items[].{type, dungeon}`. With `--romfs` it
also checks every chest flag is a saved Bool in both builds' GameDataLists (`formats.byml`, `formats.zsdic`,
`pack.source.dump_layers`, `save.murmur3_32`).

## Versions

A slot records the Clawshot commit its world was synced from. The player's checkout must place exactly what
generation assumed, so a release of the world names the Clawshot commit (or version) it needs. A Clawshot change
that alters seed output for given placements needs a world resync and release, just as it needs a version bump
for solo seeds. Determinism holds as for solo seeds: same slot file and Clawshot version, same mod folder.

## Limits today

- Only `Chest` is shuffled by the world: the other kinds need their collected flags mapped for the bridge.
- `dungeon_items` is always `own_dungeon`. Dungeon items grant through one generic actor per kind
  (`Item_Dungeon_SmallKey`, ...) that counts for the dungeon Link stands in, so a key received from the server
  cannot reach its dungeon.
- No Gossip Stone hints are chosen for a slot (`make_seed` with `placements`).
