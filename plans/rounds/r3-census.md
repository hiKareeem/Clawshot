# Round 3, track B: census and formats (cs3b)

Branch `r3/census`, from main `24512a7`. Owns `src/clawshot/census/`, `src/clawshot/data/locations.toml`,
`src/clawshot/formats/rstb.py`, `tests/test_census*.py`, `tests/test_rstb*.py`, this file and section 11 of
`plans/03-game-data.md`. Scratch scripts and decoded data: `E:/OOTRemake/work/r3-census/` (outside the repo).

## Item 2: the Treasure Chest Game reward chest

**Choice: a census kind of its own, `treasure_game_reward`** (`scan.kind_of`), for the two
`Obj_HrlCity_Shop_TBox_A_02` boxes at the reward spot. The ten room boxes (`Obj_HrlCity_Shop_TBox_A_01`) stay
`treasure_game_box`. A generator that shuffles chests adds the kind `treasure_game_reward` and leaves
`treasure_game_box` alone (D17), with no list of ids to keep in sync. A field on the definition would have done the
same, but the kind is what the census, the definitions file and the world test already select on.

| id | name | vanilla item | OoT Randomizer |
|---|---|---|---|
| 16881481538337649070 | Market Treasure Chest Game Reward | `Obj_Heart_Piece` | Market Treasure Chest Game Reward |
| 6781536951709667179 | Market Treasure Chest Game Reward Repeat (TBox_Rupee_Red) | `TBox_Rupee_Red` | none |

Both stand at the same spot, have a save flag, `IsEnableRepeatOpen` and the open event
`MiniGame_ChoiceTreasure_OpenClearTreasureBox`, and are members of one logic module
(`MiniGame_SequentialChoiceTreasure_cbde`) with the ten room boxes and the doors; which one appears is decided there
(the module reads `MiniGame_ChoiceTreasure_IsClear` among others; not decoded). The red-rupee box is presumably the
prize for a win once the Heart Piece is taken. `ootr.treasure_game` now takes the reward from the new kind; matching
is unchanged (`write_locations` reproduces the file).

**The repeat box stays vanilla** (reviewer, 18:12): it is the repeat prize, not an OoT Randomizer check. The ten room
boxes are `keep_vanilla` in track C's world data, so the generator side of D17 is covered there; the kind is for the
patch plan.

**For the patch (track A):** every treasure-game box also carries `Dynamic.DropViewActor`, the model shown in the box
(reward: `Obj_Heart_Piece_MiniGame`; room boxes: `Obj_MiniGame_SmallKey`, `Obj_OrnamentalRupee_{Green,Blue,Red}_MiniGame`).
Those five are the only `*_MiniGame` view actors in `Pack/Actor`, so a shuffled reward with another item either keeps
the heart-piece model, takes the item's own actor, or drops the field; which one works is for the in-game test D17
asks for.

**For track C:** `tests/test_world_census.py` `COVERED["Chest"]` needs `treasure_game_reward` once Market is ported
(posted 18:02).

## Item 1: Gold Skulltulas linked to OoT Randomizer names

97 linked, 3 gone (N64-only), 3 new, 0 left unlinked. Applied to `locations.toml` by a throwaway script
(`E:/OOTRemake/work/r3-census/gs_links.py`; it sets `name` = `oot_randomizer_name` for the 97 and a readable name for
the 3 new ones); `write_locations` then reproduces the file byte for byte, so the links survive a rewrite. Every name
is in OoT Randomizer's `LocationList.py` (`write_locations` checks).

**Gone (N64-only), posted 18:06:** `HF GS Cow Grotto`, `LLR GS Rain Shed`, `LLR GS Back Wall`. The `HyruleField` Banc
area (Hyrule Field, Lon Lon Ranch, Lake Hylia) holds 11 Gold Skulltulas on both sides; 8 match N64 ones, 3 are new.
The N64 cow grotto still exists (a grotto room near Gerudo Valley's rocks with `Animal_Cow`, a `Enemy_Skulltula` and two
spider-web actors) but has no Gold Skulltula; the ranch has only the tree, the house window and the new tower one.

**New (readable names, no OoT Randomizer name):**

| id | name | where (data, and both guides agree) |
|---|---|---|
| 2177746409373494991 | HF GS Lone Tree | a swaying tree in Hyrule Field (`Gimmick_SwayingTree_Skulltula_Gold`), west of the river by the Kokiri Forest entrance; both ages, roll into it |
| 9047381233010434881 | HF GS Wetland Grotto Crate | adult only: a crate (`Obj_BrokenBox`, `IsAgonyStoneBoxConnect`) in a Hyrule Field grotto with a `Enemy_Skullwalltula` and a Gossip Stone, north of the Lake Hylia entrance; the guides: kill the Skullwalltula as child, then the adult's crate holds the Gold Skulltula (a green rupee otherwise); explosives to open the grotto |
| 2730878115209290675 | LLR GS Tower | Lon Lon Ranch tower, on the vines above the boxes, 13 units from the tower heart piece; night (`Nocturnal`); both ages; Boomerang as child, Hookshot as adult |

**How they were linked.** Every Gold Skulltula's data was listed with its neighbours
(`E:/OOTRemake/work/r3-census/gs_context.txt`): room (`DefaultDungeonRoomIndex`), ages, the enemies and objects of its
room, its logic group and flags. The data marks the kind of spot: `Enemy_Skulltula_Gold_IsMagicBeanSoil` plus a
`Gimmick_MagicBeanSoil_<Area>` presence flag (soft soil), `Gimmick_SwayingTree_Skulltula_Gold` (a tree to roll into),
`Gimmick_BoxBroken_Skulltula` or a link from an `Obj_BrokenBox` (crate), and `Enemy_Skulltula_Gold_Nocturnal` with
`Gimmick_Nighttime_Skulltula_Gold_Appear` (night). Coordinates are +x east, +z south (Lake Hylia is at large +z,
checked against N64's map). Bases:

- **actor**: the only one of its spot type in the area on both sides (soft soil, tree, crate).
- **room**: in a dungeon, the room's enemies and objects pin the N64 location (e.g. Bottom of the Well room 4 has Keese
  and room 5 a Deku Baba, the guides' east and west rooms; Dodongo's Cavern room 2 has the scarecrow marker and baby
  Dodongos; Fire Temple room 18 the hammer pillars and a black rock, room 19 a Like Like and flying tiles).
- **position**: an overworld spot next to the landmark of the N64 name (Impa's house heart piece, the archery target, the
  tent with the escaped carpenters, the bridge in Zora's River, ...), or an age/night split.
- **only one**: the area has one.
- **elimination**: the last one left in its area, at a spot that differs from N64's. These are moved checks: right for
  counts and the area, but the remake's requirement is not N64's (table below).
- **room, height**: Jabu-Jabu's two lobby-basement Gold Skulltulas are in one room (3) at heights 88.4 and 90.3; Lower and
  Upper are assigned by that. OoT Randomizer gives both the same region and rule, so a swap would change only the name.

| Banc area | OoT Randomizer name | id | room | ages | night (data) | spot (data) | basis |
|---|---|---|---|---|---|---|---|
| BottomOfTheWell | Bottom of the Well GS East Inner Room | 12165938013608963606 | 4 | both |  |  | room |
| BottomOfTheWell | Bottom of the Well GS Like Like Cage | 3889761319471426870 | 7 | both |  |  | room |
| BottomOfTheWell | Bottom of the Well GS West Inner Room | 7460556442932201772 | 5 | both |  |  | room |
| DeathMountainCrater | DMC GS Bean Patch | 6397182598322965076 |  | child |  | soft soil | actor |
| DeathMountainCrater | DMC GS Crate | 18219295034534354574 |  | child |  | crate | actor |
| DeathMountainTrail | DMT GS Above Dodongos Cavern | 17669199296215821346 |  | adult |  |  | position |
| DeathMountainTrail | DMT GS Bean Patch | 17425319789138387506 |  | child |  | soft soil | actor |
| DeathMountainTrail | DMT GS Falling Rocks Path | 832677387023638406 |  | adult |  |  | position |
| DeathMountainTrail | DMT GS Near Kak | 351345377871782696 |  | both |  |  | position |
| DesertColossus | Colossus GS Bean Patch | 234735562946824289 |  | child |  | soft soil | actor |
| DesertColossus | Colossus GS Hill | 11160993739666517210 |  | both | yes |  | position |
| DesertColossus | Colossus GS Tree | 15057756765324812936 |  | both | yes |  | position |
| DodongoCavern | Dodongos Cavern GS Alcove Above Stairs | 4565265801822094851 | 18 | both |  |  | elimination |
| DodongoCavern | Dodongos Cavern GS Back Room | 13690401647626643497 | 20 | both |  |  | room |
| DodongoCavern | Dodongos Cavern GS Scarecrow | 960362013021648957 | 2 | both |  |  | room |
| DodongoCavern | Dodongos Cavern GS Side Room Near Lower Lizalfos | 1171854281537584829 | 3 | both |  |  | room |
| DodongoCavern | Dodongos Cavern GS Vines Above Stairs | 8470399761714006011 | 10 | both |  |  | room |
| FireTemple | Fire Temple GS Boss Key Loop | 14706322686481615109 | 18 | both |  |  | room |
| FireTemple | Fire Temple GS Boulder Maze | 12751796212121957464 | 5 | both |  |  | room |
| FireTemple | Fire Temple GS Scarecrow Climb | 5556173334779815044 | 7 | both |  |  | room |
| FireTemple | Fire Temple GS Scarecrow Top | 9172014785497046138 | 8 | both |  |  | room |
| FireTemple | Fire Temple GS Song of Time Room | 6789992996625105554 | 19 | both |  |  | room |
| ForestTemple | Forest Temple GS Basement | 3072474196008424241 | 27 | both |  |  | room |
| ForestTemple | Forest Temple GS First Room | 11081821111317815057 | 0 | both |  |  | room |
| ForestTemple | Forest Temple GS Level Island Courtyard | 10970805784153267902 | 12 | both |  |  | room |
| ForestTemple | Forest Temple GS Lobby | 17612196129225973969 | 2 | both |  |  | room |
| ForestTemple | Forest Temple GS Raised Island Courtyard | 2014780391754316762 | 14 | both |  |  | room |
| GanonCastle | OGC GS | 5626064870824758772 |  | both |  |  | only one |
| GerudoFortress | GF GS Archery Range | 13037049463363052038 |  | adult | yes |  | position |
| GerudoFortress | GF GS Top Floor | 9362225887419425752 |  | adult | yes |  | position |
| GerudoValley | GV GS Bean Patch | 8326970197618554626 |  | child |  | soft soil | actor |
| GerudoValley | GV GS Behind Tent | 13584527502619061465 |  | adult | yes |  | position |
| GerudoValley | GV GS Pillar | 11535915511003753934 |  | adult | yes |  | position |
| GerudoValley | GV GS Small Bridge | 15265071047503310220 |  | child | yes |  | position |
| GoronCity | GC GS Boulder Maze | 569390966671955163 |  | child |  | crate | actor |
| GoronCity | GC GS Center Platform | 18139423190738716302 |  | adult |  |  | position |
| Graveyard | Graveyard GS Bean Patch | 16798263777516949500 |  | child |  | soft soil | actor |
| Graveyard | Graveyard GS Wall | 229475726653285413 |  | both | yes |  | position |
| HountedWasteland | Wasteland GS | 14910672274965350769 |  | both |  |  | only one |
| HyruleCastle | HC GS Storms Grotto | 9162653017526462607 |  | both |  |  | position |
| HyruleCastle | HC GS Tree | 2504273934093629549 |  | both |  | tree | actor |
| HyruleField | HF GS Near Kak Grotto | 12007978132755687032 |  | both |  |  | elimination |
| HyruleField | LH GS Bean Patch | 7014193622407727514 |  | child |  | soft soil | actor |
| HyruleField | LH GS Lab Crate | 7388645484070660331 |  | adult |  | crate | actor |
| HyruleField | LH GS Lab Wall | 13944703896577680014 |  | child | yes |  | position |
| HyruleField | LH GS Small Island | 8655370827943125875 |  | both |  |  | elimination |
| HyruleField | LH GS Tree | 789492162651991711 |  | adult | yes |  | position |
| HyruleField | LLR GS House Window | 15889002414176907668 |  | child | yes |  | position |
| HyruleField | LLR GS Tree | 341792603838029977 |  | both |  | tree | actor |
| IceCavern | Ice Cavern GS Heart Piece Room | 1612219105489330028 | 6 | both |  |  | room |
| IceCavern | Ice Cavern GS Push Block Room | 14822647495538506998 | 8 | both |  |  | room |
| IceCavern | Ice Cavern GS Spinning Scythe Room | 7165255787572043804 | 3 | both |  |  | room |
| InsideJabuJabuBelly | Jabu Jabus Belly GS Lobby Basement Lower | 13852835165271311030 | 3 | both |  |  | room, height |
| InsideJabuJabuBelly | Jabu Jabus Belly GS Lobby Basement Upper | 11283202900158580106 | 3 | both |  |  | room, height |
| InsideJabuJabuBelly | Jabu Jabus Belly GS Near Boss | 15983944335296207002 | 5 | both |  |  | room |
| InsideJabuJabuBelly | Jabu Jabus Belly GS Water Switch Room | 11513774157335944149 | 14 | both |  |  | room |
| InsideTheDekuTree | Deku Tree GS Basement Back Room | 17501688996789643983 | 11 | both |  |  | room |
| InsideTheDekuTree | Deku Tree GS Basement Gate | 18075358844331090388 | 4 | both |  |  | position |
| InsideTheDekuTree | Deku Tree GS Basement Vines | 16101480770659370603 | 4 | both |  |  | position |
| InsideTheDekuTree | Deku Tree GS Compass Room | 13609975487234437568 | 3 | both |  |  | room |
| KakarikoVillage | Kak GS Above Impas House | 3310819903461047792 |  | adult | yes |  | position |
| KakarikoVillage | Kak GS House Under Construction | 14107117960174262321 |  | child | yes |  | elimination |
| KakarikoVillage | Kak GS Near Gate Guard | 11629189455828560791 |  | child | yes |  | position |
| KakarikoVillage | Kak GS Skulltula House | 15314554401574296838 |  | child | yes |  | position |
| KakarikoVillage | Kak GS Tree | 7677963516305772491 |  | child |  | tree | actor |
| KakarikoVillage | Kak GS Watchtower | 15118290503807073158 |  | child | yes |  | position |
| KokiriForest | KF GS Bean Patch | 9623998892552467148 |  | child |  | soft soil | actor |
| KokiriForest | KF GS House of Twins | 7116603238806634901 |  | adult | yes |  | position |
| KokiriForest | KF GS Know It All House | 17067594426901953848 |  | child | yes |  | position |
| LostWood | LW GS Above Theater | 4335656213162247230 |  | both |  |  | position |
| LostWood | LW GS Bean Patch Near Bridge | 9333354743976439033 |  | child |  | soft soil | position |
| LostWood | LW GS Bean Patch Near Theater | 17796658857969527112 |  | child |  | soft soil | position |
| Market | Market GS Guard House | 8942465719711548237 |  | child |  | crate | only one |
| SacredForestMeadow | SFM GS | 14473218207379268379 |  | adult |  |  | only one |
| ShadowTemple | Shadow Temple GS Falling Spikes Room | 15148554628675590606 | 11 | both |  |  | room |
| ShadowTemple | Shadow Temple GS Invisible Blades Room | 16933078188088206331 | 31 | both |  |  | room |
| ShadowTemple | Shadow Temple GS Near Ship | 8823884712433934372 | 17 | both |  |  | room |
| ShadowTemple | Shadow Temple GS Single Giant Pot | 15564367841356014861 | 14 | both |  |  | elimination |
| ShadowTemple | Shadow Temple GS Triple Giant Pot | 10270336409167849808 | 20 | both |  |  | room |
| SpiritTemple | Spirit Temple GS Boulder Room | 8120267919866495114 | 15 | both |  |  | room |
| SpiritTemple | Spirit Temple GS Hall After Sun Block Room | 10127391959410674946 | 10 | both |  |  | room |
| SpiritTemple | Spirit Temple GS Lobby | 12959656942046734931 | 7 | both |  |  | room |
| SpiritTemple | Spirit Temple GS Metal Fence | 10530233152473742636 | 4 | both |  |  | room |
| SpiritTemple | Spirit Temple GS Sun on Floor Room | 5086449036385341804 | 7 | both |  |  | elimination |
| WaterTemple | Water Temple GS Behind Gate | 16157272130665282352 | 2 | both |  |  | room |
| WaterTemple | Water Temple GS Central Pillar | 11571778270592589517 | 1 | both |  |  | room |
| WaterTemple | Water Temple GS Falling Platform Room | 4399424945134189769 | 25 | both |  |  | elimination |
| WaterTemple | Water Temple GS Near Boss Key Chest | 186694424287048567 | 24 | both |  |  | room |
| WaterTemple | Water Temple GS River | 15506432733081566465 | 21 | both |  |  | room |
| ZoraDomain | ZD GS Frozen Waterfall | 9600417828645642589 |  | adult |  |  | only one |
| ZoraFountain | ZF GS Above the Log | 7152962033963346563 |  | child | yes |  | position |
| ZoraFountain | ZF GS Hidden Cave | 9537398183107003742 |  | both | yes |  | position |
| ZoraFountain | ZF GS Tree | 17355397719442343054 |  | child |  | tree | actor |
| ZoraRiver | ZR GS Above Bridge | 9450239379321634455 |  | adult | yes |  | position |
| ZoraRiver | ZR GS Ladder | 8695975724114049706 |  | child | yes |  | position |
| ZoraRiver | ZR GS Near Raised Grottos | 10917372215719266172 |  | adult | yes |  | position |
| ZoraRiver | ZR GS Tree | 12370559827741970774 |  | child |  | soft soil | elimination |

"ages" is the census's (which placement files hold it), not a logic rule: a dungeon file serves both ages.

### Moved checks: what differs from N64 (for track C's overrides)

From the data where it says so, else from the guides (facts only). Section 9 of `03-game-data.md` already has the
Megaton Hammer (Fire Temple boss-key loop, DMT near the crater) and Hookshot (OGC) changes.

| OoT Randomizer name | In the remake |
|---|---|
| Dodongos Cavern GS Alcove Above Stairs | not in the stair room: a side room off the main hall's upper floor, behind a bombable wall (`WallCrack` in room 18), with two Dodongos; on the back of a rock spike. Needs explosives. |
| HF GS Near Kak Grotto | same grotto contents (a big Skulltula, the Gold Skulltula on the wall, Boomerang or Hookshot, a rock to blow open), but the grotto is in the woods south of Lon Lon Ranch, not near Kakariko |
| LH GS Small Island | a tunnel at the south-west shore of Lake Hylia; in both age files, and the data has no night flag on it (one guide says night) |
| ZR GS Tree | no tree: the soft soil next to the bean seller (`Gimmick_MagicBeanSoil_ZoraRiver02`). Needs bugs, child. |
| Colossus GS Tree | on the rock face north-west of the Spirit Temple (the side without the Gossip Stone), 13 units from a dead tree; night; both ages (Longshot as adult, Boomerang as child, per the guides) |
| Colossus GS Hill | on the plateau reached by the bean plant; night; in both age files |
| Forest Temple GS Raised Island Courtyard | on a ledge in the east garden reached by Scarecrow's Song and the Hookshot (scarecrow marker in room 14) |
| Ice Cavern GS Heart Piece Room | same room (the compass room), behind a pillar |
| Jabu Jabus Belly GS Water Switch Room | on the wall after climbing the vines (N64: on the vines) |
| Shadow Temple GS Single Giant Pot | not in a pot: on a wall at the end of the wind-tunnel room (room 14, fans), reached with the Longshot |
| Shadow Temple GS Triple Giant Pot | inside the last of three rotating skull pots, which have to be blown up |
| Spirit Temple GS Sun on Floor Room | on the giant statue's right hand, in the statue room (room 7, scarecrow marker): adult, Longshot and Scarecrow's Song |
| Spirit Temple GS Lobby | in a corner right of the statue, no item needed (guides) |
| Water Temple GS Falling Platform Room | in a room behind a bombable wall near where Ruto is met, at the middle water level (room 25, three Shell Blades); needs explosives |
| Water Temple GS Near Boss Key Chest | seen through the small waterfall where boulders fall; Longshot (N64: behind it) |
| GV GS Small Bridge | under the first bridge, at night, Boomerang |
| Fire Temple GS Scarecrow Climb | at the top of the climbing wall, near the door (N64: on the wall itself) |

**Night.** The data's night marker (`Enemy_Skulltula_Gold_Nocturnal`) is on 24 of 100 (table). OoT Randomizer's
night rules cover more (`DMT GS Above Dodongos Cavern`, `DMT GS Falling Rocks Path`, `ZD GS Frozen Waterfall`, `Kak GS
Tree`, `SFM GS`, ...): those are linked to other logic groups (`DeathMountainTrail_Adult_Prefab_*`,
`Gimmick_AllDay_Skulltula`, `Gimmick_SwayingTree_*`) and the guides disagree on some (one says the Kakariko tree is
night only, the other not). I did not decode the groups. Until an in-game look, keeping OoT Randomizer's night rules
is the safe side (it can only make the logic stricter).

**Weakest links** (if the world needs a wrong-link check, these first): the 9 `elimination` ones, and the two Jabu-Jabu
basement ones (`room, height`). `Spirit Temple GS Sun on Floor Room` is the least sure: the remake has no Gold
Skulltula in a sun-on-floor room on the child climb, and the statue room has two (`Lobby` beside the statue, the
scarecrow one on the hand); which of the two is N64's `Lobby` is a guess from "beside the statue, no item needed".

## Item 3: `clawshot.formats.rstb`, the resource size table

`src/clawshot/formats/rstb.py`: `read(bytes) -> ResourceSizeTable`, `write(table) -> bytes` (decompressed bytes; the
file is plain zstd, so `zsdic.Dictionaries.compress(rstb.TABLE_PATH, ...)` writes it), `table.get(path)` /
`table.set(path, size)` (romfs path with or without `.zs`; a path among the name entries is looked up by name, any
other by CRC32), and `required_size(path, size)`, the entry a file needs for its decompressed size. Format in the
module docstring (Tears of the Kingdom's RESTBL v1: 22-byte header, sorted CRC32 entries, then 160-byte name entries
for colliding paths; here 219,968 and 10, none of the 10 a placement file or event flow).

**Formula: entry = decompressed size rounded up to 32 + an overhead per type.** `required_size` knows only the types
checked against every such file in the game, and raises for any other:

| Type | Overhead | Files that fit |
|---|---:|---|
| `.bcett.byml` (placements) | 264 | 160 of 160 |
| `.bfevfl` (event flows) | 272 | 914 of 914 |
| `.sarc` (`Mals/` message archives) | 312 | 16 of 16 |
| `.pack` | 312 | 8384 of 8384 with an entry (`Pack/ZsDic.pack.zs` has none) |

Not covered, from the same survey (scratch, `E:/OOTRemake/work/r3-census/`): `GameDataList` fits 264 (one file;
`03-game-data.md` section 7 says "+ 288", which is entry minus the raw size, not minus the rounded size); `RSDB`
tables fit 264 except `ActorInfo` (+3064); `.ainb` is 376 for all 1822 `Logic/` files but varies in `Sequence/`
(`LoadBancImpl` +392) and `AI/` (+376 to +416), so it is not a fixed overhead.

**For track A (posted):** for each changed file, `need = rstb.required_size(path, len(decompressed))`; if
`need > table.get(path)`, `table.set(path, need)`; write the table to `<out>/romfs/System/Resource/...` only when an
entry changed (it is 1.76 MB decompressed). Raising only, never lowering, keeps every other file's entry as the game
has it. Round 1 and 2 loaded files up to 32 bytes over their entry, so the game tolerates some growth; how much is
untested.

Tests: `tests/test_rstb.py` (synthetic: write order and read-back, name-before-CRC lookup, `set`, the formula at the
32-byte boundary, an unchecked type, six malformed tables, an over-long name); `tests/test_rstb_dump.py` (`-m dump`:
the game's table writes back byte-identical; the formula fits every placement file, event flow, message archive and
`Pack/Actor` pack: 160, 914, 16 and 8373 of the same).

## Item 4: freestanding major items

### What the data says

**No `Obj_` pickup differs from the red rupee in a way that explains round 2's crash.** Compared (packs, their
`ActorParam` chains, `RSDB/ActorInfo` and `GameActorInfo` rows) for `Obj_Arrow_Fire`, `Obj_Rupee_Red`,
`Obj_Heart_Piece` and the other pickups:

- Every pickup inherits `Obj_Item_Base` (root AI `DropItem.root.ain`, the pick-up event `PouchContent.event.root.ain`,
  `ActorGameDataSetting` `NoRespawn`). The red rupee and the heart piece override the event (`..._EnableWarp`,
  `PouchContentUtuwa`) and ship that AINB in their own pack; `Obj_Arrow_Fire` uses the base event, whose AINB is in
  `Pack/AI.Global.Product.111.pack.zs`, as is `DropItem.root.ainb`. Nothing the Fire Arrows pick-up names is missing.
- `Obj_Arrow_Fire`'s differences are those of any "Large" pick-up: manual pick-up (`PickUpItem` attention, the get
  demo), the model of the item itself (`Item_Arrow_Fire`, bfres and textures in `Model/` and `Tex/`), its pouch item
  `Item_Arrow_Fire`. `ActorInfo` rows carry the same fields for all of them (heap sizes, radii, model names).
- **Every placed pick-up of a major item in the game is a member of a level prefab's logic group and of
  `SimultaneousGroups`/`FarDeleteGroups`**: the Fire Arrows (`HyruleField_LakeHylia_Adult_Prefab_5313`, the sun-shot
  event, which also holds an `EventRequestActor` for `GetFireArrow_FireArrowAppear`), Ruto's letter
  (`HyruleField_LakeHylia_Child_Prefab_9e98`), the fishing lures, the dungeon keys, the Gerudo Fortress keys, every
  boss heart container. Heart pieces are in no such group (each is only linked from its `HeartPieceAnchor`), and
  neither are the 7 placed red rupees. So a lone major pick-up created when an area loads has no precedent in the game.
- **The crash is Hookshot's.** Its signature (thread `OptimizeChangeBanc`, read of guest `0x4`, lr `0x809051ec`) is
  `NotRexed/Hookshot#287`, also reported without mods (#284). Upstream traced it (comment of 2026-11-07 19:49) to
  Hookshot's NVN layer: `nvnTextureBuilderGetStorageSize` called with no texture builder; the next release returns 0
  there and logs `nvn: storage size of no texture builder (lr ...)` once. That fix is not on `NotRexed/Hookshot` main
  yet (checked: no commit with that log line). The data cannot say why loading the Fire Arrows at area load asks for
  that [inference: a texture of a model not otherwise loaded in Hyrule Field; rupees and heart pieces are].

Major items with an `Obj_` pick-up (`PouchGetType` Large, pouch item named in the pack): `Obj_Arrow_Fire`,
`Obj_Shield_Deku`, `Obj_Shield_Hylian`, `Obj_Armor_Goron`, `Obj_Armor_Zora`, `Obj_Ocarina_Time`, `Obj_Bombchu`,
`Obj_Bottle_Letter`, `Obj_SinkingLure`, `Obj_Mask_Amiibo0/1`, the small keys. Most majors (Boomerang, Hookshot,
Bow, bombs, Hammer, boots, songs, ...) have none: their `Item_*` pack has no collision, attention or pick-up event, so
it cannot lie in the world as it is. For those, the candidate is a chest at the check's `Hash` (variant c below).

**Does a red rupee at a heart piece save a flag?** Not answerable from the copies: no save was written after the
pickup. Every `progress.sav` under `save-backups/` and `r2-test/user/` predates it (the newest, `slot_01` of
`2026-11-07_llr-tower-before-pickup` at 17:50, has `IsGet.Obj_Heart_Piece` false and Hash 9814903750835309225 not
set, and the `r2-test/user` slots have that backup's sizes and timestamps). What the data says: the flag key is
the actor `Hash`, the `GameDataList` entry for 9814903750835309225 is `ResetTypeValue` 24 (permanent), and the 7 red
rupees the game itself places have entries of the same type (24) under their own Hashes. So the rupee should set the
heart piece's flag and stay gone [inference]; variant a checks it.

### In-game tests for Kareem

Folders `E:/OOTRemake/work/r3-census/ingame/<variant>/romfs/`, built by
`E:/OOTRemake/work/r3-census/make_ingame.py` (each file read back and checked to differ from the original only at the
heart piece; Hash 9814903750835309225, position and everything else unchanged). Each holds
`Banc/HyruleField/HyruleField_Child_Static.bcett.byml.zs` and, because the file grows past its entry by the formula,
the size table with that one entry raised (395,912 to 395,944, or 395,976 for c): so these also test a written size
table in game.

Launcher: `E:/OOTRemake/work/r3-census/Clawshot r3 freestanding test.bat <variant>`. Each run copies the save
backup `2026-11-07_llr-tower-before-pickup` into a fresh test user folder `E:/OOTRemake/work/r3-census/user-<variant>`
(his saves and install untouched), sets `HOS_FS_OVERLAY` to the variant, starts Hookshot (the `hookshot-main` build,
as round 2's launcher) and writes the log to that folder's `hookshot_log.txt`. Load the latest save (child, by the
tower), go into the Lon Lon Ranch tower where the heart piece is. In every run the log should show
`fs: OpenFile(...HyruleField_Child_Static...): from the overlay` and the same for `...rsizetable...`.

In this order:

a. **`llr-tower-red-rupee`** (control): a red rupee where the heart piece was; pick it up (20 rupees). **Then save
   (or leave the ranch so it autosaves) and quit.** Afterwards, the flag check:
   `uv run python -c "import glob; from clawshot.save import load; [print(f, load(f).is_set(9814903750835309225)) for f in sorted(glob.glob('E:/OOTRemake/work/r3-census/user-llr-tower-red-rupee/save/*/slot_*/progress.sav'))]"`
   (True in the newest slot = the rupee saved the heart piece's flag). Also: come back into the tower; it should stay
   gone. If the game fails at boot or the area does not load here, the size table is the cause: delete that
   variant's `romfs/System` folder and retry.
b. **`llr-tower-hylian-shield`**: a Hylian Shield (`Obj_Shield_Hylian`) lying there; picking it up should show its get
   message and put it in the gear menu. The save does not own one yet.
c. **`llr-tower-chest-boomerang`**: a small chest (`Obj_TBox_A_01`) at the heart piece's spot (same Hash) holding
   the Boomerang; opening it should give the Boomerang. Look at whether the chest sits on the floor, opens normally,
   and stays open after leaving and returning. This is the fallback for majors that have no pick-up actor.
d. **`llr-tower-deku-shield`**: a Deku Shield lying there (the save owns one already, so say what the pick-up does).
e. **`llr-tower-fire-arrows`**: round 2's crash case, kept for the Hookshot build with the #287 fix. On today's build
   it is expected to crash; on the fixed one, look for `nvn: storage size of no texture builder` in the log.

A crash in b or d with the same `OptimizeChangeBanc` signature means it is not the Fire Arrows' model alone but any
lone major pick-up at area load; then the chest (c) is the way for freestanding majors until the Hookshot fix.

**Question for Kareem: run a to e on the LLR-tower save (a and b first), and tell us for each what appeared, what
picking it up did, and whether it crashed.**

## Provisional choices (for review)

1. The reward boxes are a census kind (`treasure_game_reward`) rather than a field (item 2).
2. Gold Skulltulas whose spot moved inside their area are linked to the N64 name by elimination (9 of them), with
   their remake requirement listed for the world overrides, rather than left unlinked: the counts per area hold, and
   the world needs either a link or an `n64_only` for every OoT Randomizer location.
3. The three new Gold Skulltulas are named in OoT Randomizer's style (`HF GS Lone Tree`, `HF GS Wetland Grotto Crate`,
   `LLR GS Tower`), so world files can use the same names.
4. `rstb.required_size` covers only the four types whose formula fits every file and raises for the rest;
   `GameDataList` and `RSDB` are left out though they mostly fit (264), because nothing changes them yet and
   `ActorInfo` does not fit.
5. The in-game variants carry the size table with the one raised entry, as a seed will, so they also test a written
   table; variant a is the control for that.

## Cross-track posts (thread `cs-r3`)

- 18:02: item 2 (c476035): the new kind, the repeat box, `DropViewActor` for track A, `COVERED["Chest"]` for track C.
- 18:06: item 1: the three gone Gold Skulltulas by OoT Randomizer name, with evidence.
- 18:11: item 1 committed (2b3d23f): links, new names, the moved checks and the night note for track C.
- 18:12, reviewer: the repeat box stays vanilla (recorded under item 2).
- 18:15: item 3 committed (d481e07): the `rstb` API and the suggested use in the writer, for track A.

## Left open

- The in-game results of item 4 (above), including whether the red rupee saved the heart piece's flag.
- Night rules: the data's nocturnal marker covers 24 Gold Skulltulas, fewer than OoT Randomizer's night rules; the
  other logic groups were not decoded.
- The weakest Gold Skulltula links (item 1), to settle by an in-game look if the names matter (hints).
- `.ainb`, `GameDataList` and `RSDB` size formulas, when something needs to change them.

## Gates (before the handoff)

```
uv run ruff format --check                               55 files already formatted
uv run ruff check                                        All checks passed!
uv run pytest                                            145 passed, 12 skipped
OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump   11 passed, 146 deselected (27 s)
```
