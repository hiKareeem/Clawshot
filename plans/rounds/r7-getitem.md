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
