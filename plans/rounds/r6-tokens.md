# Round 6, track D: scrubs and Skulltula tokens (cs6d)

Branch `r6/tokens`. Required AGENTS/README/plans 00–04/decisions and all round-5 reports read.
Dump and save backups read-only. No game, launcher, GUI or terminal-control command run.
Research/decoded files and generated overlays stay under `E:/OOTRemake/work/r6-tokens/`.
No dependency change. Section 23 material is below until sections 20–22 are available in number order.

## Item 1: all 21 scrub actors

Evidence: `probe.py`, `scrub_trace.py` in that external directory; build `e0f3ccfa`.
All 21 actors are `Enemy_Scrub_Business`; their `Bool64bitKey` reset type is **280**, not the
permanent pickup type 24. A placement flag alone is not a once-only reward proof.
`TalkEventName` selects a row of `RSDB/EventSetting`, which runs `Enemy_Scrub_Business_Common`.
`ScrubBusiness_ShopItemActorName0..2` are offer selectors. They are not arbitrary grant parameters:
`Variable` dispatches a fixed name list, with unrecognised values falling through to the Magic Jar sale.
Changing just a placement to a major item would therefore give the wrong sale.

### Census ledger (every actor Hash)

| Area / family | Hashes | Native sale / price | Persistence |
|---|---|---|---|
| Well, room 1 | 15945446340598299551 | Green Potion 30, small magic 10, Business Seed 30 | repeat |
| Shadow, room 9 | 8721287453021850502 | same offers | repeat |
| DC, room 7 | 7388739057158296701 | `Item` generated/rotating offers | repeat |
| Jabu, room 18 | 9496373148524757782 | `Item` generated/rotating offers | repeat |
| HF three-scrub group, seeds | 12901354557574090016 | seeds 15/30, small magic 10 | repeat |
| HF three-scrub group, bombs | 16672855544778411393 | bombs 35/60, bombchus 100 | repeat |
| HF three-scrub group, nuts | 17418042722045679657 | nuts 20, bugs 30, Business Seed 30 | repeat |
| LW grotto rear, child | 2214083465643671502 | seeds 15/30, small magic 10 | repeat |
| LW grotto rear, adult | 14619830301496284497 | arrows 20/50, small magic 10 | repeat |
| LW theater left | 2569517939889411425 | forced bugs then generated offers (`Item_SellBug`) | repeat |
| LW theater right variants | 11385057993574159532, 15048088372638595204 | heart 10 / heart bundle 20 / magic 10; red/green potion 30 / heart bundle 20 | repeat; two actors in one prefab |
| HF heart, adult/child | 1888007325063123154, 10364468093017215295 | Piece of Heart 100 | shared saved Bool `HyruleField_Enemy_Scrub_Business_HeartPiece_01` |
| DMC heart, child | 2518138296199711695 | Piece of Heart 100 | `DeathMountain_Enemy_Scrub_Business_HeartPiece_01` |
| KF alternate stick sellers, child/adult | 182031956235860994, 7488448334396031424 | medium/large stick capacity 40 | shared with LW stick sellers below |
| LW bridge stick sellers, child/adult | 5406759280757349546, 11192313919554167152 | medium/large stick capacity 40 | `LostWood_Enemy_Scrub_Business_DekuStickPouch_01` |
| LW grotto front nut sellers, child/adult | 4328741615941752705, 5764461665617243979 | medium/large nut capacity 40 | `Lostwood_Enemy_Scrub_Business_DekuNutsPouch_01` (case intentional) |

12 repeat actors; nine actors implement **four** once-sale families, not nine independent rewards.
The four completion Bools are saved in progress.sav (`SaveFileIndex=0`, `ResetTypeValue=8`, default false).
The capacity/heart prefab logic reads these Bools to retire the seller/prefab. KF/LW stick sellers share one
completion flag and grant branch. Their copies must never contribute separate pool rewards.

### Purchase and patch contract

`SimpleShopSub_Scrub_Business_OneTime`: Event300 sets `SimpleShop_Price`; Event147 asks accept/cancel;
Event288 checks rupees; only success reaches Event4 (`Dm_SY_GetInEvent:GetInEvent_NotTurn_2DShop`,
`ActorName` argument), then Event406/298 sets buy/success; caller sets the family's completion Bool.
Cancel/shortfall never sets it. Native wallet 200 covers all four prices; no new wallet predicate needed.
The generic get wrapper receives the changed actor, so get text/model follows the actor [INFERENCE until played].
Merchant flavour messages are unchanged and may still mention the original reward.

`patch/scrubs.py` edits the **shared flow**, not each Banc actor. Both ages/alternate copies therefore
receive one placement automatically. Contracts are checked before mutation; every branch/tier of the selected
family changes together, all other events, actors, entry points, prices and saved gates remain equal:

| Logical check | Grant events (`ActorName`) | Explicit selection identity |
|---|---|---|
| HF Deku Scrub Grotto | Event645 | Event653 `Shop_SelectItemName` |
| DMC Deku Scrub | Event293 | Event144 `Shop_SelectItemName` |
| LW Deku Scrub Near Bridge (including KF copies) | Event317, Event322, Event555 | no explicit item-selection write in this branch |
| LW Deku Scrub Grotto Front | Event318, Event326 | no explicit item-selection write in this branch |

Banc's original offer selectors remain intact, or the dispatcher would miss the changed grant. Existing
success-only saved flags remain intact; no new flags, stock overrides or repeat-vendor policy invented.
Reviewer approved HF and then the other three one-time families (current conversation, 2026-11-08).
Repeat vendors stay vanilla by reviewer decision. Capacity seed representation is addressed in item 3.

### Player outputs (written, never run)

`E:/OOTRemake/work/r6-tokens/ingame/Test - <name>.bat`, copied from round 5's `Test - talon-boomerang.bat`:
only `E:\Games\Hookshot\hookshot.exe`, distinct `user-<name>` folders, copies the read-only ranch backup on
first use. No source save or game folder writes. Each overlay changes only the common flow, 184536 bytes
before/after, within existing allocation 184816. Built through `clawshot.patch.write`; readback and size oracle
passed. `verification.json` per output records actual sizes. Static launcher checks passed; none executed.

| Name | What to do | Expected observation to check |
|---|---|---|
| scrub-stick-boomerang | Child: from Lost Woods entrance take left toward the bridge seller, stun it, buy for 40. Also inspect the corresponding KF seller when available. | Boomerang, no capacity upgrade; only one reward across alternate sellers/ages |
| scrub-nut-boomerang | Open the Lost Woods two-scrub grotto, stun/buy from the capacity seller (front), 40 | Boomerang on either native tier branch; rear vendor unchanged |
| scrub-dmc-boomerang | Child: summit entrance into crater, drop to left ledge seller, buy for 100 | Boomerang, no Piece of Heart |
| scrub-hf-boomerang | Adult: read the Fairy Note by the Gerudo-side fenced grotto; return as child, solve native password interaction and buy for 100 | Boomerang; adult still cannot buy, puzzle/100-rupee fee unchanged |

Ranch backup has 68 rupees; collect more for the 100-rupee cases. HF needs a later adult/child-return test;
the launcher deliberately does not forge note/quest flags or claim this child backup is adult-ready.
For each: first decline, then retry without enough money if practical, then buy; leave/re-enter, save/quit/continue
and revisit. **Kareem: does cancellation/shortfall leave it available; does successful purchase grant the
Boomerang once, with matching get text/model; do capacity tiers or adult/KF copies ever grant a duplicate?**
Require `fs: OpenFile(...Enemy_Scrub_Business_Common.bfevfl.zs): from the overlay` in that output's log.

### Exercised verification

- `uv run pytest tests/test_scrubs.py -q`: **6 passed** (all grant tiers/selection identities; exact inverse diff;
  stale grant/price/selection/missing event refuses before mutation; repeat vendor refused).
- `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_scrubs_dump.py -q -s --basetemp E:/OOTRemake/work/r6-tokens/pytest-scrub`:
  **1 passed**; four families / nine physical actors linked to the changed flow; all tiers edited; exact inverse
  full-flow equality and original saved-flag metadata verified.
- `uv run python E:/OOTRemake/work/r6-tokens/build_scrubs.py`: **four real overlays built/read back**, each one resource.
- Scoped ruff format/lint passed (three files).

## Coordination

Posted 10:22/10:23/10:24 on `cs-r6` as cs6d: dispatcher limitation, once-only subset, shared stick flag,
CLI integration heads-up, and section ordering. Reviewer approved repeat exclusion and all four once families.

## Diagnosed failures

Initial external probe called `.files` on the SARC reader's dict. Printed `type(s)`/members showed the exact
contract; changed to dict `.items()`/`len(s)` and the aimed rerun passed. No game data was written in repo.
A patch targeting line 49 in a 48-line test was refused atomically; reread exact lines, then corrected the range.

## Item 2: token grant and persistence

Item 1 commit: `daee593`. Token research: external `token_trace.py`, `extract_ai.py`, `decode_ai.py`.
Actor packs contain their own graphs (not loose `romfs/AI` or the global AI pack). Used the existing
external GPL AINB decoder **unmodified** under `work/r4-fast-start/.venv`, never its source or code in repo.
Decoded game data stays outside the repository. No NX2navi source or documentation read.

- All **100 Gold Skulltulas / 114 placement copies** have permanent type-24 Bool64bitKey entries keyed by
  enemy Hash. There is no placed `Obj_Token_Gold` per enemy: the drop is created at death.
- Enemy pack: `DropTable_Token_Gold` -> one `Obj_Token_Gold`, probability 100, count 1.
  Inherited `Drop` blackboard declares `Drop__DropActor` and `Drop__DropTable` as instance parameters.
- Enemy utility graph nodes 0–2: `QueryGenericMakeOverwriteParam` ->
  `QueryBlackboardOverwriteParamAddNoRespawnGmdHash` (key `GoldTokenGmdHash`) ->
  `OneShotDropSetOverWriteParam`. Thus the spawned token receives the enemy's persistent key.
- `Obj_Token_Gold` keeps special token AI, a non-instance `GoldTokenGmdHash` u64 blackboard key,
  and `PouchContentParam.PouchActor = Item_Token_Gold`, fixed max 100. Auto pickup/repeated get presentation
  enabled; its model/boomerang/Hookshot attachment remain native.
- Token AI queries death reason; **reason 10** reaches `OneShotGoldTokenDeadAfter` plus the death-procedure
  signal. Other reasons do not call that callback. The callback's engine implementation is not in the data.
  [INFERENCE] It records collection against the passed enemy Hash; ordinary pickup AI lacks it.

### Expressible experiment, not a safe tokensanity claim

`patch/tokens.py` overrides only `Dynamic.Drop__DropActor` at a saved enemy Hash, across **all** its
child/adult/Alternative copies. Enemy Gyaml, Hash, transform, appearance params, AiGroups and memberships
stay equal. It refuses stale/wrong/missing enemies and non-pickup inventory actors (`Item_Boomerang` etc).
Experiments use only actual pickup actors: token control, red rupee and the two freestanding-tested shields.
Native drop-override execution and the replacement pickup's persistence still need the game result.
Replacing the enemy Gyaml or globally changing every token's pouch identity is **not** implemented.

Three overlays under `E:/OOTRemake/work/r6-tokens/ingame/`, built through `clawshot.patch.write`:

| Name | Ranch tree enemy Hash 341792603838029977 drops | Changed placements / allocation |
|---|---|---|
| token-ranch-control | Obj_Token_Gold (positive control) | Adult +28 bytes / 456872; Child +24 / 395944 |
| token-ranch-rupee | Obj_Rupee_Red | Adult +24 / 456872; Child +24 / 395944 |
| token-ranch-hylian | Obj_Shield_Hylian | Adult +28 / 456872; Child +28 / 395944 |

Each includes the raised resource size table. Same isolated-save launcher pattern as item 1; only the
release executable, no launcher run. Read the six ranch backup saves: the target Hash is **unset in all six**;
the Market crate and Kakariko tree token Hashes are already set in five, so neither is an appropriate backup test.

**Kareem: load slot 01 with each corresponding launcher, record token count, roll into the ranch tree and
kill its Gold Skulltula. Control must drop/collect a token, increase count by one and retire the enemy.
Rupee/shield variants should show the new pickup, grant it without a token-count increase, and retire the
same enemy permanently. First leave the drop uncollected and revisit: does the enemy return so the reward
is not lost? Then collect, leave/re-enter, save/quit/continue, and roll the tree again: no duplicate.
Does the shield hang at the original token height, and can it be collected normally/by Boomerang/Hookshot?**

After each: `uv run python E:/OOTRemake/work/r6-tokens/ingame/check_save.py <name>` prints each slot's
target Hash plus acquired-shield flags (read only). Compare the token count in the UI and the saved Hash.
The log must show `HyruleField_Child_Static.bcett.byml.zs` and the size table `from the overlay`.
Whether uncollected drops survive a reload and whether ordinary drops run the completion callback are
**open prerequisites**, not solved by preserving the enemy Hash in the file.

### House of Skulltula gift checks

Already in `census/gifts.py` through literal wrapper calls; no second reward census or duplicate token
location is needed. `GatheringTokenGold` linked steps: Event398 wallet (10), Event75 Echo Gem/Agony Stone
(20), Event194 large wallet (30), Event200 large Bombchu bundle (40), Event219 Heart Piece (50), Event215
Gold Rupee (100). Existing `gift_rules.toml` classes all six `swap`; 10–50 use saved per-threshold flags,
100 quest completion. Event471 is an **unlinked repeat Gold Rupee**, not an additional once gift check.
`--shuffle Gift` already handles supported rewards; its 40-token check stays vanilla because its logical
Bombchu quantity does not exactly match `Item_BombchuBundle_Large` (round 5 finding), not because tokens
need to own House gifts. Token count queries remain `PouchData.Item_Token_Gold.StockNum`.

### Exercised verification

- `uv run pytest tests/test_tokens.py -q`: **5 passed**; copies change together with identity/logic intact,
  inventory-only actors and stale/missing enemies rejected.
- `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_tokens_dump.py -q -s --basetemp E:/OOTRemake/work/r6-tokens/pytest-token`:
  **1 passed**; exact inverse field diff over all 100 enemies / 114 copies. This is data proof, not persistence.
- `uv run python E:/OOTRemake/work/r6-tokens/build_tokens.py`: three overlays built/read back; seven House
  gift steps printed, six linked plus the repeat; release-only launchers statically checked.
- Scoped ruff format/lint passed (three files).

Posted token callback/persistence prerequisite and capacity integration choice on `cs-r6` at 10:29.

## Item 3: opt-in seed integration

`make_seed` automatically runs `scrubs.seed_setup` for public `Scrub`, then registers its transform through
`extra_steps`. CLI accepts `--shuffle Chest Scrub`, or Scrub with other supported kinds. Default remains
Chest only. The setup copies the spec; normalizes **only the four approved logical checks** to type Scrub;
and explicitly holds all other Scrub/GrottoScrub vendors vanilla. This keeps the public settings value
`Scrub`, rather than leaking the translated `GrottoScrub` type into a settings string. Native existing rules,
including HF's adult-note then child purchase requirement, are unchanged.

Fixed capacity choice (provisional D16 implementation): `Deku Stick Capacity` -> `Item_StickBag_Medium`
(20 sticks), `Deku Nut Capacity` -> `Item_NutBag_Medium` (30 nuts). Verified against PouchActorInfo
`AfterExpansionMaxNum`. The existing logic items are normal-class, not progressive. Every selected family
is patched even if its pool item did not move, so a native Large branch cannot give an unmodelled tier.
The capacity items are restricted to Scrub destinations until chest-grant evidence exists; an existing
stricter per-item restriction is intersected, not relaxed. Gift census/mask upgrade steps remain unchanged.
**Kareem/reviewer: fixed first-tier capacity actors follow D16; confirm this policy rather than assuming a
shuffled capacity is progressive.** Nothing assumes those capacity actors work in chests.

Token is **not a fill destination yet**: the public CLI accepts the name only to give an explicit prerequisite
error; `make_seed` refuses before reading the dump or generating/writing anything. No no-op Token shuffle,
fake persistence flag or seed accepted on an unproved callback. The experimental `tokens.changes` is a
separate explicit file-transform API, used only by the three controlled outputs. Reviewer direction requested
on this safety boundary; the roadmap permits only what passed review. Persistence remains Kareem's test.

### Exercised seed and command behavior

- `uv run pytest tests/test_scrub_seed.py tests/test_scrubs.py -q`: **8 passed**, including unchanged input spec,
  exactly four eligible families, repeat exclusion, fixed item counts and no capacity-in-chest leakage across
  20 synthetic seeds.
- Real whole-world API smoke, seed 7, `Settings(shuffle=("Chest", "Scrub"))`: **168 checks, 28 spheres,
  59 resources; finished search won with default chronological return guarantee**. Read written common flow:
  HF -> Nut Capacity (100); DMC -> Stick Capacity (100); bridge -> Slingshot (40); grotto front -> Rupee (1) (40).
  Every native tier/copy supplies the assigned actor; no shuffled capacity is in a chest.
- Actual `python -m clawshot --romfs E:/Games/Hookshot/romfs --seed 7 --out <external replay> --shuffle Chest Scrub`
  in a second interpreter with `PYTHONHASHSEED=31337`: **exit 0, all 60 canonical files byte-identical** to the
  API output, no path or byte differences.
- Actual same CLI with `--shuffle Token`: **exit 1**, names the callback/persistence prerequisite,
  output directory absent. New synthetic regression verifies API refusal without even a readable dump.
- Added full-world dump regression: seed output assigns every once-sale grant/selection to its placed actor;
  exact inverse flow equality proves native prices, control flow, saved gates and other vendors unchanged.
  Full gate result below will cover it.

### Shared-file-only commits

| Commit | Scope |
|---|---|
| daee593 | item 1 scrub transforms, census trace/report and tests |
| 7f4ee0b | item 2 token experiments, persistence trace/report and tests |
| 9b60b4e | only `data/item_actors.toml`: two fixed Medium capacity mappings |
| de1fe3c | only `patch/__init__.py`: automatic Scrub setup/extra-step hook |
| 5a823fc | only `patch/__init__.py`: explicit Token prerequisite refusal |
| b0f3f33 | only `__main__.py`: CLI choices/help |

Shared contracts/commits posted on `cs-r6`; cs6a received all four names, stable Hash groups and landmarks;
cs6b was asked to include Scrub/Token in the settings codec's public values. No shared dependency file edited.
Section 23 cannot be appended in numeric order until the other tracks' sections 20–22 are on the authorized
base; the research and reproducible findings are complete here meanwhile.

## Player artifact audit and cleanup

Independent audit of all seven saved launchers: executable exactly the release path, seven distinct isolated
users, backup copy direction outward only, no work-build fallback. Parsed and size-checked every emitted
resource against its effective resource table: four one-flow scrub outputs, three two-Banc token outputs.
All passed; no launcher executed. Player checklist: external `ingame/checklist.md`; read-only checker:
`ingame/check_save.py`.

Completed full-seed replay outputs, replay/smoke scripts and the artifact-audit script were removed after
proof. Only paths created in this session were removed; controlled player overlays, research and their builders
remain. Cleanup also named two pytest basetemps that did not exist (those earlier tests used no tmp fixture):
`rm` printed the missing paths; no retry was needed. The preceding four real smoke paths were removed.
The active full-gate basetemps were not touched.

Prepared section 23 at `E:/OOTRemake/work/r6-tokens/section23.md`; numeric-order integration is the only
documentation prerequisite outstanding, posted to the reviewer. No section 20–22 placeholders were invented.
