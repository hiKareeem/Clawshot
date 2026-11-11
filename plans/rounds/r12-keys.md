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

**Built and checked; unplayed. Claude must boot-check before handing it to Kareem.**

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
**Built and independently checked; unplayed. Boot-check required before handing over.**

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
  destinations, original story/Navi lifecycle and camera settings retained. One
  argument-driven helper writes existing saved remaining/total/first fields; metadata
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

| Commit before requested rebase | Scope |
|---|---|
| `7685b1b` | Gate1 scratch proof and plain checklist record |
| `9089d2b` | Small-key model/fill and age-copy/source binding constraints |
| `f9804b0` | New-label operation and dump-resolved English pickup pair |
| `35d3e16` | Source wrapper compiler, shared helper, guarded pipeline, allocation formula |
| `16dd52b` | Cause-directed analyzed-event registration/dependency closure for authorized2b; cache input and consumer coverage |

Registration addition: named event IDs now get source-modelled analyzed records,
preserving all native records/fields and carrying SubFlowList/ChildEventList closure.
The NUP working set includes that native registry. The synthetic event consumer now
requires both registration and declared cross-flow/child dependencies before execution.
Its six existing routing cases passed after this change; a missing-source-registration
case was then added for the full suite. This is still a startup hypothesis until2b is played.

## Questions

**Kareem: if a later gate needs a new save position, please supply it; this track will
not invent a room Teleport or modify your existing saves.** Existing r11 backups/slots
are the only sources currently authorized.

## Verification / commits

`tasklist /FI "IMAGENAME eq hookshot.exe"` reported no matching process at research
and before integration. Every pytest uses `CLAWSHOT_WORKERS=1`, regardless.
Full suites/dump/sweeps acquire `E:/OOTRemake/work/rounds/r12/gate.lock` via mkdir,
retry once a minute on contention and release via rmdir immediately on every exit.
Full gate results and rebased commit IDs will be recorded below before repository handoff.
