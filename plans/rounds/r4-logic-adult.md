# Round 4, track B: remake logic, adult areas (cs4b)

Branch `r4/logic-adult`. Build `e0f3ccfa`. Dump and save backups read-only; no game process or windows started.

## Scope and method

Audit every adult-side translated rule in the areas listed in Round 4 Track B. Facts come from remake guides,
round-three census evidence and read-only placement inspection. N64 alternatives unsupported by remake sources
remain explicitly unresolved rather than reported as verified. Hand overrides go in `remake/adult_*.toml`;
translated files and shared dependencies stay untouched. Commit area by area.

## Cross-track requests

- Loader prerequisite: Track A's sorted `remake/*.toml` loading, duplicate rejection and exit overrides are needed.
  Forest Temple's entrance now consumes a key (Nintendo Life Forest Temple walkthrough; IGN differences guide).
  The existing loader only accepts location and key-count overrides. Please include exit overrides in the
  prerequisite; event overrides are also needed where bosses have changed requirements. No loader change is
  committed by cs4b.

## Sources read

- https://www.ign.com/wikis/ocarina-of-time-remake/Biggest_Changes_and_Differences
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-forest-temple-walkthrough-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-fire-temple-walkthrough-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-water-temple-walkthrough-switch-2
- Local round-three Eurogamer and Polygon Skulltula guides (facts only; URLs to be recorded with area findings).

## Tooling observation

The first `~/go/bin/bermuda` command failed (127): the binary is `C:/Users/hi/go/bin/bermuda.exe`.
The directory listing showed `bermuda.exe`; the explicit path works. No unchanged retry.

## Forest Temple

Read every rule in `forest_temple.toml`. Changed seven gates in `remake/adult_forest_temple.toml`: entrance key;
west lobby total two; straightened hall total three; Hookshot to well/map balcony; east garden token needs
Scarecrow; both iced-eye passages need Bow. Five paired small-key locks in the Static Banc identify the
progression (rooms 0/1, 5/5, 9/10, 17/18, 20/23). The old pre-Bow lock is absent: Bow total three and frozen-eye
total five remain unchanged. These count keys acquired, not a simulated remaining-key wallet.

Checked/unchanged against the Forest walkthrough: entrance tree chest; Stalfos key; Song of Time NW door;
eye-switch NE door; strength block puzzle; Bow chest; red/blue Poes and Amy/Meg need Bow; Boss Key; Floormaster;
falling-ceiling chest; four-Poe basement event; boss key door; heart/reward follow boss defeat; one-way warp.
Hookshot to the lobby token and Longshot/upper-ledge west-garden token agree on their normal adult routes.
All N64 trick branches stay disabled.

**Kareem: can the entrance token be killed/collected without Hookshot after climbing the vines? Can the west
garden token be taken from the lower floor with ordinary Hookshot? Can the basement token be taken by hand
(Nintendo Life says no item, Eurogamer says Hookshot)? Can Phantom Ganon's first phase still be hit with
Hookshot rather than Bow? Can Din's Fire operate either iced-eye puzzle without Bow?** These alternatives are
not verified; the original boss/token rules remain pending, not certified. The two iced-eye paths use only the
documented Bow solution provisionally. Pots, drops, damage-boost/hover and cross-age alternatives have no
complete remake guide coverage and remain unverified.

Verification: `uv run pytest tests/test_world_remake_adult_forest.py -q`: **7 passed**.
`uv run python E:/OOTRemake/work/r4-logic-adult/smoke_forest.py`: old logic collected a key placed behind the
front door with no initial key; corrected logic collected nothing and could not reach the central room.
Putting the key in the entrance tree opens the central room. This exercises actual loading and search, not game
play. In-game: enter Forest with no small key, inspect the locked front door, then take the tree key; it should
open the door but not the next west lock.

Scratch inspection initially failed because `Translate` is a list, not a map (printed actor and traceback).
Fixed the distance calculation to zip the three coordinates; one rerun succeeded.

## Water Temple

Read every rule in `water_temple.toml`; compared the full IGN and Nintendo Life remake walkthroughs and five
token descriptions. Read-only Banc chest inspection: nine chests, four key actors (rooms 18, 8, 4, 20), pillar
Red Rupee (room 2), map (17), compass (3), Longshot (7), boss key (15). No chest in river room 21.
Four ordinary locks/eight lock actors agree with the walkthrough. This replaces the old assumption that capping
every N64 five-key rule at four reconstructs the remake.

Changed: map before Lullaby/keys; Compass moved to south bomb/boot/target route; pillar opens with one key,
Hookshot and Lullaby (Bow cannot bypass its lock); basement chest is a Red Rupee, not a key; basement token moves
there; high pillar token uses Longshot from inside the pillar; old falling-platform token moves to the
middle-water Ruto cracked room (explosives, not Longshot). Middle-floor east bomb wall/submerged Stinger passage/
geyser gets its own region. Three locks reach Dark Link/Longshot; Longshot targets replace Song of Time on the
river exit. The final key is behind middle-water Bow/Longshot/underwater block movement; fourth lock leads north
to bomb walls/block/geysers/boss key and the waterfall token. Boots are needed on the boss-door slope.
The river key chest is absent (`n64_only`). Existing four-key cap stays in the base override file.

Provisional naming, not a census link: the unlinked `Water Temple Cracked Wall Chest` world name represents the
remodeled middle-floor east bomb-wall/geyser key (room 4 Hash 16490222392193949581). This keeps its N64 name for
world consumers, but asserts no `locations.toml` identity. The source records this; future census linking must use
the actual Hash. Pillar Red Rupee: Hash 11682974908842171598.

Checked/unchanged normal routes: lowering water with Lullaby; torch-key Bow/Din's Fire; dragon block, boots and
Hookshot; cracked-room access at middle water; Dark Link combat as adult; Longshot chest after combat; Morpha
Hookshot combat and clear/blue-warp events; Longshot to boss ledge; boss key requirement. Sources:
- https://www.ign.com/wikis/ocarina-of-time-remake/Water_Temple_Dungeon_Walkthrough
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-water-temple-walkthrough-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2#water-temple

**Kareem: confirm the four-lock order (pillar, middle-floor west water-raise, high-west falling platforms,
north basement). Can the Ruto cracked-room token be collected by hand? Does ordinary Hookshot reach the river
and waterfall tokens (Nintendo Life says yes; Eurogamer says Longshot)? Can Hover Boots bypass the middle-water
Longshot target or boss-key block route? Can Golden Scale replace Iron Boots at the entrance?**
No such N64 alternate traversal is certified. Remaining pots/hearts/drops and child-assistance settings lack
remake coverage. Normal river-token rule remains unchanged pending the range disagreement.

Verification: `uv run pytest tests/test_world_remake_adult_water.py -q`: **12 passed**.
`uv run python E:/OOTRemake/work/r4-logic-adult/smoke_water.py`: no free Water keys; spheres were torch+dragon
keys, geyser key, Longshot, final key, boss key; four keys total, Morpha reached and goal true. Putting Longshot
behind the final key's Longshot target leaves goal false and Longshot uncollected. Moved Compass/tokens printed
their new regions and were accessible through those routes.

Cross-track: posted that `tests/test_world_data.py::test_remake_overrides`'s old four-keys-before-Dark-Link
expectation is obsolete (three now suffice). This file is outside Track B ownership; requested authorization
or a merge-time update rather than changing another track's test.

## Fire Temple

Read every rule in `fire_temple.toml`; full Nintendo Life remake walkthrough plus token guide and Banc chest/
lock inspection. Eight real key chests (rooms 1, 2, 4, 5 twice, 10, 11, 22); seven paired small-key locks plus
one single small-key lock; the cinematic boss lock is separate. Map actor is in the lower boulder maze (room 5
Hash 3688520809244472975); Compass is behind the narrow-walkway eye (room 16 Hash 16713240760352215634).
Their `GetEventName`s misleadingly name the other item: the actor's drop and walkthrough settle it.

Actual acquired-key totals: big lava room 1; two additional east/elevator locks 3; narrow path 4; upper-boulder
shortcut still 4; flame-maze entry 5; inner maze and Flare Dancer 7; lower boss-key loop 8. Changed these gates,
removed non-keysanity's automatic boss-loop unlock, moved Map/Compass and the side-room key to the flame-maze
north cell. Provisional world-name correspondence: the unlinked `Boulder Maze Side Room Chest` names this
remodeled side-room key (room 11 Hash 10521366928524045067); no census mapping is asserted.
The normal boss approach now records the Hammer/Time Block/pillar-lowered event; no unverified Hover skip.

Checked/unchanged: Goron Tunic heat protection; near-boss first key; north lava cell; bomb-wall south lava cell;
Song of Time tile-room token; strength block and ranged flame switch; bomb-wall maze token; upper keys including
bomb floor; scarecrow side route and two tokens; explosives for Flare Dancer/Hammer chest; Hammer and Song of
Time high cell; Hammer boss-loop token (already overridden); boss key; Hammer/Tunic Volvagia; heart/medallion/warp.

Source: https://www.nintendolife.com/guides/zelda-ocarina-of-time-fire-temple-walkthrough-switch-2
and https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2#fire-temple

**Kareem: confirm the eight-lock order above, particularly no key on the moving-fire shortcut back to upper
boulder maze. Can Hover Boots still skip the pillar, or bombs bypass the Time Block to the high cell? Does
Hookshot expose the first Flare Dancer (the remake walkthrough says Bombs only)?** Fire token #71's short
Nintendo Life description says Hammer room, but the full walkthrough and census place it in scarecrow room 8,
not Hammer room 13; that short description is not used to relocate it. Pots/drops and unverified alternatives
remain pending.

Verification: `uv run pytest tests/test_world_remake_adult_fire.py -q`: **8 passed** (keysanity true; no fake key).
`uv run python E:/OOTRemake/work/r4-logic-adult/smoke_fire.py`: start zero keys, nine collection spheres, eight
real keys, pillar-lowered event, Volvagia reached and goal true.

Cross-track dependency posted: `load._start_items` still injects an N64 free Fire key that the game/writer do
not grant. These real-key data rules require cs4a to remove it. Do not treat default-settings seeds as verified
until that removal; no compensating shim was added to the data.

## Shared overworld: adult-side audit

Every adult-specific location/event/exit expression was reviewed in the files below. "Unchanged" means the
named normal route agrees with sources, not that every N64 alternative or pot/drop is certified. Shared child
rules stay Track A's. No empty override files were created merely to claim area coverage.

| Area | Checked/unchanged normal routes | Changes | Unresolved |
|---|---|---|---|
| Kokiri Forest | adult House of Twins token needs Hookshot/night; forest exits and shop access | none | bean-platform rupees, Hover alternatives, adult outside-Deku drops |
| Lost Woods | adult Mido passage Saria's Song; bean ride to Above Theater token; Cojiro→Mushroom and Potion→Saw | none | Hover/Longshot bridge geometry; underwater river shortcut; trade timers vs N64 reset assumptions |
| Sacred Forest Meadow | adult maze passage and Minuet; Hookshot entrance ledge and token | none | night-only token flag disagrees with some guide descriptions; alternate combat/traversal |
| Hyrule Field | free main-area boundaries; adult Big Poe hunting needs Epona/Bow/bottle | none | old grotto Hammer alternatives, pots/wonder items, new wetland-crate token absent from world |
| Lon Lon Ranch | adult/day Epona's Song, Ingo races and escape; stables/house; cows remain excluded | none | hurdle rewards; new tower token not modeled; race-money abstraction |
| Market | ruined adult town, adult Poe Collector, five-Poe bottle reward, all other shop/minigame access child-only | five bottled Poes rather than ten; stable N64 name retained | adult pot counts, collector reward flag after repeat visits |
| Kakariko | Hookshot roofs and adult/night roof token; adult Bow gallery; Pocket Egg/Talon/Cojiro; Song of Storms as adult | none | exact Nocturne trigger without all first-three medallions; free-jump windmill heart; roof jumps/shop prices |
| Graveyard | adult Dampé race has no equipment prerequisite; Song of Time exit to windmill; bean/Longshot heart route; Din's Fire Shadow entrance | none | repeat-race chest choice; hand-collect heart alternatives; ordinary adult grave opening times |
| Death Mountain Trail | adult two grey-rock tokens need Hammer; Biggoron trades/receipt and three-day wait | none | N64 damage-drop heart, bean/Hover summit routes and exact timed-delivery safety |
| Death Mountain Crater | adult Hookshot bridge/Sheik/Fire entrance; bean-volcano heart; Hammer fairy entrance; Tunic heat protection | wall heart also has a documented child heat-risk climb; adult safe route needs Tunic, no Hookshot | no-Tunic adult brief visits, N64 Hover/Longshot drops, OHKO timing; fairy prices |
| Goron City | stop rolling Goron with bombs/bomb flowers; Tunic and Darunia passage; statue route; grey rocks | ceiling token now requires Hookshot, not adult alone | Bow stopping Goron; grotto lava crossings; wallet/price requirements |
| Zora River | adult two high tokens Hookshot/night; waterfall Lullaby; normal river passage | none | adult no-bomb boulder passage; Hover/bean heart alternatives; underwater rupees |
| Zora Domain | Blue Fire thaws King and grants Tunic; prescription/frog; frozen high token | Hookshot collection; adult lake shortcut after Water clear; shop not opened by Blue Fire alone | post-clear shop reopening provisional; ordinary Bow/ranged token alternatives; night flag |
| Zora Fountain | adult ice platforms/Ice entrance; Boots bottom-heart; Gauntlet hidden-cave rock | hidden-cave route uses Lenses, removes original-only bomb rocks | lensless invisible-enemy tunnel, magic cost, night token flag, no-Tunic bottom-heart dive |
| Lake Hylia | bean/scarecrow roof heart; Golden Scale lab dive; adult fishing; tree token Longshot; lab crate Boots/Hookshot; child-taught adult Scarecrow | Boots entry (not Scale/Longshot); Fire Arrows only at restored lake; adult return shortcut after Water clear | low-water Fire Arrows via scarecrow; Lab token without Tunic; fishing rewards and timed-trade shortcuts |
| Temple of Time | Prelude after Forest, Rauru reward, initial age change at pedestal | documented five-adult-sage Light Arrows route instead of N64 Shadow+Spirit-only helper | reduced-medallion trigger; reverse-age chronology (below) |

Specific changed checks live in `adult_death_mountain_crater.toml`, `adult_goron_city.toml`,
`adult_lake_hylia.toml`, `adult_zoras_domain.toml`, `adult_zoras_fountain.toml`, `adult_market.toml`,
`adult_temple_of_time.toml`; each has a `source`. The adult shop reopening after Water clear is provisional:
IGN explicitly says it stays sealed while doing Water even after freeing King Zora; Nintendo Life says the
Domain thaws afterwards, and both adult Banc variants place shops. This does not prove its exact reopening flag.

Sources (facts only; normal-route descriptions, not inferred sequence-break proof):
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-walkthrough-switch-2-remake
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-gold-skulltula-locations-rewards-switch-2
- https://www.eurogamer.net/all-gold-skulltulas-locations-zelda-ocarina-of-time
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-biggeron-sword-trading-sequence-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-scarecrows-song-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-horse-epona-how-to-get-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-bottle-locations-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-bow-arrow-fire-ice-light-arrows-switch-2
- https://www.nintendolife.com/guides/zelda-ocarina-of-time-great-fairy-fountain-locations-all-switch-2
- https://www.ign.com/wikis/ocarina-of-time-remake/Water_Temple_Dungeon_Walkthrough

**Kareem: check the unresolved column area by area before trusting full-game seeds. In particular: does the Zora
shop reopen immediately after Morpha? Do Light
Arrows require all five adult medallions, or only Shadow/Spirit if obtained early? Is Fire Arrows collection
possible at low water via the scarecrow? Does Lenses of Truth still consume magic?** Conservative documented
routes are modeled where alternatives lack remake proof; they can make logic stricter than the game.

**Reverse time travel:** the Forest walkthrough says child return unlocks only after Forest Temple. `Search`
retains reachable child regions and one shared inventory across ages, so it cannot distinguish a newly found
adult item used on the child side before reverse travel unlocks. Gating initial `Time Travel` on Forest would
deadlock adult access. This is an engine/temporal-model question, posted to the reviewer, not fixed by inventing
a data gate. Normal child-start monotone search may still find a valid order, but it is not a chronological
playthrough proof.

Verification: shared-overworld targeted run had **8 passed, 1 failed**. The failed shortcut test was blocked by
the test's assumption, not the rule: printed path `Domain → River → Field → Lake` was open while the direct
shortcut predicate was false. Isolated the direct source exit; rerun of both shortcut directions **2 passed**.
Additional Fountain/Market tests **2 passed**. `smoke_overworld.py` exercised all seven changed route groups:
each printed false before its required item/event and true afterwards; Golden Scale/Longshot could not replace
Boots, and Blue Fire could not open the adult shop. Separate live library smoke printed cave false before Lenses/
true after without Bombs, and Poe reward false at four/true at five.

Further source check corrected the provisional crater override before handoff:
https://www.eurogamer.net/zelda-ocarina-of-time-death-mountain-crater explicitly describes child climbing down
from the summit to the wall heart before burning, and adult collection made safe by the Tunic. The Nintendo
Life Hookshot approach is not exclusive. Rule now allows child `can_take_damage` or adult Tunic, without
Hookshot. Updated regression **1 passed**. Child-side approach/heat regions remain cs4a's; brief adult
no-Tunic/OHKO timing remains unverified.

Further read-only gate research: ZoraDomain adult shop module `ZoraDomain_Adult_Common_1185` and shop ice module
`..._8ac9` name `SageOfWater_IsCompleted_Exp`; Market Sheik module `Market_Adult_Prefab_7f43` names
`AllSage_IsAfter_Ready_Exp`. The BoolExp entries exist in GameDataList. String co-occurrence alone is not a
decoded truth table, so the exact post-clear shop/Light Arrows trigger questions are retained. Eurogamer's
Big Poe guide independently confirms 500 points/five Poes for the Bottle and 1000 for the Gold Rupee:
https://www.eurogamer.net/big-poe-locations-in-zelda-ocarina-of-time.

## Loader prerequisite and rebase

Reviewer authorized rebase onto main's `9c4abf0`. Restoring loader text first left an EOL-only dirty state:
`git rebase main` refused unstaged changes; `git diff -- load.py` showed only the CRLF normalization warning.
`git restore -- src/clawshot/world/load.py` removed the local copy byte-for-byte, then `git rebase main` succeeded.
No loader code was committed by cs4b. Area overrides now use the real prerequisite on the branch.

## Remaining areas

Shadow, Spirit and desert/endgame audit reports follow.
