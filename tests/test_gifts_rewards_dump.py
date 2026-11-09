"""Native gift previews keep assigned items and compose with Gossip Stone text."""

import pytest

from clawshot.formats import msbt, sarc, zsdic
from clawshot.patch import gifts, text


def visible(parts):
    return "".join(part for part in parts if isinstance(part, str)).replace("\n", " ")


@pytest.mark.dump
def test_skulltula_previews_name_assigned_items_without_erasing_stone_hints(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    path = text.archive_path("USen")
    original = dicts.decompress(path, (romfs / path).read_bytes())
    stone = "GOSSIP_KOKIRI_FOREST_01"
    stone_text = "A separate stone hint survives."
    with_stone = text.stone_lines_transform({stone: stone_text})(original)
    transforms = gifts.skulltula_hint_changes(
        romfs, {"Kak 10 Gold Skulltula Reward": "Item_Boomerang", "Kak 40 Gold Skulltula Reward": "Item_Hookshot"}
    )
    changed = sarc.read(transforms[path](with_stone))
    before = sarc.read(with_stone)
    file = "EventFlowMsg/Npc_SkullDad.msbt"
    assert {name for name in before if before[name] != changed[name]} == {file}
    old, new = msbt.read(before[file]), msbt.read(changed[file])
    assert {label for label in old.messages if old.messages[label] != new.messages[label]} == {"Talk_28", "Talk_25"}
    assert visible(new.messages["Talk_28"]) == "For 10 tokens, the reward is Boomerang."
    assert visible(new.messages["Talk_25"]) == "For 40 tokens, the reward is Hookshot."
    assert visible(msbt.read(changed["EventFlowMsg/GossipStone.msbt"]).messages[stone]) == stone_text
