# Round 12: physical dungeon-area constraints (cs12c)

Base: main `9f86b3a`; branch `r12/areas`. Scope requested by Kareem, 2026-11-11.

## Incident and decision

Kareem played published 0.1.1 community seed 11 at 12:41–12:47 on Hookshot 2.1.0.
Its Spirit Silver Gauntlets and Mirror Shield chests contained Spirit small/boss keys.
Both actors live in `Banc/DesertColossus`, not `Banc/SpiritTemple`. The reported
post-Save/Quit save leaves Spirit at 0/0/false with no boss key, while both chests
are open. This is authoritative played evidence; no game or save-check rerun here.
Round 11's played overworld small-key loss and section 44's handler trace explain
why generic actors cannot be placed by logical dungeon membership alone.
Incident artifacts (all read-only): `E:/OOTRemake/work/r11-release/candidates/seed-11/`;
checker `E:/OOTRemake/work/r12-spirit-hands/check_saves.py`; saves
`E:/OOTRemake/work/save-backups/2026-11-11_124548-r12-spirit-hands-2/`.

Implemented (cs12c, as requested): retain logical own-dungeon membership
and additionally require the location's physical Banc area to match its dungeon
region's own area, inside the fill predicate shared by restrictive fill and safe
swaps. No post-fill repair; every returned seed still passes the beatability oracle.
`dungeon_items` currently accepts only `own_dungeon` and `anywhere`; there is no
`vanilla` mode to modify. Unshuffled checks retain their actual vanilla items.
No version/lockfile change; Claude bumps the version at merge because output changes.

## Audit

In progress: exhaustive world/census join, including boss rooms, Castle/Tower,
Training Ground and Fortress/Hideout. Reproducers and decoded resources live only
under `E:/OOTRemake/work/r12-dungeon-areas-cs12c/`.

## Silver Gauntlets story event (note only)

Kareem observed the child cutscene while adult, including child-to-adult morphing.
Research is facts-only; no cutscene or story patch belongs to this track.

**This is not known to be cosmetic-only:** the retained chest wrapper requests a
Spirit quest step without checking Link's age. Confidence is high for the explicit
flow writes below, but whether a late request can rewind an already-later quest
step is unknown: the native challenge action's ordering semantics were not proved.
No regression or adult Nabooru break is claimed from the visual morph alone.

Existing, mutually corroborating sources: `plans/03-game-data.md` section 18
(lines 1035–1044), `plans/rounds/r5-seeds.md` (chest event audit), and
`src/clawshot/patch/chest_events.toml` entry `SageOfSpirit_NaboorIsTakenAway`.
Static cross-check: original round-1 decoded `SageOfSpirit` flow, build `e0f3ccfa`,
under `E:/OOTRemake/work/r1-research/decoded/evfl_all.json`.

| Flow/node | Effect relevant to story |
|---|---|
| `SageOfSpirit:SageOfSpirit_NaboorIsTakenAway`, `Event64` | Calls `Dm_SY_Treasurebox`, which grants the current `ContentName`, not a second Silver Gauntlets grant. |
| `SageOfSpirit/Event1` | Plays `Dm_DesertColossus_0030`, Nabooru taken away. |
| `SageOfSpirit/Event190`, `Event322` | Clears `HavePlayedEvent.NaviTips_Gauntlet_01` and `HavePlayedEvent.NaviTips_Gauntlet_03`. |
| `NaviChat:NaviChat_Serious` | Sets `NaviChat_Serious_Time=true` during the subsequent Navi talk. |
| `SageOfSpirit/Event21` | Calls `EventExecuteProgressChallengeStep` for `SageOfSpirit`, `Step07`, with `IsIgnoreCompletedChallenge=true`; follows with quest progress UI. |

An adult opening can therefore invoke the same Spirit-story progression request as
a child opening (high confidence: no age branch in this wrapper). Later adult
Nabooru progression has separate `Step08` / `Step08_01` writers; completing Spirit
has its own later writers. Whether the Step07 request skips prerequisite staging or
is ignored after a later step requires the challenge handler/AINB or a controlled
play check; it is not resolved by the EVFL action name “Progress”.

Direct dump/index-faithful wrapper and timeline inspection is queued under the
gate lock to supplement the older decode, without changing any event.

## Verification

- Before fix: `CLAWSHOT_WORKERS=1 uv run pytest tests/test_generate_dungeon_areas.py -x -q`:
  failed on `SmallKey`, printing `Outside.area='OverworldArea'` while its logical
  region belonged to Temple (`area='TempleArea'`); old `allowed()` returned true.
- After the physical-area change: `CLAWSHOT_WORKERS=1 uv run pytest tests/test_generate_dungeon_areas.py -q`:
  **7 passed** (5.27 s). Synthetic outside checks cover small keys, boss keys, maps
  and compasses, an inside positive control, synthetic anywhere compatibility,
  actual Spirit hand restrictions and a beatable seed 11 using defaults.
- `_in_dungeon_area()` is the only new fill helper. `allowed()` shares it across
  restrictive fill, return-kit placement, fill-time safe swaps and restricted filler.
  Existing area-less synthetic worlds keep their logical policy (`None == None`).
- `docs/settings.md`: one plain sentence explaining the hand-chest exclusion;
  no READ ME FIRST, project version, lockfile or settings schema changes.
- Initial `tasklist /FI "IMAGENAME eq hookshot.exe"`: no game process. All pytest
  runs conservatively use `CLAWSHOT_WORKERS=1`.
- Full gates and both 50-seed sweeps queued through the shared gate lock; initial
  `mkdir` and the required 60-second retry both reported an existing lock.

### Community seed 11 output smoke

Replayed the full string from `work/r11-release/seed11-share.txt` through the CLI's
existing Gift setup and `make_seed`/`write_seed`. New output only:
`E:/OOTRemake/work/r12-dungeon-areas-cs12c/seed11-fixed/`.

| Hand chest | New item | Written actor |
|---|---|---|
| Silver Gauntlets | Rupees (20) | `TBox_Rupee_Red` |
| Mirror Shield | Bombs (5) | `Item_BombBundle_Small` |

`uv run python E:/OOTRemake/work/r12-dungeon-areas-cs12c/sweep.py seed11` completed
in 66.28 s; the generator's beatability oracle passed before writing.
`tree_digest` (SHA-256, paths and all file contents including spoiler/play note):
`04edec972126b9b9ba0f67e1cadb001f191813118ce0fb47ece88a9677a94f91`
(share hash `04EDEC972126`).

Independent read-back smoke decoded all four written chest copies (child/adult):
both items match the plan, neither is generic dungeon loot, and the unchanged
story overrides remain `SageOfSpirit_NaboorIsTakenAway` / `SageOfSpirit_GetShield`.
The written spoiler has no dungeon-item physical-area violations. This is file
and logic proof, not a new in-game test.

Scratch failure diagnosed before retry: the shared string has expanded
`Boss/Cutscene/NPC/Song` shuffle types, not the `Gift` alias. My first replay driver
checked only that alias and omitted Gift preparation, causing `Buy Magic Bean`
to have zero allowed destinations. Printed full settings and the false condition,
then changed the driver to the existing CLI's expanded-type condition; one corrected
run succeeded. No production change was needed for this scratch-only mistake.

### Player follow-up (not run by the agent)

The new seed output is not a repair for an existing seed 11 save: placements change
and the opened hand chests are already consumed. Do not replace the published
candidate or point a played save at this changed recipe.

**Kareem: on an isolated new playthrough generated from the merged build, confirm
the hand rewards match its spoiler, remain collected after Save and Quit, and the
seed finishes; record the Hookshot `mods: Banc/DesertColossus/... <- ...` loading
line.** The pre-merge scratch output above gives 20 rupees / 5 bombs, not keys.
Use only Teleport/clock cheats if needed; do not edit inventory/story/age flags.
Native own-dungeon key persistence already has the round-11 Deku/Fire controls;
this track adds placement safety, not a new grant implementation.

## Handoff

Pending. No game launched, played output/save modified, merge or push.
