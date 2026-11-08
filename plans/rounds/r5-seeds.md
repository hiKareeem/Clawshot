# Round 5, track C: whole-game chest seeds (cs5c)

Branch `r5/seeds`. Dump and save backups read-only; no game, launcher or windows started.

## Item 1: extra patch steps

`make_seed(..., extra_steps=[step, ...])`: a `PatchStep` receives the generated placements (`Mapping[str, str]`) and returns `FileChanges`: a mapping of romfs-relative paths to `Callable[[bytes], bytes]`. Each transform receives decompressed bytes and returns decompressed bytes, validating its own format read-back. Close over romfs/census/world context when creating the step. Steps run in registration order after chest edits, including when shops and chests share one Banc. The common writer handles compression, raises size entries and builds every file before writing any. Steps must not return the size table itself.

Chest linking/planning only handles `Chest`; other kinds use these steps. A non-chest shuffle without any registered step is refused. Existing chest-only callers keep working. No dependency added.

Verification: `uv run pytest tests/test_patch.py tests/test_seed.py -q`: **20 passed** (including shared-file composition and all-or-nothing failure). Scoped ruff lint/format checks passed (4 files). Live dump-backed seed 7 slice with a registered transform wrote 6 files; the transform received the already chest-patched Banc (3,639 actors); temporary output removed. This item is committed and posted separately before chest coverage work.

## Questions and provisional choices

- Whole-game seed outputs are search-verified, not in-game certified. Track A's chronological age model requires regeneration once Claude authorizes a rebase.

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
