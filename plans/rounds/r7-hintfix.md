# Round 7, Track E: hints never name junk (cs7e)

Branch `r7/hintfix`. Read AGENTS, README, plans 00–04, decisions, all round-5/6 reports,
section 25, `r7-hints.md` and `E:/OOTRemake/work/r7-hints/make_7c.py` before edits.
Round-7 shared-file rules apply. `generate/hints.py` is now this track's. No dependency changes.
No game, launcher, window, build, terminal-control command, merge, push or stash.
Dump/save backups and the played 7b/7c folders remain read-only.

## Item 1: D29's worth-naming class

`generate.hints._worth_naming` reads the world's resolved item metadata once per shuffled candidate.
All four kinds (`item`, `always`, `sometimes`, `random`) use the same candidate class:
progression plus heart pieces/containers (including variants) and permanent non-progression capacity upgrades.
Fixed wallets inherit progression from their parent. The world's three normal-class upgrades are
`Deku Nut Capacity`, `Deku Stick Capacity`, `Bullet Bag (40)`; explicitly included because the world has
no separate upgrade type. Ammo, refills, `Buy` items, rupees and bottle-content variants are excluded
before checking progression. In particular progression-class Bombchus and Blue Potion are not worth naming.
Empty Bottle and Ruto's Letter remain progression; Odd Potion is a trade item, not a potion refill.
This interprets D29's explicit bottle-contents exclusion literally, including `Bottle with ...` items.
No settings, placement or fill behavior changed.

`_major`, required-location analysis and the barren predicate are unchanged. Hearts/capacity upgrades can
now be named but still do not disqualify a foolish area. A required item still disqualifies that area,
even if it is ammo. Exact stone assignments can change because filtering changes subsequent RNG draws;
unchanged barren means eligibility/truth, not identical randomized stone assignments.

Deleted the old test requiring random hints to name rupees; did not re-pin a randomized output.
`tests/test_hints_worth.py` exercises each of the four kinds in both mask modes across 50 permuted
placements each, using real world metadata in a synthetic geography, and checks positive coverage of
all 16 useful examples against 25 junk examples. Forced barren tests cover hearts/upgrades, ammo/refills,
wallet/equipment and required-ammo truth separately.

Checks:
- `uv run pytest tests/test_hints_select.py tests/test_hints_worth.py -q --tb=short`: **23 passed**.
- Actual public `generate(load_spec(), 7, Settings())` smoke: **164 shuffled checks, 22 spheres, 40 hints,
  zero junk named, fresh Search won**. No dump or output folder needed for this item.
- Python LSP unavailable (only Markdown's marksman configured); no exported API changed.
- Fixture failures diagnosed from printed payloads: empty pre-build item table rejected vanilla Hookshot;
  populated it before build. Then replacing the entire distribution map removed `balanced`, which Settings
  correctly rejected; preserve the real distributions and add the forced test distribution. Cause-aimed
  reruns only; no production behavior changed for these fixture errors.

## Item 2: continuation output
Completed after item 1 (`6fdf7e1`). Built the new
`E:/OOTRemake/work/r7-hints/seed-shop-7c-next/` without deleting or replacing an existing folder.
The session-owned builder copied `make_7c.py`'s existing reconstruction/patch path, changing its unsafe
OUT/STAGE deletion to fail-if-existing guards and using a session-unique stage/report path.
The original builder and played folder, user folders and running launcher were not changed.

Commands (from this worktree):
- `uv run python -u E:/OOTRemake/work/r7-hintfix-cs7e/build_7c_next.py`: **228 original placements,
  beatable in 25 spheres, 40 hints, all 77 original resources SHA-256 identical**.
- `uv run python -u E:/OOTRemake/work/r7-hintfix-cs7e/verify_7c_next.py`: independent read-back passed:
  exact placement/patch-plan equality; 40 unique stone labels; every named check has its actual placed item;
  all 13 written archives change only the 40 GossipStone messages, every other message/member unchanged;
  all lines agree with the spoiler and every highlight closes with `ffff`; no mask gate remains.
  Every added resource fits **7b's unchanged size table**.

Added text resources: `Event/EventFlow/GossipStone.bfevfl.zs` and 13 `Mals` archives
(`EUde`, `EUen`, `EUes`, `EUfr`, `EUit`, `EUnl`, `EUpl`, `EUru`, `JPja`, `USen`, `USes`, `USfr`, `USpt`).
As with A's original continuation, `CNzh`, `KRko`, `TWzh` are omitted: they would require size-table
growth, breaking the non-text-byte-identity contract. New ordinary seeds still write all languages.
The no-mask flow is part of the existing text feature, not a gameplay-placement change.
Kinds: 12 random, 11 item, 6 Way of the Hero, 5 barren, 3 sometimes, 3 junk.

### The 40 lines

| Stone | Kind | Line |
|---|---|---|
| KF Gossip Stone | random | They say Mido's house — middle left holds the Kokiri Sword. |
| KF Deku Tree Gossip Stone (Left) | random | They say Ganon's Castle Light Trial Center Pad Chest holds the Piece of Heart. |
| KF Deku Tree Gossip Stone (Right) | barren | They say searching Death Mountain Trail would only waste the hero's time. |
| LW Gossip Stone | item | They say Kokiri Forest hides the Hylian Shield. |
| SFM Maze Gossip Stone (Lower) | random | They say Ganon's Castle Forest Trial Wolfos Chest holds the Piece of Heart. |
| SFM Maze Gossip Stone (Upper) | barren | They say searching Zora's Domain would only waste the hero's time. |
| SFM Saria Gossip Stone | random | They say Market Potion Shop Bottom Inner-Left Shelf holds the Deku Shield. |
| SFM Song of Time Clearing Gossip Stone | item | They say Death Mountain Crater hides the Ice Arrow. |
| HF Southeast Grotto Gossip Stone | woth | They say Gerudo Valley holds something the hero cannot do without. |
| HF Open Grotto Gossip Stone | barren | They say searching Hyrule Field would only waste the hero's time. |
| HF Cow Grotto Gossip Stone | random | They say Goron Shop Top Far-Right Shelf holds the Hylian Shield. |
| LH Lab Gossip Stone | item | They say Goron City hides the Golden Gauntlets. |
| LH Gossip Stone (Southeast) | sometimes | They say Goron City: Boulder Maze Dark-Rock Corner Chest holds the Longshot. |
| LH Gossip Stone (Southwest) | junk | They say a hero who reads every stone has read too many stones. |
| GV Gossip Stone | random | They say Deku Tree: Falling-Platform Room Upper Chest holds the Fairy Slingshot. |
| Colossus Gossip Stone | sometimes | They say Ganon's Castle Shadow Trial Invisible Path Chest holds the Piece of Heart. |
| ToT Gossip Stone (Left) | item | They say Gerudo Valley hides the Fairy Bow. |
| ToT Gossip Stone (Left-Center) | random | They say Kokiri Forest: Deku Scrub Trio Grotto Chest holds the Bomb Bag. |
| ToT Gossip Stone (Right) | woth | They say Goron City holds something the hero cannot do without. |
| ToT Gossip Stone (Right-Center) | random | They say Kokiri Shop Bottom Far-Left Shelf holds the Goron Tunic. |
| HC Malon Gossip Stone | barren | They say searching Zora's River would only waste the hero's time. |
| HC Rock Wall Gossip Stone | woth | They say Kokiri Forest holds something the hero cannot do without. |
| HC Storms Grotto Gossip Stone | item | They say the Graveyard hides the Silver Gauntlets. |
| Kak Bomb Grotto Gossip Stone | item | They say the Bottom of the Well hides the Megaton Hammer. |
| Kak Open Grotto Gossip Stone | item | They say Goron City hides the Zora Tunic. |
| Graveyard Gossip Stone | random | They say Bottom of the Well: Invisible Alcove Chest holds the Hover Boots. |
| DMT Gossip Stone | item | They say Kokiri Forest hides the Deku Shield. |
| DMT Cow Grotto Gossip Stone | woth | They say the Deku Tree holds something the hero cannot do without. |
| GC Maze Gossip Stone | junk | They say Song of Time blocks are patient. Very, very patient. |
| GC Medigoron Gossip Stone | random | They say Deku Tree: Falling-Platform Room Chest holds the Boomerang. |
| DMC Gossip Stone | random | They say Graveyard: Dampé Race Finish Chest (under one minute) holds the Iron Boots. |
| DMC Upper Grotto Gossip Stone | item | They say the Forest Temple hides the Lenses of Truth. |
| ZR Near Grottos Gossip Stone | sometimes | They say Gerudo Training Ground Sunken Pool Room Chest holds the Piece of Heart. |
| ZR Near Domain Gossip Stone | junk | They say this stone has nothing to tell you today. |
| ZR Open Grotto Gossip Stone | item | They say Kakariko Village hides the Piece of Heart. |
| ZR Storms Grotto Gossip Stone | random | They say Spirit Temple Top Floor Sun Switch Chest holds the Piece of Heart. |
| ZD Gossip Stone | item | They say the Sacred Forest Meadow hides the Hookshot. |
| ZF Fairy Gossip Stone | woth | They say the Bottom of the Well holds something the hero cannot do without. |
| ZF Jabu Gossip Stone | woth | They say the Graveyard holds something the hero cannot do without. |
| Dodongos Cavern Gossip Stone | barren | They say searching the Spirit Temple would only waste the hero's time. |

### Human acceptance

**Claude: swap the staged overlay only after Kareem quits; never replace it while the game reads it.**
Reuse the existing isolated `Play shop seed 7c.bat` and `user-seed-shop-7c` continuation, unchanged by this
track. No new launcher/user or copied backup is needed for a text-only update of this same seed.

**Kareem: after Claude swaps it, continue through that launcher and talk to the four Temple of Time
stones without the mask. Facing the temple, left-to-right: Fairy Bow in Gerudo Valley; Bomb Bag in the
Kokiri trio grotto; Goron Tunic on Kokiri's bottom far-left shelf; Goron City Way of the Hero.**
Names should be highlighted, following words back to ordinary colour, with no rupee/ammo/refill named.
Check `fs: OpenFile(...): from the overlay` for `GossipStone.bfevfl.zs` and `Mals/USen.Product.110.sarc.zs`
in the existing launcher log. File/readback proof is complete; no in-game result is claimed.

### Shared-file integration

Only section 29 is appended to `plans/03-game-data.md`; cs7d's section 28 is not on this branch's base.
Insert that producer's full section before 29 at review, without placeholders. No shared settings,
fill, CLI, actor-table, pyproject or lockfile edit.

The saved-document check matched all 40 table rows exactly to the written spoiler's stone/kind/text.
After successful smoke/readback, removed only the two session-created throwaway scripts and their own
completed stage (the builder removes its stage); retained the requested output and JSON manifests
under `E:/OOTRemake/work/r7-hintfix-cs7e/`. The original `make_7c.py` remains untouched.

Read the actual generated `play-note.md` Gossip Stones table (40 rows), including the settled physical
Temple-of-Time order and new item/area wording. WotH remains area-only speech: its internal `Points at`
field can still identify required ammo (Goron City's Bombchus in this old seed). D29 filters the four
item-naming kinds, not that unchanged required-item analysis.

## Readiness

All four complete gates passed on the finished code (`6fdf7e1`; later commits are documentation only).
`PYTEST_ADDOPTS` supplied only session-owned external `--basetemp` directories, keeping decoded/generated
temporary data outside the repository. No filtering beyond the prescribed `-m dump`, retries or skipped failures.

| Full command | Observed result |
|---|---|
| `uv run ruff format --check` | **198 files already formatted** |
| `uv run ruff check` | **All checks passed** |
| `uv run pytest` | **586 passed, 78 skipped**, 265.69 s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | **77 passed, 587 deselected**, 523.84 s |

The full synthetic run includes the default/progressive/beatability/determinism sweeps and all new D29
boundary cases. The dump run includes both mask-mode whole-seed hint/reachability/text checks, archive
round trips and actual CLI output integration. Public generator smoke and independent continuation
readback are recorded above, not inferred from the tests.

Commits, in order: `6fdf7e1` item 1; `128e3c7` item 2; final documentation/evidence commit follows
(its hash is posted in the thread and final handoff).
No implementation acceptance criterion remains. Human game acceptance is still Kareem's: the exact
post-swap Temple-of-Time/colour/overlay-log checklist is above; no game was started by this track.

Checkpoint posted on `cs-r7` as `cs7e`: item commits `6fdf7e1`, `128e3c7`, staged continuation proof
and section-28/29 integration note; explicitly not readiness while the complete gates run.

Removed only the two completed session-owned gate basetemps after their successful processes exited.
Requested `seed-shop-7c-next`, its spoiler/note and the external JSON proof remain. Played seed/user,
save backups, dump, original builder and launcher untouched. Ready for Claude's branch review and
safe output swap; section 28 belongs before this track's section 29 when integrated.
