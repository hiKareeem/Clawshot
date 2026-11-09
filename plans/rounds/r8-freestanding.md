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

**Scope confirmed by Claude, 2026-11-09:** the 14 anchored placed heart pieces only this round,
with the five D27 destination actors. No new rupee/refill/key/silver physical logic this round.
Ordinary rupee/heart/ammo locations need
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

## Item 2: native-only seed integration and controlled output

`patch/freestanding.py`: copy the spec, retype only census-linked placed heart-piece checks
from Collectable to Freestanding, and hold original unlinked N64 Freestanding rows vanilla.
Small keys, digging rewards, chests, gifts and existing exclusions retain their original types/rules.
Every selected check must resolve to exactly one saved native heart-piece Hash in its world area.
Non-native actual-pool items intersect existing type holds to exclude Freestanding; the palette is
imported from `patch.drops.NATIVE_ITEMS`, not a second diverging allowlist. Unmoved pieces retain
their native GV actor variant. No fill algorithm, retry bound, inventory alias or game flag changes.

Transforms change only Gyaml on all age/Alternative copies; reject stale/missing/duplicate actors,
lost Phive identity or a newly introduced script binding. All anchor links and group tables remain.
Native surface/once behavior remains an in-game question, not inferred from field equality.

### Controlled player output (built, never run)

`E:/OOTRemake/work/r8-freestanding-cs8e/ingame/llr-tower-hylian-next/`.
Adjacent launcher **`Test - llr-tower-hylian-next.bat`**, copied from the approved
`r5-gifts/ingame/Test - talon-boomerang.bat`: bin game executable only, update suppression,
missing-exe stop, own `user-llr-tower-hylian-next`, one-time outward copy from read-only
`2026-11-07_llr-tower-before-pickup`. No launcher/dry run/game/window executed.
All six source saves: child, target pickup Hash unset, Hylian Shield absent. Backup SHA256
map unchanged after building. No test user/save was created by the agent.

Real common writer changed only pickup **9814903750835309225** in HyruleField Child Static:
decompressed **395636 -> 395656**, compressed **134949 -> 132472**, allocation
**395912 -> 395944**; the shared resource size table is emitted. Exact inverse Gyaml tree
diff, readback, effective allocation and static launcher checks passed (`build_llr.py`).
`verification.json` records the resource and source-backup checksum evidence outside the repo.

**Kareem:** follow `ingame/llr-checklist.md`: Continue manual slot01; ranch tower, move crates,
crawl to the rear pickup. Hylian Shield on the floor, shield notice and usable inventory, no
heart-piece/max-heart increase. Check uncollected recovery if practical, then collect/Save/quit/
Continue/re-enter: no duplicate. Require the HyruleField Child Static `from the overlay` log.
`ingame/check_llr_save.py` reads only the isolated test user; collected Hash and shield ownership
should both be true. Underwater replacement collection and other palette/location pairs are unplayed.

### Exercised checks and diagnosed failures

- Synthetic/native transform and census/name suites: **36 passed**. Covers five palette actors,
  ordinary/GV source variants, stale identity and script refusal, default-off/unsupported families,
  prior restriction intersections, actual twenty-seed fills, CS1 replay and BossHeart composition.
- All fourteen real floor hearts / **26 copies**: saved reset24/file0 and exact inverse transform
  oracle **passed**. Anchor links exactly cover all fourteen.
- First integrated dump attempt printed `Graveyard Dampe Gravedigging Tour` as an unsupported
  selected Collectable heart. Diagnostic printed all Collectable/vanilla/census identities:
  digging is an event reward, not an anchored floor actor. Corrected eligibility to require the
  actual freestanding census definition; synthetic `Event Heart` regression remains Collectable.
  No access rule or census family was loosened.
- The cause-aimed integration run passed physical eligibility, then exposed a separate fill failure:
  Chest+Freestanding seed7 exhausted the unchanged ten attempts; last failure Boomerang,
  **43 allowed / 57 remaining / four other items**. No unchanged test retry or alternate seed.
- Single-attempt diagnostic (`diagnose_fill.py`) printed the earlier Fire-key frontier:
  **8 allowed / 132 remaining / 21 items**, all eight remaining Fire chests inaccessible.
  Full actual assumed inventory, placed items, allowed/reachable frontier and holds are in
  external `fill-failure.json`; no seed output was written. Posted to Track A/Claude.
  After Claude's explicit handoff direction below, the permanent integration oracle uses independent
  successful sample14; seed7 remains a documented Track A failure, not a success claim.
- Eval's FREEFORM edit bridge rejected a string argument before mutation (`TypeError`, expects dict).
  Tool issue reported; refreshed the unchanged catalog and used the direct edit tool. No source
  data was lost or overwritten by the failed bridge.

### Shared-file checkpoints / coordination

Research item1 committed **a17e372**; definitions-only **afb0ceb** links DMC volcano/wall and GV waterfall;
owned native transforms/synthetic tests **2e060a8**. Shared pipeline, CLI and catalog wiring are isolated
commits and posted as checkpoints, not ready claims before the full gates. No fill.py/settings/dependency
change by this track. Main's plans-only **e3745f5** rebase is authorized at the next clean checkpoint.

### Exact fill handoff (not a successful seed)

Executed failing integration command:
`OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_freestanding_dump.py -q -s
--basetemp E:/OOTRemake/work/r8-freestanding-cs8e/pytest-physical-link-next`.
API arguments: seed **7**, `Settings(shuffle=("Chest","Freestanding"),
cheap_deku_shield=False, hints="mask")`; every other default unchanged (forest closed,
own-dungeon items, chronological return guarantee on). Equivalent CLI reproduction:
`uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 7 --shuffle Chest
Freestanding --no-cheap-deku-shield --hints mask --out <new absent external folder>`.
The equivalent seed7 CLI is a reproduction instruction, not an additional agent run.

The one-attempt diagnostic uses the same actual census pool/prepared spec and `Random(7)`,
calling fill once to print state instead of rerunning the ten-attempt failing check.
Fire Temple's already-placed values at the first failure:

| Location | Item |
|---|---|
| Fire Temple Big Lava Room Lower Open Door Chest | Boss Key (Fire Temple) |
| Fire Temple Boulder Maze Lower Chest | Small Key (Fire Temple) |
| Fire Temple Room 8 Chest (TBox_Rupee_Red) #1 | Small Key (Fire Temple) |
| Fire Temple Highest Goron Chest | Small Key (Fire Temple) |
| Fire Temple Map Chest | Small Key (Fire Temple) |
| Fire Temple Big Lava Room Blocked Door Chest | Small Key (Fire Temple) |
| Fire Temple Compass Chest | Small Key (Fire Temple) |
| Fire Temple Near Boss Chest | Small Key (Fire Temple) |

The eighth small key has eight allowed candidates, **all inaccessible**: Boulder Maze Shortcut,
Boulder Maze Side Room, Flare Dancer, Boulder Maze Upper, Megaton Hammer, Scarecrow,
Boss Key, and Room 8 Red #2 chests. **132 destinations** remain (118 Chest,14 Freestanding);
21 other restricted items remain. No shuffled Sword/shield/Boomerang/Slingshot has been placed
yet; they are in assumed inventory at this stage. Full exact placements (including held vanilla),
assumed inventory, restrictions, all remaining locations and per-candidate regions/access:
`E:/OOTRemake/work/r8-freestanding-cs8e/fill-failure.json`. Diagnostic executable:
`uv run python E:/OOTRemake/work/r8-freestanding-cs8e/diagnose_fill.py`. Posted to `cs-r8`.

A separate actual CLI sample **seed3**, same settings, also refuses after10 attempts
(last Fire small key,7 allowed/132 remaining/21 items); its complete transcript is
`cli-seed3-0.log`, no output folder written. A bounded distinct-seed diagnostic measures
seeds0–19 once each and prints each failure payload; it does not retry seed7 or relax a rule.

**Reviewer direction (Claude, 2026-11-09):** Track A owns the fill fix; carry on with Track E.
Handoff may rely on the synthetic proof and Chest+Freestanding samples that do generate.
The seed7 failure stays explicit, not disguised as a successful seed or a gameplay result.

Bounded one-attempt measurement completed for all20 distinct seeds: **2,14,18 pass**, in
24/26/28 collection spheres. Other failures are Fire small-key capacity or D25 Bombchus
with zero to six remaining candidates, none accessible. Exact per-seed remaining/assumed
values are in `seed-capability-measurement.json`; only this diagnostic used one attempt
(stricter than normal, not an increased bound). It did not write overlays or choose an
easier logic/settings combination. Public sample2 and independent dump sample14 keep the
same fourteen checks, native palette, closed forest and chronological return guarantee.

Latest focused checks:
- `uv run pytest tests/test_freestanding.py tests/test_names.py -q`: **33 passed**,
  including twenty seeds requiring a native Hylian Shield specifically from a floor check,
  with its actual resulting Gyaml transform exercised.
- `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_freestanding_dump.py
  -k seed -q -s --basetemp E:/OOTRemake/work/r8-freestanding-cs8e/pytest-seed14-next`:
  **1 passed,1 deselected**. Actual whole-world seed14 generated, won under a fresh Search,
  wrote/read back all14 assigned floor identities, and inverse floor/chest deltas recovered
  every entire affected original Banc. This is data/search proof, not a Hookshot run.
- Actual `python -m clawshot --shuffle Chest Freestanding --print-settings` exits0 with
  a CS1 value; no dump/output is required for that settings surface. Full CLI replay follows.

Shared checkpoints after item1: **afb0ceb** definitions, **2e060a8** owned transforms/tests,
**f194084** seed pipeline, **fc44d13** CLI, **c3d7533** directions/coverage,
**c477fc1** README/world-format contract. The next item2 commit includes the whole-dump
oracle, floor-required-shield regression, section36 and this evidence. All are checkpoints
until the complete four gates below; no commit is posted ready based only on focused checks.

## Authorized integration and CLI replay

Committed item2 as `8debaae`, then performed the reviewer-authorized `git rebase main`
onto **e3745f5** (settings backlog in the roadmap only). All eight commits replayed without
conflicts. Read the updated backlog; it adds no Track E scope or runtime change.
Earlier hashes above are historical; the rebased branch ledger is:

| Commit | Scope |
|---|---|
| `a019d45` | Item1 complete anchor/native-pack/respawn audit |
| `3be0e9d` | Shared definitions only: DMC pair and GV waterfall links |
| `97cfc47` | Owned native floor transforms, eligibility and synthetic regressions |
| `0ab2619` | Shared seed pipeline only |
| `3e86de4` | Shared public CLI choice only |
| `082c748` | Shared14-check player catalog and coverage oracle |
| `4f79c01` | README/world-format contract |
| `8a78867` | Item2 whole-dump oracle, required-floor-shield regression, section36 and output evidence |

Actual public CLI smoke, before the plans-only rebase (same source):
`uv run python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 2 --shuffle Chest
Freestanding --no-cheap-deku-shield --hints mask --out
E:/OOTRemake/work/r8-freestanding-cs8e/cli-seed2-0-next`.
Exit **0**, **178 shuffled checks /24 spheres**, **78 canonical output files**.
A second interpreter with a different `PYTHONHASHSEED` used the written effective CS1,
no shuffle/logic overrides, and fresh `cli-seed2-1-next`: exit0, same counts,
**78/78 files byte-identical**, including every resource, spoiler and play note.
Transcripts `cli-seed2-{0,1}.log` and `cli-replay-proof.json` retain exact command/settings/hashes.
Both new folders remain staged, never launched or swapped over a player output.

Read the actual rendered play-note floor rows and hints, not merely a serializer:
all14 physical pickup names/directions appear; ranch and river-near-Domain hold Deku Shields,
windmill and river-open-grotto hold Red Rupees, and the unchanged GV floor piece retains its
own variant. The different `GV Crate` and Dampé race checks are still chests, not extra floor
checks. This confirms the visible CLI/spoiler/note surface; it does not certify in-game pickup.
The independent whole-dump seed14 oracle covers native actors and all affected written Bancs.

The saved player batch was read back independently: bin EXE, update suppression, missing-EXE
stop, unique user, backup-copy direction and overlay/log paths correct. No batch, dry run,
game, window, source save or active output was run/written. Removed only the session-created
throwaway CLI driver after both successful processes and byte proof; retained the research,
failure reproducers, controlled builder/checker/checklist, outputs and JSON/transcript evidence.

All four full gates completed on rebased source through `8a78867`, with fresh external
`gate-synthetic-next` and `gate-dump-next` basetemps. No repository source/test edits followed
their start; only this documentation-only handoff follows the successful results.

Respawn evidence labels: the other-pickup ledger records **native metadata/AI contracts**,
not newly observed reload behavior. `NoRespawn`, `AlwaysRespawn`, `BancReset`, `SupplyObject`
and reset values come from the resolved pack/GameDataList; their runtime implications are
inferred unless sections11/27 explicitly record Kareem's observation. In particular, no
permanent replacement collection is certified from a flag's existence alone.

## Full gate evidence

Observed completed stages on the final rebased source, without source/test changes:

| Full command | Observed result |
|---|---|
| `uv run ruff format --check` | **209 files already formatted** |
| `uv run ruff check` | **All checks passed** |
| `uv run pytest --basetemp E:/OOTRemake/work/r8-freestanding-cs8e/gate-synthetic-next` | **651 passed,81 skipped**,785.54s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump --basetemp E:/OOTRemake/work/r8-freestanding-cs8e/gate-dump-next` | **80 passed,652 deselected**,895.04s |

732 tests collected. The synthetic suite includes the existing default/progressive/determinism/
age-return sweeps and all32 new native-floor cases. The unfiltered dump gate passed every
selected test, including both Track E whole-dump oracles. The full chain exited successfully.

## Review handoff

Branch **`r8/freestanding`**, rebased onto authorized **e3745f5**. The eight scoped commits
are listed above; the final documentation-only commit records these completed gates. No merge
or push. Track E is ready for code review, **not certified in game**.

Remaining external acceptance:

- **Kareem: run the isolated LLR shield test and `ingame/llr-checklist.md` above; provide
  the overlay log, native shield grant, and Save/Continue/re-entry once-only result.**
  Other palette/location combinations, particularly underwater collection, remain unplayed.
- Track A owns the exact seed7/seed3 fill refusals recorded above, per Claude's direction.
  No retries were added and no access, return, or native-palette restriction was relaxed.

The refused CLI seed3 output folders and isolated test-user folder were also checked absent
after the CLI probes. No game/launcher/window was opened, no source backup was written,
and no existing player output was replaced.
