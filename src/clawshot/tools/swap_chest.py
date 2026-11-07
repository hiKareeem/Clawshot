"""Change what one chest holds, as a mod folder.

    python -m clawshot.tools.swap_chest --romfs <dir> --out <dir> --file <Banc path> --hash <actor Hash>
        --item <actor name>

Reads ``<romfs>/<file>`` (a placement file, ``Banc/**/*.bcett.byml.zs``), sets ``Dynamic.Drop__DropActor`` of the
actor whose ``Hash`` is given, and writes the file to ``<out>/romfs/<file>``, compressed with the same dictionary.
Nothing under ``<romfs>`` is written.
"""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from clawshot.formats import byml, zsdic

DROP_KEY = "Drop__DropActor"


class SwapError(Exception):
    pass


@dataclass(frozen=True)
class SwapResult:
    output: Path
    gyaml: str
    old_item: str
    new_item: str
    original_size: int
    original_compressed_size: int
    new_size: int
    new_compressed_size: int


def _find_actor(tree, actor_hash: int, file: str) -> dict:
    actors = tree.get("Actors") if isinstance(tree, dict) else None
    if not isinstance(actors, list):
        raise SwapError(f"{file} has no Actors list")
    found = [a for a in actors if isinstance(a, dict) and a.get("Hash") == actor_hash]
    if len(found) != 1:
        raise SwapError(f"{file}: {len(found)} actors have Hash {actor_hash}, expected one")
    return found[0]


def swap_chest(romfs: Path, out: Path, file: str, actor_hash: int, item: str) -> SwapResult:
    rel = PurePosixPath(file.replace("\\", "/"))
    if rel.is_absolute() or ".." in rel.parts or not rel.name.endswith(".bcett.byml.zs"):
        raise SwapError(f"--file must be a romfs-relative placement file (Banc/**/*.bcett.byml.zs), not {file}")
    romfs = romfs.resolve()
    out = out.resolve()
    if out == romfs or out.is_relative_to(romfs):
        raise SwapError(f"the output folder {out} is inside the romfs {romfs}; the dump is read-only")
    if not (romfs / "Pack" / "Actor" / f"{item}.pack.zs").is_file():
        raise SwapError(f"no actor called {item!r}: Pack/Actor/{item}.pack.zs is not in the romfs")

    dicts = zsdic.Dictionaries.from_romfs(romfs)
    compressed = (romfs / rel).read_bytes()
    data = dicts.decompress(rel.as_posix(), compressed)
    tree = byml.read(data)
    actor = _find_actor(tree, actor_hash, rel.as_posix())
    dynamic = actor.get("Dynamic")
    if not isinstance(dynamic, dict) or not isinstance(dynamic.get(DROP_KEY), str):
        raise SwapError(f"actor {actor_hash} ({actor.get('Gyaml')}) has no Dynamic.{DROP_KEY} to change")
    old_item = dynamic[DROP_KEY]
    dynamic[DROP_KEY] = item

    new_data = byml.write(tree)
    if (d := byml.difference(tree, byml.read(new_data))) is not None:
        raise SwapError(f"the written file does not read back as the changed tree: {d}")
    new_compressed = dicts.compress(rel.as_posix(), new_data)
    if dicts.decompress(rel.as_posix(), new_compressed) != new_data:
        raise SwapError("the compressed file does not decompress to the written bytes")

    target = out / "romfs" / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(new_compressed)
    return SwapResult(
        output=target,
        gyaml=actor.get("Gyaml", "?"),
        old_item=old_item,
        new_item=item,
        original_size=len(data),
        original_compressed_size=len(compressed),
        new_size=len(new_data),
        new_compressed_size=len(new_compressed),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m clawshot.tools.swap_chest", description=__doc__.split("\n")[0])
    parser.add_argument("--romfs", required=True, type=Path, help="the game's romfs folder (read only)")
    parser.add_argument("--out", required=True, type=Path, help="mod folder to write; the file goes under romfs/")
    parser.add_argument("--file", required=True, help="romfs-relative placement file, e.g. Banc/Area/X.bcett.byml.zs")
    parser.add_argument("--hash", required=True, type=int, help="the chest actor's Hash (decimal)")
    parser.add_argument("--item", required=True, help="actor name to put in the chest, e.g. TBox_Rupee_Red")
    args = parser.parse_args(argv)
    try:
        r = swap_chest(args.romfs, args.out, args.file, args.hash, args.item)
    except (SwapError, zsdic.ZsError, byml.BymlError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"{r.gyaml} {args.hash}: {r.old_item} -> {r.new_item}")
    print(f"decompressed {r.original_size} -> {r.new_size} bytes")
    print(f"compressed {r.original_compressed_size} -> {r.new_compressed_size} bytes")
    print(f"wrote {r.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
