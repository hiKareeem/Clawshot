# Round 3, track A: seed output (cs3a)

Branch `r3/seed`, rebased on main `1fbc78b` (track B's `formats.rstb` and census, track C's whole world). Owns `src/clawshot/patch/`,
`src/clawshot/data/item_actors.toml`, `src/clawshot/__main__.py`, `src/clawshot/generate/`, `tests/test_patch*.py`,
`tests/test_seed*.py` and this file.

## What was built

| Item | Where | State |
|---|---|---|
| keep_vanilla (reviewer's request for track C) | `generate/fill.py` `shuffled_locations`, test in `tests/test_generate.py` | 3dc8dbe, merged to main |
| 1 Item to actor table | `src/clawshot/data/item_actors.toml`, `src/clawshot/patch/items.py` | done |
| 2 Patch plan, story overrides | `src/clawshot/patch/plan.py`, `src/clawshot/patch/events.py`, `src/clawshot/patch/chest_events.toml` | done |
| 3 Writer, with the size table | `python -m clawshot`, `src/clawshot/patch/write.py`, `src/clawshot/patch/__init__.py`; dump tests | done |
| 4 Three seeds for Kareem | `E:/OOTRemake/work/r3-seed/seed-{3,7,22}/` (outside the repo) | done |

`python -m clawshot --romfs <dump> --seed <n> --out <dir> [--shuffle ...] [--dungeon-items ...] [--logic ...]`:

1. builds the world, runs the census on the dump (`census.scan`, read only) and links each shuffled world location
   to its census chests through `locations.toml` `oot_randomizer_name` (all copies: a name carried by several Hashes
   gets the same item in each);
2. **the pool is what the remake's chests hold** (below): each linked chest's actor read back through
   `item_actors.toml` as a logic item, passed to `generate(..., vanilla=...)`;
3. the fill and the beatability search are `clawshot.generate`'s, unchanged;
4. the plan: for every chest whose actor changes, each file of the census `files` and the Hash, the new
   `Drop__DropActor`, and `GetEventName` removed where `chest_events.toml` says the override is tied to the vanilla
   item; a chest that gets the actor it already holds is left alone (and keeps its override);
5. writes `<dir>/romfs/<path>` for the changed files only (each built, re-read and compared with the changed tree
   before anything is written) and `<dir>/spoiler.json`: the generator's spoiler plus a `patch` section (each
   change with its files, old and new actor, removed override and the story state it set; unchanged chests; census
   chests no world location names, which keep their items). `<dir>` must be empty or absent;
6. the resource size table (`clawshot.formats.rstb`, track B): each changed file's entry is raised to
   `rstb.required_size` when it is short, never lowered; the table goes into `<dir>/romfs/` only if an entry changed.
   The command line prints each file's entry, kept or raised.

`python -m clawshot.generate` is gone: its options moved to `python -m clawshot` (clean cutover).
`plans/04-world-format.md` "Generating a seed" (track C's file) still names it; posted on the thread.

## Item 1: `item_actors.toml`

Logic item -> the actor a chest's `Drop__DropActor` takes, with the linked location(s) each pair comes from. Every
actor in it is one the game itself puts in a chest. Backwards, one actor gives one logic item, except the actors
shared by every dungeon's own items (`Item_Dungeon_Map`, `_Compass`, `_BossKey`, `_SmallKey`), where the chest's
dungeon picks it. Checks: `table.check(world.items)` (every item known to the world, an actor shared only by one
item per dungeon); `tests/test_seed.py` (every chest the ported world shuffles reads back to an item whose actor is
the same actor: "a placeable item with no actor" fails here); dump test `test_every_actor_in_the_table_is_in_the_game`
(each actor has `Pack/Actor/<actor>.pack.zs`).

**Derivation** (throwaway `E:/OOTRemake/work/r3-seed/pairs.py`: census `vanilla_item` against OoT Randomizer's
vanilla item, `LocationList.py` at `526b4c8d`, over every linked chest). Agreeing pairs are in the table with their
location names. Where they disagree, the remake changed the chest's contents:

| OoT Randomizer vanilla | remake actor | locations |
|---|---|---|
| Recovery Heart | `TBox_DekuNutBundle` | Deku Tree Slingshot Room Side Chest, Compass Room Side Chest |
| Recovery Heart | `Item_DekuStickBundle_Small` | Deku Tree Basement Chest |
| Recovery Heart | `TBox_Rupee_Blue` | KF Midos Bottom Right Chest |
| Rupees (20) | `TBox_Rupee_Green` | KF Storms Grotto Chest |
| Rupees (20) | `Item_ScrubBusinessSeed` | ZR Open Grotto Chest |
| Rupees (50) | `Item_ScrubBusinessSeed` | DMT Chest, Wasteland Chest |
| Bombchus (10), (20) | `Item_BombchuBundle_Small` (holds 5) | Spirit Temple Child Climb North Chest, Ganons Castle Spirit Trial Crystal Switch Chest |
| Progressive Hookshot / Strength | the tier's actor | Dampe Race Hookshot, Water Temple Longshot, Spirit Silver Gauntlets, Shadow Trial Golden Gauntlets (fixed items: the tier) |

Not in the table, for later rounds (posted for track C):

- `Item_ScrubBusinessSeed` (13 chests), `Tbox_MagicJar_Large` (1) and `Obj_Rupee_Green` (the inferred default of
  the 3 chests without a drop) have no OoT Randomizer item; the whole-game pool needs logic items for them (D12:
  the seed is filler).
- `Boss Key (Ganons Castle)`: its type `GanonBossKey` carries no dungeon in the world model, so the backwards lookup
  cannot tell `Item_Dungeon_BossKey` in Ganon's Tower from the other boss keys.
- Ammo names are OoT Randomizer's nearest: `Deku Nuts (5)` is the remake's 3-nut bundle, `Deku Stick (1)` its
  3-stick bundle (`PouchActorInfo` `BundleActorNum`); the logic only asks whether one is held.

## Item 2: the patch plan and story overrides

`chest_events.toml` classifies every `GetEventName` on a census chest (32 values; a dump test fails for any chest
override the file lacks). Read from the decoded flows (`E:/OOTRemake/work/r1-research/decoded/`, printed by the
throwaway `E:/OOTRemake/work/r3-seed/flows.py`; output in `chest_event_flows.txt` there):

- `remove`, tied to the vanilla item: `Get_StoneOfForest_GetSword` (sword cutscene), the Deku Tree's
  `InsideTheDekuTree_GetMap`/`_GetCompass`/`_GetSlingShot` (the big-chest event, then a Navi balloon about the item:
  index 354, 345, 474; the item is inferred from the names, the text was not read), and, outside the slice, the
  other Navi-line overrides (Hammer, Bow, Bomb Bag, Hover Boots, Lens, boss keys, Longshot room) and four story
  beats.
- `keep`: `KokiriForest_TreasureBox_NaviChatOff` (sets that flag, then the default small-chest `Success_`; round 1's
  Boomerang chest had it), NaviChat overrides that only play the default big-chest event, Dampé's race, the Jabu
  Ruto chests (Ruto's room state), `SageOfSpirit_GetShield`.

**Story state per removed override (the slice):**

| Override | State it leaves | Seed restores it |
|---|---|---|
| `Get_StoneOfForest_GetSword` | `HavePlayedEvent.Get_StoneOfForest_GetSword`, `HavePlayedEvent.Dm_Kokiri_0063`; the cutscene equips the sword | nothing to restore [inference, r2-census]: no flow or AINB reads those flags; Mido reads owning the sword, which the item gives wherever found. **The in-game test below checks it.** |
| `InsideTheDekuTree_GetMap`, `_GetCompass`, `_GetSlingShot` | only `HavePlayedEvent.<row>` | nothing: no event flow or `Logic`/`Sequence` AINB names them (byte search) |

**Outside the slice, no data path yet (findings for round 4):** `SageOfWater_MelodyGet_Water` (the Iron Boots chest
teaches the Serenade of Water and sets `SageOfWater_GetWaterSerenade` and SageOfWater challenge steps),
`SageOfSpirit_NaboorIsTakenAway` (Nabooru cutscene, SageOfSpirit `Step07`), `SubEvent_GetIceArrow_OpenTBox`
(side-quest step `Complete`), `InsideGanonCastle_Get_Gauntlet_Gold` (cutscene `Dm_InsideGanonCastle_0006`, not
read). Each needs an event-flow edit (EVFL writing) before its chest can take another item without losing the step.

Track B (18:02 post): every Treasure Chest Game box has `Dynamic.DropViewActor`, the model shown. The plan
changes only `Drop__DropActor`; when the reward chest joins (D17), the plan must change `DropViewActor` with it.
Track B's census now has the kind `treasure_game_reward` for that chest; `plan.link` accepts census `chest` only, so
a shuffled reward chest stops the plan with a message until the reward joins (and its `DropViewActor` with it).
The writer checks every changed actor against the census (Gyaml, current drop, override) and fails otherwise.

## Item 3: how it was checked

| Command | Result |
|---|---|
| `uv run pytest tests/test_patch.py` | 17 passed: table lookups and errors, links and their refusals (no definition, not in the census, a treasure-game box), remake pool (dungeon picks the map; copies that disagree stop), plan (only moved chests, both copies, tied override removed and kept one kept, unclassified override stops), writer (only the planned fields change in every copy, nothing written when one file does not match the census, refuses a non-empty folder or one inside the romfs, same bytes twice; a short size-table entry raised to `required_size`, a roomy one kept, the other entries untouched, and no table written when every entry fits) |
| `uv run pytest tests/test_seed.py` | 1 passed: every shuffled chest of the ported world reads back to an item and the same actor |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_seed_dump.py -s` | 6 passed: seeds 1, 2, 3 written, every file read back and diffed field by field against the original (`Actors` matched by Hash): the set of changed fields equals the plan's (`Dynamic/Drop__DropActor`, and `Dynamic/GetEventName` removed where planned); the size table in the output equals the game's with exactly the short entries of changed files raised to `required_size` (seed 1: both KF Dynamic files), and is absent when every entry fits (seeds 2 and 3); the folder holds exactly those files and `spoiler.json`; `python -m clawshot --seed 4242` in two processes (`PYTHONHASHSEED` 1 and 2) gives byte-identical folders; every table actor exists; every chest override is classified |
| the four gates | see the end of this file |

Size changes the dump test printed (decompressed bytes): seed 1: Deku Tree Dynamic -12, Static -88, KF Adult and
Child Dynamic +60 (entries 516,328 -> 516,360 and 511,176 -> 511,208); seed 2: -12, -140, +8, KF Static files 0 and
-4; seed 3: -4, -140, +4, 0, +4, -4 (every entry kept).

## Item 4: three seeds for Kareem

Made after commit 218f436 (rebased on main 1fbc78b, track C's whole-world port) with a clean worktree
(`git status --short` empty), from `E:/OOTRemake/clawshot-r3/seed`. The world is now the whole game, so the seeds
name their slice (`--areas`, `--goal`, below). This is the third making: the sets from 67cbe01 (before the size
table) and f04b910 (before the whole world) were deleted and made again; all three give the same placements as
the first.

```
uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 3 --out E:/OOTRemake/work/r3-seed/seed-3 --areas KokiriForest LostWood InsideTheDekuTree --goal "'Defeat Queen Gohma'"
uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 7 --out E:/OOTRemake/work/r3-seed/seed-7 --areas KokiriForest LostWood InsideTheDekuTree --goal "'Defeat Queen Gohma'"
uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 22 --out E:/OOTRemake/work/r3-seed/seed-22 --areas KokiriForest LostWood InsideTheDekuTree --goal "'Defeat Queen Gohma'"
```

Each folder has `romfs/` (the overlay), `spoiler.json` and `play-note.md`. Picked from a survey of seeds 1-30
(throwaway `survey.py`) so the three differ: the Kokiri Sword in three different Mido's house chests, the Slingshot
in the Deku Tree basement (3), in the Deku Tree map chest (7) and in the Kokiri Sword chest (22).

Checked on the folders themselves (throwaway `E:/OOTRemake/work/r3-seed/verify.py`): each spoiler's placements,
on the slice world rebuilt from its `settings`, pass the beatability search (seeds 3 and 7: 4 spheres, seed 22: 3;
one more each than before the rebase, with the same placements: the world data under them changed, the cause not
traced); every
written placement file differs from the dump only in the fields `patch.changes` names (the dump test's field diff);
the size table, where written (seeds 7, 22), is the dump's with exactly the short entries raised, and absent in
seed 3 where every entry fits.

| Seed | Kokiri Sword | Slingshot | Kokiri Sword chest gives | Overrides removed |
|---|---|---|---|---|
| 3 | Mido's top-left | Deku Tree Basement Chest | Deku Nuts | sword, map, compass, slingshot |
| 7 | Mido's bottom-left | Deku Tree Map Chest | blue rupee | sword, map, slingshot |
| 22 | Mido's top-right | KF Kokiri Sword Chest | Slingshot | sword, map, compass, slingshot |

**Reaching the Deku Tree (all three):** closed forest, as OoT Randomizer's default: Mido blocks the path until Link
holds the Kokiri Sword and a Deku Shield. The shield is in the Kokiri shop for 40 rupees (`Shop_Weapon_Shield_Deku`
`BuyingPrice` 40); the reachable chests give 5 to 11 rupees, so grass and rocks make up the rest. The Kokiri Sword
is always in Kokiri Forest (the logic needs it before Mido lets you pass), so a seed with the sword in the Deku Tree
cannot come out. The Slingshot is needed for Queen Gohma (child reaches her through the basement back room).

**Size table** (entries by `rstb.required_size`, ceil32(size) + 264 for placement files):

| Seed | File | decompressed | entry in the game | entry written |
|---|---|---|---:|---:|
| 3 | KF Child Dynamic | 510,884 -> 510,888 | 511,176 | kept (fits) |
| 3 | KF Adult Dynamic | 516,036 -> 516,040 | 516,328 | kept (fits) |
| 7 | KF Child Dynamic | 510,884 -> 510,940 | 511,176 | 511,208 |
| 7 | KF Adult Dynamic | 516,036 -> 516,092 | 516,328 | 516,360 |
| 22 | KF Child Dynamic | 510,884 -> 510,944 | 511,176 | 511,208 |
| 22 | KF Adult Dynamic | 516,036 -> 516,096 | 516,328 | 516,360 |

Every other written file (Deku Tree Static and Dynamic, KF Static) shrinks or stays and keeps its entry. So seeds 7
and 22 carry `System/Resource/ResourceSizeTable.Product.111.Nin_Ounce_NVN2.rsizetable.zs` (1,761,406 bytes
decompressed, the same size as the game's; two entries changed), seed 3 does not. This is the first in-game run of
a replaced size table.

### In-game check for Kareem (one seed at a time, new game on an empty test user folder)

Through the round's copy of `E:/OOTRemake/work/r2-test/Clawshot test.bat`, with `HOS_FS_OVERLAY` pointing at
`E:/OOTRemake/work/r3-seed/seed-<n>/romfs`. Each `play-note.md` says where everything is. What to see:

1. Log: `fs: OpenFile(...KokiriForest_Child_Dynamic...): from the overlay` (and `..._Static` for seeds 3 and 7,
   `InsideTheDekuTree_...` once inside the tree). Seeds 7 and 22 should also log the size table
   (`...ResourceSizeTable...`) from the overlay, presumably at boot (round 1 track C saw the game open it), and
   still boot and load Kokiri Forest.
2. The Kokiri Sword chest plays the plain big-chest opening and gives its new item (seed 22: the Slingshot), **no
   sword cutscene, no sword**.
3. The Kokiri Sword from a small chest in Mido's house, with its own get text; then the sword shows in the
   equipment menu and can be equipped. **Mido lets you pass once you also have the Deku Shield** (this is the open
   point of `Get_StoneOfForest_GetSword`: whether owning the sword from another chest is all Mido wants).
4. In the Deku Tree, the big chests with a removed override play the plain opening with no Navi line naming their
   vanilla item; the Slingshot, map and compass come from their new chests; Gohma can be beaten.
5. Seed 22 also shows a Slingshot from the big story chest, and seed 3 a Slingshot from a small chest.

## Provisional choices (for review)

1. **The pool is the remake's chest contents**, not OoT Randomizer's vanilla items. OoT Randomizer's four "Recovery
   Heart" chests in the slice hold nuts, sticks and a blue rupee here, and its "Rupees (20)" grotto chest a green
   rupee; a pool of OoT Randomizer items would put actors in chests the game never does (a recovery heart,
   `Obj_Heart`, in a chest is untested), and differ from the remake's item counts. With the remake's contents every
   seed only moves actors the game already gives from chests. `generate(..., vanilla=)` is optional, so the
   world's own tests (track C) still fill from OoT Randomizer's items. **Kareem: should a seed's pool be the remake's
   chest contents (as now) or OoT Randomizer's N64 contents?**
2. **Which overrides are removed**: only those tied to the vanilla item (story beats and Navi lines about it); those
   that are the default event plus item-neutral state stay. A chest whose item does not change keeps its override.
3. **`chest_events.toml` lives in `src/clawshot/patch/`** (the only data path this track owns besides
   `item_actors.toml`); it could move to `src/clawshot/data/` at review.
4. **The spoiler's `patch` section** carries the plan (actors, files, removed overrides and their story state), so
   one file explains a seed. Item names in `placements` stay logic (OoT Randomizer) names.
5. **The output folder must be empty or absent**: a stale file from another seed would mix two seeds; the writer
   never deletes.
6. A failed write leaves nothing: all files are built and checked before the first is written.
7. **Remake-only chests** (D12) are not shuffled until the world has a location for them: in the slice the KF purple
   chest (4349272251343787229, by the stick-upgrade scrub) and the LW one (17479747339356189279, by the bridge
   scrub). The spoiler lists them under `vanilla_chests`. Posted for track C.
8. **World slices** (218f436): `Settings.areas`/`goal` (`--areas`, `--goal`) keep only the regions in those census
   areas plus the area-less start regions (`Root`, spawns, warp songs; their exits elsewhere dangle) and swap the
   goal; the spoiler's `settings` records both, so a slice seed is reproducible from its log. A goal without areas
   is refused.
9. **`dungeon_items = "anywhere"` sets the logic setting `keysanity = true`** where the world has it (track C's
   18:23 note: otherwise OoT Randomizer's rules count one free Fire Temple key); an explicit `keysanity = false`
   with keys anywhere is an error. The spoiler's `settings.logic` shows it.

## Cross-track posts (thread `cs-r3`)

- 18:13: keep_vanilla commit 3dc8dbe (reviewer's request for track C).
- 18:20: seed writer on the branch; `python -m clawshot.generate` removed (04-world-format.md names it); for track C:
  Ganon's boss key has no dungeon in the model, remake-only chests need world locations, and the whole-game pool
  needs logic items for `Item_ScrubBusinessSeed`, `Tbox_MagicJar_Large` and the default `Obj_Rupee_Green`.
- 18:36: size table in the writer (after the rebase on track B's rstb).
- After the rebase on track C's whole world: slices, keysanity, seeds made again (this section's latest commit).

## Left for later

- The size table is written now; whether the game honours a raised entry, or needed it, shows in seeds 7 and 22 in
  game.
- **The whole world does not make a seed yet:** `python -m clawshot` without `--areas` stops at the link step with
  99 shuffled chest locations that no census definition names (e.g. `HF Southeast Grotto Chest`, `GV Chest`);
  round 4 needs those linked (or `n64_only`/`keep_vanilla`), plus the logic items above. Track C's
  `Graveyard Dampe Race Freestanding PoH` (now type `Chest`) is a census chest and links as one.
- Round 4: event-flow edits for the four story overrides with state, the Treasure Chest Game reward chest's
  `DropViewActor`, and the three drop-less chests (the writer adds `Drop__DropActor` to them, untested in game).

## Gates (before the handoff, on 218f436, rebased on main 1fbc78b)

```
uv run ruff format --check                                  65 files already formatted
uv run ruff check                                           All checks passed!
uv run pytest                                               168 passed, 18 skipped
OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump      17 passed, 169 deselected
```
