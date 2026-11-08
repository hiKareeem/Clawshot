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
  Claude's recommendation). Ammo packs grant their missing container (round 6, section 24; game-confirmed for a
  shop bomb bundle in a chest, which gave the Bomb Bag with 20 bombs). Default: a `Bombs (N)`/`Bombchus (N)` item
  goes only to a location the logic cannot reach without the Bomb Bag, so a pickup never hands out an early bag.
  Counting such pickups as extra Bomb Bags is a later advanced option. Shop refills stay in shops.

## Open (only Kareem and his co-owner decide)

- **O3 Who owns which track**, and the co-owner's access to the private repo (a collaborator invite).
- **O6 Remake content:** the remake may add or move checks compared with the N64 game (e.g. what `Banc/DreamWorld`
  with 54 files is). Round 1 track B lists differences; which ones to shuffle is a product call.
