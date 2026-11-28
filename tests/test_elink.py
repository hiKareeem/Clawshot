"""ELink tables (XLNK version 36): decode, re-encode, add a user, set call parameters, make a play-all container.

Every file here is built in code (hard rule 1): a minimal XLNK 36 table with three users."""

import struct
import zlib

import pytest
from synthetic_effects import (
    ASSET_PARAMS,
    CONDITIONS,
    HEART_ACTION_USERS,
    HEART_ACTIONS,
    TRIGGERS,
    ActionTable,
    build_table,
)

from clawshot.formats import elink


def snapshot(table: elink.Elink, skip: str | None = None) -> dict:
    """Every user's calls with their decoded parameters (or container records)."""
    out = {}
    for name in table.user_names():
        if name == skip:
            continue
        calls = []
        for call in table.calls(name):
            entry = (call.key, call.asset, call.flag, call.duration, call.parent, call.guid, call.condition)
            detail = table.container(name, call.key) if call.is_container else table.call_params(name, call.key)
            calls.append((entry, detail))
        out[name] = (calls, table.trigger_table(name))
    return out


@pytest.fixture
def data() -> bytes:
    return build_table()


def test_decode_reads_users_calls_and_parameters(data):
    table = elink.decode(data)
    assert sorted(table.user_names()) == ["Obj_Donor", "Obj_Other", "Obj_Third"]
    assert table.asset_params == ASSET_PARAMS
    assert [c.key for c in table.calls("Obj_Donor")] == ["Wait", "Get"]
    assert table.call_params("Obj_Donor", "Wait") == {"AssetName": "Wait", "Bone": "Root", "BitFlag": 0x05000004}
    assert table.call_params("Obj_Donor", "Get")["Scale"] == 1.0  # direct value 1
    assert table.call_params("Obj_Donor", "Get")["RuntimeAssetName"] == "Fx_A"
    assert table.local_properties("Obj_Donor") == ["LocalProp"]
    assert table.trigger_table("Obj_Donor").rstrip(b"\0") == TRIGGERS  # the user's padding follows it
    assert table.direct_values() == pytest.approx([0.5, 1.0, -0.21, 1.0])
    assert table.conditions == CONDITIONS


def test_encode_is_byte_identical(data):
    assert elink.decode(data).encode() == data


def test_add_user_copy_inserts_in_hash_order(data):
    table = elink.decode(data)
    before = snapshot(table)
    table.add_user_copy("Obj_Donor", "Clawshot_New")
    out = table.encode()
    again = elink.decode(out)
    assert snapshot(again, skip="Clawshot_New") == before
    hashes = struct.unpack_from("<4I", out, 0x60)
    assert list(hashes) == sorted(hashes) and zlib.crc32(b"Clawshot_New") in hashes
    assert struct.unpack_from("<I", out, 0x48)[0] == 4
    assert struct.unpack_from("<I", out, 4)[0] == len(out) and len(out) % 8 == 0
    copied = snapshot(again)["Clawshot_New"]
    assert copied == before["Obj_Donor"]  # the bytes are self-relative: the copy decodes as its source
    assert again.user_data("Clawshot_New").rstrip(b"\0") == table.user_data("Obj_Donor").rstrip(b"\0")


def test_set_call_params_appends_values_records_and_names(data):
    table = elink.decode(data)
    before = snapshot(table)
    n_direct = len(table.direct_values())
    table.set_call_params("Obj_Donor", "Wait", {"RuntimeAssetName": "Fx_New", "Scale": 0.3, "Bone": "Root"})
    again = elink.decode(table.encode())
    params = again.call_params("Obj_Donor", "Wait")
    assert params["RuntimeAssetName"] == "Fx_New"
    assert params["Bone"] == "Root"
    assert params["Scale"] == pytest.approx(0.3)
    assert params["AssetName"] == "Wait" and params["BitFlag"] == 0x05000004  # the rest of the record is kept
    values = again.direct_values()
    assert len(values) == n_direct + 2  # one float, padded to 8 bytes with 1.0
    assert values[-1] == 1.0
    names = again.names
    assert names.count(b"\0Root\0") + names.startswith(b"Root\0") == 1  # an existing name is reused
    assert b"\0Fx_New\0" in names
    after = snapshot(again)
    assert after["Obj_Other"] == before["Obj_Other"]  # shares the old record, which stays
    assert after["Obj_Third"] == before["Obj_Third"]
    assert after["Obj_Donor"][0][1] == before["Obj_Donor"][0][1]  # the other call unchanged


def test_set_call_params_overrides_an_existing_value(data):
    table = elink.decode(data)
    table.set_call_params("Obj_Donor", "Get", {"PositionY": 0.0, "Bone": "Root", "Scale": 2.5})
    params = elink.decode(table.encode()).call_params("Obj_Donor", "Get")
    assert params["Scale"] == 2.5 and params["PositionY"] == 0.0 and params["Bone"] == "Root"


def test_make_container_appends_children(data):
    table = elink.decode(data)
    before = snapshot(table)
    old_trigger_pos = struct.unpack_from("<Q", table.user_data("Obj_Donor"), 0x30)[0]
    children = [
        {"RuntimeAssetName": "Fx_A", "PositionX": 0.12, "Red": 2.0},
        {"RuntimeAssetName": "Fx_B", "PositionX": -0.12, "Red": 3.0},
        {"RuntimeAssetName": "Fx_B", "PositionX": 0.0},
    ]
    table.make_container("Obj_Donor", "Wait", children, condition=0x30)
    again = elink.decode(table.encode())
    calls = again.calls("Obj_Donor")
    assert [c.key for c in calls] == ["Wait", "Get", "Wait_00", "Wait_01", "Wait_02"]
    wait = calls[0]
    assert wait.is_container and wait.asset == -1 and wait.flag == 1
    assert again.container("Obj_Donor", "Wait") == (3, 2, 4)  # play all, children 2..4
    assert [c.asset for c in calls] == [-1, 0, 1, 2, 3]  # renumbered in call order
    for i, child in enumerate(calls[2:]):
        assert child.parent == 0 and child.condition == 0x30 and child.flag == 0
        assert child.guid == zlib.crc32(f"Obj_Donor/Wait_{i:02d}".encode())
        params = again.call_params("Obj_Donor", child.key)
        assert params["AssetName"] == child.key
        assert params["Bone"] == "Root" and params["BitFlag"] == 0x05000004  # copied from the call's record
        assert params["RuntimeAssetName"] == children[i]["RuntimeAssetName"]
        assert params["PositionX"] == pytest.approx(children[i]["PositionX"])
    assert "Red" not in again.call_params("Obj_Donor", "Wait_02")
    assert again.call_params("Obj_Donor", "Get") == before["Obj_Donor"][0][1][1]
    assert again.trigger_table("Obj_Donor").rstrip(b"\0") == TRIGGERS  # entries still name the same calls
    new_pos = struct.unpack_from("<Q", again.user_data("Obj_Donor"), 0x30)[0]
    assert new_pos == old_trigger_pos + 3 * 0x30 + 16 + 8  # three calls, one container record, ids 4 -> 12 bytes
    after = snapshot(again)
    assert after["Obj_Other"] == before["Obj_Other"] and after["Obj_Third"] == before["Obj_Third"]


def test_two_containers_in_one_user(data):
    table = elink.decode(data)
    table.make_container("Obj_Donor", "Wait", [{"PositionX": 1.0}], condition=0x30)
    table.make_container("Obj_Donor", "Get", [{"PositionX": 2.0}, {"PositionX": 3.0}], condition=0x38)
    again = elink.decode(table.encode())
    assert again.container("Obj_Donor", "Wait") == (3, 2, 2)
    assert again.container("Obj_Donor", "Get") == (3, 3, 4)
    assert [c.asset for c in again.calls("Obj_Donor")] == [-1, -1, 0, 1, 2]
    assert again.call_params("Obj_Donor", "Get_01")["PositionX"] == 3.0


def test_errors_name_what_is_wrong(data):
    bad = bytearray(data)
    struct.pack_into("<I", bad, 8, 35)
    with pytest.raises(elink.ElinkError, match="version 35"):
        elink.decode(bytes(bad))
    with pytest.raises(elink.ElinkError, match="magic"):
        elink.decode(b"XLNQ" + data[4:])
    table = elink.decode(data)
    with pytest.raises(elink.ElinkError, match="Obj_Other.*already"):
        table.add_user_copy("Obj_Donor", "Obj_Other")
    with pytest.raises(elink.ElinkError, match="no user 'Obj_Missing'"):
        table.add_user_copy("Obj_Missing", "Clawshot_X")
    with pytest.raises(elink.ElinkError, match="Obj_Donor.*no call 'Nope'"):
        table.set_call_params("Obj_Donor", "Nope", {"Scale": 1.0})
    with pytest.raises(elink.ElinkError, match="unknown asset parameter 'Wobble'"):
        table.set_call_params("Obj_Donor", "Wait", {"Wobble": 1.0})
    table.make_container("Obj_Donor", "Wait", [{"Scale": 1.0}], condition=0)
    with pytest.raises(elink.ElinkError, match="Obj_Donor/Wait is a container"):
        table.make_container("Obj_Donor", "Wait", [{"Scale": 1.0}], condition=0)


# ---------------------------------------------------------------------------------------------------------------
# Action triggers (event-items D20): a scene animation starts a user's call, as Obj_Heart_Piece's
# Dm_Goron_0040_Obj_Heart_Piece/C01 does.

SCENES = ["Dm_Test_0040_Item_Bag_Large/C02", "Dm_Test_0030_Gauntlet/C09-Gauntlet"]


def heart_table() -> elink.Elink:
    return elink.decode(build_table(HEART_ACTION_USERS))


def test_action_triggers_read_the_heart_containers_table():
    assert heart_table().action_triggers("Obj_Heart_Container") == [
        ("AS[Lower]", "Rotate_Obj", ["Wait"]),
        ("Skl[Lower]", "Rotate_GetDemo", ["GetDemo"]),
    ]


def test_add_action_triggers_copies_the_templates_trigger_into_the_slot_sorted():
    table = heart_table()
    before = snapshot(table)
    native = table.user_data("Obj_Heart_Container")
    table.add_action_triggers("Obj_Heart_Container", "AS[Lower]", SCENES, "Rotate_GetDemo")
    out = table.encode()
    again = elink.decode(out)
    assert again.encode() == out
    assert again.action_triggers("Obj_Heart_Container") == [
        ("AS[Lower]", "Dm_Test_0030_Gauntlet/C09-Gauntlet", ["GetDemo"]),
        ("AS[Lower]", "Dm_Test_0040_Item_Bag_Large/C02", ["GetDemo"]),
        ("AS[Lower]", "Rotate_Obj", ["Wait"]),
        ("Skl[Lower]", "Rotate_GetDemo", ["GetDemo"]),
    ]
    after = snapshot(again)
    assert {k: v for k, v in after.items() if k != "Obj_Heart_Container"} == {
        k: v for k, v in before.items() if k != "Obj_Heart_Container"
    }
    assert after["Obj_Heart_Container"][0] == before["Obj_Heart_Container"][0]  # the calls are untouched
    assert again.user_data("Obj_Rupee_Red") == elink.decode(build_table(HEART_ACTION_USERS)).user_data("Obj_Rupee_Red")
    user = again.user_data("Obj_Heart_Container")
    at = struct.unpack_from("<Q", user, 0x30)[0]
    assert user[:0x14] == native[:0x14] and user[0x20:at] == native[0x20:at]  # all but two counts as before
    assert struct.unpack_from("<6I", user, 0x14) == (2, 4, 4, 0, 0, 0)
    assert len(user) % 8 == 0
    rows = user[at + 2 * 16 : at + 6 * 16]
    template = native[at + 4 * 16 + 0x28 : at + 4 * 16 + 0x50]  # Rotate_GetDemo's trigger
    triggers = user[at + 6 * 16 :]
    assert len(rows) == 64
    for k, scene in enumerate(sorted(SCENES)):
        trigger = triggers[0x28 * k : 0x28 * (k + 1)]
        assert struct.unpack_from("<I", trigger)[0] == zlib.crc32(f"Obj_Heart_Container/{scene}".encode())
        assert trigger[4:] == template[4:]


def test_add_action_triggers_keeps_native_name_offsets_and_interns_new_names_once():
    table = heart_table()
    user = table.user_data("Obj_Heart_Container")
    at = struct.unpack_from("<Q", user, 0x30)[0]
    slots, rotate_obj = user[at : at + 32], struct.unpack_from("<Q", user, at + 32)[0]
    table.add_user_copy("Obj_Heart_Container", "Clawshot_Other")
    table.add_action_triggers("Obj_Heart_Container", "AS[Lower]", SCENES, "Rotate_GetDemo")
    size = len(table.names)
    table.add_action_triggers("Clawshot_Other", "AS[Lower]", SCENES, "Rotate_GetDemo")
    assert len(table.names) == size  # the second user finds the names the first one added
    out = table.user_data("Obj_Heart_Container")
    assert struct.unpack_from("<Q", out, at)[0] == struct.unpack_from("<Q", slots, 0)[0]
    assert struct.unpack_from("<Q", out, at + 16)[0] == struct.unpack_from("<Q", slots, 16)[0]
    assert struct.unpack_from("<Q", out, at + 32 + 2 * 16)[0] == rotate_obj  # Rotate_Obj, now third in AS[Lower]


def test_add_action_triggers_sorts_ignoring_case_as_native_users():
    table = heart_table()
    table.add_action_triggers("Obj_Heart_Container", "AS[Lower]", ["rotate_A", "Rotate_B", "Rotate_"], "Rotate_GetDemo")
    names = [a for slot, a, _ in table.action_triggers("Obj_Heart_Container") if slot == "AS[Lower]"]
    assert names == ["Rotate_", "rotate_A", "Rotate_B", "Rotate_Obj"]


def test_an_empty_action_list_rebuilds_the_same_table():
    table = heart_table()
    native = table.user_data("Obj_Heart_Container")
    table.add_action_triggers("Obj_Heart_Container", "AS[Lower]", [], "Rotate_GetDemo")
    assert table.user_data("Obj_Heart_Container") == native


@pytest.mark.parametrize(
    ("users", "slot", "actions", "template", "message"),
    [
        (HEART_ACTION_USERS, "AS[Lower]", ["Rotate_Obj"], "Rotate_GetDemo", r"has \['Rotate_Obj'\] already"),
        (HEART_ACTION_USERS, "AS[Upper]", SCENES, "Rotate_GetDemo", r"0 slots 'AS\[Upper\]'"),
        (HEART_ACTION_USERS, "AS[Lower]", SCENES, "Rotate_Missing", "needs one action 'Rotate_Missing'"),
        (HEART_ACTION_USERS, "AS[Lower]", [SCENES[0], SCENES[0]], "Rotate_GetDemo", "named twice"),
        (
            {
                "Obj_Heart_Container": (
                    HEART_ACTION_USERS["Obj_Heart_Container"][0],
                    ActionTable(HEART_ACTIONS.slots, 1),
                )
            },
            "AS[Lower]",
            SCENES,
            "Rotate_GetDemo",
            "property or always triggers",
        ),
        (
            {
                "Obj_Heart_Container": (
                    HEART_ACTION_USERS["Obj_Heart_Container"][0],
                    ActionTable((("AS[Lower]", (("Rotate_GetDemo", (0, 1)),)),)),
                )
            },
            "AS[Lower]",
            SCENES,
            "Rotate_GetDemo",
            "needs one action 'Rotate_GetDemo' with one trigger",
        ),
    ],
)
def test_add_action_triggers_refuses(users, slot, actions, template, message):
    table = elink.decode(build_table(users))
    with pytest.raises(elink.ElinkError, match=message):
        table.add_action_triggers("Obj_Heart_Container", slot, actions, template)


def test_a_user_without_an_action_table_layout_is_refused():
    table = elink.decode(build_table())  # Obj_Donor's trigger table is opaque bytes with zero counts
    with pytest.raises(elink.ElinkError, match="data after the action triggers"):
        table.add_action_triggers("Obj_Donor", "AS[Lower]", SCENES, "Rotate_GetDemo")
