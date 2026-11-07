import os
import random
from pathlib import Path

import pytest
import zstandard as zstd

from clawshot.formats import sarc

# The game's dictionary IDs, as recorded in each .zs frame header.
DICTIONARY_IDS = {"zs.zsdic": 1, "bkprb.zsdic": 2, "bcett.byml.zsdic": 3, "pack.zsdic": 4}


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


def _training_samples(seed: int) -> list[bytes]:
    rng = random.Random(seed)
    words = [b"Actors", b"Gyaml", b"Hash", b"Translate", b"Rotate", b"Dynamic", b"Phive", b"Placement"]
    return [b"".join(rng.choice(words) + bytes([rng.randrange(256)]) for _ in range(40)) for _ in range(400)]


@pytest.fixture(scope="session")
def zsdic_pack() -> bytes:
    """A synthetic ZsDic.pack.zs: plain zstd around a SARC of four dictionaries trained on made-up samples, with
    the game's dictionary IDs."""
    files = {
        name: zstd.train_dictionary(4096, _training_samples(dict_id), dict_id=dict_id).as_bytes()
        for name, dict_id in DICTIONARY_IDS.items()
    }
    return zstd.ZstdCompressor().compress(sarc.write(files))
