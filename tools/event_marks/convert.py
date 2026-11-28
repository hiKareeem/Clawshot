"""Write ``src/clawshot/patch/event_marks.toml`` from the hand-read reading sheets (event-items, 2026-11-27).

usage: uv run python -m tools.event_marks.convert ROMFS SHEET.tsv [SHEET.tsv ...] [--out PATH]

The sheets (``final.tsv``: columns ``group check actor file en_label lang target_label span occurrence note``) hold game
text and stay outside the repository (AGENTS.md rule 1). Each row is one mark (or ``-`` with ``COVERED BY <label>`` or
``NOT NAMED``) on one line in one language: ``span`` is the exact words in ``target_label`` of ``file`` in that
language's text as the reading helper showed it (:func:`clawshot.patch.event_lines.raw_text`, whitespace collapsed),
``occurrence`` its n-th place there. This tool finds each span in the dump (read only) and writes its position in the
raw text plus the line's fingerprint: no span text reaches the repository.

Check names in the sheets are OoT Randomizer location names (``gift_rules.toml`` checks, ``dungeon_rewards.toml``
slots) or census ``name`` fields of ``locations.toml``; ``<check> = <item>`` names a progressive tier, ``a | b`` and
``<flow> EventA / EventB (<actor>)`` two checks. A census name with an OoT Randomizer name maps to it; one without is
kept (that check is not randomizable today, so its marks wait). Any row that maps to none is listed and nothing is
written.
"""

import csv
import re
import sys
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from clawshot.census import definitions
from clawshot.formats import msbt, sarc, zsdic
from clawshot.generate.rewards import catalog
from clawshot.patch import event_lines, gifts, text

OUT = Path(__file__).resolve().parents[2] / "src" / "clawshot" / "patch" / "event_marks.toml"
COLUMNS = ["group", "check", "actor", "file", "en_label", "lang", "target_label", "span", "occurrence", "note"]
TWO_EVENTS = re.compile(r"^(?P<flow>\S+) (?P<a>Event\d+) / (?P<b>Event\d+) (?P<actor>\(.+\))$")


def read_rows(paths: Iterable[Path]) -> list[dict[str, str]]:
    rows = []
    for path in paths:
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t", quoting=csv.QUOTE_NONE)
            if reader.fieldnames != COLUMNS:
                raise SystemExit(f"{path}: columns {reader.fieldnames}, expected {COLUMNS}")
            rows += list(reader)
    return rows


def sheet_checks(name: str) -> list[str]:
    """The sheet's check name as the names it combines: ``a | b`` and ``<flow> EventA / EventB (<actor>)`` are two,
    ``<check> = <tier>`` is the check."""
    out = []
    for piece in name.split(" | "):
        piece = piece.split(" = ")[0].strip()
        if match := TWO_EVENTS.match(piece):
            out += [f"{match['flow']} {match[e]} {match['actor']}" for e in ("a", "b")]
        else:
            out.append(piece)
    return list(dict.fromkeys(out))


def check_keys() -> tuple[set[str], dict[str, str]]:
    """The placement keys the pipeline knows (gift checks, reward slots) and census name -> OoT Randomizer name."""
    known = set(gifts.load()) | set(catalog()["slots"])
    census = {d.name: d.oot_randomizer_name for d in definitions.load()}
    return known, census


def resolve(name: str, known: set[str], census: Mapping[str, str]) -> str | None:
    if name in known:
        return name
    if name in census:
        return census[name] or name  # no OoT Randomizer name: not randomizable today, the marks wait
    return None


def build(
    rows: Sequence[Mapping[str, str]],
    messages: Mapping[str, Mapping[str, Mapping[str, list]]],
    known: set[str],
    census: Mapping[str, str],
) -> tuple[list[dict], dict[str, int], list[str]]:
    """The data file's lines, counts, and problems (rows that map to no check or whose span is not found)."""
    problems: list[str] = []
    counts = {"rows": len(rows), "covered": 0, "not named": 0}
    spans: dict[tuple[str, str, str, str], set[tuple[str, int]]] = defaultdict(set)
    items: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for number, row in enumerate(rows, start=2):
        checks = []
        for name in sheet_checks(row["check"]):
            key = resolve(name, known, census)
            if key is None:
                problems.append(f"row {number}: check {name!r} ({row['check']!r}) maps to no check")
            else:
                checks.append(key)
        if row["span"] == "-":
            note = row["note"]
            counts["covered" if note.startswith("COVERED BY") else "not named"] += 1
            if not (note.startswith("COVERED BY") or note.startswith("NOT NAMED")):
                problems.append(f"row {number}: span '-' with note {note[:40]!r}")
            continue
        file = row["file"] + ".msbt"
        for check in checks:
            items[(check, file, row["target_label"])] |= set(re.split(r"\s*[|/]\s*", row["actor"]))
            spans[(check, file, row["target_label"], row["lang"])].add((row["span"], int(row["occurrence"])))
    lines: dict[tuple[str, str, str], dict] = {}
    for (check, file, label, language), marked in sorted(spans.items()):
        line = messages.get(language, {}).get(file, {}).get(label)
        if line is None:
            problems.append(f"{file}:{label} {language}: no such message in the dump")
            continue
        raw = event_lines.raw_text(line)
        at = []
        for span, occurrence in sorted(marked):
            found = event_lines.locate(raw, span, occurrence)
            if found is None:
                problems.append(f"{file}:{label} {language} ({check}): occurrence {occurrence} of a span not found")
                continue
            at.append(list(found))
        at.sort()
        if any(a + n > b for (a, n), (b, _) in zip(at, at[1:], strict=False)):
            problems.append(f"{file}:{label} {language} ({check}): marks overlap {at}")
        entry = lines.setdefault(
            (check, file, label),
            {"check": check, "item": "|".join(sorted(items[(check, file, label)])), "file": file, "label": label},
        )
        entry.setdefault("marks", {})[language] = {"fingerprint": event_lines.fingerprint(line), "at": at}
    _cross_check_overlaps(lines.values(), problems)
    return [lines[k] for k in sorted(lines, key=lambda k: (k[1], k[2], k[0]))], counts, problems


def _cross_check_overlaps(lines: Iterable[dict], problems: list[str]) -> None:
    """Two checks' marks on one line (a line naming two prizes) must not overlap: both may move in one seed. The same
    words marked for two checks (one line before either of two events) are allowed: the patch fills them once."""
    by_message: dict[tuple[str, str, str], list[list[int]]] = defaultdict(list)
    for line in lines:
        for language, value in line["marks"].items():
            by_message[(line["file"], line["label"], language)] += value["at"]
    for (file, label, language), at in sorted(by_message.items()):
        at = sorted({tuple(a) for a in at})  # the same words marked for two checks: the patch says one item there
        if any(a + n > b for (a, n), (b, _) in zip(at, at[1:], strict=False)):
            problems.append(f"{file}:{label} {language}: two checks' marks overlap {at}")


def _quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


HEADER = """\
# BBender's hand-read marks: in each line a gift's NPC says, the words naming the item given, sold, handed over or
# won (plans/event-items.md, "Hand-read marks", 2026-11-27). Read by clawshot.patch.event_lines; written by
# `uv run python -m tools.event_marks.convert ROMFS final.tsv [extra.tsv]` from the reading sheets, which hold game
# text and stay outside the repository (AGENTS.md rule 1). Read on dump 1.1.1.
#
#   check  the check whose item the marked words name (gift_rules.toml check, dungeon_rewards.toml slot, or the
#          census name of a check not randomizable today: its marks wait)
#   item   the vanilla item actor(s) the words name ("|" between a progressive pair); a record, not read
#   file   the message file in each language archive; label the message
#   marks.<language>  fingerprint: first 16 hex digits of the sha256 of the line's raw text (event_lines.raw_text:
#          text parts, and a declined-forms tag 201/10 as its first form, other tags left out); at: [start, length]
#          per mark in that raw text, in code points, a declined-forms tag counting as its form's length.
#          A language with no marks keeps its line (it names the item in an earlier box, or nowhere).
#
"""


def dumps(lines: Sequence[dict], counts: Mapping[str, int]) -> str:
    marks = sum(len(v["at"]) for line in lines for v in line["marks"].values())
    languages = sum(len(line["marks"]) for line in lines)
    out = [
        HEADER
        + f"# {len(lines)} lines, {languages} line-languages with {marks} marks; from {counts['rows']} sheet rows, of"
        + f"\n# which {counts['covered']} name the item in an earlier box and {counts['not named']} name it nowhere.\n"
    ]
    for line in lines:
        out.append("[[line]]")
        for key in ("check", "item", "file", "label"):
            out.append(f"{key} = {_quote(line[key])}")
        for language, value in sorted(line["marks"].items()):
            at = ", ".join(f"[{a}, {n}]" for a, n in value["at"])
            out.append(f'marks.{language} = {{ fingerprint = "{value["fingerprint"]}", at = [{at}] }}')
        out.append("")
    return "\n".join(out)


def dump_messages(romfs: Path, wanted: set[str]) -> dict[str, dict[str, dict[str, list]]]:
    """language -> message file -> label -> parts for the files ``wanted`` (read only)."""
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    out = {}
    for language in text.languages(romfs):
        path = text.archive_path(language)
        files = sarc.read(dicts.decompress(path, (romfs / path).read_bytes()))
        out[language] = {f: msbt.read(files[f]).messages for f in sorted(wanted) if f in files}
    return out


def main(argv: Sequence[str]) -> int:
    args = list(argv)
    out = OUT
    if "--out" in args:
        at = args.index("--out")
        out = Path(args[at + 1])
        del args[at : at + 2]
    if len(args) < 2:
        print(__doc__)
        return 2
    romfs, sheets = Path(args[0]), [Path(a) for a in args[1:]]
    rows = read_rows(sheets)
    known, census = check_keys()
    messages = dump_messages(romfs, {r["file"] + ".msbt" for r in rows})
    lines, counts, problems = build(rows, messages, known, census)
    if problems:
        print("\n".join(problems))
        return 1
    out.write_bytes(dumps(lines, counts).encode("utf-8"))
    event_lines.load(out)  # reads back
    print(f"{out}: {len(lines)} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
