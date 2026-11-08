# In-game logic question register

For Claude; player routes are in `session-*.md`. Build `e0f3ccfa`. This register records questions, not verified results.
Rule paths below are relative to `src/clawshot/data/world/`. A translated-file key identifies the behavior to override;
never hand-edit translated TOML. `fact` means record evidence before assigning a new check or deciding policy.

## How to record

Use a disposable user copy for traps, missing-item states, capture and mods. Never overwrite main saves or backup folders.
One tool/route at a time; record age, inventory, story stage, room/standing point and outcome. Token kill is not collection;
item spawn is not retrieval. An absent or already-collected item is not a failed route. A failed attempt is **inconclusive**
unless a working control and actual blocker are known. A tool owned but not used tests combat/traversal, not an `IsGet` gate.
Do not replay consumed first-time states on the main game. Mark `needs preserved copy/variant` instead.

Reviewer steering (2026-11-08): session 1 begins adult immediately after the first pull. All child sessions wait until
main-game return to child unlocks. Already-asked checks below are omitted from every session, including disposable replays.
No in-game result is claimed by this track.

## Already asked; do not ask again

- **HF01 — asked 2026-11-08, answer pending:** After Zelda throws the Ocarina into the moat, try collecting it with no Silver/Golden Scale. Does the pickup succeed?
- **FA01 — asked 2026-11-08, answer pending:** Before obtaining Din Fire, play Lullaby at the Hyrule Castle fountain. Does only Navi respond?
- **TT01 — asked 2026-11-08, answer pending:** With only Fairy Ocarina, three stones and Song of Time, play at the altar. Record door opening and whether Zelda escape already played. Compare a control without that scene only if a verified test variant exists.
- **TT02 — asked 2026-11-08, answer pending:** Immediately after the first sword pull, try putting it back. Retry after Forest Temple and its return-to-temple scene, before further temples. When does child return become available?
- **DMT03 — asked 2026-11-08, answer pending:** At the summit, speak to the owl before Din Fire. Then obtain Din Fire from a different chest on a fresh variant and speak again. Is flight offered each time?
- **ZD02 — asked 2026-11-08, answer pending:** After the first Silver Scale, win the second diving round. Record item/rupees and whether a third win differs.
- **JJ02 — asked 2026-11-08, answer pending:** Without a Scale, dive through the elevator-room underwater passage to the scrub. Can child reach and buy?
- **JJ03 — asked 2026-11-08, answer pending:** In the entrance mouth, try Bombs then Bombchus on the ceiling tonsil; do not use Slingshot. Does either open the door?
- **FA02 — asked 2026-11-08, answer pending:** At the summit fountain with fewer than 25 rupees, ask for the gift, leave and play Lullaby again. Is it offered again for 25?

## Active checks

### DT01 — Deku Tree

- Age/progress: child; Shield; use isolated test copy before entering room. Session 17.
- Do/watch: Enter the Slingshot room without a Slingshot; after the platform falls, try returning. Save/quit/continue, then separately game-over/continue on a disposable copy. Where does each resume?
- Target: `remake/child_deku_tree.toml` — exits Deku Tree Lobby -> Deku Tree Slingshot Room; reverse exit.
- Answer changes: Entrance recovery permits existing entry; trapped recovery needs owner-approved safe-room patch or stronger entry, not a claim that the seed is safe.
- Source: `plans/rounds/r4-logic-child:64-73`.

### DT02 — Deku Tree

- Age/progress: child; Shield; use isolated test copy before entering room. Session 17.
- Do/watch: At the lobby vines above the map chest, try Boomerang as child; on a later adult visit try Bow and Hookshot separately. Can each clear all spiders and let you climb to 3F?
- Target: `remake/child_deku_tree.toml` — exits Deku Tree Lobby -> Deku Tree Top Floor.
- Answer changes: Add only successful age/tool alternatives; otherwise retain Slingshot. Adult branches belong in a later return, not the child attempt.
- Source: `plans/rounds/r4-logic-child:64-73`.

### KF01 — Kokiri Forest

- Age/progress: child; Song of Storms for grotto; sword for Baba. Session 6.
- Do/watch: At the cover up the ivy by Mido, play Storms. Before fighting, is the chest present? Try beating the scrub trio with sword, Slingshot and nuts separately, without shielding. Does the chest appear/open?
- Target: `remake/child_kokiri_forest.toml` — locations KF Storms Grotto Chest.
- Answer changes: Record spawn condition and each successful stun method; require shield only if alternatives fail under controlled attempts.
- Source: `plans/rounds/r4-logic-child:165-173`.

### KF02 — Kokiri Forest

- Age/progress: child; Song of Storms for grotto; sword for Baba. Session 6.
- Do/watch: In that grotto, cut every grass patch. Does a catchable bug drop?
- Target: `remake/child_kokiri_forest.toml` — events KF Storms Grotto -> Bugs.
- Answer changes: Keep or remove this bug source; do not infer a drop from grass appearance.
- Source: `plans/rounds/r4-logic-child:165-173`.

### KF03 — Kokiri Forest

- Age/progress: child; Song of Storms for grotto; sword for Baba. Session 6.
- Do/watch: On the path past Mido, strike a Deku Baba head as child. Does it drop nuts? Repeat with Boomerang only when owned.
- Target: `remake/child_kokiri_forest.toml` — events Kokiri Forest -> Deku Nut Drop; Deku Stick Drop.
- Answer changes: Add child nut access or adjust stick/weapon alternatives only for observed drops.
- Source: `plans/rounds/r4-logic-child:165-173`.

### LW01 — Lost Woods

- Age/progress: child; Before Zelda for LW01; sword/Slingshot/nuts for alternatives. Session 17.
- Do/watch: After Gohma but before Zelda, follow the correct maze path to the meadow. Does the last turn admit you or send you to Kokiri Forest?
- Target: `remake/child_lost_woods.toml` — exits LW Beyond Mido -> SFM Entryway.
- Answer changes: Admit: remove met-Zelda condition; redirect: keep it.
- Source: `plans/rounds/r4-logic-child:225-238`.

### LW02 — Lost Woods

- Age/progress: child; After Zelda; no Bomb Bag needed for initial checks. Session 2.
- Do/watch: Drop through the Deku Theater hole. Walk toward the underground scrubs and bug grass without using bombs. Which rooms connect freely?
- Target: `remake/child_lost_woods.toml` — exits Lost Woods -> LW Scrubs Grotto; LW Near Shortcuts Grotto.
- Answer changes: Free connections remove only their demonstrated explosives gates; record actual entrances.
- Source: `plans/rounds/r4-logic-child:225-238`.

### LW03 — Lost Woods

- Age/progress: child; After Zelda; no Bomb Bag needed for initial checks. Session 2.
- Do/watch: At the bridge Business Scrub, use sword, Slingshot and nuts separately, never a reflected nut. Does each make it sell?
- Target: `remake/child_lost_woods.toml` — translated helpers.toml can_stun_deku; LW scrub location rules.
- Answer changes: Record successful methods for helper review; one scrub is not proof for every scrub type.
- Source: `plans/rounds/r4-logic-child:225-238`.

### LW04 — Lost Woods

- Age/progress: child; After Zelda; no Bomb Bag needed for initial checks. Session 2.
- Do/watch: Cut above-ground bushes in the woods; bottle any bug. Is there a renewable bug source outside the holes?
- Target: `remake/child_lost_woods.toml` — events Lost Woods -> Bugs.
- Answer changes: Confirm or remove this source.
- Source: `plans/rounds/r4-logic-child:225-238`.

### LW05 — Lost Woods

- Age/progress: child; After Zelda; no Bomb Bag needed for initial checks. Session 2.
- Do/watch: Above the bridge scrub, find the purple chest. Describe the climb from the scrub, noting every item used.
- Target: `remake/child_lost_woods.toml` — fact: chest 17479747339356189279 access.
- Answer changes: Supplies the remake-only chest rule and stable census identity for Track C.
- Source: `plans/rounds/r4-logic-child:225-238`.

### SFM01 — Sacred Forest Meadow

- Age/progress: child; After Zelda; Storms for SFM01; bombs for comparison. Session 6.
- Do/watch: At the round cover just before the Wolfos gate, try a bomb first, then Storms. Does it open into the two-Wolfos room?
- Target: `remake/child_sacred_forest_meadow.toml` — exits SFM Entryway -> SFM Wolfos Grotto.
- Answer changes: Bomb success adds explosives; Storms-only keeps current gate.
- Source: `plans/rounds/r4-logic-child:283-292`.

### SFM02 — Sacred Forest Meadow

- Age/progress: child; After Zelda; Storms for SFM01; bombs for comparison. Session 6.
- Do/watch: At the cover by Saria, try a bomb, Storms and Song of Time separately. Check whether its exit connects to the Gossip Stone/Scrub Seed chest clearing below.
- Target: `remake/child_sacred_forest_meadow.toml` — exits Sacred Forest Meadow -> SFM Storms Grotto.
- Answer changes: Use the observed opener/connection, not the old grotto name.
- Source: `plans/rounds/r4-logic-child:283-292`.

### SFM03 — Sacred Forest Meadow

- Age/progress: child; After Zelda; Storms for SFM01; bombs for comparison. Session 6.
- Do/watch: Against the gate Wolfos and the grotto pair, try Slingshot-only and stick-only fights separately. Which can win?
- Target: `remake/child_sacred_forest_meadow.toml` — exits SFM Entryway -> Sacred Forest Meadow; locations SFM Wolfos Grotto Chest.
- Answer changes: Retain or remove each weapon branch independently.
- Source: `plans/rounds/r4-logic-child:283-292`.

### HF02 — Hyrule Field

- Age/progress: child; Bombs; Storms for cover comparison; no fire for web test. Session 6.
- Do/watch: At the leafy cover west of the drawbridge, try Bombs then Storms. Repeat at the plant-ring cover by the Kakariko steps/Kaepora tree. Record both holes separately.
- Target: `remake/child_hyrule_field.toml` — exits Hyrule Field -> HF Tektite Grotto; child_kakariko.toml exits Hyrule Field -> Kak Redead Grotto.
- Answer changes: Add explosives per successful cover; keep Storms if a bomb does not open it. Deduplicates Kakariko question 4.
- Source: `plans/rounds/r4-logic-child:350-366; r4-logic-child:637-638`.

### HF03 — Hyrule Field

- Age/progress: child; Bombs; Storms for cover comparison; no fire for web test. Session 6.
- Do/watch: In the cow grotto near Gerudo Valley, try sword, unlit stick, Slingshot and Bombs on the web before the cow. Which clears it without fire?
- Target: `remake/child_hyrule_field.toml` — translated hyrule_field.toml HF Cow Grotto events and pots using has_fire_source.
- Answer changes: Substitute only demonstrated web-breaking alternatives.
- Source: `plans/rounds/r4-logic-child:350-366; r4-logic-child:637-638`.

### HF04 — Hyrule Field

- Age/progress: child; Bombs; Storms for cover comparison; no fire for web test. Session 6.
- Do/watch: Bomb open the wetlands hole north of Lake Hylia and the eastern hole near Zora River. List chests, fish, grass/bugs and beehives in each.
- Target: `remake/child_hyrule_field.toml` — child_hyrule_field.toml Fish events and HF Southeast/Open/Near Market Grotto Chest exclusions.
- Answer changes: Confirm absence or provide a stable location/source before restoring a check.
- Source: `plans/rounds/r4-logic-child:350-366; r4-logic-child:637-638`.

### HF05 — Hyrule Field

- Age/progress: child now; adult then child later; Day; uncollected tree token; age return unlocked for HF06. Session 2.
- Do/watch: By day, roll into the lone tree between the forest exit and ranch. Does its Gold Skulltula appear?
- Target: `remake/child_hyrule_field.toml` — fact: HF GS Lone Tree 2177746409373494991 time rule.
- Answer changes: Day appearance removes a night gate for the new location; absence alone needs a fresh uncollected control.
- Source: `plans/rounds/r4-logic-child:363-377`.

### HF06 — Hyrule Field

- Age/progress: adult then child; Free return to child; password note unread on control copy. Session 10.
- Do/watch: Read the Fairy Note by the Gerudo-side heart-piece scrub as adult. Try buying as adult, then return as child who has not spoken to it. Can that child buy for 100? Also try opening the note chest as adult, then child.
- Target: `remake/child_hyrule_field.toml` — locations HF Deku Scrub Grotto; fact: note chest 2967378296224661060.
- Answer changes: Confirms age-memory prerequisite and chest access; do not convert this into simple shared inventory.
- Source: `plans/rounds/r4-logic-child:365-377`.

### LLR01 — Lon Lon Ranch

- Age/progress: child; Current ranch backup; no explosives. Session 2.
- Do/watch: Step on the stone circle by the south fence without Bombs. Does the three-scrub hole open? If not, test a bomb only when available.
- Target: `remake/child_lon_lon_ranch.toml` — exits Lon Lon Ranch -> LLR Grotto.
- Answer changes: Add explosives only if required; otherwise retain child-only entry.
- Source: `plans/rounds/r4-logic-child:412-425`.

### LLR02 — Lon Lon Ranch

- Age/progress: child; Current ranch backup; no explosives. Session 2.
- Do/watch: In the ruined tower, find the high chest above the boxes. Note the exact climb and whether a tool is needed. Check the tower-vine token at night later with Boomerang.
- Target: `remake/child_lon_lon_ranch.toml` — fact: tower chest 17445672702269453589; token 2730878115209290675.
- Answer changes: Defines new chest access and checks the proposed night/ranged token route.
- Source: `plans/rounds/r4-logic-child:412-425`.

### MK01 — Market

- Age/progress: child; After Zelda; Richard reward not yet taken. Session 2.
- Do/watch: By day, find Richard and lead him to his owner. Does she give the first Heart Piece in daylight?
- Target: `remake/child_market.toml` — locations Market Lost Dog.
- Answer changes: Successful first reward removes night; repeat rupees are not evidence for first reward.
- Source: `plans/rounds/r4-logic-child:475-483`.

### MK03 — Market

- Age/progress: child; After Zelda; Richard reward not yet taken. Session 2.
- Do/watch: Check the Bombchu Shop door between 18:00 and 21:00, then just after 21:00. When does it admit you?
- Target: `remake/child_market.toml` — exits Market Back Alley -> Market Bombchu Shop.
- Answer changes: Record exact hours; refine only if time predicates later distinguish dusk from night.
- Source: `plans/rounds/r4-logic-child:475-483`.

### MK02 — Market

- Age/progress: child; Dodongo beaten; isolated copy with no Bomb Bag/Bombchus. Session 5.
- Do/watch: After Dodongo, with no Bomb Bag and no Bombchus ever obtained, ask to bowl. Are Bombchus lent, and do wins pay the first three prizes? On a pre-Dodongo copy, check refusal.
- Target: `remake/child_market.toml` — locations Market Bombchu Bowling First Prize; Second Prize; Bombchus; Bomb.
- Answer changes: Lending permits removing explosives/found-bombchus gates while keeping boss-clear. Owning but unequipping a bag is not this test.
- Source: `plans/rounds/r4-logic-child:479-481`.

### HC01 — Hyrule Castle / Zora quest

- Age/progress: child; Before diving-game quest; King Zora first talk. Session 5.
- Do/watch: Talk to King Zora, try the diving game and letter route before visiting Impa again. If stopped, speak to Impa at the castle and retry. What changes?
- Target: `remake/child_hyrule_castle.toml` — fact: Get_StoneOfWater Step03_Impa / StoneOfWater_ClearDivingGame.
- Answer changes: Add the demonstrated castle-visit event to Zora progression; no gate if both routes already work.
- Source: `plans/rounds/r4-logic-child:533-540`.

### KAK01 — Kakariko

- Age/progress: child; After Zelda; daytime/night comparison; Boomerang for KAK02. Session 3.
- Do/watch: By day, roll into the narrow tree near the village entrance. Does the uncollected Gold Skulltula drop?
- Target: `remake/child_kakariko.toml` — locations Kak GS Tree.
- Answer changes: Remove night if observed by day.
- Source: `plans/rounds/r4-logic-child:628-640`.

### KAK02 — Kakariko

- Age/progress: child; After Zelda; daytime/night comparison; Boomerang for KAK02. Session 3.
- Do/watch: As child on the windmill floor, throw Boomerang at the beam Heart Piece. Does it return with the item?
- Target: `remake/child_kakariko.toml` — translated kakariko.toml locations Kak Windmill Freestanding PoH.
- Answer changes: Remove child Boomerang branch if retrieval cannot work; keep actual successful route.
- Source: `plans/rounds/r4-logic-child:628-640`.

### KAK03 — Kakariko

- Age/progress: child; After Zelda; daytime/night comparison; Boomerang for KAK02. Session 3.
- Do/watch: Try the ladders beside Impa and a cucco glide to the cow-shed/Impa roof. Can child reach the Heart Piece without the owl?
- Target: `remake/child_kakariko.toml` — exits Kakariko Village -> Kak Impas Ledge.
- Answer changes: Restore a child route only with reproducible steps.
- Source: `plans/rounds/r4-logic-child:628-640`.

### KAK04 — Kakariko

- Age/progress: child; After Zelda; daytime/night comparison; Boomerang for KAK02. Session 3.
- Do/watch: At night, are the cuccos at the fence and windmill hill present? If so, can child glide to Granny rooftop?
- Target: `remake/child_kakariko.toml` — exits Kakariko Village -> Kak Odd Medicine Rooftop.
- Answer changes: Remove day condition only if the night traversal succeeds.
- Source: `plans/rounds/r4-logic-child:628-640`.

### GY01 — Graveyard

- Age/progress: child; Night; Lullaby; unvisited harp graves; no weapon for GY01. Session 3.
- Do/watch: At the shield grave chest, try opening while the ReDead lives, without sword/sticks/Din Fire. Separately stun it with Sun Song and try.
- Target: `remake/child_graveyard.toml` — locations Graveyard Shield Grave Chest.
- Answer changes: Opening relaxes kill gate; song-only success adds song alternative.
- Source: `plans/rounds/r4-logic-child:688-696`.

### GY02 — Graveyard

- Age/progress: child; Night; Lullaby; unvisited harp graves; no weapon for GY01. Session 3.
- Do/watch: Before touching Sharp/Flat graves, play Lullaby on the Royal Tomb Triforce. Does it open?
- Target: `remake/child_graveyard.toml` — exits Graveyard -> Graveyard Royal Familys Tomb.
- Answer changes: If brothers must be defeated, add combat/story prerequisite.
- Source: `plans/rounds/r4-logic-child:688-696`.

### GY03 — Graveyard

- Age/progress: child; Night; Lullaby; unvisited harp graves; no weapon for GY01. Session 3.
- Do/watch: In the Royal Tomb, clear Keese, inspect for torches/chest, and cast Din Fire when available. Does any chest spawn?
- Target: `remake/child_graveyard.toml` — locations Graveyard Royal Familys Tomb Chest n64_only.
- Answer changes: Restore only an identified real chest; otherwise retain exclusion.
- Source: `plans/rounds/r4-logic-child:688-696`.

### DMT01 — Death Mountain Trail

- Age/progress: child; Before breaking entrance boulder; bombs/no bracelet on test copy. Session 4.
- Do/watch: With no bracelet, try carried Bombs and Bombchus on the cavern boulder and fenced flower. Does either break the entrance?
- Target: `remake/child_death_mountain_trail.toml` — exits Death Mountain -> Dodongos Cavern Beginning; DMT GS Bean Patch; bean Fairy event.
- Answer changes: Restore explosives branches only if own explosives open it.
- Source: `plans/rounds/r4-logic-child:761-775`.

### DMT02 — Death Mountain Trail

- Age/progress: child; Before breaking entrance boulder; bombs/no bracelet on test copy. Session 4.
- Do/watch: With Bombs but no Slingshot/Boomerang, climb the spider wall below the owl. Can you safely get past all three?
- Target: `remake/child_death_mountain_trail.toml` — exits Death Mountain -> Death Mountain Summit.
- Answer changes: Add ranged weapon only if unavoidable spiders block climb; note health/damage rather than calling a hit proof of impossibility.
- Source: `plans/rounds/r4-logic-child:761-775`.

### DMT04 — Death Mountain Trail

- Age/progress: child; Before breaking entrance boulder; bombs/no bracelet on test copy. Session 4.
- Do/watch: From the bomb-flower ledge, try the child backflip over the low fence onto the trail Heart Piece. Record health lost and exact footing.
- Target: `remake/child_death_mountain_trail.toml` — translated death_mountain_trail.toml locations DMT Freestanding PoH.
- Answer changes: Keep or remove child can_take_damage route; isolated failure is inconclusive, not impossibility.
- Source: `plans/rounds/r4-logic-child:761-775`.

### DMT05 — Death Mountain Trail

- Age/progress: child; Before breaking entrance boulder; bombs/no bracelet on test copy. Session 4.
- Do/watch: Before breaking the cavern boulder, release bugs into its soil. Can you kill and collect the token?
- Target: `remake/child_death_mountain_trail.toml` — locations DMT GS Bean Patch.
- Answer changes: If accessible now, remove bracelet prerequisite for the soil check.
- Source: `plans/rounds/r4-logic-child:761-775`.

### GC01 — Goron City

- Age/progress: child; Bracelet; no Bomb Bag for flowers; bombs variant for maze. Session 4.
- Do/watch: Bomb through the upper west maze. Which two blue chests and token crate can child reach? Are purple/red blocked by grey/silver rocks?
- Target: `remake/child_goron_city.toml` — translated goron_city.toml locations GC Maze Center Chest; GC Maze Right Chest; fact chest identities.
- Answer changes: Pair physical chests to IDs before changing each reach rule.
- Source: `plans/rounds/r4-logic-child:887-896`.

### GC02 — Goron City

- Age/progress: child; Bracelet; no Bomb Bag for flowers; bombs variant for maze. Session 4.
- Do/watch: With bracelet but no Bomb Bag, light the four torches using a stick; throw Lost-Woods-wall bomb flowers into the spinning pot until a smile stops it. Does it pay?
- Target: `remake/child_goron_city.toml` — exits Goron City -> GC Spinning Pot.
- Answer changes: Success keeps normal strength branch; failure needs a controlled baseline, not automatic removal.
- Source: `plans/rounds/r4-logic-child:887-896`.

### GC03 — Goron City

- Age/progress: child; Bracelet; no Bomb Bag for flowers; bombs variant for maze. Session 4.
- Do/watch: With bracelet only, carry a bomb flower to the bottom shop wall. Does it open?
- Target: `remake/child_goron_city.toml` — translated goron_city.toml exits Goron City -> GC Shop.
- Answer changes: Confirms strength alternative; remove only if a verified different opener is required.
- Source: `plans/rounds/r4-logic-child:887-896`.

### ZR01 — Zora River

- Age/progress: child; No bombs for ZR01; night and no Boomerang for ZR02; Storms later. Session 5.
- Do/watch: Take the bean-seller cucco to the vine ledge, enter its hole and use the second cucco to reach the Heart Piece pillar, without Bombs. What blocks you?
- Target: `remake/child_zora_river.toml` — locations ZR Near Open Grotto Freestanding PoH.
- Answer changes: Add explosives only if actually required on the child route.
- Source: `plans/rounds/r4-logic-child:946-955`.

### ZR02 — Zora River

- Age/progress: child; No bombs for ZR01; night and no Boomerang for ZR02; Storms later. Session 5.
- Do/watch: At night below Domain entrance, try sword/sticks on the ivy Gold Skulltula and climb to its token, without Boomerang.
- Target: `remake/child_zora_river.toml` — locations ZR GS Ladder.
- Answer changes: Add Boomerang only if direct kill/collection is blocked.
- Source: `plans/rounds/r4-logic-child:946-955`.

### ZR03 — Zora River

- Age/progress: child or adult; Song of Storms. Session 6.
- Do/watch: Open the storms hole near the bean seller; inspect its whole room. Any Business Scrub?
- Target: `remake/child_zora_river.toml` — locations ZR Deku Scrub Grotto Front; Rear n64_only.
- Answer changes: Restore only identified real scrubs; otherwise confirm exclusions.
- Source: `plans/rounds/r4-logic-child:954-955`.

### ZD01 — Zora Domain

- Age/progress: child; Din Fire for ZD01; Silver Scale already won for ZD02. Session 5.
- Do/watch: With Din Fire and no sticks used, light all timed torches along the king stairs, shop/water paths and behind waterfall. Does the chest appear before they go out?
- Target: `remake/child_zoras_domain.toml` — translated zoras_domain.toml locations ZD Chest.
- Answer changes: Add Din Fire alternative only if the full timed route works.
- Source: `plans/rounds/r4-logic-child:994-1000`.

### LH01 — Lake Hylia

- Age/progress: child now; adult later; Day; token uncollected. Session 5.
- Do/watch: By day, swim to the southwest ledge and crawl to the old Small Island token tunnel. Is the token there? On an adult return, can you enter or reach it?
- Target: `remake/child_lake_hylia.toml` — locations LH GS Small Island.
- Answer changes: Remove night/child-only conditions only for demonstrated age/time routes.
- Source: `plans/rounds/r4-logic-child:1084-1088`.

### DC01 — Dodongo Cavern

- Age/progress: child; adult for Hammer/boots variants; Bombs; Slingshot-only variant for DC06; do comparisons before collecting Bomb Bag. Session 4.
- Do/watch: From the main hall upper lift landing, bomb the wall beside the Bomb Bag ledge. Does it break from this side? On an adult return test Hammer from each side.
- Target: `remake/child_dodongos_cavern.toml` — exits Dodongos Cavern Far Bridge <-> Dodongos Cavern Bomb Bag Ledge.
- Answer changes: Keep two-way explosive route if proven; add Hammer only on successful side(s).
- Source: `plans/rounds/r4-logic-child:1154-1172`.

### DC02 — Dodongo Cavern

- Age/progress: child; adult for Hammer/boots variants; Bombs; Slingshot-only variant for DC06; do comparisons before collecting Bomb Bag. Session 4.
- Do/watch: From the Armos/blade room upper south walkway, try walking round to the skull bridge without breaking the ledge wall. Does the path connect?
- Target: `remake/child_dodongos_cavern.toml` — exits Dodongos Cavern Climb -> Dodongos Cavern Far Bridge.
- Answer changes: Restore direct edge only for the actual connection.
- Source: `plans/rounds/r4-logic-child:1154-1172`.

### DC03 — Dodongo Cavern

- Age/progress: child; adult for Hammer/boots variants; Bombs; Slingshot-only variant for DC06; do comparisons before collecting Bomb Bag. Session 4.
- Do/watch: At the mesh above the stairs, try sword/climb collection with no ranged tool. Later compare Boomerang/Bow/Hookshot individually.
- Target: `remake/child_dodongos_cavern.toml` — locations Dodongos Cavern GS Vines Above Stairs.
- Answer changes: Add successful alternatives or remove failing tool branches after a positive control.
- Source: `plans/rounds/r4-logic-child:1154-1172`.

### DC04 — Dodongo Cavern

- Age/progress: child; adult for Hammer/boots variants; Bombs; Slingshot-only variant for DC06; do comparisons before collecting Bomb Bag. Session 4.
- Do/watch: As adult, Hammer the cracked wall off the skull bridge hiding the token. Does it break?
- Target: `remake/child_dodongos_cavern.toml` — locations Dodongos Cavern GS Alcove Above Stairs.
- Answer changes: Success changes explosives to can_blast_or_smash.
- Source: `plans/rounds/r4-logic-child:1154-1172`.

### DC05 — Dodongo Cavern

- Age/progress: child; adult for Hammer/boots variants; Bombs; Slingshot-only variant for DC06; do comparisons before collecting Bomb Bag. Session 4.
- Do/watch: As adult in the blade room, try Hover Boots and Longshot separately to reach the Bomb Bag ledge.
- Target: `remake/child_dodongos_cavern.toml` — exits Dodongos Cavern Climb -> Dodongos Cavern Bomb Bag Ledge.
- Answer changes: Keep only successful alternatives; never enable an N64 trick by assumption.
- Source: `plans/rounds/r4-logic-child:1154-1172`.

### DC06 — Dodongo Cavern

- Age/progress: child; adult for Hammer/boots variants; Bombs; Slingshot-only variant for DC06; do comparisons before collecting Bomb Bag. Session 4.
- Do/watch: As child with only Slingshot for damage, fight each Lizalfos pair without sword, sticks or bombs. Can both fights be won?
- Target: `remake/child_dodongos_cavern.toml` — exits Dodongos Cavern Lower Right Side -> Dodongos Cavern Torch Room; Upper Lizalfos -> Bomb Bag Ledge.
- Answer changes: Removes unsafe Slingshot combat branch if a controlled test establishes failure.
- Source: `plans/rounds/r4-logic-child:1154-1172`.

### DC07 — Dodongo Cavern

- Age/progress: child; adult for Hammer/boots variants; Bombs; Slingshot-only variant for DC06; do comparisons before collecting Bomb Bag. Session 4.
- Do/watch: At the staircase bomb-flower chain, try a carried Bomb, then Din Fire on a separate untriggered copy. Does each lower the stairs?
- Target: `remake/child_dodongos_cavern.toml` — exits Dodongos Cavern Staircase Room -> Dodongos Cavern Climb.
- Answer changes: Confirm or remove each non-strength trigger alternative.
- Source: `plans/rounds/r4-logic-child:1154-1172`.

### JJ01 — Jabu Jabu

- Age/progress: child; Before tentacles/Big Octo; no Scale for JJ02. Session 5.
- Do/watch: Before killing tentacles, inspect the basement west ledge by Big Octo door. Can you reach or Boomerang-collect the upper token from below? Adult grapple is a later nondefault-entry variant only.
- Target: `remake/child_jabu_jabus_belly.toml` — locations Jabu Jabus Belly GS Lobby Basement Upper.
- Answer changes: Move back to Main only if reachable before tentacle clear.
- Source: `plans/rounds/r4-logic-child:1215-1228`.

### JJ04 — Jabu Jabu

- Age/progress: child; Before tentacles/Big Octo; no Scale for JJ02. Session 5.
- Do/watch: Before Big Octo, can you reach the two wooden crates in the upper switch room toward the boss?
- Target: `remake/child_jabu_jabus_belly.toml` — translated jabu_jabus_belly.toml locations Jabu Jabus Belly Small Wooden Crate 1; 2.
- Answer changes: If only after Octo, move them to Before Boss.
- Source: `plans/rounds/r4-logic-child:1215-1228`.

### JJ05 — Jabu Jabu

- Age/progress: child; Before tentacles/Big Octo; no Scale for JJ02. Session 5.
- Do/watch: In the map/water-switch room, press the switch before killing Stingers. Does water rise and let you get the chest?
- Target: `remake/child_jabu_jabus_belly.toml` — locations Jabu Jabus Belly Map Chest.
- Answer changes: Add combat condition only if required; identify a working entry weapon.
- Source: `plans/rounds/r4-logic-child:1215-1228`.

### W01 — Bottom of the Well

- Age/progress: child; Storms drain; Lullaby; Boomerang; Lens for control, but do not use it in W05. Session 6.
- Do/watch: In coffin hall, pull the far-west slab without using sticks/Din Fire. Can you take the loose key and hearts without fire?
- Target: `remake/child_bottom_of_the_well.toml` — translated bottom_of_the_well.toml locations Bottom of the Well Freestanding Key; coffin hearts.
- Answer changes: Successful pull removes fire requirement for the demonstrated pickups.
- Source: `plans/rounds/r4-logic-child:1276-1290`.

### W02 — Bottom of the Well

- Age/progress: child; Storms drain; Lullaby; Boomerang; Lens for control, but do not use it in W05. Session 6.
- Do/watch: Without explosives, inspect/open the north-west fake-wall and front-centre B1 chests. Any actual bomb wall blocking either?
- Target: `remake/child_bottom_of_the_well.toml` — locations Bottom of the Well Back Left Bombable Chest; Front Center Bombable Chest.
- Answer changes: Remove explosives per verified chest identity, not old N64 label.
- Source: `plans/rounds/r4-logic-child:1276-1290`.

### W03 — Bottom of the Well

- Age/progress: child; Storms drain; Lullaby; Boomerang; Lens for control, but do not use it in W05. Session 6.
- Do/watch: Inspect Like Like room for a chest; also find the ladder chest by rooms 6/7. Record vanilla item and access to each.
- Target: `remake/child_bottom_of_the_well.toml` — translated bottom_of_the_well.toml locations Bottom of the Well Like Like Chest; fact Hash 12988877782812797760.
- Answer changes: Exclude absent Like Like chest or pair a real one with correct rule.
- Source: `plans/rounds/r4-logic-child:1276-1290`.

### W04 — Bottom of the Well

- Age/progress: child; Storms drain; Lullaby; Boomerang; Lens for control, but do not use it in W05. Session 6.
- Do/watch: Behind the west locked door, try collecting its token with Boomerang and no lit stick/Din Fire. Must a coffin burn first?
- Target: `remake/child_bottom_of_the_well.toml` — translated bottom_of_the_well.toml locations Bottom of the Well GS West Inner Room.
- Answer changes: Add fire if it blocks collection.
- Source: `plans/rounds/r4-logic-child:1276-1290`.

### W05 — Bottom of the Well

- Age/progress: child; Storms drain; Lullaby; Boomerang; Lens for control, but do not use it in W05. Session 6.
- Do/watch: With Lens switched off throughout, find east key niche, Compass room and central rooms using visible wall shading. Record falls/damage and reliable landmarks.
- Target: `remake/child_bottom_of_the_well.toml` — translated bottom_of_the_well.toml fake-wall entry; helpers logic_lens_botw.
- Answer changes: Evidence for owner decision: normal route or verified trick; not automatic default loosening.
- Source: `plans/rounds/r4-logic-child:1276-1290`.

### IC01 — Ice Cavern

- Age/progress: adult; Bottle/Blue Fire; before taking Boots; sword for IC02. Session 8.
- Do/watch: Past the Boots room, try the pool backdoor without Boots (record Scale). Then use Boots; can you collect Fountain bottom Heart Piece and surface without Zora Tunic?
- Target: `remake/child_ice_cavern.toml` — exits Ice Cavern End -> Zoras Fountain; translated ZF Bottom Freestanding PoH.
- Answer changes: Relax only observed dive/heat conditions; record damage/air and escape route.
- Source: `plans/rounds/r4-logic-child:1334-1343`.

### IC02 — Ice Cavern

- Age/progress: adult; Bottle/Blue Fire; before taking Boots; sword for IC02. Session 8.
- Do/watch: Along the Compass/nearby token path, break blocking ice pillars using Master Sword, never Hammer. Can you finish both paths?
- Target: `remake/child_ice_cavern.toml` — locations Ice Cavern Compass Chest; Ice Cavern GS Heart Piece Room.
- Answer changes: Add Hammer only if a mandatory pillar demonstrably needs it.
- Source: `plans/rounds/r4-logic-child:1334-1343`.

### IC03 — Ice Cavern

- Age/progress: adult; Bottle/Blue Fire; before taking Boots; sword for IC02. Session 8.
- Do/watch: Inspect every main-path ice/arrow target. Does any required door stay shut until an arrow hits one?
- Target: `remake/child_ice_cavern.toml` — fact: Ice Cavern critical-path exits.
- Answer changes: Add Bow only to a demonstrated mandatory gate, naming its room.
- Source: `plans/rounds/r4-logic-child:1334-1343`.

### FT01 — Forest approach / first adult

- Age/progress: adult; Just after first pull; Hookshot acquired for normal Forest route. Session 1.
- Do/watch: In the first entrance room, try taking the token without Hookshot: kill with Bow/Bombs if owned, then climb/hand-collect; separately try sword from reachable vines. Does either collect it?
- Target: `forest_temple.toml` — locations Forest Temple GS First Room; Forest Temple GS Lobby (record which room).
- Answer changes: Add a no-Hookshot collection path only if the actual token is taken.
- Source: `plans/rounds/r4-logic-adult:48-53; r3-world:186-187`.

### FT02 — Forest approach / first adult

- Age/progress: adult; Just after first pull; Hookshot acquired for normal Forest route. Session 1.
- Do/watch: In the west garden, aim ordinary Hookshot from the lower floor at the token. Can you collect without Longshot or upper ledge?
- Target: `forest_temple.toml` — locations Forest Temple GS Level Island Courtyard.
- Answer changes: Loosen range/ledge prerequisite only for a working standing point.
- Source: `plans/rounds/r4-logic-adult:48-53; r3-world:186-187`.

### FT03 — Forest approach / first adult

- Age/progress: adult; Just after first pull; Hookshot acquired for normal Forest route. Session 1.
- Do/watch: At the east garden token ledge, try the upper falling-room route without summoning Pierre; check direct Hookshot. Boomerang is a later nondefault child-entry variant only.
- Target: `forest_temple.toml` — remake/adult_forest_temple.toml locations Forest Temple GS Raised Island Courtyard.
- Answer changes: Successful alternate access replaces scarecrow-only rule; do not import child access from N64.
- Source: `plans/rounds/r4-logic-adult:48-53; r3-world:186-187`.

### FT04 — Forest approach / first adult

- Age/progress: adult; Just after first pull; Hookshot acquired for normal Forest route. Session 1.
- Do/watch: At each iced eye (upper hall and rotating basement), try Din Fire without firing an arrow. Does it melt AND activate the eye?
- Target: `forest_temple.toml` — remake/adult_forest_temple.toml exits Forest Temple Frozen Eye Switch Room -> Forest Temple Falling Room; Forest Temple Basement -> Forest Temple Before Boss.
- Answer changes: Add Din Fire separately for each working puzzle.
- Source: `plans/rounds/r4-logic-adult:48-53; r3-world:186-187`.

### FT05 — Forest approach / first adult

- Age/progress: adult; Just after first pull; Hookshot acquired for normal Forest route. Session 1.
- Do/watch: At the basement token, try walking/jumping to take it before grappling.
- Target: `forest_temple.toml` — locations Forest Temple GS Basement.
- Answer changes: Hand collection removes ranged prerequisite.
- Source: `plans/rounds/r4-logic-adult:48-53; r3-world:186-187`.

### FT06 — Forest approach / first adult

- Age/progress: adult; Just after first pull; Hookshot acquired for normal Forest route. Session 1.
- Do/watch: In Phantom Ganon phase one, hit the real rider with ordinary Hookshot instead of Bow. Does it damage/advance the fight?
- Target: `forest_temple.toml` — events Phantom Ganon Boss Room -> Defeat Phantom Ganon.
- Answer changes: Keep or remove boss Hookshot alternative on observed phase-one result; sword rally remains separate.
- Source: `plans/rounds/r4-logic-adult:48-53; r3-world:186-187`.

### FT07 — Forest approach / first adult

- Age/progress: adult; Just after first pull; Hookshot acquired for normal Forest route. Session 1.
- Do/watch: Before taking the entrance-tree key, inspect the front lock. As you proceed, note keys acquired/spent at entrance, west lobby, straightened hall, both final locks.
- Target: `forest_temple.toml` — remake/adult_forest_temple.toml lock exits.
- Answer changes: Confirm five-lock route; report exact first mismatching door, not just a total.
- Source: `plans/rounds/r4-logic-adult:48-53; r3-world:186-187`.

### AO01 — First adult overworld

- Age/progress: adult; Just after pull; no later-temple progress required; compare before buying/collecting. Session 1.
- Do/watch: In Kakariko windmill, try reaching the Heart Piece by a normal jump, without Song of Time race exit or Hookshot. On rooftops, record any direct jump to Impa/Granny without grappling.
- Target: `kakariko.toml` — locations Kak Windmill Freestanding PoH; exits to Kak Impas Rooftop / Odd Medicine Rooftop.
- Answer changes: A working normal route can relax only that exit; record footing and damage.
- Source: `plans/rounds/r4-logic-adult:162-179 unresolved matrix`.

### AO02 — First adult overworld

- Age/progress: adult; Just after pull; no later-temple progress required; compare before buying/collecting. Session 1.
- Do/watch: Race Dampe twice on an unmodified copy. Record which goal chest opens each run, time, reward, whether other goal chests remain usable and whether a slower repeat changes it.
- Target: `kakariko.toml` — fact: Dampe four goal-chest selection; Graveyard Dampe Race Freestanding PoH.
- Answer changes: Establishes one-time vs repeat chest identities and timer gates; no swap certification from vanilla play.
- Source: `plans/rounds/r4-logic-adult:162-179 unresolved matrix`.

### AO03 — First adult overworld

- Age/progress: adult; Just after pull; no later-temple progress required; compare before buying/collecting. Session 1.
- Do/watch: Check an ordinary grave by day and night as adult. Does either time block opening it? Try reaching the ledge Heart Piece by hand without a bean/Longshot.
- Target: `kakariko.toml` — graveyard.toml grave exits; locations Graveyard Freestanding PoH.
- Answer changes: Record time restriction and a real hand route separately.
- Source: `plans/rounds/r4-logic-adult:162-179 unresolved matrix`.

### AO04 — First adult overworld

- Age/progress: adult; Just after pull; no later-temple progress required; compare before buying/collecting. Session 1.
- Do/watch: In Sacred Forest Meadow by day, is its adult token present? Try the normal flower/maze route without combat shortcuts; note any required tool before the Forest entrance.
- Target: `kakariko.toml` — sacred_forest_meadow.toml locations SFM GS; exits to Forest Temple Entrance Ledge.
- Answer changes: Day token would drop night gate; changed geometry needs specific exit correction.
- Source: `plans/rounds/r4-logic-adult:162-179 unresolved matrix`.

### AO05 — First adult overworld

- Age/progress: adult; Just after pull; no later-temple progress required; compare before buying/collecting. Session 1.
- Do/watch: In adult Kokiri, try ordinary jumps to bean-platform rupees and inspect Baba nut/stick drops; defer Hover attempt until boots are owned.
- Target: `kakariko.toml` — fact / rule review: kokiri_forest.toml bean-platform rupees; Deku Nut Drop; Deku Stick Drop.
- Answer changes: Evidence for adult drop/geometry alternatives, not automatic child access.
- Source: `plans/rounds/r4-logic-adult:162-179 unresolved matrix`.

### AO06 — First adult overworld

- Age/progress: adult; Just after pull; no later-temple progress required; compare before buying/collecting. Session 1.
- Do/watch: In Lost Woods try the river shortcut using ordinary dive/Scale; at the bridge note a normal jump/grapple route. Hover/Longshot comparison waits until owned.
- Target: `kakariko.toml` — fact / rule review: lost_woods.toml exits LW Underwater Entrance; LW Bridge -> Lost Woods.
- Answer changes: Record exact tool/range/depth and whether connection works.
- Source: `plans/rounds/r4-logic-adult:162-179 unresolved matrix`.

### AO07 — First adult overworld

- Age/progress: adult; Just after pull; no later-temple progress required; compare before buying/collecting. Session 7.
- Do/watch: In Goron City try stopping the rolling Goron using Bow alone before bombs/flowers; try collecting the ceiling token without grappling.
- Target: `kakariko.toml` — goron_city.toml locations GC Rolling Goron as Adult; remake/adult_goron_city.toml GC GS Center Platform.
- Answer changes: Add Bow or hand-collection alternatives only on success.
- Source: `plans/rounds/r4-logic-adult:162-179 unresolved matrix`.

### AO08 — First adult overworld

- Age/progress: adult; Just after pull; no later-temple progress required; compare before buying/collecting. Session 1.
- Do/watch: Check adult Ranch tree by day, then play the Ingo race/obstacle course normally. Record entry fees, first/repeat hurdle rewards and whether more wins add a new one-time prize.
- Target: `kakariko.toml` — lon_lon_ranch.toml Epona event; hurdle wonderitems; LLR GS Tree.
- Answer changes: Confirms adult tree availability and separates repeated money from new checks.
- Source: `plans/rounds/r4-logic-adult:162-179 unresolved matrix`.

### AO09 — Adult overworld returns

- Age/progress: adult; Have Hover/Longshot; hold off on timed trade hand-ins until ready. Session 10.
- Do/watch: Test Lost Woods bridge Hover and Longshot routes separately, then one timed mushroom/frog/eyedrops delivery. Record clock at start/arrival, warp/age-change reset behavior, and shortcut used.
- Target: `lost_woods.toml` — lost_woods.toml trade access/timeouts; death_mountain_trail.toml trade gates; lake_hylia.toml Eyedrops Access.
- Answer changes: Refines timed-trade/geometry assumptions; never infer all delivery routes from one success.
- Source: `plans/rounds/r4-logic-adult:162-179 unresolved matrix`.

### AO10 — Adult overworld returns

- Age/progress: adult; Have Hover/Longshot; hold off on timed trade hand-ins until ready. Session 10.
- Do/watch: At the old Field cow/bomb holes, test Hammer as adult without Bombs. Record which covers break; do not disturb the Storms comparison copies.
- Target: `lost_woods.toml` — hyrule_field.toml grotto exits; remake/child_hyrule_field.toml cow grotto edge.
- Answer changes: Remove obsolete adult Hammer restriction or add opener per actual hole, not globally.
- Source: `plans/rounds/r4-logic-adult:162-179 unresolved matrix`.

### AO11 — Adult overworld returns

- Age/progress: adult; Have Hover/Longshot; hold off on timed trade hand-ins until ready. Session 10.
- Do/watch: After earning Poe Collector bottle at five Poes, leave and revisit with another Poe. Does he repeat the bottle or give only money?
- Target: `lost_woods.toml` — remake/adult_market.toml Market 10 Big Poes; fact reward persistence.
- Answer changes: Confirms first-prize flag and five-Poe model; record later 1000-point reward separately.
- Source: `plans/rounds/r4-logic-adult:162-179 unresolved matrix`.

### FI01 — Adult mountains / Fire

- Age/progress: adult; Goron Tunic; eight-key dungeon; before pillar dropped for FI02. Session 7.
- Do/watch: Count acquired and spent keys at lava bridge (1), east/elevator pair (3 total), narrow walkway (4), flame maze (5), inner maze/Dancer (7), lower Boss Key loop (8). Does the moving-fire upper-maze shortcut consume any extra key?
- Target: `remake/adult_fire_temple.toml` — Fire Temple lock exits and Narrow Path Room -> Boulder Maze Upper.
- Answer changes: Correct only the door where observed order differs; all eight keys must be accounted for.
- Source: `plans/rounds/r4-logic-adult:135-139; 173; 221-226`.

### FI02 — Adult mountains / Fire

- Age/progress: adult; Goron Tunic; eight-key dungeon; before pillar dropped for FI02. Session 7.
- Do/watch: Before lowering the pillar, try Hover Boots from the near-boss side to the boss approach. Separately try Bombs to bypass the high-cell Time Block.
- Target: `remake/adult_fire_temple.toml` — exits Fire Temple Near Boss -> Before Boss; events Fire Temple Upper -> Fire Temple Pillar Lowered.
- Answer changes: Add only successful bypass; otherwise keep pillar/Hammer/Time route.
- Source: `plans/rounds/r4-logic-adult:135-139; 173; 221-226`.

### FI03 — Adult mountains / Fire

- Age/progress: adult; Goron Tunic; eight-key dungeon; before pillar dropped for FI02. Session 7.
- Do/watch: At first Flare Dancer, try ordinary Hookshot to expose its core without Bombs.
- Target: `remake/adult_fire_temple.toml` — exits Fire Temple Flame Maze -> Fire Temple Upper.
- Answer changes: Success adds Hookshot combat alternative.
- Source: `plans/rounds/r4-logic-adult:135-139; 173; 221-226`.

### FI04 — Adult mountains / Fire

- Age/progress: adult; Goron Tunic; eight-key dungeon; before pillar dropped for FI02. Session 7.
- Do/watch: In the crater from summit, test the short adult wall-heart visit without Tunic. Record starting hearts, burn ticks, time to collect AND escape. Compare child climb after return if still uncollected.
- Target: `remake/adult_fire_temple.toml` — remake/adult_death_mountain_crater.toml DMC Wall Freestanding PoH; crater heat exits.
- Answer changes: Evidence for explicit health/timer route; never assume OHKO safety.
- Source: `plans/rounds/r4-logic-adult:135-139; 173; 221-226`.

### FI05 — Adult mountains / Fire

- Age/progress: adult; Goron Tunic; eight-key dungeon; before pillar dropped for FI02. Session 7.
- Do/watch: With adult Hover/Longshot, try summit/crater ledges and volcano Heart Piece without planted bean, each tool separately. At Goron grotto, note lava crossings without boots.
- Target: `remake/adult_fire_temple.toml` — fact / rule review: death_mountain_trail.toml summit/heart routes; death_mountain_crater.toml volcano/Pierre routes; goron_city.toml grotto exits.
- Answer changes: Loosen only a reproducible route; document health/damage and escape.
- Source: `plans/rounds/r4-logic-adult:135-139; 173; 221-226`.

### FI06 — Adult mountains / Fire

- Age/progress: adult; Goron Tunic; eight-key dungeon; before pillar dropped for FI02. Session 7.
- Do/watch: Confirm the early lower-maze chest gives Map and the narrow-eye chest gives Compass on vanilla overlay-free play.
- Target: `remake/adult_fire_temple.toml` — remake/adult_fire_temple.toml Fire Temple Map Chest; Compass Chest.
- Answer changes: Closes r2 census event-name discrepancy; if different, correct chest identity, not event wording.
- Source: `plans/rounds/r4-logic-adult:135-139; 173; 221-226`.

### ZA01 — Zora / lake adult approach

- Age/progress: adult; Before Morpha; bottles, Blue Fire and Boots from Ice. Session 8.
- Do/watch: After thawing King Zora but before Morpha, try entering the shop and direct Domain-to-Lake shortcut. Immediately after Morpha, revisit both before any extra quest.
- Target: `remake/adult_zoras_domain.toml` — exits Zoras Domain -> ZD Shop; Lake Hylia; adult_lake_hylia.toml reverse shortcut.
- Answer changes: Records exact reopening milestone, not merely published post-clear route.
- Source: `plans/rounds/r4-logic-adult:175-178; 200-203; 228-233; 03-game-data section 13`.

### ZA02 — Zora / lake adult approach

- Age/progress: adult; Before Morpha; bottles, Blue Fire and Boots from Ice. Session 8.
- Do/watch: By day at frozen waterfall, inspect its token and try Bow/other ranged damage followed by hand collection without Hookshot.
- Target: `remake/adult_zoras_domain.toml` — locations ZD GS Frozen Waterfall.
- Answer changes: Distinguish kill from collection and day availability.
- Source: `plans/rounds/r4-logic-adult:175-178; 200-203; 228-233; 03-game-data section 13`.

### ZA03 — Zora / lake adult approach

- Age/progress: adult; Before Morpha; bottles, Blue Fire and Boots from Ice. Session 8.
- Do/watch: At Fountain hidden cave after lifting silver rocks, traverse and fight invisible spiders with Lens off. Does Lens consume magic when on? Try ordinary Hookshot for the cave token and note night dependence.
- Target: `remake/adult_zoras_domain.toml` — remake/adult_zoras_fountain.toml hidden-cave exits; ZF GS Hidden Cave; fact Lens magic.
- Answer changes: Can remove Lens/range/time gate only for reproducible safe route; report MP consumption separately.
- Source: `plans/rounds/r4-logic-adult:175-178; 200-203; 228-233; 03-game-data section 13`.

### ZA04 — Zora / lake adult approach

- Age/progress: adult; Before Morpha; bottles, Blue Fire and Boots from Ice. Session 8.
- Do/watch: At low-water lake before Morpha, shoot dawn sun and try collecting Fire Arrows via Pierre. Do both spawn and collection work before lake restoration?
- Target: `remake/adult_zoras_domain.toml` — remake/adult_lake_hylia.toml locations LH Sun.
- Answer changes: Successful low-water route adds distant-scarecrow branch; spawned but unreachable is not enough.
- Source: `plans/rounds/r4-logic-adult:175-178; 200-203; 228-233; 03-game-data section 13`.

### ZA05 — Zora / lake adult approach

- Age/progress: adult; Before Morpha; bottles, Blue Fire and Boots from Ice. Session 8.
- Do/watch: Try Water entrance without Iron Boots using Golden Scale/Longshot. Can you reach AND open the entrance and get back out?
- Target: `remake/adult_zoras_domain.toml` — remake/adult_lake_hylia.toml exits Lake Hylia -> Water Temple Lobby.
- Answer changes: Add dive alternative only for full entry/exit, not proximity.
- Source: `plans/rounds/r4-logic-adult:175-178; 200-203; 228-233; 03-game-data section 13`.

### ZA06 — Zora / lake adult approach

- Age/progress: adult; Before Morpha; bottles, Blue Fire and Boots from Ice. Session 8.
- Do/watch: In lake lab, try breaking/collecting the underwater token crate with Boots alone, then Hookshot. Test no Zora Tunic and record air/health/escape.
- Target: `remake/adult_zoras_domain.toml` — lake_hylia.toml locations LH GS Lab Crate.
- Answer changes: Removes only unnecessary crate/tool/tunic conditions.
- Source: `plans/rounds/r4-logic-adult:175-178; 200-203; 228-233; 03-game-data section 13`.

### ZA07 — Zora / lake adult approach

- Age/progress: adult; Before Morpha; bottles, Blue Fire and Boots from Ice. Session 8.
- Do/watch: At fishing pond, record age, measured fish length, lure and first/repeat prizes. Test loach reward if available; at lab, Golden-Scale dive as child on later return.
- Target: `remake/adult_zoras_domain.toml` — lake_hylia.toml LH Child Fishing; LH Adult Fishing; LH Loach Fishing; LH Lab Dive.
- Answer changes: Confirms age/length/prize identities and one shared lab reward; no assumed new location for repeat money.
- Source: `plans/rounds/r4-logic-adult:175-178; 200-203; 228-233; 03-game-data section 13`.

### ZA08 — Zora / lake adult approach

- Age/progress: adult; Before Morpha; bottles, Blue Fire and Boots from Ice. Session 8.
- Do/watch: At adult River entrance try passing boulders without Bombs; compare ordinary Hookshot vs Longshot on both high tokens. Try adult normal jump to Domain-side Heart Piece, then Hover/bean alternatives separately.
- Target: `remake/adult_zoras_domain.toml` — zora_river.toml front exit; ZR GS Above Bridge; ZR GS Near Raised Grottos; both heart-piece rules.
- Answer changes: Add only working age/tool routes; separate token kill from collection.
- Source: `plans/rounds/r4-logic-adult:175-178; 200-203; 228-233; 03-game-data section 13`.

### WA01 — Water Temple

- Age/progress: adult; Before spending keys; Boots/Hookshot/Lullaby; Hover for optional comparison. Session 9.
- Do/watch: Log each spent lock in order: pillar, middle-west water raise, high-west falling platforms, north basement. Record how many keys were acquired before each and confirm no extra lock before Dark Link.
- Target: `remake/adult_water_temple.toml` — Water Temple lock exits; Raise Water Level event.
- Answer changes: Correct graph at first mismatch; four total keys alone does not prove order.
- Source: `plans/rounds/r4-logic-adult:95-100`.

### WA02 — Water Temple

- Age/progress: adult; Before spending keys; Boots/Hookshot/Lullaby; Hover for optional comparison. Session 9.
- Do/watch: In Ruto cracked-wall room, after blasting wall, try taking its token by hand without Hookshot/Longshot.
- Target: `remake/adult_water_temple.toml` — locations Water Temple GS Falling Platform Room.
- Answer changes: Success removes ranged collection only; bomb-wall gate remains.
- Source: `plans/rounds/r4-logic-adult:95-100`.

### WA03 — Water Temple

- Age/progress: adult; Before spending keys; Boots/Hookshot/Lullaby; Hover for optional comparison. Session 9.
- Do/watch: At river and waterfall tokens, try ordinary Hookshot from reachable ground before Longshot. Record each working standing point.
- Target: `remake/adult_water_temple.toml` — water_temple.toml locations Water Temple GS River; Water Temple GS Near Boss Key Chest.
- Answer changes: Resolve range disagreement separately per token.
- Source: `plans/rounds/r4-logic-adult:95-100`.

### WA04 — Water Temple

- Age/progress: adult; Before spending keys; Boots/Hookshot/Lullaby; Hover for optional comparison. Session 9.
- Do/watch: At middle-water north target and north Boss Key block route, try Hover Boots without Longshot, one route at a time.
- Target: `remake/adult_water_temple.toml` — exits Water Temple Middle Water Level -> Water Temple Central Bow Target; Water Temple Dive -> Water Temple North Basement.
- Answer changes: Add only actual bypassed requirements, not general Hover substitution.
- Source: `plans/rounds/r4-logic-adult:95-100`.

### GE01 — Gerudo Valley / Fortress

- Age/progress: adult; Epona or Longshot bridge; membership later; no capture on main save for testing. Session 10.
- Do/watch: At Valley underwater hole where the old silver rock stood, inspect the cover. Try normal dive/Boots/Scale before songs or explosives; record the actual entrance and chest reached.
- Target: `remake/adult_gerudo_valley.toml` — gerudo_valley.toml underwater grotto exit; fact new chest identities.
- Answer changes: Replaces obsolete rock prerequisite only after mapping actual entrance.
- Source: `plans/rounds/r4-logic-adult:364-366; 509-515; r2-census:325-328`.

### GE02 — Gerudo Valley / Fortress

- Age/progress: adult; Epona or Longshot bridge; membership later; no capture on main save for testing. Session 10.
- Do/watch: Map Valley/fortress grottos: describe each chest position, vanilla content and opener; at old storms marks test Storms without Echo Gem.
- Target: `remake/adult_gerudo_valley.toml` — gerudo_valley.toml GV Storms Grotto; gerudo_fortress.toml GF Storms Grotto; fact new chest mapping.
- Answer changes: Confirms song gates or identifies always-open drop-hole; records absent scrubs/fairies separately.
- Source: `plans/rounds/r4-logic-adult:364-366; 509-515; r2-census:325-328`.

### GE03 — Gerudo Valley / Fortress

- Age/progress: adult; Epona or Longshot bridge; membership later; no capture on main save for testing. Session 10.
- Do/watch: At fortress old storms hole, try simply dropping before playing Storms. Are fairies still inside?
- Target: `remake/adult_gerudo_valley.toml` — remake/adult_gerudo_fortress.toml exits GF Entrances Behind Crates -> GF Storms Grotto; Fairy event.
- Answer changes: An always-open hole removes only this song gate; absence removes fairy source.
- Source: `plans/rounds/r4-logic-adult:364-366; 509-515; r2-census:325-328`.

### GE04 — Gerudo Valley / Fortress

- Age/progress: adult; Epona or Longshot bridge; membership later; no capture on main save for testing. Session 10.
- Do/watch: On disposable copy, let a guard capture you once. Free each carpenter by reachable route, recording named key, door opened and whether one cell key works elsewhere.
- Target: `remake/adult_gerudo_valley.toml` — gerudo_fortress.toml jail rescue/key location rules.
- Answer changes: Validates shared-key/capture reachability abstraction; report blocked rescue sequence precisely.
- Source: `plans/rounds/r4-logic-adult:364-366; 509-515; r2-census:325-328`.

### GE05 — Gerudo Valley / Fortress

- Age/progress: adult; Epona or Longshot bridge; membership later; no capture on main save for testing. Session 10.
- Do/watch: Try direct roof jumps and Hover routes separately, without grapple. Record route to each roof chest/token.
- Target: `remake/adult_gerudo_valley.toml` — gerudo_fortress.toml roof exits; GF Chest; GF GS Top Floor.
- Answer changes: Adds only reproducible normal geometry alternatives.
- Source: `plans/rounds/r4-logic-adult:364-366; 509-515; r2-census:325-328`.

### GE06 — Gerudo Valley / Fortress

- Age/progress: adult; Epona or Longshot bridge; membership later; no capture on main save for testing. Session 10.
- Do/watch: At horseback archery try admission by day/night, before/after membership and on/off Epona as available. Record fee and first rewards at 750/1400, then repeats.
- Target: `remake/adult_gerudo_valley.toml` — gerudo_fortress.toml GF HBA 1000 Points; GF HBA 1500 Points.
- Answer changes: Confirms admission predicates and renamed-score facts; no N64 threshold assumption.
- Source: `plans/rounds/r4-logic-adult:364-366; 509-515; r2-census:325-328`.

### GE07 — Gerudo Valley / Fortress

- Age/progress: adult; Epona or Longshot bridge; membership later; no capture on main save for testing. Session 10.
- Do/watch: Inspect Valley cow crate/waterfall wonderitems and fortress signs/crates; break each and record content and respawn after exit.
- Target: `remake/adult_gerudo_valley.toml` — fact / rule review: gerudo_valley.toml cow crate/waterfall wonderitems; gerudo_fortress.toml signs/crates.
- Answer changes: Corrects resource-source existence; no invented check from scenery.
- Source: `plans/rounds/r4-logic-adult:364-366; 509-515; r2-census:325-328`.

### GE08 — Gerudo Valley / Fortress

- Age/progress: adult; Epona or Longshot bridge; membership later; no capture on main save for testing. Session 10.
- Do/watch: Open Valley Lens chest before age change, then compare opposite-age chest; compare Kakariko purple windmill chest before/after area thaw/state change. Can each pair pay twice?
- Target: `remake/adult_gerudo_valley.toml` — fact: Valley Lens chest and Kakariko purple alternate Hash pairs.
- Answer changes: Informs one-vs-two-check product decision; same-position is not same save flag.
- Source: `plans/rounds/r4-logic-adult:364-366; 509-515; r2-census:325-328`.

### GT01 — Training Ground

- Age/progress: adult; Membership, Bow/Lens/Silver Gauntlets; short Hookshot for comparisons. Session 11.
- Do/watch: Facing in from lobby entrance, inspect both chest sides before eye switch. Open Lens-only west chest, then shoot the eye for east blue chest. Record left/right from that facing.
- Target: `remake/adult_gerudo_training_ground.toml` — locations Gerudo Training Ground Lobby Left Chest; Lobby Right Chest.
- Answer changes: Pair IDs 11182647876438515984 / 2436665354602612279 before splitting combined Lens/Bow requirements.
- Source: `plans/rounds/r4-logic-adult:342-345`.

### GT02 — Training Ground

- Age/progress: adult; Membership, Bow/Lens/Silver Gauntlets; short Hookshot for comparisons. Session 11.
- Do/watch: In Like Like/heavy-block room record room-clear red chest, cracked-wall Bombs chest and eye-switch Seed chest by position. Which are First/Second old names?
- Target: `remake/adult_gerudo_training_ground.toml` — locations Gerudo Training Ground Heavy Block First Chest; Heavy Block Second Chest.
- Answer changes: Replace shared wall condition only after physical-to-ID pairing, not guesses from old names.
- Source: `plans/rounds/r4-logic-adult:342-345`.

### GT03 — Training Ground

- Age/progress: adult; Membership, Bow/Lens/Silver Gauntlets; short Hookshot for comparisons. Session 11.
- Do/watch: At Wolfos silver-block invisible eye, try Hookshot instead of Bow with Lens on. Does door open?
- Target: `remake/adult_gerudo_training_ground.toml` — exits Gerudo Training Ground Heavy Block Room -> Gerudo Training Ground Like Like Room.
- Answer changes: Success adds Hookshot eye-switch alternative.
- Source: `plans/rounds/r4-logic-adult:342-345`.

### GT04 — Training Ground

- Age/progress: adult; Membership, Bow/Lens/Silver Gauntlets; short Hookshot for comparisons. Session 11.
- Do/watch: Try hot-room loop without Tunic; record hearts, burn ticks, time and whether exit/upper door is reached alive.
- Target: `remake/adult_gerudo_training_ground.toml` — GTG lava entrance exits; Near Scarecrow Chest.
- Answer changes: Only supports explicit safe heat route; not universal no-Tunic access.
- Source: `plans/rounds/r4-logic-adult:342-345`.

### GT05 — Training Ground

- Age/progress: adult; Membership, Bow/Lens/Silver Gauntlets; short Hookshot for comparisons. Session 11.
- Do/watch: Summon Pierre then try ordinary Hookshot from reachable floor/ledge, without Longshot.
- Target: `remake/adult_gerudo_training_ground.toml` — locations Gerudo Training Ground Near Scarecrow Chest.
- Answer changes: Short-grapple success relaxes distant-scarecrow route.
- Source: `plans/rounds/r4-logic-adult:342-345`.

### GT06 — Training Ground

- Age/progress: adult; Membership, Bow/Lens/Silver Gauntlets; short Hookshot for comparisons. Session 11.
- Do/watch: From upper eye-statue doorway, try solving all eye targets without dropping to floor; can you open and return to the near-scarecrow chest?
- Target: `remake/adult_gerudo_training_ground.toml` — locations Gerudo Training Ground Near Scarecrow Chest region/rule.
- Answer changes: Successful upper-only solution changes floor-puzzle/return requirement.
- Source: `plans/rounds/r4-logic-adult:342-345`.

### HW01 — Haunted Wasteland

- Age/progress: adult; Membership, Lens; Hover/Longshot separately for sand; wallet money for seller. Session 12.
- Do/watch: On separate approaches, cross quicksand with Hover Boots only, then Longshot only. Can each reach safe ground and continue?
- Target: `remake/adult_haunted_wasteland.toml` — haunted_wasteland.toml quicksand exit.
- Answer changes: Keep or remove each alternative; guide using both does not prove both required.
- Source: `plans/rounds/r4-logic-adult:486-491`.

### HW02 — Haunted Wasteland

- Age/progress: adult; Membership, Lens; Hover/Longshot separately for sand; wallet money for seller. Session 12.
- Do/watch: At ruin token, try ordinary Hookshot before Longshot; identify the surviving Colossus-side crate, break it and inspect four ruin pots.
- Target: `remake/adult_haunted_wasteland.toml` — haunted_wasteland.toml Wasteland GS; Wasteland Crate Near Colossus; pots.
- Answer changes: Records range, real crate identity and renewable resources.
- Source: `plans/rounds/r4-logic-adult:486-491`.

### HW03 — Haunted Wasteland

- Age/progress: adult; Membership, Lens; Hover/Longshot separately for sand; wallet money for seller. Session 12.
- Do/watch: At desert salesman, record offered Bombchu count, price, wallet capacity needed and whether he sells again after leaving.
- Target: `remake/adult_haunted_wasteland.toml` — haunted_wasteland.toml Wasteland Bombchu Salesman.
- Answer changes: Sets price/wallet and one-time/repeat facts.
- Source: `plans/rounds/r4-logic-adult:486-491`.

### HW04 — Haunted Wasteland

- Age/progress: adult; Membership, Lens; Hover/Longshot separately for sand; wallet money for seller. Session 12.
- Do/watch: At ruin, light all three torches, open the chest and record actual item.
- Target: `remake/adult_haunted_wasteland.toml` — haunted_wasteland.toml Wasteland Chest.
- Answer changes: Confirms Business Scrub Seed reward; world-item representation is reviewer-owned, not a playtest decision.
- Source: `plans/rounds/r4-logic-adult:486-491`.

### CO01 — Desert Colossus

- Age/progress: adult; child comparison after return; Night; Hookshot/Longshot; bean absent for bypass test. Session 12.
- Do/watch: At north-west cliff token, try ordinary Hookshot from every safe reachable standing point, then Longshot. Later as child compare Boomerang.
- Target: `remake/adult_desert_colossus.toml` — locations Colossus GS Tree.
- Answer changes: Adds short-Hookshot branch only for actual collection; keep night until day control observed.
- Source: `plans/rounds/r4-logic-adult:404-407; r3-world:184-185`.

### CO02 — Desert Colossus

- Age/progress: adult; child comparison after return; Night; Hookshot/Longshot; bean absent for bypass test. Session 12.
- Do/watch: Without planted bean, try Hover and Longshot separately to the bean-platform heart and token.
- Target: `remake/adult_desert_colossus.toml` — desert_colossus.toml Colossus Freestanding PoH; Colossus GS Hill.
- Answer changes: Add only proven no-bean route.
- Source: `plans/rounds/r4-logic-adult:404-407; r3-world:184-185`.

### CO03 — Desert Colossus

- Age/progress: adult; child comparison after return; Night; Hookshot/Longshot; bean absent for bypass test. Session 12.
- Do/watch: Lift grotto rock, inspect the purple chest and whole room; any scrubs? Record position and route.
- Target: `remake/adult_desert_colossus.toml` — locations Colossus Deku Scrub Grotto Front; Rear n64_only; fact chest 1186167733408299582.
- Answer changes: Confirms exclusions and new chest identity, not a renamed scrub.
- Source: `plans/rounds/r4-logic-adult:404-407; r3-world:184-185`.

### SP01 — Spirit Temple

- Age/progress: child then adult; Child keys first; adult Silver Gauntlets, Mirror Shield; short Hookshot comparison. Session 13.
- Do/watch: After Lullaby spawns the hand key, try direct hand target/jump without summoning Pierre. Can you collect and leave?
- Target: `remake/adult_spirit_temple.toml` — locations Spirit Temple Statue Room Hand Chest.
- Answer changes: Success removes distant-scarecrow requirement in favour of real direct route.
- Source: `plans/rounds/r4-logic-adult:302-307; 615-617`.

### SP02 — Spirit Temple

- Age/progress: child then adult; Child keys first; adult Silver Gauntlets, Mirror Shield; short Hookshot comparison. Session 13.
- Do/watch: Fight first invisible Floormaster with Lens off; can you finish and receive chest normally?
- Target: `remake/adult_spirit_temple.toml` — fact / rule review: spirit_temple.toml invisible Floormaster/chest access.
- Answer changes: Adds/removes visibility-combat gate only for observed route; seeing enemy is not mandatory combat by itself.
- Source: `plans/rounds/r4-logic-adult:302-307; 615-617`.

### SP03 — Spirit Temple

- Age/progress: child then adult; Child keys first; adult Silver Gauntlets, Mirror Shield; short Hookshot comparison. Session 13.
- Do/watch: Try ordinary Hookshot at moving wall, Boss Key platform and final statue face separately, then use Longshot as positive control.
- Target: `remake/adult_spirit_temple.toml` — spirit_temple.toml Adult Climb/upper exits; Spirit Temple Boss Key Chest.
- Answer changes: Require Longshot only at proven out-of-range mandatory crossing.
- Source: `plans/rounds/r4-logic-adult:302-307; 615-617`.

### SP04 — Spirit Temple

- Age/progress: child then adult; Child keys first; adult Silver Gauntlets, Mirror Shield; short Hookshot comparison. Session 13.
- Do/watch: At Beamos/Anubis sequence, try Hammer without explosives; note each enemy/barrier it can clear and how Anubis is finished.
- Target: `remake/adult_spirit_temple.toml` — spirit_temple.toml adult combat/explosives exits.
- Answer changes: Add Hammer only to the actual successful encounter.
- Source: `plans/rounds/r4-logic-adult:302-307; 615-617`.

### SP05 — Spirit Temple

- Age/progress: child then adult; Child keys first; adult Silver Gauntlets, Mirror Shield; short Hookshot comparison. Session 13.
- Do/watch: As adult, try equipping/using Slingshot in the item menu and hitting an ordinary eye. Is it usable or only ambiguous guide wording?
- Target: `remake/adult_spirit_temple.toml` — helpers.toml can_use(Slingshot); age/tool fact.
- Answer changes: Reviewer owns any broad age-usage change; do not loosen from guide wording.
- Source: `plans/rounds/r4-logic-adult:302-307; 615-617`.

### SP06 — Spirit Temple

- Age/progress: child then adult; Child keys first; adult Silver Gauntlets, Mirror Shield; short Hookshot comparison. Session 13.
- Do/watch: In sun-block room, move cube into window light without lighting torches; does key chest appear before collecting silver rupees? Record child/adult side and keys spent to enter.
- Target: `remake/adult_spirit_temple.toml` — locations Spirit Temple Sun Block Room Chest; cross-age key abstraction.
- Answer changes: Confirms revised spawn condition and supplies chronology missing from worst-order key count.
- Source: `plans/rounds/r4-logic-adult:302-307; 615-617`.

### SH01 — Shadow Temple

- Age/progress: adult; No strength upgrades for SH06; Lens off comparisons only on disposable copy. Session 14.
- Do/watch: At high scythe-room silver rupee, try ordinary Hookshot target, then Longshot. Can short Hookshot collect it?
- Target: `remake/adult_shadow_temple.toml` — locations Shadow Temple Scythe Shortcut Silver Rupee Ledge.
- Answer changes: Short range success keeps existing gate; longer-only adds Longshot.
- Source: `plans/rounds/r4-logic-adult:268-272; 420-425; r3-world:188`.

### SH02 — Shadow Temple

- Age/progress: adult; No strength upgrades for SH06; Lens off comparisons only on disposable copy. Session 14.
- Do/watch: At fan corridor try timed walking and Hookshot without Iron Boots; then Boots as control. Can you safely cross both directions?
- Target: `remake/adult_shadow_temple.toml` — shadow_temple.toml Wind Tunnel exits.
- Answer changes: Add Boots only if mandatory; record timing and damage.
- Source: `plans/rounds/r4-logic-adult:268-272; 420-425; r3-world:188`.

### SH03 — Shadow Temple

- Age/progress: adult; No strength upgrades for SH06; Lens off comparisons only on disposable copy. Session 14.
- Do/watch: At invisible Floormaster, keep Lens off and finish fight. Does key chest appear and remain reachable?
- Target: `remake/adult_shadow_temple.toml` — locations Shadow Temple Invisible Floormaster Chest.
- Answer changes: Distinguishes visibility help from mandatory combat gate; web gate remains separate.
- Source: `plans/rounds/r4-logic-adult:268-272; 420-425; r3-world:188`.

### SH04 — Shadow Temple

- Age/progress: adult; No strength upgrades for SH06; Lens off comparisons only on disposable copy. Session 14.
- Do/watch: Beyond boat, try Pierre/Hover/Longshot routes without Bomb Bag to bypass cracked-pillar bridge.
- Target: `remake/adult_shadow_temple.toml` — exits Shadow Temple Beyond Boat -> Before Boss; Beyond Boat SoT Block -> Before Boss.
- Answer changes: Add only full successful bridge bypass; no Time Block is assumed to exist.
- Source: `plans/rounds/r4-logic-adult:268-272; 420-425; r3-world:188`.

### SH05 — Shadow Temple

- Age/progress: adult; No strength upgrades for SH06; Lens off comparisons only on disposable copy. Session 14.
- Do/watch: In fifth-lock spike-wall room, use Fire Arrows without Din Fire. Do both walls burn so Boss Key and left chest can be opened?
- Target: `remake/adult_shadow_temple.toml` — locations Shadow Temple Boss Key Chest; Spike Walls Left Chest.
- Answer changes: Adds fire-arrow branch while retaining fifth-key gate.
- Source: `plans/rounds/r4-logic-adult:268-272; 420-425; r3-world:188`.

### SH06 — Shadow Temple

- Age/progress: adult; No strength upgrades for SH06; Lens off comparisons only on disposable copy. Session 14.
- Do/watch: With no bracelet/gauntlets, push falling-spikes cube and boat cube separately. Can each move far enough? Ride ceiling to token with no Hookshot and note damage.
- Target: `remake/adult_shadow_temple.toml` — shadow_temple.toml strength exits; remake/adult_shadow_temple.toml Shadow Temple GS Falling Spikes Room.
- Answer changes: Remove strength only for tested cube; no-damage ride distinguishes normal route from damage/trick.
- Source: `plans/rounds/r4-logic-adult:268-272; 420-425; r3-world:188`.

### SH07 — Shadow Temple

- Age/progress: adult; No strength upgrades for SH06; Lens off comparisons only on disposable copy. Session 14.
- Do/watch: Beyond boat, Bomb each rotating skull; does the token emerge only after an explosion? Is any alternate nonbomb hit effective?
- Target: `remake/adult_shadow_temple.toml` — locations Shadow Temple GS Triple Giant Pot.
- Answer changes: Confirms r3 skull question and bombs-only drop; do not loosen from skull destruction without token.
- Source: `plans/rounds/r4-logic-adult:268-272; 420-425; r3-world:188`.

### SH08 — Shadow Temple

- Age/progress: adult; No strength upgrades for SH06; Lens off comparisons only on disposable copy. Session 14.
- Do/watch: Check old loose-heart sites, especially the absent Time Block/scarecrow dead end; record each present/missing location and whether spawned from a pot.
- Target: `remake/adult_shadow_temple.toml` — fact / rule review: shadow_temple.toml freestanding-heart locations.
- Answer changes: Seven inherited heart sources need individual existence records before exclusion.
- Source: `plans/rounds/r4-logic-adult:268-272; 420-425; r3-world:188`.

### SH09 — Shadow Temple

- Age/progress: adult; No strength upgrades for SH06; Lens off comparisons only on disposable copy. Session 14.
- Do/watch: Log five keys and their spent doors; confirm fifth opens spike-wall room, while boss approach has no small-key lock. At post-boat pillar use carried Bombs as normal route control.
- Target: `remake/adult_shadow_temple.toml` — Shadow Temple lock graph; Beyond Boat -> Before Boss.
- Answer changes: Confirms graph and Bomb-Bag bridge requirement independently of alternate bypasses.
- Source: `plans/rounds/r4-logic-adult:268-272; 420-425; r3-world:188`.

### EN01 — Endgame triggers

- Age/progress: adult; Preserve pre-trigger copy before each sage reward. Session 15.
- Do/watch: Before Fire/Water/Forest are all complete, visit Kakariko after each sage if possible. When does Nocturne scene trigger? Record exact medallions and completed temples.
- Target: `remake/adult_temple_of_time.toml` — kakariko.toml Sheik in Kakariko.
- Answer changes: Determines exact trigger; later all-sage success cannot prove earlier sufficiency.
- Source: `plans/rounds/r4-logic-adult:170; 200-203`.

### EN02 — Endgame triggers

- Age/progress: adult; Preserve pre-trigger copy before each sage reward. Session 15.
- Do/watch: If a reviewed seed naturally gives Shadow/Spirit before other sages, visit Temple before completing the others. Does Light Arrows scene trigger? Record all boss-clear flags/items.
- Target: `remake/adult_temple_of_time.toml` — locations ToT Light Arrows Cutscene.
- Answer changes: Relaxes five-medallion gate only with reduced-sage positive evidence; otherwise remains untested, not failed.
- Source: `plans/rounds/r4-logic-adult:170; 200-203`.

### GA01 — Ganon Castle / Tower

- Age/progress: adult; All six trials accessible; Light Arrows; Gauntlets; before relevant puzzle solved. Session 15.
- Do/watch: In Forest wind trial, label five diamonds by physical position and collection order. Try normal jumps/short Hookshot before Hover/Time; record which tool each actually needs.
- Target: `remake/adult_ganons_castle.toml` — fact / rule review: locations Ganons Castle Forest Trial silver rupees; exit Forest Trial Wind Room -> Ending.
- Answer changes: Split combined end gate into correctly identified per-diamond requirements after mapping.
- Source: `plans/rounds/r4-logic-adult:458-467; 509-515; 03-game-data section 13`.

### GA02 — Ganon Castle / Tower

- Age/progress: adult; All six trials accessible; Light Arrows; Gauntlets; before relevant puzzle solved. Session 15.
- Do/watch: At Spirit ceiling web, shoot ordinary arrow through lit candle. On a separate unsolved copy try Din Fire from below. Does web fully burn and sun switch become usable?
- Target: `remake/adult_ganons_castle.toml` — exits Ganons Castle Spirit Trial Second Room Back -> Ending.
- Answer changes: Adds precise fire-transfer options, not every fire source by assumption.
- Source: `plans/rounds/r4-logic-adult:458-467; 509-515; 03-game-data section 13`.

### GA03 — Ganon Castle / Tower

- Age/progress: adult; All six trials accessible; Light Arrows; Gauntlets; before relevant puzzle solved. Session 15.
- Do/watch: At Shadow final stone and invisible chest-switch route, try Hover/Longshot without lifting stone; compare Lens off/on for chest path.
- Target: `remake/adult_ganons_castle.toml` — exits Ganons Castle Shadow Trial Second Gap -> Ending; remake.toml Golden Gauntlets Chest.
- Answer changes: Successful full bypass can relax strength/Lens only for that path.
- Source: `plans/rounds/r4-logic-adult:458-467; 509-515; 03-game-data section 13`.

### GA04 — Ganon Castle / Tower

- Age/progress: adult; All six trials accessible; Light Arrows; Gauntlets; before relevant puzzle solved. Session 15.
- Do/watch: On ordinary full equipment run, record required attacks/equipment through Ganondorf, collapse, Ganon phase before sword retrieval and final blow.
- Target: `remake/adult_ganons_castle.toml` — ganons_castle.toml goal Triforce / final combat rules.
- Answer changes: Check solver Light-Arrow-only abstraction against real mandatory combat; do not attempt a deliberately unwinnable main-save loadout.
- Source: `plans/rounds/r4-logic-adult:458-467; 509-515; 03-game-data section 13`.

### GA05 — Ganon Castle / Tower

- Age/progress: adult; All six trials accessible; Light Arrows; Gauntlets; before relevant puzzle solved. Session 15.
- Do/watch: Outside castle, before sage bridge appears if reachable, try reaching fairy path with Golden Gauntlets. What barrier still blocks it?
- Target: `remake/adult_ganons_castle.toml` — outside_ganons_castle.toml OGC Great Fairy Fountain exit.
- Answer changes: Add bridge/story barrier if gauntlets alone are insufficient; late successful visit does not settle pre-bridge access.
- Source: `plans/rounds/r4-logic-adult:458-467; 509-515; 03-game-data section 13`.

### GA06 — Ganon Castle / Tower

- Age/progress: adult; All six trials accessible; Light Arrows; Gauntlets; before relevant puzzle solved. Session 15.
- Do/watch: Inspect hidden fairy room: any Business Scrub? In Light trial, open Lullaby chest before spending the single key and record reward; inspect Spirit room for any second invisible chest.
- Target: `remake/adult_ganons_castle.toml` — Ganons Castle scrub exclusions; Light Trial Lullaby Chest; Spirit Trial Invisible Chest.
- Answer changes: Confirms old r2/r3 questions and one-key/absent-chest facts.
- Source: `plans/rounds/r4-logic-adult:458-467; 509-515; 03-game-data section 13`.

### MOD01 — Isolated mod checks

- Age/progress: child; adult only for upgrade order; Fresh throwaway user copy per variant; never main save. Session 16.
- Do/watch: In existing tower red-rupee variant, collect 20, trigger a save, leave and re-enter, then reload that same test user. Is rupee still gone?
- Target: `fact` — fact: heart-piece Hash 9814903750835309225 persistence.
- Answer changes: Confirms whether swapped pickup sets original permanent flag; missing Bool64 alone is not proof a chest reset.
- Source: `plans/rounds/r3-census:296-333; 03-game-data sections 10-11; decisions D16-D17`.

### MOD02 — Isolated mod checks

- Age/progress: child; adult only for upgrade order; Fresh throwaway user copy per variant; never main save. Session 16.
- Do/watch: In existing tower chest-Boomerang variant, open chest replacing heart piece, use Boomerang, save/reload and revisit. Does chest stay open and item stay owned?
- Target: `fact` — fact: chest fallback at Hash 9814903750835309225.
- Answer changes: Determines freestanding-major fallback; do not rerun Fire Arrows crash variant.
- Source: `plans/rounds/r3-census:296-333; 03-game-data sections 10-11; decisions D16-D17`.

### MOD03 — Isolated mod checks

- Age/progress: child; adult only for upgrade order; Fresh throwaway user copy per variant; never main save. Session 16.
- Do/watch: On separate adult test users, collect Longshot before Hookshot and inspect usable range after each. Also collect a higher bag/gauntlet tier before lower only if a reviewed variant exists.
- Target: `fact` — fact: D16 fixed-item downgrade/order.
- Answer changes: A downgrade requires generator/runtime policy review, not invented progressive behavior.
- Source: `plans/rounds/r3-census:296-333; 03-game-data sections 10-11; decisions D16-D17`.

### MOD04 — Isolated mod checks

- Age/progress: child; adult only for upgrade order; Fresh throwaway user copy per variant; never main save. Session 16.
- Do/watch: With a reviewed Treasure Chest Game reward swap, win the final room. Record visible preview, granted item/model/text and later repeat reward.
- Target: `fact` — fact: D17 reward DropViewActor compatibility.
- Answer changes: Reward may join shuffle only after preview/grant/persistence pass; eleven ordinary boxes stay vanilla.
- Source: `plans/rounds/r3-census:296-333; 03-game-data sections 10-11; decisions D16-D17`.

### MOD05 — Isolated mod checks

- Age/progress: child; adult only for upgrade order; Fresh throwaway user copy per variant; never main save. Session 16.
- Do/watch: On a corrected mini-seed with sword moved to Mido chest, get sword and shield, equip them and approach Mido. Does he admit Link without vanilla sword cutscene?
- Target: `fact` — fact: Get_StoneOfForest_GetSword removal and Mido inventory gate.
- Answer changes: Confirms ownership is sufficient; moved sword without gate success is not end-to-end proof.
- Source: `plans/rounds/r3-census:296-333; 03-game-data sections 10-11; decisions D16-D17`.

### MOD06 — Isolated mod checks

- Age/progress: child; adult only for upgrade order; Fresh throwaway user copy per variant; never main save. Session 16.
- Do/watch: On existing intro-removed test, start empty test user. Does forest load without movie and Navi wake correctly? On all-skip copy, finish Deku Tree and walk Field-to-Market-to-Zelda chain: any owl or blocked quest step?
- Target: `fact` — fact: fast-start intro removal; Step_Goto_HyruleCastle monotonicity.
- Answer changes: Checks only still-unplayed paths; intro-skippable and initial all-skip already passed.
- Source: `plans/rounds/r3-census:296-333; 03-game-data sections 10-11; decisions D16-D17`.

### MOD07 — Isolated mod checks

- Age/progress: child; adult only for upgrade order; Fresh throwaway user copy per variant; never main save. Session 16.
- Do/watch: Use Track B reviewed Kokiri shop-slot variant; buy substitute, inspect display/name/price/granted item, tutorial and stock after reload. Use separate chest-shield variant for inventory/Mido check.
- Target: `fact` — fact: Track B D19 shop tutorial / shield chest.
- Answer changes: Shop shuffle remains opt-in until in-game display/grant/stock pass; do not build a competing shop patch.
- Source: `plans/rounds/r3-census:296-333; 03-game-data sections 10-11; decisions D16-D17`.

### MOD08 — Isolated mod checks

- Age/progress: child; adult only for upgrade order; Fresh throwaway user copy per variant; never main save. Session 16.
- Do/watch: Use Track D reviewed Talon/NPC/fairy/song variants separately. Check overlay log, actual grant/model/text and repeat refusal after reload; for song also inspect whether vanilla melody is still learned.
- Target: `fact` — fact: Track D gift flags and duplicate song grant.
- Answer changes: Gift families join only after reviewed wrapper-specific check; use producer save/launcher, not a main-save overlay.
- Source: `plans/rounds/r3-census:296-333; 03-game-data sections 10-11; decisions D16-D17`.

### GIFT01 — Early gift identities

- Age/progress: child; After return to child; first reward not already collected. Session 2.
- Do/watch: At Market potion/bug shop, ask about the bottle tutorial and catch its bug if prompted. Does it give an empty bottle once? Record prerequisite and whether already owning a bottle changes it.
- Target: `fact` — fact: Npc_Hylia_020_Shop_Child Item_Bottle_TutorialEvent_Talk.
- Answer changes: Confirms remake-only gift and gate; guide fact already suggests bug tutorial, so no assumed free unconditional bottle.
- Source: `plans/rounds/r4-evfl:131-145; 03-game-data section 15; r4-logic-child:485-488`.

### GIFT02 — Early gift identities

- Age/progress: child; After return to child; first reward not already collected. Session 2.
- Do/watch: At Kokiri shop, speak before and after ordinary shield purchase without accepting a second purchase. Does shopkeeper ever give a free shield? Record story stage, rupees and ownership.
- Target: `fact` — fact: Npc_Kokiri_001_Shop_Child present_DekuSheld.
- Answer changes: Distinguishes tutorial/shop handover from independent gift; Track B owns tracing.
- Source: `plans/rounds/r4-evfl:131-145; 03-game-data section 15; r4-logic-child:485-488`.

### GIFT03 — Frogs

- Age/progress: child; After child return; known child songs and Storms. Session 6.
- Do/watch: At River frogs, try Storms for first reward, then the bug-eating game after teaching the required songs. Record each first Heart Piece and whether repeat games pay only rupees.
- Target: `fact` — fact: MiniGame_FrogTenors Event75/161/384 and ZR Frogs in the Rain.
- Answer changes: Separates bug game from Storms prize; prevents treating duplicate flow branches as separate checks.
- Source: `plans/rounds/r4-evfl:134-145; 03-game-data section 15`.

### PAIR01 — Paired upgrades

- Age/progress: child then adult; Both ages available; unbought upgrade pair on isolated copy. Session 10.
- Do/watch: Buy Kokiri/Lost Woods stick/nut upgrade as child, then visit same scrub as adult; reverse on a separate copy if possible. Does second age offer another one-time tier?
- Target: `fact` — fact: separate scrub age Hashes.
- Answer changes: Evidence for one-vs-two-check owner choice; record tier before/after and repeat price.
- Source: `plans/rounds/r2-census:295-300,325-328`.

### GROT01 — Remaining grotto identities

- Age/progress: adult; Hammer access for Crater/Goron grotto. Session 7.
- Do/watch: In Goron City and Crater hammer grottos inspect entire rooms, list chest positions/vanilla rewards and whether any scrub remains.
- Target: `fact` — fact: GC/DMC absent scrub checks and remake-only chests.
- Answer changes: Confirms exclusions and supplies distinct new chest rules; do not rename chest as a scrub.
- Source: `plans/rounds/r2-census:329-330; r3-world:184-185; r4-logic-child:835-837,903-905`.

### GROT02 — Lake grotto identity

- Age/progress: child; After child return; island grave. Session 5.
- Do/watch: Push island grave and inspect Lake grotto. Is there only red-rupee chest and no Business Scrub? Record entrance method and item.
- Target: `fact` — fact: LH grotto chest 6900843020594897860; absent scrub trio.
- Answer changes: Confirms relocation/exclusion; ranch trio is checked separately by LLR01.
- Source: `plans/rounds/r2-census:329-330; r3-world:184-185; r4-logic-child:1068-1099`.

### RES01 — Unverified resource sources

- Age/progress: adult then child on return; Observe only along current area route; do not grind drops. Session 1.
- Do/watch: Along first-adult forest/Kakariko/Market route, note claimed pots, crates, hearts and wonderitems that are actually missing or have different drops. Record area/landmark, age, tool and repeat after leaving.
- Target: `fact` — fact: first-adult area resource-source audit.
- Answer changes: Correct named resource rule only when tied to a real location; one empty random drop is inconclusive.
- Source: `plans/rounds/r4-logic-adult:162-179 unresolved matrix; r4-logic-child per-area low-priority notes`.

### RES02 — Child forest/Field/Ranch/Market

- Age/progress: age of this session; Observe on planned route only. Session 2.
- Do/watch: On this route, note any old pot/crate/heart/wonderitem source that is absent or has a different drop. Record room/landmark, age, tool, item and whether it respawns; skip already-collected sources.
- Target: `fact` — fact: Child forest/Field/Ranch/Market resource-source audit.
- Answer changes: Resolve the named inherited resource check only after stable identity; guide silence and a single empty random drop do not prove absence.
- Source: `plans/rounds/r4-logic-child per-area low-priority notes; r4-logic-adult area unresolved resource notes`.

### RES03 — Child Kakariko/Graveyard

- Age/progress: age of this session; Observe on planned route only. Session 3.
- Do/watch: On this route, note any old pot/crate/heart/wonderitem source that is absent or has a different drop. Record room/landmark, age, tool, item and whether it respawns; skip already-collected sources.
- Target: `fact` — fact: Child Kakariko/Graveyard resource-source audit.
- Answer changes: Resolve the named inherited resource check only after stable identity; guide silence and a single empty random drop do not prove absence.
- Source: `plans/rounds/r4-logic-child per-area low-priority notes; r4-logic-adult area unresolved resource notes`.

### RES04 — Child mountains/Dodongo

- Age/progress: age of this session; Observe on planned route only. Session 4.
- Do/watch: On this route, note any old pot/crate/heart/wonderitem source that is absent or has a different drop. Record room/landmark, age, tool, item and whether it respawns; skip already-collected sources.
- Target: `fact` — fact: Child mountains/Dodongo resource-source audit.
- Answer changes: Resolve the named inherited resource check only after stable identity; guide silence and a single empty random drop do not prove absence.
- Source: `plans/rounds/r4-logic-child per-area low-priority notes; r4-logic-adult area unresolved resource notes`.

### RES05 — Child Zora/Jabu/Lake

- Age/progress: age of this session; Observe on planned route only. Session 5.
- Do/watch: On this route, note any old pot/crate/heart/wonderitem source that is absent or has a different drop. Record room/landmark, age, tool, item and whether it respawns; skip already-collected sources.
- Target: `fact` — fact: Child Zora/Jabu/Lake resource-source audit.
- Answer changes: Resolve the named inherited resource check only after stable identity; guide silence and a single empty random drop do not prove absence.
- Source: `plans/rounds/r4-logic-child per-area low-priority notes; r4-logic-adult area unresolved resource notes`.

### RES06 — Well and storms grottos

- Age/progress: age of this session; Observe on planned route only. Session 6.
- Do/watch: On this route, note any old pot/crate/heart/wonderitem source that is absent or has a different drop. Record room/landmark, age, tool, item and whether it respawns; skip already-collected sources.
- Target: `fact` — fact: Well and storms grottos resource-source audit.
- Answer changes: Resolve the named inherited resource check only after stable identity; guide silence and a single empty random drop do not prove absence.
- Source: `plans/rounds/r4-logic-child per-area low-priority notes; r4-logic-adult area unresolved resource notes`.

### RES07 — Adult mountains/Fire

- Age/progress: age of this session; Observe on planned route only. Session 7.
- Do/watch: On this route, note any old pot/crate/heart/wonderitem source that is absent or has a different drop. Record room/landmark, age, tool, item and whether it respawns; skip already-collected sources.
- Target: `fact` — fact: Adult mountains/Fire resource-source audit.
- Answer changes: Resolve the named inherited resource check only after stable identity; guide silence and a single empty random drop do not prove absence.
- Source: `plans/rounds/r4-logic-child per-area low-priority notes; r4-logic-adult area unresolved resource notes`.

### RES08 — Ice/Water/Zora/Lake

- Age/progress: age of this session; Observe on planned route only. Session 9.
- Do/watch: On this route, note any old pot/crate/heart/wonderitem source that is absent or has a different drop. Record room/landmark, age, tool, item and whether it respawns; skip already-collected sources.
- Target: `fact` — fact: Ice/Water/Zora/Lake resource-source audit.
- Answer changes: Resolve the named inherited resource check only after stable identity; guide silence and a single empty random drop do not prove absence.
- Source: `plans/rounds/r4-logic-child per-area low-priority notes; r4-logic-adult area unresolved resource notes`.

### RES09 — Gerudo/Training Ground/desert

- Age/progress: age of this session; Observe on planned route only. Session 10.
- Do/watch: On this route, note any old pot/crate/heart/wonderitem source that is absent or has a different drop. Record room/landmark, age, tool, item and whether it respawns; skip already-collected sources.
- Target: `fact` — fact: Gerudo/Training Ground/desert resource-source audit.
- Answer changes: Resolve the named inherited resource check only after stable identity; guide silence and a single empty random drop do not prove absence.
- Source: `plans/rounds/r4-logic-child per-area low-priority notes; r4-logic-adult area unresolved resource notes`.

### RES10 — Spirit Temple

- Age/progress: age of this session; Observe on planned route only. Session 13.
- Do/watch: On this route, note any old pot/crate/heart/wonderitem source that is absent or has a different drop. Record room/landmark, age, tool, item and whether it respawns; skip already-collected sources.
- Target: `fact` — fact: Spirit Temple resource-source audit.
- Answer changes: Resolve the named inherited resource check only after stable identity; guide silence and a single empty random drop do not prove absence.
- Source: `plans/rounds/r4-logic-child per-area low-priority notes; r4-logic-adult area unresolved resource notes`.

### RES11 — Shadow Temple

- Age/progress: age of this session; Observe on planned route only. Session 14.
- Do/watch: On this route, note any old pot/crate/heart/wonderitem source that is absent or has a different drop. Record room/landmark, age, tool, item and whether it respawns; skip already-collected sources.
- Target: `fact` — fact: Shadow Temple resource-source audit.
- Answer changes: Resolve the named inherited resource check only after stable identity; guide silence and a single empty random drop do not prove absence.
- Source: `plans/rounds/r4-logic-child per-area low-priority notes; r4-logic-adult area unresolved resource notes`.

### RES12 — Castle/Tower

- Age/progress: age of this session; Observe on planned route only. Session 15.
- Do/watch: On this route, note any old pot/crate/heart/wonderitem source that is absent or has a different drop. Record room/landmark, age, tool, item and whether it respawns; skip already-collected sources.
- Target: `fact` — fact: Castle/Tower resource-source audit.
- Answer changes: Resolve the named inherited resource check only after stable identity; guide silence and a single empty random drop do not prove absence.
- Source: `plans/rounds/r4-logic-child per-area low-priority notes; r4-logic-adult area unresolved resource notes`.

### FT08 — Forest default chest

- Age/progress: adult; Forest basement; vanilla chest content not already shuffled. Session 1.
- Do/watch: On vanilla copy open the plain basement chest with no specified drop. Does it give a green rupee? Record which physical chest.
- Target: `fact` — fact: ForestTemple chest Hash 15117164073907033527 default drop.
- Answer changes: Confirms default-green inference; a shuffled chest says nothing about actor default.
- Source: `plans/rounds/r1-research:63-64; 03-game-data section 2`.

## Pending-answer rule targets

- **HF01**: `remake/child_hyrule_field.toml` — remake.toml locations HF Ocarina of Time Item; translated Song from Ocarina of Time. Failure adds a scale gate to both linked gifts; success keeps scaleless route. Source: `r4-logic-child:350-366`.
- **FA01**: `remake.toml` — locations HC Great Fairy Reward. Confirms the Din Fire possession gate, not a first-fairy visit condition. Source: `r4-logic-child:1424-1427; 03-game-data section 12`.
- **TT01**: `remake/child_temple_of_time.toml` — exits Temple of Time -> Beyond Door of Time. Opening drops Ocarina tier 2; scene dependence requires a story-event gate. No verified tier-removal mod is supplied here. Source: `r4-logic-child:563-574; r4-logic-adult:206-211`.
- **TT02**: `remake/child_temple_of_time.toml` — fact: age-travel return gate; Track A search chronology. Sets temporal gate/unlock event, not a gate on first adult access. Source: `r4-logic-child:563-574; r4-logic-adult:206-211`.
- **DMT03**: `remake/child_death_mountain_trail.toml` — exits Death Mountain Summit -> DMT Owl Flight; fact IsGet.Item_DinFire. Confirms possession vs fountain-visit gate; compare variants on separate save copies. Source: `r4-logic-child:761-775`.
- **ZD02**: `remake/child_zoras_domain.toml` — fact: repeat diving reward. A new one-time prize needs gift/census entry; repeat money alone is not a new check. Source: `r4-logic-child:994-1000`.
- **JJ02**: `remake/child_jabu_jabus_belly.toml` — translated jabu_jabus_belly.toml locations Jabu Jabus Belly Deku Scrub. Add scale if ordinary child dive cannot reach it. Source: `r4-logic-child:1215-1228`.
- **JJ03**: `remake/child_jabu_jabus_belly.toml` — translated jabu_jabus_belly.toml exits Jabu Jabus Belly Beginning -> Jabu Jabus Belly Main. Keep only demonstrated explosives branches of projectile access. Source: `r4-logic-child:1215-1228`.
- **FA02**: `remake.toml` — fact: DMT fairy fee and retry. Confirms fixed 25-rupee fee and repeat offer after refusal; no fee-order rule. Source: `r4-logic-child:1424-1427; 03-game-data section 12`.

## Deduplication and closed historical questions

- Child area numbered open lists (`r4-logic-child.md:64-73,165-1343`) map in order to DT, KF, LW, SFM, HF, LLR,
  MK, FA/HC, TT, KAK, GY, DMT, GC, ZR, ZD, LH, DC, JJ, W and IC. Its final ten-question summary repeats these;
  Kakariko question 4 is HF02, not another test. Crater/Fountain child sections explicitly have no separate rule questions.
- Adult bold area paragraphs and unresolved overworld matrix map to FT, AO, FI, ZA, WA, GE, GT, HW, CO, SP, SH,
  EN and GA. RES01-RES12 retain the broad unverified pots/drops categories as optional observations, not invented gates.
- `r2-census` / `r3-world` missing grotto scrubs: SFM02, ZR03, LLR01, GROT01/02, GE02/03, CO03, GA06.
  LLR and Lake are distinct: the three-scrub hole is in the ranch, not Lake. DMT grotto chest and tomb absence use GY03
  and route resource notes; dungeon exclusions are not restored from an unlocated memory.
- `r3-world` Forest east-garden alternative = FT03; rotating-skull question = SH07. Fire Map/Compass dispute = FI06.
- `r4-evfl` Market bottle/Kokiri shield/frogs = GIFT01/02/03; gift-swap proof = MOD08. `03-game-data` child lab-dive
  ambiguity = ZA07. Multiple grant steps are not automatically independent checks.
- `r2-census` separate age/state Hashes = GE08 and PAIR01; **Kareem/co-owner still decide one check vs two**.
  Their observation does not authorize a pool/settings change.
- `r1-research` product questions are decided by D10-D14: traps out, cows out, extra chests/Business Seeds in,
  DreamWorld out, no size-matches-item feature, no exefs. Not player errands. Fairy identity was confirmed by Kareem
  (`03-game-data` sections 9-10); old HC/DMT visit-order and rising-fee assumptions are superseded by section 12's flows.
- Round 1/2 small↔big chest grant, removal of sword story override, freestanding shield appearance/pickup, and round 4
  intro-skippable/initial all-skip are already tested (`03-game-data` sections 10,11,14). Do not replay them. Still-open
  pickup persistence/chest fallback, moved-sword Mido admission and later quest-chain behavior are MOD01/02/05/06.
- Fire Arrows pickup crashed three times (`03-game-data` section 10): **no crash rerun is scheduled**. An upstream
  cause-specific fix and reviewer instruction are prerequisites, not another variant in a player sitting.
- `r2-census:464` backup-before-pickup question is resolved for the archived tower copy: all six slots inspected here
  have Hash 9814903750835309225 unset. Chest Hash absence is NOT an unopened-chest oracle (`r2-census:466-470`).
- D16 downgrade = MOD03; D17 reward-preview swap = MOD04. Track E prepared isolated upgrade-order and red-rupee
  reward-preview variants (`prepared-mods.md`); both await reviewer approval, matching milestone saves and gameplay.
- Fast-start policy questions (`r4-fast-start:142-151`): D18 settles intro-skippable default and separate Saria/Mido/
  Tree/owl toggles. **Courtyard skip, Navi-wake policy, tying Mido skip to forest exit, and removing the movie entirely
  remain owner choices**, not logic-session questions. MOD06 tests the existing removal experiment only.
- `r3-seed:200-201` remake-vs-N64 pool remains a product question for reviewer/owners; implementation currently uses
  remake chest contents. No in-game experiment can decide their desired pool.
- Old loader/count assertions, root ownership collisions and shared night compiler semantics are engineering review,
  not questions for a player. Round 4 integration resolved phantom keys/ninth GTG key/root Lens rule; do not ask Kareem
  to diagnose a previously fixed synthetic-test failure.

## Evidence sources

Primary question provenance is the cited local round file plus `plans/03-game-data.md` sections 2,6,10-15 and
`plans/decisions.md`. Those documents retain their guide URLs. No guide text was copied or newly relied on here.
For factual guide context only: https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake
and https://www.eurogamer.net/all-new-changes-zelda-ocarina-of-time-switch-2 .
