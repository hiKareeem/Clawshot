# Round 12: small keys anywhere (cs12b)

Branch `r12/keys`; scratch `E:/OOTRemake/work/r12-keys-cs12b`.
Read AGENTS, README, CONTRIBUTING, roadmap, architecture, orchestration, world format,
decisions (D38/key policies), game-data sections40/44/45, r11-keys, external production
binding/text plans, handoff notes, played results, Test6 launcher/builder/verifier.
The dump and all previous mods/profiles/save backups remain read-only. No game starts,
windows, bootchecks, merges, pushes, dependency/version changes or terminal-control commands.

## Scope / provisional implementation choices

- cs12b proposes Gate1 alone: extract the parameterized common helper through the
  already-played native small/big bindings. Keep Gate2 source-binding startup separate:
  a failure then identifies the gate rather than conflating helper and event startup.
- Gate1 uses Forest target only, native small-key appearance and generic messages.
  New target-labelled text is generator work, not claimed played by this gate.
- Independent generator slices: off-dungeon small-key model/fill restrictions;
  strict new-label writer and dump-resolved English names. Parent owns grant/bindings.
- `dungeon_items=anywhere` remains refused by CLI and seed pipeline. Only small keys
  may leave their dungeon in the intended mode; boss keys/maps/compasses stay inside.
- No in-game roster. The later Tracker tab reads the seed's own saves (D38); no UI work
  in this track. Native current-dungeon standing counters remain unchanged.
- Gate3/4 mods will not be built before Claude posts the preceding played result.
  A failed gate stops forward mod construction; record evidence/diagnosis and post.

## Gate 1

**PASSED. Staging/checklist record below; played evidence follows under “Played result”.**

Launcher (copied from the current central template, ASCII/CRLF):
`E:/OOTRemake/work/r12-keys-cs12b/ingame/Key gate 1 - Midos house then Deku Tree map chest.bat`.
Exactly one real mod below `ingame/mods/key-gate1-common-helper-next/`:
`key-gate1-common-helper-next/romfs`. Never enable another mod for this test.

Source: read-only backup `E:/OOTRemake/work/save-backups/2026-11-07_1630`,
**autosave slot_04**, the r11 small-chest source. It has both test chests explicitly
closed and Forest0/0/false. Test6's slot_02 has Mido already open, so it cannot prove
both sizes in one continued run. This uses an existing r11 checkpoint, not an invented
save position. The launcher copies all slots; choose autosave04 explicitly.

### Player checklist (one continued copy, small chest first)

1. Quit the other game. After Claude's boot check, run the launcher above. Continue
   **autosave04**. Only Teleport and the clock are allowed; no inventory, age or flag cheats.
2. Go into **Mido's house in Kokiri Forest**. Open only the **far-right small chest**
   (same chest as r11 test1/first named-Forest test). If unsure which chest that means,
   stop and report rather than opening the others. It should give one small key.
3. Report the **exact message text**, whether the item window closes and Link moves
   normally, the key number beside the on-screen map and on the pause map, or
   **“no key number visible”** separately for each. Generic small-key text is intentional
   in this helper-only gate; it is not expected to say Forest yet.
4. **Save and Continue now.** Tell Claude to take the after-small save snapshot before
   continuing. Expected saved change: Forest remaining/total0/0→1/1, first-key true;
   all13 other dungeon inventories unchanged. Do not collect or spend any other keys.
5. Use Insert > Cheats > Teleport > **Inside the Deku Tree (Entrance)**. Teleport reaches
   only that entrance. Climb the lobby ladder and follow the second-floor ledge to
   the **big map chest beside the vine wall**, the same chest as r11 tests2/5/6.
   Open only that chest; do not go to the Slingshot room or open other chests.
6. Report whether it opens, the **exact message text**, normal window/animation cleanup,
   and the key numbers on **both** the on-screen and pause maps (or their absence).
   It should give a second small key, not the Deku map.
7. **Save and Continue again.** Tell Claude to take the after-big snapshot. Expected:
   Forest remaining/total1/1→2/2, first-key true; Deku stays0/0/false with map false;
   all other dungeons unchanged. Return to each opened chest after reloading: neither
   should offer a second reward. Report any repeat, lost movement, wrong item or crash.
8. **Do not try a locked door in this child checkpoint.** Door spending was played in
   r11 and will be rechecked with mixed source routing in gate3; gate1's door report is
   “not attempted”. A new adult checkpoint would be a different experiment. If a door
   unexpectedly opens or a key is spent, report it and stop.

**Isolation limit:** all big-chest small keys route to Forest in this mod, as in
Test6. The small binding is the played Mido wrapper. No production source routing is
being certified; open only the two named chests. Stop on the first failed step.

### Artifact proof

`build_gate1.py` and independent `verify_gate1.py` live in the scratch root.
The latter read the actual seven emitted resources, not just builder expectations:
three Bancs, three flows and the size table. It checked whole native-flow inverses,
byte-identical played small binding, exact original actor trees after reversing drops,
all original entries/operations except declared additions, exact table growth,
dictionary compression, one real mod/no links, template/ASCII/CRLF and backup hashes.
The parameterized helper lives once in GetPouchContent; both chest paths pass the
three literal Forest field names. Owning entries include the new sub-flow dependencies.
Six serialized traces (small/big × first/existing/spent) compared all14 inventories:
one target grant, no standing-dungeon or pouch credit. Non-key small content retains
the original native pouch grant. This interpreter does **not** prove native startup/UI.

`uv run python .../build_gate1.py`: built7 resources. Initial extraction assertion
printed nodes128–131; a diagnostic printed total219 events and trailing clone nodes:
the grant is embedded, not the last4. Corrected to share those nodes in place, then
the single cause-directed build passed. No files had been emitted by the failed build.
`uv run python .../verify_gate1.py`: **PASS**,6 traces, exact inverse/table.
Actual launcher dry-run via cmd with **CLAWSHOT_DRY_RUN=1**: exit0; printed the
bin executable, isolated user and exact HOS_MODS. Copied saves match backup hashes;
no hookshot_log exists. The profile now exists only from this dry run; never reset it.
Proof: `gate1-build.json`, `gate1-verification.json`. Old r11 artifacts untouched.

### Played result: Gate 1 PASSED

Claude's 2026-11-11 report is accepted ground truth, not rerun here. Kareem played
12:17–12:25 on Hookshot2.1.0 from the autosave04 copy. Claude boot-checked it first:
509 log lines, no crash, save reached,7 mod files indexed/14 entries. He automatically
snapshots save writes; Kareem need not stop for manual copying.

All14 dungeons and both named chest flags were compared against source slot04 by
`E:/OOTRemake/work/r12-keygate1-check/gate1_saves.py`; snapshots are
`E:/OOTRemake/work/save-backups/2026-11-11_12*-r12-keygate1-1..10`.
After Mido: Forest remaining/total/first0/0/false→1/1/true, chest open.
After Deku: Forest2/2/true; Deku0/0/false/map false; every other dungeon unchanged.
Both chests remain open after Save and Quit, no duplicate.

Kareem's words:
- Mido: **“Small Key, counter showed up but did not increment”**. Window closed;
  Link could move; no key number by either on-screen or pause map in Kokiri Forest.
- Deku: **“You found a small key!”** / **“You can use it to unlock doors in this area,
  but it won't fit locks you find elsewhere.”** No key number on either map in Deku
  (expected: saved credit belongs to Forest, not Deku).
- Could not walk back to Mido's house: Mido and a Kokiri blocked both ways. Could not
  load an earlier autosave from the title; not investigated. After-small slot05 and00
  both hold Forest1/1. Teleport to Kokiri started vanilla Saria farewell/ocarina scene;
  unrelated to the key grant. Do not claim physical Mido re-entry was played.

Claude authorized Gate2 only after this result, now including the dungeon-named text.
Requested rebase onto main `9f86b3a` before the next repository handoff.

## Gate 2

**FAILED at startup for both sizes. Do not rerun, alter or reset this mod/profile.**

Launcher:
`E:/OOTRemake/work/r12-keys-cs12b/ingame/Key gate 2 - Midos house then Deku Tree map chest.bat`.
New real one-mod layout: `ingame/mods/key-gate2-named-wrappers-next/`
`key-gate2-named-wrappers-next/romfs`. Fresh profile; Gate1 profile/mod remain untouched.
Same original1630 backup and **slot_04** checkpoint as Gate1; Forest starts0/0/false,
both chests closed. No new save position or room Teleport.

### Player checklist

1. Quit the other game. After Claude's boot check, run **Key gate 2** above, not Gate1.
   Continue this fresh copy (the original autosave04 checkpoint used for Gate1).
   If the Mido target is already open, stop: do not try to select an old autosave from
   Gate1's played profile. Only Teleport/clock cheats; no inventory/age/flag cheats.
2. Enter **Mido's house**, open only the **far-right small chest**, the same one as Gate1.
   Report **does it open when you press Open?** If not, stop here and report the prompt.
   If it opens, both messages should name Forest:
   **“Small Key (Forest Temple)”**, then **“Opens one locked door.”** /
   **“Dungeon: Forest Temple”**. Report the exact text actually seen, line wrapping,
   whether the window closes and Link moves normally, and any extra generic message.
3. Report the key number by the **on-screen map** and on the **pause map** separately,
   or “no key number visible” for each. A current-area key increase is not expected in
   Kokiri Forest. **Save and Quit, then Continue this copy.** Claude captures save writes.
   Expected saved state: Forest1 remaining/1 total/first true; all other dungeons unchanged.
4. Teleport to **Inside the Deku Tree (Entrance)**. Climb the lobby ladder to the
   second-floor ledge and the **big map chest beside the vine wall**, same chest as
   Gate1. Open only that chest. Again report whether the Open prompt actually starts
   opening; stop on failure, without trying other chests.
5. Report the exact **main message and caption**, wrapping, model, animation/window
   cleanup, and key numbers on **both** maps (or absence). Both messages should still
   say **Forest Temple**, not Deku or “this area”; there should be no second generic
   caption. It should give a small key, not the map.
6. **Save and Quit, then Continue.** Expected saved state: Forest2/2/true,
   Deku0/0/false/map false, all13 other dungeons unchanged. The Deku chest should
   remain open and give nothing again. Mido's saved opened flag is checked too;
   **do not try to walk back through the blocked Kokiri route** from Gate1.
7. Report any duplicate, crash, wrong target, misleading caption or lost movement.
   **No door is attempted in this child checkpoint**; report “not attempted”.
   Spending belongs to the later mixed-source test, not a silently substituted adult save.

### Artifact proof

`build_gate2.py` uses the actual production `make_plan` → `keys.changes` → common writer,
with two Forest assignments. It emits25 resources:3 Bancs,4 flows,16 Mals,EventSetting,
size table. New source-specific wrappers preserve the original Mido flag and Deku
Navi follow-up, player participation and EventTransition; named destination rows copy
native chest/camera settings. Original rows/entries/events remain untouched.
The single helper is graph/type/parameter-identical to played Gate1; only its callers'
binding and presentation change. Four new EventSetting rows, two literal Forest callers.

Independent `verify_gate2.py` read actual staged bytes: whole native-flow and row inverses,
exact actor-tree inverses, all new sub-flow dependency lists, local/external entry resolution,
all16 English-only new-label inverses (old MSBT order/buckets and other members unchanged),
dictionary compression and the exact entire size table passed. EventSetting509212→509916,
allocation509480→510184. Its `(32-byte alignment,+264)` formula matches the original
EventSetting and all19 ordinary non-ActorInfo RSDB tables; only EventSetting growth is
enabled. Runtime adequacy still belongs to this played gate.

Actual launcher **CLAWSHOT_DRY_RUN=1**: exit0, correct bin/user/HOS_MODS,
ASCII/CRLF/exact current template/one real mod/no links; copied saves match the read-only
backup hashes, no hookshot_log. Initial verifier used the nonexistent attribute
`bucket_count`; printed `Msbt` fields `messages,buckets`, buckets2 and both actual new
messages, corrected to `buckets`, then the one cause-directed verification passed.
No mod/profile was rebuilt. Proof: `gate2-build.json`, `gate2-verification.json`.

### Played failure and stop boundary

Kareem12:35, Hookshot2.1.0, fresh original slot04 copy. Small Mido far-right
**“does not open”**. For **both** it and the Deku big map chest:
**“The interact sound plays then nothing. No animation plays.”**
**“Deku Tree chest exactly the same.”** Walking away/back restores the prompt,
then the same failure. An unmodified neighbouring chest in the room gave its normal
interact sound, Link/chest animations, overhead item and get-item sound.
No grant was reached; this is event startup failure, not a failing named-key payout.
Claude's five save snapshots (`save-backups/2026-11-11_12*-r12-keygate2-1..5`)
show both chests still closed and no dungeon key fields changed in any save.
The failed opens left no saved state. Accepted report; not rerun here.

Claude's read-only log report:1654 lines so far, no crash/error; Hookshot served
USen Mals, EventSetting, Kokiri Child Dynamic, Small, Pouch, NaviChat, Big and size
table from this mod. The game was still running when reported. Its exact log path:
`.../ingame/user-key-gate2-named-wrappers-next/hookshot_log.txt`.
The earlier absence of that log above describes dry-run time only.
Gate1's same-save played native bindings remain the positive control.
**All forward mod construction stopped. No gate3/4, replacement mod or retry is built.**

### Data-only diagnosis (not a demonstrated native rejection guard)

`diagnose_gate2.py` read native registries and failed bytes, without touching the game
or played profile. `gate2-diagnosis-data.json` retains decoded evidence outside the repo.

| Candidate | Evidence / confidence |
|---|---|
| Missing analyzed-event registration/dependency closure | **Medium-high, leading.** Native GameAnalyzedEventInfo has2379 rows: exactly every one of2380 EventSetting IDs except PlayOcarina_ReplaceEvent. None of the4 custom Gate2 IDs has an analyzed row. Native Mido SubFlowList lacks the newly introduced NaviChat call; native Deku ChildEventList names the original big event, not the new destination. These omissions are proved; that the engine refuses startup for them is still an inference. |
| New row lookup or changed wrapper/destination context | **Medium.** Both fail before any animation; new source IDs/entries distinguish them from Gate1. Mido also introduces a participation/transition stage; Deku retains its native outer participation/transition shape. Both failing weakens a small-only lifecycle explanation. |
| EventSetting growth/allocation | **Low-medium, unplayed.** Exact read-back/inverse and aligned32+264 match the native EventSetting and19 ordinary RSDB tables; no runtime growth control has yet separated this from new row registration. Static fit does not prove the allocation contract. |
| Name truncation, grant, labels or missing file | **Low for this failed gate.** New chest event IDs are62/50 ASCII bytes, fitting the inspected String64 field. Helper graph equals played Gate1, all resources loaded, and nothing reaches animation/display/grant. These are not leading explanations for pre-animation refusal. |

EventFlowFileEntry is only the13-flow version map, **not** custom entry registration.
Linear entry resolution/read-back alone is not proof of native startup. No claim that
an English label or another serializer rerun can repair the failure.

### Proposed smallest separating test (posted; NOT built)

**cs12b proposal:** a table-growth-only control based on the exact played Gate1 mod.
Keep both chest bindings, flows, helper and generic text byte-identical to Gate1.
Add one **valid but unused** EventSetting alias row pointing to an existing native
entry, and the corresponding checked size-table growth; do not select the alias from
either chest, add no custom entry/transition, and leave all other registries alone.
Use only the Mido chest in the same original slot04 copy.

- Opens: added-row/table growth alone is not sufficient to cause startup failure;
  next isolate selecting a new event ID versus matching analyzed-event registration,
  still using a played native entry, before any custom destination.
- Fails before animation: prioritize table-addition/lookup/allocation and inspect its
  printed sizes/rows; do not add metadata, text or lifecycle changes hoping for green.

Posted before building as requested. Waiting for Claude's authorization/result-driven
next step; the failed mod remains frozen. No new mod is handed over by this proposal.

## Gate 2b: authorized registration/control experiment

Claude superseded the growth-only proposal to save Kareem a separate play.
**PASSED. Staging/checklist record below; exact played evidence follows.**

Launcher:
`E:/OOTRemake/work/r12-keys-cs12b/ingame/Key gate 2b - Midos house then Deku Tree map chest.bat`.
Fresh real one-mod/profile name `key-gate2b-registered-small-control-big-next`;
same original1630 backup **slot_04**, not a copy of either played gate profile.
Old Gate1 and failed Gate2 resources/users remain untouched.

### What this one test separates

- Mido small: same custom startup/content graph as failed Gate2 and same Forest-labelled
  text, now with analyzed-event registration for its two new event IDs. Source row
  retains every native field, adds NaviChat to SubFlowList and the named small destination
  to ChildEventList. Destination's native-modelled SubFlowList includes GetPouchContent,
  where the helper entry lives; helper is not an invented flow file. Owning EVFL entries
  also list every called sub-flow event index.
- Deku big: **Banc and big-flow bytes exactly equal played Gate1**, native source row
  and binding, generic text. It calls the same proven helper. Both paths share the
  grown EventSetting/analyzed tables, isolating registration from global table breakage.
- Only the two small aliases are registered/selected; no custom big wrapper is selected.
  A new big-wrapper attempt waits for Claude's result and gate2c authorization.

### Player checklist (try both even if the small one fails)

1. Quit the other game. After Claude's boot check, run **Key gate 2b** above; Continue
   this fresh original autosave04 copy. Only Teleport/clock cheats, no inventory/age/flags.
2. Go into **Mido's house**, press Open at the **far-right small chest**.
   Report: prompt? interact sound? Link animation? chest animation? does it open?
   If it opens, expected messages: **“Small Key (Forest Temple)”** then
   **“Opens one locked door.”** / **“Dungeon: Forest Temple”**.
   Report exact text, wrapping, item model, normal window close and restored movement,
   and any extra generic caption. If it fails, report that and continue to step4.
3. Report the key number by the **on-screen map** and on the **pause map** separately,
   or “no key number visible”. Save and Quit, then Continue. Claude captures save writes.
   On success Forest should be1 remaining/1 total/first true, all others unchanged.
4. Teleport to **Inside the Deku Tree (Entrance)**. Climb the lobby ladder to the
   second-floor ledge and **big map chest beside the vine wall**, the same as Gate1.
   Press Open. Again report prompt/sound, Link/chest animation and whether it opens.
5. On success the big **control** intentionally says the game's generic small-key
   message/caption (unlike Mido). Report exact text, normal cleanup and numbers on
   **both maps**, or their absence. It should not give a map. Save and Quit, then Continue.
6. Expected saves: both open→Forest2/2/true; only big open→Forest1/1/true;
   only small open→Forest1/1/true; neither open→Forest0/0/false. Deku stays0/0/false,
   map false; every other dungeon unchanged. The opened chest(s) must stay open and
   give nothing twice. Failed chest(s) should stay closed. No door is attempted;
   report “not attempted”. Do not walk back through Mido's blocked route.
7. Report any crash, duplicate, lost movement or wrong target. The two openings are
   the whole experiment; do not open other chests or collect/spend another key.

Readings agreed by Claude: Mido opens→registration caused the original failure
(then treat the big wrapper in2c); Mido fails/Deku opens→grown tables are usable,
some other custom-startup difference remains; both fail→investigate the grown tables
before more custom startup changes. Partial animation/failure is reported exactly,
not forced into one of those outcomes.

### Independent artifact checks

`build_gate2b.py` / `verify_gate2b.py` use new scratch artifacts only.
**26 resources**; two new EventSetting and two matching analyzed rows. Actual-byte
whole native-flow/Banc/registry inverses and exact entire size table passed.
Mido startup/content graph equals failed Gate2 after normalizing unrelated node indices;
all16 text archives equal Gate2 bytes. Deku Banc/big flow equal played Gate1 bytes.
Helper graph/parameter types equal played Gate1; source-modeled analyzed fields preserve
everything except new ID and declared dependency lists.

EventSetting509212→509568/allocation509480→509832.
Analyzed247276→247532/allocation247560→247816.
Both formulas align32+264, checked against original entries and the19 ordinary RSDB
tables. Both registries preserve all old rows and sort the new rows deterministically.
Source constructor/writer inverse/read-back, compressed bytes, entry dependency lists,
one real mod/no links and ASCII/CRLF/exact central template all passed.
Actual **CLAWSHOT_DRY_RUN=1** exit0; correct bin/user/HOS_MODS, copied backup hashes
match, no hookshot_log. Proof: `gate2b-build.json`, `gate2b-verification.json`.
No native startup claim follows from these data checks; Claude/Kareem supply that result.

### Played result: Gate 2b PASSED

Accepted Claude/Kareem report,12:52–12:56, Hookshot2.1.0, fresh slot04 copy.
Mido's registered named small wrapper opened normally. Main:
**“Small Key (Forest Temple)”**. Screenshot caption exactly two lines:
**“Opens one locked door.”** / **“Dungeon: Forest Temple”**.
Key held overhead; **“indicator comes up but does not increment”** in Kokiri Forest,
expected for a Forest credit. Deku's played big control opened with normal generic
text and no key indicator.

All14 comparison: after Mido Forest0/0/false→1/1/true; after Deku2/2/true;
Deku0/0/false/map false, every other dungeon unchanged. Chests remain open after
Save and Quit; no crash line. Snapshots:
`save-backups/2026-11-11_12*-r12-keygate2b-1..6`;
checker `work/r12-keygate1-check/gate2b_saves.py`.
No rerun to confirm reported facts.

**Cause confirmed by this controlled play:** missing analyzed-event registration
prevented the original custom startup. Registered small startup and Forest text now
have played acceptance, and the native big control proves both grown tables usable.
The custom big destination still needs its own registration/startup proof (2c).

## Gate 2c: registered big destination, registered small positive control

Authorized only after2b passed. **Built and independently checked; UNPLAYED.**
Claude reported normal game exit13:04, no Hookshot process; snapshots7–8 changed
option.sav only. Accepted without rerunning that observation. Build and verifier then
ran serially, one process each; no gate lock taken for these focused artifact checks.

Launcher:
`E:/OOTRemake/work/r12-keys-cs12b/ingame/Key gate 2c - Midos house then Deku Tree map chest.bat`.
Fresh real one-mod/user `key-gate2c-registered-both-sizes-next`, same original1630
backup and **slot_04**, not either played profile. Gate2b Mido's actor binding and
both small analyzed/settings records are retained exactly; its full startup/content
graph is unchanged after normalizing unrelated shared-flow indices.

### Player checklist

1. Quit any other game. After Claude's boot check, run **Key gate 2c** above and
   Continue the fresh original autosave04 copy. Only Teleport/clock cheats.
2. Enter **Mido's house**, open the **far-right small chest**, same as2b.
   This is the **positive control**. Report prompt/interact sound, Link/chest animation,
   whether it opens, item model, exact main/caption and normal window close/movement.
   Expected **“Small Key (Forest Temple)”** then **“Opens one locked door.”** /
   **“Dungeon: Forest Temple”** on two caption lines.
3. Report key number on the **on-screen map** and **pause map** separately, or none;
   the Kokiri pickup indicator can appear without incrementing, as in2b.
   **Save and Quit, then Continue.** Expected Forest1/1/true, all others unchanged.
4. Teleport to **Inside the Deku Tree (Entrance)**. Climb the lobby ladder to the
   second-floor ledge and **big map chest beside the vine wall**. Open only it.
   This is now the **registered custom big wrapper**, not2b's generic control.
   Report sound, Link/chest animation, whether it opens, exact two messages, wrapping,
   item model, cleanup and restored movement. Both messages must name **Forest Temple**,
   exactly as Mido; no extra generic “this area” caption should appear.
5. Report key numbers beside **both maps**, or absence. It should give a Forest key,
   not a Deku map/key. **Save and Quit, then Continue.** Expected Forest2/2/true,
   Deku0/0/false/map false, all13 other dungeons unchanged. Opened flags must persist
   with no second reward. Do not walk back through Mido's blocked route.
6. Report any failure/partial animation, wrong text/target, repeat, crash or lost control.
   No door is attempted in this child checkpoint; report “not attempted”.
   If the big path fails, stop after recording it; no other chests or key pickups.

### Actual artifact proof

`build_gate2c.py` and independent `verify_gate2c.py`: **PASS**,26 resources.
Four new EventSetting IDs have four matching analyzed records and exact declared
sub-flow/child dependency closure. All native actor trees, flow entries/events and
registry rows invert exactly. Mido Banc bytes and its selected row/metadata equal2b;
its complete startup/content graph equals played2b. All16 English message archives
equal played2b bytes. Big source/destination rows copy their native lifecycle/camera
settings and add the corresponding analyzed records. The original common helper is
unchanged; no standing-dungeon or second pouch payout is introduced.

EventSetting509212→509904/allocation509480→510184.
Analyzed247276→247716/allocation247560→248008.
Exact entire table, dictionary compression, every new entry's sub-flow indices and
runtime ID closure passed. Mido keeps its played alias; only the newly selected big
source uses the bounded production alias. One real mod, exact current central template,
ASCII/CRLF and no links. Actual **CLAWSHOT_DRY_RUN=1** exit0; correct bin/user/HOS_MODS,
copied saves match read-only backup hashes, no hookshot_log.
Proofs: `gate2c-build.json`, `gate2c-verification.json`.
Old mods/users remain untouched; no gate3/4 is built before Claude posts2c's result.

### Played result: Gate 2c PASSED

Accepted Claude/Kareem report,~13:08–13:12, Hookshot2.1.0, fresh slot04 copy:
**“Works perfectly, Forest Temple shows for both small keys, no map from the Deku Tree.”**
All14 comparison: after Mido Forest0/0/false→1/1/true; after named Deku big2/2/true.
Deku0/0/false/map false; every other dungeon unchanged; chests stay open; no crash line.
Snapshots `save-backups/2026-11-11_13*-r12-keygate2c-*`;
checker `work/r12-keygate1-check/gate2c_saves.py`. No reconfirmation rerun.

Cosmetic finding: opening the changed Deku map chest still makes Navi say
**“Now we won't get lost”**. That is the preserved source map follow-up, not a map
grant. Production named-key clones must omit item-specific Navi follow-ups when the
chest no longer gives that item, without deleting story state. Ordinary plans already
retain `keep` overrides for changed map/compass chests (`chest_events.toml`,
`plan.make_plan`, `write.patch_tree`); the observed Deku wrapper is unconditional.
The same retention mechanism exists for other map/compass sources, but each native
wrapper's actual follow-up must be checked before claiming it speaks the wrong line.
Only named-key clones will be corrected in this track; ordinary seed behavior is
reported, not silently changed. The running full-source gate snapshot remains frozen
until the separately prepared correction can be verified against its actual native call sites.

## Gate 3 preparation: door source, no invented position

**Existing door source available:** original
`save-backups/2026-11-09_1022-main-adult-first/save/5a3c9e1f0b7d24680000000000000001`,
manual **slot_01**. R11's played door experiment used exactly this checkpoint:
Bombs/Master Sword owned, Hookshot absent, Forest0/0/false;
Goron center maze chest1176975953041865014, Forest entrance door1163369963105284964
and native tree chest1171460703078800858 explicitly closed. Mido's opened chest is
the same-slot positive save control. No new door save position is needed.

Played route: Teleport **Goron City**, top-floor west boulder maze, bomb the
middle-corridor rock, open the straight-ahead center pocket chest, not its twin.
Teleport **Forest Temple (entrance)**; walk to the entrance courtyard's first chained
door and spend the routed Forest key. Then climb the east vines/high branches to
the untouched native tree key. No Hookshot or room Teleport; this exact grant/spend/
native-key route already passed r11. Gate3 will compare all14 states at each stage.

**Resolved by Claude:** ONE mod, two launchers, two fresh users from these existing
backups; no new checkpoint. Part A uses child slot04 for both sizes/two targets and
the unchanged Slingshot; part B uses adult manual slot01 for the existing Goron
grant/Forest door/native tree-key route. Availability and all14 source fields were
checked before building. Both source copies remain byte-identical to the backups.
The exact staged artifacts, two checklists and expected transitions are below.

## Generator implementation (still refused for players)

- Model:8 explicit native target IDs, no copied names. An off-dungeon small key remains
  a change even if its generic drop actor matches the old actor. Target selection uses
  the physical Banc area, not the logical region or current standing dungeon.
  All age/Hash copies retain their physical kind and source-specific event classification.
  The writer refuses an unbound named key or stale source event before writing anything.
- Fill: anywhere releases only small keys, and only chests outside their dungeon can
  deliver those. Boss keys/maps/compasses remain own-dungeon; every fill/swap stage
  uses the same restriction. Hint classification uses that restriction too.
- Bindings: deterministic source-family/target wrappers, separate named small/big
  destinations, independent story/Navi lifecycle and camera settings retained; obsolete
  item-only Navi comments omitted in named clones. One argument-driven helper writes
  existing saved remaining/total/first fields; metadata
  validates those fields. No invented actor/Hash query, new saved state or global latch.
  Original flow entries/events and EventSetting rows invert exactly; owning cloned
  entries carry their sub-flow dependencies. Prior gift/text transforms compose first.
- Text: strict new-label addition, preserving every old message/index/bucket and other
  SARC members. English noun and dungeon names read from USen at generation; all16
  languages receive the same pair per used target. Native generic messages are unchanged.
- Public CLI and `make_seed` still refuse anywhere before dump access/output; no research
  bypass setting was added. Source-bound steps are ready behind that unchanged boundary.
  Defaults keep their previous placement/output policy. Version and uv.lock untouched.

### No-game behavioral evidence

Focused single-file runs (`CLAWSHOT_WORKERS=1 uv run pytest <file> -q --tb=short`,
fresh scratch `--basetemp` per run):

| File | Result |
|---|---|
| `tests/test_key_bindings.py` |6 passed: both sizes/two targets in two orders, source follow-ups, native/non-key controls, deterministic bindings, collisions |
| `tests/test_key_model.py` |18 passed: same-actor/different target, age copies, stale/unbound rejection, physical-area routing, fill/return-kit boundaries, deterministic writer |
| `tests/test_key_text.py` |18 passed,1 skipped (dump unset); later removed2 label-format-only tests, retained behavioral archive/target tests |
| `tests/test_keys.py` |7 passed: direct/CLI/CS1 refusal, no output, print/replay |

`uv run ruff format <15 named source/test paths>`:3 reformatted/12 unchanged;
`uv run ruff check`: all checks passed. Full four-command gates follow after rebase.

Actual CLI smoke (`smoke_cli.py`, one worker): explicit anywhere+Gift and CS1 replay
each exit1, no output folder; default own-dungeon seed7 Kokiri/Lost Woods/Deku slice
exit0,28 resources with spoiler/play note. `cli-smoke-proof.json` and logs retained.

Actual native-data API smokes (not playable gate mods; no launcher or save user):
- `smoke_emission.py`:33 source families ×2 targets,66 requests/68 bindings including
  dependent Jabu wrappers;16 native flowcharts; common writer emitted34 resources
  twice with identical SHA256 maps and exact allocations. `generator-emission-proof.json`.
- `smoke_plan.py`: real census/definitions/world, Mido Forest and Deku Fire assignments,
  `make_plan`→`keys.changes`→common writer;25 resources twice byte-identical, correct
  drop and wrapper binding in every age Banc. `placement-emission-proof.json`.
- Those outputs are solely generator-emission probes, not gate3/4 test mods or gameplay
  evidence. No game/bootcheck was started by this track.

### Pre-existing physical-area risk for review (not silently fixed)

Spirit hand chests2490063409521505179 (Silver Gauntlets, kept Nabooru event) and
10012167258643363548 (Mirror Shield, kept shield event) belong to Spirit logic regions
but physical `DesertColossus`, whose DungeonParam has no target. Anywhere small keys
there now use the named Spirit grant. **[INFERENCE, not played]** generic own-dungeon
small keys and Spirit boss keys/maps/compasses there may be lost. The existing logical
own-dungeon policy is deliberately unchanged in this track; this is a release-review
risk, not a proven new regression or acceptance for those other item families.
Posted to Claude; no unrelated logic/default cutover was invented.

## Commit ledger

Rebased successfully onto requested main `9f86b3a`; earlier thread hashes are superseded.

| Commit on the requested base | Scope |
|---|---|
| `066c361` | Gate1 scratch proof and plain checklist record |
| `1820f44` | Small-key model/fill and age-copy/source binding constraints |
| `1f0da7b` | New-label operation and dump-resolved English pickup pair |
| `81af742` | Source wrapper compiler, shared helper, guarded pipeline, allocation formula |
| `f94371d` | Cause-directed analyzed-event registration/dependency closure for authorized2b; cache input and consumer coverage |
| `19ccbf2` | Gate1/2 results,2b checklist, artifact evidence and public refusal reference |
| `32da483` | Bound production source event IDs to the actor's String64 field |
| `4d7990c` | Record passed registered-small gate and verified registered-big handoff |
| `b888fd7` | Record passed named-big gate and existing mixed-test door route |
| `02e20c8` | Preserve the default small source's argument bootstrap;9 focused tests pass |

Registration addition: named event IDs now get source-modelled analyzed records,
preserving all native records/fields and carrying SubFlowList/ChildEventList closure.
The NUP working set includes that native registry. The synthetic event consumer now
requires both registration and declared cross-flow/child dependencies before execution.
Its six existing routing cases passed after this change; a missing-source-registration
case was then added for the full suite. Gate2b subsequently confirmed registration
as the startup cause; Gate2c confirmed the same treatment for the named big path.

Production-name boundary: the dump's chest GetEventName blackboard parameter is
String64. Longer source-family/target concatenations could overflow it, so new source
IDs use a deterministic12-hex SHA256 source digest plus target, with collision refusal.
Binding records still retain the full source identity. A synthetic boundary case covers
two long sources with the same prefix and the long Gerudo target; IDs must remain
distinct and below64 bytes. This is **not** a diagnosis of Gate2 (its62/50-byte IDs fit).
All staged gate mods, including2b, remain frozen with their independently verified IDs.

## Questions

**Kareem: if a later gate needs a new save position, please supply it; this track will
not invent a room Teleport or modify your existing saves.** Existing r11 backups/slots
are the only sources currently authorized.

## Verification / commits

`tasklist /FI "IMAGENAME eq hookshot.exe"` reported no matching process at research
and before integration. Every pytest uses `CLAWSHOT_WORKERS=1`, regardless.
Full suites/dump/sweeps acquire `E:/OOTRemake/work/rounds/r12/gate.lock` via mkdir.
**Queue directive from Claude:** cs12c finishes its current sequence, then Claude's
`review-pr3` gates run. This track will not acquire the lock until Claude posts
`review-pr3 gates done`; focused single-file checks and the single-process Gate3
build/readback need no lock. No automatic lock-waiting runner remains active here.

## Gate 3: approved one-mod, two-user handoff

Claude selected the two existing backups above. No new save or position is requested.
Built with production source bindings after `02e20c8`, not by forcing the Mido
source onto unrelated small chests. That fix preserves the default source's false
Navi-off reset and its `IsMiniGame=False` argument bootstrap before the registered
handoff. Mido's separate true bootstrap remains intact. Its regression file passed
**9 tests in0.23s**; later focused format/check of the two changed files also passed.

### Artifacts and actual non-game proof

All paths below are under `E:/OOTRemake/work/r12-keys-cs12b/ingame/`.

- ONE real mod root: `mods/key-gate3-mixed-targets-next/`, containing exactly the
  same-named mod directory and no links. **28 resources**; no Forest Banc, saved
  defaults, new GameData fields, game folder or source backup was written.
- A launcher: **`Key gate 3A - Kokiri Forest and Deku Tree chests.bat`**.
  Separate user: `user-key-gate3-mixed-targets-next-part-a`.
  Original `2026-11-07_1630`, child slot04.
- B launcher: **`Key gate 3B - Goron City maze chest then Forest Temple door.bat`**.
  Separate user: `user-key-gate3-mixed-targets-next-part-b`.
  Original `2026-11-09_1022-main-adult-first/save/5a3c9e1f0b7d24680000000000000001`,
  adult manual slot01.
- Each launcher has its own adjacent **same-name `.md` checklist**, in plain player
  language. Both are the current central template with only name/source/slot/user
  suffix substitutions, ASCII/CRLF.
- `build_gate3.py`: PASS. All84 key/boss/map/compass fields exist in each source;
  required chest/door flags are explicitly closed, Forest/Fire counts0/0.
- Independent `verify_gate3.py`: **PASS**. Actual compressed bytes, every age Banc
  inverse, original event/entry/actor-operation prefixes, original registry rows and
  all old text/member bytes preserved. Nine matching new registry IDs; serialized
  sub-flow indices and cross-flow/child dependency closure; five actual source
  routes resolve the intended helper's literal target fields. Both named small/big
  destinations used per target. All16 languages receive only four English labels.
  Helper executed from written bytes for the actual mixed order and a nonzero
  standing-dungeon baseline; all14 groups match, including unchanged standing Deku.
- Exact complete resource-size table read-back passed:
  EventSetting509212→510688, allocation509480→510952;
  analyzed247276→248152, allocation247560→248424.
- Both **actual `CLAWSHOT_DRY_RUN=1` launcher runs exit0**: correct executable,
  separate users, same HOS_MODS. Each copied save tree matches its original backup
  SHA256 map; no game log or game process was started.
- Proofs outside the repository: `gate3-build.json`, `gate3-verification.json`.
  `check_gate3_save.py A|B <snapshot/slot_NN/progress.sav>` is a read-only all14
  oracle, deriving exact grants/spend from these chest/door flags; both copied
  untouched baselines pass. It has not checked played Gate3 saves yet.

The verifier initially mistook two small-chest presentation queries for additional
payout queries. Printed graph values showed those were in `Dm_SY_TreasureboxSmall`,
not `GetPouchContent`; scoping to the payout flow fixed the verifier. No mod byte
or production code was changed to satisfy that assertion.

### A: mixed targets, both sizes, reverse order and reload

1. **Walk from autosave04's starting position to Mido's house; NO Kokiri Forest
   Teleport first.** Same far-right small chest: Forest key.
2. **Deku big map chest**: Fire key. Save and Quit/Continue; verify the Deku chest
   stays open. **Do not return to Mido's house:** Claude checks its persistence in
   the automatic snapshots. These two route corrections are Claude's, from Gate1's
   played Saria-farewell/Mido/Kokiri blockage; no reconfirmation run is needed.
3. Normal wooden-shield setup if needed: unchanged shopkeeper gift after talking
   to the Deku Tree. Source shield IsGet=false/stock0; no inventory is edited.
4. Unchanged **big Slingshot chest**821372075822700622: normal Slingshot, equip/fire it.
5. **Slingshot-room small side chest**13027331340815880287: Fire key.
6. Normal upper-floor route with Slingshot; **big compass chest**
   9284193025315608699: Forest key. Save and Quit/Continue; check persistence and
   Slingshot use again. Quit before B.

Thus small chests give Forest→Fire and big chests Fire→Forest, with a reload between
pairs, without resetting either fresh copy. Named main/caption must match the target
each time. No map/compass grant, no new item from revisiting opened chests.

| A stage | Forest remaining/total/once | Fire remaining/total/once |
|---|---|---|
| Source |0/0/false|0/0/false|
| Mido small |1/1/true|0/0/false|
| Map big + first reload |1/1/true|1/1/true|
| Native Slingshot |1/1/true|1/1/true|
| Side small |1/1/true|2/2/true|
| Compass big + second reload |2/2/true|2/2/true|

Every other field in all14 groups equals its source, including Deku counts/first,
map and compass. The usual standing-area counter need not rise. Preserved old
item-specific Navi comments remain a known cosmetic issue in this frozen gate;
record separately from the key's actual acquisition main/caption. Production
named-key follow-up correction remains required; ordinary seed behavior is not
changed by this track.

### B: routed grant, reload, exact door spend, native control

1. Existing played Goron City top-floor west boulder-maze center pocket route:
   chest1176975953041865014 gives the named Forest key. Save/reload, check it stays open.
2. Existing played Forest entrance courtyard door1163369963105284964:
   spend that key **before** taking the tree chest. Save/reload, check door persists.
3. Existing east-vines/high-branches tree chest1171460703078800858:
   unchanged native Forest key and generic message. Save/reload, check both chests
   and door remain open. No Hookshot, no room Teleport, no second spend.

| B stage | Forest remaining/total/once |
|---|---|
| Source |0/0/false|
| Goron grant + reload |1/1/true|
| Entrance lock + reload |0/1/true|
| Native tree key + reload |1/2/true|

All other all14 fields equal the adult source. Untouched tree key and physical lock
are controls; their Banc was not emitted, and their original flow nodes remain unchanged.

**Before handover:** post this artifact/checklist pair to `cs-r12`; Claude can use
the read-only oracle or his existing snapshot checkers. Stop on failed opening,
wrong named acquisition text, wrong saved target/delta or persistence failure.
No game startup, message rendering, navigation or door behavior is claimed from
read-back. Runtime load log plus Kareem's results remain required for Gate3.
Gate4 is not built and anywhere player refusal remains enabled.

Claude subsequently boot-checked Gate3 headless (`kg3`), Hookshot2.1.0:
**526 log lines, no crash, save reached,28 files indexed/38 entries**, then handed
both parts to Kareem. Accepted report, not rerun here. Automatic snapshots cover
both parts. The adjacent part-A `.md` now incorporates his two route corrections
above; mod bytes, launchers, source copies and part-B route remain unchanged.

### Repository gate snapshot and queue

The serialized full runner obtained the lock at13:21 after waiting:
format **PASS**, lint **PASS**, synthetic **1011 passed/130 skipped** in1231.46s.
This began before the13:37 bootstrap fix, so it is **not** claimed as full-suite
coverage of that later fix (focused9 tests and actual Gate3 smokes cover it).
The dump suite began13:41 and the harness's3600s overall deadline killed the
runner during `test_pack_nup_dump`; no assertion failure was printed. This is an
**interrupted run, not PASS**. Process census showed no surviving test child;
only this runner's stale lock was removed, and the interruption/queue was posted.
Logs: `full-format.log`, `full-lint.log`, `full-synthetic.log`, `full-dump.log`.
Latest full gates/dump are deferred until Claude's explicit review-pr3 completion,
not silently retried or allowed to leapfrog his queued review.


## Production named-key Navi correction (Gate3 artifacts remain frozen)

Claude requested this after Gate2c's misleading map comment. cs12b proposes the
narrow correction: splice only audited item-acquisition balloon actions out of
**named-key wrapper clones**, continuing at their original successor. Preserve
all before/after story writes, independent story reactions, cameras, participation,
cleanup and every original entry/action. Ordinary seeds and all staged Gate1–3
mods/users/launchers are unchanged; this will need presentation-gameplay evidence.

### Native audit and ordinary-seed exposure

`audit_named_key_navi.py`:33 supported source families,16 native flowcharts,
12 reachable `Npc_Navi.EventNaviRequestBallonMessage` sites. Do **not** delete all
balloons: Nabooru's reaction is story-dependent, not reward-dependent.

The global `BalloonMessageParamList` is a512-field Hash32Map, not an ordinal
array. Its sorted order is **not** the action's Index. To resolve rather than
guess: `resolve_navi_reflection.py` found one contiguous512-u32 field-key table in
the installed read-only `image.bin`, offset66097232, stride4, with exactly the
global map's complete unique key set. Slot354 resolves the played map comment;
slot345 resolves the compass parameter. All12 indices were then resolved through
`Pack/NaviBallonMess.pack.zs`, parent/item metadata and the game's USen message
labels. No native data/text/table is copied into this repository.

| Index | Acquisition classification |
|---|---|
|228|Hover Boots|
|345|Deku compass|
|354|Deku map|
|361|Forest boss key|
|474|Slingshot|
|475|Boomerang|
|476|Bow|
|478|Ice Arrows|
|479|Hammer|
|480|Long Hookshot|
|495|Bomb Bag|

Index197 is the **independent Nabooru capture reaction** and remains. The curated
11-index set in the compiler identifies existing supported-build API values, not
an invented query or new saved state. No English game messages ship in that set.

Ordinary-plan finding: both Deku map/compass overrides are `keep`, their original
NaviChat wrappers request354/345 after the big-chest child returns, and their
balloon parameter ConditionList is empty. Ordinary item replacements therefore
retain the same item-related follow-up mechanism; the map case is already played.
The33-source audit found no corresponding balloon call in the other map/compass
source families within these16 graphs. That is not a claim about unrelated ambient
Navi hints. No ordinary-source flow or event policy is changed here.

External evidence: `named-key-navi-audit.json`, `navi-reflection-map.json`,
`navi-followups-decoded.json`; the latter native decoded material stays **outside**
the repository. A failed enum-name/hash-spelling probe was removed after the
complete native reflection table supplied the actual mapping.

### Cause-directed verification

- Synthetic serialized consumer before fix: **1 failed/9 deselected**, exact
  payload `[354,197] != [197]`, reproducing the false item comment while retaining
  the separate story reaction.
- After splice: focused `tests/test_key_bindings.py` **10 passed in0.20s**.
  The regression also proves story writes before/after the omitted node persist,
  the correct named grant/message remains, and the untouched original source
  still requests both comments when used normally.
- Focused format/check of `keys.py` and that test file: **PASS**.
- `smoke_navi_wrappers.py`: actual native33-source compiler and common writer,
  **35 resources** in a non-game emission probe, not an `ingame` mod or Gate4.
  Read-back of all appended actions retains exactly the Nabooru197 balloon, no
  old-item balloon. All original flow prefixes invert exactly, source-request
  reversal is byte-identical and every emitted allocation is exact.
  Frozen Gate3's entire resource SHA256 map matches before/after.
  Proof: `navi-wrapper-emission-proof.json`.
- No game was started, no global gate lock taken and no latest full-suite/dump
  pass is claimed. Player refusal stays enabled. Kareem's Gate3 uses the frozen,
  already handed-over bytes, not this source-only correction.


## Gate 3 played progress and same-copy continuation

Accepted Claude/Kareem report, **14:25–14:46**; no game reconfirmation run.

**Part B PASSED.** Goron center chest gave Small Key (Forest Temple); the entrance
door opened with that key; the unchanged tree chest gave its normal key. Kareem
also reloaded and took the tree key before opening the door: standing counter1→2.
Claude's watcher missed the switch to B, so these are the preserved **part-b user's
actual slots, not live snapshots**:

- slot05/00: Goron open, Forest1/1; match.
- slot01/02: door open, one spent; match.
- slot04: tree open after the door; match.
- slot03: tree-first reload, Goron and tree open, door closed, Forest2/2; correct.

The last state exposed only an overstrict assertion in this track's external save
oracle, not a game fault. Removed collection-order assertions: saved flags describe
current grants/spend, not their timeline. The invariant is total=opened routed
chest+opened native tree chest; remaining=total−opened entrance lock, with other
all14 fields compared against source. After that fix, actual slot03 **PASS**,
all14 match, Forest2/2/true, door false, no mismatches. No game or source save changed.

**Part A steps1–3 PASSED.** Mido→Forest, Deku map→Fire; all14 match in automatic
snapshots `save-backups/2026-11-11_14*-r12-keygate3a-1..8`. One Continue loaded an
earlier autosave; counts always match the opened chests, no duplicate credit.

**Part A steps4–8 blocked on equipment, not key routing.** This copy has no Kokiri
Sword; Kareem could not pass the Slingshot-room Scrub with the Deku Shield alone.
The earlier shield-only checklist was insufficient. No world-logic change is made
in this track from that observation.

### Superseded 3A2 proposal: CANCELLED before staging

Claude first proposed a fresh `-part-a2` user and Sword-first launcher, then
explicitly cancelled it: Kareem reports the Kokiri Sword chest **already open in
every copy, with no sword available there**. Accepted as ground truth; no attempt
to prove it closed or to replace the save. No 3A2 mod, launcher or profile was
created. Only read-only rule/route research had begun. No new checkpoint is needed.

### Superseded Sticks plan: same-copy continuation

Claude proposed the following plan, then reported the Sticks route unreachable.
It is retained as history, not a current instruction to retry the detour:

1. Continue **`user-key-gate3-mixed-targets-next-part-a`** at its existing state:
   Mido Forest key, Deku map Fire key, Deku Shield already owned. Do not repeat
   steps1–3 or reset/replace the profile.
2. Buy **Deku Sticks at the Kokiri shop where Kareem got the shield**. No new gift
   or shield acquisition is needed. If rupees are needed, open the still-closed
   **untouched Mido chest beside the key-test chest** for its normal rupees; this is
   an additional small non-key control. The latest plan permits that rupee visit,
   superseding the earlier blanket no-return instruction. Do not Teleport to Kokiri
   Forest or reopen the key-test chest.
3. Teleport to **the Deku Tree entrance**, use Shield plus Sticks to get past the
   Scrub, then take the unchanged Slingshot and verify use; side small chest→Fire,
   compass big chest→Forest; Save/Quit/Continue and check persistence as before.
4. Claude starts a fresh automatic watcher on **part-a**. No manual copying, new
   mod, launcher, user, altered inventory, source save write or game start by this
   track. Existing frozen Gate3 bytes remain in use.

Rupees/Stick purchase/Slingshot must not change any dungeon's key/map/compass/boss
fields. Remaining A expectations are unchanged: side small takes Fire1/1→2/2,
compass big takes Forest1/1→2/2; all other all14 fields equal source. Actual Sticks
passage and the remaining pickups/reload are still **pending**, not inferred PASS.
Gate4 remains blocked; full gates still respect the review-pr3 queue.


## Gate 3 A continuation: received items, equipment deviation, compass still pending

Accepted Claude/Kareem report, **14:53–15:06**, without rerunning the game or save
audit to confirm it:

- Unchanged Slingshot chest gave the Slingshot.
- Slingshot-room side chest gave the Fire key: **Fire2/2, Forest1/1, all14 match**.
  No crash. This proves the additional small-source Fire attribution and saved
  non-key reward; actual Slingshot firing is not separately reported here.
- **Compass chest was not opened in any save.** Last save15:06:17 was immediately
  after the side chest; normal game quit15:06:34. Claude is asking Kareem about the
  missing step. Do not infer the compass grant or final reload/persistence PASS.
- **Deviation:** the Sticks route was not reachable. Kareem gave this same copy the
  Kokiri Sword through the cheat menu to pass the Scrub, contrary to the checklist's
  Teleport/clock-only limit. Record the actual equipment modification; neither a
  Sword-free/Sticks route nor unassisted progression is certified by this run.
  All14 dungeon-field comparisons do not establish unchanged non-dungeon inventory.
  The agent did not grant/equip anything or alter any save.

Part B remains PASSED. Part A now has Mido Forest, big-map Fire, native Slingshot
and small-side Fire evidence. Big-compass Forest and the final reload check remain
pending; **Gate3 is not yet complete and Gate4 is not built**. The part-A adjacent
checklist now distinguishes saved pickups, the recorded equipment exception and
the remaining compass step. Same frozen mod and existing user; no new launcher.

### Future-launcher rule: current single-save template, thumbnail identification

Claude traced repeated old-Continue loads to the backup containing six saves and
the UI identifying them by thumbnail rather than internal slot names. He revised
`E:/OOTRemake/tools/test-launcher-template.bat` and reported its dry run checked.
Read the revised template here; its first-copy branch now copies only:

- `account.sav`;
- `option.sav`;
- the selected internal `SLOT` directory.

For **every future launcher**, copy that central template anew, never an existing
gate launcher. Keep the slot only as internal copy configuration. Player checklists
must identify the save **by place and what its actual thumbnail shows, never a slot
number**; inspect the chosen source thumbnail before writing that description.
Do not invent its image from a filename or room assumption.

Future dry-run verification must compare the copied UID tree against exactly that
three-part source subset, not the old six-save whole-tree hash map. Check no other
slot directories were copied, with no game started by this track.
Existing played Gate1–3 launchers/profiles and their historical verification reports
remain unchanged; no retroactive resetting/pruning of Kareem's current copy. This
is a forward rule, not permission to overwrite old evidence.


## Gate 3 COMPLETE — PASSED (Claude/Kareem final acceptance)

Claude reports Kareem opened the Deku compass chest: **“Forest Temple key.”**
Final part-A saves, copied to
`save-backups/2026-11-11_gate3a-final`:15:13:31 and15:13:35 (internal slots05/01).
Mido, map, Slingshot-room side and compass chests are open; the unchanged Slingshot
chest is open. **Forest2/2/true and Fire2/2/true, all14 match, no crash.**
Small-source order Forest→Fire and big-source order Fire→Forest were both played.
Part B already played the routed spend plus native key in both orders. Accepted
as complete by Claude; no unchanged rerun of the game or his save audits.

The documented Sword-cheat deviation is retained: Gate3 certifies the played key
attribution/spend/persistence/order controls, not a no-cheat opening route from the
old child checkpoint. It does not authorize more inventory cheats in Gate4.

Next requested gate is **presentation/release on a real generated anywhere seed**,
not manually chosen placements: short multi-target route, long-name layout and
item-bar/caption inside another dungeon. Tracker/save-roster reads come later.
This track will propose exact seed/settings/placements/checkpoints and post before
building. **Player refusal stays until Gate4 passes.** No Gate4 mod or launcher has
been built; single-candidate placement inspection writes only research evidence.


## Gate 4 proposal — real generated seed7, not built

**Proposed by cs12b for Claude/Kareem review before construction.** One full generated
mod, two fresh copies of existing normal-play adult checkpoints, four pickups.
Part B alone crosses **Shadow→Forest→Gerudo Proving Grounds**; part A compares the
same long-name target in an overworld small chest against B's dungeon big chest.
No new checkpoint, child equipment bootstrap, inventory cheat or room Teleport.

### Real seed and unchanged release boundary

- **Seed7**, full world, **Chest-only** shuffle, `dungeon_items=anywhere`; other
  settings stay default: forest closed, Door of Time closed, intro skip, vanilla
  prices/cheap Deku Shield, songs at song checks, always/balanced hints.
- Actual `generate` with census-linked **remake-native pool**, not N64 vanilla,
  produced **165 shuffled locations,37 small keys,23 beatability spheres**. Normal
  fill and `check_beatable` ran; placements were not selected or edited by hand.
  Shuffled boss keys/maps/compasses were checked to stay in their logical dungeon.
- Exact settings/CS1 and all placements:
  `work/r12-keys-cs12b/gate4-seed7-inspection.json`.
  Canonical placements SHA256:
  `836c76e51cdb61338917ecf7886b5bc1693d4acc879e16f9c884eba163dc91de`.
- Seed12 was also inspected as a single candidate but not selected: its long-name
  sources complicated this short checkpoint route. Neither candidate wrote any mod,
  transformed resource, launcher or user directory.
- Proposed acceptance-only harness: call real `generate`/native-pool resolution,
  the existing normal patch-step functions (`make_plan`, hints/shops/door/fast-start
  steps, then source-bound `keys.changes` composition), and `SeedOutput`/`write_seed`.
  Emit the **whole generated seed**, including normal spoiler/CS1/play note, not a
  four-chest excerpt. Check emitted spoiler placements against the digest above.
  No monkeypatch/no-op guard, hand-authored `Seed.placements`, manual wrapper binding,
  new public bypass setting or guard removal. Public CLI/`make_seed` keep refusing.
  This is use of existing lower-level generation/emission APIs for the authorized
  acceptance experiment, not a claim the guarded convenience entry accepts it.
- Use current production source (including the audited Navi correction5cf92e5).
  Version/uv.lock unchanged. Tracker reads explicitly come later.

### Exact generated pickups

Names below are generator identities for review; player checklists will use the
plain physical directions and the game's English target names.

| Part/order | Actual generated location | Hash | Size | Key shown |
|---|---|---|---|---|
|A1|Sacred Forest Meadow Chest (Item_ScrubBusinessSeed)|1764383515296652106|Small|Gerudo Proving Grounds|
|B1|GC Maze Left Chest|4402942101476009858|Small|Shadow Temple|
|B2|ZR Open Grotto Chest|8838426083116998768|Small|Forest Temple|
|B3|Ice Cavern Compass Chest|13542013937093159888|Big|Gerudo Proving Grounds|

These exact four rewards came from the real fill. The Gerudo logical key is
`Small Key (Gerudo Training Ground)`; USen's actual location name is **Gerudo Proving
Grounds**,22 characters. Expected acquisition is **Small Key (Gerudo Proving
Grounds)**,34 characters; caption's target row **Dungeon: Gerudo Proving Grounds**,
31 characters. Values are read from the dump at generation, not shipped as names.
The absolute longest native target name is Inside Ganondorf's Castle,25 characters;
this proposal does **not** claim that separate case was played. The chosen22-character
case is available both outside a dungeon and in a different dungeon without a deep
castle/proving-ground route or a forced placement.

### Existing saves and actual thumbnail descriptions

All sources remain read-only. Internal slot identifiers belong only in this
technical record/template configuration, never player save-selection instructions.

**A source:** `save-backups/2026-11-09_1022-main-adult-first/save/`
`5a3c9e1f0b7d24680000000000000001`, internal manual01.
Player description: **Temple of Time; adult Link beside Sheik on the round stone
pedestal in the sword chamber.** Its actual embedded JPEG was decoded/read at
`work/r12-keys-cs12b/gate4-source-adult.jpg`; no invented position.
Sword, Bombs, Ocarina of Time and Song of Time are explicitly owned; the meadow
chest is explicitly closed. Hookshot is not needed by its sourced route.

**B source:** `save-backups/2026-11-10_1402-main-fire-hammer/save/`
`5a3c9e1f0b7d24680000000000000001`, internal manual01.
Player description: **Fire Temple after getting the Hammer; adult Link seen from
behind with the blue/red Hylian Shield, facing the orange-brown rock wall, Navi
bright on his right.** Actual image:
`work/r12-keys-cs12b/gate4-source-hammer.jpg`; caption string metadata says
`FireTemple`/`FireTemple/FireTemple`.
Master Sword, Hammer, Bombs, bottle, Bow and Hookshot are explicitly owned, adult
state confirmed. Goron left, river grotto and Ice compass chests explicitly closed.
This avoids repeating Gate3's missing-weapon situation. Empty a normal bottle for
Blue Fire if needed; no item or age cheat.

All84 dungeon key/boss/map/compass fields exist in each source. Evidence:
`gate4-proposal-proof.json` and `verify_gate4_proposal.py` **PASS**. The initial
policy assertion incorrectly included an unshuffled SilverRupee puzzle, whose
“dungeon” names the puzzle rather than the containing temple; printed type and
shuffled-membership values showed the cause. Scoped that oracle to the165 shuffled
chests, then it passed; no production/placement change was made to get green.

### Proposed short route and reload points

**A — overworld long-name window**

1. Load the Temple of Time/Sheik thumbnail above. Teleport to Sacred Forest Meadow
   entrance. Follow the normal adult route to the side clearing behind the Song
   of Time blocks; use Bombs/Song of Time as its access requires. Open the former
   Business Scrub Seed small chest, not another chest.
2. Capture exact acquisition **and** caption, readable line wrapping, normal key
   model and cleanup. Save/Quit/Continue, choose the newest picture from this test,
   check the chest stays open, then quit before B.

Sourced access: `remake/extra_sacred_forest_meadow.toml` requires adult, explosives
and Song of Time; r4-logic-child.md describes this clearing. Those abilities were
checked against the actual source, not assumed from a filename.

**B — three targets, then the same long name inside Ice Cavern**

1. Load the Fire Temple/Hylian Shield thumbnail above. Teleport to Goron City.
   Follow the top-floor west maze, use the Hammer on its dark hammer-breakable rocks,
   open the **left/red-rupee chest**, not Gate3's center pocket and not the silver-
   gauntlet purple chest. Expect Shadow Temple.
2. Teleport to Zora's River, take the normal raised-ledge **open-hole grotto** with
   the chest/gossip stone/shallow pool; not the Song of Storms grotto. Open its small
   chest: Forest Temple. Save/Quit/Continue; confirm both rewards persisted, no repeat.
3. Teleport to Zora's Fountain, use the normal adult ice-floe entrance to Ice Cavern.
   Clear the ordinary entrance/Freezard/scythe route; collect the required silver
   rupees, bottle Blue Fire, melt the route to the compass room. Do not take the map
   or Iron Boots chest. Open the **big compass chest**: Gerudo Proving Grounds.
4. Capture both target-labelled messages and the floating pickup notice **while
   still inside Ice Cavern**; report on-screen and pause-map numbers or their
   absence. Save/Quit/Continue and confirm this chest and the prior two stay open.

Route sources: r4-logic-child.md Goron maze (left requires Hammer or Silver
Gauntlets); Zora River open grotto is uncovered and its chest item-free (Hash above);
Ice Cavern's normal Blue Fire/compass route. The supplied late source has the
weapons/bottle even for the previously noted optional ice-pillar/arrow-route doubts.
Only entrance Teleports/clock; if blocked, stop and report instead of granting gear.
Ice Cavern is a **different, keyless dungeon**, not the key's target; that distinction
is deliberate, not a claim this route enters the Proving Grounds.

### Expected saved changes and presentation acceptance

Profiles are separate: never add A's count to B's. Compare every stage against
that profile's84-field baseline.

| Profile/stage | Intended remaining/total/once |
|---|---|
|A meadow|Gerudo0/0/false→1/1/true|
|B Goron left|Shadow0/0/false→1/1/true|
|B river grotto|Forest0/5/true→1/6/true|
|B Ice compass|Gerudo0/0/false→1/1/true|

The old normal-play saves are **presentation checkpoints, not a new-seed
playthrough**; B already acquired/spent Forest keys before this experiment.
Do not reset/rewrite that history or pretend total6 came from six pickups in this
route. Real generation's beatability search is separate from this checkpoint test.
All unlisted all14 fields stay baseline, especially standing Ice key/map/compass
fields. No double/standing/pouch credit or new compass grant.

Both acquisition and caption must name the actual target, with no “this area”
wording, clipped/overlapping/unreadable long text or extra generic dialog; normal
model, close, movement and persistence. Record any item-specific Navi comment
separately and fail a misleading old-item claim on a named-key path.
The inspected floating notice is icon/count-only: **do not promise a target-name
pane or inject the remote count into it**. Record its actual count/absence separately
from the named window and pause/on-screen standing counters. No roster/HUD hook.

### Construction only after this proposal is reviewed

Proposed real mod root: `key-gate4-generated-seed7-next`; fresh profile suffixes A/B.
Proposed launcher names:
**Key gate 4A - Sacred Forest Meadow long key.bat**;
**Key gate 4B - Goron City, Zoras River, then Ice Cavern.bat**.
Copy the current central template separately for each; only account/options and the
chosen internal save directory. Dry-run subset hashes are already recorded in the
proposal proof. Real folders, exactly one mod, ASCII/CRLF; no old user reuse.
Switch the automatic watcher explicitly before B so its saves are not missed.

Before handover: whole-seed read-back/inverses, registrations/dependency closure,
allocations, all16 message pairs and exact placement digest; deterministic repeated
output; actual template dry runs/exact four-file UID subsets/no links/source hashes.
Claude boot-checks and hands it to Kareem. Public refusal remains; no game start here.
Latest full repository gates still wait for the review-pr3 queue release; this
proposal is not a claim they passed or that release is ready.

**Claude/Kareem: approve this two-checkpoint seed7 route and the22-character
Gerudo Proving Grounds long-name case before I build?** No mod/launcher/profile has
been constructed. If the absolute25-character castle name is required instead,
say so rather than silently treating this as proof of that different case.

## Rebase onto merged main cd81449

Claude reported review-pr3 gates complete/PR3 merged and released the normal
shared-lock queue. Rebased all16 `r12/keys` commits onto main **cd81449** without
conflicts; rebased tip **f26071b**. No version/uv.lock change.

Post-rebase actual CLI smoke, explicit anywhere+Chest/Gift and encoded-CS1 replay:
both **exit1**, ordered in-game acceptance refusal, **no output directory**.
The public boundary survives integration. No Gate4 construction was performed.

Latest four-command gates started with `CLAWSHOT_WORKERS=1`, cooperative
`gate.lock` held across the entire sequence and waiting if another track owns it.
Evidence directory: `work/r12-keys-cs12b/rebased-cd81449/`; earlier interrupted
logs are preserved. No overall runner deadline, correcting the previous harness's
3600-second interruption rather than blindly repeating that configuration.
Full-suite/dump outcome is still **pending**, not inferred from the rebase/smoke.

### Post-rebase gates: initial outcome and input correction

The runner waited for the shared lock until17:35, then released it18:29:

- Format **PASS**, lint **PASS**.
- Synthetic **1020 passed/130 skipped**,1178.22s.
- Dump **112 passed/1022 deselected/16 setup errors**,2082.16s; **not PASS**.
  All16 errors were the `OOT_DUMP` parameter of `test_pack_nup_dump.py`'s shared
  cache fixture; the NUP counterpart and remaining dump tests passed.

Cause printed before any rerun: this runner inherited
`OOT_DUMP=work/pr1-check/dump`, a legacy layered real-resource fixture with1243
indexed files. Current `working_files(...)` minus that index is exactly
`RSDB/GameAnalyzedEventInfo.Product.111.rstbl.byml.zs`; full supported romfs has it.
The version digest check had passed, but that does not prove a working set complete.
This is stale **runner input**, not a reason to weaken the cache loader/tests.

Cause-directed recovery started: verify every indexed legacy file against the
independent full-romfs bytes, copy the fixture into private cs12b scratch, add the
missing **unmodified** resource to that copy's131072 update layer, and rerun the
**entire dump suite** with romfs/NUP/refreshed layered inputs under the same
one-worker/shared-lock/no-deadline policy. No original fixture/dump, production or
test is edited. The private copy is a real-resource working-set fixture, not a
claim to have produced a new complete game dump.

Initial logs/results are preserved in `rebased-cd81449/`; recovery input proof,
log and result go in its `dump-recovery/` subdirectory. Recovery outcome is
**pending**, not inferred PASS. Latest source remains rebased onto cd81449;
no Gate4 build or player-refusal change.

### Final post-rebase gates — all PASS

Supersedes the pending recovery status above. The full cause-directed dump rerun
finished19:33; its cooperative lock was released normally.

| Gate | Latest result |
|---|---|
|`uv run ruff format --check`|PASS|
|`uv run ruff check`|PASS|
|`uv run pytest`|1020 passed/130 skipped,1178.22s|
|`uv run pytest -m dump` with romfs/NUP/refreshed layered input|128 passed/1022 deselected,3651.81s|

All ran with one worker after the conflict-free rebase onto **cd81449**. No tested
production/test source changed between these results; intervening commits only
recorded evidence in this round file. Both post-rebase real CLI refusal smokes
also passed, with no output directory.

Recovery preflight proved **all1243 indexed legacy resources byte-identical** to
the full-romfs oracle. The private1244th file was unmodified analyzed-event data,
SHA256 `40f61c00c80e141ff2a7c766097f906e5e675043168f99e0f9c7989469657e80`.
All original dump/fixture files stayed untouched. No loader fallback, disabled
case, test change or production fix was used to turn the stale input green.
The initial112-pass/16-setup-error log remains preserved, not relabelled PASS.

Retained text logs/results/input proof under `rebased-cd81449/` and
`dump-recovery/`. Removed only this run's owned synthetic/dump/recovery temporary
trees and private layered fixture; verified all four paths absent. Original
`pr1-check/dump`, full romfs, NUP and prior gate evidence were not removed.

**Remaining:** Gate4's posted seed7/two-checkpoint/22-character long-name proposal
still needs Claude/Kareem review before construction. Gate3 remains accepted PASS;
Gate4 is unbuilt, Tracker later, player refusal retained. No version/uv.lock change,
game launch, merge or push.

## Gate 4 approved and built — real whole seed7

Claude approved the proposal **as written**, including the22-character long-name
case and two existing checkpoints. Conditions: current single-slot template;
honest checklist estimates/explicit B2 stop-and-report option; emitted placement
digest and both public refusals checked; no full run/lock use while review-012
owns it. Build on the current **a2c0c8e** source; rebase only **after** main moves
to0.1.2, not during this build. No version/uv.lock changes.

`work/r12-keys-cs12b/build_gate4.py` calls real `generate` with native census pool,
normal cheap-shield/door/hints/Sheik/intro patch functions, source-bound
`keys.changes(prior_changes=...)`, then `SeedOutput`/`write_seed`. No entry-point
guard replacement or hand-authored placements. Whole seed:165 shuffled checks,
37 small keys,23 beatability spheres;155 changed physical chests,34 named off-
dungeon bindings across all8 targets. **91 resources plus normal spoiler/play note**
were emitted to the approved single-mod root.

### Exact placement proof and harness correction

Full real generation remains **1331 placements**, canonical SHA256
`836c76e51cdb61338917ecf7886b5bc1693d4acc879e16f9c884eba163dc91de`.
Normal `generate.spoiler` intentionally serializes only the **165 shuffled**
placements; their canonical SHA256 is
`207c42dbf0733d81888f11542793c50667135115b4408619c05250ddfe4b1894`.
All emitted entries equal the approved candidate's complete shuffled projection.
Combining them with independently generated fixed placements recovers the full
approved digest. This distinction does not change the seed or narrow its emission.

The first normal write succeeded, then my harness incorrectly compared that165-
entry spoiler mapping directly to the1331-entry model. Printed counts/digests
showed the exact cause. Preserved that first emission outside the mod root,
corrected only the harness's scope assertion, then one corrected build passed.
The corrected builder independently regenerated and wrote the **entire seed**
again to a non-mod scratch root: all93 files (including spoiler/play note) are
byte-identical. Source resource/save hashes remain unchanged.

Read-only `check_gate4_save.py A|B <progress.sav>` compares all84 fields against
that profile's baseline and the actual opened planned chests, not collection
order. It reports partial-route inventory matches separately from route completion
(B2 stopping is not Gate4 completion). Actual source A/B smoke: all14 match, no
changes, every planned chest closed, route incomplete as expected.

Native load, rendered layout, pickup bar/caption behavior and route/reload results
remain **unplayed** here. Public refusal remains until the played acceptance;
Tracker follows later. Final read-back/launcher proof and handoff are recorded below.

### Staged player artifacts

Root: `work/r12-keys-cs12b/ingame/`. Each launcher has the same-stem `.md`.

| Part | Launcher | Honest estimate at checklist top |
|---|---|---|
|A|`Key gate 4A - Sacred Forest Meadow long key.bat`|15–25 minutes|
|B|`Key gate 4B - Goron City, Zoras River, then Ice Cavern.bat`|60–90 minutes, longer if navigating; B1–B2 about20–30|

Both independently copied the **current** central template, SHA256
`80795106951ff85cbb9b48251328eb28a4c728dba1f72120ccde5579dab1fc9b`.
Only NAME/ROUND/SAVES/T substitutions; both use the source's internal manual01.
Player selection is **Temple of Time/Sheik pedestal** for A, **Fire Temple/Link's
Hylian Shield/orange-brown wall/Navi right** for B, never a slot number.
The fresh users are `user-key-gate4-generated-seed7-next-part-a` and `-part-b`.
Watcher confirmation is explicit before playing **each** copy.

B's first paragraph expressly permits **Save/Quit after B2 and partial report** if
short of time; B3's silver-rupee/Blue Fire navigation is not presented as a quick
detour. Reload/finish from the newest actual picture later. No Gate4 completion
claim from B1–B2 alone. Neither checklist promises an unplayed shortcut.

Physical directions use the existing Banc-backed `location_names.toml` entries:
SFM Gossip Stone clearing1275–1279; Goron south-west dark-rock pocket809–811;
river hole relative to first bridge/fairy hole1640–1644; Ice east room/Blue Fire
font/wall Skulltula962–967. Both messages, long-name readability, floating notice
and standing HUD/pause-map counters are separate observations, with no remote
HUD/name-pane promise. No inventory/age/door/room cheats; no off-route chests/key spend.

### Runtime proof still to collect

Claude boot-checks before handing these to Kareem. Require actual
`mods: <file> <- <path>` lines from this mod for both common chest flows,
`GetPouchContent`, active-language Mals, both registration tables and the reached
adult placement files: SFM/Goron City/Zora River `*_Adult_Dynamic` and Ice Cavern
`IceCavern_Static`. File counts alone are not proof of the particular route file.
Do not fabricate these lines from read-back: no game has been started here.

Kareem's exact acquisition/caption/bar/HUD observations and saved all14 deltas,
followed by chest-open/reload/no-repeat results, remain required. Partial B2 is
valid progress, not a passed Gate4. Preserve these staged bytes across later
source rebases; their provenance remains the approved a2c0c8e experiment.

### Gate 4 file verification and launcher dry runs — PASS

Actual `uv run python -u work/r12-keys-cs12b/verify_gate4.py` completed in25.10s:
**165 placements,34 named keys,30 registrations,8 targets; A1+B3 traces all84;
refusals×3; two dry runs PASS**.91 romfs resources/93 seed files.

- Independent real regeneration matches the full approved digest and complete
  emitted shuffled projection; full spoiler/play note byte-equal to normal builders.
- Every changed/unchanged chest and every changed Banc copy checked; exact inverses.
  Eight key-touched flows append to their **pre-key normal-patch baseline**, preserving
  hint/Sheik/cheap-shield/intro composition. All30 additions match between registry
  tables, are String64-safe and reachable; actual subflow/child closure checked.
- All34 serialized routes: correct target arguments, native source bootstrap,
  target message/caption labels, no generic/pouch/standing dungeon credit or
  item-specific Navi follow-up. Exact four-node helper; A/B stages match all84
  expected fields, including B's Forest total5→6 and unchanged Ice fields.
- All16 language archives contain exactly the16 added English labels (8 pairs),
  with inverse to the composed prior text; entire resource size table, actor-member
  growth, compression and fast-start bytes checked.97 verifier-read dump files and
  the builder's broader input hash set unchanged.
- **Actual public CLI explicit anywhere and CS1:** exit1/in-game acceptance refusal,
  no output. **Actual `make_seed`:** same `PatchError`, no output. Nothing released.
- **Actual .bat dry runs:** both exit0/exact expected command, ASCII/CRLF and exact
  current-template substitution. Each fresh UID has **only four files**: account,
  options, chosen caption and progress. No other slot/reparse/game log; source
  backups unchanged. `HOS_FS_OVERLAY` cleared, HOS_MODS holds exactly this one real mod.

One verifier bookkeeping defect was diagnosed, not worked around in the mod:
it discarded each owned helper index before later collecting that appended node,
then called all8 grants orphans. Printed switches122→132,224→234,… showed the
forward-reference order. Compare complete declared/claimed sets after traversal
instead; all exact grant-edge/type/argument checks remain. One cause-directed
rerun passed; no artifact or production/test edit.

Evidence outside repo: `gate4-build.json`, `gate4-verification.json`,
`gate4-launcher-manifest.json`, `check_gate4_save.py`, and both source thumbnail
images. Removed only owned duplicate first/repeat emissions after byte-equality
proof; reports retain their hashes. **Kept the staged mod and both fresh test
profiles.** The once-only verifier requires fresh users/repeat scratch; never
delete played copies or rerun it over a played handoff.

**Ready for Claude's boot check and handover, not claimed passed in game.**
Use the two same-stem checklists above; confirm watcher A, switch explicitly to B,
and allow the B2 partial stop. No game start, full suite, gate.lock acquisition,
rebase, version change, merge or push during this approved build. Rebase onto0.1.2
only when Claude reports that integration; these staged bytes stay frozen.

### Claude's Gate 4 boot check accepted; part A handed over

Claude reports **kg4 boot OK:508 log lines, rendering, no crash**. Accepted as
reported; not rerun here. This establishes boot/rendering, not the unplayed
acquisition/layout/bar/credit/persistence acceptance.

Claude is handing4A to Kareem with the automatic watcher **armed on part A**.
Part-A pickup/reload results remain pending; explicitly switch the watcher before
B, retaining its permitted B2 partial stop. Staged bytes/users remain untouched,
and the public refusal stays enabled.

Coordination correction reported by Claude: the cs-r12 watcher had been blind
after the thread exceeded50 posts because its `bermuda thread log` read retained
only the newest50. That delayed seeing the20:13 handover; **watcher fixed**.
This was a message-visibility failure, not a mod boot failure.

### Gate 4A played results — attribution/text/reload PASS; visual-age question open

Claude reports Kareem's21:16–21:20 run, snapshots
`save-backups/2026-11-11_21*-r12-keygate4a-1..7`; accepted as reported, not rerun.
Final saves: internal04 at21:19:22 and01 at21:19:58, both **adult**.
Only GerudoTrainingGround remaining0→1, total0→1, once false→true changed;
the other81 baseline fields stayed unchanged.

Reported screenshots/result:
- Acquisition **Small Key (Gerudo Proving Grounds)**: one line, fully readable.
- Caption **Opens one locked door.** / **Dungeon: Gerudo Proving Grounds**: readable.
- Normal key model; floating indicator appeared without increment, as specified.
- Chest stayed open after Save/Quit/Continue; no second reward.

Route deviation: SFM entrance Teleport landed at the **Forest Temple end**, not
the expected lower entrance. Sheik's Minuet scene played in this copy; Kareem then
took the adult route to the clearing. No seed/profile change is made here.

**Open — Claude is asking Kareem:** Link looks child-like in both pickup screenshots
(young face/Kokiri-style tunic), although every before/after save says adult.
Do not infer a saved age change or certify the player's model from those saves.
If confirmed, inspect the actual named-small-chest wrapper's get-item demo/actor
and whether that path selects a child-only model; do not patch speculatively.
The suggestion that gates1–3 were all child is inaccurate: **Gate3B used the adult-
first checkpoint and played a named small key**. Its visual age was not recorded,
so it is relevant prior exposure, not proof the appearance is correct.

Minuet button prompts reportedly showed **Xbox** icons despite the runtime's
resource-size-table/game-icons message. A separate ocarina-hint rendering path is
**an inference only**; no Clawshot cause or fix is established.

Part B is next; Claude reports its watcher **armed for the switch after A closes**.
Gate4 as a whole remains incomplete, the model question unresolved, public refusal
retained, all staged mod/save bytes untouched.

## Gate 4 COMPLETE — PASSED (Claude/Kareem acceptance)

Claude reports Kareem's~21:25–21:36 part B: `check_gate4_save.py B` on internal03,
21:35:51, **planned_route_complete=true, all14_match=true, no mismatch**, adult
throughout, no crash in the log.15 snapshots: `save-backups/*r12-keygate4b-*`.
Accepted as reported, not rerun:

- Goron maze **left**, river **open grotto**, Ice **compass** chests open.
- Shadow+1; Forest+1 with historical total5→6; Gerudo+1. Other fields match baseline.
- Grotto screenshot: **Small Key (Forest Temple)** and **Opens one locked door.** /
  **Dungeon: Forest Temple**. Ice screenshot: **Small Key (Gerudo Proving Grounds)**
  with both caption rows, readable, normal key model/chest.
- Kareem: Goron/grotto floating indicator appeared without increment, like4A.
  **Ice: no floating indicator appeared.** That absence is accepted, not a missing
  reward; the save proves target credit. “Only areas with small keys show the
  counter” remains an inference, not a reason to add a HUD hook.

Resolved by Kareem/Claude: the child-like appearance **is this game's adult model**;
adult throughout. No get-item age/model defect is established and no fix is needed.
Minuet's Xbox prompts occur **only in the ocarina interface**, a Hookshot path,
not this patch. The SFM Teleport/Minuet route deviation remains in the4A record.

**All four ordered played gates now accepted.** This is not automatic public
release: current public CLI/`make_seed` refusal and UI unavailability remain in
place. Claude requests a reviewed production plan below before any switch-on;
staged/played seed files and users remain frozen. Tracker reads remain later.

## Keysanity production plan — PROPOSAL ONLY; no switch-on approved

**Proposed by cs12b after Claude/Kareem accepted Gate4.** “Anywhere” here means
**small keys only**, not all dungeon items. Current CLI/API refusal and disabled
UI choice remain in force. Claude reviews this scope/cutover before implementation.

### 0. Integration prerequisite and current evidence

Main is now **22095a5 /0.1.2** (public+physical-area tracks integrated). Followed
the earlier rebase-after-integration instruction:23 commits replayed. Resolved
only `generate/fill.py` and `docs/settings.md` conflicts by combining both policies:
native physical-area safety **and** small-key-only named chest destinations.
All played Gate4 files/users stay frozen at their original a2c0c8e provenance.

Important merge detail: use `_in_dungeon_area(...)`, not the old logical-region
early return, to admit an ordinary dungeon item. Otherwise a Spirit hand bypasses
the new safety check. Only a supported small key may take the out-of-area chest
branch. Do not overwrite this with main's older unrestricted-anywhere predicate.

Incoming area tests assumed that synthetic anywhere also releases boss keys/maps/
compasses. The first focused run printed3 failing family assertions; retained all
families, corrected their contract, and added the real Spirit-hand anywhere
boundary to the existing test. Corrected run: **31 passed/1 skipped** across
`test_generate_dungeon_areas.py`, `test_key_model.py`, `test_keys.py`; one worker.
Named format/check of the two affected files PASS. The skipped test needs romfs;
**latest full gates and sweeps must be rerun after reviewed production edits**.

Actual post-rebase API smoke: both Spirit hands' own-dungeon generic families
are excluded; with anywhere only their small-key chest destination is admitted,
not boss/map/compass; inside-Temple destinations remain admitted. Actual UI schema
still marks anywhere disabled; schema validation and `make_seed` still refuse.
No public enabling change was made by the rebase.

### 1. Proposed release scope — preserve defaults and physical safety

- Keep `dungeon_items=own_dungeon` as default and keep current presets unchanged.
  Keep enum/CS1/CLI values `own_dungeon` and `anywhere`; no renamed setting or shim.
- Anywhere releases **SmallKey only**, through source-bound named grants when a
  chest's actual Banc is outside the target. All8 existing native target IDs; no
  raw-name fallback, new saved fields, global target latch or in-game roster.
- **BossKey/GanonBossKey, maps and compasses remain own-dungeon and physically
  collectable inside that dungeon**, in both modes. They get no portable grant.
  In particular the Colossus hands stay ineligible for generic Spirit rewards;
  an anywhere **named small key** may use those chests.
- “Chest destinations” does **not** mean globally requiring Chest-only shuffle.
  Preserve mixed Chest/Shop/Gift/Scrub and existing optional kinds/palettes:
  no off-dungeon keys on NPCs, shelves, scrubs or floors. Existing same-dungeon
  native paths/palettes stay as they are. Test the supported mixed combinations
  before release; do not advertise them on the strength of Chest-only Gate4.
  With no shuffled key/chest source, do not invent keys or change the pool.
- Preserve shared `allowed()` use in every fill/swap/age-return stage and hint
  restriction classification. Preserve native pool counts, stable actor Hashes,
  all age/file copies, story effects, bootstrap and dependency registrations.

### 2. UI option and help — one existing metadata contract

In `src/clawshot/app/settings.toml`, after review:
- Remove only `dungeon_items.unavailable.anywhere`; Token remains unavailable.
  `app/schema.py` then exposes/enforces the same enabled choice for UI/form/CS1.
  No separate JS whitelist, backend bypass or auto-reset of a chosen setting.
- Proposed label: **Small keys anywhere** (value remains `anywhere`).
  Keep **Own dungeon**; default/presets unchanged.
- Proposed field help: **Choose whether small keys stay in their dungeon or can
  appear in chests elsewhere. Boss Keys, maps and compasses stay in their own dungeon.**
- Proposed anywhere choice help: **Find small keys in shuffled chests, including
  other dungeons and the overworld. The pickup message and caption name the target
  dungeon in English. Boss Keys, maps and compasses do not leave their dungeon.**
- Keep the0.1.2 public track's corrected small-key-only wording, not this branch's
  obsolete pre-rebase “keys, maps and compasses anywhere” text. Add the same scope
  to `--dungeon-items` CLI help, whose current argument has no explanatory help.
- Browser smoke on the actual Settings/Generate surface: select/persist/import/
  export the choice, see help, build a real seed, inspect result; no Play/game start.
  Check actual unavailable-option/Token behavior still works. Do not test literal
  strings or mock forwarding instead of consumer behavior.

### 3. Refusal removal — reviewed clean cutover, not a no-op guard

First run LSP references for exported `patch.check_dungeon_items`. Then delete
the obsolete function, `patch.__all__` entry, CLI import/call and `make_seed` call;
migrate any other live references found. No always-return-success stub/alias,
research bypass flag or compatibility shim. Existing
`make_seed`→`keys.changes(prior_changes=...)`→`write_seed` is already wired:
use that normal public path, not the scratch Gate4 pipeline.

Keep all real restrictions/errors: Token refusal, palette and physical-area
checks, supported saved-field validation, unbound/stale event/unsupported-target
refusals, safe output paths, source read-only and per-seed beatability.
Change UI availability and backend permission in the **same reviewed cutover**.

Retire only now-obsolete anywhere-refusal assertions in `tests/test_keys.py`
and the disabled-option row in `tests/test_app.py`; preserve CS1 roundtrip/explicit
override tests and other invalid-option tests. Replace with real generation/
destination/credit/error behavior using existing synthetic fixtures where useful;
use native smoke instead of adding wiring/mock-echo tests. Keep key model/binding/
text and physical-area regressions, including nonportable boss/map/compass families.

### 4. Docs, version and honest player expectations

Update existing `README.md`, `docs/settings.md`, applicable `docs/ui.md` guidance,
release notes and roadmap/playtest evidence in the repository's normal convention.
Remove the stale “no in-game acceptance/never use” claims only in the reviewed
release; state **small-key-only**, opt-in and Gate1–4 evidence, not complete-game
acceptance of every source/target combination. Preserve own-dungeon hand safety.
Review the unsupported-keysanity line in `docs/discord/server-kit.md`; don't post
external announcements automatically.

Explain two named pickup messages, English in all16 languages, and that standing
HUD/pause-map/floating notices do **not** provide a remote key roster. In Gate4
the overworld notices appeared without increment; Ice Cavern showed none, despite
correct remote credit. Do not promise a target counter in those notices. Tracker
reads come later and are **not** a prerequisite implementation in this cutover.
No new model fix: the observed young-looking adult is normal. Qualify generic
Switch-icon text guidance for the separately rendered ocarina interface.

Maintainers select/bump the **next release version** because the set of supported
seed outputs changes; do not reuse published0.1.2 or silently regenerate/replace
a played seed. No agent version/lockfile bump without that approval.

### 5. Release gates after reviewed implementation

1. **Focused contracts + actual public API/CLI:** `make_seed`/`write_seed`, explicit
   anywhere CLI and encoded-CS1 replay now succeed on the supported dump; reject
   actual bad/unsupported destinations instead of bypassing checks. Exercise the
   normal Gift/Scrub setup paths for mixed recipes. Preserve default own behavior.
2. **Native fill sweep, proposed100 seeds each for Chest-only and Recommended
   mixed shuffle**, seeds0–99, one worker: real census/native pool, no monkeypatch.
   Every seed must pass `check_beatable`/existing age-return guarantee; audit every
   shuffled placement for small-only release, destination palettes, physical
   boss/map/compass home, exact pool conservation and no unbound off-area key.
   Keep first failing seed/settings/parsed values and diagnose before any rerun;
   do not count retried/filtered/failed rows as PASS. Representative optional
   BossHeart/Freestanding and door/free-travel modes get boundary cases too.
3. **Whole-seed emission/readback:** emit representative Chest and mixed public
   seeds, repeat same recipe in fresh output and compare every file; check exact
   placements/normal spoiler/CS1/play note, all copies, full allocations, native
   prefix/story inverses, registration/dependency closure, text in all16 archives,
   and serialized per-target grants. Reuse the existing source-family emission
   probe across **all8 targets**, not only its earlier two-target sample. Static
   coverage is not a claim every family/target was played.
4. **Own-dungeon control:** compare representative default/community recipes
   against pristine0.1.2 placements and romfs hashes; expected version metadata
   differences must be explicit. No collateral default-output change or revival
   of the Spirit-hand loss. Keep the integrated community-seed11 regression.
5. **Pack/UI path:** include anywhere in real romfs/NUP/layered-cache generation
   equivalence and UI generation smokes; stale scratch fixtures must be refreshed
   privately from the same build (include analyzed-event111), not “fixed” by
   disabling cache checks or mutating a player's dump.
6. **All four mandatory repository gates** on the final integrated source:
   ruff format/check, synthetic pytest, full dump pytest with recorded coverage.
   Full suites/sweeps serialize under normal `gate.lock`; worker1 while Kareem
   plays. No inherited pre-rebase/pre-switch PASS substituted for these runs.

Do not force a post-integration seed7 to retain the old gate placement digest:
the0.1.2 physical-area fix may legitimately change the fill/recipe/version.
Gate4's old output is evidence and stays frozen; new public outputs must satisfy
the audited invariants and their **own** deterministic digest.

### 6. Navi's map follow-up — scoped fix versus known ordinary-seed note

Named-key source clones **already** omit the audited acquisition-only Navi
balloons; native entries and independent story reactions (including Nabooru197)
remain intact. Keep that implementation and its behavioral/native inverses.
Any misleading old-item comment on a named-key route is a blocker, not cosmetic
acceptance for this feature.

Separate existing ordinary-seed issue: a changed non-key reward in a source map
chest can retain **“Now we won't get lost”** even without receiving a map. The
source comment is not a map grant; it does not invalidate saved target counts.
Do **not** silence all Navi, delete story effects, or broaden this patch to every
map/compass wrapper without native call-site evidence and review.

**cs12b recommendation for Claude review:** disclose that ordinary-seed cosmetic
follow-up in Known Issues/settings notes and track a separate focused fix; do not
claim all Navi text is corrected. If Claude requires it fixed before this release,
make that an explicit additional reviewed work item, with source-specific
preservation proof, rather than slipping it into refusal removal.

### 7. Decision / handoff boundary

**Claude: review the small-key-only mixed-shuffle scope, UI/help wording,
200-seed/native emission gates, and the proposed documented ordinary-Navi caveat.
Only then authorize production switch-on and choose the next version.**
This commit is acceptance/rebase evidence plus a plan; no availability/refusal
switch, new public preset, Tracker implementation or publication is authorized.

## Production cutover APPROVED — 0.2.0 implementation

Claude approved the preceding plan and authorized implementation on `r12/keys`.
Decisions: small-key-only/off-area chest grants; other dungeon items physically
home; native mixed-shuffle paths/defaults/presets unchanged; exact supplied
**Small keys anywhere** UI wording and equivalent CLI help. Delete the obsolete
guard/export/callers, no shim. Cosmetic ordinary-seed Navi map follow-up is
**not a blocker**: disclose in README Known issues, UI troubleshooting, settings
and the follow-up list; no broad Navi edit. Named-key misinformation stays blocking.

Authorized version **0.2.0**, including pyproject+uv.lock in the cutover commit.
Sweeps choose3 workers if no hookshot.exe at **each** start, otherwise1; full
suites/sweeps serialize under the shared lock. Keep first failures, no retried
rows counted. Stage one real public-path Recommended anywhere seed as one mod
for Claude's boot check, optional10-minute pickup/door route/current template/
thumbnail save description. Post cutover and each gate result; no merge/push/game.

LSP references for `patch.check_dungeon_items` were attempted: **no language
server available**. Literal whole-src/tests lookup found only its export/body,
CLI import/call and `make_seed` call; all removed together with UI availability.
Obsolete refusal tests removed, CS1/override coverage preserved; UI CS1 validation
now includes anywhere, and native NUP/layered equivalence gains Chest/mixed
anywhere modes. Production key/story/registration implementation otherwise unchanged.

### Approved follow-up list

- Ordinary changed map-chest **“Now we won't get lost”** is a cosmetic known issue,
  not a map grant/count defect. Separate future source-specific investigation/fix;
  keep native story reactions, no blanket Navi suppression.
- Tracker reads later; no roster/HUD implementation in this cutover.
- Played Gate4 assets/users remain frozen at a2c0c8e; new public recipe outputs
  receive their own version/digest and do not replace a played seed.

### Cutover implementation smoke

Backend/UI availability switched together with the exact approved label/help;
obsolete guard/export/imports/calls deleted. Defaults/presets unchanged. Version
and locked editable package are **0.2.0**; `uv lock --check` PASS. Six named
source/test files: format/check PASS.

Focused consumer/model/binding/text/physical-area checks: **66 passed/2 skipped**,
5.80s, worker1; skips require native dump. Actual **public CLI** seed7 anywhere
Chest-only succeeded:165 checks/23 spheres,90 romfs resources plus normal
spoiler/play note,26.15s. This is a new integrated recipe, not a rewrite of Gate4.
Full suites, sweeps, cache/UI/determinism and public mixed boot-stage evidence
remain pending; no inherited gate result is claimed for the cutover.

README/UI troubleshooting/settings now disclose the approved ordinary-seed Navi
cosmetic issue without claiming a map grant or applying it to named-key pickups.
Small-only scope and current-area counters are documented; Discord kit changed
locally only. Removed an unexercised sweep-success claim from the draft docs:
only completed played evidence is stated there.

### Production sweep failure and native eligibility correction

The first production sweeps are **failed product evidence**, not release passes:
Chest-only **76 passed/24 failed**; Recommended **70 passed/30 failed**. Every
failure was `opening_contract` at **Hyrule Field Chest (Obj_Heart_Piece)**,
hash `2967378296224661060`, kind `Obj_TBox_A_01_memo11`, no kept event. Fill
admitted an off-area small key, while the key compiler correctly refused its
unplayed opening. Original JSONL/first-failure/summary files remain under
`work/r12-keys-cs12b/production-020/sweep/`; no failed rows count as passing.

**Claude directed the fix:** share the played opening contract, refuse unsupported
off-area destinations before fill, preserve kept-event cases, and restart both
100-seed sweeps from zero. `clawshot.chest_openings.source_for` now owns the
small kinds (`A_01`, `A_06`, `GlassTruth_A_01`), big kinds (`A_02`, `A_03`),
`_NoBake` normalization and kept-event precedence. Both native destination
preparation and `patch/keys.py` use it. `restrict_key_openings` adds existing
per-location `excluded_items` data per target; `allowed()` already enforces it.
Every census copy is checked; physical-home generic key grants remain valid.
This preparation runs only for anywhere, leaving default own-dungeon untouched.

Whole native census: **10 raw kinds/184 checks**. Counts: `A_01`79,
`A_01_NoBake`39, `A_01_memo11`1, `A_02`24, `A_02_NoBake`16, `A_03`4,
`A_03_NoBake`2, `A_06`7, `A_06_NoBake`1, `GlassTruth_A_01`11. The **only**
excluded kind is `Obj_TBox_A_01_memo11`, the single Hyrule Field check above.
No new opening kind has been declared played. Synthetic regression on that
logical check plus supported, unknown, NoBake and kept-event cases: **9 passed**.

Separate first public-emission failure was an **audit-harness error**, as Claude
diagnosed: the intro setting component shrank512→384 bytes and retained its
5736-byte allocation. The audit had incorrectly demanded a generic `.bgyml`
growth formula. Corrected it to mirror the writer's no-growth rule, preserving
the initial failure and rerunning unchanged seed generation successfully.
That harness correction is not a product fix or an excuse for the chest failure.

Fresh evidence for the native eligibility fix is isolated under
`work/r12-keys-cs12b/production-020/opening-contract-fix/`. The new public UI
job completed seed7 Recommended anywhere: **300 checks/153 mod files**;
the completed record passed normal library integrity verification and the
actual rendered result was observed. No game/runtime was started.

### Fresh production sweeps, own controls and public boot stage

Both corrected native sweeps completed seeds **0–99**, **100 passed/0 failed**
each, **3 workers** each (Hookshot absent at each start), with age-return proofs
for all200 seeds. The summaries are separate new-run artifacts; original
76/24 and70/30 results stay failed. No opening/palette/pool/beatability/binding
violation remains in these200 rows.

Actual own-dungeon CLI controls against pristine0.1.2 passed for default seed7
and community seed11: placements and all romfs bytes match (80/139 resources).
The only changed spoiler field is `generator`: `clawshot 0.1.2`→`clawshot 0.2.0`.
No other default output change is being classified as version metadata.

The boundary harness's first run failed after product generation returned:
it passed an `Item` object to `allowed`, which takes an item **name**. The
printed `KeyError: Item(name='Ocarina of Time', ...)` is preserved in
`production-020/final-gates/boundaries.log`. Corrected only the harness
argument and moved fresh boundary outputs into `opening-contract-fix`;
the continuation runner skips the already-passing own controls and runs
corrected boundaries, then the four repository gates under `gate.lock`.

**Public stage:** the complete successful normal UI Recommended/anywhere
seed7 was copied byte-for-byte into the sole real mod
`ingame/mods/key-production-020-seed7-next/key-production-020-seed7-next`.
No forced placements. Both fresh sweeps have no Forest key at GC Maze Center;
instead the actual generated **Zora's River open grotto** holds a Forest key.
Readback verifies its binding in all source copies. The adult backup has that
chest and the first Forest courtyard chained door closed, zero Forest keys.

Launcher/checklist:
`ingame/Small keys 0.2.0 - seed 7 - Zoras River then Forest door.bat` / `.md`.
Current central template copied directly (SHA256 `80795106951ff85cbb9b48251328eb28a4c728dba1f72120ccde5579dab1fc9b`),
only NAME/ROUND/SAVES substitutions, ASCII/CRLF; actual dry run passed.
Exactly one four-file save copy, original source unchanged, played Gate4
outputs untouched. Player selects **Temple of Time, adult by Sheik/pedestal**
by thumbnail. Optional approximately10-minute pickup→reload→Forest door→reload
route permits a pickup-only partial report; no item/key/door cheats.

**Claude reported kp020 boot PASS:**515 log lines,12 mod lines from this exact
mod, rendering correct, no crash. Claude handed the optional route to Kareem
and armed the watcher on `user-key-production-020-seed7-next`. Do not alter
that user or staged mod. Pickup/credit/spending/persistence for this new seed
are not yet claimed; the earlier played Gates1–4 remain their own evidence.
No game was started by cs12b.

### Fresh public emission, source-family closure and UI equivalence — PASS

Fresh public API→CS1 CLI repeats on the corrected source are byte-identical
for every seed file, not only placements:

| Seed7 profile | Shuffled / small keys / spheres | Named copies | Registry additions | Banc copies checked | Native flow inverses | Languages |
|---|---|---|---|---|---|---|
|Chest-only|165 /37 /22|34|32|186|8|16|
|Recommended|300 /37 /22|36|30|185|6|16|

All allocations match writer behavior, including the shrinking intro component.
Both registration tables retain identical native rows and matching added IDs.
Composed actor/flow/text inverses, exact named messages in all16 archives,
actual child/subflow closure and absence of old-item named Navi comments passed.
The serialized helper's16 traces per profile (8 targets, empty/existing counts)
match all84 fields exactly.

Expanded source-family emission: **33 sources ×8 targets =264 requests**,
272 bindings including dependencies,16 flowcharts. Two independent writes
are byte-identical:35 files/296 added registry rows each. These source-family
bytes also match the pre-eligibility-fix probe; the compiler's source behavior
was not broadened to make an unsupported kind appear valid.

The browser-made Recommended seed7, fresh API output and fresh CS1 CLI repeat
match in **all155 files** (153 romfs plus spoiler/play note), all300 placements
and settings; no missing/extra/mismatched file. UI record short hash
`D3FEB009C792`; evidence aggregate
`51f6f51394a07750b991fea1206dcbaf1c3b5f4f4ede9a251ec8476991a734c7`.
The watched/staged mod is that unchanged UI output.

Legitimate anywhere outputs changed after correcting eligibility (75 changed
files for Chest-only,84 for Recommended versus the pre-fix run). Do not force
old0.2.0 scratch placements or use them as the deterministic oracle. This is
the still-unreleased0.2.0 correction; own-dungeon output preservation is proved
separately above. All earlier scratch failures and outputs remain preserved.
Proof JSON/logs live under `production-020/opening-contract-fix/`; full
synthetic/native cache/format suite results are recorded separately when complete.

### Corrected boundary run and lint gates

Product correction committed locally as **9a800d4**; no merge/push. The
corrected boundary harness passed all three real public generation/write
profiles on the same product source:

| Profile | Shuffled | Spheres | Written resources | Beatability and destinations |
|---|---|---|---|---|
|Recommended + Freestanding|314|16|158|PASS|
|Open Door of Time + free travel|301|18|151|PASS|
|Song-only door + mixed songs + mask hints, no fast start|300|15|149|PASS|

The first failed boundary log remains classified as **harness Item/name
argument error**, not a product failure or a passing row. Fresh successful
boundary proof is `opening-contract-fix/boundaries-proof.json`.
Full `uv run ruff format --check`: **314 files already formatted**;
`uv run ruff check`: **all checks passed**. Both ran worker1 under the
shared lock after corrected boundaries. Synthetic/dump results follow separately.

The0.2.0 wheel also built successfully outside the checkout. An isolated
`uv run --no-project --with <wheel> python -I` process imported the new
`clawshot.chest_openings` from installed `site-packages` (not editable source),
resolved the played A_01 source and refused memo11. Repository test environment
and the watched game/user copy were not changed by this packaging smoke.

