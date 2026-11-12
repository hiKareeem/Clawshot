"""Synthetic sequence graphs: ordered native pushes, no copied game fixtures."""

import hashlib
import struct

import pytest

from clawshot.formats import rstb, zsdic
from clawshot.patch import start_items
from clawshot.patch.plan import PatchError


def synthetic_sequence():
    pool = bytearray()
    names = {}

    def name(text):
        if text not in names:
            names[text] = len(pool)
            pool.extend(text.encode() + b"\0")
        return names[text]

    empty = name("")
    push_name = name(start_items.PUSH)
    int_names = [name("EndPolicy"), name("ResultPolicy")]
    every = name("ExecuteEveryFrame")
    num, actor = name("Num"), name("ActorName")
    wallet = name("Work/Actor/SyntheticWallet.engine__actor__ActorParam.gyml")
    untouched = name("SyntheticUnrelatedAction")
    out = bytearray(0x74 + 0x18 + 3 * 0x3C)
    out[:8] = b"AIB \x08\x04\x00\x00"

    def put(offset, *values):
        struct.pack_into("<" + "I" * len(values), out, offset, *values)

    put(0x0C, 1, 3, 1)
    put(0x74, name("SyntheticRoot"))
    put(0x88, 0)
    put(0x20, len(out))
    out.extend(bytes(56))
    for i, (kind, label) in enumerate(((3, empty), (0, push_name), (0, untouched))):
        header = 0x8C + i * 0x3C
        struct.pack_into("<HH", out, header, kind, i)
        put(header + 8, label)
        put(header + 0x14, len(out))
        body = len(out)
        out.extend(bytes(0xA4))
        if i == 0:
            put(body, 0, 2)
            out[body + 0x94] = 2
            for j in range(7, 20, 2):
                out[body + 0x90 + j] = 2
            out.extend(struct.pack("<6I", body + 0xAC, body + 0xB4, 1, empty, 2, empty))
        elif i == 1:
            put(body + 8, 0, 1)
            put(body + 0x30, 0, 1)
            put(body + 0x60, 0, 1)
    props = len(out)
    put(0x2C, props)
    out.extend(bytes(24))
    ip = len(out)
    out.extend(b"".join(struct.pack("<III", n, 0, 0) for n in int_names))
    bp = len(out)
    out.extend(struct.pack("<III", every, 0, 0))
    pe = len(out)
    put(props, ip, bp, pe, pe, pe, pe)
    inputs = len(out)
    put(0x34, inputs)
    out.extend(bytes(48))
    ii = len(out)
    out.extend(struct.pack("<IHHiI", num, 0xFFFF, 0, 0x01800000, 1))
    si = len(out)
    out.extend(struct.pack("<IHHiI", actor, 0xFFFF, 0, 0x00800000, wallet))
    end = len(out)
    put(inputs, ii, si, si, si, si, si, si, end, end, end, end, end)
    put(0x24, end)
    out.extend(pool)
    return bytes(out)


def decode(data):
    """Independent semantic reader for the fixture's literal, attachment-free nodes."""

    def u32(offset):
        return struct.unpack_from("<I", data, offset)[0]

    pool = u32(0x24)

    def text(offset):
        return data[pool + offset : data.index(b"\0", pool + offset)].decode()

    prop_tables = struct.unpack_from("<6I", data, u32(0x2C))
    io_tables = struct.unpack_from("<12I", data, u32(0x34))
    nodes = []
    for i in range(u32(0x10)):
        header = 0x74 + u32(0x0C) * 24 + i * 60
        body = u32(header + 20)
        props = {}
        for typ in range(2):
            start, count = struct.unpack_from("<II", data, body + typ * 8)
            for j in range(start, start + count):
                n, flags, value = struct.unpack_from("<III", data, prop_tables[typ] + j * 12)
                assert flags == 0
                props[text(n)] = value
        params = {}
        for typ, table in ((0, 0), (3, 6)):
            start, count = struct.unpack_from("<II", data, body + 48 + typ * 16)
            for j in range(start, start + count):
                p = io_tables[table] + j * 16
                n, source, output, flags, value = struct.unpack_from("<IHHIi", data, p)
                assert source == 0xFFFF and output == 0 and flags & 0x800000
                params[text(n)] = text(value) if typ == 3 else value
        children = []
        for j in range(data[body + 0x94]):
            link = u32(body + 164 + j * 4)
            children.append(u32(link))
        nodes.append(
            {
                "kind": struct.unpack_from("<H", data, header)[0],
                "name": text(u32(header + 8)),
                "props": props,
                "params": params,
                "children": children,
                "guid": data[header + 44 : header + 60],
            }
        )
    return nodes


def assert_branch(original, patched):
    before, after = decode(original), decode(patched)
    assert after[1 : len(before)] == before[1:]
    assert {k: v for k, v in after[0].items() if k != "children"} == {
        k: v for k, v in before[0].items() if k != "children"
    }
    assert after[0]["children"] == before[0]["children"] + [len(before)]
    branch, bag, nuts = after[-3:]
    assert branch["kind"] == 2  # native Sequential, not Simultaneous
    assert branch["children"] == [len(before) + 1, len(before) + 2]
    assert branch["props"] == {
        "BusyPolicy": 0,
        "NumLoop": 0,
        "PlayPolicy": 0,
        "ResultPolicy": 0,
        "IsDelayJudge": 0,
        "IsLoop": 0,
        "IsUpdateNextInFrame": 1,
    }
    assert [(n["name"], n["params"]) for n in (bag, nuts)] == [
        (start_items.PUSH, {"Num": 1, "ActorName": "Work/Actor/Item_NutBag_Small.engine__actor__ActorParam.gyml"}),
        (start_items.PUSH, {"Num": 0, "ActorName": "Work/Actor/Item_DekuNut.engine__actor__ActorParam.gyml"}),
    ]
    assert bag["props"] == nuts["props"] == {"ExecuteEveryFrame": 0}
    assert len({n["guid"] for n in after[-3:]}) == 3


def test_new_game_pushes_bag_before_zero_nuts_without_changing_original_setup():
    original = synthetic_sequence()
    patched = start_items._splice(original)
    assert_branch(original, patched)
    assert start_items._splice(original) == patched


def test_refuses_a_changed_or_already_patched_native_sequence():
    with pytest.raises(PatchError, match="fingerprint changed"):
        start_items.patch_sequence(synthetic_sequence())


@pytest.mark.dump
def test_native_new_game_keeps_original_setup_and_sizes_the_added_branch(romfs):
    original = (romfs / start_items.PATH).read_bytes()
    patched = start_items.patch_sequence(original)
    assert_branch(original, patched)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    assert table.get(start_items.PATH) == rstb.required_size(start_items.PATH, len(original))
    assert rstb.required_size(start_items.PATH, len(patched)) >= len(patched) + 376
    assert hashlib.sha256(original).hexdigest() == start_items.SHA256
