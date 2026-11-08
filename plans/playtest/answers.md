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

