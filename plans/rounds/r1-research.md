# Round 1, track B: game-data research (cs1b)

Branch `r1/research`, rebased on main `fa37c50` when the reviewer said track A had landed. Findings are in
`plans/03-game-data.md`; this file says how they were checked, what I chose provisionally, and what is open.

## What was built (outside the repo)

All in `E:/OOTRemake/work/r1-research/`; nothing decoded is in the repo.

| File | What |
|---|---|
| `lib.py` | romfs loader: `clawshot.formats.zsdic` for zstd, `clawshot.formats.byml` for `YB`, `byml_any.py` for `BY` |
| `byml_any.py` | BYML v7 reader for both byte orders (a scratch copy of the spike reader with the byte order made a parameter) |
| `r1_numbers.py` | recomputes the headline numbers of sections 1, 2, 3, 6 and 7 |
| `LocationList.py` | OoT Randomizer `Dev` at `526b4c8d81b7c4023ef4573ffbaf39344e270d5b` (MIT), for section 9 |
| `decoded/` | `banc_all.json`, `evfl_all.json` (914 flows via zeldamods `evfl` 1.3.0, GPL, unmodified, in `.venv` here), `gamedatalist.json` |

Sections 4, 5, 8 and 9 were worked out interactively over those decoded files; each claim in `03-game-data.md`
names the flow, event, actor or flag it rests on, so it can be re-checked by reading that one thing. Claims I could
not confirm from data are marked [inference].

## Checks run

- `uv run python E:/OOTRemake/work/r1-research/r1_numbers.py` from the worktree (clawshot.formats on main
  `fa37c50`): 160 Banc files, 120834 actors; 267 `Obj_TBox*` placements, 232 unique; 194 chests, 32 pedestals,
  6 traps; 41 placements without `Drop__DropActor` = 32 pedestals + 6 traps + 3 chests; chest and trap hashes with a
  `Bool64bitKey` flag 200 of 200; Gold Skulltulas 100, all with a flag; `GetEventName` values 36, all rows of
  `RSDB/EventSetting`; RESTBL v1 with 219968 CRC entries and 10 named; for all 160 Banc files
  entry − ceil32(decompressed size) = 264; 20 RSDB tables. The same numbers came out of the spike reader earlier.
- Flag hashing: murmur3_x86_32 seed 0 of 2565 `GameDataName` strings from event flows, 2540 found in
  `GameDataList` (the 25 misses include the empty string; not chased). `HavePlayedEvent.<row>` found for 2380 of
  2380 EventSetting rows.
- OoT Randomizer comparison: Gold Skulltulas per area equal in all 31 areas (100 = 100), which is also the check
  that the area mapping in section 9 is right.
- Track A's gates are not touched by this branch (docs only).

## Provisional choices (Claude or Kareem to confirm)

- Pedestals (`Obj_TBoxPedestal_*`) and trap chests (`Obj_TBox_A_04`) are not counted as chests; `DreamWorld`
  chests are listed but left out of the OoT Randomizer comparison.
- OoT Randomizer areas map onto Banc folders as in section 9 (Lon Lon Ranch and Lake Hylia under `HyruleField`,
  Temple of Time under `Market`, Ganon's Tower under `InsideGanonCastle`, Thieves' Hideout under `GerudoFortress`).
- For a changed chest, keep story `GetEventName` overrides (Kokiri Sword, Iron Boots → Serenade, Silver Gauntlets →
  Nabooru, Gold Gauntlets) and consider dropping the Navi-only ones, whose line names the vanilla item. Not
  implemented; a choice for the patch plan.

## Questions for Kareem and the co-owner (product calls)

- **Trap chests: the six N64 Ice Trap chests are trap chests here and hold no item. Leave them out of the shuffle,
  or turn them into normal chests (a different actor, needs an in-game test)?**
- **Cows have no per-cow save flag here (milk sets global flags only). Leave cows out of data-only seeds?**
- **Remake-only content: shuffle the extra overworld and dungeon chests (mostly rupees and
  `Item_ScrubBusinessSeed`)? Leave `DreamWorld` out (its inventory is temporary)? Is `Item_ScrubBusinessSeed` part
  of the item pool?**
- **Chest appearance: the big/small chest is the actor (`A_01` vs `A_02`), so "chest size matches contents" means
  swapping the actor. Wanted for M2, or later?**

## In-game looks that would settle open points (optional, not blocking)

1. Death Mountain Trail Great Fairy (summit, after bombing the wall): the data says this fountain is
   `Dm_FairyFountain_Din`, so she should give **Din's Fire**, not the magic meter as on N64. Kareem: if a save has
   been there, which spell did she give?
2. A chest with no `Drop__DropActor` should give a green rupee (the chest default). The earliest one is in the Forest
   Temple (room 24); low priority.

## Cross-track posts (thread `cs-r1`)

- 14:53: for track A item 6: the size table is `System/Resource/ResourceSizeTable...rsizetable.zs`, not RSDB;
  every placement file has an entry, entry = ceil32(size) + 264; `GameDataList` is big-endian BYML.
- 15:02: `clawshot.formats.byml` reads only little-endian, so the M1 census needs a big-endian reader for
  `GameDataList`.

## Left for round 2

- Match every chest here to an OoT Randomizer location by room and position (census), and the same for event
  gifts; section 9 gives counts and the known differences only.
- Decode the chest AI (`AI/Obj_TBox_*.root.ainb`) to confirm the `DefaultDropActorName` and
  `Drop__CheckActor`/`Substitute` behaviour, and how the actor passes its item to the open event.
- The 7971 `Bool64bitKey` keys that match no Banc `Hash`; what triggers each Great Fairy event; scrub and shop
  sale flags.
