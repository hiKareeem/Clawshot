import copy

import pytest

from clawshot.formats import evfl
from clawshot.patch import scrubs
from clawshot.patch.plan import PatchError


def fixture():
    events = []
    for sale in scrubs.SALES.values():
        for name, old in sale.grants:
            events.append(
                evfl.SubFlowEvent(
                    name, "", "SimpleShopSub_Scrub_Business_OneTime", params={"ActorName": old, "Price": sale.price}
                )
            )
        if sale.selection:
            events.append(
                evfl.ActionEvent(
                    sale.selection, 0, 0, params={"GameDataName": "Shop_SelectItemName", "Value": "Obj_Heart_Piece"}
                )
            )
    events.append(evfl.ActionEvent("Once", 0, 1, params={"GameDataName": "Saved", "Value": True}))
    return evfl.Flowchart(
        scrubs.FLOW,
        [evfl.Actor("GameDataActor", actions=["EventTriggerSetGameDataString64", "EventTriggerSetGameDataBool"])],
        events,
        [],
    )


def test_all_tiers_and_shared_copies_receive_one_reward_without_changing_gates():
    before = fixture()
    file = evfl.EventFlowFile(scrubs.FLOW, flowchart=copy.deepcopy(before))
    placements = dict(zip(scrubs.SALES, ("Item_A", "Item_B", "Item_C", "Item_D"), strict=True))
    after = evfl.read(scrubs.changes(placements)[scrubs.PATH](evfl.write(file))).flowchart
    index = {e.name: e for e in after.events}
    for check, sale in scrubs.SALES.items():
        for name, old in sale.grants:
            assert index[name].params["ActorName"] == placements[check]
            index[name].params["ActorName"] = old
        if sale.selection:
            assert index[sale.selection].params["Value"] == placements[check]
            index[sale.selection].params["Value"] = "Obj_Heart_Piece"
    assert after == before


@pytest.mark.parametrize("broken", ["grant", "price", "selection", "missing"])
def test_stale_contract_fails_before_mutation(broken):
    fc = fixture()
    if broken == "missing":
        fc.events.pop(1)
    elif broken == "selection":
        fc.events[1].params["Value"] = "Item_Wrong"
    else:
        fc.events[0].params["ActorName" if broken == "grant" else "Price"] = "Wrong"
    before = copy.deepcopy(fc)
    with pytest.raises(PatchError):
        scrubs.patch_flowchart(fc, {"HF Deku Scrub Grotto": "Item_New"})
    assert fc == before


def test_repeat_vendor_is_not_a_once_check():
    with pytest.raises(PatchError):
        scrubs.changes({"LW Deku Scrub Near Deku Theater Left": "Item_New"})
