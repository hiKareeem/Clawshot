"""Reachability on synthetic worlds: ages and the Temple of Time, here(), time of day, key doors."""

from clawshot.world import ADULT, CHILD, build_world, reachable

HELPERS = {
    "is_child": "age == 'child'",
    "is_adult": "age == 'adult'",
    "is_starting_age": "age == starting_age",
}


def spec(regions: list[dict], items: dict | None = None, flags: dict | None = None) -> dict:
    return {
        "start": "Root",
        "goal": "True",
        "items": {"Time Travel": {"type": "Event"}, "Sword": {}, "Beans": {}, "Hookshot": {}, "Key": {}}
        | (items or {}),
        "helpers": HELPERS,
        "settings": {"starting_age": "child"},
        "flags": {"ensure_tod_access": False} | (flags or {}),
        "regions": [{"name": "Root", "exits": {"Spawn": "is_starting_age or Time_Travel"}}, *regions],
    }


def chest(rule: str = "True") -> dict:
    return {"rule": rule, "type": "Chest"}


TEMPLE_WORLD = spec(
    [
        {"name": "Spawn", "exits": {"Field": "True"}},
        {
            "name": "Field",
            "locations": {"Field Chest": chest(), "Ledge Chest": chest("is_adult and Hookshot")},
            "exits": {"Temple": "Sword"},
        },
        {"name": "Temple", "events": {"Time Travel": "is_child"}},
    ]
)


def test_adult_starts_only_after_time_travel():
    w = build_world(TEMPLE_WORLD)
    search = reachable(w)
    assert search.regions(CHILD) == ["Root", "Spawn", "Field"]
    assert search.regions(ADULT) == ["Root"]  # the other age waits for the Temple of Time
    assert not search.holds("Time Travel")

    search = reachable(w, ["Sword"])
    assert search.holds("Time Travel")
    assert search.regions(ADULT) == ["Root", "Spawn", "Field", "Temple"]


def test_location_reachable_only_as_adult():
    w = build_world(TEMPLE_WORLD)
    ledge = w.locations["Ledge Chest"]
    assert not reachable(w, ["Hookshot"]).can_access(ledge)  # child can't, and there is no adult yet
    search = reachable(w, ["Hookshot", "Sword"])
    assert search.can_access(ledge, ADULT)
    assert not search.can_access(ledge, CHILD)
    assert search.locations(CHILD) == ["Field Chest"]


def test_here_is_an_event_any_age_can_set():
    # A bean planted as child lets adult ride the platform (OoT Randomizer's here(can_plant_bean)).
    w = build_world(
        spec(
            [
                {"name": "Spawn", "exits": {"Field": "True"}},
                {
                    "name": "Field",
                    "locations": {"Platform": chest("is_adult and here(is_child and Beans)")},
                    "exits": {"Temple": "True"},
                },
                {"name": "Temple", "events": {"Time Travel": "True"}},
            ]
        )
    )
    assert [e.name for e in w.events] == ["Time Travel", "Field Subrule 1"]
    assert not reachable(w).can_access(w.locations["Platform"])
    search = reachable(w, ["Beans"])
    assert search.holds("Field Subrule 1")
    assert search.can_access(w.locations["Platform"], ADULT)


def test_time_of_day_spreads_from_where_time_passes():
    regions = [
        {"name": "Spawn", "exits": {"Town": "True", "Field": "Sword"}},
        {"name": "Town", "locations": {"Night Shop": chest("at_night")}, "exits": {"Field": "Sword"}},
        {"name": "Field", "time_passes": True, "exits": {"Town": "True"}},
        {"name": "Blue Warp", "provides_time": "day", "exits": {"Town": "True"}},
    ]
    w = build_world(spec(regions, flags={"ensure_tod_access": True}))
    assert not reachable(w).can_access(w.locations["Night Shop"])  # the game starts at day
    assert reachable(w, ["Sword"]).can_access(w.locations["Night Shop"])  # wait in the field, walk back
    # Without entrance shuffle the rule folds: any time is assumed reachable (OoT Randomizer).
    w = build_world(spec(regions))
    assert reachable(w).can_access(w.locations["Night Shop"])


def test_key_doors_count_keys():
    w = build_world(
        spec(
            [
                {"name": "Spawn", "exits": {"Room 1": "True"}},
                {"name": "Room 1", "exits": {"Room 2": "Key"}},
                {"name": "Room 2", "exits": {"Room 3": "(Key, 2)"}},
                {"name": "Room 3", "locations": {"Prize": chest()}},
            ]
        )
    )
    assert reachable(w, ["Key"]).regions(CHILD)[-1] == "Room 2"
    assert reachable(w, ["Key", "Key"]).can_access(w.locations["Prize"])


def test_partial_world_reports_what_is_missing():
    w = build_world(spec([{"name": "Spawn", "exits": {"Elsewhere": "True"}, "events": {"Done": "'Not Here'"}}]))
    assert w.dangling_exits == [("Spawn", "Elsewhere")]
    assert w.undefined_events == ["Not Here"]
    assert reachable(w).regions(CHILD) == ["Root", "Spawn"]
