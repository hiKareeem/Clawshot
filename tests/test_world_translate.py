"""The committed world files are what the translator writes from OoT Randomizer at port.toml's commit.

Needs an OoT-Randomizer checkout in ``OOTR_DIR`` (e.g. ``E:/OOTRemake/work/r2-world/OoT-Randomizer``); skipped
otherwise.
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
    # A rerun over the committed files: hand-written fields (vanilla_fixed, n64_only) are read back from them.
    for name in ["port.toml", *region_files]:
        shutil.copy(DATA_DIR / name, tmp_path / name)
    translate(Path(OOTR_DIR).resolve(), tmp_path)
    for name in [*region_files, "helpers.toml", "items.toml", "settings.toml"]:
        assert (tmp_path / name).read_bytes() == (DATA_DIR / name).read_bytes(), name
