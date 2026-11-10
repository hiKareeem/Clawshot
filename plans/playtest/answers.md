# Answers — Claude fills after play

One row per question ID in [questions.md](questions.md), plus direct-play observations identified below.
Replace `—` with age, inventory/story stage, exact result, room/standing point and save/log reference where relevant.
Use `confirmed`, `inconclusive`, `already collected`, or `needs preserved copy/tool`; never turn one failed attempt into impossibility.
Then apply the register's rule/fact consequence in the owning track, recording Kareem/build/date. Product calls still need owner approval.

Rows still marked **asked 2026-11-08, answer pending** are absent from every session; do not ask again.
A dash in Session means already asked or supplied directly, not forgotten. Mod checks require overlay log AND observed result.
Track C followup adds XC01–XC20 in [excluded-chests.md](excluded-chests.md); LW05→XC19 and GE01→XC04 are aliases.
Round 6 adds direct observation R6F-GOHMA (not a scheduled register question). Partial answers retain their untested parts.


| ID | Session | Check | Status | Observed answer / evidence |
|---|---|---|---|---|
| HF01 | — | After Zelda throws the Ocarina into the moat, collect it without a Scale | confirmed | Kareem in game via Claude, 2026-11-08: the moat is shallow and needs no Silver Scale. Both HF moat checks keep `is_child and has_all_stones`; no scale gate. Section 12 and `r6-play.md` item 2; no new agent game run or invented log evidence. |
| FA01 | — | Before obtaining Din Fire, play Lullaby at the Hyrule Castle fountain | asked 2026-11-08, answer pending | — |
| TT01 | — | With only Fairy Ocarina, three stones and Song of Time, play at the altar | asked 2026-11-08, answer pending | — |
| TT02 | — | Immediately after the first sword pull, try putting it back | asked 2026-11-08, answer pending | — |
| DMT03 | — | At the summit, speak to the owl before Din Fire | confirmed | Child, test `r5-gifts/ingame/din-fairy-hookshot` (Kareem, 2026-11-08, Hookshot release build): the owl refused before the fairy, and still refused after she gave the Hookshot instead of Din's Fire. The owl needs Din's Fire itself (`IsGet.Item_DinFire`, flow `Npc_Kaepora_DeathMountainTrail`); `child_death_mountain_trail.toml`'s `is_child and Dins_Fire` stands. |
| ZD02 | — | After the first Silver Scale, win the second diving round | asked 2026-11-08, answer pending | — |
| JJ02 | — | Without a Scale, dive through the elevator-room underwater passage to the scrub | asked 2026-11-08, answer pending | — |
| JJ03 | — | In the entrance mouth, try Bombs then Bombchus on the ceiling tonsil; do not use Slingshot | asked 2026-11-08, answer pending | — |
| FA02 | — | At the summit fountain with fewer than 25 rupees, ask for the gift, leave and play… | asked 2026-11-08, answer pending | — |
| AO01 | [ 1 ](session-1.md) | In Kakariko windmill, try reaching the Heart Piece by a normal jump, without Song of… | not yet played | — |
| AO02 | [ 1 ](session-1.md) | Race Dampe twice on an unmodified copy | not yet played | — |
| AO03 | [ 1 ](session-1.md) | Check an ordinary grave by day and night as adult | not yet played | — |
| AO08 | [ 1 ](session-1.md) | Check adult Ranch tree by day, then play the Ingo race/obstacle course normally | not yet played | — |
| AO05 | [ 1 ](session-1.md) | In adult Kokiri, try ordinary jumps to bean-platform rupees and inspect Baba nut/stick… | not yet played | — |
| AO06 | [ 1 ](session-1.md) | In Lost Woods try the river shortcut using ordinary dive/Scale; at the bridge note a… | not yet played | — |
| AO04 | [ 1 ](session-1.md) | In Sacred Forest Meadow by day, is its adult token present? Try the normal flower/maze… | not yet played | — |
| FT07 | [ 1 ](session-1.md) | Before taking the entrance-tree key, inspect the front lock | not yet played | — |
| FT01 | [ 1 ](session-1.md) | In the first entrance room, try taking the token without Hookshot: kill with Bow/Bombs… | not yet played | — |
| FT02 | [ 1 ](session-1.md) | In the west garden, aim ordinary Hookshot from the lower floor at the token | not yet played | — |
| FT03 | [ 1 ](session-1.md) | At the east garden token ledge, try the upper falling-room route without summoning… | not yet played | — |
| FT04 | [ 1 ](session-1.md) | At each iced eye (upper hall and rotating basement), try Din Fire without firing an arrow | not yet played | — |
| FT05 | [ 1 ](session-1.md) | At the basement token, try walking/jumping to take it before grappling. | not yet played | — |
| FT08 | [1](session-1.md) | Forest falling-ceiling chest Hash 15117164073907033527: green rupee or Bombs? | not yet played | — |
| FT06 | [ 1 ](session-1.md) | In Phantom Ganon phase one, hit the real rider with ordinary Hookshot instead of Bow | not yet played | — |
| RES01 | [ 1 ](session-1.md) | Along first-adult forest/Kakariko/Market route, note claimed pots, crates, hearts and… | not yet played | — |
| LLR01 | [ 2 ](session-2.md) | Step on the stone circle by the south fence without Bombs | not yet played | — |
| LLR02 | [2](session-2.md) | Tower-vine token night/range; high chest is XC14 | not yet played | — |
| HF05 | [ 2 ](session-2.md) | By day, roll into the lone tree between the forest exit and ranch | not yet played | — |
| LW03 | [ 2 ](session-2.md) | At the bridge Business Scrub, use sword, Slingshot and nuts separately, never a… | not yet played | — |
| LW05 | — | Lost Woods elevated chest; same question as XC19 | alias → XC19; answer once | — |
| LW02 | [ 2 ](session-2.md) | Drop through the Deku Theater hole | not yet played | — |
| LW04 | [ 2 ](session-2.md) | Cut above-ground bushes in the woods; bottle any bug | not yet played | — |
| GIFT02 | [ 2 ](session-2.md) | Does the Kokiri shopkeeper give a free shield? | confirmed | Kareem via Claude, 2026-11-08, `seed-shop-7`, Hookshot 2.0.1: child with Kokiri Sword/Hylian Shield, no Deku Shield, after Mido; free Deku Shield, while shelf still sold one at 40. Data: early quest window and not-equipped Deku test; both first/repeat dialogue paths grant. New child-shop event models early access, not a shuffled check. Repeat/cutoff play confirmation remains open (`r6-play.md` item 3, section 12). |
| GIFT01 | [ 2 ](session-2.md) | At Market potion/bug shop, ask about the bottle tutorial and catch its bug if prompted | not yet played | — |
| MK01 | [ 2 ](session-2.md) | By day, find Richard and lead him to his owner | not yet played | — |
| MK03 | [ 2 ](session-2.md) | Check the Bombchu Shop door between 18:00 and 21:00, then just after 21:00 | not yet played | — |
| RES02 | [ 2 ](session-2.md) | On this route, note any old pot/crate/heart/wonderitem source that is absent or has a… | not yet played | — |
| KAK01 | [ 3 ](session-3.md) | By day, roll into the narrow tree near the village entrance | not yet played | — |
| KAK03 | [ 3 ](session-3.md) | Try the ladders beside Impa and a cucco glide to the cow-shed/Impa roof | not yet played | — |
| KAK02 | [ 3 ](session-3.md) | As child on the windmill floor, throw Boomerang at the beam Heart Piece | not yet played | — |
| KAK04 | [ 3 ](session-3.md) | At night, are the cuccos at the fence and windmill hill present? If so, can child… | not yet played | — |
| GY02 | [ 3 ](session-3.md) | Before touching Sharp/Flat graves, play Lullaby on the Royal Tomb Triforce | not yet played | — |
| GY01 | [ 3 ](session-3.md) | At the shield grave chest, try opening while the ReDead lives, without… | not yet played | — |
| GY03 | [ 3 ](session-3.md) | In the Royal Tomb, clear Keese, inspect for torches/chest, and cast Din Fire when… | not yet played | — |
| RES03 | [ 3 ](session-3.md) | On this route, note any old pot/crate/heart/wonderitem source that is absent or has a… | not yet played | — |
| DMT05 | [ 4 ](session-4.md) | Before breaking the cavern boulder, release bugs into its soil | not yet played | — |
| DMT01 | [ 4 ](session-4.md) | With no bracelet, try carried Bombs and Bombchus on the cavern boulder and fenced flower | not yet played | — |
| DMT04 | [ 4 ](session-4.md) | From the bomb-flower ledge, try the child backflip over the low fence onto the trail… | not yet played | — |
| GC01 | [ 4 ](session-4.md) | Bomb through the upper west maze | not yet played | — |
| GC03 | [ 4 ](session-4.md) | With bracelet only, carry a bomb flower to the bottom shop wall | not yet played | — |
| GC02 | [ 4 ](session-4.md) | With bracelet but no Bomb Bag, light the four torches using a stick; throw… | not yet played | — |
| DMT02 | [ 4 ](session-4.md) | With Bombs but no Slingshot/Boomerang, climb the spider wall below the owl | not yet played | — |
| DC06 | [ 4 ](session-4.md) | As child with only Slingshot for damage, fight each Lizalfos pair without sword,… | not yet played | — |
| DC07 | [ 4 ](session-4.md) | At the staircase bomb-flower chain, try a carried Bomb, then Din Fire on a separate… | not yet played | — |
| DC03 | [ 4 ](session-4.md) | At the mesh above the stairs, try sword/climb collection with no ranged tool | not yet played | — |
| DC02 | [ 4 ](session-4.md) | From the Armos/blade room upper south walkway, try walking round to the skull bridge… | not yet played | — |
| DC01 | [ 4 ](session-4.md) | From the main hall upper lift landing, bomb the wall beside the Bomb Bag ledge | not yet played | — |
| DC04 | [ 4 ](session-4.md) | As adult, Hammer the cracked wall off the skull bridge hiding the token | not yet played | — |
| DC05 | [ 4 ](session-4.md) | As adult in the blade room, try Hover Boots and Longshot separately to reach the Bomb… | not yet played | — |
| RES04 | [ 4 ](session-4.md) | On this route, note any old pot/crate/heart/wonderitem source that is absent or has a… | not yet played | — |
| HC01 | [ 5 ](session-5.md) | Talk to King Zora, try the diving game and letter route before visiting Impa again | not yet played | — |
| ZR01 | [ 5 ](session-5.md) | Take the bean-seller cucco to the vine ledge, enter its hole and use the second cucco… | not yet played | — |
| ZR02 | [ 5 ](session-5.md) | At night below Domain entrance, try sword/sticks on the ivy Gold Skulltula and climb… | not yet played | — |
| ZD01 | [ 5 ](session-5.md) | With Din Fire and no sticks used, light all timed torches along the king stairs,… | not yet played | — |
| JJ01 | [ 5 ](session-5.md) | Before killing tentacles, inspect the basement west ledge by Big Octo door | not yet played | — |
| JJ05 | [ 5 ](session-5.md) | In the map/water-switch room, press the switch before killing Stingers | not yet played | — |
| JJ04 | [ 5 ](session-5.md) | Before Big Octo, can you reach the two wooden crates in the upper switch room toward… | not yet played | — |
| GROT02 | [ 5 ](session-5.md) | Push island grave and inspect Lake grotto | not yet played | — |
| LH01 | [ 5 ](session-5.md) | By day, swim to the southwest ledge and crawl to the old Small Island token tunnel | not yet played | — |
| MK02 | [ 5 ](session-5.md) | After Dodongo, with no Bomb Bag and no Bombchus ever obtained, ask to bowl | not yet played | — |
| RES05 | [ 5 ](session-5.md) | On this route, note any old pot/crate/heart/wonderitem source that is absent or has a… | not yet played | — |
| HF02 | [ 6 ](session-6.md) | At the leafy cover west of the drawbridge, try Bombs then Storms | not yet played | — |
| HF04 | [ 6 ](session-6.md) | Bomb open the wetlands hole north of Lake Hylia and the eastern hole near Zora River | not yet played | — |
| HF03 | [ 6 ](session-6.md) | In the cow grotto near Gerudo Valley, try sword, unlit stick, Slingshot and Bombs on… | not yet played | — |
| KF03 | [ 6 ](session-6.md) | On the path past Mido, strike a Deku Baba head as child | not yet played | — |
| KF01 | [ 6 ](session-6.md) | At the cover up the ivy by Mido, play Storms | not yet played | — |
| KF02 | [ 6 ](session-6.md) | In that grotto, cut every grass patch | not yet played | — |
| SFM01 | [ 6 ](session-6.md) | At the round cover just before the Wolfos gate, try a bomb first, then Storms | not yet played | — |
| SFM03 | [ 6 ](session-6.md) | Against the gate Wolfos and the grotto pair, try Slingshot-only and stick-only fights… | not yet played | — |
| SFM02 | [ 6 ](session-6.md) | At the cover by Saria, try a bomb, Storms and Song of Time separately | not yet played | — |
| ZR03 | [ 6 ](session-6.md) | Open the storms hole near the bean seller; inspect its whole room | not yet played | — |
| GIFT03 | [ 6 ](session-6.md) | At River frogs, try Storms for first reward, then the bug-eating game after teaching… | not yet played | — |
| W02 | [ 6 ](session-6.md) | Without explosives, inspect/open the north-west fake-wall and front-centre B1 chests | not yet played | — |
| W03 | [6](session-6.md) | East ladder chest before Lullaby: submerged? Old west pit/Like Like room empty? | not yet played | — |
| W01 | [ 6 ](session-6.md) | In coffin hall, pull the far-west slab without using sticks/Din Fire | not yet played | — |
| W04 | [ 6 ](session-6.md) | Behind the west locked door, try collecting its token with Boomerang and no lit… | not yet played | — |
| W05 | [ 6 ](session-6.md) | With Lens switched off throughout, find east key niche, Compass room and central rooms… | not yet played | — |
| RES06 | [ 6 ](session-6.md) | On this route, note any old pot/crate/heart/wonderitem source that is absent or has a… | not yet played | — |
| AO07 | [ 7 ](session-7.md) | In Goron City try stopping the rolling Goron using Bow alone before bombs/flowers; try… | not yet played | — |
| GROT01 | [7](session-7.md) | City/Crater scrub absence and Crater chest; City sign chests are XC07/08 | not yet played | — |
| FI04 | [ 7 ](session-7.md) | In the crater from summit, test the short adult wall-heart visit without Tunic | not yet played | — |
| FI05 | [ 7 ](session-7.md) | With adult Hover/Longshot, try summit/crater ledges and volcano Heart Piece without… | not yet played | — |
| FI01 | [ 7 ](session-7.md) | Count acquired and spent keys at lava bridge (1), east/elevator pair (3 total), narrow… | not yet played | — |
| FI06 | [ 7 ](session-7.md) | Confirm the early lower-maze chest gives Map and the narrow-eye chest gives Compass on… | not yet played | — |
| FI03 | [ 7 ](session-7.md) | At first Flare Dancer, try ordinary Hookshot to expose its core without Bombs. | not yet played | — |
| FI02 | [ 7 ](session-7.md) | Before lowering the pillar, try Hover Boots from the near-boss side to the boss approach | not yet played | — |
| RES07 | [ 7 ](session-7.md) | On this route, note any old pot/crate/heart/wonderitem source that is absent or has a… | not yet played | — |
| ZA08 | [ 8 ](session-8.md) | At adult River entrance try passing boulders without Bombs; compare ordinary Hookshot… | not yet played | — |
| ZA02 | [ 8 ](session-8.md) | By day at frozen waterfall, inspect its token and try Bow/other ranged damage followed… | not yet played | — |
| ZA01 | [ 8 ](session-8.md) | After thawing King Zora but before Morpha, try entering the shop and direct… | not yet played | — |
| IC02 | [ 8 ](session-8.md) | Along the Compass/nearby token path, break blocking ice pillars using Master Sword,… | not yet played | — |
| IC03 | [ 8 ](session-8.md) | Inspect every main-path ice/arrow target | not yet played | — |
| IC01 | [ 8 ](session-8.md) | Past the Boots room, try the pool backdoor without Boots (record Scale) | not yet played | — |
| ZA03 | [ 8 ](session-8.md) | At Fountain hidden cave after lifting silver rocks, traverse and fight invisible… | not yet played | — |
| ZA07 | [ 8 ](session-8.md) | At fishing pond, record age, measured fish length, lure and first/repeat prizes | not yet played | — |
| ZA06 | [ 8 ](session-8.md) | In lake lab, try breaking/collecting the underwater token crate with Boots alone, then… | not yet played | — |
| ZA05 | [ 8 ](session-8.md) | Try Water entrance without Iron Boots using Golden Scale/Longshot | not yet played | — |
| ZA04 | [ 8 ](session-8.md) | At low-water lake before Morpha, shoot dawn sun and try collecting Fire Arrows via Pierre | not yet played | — |
| WA01 | [ 9 ](session-9.md) | Log each spent lock in order: pillar, middle-west water raise, high-west falling… | not yet played | — |
| WA02 | [ 9 ](session-9.md) | In Ruto cracked-wall room, after blasting wall, try taking its token by hand without… | not yet played | — |
| WA04 | [ 9 ](session-9.md) | At middle-water north target and north Boss Key block route, try Hover Boots without… | not yet played | — |
| WA03 | [ 9 ](session-9.md) | At river and waterfall tokens, try ordinary Hookshot from reachable ground before Longshot | not yet played | — |
| RES08 | [ 9 ](session-9.md) | On this route, note any old pot/crate/heart/wonderitem source that is absent or has a… | not yet played | — |
| AO09 | [ 10 ](session-10.md) | Test Lost Woods bridge Hover and Longshot routes separately, then one timed… | not yet played | — |
| AO10 | [ 10 ](session-10.md) | At the old Field cow/bomb holes, test Hammer as adult without Bombs | not yet played | — |
| HF06 | [ 10 ](session-10.md) | Read the Fairy Note by the Gerudo-side heart-piece scrub as adult | not yet played | — |
| PAIR01 | [ 10 ](session-10.md) | Buy Kokiri/Lost Woods stick/nut upgrade as child, then visit same scrub as adult;… | not yet played | — |
| GE08 | [ 10 ](session-10.md) | Open Valley Lens chest before age change, then compare opposite-age chest; compare… | not yet played | — |
| GE01 | — | Valley underwater Seed chest; same question as XC04 | alias → XC04; answer once | — |
| GE02 | [ 10 ](session-10.md) | Map Valley/fortress grottos: describe each chest position, vanilla content and opener;… | not yet played | — |
| GE07 | [ 10 ](session-10.md) | Inspect Valley cow crate/waterfall wonderitems and fortress signs/crates; break each… | not yet played | — |
| GE04 | [ 10 ](session-10.md) | On disposable copy, let a guard capture you once | not yet played | — |
| GE05 | [ 10 ](session-10.md) | Try direct roof jumps and Hover routes separately, without grapple | not yet played | — |
| GE03 | [ 10 ](session-10.md) | At fortress old storms hole, try simply dropping before playing Storms | not yet played | — |
| GE06 | [ 10 ](session-10.md) | At horseback archery try admission by day/night, before/after membership and on/off… | not yet played | — |
| AO11 | [ 10 ](session-10.md) | After earning Poe Collector bottle at five Poes, leave and revisit with another Poe | not yet played | — |
| RES09 | [ 10 ](session-10.md) | On this route, note any old pot/crate/heart/wonderitem source that is absent or has a… | not yet played | — |
| GT01 | [ 11 ](session-11.md) | Facing in from lobby entrance, inspect both chest sides before eye switch | not yet played | — |
| GT03 | [ 11 ](session-11.md) | At Wolfos silver-block invisible eye, try Hookshot instead of Bow with Lens on | not yet played | — |
| GT02 | [ 11 ](session-11.md) | In Like Like/heavy-block room record room-clear red chest, cracked-wall Bombs chest… | not yet played | — |
| GT04 | [ 11 ](session-11.md) | Try hot-room loop without Tunic; record hearts, burn ticks, time and whether… | not yet played | — |
| GT06 | [ 11 ](session-11.md) | From upper eye-statue doorway, try solving all eye targets without dropping to floor;… | not yet played | — |
| GT05 | [ 11 ](session-11.md) | Summon Pierre then try ordinary Hookshot from reachable floor/ledge, without Longshot. | not yet played | — |
| HW01 | [ 12 ](session-12.md) | On separate approaches, cross quicksand with Hover Boots only, then Longshot only | not yet played | — |
| HW03 | [ 12 ](session-12.md) | At desert salesman, record offered Bombchu count, price, wallet capacity needed and… | not yet played | — |
| HW02 | [ 12 ](session-12.md) | At ruin token, try ordinary Hookshot before Longshot; identify the surviving… | not yet played | — |
| HW04 | [ 12 ](session-12.md) | At ruin, light all three torches, open the chest and record actual item. | not yet played | — |
| CO03 | [ 12 ](session-12.md) | Lift grotto rock, inspect the purple chest and whole room; any scrubs? Record position… | not yet played | — |
| CO01 | [ 12 ](session-12.md) | At north-west cliff token, try ordinary Hookshot from every safe reachable standing… | not yet played | — |
| CO02 | [ 12 ](session-12.md) | Without planted bean, try Hover and Longshot separately to the bean-platform heart and… | not yet played | — |
| SP05 | [ 13 ](session-13.md) | As adult, try equipping/using Slingshot in the item menu and hitting an ordinary eye | not yet played | — |
| SP06 | [ 13 ](session-13.md) | In sun-block room, move cube into window light without lighting torches; does key… | not yet played | — |
| SP01 | [ 13 ](session-13.md) | After Lullaby spawns the hand key, try direct hand target/jump without summoning Pierre | not yet played | — |
| SP02 | [ 13 ](session-13.md) | Fight first invisible Floormaster with Lens off; can you finish and receive chest… | not yet played | — |
| SP04 | [ 13 ](session-13.md) | At Beamos/Anubis sequence, try Hammer without explosives; note each enemy/barrier it… | not yet played | — |
| SP03 | [ 13 ](session-13.md) | Try ordinary Hookshot at moving wall, Boss Key platform and final statue face… | not yet played | — |
| RES10 | [ 13 ](session-13.md) | On this route, note any old pot/crate/heart/wonderitem source that is absent or has a… | not yet played | — |
| SH01 | [ 14 ](session-14.md) | At high scythe-room silver rupee, try ordinary Hookshot target, then Longshot | not yet played | — |
| SH06 | [ 14 ](session-14.md) | With no bracelet/gauntlets, push falling-spikes cube and boat cube separately | not yet played | — |
| SH02 | [ 14 ](session-14.md) | At fan corridor try timed walking and Hookshot without Iron Boots; then Boots as control | not yet played | — |
| SH09 | [ 14 ](session-14.md) | Log five keys and their spent doors; confirm fifth opens spike-wall room, while boss… | not yet played | — |
| SH04 | [ 14 ](session-14.md) | Beyond boat, try Pierre/Hover/Longshot routes without Bomb Bag to bypass… | not yet played | — |
| SH03 | [ 14 ](session-14.md) | At invisible Floormaster, keep Lens off and finish fight | not yet played | — |
| SH07 | [ 14 ](session-14.md) | Beyond boat, Bomb each rotating skull; does the token emerge only after an explosion?… | not yet played | — |
| SH05 | [ 14 ](session-14.md) | In fifth-lock spike-wall room, use Fire Arrows without Din Fire | not yet played | — |
| SH08 | [ 14 ](session-14.md) | Check old loose-heart sites, especially the absent Time Block/scarecrow dead end;… | not yet played | — |
| RES11 | [ 14 ](session-14.md) | On this route, note any old pot/crate/heart/wonderitem source that is absent or has a… | not yet played | — |
| EN01 | [ 15 ](session-15.md) | Before Fire/Water/Forest are all complete, visit Kakariko after each sage if possible | not yet played | — |
| EN02 | [ 15 ](session-15.md) | If a reviewed seed naturally gives Shadow/Spirit before other sages, visit Temple… | not yet played | — |
| GA05 | [ 15 ](session-15.md) | Outside castle, before sage bridge appears if reachable, try reaching fairy path with… | not yet played | — |
| GA01 | [ 15 ](session-15.md) | In Forest wind trial, label five diamonds by physical position and collection order | not yet played | — |
| GA02 | [ 15 ](session-15.md) | At Spirit ceiling web, shoot ordinary arrow through lit candle | not yet played | — |
| GA03 | [ 15 ](session-15.md) | At Shadow final stone and invisible chest-switch route, try Hover/Longshot without… | not yet played | — |
| GA06 | [ 15 ](session-15.md) | Inspect hidden fairy room: any Business Scrub? In Light trial, open Lullaby chest… | not yet played | — |
| GA04 | [ 15 ](session-15.md) | On ordinary full equipment run, record required attacks/equipment through Ganondorf,… | not yet played | — |
| RES12 | [ 15 ](session-15.md) | On this route, note any old pot/crate/heart/wonderitem source that is absent or has a… | not yet played | — |
| MOD01 | [ 16 ](session-16.md) | In existing tower red-rupee variant, collect 20, trigger a save, leave and re-enter,… | not yet played | — |
| MOD02 | [ 16 ](session-16.md) | In existing tower chest-Boomerang variant, open chest replacing heart piece, use… | not yet played | — |
| MOD03 | [ 16 ](session-16.md) | On separate adult test users, collect Longshot before Hookshot and inspect usable… | not yet played | — |
| MOD04 | [ 16 ](session-16.md) | With a reviewed Treasure Chest Game reward swap, win the final room | not yet played | — |
| MOD05 | [ 16 ](session-16.md) | On a corrected mini-seed with sword moved to Mido chest, get sword and shield, equip… | not yet played | — |
| MOD06 | [ 16 ](session-16.md) | On existing intro-removed test, start empty test user | not yet played | — |
| MOD07 | [ 16 ](session-16.md) | Use Track B reviewed Kokiri shop-slot variant; buy substitute, inspect… | not yet played | — |
| MOD08 | [ 16 ](session-16.md) | Use Track D reviewed Talon/NPC/fairy/song variants separately | not yet played | — |
| DT01 | [ 17 ](session-17.md) | Leave the Slingshot room without Slingshot; separately test unarmed save/game-over recovery | confirmed (Boomerang); recovery pending | Kareem via Claude, 2026-11-08, `seed-shop-7`, Hookshot 2.0.1: Boomerang hits the exit switch. Rule adds Boomerang; room 2 eye Hash 9080063866993537303 / ladder 2096903280161003875 agree. This does not answer save/quit or game-over recovery without either ranged weapon. |
| DT02 | [ 17 ](session-17.md) | Clear the lobby vine wall with child Boomerang; later compare adult Bow/Hookshot | confirmed (child); adult pending | Kareem via Claude, 2026-11-08, `seed-shop-7`, Hookshot 2.0.1: Boomerang permits reaching 3F. `child_deku_tree.toml` accepts Slingshot or Boomerang; room 0 Skullwalltulas verified in both Banc files. Adult Bow/Hookshot not established by this observation. |
| LW01 | [ 17 ](session-17.md) | After Gohma but before Zelda, follow the correct maze path to the meadow | not yet played | — |
| XC01 | [6](session-6.md) | Well room-11 Seed chest: safe route round fake floor; Hash 6064359710907908886 | not yet played | — |
| XC02 | [10](session-10.md) | Fortress underground red chest entrance/route; Hash 16619432200060282313 | not yet played | — |
| XC03 | [10](session-10.md) | Valley adult invisible red chest entrance/appearance; Hash 18413589940135955604 | not yet played | — |
| XC04 | [10](session-10.md) | Valley underwater Seed chest replacement opener; Hash 6463521162691873710 | not yet played | — |
| XC05 | [10](session-10.md) | Valley green grotto chest independent appearance; Hash 17750686910716887133 | not yet played | — |
| XC06 | [10](session-10.md) | Valley child invisible red copy, age/repeat state; Hash 6205043616869463865 | not yet played | — |
| XC07 | [7](session-7.md) | City sign-puzzle green chest trigger/independence; Hash 9159710900681116662 | not yet played | — |
| XC08 | [7](session-7.md) | City sign-puzzle purple chest trigger/order; Hash 10944569637726152230 | not yet played | — |
| XC09 | [1](session-1.md) | Dampe red repeat chest time/previous rewards; Hash 234006393181394602 | not yet played | — |
| XC10 | [1](session-1.md) | Dampe blue repeat chest time/previous rewards; Hash 4322670163630771947 | not yet played | — |
| XC11 | [10](session-10.md) | Southern adult Field red chest spawn/route; Hash 1163740567397714729 | not yet played | — |
| XC12 | [10](session-10.md) | Northern adult Field red chest spawn/route; Hash 9891111455604007674 | not yet played | — |
| XC13 | [8](session-8.md) | Adult Lake red chest spawn/low-water route; Hash 17023457248274633121 | not yet played | — |
| XC14 | [2](session-2.md) | Ranch tower upper chest climb/appearance; Hash 17445672702269453589 | not yet played | — |
| XC15 | [5](session-5.md) | Lake grotto timed candles/red chest spawn; Hash 6900843020594897860 | not yet played | — |
| XC16 | [15](session-15.md) | Alternative adult windmill chest route/state-copy; Hash 13080955777249750889 | not yet played | — |
| XC17 | [1](session-1.md) | Normal adult windmill high chest route; Hash 11929552275106311978 | not yet played | — |
| XC18 | [2](session-2.md) | Kokiri elevated purple chest climb/spawn; Hash 4349272251343787229 | not yet played | — |
| XC19 | [2](session-2.md) | Lost Woods elevated purple chest climb/spawn; Hash 17479747339356189279 | not yet played | — |
| XC20 | [8](session-8.md) | Fountain upper ruins purple chest route/spawn; Hash 15055117029957340138 | not yet played | — |
| SHOP01 | later | With the Deku Shield in no shop, burn it then ask the shopkeeper after Mido | needs preserved copy/tool | GIFT02 confirms a first free grant without purchase, not a burned-shield replacement. Flow Event63's true branch still grants (Event116); equipped Deku Shield suppresses either grant. Repeat-after-burning and post-Gohma cutoff remain unplayed; do not mark those confirmed. |
| R6F-GOHMA | — | Does Boomerang stun Gohma? | confirmed | Kareem via Claude, 2026-11-08, `seed-shop-7`, Hookshot 2.0.1: yes. `Defeat Queen Gohma` adds Boomerang to stuns; retains jumpslash damage. Static boss Hash 15302759724049838417. Direct Round 6 Track F observation, not a new player errand. |
| R6-MINUET | — | Minuet of Forest and Fairy Ocarina from Mido's chests (`r6-settings/chest-ocarina-minuet`) | confirmed | Kareem via Claude, 2026-11-08, Hookshot 2.0.1: Ocarina get shows no model, correct text; Minuet shows the green rupee model, correct text; listed in the menu; warps to Sacred Forest Meadow. Log: no crash. |
| R6-CLOSEDDEKU | — | `closed_deku`: bridge exit open, Mido kept (`r6-settings/forest-closed-deku`) | confirmed | Kareem via Claude, 2026-11-08, Hookshot 2.0.1: the bridge Kokiri is moved; Link reached Hyrule Field; Saria's Fairy Ocarina cutscene played on the bridge before Gohma; Mido still blocks. |
| R6-PRICES | — | `cheap_deku_shield`/affordable Kokiri prices (`r6-settings/shop-prices-10`) | confirmed | Kareem via Claude, 2026-11-08, Hookshot 2.0.1: Deku Shield and Deku Nuts show 10; the shield bought for 10; after leaving and returning, the replacement shield and the sticks still show 10. |
| R6-GOSSIP | — | Custom Gossip Stone line without the Mask of Truth (`r6-hints/ingame/gossip-kf-line`) | confirmed | Kareem via Claude, 2026-11-08, Hookshot 2.0.1: the Kokiri Forest stone by the Lost Woods entrance said the "Clawshot test" line. |
| GF-SPIN | — | Spin Attack fairy before Din's Fire | confirmed: not allowed | Kareem via Claude, 2026-11-08, Hookshot 2.0.1, main save: the castle Great Fairy refused before Din's Fire, as the data says (section 13). |
| JB-TONSIL | — | Jabu-Jabu's first room: open the way with bombs? | confirmed: no | Kareem via Claude, 2026-11-08, main save, Hookshot 2.0.1: bombs do not hit the ceiling switch; the Slingshot or Boomerang is needed. Rule changed in `child_jabu_jabus_belly.toml`; Bombchus untested. |
| JB-TONSIL-2 | — | Jabu-Jabu's first room with explosives, retried | no (bombs) | Kareem via Claude, 2026-11-08, Hookshot 2.0.1: ten more bombs did not hit the switch; Bombchus not yet tried; Kareem asked speedrunners. Adult Link never reaches Jabu-Jabu (only the Deku Tree and Dodongo's Cavern of the child dungeons). |
| R7-SHOPKEEPER | — | Shopkeeper's gift as a once-only check (`r7-gifts/ingame/shopkeeper-boomerang`) | confirmed | Kareem via Claude, 2026-11-08, Hookshot 2.0.1: the Kokiri shopkeeper gave the Boomerang with the Deku Shield equipped; nothing on later talks. |
| R7-BOSSHEART | — | King Dodongo's Heart Container swapped (`r7-drops/ingame/dodongo-heart-hylian`) | confirmed | Kareem via Claude, 2026-11-08, Hookshot 2.0.1: a Hylian Shield where the Heart Container appears; no heart added; it did not come back. |
| R7-TOKEN | — | Native Gold Token with its pouch redirected to the Boomerang (`r7-drops/ingame/native-token-boomerang`) | no | Kareem via Claude, 2026-11-08, Hookshot 2.0.1: the Skulltula dropped a token, collected as a token and counted; no Boomerang. The pouch reference does not control the token grant; tokens stay unshuffled. |
| R7-TREASURE | — | Treasure Chest Game first prize as a red rupee (`r7-gifts/ingame/treasure-red`) | not tried | Kareem skipped it without the Lens of Truth. |
| R7-GETITEM | — | Gift items from chests with native models (`r7-getitem/ingame/chest-gift-models`) | partly | Kareem via Claude, 2026-11-08, Hookshot 2.0.1: Fairy Ocarina still shows no model; Song of Storms shows the ocarina stand-in; Din's Fire gives the magic meter and the spell works; Adult's Wallet holds 500. Ocarina of Time chest not reported. |
| R7-HINTS | — | Hints on Gossip Stones without the Mask of Truth (`r7-hints/seed-shop-7c`, Temple of Time courtyard) | works; colour bug | Kareem via Claude, 2026-11-08, Hookshot 2.0.1, screenshots: facing the temple, left to right, the stones are `GOSSIP_HYRULE_MARKET_01` to `04`; each speaks its hint without the mask and wraps cleanly. The highlight colour does not end after the first name: the rest of the line stays highlighted. |
| R7-BOMBBAG | — | Bombs from a shop bomb bundle in a chest, with no Bomb Bag before | bag shown, bombs unusable; cause traced, fix unplayed | Kareem via Claude, 2026-11-08, Hookshot 2.0.1, `seed-shop-7c`: Deku Tree basement `Buy Bombs (10)` gave a Bomb Bag and 20 bombs; bombs equip, briefly raise, then cancel. Read-only audit: both saves have the bag and capacity20; 7c `PlayerStatus.LiftGrade=None`, main `Low`. Native bomb hold requires Low; Goron's Bracelet grants it, the real bag only expands capacity. **[INFERENCE] KF Storms bag alone will not fix this; get Darunia's unshuffled Bracelet and retry.** In-game before/after confirmation pending, no save edit. Section30; `r7-play.md` item2. |
| R7-GRAVES | — | Child graveyard graves, seen from the Royal Family's Tomb | partly confirmed; other ordinals data-derived | Kareem via Claude, 2026-11-08, Hookshot 2.0.1: fourth from right (unmarked) has ReDead/chest; marked grave has cracked wall. At tomb entrance face outward: nearest seven-grave row, fourth right = shield, leftmost = heart chest; lower five-grave row, second right = marked fairy grave. Last two ordinals from placement, not new play. Wall leads to eight fairies, no check. Logic splits Fairy Grave from Shield Grave and needs explosives+bottle for Fairy; heart chest has no song/spawn trigger. Vanilla loaded during 17:38–17:42 overlay gap: not a shuffled-check acceptance. Section30; `r7-play.md` item1. |
| R7-BOMBCHUS | — | Bombchus without a Bomb Bag; pre-D25 7b/7c continuation | confirmed on main; GC8 route data-checked, unplayed | Kareem via Claude, 2026-11-08: used Bombchus on main without a bag. Native Item_Bombchu requires lift grade None. Written 7b GC Shop Item8 is native Shop_BombchuBundle_05 (five), repeatable sale; 7c's 228 placements match. Fixed-placement search wins with GC8 before Storms bag and stalls without GC8; child-only prefix gets Saria's Song/Darunia's Bracelet without adult items. Continue via GC8 chus and obtain Bracelet for ordinary bombs, not a forced restart. **GC8 purchase/use on 7c and bombs after Bracelet still need Kareem's check.** Section30; `r7-play.md` item2. |
| R7-SHIELD-DUPLICATE | — | Vanilla shield grave with Hylian Shield already held | confirmed observation, data explanation | Kareem via Claude, 2026-11-08: 20 rupees from the grave while vanilla files loaded. A_06 chest16912540161937823130 explicitly checks TBox_Shield_Hylian and substitutes TBox_Rupee_Red (20) when owned, in both ages. Not every duplicate item/chest has this rule. Shuffled writer already sets both branches to the assigned reward; real-placement in-memory smoke confirms it. No new shuffled in-game result claimed. Section30; `r7-play.md` item3. |
| R7-BRACELET | — | Bombs from the chest-granted bag, before and after Goron's Bracelet (`seed-shop-7c`) | confirmed | Kareem via Claude, 2026-11-09, Hookshot 2.0.1: with Darunia's Bracelet the bombs already in his inventory work (D30). |
| R8-GETITEM | — | Gift items in chests and ocarina hand props (`r8-getitem/ingame/chest-gifts-next`) | partly | Kareem via Claude, 2026-11-09, Hookshot 2.0.1, screenshot: the Fairy Ocarina (Mido far left) and the Ocarina of Time (Deku lobby map chest) still show no model; correct text, both work, songs play on the Ocarina of Time. Zelda's Letter, the Weird Egg and the Gerudo Membership Card show their models and text. The Weird Egg left the inventory once the Letter was taken (Kareem's inference: one shared child trade slot). Epona's Song shows the ocarina stand-in and plays. Save and Continue and the masks not reported. |
| R8-FREESTANDING | — | Lon Lon Ranch tower heart piece swapped for a Hylian Shield (`r8-freestanding-cs8e/ingame/llr-tower-hylian-next`) | confirmed | Kareem via Claude, 2026-11-09, Hookshot 2.0.1: the shield lay where the heart piece was, was collected and equipped; no heart piece. Overlay log hit; the save sets pickup Hash 9814903750835309225 and Hylian Shield ownership (slots 01, 04). |
| R8-PEDESTAL | — | Main save, first time adult in the Temple of Time, before the Forest Temple | confirmed: locked | Kareem via Claude, 2026-11-09, Hookshot 2.0.1, screenshot: no prompt at the pedestal, and Sheik stands beside it with a Talk prompt in the way. The remake's adult lock is Sheik's placement as well as the pedestal's gate; round 5's `free_time_travel` patch changes only the pedestal, so it is not expected to work as built. Adult save backed up at `save-backups/2026-11-09_1022-main-adult-first`. |
| R8-SHOPKEEPER-LATE | — | Shopkeeper's gift after Gohma and the castle (`r8-shops-cs8c/ingame`, copy of the ranch save) | confirmed | Kareem via Claude, 2026-11-09, Hookshot 2.0.1: with the Forest stone and Zelda's Lullaby already held, the shopkeeper gave the Boomerang and did not offer it again. The extended window works; D28's restriction lifts. |
| R8-SHEIK | — | What Sheik says at the pedestal (adult, before the Forest Temple) | recorded | Kareem via Claude, 2026-11-09: first talk, go to the Forest Temple first; talking again, go to Kakariko for the Hookshot. The second line names the Hookshot's vanilla place (Dampé), matching round 6's note that Sheik's `Talk_01`/`Talk_03` are a Hookshot hint slot; in a seed it misleads unless rewritten. |
| R8-SHEIK-MOVE | — | What moves Sheik off the pedestal | answered (community) | Speedrunning Discord via Kareem, 2026-11-09: tied to the Forest Medallion, not to learning the Minuet. Matches the pedestal's own gate (`SageOfForest_IsCompleted_Exp`, section 16) [inference: whether the game reads the medallion item or the sage flag is to trace]. |
| R8-GROTTOS | — | What opens the Kokiri Forest and Sacred Forest Meadow Wolfos grottos; the Kokiri grotto's scrub trio | confirmed | Kareem via Claude, 2026-11-09, main save: the Kokiri Forest grotto by the Lost Woods entrance and its Gossip Stone opens with the Song of Storms; inside, three scrubs, hit in the passcode order, and the last spawns the chest. The Sacred Forest Meadow Wolfos grotto also opens with the Song of Storms. Bombs open neither. Confirms round 4's overrides (`child_kokiri_forest.toml` KF Storms Grotto, `child_sacred_forest_meadow.toml` SFM Wolfos Grotto = `can_play(Song_of_Storms)`) and that the trio's chest is KF Storms Grotto Chest. The trio's `has_shield` is kept (not asked). |
| R8-SFM-TOPHOLE | — | The meadow's covered hole at the top near Saria | confirmed (adult) | Kareem via Claude, 2026-11-09, main save as adult: bombs open it (not the Song of Storms); inside, the Song of Time moves blocks, and behind them are a Gossip Stone and a small chest with a Business Scrub Seed. Confirms the round 5 rule of `Sacred Forest Meadow Chest (Item_ScrubBusinessSeed)` and GOSSIP_KOKIRI_FOREST_02 (`is_adult and has_explosives and can_play(Song_of_Time)`). Child access (child Song of Time at those blocks) and Bombchus on the cover are untried, so the rule stays adult and as is. |
| R8-PRELUDE | — | Temple of Time after the Forest Temple (main save) | confirmed | Kareem via Claude, 2026-11-09: after the Forest Temple Sheik still stands at the pedestal; entering the room triggers the Prelude of Light cutscene, after which Sheik leaves and the pedestal can be used. So Sheik's block lifts with the Prelude scene (Sheik at Temple), which the Forest Medallion triggers; OoT Randomizer's `Sheik at Temple` rule (adult, Forest Medallion) fits. Saves from before Phantom Ganon to after the scene backed up at `save-backups/2026-11-09_1347-main-after-forest`. |
| R8-SEED8-BOWLOCK | — | Seed 8 (full seed, main 14d7a26), child at the start | bug (open) | Kareem via Claude, 2026-11-09: after taking the Bow from a chest as child (it auto-equipped to a button and could not be used), then the Boomerang and Deku Sticks, none of the three could be used from the buttons until he saved and reloaded. Vanilla never gives child the Bow; first adult-only button item obtained as child in a seed. Saves and log backed up at `save-backups/2026-11-09_1423-seed8-bow-lock`. Follow-up: loading zones did not clear it (Mido's house to the Deku Tree); only Save and Continue. The remake's item bar (one ZR item, R cycles a bar): the Bow went on the bar at pickup although greyed out for child in the Items menu ("it takes adult strength"); switching to another item did not help; after the reload the Bow was off the bar and the items worked. [inference: the get adds the item to the bar without the age check the load-time rebuild applies; an alternative is a first-button-item tutorial state; all six backed-up slots already own the Bow, so no replay is possible from them.] |
| R9-LICHII | — | Seed 8 on the Lichii emulator (Eden family), as a LayeredFS mod in `%APPDATA%\eden\load\0400486024DEC000\Clawshot seed 8\romfs` | confirmed | Kareem via Claude, 2026-11-09: the seed loads (Mido's chests match his Hookshot run); the item-bar lock after taking the Bow before the Boomerang happens the same way and Save and Continue clears it, so the lock is the game's behaviour, not Hookshot's. Performance much worse than Hookshot. His earlier Lichii save backed up at `save-backups/2026-11-09_1535-lichii-oot-save`. |
| R9-SEED8-GUARDHOUSE | — | Seed 8, crash in the Market guard house (child) | upstream (known) | Kareem via Claude, 2026-11-09, Hookshot v2.0.11: crash on entering/inside the guard house. `sead::MainThread`, read of guest 0x48, `lr 0x80060308`, x23 = 0, x27 = 0, x9 = 0x160, x10 = -0x160: the same signature as open upstream issue NotRexed/Hookshot#1112 ("Crash when meeting Zelda", vanilla; the game's render code after `nn::os::LockMutex`). The seed changes nothing near the guard house (Market_Child_Static differs only at the Bazaar and Bombchu shop shelves, no dangling references). Log and saves at `save-backups/2026-11-09_1558-seed8-gatehouse-crash`; last autosave 15:56. A second crash in the same room ~16:06 (breaking pots; first time crates), same fault on `ModuleSystemWorker5`, log at `save-backups/2026-11-09_1607-seed8-gatehouse-crash2`. Both while Python test pools held the CPU at 100% (11 to 25 fps); pool capped in `c9e2e2b`. Posted on #1112 with Kareem's OK (issuecomment-6751538874). |
| R9-SEED8-MARKET | — | Seed 8, Castle Town Market as child | recorded | Kareem via Claude, 2026-11-09: (1) **new check, not in the census**: the Market Potion Shop owner (child) gives an empty bottle, has Link catch a bug in the shop, then fills the bottle with Red Potion; the save then has `IsGet.Item_Bottle` true [inference: `Npc_Hylia_046_BottleShop_Child` flow, untraced]. A free early bottle, unknown to the logic. (2) Child Shooting Gallery played without owning the Slingshot gave the vanilla seed bag (`MiniGame_HitTarget_HrlCity_Get_BulletBag` true); that check is not in seed 8's shuffled pool. (3) Bombchu Bowling closed; he has no explosives yet, so the prizes' `has_explosives` agrees; what opens the alley in the remake is to be seen. (4) Impa gave Serenade of Water (songs shuffled among song checks, D23). |
| R9-FREE-TRAVEL | — | `free_time_travel` overlay (`work/r9-sheik-cs9b/ingame`), adult-first copy before the Forest Temple | confirmed | Kareem via Claude, 2026-11-09: "working flawlessly": Sheik not at the pedestal, the pedestal returns Link to child before the Forest Temple, repeated age changes and Save and Continue fine. |
| R9-PRELUDE-PATCHED | — | Same overlay, after-Forest autosave before the Prelude scene | confirmed | Kareem via Claude, 2026-11-09: the Prelude scene plays as in vanilla (Sheik appears, song once, then leaves). First-pull boundary tested the same day, see R9-FIRST-PULL. |
| R9-FIRST-PULL | — | Same overlay, older child autosave, first Master Sword pull | **bug** | Kareem via Claude, 2026-11-09: the Rauru / Chamber of Sages scenes are fine; back in the Temple, Sheik's first adult scene plays **without Sheik**: no body, all of his dialogue skipped, only Navi talking and the camera cutting between Link/Navi and where Sheik should stand; the pedestal is usable at once. The patch's Forest-completion presence hides the placed Temple Sheik that the first scene (`Dm_TimeTemple_0050`) needs. Fix in round 10: keep him for that scene (present while `HavePlayedEvent.Dm_TimeTemple_0050` is false, or after Forest completion until the Prelude), check what the skipped dialogue sets, and retest from a child autosave. Default stays off. |
| R8-SKULLTULA-HOUSE | — | `r8-gifts/ingame/Test - skulltula-rewards-play-next.bat` (Jabu backup copy, 14 tokens) | confirmed (10 reward) | Kareem via Claude, 2026-11-09: the overlay loaded; the 10-token reward gave the Hookshot, and the father's next preview named the Boomerang at 20. Later thresholds are long-term; the 40 reward stays held. |
| R8-FROGS | — | `r8-gifts/ingame/Test - frog-seven-play-next.bat` (Jabu backup copy) | confirmed | Kareem via Claude, 2026-11-09: "exactly as expected" per `frog-check.md` (song replacements once, Storms prize, bug game). Taking the Hookshot after the Longshot did not replace the Longshot in the menu. |
| R8-MERCHANTS | — | `Test - merchants-from-after-forest.bat` | deferred | Kareem, 2026-11-09: he will progress his main save instead; Claude builds a merchant launcher from a copy of it when he reaches Medigoron, Granny's trade or the desert. |
| R10-FIRST-PULL-FIXED | — | `r10-agetravel-cs10b/ingame/Test - first-pull-fixed-next.bat`, child autosave 02 | confirmed | Kareem via Claude, 2026-11-09: Sheik is present for his first adult scene, gone immediately after; Link can return to child at once. |
| R10-MARKET-BOTTLE | — | `r10-gifts-cs10a/ingame/Test - market-bottle-next.bat` (Boomerang in place of the bottle) | **bug** | Kareem via Claude, 2026-11-09: Boomerang granted, bug lesson and potion skipped, he kept the one bottle he had (he emptied it himself beforehand; no extra bottle, no potion refill), the bug stayed in the room. On re-entry the shop kid played his frightened tutorial animation instead of the relaxed one, and talking to him crashed Hookshot (`ModuleSystemWorker2` FATAL indirect call, lr `0x8124948c`, log line 3079). The bypass leaves post-tutorial state unset; held until a fix passes. |
| R10-RUPEE-KOKIRI | — | `r10-pots-cs10d/ingame/Test - rupee-kokiri-piece-next.bat` | confirmed (grant) | Kareem via Claude, 2026-11-09: the child-only blue rupee gave a Piece of Heart, "no problem". The saves hold no post-collection save, so the repeat steps rest on his report. |
| R10-RUPEE-FIELD | — | `r10-pots-cs10d/ingame/Test - rupee-field-hylian-next.bat` | confirmed (grant) | Kareem via Claude, 2026-11-09: the grotto blue rupee gave the Hylian Shield, "no problem". |
| R10-POT-SUPPLY | — | `r10-pots-cs10d/ingame/Test - pot-supply-piece-next(-uncollected).bat` | partial | Kareem via Claude, 2026-11-09: the House of Twins pot dropped the Piece of Heart. In the uncollected run he threw the pot at a tree and the piece floats on the trunk above child Link: a thrown pot drops where it breaks, so a shuffled item can land out of reach. Respawn: that save's forest is closed, so he went to the Lost Woods and back; the broken pot did not respawn (no second piece). Save and Continue did not bring it back either (Kareem, later the same evening). The piece on the tree was out of reach: the item was lost. He notes Ship of Harkinian marks item-holding pots with a different look until collected. The Forest Temple hidden pot was not run. |
| R10-EXPERT-GALLERY | — | decision | decided | Kareem, 2026-11-09: the first expert win at each gallery is a check that adds Rupees (20) to the pool. |
| XC07/XC08 GC sign puzzle | — | Kareem's main save | answered | Kareem, 2026-11-09: any wrong sign at any point spawns the left green-rupee chest and locks the puzzle until Link leaves Goron City and returns; the correct order spawns the right purple-rupee chest. Decision (Kareem): shuffle only the solution chest; the failure chest stays a green rupee and its direction says there is no need to go back for it. |
| R11-HOOKSHOT-2012 | — | every `HOS_FS_OVERLAY` launcher on Hookshot v2.0.12 / v2.0.13 | **cause found, launchers fixed** | Kareem, 2026-11-10: every round-10 gift and age-travel test crashed at start; his vanilla game from the Hookshot launcher was fine. Logs (`save-backups/2026-11-10_0905-r10-tests-crash-on-start`): `sead::MainThread` read of guest 0 right after `prompts: xbox icons`, the stack holding `Font2/Scalable/External.Nin_Ounce_NVN2`. Cause, from the v2.0.13 release source (`host/prompts.c`, `host/mods.c`, `nx2/prompt_assets.py`; GPL, facts only): Hookshot now serves a controller-icon font larger than the game's and its own size table with that font's entry raised; it steps back to the game's icons when a *mod* carries the size table (`hos_mods_has`), but not for `HOS_FS_OVERLAY`, so the overlay's table is served, the larger font no longer fits and the game drops it. Every Clawshot output carries a size table, so every overlay launcher crashes (seed 8 too). Fix: load as a mod, `HOS_MODS=<folder holding exactly one <name>\romfs>` with `HOS_FS_OVERLAY` cleared; Hookshot then logs `prompts: a mod has the resource size table: the game's own icons in texts`. Claude checked both ways with headless boots of his exe (no window, scratch user folder, his game closed): the overlay crashes, the mod boots to the save mount, seed 8 loads 129 files as one mod. 28 test launchers and seed 8's converted (originals kept in the backup folder). Cosmetic cost: button icons in text are the game's Switch icons while a seed is loaded. |
| R10-DOOR-CLOSED | — | `r10-agetravel-cs10b/ingame/Test - door-closed-child-next.bat` (Jabu save: child, two stones, Fairy Ocarina) | confirmed | Kareem via Claude, 2026-11-10: the door "stays closed". His test saves show the grave chest opened (Song of Time taken) and Link still a child, so it stayed closed with the song learned, as vanilla does without the third stone and the Ocarina of Time. Log: no crash; the Graveyard file loaded from the mod. |
| R10-DOOR-SONG | — | `Test - door-song_only-child-next.bat` | confirmed, one cosmetic note | Kareem via Claude, 2026-11-10: the door starts closed; the Song of Time on the Fairy Ocarina opens it; the opening scene shows all three stones although he owns two and no Ocarina of Time (the native scene, cosmetic); the sword pulls fine. Log: no crash; `DoorOfTime.bfevfl`, `GameDataList` and the Graveyard file loaded from the mod. Re-entry after opening and the return to child are not reported. |
| R10-DOOR-OPEN | — | `Test - door-open-child-next.bat` | confirmed | Kareem via Claude, 2026-11-10: the door is open with no song, the pull works and the first-adult scenes play; he holds the Light Medallion only, with no Water stone and no Ocarina of Time. Saves: the grave chest unopened and Link adult. Log: no crash; `Market_Child_Static` and `Market_Common_f252.logic.module` loaded from the mod. Not tested (needs a way back to child): whether the Zelda escape and the moat Ocarina play early after an early pull. |

