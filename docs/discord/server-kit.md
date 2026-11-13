# Clawshot Discord kit (drafts for Kareem to post)

Drafts for Kareem to review and post himself; editing this file does not publish a message.
The repository and source-containing seed packs are **public test builds**. Share the pack zip,
never a generated `seed` folder, cache or save. Full instructions: [seed-pack guide](../seed-pack.md).
Permanent invite: **https://discord.gg/7R5ZXPcJqn**.

---

## Channel topics

- **#announcements**: Progress updates and new seed packs. Read only.
- **#seeds**: Seed packs to play. Each pack builds the seed from your own copy of the game; no game files are shared here.
- **#playtest-reports**: One thread per report. Use the template in the pinned message.
- **#logic-questions**: Open questions about what the remake allows (can you do X with Y). One thread per question.
- **#help**: Setup problems, stuck in a seed, Hookshot or Longshot questions.
- **#dev**: Code, data and planning talk.
- **#general**: Everything else.

---

## Rules

1. Bring your own game. No ROMs, romfs files, keys, or saves from someone else's copy, and no links to any of them.
   Seed packs never contain game files; every seed is built from your own dump on your own PC.
2. No piracy talk, including "where do I get the game files".
3. Public test packs may be shared as their original zip. Never share a generated seed folder,
   extracted cache, decoded game data, keys or saves.
4. Reports and logs are welcome. Attach only the whole game log; it contains folder paths and your user name, but no game data.
5. Use spoiler tags for item locations, or keep them in the report thread.
6. If something also breaks without Clawshot, it's probably the game runtime. Report Longshot problems in
   Longshot's issue tracker (git.magicbean.dev/MagicBeanDev/Longshot). Hookshot's GitHub repository has been
   offline since 2026-11-13.
7. Be decent to each other.

---

## Pinned in #playtest-reports: report template

```
Clawshot version (zip folder name, or Clawshot-<version>: at the start of the settings):
Seed number and whole settings string (inside single backticks, or use Copy for Discord):
Hash (Generate's Seed ready panel, or beside the seed in My seeds):
Hookshot or Longshot version (Hookshot: first line of hookshot_log.txt; Longshot: the "longshot v..." line near the top of longshot_log.txt), or emulator name/version:
Operating system:
Where you were (area, child/adult Link) and what Link was doing:
What you expected:
What happened:
Attach only the whole hookshot_log.txt or longshot_log.txt: output folder, beside seed and user; pack folder for seed packs.
Emulator players: attach only the emulator's log instead.
Nothing else attached: never game files, seed folders, saves, keys, caches or spoilers.
```

The game log contains your folder paths, including your user name, but no game data. Those paths will be public.
Settings strings use `_` and `-`: without single backticks around them, Discord turns text between two `_` into
italics and drops the `_`, and the string stops working. **Copy for Discord** in the UI adds the backticks.

---

## Pinned in #logic-questions

Each thread is one question about what the remake allows, like "can the Boomerang hit the switch in the Slingshot
room?" If you know the answer, reply with the exact steps and what you saw. Answers from
real play can correct the logic: the Boomerang in the Deku Tree, the shallow castle moat and bombs
needing Goron's Bracelet already have recorded answers. Temple Sheik follows Forest quest completion,
not medallion ownership alone. Say what was observed, inferred or still untested.

---

## Pinned in #seeds: how to play a seed pack

You need:
- your own legally dumped copy of the supported game update (build `e0f3ccfa`; the pack checks it);
- [uv](https://docs.astral.sh/uv/getting-started/installation/), with internet for the first dependency setup;
- Hookshot or Longshot for Play, **or** an emulator for the loading steps below. Neither is needed for Make.
  Longshot: https://longshot.magicbean.dev/download (its launcher builds the game from your own dump).

Steps:
1. Install uv, then download the public test pack zip. Extract it into its own new folder **outside**
   RomFS and your Hookshot or Longshot folders. Never extract over an older pack; each folder has its own saves.
2. Run `Make seed.bat`. It asks for your **full `.nup` filename or extracted RomFS folder** and an
   **optional** Hookshot or Longshot folder (the game folder containing `bin`, or your Longshot Launcher
   folder). Leave it empty for an emulator.
   Make fingerprints the supported dump before generation, builds locally from the included source,
   settings and seed, then checks every output byte against the pack's reference digest.
   NUP input may need uv/Python dependencies installed before that version check.
   Existing seeds are verified, never overwritten; nothing is written to your game folder.
3. After **Verified seed**, use a current pack's `Play seed.bat`. It verifies again and starts only
   `bin\hookshot.exe` or `bin\longshot.exe`, with that game's update check off, `HOS_FS_OVERLAY` cleared and
   the made seed loaded **as a mod through `HOS_MODS`**, using this pack's isolated `user` folder. Missing
   bin or missing mod-loader support must stop Play, never fall back to the root launcher or vanilla game.
   Start a new game the first time; later plays continue this pack's saves. Longshot v3.0.0-rc.2
   passed Kareem's Windows app Play check on 2026-11-13: isolated saves/options, shuffled rewards and reload.
4. **Old overlay launchers crash on Hookshot 2.0.12+.** Use a newly built pack and the
   [current seed-pack guide](../seed-pack.md), not a zip or launcher from before the loading change.
   Hookshot 2.1.0 shows Switch icons in ordinary text while a seed is loaded.
   Longshot v3.0.0-rc.2 kept Xbox prompts correctly in Kareem's app check.
5. `seed/play-note.md` and `seed/spoiler.json` reveal item locations; open them only if you want spoilers,
   and keep them local. Ask in #help for one location if you want less of a spoiler.
   Reports need the seed/settings, hash, Clawshot version, runtime/version, OS, steps and the whole game log.
   Paste settings strings inside single backticks.

For manual mods-folder loading follow the guide: **it uses the game's normal saves**. Back up first.
Hookshot: a new game there overwrites that playthrough. Longshot: copy `seed\romfs` to
`<game folder>\mods\Clawshot-seed-<number>\romfs`, start a New Game in an empty slot, and remove that
folder before playing your normal saves, because the mod applies to every slot. Pack save isolation does
not apply. The proof a changed file loaded on current Hookshot is `mods: <file> <- <path>`, plus the game
result; Longshot's `longshot_log.txt` names each mod and the files read from it.

Version/digest mismatch: stop and post the actual/expected fingerprints in #help. Do not bypass it.
Partial/modified build: extract the original zip into a new folder, keeping the old folder and its saves.
Code is included for inspection. Share the source-only zip, never its locally generated seed or cache.

### Playing in Lichii instead of Hookshot or Longshot

Kareem confirmed seed8 loads and plays on **Lichii (Eden/yuzu family)**. Install uv, extract the pack and
run **Make seed** as above, providing your `.nup` filename or RomFS and **leaving the game folder empty**.
No Hookshot or Longshot installation is needed. Wait for Verified seed, then follow these steps; do not run Play.

1. **Back up the emulator's saves for this game before starting.** A **New Game** for the seed takes over
   this game's emulator save slots; the pack's `user` folder does not isolate emulator saves.
2. Copy generated `seed\romfs` to
   `%APPDATA%\eden\load\0400486024DEC000\<mod name>\romfs` (no extra nested `romfs`).
3. Tick the mod in the game's **Properties > Add-ons**, launch in Lichii, and start New Game.
4. Untick the mod to play normally. Restore your backup if you want the old save progress;
   unticking does not undo changes to saves.

For emulator reports, give its name/version and attach only its own log;
there is no Hookshot or Longshot log when Play was not used. Paste the seed number and settings from
`pack.json`, the settings inside single backticks.

**Untested:** Ryujinx `mods/contents/0400486024dec000/<name>/romfs`;
Atmosphere `atmosphere/contents/0400486024DEC000/romfs`. Those layouts are not confirmation that
Clawshot works there. Keep backups, and never share generated overlays.

---

## First post in #announcements

Clawshot is an unofficial item randomizer for the Switch 2 Ocarina of Time remake. The repository and
seed packs are public test builds, not a finished randomizer. You build each seed from your own dump;
no game files are included or shared. Invite: https://discord.gg/7R5ZXPcJqn.

What has in-game evidence:
- Changed chest rewards and shuffled native shop purchases work. Unresolved/repeat checks stay unchanged.
- NPC gift swaps, Great Fairies, the Kokiri shopkeeper's extended gift window and all seven frog checks
  have passed experiments, not every possible reward combination.
- Optional boss-heart and floor-heart-piece replacements use only native floor pickups; a Hylian Shield
  was observed at King Dodongo and the ranch tower. Other locations/pickups are not all verified.
- Gossip Stone hints without the mask, fast start, the forest option that opens only the exit bridge
  (`--forest closed_deku`) and cheap Kokiri prices have been observed. Experimental free time travel
  is off by default; early return, Prelude
  and the corrected first adult arrival have passed checks.

The two Bombchu Bowling prizes and both normal shooting-gallery prizes are confirmed in game
(`R10-MINIGAMES-CHILD-JABU`, `R10-MINIGAMES-ADULT`). The first expert gallery wins are the only
minigame checks not shuffled yet; their tests have not run. Four kinds of one-time Deku Scrub
sale are enabled; not every shuffled sale has recorded acceptance.

With Gift shuffle, the child Market Potion Shop bottle tutorial and Dampé's graveyard digging
prize now give shuffled rewards. Both passed their in-game checks on 2026-11-10
(`R10-MARKET-BOTTLE-FIX`, `R10-DIGGING`); the corrected shop swap passed re-entry and shopping.
Digging still shows a heart prize but gives the shuffled item. First expert gallery rewards,
merchant experiments and some Skulltula House rewards stay unchanged until tested.
The Door of Time's song-only and open modes passed a first check each.

Tokens, cows, dungeon completion rewards, pots, crates and loose rupees are not shuffled. Small
keys can leave their dungeon only through the opt-in **Small keys anywhere** choice (any shuffled
chest, named to the key's own dungeon; boss keys, maps and compasses always stay home); wider
keysanity, entrance shuffle and Archipelago are not supported for play. All eight upgrade chains
are always progressive; copies are chest-only. Native tier name/text and grant follow ownership,
while the rising model stays the base item. This progressive route is built and data-tested,
not yet player-accepted; its staged check uses Longshot. See the [README](../../README.md) and
[settings reference](../settings.md) for exact limits.

New games initialize an empty nut slot (0/20); child Bow first followed by Boomerang use without a
reload passed Kareem's 2026-11-12 check. Saves started with older builds are unchanged: after an
age-unusable pickup, Save and Continue before using other items; changing areas does not clear that jam.
Known issues: ocarinas from chests have no model despite working; songs may use a stand-in. Hookshot 2.0.12+
loads seeds as mods, not through the crashing overlay route; Hookshot 2.1.0 text uses Switch icons.
Play also supports Longshot (https://longshot.magicbean.dev/download). Its v3.0.0-rc.2 app check passed
on 2026-11-13, including game options, Xbox prompts, shuffled rewards and save/reload.
Paste settings strings inside single backticks (or use Copy for Discord): Discord drops their `_` otherwise.

Full disclosure: Kareem directs AI coding agents building Clawshot. Automated checks test formats,
logic and output; Kareem performs in-game acceptance. Untested work is labelled, not called proven.
We welcome testers, remake route evidence and small contributions under the MIT licence.

Read the rules and seed-pack guide first. Share the pack zip, **never the generated seed folder**.
