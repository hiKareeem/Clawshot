# Round 2, track B: world engine (cs2b)

Branch `r2/world`. OoT Randomizer: `https://github.com/OoTRandomizer/OoT-Randomizer`, branch `Dev`, commit
`526b4c8d81b7c4023ef4573ffbaf39344e270d5b` (the same commit round 1 used), cloned to
`E:/OOTRemake/work/r2-world/OoT-Randomizer`. MIT except `bin/Compress`, `bin/Decompress`, `bin/gzinject` and
`Notes/Chest Textures/rgba5551topng`, which carry their own GPL licence files; nothing from those was read or used.

## What is on the branch

| Item | Where | State |
|---|---|---|
| 1 Format, loader, translation tool | `plans/04-world-format.md`, `src/clawshot/world/{rules,model,load,translate}.py`, `src/clawshot/data/world/` | done |
| 2 Reachability (ages, Temple of Time as an event, time of day) | `src/clawshot/world/search.py` | done |
| 3 Assumed fill, beatability search on every seed, JSON spoiler, determinism | `src/clawshot/generate/` (`python -m clawshot.generate`) | done |
| 4 Synthetic tests | `tests/test_world_rules.py`, `test_world_search.py`, `test_generate.py` | done |
| 5 Port of Kokiri Forest, Lost Woods, Deku Tree, credited in `NOTICE` | `src/clawshot/data/world/*.toml`, `tests/test_world_data.py`, `test_world_translate.py` | done, except the last test (waits for track A on `main`) |

**Rule language.** OoT Randomizer's syntax and meaning, so its region JSON is copied rule for rule: items and
counts, `age`, `at_day`/`at_night`, quoted and capitalised events, helpers with parameters (`can_use(item)`, by text
substitution as OoT Randomizer does), settings as constants folded at build time, `here()`/`at()` as region events,
and the `State` built-ins the ported rules reach. Rules are parsed with `ast`, never executed; unknown names, helper
cycles and unsupported built-ins in a live branch are errors that name the region and location.

**Translator.** `python -m clawshot.world.translate --ootr <checkout>` reads `port.toml` (which OoT Randomizer
regions go into which file, and the commit, which it checks) and writes the region files, `helpers.toml` (all 156
helpers), `items.toml` (all 286 items) and `settings.toml` (the 42 settings, 42 tricks and 5 world flags the rules
name, at OoT Randomizer's defaults). Each requirement keeps its OoT Randomizer file and line as a comment, plus
OoT Randomizer's comments above it.

**Ported world.** 31 regions, 106 locations, 35 events (14 of them `here()` subrules). Location types: Freestanding
29, Chest 13, Wonderitem 12, GS Token 10, NPC 8, Shop 8, RupeeTower 7, Pot 5, Beehive 5, Scrub 3, Cutscene 2,
GrottoScrub 2, BossHeart 1, Boss 1. 8 hint locations left out. `world.toml` goal: `'Defeat Queen Gohma'`.
What the partial port cannot reach is reported, not hidden: 16 exits lead to regions not ported yet (Hyrule Field,
Zora River, SFM, the warp songs, the Temple of Time, ...), and three events no ported region defines
(`Cojiro Access`, `Links Cow`, `Odd Potion Access`).

## How it was checked

| Command | Result |
|---|---|
| `uv run ruff format --check` | 38 files already formatted |
| `uv run ruff check` | All checks passed |
| `uv run pytest` | 87 passed, 6 skipped (the dump tests, and the translator test without `OOTR_DIR`) |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | 5 passed (formats; this track touches none) |
| `OOTR_DIR=E:/OOTRemake/work/r2-world/OoT-Randomizer uv run pytest tests/test_world_translate.py` | 1 passed: the committed files are byte-identical to a fresh translation |
| `uv run python -m clawshot.generate --seed 12345 --out <work dir>`, twice, then `cmp` | identical `spoiler.json` |
| `... --logic logic_deku_b1_skip=true` | exit 1, `trick logic_deku_b1_skip stays off until it is verified in the remake` |
| 100 seeds shuffling every location type of the ported world (throwaway script) | 100 of 100 filled and beatable, 3.9 s |

What the tests show:

- Synthetic worlds (`test_generate.py`): a child village, a Temple of Time that gives `Time Travel`, a dungeon with
  two small-key doors and a boss door, a boss that needs the Bow, and a roof reachable only by adult with the
  Hookshot. The vanilla placement's spheres are exactly as worked out by hand; 200 of 200 seeds are beatable, with
  the dungeon's keys, boss key and map always in the dungeon and never behind the door they open; with
  `dungeon_items = "anywhere"` keys do leave it; whatever lands on the adult-only roof is collected after the
  Hookshot's sphere; a goal needing an item no location holds and a Sword locked behind its own door both raise
  `FillError`; one seed gives the same spoiler bytes twice, and eight seeds give more than one spoiler.
- Reachability (`test_world_search.py`): adult starts only once `Time Travel` is held; an adult-only location is
  reachable as adult and not as child; `here()` lets an adult use what the child did; night spreads from a region
  where time passes; key doors count keys; dangling exits and undefined events are reported.
- Rules (`test_world_rules.py`): every construct of the table in `04-world-format.md`, settings folding, the
  short-circuit that lets a switched-off branch name an unsupported built-in, and each error.
- Ported world (`test_world_data.py`): the vanilla placement is beatable (Queen Gohma in the last sphere); the
  forest start matches OoT Randomizer's rules (Mido wants the Kokiri Sword and a Deku Shield; `open_forest =
  "open"` lets the child through and out of the forest); Gohma needs the Slingshot, with sticks from the Deku
  Babas; 100 seeds beatable; two interpreters with `PYTHONHASHSEED` 1 and 2 write the same spoiler bytes.

## Provisional choices (for review)

- **Data format TOML**, one file per area plus `helpers`, `items`, `settings`, `world`, `port`. Requirements are
  strings; a requirement verified in the remake becomes `{ rule = ..., source = ... }`.
- **Settings are OoT Randomizer's names and defaults**, kept in `settings.toml` rather than folded away by the
  translator, so rules stay verbatim and a later settings round can switch them. Tricks and glitches are a separate
  table that cannot be turned on (rule 6).
- **Time of day as OoT Randomizer without entrance shuffle**: `ensure_tod_access = false`, so `at_day`/`at_night`
  are always true. The engine does track day and night per region (tested with the flag on) for when entrance
  shuffle or the remake's own data needs it.
- **Drops and fixed events become events** named after their item (`Deku Stick Drop`, `Fairy`, `Time Travel`);
  OoT Randomizer models them as locations with a fixed item, which is the same in the search.
- **Item pool = the vanilla items of the shuffled locations**; every other location keeps its vanilla item and is
  collected by the search. Default shuffle is OoT Randomizer type `Chest` only (M2).
- **The search is rebuilt from scratch for each item the fill places** (OoT Randomizer copies caches). Ported world:
  about 25 ms a seed with chests shuffled. Worth revisiting once the whole game is ported.
- **Spoiler spheres list progression items only**, every placement is under `placements`; OoT Randomizer's
  playthrough also drops items not needed for the goal, which is not done here.
- **Goal for round 2**: `'Defeat Queen Gohma'`, in `world.toml`, until Ganon is ported.
- Dropped from OoT Randomizer region data for now: `savewarp`, `is_boss_room`, `alt_hint`; shop price and wallet
  rules; `logic_no_night_tokens_without_suns_song`. Listed in `04-world-format.md`.

## Findings for the next rounds

- **Progressive items.** OoT Randomizer's vanilla items and rules are progressive (`Progressive Hookshot`,
  `Slingshot` as a bullet-bag upgrade at `LW Target in Woods`, `Ocarina`). With non-chest locations kept vanilla,
  the logic counts the Target in Woods prize as a second Slingshot. In the remake a chest gives one fixed actor
  until Hookshot has hooks (M4), so the item mapping (logic item to remake actor) has to say how these read; that
  is where the vanilla items of non-shuffled locations should come from the census instead of OoT Randomizer.
- The translator test compares committed files with a fresh translation. Once a file carries remake edits, it needs
  an override layer (or the file leaves the translator); round 3 decides when the first edit comes.

## Item 5's last test: waiting

Track A's `locations.toml` is on `r2/census` (dd08991, cs2a's post), not on `main` yet. Per the prompt, this test
comes last, after Claude says it is on `main`.

Two things the test as specified will meet, from cs2a's post:

- Gold Skulltulas are deliberately unlinked (the remake moved them, `03-game-data.md` section 9), and they are
  not N64-only. 10 GS tokens are in the ported regions. Unlinked non-GS, per cs2a: `KF Storms Grotto Chest` and
  the two scrubs near the Deku Theater (`LW Deku Scrub Near Deku Theater Left`/`Right`).
- `03-game-data.md` lists N64-only checks as prose, not as OoT Randomizer names a test can read.
- OoT Randomizer's location types include ones the census does not cover (Freestanding rupees and hearts, Pot,
  Beehive, Wonderitem, RupeeTower, NPC, Cutscene, song and event gifts). The census covers placements only.

My plan unless told otherwise: the test checks OoT Randomizer locations of the types the census covers (`Chest`,
`BossHeart`, `Scrub`, `GrottoScrub`, `Shop`, and `Freestanding` whose vanilla item is a Piece of Heart or a key),
treats `GS Token` as a known gap with its own assertion (all GS unlinked, by design), and needs an N64-only list
by OoT Randomizer name. **Kareem: should the N64-only list live in `03-game-data.md` (as a table of OoT Randomizer
names) or in the world data (a `n64_only` field on the location)?** I would put it in the world data, next to the
location, with the reason.

## Questions for Kareem

1. **The N64-only list (above): `03-game-data.md` or a field in the world data?**
2. **Should seeds shuffle only chests for now (M2), or also the other placement checks the census covers
   (freestanding heart pieces, boss heart containers, scrubs, shop slots)?** The engine handles any set of OoT
   Randomizer location types (`Settings.shuffle`); the patch plan decides what can be written.
3. **Progressive items without code hooks (findings, above): fixed items per chest (finding the Longshot first
   gives the Longshot), or keep OoT Randomizer's progressive pool and wait for M4?** This changes the item pool
   and several helpers (`Hookshot`, `Longshot`, `Ocarina`).
