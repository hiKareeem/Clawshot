# Settings and restrictions

This is the command-line and developer reference. Start with the [README](../README.md) or
[seed-pack guide](seed-pack.md) to play. Status below distinguishes in-game observations from
implementation tests; an enabled option is not proof that every combination has been played.
Evidence: [recorded results](../plans/00-roadmap.md), [player answers](../plans/playtest/answers.md)
and [decisions](../plans/decisions.md).

## Settings strings and reproducibility

```sh
uv run python -m clawshot --shuffle Chest Shop Gift --print-settings
uv run python -m clawshot --romfs C:/Games/OoT/romfs --seed 7 --settings CS1 --out C:/Clawshot/seed-7
```

`--print-settings` prints a shareable `CS1` string and exits without opening the dump. `CS1` alone
means defaults; replace it with the complete printed string to replay custom choices. Explicit
command-line options override its fields, and `--logic name=value` overrides individual logic values.
The spoiler records both effective settings and their replay string. Use `--help` for the full CLI.

Reproduction needs the same seed, settings, generator source/version and world data. Generator
defaults are in `src/clawshot/data/settings.toml`; logic defaults are in `src/clawshot/data/world/`.
A version label alone does not identify the exact source. The generator reads an extracted RomFS;
the pack workflow additionally accepts `.nup` input. Output is changed files under `romfs/`, plus
`spoiler.json` and `play-note.md`, never a copy of the whole game.

## What enters the shuffle

`--shuffle` selects kinds; default is `Chest`. Checks excluded for unresolved access or unsafe
grants stay unchanged even when their kind is selected. Upgrade chains are always progressive,
in chests only; see [Progressive items](#progressive-items).

| Kind | Scope and acceptance |
|---|---|
| `Chest` | 165 of 184 ordinary chests; changed chest grants work in game. Includes the sign-puzzle solution chest, not its failure chest. Unresolved/repeat chests stay unchanged. Treasure Chest Game reward swap is built but untested and held; its 11 game boxes stay unchanged. |
| `Shop` | Ordinary shop shelves, native-display items only; slot swaps, restock and Castle Town purchases have in-game evidence. Refill goods stay in shops. Mask loans stay unchanged. |
| `Gift` | Eligible NPC and song gifts, including Great Fairies, Kokiri shopkeeper and all seven frog checks. These families have in-game evidence, not every individual swap. The shopkeeper's late window passed. See the unaccepted checks below. |
| `Scrub` | Four kinds of one-time Deku Scrub sale; repeat vendors unchanged. Implementation tested; not every sale has recorded in-game acceptance. |
| `BossHeart` | Eight boss-heart checks, off by default. Limited to the five native floor pickups below. King Dodongo's Hylian Shield grant/no-respawn was observed; not every combination. |
| `Freestanding` | Fourteen anchored floor Heart Pieces, off by default; same five-pickup palette. Ranch tower Hylian Shield collected/equipped with its saved Hash set; other surfaces, underwater pickup and complete reload coverage are not all verified. |

`--shuffle Token` is unavailable. Tokens, cows, dungeon completion rewards, pots, crates, loose
rupees, recovery hearts, loose keys and silver-rupee puzzles stay unchanged. Pot and ground-rupee
experiments are not seed options: grants were observed, but a thrown pot stranded and lost its
reward. Completion and recovery are not solved by a destruction flag.

The floor palette is **Heart Container, Piece of Heart, Deku Shield, Hylian Shield and red rupee**.
Major items on the floor can crash. Heart Containers from chests have no recorded in-game acceptance.

### Progressive items

Every upgrade chain is progressive, OoT Randomizer style, and there is **no setting** to turn it
off (Kareem, 2026-11-13):

| Family | Tiers, in order |
|---|---|
| Progressive Hookshot | Hookshot, Longshot |
| Progressive Strength | Goron Bracelet, Silver Gauntlets, Golden Gauntlets |
| Progressive Scale | Silver Scale, Golden Scale |
| Progressive Wallet | Adult Wallet (500), Giant Wallet (1000); the 200-rupee wallet is starting equipment |
| Progressive Bomb Bag | Bomb Bag, Bomb Bag (30), Bomb Bag (40) |
| Progressive Quiver | Bow, Quiver (40), Quiver (50) |
| Progressive Slingshot | Slingshot, Bullet Bag (40), Bullet Bag (50) |
| Progressive Magic | Magic Meter (Single), Magic Meter (Double) |

**Chests only.** A copy's chest event reads what Link owns and chooses the next tier before the
get window, so the window's name and text and the granted item are that tier; the model rising
from the chest stays the family's first tier ([section 47](../plans/03-game-data.md)). Gifts,
shops, scrubs and floor pickups cannot choose a tier, so the fill never places a copy there.
Every physical chest linked to a check must have a supported source-bound opening.
Unreviewed variants remain eligible for ordinary fixed rewards, but not progressive
copies; the generator applies that exclusion before fill rather than failing at write time.


**Native upgrades are bonuses.** Wherever a native check still gives a fixed upgrade (Darunia's
Bracelet, a Great Fairy's magic, a Skulltula wallet, a minigame bag or scale), the chests also
hold the full set of copies, one per tier, each replacing an ordinary filler item, and the logic
counts only the copies. No play order between native rewards and chests is assumed or needed.
A native reward never downgrades: where the native grant would not keep a higher tier, it is
skipped when that tier or a higher one is already owned.

**Child-strength exception.** Logic requires Darunia's native Bracelet route: his door, Zelda's
Lullaby and Saria's Song. That gift adds no copy tier; all three strength copies remain in chests
and adult strength stays copy-only. An early copy Bracelet physically works out of logic, but
logic never relies on it for child strength. Darunia stays unshuffled even with free time travel.


**Which tier.** The next tier above the highest one owned. A copy opened when its family has no
tier left (for example after a native bonus) is a **harmless leftover**: it gives the last tier
again and no tier becomes unobtainable. Progressive Strength gives child Link's Goron Bracelet
first whenever it is missing, even to adult Link, because adult gauntlets do not supersede it
across time travel (Kareem, 2026-11-12). Progressive Quiver and Slingshot give their weapon first,
then capacity; a fixed bag upgrade alone is not the weapon. Progressive Magic gives the double
meter once Link has any magic, including the meter a spell, the Lens of Truth or magic arrows
open. Logic counts only copies: the Nth copy is tier N ([logic reference](logic.md)).

**Names.** Hints, `spoiler.json` and `play-note.md` name the family ("Progressive Hookshot"),
never a tier. The spoiler's `progressive_grants` and the note's Progressive items table list each
copy's tiers in order and the tier it gives in one canonical replay of the seed's search spheres,
marking leftovers. That depends on collection order: it is not a play order and not a promise for
another route.

Status: built, with synthetic selection and presentation tests and a trace of the native chest
flows; **not yet played in game**. The in-game check runs on Longshot.

### Gifts: enabled versus held

`Gift` includes five frog song prizes contributing **Rupees (20)** each, the Storms prize and the
bug game. All seven passed the frog experiment. The two deterministic Bombchu Bowling
prizes (first win, second win, then the usual rupees) and both normal shooting-gallery prizes
are confirmed in game (`R10-MINIGAMES-CHILD-JABU`, `R10-MINIGAMES-ADULT`).
Rental weapons do not become inventory rewards. The first expert gallery wins are the only
minigame checks not shuffled yet; their tests have not run.

With `Gift` selected, the child Market Potion Shop bottle tutorial and Dampé's graveyard
digging prize give shuffled rewards. Both passed their in-game checks on 2026-11-10
(`R10-MARKET-BOTTLE-FIX`, `R10-DIGGING`). Accept the shop owner's offer by day; the shuffled
gift skips the bug-catching lesson. Without `Gift`, the free bottle and lesson stay unchanged,
and logic still counts that bottle. Digging still shows a heart prize but awards the shuffled item.
Both first-expert gallery rewards stay unchanged until tested. They contribute Rupees (20)
when released; later expert wins keep the usual 30/70-rupee payouts.

Merchant sale experiments (Medigoron, Granny, desert carpet) remain held. The Skulltula House's
10-token swap passed, with the 20-token preview observed; that does not certify the later thresholds.
The corrected 40-token reward remains held. The Weird Egg, Zelda's Letter and the adult trading items
stay at their native checks. All fourteen share one trade inventory cell that shows a single owned item,
adult items first (a child sees an owned adult item instead of the Cucco Talon must be shown), and every
adult trade hand-in shows the item the previous native trade gave, as the logic assumes. Biggoron's
final sword reward is still shuffled behind the native Claim Check.

The Gerudo Membership Card stays at the captain under every preset and setting, never in the
shuffled pool (D39). Free all four carpenters and receive it from her: the native hand-over advances
Spirit Step02, which the guards and desert gate, Training Ground and horseback archery entry NPCs
check. The logic's card rules stay unchanged. Evidence is the [static game-data trace](../plans/rounds/r13-gerudo-card.md),
not a played D39 acceptance test.

Older Gift seeds could move the card without clearing the guards. Finishing their carpenter/captain
sequence still advances the quest even if its reward differs (same static trace). Existing seed
folders and saves are not retroactively repaired.

### First ammo containers

Newly generated seed mods add a missing small bag before the shared item grant: 10-stick capacity
for Deku Sticks, 20-nut capacity for Deku Nuts, a 30-seed Bullet Bag for the Slingshot and a
30-arrow Quiver for the Bow. The ranged bags use their native full-stock grant; sticks and nuts
keep the original bundle quantity. A bag already owned, including a larger tier, is not replaced
or refilled. A bag upgrade does not grant its weapon.

This covers shared chest/shopkeeper grants, direct NPC hand-overs, successful scrub purchases and
literal source gifts; refused or cancelled purchases grant nothing. Chest Deku Sticks and the Kokiri
counter-gift Slingshot passed pickup, use and Save and Quit → Continue (Kareem, 2026-11-12).
Scrub/Goron and other companion paths have native-data/test coverage, not individual played acceptance.
Older seed folders and saves are not retroactively changed. New-game empty nut-slot initialization remains 0/20.

### Songs and chest-only evidence

With `--shuffle Chest Gift`, `--songs song` (default) keeps songs on song checks;
`--songs anywhere` releases all twelve for chest placement, subject to other destination restrictions.
Storms, Minuet and Epona have been played from chests; the rest use the shared grant path but are
**inferred, not individually verified**. Songs can show a stand-in model. Both chest ocarinas work
but show no model; the Ocarina of Time plays songs. Din's Fire and Adult's Wallet have chest evidence.
Other gift actors remain subject to the sourced chest allowlist and destination holds, not blanket
permission for every gift to go in a chest. Authoritative restrictions: `data/settings.toml`.

Shuffled ocarinas come from chests or story scenes, not ordinary gifts, minigame prizes,
frog rewards, digging rewards or Deku Scrub purchases. This avoids a crash when receiving them.

## Shops and scrub prices

| Option | Behavior |
|---|---|
| `--shop-prices vanilla` | Default: original slot prices. |
| `--shop-prices affordable` | Exactly 10 rupees for each selected shuffled shelf. |
| `--cheap-deku-shield` | Provisionally on: an actual Deku Shield in Kokiri shop costs 10 even without Shop shuffle. |
| `--no-cheap-deku-shield` | Disables that independent discount. |
| `--shop-slots 0..8` | Default 8: first N native shelf indices in each ordinary shop; remaining stock unchanged. |
| `--scrub-prices vanilla` | Default: retain the supported one-time sales' 40/100-rupee fees. |
| `--scrub-prices fixed --scrub-price 10` | Exact selected fee, range 0–1000, for the four supported shuffled once-sales only. |

Exact prices replace conditional discounts. Affordable prices affect selected shelves only; the
independent cheap shield rule still applies with zero shuffled shelves. Logic uses the patched wallet
requirement and the native 200/500/1000 wallet capacities, retaining release, refill and adult-only
gates. These fields replay through CS1. The 10-rupee Kokiri shield/nuts purchase and restock were
observed (R6-PRICES); partial shelves and fixed scrub fees are built/tested, not independently
certified in game by that observation.

## Forest and fast start

`--forest closed` is the vanilla-like default: Mido guards the Deku Tree and the bridge exit stays
closed until Gohma. `closed_deku` opens just the bridge; `open` also bypasses Mido. The bridge-only
option has in-game evidence with Mido still blocking (R6-CLOSEDDEKU). Mido skip and fast start also
have recorded in-game results. Legacy `--skip mido` aliases `--forest open`; conflicting explicit
forest choices are refused. Forest flags compose with gift save flags.

The opening-movie skip is on by default. It removes the movie entirely, not just its skip-button
restriction; Navi waking Link and normal new-game initialization still run. Movie removal
**passed Kareem's new-game check on 2026-11-12**. `--skip intro saria deku_tree kaepora`
selects fast-start skips; `--skip` alone disables them. These are separate from shuffled kinds.

The Kaepora skip also marks the skipped first-field panorama complete, ending its native
music-suppression window. The previous preset could leave Hyrule Field silent during the day.
This changes **new games only**, not existing saves. Kareem verified the repaired field
music and the story/escape checks on Longshot on 2026-11-13
([section 46](../plans/03-game-data.md#46-round-14-child-story-and-field-music)).

Every new seed enables the D-pad HUD shortcuts from the start, independently of fast-start
choices (including `--skip` with no selections): **Navi, Ocarina, Boots and Masks**.
This sets the saved `ActionGuide_IsEnd.Navi` initial value; it does not grant an item or
complete a story quest. Intro/Saria/Deku-talk skips alone do not set it. Kareem verified
the HUD after the first Boomerang pickup, before entering the Deku Tree, and after
Save → title → Continue on 2026-11-12. Boomerang and ordinary items use the right-bumper
item menu, not these D-pad shortcuts. Existing saves are not migrated.

Skipping the Deku Tree's talk does **not** bypass kept Mido: equip the Kokiri Sword and
a shield, then talk to him. His early quest state, idle schedule, Talk initialization and
blocker clear remain native; only that clear applies the skipped tree-talk state. Bypassed
Mido instead keeps the initial completed-meeting preset. Saria's skip preserves the forest
visit flag normally set by her area banner; the forest pause map opens in the same played check.
The first Mido repair **hung in game and was replaced**. Kareem verified the native-clear
replacement: normal middle position, sword-only refusal, clear after adding a shield, and
no Deku Tree talk with its mouth open. Reload also passed: after Continue, Mido's dialogue
finished normally and the Deku Tree's mouth was open. Shuffled own-dungeon map/compass
credit is a separate bug, not a failure of this map-access correction.

## Door of Time and returning to child

| Option | Requirement / effect |
|---|---|
| `--door-of-time closed` | Default, native: meet Zelda and Impa at the child castle, complete the three Spiritual Stones, then obtain the Ocarina of Time and playable Song of Time. |
| `--door-of-time song_only` | Either child ocarina and the learned Song of Time. Passed a first in-game check with the Fairy Ocarina and two stones (R10-DOOR-SONG); the opening scene still shows all three stones. |
| `--door-of-time open` | Opens the door and first-pull pedestal without items. Passed a first in-game check: open door, first pull and first-adult scenes (R10-DOOR-OPEN). |
| `--logic free_time_travel=true` | Experimental, default off: adult return before Forest completion. |

Door mode and reverse travel are independent. The default return guarantee proves an adult can
unlock return from the minimum mandatory first-pull inventory and adult checks; optional child
errands are not assumed. Early-door settings can be refused with unshuffled child-only prerequisites.
There is no automatic free-travel override. Early Zelda escape/moat story timing with an open door
still needs a player check.

**The three stones alone do not trigger Zelda's escape.** Visit the child castle courtyard and
finish Impa's send-off too: Malon's fixed Weird Egg / Chicken wakes Talon to reach that route.
Both moat rewards, Saria's song source and the closed Door of Time require the completed
courtyard/Impa sequence in logic, even if ocarinas or songs were shuffled elsewhere
(`Met Child Zelda` models DoorOfTime Step02). Zelda's Letter stays at Zelda (D31); no child-Zelda
skip or quest-precompletion patch is offered. The native-data trace is
[section 46](../plans/03-game-data.md#46-round-14-child-story-and-field-music).
Kareem passed the staged Longshot story controls on 2026-11-13, including Saria before Darunia and escape/reload.

With the return guarantee enabled, this generator cannot build Chest-only seeds with
`song_only` or `open`: its return-kit bound needs movable ocarinas and Saria's Song, but those
remain at child gifts. Validation names the fixed checks and offers a closed door or Gift
shuffle. This is a construction limitation, not proof that no physical route exists;
in particular, an unshuffled Time-song gift already requires all three stones.

An open-bridge, early-door seed can validly require adult Link before Gohma. Its play note
explains when no child-only opening guide exists instead of rejecting the beatable seed.

Free travel keeps Temple Sheik through both first-arrival scenes, then hides him until Forest quest
completion. Forest rewards remain native; Prelude follows quest completion, **not medallion ownership**.
Early return, repeated age changes, the post-Forest Prelude and the fixed first adult arrival have
recorded in-game acceptance (R9-FREE-TRAVEL, R9-PRELUDE-PATCHED, R10-FIRST-PULL-FIXED). Default stays off.
Adult song logic requires the Ocarina of Time; that age restriction comes from the game's inventory
metadata, **not a played adult Fairy Ocarina test**.

`--dungeon-items own_dungeon` keeps dungeon items in their dungeon and is the default; both UI
presets keep it. While it is set, the two chests on the Desert Colossus statue's hands cannot
hold Spirit Temple keys, maps or compasses: a generic grant there would credit the wrong
dungeon or nothing.

`--dungeon-items anywhere` (the UI choice **Small keys anywhere**) moves **small keys only**,
into shuffled chests whose access and native opening contracts permit it, including other dungeons
and the overworld. An off-dungeon key is delivered as a named chest grant; no other shuffled kind can grant one.
Boss keys (Ganon's Castle included), maps and compasses stay in their own dungeon in both
modes. With anywhere, the statue's two hand chests may hold a small key, named to its own
dungeon, so it is not lost.

Dungeon-item delivery uses the native grant where it already works: own-dungeon small keys
in small chests and all four families in big chests. Moved small-chest maps and compasses
use source-bound ownership writes; own-dungeon boss keys reuse the native boss-key action
and pickup indicator on existing actors. A get message or HUD icon alone does not prove
saved ownership. Native pickup text and unchanged placements are preserved.
Map/compass saves and pause menus, and boss-key credit, pickup indicator and normal boss-door
opening passed in-game. Boss-door reload persistence is untested: the arena prevents saving.

Previously generated seeds can lose these three items from small chests. Rebuilding a mod
does not re-award a chest already opened in an existing save.

Every physical copy of a destination must support that named opening. The Hyrule Field heart-piece
chest does not have a played named-key opening contract, so it cannot hold an off-dungeon small key.
It remains shuffled for other eligible rewards; it has not been enabled by assuming it opens like another chest.

A key found outside its dungeon names that dungeon in both pickup messages — for example
"Small Key (Forest Temple)" and the caption "Opens one locked door." / "Dungeon: Forest Temple" —
in English in all 16 language archives; dungeon names are read from your dump, not bundled with Clawshot.
There is no new in-game key list: the standing HUD, pause-map counters and floating notices show only the
dungeon you are in. A key credited to another dungeon can show no notice or no counter change
where you stand (in the played gates an overworld pickup showed no increment and an Ice Cavern
one no notice, both with the saved count correct); the notices do not track the key's target
dungeon. The planned Tracker tab will show keys per dungeon from that seed's own save; it is
not in this release.

Acceptance: Gates 1–4 passed in game — native and named key chests of both sizes, in-dungeon
and out, child and adult, correct remote credit, door spending and reload persistence, ending
with a whole generated anywhere seed ([round 12](../plans/rounds/r12-keys.md)). That is not every
source/target combination or a complete playthrough.

## Hints, models and age warnings

Gossip Stones give English hints in all 16 language archives. `--hints always` is the default;
`--hints mask` restores the Mask of Truth requirement. The balanced distribution includes required-route,
barren-area and item hints. Location hints never name junk. The no-mask lines and corrected highlight
reset were observed in game; that is not certification of every distribution. Both native Sheik
Hookshot-direction lines are replaced with a seed location holding the Hookshot or a Progressive
Hookshot (any copy is the Hookshot while none is owned), or omit the tool if none exists in a
partial world. This text is built/read-back-tested, not separately player-accepted.

**Wrong-age pickups:** the note lists shuffled age-locked rewards reachable by the wrong age at their
first search frontier, including ties. Optional later pickups can differ from that order. Progressive
Hookshot, Quiver and Slingshot warn like their weapon, which any copy can give.
New games initialize the native small Nut Bag and zero Deku Nuts (0/20); Kareem verified a child
Bow-first pickup followed by working Boomerang use without reloading on 2026-11-12.
Existing saves are unchanged: in saves started with older builds, Save and Continue before using
other items after an age-unusable reward. Changing areas does not clear that older item-bar jam.

Changed rewards omit the old item's acquisition-only Navi reaction. Where that reaction
shares a wrapper with room or quest progress, a source-bound clone removes only the stale
comment and retains the story writes. Native unchanged rewards retain their original event.

On Hookshot 2.0.12+, clear `HOS_FS_OVERLAY` and load through mods; the old overlay route crashes.
The game's Switch button icons then appear in ordinary text; the separately drawn ocarina note
interface keeps its own controller prompts. See [loading instructions](seed-pack.md).

## Developer layout

Python 3.12+ with uv; rationale and product choices: [decisions](../plans/decisions.md).

| Path | Responsibility |
|---|---|
| `src/clawshot/formats/` | BYML, SARC, zstd dictionaries, EVFL, MSBT and resource size table |
| `src/clawshot/census/` | Finds locations in the player's dump |
| `src/clawshot/world/` | World loader, rule language and search |
| `src/clawshot/data/world/` | Regions, items, helpers, settings and remake overrides |
| `src/clawshot/generate/` | Fill, spoiler and play-note generation |
| `src/clawshot/patch/` | Changed-resource plans and writer |
| `src/clawshot/pack/` | Source-only seed packs and local dump handling |
| `tests/` | Synthetic fixtures; tests marked `dump` need `OOT_ROMFS` |
| `plans/` | Architecture, format specification, evidence and decisions |

For porting, see [logic reference](logic.md). Credits: [NOTICE](../NOTICE), including OoT Randomizer
`526b4c8d` and Archipelago `Fill.py` at `1041167c` (`generate/fill.py` safe swap). Licence: [MIT](../LICENSE).
