"""Optional NUP oracle: every cached generator input equals the extracted supported dump."""

import os
from pathlib import Path

import pytest

from clawshot.pack import check_version, version_digest
from clawshot.pack.source import local_romfs

pytestmark = pytest.mark.dump


def test_nup_generator_working_set_matches_romfs(romfs, tmp_path):
    if not os.environ.get("OOT_NUP"):
        pytest.skip("OOT_NUP is not set")
    path = Path(os.environ["OOT_NUP"])
    check_version(path)
    assert version_digest(path) == version_digest(romfs)
    before = path.stat()
    with local_romfs(path, tmp_path) as cache:
        for member in cache.rglob("*"):
            if member.is_file():
                relative = member.relative_to(cache)
                assert member.read_bytes() == (romfs / relative).read_bytes(), relative
    assert not cache.exists()
    after = path.stat()
    assert (after.st_size, after.st_mtime_ns) == (before.st_size, before.st_mtime_ns)
