"""Seeds written from the dump (``-m dump``): every written file differs from the game's only where the patch plan
says, field by field; the same seed gives the same folder in two processes; the data files fit the dump."""

import os
import subprocess
import sys

import pytest

from clawshot.census.scan import CHEST, scan
from clawshot.formats import byml, zsdic
from clawshot.generate import Settings
from clawshot.patch import events as chest_events
from clawshot.patch import items as item_actors
from clawshot.patch import make_seed, write_seed
from clawshot.patch.plan import DROP_KEY, EVENT_KEY, Plan

pytestmark = pytest.mark.dump

REMOVED = "<removed>"


def field_changes(a, b, path=(), actor=None):
    """Every leaf that differs between two trees: (actor Hash or None, key path, old, new). Actors in a list are
    matched by position and named by their Hash, with key paths from the actor; a key on one side only counts as
    added or removed."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                yield actor, (*path, k), a.get(k, REMOVED), b.get(k, REMOVED)
            else:
                yield from field_changes(a[k], b[k], (*path, k), actor)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for x, y in zip(a, b, strict=True):
            inner = int(x["Hash"]) if isinstance(x, dict) and "Hash" in x and actor is None else actor
            yield from field_changes(x, y, () if inner != actor else (*path, "[]"), inner)
    elif not byml.same(a, b):
        yield actor, path, a, b


def expected_changes(plan: Plan, path: str) -> set:
    out = set()
    for change in plan.for_file(path):
        out.add((change.id, ("Dynamic", DROP_KEY), change.old_actor, change.new_actor))
        if change.event is not None:
            out.add((change.id, ("Dynamic", EVENT_KEY), change.event.name, REMOVED))
    return out


@pytest.mark.parametrize("seed_number", [1, 2, 3])
def test_written_files_differ_only_where_the_plan_says(romfs, tmp_path, seed_number):
    output = make_seed(romfs, seed_number, Settings())
    out = tmp_path / "seed"
    written = write_seed(output, romfs, out)
    plan = output.plan
    assert plan.changes, "a seed that changes nothing tests nothing"
    files = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    assert files == sorted(["spoiler.json", *(f"romfs/{path}" for path in plan.files())])

    dicts = zsdic.Dictionaries.from_romfs(romfs)
    print(f"\nseed {seed_number}: {len(plan.changes)} chest changes")
    for f in written:
        original = byml.read(dicts.decompress(f.path, (romfs / f.path).read_bytes()))
        new = byml.read(dicts.decompress(f.path, (out / "romfs" / f.path).read_bytes()))
        found = set(field_changes(original, new))
        assert found == expected_changes(plan, f.path), f.path
        print(
            f"  {f.path}: {f.size} -> {f.new_size} ({f.new_size - f.size:+d}), "
            f"compressed {f.compressed_size} -> {f.new_compressed_size}"
        )


def test_same_seed_same_folder_in_two_processes(romfs, tmp_path):
    folders = []
    for hash_seed in ("1", "2"):
        out = tmp_path / f"run{hash_seed}"
        env = {**os.environ, "PYTHONHASHSEED": hash_seed}
        argv = [sys.executable, "-m", "clawshot", "--romfs", str(romfs), "--seed", "4242", "--out", str(out)]
        subprocess.run(argv, capture_output=True, env=env, check=True)
        folders.append({p.relative_to(out).as_posix(): p.read_bytes() for p in sorted(out.rglob("*")) if p.is_file()})
    assert folders[0] == folders[1]
    assert "spoiler.json" in folders[0] and len(folders[0]) > 1


def test_every_actor_in_the_table_is_in_the_game(romfs):
    missing = [a for a in item_actors.load().actors.values() if not (romfs / "Pack/Actor" / f"{a}.pack.zs").is_file()]
    assert missing == []


def test_every_chest_override_in_the_game_is_classified(romfs):
    events = chest_events.load()
    found = {loc.event for loc in scan(romfs) if loc.kind == CHEST and loc.event is not None}
    assert sorted(found - events.keys()) == []
