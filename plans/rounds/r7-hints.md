# Round 7, track A: hints (cs7a)

Branch `r7/hints`, from main `e498402`. Owns `src/clawshot/generate/hints.py`, the hint step in
`src/clawshot/patch/text.py`, `tests/test_hints*.py`, this file and section 25 of `plans/03-game-data.md`. Scratch
scripts and decoded data: `E:/OOTRemake/work/r7-hints/` (outside the repo).

| Item | Where | Commit |
|---|---|---|
| 1 Gossip Stones in the world (shared world files) | `world/translate.py`, translated region files, `world/model.py`, `world/load.py`, `04-world-format.md` | abbce51 |
| 1 the 40 stones, one label each | `data/world/remake/hint_stones.toml`, `census/hints.py` (`REMAKE_STONES`, `stone_labels`), `tests/test_hints_world.py` | 7fe1e63 |
| 2 hint selection | `data/hints.toml`, `generate/hints.py`, `tests/test_hints_select.py` | (item 2 commit) |

## Item 1: Gossip Stones as hint locations

OoT Randomizer lists its 40 Gossip Stones as locations of type `HintStone` (`LocationList.py:2562-2602` at
`526b4c8d`) with a region and a rule in `data/World/*.json` (e.g. `"DMC Gossip Stone": "has_explosives"`,
`Overworld.json:2344`; `"Dodongos Cavern Gossip Stone": "here(can_blast_or_smash or Progressive_Strength_Upgrade)"`,
`Dodongos Cavern.json:19`). The translator dropped them; now it writes them like any location (type `HintStone`, no
vanilla item), and the loader builds every `HintStone` into `World.hint_stones` instead of `World.locations`: a stone
is a place to read a hint, not a check, so the fill, the beatability search, the spoiler's locations and every test
that walks `World.locations` see the same 1405 locations as before. `Search.can_access(stone)` answers whether a stone
can be reached, for either age, like any location. Rules compile in the world's compiler, so a stone's `here()` (the
Dodongo's Cavern stone) becomes its subrule event as in OoT Randomizer.

The remake's differences are `data/world/remake/hint_stones.toml`:

- OoT Randomizer's four stones with no stone in the remake get `n64_only` (KF Storms Grotto, LW Near Shortcuts Grotto,
  HF Near Market Grotto, DMT Storms Grotto: round 6's `OOTR_STONES_MISSING`).
- The four remake-only stones get regions and rules by hand, with sources: `SFM Song of Time Clearing Gossip Stone`
  (the rule of the Business Scrub Seed chest in the same clearing), `Kak Bomb Grotto Gossip Stone` (Kakariko's bomb
  grotto, `can_blast_or_smash` as round 4 opened the remake's bomb grottos), `ZR Storms Grotto Gossip Stone` and `DMT
  Cow Grotto Gossip Stone` (their grotto regions, `True`).
- Every other stone keeps OoT Randomizer's region and rule. Not checked against the remake: whether the HF cow grotto
  stone needs a fire source (`has_fire_source`, N64's webs) and whether the adult Zora's Domain copy (its `Presence`
  `IsAppear_GossipStone_ZoraDomain_Adult`) matters: the child copy reads the same label, and OoT Randomizer's rule
  is `True`.

`census.hints.stone_labels()` gives each live world stone the message label it speaks (40 stones, 40 labels):
`STONE_LINKS` for the 36 linked stones, `REMAKE_STONES` for the four remake-only ones; the Kokiri Forest files'
copy of the Lost Woods bridge stone adds no stone.

Checks:

| Command | Result |
|---|---|
| `uv run pytest tests/test_hints_world.py tests/test_world_data.py tests/test_world_census.py tests/test_hints.py -q` | 26 passed (235 s; the world data tests are the slow part): a `HintStone` is in `hint_stones`, not `locations` or its region's checks, reachable only once its region is; one naming an item is refused; a new stone override needs no vanilla item while a new check still does; the world's live stones are exactly `stone_labels()`, 40 stones and 40 labels, every census label used, the four `n64_only` stones as listed |
| `OOTR_DIR=E:/OOTRemake/work/r2-world/OoT-Randomizer uv run pytest tests/test_world_translate.py -q` | 1 passed: the committed files are what the translator writes |
| `uv run python E:/OOTRemake/work/r7-hints/check_stones.py` | 44 stones (40 + 4 remake-only), 40 live = 40 labels, 1405 locations; with no items only the KF and LW stones are reachable |

## Item 2: hint selection (`clawshot.generate.hints`)

`hints.choose(seed, mode, distribution)` gives one `Hint` per live stone (stone, label, kind, area, location, item,
junk line), in world order; `hints.text(hint, item_name, location_name)` words it. The kinds, the weights, the
always/sometimes lists, the area names, each stone's place and the wording are data (`data/hints.toml`), each list
and weight with its OoT Randomizer source (`Hints.py`, `HintList.py`, `data/Hints/*.json` at `526b4c8d`, MIT). What
each kind is and how a hint finds its stone is in the module docstring and section 25. The wording is Clawshot's
own ("They say {area} hides the {item}.", "They say searching {area} would only waste the hero's time.", eight junk
lines); no OoT Randomizer or game text is copied.

Choices made here (provisional, for review):

- Distributions `balanced` (default), `strong`, `useless`, ported from OoT Randomizer's files of those names. Its
  `song`, `overworld` and `dungeon` kinds draw from the `sometimes` list, so here they are one `sometimes` kind with
  their summed weight; entrance and goal/dual hints are left out (no entrance shuffle, no goals yet); `copies` is
  always 1 (40 stones, 40 hints).
- Barren is stricter than OoT Randomizer's: any major item in an area keeps it off the barren list, even a surplus
  copy (OoT Randomizer counts copies beyond what the goal needs as useless). A barren hint is never wrong this way;
  it is offered for fewer areas.
- Location hints (`random`, `sometimes`, `item`) leave out a dungeon's own keys, maps and compasses with
  `dungeon_items = own_dungeon`: they are where the player expects them.
- Junk goes to stones nobody can read first (with `mask`, e.g. the adult-only Sacred Forest Meadow clearing stone).
- The hint `random.Random` is seeded from the seed number (`"clawshot hints <n>"`), separate from the fill's, so
  hints never change placements and hints can be chosen for an existing seed's placements (item 4's 7c).

Checks:

| Command | Result |
|---|---|
| `uv run pytest tests/test_hints_select.py -q` | 8 passed: a region's area from where it is entered (a `False` exit not followed); the required locations are the two the goal needs; over 30 seeds and two distributions, one hint per stone and a hint naming the Hookshot's chest never on the stone behind the Hookshot, barren only for the area without a required item, Way of the Hero only for the two areas with one (a coverage print showed every kind on every stone that may hold it); same seed same hints; with `mask` and no Mask of Truth only junk, with the mask in a chest that chest is never named; `useless` only junk; unknown mode or distribution refused; the wording fills in names |
| `uv run python E:/OOTRemake/work/r7-hints/try_hints.py` (seed 7, chests, the real world, no dump) | 11 required locations (1.1 s); 40 hints per mode (about 1.1 s each): `always` 12 item, 10 random, 7 sometimes, 5 Way of the Hero, 3 barren, 3 junk; `mask` 4 Way of the Hero, 4 barren, 5 junk (the Song of Time clearing stone is adult-only, so unreadable with the mask) |

## Cross-track posts (thread `cs-r7`)

- abbce51 changes shared world files (translator, regenerated region files, `model.py`, `load.py`). The post failed:
  `bermuda thread post --thread cs-r7 ...` printed `bermuda: no thread cs-r7: create it with bermuda thread new
  cs-r7` (exit 1); I may not create threads. **Claude: the thread `cs-r7` does not exist; the posts below wait for it.**
