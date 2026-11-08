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
