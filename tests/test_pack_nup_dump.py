"""Cache-only full seed generation must match the original dump in every resource-reading mode."""

import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path

import pytest

from clawshot.__main__ import main as generate_main
from clawshot.census.hints import flow_path
from clawshot.formats import evfl, zsdic
from clawshot.generate import Settings
from clawshot.pack import check_version, version_digest
from clawshot.pack.source import local_romfs
from clawshot.patch import gamedata, gifts
from clawshot.patch.items import load as load_actors
from clawshot.settings import CATALOG

pytestmark = pytest.mark.dump

# Token is explicitly disabled, not a supported generation route. Each supported kind
# gets its own row with Chest (native fixed dungeon-key layouts are not shuffled otherwise).
SHUFFLES = ("Chest", "Shop", "Gift", "Scrub", "BossHeart", "Freestanding")


def resource_modes():
    for kind in SHUFFLES:
        yield kind.lower(), Settings(shuffle=tuple(dict.fromkeys(("Chest", kind))))
    all_kinds = Settings(shuffle=SHUFFLES)
    skips = tuple(name for name in gamedata.load() if name not in ("mido", "forest_exit"))
    for forest in CATALOG["forest"]:
        yield f"forest-{forest}", replace(all_kinds, forest=forest, fast_start=skips)
    yield "free-travel", replace(all_kinds, logic={"free_time_travel": True})
    yield (
        "songs-prices",
        replace(
            all_kinds,
            songs="anywhere",
            shop_prices="affordable",
            shop_slots=3,
            scrub_prices="fixed",
            scrub_price=201,
        ),
    )
    yield "mask-no-skips", replace(all_kinds, hints="mask", fast_start=(), cheap_deku_shield=False, shop_slots=0)
    # Track B adds this field. Review rebases automatically exercise all door modes;
    # before that integration there is no nonexistent setting to skip or pretend to test.
    if "door_of_time" in Settings.__dataclass_fields__:
        for door in ("closed", "song_only", "open"):
            yield f"door-{door}", replace(all_kinds, door_of_time=door, logic={"free_time_travel": True})


@pytest.fixture(scope="module")
def cached_romfs(romfs, tmp_path_factory):
    if not os.environ.get("OOT_NUP"):
        pytest.skip("OOT_NUP is not set")
    source = Path(os.environ["OOT_NUP"])
    check_version(source)
    assert version_digest(source) == version_digest(romfs)
    before = source.stat()
    parent = tmp_path_factory.mktemp("nup-working-set")
    with local_romfs(source, parent) as cache:
        yield cache
    assert not cache.exists()
    after = source.stat()
    assert (after.st_size, after.st_mtime_ns) == (before.st_size, before.st_mtime_ns)


def test_nup_generator_working_set_matches_romfs(romfs, cached_romfs):
    for member in cached_romfs.rglob("*"):
        if member.is_file():
            relative = member.relative_to(cached_romfs)
            assert member.read_bytes() == (romfs / relative).read_bytes(), relative


def generate_and_write(source, output, settings, capsys):
    """Use the real CLI setup, census, fill, search and writer; never a fallback root."""
    try:
        result = generate_main(
            [
                "--romfs",
                str(source),
                "--seed",
                "7",
                "--settings",
                settings.to_string(),
                "--out",
                str(output),
            ]
        )
    except FileNotFoundError as error:
        missing = Path(error.filename).relative_to(source).as_posix()
        raise AssertionError(f"NUP cache missing resource: {missing}; add its path to pack/resources.toml") from error
    captured = capsys.readouterr()
    assert result == 0, captured.out + captured.err
    return {
        path.relative_to(output).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in output.rglob("*")
        if path.is_file()
    }


@pytest.mark.parametrize(
    "mode,settings", list(resource_modes()), ids=lambda value: value if isinstance(value, str) else ""
)
def test_cache_only_generates_and_writes_every_resource_mode(romfs, cached_romfs, tmp_path, capsys, mode, settings):
    # The cache run is passed ONLY the cache directory. The independent full-dump run
    # is the oracle, catching even silent missing glob members (e.g. a language archive).
    actual = generate_and_write(cached_romfs, tmp_path / "cached", settings, capsys)
    if mode == "gift":
        # Prove that this real cache-only CLI build exercises both newly released patches,
        # not merely that two builds silently omitted the same gift.
        output = tmp_path / "cached"
        placements = json.loads((output / "spoiler.json").read_text(encoding="utf-8"))["placements"]
        dictionaries = zsdic.Dictionaries.from_romfs(cached_romfs)
        actors = load_actors()
        for check, flow, event in (
            (gifts.MARKET_BOTTLE_CHECK, gifts.MARKET_BOTTLE_FLOW, "Event171"),
            (gifts.DAMPE_CHECK, "Npc_Hylia_Dampe_001", "Event628"),
        ):
            assert check in placements, f"Cache-only Gift build omitted {check}"
            path = flow_path(cached_romfs, flow)
            assert f"romfs/{path}" in actual, f"Cache-only Gift build omitted patched {path}"
            data = dictionaries.decompress(path, (output / "romfs" / path).read_bytes())
            chart = evfl.read(data).flowchart
            grant = next(node for node in chart.events if node.name == event)
            assert grant.params["ActorName"] == actors.actor(placements[check]), check
    expected = generate_and_write(romfs, tmp_path / "reference", settings, capsys)
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    changed = sorted(name for name in actual.keys() & expected.keys() if actual[name] != expected[name])
    assert actual == expected, f"{mode}: missing resources {missing}; extra {extra}; changed {changed}"


def test_missing_cache_input_reports_its_romfs_path(tmp_path, capsys):
    empty_cache = tmp_path / "empty-cache"
    empty_cache.mkdir()
    with pytest.raises(AssertionError, match="Pack/ZsDic.pack.zs"):
        generate_and_write(empty_cache, tmp_path / "not-written", Settings(), capsys)
    assert not (tmp_path / "not-written").exists()
