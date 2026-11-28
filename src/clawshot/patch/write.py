"""Write a patch plan as a mod folder: ``<out>/romfs/<romfs path>`` for each changed placement file, each file the
game does not have (:class:`NewFile`), and the resource size table when a changed file needs a bigger entry or a new
resource needs one, through ``clawshot.formats``. Nothing under the romfs is written."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from clawshot.census.scan import DEFAULT_CHEST_DROP, GAME_DATA_LIST
from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.formats.rstb import RstbError
from clawshot.patch import placed_models
from clawshot.patch.getitem import member_growth as getitem_member_growth
from clawshot.patch.plan import DROP_KEY, EVENT_KEY, SUBSTITUTE_KEY, PatchError, Plan
from clawshot.patch.shops import member_growth
from clawshot.progressive import CHAINS

if TYPE_CHECKING:
    from clawshot.patch.gamedata import BuiltFile

FileChanges = Mapping[str, Callable[[bytes], bytes]]
"""Romfs-relative paths to transforms of decompressed file bytes. Transforms must validate their read-back."""


@dataclass(frozen=True)
class NewFile:
    """A new file's decompressed bytes and native sizing/copy provenance.

    ``members`` names renamed pack members and their native donor entry plus rounded growth (custom items).
    ``copied`` names byte-identical members and their donor pack (Skulltula pickups): a native pack, or a pack the
    same write changes, whose written member it must equal (song pickups hold the song's changed model); other
    pickup members get measured entries. Both producers share the same path-to-file mapping and size table."""

    data: bytes
    members: Mapping[str, tuple[str, int]] = field(default_factory=dict)
    copied: Mapping[str, str] = field(default_factory=dict)
    # A loose file with no size formula: (the native file whose entry it starts from, its growth) (event-items).
    sized_like: tuple[str, int] | None = None


NewFiles = Mapping[str, NewFile]


@dataclass(frozen=True)
class WrittenFile:
    path: str  # romfs-relative
    size: int  # decompressed, before (0 for a file new to the game)
    new_size: int  # decompressed, after
    compressed_size: int
    new_compressed_size: int
    entry: int | None = None  # its resource-size-table entry, before (None for the table itself or a new file)
    new_entry: int | None = None  # and after


def check_romfs(romfs: Path) -> None:
    """A plain error for a folder that is not the supported romfs (Version 1.1.1, update v131072), instead of a
    traceback from the first missing file. The base game's romfs alone keeps the update's files at version 100."""
    if not romfs.is_dir():
        raise PatchError(f"romfs folder not found: {romfs}")
    if (romfs / GAME_DATA_LIST).is_file():
        return
    base = (romfs / GAME_DATA_LIST.replace(".110.", ".100.")).is_file()
    hint = (
        "this looks like the base game (Version 1.0.0) on its own; give the dump folder that holds both base/ and "
        "updates/131072/, or a romfs with update v131072 (Version 1.1.1) laid over it"
        if base
        else "give the game's romfs folder at update v131072 (Version 1.1.1)"
    )
    raise PatchError(f"{romfs} has no {GAME_DATA_LIST}: {hint}")


def check_output_folder(romfs: Path, out: Path) -> None:
    """The output folder must be outside the romfs and must not hold a seed already (a stale file would mix two
    seeds)."""
    romfs, out = romfs.resolve(), out.resolve()
    if out == romfs or out.is_relative_to(romfs) or romfs.is_relative_to(out):
        raise PatchError(f"the output folder {out} overlaps the romfs {romfs}; the dump is read-only")
    if out.exists() and any(out.iterdir()):
        raise PatchError(f"the output folder {out} is not empty")


def patch_tree(tree: dict, path: str, plan: Plan) -> None:
    """Apply the plan's changes for the placement file ``path`` to its parsed tree, in place.

    A source-bound grant (``ChestChange.key_event``) is written last, after the removed native event, and only over
    the event state the plan classified, so a binding chosen for another source cannot land."""
    changes = plan.for_file(path)
    actors = tree.get("Actors") if isinstance(tree, dict) else None
    if not isinstance(actors, list):
        raise PatchError(f"{path} has no Actors list")
    for change in changes:
        if (
            change.named_key is not None or change.dungeon_item is not None or change.item in CHAINS
        ) and change.key_event is None:
            raise PatchError(f"{path}: actor {change.id} has a source-bound reward but no grant binding")
        found = [a for a in actors if isinstance(a, dict) and a.get("Hash") == change.id]
        if len(found) != 1:
            raise PatchError(f"{path}: {len(found)} actors have Hash {change.id}, expected one")
        actor = found[0]
        dynamic = actor.setdefault("Dynamic", {})
        # A chest without Drop__DropActor gives the chest default, which the census records as its item.
        current = dynamic.get(DROP_KEY, DEFAULT_CHEST_DROP)
        if actor.get("Gyaml") != change.chest or current != change.old_actor:
            raise PatchError(
                f"{path}: actor {change.id} is {actor.get('Gyaml')} holding {current!r}; the census said "
                f"{change.chest} holding {change.old_actor!r}"
            )
        dynamic[DROP_KEY] = change.new_actor
        # A_06's already-owned branch must not replace a shuffled progression item with vanilla ammo/rupees.
        if SUBSTITUTE_KEY in dynamic or "Drop__CheckActor" in dynamic:
            dynamic[SUBSTITUTE_KEY] = change.new_actor
        if change.event is not None:
            if dynamic.get(EVENT_KEY) != change.event.name:
                raise PatchError(
                    f"{path}: actor {change.id} has GetEventName {dynamic.get(EVENT_KEY)!r}, "
                    f"the census said {change.event.name!r}"
                )
            del dynamic[EVENT_KEY]
        if change.key_event is not None:
            source = change.kept_event.name if change.kept_event is not None else None
            if dynamic.get(EVENT_KEY) != source:
                raise PatchError(
                    f"{path}: actor {change.id} has GetEventName {dynamic.get(EVENT_KEY)!r}; its key binding "
                    f"{change.key_event!r} was chosen for {source!r}"
                )
            dynamic[EVENT_KEY] = change.key_event


def _patch_path(path: str) -> PurePosixPath:
    relative = PurePosixPath(path)
    if relative.is_absolute() or ".." in relative.parts or "\\" in path or ":" in path or path == rstb.TABLE_PATH:
        raise PatchError(f"invalid patch path {path!r}")
    return relative


def _absent(romfs: Path, table: rstb.ResourceSizeTable, path: str, what: str) -> None:
    """``path`` must be new to the game: no romfs file of that name and no size-table entry. An entry means an
    existing resource or another path with the same CRC32, whose allocation a new entry would silently replace."""
    resource = rstb.resource_path(path)
    for candidate in (resource, resource + ".zs"):
        if (romfs / PurePosixPath(candidate)).exists():
            raise PatchError(f"{what} {path}: the romfs already has {candidate}")
    if table.get(path) is not None:
        raise PatchError(
            f"{what} {path}: the size table already has entry {table.get(path)} for its CRC32 "
            f"0x{rstb.path_hash(path):08x} (an existing resource or a collision)"
        )


def _entry_for(path: str, data: bytes) -> int:
    """The measured size entry of a resource new to the game (an actor parameter counts its own components, an
    animation parameter its own AnimationResources entries)."""
    components = resources = None
    if path.endswith(rstb.ACTOR_PARAM):
        node = byml.read(data)
        own = node.get("Components", {}) if isinstance(node, dict) else None
        if not isinstance(own, dict):
            raise PatchError(f"{path}: an actor parameter file without a Components map")
        components = len(own)
    elif path.endswith(rstb.ANIMATION_PARAM):
        node = byml.read(data)
        listed = node.get("AnimationResources", []) if isinstance(node, dict) else None
        if not isinstance(listed, list):
            raise PatchError(f"{path}: an animation parameter file without an AnimationResources list")
        resources = len(listed)
    try:
        return rstb.required_size(path, len(data), components, resources=resources)
    except RstbError as error:
        raise PatchError(f"{path}: {error}") from error


def _new_file(
    path: str,
    file: NewFile,
    romfs: Path,
    dicts: zsdic.Dictionaries,
    table: rstb.ResourceSizeTable,
    native_packs: dict[str, dict[str, bytes]],
    new_members: dict[str, bytes],
    written_packs: Mapping[str, dict[str, bytes]] | None = None,
) -> tuple[WrittenFile, bytes]:
    """Build one new file, retaining native/custom sizing and validating pickup copy provenance."""
    _patch_path(path)
    _absent(romfs, table, path, "new file")
    if path.endswith(".pack.zs"):
        members = sarc.read(file.data)
        if sarc.write(members) != file.data:
            raise PatchError(f"{path}: the new pack does not read back to the same bytes")
        if stray := sorted((set(file.copied) | set(file.members)) - set(members)):
            raise PatchError(f"{path}: declared members {stray} are not in the pack")
        for name in sorted(members):
            content, source = members[name], file.copied.get(name)
            if name in file.members:
                donor, growth = file.members[name]
                entry = table.get(donor)
                if entry is None:
                    raise PatchError(f"{name}: its donor {donor} has no resource size table entry")
                _absent(romfs, table, name, f"{path}: new member")
                table.set(name, entry + growth)
                new_members[name] = content
            elif source is not None and source in (written_packs or {}):
                # A pack this write changes: the copy is its written member, sized with that pack.
                if written_packs[source].get(name) != content:
                    raise PatchError(f"{path}: member {name} is not byte-identical to its copy in {source} as written")
                if table.get(name) is None:
                    raise PatchError(f"{path}: copied member {name} has no size entry")
            elif source is not None:
                if source not in native_packs:
                    source_path = _patch_path(source)
                    if not (source.startswith("Pack/") and source.endswith(".pack.zs")):
                        raise PatchError(f"{path}: {name} names {source!r}, not a native pack")
                    if not (romfs / source_path).is_file():
                        raise PatchError(f"{path}: {name} is copied from {source}, which the romfs lacks")
                    native_packs[source] = sarc.read(dicts.decompress(source, (romfs / source_path).read_bytes()))
                if native_packs[source].get(name) != content:
                    raise PatchError(f"{path}: member {name} is not byte-identical to its copy in {source}")
                if table.get(name) is None:
                    raise PatchError(f"{path}: copied member {name} has no native size entry")
            elif file.members:
                # Custom-item packs retain the donor's other members under their original native paths.
                continue
            elif name in new_members:
                if new_members[name] != content:
                    raise PatchError(f"{path}: new member {name} differs from another new file's")
            else:
                _patch_path(name)
                _absent(romfs, table, name, f"{path}: new member")
                table.set(name, _entry_for(name, content))
                new_members[name] = content
    elif file.copied or file.members:
        raise PatchError(f"{path}: only a pack has members to copy")
    if file.sized_like is not None:
        donor, growth = file.sized_like
        if (donor_entry := table.get(donor)) is None:
            raise PatchError(f"{path}: its size donor {donor} has no resource size table entry")
        entry = donor_entry + growth
    else:
        entry = _entry_for(path, file.data)
    table.set(path, entry)
    compressed = dicts.compress(path, file.data) if path.endswith(".zs") else file.data
    if path.endswith(".zs") and dicts.decompress(path, compressed) != file.data:
        raise PatchError(f"{path}: the compressed file does not decompress to the written bytes")
    return WrittenFile(path, 0, len(file.data), 0, len(compressed), None, entry), compressed


def write(
    plan: Plan,
    romfs: str | Path,
    out: str | Path,
    *,
    extra_changes: Sequence[FileChanges] = (),
    fast_start_files: Sequence["BuiltFile"] = (),
    new_files: NewFiles | None = None,
) -> list[WrittenFile]:
    """Write every file the plan changes to ``<out>/romfs/``, compressed with the dictionary its name calls for.

    Each changed file's resource-size-table entry is raised to ``rstb.required_size`` when it is short (never
    lowered); the table is written only when an entry changed. ``new_files`` are files the dump does not hold: each
    gets a new entry (``rstb.required_size``), and each member it lists the entry of the member it copies plus its
    growth. Every file is built and read back first; nothing is written if one fails."""
    new_files = dict(new_files or {})
    romfs, out = Path(romfs), Path(out)
    check_output_folder(romfs, out)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    table_compressed = (romfs / rstb.TABLE_PATH).read_bytes()
    table_data = dicts.decompress(rstb.TABLE_PATH, table_compressed)
    table = rstb.read(table_data)
    built: list[tuple[WrittenFile, bytes]] = []
    member_entries: dict[str, int] = {}
    written_packs: dict[str, dict[str, bytes]] = {}
    members_grew = False
    paths = sorted(set(plan.files()).union(*(changes.keys() for changes in extra_changes)))
    for path in paths:
        relative = _patch_path(path)
        compressed = (romfs / relative).read_bytes()
        data = dicts.decompress(path, compressed) if path.endswith(".zs") else compressed
        new_data = data
        if plan.for_file(path):
            document = byml.load(new_data)
            patch_tree(document.root, path, plan)
            new_data = byml.dump(document)
            if (d := byml.difference(document.root, byml.read(new_data))) is not None:
                raise PatchError(f"{path}: the written file does not read back as the changed tree: {d}")
        for changes in extra_changes:
            if transform := changes.get(path):
                new_data = transform(new_data)
        if path.startswith("Pack/Actor/") and path.endswith(".pack.zs"):
            growths = member_growth(data, new_data) | getitem_member_growth(data, new_data)
            donor_sized = placed_models.added_member_sizes(data, new_data)  # no formula: a native entry + growth
            old_members, packed_members = sarc.read(data), sarc.read(new_data)
            written_packs[path] = packed_members
            for member, content in packed_members.items():
                if member not in old_members and table.get(member) is None:
                    _absent(romfs, table, member, f"{path}: added pack member")
                    if member in donor_sized:
                        donor, growth = donor_sized[member]
                        if (entry := table.get(donor)) is None:
                            raise PatchError(f"{member}: its donor {donor} has no resource size table entry")
                        table.set(member, entry + growth)
                    else:
                        table.set(member, _entry_for(member, content))
                    members_grew = True
                elif member.endswith(rstb.ACTOR_PARAM) and old_members.get(member) != content:
                    required = _entry_for(member, content)
                    entry = table.get(member)
                    if entry is None:
                        raise PatchError(f"{member}: the native actor parameter has no size entry")
                    if required > entry:
                        table.set(member, required)
                        members_grew = True
            for member, growth in growths.items():
                if member not in member_entries:
                    entry = table.get(member)
                    if entry is None:
                        raise PatchError(f"{member}: the resource size table has no entry for it")
                    member_entries[member] = entry
                required = member_entries[member] + growth
                if required > table.get(member):
                    table.set(member, required)
                    members_grew = True
        new_compressed = dicts.compress(path, new_data) if path.endswith(".zs") else new_data
        if path.endswith(".zs") and dicts.decompress(path, new_compressed) != new_data:
            raise PatchError(f"{path}: the compressed file does not decompress to the written bytes")
        entry = table.get(path)
        if entry is None:
            raise PatchError(f"{path}: the resource size table has no entry for it")
        new_entry = max(entry, rstb.required_size(path, len(new_data)))
        table.set(path, new_entry)
        info = WrittenFile(path, len(data), len(new_data), len(compressed), len(new_compressed), entry, new_entry)
        built.append((info, new_compressed))
    native_packs: dict[str, dict[str, bytes]] = {}
    new_members: dict[str, bytes] = {}
    for path, file in sorted(new_files.items()):
        if path in paths:
            raise PatchError(f"{path}: a new file must be one the dump does not hold")
        built.append(_new_file(path, file, romfs, dicts, table, native_packs, new_members, written_packs))
    occupied = set(paths) | set(new_files)
    for file in sorted(fast_start_files, key=lambda f: f.path):
        relative = _patch_path(file.path)
        if file.path in occupied:
            raise PatchError(f"{file.path}: fast start collides with another patch step")
        occupied.add(file.path)
        compressed = (romfs / relative).read_bytes()
        data = dicts.decompress(file.path, compressed) if file.path.endswith(".zs") else compressed
        new_data = dicts.decompress(file.path, file.content) if file.path.endswith(".zs") else file.content
        if (len(data), len(new_data), table.get(file.path)) != (file.size, file.new_size, file.entry):
            raise PatchError(f"{file.path}: fast-start build no longer matches its input or size entry")
        # The builder (door.build) validates its exact edit; a prebuilt file keeps its original allocation instead
        # of borrowing an unverified generic size formula for its type.
        if file.new_size > file.size or file.new_size > file.entry:
            raise PatchError(f"{file.path}: fast-start file must fit without growing its original allocation")
        info = WrittenFile(
            file.path, file.size, file.new_size, len(compressed), len(file.content), file.entry, file.entry
        )
        built.append((info, file.content))
    if members_grew or any(info.entry != info.new_entry for info, _ in built):
        new_table = rstb.write(table)
        new_table_compressed = dicts.compress(rstb.TABLE_PATH, new_table)
        if dicts.decompress(rstb.TABLE_PATH, new_table_compressed) != new_table:
            raise PatchError("the compressed size table does not decompress to the written bytes")
        info = WrittenFile(
            rstb.TABLE_PATH, len(table_data), len(new_table), len(table_compressed), len(new_table_compressed)
        )
        built.append((info, new_table_compressed))
    for info, content in built:
        target = out / "romfs" / PurePosixPath(info.path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return [info for info, _ in built]
