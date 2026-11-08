# Round 6, track C: text and Gossip Stones (cs6c)

Branch `r6/hints`, from main `57c2a57`. Owns `src/clawshot/formats/msbt.py`, `src/clawshot/census/hints.py`,
`src/clawshot/patch/text.py`, `tests/test_msbt*.py`, `tests/test_hints*.py`, this file and section 22 of
`plans/03-game-data.md`. Scratch scripts and decoded data: `E:/OOTRemake/work/r6-hints/` (outside the repo).

| Item | Where | Commit |
|---|---|---|
| 1 `formats/msbt` | `src/clawshot/formats/msbt.py`, `tests/test_msbt.py`, `tests/test_msbt_dump.py` | (this commit) |

## Item 1: `clawshot.formats.msbt`

Written from the files and the public description of MSBT v3 (https://nintendo-formats.com/libs/lms/msbt.html); round
4's scratch `msbt_dump.py` only for what the files are. No code from another implementation.

What the survey found (`E:/OOTRemake/work/r6-hints/explore_msbt.py`, `explore_msbt2.py`, `explore_sarc.py`, run with
`uv run python ...` from this worktree): `Mals/` holds 16 archives (one per language), each a SARC of 540 `.msbt` files
(`EventFlowMsg/<flow>.msbt`, `LayoutMsg/...`, `LocationMsg/Location.msbt`, ...), 8640 files and 338,208 messages in
all. Every file has the same shape: little-endian, UTF-8, version 3, exactly two sections `LBL1` then `TXT2` (no
`ATR1`, `TSY1`, `NLI1`), 0xAB padding to 16 bytes, labels in their hash bucket in ascending message index, one zero byte
ending each message and nothing after it, no message without a label. The reader accepts exactly that and raises
`MsbtError` naming what differs. Tags seen (group.type, count over all languages): 0.0-0.4 (the library's ruby, font,
size, colour, page break), 1.x, 2.x (2.x carry a game-data name, e.g. `Shop_SelectItemName`,
`UI_MessageTargetActorName`: values filled in at run time), 3.0, 4.0, 5.x, and 201.x (grammar: articles, gender, in the
European languages). Parameters are kept as bytes.

`clawshot.formats.sarc.write` (alignment 8, its default) writes each `Mals` archive back byte-identical.

Checks:

| Command | Result |
|---|---|
| `uv run pytest tests/test_msbt.py` | 14 passed: a file built byte by byte reads into the expected labels, text and tags and writes back identical; bucket entries follow the message index; a changed or added message reads back with the others intact; size and alignment; refusals (reserved bytes in text, UTF-16, a label in the wrong bucket, an unknown section, a tag running past its message) |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_msbt_dump.py -s` | 1 passed: 16 archives, 8640 message files, 338,208 messages, every file byte-identical after read and write; every archive byte-identical through `sarc` |
