# Decisions

## Decided

- **D1 Python 3.12+ with uv** (Claude, 2026-11-07). OoT Randomizer and Archipelago are Python and MIT, so their
  logic, fill and multiworld code can be ported; the generator is not speed-critical. Alternative: Rust or C++ (as
  Ship of Harkinian) would be faster but loses that reuse.
- **D2 Output is a mod folder in the emulator layout** (Claude, 2026-11-07): `<out>/romfs/...`, only changed
  files. It runs on Switch 2 emulators (and their PS5 builds), on Hookshot (`HOS_FS_OVERLAY` now, `mods\` after
  round 1 track C) and on native ports that let romfs files be replaced. Code hooks come later and stay optional.
- **D3 Own BYML, SARC and zstd-dictionary code** (Claude, 2026-11-07). The existing Python libraries for these
  formats are GPL-2.0; the reader is ~120 lines.
- **D4 Location IDs are (file, actor Hash)** (Claude, 2026-11-07). Stable across tools and settings.
- **D5 Location definitions are committed, game files never are** (Claude, 2026-11-07). Definitions are
  identifiers and names, as OoT Randomizer's location list is.
- **D6 Name: Clawshot** (Kareem, 2026-11-07). "Longshot" is kept for a Hookshot-specific tool. Collision check
  2026-11-07: one unrelated GitHub repo, PyPI `clawshot` free.
- **D7 License: MIT** (Claude, at Kareem's request to decide, 2026-11-07). The same license as OoT Randomizer and
  Archipelago, so code can move between them in both directions and an Archipelago world can later go into
  Archipelago's own repository. GPL would require anyone who distributes a modified Clawshot to publish its
  source; little is lost without that here, since the tool carries no game data and can't be sold. The Hookshot
  code we contribute stays under Hookshot's GPL.
- **D8 Archipelago after a stable solo randomizer** (Kareem, 2026-11-07). Moved to Later in the roadmap.
- **D9 Rounds run as in `02-orchestration.md`** (Kareem, 2026-11-07): Claude launches and watches omp agents in
  herdr, Bermuda for cross-track posts, parallel where possible, Kareem tests in game when asked.
- **D10 Trap chests stay out of the first seeds** (Kareem, 2026-11-07, on round 1 track B's finding that the six
  N64 Ice Trap chests are item-less trap actors here).
- **D11 Cows stay out** (Kareem, 2026-11-07): no per-cow save flag, so not a one-time check without code hooks.
- **D12 The remake's extra chests are shuffled; `Item_ScrubBusinessSeed` is filler; `DreamWorld` stays out**
  (Kareem, 2026-11-07).
- **D13 No chest-size-matches-contents feature** (Kareem, 2026-11-07), provided a small chest can give a big
  chest's item and a big chest a small item. Round 1's in-game test checks both directions.
- **D14 Hookshot mods are RomFS only; no exefs patches** (Claude, 2026-11-07, on round 1 track C's question).
  Recompiled code can't take instruction patches, and nothing Clawshot plans needs data patches. Upstream PR
  `NotRexed/Hookshot#321`.
- **D15 First playable seeds shuffle chests only** (Kareem, 2026-11-07). Each other kind (freestanding items, boss
  hearts, scrubs, shops, gifts) joins once its in-game test passes.
- **D16 Fixed items now, progressive later** (Kareem, 2026-11-07): a check gives one fixed item (finding the
  Longshot first gives the Longshot). Progressive items come later through event-flow edits or Hookshot hooks. A
  downgrade (the Hookshot found after the Longshot) is to be tested in game.
- **D17 Treasure Chest Game: only the reward chest is shuffled** (Kareem, 2026-11-07). The 11 game boxes stay
  vanilla for now (Ship of Harkinian has shuffling them as an option; a later setting). The reward chest joins
  the chests once its contents swap is tested in game.
- **D18 Fast start: the intro skip is on by default; Saria, Mido, the Deku Tree's talk and Kaepora are settings**
  (Claude, round 4 spec; both settings' in-game tests passed for Kareem, 2026-11-07). Skipping Mido changes the
  logic (no sword and shield to reach the Deku Tree).
- **D19 The Deku Shield and shop contents are shuffled with the other items** (Kareem, 2026-11-07, after seed 22
  needed nearly every rupee in the forest for the shield). The logic places the shield: with Mido kept, it must be
  reachable before him; with Mido skipped, anywhere the logic allows. Shop contents (shopsanity) join once a
  changed shop slot is tested in game, like the other kinds (D15). Buying the shield plays a short tutorial: the
  test checks it with another item in that slot.
- **D20 Seeds guarantee adult Link can get back to child** (Kareem, 2026-11-08). The remake keeps adult Link adult
  until the Forest Temple's sage (section 16); `age_return_guarantee` (on) accepts a seed only if adult can open
  the return with what the first sword pull requires plus adult checks, so an early pull cannot lock a player out.
  It stays the default until the `free_time_travel` pedestal patch passes its in-game test.
- **D21 Shops take only items with a native shop display** (Claude, round 5, provisional; Kareem not yet asked
  whether he wants majors in shops). A stand-in display does not work as tried: changing only the seller's
  `GoodsList` actor left the shelf's Deku Shield on sale (Kareem in game, 2026-11-08).
- **D22 A gift's "already given" check uses an existing once-only flag, else a new saved `GameDataList` Bool**
  (cs5d, reviewed by Claude, round 5). The Great Fairies have no once-only flag of their own; the new Bool
  (`Clawshot.Gift.<flow>.<event>`) worked in game: a save made before the patch loaded, the fairy gave the
  Hookshot once and only healed after, also after quit and continue (Kareem, 2026-11-08).
- **D23 Songs go only to song locations; other gift items only to gift locations, until seen working in a chest**
  (Claude, round 5, provisional; OoT Randomizer's `shuffle_song_items = 'song'`). The Song of Storms in a chest
  showed a green rupee with the song's text and set `IsGet.Item_Melody_StormSong`; with the Fairy Ocarina (itself
  from a chest) it plays as a learned song (Kareem, 2026-11-08). So songs and the Fairy Ocarina work in chests; the
  default stays songs-on-song-locations (OoT Randomizer's default) and "songs anywhere" becomes a setting (round 6).
  Other gift items stay on gift locations until each actor is seen in a chest.
- **D24 Defaults stay close to vanilla; difficulty is opt-in** (Kareem, 2026-11-08). The base seed keeps new
  players on the vanilla path (the forest closed until Gohma, Mido kept, songs on song spots, own-dungeon items,
  the return guarantee on); settings add difficulty for players who want it. So `forest` defaults to `closed`, with
  `closed_deku` and `open` as options for advanced players; not all at once. Quality-of-life settings that remove
  grind without changing the route (the intro skip, the cheap Deku Shield) may stay on.
- **D25 Bomb and Bombchu pickups from chests only where the Bomb Bag is already guaranteed** (Kareem, 2026-11-08,
  Claude's recommendation). Ammo packs grant their missing container (round 6, section 24). In game, a shop bomb
  bundle in a chest gave a Bomb Bag and 20 bombs in the menu, but the bombs cannot be used (Link raises one and
  the action cancels; Kareem, 2026-11-08, round 7). Default: a `Bombs (N)`/`Bombchus (N)` item
  goes only to a location the logic cannot reach without the Bomb Bag, so a pickup never hands out an early bag.
  Counting such pickups as extra Bomb Bags is a later advanced option. Shop refills stay in shops.
- **D26 Hints: stones speak without the Mask of Truth by default; English hint text in every language archive**
  (Kareem, 2026-11-08, Claude's provisional picks). `hints = mask` (vanilla) is an option; Kareem's note for it: a
  stone's hint can be read only once the mask is held, so in that mode hints must stay useful from the point the
  mask is obtained (no hints about items the player must already have collected to get the mask).
- **D27 Boss Heart Containers hold only native floor pick-ups** (Claude, 2026-11-08, after Kareem's King Dodongo
  test; provisional as D21). `--shuffle BossHeart` (off) places only the five pick-ups the boss rooms can show
  (Heart Container, Piece of Heart, Deku Shield, Hylian Shield, red rupee), because majors on the floor crash
  (#287 signature, section 11).
- **D28 The Kokiri shopkeeper's gift holds only items no seed needs while it can be missed** (Kareem accepted
  Claude's recommendation, 2026-11-08). The gift is once-only (round 7, game-confirmed) but its vanilla window ends
  at Gohma or the castle visit; extending the window is later work.
  **Lifted 2026-11-09:** round 8's window patch keeps a shuffled gift available after Gohma and the castle
  (Kareem's late test on a copy of his ranch save); the gift may then hold any item.
- **D29 Location hints never name junk** (Kareem, 2026-11-08, Claude's recommendation). Item, `always`,
  `sometimes` and random hints name only items worth having (progression, heart pieces and containers, upgrades);
  never rupees, ammo, refills or shop items. Barren ("foolish") hints still mark empty areas. This departs from OoT
  Randomizer, whose random and `sometimes` hints can name junk.
- **D30 Bombs need the Bomb Bag and Goron's Bracelet in logic** (Kareem, 2026-11-08, Claude's recommendation). The
  remake's `Item_Bomb` requires lift grade Low, which only the Bracelet (or a higher strength upgrade) grants; Bombchus
  require none (round 7, section 30; Kareem used Bombchus without a bag). The logic follows the game; no patch.
  Patching bombs to need no strength (N64 behaviour) is a possible later option. Game-confirmed: on Kareem's 7c save the
  same bombs failed before Darunia's Bracelet and worked after it (2026-11-09).
- **D31 The Weird Egg and Zelda's Letter stay at their vanilla checks** (Claude, 2026-11-09, provisional; Kareem
  told). The remake keeps the Letter, the Chicken and the Weird Egg as variants of one inventory cell (round 8,
  section 35; Kareem's chest test lost the Egg when he took the Letter). OoT Randomizer keeps both in a seed only
  through code patches (separate owned bits, menu cycling), which RomFS-only mods (D14) cannot do. Neither item
  enters the pool or a chest; Malon and Zelda give them as in vanilla.
- **D32 Fill order: small keys before boss keys, other dungeons' items before the return kit** (Claude, 2026-11-09,
  round 8 track A). The Fire Temple has no spare chest for its first small key once a boss key takes it.
- **D33 Item type palettes are a setting, `Settings.location_type_items`** (Claude, 2026-11-09, round 8). Locations
  that can only show some items (boss hearts, floor pickups) take them from their own stage, before the general fill;
  `patch/drops.py` and `patch/freestanding.py` read it.
- **D34 The fill may swap** (Claude, 2026-11-09, round 8). When an item has no reachable location left, it takes one
  its stage filled before and the displaced item is placed next under the same rules: Archipelago's safe swap
  (`Fill.py`, MIT, credited in `NOTICE`). Only on failure, no RNG, each item name displaced at most twice. Result:
  every mode 200/200 seeds on the first attempt.
- **D35 Door of Time setting, default closed** (Kareem, 2026-11-09: "closed to match SoH"). `door_of_time` =
  closed (vanilla: the three Spiritual Stones, the Ocarina of Time and the Song of Time) | song_only | open, built in
  round 10; `free_time_travel` stays a separate option. All three modes passed a first in-game check on 2026-11-10
  (answers.md R10-DOOR-CLOSED, R10-DOOR-SONG, R10-DOOR-OPEN); the return to child with an early door is untested.
- **D36 The repository goes public, `plans/` included** (Kareem, 2026-11-10: "going public is the right move once
  we clean things up"; "keep plans public"; his commit email stays). Write and admin access stay with Kareem and his
  co-owner; others read and send pull requests. Before the flip: round 11 track A (README, `CONTRIBUTING.md`,
  templates, `docs/logic.md`), `AGENTS.md` reduced to the rules every contributor's agent needs (`51dfed2`), `main`
  protected. `plans/` stays as the maintainers' working notes (`plans/README.md`): the logic data cites it.
- **D37 A UI base: local web front end, styled after Hookshot's in-game menu.** Toolkit proposed by Claude,
  2026-11-10 (Kareem can overturn): HTML, CSS and JavaScript with no build step, a standard-library server on
  127.0.0.1, shown through `pywebview` (BSD-3-Clause, optional extra) or the browser; Qt is excluded by rule 7
  (PySide6 is LGPL). Look decided by Kareem the same day: follow the in-game menus as Hookshot's own menu does, kept
  clean. Flat colours only: nothing from the game's art or fonts, no code or image from Hookshot (GPL-3.0). Every
  setting comes from one schema, so front ends hard-code none. Fonts (Kareem, 2026-11-10: "if there's a pick to
  make it less 'default' that's fine"; pick by Claude): no font file is bundled; titles use a Palatino-family stack
  and rows a Candara/Optima-family humanist stack, both installed with Windows and macOS, with Linux equivalents and
  generic fallbacks. Bundling an open font (SIL OFL) stays open: rule 7's licence list does not name the OFL.

## Open (only Kareem and his co-owner decide)

- **O3 Who owns which track**, and the co-owner's access to the private repo (a collaborator invite).
- **O6 Remake content:** the remake may add or move checks compared with the N64 game (e.g. what `Banc/DreamWorld`
  with 54 files is). Round 1 track B lists differences; which ones to shuffle is a product call.
