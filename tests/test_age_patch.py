"""Synthetic pedestal identities; no game trees or decoded modules as fixtures."""

from copy import deepcopy

import pytest

from clawshot.formats import byml
from clawshot.patch import age
from clawshot.patch.plan import PatchError


def pedestal_tree():
    refs, actors = [], []
    for name, (actor_hash, actor_type, _) in age.BINDINGS.items():
        refs.append({"Id": name, "Path": name, "Reference": byml.U64(actor_hash)})
        actor = {"Hash": byml.U64(actor_hash), "Gyaml": actor_type, "Translate": [byml.F32(1.0)] * 3}
        if actor_type == "EventRequestActor":
            actor["Dynamic"] = {"RequestEventName": "Market_Adult_Field_AdultToChild"}
        actors.append(actor)
    actors.append(
        {
            "Hash": byml.U64(2669233513522124871),
            "Gyaml": "Npc_Hylia_Sheik_Adult",
            "Phive": {"Placement": {"ID": byml.U64(2669233513522124871)}},
        }
    )
    return {
        "Actors": [*actors, {"Hash": byml.U64(123), "Gyaml": "SyntheticUnrelatedActor"}],
        "AiGroups": [
            {"Hash": byml.U64(321), "Logic": "SyntheticUnrelatedLogic", "References": []},
            {"Hash": byml.U64(age.GROUP_HASH), "Logic": age.GATED_LOGIC, "References": refs},
            {
                "Hash": byml.U64(6012439728933042438),
                "Logic": "Logic/Module/Market_Adult_Prefab/Market_Adult_Prefab_7f43.logic.module.ain",
                "References": [
                    {
                        "Id": "Npc_Hylia_Sheik_Adult_4b5b",
                        "Path": "Npc_Hylia_Sheik_Adult_4b5b",
                        "Reference": byml.U64(2669233513522124871),
                    }
                ],
            },
        ],
        "SyntheticOtherTable": {"Value": byml.U32(19)},
    }


def test_rebinding_preserves_actors_hashes_paths_and_unrelated_groups():
    old = pedestal_tree()
    expected = deepcopy(old)
    group = expected["AiGroups"][1]
    group["Logic"] = age.UNGATED_LOGIC
    for ref in group["References"]:
        ref["Id"] = age.BINDINGS[ref["Id"]][2]
    expected["Actors"][2]["Presence"] = {
        "FlagName": "SageOfForest_IsCompleted_Exp",
        "IsCheckLazy": False,
        "IsNegation": False,
    }
    data = byml.write(old)
    result = age.changes({}, free_time_travel=True)[age.PLACEMENT](data)
    assert byml.same(byml.read(result), expected)
    assert byml.same(old, byml.read(data))
    assert age.changes({}) == {}


@pytest.mark.parametrize("changed", ["module", "binding", "event"])
def test_changed_pedestal_contract_is_rejected_without_partial_mutation(changed):
    tree = pedestal_tree()
    if changed == "module":
        tree["AiGroups"][1]["Logic"] = "DifferentGate"
    elif changed == "binding":
        tree["AiGroups"][1]["References"][1]["Reference"] = byml.U64(555)
    else:
        tree["Actors"][0]["Dynamic"]["RequestEventName"] = "DifferentEvent"
    before = deepcopy(tree)
    with pytest.raises(PatchError):
        age.patch_tree(tree)
    assert byml.same(tree, before)


@pytest.mark.parametrize("changed", ["missing", "duplicate", "presence", "identity", "group", "reference"])
def test_changed_sheik_contract_rejects_before_pedestal_mutation(changed):
    tree = pedestal_tree()
    sheik = tree["Actors"][2]
    if changed == "missing":
        tree["Actors"].remove(sheik)
    elif changed == "duplicate":
        tree["Actors"].append(deepcopy(sheik))
    elif changed == "presence":
        sheik["Presence"] = {"FlagName": "DifferentQuest"}
    elif changed == "identity":
        sheik["Gyaml"] = "DifferentNpc"
    elif changed == "group":
        tree["AiGroups"][2]["Logic"] = "DifferentModule"
    else:
        tree["AiGroups"][2]["References"][0]["Reference"] = byml.U64(999)
    before = deepcopy(tree)
    with pytest.raises(PatchError):
        age.patch_tree(tree)
    assert byml.same(tree, before)
