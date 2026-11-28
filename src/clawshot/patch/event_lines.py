"""NPC lines that name a gift's item say the item the seed gives there (spec event-items 1.4, plan task 5.6).

``event_marks.toml`` holds BBender's hand-read marks (``plans/event-items.md``, "Hand-read marks", 2026-11-27): for
each line in scope, its check, and per language the characters naming the vanilla item as ``[start, length]`` in the
line's :func:`raw_text`, plus a :func:`fingerprint` of that text. When a check's item changes, each language's marked
characters are cut and the given item's name (:func:`clawshot.patch.text.item_name`, grammar tags included) is put
in, always the same form and with no grammar fixed around it (decision 5.6, BBender 2026-11-25). A language without
marks keeps its line (it names the item in an earlier box, or nowhere). The repository keeps no game text (AGENTS.md
rule 1): the marks are positions; ``tools/event_marks`` converts the reading sheets, kept outside, into them.

A line whose text in the dump is not the one marked (its fingerprint differs: a game update changed it) is refused
with :class:`PatchError`, never guessed at.
"""

import hashlib
import tomllib
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from clawshot.formats import msbt, sarc, zsdic
from clawshot.formats.msbt import Part
from clawshot.patch import talon, text
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

MARKS_TOML = Path(__file__).with_name("event_marks.toml")
FIELDS = {"check", "item", "file", "label", "marks"}
# A word with its declined forms: a grammar tag whose parameters are (u16 byte length, UTF-8 text) per form; "0"
# marks a form the language does not have. The game shows the first form; Polish and some German names are only this.
FORMS_TAG = (201, 10)
# The grammar tag a language puts before a name (its gender and number); it belongs to the word that follows.
GENDER_TAG = (201, 0)
FINGERPRINT_SIZE = 16  # hex digits of the sha256 of the raw text
# Merchants whose first sale is a shuffled check and who return to their native sale afterwards (main's merchant
# sales: gifts.MERCHANT_SHOPS and gifts.GRANNY_CHECK). Both sales speak the same messages, so a renamed offer would
# keep naming the shuffled item on every repeat sale: their marks wait, like decision D's re-offers (Claude,
# 2026-11-28, rebase onto main; for BBender to confirm).
REPEAT_SALES = frozenset({"GC Medigoron", "Kak Granny Buy Blue Potion", "Wasteland Bombchu Salesman"})
# Talon's Cucco game (main's talon.py): with a moved prize, his first-prize lines (Talk_09_2, Talk_29) are main's
# neutral lines (its D26), and his repeat prize (Talk_11, Talk_56) and milk sale (Talk_57) still give milk. None of
# the five marked lines names the given item any more, so their marks wait (Claude, 2026-11-28, rebase onto main;
# for BBender to confirm; naming the item in the first-prize lines instead is a question for the maintainers).
WRITTEN_ELSEWHERE = frozenset({talon.CHECK})

Message = tuple[str, str]  # (message file in the archive, label)
Span = tuple[int, int]  # (start, length) in the raw text


@dataclass(frozen=True)
class Marks:
    fingerprint: str  # of the language's raw text the marks were read on
    spans: tuple[Span, ...]  # in the raw text, sorted, not overlapping


@dataclass(frozen=True)
class Line:
    check: str  # the check whose item the marked words name (a placement key; see tools/event_marks)
    item: str  # the vanilla item actor(s) the words name, "|" between a progressive pair (a record; not read)
    file: str  # "EventFlowMsg/<name>.msbt"
    label: str
    marks: Mapping[str, Marks]  # language -> its marks; a language without marks keeps its line


def _form(tag: msbt.Tag) -> str:
    """The word a declined-forms tag shows: its first form."""
    size = int.from_bytes(tag.params[:2], "little")
    return tag.params[2 : 2 + size].decode("utf-8")


def _is(part: Part, kind: tuple[int, int]) -> bool:
    return isinstance(part, msbt.Tag) and (part.group, part.type) == kind


def units(parts: Sequence[Part]) -> list[tuple[int, int, int]]:
    """(part index, start, end) in the raw text for each text part and each declined-forms tag (its first form's
    characters); other tags take no room."""
    out, at = [], 0
    for index, part in enumerate(parts):
        if isinstance(part, str):
            size = len(part)
        elif _is(part, FORMS_TAG):
            size = len(_form(part))
        else:
            continue
        out.append((index, at, at + size))
        at += size
    return out


def raw_text(parts: Sequence[Part]) -> str:
    """The line as the marks count it: its text parts as they are and each declined-forms tag as its first form (the
    word the game shows), other tags left out. Positions are Python string indices (code points)."""
    return "".join(
        part if isinstance(part, str) else _form(part)
        for part in parts
        if isinstance(part, str) or _is(part, FORMS_TAG)
    )


def fingerprint(parts: Sequence[Part]) -> str:
    return hashlib.sha256(raw_text(parts).encode("utf-8")).hexdigest()[:FINGERPRINT_SIZE]


def collapse(raw: str) -> tuple[str, list[int]]:
    """``raw`` with whitespace collapsed to single spaces and trimmed (the text the marks were read on), and for each
    of its characters the index in ``raw`` it comes from (a space: the first of its whitespace run)."""
    out: list[str] = []
    where: list[int] = []
    pending = -1
    for index, char in enumerate(raw):
        if char.isspace():
            if pending < 0:
                pending = index
            continue
        if pending >= 0 and out:
            out.append(" ")
            where.append(pending)
        pending = -1
        out.append(char)
        where.append(index)
    return "".join(out), where


def locate(raw: str, span: str, occurrence: int) -> Span | None:
    """The ``occurrence``-th (from 1) place of ``span`` in the collapsed ``raw``, as (start, length) in ``raw``."""
    collapsed, where = collapse(raw)
    at = -1
    for _ in range(occurrence):
        at = collapsed.find(span, at + 1)
        if at < 0:
            return None
    start, end = where[at], where[at + len(span) - 1] + 1
    return start, end - start


def apply_marks(parts: Sequence[Part], marks: Sequence[tuple[int, int, Sequence[Part]]]) -> list[Part]:
    """``parts`` with each (start, length, given) mark's raw-text characters replaced by ``given``, right to left.

    A text part loses the marked characters; a declined-forms tag touched by a mark goes whole. The gender tags
    (201/0) right before such a tag, or right before a mark that starts a text part, go too: they are the cut name's
    (the name as the item stores it), and ``given`` brings its own. Other tags inside a mark stay (a highlight around
    the name), and ``given`` goes where the mark's last character was, so it sits inside the name's highlight."""
    ordered = sorted(marks, key=lambda m: m[0], reverse=True)
    for (start, length, _), (next_start, *_rest) in zip(ordered[1:], ordered, strict=False):
        if start + length > next_start:
            raise PatchError(f"marks at {start} and {next_start} overlap")
    out = list(parts)
    for start, length, given in ordered:
        out = _cut(out, start, start + length, given)
    return msbt.normalized(out)


def _cut(parts: list[Part], start: int, end: int, given: Sequence[Part]) -> list[Part]:
    touched = [(index, s, e) for index, s, e in units(parts) if s < end and e > start]
    if end <= start or not touched or touched[0][1] > start or touched[-1][2] < end:
        raise PatchError(f"mark {start}+{end - start} is outside the line's text")
    last = touched[-1][0]
    drop: set[int] = set()
    first, first_start, _ = touched[0]
    heads = [index for index, _, _ in touched if not isinstance(parts[index], str)]
    if first_start == start:
        heads.append(first)  # the mark starts a name: the gender tags right before it are that name's
    for head in heads:
        if not isinstance(parts[head], str):
            drop.add(head)
        before = head - 1
        while before >= 0 and _is(parts[before], GENDER_TAG):
            drop.add(before)
            before -= 1
    spans = {index: (s, e) for index, s, e in touched}
    out: list[Part] = []
    for index, part in enumerate(parts):
        if index in spans and isinstance(part, str):
            s, e = spans[index]
            out.append(part[: max(0, start - s)])
            if index == last:
                out += [*given, part[end - s :]]
        elif index in drop:
            if index == last:
                out += list(given)
        else:
            out.append(part)
    return out


def _span(value: object) -> Span:
    if not (isinstance(value, list) and len(value) == 2 and all(type(v) is int for v in value)):
        raise PatchError(f"mark {value!r}: expected [start, length]")
    start, length = value
    if start < 0 or length < 1:
        raise PatchError(f"mark {value!r}: start must be >= 0 and length >= 1")
    return start, length


def loads(data: str) -> tuple[Line, ...]:
    out = []
    for entry in tomllib.loads(data).get("line", []):
        if set(entry) != FIELDS or not all(isinstance(entry[k], str) and entry[k] for k in FIELDS - {"marks"}):
            raise PatchError(f"event line {entry!r}: needs {sorted(FIELDS)}, each but marks a non-empty string")
        where = f"{entry['file']}:{entry['label']} ({entry['check']})"
        if not isinstance(entry["marks"], dict) or not entry["marks"]:
            raise PatchError(f"{where}: marks must map languages to their marks")
        marks = {}
        for language, value in sorted(entry["marks"].items()):
            if set(value) != {"fingerprint", "at"} or not isinstance(value["fingerprint"], str):
                raise PatchError(f"{where} {language}: needs fingerprint and at")
            if len(value["fingerprint"]) != FINGERPRINT_SIZE or not isinstance(value["at"], list) or not value["at"]:
                raise PatchError(f"{where} {language}: a {FINGERPRINT_SIZE}-digit fingerprint and one mark or more")
            spans = tuple(sorted(_span(v) for v in value["at"]))
            if any(a + n > b for (a, n), (b, _) in zip(spans, spans[1:], strict=False)):
                raise PatchError(f"{where} {language}: marks overlap")
            marks[language] = Marks(value["fingerprint"], spans)
        out.append(Line(entry["check"], entry["item"], entry["file"], entry["label"], marks))
    keys = [(line.check, line.file, line.label) for line in out]
    if len(set(keys)) != len(keys):
        raise PatchError("an event line is listed twice for one check")
    return tuple(out)


def load(path: str | Path = MARKS_TOML) -> tuple[Line, ...]:
    return loads(Path(path).read_text(encoding="utf-8"))


# message -> (line, text key of the given item), for the lines of moved checks
Swaps = Mapping[Message, Sequence[tuple[Line, str]]]


def edit_line(language: str, parts: Sequence[Part], swaps: Sequence[tuple[Line, Sequence[Part]]]) -> list[Part] | None:
    """One language's ``parts`` with every swap's marks replaced by its given name, or None when no swap marks
    anything in that language. A fingerprint that differs from the line's refuses it. The same words marked for two
    moved checks (a line said before either of two events) take the first swap's name."""
    marks: dict[Span, Sequence[Part]] = {}
    for line, given in swaps:
        mine = line.marks.get(language)
        if mine is None:
            continue
        if (found := fingerprint(parts)) != mine.fingerprint:
            raise PatchError(
                f"{line.file}:{line.label} {language}: the line is not the one marked (fingerprint {found}, marks "
                f"read on {mine.fingerprint}): a game update changed it; read its marks again"
            )
        for span in mine.spans:
            marks.setdefault(span, given)
    return apply_marks(parts, [(start, length, given) for (start, length), given in marks.items()]) if marks else None


def archive_transform(language: str, swaps: Swaps) -> Callable[[bytes], bytes]:
    """``language``'s archive transform: each line's marked words replaced by the given item's name."""

    def transform(data: bytes) -> bytes:
        files = sarc.read(data)
        pouch = msbt.read(files[text.POUCH_TEXT])
        edits: dict[str, dict[str, list[Part]]] = {}
        for (file, label), pairs in sorted(swaps.items()):
            if file not in files or label not in (messages := msbt.read(files[file]).messages):
                raise PatchError(f"{file}:{label}: no such message in {language}")
            given = [(line, text.item_name(pouch, key)) for line, key in pairs]
            edited = edit_line(language, messages[label], given)
            if edited is not None:
                edits.setdefault(file, {})[label] = edited
        return text.edit_messages(edits)(data)

    return transform


def moved_lines(
    lines: Sequence[Line], placements: Mapping[str, str], vanilla: Mapping[str, str], actor: Callable[[str], str]
) -> dict[Message, list[tuple[Line, str]]]:
    """Message -> (line, given actor) for the lines of checks whose placed item is not their vanilla one
    (``actor``: logic item -> the actor the grant gives); :data:`REPEAT_SALES` and :data:`WRITTEN_ELSEWHERE` keep
    their native text."""
    out: dict[Message, list[tuple[Line, str]]] = {}
    for line in lines:
        item = placements.get(line.check)
        if item is None or item == vanilla.get(line.check) or line.check in REPEAT_SALES | WRITTEN_ELSEWHERE:
            continue
        out.setdefault((line.file, line.label), []).append((line, actor(item)))
    return out


def _text_key(romfs: Path, actor: str, dicts: zsdic.Dictionaries) -> str:
    """The actor's text key; an actor without a pack in the dump (a custom item) labels its texts by its name."""
    if not (romfs / text.ACTOR_PACK.format(actor=actor)).is_file():
        return actor
    return text.read_text_key(romfs, actor, dicts)


def native_inputs(actors: Iterable[str]) -> tuple[str, ...]:
    """Every romfs file :func:`changes` can read when a line names any of the item ``actors``, the dictionaries' pack
    included, so the app's working set (``clawshot.pack.source.working_files``) holds them: each actor's pack, whose
    text key the line names (an actor without one is labelled by its name, so a pack left out would change the text
    silently). The language archives are every ``Mals/*.Product.110.sarc.zs``, which the working set's patterns
    hold."""
    return (zsdic.PACK_PATH, *(text.ACTOR_PACK.format(actor=actor) for actor in sorted(set(actors))))


def changes(romfs: str | Path, moved: Mapping[Message, Sequence[tuple[Line, str]]]) -> FileChanges:
    """The transforms of the language archives holding marks of ``moved`` (from :func:`moved_lines`)."""
    if not moved:
        return {}
    romfs = Path(romfs)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    keys = {a: _text_key(romfs, a, dicts) for a in sorted({a for pairs in moved.values() for _, a in pairs})}
    swaps = {message: [(line, keys[a]) for line, a in pairs] for message, pairs in sorted(moved.items())}
    present = set(text.languages(romfs))
    marked = sorted({language for pairs in swaps.values() for line, _ in pairs for language in line.marks})
    if missing := [language for language in marked if language not in present]:
        raise PatchError(f"event line marks for languages the dump does not have: {missing}")
    return {text.archive_path(language): archive_transform(language, swaps) for language in marked}
