# Clawshot

An unofficial item randomizer for *The Legend of Zelda: Ocarina of Time* on Nintendo Switch 2,
inspired by OoT Randomizer and Ship of Harkinian's randomizer.

Clawshot reads **your own game dump**, moves items according to access rules, and writes a
RomFS mod: a folder of changed game files loaded instead of the originals. The supported game is
program `0400486024DEC000`, update v131072, build `e0f3ccfa`.

**This is not the game.** This repository contains code, logic and location definitions, not game
files, keys or generated mods. You must generate the mod locally from your own dump. Never share
that output. Clawshot is not affiliated with or endorsed by Nintendo.

## At a glance

- **Shuffled now:** chests, shop shelves, NPC gifts and songs, one-time Deku Scrub sales.
- **Optional:** boss Heart Containers and floor Heart Pieces.
- **Not shuffled yet:** Gold Skulltula tokens, cows, dungeon rewards, pots, crates, loose rupees,
  or keys outside their dungeon.

Choose the kinds you want; the default shuffles chests only. Some checks stay unchanged pending
in-game tests; the evidence and limits are below.

## Status

**Public test builds, not a finished randomizer.** Seeds are being played and the remake's access
rules are still being checked. Every generated seed must pass the logic search before it is written;
that proves the model, not that every route has been verified in the game.

| Feature | Current evidence and limits |
|---|---|
| Chests | Changed chest rewards work in game. 165 of 184 ordinary chests are shuffled; unresolved routes and repeat rewards stay unchanged. The Goron City sign-puzzle solution is included, its failure chest is not. |
| Shops | Shuffled native shop items and purchases work in game. Arbitrary major items cannot use a stand-in shelf display. |
| NPC gifts and songs | Gift swaps and Great Fairy once-only rewards work in game, as does the Kokiri shopkeeper's extended gift window. All seven frog checks have passed their in-game experiment. Not every gift or item combination has been played. |
| One-time Business Scrubs | Four kinds of one-time Deku Scrub sale are enabled; repeat vendors stay unchanged. The implementation is tested, but the recorded results do not establish every shuffled sale in game. |
| Boss hearts and floor Heart Pieces | Optional, off by default. A Hylian Shield worked at King Dodongo and the ranch tower. Only native floor pickups are allowed; other locations and pickup combinations are not all verified. |
| Hints and convenience options | Gossip Stones speak hints without the Mask of Truth by default; this, fast start, the forest option that opens only the exit bridge (`--forest closed_deku`) and 10-rupee Kokiri prices have in-game evidence. |
| Free time travel | Experimental, off by default. Early adult return, the Prelude scene and the corrected first adult arrival have passed in-game checks. |

**Implemented, not yet accepted in game:** deterministic first/second Bombchu Bowling prizes and
the child shooting-gallery prize are enabled with gift shuffle but await their player checks; the
adult gallery prize passed its check.

**New with Gift shuffle:** the child Market Potion Shop bottle tutorial and Dampé's graveyard
digging prize now give shuffled rewards. Both passed their in-game checks on 2026-11-10
(`R10-MARKET-BOTTLE-FIX`, `R10-DIGGING`). The shop's corrected swap passed re-entry and shopping;
Dampé still shows a heart prize but gives the shuffled item.

First expert gallery rewards, merchant experiments and some Skulltula House rewards stay
unchanged until their tests pass; the 10-token swap alone has been observed, not every threshold.
The Door of Time's song-only and open modes each passed a first in-game check (the door and
first sword pull); returning to child afterwards is untested.

Gold Skulltula tokens, cows, dungeon completion rewards, pots, crates and loose rupees are not
shuffled. Keysanity (dungeon items outside their own dungeon) has no in-game acceptance; do not use
it for a playthrough. Progressive items, entrance shuffle and Archipelago are not supported.
See [settings and restrictions](https://github.com/hiKareeem/Clawshot/blob/main/docs/settings.md) for the detailed reference.
Evidence: [recorded results](https://github.com/hiKareeem/Clawshot/blob/main/plans/00-roadmap.md)
and [playtest answers](https://github.com/hiKareeem/Clawshot/blob/main/plans/playtest/answers.md).

### Known issues

- **After receiving an item Link cannot use at his current age, Save and Continue before using
  other items.** A child Bow pickup jammed the item bar on both Hookshot and Lichii; changing areas
  did not fix it. Other item families carry precautionary warnings. Read this seed's `play-note.md`.
- Chest ocarinas show no model despite working; songs can show an ocarina stand-in rather than a
  normal item model. Only some songs have been individually played from chests.
- **Hookshot 2.0.12 and later: use a current pack's `Play seed.bat`,** which loads the seed as a
  Hookshot mod. Packs built before 2026-11-10 used Hookshot's older overlay loading
  (`HOS_FS_OVERLAY`), which now crashes at start-up; rebuild the pack from current source.
  While a seed is loaded, button icons in text show Switch buttons instead of your controller's.
- A Market guard-house crash on Hookshot 2.0.11 matched the upstream
  [Hookshot issue #1112](https://github.com/NotRexed/Hookshot/issues/1112); no fix is claimed here.

## Play a seed pack

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Unzip the seed pack into **its own new folder outside your game dump and Hookshot**.
   Do not extract over another pack.
3. Run **`Make seed.bat`** and give it your own supported **`.nup` file or extracted RomFS folder**.
   For Hookshot, also give its installation folder (the one containing `bin`); for an emulator,
   leave that answer blank. Wait for **Verified seed** before playing.
4. **Hookshot:** run **`Play seed.bat`** and start a **new game** the first time. Later plays
   continue this pack's isolated saves.
5. **Emulator, instead of Play:** **back up this game's entire emulator save folder first**.
   Copy the generated `seed/romfs` into the emulator's per-game mod folder as `<mod name>/romfs`,
   enable the mod and start a new game. For Lichii, the destination is
   `%APPDATA%\eden\load\0400486024DEC000\<mod name>\romfs`; enable it in **Properties > Add-ons**.

See the **[seed-pack guide](docs/seed-pack.md)** for detailed setup, version/digest checks and
runtime troubleshooting. Packs contain the generator's source and settings, not a ready-made game
mod; Make builds it locally from your dump.

Hookshot and Lichii have recorded loading/play results; other emulator and console layouts are
**untested with Clawshot**. Use the current mod-loading instructions, not an older overlay launcher.
Keep packs in separate new folders and preserve your saves. Emulator New Game replaces this game's
save progress: back up the entire save folder first. The pack's isolated Hookshot saves do not
isolate emulator saves, and manually installing a Hookshot mod uses its normal save folder.

Questions, test packs and reports: **[Clawshot Discord](https://discord.gg/7R5ZXPcJqn)**.
Never post a dump, generated mod, cache or save.

## Run from source

Use Python 3.12+ and uv. From a checkout, generate into a **new folder outside the repository and
game dump**; never overwrite a seed that might be in use:

```sh
uv sync --frozen
uv run python -m clawshot --help
uv run python -m clawshot --romfs C:/Games/OoT/romfs --seed 7 --out C:/Clawshot/seed-7
```

The generator CLI takes an extracted RomFS folder. For `.nup` input use the seed-pack workflow.
A default seed shuffles chests. To print settings without opening the dump, then replay them:

```sh
uv run python -m clawshot --shuffle Chest Shop Gift --print-settings
uv run python -m clawshot --romfs C:/Games/OoT/romfs --seed 7 --settings CS1 --out C:/Clawshot/seed-7-defaults
```

`CS1` alone means defaults; replace it with the **complete string printed by the first command**
to replay that command's choices. Explicit options override the string. Reproduction needs the
same seed, settings, generator source and world data, not just the same version label.

The output has `romfs/`, `play-note.md` (directions and warnings) and `spoiler.json` (all placements).
Load it using the [seed-pack guide's runtime instructions](docs/seed-pack.md); generation does not
start the game. More options: [settings](https://github.com/hiKareeem/Clawshot/blob/main/docs/settings.md).
For logic ports and trackers: [logic reference](https://github.com/hiKareeem/Clawshot/blob/main/docs/logic.md).

## Development and contributions

Kareem directs AI coding agents that implement Clawshot. Automated tests check formats, logic and
output; Kareem performs the in-game checks. A behavior change is not called working in game until
he has observed it; built and untested work is labelled above. Contributions from people are welcome.
Kareem and his co-owner decide scope and merge changes.

Read [CONTRIBUTING.md](https://github.com/hiKareeem/Clawshot/blob/main/CONTRIBUTING.md)
for licensing, source restrictions, checks and evidence to
include. Start with a small, single-topic change, or discuss it on Discord. Do not submit game files
or anything generated from them, including in issues and attachments.

## Credits and licence

Clawshot is [MIT licensed](LICENSE). [NOTICE](NOTICE) lists the pinned sources and licences:
OoT Randomizer's world, rule language, search and fill; Archipelago's safe fill swap; and a55uka's
NUP reader. Their work is credited without implying endorsement. Nintendo owns the game and its
trademarks; no part of it is included here.
