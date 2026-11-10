"""Small token-authenticated loopback transport; no game launch and no arbitrary file server."""

import json
import os
import secrets
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.metadata import version
from pathlib import Path

from clawshot.app import (
    STAGES,
    GenerationRequest,
    Jobs,
    detect_dump,
    detect_hookshot,
    input_schema,
    presets,
    schema,
    settings_payload,
    validate,
)
from clawshot.app.paths import absolute_path, default_output_root

ASSETS = Path(__file__).with_name("static")
STATIC = {
    "": ("index.html", "text/html"),
    "app.js": ("app.js", "text/javascript"),
    "style.css": ("style.css", "text/css"),
}
MAX_BODY = 65536


class Application:
    def __init__(self, jobs=None, *, spec=None, chooser=None, allow_open=False):
        self.jobs = jobs if jobs is not None else Jobs()
        self.spec = spec
        self.chooser = chooser
        self.allow_open = allow_open

    def call(self, method, route, body):
        if method == "GET" and route == "schema":
            return {
                "schema": schema(),
                "version": version("clawshot"),
                "output_root": str(default_output_root()),
                "dialogs_available": self.chooser is not None,
                "open_available": self.allow_open,
                "presets": presets(spec=self.spec),
                "inputs": input_schema(),
                "stages": [{"key": key, "label": label, "status": "pending", "seconds": 0} for key, label in STAGES],
                **settings_payload(validate({}, spec=self.spec)),
            }
        if method == "GET" and route == "job":
            return self.jobs.snapshot()
        if method == "POST" and route == "settings":
            return settings_payload(validate(body.get("values"), text=body.get("settings_string"), spec=self.spec))
        if method == "POST" and route == "normalize-path":
            return {"path": str(absolute_path(body.get("path"), "Path"))}
        if method == "POST" and route == "browse":
            if self.chooser is None:
                raise ValueError("Path dialogs are disabled in --no-open and tests; paste a path instead")
            kind = body.get("kind")
            if kind not in ("dump-folder", "dump-file", "hookshot", "output"):
                raise ValueError("Unknown path chooser")
            seed = body.get("seed", 0)
            if type(seed) is not int or not -(2**53 - 1) <= seed <= 2**53 - 1:
                raise ValueError("Seed must be an exact integer")
            path = self.chooser(kind)
            if path is not None:
                selected = absolute_path(str(path), "Selected path")
                if kind == "dump-file":
                    if not selected.is_file() or selected.suffix.lower() != ".nup":
                        raise ValueError("Choose a .nup file")
                elif not selected.is_dir():
                    raise ValueError("Choose an existing folder")
                path = str(selected / f"seed-{seed}") if kind == "output" else str(selected)
            return {"path": path}
        if method == "POST" and route == "detect":
            result = {}
            if body.get("dump"):
                result["dump"] = detect_dump(body["dump"])
            if body.get("hookshot"):
                result["hookshot"] = detect_hookshot(body["hookshot"])
            if not result:
                raise ValueError("Enter a dump or Hookshot path")
            return result
        if method == "POST" and route == "generate":
            request = GenerationRequest(**body)
            validate(text=request.settings, spec=self.spec)
            return self.jobs.start(request)
        if method == "POST" and route == "cancel":
            return self.jobs.cancel()
        if method == "POST" and route in ("result", "open"):
            result = self.jobs.snapshot()["result"]
            if result is None:
                raise ValueError("No completed seed is available")
            root = absolute_path(result["output"], "Result")
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
            path = absolute_path(str(root / names[choice]), "Result document")
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
        if not secrets.compare_digest(self.headers.get("X-Clawshot-Token", ""), server.token):
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
