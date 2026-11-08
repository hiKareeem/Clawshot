# Round 7, track A: hints (cs7a)

Branch `r7/hints`, from main `e498402`. Owns `src/clawshot/generate/hints.py`, the hint step in
`src/clawshot/patch/text.py`, `tests/test_hints*.py`, this file and section 25 of `plans/03-game-data.md`. Scratch
scripts and decoded data: `E:/OOTRemake/work/r7-hints/` (outside the repo).

Rebased onto main `9b4735c` (round 7 B and C merged, D27/D28); commit ids below are after that rebase. Before it
(on `dfe923a`): 914d375, 0fb2d53, e7c03dc, 9f2dbd0, 512adb2, e96ff8e, af7cd2d, 86cb02d, a341990, f180296, 10272df,
b5fcda0, 56a263c, in commit order; before the first rebase (on `e498402`): abbce51, 7fe1e63, a567b05, 2cb1e98,
dded73e, 7fe2e97, 93dde8c, e4c9d43, a341990.

| Item | Where | Commit |
|---|---|---|
| 1 Gossip Stones in the world (shared world files) | `world/translate.py`, translated region files, `world/model.py`, `world/load.py`, `04-world-format.md` | 43a18ec |
| 1 the 40 stones, one label each | `data/world/remake/hint_stones.toml`, `census/hints.py` (`REMAKE_STONES`, `stone_labels`), `tests/test_hints_world.py` | 3f03bec |
| 2 hint selection | `data/hints.toml`, `generate/hints.py`, `tests/test_hints_select.py` | d099e91 |
| 3 hint settings (shared files) | `generate/fill.py` (`Settings`), `data/settings.toml`, `__main__.py`, `tests/test_hints_settings.py` | 78f0d15 |
| 4 the stones' lines | `patch/text.py` (hint step), `tests/test_hints_lines.py`, item hints once per item | eab8b5d |
| 4 seed step, spoiler, play note (shared files) | `generate/__init__.py` (`Seed.hints`, `spoiler`, `play_note`), `patch/__init__.py` (`hint_step`), `tests/test_hints_seed_dump.py` | d91b197 |
| 4 fix: shop refills are not major items | `generate/hints.py`, `tests/test_hints_select.py` | 4784433 |
| D26 mask rule (reviewer steer) | `generate/hints.py` (`mask_prerequisites`), tests, `settings.toml` comment | 7bef02d |
| 4 section 25, this file | `plans/03-game-data.md`, `plans/rounds/r7-hints.md` | 33b36ab, 70787c6, then the final commit |
| gate fix: the seed oracle allows the hint text files (shared test, r5's) | `tests/test_seed_dump.py` | 62b9e9f |
| 7c fix: a name ends with colour `ffff` | `patch/text.py` (`RESET`), `tests/test_hints_lines.py` | 57a7fe9 |
| 7c fix: random hints skip Drop, Event and Shop items | `generate/hints.py` (`RANDOM_SKIP_TYPES`), `tests/test_hints_select.py` | 4552332 |
| 7c result: the Temple of Time stones settled | `census/hints.py` (`STONE_LINKS` evidence), `data/hints.toml` (`[stones]`) | 35320e0 |

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

## Item 3: settings

`Settings.hints` (`always` or `mask`) and `Settings.hint_distribution` (`balanced`, `strong`, `useless`: the names of
`data/hints.toml`), defaults in `data/settings.toml` (`always`, `balanced`), carried by the settings string like
every field (`as_dict`, so a default seed's string stays `CS1` and old strings decode to the defaults), and CLI
`--hints` / `--hint-distribution`, which override a `--settings` string. Shared files, one commit.

**Decided (D26, Kareem via the reviewer):** `always` is the default. For `mask` he added that a stone can be read only
once the mask is held, so a hint must stay useful from then on. Modelled (item 4 fix commit): under `mask` a stone is
readable only in a search state holding the Mask of Truth (as child: the remake asks for it worn), and
`hints.mask_prerequisites` lists the shuffled locations whose item the mask cannot be reached without (the mask's own
location too); none of them is named by any hint, and Way of the Hero starts from the mask (prerequisites left out
of the required list). Barren needs no change: an area holding a prerequisite holds a required item, so it is never
called barren. No flow change is written with `mask`.

| Command | Result |
|---|---|
| `uv run pytest tests/test_hints_settings.py tests/test_settings.py tests/test_settings_songs.py tests/test_settings_forest.py -q` | 25 passed: default string still `CS1`; `mask`/`strong` round-trip through the string; an unknown mode or distribution refused; `--hints always` overrides a `--settings` string's `mask` and keeps its distribution |

## Item 4: the seed step, the spoiler, the play note and the test output

**In a seed.** `generate()` chooses the hints after the fill (`Seed.hints`, the hint generator separate from the
fill's, so placements are what they were). `make_seed` adds `hint_step`: the game's English names of the hinted
items (`patch.text.item_names`, `USen` `<key>_Name` without grammar tags; an item with no actor keeps its logic name),
each stone's line (`patch.text.stone_line`: the stone's own opening tags, rows of at most 60 characters, two rows a
page, a page break reopening size and colour, names in colour `0000` and back to the stone's colour), written into
every language archive of the dump, and with `hints = always` the `GossipStone` flow edit of round 6. `spoiler.json`
gains `hints` (stone, where it stands, label, kind, the line as the stone says it, area, location, item), and
`play-note.md` a "Gossip Stones" table. A world without stones (a slice) gets no hints and no text files.

Size: with the English lines, every Western and the Japanese archive shrinks; `CNzh` (+1,024 bytes), `KRko` (+512)
and `TWzh` (+992) outgrow their size-table entries, which the writer raises like any file (so a seed with hints
writes the size table). **Decided (D26, Kareem): English hint text in every language archive.**

Checks:

| Command | Result |
|---|---|
| `uv run pytest tests/test_hints_lines.py tests/test_hints_text.py -q` | 12 passed: a short hint keeps the stone's colour, size and voice and colours the two names, back to the stone's colour after each; 40 six-letter words at width 30 make rows of four words, a page break every second row reopening size and colour (not the voice), no word split, nothing lost; the archive transform changes only the hinted stone and no other file; a label the archive lacks is refused |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_hints_seed_dump.py -s -q` (after the rebase, within the full dump gate) | 4 passed: seed 7, Chest+Shop, `always` and `mask`: 40 hints on the 40 labels in world order; every hint naming a location names its placed item at a shuffled location, and a fresh search with that item withheld reaches the stone (with `mask`, as child holding the mask); with `mask` no hint names one of the five mask prerequisites (KF Kokiri Sword Chest, KF Midos Bottom Left and Top Left Chests, Deku Tree Slingshot Room Side Chest, Dodongos Cavern End of Bridge Chest); Way of the Hero, item and junk present (`mask`: 4 woth, 3 barren, 6 item, 10 sometimes, 13 random, 4 junk); all 16 archives change, the flow only with `always`; every archive's stone line reads, page breaks as spaces, exactly the spoiler's text |
| `uv run pytest tests/test_hints_select.py -q` | 10 passed, adding: a shop refill (`Buy Bombchu (8)`, a progression item in the world) gets no item hint and leaves its area barren (it failed before the fix, printed seed 2 naming the refill; found in 7c's first build, which hinted "Eight Bombchus" and "Five Deku Sticks"); with the mask behind the Hookshot, `mask_prerequisites` is the Hookshot's chest and the mask's own, neither is ever named under `mask` while the Hookshot's chest is under `always`, and the Bow found after the mask still is |
| `uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 7 --out E:/OOTRemake/work/r7-hints/smoke-7` | exit 0, 79 files (the 16 archives, the flow, the size table for the three growing archives); spoiler `hints` 40 lines, `play-note.md` has the Gossip Stones table |

### The test output `seed-shop-7c` (`E:/OOTRemake/work/r7-hints/`)

Built by `E:/OOTRemake/work/r7-hints/make_7c.py` (throwaway, outside the repo): 7b's 228 shuffled placements from its
`spoiler.json`, every other check at the remake's vanilla item (census links, as `make_seed` does), under the current
logic with 7b's settings (Chest+Shop, own-dungeon items, the intro skip, forest closed, no cheap Deku Shield, which 7b
predates). The beatability search passes (25 spheres; every 7b placement and item exists in the current world). The
hints are `choose(seed, "always", "balanced")`; the text goes through `patch.text` and the writer.

- `seed-shop-7c/romfs`: 7b's 77 files copied and checked byte-identical by SHA-256
  (`E:/OOTRemake/work/r7-hints/seed-shop-7c-files.json`), plus `Event/EventFlow/GossipStone.bfevfl.zs` (no mask) and
  13 language archives. **`CNzh`, `KRko` and `TWzh` are left out of 7c**: their English text outgrows the size-table
  entry, and raising it would change 7b's size table (a non-text file); Kareem's game is `en-US` (`oe: language
  en-US (language.txt)` in his 7b log). No entry changed for the written files.
- `seed-shop-7c/spoiler.json` (7b's `patch` plan kept, `based_on` 7b) and `play-note.md` with the Gossip Stones table.
- `Play shop seed 7c.bat`: copied from round 5's save-copy launcher (`Test - talon-boomerang.bat`) and 7b's: starts
  `E:\Games\Hookshot\bin\hookshot.exe` only, `HOOKSHOT_NO_UPDATE_CHECK=1`, stops if the exe is missing; on its first
  run it copies the save from `E:\OOTRemake\work\r5-seed\user-seed-shop-7b\save\5a3c9e1f0b7d24680000000000000001`
  (read only; stops if `slot_01\progress.sav` is missing) into its own `user-seed-shop-7c`, overlay
  `seed-shop-7c\romfs`, log `seed-shop-7c\hookshot_log.txt`. Not run by me (checked by reading it).
- `uv run python E:/OOTRemake/work/r7-hints/readback_7c.py` read the written `USen` archive and flow back from the
  output folder: the lines below with their tags, and no Mask of Truth question left in the flow.
- Rebuilt after the rebase onto `dfe923a` (the Jabu-Jabu rule): beatable, 25 spheres, the same 40 lines; 77 files
  byte-identical to 7b's, 14 added; the readback repeated.
- Cost: choosing hints takes about 1 s a seed (one search per shuffled progression item for Way of the Hero), so
  `tests/test_world_data.py::test_seeds_with_the_default_settings_are_beatable` (200 seeds) took 384 s in a full run
  while the game was running on this PC, and the CLI's seed 7 about 150 s with the 16 archives.

**What Kareem should do and see** (quit 7b first; 7c continues a copy of the 7b save, so nothing in 7b changes):

1. Run `E:\OOTRemake\work\r7-hints\Play shop seed 7c.bat` and continue the save. The game plays exactly as 7b (same
   chests and shelves).
2. In the Temple of Time courtyard (the Market's north exit) the four Gossip Stones stand in a row. Talk to each,
   **without the Mask of Truth**. Each speaks (the stone, not Navi): an opener, then one of these four lines, with the
   names in a highlight colour, then a closing line:
   - `GOSSIP_HYRULE_MARKET_01`: "They say Gerudo Training Ground Torch Slug Room Chest holds / the Red Rupee."
   - `GOSSIP_HYRULE_MARKET_02`: "They say Haunted Wasteland: Ruins Cellar Torch Chest holds / the Poe."
   - `GOSSIP_HYRULE_MARKET_03`: "They say searching the Shadow Temple would only waste the / hero's time."
   - `GOSSIP_HYRULE_MARKET_04`: "They say searching Zora's Domain would only waste the hero's / time."
   (`/` is where the row breaks.) **Report, left to right as you face the temple, which line each stone says**: that
   settles round 6's open question of which label is the far left.
3. Optional, on the way: Hyrule Castle's stone beside Malon and Talon (child) says "They say Goron City hides the
   Hylian Shield."; the Kokiri Forest stone by the Lost Woods entrance says "They say Kokiri Forest hides the Kokiri
   Sword." (both true in 7b: GC shop shelf 6, Mido's middle-left chest).
4. The log `E:\OOTRemake\work\r7-hints\seed-shop-7c\hookshot_log.txt` should show `fs: OpenFile(...GossipStone.bfevfl.zs):
   from the overlay` and the same for `Mals/USen.Product.110.sarc.zs`.
5. **Report:** do the stones speak without the mask, are the lines as written (wrapping, the highlight colour, no
   broken box or crash), and is anything hard to read? Every stone's line is in `seed-shop-7c\play-note.md`, "Gossip
   Stones", if you meet others.

### Kareem's 7c run, the two fixes and `seed-shop-7c-next`

**What he saw** (reviewer, from his screenshots): facing the temple, left to right, the stones say
`GOSSIP_HYRULE_MARKET_01` to `_04`, each without the mask; wrapping fine. That is how `STONE_LINKS` already had them
(Left, Left-Center, Right-Center, Right); 35320e0 records it as in-game evidence and drops "unsettled" from the four
`[stones]` descriptions. **Bug:** after the first name the rest of the line stayed highlighted.

**Colour.** Printed tags of the written `GOSSIP_HYRULE_MARKET_01`: `0100`, size `P`, voice, "They say ", `0000`,
name, `0100`, " holds\nthe ", `0000`, "Red Rupee", `0100`, ".". The game never ends a highlight that way. Every
colour tag (group 0 type 3) in every `USen` message that follows a `0000`: `ffff` 3046 times, `0000` twice, the
line's own colour never (`E:/OOTRemake/work/r7-hints/colour_probe3.py`). For example, `EventFlowMsg/GossipStone.msbt`'s
`Talk_13` stresses two words with `0000` and ends them with `ffff`. Lines that open in `0100` and stress a word end it
with `ffff` too. 57a7fe9 ends each name with `ffff` (`text.RESET`). `test_a_short_line_keeps_the_stone_style_and_colours_the_names`
now pins `Tag(0, 3, b"\xff\xff")` after each name; the old test pinned `0100`, the bug. Read back from
`seed-shop-7c-next`: "They say " `0000` "Gerudo Training Ground Like Like Hall Bomb Wall\nChest" `ffff` " holds the "
`0000` "Red Rupee" `ffff` ".".

**Junk items in hints** (reviewer: stone 01 named a Red Rupee, 02 a Poe). OoT Randomizer, `Hints.py` at `526b4c8d`
(`E:/OOTRemake/work/r7-hints/ootr/`):
- random, `get_random_location_hint` (1088-1097): any filled location except items of type `Drop`, `Event` or
  `Shop`, restricted dungeon items, locked locations, hint exclusions. No junk filter: a Red Rupee can be named.
- sometimes, `get_specific_hint` (1127-1172): a fixed list of locations; no filter on the item at all.
- item, `get_good_item_hint` (882-891): `majoritem` only, so never junk.

Clawshot matched item and sometimes already; its random kind lacked the type filter and named shop refills (`Buy
...`, type `Shop`, or type `Item` for the remake's own refill sizes). 4552332 adds it (`RANDOM_SKIP_TYPES`, and the
`Buy ` prefix), with `test_a_random_hint_names_junk_but_never_a_shop_refill` (fails without the filter for both a
`Shop`-typed and an `Item`-typed refill). The Poe on stone 02 was a sometimes hint (`Wasteland Chest` holds `Buy
Poe`), which OoT Randomizer does not filter either; there a `Buy` item never leaves the shops, here r5's shop shuffle
puts them in chests. Junk stays nameable, as there (question 4 below).

Hint kinds and named items for 7c (same placements, `balanced`), the first build and `seed-shop-7c-next`:

| Kind | 7c first build | 7c-next |
|---|---|---|
| woth | 6 | 4 |
| barren | 2 | 3 |
| item | 8 | 13 |
| sometimes | 9 | 8 |
| random | 11 | 10 |
| junk | 4 | 2 |

Random hints, first build: 5 shop refills (Green Potion, 10 Deku Seeds, Blue Fire, 3 Bombchus, 10 Deku Nuts), 4
rupees, Ice Arrows, a Deku Shield. 7c-next: no refill; 5 rupees, 2 Business Scrub Seeds, a Deku Stick, the Kokiri
Sword, a Piece of Heart. Every kind moved because one random draw has fewer candidates, which shifts every later draw
of the hint generator. Observation, not checked: a random hint names logic item `Deku Stick (1)` as "Three Deku
Sticks" (r5's item-name table).

**The folder.** My first rebuild ran `shutil.rmtree(seed-shop-7c)` while `hookshot.exe` (PID 49340) was running with
that overlay. It deleted `romfs/`, then stopped on the open `hookshot_log.txt`; I posted it. Two more builds, with only
`romfs/` removed, then wrote the fixed romfs into that folder while the game ran: one before the rebase onto
`9b4735c`, one after. Then came the reviewer's stop, and the reviewer restores the romfs from 7b. After the stop
nothing more was written there. `make_7c.py` now builds `seed-shop-7c-next` (asserting it is not the played folder),
and no longer rewrites `Play shop seed 7c.bat` (cmd reads a running batch file as it goes). **Rule for this track:
before deleting or overwriting a folder, check `tasklist /FI "IMAGENAME eq hookshot.exe"`. Never delete or overwrite a
folder a running game may read (an overlay, its log, its launcher); build into a new folder for the reviewer to swap
in.**

**`seed-shop-7c-next`** (`E:/OOTRemake/work/r7-hints/`): romfs, `spoiler.json`, `play-note.md`, built on 35320e0. The
placements are 7b's, beatable in 25 spheres. 7b's 77 files are byte-identical; it adds the stone flow (identical to
the first 7c's) and the 13 language archives (all changed, nothing else did). The reviewer swaps it into
`seed-shop-7c` after Kareem quits; the launcher is unchanged. What Kareem should see at the Temple of Time, left to
right (names highlighted, the rest in the stone's colour, `/` a row break):
1. "They say Gerudo Training Ground Like Like Hall Bomb Wall / Chest holds the Red Rupee."
2. "They say Kokiri Forest hides the Goron Tunic."
3. "They say searching Zora's Domain would only waste the hero's / time."
4. "They say searching Dodongo's Cavern would only waste the / hero's time."

**Report:** after each highlighted name, are " holds the ", " hides the " and " would only waste ..." back in the
stone's ordinary colour?

## Questions for Kareem

1. Answered (7c, above): the Temple of Time stones speak without the mask, `_01` to `_04` left to right; the colour
   bug is fixed in `seed-shop-7c-next`, which is waiting for the in-game check above.
2. Answered (D26): `always` by default; `mask` hints start from the mask (modelled, above). English in every archive.
3. **Distribution:** `balanced` (OoT Randomizer's default) as the default, with `strong` and `useless` as options?
4. **Junk in location hints:** OoT Randomizer's random and sometimes hints may name junk (a Red Rupee, a Business
   Scrub Seed). Clawshot now does the same: random hints skip only `Drop`/`Event`/`Shop` items, as OoT Randomizer
   does. Should random and sometimes hints also skip junk (non-progression items), at the cost of differing from OoT
   Randomizer?

## Left for later

- Other hint givers (Skulltula House rewards, Dampé's diary, Sheik) and dual, goal and entrance hints.
- The Deku Tree, maze and Lake Hylia sets: which name is which stone (the Temple of Time row is settled, 7c).
- The HF cow grotto stone's `has_fire_source` and the adult Zora's Domain stone copy are OoT Randomizer's rules,
  not checked in the remake.

## Cross-track posts (thread `cs-r7`)

- The thread did not exist at first (`bermuda: no thread cs-r7`, exit 1; the reviewer created it). Posted at 16:23,
  in order: abbce51 (world: stones as hint locations; translator, 18 regenerated region files, `model.py`,
  `load.py`), 2cb1e98 (settings: `hints`, `hint_distribution`, CLI), 7fe2e97 (seed: `Seed.hints`, `spoiler`,
  `play_note`, `make_seed` hint step; hint seeds now write the size table for `CNzh`/`KRko`/`TWzh`) with e4c9d43
  (D26 mask rule). Handoff post below.

## Gates (on 35320e0, rebased on main `9b4735c`; only round-file and section 25 commits follow)

```
uv run ruff format --check                                  196 files already formatted
uv run ruff check                                           All checks passed!
uv run pytest                                               575 passed, 78 skipped (307 s)
OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump      77 passed, 576 deselected (764 s)
```

Earlier, on f180296 (on `dfe923a`): 186 formatted, check clean, 535 passed / 73 skipped, dump 72 passed. The first
dump run after the `dfe923a` rebase failed 3 tests, `tests/test_seed_dump.py::test_written_files_differ_only_where_the_plan_says[1-3]`:
the Kokiri Forest slice's folder listed the 16 language archives and the stone flow (the slice has stones, so it
gets hints) where the oracle expected only chest files, the intro and the size table. f180296 (now 62b9e9f) adds the
other steps' files to the expected list and checks their size-table entries are raised only to what they need. The
three then passed (each "other steps: 17 files, size table written").

The `9b4735c` rebase had two conflicts. In `patch/__init__.py`, main's `drops` import and this branch's `text` import
merged into one line. In `03-game-data.md`, section 25 now sits before main's 26 and 27.

## Handoff

Commits on `r7/hints` (rebased on `9b4735c`): 43a18ec world (stones as hint locations, shared), 3f03bec the 40 stones
and labels, d099e91 hint selection, 78f0d15 settings (shared), eab8b5d the stones' lines, d91b197 seed step, spoiler
and play note (shared), 4784433 shop refills not major, 7bef02d the D26 mask rule, 33b36ab round file and section 25,
62b9e9f the seed oracle test (shared), 70787c6 gates and handoff, 57a7fe9 names end with colour `ffff`, 4552332
random hints skip Drop/Event/Shop items, 35320e0 Temple of Time stones settled, then this commit. Checked: the four
gates above, `seed-shop-7c-next` built, read back and compared with 7b and with the first 7c by SHA-256. Left:
Kareem's look at `seed-shop-7c-next` (colour back after each name), questions 3 and 4, other hint givers and the
unsettled stone names (above).
