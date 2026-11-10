# Round 10, Track D: pots and loose rupees (cs10d)

Branch `r10/pots`. Required AGENTS/README, plans00–04, decisions and all round8/9 reports read;
Round10's opening/shared-file policy applies. Dump build `e0f3ccfa`, game directory and save
backups are read-only. No unlicensed randomizer archive/code, NX2navi code/docs, game, batch,
window, Hookshot build or terminal-control command accessed/run. No dependency changes,
merge, push, stash or unauthorized rebase. Scratch: `E:/OOTRemake/work/r10-pots-cs10d/`.
Hookshot was already running; all local work uses one process/worker. Full gates take the
shared `E:/OOTRemake/work/rounds/r10/gate.lock` directory and release it on every exit.

## Item 1: physical census

Executed `uv run python E:/OOTRemake/work/r10-pots-cs10d/census_probe.py`, `summarize.py`
and `landmarks.py`. Read every non-DreamWorld `Banc/*/*.bcett.byml.zs`, join actor Hashes
to GameDataList Bool64bitKey entries, resolve inherited actor-pack components, and parse
MIT OoT Randomizer `LocationList.py` with Python AST, without executing it. Its checkout
is the existing pinned `526b4c8d81b7c4023ef4573ffbaf39344e270d5b`; licence read first.
Decoded trees stay external (`physical.json`, `packs.json`, `census-summary.json`).
`ootr-candidates.json` holds upstream names/types/vanilla/line references, not copied game data.

Counts below are **unique placement Hashes**, not a claim of independent once-only checks.
Pots/crates have different child/adult Hashes even at the same physical site; ordinary ground
rupees share their Hash across age copies. Exactly530 pot copies,50 crate copies and170
ordinary-rupee copies represent530/50/112 identities. Do not merge by coordinates or list index.

| Banc area | Pots | Breakable crates | Green | Blue | Red | Purple |
|---|---:|---:|---:|---:|---:|---:|
| BottomOfTheWell |44|0|0|0|0|0|
| DeathMountainCrater |7|3|8|0|1|1|
| DeathMountainTrail |0|0|3|2|1|0|
| DodongoCavern |37|0|0|0|0|0|
| FireTemple |18|4|0|0|0|0|
| ForestTemple |29|0|0|0|0|0|
| GanonCastle |9|0|0|0|0|0|
| GerudoFortress |15|13|0|0|0|0|
| GerudoTrainingGround |2|0|0|0|0|0|
| GerudoValley |8|0|0|0|0|0|
| GoronCity |13|2|0|0|0|0|
| Graveyard |0|0|8|0|0|0|
| HountedWasteland |8|2|0|0|0|0|
| HyruleCastle |6|2|0|0|0|0|
| HyruleField |11|14|17|7|2|0|
| IceCavern |15|0|0|0|0|0|
| InsideGanonCastle |52|0|0|0|0|0|
| InsideJabuJabuBelly |19|2|0|0|0|0|
| InsideTheDekuTree |0|0|3|0|0|0|
| KakarikoVillage |30|2|0|0|0|0|
| KokiriForest |8|0|9|7|0|1|
| Market |54|6|0|0|0|0|
| ShadowTemple |64|0|0|0|0|0|
| SpiritTemple |31|0|0|0|0|0|
| WaterTemple |24|0|0|0|0|0|
| ZoraDomain |10|0|0|6|0|0|
| ZoraFountain |8|0|16|0|0|0|
| ZoraRiver |8|0|17|3|0|0|
| **Total** |**530**|**50**|**81**|**25**|**4**|**2**|

### Actors and exclusions

- Ordinary pots: `Obj_Pot_A_01..08` =98/28/75/85/61/25/64/72 Hashes; four
  `_Respawn` variants02/05/07/08 =1/3/4/2; `Obj_Pot_A_06_Dream` =12 placed
  **outside DreamWorld**, so excluding the DreamWorld directory alone does not remove them.
- Breakable crates: `Obj_BrokenBox_A_01`38, `_02`1, `_03`6, `_06`5.
  `_02`/`_06` have no DropRef and are not ordinary item-supply crates.
- Ordinary ground rupees: `Obj_Rupee_{Green,Blue,Red,Purple}` only. Three Deku Tree
  green rupees have `Enemy_Scrub_Deku_ItemDrop_01..03` Presence gates; two lake rupees
  have AiGroup references. These112 are not all ungated ground checks.
- Exclude85 silver puzzle rupees, their counters, diving-game rupees, shop/event `TBox_`
  representations, flying-pot enemies, seven horseback-archery targets, Goron City's
  spinning-pot minigame, four Shadow skull pots, scenery/plant/cooking pots and movable
  puzzle boxes. Their identifiers occurred in the broad inventory; none was counted as
  an ordinary pot/crate/rupee merely because its name contained the word.

### How a pot's drop is set

Inherited `Pot` ActorParam resolves `DropRef` to `Drop_ResourceSupply_00`; its DropParam
uses the common `Drop` blackboard. `Drop__DropActor` and `Drop__DropTable` are explicit
**instance** String128 parameters, native initial value empty. `Drop__DropTableOverWrite`
is **not** an instance parameter. Banc `Dynamic.Drop__DropActor` names the native pickup;
`Dynamic.Drop__DropTable` names one of the loaded tables, including `None`.

Of530 pots,101 have a direct actor only,250 a table only,2 both,177 neither.
Unspecified drops use the resource-supply table rather than a fixed N64 item. Its rows
include probabilities, resource types and before-boss first/second/third candidates;
`Drop_Rupee_Red2` explicitly creates two red rupees. A table name is not one fixed grant.

### OoT Randomizer correspondence: names, not fabricated joins

Reference: [MIT LocationList.py at526b4c8d](https://github.com/OoTRandomizer/OoT-Randomizer/blob/526b4c8d/LocationList.py),
lines54–58 describe N64 room/setup/actor-index IDs. Those indices are **not remake Hashes**.
Non-MQ upstream rows:341 Pot,74 Crate,6 SmallCrate,155 Freestanding (the last includes
hearts/ammo, not155 ground rupees). The complete upstream name ledger and per-area counts
are retained in the external research output.

Useful named groups and their actual mismatch:

- `KF Know it All House Pot 1/2`, `KF House of Twins Pot 1/2` (lines145–148) correspond
  to the two remade house pairs; each has distinct age Hashes. The green/blue Twins pair
  distinguishes those rewards; the two green Know-It-All pots cannot be numbered by item.
  `KF Links House Pot` is not among the four child pots; no fake fifth placement is added.
- `KF Boulder Maze Blue Rupee 1/2` (115–116): two blue actors near the sword enclosure,
  Hashes6618764049130440222/16647730239269178270, one shared across ages and one child-only.
  Their individual N64 ordinal is unresolved; a shared area rule is not proof of the names.
  Seven actual KF blue pickups also include one beside Fado and one inside the shop;
  four N64 blue rows cannot be assigned in placement order.
- `Graveyard Dampe Race Rupee 1..8` (547–554): eight actual green pickups in the adult
  race course. Room/ordinal correspondence still needs its remake course/path audit.
- `DMT Rock Red Rupee`/`DMT Rock Blue Rupee` (595–596): the remade trail has one red,
  **two** blue and three green pickups in one low cave group. Colour alone cannot select
  the N64 blue name; the old rock access rule is not silently attached to a cave.
- `Wasteland Near GS Pot 1..4` (962–965): four pots per age at the buried building,
  versus eight independent Hashes. Native hearts/magic differ from N64 heart/nut/fairy/blue.
  `Wasteland Crate Near Colossus` (970) is a candidate for the single physical crate
  per age; the other four N64 crate names are not four additional remade crates.
- The remake has20 river ground rupees, but N64 `ZR Waterfall Red Rupee 1..3` are three
  adult red pickups. Reassigning all20 that N64 waterfall rule would be unsound.

These are evidence-labelled candidate groups, **not seeded physical-to-logic mappings**.
No `locations.toml`, generated world file, census scanner or existing shuffle policy changes
in item1. Exact stable IDs remain in the external physical ledger for subsequent work.

### Diagnostics / coordination

The first landmark sort failed because `(distance, actor-dict)` tuples compared dicts on
identical distances. Printed tied distances and both Hash/type pairs (chest plus its
KeepAway actor, and shared building pieces), then sorted explicitly by distance/Hash.
The cause-specific run succeeded; no unchanged failed rerun. No production issue was hidden.

Posted cs-r10: reset88/unsaved containers differ from reset24 ground rupees; destruction
is not pickup completion; counts/age variants do not establish N64 check identity. Proposed
controlled experiments and explicit blockers instead of unproved seed switches. All four
full gates remain required before ready/handoff; this item1 commit is a research checkpoint.

## Item 2: native grant and persistence contracts

`native_contracts.py` extracted seven native AI graphs; `decode.py` ran the already-installed,
unmodified external `ainb` decoder in `work/r7-play-cs7f/decoder-venv`. No GPL implementation
was read/copied and no dependency was added. All graphs/decoded JSON remain under this
track's external `ai/` folder. This is native-data evidence, not an engine or gameplay run.

- All499 flagged pots and44 flagged crates use reset88/file0 (`SupplyObject` in ordinary
  supply variants). All112 ordinary ground rupees use reset24/file0 and `NoRespawn`.
  No pot or crate in this census has a permanent reset24 pickup flag.
- Thirty-one pots lack any Bool64bitKey entry:10 explicit `_Respawn` pots,12 `_Dream`
  pots in the Ganondorf room and9 ordinary pots in CrumblingGanonCastle. Six crates
  have no flag (`_02`/`_06`, no native DropRef); their scene logic has other jobs.
  No flag is allocated or changed by this exploration.
- `Obj_Pot.root` calls `OneShotDeathRequestDeath` with reason10 when broken/thrown.
  `Obj_Common_LiftableBreakable.root` likewise requests object death. `DropItem.root`
  handles drop physics/rotation. The inspected graphs do **not** expose a pot Hash ->
  collected-child-drop flag channel. The death/drop component's engine implementation
  has not been reverse-engineered; absence of a graph node is not proof it cannot exist.
- **[INFERENCE]** Reusing reset88 destruction as check completion risks either renewable
  shuffled upgrades or losing an item left uncollected. Making destruction permanent
  could make the loss irreversible. It does not prove collection and must not be presented
  as a once-only oracle.
- Native ground-rupee replacement is data-expressible: change only Gyaml, retain its permanent
  Hash/Phive identity and every age copy. The D27/D33 five-item palette is the conservative
  candidate: Heart Container, Piece of Heart, Deku Shield, Hylian Shield, red20-rupee pickup.
  Shields/red rupees have freestanding gameplay evidence (sections11/27); that does **not**
  certify a spawned pot drop, every ground surface, or every replacement callback.
- `Obj_Heart_Piece` has its own `OneShotHeartPieceTakenDeadAfter` rather than the ordinary
  DropItem graph. A spawned piece without a shipped placement flag is therefore a useful
  **experiment**, not proof of a saved pot check. Inventory-only `Item_*` majors and the
  known-crashing Fire Arrows remain outside the candidate palette.

**Reviewer direction (Claude, this conversation):** agreed exploration outcome. Commit census
and native contracts; build isolated `-next` save-copy experiments, not Pot/Rupee seed switches.
Test one reset88 supply pot, one never-saved pot, one Kokiri ground rupee and one early-child
ground rupee elsewhere. Observe collection, leave/return, Save/Continue, repeat destruction,
and recovery when a pot drop is left uncollected. Kareem runs every game check.

Future logic policy is also explicit: remake names and the region's actual access rule, as with
`extra_*` chests; retain an N64 mapping only where exact. Count/ordinal mismatches do not justify
forcing OoTR names or using a more permissive N64 room rule. No product question is silently
decided by a physical-position guess. Posted the original boundary on cs-r10; this reviewer
direction supersedes that proposal.

## Item 3: reviewed experiments, no seed switches

The reviewer explicitly accepted the exploration/report branch in this conversation.
No `patch/pots.py`, census kind, permanent test, generated logic, Settings/CS1/CLI option,
fill rule or seed pipeline hook is added. Reusable research/build/check scripts remain
external; they are not an unimplemented production API. Existing seeds are unchanged.

### Actual outputs (built, not played)

All paths below are under `E:/OOTRemake/work/r10-pots-cs10d/ingame/`.

| New overlay | Existing physical target | Replacement | Copied backup / load slot |
|---|---|---|---|
| `pot-supply-piece-next` | child Twins-house supply pot15406610986108637956 | Piece of Heart | `2026-11-07_llr-tower-before-pickup` / manual01 |
| `pot-unsaved-piece-next` | Forest2F Bow-room respawn pot18069611988256927347 | Piece of Heart | `2026-11-09_1347-main-after-forest` / autosave00 |
| `rupee-kokiri-piece-next` | child-only boulder-enclosure blue16647730239269178270 | Piece of Heart | early ranch / manual01 |
| `rupee-field-hylian-next` | east Field bomb-grotto separate blue5620885265123329978 | Hylian Shield | `2026-11-08_2140-main-jabu` / manual01 |

Each has `Test - <overlay>.bat`, copied/adapted from the approved talon launcher, own
initially absent `user-<overlay>`, bin executable only, updater disabled and missing-exe,
source-save and overlay stops. Both pots also have `Test - <overlay>-uncollected.bat`,
using a second independent profile but the same overlay. **Six launchers, six separate
users; none executed/created by the agent.** Logs go inside their individual users.

`ingame/checklist.md` has the complete routes, required source slots, collection,
area leave/return, repeat break, Save/quit/Continue and independent uncollected-recovery
procedures. **Kareem: run those four experiments after quitting the played game; report
the actual reward/counter/inventory, repeat/change/loss, and overlay-open logs.** The
read-only `ingame/check_saves.py` examines only these six isolated profiles afterwards.

Save selection is evidence-based: all six relevant early saves leave the chosen supply
pot and child-only maze rupee unset; all six main-Jabu slots leave the Field rupee unset
and lack Hylian Shield. That child has Bomb Bag plus Bracelet, so the bomb-cover test
does not require late travel or Storms. The initially considered DMT red lives in a
Storms cave and was not used. The shared-age KF blue was already collected in manual01,
so the uncollected child-only blue is selected instead; no save flag was cleared.

The never-Hash-saved case cannot honestly be put in an early overworld location: none
exists there in this census. Forest's original room17/Bow-chest target is on2F, using
the completed-Forest/latest00 save, not earlier manual01. Its source has20 arrows.
The unchanged `ForestTemple_Level_Room_06_Prefab_6d52` graph creates/respawns the target
only with zero arrows, the ordinary partner dead, arrow bundle absent, camera/player
clearance and1200-frame delay. It has a native **AutogenGameData destruction latch**.
This corrects any inference that absence of a placement Hash means no other saved
state. The checklist explicitly sets up the native gates, does not bypass them, and
asks for the zero-arrow/ordinary-pot/route facts if it stays hidden. Its sensor still
watches arrow bundles, not the replacement heart: simultaneous pieces are an explicit
duplication question, not an accepted behavior.

### File deltas and exercised oracle

`uv run python .../build_experiments.py` completed through the real common writer.
No overlay existed beforehand; no player folder, backup, game file or existing seed
was rewritten. Exact tree inversions recover every entire original Banc, retaining
Hash/Phive, transforms, native AI references/group tables, anchors/Presence and all
other actors. Pots change only explicit drop selector (plus native table `None` for
the Forest source); rupees change only Gyaml on all copies of their selected Hash.

| Resource in its experiment | Raw before -> after | Allocation before -> after |
|---|---|---|
| Supply: Kokiri child Dynamic |510884 ->510916|511176 ->511208|
| Unsaved: Forest Static |215192 ->215220|215464 ->215496|
| KF rupee: Kokiri child Dynamic |510884 ->510904|511176 ->511176|
| Field rupee: adult Dynamic |591144 ->591168|591432 ->591432|
| Field rupee: child Dynamic |594868 ->594892|595144 ->595176|

The common writer emits the resource table for both pot experiments and the Field
experiment; no table is needed for the KF rupee. No GameDataList or actor pack is emitted.
`experiment-proof.json` retains the baseline, sizes/compressed sizes, resource hashes
and source-backup SHA256 maps. All source-backup hashes are unchanged after building.

Independent actual-artifact smoke:
`PYTHONHASHSEED=1010 uv run python .../verify_experiments.py` **passed** all four exact
inverse trees, recomputed deterministic compressed bytes, allocation-only table deltas,
six static launcher/absent-profile checks and unchanged backup hash maps.
`uv run python .../ingame/check_saves.py` **completed** and reported all six users have
no isolated saves yet; it creates nothing and starts nothing. Read actual launchers
back as text; safe bin path, nested/flat backup sources, overlay and per-user logs agree.
Retained `independent-proof.json`; no game, batch, dry-run, GUI or new save was run.

### Integration and acceptance boundary

Section43 is a small shared documentation-only checkpoint. It follows39 on this base;
Claude inserts tracksA/B/C sections40–42 before43 at integration, without placeholders.
No dependency files or other-track source are touched. Research checkpoints:
`af54354` item1 and `1146193` item2, both on `r10/pots`.

**Remaining external acceptance:** Kareem's grants, pot repetition/uncollected recovery,
ground-pickup persistence and overlay logs. Grant/persistence tests in an interpreter
cannot answer those native engine questions. Only after those results and review can
future seed checks use remake names/actual region rules; no N64 ordinal links are forced.
The full four-command gate evidence and final commit IDs follow once the serial locked
run completes. No commit has been posted ready based only on the artifact smoke.

### Gate runner diagnosis

The first runner launch (`bash E:/.../gates.sh`) failed127 **before running a gate or
acquiring the lock**. Printed `command -v bash` resolves to `C:\WINDOWS\system32/bash.exe`
(WSL), whose `/bin/bash` cannot open this native Windows path. The external script
exists and was read back. The cause-specific invocation explicitly uses
`"C:/Program Files/Git/bin/bash.exe" E:/OOTRemake/work/r10-pots-cs10d/gates.sh`.
Its native uv/pytest arguments retain Windows paths. No unchanged failed command is
rerun, no gate result is inferred from that wrapper failure, and no lock was removed
without ownership. The runner traps EXIT to release only the lock it successfully took.

## Kareem's first results (Claude relay, this conversation)

Ground experiment `rupee-kokiri-piece-next` **granted its Piece of Heart, no problem**;
`rupee-field-hylian-next` **granted its Hylian Shield, no problem**. The supply-pot
experiment **dropped its Piece of Heart**. These are accepted gameplay observations,
not agent reruns. The hidden Forest pot was **not run**.

**Supply-pot Run1 return result (further Claude relay):** this save's forest exit was
closed, so Kareem crossed the separate loading screen into Lost Woods and returned,
instead of leaving Kokiri Forest by its field exit. The broken target pot **did not
respawn**, so it awarded no second piece on that route. **Save and Continue was not
tried.** This is a specific loaded-area round trip, not proof of permanent completion
or behavior after a full save reload.

**Concrete thrown-pot hazard:** in the supply-pot uncollected run, Kareem threw the pot
at a tree; the Piece of Heart remained floating on the trunk, above child Link's reach.
Kareem confirms it was **unreachable and lost** in the uncollected run. A pot creates its
item at its **break position**, not necessarily its original placement. Even a collection-
correct once gate would not make thrown drops safe. Future delivery must be recoverable:
for example spawn at the pot's **placed position**, with its own reachability checked,
or grant directly, rather than using the thrown pot's landing/break position. Neither
alternative is implemented or player-verified by this report.

Claude reports `check_saves.py` found no slot with the target set or a new piece;
the player probably did not save after collecting. That is **not evidence of a failed
grant or absent persistence** and is not used to contradict the reported pickups.
Claude's question about return/repeat steps is answered only by the Lost Woods route
above; Save/Continue remains open. No negative save conclusion or unreported success is
invented. Preserve played experiment outputs/users, never rebuild them.

New report-only requests accepted: assess D22 collection-gated pot rewards plus a
distinct native appearance, and census floor recovery hearts (Saria's house/roof first).
No switch, save edit, model patch or new gameplay experiment is added by that request.

## Report addition A: collection-gated reward and native marker

**Assessment: the state-machine design is appropriate; a complete data-only connection
from an individual spawned drop's successful collection to its pot's D22 Bool is not
established.** Allocating the Bool alone does not provide that connection.

Desired behavior, following Kareem's description of Ship of Harkinian (not a source-code
port): while this stable pot check's saved Bool is false, show a recognizably marked pot
and drop its shuffled item. Only successful collection of **that pot's item** sets the
Bool. Later spawns look/behave natively and use the original drop selector/table. Native
reset88 destruction remains separate; it must not consume the shuffled check.
The observed Lost Woods round trip also shows why “leave and break it again” is not
yet a recovery mechanism: that pot stayed broken. A false shuffled-item Bool must not
be mistaken for a guarantee that the native pot will already respawn. If a loose reward
is lost, recovery must account for this independent destruction state as well.

The proven and missing pieces are distinct:

- D22 already demonstrates saved Bool allocation, an older save loading it, and event
  queries/writes retaining it. A per-check namespace can use the source file and actor
  Hash, never a positional ordinal. This storage is feasible, not a new feature here.
- Current pot `Drop__DropActor`/`Drop__DropTable` blackboard values are constant strings,
  not conditional expressions or named completion-flag selectors. Neither reads a D22
  Bool. A reviewed per-instance selector/graph would have to choose shuffled versus
  original drop and native appearance from that Bool.
- The generated item must carry its **source check identity** through breaking, being
  thrown, saving/loading and collection. Setting a Bool on pot death is too early;
  setting it on generic item ownership is wrong if the item came from another check.
  Patching a shared pickup pack or shared get flow with one constant Bool makes all
  uses of that actor one global check, not independent pots.
- Native Heart Piece has `DropActorRespawnData.RespawnGmdHash` (u64, default0,
  **IsInstanceParam=false**) and `OneShotHeartPieceTakenDeadAfter` (node7, no supplied
  flag-name input). This is a useful native lead for collection-linked **64-bit** state,
  not an exposed named-Bool write and not a validated `Dynamic.RespawnGmdHash` channel.
  The latter would simply be inventing an instance parameter. Ordinary DropItem pickups
  do not all share the heart-specific callback.
- A new pickup-specific graph/actor variant might write a per-pot flag after successful
  pickup; **[INFERENCE]** it needs a validated source-identity binding or safe per-check
  registered actor variants, native collection-vs-other-death semantics, save/layout/
  resource sizing and reload tests. None is supplied by the present constant-drop patch.
  The native engine callback has not been proved unable to support such a future path.
- Outstanding items need exactly-one recovery: do not spawn a second while the first
  exists; if an uncollected item disappears or becomes unreachable on a tree, the next
  visit must recover the same check without awarding it twice. The confirmed lost item
  requires recoverable delivery (placed-position spawn or direct grant, for example),
  not merely a completion Bool. A direct grant must set completion only after success;
  a placed-position item still needs actual collection before setting it.

### Native appearance assets

The native packs resolve **eight different ModelInfo/Fmdb identities**,
`Obj_Pot_A_01..08`, all in model project `Obj_Pot_A`. All eight ordinary variants use
the same `Obj_Pot_A_01` PhysicsParam and pot AI, but retain their own ModelInfo and
fracture/destruction appearance resources. The dump actually contains their eight
`Model/Obj_Pot_A.Obj_Pot_A_0N.bfres.zs` files and corresponding fracture resources.
Thus a native variant can be a **candidate** static mark without importing artwork.
No model was rendered and no exact colour/visual contrast is certified from its name.

An out-of-area variant (for example Forest02 against Kokiri01) is a candidate for
Kareem's visual comparison, not a globally unique “uncollected” model: the eight variants
already occur in vanilla areas. Do not replace an entire `_Respawn` Gyaml with an
ordinary variant merely to recolour it; that can discard the original creation/persistence
contract. Do not change a shared pot pack globally, which would mark vanilla pots too.
A per-instance/registered variant retaining the original physics/AI plus the matching
native visual assets, and a Bool-driven transition back after collection, still needs
validated wiring and a player check. No such model/actor/graph patch is built this round.

**Recommendation for review:** retain this design as the target, but block a pot seed
switch on source-bound collection state, native-after-collection behavior, and thrown/
uncollected recovery. Continue the current repeat/reload experiments before choosing
an implementation. The floor-heart report below is independent of this pot problem.

## Report addition B: placed recovery hearts, Saria first

**Native contract: these are saved NoRespawn pickups, like ground rupees, not reset88
supply pots. [INFERENCE] Their collected/dead state should persist rather than replenish
on area return. Actual floor-heart collection/reload behavior is not yet player-proven.**
Do not call metadata or an unread/newly unwritten save a gameplay result.

Round8's `all-pickups.json` already inventories these actors; the new read-only
`work/r10-pots-cs10d/floor_hearts.py` reproduces the current placement/flag/model audit.
Scope is **placed** `Obj_Heart` and `Obj_Heart_InWater` in non-DreamWorld Banc files,
not hearts dynamically generated by pots, enemies, grass or drop tables.

| Native area | Ordinary hearts | Water hearts | Physical identities |
|---|---:|---:|---:|
| KokiriForest | 14 | 0 | 14 |
| InsideTheDekuTree | 6 | 3 | 9 |
| FireTemple | 2 | 0 | 2 |
| Total | 22 | 3 | 25 |

All25 have a placement-Hash `Bool64bitKey` with **ResetTypeValue24, SaveFileIndex0**.
Both heart actors inherit `NoRespawn` and ordinary `DropItem.root`, not the pot supply
AI and not Heart Piece's special `OneShotHeartPieceTakenDeadAfter` callback. Round8's
warning still applies: replacement actors, underwater physics and collection/reload
must be demonstrated, not certified by finding a flag alone.

### Saria's house: separate child and adult identities

Four ordinary hearts around **(-10,111.8,17.8)** form the house-floor cluster; three
around **(-10,117.6,17)** form the roof cluster directly above. They occur in both
`Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs` and
`Banc/KokiriForest/KokiriForest_Adult_Dynamic.bcett.byml.zs`, with **different Hashes
and flags**. That is14 physical/saved identities at seven near-matching positions,
not seven shared-age flag entries. No arbitrary list-index join is made.

| Remake cluster / approximate x,z | Child Hash | Adult Hash |
|---|---|---|
| House / -10.08,18.83 | 8217415107461137996 | 11501932305561522817 |
| House / -11.07,17.77 | 3211747475593407179 | 4751294038826612236 |
| House / -9.95,16.74 | 9333984718219537434 | 13752432406165881016 |
| House / -9.00,17.87 | 13766700305743331316 | 16890252572970412506 |
| Roof / -9.12,17.64 | 9778104484775444655 | 12317452644253046635 |
| Roof / -10.04,15.87 | 1135865174486388723 | 1214219023609128151 |
| Roof / -11.31,17.48 | 12744945159394614918 | 15227875255265438204 |

The MIT port data has exactly four `KF Sarias House Recovery Heart` rows
(`world/kokiri_forest.toml:124-127`) and three `KF Top of Sarias Recovery Heart` rows
(`:209-211`). The **cluster counts agree for each age**. It does not prove which
geometric actor is N64's ordinal1/2/3/4, or that collecting in one age retires the other
age's identity. These are reference-level correspondences, not an exact shuffle mapping.
No logic rule or location row is added; later integration still uses remake names and
the actual region's access rule, with any age-family product decision reviewed.

**Kareem, if testing floor-heart persistence:** use an isolated disposable save with a
known uncollected house/roof heart, take damage so the heart can actually be consumed,
collect it, cross the Lost Woods loading screen and return; then Save and Continue,
and return again. Record which heart returns/disappears and the age. A saved check can
be corroborated by its exact table Hash only after confirming a save was written.
Repeat for the roof and, separately, adult identity if available. No heart experiment
or shuffle switch has been built by this report-only request.

## Final verification and handoff

The serialized gate runner finished successfully with `CLAWSHOT_WORKERS=1`, having
acquired the shared gate lock and released it via its EXIT trap:

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | 239 files already formatted; exit0 |
| `uv run ruff check` | All checks passed; exit0 |
| `uv run pytest --basetemp E:/OOTRemake/work/r10-pots-cs10d/gate-synthetic-next` | 761 passed,89 skipped;1257.40s; exit0 |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump --basetemp E:/OOTRemake/work/r10-pots-cs10d/gate-dump-next` | 88 passed,762 deselected;826.97s; exit0 |

Runner emitted `ALL_GATES_EXIT=0`. The full logs remain outside the repo as
`work/r10-pots-cs10d/gate-{format,lint,synthetic,dump}.log`.

After the gate process ended, a single read-only runtime audit,
`uv run python E:/OOTRemake/work/r10-pots-cs10d/floor_hearts.py`, completed in2.16s
with `READ_ONLY_CENSUS_PASS`:25 identities/25 placements, all reset24/file0;
22 ordinary and3 water hearts; area counts2/9/14; both native NoRespawn/DropItem
contracts; zero AiGroup references for the14 Kokiri hearts; all eight referenced native
pot model resource files exist. The current scan also places both heart clusters at
the native `Land_Kokiri_House_{Inside,Outside}_B` house anchor
(-10.241,111.732,18.278), consistent across the two age Bancs.
Its detailed output is `work/r10-pots-cs10d/floor-heart-report.json`, outside the repo.
It neither reads played saves nor rewrites overlays/users; this is metadata/runtime
readback proof, not player collection/reload or rendered-model proof.

Reviewed deliverable is the census, native-contract report, four independently verified
isolated overlays/six launchers and player checklist, plus the additions above. No
Pot/Rupee/RecoveryHeart switch, production location/logic integration, named pot Bool,
new pickup callback or model replacement ships. No experiment is rebuilt after play.

**Player evidence still open:** supply-pot Save/Continue, the hidden Forest pot,
ground-rupee return/reload outcomes, and floor-heart collection/reload. A native visual
mark also needs an actual contrast check. The observed Lost Woods no-respawn and
confirmed thrown-item loss are already recorded, not rerun or discounted from saves.
These limitations block any claim of safe pot seed support, not this exploration handoff.
