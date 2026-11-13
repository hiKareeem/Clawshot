"""Small HTTP-facing tracker controller; saves and icon parsing live in the headless package."""

import threading
from pathlib import Path

from clawshot.app.paths import absolute_path
from clawshot.tracker.icons import IconCache, icon_id
from clawshot.tracker.saves import TrackerSession


class TrackerController:
    def __init__(self):
        self.session = TrackerSession()
        self.lock = threading.RLock()
        self.source = ""
        self.icons = None
        self.icon_warning = ""
        self.allowed_icons = set()

    def configure(self, app, body):
        show_locations = body.get("show_locations", False)
        if type(show_locations) is not bool or (show_locations and body.get("confirmed") is not True):
            raise ValueError("Confirm that showing locations reveals unvisited rewards.")
        seed = body.get("seed")
        if seed is None:
            result = app.result_for({})
            if not result:
                raise ValueError("Choose a seed output folder, or first View a seed on Generate.")
            seed = result["output"]
        seed = absolute_path(seed, "Seed output", allow_links=True)
        folder = body.get("save_folder")
        if folder is not None:
            folder = absolute_path(folder, "Save folder", allow_links=True)
            if not folder.is_dir():
                raise ValueError("Choose an existing save folder.")
        slot = body.get("slot")
        if slot is not None and (not isinstance(slot, str) or not slot):
            raise ValueError("Choose a listed save slot, or newest slot.")
        with self.lock:
            source = app.preferences.snapshot().get("dump", "")
            if source != self.source:
                self.source, self.icons, self.icon_warning = source, None, ""
            self.session.configure(seed, save_folder=folder, slot=slot, show_locations=show_locations)
            return self.snapshot()

    def snapshot(self, *, obs=False):
        with self.lock:
            data = self.session.snapshot()
            state = data.get("state")
            self.allowed_icons = set()
            for group in ("items", "songs", "rewards"):
                for cell in (state or {}).get(group, []):
                    actor = cell.get("icon")
                    if actor and icon_id(actor) is not None:
                        self.allowed_icons.add(actor)
                    else:
                        cell["icon"] = None  # No file exists for songs/rewards: ordinary text fallback, not an error.
            identity = (state or {}).get("identity", {})
            if identity.get("status") == "consistent":
                data.setdefault("warnings", []).append(
                    "Save flag layout is consistent, but this does not prove seed identity."
                )
            if self.icon_warning:
                data.setdefault("warnings", []).append(self.icon_warning)
            if obs:
                # OBS is permanently spoiler-free even while the app's explicit spoiler mode is enabled.
                data["show_locations"] = False
                if state is not None:
                    state["show_locations"] = False
                for area in (state or {}).get("areas", []):
                    area.pop("checks", None)
                data.pop("save_folder", None)
                data.pop("slots", None)
                data.pop("save_path", None)
            return data

    def icon(self, actor):
        with self.lock:
            if actor not in self.allowed_icons or not self.source:
                return None
            if self.icons is None:
                self.icons = IconCache(Path(self.source))
            path = self.icons.get(actor)
            if path is None:
                self.icon_warning = "Some local icons are unavailable; text labels remain complete."
                return None
            return path.read_bytes()


def call(app, method, route, body):
    if method == "POST" and route == "tracker-configure":
        return app.tracker.configure(app, body)
    if method == "GET" and route in ("tracker", "tracker-obs"):
        return app.tracker.snapshot(obs=route == "tracker-obs")
    if method == "POST" and route == "tracker-browse":
        if app.chooser is None:
            raise ValueError("Path dialogs are disabled in --no-open; paste a path instead.")
        kind = body.get("kind")
        if kind not in ("seed", "save"):
            raise ValueError("Choose a seed or save folder.")
        path = app.chooser("tracker-" + kind, None)
        if path is not None:
            path = absolute_path(str(path), "Selected folder", allow_links=True)
            if not path.is_dir():
                raise ValueError("Choose an existing folder.")
        return {"path": str(path) if path is not None else None}
    raise LookupError("Unknown tracker endpoint")
