# Round 5, track C: whole-game chest seeds (cs5c)

Branch `r5/seeds`. Dump and save backups read-only; no game, launcher or windows started.

## Item 1: extra patch steps

`make_seed(..., extra_steps=[step, ...])`: a `PatchStep` receives the generated placements (`Mapping[str, str]`) and returns `FileChanges`: a mapping of romfs-relative paths to `Callable[[bytes], bytes]`. Each transform receives decompressed bytes and returns decompressed bytes, validating its own format read-back. Close over romfs/census/world context when creating the step. Steps run in registration order after chest edits, including when shops and chests share one Banc. The common writer handles compression, raises size entries and builds every file before writing any. Steps must not return the size table itself.

Chest linking/planning only handles `Chest`; other kinds use these steps. A non-chest shuffle without any registered step is refused. Existing chest-only callers keep working. No dependency added.

Verification: `uv run pytest tests/test_patch.py tests/test_seed.py -q`: **20 passed** (including shared-file composition and all-or-nothing failure). Scoped ruff lint/format checks passed (4 files). Live dump-backed seed 7 slice with a registered transform wrote 6 files; the transform received the already chest-patched Banc (3,639 actors); temporary output removed. This item is committed and posted separately before chest coverage work.

## Verification status

Whole-game outputs are search-verified, not in-game certified. The final four outputs below include the reviewed
chronological model and default-on earliest-return guarantee; no integration prerequisite remains.

## Item 2 prerequisites and investigation

- New checks were not supported by the existing override loader: `3a9b692` adds explicit `new = true` locations. Four schema/reachability tests passed; live search printed `[]` before Bomb Bag and the new chest afterwards. Posted on `cs-r5`.
- `1b2fbfd` (reviewer-authorized, model and test only) gives `GanonBossKey` dungeon ownership. Before: dungeon `None`, outside placement allowed. After: `Ganons Castle`, outside refused; regression also checks actor disambiguation and the `anywhere` setting.
- Follow-up reviewer request: region `Ganons Castle Tower` inherited no dungeon from `Bosses.json`. `extra_ganon_tower.toml` sets its dungeon with explicit existing-region metadata (`new = false`, source required); this preserves its checks/exits. Six focused tests passed. Actual full-world smoke: tower dungeon `Ganons Castle`, tower chest allowed, Kokiri Sword chest refused.
- OoT Randomizer treats the tower as castle for its boss-key setting: `Region.py:112-140` selects `shuffle_ganon_bosskey`, then checks `HintArea.at`; `Hints.py:475-507` inherits the castle hint through the tower's entrances (`Bosses.json:214-229`), at MIT commit `526b4c8d`. Clawshot's explicit dungeon field reproduces that ownership without adding a second hint-traversal model.
- The first Bermuda command failed with exit 127 because `~/go/bin/bermuda` resolves without `.exe` in this shell. Directory inspection showed `C:/Users/hi/go/bin/bermuda.exe`; all posts use that binary now.
- Launcher requirement (reviewer): use the corrected r2-test/cs5b launcher, executable **only** `E:\Games\Hookshot\hookshot.exe`, never the device-losing `work\hookshot-main` build. Launchers will be written, never run.

## Item 2: every chest accounted for

The dump census has **184 chests**, **119 initially unlinked**. All now have a world identity: **164 shuffled**, **20 explicitly excluded** with `keep_vanilla`, a specific reason and `rule = "False"` (the oracle cannot collect an excluded vanilla item). No unrepresented chest remains. DreamWorld remains outside the census. The Treasure Chest Game reward stays vanilla pending D17's in-game swap test.

The parent linked the overworld checks using round 4's room/actor findings and a read-only nearest-actor probe. Two independent investigations mapped the child/small dungeons and seven adult dungeons; full per-Hash evidence stays outside the repo in `E:/OOTRemake/work/r5-seeds/{child,adult}-chests.{json,md}`. Definitions were regenerated with `clawshot.census.write_locations` (625 entries; 510 OoTR-linked across all kinds). New checks use the existing census readable name, never a fabricated OoTR identity. Rules and exclusion evidence live in `remake/extra_<area>.toml`.

Corrections to earlier item-only matching:

- DC Hash `7764016096998075927` is the lower-Lizalfos red-rupee reward, not Bomb Flower Platform. The latter is `11582649900854566065` (Deku Shield). Room/event/nearby Bomb Flower settle the identity.
- Ganon Hash `14404733996390762670` is Water Trial Right (room 5), not Spirit Crystal Switch. The Spirit switch chest is `7899179288432849355` (room 17, Scrub Business Seed).
- Forest Raised Island Courtyard, Well Front Center Bombable and Well Like Like have no chest in their remake rooms; marked N64-only rather than retaining phantom checks.
- Symmetric blue GC maze chests, GTG lobby/first-two heavy-block chests, Spirit invisible pair and Fire's three timed scarecrow-room chests have provisional name pairings but identical conservative requirements within each pair/group. They do not loosen access. **Kareem: identify their left/right/first/second names in game when convenient.**

The actor table now covers Scrub Business Seed (D12 normal filler), Magic Jar, Ganon's boss key and the default `Obj_Rupee_Green` spelling (backwards alias to the canonical green-rupee chest actor). Changed chests with an already-owned substitute branch give the placed actor on **both** branches; vanilla arrows/rupees cannot replace progression just because Bow or Deku Shield is already owned. No actor packs or game source were changed.

Excluded checks (all normal filler/heart pieces, never keys or equipment): KF/LW elevated purple chests; LLR tower upper chest; two Kakariko windmill variants; two Dampé repeat-rupee rewards; two GC sign-puzzle chests; GF underground red chest; GV underwater seed and three grotto-copy entries; three adult Field/Lake red chests with unresolved appearance triggers; LH timed-candle grotto chest; ZF high masonry chest; Well room 11 fake-floor chest.

**Kareem: establish the routes/appearance conditions for those excluded chests before including them.** In particular: the KF/LW upper ledges and ranch tower climb; Kakariko upper windmill; GC grotto sign puzzle and whether its rewards are independent; which remade GF/GV holes lead to each grotto; the adult Field/Lake red chests; the LH timed-candle puzzle; the ZF upper ruins; and safe access around the Well room 11 hole. Exact Hashes and reasons are in the corresponding extra files. **Well: is the east-corridor ladder chest submerged before Lullaby, and are the old west pit and Like Like room empty?** Its Underwater Left correspondence is provisional but retains the stricter Lullaby requirement. **Forest falling-ceiling chest: green rupee (actor default) or Bombs as one guide says?**

Checks: `uv run pytest tests/test_patch.py tests/test_patch_chests.py tests/test_patch_extra_loader.py tests/test_patch_ganon_key.py tests/test_seed.py -q`: **29 passed**. Scoped ruff lint/format checks: **5 files clean**. Live dump-backed `make_seed(..., 7, Settings())`: **164 shuffled, 27 spheres, 135 changed chests, zero unrepresented**; all eight dungeon chest-key counts match the census (5/8/4/5/4/1/9/1), plus exactly one Ganon boss key. First smoke one-liner had an unmatched `)` (printed SyntaxError); moved it to a script and corrected that cause, then the single rerun above passed. No game was started.

The full seed-7 overlay smoke also wrote **52 files** to a session-created temporary folder, read the output
back and checked every size-table entry against `rstb.required_size`; all fit. Six changed substitute branches
in the written Banc files matched their primary placed actor. Temporary output removed.

## Item 3: keep story state with the opened chest

Reviewer approved retaining every wrapper except the unsafe Kokiri Sword wrapper. Chest `ContentName` still
comes from the placed actor; four previously removed wrappers now keep their real state automatically:
Ice Arrows quest `Complete`; Nabooru timeline/two Navi-tip clears/Spirit `Step07`; gold-gauntlet cosmetic scene;
Water Serenade event, its learned flag and Water `Step04`/`Step05`. Exact flow/node identifiers are in section 18
and `chest_events.toml`; the spoiler patch records kept wrappers and their state audit.

The Water event's **song check** is `Dm_MelodyGet_Water:C15/Event29`, argument
`ActorName = Item_Melody_WaterSerenade`; its shared play-along is `EntryPoint0/Event14` →
`Dm_SY_Ocarina:LearningOcarinaPlayAutoForSeek`, Water case `Event68`. Chest patching does not shuffle that gift.
The reviewer is coordinating it with cs5d. `Sheik in Ice Cavern` remains the song's world identity.

The Kokiri wrapper and `Dm_Kokiri_0063:C01` write no persistent flag or quest step, so nothing needs restoring.
Only the unsafe equipment creation is bypassed by the default chest event. Other Navi lines/cosmetic scenes
may still name/show a vanilla item; they cannot replace the actual placed grant. **Kareem: when opening the
four stateful chests, confirm their quest/cutscene/song continuation still runs and the inventory reward is
the spoiler's placed item, not the vanilla chest item; record the overlay-open log line.**

Verification: synthetic patch tests **20 passed**; scoped ruff lint/format **4 files clean**. Targeted dump
regressions **7 passed**: each of the four retained wrappers remained on every written copy of its chest with
a changed placed actor; only the Kokiri Sword wrapper was removed; no sword-wrapper story writes; Serenade's
embedded gift step identified. Live full-seed overlay smoke likewise read all four retained wrappers and
placed actors back, all 52 size entries sufficient. Temporary output removed.

Probe failures were diagnosed from printed values, not retried blindly: EventSetting names are virtual
`Work/...evfc` paths, normalized to basename; some rows omit EntryPointName and use EntryPoint0/cuts;
Nabooru's row uses TimelineFileName rather than FlowchartFileName. The corrected probe explicitly handled
flowchart entries and timeline clips. No game was started.

## Item 4: fast start in seeds; independent Mido gate

`Settings.fast_start` is serialized in the spoiler. `python -m clawshot` defaults to `("intro",)`:
the movie is skippable by button, not removed. `--skip intro saria mido deku_tree kaepora` chooses the complete
list explicitly; `--skip` alone turns fast start off. Unknown names are refused before the census/fill.
The existing `gamedata.build` builds and validates the selected files; the common writer includes them only
after all chest/kind patches have also built. A path collision is refused rather than overwriting another
step. GameDataList's layout/size is unchanged; the intro's component tree shrinks; neither borrows an unverified
generic BYML sizing formula.

Mido's skip derives `skip_mido` from that same list (a contradictory `--logic skip_mido=...` is refused).
It changes only the child sword/shield event, never `open_forest` or `can_leave_forest`.
Read-only decoded module `KokiriForest_Child_Level_All_02_d26e` shows the independent exit guard's
`KokiriForest_Npc_Kokiri_007_Child_Blocker`/`_00` and `Get_StoneOfForest` `Complete` check; neither is changed
by the Mido flag patch. Search regression: no equipment + Mido skipped reaches outside the Deku Tree but not
the forest bridge; defeating Gohma opens the bridge. Kept Mido still needs the sword and a shield.

Reviewer supplied Kareem's in-game result (2026-11-08, `r5-shops/shield-slot-hylian`): sword + bought Hylian
Shield, no Deku Shield, Mido blocker cleared. All three definitions of the Mido event now accept either shield,
with that source. Five focused logic tests pass (including Hylian Shield). Physical found-shield aliases and
progression classification remain cs5b's shared normalization; verify them after its authorized rebase.

Actual CLI smoke (three subprocesses, never a launcher): default **7 overlay files**, Mido **8 files** with its
GameDataList blocker false, `--skip` disabled **6 files** and neither fast-start file. All exit codes **0**;
temporary overlays removed. Full dump gate includes exact selected-flag-only and default-intro seed checks.
The source edit briefly lost a docstring terminator; the edit tool printed that syntax cause and it was restored
before execution. Ruff printed one 122-column writer call; wrapped that exact call, then format/lint passed.

## Reviewer-requested oracle correction

`ed80a46` changes only `tests/test_world_data.py`. The vanilla all-chests assertion now exempts exactly the
twenty documented `keep_vanilla` + constant-False checks and asserts their complete name set; it does **not**
exempt reachable D17 checks or arbitrary unreachable/shuffled chests. The reviewer-reported failure was not
rerun unchanged. Printed all twenty names, patched the predicate, and the corrected vanilla oracle passed.
Ruff printed the needed multi-line assertion layout; formatted that file before its isolated commit.

## Full gates before the item-4 checkpoint

All four required gates passed on this tree, including the isolated `ed80a46` oracle correction:

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | 101 files formatted |
| `uv run ruff check` | All checks passed |
| `uv run pytest` | 313 passed, 35 skipped |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | 34 passed |

Pytest basetemps were explicitly under `E:/OOTRemake/work/r5-seeds/` so dump-derived temporary files stayed
outside the repo. Five completed parent smoke/probe scripts were removed after their evidence was recorded;
the per-Hash research inventories remain outside the repo. No dependency, game/save file, window or game process
was changed/started. No test or launcher was run through Hookshot.

## Item 5: original pre-age baselines (superseded)

Generated `E:/OOTRemake/work/r5-seed/seed-{3,7,22}/`: each has `romfs`, `spoiler.json`, a short
`play-note.md` with fifteen key-item locations/opening checks, and `size-check.json`. Each seed passed its
finished-seed search before writing. All 184 chest identities are accounted for; each shuffles 164 checks.

| Seed | Search spheres | Written overlay files checked |
|---|---:|---:|
| 3 | 24 | 58 |
| 7 | 27 | 53 |
| 22 | 28 | 59 |

Every non-table file was independently decompressed/read back; sized resource entries cover their required
allocation. Fast-start files use the validated non-growing/original-allocation policy above; the emitted size
table itself parses. A second actual CLI process regenerated whole-game seed 7 with `PYTHONHASHSEED=31337`:
exit 0, all 54 canonical files (`romfs` plus spoiler) byte-identical, zero differences. Temporary duplicate removed.

Prepared release-only `Clawshot play seed.bat` plus `Play seed {3,7,22}.bat`, copied from the corrected r3
pattern with separate round-5 user/log paths. Static check confirms executable exactly
`E:\Games\Hookshot\hookshot.exe`, no work-build fallback; none was run. No user folder was created by launching.

These pre-age baselines were explicitly marked provisional while awaiting the reviewed age model. They have
now been replaced by the four final integrated outputs below, including new route notes and return proofs.

Parent generation/determinism helper scripts were removed after recording this proof; no game-derived output
is in the repository. No merge or push.

## Authorized shops integration (`ccd1963`)

Claude authorized the rebase onto reviewed main `ccd1963`. Rebase completed; additive conflicts preserve
section 17 before section 18 and both appended native-shop/chest-filler actor blocks before `[aliases]`.
The CLI docstring now describes shops and fast start together; both implementations remain.

Added a two-case permanent regression in `test_generate_fast_start.py`: a real Deku/Hylian Shield collected
from Mido's top-left chest, with only Kokiri Sword initially, satisfies its corresponding
`Deku_Shield`/`Hylian_Shield` goal and the kept-Mido path. No bought-item proxy is supplied. The independent
forest-exit gate remains closed. Live runtime smoke printed both cases: helper/Mido `(False, False)` before,
`(True, True)` after, forest exit `False`, exactly that chest collected. Shop normalization needed no change.

The first combined gate stopped at Ruff's printed `I001`: auto-merged `gamedata`/`shops` imports needed
grouping. Grouped those imports exactly as diagnosed; the restarted gate targets that cause, not an unchanged
retry. No source behavior changed by that import cleanup.

At this checkpoint only shops was integrated; age regeneration awaited the next authorization. That dependency
is resolved by the final `2d7c02a` integration below.

Post-rebase delivery ledger (the earlier IDs above are historical): `4c5e465` Ganon-key type,
`ce15fa8` tower ownership, `0366a6e` Fire identity, `97912bc` coverage, `42b5c12` wrappers,
`6bded97` isolated oracle correction, `0134887` fast start, `cacb2a1` baseline evidence,
`741303d` found-shield integration coverage/import grouping.

An independent TOML parse also confirmed the two actor blocks remain in `[items]`: shop `Buy Magic Jar`
maps to `Shop_MagicJar_Small`, chest `Magic Jar` to `Tbox_MagicJar_Large`, Scrub Business Seed to its item
actor and the 30-Bombchu shop bundle to its native actor. The green-rupee alias remains in `[aliases]`.
The synthetic gate finished **342 passed, 40 skipped**; format **130 files** and lint passed.

The shops-rebase dump gate finished **38 passed, 1 failed, 343 deselected**. Failure was the existing shop
seed test applying `rstb.required_size` to the now-default intro component, a format without a verified generic
formula. Printed the actual failed output: **512 -> 384 bytes**, original/output allocation both **5736**.
Updated only that test's allocation oracle: selected fast-start resources must independently be non-growing,
fit their entry and retain the original table allocation; every other written resource still needs its verified
formula. Fast start remains enabled in this combined Chest+Shop test. No formula was invented or error hidden.

Claude then authorized final rebase onto `2d7c02a` (shops + age + gifts). The final request supersedes waiting
for A: rerun all gates on that integration, then replace the three baselines and add `seed-shop-7`, all with
default intro skip and the default-on chronological return guarantee.

The focused oracle rerun exposed a second printed test-helper assumption: it tried zstd decoding the intro's
plain `.bgyml`. Resource reads now decode only `.zs`, as the writer does. After that cause-aimed correction,
`test_seed_shop_copies_share_the_placement_and_keep_slot_prices`: **1 passed**.

## Final integrated main (`2d7c02a`)

Authorized rebase completed. Sections are **16, 17, 18, 19**; native-shop, gift and chest-filler actor blocks
all remain under `[items]`, with `[aliases]` last. The fill conflict was additive settings only: kept all main
shop restrictions, gift item/exclusive-type fields and age return-kit stages; added `fast_start`.
Kept both automatic free-travel placement patch pairing (off by default) and fast-start file handling.
CLI retains Gift setup and the fast-start option.

All four full gates on the integration passed:

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | 140 files formatted |
| `uv run ruff check` | All checks passed |
| `uv run pytest` | 381 passed, 46 skipped |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | 45 passed, 382 deselected |

Both pytest basetemps stayed under `E:/OOTRemake/work/r5-seeds/`. The corrected combined shop/default-intro
allocation oracle passed in this full dump run. No retries, weakened generation assertions or world logic
were added to get these gates through.

Final code ledger above base `2d7c02a`: `27b750e` key type, `4b7e5ff` tower ownership, `b205c73` Fire identity,
`a05226e` whole-game coverage, `a76c19f` wrappers, `c3dc76c` twenty-exclusion oracle, `b8aa345` fast start,
`99e1ca5` baseline evidence, `4f0b9a6` found-shield coverage, `8015de5` combined allocation-oracle correction.

### Final generated outputs

All four were regenerated with code **`8015de5`**, based on reviewed main **`2d7c02a`**, after the four full
gates passed. Inputs: whole world, own-dungeon keys, default `intro` skip only, Mido kept,
`age_return_guarantee = true`, `free_time_travel = false`. No Gift shuffle.

| Folder under `E:/OOTRemake/work/r5-seed/` | Shuffled checks | Search spheres | Overlay files checked |
|---|---:|---:|---:|
| `seed-3` | 164 Chest | 27 | 60 |
| `seed-7` | 164 Chest | 28 | 60 |
| `seed-22` | 164 Chest | 23 | 61 |
| `seed-shop-7` | 164 Chest + 64 Shop | 26 | 77 |

Each has `romfs/`, `spoiler.json`, `play-note.md`, `size-check.json`, `return-proof.json`. Every seed passed
the finished-seed oracle before writing and a fresh search with the chronological return guarantee afterward.
The separate adult-only proof reaches Phantom Ganon and the return pedestal from mandatory first-pull
inventory, without optional child loot. That raw inventory and its proof spheres are recorded per output.

Every written file was decompressed when appropriate and parsed; all non-table allocations cover their
verified formula or the fast-start non-growing/original-allocation policy. The size table itself parses.
The combined output independently checked **120 physical shop copies** against their placed native display,
GoodsList actor and original slot price. Live opening-route smoke found **KF Shop Item 8: Hylian Shield,
10 rupees**, child-accessible with only Kokiri Sword; that specific pre-Mido purchase is in its short note.

An actual second full Chest+Shop CLI invocation (`--seed 7 --shuffle Chest Shop`, hash seed 31337) exited **0**:
all **78 canonical files** (77 overlay files plus spoiler) byte-identical to the library-generated combined seed.
Temporary duplicate removed. All four outputs were published only after every build/check succeeded; only
this session's three known provisional output folders were replaced. No user/save folder was deleted.
All provisional/NOT-final marks are gone from the output folder and its notes.

Unrun release-only launchers: `Play seed 3.bat`, `Play seed 7.bat`, `Play seed 22.bat`,
`Play shop seed 7.bat`; shared launcher argument `shop-7` selects `seed-shop-7` and a separate
`user-seed-shop-7`. Only `E:\Games\Hookshot\hookshot.exe`; no fallback build. Fresh New Game, not a baseline save.
The parent generation helper was removed after proof. `verification.json` records the four results.

**Kareem's remaining in-game check:** pick a fresh isolated seed; confirm spoiler rewards plus the overlay-open
log, then adult Forest completion, return at the Temple pedestal and second pull. Confirm the four retained
chest wrappers keep their quest/song continuation, and no shuffled sword chest gives an extra vanilla sword.
No game/launcher was started by this track; no in-game certification, merge or push is claimed.
