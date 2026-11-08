import pytest

from clawshot.census.scan import scan
from clawshot.formats import byml, sarc, zsdic
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


@pytest.mark.dump
def test_native_token_grant_keeps_enemy_callback_ai_byte_identical(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    raw = dicts.decompress(tokens.PACK_PATH, (romfs / tokens.PACK_PATH).read_bytes())
    before = sarc.read(raw)
    transform = tokens.grant_experiment()[tokens.PACK_PATH]
    after = sarc.read(transform(raw))
    assert set(after) == set(before)
    for member in before:
        if member == tokens.POUCH_MEMBER:
            pouch = byml.read(after[member])
            assert pouch["PouchActor"] == tokens.EXPERIMENT_GRANT
            pouch["PouchActor"] = tokens.NATIVE_GRANT
            assert byml.same(pouch, byml.read(before[member]))
            assert len(after[member]) <= len(before[member])
        else:
            assert after[member] == before[member], member
    assert b"OneShotGoldTokenDeadAfter" in after[tokens.TOKEN_AI_MEMBER]
    print("Native callback, model, blackboard and pickup rules unchanged; only global PouchActor changed")
