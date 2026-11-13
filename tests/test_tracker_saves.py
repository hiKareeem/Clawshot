"""Save discovery and the polling session, on synthetic save folders written by the tests."""

import os
import struct
import threading

import pytest
from test_tracker_state import build_save, make_seed
from test_tracker_state import places as places

from clawshot import save
from clawshot.tracker import TrackerSession, choose_slot, list_slots, read_complete
from clawshot.tracker import saves as tracker_saves

ACCOUNT = "0123456789abcdef0123456789abcdef"
SECOND = 1_000_000_000


def write_slot(folder, number, data, mtime):
    slot = folder / f"slot_{number:02d}"
    slot.mkdir(parents=True, exist_ok=True)
    path = slot / "progress.sav"
    path.write_bytes(data)
    os.utime(path, ns=(mtime, mtime))
    return path


def chest(opened: bool) -> bytes:
    return build_save({"IsTreasureBoxOpen.123": opened})


def collected(snapshot):
    return {c["id"]: c["collected"] for a in snapshot["state"]["areas"] for c in a["checks"]}["Test Chest"]


def test_slots_in_runtime_and_emulator_layouts(tmp_path):
    user = tmp_path / "user" / "save" / ACCOUNT
    write_slot(user, 0, b"a", 5 * SECOND)
    write_slot(user, 2, b"b", 9 * SECOND)
    write_slot(user, 1, b"c", 7 * SECOND)
    (user / "slot_03").mkdir()  # an empty slot folder is not a save
    slots = list_slots(tmp_path / "user")
    top = dict(slots[0], path=None)
    assert top == {"id": "slot_02", "name": "slot_02", "number": 2, "path": None, "mtime_ns": 9 * SECOND, "size": 1}
    assert choose_slot(slots, None)["id"] == "slot_02"
    assert choose_slot(slots, 1)["id"] == choose_slot(slots, "slot_01")["id"] == "slot_01"
    assert choose_slot(slots, 4) is None and choose_slot([], None) is None

    nand = tmp_path / "eden" / "nand" / "user" / "save" / ("0" * 16) / ("AB" * 16)
    write_slot(nand / "0400486024DEC000", 1, b"game", 3 * SECOND)
    write_slot(nand / "0100000000010000", 0, b"other game", 8 * SECOND)
    assert [s["id"] for s in list_slots(tmp_path / "eden")] == ["slot_01"]

    write_slot(tmp_path / "user" / "save" / ("f" * 32), 1, b"second account", 1 * SECOND)
    both = list_slots(tmp_path / "user")
    ids = [s["id"] for s in both]
    assert f"save/{ACCOUNT}/slot_01" in ids and f"save/{'f' * 32}/slot_01" in ids and "slot_02" in ids
    assert choose_slot(both, 1) is None  # two accounts share the number: the id must be given
    assert choose_slot(both, f"save/{'f' * 32}/slot_01")["size"] == len(b"second account")
    assert list_slots(tmp_path / "missing") == []


def test_read_complete_refuses_partial_files():
    good = build_save({"IsTreasureBoxOpen.123": True})
    assert read_complete(good).flag("IsTreasureBoxOpen.123") is True
    header_only = struct.pack("<III", save.MAGIC, 1, save.HEADER_SIZE).ljust(save.HEADER_SIZE, b"\0")
    for partial, message in (
        (header_only, "no Bool entries"),
        (good[: save.HEADER_SIZE], "entry table ends"),
        (good[:-8], "runs past the end"),
        (b"\0" * len(good), "magic"),
    ):
        with pytest.raises(save.SaveError, match=message):
            read_complete(partial)
    pointing = build_save(extra={16: {7: 10**6}})  # a String64 entry's offset past the end of the file
    with pytest.raises(save.SaveError, match="past the"):
        read_complete(pointing)
    assert read_complete(build_save(extra={16: {7: save.HEADER_SIZE}})) is not None


def test_session_reads_on_change_and_keeps_the_last_good_state(tmp_path, places, monkeypatch):
    root = make_seed(tmp_path)
    folder = root / "user" / "save" / ACCOUNT
    path = write_slot(folder, 0, chest(False), 10 * SECOND)
    reads = []
    real = tracker_saves.read_complete
    monkeypatch.setattr(tracker_saves, "read_complete", lambda data: reads.append(len(data)) or real(data))

    session = TrackerSession()
    first = session.configure(root)
    assert (first["status"], first["selected_slot"], first["save_folder"]) == ("ok", "slot_00", str(root / "user"))
    assert collected(first) is False and len(reads) == 1
    again = session.snapshot()
    assert again["revision"] == first["revision"] and len(reads) == 1  # unchanged file: not read again

    write_slot(folder, 0, chest(True), 11 * SECOND)
    opened = session.snapshot()
    assert (opened["status"], collected(opened), len(reads)) == ("ok", True, 2)
    assert opened["revision"] > first["revision"]

    header_only = struct.pack("<III", save.MAGIC, 1, save.HEADER_SIZE).ljust(save.HEADER_SIZE, b"\0")
    for number, partial in enumerate((header_only, chest(False)[:-8]), 12):
        write_slot(folder, 0, partial, number * SECOND)
        stale = session.snapshot()
        assert stale["status"] == "stale" and collected(stale) is True  # the last complete read stays
        assert stale["revision"] == opened["revision"] and "last complete read" in stale["warnings"][0]
        assert session.snapshot()["revision"] == opened["revision"]  # the same bad file is not re-read
    reads_before = len(reads)
    session.snapshot()
    assert len(reads) == reads_before

    write_slot(folder, 0, chest(False), 20 * SECOND)
    recovered = session.snapshot()
    assert (recovered["status"], collected(recovered)) == ("ok", False)

    path.unlink()  # replaced by the game: briefly missing
    vanished = session.snapshot()
    assert vanished["status"] == "stale" and collected(vanished) is False


def test_session_slot_override_newest_and_waiting(tmp_path, places):
    root = make_seed(tmp_path)
    folder = root / "user" / "save" / ACCOUNT
    session = TrackerSession()
    waiting = session.configure(root)
    assert waiting["status"] == "waiting" and waiting["state"] is not None and waiting["selected_slot"] is None
    assert collected(waiting) is None

    write_slot(folder, 1, chest(True), 5 * SECOND)
    write_slot(folder, 2, chest(False), 6 * SECOND)
    assert session.snapshot()["selected_slot"] == "slot_02"
    pinned = session.configure(root, slot=1)
    assert (pinned["selected_slot"], collected(pinned)) == ("slot_01", True)
    write_slot(folder, 2, chest(False), 9 * SECOND)
    assert session.snapshot()["selected_slot"] == "slot_01"
    missing = session.configure(root, slot="slot_07")
    assert missing["status"] == "waiting" and "slot_07" in missing["warnings"][0]

    elsewhere = tmp_path / "picked"
    write_slot(elsewhere, 3, chest(True), 4 * SECOND)
    picked = session.configure(root, save_folder=elsewhere)
    assert (picked["save_folder"], picked["selected_slot"], collected(picked)) == (str(elsewhere), "slot_03", True)


def test_session_states_without_seed_or_folder(tmp_path, places):
    session = TrackerSession()
    assert session.snapshot()["status"] == "unconfigured"
    broken = session.configure(tmp_path / "nothing-here")
    assert broken["status"] == "error" and broken["state"] is None and "does not exist" in broken["warnings"][0]
    raw = make_seed(tmp_path, layout="raw", name="raw")  # <raw>/seed/spoiler.json, no manifest and no user folder
    loose = session.configure(raw / "seed")
    assert loose["status"] == "no_save_folder" and loose["state"]["seed"]["layout"] == "raw"


def test_session_never_writes_and_is_thread_safe(tmp_path, places):
    root = make_seed(tmp_path)
    folder = root / "user" / "save" / ACCOUNT
    path = write_slot(folder, 0, chest(True), 10 * SECOND)
    before = sorted(p.relative_to(root) for p in root.rglob("*")), path.read_bytes(), path.stat().st_mtime_ns
    session = TrackerSession()
    session.configure(root, show_locations=True)
    results = []

    def poll():
        for _ in range(20):
            results.append(session.snapshot())

    threads = [threading.Thread(target=poll) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len({(r["revision"], r["status"]) for r in results}) == 1
    assert all(r["show_locations"] and r["state"]["show_locations"] for r in results)
    results[0]["state"]["areas"].clear()  # a caller's copy, not the session's
    assert session.snapshot()["state"]["areas"]
    after = sorted(p.relative_to(root) for p in root.rglob("*")), path.read_bytes(), path.stat().st_mtime_ns
    assert after == before
