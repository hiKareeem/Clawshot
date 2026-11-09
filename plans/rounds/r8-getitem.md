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
Section33 follows the last present section31; reviewer inserts A's32 before33.
After the item1 checkpoint, rebased onto the reviewer's authorized plans-only main `e3745f5`.
No commit is called ready before the complete four gates.

## Item 2: one isolated new-game output

Output: `E:/OOTRemake/work/r8-getitem/ingame/chest-gifts-next/`.
Launcher: `E:/OOTRemake/work/r8-getitem/ingame/Test - chest-gifts-next.bat`.
Exact routes, models, use checks and log evidence:
`E:/OOTRemake/work/r8-getitem/ingame/checklist.md`. Neither launcher nor game was run.
`build_output.py` built this fresh destination through the real common writer; no played output was replaced.

Fourteen existing saved chest Hashes, across ten Banc files:

- Mido far-left/middle-left/middle-right/far-right: Fairy Ocarina, Zelda's Letter, Weird Egg, Membership Card.
- Deku Slingshot-room upper side chest: Epona's Song; lobby map chest: Ocarina of Time.
- Deku compass main/side and basement: Keaton, Skull and Spooky masks.
- Graveyard left-end/ReDead graves: Bunny Hood and Goron Mask.
- Dodongo map/compass/lower-Lizalfos reward: Zora Mask, Gerudo Mask and Mask of Truth.

The enabled seed actor catalog currently has **zero mask mappings**. To provide useful complete evidence
without inventing mask shuffle, the controlled output tests all eight ordinary native `Item_Mask_*` actors;
no shop display/raw armor/Amiibo actor or seed mapping was added. Mask discovery initially printed no mappings
and then failed resolving the external default pouch parent from the actor-local pack. Printed each actual
local component with that parent explicitly omitted; no inherited defaults or policy/engine fix were invented.

This is an experiment, **not a randomized seed or beatability-certified placement**. Native Sword, main
Slingshot and Bomb Bag chests, gifts, doors, forest progression and prices remain unchanged. The route obtains
Epona with Fairy before opening Time, then checks song retention after upgrade. Later native Saria can still
give Fairy; the checklist explicitly distinguishes that native downgrade behavior from this overlay.

### Eligibility: evidence only

Item2 source commit `02277d1` adds only already reported round7 successes: `Item_DinFire` (spell/magic meter)
and `Item_Wallet_Medium` (500 rupees), citing section26. They were omitted from the old list despite supplied
player results. Minuet was already explicitly confirmed; the opt-in song inference wording now correctly says
the other **ten**, not eleven, are inferred. No new result is invented for Epona or the other experiment actors.
Letter, Egg, Card, Time and masks gain no chest admission from output construction. The songs-anywhere policy
is otherwise unchanged.

### Independent actual-output proof

`PYTHONHASHSEED=803 E:/OOTRemake/clawshot-r8/getitem/.venv/Scripts/python.exe -u
E:/OOTRemake/work/r8-getitem/verify_output.py` completed; evidence:
`E:/OOTRemake/work/r8-getitem/artifact-proof.json`.

- All source and output SHA256 values match the build manifest; **14 chests / 15 resources**.
- Inverse tree diffs leave every Banc field native except the intended chest content/substitute edits.
  Sword, Slingshot and Bomb Bag contents remain native in actually written files.
- Independent inverse EVFL diffs preserve all original event data except the intended display/cleanup edges.
  Both added prop actors use native creation method1. Neither playable nor prop ocarina pack is emitted.
- Fresh `deterministic-replay-next` uses reversed requested actor order and another Python hash seed:
  all **15 resource bytes identical**. No old output was regenerated in place.
- Launcher statically checked: bin executable only, missing-exe stop, updater disabled, unique `--user`,
  no backup/main-user copy; isolated user directory does not exist before play.

The initial verification attempt did not expose a replay/proof result. Printed the script and the actual
`Location.id` contract, then added flushed per-stage diagnostics before the independent run above.
That run produced its complete proof. Background tool delivery exposed only early stdout;
the completed proof artifact, not that partial delivery, supplies the claims above.

**Kareem: run the single launcher after quitting the current game. Do both native hand props appear and
disappear correctly, do Fairy/Time equip/play, and does Epona survive the upgrade and Save/Continue? For every
other gift/mask, return its model, actual inventory/use and persistence, plus the overlay log. Egg hatching,
Letter guard use and adult Card use are separate observations, not proved by the item notice.**

**Provisional presentation choice for review:** reuse native handheld cutscene props, rather than mutate
playable equipment or claim an unproved floating get-model fix. Runtime visibility remains unverified.

## Commits and full gates

Item1: `b76da61` (authorized rebase of initial `0a96aa1` onto `e3745f5`).
Item2 eligibility: `02277d1`; experiment/report: `129a816`.
All commits are local on `r8/getitem`; no merge or push performed.

The full chained gates use fresh external `PYTEST_ADDOPTS=--basetemp=.../gate-synthetic-next`
and `.../gate-dump-next` directories:

- `uv run ruff format --check`: **207 files already formatted**.
- `uv run ruff check`: **All checks passed**.
- `uv run pytest`: **628 passed, 80 skipped**, 584.60s.
- `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump`: **79 passed, 629 deselected**, 860.47s.

All four full gates passed in one chain (1448.74s total); no unchanged failed command was rerun.
Actual-output common-writer smoke and byte-identical replay proof are recorded above, independently of tests.
Only round-file evidence wording changed after the gates; source and test contracts did not.

### Handoff boundary

Ready for code review, **not in-game certified**. Source checkpoints `b76da61` and `02277d1`,
experiment/report `129a816`, plus the final evidence-only round-file commit. Reviewer integrates section33
after Track A's32; no other track's source was changed. The staged-prop path is still explicit experiment-only,
not automatically applied to generated seeds.

Remaining: Kareem's single isolated new-game check and model/use/persistence/overlay results listed above.
The exact engine visibility predicate remains unproved; no claim that data tests establish runtime visibility.
No additional chest allowlist expansion until those player results. The reviewer owns final product approval
of the native handheld presentation choice.
