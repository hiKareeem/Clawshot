import copy

import pytest

from clawshot.formats import evfl
from clawshot.patch import gifts
from test_gifts import FLOW, change, flowchart


def test_terminal_inventory_write_becomes_completion_without_clearing_held_item():
    chart = flowchart()
    chart.events[2].params["GameDataName"] = "IsGet.Item_Old"
    original = copy.deepcopy(chart)
    selected = change(cls="rewrite", writes=(FLOW + "/Event2",), flag="HavePlayedEvent.Npc_Test")
    gifts.patch_flowchart(chart, FLOW, [selected])
    assert chart.events[2].next == evfl.NONE
    assert chart.events[2].params == {"GameDataName": "HavePlayedEvent.Npc_Test", "Index": -1, "Value": True}
    assert selected.new_flag is None  # no extra save flag/layout change
    chart.events[2].params["GameDataName"] = "IsGet.Item_Old"
    chart.events[1].params["ActorName"] = "Item_Old"
    chart.events[4].params["ActorName"] = "Item_Old_Large"
    assert chart == original  # all other fields, including the original inventory read, stay intact


@pytest.mark.parametrize("field,value", [("GameDataName", "IsGet.Other"), ("Value", False)])
def test_redirect_refuses_stale_inventory_write(field, value):
    chart = flowchart()
    chart.events[2].params["GameDataName"] = "IsGet.Item_Old"
    chart.events[2].params[field] = value
    with pytest.raises(gifts.GiftPatchError):
        gifts.patch_flowchart(
            chart, FLOW, [change(cls="rewrite", writes=(FLOW + "/Event2",), flag="HavePlayedEvent.Npc_Test")]
        )


@pytest.mark.parametrize("flag", [None, "IsGet.Item_Old", ""])
def test_write_redirect_requires_existing_completion_flag(flag):
    text = '[check.Test]\nclass="rewrite"\nwrites=["Flow/Event1"]\n'
    if flag is not None:
        text += 'flag="' + flag + '"\n'
    with pytest.raises(gifts.GiftPatchError):
        gifts.loads(text)
