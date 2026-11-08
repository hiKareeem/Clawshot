# Round 6, track C: text and Gossip Stones (cs6c)

Branch `r6/hints`, from main `57c2a57`. Owns `src/clawshot/formats/msbt.py`, `src/clawshot/census/hints.py`,
`src/clawshot/patch/text.py`, `tests/test_msbt*.py`, `tests/test_hints*.py`, this file and section 22 of
`plans/03-game-data.md`. Scratch scripts and decoded data: `E:/OOTRemake/work/r6-hints/` (outside the repo).

| Item | Where | Commit |
|---|---|---|
| 1 `formats/msbt` | `src/clawshot/formats/msbt.py`, `tests/test_msbt.py`, `tests/test_msbt_dump.py` | 2272d6a |
| 2 Gossip Stone census, other hint givers | `src/clawshot/census/hints.py`, `tests/test_hints.py`, `tests/test_hints_dump.py`, section 22 | a14aed7 |
| 3 item-get text and model; naming an item in a line; stones without the mask | `src/clawshot/patch/text.py`, `src/clawshot/census/hints.py` (`flow_path`), `tests/test_hints_text.py`, `tests/test_hints_text_dump.py`, section 22 | (this commit) |

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

## Item 2: Gossip Stones and the other hint givers (`clawshot.census.hints`)

The facts are in section 22. How they were found (scratch scripts in `E:/OOTRemake/work/r6-hints/`, `uv run python ...`
from this worktree; `lib.py` caches decoded placements and text under `cache/`, outside the repo):

- `explore` of every `Banc` actor name for stones, signs, owls (one-off), then `stone_context.py` (the actors within
  25 m of each stone) and `grotto_link.py` (grotto exits, rooms and covers near each stone); covers and chests by
  `Hash` against round 4's grotto rows (`r4-logic-child.md`).
- `lib.show_flow('GossipStone')` printed the flow; the instance-name talk step was found by `talk_survey.py`, which
  lists every talk action in every flow (only `GossipStone`, signs, `RestrictedDoor` and Pierre pick text by instance
  name) and writes each flow's message ids to `flow_messages.json`.
- The text of `GossipStone.msbt`, `Npc_SkullDad.msbt`, the diaries, Sheik and Kaepora (USen) was read locally to know
  which line is which; nothing of it is in the repo.
- OoT Randomizer's `HintStone`s and their regions: `LocationList.py` and `data/World/*.json` at `526b4c8d`
  (`E:/OOTRemake/work/r2-world/OoT-Randomizer`).

What the module gives: `scan_stones(banc)` / `read_stones(romfs)` (41 `GossipStone`s: area, label, position, both
copies' file and `Hash`, ages, presence flags), `talk_gates(flowchart)` (the switches every path to the stone's line
passes, with their case) and `needs_mask_of_truth`, `read_flow` (the flow file the game loads, through the census's
versions list), `STONE_LINKS` (each stone to an OoT Randomizer stone or `None`, with its evidence),
`OOTR_STONES_MISSING`, and `HINT_GIVERS` (flow, message file, labels).

Checks:

| Command | Result |
|---|---|
| `uv run pytest tests/test_hints.py` | 7 passed: age copies merged, a label shared by two areas kept as two stones, unnamed silent stones and `DreamWorld` left out; one label at two places in an area and a talking stone without a name refused; gates are only the switches every path passes (a random branch both ways is not one), with and without the equip gate; a flow that never reaches the line refused; no OoT Randomizer stone linked twice |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_hints_dump.py -s` | 4 passed: 41 stones, 40 labels, every stone in `STONE_LINKS` and back, 36 linked + 4 missing = OoT Randomizer's 40; every label in `GossipStone.msbt` of all 16 languages; the gates are exactly Mask of Truth held (Event112, case 0) and worn (Event25, case 0); every hint giver's flow shows its labels and every language has them |

Provisional (for review): the order inside the Deku Tree pair, the SFM maze pair, the three Lake Hylia stones and the
four Temple of Time stones (labels only: each group is one OoT Randomizer region), and the east Hyrule Field grotto
as "Southeast" rather than "Near Market". **Kareem, when convenient (low priority): at the Temple of Time's four
stones, which label (01-04) is the far left when facing the temple?** The test output in item 4 can answer it for one
stone.

Finding for the logic (round 4's `child_*` files, no owner this round; not changed): the Zora's River storms grotto
holds a talking stone (`GOSSIP_LOST_WOOD_01`), so its `Fairy` event could use `can_summon_gossip_fairy`; and the
Kokiri Forest stone by the stick-bag scrub and the Kakariko beehive grotto stone are gossip fairies OoT Randomizer
does not model. Stricter as it is; nothing breaks.

## Item 3: item-get text and model (`clawshot.patch.text`)

Facts in section 22, "Item-get text and model". Found with `lib.show_flow('GetPouchContent', ...)` (the chest and gift
entries, `OpenGetWindow`, `DefaultGetMessage`), the run-time tag survey (every group 2 tag's type and game-data name
over all messages), `models.py` (each pouch actor's `ModelInfo` and whether it has get texts) and `actornames.py` (each
pouch actor's `ActorName` component against the `PouchContent` labels), all in `E:/OOTRemake/work/r6-hints/`; the
setter of the scrubs' name variables by a scan of every flow's `String64` actions.

`clawshot.patch.text`: `edit_messages(edits)` (the transform of one language archive replacing named messages; it
refuses a missing file or label and reads back the archive and each changed file), `item_name(pouch_text, key)` (an
item's name parts in one language), `text_key(pack, actor)` / `read_text_key(romfs, actor)` (the `ActorName` key),
`languages(romfs)`, `archive_path(language)`, `gossip_without_mask(flowchart)` and `gossip_flow_transform(data)` (the
stones speak without the Mask of Truth). The transforms fit `clawshot.patch.write`'s `FileChanges`, so a later hint
step is one `make_seed` extra step (round 5's interface).

Checks:

| Command | Result |
|---|---|
| `uv run pytest tests/test_hints_text.py` | 7 passed: one message replaced, the other file and messages untouched, bucket count kept; a missing file or label refused; an item name keeps its grammar tag, an unknown item refused; the text key from `ActorNameRef`, through a parent, and the actor's own name without one; the mask questions re-pointed so no gate is left; a flow without them refused |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_hints_text_dump.py -s` | 3 passed: the `GossipStone` flow changes only Event112 and Event25 (actors and entry points equal, no mask gate left; 93,400 bytes before and after, entry 93,680); one stone line in `USen` changes only that message of that file (2,373,416 -> 2,373,288 bytes, entry 2,373,752); all 106 `item_actors.toml` actors have a name and get text under their `ActorName` key in all 16 languages |

**Product questions for Kareem (and his co-owner), in bold: which languages should a seed's custom text cover?**
Hint lines are new text, so they exist only in the languages Clawshot writes; English-only (written into every
language archive, or only `USen`/`EUen`) is the simplest. And: **should Gossip Stones speak without the Mask of
Truth?** OoT Randomizer's default is that stones always speak (its `hints` setting; the Mask of Truth is an option);
the patch above does that.
