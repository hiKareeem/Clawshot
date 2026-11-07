# Roadmap

## M0: scaffold and day-1 risk check (one agent)

The riskiest dependency is writing the game's files back so the game accepts them.

1. uv project, `src/` layout, ruff, pytest with a `dump` marker.
2. `formats/zsdic`: open `Pack/ZsDic.pack.zs` (plain zstd around a SARC with `zs.zsdic`, `bcett.byml.zsdic`,
   `pack.zsdic`, `bkprb.zsdic`); decompress and compress `.zs` files with the right dictionary.
3. `formats/byml`: BYML v7 little-endian reader and writer. Starting point: the reader in
   `E:\OOTRemake\work\spike_banc.py` (node types seen: 0xC0 array, 0xC1 map, 0xA0 string, 0xD0 bool, 0xD1 int,
   0xD2 float, 0xD3 uint, 0xD5 u64; hash maps 0x20/0x21 handled but not yet seen). Synthetic fixtures for every type.
4. Round-trip every `Banc/**/*.bcett.byml.zs` (160 files) under `-m dump`.
5. `tools/swap_one_chest`: write one Kokiri Forest chest with a different `Dynamic.Drop__DropActor` into an
   output folder at the same relative path.
6. **Risk check, with Kareem:** set `HOS_FS_OVERLAY=<output>` in `E:\Games\Hookshot\hookshot_env.txt`, open
   that chest, record the result. Also record whether a file that grew needs a resource-size table entry
   (`RSDB`/RESTBL in Tears of the Kingdom).

Acceptance: round-trip test green over the whole dump; the swapped item comes out of the chest in game; both
results written into `decisions.md`.

## M1: check census (after M0; parallel tracks)

| Track | Owns | What | Done when |
|---|---|---|---|
| A formats | `formats/` | EVFL (event flows: NPC gifts, songs), MSBT in `Mals` (item-get and hint text), resource size table | round-trip over every file of each kind in the dump |
| B census | `census/` | every check: chests (deduplicate child/adult copies by `Hash`; find the contents of the 41 chests with no `Drop__DropActor`), freestanding items, shops, Gold Skulltulas, scrubs, NPC and song gifts | a location table the generator can load, every vanilla item accounted for, compared against OoT Randomizer's location list with differences listed |
| C logic | `world/` | port OoT Randomizer's region graph and requirements to the rule format; map its locations to the census IDs | the vanilla placement passes the beatability search |
| D Hookshot | `E:\OOTRemake\Hookshot` (upstream PRs) | a `mods\` folder loader (`hos_mods_init` is already called at boot and stubbed in `host/mkw_glue.c`) | merged upstream, or the PR open with a test build |

Day-1 numbers from the spike (raw placements, not deduplicated): 267 chests in 72 files; 41 without a drop
parameter; major items found in chests include the Hookshot, Longshot, Megaton Hammer, Bow, Slingshot, Boomerang,
Iron and Hover Boots, Lens of Truth, Kokiri Sword, Mirror Shield, Ice Arrows and both gauntlets.

## M2: first playable seeds

Chest-only shuffle with logic, spoiler log, settings string. Kareem and his co-owner play a seed start to finish.

## M3: the rest of the shuffle

NPC and song gifts, shops, scrubs, Skulltula tokens, item-get text and Gossip Stone hints.

## M4: code features (need Hookshot hooks)

A code-hook API upstream in Hookshot; then progressive items, arbitrary item models, entrance shuffle.

## M5: Archipelago

An Archipelago world (generation) and a client in the Hookshot runtime.

## Later

Emulator support beyond a plain romfs mod; a settings GUI; race seeds.
