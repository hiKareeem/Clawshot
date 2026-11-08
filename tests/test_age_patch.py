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
    return {
        "Actors": [*actors, {"Hash": byml.U64(123), "Gyaml": "SyntheticUnrelatedActor"}],
        "AiGroups": [
            {"Hash": byml.U64(321), "Logic": "SyntheticUnrelatedLogic", "References": []},
            {"Hash": byml.U64(age.GROUP_HASH), "Logic": age.GATED_LOGIC, "References": refs},
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
    with pytest.raises(PatchError, match="pedestal"):
        age.patch_tree(tree)
    assert byml.same(tree, before)
