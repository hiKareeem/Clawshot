# Round 7, Track B: get-item models and gift items in chests (cs7b)

Branch `r7/getitem`. Read AGENTS, README, plans 00–04, decisions, all round-5/6 reports and the
Round-7 shared-file opening before changes. Dump/build `e0f3ccfa` read-only. No game, launcher,
window, terminal-control command, save mutation, dependency change, merge, push or stash.
Research/decoded data stays under `E:/OOTRemake/work/r7-getitem/`.

## Item 1: chest presentation trace

Reproducers: `trace_models.py`, `trace_presentation.py`, `extract_event_ai.py`, `decode_events.py`
in that external folder. Ran the real dump readers and the existing unmodified external `ainb` decoder
(`work/r4-fast-start/.venv`, GPL used only outside the repo; no implementation source read/copied).
Decoded event graphs and flow traces remain external. No NX2navi code/docs read.

| Stage | Exact field/action | Finding |
|---|---|---|
| Item identity | chest `Dynamic.Drop__DropActor` -> `ContentName` | Same identity drives grant/text and guest display; the grant is not the model resource |
| Visible shape | ActorParam `Components.ModelInfoRef` -> ModelInfo `ModelProjectName` + `FmdbName` | All twelve ordinary `Item_Melody_*` songs resolve to `Obj_Rupee`/`Obj_Rupee`; both ocarinas already resolve to their correct native ocarina models |
| Preloaded model | `RSDB/ActorInfo` row `ModelProjectName`, `FmdbName`, model bounds and render heap | Mirrors the component identity; changing only a pack would leave a stale resource descriptor |
| Display binding | ActorParam `Components.EventPerformerRef` -> `EventUniqueAin` | Songs/Boomerang use `PouchContent.event.root`; both ocarinas use `Common.event.root` |
| Small chest | `Dm_SY_TreasureboxSmall` Event10 | Calls guest `EventTriggerModelBindForItemGetDemo`, then Event34 requests `Rotate_GetDemo`; Event91 sets model LOD |
| Big chest | `Dm_SY_Treasurebox` Event66 | Same guest bind action; Event111 requests `Rotate_GetDemo`, Event31 sets LOD |
| Native bind graph | `PouchContent.event.root`, root151 -> simultaneous144 -> bind146 | `OneShotModelBindSetModelBind` receives player performer link; query152 obtains child/adult get-demo offset, query153 adds event offset |
| Ocarina mismatch | `Common.event.root` command list | Has generic `EventModelBind`/`EventTriggerModelBind`, but **not** `EventTriggerModelBindForItemGetDemo`, `EventTriggerPlayerNoHit` or `EventTriggerSetModelVisible` |
| Text/grant | `GetPouchContent` Event11, Event15, Event0 | `EventTriggerSetForGetWindow(ActorName)` and `EventTriggerAddOrRemovePouchContent(ActorName)` stay separate from display binding |

**Observed in game, not rerun:** Kareem's round-5 Storms and round-6 Minuet show a green rupee;
Fairy Ocarina shows no model with correct text and usable inventory. The song model resource explains the
rupee directly. **[INFERENCE]** The absent ocarina get-demo bind command explains its invisible/off-camera
presentation; changing its already-correct `FmdbName` alone cannot fix that mismatch. No runtime success
is claimed from the decoded graph.

### Native song representation

Enumerated every native non-animation `Model/` filename and music/note/score/ocarina/harp actor names.
No standalone musical-note/song mesh found. Named native candidates are the two ocarinas, Sheik's harp,
NPC notebook and Sun-song quest tapestries; the `HrlField_Note_*` actors are world notes, not musical notes.
The song-named resources are cutscene animation files, not standalone song meshes.

**Proposal for Kareem/review:** use the native Fairy Ocarina for the six non-warp songs and native Ocarina
of Time for the six warp songs. This is a clearly documented stand-in, not twelve distinct note assets.
Keep song text/inventory identity and every grant flag unchanged. Keep both ocarinas' own models and
supply their missing native get-demo event performer. Visual placement still needs Kareem's check.

### Diagnostics and coordination

- First trace encountered an omitted external ModelBind default, then an omitted ASInfo parent. Printed
  exact missing member paths; changed the diagnostic to show raw local components and label external
  defaults instead of pretending every component's parents are embedded. Cause-specific trace succeeded.
- Global AI pack paths are flattened (`AI/PouchContent.event.root.ainb`), not `AI/Root/Event/...`.
  Printed real pack members before selecting the flattened resources. Both native graphs decoded.
- Eval initially used Windows cp1252 on decoder UTF-8 JSON; printed UnicodeDecodeError byte/offset,
  then explicitly read UTF-8. No production code was changed for diagnostic failures.
- `xd://lsp status`: only Markdown marksman configured; no Python language server available.
- Two plain `thread post --thread cs-r7 --as cs7b` attempts failed with **no thread cs-r7**;
  the allowed `thread log --thread cs-r7` printed empty despite that. No thread creation/other command
  used. **Claude: create/restore cs-r7 so the required shared-file/handoff posts can be delivered.**
- Section 26 is held here until section 25 exists on an authorized base, preserving numeric append order;
  no placeholder section or other track's prose is inserted.

Item 1 check: live read-only traces above completed, model assets/RSDB/component references and native
bind dispatch inspected. Investigation only: no tests/docs beyond this required research report.

## Item 2: explicit native presentation patch

`patch/getitem.py` exposes `changes(romfs, actors)` for the common overlay writer. All fourteen
identities are explicit: both ocarinas plus the twelve ordinary songs (not Scarecrow).

- Songs: change only the existing ModelInfo's `FmdbName`/`ModelProjectName`; Fairy Ocarina for
  non-warp songs, Ocarina of Time for warp songs. No replacement of the pouch actor.
- Ocarinas: keep their existing native model, OcarinaParam, Accessory, text and pouch data. Replace
  only their ActorParam `EventPerformerRef` with the native PouchContent component, copied byte-for-byte
  from the Boomerang pack. The selected graph includes every Common command plus the missing chest
  presentation commands. No graph is edited and no animation/mesh is created.
- ActorInfo: song model names/bounds match the native donor. Existing render reservations never shrink.
  Instance heap reserves the original budget **plus the whole native donor budget** (ocarina donor for
  song geometry, Boomerang for ocarina's pouch event dispatch). This is deliberately conservative,
  **not a measured minimal heap formula**. Native donors are captured before updating any row.
- Every other pack member/table row, ActorName, item category, SpecialDeal, grant flags and event
  flows stay unchanged. Typed BYML/endian and SARC read-back are checked.
- The common writer's isolated hook includes positive rounded growth of changed ModelInfo/ActorParam
  members, retaining their original parsed overhead and taking maximum across copies. Only the two
  known same-shape string substitutions are accepted; structural growth is refused.
- ActorInfo's own existing allocation is verified as raw **1,934,492**, rounded **1,934,496**,
  entry **1,937,560**, overhead **3,064**. Isolated format support: `dc54dbb`, plus the whole-file oracle.

**Deliberate acceptance boundary:** this is an explicit experiment API, not an automatic seed default.
The spec asks for a patch and a player output, not an unverified forced model change in every seed.
Kareem must confirm the native ocarina binding, usable ocarina after the change, song presentation and
normal Saria/ocarina behavior before a reviewer enables it by default. In particular, the native pouch
graph's no-hit action queries the rigid body; ocarina packs differ from normal chest-item packs. That
runtime behavior is not established by a byte diff. No placeholder, fake grant or allowlist bypass.

Checks:

| Command | Observed result |
|---|---|
| `uv run ruff format src/clawshot/patch/getitem.py tests/test_getitem*.py` | Formatted; scoped lint passed |
| `uv run pytest tests/test_getitem.py -q` | **18 passed** |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_getitem_dump.py -q -s --basetemp E:/OOTRemake/work/r7-getitem/pytest-item2-after-allocation` | **1 passed**; all 14 pack inverse diffs, all 8,363 ActorInfo rows, native assets, nested/outer allocations |
| `uv run python E:/OOTRemake/work/r7-getitem/smoke_models.py` | Public transforms/common writer actually wrote **16 resources**; independent output read printed all 14 native model identities and PouchContent performer refs |

Original/output ActorInfo size is identical; ocarina packs grow **8,376 -> 8,632** and
**8,216 -> 8,472**, with outer entries raised **8,696 -> 8,952** and **8,536 -> 8,792**.
Songs grow eight serialized pack bytes each; the writer raises only entries that need it.

Failures were diagnosed, not retried unchanged:
- Synthetic nested-size test initially had **zero** rounded growth (104 -> 112 both round to 128).
  Printed the size-boundary values; gave only that synthetic fixture a padding field to put the original
  on the 128-byte boundary. The corrected behavioral allocation test passes.
- First dump test printed `RstbError` for ActorInfo's unsupported formula. Printed its actual original
  raw/rounded/allocation/row count, added the measured own-file formula, then the aimed rerun passed.
- Coordination database metadata confirms **no cs-r7 thread exists**; no message data edited/read through
  SQL, no thread created. Shared writer/formats changes are isolated commits for review; post remains blocked.

## Item 3: exact gift-actor gaps and one player output

Read-only `inventory_gifts.py` scanned all **148 gift steps / 82 distinct actors**, joined linked
checks/rules and current seed eligibility, and compared exact actors with native chest contents and
sourced observations. Full identifier/check inventory stays in external `unverified-gifts.json`.
The raw difference is 77; `Obj_Shield_Deku` has the explicit successful round-5 chest result and is
therefore not listed as unobserved below. This leaves **76 exact-actor evidence gaps**. Raw pickup
rupee spellings are not silently equated to tested `TBox_Rupee_*` display/grant paths.

Only the existing Minuet observation was added to the shared allowlist: `0cd8feb` (settings-only).
Storms and Fairy Ocarina were already recorded. The other ten ordinary songs keep the reviewer-approved
family inference in opt-in anywhere mode; **no newly prepared gift experiment releases any actor**.
The unlinked/repeat/upgrade/class-three entries below are an inventory, not requests to shuffle them.

### Current shuffle, non-song (25)

- `Item_AgonyStone`, `Item_Arrow_Light`, `Item_Bottle`, `Item_Bottle_Milk`.
- `Item_BrokenSword`, `Item_ClaimCheck`, `Item_CojiroCucco`, `Item_DinFire`.
- `Item_FairyBless_DefenseDouble`, `Item_FaroreWind`, `Item_NayruLove`, `Item_Ocarina_Time`.
- `Item_OddPowder`, `Item_PoacherSaw`, `Item_PocketEgg`, `Item_Prescription`.
- `Item_Scale_Gold`, `Item_Scale_Silver`, `Item_Sword_Biggoron`, `Item_Token_Gerudo`.
- `Item_Wallet_Large`, `Item_Wallet_Medium`, `Item_WeirdEgg`, `Item_ZeldaLetter`.
- `Obj_Rupee_Gold`.

### Song family inferred, not individually observed (10)

- `Item_Melody_EponaSong`, `Item_Melody_FireBolero`, `Item_Melody_LightPrelude`, `Item_Melody_SariaSong`.
- `Item_Melody_ShadowNocturne`, `Item_Melody_SpiritRequiem`, `Item_Melody_SunSong`, `Item_Melody_TimeSong`.
- `Item_Melody_WaterSerenade`, `Item_Melody_ZeldaLullaby`.

### Held/unlinked/class-three or mismatched-tier actors (41)

- `Item_AlarmCucco`, `Item_BombBag_Large`, `Item_BombBag_Medium`, `Item_BombchuBundle_Large`.
- `Item_BombchuBundle_Medium`, `Item_BulletBag_Large`, `Item_BulletBag_Medium`, `Item_EyeDrop`.
- `Item_EyeballFrog`, `Item_FairyBless_MP`, `Item_FairyBless_MPDouble`, `Item_Gauntlet_Goron`.
- `Item_MagicBean`, `Item_Mask_Truth`, `Item_Medal_Fire`, `Item_Medal_Forest`.
- `Item_Medal_Light`, `Item_Medal_Shadow`, `Item_Medal_Spirit`, `Item_Medal_Water`.
- `Item_Melody_ScarecrowSong`, `Item_NutBag_Large`, `Item_NutBag_Medium`, `Item_OddMushroom`.
- `Item_PocketCucco`, `Item_Quiver_Large`, `Item_Quiver_Medium`, `Item_StickBag_Large`.
- `Item_StickBag_Medium`, `Item_Stone_Fire`, `Item_Stone_Forest`, `Item_Stone_Water`.
- `Obj_Armor_Goron`, `Obj_Armor_Zora`, `Obj_Rupee_Blue`, `Obj_Rupee_Purple`.
- `Obj_Rupee_Red`, `Pouch_Amiibo`, `Shop_BombchuBundle_01`, `Shop_Sword_Giant`.
- `Weapon_Sword_Master`.

### Controlled output

One launcher: `E:/OOTRemake/work/r7-getitem/ingame/Test - chest-gift-models.bat`.
Overlay: adjacent `chest-gift-models/romfs`; empty new-game user `user-chest-gift-models`.
Checklist: `ingame/checklist.md`; read-only post-play report `ingame/check_save.py`.
Built by `build_chest_gifts.py` through the real `ChestChange`/`Plan`/common writer and `getitem.changes`.
This is an explicit controlled experiment, **not a search-certified playable seed**.

| Place / Hash | Item and expected evidence |
|---|---|
| Mido middle-left / `12786193094758345086` | Fairy Ocarina first: brown native model, correct text and usable ocarina |
| Mido far-left / `4555665598794293658` | Storms: brown-ocarina stand-in rather than green rupee; correct song text; play outside and get rain |
| Mido middle-right / `10831981390482426294` | Din's Fire: native model/text, usable spell and magic gauge |
| Mido far-right / `9725242744547055868` | Adult Wallet: native model/text and 500 capacity |
| Training-area ledge / `16757992849254467386` | Ocarina of Time: blue native model/text, usable upgraded ocarina; Storms retained; **no sword/equip/cutscene** |
| Storms grotto / `14818888396401495482` | Echo Gem: native model/text, equipment/Skulltula signal, retained after Continue; conditional native puzzle check |

Five are reachable without progression items. The sixth uses the ocarina/Storms from the first two;
its native scrub order/chest appearance remains a research question, not a made-up gate. The checklist
explains the vanilla 40-rupee shop Deku Shield if required (no price patch). The sword chest no longer
supplies a sword, so the experiment cannot rely on kept Mido/free merchant access. The upper bridge
ledge's seventh chest stays untouched because its route is unresolved; no chest was moved/duplicated
and no new saved flag or world requirement was created merely to pack more tests into this output.

**Kareem: run that one new-game launcher; report each model AND actual item use/menu/capacity, then
Save/Continue persistence. Does the patched Fairy/Time Ocarina still play normally, including after
Time replaces Fairy? Does Storms retain its song identity despite its stand-in model? Does the grotto
chest appear with the native puzzle, or is an additional prerequisite needed?** The exact overlay-open
paths and crash-stop instruction are in the short external checklist. No game run by the agent.

Observed build: **six saved Hashes, four Banc files, three actor packs, ActorInfo and size table = nine
resources**. Independent inverse tree comparison over every placement file allows only six drop values
and removal of the unsafe sword event. All other actors/groups/transforms/flags are identical.
All output resources parse/fit the effective table; SHA256 of every input resource was unchanged after
building. No generated data or launcher is committed in the repository. Static read-back of the saved
launcher confirms only the bin executable, update-check suppression, missing-exe stop, isolated user,
correct overlay/log and no backup or main-user access. No batch/dry-run execution.

Small diagnosed edit failure: the save-checker footer patch named a nonexistent line; the tool refused
atomically. Re-read the exact footer, removed the unverified wallet-data lookup and kept wallet capacity
as a UI observation. No source save was opened or fabricated to validate a guessed key.
