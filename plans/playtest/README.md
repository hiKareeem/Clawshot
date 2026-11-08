# Logic sessions

**Start with [session 1](session-1.md), just after the first Master Sword pull.**
Child sessions wait until Link can return to child. No need to finish every checklist in one sitting; stop at an area heading.
Skip a missing tool or already-consumed first-time state and tell Claude why. Never reset main progress to answer a question.

## Route cards

| Session | Start / area |
|---|---|
| [1](session-1.md) | First adult → Kakariko/Hookshot → woods/meadow → Forest Temple |
| [2](session-2.md) | Child return: ranch → Field/woods/forest → Market |
| [3](session-3.md) | Child: Kakariko by day → graves at night |
| [4](session-4.md) | Child: Trail → City/summit → Dodongo; adult tool comparisons on later return |
| [5](session-5.md) | Child: River → Domain/Jabu → Lake; earlier-state checks need preserved copies |
| [6](session-6.md) | Child with Storms: Field holes → forest/meadow → River → Well |
| [7](session-7.md) | Adult: City/Crater → Fire Temple |
| [8](session-8.md) | Adult before Morpha: River/Domain → Ice → low-water Lake |
| [9](session-9.md) | Adult Water Temple; afterwards revisit Domain for session 8's shop/shortcut observation |
| [10](session-10.md) | Adult returns/trades → Valley/Fortress; paired checks need both ages |
| [11](session-11.md) | Adult Training Ground |
| [12](session-12.md) | Adult Wasteland → Colossus |
| [13](session-13.md) | Spirit child side first, then adult side |
| [14](session-14.md) | Adult Shadow Temple |
| [15](session-15.md) | Late-sage triggers → Castle/Tower |
| [16](session-16.md) | Separate mod checks, only after main child return unlocks |
| [17](session-17.md) | Separate fresh-game early-state replays, only after main child return unlocks |

Later cards are milestones, not claims that today's save can reach them. Return visits need the listed tools.
An unused owned weapon can test a weapon-only fight; it cannot test an ownership flag. No-bracelet, no-Bomb-Bag,
pre-tentacle, untouched-grave and pre-cutscene comparisons require a real preserved state or reviewed variant.
Do not manufacture them by unequipping, and do not label them failed when that state is unavailable.

## Claude: staging and evidence

Kareem plays. Stage a disposable `--user` copy outside the repository; do not alter live saves or backup folders.
Launchers must use **`E:\Games\Hookshot\hookshot.exe` only**. No `work\hookshot-main` build or fallback (GPU device loss).
No agent starts a launcher, game, GUI or build. No overlay is needed for the normal logic route cards.

Read-only save inspection on 2026-11-08:

- New snapshot: `E:/OOTRemake/work/save-backups/2026-11-08_0802-before-adult/` is a **whole user root**
  (`save/5a3c9e1f0b7d24680000000000000001/slot_NN`), not the older flat backup layout.
  Slots 00/01/05 have Emerald, Lullaby, Saria, Sun Song, sword/shield and Zelda visit; no Ruby/Sapphire or Forest
  medallion. Forest quest complete, Fire `DodongoCavernOpne`, Water ready, Door `Step02`. This is **before adult**.
- `2026-11-07_llr-tower-before-pickup/` is flat (`slot_NN` directly). Slot 01: Forest complete, Fire `DungeonStart`,
  Lullaby/Saria, Talon game uncleared, tower-heart Hash unset, no Din Fire/Boomerang/Hookshot/Longshot.
  Use only for the isolated tower controls, not an adult session.
- `2026-11-07_1630/slot_01`: Forest complete, Fire `DodongoCavernOpne`; other slots are intro tests.
  Neither old backup is demonstrated adult-ready. Latest file timestamp does not identify main progress.
- Missing flag lookup (`None`) means unknown. Chest Hash absence does not prove unopened: chest persistence encoding
  is still unresolved (`r2-census.md:466-470`). Never reset a chest test on that assumption.

Claude needs a **new disposable checkpoint just after first pull** for session 1, then another after return travel unlocks
for child cards. Kareem is already progressing to those milestones; no agent needs to stop him or request answers twice.
Nine checks already asked on 2026-11-08 are marked pending in [questions.md](questions.md) and omitted from every route.

[questions.md](questions.md): technical targets, outcome implications, sources and deduplication.
[answers.md](answers.md): Claude's one-line-per-ID ledger (filled only after actual observation).
[prepared-mods.md](prepared-mods.md): isolated overlay/launcher instructions and prerequisite limits.
