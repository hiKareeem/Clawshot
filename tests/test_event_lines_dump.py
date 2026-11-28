"""The hand-read marks in ``patch/event_marks.toml`` against the dump (spec event-items 1.4, plan 5.6;
plans/event-items.md "Hand-read marks")."""

from pathlib import Path

import pytest

from clawshot.formats import msbt, sarc, zsdic
from clawshot.patch import event_lines, text

pytestmark = pytest.mark.dump

GIVEN = "Item_Boomerang"


def _archives(romfs: Path) -> dict[str, bytes]:
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    out = {}
    for language in text.languages(romfs):
        path = text.archive_path(language)
        out[language] = dicts.decompress(path, (romfs / path).read_bytes())
    return out


def test_dump_every_mark_resolves_its_fingerprint_matches_and_its_slice_is_not_empty(romfs):
    archives = {language: sarc.read(data) for language, data in _archives(romfs).items()}
    problems = []
    for line in event_lines.load():
        for language, marks in line.marks.items():
            files = archives.get(language, {})
            parts = msbt.read(files[line.file]).messages.get(line.label) if line.file in files else None
            if parts is None:
                problems.append((line.file, line.label, language, "missing"))
                continue
            if event_lines.fingerprint(parts) != marks.fingerprint:
                problems.append((line.file, line.label, language, "fingerprint"))
            raw = event_lines.raw_text(parts)
            problems += [
                (line.file, line.label, language, (start, length))
                for start, length in marks.spans
                if start + length > len(raw) or not raw[start : start + length].strip()
            ]
    assert problems == []


def test_dump_with_every_check_moved_each_marked_line_names_the_given_item_and_nothing_else_changes(romfs):
    lines = event_lines.load()
    moved = event_lines.moved_lines(lines, {line.check: "moved" for line in lines}, {}, lambda item: GIVEN)
    transforms = event_lines.changes(romfs, moved)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    key = text.read_text_key(romfs, GIVEN, dicts)
    for language, data in _archives(romfs).items():
        before, after = sarc.read(data), sarc.read(transforms[text.archive_path(language)](data))
        name = event_lines.raw_text(text.item_name(msbt.read(before[text.POUCH_TEXT]), key))
        for (file, label), pairs in sorted(moved.items()):
            old, new = (msbt.read(x[file]).messages[label] for x in (before, after))
            spans = sorted({s for line, _ in pairs if language in line.marks for s in line.marks[language].spans})
            raw, expected, at = event_lines.raw_text(old), [], 0
            for start, length in spans:
                expected += [raw[at:start], name]
                at = start + length
            assert event_lines.raw_text(new) == "".join([*expected, raw[at:]]), (language, file, label)
            if not spans:
                assert new == old, (language, file, label)
        changed = {f for f in after if after[f] != before[f]}
        assert changed <= {file for file, _ in moved}, (language, sorted(changed))
