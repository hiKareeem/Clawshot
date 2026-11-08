# Round 6, Track F: findings from play (cs6f)

Branch `r6/play`. Required worktree instructions, plans 00–04, decisions, all round-5 round files and
round 4's child-logic report read before edits. Round-6 opening/shared-file rules followed. No dependency
change, game/window/launcher run, dump/save write, merge or push. Research lives outside the repository at
`E:/OOTRemake/work/r6-play-cs6f/`; dump build `e0f3ccfa` is read-only.

## Item 1: Deku Tree weapon alternatives

Source: Kareem in game via Claude, 2026-11-08, `seed-shop-7`, Hookshot 2.0.1: Boomerang activates the
Slingshot-room exit switch, clears the lobby vine-wall route to 3F and stuns Gohma. These are supplied
player observations, not a new agent game run.

Read-only `probe.py` parsed both Deku Banc files and the shop flow; `switches.py` parsed the eye-switch,
Skullwalltula and boss packs and inspected existing decoded room modules. Room 0's vine blockers are
Skullwalltulas 2729587378952040865, 16183956171357380613 and 3995458350586152163 (y 113–116).
Room 2 eye 9080063866993537303 drives the ladder 2096903280161003875 via
`InsideTheDekuTree_Level_Room_C_Prefab_efa7`: node 6's first-on output starts node 8's event, whose
Bool participates in node 14's ladder trigger. Room 5 eye 10433048972954508847 is the same
`Obj_EyeSwitch_A_02`, with no placement weapon override; `...Room_F_Prefab_bdf4` node 8 likewise
starts its event from first-on. Therefore the same Boomerang switch response is applied to the basement
eye too; fire for the web remains required. This is data-backed shared-actor behavior, not a claim that
Kareem separately tested room 5. Boss Hash 15302759724049838417 is `Enemy_DungeonBoss_Gohma` in room 10.

`child_deku_tree.toml`: Slingshot or Boomerang for 3F; add Boomerang to both eye-switch routes and the
Gohma stun alternatives. Preserve Bow where already allowed, jumpslash damage, fire and Deku Shield
scrub requirements. Adult Bow/Hookshot vine traversal and unarmed room recovery remain unverified.

First targeted run: 30 passed, 2 failed in new tests. Printed counts/reached regions showed the test
start region enabled both ages (adult Nuts could beat Gohma), and the stick name was incorrectly plural.
The test start now gates on the requested starting age; the real item is `Deku Stick (1)`. No production
rule was weakened to satisfy the tests. The edit response also exposed a replaced test declaration;
restored it before execution. Corrected targeted result and live smoke follow in the next checkpoint.

Checkpoint: `uv run pytest tests/test_world_remake.py tests/test_world_remake_play.py -q`:
**32 passed**. Scoped ruff format/lint passed (2 files). Actual `load_world()` / `Search` smoke with sword,
Deku Shield, Boomerang and one stick reached 3F, basement, basement back room and Gohma as child;
`Defeat Queen Gohma = True`, `Slingshot held = False`. Full gates reserved for the branch handoff,
before any commit is posted as ready.

## Item 2: shallow castle moat

HF01 source: Kareem in game via Claude, 2026-11-08: the moat is shallow; no Silver Scale is needed.
The current rules already agree: both `HF Ocarina of Time Item` and `Song from Ocarina of Time` are
`is_child and has_all_stones`. No scale requirement was present to remove. Kept the rules intact and
recorded the confirmation beside the child-field rules, rather than adding a duplicate override for the
item already owned by `remake.toml` (`vanilla_fixed`). Read-only placement inventory identifies
`Obj_Ocarina_Time_A_01` Hash 2802436684568022035 at (16,145,43), Child Static.

`uv run pytest tests/test_world_remake_play.py -k moat -q`: **2 passed, 8 deselected**: both checks
work with three stones and no scale, not two stones, and not as adult. First full-world smoke had not
opened the forest exit: printed child frontier ended in Kokiri/Lost Woods. Supplying the actual
`Defeat Queen Gohma` event opened the path and both moat checks became reachable with scale false.
Ruff printed one required assertion-line join; applied that exact formatting correction.

## Item 3: free post-Mido Deku Shield — trace correction

`probe.py` and compact `shield_trace.py` read the original flow with `clawshot.formats.evfl`:

1. `Talk` reaches Event23: `Goto_HyruleCastle_IsCompleted_Exp` false → Event21.
2. Event21: `Get_StoneOfForest_IsCompleted_Exp` false → Event1.
3. Event1: `Meet_DekuTree_IsAfter_Step02_Exp` true → Event83 → `present_DekuSheld`.
4. Event45: equipped `Weapon_Shield_Deku` (slot 4) → return, no grant; not equipped → Event63.
5. Event63's first-talk flag false → Event46 → Event117 gives `Obj_Shield_Deku` → Event61 →
   Event44 sets `HaveTalked_Npc_Kokiri_001_Shop_Child_PresentDekuShield` true.
6. **The same flag true does not stop a grant:** Event64 → Event116 gives `Obj_Shield_Deku` → Event66.

Thus the flag selects first/repeat dialogue, not once-only eligibility. No sword, Hylian Shield, ownership
history, shelf contents, purchase or rupee test occurs in `present_DekuSheld`. Unequipping the Deku Shield
satisfies the equipped test. GameDataList confirms the first-talk Bool is saved (reset type 8/file 0,
default false); the quest predicates are BoolExp, not saved independent flags.

This corrects section 19's historical “given once” characterization and section 17's unresolved replacement
question; no change to gift patching/census is made here. Repeatability and the equipped-item test mean it
is **not a safe shuffle check as-is**. Shuffling later needs a true once-only gate on both grant branches
and removal of the old equipped-item dependency, subject to owner approval. No new pool reward is added.

Source: Kareem in game via Claude, 2026-11-08, `seed-shop-7`: child, Kokiri Sword/Hylian Shield, post-Mido,
no Deku Shield; shopkeeper gave one free while the shelf still sold one at 40. The supplied observation
supports the first grant; repeat grants and the late-story cutoff are data findings, not new play results.

### Applied model and checks

`child_kokiri_forest.toml` adds event `Deku Shield` in `KF Kokiri Shop`, requiring a child route to
`KF Outside Deku Tree`. That route lets the child advance the meeting quest by talking to the tree, then
return for the gift **before** completing Gohma/castle quests. It is a monotone record of that obtainable
early shield, not a claim the offer remains open after those quests. The Deku Tree talk advances the quest
even with Mido skipped; merely being in the shop before Mido cannot bootstrap the event. No invented
inventory-absence requirement: the equipped test is satisfiable by unequipping; already having the shield
also already satisfies the capability. No fixed/shuffled location, item pool or gift patch contract changes.

`uv run pytest tests/test_world_remake_play.py tests/test_world_remake.py -q`: **41 passed**.
Regressions: sword alone, Hylian alone and sword/Boomerang cannot bootstrap kept Mido; sword/Hylian
permits the free shield and the Deku Scrub route without buying a Deku Shield or beating Gohma; Mido-skip
permits visiting the tree then the gift without a sword; adult cannot claim it. The independent forest exit
stays shut. Live full-world Search smoke printed `(free shield, outside tree) = (False, False)` with sword
alone; after collecting Hylian: free Deku true, bought Deku false, Slingshot-room route true, forest exit false.
Scoped format/lint passed (1 file).

Posted the exact repeat-branch correction on `cs-r6` as cs6f; no other track's file changed.
**Kareem via Claude: on a disposable early post-Mido save, unequip the first free Deku Shield and talk
again; does the repeat branch give another shield notice? After Gohma, does the free offer disappear?**
These corroborate the data, not prerequisites for accepting the supplied first-grant observation.

## Item 4: answers and section 12

Updated HF01/GIFT02 and the answered parts of DT01/DT02. Left unarmed recovery and adult vine weapons
pending; SHOP01's burned/repeat scenario is not mislabeled as played. Added direct observation
`R6F-GOHMA` rather than pretending a new question had been scheduled. Removed stale ledger claims that
no answer was observed/all nine already-asked rows remain pending. Section 12 records all three findings,
corrects its Slingshot-only summary and explicitly distinguishes shared-actor/repeat-branch deductions
from Kareem's actual observations. Historical sections 17/19 remain untouched; section 12 names the correction.
Updated one stale Slingshot-only comment in the existing whole-world test; its assertions are unchanged.

Saved-document smoke: **199 unique ledger IDs, 188 local Markdown links resolved**; all supplied findings
are in section 12, before section 13. No guide text, decoded data, generated overlay or save bytes were added.

## Commit checkpoints

- `cb5fee3`: item 1, sourced Deku Tree Boomerang routes and regressions.
- `dc1ed26`: item 2, no-scale moat confirmation and boundary regressions (existing rules correct).
- `f81146f`: item 3, free-shield event, exact merchant branch trace and non-bootstrap regressions.
- `8346a48`: item 4, answer ledger, section-12 findings and stale test-comment correction.

### Cross-track integration note

The thread's cs6a opening-route checkpoint still requires buying KF6 Deku Shield after Hylian/Mido.
After this track merges, that purchase is no longer mandatory: the early merchant event supplies the shield
for free. **Claude/cs6a: regenerate the opening witness/note on the merged logic; update any regression
that insists on a KF6 purchase, and explain the free shopkeeper visit before entering the tree.**
This worktree does not contain the names track's unmerged presentation code/tests; no other worktree is edited.
The existing scrub still needs a Deku Shield; do not replace its requirement with the Hylian Shield.

Additional runtime smoke: the historical `python -m clawshot.generate` command in the world-format plan
failed because that package has no `__main__`. The printed exception identified the missing entry point.
Used the supported `python -m clawshot --romfs ... --seed 7 --out ...` instead; it passed as recorded below.
No module stub/extra CLI or unrelated documentation rewrite was added.

Supported full CLI smoke completed: **seed 7, 164 shuffled checks, 28 spheres, 60 overlay resources**
plus spoiler, default gated return retained. `python -m clawshot` exercised actual fill, finished-seed
oracle and writer, with every changed resource/size decision printed. Output was only under
`E:/OOTRemake/work/r6-play-cs6f/seed-smoke/`, not a player launcher or active seed. Posted the opening-note
integration request to cs6a/Claude, including the free visit before the Deku Tree rather than a KF6 purchase.

## Final full gates and handoff

All four required commands completed in full on the finished behavior/test tree through `8346a48`.
Pytest's `PYTEST_ADDOPTS` set only `--basetemp` to session-created directories under
`E:/OOTRemake/work/r6-play-cs6f/`, keeping all dump-derived temporary output outside the repository.

| Command | Observed result |
|---|---|
| `uv run ruff format --check` | 160 files already formatted |
| `uv run ruff check` | All checks passed |
| `uv run pytest` | 443 passed, 58 skipped; 695.51 s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | 57 passed, 444 deselected; 633.83 s |

The synthetic gate includes the whole-world vanilla/200-default-seed/progressive/determinism checks,
gated-return checks and all 17 new play regressions. The unchanged full dump gate covers census/formats/
writer integration on this branch's C/D-inclusive base. No failed test was suppressed or accepted.
The separate actual CLI smoke succeeded (164 checks, 28 spheres, 60 resources); its generated overlay
and both completed pytest basetemps have now been removed. Three read-only research probes remain
outside the repo for reproducibility. No dependency change, game/window/launcher run or save/dump write.

Track F items 1–4 are complete. No merge/rebase/push performed. Four item commits are listed above;
the next documentation-only commit records this final evidence and the cross-track presentation request.

Left for Claude/Kareem, not a reduced implementation scope:

- Merge/review on the round's integrated tree; cs6a's opening note/witness must use the free merchant
  visit rather than insisting on a KF6 purchase. Request posted to `cs-r6`; names code is not on this branch.
- Optional play corroboration of repeat-shield/late-story cutoff; do not shuffle this repeat grant as-is.
- Still unanswered original questions: unarmed Slingshot-room recovery, adult Bow/Hookshot vine routes.
- The old module-only generation command in `04-world-format.md` is stale; supported CLI was used.
  That unrelated historical documentation was intentionally left outside this track's edits.
