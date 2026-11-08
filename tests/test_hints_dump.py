import pytest

from clawshot.census import hints
from clawshot.formats import evfl, msbt, sarc, zsdic


@pytest.fixture(scope="module")
def stones(romfs):
    return hints.read_stones(romfs)


@pytest.fixture(scope="module")
def message_files(romfs):
    """language -> {message file name -> parsed MSBT}, for the files this test reads."""
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    wanted = {hints.GOSSIP_MESSAGES} | {giver.messages for giver in hints.HINT_GIVERS}
    out = {}
    for path in sorted(romfs.glob("Mals/*.sarc.zs")):
        files = sarc.read(dicts.decompress(path.name, path.read_bytes()))
        out[path.name.split(".")[0]] = {name: msbt.read(files[name]) for name in wanted}
    return out


@pytest.mark.dump
def test_dump_every_stone_is_linked_and_every_link_is_a_stone(stones):
    found = {(s.area, s.label) for s in stones}
    print(f"{len(stones)} talking stones, {len({s.label for s in stones})} labels")
    for s in stones:
        print(f"  {s.area:20} {s.label:34} {s.ages:6} {hints.STONE_LINKS.get((s.area, s.label), ('?',))[0]}")
    assert found == set(hints.STONE_LINKS)
    linked = sum(1 for name, _ in hints.STONE_LINKS.values() if name)
    assert linked + len(hints.OOTR_STONES_MISSING) == 40  # OoT Randomizer's HintStone locations at 526b4c8d


@pytest.mark.dump
def test_dump_every_stone_has_its_line_in_every_language(stones, message_files):
    labels = {s.label for s in stones}
    for language, files in message_files.items():
        missing = labels - set(files[hints.GOSSIP_MESSAGES].messages)
        assert not missing, f"{language}: {sorted(missing)}"
    print(f"{len(labels)} labels in {hints.GOSSIP_MESSAGES} of {len(message_files)} languages")


@pytest.mark.dump
def test_dump_a_stone_speaks_only_to_the_mask_of_truth(romfs):
    flow = hints.read_flow(romfs, hints.GOSSIP_FLOW)
    gates = hints.talk_gates(flow)
    for gate in gates:
        print(f"  {gate.event} {gate.actor}.{gate.query} {dict(gate.params)} case {gate.case}")
    assert [(g.query, dict(g.params).get("Actor") or dict(g.params).get("ArmorName"), g.case) for g in gates] == [
        ("EventQueryIsExistInPouch", hints.MASK_OF_TRUTH, 0),
        ("EventQueryPlayerIsEquipArmor", hints.MASK_OF_TRUTH, 0),
    ]
    assert hints.needs_mask_of_truth(gates)


@pytest.mark.dump
def test_dump_hint_givers_show_their_labels(romfs, message_files):
    for giver in hints.HINT_GIVERS:
        flow = hints.read_flow(romfs, giver.flow)
        shown = {
            value
            for event in flow.events
            if isinstance(event, evfl.ActionEvent)
            for value in (event.params or {}).values()
            if isinstance(value, str)
        }
        prefix = giver.messages.removesuffix(".msbt") + ":"
        for label in giver.labels:
            assert prefix + label in shown, f"{giver.flow} does not show {prefix}{label}"
            for language, files in message_files.items():
                assert label in files[giver.messages].messages, f"{language}: {giver.messages} lacks {label}"
