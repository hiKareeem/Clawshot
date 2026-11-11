"""Get-window text for small keys that leave their dungeon: one message pair per target dungeon a seed uses.

The native get window shows the small key's own lines (``Dm_SY_Get:GetMessage``/``GetCaption`` look them up at run
time), which name no dungeon and speak of the current area: wrong for a key found elsewhere. Instead of renaming the
native key, :func:`changes` appends to ``EventFlowMsg/Dm_SY_Get.msbt`` in every language archive, for each target
used, the pair :func:`labels` names (``Clawshot_SmallKey_<target ID>_GetMessage`` and ``_GetCaption``):

- main: ``<key noun> (<dungeon name>)``;
- caption: ``Opens one locked door.`` and, on a second row, ``Dungeon: <dungeon name>``.

The key noun (``ActorMsg/PouchContent.msbt:Item_Dungeon_SmallKey_Name``) and each dungeon's name
(``LocationMsg/Location.msbt``, by the target's location label) are the game's English ones, read from the player's
``USen`` archive when the seed is made, their text without tags; every language gets the same English lines (as hints
do, D26). Plain text rows like the native key's own get lines; no table of game text is kept here. A target ID not
in :data:`~clawshot.patch.key_targets.TARGETS`, claimed by two targets, or one whose name is missing, blank or the
same as another used target's is refused: there is no fallback to a raw ID or the current area.
"""

import re
from collections.abc import Iterable
from pathlib import Path

from clawshot.formats import msbt, sarc, zsdic
from clawshot.patch import text
from clawshot.patch.key_targets import TARGETS, KeyTarget
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

GET_TEXT = "EventFlowMsg/Dm_SY_Get.msbt"
GET_MESSAGES = GET_TEXT.removesuffix(".msbt")  # the file as a MessageId names it
LOCATION_TEXT = "LocationMsg/Location.msbt"
KEY_NOUN = "Item_Dungeon_SmallKey_Name"
LABEL = "Clawshot_SmallKey_{target}_{role}"
ROLES = ("GetMessage", "GetCaption")
MAIN = "{key} ({dungeon})"
CAPTION = "Opens one locked door.\nDungeon: {dungeon}"
_TARGET_ID = re.compile(r"[A-Za-z0-9_]+")  # fits a message label and a ``file:label`` MessageId


def _targets() -> dict[str, KeyTarget]:
    """:data:`TARGETS` by native target ID."""
    by_id: dict[str, KeyTarget] = {}
    for logical in sorted(TARGETS):
        target = TARGETS[logical]
        if not _TARGET_ID.fullmatch(target.id):
            raise PatchError(f"small-key target {logical}: {target.id!r} cannot be part of a message label")
        if by_id.setdefault(target.id, target) != target:
            raise PatchError(f"small-key target ID {target.id} is claimed by {by_id[target.id]} and {target}")
    return by_id


def _known(target_ids: Iterable[str]) -> dict[str, KeyTarget]:
    """The targets of ``target_ids``, sorted by ID; an unknown ID raises :class:`PatchError`."""
    by_id = _targets()
    used = sorted(set(target_ids))
    unknown = [target for target in used if target not in by_id]
    if unknown:
        raise PatchError(f"no small-key target {unknown}")
    return {target: by_id[target] for target in used}


def _labels(target_id: str) -> tuple[str, str]:
    main, caption = (LABEL.format(target=target_id, role=role) for role in ROLES)
    return main, caption


def labels(target_id: str) -> tuple[str, str]:
    """The MessageIds of ``target_id``'s acquisition message and caption, as a flow's ``EventTalk`` names them
    (``EventFlowMsg/Dm_SY_Get:Clawshot_SmallKey_<target_id>_GetMessage`` and ``..._GetCaption``)."""
    _known([target_id])
    main, caption = (f"{GET_MESSAGES}:{label}" for label in _labels(target_id))
    return main, caption


def _name(messages: msbt.Msbt, label: str, what: str) -> str:
    """The text of message ``label`` without its tags, its whitespace closed up to single spaces."""
    if label not in messages.messages:
        raise PatchError(f"{what}: no English message labelled {label}")
    name = " ".join(msbt.plain(messages.messages[label]).split())
    if not name:
        raise PatchError(f"{what}: the English message {label} has no text")
    return name


def changes(romfs: str | Path, target_ids: Iterable[str]) -> FileChanges:
    """Every language archive with the get-window pair of each small-key target in ``target_ids`` (native IDs, as
    :func:`labels` takes them) added; nothing for no targets."""
    targets = _known(target_ids)
    if not targets:
        return {}
    romfs = Path(romfs)
    archive = text.archive_path(text.NAME_LANGUAGE)
    if not (romfs / archive).is_file():
        raise PatchError(f"no {archive} to read the English names from")
    files = sarc.read(zsdic.Dictionaries.from_romfs(romfs).decompress(archive, (romfs / archive).read_bytes()))
    for member in (LOCATION_TEXT, text.POUCH_TEXT):
        if member not in files:
            raise PatchError(f"{archive}: no message file {member}")
    locations, pouch = msbt.read(files[LOCATION_TEXT]), msbt.read(files[text.POUCH_TEXT])
    key = _name(pouch, KEY_NOUN, text.POUCH_TEXT)
    owners: dict[str, str] = {}
    additions: dict[str, list[msbt.Part]] = {}
    for target_id, target in targets.items():
        dungeon = _name(locations, target.location_label, f"{LOCATION_TEXT} (small-key target {target_id})")
        if owners.setdefault(dungeon, target_id) != target_id:
            raise PatchError(f"small-key targets {owners[dungeon]} and {target_id} are both named {dungeon!r}")
        main, caption = _labels(target_id)
        additions[main] = [MAIN.format(key=key, dungeon=dungeon)]
        additions[caption] = [CAPTION.format(dungeon=dungeon)]
    transform = text.add_messages({GET_TEXT: additions})
    return {text.archive_path(language): transform for language in text.languages(romfs)}
