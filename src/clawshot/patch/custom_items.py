"""Items the game does not have: **Nothing** and **another player's item** (Archipelago), shown as Zelda's Letter.

Each is a new actor made from ``Item_ZeldaLetter`` (:data:`DONOR`), so a chest shows the letter in Link's hands, and
a get window with the actor's own text (``clawshot.patch.get_text``), and gives nothing:

- **Pack** ``Pack/Actor/<actor>.pack.zs``: the donor's pack with its ``ActorParam`` renamed for the new actor and its
  ``ActorNameRef`` pointing at the new name (:func:`build_pack`). Every other member (model, pouch component, physics)
  is the donor's, under the donor's paths.
- **Rows** in the three actor tables the game reads by name (all three hold ``Item_ZeldaLetter``, no other RSDB
  table does: a byte search of the dump): ``ActorInfo`` (model, heap sizes; ``ActorName`` is the text key),
  ``GameActorInfo``, and ``PouchActorInfo``, where the new row is the dungeon map's kind of content:
  ``PouchSpecialDeal: NotPushToPouch`` (the game's own way to give a content that is not put in the pouch: maps,
  compasses, boss keys, magic jars), category ``KeyItem``, the letter's ``Large`` get. Rows are inserted in name
  order, as every table keeps them.
- **Texts** ``<actor>_Name``, ``_Caption``, ``_GetMessage``, ``_GetCaption`` added to ``ActorMsg/PouchContent.msbt``
  of every language archive. The get window's default path shows ``_GetMessage`` then ``_GetCaption``
  (``GetPouchContent:DefaultGetMessage``); a new name takes that path (``EventQueryCheckUIMessageTargetActorName``
  branches only for named natives).
- **Flags** ``HavePlayedGetEvent.<actor>`` and ``IsGet.<actor>``, saved Bools the get flow may set for a content
  (every native item has both), added to the GameDataList.

One actor is the Nothing item (:data:`NOTHING`); each location holding another player's item gets its own
(:func:`foreign_actors`), since the get window's text is the actor's and names that player and item.

**Not yet seen in game:** that a romfs mod may add a pack the game did not ship, that the get window opens and the
chest stays open with a ``NotPushToPouch`` content of a new name, and the size-table entries of grown RSDB tables
(``rstb.OWN_FORMULA``). ``plans/03-game-data.md`` section 46 gives the check.
"""

import bisect
import copy
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from clawshot.census.hints import flow_path
from clawshot.formats import byml, evfl, msbt, sarc, zsdic
from clawshot.patch import get_text
from clawshot.patch.plan import PatchError
from clawshot.patch.text import POUCH_TEXT, archive_path, languages, text_key
from clawshot.patch.write import NewFile

DONOR = "Item_ZeldaLetter"
NOTHING = "Item_Clawshot_Nothing"
FOREIGN = "Item_Clawshot_AP_{index:03d}"
NOTHING_ITEM = "Nothing"
FOREIGN_ITEM = "Archipelago Item"
CUSTOM_ITEMS = (NOTHING_ITEM, FOREIGN_ITEM)

ACTOR_INFO = "RSDB/ActorInfo.Product.111.rstbl.byml.zs"
GAME_ACTOR_INFO = "RSDB/GameActorInfo.Product.111.rstbl.byml.zs"
POUCH_ACTOR_INFO = "RSDB/PouchActorInfo.Product.111.rstbl.byml.zs"
TABLES = (ACTOR_INFO, GAME_ACTOR_INFO, POUCH_ACTOR_INFO)
PACK = "Pack/Actor/{actor}.pack.zs"
PARAM = "Actor/{actor}.engine__actor__ActorParam.bgyml"
ACTOR_NAME_REF = "?ActorSystem/ActorName/{actor}.engine__actor__ActorName.bgyml"
TEXT_LABELS = ("_Name", "_Caption", "_GetMessage", "_GetCaption")
POUCH_ROW = {
    "BundleActorNum": byml.I32(1),
    "PouchCategory": "KeyItem",
    "PouchGetType": "Large",
    "PouchSpecialDeal": "NotPushToPouch",
    "PouchTabCategory": "KeyItem",
}


@dataclass(frozen=True)
class Foreign:
    """Another player's item at a location of this world, or with ``own``, an item of this world the multiworld
    gives later (a progressive item, whose tier depends on how many came before): its window says "your"."""

    player: str
    item: str
    own: bool = False


@dataclass(frozen=True)
class CustomItems:
    actors: Mapping[str, str]  # location -> actor
    changes: dict[str, Callable[[bytes], bytes]]
    new_files: dict[str, NewFile]
    flags: list[str]


def foreign_actors(foreign: Mapping[str, Foreign]) -> dict[str, str]:
    """One actor per location holding another player's item, numbered in location order."""
    if len(foreign) > 1000:
        raise PatchError(f"{len(foreign)} locations hold other players' items; at most 1000 are named")
    return {location: FOREIGN.format(index=i) for i, location in enumerate(sorted(foreign))}


def _rounded(n: int) -> int:
    return (n + 31) // 32 * 32


def build_pack(donor: bytes, actor: str, donor_actor: str = DONOR) -> NewFile:
    """The new actor's pack from the donor's (decompressed SARC bytes)."""
    files = sarc.read(donor)
    old = PARAM.format(actor=donor_actor)
    if old not in files:
        raise PatchError(f"{donor_actor}'s pack has no {old}")
    param = byml.load(files[old])
    components = param.root.get("Components")
    if not isinstance(components, dict) or "ActorNameRef" not in components:
        raise PatchError(f"{old}: no ActorNameRef component")
    components["ActorNameRef"] = ACTOR_NAME_REF.format(actor=actor)
    written = byml.dump(param)
    if (difference := byml.difference(param.root, byml.read(written))) is not None:
        raise PatchError(f"{actor}: ActorParam failed read-back: {difference}")
    new = PARAM.format(actor=actor)
    out = {(new if name == old else name): (written if name == old else data) for name, data in files.items()}
    data = sarc.write(out)
    if sarc.read(data) != out:
        raise PatchError(f"{actor}: pack failed read-back")
    return NewFile(data, {new: (old, max(0, _rounded(len(written)) - _rounded(len(files[old]))))})


def _row_for(table: str, donor: Mapping, actor: str) -> dict:
    if table == POUCH_ACTOR_INFO:
        return {**copy.deepcopy(POUCH_ROW), "__RowId": actor}
    row = copy.deepcopy(dict(donor))
    row["__RowId"] = actor
    if table == ACTOR_INFO:
        row["ActorName"] = actor
    return row


def add_rows(data: bytes, *, table: str, actors: Sequence[str], donor_actor: str = DONOR) -> bytes:
    """``table`` (decompressed) with a row for each new actor, copied from the donor's, in name order."""
    document = byml.load(data)
    rows = document.root
    if not isinstance(rows, list):
        raise PatchError(f"{table}: not a list of rows")
    ids = [str(row["__RowId"]) for row in rows]
    if ids != sorted(ids):
        raise PatchError(f"{table}: rows are no longer in name order")
    donor = next((row for row in rows if row["__RowId"] == donor_actor), None)
    if donor is None:
        raise PatchError(f"{table}: no {donor_actor} row")
    for actor in sorted(actors):
        at = bisect.bisect_left(ids, actor)
        if at < len(ids) and ids[at] == actor:
            raise PatchError(f"{table}: already has a row {actor}")
        ids.insert(at, actor)
        rows.insert(at, _row_for(table, donor, actor))
    written = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(written))) is not None:
        raise PatchError(f"{table}: failed read-back: {difference}")
    return written


def pouch_texts(
    language: str,
    pouch: msbt.Msbt,
    *,
    nothing: bool,
    foreign: Mapping[str, Foreign],
    actors: Mapping[str, str],
    own_keys: Iterable[str] = (),
) -> msbt.Msbt:
    """``pouch`` (one language's ``PouchContent.msbt``) with the new actors' texts and, for each key in
    ``own_keys``, its get line saying "your" where :func:`get_text.possessive` can."""
    messages = dict(pouch.messages)
    new: dict[str, list] = {}
    if nothing:
        new.update({NOTHING + label: parts for label, parts in get_text.nothing_texts(language).items()})
    for location, item in foreign.items():
        texts = (
            get_text.own_texts(language, item.item)
            if item.own
            else get_text.foreign_texts(language, item.player, item.item)
        )
        new.update({actors[location] + label: parts for label, parts in texts.items()})
    taken = sorted(set(new) & set(messages))
    if taken:
        raise PatchError(f"{POUCH_TEXT}: labels already taken: {taken[:3]}")
    for key in sorted(set(own_keys)):
        name, line = messages.get(f"{key}_Name"), messages.get(f"{key}_GetMessage")
        if name is None or line is None:
            continue
        mine = get_text.possessive(language, name, line)
        if mine is not None:
            messages[f"{key}_GetMessage"] = mine
    messages.update({label: msbt.normalized(parts) for label, parts in sorted(new.items())})
    return msbt.Msbt(messages, pouch.buckets)


def text_transform(language: str, **kwargs) -> Callable[[bytes], bytes]:
    def transform(data: bytes) -> bytes:
        files = sarc.read(data)
        if POUCH_TEXT not in files:
            raise PatchError(f"no message file {POUCH_TEXT} in the {language} archive")
        document = pouch_texts(language, msbt.read(files[POUCH_TEXT]), **kwargs)
        written = msbt.write(document)
        if msbt.read(written) != document:
            raise PatchError(f"{language} {POUCH_TEXT}: failed read-back")
        files[POUCH_TEXT] = written
        out = sarc.write(files)
        if sarc.read(out) != files:
            raise PatchError(f"{language}: the written archive does not read back")
        return out

    return transform


GET_FLOW = "GetPouchContent"
GET_MESSAGE = "EventFlowMsg/Dm_SY_Get:GetMessage"
GET_CAPTION = "EventFlowMsg/Dm_SY_Get:GetCaption"


def single_box(flowchart: evfl.Flowchart) -> None:
    """The default get window in one box: ``DefaultGetMessage`` shows ``Dm_SY_Get:GetMessage`` and then
    ``GetCaption`` (two talk steps); the first now ends the window. Items with a window of their own (Pieces of Heart,
    tokens, bottles) keep theirs. Edits ``flowchart`` in place."""
    entry = flowchart.entry_point("DefaultGetMessage")
    first = flowchart.events[entry.main_event]
    second = flowchart.events[first.next] if isinstance(first, evfl.ActionEvent) and first.next != evfl.NONE else None
    message = (first.params or {}).get("MessageId")
    caption = (second.params or {}).get("MessageId") if isinstance(second, evfl.ActionEvent) else None
    if (message, caption) != (GET_MESSAGE, GET_CAPTION):
        raise PatchError(f"{GET_FLOW}: DefaultGetMessage is no longer GetMessage then GetCaption: {message}, {caption}")
    first.next = second.next


def single_box_transform(data: bytes) -> bytes:
    document = evfl.read(data)
    if document.flowchart is None:
        raise PatchError(f"{GET_FLOW}: no flowchart")
    single_box(document.flowchart)
    written = evfl.write(document)
    if evfl.read(written) != document:
        raise PatchError(f"{GET_FLOW}: the written flow does not read back")
    return written


def own_text_keys(romfs: str | Path, actors: Iterable[str]) -> list[str]:
    """The text keys of native actors (their ``ActorNameRef``; ``clawshot.patch.text.text_key``)."""
    romfs = Path(romfs)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    keys = set()
    for actor in sorted(set(actors)):
        path = PACK.format(actor=actor)
        if (romfs / path).is_file():
            keys.add(text_key(sarc.read(dicts.decompress(path, (romfs / path).read_bytes())), actor))
    return sorted(keys)


def changes(
    romfs: str | Path,
    *,
    nothing_locations: Iterable[str] = (),
    foreign: Mapping[str, Foreign] | None = None,
    own_actors: Iterable[str] = (),
) -> CustomItems:
    """Everything a seed's custom items need. ``own_actors``: native actors of the player's own items whose get line
    says "your" (an Archipelago slot); empty for a solo seed."""
    romfs = Path(romfs)
    foreign = dict(foreign or {})
    nothing_locations = sorted(set(nothing_locations))
    actors = foreign_actors(foreign)
    location_actors = {**{location: NOTHING for location in nothing_locations}, **actors}
    new_actors = sorted(set(location_actors.values()))
    own_keys = own_text_keys(romfs, own_actors)
    if not new_actors and not own_keys:
        return CustomItems({}, {}, {}, [])
    out: dict[str, Callable[[bytes], bytes]] = {}
    new_files: dict[str, NewFile] = {}
    if new_actors:
        dicts = zsdic.Dictionaries.from_romfs(romfs)
        donor_path = PACK.format(actor=DONOR)
        donor = dicts.decompress(donor_path, (romfs / donor_path).read_bytes())
        for actor in new_actors:
            path = PACK.format(actor=actor)
            if (romfs / path).exists():
                raise PatchError(f"{path} is in the dump already")
            new_files[path] = build_pack(donor, actor)
        for table in TABLES:
            out[table] = _rows_transform(table, tuple(new_actors))
    text = {"nothing": bool(nothing_locations), "foreign": foreign, "actors": actors, "own_keys": own_keys}
    # The get lines are rewritten: each says it all in one box (mysterypaint, 2026-11-12).
    out[flow_path(romfs, GET_FLOW)] = single_box_transform
    for language in languages(romfs):
        out[archive_path(language)] = text_transform(language, **text)
    flags = [f"{kind}.{actor}" for actor in new_actors for kind in ("HavePlayedGetEvent", "IsGet")]
    return CustomItems(location_actors, out, new_files, flags)


def _rows_transform(table: str, actors: tuple[str, ...]) -> Callable[[bytes], bytes]:
    def transform(data: bytes) -> bytes:
        return add_rows(data, table=table, actors=actors)

    return transform
