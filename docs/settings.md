# Settings and restrictions

This is the command-line and developer reference. Start with the [README](../README.md) or
[seed-pack guide](seed-pack.md) to play. Status below distinguishes in-game observations from
implementation tests; an enabled option is not proof that every combination has been played.
Evidence: [the roadmap index](../plans/00-roadmap.md) plus the linked play records,
[player answers](../plans/playtest/answers.md) and [decisions](../plans/decisions.md).

## Settings strings and reproducibility

```sh
uv run python -m clawshot --shuffle Chest Shop Gift --print-settings
uv run python -m clawshot --romfs C:/Games/OoT/romfs --seed 7 --settings CS1 --out C:/Clawshot/seed-7
```

`--print-settings` prints a shareable `CS1` string and exits without opening the dump. `CS1` alone
means defaults; replace it with the complete printed string to replay custom choices. Explicit
command-line options override its fields, and `--logic name=value` overrides individual logic values.
The spoiler records both effective settings and their replay string. Use `--help` for the full CLI.

Native seeds accept only supported `--logic` overrides. Unchanged world defaults
remain valid; supported non-default values cover free time travel, the return
guarantee, and the derived key/forest/Mido/door modes and return-kit tables.
Prefer `--dungeon-items`, `--forest` and `--door-of-time` for those modes.
Conflicting forest/door fields are still refused. Effective return-kit fields
are regenerated from the selected mode; stored copies cannot override the world.
Versioned share-prefix checks are unchanged; this adds no cross-version import support.

Bag bombs without the Bracelet is also supported, off by default:
`--logic bombs_without_bracelet=true` (app: **Bag bombs without the Bracelet (experimental)**).
It lowers only the ordinary bag bomb's lift requirement and removes strength from the shared `Bombs`
logic predicate. The Bomb Bag is still necessary, including for Bombchus. Bomb Flowers and strength-gated
rocks keep their native requirements; this does not open Dodongo's Cavern's child entrance with bag bombs.
Kareem played it on Longshot 3.2.0 (2026-11-25): in a New Game with the Bomb Bag and Boomerang but no Bracelet,
bag bombs worked and so did the Boomerang, while Goron City's Bomb Flowers still could not be picked up. After
reloading, bag bombs still worked. Not every route the logic opens with bag bombs has been played
([played results](../plans/rounds/r22-games.md#played-results-2026-11-25-longshot-320)).

OoT-only access overrides such as `open_kakariko=open`, `gerudo_fortress=open`,
`scarecrow_behavior=free` and `skip_child_zelda=true` are refused: no native patch
makes them true. The same policy applies to CLI settings strings, app validation
and native seed generation; new imported OoT keys are not implicitly supported.
The CS1 codec and standalone logic-model APIs remain generic for research.

Reproduction needs the same seed, settings, generator source/version and world data. Generator
defaults are in `src/clawshot/data/settings.toml`; logic defaults are in `src/clawshot/data/world/`.
A version label alone does not identify the exact source. The generator reads an extracted RomFS;
the pack workflow additionally accepts `.nup` and `.nx` input. Output is changed files under `romfs/`, plus
`spoiler.json` and `play-note.md`, never a copy of the whole game.

The [Tracker's in-logic view](tracker.md#in-logic) works within these limits. It rebuilds a seed's logic from
the spoiler's settings string only when the spoiler's `generator` is this installed Clawshot version and every
location the spoiler names exists in this version's world, since one version label can cover different world
data. Otherwise in-logic is off with the reason shown and item tracking continues
([logic reference](logic.md#tracker-in-logic-contract)).

## Excluded locations

In the app, **Excluded locations** groups checks by area and supports search. Permanently held
progression sources are not offered. Selected checks never hold progression; they still receive
ordinary or priority non-progression items. Nothing is excluded by default. The CLI accepts exact world check names:

```sh
uv run python -m clawshot --shuffle Chest Gift --exclude-locations "ZR Frogs Ocarina Game" "Kak 100 Gold Skulltula Reward" --print-settings
```

`--exclude-locations` without names clears a list loaded from `--settings`. The list travels in
CS1, `spoiler.json` and `play-note.md`. Unknown names and insufficient compatible non-progression
capacity are refused with an explanation. An unshuffled progression reward cannot be excluded:
shuffle that kind or remove the check. An unshuffled non-progression reward may stay in the list.
Existing song, shop, dungeon-item, pickup-palette and delivery holds still apply; exclusions never
override those restrictions or the adult-return/beatability proofs. Fill failures name the list;
no output is written for a seed that cannot be proved. This changes generation only, not the game.

## What enters the shuffle

`--shuffle` selects kinds; default is `Chest`. Checks excluded for unresolved access or unsafe
grants stay unchanged even when their kind is selected. Upgrade chains are always progressive,
in chests only; see [Progressive items](#progressive-items).

| Kind | Scope and acceptance |
|---|---|
| `Chest` | 178 of 184 ordinary chests; changed chest grants work in game. Includes the played bridge bean, ranch Hookshot, late windmill Longshot, Field/Lake, four-torch Lake grotto, Valley grottos, Fortress underground, Fountain scarecrow, Well hidden-hole and sign-puzzle routes. The Well requires the Lens conservatively. Duplicate/failure copies and repeat chests stay unchanged. Treasure Chest Game reward swap is built but untested and held; its 11 game boxes stay unchanged. |
| `Shop` | Ordinary shop shelves, native-display items only; slot swaps, restock and Castle Town purchases have in-game evidence. Bought goods (refills, ammo, Bombchus, bottle contents, hearts and magic jars) go only to shop shelves in every seed; no setting moves one to a chest, gift, scrub, floor pickup or Skulltula. Mask loans stay unchanged. |
| `Gift` | Eligible NPC and song gifts, including Great Fairies, Kokiri shopkeeper, the adult Rolling Goron's and King Zora's tunic gifts, all seven frog checks, and the first paid item from Medigoron, Granny and the Wasteland carpet seller. These families have in-game evidence, not every individual swap. The shopkeeper's late window passed. See the remaining held checks below. |
| `Scrub` | Four kinds of one-time Deku Scrub sale; repeat vendors unchanged. The adult Mirror Shield purchase that previously froze now finishes; other item/age combinations are not all played. |
| `BossHeart` | Eight boss-heart checks, off by default. Limited to the floor palette below (five native pickups, both ocarinas, songs with `--songs anywhere`). King Dodongo's Hylian Shield grant/no-respawn was observed; not every combination. |
| `Freestanding` | Fourteen anchored floor Heart Pieces, off by default; the native five, Ocarina of Time and songs with `--songs anywhere`. Fairy Ocarina is excluded after the empty original-child roof failure; BossHeart/chest/NPC delivery stays admitted. Ranch tower Hylian Shield collected/equipped with its saved Hash set; other surfaces, underwater pickup and complete reload coverage are not all verified. |
| `Token` | All 100 native Gold Skulltulas, off in both presets; needs `Chest` (Token alone is refused). Admitted rewards: native tokens, fixed Boomerang/Hammer, shields/swords/boots/tunics, new empty/Milk bottles, all rupee colours, Heart Pieces/Containers, fixed Nut/Stick capacity, ordinary arrow/bomb/nut/stick bundles, Bombchus, magic jars/spells/arrows, Lens, Echo Gem, Double Defense, Scrub Business Seed, both ocarinas and (with `--songs anywhere`) the twelve songs. Core, packets 1–3 and the separate first-Time-ocarina part passed on rc.3; each catalogue member still needs its own native structural check, not every member/boundary was played. See `src/clawshot/data/token_rewards.toml`. Tokens spill only into shuffled chests; non-token grants add no token. The Field tree works by day, the ranch tower needs night/retrieval, and wetlands needs the child wall kill before the adult crate. |

The windmill floor check is in logic only through its adult approach from Dampé's grave, not
child Boomerang retrieval. The cow-shed roof pickup remains a separate native check, not the
rooftop man's gift. These source-logic corrections do not expand the floor palette or certify
every surface ([ranged pickup audit](../plans/rounds/r20-audit.md)).

With Gift and Token selected, played bottles, Double Defense, the Echo Gem and gold rupees may also reach
Skulltulas. With Gift selected, eight gift items may also be found in shuffled chests: Light Arrows, Nayru's Love,
Farore's Wind, the Echo Gem, Double Defense, Biggoron's Sword, an empty Bottle and Rupees (200); they never go
to one-time scrub sales. Fixed Deku Stick and Nut capacity upgrades may be found in chests as well as at one-time
scrub sales and, with Token on, at Skulltulas. On Longshot 3.2.0 (2026-11-25) Kareem checked each of these chest
rewards (right model and text, and the item works) and the Stick upgrade from a Skulltula; the Nut upgrade's
Skulltula pickup passed earlier on rc.3 ([evidence](../plans/rounds/r22-lifts.md)).
Token placement retains the existing seeded random ordering; there is no target percentage or weighting.
Reachability, container requirements, pool composition and earlier fill stages still limit the result.

Skulltula ammo requires its existing container before the source; refills never grant a bag or weapon.
**D25:** Bombs and Bombchus require an independent Bomb Bag at every shuffled destination, not only Skulltulas.
Arrow and stick bundles retain their container screens; the native new game already has an empty Nut Bag.
The legacy labels **Deku Nuts (5)** and **Deku Stick (1)** each deliver the native bundle of **3**.
Scrub Business Seed is not an ammo bundle or N64 Magic Bean: the played pickup added one seed; using it
without buying anything **does not consume it**, which is native behavior.

**Excluded at Skulltulas:** songs unless `--songs anywhere`; progressive copies and their fixed tiers; keys, maps and
compasses; every `Buy*`/shop-stock item (including refills and bottle contents); trade items; and Gerudo Pass
(Gerudo Membership Card). Their existing destination/pool holds remain unchanged. Fire Arrows and other
out-of-pool items are not silently added.

By default the 100-token House reward accepts only non-progression items, including Gift shuffle with
Token off. This is an explicit placement rule, not a consequence of which Skulltulas are reachable.

`--shuffle-100-token-reward` (app: **100-token reward (experimental)**, under Items) is a separate
default-off opt-in for [#12](https://github.com/hiKareeem/Clawshot/issues/12); both presets keep it off.
It needs `Gift` shuffle (an effective spoiler string's `NPC` also counts) and is refused otherwise.
When on, only that automatic non-progression rule is lifted: the first 100-token reward may hold a
progression item, so a seed can require collecting all 100 Gold Skulltula tokens. The threshold stays 100
and other destination holds and exclusions still apply. `--no-shuffle-100-token-reward` overrides a
settings string; CS1 stores the choice. The shuffled reward is the father's first `GatheringTokenGold`
grant (Event215), gated by the quest's native completion; his later repeat 200-rupee payout (Event471)
is not a check and stays native (native trace:
[section 35](../plans/03-game-data.md#35-round-8-gift-checks-native-identities-and-success-only-merchant-sales-cs8d)).
Played on **Longshot 3.0.0 stable, 2026-11-20**: the first reward gave Hammer at 100 tokens,
then the native repeating 200-rupee gold payout. This does not certify every possible replacement
([100-token reward checks](../plans/rounds/r19-tokens.md)).

Cows, pots, crates, loose rupees, recovery hearts, Treasure Chest Game keys and
silver-rupee puzzles stay unchanged. Dungeon rewards have their own default-off
option below. Pot and ground-rupee
experiments are not seed options: grants were observed, but a thrown pot stranded and lost its
reward. Completion and recovery are not solved by a destruction flag.
Cow work remains research only: no cow locations, option or production patch shipped
([cow research](../plans/rounds/r19-cows.md)).

Forced diagnostic placements are not shuffle options or beatable seeds. Their core, reward-family,
route and first-Time-ocarina parts provide the played evidence for this explicit catalogue; they do not
establish every item, full-capacity case or route combination.

Maintainer packet/checker tools live in `tools/token_packets/`, outside the release package.
From the repository root, run `uv run python -m tools.token_packets.token_family_packet`
with `--manifest`, `--baseline`, `--save` and `--phase` to check a staged family or route packet read-only.

**Ocarinas and songs at Skulltulas and on floors.** Both instruments use generated
`Obj_Clawshot_Ocarina_*` actors; songs use `Obj_Clawshot_Melody_*`. These packs are selected by settings:
a Gift kind plus an admitted destination for that instrument (`Token`/`BossHeart` for Fairy, also `Freestanding` for Time); additionally `--songs anywhere` for songs.
The native moat `Obj_Ocarina_Time` is not their world donor. Pickups float above the original spot;
ocarinas glow warm white, songs use their own effect, and every non-token Skulltula reward spins.
BBender's H1/H2/TG2/TB3/TB4/SP1 records span Longshot 3.1.1 and 3.2.0, not every source/reward pair.
The ten unplayed songs are accepted by analogy, not individually played.
**Known issue:** after a Time Skulltula pickup while Fairy is active, Fairy's model/sound may remain
until Save/Continue. Time is owned/selected; Kareem confirmed both instruments function identically and
accepted this as cosmetic. The five remaining floor/GrottoScrub/song-use/spin checks are planned separately,
not claimed played: [integration record](../plans/rounds/r22-pr42-integration.md).

Fairy's final world-pickup kinds are **Token and BossHeart, not Freestanding**; supported chest/NPC
delivery is unchanged. Kareem's daylight Market GS gave a spinning Fairy, full item-get animation, playable
instrument and updated D-pad. The same child's shed roof gave Bolero with a Time-ocarina model/red VFX;
Bolero was playable and Fairy stayed selected. These passes were on7968343, before the ineffective
generated-Fairy Large override was reverted. Final-head Token artifact comparison/replay is tracked in the
integration record; this play does not prove the reverted classification. No claim that c's empty Fairy roof is fixed.

Both floor kinds keep **Heart Container, Piece of Heart, Deku Shield, Hylian Shield and red rupee**,
**Ocarina of Time** and, with `--songs anywhere`, **the twelve songs**. **Fairy Ocarina is BossHeart-only
among floors**, retaining the played Gohma case; it cannot be generated or forced externally at Freestanding.
Other major items on the floor can crash. Heart Containers from chests have no recorded in-game acceptance.

### Starting inventory (experimental)

Empty/off by default; new games only. Existing saves are never changed.
`--starting-items "Kokiri Sword" "Slingshot" "Ocarina of Time" "Zeldas Lullaby"`
chooses audited native items. The app lists the supported choices, including all twelve songs and
each ordinary dungeon's map/compass. `--starting-items` alone clears a settings string's selection.
`--starting-hearts 3` adds three hearts to the usual three; valid extras are 0–17.
`--starting-full-wallet` starts with 200 rupees, or 500/1000 with the selected Adult/Giant Wallet;
`--no-starting-full-wallet` overrides an imported string.

Choose a concrete upgrade tier, not a number of copies: Longshot includes Hookshot, Golden Gauntlets
include the child Bracelet and Silver Gauntlets, and Quiver/Bullet Bag upgrades include Bow/Slingshot
and their containers. Lower selections in the same family do not add extra tiers.
Native bag grants supply their declared ammunition; a Bomb Bag never invents Bombchu ownership.
Bombs still require age-appropriate strength unless **Bag bombs without the Bracelet** is on. Other equipment is owned, not forcibly worn:
equip sword/shield in the pause menu. The selected ocarina is active (Time wins if both are chosen).
With the adult-return guarantee, starting strength no longer proves the child learned Saria's Song.
If that song remains at its fixed child source, also start with it, enable Gift/song shuffle, or enable
free time travel; otherwise validation refuses the combination rather than assume a safe return.

Logic owns the initial items before its first check. Each selected item or progressive-prefix copy
actually present in the shuffled pool becomes a red rupee; extra hearts replace pooled Heart Containers
when present. Pool size stays fixed; unshuffled native rewards remain. Missing songs leave junk in
song slots, not extra copies of other songs. A starting spell/arrow's native magic floor counts as
one initial magic copy and removes one pooled magic copy too.

Starting ownership does **not** complete the corresponding lesson, source, dungeon or story quest.
Impa's real send-off, Malon's source for Epona, the Ice Cavern chest, Forest completion/Prelude and
pedestal age transitions remain separate. A prelearned Storms song retains the Windmill's first lesson.
Starting with the Kokiri Sword natively replaces Saria's first event door with a plain door.
That start therefore inherits the existing Saria fast-start state (opening histories, open door,
talked-to flag and Kokiri map visit). Later song lessons and Saria's bridge farewell remain separate.
Trade items, bottles, masks, Lens, raw ammo, keys, tokens, dungeon rewards and arbitrary names are refused;
they need additional source/slot/active-equipment contracts, not guessed save values.
The broad inventory, Continue and Time-ocarina lessons passed Kareem's check. On Longshot 3.0.0 (2026-11-21),
a New Game with Kokiri Sword, Deku Shield, Boomerang, Slingshot, Bomb Bag, Goron Bracelet, Hookshot, Ocarina of
Time, Zelda's Lullaby, Song of Storms, Adult Wallet, Deku Tree map/compass, 6 hearts and 500 rupees had those
items, songs, hearts and rupees present and working; Impa's Lullaby and the Windmill's Storms lessons still
played with the songs owned; the Ocarina of Time stayed equipped after Saria's gift; and the Master Sword pull
worked. After the Saria-state fix, that starting Kokiri Sword's Kokiri Forest pause map, Deku Tree map/compass
and Hyrule Field big map also worked. Other choices retain their documented evidence limits.
Evidence and provisional pool policy: [starting inventory record](../plans/rounds/r20-start.md).

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

Status: played on Longshot (Kareem, 2026-11-13). Mido's chests gave Hookshot then Longshot and
Silver then Golden Scale; separate chests gave every remaining top tier (Bomb Bag 40, Quiver 50,
Bullet Bag 50, Golden Gauntlets, Giant Wallet, double magic); Darunia's dance with the Bracelet
already held kept Silver Gauntlets and gave no duplicate. Get windows name the tier received;
the rising chest model still shows the base item. A seed puts one copy in a chest; several copies
granted inside one chest event read stale ownership, so that is not supported.

### Gifts: enabled versus held

`Gift` includes five frog song prizes contributing **Rupees (20)** each, the Storms prize and the
bug game. All seven passed the frog experiment. The two deterministic Bombchu Bowling
prizes (first win, second win, then the usual rupees) and both normal shooting-gallery prizes
are confirmed in game (`R10-MINIGAMES-CHILD-JABU`, `R10-MINIGAMES-ADULT`).
Rental weapons do not become inventory rewards. Both expert galleries remain unshuffled:
native expert wins pay repeatable wallet rupees, with no separate first-win prize.

In every seed, **LW Ocarina Memory Game** gives its prize on the first completed won round and sets the
native once-flag: the shuffled reward with `Gift`, or the vanilla Heart Piece without it.
It then keeps the native post-prize session state and repeat payouts. Failure or declining gives nothing.
No setting: this matches the other minigames' first-win policy. Its all-five-ocarina-buttons logic
requirement is unchanged. Kareem played it on Longshot 3.2.0 (2026-11-25) with a shuffled prize: declining or
missing gave nothing, the first won round gave the prize, the Skull Kid then said there were no more prizes, a
later win paid a Blue Rupee, and after reloading the prize was still owned and not given again. The unshuffled
Heart Piece case was not played separately ([played results](../plans/rounds/r22-games.md#played-results-2026-11-25-longshot-320)).

With `Gift` selected, the child Market Potion Shop bottle tutorial and Dampé's graveyard
digging prize give shuffled rewards. Both passed their in-game checks on 2026-11-10
(`R10-MARKET-BOTTLE-FIX`, `R10-DIGGING`). Accept the shop owner's offer by day; the shuffled
gift skips the bug-catching lesson. Without `Gift`, the free bottle and lesson stay unchanged,
and logic still counts that bottle. Digging still shows a heart prize but awards the shuffled item.
Market expert wins pay 30 rupees and Kakariko expert wins 70, including the first win. Clawshot's
held first-expert-check experiment would add a new once-only prize; it is off under every setting.

With `Gift`, the adult Rolling Goron's tunic gift and thawed King Zora's tunic gift are shuffled checks. Their
usual requirements stay: stop the Rolling Goron as adult, or thaw King Zora with Blue Fire. Kareem played both on
Longshot 3.2.0 (2026-11-25): Ice Arrows and the Mirror Shield came in place of the tunics, neither gift repeated,
and Goron City's doors and story continued as usual ([shop and gift checks](../plans/rounds/r22-shops.md)).
The Goron and Zora Tunics themselves can still be found in shops and chests.

With `Gift` selected, **Medigoron, Granny and the Wasteland carpet seller each sell one shuffled
item once**, at their normal price. Declining does not use up the shuffled item. After buying it,
their normal sales return; saving and continuing does not give another shuffled reward.

| Seller | Price of the shuffled item | Afterwards |
|---|---:|---|
| Medigoron | 200 rupees | Sells a replacement Giant's Knife only after the Knife breaks. An intact Knife does not unlock another purchase; “come back if it breaks” is dialogue only. |
| Granny | 100 rupees | Refills an existing empty bottle with Blue Potion for 100 rupees. She does not give an extra bottle. |
| Wasteland carpet seller | 90 rupees | Sells his normal Bombchus for 90 rupees. |

Granny's Blue Potion leaves the shuffled item pool and is replaced by **Rupees (5)**. This does
not make Granny's shuffled reward a fixed five rupees; she can sell another item from the pool.
Without `Gift`, these merchants keep their normal sales.

Medigoron needs **no wallet upgrade**: the starting wallet holds his 200-rupee price. His adult
room-access requirement remains. To reach the carpet seller, come from the **Gerudo Fortress
side of the Wasteland** and cross with **Hover Boots or Longshot**, or enable the existing opt-in
Wasteland crossing trick. The trick is off by default; it is not a new merchant shortcut.

Kareem played the shuffled purchases, saved returns and normal repeat sales on Longshot 3.2.0
(2026-11-27), including Blue Potion refills without extra bottles and Medigoron's replacement
Knife after a normal break. All merchant rows passed ([play record](../plans/rounds/r22-merchants.md)).

The Skulltula House's 10- and 40-token reward swaps passed; the 20-token preview was observed,
not every later threshold.
With `Gift`, the 40-token reward contributes **Bombchus (20)** to the pool and gives its
assigned item, using the usual forty-token requirement and collected state. Without `Gift`,
it stays the usual twenty-Bombchu bundle. Kareem passed the changed reward on Longshot rc.7
on 2026-11-19; this does not certify every House reward or every possible replacement.
The Weird Egg, Zelda's Letter and the adult trading items stay at their native checks.
All fourteen share one trade inventory cell that shows a single owned item,
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
With Gift shuffle, songs show an ocarina with their own effect rather than a green rupee; ordinary songs
use Fairy and warp songs use Time. Without Gift, songs stay at their native sources.
Both chest ocarinas work and show their model in small and big chests. Gift shuffle, or any of its expanded
gift kinds in effective settings, always includes the ocarina get model, even without Chest shuffle or when
neither instrument lands at a display hand-over. This settings-based build rule is reported in the spoiler's
`patch.steps`; uncovered ocarina placements and unavailable model inputs are refused.
This does not relax the whole-game progressive pool's separate requirement to shuffle Chest checks.
Small and big chests were played with BBender on Longshot v3.1.1
(2026-11-22, [chest ocarina record](../plans/chest-ocarina-model.md)). Kareem
played small chests in both orders on Longshot 3.0.0 (2026-11-23): the Ocarina of Time stayed the equipped
one, also after Save and Continue, and Saria's farewell, Zelda's escape and the moat looked as before
([chest ocarina check](../plans/rounds/r21-pr40.md#played-results-kareem-longshot-300-2026-11-23-pass)).
The Ocarina of Time plays songs. Din's Fire, Adult's Wallet and the eight gift items
[listed above](#what-enters-the-shuffle) have chest evidence.
Other gift actors remain subject to the sourced chest allowlist and destination holds, not blanket
permission for every gift to go in a chest. Authoritative restrictions: `data/settings.toml`.

Ocarinas may use item-display hand-overs only with the required get model: both ocarina actor packs and
ActorInfo changes, never native-pack fallback. On Longshot 3.2.0 (2026-11-25) Kareem received both ocarinas
at the child Market Shooting Gallery with that model; without it, the Ocarina of Time crashed there.
BBender's H1/H2 on Longshot 3.1.1 (2026-11-24) also played both ocarinas at the Kokiri shopkeeper and
Lost Woods scrub, in both orders. Other hand-overs were not each played. Gift destinations require an
audited native receipt. Chests and direct story grants remain allowed under the same settings rule.
Shops never sell an ocarina or a song. See the [played scope and limits](../plans/rounds/r22-lifts.md).

Ocarinas remain separate fixed items, **not progressive copies**. Newly generated seeds still give the
Fairy Ocarina when found, but keep the Ocarina of Time selected if it is already owned, at either age.
Kareem passed the child and adult checks on Longshot rc.7 on 2026-11-19: adult Sun's Song worked,
and Time stayed selected after Continue. In the unchanged adult check, Sun's Song also worked while
holding Fairy. That result covers Sun's Song, not every adult song or the automatic song lessons.
Ordinary adult song-playing logic still requires Time; lesson logic accepts either ocarina at either age.
The separate [scene handoff](#scene-handoffs-experimental) handles zero stock of both instruments.
Existing seed folders and saves are not repaired.

### Cross-age equipment receipts

Age restrictions govern **use**, not ownership. There is no blanket matching-age placement rule.
Native shops still refuse child tunic purchases; unsupported shelf displays and the
boss-heart/floor palette remain restricted. Trade-cell items stay vanilla.

Newly generated scrub shield sales keep the native inventory grant and one-frame yield, then
finish without requiring any shield to equip. This covers an adult owning only the unusable Deku
Shield, as in issue #33, and opposite-age Mirror/Deku receipts. The patch does **not request forced
auto-equip** or enable wrong-age shield use. Inventory, native auto-selection and equipment are
separate; manual equipment remains available at the usable age. Kareem passed the adult Mirror Shield
purchase on Longshot rc.7 on 2026-11-19. Other shield/age combinations are not all played;
old generated folders are not repaired.

Other chest/gift/pickup paths do not use that scrub-only equipment wait. They retain their existing
native grants and admission rules, not a claim that every item/age pair has been played.
The [equipment audit](../plans/rounds/r18-equipment.md) separates played results, native-data evidence
and unverified boundaries. Wrong-age item-bar precautions remain [below](#hints-models-and-age-warnings).

An attempted late lesson bypass was withdrawn. Kareem's control on 2026-11-20
established that adult Link **can** play the native Minuet lesson with the Fairy Ocarina and
receive its shuffled reward, consistent with the earlier adult Sun's Song check.
Lesson logic therefore accepts either ocarina at either age; the no-instrument physical guard
uses the early caller handoff described below ([scene checks](../plans/rounds/r19-scenes.md)).

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

**Potion shops:** Kareem's 0.2.6 report of a Kakariko Potion Shop shelf that would not sell a shuffled Deku
Shield, with no prompt, has not been reproduced. On Longshot 3.2.0 (2026-11-25), with no potion-shop change,
that shelf sold the Deku Shield to an adult who had never owned one and had the Mirror Shield equipped, also with
Kareem's own 0.2.6 seed and no bottle ever owned; another test sold the shield and both tunics. A proposed
message fix for non-bottle potion-shop sales is not included. Buying Deku Nuts into a part-full bag at the Market
Potion Shop, and the refusal once the bag was full, were played only with that unshipped fix
([shop checks](../plans/rounds/r22-shops.md)).

**Scrub offer wording:** newly generated shuffled one-time sales name their actual
reward and effective price (English in all16 languages). HF and DMC have separate
offers even though their native pitch shares one message. On Longshot 3.0.0 (Kareem,
2026-11-21) all four supported offers named their real item: the Lost Woods bridge scrub, the two-scrub
grotto's front scrub, the Hyrule Field password scrub and the Death Mountain Crater ledge scrub
([hints play record](../plans/rounds/r20-hints.md)). Not every reward or price has been played.
Repeat vendors are not shuffled; their native weapon/magic/bottle gates can hide every offer.
The no-offers guard for [#26](https://github.com/hiKareeem/Clawshot/issues/26) ends that
conversation before opening an empty shop menu. It applies even without Scrub shuffle.
Kareem reproduced the control's second-talk softlock on Longshot rc.3 and passed the repair:
repeated empty-offer talks, Song of Storms for 10 rupees, normal seed refill and Save/Continue
(2026-11-14). Decline-then-Leave and full-capacity refusal were not exercised.
Existing seed folders are not changed.

## Forest and fast start

`--forest closed` is the vanilla-like default: Mido guards the Deku Tree and the bridge exit stays
closed until Gohma. `closed_deku` opens just the bridge; `open` also bypasses Mido. The bridge-only
option has in-game evidence with Mido still blocking (R6-CLOSEDDEKU). Mido skip and fast start also
have recorded in-game results. Legacy `--skip mido` aliases `--forest open`; conflicting explicit
forest choices are refused. Forest flags compose with gift save flags.

With Mido kept, his post-Zelda schedule waits until his saved wall blocker has actually cleared.
This preserves the native sword-and-shield conversation after an early castle visit instead of moving
him beyond a still-closed wall ([#35](https://github.com/hiKareeem/Clawshot/issues/35)).
Only that completed-castle schedule is guarded; open/Mido-skipped mode is unchanged.
Kareem passed the repair on Longshot rc.7 on 2026-11-19: sword-only Link was refused, adding the shield
opened the passage and tree mouth, and both stayed open after reloading. Do not regenerate a played seed
or reset story quests to repair it.

The opening-movie skip is on by default. It removes the movie entirely, not just its skip-button
restriction; Navi waking Link and normal new-game initialization still run. Movie removal
**passed Kareem's new-game check on 2026-11-12**. `--skip intro saria deku_tree kaepora`
selects fast-start skips; `--skip` alone disables them. These are separate from shuffled kinds.

**Story-dialogue skipping is not available yet.** It is withdrawn for 0.2.3: the option is hidden
and requests to enable it are refused.

The Kaepora skip also marks the skipped first-field panorama complete, ending its native
music-suppression window. The previous preset could leave Hyrule Field silent during the day.
This changes **new games only**, not existing saves. Kareem verified the repaired field
music and the story/escape checks on Longshot on 2026-11-13
([section 46](../plans/03-game-data.md#46-round-14-child-story-and-field-music)).
The skip now also preserves `IsVisitLocation.HyruleField`, normally supplied by the panorama's
location UI and required for the Field map. Like the Saria skip's Kokiri Forest visit flag, this
also reveals the area's pause map before the first visit. This new-game minimap/full-map correction
still awaits in-game verification; existing saved visit state is not migrated.

The optional, default-off `kaepora` fast-start selection remains **experimental**, including under
Recommended. It omits later owl speech while preserving scene flags and travel.
On Longshot 3.0.0 stable (2026-11-19/20), Kareem played the castle arrival: no speech, a short
stop/fly-away, with banner/map/Malon preserved. The Field owls near Kakariko and the Lake approach
also passed: no speech, a short look-and-fly-away. The summit and Lake travel owls kept a short offer and working flights.
These results do not cover every owl scene; later Woods/Zora owl additions remain unplayed.

Every new seed refuses Dampé's race without an owned Hookshot or Longshot: he explains the requirement
before race setup, then fades out and returns Link to the surface. With either tool, the first race and its
chest remain available until that chest is opened; an unopened retry and old second-race saves are supported.
The first race has no one-minute prize condition. After collection, the native second race/timed prize resumes.
Kareem played refusal, retry, both prizes and old-save recovery on Longshot 3.2.0 (2026-11-24); the first chest
now accepts progression under the usual item restrictions. This replaces 0.2.7's non-progression workaround.
New generation does not rewrite old seed outputs, which may retain the item-based second-race-only bug.

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

## Scene handoffs (experimental)

`--skip-saria-farewell` (app: **Skip Saria's bridge farewell**) is off by default.
It skips both the bridge farewell movie and its animated gift, then gives that location's
actual reward through the normal get window. It preserves the source's completion flags
and native travel/lighting continuation. `--no-skip-saria-farewell` restores the native sequence.
This is separate from fast start's Saria **opening** scene and from skippable dialogue.

An always-on softlock guard replaces song lessons with a normal item get only when **both**
Fairy Ocarina and Ocarina of Time have zero pouch stock. Either instrument keeps the entire
native lesson at either age, regardless of the selected instrument or historical `IsGet` flags.
Shuffled lessons give the placed reward, not an additional vanilla song; native quest,
scene-history and once-only effects remain. The moat's item and Time-song reward are distinct
and both survive its replacement.

Kareem passed the morning candidates on **Longshot 3.0.0 stable, 2026-11-20**: Minuet gave Boomerang
without a lesson; Impa skipped its lesson, gave Boomerang and kept the normal Hyrule Field dialogue.
With `skip_saria_farewell` on, Saria gave the correct item text and went straight to Hyrule Field
without the farewell movie; her brief pop-in is cosmetic
([morning played results](../plans/rounds/r19-scenes.md#played-results-and-stock-only-correction--2026-11-20)).
Both corrected Minuet stock-v2 candidates also **played pass at 14:16**: adult Fairy keeps the
native lesson, then Boomerang; zero stock of both instruments skips straight to a normal get.
Both give correct text, with saved ownership/source completion, no extra Minuet and unchanged ocarina stocks.
Continue/re-entry was not reported. The native arm's override is inferred from its played lesson
and saved shuffled reward; two expected file-load lines are absent for an unexplained logger gap.
The [Minuet play record](../plans/rounds/r19-scenes.md#minuet-v2-played-pass-and-accepted-logger-gap)
separates that inference from direct load evidence. Logic still conservatively requires **any**
ocarina for lessons; general Great Fairy/Rauru/story skips and non-instrument prerequisites are unchanged.

## Items shown in events

`--event-item-models` (setting `event_item_models`, app: **Show shuffled items in events**) is **on** by default; `--no-event-item-models` turns
it off. Gift and reward scenes that show the vanilla item show the item the seed gives there instead: Saria presents
it at the forest bridge and hands it over, Zelda throws it into the moat and Link holds it when he takes it from the
water, the scrub at the Lost Woods target, Biggoron and the Light Arrows scene hold it, and with dungeon reward shuffle
the boss and sage scenes show the reward placed there, as does the stone Ruto finds in Jabu-Jabu's Belly. A song shows its ocarina with the song's own effect; Nothing and another player's item show Zelda's Letter, as
Link's get pose does. The item takes the scene's native pose and place, so a big item can clip or sit oddly: that is
intended. It spins only where the scene spins its item (the Light Arrows scene), never idles, and it cannot be picked
up: the grant is unchanged. The moat's water
object stays the pickup and only changes its look. Scenes whose item never moves (Darunia's Bracelet, Zelda's Letter,
the Claim Check) and played instruments (Saria's own ocarina, Sheik's harp, Link's ocarina in song lessons) keep
their models.

Whatever the setting, the item texts name the given item: the get window and the Zelda's Notes screenshot of Saria's
farewell and the moat, the Deku Tree's farewell and the Key Items screen after it, Ruto's line in Jabu-Jabu's Belly,
and NPC prize lines such as the shooting galleries', bowling's, Talon's and Anju's. In each
language only the words naming the vanilla item are replaced, even when the grammar around them is then wrong; a line
that does not name the item in words the patch can find keeps its own text. Other lines that mention the vanilla item
(trade-quest dialogue, song lessons, Great Fairy explanations) are not changed yet.

Known issues:
- In the moat scene Link holds the given item and, beside it, his own equipped ocarina: his animation shows it.
  The item hangs from his hand by its model's origin (a heart piece by its tip), not centred as in his get pose.
- Lines that describe an item without naming it keep their text (Darunia's line about what the bracelet lifts; his gift is never
  shuffled today).
- Ruto's line in Jabu-Jabu's Belly keeps its own words in Chinese, Japanese and Korean, which name the stone
  differently from the quest log.
- The Zelda's Notes targets are changed but cannot be checked: Longshot does not connect to the Nintendo Switch App.
  Ruto's Notes screenshot in Jabu-Jabu's Belly keeps its own target.

Played on Longshot 3.2.0 by BBender (2026-11-25/26): Saria's farewell (Biggoron Sword, Piece of Heart), the Deku Tree's
farewell and Key Items screen (Light Medallion), the Lost Woods target (Rupees (20)), Anju's prize lines and gift
(Hylian Shield), Ruto's stone and line in Jabu-Jabu's Belly and Ruto's thanks after Barinade (Spirit Medallion), and
the moat (Piece of Heart: Zelda's throw, the moat object's glow and pickup, Link's hold, the get text), Rauru (Kokiri
Emerald), Impa's and Nabooru's awakenings (Zora's Sapphire, Shadow Medallion) and the Light Arrows scene (Bolero of
Fire: the ocarina spins with Bolero's effect); unchanged with their vanilla item: Darunia, Zelda's Letter, King Dodongo
and Phantom Ganon's rewards. Not played: Biggoron, the Eyedrops trade, Volvagia's and Morpha's rewards with another
item; they are checked against the written files only ([record](../plans/event-items.md)).

## Dungeon rewards and Ganon's Castle bridge

`--dungeon-rewards` (app: **Dungeon reward shuffle**) is experimental and off by default.
It shuffles the three Spiritual Stones and six medallions only among their nine reward
slots, including Rauru's Light Medallion on the first sword pull. Rewards cannot go
to chests, gifts, shops or Skulltulas, and other items cannot occupy reward slots.
The first pull retains the native song/story sequence. It still grants the sword unless the
separate Master Sword shuffle option is on.
Placement obeys reachability: in a normal closed-Door seed the three Stones must
come from Gohma, King Dodongo and Barinade, in a seeded order, before adult rewards.

With reward shuffle on, the **closed Door needs the three owned Spiritual Stones**,
not child dungeon completions, plus its existing Ocarina of Time, learned Song of Time
and real Impa send-off requirements. Open and song-only keep their existing clock/send-off
gates. An early opening cannot strand the later native escape or moat rewards.
Boss deaths, blue warps, sage scenes, world restoration, carpenters/card and reverse
time travel remain completion-driven. Prelude follows Forest completion; Light Arrows
follow the Shadow and Spirit awakening scenes, not their medallions. Logic matches
these separate ownership and completion predicates.
Lesson logic conservatively requires either ocarina at either age; the physical zero-stock guard
is described above. The moat item precedes its Time-song lesson, so that item check needs no instrument.
With **Show shuffled items in events** off, the native animated emblem in each sage/stone scene remains its source
symbol; with it on (the default) the scene shows the shuffled reward. The acquisition window, owned reward and Zelda
Notes target follow the shuffled item either way.

`--bridge vanilla` is the default native story route. The experimental count modes
`--bridge stones --bridge-count N`, `--bridge medallions --bridge-count N`, and
`--bridge rewards --bridge-count N` count unique owned rewards, respectively 0–3,
0–6 (including Light), and 0–9. Vanilla requires count zero. Invalid combinations
are refused. These settings open **only the bridge**: they give no Light Arrows,
complete no sages and skip none of the six native Light Arrow trial cores.
With Gift shuffle, the native Light Arrow story still runs even if its gift moved.

`--bridge tokens --bridge-count N` (0–100) is experimental. On Longshot 3.0.0 (Kareem, 2026-11-21), a
16-token bridge on a 15-token adult save stayed closed at 15; the 16th token came from a shuffled chest, the
rainbow bridge scene played at 16 and the bridge persisted after Save/Continue
([trials play record](../plans/rounds/r20-trials.md)). Other counts are not individually played.
It compares the native Gold Skulltula token counter, including tokens found in shuffled
chests; defeating a Skulltula that gives a different item does not add a token. Tokens
are not spent. The bridge scene and permanent latch remain native. This setting does
not skip trials, grant Light Arrows or change the Skulltula House thresholds.

Kareem's Longshot rc.7 checks on 2026-11-19 confirmed the shuffled first-pull reward, a medallion-count
bridge staying closed below its count and opening at the count, and the closed Door opening with all
three Stones owned while Dodongo and Jabu were unfinished. The Door stayed open; no escape or moat
scene played. On Longshot 3.0.0 stable (2026-11-19/20), with only Emerald and Ruby owned, the Door
stayed closed and no opening scene played; the saved state confirmed both Stones and the closed Door.
Other shuffled boss rewards, stones/combined bridge counts, late story order and a full playthrough
are not certified by those checks. Both options remain experimental.
Detailed evidence: [dungeon rewards and bridge](../plans/rounds/r18-rewards.md).

The Temple of Time Light Arrows scene is an ordinary `Gift` check, already included
when Gift shuffle is selected. It may give another eligible gift item; without Gift
shuffle it still gives Light Arrows. In every mode its trigger remains the completed
Shadow and Spirit awakening scenes, not owned medallions. The vanilla bridge follows
that Temple story even when its reward is not Light Arrows; the six trials and finale
still require usable Light Arrows. Ganon's boss key is never awarded by this scene:
it follows the ordinary boss-key placement rules below. Default logic follows these native readers,
without changing the scene or its saved writes.
This is **static event-data evidence only, not played**
([Light Arrows scene research](../plans/rounds/r19-lacs.md)).

## Ganon's trials remaining

`--trials-count N` (app: **Ganon's trials remaining (experimental)**) accepts 0–6.
**Six is the native default** and leaves trial state/text unchanged. Zero clears all;
one to five leaves a deterministic, seed-selected subset. Selection uses a separate
random stream, so fill retries cannot change it. The spoiler's `ganon_trials.remaining`,
play note and first tower-barrier-view dialogue name the trials that remain.

This is **new games only**. It initializes only existing native
trial completion flags and the matching remaining counter. Zero also initializes the
native all-barrier-clear flag and the barrier-clear scene history that enables the tower lift;
it does not add a quest step.
Partial counts retain the real last-core scene. Remaining trials still need their usual
route and Light Arrows. The tower boss key and finale are unchanged.
Zero trials passed on Longshot 3.0.0 (Kareem, 2026-11-21): the barrier was gone and, after the lift fix,
the tower lift was down, rode up, returned and persisted after Save/Continue. That check was played on an
adjusted save, not a fresh new game.
Count one passed end to end on Longshot 3.0.0 (Kareem, 2026-11-23) in two parts. A new game showed one beam and
the line naming the remaining trial. Then Kareem's castle save, adjusted to one remaining trial, finished that
trial: the barrier-breaking scene played, the barrier went down, four pots appeared inside the barrier by the
elevator and the lift carried him up. Count two passed for its first trial: that beam went down while the other
beam and the tower barrier stayed. Counts 3–5 are **built, not played**.
Evidence: [trials play record](../plans/rounds/r20-trials.md), [count 1 and 2 checks](../plans/rounds/r21-checks.md#played).


## Master Sword shuffle

`--shuffle-master-sword` (app: **Master Sword shuffle (experimental)**, under Items) is experimental
and off by default, including both presets; `--no-shuffle-master-sword` overrides a settings string.
Off, the first pull grants and equips the Master Sword natively, and existing settings strings and
spoiler settings keep their bytes.

On, the Temple of Time pedestal's first pull becomes its own check, **Master Sword Pedestal**, which
gives one ordinary shuffled item instead of the sword; progressive copies cannot go there. The
reward uses the native nonblocking pouch receipt, without a separate get window, to preserve the
white-faded handoff before the age write.
Rauru's reward, the first-pull and first-arrival scenes and the Door's completion stay native. The
**Master Sword** item (`Weapon_Sword_Master`) goes only to shuffled chests. The pedestal still moves
Link between ages in both directions, and changing age neither gives nor removes the sword: adult
Link has no Master Sword until he finds it. Logic models that adult without a blade; an owned
Biggoron Sword still counts where a sword is needed, and the final battle requires the owned Master
Sword. The breakable Giant's Knife is preserved as equipment, but logic does not rely on its
unmodelled durability to reach another check.

It requires two existing settings ([Master Sword play record](../plans/rounds/r19-sword.md)):

- **Chest shuffle.** Without `Chest` the settings are refused everywhere: a settings string, the
  command line, `--print-settings` and the app.
- **Free time travel** (`--logic free_time_travel=true`, or the app's **Free time travel
  (experimental)** switch). Natively an adult returns to child only after the Forest Temple, which an
  adult without a sword may be unable to clear; free travel keeps that return open instead of a new
  fill guarantee. App validation and seed generation refuse Master Sword shuffle unless the effective
  logic has `free_time_travel=true`. `--print-settings` only encodes the string and does not check
  this requirement, so a printed string can still be refused when you generate.

**Candidate v4 played pass, Longshot 3.0.0 stable, 2026-11-20 at 16:21.**
Kareem completed the first pull without Master Sword,
returned to child, then passed the second unowned pull that froze in v3. Zora's River chest granted
and immediately equipped a usable Master Sword; the owned child/adult round trip also passed.
Exactly two unowned pulls were played, not three; the maintainer accepted the repeated-path coverage.
The main v4 control also passed. These checks do not certify a full playthrough or finale refusal.
The pedestal remains silent; no item window is inserted into the scene. Design, deviation and
evidence: [Master Sword play record](../plans/rounds/r19-sword.md) and
[Master Sword design](../plans/rounds/r18-master-sword-design.md).

## Door of Time and returning to child

| Option | Requirement / effect |
|---|---|
| `--door-of-time closed` | Default: meet Zelda and Impa, then Ocarina of Time and playable Song of Time. With vanilla rewards, keep the native completed-stone route. With reward shuffle, require all three **owned** Spiritual Stones instead; finding stones never completes their dungeons. |
| `--door-of-time song_only` | Field-arrival clock state and Impa's real field send-off, then either child ocarina and the learned Song of Time. No stones needed to open the Door. |
| `--door-of-time open` | The Door waits for Field-arrival clock state and Impa's real field send-off, then opens without songs or stones; the first-pull pedestal has no extra item gate. |
| `--logic free_time_travel=true` | Experimental, default off: adult return before Forest completion. The app's **Free time travel (experimental)** switch is the same override. Required by [Master Sword shuffle](#master-sword-shuffle). |

Door mode and reverse travel are independent. The default return guarantee proves an adult can
unlock return from the minimum mandatory first-pull inventory and adult checks; optional child
errands are not assumed. Early-door settings can be refused with unshuffled child-only prerequisites.
There is no automatic free-travel override. Both early modes keep the escape and both moat rewards
available after an early sword pull: finish the required stone route, return as child, then approach the
Market from Hyrule Field and collect the moat pickup. Logic still assumes all three stone quests; the
native repair follows the Fire/Water counter and adds no Forest condition. All Door modes defer that
counter until the real Impa send-off, recount there, and ignore calls after escape. This also covers
closed mode when shuffled songs allow stones before Zelda. The native courtyard Step01 reset remains;
early-mode post-pull callbacks do not roll the completed Door quest back.
Kareem passed the open-mode send-off gate, early-pull escape/moat order repair and immediate
child-return clock clear on Longshot rc.7, and reports the day/night clock working as expected in his later
seeds (2026-11-21). The first-arrival lighting repair below has no separate staged v5 check;
the [evidence review](../plans/rounds/r18-docs.md#review-corrections-after-3e31f160cb) retracted the broader pass claim.
The late first Forest-exit ordering (send-off before the first bridge departure, panorama never played) has
no separate played check ([time record](../plans/rounds/r16-time.md#late-first-forest-exit-guard)).

**For new seeds; no save-repair pass.** Both early modes read the
arrival flag and the real send-off history. Kaepora fast start now preserves the skipped owl's
arrival effect; the actual send-off restores it if a different route missed the owl. Independently,
that send-off clears a leftover first-arrival environment, waits one frame and rebuilds its palette.
The Forest exit does not re-enable that environment once the Field panorama or real send-off has played.
Returning to child through the Temple clears the pending first-adult clock hold without changing
the native first-adult scenes or the adult Market exit.
An adult who warps out before walking Market → Hyrule Field keeps the native first-night hold; walk that exit or return to child through the Temple to clear it.
Rebuilding an old seed can change output; do not replace a played seed or assume save compatibility.

**The three stones alone do not trigger Zelda's escape.** Visit the child castle courtyard and
finish Impa's send-off too: Malon's fixed Weird Egg / Chicken wakes Talon to reach that route.
Both moat rewards, Saria's song source and every Door mode require the completed
courtyard/Impa sequence in logic, even if ocarinas or songs were shuffled elsewhere
(`Met Child Zelda` models the completed send-off). Zelda's Letter stays at Zelda (D31); no child-Zelda
skip or quest-precompletion patch is offered. The native-data trace is
[section 46](../plans/03-game-data.md#46-round-14-child-story-and-field-music).
Kareem passed the staged Longshot story controls on 2026-11-13, including Saria before Darunia and escape/reload.

With the return guarantee enabled, this generator cannot build Chest-only seeds with
`song_only` or `open`: its return-kit bound needs movable ocarinas and Saria's Song, but those
remain at child gifts. Validation names the fixed checks and offers a closed door or Gift
shuffle. This is a construction limitation, not proof that no physical route exists;
in particular, the logic for the unshuffled Time-song gift already requires all three stones.
Free time travel replaces that return proof, so with it on all three door modes are accepted
with Chest only. Early open-mode return, preserved moat rewards and the immediate-child-return
clock clear passed on rc.7.

An open-bridge, early-door seed can validly require adult Link before Gohma. Its play note
explains when no child-only opening guide exists instead of rejecting the beatable seed.

Free travel keeps Temple Sheik through both first-arrival scenes, then hides him until Forest quest
completion. Forest completion, not its medallion, controls Prelude even when rewards are shuffled.
Early return, repeated age changes, the post-Forest Prelude and the fixed first adult arrival have
recorded in-game acceptance (R9-FREE-TRAVEL, R9-PRELUDE-PATCHED, R10-FIRST-PULL-FIXED). Default stays off.
Ordinary adult song-playing logic still requires the Ocarina of Time. Adult Sun's Song worked with Fairy
in the 2026-11-19 check; the separate adult-Fairy Minuet lesson passed on 2026-11-20
([Minuet play record](../plans/rounds/r19-scenes.md#minuet-v2-played-pass-and-accepted-logger-gap)).
Neither result certifies every adult song.

The app shows this override as the **Free time travel (experimental)** switch under World, not as a
separate generator setting. On writes the same settings string as `--logic free_time_travel=true`;
turning it Off removes the override (the default meaning). Importing a CLI or spoiler string sets
the switch from its value. Explicit overrides, including `free_time_travel=false`, keep their exact
settings string through unrelated form edits. Editing the switch replaces its old override; editing
the advanced logic JSON resynchronizes the switch from that explicit value.

`--dungeon-items own_dungeon` keeps dungeon items in their dungeon and is the default; both UI
presets keep it. While it is set, the two chests on the Desert Colossus statue's hands cannot
hold Spirit Temple keys, maps or compasses: a generic grant there would credit the wrong
dungeon or nothing.

In every mode, small keys, boss keys, maps and compasses go only to chests, even inside
their own dungeon (Kareem, 2026-11-23). Other pickup types do not generally write the dungeon's
ownership flag. An own-dungeon map/compass writer for gifts and song lessons is built, but the
Ice Cavern Sheik map/compass checks remain unplayed and held, so the chest-only rule stays.
The one exception is a released floor-key source holding its own native key.

`--dungeon-items anywhere` (the UI choice **Small keys anywhere**) moves **small keys only**,
into shuffled chests whose access and native opening contracts permit it, including other dungeons
and the overworld. An off-dungeon key is delivered as a named chest grant; no other shuffled kind can grant one.
Both release modes include the Well floor key and require Chest shuffle.
Its floor source keeps its own key or gives a red rupee; the replacement retains a key-shaped
model and native room retirement wiring. Other dungeons' keys, majors, hearts and shields
are not floor-key rewards. On Longshot rc.7 on 2026-11-19, Kareem left the Well replacement,
recovered it, collected its silent +20 rupees, and confirmed it stayed collected after leaving,
returning and Continue. This proves the checked Well pickup, not every scripted floor key.
Own-dungeon mode leaves it untouched. The Shadow Temple floor key stays in its usual place
under every setting ([floor-key record](../plans/rounds/r19-keys.md)).

`--shuffle-hideout-keys` (UI: **Fortress jail keys (experimental)**) separately releases the four
Fortress guard floor keys into supported shuffled chests. Default **off** in both presets;
`--no-shuffle-hideout-keys` overrides a settings string. Chest shuffle is required. Each guard's
drop, staged event pickup and resting pickup remain one check. Replacement rewards are red rupees
with the native key-shaped floor display and the key's get-event/window, not silent rupee collection.
That completion writes the source's native once-only Bool; the initial silent candidate repeated
after re-entry and is superseded. Kareem passed one guard/rescue and the repaired 20-rupee drop,
including leaving/returning and Continue, on Longshot rc.7 on 2026-11-19. Chest keys credit only
Fortress inventory, not guard defeat, source collection, carpenter rescues or Spirit progress.
Talk to the Valley carpenter boss and answer Yes before the jailed carpenters; this enabled the
guard in the played check. On Longshot 3.0.0 (Kareem, 2026-11-21) the option also passed four keys from
four chests, the guards' 20-rupee drops, all four rescues, the captain's unchanged card (D39) given once and
Training Ground entry with its 30-rupee fee ([Fortress play record](../plans/rounds/r20-cows.md)).
That is a bounded check, not a full playthrough, so it stays experimental. The card alone does not clear guards.

The four jail sources use stable native actor/Hash identities, not a guessed torch-room match.
Until that correspondence is verified, logic conservatively requires access to all four guard
fights before relying on any shuffled jail-floor reward. Native jail-door spending remains unchanged.

The experimental `--dungeon-items all_anywhere` (UI: **All dungeon items anywhere**) also
releases maps, compasses and boss keys, including Ganon's Castle's boss key, into supported
shuffled chests. It is off in defaults and both presets. Source-bound grants write only the
intended dungeon's saved ownership flag, never the standing dungeon's. Both pickup messages
name the item and its target dungeon in English in every language. An off-area boss key
does not animate the standing dungeon's boss-key indicator. Map/compass display passed Kareem's
Longshot rc.7 check on 2026-11-19; an earlier remote Forest boss key opened its normal door.
These checks do not cover every source/target combination or a whole playthrough. The option remains
experimental; it does not shuffle dungeon-completion rewards or change the bridge.

In either anywhere mode, the statue's two hand chests may hold a named small key.
Only `all_anywhere` allows named maps, compasses and boss keys there.

Dungeon-item delivery uses the native grant where it already works: own-dungeon small keys
in small chests and all four families in big chests. Moved small-chest maps and compasses
use source-bound ownership writes; own-dungeon boss keys reuse the native boss-key action
and pickup indicator on existing actors. A get message or HUD icon alone does not prove
saved ownership. Native pickup text and unchanged placements are preserved.
Map/compass saves and pause menus, and boss-key credit, pickup indicator and normal boss-door
opening passed in-game. Boss-door reload persistence is untested: the arena prevents saving.

Previously generated seeds can lose these three items from small chests. Rebuilding a mod
does not re-award a chest already opened in an existing save.

Every physical copy of a destination must support its source-bound opening. The Hyrule Field
heart-piece chest lacks that contract, so it cannot hold off-dungeon keys, maps or compasses.
It remains shuffled for other eligible rewards; no new opening is assumed.

A key found outside its dungeon names that dungeon in both pickup messages — for example
"Small Key (Forest Temple)" and the caption "Opens one locked door." / "Dungeon: Forest Temple" —
in English in all 16 language archives; dungeon names are read from your dump, not bundled with Clawshot.
There is no new in-game key list: the standing HUD, pause-map counters and floating notices show only the
dungeon you are in. A key credited to another dungeon can show no notice or no counter change
where you stand (in the played gates an overworld pickup showed no increment and an Ice Cavern
one no notice, both with the saved count correct); the notices do not track the key's target
dungeon. The [Tracker tab](tracker.md) shows per-dungeon held and found keys from that seed's own
save, with a compact OBS view; it is separate from the game's current-dungeon counters.

Acceptance: Gates 1–4 passed in game — native and named key chests of both sizes, in-dungeon
and out, child and adult, correct remote credit, door spending and reload persistence, ending
with a whole generated anywhere seed ([dungeon-item play record](../plans/rounds/r12-keys.md)). That is not every
source/target combination or a complete playthrough.

## Hints, models and age warnings

Gossip Stones give English hints in all 16 language archives. `--hints always` is the default;
`--hints mask` restores the Mask of Truth requirement. The balanced distribution includes required-route,
barren-area and item hints. Location hints never name junk. The no-mask lines and corrected highlight
reset were observed in game; that is not certification of every distribution. Both native Sheik
Hookshot-direction lines are replaced with a seed location holding the Hookshot or a Progressive
Hookshot (any copy is the Hookshot while none is owned), or omit the tool if none exists in a
partial world. This text is built/read-back-tested, not separately player-accepted.

The generator also accepts `--hint-distribution strong`, `very_strong` and `useless`.
Strong favors required routes and barren areas; Very strong raises those weights and
allows more dungeon-area hints. Useless gives only original joke lines. No distribution
changes placements, item eligibility or D29's no-junk location clues; an exhausted useful
hint pool still falls back to jokes. All four are app choices. Very strong was played in one new game on
Longshot 3.0.0 (Kareem, 2026-11-23): all ten Gossip Stone texts he checked were correct.

**Static text (partially played):** with dungeon rewards shuffled or a count-mode
bridge, the Temple of Time altar lists reward regions and the selected Door/bridge
conditions. Ganondorf's battle-intro subtitle names the Light Arrow's region; this is
not an earlier interactive hint, and the unchanged native trials normally need the
Light Arrow already. Its timed subtitle stays within two 35-character rows.
With Gift shuffle, the freed Skulltula sons name their actual 10–50 rewards instead
of describing vanilla wallets, the Echo Gem or Bombchus. Those item previews may name
junk; they are not D29 location clues. The five non-Death-Mountain-Trail fountains'
shared refusal now says their gift waits on owning Din's Fire, not a visit to the
summit. Both existing hint modes retain normal NPC/sign access. New custom text is
English in every language; spoken audio and all event timing remain native.
Each reward and region stays on one complete altar line. Door requirements form one
cumulative sentence across pages, followed by the Rainbow Bridge condition; these
condition lines are at most36 characters. Page breaks never split a reward/region.
Kareem passed the staged Fairy refusals, House advice (including after the cure),
legible Ganondorf subtitle, and bridge-scrub price/grant. On Longshot 3.0.0 (2026-11-21)
the other three scrub offers (Lost Woods grotto front, Hyrule Field password, Death Mountain
Crater ledge) also named their real items, and the revised altar passed: one reward per line,
the Door of Time as one sentence and the Rainbow Bridge line. Ganondorf's subtitle shows during
his skippable voiced line ([hints play record](../plans/rounds/r20-hints.md)). Other Door and
bridge modes and languages are not each played.

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
