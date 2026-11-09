"""A whole seed's hints on the dump (round 7): every hint names a placed item at a stone readable without it, and
the stones say what the spoiler says."""

import pytest

from clawshot.census import hints as census
from clawshot.formats import msbt, sarc, zsdic
from clawshot.generate import Settings
from clawshot.generate import hints as stone_hints
from clawshot.patch import make_seed, text, write_seed
from clawshot.world.search import Search


@pytest.fixture(scope="module", params=["always", "mask"])
def output(request, romfs):
    return make_seed(romfs, 7, Settings(shuffle=("Chest", "Shop"), hints=request.param))


@pytest.mark.dump
def test_dump_every_hint_names_a_placed_item_at_a_stone_readable_without_it(output):
    seed = output.seed
    labels = census.stone_labels()
    assert [hint.stone for hint in seed.hints] == [name for name in seed.world.hint_stones if name in labels]
    assert {hint.label for hint in seed.hints} == set(labels.values())
    named = [hint for hint in seed.hints if hint.location is not None]
    assert named, "no hint names a location"
    if seed.settings.hints == "mask":
        before_mask = set(stone_hints.mask_prerequisites(seed))
        print("mask prerequisites:", sorted(before_mask))
        assert before_mask, "the Mask of Truth needs nothing shuffled"
        assert not before_mask & {hint.location for hint in named}
    for hint in named:
        assert hint.location in seed.shuffled, hint
        assert seed.placements[hint.location] == hint.item, hint
        search = Search(seed.world)
        search.collect_spheres({k: v for k, v in seed.placements.items() if k != hint.location})
        stone = stone_hints._readable(seed.world.hint_stones[hint.stone], seed.settings.hints)
        assert search.can_access(stone), hint
    kinds = {hint.kind for hint in seed.hints}
    print(seed.settings.hints, {kind: sum(h.kind == kind for h in seed.hints) for kind in sorted(kinds)})
    assert {"woth", "item", "junk"} <= kinds


@pytest.mark.dump
def test_dump_the_stones_say_the_spoiler_hints(output, romfs, tmp_path):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    out = tmp_path / "seed"
    write_seed(output, romfs, out)
    archives = [text.archive_path(language) for language in text.languages(romfs)]
    assert all((out / "romfs" / path).is_file() for path in archives)
    flow = census.flow_path(romfs, census.GOSSIP_FLOW)
    assert (out / "romfs" / flow).is_file() == (output.seed.settings.hints == "always")
    log = output.spoiler()
    spoken = {hint["label"]: hint["text"] for hint in log["hints"]}
    hookshot_locations = [
        log["locations"][name]["name"] for name in output.seed.shuffled if output.seed.placements[name] == "Hookshot"
    ]
    assert hookshot_locations
    for path in archives:
        written = dicts.decompress(path, (out / "romfs" / path).read_bytes())
        archive = sarc.read(written)
        lines = msbt.read(archive[census.GOSSIP_MESSAGES]).messages
        for label, said in spoken.items():
            shown = "".join(p if isinstance(p, str) else " " if p == text.PAGE_BREAK else "" for p in lines[label])
            assert " ".join(shown.split()) == said, (path, label)
        sheik = msbt.read(archive[text.SHEIK_MESSAGES]).messages
        for label in text.SHEIK_TOOL_LABELS:
            said = " ".join(msbt.plain(sheik[label]).split())
            assert any(location in said for location in hookshot_locations), (path, label, said)
