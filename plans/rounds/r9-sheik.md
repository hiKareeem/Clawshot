# Round 9, Track B: Sheik and free time travel (cs9b)

Branch `r9/sheik`. Read AGENTS/README, plans00–04, decisions, all round7/8 reports and
`r5-age.md`; Round9's shared-file rules apply. Dump and save backups read-only. No game,
launcher, GUI, Hookshot build, terminal-control command, merge, push or stash. External
research/output: `E:/OOTRemake/work/r9-sheik-cs9b/`. No dependency changes.

## Item 1: placement, Prelude trigger and saved evidence

Executed `uv run python E:/OOTRemake/work/r9-sheik-cs9b/probe.py` against builde0f3ccfa;
complete native flow/placement/GameData/save evidence is in external `probe.log` and flow
reports. Read existing decoded native modules in `work/r4-fast-start/ainb_json/Logic`;
no GPL implementation or NX2navi code/docs read/copied. Python LSP reports no server.

- Temple Sheik is actor **2669233513522124871**, at (139.0265,106.3536,-34), adult Market
  Static. Group **6012439728933042438**, module `Market_Adult_Prefab_7f43`, binds
  `Npc_Hylia_Sheik_Adult_4b5b`. `ActorLogicNpc.Logic_Delete` reads saved Bool
  **Market_Adult_GetLightPrelude**, not a medal, Minuet, Prelude inventory or Forest completion.
  There is no placement Presence gate. Its other module query, `AllSage_IsAfter_Ready_Exp`,
  is not connected to that deletion input. Sheik stays until the Prelude **scene/check** finishes.
- The separate group **17364055337479607892**, `Market_Adult_Prefab_edc2`, ANDs player
  contact with **SageOfForest_IsCompleted_Exp**. The area actor **3406708549665898725**
  is present while `Market_Adult_GetLightPrelude` is false. Request actor
  **3409851866200498477** names `Market_Adult_Field_GetLightPrelude`.
- EventSetting resolves that request to `AllSage:Market_Adult_Field_GetLightPrelude`.
  Event169/170 -> Event73 -> Event39 -> Event37 transitions to `Dm_MelodyGet_Shine`.
  The latter's Event53 gives `Item_Melody_LightPrelude`; Event46 sets
  `Market_Adult_GetLightPrelude=true`. AllSage Event34 then rolls its quest to Step01_01.
- **The scene/travel unlock reads the Forest sage quest, NOT Forest Medallion ownership.**
  GameData BoolExp1371974465 compares `Step_SageOfForest`2841849034 with Complete1275749364.
  The native Forest warp chain Event199 completes the quest separately from the reward grant.
  Speedrunners' medal observation is consistent with vanilla's simultaneous reward/completion,
  not evidence of an item query. Future shuffled medals must not silently inherit an item gate.

Read all twelve supplied `progress.sav` files, not live saves:

| Backup / slots | Era | Forest quest | Forest medal | Prelude scene / completion Bool |
|---|---|---|---|---|
| adult-first /01,04 | adult | Step01 | absent | false /false |
| adult-first /00,02,03,05 | child | Ready | absent | false /false |
| after-forest /01,02 | adult | Step06_2 | absent | false /false |
| after-forest /03 | adult | Step09 | absent | false /false |
| after-forest /04,05 | adult | Complete | owned(1) | false /false |
| after-forest /00 | adult | Complete | owned(1) | true /true |

The last pair isolates the missing scene: medal already owned in04/05, but Sheik's deletion
Bool is still false. Slot00 has both the scene and Bool true. This corroborates Kareem's
reported room-entry transition, not a game run by this agent.

### Item 2 design / provisional implementation choice

Keep the existing ungated pedestal binding. Add a non-negated, non-lazy Presence gate on
**only the placed Temple Sheik** using the SAME Forest-completion BoolExp as his scene.
Before completion he is absent; afterwards he can participate normally, then his existing
Prelude-completion deletion still removes him. Preserve actor Hash/links/transforms, his
module, area/request/flow, song grant and every quest/save value. Native adult Market already
uses that Presence shape with the Fire-completion BoolExp (two distant cloud actors).
This avoids moving a schedule-driven NPC or globally deleting the actor used by cutscenes.
Default remains off; no early Prelude, fake medal, quest completion or saved flag is added.

**Kareem: verify pre-Forest return and second pull, then normal Forest reward/Prelude and
no repeat after Save/Continue on the isolated copies described below.** Runtime actor/scene
compatibility remains unverified until that game check.

### Diagnostics

First probe passed a third argument to two-argument `read_flow`; printed TypeError/signature,
removed it. Next printed timeline-only0050 (`holds no flowchart`); inspect it as a timeline.
The request name is not a flow-map key; printed EventSetting row resolves AllSage.evfc,
then normalized that explicit Work path to its filename stem. Each cause was printed before
its targeted correction; final probe exit0. No game bytes written or unchanged failed retry.
