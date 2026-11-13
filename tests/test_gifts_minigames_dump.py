"""Real gift setup cannot retain ownership-dependent or phantom minigame rewards."""

from copy import deepcopy

import pytest

from clawshot.census.hints import flow_path
from clawshot.formats import evfl, zsdic
from clawshot.generate import Settings, prepare
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import gifts
from clawshot.progressive import TIERED_GIFTS
from clawshot.world.load import load_spec


@pytest.mark.dump
def test_gift_setup_normalizes_both_bowling_prizes_and_both_normal_galleries(romfs):
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), Settings(shuffle=("Chest", "Gift")))
    _, world = prepare(spec, settings)
    selected = shuffled_locations(world, settings)
    assert set(gifts.BOWLING_CHECKS) | set(TIERED_GIFTS) <= set(selected)
    for name in ("Market Bombchu Bowling Bombchus", "Market Bombchu Bowling Bomb"):
        assert world.locations[name].n64_only
    placements = {name: loc.vanilla for name, loc in world.locations.items()}
    transforms = step(placements)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    for flow, expected in (
        (
            gifts.BOWLING_FLOW,
            {"Event304": "Item_BombBag_Medium", "Event306": "Item_BombBag_Medium", "Event143": "Obj_Heart_Piece"},
        ),
        (
            "MiniGame_HitTarget",
            {
                "Event241": "Item_BulletBag_Medium",
                "Event378": "Item_BulletBag_Medium",
                "Event242": "Item_Quiver_Medium",
                "Event381": "Item_Quiver_Medium",
            },
        ),
    ):
        path = flow_path(romfs, flow)
        data = dictionaries.decompress(path, (romfs / path).read_bytes())
        before = evfl.read(data).flowchart
        after = evfl.read(transforms[path](data)).flowchart
        for name, actor in expected.items():
            event = next(e for e in after.events if e.name == name)
            assert event.params["ReveiveItem"] == actor
        restored = deepcopy(after)
        restored.events = restored.events[: len(before.events)]
        allowed = set(expected)
        if flow == gifts.BOWLING_FLOW:
            allowed |= {"Event73", "Event72"}
            first = next(e for e in after.events if e.name == "Event73")
            second = next(e for e in after.events if e.name == "Event72")
            assert after.events[dict(first.cases)[1]].name == "Event76"
            assert after.events[dict(second.cases)[1]].name == "Event143"
            assert after.events[dict(second.cases)[0]].name == "Event81"
        for index, event in enumerate(before.events):
            if event.name in allowed:
                restored.events[index] = deepcopy(event)
        assert restored == before
