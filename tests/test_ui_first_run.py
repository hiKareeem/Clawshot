"""A checked game path persists outside the checkout; invalid replacement paths do not replace it."""

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
