"""Player directions cover actual check identities, including copies and held checks."""

import tomllib
from collections import defaultdict
from pathlib import Path

from clawshot.census.definitions import load as load_definitions
from clawshot.patch.gifts import SHOPKEEPER_CHECK, SHOPKEEPER_STEPS

CATALOG = Path(__file__).resolve().parents[1] / "src/clawshot/data/location_names.toml"
GIFT_KINDS = {"npc_gift", "event_gift", "song"}
SCRUB_CHECKS = {"HF Deku Scrub Grotto", "DMC Deku Scrub", "LW Deku Scrub Near Bridge", "LW Deku Scrub Grotto Front"}


def catalog():
    return tomllib.loads(CATALOG.read_text(encoding="utf-8"))["location"]


def test_every_supported_placement_and_linked_gift_has_directions_for_all_copies():
    expected = defaultdict(set)
    ootr = {}
    definitions = load_definitions()
    for definition in definitions:
        if definition.kind not in {"chest", "shop_slot"} and not (
            (definition.kind in GIFT_KINDS and definition.oot_randomizer_name)
            or (
                definition.kind == "freestanding"
                and definition.vanilla_item in {"Obj_Heart_Piece", "Obj_GerudoValley_Heart_Piece"}
            )
        ):
            continue
        key = definition.oot_randomizer_name or definition.name
        expected[key].add(str(definition.id))
        ootr[key] = definition.oot_randomizer_name
    expected[SHOPKEEPER_CHECK].update(SHOPKEEPER_STEPS)
    ootr[SHOPKEEPER_CHECK] = ""
    rows = catalog()
    actual = {row["location"]: row for row in rows}
    assert len(actual) == len(rows), "two descriptions for one logical check"
    assert set(actual) == set(expected) | SCRUB_CHECKS, (set(expected) - set(actual), set(actual) - set(expected))
    for key, ids in expected.items():
        row = actual[key]
        assert set(row["ids"]) == ids, (key, row["ids"], ids)
        assert row["oot_randomizer_name"] == ootr[key], key
    by_id = {str(definition.id): definition for definition in definitions}
    for key in SCRUB_CHECKS:
        row = actual[key]
        assert all(by_id[actor_hash].kind == "scrub" for actor_hash in row["ids"]), key
        linked = {str(d.id) for d in definitions if d.kind == "scrub" and d.oot_randomizer_name == key}
        assert linked <= set(row["ids"]), key
    for row in rows:
        for field in ("name", "where", "source"):
            assert isinstance(row[field], str) and row[field].strip(), (row["location"], field)
        assert "\n" not in row["where"], row["location"]
    labels = [row["name"] for row in rows]
    assert len(set(labels)) == len(labels), "player-facing names must distinguish checks"
