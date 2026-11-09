# Round 7, Track F: graveyard and bombs from play (cs7f)

Branch `r7/play`. Required AGENTS/README, plans 00–04, decisions and round-5/6 reports read;
Round 7 shared-file opening applies. No dependency edit, game/window/launcher/build, save edit,
dump write, active-overlay rewrite, merge, push, stash or terminal-control command.
Read-only research/decoded data stays in `E:/OOTRemake/work/r7-play-cs7f/`.

## Item 1: the three pull-back graves

Source observation: Kareem via Claude, 2026-11-08, Hookshot 2.0.1: from the Royal Family's Tomb,
fourth grave from the right is unmarked and contains a ReDead and chest; a marked grave has a cracked wall.
His graveyard loaded vanilla during the reported overlay gap; this is not a shuffled-chest acceptance result.

`graves.py` independently reads both ages' Static/Dynamic placements with the project's reader. Coordinates
are x/y/z, metres, y up. Stand at the Royal Family's Tomb entrance (48.4,104.6,2.6), **face out over the
graveyard**, not toward the tomb. Kareem's shield-grave observation calibrates right-to-left as increasing z:

| Grave | Where from that viewpoint | Surface hole (child Hash) | Underground |
|---|---|---|---|
| ReDead / shield | Nearest row of seven; fourth from right, unmarked | (21.47,103,11.2), `13042589291289571846` | ReDead `17994273783244561622`; chest `16912540161937823130` (38.3,86.3,11.2) |
| Heart-piece chest | Same seven-grave row; leftmost, seventh from right | (21.39,103,23.15), `14989078271173641200` | Chest `9622128545943056087` (21.4,85.8,39.3); no enemy/song puzzle |
| Marked fairy grave | Lower row of five (farther from tomb); second from right, flowers/butterflies | (4,101.5,5.75), `11636637601453373828` | `WallCrack` `9366825990748670811` (3.94,83.92,27); passage to pool around (-21,84,34), **eight `Obj_Fairy`, no chest/check** |

The last two ordinals are placement-derived, not new gameplay observations. Both chest catalogue rows now
use this single viewpoint. The fairy-only grave is explained as a non-check, not fabricated as a catalogue
location or added to the pool. Reviewer follow-up explicitly requests a separate `Graveyard Fairy Grave`
region: implemented below rather than retaining the translated N64 Shield Grave fairy source.
Both chest identities and the item pool remain unchanged.
Heart chest remains `True` **inside** the grave. Both age Static copies have only
`Drop__DropActor=Obj_Heart_Piece` in Dynamic; no Presence, SpawnType override, links or AiGroup reference to
that chest in either age's pair. Native `SpawnType=0`; no Sun's Song, wall or clear trigger binds it. The only
wall AI group binds the fairy wall: `Graveyard_Common_8f81`, death -> 60-frame timer -> riddle sound,
not chest creation. Child entrance still requires night plus `Time Flows`; no adult requirement was added.
Shield combat and all other access rules are unchanged.

Guide corroboration (facts only):
https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2 (#8),
https://www.ign.com/wikis/ocarina-of-time-remake/Spiritual_Stone_of_Fire_-_Kakariko_Village_Walkthrough .

### Diagnostics

- First probe used `str(U64)` for reference comparison. Printed `U64(7)`, `int=7`, `isinstance(int)=True`:
  typed numbers' repr is not decimal. Normalize to builtin numbers; the corrected probe finds the wall group
  and no chest group. No absence conclusion was retained from the faulty comparison.
- External GPL `ainb` 0.2.16 failed decoding the chest expression string pool: `ParseWarning.__init__`
  missing `msg`. Printed the signature `(reader, msg)`, failing call and 22,242-byte chest header.
  Upstream `main/ainb/utils.py` removes that erroneous duplicate-string warning call. Installed **unmodified
  0.2.17 in a new external venv only**, and the cause-aimed decode passed (two chest graphs). No GPL code,
  dependency or decoded tree enters the repository; no NX2navi code/docs read.
- `uv pip index versions ainb` is unsupported (exit 2, printed command usage); used PyPI's JSON release metadata
  instead. No unchanged command retry.

Full gates will run on the final tree before any commit is posted ready. Targeted/runtime results follow.

### Item 1 checks

`uv run pytest tests/test_world_remake_play.py -k grave -q`: **2 passed, 21 deselected**.
Scoped ruff format/lint passed. Actual full-world `load_world`/`Search` plus catalogue reader smoke:
child with Gohma exit and `Time Flows`, no weapon/song/bombs, reaches the heart chest but not the
guarded shield chest. Rendered both player directions. No in-game observation is claimed.

### Reviewer follow-up: split N64's combined grave

Claude supplied N64 comparison facts from
https://www.zeldadungeon.net/wiki/Graveyard_(Ocarina_of_Time) : its flower-marked shield grave combines
the shield chest and the bombable fairy wall, and its heart chest needs Sun's Song. Direct fetch here
returned HTTP 403; citation/facts are reviewer-supplied, not a claimed successful web read.
The remake placements above confirm the split: ReDead/shield at x21.5/z11.2, fairy wall under the
marked grave at x4/z5.7, heart chest at x21.4/z23.2 without the old song trigger.

Added `Graveyard Fairy Grave` with its own night/time-flow child entrance and unrestricted return.
Disabled the translated Shield Grave Fairy event (`was` guards the old rule); new fairy event needs
`has_explosives and has_bottle`, not an unverified Hammer alternative. No shuffled check added.

First targeted follow-up: 4 passed, 2 failed because the full-world searches escaped into unrelated
fairy sources. Printed successful event sources: adult HF/ZR fairy grottos; child several overworld
sources after acquiring implicit drops. Isolated the three real graves' graph by excluding the
surface's exits to other areas in the test fixture, leaving actual grave/event rules intact.
This fixes the test's scope, not a production gate. Cause-aimed rerun:
`uv run pytest tests/test_world_remake_play.py -k grave -q`: **6 passed, 21 deselected**;
scoped ruff format/lint passed. Full-world runtime smoke was already exercised above; the new source's
explosive/bottle and Hammer-negative behavior is exercised by these searches.

## Item 2: bombs cancel because lifting strength is missing

Read-only samples: newest 7c `user-seed-shop-7c/save/5a3c9e1f0b7d24680000000000000001/slot_00/progress.sav`;
main backup `E:/OOTRemake/work/save-backups/2026-11-08_2140-main-jabu`, newest slot selected by mtime.
`bombs.py` records exact paths and SHA-256s in `bomb-save-comparison.json` outside the repo.
`bomb_gate.py` re-read these samples: main digest unchanged; live 7c digest changed during play, but every
diagnostic field below retained its reported value. No claim that the live save stayed byte-identical.

| GameDataList name | Type | 7c | main |
|---|---|---|---|
| `IsGet.Item_Bomb` | Bool | true | true |
| `IsGet.Item_BombBag_Small` | Bool | true | true |
| `PouchData.Item_BombBag_Small.StockNum` | Int | 1 | 1 |
| `PouchContentMaxNum.Bomb` | Int | 20 | 20 |
| `PouchData.Item_Bomb.StockNum` | Int | 20 | 8 |
| `HavePlayedGetEvent.Item_BombBag_Small` | Bool | false | true |
| `IsGet.Armor_Child_Gauntlet_Goron` | Bool | false | true |
| `PouchData.Armor_Child_Gauntlet_Goron.StockNum` | Int | 0 | 1 |
| `PlayerStatus.LiftGrade` | Enum | `None` (3069107721) | `Low` (3655598229) |

Names are validated against GameDataList, not guessed from arbitrary save bytes. `PlayerStatus` Struct
hash `0x060890b0` maps field `LiftGrade` (`0x377c9cdd`) to Enum `PlayerStatus.LiftGrade` (`0x59979321`);
its declared order is None, Low, Middle, High. `save.TYPES` resolves the Enum section.
An early diagnostic used `Item_Gauntlet` / `Armor_Child_Goron`: neither is the actual saved armor name;
their absent values were not interpreted as false. Exact armor name and actual grade resolve the gate.

### Native action, not the get-animation flag

Read only the game's own guest `E:/Games/Hookshot/.hookshot_exefs/main`, build e0f3ccfa; no NX2navi
code/docs or port implementation. External `nso.py`/`locate.py` use permissively licensed Capstone to
disassemble its uncompressed AArch64 text. `Player.action.prelift.module` uses `SelectorPlayerPreLift`.
Its native action initializes the selected item, then `0x027e2c50` calls `0x02e50760`; that calls
`0x02e50570`. At `0x02e50694` the object-required lift grade is obtained; virtual slot +0x100 obtains
the player's maximum. `0x02e506ac..b0` returns required <= available. Player override `0x02e878d0`
reads precisely the PlayerStatus/LiftGrade struct field and maps None/Low/Middle/High to 0/1/2/3,
capped by the actor's maximum. Failure marks the pre-lift action finished at `0x027e2d94`.

`Pack/Actor/Item_Bomb.pack.zs`, `Component/LiftableParam/Item_Bomb.game__component__LiftableParam.bgyml`:
required grade Low. **7c's None cannot hold the spawned bomb; main's Low can.** Equipping and briefly
raising a bomb therefore does not prove it is usable. The different `HavePlayedGetEvent` is presentation
history, not evidence of an additional bomb-use gate; do not "repair" it.

`Item_BombBag_Small` expands Item_Bomb and Item_Bombchu capacity to 20; its expansion resource has no
LiftGrade grant. The native Bracelet rows `Item_Gauntlet_Goron` / `Armor_Child_Gauntlet_Goron` instead
declare `ExpansionAvility=LiftGradeUP`, `LiftableGrade=Low`, special deal GoronGauntlet.
**[INFERENCE] Getting the real KF Storms Grotto Bomb Bag alone will NOT fix this cancellation while
strength remains None. Getting Goron's Bracelet should.** The save is not shown corrupted or permanently
without bombs; it lacks a vanilla ability. This expectation still needs Kareem's in-game confirmation.

### Pre-D25 7b/7c: keep playing via Bombchus, not a forced restart

Reviewer-supplied gameplay fact: Kareem used Bombchus on main without owning a Bomb Bag.
Independent metadata: Item_Bombchu's own LiftableParam requires **None**, unlike Item_Bomb's Low.
Its SmallBagActor points to the small Bomb Bag, but that is a container link, not a prerequisite to hold it.

Read back 7b's **written** Goron shop pack, not just the spoiler: GC Shop Item 8 replaces vanilla
Shop_BombBundle_04 with **Shop_BombchuBundle_05**, PriceOffset35, StockNum -1 (repeatable native sale).
PouchActorInfo identifies the actor as five Item_Bombchu. It uses the normal ShopItem purchase path,
not a chest get or synthetic grant; section 24 records no explicit bag/Dodongo check for this branch.
7c and 7b's 228 placements compare exactly equal. No active output was rebuilt or edited.

`old_seed.py` replays those exact 228 shuffled placements with current remake rules and data-derived fixed
vanilla items (Chest/Shop only, no new fill). Baseline **won=True**, 25 spheres, 1307 collected.
GC8 Bombchus arrive at sphere 4; Windmill/Storms at 9; KF Storms Grotto Bomb Bag at 10.
Removing GC8 only: **won=False**, no Time Travel, no logical bag, 334 collected, 8 spheres; removing
all bomb/Bombchu ammo likewise stalls. This confirms the hint's pre-bag dependency **in this logic**,
not a claim that every possible in-game route needs GC8. Buy refills alone do not grant the default
free-drop logical Bombchu capability. Old native pack bag grants can supply extra in-game routes.
The child-only proof gets vanilla Saria's Song at sphere 3, vanilla Darunia's Goron Bracelet and GC8
at sphere 4, reaches the pull, and does not reach the Storms bag. No adult find supplied that prefix.

**Continuation:** buy the five-Bombchu offer at Goron City's shop and use those for early explosives.
Also learn Saria's Song and play it for Darunia to get the unshuffled Bracelet: this seed shuffles only
chests/shops. Then try the already-equipped bombs again; do not wait for Storms to fix strength.
Repeat purchases allow replenishment, subject to native rupees/capacity. The fixed route replay plus
Kareem's no-bag Bombchu observation supports continuing 7b/7c, not discarding these saves.

Diagnostic correction: the first replay printed `Search.holds("Bomb Bag")=False` even after collecting
bags; `holds` queries events only. Printed actual bag spheres exposed it; corrected diagnostic reads
the item count (baseline 3, stalled scenarios 0). Distinct scenario filenames now preserve both reports.
No search or production gate was changed to obtain this result.

### Proposed follow-up, not an unauthorized save/game patch

Conservative future-logic fix: ordinary usable bombs must require the real bag **and** the appropriate
lifting strength; keep Bombchus separate. The shared bomb helper is outside this track's owned files:
request posted to reviewer rather than silently changing it. Alternative: deliberately lower only the
spawned ordinary Item_Bomb's requirement to None, without weakening bomb flowers; that changes gameplay
and needs an owner decision and a separate isolated test. Neither a history-flag edit nor granting a
Bracelet with an ammo pack is justified. D25 bag-placement policy remains unchanged.

**Kareem: on 7c, buy/use GC8 Bombchus before any real bag; then obtain Darunia's Bracelet and retry
the same equipped bombs. Expected: Bombchus work immediately; bombs stop canceling after Bracelet.
Please also report whether the real bag was acquired before that comparison.**
No game was launched here; no in-game acceptance result is claimed.

Checks: `uv run python E:/OOTRemake/work/r7-play-cs7f/bomb_gate.py` and `old_seed.py` produced the
metadata/save/route results above. Native address probes are recorded by the helpers in that directory.

## Item 3: owned Hylian Shield selects the grave's explicit red-rupee substitute

Both Child and Adult Dynamic files configure chest Hash 16912540161937823130, `Obj_TBox_A_06`, with
`Drop__CheckActor=TBox_Shield_Hylian`, `Drop__DropActor=TBox_Shield_Hylian`,
`Drop__DropActor_Substitute=TBox_Rupee_Red`. Its native Drop_TreasureBox_A_06 blackboard defaults
`Drop__CheckCondition=true`; neither placement overrides it.

Decoded native A_06 root graph: node16 queries pouch count of CheckActorName; node30 evaluates 0<count;
node29 XORs that with CheckCondition. Nodes24/25 select main content when true and substitute when false.
Consequently stock0 gives shield; stock1 gives the configured substitute. PouchActorInfo defines
TBox_Rupee_Red as 20 of Obj_Rupee_Green. This exactly explains Kareem's reported **20 rupees while vanilla
graveyard files were loaded**, without inventing a different grave or a shuffled reward.
The substitution is this instance's data, **not a universal "every duplicate chest item gives 20" rule**.
Owning the shield and having opened this chest are different state.

The randomizer already handles this: `patch/write.py:patch_tree` sets both primary and substitute to
the shuffled actor whenever a substitute or CheckActor exists. It retains the check actor but either
branch now gives the intended shuffled item. No implementation change is needed.

`uv run python E:/OOTRemake/work/r7-play-cs7f/shield_probe.py` reads both real placement files,
evaluates the decoded condition for pouch counts0/1, and invokes the actual `patch_tree` in memory:
both ages choose shield/red rupee before patch, and Item_Boomerang/Item_Boomerang after patch.
It asserts both shuffled branches and prints the red-rupee count20. No output under the dump was written.
This is a data/patch-path smoke, not an invented in-game play result; Kareem's vanilla observation is
the gameplay evidence. Existing `test_owned_item_substitute_cannot_replace_a_shuffled_reward` covers
the synthetic writer regression and will run in the full gates.
