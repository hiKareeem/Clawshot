"""All sixteen native archives: replace only both Sheik tool lines and compose with stone text."""

import pytest

from clawshot.formats import msbt, sarc, zsdic
from clawshot.patch import text

pytestmark = pytest.mark.dump


def test_sheik_directions_in_every_language_preserve_all_other_messages(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    location = "Synthetic Forest Reward Chest"
    transforms = text.sheik_hint_changes(romfs, [location])
    assert set(transforms) == {text.archive_path(language) for language in text.languages(romfs)}
    assert len(transforms) == 16
    for path, transform in transforms.items():
        data = dictionaries.decompress(path, (romfs / path).read_bytes())
        originals = sarc.read(data)
        stone = next(
            label
            for label in msbt.read(originals["EventFlowMsg/GossipStone.msbt"]).messages
            if label.startswith("GOSSIP_")
        )
        composed = text.stone_lines_transform({stone: "A separate synthetic rumor."})(data)
        before = sarc.read(composed)
        after = sarc.read(transform(composed))
        expected = msbt.read(before[text.SHEIK_MESSAGES])
        changed = msbt.read(after[text.SHEIK_MESSAGES])
        for label in text.SHEIK_TOOL_LABELS:
            shown = msbt.plain(changed.messages[label])
            assert location in shown.replace("\n", " ")
            assert "Hookshot" in shown
            assert msbt.Tag(0, 3, text.HIGHLIGHT) in changed.messages[label]
            assert msbt.Tag(0, 3, text.RESET) in changed.messages[label]
            changed.messages[label] = expected.messages[label]
        assert changed == expected
        after[text.SHEIK_MESSAGES] = before[text.SHEIK_MESSAGES]
        assert after == before
