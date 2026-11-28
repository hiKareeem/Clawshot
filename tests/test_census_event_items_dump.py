"""Every display-only get window and Zelda's Notes target in a gift flow is assigned to a check (spec event-items
1.1): a gift check's ``display`` in ``gift_rules.toml``, or a dungeon reward slot's ``notes``."""

import pytest

from clawshot.census import definitions
from clawshot.census.event_items import NOTES, WINDOW, scan_displays
from clawshot.census.gifts import scan_gifts
from clawshot.generate.rewards import catalog
from clawshot.patch import gifts

pytestmark = pytest.mark.dump


@pytest.fixture(scope="module")
def displays(romfs):
    return {d.id: d for d in scan_displays(romfs)}


def _assigned() -> dict[str, str]:
    """``<flow>/<event>`` -> the check (gift rule or reward slot) it is assigned to."""
    out: dict[str, str] = {}
    for check, rule in gifts.load().items():
        for ref in rule.display:
            assert ref not in out, f"{ref} assigned to {out[ref]} and {check}"
            out[ref] = check
    for slot_name, slot in catalog()["slots"].items():
        ref = f"{slot['flow']}/{slot['notes']}"
        assert ref not in out, f"{ref} assigned to {out[ref]} and {slot_name}"
        out[ref] = slot_name
    return out


def test_dump_every_display_in_a_gift_flow_is_assigned_and_every_assignment_exists(displays):
    assigned = _assigned()
    assert sorted(set(displays) - set(assigned)) == [], "unassigned displays: add them to a check's display"
    assert sorted(set(assigned) - set(displays)) == [], "assigned displays the dump does not have"


def test_dump_a_gift_check_display_lies_in_one_of_its_own_step_flows(romfs):
    steps = gifts.check_steps(scan_gifts(romfs), definitions.load())
    for check, rule in gifts.load().items():
        flows = {step.flow for step in steps.get(check, ())}
        for ref in rule.display:
            assert ref.split("/")[0] in flows, f"{check}: {ref} is not in its gift flows {sorted(flows)}"


@pytest.mark.parametrize(
    ("ref", "kind", "native", "check"),
    [
        ("Dm_Kokiri_0155/Event77", WINDOW, "Item_Ocarina_Fairy", "LW Gift from Saria"),
        ("Dm_MelodyGet_Time/Event229", WINDOW, "Item_Ocarina_Time", "HF Ocarina of Time Item"),
        ("Dm_Kokiri_0155/Event58", NOTES, "Item_Ocarina_Fairy", "LW Gift from Saria"),
    ],
)
def test_dump_the_known_displays_are_listed_and_assigned(displays, ref, kind, native, check):
    assert (displays[ref].kind, displays[ref].native) == (kind, native)
    assert _assigned()[ref] == check
