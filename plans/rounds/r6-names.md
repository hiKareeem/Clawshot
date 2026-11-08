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

## Item 2: audit of positional/provisional chest matches

Read-only probes `audit_pairs.py`, `link_inventory.py` and `rule_equivalence.py` under
`E:/OOTRemake/work/r6-names/` printed each current Hash, actual actor-to-item resolution, world vanilla,
region, rule and compiled dependencies. Detailed evidence: `pair-audit.md` there; per-check sources for
all 184 chests are in the catalog. No census/world identity or rule is changed.

Recomputed original matching against the existing 184-chest inventory (exact same current IDs):
49 current links agree with unique-item matching; two with residual matching (sole chests at Wasteland
and Zora River); 98 are manually linked/corrected; 35 are remake-only. The three old automatic proposals
that differ from current identities are the already-corrected DC Bomb Flower Platform, Ganon Spirit/Water,
and LW Near Shortcuts falsely paired to the excluded elevated purple chest. None is reinstated.

| Group | Remake items and effect of a label permutation |
|---|---|
| Mido, doorway order | Blue/Blue/Green/Blue; in-game settled. Same region, `True`. Naming orientation changes no access. N64 Bottom Right's Recovery Heart is replaced by its physical Blue Rupee through `remake_vanilla`. |
| GC Center/Right blue pair (`1176975953041865014`, `14647422914070455120`) | Blue/Blue; same exact rule and region. Label-only. |
| GC red/Left (`4402942101476009858`) and extra purple (`3870071239709713434`) | Red/Purple; NOT interchangeable with blue pockets: red is Hammer-or-Silver, purple Silver-only. The red/Left match is rock-layout evidence, not a proven N64-left viewing orientation. |
| GTG Lobby Left/Right (`2436665354602612279`, `11182647876438515984`) | Blue/default Green; native mechanisms differ (east eye-switch drop versus west Lens chest). Both modeled with the conservative `(Bow or Slingshot) and Lens` union, same region: label permutation currently solver-neutral, not evidence that native requirements are equal. |
| GTG Heavy Block First/Second (`6897789835137994741`, `3750231902048775592`) | Red/Bombs (5); room-clear versus cracked-wall chest. Both currently require `can_blast_or_smash`, same region: label permutation neutral under that union only. Third is the unique key; the extra Seed is the Bow-switch chest, not part of the ambiguous pair. |
| Spirit invisible Left/Right (`9143177002861777924`, `14040210993541550542`) | Red/Red; same region and exact Lens rule. Label-only. |
| Fire timed scarecrow trio (`862385681502746018`, `15073195886628236505`, `17001858340376096722`) | Purple/Red/Red; same region and Scarecrow requirement with supported tricks off. Which chest inherits the old name affects per-check vanilla identification, not supported access or the total actual pool. |
| Ganon Light static blues (`1029712040059298120`, `7461796063704896255`, `14046623154429024571`) | Blue/Blue/Blue; same region, `True`. Positional N64 labels neutral within these three; trap positions remain out. |
| Ganon Light “Invisible Enemies” key (`15320975652699461295`) versus first-room spawned Red (`14962432460641118089`) | Different items/mechanisms; both same region and Lens requirement with the unsupported Lens trick off. Preserve the unique-key correspondence, physical room labels and actual drops. Do not conflate with the second-room Lullaby Green Rupee, whose requirement differs. |
| Well “Underwater Left” (`12988877782812797760`) | Actual east/right ladder dip, Blue Rupee. The old name is provisional; there is no west chest to swap with. Existing Lullaby requirement remains conservative pending water-state observation. |

**Logic-sensitive boundaries:** GC red/purple versus blue pockets; GTG native eye/Lens and clear/wall
requirements if the conservative unions are ever removed; Well east-dip water state. Within each listed
ambiguous pair/group, the supported solver currently has equivalent access. Different vanilla items are
explicitly not called identical: `remake_vanilla` resolves each physical actor, not the old N64 heart/ammo value.

Resolved route/item distinctions stay distinct: DC lower-Lizalfos Red `7764016096998075927` versus Bomb Flower
Platform Shield `11582649900854566065`; Ganon Water Bombchus `14404733996390762670` versus Spirit Seed
`7899179288432849355`; Fire north flame-maze cell `12945617941305968586` versus Highest Goron
`10521366928524045067`. Their room/event/landmark evidence corrected prior matches in round 5.

Actual compiled-rule smoke exhausted child/adult × day/night/both × counts 0–3 for every read dependency
(all local thresholds fit that range), also asserting same region. Equivalent results: Mido 6 states;
GC blue 98,304; GTG lobby 1,536; GTG First/Second 24,576; Spirit invisible 96; Fire trio 384; Ganon blues 6;
Ganon Lens key/spawn 96. Negative boundaries passed: child Bomb Bag opens GC blue, not red; adult Hammer
opens red, not purple. This executes compiled predicates, not just string/dependency comparisons.
Printed supported assumptions: `logic_fire_scarecrow`, `logic_lens_spirit`, `logic_lens_castle`,
`logic_goron_city_leftmost` are all false. No gameplay certification is claimed.

Sources: round-4 Goron City audit; round-5 adult/child chest inventories; current sourced overrides;
https://www.eurogamer.net/gerudo-proving-grounds-walkthrough-zelda-ocarina-of-time ;
https://www.eurogamer.net/spirit-temple-walkthrough-zelda-ocarina-of-time ;
https://www.nintendolife.com/guides/zelda-ocarina-of-time-fire-temple-walkthrough-switch-2 ;
https://www.eurogamer.net/inside-ganondorfs-castle-walkthrough-zelda-ocarina-of-time .
**Kareem: existing GC bomb-only, GTG native-prerequisite and Well water-state questions remain useful;
no Mido replay is requested.**

## Item 3: readable output and logic-derived opening

`spoiler()` preserves world-keyed `placements` and progression `spheres`, adding `locations` metadata
(player name, where, OoTR identity, physical IDs, provenance; shops include price/release).
`play_note()` renders those descriptions beside unchanged world/OoTR keys for every shuffled reward.
The isolated shared writer change emits `play-note.md` beside `spoiler.json`, computing both before
romfs writing so a presentation/proof error cannot leave a partially written seed.

### Reviewer extension: the actual opening route

Kareem's reported seed-shop-7 lock is ground truth, not replayed: its Hylian Shield passes Mido but cannot
reflect the Slingshot-room scrub's nuts as child. The existing `here(has_shield)` logic also needs the
post-Mido Deku Shield purchase. The old handwritten “buy Hylian, then clear Tree” note omitted it.

`generate.route.opening` now proves a concrete child-only source witness for the catalog's presentation
milestone (`Defeat Queen Gohma`, entry `Deku Tree Lobby`), through existing logic rather than new game rules:

1. Find the first collection prefix that actually reaches the milestone.
2. Reverse-delete source checks while the milestone remains reachable, retaining one sufficient witness
   even with OR alternatives (not the unsound intersection of individually optional items).
3. Replay those sources one at a time through `Search.child_only`, prioritizing currently reachable
   outside-dungeon prerequisites before entering. Adult-only finds/events cannot satisfy child requirements.
4. For every acquisition, reverse-delete prior sources against actual access to that check; list the
   predecessor items/counts and source steps. Entry preparation covers the selected clear, not merely the
   weaker lobby reachability predicate. Finish is checked against the actual milestone event.

This is a deterministic deletion-minimal witness, not a claim of shortest travel, globally cheapest
shopping, every possible route or exact rupee earnings. Alias/count semantics remain Search's.
The opening table includes each needed purchase with physical shelf, price and original shelf-release
condition; ordinary sphere finds are explicitly not a mandatory shopping list.

Observed regenerated baseline (outside the protected active folder): Sword from Mido second-left;
Hylian Shield from KF8 (10); Deku Shield from KF6 (40), requiring the prior Sword/Hylian to open its
post-Mido shelf; THEN enter the Deku Tree; Slingshot from the falling-platform room's upper chest;
complete Gohma. The actual CLI wrote 228 shuffled checks, 26 spheres, 77 romfs resources plus spoiler/note
under `E:/OOTRemake/work/r6-names/smoke-shop7/`. No active seed/user/save was read or changed.

`tests/test_names_route.py`: **2 passed**, including OR alternatives, optional-source deletion, required
purchase-before-entry ordering and rejection of an adult-only pickup faking child access.
Catalog + presentation + route synthetic checks: **4 passed**. `tests/test_names_dump.py`:
**1 passed**, recreating seed 7 Chest+Shop and checking its serialized spoiler and rendered note put the
KF6 Deku Shield purchase before Tree entry, with Sword/Hylian prerequisites and the post-Mido release.
Scoped format/lint passed. The complete four-gate chain is running; no full-ready claim yet.

Canonical settings integration prerequisite: cs6b's `clawshot.settings.shop_price` is the shared price API;
this pre-settings baseline still has fixed vanilla slot prices. Requested authorized rebase once its
producer is on main; the final settings-aware presenter will call that API, not duplicate pricing policy.
The actor used for cheap-shield pricing must be the placed native display, not the original shelf item.

### Launcher safety update (reviewer, Hookshot 2.0.1)

No launcher was created/run by this track. For any future launcher, the ONLY executable is now
`E:\Games\Hookshot\bin\hookshot.exe`, with `HOOKSHOT_NO_UPDATE_CHECK=1`, and missing exe is a hard stop.
Never fall back to the folder-root launcher: it ignores `--user` and can target Kareem's main save.
