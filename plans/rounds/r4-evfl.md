# Round 4, track D: event flows and gifts (cs4d)

Branch `r4/evfl`, from main `e9f9cec`. Owns `src/clawshot/formats/evfl.py`, `src/clawshot/census/` (gifts),
`src/clawshot/data/locations.toml`, `tests/test_evfl*.py`, `tests/test_census*.py`, this file and section 15 of
`plans/03-game-data.md`. Scratch scripts and decoded data: `E:/OOTRemake/work/r4-evfl/` (outside the repo).

| Item | Where | Commit |
|---|---|---|
| 1 `formats.evfl` reader and writer | `src/clawshot/formats/evfl.py`, `tests/test_evfl.py`, `tests/test_evfl_dump.py` | 79c98f0 |
| (reviewer's request) GTG chest linked to the freestanding key | `locations.toml` | f3fb5ef |
| 2 gift census, definitions, OoT Randomizer links | `src/clawshot/census/gifts.py`, `definitions.py`, `write_locations.py`, `locations.toml`, `tests/test_census_gifts.py`, `tests/test_census_dump.py`, `tests/test_world_census.py` | 93492a3 |
| 3 changing a gift's item: finding and in-game test folders | this file, `03-game-data.md` section 15, `E:/OOTRemake/work/r4-evfl/ingame/` | this file's commit |

## Item 1: `clawshot.formats.evfl`

**Every one of the 914 flows in the dump writes back byte-identical** (653 flowcharts, 261 timelines), and reads back
to the same tree (`tests/test_evfl_dump.py`).

Written from the files themselves and the ZeldaMods wiki's BFEVFL page (https://zeldamods.org/wiki/BFEVFL, revision
11752, a description of the structures, no code). The GPL `evfl` library's source was not read; nothing of it is in
the repository. How the layout was found: scratch scripts in `E:/OOTRemake/work/r4-evfl/` parse the relocation table
(which lists every pointer field, so it shows each structure's size and pointer slots), map every structure to its
offset (`layout.py`) to learn the writer's order, and compare the writer's bytes against each file (`rt.py`, first
difference with the structure it falls in). Two passes: the first gave 465 of 914 identical; the cause (a switch's
cases come before its parameters) fixed, 914 of 914.

The game writes version 0.4.0.0, which differs from the wiki's description (module docstring has the details):

- events are 0x30 bytes, with two more types: 5 calls an entry point and branches on the value it returns, 6 returns
  a 32-bit value (583 such events; named `SubFlowSwitchEvent` and `ReturnEvent` here, the official names are unknown);
- entry points can carry variables (5 in the game: an 8-byte value, count, type); an entry point without them still
  owns 0x18 zero bytes;
- String, Argument and Actor identifier items hold pointers to strings that follow the item;
- the string pool is sorted by each string's bits read from the last byte's lowest bit (the order the radix-tree
  dictionaries compare in); the relocation table lists every array pointer even when null, an optional object's
  pointer only when set;
- a file holds exactly one flowchart or one timeline; no timeline has oneshots; container items use types 0-5, 9 and
  12 only. The reader refuses anything else (oneshots, other item types, both or neither block) rather than guess a
  layout no file shows.

API: `evfl.read(bytes) -> EventFlowFile`, `evfl.write(EventFlowFile) -> bytes` (decompressed; `zsdic` compresses),
plain dataclasses (`Flowchart`, `Actor`, the event classes, `EntryPoint`, `Timeline`, ...), parameters as `dict`
with typed values (`Argument`, `FloatArray`, `ActorIdentifier`, `int`, `bool`, `float`, `str`).

Tests: `tests/test_evfl.py` (synthetic files with every event type, every parameter type and entry point variables,
and a timeline: read back to the same tree and bytes; a longer item name moves the rest of the file and reads back;
the radix search finds every dictionary name at its index and no other; refusals for a bad magic, version, size,
block count, item type, triggers that don't pair with clips, a duplicate dictionary name, a non-parameter value).

## Item 2: the census of gifts

`clawshot.census.gifts.scan_gifts(romfs) -> list[Gift]`: **148 gifts** (96 `npc_gift`, 26 `event_gift`, 26 `song`).

**How a gift is found.** Every item is given by one action, `PouchSystemActor.EventTriggerAddOrRemovePouchContent`
(`Actor` = the item, `Num` the count). Instead of a hand list of wrappers, the census computes which entry points
give an argument: an entry point gives its argument `A` when an event reachable from it gives `Argument(A)`, directly
or by passing it to another giving entry point; repeated to a fixed point over all flows. That finds 64 wrapper entry
points (`GetPouchContent:*`, 25 `Dm_SY_GetInEvent:*`, `NpcCommon:NpcCommon_HandOver_*`,
`GatheringTokenGold:TakenReward_*`, `SimpleShop:*`, `MiniGame_FrogTenors:MushiToriGame`, the chest flows, ...). A gift
is a step that passes a literal item name to the action or to such a wrapper. Left out: steps that take an item
(`Num` < 0: 22 trade hand-ins, planted beans), the business scrubs' sale flows (the scrubs are census `scrub`s with
their offers in their placements) and the DreamWorld boss-rush flows (D12).

**Flows the game loads.** 13 flows exist twice, `X.bfevfl.zs` and `X.110.bfevfl.zs`;
`Event/EventFlow/EventFlowFileEntry.Product.110.byml.zs` lists them (`Versions: {X: "110"}`), so the census reads the
`.110` file for those [inference that the game loads the listed version; the five medallion flows, Dampé's flow and
the horse race are among them]. 640 flowcharts after that.

**Ids and fields.** A gift is `<flow>/<event>` (rule 5: the event flow and node). `Gift` also has the file read, the
entry points the step is reached from, the wrapper called, the parameter holding the item, the vanilla item and the
area. Kind: `song` for `Item_Melody_*`, `event_gift` in a cutscene flow (`Dm_*`), `npc_gift` otherwise. **Area** is
the Banc folder whose placements start the flow (an actor named like the flow, as NPCs run their own flows, or an
actor parameter naming one of the flow's `EventSetting` rows), when exactly one does; 60 of 148 have one, the rest
`""` (cutscenes are started from `Logic` graphs and other flows, which the census does not follow).

**Definitions.** `locations.toml` gets the 148 gifts after the 477 placement checks (625 in all); `Definition.id` is
now `int | str`. `write_locations` writes them, keeping hand-edited names and links, and reproduces the committed
file byte for byte. `tests/test_census_dump.py` checks the file against both censuses.

### Against OoT Randomizer

OoT Randomizer (`LocationList.py` at `526b4c8d`, no Master Quest): NPC 71, Song 12, Cutscene 9, Boss 9 (the
spiritual stones and medallions, which the remake also gives in cutscene flows).

| OoT Randomizer type | checks | linked | not linked |
|---|---:|---:|---|
| Song | 12 | 12 | |
| Boss | 9 | 9 | |
| Cutscene | 9 | 8 | Gift from Sages (no item in OoT Randomizer either) |
| NPC | 71 | 50 | 9 cows (n64_only, D11); LH Sun and LH Underwater Item (placed pick-ups, not flow gifts); ZR Frogs Zeldas Lullaby, Eponas Song, Sarias Song, Suns Song, Song of Time and Frogs in the Rain; LH Loach Fishing; Market Bombchu Bowling Bomb; Market Treasure Chest Game Salesman; Kak Granny Buy Blue Potion |

93 gift steps carry the 79 names: where the game gives one check in several steps (a progressive upgrade picks
Medium or Large, two code paths for one prize), every step is linked, as chest copies are. Applied by the throwaway
`E:/OOTRemake/work/r4-evfl/link_gifts.py`; `write_locations` keeps them. Each link's basis:

| OoT Randomizer name | gift step(s) | basis |
|---|---|---|
| Song from Impa, Malon, Saria, Royal Familys Tomb, Ocarina of Time, Windmill; Sheik in Forest, Crater, Ice Cavern, at Colossus, in Kakariko, at Temple | `Dm_MelodyGet_{Zelda,Epona,Saria,Sun_03,Time,Storm,Forest,Fire,Water,Spilit,Shadow,Shine}` (the step calling `GetPouchContent`) | the song item; one flow per song |
| Queen Gohma, King Dodongo, Barinade | `Dm_Kokiri_0130/Event22`, `Dm_DeathMtTrail_0025/Event26`, `Dm_ZoraFountain_0030/Event3` | the stone given; the only step giving it |
| Phantom Ganon, Volvagia, Morpha, Bongo Bongo, Twinrova, ToT Reward from Rauru | `Dm_Awake_{Forest,Fire,Water,Shadow,Spirit}_Get`, `Dm_SageRoom_0005/Event48` | the medallion; the only step giving it |
| LW Gift from Saria, HF Ocarina of Time Item | `Dm_Kokiri_0155/Event68`, `Dm_MelodyGet_Time/Event70` | Fairy Ocarina, Ocarina of Time |
| ToT Light Arrows Cutscene | `Dm_TimeTemple_0130/Event85` | Light Arrows |
| HC, DMT, DMC, ZF, Colossus, OGC Great Fairy Reward | `Dm_FairyFountain_{Power,Din,Wisdom,Frore,Nayru,Courage}` | linked by place, not item: the remake swapped Din's Fire (DMT) and the magic meter (HC) (`03-game-data.md` section 9, seen in game) |
| HC Malon Egg, HC Zeldas Letter | `Goto_HyruleCastle/Event35`, `Dm_HrlCastle_0050/Event59` | Weird Egg, Zelda's Letter |
| LW Skull Kid, LW Ocarina Memory Game | `Npc_SkullKid_Child/Event71`, `Npc_SkullKid_Child_02/Event24` | heart piece from each Skull Kid flow; the second is the ocarina session (`PlayOcarinaForSkullKidSession`) |
| LW Target in Woods | `Dm_LostWood_0040/Event30`, `/Event17` | bullet bag Medium/Large |
| Deku Theater Skull Mask, Mask of Truth | `LostWood_ScrubForestStageElder_SkullMaskFirst/Event29, 32`, `..._TrueMaskFirst/Event2, 31` | stick and nut capacity, Medium/Large |
| Trade sequence: LW Trade Cojiro, LW Trade Odd Potion, GV Trade Poachers Saw, DMT Trade Broken Sword, ZD Trade Prescription, LH Trade Eyeball Frog, DMT Trade Eyedrops, Kak Anju Trade Pocket Cucco, Kak Granny Trade Odd Mushroom | `Npc_Hylia_017_Adult/Event100, 116`, `Npc_Kokiri_Fado_Adult/Event123`, `Npc_Hylia_012_Adult/Event58`, `Npc_Goron_Biggoron_Adult/Event232`, `Npc_Zora_KingZora_adult/Event131, 87`, `Npc_Hylia_045_Adult/Event26, 27, 45`, `Dm_DeathMtTrail_0050/Event21`, `Npc_Hylia_049_Adult/Event234`, `Npc_Hylia_053_Adult/Event167` | the item handed over; entry points named `SubEvent_GetSwordBigGoron_StepNN`; areas match |
| DMT Biggoron, Kak Anju as Adult | `Npc_Goron_Biggoron_Adult/Event123`, `Npc_Hylia_049_Adult/Event264` | Biggoron's Sword, Pocket Egg |
| Market and Kak Shooting Gallery Reward | `MiniGame_HitTarget/Event241, 378` (`Child_Reward`), `/Event381, 242` (`Adult_Reward`) | bullet bag / quiver |
| Market Bombchu Bowling First Prize, Second Prize, Bombchus | `MiniGame_BombchuBowling/Event304, 306`, `/Event143`, `/Event309` | bomb bag, heart piece, bombchus |
| Market Lost Dog, Market 10 Big Poes | `SubEvent_FindRichard/Event16`, `Npc_Hylia_048_BottleShop/Event329` | heart piece; bottle |
| LLR Talons Chickens, Kak Anju as Child | `Minigame_FindOutCucco/Event23`, `Minigame_CatchCucco/Event181` | milk bottle; bottle |
| Kak Man on Roof | `Npc_Hylia_001_Adult/Event4` | the only Kakariko NPC giving a heart piece (entry `Get_HeartPiece`) |
| Kak 10, 20, 30, 40, 50, 100 Gold Skulltula Reward | `GatheringTokenGold/Event398, 75, 194, 200, 219, 215` | `03-game-data.md` section 4, example 3; 100 = the `_200Rupee` wrapper |
| GC Darunias Joy, Rolling Goron as Child, as Adult, Medigoron | `Dm_Goron_0030/Event127`, `Npc_Goron_006_Child/Event58, 92`, `SageOfFire/Event18`, `Npc_Goron_Medigoron_Adult/Event11` | Goron Bracelet; bomb bags; Goron Tunic from Darunia's son (`Step02_DaruniaJr_*`); Giant's Knife |
| ZR Magic Bean Salesman, ZR Frogs Ocarina Game | `SimpleShop/Event182`, `MiniGame_FrogTenors/Event384` | entry `Sub_SimpleShop_Buy_MagicBean`; heart piece in `PlayOcarinaForFrogMiniGame_Melody` |
| ZD Diving Minigame, ZD King Zora Thawed | `MiniGame_Diving/Event21` (`FirstClear`), `SageOfWater/Event242` | Silver Scale; Zora Tunic in `KingZora_IsMelted_Ice` |
| LH Child Fishing, LH Adult Fishing | `MiniGame_Fishing/Event573, 821`, `/Event579, 822` | by item (heart piece, Golden Scale): both pairs sit in `GiveReward`, the data does not say which age |
| LH Lab Dive | `Npc_Hylia_045_Child/Event113` | heart piece in the lake scientist's `DivingChallenge_Common` (rows `Npc_Hylia_045_{Child,Adult}DivingChallenge`) |
| GF HBA 1000 Points, 1500 Points | `Minigame_HorsebackArchery/Event322`, `/Event320, 319` | heart piece; quiver |
| Hideout Gerudo Membership Card, Wasteland Bombchu Salesman | `Dm_Gerudo_0025/Event294`, `Npc_Hylia_044_Adult/Event3` | Gerudo card; bombchus via `SimpleShop` |

The 55 gift steps without a link: 13 `Dm_SY_Ocarina` steps (the shared song-learning playback, below); Scarecrow's
Song (`Npc_Bonooru/Event159`; OoT Randomizer has no location for it); two Master Sword grants (`DoorOfTime`, the
final battle); the Amiibo pouch (`Goto_HyruleCastle/Event205`); the hatching cuccos (`Goto_HyruleCastle/Event20`,
`SubEvent_GetSwordBigGoron/Event82, 113`); 25 rupee prizes (repeat or lesser prizes of minigames, Kokiri children,
the running man, Skull Kid's other rounds, the Poe buyer, the mask salesman); the Zora shop's tunic sale
(`Npc_Zora_011_Shop_Adult/Event2`); and these, to look at:

- `Npc_Hylia_Dampe_001/Event628` (heart piece): OoT Randomizer's `Graveyard Dampe Gravedigging Tour`, but that one is
  typed `Collectable` (a freestanding item there), so the world test would reject a gift linked to it. **For track
  B/Claude: link it once the world types it as an NPC gift, or leave it with the heart-piece anchor.**
- `MiniGame_FrogTenors/Event75, 161` (heart piece, entries `FrogMiniGame_RetryFlow`, `..._Insectrepellent`) and
  `Event76, 162` (blue rupee): the frogs' bug-eating game. Whether it is the remake's `ZR Frogs in the Rain` is open.
- `Npc_Kokiri_001_Shop_Child/Event116, 117` (Deku Shield, entry `present_DekuSheld`): the Kokiri shop gives a Deku
  Shield as a present [inference from the entry name]: a remake-only check?
- `Npc_Hylia_020_Shop_Child/Event171` (empty bottle, entry `Item_Bottle_TutorialEvent_Talk`) and
  `Npc_Hylia_023_Shop_Child/Event51` (Mask of Truth, `Pay_usagi`): a remake-only bottle in the Market, and the mask
  shop's Mask of Truth.

**Questions for Kareem.** **Is there a Market NPC (the bug or potion shop, `Npc_Hylia_020_Shop_Child`) who gives an
empty bottle, and does the Kokiri shopkeeper give a Deku Shield for free at some point?** Both would be remake-only
checks. **In Zora's River, do the frogs give a heart piece for a bug-eating game, and is the Song of Storms heart
piece still there?**

## Item 3: changing a gift's item

**The item is one string parameter of the gift step** (`Gift.param`: `ActorName`, `ReveiveItem` (sic), `Actor`,
`TakenRewardActor`, ...). Changing it is: read the flow, set the parameter, write the flow (`formats.evfl`), compress
it with its dictionary, and raise its size-table entry when the new size needs it (`.bfevfl` entries are the size
rounded to 32 + 272, `formats.rstb.required_size`). The rest of the file moves with the string; nothing else changes.

What follows the item name [inference from the flows; to check in game]: every wrapper ends in
`Dm_SY_GetInEvent:*` or `GetPouchContent:*`, which play the get animation and open the get window by actor name, so
the model and the get text should follow the new item. What does not follow: the NPC's own lines before and after
(message ids such as `EventFlowMsg/Npc_Hylia_Talon_Child:Talk_08`, in `Mals/`) still name the vanilla item, and any
flag the flow sets stays (the cucco game sets `IsClear_Minigame_FindOutCucco`, which is what stops a repeat, not the
item).

**Songs are given twice.** Every `Dm_MelodyGet_*` flow first calls `Dm_SY_Ocarina:LearningOcarinaPlayAuto` (or
`...ForSeek`), which switches on the game's current melody (`EventQueryMelodyTypeForNormal`) and adds that song
directly (the 13 `Dm_SY_Ocarina` steps), then gives the song again by name through `GetPouchContent`. So a song
location given another item would still teach its vanilla song through the playback: a seed has to change or skip
that call too. The playback steps are shared by all songs, so they are not locations of their own.

**The in-game example** (outside the repo, `E:/OOTRemake/work/r4-evfl/ingame/`, built by
`E:/OOTRemake/work/r4-evfl/make_gift_test.py`, which checks that each written flow reads back equal to the game's but
for the one parameter): `LLR Talons Chickens`, flow `Minigame_FindOutCucco`, step `Event23`
(`NpcCommon:NpcCommon_HandOver_NpcToPlayer_NoDisplay`, `ReveiveItem` = `Item_Bottle_Milk`):

| Folder | `ReveiveItem` | why |
|---|---|---|
| `talon-heart-piece/romfs` | `Obj_Heart_Piece` | an item this same wrapper hands over in the game (Bombchu Bowling's second prize) |
| `talon-boomerang/romfs` | `Item_Boomerang` | a major item no NPC hands over in the game |

Each holds only `Event/EventFlow/Minigame_FindOutCucco.bfevfl.zs`: the decompressed size stays 200,408 bytes (the
vanilla name stays in the pool, used by the bottle refill `Event304`), so the size-table entry (200,688) fits and no
table is written.

**For Kareem (no seed writes flows yet; this checks that a written flow loads and gives the new item).** From a fresh
copy of `E:/OOTRemake/work/save-backups/2026-11-07_llr-tower-before-pickup` (child Link at Lon Lon Ranch; the save
copies have Talon back at the ranch, `HavePlayedEvent.Dm_HrlCastle_0020` set, and the cucco game not cleared, no
Boomerang), with `HOS_FS_OVERLAY` at one folder's `romfs`:

1. The log shows `fs: OpenFile(...Minigame_FindOutCucco.bfevfl.zs): from the overlay` (when the game first needs the
   flow; at the latest when talking to Talon).
2. In the ranch house, talk to Talon and play his cucco game (pick out his super cuccos, as on N64). On
   winning, instead of the milk bottle, Link gets **a Heart Piece** (first folder: the heart-piece get animation and
   text, the heart container quarter added) or **the Boomerang** (second folder: Boomerang model and get text, then in
   the item menu and usable).
3. Talon's lines probably still talk about milk [inference; the text was not read]. Talking to him again afterwards
   should not give the item again (the clear flag).

## Provisional choices (for review)

1. **Gift id `<flow>/<event>`**, a string next to the placement Hashes (`Definition.id: int | str`). The entry point is
   not part of the id: an event belongs to one flowchart, and some gift steps are reached from several entries.
2. **Kinds by flow**: `event_gift` in a `Dm_*` flow, `npc_gift` otherwise, `song` for songs. OoT Randomizer's types
   don't map one to one (Zelda's Letter and the Gerudo card are given in `Dm_*` cutscenes), so the world test accepts
   both gift kinds for its NPC type.
3. **Every literal give step is a location**, repeat prizes included; only the generator's links decide what is
   shuffled. Rupee prizes could be left out of the definitions instead; they are kept so the census is complete and a
   person can link one if it turns out to be a check.
4. **`tests/test_world_census.py` edited** (no round-4 owner; posted 20:13): NPC, Song, Cutscene and Boss are now
   covered types with the gift kinds, and an empty gift area skips the area comparison. Pending went from 140 to 153.
5. The GTG chest link (reviewer's request) is committed alone; `test_world_census.py::test_links_match_kind_and_area`
   fails until the world drops `remake.toml`'s `n64_only` for `Gerudo Training Ground Freestanding Key` and types it
   as a chest (posted 20:09).

## Cross-track posts (thread `cs-r4`)

- 20:02: `formats.evfl` on the branch, 914 of 914 byte-identical.
- 20:09: GTG link done (f3fb5ef); the world-side change it needs.
- 20:13: gift census (93492a3), the gift ids and kinds, the `test_world_census.py` edit.

## Left for later

- No seed writes flows yet. A gift seed needs, per gift: the step's parameter, the song playback for songs, the
  message text if the NPC's lines should match, and an in-game check per wrapper family (the example covers
  `NpcCommon_HandOver`).
- Areas for the 88 gifts without one need the `Logic` graphs that start cutscenes.
- The gifts listed to look at above, and Dampé's digging heart piece's type in the world.

## Gates (before the handoff, on 93492a3; the commit after it changes only plans)

```
uv run ruff format --check                                  70 files already formatted
uv run ruff check                                           All checks passed!
uv run pytest                                               1 failed, 183 passed, 19 skipped
OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump      18 passed, 185 deselected
```

The one failure is `tests/test_world_census.py::test_links_match_kind_and_area`: "linked from the census and marked
n64_only: ['Gerudo Training Ground Freestanding Key']", from the reviewer-requested link (f3fb5ef); no other link is
wrong (checked by listing every kind or area mismatch: only that one). It clears when the world drops that
location's `n64_only` in `remake.toml` and types it as a chest (posted 20:09); before f3fb5ef the test file passed
(4 passed). The dump run includes 914 of 914 flows byte-identical and 148 gifts (26 event_gift, 26 song, 96
npc_gift) agreeing with `locations.toml`.
