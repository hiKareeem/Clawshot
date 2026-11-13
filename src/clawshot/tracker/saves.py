"""Which save to read, read safely while the game writes it, and a polling session for the UI.

Save layout (sloperina-FINDINGS.md section 1, "Save files"; plans/03-game-data.md section 6, ``MetaData``):
``slot_NN/progress.sav`` beside ``option.sav``/``account.sav``. Hookshot and Longshot keep them in
``<--user folder>/save/<account id>/``; emulators under ``nand/user/save/0000000000000000/<user id>/
0400486024DEC000/``. :func:`list_slots` finds slot folders anywhere a few levels under the chosen folder.

Nothing here writes to a save folder: files are opened read-only, once per change of (path, mtime, size).
"""

import copy
import os
import re
import stat
import threading
from pathlib import Path
from typing import Any

from clawshot import save as save_format
from clawshot.tracker import state as tracker_state
from clawshot.tracker.seeds import Seed, SeedError, load_seed

SLOT = re.compile(r"^slot_(\d{2})$")
PROGRESS = "progress.sav"
GAME_SAVE_ID = "0400486024dec000"  # the game's save-data folder in an emulator NAND (sloperina section 1)
_TITLE_FOLDER = re.compile(r"^[0-9a-fA-F]{16}$")
MAX_DEPTH = 8  # an emulator's nand/user/save/<zeros>/<user>/<game>/slot_NN from its data folder is 7 deep
MAX_FOLDERS = 5000  # stop walking a folder that is clearly not a save folder (a whole drive)
MAX_SAVE_BYTES = 16 << 20
# Types whose entry value is a file offset rather than the value itself (clawshot.save: Bool, Int, Float, Enum and
# UInt are stored in the pair; Bool64bitKey's offset is checked by the reader).
_INLINE = {save_format.BOOL, save_format.INT, save_format.FLOAT, save_format.ENUM, save_format.UINT, save_format.BOOL64}


def _walk(folder: Path):
    """Slot folders under ``folder`` (itself included), never following links, depth- and size-bounded."""
    stack = [(folder, 0)]
    visited = 0
    while stack:
        current, depth = stack.pop()
        visited += 1
        if visited > MAX_FOLDERS:
            return
        if SLOT.match(current.name):
            yield current
            continue
        if depth >= MAX_DEPTH:
            continue
        try:
            entries = sorted(os.scandir(current), key=lambda e: e.name)
        except OSError:
            continue
        for entry in entries:
            if entry.name.startswith("."):
                continue
            try:
                if not entry.is_dir(follow_symlinks=False) or entry.is_junction():
                    continue
            except OSError:
                continue
            # In an emulator NAND, other games' 16-digit save folders sit beside this game's one; the all-zero
            # system folder above them is kept (sloperina section 1's path).
            name = entry.name.lower()
            if _TITLE_FOLDER.match(name) and name not in (GAME_SAVE_ID, "0" * 16):
                continue
            stack.append((Path(entry.path), depth + 1))


def list_slots(folder: str | Path) -> list[dict[str, Any]]:
    """Every ``slot_NN/progress.sav`` under ``folder``, newest first (by the file's mtime, then id).

    Each entry: ``id`` (``slot_NN``, or the folder path relative to ``folder`` when two accounts share a number),
    ``name`` (``slot_NN``), ``number``, ``path`` (of ``progress.sav``), ``mtime_ns`` and ``size``."""
    folder = Path(folder)
    if not folder.is_dir():
        return []
    found = []
    for slot in _walk(folder):
        progress = slot / PROGRESS
        try:
            info = progress.lstat()
        except OSError:
            continue
        if not stat.S_ISREG(info.st_mode):
            continue
        found.append((slot, progress, info))
    names = [slot.name for slot, _, _ in found]
    entries = []
    for slot, progress, info in found:
        relative = slot.relative_to(folder).as_posix() if slot != folder else slot.name
        entries.append(
            {
                "id": slot.name if names.count(slot.name) == 1 else relative,
                "name": slot.name,
                "number": int(SLOT.match(slot.name).group(1)),
                "path": str(progress),
                "mtime_ns": info.st_mtime_ns,
                "size": info.st_size,
            }
        )
    entries.sort(key=lambda e: (-e["mtime_ns"], e["id"]))
    return entries


def choose_slot(slots: list[dict[str, Any]], slot: str | int | None) -> dict[str, Any] | None:
    """The newest slot, or the one ``slot`` names (an id, ``slot_NN`` or the number NN); None when absent."""
    if not slots:
        return None
    if slot is None:
        return slots[0]
    if isinstance(slot, int):
        matches = [s for s in slots if s["number"] == slot]
    else:
        matches = [s for s in slots if s["id"] == slot] or [s for s in slots if s["name"] == slot]
    return matches[0] if len(matches) == 1 else None


def read_complete(data: bytes) -> save_format.Save:
    """Parse ``progress.sav`` bytes and refuse anything a half-written file could be.

    Beyond ``clawshot.save.read`` (magic, table bounds, known sections, the Bool64bitKey list's end): the entry table
    must hold entries, the Bool, Int and Bool64bitKey sections must be there with values, and every offset-valued
    entry (strings, arrays, binaries) must point inside the file, so a header-only or truncated copy never replaces
    a good read."""
    if len(data) > MAX_SAVE_BYTES:
        raise save_format.SaveError(f"{len(data)} bytes, larger than any game save")
    parsed = save_format.read(data)
    for section in (save_format.BOOL, save_format.INT):
        if not parsed.entries.get(section):
            raise save_format.SaveError(f"no {save_format.TYPES[section]} entries: an incomplete save")
    if parsed.save_type is None:
        raise save_format.SaveError("no Bool64bitKey list: an incomplete save")
    for section, entries in parsed.entries.items():
        if section in _INLINE:
            continue
        for value in entries.values():
            if not save_format.HEADER_SIZE <= value < len(data):
                kind = save_format.TYPES[section]
                raise save_format.SaveError(f"a {kind} entry points at 0x{value:x}, past the 0x{len(data):x}-byte file")
    return parsed


class TrackerSession:
    """The UI's tracker: one seed, one save folder, the newest (or chosen) slot. Thread-safe.

    ``configure(seed_path, save_folder=None, slot=None, show_locations=False)`` loads the seed and returns
    :meth:`snapshot`. ``snapshot()`` re-reads the save only when its (path, mtime, size) changed; a save that does not
    read completely keeps the previous good state, marked ``status: "stale"`` with a warning.

    Snapshot: ``status`` (``unconfigured``, ``error``, ``no_save_folder``, ``waiting``, ``ok``, ``stale``),
    ``state`` (``clawshot.tracker.state.build_state``'s dict, or None), ``slots`` (:func:`list_slots`),
    ``selected_slot`` (an id or None), ``save_folder``, ``seed_path``, ``show_locations``, ``revision`` (grows
    whenever ``state`` changes) and ``warnings``."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._configured = False
        self._seed_path: str | None = None
        self._seed: Seed | None = None
        self._error: str | None = None
        self._folder: Path | None = None
        self._slot: str | int | None = None
        self._show = False
        self._revision = 0
        self._state: dict[str, Any] | None = None
        self._state_slot: str | None = None
        self._read: tuple[str, int, int] | None = None  # (path, mtime_ns, size) of the save behind _state
        self._bad: tuple[tuple[str, int, int], str] | None = None  # last refused file signature and why

    def configure(
        self,
        seed_path: str | Path,
        save_folder: str | Path | None = None,
        slot: str | int | None = None,
        show_locations: bool = False,
    ) -> dict[str, Any]:
        with self._lock:
            self._configured = True
            self._seed_path = str(seed_path)
            self._slot = slot
            self._show = bool(show_locations)
            self._state = self._read = self._bad = self._state_slot = None
            try:
                self._seed = load_seed(seed_path)
                self._error = None
            except (SeedError, OSError) as error:
                self._seed, self._error = None, str(error)
            folder = save_folder if save_folder not in (None, "") else (self._seed and self._seed.user_path)
            self._folder = Path(folder).expanduser() if folder else None
            self._revision += 1
            return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return copy.deepcopy(self._poll())

    def _base(self, status: str, slots: list[dict[str, Any]], selected: str | None, warnings: list[str]) -> dict:
        return {
            "status": status,
            "state": self._state,
            "slots": slots,
            "selected_slot": selected,
            "save_folder": str(self._folder) if self._folder else None,
            "seed_path": self._seed_path,
            "show_locations": self._show,
            "revision": self._revision,
            "warnings": warnings,
        }

    def _set_state(self, state: dict[str, Any], slot: str | None) -> None:
        if state != self._state or slot != self._state_slot:
            self._state, self._state_slot = state, slot
            self._revision += 1

    def _no_save(self) -> None:
        """Show the seed with every save value unknown (built once, not on every poll)."""
        if self._state is None or self._state_slot is not None:
            self._read = None
            self._set_state(tracker_state.build_state(self._seed, None, show_locations=self._show), None)

    def _poll(self) -> dict[str, Any]:
        if not self._configured:
            return self._base("unconfigured", [], None, [])
        if self._seed is None:
            return self._base("error", [], None, [self._error or "No seed loaded."])
        if self._folder is None:
            self._no_save()
            return self._base("no_save_folder", [], None, ["Choose the folder your game saves in."])
        slots = list_slots(self._folder)
        chosen = choose_slot(slots, self._slot)
        if chosen is None:
            if self._read is not None and self._slot is None and Path(self._read[0]).parent.is_dir():
                # The newest save vanished mid-write (written by replacing the file); keep what was read from it.
                warning = "The save is being written; showing the last complete read."
                return self._base("stale", slots, self._state_slot, [warning])
            if self._slot is not None and slots:
                warning = f"No single save slot matches {self._slot!r}."
            elif not self._folder.is_dir():
                warning = f"The save folder does not exist yet: {self._folder}"
            else:
                warning = "No save in this folder yet: save in the game to start tracking."
            self._no_save()
            return self._base("waiting", slots, None, [warning])
        signature = (chosen["path"], chosen["mtime_ns"], chosen["size"])
        if signature == self._read:
            return self._base("ok", slots, chosen["id"], [])
        if self._bad is not None and self._bad[0] == signature:
            return self._stale(slots, chosen, self._bad[1])
        try:
            with open(chosen["path"], "rb") as stream:
                data = stream.read(MAX_SAVE_BYTES + 1)
            after = os.stat(chosen["path"])
        except OSError as error:
            return self._stale(slots, chosen, f"the save could not be read ({error.strerror or error})")
        if (after.st_mtime_ns, after.st_size, len(data)) != (chosen["mtime_ns"], chosen["size"], chosen["size"]):
            return self._stale(slots, chosen, "the save changed while it was read")
        try:
            parsed = read_complete(data)
        except save_format.SaveError as error:
            self._bad = (signature, str(error))
            return self._stale(slots, chosen, str(error))
        self._read, self._bad = signature, None
        self._set_state(tracker_state.build_state(self._seed, parsed, show_locations=self._show), chosen["id"])
        return self._base("ok", slots, chosen["id"], [])

    def _stale(self, slots: list[dict[str, Any]], chosen: dict[str, Any], why: str) -> dict[str, Any]:
        """Keep the last complete read (``stale``), or show the seed alone until one exists (``waiting``)."""
        if self._read is None:
            self._no_save()
            return self._base("waiting", slots, chosen["id"], [f"{chosen['id']}: {why}; waiting for a complete save."])
        return self._base("stale", slots, self._state_slot, [f"{chosen['id']}: {why}; showing the last complete read."])
