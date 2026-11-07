# Decisions

## Decided (proposed by Claude, 2026-11-07; Kareem or his co-owner can overturn)

- **D1 Python 3.12+ with uv.** OoT Randomizer and Archipelago are Python and MIT, so their logic, fill and
  multiworld code can be ported; the generator is not speed-critical. Alternative: Rust or C++ (as Ship of
  Harkinian) would be faster but loses that reuse.
- **D2 Output is a folder of changed game files.** Works with Hookshot today and with emulators; code hooks come
  later and stay optional.
- **D3 Own BYML, SARC and zstd-dictionary code.** The existing Python libraries for these formats are GPL-2.0;
  writing our own (the reader is ~120 lines) keeps every license option open.
- **D4 Location IDs are (file, actor Hash).** Stable across tools and settings.
- **D5 Location definitions are committed, game files never are.** Definitions are identifiers and names, as OoT
  Randomizer's location list is.

## Open (only Kareem and his co-owner decide)

- **O1 Name.** Candidates checked for collisions on 2026-11-07: Longshot (PyPI taken), Gaebora, Lost Woods,
  Gossip Stone (all free).
- **O2 License.** GPL-3.0 (as Hookshot) or MIT (as OoT Randomizer and Archipelago).
- **O3 Who owns which track**, and how the co-owner gets access to the private repo.
- **O4 Archipelago from the start**, or after M2.
- **O5 Runtimes:** Hookshot only at first, or emulators too from M2.
- **O6 Remake content:** the remake may add or move checks compared with the N64 game (e.g. what `Banc/DreamWorld`
  with 54 files is). The census will list differences; which ones to shuffle is a product call.
