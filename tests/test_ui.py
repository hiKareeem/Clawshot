"""Run the real loopback server; all files/worlds are synthetic and no GUI is opened."""

import http.client
import json
from contextlib import contextmanager
from pathlib import Path

import pytest
from test_app import synthetic_run, synthetic_spec

from clawshot.app import Jobs
from clawshot.ui.server import Application, LocalServer, serve_in_thread


@contextmanager
def running_server(app=None):
    server = LocalServer(app or Application(Jobs(synthetic_run), spec=synthetic_spec()))
    thread = serve_in_thread(server)
    try:
        yield server
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def request(server, route, body=None, *, token=True, headers=None, path=None, raw=None):
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=10)
    outgoing = {}
    if token:
        outgoing["X-Clawshot-Token"] = server.token
    if body is not None or raw is not None:
        outgoing["Content-Type"] = "application/json"
    outgoing.update(headers or {})
    data = raw if raw is not None else json.dumps(body).encode() if body is not None else None
    try:
        connection.request(
            "POST" if data is not None else "GET", path or server.prefix + "api/" + route, body=data, headers=outgoing
        )
        response = connection.getresponse()
        content = response.read()
        value = (
            json.loads(content) if response.getheader("Content-Type", "").startswith("application/json") else content
        )
        return response.status, dict(response.getheaders()), value
    finally:
        connection.close()


def test_loopback_token_host_and_origin_are_required_for_api_calls():
    with running_server() as server:
        assert server.server_address[0] == "127.0.0.1"
        assert request(server, "schema")[0] == 200
        for headers, token in (
            ({}, False),
            ({"Origin": "https://untrusted.example"}, True),
            ({"Origin": "null"}, True),
            ({"Sec-Fetch-Site": "cross-site"}, True),
            ({"Host": "attacker.example"}, True),
            ({"X-Clawshot-Token": "é"}, True),
        ):
            status, returned, _ = request(server, "schema", headers=headers, token=token)
            assert status == 403
            assert "Access-Control-Allow-Origin" not in returned
        assert request(server, "schema", path="/s/wrong/api/schema")[0] == 403
        with LocalServer() as second:
            assert second.token != server.token


def test_static_allowlist_does_not_serve_paths_or_the_repository():
    with running_server() as server:
        status, headers, _ = request(server, "", path=server.prefix)
        assert status == 200 and headers["Content-Type"].startswith("text/html")
        assert headers["Referrer-Policy"] == "no-referrer"
        assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
        for relative in (
            "../pyproject.toml",
            "%2e%2e/pyproject.toml",
            "src/clawshot/app/paths.py",
            "C:/Windows/win.ini",
            "style.css?file=../pyproject.toml",
            "index.html",
            "api/schema?token=anything",
        ):
            assert request(server, "", path=server.prefix + relative)[0] == 404
        status, headers, _ = request(server, "", path=server.prefix + "app.js")
        assert status == 200 and headers["X-Content-Type-Options"] == "nosniff"
        assert headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize(
    "raw, headers",
    [
        (b"[]", {}),
        (b"{broken", {}),
        (b"{}", {"Content-Type": "text/plain"}),
        (b"{}", {"Content-Length": "70000"}),
        (b"{}", {"Content-Length": "-1"}),
        (b'{"values":{"logic":{"x":NaN}}}', {}),
    ],
)
def test_invalid_request_bodies_cannot_start_work(raw, headers):
    with running_server() as server:
        assert request(server, "settings", raw=raw, headers=headers)[0] == 400
        assert request(server, "job")[2]["status"] == "idle"


def test_no_open_rejects_native_dialogs_and_has_no_completed_folder_to_open():
    with running_server() as server:
        config = request(server, "schema")[2]
        assert not config["dialogs_available"] and not config["open_available"]
        assert request(server, "browse", {"kind": "dump-folder"})[0] == 400
        assert request(server, "open", {"target": "folder"})[0] == 400
        assert request(server, "job")[2]["status"] == "idle"


def test_enabled_browse_validates_selection_without_opening_a_dialog(tmp_path):
    selected = tmp_path
    calls = []

    def chooser(kind):
        calls.append(kind)
        return selected

    app = Application(Jobs(synthetic_run), spec=synthetic_spec(), chooser=chooser, allow_open=True)
    with running_server(app) as server:
        config = request(server, "schema")[2]
        assert config["dialogs_available"] and config["open_available"]
        assert request(server, "browse", {"kind": "output", "seed": 11}, token=False)[0] == 403
        assert request(server, "browse", {"kind": "output", "seed": True})[0] == 400
        assert request(server, "browse", {"kind": "unknown"})[0] == 400
        assert calls == []  # no untrusted/invalid request may trigger an OS dialog
        status, _, value = request(server, "browse", {"kind": "output", "seed": 11})
        assert status == 200 and Path(value["path"]) == tmp_path / "seed-11"
        assert not (tmp_path / "seed-11").exists()  # selecting is not generating/overwriting
        selected = "relative/path"
        assert request(server, "browse", {"kind": "hookshot"})[0] == 400
        selected = tmp_path
        assert request(server, "browse", {"kind": "dump-file"})[0] == 400
        selected = tmp_path / "own.nup"
        selected.write_bytes(b"invented file selection, not a game container")
        status, _, value = request(server, "browse", {"kind": "dump-file"})
        assert status == 200 and Path(value["path"]) == selected


def test_normalized_paths_and_protected_outputs_refuse_without_staging(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    with running_server() as server:
        status, _, value = request(server, "normalize-path", {"path": source.as_posix()})
        assert status == 200 and value["path"] == str(source)
        assert request(server, "normalize-path", {"path": "relative"})[0] == 400
        assert (
            request(
                server, "generate", {"dump": str(source), "output": str(source / "seed"), "seed": 11, "settings": "CS1"}
            )[0]
            == 400
        )
        assert request(server, "job")[2]["status"] == "idle"
        assert not list(source.iterdir()) and not list(tmp_path.glob(".clawshot-job-*"))
