# Round 13: dungeon items (cs13c)

Branch `r13/dungeon-items`; based on `30ba5c9` (0.2.0, unpublished).
No version bump, game start, merge, push, hc/herdr command or game-folder write.
Research/output: `E:/OOTRemake/work/rounds/r13/dungeon-items-cs13c`.

## Played defect and urgent audit

Kareem, 2026-11-12 11:44, Hookshot 2.1.0: Chest-only own-dungeon seed7,
Deku Tree Basement Chest gives Map (Deku Tree) text/animation but not the pause map.
Accepted ground truth: `IsGet.Item_Dungeon_Map` changes false→true while
`DungeonInfo.InsideTheDekuTree.IsGetMap` remains false. The seed's Slingshot Chest
holds Compass (Deku Tree), and its native Map Chest holds Deku Stick (1).
Read the actual staged spoiler; no played output or save was altered.

Native dump diagnostic `inspect_flows.py` reads the supported game through our
EVFL/zstd readers. Big chest `Dm_SY_Treasurebox` indices21–24 explicitly invoke
`EventGetDungeonMap`, `EventGetDungeonCompass`, `EventGetDungeonBossKey`, and
`EventGetDungeonSmallKey`. Boss event23 (`Event27`) continues to UI boss-key
indicator event82; that display is not itself saved ownership. Small chest
`Dm_SY_TreasureboxSmall` has no corresponding boss/map/compass action: its grant
calls `GetPouchContent`. The 11:50 cs-r13 post immediately reported this distinction.
At11:50 the small-chest boss-key loss was labelled inference pending its native
pouch branch. At12:06 the native-handler trace settled the branch statically:
small key `PouchSpecialDeal=SmallKey`; boss/map/compass `NotPushToPouch`.
The positive pouch path `0x033ac518..0x033ac530` invokes `0x03283160` only
for small keys. Big boss action `0x028cae10` invokes `0x032830e0`;
map/compass invoke `0x03282fe0`/`0x03283060`. The shared live dungeon is
resolved through `0x00b2af20`/`0x00b2afc0`. Source: r11 native trace and
PouchActorInfo, independently checked by the native-audit slice; no code copied.
Small-chest boss/map/compass loss is therefore a static native-code conclusion,
not yet a played same-dungeon boss result. The identical map path is played.

### Per-opening/family gate (before the restricted repair)

| Native opening | Small key | Boss key | Map | Compass |
|---|---|---|---|---|
| Small (`A_01`, `A_06`, GlassTruth; supported NoBake variants) | Present through `PouchSpecialDeal=SmallKey`; three native fields and counter demo, played Forest tree key | Missing: `NotPushToPouch`, no explicit dungeon action | Missing: same native branch; played Basement Chest | Missing: same native branch |
| Big (`A_02`, `A_03`; NoBake) | Present, Event30/index24 | Present, Event27/index23 | Present, Event23/index21 | Present, Event26/index22 |
| Native acquisition wrappers | Transition to the corresponding opening; not a separate item grant | Same | Same | Same |

Claude's 11:56 scope condition: repair only missing grant pairs. Do not add
redundant grants to own small-key pickups or own big-chest pickups. The initial
generalized compiler prototype is being narrowed before acceptance; no redundant
grant is intended for delivery. Presentation-only stale-comment removal is distinct
from grant repair and must not replace story progress.

## Priority runtime diagnosis — staged, not played by cs13c

Claude superseded sweep priority with a3-minute unpatched boss-key check.
Current main was explicitly identified as `30ba5c98826bb3ccc49e96b9b4ed9665f124fcbe`;
the scratch builder imports **that checkout**, not this repair worktree.
Initial pins-only public `make_seed` failed10attempts with printed
`return kit: no adult return-kit destination for ['Boss Key (Forest Temple)']`.
The tree is the only pre-door key check; its next exit requires one key.
Claude then explicitly authorized a diagnostic-only unbeatability exception.

Final launcher, posted ready12:07:
`E:/OOTRemake/work/r13-dungeon-items/ingame/TEST ONLY - not beatable - boss key tree unfixed.bat`.
Same-folder `BOSS-UNFIXED-CHECKLIST.md`, **3minutes**, one real mod/fresh user.
Adult checkpoint thumbnail: **Temple of Time, adult Link beside Sheik on the
pedestal** (`2026-11-09_1022-main-adult-first`, source manual01).
Original source read: adult, tree closed, boss=false, remaining0/total0/once=false.

Exact pin: Forest boss key→First Room/tree chest1171460703078800858.
Existing input `excluded_items` pins it; no post-fill placements or output edits.
Input-only relaxation: goal=True, age_return_guarantee=false, Forest
Lobby→Central Area rule=True instead of one small key. The actual game door is
**unchanged and locked**. Never reuse this diagnostic seed. A Settings goal
argument was rejected (goals require area slices); the printed cause was fixed
by setting the test spec's goal instead. No unchanged failure was rerun.

Public `make_seed`/`write_seed`:82resources/29spheres. Independent emitted-byte
readback: exact A_01 tree actor/BossKey/no GetEventName; native small-chest and
pouch flows are **not** replaced. Actual cmd `CLAWSHOT_DRY_RUN=1`:exit0,
current-template ASCII/CRLF, correct bin/user/HOS_MODS, exactly four copied save
files byte-equal to the source, no game log/start. Builder/proofs live outside
the repo at `work/r13-dungeon-items`. Mod digest:
`b06d8f9c1c2baa6424c5d4886fbfd6e8bf6249b5d7f81bcf1ea6ab3cc137070b`.
Claude boot-checks and reads after-pickup saves; no runtime result is fabricated.
The optional next small-key chest was omitted because this checkpoint has no
entry key; it would not be a3-minute route.

### Unfixed runtime result: BUG CONFIRMED

Kareem12:18–12:20, accepted via Claude as ground truth; not rerun by cs13c.
Snapshots: `save-backups/2026-11-12_121*-r13-bosstree-1..3`.
After the tree-chest pickup, `IsGet.Item_Dungeon_BossKey` false→true but
`DungeonInfo.ForestTemple.IsGetBossKey` remains **false**, including saves
12:19:41 and12:19:45. Small-key remaining/total/first stay0/0/false; adult,
no crash. Claude confirmed the Forest Banc loaded from this diagnostic mod.
This directly proves the same-dungeon small-chest boss-key loss, beyond the
earlier map report and the seed11 off-area boss-key indicator-without-save result.

## Fixed check: one combined12–15minute packet

Staged and posted ready12:27 under `work/r13-dungeon-items/ingame`:

- `TEST ONLY - not beatable - fixed adult.bat`: same original adult checkpoint
  and same tree chest, now repaired. Expected boss=false→true; keys unchanged;
  Save and Quit/Continue, chest stays open; about3minutes.
- `TEST ONLY - not beatable - fixed child.bat`: original1630 child checkpoint,
  whose exact extracted thumbnail is young Link with a red rupee above the
  open Kokiri Sword chest. Both Deku side chests and the native Slingshot chest
  were read closed; Deku map/compass false. Map is in the Slingshot-room small
  side chest13027331340815880287; compass in the Compass-room small side
  chest11368028582977069031. Native big Slingshot821372075822700622 is pinned
  unchanged so the short route needs no inventory cheat. About8–10minutes+reload.

One checklist: `FIXED-DUNGEON-ITEMS-CHECKLIST.md`, native exact text, menu
boxes/markers, saved flags, no duplicate after reload and no unrelated Navi line.
Two templates/profiles are necessary: the adult source already owns Deku's map
and compass, while the child source cannot test Forest. Both load **identical**
public-writer output,88resources/25spheres. Claude explicitly authorized the same
test-only unbeatability relaxation for this fixed check; it is recorded with
all four pre-fill pins in `fixed-staging-proof.json`. The actual door is untouched.

`verify_fixed_check.py`: actual emitted three source-bound graphs each write
only the intended DungeonInfo Bool, no parallel native/current-dungeon grant;
native get-message/caption IDs and both registry registrations present.
Both exact-template ASCII/CRLF cmd dry runs passed, four source-save hashes
matched per profile, no game start. Two mod copies' digest:
`8c1ddd5aa8fd88ed6f9707ad056400dd00c92d4c21335789cc663912fd8e47ef`.
Original saves and the played unfixed output/user remain frozen.
Fixed startup/gameplay acceptance is pending Claude/Kareem, not inferred.




## Implementation and verification

Implemented using the existing registered source-bound compiler, in one pass
for named keys and missing dungeon-item grants. Do not append two independent
compiler passes to GetPouchContent: they would collide on helper/index ownership.
`patch/__init__.py` invokes this pass in both modes; bags must compose afterwards.
The integration call is kept in its own commit. The reverse-order regression
mutates the original pouch grant to a literal bag actor and verifies compilation
refuses rather than overwrites it, for both sizes and named/own/map grants.

The plan repairs only small-chest map/compass/boss grants and physical off-area
targets. Native own small-key and own big-chest handlers remain native. Ganon's
separate logic type `GanonBossKey` normalizes to the same BossKey saved field.
Native unchanged placements are skipped before binding work. Per-family tests
execute serialized synthetic graphs and verify exact fields, no cross-credit,
native messages, story state, counter transitions and unchanged native controls.

`audit_wrappers.py` walked all native source wrappers, including local subflows.
Ten item-only reactions have no game-data/quest writes (the Lens has item-only
Navi dialogue rather than a balloon); changed rewards remove their GetEventName.
Ruto09 and IceArrow retain source-bound clones with only acquisition balloon475
or478 removed. Their room/quest writes and the separate Nabooru story reaction
remain. Obsolete source-ID/wording-only wrapper tests were removed, not re-pinned;
behavioral story-preservation and native inverse tests replace that assumption.

Focused run:129passed/12.27s, plus the separate Ganon normalization regression
1passed/0.17s. Full `ruff format --check`:317files; `ruff check`:PASS.
Initial two new native-row tests incorrectly assumed additions were row prefixes;
the failure payload showed the writer's normal sorted merge. Identity-filtered
native-row invariants fixed those harness errors; one cause-directed rerun passed.

Own copied fixture builder completed before gates:1244working-set files,
1209base/48update/1196same/**0missing**, at
`work/rounds/r13/dump-dungeon-items`. Original pr1 builder/dump untouched.
Full four-gate supervisor queued without a deadline under r13/gate.lock,
with explicit ROMFS/NUP/new OOT_DUMP and start-time worker1/3 selection.
Logs/results: `work/rounds/r13/dungeon-items-cs13c/gates-final`.
No incomplete or skipped native coverage is counted as a pass.

## Decisions proposed by cs13c

- Separate small-chest pouch delivery from big-chest explicit dungeon delivery;
  do not equate an item-get animation, generic IsGet bit, or HUD icon with ownership.
- Reuse registered source-bound event cloning rather than add per-chest map logic.
  No new chest-kind opening contract is declared played by this work.
