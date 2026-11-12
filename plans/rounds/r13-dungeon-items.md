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
- **Superseded child donor:** the initially staged `fixed child.bat` used1630.
  Although its targets were closed, the subsequent route audit found it lacked
  the sword required to pass the Slingshot-room Scrub; r12 had needed an explicit
  sword-cheat exception. At12:30 cs13c immediately posted HOLD for that phase.
  No such cheat is permitted here. The old launcher was moved into
  `ingame/superseded/` at Claude's request; its mod/user remain untouched.
- **Current child:** `TEST ONLY - not beatable - fixed child geared.bat`,
  posted ready12:32 (exact watcher paths repeated12:34). New source:
  `2026-11-12_114031-r13-faststart-native-8` account/manual-auto04. Actual saved
  sword=true, shield=true, child=true, Deku map/compass=false, all three targets
  closed. Its directly decoded thumbnail shows Link with sword and wooden shield
  facing Mido in the forest tunnel. No inventory/flag cheat or resource change.
  Native Slingshot stays at its big chest821372075822700622, Map at the
  Slingshot-room small side13027331340815880287, Compass at the Compass-room
  crawl-vent side11368028582977069031. About8–10minutes+reload.

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
Runtime results for this literal-Bool candidate are recorded below; do not imply a boss-icon or door pass.
`geared-child-verification.json` supersedes only the initial child donor/launcher.
Its mod is byte-identical to the adult's digest above; all four new copied save
files match the chosen pre-pickup backup, exact-template ASCII/CRLF and actual
cmd dry run pass. Adult output/user and the earlier child output/user were not reset.

### Fixed adult: saved ownership and persistence PASS; icon gap

Kareem12:31–12:34, accepted via Claude; not rerun. Snapshots:
`save-backups/2026-11-12_123*-r13-fixed-adult-1..4`.
Forest `IsGetBossKey` false→true (12:33:10 and12:33:14), all other dungeon
fields across the12 compared dungeons unchanged; Forest keys0/0/false.
Adult, no crash. Mod loading proof supplied for `Dm_SY_Treasurebox`,
`Dm_SY_TreasureboxSmall`, `EventSetting`, `GameAnalyzedEventInfo`.
Kareem confirmed normal boss-key text, no Navi comment, chest stayed open after
reload. **No boss-key icon appeared on the HUD or pause map; door unplayed.**
Generic `IsGet.Item_Dungeon_BossKey` stayed false (unfixed run set it true).

Claude requested read-only icon-reader/native-action investigation before any
code change. Forest map=false in this checkpoint; whether map ownership/view
gates the boss display is an inference, not an excuse to claim UI acceptance.
`action_scope.py` confirms existing unscoped GameSystemActor and UISystemActor
in Small/Pouch have the same native binding parameters as Big. The shared
GameSystemActor EventUniqueAin contains all three native EventGetDungeon actions.
Appending these already-registered operations to an existing small-chest actor
and reusing Big's boss-display action is feasible statically; no new actor or
opening contract is needed. Exact icon-reader trace remains pending.

### Fixed child: map and compass menu/saved ownership PASS

Kareem12:38–12:42, accepted via Claude; not rerun.
Snapshots: `save-backups/2026-11-12_12*-r13-fixed-child-geared-*`.
Deku `IsGetMap` false→true at12:40:39, `IsGetCompass` false→true at12:42:05;
nothing else changed in any compared dungeon. Native big Slingshot collected,
child, no crash. Kareem: **“Got the map and compass, no problems.”**
Claude's supplied screenshot shows full3F outline, boss marker onB2, a chest
marker, and both compass/map boxes filled. This directly proves pause-map
ownership/rendering reads the literal DungeonInfo map/compass Bools correctly.
It does not prove the boss-key icon uses the same predicate or that the boss
door was exercised. Fixed map/compass re-entry/reload beyond this report is not
invented.

### Native boss action/indicator candidate — approved and staged

Claude approved the boss-only native-action design after the read-only report:
reuse the small flow's existing unscoped GameSystemActor and UISystemActor.
Map/compass stay on the literal-Bool implementation Kareem just played; no replay
or changed map/compass action is implied. No new actor or opening contract.
The same-dungeon small-chest boss helper calls native
`EventGetDungeonBossKey{IsWaitEnd:true}`, then
`EventTriggerSetDisplayBossKey{IsDisplayBossKey:true}`, then the native50-frame
display wait before the existing pickup-window continuation. Parameterized
off-area literals remain separate; native big grants and own small keys stay native.

`IsDisplayBossKey` is pickup presentation, not proof of saved ownership.
The generic IsGet flag is dynamically read by PouchContent's
`QueryGetNonStructGameDataStruct(IsGet)` + actor-name Bool lookup; that does not
prove a pause-map consumer. Native DungeonIsGetBossKey queries per-dungeon
ownership. The exact boss pause-box predicate remains unisolated; Forest map=false
is a possible gate, explicitly **inference**, not a claimed UI pass.
Child map/compass menu success is direct ground truth; it must not be generalized
to the boss-specific pause box.

New launcher posted ready13:10:
`work/r13-dungeon-items/ingame/TEST ONLY - not beatable - native boss.bat`.
Same-folder `NATIVE-BOSS-CHECKLIST.md`; fresh user
`user-TEST ONLY - not beatable - native boss`. Original adult-first save,
Temple of Time/adult Link beside Sheik thumbnail; tree closed, boss key/map
false, keys0/0/false, boss lock false. All four donor files byte-equal;
current central-template ASCII/CRLF launcher with only placeholders and the
separately approved movement-only NOCLIP instructions changed; actual cmd
dry run exit0. No game started by cs13c; all played users/mods frozen.

Public `make_seed`/`write_seed`:90resources/29spheres; exact pre-fill pin
Forest Boss Key→courtyard tree1171460703078800858, existing exclusions only.
Same previously authorized diagnostic-only model relaxation: goal=True,
return guarantee=false, Forest lobby exit=True; no real game door/flag changes.
Serialized readback verifies the native three-action helper, no new actors,
and unchanged original small-flow events/entries.
Digest `0df27b00116d47f4ec3552149e0ced219e840d5d9e3a4ce4b3bb3a17f286b6c2`.
Proofs: `native-boss-staging-proof.json`, `native-boss-profile-proof.json`
under `work/r13-dungeon-items`. Runtime acceptance follows below.

Claude additionally authorized **NOCLIP for movement only** in this TEST ONLY
copy, superseding the earlier no-short-legal-route handoff. Checklist now requires
pickup Save/Continue first, then movement through the locked front entrance and
down the central elevator shaft to the **B2F** boss door; disable NOCLIP on its
approach side and open **normally**, never noclip through the boss door. Save/Continue
again and record key consumption and lock persistence; do not fight Phantom Ganon.
Native MapParam room27 and boss room29 both have Floor[-2], proving B2F.
Door controller `Obj_ForestTemple_SwitchShutter_A_04` Hash11429592239509371885
links boss lock `Obj_DoorChainLock_A_02` Hash1742952115574306870.
Exact saved release field:
`IsChainLockDoorOpen.11429592239509371885` = **false** in the donor.
The lock hash itself has no saved member (`None`); DoorChainLock.root uses
`QueryDoorChainLockGetControllerInstanceId` under `IsChainLockDoorOpen`.
Lock position approximately(-0.04,59.53,-40.86), elevator bottom(0,59.73,-3.5);
approach from positiveZ. No door or ownership success is inferred from these data.

### Native boss candidate: played credit, indicator and normal boss-door PASS

Kareem approximately13:17–13:20, accepted via Claude; not replayed.
Snapshots `save-backups/2026-11-12_13*-r13-native-boss-*`.
Boss-key pickup counter/indicator increments; boss door opens **normally** with
the key. Link auto-walks through, then the native boss-room seal locks behind him.
No crash; Claude confirmed all named flows loaded from this mod.
This accepts small-chest boss-key credit + indicator + normal boss-door opening,
alongside the earlier played map/compass acceptance.

All supplied saves are **before the door**: Forest `IsGetBossKey=true`,
generic `IsGet.Item_Dungeon_BossKey=false`, Forest small keys0/0, and
`IsChainLockDoorOpen.11429592239509371885=false`.
**Post-door key consumption and door reload persistence remain unverified**:
the arena prevents saving. Do not turn the pre-door false flag into a failed-door
claim, or claim a post-door save that does not exist. No additional fight/replay requested.

Claude's chest-reader discrepancy was resolved by printing both native save
representations, not replaying the game. Correct named Bool
`Save.flag("IsTreasureBoxOpen.1171460703078800858")` is **true** in every
updated save: auto00 from13:17:48, manual01 at13:19:00, manual02 at13:19:11.
The unchanged donor manual01 is still false in backups1–3; manual01 becomes
true in backups4–5. `Save.is_set(1171460703078800858)` instead reads the
separate section32/Bool64bitKey and stays false; it is not this chest-open flag.
Native schema confirms the named struct member hash1765082576 maps to Bool
value hash2342141199. No save edits. Full payload:
`work/r13-dungeon-items/native-boss-chest-flags.json`.



## Historical incidence — completed100+100

Recommended seeds **1–100** from each source:
0.1.2 tag `0af23642`, 0.2.0 main `30ba5c98`.
Release source zip contents were checked against their pinned source trees;
recipe setup uses each version's own Gift setup/generate/make_plan pipeline.
Published0.1.1 seed11 (`1C37F227BEDE`) and0.1.2 seed15 (`0EF74161E8AF`)
were reproduced with zero placements/plan differences. Candidate12/14/16 and
0.2.0 candidates20–23 were additional zero-difference controls.
0.1.2/0.2.0 placements are identical for all100 seeds; all200 completed with
zero failures, no reroll inflation. Counts below are **per version**, not pooled.

| Family | Items | Native | Moved | Moved→small | Moved→big | Seeds with a move |
|---|---:|---:|---:|---:|---:|---:|
|Boss key, including Ganon|600|75|525|425|100|100/100|
|Small key|3700|1779|1921|1203|718|100/100|
|Map|1000|115|885|536|349|100/100|
|Compass|1000|130|870|587|283|100/100|

Every seed in both versions has at least one **non-Ganon boss key** in a small
chest; this now matches the played loss path. Every seed also puts at least one
map and compass into a small chest. No non-chest placement, physical Banc
mismatch or native target mismatch occurred in these two own-dungeon samples.
Native means the same generic family actor stayed in its native chest.

Each native boss/map/compass chest is big; each native small-key chest is small.
Of100 moved boss keys in big chests,95 keep a source wrapper and5 use the plain
big opening. Those big paths invoke the explicit dungeon action; all425 small
boss-key destinations have no override and use the pouch-only opening.

| Recipe | Boss moved/small | Small key moved/small | Map moved/small | Compass moved/small |
|---|---:|---:|---:|---:|
|Published11,0.1.1|6/3|21/14|6/2|10/4|
|Published15,0.1.2|6/6|21/15|9/4|8/5|
|Regenerated11,0.1.2 or0.2.0|6/4|21/14|9/5|9/4|
|Regenerated15,0.1.2 or0.2.0|6/6|21/15|9/4|8/5|

Published11 additionally loses the Spirit boss key in its big outdoor Mirror
Shield hand chest, and a Spirit small key in the Silver Gauntlets hand chest.
The off-area boss indicator-without-save was already played in r12. Published15
has all six boss keys in small chests. Regenerated11/15 have no Banc mismatches.
These are generation/emission counts, not200 played-through games.

Measurement held r13/gate.lock12:10:11–12:39:46 with one worker. Source/scripts,
raw rows and exact reproduction proof remain outside the repo in this track's
scratch: `summary.json`, `verify.json`, `published.json`, `count_moves.py`,
`sweep2.sh`, `community-*.json`, `recommended-*.json`.





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
Full four-gate supervisor queued with explicit ROMFS/NUP/new OOT_DUMP and
start-time worker1/3 selection, no deadline. At12:38 it was still waiting with
no lock acquired; cs13c cancelled only that own waiter for the requested read-only
boss-icon investigation. No child supervisor remained and no foreign lock was
removed. The empty `gates-final` directory is **not a gate result**. Requeue
after the native-action decision; no partial or skipped coverage counts as PASS.

After native boss approval, focused changed-path run: **133passed/12.86s**,
`ruff check` PASS. Source-string/name/trace-end assumptions are not acceptance;
regressions exercise native boss ownership once, display armed before pickup,
source story-state preservation, no literal parallel credit and no cross-dungeon
credit when literal/native bindings coexist.
Final serialized four-gate runner requeued at13:07, position3 after cs13b,
using the same own OOT_DUMP, start-time worker selection and no deadline.
Results go to `gates-native-boss/results.json`; pending is not PASS.


## Decisions proposed by cs13c

- Separate small-chest pouch delivery from big-chest explicit dungeon delivery;
  do not equate an item-get animation, generic IsGet bit, or HUD icon with ownership.
- Reuse registered source-bound event cloning rather than add per-chest map logic.
  No new chest-kind opening contract is declared played by this work.
