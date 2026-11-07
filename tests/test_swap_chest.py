import copy

import pytest

from clawshot.formats import byml, zsdic
from clawshot.formats.byml import F32, U32, U64
from clawshot.tools import swap_chest

BANC = "Banc/Test/Test_Child_Dynamic.bcett.byml.zs"
CHEST = 1111
TWIN = 2222  # same Dynamic as CHEST, so the file stores that map once
SIGN = 3333


def actor(gyaml: str, actor_hash: int, dynamic: dict | None = None) -> dict:
    a = {
        "Gyaml": gyaml,
        "Hash": U64(actor_hash),
        "Phive": {"Placement": {"ID": U64(actor_hash)}},
        "SRTHash": U32(actor_hash),
        "Translate": [F32(1.0), F32(2.0), F32(3.0)],
    }
    if dynamic is not None:
        a["Dynamic"] = dynamic
    return a


TREE = {
    "Actors": [
        actor("Obj_TBox_A_01", CHEST, {"Drop__DropActor": "TBox_Rupee_Blue", "GetEventName": "Some_Event"}),
        actor("Obj_TBox_A_01", TWIN, {"Drop__DropActor": "TBox_Rupee_Blue", "GetEventName": "Some_Event"}),
        actor("Obj_Signboard", SIGN),
    ],
    "FilePath": "Work/Banc/Test/Test_Child_Dynamic.bcett.json",
}


@pytest.fixture
def fake_romfs(tmp_path, zsdic_pack):
    root = tmp_path / "romfs"
    (root / "Pack" / "Actor").mkdir(parents=True)
    (root / zsdic.PACK_PATH).write_bytes(zsdic_pack)
    for item in ("TBox_Rupee_Red", "Item_Boomerang"):
        (root / "Pack" / "Actor" / f"{item}.pack.zs").write_bytes(b"")
    dicts = zsdic.Dictionaries.from_pack(zsdic_pack)
    (root / BANC).parent.mkdir(parents=True)
    (root / BANC).write_bytes(dicts.compress(BANC, byml.write(TREE)))
    return root


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def test_swap_changes_only_that_chest(fake_romfs, tmp_path):
    before = snapshot(fake_romfs)
    out = tmp_path / "out"
    result = swap_chest.swap_chest(fake_romfs, out, BANC, CHEST, "Item_Boomerang")

    assert result.output == out / "romfs" / "Banc" / "Test" / "Test_Child_Dynamic.bcett.byml.zs"
    assert (result.old_item, result.new_item) == ("TBox_Rupee_Blue", "Item_Boomerang")
    packed = result.output.read_bytes()
    assert zsdic.frame_dictionary_id(packed) == 3
    assert result.new_compressed_size == len(packed)
    changed = byml.read(zsdic.Dictionaries.from_romfs(fake_romfs).decompress(BANC, packed))
    expected = copy.deepcopy(TREE)
    expected["Actors"][0]["Dynamic"]["Drop__DropActor"] = "Item_Boomerang"
    assert byml.difference(changed, expected) is None
    assert snapshot(fake_romfs) == before
    assert [p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()] == [f"romfs/{BANC}"]


def test_same_inputs_give_the_same_bytes(fake_romfs, tmp_path):
    a = swap_chest.swap_chest(fake_romfs, tmp_path / "a", BANC, CHEST, "TBox_Rupee_Red").output.read_bytes()
    b = swap_chest.swap_chest(fake_romfs, tmp_path / "b", BANC, CHEST, "TBox_Rupee_Red").output.read_bytes()
    assert a == b


@pytest.mark.parametrize(
    ("actor_hash", "item", "message"),
    [
        (4444, "TBox_Rupee_Red", "0 actors have Hash 4444"),
        (SIGN, "TBox_Rupee_Red", "no Dynamic.Drop__DropActor"),
        (CHEST, "Item_Nonexistent", "no actor called 'Item_Nonexistent'"),
    ],
)
def test_refusals(fake_romfs, tmp_path, actor_hash, item, message):
    with pytest.raises(swap_chest.SwapError, match=message):
        swap_chest.swap_chest(fake_romfs, tmp_path / "out", BANC, actor_hash, item)
    assert not (tmp_path / "out").exists()


def test_never_writes_inside_the_romfs(fake_romfs):
    with pytest.raises(swap_chest.SwapError, match="read-only"):
        swap_chest.swap_chest(fake_romfs, fake_romfs / "mods", BANC, CHEST, "TBox_Rupee_Red")
    with pytest.raises(swap_chest.SwapError, match="romfs-relative"):
        swap_chest.swap_chest(fake_romfs, fake_romfs.parent / "out", "../romfs/" + BANC, CHEST, "TBox_Rupee_Red")


def test_command_line(fake_romfs, tmp_path, capsys):
    argv = ["--romfs", str(fake_romfs), "--out", str(tmp_path / "out"), "--file", BANC, "--hash", str(CHEST)]
    assert swap_chest.main([*argv, "--item", "TBox_Rupee_Red"]) == 0
    assert "TBox_Rupee_Blue -> TBox_Rupee_Red" in capsys.readouterr().out
    assert swap_chest.main([*argv, "--item", "Nope"]) == 1
    assert "error: no actor called 'Nope'" in capsys.readouterr().err
