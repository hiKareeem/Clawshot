"""Message files (``.msbt`` inside ``Mals/<language>.Product.110.sarc.zs``): read and write.

Written from the files themselves and the public description of LibMessageStudio's MSBT version 3
(https://nintendo-formats.com/libs/lms/msbt.html). No code from any other implementation. Every message file in this
game (build ``e0f3ccfa``, 540 per language, 16 languages) has the same shape, and the reader accepts only that:

- A 0x20-byte header: ``MsgStdBn``, byte-order mark ``FF FE`` (little-endian), encoding 0 (UTF-8), version 3, two
  sections, the file size, zero padding.
- Two sections, ``LBL1`` then ``TXT2``, each a 0x10-byte header (magic, body size, eight zero bytes) and its body,
  padded with ``0xAB`` to a multiple of 16; the file ends after the last padding. No ``ATR1``, ``TSY1`` or ``NLI1``.
- ``LBL1`` is a hash table: a bucket count, per bucket (entry count, offset of its first entry), then the entries
  bucket after bucket, each a length byte, the label in ASCII and the u32 index of its message. A label's bucket is
  :func:`label_hash` modulo the bucket count, and inside a bucket entries come in ascending message index.
- ``TXT2`` is the message count, one u32 offset per message (from the body's start), then the messages in index
  order, each UTF-8 text with control tags, ended by one zero byte. A tag is ``0x0E``, u16 group, u16 type, u16
  parameter size and the parameters; ``0x0F``, u16 group, u16 type closes one. UTF-8 never uses the bytes 0x00,
  0x0E or 0x0F inside a character, so the text is scanned byte by byte.

A file is read into :class:`Msbt`: the messages by label, in index order, each a list of text and :class:`Tag` /
:class:`TagEnd` parts, plus the bucket count. Writing puts it back in the layout above, so every message file in the
dump writes back byte-identical (``tests/test_msbt_dump.py``). Tag parameters are kept as bytes: their meaning is
game-specific (group 0 is the library's own: ruby, font, size, colour, page break; the others are this game's).
"""

import struct
from dataclasses import dataclass

MAGIC = b"MsgStdBn"
VERSION = 3
ENCODING_UTF8 = 0
HASH_MULTIPLIER = 0x492
_HEADER = struct.Struct("<8sHHBBHHI10s")
_SECTION = struct.Struct("<4sI8s")
_TAG = struct.Struct("<HHH")
_TAG_END = struct.Struct("<HH")
_PAD = b"\xab"
TAG_START, TAG_CLOSE = 0x0E, 0x0F


class MsbtError(ValueError):
    pass


@dataclass(frozen=True)
class Tag:
    """A control tag: ``group`` and ``type`` name it, ``params`` are its raw parameter bytes."""

    group: int
    type: int
    params: bytes = b""


@dataclass(frozen=True)
class TagEnd:
    """The end of the region a :class:`Tag` of the same group and type affects."""

    group: int
    type: int


Part = str | Tag | TagEnd


@dataclass
class Msbt:
    """A message file: ``messages`` maps each label to its parts, in message index order; ``buckets`` is the size of
    the label hash table."""

    messages: dict[str, list[Part]]
    buckets: int


def label_hash(label: str) -> int:
    """The label's hash; its bucket is this modulo the bucket count."""
    h = 0
    for c in label.encode("ascii"):
        h = (h * HASH_MULTIPLIER + c) & 0xFFFFFFFF
    return h


def plain(parts: list[Part]) -> str:
    """The message's text with its tags left out."""
    return "".join(p for p in parts if isinstance(p, str))


def normalized(parts: list[Part]) -> list[Part]:
    """``parts`` as :func:`read` returns them: neighbouring text joined, empty text dropped. Writing ``parts`` and
    reading the file back gives this."""
    out: list[Part] = []
    for part in parts:
        if isinstance(part, str):
            if not part:
                continue
            if out and isinstance(out[-1], str):
                out[-1] += part
                continue
        out.append(part)
    return out


# --- reading ------------------------------------------------------------------------------------------------------


def _sections(data: bytes) -> dict[bytes, bytes]:
    if len(data) < _HEADER.size:
        raise MsbtError(f"too short for an MSBT header: {len(data)} bytes")
    magic, bom, unknown, encoding, version, count, unknown2, size, padding = _HEADER.unpack_from(data, 0)
    if magic != MAGIC:
        raise MsbtError(f"not an MSBT file: magic {magic!r}")
    if bom != 0xFEFF:
        raise MsbtError(f"only little-endian MSBT is supported (byte-order mark bytes {data[8:10].hex()})")
    if encoding != ENCODING_UTF8:
        raise MsbtError(f"only UTF-8 MSBT is supported (encoding {encoding})")
    if version != VERSION or unknown or unknown2 or any(padding):
        raise MsbtError(
            f"unexpected header: version {version}, fields 0x0a={unknown} 0x10={unknown2}, padding {padding.hex()}"
        )
    if size != len(data):
        raise MsbtError(f"header says {size} bytes, file has {len(data)}")
    sections: dict[bytes, bytes] = {}
    off = _HEADER.size
    for _ in range(count):
        magic, body_size, reserved = _SECTION.unpack_from(data, off)
        if any(reserved):
            raise MsbtError(f"section {magic!r} at 0x{off:x}: non-zero header bytes {reserved.hex()}")
        body_at = off + _SECTION.size
        body_end = body_at + body_size
        sections[magic] = data[body_at:body_end]
        off = _align16(body_end)
        if data[body_end:off] != _PAD * (off - body_end):
            raise MsbtError(f"section {magic!r}: padding {data[body_end:off].hex()} is not 0xAB")
    if off != len(data):
        raise MsbtError(f"{len(data) - off} bytes after the last section")
    if list(sections) != [b"LBL1", b"TXT2"]:
        raise MsbtError(f"expected sections LBL1, TXT2; found {[m.decode('latin-1') for m in sections]}")
    return sections


def _labels(body: bytes) -> tuple[int, dict[int, str]]:
    (buckets,) = struct.unpack_from("<I", body, 0)
    labels: dict[int, str] = {}
    expected = 4 + 8 * buckets
    for bucket in range(buckets):
        count, off = struct.unpack_from("<II", body, 4 + 8 * bucket)
        if off != expected:
            raise MsbtError(f"LBL1 bucket {bucket} starts at 0x{off:x}, expected 0x{expected:x}")
        previous = -1
        for _ in range(count):
            length = body[off]
            label = body[off + 1 : off + 1 + length].decode("ascii")
            (index,) = struct.unpack_from("<I", body, off + 1 + length)
            if label_hash(label) % buckets != bucket:
                raise MsbtError(f"label {label!r} is in bucket {bucket}, its hash says {label_hash(label) % buckets}")
            if index <= previous:
                raise MsbtError(f"LBL1 bucket {bucket}: index {index} after {previous} (not ascending)")
            if index in labels:
                raise MsbtError(f"message {index} has two labels: {labels[index]!r}, {label!r}")
            labels[index] = label
            previous = index
            off += 1 + length + 4
        expected = off
    if expected != len(body):
        raise MsbtError(f"LBL1: {len(body) - expected} bytes after the last label")
    return buckets, labels


def _parse_text(raw: bytes, where: str) -> list[Part]:
    parts: list[Part] = []
    text = bytearray()

    def flush() -> None:
        if text:
            parts.append(text.decode("utf-8"))
            text.clear()

    i = 0
    while i < len(raw):
        c = raw[i]
        if c == TAG_START:
            flush()
            group, type_, size = _TAG.unpack_from(raw, i + 1)
            start = i + 1 + _TAG.size
            if start + size > len(raw):
                raise MsbtError(f"{where}: tag {group}.{type_} at {i} runs past the message ({size} parameter bytes)")
            parts.append(Tag(group, type_, bytes(raw[start : start + size])))
            i = start + size
        elif c == TAG_CLOSE:
            flush()
            group, type_ = _TAG_END.unpack_from(raw, i + 1)
            parts.append(TagEnd(group, type_))
            i += 1 + _TAG_END.size
        elif c == 0:
            raise MsbtError(f"{where}: zero byte at {i} before the end of the message")
        else:
            text.append(c)
            i += 1
    flush()
    return parts


def _texts(body: bytes) -> list[list[Part]]:
    (count,) = struct.unpack_from("<I", body, 0)
    offsets = list(struct.unpack_from(f"<{count}I", body, 4))
    expected = 4 + 4 * count
    messages = []
    for index, start in enumerate(offsets):
        end = offsets[index + 1] if index + 1 < count else len(body)
        if start != expected or end <= start or body[end - 1] != 0:
            raise MsbtError(f"TXT2 message {index}: bytes 0x{start:x}..0x{end:x} are not one zero-ended message")
        messages.append(_parse_text(body[start : end - 1], f"TXT2 message {index}"))
        expected = end
    return messages


def read(data: bytes) -> Msbt:
    sections = _sections(data)
    buckets, labels = _labels(sections[b"LBL1"])
    texts = _texts(sections[b"TXT2"])
    if sorted(labels) != list(range(len(texts))):
        raise MsbtError(f"{len(labels)} labels for {len(texts)} messages, or a message without a label")
    return Msbt({labels[i]: texts[i] for i in range(len(texts))}, buckets)


# --- writing ------------------------------------------------------------------------------------------------------


def _align16(n: int) -> int:
    return (n + 15) & ~15


def encode_text(parts: list[Part]) -> bytes:
    """One message's bytes, without its ending zero byte."""
    out = bytearray()
    for part in parts:
        if isinstance(part, str):
            raw = part.encode("utf-8")
            bad = {b for b in raw if b in (0, TAG_START, TAG_CLOSE)}
            if bad:
                raise MsbtError(f"text {part!r} holds a reserved byte ({', '.join(f'0x{b:02x}' for b in sorted(bad))})")
            out += raw
        elif isinstance(part, Tag):
            out.append(TAG_START)
            out += _TAG.pack(part.group, part.type, len(part.params)) + part.params
        elif isinstance(part, TagEnd):
            out.append(TAG_CLOSE)
            out += _TAG_END.pack(part.group, part.type)
        else:
            raise MsbtError(f"not a message part: {part!r} ({type(part).__name__})")
    return bytes(out)


def _label_section(labels: list[str], buckets: int) -> bytes:
    if buckets < 1:
        raise MsbtError(f"bucket count must be at least 1, not {buckets}")
    table: list[list[tuple[str, int]]] = [[] for _ in range(buckets)]
    for index, label in enumerate(labels):
        raw = label.encode("ascii")
        if not 0 < len(raw) < 256:
            raise MsbtError(f"label {label!r}: length must be 1..255 bytes")
        table[label_hash(label) % buckets].append((label, index))
    head = bytearray(struct.pack("<I", buckets))
    entries = bytearray()
    first = 4 + 8 * buckets
    for bucket in table:
        head += struct.pack("<II", len(bucket), first + len(entries))
        for label, index in bucket:
            raw = label.encode("ascii")
            entries += bytes([len(raw)]) + raw + struct.pack("<I", index)
    return bytes(head + entries)


def _text_section(texts: list[list[Part]]) -> bytes:
    blobs = [encode_text(parts) + b"\0" for parts in texts]
    offsets = []
    at = 4 + 4 * len(blobs)
    for blob in blobs:
        offsets.append(at)
        at += len(blob)
    return struct.pack(f"<I{len(blobs)}I", len(blobs), *offsets) + b"".join(blobs)


def write(msbt: Msbt) -> bytes:
    labels = list(msbt.messages)
    sections = [
        (b"LBL1", _label_section(labels, msbt.buckets)),
        (b"TXT2", _text_section([msbt.messages[label] for label in labels])),
    ]
    body = bytearray()
    for magic, section in sections:
        body += _SECTION.pack(magic, len(section), bytes(8)) + section
        body += _PAD * (_align16(len(body)) - len(body))
    size = _HEADER.size + len(body)
    header = _HEADER.pack(MAGIC, 0xFEFF, 0, ENCODING_UTF8, VERSION, len(sections), 0, size, bytes(10))
    return header + bytes(body)
