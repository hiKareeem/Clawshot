# Round 8, Track E: freestanding items with native pick-ups (cs8e)

Branch `r8/freestanding`. Read AGENTS, README, plans 00–04, decisions, every round-6/7 report,
and the Round-8/shared-file opening. Dump/build `e0f3ccfa` and save backups are read-only.
No game, launcher, window, Hookshot build, terminal-control command, merge, push or stash.
External research: `E:/OOTRemake/work/r8-freestanding-cs8e/`. No dependencies changed.

## Item 1: complete anchor and pickup audit

Executed `uv run python E:/OOTRemake/work/r8-freestanding-cs8e/audit.py`, `summarize.py`,
`all_pickups.py` and `identity.py`. The last two read every non-DreamWorld Banc and resolve
all 7,239 placed actor types' native packs (none missing), including inherited ActorParams.
No decoded tree or game resource enters the repository. `audit.json` and `all-pickups.json`
retain the complete physical ledger outside it.

### All 36 anchors

55 placement copies deduplicate to 36 anchors: **14 placed heart pieces, six ordinary chests,
16 named completion flags**. Section 5's historical 21 named-flag count is not current.
An anchor is a map marker, not an item or saved pickup identity. Preserve it and its links;
shuffle the linked pickup's Hash, never the anchor's Hash. LLR's second reference is its
`LocationArea_LonLonRanch`, not another reward. The Treasure Chest Game uses its named first-clear
flag rather than a direct anchor link; D17 still owns that chest, not Freestanding.

| Check | Anchor Hash | Pickup/chest Hash or named completion Bool |
|---|---|---|
| DMC volcano summit | `12975373498949047978` | `744856631664786545` |
| DMC wall alcove | `16784485264831565984` | `10331043360028932045` |
| DMC scrub | `12493798230772313904` | `DeathMountain_Enemy_Scrub_Business_HeartPiece_01` |
| DMT above Dodongo | `15856934019904510189` | `715147239509454487` |
| Colossus arch | `2308531337658761834` | `10592092054086534681` |
| Fortress roof chest | `267586701490681000` | `12343753510713797715` |
| Horseback archery | `3389467775572858537` | `MiniGame_HorsebackArchery_GotaHeart` |
| GV waterfall | `1077480308077338993` | `16129198288828948135` |
| GV gorge ledge chest | `14813002874583645116` | `15856256242099990922` |
| GC spinning pot | `3483734707455267135` | `GoronLargePot_IsGetHeartPiece` |
| Graveyard heart grave chest | `9353003823584590464` | `9622128545943056087` |
| Graveyard upper ledge | `77201491298807580` | `2157466067026784951` |
| Dampé race chest | `13358460016985463621` | `5534919361313859554` |
| Dampé digging | `10075158462075677237` | `GraveYard_DiggingHoleTour_Drop_HeartPiece` |
| Lake lab dive | `3889886157160285015` | `Npc_Hylia_045_HasDived` |
| Lake lab roof | `8693044901437535425` | `13469300937852836203` |
| HF scrub | `14825051130171187671` | `HyruleField_Enemy_Scrub_Business_HeartPiece_01` |
| LLR tower | `11156084763374250886` | `9814903750835309225` |
| Child fishing | `6175378250368022556` | `MiniGame_Fishing_GetHeartPiece` |
| Lake timed-candle chest | `14128250030289710996` | `2967378296224661060` |
| Kakariko rooftop man | `1416092057268113387` | `Npc_Hylia_001_IsGetHeartPiece` |
| Kakariko windmill | `3518965357024502806` | `13389209437182306002` |
| Impa cow pen | `1051454338871863592` | `17926402522258180222` |
| Skulltula House 50 | `12012336414699946951` | `KakarikoVillage_IsAfterSave_Npc_Hylia_025` |
| Skull Kid | `605877630645816565` | `Npc_SkullKid_Child_IsGetHeartPiece` |
| Skull Kid memory game | `18092305056327665421` | `Minigame_SkullKidSession_IsGetHeartPiece` |
| Lost dog | `8568137720802848289` | `SubEvent_FindRichard_GetHeartPiece` |
| Treasure Chest Game | `5215133574889185473` | `MiniGame_ChoiceTreasure_IsClear` |
| Bombchu Bowling | `11628104451986877978` | `MiniGame_BombchuBowling_ClearThirdTime` |
| Zora torch chest | `12099229167357371868` | `3130048366421939233` |
| ZF bottom | `11514535765115882860` | `8030885465575590602` |
| ZF iceberg | `12439817999368518552` | `12406896586250888098` |
| ZR open-grotto ledge | `3814878871658269103` | `11455676800795329345` |
| ZR near Domain | `6961804965205481566` | `4189391771527808272` |
| Frogs Storms | `18246168067761770276` | `MiniGame_FrogTenors_StormSong` |
| Frogs bug game | `4877056571307262080` | `MiniGame_FrogTenors_InsectRepellent` |

All 20 directly linked reward Hashes (14 pickups + six chests) are permanent
`Bool64bitKey`, reset **24**, save file **0**. All 16 named Bools exist, default false,
reset **8**, save file **0**. The names identify check completion, not ownership of whatever
item a seed puts there. Gift/Scrub/Chest machinery remains responsible for their own checks;
none is duplicated into a Freestanding pool entry.

All 14 heart-piece pickups have **no AiGroup reference**. Preserve placement Phive ID,
Hash, transforms, Presence, anchor links and all group tables. Thirteen are `Obj_Heart_Piece`;
GV waterfall is `Obj_GerudoValley_Heart_Piece` (same inherited heart-piece AI/NoRespawn policy).
Both inherit `Obj_Item_Base`, `ActorLogicSimpleActor`, `ActorGameDataSetting=NoRespawn`.
Their own AI is `Obj_Heart_Piece.root`: pickup death reaches `OneShotHeartPieceTakenDeadAfter`
(node 7). D27 shield/rupee/container replacements use native `DropItem.root` instead, so merely
finding a saved Hash is NOT runtime persistence proof. King Dodongo's actual no-respawn result
(section27) is the precedent; this round's early shield Save/Continue check is still required.

Census linkage gaps: DMC wall **10331043360028932045** (summit-side alcove below the trail
entrance), DMC volcano **744856631664786545** (central high spire), GV waterfall
**16129198288828948135** (north gorge recess). These are existing OoTR checks/rules, not
new access rules. The other 11 placed heart pieces are already linked. Crater geometry and
anchor links settle the physical pair, not file order. GV's other heart is already a chest.

### Other placed pick-ups (complete pack-derived survey)

Counts are unique actor Hashes outside DreamWorld; age/Alternative copies are not extra checks.

| Family | Count | Native persistence / replacement boundary |
|---|---:|---|
| Green / blue / red / purple rupees | 81 / 25 / 4 / 2 | All reset24/file0, NoRespawn, DropItem AI; native palette can replace ordinary pickups in principle; exact remake logic/physical links still needed |
| Recovery hearts / water hearts | 22 / 3 | All reset24/file0, NoRespawn, DropItem; underwater collection/physics is not certified by the boss-floor test |
| Loose nut / seed / stick | 1 / 1 / 1 | All reset24/file0; native DropItem, grouped with underwater Ruto-letter scene; do not alter that scene casually |
| Boss hearts | 8 | Existing BossHeart kind/D27; preserve all scripted spawn gates; not Freestanding duplicates |
| Fire Arrows | 1 | reset24/file0 but known crashing actor; native scripted group; excluded |
| Small keys (Well/Shadow) | 2 | No Bool64bitKey; effective AlwaysRespawn despite NoRespawn base; level logic owns retirement; cannot use a saved-Hash transform |
| Fortress small keys | 8 | Two actors per four key families, no saved actor Hash, AlwaysRespawn plus key-specific AI/Presence; not eight checks |
| Ocarina of Time / Ruto letter | 1 / 1 | No saved actor Hash; AlwaysRespawn and special actor/scene AI; existing event-gift/story handling, not floor-swap-safe |
| Sinking lures | 10 | No saved Hash; AlwaysRespawn; fishing-specific state, not ten one-time rewards |
| Blue Fire | 6 | AlwaysRespawn, no saved Hash; bottle refill source, not a one-time check |
| Fish / insect | 40 / 1 | Fish SupplyObject/reset88; insect AlwaysRespawn/no flag; renewable bottle contents |
| Ordinary fairies / spirit fairies | 30 / 113 | reset25 (Fairy/BancReset); renewable, not permanent pickups |
| Fountain fairies | 56 | AlwaysRespawn, no saved actor Hash; renewable |
| Diving-game rupees | 15 | No saved Hash, AlwaysRespawn, minigame-specific AI; not independent rewards |
| Composer-ghost event actors | 4 | No saved Hash, AlwaysRespawn, special scene AI |
| Milk bottle ornament / weapon bottle / Master Sword | 1 / 1 / 1 | No saved Hash, AlwaysRespawn; display/event actors, not ordinary pickup checks |
| Placed TBox_Rupee_Red | 1 | No saved Hash, no native pickup AI; a get/event representation, not an Obj_ floor pickup |

The census additionally finds **85 silver rupees** (saved type24, `Obj_Rupee_Silver.root` puzzle AI).
They lack ordinary PouchContent and are outside the pack survey's pickup predicate: retain puzzle
completion behavior, not a native shield swap. Shop display families were inspected but excluded
from floor counts; their stock/reset behavior remains the shop track's.

**Provisional boundary / question for Claude and Kareem:** enable the 14 anchored placed heart
pieces first, with the five D27 destination actors only. Ordinary rupee/heart/ammo locations need
exact physical-to-logic links before a seed may use them; no N64 row-count/position guess is a safe
substitute. Keys, refills and scripted story objects cannot use the permanent saved-Hash contract.
This is an explicit eligibility finding, not a claim all 36 anchors are floor pickups or that every
translated Freestanding row has a remake counterpart. Posted the finding on `cs-r8` as `cs8e`.

### Coordination and diagnostics

The requested tilde Bermuda path failed once (exit127): HOME=`C:\Users\hi` expanded into a mixed
backslash/slash executable path. `command -v bermuda` printed the PATH-resolved `bermuda.exe`;
the cause-specific PATH invocation posted successfully. Only thread post/log commands are used.
LSP status: marksman only, no Python language server. No unchanged failed command rerun.
Item1 is research-only; full four gates run on the implementation before any ready/handoff post.
