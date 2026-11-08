# Round 5, track D: gifts through the flows (cs5d)

Branch `r5/gifts`, from main `91b3ed5`, rebased on `cd592e3` and then on `ccd1963` (r5/shops merged; conflicts resolved
in section placement, `item_actors.toml` and `allowed()`; hashes below are after that rebase). Owns
`src/clawshot/patch/gifts.py` (new), `src/clawshot/census/gifts.py`, `src/clawshot/formats/evfl.py`,
`tests/test_gift*.py`, `tests/test_evfl*.py`, this file and section 19 of `plans/03-game-data.md`. Scratch scripts and
decoded data: `E:/OOTRemake/work/r5-gifts/` (outside the repo).

| Item | Where | Commit |
|---|---|---|
| 1 readers of each gift's item, flags to use, classes | `plans/03-game-data.md` section 19, this file | 5a6414c |
| 2 `patch/gifts.py`: item swap, flag rewrites, skips | `src/clawshot/patch/gifts.py`, `src/clawshot/patch/gift_rules.toml`, `tests/test_gifts.py`, `tests/test_gifts_dump.py`; section 19 revised (reviewer, 08:40) | 5828fc6 |
| (needed by 2) a size formula for `GameDataList` | `src/clawshot/formats/rstb.py`, `tests/test_rstb_dump.py` (no owner this round; posted) | b2bf7d4 |
| 3 in-game test folders | `E:/OOTRemake/work/r5-gifts/ingame/`, this file | cb18c63 |
| (needed by 4) item actors for the gift items | `src/clawshot/data/item_actors.toml` (track C's; posted; at the rebase the two tunics were dropped, track B maps them to shop actors) | 2f05d15 |
| 4 `--shuffle Gift` through `make_seed`'s extra steps | `src/clawshot/patch/gifts.py`, `src/clawshot/__main__.py`, tests | eab6195 |
| (reviewer) songs to song locations, chestless gift items to gifts | `src/clawshot/generate/fill.py`, `tests/test_generate.py` (track C's; alone, posted) | 52d0342 |
| (reviewer) the gift shuffle uses it; a song-in-a-chest test output | `src/clawshot/patch/gifts.py`, tests; `E:/OOTRemake/work/r5-gifts/ingame/chest-song-storms` | d385896 |
| round file for item 4 | this file | 2a64445 |
| (reviewer) GC Darunias Joy held vanilla unless `free_time_travel` | `src/clawshot/patch/gifts.py`, `tests/test_gifts.py` | bf63f8a |
| `Gift` among the `--shuffle` choices (track B made it a choice list) | `src/clawshot/__main__.py` | 409c40b |
| (reviewer) Kareem's five results in section 19, "In game" | `plans/03-game-data.md` | 3cee2c7 |
| (reviewer) the Great Fairies join the gift shuffle through their new flags | `src/clawshot/patch/gifts.py`, `tests/test_gifts.py`, `tests/test_gifts_dump.py` | 2c4a427 |
| (reviewer) `chest-song-storms-kak` test output; results and the new test in this file | `E:/OOTRemake/work/r5-gifts/ingame/`, this file | (this file's commit) |

## Item 1: what reads each gift's item, and the classes

The table and the facts behind it are in section 19. In short, over the 79 gift checks linked to OoT Randomizer names
(93 steps):

| Class | Checks | What the patch does |
|---|---:|---|
| 1 item swap only | 45 | sets the step's item parameter (every step of the check) |
| 2 swap plus rewrite | 19 | also: a new saved flag per check, set after the gift, replacing the flow's "already given" reads of the vanilla item (six Great Fairies, Song from Windmill); or skips steps that would give or take something else (the twelve songs' play-along add, Biggoron taking the Giant's Knife) |
| 3 needs more | 15 | not changed: nine boss rewards, three timed trades with a retry step, three sales inside `SimpleShop` |

How it was found: `E:/OOTRemake/work/r5-gifts/readers.py` (run with `uv run python ...` from this worktree) loads every
flowchart the game loads, joins them through `SubFlow` calls and `EventTransition`s by `EventSetting` row, and lists per
check the item reads on paths into the gift step, the item reads elsewhere, and the saved flags read before and set
after the step. Each class-2 and class-3 check, and each "gate" reader, was then read in the flow by hand (an
interactive session over the same functions: `pflow`-style dumps of the entry points involved). Logic modules: round
4's decoded JSON (`E:/OOTRemake/work/r4-fast-start/ainb_json/`, grep for `IsGet.` and item names). Placements: every
`Presence.FlagName` and parameter string. Saves: `clawshot.save` on `E:/OOTRemake/work/save-backups/` (read only).

Findings worth a second look by the logic tracks (also in section 19):

- **The castle-grounds soldier opens his gate for `IsGet.Item_WeirdEgg`** (`Npc_Hylia_Soldier_009_Child` Event6 ->
  `Npc_Hylia_Soldier_009_Child_OpenTheGate`); OoT Randomizer's `HC Garden` asks `Weird_Egg or Chicken`, which matches
  as an item gate.
- **No flow, logic module or placement reads a spiritual stone or medallion.** The Door of Time reads the dungeons'
  quest steps (`Get_StoneOfFire_IsCompleted_Exp`, `Get_StoneOfWater_IsCompleted_Exp`) and
  `HavePlayedEvent.Dm_MelodyGet_Zelda`. Shuffling boss rewards (class 3) needs those gates rewritten to items or the
  logic to ask for the bosses.
- **The Serenade of Water lives inside a chest's open event** (reviewer's request): the Ice Cavern Iron Boots chest
  (`SageOfWater_MelodyGet_Water`) is the only start of `Dm_MelodyGet_Water`; the census has its step
  (`Dm_MelodyGet_Water/Event29`, `Sheik in Ice Cavern`), class 2. The other three kept chest overrides (Ice Arrows, gold
  gauntlets, Silver Gauntlets/Nabooru) reach no gift step.

## Item 2: `clawshot.patch.gifts`

`src/clawshot/patch/gift_rules.toml` holds one entry per linked gift check (79): `class` (`swap`, `rewrite`, `more`),
`gate` (evidence), and for `rewrite` the `given` reads, an optional existing `flag`, and the `skip` steps; `more` has a
`reason`. `clawshot.patch.gifts`:

- `load()` / `loads(text)`: the rules, refusing unknown fields and classes, edits on a non-`rewrite` check, a `rewrite`
  with nothing to do, a flag without reads, a `more` without a reason.
- `plan(placements, gifts, definitions, rules) -> [GiftChange]`: placements are OoT Randomizer name -> item actor; the
  census steps linked to each name form the check; refuses an unlinked name, a check with no rule, a `more` check.
- `file_changes(changes, files) -> {romfs path: transform}`: one transform per flow touched and one for `GameDataList`
  when a check needs a new flag. Each transform takes and returns the decompressed file, so they compose with other
  kinds' changes to the same file in `clawshot.patch.write` (the reviewer's point 2); the flow transform reads, edits
  and writes the flow and checks it reads back; the `GameDataList` transform does the same with BYML, keeping big endian.
- The edits: every step's item parameter (refused unless it holds the census's vanilla item); for a new flag, an
  `EventTriggerSetGameDataBool` event appended to the flow (`ClawshotGift<n>`) between the step and its `next`; each
  `given` read (refused unless it is `GameDataActor.EventQueryIsGameDataBool` on `IsGet.<vanilla item>`) made to read the
  flag; each `skip` step's predecessors (`next`, switch cases, fork branches, entry points) pointed at its `next`
  (refused for a step without one or with nothing leading to it). New events are appended, so no index moves.
- `add_flags(tree, names)`: appends saved Bools to a parsed `GameDataList` and grows the four `MetaData` layout values
  by 8 bytes per flag, after checking the values match the entries by the formula in section 19 (refused otherwise, and
  for a name whose hash any list already has).

**Flags (the reviewer's point 1, 08:40).** Song from Windmill now reads the existing
`HavePlayedEvent.Dm_MelodyGet_Storm` (`flag` in the rules; nothing is set or added). For the six Great Fairies no
existing flag works; section 19 gives the reason for each candidate (the fountain's `HavePlayedEvent`, the
`Meet_GreatFairy_0N` flags, the shared fairy flags, the count and the quest). They get new Bools, and item 3 has the
old-save test.

Checks:

| Command | Result |
|---|---|
| `uv run pytest tests/test_gifts.py` | 13 passed: swap touches only the steps; a new flag is set after each step and replaces the read, and the file round-trips; an existing flag is read and nothing is set; skip re-points cases, `next` and entry points; refusals (stale item, a read of another flag, not a query, a step without `next`, skipped twice, unknown event); rules and plan refusals; `GameDataList` flags appended, the four layout values grown, the formula refused when it does not hold, a taken hash refused, big endian kept; every linked gift check in `locations.toml` has a rule |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_gifts_dump.py -s` | 3 passed: all 64 class 1-2 checks given `Item_Boomerang` at once: 54 flows changed, each reads back and differs from the game's only in its steps, given reads and skip predecessors (new events appended, actors only gain action names, entry points equal); every step gives the new item, every given read reads the flag, nothing leads to a skipped step; `GameDataList` differs only in the six added Bools and the four layout values (1,462,888 -> 1,463,136 bytes, within its size entry 1,463,176). Flows that grow (the fairies, `TriForcePoint` 27,768 -> 27,888 bytes, `Npc_Hylia_009_Adult`) can outgrow their size entry; `clawshot.patch.write` raises the entry, as for placement files |

## Item 3: in-game tests (`E:/OOTRemake/work/r5-gifts/ingame/`)

Built by `E:/OOTRemake/work/r5-gifts/make_tests.py` through `clawshot.patch.gifts` and the seed writer
(`clawshot.patch.write` with an empty chest plan), so the files are what a seed would write. Each folder holds only the
changed files under `romfs/`; each `Test - <name>.bat` was written from r2-test's fixed launcher: it starts
`E:\Games\Hookshot\hookshot.exe` only, with `HOS_FS_OVERLAY` at the folder's `romfs`, on a copy of
`E:/OOTRemake/work/save-backups/2026-11-07_llr-tower-before-pickup` in `ingame/user-<name>` (child Link at Lon Lon
Ranch: Fairy Ocarina, Saria's Song, Zelda's Lullaby, Sun's Song, Slingshot, Goron Bracelet, a bottle, 68 rupees, no
bomb bag, no Epona's Song, the cucco game and both Skull Kid prizes not done, no Great Fairy met: read with
`clawshot.save`). Not run by me. After a test, `uv run python E:/OOTRemake/work/r5-gifts/ingame/check_save.py <name>`
prints its flags from the test user's newest save.

| Test | Changed | Files |
|---|---|---|
| `talon-boomerang` (round 4's, rebuilt) | LLR Talons Chickens -> `Item_Boomerang` | `Minigame_FindOutCucco` |
| `skullkid-bombbag` (child NPC gift) | LW Skull Kid -> `Item_BombBag_Small` | `Npc_SkullKid_Child` |
| `din-fairy-hookshot` (Great Fairy, new flag, old save) | LW Skull Kid -> Bomb Bag (to reach the fountain); DMT Great Fairy Reward -> `Item_Hookshot` | `Npc_SkullKid_Child`, `Dm_FairyFountain_Din` (297,920 -> 298,256 bytes), `TriForcePoint`, `GameDataList` (+1 Bool, 1,462,888 -> 1,462,932 bytes), the size table (three entries raised) |
| `malon-song-heartpiece` (song) | Song from Malon -> `Obj_Heart_Piece` | `Dm_MelodyGet_Epona`, `Dm_SY_Ocarina` |

**What Kareem should do and see** (each from its own launcher; in every test the log shows
`fs: OpenFile(...<file>): from the overlay` for each changed file when the game first opens it):

1. `talon-boomerang`: in the ranch house, play Talon's cucco game and win: **the Boomerang** (its model and get text)
   instead of the milk bottle; it is in the item menu and usable. Talking to him again gives nothing more. Talon's lines
   still talk about milk.
2. `skullkid-bombbag`: in the Lost Woods, play Saria's Song to the Skull Kid on the stump: **the Bomb Bag** (model,
   text, bombs usable) instead of the heart piece. Playing to him again gives nothing more.
3. `din-fairy-hookshot`, the new-flag test, in this order:
   - **The save loads** (it was made before the patch and has no entry for the new flag): Continue works, Link is where
     he was.
   - Get the Bomb Bag from the Skull Kid as in 2.
   - On the Death Mountain summit, bomb the cracked wall, stand on the Triforce mark and play Zelda's Lullaby; the Great
     Fairy asks 25 rupees; say yes: **the Hookshot** (model and get text) instead of Din's Fire. With no magic yet the
     game may still show the magic gauge being born (the wrapper `GetInEvent_GreatFairyDin` does that when
     `PlayerStatus.MPMax` is 0): **say whether a magic gauge appears, and whether it stays.**
   - Leave the fountain, come back, play the lullaby again: **she only heals, asks no fee and gives no second
     Hookshot.** (Unpatched, she would offer again, because she checks `IsGet.Item_DinFire`.)
   - Let it autosave, quit to the title, Continue, go back and play again: **still only healing** (the new flag was saved).
   - Optional: at the Hyrule Castle fountain the lullaby still does nothing (no Din's Fire): the item gate is kept.
4. `malon-song-heartpiece`: at Lon Lon Ranch in the day, talk to Malon with the ocarina: the play-along runs as usual;
   at the end **a Piece of Heart** instead of Epona's Song. **Epona's Song is not in the ocarina's song list**, and
   talking to her again does not teach it again (or say if she does).
5. `chest-song-storms` (added at the reviewer's request; a NEW GAME in an empty test user, launcher like cs5b's
   corrected one): Mido's house, top left chest (`KF Midos Top Left Chest`, Hash 9725242744547055868) holds
   `Item_Melody_StormSong`; its open event `KokiriForest_TreasureBox_NaviChatOff` is kept. Open it: **does Link get the
   Song of Storms (get window, then in the song list and playable), or something else, or nothing, or does it
   crash?** Until this works, the gift shuffle keeps songs and other chestless gift items out of chests (item 4).

## Item 4: `--shuffle Gift`

`python -m clawshot ... --shuffle Chest Gift` (or `Gift` alone). `__main__` calls `gifts.seed_setup(romfs, load_spec(),
settings)` when `Gift` is asked for and passes its step to `make_seed(..., extra_steps=[step])`; nothing else in
`make_seed` changed (rebased on `ccd1963`, where it also adds the shop step itself). `seed_setup`:

- replaces `Gift` in `Settings.shuffle` with OoT Randomizer's gift location types (`NPC`, `Song`, `Cutscene`, `Boss`);
- picks the gift checks that may move (`seed_checks`, 49 of the world's 79 linked checks): class `swap` or `rewrite`
  (a Great Fairy through its new `GameDataList` flag since Kareem's `din-fairy-hookshot` result: four fairies move,
  the two Magic Meter ones stay, as their pool item is a tier, below); not an anchor (`ANCHORS`: **GC Darunias Joy
  stays vanilla** while `free_time_travel` is off, because the adult-return guarantee D20 relies on the child getting
  the Goron Bracelet there; the reviewer, 08:55); and whose world vanilla item has, in `item_actors.toml`, the actor
  every step of the check gives, so the pool item a check adds is what it gave. That last test leaves out 10 upgrade
  checks (both shooting galleries, Horseback Archery 1500, the Deku scrub target, both Deku Theater masks, the child
  Rolling Goron, Bombchu Bowling's first prize and bombchus, the 40-token reward: bags, quivers, capacities, bombchu
  packs) and the two Magic Meter fairies (HC, DMC: `Magic Meter` is a tier, `Item_FairyBless_MP` or `_MPDouble`),
  which need fixed-tier logic items first (`04-world-format.md`, "Not carried over yet"), and, since `ccd1963` maps
  the tunics to the shop actors `Shop_Armor_Goron`/`Shop_Armor_Zora`, the two tunic gifts (GC Rolling Goron as Adult,
  ZD King Zora Thawed, which give `Obj_Armor_*`);
- holds every other gift-type location vanilla (`restrict_spec`: `keep_vanilla` on a copy of the spec);
- holds songs to song locations and song locations to songs, and every other pool gift item whose actor no census
  chest holds to the `NPC`/`Cutscene`/`Boss` locations (`held_items`, through `Settings.item_location_types` and
  `exclusive_location_types`, the reviewer's request, in `generate/fill.py` as its own commit 52d0342, merged with
  track B's shop check in `allowed()`);
- returns the patch step: placements in, `file_changes` for every moved gift out (its item through `item_actors`).

Checks:

| Command | Result |
|---|---|
| `uv run pytest tests/test_gifts.py tests/test_generate.py` | 17 + 11 passed: `seed_checks` takes `swap`/`rewrite` checks whose pool item's actor is what they give (since 2c4a427 also one that needs a new flag), leaves out `more`, held and non-gift locations; `restrict_spec` holds the others vanilla on a copy; `seed_step` changes only moved gifts; `held_items`; in the fill, a song goes only to the song location, the song location takes only the song, and a held letter goes to one of two gift locations and never to a chest, over 40 seeds |
| `OOT_ROMFS=... uv run pytest -m dump tests/test_gifts_dump.py -k slice -s` | passed: the Kokiri Forest / Lost Woods / Deku Tree slice with `Chest Gift`, seed 7: no `more` check shuffled, every held item where it is held, each moved gift's steps written with the placed item's actor (moved: LW Skull Kid -> Deku Nuts (5), LW Trade Odd Potion -> Rupee (1), LW Ocarina Memory Game -> Poachers Saw) |
| `python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 7 --out E:/OOTRemake/work/r5-gifts/slice-7 --shuffle Chest Gift --areas KokiriForest LostWood InsideTheDekuTree --goal "'Defeat Queen Gohma'"` | 16 locations shuffled, 3 spheres; wrote the six placement files, `Npc_Kokiri_Fado_Adult`, `Npc_SkullKid_Child`, `Npc_SkullKid_Child_02` and the size table |
| the same with `--shuffle Chest Shop Gift` (after the rebase on `ccd1963`), `--out .../slice-7-shop` | 24 locations shuffled, 3 spheres; 13 files: the same three gift flows plus the shop changes; the shop and gift steps compose in one seed |
| `OOT_ROMFS=... uv run pytest -m dump tests/test_gifts_dump.py -k fairies` (after Kareem's results) | passed: a whole-world `seed_setup` holds only the two Magic Meter fairies vanilla; its step with DMT and ZF swapped (Farore's Wind, Din's Fire) adds two Bools to `GameDataList`, one of them `Clawshot.Gift.Dm_FairyFountain_Din.Event212`, the name Kareem's save showed set, and writes each fairy's steps with the other's actor |

Whole-game seeds could not be smoked on this base (main `cd592e3`): `--shuffle Chest Gift` stops at chests with no
census definition (track C's item 2), and `--shuffle Gift` alone fails every fill (seeds 1-5, 11) because two gift
locations are unreachable with every item held: `ToT Light Arrows Cutscene` and `Kak 100 Gold Skulltula Reward` lie
behind dungeons whose vanilla key layouts OoT Randomizer's worst-order key counts cannot prove (`04-world-format.md`,
"Key logic and the vanilla placement"); with chests shuffled, keys are placed by the fill.

## Left for later

- Songs and chestless gift items may go to chests once `chest-song-storms-kak` shows a song from a chest plays (and a
  key-item twin works). The two Magic Meter fairies need fixed-tier magic items, as the upgrades below.
- Class 3: the boss rewards (their story gates read dungeon quest steps; rewrite those reads or ask for the bosses in
  the logic), the three timed trades (retry steps), the three `SimpleShop` sales (a once flag inside the purchase).
- The 10 upgrade gifts need fixed-tier logic items (`Bullet Bag (40)`-style tiers per check); the two tunic gifts
  need the gift step to give the tunic under the shop actor or the table to keep both actors.
- The spoiler's `patch` section lists chest changes only; gift changes show in `placements`.
- Whole-game `--shuffle Chest Gift` seeds wait for every chest to be a location (track C's item 2).

## Provisional choices (for review)

1. **New `GameDataList` flags for "given", for the six Great Fairies only**, named `Clawshot.Gift.<flow>.<event>`
   after the check's first step; the windmill reads an existing flag. The `MetaData` save layout (file 0 and the
   all-files table) grows by 8 bytes per flag, by the formula section 19 derives from the entries and the saves.
   Kareem, 2026-11-08: the game keeps such a flag and an older save loads (`din-fairy-hookshot`); the fairies are in
   the gift shuffle since 2c4a427.
2. **Songs are class 2, not 3**: the play-along's add step for that song is skipped (its predecessors point at its
   `next`), so the song flow's own `GetPouchContent` gives the new item with its get window. The roadmap expected songs to
   need more; the data shows the play-along is called only by the twelve song flows and Scarecrow's, one add step per
   melody.
3. **Every step of a check gets the new item**, so a tier pick (`IsExistInPouch` of the medium bag) or two code paths
   (fishing) give the same item either way; the tier read stays.
4. **Lines are not changed** (NPCs still talk about the vanilla item; section 15).
5. **Medigoron, the bean salesman and the Wasteland bombchu salesman are class 3**: the sale runs inside the shared
   `SimpleShop` flow, which returns without giving on a refusal, so a "given" flag would need setting inside the shared
   purchase path; OoT Randomizer shuffles them only with non-default settings.

## In game (Kareem, 2026-11-08)

All five tests passed as described in item 3; the details are in `03-game-data.md` section 19, "In game". In short:
Talon gave the Boomerang (equippable; milk refills only into an empty bottle), the Skull Kid the Bomb Bag, Din's fairy
the Hookshot on the old save (once; no magic gauge, no Din's Fire; the new flag set in the save), Malon the heart piece
(no Epona's Song in the list). `chest-song-storms`: the chest showed a green rupee model with the Song of Storms'
pickup text and set `IsGet.Item_Melody_StormSong`; with no ocarina, whether the song plays is unknown.

Follow-up (reviewer's request), `E:/OOTRemake/work/r5-gifts/ingame/`, built by
`E:/OOTRemake/work/r5-gifts/make_chest_song_kak.py` through the seed writer (three Kakariko placement files, size
entries kept; the child file's chest reads `Drop__DropActor: Item_Melody_StormSong`; launcher checked with
`CLAWSHOT_DRY_RUN=1`):

6. `chest-song-storms-kak`, on a copy of the ranch save (child, Fairy Ocarina, Sun's Song, no Song of Storms; the
   chest's Hash unset in slot 01). Launch `Test - chest-song-storms-kak.bat`, load the ranch save (slot 01). Go out
   to Hyrule Field, up the steps to Kakariko, into the backyard by day (play the Sun's Song if it is night) and down
   the open grotto. Open the chest, then play the Song of Storms (A, down, up, A, down, up). **Expected: the song is
   in the song list and plays (its melody, rain starts).** Then
   `uv run python E:/OOTRemake/work/r5-gifts/ingame/check_save.py chest-song-storms-kak` prints
   `IsGet.Item_Melody_StormSong`. The log should show `fs: OpenFile(...): from the overlay` for
   `KakarikoVillage_Child_Dynamic.bcett.byml.zs`. Chosen over the Lon Lon Ranch tower chest, whose climb is unknown
   (`plans/playtest`, XC14).

## Questions for Kareem

1. **`chest-song-storms-kak`**: after the chest, does the Song of Storms play (melody and rain) and is it in the song
   list? What does the chest show this time (the green rupee again)?

## Cross-track posts (thread `cs-r5`)

- 08:22: item 1 (e47caf5), the classes, the Serenade inside the Ice Cavern chest's event, GameDataList heads-up.
- 08:36: item 2 (acde59a), the `GameDataList` size formula commit (0cf3725) outside my files.
- 08:38: item 3 ready.
- 08:41: item actors for the gift items (6d754f6) in track C's `item_actors.toml`.
- 08:50: item 4, the `allowed()` commit in track C's `fill.py`, its use (pre-rebase hashes a537bd5, 6e0a7f8, b44bb4e; now eab6195, 52d0342, d385896).
- handoff: below.

## Gates (on 409c40b, rebased on main `ccd1963`, before the handoff)

```
uv run ruff format --check                                  129 files already formatted
uv run ruff check                                           All checks passed!
uv run pytest                                               349 passed, 36 skipped
OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump      35 passed, 350 deselected
```
