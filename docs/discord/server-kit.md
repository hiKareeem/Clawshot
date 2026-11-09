# Clawshot Discord kit (drafts for Kareem to post)

Drafts only; nothing here has been posted. The repository and source-containing packs remain private
to invited testers. The implemented pack format is documented in `docs/seed-pack.md`.

---

## Channel topics

- **#announcements**: Progress updates and new seed packs. Read only.
- **#seeds**: Seed packs to play. Each pack builds the seed from your own copy of the game; no game files are shared here.
- **#playtest-reports**: One thread per report. Use the template in the pinned message.
- **#logic-questions**: Open questions about what the remake allows (can you do X with Y). One thread per question.
- **#help**: Setup problems, stuck in a seed, Hookshot questions.
- **#dev**: Code, data and planning talk.
- **#general**: Everything else.

---

## Rules

1. Bring your own game. No ROMs, romfs files, keys, or saves from someone else's copy, and no links to any of them.
   Seed packs never contain game files; every seed is built from your own dump on your own PC.
2. No piracy talk, including "where do I get the game files".
3. Keep seed packs and Clawshot builds inside this server for now. Please don't repost them elsewhere.
4. Screenshots, short clips and log files are welcome.
5. Use spoiler tags for item locations, or keep them in the report thread.
6. If something also breaks without Clawshot, it's probably Hookshot. Report it on Hookshot's GitHub.
7. Be decent to each other.

---

## Pinned in #playtest-reports: report template

```
Seed pack:
Hookshot version:
Where you were and what you did:
What you expected:
What happened:
Log: attach hookshot_log.txt from the seed folder
```

A crash report without the log is very hard to use, so please attach it even if it looks like noise.

---

## Pinned in #logic-questions

Each thread is one question about what the remake allows, like "can the Boomerang hit the switch in the Slingshot
room?" If you know the answer, reply with what you saw, and a screenshot or short clip if you have one. Answers from
real play change the logic directly; a few already have (the Boomerang in the Deku Tree, the shallow castle moat, bombs
needing Goron's Bracelet, Sheik leaving the pedestal with the Forest Medallion).

---

## Pinned in #seeds: how to play a seed pack

You need:
- your own legally dumped copy of the game, at the same version Clawshot is built against (the pack checks this);
- Hookshot set up and working with that dump;
- about ten minutes for the first setup.

Steps:
1. Install uv (it runs Clawshot's Python code). In PowerShell:
   `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. Download the private seed pack and unzip it into its own new folder **outside** RomFS and Hookshot.
   Never extract over an older pack; each folder has its own saves.
3. Run `Make seed.bat`. It asks once for both your romfs folder and Hookshot folder (the one containing `bin`).
   Before uv or generation, it fingerprints the supported game dump. It builds `seed` from the included
   source/settings, then checks every output byte against the pack's reference digest. Existing seeds are
   verified, never overwritten. Nothing is written to your game folder.
4. After **Verified seed**, run `Play seed.bat`. It verifies again and starts only `bin\\hookshot.exe`,
   with update checks disabled and this pack's `user` folder. A missing bin exe stops; no launcher fallback.
   Start a new game the first time; later plays continue this pack's saves, never your normal game.
5. `seed/play-note.md` explains the opening; `seed/spoiler.json` reveals all placements.
   Ask in #help for one location if you want less of a spoiler. Attach `hookshot_log.txt` from the pack root
   and `pack.json` to reports; never share your dump, generated overlay or saves.

Version/digest mismatch: stop and post the actual/expected fingerprints in #help. Do not bypass it.
Partial/modified build: extract into a new folder, keeping the old folder and its saves.
Code is included for inspection; neither the repository nor packs are public yet. Do not repost.

---

## First post in #announcements

Hey all. This is the server for Clawshot, an item randomizer for the Switch 2 Ocarina of Time remake, running on the
Hookshot recomp. It's a mod made only of game data: no code changes, and nothing from the game is shared. You build
each seed from your own dump.

Where it stands:
- Chests, shop shelves, NPC gifts (songs, Great Fairies, the Kokiri shopkeeper and more) and one-time Deku Scrubs can
  be shuffled. Boss Heart Containers and floor heart pieces can too, for now only with items the game can already
  show on the floor.
- The logic started from OoT Randomizer's (MIT) and has been corrected against the remake, mostly by playing it. The
  remake changes more than you'd think. Bombs need Goron's Bracelet now, for example.
- Gossip Stones give hints, and they don't need the Mask of Truth.
- One settings string covers everything, so a seed and its string always build the same game.

Not there yet: Gold Skulltula tokens, dungeon rewards, entrance shuffle, cows, the trade sequences. Some items show the
wrong model when they come out of a chest (songs show an ocarina, the ocarinas show nothing), but they work.

I'm looking for a few testers who can play seed packs and send reports, and for anyone who knows the remake well
enough to answer "can you do X here" questions. Speedrunners have already settled a few of those.

Full disclosure: Clawshot's code is AI assisted. I direct and review a set of coding agents, and every change gets
tested in game before it counts.

First seed pack coming soon. Read the rules first, especially the one about game files.
