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

## Settings strings

```sh
uv run python -m clawshot --shuffle Chest Shop Gift --print-settings
uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 7 --settings CS1 --out E:/OOTRemake/work/my-seed
```

`--print-settings` prints a shareable `CS1` string and exits without opening the dump. Pass it to `--settings`;
explicit command-line options override its fields, and `--logic name=value` overrides individual logic values.
`--skip` alone disables fast start. The spoiler records both settings and their replay string.
Reproduction requires the same seed, generator version and world data. Generator defaults are in
`src/clawshot/data/settings.toml`; logic defaults are in `src/clawshot/data/world/`.

With `--shuffle Chest Gift`, `--songs song` (default) keeps songs on song checks; `--songs anywhere` allows
all twelve songs in chests. Only Storms has been played from a chest; the other eleven share its grant path
and are inferred. Other gift-only items remain on gifts until individually observed in a chest; the sourced
allowlist in `settings.toml` currently permits the Fairy Ocarina.

`--shop-prices vanilla` (default) keeps original slot prices; `affordable` makes every shuffled shop item
exactly 10 rupees. `--cheap-deku-shield` (provisionally on) prices a Deku Shield in Kokiri shop at 10 even
without Shop shuffle; `--no-cheap-deku-shield` disables it. Exact prices replace conditional discounts.
The logic uses the patched wallet requirement, preserving stock releases, refill gates and adult-only offers.

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
