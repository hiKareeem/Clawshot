"""The common writer's files new to the game (write(..., new_files=...)), over a synthetic romfs."""

import struct
import zlib

import pytest

from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import NewFile, write

NATIVE = "Pack/Actor/Native.pack.zs"
SHARED = "Component/Shared/Shared.game__component__Thing.bgyml"
NATIVE_PARAM = "Actor/Native.engine__actor__ActorParam.bgyml"
NEW = "Pack/Actor/Created.pack.zs"
NEW_PARAM = "Actor/Created.engine__actor__ActorParam.bgyml"
NEW_POUCH = "Component/PouchContentParam/Created.game__component__PouchContentParam.bgyml"
SECOND = "Pack/Actor/Second.pack.zs"
SHARED_ENTRY = 7000


def native_pack():
    return {
        NATIVE_PARAM: byml.write({"Components": {"ThingRef": "?" + SHARED}}),
        SHARED: byml.write({"Value": 1}),
    }


def created_pack(**extra):
    base = "Work/Actor/Base.engine__actor__ActorParam.gyml"
    return {
        NEW_PARAM: byml.write({"$parent": base, "Components": {"A": "?a", "B": "?b"}}),
        NEW_POUCH: byml.write({"DefaultAutoGet": True}),
        SHARED: native_pack()[SHARED],
        **extra,
    }


@pytest.fixture
def romfs(tmp_path, zsdic_pack):
    root = tmp_path / "romfs"
    (root / "Pack/Actor").mkdir(parents=True)
    (root / "Pack/ZsDic.pack.zs").write_bytes(zsdic_pack)
    dictionaries = zsdic.Dictionaries.from_pack(zsdic_pack)
    (root / NATIVE).write_bytes(dictionaries.compress(NATIVE, sarc.write(native_pack())))
    table = rstb.ResourceSizeTable()
    table.set(NATIVE, 1 << 16)
    table.set(NATIVE_PARAM, 6000)
    table.set(SHARED, SHARED_ENTRY)
    table.set("Unrelated/File.bfevfl", 1234)
    (root / rstb.TABLE_PATH).parent.mkdir(parents=True)
    (root / rstb.TABLE_PATH).write_bytes(dictionaries.compress(rstb.TABLE_PATH, rstb.write(table)))
    return root


def decompressed(root, out, path):
    return zsdic.Dictionaries.from_romfs(root).decompress(path, (out / "romfs" / path).read_bytes())


def created(files=None, copied=None):
    return NewFile(sarc.write(files or created_pack()), copied={SHARED: NATIVE} if copied is None else copied)


def test_a_new_pack_gets_measured_entries_and_copied_members_keep_theirs(romfs, tmp_path):
    out = tmp_path / "out"
    file = created()
    written = write(Plan([], [], []), romfs, out, new_files={NEW: file})
    assert [info.path for info in written] == [NEW, rstb.TABLE_PATH]
    info = written[0]
    assert (info.size, info.new_size, info.entry, info.compressed_size) == (0, len(file.data), None, 0)
    assert decompressed(romfs, out, NEW) == file.data
    table = rstb.read(decompressed(romfs, out, rstb.TABLE_PATH))
    param = created_pack()[NEW_PARAM]
    assert table.get(NEW) == info.new_entry == rstb.required_size(NEW, len(file.data))
    assert table.get(NEW_PARAM) == (len(param) + 31) // 32 * 32 + 5144 + 2 * 48  # two own components
    assert table.get(NEW_POUCH) == (len(created_pack()[NEW_POUCH]) + 31) // 32 * 32 + 5216
    untouched = (table.get(SHARED), table.get(NATIVE_PARAM), table.get("Unrelated/File.bfevfl"))
    assert untouched == (SHARED_ENTRY, 6000, 1234)


def test_shared_new_component_is_readable_from_both_packs_with_one_allocation(romfs, tmp_path):
    other = NewFile(sarc.write({NEW_POUCH: created_pack()[NEW_POUCH]}))
    out = tmp_path / "out"
    write(Plan([], [], []), romfs, out, new_files={NEW: created(), SECOND: other})
    for path in (NEW, SECOND):
        pack = sarc.read(decompressed(romfs, out, path))
        assert byml.read(pack[NEW_POUCH]) == {"DefaultAutoGet": True}
    table = rstb.read(decompressed(romfs, out, rstb.TABLE_PATH))
    assert table.get(NEW_POUCH) == rstb.required_size(NEW_POUCH, len(created_pack()[NEW_POUCH]))
    assert table.get(SHARED) == SHARED_ENTRY


def _crc_taken(table):
    table.hashes[zlib.crc32(rstb.resource_path(NEW).encode())] = 99


def _member_crc_taken(table):
    table.hashes[zlib.crc32(NEW_PARAM.encode())] = 99


def _bad_node_hash():
    data = bytearray(sarc.write(created_pack()))
    struct.pack_into("<I", data, 0x20, 0)  # first SFAT node no longer hashes its member name
    return NewFile(bytes(data), copied={SHARED: NATIVE})


@pytest.mark.parametrize(
    ("files", "table_change"),
    [
        (lambda: {NEW: created(created_pack(**{SHARED: byml.write({"Value": 2})}))}, None),
        (lambda: {NEW: created(copied={SHARED: "Pack/Actor/Missing.pack.zs"})}, None),
        (lambda: {NEW: created(copied={SHARED: "Banc/A/A.bcett.byml.zs"})}, None),
        (lambda: {NEW: created(copied={SHARED: NATIVE, "Other": NATIVE})}, None),
        (lambda: {NEW: created(copied={})}, None),  # a native member offered as new
        (lambda: {NEW: created(created_pack(**{"Logic/X.module.ainb": b"AIB"}))}, None),
        (lambda: {NATIVE: NewFile(sarc.write(native_pack()))}, None),
        (lambda: {"Event/EventFlow/New.bfevfl.zs": NewFile(b"flow", copied={SHARED: NATIVE})}, None),
        (lambda: {NEW: _bad_node_hash()}, None),
        (lambda: {"../escape.pack.zs": NewFile(b"")}, None),
        (lambda: {NEW: created()}, _crc_taken),
        (lambda: {NEW: created()}, _member_crc_taken),
        (
            lambda: {
                NEW: created(),
                SECOND: NewFile(sarc.write({NEW_POUCH: byml.write({"DefaultAutoGet": False})})),
            },
            None,
        ),
    ],
)
def test_unsafe_new_files_are_refused_and_nothing_is_written(romfs, tmp_path, files, table_change):
    if table_change is not None:
        dictionaries = zsdic.Dictionaries.from_romfs(romfs)
        table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
        table_change(table)
        (romfs / rstb.TABLE_PATH).write_bytes(dictionaries.compress(rstb.TABLE_PATH, rstb.write(table)))
    out = tmp_path / "out"
    with pytest.raises(PatchError):
        write(Plan([], [], []), romfs, out, new_files=files())
    assert not out.exists() or not any(out.iterdir())


def test_a_new_file_may_not_take_a_changed_files_path(romfs, tmp_path):
    with pytest.raises(PatchError):
        write(
            Plan([], [], []),
            romfs,
            tmp_path / "out",
            extra_changes=({NATIVE: lambda data: data},),
            new_files={NATIVE: NewFile(b"")},
        )


def test_added_component_in_existing_pack_gets_allocation_and_actor_growth(romfs, tmp_path):
    def transform(data):
        packed = sarc.read(data)
        packed[NEW_POUCH] = created_pack()[NEW_POUCH]
        packed[NATIVE_PARAM] = byml.write({"Components": {f"RewardRef{i}": "?" + NEW_POUCH for i in range(20)}})
        return sarc.write(packed)

    out = tmp_path / "changed-pack"
    write(Plan([], [], []), romfs, out, extra_changes=({NATIVE: transform},))
    packed = sarc.read(decompressed(romfs, out, NATIVE))
    table = rstb.read(decompressed(romfs, out, rstb.TABLE_PATH))
    assert table.get(NEW_POUCH) == rstb.required_size(NEW_POUCH, len(packed[NEW_POUCH]))
    assert table.get(NATIVE_PARAM) >= rstb.required_size(NATIVE_PARAM, len(packed[NATIVE_PARAM]), 20)
    assert table.get(SHARED) == SHARED_ENTRY


def changed_native(value):
    """An extra change to the native pack: its shared member now holds ``value``."""

    def transform(data):
        pack = sarc.read(data)
        pack[SHARED] = byml.write({"Value": value})
        return sarc.write(pack)

    return {NATIVE: transform}


def test_a_new_pack_may_copy_a_member_of_a_pack_this_write_changes(romfs, tmp_path):
    """Song pickups hold the song's ModelInfo as the seed writes it (song get effects): the copy matches the written
    member, whose entry the changed pack's own sizing set."""
    out = tmp_path / "out"
    file = created(created_pack(**{SHARED: byml.write({"Value": 2})}))
    write(Plan([], [], []), romfs, out, extra_changes=(changed_native(2),), new_files={NEW: file})
    assert byml.read(sarc.read(decompressed(romfs, out, NEW))[SHARED]) == {"Value": 2}
    table = rstb.read(decompressed(romfs, out, rstb.TABLE_PATH))
    assert table.get(SHARED) == SHARED_ENTRY


def test_a_copy_of_a_changed_pack_must_match_what_this_write_holds(romfs, tmp_path):
    with pytest.raises(PatchError, match="not byte-identical"):
        write(Plan([], [], []), romfs, tmp_path / "out", extra_changes=(changed_native(2),), new_files={NEW: created()})


LOOSE = "Component/AIScheduleParam/Created.game__component__AIScheduleParam.bgyml"


def test_a_new_loose_file_without_a_size_formula_is_sized_from_its_native_donor_plus_growth(romfs, tmp_path):
    data = byml.write({"ConditionalSchedule": [], "DefaultSchedule": {}})
    write(Plan([], [], []), romfs, tmp_path / "out", new_files={LOOSE: NewFile(data, sized_like=(SHARED, 64))})
    table = rstb.read(decompressed(romfs, tmp_path / "out", rstb.TABLE_PATH))
    assert table.get(LOOSE) == SHARED_ENTRY + 64
    assert (tmp_path / "out/romfs" / LOOSE).read_bytes() == data


def test_a_loose_file_sized_from_a_donor_without_an_entry_is_refused(romfs, tmp_path):
    files = {LOOSE: NewFile(b"x", sized_like=("Component/Missing.bgyml", 0))}
    with pytest.raises(PatchError, match="Missing"):
        write(Plan([], [], []), romfs, tmp_path / "out", new_files=files)
    assert not (tmp_path / "out").exists()
