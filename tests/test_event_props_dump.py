"""``patch/event_props.toml`` against the dump (spec event-items 2.1, 2.7, 2.8; plan task 4): every item actor an
event shows is a prop or excluded with a reason, and every prop names a real check, its vanilla item and grant."""

import pytest

from clawshot.census import definitions
from clawshot.census.event_items import scan_prop_actors
from clawshot.census.gifts import load_flowcharts, scan_gifts
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import zsdic
from clawshot.generate.rewards import catalog
from clawshot.patch import event_props, gifts

pytestmark = pytest.mark.dump


@pytest.fixture(scope="module")
def candidates(romfs):
    return scan_prop_actors(romfs)


@pytest.fixture(scope="module")
def steps(romfs):
    return gifts.check_steps(scan_gifts(romfs), definitions.load())


def test_dump_every_shown_item_actor_is_a_prop_or_excluded_and_nothing_is_stale(romfs, candidates):
    data = event_props.load()
    props = {p.id for p in data.props if p.part != event_props.PLACEMENT}
    excluded = {c for c in candidates if data.excluded(c) is not None}
    assert sorted(set(candidates) - props - excluded) == [], "new prop actors: add them as props or exclude them"
    assert sorted(props - set(candidates)) == [], "props the dump does not show"
    listed = {a for e in data.exclusions.values() for a in e.actors}
    assert sorted(listed - set(candidates)) == [], "excluded actors the dump does not show"
    files, _ = load_flowcharts(romfs)
    events = {e for x in data.exclusions.values() for e in x.events}
    assert sorted(events - set(files)) == [], "excluded events the dump does not have"


def test_dump_each_prop_stands_for_its_check_vanilla_item_and_branch_grant(steps):
    rules = gifts.load()
    slots = catalog()["slots"]
    for prop in event_props.load().props:
        if prop.check in slots:
            assert prop.item == slots[prop.check]["actor"], prop
            continue
        assert prop.check in rules, f"{prop.id}: {prop.check} is no gift check"
        items = {s.vanilla_item: s for s in steps[prop.check]}
        assert prop.item in items, f"{prop.id}: {prop.item} not given by {prop.check} ({sorted(items)})"
        if prop.grant:
            assert items[prop.item].id == prop.grant, prop


def test_dump_a_check_with_two_props_of_different_items_in_one_event_names_each_branch_grant():
    by_event: dict[tuple[str, str, str], set[str]] = {}
    for prop in event_props.load().props:
        by_event.setdefault((prop.check, prop.event, prop.part), set()).add(prop.item)
    for prop in event_props.load().props:
        if len(by_event[(prop.check, prop.event, prop.part)]) > 1:
            assert prop.grant, f"{prop.id}: a branch prop needs its grant (D13)"


def test_dump_lw_target_in_woods_keeps_one_prop_per_bag_branch():
    props = sorted(
        (p.actor, p.secondary, p.item, p.grant) for p in event_props.load().props if p.check == "LW Target in Woods"
    )
    assert props == [
        ("Item_BulletBag_Large", "LostWood", "Item_BulletBag_Large", "Dm_LostWood_0040/Event17"),
        ("Item_BulletBag_Medium", "LostWood", "Item_BulletBag_Medium", "Dm_LostWood_0040/Event30"),
    ]


def test_dump_the_moat_object_and_rutos_stone_are_placed_where_the_data_says(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    placed = [p for p in event_props.load().props if p.part == event_props.PLACEMENT]
    assert [(p.check, p.hash) for p in placed] == [
        ("HF Ocarina of Time Item", 2802436684568022035),
        ("Barinade", 15570932853683785298),  # Ruto's stone in Jabu-Jabu, plan 10b (decision Q6)
    ]
    for prop in placed:
        actors = {a["Hash"]: a for a in read_romfs_byml(romfs, dicts, prop.banc)["Actors"]}
        assert actors[prop.hash]["Gyaml"] == prop.actor


def test_dump_played_instruments_and_events_that_are_no_check_are_excluded_by_name():
    data = event_props.load()
    played = set(data.exclusions["played"].actors)
    assert {
        "Dm_Kokiri_0150/timeline/Dm_Item_Ocarina_Fairy_Saria@0",
        "Dm_Kokiri_0155/flowchart/Dm_Item_Ocarina_Fairy_Saria@saria",
        "Dm_MelodyGet_Fire/flowchart/Dm_Item_Sheik_Harp",
        "Dm_MelodyGet_Fire/flowchart/Item_Ocarina_Time_Holder",
    } <= played
    assert {
        "Dm_TimeTemple_0010",
        "Dm_Kokiri_0030",
        "Dm_FinalBattle_0010",
        "Dm_WaterTemple_0000",
        "Dm_InsideGanonCastle_0150",
    } <= set(data.exclusions["not_check"].events)


def test_dump_zeldas_ocarina_in_the_moat_lesson_is_played_not_the_given_item():
    """Played run E10 (BBender 2026-11-26): ``Dm_MelodyGet_Time``'s ``Dm_Item_Ocarina_Time`` is bound to Zelda's hand
    (Event35, bone Weapon_L) in the Song of Time lesson, a memory of her playing it: an instrument someone plays, so it
    keeps its look (D3), not a prop of HF Ocarina of Time Item."""
    data = event_props.load()
    assert "Dm_MelodyGet_Time/flowchart/Dm_Item_Ocarina_Time" in data.exclusions["played"].actors
    assert not [p for p in data.props if p.event == "Dm_MelodyGet_Time"]
