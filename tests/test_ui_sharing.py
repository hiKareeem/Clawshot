"""A player share string replays the real synthetic pipeline, not a second settings codec."""

from pathlib import Path

from test_app import app_source as app_source
from test_app import synthetic_run, synthetic_spec, wait_job
from test_ui import request, running_server

from clawshot.app import Jobs
from clawshot.app.sharing import share_settings
from clawshot.ui.server import Application


def test_shared_seed_replays_identical_output_and_other_versions_cannot_start_work(app_source, tmp_path):
    app = Application(Jobs(synthetic_run), spec=synthetic_spec())
    with running_server(app) as server:
        assert request(server, "shared-seed", {"seed": 42, "settings_string": "Clawshot-99.0:CS1"})[0] == 400
        assert request(server, "shared-seed", {"seed": 42, "settings_string": "CS1"})[0] == 400
        assert request(server, "job")[2]["status"] == "idle"
        imported = request(server, "shared-seed", {"seed": 42, "settings_string": share_settings("CS1")})[2]
        results = []
        for name in ("one", "two"):
            assert (
                request(
                    server,
                    "generate",
                    {
                        "dump": str(app_source),
                        "output": str(tmp_path / name),
                        "seed": imported["seed"],
                        "settings": imported["settings_string"],
                    },
                )[0]
                == 200
            )
            wait_job(app.jobs)
            state = request(server, "job")[2]
            assert state["status"] == "succeeded", state
            results.append(state["result"])
        assert results[0]["output_sha256"] == results[1]["output_sha256"]
        assert results[0]["share_string"] == share_settings(results[0]["settings_string"])

        def files(root):
            return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}

        assert files(Path(results[0]["output"])) == files(Path(results[1]["output"]))
