# Clawshot

An item randomizer for *The Legend of Zelda: Ocarina of Time* on Nintendo Switch 2 (program `0400486024DEC000`,
update v131072, build `e0f3ccfa`), in the spirit of OoT Randomizer and Ship of Harkinian's randomizer.

**What it is:** a generator that reads the player's own copy of the game, places items by logic, and writes a mod
folder in the layout emulators use (`<mod>/romfs/...`). Anything that loads romfs mods can run a seed: Switch 2
emulators (including their PS5 builds), the [Hookshot](https://github.com/NotRexed/Hookshot) PC port
(`HOS_FS_OVERLAY` today, its `mods` folder once that lands), and other native ports that read the game's files
from disk. Features that need code changes come later and only where a runtime offers hooks.

**What it is not:** a copy of the game or any part of it. The repository holds code, logic and location
definitions only. Nothing generated from the game is committed or shared; players run the generator on their own
dump. Not affiliated with or endorsed by Nintendo.

## Status

Day-1 spike done (see `plans/00-roadmap.md`, M0): the game's placement files decompress and parse (BYML v7, the
same engine as Tears of the Kingdom), and chest contents are a single actor-name parameter. Writing files back and
a swapped chest in game are next.

## Stack

Python 3.12+ with uv. Reasons and alternatives: `plans/decisions.md`.

## Layout (planned, built in M0)

| Path | What |
|---|---|
| `src/clawshot/formats/` | BYML, SARC, zstd dictionaries, later EVFL, MSBT, resource size table |
| `src/clawshot/census/` | finds item locations in the player's dump |
| `src/clawshot/world/` | regions, locations, logic (data files + loader) |
| `src/clawshot/generate/` | fill, spoiler log, overlay writer |
| `tests/` | unit tests on synthetic fixtures; `-m dump` tests need `OOT_ROMFS` |
| `plans/` | roadmap, architecture, decisions |

## License

MIT (`LICENSE`), like OoT Randomizer and Archipelago. Code ported from other projects is credited in `NOTICE`.
