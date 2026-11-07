# Architecture

## Principles

- The generator is a pure function: (player's dump, seed, settings, generator version) -> output folder.
- Output is a folder of replacement game files at their romfs-relative paths. Hookshot reads it through
  `HOS_FS_OVERLAY`; an emulator reads it as a romfs mod. Only files that changed are written.
- Code-level features wait for a hook API in Hookshot (M4) and stay optional, so data-only seeds keep working
  on any runtime.

## Data the game keeps (verified on the dump unless marked)

| romfs path | Holds | Use |
|---|---|---|
| `Pack/ZsDic.pack.zs` | zstd dictionaries | read and write every `.zs` |
| `Banc/<Area>/*_{Child,Adult}_{Static,Dynamic}.bcett.byml.zs` | actor placements: `Gyaml`, `Hash`, `SRTHash`, `Translate`/`Rotate`/`Scale`, `Phive`, optional `Dynamic` params | chests (`Obj_TBox_*`, contents `Dynamic.Drop__DropActor`), freestanding items, drops in pots, grass and rocks |
| `Event/EventFlow/*.bfevfl.zs` (915) | event scripts | NPC gifts, songs (unverified) |
| `GameData/GameDataList.Product.110.byml.zs` | game flags | checks collected, logic state (unverified) |
| `Mals/<lang>.Product.110.sarc.zs` | message text | item-get and hint text (unverified) |
| `RSDB/*.rstbl.byml.zs` | resource tables | sizes of changed files (unverified) |
| `Logic/*.ainb`, `Sequence/*.ainb` | node graphs | scripted gating (unverified) |

## Layers

1. `formats`: bytes <-> trees. No game knowledge.
2. `census`: trees -> location table (IDs, vanilla items, area, age).
3. `world`: regions, exits, locations, rules (data files); a rule evaluator over a player state.
4. `generate`: settings -> item pool -> assumed fill with the beatability search -> spoiler log -> patch plan ->
   overlay writer (through `formats`).

A layer imports only from layers above it in this list.

## The beatability search (the logic oracle)

From the start state, collect every reachable location's item repeatedly until nothing new is reachable; the
seed is valid only if the goal is reached. Run on every generated seed, and on the vanilla placement as a test of
the world data.
