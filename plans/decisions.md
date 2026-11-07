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

## Open (only Kareem and his co-owner decide)

- **O3 Who owns which track**, and the co-owner's access to the private repo (a collaborator invite).
- **O6 Remake content:** the remake may add or move checks compared with the N64 game (e.g. what `Banc/DreamWorld`
  with 54 files is). Round 1 track B lists differences; which ones to shuffle is a product call.
