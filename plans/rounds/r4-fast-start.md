# Round 4, track C: fast start (cs4c)

Branch `r4/fast-start`, on main `e9f9cec`. Owns `src/clawshot/patch/gamedata.py`, `src/clawshot/data/fast_start.toml`,
`tests/test_fast_start*.py`, this file and section 14 of `plans/03-game-data.md`.

## What was built

| Item | Where | State |
|---|---|---|
| 1 What a new game sets and plays, which flags gate the opening scenes | `plans/03-game-data.md` section 14 | done |
| 2 The patch: initial values in `GameDataList`, one setting per skip, default the intro alone | `src/clawshot/data/fast_start.toml`, `src/clawshot/patch/gamedata.py`; tests `tests/test_fast_start.py`, `tests/test_fast_start_dump.py` | done (361b1d9) |
| 3 Test outputs for Kareem | `E:/OOTRemake/work/r4-fast-start/` (`intro/`, `all/`, `intro-removed/`, `README.md`, launchers) | done, not run in game |

## The plan and the data disagree on the intro (posted 19:53)

The roadmap assumed flags gate the opening. The intro is not gated by any flag: after New Game the title sequence
resets the game data and runs `Sequence/Opening.module` unconditionally, which requests event
`Opening_LoadingKokiriForest` (flow `OpeningEvent`, `EventTransition Dm_Kokiri_0000`: the opening movie) and reserves
`Opening_Introduction` (Navi wakes Link, `Dm_Kokiri_0030`). Changing initial values cannot skip either. And the movie
is one of only three events the game forbids skipping (`SkipSetting` `DisableSkip` in its event-setting component
list; the others are the title loop and the credits).

What I did, provisionally (no answer on the thread yet): the `intro` setting removes that `SkipSetting`, so the
player can skip the movie with the skip button. It is a small BYML edit of
`Event/EventSetting/EventSettingComponentList/Dm_Kokiri_0000.engine__event__EventSettingComponentList.bgyml` (512 ->
384 bytes; size-table entry 5,736), done by the same module, from the same data file (`skippable = [...]`). The
other skips are initial values in `GameDataList`, as specified. Removing the movie outright needs an event-flow
edit; track D's EVFL writer (`r4/evfl` 79c98f0, posted 20:02) makes that possible, and a scratch test of it is
output 2 below. Once that writer is on main, `intro` could start `OpeningEvent:Opening_LoadingKokiriForest` after the
movie instead (a few lines in `gamedata.py`; the scratch script shows the edit).

## Item 1: what a new game sets and plays

Full write-up in `plans/03-game-data.md` section 14. In short:

- **Sequence.** New Game: `NormalTitle` → `ConfirmationNewGame` → reset game data (ResetType 3, then 5) →
  `Opening` (start pouch and status: 3 hearts, no magic, small wallet, both tunics; load Kokiri Forest; play the
  movie; then the reserved boot event: time 6:00, challenge `Meet_DekuTree` `Step01`, Navi wakes Link, autosave).
- **Initial values** are each entry's `DefaultValue`; a new game resets the entries whose `ResetTypeValue` has bit
  3 (every per-slot story flag: 8 or 24) [inference from the values]. Placement flags (`Bool64bitKey`) have no
  default and start clear.
- **Challenge (quest) progress is game data**: Enum `Step_<challenge>` (all 45 rows of `RSDB/Challenge`; names
  found by hashing), values = the challenge's steps. Story triggers test it, some at exactly one step.
- **The saves.** Kareem's round 3 seed-3 run is a new game played to the Deku Tree with six autosaves; it gives
  the order of events and what each sets:

| Autosave (time) | Where | New since the previous save |
|---|---|---|
| slot_01 (19:27) | after the opening | `HavePlayedEvent` `Dm_Kokiri_0000`, `_0030`, `Opening_*`; Navi talked; `Meet_DekuTree` `Step01`; 39 challenges `Ready`; no placement flag |
| slot_03 (19:30) | Saria, village, sword | `Dm_Kokiri_0045`, `_0050`, `_0050_After_Near`, `_0060`; `KokiriForest_LinkHouseDoor_Open`; Saria talked; Kokiri Sword; 3 chests |
| slot_04 (19:31) | chests | Deku Nuts |
| slot_05 (19:33) | Mido | Deku Shield; `KokiriForest_Npc_Kokiri_Mido_Child_Blocker` false; `Meet_DekuTree` `Step03` |
| slot_00 (19:35) | Deku Tree talk, inside | `Dm_Kokiri_0070`, `_0075`; `KokiriForest_Meet_DekuTree_OpenDekuTreeMouth`; `Meet_DekuTree` `Complete`; `Get_StoneOfForest` `MeetBoss` |
| slot_02 (19:36) | in the dungeon | Deku Tree rooms |

  Kareem's main game (`save-backups/.../slot_01`) holds the later scenes (Kaepora in Hyrule Field, Zelda's
  courtyard, Impa's song), which identified their events.
- **Gates, per scene** (table in section 14): Saria's two scenes, Mido's block, the Deku Tree's talk and
  Kaepora's first two talks are gated by flags and challenge steps, so initial values skip them; Zelda's courtyard
  is gated by `Goto_HyruleCastle` = `Step04` but gives two checks (Zelda's Letter, Zelda's Lullaby), so skipping it
  is a product call (question below); Navi waking Link is sequence-driven and skippable already.

How it was found: scratch scripts and decoded data in `E:/OOTRemake/work/r4-fast-start/` (outside the repo):
`dump_ainb.py` decodes every `Logic/` and `Sequence/` AINB with dt-12345's `ainb` 0.2.16 (GPL-2.0, installed
unmodified in the scratch `.venv` there, rule 7; 1822 + 110 files, one failure: `Sequence/LoadBancImpl`), JSON in
`ainb_json/`; flows from round 1's `decoded/evfl_all.json`; text of a few cutscenes read from `Mals/USen` only to
tell the cutscenes apart (nothing of it copied anywhere). The interactive session's helpers (event references,
flag references, logic-module summaries, save diffs) are not kept as files; every fact above names its file and
event so it can be looked up again.

## Item 2: the patch

`src/clawshot/data/fast_start.toml`, one table per setting: `default`, `skips` (what a new game no longer plays),
`state` (what the skipped scenes would have left and how the setting gives it), `source`, optional `logic` (how it
changes what a seed's logic may assume), and the changes: `game_data` (flag name → initial value: true/false, a
number, or a step name for a challenge Enum) and `skippable` (events whose `SkipSetting` is removed).

| Setting | Default | Changes |
|---|---|---|
| `intro` | on | `Dm_Kokiri_0000` skippable |
| `saria` | off | `HavePlayedEvent` `Dm_Kokiri_0045`, `_0050`, `_0060`; `KokiriForest_LinkHouseDoor_Open`; `HaveTalked.Npc_Kokiri_Saria_Child` |
| `mido` | off | `KokiriForest_Npc_Kokiri_Mido_Child_Blocker` false (`logic`: Mido no longer needs sword and shield) |
| `deku_tree` | off | `HavePlayedEvent.Dm_Kokiri_0070`; `KokiriForest_Meet_DekuTree_OpenDekuTreeMouth`; `Step_Meet_DekuTree` `Complete`; `Step_Get_StoneOfForest` `GoInside` |
| `kaepora` | off | `HavePlayedEvent` `Dm_HrlField_0010`, `Dm_LostWood_0010`; `UI_IsFinishChallengeMenuOpenEvent`; `Step_Goto_HyruleCastle` `Step02` |

A setting sets only what the skipped trigger reads and the state the scene leaves that something else reads (each
flag was traced to its readers in flows, logic modules and placements); `HavePlayedEvent` of a scene part nobody
reads is left alone.

`clawshot.patch.gamedata`: `load()`, `build(romfs, names)` (the changed files, built, read back and checked against
the size table; nothing written), `write(romfs, out, names)` (`<out>` empty or absent, outside the romfs, as the
seed writer), and `python -m clawshot.patch.gamedata --romfs <dump> --out <dir> [--skip ...] [--list]`. Names are
looked up by murmur3 in the Bool, Int and Enum lists. It refuses: an unknown name or setting, a value of the wrong
type, a step the Enum lacks, a value that is already the game's (stale data), an entry a new game does not reset,
two settings that disagree, a component list another event shares or whose parent also disables skipping, a file
that outgrows its size-table entry. `GameDataList` keeps its size (values sit in their nodes: 1,462,888 bytes,
entry 1,463,176), so no size table is written.

## Item 3: test outputs (`E:/OOTRemake/work/r4-fast-start/`)

Each folder holds `romfs/` with only the changed files. `README.md` there says what to do and see; `Test -
<variant>.bat` starts a new game in `user-<variant>` (written, not run by me); `check_save.py <variant>` prints the
flags and quest steps afterwards (tried on a copy of a seed-3 save).

1. `intro` (the default, from 361b1d9): the opening movie starts and **can be skipped with the skip button**;
   Kokiri Forest loads, Navi wakes Link.
2. `intro-removed` (scratch, track D's writer): **no movie at all**; after loading, Kokiri Forest fades in and Navi
   wakes Link. `OpeningEvent:Opening_LoadingKokiriForest` starts at the wait-for-load switch (Event18), with a new
   1-frame wait looping back while the area is not loaded; the flow grows 17,504 → 17,744 bytes and its size-table
   entry is raised 17,776 → 18,032 (`rstb.required_size`), so the table is in the folder.
3. `all` (all five settings, from 361b1d9): the movie skippable; **no Saria scene at the house (door open); Mido not
   in the way; no Deku Tree talk, mouth open, no fog; no Kaepora talk in Hyrule Field or the Lost Woods.** Two
   in-game questions only a run answers, with the save check: whether the opening's own `Meet_DekuTree` `Step01`
   overwrites the initial `Complete`, and whether leaving the Deku Tree (`Goto_HyruleCastle` → `Step01`) overwrites
   the initial `Step02` (which would stop the Market → Zelda chain).

## Checks

| Command | Result |
|---|---|
| `uv run pytest tests/test_fast_start.py` | 21 passed: the shipped default is `intro` alone; settings-file errors; names and Enum steps resolved, two settings agreeing merge, disagreeing refused; wrong type, unknown step, unknown name, already-default value, entry not reset on New Game refused; on a synthetic romfs the written `GameDataList` (big-endian kept) differs from the original only in the chosen `DefaultValue`s with node types kept, the component list only lost `SkipSetting`, the romfs is unchanged; shared list, parent `DisableSkip`, already-skippable refused; nothing written when a file outgrows its entry; output folder rules |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_fast_start_dump.py -s` | 7 passed: each of the five settings applies to the dump alone; all together change exactly the 14 named entries' `DefaultValue` (every other entry, `MetaData` and byte order equal; same size 1,462,888) and the component list only by its `SkipSetting` (512 → 384 bytes); the default writes only the component list |
| `python -m clawshot.patch.gamedata --romfs ... --out .../all --skip intro saria mido deku_tree kaepora` | 2 files; the same 14 entries listed by a scratch diff (Bools as named; Enums `Step_Meet_DekuTree` `Complete`, `Step_Get_StoneOfForest` `GoInside`, `Step_Goto_HyruleCastle` `Step02`) |
| the four gates | end of this file |

## Provisional choices (for review)

1. **The intro is made skippable, not removed** (above): the only data path on main. `gamedata.py` therefore also
   edits an event-setting file, not only `GameDataList`; both come from `fast_start.toml`.
2. **Minimal flags**: a setting sets what the trigger reads and what other readers need, not every flag the
   vanilla scene sets.
3. **Strict refusals**, including "already the game's value": the data is for build `e0f3ccfa` and should fail
   loudly on another.
4. **Not wired into `python -m clawshot`** (`__main__.py` and the seed writer are no track's this round). `build()`
   returns the files so the seed writer can add them; no seed writes `GameDataList` or event settings, so they
   cannot collide. `mido`'s `logic` note must become a world setting at that point; until then a seed must not be
   played with `mido` (its logic would still ask for the sword and shield, which is only stricter, so a seed stays
   beatable [inference]).
5. `kaepora` sets `Step_Goto_HyruleCastle` to `Step02` from the start, because the Market arrival fires only at
   exactly `Step02`; side effect: the Kokiri in front of the shop no longer stops Link.

## Questions for Kareem

1. **Intro: is "skippable by button" enough as the default, or should a new game drop the movie entirely (test 2;
   needs track D's event-flow writer on main)?**
2. **Zelda's courtyard: should a fast start skip it? It gives Zelda's Letter and leads to Impa teaching Zelda's
   Lullaby, both checks; OoT Randomizer's "skip child Zelda" starts with the letter and treats the song check as
   collected. Skipping it here needs items given at the start (not a flag), so it is not offered yet.**
3. **Mido: offer it (it changes the logic like OoT Randomizer's open Deku Tree), and should it go with opening the
   forest exit too?**
4. **Navi waking Link stays (it is sequence-driven and already skippable); is that fine?**

## Cross-track posts (thread `cs-r4`)

- 19:53: the intro is not flag-gated; the three data paths; my provisional choice (a).

## Left for later

- The in-game results of the three outputs, above all the two quest-step questions of `all`.
- Removing the intro outright once EVFL writing is on main (and, if Kareem wants it, Zelda's courtyard with start
  items).
- Wiring fast start into `python -m clawshot` and `mido` into the world's settings.
- `Pouch_Amiibo`, which the skipped Hyrule Field talk would give: what it unlocks is not traced.

## Gates (before the handoff)

On 361b1d9 plus this file and section 14 (main `e9f9cec`):

```
uv run ruff format --check                                  68 files already formatted
uv run ruff check                                           All checks passed!
uv run pytest                                               189 passed, 25 skipped
OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump      24 passed, 190 deselected
```
