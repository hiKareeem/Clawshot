import pytest

from clawshot.formats import evfl, zsdic


def _first_byte_difference(a: bytes, b: bytes) -> str:
    n = min(len(a), len(b))
    i = next((i for i in range(n) if a[i] != b[i]), n)
    return f"lengths {len(a)}/{len(b)}, first difference at 0x{i:x}: {a[i : i + 16].hex()} vs {b[i : i + 16].hex()}"


@pytest.mark.dump
def test_dump_every_event_flow_writes_back_byte_identical(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    paths = sorted((romfs / "Event" / "EventFlow").glob("*.bfevfl.zs"))
    assert len(paths) == 914
    differences = {}
    kinds = {"flowchart": 0, "timeline": 0}
    for path in paths:
        rel = path.relative_to(romfs).as_posix()
        data = dicts.decompress(rel, path.read_bytes())
        tree = evfl.read(data)
        kinds["flowchart" if tree.flowchart else "timeline"] += 1
        written = evfl.write(tree)
        if written != data:
            differences[rel] = _first_byte_difference(data, written)
        else:
            assert evfl.read(written) == tree, rel
    print(f"{len(paths) - len(differences)} of {len(paths)} event flows byte-identical after a round trip; {kinds}")
    assert differences == {}
