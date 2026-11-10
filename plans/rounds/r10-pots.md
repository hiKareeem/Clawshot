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
