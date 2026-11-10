"""Readable output must not relink a check or lose a shuffled destination."""

import json
from dataclasses import replace

import pytest

from clawshot.census.definitions import load as load_definitions
from clawshot.generate import Settings, generate, play_note, spoiler_json
from clawshot.generate.names import shops
from clawshot.world import load_spec


def test_every_shuffled_check_has_directions_beside_its_unchanged_identity():
    seed = generate(load_spec(), 7, Settings(shuffle=("Chest", "Shop")))
    log = json.loads(spoiler_json(seed))
    assert log["placements"] == {name: seed.placements[name] for name in seed.shuffled}
    assert set(log["locations"]) == set(seed.shuffled)
    definitions = {}
    for definition in load_definitions():
        definitions.setdefault(definition.oot_randomizer_name or definition.name, set()).add(str(definition.id))
    rows = {}
    for line in play_note(seed, log).splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.replace(r"\|", "|") for cell in line.removeprefix("| ").removesuffix(" |").split(" | ")]
        if len(cells) != 5 or cells[3] not in seed.shuffled:
            continue
        _sphere, name, where, world_key, _item = cells
        assert world_key not in rows, world_key
        rows[world_key] = (name, where)
    assert set(rows) == set(seed.shuffled)
    for world_key in seed.shuffled:
        details = log["locations"][world_key]
        assert set(details["ids"]) == definitions[world_key], world_key
        assert details["name"] and details["where"] and details["source"], world_key
        assert details["oot_randomizer_name"] in ("", world_key), world_key
        assert rows[world_key] == (details["name"], details["where"]), world_key


@pytest.mark.parametrize(
    ("policy", "shuffled", "cheap", "expected"),
    [
        ("vanilla", False, True, (10, 40, 600)),
        ("vanilla", False, False, (40, 40, 600)),
        ("vanilla", True, True, (10, 40, 600)),
        ("affordable", False, False, (40, 40, 600)),
        ("affordable", True, False, (10, 10, 10)),
    ],
)
def test_spoiler_prices_follow_actual_item_slot_and_settings(policy, shuffled, cheap, expected):
    # Fixed contents isolate the presentation contract from fill ordering.
    contents = {"KF Shop Item 6": "Deku Shield", "KF Shop Item 7": "Hylian Shield", "GC Shop Item 4": "Deku Shield"}
    spec = {
        "start": "Sales",
        "goal": "True",
        "items": {item: {} for item in contents.values()},
        "locations": {name: {"type": "Shop", "vanilla": item} for name, item in contents.items()},
        "regions": [{"name": "Sales", "locations": {name: "True" for name in contents}}],
    }
    seed = generate(spec, 7, Settings(shuffle=()))
    seed = replace(
        seed,
        settings=replace(seed.settings, shop_prices=policy, cheap_deku_shield=cheap),
        shuffled=list(contents) if shuffled else [],
    )
    sales = shops(seed)
    assert tuple(sales[name]["price"] for name in contents) == expected
    if shuffled:
        log = json.loads(spoiler_json(seed))
        assert tuple(log["locations"][name]["price"] for name in contents) == expected
