import copy

import pytest
from test_fast_start_mido import run_mido

from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import gamedata, mido

pytestmark = pytest.mark.dump


@pytest.mark.parametrize("sword,shield", [(False, False), (True, False), (False, True), (True, True)])
@pytest.mark.parametrize("meeting", ["Step01", "Step02"])
def test_native_early_talk_finishes_missing_equipment_without_applying_the_tree_skip(romfs, sword, shield, meeting):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    original = evfl.read(dictionaries.decompress(mido.FLOW, (romfs / mido.FLOW).read_bytes()))
    changed = evfl.read(mido.complete_deku_meeting(evfl.write(original)))
    before, before_trace = run_mido(original, sword=sword, shield=shield, meeting=meeting)
    after, trace = run_mido(changed, sword=sword, shield=shield, meeting=meeting)
    cleared = sword and shield
    assert after[mido.BLOCKER] is not cleared
    assert after[mido.MOUTH_OPEN] is cleared and after[mido.SEEN_TREE] is cleared
    if cleared:
        assert before["Step_Meet_DekuTree"] == "Step03" and after["Step_Meet_DekuTree"] == "Complete"
        assert after["Step_Get_StoneOfForest"] == "GoInside"
        split = before_trace.index("Event0")
        assert trace[:split] == before_trace[:split]
        assert trace.index("blocker-ai-ended") < trace.index("ClawshotDekuSeen")
    else:
        assert (after, trace) == (before, before_trace)
        assert after["Step_Get_StoneOfForest"] == "Ready"
    assert "blocker-wait" in trace  # the native initializer is reached, with its wait modeled


def test_native_entry_registration_and_all_pre_clear_content_remain_unchanged(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    original = evfl.read(dictionaries.decompress(mido.FLOW, (romfs / mido.FLOW).read_bytes()))
    changed = evfl.read(mido.complete_deku_meeting(evfl.write(original)))
    assert changed.flowchart.entry_points == original.flowchart.entry_points
    assert changed.flowchart.actors == original.flowchart.actors
    restored = copy.deepcopy(changed)
    restored.flowchart.events = restored.flowchart.events[: len(original.flowchart.events)]
    for index, event in enumerate(original.flowchart.events):
        if event.name in {"Event0", "Event48"}:
            restored.flowchart.events[index] = event
    assert restored == original


@pytest.mark.parametrize("bypassed", [False, True])
def test_tree_skip_presets_only_when_mido_is_also_bypassed(romfs, bypassed):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    path = gamedata.GAME_DATA_LIST
    data = dictionaries.decompress(path, (romfs / path).read_bytes())
    settings = gamedata.load()
    chosen = gamedata.select(settings, ["deku_tree", *(["mido"] if bypassed else [])])
    patched = byml.read(gamedata.patch_initial_values(data, chosen))
    original = byml.read(data)
    for name, value in settings["deku_tree"].game_data.items():
        kind, row = gamedata._find(patched, name)
        expected = gamedata.murmur3_32(value.encode()) if kind == "Enum" else value
        if bypassed:
            assert row["DefaultValue"] == expected
        else:
            assert row == gamedata._find(original, name)[1]
    assert gamedata._find(patched, mido.BLOCKER)[1]["DefaultValue"] is not bypassed
    # The native invisible wall reads the same saved Bool that the equipment clear writes.
    path = "Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs"
    tree = byml.read(dictionaries.decompress(path, (romfs / path).read_bytes()))
    wall = next(actor for actor in tree["Actors"] if actor["Hash"] == 3960132711735390266)
    assert wall["Presence"] == {"FlagName": mido.BLOCKER, "IsCheckLazy": False, "IsNegation": False}
