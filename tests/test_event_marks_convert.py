"""The converter from the hand-read reading sheets to ``patch/event_marks.toml`` (tools/event_marks). Synthetic rows
and texts only."""

from clawshot.patch import event_lines
from tools.event_marks import convert

FILE = "EventFlowMsg/Npc_Test"


def test_sheet_check_names_split_into_the_checks_they_combine():
    assert convert.sheet_checks("A = Bigger Quiver | A = Biggest Quiver") == ["A"]
    assert convert.sheet_checks("Song from Windmill = Song of Storms") == ["Song from Windmill"]
    assert convert.sheet_checks("MiniGame_Frog Event162 / Event76 (Obj_Rupee_Blue)") == [
        "MiniGame_Frog Event162 (Obj_Rupee_Blue)",
        "MiniGame_Frog Event76 (Obj_Rupee_Blue)",
    ]
    assert convert.sheet_checks("Npc_X Event116 (Obj_A) | Npc_X Event117 (Obj_A)") == [
        "Npc_X Event116 (Obj_A)",
        "Npc_X Event117 (Obj_A)",
    ]


def test_a_census_name_maps_to_its_oot_randomizer_name_or_stays_and_an_unknown_one_maps_to_none():
    census = {"Flow Event1 (Obj_A)": "Some Check", "Flow Event2 (Obj_B)": ""}
    assert convert.resolve("Known", {"Known"}, census) == "Known"
    assert convert.resolve("Flow Event1 (Obj_A)", set(), census) == "Some Check"
    assert convert.resolve("Flow Event2 (Obj_B)", set(), census) == "Flow Event2 (Obj_B)"
    assert convert.resolve("Nobody", set(), census) is None


def row(check, lang, label, span, occurrence="1", note="", target=None):
    return {
        "group": "g01",
        "check": check,
        "actor": "Item_A / Item_B",
        "file": FILE,
        "en_label": label,
        "lang": lang,
        "target_label": target or label,
        "span": span,
        "occurrence": occurrence,
        "note": note,
    }


MESSAGES = {
    "USen": {FILE + ".msbt": {"T1": ["Win a big\nbag, a big bag!"], "T0": ["Hi."]}},
    "EUde": {FILE + ".msbt": {"T0": ["Eine Tasche wartet."], "T1": ["Nimm sie!"]}},
}


def test_rows_become_positions_and_fingerprints_with_counts_and_no_span_text():
    rows = [
        row("C", "USen", "T1", "big bag", "2"),
        row("C", "EUde", "T1", "Tasche", target="T0"),
        row("C", "EUde", "T1", "-", "", "COVERED BY T0"),
        row("C", "USen", "T0", "-", "", "NOT NAMED"),
    ]
    lines, counts, problems = convert.build(rows, MESSAGES, {"C"}, {})
    assert problems == []
    assert counts == {"rows": 4, "covered": 1, "not named": 1}
    raw = "Win a big\nbag, a big bag!"
    assert lines == [
        {
            "check": "C",
            "item": "Item_A|Item_B",
            "file": FILE + ".msbt",
            "label": "T0",
            "marks": {"EUde": {"fingerprint": event_lines.fingerprint(["Eine Tasche wartet."]), "at": [[5, 6]]}},
        },
        {
            "check": "C",
            "item": "Item_A|Item_B",
            "file": FILE + ".msbt",
            "label": "T1",
            "marks": {"USen": {"fingerprint": event_lines.fingerprint([raw]), "at": [[17, 7]]}},
        },
    ]
    written = convert.dumps(lines, counts)
    assert "big" not in written and "Tasche" not in written
    assert [line.marks for line in event_lines.loads(written)] == [
        {"EUde": event_lines.Marks(lines[0]["marks"]["EUde"]["fingerprint"], ((5, 6),))},
        {"USen": event_lines.Marks(lines[1]["marks"]["USen"]["fingerprint"], ((17, 7),))},
    ]


def test_unmapped_checks_missing_spans_and_overlaps_are_listed():
    rows = [
        row("Nobody", "USen", "T1", "big bag"),
        row("C", "USen", "T1", "small bag"),
        row("C", "USen", "T0", "Hi"),
        row("C", "USen", "T0", "i."),
        row("D", "USen", "T0", "Hi."),
    ]
    _, _, problems = convert.build(rows, MESSAGES, {"C", "D"}, {})
    assert len(problems) == 4, problems
    assert "maps to no check" in problems[0]
    assert any("not found" in p for p in problems)
    assert any("C): marks overlap" in p for p in problems)
    assert any("two checks' marks overlap" in p for p in problems)
