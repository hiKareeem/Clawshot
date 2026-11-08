import pytest

from clawshot.formats import msbt, sarc, zsdic


@pytest.mark.dump
def test_dump_every_message_file_round_trips(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    archives = sorted(romfs.glob("Mals/*.sarc.zs"))
    assert archives
    files = messages = 0
    for path in archives:
        data = dicts.decompress(path.name, path.read_bytes())
        contents = sarc.read(data)
        assert sarc.write(contents) == data, f"{path.name}: the archive does not write back byte-identical"
        for name, blob in contents.items():
            assert name.endswith(".msbt"), name
            parsed = msbt.read(blob)
            written = msbt.write(parsed)
            assert written == blob, f"{path.name}:{name}"
            files += 1
            messages += len(parsed.messages)
    print(f"{len(archives)} archives, {files} message files, {messages} messages: all byte-identical")
