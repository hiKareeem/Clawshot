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

Proposed implementation (cs12c, as requested): retain logical own-dungeon membership
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

Pending focused regressions, two locked 50-seed sweeps, regenerated seed 11 and all
four full gate commands. Initial `tasklist /FI "IMAGENAME eq hookshot.exe"`: no game
process. All pytest runs will conservatively use `CLAWSHOT_WORKERS=1`.

## Handoff

Pending. No game launched, played output/save modified, merge or push.
