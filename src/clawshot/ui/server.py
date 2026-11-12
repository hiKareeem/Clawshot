"""Token-authenticated loopback transport; native actions require explicit normal-session capability."""

import json
import os
import secrets
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.metadata import version
from pathlib import Path

from clawshot.app import (
    STAGES,
    GenerationRequest,
    Jobs,
    Player,
    detect_dump,
    detect_hookshot,
    input_schema,
    presets,
    schema,
    validate,
)
from clawshot.app.emulator import copy_to_emulator
from clawshot.app.library import SeedLibrary
from clawshot.app.paths import absolute_path, default_output_root
from clawshot.app.play import play_refusal
from clawshot.app.preferences import Preferences, suggested_eden_folder
from clawshot.app.sharing import import_settings, player_settings, share_settings
from clawshot.ui.dialogs import FILE_KINDS, KINDS

ASSETS = Path(__file__).with_name("static")
STATIC = {
    "": ("index.html", "text/html"),
    "app.js": ("app.js", "text/javascript"),
    "style.css": ("style.css", "text/css"),
}
MAX_BODY = 65536
WINDOW_KEYS = ("x", "y", "width", "height")


def check_id(value):
    if type(value) is not int or not 0 <= value <= 2**53 - 1:
        raise ValueError("Check id must be a whole number")
    return value


def browser_window(value):
    """The page's own screen rectangle, used only to center a native dialog over it; anything odd means none."""
    if not isinstance(value, dict) or set(value) != set(WINDOW_KEYS):
        return None
    if not all(type(value[key]) is int and -100000 <= value[key] <= 100000 for key in WINDOW_KEYS):
        return None
    if value["width"] <= 0 or value["height"] <= 0:
        return None
    return {key: value[key] for key in WINDOW_KEYS}


class Application:
    def __init__(self, jobs=None, *, spec=None, chooser=None, allow_open=False, allow_play=False, preferences=None):
        self.jobs = jobs if jobs is not None else Jobs()
        self.spec = spec
        self.chooser = chooser
        self.allow_open = allow_open
        self.allow_play = allow_play
        self.player = Player()
        self.preferences = preferences if preferences is not None else Preferences()
        self.library = SeedLibrary(self.preferences)
        self.selected = None
        self.editing = False
        self.checks_lock = threading.Lock()
        self.cancelled_checks = set()

    def remember_completed(self):
        state = self.jobs.snapshot()
        if state["status"] == "succeeded" and state["result"]:
            parent = Path(state["result"]["output"]).parent
            if parent != default_output_root() and str(parent) not in self.preferences.snapshot().get("seed_roots", []):
                self.library.add_folder(str(parent))

    def job_view(self):
        self.remember_completed()
        state = self.jobs.snapshot()
        if self.selected is not None:
            state = {"status": "loaded", "result": self.selected, "stages": [], "error": None, "seconds": 0}
        elif self.editing and state["status"] not in ("running", "cancelling"):
            state = {"status": "idle", "result": None, "stages": [], "error": None, "seconds": 0}
        if state["result"] is not None:
            result = state["result"]
            state = state | {
                "result": result
                | {
                    "share_string": share_settings(result["settings_string"], result["clawshot_version"]),
                    "short_hash": result["output_sha256"][:12].upper(),
                }
            }
        return state | {"play": self.player.snapshot()}

    def result_for(self, body):
        self.remember_completed()
        if body.get("output") is not None:
            return self.library.get(body["output"], verify=False)
        return self.selected if self.selected is not None else self.jobs.snapshot()["result"]

    def call(self, method, route, body):
        if method == "GET" and route == "schema":
            choices = presets(spec=self.spec)
            recommended = next(p for p in choices if p["id"] == "recommended")
            return {
                "schema": schema(),
                "version": version("clawshot"),
                "output_root": str(default_output_root()),
                "paths": self.preferences.snapshot(),
                "preferences_warning": self.preferences.warning,
                "dialogs_available": self.chooser is not None,
                "copy_available": self.chooser is not None,
                "eden_folder": suggested_eden_folder(),
                "open_available": self.allow_open,
                "play_available": self.allow_play and not play_refusal(),
                "play_unavailable_reason": (
                    "Play needs Windows or Linux. Use the emulator steps below."
                    if play_refusal()
                    else "Play is disabled in --no-open. Open Clawshot normally to play."
                ),
                "presets": [p | {"share_string": share_settings(p["settings_string"])} for p in choices],
                "inputs": input_schema(),
                "stages": [{"key": key, "label": label, "status": "pending", "seconds": 0} for key, label in STAGES],
                **player_settings(validate(text=recommended["settings_string"], spec=self.spec)),
            }
        if method == "GET" and route == "job":
            return self.job_view()
        if method == "GET" and route == "seeds":
            self.remember_completed()
            return {
                "seeds": self.library.entries(),
                "folders": [str(path) for path in self.library.folders()],
                "warning": self.preferences.warning,
            }
        if method == "POST" and route == "select-seed":
            if self.jobs.snapshot()["status"] in ("running", "cancelling"):
                raise ValueError("Wait for the current seed to finish, or Cancel it before choosing another.")
            if body.get("output") is None:
                self.selected = None
                self.editing = True
            else:
                entry = self.library.get(body["output"])
                if not entry["playable"]:
                    raise ValueError(entry["reason"])
                self.selected = entry
                self.editing = False
            return self.job_view()
        if method == "POST" and route == "settings":
            return player_settings(validate(body.get("values"), text=body.get("settings_string"), spec=self.spec))
        if method == "POST" and route in ("import-settings", "shared-seed"):
            if route == "shared-seed":
                number = body.get("seed")
                if type(number) is not int or not -(2**53 - 1) <= number <= 2**53 - 1:
                    raise ValueError("Enter an exact whole seed number.")
            payload = player_settings(import_settings(body.get("settings_string"), spec=self.spec))
            return payload | ({"seed": number} if route == "shared-seed" else {})
        if method == "POST" and route == "normalize-path":
            kind = body.get("kind", "output")
            if kind not in ("dump", "update", "hookshot", "output"):
                raise ValueError("Choose a game, update, Hookshot or output path.")
            return {"path": str(absolute_path(body.get("path"), "Path", allow_links=kind != "output"))}
        if method == "POST" and route == "browse":
            if self.chooser is None:
                raise ValueError("Path dialogs are disabled in --no-open and tests; paste a path instead")
            kind = body.get("kind")
            if kind not in KINDS:
                raise ValueError("Unknown path chooser")
            seed = body.get("seed", 0)
            if type(seed) is not int or not -(2**53 - 1) <= seed <= 2**53 - 1:
                raise ValueError("Seed must be an exact integer")
            path = self.chooser(kind, browser_window(body.get("window")))
            if path is not None:
                selected = absolute_path(
                    str(path), "Selected path", allow_links=kind not in ("output", "emulator_mods")
                )
                if kind in FILE_KINDS:
                    if not selected.is_file() or selected.suffix.lower() != ".nup":
                        raise ValueError("Choose a .nup file")
                elif not selected.is_dir():
                    raise ValueError("Choose an existing folder")
                path = str(selected / f"seed-{seed}") if kind == "output" else str(selected)
                if kind == "seeds":
                    self.library.add_folder(path)
                elif kind == "emulator_mods":
                    self.preferences.remember("emulator_mods", path)
            return {"path": path, "warning": self.preferences.warning}
        if method == "POST" and route == "cancel-check":
            check = check_id(body.get("check"))
            with self.checks_lock:
                if len(self.cancelled_checks) > 100:
                    self.cancelled_checks.clear()
                self.cancelled_checks.add(check)
            return {"cancelled": check}
        if method == "POST" and route == "detect":
            check = check_id(body.get("check", 0))
            result = {}
            try:
                if body.get("dump"):
                    update = body.get("update") or None
                    result["dump"] = detect_dump(body["dump"], update)
                if body.get("hookshot"):
                    result["hookshot"] = detect_hookshot(body["hookshot"])
                if not result:
                    raise ValueError("Enter a dump or Hookshot path")
                with self.checks_lock:  # a cancelled check's answer is dropped, and nothing is remembered from it
                    if check in self.cancelled_checks:
                        raise ValueError("Check cancelled.")
            finally:  # answered or failed, this id is done: a later check that reuses it must not read as cancelled
                with self.checks_lock:
                    self.cancelled_checks.discard(check)
            if "dump" in result:
                self.preferences.remember("dump", result["dump"]["path"])
                self.preferences.remember("update", result["dump"]["update"] or "")
            if "hookshot" in result:
                self.preferences.remember("hookshot", result["hookshot"]["folder"])
            result["warning"] = self.preferences.warning
            return result
        if method == "POST" and route == "generate":
            request = GenerationRequest(**body)
            validate(text=request.settings, spec=self.spec)
            state = self.jobs.start(request)
            self.selected = None
            self.editing = False
            return state
        if method == "POST" and route == "cancel":
            return self.jobs.cancel()
        if method == "POST" and route in ("choose-eden", "copy-emulator"):
            if self.chooser is None:
                raise ValueError("Emulator copying is disabled in --no-open. Open Clawshot normally to copy a seed.")
            if route == "choose-eden":
                folder = suggested_eden_folder()
                if folder is None:
                    raise ValueError("No Eden mod folder was found. Use Choose mod folder for your emulator.")
                self.preferences.remember("emulator_mods", folder)
                return {"path": folder, "warning": self.preferences.warning}
            if body.get("confirmed") is not True:
                raise ValueError("Back up your emulator's normal saves, then confirm copying this seed.")
            saved = self.preferences.snapshot()
            if not saved.get("emulator_mods"):
                raise ValueError("Choose your emulator's mod folder for this game first.")
            protected = (saved.get("dump"), saved.get("update"), saved.get("hookshot"), os.environ.get("OOT_ROMFS"))
            return copy_to_emulator(self.result_for(body), saved["emulator_mods"], protected=protected)
        if method == "POST" and route == "play":
            if not self.allow_play:
                raise ValueError("Play is disabled in --no-open. Open Clawshot normally to play.")
            return self.player.start(self.result_for(body), body.get("hookshot"))
        if method == "POST" and route in ("result", "open"):
            result = self.result_for(body)
            if result is None:
                raise ValueError("No completed seed is available")
            base = absolute_path(result["output"], "Result")
            root = absolute_path(str(base / "seed"), "Seed files") if (base / "seed").is_dir() else base
            if route == "open":
                if not self.allow_open:
                    raise ValueError("Opening folders is disabled in --no-open and tests")
                if body.get("target") != "folder":
                    raise ValueError("Only the generated folder can be opened")
                if not root.is_dir():
                    raise ValueError("Result folder is missing")
                if sys.platform == "win32":
                    os.startfile(root)
                else:
                    subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(root)])
                return {"opened": True}
            names = {"note": "play-note.md", "spoiler": "spoiler.json"}
            choice = body.get("file")
            if choice not in names:
                raise ValueError("Unknown result document")
            if choice == "spoiler" and body.get("confirmed") is not True:
                raise ValueError("Confirm revealing the spoiler first")
            path = absolute_path(str(base / "seed" / names[choice]), "Result document")
            return {"text": path.read_text(encoding="utf-8"), "name": names[choice]}
        raise LookupError("Unknown endpoint")

    def close(self):
        self.jobs.close()


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = False

    def __init__(self, app=None):
        self.app = app if app is not None else Application()
        self.token = secrets.token_urlsafe(32)
        super().__init__(("127.0.0.1", 0), Handler)
        self.origin = f"http://127.0.0.1:{self.server_port}"
        self.prefix = f"/s/{self.token}/"
        self.url = self.origin + self.prefix

    def server_close(self):
        super().server_close()
        self.app.close()


class Handler(BaseHTTPRequestHandler):
    server_version = "Clawshot"
    sys_version = ""

    def setup(self):
        super().setup()
        self.connection.settimeout(10)
        self.body_consumed = False

    def finish(self):
        # Closing a rejected POST with unread bytes can reset TCP and discard its error response on Windows.
        # Drain only a bounded amount for a bounded time; never trust a rejected Content-Length.
        if getattr(self, "command", None) == "POST" and not self.body_consumed:
            self.connection.settimeout(0.05)
            deadline = time.monotonic() + 0.05
            remaining = MAX_BODY + 1
            try:
                while remaining and time.monotonic() < deadline:
                    chunk = self.rfile.read1(remaining)
                    if not chunk:
                        break
                    remaining -= len(chunk)
            except OSError:
                pass  # Peer closed, or the bounded drain expired; the original error has already been sent.
        super().finish()

    def log_message(self, *_):
        pass  # No token/path logging to external access logs.

    def reply(self, status, value, content_type="application/json"):
        raw = json.dumps(value, ensure_ascii=False).encode("utf-8") if content_type == "application/json" else value
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
        )
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        self.dispatch("GET")

    def do_POST(self):
        self.dispatch("POST")

    def dispatch(self, method):
        server = self.server
        if (
            self.headers.get("Host") != server.origin.removeprefix("http://")
            or self.headers.get("Origin", server.origin) != server.origin
            or self.headers.get("Sec-Fetch-Site") == "cross-site"
            or not self.path.startswith(server.prefix)
        ):
            self.reply(403, {"error": "Local UI authorization required"})
            return
        route = self.path[len(server.prefix) :]
        if method == "GET" and route in STATIC:
            filename, content_type = STATIC[route]
            self.reply(200, (ASSETS / filename).read_bytes(), content_type)
            return
        if not route.startswith("api/"):
            self.reply(404, {"error": "Not found"})
            return
        supplied_token = self.headers.get("X-Clawshot-Token", "")
        if not supplied_token.isascii() or not secrets.compare_digest(supplied_token, server.token):
            self.reply(403, {"error": "Local UI token required"})
            return
        try:
            body = {}
            if method == "POST":
                if self.headers.get("Content-Type") != "application/json":
                    raise ValueError("Expected application/json")
                if self.headers.get("Transfer-Encoding"):
                    raise ValueError("Chunked requests are not accepted")
                length = int(self.headers.get("Content-Length", "-1"))
                if not 0 < length <= MAX_BODY:
                    raise ValueError("JSON body must be 1..65536 bytes")
                raw = self.rfile.read(length)
                self.body_consumed = len(raw) == length
                body = json.loads(raw)
                if not isinstance(body, dict):
                    raise ValueError("JSON body must be an object")
            result = server.app.call(method, route[4:], body)
            self.reply(200, result)
        except LookupError:
            self.reply(404, {"error": "Unknown endpoint"})
        except (ValueError, TypeError, OSError) as error:
            self.reply(400, {"error": str(error)})


def serve_in_thread(server):
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread
