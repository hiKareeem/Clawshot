"""Static Sheik directions cannot send players to the vanilla Hookshot in a shuffled seed."""

import pytest

from clawshot.formats import msbt, sarc
from clawshot.formats.msbt import Msbt, Tag
from clawshot.patch import text
from clawshot.patch.plan import PatchError


def archive(labels=("Talk_01", "Talk_03", "Talk_00")):
    messages = Msbt({label: [Tag(0, 2, b"P\0"), f"Synthetic {label}"] for label in labels}, buckets=3)
    return sarc.write({text.SHEIK_MESSAGES: msbt.write(messages), "Other.bin": b"unrelated"})


def apply(tmp_path, locations):
    (tmp_path / "Mals").mkdir()
    (tmp_path / text.archive_path("Synthetic")).touch()
    return text.sheik_hint_changes(tmp_path, locations)[text.archive_path("Synthetic")]


def test_both_directions_name_actual_location_and_preserve_other_messages(tmp_path):
    source = archive()
    patch = apply(tmp_path, ["Synthetic Hill Chest"])
    files = sarc.read(patch(source))
    messages = msbt.read(files[text.SHEIK_MESSAGES]).messages
    for label in text.SHEIK_TOOL_LABELS:
        assert "Synthetic Hill Chest" in msbt.plain(messages[label])
        assert "Hookshot" in msbt.plain(messages[label])
        assert Tag(0, 3, text.HIGHLIGHT) in messages[label]
        assert Tag(0, 3, text.RESET) in messages[label]
    assert messages["Talk_00"] == msbt.read(sarc.read(source)[text.SHEIK_MESSAGES]).messages["Talk_00"]
    assert files["Other.bin"] == b"unrelated"


def test_no_hookshot_in_slice_omits_false_tool_directions(tmp_path):
    files = sarc.read(apply(tmp_path, [])(archive()))
    for label in text.SHEIK_TOOL_LABELS:
        line = msbt.plain(msbt.read(files[text.SHEIK_MESSAGES]).messages[label])
        assert "Hookshot" not in line
        assert "Kakariko" not in line


def test_multiple_real_sources_select_same_true_location_in_any_order(tmp_path):
    patch = apply(tmp_path, ["B chest", "A chest"])
    original = archive()
    forward = patch(original)
    reverse = text.sheik_hint_changes(tmp_path, ["A chest", "B chest"])[text.archive_path("Synthetic")](original)
    assert forward == reverse
    said = msbt.plain(msbt.read(sarc.read(forward)[text.SHEIK_MESSAGES]).messages["Talk_03"])
    assert any(location in said for location in ("A chest", "B chest"))


def test_missing_native_tool_line_refuses_instead_of_leaving_wrong_directions(tmp_path):
    with pytest.raises(PatchError):
        apply(tmp_path, ["Hill"])(archive(("Talk_01", "Talk_00")))
