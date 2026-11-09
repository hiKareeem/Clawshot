# Round 8, Track A: dependable fill (cs8a)

Branch `r8/fill`. Read AGENTS/README, plans 00–04, decisions, the round 6 and 7 reports and Round 8's opening on
shared files. OoT Randomizer's `Fill.py` read at `526b4c8d` (`E:/OOTRemake/work/r2-world/OoT-Randomizer`). No game,
launcher, window, dump write, merge, push or stash. Scratch scripts and measurements: `E:/OOTRemake/work/r8-fill/`.

## Item 1: measurement

`FillError` now carries the failed stage, the item, the allowed empty locations (none reachable) and the frontier
(the empty locations reachable with the assumed items, which the item may not take); the message names the stage
(commit `27ec803`).

`E:/OOTRemake/work/r8-fill/measure.py <mode> 0 200 <workers> <out.jsonl>` rebuilds `make_seed`'s inputs up to
`generate()` (gift, scrub, boss-heart and freestanding setup; the remake's own vanilla pool from the census) and runs
`generate()`'s attempt loop on `random.Random(seed)` for seeds 0–199 within the unchanged ten-attempt bound,
recording every failed attempt's payload and running the beatability search on the success. `summary.py` prints
the tables below; `debug_spots.py` and `fire_keys.py` printed the placements and key counts quoted under item 2.
Modes: `chest` (`--shuffle Chest`), `shop` (Chest Shop), `gift` (Chest Shop Gift), `all` (Chest Shop Gift Scrub
BossHeart), `default` (`Settings()`, the `CS1` string: the same settings as `chest`; its 200 attempt counts came out
identical to `chest`'s) and, at Claude's request, `freestanding` (Chest Freestanding) from a read-only
`git archive` of `r8/freestanding` at `c477fc1` with this branch's diagnostic `fill.py` laid over it.

### Before (main `3d803e5` plus the diagnostics only)

| Mode | First attempt | Most attempts | No fill in 10 | Failed attempts |
|---|---|---|---|---|
| chest | 118/200 (59.0%) | 6 | 0 | 134 |
| shop | 118/200 (59.0%) | 5 | 0 | 130 |
| gift | 19/200 (9.5%) | 10 | 42 | 1,001 |
| all | 0/200 (0%) | 10 | 196 | 1,983 |
| default | 118/200 (59.0%) | 6 | 0 | 134 |

Seed 7 Gift reproduced round 7's result: all ten attempts (nine failures: four songs, four Bombchu packs, one Fire
Temple key).

Failed attempts by stage and item:

| Cause | chest | shop | gift | all |
|---|---|---|---|---|
| dungeon: Small Key (Fire Temple) | 134 | 119 | 391 | 658 |
| type-held: a song (Zelda's Lullaby, Saria's Song, Song of Time, Requiem ...) | | | 451 | 1,223 |
| type-held: Weird Egg | | | 4 | |
| bomb ammo: Bombchus (5) / Bombs (5) | | | 144 | 97 |
| progression: Deku Shield / Hylian Shield | | 11 | 11 | 5 |

## Item 2: causes and fixes

Each fix has a synthetic failing-before test in `tests/test_fill.py` (seeds 0–19, one attempt each); every one of
them failed before its fix with the same message as the whole-world failure it models, and passes after.

1. **Fire Temple small keys** (`72e3e46`). `fire_keys.py` counts, all other items held, how many own keys each
   shuffled Fire chest needs: 0 (Near Boss), 1, 1 (both Big Lava Room chests), then 3, 3, 4 x6, 5, 7, 7, 8, 8. Eight
   keys need a key-free chest, two chests at one key and three at two: the first three chests must hold small
   keys, with no slack (the remake removed the N64 freebie; `remake/adult_fire_temple.toml`). OoT Randomizer
   places boss keys before small keys (`Fill.fill_dungeons_restrictive`), so the boss key could take one of the
   three (any of the 16 chests). Keys-first alone left 45 of 200 chest seeds failing their first attempt;
   `debug_spots.py` on seed 6 then
   showed Golden Gauntlets in the Near Boss Chest: the return kit (`age_return_fill_families`, D20) is placed
   forward into any adult chest before the dungeon stage. Fix: small keys, then boss keys, then the rest; and
   the own-dungeon items of every dungeon the kit does not draw from (all but the Forest Temple) go before the
   kit. Measured on chest mode alone, keys-first gave 155/200 first attempts, keys-first plus dungeons-before-kit
   200/200. Tests: `test_small_keys_take_their_forced_chests_before_the_boss_key`,
   `test_the_return_kit_leaves_another_dungeons_key_chest_to_its_key`.
2. **Bombchu packs with nowhere to go** (`da2f74f`). Seed 7 Gift, attempt 1: `Bombchus (5)`, 13 allowed, 0
   reachable. The search at the failure held the Bomb Bag but no Goron Bracelet and no Time Travel; Zelda's Letter
   was at the DMT Great Fairy and the Bracelet at Darunia, both placed by the type-held stage while it assumed the
   Bombchu packs, and D25 then put every pack behind a bag that needed them. Fix: stages before the D25 ammo stage
   (dungeon items, palettes, type-held) do not assume the packs. Test:
   `test_held_items_before_the_ammo_stage_do_not_rely_on_bag_gated_bombchus`.
3. **Songs** (`3619b67`). With Gift, the twelve song checks take exactly the twelve songs (`songs = song`), and a
   song placed early can take the only song check reachable without another song (Zelda's Lullaby left with Sheik
   at Colossus and the Royal Family's Tomb). OoT Randomizer meets this with `fill_ownworld_restrictive`: songs and
   shop items are placed on their own and only that stage is undone and retried, up to 15 times (`Fill.py`
   348–404 at 526b4c8d). The type-held stage (songs, shop refills, gift-held items) now does the same
   (`STAGE_ATTEMPTS = 15`); the ten-attempt bound of the whole fill is unchanged. Test:
   `test_songs_with_no_spare_song_location_are_retried_as_their_own_stage`.
4. **The second shield** (`cc2cbc4`). With Shop, items that have a native shop display were taken last in every
   stage, so both shields were the last progression placed; Mido accepts either, so the second needed a chest
   before Mido and found them all full (seed 17 shop: `Deku Shield`, 70 allowed, 0 reachable). The progression
   stage now takes them first; the other stages keep them last. Test:
   `test_either_shield_is_placed_while_the_other_can_still_open_the_way`.
5. **Native pick-up destinations** (`7345a02`, shared `cad8801`). BossHeart (and Freestanding on track E's branch)
   held every non-native pool item away from those locations. That made every item type-held, so junk went through
   the reachability stage alongside the progression and took the early chests (track E's Chest+Freestanding seed 7:
   no reachable location for the Boomerang; in the before-measurement, Bombchu packs with zero allowed locations
   left). New `Settings.location_type_items` holds a location type to its only items; `allowed()` enforces it and
   `fill()` fills those locations first from their palette (the first matching items of the shuffled pool), as OoT
   Randomizer fills shops first. `drops.seed_setup` uses it (shared commit `cad8801`, posted); track E is asked
   to do the same in `freestanding.seed_setup`. Test:
   `test_native_pickup_destinations_take_their_palette_and_leave_junk_to_the_fast_fill`; with the old holds the
   same world failed 4 of 20 seeds.
6. **An unbeatable fill** (`d498214`). Measuring the first five fixes, all-kinds seed 40 filled on its first attempt
   and then failed the beatability search (`generate()` raises there without another attempt): the Kokiri Sword was
   at LW Deku Scrub Near Bridge (`can_stun_deku`), placed while the progression stage assumed the junk.
   `shops.toml`'s `Nuts` and `Sticks` helpers read the physical `Deku Nuts (5)`, `Deku Nuts (10)` and
   `Deku Stick (1)`, normal items (so hints never name them, D29) that the fast fill puts anywhere; it put them all
   behind Mido. The only normal items any rule reads are those three (printed from every compiled rule's `reads`).
   OoT Randomizer's progression stage assumes only progression; now no stage assumes an item that a later stage
   does not place by reachability. This replaces fix 2's helper (`_assumable`). Test:
   `test_no_stage_assumes_junk_that_the_fast_fill_may_leave_out_of_reach` (failed before: "the goal cannot be
   reached"). The measurement harness now records such a seed instead of stopping.

The fill's stage order and assumptions are written up in `plans/04-world-format.md` ("Generating a seed").
