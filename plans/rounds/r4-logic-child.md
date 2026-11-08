# Round 4, track A: remake logic, child areas (cs4a)

Branch `r4/logic-child`. Owns `src/clawshot/world/load.py` (item 1 only), `src/clawshot/data/world/remake.toml`,
`src/clawshot/data/world/remake/child_*.toml`, `tests/test_world_remake*.py`, this file and section 12 of
`plans/03-game-data.md`. Scratch scripts (read only on the dump) and decoded data: `E:/OOTRemake/work/r4-logic-child/`.

## Item 1: overrides in several files (9c4abf0)

`load_spec` applies `remake.toml`, then every `remake/*.toml` sorted by name (`load.apply_overrides`). Tables:
`[locations]` (as before, plus `region` to move a location), `[regions]` (a region the translation lacks),
`[exits."<region>"."<target>"]` and `[events."<region>"."<event>"]` (`rule` with `was`, or with `new = true`),
`[key_counts]`. One location, exit, event, region or key count set in two files stops the build, naming both files.
Regions are added before anything else is applied, so a file may use a region from a file sorted after it. Format
written into `plans/04-world-format.md` ("Overrides"; that file had no round 4 owner, the format change is this
item's). Tests: `tests/test_world_remake.py` (files applied in order, a region from a later file, the same location
or exit in two files, a stale `was`, `new` on an existing exit, unknown tables and fields, missing source). Posted on
`cs-r4` at 19:52.

## Item 2: the Deku Tree (`remake/child_deku_tree.toml`)

Evidence: Kareem's round 3 seed 3 report (`00-roadmap.md`, "Round 3 result"); Nintendo Life, "Great Deku Tree
walkthrough" (Switch 2, 2026-11-05,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-great-deku-tree-walkthrough-switch-2); the placement files
(`InsideTheDekuTree_Static`/`_Dynamic`, listed by `E:/OOTRemake/work/r4-logic-child/actors.py`; output
`deku_all.tsv` there). Rooms are the actors' `DefaultDungeonRoomIndex`; heights are Banc `y`.

| Room | What the data has | What the guide says |
|---|---|---|
| 0 lobby | 1F web `Obj_InsideTheDekuTree_SpiderWeb_A_01` at y 100; map chest y 108 (2F); three `Enemy_Skullwalltula` at y 113-116 on the wall above the map chest; Skulltulas at y 127 (3F) | 2F by ladder or vines; the Slingshot shoots down the Skulltulas that block the vine wall to 3F; the basement is entered by jumping from 3F into the 1F web |
| 1 | `Enemy_Scrub_Deku`, shutter | reflect the nut with the shield |
| 2 Slingshot room | `FallingFloor_A_01/02/03` (y 110, at the entrance), `Obj_EyeSwitch_A_02` (y 114) and `FallingLadder_A_01` (y 116) above the entrance, Slingshot chest y 112, side chest y 116 | the floating platform breaks under Link; vines up to the Slingshot chest; shoot the switch above the entrance door to drop it and escape; the side chest is up the vines by the Slingshot chest |
| 3 compass room | compass chest y 120, side chest y 126, Gold Skulltula y 121, `Obj_StepSwitch_A_02`, three `ElevatorLift` platforms | floor switch raises three platforms to the alcove (Gold Skulltula) and to the compass chest; the side chest through a vent |
| 4-11 basement | eye switch in room 5, water room 6, torches 7, webs 8, scrubs 9, boss 10 | as N64 (OoT Randomizer's basement rules hold) |

Overrides (each with `source` in the file):

| Change | Rule |
|---|---|
| new region `Deku Tree Top Floor` (3F and the compass room) | entered from `Deku Tree Lobby` with `can_use(Slingshot)`; back down `True` |
| `Deku Tree Compass Chest`, `Compass Room Side Chest`, `GS Compass Room` | moved to `Deku Tree Top Floor`, rules unchanged |
| `Deku Tree Top Floor` -> `Deku Tree Basement` (new) | `here(is_adult or can_child_attack or Nuts)`, OoT Randomizer's condition for the way down (Deku Tree.json:20) |
| `Deku Tree Lobby` -> `Deku Tree Basement` | was `deku_tree_shortcuts or here(...)`, now `deku_tree_shortcuts` (the basement opens from 3F only) |
| `Deku Tree Slingshot Room` -> `Deku Tree Lobby` (new; OoT Randomizer's room has no exit) | `can_use(Slingshot) or can_use(Bow)` |

Checked and unchanged: the Slingshot room entry `here(has_shield)` (the scrub); both Slingshot room chests `True`
after the drop; the map chest `True`; the basement back room (an eye switch: Slingshot or Bow, and a fire source),
the ledge, the B2 web (torch and stick), the boss door (`has_shield`: the 2-3-1 scrubs), Queen Gohma (stun with
the Slingshot or nuts, then the sword).

Tests (`tests/test_world_remake.py`): on round 3's slice (Kokiri Forest, Lost Woods, Deku Tree, goal Queen Gohma),
the vanilla placement is beatable and the vanilla placement with the Slingshot and the basement chest's item swapped
(seed 3's case) is not; holding every other vanilla item of the slice, the compass chest, the compass room Gold
Skulltula and the basement chest are out of reach without the Slingshot and in reach with it, and the map chest and
both Slingshot room chests are in reach without it.

**Getting out of the Slingshot room without the Slingshot.** The exit in logic does not change what is reachable
(the lobby is reached before the room), so it only records the trap. Nothing in the data shows a way out besides the
eye switch: the only "return to entrance" flow is the Wallmaster's (`Enemy_Wallmaster_ReturnToEntrance`), and room
2's only other actors are the vines, a Skullwalltula and the chests. Farore's Wind would work, but no child holds it
this early. Against an easy way out: the remake keeps one save with BotW-style autosave and resumes at the last
save point (Eurogamer, https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2), so a reload may
put Link back in the room; and with one save file a trap would end the seed, not just cost a reset.

- **Kareem: in the Slingshot room without the Slingshot (seed 3), how did you get out? Does saving and quitting (or
  a game over) and continuing put Link at the Deku Tree's entrance, as on N64?**
- If it does, the room is no trap: the rules above stand (enter with a shield, the chests open, reload to leave).
- If it does not, proposal: the room's entry asks for the Slingshot too (`here(has_shield) and can_use(Slingshot)`
  on `Deku Tree Lobby` -> `Deku Tree Slingshot Room`), so the logic never sends a player in without it; a seed then
  never puts the Slingshot in either of the room's chests, and the vanilla-placement test must accept that
  (vanilla is then out of logic). A player can still walk in early, so the better fix is a placement patch that
  leaves the ladder down (`Obj_InsideTheDekuTree_FallingLadder_A_01`) or the platform whole, for an in-game test.
- **Kareem: can the Boomerang (child), or the Bow or Hookshot (adult), clear the Skullwalltulas on the lobby's vine
  wall to 3F?** Until then only the Slingshot opens 3F, so an adult never reaches 3F or the basement in logic.

## Items 3 and 4: the child areas

Every area of item 3 has a file `src/clawshot/data/world/remake/child_<area>.toml` (Deku Tree: item 2). Each rule of the
translated files that a child evaluates (and, in the five dungeons, every rule) was checked against remake guides
(Switch 2, cited per entry; facts only), `plans/03-game-data.md`, the census and the placement files. The research
ran in eight parallel sub-agents under this track, one per area group, on one brief
(`E:/OOTRemake/work/r4-logic-child/brief.md`); I reviewed each file and set the cross-area rules. Per-rule notes,
longer than the sections below, are in `E:/OOTRemake/work/r4-logic-child/findings/<area>.md` (outside the repo);
the sections below are condensed from them and from the committed files.

**Decision rule (provisional, for review):** a rule became stricter where a remake source shows the N64 way gone or
a new obstacle; looser only where a source shows the easier way works in the remake; unclear or silent sources left
OoT Randomizer's rule (counted as checked, unchanged). Every change has a `source`. Shared rules (one rule for both
ages) were changed only in their child part, flagged for track B; the five dungeons are wholly this track's.

**Cross-area rules** (decided here, applied in each area's file; posted on `cs-r4`):

- *Time flows only after Link has met Zelda* (Eurogamer, https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2).
  Event `'Time Flows'` in `HC Garden` (child); every child rule with `at_night` / `at_dampe_time` asks for it. Adult
  night rules are track B's. A world-wide gate in the rule compiler would be cleaner (rules.py is no track's): a
  reviewer's call.
- *Grottos need no Stone of Agony* (same article; data: `AgonyStoneReactArea` only at grotto Gold Skulltulas).
  `can_open_bomb_grotto` -> `can_blast_or_smash`, `can_open_storm_grotto` -> `can_play(Song_of_Storms)`, exit by
  exit; where the data shows a storms cover (`Land_Kokiri_HidingHoleCover_A_01` with an `EventProxyRequestActor`)
  on an N64 bomb grotto, the Song of Storms (HF tektite grotto, Kak ReDead grotto, SFM Wolfos grotto).
- *The first Great Fairy must be Death Mountain Trail's or Hyrule Castle's* (games.gg,
  https://games.gg/the-legend-of-zelda-ocarina-of-time-2026/guides/ocarina-of-time-remake-great-fairy-locations-rewards-and-costs).
  Event `'Great Fairy Met'` at those two fountains; ZF's reward asks for it (DMC, Colossus, OGC: posted for track B).
  Fees (25 to 500 rupees, rising per fairy met) are not modelled: there is no rupee logic. **Superseded by item 6**:
  the data says only Din's fairy comes without Din's Fire, and the fees are fixed and modelled as wallets.

| Area | Changed entries | Open questions |
|---|---:|---:|
| Inside the Deku Tree (item 2) | 7 | 2 |
| Kokiri Forest | 5 | 3 |
| Lost Woods | 3 | 5 |
| Sacred Forest Meadow | 4 | 3 |
| Hyrule Field | 16 | 6 |
| Lon Lon Ranch | 1 | 2 |
| Market | 15 | 3 |
| Hyrule Castle | 3 | 2 |
| Temple of Time | 1 | 1 |
| Kakariko Village | 12 | 5 |
| Graveyard | 8 | 3 |
| Death Mountain Trail | 7 | 5 |
| Death Mountain Crater | 1 | 0 |
| Goron City | 1 | 3 |
| Zora's River | 5 | 3 |
| Zora's Domain | 2 | 2 |
| Zora's Fountain | 2 | 0 |
| Lake Hylia | 3 | 1 |
| Dodongo's Cavern | 20 | 7 |
| Inside Jabu-Jabu's Belly | 2 | 5 |
| Bottom of the Well | 4 | 5 |
| Ice Cavern | 3 | 3 |
| **total** | 125 | 69 |

### Kokiri Forest (`child_kokiri_forest.toml`)

Sources: Eurogamer 17 changes, https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, Nintendo Life
walkthrough hub, https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake, Nintendo Life
Gold Skulltulas, https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2,
Game8 100% walkthrough, https://game8.co/games/Zelda-Ocarina-of-Time/archives/480402, Zelda Central remake guide
(Kokiri Forest, Lost Woods and Sacred Grove, adult Sacred Grove, secret grottos, 100% checklist),
https://zeldacentral.com/games/ocarina-of-time-remake/walkthrough/kokiri-forest/, z64central Switch 2 page
(screenshots only), https://z64central.com/switch-2/, placement data (actors.py KokiriForest), plans/03-game-data.md
sections 5, 9-11, census.

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|`Kokiri Forest -> KF Storms Grotto`|`can_open_storm_grotto` -> `can_play(Song_of_Storms)`|Main's grotto decision (entrances visible, Agony stone is the Echo Gem); cover 389687166017056250 at (-52,122,-63) with EventProxyRequestActor 4820144275644776441, the storms pattern.|
|`KF Storms Grotto Chest`|`True` -> `is_adult or has_shield`|Grotto holds the Deku Tree boss-door scrub trio (manager 13177382922536876309); last scrub links chest 14818888396401495482; OoTR trio rule `has_shield`. Shared; adult kept. Open 1.|
|`KF Storms Grotto -> Fairy` (event)|`(can_summon_gossip_fairy ...) or (can_use(Sticks) ...)` -> `False`|No Gossip Stone or Animal_ButterflyToFairy in the grotto room; KF has no butterflies; nearest stone 15788731894432615343 stands outside.|
|`KF Storms Grotto -> Fish` (event)|`has_bottle` -> `False`|No Animal_Fish_* or FishAnchor anywhere in the KokiriForest Banc; the room holds the scrub trio and chest.|
|`KF GS Know It All House`|`... (at_night or gold_skulls_ignore_daytime) ...` -> `... ((at_night and 'Time Flows') or gold_skulls_ignore_daytime) ...`|Main's 'Time Flows' decision (clock starts after meeting Zelda); GS 17067594426901953848 Nocturnal, child file only; NL GS #3, Zelda Central GS #16: night.|

Checked, unchanged: Mido event `Showed Mido Sword & Shield` and the child part of `KF Outside Deku Tree` (sword and
shield needed; NL hub, Zelda Central, Game8); `KF Kokiri Sword Chest` `is_child` (crawl hole, ladder, ledge; NL, Zelda
Central, Game8); `KF GS Bean Patch` (bottle bug in soil behind shop; NL GS #1; not Nocturnal); the four `KF Midos ...
Chest` `True` (four chests, census-linked); `KF Shop Item 1..8` `True` (census links all eight); house and shop exits
`True` (Kokiri doors, seamless interiors); `Lost Woods` `True` (open from the start; NL); `LW Bridge From Forest`
`can_leave_forest` (guard until the Deku Tree; Zelda Central, Game8); KF `Fairy` (two Gossip Stones, bean soil);
`Deku Stick Drop` (Deku Babas past Mido; Zelda Central; Boomerang part unconfirmed); `Deku Tree Lobby` and return exits
(no contrary evidence); grotto `Bugs` (no evidence either way; open 2) and grotto exit back `True` (bean flower
6558321208438184222). Low priority, unchanged: freestanding rupees and hearts, wonder items, pots, Saria's hearts, shop
wonder item, grotto beehives (no beehive actor in the Banc). Adult-only rules left to track B: KF Bean Platform rupees,
`KF GS House of Twins`, `KF Links House Cow` (n64_only in remake.toml), `Deku Nut Drop`.

Open (in-game check for Kareem):

1. **Is the grotto chest the scrub trio's reward, and is a shield needed?** Child with Song of Storms, once without a
   Deku Shield: up the ivy by Mido's house, play Storms at the cover (-52,122,-63), drop in. Chest there before the
   scrubs fall? Slingshot or sword alone enough? Rule: `KF Storms Grotto Chest`.
2. **Does any grass in the KF grotto give a bug?** Cut every grass patch in the storms grotto room. Rule: event `Bugs`
   (KF Storms Grotto).
3. **Do the Deku Babas past Mido drop nuts for a child?** Hit a Baba's head on the path to the Deku Tree (Game8 reports
   nuts from Babas inside the tree). Would loosen `Deku Nut Drop` (adult-only in OoTR; shared, adult part track B's).

Remake-only checks noticed / for other tracks:

- Remake-only chest 4349272251343787229 (TBox_Rupee_Purple) at (-132,124,-16), 9 m above the stick-bag Business Scrub
  (Item_StickBag_Medium; child 182031956235860994, adult 7488448334396031424); no OoTR location for either.
- Track B: the scrub trio and chest are in the adult file too (scrub 9098168071222924162 links the chest), so an adult
  likely needs the Hylian Shield; the adult part was left `True`.
- Nocturnal check agrees with OoTR: Know-It-All GS (child, night), Twins GS (adult, night, Hookshot; NL GS #2); the
  bean patch GS is not night in either.

### Lost Woods (`child_lost_woods.toml`)

Sources: Nintendo Life Lost Woods path guide,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-lost-woods-path-guide-maze-directions-switch-2, Nintendo
Life heart pieces, https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2, Nintendo
Life Gold Skulltulas,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2, Nintendo Life
Happy Mask Shop,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-happy-mask-shop-quest-mask-of-truth-switch-2, Game8 100%
walkthrough, https://game8.co/games/Zelda-Ocarina-of-Time/archives/480402, Zelda Central remake guide (Lost Woods and
Sacred Grove, last child errands, Kokiri Forest to Hyrule Field, adult Sacred Grove, business scrubs, equipment
upgrades, mask guide, 100% checklist),
https://zeldacentral.com/games/ocarina-of-time-remake/walkthrough/lost-woods-and-sacred-grove/, Eurogamer 17 changes,
https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, z64central Switch 2 page (screenshots),
https://z64central.com/switch-2/, placement data and event flow (actors.py LostWood), census.

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|`LW Beyond Mido -> SFM Entryway`|`True` -> `is_adult or at('HC Garden Skippable Locations', is_child)`|NL path guide: no exit at the maze's end before meeting Zelda; OoTR's own met-Zelda test (Song from Saria). Transition 10348290711387667549. Shared; adult kept. Open 1.|
|`LW Near Shortcuts Grotto -> Fairy` (event)|`(can_summon_gossip_fairy ...) or (can_use(Sticks) ...)` -> `False`|Room under the boulder (28,95,-28) has no Gossip Stone or butterflies; LW's only stone (-36,95,72) and butterflies (7,101,-48) are above ground.|
|`LW Near Shortcuts Grotto -> Fish` (event)|`has_bottle` -> `False`|No Animal_Fish_* or FishAnchor in LostWood; its only water (Obj_WaterPlane_A_01 10199661799331481022) is the river above ground.|

Checked, unchanged: `LW Skull Kid` `is_child and can_play(Sarias_Song)` (NL HP #2, Game8, Zelda Central HP #9);
`LW Ocarina Memory Game` (three rounds, heart piece last; NL HP #3, Game8; buttons are start items); `LW Target in
Woods` `can_use(Slingshot)` (Game8, Zelda Central; target in data); `LW Deku Scrub Near Bridge` and both `LW Deku Scrub
Near Deku Theater` `is_child and can_stun_deku` (Game8, Zelda Central; child-file scrubs; open 3); `LW Deku Scrub Grotto
Front/Rear` `can_stun_deku` (Zelda Central: nut bag 40, seeds); `LW GS Bean Patch Near Bridge` (NL GS #33) and `LW GS
Bean Patch Near Theater` (NL GS #34, Game8), not Nocturnal; `Deku Theater Skull Mask` and `Deku Theater Mask of Truth`
(Game8, Zelda Central; stage scrubs and elder in data); `LW Gift from Saria` `True` and the bridge exit (Zelda
Central, trailer); Lost Woods `Fairy` (Gossip Stone, bean soil) and Beyond Mido `Fairy` (butterflies in data); Lost
Woods `Bugs` (no evidence either way; open 4); grotto `Bugs` (nine bug-dropping grass actors; Zelda Central); exits
`LW Forest Exit` and `GC Woods Warp` (data transitions), `Zora River` (underwater transition), `LW Underwater Entrance`
(no contrary evidence), `LW Near Shortcuts Grotto` and `LW Scrubs Grotto` `here(can_blast_or_smash)` (boulders on both
holes; open 2), `Deku Theater` `True` (open hole, no cover), child `LW Beyond Mido` and grotto exits back `True`. Low
priority, unchanged: underwater rupees, `LW Under Boulder Blue Rupee`, wonder items, beehives (no beehive actor); the
N64 grotto chest is n64_only in remake.toml. Adult-only rules left to track B: `Odd Mushroom Access`, `Poachers Saw
Access`, `LW GS Above Theater`, the `LW Bridge` exits including `LW Bridge -> Lost Woods` (Longshot), Mido blocking the
adult at `LW Beyond Mido`, Mushroom Timeout.

Open (in-game check for Kareem):

1. **Can a child reach the meadow before meeting Zelda?** On a save past the Deku Tree but before Zelda, take the
   correct path through the woods. Does the last turn send Link back to Kokiri Forest (NL says yes)? Rule: `LW Beyond
   Mido -> SFM Entryway`.
2. **Is the underground glade one connected space?** Theater hole, grotto scrubs and bug patch all lie at y 83; Zelda
   Central walks between them. From the theater, walk to the scrubs and the bugs without bombs? If yes, `LW Scrubs
   Grotto` and `LW Near Shortcuts Grotto` need no explosives.
3. **Do the LW scrubs sell without a shield?** Face the bridge scrub with only the Slingshot, Kokiri Sword or Deku Nuts.
   Does it give up and sell? Rule: `can_stun_deku` in every LW scrub rule (guides only show the shield).
4. **Does any bush above ground give a bug?** Cut bushes around the Lost Woods outside the grottos. Rule: event `Bugs`
   (Lost Woods).
5. **How is the chest above the bridge scrub reached?** Remake-only chest at (-49,105,72), 10 m above the scrub; find
   the way up. Needed for a future location.

Remake-only checks noticed / for other tracks:

- Remake-only chest 17479747339356189279 (TBox_Rupee_Purple) at (-49,105,72) above the bridge scrub (open 5); adult
  rear grotto scrub 14619830301496284497 sells arrows (census, remake-only).
- Target game prize (D16, remake.toml `vanilla_fixed = "Bullet Bag (40)"`): event Dm_LostWood_0040 checks for the 40
  bag and carries 40 and 50 bag models; Zelda Central, holding the 40 bag, got the 50 one. The game gives the next tier.
- Track B: `LW GS Above Theater` (4335656213162247230, both age files) is not Nocturnal; OoTR asks `at_night`; NL GS
  #35 and Zelda Central GS #45 list no night.
- Track B: adult scrubs at the bridge (stick bag, 11192313919554167152) and grotto front (nut bag, 5764461665617243979),
  and the theater elder 10978827534277086146 is in the adult file (adults wear masks, Eurogamer); OoTR says `is_child`.

### Sacred Forest Meadow (`child_sacred_forest_meadow.toml`)

Sources: Eurogamer 17 changes, https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, Nintendo Life
Lost Woods path guide (covers the Sacred Grove),
https://www.nintendolife.com/guides/zelda-ocarina-of-time-lost-woods-path-guide-maze-directions-switch-2, Nintendo
Life Gold Skulltulas,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2,
Game8 100% walkthrough, https://game8.co/games/Zelda-Ocarina-of-Time/archives/480402, Zelda Central remake guide (Lost
Woods and Sacred Grove, adult Sacred Grove, secret grottos),
https://zeldacentral.com/games/ocarina-of-time-remake/walkthrough/lost-woods-and-sacred-grove/, Zelda Central business
scrubs, https://zeldacentral.com/games/ocarina-of-time-remake/business-scrubs/, z64central Switch 2 page (trailer
screenshot of the gate Wolfos), https://z64central.com/switch-2/, placement data (actors.py SacredForestMeadow), logic
module Gimmick_Ocarina_Appearance_01_SacredForest, plans/03-game-data.md sections 5, 11, census.

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|`SFM Entryway -> SFM Wolfos Grotto`|`can_open_bomb_grotto` -> `can_play(Song_of_Storms)`|Wolfos room and rising chest 7995233962349162969 lie under cover 8456945034417122929 (-2,100,51), which the Song of Storms module removes; no bomb rock. Shared. Open 1.|
|`Sacred Forest Meadow -> SFM Storms Grotto`|`can_open_storm_grotto` -> `can_play(Song_of_Storms)`|Main's grotto decision (no Stone of Agony). The hole here (1,114,-85) is not the storms one and holds no N64 check; opener unknown (open 2).|
|`SFM Deku Scrub Grotto Rear`|`can_stun_deku` -> `n64_only`|No Enemy_Scrub_Business in the SFM Banc (03-game-data section 5, census, Zelda Central scrub list); the hole drops into a Gossip Stone clearing.|
|`SFM Deku Scrub Grotto Front`|`can_stun_deku` -> `n64_only`|As Rear: no business scrub anywhere in the remake's meadow.|

Checked, unchanged: `Song from Saria` `is_child and at('HC Garden Skippable Locations', is_child)` (song only after
Zelda; NL, Game8, Zelda Central); entryway -> `Sacred Forest Meadow` `is_adult or Slingshot or Sticks or Kokiri_Sword or
can_use(Dins_Fire)` (gate Wolfos opens the shutter; NL, Game8, z64central; open 3) and `SFM Wolfos Grotto Chest`, same
rule (two Wolfos raise the chest, as N64; open 3); meadow `Fairy` (three Gossip Stones in data); `SFM Fairy Grotto`
entry `True` and its `Fairy` `has_bottle` (open hole, eight fountain fairies; NL, Game8); exits `LW Beyond Mido`
(transition in data), `SFM Entryway` and grotto exits back `True`. Low priority, unchanged: `SFM Near Lost Woods
Wonderitem`, maze wonder items, `SFM Storms Grotto Beehive` (no beehive actor). Adult-only rules left to track B: `Sheik
in Forest`, `SFM GS` (Hookshot), `SFM Forest Temple Entrance Ledge` (Hookshot target).

Open (in-game check for Kareem):

1. **Does the Song of Storms open the Wolfos grotto?** At the entryway, by the round cover just before the Wolfos gate
   (-2,100,51), play the Song of Storms; also try bombs. Does it lead to the two-Wolfos grotto? Rule: `SFM Entryway ->
   SFM Wolfos Grotto`.
2. **What opens the top hole by Saria?** Cover at (1,114,-85) near Saria's stump: try bombs, songs, or reach it from
   below. Does it drop into the Gossip Stone clearing with the Scrub Seed chest? Rule: `Sacred Forest Meadow -> SFM
   Storms Grotto`.
3. **Which child weapons beat the Wolfos?** (low priority) Slingshot only, then Deku Sticks only, against the gate
   Wolfos and the grotto pair. Rules: entryway -> `Sacred Forest Meadow`, `SFM Wolfos Grotto Chest`.

Remake-only checks noticed / for other tracks:

- Remake-only Business Scrub Seed chest 1764383515296652106 at (12,96,-74), in the clearing behind the Song of Time
  blocks (Zelda Central: adult plays Song of Time); possibly also under the top hole (open 2).
- Track B: the Wolfos grotto cover is in the adult file too (EventProxyRequestActor 3397472349600050316), so Song of
  Storms applies to both ages; this differs from Main's blanket `can_blast_or_smash` instruction, per the data.
- Track B: `SFM GS` (14473218207379268379, adult file only) is not Nocturnal; OoTR asks `at_night`; NL GS #62 and
  Zelda Central GS #46 list no night. Adult enters by a Deku Flower launch over the wall (Zelda Central).
- A child now reaches nothing here before meeting Zelda (new `LW Beyond Mido -> SFM Entryway` rule, Lost Woods file).

### Hyrule Field (`child_hyrule_field.toml`)

Sources: Eurogamer 17 changes, https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, IGN changes,
https://www.ign.com/wikis/ocarina-of-time-remake/Biggest_Changes_and_Differences, Nintendo Life walkthrough hub,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake, Nintendo Life heart pieces,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2, Nintendo Life Business Scrub
password, https://www.nintendolife.com/guides/zelda-ocarina-of-time-business-scrub-password-switch-2, Nintendo Life Song
of Storms, https://www.nintendolife.com/guides/zelda-ocarina-of-time-song-of-storms-change-weather-music-man-switch-2,
RPG Site minimalist 100% walkthrough,
https://www.rpgsite.net/guide/21671-the-legend-zelda-ocarina-time-remake-minimalist-100-walkthrough-all-items-gold-skulltula-tokens-heart-pieces,
Eurogamer and Polygon Gold Skulltula guides (local copies in E:/OOTRemake/work/r3/), placement data (actors.py
HyruleField; the Banc also holds Lon Lon Ranch and Lake Hylia).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|`Hyrule Field -> HF Inside Fence Grotto`|`can_open_bomb_grotto` -> `can_blast_or_smash`|Main's grotto decision (entrances visible, Agony stone is the Echo Gem); NL scrub guide: bomb right of the castle gate; cover 2319887810288392884. Shared.|
|`Hyrule Field -> HF Cow Grotto`|`(is_child or Megaton_Hammer) and can_open_bomb_grotto` -> `... and can_blast_or_smash`|Grotto decision; Obj_BrokenRock_A_01 15605814217953065995 inside a ring of four lift rocks, cow below. Shared; adult part kept.|
|`Hyrule Field -> HF Near Kak Grotto`|`can_open_bomb_grotto` -> `can_blast_or_smash`|Grotto decision; Eurogamer, Polygon GS: bombs open the circular rock in the southern wood; cover 4105624336310342731; Agony area at the GS inside. Shared.|
|`Hyrule Field -> HF Tektite Grotto`|`can_open_bomb_grotto` -> `can_play(Song_of_Storms)`|Leafy storms cover 18359593268860138712 with EventProxyRequestActor, as KF/SFM/DMT/ZR/HC; IGN: plants need wind. No check inside. Unseen (open 1). Shared.|
|`Hyrule Field -> HF Open Grotto`|`True` -> `here(can_blast_or_smash)`|All eight HF grotto entrances covered (data, IGN, Eurogamer); wetlands cover 2786334400301738354; Eurogamer GS: bombs open the wetlands hole. Shared.|
|`HF Southeast Grotto Chest`|`True` -> `n64_only`|No generic grotto chest: the HF Banc's only grotto chest outside Lake Hylia is the ReDead grotto's (5755485285664292988).|
|`HF Open Grotto Chest`|`True` -> `n64_only`|As above; the census's extra HF chests are three Fairy Note chests and the LLR tower chest, not N64's.|
|`HF Near Market Grotto Chest`|`True` -> `n64_only`|As above; the hole by the drawbridge (40,148,27) is the heart piece scrub's (NL scrub guide).|
|`HF Southeast Grotto -> Fish` (event)|`has_bottle` -> `False`|No Animal_Fish or FishAnchor in the wetlands or east grottos; fish only in the tektite pool and Lake Hylia. Shared.|
|`HF Open Grotto -> Fish` (event)|`has_bottle` -> `False`|Same data. Shared.|
|`HF Near Market Grotto -> Fish` (event)|`has_bottle` -> `False`|Same; the scrub grotto has shallow water and no fish. Shared.|
|`HF Tektite Grotto Freestanding PoH`|`(Progressive_Scale, 2) or can_use(Iron_Boots)` -> `n64_only`|NL HP #35/#36, RPG Site #34/#35: HF heart pieces are the Fairy Note chest and scrub; pool holds three rupee crates, no Obj_Heart_Piece.|
|`HF Deku Scrub Grotto`|`can_stun_deku` -> `is_child and can_stun_deku and at('Hyrule Field', is_adult)`|NL scrub guide, RPG Site #35: adult reads password on Fairy Note 7446547123750630562 (Adult_Static); child buys heart piece, 100 rupees; adult told sold out. Shared.|
|`HF Child Above Drawbridge Wonderitem 1`|`is_child` -> `n64_only`|IGN, Eurogamer: the drawbridge chains can no longer be climbed; the rupees above it are gone.|
|`HF Child Above Drawbridge Wonderitem 2`|`is_child` -> `n64_only`|Same.|
|`HF Child Above Drawbridge Wonderitem 3`|`is_child` -> `n64_only`|Same.|

Checked, unchanged: `HF Ocarina of Time Item` and `Song from Ocarina of Time` `is_child and has_all_stones` (NL
walkthrough, RPG Site; open 2; the item is vanilla_fixed in remake.toml, so a rule change needs Main); exits to LW
Bridge, Lake Hylia, Gerudo Valley, Market Entrance, Kakariko Village, ZR Front and Lon Lon Ranch `True` (IGN: no loading
screens); `HF Southeast Grotto`, `HF Near Market Grotto`, `HF Fairy Grotto` entries `here(can_blast_or_smash)` (bomb
covers in data; region kept, no third generic grotto); grotto exits back `True`; generic-grotto `Fairy` and `Bugs`
(stricter than game: sources outside); `HF Fairy Grotto` `Fairy` (eight fountain fairies); cow grotto `Fairy`, `Bugs`,
`Deku Nut Drop` `has_fire_source` (three webs, no torch; open 3); `HF GS Near Kak Grotto` (remake.toml rule; not
Nocturnal); the scrub's `can_stun_deku` (NL: shield the nut); `HF GS Cow Grotto`, `HF Cow Grotto Cow` (n64_only in
remake.toml); no child night rule here. Low priority: the beehives (no beehive actor in the Banc; n64_only candidates if
shuffled) and the two cow grotto pots behind a web, unchanged. Adult side (cow grotto without the hammer, scrub sold out
to adults, Big Poes) left to track B.

Open (in-game check for Kareem):

1. **Do the leafy covers open with a bomb?** At the cover west of the drawbridge (-98,147,17), throw a bomb, then play
   Storms. If a bomb works, `HF Tektite Grotto` becomes `can_blast_or_smash`. Same test at the Kakariko-steps cover (Kak
   Redead Grotto).
2. **Can a scaleless child reach the moat Ocarina?** All three stones, no Silver Scale: after the drawbridge cutscene,
   swim to (16,145,43). If unreachable, `HF Ocarina of Time Item` and `Song from Ocarina of Time` need
   `Progressive_Scale`.
3. **Do the cow grotto webs need fire?** Child without Din's Fire, cow grotto by Gerudo Valley: hit the web before the
   cow with sword, Deku Stick, Slingshot, Bomb. Any success replaces `has_fire_source` on the grotto's events and pots.
4. **What is in the wetlands and east grottos?** Bomb open (40,145,342) north of Lake Hylia and (180,157,190) by Zora's
   River; look for a chest, fish, shrubs, beehives. Settles the three `Fish` events and the three n64_only grotto
   chests.
5. **Is HF GS Lone Tree there by day?** Roll into the lone tree between Kokiri Forest and Lon Lon Ranch (71,167,264) by
   day; actor not Nocturnal, RPG Site says night. Sets the new location's time rule.
6. **Who can buy the scrub's heart piece?** Confirm a child who never spoke to the scrub buys it after the adult read
   the note, and the adult cannot buy with the password. Rule: `HF Deku Scrub Grotto`.

Remake-only checks noticed / for other tracks:

- `HF GS Lone Tree` (census 2177746409373494991, both ages, not Nocturnal): roll into the lone tree, no item (Eurogamer,
  Polygon); region Hyrule Field, `can_bonk` (open 5).
- `HF GS Wetland Grotto Crate` (census 9047381233010434881, Adult_Static, Echo Gem reacts): child bombs the wetlands
  hole and kills the back-wall Skullwalltula, then the adult breaks the crate (else a green rupee). Sketch: `is_adult
  and can_break_crate and at('<wetlands grotto>', is_child and can_blast_or_smash and can_child_attack)`.
- Fairy Note heart piece chest (census 2967378296224661060) by the Gerudo Valley entrance: adult reads HrlField_Note_11,
  then the child opens it (NL HP #35, RPG Site #34); sketch `is_child and at('Hyrule Field', is_adult)`. Adult rupee
  chests 9891111455604007674, 1163740567397714729 mirror it (inferred: child reads the note).
- Other areas: the ReDead grotto (163,156,27) is Kakariko's, the three-scrub grotto (-36,151,291) LLR's, the tombstone
  grotto (-205,138,455) Lake Hylia's. Track B: the adult cow grotto rock may need only explosives; Big Poes at purple
  lanterns (RPG Site).

### Lon Lon Ranch (`child_lon_lon_ranch.toml`)

Sources: Eurogamer 17 changes, https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, IGN changes,
https://www.ign.com/wikis/ocarina-of-time-remake/Biggest_Changes_and_Differences, Nintendo Life Epona,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-horse-epona-how-to-get-switch-2, Nintendo Life bottles,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-bottle-locations-switch-2, Nintendo Life heart pieces,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2, Nintendo Life Hyrule Castle,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-hyrule-castle-walkthrough-weird-egg-wake-up-cucco-switch-2,
RPG Site minimalist 100% walkthrough,
https://www.rpgsite.net/guide/21671-the-legend-zelda-ocarina-time-remake-minimalist-100-walkthrough-all-items-gold-skulltula-tokens-heart-pieces,
Eurogamer and Polygon Gold Skulltula guides (local copies in E:/OOTRemake/work/r3/), placement data and Presence flags
(actors.py HyruleField, fieldranch_flags.py).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|`LLR GS House Window`|`can_use(Boomerang) and (at_night or gold_skulls_ignore_daytime)` -> `can_use(Boomerang) and ((at_night and 'Time Flows') or gold_skulls_ignore_daytime)`|Main's time decision (Eurogamer: time flows after meeting Zelda); GS guides: child, night, Boomerang, upper house window; 15889002414176907668 Nocturnal, Child_Static.|

Checked, unchanged: `Song from Malon` and `LLR Talons Chickens` (NL Epona, bottles, Hyrule Castle: Talon woken at the
castle first; Malon, Talon and Epona are at the ranch only after `Goto_HyruleCastle_IsAfter_Step03_02_Exp`; `at_day`
holds before Zelda, clock stopped); `LLR GS Tree` `is_child and can_bonk` (roll into tree; not Nocturnal); `LLR
Freestanding PoH` `is_child` (NL HP #1, RPG Site #1: tower crates); `LLR Deku Scrub Grotto Left/Right/Center`
`can_stun_deku` (three scrubs: nuts, bombs, seeds); `Lon Lon Ranch -> LLR Grotto` `is_child` (child cover lacks AirWall;
open 1); exits to Hyrule Field, Stables, Tower and back `True` (IGN: ranch inside the field); `Lon Lon Ranch -> LLR
Talons House` `is_adult or at_day` (no evidence either way); `LLR GS Rain Shed`, `LLR GS Back Wall` and the four cows
(n64_only in remake.toml). Low priority: front, rain shed and Talon's house pots, the child crate and `LLR Grotto
Beehive` (no pot, crate or beehive actor at the ranch; n64_only candidates if shuffled), unchanged. Adult-only `Epona`,
`Links Cow` and `LLR Epona Hurdle Wonderitem 1/2` left to track B.

Open (in-game check for Kareem):

1. **Does the LLR grotto open without a bomb?** Child, no explosives: step onto the stone circle by the south fence
   (-36,151,291). If a bomb is needed, `Lon Lon Ranch -> LLR Grotto` becomes `is_child and has_explosives`.
2. **How is the tower chest reached?** In the ruined tower, find the way to the chest about 11 m up (-152,162,265):
   vines, the crate puzzle? Needed to add the remake-only location (census 17445672702269453589).

Remake-only checks noticed / for other tracks:

- `LLR GS Tower` (census 2730878115209290675, both ages, Nocturnal): vines above the tower boxes; Boomerang (child) or
  Hookshot (adult) at night (Eurogamer, Polygon, RPG Site #35). Sketch in LLR Tower: `(can_use(Boomerang) or
  can_use(Hookshot)) and ((at_night and (is_adult or 'Time Flows')) or gold_skulls_ignore_daytime)`.
- LLR tower chest (census 17445672702269453589, Item_ScrubBusinessSeed, both ages), HrlField_Note_15 in the tower;
  access is open 2.
- Census owner: the three grotto scrubs ("Hyrule Field Scrub (...)") lack `oot_randomizer_name`: nuts
  17418042722045679657 = Left, bombs 16672855544778411393 = Right, seeds 12901354557574090016 = Center.
- Track B: the `LLR GS Tree` actor is in Adult_Static too (Eurogamer: both ages; OoT Randomizer `is_child`); Link's Cow
  needs more obstacle-course wins (RPG Site); Epona as N64 (NL).

### Market (`child_market.toml`)

Sources: Nintendo Life heart pieces,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2, Nintendo Life bottles,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-bottle-locations-switch-2, Nintendo Life Happy Mask Shop,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-happy-mask-shop-quest-mask-of-truth-switch-2, Nintendo Life
walkthrough hub, https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake, Eurogamer 17
changes, https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, Eurogamer and Polygon Gold Skulltula
guides (local copies in E:/OOTRemake/work/r3/), event flows (E:/OOTRemake/work/r1-research/decoded/evfl_all.json, switch
case 0 = yes), placement data (actors.py Market).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|`Market Night Red Rupee Crate`|`is_child and at_night and (...)` -> `is_child and (at_night and 'Time Flows') and (...)`|Main's time decision (Eurogamer: time flows only after meeting Zelda).|
|`Market Night Green Rupee Crate 1`|`is_child and at_night and (...)` -> `is_child and (at_night and 'Time Flows') and (...)`|Same.|
|`Market Night Green Rupee Crate 2`|`is_child and at_night and (...)` -> `is_child and (at_night and 'Time Flows') and (...)`|Same.|
|`Market Night Green Rupee Crate 3`|`is_child and at_night and (...)` -> `is_child and (at_night and 'Time Flows') and (...)`|Same.|
|`Market Night Balcony Wonderitem 1`|`is_child and at_night` -> `is_child and (at_night and 'Time Flows')`|Same.|
|`Market Night Balcony Wonderitem 2`|`is_child and at_night` -> `is_child and (at_night and 'Time Flows')`|Same.|
|`Market -> Market Treasure Chest Game`|`is_child and at_night` -> `is_child and (at_night and 'Time Flows')`|Time decision; NL HP: the Treasure Chest shop at night; flow MiniGame_SequentialChoiceTreasure: closed 06:00-21:00.|
|`Market Back Alley -> Market Bombchu Shop`|`at_night` -> `(at_night and 'Time Flows')`|Time decision; flow Npc_Hylia_021_Shop_Child `CheckRestrictedDoor`: closed 06:00-21:00.|
|`Market Back Alley -> Market Man in Green House`|`at_night` -> `(at_night and 'Time Flows')`|Time decision.|
|`Market Lost Dog`|`is_child and at_night` -> `is_child and (at_night and 'Time Flows')`|Time decision; NL HP #29: at night (the woman by the market entrance, Richard in the back alley).|
|`Market Bombchu Bowling First Prize`|`has_explosives` -> `has_explosives and 'Defeat King Dodongo'`|Flow MiniGame_BombchuBowling: `Get_StoneOfFire_IsCompleted_Exp` (quest state, so boss event, not `Goron_Ruby`) gates play; NL HP: after Dodongo's Cavern. Explosives kept (open 2).|
|`Market Bombchu Bowling Second Prize`|`has_explosives` -> `has_explosives and 'Defeat King Dodongo'`|Same gate; the heart piece comes on the third clear (HeartPieceAnchor `MiniGame_BombchuBowling_ClearThirdTime`).|
|`Market Bombchu Bowling Bombchus`|`found_bombchus` -> `found_bombchus and 'Defeat King Dodongo'`|Same gate; the first clear gives Bombchus.|
|`Market Bombchu Bowling Bomb`|`has_explosives` -> `has_explosives and 'Defeat King Dodongo'`|Same gate; clears after the third give a red rupee.|
|`Market Shooting Gallery Reward` (vanilla_fixed)|`Slingshot` -> `Bullet Bag (40)`|Flow MiniGame_HitTarget `Child_Reward`: Bullet Bag (Medium; Large if held) once, then rupees; gallery lends a slingshot. Fixes a free Slingshot the Deku Tree needs.|

Checked, unchanged: square and alley exits (`Market Entrance -> Hyrule Field` `is_adult or at_day`, Guard House, ToT
Entrance, Castle Grounds, `Market -> Market Back Alley` `is_child`, returns: no evidence against); `Market Bazaar`,
`Market Potion Shop`, `Market Shooting Gallery` `is_child and at_day` (flows: closed 20:00-07:00) and `Market Mask Shop`
(flow: closed at night); `Market Bombchu Bowling` `is_child` (door has no hours check); `Market Shooting Gallery Reward`
`is_child` (no Slingshot needed to play); mask shop storefront, `Mask of Truth Access` and `Market Mask Shop Item 1-8`
(NL mask quest; Saria's Song and stones parts kept); Treasure Chest Game salesman, room boxes and reward with six keys
(NL HP: five keys, Lens of Truth); `Market GS Guard House` `is_child and can_break_crate` (GS guides: shaking crate; not
Nocturnal); bazaar, potion and Bombchu shop items `True` (shops not changed); ToT Entrance `Fairy` (four gossip stones);
`Market Lost Dog` region (alley needed for Richard anyway); Bombchu Shop door at square level (alley exit equivalent,
child only). Low priority: guard house crates and pots, day crates, daytime balcony wonder items, the dog lady's crate
and the Man in Green's pots, unchanged. Adult-only Poe collector (NL bottle #5: five Poes, not `Market 10 Big Poes`)
left to track B.

Open (in-game check for Kareem):

1. **Does Richard's owner pay by day?** After meeting Zelda, by day, lead Richard (back alley or square) to the woman.
   If she gives the heart piece, `Market Lost Dog` loses its night part.
2. **Can a child bowl without explosives?** Dodongo's Cavern beaten, no Bomb Bag or Bombchus: ask the bowling lady. If
   she lends ten Bombchus and pays prizes, drop `has_explosives`/`found_bombchus` (keep `'Defeat King Dodongo'`). Before
   the cavern she should refuse.
3. **Is the Bombchu Shop shut 18:00-21:00?** Confirm closed then and open 21:00-06:00 (flow data). `at_night` covers
   both; matters only if time of day is split finer. Rule: `Market Back Alley -> Market Bombchu Shop`.

Remake-only checks noticed / for other tracks:

- Potion Shop bottle (remake-only, child, by day): the shopkeeper's tutorial gives `Item_Bottle` once a bug is caught
  (flow Npc_Hylia_020_Shop_Child; NL bottle #1); no OoT Randomizer location, no census Hash (event gift).
- Mask shop: census `Item 1-8` follow `ShopItemIndex`, not OoT Randomizer's masks (census Item 1 = Spooky, Item 8 =
  Truth); if mask slots are shuffled, link by mask, not index.
- Bowling prizes: Bombchus, then a Bomb Bag upgrade, then the heart piece, then red rupees; OoT Randomizer's `Bomb`
  matches the repeat rupee; vanilla items not changed.
- Not checks: the treasure game's repeat red rupee (census 6781536951709667179) and Richard's blue rupee 72 hours after
  the first return.

### Hyrule Castle (`child_hyrule_castle.toml`)

Sources: Nintendo Life Hyrule Castle,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-hyrule-castle-walkthrough-weird-egg-wake-up-cucco-switch-2,
Nintendo Life Great Fairy fountains,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-great-fairy-fountain-locations-all-switch-2, Nintendo Life
walkthrough hub, https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake, Eurogamer 17
changes, https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, games.gg Great Fairies,
https://games.gg/the-legend-of-zelda-ocarina-of-time-2026/guides/ocarina-of-time-remake-great-fairy-locations-rewards-and-costs,
Eurogamer and Polygon Gold Skulltula guides (local copies in E:/OOTRemake/work/r3/), placement data (actors.py
HyruleCastle), event flows Get_StoneOfWater, Goto_HyruleCastle.

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|`Hyrule Castle Grounds -> HC Storms Grotto`|`can_open_storm_grotto` -> `can_play(Song_of_Storms)`|Grotto decision; GS guides: Song of Storms by the lone tree opens it; cover 13073548223054495027 (36,117,-106); Agony area only inside.|
|`HC Garden -> Time Flows` (event, new)|- -> `is_child`|Eurogamer: time flows only after meeting Zelda, who is met in the garden (Npc_Hylia_Zelda_Child 13027585550451396507). Other areas' night rules read it.|
|`HC Great Fairy Fountain -> Great Fairy Met` (event, new)|- -> `can_play(Zeldas_Lullaby)`|games.gg: the first Great Fairy visited must be DMT's or HC's; NL: Lullaby on the Triforce. DeathMountain sets the same event at DMT.|

Checked, unchanged: `Castle Grounds -> Hyrule Castle Grounds` `is_child` (NL step 1: vines); `Castle Grounds -> Market`
`is_child or at_dampe_time` (child part `True`; shared, not overridden); `HC Malon Egg` `True` (NL: Malon gives it);
`Hyrule Castle Grounds -> HC Garden` `Weird_Egg or Chicken` (NL steps 4-7: wake Talon, blocks, vent; the egg hatches on
an area trigger, no wait); `HC Zeldas Letter`, `Song from Impa` and the garden exits `True` (NL steps 8-10; guards
only); `HC GS Tree` `can_child_attack and can_bonk` (GS guides: lone garden tree; not Nocturnal); `Hyrule Castle Grounds
-> HC Great Fairy Fountain` `has_explosives` (NL: bomb the corner rock; child-only region); `HC Great Fairy Reward`
`can_play(Zeldas_Lullaby)` (NL; vanilla Magic Meter already in remake.toml, though NL calls her the Spin Attack fairy,
swapped with Death Mountain's); `HC GS Storms Grotto` (GS guides: bomb the back wall, Boomerang; trick off); storms
grotto `Fairy`, `Bugs`, `Deku Nut Drop` `can_blast_or_smash` (gossip stone behind a wall crack); exits back `True`;
grounds `Fairy` and `Bugs` (gossip stones, four butterflies). Low priority: storms grotto pots (two in the remake, OoT
Randomizer lists four) and the castle torch, moat and courtyard wonder items, unchanged. Adult part of `Castle Grounds
-> Market` (`at_dampe_time`, probably needs `'Time Flows'`) left to track B.

Open (in-game check for Kareem):

1. **Do Great Fairies charge rupees?** With 0 rupees and no other fairy met, play Zelda's Lullaby at the HC fountain
   (games.gg: fees 25 to 500, rising). If she refuses, `HC Great Fairy Reward` needs a wallet or rupee condition.
2. **Does the Zora quest need Impa at the castle?** After King Zora's first talk, see if Impa (58,108,-64) talks; then
   whether the diving game or Ruto's letter waits for her. If so, ZoraLake rules need a castle visit.

Remake-only checks noticed / for other tracks:

- No remake-only checks: the census lists only `HC GS Tree` and `HC GS Storms Grotto`.
- ZoraLake: the Stone of Water quest has a step `Step03_Impa` between King Zora's first talk and the diving game, which
  reads it (`StoneOfWater_ClearDivingGame`); Impa 8386608225181456612 at the castle (open 2).
- Great Fairy fees (games.gg: 25 to 500 rupees, rising per fairy; NL also mentions rupees) are not modelled (open 1).

### Temple of Time (`child_temple_of_time.toml`)

Sources: Nintendo Life walkthrough hub (Temple of Time, Awakening the Five Sages),
https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake, Nintendo Life Hyrule Castle,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-hyrule-castle-walkthrough-weird-egg-wake-up-cucco-switch-2,
event flow DoorOfTime and GameDataList (E:/OOTRemake/work/r1-research/decoded/, switch case 0 = yes), placement data
(actors.py Market).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|`Temple of Time -> Beyond Door of Time`|`can_open_door_of_time` (default `sot`: Song of Time only) -> `has_all_stones and (Ocarina, 2) and can_play(Song_of_Time)`|Flow DoorOfTime: needs Fire and Water stone quests, Zelda's escape, then the Song of Time; altar and stones linked to door proxy 11695057968283014044. Shared.|

Checked, unchanged: `Temple of Time Access` `True` (goal bookkeeping only); exits to ToT Entrance, back from Beyond Door
of Time and to its Skippable Locations `True` (nothing in the way); `Time Travel` `True` (NL: Master Sword, no item);
`ToT Reward from Rauru` `True` (NL; flow `SageRoom_MeetRauru`); no child night rule here; the ToT Entrance gossip-stone
`Fairy` is in the Market section. Low priority: none listed for this file. Adult `Sheik at Temple` (matches NL) and `ToT
Light Arrows Cutscene` (medallion check not read) left to track B.

Open (in-game check for Kareem):

1. **Fairy Ocarina at the Door of Time?** Three stones, Song of Time, Fairy Ocarina only: play at the altar. Opens: drop
   `(Ocarina, 2)`. If shut before Zelda's escape scene with the song (modded save), the exit depends on that scene.

Remake-only checks noticed / for other tracks:

- Settings: `open_door_of_time` is no longer read by this exit; the game cannot honour it without a code hook.
- The flow reads stone quest states (boss beaten, stone scene), not stone items; if boss rewards are shuffled, read the
  three boss events instead, as the bowling gate does.
- The flow does not test the Ocarina of Time item; `(Ocarina, 2)` is the vanilla route (moat Ocarina and Song of Time
  after three stones); open 1 matters only if those gifts are shuffled.
- Track B: `ToT Light Arrows Cutscene` medallion set unread (flow `Market_Adult_Field_GetArrowLight` would settle it).
  No remake-only checks (no chest, Gold Skulltula or heart piece).

### Kakariko Village (`child_kakariko.toml`)

Sources: IGN Kakariko walkthrough,
https://www.ign.com/wikis/ocarina-of-time-remake/Spiritual_Stone_of_Fire_-_Kakariko_Village_Walkthrough, IGN heart
pieces, https://www.ign.com/wikis/ocarina-of-time-remake/All_Heart_Piece_Locations, IGN changes,
https://www.ign.com/wikis/ocarina-of-time-remake/Biggest_Changes_and_Differences, Eurogamer Kakariko,
https://www.eurogamer.net/zelda-ocarina-of-time-kakariko-village, Eurogamer 17 changes,
https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, Nintendo Life walkthrough hub,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake, Nintendo Life Cuccos,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-cucco-locations-kakariko-village-switch-2, Nintendo Life
bottles, https://www.nintendolife.com/guides/zelda-ocarina-of-time-bottle-locations-switch-2, Nintendo Life Song of
Storms, https://www.nintendolife.com/guides/zelda-ocarina-of-time-song-of-storms-change-weather-music-man-switch-2,
Nintendo Life heart pieces, https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2,
Nintendo Life Gold Skulltulas,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2, Eurogamer and
Polygon Gold Skulltula guides (local copies in E:/OOTRemake/work/r3/), placement data (KakarikoVillage_*,
HyruleField_*).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|`Kakariko Village -> Kak Impas Ledge`|`(is_child and at_day) or (is_adult and logic_visible_collisions)` -> `is_adult and logic_visible_collisions`|IGN HP #11: pen-roof heart piece only from Impa's roof; child via owl (Eurogamer, NL); heart piece 17926402522258180222. Shared; adult part unchanged.|
|`Kakariko Village -> Kak Odd Medicine Rooftop`|`can_use(Hookshot) or (logic_man_on_roof and ...)` -> `can_use(Hookshot) or (is_child and at_day) or (logic_man_on_roof and ...)`|IGN walkthrough, HP #2: child glides with cuccos (fence, windmill hill) onto Granny's roof, no item; NL Cuccos #6/#7. Day only (open 5). Looser; shared.|
|`Kakariko Village -> Kak Redead Grotto`|`can_open_bomb_grotto` -> `False`|Kakariko's only bomb grotto (-20,97,66) holds a gossip stone and seven beehives, no chest; no Enemy_ReDead in the village. Supersedes the grotto decision.|
|`Kak Redead Grotto -> Kakariko Village`|`True` -> `False`|The grotto's way out leads to Hyrule Field.|
|`Hyrule Field -> Kak Redead Grotto` (new)|- -> `can_play(Song_of_Storms)`|HF grotto (163,151,27) by Kaepora's tree: two ReDeads, chest 5755485285664292988 on a raised pedestal; storms cover 14656437530366949192, proxy, bug-plant ring. Unseen (open 4).|
|`Kak Redead Grotto -> Hyrule Field` (new)|- -> `True`|Way out.|
|`Kak Redead Grotto Chest`|area KakarikoVillage -> `area = "HyruleField"`|Census chest 5755485285664292988 "Hyrule Field Chest (TBox_Rupee_Purple)"; kill-the-ReDeads rule unchanged.|
|`Kak GS House Under Construction`|`is_child and (at_night or ...)` -> `is_child and ((at_night and 'Time Flows') or ...)`|Main's time decision (Eurogamer; IGN "Time Always Moves"); 14107117960174262321 Nocturnal; IGN: night, construction site wall.|
|`Kak GS Skulltula House`|`is_child and (at_night or ...)` -> `is_child and ((at_night and 'Time Flows') or ...)`|Time decision; 15314554401574296838 Nocturnal; IGN: left of the door, night only.|
|`Kak GS Near Gate Guard`|`is_child and (at_night or ...)` -> `is_child and ((at_night and 'Time Flows') or ...)`|Time decision; 11629189455828560791 Nocturnal; NL GS #18: night, behind the house by the Death Mountain gate.|
|`Kak GS Tree`|`... (at_night or ...) and can_bonk` -> `... ((at_night and 'Time Flows') or ...) and can_bonk`|Time decision; night kept (NL, Eurogamer, Polygon) though 7677963516305772491 is not Nocturnal and IGN gets it by day (open 1).|
|`Kak GS Watchtower`|`... (at_night or ...) and (Slingshot or ...)` -> `... ((at_night and 'Time Flows') or ...) and (Slingshot or ...)`|Time decision; 15118290503807073158 Nocturnal on the watchtower ladder; NL GS #17, IGN: Slingshot, then climb.|

Checked, unchanged: `Kakariko Village Gate Open` `is_child and Zeldas_Letter` (NL, IGN, Eurogamer: show the letter);
`Kak Anju as Child` (NL Cuccos, IGN: one cucco in a wobbling crate; day unverified); the GS rules' items (guides: none,
Slingshot, roll); exits to Hyrule Field, Carpenter Boss House, House of Skulltula, Impas House, Windmill and Graveyard
`True` (doors in child files); `Drain Well` and the Bottom of the Well exit (NL, Eurogamer: Storms in the windmill);
`Kak Potion Shop Front` `is_child or at_day` (IGN: closed; no child check behind); `Kak Backyard` `is_adult or at_day`
(IGN, NL Cuccos #6: cucco over the fence; night unchecked); `Kak Behind Gate` both ways (no evidence either way); `Kak
Impas Rooftop` Hookshot or trick (adult; IGN, Eurogamer: vines); the Impas Ledge, Rooftop, Odd Medicine Rooftop and
Backyard returns `True` (no evidence against); `Kak Man on Roof` `True` (IGN HP #2); Gold Skulltula rewards (N64 token
counts); `Kak Impas House Freestanding PoH` (reach changes via ledge only); `Kak Windmill Freestanding PoH` (no source
on the child Boomerang; open 2); `Kak Open Grotto Chest` and its exit `True` (IGN: open hole, 5-rupee chest); `Kak
Redead Grotto Chest` rule (same ReDeads and pedestal). Low priority: pots, child crates, the wonder item, the `Bugs`
drop, open-grotto fairies, bugs and fish, and `Beehive 1/2` (the beehives are in the unmodelled bomb grotto), unchanged.
Adult side (`Kak GS Above Impas House`, the adult Odd Medicine Rooftop and windmill heart piece ways, all matching OoT
Randomizer) left to track B.

Open (in-game check for Kareem):

1. **Is Kak GS Tree there by day?** After meeting Zelda, by day, roll into the narrow tree by the village entrance
   (-74,97,43). If it drops, `Kak GS Tree` loses its night part.
2. **Does the Boomerang fetch the windmill heart piece?** As child, from the windmill floor throw it at the heart piece
   on the beam (1,109,38). If not, drop `can_use(Boomerang)` from `Kak Windmill Freestanding PoH` (OoT Randomizer counts
   it as child logic).
3. **A child route to Impa's roof without the owl?** Try the ladders by Impa's house (-54,105,104), (-46,105,92) or a
   cucco glide. If either reaches Impa's or the cow-shed roof, restore a child path to `Kak Impas Ledge`.
4. **What opens the ReDead grotto by the Kakariko steps?** At the plant ring by Kaepora's tree (HF 163,156,27), try a
   bomb, then the Song of Storms. Rule: `Hyrule Field -> Kak Redead Grotto`. Same test as Hyrule Field open 1.
5. **Are the windmill cuccos there at night?** As child at night, check the cuccos at the fence and on the hill by the
   windmill. If present, the new child path to `Kak Odd Medicine Rooftop` drops `at_day`.

Remake-only checks noticed / for other tracks:

- DeathMountain makes `DMT Owl Flight` `is_child and Dins_Fire` (Kaepora's flow checks Din's Fire), so the child's
  cow-pen heart piece now needs Din's Fire.
- Census links to set: 12902291359202819102 -> `Kak Open Grotto Chest`, 5755485285664292988 -> `Kak Redead Grotto
  Chest`.
- Remake-only, adult: windmill chests 11929552275106311978 ("[Adult]") and 13080955777249750889 ("[Adult Alternative]")
  at (6,130,41), high in the windmill.
- Kakariko's bomb grotto (-20,97,66): gossip stone, seven beehives (three drop blue rupees), butterflies; no OoT
  Randomizer region. Bazaar and Potion Shop actors are adult-only.

### Graveyard (`child_graveyard.toml`)

Sources: IGN Kakariko walkthrough (Graveyard),
https://www.ign.com/wikis/ocarina-of-time-remake/Spiritual_Stone_of_Fire_-_Kakariko_Village_Walkthrough, IGN heart
pieces, https://www.ign.com/wikis/ocarina-of-time-remake/All_Heart_Piece_Locations, Nintendo Life Sun's Song,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-suns-song-switch-2, Nintendo Life heart pieces,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2, Nintendo Life Gold Skulltulas,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2, Nintendo Life
walkthrough hub, https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake, Eurogamer 17
changes, https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, Eurogamer and Polygon Gold Skulltula
guides (local copies in E:/OOTRemake/work/r3/), census and plans/rounds/r2-census.md, placement data (Graveyard_*).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|`Graveyard -> Graveyard Shield Grave`|`is_adult or at_night` -> `is_adult or (at_night and 'Time Flows')`|Main's time decision; IGN: by day the boy threatens to tell, at night Link may pull graves. Shared; adult unchanged.|
|`Graveyard -> Graveyard Heart Piece Grave`|`is_adult or at_night` -> `is_adult or (at_night and 'Time Flows')`|Same.|
|`Graveyard -> Graveyard Dampes House`|`is_adult or at_dampe_time` -> `is_adult or (at_dampe_time and 'Time Flows')`|Time decision; door Obj_Graveyard_Door_A_01 11317197928420415449 checks `Npc_Hylia_Dampe_001_Child_CheckRestrictedDoor`. Shared.|
|`Graveyard Dampe Gravedigging Tour`|`is_child and at_dampe_time` -> `is_child and (at_dampe_time and 'Time Flows')`|IGN, NL HP #9: at night; Eurogamer: tour reworked, Link leads Dampé; HeartPieceAnchor `GraveYard_DiggingHoleTour_Drop_HeartPiece`.|
|`Graveyard GS Wall`|`can_use(Boomerang) and (at_night or ...)` -> `... ((at_night and 'Time Flows') or ...)`|Time decision; 229475726653285413 Nocturnal, behind Dampé's house; NL GS #21: night, Boomerang.|
|`Graveyard Shield Grave Chest`|`True` -> `is_adult or Sticks or Kokiri_Sword or can_use(Dins_Fire)`|Stricter: Enemy_ReDead 17994273783244561622 1 m from the chest; IGN: defeat the ReDead, then open. Kill items from OoT Randomizer's redead grotto chest. Shared (open 1).|
|`Graveyard Heart Piece Grave Chest`|`can_play(Suns_Song)` -> `True`|Looser: NL HP #8: Sun's Song no longer needed; IGN HP #4: no enemies; plain placed chest 9622128545943056087 (no appear event).|
|`Graveyard Royal Familys Tomb Chest`|`has_fire_source` -> `n64_only`|No chest or torch in the tomb (data: Keese, ReDeads, song monument); IGN, NL: Keese room, ReDead room, tablet; no census id. Was Bombs (5).|

Checked, unchanged: `Graveyard GS Bean Patch` `can_plant_bugs and can_child_attack` (all guides: bugs into soft soil; no
night flag); `Graveyard -> Graveyard Royal Familys Tomb` `can_play(Zeldas_Lullaby)` (NL Sun's Song; open 2); `Song from
Royal Familys Tomb` attack list (four Keese seal room; IGN, NL: Slingshot); `Graveyard -> Graveyard Dampes Grave`
`is_adult` (adult race); exits back to Graveyard and Kakariko `True` (no evidence against); `Graveyard Freestanding PoH`
child trick part (off by default); Shield Grave `Fairy` `can_blast_or_smash and has_bottle` (wall and pool in a third
grave, same entry rule); `Bugs` (IGN: under the entrance stones); `Graveyard Warp Pad Region -> Shadow Temple Entryway`
(shared; no evidence); `Graveyard Dampe Race Freestanding PoH` (remake.toml type override kept). Low priority: the
`Fairy` drops (sticks by day, bean and Song of Storms, warp pad region), unchanged. Adult side (`Graveyard Freestanding
PoH` crate, `Graveyard GS Wall` with the Hookshot) left to track B.

Open (in-game check for Kareem):

1. **Shield chest without a weapon?** At night, no sword, sticks or Din's Fire: open the chest past the ReDead in the
   second grave right of the tomb path; also try Sun's Song. If it opens, relax `Graveyard Shield Grave Chest`.
2. **Does the Royal tomb open before Sharp and Flat?** Play Zelda's Lullaby on the Triforce before touching the harp
   graves. If it stays shut until both Poe brothers fall, `Graveyard -> Graveyard Royal Familys Tomb` needs a child
   attack.
3. **Is there a chest in the Royal tomb?** With Din's Fire, clear the Keese room, look for torches or a chest and cast
   Din's Fire there. If a chest appears, remove `n64_only` from `Graveyard Royal Familys Tomb Chest`.

Remake-only checks noticed / for other tracks:

- Track B: `Graveyard Freestanding PoH` has no crate (Obj_Heart_Piece 2157466067026784951 on a ledge above the soft
  soil; NL HP #10: bean as child, ride as adult), so `can_break_crate` goes and `Graveyard Freestanding PoH Crate` looks
  N64-only.
- Track B: `Graveyard GS Wall` also falls to the Hookshot or Longshot (Eurogamer GS); OoT Randomizer asks the Boomerang
  only.
- Remake-only: Dampé's race goal chests, census 234006393181394602 (TBox_Rupee_Red) and 4322670163630771947
  (TBox_Rupee_Blue) (`MiniGame_DampeRace_OpenGoalTBox`).
- For Main: the flower grave (hole (4,101,6), bombable wall, fairy pool) has no OoT Randomizer region; the tomb chest's
  `n64_only` rests on data and guides only.

### Death Mountain Trail (`child_death_mountain_trail.toml`)

Sources: Nintendo Life walkthrough hub,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake, Nintendo Life Dodongo's Cavern,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-dodongo-cavern-walkthrough-switch-2, Nintendo Life Great Fairy
fountains, https://www.nintendolife.com/guides/zelda-ocarina-of-time-great-fairy-fountain-locations-all-switch-2,
Nintendo Life wallet,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-bigger-wallet-upgrade-more-rupees-switch-2, IGN Goron City and
Lost Woods,
https://www.ign.com/wikis/ocarina-of-time-remake/Spiritual_Stone_of_Fire_-_Goron_City_and_the_Lost_Woods_Walkthrough,
Eurogamer Death Mountain Trail, https://www.eurogamer.net/zelda-ocarina-of-time-death-mountain-trail, Eurogamer
Kakariko, https://www.eurogamer.net/zelda-ocarina-of-time-kakariko-village, Eurogamer 17 changes,
https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, games.gg Great Fairies,
https://games.gg/the-legend-of-zelda-ocarina-of-time-2026/guides/ocarina-of-time-remake-great-fairy-locations-rewards-and-costs,
games.gg heart pieces,
https://games.gg/the-legend-of-zelda-ocarina-of-time-2026/guides/ocarina-of-time-remake-heart-pieces-all-36-locations/,
Game8 heart pieces, https://game8.co/games/Zelda-Ocarina-of-Time/archives/616225, Respec 100%,
https://www.respec.net/guide/276-the-legend-zelda-ocarina-time-remake-walkthrough-100-completion-guide-with-all-switch-2-changes,
RPG Site 100%,
https://www.rpgsite.net/guide/21671-the-legend-zelda-ocarina-time-remake-minimalist-100-walkthrough-all-items-gold-skulltula-tokens-heart-pieces,
Eurogamer and Polygon Gold Skulltula guides (local copies E:/OOTRemake/work/r3/gs-guide-*.txt), placement data
(actors.py DeathMountainTrail), event flow Npc_Kaepora_DeathMountainTrail.

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|exit `Death Mountain -> Dodongos Cavern Beginning`|`has_explosives or Progressive_Strength_Upgrade or is_adult` -> `Progressive_Strength_Upgrade or is_adult`|NL, IGN, Eurogamer, Respec: bracelet bomb flower by the fence breaks it. Boulder 9966036182374691433 takes no damage; scripted break via flower 12145309744777105449. Open 1.|
|location `DMT GS Bean Patch`|`... (has_explosives or Progressive_Strength_Upgrade or (logic_dmt_soil_gs and can_use(Boomerang)))` -> `has_explosives or` dropped|Soil sits by the bracelet-only boulder (Polygon: child, bracelet, bug; IGN: inside the tunnel). GS 17425319789138387506, plain, (-45,109,-20). Open 5.|
|event `Death Mountain -> Fairy` (bean-plant fairy)|`... and (has_explosives or Progressive_Strength_Upgrade)` -> `... and Progressive_Strength_Upgrade`|Same soft soil behind the same boulder; low priority, changed for consistency.|
|exit `Death Mountain -> DMT Storms Grotto`|`can_open_storm_grotto` -> `can_play(Song_of_Storms)`|Main's decision (Eurogamer 17 changes: grottos visible, Stone of Agony now Echo Gem); IGN: alcove right of Goron City entrance; cover 10160504174807262319. Shared rule.|
|location `DMT Storms Grotto Chest`|`True` -> `n64_only`|Grotto 1154915296159103350 holds 5 Baby Dodongos, 3 bomb flowers, 6 rupees, no chest; census: one trail chest against OoT Randomizer's two.|
|exit `Death Mountain Summit -> DMT Owl Flight`|`is_child` -> `is_child and Dins_Fire`|Owl flow Npc_Kaepora_DeathMountainTrail offers the flight only with `IsGet.Item_DinFire` set; Eurogamer Kakariko: flight after the summit Great Fairy. Open 3.|
|event `DMT Great Fairy Fountain -> Great Fairy Met` (new)|none -> `can_play(Zeldas_Lullaby)`|Main's request; games.gg: first Great Fairy must be this one or Hyrule Castle's, else the Lullaby summons no other. Fee not modelled.|

Checked, unchanged: exits to Kakariko and Goron City `True` (NL, IGN, Eurogamer walk them; the Red Tektites do not
gate); summit climb, child part `here(can_blast_or_smash)` (NL, IGN; three bombable rocks on the path; open 2);
`DMT Chest` (bombable WallCrack 12869454506934697528 in front; no guide, trick stays off); `DMT Freestanding PoH` child
part `can_take_damage` (Eurogamer, Game8: backflip over the lower fence from the bomb-flower ledge; heart piece
715147239509454487; games.gg lists only the adult bean way; open 4); `DMT GS Near Kak` `can_blast_or_smash` (Eurogamer,
Polygon: bomb the wall near Kakariko; plain actor, so no night despite Eurogamer); summit to `DMC Upper Local` and back
down `True` (child enters the crater from the summit; kept per Main); cow grotto `here(can_blast_or_smash)` (Respec;
bombable rock 8580335210618464267); Great Fairy fountain `here(can_blast_or_smash)` (NL, games.gg: bomb the wall left of
the owl); `DMT Great Fairy Reward` `can_play(Zeldas_Lullaby)` (NL, games.gg; gives Din's Fire, plus magic per games.gg);
returns from the fountain and grottos, and the owl's landing on Impa's roof, `True` (NL, IGN, games.gg). Low priority,
unchanged: rock rupees, summit `Fairy` and `Bugs`, cow grotto rupees and heart (no rupee or heart actor there, look
absent), storms grotto `Fairy`, `Bugs`, `Fish` (no gossip stone or fish inside), beehives (no beehive actor; n64_only
candidates if beehives get shuffled); `DMT Cow Grotto Cow` is already n64_only (remake.toml). No child rule here uses
`at_night` or `at_dampe_time`. Adult-only rules left to track B: Biggoron and his trades, `Prescription Access`, the
adult parts of the cavern and summit exits, the adult bean branches.

Open (in-game check for Kareem):

1. **Do Bombs break the Dodongo's Cavern boulder?** Child with Bombs or Bombchus, no bracelet: blast the boulder at the
   cavern mouth and the fenced bomb flower. If it breaks, restore `has_explosives` in the cavern exit,
   `DMT GS Bean Patch` and the bean `Fairy`.
2. **Do the summit wall's Skullwalltulas need a ranged weapon?** Child with Bombs only (no Slingshot or Boomerang):
   climb the wall below the owl (three Skullwalltulas, y 191-203). If they knock Link off, the summit exit's child part
   needs that weapon.
3. **Does the owl fly a child without Din's Fire?** At the summit without Din's Fire, talk to him: expect no offer.
   After the item patch, does Din's Fire from another check set `IsGet.Item_DinFire`? Rule: `DMT Owl Flight`.
4. **Can a child reach the trail heart piece?** From the bracelet bomb-flower ledge, backflip over the lower fence onto
   it (Eurogamer: fiddly). If impossible, drop the child part `can_take_damage` of `DMT Freestanding PoH` (shared rule).
5. **Does the soft soil work before the boulder breaks?** With the boulder intact, drop bugs on the soil by the cavern
   (Eurogamer: outside; IGN: inside the tunnel). If a killable Gold Skulltula appears, `DMT GS Bean Patch` no longer
   needs the bracelet.

Remake-only checks noticed / for other tracks:

- Kakariko/Graveyard: the owl flight now needs Din's Fire and is the child's only way to Impa's rooftop heart piece
  (owner told).
- Great Fairy fees rise per fairy met (games.gg: 25, 50, 100, 200, 300, 500 in the usual order; default wallet 200), so
  the fifth and sixth need bigger wallets; not modelled, reported to Main.
- Track B: `DMT GS Above Dodongos Cavern` and `DMT GS Falling Rocks Path` sit behind hammer rocks (Eurogamer, Polygon);
  both plain actors, though OoT Randomizer and Eurogamer say night. The adult bean branch of `DMT Freestanding PoH`
  keeps `has_explosives`, which no longer opens the soil.
- Remake-only: the storms grotto's six placed rupees (red 991975198297951915) and the cow grotto's gossip stone; no new
  census check.

### Death Mountain Crater (`child_death_mountain_crater.toml`)

Sources: Eurogamer Death Mountain Crater, https://www.eurogamer.net/zelda-ocarina-of-time-death-mountain-crater,
games.gg heart pieces,
https://games.gg/the-legend-of-zelda-ocarina-of-time-2026/guides/ocarina-of-time-remake-heart-pieces-all-36-locations/,
games.gg Great Fairies,
https://games.gg/the-legend-of-zelda-ocarina-of-time-2026/guides/ocarina-of-time-remake-great-fairy-locations-rewards-and-costs,
Game8 heart pieces, https://game8.co/games/Zelda-Ocarina-of-Time/archives/616225, Nintendo Life Great Fairy fountains,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-great-fairy-fountain-locations-all-switch-2, Respec 100%,
https://www.respec.net/guide/276-the-legend-zelda-ocarina-time-remake-walkthrough-100-completion-guide-with-all-switch-2-changes,
RPG Site 100%,
https://www.rpgsite.net/guide/21671-the-legend-zelda-ocarina-time-remake-minimalist-100-walkthrough-all-items-gold-skulltula-tokens-heart-pieces,
Eurogamer and Polygon Gold Skulltula guides (local copies E:/OOTRemake/work/r3/gs-guide-*.txt), placement data
(actors.py DeathMountainCrater).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|location `DMC Deku Scrub`, vanilla item (rule unchanged)|`Buy Bombs (5) for 35 Rupees` -> `Piece of Heart`|Eurogamer: child drops left from the top to the scrub's ledge; heart piece, 100 rupees. games.gg: Ice Cavern's piece moved here. Scrub 2518138296199711695.|

Checked, unchanged: the child enters by `Death Mountain Summit -> DMC Upper Local` `True` (Eurogamer, Respec, RPG Site),
so `DMC Upper Nearby -> DMC Upper Local` and `DMC Central Nearby -> DMC Central Local` (`can_use(Goron_Tunic)`) never
apply to a child; `DMC Upper Nearby -> Death Mountain Summit` `True`; upper grotto `here(can_blast_or_smash)` (bombable
rock 5524931827254348969; no guide); `DMC GS Crate` (Eurogamer, Polygon, Respec, RPG Site; crate 1617141603420049765 a
little further in, still on the upper level); Upper Local exits to Upper Nearby and Ladder Area `True` (Eurogamer,
Game8: drop or climb down to the scrub's ledge), to the Pierre platform (only adult rupees there) and Central Nearby
(adult items); `DMC Deku Scrub` rule `is_child and can_stun_deku` (guides use the Slingshot, a Deku Nut or a shield
reflection; 100 rupees fits the default 200 wallet, not modelled); Central Local by Bolero: `DMC GS Bean Patch`
`can_plant_bugs and can_child_attack` (Eurogamer, Polygon: soil by the warp pad; plain actor 6397182598322965076), exits
`-> DMC Central Nearby` `True` and `-> DMC Fire Temple Entrance` `is_adult or shuffle_dungeon_entrances`;
`DMC Upper Grotto Chest` `True` (census 1158729434763801603). Low priority, unchanged: `Fairy` events (Upper Local
gossip stone behind a WallCrack, Central Local bean and Song of Storms, Upper Grotto gossip stone), grotto `Bugs` and
`Fish`, `DMC Child Red/Blue Rupee 1-6`, beehives (no beehive actor). No child rule here uses a time or grotto helper.
Adult-only rules left to track B: Ladder Area exits, the lower and central regions, Fire Temple entrance, Great Fairy,
hammer grotto, Pierre platform rupees, `DMC Volcano Freestanding PoH`, `Sheik in Crater`, `DMC Wall Freestanding PoH`.

Open (in-game check for Kareem):

None that change a rule; the scrub's 100-rupee price and the heat timer (games.gg: young Link burns the whole time) are
not modelled.

Remake-only checks noticed / for other tracks:

- Census: link `DMC Deku Scrub` to 'Death Mountain Crater Scrub (Obj_Heart_Piece)' (the area's only scrub) and
  `DMC Upper Grotto Chest` to chest 1158729434763801603.
- Track B: the hammer grotto holds no scrub, so `DMC Deku Scrub Grotto Left/Right/Center` look n64_only; a remake-only
  purple-rupee chest 9128916506605227251 appears there instead (`DeathMountainCrater_SecretHole_AppearTreasureBox`;
  census 'Death Mountain Crater Chest (TBox_Rupee_Purple)').
- Track B: `DMC Wall Freestanding PoH`: Eurogamer, Game8 and games.gg take it as child from the summit, down the net
  within the heat timer (Game8: about 5 hearts, full health). `DMC Volcano Freestanding PoH`: bean planted by the warp
  pad as child, ridden as adult.
- Track B: the Great Fairy sits behind hammer rocks near (-34,121,24); NL, games.gg: Megaton Hammer, magic meter
  upgrade, 200 rupees in the usual order; needs `Great Fairy Met` first.

### Goron City (`child_goron_city.toml`)

Sources: Nintendo Life walkthrough hub,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake, Nintendo Life Dodongo's Cavern,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-dodongo-cavern-walkthrough-switch-2, IGN Goron City and Lost
Woods,
https://www.ign.com/wikis/ocarina-of-time-remake/Spiritual_Stone_of_Fire_-_Goron_City_and_the_Lost_Woods_Walkthrough,
Eurogamer Goron City, https://www.eurogamer.net/zelda-ocarina-of-time-goron-city, Game8 heart pieces,
https://game8.co/games/Zelda-Ocarina-of-Time/archives/616225, games.gg heart pieces,
https://games.gg/the-legend-of-zelda-ocarina-of-time-2026/guides/ocarina-of-time-remake-heart-pieces-all-36-locations/,
Respec 100%,
https://www.respec.net/guide/276-the-legend-zelda-ocarina-time-remake-walkthrough-100-completion-guide-with-all-switch-2-changes,
RPG Site 100%,
https://www.rpgsite.net/guide/21671-the-legend-zelda-ocarina-time-remake-minimalist-100-walkthrough-all-items-gold-skulltula-tokens-heart-pieces,
Nintendo Life wallet,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-bigger-wallet-upgrade-more-rupees-switch-2, Eurogamer and
Polygon Gold Skulltula guides (local copies E:/OOTRemake/work/r3/gs-guide-*.txt), placement data (actors.py GoronCity).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|exit `Goron City -> GC Spinning Pot`|`... (Bombs or (Progressive_Strength_Upgrade and logic_goron_city_pot_with_strength) or (has_bombchus and logic_goron_city_pot))` -> `... (Bombs or Progressive_Strength_Upgrade or (has_bombchus and logic_goron_city_pot))`|Eurogamer: light the torches, throw bomb flowers into the pot (bracelet). Game8: flowers by the Lost Woods wall. Respawning flowers 7966326031307316945, 4547230728780892731. Open 2.|

Checked, unchanged: Darunia's door, child part `can_play(Zeldas_Lullaby)` (NL, IGN, Eurogamer; Triforce mat at the
shutter); `GC Darunias Joy` `is_child and can_play(Sarias_Song)` (NL, IGN, Eurogamer, Respec); `Goron City Child Fire`
by Sticks in Darunia's room (IGN: two torches there) or Din's Fire (no evidence against; games.gg: it lights torches);
shop door, child part `has_explosives or Progressive_Strength_Upgrade or 'Goron City Child Fire'` (IGN, Respec: lit
stick on the bomb flower; Eurogamer: bracelet; bombable WallCrack 12783164907437496571; open 3) and shop slots 1-8
`True` (census: 8 child slots); `GC Woods Warp Open` and the Lost Woods shortcut both ways (IGN, Respec: bomb flowers by
the cracked wall; the wall also breaks with bombs or hammer); `GC Rolling Goron as Child` (Respec, RPG Site: bomb in
front of the sign he rolls past; Bigger Bomb Bag, Eurogamer says Biggest; bracelet trick stays off);
`GC GS Boulder Maze` `is_child and has_explosives` (Eurogamer, Polygon, Respec, RPG Site; crate in the maze's north-west
corner, plain actor); maze chests (Respec, RPG Site: bomb through the maze): Left needs hammer or silver gauntlets,
never a child; Center and Right `can_blast_or_smash or ...`; from rock positions [inference], red 4402942101476009858
behind hammer rocks and a silver row = Left, blues 1176975953041865014 and 14647422914070455120 in the bombable west
pocket = Center/Right, purple 3870071239709713434 between silver boulders = remake-only adult chest (open 1);
`GC Pot Freestanding PoH` `True` (games.gg, Eurogamer, Game8, Respec; event heart piece, anchor 3483734707455267135);
return exits `True`. Low priority, unchanged: `Fairy` (gossip stones in Medigoron's room and the maze), `Bugs`,
`Deku Stick Drop`, pots, spinning-pot drops, `GC Boulder Maze Crate` (the maze's only crate is the GS one; the rupee
crate may be gone). No time or grotto helper here. Adult-only rules left to track B: Medigoron, Rolling Goron as adult,
`GC GS Center Platform`, the grotto platform and grotto, Darunia's chamber to the crater, Darunia's door adult part.

Open (in-game check for Kareem):

1. **Which maze chests open with Bombs only?** As child, bomb into the top floor's west boulder room. Expected: two blue
   chests by the gossip stone, the GS crate; not purple (north, grey/white boulders) or red (south-west, dark rocks).
   Rules: `GC Maze Center/Right Chest`.
2. **Do bomb flowers stop the spinning pot?** Child, bracelet, no Bomb Bag: light the four torches (Darunia's-room
   stick), throw Lost Woods-wall bomb flowers into the pot until it stops on the smile. Else restore the trick on
   `GC Spinning Pot`.
3. **Does the bracelet open the shop door?** Child with only the bracelet: drop a bomb flower at the sealed bottom-floor
   door. Expected yes (Eurogamer); the current rule already allows it.

Remake-only checks noticed / for other tracks:

- Census: 6 chests against OoT Randomizer's 3, none linked. Proposed: red 4402942101476009858 = `GC Maze Left Chest`;
  blues 1176975953041865014 / 14647422914070455120 = `GC Maze Center Chest` / `GC Maze Right Chest` (order open); the
  purple maze chest is remake-only (silver gauntlets).
- Track B: GC Grotto has no scrub or beehive actor, so `GC Deku Scrub Grotto Left/Right/Center` and `GC Grotto Beehive`
  look n64_only; two remake-only chests (green 9159710900681116662, purple 10944569637726152230) appear via
  `GoronCity_SecretHole_AppearTreasureBox`.
- Track B: `GC Medigoron`: the Giant's Knife costs 200 rupees (Eurogamer) and the default wallet holds 200 (NL), so
  `Progressive_Wallet` looks unneeded [inference].
- Track B: `GC GS Center Platform` is a plain actor (18139423190738716302) in adult files only (Hookshot); the adult
  rolling Goron is three Darunia Jr actors (flag `SageOfFire_Step01_DaruniaJr_BombHit`).

### Zora's River (`child_zora_river.toml`)

Sources: Nintendo Life Zora's River and Domain,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-zora-river-zora-domain-switch-2, Nintendo Life heart pieces,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2, Nintendo Life Gold Skulltulas,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2, Eurogamer heart
pieces, https://www.eurogamer.net/all-heart-pieces-locations-zelda-ocarina-of-time, Eurogamer 17 changes,
https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, Eurogamer and Polygon Gold Skulltula guides
(local copies E:/OOTRemake/work/r3/gs-guide-*.txt), placement data (actors.py ZoraRiver).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|location `ZR GS Tree` (region `ZR Front` -> `Zora River`)|`is_child and can_child_attack and can_bonk` -> `can_plant_bugs and can_child_attack`|Now the bean seller's soft soil, past the boulders (03-game-data section 11); GS 12370559827741970774 `IsMagicBeanSoil`; Eurogamer, Polygon, NL GS #49: bugs.|
|location `ZR GS Ladder`|`(at_night or gold_skulls_ignore_daytime)` -> `((at_night and 'Time Flows') or gold_skulls_ignore_daytime)`|Eurogamer 17 changes: time flows only after meeting Zelda (Main's decision); actor 8695975724114049706 is Nocturnal.|
|exit `Zora River -> ZR Storms Grotto`|`can_open_storm_grotto` -> `can_play(Song_of_Storms)`|Eurogamer 17 changes: grottos visible, Stone of Agony now Echo Gem (Main's decision); cover 5489068764052953067 at (-78,99,-17). Shared rule.|
|locations `ZR Deku Scrub Grotto Rear`, `ZR Deku Scrub Grotto Front`|`can_stun_deku` -> `n64_only`|Storms grotto holds a gossip stone, butterfly fairy, four pots; no Enemy_Scrub_Business anywhere in ZoraRiver (03-game-data section 5). Open 3.|
|event `ZR Open Grotto -> Fish`|`has_bottle` -> `False`|Open grotto: chest, gossip stone, grass, shallow pool, Cucco; no fish actor in ZoraRiver. Shared; no practical effect (Jabu's fish comes from the Domain).|

Checked, unchanged: `ZR Front -> Zora River` `is_adult or has_explosives` (NL: bomb the two entrance boulders);
`ZR Magic Bean Salesman` `is_child` (NL HP #10; seller past the boulders, child files only); the frog song checks (NL HP
#14, Eurogamer HP; frogs in child files only) and `ZR Frogs Ocarina Game` (Eurogamer: all six songs incl. Song of
Storms; NL lists five; OoT Randomizer's six kept, stricter); `ZR Near Open Grotto Freestanding PoH` child part
`is_child` (shared; Eurogamer HP: bean seller's Cucco to the vine ledge, second Cucco in the uncovered open-grotto hole,
glide to the pillar; NL says bomb, open 1); `ZR Near Domain Freestanding PoH` child part `is_child` (NL HP #13,
Eurogamer: Cucco glide from the river start); waterfall `can_play(Zeldas_Lullaby) or ...`, tricks off (NL; triforce
point at the waterfall); fairy grotto `here(can_blast_or_smash)` (bombable rock 16547116969322393756; eight fountain
fairies) and its `Fairy` `has_bottle`; open grotto `True` (no cover) with `ZR Open Grotto Chest` `True` (census
8838426083116998768), `Fairy`, `Bugs`; Lost Woods underwater exit `can_dive or can_use(Iron_Boots)` (gate about 6 m
deep; no remake source); `ZR GS Ladder` attack part (open 2); all other exits `True`. Low priority, unchanged: river
`Fairy` and `Bugs` (a liftable rock 9080915605353397341 drops a bug), wonder items, beehives (no beehive actor; n64_only
candidates). Adult-only rules left to track B: `ZR GS Above Bridge`, `ZR GS Near Raised Grottos`, the adult parts of
both heart pieces.

Open (in-game check for Kareem):

1. **Does the grotto-hole heart piece need a bomb?** Without bombs, take the bean seller's Cucco to the vine ledge,
   enter the hole at its south end, glide to the pillar with its Cucco. If blocked:
   `ZR Near Open Grotto Freestanding PoH` child part adds `has_explosives`.
2. **Does `ZR GS Ladder` need the Boomerang?** At night (after Zelda), child with only Sticks or Kokiri Sword: kill the
   Gold Skulltula on the ivy below the Domain entrance (113,112,-49). If only the Boomerang works (NL GS #50), add
   `Boomerang`.
3. **Is the storms grotto free of scrubs?** In the Song of Storms grotto by the bean seller (circle of rocks,
   (-78,99,-17)), confirm no scrubs inside. Rule: the two `n64_only` scrubs.

Remake-only checks noticed / for other tracks:

- Track B: `ZR GS Above Bridge` and `ZR GS Near Raised Grottos` are both Nocturnal (as OoT Randomizer); Eurogamer: the
  waterfall one needs the Longshot; NL, Polygon: Hookshot for both.
- Track B: `ZR Near Domain Freestanding PoH`: adult can jump across (Eurogamer; OoT Randomizer: Hover Boots or a trick);
  `ZR Near Open Grotto Freestanding PoH` adult via the bean plant, as OoT Randomizer.
- Remake-only: none new; the storms grotto now has a gossip stone and a butterfly fairy (possible extra `Fairy` source,
  not added).

### Zora's Domain (`child_zoras_domain.toml`)

Sources: Nintendo Life Zora's River and Domain,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-zora-river-zora-domain-switch-2, Nintendo Life heart pieces,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2, Eurogamer Zora's Domain,
https://www.eurogamer.net/zelda-ocarina-of-time-zora-domain, Eurogamer 17 changes,
https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, games.gg Great Fairies (Din's Fire),
https://games.gg/the-legend-of-zelda-ocarina-of-time-2026/guides/ocarina-of-time-remake-great-fairy-locations-rewards-and-costs,
placement data (actors.py ZoraDomain).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|exit `Zoras Domain -> ZD Storms Grotto`|`can_open_storm_grotto` -> `can_play(Song_of_Storms)`|Eurogamer 17 changes: grottos visible, Stone of Agony now Echo Gem (Main's decision); cover 13590128656727522529 at (17,100,-18). Shared rule.|
|event `ZD Storms Grotto -> Fairy`|`has_bottle` -> `False`|The room under the hole holds six blue rupees, no fairy; no fountain-fairy actor in any ZoraDomain file. Shared (both ages).|

Checked, unchanged: `ZD Diving Minigame` `is_child` (NL, Eurogamer: five scales in 40 s, Silver Scale; child files
only); `ZD Chest` `can_use(Sticks)` (NL HP #16, Eurogamer: a stick lit at the throne-room torch lights the eight timed
torches, 45 s; chest 3130048366421939233 holds the heart piece; Din's Fire not adopted, open 1); `Fish`
`is_child and has_bottle` (NL, Eurogamer: pool under the stairs to the King; five fish; the shop also sells fish);
`Zoras Domain -> Lake Hylia` `is_child and can_dive` (NL, Eurogamer: portal at the bottom of the diving pool, about 6 m
deep); Ruto's letter delivery and `Deliver Letter` (NL, Eurogamer: show the bottle to King Zora); `ZD Behind King Zora`
child part (the fountain entrance is behind the King) and its exits; `ZD Shop` `is_child or Blue_Fire` (child shop
actors), shop items `True`; waterfall, frog-timeout, grotto and shop returns `True`. Low priority, unchanged:
gossip-stone `Fairy`, stick and nut drops, pots, beehives (no beehive actor). Adult-only rules left to track B:
`King Zora Thawed`, `Eyeball Frog Access`, `ZD King Zora Thawed`, `ZD Trade Prescription`, `ZD GS Frozen Waterfall`.

Open (in-game check for Kareem):

1. **Does Din's Fire light the torches?** Child with Din's Fire and magic, no sticks: light every timed torch (King's
   stairs, beside the shop, water's edge, walkway, two behind the waterfall) before they go out. If yes (games.gg),
   `ZD Chest` adds `or can_use(Dins_Fire)`.
2. **Does the second diving round give a prize?** After the Silver Scale, play again (Eurogamer: harder, scales at
   different depths). A prize would be a remake-only check with no OoT Randomizer location.

Remake-only checks noticed / for other tracks:

- Track B: the Domain thaws after the Water Temple (Eurogamer 17 changes) and the adult shop opens then; OoT Randomizer
  thaws King Zora with `Blue_Fire`; the data has `Adult_Alternative_*` files with the thawed Domain.
- Track B: `ZD GS Frozen Waterfall` actor 9600417828645642589 is plain (not Nocturnal), while OoT Randomizer and
  Eurogamer say night.
- Remake-only: the storms grotto's six blue rupees (freestanding, no check type).

### Zora's Fountain (`child_zoras_fountain.toml`)

Sources: Nintendo Life Zora's River and Domain,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-zora-river-zora-domain-switch-2, Nintendo Life Gold
Skulltulas, https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2,
Nintendo Life Great Fairy fountains,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-great-fairy-fountain-locations-all-switch-2, games.gg Great
Fairies,
https://games.gg/the-legend-of-zelda-ocarina-of-time-2026/guides/ocarina-of-time-remake-great-fairy-locations-rewards-and-costs,
Eurogamer 17 changes, https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, Eurogamer heart pieces,
https://www.eurogamer.net/all-heart-pieces-locations-zelda-ocarina-of-time, Eurogamer and Polygon Gold Skulltula guides
(local copies E:/OOTRemake/work/r3/gs-guide-*.txt), placement data (actors.py ZoraFountain).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|location `ZF GS Above the Log`|`(at_night or gold_skulls_ignore_daytime)` -> `((at_night and 'Time Flows') or gold_skulls_ignore_daytime)`|Eurogamer 17 changes: time flows only after meeting Zelda (Main's decision); actor 7152962033963346563 Nocturnal; NL GS #55, Eurogamer, Polygon: child, night, Boomerang.|
|location `ZF Great Fairy Reward`|`can_play(Zeldas_Lullaby)` -> `can_play(Zeldas_Lullaby) and 'Great Fairy Met'`|games.gg: first Great Fairy must be Death Mountain Trail's or Hyrule Castle's, else others stay away (Main's decision; event set there). Shared rule.|

Checked, unchanged: `ZF GS Tree` `is_child and can_bonk` (NL GS #54, Eurogamer, Polygon: roll into the tree; plain actor
17355397719442343054); Jabu entrance `is_child and Fish` (NL: fish into the shell recess before Jabu-Jabu); Great Fairy
fountain `has_explosives` (NL: bomb the wall in the south corner; WallCrack 15706960959866666216; Farore's Wind, as
N64); return exits to the Domain, from the fountain and from the ice ledge `True`. Low priority, unchanged:
`ZF Near Jabu Pot 1-4`, `Fairy` (two gossip stones, butterflies). Adult-only rules left to track B:
`ZF Iceberg Freestanding PoH`, the ice ledge, underwater and hidden-cave exits and regions.

Open (in-game check for Kareem):

None in game; the Great Fairy fee is a modelling point (below).

Remake-only checks noticed / for other tracks:

- Great Fairy fee not modelled: it rises per fairy met (games.gg: 25 to 500; Farore 100 in the usual order; NL: bigger
  wallet needed for all, start 200). In a random order this may be the fifth or sixth fairy (300 or 500: Adult's or
  Giant's Wallet); needs wallet logic.
- Track B: `ZF Hidden Cave`: Eurogamer GS guide says the remake needs only the silver rocks lifted (bombs on N64 only);
  three silver rocks, four invisible Skulltulas inside. `ZF GS Hidden Cave` is Nocturnal; Polygon says Longshot (OoT
  Randomizer: Hookshot).
- Remake-only: purple-rupee chest 15055117029957340138 at (33,108,2), adult files only (census
  `Zora Fountain Chest (TBox_Rupee_Purple)`, no OoT Randomizer name).

### Lake Hylia (`child_lake_hylia.toml`)

Sources: Eurogamer Lake Hylia, https://www.eurogamer.net/zelda-ocarina-of-time-lake-hylia, Eurogamer Zora's Domain,
https://www.eurogamer.net/zelda-ocarina-of-time-zora-domain, Eurogamer heart pieces,
https://www.eurogamer.net/all-heart-pieces-locations-zelda-ocarina-of-time, Eurogamer 17 changes,
https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2, Nintendo Life Zora's River and Domain,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-zora-river-zora-domain-switch-2, Nintendo Life Scarecrow's
Song, https://www.nintendolife.com/guides/zelda-ocarina-of-time-scarecrows-song-switch-2, Nintendo Life Gold Skulltulas,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2, Eurogamer and
Polygon Gold Skulltula guides (local copies E:/OOTRemake/work/r3/gs-guide-*.txt), placement data (actors.py HyruleField;
the lake, lab and fishing pond are part of Banc HyruleField).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|location `LH GS Lab Wall`|`(at_night or gold_skulls_ignore_daytime)` -> `((at_night and 'Time Flows') or gold_skulls_ignore_daytime)`|Eurogamer 17 changes: time flows only after meeting Zelda (Main's decision); actor 13944703896577680014 Nocturnal on the lab wall; NL GS #31, Eurogamer, Polygon: Boomerang.|
|location `LH GS Small Island`|same night change|Same decision; now at a crawl tunnel's end, south-west corner (Eurogamer, NL GS #30, Polygon). Actor 8655370827943125875 plain; night kept from Eurogamer only. Open 1.|
|locations `LH Deku Scrub Grotto Left`, `Right`, `Center`|`can_stun_deku` -> `n64_only`|LH grotto (under a pushable grave on the island) holds one red-rupee chest, no scrub; HyruleField's three-scrub grotto lies inside Lon Lon Ranch's fences.|

Checked, unchanged: `Bonooru` `is_child and Ocarina` (NL Scarecrow's Song: a made-up song to the lower scarecrow by the
shore); `LH Underwater Item` `is_child and can_dive` (NL, Eurogamer; Ruto's bottle about 6 m deep near the portal exit);
`LH GS Bean Patch` (NL GS #29, Eurogamer, Polygon; soil Gold Skulltula 7014193622407727514);
`Lake Hylia -> Zoras Domain` `is_child and can_dive` (NL; trigger 7-9 m under the surface); `LH Owl Flight` `is_child`
(owl in child files); `LH Grotto` `True` (pushable grave; children push graves in the remake, NL); field, lab and
fishing exits and returns `True`, fishing island child part `is_child` (child swims); `LH Lab Dive` Golden Scale, any
age (Eurogamer; one heart-piece flag for both ages); `LH Child Fishing` `is_child` (Eurogamer: 50 cm fish, 10 rupees to
fish) and `LH Loach Fishing` `True` (no evidence against). Low priority, unchanged: `Fairy`, `Bugs`, underwater and
lab-dive rupees, `LH Grotto Beehive` (no beehive actor). Adult-only rules left to track B: `Scarecrow Song`, `LH Sun`,
`LH Freestanding PoH`, `LH GS Tree`, `Water Temple Lobby`, `Eyedrops Access`, `LH Trade Eyeball Frog`,
`LH GS Lab Crate`, `LH Adult Fishing`.

Open (in-game check for Kareem):

1. **Is `LH GS Small Island` there by day?** Child, daytime: swim the west shore to the south-west ledge, crawl into the
   tunnel (-296,132,598). If the Gold Skulltula is there, drop the night part. Also: can adult reach it (actor also in
   adult files)?

Remake-only checks noticed / for other tracks:

- Lon Lon Ranch (owner told): HyruleField's only three-scrub grotto (seeds, nuts, bombs; hole (-36,151,291)) is inside
  the ranch fences, so it is the ranch's grotto.
- Track B: `LH GS Tree` is Nocturnal, Longshot to the top vines (Eurogamer; rule unchanged); `LH GS Lab Crate` is plain:
  Eurogamer and NL roll into it with Iron Boots, Polygon uses the Hookshot (OoT Randomizer asks both).
- Track B: `LH Freestanding PoH` by bean plant or Scarecrow's Song (Eurogamer), as OoT Randomizer; Water Temple: Iron
  Boots and the Hookshot target above the door (Eurogamer).
- Remake-only: the LH grotto's red-rupee chest 6900843020594897860 (census `Hyrule Field Chest (TBox_Rupee_Red) #4`), no
  OoT Randomizer name.

### Dodongo's Cavern (`child_dodongos_cavern.toml`)

Sources: Nintendo Life walkthrough,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-dodongo-cavern-walkthrough-switch-2, IGN walkthrough,
https://www.ign.com/wikis/ocarina-of-time-remake/Dodongo_Cavern_Dungeon_Walkthrough, QuestFern,
https://questfern.com/oot/guides/dodongos-cavern-walkthrough/, VGC Gold Skulltulas,
https://www.videogameschronicle.com/guide/all-dodongos-cavern-gold-skulltula-locations-in-zelda-ocarina-of-time-switch-2/,
Eurogamer and Polygon Gold Skulltula guides (local copies in E:/OOTRemake/work/r3/), placement data (actors.py
DodongoCavern), plans/03-game-data.md sections 5, 9, r2 and r3 census.

Changed (whole dungeon, both ages; region and location names drop the `Dodongos Cavern` prefix):

|Rule|Was -> now|Evidence|
|---|---|---|
|region `Bomb Bag Ledge` (new)|part of `Far Bridge` -> own region (room 13 upper ledge, room 17 passage)|WallCrack 13202633467597206724 (30,115,-23) splits the ledge from the hall's upper floor; NL, IGN, QuestFern: bomb the wall behind the Bomb Bag chest.|
|`Bomb Bag Chest`|region `Far Bridge` -> `Bomb Bag Ledge`|Chest 12161709650443144121 at (39,116,-23), east of the wall; IGN: the passage from the upper Lizalfos ends at it.|
|`Double Eye Switch Room Pot 1`|region `Far Bridge` -> `Bomb Bag Ledge`|Room 17 (two eye switches, two fire walls) lies between the upper Lizalfos and the ledge, not on the bridge.|
|`Double Eye Switch Room Pot 2`|region `Far Bridge` -> `Bomb Bag Ledge`|As Pot 1.|
|`Upper Lizalfos -> Far Bridge`|`is_adult or Sticks or Slingshot or Bombs or Kokiri_Sword` -> `False`|The upper Lizalfos lead to the ledge, not the bridge; the bombable wall is between.|
|`Upper Lizalfos -> Bomb Bag Ledge` (new)|none -> `(is_adult or Sticks or Slingshot or Bombs or Kokiri_Sword) and (can_use(Slingshot) or can_use(Bow))`|OoTR fight rule plus room 17's two timed eye switches (LimitTime 10; NL, IGN, QuestFern). Child needs the Slingshot one room earlier anyway.|
|`Bomb Bag Ledge -> Upper Lizalfos` (new)|none (bridge side was `True`) -> `can_use(Slingshot) or can_use(Bow)`|Back through room 17's timed eye switches and fire walls; stricter, matters only for an adult arriving by Hover Boots or Longshot.|
|`Bomb Bag Ledge -> Far Bridge` (new)|same region -> `here(has_explosives)`|The bombable wall (NL, IGN, QuestFern); no Bomb Flower on the ledge (blade room's one is below); Hammer unchecked, so not allowed.|
|`Far Bridge -> Upper Lizalfos`|`True` -> `False`|The bridge reaches the upper Lizalfos only through the Bomb Bag ledge.|
|`Far Bridge -> Bomb Bag Ledge` (new)|none -> `here(has_explosives)`|Same wall from the hall side; that it breaks from this side is unchecked (open 1).|
|`Climb -> Far Bridge`|`is_adult and (logic_dc_jump or Hover_Boots or Longshot)` -> `False`|OoTR's adult jump from the blade room lands on the Bomb Bag ledge, which the wall cuts off from the bridge.|
|`Climb -> Bomb Bag Ledge` (new)|none -> `is_adult and (logic_dc_jump or Hover_Boots or Longshot)`|OoTR rule moved to the ledge it reaches; NL: one leaps from the ledge onto the blade room's tall platforms. Adult; open 5.|
|`Blade Room Pot 1`|`... or at('Dodongos Cavern Far Bridge', True)` -> `... or at('Dodongos Cavern Bomb Bag Ledge', True)`|NL: from the Bomb Bag chest leap south onto the tall platforms for the pots; the ledge is now its own region.|
|`Blade Room Pot 2`|`... or at('Dodongos Cavern Far Bridge', True)` -> `... or at('Dodongos Cavern Bomb Bag Ledge', True)`|As Pot 1.|
|`GS Alcove Above Stairs`|`can_use(Hookshot) or can_use(Boomerang)` -> `has_explosives`|Moved check: GS 4565265801822094851, room 18 floor, behind WallCrack 1823997448213534774 off the skull bridge; Eurogamer, Polygon: Bombs; IGN, NL, VGC: bombable wall.|
|`GS Vines Above Stairs`|`at('Dodongos Cavern Climb', True) or (...)` -> `at('Dodongos Cavern Climb', can_use(Slingshot) or can_use(Boomerang) or can_use(Bow) or can_use(Hookshot)) or (...)`|GS 8470399761714006011 about 5 m up the mesh by a Skullwalltula; IGN, Eurogamer, QuestFern: shoot it, then climb; Polygon: no item (stricter kept). Open 3.|
|`Boss Room Chest`|`True` -> `n64_only`|No chest in room 21 (cracked floor) or 22 (boss); all nine DC chests elsewhere; r2 census unmatched; IGN, NL: bomb the floor, drop.|
|`Deku Scrub Lobby`|OoTR scrub rule -> `n64_only`|Dungeon's only Enemy_Scrub_Business is 7388739057158296701 in room 7; IGN walks both hall alcove sides, no scrub; census has one DC scrub.|
|`Deku Scrub Near Bomb Bag Left`|OoTR scrub rule -> `n64_only`|Only scrub is room 7's; the blade room holds a Bomb Flower, chests, pots, spike traps (IGN, NL); census has one DC scrub.|
|`Deku Scrub Near Bomb Bag Right`|OoTR scrub rule -> `n64_only`|As Left.|

Checked, unchanged: entrance and hall: `Beginning -> Lobby` (Bomb Flowers at the cracked wall; all guides), `Beginning
-> Death Mountain` and `Farores Wind Warp` (entrance actor; generic), Lobby `Fairy` (Gossip Stone behind a crack; IGN),
`Map Chest`, `Lobby -> Lower Right Side`, `Compass Chest` and `Deku Scrub Side Room Near Dodongos` `can_blast_or_smash
or Strength` (wall cracks, Bomb Flowers nearby; NL, IGN, QuestFern), `Lobby -> Far Bridge` (lift shortcut switch; IGN,
QuestFern), `Lobby -> Mouth` (trick off); torches and stairs: `Lobby -> Staircase Room` (light a Deku Stick; guides),
`Lower Right Side -> Torch Room` (guides fight with the sword; open 6), `Staircase Room -> Climb` (Bomb Flower into the
gap; open 7), `Bomb Flower Platform Chest` `True` in Climb (right or stricter either way), `Climb -> Before Upper
Lizalfos` (block, ladders, Bomb Flower; guides), `Before Upper Lizalfos -> Upper Lizalfos` (shoot the timed eye; all
guides), `End of Bridge Chest` `can_blast_or_smash` (bomb the bridge-end wall; NL, IGN), `Far Bridge -> Mouth`
`has_explosives` (bombs into both eyes; guides), return exits `True`; Gold Skulltulas: `GS Side Room Near Lower
Lizalfos` (Baby Dodongo or bomb; IGN, Eurogamer, Polygon), `GS Scarecrow` (adult Scarecrow's Song plus Hookshot;
Eurogamer, Polygon, VGC), `GS Back Room` `can_blast_or_smash` (push block, bomb wall; guides), none of the five
Nocturnal, as OoTR; boss: Mouth exits (block puzzle, no item), Before Boss `Fairy` and boss door (cracked floor folded
into the boss rule), `Defeat King Dodongo` (bomb floor, bomb into mouth, sword), heart, warp and `Blue Warp -> Death
Mountain` `at_day` (guides). Unchecked branches kept: Din's Fire, Megaton Hammer, Longshot-only. Low priority,
unchanged: pots, freestanding and recovery hearts, apart from the four pot moves above. Adult rules: none left to track
B (DC is wholly track A's); `Lobby -> Torch Room` `is_adult` kept, no evidence either way.

Open (in-game check for Kareem):

1. **Does the Bomb Bag ledge wall break from the hall side?** Ride the lift to the hall's upper floor (switch hit
   once), bomb the wall west of the Bomb Bag chest (30,115,-23); also try the Megaton Hammer from both sides. Rules:
   `Far Bridge <-> Bomb Bag Ledge`.
2. **Can the skull bridge be reached without that wall?** From the Armos room (room 12) step onto the upper south
   walkway (z -8); does it lead round to the skull bridge (End of Bridge wall, lift switch)? If yes, `Climb -> Far
   Bridge` goes back to `True`.
3. **Can GS Vines Above Stairs be taken without a ranged weapon?** Without Slingshot or Boomerang, climb the mesh past
   the Skullwalltula, or kill the Gold Skulltula by sword or jumpslash. Also test Boomerang, Bow, Hookshot. Rule: `GS
   Vines Above Stairs`.
4. **Does the Megaton Hammer break the GS alcove wall?** Hit WallCrack 1823997448213534774 off the skull bridge with the
   hammer. If it breaks, `GS Alcove Above Stairs` becomes `can_blast_or_smash`.
5. **Can an adult reach the Bomb Bag ledge from the blade room?** From the blade room's platforms, try Hover Boots or
   the Longshot up to the ledge (OoTR's `logic_dc_jump` route). Rule: `Climb -> Bomb Bag Ledge`.
6. **Can a Slingshot-only child beat the Lizalfos?** Child with only the Slingshot (no sword, sticks or bombs) against
   the lower pair in room 5; OoTR says yes. Rules: `Lower Right Side -> Torch Room` and the upper pair's.
7. **Do bombs or Din's Fire set off the staircase chain?** In room 10, put a bomb (not a Bomb Flower) in the gap, or
   cast Din's Fire. Rule: `Staircase Room -> Climb`, its non-Strength branches.

Remake-only checks noticed / for other tracks:

- Census: `End of Bridge Chest` is unlinked census 7524527082521156886 (room 1, Deku Shield); room 7 scrub
  7388739057158296701 is `Deku Scrub Side Room Near Dodongos`, also unlinked.
- Census: `Bomb Flower Platform Chest` is linked by item to 7764016096998075927 (room 5, after the lower Lizalfos), but
  the N64 spot holds 11582649900854566065 (room 13, Bomb Flower platform, Deku Seeds); link doubtful.
- Remake-only: blue rupee 8607798771661947511 (hall west alcove; Lobby, `can_blast_or_smash or
  Progressive_Strength_Upgrade`), scrub seeds 12253889300578348965 (staircase top; Climb, `has_explosives`) and
  850464708089653824 (after upper Lizalfos; their fight rule), plus whichever chest above is not the platform chest.
- Adult side handled here: Climb's adult route retargeted to the ledge, explosives (not Hammer) from ledge to bridge,
  Bow back through room 17.

### Inside Jabu-Jabu's Belly (`child_jabu_jabus_belly.toml`)

Sources: Nintendo Life walkthrough,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-lord-jabu-jabu-belly-walkthrough-switch-2, IGN walkthrough,
https://www.ign.com/wikis/ocarina-of-time-remake/Lord_Jabu-Jabu's_Belly_Dungeon_Walkthrough, Eurogamer and Polygon Gold
Skulltula guides (local copies in E:/OOTRemake/work/r3/), placement data (actors.py InsideJabuJabuBelly),
plans/03-game-data.md sections 5, 9, r2 and r3 census.

Changed (whole dungeon, both ages; names drop the `Jabu Jabus Belly` prefix):

|Rule|Was -> now|Evidence|
|---|---|---|
|`Map Chest`|region `Depths` (needs Boomerang) -> `Main` (`True`)|Map before the Boomerang: NL (alcove after throwing Ruto and hitting the switch), IGN (east chest after raising water); chest 14933854942830098290, room 14.|
|`GS Lobby Basement Upper`|region `Main` -> `Depths` (rule `can_use(Boomerang) or can_use(Hookshot)` unchanged)|GS 11283202900158580106 on the basement's west ledge by Big Octo's door; NL, IGN, Polygon, Eurogamer: drop in once the tentacles die.|

Checked, unchanged: `Beginning -> Main` `can_use_projectile` (Slingshot at the ceiling tonsil; NL, IGN; open 3),
`Beginning -> Zoras Fountain` (walk out any time; IGN) and `Farores Wind Warp` (IGN); `Boomerang Chest` `True`
(Stingers by Slingshot, Ruto on the switch; NL, IGN); `Deku Scrub` (dive to the elevator-room scrub; IGN; open 2); `GS
Water Switch Room` `True` (top of the vine wall; Eurogamer, IGN, NL); `GS Lobby Basement Lower` (Boomerang from the
north hole; Eurogamer, Polygon); `Basement 2 Octoroks Pots 1-5` (Boomerang freezes the swaying floor; IGN); `Main ->
Depths` `can_use(Boomerang)` (tentacles; NL, IGN); `Main -> Before Boss` (platform rises after Big Octo; NL, IGN);
`Compass Chest` `True` in Depths (Boomerang pops the Shaboms); `Depths -> Past Big Octo` `Sticks or Kokiri_Sword`
(stun, then strike its back); Past Big Octo events and pots (guides); `GS Near Boss` (Slingshot or Boomerang; IGN,
Polygon, Eurogamer); `Before Boss -> Barinade Boss Room` `can_use(Boomerang) or tricks` (Boomerang curves round the
barrier; IGN, NL); `Defeat Barinade` (Boomerang the tethers, then sword); Barinade heart, pots, boss exits, `Blue Warp
-> Zoras Fountain` `at_day` (guides); none of the four GS Nocturnal, as OoTR. Low priority, unchanged: Main `Fairy`
(pot), Basement Switch Room pots, `Small Wooden Crate 1/2` (open 4). Adult rules: none left to track B (whole dungeon
track A's; adult cannot enter by default, `is_child and Fish`).

Open (in-game check for Kareem):

1. **Is the basement's upper ledge reachable before the tentacles die?** Basement below Ruto's room: climb or (adult)
   hookshot onto the west ledge (y 85, by Big Octo's door), or see the GS at (-15,90,-83) from the floor. If yes, `GS
   Lobby Basement Upper` returns to Main.
2. **Can a scaleless child dive to the Jabu scrub?** Elevator room (room 18), no Silver Scale: dive through the
   underwater passage to the Business Scrub; OoTR says yes (`is_child`). Rule: `Deku Scrub` (scrubs not shuffled yet,
   D15).
3. **Do explosives hit the tonsil switch?** Mouth room: throw a bomb or send a Bombchu at the ceiling switch (y 98,
   about 8 m up); OoTR's `can_use_projectile` counts them. Rule: `Beginning -> Main`.
4. **Are the two crates reached before Big Octo?** (low priority) The Obj_BrokenBox_A_03 pair is in room 17, the 2F
   switch room toward the boss. If not reachable before Big Octo, `Small Wooden Crate 1/2` belong in Before Boss.
5. **Must the room 14 Stingers die before the water switch works?** IGN raises the water after killing them. Concerns
   the `Map Chest` move; any weapon a child has on entering Main suffices either way.

Remake-only checks noticed / for other tracks:

- Remake-only red rupee chest 3609242017501283521, room 13 (-34,82,-52), past the swaying floor and two Octoroks;
  Main, `can_use(Boomerang) or can_use(Hover_Boots)` (as the room's pots; IGN).
- Effect of the moves: the Map no longer needs the Boomerang; the Upper basement GS now needs the tentacles (Boomerang);
  the adult Hookshot route to it is gone.

### Bottom of the Well (`child_bottom_of_the_well.toml`)

Sources: ZeldaCentral Bottom of the Well,
https://zeldacentral.com/games/ocarina-of-time-remake/walkthrough/bottom-of-the-well/, VGC full walkthrough,
https://www.videogameschronicle.com/guide/zelda-oot-remake-full-bottom-of-the-well-walkthrough/, VGC Gold Skulltulas,
https://www.videogameschronicle.com/guide/all-bottom-of-the-well-gold-skulltula-locations-in-zelda-ocarina-of-time-switch-2/,
Nintendo Life walkthrough hub (no well page yet),
https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake, Eurogamer and Polygon Gold
Skulltula guides (local copies E:/OOTRemake/work/r3/gs-guide-*.txt), thonky (N64, only to map names onto rooms),
https://www.thonky.com/ocarina-of-time/under-the-well, OoT Randomizer SettingsListTricks.py (logic_botw_basement),
placement data (actors.py BottomOfTheWell, E:/OOTRemake/work/r4-logic-child/botw_actors.txt).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|location `Bottom of the Well Fire Keese Chest`|region `Behind Locked Doors` (keys) -> `Behind Fake Walls` (Lens or `logic_lens_botw`), rule `True`|Chain locks sit on two doors only (rooms 4, 5); room 6's door has none. ZeldaCentral: chest opened before either key was used. Chest 874970148260328653.|
|location `Bottom of the Well Fire Keese Pot`|same region move|Same room 6 (pot 7569958918344529585).|
|location `Bottom of the Well GS Like Like Cage`|same region move, `Boomerang` kept|GS 3889761319471426870 in room 7; Eurogamer: Lens and Boomerang, no key; ZeldaCentral #76 before any key; VGC: found with the Lens.|
|location `Bottom of the Well Map Chest`|`has_explosives or (Progressive_Strength_Upgrade and (...))` -> `has_explosives`|No bomb flower in the dungeon (the strength way used basement flowers); four boulders close the chest's corner; ZeldaCentral: B2 boulders need an explosion.|

Checked, unchanged: entry `is_child and (can_child_attack or Nuts)` (ZeldaCentral: Skulltula in the first corridor; VGC:
child only) and the exit to Kakariko `True`; Farore's warp (no evidence either way); `Underwater Left Chest`,
`Underwater Front Chest` `can_play(Zeldas_Lullaby)` (ZeldaCentral, VGC: the Lullaby on the triforce lowers the water);
`Invisible Chest` (the only invisible chest, room 2 past the Lullaby crawlspace; same rule, though N64's stood in Dead
Hand's room); `Lens of Truth Chest` (appears when Dead Hand dies; Lullaby crawlspace and hole; sword fight,
ZeldaCentral, VGC); `Freestanding Key` `Sticks or can_use(Dins_Fire)` (open 1); both Bombable chests `has_explosives`
(stricter kept; open 2); basement silver rupees `True` (five in room 9) and the Left Side exit behind them
(ZeldaCentral: door on the far shore of the B2 pond); `Behind Fake Walls` entry, Lens or `logic_lens_botw`
(ZeldaCentral: Compass in a hidden room, key chest unseen without the Lens; VGC: Lens shows walls and holes; open 5);
fake-wall, Compass and Center Skulltula chests `True` (ZeldaCentral); `Behind Locked Doors`
`(Small_Key_Bottom_of_the_Well, 3)`, capped to 2 in remake.toml (two chain-locked doors, one key each per ZeldaCentral);
`Like Like Chest` kept behind the locked doors (stricter, safe; open 3); `GS West Inner Room` `Boomerang` (Eurogamer,
Polygon, ZeldaCentral #78; open 4); `GS East Inner Room` `Boomerang` (Eurogamer: Lens, key, Boomerang; Polygon;
ZeldaCentral #77). No time or grotto rule; the three Gold Skulltulas are plain actors, as OoT Randomizer has them. Low
priority, unchanged: stick and nut drops, pots, coffin hearts and pit-fall blue rupees (no placed heart or rupee actor:
may not exist), West Inner Room flying pots (no flying-pot actor: probably plain pots). Adult-only rules: none, the
dungeon is child-only.

Open (in-game check for Kareem):

1. **Does the freestanding key need fire?** In the coffin hall (room 3, west door of the main floor), with no sticks or
   Din's Fire, pull out the slab between the far-west torches (ZeldaCentral). Yes: `Freestanding Key` (and coffin
   hearts) become `True`.
2. **Do the Bombable chests need bombs?** B1 has no breakable wall in the data. Without explosives, open every B1 chest,
   mainly north-west 10905582354954996284 (behind fake walls) and (20,98,-19). Yes: both Bombable chests become `True`
   once linked.
3. **Is there a chest in the Like Like room?** The data has none (12 chests against N64's 13). Also find chest
   12988877782812797760 (ladder at (20,100,-15), by the doors to rooms 6/7). None: `Like Like Chest` gets `n64_only` or
   that chest's rule.
4. **Does `GS West Inner Room` need fire?** In room 5 (west locked door) with the Boomerang but no Din's Fire or lit
   stick, take the Gold Skulltula on the wall (VGC: burn a coffin). Fire needed: add `(Sticks or can_use(Dins_Fire))`.
5. **Can the fake-wall areas be found without the Lens?** VGC: passable walls look slightly darker. Try the key chest
   (east niche), the Compass room and the central rooms. Owner decides: trick (`logic_lens_botw`) or default.

Remake-only checks noticed / for other tracks:

- Census (9 of 12 chests pending), suggested links: key 8397646530660039355 = `Right Bottom Fake Wall Chest`; red
  8975637636514249074 = `Front Left Fake Wall Chest` (N64's key; the third key is gone); 5429815628949128345 =
  `Underwater Front Chest`; 11718708984125260282 = `Invisible Chest`; tentative 631709185320708287 =
  `Center Skulltula Chest`, 10905582354954996284 = `Back Left Bombable Chest`; 12988877782812797760 unsure (open 3).
- Remake-only: Business Scrub 15945446340598299551 (room 1; green potion, magic jar, scrub seed), no OoT Randomizer
  location; chest 6064359710907908886 (room 11, past the Lullaby, fake floor in front drops to Dead Hand) if it is not
  an N64 chest.

### Ice Cavern (`child_ice_cavern.toml`)

Sources: Nintendo Life Ice Cavern,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-ice-cavern-walkthrough-switch-2, Nintendo Life heart pieces,
https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2, ZeldaCentral Ice Cavern,
https://zeldacentral.com/games/ocarina-of-time-remake/walkthrough/ice-cavern/, Eurogamer and Polygon Gold Skulltula
guides (local copies E:/OOTRemake/work/r3/gs-guide-*.txt), OoT Randomizer SettingsListTricks.py (ice tricks), placement
data (actors.py IceCavern, E:/OOTRemake/work/r4-logic-child/ice_actors.txt; ZoraFountain files).

Changed:

|Rule|Was -> now|Evidence|
|---|---|---|
|location `Ice Cavern Freestanding PoH`|`True` -> `n64_only`|No heart-piece actor in IceCavern or the census; NL: room 6 has compass, GS, Blue Fire, rupee jars, fairy; NL's 36 pieces: none in dungeons.|
|locations `Ice Cavern Push Block Room Red Rupee 1/2/3`|`can_play(Song_of_Time) or can_use(Boomerang)` -> `n64_only`|No freestanding rupee actor; the ledge holds one red-rupee chest (census 4128092231168513176, remake-only) over Song of Time blocks (NL, ZeldaCentral).|
|exit `Ice Cavern End -> Zoras Fountain` (new)|none -> `can_use(Iron_Boots)`|NL: with boots, sink into the opening past the Iron Boots room; entrance 10544815606216485062 in room 11's pool lands underwater in the fountain. Open 1.|

Checked, unchanged (the dungeon is adult-only, every rule adult-evaluated, but the whole dungeon is this track's per
Main): Beginning: ice ledge exit `True`; Spinning Scythe Room entry `here(is_adult or ...)` (three Freezards must die;
NL: sword; child part unreachable); Farore's warp (no evidence). Spinning Scythe Room: five silver rupees (NL; Ledge
`is_adult`); GS `can_use(Hookshot) or can_use(Boomerang)` (Eurogamer, Polygon, ZeldaCentral #64); Map Room exit after
the five (NL); Behind Ice Walls `here(Blue_Fire)` (red ice at both doors; NL, ZeldaCentral). Map Room: `Blue Fire`
`has_bottle` (NL), Map Chest `Blue_Fire` (chest in red ice), Frozen Pot `Blue_Fire or logic_ice_frozen_pot`. Behind Ice
Walls: Compass Chest `True`; push-block silver rupees `True` (fifth behind red ice, a Blue Fire font in the room); GS
Heart Piece Room and GS Push Block Room (Eurogamer, Polygon, NL, ZeldaCentral #65, #66); exit to the End after the five
(NL). End: Iron Boots Chest and Sheik (White Wolfos opens the gate; the chest gives the Serenade; NL, ZeldaCentral). Bow
and Megaton Hammer not added: ZeldaCentral lists them, but the data has no target, eye switch or hammer-only obstacle
and NL uses the sword (open 2, 3). Low priority, unchanged: Frozen Blue Rupee (no freestanding rupee, likely a pot drop
now; not changed without a guide), pots and flying pots, Map Room Recovery Hearts (no heart actor, probably gone). No
time or grotto rule; the three Gold Skulltulas are plain, as OoT Randomizer has them. Adult-only rules left to track B:
Zora's Fountain's adult side.

Open (in-game check for Kareem):

1. **Does the backdoor need Iron Boots?** In room 11, past the Iron Boots room, dive into the opening bootless. Yes: the
   new exit becomes `True` (or a scale). Also: with boots, does that arrival allow `ZF Bottom Freestanding PoH` without
   the Zora Tunic?
2. **Does the compass path need the Megaton Hammer?** In rooms 4 and 6, break every ice pillar on the way to the compass
   chest with the Master Sword (NL; ZeldaCentral used the Hammer). Hammer needed: `Ice Cavern Compass Chest` and
   `GS Heart Piece Room` get `can_use(Megaton_Hammer)`.
3. **Is any arrow target on the critical path?** ZeldaCentral shoots ice targets before GS #65. If a door needs it, that
   region exit gets `can_use(Bow)`.

Remake-only checks noticed / for other tracks:

- Track B: `ZF Iceberg Freestanding PoH` = heart piece 12406896586250888098, `ZF Bottom Freestanding PoH` =
  8030885465575590602; NL takes the bottom one with Iron Boots before the Zora Tunic (OoT Randomizer asks `Zora_Tunic`
  unless `logic_fewer_tunic_requirements`).
- Track B: `ZF Ice Ledge` `is_adult` agrees with the data (only adult ZoraFountain files have Ice Cavern entrance
  actors).
- Remake-only: red-rupee chest 4128092231168513176 on room 8's ledge (census 'Ice Cavern Room 8 Chest
  (TBox_Rupee_Red)'), no OoT Randomizer location; its rule would be `can_play(Song_of_Time)` in Behind Ice Walls.

## Item 5: the three mini-seeds on the new logic

`E:/OOTRemake/work/r4-seed/seed-{3,7,22}/` (`romfs/`, `spoiler.json`, `play-note.md`), the round 3 command
(`python -m clawshot --romfs E:/Games/Hookshot/romfs --seed <n> --out ... --areas KokiriForest LostWood
InsideTheDekuTree --goal "'Defeat Queen Gohma'"`) run from a `git archive` of 1d76316
(`E:/OOTRemake/work/r4-logic-child/src-1d76316`), so the seeds see the committed logic and none of the area files
still being written. Each spoiler's placements pass the beatability search on the slice world rebuilt from its
settings, with the Slingshot never behind 3F (`E:/OOTRemake/work/r4-logic-child/verify_seeds.py`).

| Seed | Kokiri Sword | Slingshot | Spheres | Size table |
|---|---|---|---:|---|
| 3 | Mido's bottom-right | Mido's top-left (round 3: the basement chest, unbeatable) | 3 | written (two KF Dynamic entries raised) |
| 7 | Mido's bottom-left | Deku Tree map chest (2F, before 3F) | 4 | not needed |
| 22 | Mido's top-right | KF Kokiri Sword chest | 3 | not needed |

Same seed numbers as round 3. Seeds 7 and 22 keep their Kokiri Sword and Slingshot places; their other Deku
Tree and Mido chests moved (the fill draws over a different reachable set now). Seed 3's round 3 placement is
out of logic, and its Slingshot is now in Kokiri Forest. Each play note says where everything is, what to see, and
asks the Slingshot room question.

Checked again after items 3 and 4 (every `child_*.toml` file and track B's `adult_*.toml` from main): the three
spoilers still pass the beatability search on the slice (`verify_seeds.py`, seeds 3 / 7 / 22: 3 / 4 / 3 spheres), so
the seeds Kareem plays stay in logic.

## Item 6: the Great Fairies, from the data

The reviewer's request (after items 1-5 went to main): trace the fairy flows, answer which fountain is which fairy,
who can be met first, whether fees are fixed, what happens without the rupees and Kareem's question (Improved Spin
before Din's Fire?), then model it. The answer, with the evidence, is in `plans/03-game-data.md` section 12 ("Great
Fairies"). In short:

- Death Mountain Trail is Din's fairy (Din's Fire, 25), Hyrule Castle the Power fairy (`Item_FairyBless_MP`: stronger
  spin attack and a magic meter, 50), Zora's Fountain Farore's Wind (100), the crater double magic (200), the
  Colossus Nayru's Love (300), Ganon's Castle halved damage (500): Kareem's table, from `RSDB/EventSetting` and the
  `Obj_TriForcePoint_A_0N` placements.
- Only Din's fairy comes without Din's Fire: flow `TriForcePoint` checks `IsGet.Item_DinFire` for the other five, and
  Navi says nothing happened. **So no Improved Spin before Din's Fire.** No gift needs the magic meter or another
  fairy met.
- Fees are fixed per fairy (`EventQueryHasRuppe` constants), not rising per visit. Without the rupees the fairy sends
  Link away and offers again at the next Lullaby.
- Wallets: start 200, Adult Wallet 500, Giant Wallet 1000 (`PouchActorInfo` `AfterExpansionMaxNum`).
- Every magic item (Din's Fire, Farore's Wind, Nayru's Love, Lens of Truth, the three magic arrows) and both fairy
  magic gifts carry the magic meter (`ExpansionAvility: MPMaxUP`).

Changes (this supersedes items 3 and 4's `'Great Fairy Met'`, taken from games.gg, which the data contradicts for
Hyrule Castle):

| Where | Entry | Before -> after |
|---|---|---|
| `src/clawshot/world/load.py`, `plans/04-world-format.md` | overrides table `[items."<name>"]` with `alias` (an item without one) | new |
| `remake.toml` | `[items]` Din's Fire, Farore's Wind, Nayru's Love, Lens of Truth, Fire/Ice/Light Arrows | each also counts as one `Magic Meter` |
| `remake.toml` | `HC Great Fairy Reward` | `can_play(Zeldas_Lullaby)` -> `... and Dins_Fire` |
| `child_zoras_fountain.toml` | `ZF Great Fairy Reward` | `... and 'Great Fairy Met'` -> `... and Dins_Fire` |
| `adult_death_mountain_crater.toml` (reviewer's leave) | `DMC Great Fairy Reward` | `can_play(Zeldas_Lullaby)` -> `... and Dins_Fire` |
| `adult_desert_colossus.toml` (reviewer's leave) | `Colossus Great Fairy Reward` | `can_play(Zeldas_Lullaby)` -> `... and Dins_Fire and Progressive_Wallet` |
| `adult_ganons_castle.toml` (reviewer's leave) | `OGC Great Fairy Reward` | `can_play(Zeldas_Lullaby)` -> `... and Dins_Fire and Progressive_Wallet` |
| `child_hyrule_castle.toml`, `child_death_mountain_trail.toml` | events `Great Fairy Met` | removed |
| `tests/test_world_remake_adult_gerudo_training_ground.py` (track B's) | lobby chests: "the Lens needs magic" | the Lens alone opens them (it carries its magic) |

Tests (`tests/test_world_remake.py`): an item alias counts the other item and bad aliases are refused; Din's fairy
comes with the Lullaby alone, Hyrule Castle's not with the magic meter but with Din's Fire; the Colossus and OGC
fairies need the Adult Wallet. Scratch scripts (read only on the dump): `E:/OOTRemake/work/r4-logic-child/`
`fairy_logic.py`, `fairy_flows.py`, `msbt_dump.py`, `rsdb_rows.py`, `gd_lookup.py`, `tfp_params.py`.

Provisional: the magic meter as an item alias (collecting Din's Fire also counts one `Magic Meter`) rather than a
rule-compiler change; a rule asking for two meters would now count two magic items as double magic, and none does.
`IsGet.Item_DinFire` being set however Din's Fire is got is an inference; so is the note for the seed patch in section 12
(the flows use each gift's own `IsGet` as "already given").

In-game check for Kareem (one save, no Din's Fire yet): **play Zelda's Lullaby on the Triforce in the Hyrule Castle
fountain.** Expected: Navi says "It doesn't seem like anything happened, but... I do sense some kind of mysterious
power here" and no fairy comes. Then, with fewer than 25 rupees, at the Death Mountain Trail fountain: she appears,
asks for 25 and sends Link away; playing again offers again.

Gates on the branch: `ruff format --check` 94 files formatted, `ruff check` clean, `pytest` 297 passed / 26 skipped,
`pytest -m dump` 25 passed; the three mini-seeds still pass the beatability search (`verify_seeds.py` 3 / 7 / 22: 3 /
4 / 3 spheres).

## Questions for Kareem (the ones that change progression; every area's list is above)

1. **Deku Tree: in the Slingshot room without the Slingshot (seed 3), how did you get out? Does continuing after a
   save or a game over put Link at the dungeon's entrance?** If not, the room is a trap (item 2's proposal).
2. **Lost Woods: before meeting Zelda, does the right path through the woods still send a child back instead of
   letting him into the Sacred Forest Meadow?** (`LW Beyond Mido -> SFM Entryway` now asks for having met Zelda.)
3. **Death Mountain Trail: can a child's own Bombs break the boulder in front of Dodongo's Cavern, or only the bomb
   flower thrown with the Goron's Bracelet?** (now the bracelet only.)
4. **Death Mountain summit: does the owl refuse to fly a child to Kakariko before Din's Fire is held?** (Impa's
   cow-pen heart piece now hangs on it.)
5. **Dodongo's Cavern: does the cracked wall beside the Bomb Bag chest also break from the main hall's side, and with
   the Megaton Hammer?**
6. **Temple of Time: does the Door of Time open with the Fairy Ocarina (three stones, Song of Time)?** (now the Ocarina
   of Time is asked.)
7. **Market: can a child play Bombchu Bowling after Dodongo's Cavern without a Bomb Bag or Bombchus?**
8. **Hyrule Field and Kakariko: do the leafy grotto covers (tektite grotto west of the drawbridge, the ReDead grotto
   by the Kakariko steps) open with a bomb, or only with the Song of Storms?**
9. **Kokiri Forest's grotto: does its chest appear only after the three Deku Scrubs, and do they need a shield?**
10. **Great Fairies (item 6): without Din's Fire, does Zelda's Lullaby at the Hyrule Castle fountain bring only
    Navi's "It doesn't seem like anything happened"?**

## Provisional choices (for review)

1. **Several override files, one per area and track** (item 1); anything set twice is an error, so a shared rule has one
   owner. Where a rule serves both ages, track A changed only its child part and flagged it.
2. **Conservative rule** (items 3, 4): stricter with remake evidence, looser only with clear evidence, otherwise OoT
   Randomizer's rule. Looser changes made: Kak man on the roof by cucco, the heart-piece grave without the Sun's Song,
   Jabu's map chest before the Boomerang, Goron City's spinning pot with the bracelet, the Ice Cavern pool to Zora's
   Fountain.
3. **`'Time Flows'` per rule**, not in the rule compiler (`rules.py` is no track's). A world-wide gate would also cover
   adult night rules; reviewer's call.
4. **Great Fairies (item 6)**: the magic meter as an item alias of every magic item; fees as `Progressive_Wallet`
   where they pass the starting 200.
5. **The Door of Time is the vanilla one**: OoT Randomizer's `open_door_of_time` setting is not read, since the game
   cannot open the door otherwise without a code hook.
6. **N64-only from placement data** where a grotto or room holds other actors and no check (grotto scrubs, generic
   HF grotto chests, the DMT storms grotto chest, the Royal Family's Tomb chest, DC's boss room chest and two scrubs,
   the Ice Cavern heart piece and rupees). Remake-only checks found instead are listed per area for the census owner.
7. **The research was done by eight sub-agents** (one brief, `E:/OOTRemake/work/r4-logic-child/brief.md`); every
   committed file was read and load- and test-checked here. Their full per-rule notes stay outside the repo
   (`E:/OOTRemake/work/r4-logic-child/findings/`).

## Cross-track posts (thread `cs-r4`)

- 19:52 item 1 (loader) schema; 20:00 item 2 and the region-count test; 20:02 item 5 seeds; 20:03 answer to track B
  (free Fire key: not mine to change; region count already handled); 20:05 grottos without the Stone of Agony
  (Gerudo Valley and Fortress left to track B); 20:06 time flows after meeting Zelda (adult night rules to track B);
  20:10 GTG key as a chest (fa9ed2b); 20:11 Great Fairies (first fairy, fees; DMC, Colossus, OGC to track B);
  21:01 Shadow Trial Golden Gauntlets chest needs the Lens (138fb85).

## Gates (on the branch, rebased on main 00a9b63, before the handoff)

```
uv run ruff format --check                                   94 files already formatted
uv run ruff check                                            All checks passed!
uv run pytest                                                290 passed, 26 skipped
OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump      25 passed, 291 deselected
```

Each area batch was also checked before its commit on a `git archive` of the branch plus that batch's files
(`E:/OOTRemake/work/r4-logic-child/check_files.sh`: the world loads with no dangling exit or undefined event, and
`test_world_remake`, `test_world_data` (vanilla beatable, 200 default and 20 progressive seeds), `test_world_census`,
`test_seed` and `test_generate` pass). One full run stalled at about 70 % while a Hookshot build used every core
(not this track's); timing every seed alone (`seed_times.py`) showed none slow, and the run above finished.

## Left for later

- The in-game questions above (Kareem), and the Slingshot room: rule or placement patch once his answer is in.
- Remake-only checks found per area (census Hashes in the area sections) need world locations and census links.
- Census links the area work suggests (census owner): Kak Open Grotto Chest 12902291359202819102, Kak Redead Grotto
  Chest 5755485285664292988, DC End of Bridge Chest 7524527082521156886, the LLR grotto scrubs, BotW's nine chests
  (`findings/bottom_of_the_well.md`).
- Other rupee costs (shops, Medigoron, the Bombchu salesman) against the remake's wallets (200 / 500 / 1000).
- `'Time Flows'` as a compiler-level gate, and the adult night rules (track B).
