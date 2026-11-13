"""The skipped field panorama must end the native BGM-suppression interval (section 46)."""

import pytest
from test_fast_start import flag, h

from clawshot.formats import byml, zsdic
from clawshot.formats.byml import I32
from clawshot.patch import gamedata
from clawshot.save import murmur3_32

FIELD_PANORAMA = "HavePlayedEvent.Dm_HrlField_0000"


def panorama_played(data):
    entries = byml.read(data)["Data"]["Bool"]
    return next(row["DefaultValue"] for row in entries if row["Hash"] == murmur3_32(FIELD_PANORAMA.encode()))


@pytest.mark.parametrize("skip", [False, True])
def test_kaepora_skip_writes_the_field_music_release_history(skip):
    settings = gamedata.load()
    names = [FIELD_PANORAMA, *settings["kaepora"].game_data]
    steps = ["NotReady", "Ready", "Step01", "Step02", "Complete"]
    tree = {
        "Data": {
            "Bool": [flag(name, False) for name in dict.fromkeys(names) if name != "Step_Goto_HyruleCastle"],
            "Int": [],
            "Enum": [
                {
                    **flag("Step_Goto_HyruleCastle", h("NotReady")),
                    "RawValues": steps,
                    "Values": [h(step) for step in steps],
                    "ResetTypeValue": I32(8),
                }
            ],
        }
    }
    chosen = gamedata.select(settings, ["kaepora"] if skip else [])
    written = gamedata.patch_initial_values(byml.write(tree, "big"), chosen)
    assert panorama_played(written) is skip


@pytest.mark.dump
def test_native_kaepora_output_ends_the_field_panorama_mute_range(romfs, tmp_path):
    out = tmp_path / "kaepora"
    gamedata.write(romfs, out, ["kaepora"])
    path = gamedata.GAME_DATA_LIST
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    assert panorama_played(dictionaries.decompress(path, (out / "romfs" / path).read_bytes()))
