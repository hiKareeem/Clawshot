# Round 5, track D: gifts through the flows (cs5d)

Branch `r5/gifts`, from main `91b3ed5`, rebased on `cd592e3`. Owns `src/clawshot/patch/gifts.py` (new),
`src/clawshot/census/gifts.py`, `src/clawshot/formats/evfl.py`, `tests/test_gift*.py`, `tests/test_evfl*.py`, this file
and section 19 of `plans/03-game-data.md`. Scratch scripts and decoded data: `E:/OOTRemake/work/r5-gifts/` (outside the
repo).

| Item | Where | Commit |
|---|---|---|
| 1 readers of each gift's item, flags to use, classes | `plans/03-game-data.md` section 19, this file | this file's first commit |

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

## Provisional choices (for review)

1. **New `GameDataList` flags for "given"** (Great Fairies, windmill), named `Clawshot.Gift.<flow>.<event>` after the
   check's first step. Existing flags were looked for first: `HavePlayedEvent` of the fountain is set on a refusal too,
   `Meet_GreatFairy_01` defaults to true and Din's fairy has no flag of its own; only the windmill had a usable one
   (`HavePlayedEvent.Dm_MelodyGet_Storm`), and one mechanism for all is simpler to test. The `MetaData` file-0 table
   offset and size grow by 8 bytes per flag (the formula in section 19 matches the saves). Whether the game keeps a flag
   it did not ship with is the first in-game question (item 3, the Din output).
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

(none yet)

## Cross-track posts (thread `cs-r5`)

(none yet)
