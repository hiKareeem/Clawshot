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

Pending after the item-1 commit. `seed-shop-7c-next` was absent at initial inspection, so a new folder
can be built without deleting another session's output. Never run the original builder unchanged:
it removes existing OUT and STAGE folders. Use a session-owned copy with fail-if-exists guards and a
unique session stage; never touch the played `seed-shop-7c`, any user or the running launcher.

## Readiness

Four complete gates will be recorded before posting any commit ready and before final handoff.
In-game presentation requires Kareem's check after Claude swaps the new overlay following game exit.
