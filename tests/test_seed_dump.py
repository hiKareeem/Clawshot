"""Seeds written from the dump (``-m dump``): every written file differs from the game's only where the patch plan
says, field by field; the same seed gives the same folder in two processes; the data files fit the dump."""

import copy
import json
import os
import subprocess
import sys
from dataclasses import replace

import pytest

from clawshot.census.scan import CHEST, scan
from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.generate import Settings, prepare
from clawshot.patch import events as chest_events
from clawshot.patch import getitem, make_seed, placed_models, saria_farewell, songs, write_seed
from clawshot.patch import items as item_actors
from clawshot.patch.plan import DROP_KEY, EVENT_KEY, Plan
from clawshot.world.load import load_spec
from clawshot.world.model import Location
from clawshot.world.rules import CHILD
from clawshot.world.search import Search

pytestmark = pytest.mark.dump

# Round 3's playtest slice, as tests/test_seed.py has it.
SLICE = Settings(
    areas=("KokiriForest", "LostWood", "InsideTheDekuTree"),
    goal="'Defeat Queen Gohma'",
    cheap_deku_shield=False,  # this oracle isolates chest/intro edits, not the independent price policy
)

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
        if change.old_actor != change.new_actor:
            out.add((change.id, ("Dynamic", DROP_KEY), change.old_actor, change.new_actor))
        if change.key_event is not None:
            source = change.kept_event or change.event
            out.add((change.id, ("Dynamic", EVENT_KEY), source.name if source else REMOVED, change.key_event))
        elif change.event is not None:
            out.add((change.id, ("Dynamic", EVENT_KEY), change.event.name, REMOVED))
    return out


@pytest.mark.parametrize("seed_number", [1, 2, 3])
def test_written_files_differ_only_where_the_plan_says(romfs, tmp_path, seed_number):
    """Placement files: only the planned fields. The size table: each changed file's entry raised to what it needs
    when short, nothing else; and the table is written only then."""
    output = make_seed(romfs, seed_number, SLICE)
    out = tmp_path / "seed"
    written = {f.path: f for f in write_seed(output, romfs, out)}
    plan = output.plan
    assert plan.changes, "a seed that changes nothing tests nothing"

    dicts = zsdic.Dictionaries.from_romfs(romfs)
    table = rstb.read(dicts.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    expected_table = copy.deepcopy(table)
    print(f"\nseed {seed_number}: {len(plan.changes)} chest changes")
    for path in plan.files():
        f = written[path]
        original = byml.read(dicts.decompress(path, (romfs / path).read_bytes()))
        new_data = dicts.decompress(path, (out / "romfs" / path).read_bytes())
        expected = expected_changes(plan, path)
        if path == saria_farewell.PLACEMENT_FILE:  # every seed (event-items D9): the bridge Saria's own actor
            expected.add((saria_farewell.PLACEMENT_HASH, ("Gyaml",), saria_farewell.SARIA, saria_farewell.FAREWELL))
        assert set(field_changes(original, byml.read(new_data))) == expected, path
        need = rstb.required_size(path, len(new_data))
        expected_table.set(path, max(table.get(path), need))
        print(
            f"  {path}: {f.size} -> {f.new_size} ({f.new_size - f.size:+d}), compressed {f.compressed_size} -> "
            f"{f.new_compressed_size}, size-table entry {table.get(path)} -> {f.new_entry} (needs {need})"
        )

    # The other steps include compressed hints/flows and the raw new-game AINB:
    # each entry raised to what its written size needs, nothing else.
    extra = sorted({path for changes in output.extra_changes for path in changes})
    for path in extra:
        data = (out / "romfs" / path).read_bytes()
        if path.endswith(".zs"):
            data = dicts.decompress(path, data)
        need = rstb.required_size(path, len(data))
        expected_table.set(path, max(table.get(path), need))
        if path.startswith("Pack/Actor/") and path.endswith(".pack.zs"):
            expect_member_entries(expected_table, table, dicts.decompress(path, (romfs / path).read_bytes()), data)
    print(f"  other steps: {len(extra)} files")
    # Raw preallocated components retain their native entry; the writer must not
    # apply the compressed-resource size formula to these measured allocations.
    raw = [file.path for file in output.fast_start_files]
    for path in raw:
        native_entry = table.get(path)
        assert native_entry is not None, path
        assert len((out / "romfs" / path).read_bytes()) <= (romfs / path).stat().st_size <= native_entry, path
    for path, generated in output.new_files.items():
        data = (out / "romfs" / path).read_bytes()
        if path.endswith(".zs"):  # a loose file (Saria's farewell schedule list, event-items) is written as it is
            data = dicts.decompress(path, data)
        assert data == generated.data, path
        assert not (romfs / path).exists(), path
        if generated.sized_like is not None:  # no size formula: the native donor's entry plus the growth
            donor, growth = generated.sized_like
            expected_table.set(path, table.get(donor) + growth)
        else:
            expected_table.set(path, rstb.required_size(path, len(data)))
        if path.endswith(".pack.zs"):  # its members: declared donors, copied natives, else their type's formula
            for name, content in sarc.read(data).items():
                if name in generated.members:
                    donor, growth = generated.members[name]
                    expected_table.set(name, table.get(donor) + growth)
                elif name not in generated.copied and table.get(name) is None and not generated.members:
                    expected_table.set(name, member_entry(name, content))

    raised = expected_table != table
    files = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    table_file = [f"romfs/{rstb.TABLE_PATH}"] if raised else []
    planned = sorted({*plan.files(), *extra, *raw, *output.new_files})  # a chest file a step also edits counts once
    assert files == sorted(["spoiler.json", "play-note.md", *(f"romfs/{p}" for p in planned), *table_file])
    if raised:
        new_table = rstb.read(dicts.decompress(rstb.TABLE_PATH, (out / "romfs" / rstb.TABLE_PATH).read_bytes()))
        assert new_table == expected_table
    print(f"  size table {'written' if raised else 'not written: every entry fits'}")


def member_entry(name, content):
    """A member new to the game: its type's formula (an actor parameter counts its own components, an animation
    parameter its AnimationResources entries)."""
    components = resources = None
    if name.endswith(rstb.ACTOR_PARAM):
        components = len(byml.read(content).get("Components", {}))
    elif name.endswith(rstb.ANIMATION_PARAM):
        resources = len(byml.read(content).get("AnimationResources", []))
    return rstb.required_size(name, len(content), components, resources=resources)


def expect_member_entries(expected_table, table, before, after):
    """A changed actor pack's members: a new member with no entry gets its type's formula, or for a placed object's
    own model member (event-items) its native ModelInfo entry plus growth; a changed actor parameter is raised to what
    its own components need (never lowered); copied native members keep theirs."""
    old, new = sarc.read(before), sarc.read(after)
    donor_sized = placed_models.added_member_sizes(before, after)
    for name, content in new.items():
        if name not in old and table.get(name) is None:
            if name in donor_sized:
                donor, growth = donor_sized[name]
                expected_table.set(name, table.get(donor) + growth)
            else:
                expected_table.set(name, member_entry(name, content))
        elif name.endswith(rstb.ACTOR_PARAM) and old.get(name) != content:
            need = rstb.required_size(name, len(content), len(byml.read(content).get("Components", {})))
            expected_table.set(name, max(table.get(name), need))


def test_same_seed_same_folder_in_two_processes(romfs, tmp_path):
    folders = []
    for hash_seed in ("1", "2"):
        out = tmp_path / f"run{hash_seed}"
        env = {**os.environ, "PYTHONHASHSEED": hash_seed}
        argv = [sys.executable, "-m", "clawshot", "--romfs", str(romfs), "--seed", "4242", "--out", str(out)]
        argv += ["--areas", *SLICE.areas, "--goal", SLICE.goal, "--no-cheap-deku-shield"]
        result = subprocess.run(argv, capture_output=True, text=True, env=env)
        assert result.returncode == 0, result.stderr
        folders.append({p.relative_to(out).as_posix(): p.read_bytes() for p in sorted(out.rglob("*")) if p.is_file()})
    assert folders[0] == folders[1]
    assert "spoiler.json" in folders[0] and len(folders[0]) > 1
    # Chest-only settings can put no ocarina in a chest and move no song, so the seed carries neither the ocarina
    # get model nor the song get effects (by setting: PR #41, the maintainers' option 2).
    song_files = (songs.ELINK, songs.STATIC, *map(getitem.pack_path, getitem.SONG_MODELS))
    for path in (*map(getitem.pack_path, getitem.OCARINAS), *song_files):
        assert f"romfs/{path}" not in folders[0], path


def test_every_actor_in_the_table_is_in_the_game(romfs):
    missing = [a for a in item_actors.load().actors.values() if not (romfs / "Pack/Actor" / f"{a}.pack.zs").is_file()]
    assert missing == []


def test_every_chest_override_in_the_game_is_classified(romfs):
    events = chest_events.load()
    found = {loc.event for loc in scan(romfs) if loc.kind == CHEST and loc.event is not None}
    assert sorted(found - events.keys()) == []


def test_seed_7_cli_writes_a_play_note_with_a_child_opening_to_gohma(romfs, tmp_path):
    out = tmp_path / "seed7"
    argv = [
        sys.executable,
        "-m",
        "clawshot",
        "--romfs",
        str(romfs),
        "--seed",
        "7",
        "--shuffle",
        "Chest",
        "Shop",
        "--out",
        str(out),
    ]
    result = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    log = json.loads((out / "spoiler.json").read_text(encoding="utf-8"))
    route = log["opening_route"]
    assert route["event"] == "Defeat Queen Gohma"
    steps = route["steps"]
    complete = steps[-1]
    assert (complete["kind"], complete["location"]) == ("complete", route["event"])
    _, world = prepare(load_spec(), Settings(**log["settings"]))
    visits = {}
    implicit = list(world.events)
    for step in steps:
        if step["kind"] == "visit":
            event = next(e for e in implicit if e.region == step["region"] and e.name == step["event"])
            visits[step["location"]] = Location(
                step["location"], event.region, event.rule, "Event", event.name, event.source
            )
            implicit.remove(event)
    # Do not let an implicit gift supply an item before the note tells the player to visit it.
    search = Search.child_only(replace(world, events=implicit))
    for step in steps:
        if step["kind"] in ("collect", "visit"):
            location = visits[step["location"]] if step["kind"] == "visit" else world.locations[step["location"]]
            assert step["item"] == log["placements"].get(step["location"], location.vanilla), step
            assert search.can_access(location, CHILD), step
            search.collect(step["item"])
        elif step["kind"] == "enter":
            assert search.can_reach(step["location"], CHILD), step
        else:
            assert step["kind"] == "complete", step
            assert search.holds(step["location"]), step
    note = (out / "play-note.md").read_text(encoding="utf-8")
    rows = note.splitlines()
    entry_row = next(row for row in rows if "| Enter |" in row)
    complete_row = next(row for row in rows if "| Complete |" in row and complete["name"] in row)
    assert note.index(entry_row) < note.index(complete_row)
