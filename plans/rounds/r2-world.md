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
| 5 Port of Kokiri Forest, Lost Woods, Deku Tree, credited in `NOTICE`; link to the census | `src/clawshot/data/world/*.toml`, `tests/test_world_data.py`, `test_world_translate.py`, `test_world_census.py` | done; 3 locations pending track A's answer (below) |
| Fixed items (D16) | `world.toml` `[settings] progressive_items = false`, `[progressive]`; `vanilla_fixed` | done |

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
| `uv run ruff format --check` | 48 files already formatted |
| `uv run ruff check` | All checks passed |
| `uv run pytest` | 116 passed, 7 skipped (the dump tests, and the translator test without `OOTR_DIR`) |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | see the last commit's handoff (formats and census; this track touches neither) |
| `OOTR_DIR=E:/OOTRemake/work/r2-world/OoT-Randomizer uv run pytest tests/test_world_translate.py` | 1 passed: rerunning the translator over the committed files changes no byte |
| `uv run pytest -rP tests/test_world_census.py` | 4 passed; prints the 3 pending locations |
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
  Babas; 100 seeds beatable with fixed items and 100 with progressive items; two interpreters with
  `PYTHONHASHSEED` 1 and 2 write the same spoiler bytes; by default Saria gives the Fairy Ocarina and the target
  game a bigger bullet bag (`vanilla_fixed`).
- Fixed items (`test_world_rules.py`): a chest whose OoT Randomizer vanilla item is the progressive hookshot gives
  its `vanilla_fixed` tier; a Longshot found first opens both the Hookshot post and the Longshot ledge, a Hookshot
  only the post, two progressive hookshots both; a progressive vanilla item without its tier, or with a wrong one,
  stops the build.

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
  collected by the search. Default shuffle is OoT Randomizer type `Chest` only (D15). N64-only locations are
  neither shuffled nor placed.
- **Fixed items (D16)** through tiers: each tier of a progressive item (`[progressive]` in `world.toml`: Hookshot,
  Strength, Scale, Wallet, Ocarina) is an item counting as that many of the progressive item, so OoT Randomizer's
  rules are unchanged and read both modes. Clawshot's own settings and items live in `world.toml` so the generated
  files stay byte-identical to a translation; the hand fields `vanilla_fixed` and `n64_only` live on the location
  and the translator keeps them. Tier names (`Goron Bracelet`, `Adult Wallet`, ...) are mine; that a higher tier
  found first gives its ability in the remake is an inference, not checked in game.
- **Census area per region** comes from `port.toml` (one Banc folder per file; grottos belong to the overworld
  folder they open from).
- **The search is rebuilt from scratch for each item the fill places** (OoT Randomizer copies caches). Ported world:
  about 25 ms a seed with chests shuffled. Worth revisiting once the whole game is ported.
- **Spoiler spheres list progression items only**, every placement is under `placements`; OoT Randomizer's
  playthrough also drops items not needed for the goal, which is not done here.
- **Goal for round 2**: `'Defeat Queen Gohma'`, in `world.toml`, until Ganon is ported.
- Dropped from OoT Randomizer region data for now: `savewarp`, `is_boss_room`, `alt_hint`; shop price and wallet
  rules; `logic_no_night_tokens_without_suns_song`. Listed in `04-world-format.md`.

## Findings for the next rounds

- **Upgrades without tiers.** Quivers, bomb bags and bullet bags: OoT Randomizer's rules only ask whether the base
  item is held. With fixed items each such check needs `vanilla_fixed` when it is ported (done for
  `LW Target in Woods`). The vanilla items of non-shuffled checks should come from the census (actor names) once
  the item mapping (logic item to remake actor) exists.
- The translator test reruns the translator over the committed files. Hand edits to *rules* would need an override
  layer; round 3 decides when the first one comes.

## Item 5's last test (`tests/test_world_census.py`)

Reviewer's answers, applied: N64-only checks are an `n64_only = "<reason>"` field on the location, set only with
evidence; Gold Skulltulas match by count per area; uncovered types are skipped by type.

- **Covered types, checked one by one:** `Chest` (census `chest`, `treasure_game_box`), `BossHeart`
  (`heart_container`), `Scrub` and `GrottoScrub` (`scrub`), `Shop` (`shop_slot`), and `Freestanding` whose vanilla
  item is a Piece of Heart or a small key (`freestanding`). Each must be linked from a census definition of that
  kind in the region's area, or be `n64_only`, or be on the pending list. Every census `oot_randomizer_name` in the
  ported areas must name a ported location. Result: all linked except the three pending ones; no `n64_only` needed.
- **Pending** (printed by the test, each must leave the list as a link or an `n64_only` with evidence; the test
  fails if one becomes linked while still listed): `KF Storms Grotto Chest`, `LW Deku Scrub Near Deku Theater
  Left`, `LW Deku Scrub Near Deku Theater Right`. The reviewer asked track A whether they exist in the remake.
- **Gold Skulltulas by count:** OoT Randomizer GS Token locations per area against census `gold_skulltula`:
  KokiriForest 3 = 3, LostWood 3 = 3, InsideTheDekuTree 4 = 4.
- **Skipped by type** (the census has no placement for them): `Freestanding` rupees and recovery hearts (29 in the
  port), `Wonderitem` (12), `RupeeTower` (7), `Pot` (5), `Beehive` (5); and gifts from event flows, round 3:
  `NPC` (8), `Cutscene` (2), `Boss` (1, the Kokiri Emerald), `Song` (none in the port). A type not in any of these
  lists fails the test, so a new port has to classify it.

## Decisions taken since the first handoff

- D15 (Kareem): first seeds shuffle chests only; `Settings.shuffle` defaults to `("Chest",)`.
- D16 (Kareem): fixed items now; `progressive_items` defaults to `false`, progressive stays as a setting.

No open questions.
