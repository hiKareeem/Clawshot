"""Recreate the played seed outside its active output; game resources remain read-only."""

import json

import pytest

from clawshot.generate import Settings, play_note
from clawshot.patch import make_seed

pytestmark = pytest.mark.dump


def test_seed_shop_7_opening_prefers_free_shield_visit_with_paid_alternative(romfs):
    output = make_seed(romfs, 7, Settings(shuffle=("Chest", "Shop")))
    seed = output.seed
    log = json.loads(output.spoiler_json())
    steps = log["opening_route"]["steps"]
    entry = next(i for i, step in enumerate(steps) if step["kind"] == "enter")
    deku = next(i for i, step in enumerate(steps) if step["kind"] == "visit" and step["item"] == "Deku Shield")
    assert deku < entry
    free = steps[deku]
    assert free["region"] == "KF Kokiri Shop" and free["event"] == "Deku Shield"
    assert free["price"] == 0 and free["not_equipped"] == "Deku Shield"
    assert {item["item"] for item in free["requires"]} == {"Kokiri Sword", "Hylian Shield"}
    assert not any(step["kind"] == "collect" and step["item"] == "Deku Shield" for step in steps)
    purchase = next(alt for alt in free["alternatives"] if alt["location"] == "KF Shop Item 6")
    assert purchase["price"] == 10
    assert "Showed Mido Sword & Shield" in purchase["release_rule"]
    assert {item["item"] for item in purchase["requires"]} == {"Kokiri Sword", "Hylian Shield"}
    assert any(step["location"] == "KF Shop Item 8" and step["item"] == "Hylian Shield" for step in steps[:deku])
    assert free["location"] not in seed.placements and free["location"] not in seed.world.locations
    for index, step in enumerate(steps):
        prior = {earlier["location"] for earlier in steps[:index] if earlier["kind"] in ("collect", "visit")}
        for option in (step, *step["alternatives"]):
            assert all(set(item["sources"]) <= prior for item in option["requires"]), option
    note = play_note(seed, log)
    rows = [line for line in note.splitlines() if line.startswith("| ")]
    entry_row = next(line for line in rows if "| Enter |" in line)
    visit_row = next(line for line in rows if f"[{free['location']}]" in line)
    alternative_row = next(line for line in rows if "[KF Shop Item 6]" in line and " alt |" in line)
    assert note.index(visit_row) < note.index(alternative_row) < note.index(entry_row)
