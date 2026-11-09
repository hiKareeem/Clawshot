# Round 9, Track A: item bar and age-locked items (cs9a)

Branch `r9/itembar`. Read the supplied AGENTS rules, README, plans00–04, decisions and all round7/8
reports; Round9's shared-file opening applies. No game, batch, GUI, build, terminal-control command,
save/dump mutation, dependency edit, merge, push or stash. External read-only research and decoded data:
`E:/OOTRemake/work/r9-itembar-cs9a/`. Initial tasklist found no Hookshot; work remains single-process.

## Item 1: get, saved selection and age filtering

Build `e0f3ccfa`. Ran `probe.py`, `contracts.py` and `details.py` against the actual dump and the supplied
read-only bow-lock backup. Native probes (`native.py`, `snapshot.py`, `sync.py`) read only the game's own
`.hookshot_exefs/main`; permissive Capstone was supplied with ephemeral `uv run --with capstone`, not
added to the project. No NX2navi code/docs or GPL implementation was read or copied.

### Established contracts

- Chest identity is `Dynamic.Drop__DropActor` -> `ContentName` -> `GetPouchContent`'s actor argument.
  `GetPouchContent/Event0` already gives with **`IsEquipDIrect=False`**. Turning this off again is not a fix.
  Display binding, get text and grant remain distinct (sections19/26/33); no presentation edit is justified.
- `RSDB/PouchActorInfo.Product.111.rstbl.byml.zs` maps pouch actors to `AssignableItem`: Bow, SlingShot,
  Boomerang, Hammer, Hookshot, Longshot, etc. `Item_Range_Bow` resolves to `Weapon_Range_Bow`; its actual
  saved ownership is `IsGet.Weapon_Range_Bow` / `PouchData.Weapon_Range_Bow.StockNum`, not Item_Range_Bow.
- `UI/Pouch/PouchTable/PouchTable.game__ui__PouchTable.bgyml` defines the pause cells and each variant's
  **`ActorShort`, `PouchActorShort`, `IsUsableChild`, `IsUsableAdult`**. Missing age fields are false in the
  native default (native property reader `0x033a25a0..0x033a2660`); this is not N64's age table.
- Native get code `0x01110158..0x01110198` reads current age/selection and calls selection setter
  `0x01211c00` when the current selection is empty or the new category permits it. That path is independent
  of the flow's direct-equipment flag. The setter writes the selected AssignableItem enum through GameData
  (`0x01211dc8..0x01211e58`). **[INFERENCE]** This out-of-age selection is the get-side mismatch in the
  reported lock; no live engine watchpoint was used and the exact item-use cancellation predicate is unproved.
- The native item-list/age readers use the PouchTable child/adult fields (e.g. `0x00a6ef20`,
  `0x033a5b40..0x033a5cc4`, `0x033a7fd4..0x033a80d4`). Saved selection is not the whole live bar.
  Kareem's observed Save/Continue removes Bow while keeping ownership; loading zones do not repair it.
  **The precise boot caller that reconstructs the live ZR bar has not been identified.** The observed reload
  repair plus these age readers support a load-time age-filtered rebuild, not a proven refresh API.
- All shipped active-flow action tables were enumerated. No explicit item-bar rebuild/clear action was found.
  The tempting `UISystemActor.EventTriggerSyncPlayerEquipmentAndPouch` is **not** such a contract:
  native `OneShotSyncPlayerEquipmentAndPouch` execute `0x02951f50` calls `0x00f201b0` to reapply wearable
  equipment. Its name is not evidence that it rebuilds the selectable bar. Changing age usability globally
  would allow unsupported actions instead of repairing assignment. Removing AssignableItem would also remove
  legitimate menu selection. Neither experiment is shipped as a default-on fix.

Reviewer-relayed gameplay evidence (`answers.md`, R9-LICHII): Kareem reproduced the seed8
item-bar lock in **Lichii**, obtaining Bow before Boomerang; Save and Continue cleared it.
This establishes the game's own behaviour, not a Hookshot-specific defect. This is Kareem's
observed emulator result, not an agent-run check; no code or policy change follows.

### Read-only save evidence

All six `progress.sav` slots have `Sequence_IsChildhood=true`, Bow acquired and Bow stock1. Slots01–04
retain Bow (`1399920009`) in enum `0xa0029837`; slots00/05 instead contain Boomerang there. The other saved
assignable enums are `0x6bee602d` and `0xbc32ce24`, reset8/save0. The fourth field cited by sloperina,
`0x76f85e6d`, is **save-1** in the real GameDataList and absent in every supplied progress save; it is not a
missing/corrupt saved button. The backup does not label a controlled before/after reload pair, so none is claimed.

Facts-only external lead: [sloperina docs/FINDINGS.md sections1,2,5.6](https://github.com/PracticeROM/sloperina/blob/master/docs/FINDINGS.md)
names the four enum hashes, PouchTable and the wheel's separate live copy. Independently verified the enums,
layout and saved values above against the player's dump. No sloperina code/file is in this repository.

### Every ordinary button-item family

Usability below is the remake's **PouchTable metadata**, not a new gameplay test. Inventory/quest/passive
items are not item-bar buttons merely because their get window appears. Additional native action prerequisites
(magic, ammunition, bomb lifting, scene restrictions) still apply. Equipment/head/boot shortcuts are separated
from the ZR items; raw metadata does not certify adult mask use.

| Family / native identity | Usable age in the table |
|---|---|
| Deku Stick / Item_DekuStick | Child |
| Fairy Slingshot / Weapon_Range_SlingShot | Child |
| Boomerang / Item_Boomerang | Child |
| Deku Nuts / Item_DekuNut | Both |
| Bombs / Item_Bomb | Both (bag and lift strength still required) |
| Bombchus / Item_Bombchu | Both |
| Megaton Hammer / Item_Hammer | Adult |
| Hookshot, Longshot / Item_Hookshot, Item_Longshot | Adult |
| Bow, normal arrows / Weapon_Range_Bow, Item_Arrow_Normal | Adult |
| Fire, Ice, Light Arrows / Item_Arrow_Fire, Item_Arrow_Ice, Item_Arrow_Light | Adult |
| Magic Bean / Item_MagicBean | Child |
| Din's Fire, Farore's Wind, Nayru's Love | Both |
| Five bottle positions: empty, Big Poe, Blue Fire, Blue/Green/Red Potion, Bug, Fairy, Fish, Half Milk, Letter, Milk, Poe | Both |
| Business Scrub Seed / Item_ScrubBusinessSeed | Both |
| Pocket Egg/Cucco, Cojiro, Odd Mushroom/Potion, Poacher's Saw, Broken Sword, Prescription, Eyeball Frog, Eyedrops, Claim Check | Adult |
| Weird Egg, Chicken (Item_AlarmCucco), Zelda's Letter | Child (D31 shared trade cell) |
| Amiibo / Pouch_Amiibo | Both |
| Fairy Ocarina / Item_Ocarina_Fairy (separate ocarina shortcut) | Child |
| Ocarina of Time / Item_Ocarina_Time (separate ocarina shortcut) | Both |
| Lens of Truth / Armor_GlassTruth (equipment shortcut) | Both |
| Iron/Hover Boots / Armor_Adult_HeavyBoot, Armor_Adult_HoverBoot (boot shortcuts) | Adult |
| Eight ordinary masks, two Amiibo masks (head shortcut) | Both in metadata; adult action support is not proved |
| Fishing rod, normal/sinking lure | Scene/minigame buttons; no PouchTable ItemArray age entry, so no invented age classification |

No ages are changed in the world. The table deliberately does not broaden the existing logic's mask policy.

### Diagnostics

Initial save probe printed absent `IsGet.Item_Range_Bow` and an absent `Sequence_IsChild`; the real pouch row
and section19 establish Weapon_Range_Bow and `Sequence_IsChildhood`. Printed corrected values above, not false
ownership. A scratch edit response exposed a displaced loop; reread and repaired it before execution. Native
pointer-reference lookup for sync names returned no results; ADRP/ADD string references located the RTTI getter,
then its vtable/execute entry instead. No failed command was repeated unchanged. LSP status: marksman only,
no Python language server.

## Item 2: conditional data fix

No supported data-only fix established. Native get assignment and the bar's separate live state cannot safely
be repaired by flipping the already-false direct-equip flag, mutating wearable equipment, or enabling child Bow
use. Therefore item2's conditional patch/setting/player-overlay branch is **not taken**. Item3's specified
fallback follows; no setting or gameplay patch is silently substituted.

**Kareem: the adult Slingshot/Boomerang case is not yet observed. On an isolated save/seed copy, acquire one
as adult, note whether it appears greyed on ZR and whether adult items stop working, then Save and Continue.
Report both the bar and actual item use before/after; a zone transition alone is not the recovery step.**
This is a pending reverse-direction gameplay check, not an agent-run reproduction.

Item2 checkpoint: no `patch/itembar.py`, dependency, saved layout, age permission, setting or experimental
default is introduced. No speculative patched player overlay/launcher is produced. The conditional outcome
is explicit rather than calling an unobserved refresh a fix. Item1 source checkpoint: `486f832`.

## Item 3: specified fallback and owner choices

Implemented a sourced `data/itembar.toml` age catalogue and `generate/itembar.py` warning analysis.
It replays **complete existing sphere prefixes**, including fixed rewards, through the existing Search.
Before collecting each next sphere it checks both ages at every pending shuffled age-locked destination.
An opposite-age first frontier is warned; ties also warn conditionally. Correct-age-first and unshuffled
destinations do not get rows. Pre-return child inventory never borrows adult finds; no area-name inference,
assumed future inventory, new RNG or second reachability engine.

The spoiler gets `age_locked_pickups` (world identity, item, usable age, first reachable ages, sphere).
The play note consumes that same snapshot before the opening route, with real catalogue directions.
It says to Save and Continue after an unusable-age pickup, distinguishes the observed child Bow lock from
precautions for the other families, and warns that optional later pickups can differ from oracle order.
Separate native ocarina/boot restrictions are precautionary rows too, not newly claimed ZR failures.
No native permission, fill, setting string, placement or RomFS resource changes.

### Proposals only — not built

| Option | Proposal | Cost / boundary |
|---|---|---|
| Get text | Append an original line to relevant item-get notices: “If Link cannot use this item at his current age, Save and Continue before using other items.” | Requires traced per-item MSBT labels and all16 language archives (D26), pagination checks and a player text check. Without an age-conditional flow, correct-age pickups see the conditional warning too. It informs, not repairs, and would also affect native grants of that item. |
| Fill setting | Optional `age_locked_items = matching_age_only`; leave current unrestricted placements as the default until approved. Restrict the actual fixed button item to checks physically unavailable to the other age, not just earlier in one oracle witness. | Far fewer eligible checks and less variety; dual-age chests would be excluded for either one-age family. Own-dungeon/return-kit/type-held capacities may become impossible; reject rather than relax rules/retries. Needs audited physical age gates, all alternate-route tests, CS1/CLI integration and bounded fill measurements. A first-sphere-only filter is not safe: players may defer a shared chest until the other age. |

**Kareem/co-owner: keep note-only recovery, add the conditional get-text warning, or approve the strict
matching-age fill option?** Neither proposed feature is implemented or made a hidden default.

### Focused checks and diagnoses

Initial synthetic run printed `WorldError: ... no type`: the fixture omitted `[locations]` metadata.
Added actual Chest/vanilla declarations, not weaker production validation. Cause-aimed run:14 passed,
one parser failure, which printed trailing `Field |`; corrected the test's Markdown boundary stripping
to the existing presentation-test convention. Targeted corrected renderer case:1 passed/14 deselected.
Scoped ruff format unchanged; scoped ruff check passed. Full gates and actual CLI evidence follow.

### Actual seed8 surface / unchanged game resources

`uv run python -u E:/OOTRemake/work/r9-itembar-cs9a/smoke.py` invoked the real public CLI with
the **played seed8's exact CS1**, writing only fresh `seed8-warning-next` under this track's scratch.
Exit0: **287 shuffled locations,24 spheres**. Independently hashed both actual RomFS folders:
**129/129 resources byte-identical**, exact287-placement equality, original resource hash map
unchanged after the run. Only spoiler/note gain warning presentation. No new launcher/user folder.
Evidence retained: `seed8-cli.log`, `seed8-smoke-proof.json`, generated fresh note/spoiler/resources.

Read the actual written note:10 warning rows, starting with **Mido's house middle-left Bow**,
child-first/sphere1, matching Kareem's reported source. Other child-first rows: Hammer at the
memory game, Iron Boots in the shield grave, Claim Check at30 tokens, Odd Potion at Skull Kid,
Longshot in Dodongo's west alcove, Pocket Egg at the moat. Adult-first precautions: two Kakariko
potion shelves' sticks and the Ganon Light Trial sticks. No new gameplay result is inferred.
Removed only the completed session-created throwaway smoke driver after this proof; research
reproducers and the fresh review output remain external. Existing player folders were not rebuilt.

## Full gates and handoff

All four required gates ran in full, serially, with no source change during the run.
The reviewer-requested Lichii evidence was the only intervening documentation change.

| Command | Result |
|---|---|
| `uv run ruff format --check` | 227 files already formatted |
| `uv run ruff check` | All checks passed |
| `uv run pytest` (OOT_ROMFS unset) | 736 passed, 87 skipped; 462.04s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | 86 passed, 737 deselected; 847.14s |

Both pytest runs used separate session-created external `PYTEST_ADDOPTS=--basetemp=...`
folders under `E:/OOTRemake/work/r9-itembar-cs9a/`; no fixture data was written into the repo.
The new frontier/presentation tests passed (15 synthetic), and the native-age catalogue
oracle passed in the full dump run. Actual CLI/unchanged-resource proof is recorded above.
No game was started, no player output rebuilt, no save copy altered.

Branch `r9/itembar`, in order:

- `486f832` — item1 age table, assignment trace and section37.
- `a65af4e` — item2 unsupported data-fix boundary and reverse-age checklist.
- `5502718` — sourced native-age catalogue, first-frontier analysis and tests.
- `e05a45a` — isolated shared generator integration for spoiler/play-note warnings.
- `594432e` — seed8 replay proof, documentation and proposed owner choices.
- `4085413` — reviewer-relayed Lichii reproduction, documentation only.

The final handoff metadata commit follows these checkpoints; no merge or push was performed.
Shared edits for review: `generate/__init__.py`, README and section37 of `03-game-data.md`.
Preserve the other tracks' shared additions; the location catalogue is read dynamically,
so their floor-qualified names can flow into these warning rows at integration.

Remaining limits: the precise boot caller reconstructing the live ZR bar is unproved;
no supported data-only repair is claimed. Adult-first Slingshot/Boomerang gameplay remains
Kareem's isolated-copy check. Get-text and matching-age fill remain proposals awaiting
Kareem/co-owner approval, not shipped settings. The specified note-only fallback is implemented.

Thread-command diagnosis: `~/go/bin/bermuda` failed with exit127 because this host has
`C:/Users/hi/go/bin/bermuda.exe`, not an extensionless binary. Printed the installed filename
before using that exact executable; no unchanged retry.
