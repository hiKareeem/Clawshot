"""Build the versioned UI source zip without opening game files or running generation."""

import argparse
import os
import tomllib
import zipfile
from pathlib import Path

from clawshot.pack import ROOT, source_files

EXTRA = (
    "Clawshot.bat",
    "Clawshot.command",
    "clawshot.sh",
    "scripts/start-windows.ps1",
    "docs/ui.md",
    "src/clawshot/ui/static/index.html",
    "src/clawshot/ui/static/app.js",
    "src/clawshot/ui/static/style.css",
)
READ_ME = (
    "Unzip the whole folder outside your game and Hookshot folders.\n"
    "Windows: double-click Clawshot.bat. Linux: run clawshot.sh. "
    "macOS (untested): first right-click Clawshot.command and choose Open (unsigned download).\n"
    "Choose your own supported romfs, .nup or .nx on Game; Hookshot is optional and only needed for Play.\n"
    "Generate with Recommended; Play uses separate Hookshot saves, or Copy to my emulator after backing up saves.\n"
    "Keep the terminal open. No game is included or downloaded; never share generated mods. See docs/ui.md.\n"
)


def build(out: Path, *, root: Path = ROOT) -> Path:
    root = root.resolve()
    release_version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    folder = f"Clawshot-{release_version}"
    destination = out.resolve() / (folder + ".zip")
    protected = os.environ.get("OOT_ROMFS")
    if protected and destination.is_relative_to(Path(protected).resolve()):
        raise ValueError("Choose a release folder outside your read-only game dump.")
    files = source_files(root)
    files.update({name: (root / name).read_bytes() for name in EXTRA})
    for name in files:
        path = root / name
        for part in (path, *path.parents):
            if part.is_symlink() or part.is_junction():
                raise ValueError(f"Release source must not traverse links: {part}")
            if part == root:
                break
    files["READ ME FIRST.txt"] = READ_ME.encode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    stream = destination.open("xb")  # Reservation must succeed before failure cleanup owns this path.
    try:
        with stream, zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(files.items()):
                entry = zipfile.ZipInfo(folder + "/" + name, date_time=(1980, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.create_system = 3
                entry.external_attr = (0o100755 if name in {"clawshot.sh", "Clawshot.command"} else 0o100644) << 16
                archive.writestr(entry, data)
    except BaseException:
        destination.unlink()
        raise
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("dist"), help="Release output directory (default: dist)")
    args = parser.parse_args()
    try:
        print(build(args.out))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Release not built: {error}\n")


if __name__ == "__main__":
    main()
