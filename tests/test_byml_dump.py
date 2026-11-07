import pytest

from clawshot.formats import byml, zsdic


def _first_byte_difference(a: bytes, b: bytes) -> str:
    n = min(len(a), len(b))
    i = next((i for i in range(n) if a[i] != b[i]), n)
    return f"lengths {len(a)}/{len(b)}, first difference at 0x{i:x}: {a[i : i + 16].hex()} vs {b[i : i + 16].hex()}"


@pytest.mark.dump
def test_dump_every_placement_file_round_trips(romfs):
    """Read, write, read gives the same tree, and the written bytes equal the decompressed original."""
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    paths = sorted((romfs / "Banc").rglob("*.bcett.byml.zs"))
    assert len(paths) == 160
    tree_differences = {}
    byte_differences = {}
    for path in paths:
        rel = path.relative_to(romfs).as_posix()
        data = dicts.decompress(rel, path.read_bytes())
        tree = byml.read(data)
        written = byml.write(tree)
        if (d := byml.difference(tree, byml.read(written))) is not None:
            tree_differences[rel] = d
        elif written != data:
            byte_differences[rel] = _first_byte_difference(data, written)
    assert tree_differences == {}
    identical = len(paths) - len(byte_differences)
    print(f"{identical} of {len(paths)} placement files are byte-identical after a round trip")
    assert byte_differences == {}
