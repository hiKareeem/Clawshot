"""The game's zstd dictionaries and ``.zs`` files.

``Pack/ZsDic.pack.zs`` is a plain zstd frame around a SARC holding four dictionaries. Every ``.zs`` file is
compressed with the dictionary its name calls for, or with none (:func:`dictionary_for`); the frame header records
the dictionary's ID and :meth:`Dictionaries.decompress` checks that it matches.
"""

from pathlib import Path, PurePosixPath

import zstandard as zstd

from clawshot.formats import sarc

PACK_PATH = "Pack/ZsDic.pack.zs"

# File-name suffix -> dictionary (None: plain zstd), first match wins. Any other ``.zs`` file uses ``zs.zsdic``.
# Taken from the frame headers of every ``.zs`` file in the game (checked by a dump test).
_SUFFIX_DICTIONARY: tuple[tuple[str, str | None], ...] = (
    ("/ZsDic.pack.zs", None),
    (".bcett.byml.zs", "bcett.byml.zsdic"),
    (".pack.zs", "pack.zsdic"),
    (".bkprb.zs", "bkprb.zsdic"),
    (".rstbl.byml.zs", None),
    (".atbl.byml.zs", None),
    (".HeapDef.byml.zs", None),
    (".rsizetable.zs", None),
    (".bntx.zs", None),
    (".bcul.zs", None),
    (".bars.zs", None),
)
_DEFAULT_DICTIONARY = "zs.zsdic"
DICTIONARY_NAMES = ("zs.zsdic", "bcett.byml.zsdic", "pack.zsdic", "bkprb.zsdic")

# Large enough for any file in the game; bounds memory when a frame does not record its size.
MAX_OUTPUT = 1 << 30
DEFAULT_LEVEL = 19


class ZsError(ValueError):
    pass


def dictionary_for(name: str) -> str | None:
    """The dictionary a ``.zs`` file's name (a romfs path or a bare file name) calls for; None for plain zstd."""
    base = "/" + PurePosixPath(name.replace("\\", "/")).name
    if not base.endswith(".zs"):
        raise ZsError(f"not a .zs file: {name}")
    for suffix, dictionary in _SUFFIX_DICTIONARY:
        if base.endswith(suffix):
            return dictionary
    return _DEFAULT_DICTIONARY


def frame_dictionary_id(data: bytes) -> int:
    """The dictionary ID in a zstd frame header (0 when the frame names none)."""
    return zstd.get_frame_parameters(data).dict_id


class Dictionaries:
    """The four dictionaries from ``Pack/ZsDic.pack.zs``, and (de)compression of ``.zs`` files by name."""

    def __init__(self, files: dict[str, bytes]):
        missing = [n for n in DICTIONARY_NAMES if n not in files]
        if missing:
            raise ZsError(f"dictionary pack lacks {missing}; it holds {sorted(files)}")
        self._dicts = {name: zstd.ZstdCompressionDict(files[name]) for name in DICTIONARY_NAMES}

    @classmethod
    def from_pack(cls, pack: bytes) -> "Dictionaries":
        """Parse the bytes of ``ZsDic.pack.zs`` (compressed)."""
        return cls(sarc.read(zstd.ZstdDecompressor().decompress(pack, max_output_size=MAX_OUTPUT)))

    @classmethod
    def from_romfs(cls, romfs: str | Path) -> "Dictionaries":
        return cls.from_pack((Path(romfs) / PACK_PATH).read_bytes())

    def dictionary(self, name: str) -> zstd.ZstdCompressionDict:
        return self._dicts[name]

    def dictionary_id(self, name: str) -> int:
        return self._dicts[name].dict_id()

    def decompress(self, name: str, data: bytes) -> bytes:
        """Decompress the ``.zs`` file called ``name`` (a path or file name)."""
        dictionary = dictionary_for(name)
        expected = self._dicts[dictionary].dict_id() if dictionary else 0
        found = frame_dictionary_id(data)
        if found != expected:
            raise ZsError(f"{name}: frame names dictionary ID {found}, its name calls for {dictionary} ({expected})")
        if dictionary is None:
            return zstd.ZstdDecompressor().decompress(data, max_output_size=MAX_OUTPUT)
        return zstd.ZstdDecompressor(dict_data=self._dicts[dictionary]).decompress(data, max_output_size=MAX_OUTPUT)

    def compress(self, name: str, data: bytes, level: int = DEFAULT_LEVEL) -> bytes:
        """Compress ``data`` for the ``.zs`` file called ``name``, with the dictionary its name calls for.

        The frame records the content size and dictionary ID and carries no checksum, as the game's own files do.
        """
        dictionary = dictionary_for(name)
        params = {"level": level, "write_content_size": True, "write_checksum": False}
        if dictionary is None:
            return zstd.ZstdCompressor(**params).compress(data)
        return zstd.ZstdCompressor(dict_data=self._dicts[dictionary], write_dict_id=True, **params).compress(data)
