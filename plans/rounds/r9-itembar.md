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
