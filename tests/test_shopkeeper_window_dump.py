"""Execute the real merchant story dispatch on read-only dump bytes."""

import pytest
from test_shopkeeper_window import CASTLE, FLAG, FLOW, GOHMA, MEETING, dispatch_offer

from clawshot.census import definitions
from clawshot.census.gifts import scan_gifts
from clawshot.formats import evfl, zsdic
from clawshot.generate import Settings, prepare
from clawshot.generate.fill import allowed
from clawshot.patch import gifts
from clawshot.world.load import load_spec


@pytest.mark.dump
def test_real_merchant_uncollected_gift_survives_story_completion(romfs):
    [change] = gifts.plan(
        {gifts.SHOPKEEPER_CHECK: "Item_Boomerang"}, scan_gifts(romfs), definitions.load(), gifts.load()
    )
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    path = change.steps[0].file
    original = dictionaries.decompress(path, (romfs / path).read_bytes())
    transform = gifts.file_changes([change], {FLOW: path})[path]
    before = evfl.read(original).flowchart
    after = evfl.read(transform(original)).flowchart
    for castle, gohma in ((False, False), (False, True), (True, False), (True, True)):
        flags = {CASTLE: castle, GOHMA: gohma, MEETING: True}
        assert dispatch_offer(after, flags) == ["Item_Boomerang"], flags
        assert flags[FLAG] is True
        assert dispatch_offer(after, dict(flags)) == []
        if castle or gohma:
            assert dispatch_offer(before, {CASTLE: castle, GOHMA: gohma, MEETING: True}) == []
    flags = {CASTLE: True, GOHMA: True}
    assert dispatch_offer(after, flags) == []
    assert FLAG not in flags


@pytest.mark.dump
def test_progression_policy_and_effective_cs1_apply_the_late_gift_flow(romfs):
    settings = Settings(shuffle=("Gift",))
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    for _ in range(2):  # Public Gift input, then its expanded effective CS1 replay.
        spec, settings, step = gifts.seed_setup(romfs, load_spec(), settings)
        _, world = prepare(spec, settings)
        assert allowed(world, settings, gifts.SHOPKEEPER_CHECK, "Boomerang")
        placements = {name: location.vanilla for name, location in world.locations.items()}
        placements[gifts.SHOPKEEPER_CHECK] = "Boomerang"
        transforms = step(placements)
        [path] = [path for path in transforms if FLOW in path]
        original = dictionaries.decompress(path, (romfs / path).read_bytes())
        chart = evfl.read(transforms[path](original)).flowchart
        flags = {CASTLE: True, GOHMA: True, MEETING: True}
        assert dispatch_offer(chart, flags, equipped=True) == ["Item_Boomerang"]
        assert dispatch_offer(chart, dict(flags), equipped=True) == []
        settings = Settings.from_string(settings.to_string())
