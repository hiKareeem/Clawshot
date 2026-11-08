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

## Remaining areas

Fire, Shadow, Spirit, desert/endgame and shared adult-overworld audits follow.
