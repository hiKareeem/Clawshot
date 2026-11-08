"""A whole seed's hints on the dump (round 7): every hint names a placed item at a stone readable without it, and
the stones say what the spoiler says."""

import pytest

from clawshot.census import hints as census
from clawshot.formats import msbt, sarc, zsdic
from clawshot.generate import Settings
from clawshot.generate import hints as stone_hints
from clawshot.patch import make_seed, text
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
def test_dump_the_stones_say_the_spoiler_hints(output, romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    changes = {path: transform for step in output.extra_changes for path, transform in step.items()}
    archives = [text.archive_path(language) for language in text.languages(romfs)]
    assert set(archives) <= set(changes)
    flow = census.flow_path(romfs, census.GOSSIP_FLOW)
    assert (flow in changes) == (output.seed.settings.hints == "always")
    spoken = {hint["label"]: hint["text"] for hint in output.spoiler()["hints"]}
    for path in archives:
        data = dicts.decompress(path, (romfs / path).read_bytes())
        written = changes[path](data)
        lines = msbt.read(sarc.read(written)[census.GOSSIP_MESSAGES]).messages
        for label, said in spoken.items():
            shown = "".join(p if isinstance(p, str) else " " if p == text.PAGE_BREAK else "" for p in lines[label])
            assert " ".join(shown.split()) == said, (path, label)
