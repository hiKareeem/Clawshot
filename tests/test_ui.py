"""Run the real loopback server; all files/worlds are synthetic and no GUI is opened."""

import http.client
import json
import multiprocessing
from contextlib import contextmanager
from functools import partial
from pathlib import Path

import pytest
from test_app import app_source as app_source
from test_app import synthetic_run, synthetic_spec, wait_job

from clawshot.app import Jobs
from clawshot.generate import FillError, Settings, generate
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
        assert not config["dialogs_available"] and not config["open_available"] and not config["play_available"]
        assert request(server, "browse", {"kind": "dump-folder"})[0] == 400
        assert request(server, "open", {"target": "folder"})[0] == 400
        assert request(server, "play", {"hookshot": "not-a-game-path"})[0] == 400
        assert request(server, "job")[2]["status"] == "idle"


def test_enabled_browse_validates_selection_without_opening_a_dialog(tmp_path):
    selected = tmp_path
    calls = []

    def chooser(kind, window):
        calls.append((kind, window))
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
        rectangle = {"x": -1440, "y": 25, "width": 1200, "height": 800}
        assert request(server, "browse", {"kind": "dump-file", "window": rectangle})[0] == 200
        assert calls[-1] == ("dump-file", rectangle)
        for odd in ({"x": 1}, {**rectangle, "width": 0}, {**rectangle, "y": True}, {**rectangle, "x": 1.5}, "a"):
            assert request(server, "browse", {"kind": "dump-file", "window": odd})[0] == 200
            assert calls[-1] == ("dump-file", None)  # an odd rectangle only loses centering


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


def held_generation(release, job, stage, report):
    report("validate")
    if not release.wait(10):
        raise RuntimeError("synthetic generation was not released")
    return synthetic_run(job, stage, report)


def test_http_generation_stays_responsive_and_spoiler_needs_consent(app_source, tmp_path):
    release = multiprocessing.get_context("spawn").Event()
    app = Application(Jobs(partial(held_generation, release)), spec=synthetic_spec())
    output = tmp_path / "made"
    with running_server(app) as server:
        status, _, settings = request(server, "settings", {"values": {"forest": "open"}})
        assert status == 200
        restored = request(server, "settings", {"settings_string": settings["settings_string"]})[2]
        assert restored["values"] == settings["values"]
        body = {"dump": str(app_source), "output": str(output), "seed": 7, "settings": settings["settings_string"]}
        assert request(server, "generate", body)[0] == 200
        assert request(server, "job")[2]["status"] == "running"
        assert request(server, "schema")[0] == 200  # blocked worker cannot block the UI server
        assert not output.exists()
        release.set()
        state = wait_job(app.jobs)
        assert state["status"] == "succeeded", state
        assert request(server, "job")[2]["result"]["output"] == str(output)
        assert request(server, "result", {"file": "spoiler"})[0] == 400
        status, _, document = request(server, "result", {"file": "spoiler", "confirmed": True})
        assert status == 200
        spoiler = json.loads(document["text"])
        assert spoiler["seed"] == 7
        assert sorted(spoiler["placements"].values()) == ["Rupees (5)", "Sword"]
        assert any("Sword" in sphere.values() for sphere in spoiler["spheres"])
        assert request(server, "result", {"file": "../source"})[0] == 400
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in output.rglob("*") if p.is_file()}
        assert request(server, "generate", body)[0] == 400
        assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in output.rglob("*") if p.is_file()}


def test_http_cancellation_removes_only_its_private_staging(app_source, tmp_path):
    release = multiprocessing.get_context("spawn").Event()
    app = Application(Jobs(partial(held_generation, release)), spec=synthetic_spec())
    output = tmp_path / "cancelled"
    with running_server(app) as server:
        assert (
            request(server, "generate", {"dump": str(app_source), "output": str(output), "seed": 7, "settings": "CS1"})[
                0
            ]
            == 200
        )
        assert request(server, "job")[2]["status"] == "running"
        assert request(server, "cancel", {})[0] == 200
        assert wait_job(app.jobs)["status"] == "cancelled"
        assert request(server, "result", {"file": "spoiler", "confirmed": True})[0] == 400
        assert not output.exists() and not list(tmp_path.glob(".clawshot-job-*"))
        assert (app_source / "Pack/ZsDic.pack.zs").is_file()


def test_http_failed_fill_keeps_original_error_and_writes_nothing(app_source, tmp_path):
    impossible = synthetic_spec()
    impossible["goal"] = "False"
    with pytest.raises(FillError) as expected:
        generate(impossible, -1, Settings())
    output = tmp_path / "impossible"
    with running_server() as server:
        assert (
            request(
                server, "generate", {"dump": str(app_source), "output": str(output), "seed": -1, "settings": "CS1"}
            )[0]
            == 200
        )
        state = wait_job(server.app.jobs)
        assert state["status"] == "failed", state
        assert state["error"] == {"type": "FillError", "message": str(expected.value)}
        assert not output.exists() and not list(tmp_path.glob(".clawshot-job-*"))


def test_concurrent_output_creation_is_not_overwritten_or_cleaned(app_source, tmp_path):
    release = multiprocessing.get_context("spawn").Event()
    app = Application(Jobs(partial(held_generation, release)), spec=synthetic_spec())
    output = tmp_path / "concurrent"
    with running_server(app) as server:
        assert (
            request(server, "generate", {"dump": str(app_source), "output": str(output), "seed": 7, "settings": "CS1"})[
                0
            ]
            == 200
        )
        output.mkdir()
        marker = output / "played"
        marker.write_bytes(b"created by another owner")
        release.set()
        state = wait_job(app.jobs)
        assert state["status"] == "failed" and state["result"] is None, state
        assert marker.read_bytes() == b"created by another owner"
        assert sorted(p.name for p in output.iterdir()) == ["played"]
        assert not list(tmp_path.glob(".clawshot-job-*"))
