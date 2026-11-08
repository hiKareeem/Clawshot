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

## Remaining areas

Fire, Water, Shadow, Spirit, desert/endgame and shared adult-overworld audits follow.
