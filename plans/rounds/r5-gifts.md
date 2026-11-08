# Round 5, track D: gifts through the flows (cs5d)

Branch `r5/gifts`, from main `91b3ed5`, rebased on `cd592e3`. Owns `src/clawshot/patch/gifts.py` (new),
`src/clawshot/census/gifts.py`, `src/clawshot/formats/evfl.py`, `tests/test_gift*.py`, `tests/test_evfl*.py`, this file
and section 19 of `plans/03-game-data.md`. Scratch scripts and decoded data: `E:/OOTRemake/work/r5-gifts/` (outside the
repo).

| Item | Where | Commit |
|---|---|---|
| 1 readers of each gift's item, flags to use, classes | `plans/03-game-data.md` section 19, this file | e47caf5 |
| 2 `patch/gifts.py`: item swap, flag rewrites, skips | `src/clawshot/patch/gifts.py`, `src/clawshot/patch/gift_rules.toml`, `tests/test_gifts.py`, `tests/test_gifts_dump.py`; section 19 revised (reviewer, 08:40) | acde59a |
| (needed by 2) a size formula for `GameDataList` | `src/clawshot/formats/rstb.py`, `tests/test_rstb_dump.py` (no owner this round; posted) | 0cf3725 |
| 3 in-game test folders | `E:/OOTRemake/work/r5-gifts/ingame/`, this file | dc576d3 |
| (needed by 4) item actors for the gift items | `src/clawshot/data/item_actors.toml` (track C's; posted) | 6d754f6 |
| 4 `--shuffle Gift` through `make_seed`'s extra steps | `src/clawshot/patch/gifts.py`, `src/clawshot/__main__.py`, tests | a537bd5 |
| (reviewer) songs to song locations, chestless gift items to gifts | `src/clawshot/generate/fill.py`, `tests/test_generate.py` (track C's; alone, posted) | 6e0a7f8 |
| (reviewer) the gift shuffle uses it; a song-in-a-chest test output | `src/clawshot/patch/gifts.py`, tests; `E:/OOTRemake/work/r5-gifts/ingame/chest-song-storms` | b44bb4e |

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
`make_seed` changed. `seed_setup`:

- replaces `Gift` in `Settings.shuffle` with OoT Randomizer's gift location types (`NPC`, `Song`, `Cutscene`, `Boss`);
- picks the gift checks that may move (`seed_checks`, 48 of the world's 79 linked checks): class `swap` or `rewrite`;
  not needing a new `GameDataList` flag (the reviewer: the six fairies wait for `din-fairy-hookshot`; `new_flags=True`
  takes four of them, the other two are upgrades); and whose world vanilla item has, in `item_actors.toml`, the actor
  every step of the check gives, so the pool item a check adds is what it gave. That leaves out 10 upgrade checks (both
  shooting galleries, Horseback Archery 1500, the Deku scrub target, both Deku Theater masks, the child Rolling Goron,
  Bombchu Bowling's first prize and bombchus, the 40-token reward: bags, quivers, capacities, bombchu packs), which need
  fixed-tier logic items first (`04-world-format.md`, "Not carried over yet");
- holds every other gift-type location vanilla (`restrict_spec`: `keep_vanilla` on a copy of the spec);
- holds songs to song locations and song locations to songs, and every other pool gift item whose actor no census
  chest holds to the `NPC`/`Cutscene`/`Boss` locations (`held_items`, through `Settings.item_location_types` and
  `exclusive_location_types`, the reviewer's request, in `generate/fill.py` as its own commit 6e0a7f8);
- returns the patch step: placements in, `file_changes` for every moved gift out (its item through `item_actors`).

Checks:

| Command | Result |
|---|---|
| `uv run pytest tests/test_gifts.py tests/test_generate.py` | 17 + 11 passed: `seed_checks` takes `swap`/`rewrite` checks whose pool item's actor is what they give, leaves out `more`, new-flag checks (unless asked), held and non-gift locations; `restrict_spec` holds the others vanilla on a copy; `seed_step` changes only moved gifts; `held_items`; in the fill, a song goes only to the song location, the song location takes only the song, and a held letter goes to one of two gift locations and never to a chest, over 40 seeds |
| `OOT_ROMFS=... uv run pytest -m dump tests/test_gifts_dump.py -k slice -s` | passed: the Kokiri Forest / Lost Woods / Deku Tree slice with `Chest Gift`, seed 7: no `more` or new-flag check shuffled, every held item where it is held, each moved gift's steps written with the placed item's actor (moved: LW Skull Kid -> Deku Nuts (5), LW Trade Odd Potion -> Rupee (1), LW Ocarina Memory Game -> Poachers Saw) |
| `python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 7 --out E:/OOTRemake/work/r5-gifts/slice-7 --shuffle Chest Gift --areas KokiriForest LostWood InsideTheDekuTree --goal "'Defeat Queen Gohma'"` | 16 locations shuffled, 3 spheres; wrote the six placement files, `Npc_Kokiri_Fado_Adult`, `Npc_SkullKid_Child`, `Npc_SkullKid_Child_02` and the size table |

Whole-game seeds could not be smoked on this base (main `cd592e3`): `--shuffle Chest Gift` stops at chests with no
census definition (track C's item 2), and `--shuffle Gift` alone fails every fill (seeds 1-5, 11) because two gift
locations are unreachable with every item held: `ToT Light Arrows Cutscene` and `Kak 100 Gold Skulltula Reward` lie
behind dungeons whose vanilla key layouts OoT Randomizer's worst-order key counts cannot prove (`04-world-format.md`,
"Key logic and the vanilla placement"); with chests shuffled, keys are placed by the fill.

## Provisional choices (for review)

1. **New `GameDataList` flags for "given", for the six Great Fairies only**, named `Clawshot.Gift.<flow>.<event>`
   after the check's first step; the windmill reads an existing flag. The `MetaData` save layout (file 0 and the
   all-files table) grows by 8 bytes per flag, by the formula section 19 derives from the entries and the saves.
   Whether the game keeps such a flag and still loads an older save is the first in-game question (item 3).
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

## Questions for Kareem

1. **The five in-game tests above, above all `din-fairy-hookshot`**: does the old save load, does the fairy give the
   Hookshot once and only heal afterwards, also after a reload, and does a magic gauge appear?
2. **`malon-song-heartpiece`**: after the play-along, is Epona's Song absent from the song list (the play-along's own
   add is skipped)?
3. **`chest-song-storms`**: does a chest give a song?

## Cross-track posts (thread `cs-r5`)

- 08:22: item 1 (e47caf5), the classes, the Serenade inside the Ice Cavern chest's event, GameDataList heads-up.
- 08:36: item 2 (acde59a), the `GameDataList` size formula commit (0cf3725) outside my files.
- 08:38: item 3 ready.
- 08:41: item actors for the gift items (6d754f6) in track C's `item_actors.toml`.
- 08:50: item 4 (a537bd5), the `allowed()` commit in track C's `fill.py` (6e0a7f8), its use (b44bb4e).
