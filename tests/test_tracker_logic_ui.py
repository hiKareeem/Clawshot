"""The Tracker tab's in-logic display, age control and manual marks: the shipped tracker.js under Node."""

import pytest
from test_tracker_options import NODE, render_tracker

from clawshot.ui.server import ASSETS, STATIC

pytestmark = pytest.mark.skipif(NODE is None, reason="Node is needed only for frontend rendering tests")
AGE_KEY = "clawshot.tracker.age"


def check(check_id, collected, in_logic=None, *, marked=False):
    entry = {"id": check_id, "label": check_id, "where": "", "kind": "chest", "dungeon": None, "collected": collected}
    if in_logic is not None:
        entry["in_logic"] = dict(zip(("child", "adult", "either"), in_logic, strict=True))
    if marked:
        entry["marked"] = True
    return entry


def snapshot(*, available=True, reason=None, save_age="child", unknown_items=()):
    """Two areas: Field (child-only, adult-only, collected, marked) and Lake (one open check in logic for neither)."""
    field = [
        check("Child Chest", False, (True, False, True)),
        check("Adult Chest", None, (False, True, True)),
        check("Done Chest", True),
        check("Shop Item", None, marked=True),
    ]
    lake = [check("Far Chest", False, (False, False, False))]
    areas = [
        {"name": "Field", "collected": 1, "total": 4, "unknown": 2, "marked": 1, "checks": field},
        {"name": "Lake", "collected": 0, "total": 1, "unknown": 0, "marked": 0, "checks": lake},
    ]
    if not available:
        for area in areas:
            for entry in area["checks"]:
                entry.pop("in_logic", None)
    else:
        for area in areas:
            area["in_logic"] = {
                age: sum(bool(c.get("in_logic", {}).get(age)) for c in area["checks"])
                for age in ("child", "adult", "either")
            }
    state = {
        "seed": {"seed": 1},
        "dungeons": [],
        "items": [{"id": "hookshot", "group": "upgrades", "label": "Hookshot", "held": None, "max_tier": 2}],
        "songs": [],
        "rewards": [],
        "hearts": {},
        "tokens": None,
        "skulltula_checks": {"collected": 0, "total": 0, "unknown": 0},
        "areas": areas,
        "show_locations": False,
        "warnings": [],
        "logic": {"available": available, "reason": reason, "unknown_items": list(unknown_items), "save_age": save_age},
    }
    return {"status": "ok", "state": state, "slots": [], "selected_slot": "slot_00", "revision": 1, "warnings": []}


def tab(tmp_path, snap=None, **page):
    return render_tracker(tmp_path, snap or snapshot(), obs=False, **page)


def classes(rendered):
    return {entry["id"]: entry for entry in rendered["checks"]}


def styled(rendered, name):
    entry = classes(rendered)[name]["className"].split()
    if "tracker-check-in-logic" in entry:
        return "in"
    if "tracker-check-out-of-logic" in entry:
        return "out"
    if "tracker-check-collected" in entry:
        return "collected"
    if "tracker-check-marked" in entry:
        return "marked"
    return "plain"


# 10.2 (5.1)
def test_age_control_defaults_to_either(tmp_path):
    rendered = tab(tmp_path)
    assert (rendered["controls"]["age"]["value"], rendered["controls"]["age"]["disabled"]) == ("either", False)
    assert styled(rendered, "Child Chest") == "in" and styled(rendered, "Adult Chest") == "in"
    assert styled(rendered, "Far Chest") == "out"


# 10.3 (5.2)
def test_follow_save_uses_the_saves_age_or_either_with_a_note(tmp_path):
    follow = [{"id": "tracker-age", "value": "save", "event": "change"}]
    rendered = tab(tmp_path, snapshot(save_age="adult"), actions=follow)
    assert styled(rendered, "Child Chest") == "out" and styled(rendered, "Adult Chest") == "in"
    assert not any("Follow save" in note for note in rendered["notes"])
    unreadable = tab(tmp_path, snapshot(save_age=None), actions=follow)
    assert styled(unreadable, "Child Chest") == "in" and styled(unreadable, "Adult Chest") == "in"
    assert [note for note in unreadable["notes"] if "Follow save" in note] and len(unreadable["notes"]) == 1


# 10.4 (5.3)
def test_a_non_default_age_persists_and_storage_may_be_unavailable(tmp_path):
    chosen = tab(tmp_path, actions=[{"id": "tracker-age", "value": "child", "event": "change"}])
    assert chosen["storage"] == {AGE_KEY: "child"}
    back = tab(
        tmp_path, storage={AGE_KEY: "child"}, actions=[{"id": "tracker-age", "value": "either", "event": "change"}]
    )
    assert back["storage"] == {}
    restored = tab(tmp_path, storage={AGE_KEY: "adult"})
    assert restored["controls"]["age"]["value"] == "adult"
    assert tab(tmp_path, storage={AGE_KEY: "nonsense"})["controls"]["age"]["value"] == "either"
    private = tab(tmp_path, storage=None, actions=[{"id": "tracker-age", "value": "adult", "event": "change"}])
    assert private["controls"]["age"]["value"] == "adult"
    assert styled(private, "Child Chest") == "out"


# 10.5 (5.4), 11.1 (6.1), 11.2 (6.2)
@pytest.mark.parametrize(
    ("age", "child_chest", "adult_chest", "counts"),
    [("child", "in", "out", (1, 0)), ("adult", "out", "in", (1, 0)), ("either", "in", "in", (2, 0))],
)
def test_styles_and_area_counts_follow_the_age(tmp_path, age, child_chest, adult_chest, counts):
    rendered = tab(tmp_path, actions=[{"id": "tracker-age", "value": age, "event": "change"}])
    assert (styled(rendered, "Child Chest"), styled(rendered, "Adult Chest")) == (child_chest, adult_chest)
    assert styled(rendered, "Done Chest") == "collected"
    assert styled(rendered, "Shop Item") == "marked"
    heads = [head["text"] for head in rendered["areaHeads"]]
    assert [f"{n} in logic" in head for head, n in zip(heads, counts, strict=True)] == [True, True]


# 11.3 (6.3)
def test_show_only_in_logic_hides_the_rest_and_collapses_empty_areas(tmp_path):
    rendered = tab(
        tmp_path,
        actions=[
            {"id": "tracker-age", "value": "child", "event": "change"},
            {"id": "tracker-logic-only", "checked": True, "event": "change"},
        ],
    )
    shown = {name for name, entry in classes(rendered).items() if entry["shown"]}
    assert shown == {"Child Chest"}
    assert [head["shown"] for head in rendered["areaHeads"]] == [True, False]


# 11.4 (6.4)
def test_unavailable_logic_disables_the_controls_and_says_why(tmp_path):
    rendered = tab(tmp_path, snapshot(available=False, reason="This seed was made by clawshot 0.0.1"))
    assert rendered["controls"]["age"]["disabled"] and rendered["controls"]["only"]["disabled"]
    assert [note for note in rendered["notes"] if "clawshot 0.0.1" in note]
    assert {styled(rendered, name) for name in ("Child Chest", "Adult Chest", "Far Chest")} == {"plain"}
    assert not any("in logic" in head["text"] for head in rendered["areaHeads"])


# 11.5 (6.5)
def test_unknown_items_say_in_logic_may_be_conservative(tmp_path):
    rendered = tab(tmp_path, snapshot(unknown_items=["hookshot", "Forest Temple small keys"]))
    [note] = [note for note in rendered["notes"] if "conservative" in note]
    assert "Hookshot" in note and "Forest Temple small keys" in note
    assert not [note for note in tab(tmp_path)["notes"] if "conservative" in note]


# 11.6 (4.1, 4.2, 4.8)
def test_unknown_checks_have_a_mark_toggle(tmp_path):
    rendered = tab(tmp_path, actions=[{"class": "tracker-mark", "index": 0, "event": "click"}])
    toggles = {
        name for name, entry in classes(rendered).items() if "Mark done" in entry["text"] or "Unmark" in entry["text"]
    }
    assert toggles == {"Adult Chest", "Shop Item"}  # only checks the save cannot read
    assert "Unmark" in classes(rendered)["Shop Item"]["text"]
    assert rendered["posts"] == [{"route": "tracker-mark", "body": {"check": "Adult Chest", "marked": True}}]
    unmark = tab(tmp_path, actions=[{"class": "tracker-mark", "index": 1, "event": "click"}])
    assert unmark["posts"] == [{"route": "tracker-mark", "body": {"check": "Shop Item", "marked": False}}]


def test_clear_marks_asks_first(tmp_path):
    clear = [{"id": "tracker-clear-marks", "event": "click"}]
    assert tab(tmp_path, actions=clear, confirm=False)["posts"] == []
    assert tab(tmp_path, actions=clear, confirm=True)["posts"] == [
        {"route": "tracker-clear-marks", "body": {"confirmed": True}}
    ]


def test_check_names_without_spoilers_show_no_items(tmp_path):
    rendered = tab(tmp_path)
    assert all(":" not in entry["text"] for entry in rendered["checks"])


def test_obs_shows_no_checks_or_controls(tmp_path):
    rendered = render_tracker(tmp_path, snapshot(), obs=True)
    assert rendered["checks"] == [] and rendered["notes"] == []
    assert rendered["controls"] == {"age": None, "only": None, "vanilla": None, "clear": None}


# 11.7 (P11.a): no new static file; the three tracker assets stay the served ones.
def test_no_new_static_files():
    tracker_files = sorted(name for name in STATIC if name.startswith("tracker"))
    assert tracker_files == ["tracker.css", "tracker.html", "tracker.js"]
    assert sorted(p.name for p in ASSETS.glob("tracker*")) == tracker_files


# --- Task 16: vanilla pick-ups (D19, 8.6).
VANILLA_KEY = "clawshot.tracker.vanilla"


def with_vanilla(**options):
    """The snapshot plus a vanilla row in Field (open, in logic for child) and a vanilla-only Fountain area."""
    snap = snapshot(**options)
    row = check("Letter Pickup", False, (True, False, True)) | {"vanilla": True, "item": "Rutos Letter"}
    row["item_label"] = "Ruto's Letter"
    far = check("Fountain Pickup", False, (False, False, False)) | {"vanilla": True, "item": "Silver Scale"}
    snap["state"]["vanilla_areas"] = [
        {
            "name": "Field",
            "collected": 0,
            "total": 1,
            "unknown": 0,
            "marked": 0,
            "checks": [row],
            "in_logic": {"child": 1, "adult": 0, "either": 1},
        },
        {
            "name": "Fountain",
            "collected": 0,
            "total": 1,
            "unknown": 0,
            "marked": 0,
            "checks": [far],
            "in_logic": {"child": 0, "adult": 0, "either": 0},
        },
    ]
    return snap


def test_vanilla_rows_show_in_their_area_by_default_with_a_tag(tmp_path):
    rendered = tab(tmp_path, with_vanilla())
    assert rendered["controls"]["vanilla"] == {"checked": True, "disabled": False}
    letter = classes(rendered)["Letter Pickup"]
    assert "tracker-check-vanilla" in letter["className"] and "vanilla" in letter["text"]
    assert "Ruto's Letter" in letter["text"] and styled(rendered, "Letter Pickup") == "in"
    assert styled(rendered, "Fountain Pickup") == "out"
    heads = [head["text"] for head in rendered["areaHeads"]]
    assert len(heads) == 3 and "vanilla 0 / 1" in heads[0] and heads[2].startswith("vanilla 0 / 1")
    assert "1 in logic" in heads[0].split("vanilla")[1]


def test_the_vanilla_toggle_hides_them_and_is_remembered(tmp_path):
    hide = [{"id": "tracker-vanilla", "checked": False, "event": "change"}]
    rendered = tab(tmp_path, with_vanilla(), actions=hide)
    assert "Letter Pickup" not in classes(rendered) and len(rendered["areaHeads"]) == 2
    assert rendered["storage"] == {VANILLA_KEY: "hidden"}
    restored = tab(tmp_path, with_vanilla(), storage={VANILLA_KEY: "hidden"})
    assert restored["controls"]["vanilla"]["checked"] is False
    back = tab(
        tmp_path,
        with_vanilla(),
        storage={VANILLA_KEY: "hidden"},
        actions=[{"id": "tracker-vanilla", "checked": True, "event": "change"}],
    )
    assert back["storage"] == {} and "Letter Pickup" in classes(back)
    private = tab(tmp_path, with_vanilla(), storage=None, actions=hide)
    assert "Letter Pickup" not in classes(private)


def test_show_only_in_logic_applies_to_vanilla_rows(tmp_path):
    only = [{"id": "tracker-logic-only", "checked": True, "event": "change"}]
    rendered = classes(tab(tmp_path, with_vanilla(), actions=only))
    assert rendered["Letter Pickup"]["shown"] is True
    assert rendered["Fountain Pickup"]["shown"] is False


def test_vanilla_toggle_is_disabled_without_logic(tmp_path):
    rendered = tab(tmp_path, with_vanilla(available=False, reason="old seed"))
    assert rendered["controls"]["vanilla"]["disabled"] is True
    assert "Letter Pickup" not in classes(rendered)
