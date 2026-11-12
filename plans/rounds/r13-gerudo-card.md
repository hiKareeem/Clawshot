# Round 13: moved Gerudo card investigation (cs13d, issue #19)

Branch `r13/gerudo-card`, baseline `fa6f4efd449ea3f801fb82103cee20aea8f8aedb`
(0.2.0 plus dungeon-item repair, unpublished). Investigation only: no version,
logic, gift rule, generator or patch changes. Proposed decisions below are cs13d's,
not accepted product decisions. No merge, push, game start, hc/herdr command or
write beneath `E:/Games/Hookshot`.

## Scope and evidence

Keanu's Discord report, 2026-11-12 16:51, is accepted played evidence: a moved
Gerudo Pass did not stop detection; without Hookshot he was expelled, with
Hookshot he was jailed. It concerns an unidentified 0.1.x seed on Hookshot 2.1.0;
no exact recipe or before/after saves were supplied. This investigation reads
supported dump `e0f3ccfa`, not a string scan or an attempted replay of his result.

External research: `E:/OOTRemake/work/rounds/r13/gerudo-card-cs13d/`.
`inspect_game.py` decodes actual Logic AINBs and EVFL events/edges;
`inspect_resources.py` reads actor/global packs; `schedules.py` reads loose and
packed AI schedules; `flag_readers.py` checks all native event flows for the
relevant prison/card flags. Decoded resources stay outside the repository.
Our BYML/EVFL/zstd/SARC readers are used. The external, unmodified GPL `ainb`
library is research-only: 0.2.16 failed on a duplicate-string warning in complex
AI expressions; isolated 0.2.17 fixes that parser defect and decoded those graphs.
No library code was copied into Clawshot.

**Existing plan discrepancy:** `03-game-data.md` section 19 (including the card
row and its "guards send Link to the cell without it" claim) mistakes a stealth
area sensor for the security-mode predicate. Actual data below contradict that
claim. No implementation was attempted while this disagreement is unresolved.

The underlying saved state is Enum `Step_SageOfSpirit` (hash421043869,
`SaveFileIndex=0`, Reset8), not a standalone saved "friendly guards" Bool.
The BoolExp's operands identify that enum and the `Step01` enum value
(hash3949112793). Direct AINB comparison outputs independently establish
the strict "after Step01" relation; the expression comparison opcode's meaning
is **[INFERENCE]** from the native enum/flow contracts, not executable-code tracing.

## 1. What makes adult guards hostile

The missing condition is **Spirit quest progress past Step01**, not the card's
inventory flag and not a direct AND of four carpenter Bools in each guard.
`SageOfSpirit_IsAfter_Step01_Exp` is the corresponding native BoolExp. The native
captain sequence advances that quest to `Step02` after giving its reward.

| Resource under `Logic/` (suffix `.logic.module.ainb`) | Structural condition |
|---|---|
| `GerudoFortress_Level_Exterior_01_a401` | Node4 compares `SageOfSpirit` to `Step01`; node5 ORs `IsBefore` and `IsEqual`. Its true output feeds `EnableSecurityGuard` for nodes0/1/2/6/7/8/9/11: the placed outdoor 012/004/009/020/010/012/003_Adult/011 guards. |
| `GerudoFortress_Common_178b`, `..._1d80` | 007 and 006 gate guards: node1 `IsAfter Step01` is inverted by node2's OR-False output, then drives security through node3. |
| `GerudoFortress_Level_Room_02_5d06` | Hideout 013/014/015: node3 `IsAfter Step01`, node4 False output enables security. |
| `GerudoFortress_Level_Room_05_ee1c` | Hideout 016: node2 `IsAfter Step01` inverted through nodes3/4. The named `...HideOutGuard_SightON_05` reader is unused, not another live condition. |
| `GerudoFortress_Level_Room_06_ade9` | Let P = quest past Step01, I = `GerudoFortress_IsInPrison`, D = restricted door open. Node4 False output enables 018 iff `not (P or I)`. Node29 enables 017 iff `not (P or I) or (I and D)`. Thus 017 can remain a prison sentinel after clearance, not an ordinary hostile patrol. Its `...SightON_06` reader is unused. |
| `MiniGame_HorsebackArchery_8380` | Nodes1/2 enable 008's security at/before Step01. Nodes3/4 create its proximity area only after Step01. |

Some outdoor duplicates (a401 nodes3/10/12) have security hard-disabled and are
deleted while the hostile phase is active; captain variants likewise have
security disabled. Do not count every actor with SecurityGuard in its type as an
always-hostile guard.

The remaining detection is normal security AI, not a card query:
`NpcSecurityGuard.brain.prioritySecurity.module` checks security mode, schedule
flags, target and LOS, and drives `IsObserve`/`IsFoundPlayer`;
`NpcSecurityGuard.action.CheckLineOfSight.module` does angle/distance and physics
ray casts. Their definitions are in the actor packs and
`Pack/AI.Global.Product.111.pack.zs`. Light/dark/horse context changes the native
thresholds. Incapacitating/avoiding a guard can still avoid detection; ownership
of the moved card does not disable this machinery. The placed actors' dynamic
`PlayerDiscoveredEventName` selects `GerudoFortress_GotoPrison` or its pair/004
variants; `RSDB/EventSetting` resolves these to `SageOfSpirit` entries. Paired
014/015 and 017/018 paths ultimately share that capture flow.

### What the card read really does

`GerudoFortress_Common_35d7` node2 reads `GerudoFortress_GoToPrison` to create two
area sensors (nodes0/5). Node1 reads `IsGet.Item_Token_Gerudo` to **delete those
sensors**, not disable guards. Nodes3/4 observe the player; node6 ANDs inside the
outer area and outside the inner area; nodes7/8 write `IsInSneakArea` false/true.
This is a separate stealth-area contract. A card acquired remotely can remove
that area while leaving actual patrol hostility and entry talk restrictions.

The CarpenterSet `IgnoreCarpenter`/`ThreatCarpenter` graphs operate carpenter
reactions, not general guard friendship. The four shutter graphs set
`GerudoFortress_IsAfterHelpCarpenter_Npc_Hylia_013_Adult` through `_016_Adult` when
the corresponding shutter opens (`01_fe0d`, `02_a38e`, `03_da02`, `04_cd7f`).
Those source-state flags must not be confused with owning the card.

## 2. Native captain hand-over versus moved card

### Native source sequence

`SageOfSpirit_RescueCarpenter` increments
`GerudoFortress_Meet_FourCarpenter_NumOfCarpenterHelped` at Event184 (index335),
and decrements its `_02` counter at Event191 (index337). Its post-rescue branch
Event154 (index331) transitions to `Meet_FourCarpenter_ClearEvent` at Event145
(index328) when the helped count is greater than 3. This is upstream rescue
state, **not an effect of picking up Item_Token_Gerudo**.

`RSDB/EventSetting` maps `Meet_FourCarpenter_ClearEvent` to the same-named entry
in `SageOfSpirit.bfevfl.zs`. Its complete relevant continuation is:

1. Participate/init the player and captain (`InitTalk:Sub_InitFlag_Npc`).
2. `SageOfSpirit/Event145` (index35) transitions to `Dm_Gerudo_0025`.
3. `Dm_Gerudo_0025/Event294` (index120), reached through C05, calls
   `Dm_SY_GetInEvent:GetInEvent_NotLookatObjectTurnOff` with
   `ActorName=Item_Token_Gerudo`; the common item grant supplies inventory/IsGet
   and its pickup presentation. The 0025 flow itself has **no direct GameData or
   Challenge write**; its four WarpPoint reads choose staging for the last
   rescued carpenter.
4. Return to the enclosing flow: fade out, move captain to schedule anchor2,
   wait 60 frames, then Event192 (index210) sets
   `GerudoFortress_Npc_Gerudo_001_IsInFirstPlace=false`.
5. Event146 (index22) calls `EventExecuteProgressChallengeStep` for
   `SageOfSpirit/Step02` (`IsIgnoreCompletedChallenge=true`, UI not ignored).
6. Event292 (index217) warps 017 to schedule anchor6; Event87 (index142) requests
   the quest progress UI; the remaining camera restoration ends the event.

Native event-history bookkeeping has `HavePlayedEvent.Dm_Gerudo_0025` and
`HavePlayedEvent.Meet_FourCarpenter_ClearEvent` entries. Their existence and the
registered event transitions are data facts; exact engine timing of setting
history is **[INFERENCE]**, not measured in Keanu's save. Subflow calls are not
proof that every wrapper's own HavePlayedEvent changes.

`RSDB/Challenge` makes Step01 own the four carpenter rescue schedules (plus the
captain's Step01 schedule); Step02 replaces these with two captain meeting
schedules. This is a quest-state transition with consequences beyond guards.
The hand-over does not explicitly grant Hookshot, set all carpenter flags, open
the desert gate, or charge/open Training Ground. Those are separate sources.

### Moved card

**Current public generation does not put the card in a chest.**
`data/settings.toml:34-51` does not admit `Item_Token_Gerudo` to `chest_verified`,
and no vanilla chest supplies it. `patch/gifts.py:1099-1114` therefore holds it
to gift types (`Boss`, `Cutscene`, `NPC` under Recommended); defaults leave it
vanilla. The same restriction exists in the externally retained 0.1.1/0.1.2/
0.2.0 source snapshots. The reported moved-card gift is consistent with this.
R8's diagnostic card chest showed presentation but never established the
friendly-guard contract or added production chest admission. A manually forced
chest would be a diagnostic outside current public placement rules, not another
supported route to claim tested.

The current gift patch changes the destination's item parameter
(`gifts.py:400-413`). If it appends a once Bool, that Bool belongs to the source
check (`416-429`), not the card. The card can reach 54 native grant steps across
47 checks in 32 flows, using 21 wrapper entries plus 2 direct pouch-add steps
(external `scratch/grants/destinations.json` and `wrapper-summary.json`).
Wrappers reach `GetPouchContent:GetPouchContent/Event0`; the 2 direct steps use
the same `PouchSystemActor.EventTriggerAddOrRemovePouchContent` action locally.
No wrapper writes or branches on card-specific story state.

The card's PouchActorInfo is KeyItem/Large, autosave-on-get, with no special
deal, equipment or bundle alias. The common native grant records
`IsGet.Item_Token_Gerudo` (saved Bool 241329351), recognizes its inventory
identity, and takes the autosave branch (`GetPouchContent/Event67`). The saved
`PouchData.Item_Token_Gerudo.StockNum` Int 4273263979 is the associated stock
field; its update is **[INFERENCE: native]**, not a card-specific flow write.

Unlike the native captain source, a remote gift does not enter
`Meet_FourCarpenter_ClearEvent`, set Step02, move the captain, or record that
event's history. The destination's own once flag and story continuation stay
source-bound. The original card check's `class="swap"`
(`gift_rules.toml:115-117`) changes only Event294's item; completing it still
advances Step02 even if its shuffled reward is not the card.

Thus inventory recognition/"Gerudo Pass" presentation is insufficient evidence
for friendship. The missing story-progress write explains the reported guards
remaining hostile; the matching exact Hookshot query explains the reported
change from expulsion to imprisonment.

## 3. Wasteland, Training Ground, horseback archery

| Access | Actual data contract |
|---|---|
| Haunted Wasteland gate guard 006 | `Component/AIScheduleParam/Npc_Gerudo_006...bgyml` has a reversed `SageOfSpirit_IsAfter_Step01_Exp` conditional with **empty EventEntry**: no normal gate talk before clearance. Default talk resolves to `Npc_Gerudo_006:Talk`; first gate conversation runs `Dm_Gerudo_0030`, sets `Gerudo_phantomdesert_gate=true`, records `HaveTalked_Special.Npc_Gerudo_006_Talk_Event8`, and calls progress to Step02. `GerudoFortress_Common_305a` ANDs the gate Bool with adulthood to open the shutter/remove the air wall. Later conversation distinguishes `SageOfSpirit_IsAfter_Step03_Exp`. No card query. |
| Gerudo Training Ground guard 004 | `Npc_Gerudo_004...AIScheduleParam` suppresses normal talk while not past Step01. Previously-started Ice Arrow quest and finished-talk variants precede that conditional. `Open_TrainingGround` Event88 checks 30 rupees, Event123 deducts 30, Event109 sets `GerudoTrainingGround_Gate`, Event0 sets `GerudoFortress_TrainingGroundGateOpend`, Event111 progresses `SubEvent_GetIceArrow/Step00`. No card query. `PayTalk`, called by `ItemCheck_ForTrainingGround`, optionally checks Bow, Hammer, Iron Boots, Longshot-or-Hookshot and Silver Gauntlets under the Mask of Truth branch; these choose equipment-advice lines and converge on the same rupee display/payment choice, not a mandatory equipment gate. |
| Horseback archery 008 | `MiniGame_HorsebackArchery_8380` gates both security and the proximity sensor on Spirit progress. The ready schedule suppresses pre-clear talk; its earlier near-player conditional cannot normally bypass this because the proximity sensor exists only after clearance. Day actions start 05:20, switch at 18:00. `Minigame_HorsebackArchery` then tests Epona quest completion, horse proximity/riding, Bow ownership/rental branch and 30 rupees; this remake has rental paths, not simply the N64 "own Epona+Bow" conjunction. No card query. |

These are static data findings, not played entry tests. In particular, no claim
is made that arbitrary stale/debug-set flags could not activate an earlier
schedule override.

Exact HBA predicates: `Get_Epona_IsCompleted_Exp` at Event175/Event168,
`EventQueryIsHorseEponaNear{Distance=30}` at Event143 (and 5 at retry Event15),
`EventQueryPlayerCheckRideHorse`, `IsExistInPouch(Weapon_Range_Bow)` at Event247,
and `EventQueryHasRuppe{Value=30}` at Event75. The rental/first-talk branches
also read `MiniGame_HorseBackArcher_HaveTalkedAboutBow`,
`...HaveTalkedAboutRentalHorse`, `...HaveTalkedAboutHorse`, and
`GerudoFortress_PlayedYabusame`. None substitutes a card read for quest clearance.

## 4. Jail versus expulsion; softlock boundary

Before clearance, `SageOfSpirit/Event123` (index174) selects the not-past-Step01
branch, then **Event230 (index71) reads exactly `IsGet.Item_Hookshot`**. It does
not OR `IsGet.Item_Longshot`, count progressive tiers, or test the card.

- True: first/repeat dialogue flags choose presentation; Event274 records the
  first alert, Event202 sets saved `GerudoFortress_GoToPrison=true`, closes
  `Obj_Gerudo_SwitchShutter_A_08`, warps to `GotoPrison_FromFortressGuard`, lifts
  active NPC security, handles the horse, and transitions to `Dm_Gerudo_0010`.
- False: Navi's escape conversation, Event294 first-alert bookkeeping,
  Event235 sets `GerudoFortress_RunFromFortress=true`, then Event338 changes
  Banc to `GerudoValley_Adult/GerudoValley_FromGerudoFortress`.
  `Dm_SY_BancChangeArrive/Event414` clears RunFromFortress after the arrival.
- Losing to a carpenter-room Gerudo thief also checks the **same exact**
  Hookshot Bool (`SageOfSpirit_RescueCarpenter/Event339`, index264), rather than
  automatically imprisoning a player without it.
- After clearance, the capture flow has a separate reprimand/imprisonment
  branch and writes `GerudoFortress_GoToPrison_AfterClear`. Friendly hideout
  NPC015/018 explicitly invoke prison for standing on their table. These
  punishments are not a failed membership-card grant.

`Item_Longshot` has its own saved `IsGet.Item_Longshot` Bool (hash950969275),
distinct from `IsGet.Item_Hookshot` (hash4288212312). Its PouchActorInfo row has
no bundle/lower-tier grant, and its actor pack names Hookshot only in shared
model/animation resources, not its pouch/assignable-item parameters.
**[INFERENCE]** The data contain no automatic lower-tier IsGet alias; native
code side effects cannot be excluded from data alone. Keanu's Longshot-only
expulsion is the played observation supporting the exact-flag distinction.

`GerudoFortress_Common_be48` observes the prison volume and writes
`GerudoFortress_IsInPrison` true inside/false outside. GameDataList marks it
unsaved (`SaveFileIndex=-1`); GoToPrison and AfterClear are saved Bools.
`Room_06_ade9` drives restricted-door access explicitly:
inside opening is allowed by `P or not GoToPrison or 017 knocked down`;
outside opening also allows `not IsInPrison`.
Thus **past Step01 the cell door can be opened without Hookshot**, even if the
player is jailed for a table reprimand.

**[INFERENCE]** No unavoidable card-specific jail softlock is established by
these data: the pre-clear capture paths require the actual Hookshot-acquisition
flag, and the post-clear cell has the quest-progress door escape. The Hookshot
escape through the prison opening and behavior after Save/Continue still need
an in-game movement check to certify geometry/runtime state. Longshot-only
expulsion is a separate fixed-tier predicate mismatch, not evidence that the
Longshot itself is unusable. Do not claim "all jail states proven safe" from a
static graph; modified/stale/debug flags are outside this proof.

## 5. Proposed fixes (not implemented)

**Claude/Kareem: choose A, B or C before any gameplay or logic implementation.**

- **A — source-bound moved-card side effects. High cost/risk.** Use the actual
  destination actor Hash or gift source identity, not a global actor-name hook,
  and only opening contracts already played (the 0.2.0 named-key and r13
  dungeon-item machinery show how to bind/dispatch). But copying Step02 is
  not like crediting a named dungeon key: it removes Step01's rescue schedules
  and can bypass the original captain reward when another progression item
  sits there. Must preserve that source check, rescue progression, later quest
  stages, once-only state and existing saves; must never regress a later Spirit
  stage. A guard-only/card predicate patch avoids forging rescue completion but
  also needs the gate/GTG/archery schedules and prison handling, so is a different
  broad gameplay change, not a cheap extra flag. Needs actual early-card,
  original-source, reload and later-Spirit played acceptance for every admitted
  chest/gift contract. Not safe to assume ready for the next public release.

  Concrete feasibility cost: of the 32 current destination flows, 19 already
  have the unscoped ChallengeSystemActor/progress action, 1 has the actor but
  needs the action added, and 12 have no challenge actor. The current gift-Bool
  helper cannot write quest progress; the named-key compiler is chest-only
  and rejects added actors. A shared helper would need analyzed-event preload
  closure updates as well **[INFERENCE]**. No patched gift/chest challenge-step
  write has played acceptance; a global GetPouchContent actor-name hook would
  also violate the requested source-bound scope.
- **B — keep the card at its vanilla check. Lowest cost/risk; recommended for
  the next public release.** Hold `Hideout Gerudo Membership Card` vanilla,
  removing its item from the shuffle pool and retaining the full native captain
  sequence. This fits existing `keep_vanilla` policy, needs no new runtime
  state/flow contract, and makes card ownership and native clearance coincide.
  Verify pool/placement conservation and regenerate release recipes. It changes
  outputs; Claude chooses the release/version policy. It does not repair old
  generated seeds or retroactively grant quest progress to existing saves.
  This is the safest **card-specific** next-release choice, not a claim that
  every other route is verified; the separate Longshot arrest-route assumption
  below still deserves its own logic review.
- **C — model source completion instead of card ownership. Medium cost.** Add
  a completion event tied to actually finishing the carpenter/captain source,
  use it for friendly fortress/entry gates, and stop treating a remotely held
  card as `can_finish_GerudoFortress`. Keep stealth/rescue routes distinct from
  friendly access and keep the original shuffled captain reward reachable.
  Re-audit fixed Hookshot versus Longshot jail assumptions separately; do not
  silently add native item/quest writes. Requires all affected helper/exit/check
  consumers to migrate plus the full fill/beatability/return-kit seed gates.
  This preserves shuffle without changing the game, but the model still needs
  played stealth/rescue route evidence. Safer than A's quest forgery, less
  conservative than B for an immediate release.

## 6. World-rule audit

Pinned OoT Randomizer source: MIT commit
`526b4c8d81b7c4023ef4573ffbaf39344e270d5b`, `data/World/Overworld.json`
and `data/LogicHelpers.json`, as recorded in the generated TOML headers.
There are **33 direct card-reading rules**, all in
`src/clawshot/data/world/gerudo_fortress.toml`; none is corrected by a remake
override or a helper. The ledger lists every term, including currently
unshuffled pots/crates/wonderitems. Their card-as-friendly-pass branch is wrong;
this does not prove every physical route impossible when a guard can be
avoided or incapacitated. Other item/stealth alternatives remain separate.

All line numbers below are in `gerudo_fortress.toml` on the baseline:

| Lines | Rule/check/exit | Defect when card and native source are separated |
|---|---|---|
| 13 | `GF Gate Open` event | Adult + held card invents gate permission before Step02; conversely a completed captain source with its reward shuffled away is friendly without the held card. |
| 16,17 | `GF HBA 1000 Points`, `GF HBA 1500 Points` | Card substitutes for the native story-gated talk schedule. Existing Bow/Epona/day restrictions are independent. |
| 19 | `GF Sign Wonderitem Near HBA` | Card is not a friendly-patrol pass. |
| 26–38 | `GF HBA Crate 1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, `13` | Each adult card branch assumes friendly archery access. Child/crate-breaking alternatives are not changed by this finding. |
| 39 | `GF GS Archery Range` | Same friendly-access assumption; token is vanilla but may contribute to shuffled Skulltula rewards. |
| 49 | `Gerudo Fortress` → `GF Kitchen Roof Access` | Card + Longshot does not disable patrols; this propagates to roof chest/GS and the three-torch carpenter route. Actual stealth traversal alternatives need their own evidence. |
| 53 | `Gerudo Fortress` → `Gerudo Training Ground Lobby` | Native guard's normal entry talk is gated by quest progress, not the card. |
| 286 | `Hideout Near Kitchen Crate 1` | Invalid card alternative alongside Bow/Hookshot/stealth. |
| 292 | `Hideout Kitchen Stove Wonderitem` | Same invalid card alternative; heat/damage alternatives are independent. |
| 297 | Kitchen Hallway → Kitchen Front | Invalid friendly-card alternative. |
| 298 | Kitchen Hallway → Kitchen Rear | Invalid friendly-card alternative. |
| 299 | Kitchen Hallway → Kitchen Pots | Invalid friendly-card alternative. |
| 310 | Kitchen Front → Kitchen Rear | Invalid friendly-card alternative; Hover Boots is a separate alternative here. |
| 311 | Kitchen Front → Kitchen Hallway | Invalid friendly-card alternative. |
| 323 | Kitchen Rear → Kitchen Front | Invalid friendly-card alternative; Hover Boots is separate. |
| 324 | Kitchen Rear → Kitchen Hallway | Invalid friendly-card alternative. |
| 346,347 | `Hideout Break Room Pot 1`, `2` | Invalid card alternative; Bow/Hookshot/child-combat routes remain separate. |
| 351,352 | `Hideout Break Room Crate 1`, `2` | Invalid card alternative; crate-breaking and child-height/combat alternatives are separate. |

**Transitive consumers, not additional direct card terms:**

- Gate event → fortress exit52 → `GF Outside Gate` → `Wasteland Near Fortress`
  and the desert chain in `haunted_wasteland.toml`. Back edges fortress179 and
  wasteland16 are not additional adult membership gates (179 already admits
  adults, 16 is True); fixing the forward source condition must not close a
  legitimate return route. Spirit/Colossus also have other entrances/warp
  routes, so do not call every desert check unconditionally card-required.
- Roof49 feeds `GF Chest`117, `GF GS Top Floor`131 and the route through
  exterior92 to the three-torch jail. Alternative roof/balcony routes remain.
- The GTG lobby admits its whole region graph; wrong entrance permission can
  unlock its shuffled chests before native entry talk is available.
- Kitchen and break-room terms can affect traversal even while their
  individual pot/crate contents are not shuffled.

**Helper/source audit:** `helpers.toml:90` `can_finish_GerudoFortress` already
reads the four carpenter events in normal mode, not the card. The events are
fortress191/216/245/265; the original captain reward is fortress195. Those are
the source-completion side of the mismatch, not extra card terms to delete.
`gerudo_valley.toml:27,112` use carpenter completion for the bridge and should
not be switched to remotely-held-card ownership. Fast/open fortress settings
are inherited assumptions, not native fast-carpenter patch evidence; this
investigation's Recommended measurement uses normal mode.

**Separate fixed-tier jail mismatch:** fortress50–51 models asking a guard to
jail Link as `can_use(Hookshot)`. `helpers.toml:10` aliases this to the progressive
tier, so Longshot alone satisfies it, unlike native `IsGet.Item_Hookshot`.
The rest of `can_use(Hookshot)` must not be globally narrowed: Longshot really
does serve ordinary hookshot targets. A future logic repair needs a local
arrest predicate or a verified alternative entrance, not a global tier change.

No translated TOML, remake overrides or helpers were edited. A future C repair
belongs in sourced remake overrides, not manual edits to generated N64 files.

## 7. Verification and measurement provenance

Executed on this worktree, no game start:

- `uv run python E:/OOTRemake/work/rounds/r13/gerudo-card-cs13d/inspect_game.py logic '*GerudoFortress*'`
  and the analogous `MiniGame_HorsebackArchery*` decode: actual dump graphs read.
- `inspect_game.py flow ...`: actual captain, SageOfSpirit, carpenter rescue,
  all relevant Gerudo NPC and archery flows parsed; indices above are file
  indices, Event names are native labels (not interchangeable).
- `inspect_resources.py`, `schedules.py`, `flag_readers.py`: actor/global pack,
  schedule/registry/schema and every-flow prison-state cross-checks described
  above. Initial parser/API failures printed their actual payloads before
  cause-directed correction; no unchanged failing command was rerun.
- `uv run python E:/OOTRemake/work/rounds/r13/gerudo-card-cs13d/verify_structure.py`:
  **PASS, 48 guard decision cases**, six real graph paths × four quest-step
  positions × card false/true. No card value changed security; crossing
  Step01 did. It also checks the exact native jail query and captain
  continuation. `structural-proof.json` holds the results outside the repo.
  This is a structural data oracle, **not a game/runtime test**.
- `uv run ruff format --check`: **PASS, 318 files**.
- `uv run ruff check`: **PASS**.

The 100-seed public CLI audit is queued after the ordered heavy jobs under
`E:/OOTRemake/work/rounds/r13/gate.lock` (Claude's 17:05 order: cs13b public
generation, then cs13a integrated gates/matrix). It remains pinned to this
baseline and is not replaced with cs13b's newer-code API sweep. No count or
full pytest result is claimed by this first evidence record.
