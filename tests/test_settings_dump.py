"""Settings-string replay through the public CLI, using read-only player resources."""

import json
import os
import subprocess
import sys

import pytest

from clawshot.generate import Settings

pytestmark = pytest.mark.dump


def test_settings_string_and_spoiler_replay_write_identical_folders(romfs, tmp_path):
    settings = Settings(
        shuffle=("Chest", "Gift"),
        areas=("KokiriForest", "LostWood", "InsideTheDekuTree"),
        goal="'Defeat Queen Gohma'",
        fast_start=("intro", "mido"),
        logic={"free_time_travel": True, "age_return_guarantee": False},
    )
    text = settings.to_string()
    folders = []
    for hash_seed in ("1", "31337"):
        out = tmp_path / hash_seed
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "clawshot",
                "--romfs",
                str(romfs),
                "--seed",
                "7",
                "--out",
                str(out),
                "--settings",
                text,
            ],
            env={**os.environ, "PYTHONHASHSEED": hash_seed},
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (result.returncode, result.stdout, result.stderr)
        files = {
            path.relative_to(out).as_posix(): path.read_bytes() for path in sorted(out.rglob("*")) if path.is_file()
        }
        folders.append(files)
        log = json.loads(files["spoiler.json"])
        text = log["settings_string"]  # Replay the expanded gift policy, not just the CLI inputs.
        assert Settings.from_string(text).as_dict() == log["settings"]
        assert log["settings"]["logic"]["free_time_travel"] is True
        assert log["settings"]["logic"]["age_return_guarantee"] is False
        assert "romfs/Banc/Market/Market_Adult_Static.bcett.byml.zs" in files
    assert folders[0] == folders[1]
