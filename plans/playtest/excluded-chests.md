# Excluded chest checks — Track C register addendum

Part of [questions.md](questions.md), not new logic or seed data. Read with `git show r5/seeds:<path>`;
branch observed at `b42b0f4c1602`. All **20** entries currently have `rule = "False"` and `keep_vanilla`.
Each question below names the exact entry that evidence may unlock. Hash, not a list index, is the chest identity.
Positions are identification aids for Claude (Banc x/y/z), not copied placements.

Answer records must include **age, progress, tools, surface entrance, path, appearance trigger and safe collection/return**.
Record before touching a note/switch where possible. Missing after collection is not evidence of an absent route.
A working route is not enough to call an alternate/repeat reward independent. Claude changes the owning entry only after
review: replace `False` with the verified rule and remove `keep_vanilla` if appropriate; otherwise retain exclusion.
No code/data edits are made by Track E. Entries exist on `r5/seeds`; do not invent a local TOML file before merge.

Use existing area visits/logs: Dampe's two rupees share AO02's race log; GC signs share one puzzle visit. LW05 is now
an alias of XC19, GE01 of XC04; answer each once. LLR02 now covers tower token only; chest climb is XC14.
GROT01/02 and GE02 keep scrub/entrance/resource observations, while exact chest conditions live here.
The 9 checks already asked on 2026-11-08 remain pending and absent from all routes.

## XC01 — Bottom Of The Well Room 11 Chest (Item_ScrubBusinessSeed)

- **Where/when:** child, after draining Well; compare before/after Lullaby on preserved copy. Session [6](session-6.md); Hash `6064359710907908886`, Banc position (0.0, 102.2, -100.5).
- **Do/watch:** Past the Lullaby crawlspace, use Lens to mark the room-11 fake-floor hole to Dead Hand. Can you walk round or jump it, open the Seed chest and return safely? Record exact footing and every item needed.
- **Unlock target:** `src/clawshot/data/world/remake/extra_bottom_of_the_well.toml` → `[locations."Bottom Of The Well Room 11 Chest (Item_ScrubBusinessSeed)"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_bottom_of_the_well.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC02 — Gerudo Fortress Chest (TBox_Rupee_Red)

- **Where/when:** adult, fortress access; before opening underground reward. Session [10](session-10.md); Hash `16619432200060282313`, Banc position (15.0, 89.2, -67.7).
- **Do/watch:** Find the underground red chest among flying pots and a Skulltula. Start at its surface hole: what opens it, and which path reaches and leaves this chest? Record whether it is the old storms hole or another entrance.
- **Unlock target:** `src/clawshot/data/world/remake/extra_gerudo_fortress.toml` → `[locations."Gerudo Fortress Chest (TBox_Rupee_Red)"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_gerudo_fortress.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC03 — Gerudo Valley Chest (TBox_Rupee_Red) [Adult]

- **Where/when:** adult, before Valley red Lens-chest reward. Session [10](session-10.md); Hash `18413589940135955604`, Banc position (-43.3, 84.0, -46.0).
- **Do/watch:** From the surface, find the hole leading to the invisible red chest. Record opener, route, whether Lens is needed to open it, and reward. Compare the child counterpart using the same route only after child return.
- **Unlock target:** `src/clawshot/data/world/remake/extra_gerudo_valley.toml` → `[locations."Gerudo Valley Chest (TBox_Rupee_Red) [Adult]"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_gerudo_valley.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC04 — Gerudo Valley Chest (Item_ScrubBusinessSeed)

- **Where/when:** adult first; child comparison only after return. Session [10](session-10.md); Hash `6463521162691873710`, Banc position (31.2, -22.6, 37.0).
- **Do/watch:** At Valley underwater hole, the old silver rock is gone. What now opens or reaches the Seed chest? Try ordinary dive/Scale/Boots as available, then record actual blocker, route and safe return. Check whether child can use the same entrance.
- **Unlock target:** `src/clawshot/data/world/remake/extra_gerudo_valley.toml` → `[locations."Gerudo Valley Chest (Item_ScrubBusinessSeed)"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_gerudo_valley.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC05 — Gerudo Valley Chest (TBox_Rupee_Green)

- **Where/when:** adult first; child comparison after return. Session [10](session-10.md); Hash `17750686910716887133`, Banc position (-47.3, 84.0, -46.0).
- **Do/watch:** Find the green chest beside the Valley underground red chest. Does the same hole/path reach it, and does it appear without opening the red chest or solving another puzzle? Record each age actually able to enter.
- **Unlock target:** `src/clawshot/data/world/remake/extra_gerudo_valley.toml` → `[locations."Gerudo Valley Chest (TBox_Rupee_Green)"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_gerudo_valley.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC06 — Gerudo Valley Chest (TBox_Rupee_Red) [Child]

- **Where/when:** child after return, counterpart of adult red chest. Session [10](session-10.md); Hash `6205043616869463865`, Banc position (-43.3, 84.0, -46.0).
- **Do/watch:** At the Valley red Lens-chest spot as child, record surface opener, route and Lens requirement. On a disposable cross-age run, was it already open after adult collected the counterpart, or does it pay again? Do not count copies twice by default.
- **Unlock target:** `src/clawshot/data/world/remake/extra_gerudo_valley.toml` → `[locations."Gerudo Valley Chest (TBox_Rupee_Red) [Child]"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_gerudo_valley.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC07 — Goron City Chest (TBox_Rupee_Green)

- **Where/when:** adult at Goron grotto; child comparison if normal entrance permits. Session [7](session-7.md); Hash `9159710900681116662`, Banc position (-52.2, 94.8, 32.0).
- **Do/watch:** In City grotto, before following its signs, is the green chest present? Solve the sign puzzle one step at a time; which exact action makes green appear? Can it pay without purple, and does it remain open after reload?
- **Unlock target:** `src/clawshot/data/world/remake/extra_goron_city.toml` → `[locations."Goron City Chest (TBox_Rupee_Green)"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_goron_city.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC08 — Goron City Chest (TBox_Rupee_Purple) #2

- **Where/when:** adult at same sign puzzle; preserved unclaimed control. Session [7](session-7.md); Hash `10944569637726152230`, Banc position (-52.2, 94.8, 26.3).
- **Do/watch:** At the same grotto, when does purple appear: same solution, another solution, or only after green? Note action/order, age and first/repeat payout. Use the same visit as the green check, but record this chest separately.
- **Unlock target:** `src/clawshot/data/world/remake/extra_goron_city.toml` → `[locations."Goron City Chest (TBox_Rupee_Purple) #2"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_goron_city.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC09 — Graveyard Chest (TBox_Rupee_Red)

- **Where/when:** adult at Dampe; log first and repeat races on disposable copy. Session [1](session-1.md); Hash `234006393181394602`, Banc position (-6.0, 82.5, 77.6).
- **Do/watch:** For Dampe red-rupee goal chest, record race time, previous first rewards and exactly when red appears. Can it be opened independently of Hookshot/Heart Piece, or only as their repeat substitute? Does another race or reload pay red again?
- **Unlock target:** `src/clawshot/data/world/remake/extra_graveyard.toml` → `[locations."Graveyard Chest (TBox_Rupee_Red)"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_graveyard.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC10 — Graveyard Chest (TBox_Rupee_Blue)

- **Where/when:** adult at same race; same shared race log. Session [1](session-1.md); Hash `4322670163630771947`, Banc position (-6.0, 82.5, 77.6).
- **Do/watch:** For Dampe blue-rupee goal chest, record time and prior rewards when blue appears. Can red and blue coexist or be claimed separately? Check repeat/reload only on disposable copy; distinguish repeat filler from a one-time location.
- **Unlock target:** `src/clawshot/data/world/remake/extra_graveyard.toml` → `[locations."Graveyard Chest (TBox_Rupee_Blue)"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_graveyard.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC11 — Hyrule Field Chest (TBox_Rupee_Red) #1

- **Where/when:** adult, southern Field on approach to Lake; note before/after child-note reading. Session [10](session-10.md); Hash `1163740567397714729`, Banc position (-5.7, 146.2, 406.9).
- **Do/watch:** Find southern Field red chest near a Poe. Is it present before reading nearby Fairy Notes? Record each note/puzzle/ghost action tried, what makes the chest appear, and the path/tool needed to open it. If absent, preserve baseline rather than guessing.
- **Unlock target:** `src/clawshot/data/world/remake/extra_hyrule_field.toml` → `[locations."Hyrule Field Chest (TBox_Rupee_Red) #1"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_hyrule_field.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC12 — Hyrule Field Chest (TBox_Rupee_Red) #2

- **Where/when:** adult, northern Field near drawbridge/Kakariko approach. Session [10](session-10.md); Hash `9891111455604007674`, Banc position (84.4, 152.6, 45.4).
- **Do/watch:** Find northern Field red chest near a Poe. Record presence before touching notes, then the exact appearance trigger and collection path. If a child note seems involved, compare a preserved before/after age-return copy, not item ownership alone.
- **Unlock target:** `src/clawshot/data/world/remake/extra_hyrule_field.toml` → `[locations."Hyrule Field Chest (TBox_Rupee_Red) #2"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_hyrule_field.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC13 — Hyrule Field Chest (TBox_Rupee_Red) #3

- **Where/when:** adult at Lake west shore before Morpha; compare full lake later. Session [8](session-8.md); Hash `17023457248274633121`, Banc position (-297.4, 131.3, 558.1).
- **Do/watch:** At west-shore red chest by lakeside Poe, record low-water access and whether chest exists before notes/ghost action. What makes it appear and lets you collect it? Revisit after Morpha only if lake height appears to block the same route.
- **Unlock target:** `src/clawshot/data/world/remake/extra_hyrule_field.toml` → `[locations."Hyrule Field Chest (TBox_Rupee_Red) #3"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_hyrule_field.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC14 — Hyrule Field Chest (Item_ScrubBusinessSeed)

- **Where/when:** child after return; adult comparison if child route blocked. Session [2](session-2.md); Hash `17445672702269453589`, Banc position (-151.9, 162.0, 265.3).
- **Do/watch:** In ranch tower, reach the high chest above the boxes, not the floor crawl-hole Heart Piece. Give exact climb, tool and any Fairy Note/appearance step. Check age distinction on an adult return only if it matters.
- **Unlock target:** `src/clawshot/data/world/remake/extra_hyrule_field.toml` → `[locations."Hyrule Field Chest (Item_ScrubBusinessSeed)"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_hyrule_field.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC15 — Hyrule Field Chest (TBox_Rupee_Red) #4

- **Where/when:** child after return in Lake island-grave grotto; adult comparison if possible. Session [5](session-5.md); Hash `6900843020594897860`, Banc position (-214.9, 98.0, 449.1).
- **Do/watch:** In Lake grave grotto inspect chest before lighting anything. Light timed candles using one fire method at a time on unsolved copies. Which sequence spawns the red chest, and what item/magic/timing is mandatory? Record age and repeat payout.
- **Unlock target:** `src/clawshot/data/world/remake/extra_hyrule_field.toml` → `[locations."Hyrule Field Chest (TBox_Rupee_Red) #4"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_hyrule_field.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC16 — Kakariko Village Chest (TBox_Rupee_Purple) [Adult Alternative]

- **Where/when:** adult later alternative Kakariko state; record actual story transition. Session [15](session-15.md); Hash `13080955777249750889`, Banc position (5.6, 130.2, 41.4).
- **Do/watch:** Revisit high windmill chest in the later village state. Does earlier route still reach it, what changed its appearance, and is it already open after normal-state collection? Record which scene/state changed; do not assume Morpha selects this variant.
- **Unlock target:** `src/clawshot/data/world/remake/extra_kakariko_village.toml` → `[locations."Kakariko Village Chest (TBox_Rupee_Purple) [Adult Alternative]"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_kakariko_village.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC17 — Kakariko Village Chest (TBox_Rupee_Purple) [Adult]

- **Where/when:** adult just after first pull; return with needed grapple only if blocked. Session [1](session-1.md); Hash `11929552275106311978`, Banc position (5.6, 130.2, 41.4).
- **Do/watch:** Inside windmill, locate purple chest high above the Heart Piece beam. What climb/grapple/launch reaches it and permits return? Start with normal movement/Hookshot; note required longer range or story trigger. Do not infer access from the Heart Piece route.
- **Unlock target:** `src/clawshot/data/world/remake/extra_kakariko_village.toml` → `[locations."Kakariko Village Chest (TBox_Rupee_Purple) [Adult]"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_kakariko_village.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC18 — Kokiri Forest Chest (TBox_Rupee_Purple)

- **Where/when:** child after return; adult route comparison later if needed. Session [2](session-2.md); Hash `4349272251343787229`, Banc position (-132.2, 123.9, -16.0).
- **Do/watch:** Above Kokiri stick-bag scrub, find purple chest on high ledge. Give route from a named ground landmark, tools, age and any note/spawn condition. Can it be opened without entering the storms grotto?
- **Unlock target:** `src/clawshot/data/world/remake/extra_kokiri_forest.toml` → `[locations."Kokiri Forest Chest (TBox_Rupee_Purple)"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_kokiri_forest.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC19 — Lost Wood Chest (TBox_Rupee_Purple)

- **Where/when:** child after return; adult comparison if child blocked. Session [2](session-2.md); Hash `17479747339356189279`, Banc position (-49.4, 104.5, 71.9).
- **Do/watch:** Above Lost Woods bridge scrub, find purple chest ledge. Record exact climb/tool/age and any appearance trigger, then safe return. This is the old LW05 question with its exact excluded-entry identity.
- **Unlock target:** `src/clawshot/data/world/remake/extra_lost_wood.toml` → `[locations."Lost Wood Chest (TBox_Rupee_Purple)"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_lost_wood.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## XC20 — Zora Fountain Chest (TBox_Rupee_Purple)

- **Where/when:** adult at Fountain upper ruins; before/after Ice visit as needed. Session [8](session-8.md); Hash `15055117029957340138`, Banc position (33.0, 108.5, 1.7).
- **Do/watch:** At Fountain upper ruined masonry, find purple chest. Which jump, climb, ice route or grapple reaches it? Record age, every item used and any spawn/story condition; distinguish standing near it from opening it and returning.
- **Unlock target:** `src/clawshot/data/world/remake/extra_zora_fountain.toml` → `[locations."Zora Fountain Chest (TBox_Rupee_Purple)"]` (`rule` and `keep_vanilla`).
- **Answer changes:** verified entrance/appearance/tool/age conditions supply this entry's reach rule; a repeat or mutually-exclusive copy stays excluded unless reviewer establishes correct check identity.
- **Source:** `r5/seeds:plans/rounds/r5-seeds.md`, “Excluded checks”; `r5/seeds:src/clawshot/data/world/remake/extra_zora_fountain.toml`; branch census-readable name mapped to this Hash. No OoTR name is fabricated.

## Accompanying branch clarifications

- FT08 is **Forest Temple Falling Ceiling Room Chest**, Hash 15117164073907033527, not the basement chest.
  On vanilla copy record green rupee vs Bombs; correct the existing question/route instead of asking twice.
- W03 also checks east-corridor ladder chest Hash 12988877782812797760 **before Lullaby**: is it submerged/collectible?
  Inspect old west pit and Like Like room for absent chests. Keep conservative Lullaby until this is settled;
  Like Like exclusion is data-backed, not proof from one already-cleared visit.
