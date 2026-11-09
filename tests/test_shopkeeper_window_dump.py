"""Execute the real merchant story dispatch on read-only dump bytes."""

import pytest
from test_shopkeeper_window import CASTLE, FLAG, FLOW, GOHMA, MEETING, dispatch_offer

from clawshot.census import definitions
from clawshot.census.gifts import scan_gifts
from clawshot.formats import evfl, zsdic
from clawshot.patch import gifts


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
