# Round 6, Track A: readable locations (cs6a)

Branch `r6/names`. Read AGENTS, README, plans 00–04, decisions and all five round-5 reports;
round-6 opening and round-5 shared-file rules apply. No dependencies or shared generated definitions changed.
The running `E:/OOTRemake/work/r5-seed/` and every user/save folder are untouched. No game, launcher,
window, Hookshot build or terminal-control command started.

## Item 1: player-facing catalog

Catalog complete: `src/clawshot/data/location_names.toml`, read by `generate.names.load`.
Reproducible placement/guide research stays outside the repository under `E:/OOTRemake/work/r6-names/`.
Keep internal world/OoTR identities and physical Hash/flow identities unchanged; readable labels are presentation.
Names include currently excluded chests and held gift checks as well as the enabled pool, so settings do not
silently change what a check is called. Excluded routes stay excluded; a label is not a new access guarantee.

### Mido's house

All four are settled in game (Kareem, 2026-11-08; Claude's reviewer update): walking in, left-to-right.
`seed-shop-7` gave Mirror Shield at far left (`Top Right`) and Kokiri Sword second from left (`Bottom Right`).
The earlier `chest-ocarina-storms` test identifies far right as `Top Left`; third is therefore `Bottom Left`
by elimination (both right-hand checks gave Blue Rupees in the current seed). The read-only placement probe
independently agrees. No new mod, replay or observation is requested.

| Walking in, left to right | Hash | Internal OoTR name | Vanilla |
|---|---|---|---|
| Far left | `4555665598794293658` | `KF Midos Top Right Chest` | Blue Rupee |
| Middle left | `12786193094758345086` | `KF Midos Bottom Right Chest` | Blue Rupee |
| Middle right | `10831981390482426294` | `KF Midos Bottom Left Chest` | Green Rupee |
| Far right | `9725242744547055868` | `KF Midos Top Left Chest` | Blue Rupee |

Provenance: Kareem in game, 2026-11-08, `seed-shop-7` plus `chest-ocarina-storms`, reported by Claude.
The initial placement-inferred middle mapping is superseded by that settled in-game mapping.
Existing world labels/IDs, vanilla pool and grants are unchanged.

Probe first failed because `Translate` is a list, not a map. Printed the exact three position payloads;
changed only axis indexing to 0/1/2; the single aimed rerun printed all four chests and nearby house props.
Decoded values remain outside the repository.

The independent read of both Child/Adult Dynamic files printed the same ordered four identities, exact
positions and vanilla drops (`age_copies_identical = True`). No age-specific reordering is hidden.

Required coverage inventory: **335 logical checks / 405 physical definitions**: 184 chests; 128 shop
shelves grouped into 72 logical slots (64 ordinary and eight mask loans); 93 linked gift steps grouped into
79 checks (including twelve songs and six Great Fairies). Extra held checks are documentation only.
The cs6d integration contract adds four opt-in once-sale Scrub families (nine physical copies, including
the shared KF/LW stick check): **339 descriptions / 414 physical identities total**. Token is not enabled.
Coverage oracle: `uv run pytest tests/test_names.py -q` **1 passed**; actual catalog reader printed
339/414 and the correct second-left Mido identity. Both completed fragment readers also passed (236/306
and 99/99 respectively; the latter was independently checked by its producing research slice).

### Catalog conventions and remaining observations

Shop names use the customer's view facing the shopkeeper: top/bottom row, far/inner left/right. Shelf
geometry was checked across every age/Alternative/short-stock copy, calibrated against Kareem's Mido
handedness. It is placement-derived, not newly observed shop gameplay; each source marks that limitation.
Static directions omit vanilla rewards/prices, which change with placements and cs6b's settings.
Sources retain the guide URLs and Hash/flow evidence; no guide prose or decoded file tree is committed.
Two draft Ganon Light-trial locators incorrectly said the second-room chests were behind a lock. The current
plan and override explicitly put both before the single boulder-room lock; the final catalog follows that
existing contract. No key requirement or world rule was changed.

Research found no reason to lift an exclusion:

- The two excluded purple chests at the forest-exit bridge ledge (`4349272251343787229` in KF,
  `17479747339356189279` in LW) have identical translated surroundings. **Kareem: are these two independently
  collectible checks or two map copies of one chest?** Both stay excluded. The scrub copies below also
  duplicate across maps; posted to cs6d for the existing shared-once-flag work.
- **Gerudo Valley Octorok grotto:** placement has a silver boulder above its joint; round-4 prose says the old
  silver rock is gone. It may mean a different rock. The opener remains unresolved, not silently changed.
- Tent-grotto cover, Fortress underground entrance, windmill high-chest approach, Fountain ruins approach,
  and KF storms-grotto chest appearance remain the existing playtest questions. Labels identify landmarks
  without declaring those routes verified. All twenty excluded chests retain exclusion notes.
- Mask loans are catalogued but not shuffled. Their physical shelf displays differ from translated
  `MaskShop` vanilla assignments (e.g. Item 1 is the Spooky Mask display, translated Gerudo Mask).
  No mask pool or logic normalization is introduced by naming work.
- Guide disagreements on fish length, rooftop routes and extra gift triggers are not converted into new
  logic. Directions use the supported landmark/action, not an invented threshold or alternate route.
  The Kakariko rooftop man uses Nintendo Life's Potion Shop rear/Hookshot route (#6):
  https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2 .

## Cross-track coordination

Posted on `cs-r6` as cs6a: spoiler ownership; preserve `placements`/`spheres` world keys, add separate
`locations` presentation metadata. No repository play-note writer exists; planned `generate.play_note(seed)`
and isolated `patch/__init__.py` wiring to emit `play-note.md` (own separate commit under shared-file rule).
Asked cs6b for the settings-string serializer API; Settings and CLI remain theirs.

## Verification

No ready claim yet. Four full gates will run before each item is posted ready, with dump-test temporary
folders outside the repository. Actual CLI output smoke will verify the final spoiler and note surface;
no game verification is claimed for presentation-only output.

`generate.names.load` was exercised on a session-created synthetic TOML outside the repository: preserved
the logical key, grouped two physical IDs, kept Unicode and an empty non-OoTR identity. Smoke passed; the
temporary synthetic file was removed. No dependency on a player dump is needed to read the catalog.
