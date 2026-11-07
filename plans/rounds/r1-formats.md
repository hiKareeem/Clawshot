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

### BYML layout of the placement files

Found by walking `KokiriForest_Child_Dynamic` node by node (script in `E:/OOTRemake/work/r1-formats/`), then
confirmed by the writer reproducing all 160 placement files byte for byte:

- 16-byte header (`YB`, version 7, key table, string table, root offset), then the key table at 0x10, then the
  string table; both sorted by UTF-8 bytes, `n + 1` offsets (the last is the end of the last string), padded to 4.
- Then every 8-byte value (u64 here: each actor's `Hash`), each distinct value once, in depth-first order of first
  use. An actor's `Hash` and its `Phive.Placement.ID` share one value.
- Then the containers: the root first, each container followed by its child containers, depth first. A container
  equal to one already written (same types and values) is not written again: in that file 141 `Rotate`, 42
  `Scale`, 23 `Translate` arrays and 17 `Dynamic`/`Presence` maps are shared.
- No padding at the end of the file.

## How it was checked

(filled in at the end of the round)

## Provisional choices

- **Dictionary by name**: `.bcett.byml.zs` -> `bcett.byml.zsdic`, `.pack.zs` -> `pack.zsdic`, `.bkprb.zs` ->
  `bkprb.zsdic`, any other `.zs` -> `zs.zsdic`, and `Pack/ZsDic.pack.zs` itself is plain zstd.
- **Compression**: level 19, content size in the frame, dictionary ID in the frame, no checksum (as the game's
  files are). The compressed bytes will not match the game's (its encoder and level are unknown); only the
  decompressed bytes are compared.
- **Plain `int`/`float`** in a tree to be written become int32/float32; anything else must use the typed classes.
- **Maps compare as unordered** in `difference`, since the writer sorts entries by key (the game looks keys up by
  binary search). Equal 8-byte values are shared by their bytes, whatever their type (int64 vs uint64): not seen
  in the dump, so untested against the game.
- Node types 0xA1/0xA2 (binary data) are not read or written: they don't occur in placement files; the reader
  names the type when it meets one.

## Questions for Kareem

(none yet)
