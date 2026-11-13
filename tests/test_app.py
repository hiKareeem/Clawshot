"""Invented worlds/resources exercise settings, worker lifecycle and actual seed writing."""

import json
import time
from dataclasses import fields
from pathlib import Path

import pytest

from clawshot.app import GenerationRequest, Jobs, detect_game, schema, validate
from clawshot.app.paths import absolute_path, output_path
from clawshot.app.preferences import Preferences
from clawshot.formats import byml, rstb, zsdic
from clawshot.generate import Settings, generate
from clawshot.patch import SeedOutput, write_seed
from clawshot.patch.plan import ChestChange, Links, Plan

RESOURCE = "Banc/Test/Test_Static.bcett.byml.zs"


def synthetic_spec(blocked=False):
    return {
        "start": "Start",
        "goal": "Sword",
        "settings": {},
        "items": {"Sword": {}, "Rupees (5)": {"class": "normal"}},
        "regions": [{"name": "Start", "locations": {"First": "False" if blocked else "True", "Second": "True"}}],
        "locations": {
            "First": {"type": "Chest", "vanilla": "Sword"},
            "Second": {"type": "Chest", "vanilla": "Rupees (5)"},
        },
    }


def synthetic_run(request, stage, report):
    report("validate")
    settings = validate(text=request.settings, spec=synthetic_spec())
    report("source")
    report("prepare")
    report("generate")
    spec = synthetic_spec()
    if request.seed == -1:
        spec["goal"] = "False"
    seed = generate(spec, request.seed, settings)
    actors = {"Sword": "Item_Sword", "Rupees (5)": "TBox_Rupee_Blue"}
    changes = [
        ChestChange(
            name,
            index,
            name,
            (RESOURCE,),
            "Obj_TBox_A_01",
            seed.placements[name],
            actors[old],
            actors[seed.placements[name]],
            None,
        )
        for index, (name, old) in enumerate((("First", "Sword"), ("Second", "Rupees (5)")), 1)
    ]
    result = SeedOutput(seed, Links({}, {}, []), Plan(changes, [], []))
    report("write")
    written = write_seed(result, request.dump, stage / "seed")
    return {
        "seed": seed.seed,
        "shuffled": len(seed.shuffled),
        "resources": len(written),
        "spheres": len(seed.spheres),
        "settings_string": seed.settings.to_string(),
    }


def slow_run(request, stage, report):
    report("generate")
    (stage / "private-partial").write_text("session-owned")
    time.sleep(60)
    raise AssertionError("cancellation should terminate this worker")


@pytest.fixture
def app_source(tmp_path, zsdic_pack):
    root = tmp_path / "input"
    dictionaries = zsdic.Dictionaries.from_pack(zsdic_pack)
    files = {
        zsdic.PACK_PATH: zsdic_pack,
        RESOURCE: dictionaries.compress(
            RESOURCE,
            byml.write(
                {
                    "Actors": [
                        {"Gyaml": "Obj_TBox_A_01", "Hash": byml.U64(i), "Dynamic": {"Drop__DropActor": actor}}
                        for i, actor in ((1, "Item_Sword"), (2, "TBox_Rupee_Blue"))
                    ]
                }
            ),
        ),
    }
    table = rstb.ResourceSizeTable()
    table.set(RESOURCE, 1 << 20)
    files[rstb.TABLE_PATH] = dictionaries.compress(rstb.TABLE_PATH, rstb.write(table))
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return root


def wait_job(jobs):
    jobs.thread.join(20)
    assert not jobs.thread.is_alive(), jobs.snapshot()
    return jobs.snapshot()


def test_schema_is_exhaustive_and_replay_preserves_values():
    assert {row["key"] for row in schema()} == {field.name for field in fields(Settings)}
    settings = validate(
        {"dungeon_items": "anywhere", "forest": "open", "shop_slots": 3, "logic": {"free_time_travel": True}}
    )
    restored = validate(text=settings.to_string())
    assert restored == settings
    assert restored.shop_slots == 3 and restored.forest == "open" and restored.logic["free_time_travel"] is True


@pytest.mark.parametrize(
    "values",
    [
        {"shop_slots": True},
        {"shop_slots": 9},
        {"cheap_deku_shield": "false"},
        {"shuffle": ["Imaginary"]},
        {"shuffle": ["Token"]},
        {"areas": ["Test"]},
        {"no_such_setting": True},
        {"logic": {"open_forest": "open"}},
    ],
)
def test_invalid_settings_refuse_before_generation(values):
    with pytest.raises(ValueError):
        validate(values)


def test_paths_refuse_existing_source_and_relative_output(tmp_path):
    source = tmp_path / "input"
    source.mkdir()
    with pytest.raises(ValueError, match="absolute"):
        absolute_path("relative", "Output")
    with pytest.raises(ValueError, match="protected"):
        output_path(str(source / "seed"), source)
    existing = tmp_path / "played"
    existing.mkdir()
    (existing / "keep").write_text("played")
    with pytest.raises(ValueError, match="already exists"):
        output_path(str(existing), source)
    assert (existing / "keep").read_text() == "played"


@pytest.mark.parametrize("game, program", [("Hookshot", "hookshot"), ("Longshot", "longshot")])
def test_game_detection_does_not_execute_binary(tmp_path, game, program):
    (tmp_path / "bin").mkdir()
    (tmp_path / f"bin/{program}.exe").write_bytes(b"not executable HOS_MODS\0")
    (tmp_path / f"{program}_version.txt").write_text("version=v2.0.13\nbuilder=not-used\n")
    (tmp_path / "romfs").mkdir()
    (tmp_path / "own.nup").write_bytes(b"invented")
    result = detect_game(str(tmp_path))
    assert (result["game"], result["version"]) == (game, "v2.0.13")
    assert result["supports_mods"] and not result["reason"]
    assert result["selected_folder"] == result["folder"] == str(tmp_path) and result["launcher"] is None
    assert result["folders"] == [str(tmp_path)]
    assert Path(result["romfs"]) == tmp_path / "romfs"
    assert result["nups"] == [str(tmp_path / "own.nup")]


def test_launcher_detection_keeps_the_chosen_folder_and_protects_its_build(tmp_path):
    home = tmp_path / "AppData/Local/LongshotLauncher"
    build = tmp_path / "Games/Longshot/v3.0.0"
    (build / "bin").mkdir(parents=True)
    (build / "bin/longshot.exe").write_bytes(b"not executable HOS_MODS\0")
    home.mkdir(parents=True)
    registry = {"format": 1, "builds": [{"folder": str(build), "version": "v3.0.0"}]}
    (home / "builds.json").write_text(json.dumps(registry))
    result = detect_game(str(home))
    assert (result["game"], result["version"], result["folder"]) == ("Longshot", "v3.0.0", str(build))
    assert result["selected_folder"] == result["launcher"] == str(home)
    assert result["folders"] == [str(home), str(build)]
    source = tmp_path / "dump"
    source.mkdir()
    for inside in (home / "seed-1", build / "seed-1"):
        with pytest.raises(ValueError, match="protected"):
            output_path(str(inside), source, home)
        with pytest.raises(ValueError, match="protected"):
            GenerationRequest(str(source), str(inside), 1, "CS1", str(home)).paths()
    assert output_path(str(tmp_path / "seed-1"), source, home) == tmp_path / "seed-1"
    assert not (home / "seed-1").exists() and not (build / "seed-1").exists()


@pytest.mark.parametrize(
    "saved, expected",
    [
        ({"hookshot": "C:/Games/Hookshot"}, "C:/Games/Hookshot"),
        ({"hookshot": "C:/Games/Hookshot", "game": "D:/LongshotLauncher"}, "D:/LongshotLauncher"),
        ({"game": "D:/LongshotLauncher"}, "D:/LongshotLauncher"),
    ],
)
def test_saved_hookshot_folder_becomes_the_game_folder(tmp_path, saved, expected):
    config = tmp_path / "config/paths.json"
    config.parent.mkdir()
    config.write_text(json.dumps(saved | {"dump": "C:/dump"}), encoding="utf-8")
    preferences = Preferences(config)
    assert preferences.snapshot() == {"dump": "C:/dump", "game": expected} and not preferences.warning
    assert json.loads(config.read_text(encoding="utf-8")) == saved | {"dump": "C:/dump"}  # reading never writes
    with pytest.raises(ValueError):
        preferences.remember("hookshot", "C:/Games/Hookshot")
    assert preferences.remember("emulator_mods", "C:/mods") == ""
    written = json.loads(config.read_text(encoding="utf-8"))
    assert written == {"dump": "C:/dump", "emulator_mods": "C:/mods", "game": expected}


def test_job_writes_beatable_synthetic_seed_and_preserves_source(app_source, tmp_path):
    before = {p.relative_to(app_source): p.read_bytes() for p in app_source.rglob("*") if p.is_file()}
    out = tmp_path / "new-seed"
    jobs = Jobs(synthetic_run)
    try:
        jobs.start(GenerationRequest(str(app_source), str(out), 7, "CS1"))
        state = wait_job(jobs)
        assert state["status"] == "succeeded", state
        assert all(row["status"] == "done" for row in state["stages"]), state
        log = json.loads((out / "seed/spoiler.json").read_text())
        assert sorted(log["placements"].values()) == ["Rupees (5)", "Sword"]
        assert any("Sword" in sphere.values() for sphere in log["spheres"])
        assert state["result"]["resources"] == 1
        dictionaries = zsdic.Dictionaries.from_romfs(app_source)
        written = byml.read(dictionaries.decompress(RESOURCE, (out / "seed/romfs" / RESOURCE).read_bytes()))
        for actor, name in zip(written["Actors"], ("First", "Second"), strict=True):
            expected = "Item_Sword" if log["placements"][name] == "Sword" else "TBox_Rupee_Blue"
            assert actor["Dynamic"]["Drop__DropActor"] == expected
        assert before == {p.relative_to(app_source): p.read_bytes() for p in app_source.rglob("*") if p.is_file()}
        assert not list(tmp_path.glob(".clawshot-job-*"))
    finally:
        jobs.close()


def test_worker_failure_exposes_fill_error_and_publishes_nothing(app_source, tmp_path):
    out = tmp_path / "impossible"
    jobs = Jobs(synthetic_run)
    try:
        jobs.start(GenerationRequest(str(app_source), str(out), -1, "CS1"))
        state = wait_job(jobs)
        assert state["status"] == "failed", state
        assert state["error"]["type"] == "FillError"
        assert not out.exists() and not list(tmp_path.glob(".clawshot-job-*"))
    finally:
        jobs.close()


def test_cancel_kills_only_worker_and_keeps_concurrent_output(tmp_path):
    source = tmp_path / "input"
    source.mkdir()
    out = tmp_path / "new"
    jobs = Jobs(slow_run)
    try:
        jobs.start(GenerationRequest(str(source), str(out), 7, "CS1"))
        with pytest.raises(ValueError, match="already running"):
            jobs.start(GenerationRequest(str(source), str(tmp_path / "other"), 8, "CS1"))
        out.mkdir()
        (out / "keep").write_text("another process owns this")
        jobs.cancel()
        assert wait_job(jobs)["status"] == "cancelled"
        assert (out / "keep").read_text() == "another process owns this"
        assert not list(tmp_path.glob(".clawshot-job-*"))
    finally:
        jobs.close()
