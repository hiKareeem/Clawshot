"""NPC lines that name a gift's item say the item given, by BBender's hand-read marks (spec event-items 1.4; plan
5.6; plans/event-items.md "Hand-read marks", 2026-11-27). Synthetic texts only."""

import re
from dataclasses import replace

import pytest

from clawshot.census import definitions
from clawshot.formats import msbt, sarc
from clawshot.formats.msbt import Tag
from clawshot.generate.rewards import catalog
from clawshot.patch import event_lines, gifts, talon, text
from clawshot.patch.event_lines import Line, Marks
from clawshot.patch.plan import PatchError

COLOUR, RESET = Tag(0, 3, b"\x00\x00"), Tag(0, 3, b"\xff\xff")
GENDER = Tag(201, 0, b"\x03\x02\x02\x01")
FILE = "EventFlowMsg/Npc_Test.msbt"


def form_tag(*forms: str) -> Tag:
    data = b"".join(len(f.encode()).to_bytes(2, "little") + f.encode() for f in forms)
    return Tag(201, 10, data)


def test_the_raw_text_counts_a_declined_forms_tag_as_its_first_form_and_drops_other_tags():
    parts = ["Take my ", COLOUR, GENDER, form_tag("Tunic", "0", "Tunics"), RESET, "!"]
    assert event_lines.raw_text(parts) == "Take my Tunic!"
    assert event_lines.units(parts) == [(0, 0, 8), (3, 8, 13), (5, 13, 14)]
    assert event_lines.fingerprint(parts) == event_lines.fingerprint(["Take my Tunic!"])
    assert event_lines.fingerprint(parts) != event_lines.fingerprint(["Take my Tunic?"])
    assert re.fullmatch("[0-9a-f]{16}", event_lines.fingerprint(parts))


def test_a_span_read_on_the_collapsed_text_maps_back_to_the_raw_text_across_line_breaks():
    raw = "  Win a big\n  bag, a big bag!"
    assert event_lines.collapse(raw)[0] == "Win a big bag, a big bag!"
    assert event_lines.locate(raw, "big bag", 1) == (8, 9)  # "big\n  bag": the whole whitespace run
    assert raw[8:17] == "big\n  bag"
    assert event_lines.locate(raw, "big bag", 2) == (21, 7)
    assert event_lines.locate(raw, "big bag", 3) is None


def test_a_mark_in_one_text_part_is_replaced_by_the_given_name_and_the_tags_stay():
    parts = [COLOUR, "I'll give you a bigger quiver!"]
    assert event_lines.apply_marks(parts, [(16, 13, ["Piece of Heart"])]) == [COLOUR, "I'll give you a Piece of Heart!"]


def test_a_mark_across_a_highlight_puts_the_given_name_inside_it():
    parts = ["a bigger ", COLOUR, "quiver", RESET, "!"]
    assert event_lines.apply_marks(parts, [(2, 13, ["Heart"])]) == ["a ", COLOUR, "Heart", RESET, "!"]


def test_a_mark_on_a_declined_forms_tag_replaces_the_tag_and_its_gender_tag():
    parts = ["Ich gebe dir mein ", COLOUR, GENDER, form_tag("Goronengewand", "Goronengewandes"), RESET, "."]
    given = [Tag(201, 0, b"\x01\x00\x00\x01"), form_tag("Bumerang")]
    assert event_lines.apply_marks(parts, [(18, 13, given)]) == ["Ich gebe dir mein ", COLOUR, *given, RESET, "."]


def test_a_mark_starting_a_text_drops_the_gender_tag_before_it_but_not_one_before_other_text():
    gender = Tag(201, 0, b"\x01\x00\x00\x01")
    assert event_lines.apply_marks(["ma ", gender, "tunique goron !"], [(3, 13, [gender, "Boomerang"])]) == [
        "ma ",
        gender,
        "Boomerang !",
    ]
    assert event_lines.apply_marks(["ma ", gender, "belle tunique !"], [(9, 7, ["X"])]) == ["ma ", gender, "belle X !"]


def test_several_marks_are_replaced_right_to_left_even_when_they_touch():
    parts = ["Earn a Piece of Heart, then a Quiver", COLOUR, "Quiver", RESET]
    marks = [(7, 14, ["Bombs"]), (30, 6, ["A"]), (36, 6, ["B"])]
    assert event_lines.apply_marks(parts, marks) == ["Earn a Bombs, then a A", COLOUR, "B", RESET]
    assert event_lines.apply_marks(parts, list(reversed(marks))) == event_lines.apply_marks(parts, marks)


def test_overlapping_marks_and_a_mark_past_the_text_are_refused():
    with pytest.raises(PatchError, match="overlap"):
        event_lines.apply_marks(["abcdef"], [(0, 3, ["x"]), (2, 2, ["y"])])
    with pytest.raises(PatchError, match="outside"):
        event_lines.apply_marks(["abc"], [(2, 5, ["x"])])


# One line, two languages: English names the quiver in Talk_04; German uses a pronoun there, so its mark sits in the
# earlier box Talk_03 (BBender's rule), and Spanish names it nowhere.
TEXTS = {
    "USen": {"Talk_03": "Shoot well!", "Talk_04": "Here, a bigger quiver!"},
    "EUde": {"Talk_03": "Ein großer Köcher wartet!", "Talk_04": "Hier, nimm ihn!"},
    "EUes": {"Talk_03": "¡Dispara bien!", "Talk_04": "¡Toma tu premio!"},
}
GIVEN = {"USen": [COLOUR, "Piece of Heart", RESET], "EUde": ["Herzteil"], "EUes": ["Pieza de corazón"]}


def archive(language: str, texts: dict | None = None) -> bytes:
    pouch = msbt.Msbt({"Obj_Heart_Piece_Name": GIVEN[language]}, buckets=101)
    lines = msbt.Msbt(
        {k: [v] for k, v in (texts or TEXTS[language]).items()} | {"Talk_05": ["Untouched."]}, buckets=101
    )
    return sarc.write({text.POUCH_TEXT: msbt.write(pouch), FILE: msbt.write(lines)})


def line_for(label: str, language: str, span: str, check: str = "Kak Shooting Gallery Reward") -> Line:
    parts = [TEXTS[language][label]]
    at = event_lines.locate(event_lines.raw_text(parts), span, 1)
    return Line(check, "Item_Quiver_Medium", FILE, label, {language: Marks(event_lines.fingerprint(parts), (at,))})


EN = line_for("Talk_04", "USen", "bigger quiver")
DE = line_for("Talk_03", "EUde", "großer Köcher")
SWAPS = {(FILE, "Talk_04"): [(EN, "Obj_Heart_Piece")], (FILE, "Talk_03"): [(DE, "Obj_Heart_Piece")]}


def messages(data: bytes) -> dict:
    return msbt.read(sarc.read(data)[FILE]).messages


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("USen", {"Talk_03": ["Shoot well!"], "Talk_04": ["Here, a ", COLOUR, "Piece of Heart", RESET, "!"]}),
        ("EUde", {"Talk_03": ["Ein Herzteil wartet!"], "Talk_04": ["Hier, nimm ihn!"]}),
        ("EUes", {"Talk_03": ["¡Dispara bien!"], "Talk_04": ["¡Toma tu premio!"]}),
    ],
)
def test_each_language_replaces_its_own_marks_in_its_own_label_and_keeps_the_rest(language, expected):
    edited = messages(event_lines.archive_transform(language, SWAPS)(archive(language)))
    assert {k: edited[k] for k in expected} == expected
    assert edited["Talk_05"] == ["Untouched."]


def test_a_line_that_is_not_the_one_marked_is_refused_naming_file_label_and_language():
    changed = dict(TEXTS["USen"], Talk_04="Here, a larger quiver!")
    with pytest.raises(PatchError, match=r"Npc_Test\.msbt:Talk_04 USen: the line is not the one marked"):
        event_lines.archive_transform("USen", SWAPS)(archive("USen", changed))


def test_the_transform_is_deterministic():
    one = event_lines.archive_transform("USen", SWAPS)(archive("USen"))
    assert one == event_lines.archive_transform("USen", dict(reversed(list(SWAPS.items()))))(archive("USen"))


def test_the_same_words_marked_for_two_moved_checks_take_the_first_swaps_name():
    other = Line("Other", "Item_Quiver_Medium", FILE, "Talk_04", EN.marks)
    parts = [TEXTS["USen"]["Talk_04"]]
    assert event_lines.edit_line("USen", parts, [(EN, ["A"]), (other, ["B"])]) == ["Here, a A!"]
    assert event_lines.edit_line("EUde", parts, [(EN, ["A"])]) is None  # no marks in that language


def test_lines_of_checks_that_keep_their_vanilla_item_change_nothing_and_moved_ones_name_the_given_actor():
    assert event_lines.moved_lines([EN], {EN.check: "Quiver (40)"}, {EN.check: "Quiver (40)"}, str) == {}
    assert event_lines.moved_lines([EN], {}, {}, str) == {}
    moved = event_lines.moved_lines(
        [EN, DE], {EN.check: "Piece of Heart"}, {EN.check: "Quiver (40)"}, {"Piece of Heart": "Obj_Heart_Piece"}.get
    )
    assert moved == {(FILE, "Talk_04"): [(EN, "Obj_Heart_Piece")], (FILE, "Talk_03"): [(DE, "Obj_Heart_Piece")]}


def test_merchants_that_return_to_their_native_sale_keep_their_native_text():
    # Their shuffled first sale and their repeat sales speak the same messages (main's merchant sales).
    assert {*gifts.MERCHANT_SHOPS, gifts.GRANNY_CHECK} == event_lines.REPEAT_SALES
    for check in sorted(event_lines.REPEAT_SALES):
        line = replace(EN, check=check)
        assert event_lines.moved_lines([line], {check: "Piece of Heart"}, {check: "Bombchus (10)"}, str) == {}
    assert {line.check for line in event_lines.load()} >= event_lines.REPEAT_SALES


def test_talons_lines_are_left_to_main_s_talon_patch():
    # A moved prize: main rewrites his first-prize lines; his repeat prize and milk sale still give milk.
    assert {talon.CHECK} == event_lines.WRITTEN_ELSEWHERE
    line = replace(EN, check=talon.CHECK)
    assert (
        event_lines.moved_lines([line], {talon.CHECK: "Piece of Heart"}, {talon.CHECK: "Bottle with Milk"}, str) == {}
    )
    assert talon.CHECK in {line.check for line in event_lines.load()}


def test_the_data_format_is_read_and_checked():
    data = """
[[line]]
check = "C"
item = "Item_A|Item_B"
file = "F.msbt"
label = "L"
marks.USen = { fingerprint = "0123456789abcdef", at = [[9, 2], [0, 3]] }
"""
    (line,) = event_lines.loads(data)
    assert line.marks == {"USen": Marks("0123456789abcdef", ((0, 3), (9, 2)))}
    for bad in (
        data.replace("[[9, 2], [0, 3]]", "[[0, 3], [2, 2]]"),  # overlap
        data.replace("[[9, 2], [0, 3]]", "[[0, 0]]"),  # empty
        data.replace("0123456789abcdef", "0123"),  # short fingerprint
        data.replace('label = "L"\n', ""),
        data + data,  # twice for one check
    ):
        with pytest.raises(PatchError):
            event_lines.loads(bad)


def test_the_marks_data_holds_positions_only_for_known_checks():
    lines = event_lines.load()
    assert len(lines) == 166
    checks = set(gifts.load()) | set(catalog()["slots"]) | {d.name for d in definitions.load()}
    assert sorted({line.check for line in lines} - checks) == []
    keys = {(line.check, line.file, line.label) for line in lines}
    # Kept from the earlier lines, outside the reading (Claude, 2026-11-27, to confirm): Gohma's Key Items caption
    # (Q5) and Ruto's line (plan 10b).
    assert ("Queen Gohma", "LayoutMsg/ImportantMenu_01.msbt", "T_Message_00") in keys
    assert ("Barinade", "EventFlowMsg/Dm_InsideJabu_Jabu_0030.msbt", "Dm_InsideJabu_Jabu_0030_0019") in keys
    # BBender, final run 2026-11-28: the Great Fairies' lines that name the spell just given are replaced (F19, F25:
    # overrides Q8 and decision C for them); the castle fairy's line about strengthening the spin attack changes what
    # Link already has, so it stays (F18).
    assert ("DMT Great Fairy Reward", "EventFlowMsg/Dm_FairyFountain_Din.msbt", "Dm_FairyFountain_Din_0006_01") in keys
    assert (
        "ZF Great Fairy Reward",
        "EventFlowMsg/Dm_FairyFountain_Frore.msbt",
        "Dm_FairyFountain_Frore_0004_01",
    ) in keys
    assert (
        "Colossus Great Fairy Reward",
        "EventFlowMsg/Dm_FairyFountain_Nayru.msbt",
        "Dm_FairyFountain_Nayru_0004",
    ) in keys
    assert not any(label == "Dm_FairyFountain_Power_0004" for _, _, label in keys)
    # Dropped by decision D (a replacement shield, not the gift): the Kokiri shopkeeper's Talk_0102.
    assert not any(label == "Talk_0102" and "Kokiri_001" in file for _, file, label in keys)
    # No game text (AGENTS.md rule 1): every value is a name, a hex fingerprint or numbers.
    body = [s for s in event_lines.MARKS_TOML.read_text(encoding="utf-8").splitlines() if s and not s.startswith("#")]
    allowed = re.compile(
        r'\[\[line\]\]|(check|item|file|label) = "[^"]+"'
        r'|marks\.[A-Za-z]{4} = \{ fingerprint = "[0-9a-f]{16}", at = \[(\[\d+, \d+\](, )?)+\] \}'
    )
    assert [s for s in body if not allowed.fullmatch(s)] == []


def test_the_app_working_set_holds_every_given_actors_text_key_pack():
    from types import SimpleNamespace

    from clawshot.pack.source import resource_spec, working_files
    from clawshot.patch import items

    given = set(items.load().actors.values())
    inputs = set(event_lines.native_inputs(given))
    assert {text.ACTOR_PACK.format(actor=actor) for actor in given} <= inputs
    wanted = working_files(SimpleNamespace(files=[]), resource_spec())
    assert inputs <= wanted, sorted(inputs - wanted)
