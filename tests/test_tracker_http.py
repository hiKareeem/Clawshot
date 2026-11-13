"""Exercise saved progress through the real token/loopback HTTP boundary; never start a game."""

import json
import os
import struct
from pathlib import Path

import pytest
from test_ui import request, running_server

from clawshot.app.preferences import Preferences
from clawshot.generate import Settings
from clawshot.save import BOOL, BOOL64, INT, MAGIC, key
from clawshot.tracker.seeds import Place
from clawshot.ui.server import Application


def save_bytes(*, opened=False, held=1, found=2):
    fields = {
        BOOL: {
            "IsTreasureBoxOpen.123": opened,
            "IsTreasureBoxOpen.124": False,
            "DungeonInfo.ForestTemple.IsGetBossKey": False,
            "DungeonInfo.ForestTemple.IsGetMap": True,
            "DungeonInfo.ForestTemple.IsGetCompass": False,
        },
        INT: {
            "DungeonInfo.ForestTemple.SmallKeyNum": held,
            "DungeonInfo.ForestTemple.SmallKeyTotalNum": found,
            "PouchData.Item_Token_Gold.StockNum": 17,
        },
    }
    pairs = []
    for section, values in fields.items():
        pairs.append((0, section))
        pairs.extend((key(name), int(value)) for name, value in values.items())
    pairs.extend(((0, BOOL64), (789, 0)))
    end = 32 + len(pairs) * 8
    pairs[-1] = (789, end)
    # Conflicting raw flag proves HTTP collection uses the named chest Bool, not this raw Hash.
    return (
        struct.pack("<III20x", MAGIC, 1, end)
        + b"".join(struct.pack("<II", *p) for p in pairs)
        + struct.pack("<QQ", 123, 0)
    )


@pytest.fixture
def tracker_seed(tmp_path, monkeypatch):
    import clawshot.tracker.seeds as seeds

    monkeypatch.setattr(
        seeds, "location_index", lambda: {name: Place("Test", None, "Chest") for name in ("Test Chest", "Test Key")}
    )
    root = tmp_path / "output"
    (root / "seed").mkdir(parents=True)
    (root / "seed/spoiler.json").write_text(
        json.dumps(
            {
                "generator": "clawshot 0.2.0",
                "seed": 73,
                "settings": Settings().as_dict(),
                "settings_string": Settings().to_string(),
                "placements": {"Test Chest": "Synthetic secret reward", "Test Key": "Small Key (Forest Temple)"},
                "locations": {
                    "Test Chest": {"name": "Test Chest", "where": "Test", "ids": ["123"]},
                    "Test Key": {"name": "Test Key", "where": "Test", "ids": ["124"]},
                },
                "patch": {
                    "changes": [
                        {"location": name, "id": str(identity), "chest": "Obj_TBox_A_01"}
                        for name, identity in (("Test Chest", 123), ("Test Key", 124))
                    ],
                    "unchanged": [],
                },
            }
        ),
        encoding="utf-8",
    )
    slot = root / "user/save/profile/slot_01/progress.sav"
    slot.parent.mkdir(parents=True)
    slot.write_bytes(save_bytes())
    return root, slot


def forest(snapshot):
    return next(d for d in snapshot["state"]["dungeons"] if d["name"] == "Forest Temple")


def test_http_save_refresh_named_chests_keys_and_spoiler_consent(tracker_seed):
    root, slot = tracker_seed
    before = slot.read_bytes(), slot.stat().st_mtime_ns
    app = Application(preferences=Preferences())
    with running_server(app) as server:
        body = {"seed": str(root)}
        assert request(server, "tracker-configure", body, token=False)[0] == 403
        assert request(server, "tracker-browse", {"kind": "save"})[0] == 400
        status, _, first = request(server, "tracker-configure", body)
        assert status == 200, first
        assert first["state"]["areas"][0]["collected"] == 0
        assert forest(first)["small_keys"]["held"] == 1
        assert forest(first)["small_keys"]["found"] == 2
        assert "Synthetic secret reward" not in json.dumps(first)
        assert (slot.read_bytes(), slot.stat().st_mtime_ns) == before
        assert request(server, "tracker-configure", body | {"show_locations": True})[0] == 400
        shown = request(server, "tracker-configure", body | {"show_locations": True, "confirmed": True})[2]
        assert "Synthetic secret reward" in json.dumps(shown)
        obs = request(server, "tracker-obs")[2]
        assert "Synthetic secret reward" not in json.dumps(obs)
        assert all("checks" not in area for area in obs["state"]["areas"])
        assert "save_folder" not in obs
        # Exercise the actual poll endpoint after a save is replaced, without reconfiguring/reloading.
        slot.write_bytes(save_bytes(opened=True, held=0, found=2))
        os.utime(slot, ns=(before[1] + 10_000_000, before[1] + 10_000_000))
        updated = request(server, "tracker")[2]
        assert updated["revision"] != first["revision"]
        assert forest(updated)["small_keys"]["held"] == 0
        assert forest(updated)["small_keys"]["found"] == 2
        assert updated["state"]["areas"][0]["collected"] == 1
        # A game save in flight must not replace good inventory with a blank tracker.
        slot.write_bytes(b"partial")
        incomplete = request(server, "tracker")[2]
        assert incomplete["state"] == updated["state"]
        assert incomplete["warnings"]


def test_tracker_assets_and_icons_keep_transport_guards(tracker_seed):
    root, _ = tracker_seed
    with running_server(Application(preferences=Preferences())) as server:
        assert request(server, "tracker-configure", {"seed": str(root)})[0] == 200
        for asset in ("tracker.html", "tracker.css", "tracker.js"):
            status, headers, _ = request(server, "", path=server.prefix + asset, token=False)
            assert status == 200
            assert headers["Cache-Control"] == "no-store"
            assert "default-src 'none'" in headers["Content-Security-Policy"]
            assert request(server, "", path=server.prefix + asset, headers={"Origin": "https://evil.example"})[0] == 403
        for actor in ("../../progress.sav", "%2e%2e%2fsecret", "Unlisted_Actor"):
            assert request(server, "", path=server.prefix + "tracker-icons/" + actor + ".png")[0] == 404
        assert request(server, "tracker-obs", token=False)[0] == 403
        assert request(server, "", path="/s/wrong/tracker.html")[0] == 403


def test_tracker_folder_picker_is_explicit_and_read_only(tmp_path):
    calls = []

    def chooser(kind, window):
        calls.append((kind, window))
        return tmp_path

    with running_server(Application(preferences=Preferences(), chooser=chooser)) as server:
        assert request(server, "tracker-browse", {"kind": "bad"})[0] == 400
        assert calls == []
        picked = request(server, "tracker-browse", {"kind": "save"})[2]
        assert Path(picked["path"]) == tmp_path
        assert calls == [("tracker-save", None)]
        assert list(tmp_path.iterdir()) == []
