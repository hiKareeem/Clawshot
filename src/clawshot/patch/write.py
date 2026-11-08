"""Write a patch plan as a mod folder: ``<out>/romfs/<romfs path>`` for each changed placement file, and the
resource size table when a changed file needs a bigger entry, through ``clawshot.formats``. Nothing under the
romfs is written."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from clawshot.census.scan import DEFAULT_CHEST_DROP
from clawshot.formats import byml, rstb, zsdic
from clawshot.patch.plan import DROP_KEY, EVENT_KEY, SUBSTITUTE_KEY, PatchError, Plan

if TYPE_CHECKING:
    from clawshot.patch.gamedata import BuiltFile

FileChanges = Mapping[str, Callable[[bytes], bytes]]
"""Romfs-relative paths to transforms of decompressed file bytes. Transforms must validate their read-back."""


@dataclass(frozen=True)
class WrittenFile:
    path: str  # romfs-relative
    size: int  # decompressed, before
    new_size: int  # decompressed, after
    compressed_size: int
    new_compressed_size: int
    entry: int | None = None  # its resource-size-table entry, before (None for the table itself)
    new_entry: int | None = None  # and after


def check_output_folder(romfs: Path, out: Path) -> None:
    """The output folder must be outside the romfs and must not hold a seed already (a stale file would mix two
    seeds)."""
    romfs, out = romfs.resolve(), out.resolve()
    if out == romfs or out.is_relative_to(romfs) or romfs.is_relative_to(out):
        raise PatchError(f"the output folder {out} overlaps the romfs {romfs}; the dump is read-only")
    if out.exists() and any(out.iterdir()):
        raise PatchError(f"the output folder {out} is not empty")


def patch_tree(tree: dict, path: str, plan: Plan) -> None:
    """Apply the plan's changes for the placement file ``path`` to its parsed tree, in place."""
    changes = plan.for_file(path)
    actors = tree.get("Actors") if isinstance(tree, dict) else None
    if not isinstance(actors, list):
        raise PatchError(f"{path} has no Actors list")
    for change in changes:
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


def _patch_path(path: str) -> PurePosixPath:
    relative = PurePosixPath(path)
    if relative.is_absolute() or ".." in relative.parts or "\\" in path or ":" in path or path == rstb.TABLE_PATH:
        raise PatchError(f"invalid patch path {path!r}")
    return relative


def write(
    plan: Plan,
    romfs: str | Path,
    out: str | Path,
    *,
    extra_changes: Sequence[FileChanges] = (),
    fast_start_files: Sequence["BuiltFile"] = (),
) -> list[WrittenFile]:
    """Write every file the plan changes to ``<out>/romfs/``, compressed with the dictionary its name calls for.

    Each changed file's resource-size-table entry is raised to ``rstb.required_size`` when it is short (never
    lowered); the table is written only when an entry changed. Every file is built and read back first; nothing is
    written if one fails."""
    romfs, out = Path(romfs), Path(out)
    check_output_folder(romfs, out)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    table_compressed = (romfs / rstb.TABLE_PATH).read_bytes()
    table_data = dicts.decompress(rstb.TABLE_PATH, table_compressed)
    table = rstb.read(table_data)
    built: list[tuple[WrittenFile, bytes]] = []
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
    occupied = set(paths)
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
        # gamedata.build validates the exact tree edits. Initial-value edits keep the layout; removing the
        # intro's SkipSetting only shrinks its tree. Neither needs an unverified generic .bgyml size formula.
        if file.new_size > file.size or file.new_size > file.entry:
            raise PatchError(f"{file.path}: fast-start file must fit without growing its original allocation")
        info = WrittenFile(
            file.path, file.size, file.new_size, len(compressed), len(file.content), file.entry, file.entry
        )
        built.append((info, file.content))
    if any(info.entry != info.new_entry for info, _ in built):
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
