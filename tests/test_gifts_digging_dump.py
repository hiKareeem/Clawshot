"""The native .110 grant retains its cleanup and uses a real persistent completion flag."""

from copy import deepcopy

import pytest

from clawshot.census.definitions import load
from clawshot.census.gifts import scan_gifts
from clawshot.census.hints import flow_path
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import evfl, zsdic
from clawshot.patch import gifts
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.patch.plan import Plan
from clawshot.patch.write import write
from clawshot.save import murmur3_32


@pytest.mark.dump
def test_native_digging_grant_is_guarded_by_saved_completion_and_preserves_cleanup(romfs, tmp_path):
    flow = "Npc_Hylia_Dampe_001"
    path = flow_path(romfs, flow)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    flags = read_romfs_byml(romfs, dictionaries, GAME_DATA_LIST)["Data"]["Bool"]
    flag = next(f for f in flags if int(f["Hash"]) == murmur3_32(gifts.DAMPE_FLAG.encode()))
    assert (flag["DefaultValue"], int(flag["ResetTypeValue"]), int(flag["SaveFileIndex"])) == (False, 8, 0)
    changes = gifts.plan({gifts.DAMPE_CHECK: "Item_Boomerang"}, scan_gifts(romfs), load(), gifts.load())
    transforms = gifts.file_changes(changes, {flow: path})
    assert GAME_DATA_LIST not in transforms
    out = tmp_path / "digging"
    write(Plan([], [], []), romfs, out, extra_changes=[transforms])
    before = evfl.read(dictionaries.decompress(path, (romfs / path).read_bytes())).flowchart
    after = evfl.read(dictionaries.decompress(path, (out / "romfs" / path).read_bytes())).flowchart
    index = {e.name: i for i, e in enumerate(after.events)}
    grant = after.events[index["Event628"]]
    gate = after.events[after.events[index["Event449"]].forks[0]]
    assert gate.params == {"GameDataName": gifts.DAMPE_FLAG, "Index": -1}
    assert gate.cases == [(0, evfl.NONE), (1, index["Event628"])]
    assert grant.params["ActorName"] == "Item_Boomerang"
    saved = after.events[grant.next]
    assert after.actors[saved.actor].actions[saved.action] == gifts.SET_ACTION
    assert saved.params == {"GameDataName": gifts.DAMPE_FLAG, "Index": -1, "Value": True}
    restored = deepcopy(after)
    restored.events = restored.events[: len(before.events)]
    for name in ("Event449", "Event628"):
        restored.events[index[name]] = deepcopy(before.events[index[name]])
    assert restored == before
