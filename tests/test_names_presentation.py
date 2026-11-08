"""Readable output must not relink a check or lose a shuffled destination."""

import json

from clawshot.census.definitions import load as load_definitions
from clawshot.generate import Settings, generate, play_note, spoiler_json
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
        _sphere, name, where, world_key, item = cells
        assert world_key not in rows, world_key
        rows[world_key] = (name, where, item)
    assert set(rows) == set(seed.shuffled)
    for world_key in seed.shuffled:
        details = log["locations"][world_key]
        assert set(details["ids"]) == definitions[world_key], world_key
        assert details["name"] and details["where"] and details["source"], world_key
        assert details["oot_randomizer_name"] in ("", world_key), world_key
        assert rows[world_key] == (details["name"], details["where"], seed.placements[world_key]), world_key
