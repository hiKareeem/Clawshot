"""A hint as a Gossip Stone's line (``clawshot.patch.text``): wrapped to the stone's box in its own style."""

import pytest

from clawshot.formats import msbt, sarc
from clawshot.formats.msbt import Msbt, Tag
from clawshot.generate.hints import FIELD_END, FIELD_START
from clawshot.patch import text
from clawshot.patch.plan import PatchError

COLOUR = Tag(0, 3, b"\x01\x00")
SIZE = Tag(0, 2, b"P\x00")
VOICE = Tag(3, 0, b"\x0f\x00\x00")
ORIGINAL = [COLOUR, SIZE, VOICE, "an old rumor", Tag(0, 4), "more"]


def test_a_short_line_keeps_the_stone_style_and_colours_the_names():
    line = text.stone_line(
        ORIGINAL, f"They say {FIELD_START}Lake Hylia{FIELD_END} hides the {FIELD_START}Bow{FIELD_END}."
    )
    # A name ends as the game's own highlights end, with colour ff ff, not by naming the stone's 01 00 again: that
    # left the rest of the line highlighted in game (seed-shop-7c).
    highlight, back = Tag(0, 3, b"\x00\x00"), Tag(0, 3, b"\xff\xff")
    assert line == [
        COLOUR,
        SIZE,
        VOICE,
        "They say ",
        highlight,
        "Lake Hylia",
        back,
        " hides the ",
        highlight,
        "Bow",
        back,
        ".",
    ]


def test_a_long_line_breaks_into_rows_and_pages_without_splitting_words():
    words = " ".join(f"word{i:02}" for i in range(40))  # 40 words of 6 characters: 279 characters
    line = text.stone_line(ORIGINAL, words, width=30, rows=2)
    assert len(msbt.plain(line).split("\n")[0]) == 27  # four words a row
    # a page break after every second row, reopening the size and colour (not the voice)
    breaks = [i for i, part in enumerate(line) if part == text.PAGE_BREAK]
    assert len(breaks) == 4
    for i in breaks:
        assert line[i + 1 : i + 3] == [COLOUR, SIZE]
    rows = [row for chunk in line if isinstance(chunk, str) for row in chunk.split("\n") if row]
    assert " ".join(rows) == words
    assert max(map(len, rows)) <= 30


def _archive(labels):
    stone = Msbt({label: [COLOUR, SIZE, f"old {label}"] for label in labels}, buckets=3)
    return sarc.write(
        {"EventFlowMsg/GossipStone.msbt": msbt.write(stone), "Other.msbt": msbt.write(Msbt({"A": ["a"]}, buckets=1))}
    )


def test_the_archive_transform_changes_only_the_hinted_stones():
    data = _archive(["GOSSIP_A", "GOSSIP_B"])
    out = sarc.read(text.stone_lines_transform({"GOSSIP_A": "They say nothing."})(data))
    messages = msbt.read(out["EventFlowMsg/GossipStone.msbt"]).messages
    assert messages["GOSSIP_A"] == [COLOUR, SIZE, "They say nothing."]
    assert messages["GOSSIP_B"] == [COLOUR, SIZE, "old GOSSIP_B"]
    assert out["Other.msbt"] == sarc.read(data)["Other.msbt"]


def test_a_label_the_archive_lacks_is_refused():
    with pytest.raises(PatchError, match="GOSSIP_C"):
        text.stone_lines_transform({"GOSSIP_C": "x"})(_archive(["GOSSIP_A"]))
