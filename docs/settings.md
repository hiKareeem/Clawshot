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
grants stay unchanged even when their kind is selected. Items are fixed, not progressive:
finding the Longshot first gives the Longshot. A later Hookshot did not replace it in the recorded
frog experiment (R8-FROGS), not a guarantee about every upgrade family.

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
The corrected 40-token reward remains held. The Weird Egg and Zelda's Letter stay at their native
checks because they share one trade inventory cell, rather than two independently retained items.

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

The intro skip is on by default. `--skip intro saria deku_tree kaepora` selects fast-start skips;
`--skip` alone disables them. These are separate from changing shuffled kinds.

## Door of Time and returning to child

| Option | Requirement / effect |
|---|---|
| `--door-of-time closed` | Default, native: three Spiritual Stones, Ocarina of Time and playable Song of Time. |
| `--door-of-time song_only` | Either child ocarina and the learned Song of Time. Passed a first in-game check with the Fairy Ocarina and two stones (R10-DOOR-SONG); the opening scene still shows all three stones. |
| `--door-of-time open` | Opens the door and first-pull pedestal without items. Passed a first in-game check: open door, first pull and first-adult scenes (R10-DOOR-OPEN). |
| `--logic free_time_travel=true` | Experimental, default off: adult return before Forest completion. |

Door mode and reverse travel are independent. The default return guarantee proves an adult can
unlock return from the minimum mandatory first-pull inventory and adult checks; optional child
errands are not assumed. Early-door settings can be refused with unshuffled child-only prerequisites.
There is no automatic free-travel override. Early Zelda escape/moat story timing with an open door
still needs a player check.

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
Hookshot-direction lines are replaced with the seed's actual Hookshot location, or omit the tool if
none exists in a partial world. This text is built/read-back-tested, not separately player-accepted.

**Wrong-age pickups:** Save and Continue before using other items after taking an age-unusable
reward. Child Bow jam/recovery is confirmed on Hookshot and Lichii; other families are precautionary.
The note lists shuffled age-locked rewards reachable by the wrong age at their first search frontier,
including ties. Optional later pickups can differ from that order. No data-only repair is enabled.

For rewards other than named keys, a chest that originally held a map can still play its Navi
follow-up — "Now we won't get lost" — after a different reward. Cosmetic only: the line does
not grant a map or alter saved map/key fields. Named off-dungeon key pickups omit that obsolete
comment; no broad Navi change is made for ordinary seeds.

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

For porting, see [logic reference](logic.md); for writing a seed from an Archipelago slot, see
[Archipelago slots](archipelago.md). Credits: [NOTICE](../NOTICE), including OoT Randomizer
`526b4c8d` and Archipelago `Fill.py` at `1041167c` (`generate/fill.py` safe swap). Licence: [MIT](../LICENSE).
