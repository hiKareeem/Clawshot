"""Read-only NUP and NX input and a disposable, generator-only RomFS working set."""

import argparse
import hashlib
import struct
import sys
import tomllib
from contextlib import ExitStack, contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import zstandard

from clawshot.pack import VERSION_FILES, PackError, is_os_metadata
from clawshot.pack._nup import format as F
from clawshot.pack._nup.read import NupReader
from clawshot.pack._nx import read as nx

# A game's update has its own title ID: the base's plus 0x800. Both share the application ID (the upper bits).
APPLICATION_ID_MASK = ~0xFFF


class NupRomfs:
    """Use the newest full base/update RomFS; never mix packages or fall back to an old build."""

    def __init__(self, path: Path):
        self.reader = NupReader(str(path))
        try:
            packages = [p for p in self.reader.packages if p.kind in (F.KIND_BASE, F.KIND_UPDATE)]
            if not packages or len({p.title_id & APPLICATION_ID_MASK for p in packages}) != 1:
                raise PackError("NUP must contain one game's base/update packages")
            newest = max(p.version for p in packages)
            packages = [p for p in packages if p.version == newest]
            if len(packages) != 1 or packages[0].romfs_dir == F.NO_DIR:
                raise PackError("NUP newest package must have one complete RomFS")
            self.package = packages[0]
            self.files = {}
            visited = set()
            stack = [(self.package.romfs_dir, "")]
            while stack:
                index, prefix = stack.pop()
                if index in visited:
                    raise PackError("NUP RomFS directory cycle or shared directory")
                visited.add(index)
                _, first, count = self.reader.dirs[index]
                names = set()
                for child in self.reader.children[first : first + count]:
                    is_dir = child < self.reader.dir_count
                    table = self.reader.dirs if is_dir else self.reader.files
                    entry = child if is_dir else child - self.reader.dir_count
                    if entry >= len(table):
                        raise PackError(f"NUP child index out of bounds: {child}")
                    name = table[entry][0].decode("utf-8")
                    if (
                        not name
                        or name in (".", "..")
                        or any(c in name for c in '/\\:<>"|?*\0')
                        or name.endswith((".", " "))
                        or name.casefold() in names
                    ):
                        raise PackError(f"unsafe or duplicate NUP member: {prefix}{name!r}")
                    names.add(name.casefold())
                    relative = prefix + name
                    if is_dir:
                        stack.append((entry, relative + "/"))
                    else:
                        self.files[relative] = entry
        except BaseException:
            self.reader.close()
            raise

    def has(self, relative: str) -> bool:
        return relative in self.files

    def close(self):
        self.reader.close()

    def read(self, relative: str) -> bytes:
        if relative not in self.files:
            raise PackError(f"NUP newest package is missing romfs/{relative}; a complete supported dump is required")
        index = self.files[relative]
        data = self.reader.read_file(index)
        expected = self.reader.file_info(index)[2]
        if hashlib.sha256(data).digest() != expected:
            raise PackError(f"NUP SHA256 mismatch: romfs/{relative}")
        return data


class NxRomfs:
    """The newest base/update snapshot of an NX archive (fab918/nxformat). Each NX snapshot is a complete tree
    (``exefs/``, ``romfs/``, optional ``data/``; SPEC.md section 8), so the update snapshot is read on its own, never
    laid over the base. Only archives converted from a NUP or an extracted dump hold a ``romfs/`` tree: one packed
    from a decrypted NSP stores native NCAs, which Clawshot does not read."""

    def __init__(self, path: Path):
        self.archive = nx.NxArchive(path)
        try:
            games = [
                s
                for s in self.archive.snapshots
                if s.snapshot_type in (nx.SNAPSHOT_BASE, nx.SNAPSHOT_UPDATE, nx.SNAPSHOT_STANDALONE_UPDATE)
            ]
            if not games or len({s.application_id & APPLICATION_ID_MASK for s in games}) != 1:
                raise PackError("NX archive must contain one game's base/update snapshots")
            newest = max(s.version for s in games)
            games = [s for s in games if s.version == newest]
            if len(games) != 1:
                raise PackError("NX archive has more than one snapshot of its newest version")
            self.snapshot = games[0]
            tree = self.archive.tree(self.snapshot)
            self.files = {path[len("romfs/") :]: record for path, record in tree.items() if path.startswith("romfs/")}
            if not self.files:
                raise PackError(
                    "NX snapshot has no romfs/ tree (packed from a decrypted NSP?); convert the game from its NUP "
                    "or an extracted dump folder, or choose those directly"
                )
        except BaseException:
            self.archive.close()
            raise

    def has(self, relative: str) -> bool:
        return relative in self.files

    def close(self):
        self.archive.close()

    def read(self, relative: str) -> bytes:
        if relative not in self.files:
            raise PackError(f"NX newest snapshot is missing romfs/{relative}; a complete supported dump is required")
        return self.archive.read(self.files[relative])


class FolderRomfs:
    """One extracted RomFS folder. Its file index is built only when asked: a full dump holds ~190,000 files and
    listing them takes seconds, while the version check reads four."""

    def __init__(self, root: Path):
        self.root = root
        self._files = None

    @property
    def files(self) -> dict[str, Path]:
        if self._files is None:
            self._files = {
                file.relative_to(self.root).as_posix(): file
                for file in self.root.rglob("*")
                if file.is_file() and not any(is_os_metadata(p) for p in file.relative_to(self.root).parts)
            }
        return self._files

    def has(self, relative: str) -> bool:
        return relative in self._files if self._files is not None else (self.root / relative).is_file()

    def close(self):
        pass

    def read(self, relative: str) -> bytes:
        if not self.has(relative):
            raise PackError(f"romfs folder is missing {relative}: {self.root}")
        return (self.root / relative).read_bytes()


class StackedRomfs:
    """Layers oldest first; a newer layer's file shadows an older one's by path, as a console applies an update
    (NUP SPEC.md, "Update layering"). An update may hold the full tree or only its changed files."""

    def __init__(self, sources):
        self.sources = list(sources)

    @property
    def files(self) -> dict:
        merged = {}
        for source in self.sources:  # oldest first, so the newest copy wins
            merged.update(dict.fromkeys(source.files, source))
        return merged

    def has(self, relative: str) -> bool:
        return any(source.has(relative) for source in self.sources)

    def close(self):
        for source in self.sources:
            source.close()

    def read(self, relative: str) -> bytes:
        for source in reversed(self.sources):
            if source.has(relative):
                return source.read(relative)
        raise PackError(f"game files are missing romfs/{relative}; base and update must both be complete")


class LayeredRomfs(StackedRomfs):
    """A dump folder in the layout NUP packs from: ``base/romfs`` and optionally ``updates/<version>/romfs``.

    Lists of removed paths that some unpackers write are not read: for build e0f3ccfa they name only superseded
    ``.Product.100.`` files, which Clawshot never reads, and ``check_version`` rejects any other build.
    """

    def __init__(self, path: Path):
        layers = dump_layers(path)
        if layers is None:
            raise PackError(f"not a dump folder (no base/romfs): {path}")
        self.layers = layers
        super().__init__(FolderRomfs(layer) for layer in layers)

    def read(self, relative: str) -> bytes:
        if not self.has(relative) and len(self.layers) == 1 and relative == VERSION_FILES[1]:
            # a base-only dump folder: say that the update is missing, as a plain romfs check would
            from clawshot.patch.write import PatchError, check_romfs

            try:
                check_romfs(self.layers[0])
            except PatchError as error:
                raise PackError(str(error)) from error
        return super().read(relative)


def dump_layers(path: Path) -> list[Path] | None:
    """``[base romfs, newest update romfs]`` (or only the base) for a dump folder, else None."""
    base = path / "base" / "romfs"
    if not base.is_dir():
        return None
    updates = path / "updates"
    versions = []
    if updates.is_dir():
        versions = [int(d.name) for d in updates.iterdir() if d.name.isdecimal() and (d / "romfs").is_dir()]
    if not versions:
        return [base]
    return [base, updates / str(max(versions)) / "romfs"]


@contextmanager
def _open_one(path: Path):
    if path.is_dir():
        yield LayeredRomfs(path) if dump_layers(path) is not None else FolderRomfs(path)
        return
    if path.suffix.lower() == ".nx":
        with open_nx(path) as source:
            yield source
        return
    with open_nup(path) as source:
        yield source


@contextmanager
def open_source(path: Path, update: Path | None = None):
    """A RomFS folder, a dump folder, a ``.nup`` or an ``.nx``, optionally with a separate update (a RomFS folder
    holding the update's files, or an update ``.nup`` or ``.nx``) laid over it, read through one
    ``files``/``has``/``read`` interface."""
    with ExitStack() as stack:
        base = stack.enter_context(_open_one(path))
        if update is None:
            yield base
            return
        yield StackedRomfs([base, stack.enter_context(_open_one(update))])


# GameDataList.Product.<n> names the game version; a dump keeps older lists beside newer ones.
GAME_VERSIONS = {110: "1.1.1", 100: "1.0.0"}


def game_version(source) -> str | None:
    """The official version the game files identify as (by file name only), or None if none is known."""
    for product, name in sorted(GAME_VERSIONS.items(), reverse=True):
        if source.has(f"GameData/GameDataList.Product.{product}.byml.zs"):
            return name
    return None


@contextmanager
def open_nup(path: Path):
    source = None
    try:
        source = NupRomfs(path)
        yield source
    except (F.NupError, struct.error, IndexError, UnicodeError, zstandard.ZstdError) as error:
        raise PackError(f"invalid NUP: {error}") from error
    finally:
        if source is not None:
            source.close()


@contextmanager
def open_nx(path: Path):
    source = None
    try:
        source = NxRomfs(path)
        yield source
    except (nx.NxError, struct.error, IndexError, UnicodeError, zstandard.ZstdError) as error:
        raise PackError(f"invalid NX archive: {error}") from error
    finally:
        if source is not None:
            source.close()


def fingerprint(read) -> str:
    hashes = "".join(hashlib.sha256(read(p)).hexdigest() + "\n" for p in VERSION_FILES)
    return hashlib.sha256(hashes.encode("ascii")).hexdigest()


def resource_spec() -> dict:
    return tomllib.loads(Path(__file__).with_name("resources.toml").read_text(encoding="utf-8"))


def working_files(source: "NupRomfs | NxRomfs | StackedRomfs | FolderRomfs", spec: dict) -> set[str]:
    """Resolve the one cache definition against the source's file index and the catalogues."""
    from fnmatch import fnmatchcase

    from clawshot.patch import items, shops

    actors = set(items.load().actors.values())
    slots = shops.load()
    actors.update(slot.owner for slot in slots)
    actors.update(slot.vanilla_item for slot in slots)
    wanted = set(spec["files"])
    wanted.update(spec["actor_pack"].format(actor=actor) for actor in actors)
    wanted.update(path for path in source.files if any(fnmatchcase(path, pattern) for pattern in spec["patterns"]))
    return wanted


@contextmanager
def local_romfs(path: Path, parent: Path | None, update: Path | None = None):
    """A RomFS folder as given; for a ``.nup`` or ``.nx``, a base+update dump folder or a separate ``update``, a
    disposable working set of the files the generator reads, under ``parent`` (the system temporary folder when None).
    Never write under the source; remove only this invocation's disposable cache."""
    if update is None and path.is_dir() and dump_layers(path) is None:
        yield path
        return
    from clawshot.formats import byml, zsdic
    from clawshot.pack import check_version
    from clawshot.patch import gamedata

    check_version(path, update)  # before creating even an empty cache
    with open_source(path, update) as source, TemporaryDirectory(prefix=".romfs-", dir=parent) as temporary:
        root = Path(temporary)
        spec = resource_spec()

        def fetch(relative):
            target = root / relative
            if not target.is_file():
                data = source.read(relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            return target

        for relative in sorted(working_files(source, spec)):
            fetch(relative)
        dictionaries = zsdic.Dictionaries.from_romfs(root)

        def tree(relative):
            raw = fetch(relative).read_bytes()
            return byml.read(dictionaries.decompress(relative, raw) if relative.endswith(".zs") else raw)

        if spec["fast_start_components"]:
            event_settings = tree(gamedata.EVENT_SETTING_TABLE)
            for setting in gamedata.load().values():
                for event in setting.skippable:
                    relative = gamedata.component_list_path(event_settings, event)
                    gamedata._skip_setting_in_parents(tree, relative)
        yield root


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a RomFS folder, NUP or NX before configuration/generation.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--expected", required=True)
    args = parser.parse_args(argv)
    from clawshot.pack import version_digest

    try:
        actual = version_digest(args.path)
        if actual != args.expected:
            raise PackError(f"dump fingerprint {actual}; expected {args.expected}; stop and report in help")
        print(f"Verified dump: {actual}")
        return 0
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
