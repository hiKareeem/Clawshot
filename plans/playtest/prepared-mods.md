# Isolated overlays — not yet played

**Kareem runs these only when Claude schedules session 16/17, after main-game child return unlocks.**
Normal logic sessions need no overlay. Six prepared overlays and nine release-only launchers are under `E:/OOTRemake/work/r5-playtest/`.
Every launcher is copied from the corrected round-2 template and uses **`E:\Games\Hookshot\hookshot.exe` only**.
No work-build fallback. None was executed, including dry-run mode.

## Tower: two separate copies

Launch either `Test - tower-red.bat` or `Test - tower-boomerang.bat`, not both together.
On first use each copies the **flat** `2026-11-07_llr-tower-before-pickup` backup into its own
`user-tower-red` / `user-tower-boomerang` folder. Later starts keep that test progress; they do not reset it.
Load the ranch main-progress save (archived slot 01), not the intro-era slot 04.

1. **MOD01, red control:** go to the tower floor Heart Piece spot. Pick up red rupee (20), save, leave/re-enter,
   quit and reload the **same** test user. It should stay gone. Report if it returns; Claude can inspect the saved Hash.
2. **MOD02, Boomerang chest:** on the other test copy, a small chest replaces that Heart Piece. Open it, use Boomerang,
   save/reload and return. It should remain open with Boomerang retained. This checks the chest fallback AND cheaply
   supplies Boomerang near the archived save for child range checks (e.g. KAK02). If it fails, stop this variant;
   a failed pickup conversion is not evidence that the ordinary Boomerang cannot reach a token.

Logs: `user-<variant>/hookshot_log.txt`. Claude looks for both
`fs: OpenFile(...HyruleField_Child_Static.bcett.byml.zs): from the overlay` and the size-table overlay open.
Then record actual item/model/text, inventory use and persistence; a log alone is not a pass.

## Fresh games: two separate users

These create empty test users, **never** copy a progressed save. Get the ordinary Kokiri Sword/Deku Shield and
enter the Tree normally. Keep each user's run separate; no combined overlays or transplanted size tables.

- **DT01:** `Test - deku-room-no-slingshot.bat`. The usual Slingshot chest gives a Red Rupee and its Slingshot event
  override is removed. No Slingshot is available in this variant. In that room let the platform fall, then try leaving,
  save/quit/continue, and separately game-over/continue. Record each resume location. This run may be permanently
  stranded: that is why it is disposable. Do not infer a safe escape from autosave existence.
- **DT02:** `Test - mido-boomerang.bat`. Open Mido's four house chests; the former green-rupee chest gives Boomerang.
  In Tree lobby, **before taking/using Slingshot**, try Boomerang on all vine-wall spiders and climb to 3F.
  Slingshot stays vanilla as a positive control. Adult Bow/Hookshot comparisons wait for ordinary adult access.
  LW01 can be checked later on this disposable run after Gohma, before meeting Zelda.

Logs stay in `user-deku-room-no-slingshot` / `user-mido-boomerang`. Claude checks the matching Tree Static or
Kokiri Child Dynamic overlay open; the Mido variant also raises a size-table entry.
A second pristine recovery comparison needs another disposable user staged by Claude; launchers never delete/reset users.

## Upgrade order and treasure reward

These two launchers **refuse to start until Claude stages a matching disposable user** at
`user-upgrade-order` / `user-treasure-red` (whole user root, `save/<user-id>/slot_NN`). They do not borrow an
unrelated backup or pretend today's child snapshot is adult-ready. Logs stay inside those test users.

- **MOD03:** `Test - upgrade-order.bat`, first-adult copy **before Dampe's Hookshot reward**.
  His usual Hookshot chest now gives Longshot. Test its range, then find the high windmill purple chest,
  now Hookshot (both normal/alternative adult states patched); test range again after receiving it.
  Record whether the lower item downgrades range or is ignored. If the windmill chest cannot yet be reached,
  record its access blocker, not a downgrade failure. Requires reviewer review of this isolated variant;
  it is not a beatable seed or a progressive-item implementation.
- **MOD04:** `Test - treasure-red.bat`, child-return copy **before first treasure-game reward**, preferably Lens.
  Win the game normally. First final chest now uses the repeat chest's red-rupee miniature and grants a Red Rupee,
  not a Heart Piece. Note preview, get text/model, wallet and whether another run/reload can pay the first reward again.
  Ordinary game boxes and the vanilla repeat chest are unchanged. This certifies a supported rupee preview only,
  not a major item's display compatibility. If item-based repeat logic breaks, report it; no seed integration is claimed.

Claude checks overlay opens for Graveyard Adult Static plus Kakariko Adult Dynamic/Alternative in MOD03,
and Market Child Static in MOD04, together with actual results.

## File checks performed (not game results)

| Variant | Changed placement | Raw size before → after | Existing entry → required |
|---|---|---|---|
| tower-red | HyruleField Child Static; Hash 9814903750835309225 | 395636 → 395652 | 395912 → 395944 |
| tower-boomerang | same Hash/file | 395636 → 395692 | 395912 → 395976 |
| deku-room-no-slingshot | InsideTheDekuTree Static; Hash 821372075822700622 | 109808 → 109756 | 110088 → 110024 (existing entry kept) |
| mido-boomerang | KokiriForest Child Dynamic; Hash 12786193094758345086 | 510884 → 510924 | 511176 → 511208 |
| upgrade-order | Graveyard Adult Static; Hookshot reward → Longshot | 105744 → 105744 | 106024 → 106024 |
| upgrade-order | Kakariko Adult Dynamic; high purple chest → Hookshot | 83060 → 83056 | 83336 → 83336 |
| upgrade-order | Kakariko Adult Alternative Dynamic; matching chest | 82932 → 82928 | 83208 → 83208 |
| treasure-red | Market Child Static; first reward item + preview | 259184 → 259100 | 259464 → 259368 (existing entry kept) |

Builder: `E:/OOTRemake/work/r5-playtest/build_overlays.py`; local `manifest.json` holds checksums and field diffs.
Observed run passed: four overlays, seven files total; decompress/write/read equality; independent field-diff allowlists;
original Hash/position and all unrelated fields retained; only three necessary size entries raised; all other size-table
entries unchanged; original placement checksums unchanged. No files under the game/save backups were written.
Second builder: `build_order_reward.py`; `order-reward-manifest.json` holds its checksums. Observed pass:
four further placement files, only intended drop/preview fields differ (independent reverse-field diff),
compression/readback and size-table limits pass, original bytes unchanged; no extra size table needed.
Total new outputs: six overlays, eleven files. Builders remain external reproducibility tools, not repo code.

Static checks passed for all nine copied-template launchers: one release EXE assignment each, dedicated user/
overlay/log destinations, no delete/reset/move/window-start commands. Two copy the flat tower backup, two require
pre-staged milestone users, five use new games (including three existing-overlay launchers below).
Initial checker falsely matched `start` inside inherited dry-run **echo** prose; printed predicates identified it,
and command-token check passed once corrected. No batch file was run. Runtime staging/gameplay remain unverified.

## Other controlled comparisons

- MOD03/04 artifacts above are prepared; reviewer approval and matching future milestone saves are still needed.
  Other tier-order tests wait for reviewed variants; no item stripping or new age flag is invented.
- MOD05: `Test - mini-seed-7.bat` starts its own empty user against existing corrected `r4-seed/seed-7/romfs`.
  Get moved sword and shield, then approach Mido. Other mini-seeds are not needed for this one gate observation.
- MOD06: `Test - intro-removed.bat` and `Test - all-skip-chain.bat` start separate empty users against existing
  `r4-fast-start/intro-removed/romfs` and `all/romfs`. First checks movie removal; second follows the post-Tree
  Field→Market→Zelda chain. Do not replay already-passed initial skip checks. No old launcher is invoked.
- MOD07/08 use Track B/D's reviewed artifacts and their own save/launch instructions, not a second shop/gift patch.
  Ask Claude to stage the release-only launcher if the producer has not yet supplied it.
- Missing-item/early-story states (MK02, TT01, unbroken-boulder/no-bracelet, untaken gifts, pre-tentacle Jabu) need a
  preserved matching copy or reviewed seed. Unequipping never clears ownership. TT01 is already asked, not scheduled.
- No standalone Fire Arrows pickup crash replay. No mod changes an already-asked fairy/owl/moat/Jabu/Door check.
