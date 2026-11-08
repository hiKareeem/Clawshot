"""Recreate the played seed outside its active output; game resources remain read-only."""

import json

import pytest

from clawshot.generate import Settings, play_note
from clawshot.patch import make_seed

pytestmark = pytest.mark.dump


def test_seed_shop_7_spoiler_buys_deku_shield_before_deku_tree(romfs):
    output = make_seed(romfs, 7, Settings(shuffle=("Chest", "Shop")))
    seed = output.seed
    log = json.loads(output.spoiler_json())
    steps = log["opening_route"]["steps"]
    entry = next(i for i, step in enumerate(steps) if step["kind"] == "enter")
    deku = next(i for i, step in enumerate(steps) if step["kind"] == "collect" and step["item"] == "Deku Shield")
    assert deku < entry
    assert steps[deku]["location"] == "KF Shop Item 6"
    assert steps[deku]["oot_randomizer_name"] == "KF Shop Item 6"
    assert {item["item"] for item in steps[deku]["requires"]} == {"Kokiri Sword", "Hylian Shield"}
    assert "Showed Mido Sword & Shield" in steps[deku]["release_rule"]
    assert steps[deku]["price"] == 10  # Default cheap-shield policy follows the moved shield, not KF7.
    assert any(step["location"] == "KF Shop Item 8" and step["item"] == "Hylian Shield" for step in steps[:deku])
    for index, step in enumerate(steps):
        prior = {earlier["location"] for earlier in steps[:index] if earlier["kind"] == "collect"}
        assert all(set(item["sources"]) <= prior for item in step["requires"]), step
    note = play_note(seed, log)
    opening = [line for line in note.splitlines() if line.startswith("| ") and "Deku Tree Lobby" in line]
    purchase = [line for line in note.splitlines() if line.startswith("| ") and "[KF Shop Item 6]" in line]
    assert note.index(purchase[0]) < note.index(opening[0])
