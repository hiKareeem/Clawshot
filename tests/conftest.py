import os
from pathlib import Path

import pytest


def pytest_collection_modifyitems(config, items):
    if os.environ.get("OOT_ROMFS"):
        return
    skip = pytest.mark.skip(reason="OOT_ROMFS is not set")
    for item in items:
        if "dump" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def romfs() -> Path:
    root = Path(os.environ["OOT_ROMFS"])
    assert root.is_dir(), f"OOT_ROMFS is not a directory: {root}"
    return root
