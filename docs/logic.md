# Logic reference for ports and trackers

Clawshot's access model is reusable data, not a claim that N64 rules match this remake. This guide
maps the data and contracts for a tracker or a possible Archipelago world. Paths below are relative
to the repository root. The detailed specification is [world format](../plans/04-world-format.md);
licences and exact upstream revisions are in [NOTICE](../NOTICE).

## Data map

| Path | Contract |
|---|---|
| `src/clawshot/data/world/world.toml` | Start region, goal, file list, overrides, local settings/items/helpers and progressive tiers. |
| `src/clawshot/data/world/port.toml` | Translation inputs, Banc area mapping and pinned OoT Randomizer commit. |
| `src/clawshot/data/world/*.toml` region files named by `port.toml` | Translated regions, exits, events and location metadata. Do not hand-edit these generated files. |
| `src/clawshot/data/world/helpers.toml` | Named and parameterized rule helpers, translated from OoT Randomizer. |
| `src/clawshot/data/world/items.toml` | Item types/classes, aliases and properties used by search. |
| `src/clawshot/data/world/settings.toml` | Translated settings, tricks and world flags used by rules. Not the generator's user-facing defaults. |
| `src/clawshot/data/world/remake.toml`, `src/clawshot/data/world/remake/*.toml` | Sourced remake corrections, exclusions, new regions/checks, items and helpers. |
| `src/clawshot/data/settings.toml` | Generator defaults and placement restrictions; distinct from translated logic defaults. |
| `src/clawshot/data/locations.toml` | Placement identity definitions and links to world location names. |
| `src/clawshot/data/location_names.toml` | Player-facing labels, directions, physical IDs and map-floor descriptions. Presentation is not a new identity or access rule. |
| `src/clawshot/patch/gift_rules.toml` | Event grant identities and patch policies for supported gifts. |
| `src/clawshot/patch/logic_world.py` | The one dump-free builder of the world a seed's search ran on, shared by the seed pipeline and the tracker; see [Tracker in-logic contract](#tracker-in-logic-contract). |
| `src/clawshot/data/tracker_logic.toml` | Tracker save cells → logic item names, story-step save flags, and an `unmapped` table giving a reason for every other progression name. |

Sources: `plans/04-world-format.md` sections Files, Overrides, Items/helpers/settings and Replayable
generator settings; `plans/03-game-data.md` sections Readable location names and Event gifts;
`NOTICE` for the provenance of translated data and algorithms. The world translation tool is
`src/clawshot/world/translate.py`; its inputs must match `port.toml`'s pinned commit, and the
translation comparison is in `tests/test_world_translate.py`.

### Overrides and evidence

`src/clawshot/world/load.py` applies `remake.toml` first, then `remake/*.toml` in sorted name order.
A location, exit, event, region, key count or item cannot be set in two override files. New regions
are added before their contents are resolved. A changed rule states `was` as well as `rule`; upstream
changes must not silently invalidate the correction. Overrides carry a `source` explaining the
ported file/line or remake evidence. See `plans/04-world-format.md`, Overrides.

The same specification defines `n64_only` (not a remake check), `keep_vanilla` (present but not
shuffled), `vanilla_fixed` (a concrete tier), and `new = true` (a remake addition). Preserve those
meanings in a port. Do not turn a held check into a randomized check just because it has a rule.
The current acceptance boundary is in [settings](settings.md), with observations in
`plans/playtest/answers.md` and the [roadmap index](../plans/00-roadmap.md) plus its linked play records.
Cow work remains research only; no cow shuffle option or production check shipped
([cow research](../plans/rounds/r19-cows.md)).

**Ranged pickup audit:** the windmill platform pickup requires the existing adult
Dampé approach; child Boomerang retrieval failed in BBender's report and the native Heart Piece
actor has no liftable component. The Graveyard Heart Piece's disabled Boomerang trick is also
removed. The cow-shed pickup does exist, with its own actor and map anchor in all three village
variants; its owl/Hookshot roof route is unchanged. The nonexistent Ice Cavern loose blue rupee
is excluded. Native tokens have a different, liftable pickup contract: this is not a blanket
Boomerang ban. [Per-rule evidence and unplayed alternatives](../plans/rounds/r20-audit.md).
Dodongo's torch-room route accepts plain adult arrows through its permanently lit candle: Kareem
played that method on Longshot 3.2.0 (0.2.6), without Fire Arrows. Child Sticks and Din's remain valid.
Its three candles open the room-8 door to the room-9 floor switch, which opens the staircase door;
they do not directly open the latter. The adult's possible 3 m lobby ledge shortcut remains unplayed.

**DMT cavern-roof Heart Piece:** adult Link must ride the bean sprout. The rule retains
`here(can_plant_bean and (plant_beans or has_explosives or Progressive_Strength_Upgrade))`,
including access to the planting spot; neither damage/backflips nor Hover Boots substitutes for it.
This is Kareem's approved tightening (2026-11-27, Bender audit R10), not a new movement-trick
admission or an extra play requirement. The child cannot collect it even with bean-plot access.

**Deku Sticks and Nuts: pots are not a source.** A child has sticks in logic from held or bought
Deku Sticks (`Buy Deku Stick (1)`/`(5)`, or a shuffled `Deku Stick (1)`) or from a child Kokiri Sword
kill of a Deku Baba (`Deku Stick Drop` in KF Outside Deku Tree, the Deku Tree Lobby and the Forest Temple's
two courtyards). Adult Baba kills never supply sticks: the native drop-unlock table gates dropped sticks
on childhood, with green-rupee replacements. The Boomerang's stick yield is unproven and is not counted.
Kareem, Longshot 3.2.0, Clawshot 0.2.6 (2026-11-24), saw sideways sword kills give sticks and Bow/bomb kills
give nuts, including as an adult with no sword. Adult nut sources accept those real kill methods even
with Master Sword shuffle; an unowned sword never counts. Nuts have a forest-story unlock, not the stick's
childhood gate. They also come from shops or shuffled `Deku Nuts (5)`/`(10)`.
OoT Randomizer's "Stick Pot" (Goron City, Zora's
Domain, Bottom of the Well) and "Nut Pot" events are closed (`remake/pot_drops.toml`): Kareem found Goron
City's pot gives one stick, refilled only by leaving and re-entering; the remake's other stick pots are the
same kind, Bottom of the Well has none, and no pot holds a fixed nut (a pot without a set drop gives one only
by chance). Loose sticks outside pots (Deku Tree grass, a Lake Hylia floor stick) are not in logic: unplayed.
The tracker's in-logic view rebuilds the same world, so it follows.
[Pot-source evidence](../plans/rounds/r21-sticks.md), [Baba drop audit](../plans/rounds/r22-tracker.md).

**Child Gold Skulltulas need a kill (0.2.6).** A token is the death drop of its Gold Skulltula, so a
child token needs `can_child_attack` like the rest: `LLR GS Tree` and `Market GS Guard House` (Kareem, in
game: the Skulltula pops out of the tree or crate and must be killed), `ZF GS Tree` and Kakariko's four
night tokens (`remake/child_gs_kills.toml`, `remake/child_kakariko.toml`) were the OoT Randomizer rules
without one. [Audit](../plans/rounds/r21-sticks.md).

**Megaton Hammer as explosives and as an adult weapon (0.2.6):** every cracked wall, cracked floor
and boulder actor inherits `WallCrack`, whose damage table gives the Hammer the same rate as bombs
(100; arrows, the Hookshot, fire and most other attacks 0); bomb-grotto covers share that table.
Kareem broke walls of that actor, boulders and bomb grottos with the Hammer on 0.2.5. Rules whose
explosives open one of those actors read `can_blast_or_smash` (explosives or the adult's Hammer);
`remake/hammer.toml` holds the translated ones, and each entry names its actor. Ordinary enemy
fights read the world helper `adult_weapon`
(a durable blade or the Hammer), which matters only with Master Sword shuffle on. The ground Beamos
(`Enemy_Beamos`, Spirit Temple's Beamos hall and Gerudo Training Ground's Beamos room) also takes the
Hammer: Kareem destroyed one with a single Hammer hit (Longshot 3.0.0, 2026-11-23). The adult's
Mirror Shield also kills it by **redirecting its beam back onto it**, not merely blocking (Kareem,
Longshot 3.2.0, 0.2.6); only Beamos-kill predicates gain that alternative, not cracked walls. Kareem accepted
extending that kill to Spirit Anubis Room → Beyond Anubis, GTG Beamos Chest and GTG Lobby → Lava Room Front
(2026-11-25); their other fight and heat requirements stay, and no high Beamos or unidentified target gains it
([Mirror Shield evidence](../plans/rounds/r22-logic.md)).
King Dodongo (bombs, or Bomb Flowers with the Bracelet), the Shadow Temple skull pots and webs
(Hammer rate 0), eye switches, in-place Bomb Flower chains, high-Beamos Hammer reach and boss
fights keep their prior requirements. [Hammer evidence](../plans/rounds/r21-hammer.md).

**Adult Bomb Flowers:** audited Dodongo's Cavern local flower routes admit a fixed Goron Bracelet
as adult Low lift without inventing a progressive strength copy. The same played capability now
opens Goron City's Lost Woods shortcut and stops its adult Rolling Goron; other Goron City flower
routes remain conservative. In Dodongo's Cavern, ordinary adult arrows also kill the Lizalfos pairs,
so Bracelet + Bow reaches the Bomb Bag without bag explosives or a durable sword. Flowers must be
carried to each cited wall; a Hammer hitting a growing fruit does not imply transport or a working
staircase chain. No global strength/rock policy changes. [Per-rule audit](../plans/rounds/r22-logic.md).

**Bombchus need the Bomb Bag (0.2.9).** Kareem (Longshot 3.2.0, a 0.2.6 seed, 2026-11-24): Bombchus
bought before the Bomb Bag showed a count of 0 and could not be used, also with the Goron's Bracelet,
and no strength refusal played; the bought amount appeared once he had the bag. Every Bombchus helper
requires `Bomb_Bag` whatever `free_bombchu_drops` says (`has_bombchus` and `found_bombchus` in
`remake/bombchus.toml`, `can_refill_bombchus` in `shops.toml`), so `has_explosives` and
`has_both_explosives` count Bombchus only with the bag; none needs lift strength. The setting, on in
every seed, still picks the supply: on, a found Bombchus item (and only then are Bombchus explosives);
off, a purchase, with `found_bombchus` the bag alone. Before, a Bombchus item held without a bag
counted as explosives: in the tracker, a bought stock read from the save; in generation, a pack that
stayed vanilla (the Wasteland Bombchu Salesman, then held vanilla in every seed, and the 40-token reward
unless gifts were shuffled). Shuffled packs already went only where the bag is guaranteed (D25); with Gift
shuffle the salesman's pack is now one of them (merchants below). The tracker's in-logic view rebuilds the
same world, so it follows. [Decision D30](../plans/decisions.md).

**Merchants under Gift shuffle.** With Gift shuffle, `GC Medigoron`, `Kak Granny Buy Blue Potion` and
`Wasteland Bombchu Salesman` are shuffled checks. Each sells one shuffled item once at its native price
(200, 100 and 90 Rupees); the patch saves the check only after a completed purchase, and later visits run
the untouched native sale. Afterwards Granny fills an existing empty bottle with Blue Potion for 100 and
never adds a bottle, the carpet seller sells Bombchus for 90, and Medigoron sells a replacement Giant's Knife
only after a genuine Knife breaks (with an intact Knife, "come back if it breaks" is dialogue, not a sale).
Without Gift shuffle all three keep their native sales. Medigoron's rule is `is_adult and can_blast_or_smash`
(his room access stays) and Granny's keeps her empty bottle and Odd Mushroom trade prerequisites; neither
requires `Progressive_Wallet`, because both prices fit the default 200-Rupee wallet. On Longshot 3.2.0,
unmodded with no wallet upgrade (2026-11-26), Kareem bought the Giant's Knife (rupees 200→0,
`Weapon_Sword_Giant` 0→1) and Granny's Blue Potion (100→0, an empty bottle filled); on test seeds
(2026-11-27) he bought shuffled items from all three (200→0, 100→0, 90→0), then their native repeat sales.
Owning the Biggoron Sword does not block Medigoron's check: the patch neutralises his sword-ownership reads
until it is bought (static trace, not played). The carpet seller adds only its inherited `can_jumpslash` to
the shared Wasteland gate, unchanged from 0.2.9: the Gerudo Fortress side, then usable Hover Boots or
Longshot, or the opt-in `logic_wasteland_crossing` trick (default off) that already gates the other Wasteland
and Colossus checks. There is no merchant-specific trick. Granny's plain Blue Potion is a refill, not a bottle,
so it never enters the pool: `gifts.logic_spec` replaces it one-for-one with `Rupees (5)` (no Blue Potion
alias exists); only an explicit `keep_vanilla` pin keeps her native refill.
[Player summary](settings.md#gifts-enabled-versus-held), [play record and traces](../plans/rounds/r22-merchants.md).

**Bag bombs without the Bracelet (experimental, default off):** `bombs_without_bracelet` is paired with
`patch.bombs`, which lowers only `Item_Bomb`'s required lift grade. `remake/bombs.toml` then requires the
Bomb Bag but no strength for `Bombs`; `can_use(Bombs)`, explosives and both Octorok bomb shortcuts inherit it.
Bomb Flowers, child Dodongo's Cavern entrance and other local lift routes retain strength; Bombchus remain
independent and still need their bag. Kareem played it on Longshot 3.2.0 (2026-11-25): with the Bomb Bag and
no Bracelet, bag bombs worked, also after a reload, while Goron City's Bomb Flowers still could not be lifted.
[Native trigger chain and play record](../plans/rounds/r22-games.md).


**Water Temple source gate (0.2.2): confirmed by a played save-edit control.** Entry requires
access to the real Ice Cavern end chest as well as Hookshot and Iron Boots, independent of where
Boots or Serenade are shuffled. This precaution dates from 2026-11-17.
Kareem tested rc.7 unmodded, Debug-made adult with Hookshot and Iron Boots at adult Lake Hylia.
With the quest at `Ready` and `SageOfWater_GetWaterSerenade=false`, the Hookshot did not latch.
On the same save, setting the Ice end-chest wrapper's writes, `SageOfWater_GetWaterSerenade=true`
and `Step_SageOfWater=Step05`, made the switch work and the door open. This confirms that the
Ice end-chest state enables entry; which of the two values matters was not separated. It is a
played save-edit control, not a normal-progression or modded Clawshot certification. See
[the Water gate evidence](../plans/rounds/r16-water-gate.md).

**Zora's River entrance wall:** both directions between `ZR Front` and `Zora River` require
`can_blast_or_smash` or the native `Zora River Domain Arrival` event. Entering from the Lost Woods
does not bypass the downstream wall. Kareem met it going downstream on Longshot 3.2.0 (0.2.6);
this mirrors the already verified upstream predicate, a tightening only.
[Evidence](../plans/rounds/r22-logic.md).

**Jabu Jabu's Compass chest needs no Ruto.** It stays `True` inside `Jabu Jabus Belly Depths`, which already
requires the Boomerang. On Longshot 3.2.0 (2026-11-26), on a test seed, the room-12 chest opened both with Ruto
left in the entryway and with her carried into the room. That is one played purple-rupee reward, not every
reward or save state.

## Rule language

Rules are parsed expressions, **not Python to execute**. The compiler validates and folds settings
once; the remaining predicate reads items, events, age and time. Implementation:
`src/clawshot/world/rules.py`; syntax/lookup/unsupported branches:
`plans/04-world-format.md`, The rule language.

| Form | Meaning |
|---|---|
| `True`, `False`, `and`, `or`, `not`, parentheses | Boolean requirements. |
| `Kokiri_Sword`, `'Kokiri Sword'` | Item identifier; quoted names can also name events. Identifier normalization follows the compiler, not a new port-specific naming scheme. |
| `(Progressive_Hookshot, 2)` | Required count. Counts can also refer to a setting. |
| `is_child`, `can_use(Bow)`, `can_play(Song_of_Time)` | Helpers resolved from helper data and remake overrides, not hard-coded N64 assumptions. |
| `open_forest == 'open'`, `'Deku Tree' in dungeon_shortcuts` | Setting comparisons/membership; tables use their declared data shape. |
| `age == 'child'`, `at_day`, `at_night` | Age/time predicates; time semantics depend on settings. |
| `here(rule)`, `at('Region', rule)` | Region-scoped subrules represented as persistent events; not arbitrary teleports. |
| `has_bottle`, `has_stones(n)`, `has_medallions(n)` | Built-in inventory predicates. The specification lists all supported built-ins. |

Names resolve through built-ins, helpers, items, settings and events as specified by the compiler;
unknown names, helper recursion and unsupported live features fail rather than becoming true.
An inactive constant-folded branch can contain an unsupported name; do not eagerly evaluate it in a
port. N64 tricks default false and cannot be enabled without remake verification.
Sources: `src/clawshot/world/rules.py`, `src/clawshot/world/load.py`, and the rule-language and
Items/helpers/settings sections of `plans/04-world-format.md`.

Items have types and classes (progression, priority, normal), aliases and optional properties such
as bottle/stone/medallion. Dungeon items belong to their declared dungeon. Fixed tiers count toward
the progressive names read by imported rules. Starting items and event grants also participate in
search; the remake has no free starting Fire Temple key. Sources: `plans/04-world-format.md`, Fixed
or progressive items, Items/helpers/settings and Reachability; `src/clawshot/world/load.py`.

**Progressive copies (Kareem, 2026-11-13; `plans/03-game-data.md` section 47).** Generated seeds
always place the eight native chains of `src/clawshot/progressive.py` (`CHAINS`) as counted
copies, with no setting: Progressive Hookshot, Strength, Scale, Wallet, Bomb Bag, Quiver,
Slingshot and Magic. Only chests may hold a copy (other kinds cannot select a tier). Wherever a
native fixed-tier source stays vanilla, the pool holds the full set of copies (N copies for N
tiers, extras replacing ordinary filler) and **logic counts only the copies**: the Nth copy is
tier N. The native reward is a bonus outside that count, so no order between it and the chests
is assumed; it never downgrades, and a copy that finds no tier left is a harmless leftover. The
fixed-tier placement rule applies only to items that stay fixed.

**Deliberate child-strength exception (2026-11-13):** child capability requires Darunia's
native source via his door, Lullaby and Saria's Song, never a copy Bracelet. The gift adds no
copy tier; all three copies remain, adult strength stays copy-only, and Darunia stays native even
with free time travel. An early copy Bracelet
can physically work out of logic. The first adult copy is not assumed in the return-kit lower
bound; the kit must place it. See the [progressive-chest record](../plans/rounds/r14-progressive.md)
for an unplayed post-boulder Darunia source-lock finding.
Progressive Quiver and Slingshot establish the weapon before any capacity; a fixed bag upgrade is not the weapon.
A spell, the Lens or magic arrows open the native meter; at run time that makes the first magic copy give the
double meter, never an extra copy. A port must model these as counted chain items, not as their
first tier's fixed item.

Fixed strength levels **MAX-combine**, never add: Bracelet plus Silver is strength 2, not 3.
**Played evidence (Kareem, 2026-11-12, 21:15):** switching ages with Silver/Golden Gauntlets
does not replace child Link's Goron Bracelet; the child keeps it. The Bracelet is separate
child equipment, not an adult downgrade predecessor. `downgrade_tier_exemptions` therefore
excludes it from both the placement screen and finished-seed order replay.
The conservative **adult Silver → Golden** and **Silver Scale → Golden Scale** restrictions
remain; actual downgrade behavior within those pairs is not game-proven.
[INFERENCE] Adult use of Bracelet strength follows vanilla's Forest-before-Spirit order;
the played age-switch check did not test that ability directly.


## Identity: model names are not physical IDs

A placement is identified by **source file and actor `Hash`**, never its array index, position or
translated N64 actor number. Child/adult/Alternative copies of one check must receive the same patch.
Event gifts use **flow and grant node**. Keep the world key, physical identity and player label distinct.
Sources: `AGENTS.md` rules 4–6; `plans/01-architecture.md`; `plans/03-game-data.md`, How collected
checks are recorded; `src/clawshot/data/locations.toml`; `src/clawshot/patch/gift_rules.toml`.

`oot_randomizer_name` links a known corresponding check; an empty link is not permission to infer
one by list order or distance. Remake-only checks use sourced additions. Floor labels come from map
metadata and describe directions, not identity. Pots and other age-dependent actors can have distinct
Hashes at matching positions. Sources: `plans/04-world-format.md`, Overrides;
`plans/03-game-data.md`, Readable location names, Pause-map floors and Pots/crates/ground rupees.

For a tracker, preserve world keys for placements/rules and use `location_names.toml` for display.
Do not allocate Archipelago network IDs from mutable array order; an eventual port needs an explicit
stable mapping from these identities. That network-ID mapping is a port requirement, not an existing
Clawshot feature (architecture: `plans/01-architecture.md`; current scope: [roadmap](../plans/00-roadmap.md)).

## Search and seed acceptance

The search repeatedly collects every reachable reward, updates events/inventory and explores exits
until nothing changes. Child/adult reachability is separate, with time tracked when enabled. The
configured goal must hold before a generated seed can be written. Sources:
`src/clawshot/world/search.py`, `src/clawshot/generate/__init__.py`,
`plans/01-architecture.md`, The beatability search, and `plans/04-world-format.md`, Reachability.

Before adult return unlocks, child reachability uses an independent pre-pull inventory/event view;
it cannot borrow later adult finds. Native return follows Forest **quest completion**, not owning
a shuffled medallion. The default first-pull guarantee separately proves adult return from mandatory
pull prerequisites and adult checks, without assuming optional child errands. Free travel changes
both logic and native patches; do not copy the search assumption without that patch contract.
Sources: `plans/04-world-format.md`, Ages; `src/clawshot/world/search.py`;
`src/clawshot/data/world/remake/sheik.toml`; `plans/playtest/answers.md`, R9-FREE-TRAVEL and
R10-FIRST-PULL-FIXED. Open-mode early return and preserved escape/moat rewards passed on rc.7.
Kareem reports the Hyrule Field day/night clock working as expected in his seeds (2026-11-21); the
first-arrival lighting repair has no separate staged v5 check. The earlier broader clock-pass claim was
retracted in the [evidence review](../plans/rounds/r18-docs.md#review-corrections-after-3e31f160cb).
See [settings](settings.md).

**No save warp.** The remake autosaves room changes; an older manual save is not a logic escape.
The Slingshot Room's entry now requires its existing usable Slingshot/Boomerang/Bow exit condition as well
as the scrub's shield condition. Neither room chest can supply its own first escape tool. A Slingshot copy
may still be there when another usable exit tool is already available.

`world/softlocks.py` checks returns at the initial frontier and each full collection sphere, preserving
age-specific inventory and arrival time. Targets are physical safe anchors: child Link's House or Kokiri
Forest, adult Temple of Time, never the abstract `Root`. Generated and external placements are refused
when the data's `softlock_verified_regions` certificate fails. Its evidenced scope covers the played
Slingshot Room and Dampé traps and Kareem's warp-only Colossus policy, not the whole world.
Unscoped `audit(world, placements)` reports unresolved graph returns for triage; an absent ordinary
edge is not physical-trap proof. Held warp songs count as returns indoors too (Kareem, played 2026-11-17),
through the same age/instrument rules as normal travel. Farore's Wind ownership proves no saved escape point.

**One-way arrivals.** Dampé's whole grave descent requires usable Hookshot before entry;
neither race reward can supply it. There is no reverse race return, and the windmill climb uses Hookshot,
not the N64 Song of Time. Ordinary windmill access from Kakariko is unchanged. Kareem's no-Hookshot
check on Longshot rc.7 (2026-11-19) refused the race and faded back in front of Dampé, with normal
movement and the existing warp back up usable. It did not return Link to the surface; newer seeds do (below).

**Dampé's first race (0.2.9, played).** The first prize has no one-minute condition: finish the course
and open its chest. Descent/admission still requires a usable Hookshot (either tier). The race stays available
until `IsTreasureBoxOpen.16041366920820397198` is true, including old second-race saves and an unopened retry.
After collection the native second race and its timed prize resume. Kareem played these paths on Longshot
3.2.0 (2026-11-24), so the first chest now admits progression under the ordinary item-family restrictions.
Without either tool, Dampé explains the requirement before race setup, then returns Link to the surface.
[Native trigger chain and played evidence](../plans/rounds/r22-dampe.md).

Child Bolero and both-age Requiem arrivals require an already playable Minuet, Serenade, Nocturne or
Prelude. The final Wasteland leg into Colossus has the same guard, before its one-way boundary.
Kareem ruled Colossus warp-exit-only at either age: reverse desert walking is impractical. Neither
hazardous arrival rescues the other and a destination reward cannot provide its own first escape song.
This affects all new seeds, including Defaults, without changing settings.
[Evidence and unresolved audit questions](../plans/rounds/r18-logic.md).

New seeds also validate the incoming native era-change Kokiri Sword equipment candidate against pouch
ownership before equipping it. An absent sword clears only that candidate; no item is granted and logic
does not gain a sword from time travel. Kareem passed the child-return repair on Longshot rc.7
on 2026-11-19; this is not a claim that every equipment/age combination has been played.

Experimental, default-off Master Sword shuffle requires Chest shuffle and free time travel.
Sword-dependent adult rules then require an owned Master Sword or durable Biggoron Sword, and the finale
requires the owned Master Sword. Two unowned pulls, chest acquisition/equip/use and the owned age round
trip passed on Longshot 3.0.0 stable, 2026-11-20 at 16:21; that does not certify every combat gate or
finale refusal ([Master Sword play record](../plans/rounds/r19-sword.md#final-acceptance--candidate-v4-played-pass--ready)).

Imported Gerudo Fortress rules treat `Gerudo_Membership_Card` as friendly access. In the remake the guards,
desert gate, Training Ground entrance and horseback archery check Spirit quest progress, which the
captain's native hand-over writes after giving the card. D39 keeps `Hideout Gerudo Membership Card`
`keep_vanilla` under every preset and setting, so the card is never in the pool and owning it implies all
four carpenter rescues and that hand-over; the card rules stay unchanged. A port that moves the card
must model completing the captain's source instead: a moved card writes no quest progress. The arrest
route that accepts Longshot where the game checks the Hookshot itself is a separate open review.
Sources: `src/clawshot/data/world/remake/gifts.toml`; D39 in `plans/decisions.md`;
`plans/rounds/r13-gerudo-card.md` (static data trace, not a played route check).

With Fortress jail-key shuffle enabled, one guard/rescue and the repaired once-only 20-rupee drop
passed on Longshot rc.7 (2026-11-19), after the carpenter boss's Yes. On Longshot 3.0.0 (2026-11-21),
four keys from four chests, all four rescues, the card once and Training Ground entry with its 30-rupee fee
also passed with that option ([Fortress play record](../plans/rounds/r20-cows.md)); no new pre-rescue access
is inferred.
The Well floor replacement passed recovery and once-only leave/return/Continue checks.
Shadow's floor key always stays in its usual place, under every setting
([floor-key record](../plans/rounds/r19-keys.md)). See [key placement limits](settings.md#door-of-time-and-returning-to-child).

With dungeon rewards shuffled, the closed Door uses the three owned Stones rather than child boss
completion, retaining the instrument/song/send-off prerequisites. Kareem opened it before Dodongo and
Jabu were done, with no escape/moat scene. With only Emerald and Ruby owned, the Door stayed closed
and no opening scene played; the saved state confirmed the two Stones and closed Door. The first-pull
shuffled reward and a medallion-count bridge below/at its count also passed. These are bounded checks, not a
complete reward-shuffled playthrough. Other completion gates stay native; see [reward settings](settings.md#dungeon-rewards-and-ganons-castle-bridge).

The Light Arrows scene (LACS) and vanilla bridge follow completion of the Shadow and Spirit awakenings,
not owned medallions, including with default settings. This is a logic correction based on **static
event-data evidence only, not played**; the six trials and finale still require usable Light Arrows
([Light Arrows scene research](../plans/rounds/r19-lacs.md)).

The persistent `Met Child Zelda` event models the **whole courtyard/Impa lesson and accepted
send-off through DoorOfTime Step02**, not first courtyard contact. Both moat rewards, Saria's
song source and **every** Door mode require it; shuffled items do not advance native quests.
Its route is Malon's fixed Egg / Chicken, Talon, the courtyard, Impa and an Ocarina.
`Field Owl Arrival` models the saved arrival effect, not literal owl history: native owl play or the real send-off's
missing-arrival restoration supplies it. `Time Flows` and both early Door rules require both events.
The temporary first-adult clock hold is clearable at the native adult Market exit or a genuine
Temple return to child; it is not a persistent search prerequisite. The Market Bombchu Shop also
requires Dodongo's completion and available night. Sources: `remake/child_hyrule_castle.toml`,
`remake/child_hyrule_field.toml`, `remake/child_sacred_forest_meadow.toml`,
`remake/child_market.toml`, `remake/child_temple_of_time.toml`;
[native trace](../plans/03-game-data.md#46-round-14-child-story-and-field-music) and
[clock audit](../plans/rounds/r16-time.md#rc7-played-results-and-clock-follow-up-2026-11-17).
Kareem verified Saria before Darunia and the Step03 escape/reload controls on Longshot on
2026-11-13; Bombchu Shop's entrance correction remains native-data evidence.

**Richard and Cojiro (0.2.6).** Richard the Lost Dog's Heart Piece also requires `Kakariko Village Gate Open`:
the findable Richard exists only after the Kakariko gate guard has read Zelda's Letter; before that the owner keeps
him (at night both stay in her back-alley house, as Kareem saw). Static event-data evidence, a tightening, not played
([NPC record](../plans/rounds/r21-npcs.md)). `Cojiro Access` also requires `Epona`: Kareem found in game that
woken adult Talon stays until Epona is freed from Ingo. Sources: `remake/child_market.toml`, `remake/gifts.toml`.

**Song lessons and no-instrument safety.** Logic conservatively requires an Ocarina for all twelve
`Dm_MelodyGet_*` checks: either instrument at either age. Kareem reproduced the old no-ocarina Minuet
softlock and passed its Ocarina control on
2026-11-18. On 2026-11-20 his [Minuet control](../plans/rounds/r19-scenes.md) (adult, Fairy Ocarina
only, main build) played the native lesson and granted its Boomerang; the earlier issue #34 adult-Fairy control
had already played Sun's Song
([check13](../plans/rounds/r18-equipment.md#check13-acceptance-and-combined-integration)). Lessons therefore no
longer ask an adult for the Ocarina of Time. Generic song playing (`remake/age_ocarina.toml`) keeps its
Time-only adult rule, and existing age, story, source and weapon prerequisites stay. Shuffled gifts
retain the native lesson when either instrument has pouch stock.
The post-lesson Impa send-off and Ice Cavern Water-quest event share the requirement; the moat Ocarina
and Iron Boots chest rewards are given before their lessons, so those reward rules are not gated.
The physical guard now replaces the lesson with a normal get only when **both instruments have zero
pouch stock**, independently of age, selection or historical ownership. That fixes the former
no-ocarina lesson-freeze known issue without relaxing the model's conservative instrument requirement.
On Longshot 3.0.0 stable, 2026-11-20, the morning Minuet/Impa checks skipped lessons and gave
Boomerang; Impa retained normal Hyrule Field dialogue. The separate `skip_saria_farewell` option gave
correct item text and continued straight to Hyrule Field without the farewell movie; Saria's brief
pop-in is cosmetic. The Minuet stock check passed at 14:16 with adult Fairy retaining the native lesson,
then Boomerang, and zero stock of both instruments going straight to a normal get.
Continue/re-entry was not reported; the play record distinguishes the accepted native-arm inference
from its missing load lines ([scene checks](../plans/rounds/r19-scenes.md)).

The fixed `Ocarina` alias MAX-combines Fairy tier1 and Time tier2; it is not a count of two progressive
copies. Issue #34 showed that a later Fairy receipt can overwrite the native selected instrument while
logic retains tier2. New outputs preserve Time selection after the genuine Fairy grant when Time is
owned; stock, `IsGet` and source flags remain native. Kareem passed the child and adult checks on
Longshot rc.7 on 2026-11-19: adult Sun's Song worked and Time remained selected after Continue.
Adult Sun's Song also worked with Fairy in the control; adult-Fairy Minuet has the separate
lesson acceptance above. Neither proves every adult melody; ordinary adult song-playing logic keeps Time.
Older outputs can still select Fairy after Time; ownership history alone does not prove the active instrument.

The independent adult-return proof retains compulsory child story events using the same
count-cap test as items; optional history is excluded. Both early-door construction bounds include
`Met Child Zelda` and `Field Owl Arrival`; the closed kit retains its native inventory/story minimum.

The fill uses seeded assumed fill, placement restrictions and safe swaps, then an independent
collection search on the completed placement. Item pool preparation uses actual remake identities,
not the untranslated N64 vanilla pool. Shops, floor pickups and gifts have destination restrictions;
held/excluded checks remain fixed sources for logic where applicable. Sources:
`src/clawshot/generate/fill.py`, `src/clawshot/generate/__init__.py`,
`plans/04-world-format.md`, Generating a seed and Replayable generator settings; attribution: `NOTICE`.

The default non-progression restriction at the first 100-token House reward is lifted only by the
separate `shuffle_100_token_reward` opt-in, which requires Gift shuffle. Hammer at the first 100-token
reward followed by the native repeating gold rupee passed on Longshot 3.0.0 stable, 2026-11-20
([100-token reward checks](../plans/rounds/r19-tokens.md)). This does not certify every replacement.

Determinism requires the same source/world data, seed and effective settings. Tests include changed
Python hash seeds; unordered placement iteration and timestamps are forbidden. A passing search is
proof of **this model**, not of unplayed remake routes. The earlier Slingshot-room softlock exposed an
N64/remake mismatch; player answers remain essential. Sources: `AGENTS.md` rule 4;
`plans/04-world-format.md`, Generating a seed; [early mini-seed result](../plans/rounds/r3-overview.md);
`plans/playtest/answers.md`, DT01/DT02.

## Spoiler contract

The JSON is local generated output: **do not upload or distribute it**. The producer is
`src/clawshot/generate/__init__.py` (`spoiler`, `spoiler_json`); metadata specification:
`plans/04-world-format.md`, Generating a seed; physical descriptions:
`src/clawshot/data/location_names.toml`. Consumers should handle nullable/optional descriptive data.

| Top-level field | Meaning |
|---|---|
| `generator` | Generator name and package version (`clawshot <version>`); not an exact source revision by itself, so the tracker's in-logic gate also checks the spoiler's locations. |
| `seed` | Seed number. |
| `settings` | Effective settings mapping. |
| `settings_string` | Replayable CS1 representation, requiring the same source/world data. |
| `placements` | World-location key → item for shuffled checks only, not a complete list of fixed rewards. |
| `locations` | Descriptions keyed by those world keys, with catalogue fields and applicable shop/scrub metadata. Custom worlds can lack physical IDs. |
| `opening_route` | A proved child-only opening witness (`name`, `event`, `region`, `steps`), or null. Steps carry kind, location, requirements and alternatives. Not the entire game's route; adult-first seeds can lack this guide while remaining beatable. |
| `opening_route_unavailable` | Null, or `name`, `event`, `region`, `reason` explaining why no child-only opening is listed. No invented pre-pull purchases; the full beatability search remains the seed-validity oracle. |
| `age_locked_pickups` | Wrong-age first-frontier item information, including ties. Not a required play order or a complete pickup-timing analysis. |
| `spheres` | World-keyed progression pickups grouped by search collection sphere; empty progression spheres omitted. Not every collected filler item. |
| `hints` | Stone, where, message label, kind, rendered text, area, location and item; some target fields can be null. |
| `item_names` | Logic item → the name the player sees, for placed items (and the tiers of placed progressive families) whose name differs. A progressive family always keeps its own label. |
| `progressive_grants` | `note` (the route disclaimer) and `locations`: world key → `family`, `possible_tiers` (in order), `canonical_sphere`, `given_in_canonical_sphere_replay` and `leftover_in_canonical_replay` (that tier was already owned); the last three are null where the search never collects it. |

Age-usability source: `src/clawshot/generate/itembar.py`, `plans/03-game-data.md`, Item-bar assignment.
Older-save child Bow failure/recovery: `plans/playtest/answers.md`, R8-SEED8-BOWLOCK/R9-LICHII.
New-game prevention passed Kareem's Bow-first/Boomerang check on 2026-11-12
(`plans/rounds/r13-item-grants.md`); existing saves are unchanged.
Do not reconstruct the complete search using only the progression-filtered `spheres`: include fixed
rewards and the actual world/settings instead (`plans/04-world-format.md`, Reachability).

`progressive_grants` replays the full search spheres in order (native bonuses included as owned
tiers, `clawshot.progressive.next_tier` for each copy, no randomness); `canonical_sphere` counts every
full-search sphere, as the play note does, so it can exceed the length of `spheres`. The tier is
**route dependent**: the child view before return is an independent search prefix, and another
collection order gives other tiers. It is a labelled witness, not a play order or gameplay proof.
Unshuffled ownership-dependent capacity prizes replay their native Medium/Large choice from
that ownership state; a shuffled fixed reward remains its literal assignment.

## Tracker in-logic contract

The Tracker tab's in-logic view and manual marks (contributed by BBender in PR #36) rebuild a seed's
logic offline and search it with what the save holds. Design record and decisions D1–D18:
[tracker in logic](../plans/tracker-in-logic.md); player guide: [tracker](tracker.md#in-logic);
implementation: `src/clawshot/tracker/logic.py` and `src/clawshot/tracker/marks.py`.

**Shared logic-world builder (D15).** `clawshot.patch.logic_world.logic_world(settings, spec=None)` returns
`(settings, world)` for the world the seed's beatability search ran on, without the dump. `validate` plus
`prepare` alone is not that world: before `prepare` the seed pipeline applies two spec steps that change
reachability. `gifts.logic_spec` (Gift or NPC shuffled) applies `gifts.shopkeeper_spec`, which turns the
Kokiri shopkeeper's free Deku Shield event into a placed check that the search would otherwise grant on
reaching the shop. Its only other change gives Granny's Blue Potion sale `Rupees (5)` as its pool item,
unless a `keep_vanilla` pin keeps her native refill.
`scrubs.logic_spec` (Scrub shuffled) adds each one-time sale's wallet tier to its rule. The pipeline
(`gifts.seed_setup`, and `make_seed` through `scrubs.seed_setup`) takes both steps from these same
functions, so a tracker and the generator cannot drift. The other pre-`prepare` changes only hold checks
vanilla, exclude items or set fill palettes. A port rebuilding a seed should use this builder, not a copy
of its steps. Equivalence and no-dump tests: `tests/test_logic_world.py`.

**Version gate (D14).** Logic is rebuilt once per loaded seed, only when the spoiler's `generator` equals
`clawshot <installed version>`, its `settings_string` validates and builds, and every location the spoiler
names exists in the rebuilt world. `generator` carries no commit, so two builds with one version label can
differ in logic. Otherwise `logic.available` is false with a human-readable `logic.reason`, no check
carries in-logic data, and item tracking is unchanged.

**Inventory (D1–D4, D16–D18).** Built only from the tracker's save-read cells through
`src/clawshot/data/tracker_logic.toml`, never from the spoiler's placements; the world's starting items are
added by the search. Per logic name the largest grant of any cell counts, never a sum, and names the world
lacks are dropped.

- Tier cells grant counted chain copies, as seeds count them: a held Longshot is two Progressive Hookshot.
  Bow and Slingshot are their chains' first tiers; quiver and bullet-bag tiers count only while that weapon
  is held. The Ocarina cell grants Fairy Ocarina or Ocarina of Time.
- Trade items, masks, the three shields, Bombchus and Ruto's Letter count when held now **or** their
  acquired-once `IsGet` flag is set. Bombchus additionally require a held Bomb Bag. Every other item counts
  only while held. Deku Sticks and Nuts count only as held stock: a new game sets the nut `IsGet` with no nuts held.
  Magic beans count as held now.
- Bottles follow `has_bottle`: each owned slot without the letter is one `Bottle`; a slot holding Ruto's
  Letter is one `Rutos Letter`, never also a bottle. Contents are not mapped.
- Hearts beyond the starting three count as four `Piece of Heart` each; loose saved pieces are not
  added. Gold Skulltula tokens use the native stock.
- Per dungeon, small keys are the found count including spent keys; boss keys, maps and compasses are
  their saved flags.
- Silver-rupee groups read native saved completion Bools from `[silver_rupees]`: true grants the group's five,
  false grants none, absent is unknown. All sixteen live groups are mapped, including all four castle puzzles.
  GTG lava uses its unique all-five unlock event's history; the other fifteen use room-clear Bools.
  Partial puzzles are not counted; pouches are not invented.
- `Field Owl Arrival` reads `HyruleField_ArriveEntrance` and `Met Child Zelda` reads
  `HavePlayedEvent.Dm_HrlField_0020` (Impa's send-off). Other events and the remake story steps without an
  audited save flag are listed in `unmapped` and derived by the search. A test fails when a progression
  item is neither mapped nor listed there (`tests/test_tracker_logic_data.py`).
- A cell the save cannot read (`?`) counts as not held and is named in `logic.unknown_items`, so the result
  can be more cautious than the game.

**Search.** The inventory goes to `Search(world, items)` as constructor items, the way the generator feeds
assumed items, so the child view behind a closed return gate behaves as in generation. Each name is fed as
the save's count less the starting count (floored at zero), so it counts as the larger of the two. Each
open check carries `in_logic`: `child` and `adult` from `can_access(location, age)`, `either` from
`can_access(location)` with no age; each area counts all three. In the current search `either` equals
child-or-adult, but a port should keep the no-age call. The search is rebuilt only when the inventory
changes. The page's age choice (Either by default, Follow save, Child or Adult) drives the styling, area
counts and **Show only in-logic** filter. Follow save uses `logic.save_age`: `child` or `adult` from the
saved `Sequence_IsChildhood` Bool, or null when it cannot be read, which shows Either with a note.
Longshot's debug age switch does not change that Bool.

**Open checks and manual marks (D5–D10).** A check is open when the save reads it as not collected, or
cannot read it and it is not marked. Only checks the save cannot read (`collected` is null) can be marked,
through POST `tracker-mark` (`check`, `marked`) and POST `tracker-clear-marks` (`confirmed: true`) behind
the local server's token/Host/Origin checks. A marked check is `marked: true`, counts as done, carries no
`in_logic`, adds nothing to the inventory and keeps its item hidden unless spoiler mode is on. When a later
save reads that check either way, the save wins and the mark is removed. Marks live in `tracker-marks.json`
in Clawshot's preferences folder, keyed by seed identity (the manifest's `output_sha256`, else the spoiler
file's SHA-256) and save folder, never in seed, save or game folders. The OBS payload (`tracker-obs`) has
no logic, marks or marks warnings.

Evidence: synthetic-fixture tests (`tests/test_tracker_logic*.py`, `tests/test_tracker_marks.py`). The
maintainers' in-game acceptance (design record, plan item 15) is not recorded. In-logic proves reachability
in **this model**, like every search result here, not a played route.

## What a multiworld port still needs

Clawshot currently generates a static RomFS mod, not a live multiworld client. Archipelago remains
future scope ([roadmap index](../plans/00-roadmap.md), Milestones; decision D8 in `plans/decisions.md`). Reusing the logic does not
automatically provide a playable multiworld integration.

An integration would still need a stable network item/location mapping, check-completion reporting,
connection/session handling, and **items delivered during play**, including durable receipt/reconnect
semantics. A static RomFS mod cannot receive arbitrary items from a network by itself: delivery needs
a hook/API in the runtime plus a client. Runtime code hooks are explicitly a separate future layer in
`plans/01-architecture.md`; these requirements are not shipped interfaces. Keep data licensing
attribution from `NOTICE`, and verify remake routes/grants rather than assuming another runtime or
N64 behavior supplies them. Clawshot's own tracker reads saved games, not live memory
([contract above](#tracker-in-logic-contract)); any other tracker likewise needs its own observation/import
mechanism, and the spoiler is an offline description, not a live state feed.
