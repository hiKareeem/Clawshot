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

## Handoff

Pending. No game launched, played output/save modified, merge or push.
