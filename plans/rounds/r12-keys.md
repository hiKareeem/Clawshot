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

## Questions

**Kareem: if a later gate needs a new save position, please supply it; this track will
not invent a room Teleport or modify your existing saves.** Existing r11 backups/slots
are the only sources currently authorized.

## Verification / commits

Research process check: `tasklist /FI "IMAGENAME eq hookshot.exe"` reported no matching
process. All pytest commands will use `CLAWSHOT_WORKERS=1`; full suites/dump/sweeps
hold the round12 mkdir gate lock and release it on every exit. No checks run yet.
