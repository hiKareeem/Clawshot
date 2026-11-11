# Round 11: hand-over ocarina crash (cs11f)

## Scope and safety

Requested by Kareem/Claude: investigate the public seed 10 Market child gallery crash;
constrain unsafe item/delivery combinations during logic-aware fill, not afterwards.
Base main `b1253a7`, branch `r11/ocarina`. No version, dependency, loader or save changes.
All game data and generated output remain outside the repository in
`E:/OOTRemake/work/r11-ocarina-cs11f/`. Dump, tester report, existing outputs and save
backups are read-only. No game process or launcher is started by this agent.

## Reported failure and evidence

Tester: Hookshot 2.0.14, German, seed 10 from
`work/r11-packs/clawshot-seed-10-2026-11-10d.zip`.
Pack output SHA256: `45358d89b14bb3716fa7bbb7838b76163d5f5ee8f7d8a0638e27f4aa93a09984`.
Read-only seed: `work/r11-packs/check-10-2026-11-10d/seed/`.
Market gallery reward: Ocarina of Time (`Item_Ocarina_Time`).
Log: `work/tester-reports/2026-11-11-juna-gallery/hookshot_log.txt:44228-44239`:
BaseProcExecutor3 access violation reads guest address `0x270`, x0 is zero;
x6/x7 contain the start of `MiniGame_HitTarget`. This establishes a near-null read,
not its owning native function.

**Confirmed reproduction (Kareem via Claude, current conversation):** English
`en-US`, Hookshot 2.0.14, Jabu backup child `slot_01`, seed 10 game files as the
only mod, Teleport to Market, win the Slingshot Gallery. Same exception/address,
host offset `hookshot.exe+0xe3fd73d`, identical guest backtrace and x6/x7 text.
Read-only log copy:
`work/save-backups/2026-11-11-r11-gallery-ocarina-repro/hookshot_log.txt`.
This rules out a German-only issue and a tester-PC-only issue. The supplied
observation is accepted directly; no agent reproduction or confirmation run.

Claude's comparison identifies only the reward parameter at Event378/Event241 as
different from the successfully played Echo Gem child-gallery experiment.
Recorded positive controls: `03-game-data.md` section 40 and
`playtest/answers.md` R10-MINIGAMES-CHILD-JABU, R10-DIGGING,
R10-MARKET-BOTTLE-FIX and R8-FROGS. Static subflow audit in progress.

## Provisional choices

### Exact pack comparison and existing placement-policy gap

`compare_exact.py` in scratch reads the requested **10d** output, not Claude's
older comparison script's `10c` path. Both charts contain 646 events, identical
actors and entry points. The child reward pair Event378/Event241 differs only
in `ReveiveItem` (Echo Gem versus Ocarina of Time). The complete file also
differs at the adult pair Event242/Event381 (Epona's Song versus Poacher's Saw);
that is not a difference on the reported child reward branch.

`data/settings.toml` admits Fairy Ocarina to chests but omits Ocarina of Time.
`playtest/answers.md` R8-GETITEM explicitly confirms both chest pickups work and
Time Ocarina plays songs. Thus `gifts.held_items` currently forces Time Ocarina
into gift types, while Fairy Ocarina remains eligible for those same types.
The correction must both recognize the recorded Time Ocarina chest evidence and
exclude unsafe hand-over destinations.

Synthetic read-only reproduction (`reproduce_fill.py`, seed 1): Fairy Ocarina
lands at Gift with no restriction; Time Ocarina lands there with allowed types
NPC/Cutscene/Boss. The other chest requires the instrument, so the regression
must show an early reachable chest rather than an arbitrary post-fill move.

- Proposed by cs11f, following the request: preserve the existing fill restriction
  mechanism; do not repair placements after reachability has been proved.
- Do not equate a default branch with an unsupported item: compare the actual
  operations and actor data with played controls first.
- Job 3 is conditional on a small, evidenced data gap; no speculative shared-flow
  patch or game launch.

## Delivery-route audit

`export_audit.py` reads the dump's active flow versions (640 flowcharts), then
`delivery_routes.py` applies the real gift patcher to all 60 potentially enabled
gift checks using a representative Boomerang assignment. It recursively walks
each grant's callee entries before and after patching. No missing callee or entry
was found. Full decoded artifacts stay in scratch `audit/`; the table below is
only location identities and factual classification.

The maximum set includes Darunia's gift when free time travel is enabled.
Default return guarantees can retain that gift unchanged. Other existing holds
(expert galleries, merchants, unresolved checks) are not released by this work.

| Delivery route | Shufflable location names |
|---|---|
| GetInEvent: forest | KF Shopkeeper Gift; LW Skull Kid; LW Trade Odd Potion; LW Ocarina Memory Game |
| GetInEvent: ranch/lake | LLR Talons Chickens; LH Lab Dive; LH Child Fishing; LH Adult Fishing |
| GetInEvent: Gerudo | GV Trade Poachers Saw; GF HBA 1000 Points; Hideout Gerudo Membership Card |
| GetInEvent: Market | Market 10 Big Poes; Market Shooting Gallery Reward; Market Bombchu Bowling First Prize; Market Bombchu Bowling Second Prize; Market Potion Shop Bottle; Market Lost Dog |
| GetInEvent: Kakariko | Kak Anju as Adult; Kak Anju as Child; Kak Anju Trade Pocket Cucco; Kak Man on Roof; Kak 10 Gold Skulltula Reward; Kak 20 Gold Skulltula Reward; Kak 30 Gold Skulltula Reward; Kak 50 Gold Skulltula Reward; Kak 100 Gold Skulltula Reward; Kak Shooting Gallery Reward; Kak Granny Trade Odd Mushroom |
| GetInEvent: graveyard/mountain | Graveyard Dampe Gravedigging Tour; DMT Biggoron; DMT Trade Broken Sword; DMT Trade Eyedrops; GC Darunias Joy |
| GetInEvent: Great Fairies | Colossus Great Fairy Reward; OGC Great Fairy Reward; DMT Great Fairy Reward; ZF Great Fairy Reward |
| GetInEvent: river/domain | ZR Frogs Ocarina Game; ZR Frogs Zeldas Lullaby; ZR Frogs Eponas Song; ZR Frogs Sarias Song; ZR Frogs Suns Song; ZR Frogs Song of Time; ZR Frogs in the Rain; ZD Diving Minigame |
| Direct pouch grant, no GetInEvent | LW Gift from Saria; HF Ocarina of Time Item |
| GetPouchContent, no GetInEvent | ToT Light Arrows Cutscene; Song from Saria; Sheik in Forest; Song from Ocarina of Time; Song from Malon; Sheik at Colossus; Sheik at Temple; Song from Impa; Sheik in Kakariko; Song from Windmill; Song from Royal Familys Tomb; Sheik in Crater; Sheik in Ice Cavern |
| GetInEvent, separate Scrub shuffle | HF Deku Scrub Grotto; DMC Deku Scrub; LW Deku Scrub Near Bridge; LW Deku Scrub Grotto Front |
| Chest events | All shuffled ordinary chests, including Dampé's **race** Hookshot chest (not his digging gift), use Dm_SY_TreasureboxSmall/Dm_SY_Treasurebox after the existing story-override handling. |
| Shops/floor rewards | Shops use their purchase flow and item-display allowlist; floor Heart Pieces and boss hearts use pickup actors and their five-item palette. These already exclude both ocarinas. |

Thus 45 of the 60 gift checks can reach show-item creation in GetInEvent;
15 bypass that presentation path. Four one-time Scrub checks also use GetInEvent
(`Enemy_Scrub_Business_Common` Event2/Event4 -> GetInEvent_NotTurn_2DShop).
The five ordinary frog-song calls are specialized by the gift patcher; the bottle
tutorial's replacement also uses the generic gift wrapper. Native story ocarina
grants do not use that wrapper.

Proposed by cs11f: constrain the actual hand-over locations, **not all NPC,
Cutscene or Song locations**. That preserves the native safe ocarina scenes and
does not make Gift-only settings impossible merely because no chest is selected.
Include the Scrub destinations: with mixed shuffle, the old Fairy Ocarina could
otherwise be placed there.

## Before-fix verification

- `CLAWSHOT_WORKERS=1 uv run --frozen python E:/OOTRemake/work/r11-ocarina-cs11f/sweep.py before`:
  seeds 1–50 on Defaults and the exact pack's settings all pass the beatability
  oracle (100/100). Defaults have 165 checks; pack settings have 300.
  The latter place Time Ocarina at a gift in all 50 seeds, including the reported
  Market gallery in seed 10. These are logic proofs, not safe-runtime proofs.
  Complete placement/settings snapshots: scratch `before.json`.
  One process; the gate lock was acquired and released in `finally`.
- Focused regression before the fix:
  `CLAWSHOT_WORKERS=1 uv run --frozen pytest tests/test_settings_songs.py -k ocarina_fill -q`:
  **4 failed, 3 deselected**. The printed assertion values show seed 1's early
  chest contains Boomerang instead of either ocarina; the instrument is at the
  unrestricted gift. Both song modes expose the same unsafe destination policy.

## Item/subflow audit and crash assessment

Coverage: **143 logic-to-actor mappings, 113 distinct grant actors**; every actor
has a PouchActorInfo row. Items without a mapping cannot be emitted by the
generator. The mapping set includes currently retained vanilla checks (Egg,
Letter, some upgrade rewards); listing them does not release them.

### Shared behavior for every mapped item

| Requested subflow | Explicit case/entry versus fall-through |
|---|---|
| GetInEvent_NotTurn_Sub | No item-name case. Event254 unconditionally calls Player_Event.EventCreateShowItemFromActorFileName with the item, then camera save, look lock and GetInEvent_SetLocator. |
| Item_Position | No item-name case. Event10 forks: set model LOD then Event51 EventIgnitionShowItem (`Rotate_GetDemo`); one-frame delay then the item's fanfare/effect. |
| GetInEvent_Animation | Explicit **native query** dispatch, not an item-name table: child/adult, then Event277/Event279 PouchContentGetType. Case0 uses DemoGet; cases1/2/3 share DemoGet_Smile, with camera/Navi/depth-of-field branches. |
| GetPouchContentByActorName_ForGetInEvent | Every item enters GetPouchContent: set message target, OpenGetWindow, optional rupee count UI, add one actual item, close rupee UI, conditional autosave. No special ocarina grant is missing. |
| Dm_SY_Get / CheckHeart | Native predicates distinguish max-life increase, heart piece, fairy and heart/MP recovery. Matching items reach gauge/recovery work; ordinary items fall through. No ocarina-name case. |
| ActionGuide / ActionGuide | Explicit native category dispatch, followed by inventory/tutorial-state gates. Category results0/3/4 use type52,1/5 item-menu guides,6 type61,9 type44,10 type45;2/7/8 have no arm. No ocarina-name case. |

OpenGetWindow's native CheckUIMessageTargetActorName has the complete EVFL
result-to-entry map: 0 DefaultGetMessage;1 HeartPiece;2 TokenGold;3 bottle
subprocess;4 MiniGame_SmallKey;5/6/16 ReleaseMagic;7 Stone_Fire;8 Stone_Water;
9/10 EarlyFadeOut;11 ClaimCheck;12 HeavyBoot;13 HoverBoot;14 Longshot;
15 Sword_Biggoron. All arms rejoin OpenGetWindow_End.

**Static limit:** these are integer-returning native queries. EVFL does not
contain their actor-to-integer implementations. The declared type/category/
guide columns below identify each item's inputs, **not an invented native
result integer**. In particular, no numbered get-type branch or window default
is asserted for either ocarina. Tutorial state can also suppress a guide.
This audit does not certify every item/location combination in game.

### Per-item declared selectors

For every row, NotTurn_Sub and Item_Position take the unconditional shared
entries above; animation, window and guide use the native dispatchers above.
Get type is shown as L=Large, S=Small, M=Medium, H=Heart. `—` means no explicit
ActionGuideType field, not proof that every guide is skipped. Actor identities
are those in `data/item_actors.toml`; dungeon rows enumerate all shared mappings.

| Logic item(s) | Get type | Category / guide selector | Heart/recovery special handling |
|---|---|---|---|
| Fairy Ocarina | S | KeyItem / — | ordinary fall-through; Ocarina inventory deal |
| Ocarina of Time | L | KeyItem / — | ordinary fall-through; Ocarina inventory deal |
| Bolero of Fire; Eponas Song; Minuet of Forest; Nocturne of Shadow; Prelude of Light; Requiem of Spirit; Sarias Song; Serenade of Water; Song of Storms; Song of Time; Suns Song; Zeldas Lullaby | S | KeyItem / — | ordinary; Melody deal |
| Stone of Agony (Echo Gem) | L | KeyItem / HeadShortcut | ordinary; AgonyStone deal |
| Boomerang | L | Material / Boomerang | ordinary |
| Kokiri Sword | L | Weapon / AttackByWeapon | ordinary |
| Slingshot; Bow; Ice Arrows; Light Arrows | L | Bow / SlingShot, Bow, IceArrow, LightArrow respectively | ordinary |
| Megaton Hammer; Hookshot; Longshot | L | Material / Hammer, Hookshot, Longshot respectively | ordinary |
| Silver Gauntlets; Golden Gauntlets | L | KeyItem / — | ordinary; Gauntlet deal |
| Goron Bracelet | L | KeyItem / GoronGauntlet | ordinary |
| Iron Boots; Hover Boots | L | Boot / BootShortcut | ordinary |
| Lens of Truth | L | HeadArmor / HeadShortcut | ordinary |
| Mirror Shield; Hylian Shield | L | Shield / EquipmentMenu | ordinary |
| Deku Shield | L | Shield / — | ordinary |
| Biggoron Sword | L | Weapon / EquipmentMenu | ordinary |
| Bomb Bag; Bomb Bag (30) | L | KeyItem / Bomb | ordinary |
| Bullet Bag (40); Quiver (40); Adult Wallet; Giant Wallet; Silver Scale; Golden Scale; Gerudo Membership Card; Deku Stick Capacity; Deku Nut Capacity | L | KeyItem / — | ordinary |
| Piece of Heart | M | KeyItem / — | HeartPiece predicates/window/gauge, inventory-state dependent |
| Heart Container | H | KeyItem / — | HeartContainer/max-life gauge path |
| Rupee (1); Rupees (5); Rupees (20); Rupees (50) | S | Rupee / — | ordinary; optional rupee count UI |
| Rupees (200) | M | Rupee / — | ordinary; optional rupee count UI |
| Deku Nuts (5) | S | Material / DekuNut | ordinary |
| Deku Stick (1) | S | Material / DekuStick | ordinary |
| Bombs (5) | S | Material / Bomb | ordinary |
| Bombchus (5); Bombchus (20) | L | Material / Bombchu | ordinary |
| Arrows (5); Arrows (10) | S | Arrow / — | ordinary |
| Map and Compass, each of Deku Tree, Dodongos Cavern, Jabu Jabus Belly, Forest Temple, Fire Temple, Water Temple, Spirit Temple, Shadow Temple, Bottom of the Well, Ice Cavern (20 mappings) | L | KeyItem / — | NotPushToPouch; standing-dungeon handling, section44; hand-over not played |
| Boss Key, each of Forest Temple, Fire Temple, Water Temple, Spirit Temple, Shadow Temple, Ganons Castle (6 mappings) | L | KeyItem / — | NotPushToPouch; standing-dungeon handling, section44; hand-over not played |
| Small Key, each of Forest Temple, Fire Temple, Water Temple, Spirit Temple, Shadow Temple, Bottom of the Well, Gerudo Training Ground, Ganons Castle (8 mappings) | L | KeyItem / — | SmallKey deal; standing-dungeon handling, section44; hand-over not played |
| Goron Tunic; Zora Tunic | L | Armor / EquipmentMenu | ordinary; Shop_Armor actors |
| Buy Heart; Buy Magic Jar; Magic Jar | S | CureItem / — | recovery predicate; NotPushToPouch |
| Buy Deku Nut (5); Buy Deku Nut (10) | S | Material / DekuNut | ordinary |
| Buy Deku Stick (1); Buy Deku Stick (5) | S | Material / DekuStick | ordinary |
| Buy Deku Seeds (10); Buy Deku Seeds (30); Buy Arrows (10); Buy Arrows (30); Buy Arrows (50) | S | Arrow / — | ordinary |
| Buy Fish; Buy Bottle Bug; Buy Blue Fire; Buy Fairy's Spirit; Buy Red Potion for 30 Rupees; Buy Green Potion; Buy Half Milk; Buy Poe | L | Material / Bottle | NotPushToPouch; bottle-content/fairy handling depends on native predicates |
| Buy Bombs (5) for 35 Rupees; Buy Bombs (10); Buy Bombs (20); Buy Bombs (30) | S | Material / Bomb | ordinary |
| Buy Bombchu (1); Buy Bombchu (3); Buy Bombchu (5); Buy Bombchu (8); Buy Bombchu (10); Buy Bombchu (15); Buy Bombchu (20); Buy Bombchu (30) | L | Material / Bombchu | ordinary |
| Bottle; Bottle with Milk | L | Material / Bottle | Bottle deal; bottle-window handling |
| Broken Sword; Claim Check; Cojiro; Odd Potion; Poachers Saw; Pocket Egg; Prescription; Weird Egg; Zeldas Letter | L | Material / — | ordinary; dedicated ClaimCheck window exists |
| Scrub Business Seed | S | Material / — | ordinary |
| Dins Fire; Farores Wind; Nayrus Love | H | Material / DinFire, FaroreWind, NayruLove respectively | spell/MP handling; ReleaseMagic window entries exist, not an ordinary heart-container grant |
| Double Defense | H | KeyItem / — | FairyBlessDefenseDouble deal, not an ordinary heart-container grant |

Performer audit: the two ocarinas are the **only two explicitly resolved Common
performer roots**. Both also use GameActorAfter, Accessory, EquipmentCommon
blackboard and no AS/Animation bundle. Ordinary resolved items use PouchContent;
the two hearts use PouchContentUtuwa; gold rupee uses the pickup/warp variant.
All **33 Shop_* actor packs exist** and their resolved roots have EventMemberRef,
shop AI/blackboard, GameActorDefault and item-shop AS, but no explicit
EventPerformerRef. Their performer is **unresolved**, not claimed to be
PouchContent or Common. An earlier scout/parent interpretation incorrectly
called these missing packs; querying the export's `missing_pack` count gives
zero. Their PouchActorInfo rows also exist. Refill rows remain shop-restricted;
absence of an explicit performer field alone does not prove a hand-over crash.

### Played controls and verdict

| Played through GetInEvent | Observation / source |
|---|---|
| Echo Gem / Stone of Agony | Child Market gallery; R10-MINIGAMES-CHILD-JABU |
| Song of Storms, Epona's Song | First and second bowling prizes; same answer. Epona also adult gallery, R10-MINIGAMES-ADULT. |
| Boomerang | Dampé digging, Market bottle replacement, Kokiri shopkeeper; R10-DIGGING, R10-MARKET-BOTTLE-FIX, R8-SHOPKEEPER-LATE |
| Frog rewards | All seven accepted in R8-FROGS. Recorded item controls include Hammer (Epona), Lens (Time), Longshot (Storms), Hookshot (bug game). |

**[INFERENCE, high confidence]** the cause is an ocarina/show-item presentation
lifecycle mismatch, not a missing pouch row, missing localized text or generic
absence of item-specific cases. Native ocarina scenes grant directly; both
ocarinas work from chests. Songs also lack an AS bundle yet work here, so absence
of AS alone is not a sufficient diagnosis. Time Ocarina's unsafe gallery grant
is confirmed by both German and English reproductions. Fairy Ocarina is excluded
precautionarily under the request: same distinctive equipment/presentation setup,
no positive hand-over test.

**[INFERENCE, medium confidence]** the exact crashing action is in show-item
creation/use/cleanup rather than the pouch grant. The log alone does not name it;
the native query case identities remain unresolved. No claim that a missing
literal ocarina case is the cause.

**Job 3 decision:** no small, evidenced EVFL data gap was found. Do not build a
speculative mod that changes playable ocarina components or guesses a new prop
lifecycle. A RomFS-side repair is not proved impossible; it is simply not
established by this audit. Proceed with the placement constraint.

### Native crash-address correlation (read-only follow-up)

The existing permissive inspection helper
`work/r9-itembar-cs9a/native.py` reads the player's own NSO; ephemeral Capstone
was used without changing dependencies. No Hookshot or NX2navi implementation
was copied or used.

`map_guest.py` matches the NSO text in `E:/Games/Hookshot/image.bin` at offset
`0x20000` (rodata has the same offset). Thus the logged return address
`0x829630ac` corresponds to main-relative `0x029430ac`, not `0x029630ac`.
The instruction immediately before it calls `0x00974de0`; that function's first
instruction is `ldr x8, [x0, #0x270]`. The logged x0 is zero and the reported
read is guest `0x270`. This is a direct address/register match, not a guessed
localized-text fault.

The caller at `0x02943040` obtains a resource named **ShowItem**, invokes its
virtual accessor, then passes the result to that getter **without a null
check**. The ShowItem literal is at `0x03cfc180`. The logged x19 vtable also
maps to the current image's `0x04a38f60`. **[INFERENCE, high confidence]** the
missing show-item actor is the immediate cause. The EVFL action name owning
this native routine is still unbound; creation, use versus cleanup timing is
not certified, and inventory may already have been granted. Do not claim that
the pouch grant was necessarily never reached.

Reproducers and printed diagnostics are all in scratch:
`map_guest.py`, `native_site.py`, `native_registry.py`; native helper commands
`dis 2943030 e0`, `dis 974de0 80`, `xrefs 4a38f60`.
An initial inspection incorrectly subtracted only `0x80000000`; the printed
NSO/image segment matches established the corrected base before interpretation.
