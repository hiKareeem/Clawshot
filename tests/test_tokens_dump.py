import pytest

from clawshot.census.scan import scan
from clawshot.formats import byml, zsdic
from clawshot.patch import tokens


@pytest.mark.dump
def test_all_token_copies_keep_hash_and_logic_when_drop_changes(romfs):
    census = [loc for loc in scan(romfs) if loc.kind == "gold_skulltula"]
    transforms = tokens.changes({loc.id: "Obj_Shield_Hylian" for loc in census}, census)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    seen = set()
    for path, transform in transforms.items():
        raw = dicts.decompress(path, (romfs / path).read_bytes())
        before, after = byml.read(raw), byml.read(transform(raw))
        for actor in after["Actors"]:
            if actor["Gyaml"] == tokens.ENEMY:
                assert actor["Dynamic"].pop(tokens.DROP) == "Obj_Shield_Hylian"
                seen.add(int(actor["Hash"]))
                original = next(a for a in before["Actors"] if a["Hash"] == actor["Hash"])
                if "Dynamic" not in original:
                    assert actor["Dynamic"] == {}
                    del actor["Dynamic"]
        assert byml.same(before, after), path
    assert seen == {loc.id for loc in census}
    print(
        f"{len(census)} enemies / {sum(len(loc.files) for loc in census)} copies; exact field diff, not gameplay proof"
    )
