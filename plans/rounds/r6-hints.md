# Round 6, track C: text and Gossip Stones (cs6c)

Branch `r6/hints`, from main `57c2a57`. Owns `src/clawshot/formats/msbt.py`, `src/clawshot/census/hints.py`,
`src/clawshot/patch/text.py`, `tests/test_msbt*.py`, `tests/test_hints*.py`, this file and section 22 of
`plans/03-game-data.md`. Scratch scripts and decoded data: `E:/OOTRemake/work/r6-hints/` (outside the repo).

| Item | Where | Commit |
|---|---|---|
| 1 `formats/msbt` | `src/clawshot/formats/msbt.py`, `tests/test_msbt.py`, `tests/test_msbt_dump.py` | 2272d6a |
| 2 Gossip Stone census, other hint givers | `src/clawshot/census/hints.py`, `tests/test_hints.py`, `tests/test_hints_dump.py`, section 22 | a14aed7 |
| 3 item-get text and model; naming an item in a line; stones without the mask | `src/clawshot/patch/text.py`, `src/clawshot/census/hints.py` (`flow_path`), `tests/test_hints_text.py`, `tests/test_hints_text_dump.py`, section 22 | ddbb286 |
| 4 test output `gossip-kf-line`, hint design note; `msbt.normalized` and `text.keep_style` (needed by the test) | `E:/OOTRemake/work/r6-hints/ingame/`, `src/clawshot/formats/msbt.py`, `src/clawshot/patch/text.py`, tests, this file, section 22 | (this commit) |

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
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump tests/test_hints_dump.py -s` | 4 passed: 41 census entries (40 stones: the Lost Woods bridge stone is also in the Kokiri Forest files), 40 labels, every entry in `STONE_LINKS` and back, 36 linked + 4 missing = OoT Randomizer's 40; every label in `GossipStone.msbt` of all 16 languages; the gates are exactly Mask of Truth held (Event112, case 0) and worn (Event25, case 0); every hint giver's flow shows its labels and every language has them |

Provisional (for review): the order inside the Deku Tree pair, the SFM maze pair, the three Lake Hylia stones and the
four Temple of Time stones (labels only: each group is one OoT Randomizer region), and the east Hyrule Field grotto
as "Southeast" rather than "Near Market". **Kareem, when convenient (low priority): at the Temple of Time's four
stones, which label (01-04) is the far left when facing the temple?** The test output in item 4 can answer it for one
stone.

Finding for the logic (round 4's `child_*` files, no owner this round; not changed): the Zora's River storms grotto
holds a talking stone (`GOSSIP_LOST_WOOD_01`), so its `Fairy` event could use `can_summon_gossip_fairy`; and the
Kakariko beehive grotto stone is a gossip fairy OoT Randomizer does not model. Stricter as it is; nothing breaks.

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
Truth?** OoT Randomizer's default is that stones always speak (`hints = Combobox(default='always', ...)`,
`SettingsList.py:3696` at `526b4c8d`; `mask` and `agony` are its other choices); the patch above does that.

## Item 4: in-game test and the hint design note

### The test output (`E:/OOTRemake/work/r6-hints/ingame/`)

Built by `E:/OOTRemake/work/r6-hints/make_test.py` through `clawshot.patch.text` and the seed writer
(`clawshot.patch.write` with an empty chest plan), so the files are what a seed step would write:

| File | Change | Size (decompressed) | Size entry |
|---|---|---|---|
| `Event/EventFlow/GossipStone.bfevfl.zs` | Event112 and Event25 send every answer on (no Mask of Truth needed) | 93,400 -> 93,400 | 93,680, unchanged |
| `Mals/USen.Product.110.sarc.zs` | `GossipStone.msbt`: `GOSSIP_KOKIRI_FOREST_01` a custom line naming the Boomerang through `item_name` (USen `Item_Boomerang` key); every other stone label "Clawshot test stone" and its label; each line keeps the stone's opening style tags | 2,373,416 -> 2,371,192 | 2,373,752, unchanged |

The size table is not written (no entry had to grow). The launcher `Test - gossip-kf-line.bat` was copied from
round 5's `Test - chest-ocarina-storms.bat`: it starts `E:\Games\Hookshot\hookshot.exe` only, with `HOS_FS_OVERLAY` at
`gossip-kf-line\romfs` and its own empty user folder `user-gossip-kf-line`, the log to
`gossip-kf-line\hookshot_log.txt`. Not run by me (checked by reading it). Only the English (US) archive is changed:
Kareem's game runs `en-US` (`oe: language en-US` in round 5's logs), which is `USen` [inference from the name].

**What Kareem should do and see** (a new game; nothing else is changed, so the intro plays as usual):

1. Run `E:\OOTRemake\work\r6-hints\ingame\Test - gossip-kf-line.bat` and start a **new game**.
2. Once Link can move, go up to the **Lost Woods entrance** (the tunnel on the high ground of Kokiri Forest, near
   Mido's house). The Gossip Stone stands about 18 m from the tunnel's mouth, next to where the Song of Storms grotto
   opens (placement `GOSSIP_KOKIRI_FOREST_01`, Hash 15788731894432615343 child).
3. Talk to it **without the Mask of Truth**. Expected: the stone speaks (not Navi): first its own opener, which
   mentions a mask (the game's first-time lines `Talk_03` and `Talk_10`; expected), then **"Clawshot test: they say
   the Boomerang is hidden / somewhere in Kokiri Forest."** in the stone's usual colour and size, then one of its
   closing lines; Navi may show a small balloon the first time. Talk again: a shorter opener and the same line.
4. The log `gossip-kf-line\hookshot_log.txt` should show `fs: OpenFile(content:/Event/EventFlow/GossipStone.bfevfl.zs):
   from the overlay` and the same for `Mals/USen.Product.110.sarc.zs`.
5. **Report:** does the stone speak without the mask, is the line shown as written (two lines, the word Boomerang
   right), and does anything look wrong (text box, colour, a crash)? If the stone's text is unchanged but it speaks,
   the game reads another language archive: send the log's `oe: language` line.
6. Optional, if you get past Mido in this test: the two stones in front of the Deku Tree say "Clawshot test stone"
   and their label: **which label is on the left as you face the Deku Tree?** (it settles OoT Randomizer's "Left" and
   "Right" names; `STONE_LINKS` guesses `GOSSIP_KOKIRI_FOREST_03` is the left one).

### Design note: hints in round 7

OoT Randomizer's hints (`Hints.py`, `HintList.py`, default distribution `balanced`, at `526b4c8d`) and how each fits:

| OoT Randomizer hint | Fits the remake? | Needs |
|---|---|---|
| Way of the Hero (an area holds a required item), barren ("foolish") areas | yes | the world's region `hint` areas are already ported (`04-world-format.md`); the search's required-item set |
| item (where an item is), `always` and `sometimes` location hints | yes | location names a player understands (track A's names this round) |
| dual, goal (path to a boss) | later | the same, plus goal sets |
| entrance hints | no | no entrance shuffle |
| junk | yes | lines Clawshot writes (no copied text) |
| Skulltula House rewards (10 to 50) | yes | rewrite `Npc_SkullDad` `Talk_28`/`_23`-`_26` to name the reward (`item_name`) |
| Dampé's diary (Hookshot) | yes | rewrite `Diary_Hylia_Dampe_Adult` `Talk_03`; Sheik's `Talk_01`/`Talk_03` are a second Hookshot slot |
| Temple of Time altar (stones, medallions), Ganondorf (Light Arrows) | not yet | the altar text is a cutscene (`Dm_TimeTemple_0020`), Ganondorf's not traced |
| frogs, Big Poes, Deku Theater, warp songs | later | each NPC's lines traced like the Skulltula House |

What round 7 needs: (1) **stones as hint locations in the world**: OoT Randomizer's `HintStone` locations (its
regions and rules, e.g. `DMC Gossip Stone` asks `has_explosives`, `HC Storms Grotto Gossip Stone` `can_blast_or_smash`)
are dropped by the translator today; keep them as a non-item kind, linked through `STONE_LINKS`, and give the four
remake-only stones regions and rules by hand, so a hint is placed only on a stone reachable where it matters
(OoT Randomizer's rule). (2) **One label per stone**: 40 stones, 40 labels, so one hint per label; the Lost Woods
bridge stone's second census entry (the Kokiri Forest files' copy) is the same stone. (3) **Text**: one hint per stone
label via `edit_messages`, item names through `item_name` per language and area names from the hint areas (English,
unless Kareem decides otherwise; the remake's `LocationMsg/Location.msbt` holds the game's own area names per language,
an option); `keep_style` keeps the stone's look. (4) **Settings**: `hints` (`always` with `gossip_without_mask`, or
`mask` as vanilla) and the distribution, through track B's settings string. (5) A `make_seed` extra step returning the
archive and flow transforms, the hints in the spoiler, and a dump test that every hint names a placed item at a
reachable stone.

## Questions for Kareem

1. **`gossip-kf-line`** (item 4): does the Kokiri Forest stone by the Lost Woods entrance speak without the Mask of
   Truth and show the Clawshot line naming the Boomerang? Optionally: which Deku Tree stone label is on the left?
2. **Languages:** should a seed's hint text cover every language archive (English text in all of them) or only the
   English ones?
3. **Mask of Truth:** should stones speak without it (OoT Randomizer's default) or need it, as vanilla?
4. Low priority: at the Temple of Time's four stones, which label (01-04) is the far left facing the temple?

## Left for later

- Hints themselves (round 7, design note above): stones as world locations, hint selection, the seed step.
- The Temple of Time altar (a cutscene's text) and Ganondorf's line are not traced; the frogs, Big Poes and Deku
  Theater lines as hint slots are not traced.
- Renaming a stone's placement `Name` is untested (not needed now: one label per stone).
- Naming an item at run time through a String64 variable and a group 2 type 3 tag (mechanism (b), section 22) is
  described, not implemented or tested.

## Cross-track posts (thread `cs-r6`)

- None needed during the round: no other track's file was changed. Handoff post below.

## Gates (on b4059e9, base main `57c2a57`)

```
uv run ruff format --check                                  150 files already formatted
uv run ruff check                                           All checks passed!
uv run pytest                                               411 passed, 55 skipped
OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump      54 passed, 412 deselected
```

## Handoff

Commits on `r6/hints` (not rebased; main has not moved for this track): `2272d6a` item 1 (MSBT), `a14aed7` item 2
(Gossip Stone census, hint givers), `ddbb286` item 3 (text patches, item-get text and model), `b4059e9` item 4 (test
output, design note, `msbt.normalized`, `text.keep_style`), then this round-file commit. Section 22 of
`03-game-data.md` is appended after section 19; sections 20 and 21 (tracks A and B) are not on main yet, so on a rebase
it moves after them. Left: the in-game check (Kareem), the product questions above, and round 7's hints.
