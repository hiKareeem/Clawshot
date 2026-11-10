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
