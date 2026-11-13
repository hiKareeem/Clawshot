"""A checked game path persists outside the checkout; invalid replacement paths do not replace it."""

import pytest
from test_app import app_source as app_source
from test_app import synthetic_run, synthetic_spec
from test_app_play import made_ui_seed as made_ui_seed
from test_ui import request, running_server

from clawshot.app import Jobs
from clawshot.app.preferences import Preferences
from clawshot.pack import VERSION_FILES
from clawshot.ui.server import Application


def test_only_a_verified_dump_replaces_the_remembered_game(made_ui_seed, tmp_path):
    _, _, source = made_ui_seed
    config = tmp_path / "user-config/paths.json"
    first = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=Preferences(config))
    with running_server(first) as server:
        assert request(server, "detect", {"dump": str(source)})[0] == 200
    before = config.read_bytes(), config.stat().st_mtime_ns
    (source / VERSION_FILES[1]).write_bytes(b"unsupported synthetic game version")
    second = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=Preferences(config))
    with running_server(second) as server:
        assert request(server, "schema")[2]["paths"]["dump"] == str(source)
        assert request(server, "detect", {"dump": str(source)})[0] == 400
    assert before == (config.read_bytes(), config.stat().st_mtime_ns)


@pytest.mark.parametrize("exists", [False, True])
def test_missing_dump_and_existing_wrong_kind_have_distinct_http_errors(made_ui_seed, tmp_path, exists):
    _, _, source = made_ui_seed
    bad = tmp_path / ("existing.txt" if exists else "missing.nup")
    if exists:
        bad.write_bytes(b"synthetic wrong file kind")
    preferences = Preferences()
    preferences.remember("dump", str(source))
    app = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=preferences)
    with running_server(app) as server:
        status, _, response = request(server, "detect", {"dump": str(bad)})
        assert status == 400
        expected = (
            "Choose an extracted romfs folder or a .nup file"
            if exists
            else f"Not found: {bad}. Choose your romfs folder or .nup again."
        )
        assert response["error"] == expected
        assert request(server, "schema")[2]["paths"]["dump"] == str(source)
