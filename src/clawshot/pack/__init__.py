"""Public test, game-free source packs with a reproducible local seed build."""

import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

BUILD = "e0f3ccfa"
VERSION_FILES = (
    "Pack/ZsDic.pack.zs",
    "GameData/GameDataList.Product.110.byml.zs",
    "RSDB/EventSetting.Product.111.rstbl.byml.zs",
    "Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs",
)
# SHA256 of the four lowercase SHA256 hex strings, each followed by LF. No game bytes.
ROMFS_SHA256 = "fc09c4af707a0ca092188cf014f6fdf3d40514def773f097b798f52f9f28bc93"
ROOT = Path(__file__).resolve().parents[3]
ASSETS = Path(__file__).with_name("templates")


class PackError(ValueError):
    """A pack cannot be built or safely used."""


def version_digest(romfs: Path, update: Path | None = None) -> str:
    from clawshot.pack.source import dump_layers, fingerprint, open_source

    if update is None and romfs.is_dir() and dump_layers(romfs) is None:
        return fingerprint(lambda relative: (romfs / relative).read_bytes())
    with open_source(romfs, update) as source:  # a .nup, an .nx, a base+update dump folder, or a separate update
        return fingerprint(source.read)


def check_version(romfs: Path, update: Path | None = None) -> None:
    actual = version_digest(romfs, update)
    if actual != ROMFS_SHA256:
        raise PackError(f"RomFS does not match build {BUILD}: fingerprint {actual}, expected {ROMFS_SHA256}")


MACOS_METADATA = {".DS_Store", ".AppleDouble", ".LSOverride", ".Spotlight-V100", ".Trashes", ".fseventsd", "__MACOSX"}


def is_os_metadata(name: str) -> bool:
    """Files macOS Finder writes into folders it opens (or zips): never game or seed content."""
    return name in MACOS_METADATA or name.startswith("._") or name == "Icon\r"


def ignore_os_metadata(_folder, names):
    """``shutil.copytree`` ignore callback."""
    return {name for name in names if is_os_metadata(name)}


def tree_digest(root: Path) -> str:
    """Hash sorted relative paths and file hashes, including spoiler/note; never filesystem metadata, including
    the .DS_Store Finder adds when a seed folder is opened."""
    if not root.is_dir():
        raise PackError(f"seed folder missing: {root}; run Make seed.bat first")
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        if any(is_os_metadata(part) for part in path.relative_to(root).parts):
            continue
        if path.is_symlink() or path.is_junction():
            raise PackError(f"seed contains a link: {path}")
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            with path.open("rb") as stream:
                digest.update(relative.encode("utf-8") + b"\0" + hashlib.file_digest(stream, "sha256").digest())
    return digest.hexdigest()


def source_files(root: Path = ROOT) -> dict[str, bytes]:
    """Positive allowlist: no plans, tests, outputs, Git metadata, caches or arbitrary root files."""
    names = ["pyproject.toml", "uv.lock", ".python-version", "README.md", "LICENSE", "NOTICE", "docs/seed-pack.md"]
    files = {name: (root / name).read_bytes() for name in names}
    for vendored in ("_nup", "_nx"):  # the upstream permission notices NOTICE points to
        licence = f"src/clawshot/pack/{vendored}/LICENSE.txt"
        files[licence] = (root / licence).read_bytes()
    for path in sorted((root / "src/clawshot").rglob("*")):
        if path.is_file() and path.suffix in {".py", ".toml", ".bat", ".ps1"} and "__pycache__" not in path.parts:
            if path.is_symlink():
                raise PackError(f"source contains a link: {path}")
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def generate(root: Path, romfs: Path, seed: int, settings: str, out: Path) -> None:
    from clawshot.pack.source import local_romfs

    with local_romfs(romfs, root) as extracted:
        _generate(root, extracted, seed, settings, out)


def _generate(root: Path, romfs: Path, seed: int, settings: str, out: Path) -> None:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)  # run the shipped source, not the publisher's checkout
    env.pop("VIRTUAL_ENV", None)
    subprocess.run(
        [
            "uv",
            "run",
            "--project",
            str(root),
            "--frozen",
            "--no-dev",
            "python",
            "-m",
            "clawshot",
            "--romfs",
            str(romfs),
            "--seed",
            str(seed),
            "--settings",
            settings,
            "--out",
            str(out),
        ],
        cwd=root,
        env=env,
        check=True,
    )


def build(romfs: Path, seed: int, settings: str, out: Path) -> dict:
    """Build a reference using the exact shipped source; retain only its digest in the zip."""
    check_version(romfs)  # no uv, generation, temporary files or output before version preflight
    from clawshot.generate import Settings

    settings = Settings.from_string(settings).to_string()
    out = out.resolve()
    if out.exists():
        raise PackError(f"refusing to replace existing pack: {out}")
    for protected in (romfs.resolve(), ROOT):
        if out.is_relative_to(protected) or protected.is_relative_to(out):
            raise PackError(f"pack output overlaps protected folder: {protected}")
    files = source_files()
    for name in ("Make seed.bat", "Play seed.bat", "setup.ps1", "READ ME FIRST.txt"):
        files[name] = (ASSETS / name).read_bytes()
    with tempfile.TemporaryDirectory(prefix="clawshot-pack-") as temporary:
        root = Path(temporary)
        for name, data in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        generate(root, romfs.resolve(), seed, settings, root / "seed")
        manifest = {
            "format": 1,
            "build": BUILD,
            "romfs_sha256": ROMFS_SHA256,
            "seed": seed,
            "settings": settings,
            "output_sha256": tree_digest(root / "seed"),
        }
    files["pack.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    with (
        out.open("xb") as stream,
        zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive,
    ):
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    return manifest
