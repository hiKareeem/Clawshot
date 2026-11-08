"""Text patches: change message lines, name an item in a line, let Gossip Stones speak without the Mask of Truth.

Where the game's text comes from (``03-game-data.md`` section 22):

- Every line is a message in ``Mals/<language>.Product.110.sarc.zs``, an archive of MSBT files; a flow shows it by
  ``MessageId: "<file without .msbt>:<label>"``. :func:`edit_messages` gives the transform that replaces messages
  in one language's archive (decompressed bytes in and out, as :data:`clawshot.patch.write.FileChanges` expects).
- An item's texts are labelled by its actor's ``ActorName`` component (:func:`text_key`), in
  ``ActorMsg/PouchContent.msbt``: ``<key>_Name``, ``_Caption``, ``_GetMessage``, ``_GetCaption``, ... The get
  window shows ``Dm_SY_Get:GetMessage`` and ``GetCaption``, whose only content is a run-time tag (group 2, types
  23 and 19) for the item being given, so it names whatever item a chest, gift or shop gives. To name an item in
  another line, :func:`item_name` returns that language's ``<key>_Name`` (text and grammar tags), to put into the
  line; the line then reads right in each language it is built for.
- A stone's line is the ``GossipStone`` message labelled with its placement name; the flow asks for the Mask of
  Truth first. :func:`gossip_without_mask` re-points those two questions so every answer leads on.
"""

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from clawshot.census import hints
from clawshot.formats import byml, evfl, msbt, sarc, zsdic
from clawshot.formats.msbt import Part
from clawshot.patch.plan import PatchError

ARCHIVE = "Mals/{language}.Product.110.sarc.zs"
POUCH_TEXT = "ActorMsg/PouchContent.msbt"
ACTOR_PACK = "Pack/Actor/{actor}.pack.zs"


def archive_path(language: str) -> str:
    return ARCHIVE.format(language=language)


def languages(romfs: str | Path) -> list[str]:
    """The message languages in the dump (``USen``, ``EUen``, ...), sorted."""
    return sorted(p.name.split(".")[0] for p in (Path(romfs) / "Mals").glob("*.Product.110.sarc.zs"))


def edit_messages(edits: Mapping[str, Mapping[str, Sequence[Part]]]) -> Callable[[bytes], bytes]:
    """The transform of one language archive that sets ``edits[file][label]`` as each message's parts.

    Only existing messages are replaced; a missing file or label raises :class:`PatchError`. The archive and every
    changed file are read back before the bytes are returned."""

    def transform(data: bytes) -> bytes:
        files = sarc.read(data)
        for name in sorted(edits):
            if name not in files:
                raise PatchError(f"no message file {name} in the archive")
            document = msbt.read(files[name])
            for label, parts in edits[name].items():
                if label not in document.messages:
                    raise PatchError(f"{name}: no message labelled {label}")
                document.messages[label] = list(parts)
            written = msbt.write(document)
            if msbt.read(written) != document:
                raise PatchError(f"{name}: the written file does not read back as the edited messages")
            files[name] = written
        out = sarc.write(files)
        if sarc.read(out) != files:
            raise PatchError("the written archive does not read back as the edited files")
        return out

    return transform


def text_key(pack: Mapping[str, bytes], actor: str) -> str:
    """The name ``actor``'s texts are labelled by: its ``ActorNameRef`` component, the nearest along its ``$parent``
    chain inside ``pack`` (the actor pack's files), else the actor's own name."""
    name = f"Actor/{actor}.engine__actor__ActorParam.bgyml"
    seen = set()
    while name in pack and name not in seen:
        seen.add(name)
        tree = byml.read(pack[name])
        ref = str((tree.get("Components") or {}).get("ActorNameRef", ""))
        if ref:
            return ref.rsplit("/", 1)[-1].split(".", 1)[0]
        parent = str(tree.get("$parent", ""))
        name = "Actor/" + parent.rsplit("/", 1)[-1].replace(".gyml", ".bgyml") if parent else ""
    return actor


def read_text_key(romfs: str | Path, actor: str, dicts: zsdic.Dictionaries | None = None) -> str:
    romfs = Path(romfs)
    path = ACTOR_PACK.format(actor=actor)
    if not (romfs / path).is_file():
        raise PatchError(f"no actor pack {path}")
    dicts = dicts or zsdic.Dictionaries.from_romfs(romfs)
    return text_key(sarc.read(dicts.decompress(path, (romfs / path).read_bytes())), actor)


def item_name(pouch_text: msbt.Msbt, key: str) -> list[Part]:
    """The parts of ``<key>_Name`` in one language's ``ActorMsg/PouchContent.msbt``: the item's name as that
    language writes it, grammar tags included."""
    label = f"{key}_Name"
    if label not in pouch_text.messages:
        raise PatchError(f"{POUCH_TEXT}: no message labelled {label}")
    return list(pouch_text.messages[label])


def _is_mask_gate(gate: hints.TalkGate) -> bool:
    return hints.MASK_OF_TRUTH in dict(gate.params).values()


def gossip_without_mask(flowchart: evfl.Flowchart) -> list[str]:
    """Let every Gossip Stone speak whether or not Link has or wears the Mask of Truth: each Mask of Truth question
    on the way to the stone's line sends every answer where the needed one went. Edits ``flowchart`` in place and
    returns the names of the events changed."""
    gates = [gate for gate in hints.talk_gates(flowchart) if _is_mask_gate(gate)]
    if not gates:
        raise PatchError(f"{flowchart.name}: no Mask of Truth question on the way to the stone's line")
    by_name = {event.name: event for event in flowchart.events}
    for gate in gates:
        event = by_name[gate.event]
        target = dict(event.cases)[gate.case]
        event.cases = [(value, target) for value, _ in event.cases]
    left = [gate for gate in hints.talk_gates(flowchart) if _is_mask_gate(gate)]
    if left:
        raise PatchError(f"{flowchart.name}: Mask of Truth questions left after the edit: {left}")
    return [gate.event for gate in gates]


def gossip_flow_transform(data: bytes) -> bytes:
    """The ``GossipStone`` flow file (decompressed) with :func:`gossip_without_mask` applied, read back checked."""
    document = evfl.read(data)
    if document.flowchart is None:
        raise PatchError("the GossipStone flow holds no flowchart")
    gossip_without_mask(document.flowchart)
    written = evfl.write(document)
    if evfl.read(written) != document:
        raise PatchError("the written GossipStone flow does not read back as the edited flow")
    return written
