# Round 8, Track B: get-item models (cs8b)

Branch `r8/getitem`. Required instructions, README, plans00–04, decisions, round6/7 reports and Round8's
shared-file opening read. No game, batch/dry-run, window, Hookshot build, terminal-control command,
dump/save write, dependency-file change, merge, push or stash. External work: `E:/OOTRemake/work/r8-getitem/`.
The supplied post-bind invisible Fairy Ocarina observation is ground truth, not rerun.

## Item 1: isolate chest presentation from playable equipment

### Corrected trace

Read-only reproducers: `probe.py`, `guest.py`, `extract_guest.py`, `decode.py`, `contracts.py`, `lifecycle.py`,
`paths.py`; original dump build `e0f3ccfa`. The unmodified external AINB0.2.17 decoder ran in
`work/r7-play-cs7f/decoder-venv` outside the repository. No NX2navi source/docs or GPL implementation read/copied.
Native-executable diagnostic scripts also read only the player's own guest executable, using permissive
Capstone through ephemeral `uv run --with capstone`; no repository dependency changed. Those diagnostics did
not establish an additional exact engine visibility predicate, and none is claimed.

- Both ocarinas' native ModelInfo and ActorInfo already point to the correct Fairy/Time mesh. Their same
  geometry is visible for the patched Storms actor (Kareem's supplied result). Replacing the mesh is not a fix.
- **Correction to section26's explanation:** `PouchContentGuestPerformer.pack` has its own
  `EquipmentCommon.event.root` with exceptional binding; that graph already includes get-demo binding.
  Changing the instrument's `EventPerformerRef` alone is not proof that this guest path was repaired.
  Existing round7 player log2827 confirms the old Fairy pack actually came from the overlay.
- Native `Item_Ocarina_*` are Accessory equipment, with OcarinaParam/holder, equipment Blackboard,
  `GameActorAfter`, no PhysicsRef/AnimationRef/ASRef. Ordinary get actors, including the visible song stand-in,
  are event objects. Do not globally remove Accessory or change equipment-created flags to force a display.
- Saria's `Dm_Kokiri_0155/Event100` explicitly participates the instrument; Event93 binds it to Player's
  `Weapon_L`. Grant Event68 and get-text Event77 are independent. Native Time flow uses a separate
  `Dm_Item_Ocarina_Time` prop; both generic `Dm_Item_Ocarina_{Fairy,Time}` packs exist, use the correct mesh,
  have dummy Physics and **no Accessory**. Their native actor-creation metadata is method1.

**[INFERENCE]** The generic chest guest is an unsuitable presentation lifecycle for these equipment actors.
The exact hidden engine condition was not proved. The implemented correction bypasses that lifecycle rather
than pretending that a second blind instrument-component change proves the cause.

### Implemented path

`getitem.changes(romfs, actors)` remains an explicit experiment API, not a seed default.
When either ocarina is requested, it transforms both native chest flows only:

1. Compare `ContentName` through the existing `UI_MessageTargetActorName` String64 scratch field and native
   GameData string set/query actions. The dump oracle verifies this field exists; no saved Bool/layout is added.
2. For Fairy/Time, stage only its existing native `Dm_` prop, bind it to Player `Weapon_L` using the native
   gift's zero-offset hand binding, then continue the unchanged get-window/grant chain. **This is a handheld
   prop, not a claim of the usual floating/rotating get model.** Other actors run the exact old guest chain.
3. When the native chest sleeps its displayed content, offstage the selected prop. Neither prop grants items.
   The original grant still receives `ContentName`, exactly once; no sword equip, extra song, item clear or
   story flag is introduced. Native small and big chest command order differs and is checked separately.

Removed the ineffective ocarina pack/ActorInfo substitutions and their old tests; no compatibility shim.
Both playable ocarinas, their cutscene props, inventory tables, native gift flows and all grant helpers are
now byte-for-byte native because they are not emitted. The proven song mesh corrections remain unchanged.
No song inference policy, chest eligibility, fill, CLI, dependency or other-track source changed.

**Kareem: does the staged Fairy prop appear in Link's left hand during the chest notice, disappear after it,
and leave an instrument that still equips/plays? Repeat for Time and confirm the song survives the upgrade.
Report any stray prop, wrong position, lingering object, or native Saria/Time presentation regression.**
These runtime observations cannot be certified by a parsed file or flow interpreter.

### Exercised checks and printed failures

- Focused format/lint: four files formatted; lint passed after adding explicit `zip(strict=False)`.
- `uv run pytest tests/test_getitem.py tests/test_getitem_flow.py -q`: **27 passed**. Both chest orders,
  selected prop participation/bind/grant/offstage ordering, normal-item fallback, stale-chain rejection,
  reapplication rejection, song inverse diffs and embedded allocations.
- First targeted dump run: song oracle passed; ocarina oracle printed big-chest `Event11` is a **SubFlowEvent**
  whose incoming display edge changed. Extended only that inverse oracle's allowed event type, retaining the
  entire original event equality after restoring its single edge. Cause-specific `-k ocarina` run: **1 passed**.
- Real `uv run python E:/OOTRemake/work/r8-getitem/smoke.py`: common writer emitted two flows plus size table.
  Small **74808 -> 79616**, allocation **79888**; big **38848 -> 43680**, allocation **43952**. Native
  EVFL read/write/read and allocation checks passed. This was not a game run.
- Earlier smoke printed the actual big-chest order **Rotate -> NoHit -> Bind**, unlike small
  **NoHit -> Bind -> Rotate**; updated the guard to follow those exact original chains. Next diagnosed error
  was `evfl.I32` absent: EVFL uses builtin ints, unlike BYML wrappers. Corrected those parameters and fixtures.
  Failed/partial outputs were never reused; every aimed smoke used a fresh `-next` destination.
- Initial flow probe's import failed: `read_flow` belongs to census.hints, not census.gifts. Printed import
  path corrected. Initial extensionless Bermuda command failed127; listing found `bermuda.exe`, then post passed.
- Python LSP references reported no server; marksman only. Known-symbol callers migrated directly.

## Coordination

Posted scope, corrected guest-dispatch finding and instrument-preservation design on `cs-r8` as cs8b.
No shared code edit yet. Section33 follows the last present section31; reviewer inserts A's32 before33.
Reviewer's plans-only main move `e3745f5` is authorized; rebase at the next committed checkpoint.
No commit is called ready before the complete four gates.

## Item 2

Player output and exact actor/checklist inventory follow after the item1 commit. Chest admission changes
will use only supplied player results; unreported actors are not enabled by preparing an experiment.
