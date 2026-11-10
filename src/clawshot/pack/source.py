"""Read-only NUP input and a disposable, generator-only RomFS working set."""

import argparse
import hashlib
import struct
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import zstandard

from clawshot.pack import VERSION_FILES, PackError
from clawshot.pack._nup import format as F
from clawshot.pack._nup.read import NupReader


class NupRomfs:
    """Use the newest full base/update RomFS; never mix packages or fall back to an old build."""

    def __init__(self, path: Path):
        self.reader = NupReader(str(path))
        try:
            packages = [p for p in self.reader.packages if p.kind in (F.KIND_BASE, F.KIND_UPDATE)]
            if not packages or len({p.title_id for p in packages}) != 1:
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


def fingerprint(read) -> str:
    hashes = "".join(hashlib.sha256(read(p)).hexdigest() + "\n" for p in VERSION_FILES)
    return hashlib.sha256(hashes.encode("ascii")).hexdigest()


def working_files(source: NupRomfs) -> set[str]:
    """Bounded generator inputs, not a dump extraction (no models, textures, audio or ExeFS)."""
    from fnmatch import fnmatchcase

    from clawshot.census.gifts import FLOW_VERSIONS
    from clawshot.census.scan import BANC_GLOB
    from clawshot.formats.rstb import TABLE_PATH
    from clawshot.patch import items, shops

    actors = set(items.load().actors.values())
    slots = shops.load()
    actors.update(slot.owner for slot in slots)
    actors.update(slot.vanilla_item for slot in slots)
    wanted = set(VERSION_FILES) | {FLOW_VERSIONS, TABLE_PATH, shops.POUCH_TABLE}
    wanted.update(f"Pack/Actor/{actor}.pack.zs" for actor in actors)
    for path in source.files:
        if (
            fnmatchcase(path, BANC_GLOB)
            or path.startswith("Event/EventFlow/")
            and path.endswith(".bfevfl.zs")
            or fnmatchcase(path, "Mals/*.Product.110.sarc.zs")
            or fnmatchcase(path, "Pack/Actor/Shop_Board_Bundle_*.pack.zs")
        ):
            wanted.add(path)
    return wanted


@contextmanager
def local_romfs(path: Path, parent: Path):
    """Never write under the source; remove only this invocation's disposable cache."""
    if path.is_dir():
        yield path
        return
    from clawshot.formats import byml, zsdic
    from clawshot.pack import check_version
    from clawshot.patch import gamedata

    check_version(path)  # before creating even an empty cache
    with open_nup(path) as source, TemporaryDirectory(prefix=".romfs-", dir=parent) as temporary:
        root = Path(temporary)

        def fetch(relative):
            target = root / relative
            if not target.is_file():
                data = source.read(relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            return target

        for relative in sorted(working_files(source)):
            fetch(relative)
        dictionaries = zsdic.Dictionaries.from_romfs(root)

        def tree(relative):
            raw = fetch(relative).read_bytes()
            return byml.read(dictionaries.decompress(relative, raw) if relative.endswith(".zs") else raw)

        event_settings = tree(gamedata.EVENT_SETTING_TABLE)
        for setting in gamedata.load().values():
            for event in setting.skippable:
                relative = gamedata.component_list_path(event_settings, event)
                gamedata._skip_setting_in_parents(tree, relative)
        yield root


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a RomFS folder or NUP before configuration/generation.")
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
