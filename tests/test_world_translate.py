"""The committed world files are what the translator writes from OoT Randomizer at port.toml's commit, and the
port covers every region of OoT Randomizer's world (Master Quest aside).

Needs an OoT-Randomizer checkout in ``OOTR_DIR`` (e.g. ``E:/OOTRemake/work/r2-world/OoT-Randomizer``); skipped
otherwise. The remake's overrides (``remake.toml``) are kept apart, so the translation compares byte for byte.
"""

import os
import shutil
import tomllib
from pathlib import Path

import pytest

from clawshot.world.load import DATA_DIR
from clawshot.world.translate import translate

OOTR_DIR = os.environ.get("OOTR_DIR")


@pytest.mark.skipif(not OOTR_DIR, reason="OOTR_DIR is not set")
def test_committed_files_match_the_translator(tmp_path: Path):
    with (DATA_DIR / "port.toml").open("rb") as f:
        region_files = list(tomllib.load(f)["files"])
    shutil.copy(DATA_DIR / "port.toml", tmp_path / "port.toml")
    report = translate(Path(OOTR_DIR).resolve(), tmp_path)
    assert report["regions_not_ported"] == []
    for name in [*region_files, "helpers.toml", "items.toml", "settings.toml"]:
        assert (tmp_path / name).read_bytes() == (DATA_DIR / name).read_bytes(), name
