# Round 1, track A: formats and the chest swap (`r1/formats`, agent cs1a)

## What is built

### Items 1-3 (early slice)

- **uv project** `clawshot` (`pyproject.toml`, `.python-version` 3.12, `uv.lock`), `src/` layout, hatchling build.
  Runtime dependency: `zstandard` (BSD-3-Clause). Dev group: `pytest`, `ruff` (both MIT). Ruff: line length 120,
  rules `E F W I B UP SIM`.
- **`dump` marker** (`tests/conftest.py`): tests marked `dump` are skipped when `OOT_ROMFS` is unset; the `romfs`
  fixture gives the dump root as a `Path`.
- **`clawshot.formats.sarc`**: SARC reader (`read(bytes) -> {name: bytes}`) and writer (`write(files, alignment)`),
  little-endian only. Needed to open the dictionary pack; the writer builds synthetic packs for tests.
- **`clawshot.formats.zsdic`**: `Dictionaries.from_romfs(romfs)` / `.from_pack(bytes)`;
  `.decompress(name, data)` and `.compress(name, data, level=19)` pick the dictionary from the file name
  (`dictionary_for`), and `decompress` checks it against the dictionary ID in the zstd frame header.
- **`clawshot.formats.byml`**: BYML v7 reader (`read`) and writer (`write`), with exact node types (table in the
  module docstring): `I32 U32 I64 U64 F32 F64` are `int`/`float` subclasses, `Hash32Map`/`Hash64Map` are `dict`
  subclasses; `str`, `bool`, `None`, `list`, `dict` map directly. `difference(a, b)` / `same(a, b)` compare trees
  with types (`==` alone treats `I32(1)` and `U32(1)` as equal).

### Item 4: round trip of every placement file

`tests/test_byml_dump.py::test_dump_every_placement_file_round_trips`: **160 of 160** `Banc/**/*.bcett.byml.zs`
files read, write and read back to the same tree, and **all 160 are byte-identical** to the decompressed original,
so there is no first difference to report. The test asserts byte identity, and prints the first differing offset
for any file that stops matching.

### Item 5: `python -m clawshot.tools.swap_chest`

`src/clawshot/tools/swap_chest.py`, as specified (`--romfs --out --file --hash --item`). It sets
`Dynamic.Drop__DropActor` of the one actor with that `Hash`, keeps everything else (including `GetEventName`), and
writes `<out>/romfs/<file>` with the same dictionary and byte order. It refuses: an output folder inside the romfs,
a `--file` that is not a romfs-relative `.bcett.byml.zs`, a Hash that matches no actor or several, an actor without
`Dynamic.Drop__DropActor`, and an item with no `Pack/Actor/<item>.pack.zs` in the romfs (a typo guard).
Synthetic tests in `tests/test_swap_chest.py` (fake romfs built in the test).

Outputs, written outside the repo (`E:/OOTRemake/work/r1-formats/`), each changing only
`romfs/Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs`:

| Output | Chest (Hash) | Vanilla | New | SHA-256 of the file |
|---|---|---|---|---|
| `out-red` | 10831981390482426294 | `TBox_Rupee_Green` | `TBox_Rupee_Red` | `8a71116f…0c1fcc` |
| `out-boomerang` | 12786193094758345086 | `TBox_Rupee_Blue` | `Item_Boomerang` | `ebb196b5…78b961` |
| `out-boomerang-samesize` (spare, see item 6) | 10831981390482426294 | `TBox_Rupee_Green` | `Item_Boomerang` | `d4a34ea9…65ea5e2` |

Each output was read back and compared with the original tree actor by actor: exactly one field differs
(`/Actors/37/Dynamic/Drop__DropActor` for the green chest, `/Actors/40/...` for the blue one), the frame names
dictionary 3, and rerunning the tool gives the same bytes.

**How the chests were identified.** `KokiriForest_Child_Dynamic` has six chests with `Drop__DropActor`. Four of
them (`Obj_TBox_A_01`, all with `GetEventName: KokiriForest_TreasureBox_NaviChatOff`) stand within 5 m of each
other at height 112.3, among `Land_Kokiri_Interior_*` props, with a message board (`Obj_Kokiri_MessageBoard_A_02`,
message `KokiriForest_021`) beside them and a door (`Obj_Kokiri_Door_A_02`) 8 m away; they hold one green and three
blue rupees. That is the N64 game's Mido's house (four chests, the only Kokiri house with chests), so I take it to
be Mido's house; I have not seen it in game. Layout seen from the door: the four chests form a shallow arc, the
two middle chests about a metre further back than the outer two. **The red-rupee chest is the middle chest that
held the green rupee; the boomerang chest is the other middle chest.** The same four chests (same Hashes) are in
`KokiriForest_Adult_Dynamic`, which these outputs leave alone, so adult Link would find the vanilla rupees.
The other two chests in the file were not used: the Kokiri Sword chest (`Obj_TBox_A_02`) carries the event
`Get_StoneOfForest_GetSword`, and a purple-rupee chest at (-132, 124, -16) sits by cliffs in a place I could not
name.

### Item 6: sizes and the resource size table

| Output | Decompressed | Compressed |
|---|---|---|
| original | 510,884 | 192,909 |
| `out-red` | 510,884 (+0) | 190,435 |
| `out-boomerang` | 510,924 (+40) | 190,321 |
| `out-boomerang-samesize` | 510,884 (+0) | 190,443 |

(Our level-19 frames are smaller than the game's; only the decompressed size matters for the table below.)

`out-boomerang` grows because the three blue chests shared one `Dynamic` map (now split: +20 bytes) and
`Item_Boomerang` is a new string (+20 with its offset and padding). `out-red` and the spare don't grow: the green
chest's map was its own and its old string drops out.

**RSDB/** (20 `*.rstbl.byml.zs` tables) holds **no size entry** for placement files: none of the 19 tables I could
read mentions `KokiriForest_Child_Dynamic`, and their only size-like columns are heap sizes (`ActorInfo`:
`InstanceHeapSize`, `PreActorRenderInfoHeapSize`; `UIScreen`: `HeapInitialSize`). `Tag.Product.111` could not be
read: it uses node type 0xA1 (binary data), which the reader does not support yet.

**The resource size table is elsewhere**, as in Tears of the Kingdom:
`System/Resource/ResourceSizeTable.Product.111.Nin_Ounce_NVN2.rsizetable.zs` (plain zstd, `RESTBL` version 1,
219,968 CRC32 entries sorted by CRC, 10 named entries with a 160-byte name field). It **has an entry for all 160
placement files**, keyed by the CRC32 of the romfs path without `.zs`
(`Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml` -> 511,176). Over the 160 files, entry minus
decompressed size is always 264-292 and fits `entry = align_up(size, 32) + 264` exactly.

So `out-red` (and the spare) stay within the entry. `out-boomerang` (510,924 bytes) is still smaller than the
entry (511,176), but by that formula it would need 511,208: 32 more than the table gives. If the game sizes its
buffer from the entry and needs about 264 bytes beyond the file, `out-boomerang` is 12 bytes short. Whether that
fails is for the in-game check; if `out-boomerang` fails and `out-boomerang-samesize` works, the size entry is the
likely cause and a writer for the table is needed before any seed grows a file.

### Item 7: big-endian BYML (reviewer's addition)

`GameData/GameDataList.Product.110.byml.zs` is big-endian (magic `BY`, 1,462,888 bytes; node types C0 C1 A0 D0
D1 D2 D3 D4 D5). `byml.read` takes either byte order; `byml.write(root, "little" | "big")`; `byml.load(data)`
returns `Document(root, byte_order)` and `byml.dump(document)` writes it in that order. Big-endian layout is the
same as little-endian with every number swapped; a node header is the type byte then a 24-bit count, a map entry
a 24-bit key index then the type byte. `test_dump_game_data_list_round_trips`: **tree equal and byte-identical**.

The first attempt was 8 bytes short: the game keeps `int64 0` and `uint64 0` as two 8-byte values. Shared 8-byte
values are now keyed by type and bytes (this replaces my provisional "shared by bytes whatever the type"); the 160
placement files stay byte-identical.

## Findings

### Dictionaries (`Pack/ZsDic.pack.zs`)

Plain zstd frame (no dictionary, content size recorded, no checksum) around a SARC of four 128 KiB dictionaries.
Dictionary IDs, read from each dictionary's header and checked by `test_dump_dictionaries`:

| Dictionary | ID |
|---|---|
| `zs.zsdic` | 1 |
| `bkprb.zsdic` | 2 |
| `bcett.byml.zsdic` | 3 |
| `pack.zsdic` | 4 |

Which dictionary each `.zs` file uses, from the frame headers of all 102,185 `.zs` files in the dump (encoded in
`zsdic.dictionary_for`; `test_dump_every_zs_frame_names_the_dictionary_its_name_calls_for` checks every file):

| File names | Dictionary |
|---|---|
| `*.bcett.byml.zs` (placements) | `bcett.byml.zsdic` |
| `*.pack.zs`, except `Pack/ZsDic.pack.zs` | `pack.zsdic` |
| `*.bkprb.zs` | `bkprb.zsdic` |
| `Pack/ZsDic.pack.zs`, `*.bntx.zs`, `*.bcul.zs`, `*.bars.zs`, `RSDB/*.rstbl.byml.zs`, `*.atbl.byml.zs`, `*.HeapDef.byml.zs`, `*.rsizetable.zs` | none (plain zstd) |
| every other `.zs` (event flows, `GameData`, `Mals/*.sarc.zs`, models, ...) | `zs.zsdic` |

### BYML layout of the placement files

Found by walking `KokiriForest_Child_Dynamic` node by node (script in `E:/OOTRemake/work/r1-formats/`), then
confirmed by the writer reproducing all 160 placement files byte for byte:

- 16-byte header (`YB`, version 7, key table, string table, root offset), then the key table at 0x10, then the
  string table; both sorted by UTF-8 bytes, `n + 1` offsets (the last is the end of the last string), padded to 4.
- Then every 8-byte value (u64 here: each actor's `Hash`), each distinct (type, value) once, in depth-first order
  of first use. An actor's `Hash` and its `Phive.Placement.ID` share one value.
- Then the containers: the root first, each container followed by its child containers, depth first. A container
  equal to one already written (same types and values) is not written again: in that file 141 `Rotate`, 42
  `Scale`, 23 `Translate` arrays and 17 `Dynamic`/`Presence` maps are shared.
- No padding at the end of the file.

## How it was checked

On the branch, last run after commit `b0089f7`:

| Command | Result |
|---|---|
| `uv run ruff format --check` | 21 files already formatted |
| `uv run ruff check` | All checks passed |
| `uv run pytest` (no `OOT_ROMFS`) | 53 passed, 5 skipped |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` | 5 passed (37 s): dictionary IDs; 160 placement files decompress; every `.zs` frame's dictionary matches its name; 160/160 placement files byte-identical; GameDataList byte-identical |

Scratch scripts for the findings (layout walk, dictionary scan, chest listing, size table) are in
`E:/OOTRemake/work/r1-formats/`, outside the repo.

## What Kareem should do in game (Claude sets `HOS_FS_OVERLAY`)

For each output in turn, `HOS_FS_OVERLAY=E:/OOTRemake/work/r1-formats/<output>/romfs`, then start a new game (or a
child save that has not opened the four chests in Mido's house) and go into Mido's house, the Kokiri house with
four small chests:

1. The game log shows `fs: OpenFile(...KokiriForest_Child_Dynamic.bcett.byml.zs...): from the overlay`.
2. `out-red`: open the two middle chests (about a metre further back than the outer two). One gives a **Red
   Rupee (20)** instead of the Green Rupee; the other three chests give Blue Rupees as before.
3. `out-boomerang`: open the middle chests. The one that is not the green-rupee chest gives the **Boomerang**
   (and Link can equip it); the green chest still gives a Green Rupee.
4. Only if step 3 fails (no Boomerang, a crash, or the area does not load): try `out-boomerang-samesize`, where
   the green-rupee chest gives the Boomerang. Working there and not in step 3 points at the size table (item 6).

Also worth noting: whether the Boomerang plays its item-get message and model from a plain chest. Vanilla
major-item chests carry a `GetEventName` (the Boomerang's is `InsideJabuJabuBelly_TreasureBoxWithRuto09`); ours
keeps the chest's own `KokiriForest_TreasureBox_NaviChatOff`.

## What is left

- The in-game check of item 5 (above).
- A writer for the resource size table, if the in-game check shows growth matters (not done: the spec says
  don't change it yet).
- BYML node type 0xA1 (binary data, in `RSDB/Tag.Product.111`) is not supported.

## Provisional choices

- **Decompression checks the name against the frame**: `decompress(name, data)` raises if the frame's dictionary
  ID is not the one the name calls for, rather than silently using the frame's.
- **Compression**: level 19, content size in the frame, dictionary ID in the frame, no checksum (as the game's
  files are). The compressed bytes will not match the game's (its encoder and level are unknown); only the
  decompressed bytes are compared.
- **Plain `int`/`float`** in a tree to be written become int32/float32; anything else must use the typed classes.
- **Maps compare as unordered** in `difference`, since the writer sorts entries by key (the game looks keys up by
  binary search).
- Node types 0xA1/0xA2 (binary data) are not read or written: they don't occur in placement files or GameDataList;
  the reader names the type when it meets one.
- **`swap_chest` checks the item name** against `Pack/Actor/<item>.pack.zs` in the romfs. Every chest item I used
  has one; if some valid drop actor turns out to have no pack of its own, that check will need to change.
- **A spare output** (`out-boomerang-samesize`) beyond the two the spec asks for, so a failed Boomerang check can
  tell the size table apart from the item itself.

## Questions for Kareem

- **None blocking.** After the in-game check: if the Boomerang from a plain chest shows no item-get message or
  the wrong model, should seeds also rewrite `GetEventName` to the item's own event (a product call on how
  faithful item gets must be)? Track B's question 3 covers what these events do.
